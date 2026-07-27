import os
import subprocess
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
    "💡 **Hệ thống tự động:** Video nặng sẽ được tự động tách lấy âm thanh siêu"
    " nhẹ để gửi cho AI, không lo giới hạn dung lượng!"
)

# Khu vực tải lên file từ điện thoại/máy tính
uploaded_file = st.file_uploader(
    "📁 Tải lên Video hoặc Audio bất kỳ", type=["mp4", "mp3", "wav", "m4a"]
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
          "🔄 Đang tự động tách âm thanh và phân tích bằng Whisper Large V3..."
      ):
        try:
          # Lưu file gốc tạm thời
          input_ext = uploaded_file.name.split(".")[-1].lower()
          with tempfile.NamedTemporaryFile(
              delete=False, suffix=f".{input_ext}"
          ) as tmp_in:
            tmp_in.write(uploaded_file.read())
            input_path = tmp_in.name

          output_audio_path = input_path + ".mp3"

          # Tự động dùng ffmpeg trích xuất audio từ video để giảm dung lượng xuống dưới 25MB
          cmd = [
              "ffmpeg",
              "-y",
              "-i",
              input_path,
              "-vn",
              "-acodec",
              "libmp3lame",
              "-ab",
              "128k",
              output_audio_path,
          ]
          subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

          # Chọn file audio đã trích xuất (hoặc file gốc nếu là mp3)
          target_file = (
              output_audio_path
              if os.path.exists(output_audio_path)
              else input_path
          )
          file_size_mb = os.path.getsize(target_file) / (1024 * 1024)

          if file_size_mb > 25:
            st.error(
                f"❌ File âm thanh quá lớn ({file_size_mb:.1f}MB). Vui lòng chọn"
                " video ngắn hơn!"
            )
          else:
            # Khởi tạo Groq Client
            client = Groq(api_key=groq_api_key)

            # Bước 1: Nhận diện giọng nói
            with open(target_file, "rb") as file:
              transcription = client.audio.transcriptions.create(
                  file=(os.path.basename(target_file), file.read()),
                  model="whisper-large-v3",
                  response_format="verbose_json",
                  timestamp_granularities=["word"],
              )

            # Xóa các file tạm
            os.unlink(input_path)
            if os.path.exists(output_audio_path):
              os.unlink(output_audio_path)

            words_data = getattr(transcription, "words", [])
            full_text = getattr(transcription, "text", "")

            # Bước 2: Dịch thuật sử dụng LLaMA 3
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

            # Hiển thị phụ đề chi tiết phong cách CapCut
            st.subheader("⏱️ Phụ đề chi tiết theo thời gian (CapCut Style):")

            if words_data:
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
              for segment in getattr(transcription, "segments", []):
                st.markdown(
                    f"`[{segment['start']:.2f}s -> {segment['end']:.2f}s]`"
                    f" **{segment['text']}**"
                )

        except Exception as e:
          st.error(f"❌ Đã xảy ra lỗi trong quá trình xử lý: {e}")
        
