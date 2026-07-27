import os
import tempfile
import time
import streamlit as st
from groq import Groq

# Cấu hình giao diện trang web
st.set_page_config(
    page_title="AI Live Speech Streaming Translator",
    page_icon="🎙️",
    layout="centered",
)

st.markdown(
    """
    <h2 style='text-align: center; color: #4B9CD3;'>🎙️ AI Dịch Trực Tiếp & Streaming Thời Gian Thực</h2>
    <p style='text-align: center;'>Xem AI phân tích giọng nói và hiện chữ dịch động mượt mà từng dòng!</p>
    """,
    unsafe_allow_html=True,
)

# Sidebar cấu hình API
st.sidebar.header("🔑 Cấu hình hệ thống")
groq_api_key = st.sidebar.text_input(
    "Nhập Groq API Key:",
    type="password",
    help="Lấy key miễn phí tại console.groq.com",
    key="live_api_key",
)

target_lang = st.sidebar.selectbox(
    "🌍 Ngôn ngữ dịch đích:",
    [
        "Tiếng Việt",
        "Tiếng Anh",
        "Tiếng Trung",
        "Tiếng Nhật",
        "Tiếng Hàn",
    ],
    key="live_lang",
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Mẹo:** Ghi âm hoặc tải lên một đoạn âm thanh ngắn để trải nghiệm"
    " hiệu ứng AI streaming chữ chạy trực tiếp cực kỳ sống động."
)

# Tùy chọn đầu vào âm thanh trực tiếp
input_method = st.radio(
    "Chọn phương thức nhập âm thanh:",
    ["Ghi âm trực tiếp (Audio Input)", "Tải lên file âm thanh/video ngắn"],
    horizontal=True,
)

audio_to_process = None

if input_method == "Ghi âm trực tiếp (Audio Input)":
  st.markdown("🎙️ **Bấm vào biểu tượng micro bên dưới để bắt đầu nói:**")
  audio_file_recorded = st.audio_input("Ghi âm giọng nói của bạn")
  if audio_file_recorded is not None:
    audio_to_process = audio_file_recorded
    st.audio(audio_file_recorded)
else:
  uploaded_live_file = st.file_uploader(
      "📁 Tải lên file ghi âm/video ngắn (.mp3, .wav, .mp4)",
      type=["mp3", "wav", "m4a", "mp4"],
  )
  if uploaded_live_file is not None:
    audio_to_process = uploaded_live_file
    st.audio(uploaded_live_file)

if audio_to_process is not None:
  if st.button(
      "🚀 Bắt đầu Dịch Trực Tiếp (Live Stream)",
      type="primary",
      use_container_width=True,
  ):
    if not groq_api_key:
      st.error("⚠️ Vui lòng nhập Groq API Key ở thanh bên trái!")
    else:
      # Lưu file tạm
      ext = getattr(audio_to_process, "name", "audio.wav").split(".")[-1]
      with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(audio_to_process.read())
        tmp_path = tmp.name

      with st.spinner("🔄 Whisper đang bóc tách âm thanh..."):
        try:
          client = Groq(api_key=groq_api_key)
          with open(tmp_path, "rb") as f_audio:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(tmp_path), f_audio.read()),
                model="whisper-large-v3",
                response_format="json",
            )
          os.unlink(tmp_path)

          original_text = getattr(transcription, "text", str(transcription))

          # Hiển thị văn bản gốc nhận diện được
          st.subheader("📜 Văn bản gốc nhận diện:")
          st.info(original_text)

          # Khung hiển thị hiệu ứng AI dịch streaming (chữ chạy dòng dòng trực tiếp)
          st.subheader(
              f"✨ AI đang dịch trực tiếp sang {target_lang} (Streaming Mode):"
          )

          prompt = (
              f"Translate the following text into natural, fluent"
              f" {target_lang}. Translate accurately without adding extra"
              f" commentary:\n\n{original_text}"
          )

          # Gọi Groq API với chế độ stream=True để tạo hiệu ứng chữ hiện ra từ từ trực tiếp
          stream = client.chat.completions.create(
              messages=[{"role": "user", "content": prompt}],
              model="llama-3.3-70b-versatile",
              stream=True,
          )

          # Sử dụng st.write_stream để hiển thị hiệu ứng chữ chạy thời gian thực
          def generate_response():
            for chunk in stream:
              content = chunk.choices[0].delta.content
              if content:
                yield content
                time.sleep(0.01)  # Điều chỉnh tốc độ dòng chữ hiện lên mượt mà

          st.write_stream(generate_response())

        except Exception as e:
          st.error(f"❌ Đã xảy ra lỗi: {e}")

          if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    
