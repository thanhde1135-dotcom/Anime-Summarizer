import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# Cấu hình giao diện trang web
st.set_page_config(
    page_title="AI Thông Minh Tự Tra Cứu",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Chatbot Tự Động Tra Cứu Web")
st.caption("Ứng dụng không dùng dữ liệu cố định - Tự động tìm kiếm thông tin mới nhất để trả lời bạn.")

# Lấy API Key từ Streamlit Secrets hoặc thanh nhập bên trái
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    with st.sidebar:
        st.subheader("Cài đặt cấu hình")
        api_key = st.text_input("Nhập Google Gemini API Key:", type="password")
        st.markdown("[Lấy API Key miễn phí tại đây](https://aistudio.google.com/)")

if not api_key:
    st.warning("⚠️ Vui lòng cấu hình `GEMINI_API_KEY` trong Streamlit Secrets hoặc nhập vào thanh cài đặt bên trái để bắt đầu.")
    st.stop()

# Cấu hình Gemini API
genai.configure(api_key=api_key)

@st.cache_resource
def get_ai_model():
    return genai.GenerativeModel("gemini-1.5-flash")

model = get_ai_model()

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
        with st.spinner("🔍 Đang tìm kiếm thông tin và phân tích..."):
            # 1. Tự động tìm kiếm thông tin trên web dựa vào câu hỏi
            search_data = search_web(prompt)
            
            # 2. Tạo prompt kết hợp thông tin tìm được
            system_prompt = (
                "Bạn là một trợ lý AI thông minh. Dưới đây là thông tin thực tế được tìm kiếm từ internet để hỗ trợ:\n"
                f"--- \n{search_data}\n ---\n"
                "Hãy sử dụng thông tin trên kết hợp với hiểu biết của bạn để trả lời câu hỏi của người dùng một cách chính xác, ngắn gọn, tự nhiên bằng tiếng Việt. "
                "Nếu thông tin tìm kiếm không đủ, hãy tự suy luận logic nhưng tuyệt đối không bịa đặt thông tin sai lệch."
            )
            
            full_input = f"{system_prompt}\n\nCâu hỏi của người dùng: {prompt}"
            
            # 3. Gọi model sinh nội dung
            try:
                response = model.generate_content(full_input)
                answer = response.text
            except Exception as e:
                answer = f"Đã xảy ra lỗi khi kết nối với AI: {str(e)}"
            
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
  
