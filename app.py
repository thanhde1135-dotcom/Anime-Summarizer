import streamlit as st
import csv
import os

# Cấu hình trang
st.set_page_config(page_title="AI Độc Lập Nội Bộ", page_icon="⚙️", layout="centered")

st.title("⚙️ Hệ Thống AI Độc Lập Không API")
st.markdown("Con AI này đọc dữ liệu từ file `data.csv`. Hãy gõ từ khóa liên quan để nó nhận diện.")

DATA_FILE = "data.csv"

# Tự động tạo file data.csv mẫu nếu chưa có trên GitHub
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["cau_hoi", "cau_tra_loi"])
        writer.writerow(["xin chào", "Chào bạn! Tôi đã sẵn sàng nhận lệnh từ bạn."])
        writer.writerow(["nhắn lại", "Tôi đã nhận được tin nhắn thử nghiệm của bạn rồi nhé!"])
        writer.writerow(["bạn là ai", "Tôi là một thực thể AI tự tạo, không phụ thuộc vào API ngoài."])

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
    st.write(f"Số lượng quy tắc: **{len(knowledge_base)}**")
    st.markdown("---")
    if knowledge_base:
        for q, a in knowledge_base.items():
            st.markdown(f"- 🔑 `{q}`")
    else:
        st.warning("File `data.csv` đang trống.")

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

    user_text_lower = user_prompt.strip().lower()
    bot_reply = None

    # THUẬT TOÁN THÔNG MINH HƠN: Kiểm tra xem từ khóa nào xuất hiện trong câu bạn chat
    for q, a in knowledge_base.items():
        # Chia nhỏ các từ trong câu hỏi của bạn để khớp linh hoạt hơn
        keywords = q.split()
        match_count = sum(1 for word in keywords if word in user_text_lower)
        
        # Nếu khớp từ khóa chính hoặc chứa từ khóa
        if q in user_text_lower or (keywords and match_count / len(keywords) >= 0.5):
            bot_reply = a
            break

    # Nếu vẫn không tìm thấy
    if not bot_reply:
        bot_reply = f"Quy định xử lý: Tôi chưa được dạy câu này. Hãy vào file `data.csv` thêm từ khóa **'{user_prompt}'** vào cột bên trái để tôi học nhé!"

    # Lưu và hiển thị phản hồi của AI
    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
    
