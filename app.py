import streamlit as st

st.set_page_config(
    page_title="AI Studio Hub - All in One", page_icon="🚀", layout="centered"
)

st.markdown(
    """
    <h1 style='text-align: center; color: #FF4B4B;'>🚀 AI Media Studio Hub</h1>
    <p style='text-align: center;'>Hệ thống tích hợp toàn diện các công cụ AI xử lý video, phụ đề và giọng nói.</p>
    """,
    unsafe_allow_html=True,
)

st.info(
    "👈 **Hãy chọn các tính năng ở thanh menu bên trái (Sidebar)** để bắt đầu"
    " sử dụng các công cụ đã được tách riêng biệt:"
)

st.markdown(
    """
    * **🎬 Xử lý Video & Phụ Đề**: Làm mờ tùy chỉnh, nhận diện chuẩn xác từng từ bằng Whisper Large V3, dịch chuẩn bằng LLaMA 3 và chèn trực tiếp vào video.
    * **🎙️ AI Dịch Trực Tiếp (Live Stream)**: Ghi âm giọng nói hoặc tải âm thanh để xem AI dịch chữ chạy động thời gian thực (Typewriter effect).
    * **🗣️ Kho Giọng Đọc Hot Trend**: Tổng hợp các giọng đọc nổi tiếng trên TikTok, YouTube, Facebook để test và tải file âm thanh.
    """
)
