import os
import tempfile
import streamlit as st
from groq import Groq

# Cấu hình giao diện trang web
st.set_page_config(
    page_title="AI Subtitle & Translator - CapCut Style",
    page_icon="🎬",
    layout="centered",
)

st.markdown(
    """
    <h2 style='text-align: center; color: #FF4B4B;'>🎬 Tạo Phụ Đề & Dịch Tự Động (Phong cách CapCut)</h2>
    <p style='text-align: center;'>Sử dụng mô hình <b>Whisper Large V3</b> và <b>LLaMA 3</b> mạnh nhất thế giới!</p>
    """,
    unsafe_allow_html=True,
)

# Sidebar cài đặt API Key
st.sidebar.header("🔑 Cấu hình hệ thống")
groq_api_key = st.sidebar.text_input(
    "Nhập Groq API Key của bạn:",
    type="password",
    help="Lấy key miễn phí tại console.groq.com",
)

target_language = st.sidebar.selectbox(
    "🌍 Ngôn ngữ dịch đích:",
    [
        "Vietnamese (Tiếng Việt)",
        "English (Tiếng Anh)",
        "Chinese (Tiếng Trung)",
        "Japanese (Tiếng Nhật)",
        "Korean (Tiếng Hàn)",
    ],
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Hướng dẫn:**\n1. Nhập Groq API Key.\n2. Tải lên video/audio.\n3. Nhấn nút"
    " xử lý để nhận phụ đề chuẩn từng từ."
)

# Khu vực tải lên file từ điện thoại/máy tính
uploaded_file = st.file_uploader(
    "📁 Tải lên Video hoặc Audio (Hỗ trợ .mp4, .mp3, .wav, .m4a)",
    type=["mp4", "mp3", "wav", "m4a"],
)

if uploaded_file is not None:
  st.video(uploaded_file)

  if st.button(
      "🚀 Bắt đầu Phân tích & Tạo Phụ Đề", type="primary", use_container_width=True
  ):
    if not groq_api_key:
      st.error("⚠️ Vui lòng nhập Groq API Key ở thanh bên trái (Sidebar)!")
    else:
      with st.spinner(
          "🔄 Đang xử lý âm thanh bằng Whisper Large V3 & Dịch thuật thông"
          " minh..."
      ):
        try:
          # Lưu file tạm thời để gửi qua API
          tfile = tempfile.NamedTemporaryFile(
              delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}"
          )
          tfile.write(uploaded_file.read())
          tfile.close()

          # Khởi tạo Groq Client
          client = Groq(api_key=groq_api_key)

          # Bước 1: Nhận diện giọng nói (Transcribe) lấy text và thời gian (timestamp)
          with open(tfile.name, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(tfile.name, file.read()),
                model="whisper-large-v3",
                response_format="verbose_json",
                timestamp_granularities=["word"],  # Lấy thời gian từng từ
            )

          os.unlink(tfile.name)  # Xóa file tạm

          # Trích xuất dữ liệu từ kết quả trả về
          words_data = getattr(transcription, "words", [])
          full_text = getattr(transcription, "text", "")

          # Bước 2: Dịch thuật sử dụng LLaMA 3 (70B) để đảm bảo văn phong tự nhiên như người bản xứ
          lang_name = target_language.split(" ")[0]
          translation_prompt = (
              f"Translate the following text into {lang_name}. Keep the"
              f" formatting natural, accurate, and suitable for video"
              f" subtitles:\n\n{full_text}"
          )

          chat_completion = client.chat.completions.create(
              messages=[{
                  "role": "user",
                  "content": translation_prompt,
              }],
              model="llama-3.3-70b-versatile",
          )
          translated_text = chat_completion.choices[0].message.content

          st.success("✨ Xử lý thành công hoàn toàn!")

          # Hiển thị kết quả bản dịch tổng quan
          st.subheader("📝 Bản dịch tổng quan:")
          st.info(translated_text)

          # Hiển thị phụ đề chia nhỏ từng từ/câu phong cách CapCut
          st.subheader("⏱️ Phụ đề chi tiết theo thời gian (CapCut Style):")

          if words_data:
            st.markdown(
                "Dưới đây là các mốc thời gian từng từ giúp bạn dễ dàng đồng bộ"
                " vào CapCut:"
            )
            # Hiển thị dạng danh sách mốc thời gian từng từ
            word_list_markdown = ""
            for w in words_data:
              start_t = w.get("start", 0)
              end_t = w.get("end", 0)
              word_val = w.get("word", "")
              word_list_markdown += (
                  f"`[{start_t:.2f}s - {end_t:.2f}s]` **{word_val}**  \n"
              )

            st.markdown(
                f"<div style='max-height: 300px; overflow-y: scroll;"
                f" padding: 10px; border: 1px solid #ccc; border-radius: 5px;'>{word_list_markdown}</div>",
                unsafe_allow_html=True,
            )
          else:
            st.warning(
                "Không lấy được mốc từ chi tiết, hiển thị theo phân đoạn câu:"
            )
            for segment in getattr(transcription, "segments", []):
              st.markdown(
                  f"`[{segment['start']:.2f}s -> {segment['end']:.2f}s]`"
                  f" **{segment['text']}**"
              )

        except Exception as e:
          st.error(f"❌ Đã xảy ra lỗi trong quá trình xử lý: {e}")
          
