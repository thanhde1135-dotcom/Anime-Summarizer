import os
import streamlit as st
from utils import process_video_with_custom_subtitles

# Cấu hình giao diện trang web
st.set_page_config(
    page_title="AI CapCut Subtitle & Video Editor",
    page_icon="🎬",
    layout="centered",
)

st.markdown(
    """
    <h2 style='text-align: center; color: #FF4B4B;'>🎬 Tạo Phụ Đề Khớp 100% & Tùy Chỉnh Vị Trí AI</h2>
    <p style='text-align: center;'>Tích hợp Whisper Large V3, LLaMA 3 dịch chuẩn, Làm mờ & Đóng phụ đề trực tiếp vào video!</p>
    """,
    unsafe_allow_html=True,
)

# Sidebar cài đặt hệ thống & Tùy chỉnh vị trí phụ đề
st.sidebar.header("🔑 Cấu hình hệ thống")
groq_api_key = st.sidebar.text_input(
    "Nhập Groq API Key:", type="password", help="Lấy key miễn phí tại console.groq.com"
)

st.sidebar.markdown("---")
st.sidebar.header("📍 Tùy chỉnh Vị trí Phụ đề")
sub_position = st.sidebar.selectbox(
    "Vị trí hiển thị chữ trên video:",
    ["Phía dưới video (Mặc định)", "Phía trên video", "Chính giữa video"],
)
sub_margin_v = st.sidebar.slider(
    "Khoảng cách lề (Điều chỉnh lên/xuống linh hoạt):", 10, 200, 30
)

st.sidebar.markdown("---")
st.sidebar.header("🎛️ Tùy chỉnh Làm mờ Video")
enable_blur = st.sidebar.checkbox("Bật hiệu ứng làm mờ video", value=False)
blur_strength = st.sidebar.slider("Mức độ làm mờ (Blur Radius)", 1, 30, 10)
blur_region = st.sidebar.selectbox(
    "Vùng cần làm mờ:", ["Toàn bộ video", "Chỉ làm mờ nửa dưới video"]
)

# Khu vực tải lên file video
uploaded_file = st.file_uploader(
    "📁 Tải lên Video cần xử lý (MP4, MOV, AVI)",
    type=["mp4", "mov", "avi", "mkv"],
)

if uploaded_file is not None:
  st.video(uploaded_file)

  if st.button(
      "🚀 Xử lý Video, Đóng Phụ Đề Chuẩn Xác & Xuất Bản",
      type="primary",
      use_container_width=True,
  ):
    if not groq_api_key:
      st.error("⚠️ Vui lòng nhập Groq API Key ở thanh bên trái (Sidebar)!")
    else:
      with st.spinner(
          "🔄 Đang nhận diện giọng nói khớp 100%, dịch chuẩn và chèn phụ đề..."
      ):
        success, result = process_video_with_custom_subtitles(
            uploaded_file,
            groq_api_key,
            enable_blur,
            blur_strength,
            blur_region,
            sub_position,
            sub_margin_v,
        )

        if success:
          translated_text = result["translated_text"]
          words_data = result["words_data"]
          srt_content = result["srt_content"]
          final_video_path = result["final_video_path"]

          st.success("✨ Xử lý, chèn phụ đề và đóng gói video hoàn tất!")

          # Hiển thị video đã được đóng phụ đề hoàn chỉnh
          st.subheader("🎥 Video đã hoàn thiện phụ đề tiếng Việt:")
          if os.path.exists(final_video_path):
            st.video(final_video_path)
            with open(final_video_path, "rb") as f_vid:
              st.download_button(
                  label="📥 Tải xuống Video hoàn chỉnh có phụ đề",
                  data=f_vid.read(),
                  file_name="video_with_subtitles.mp4",
                  mime="video/mp4",
              )

          # Hiển thị bản dịch tổng quan
          st.subheader("📝 Bản dịch Tiếng Việt chuẩn 100%:")
          st.info(translated_text)

          # Nút tải xuống file SRT riêng biệt
          st.download_button(
              label="📥 Tải xuống file Phụ đề rời (.srt chuẩn CapCut)",
              data=srt_content,
              file_name="subtitles_capcut_style.srt",
              mime="text/plain",
          )

          # Hiển thị danh sách phụ đề chi tiết thời gian khớp từng từ
          st.subheader(
              "⏱️ Mốc thời gian chi tiết khớp 100% với giọng nói (CapCut Style):"
          )
          word_list_md = ""
          for w in words_data:
            st_t = w.get("start", 0)
            en_t = w.get("end", 0)
            w_val = w.get("word", "")
            word_list_md += f"`[{st_t:.2f}s - {en_t:.2f}s]` **{w_val}**  \n"

          st.markdown(
              f"<div style='max-height: 250px; overflow-y: scroll; padding: 10px; border: 1px solid #ccc; border-radius: 5px;'>{word_list_md}</div>",
              unsafe_allow_html=True,
          )
        else:
          st.error(f"❌ Đã xảy ra lỗi trong quá trình xử lý: {result}")
