import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS

# Cấu hình giao diện trang web
st.set_page_config(
    page_title="AI Groq Tự Tra Cứu",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ Chatbot Groq + Tự Động Tra Cứu Web")
st.caption("Ứng dụng chạy bằng Groq API - Tự động tìm kiếm thông tin Internet mới nhất để trả lời.")

# Lấy API Key từ Streamlit Secrets hoặc thanh nhập bên trái
api_key = None
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    with st.sidebar:
        st.subheader("Cài đặt cấu hình")
        api_key = st.text_input("Nhập Groq API Key:", type="password")
        st.markdown("[Lấy Groq API Key miễn phí tại đây](https://console.groq.com/)")

if not api_key:
    st.warning("⚠️ Vui lòng cấu hình `GROQ_API_KEY` trong Streamlit Secrets hoặc nhập vào thanh cài đặt bên trái để bắt đầu.")
    st.stop()

# Khởi tạo Groq Client
client = Groq(api_key=api_key)

# Hàm tìm kiếm thông tin trên web
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            if results:
                return "\n- ".join(results)
    except Exception:
        pass
    return "Không tìm thấy thông tin trực tuyến phù hợp."

# Khởi tạo lịch sử trò chuyện
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Xử lý khi người dùng nhập tin nhắn
if prompt := st.chat_input("Bạn muốn tìm hiểu điều gì hôm nay?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("⚡ Đang tìm kiếm web và tổng hợp tốc độ cao..."):
            # 1. Tự động tìm kiếm thông tin trên web dựa vào câu hỏi
            search_data = search_web(prompt)
            
            # 2. Tạo ngữ cảnh hệ thống
            system_prompt = (
                "Bạn là một trợ lý AI thông minh. Dưới đây là thông tin thực tế được tìm kiếm từ internet để hỗ trợ:\n"
                f"--- \n{search_data}\n ---\n"
                "Hãy sử dụng thông tin trên kết hợp với hiểu biết của bạn để trả lời câu hỏi của người dùng một cách chính xác, ngắn gọn, tự nhiên bằng tiếng Việt."
            )
            
            # Chuẩn bị tin nhắn gửi lên Groq API
            messages_payload = [
                {"role": "system", "content": system_prompt}
            ]
            # Thêm lịch sử trò chuyện gần đây để giữ ngữ cảnh
            for m in st.session_state.messages[-6:]:
                messages_payload.append({"role": m["role"], "content": m["content"]})
            
            # 3. Gọi model Groq (sử dụng Llama 3 mạnh mẽ và nhanh)
            try:
                chat_completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages_payload,
                    temperature=0.7,
                    max_tokens=2048
                )
                answer = chat_completion.choices[0].message.content
            except Exception as e:
                answer = f"Đã xảy ra lỗi khi kết nối với Groq API: {str(e)}"
            
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
