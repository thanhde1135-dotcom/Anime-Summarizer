import os
import subprocess
import tempfile
import streamlit as st
from groq import Groq

st.set_page_config(page_title="Video Subtitle & Blur Editor", page_icon="🎬")

st.markdown(
    "<h2>🎬 Chỉnh Sửa Video, Làm Mờ & Đóng Phụ Đề Chuẩn Xác</h2>",
    unsafe_allow_html=True,
)


def generate_srt(words_data, chunk_size=4):
  srt_content = ""
  sub_index = 1

  def format_srt_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millisecs:03d}"

  for i in range(0, len(words_data), chunk_size):
    chunk = words_data[i : i + chunk_size]
    if not chunk:
      continue
    start_t = chunk[0].get("start", 0)
    end_t = chunk[-1].get("end", start_t + 2)
    chunk_text = " ".join([w.get("word", "") for w in chunk])
    srt_content += f"{sub_index}\n"
    srt_content += f"{format_srt_time(start_t)} --> {format_srt_time(end_t)}\n"
    srt_content += f"{chunk_text}\n\n"
    sub_index += 1
  return srt_content


groq_api_key = st.sidebar.text_input(
    "Nhập Groq API Key:", type="password", key="v_key"
)
st.sidebar.markdown("---")
sub_position = st.sidebar.selectbox(
    "Vị trí hiển thị chữ:",
    ["Phía dưới video (Mặc định)", "Phía trên video", "Chính giữa video"],
)
sub_margin_v = st.sidebar.slider("Khoảng cách lề:", 10, 200, 30)
enable_blur = st.sidebar.checkbox("Bật làm mờ video")
blur_strength = st.sidebar.slider("Độ mờ:", 1, 30, 10)
blur_region = st.sidebar.selectbox(
    "Vùng làm mờ:", ["Toàn bộ video", "Chỉ làm mờ nửa dưới video"]
)

uploaded_file = st.file_uploader(
    "📁 Tải lên Video (MP4, MOV)", type=["mp4", "mov", "avi"]
)

if uploaded_file is not None:
  st.video(uploaded_file)
  if st.button("🚀 Xử lý Video & Đóng Phụ Đề", type="primary"):
    if not groq_api_key:
      st.error("⚠️ Vui lòng nhập Groq API Key!")
    else:
      with st.spinner("🔄 Đang xử lý..."):
        try:
          input_ext = uploaded_file.name.split(".")[-1].lower()
          with tempfile.NamedTemporaryFile(
              delete=False, suffix=f".{input_ext}"
          ) as tmp_in:
            tmp_in.write(uploaded_file.read())
            input_path = tmp_in.name

          processed_video_path = input_path
          if enable_blur:
            blurred_output = input_path + "_blurred.mp4"
            if blur_region == "Toàn bộ video":
              cmd_blur = [
                  "ffmpeg",
                  "-y",
                  "-i",
                  input_path,
                  "-vf",
                  f"boxblur={blur_strength}:1",
                  "-c:a",
                  "copy",
                  blurred_output,
              ]
            else:
              cmd_blur = [
                  "ffmpeg",
                  "-y",
                  "-i",
                  input_path,
                  "-filter_complex",
                  (
                      f"[0:v]split[v1][v2];[v2]crop=iw:ih/2:0:ih/2,boxblur={blur_strength}:1[blv];[v1][blv]overlay=0:ih/2"
                  ),
                  "-c:a",
                  "copy",
                  blurred_output,
              ]
            subprocess.run(
                cmd_blur, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            if os.path.exists(blurred_output) and os.path.getsize(
                blurred_output
            ) > 0:
              processed_video_path = blurred_output

          output_audio_path = input_path + ".mp3"
          cmd_audio = [
              "ffmpeg",
              "-y",
              "-i",
              processed_video_path,
              "-vn",
              "-acodec",
              "libmp3lame",
              "-ab",
              "128k",
              output_audio_path,
          ]
          subprocess.run(
              cmd_audio, stdout=subprocess.PIPE, stderr=subprocess.PIPE
          )
          target_audio = (
              output_audio_path
              if os.path.exists(output_audio_path)
              else input_path
          )

          client = Groq(api_key=groq_api_key)
          with open(target_audio, "rb") as f_audio:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(target_audio), f_audio.read()),
                model="whisper-large-v3",
                response_format="verbose_json",
                timestamp_granularities=["word"],
            )
          if os.path.exists(output_audio_path):
            os.unlink(output_audio_path)

          words_data = getattr(transcription, "words", [])
          full_text = getattr(transcription, "text", "")

          translation_prompt = (
              "Translate the following text into natural, fluent Vietnamese:\n"
              + full_text
          )
          chat_completion = client.chat.completions.create(
              messages=[{"role": "user", "content": translation_prompt}],
              model="llama-3.3-70b-versatile",
          )
          translated_text = chat_completion.choices[0].message.content

          srt_str = generate_srt(words_data, chunk_size=4)
          srt_file_path = input_path + ".srt"
          with open(srt_file_path, "w", encoding="utf-8") as f:
            f.write(srt_str)

          final_output_video = input_path + "_final.mp4"
          alignment_code = (
              6
              if sub_position == "Phía trên video"
              else (5 if sub_position == "Chính giữa video" else 2)
          )
          subtitle_filter = (
              f"subtitles={os.path.basename(srt_file_path)}:force_style="
              f"'FontName=Arial,FontSize=20,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,"
              f"BorderStyle=1,Outline=2,Shadow=1,Alignment={alignment_code},MarginV={sub_margin_v}'"
          )

          current_dir = os.getcwd()
          file_dir = os.path.dirname(input_path)
          if file_dir:
            os.chdir(file_dir)
          cmd_burn = [
              "ffmpeg",
              "-y",
              "-i",
              os.path.basename(processed_video_path),
              "-vf",
              subtitle_filter,
              "-c:a",
              "copy",
              os.path.basename(final_output_video),
          ]
          subprocess.run(
              cmd_burn, stdout=subprocess.PIPE, stderr=subprocess.PIPE
          )
          os.chdir(current_dir)

          result_video = (
              os.path.join(file_dir, os.path.basename(final_output_video))
              if os.path.exists(
                  os.path.join(file_dir, os.path.basename(final_output_video))
              )
              else processed_video_path
          )

          if os.path.exists(srt_file_path):
            os.unlink(srt_file_path)
          if os.path.exists(input_path):
            os.unlink(input_path)

          st.success("✨ Hoàn tất!")
          if os.path.exists(result_video):
            st.video(result_video)
            with open(result_video, "rb") as f_vid:
              st.download_button(
                  "📥 Tải xuống Video",
                  f_vid.read(),
                  file_name="video_sub.mp4",
                  mime="video/mp4",
              )
          st.info(translated_text)
        except Exception as e:
          st.error(f"Lỗi: {e}")
    
