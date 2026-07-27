import streamlit as st

st.set_page_config(page_title="Con AI Tự Tạo Của Tôi", page_icon="🧠")
st.title("🧠 Con AI Của Riêng Bạn (Không Dùng API)")
st.write("Đây là một con AI dạng tờ giấy trắng. Mọi câu trả lời dưới đây đều do chính bạn quy định trong mã nguồn.")

# Khởi tạo lịch sử trò chuyện trên giao diện
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử chat cũ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Khung nhập tin nhắn của người dùng
if user_input := st.chat_input("Nhập tin nhắn cho con AI của bạn..."):
    # Lưu tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # =========================================================================
    # NƠI BẠN TỰ DẶT QUY TẮC VÀ DẠY CON AI NÀY (HỆ THỐNG LUẬT LỆ)
    # Bạn có thể tự thêm các nhánh `elif` để dạy nó nói những câu khác.
    # =========================================================================
    text_lower = user_input.lower()
    
    # Quy tắc 1: Khi người dùng chào hỏi
    if "xin chào" in text_lower or "hi" in text_lower:
        bot_response = "Chào bạn! Tôi là con AI do chính bạn tạo ra. Tôi chưa có bộ não thông minh nhân tạo nào cả, tôi chỉ phản ứng theo quy tắc bạn viết."
    
    # Quy tắc 2: Khi người dùng hỏi tên nó
    elif "tên bạn là gì" in text_lower or "bạn là ai" in text_lower:
        bot_response = "Tôi chưa có tên. Bạn hãy sửa code trong GitHub để đặt tên cho tôi nhé!"
    
    # Quy tắc 3: Khi người dùng hỏi điều gì đó mà bạn chưa dạy
    else:
        bot_response = "Quy định của tôi: Tôi là AI tự chế nên tôi không biết điều này. (Hãy vào code để dạy tôi câu trả lời cho tình huống này)."

    # Lưu và hiển thị câu trả lời của AI
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    with st.chat_message("assistant"):
        st.markdown(bot_response)
        
