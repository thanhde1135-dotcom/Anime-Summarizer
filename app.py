import streamlit as st
import csv
import os
import random
import difflib
import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

st.set_page_config(page_title="AI Tự Động Cào & Tiếp Thu Web", page_icon="🤖", layout="centered")

st.title("🤖 Trợ Lý AI Tự Động Cào & Đọc Sạch Web")
st.markdown("Dán link trang web mở bất kỳ, bé sẽ tự động cào nối tiếp qua **tất cả các đường link** tìm thấy và tự tiếp thu toàn bộ thông tin!")

DATA_FILE = "data.csv"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["cau_hoi", "cau_tra_loi"])
        writer.writerow(["xin chào", "Dạ con chào anh/chị! Con đã sẵn sàng tự động cào và đọc web rồi đây! 🤖"])

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

# Trạng thái tự động cào
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
if "status_message" not in st.session_state:
    st.session_state.status_message = "Sẵn sàng nhận link."

with st.sidebar:
    st.subheader("⚙️ Điều Khởi Động Tự Động")
    url_input = st.text_input("Dán link gốc trang web mở:", value="")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Bắt đầu tự động cào"):
            if url_input:
                st.session_state.is_crawling = True
                st.session_state.to_visit = [url_input]
                st.session_state.visited = set()
                st.session_state.multi_web_text = ""
                st.session_state.crawled_urls = []
                st.session_state.status_message = "Đang bắt đầu cào tự động..."
                st.rerun()
            else:
                st.warning("Vui lòng nhập link hợp lệ!")
                
    with col2:
        if st.button("⏹️ Ngừng lại"):
            st.session_state.is_crawling = False
            st.session_state.status_message = "Đã dừng bởi người dùng."
            st.rerun()

    st.markdown("---")
    st.subheader("📊 Tiến Trình Tự Động")
    if st.session_state.is_crawling:
        st.info("🔄 Đang tự động quét các trang...")
    else:
        st.warning("⏸️ Trạng thái: Đứng yên / Hoàn tất.")
        
    st.write(f"Trạng thái: **{st.session_state.status_message}**")
    st.write(f"Đã tự động đọc: **{len(st.session_state.crawled_urls)}** trang web.")
    
    if st.session_state.crawled_urls:
        with st.expander("Xem danh sách trang đã nuốt"):
            for u in st.session_state.crawled_urls:
                st.write(f"- {u}")

# LOGIC VÒNG LẶP TỰ ĐỘNG CÀO VÀ TIẾP THU TRANG WEB
if st.session_state.is_crawling:
    if st.session_state.to_visit and len(st.session_state.crawled_urls) < 30: # Giới hạn tối đa 30 trang để an toàn hệ thống miễn phí
        current_url = st.session_state.to_visit.pop(0)
        if current_url not in st.session_state.visited:
            st.session_state.visited.add(current_url)
            try:
                scraper = cloudscraper.create_scraper()
                res = scraper.get(current_url, timeout=6)
                
                if res.status_code == 200:
                    st.session_state.crawled_urls.append(current_url)
                    st.session_state.status_message = f"Đang đọc: {current_url[:35]}..."
                    
                    soup = BeautifulSoup(res.text, 'html.parser')
                    for el in soup(["script", "style", "nav", "footer", "header", "aside"]):
                        el.decompose()
                        
                    page_text = soup.get_text(separator=' ', strip=True)
                    st.session_state.multi_web_text += f"\n--- NGUỒN TỪ LINK: {current_url} ---\n" + page_text
                    
                    # Tự động tìm tất cả các link con trên trang này để đi tiếp
                    for link in soup.find_all('a', href=True):
                        abs_url = urljoin(current_url, link['href'])
                        parsed = urlparse(abs_url)
                        if parsed.scheme in ['http', 'https']:
                            clean_url = abs_url.split('#')[0]
                            if clean_url not in st.session_state.visited and clean_url not in st.session_state.to_visit:
                                st.session_state.to_visit.append(clean_url)
                else:
                    pass # Bỏ qua trang bị chặn lỗi để tiếp tục cào trang khác
            except Exception:
                pass
        
        # Tự động lặp lại liên tục cho đến khi hết hàng đợi link
        st.rerun()
    else:
        st.session_state.is_crawling = False
        st.session_state.status_message = "Đã cào sạch sẽ toàn bộ các trang!"
        st.rerun()

# Khung chat giao tiếp thông minh với dữ liệu đã nạp tự động
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "learning_question" not in st.session_state:
    st.session_state.learning_question = None

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

if user_prompt := st.chat_input("Hỏi bé bất cứ thông tin nào từ các web đã tự động cào..."):
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
        # KIỂM TRA TRONG DỮ LIỆU CÁC WEB ĐÃ CÀO TỰ ĐỘNG
        if st.session_state.multi_web_text and any(kw in user_text_lower for kw in ["tóm tắt", "tất cả các trang", "nội dung chính"]):
            bot_reply = f"Dạ, con đã tự động cào và tiếp thu toàn bộ thông tin từ {len(st.session_state.crawled_urls)} trang web! Anh/chị muốn tìm chi tiết vấn đề gì cứ hỏi con nhé!"
        elif st.session_state.multi_web_text:
            sentences = re.split(r'[.!?]+', st.session_state.multi_web_text)
            matched = [s.strip() for s in sentences if any(w in s.lower() for w in user_text_lower.split() if len(w) > 2)]
            if matched:
                best_answers = ". ".join(matched[:3])
                bot_reply = f"Dạ, con tìm thấy thông tin này trong các trang web đã tự động đọc:\n\n> *{best_answers}.* 🔍"

        # Kiểm tra trong kho kiến thức riêng
        if not bot_reply:
            if user_text_lower in knowledge_base:
                bot_reply = knowledge_base[user_text_lower]
            else:
                matches = difflib.get_close_matches(user_text_lower, knowledge_base.keys(), n=1, cutoff=0.35)
                if matches:
                    bot_reply = knowledge_base[matches[0]]

        if not bot_reply:
            st.session_state.learning_question = user_text_lower
            bot_reply = f"Hì hì, con đã tự động cào web nhưng câu **'{user_prompt}'** này chưa thấy có trong dữ liệu! Anh/chị dạy con câu trả lời nha? 🥺"

    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
    
