import streamlit as st
import difflib
from database import load_all_knowledge, save_knowledge
from scraper import crawl_website
from smart_search import find_best_answer_ai  # Gọi mô đun tìm kiếm thông minh
from exporter import generate_report          # Gọi mô đun xuất báo cáo

st.set_page_config(page_title="Hệ Thống Trợ Lý AI Chuyên Nghiệp", page_icon="💼", layout="wide")

st.title("💼 Hệ Thống Trợ Lý AI & Quản Trị Tri Thức Đa Mô Đun")
st.markdown("Hệ thống tích hợp AI tìm kiếm ngữ nghĩa thông minh, tự động cào web và xuất báo cáo dữ liệu.")

knowledge_base = load_all_knowledge()

with st.sidebar:
    st.header("⚙️ Bảng Điều Khiển")
    tab_menu = st.radio("Chọn chức năng:", ["🤖 Cào Web & Xuất Báo Cáo", "📚 Quản Lý Tri Thức"])
    
    if tab_menu == "🤖 Cào Web & Xuất Báo Cáo":
        st.subheader("🌐 Cào Web Tự Động")
        url_input = st.text_input("Dán đường link gốc:")
        max_p = st.slider("Giới hạn số trang quét:", 5, 40, 15)
        
        if st.button("🚀 Bắt Đầu Cào"):
            if url_input:
                with st.spinner("Đang cào dữ liệu toàn bộ hệ thống link..."):
                    text, urls, err = crawl_website(url_input, max_pages=max_p)
                    st.session_state.web_text = text
                    st.session_state.crawled_urls = urls
                    if err:
                        st.warning(err)
                    else:
                        st.success(f"Đã cào thành công {len(urls)} trang!")
            else:
                st.error("Vui lòng nhập link hợp lệ!")
                
        # Tính năng xuất báo cáo cực hay
        if st.session_state.get('crawled_urls'):
            st.markdown("---")
            st.subheader("📥 Xuất Báo Cáo")
            report_content = generate_report(st.session_state.crawled_urls, st.session_state.web_text)
            st.download_button(
                label="💾 Tải báo cáo (.md)",
                data=report_content,
                file_name="bao_cao_ai_crawled.md",
                mime="text/markdown"
            )

    else:
        st.subheader("🗄️ Kho Dữ Liệu Đa File")
        st.write(f"Tổng số quy tắc: **{len(knowledge_base)}**")
        new_q = st.text_input("Thêm câu hỏi mới:")
        new_a = st.text_input("Thêm câu trả lời:")
        if st.button("💾 Lưu vào cơ sở dữ liệu"):
            if new_q and new_a:
                save_knowledge(new_q, new_a, filename="custom_expert.csv")
                st.success("Đã lưu thành công!")
                st.rerun()
            else:
                st.warning("Vui lòng điền đủ thông tin!")

st.markdown("---")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "learning_question" not in st.session_state:
    st.session_state.learning_question = None

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

if user_prompt := st.chat_input("Hỏi bé bất kỳ thông tin gì từ các trang web đã cào..."):
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    user_text_lower = user_prompt.strip().lower()
    bot_reply = None

    if st.session_state.learning_question:
        pending_q = st.session_state.learning_question
        save_knowledge(pending_q, user_prompt, filename="learned_from_chat.csv")
        bot_reply = f"✅ Hệ thống đã ghi nhớ vĩnh viễn: *'{pending_q}' -> '{user_prompt}'*."
        st.session_state.learning_question = None
    else:
        # 1. TÌM KIẾM THÔNG MINH BẰNG MÔ ĐUN smart_search.py
        web_data = st.session_state.get("web_text", "")
        if web_data and any(kw in user_text_lower for kw in ["tóm tắt", "tất cả", "nội dung chính"]):
            bot_reply = f"Dạ, hệ thống đã cào từ {len(st.session_state.get('crawled_urls', []))} trang web. Anh/chị có thể tải báo cáo về hoặc hỏi chi tiết vấn đề cụ thể!"
        elif web_data:
            # Gọi thuật toán vector thông minh
            best_match = find_best_answer_ai(user_prompt, web_data)
            if best_match:
                bot_reply = f"🧠 **AI Phân Tích Thông Minh từ Web:**\n\n> *{best_match}*"

        # 2. Tra cứu kho cơ sở dữ liệu CSV
        if not bot_reply:
            if user_text_lower in knowledge_base:
                bot_reply = knowledge_base[user_text_lower]
            else:
                matches = difflib.get_close_matches(user_text_lower, knowledge_base.keys(), n=1, cutoff=0.35)
                if matches:
                    bot_reply = knowledge_base[matches[0]]

        # 3. Kích hoạt học tập
        if not bot_reply:
            st.session_state.learning_question = user_text_lower
            bot_reply = f"🤔 Hệ thống chưa tìm thấy thông tin cho câu hỏi **'{user_prompt}'**. Mời anh/chị dạy đáp án để hệ thống tự học!"

    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
        
