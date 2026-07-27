import streamlit as st
import csv
import os
import random
import difflib
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

st.set_page_config(page_title="AI Cào Tất Cả Mọi Link", page_icon="🌐", layout="centered")

st.title("🌐 Trợ Lý AI Cào Mọi Đường Link (Không Giới Hạn)")
st.markdown("Hệ thống sẽ liên tục quét từng trang và đi theo **tất cả các đường link** tìm thấy từ bất kỳ trang nào cho đến khi bạn bấm nút **Ngừng lại**.")

DATA_FILE = "data.csv"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["cau_hoi", "cau_tra_loi"])
        writer.writerow(["xin chào", "Dạ con chào anh/chị! Con đã sẵn sàng cào mọi đường link theo yêu cầu! 🌐"])

def load_knowledge_base():
    knowledge = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if len(row) >= 2:
                    q = row[0].strip().lower()
                    a = row[1].strip()
                    knowledge[q] = a
    return knowledge

def save_new_knowledge(question, answer):
    with open(DATA_FILE, mode="a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([question, answer])

knowledge_base = load_knowledge_base()

if "multi_web_text" not in st.session_state:
    st.session_state.multi_web_text = ""
if "crawled_urls" not in st.session_state:
    st.session_state.crawled_urls = []
if "is_crawling" not in st.session_state:
    st.session_state.is_crawling = False
if "to_visit" not in st.session_state:
    st.session_state.to_visit = []
if "visited" not in st.session_state:
    st.session_state.visited = set()

with st.sidebar:
    st.subheader("⚙️ Điều Kiện Cào Mọi Link")
    url_input = st.text_input("Dán link gốc ban đầu:", value="")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Bắt đầu cào"):
            if url_input:
                st.session_state.is_crawling = True
                st.session_state.to_visit = [url_input]
                st.session_state.visited = set()
                st.session_state.multi_web_text = ""
                st.session_state.crawled_urls = []
                st.rerun()
            else:
                st.warning("Vui lòng nhập link!")
                
    with col2:
        if st.button("⏹️ Ngừng lại"):
            st.session_state.is_crawling = False
            st.rerun()

    st.markdown("---")
    st.subheader("📊 Trạng Thái")
    if st.session_state.is_crawling:
        st.info("🔄 Đang cào toàn bộ các link liên tục...")
    else:
        st.warning("⏸️ Đã dừng hoặc hoàn tất.")
        
    st.write(f"Đã quét qua: **{len(st.session_state.crawled_urls)}** đường link.")
    if st.session_state.crawled_urls:
        with st.expander("Xem các link đã cào"):
            for u in st.session_state.crawled_urls:
                st.write(f"- {u}")

# LOGIC CÀO TẤT CẢ CÁC LINK KHÔNG GIỚI HẠN TÊN MIỀN
if st.session_state.is_crawling:
    if st.session_state.to_visit:
        current_url = st.session_state.to_visit.pop(0)
        if current_url not in st.session_state.visited:
            st.session_state.visited.add(current_url)
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                res = requests.get(current_url, headers=headers, timeout=5)
                if res.status_code == 200:
                    st.session_state.crawled_urls.append(current_url)
                    soup = BeautifulSoup(res.text, 'html.parser')
                    
                    for el in soup(["script", "style", "nav", "footer", "header", "aside"]):
                        el.decompose()
                        
                    page_text = soup.get_text(separator=' ', strip=True)
                    st.session_state.multi_web_text += f"\n--- LINK: {current_url} ---\n" + page_text
                    
                    # Cào TẤT CẢ CÁC LINK tìm thấy (bất kể tên miền nào, miễn là hợp lệ http/https)
                    for link in soup.find_all('a', href=True):
                        abs_url = urljoin(current_url, link['href'])
                        parsed = urlparse(abs_url)
                        if parsed.scheme in ['http', 'https']:
                            clean_url = abs_url.split('#')[0]
                            if clean_url not in st.session_state.visited and clean_url not in st.session_state.to_visit:
                                st.session_state.to_visit.append(clean_url)
            except Exception:
                pass
        
        st.rerun()
    else:
        st.session_state.is_crawling = False
        st.success("Đã cào hoàn tất tất cả các đường link có thể tiếp cận!")
        st.rerun()

# Khung chat giao tiếp
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "learning_question" not in st.session_state:
    st.session_state.learning_question = None

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

if user_prompt := st.chat_input("Hỏi bé thông tin từ các đường link đã cào..."):
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    user_text_lower = user_prompt.strip().lower()
    bot_reply = None

    if st.session_state.learning_question:
        pending_q = st.session_state.learning_question
        save_new_knowledge(pending_q, user_prompt)
        knowledge_base[pending_q] = user_prompt
        bot_reply = f"Yay! 🥳 Con vừa tự học được câu này rồi: *'{pending_q}' -> '{user_prompt}'*."
        st.session_state.learning_question = None
    else:
        if st.session_state.multi_web_text and any(kw in user_text_lower for kw in ["tóm tắt", "tất cả các trang", "nội dung chính"]):
            bot_reply = f"Dạ, con đã cào thành công tổng cộng {len(st.session_state.crawled_urls)} đường link! Anh/chị muốn tìm thông tin chi tiết nào cứ hỏi con nhé!"
        elif st.session_state.multi_web_text:
            sentences = re.split(r'[.!?]+', st.session_state.multi_web_text)
            matched = [s.strip() for s in sentences if any(w in s.lower() for w in user_text_lower.split() if len(w) > 2)]
            if matched:
                best_answers = ". ".join(matched[:3])
                bot_reply = f"Dạ, con tìm thấy đoạn này trong các link đã cào:\n\n> *{best_answers}.* 🔍"

        if not bot_reply:
            if user_text_lower in knowledge_base:
                bot_reply = knowledge_base[user_text_lower]
            else:
                matches = difflib.get_close_matches(user_text_lower, knowledge_base.keys(), n=1, cutoff=0.35)
                if matches:
                    bot_reply = knowledge_base[matches[0]]

        if not bot_reply:
            st.session_state.learning_question = user_text_lower
            bot_reply = f"Hì hì, câu **'{user_prompt}'** này con chưa tìm thấy trong các link đã cào! Anh/chị dạy con câu trả lời nha? 🥺"

    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
                        
