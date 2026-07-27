import streamlit as st
import csv
import os
import random
import difflib
import cloudscraper  # Thư viện vượt tường lửa chống chặn
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

st.set_page_config(page_title="AI Vượt Tường Lửa Cào Web", page_icon="🛡️", layout="centered")

st.title("🛡️ Trợ Lý AI Vượt Tường Lửa & Tiếp Thu Thông Tin")
st.markdown("Hệ thống tích hợp công cụ vượt tường chống chặn và cổng nạp dữ liệu trực tiếp giúp bé tiếp thu mọi tài liệu!")

DATA_FILE = "data.csv"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["cau_hoi", "cau_tra_loi"])
        writer.writerow(["xin chào", "Dạ con chào anh/chị! Con đã sẵn sàng vượt tường lửa và nạp kiến thức rồi đây! 🛡️"])

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
if "error_log" not in st.session_state:
    st.session_state.error_log = ""

with st.sidebar:
    st.subheader("🛡️ Vượt Tường Lửa Web")
    url_input = st.text_input("Dán link trang web cần vượt rào:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Vượt rào cào"):
            if url_input:
                st.session_state.is_crawling = True
                st.session_state.to_visit = [url_input]
                st.session_state.visited = set()
                st.session_state.multi_web_text = ""
                st.session_state.crawled_urls = []
                st.session_state.error_log = ""
                st.rerun()
            else:
                st.warning("Vui lòng nhập link!")
                
    with col2:
        if st.button("⏹️ Dừng lại"):
            st.session_state.is_crawling = False
            st.rerun()

    st.markdown("---")
    st.subheader("⚡ Cổng Phụ Nạp Nhanh (Dự Phòng)")
    st.markdown("Nếu trang web bắt đăng nhập hoặc chặn hoàn toàn, hãy copy nội dung dán vào đây:")
    direct_text_input = st.text_area("Dán nội dung văn bản/tài liệu vào đây:")
    if st.button("📥 Cho bé nạp ngay văn bản"):
        if direct_text_input:
            st.session_state.multi_web_text += "\n--- DỮ LIỆU NẠP THỦ CÔNG ---\n" + direct_text_input
            st.success("Đã nạp thành công toàn bộ văn bản vào bộ nhớ của bé!")
        else:
            st.warning("Chưa có nội dung để nạp!")

    st.markdown("---")
    st.subheader("📊 Trạng Thái")
    if st.session_state.is_crawling:
        st.info("🔄 Đang vượt tường lửa cào dữ liệu...")
    else:
        st.warning("⏸️ Đang dừng hoặc hoàn tất.")
        
    st.write(f"Số link/nguồn đã nạp: **{len(st.session_state.crawled_urls) + (1 if 'DỮ LIỆU NẠP THỦ CÔNG' in st.session_state.multi_web_text else 0)}**")
    
    if st.session_state.error_log:
        st.error(f"⚠️ {st.session_state.error_log}")

# LOGIC VƯỢT TƯỜNG LỬA BẰNG CLOUDSCRAPER
if st.session_state.is_crawling:
    if st.session_state.to_visit:
        current_url = st.session_state.to_visit.pop(0)
        if current_url not in st.session_state.visited:
            st.session_state.visited.add(current_url)
            try:
                # Sử dụng cloudscraper để vượt qua tường lửa bảo mật
                scraper = cloudscraper.create_scraper()
                res = scraper.get(current_url, timeout=10)
                
                if res.status_code == 200:
                    st.session_state.crawled_urls.append(current_url)
                    soup = BeautifulSoup(res.text, 'html.parser')
                    
                    for el in soup(["script", "style", "nav", "footer", "header", "aside"]):
                        el.decompose()
                        
                    page_text = soup.get_text(separator=' ', strip=True)
                    st.session_state.multi_web_text += f"\n--- LINK: {current_url} ---\n" + page_text
                    
                    for link in soup.find_all('a', href=True):
                        abs_url = urljoin(current_url, link['href'])
                        parsed = urlparse(abs_url)
                        if parsed.scheme in ['http', 'https']:
                            clean_url = abs_url.split('#')[0]
                            if clean_url not in st.session_state.visited and clean_url not in st.session_state.to_visit:
                                st.session_state.to_visit.append(clean_url)
                else:
                    st.session_state.error_log = f"Trang từ chối (Mã {res.status_code}). Hãy dùng cổng phụ bên dưới để dán nội dung trực tiếp!"
                    st.session_state.is_crawling = False
            except Exception as e:
                st.session_state.error_log = f"Không vượt rào được: {str(e)}. Hãy dùng cổng phụ dán text trực tiếp."
                st.session_state.is_crawling = False
        
        st.rerun()
    else:
        st.session_state.is_crawling = False
        st.success("Đã vượt rào và cào hoàn tất các trang!")
        st.rerun()

# Khung chat giao tiếp
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "learning_question" not in st.session_state:
    st.session_state.learning_question = None

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

if user_prompt := st.chat_input("Hỏi bé về kiến thức đã nạp hoặc trò chuyện..."):
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
            bot_reply = f"Dạ, con đã tiếp thu thông tin từ các nguồn dữ liệu anh/chị cung cấp! Anh/chị muốn hỏi chi tiết phần nào cứ nói con nhé!"
        elif st.session_state.multi_web_text:
            sentences = re.split(r'[.!?]+', st.session_state.multi_web_text)
            matched = [s.strip() for s in sentences if any(w in s.lower() for w in user_text_lower.split() if len(w) > 2)]
            if matched:
                best_answers = ". ".join(matched[:3])
                bot_reply = f"Dạ, con tìm thấy thông tin này trong tài liệu đã nạp:\n\n> *{best_answers}.* 🔍"

        if not bot_reply:
            if user_text_lower in knowledge_base:
                bot_reply = knowledge_base[user_text_lower]
            else:
                matches = difflib.get_close_matches(user_text_lower, knowledge_base.keys(), n=1, cutoff=0.35)
                if matches:
                    bot_reply = knowledge_base[matches[0]]

        if not bot_reply:
            st.session_state.learning_question = user_text_lower
            bot_reply = f"Hì hì, câu **'{user_prompt}'** này con chưa thấy trong tài liệu đã nạp! Anh/chị dạy con câu trả lời nha? 🥺"

    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
                    
