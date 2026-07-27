import streamlit as st
import difflib
from database import load_all_knowledge, save_knowledge
from scraper import crawl_website
from smart_search import find_best_answer_ai
from exporter import generate_report
from image_downloader import get_images_as_zip
from universe_3d import render_3d_universe  # Gọi mô đun Không gian vũ trụ 3D

st.set_page_config(page_title="Hệ Thống Trợ Lý AI & Vũ Trụ 3D", page_icon="🌌", layout="wide")

st.title("🌌 Hệ Thống AI Đa Mô Đun & Không Gian Vũ Trụ 3D Vô Cực")
st.markdown("Hệ thống tích hợp: Trợ lý AI thông minh, cào web tự động, tải ảnh hàng loạt và Không gian vũ trụ 3D siêu nhẹ.")

knowledge_base = load_all_knowledge()

with st.sidebar:
    st.header("⚙️ Bảng Điều Khiển")
    tab_menu = st.radio("Chọn chức năng:", ["🌌 Không Gian Vũ Trụ 3D", "🤖 Cào Web & Xuất Báo Cáo", "🖼️ Tải Ảnh Hàng Loạt", "📚 Quản Lý Tri Thức"])
    
    if tab_menu == "🌌 Không Gian Vũ Trụ 3D":
        st.subheader("🌌 Chế Độ Vũ Trụ 3D")
        st.info("Không gian ảo không tốn dung lượng, được sinh ra hoàn toàn bằng toán học thời gian thực.")
        
    elif tab_menu == "🤖 Cào Web & Xuất Báo Cáo":
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

    elif tab_menu == "🖼️ Tải Ảnh Hàng Loạt":
        st.subheader("🖼️ Trình Tải Ảnh Từ Link")
        img_url_input = st.text_input("Dán link trang web chứa ảnh:")
        
        if st.button("🔍 Quét & Tải Ảnh"):
            if img_url_input:
                with st.spinner("Đang quét và gom toàn bộ ảnh vào file ZIP..."):
                    zip_file, msg = get_images_as_zip(img_url_input)
                    if zip_file:
                        st.success(msg)
                        st.session_state.zip_data = zip_file
                    else:
                        st.error(msg)
            else:
                st.error("Vui lòng nhập link hợp lệ!")
                
        if st.session_state.get('zip_data'):
            st.download_button(
                label="📦 Tải xuống File ZIP chứa toàn bộ ảnh",
                data=st.session_state.zip_data,
                file_name="downloaded_images.zip",
                mime="application/zip"
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

# HIỂN THỊ KHÔNG GIAN VŨ TRỤ 3D NẾU ĐƯỢC CHỌN TRÊN TAB
if tab_menu == "🌌 Không Gian Vũ Trụ 3D":
    st.subheader("✨ Trải Nghiệm Không Gian Vũ Trụ 3D Vô Cực")
    render_3d_universe()
else:
    # Giao diện Chat thông thường
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
            web_data = st.session_state.get("web_text", "")
            if web_data and any(kw in user_text_lower for kw in ["tóm tắt", "tất cả", "nội dung chính"]):
                bot_reply = f"Dạ, hệ thống đã cào từ {len(st.session_state.get('crawled_urls', []))} trang web. Anh/chị có thể hỏi chi tiết hoặc khám phá không gian 3D!"
            elif web_data:
                best_match = find_best_answer_ai(user_prompt, web_data)
                if best_match:
                    bot_reply = f"🧠 **AI Phân Tích Thông Minh từ Web:**\n\n> *{best_match}*"

            if not bot_reply:
                if user_text_lower in knowledge_base:
                    bot_reply = knowledge_base[user_text_lower]
                else:
                    matches = difflib.get_close_matches(user_text_lower, knowledge_base.keys(), n=1, cutoff=0.35)
                    if matches:
                        bot_reply = knowledge_base[matches[0]]

            if not bot_reply:
                st.session_state.learning_question = user_text_lower
                bot_reply = f"🤔 Hệ thống chưa tìm thấy thông tin cho câu hỏi **'{user_prompt}'**. Mời anh/chị dạy đáp án để hệ thống tự học!"

        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
            
