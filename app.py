import streamlit as st
import csv
import os
import random
import difflib
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="AI Đọc Web Siêu Tốc", page_icon="🌐", layout="centered")

st.title("🌐 Trợ Lý AI Đọc Web Siêu Tốc")
st.markdown("Dán link trang web vào thanh bên cạnh, bé sẽ đọc sạch toàn bộ nội dung trang web đó ngay lập tức để trò chuyện với bạn!")

DATA_FILE = "data.csv"

# Tự động tạo file dữ liệu mẫu nếu chưa có
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["cau_hoi", "cau_tra_loi"])
        writer.writerow(["xin chào", "Dạ con chào anh/chị! Con đã sẵn sàng đọc web cùng anh/chị rồi đây! 🌐"])

# Đọc dữ liệu từ file CSV
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

# ==========================================
# TÍNH NĂNG MỚI: ĐỌC TRANG WEB TỪ URL
# ==========================================
if "web_text" not in st.session_state:
    st.session_state.web_text = ""
if "web_url" not in st.session_state:
    st.session_state.web_url = ""

with st.sidebar:
    st.subheader("🌐 Nạp Kiến Thức Từ Web")
    url_input = st.text_input("Dán link trang web vào đây:")
    
    if st.button("🚀 Cho bé đọc web ngay"):
        if url_input:
            try:
                with st.spinner("Bé đang lướt web và đọc chữ cực nhanh..."):
                    # Tải nội dung trang web
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    response = requests.get(url_input, headers=headers, timeout=10)
                    response.raise_for_status()
                    
                    # Phân tích cú pháp HTML bằng BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Xóa bỏ các thẻ không cần thiết (script, style...)
                    for script in soup(["script", "style", "nav", "footer"]):
                        script.extract()
                        
                    # Lấy toàn bộ văn bản thạch sạch sẽ
                    text = soup.get_text(separator=' ', strip=True)
                    
                    st.session_state.web_text = text
                    st.session_state.web_url = url_input
                    st.success(f"Đã đọc xong! Bé đã nạp toàn bộ nội dung từ trang web.")
            except Exception as e:
                st.error(f"Không đọc được trang web này: {e}")
        else:
            st.warning("Vui lòng nhập một đường link hợp lệ!")

    st.markdown("---")
    st.subheader("🎒 Cặp Sách Của Bé")
    st.write(f"Đã học được **{len(knowledge_base)}** câu từ file.")
    if st.session_state.web_url:
        st.info(f"Đang gắn kết với web:\n`{st.session_state.web_url}`")

# Khởi tạo lịch sử chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "learning_question" not in st.session_state:
    st.session_state.learning_question = None

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# Khung nhập tin nhắn
if user_prompt := st.chat_input("Hỏi bé về nội dung web hoặc trò chuyện..."):
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    user_text_lower = user_prompt.strip().lower()
    bot_reply = None

    # 1. Nếu đang chờ dạy học lưu vào file
    if st.session_state.learning_question:
        pending_q = st.session_state.learning_question
        save_new_knowledge(pending_q, user_prompt)
        knowledge_base[pending_q] = user_prompt
        bot_reply = f"Yay! 🥳 Con vừa tự học được câu này rồi: *'{pending_q}' -> '{user_prompt}'*."
        st.session_state.learning_question = None

    else:
        # 2. KIỂM TRA TRONG NỘI DUNG TRANG WEB VỪA ĐỌC (Nếu có link được nạp)
        if st.session_state.web_text and any(kw in user_text_lower for kw in ["tóm tắt", "nói về cái gì", "nội dung", "trang web này"]):
            # Trả về đoạn đầu tiên của trang web làm tóm tắt nhanh
            snippet = st.session_state.web_text[:1000]
            bot_reply = f"Dạ, trang web ở link `{st.session_state.web_url}` có nội dung chính là:\n\n> *{snippet}...*\n\nAnh/chị muốn tìm chi tiết phần nào nữa không ạ? 🌐"
        
        elif st.session_state.web_text:
            # Tìm kiếm các câu chứa từ khóa trong văn bản trang web
            sentences = st.session_state.web_text.split('.')
            matching_sentences = [s.strip() for s in sentences if any(w in s.lower() for w in user_text_lower.split() if len(w) > 2)]
            if matching_sentences:
                bot_reply = f"Dạ, con tìm thấy trong trang web đoạn này nè:\n\n> *{matching_sentences[0]}.* 📖"

        # 3. Nếu không có trong web, tra cứu trong bộ nhớ file CSV
        if not bot_reply:
            if user_text_lower in knowledge_base:
                bot_reply = knowledge_base[user_text_lower]
            else:
                matches = difflib.get_close_matches(user_text_lower, knowledge_base.keys(), n=1, cutoff=0.35)
                if matches:
                    bot_reply = knowledge_base[matches[0]]

        # 4. Nếu vẫn không biết -> Kích hoạt chế độ tự động học
        if not bot_reply:
            st.session_state.learning_question = user_text_lower
            bot_reply = f"Hì hì, câu **'{user_prompt}'** này con chưa rõ lắm! Anh/chị dạy con đi ạ, câu trả lời là gì thế ạ? 🥺"

    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
  
