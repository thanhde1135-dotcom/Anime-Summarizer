import streamlit as st
import csv
import os

# Cấu hình trang
st.set_page_config(page_title="AI Độc Lập Nội Bộ", page_icon="⚙️", layout="centered")

st.title("⚙️ Hệ Thống AI Độc Lập Không API")
st.markdown("Con AI này hoạt động như một tờ giấy trắng, phản hồi hoàn toàn dựa trên dữ liệu bạn nạp vào file `data.csv`.")

DATA_FILE = "data.csv"

# Hàm đọc dữ liệu từ tệp CSV
def load_knowledge_base():
    knowledge = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)  # Bỏ qua tiêu đề
            for row in reader:
                if len(row) >= 2:
                    q = row[0].strip().lower()
                    a = row[1].strip()
                    knowledge[q] = a
    return knowledge

# Tải dữ liệu
knowledge_base = load_knowledge_base()

# Hiển thị bảng kiến thức hiện tại ở thanh bên (Sidebar)
with st.sidebar:
    st.subheader("📚 Kho Dữ Liệu Của AI")
    st.write(f"Tổng số quy tắc đã học: **{len(knowledge_base)}**")
    st.markdown("---")
    if knowledge_base:
        for q, a in knowledge_base.items():
            st.markdown(f"- **Hỏi:** `{q}`")
    else:
        st.warning("Chưa có dữ liệu trong file `data.csv`.")

# Khởi tạo trạng thái hội thoại
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Vẽ lại lịch sử chat trên giao diện
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# Khu vực nhập liệu trò chuyện
if user_prompt := st.chat_input("Nhập yêu cầu hoặc câu hỏi..."):
    # Lưu tin nhắn người dùng
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Xử lý logic tìm kiếm câu trả lời từ kho dữ liệu nội bộ
    user_input_clean = user_prompt.strip().lower()
    bot_reply = None

    # Quét xem từ khóa người dùng có khớp với câu hỏi nào trong file không
    for q, a in knowledge_base.items():
        if q in user_input_clean:
            bot_reply = a
            break

    # Nếu không tìm thấy trong dữ liệu
    if not bot_reply:
        bot_reply = "Quy định xử lý: Tôi chưa được huấn luyện hoặc chưa có dữ liệu về câu hỏi này trong hệ thống. Vui lòng cập nhật thêm vào file `data.csv`."

    # Lưu và hiển thị phản hồi của AI
    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
        
