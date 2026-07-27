import os
import subprocess
import tempfile
from groq import Groq


def generate_srt(words_data, chunk_size=4):
  """Tạo nội dung file SRT chuẩn phong cách CapCut từ dữ liệu từ của Whisper"""
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


def process_video_with_custom_subtitles(
    uploaded_file,
    groq_api_key,
    enable_blur,
    blur_strength,
    blur_region,
    sub_position,
    sub_margin_v,
):
  try:
    # 1. Lưu file video gốc tạm thời
    input_ext = uploaded_file.name.split(".")[-1].lower()
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=f".{input_ext}"
    ) as tmp_in:
      tmp_in.write(uploaded_file.read())
      input_path = tmp_in.name

    processed_video_path = input_path

    # 2. Xử lý làm mờ video nếu được bật
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
      subprocess.run(cmd_blur, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      if os.path.exists(blurred_output) and os.path.getsize(blurred_output) > 0:
        processed_video_path = blurred_output

    # 3. Trích xuất âm thanh gửi cho Whisper
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
    subprocess.run(cmd_audio, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    target_audio = (
        output_audio_path if os.path.exists(output_audio_path) else input_path
    )

    # 4. Nhận diện giọng nói chuẩn từng từ bằng Whisper Large V3
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

    # 5. Dịch thuật nâng cao chuẩn 100% tiếng Việt bằng LLaMA 3
    translation_prompt = (
        "You are a professional native Vietnamese translator and localization"
        " expert for video subtitles.\nTranslate the following text into"
        " natural, fluent Vietnamese.\nStrict translation rules:\n1. Translate"
        " ALL foreign currency terms (such as 块钱) into standard Vietnamese"
        " currency terms (e.g., 'tệ' or 'VND').\n2. Translate and convert ALL"
        " units of measurement and weight (such as 克, 斤) into standard"
        " Vietnamese equivalents (e.g., gram, kg, cân).\n3. Do NOT leave any raw"
        " Chinese characters; fully translate or transliterate them.\n4. Ensure"
        " the tone is extremely natural and suitable for video"
        " subtitles.\n\nText to translate:\n"
        + full_text
    )

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": translation_prompt}],
        model="llama-3.3-70b-versatile",
    )
    translated_text = chat_completion.choices[0].message.content

    # 6. Tạo file SRT phụ đề tiếng Việt
    srt_str = generate_srt(words_data, chunk_size=4)
    srt_file_path = input_path + ".srt"
    with open(srt_file_path, "w", encoding="utf-8") as f:
      f.write(srt_str)

    # 7. Chèn phụ đề trực tiếp vào video (Burn-in) với vị trí tùy chỉnh qua FFmpeg
    final_output_video = input_path + "_final.mp4"

    # Cấu hình vị trí (Alignment): 2=Dưới, 6=Trên, 5=Giữa
    alignment_code = 2
    if sub_position == "Phía trên video":
      alignment_code = 6
    elif sub_position == "Chính giữa video":
      alignment_code = 5

    # Định dạng style phụ đề: Màu vàng, chữ đậm, viền đen rõ nét, điều chỉnh khoảng cách lề
    subtitle_filter = (
        f"subtitles={os.path.basename(srt_file_path)}:force_style="
        f"'FontName=Arial,FontSize=20,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,"
        f"BorderStyle=1,Outline=2,Shadow=1,Alignment={alignment_code},MarginV={sub_margin_v}'"
    )

    # Đổi thư mục làm việc tạm thời để FFmpeg nhận diện file SRT tiếng Việt không lỗi đường dẫn
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
    subprocess.run(cmd_burn, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    os.chdir(current_dir)  # Khôi phục thư mục

    result_video = (
        os.path.join(file_dir, os.path.basename(final_output_video))
        if os.path.exists(os.path.join(file_dir, os.path.basename(final_output_video)))
        else processed_video_path
    )

    # Dọn dẹp file tạm không cần thiết
    if os.path.exists(srt_file_path):
      os.unlink(srt_file_path)
    if os.path.exists(input_path):
      os.unlink(input_path)

    return True, {
        "translated_text": translated_text,
        "words_data": words_data,
        "srt_content": srt_str,
        "final_video_path": result_video,
    }

  except Exception as e:
    return False, str(e)
    
