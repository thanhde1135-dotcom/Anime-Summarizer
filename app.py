import streamlit as st
import google.generativeai as genai

# Cấu hình giao diện Streamlit
st.set_page_config(page_title="AI Tuân Thủ Quy Tắc", page_icon="🤖")
st.title("🤖 Trợ Lý AI Riêng Tư")
st.write("Ứng dụng AI hoạt động hoàn toàn dựa trên các quy tắc do bạn thiết lập.")

# Nhập API Key (Khuyến nghị dùng Streamlit Secrets sau khi đã quen)
api_key = st.text_input("Nhập Google Gemini API Key của bạn:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    
    # =========================================================================
    # NƠI BẠN TỰ ĐẶT QUY TẮC CHO AI (SYSTEM PROMPT)
    # Bạn có thể thay đổi nội dung bên trong dấu ngoặc kép để dạy AI quy tắc mới.
    # =========================================================================
    QUY_TAC_HE_THONG = """
    Bạn là một trợ lý AI được lập trình riêng. Bạn phải tuân thủ nghiêm ngặt các quy tắc sau:
    1. TUYỆT ĐỐI KHÔNG tự ý tra cứu hay tìm kiếm thông tin trên internet.
    2. Chỉ trả lời dựa trên nội dung được cung cấp hoặc kiến thức có sẵn từ trước.
    3. Nếu gặp câu hỏi nằm ngoài phạm vi hoặc không biết câu trả lời, hãy từ chối lịch sự bằng câu: "Theo quy định, tôi không có thông tin hoặc không được phép trả lời câu hỏi này."
    4. Giữ câu trả lời ngắn gọn, rõ ràng và đúng trọng tâm.
    """
    
    # Khởi tạo mô hình AI kèm theo quy tắc hệ thống
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=QUY_TAC_HE_THONG
    )
    
    # Khởi tạo lịch sử trò chuyện
    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat(history=[])

    # Hiển thị lịch sử tin nhắn trên giao diện
    for message in st.session_state.chat.history:
        role_mapped = "user" if message.role == "user" else "assistant"
        with st.chat_message(role_mapped):
            st.markdown(message.parts[0].text)

    # Khung nhập tin nhắn cho người dùng
    if user_input := st.chat_input("Nhập tin nhắn của bạn..."):
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("AI đang xử lý theo quy tắc..."):
                try:
                    response = st.session_state.chat.send_message(user_input)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi: {e}")
else:
    st.info("Vui lòng nhập API Key để kích hoạt ứng dụng AI của bạn.")
              
