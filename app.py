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
    <p style='text-align: center;'>Sử dụng mô hình <b>Whisper Large V3</b> và <b>LLaMA 3 (70B)</b> bản tối ưu hóa dịch thuật!</p>
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
    "💡 **Mẹo:** Hệ thống đã được lập trình để lọc và Việt hóa 100% các thuật"
    " ngữ, tiền tệ và đơn vị đo lường."
)

# Khu vực tải lên file từ điện thoại/máy tính
uploaded_file = st.file_uploader(
    "📁 Tải lên Video hoặc Audio bất kỳ", type=["mp4", "mp3", "wav", "m4a"]
)

if uploaded_file is not None:
  st.video(uploaded_file)

  if st.button(
      "🚀 Bắt đầu Phân tích & Dịch chuẩn 100%",
      type="primary",
      use_container_width=True,
  ):
    if not groq_api_key:
      st.error("⚠️ Vui lòng nhập Groq API Key ở thanh bên trái (Sidebar)!")
    else:
      with st.spinner(
          "🔄 Đang xử lý âm thanh và dịch thuật chuẩn hóa hoàn toàn..."
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

          # Tự động trích xuất audio bằng ffmpeg
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

            # Bước 2: Dịch thuật nâng cao với LLaMA 3 (Ép Việt hóa 100%)
            lang_name = target_language.split(" ")[0]
            translation_prompt = (
                f"You are a professional native {lang_name} translator and"
                " localization expert for video subtitles.\nTranslate the"
                " following text into natural, fluent {lang_name}.\nStrict"
                " translation rules:\n1. Translate ALL foreign currency terms"
                " (such as 块钱) into standard Vietnamese currency terms (e.g.,"
                " 'tệ' or 'NDT').\n2. Translate and convert ALL units of"
                " measurement and weight (such as 克, 斤) into standard"
                " Vietnamese equivalents (e.g., gram, kg, cân).\n3. Do NOT leave"
                " any raw Chinese characters (漢字) in the output text; fully"
                " translate or transliterate them into Vietnamese names or"
                " words.\n4. Ensure the tone is extremely natural, professional,"
                " and perfectly suited for video subtitles.\n\nText to"
                f" translate:\n{full_text}"
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
            st.subheader("📝 Bản dịch tổng quan (Chuẩn 100%):")
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
                  
