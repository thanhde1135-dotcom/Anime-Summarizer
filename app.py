import streamlit as st
from openai import OpenAI

# ====================== CẤU HÌNH ======================
st.set_page_config(
    page_title="Grok-like Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Tiêu đề
st.title("🤖 Chatbot AI")
st.caption("Powered by Streamlit + LLM API")

# Lấy API key từ Secrets (quan trọng khi deploy)
api_key = st.secrets.get("API_KEY", "")

# Cho phép người dùng nhập API key tạm thời (khi chạy local)
if not api_key:
    api_key = st.sidebar.text_input("Nhập API Key", type="password")

# Chọn model (bạn có thể đổi)
model = st.sidebar.selectbox(
    "Chọn model",
    [
        "grok-beta",           # xAI Grok (nếu dùng API xAI)
        "gpt-4o-mini",         # OpenAI
        "gpt-4o",
        "llama-3.3-70b-versatile",  # Groq
        "gemini-1.5-flash",    # Gemini (nếu dùng OpenAI-compatible)
    ],
    index=0
)

# Base URL (để dùng nhiều nhà cung cấp)
base_url = st.sidebar.text_input(
    "Base URL (để trống = OpenAI)",
    value="https://api.x.ai/v1"   # Mặc định xAI. Đổi thành "" nếu dùng OpenAI
)

# ====================== KHỞI TẠO CLIENT ======================
if api_key:
    client = OpenAI(
        api_key=api_key,
        base_url=base_url if base_url else None
    )
else:
    st.warning("⚠️ Vui lòng nhập API Key ở sidebar hoặc thêm vào Secrets trên Streamlit Cloud.")
    st.stop()

# ====================== LỊCH SỬ CHAT ======================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Bạn là một trợ lý AI thông minh, hài hước và hữu ích, giống Grok của xAI. Trả lời bằng tiếng Việt trừ khi người dùng yêu cầu khác."}
    ]

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ====================== NHẬP TIN NHẮN ======================
if prompt := st.chat_input("Nhập tin nhắn của bạn..."):
    # Thêm tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gọi API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            stream = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
                stream=True,
                temperature=0.7,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:
            full_response = f"❌ Lỗi: {str(e)}"
            message_placeholder.error(full_response)

    # Lưu câu trả lời
    st.session_state.messages.append({"role": "assistant", "content": full_response})
