import streamlit as st
import difflib
import re
from database import load_all_knowledge, save_knowledge
from scraper import crawl_website

st.set_page_config(page_title="Hệ Thống Trợ Lý AI Chuyên Nghiệp", page_icon="💼", layout="wide")

# Giao diện chính chia cột chuyên nghiệp
st.title("💼 Hệ Thống Trợ Lý AI & Quản Trị Tri Thức Doanh Nghiệp")
st.markdown("Hệ thống đa module: Quản trị đa tệp dữ liệu, cào web tự động thông minh và học tập liên tục.")

# Tải bộ nhớ hệ thống
knowledge_base = load_all_knowledge()

# Sidebar Quản Trị Chuyên Nghiệp
with st.sidebar:
    st.header("⚙️ Bảng Điều Khiển")
    
    tab_menu = st.radio("Chọn chức năng:", ["🤖 Cào Web Tự Động", "📚 Quản Lý Tri Thức"])
    
    if tab_menu == "🤖 Cào Web Tự Động":
        st.subheader("🌐 Công Cụ Cào Web")
        url_input = st.text_input("Dán đường link gốc:")
        max_p = st.slider("Giới hạn số trang quét:", 5, 50, 15)
        
        if st.button("🚀 Bắt Đầu Cào Dữ Liệu"):
            if url_input:
                with st.spinner("Hệ thống đang vượt rào và cào dữ liệu..."):
                    text, urls, err = crawl_website(url_input, max_pages=max_p)
                    st.session_state.web_text = text
                    st.session_state.crawled_urls = urls
                    if err:
                        st.warning(err)
                    else:
                        st.success(f"Đã cào thành công {len(urls)} trang!")
            else:
                st.error("Vui lòng nhập link hợp lệ!")
                
        st.write(f"📊 Đã nạp: **{len(st.session_state.get('crawled_urls', []))}** trang vào bộ nhớ tạm.")

    else:
        st.subheader("🗄️ Kho Dữ Liệu Đa File")
        st.write(f"Tổng số quy tắc trong hệ thống: **{len(knowledge_base)}**")
        new_q = st.text_input("Thêm câu hỏi mới:")
        new_a = st.text_input("Thêm câu trả lời:")
        if st.button("💾 Lưu vào cơ sở dữ liệu"):
            if new_q and new_a:
                save_knowledge(new_q, new_a, filename="custom_expert.csv")
                st.success("Đã lưu vào kho tri thức thành công!")
                st.rerun()
            else:
                st.warning("Vui lòng điền đủ thông tin!")

# Khung Giao Tiếp Chính (Chat Interface)
st.markdown("---")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "learning_question" not in st.session_state:
    st.session_state.learning_question = None

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

if user_prompt := st.chat_input("Nhập câu hỏi hoặc yêu cầu tìm kiếm thông tin..."):
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    user_text_lower = user_prompt.strip().lower()
    bot_reply = None

    # 1. Chế độ học tập khi AI chưa biết
    if st.session_state.learning_question:
        pending_q = st.session_state.learning_question
        save_knowledge(pending_q, user_prompt, filename="learned_from_chat.csv")
        bot_reply = f"✅ Hệ thống đã tiếp thu và ghi nhớ vĩnh viễn: *'{pending_q}' -> '{user_prompt}'*."
        st.session_state.learning_question = None
    else:
        # 2. Tìm kiếm trong dữ liệu web đã cào
        web_data = st.session_state.get("web_text", "")
        if web_data and any(kw in user_text_lower for kw in ["tóm tắt", "tất cả", "nội dung"]):
            bot_reply = f"Dạ, hệ thống đã cào và phân tích từ {len(st.session_state.get('crawled_urls', []))} trang web. Anh/chị muốn tìm chi tiết vấn đề cụ thể nào ạ?"
        elif web_data:
            sentences = re.split(r'[.!?]+', web_data)
            matched = [s.strip() for s in sentences if any(w in s.lower() for w in user_text_lower.split() if len(w) > 2)]
            if matched:
                best_answers = ". ".join(matched[:3])
                bot_reply = f"🔍 **Trích xuất từ dữ liệu web:**\n\n> *{best_answers}.*"

        # 3. Tra cứu trong kho cơ sở dữ liệu đa file CSV
        if not bot_reply:
            if user_text_lower in knowledge_base:
                bot_reply = knowledge_base[user_text_lower]
            else:
                matches = difflib.get_close_matches(user_text_lower, knowledge_base.keys(), n=1, cutoff=0.35)
                if matches:
                    bot_reply = knowledge_base[matches[0]]

        # 4. Kích hoạt học tập thông minh nếu hoàn toàn không có
        if not bot_reply:
            st.session_state.learning_question = user_text_lower
            bot_reply = f"🤔 Hệ thống chưa tìm thấy thông tin cho câu hỏi **'{user_prompt}'**. Xin mời chuyên gia cung cấp đáp án để hệ thống tự động cập nhật vào cơ sở dữ liệu!"

    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
      
