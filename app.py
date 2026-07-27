import streamlit as st
import csv
import os

st.set_page_config(page_title="AI Đọc Dữ Liệu Từ File", page_icon="📚")
st.title("📚 Con AI Đọc Dữ Liệu Từ Tệp Riêng")
st.write("Con AI này không dùng API, nó tự động tra cứu các câu trả lời từ file `data.csv` nằm bên cạnh.")

# Tên file chứa dữ liệu
DATA_FILE = "data.csv"

# Hàm đọc dữ liệu từ file CSV
def load_qa_data():
    qa_dict = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # Bỏ qua dòng tiêu đề (cau_hoi, cau_tra_loi)
            for row in reader:
                if len(row) >= 2:
                    question = row[0].strip().lower()
                    answer = row[1].strip()
                    qa_dict[question] = answer
    return qa_dict

# Tải dữ liệu câu hỏi/trả lời
qa_data = load_qa_data()

# Hiển thị bảng danh sách những gì AI đang biết (để bạn dễ theo dõi)
with st.expander("📂 Xem danh sách câu hỏi/trả lời hiện có trong file `data.csv`"):
    if qa_data:
        for q, a in qa_data.items():
            st.write(f"- **Hỏi:** `{q}` ➔ **Đáp:** `{a}`")
    else:
        st.write("File `data.csv` chưa có dữ liệu hoặc đang trống.")

# Khởi tạo lịch sử trò chuyện trên giao diện
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Khung nhập tin nhắn
if user_input := st.chat_input("Nhập câu hỏi cho con AI của bạn..."):
    # Lưu tin nhắn của bạn
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    user_text_lower = user_input.strip().lower()
    
    # Tìm kiếm câu trả lời dựa trên file data.csv
    bot_response = None
    for q, a in qa_data.items():
        if q in user_text_lower:  # Kiểm tra nếu từ khóa bạn nhập khớp với dữ liệu
            bot_response = a
            break
            
    # Nếu trong file không có câu trả lời phù hợp
    if not bot_response:
        bot_response = "Quy định của tôi: Tôi chưa được dạy câu này trong file `data.csv`. Hãy vào file đó bổ sung thêm nhé!"

    # Lưu và hiển thị câu trả lời của AI
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    with st.chat_message("assistant"):
        st.markdown(bot_response)
        import streamlit as st
import csv
import os

st.set_page_config(page_title="AI Đọc Dữ Liệu Từ File", page_icon="📚")
st.title("📚 Con AI Đọc Dữ Liệu Từ Tệp Riêng")
st.write("Con AI này không dùng API, nó tự động tra cứu các câu trả lời từ file `data.csv` nằm bên cạnh.")

# Tên file chứa dữ liệu
DATA_FILE = "data.csv"

# Hàm đọc dữ liệu từ file CSV
def load_qa_data():
    qa_dict = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # Bỏ qua dòng tiêu đề (cau_hoi, cau_tra_loi)
            for row in reader:
                if len(row) >= 2:
                    question = row[0].strip().lower()
                    answer = row[1].strip()
                    qa_dict[question] = answer
    return qa_dict

# Tải dữ liệu câu hỏi/trả lời
qa_data = load_qa_data()

# Hiển thị bảng danh sách những gì AI đang biết (để bạn dễ theo dõi)
with st.expander("📂 Xem danh sách câu hỏi/trả lời hiện có trong file `data.csv`"):
    if qa_data:
        for q, a in qa_data.items():
            st.write(f"- **Hỏi:** `{q}` ➔ **Đáp:** `{a}`")
    else:
        st.write("File `data.csv` chưa có dữ liệu hoặc đang trống.")

# Khởi tạo lịch sử trò chuyện trên giao diện
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Khung nhập tin nhắn
if user_input := st.chat_input("Nhập câu hỏi cho con AI của bạn..."):
    # Lưu tin nhắn của bạn
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    user_text_lower = user_input.strip().lower()
    
    # Tìm kiếm câu trả lời dựa trên file data.csv
    bot_response = None
    for q, a in qa_data.items():
        if q in user_text_lower:  # Kiểm tra nếu từ khóa bạn nhập khớp với dữ liệu
            bot_response = a
            break
            
    # Nếu trong file không có câu trả lời phù hợp
    if not bot_response:
        bot_response = "Quy định của tôi: Tôi chưa được dạy câu này trong file `data.csv`. Hãy vào file đó bổ sung thêm nhé!"

    # Lưu và hiển thị câu trả lời của AI
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    with st.chat_message("assistant"):
        st.markdown(bot_response)
    
