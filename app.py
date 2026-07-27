import streamlit as st
import os
import tempfile
import subprocess
from pathlib import Path

st.set_page_config(page_title="AI Dubbing", page_icon="🎬", layout="centered")
st.title("🎬 AI Dịch phụ đề + Lồng tiếng")
st.caption("Phiên bản nhẹ - dùng trên điện thoại qua trình duyệt")

# --- Upload ---
uploaded_file = st.file_uploader("Chọn video", type=["mp4", "mov", "mkv", "webm"])

target_lang = st.selectbox(
    "Ngôn ngữ đích",
    ["vi", "en", "zh-cn", "ja", "ko", "th", "id"],
    format_func=lambda x: {
        "vi": "Tiếng Việt",
        "en": "English",
        "zh-cn": "中文",
        "ja": "日本語",
        "ko": "한국어",
        "th": "ไทย",
        "id": "Indonesia"
    }[x]
)

if uploaded_file and st.button("Bắt đầu xử lý", type="primary"):
    with st.spinner("Đang xử lý... (có thể mất vài phút)"):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.mp4"
            with open(input_path, "wb") as f:
                f.write(uploaded_file.read())

            # 1. Tách audio
            audio_path = Path(tmpdir) / "audio.wav"
            subprocess.run([
                "ffmpeg", "-y", "-i", str(input_path),
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                str(audio_path)
            ], check=True, capture_output=True)

            # 2. Nhận diện (dùng faster-whisper tiny để nhẹ)
            from faster_whisper import WhisperModel
            model = WhisperModel("tiny", device="cpu", compute_type="int8")
            segments, info = model.transcribe(str(audio_path), beam_size=1)

            # 3. Dịch (dùng deep-translator - nhẹ)
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source="auto", target=target_lang)

            srt_lines = []
            translated_texts = []
            for i, seg in enumerate(segments, 1):
                start = seg.start
                end = seg.end
                text = seg.text.strip()
                translated = translator.translate(text)
                translated_texts.append((start, end, translated))

                # Tạo SRT
                def format_time(t):
                    h = int(t // 3600)
                    m = int((t % 3600) // 60)
                    s = int(t % 60)
                    ms = int((t % 1) * 1000)
                    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

                srt_lines.append(f"{i}\n{format_time(start)} --> {format_time(end)}\n{translated}\n")

            srt_path = Path(tmpdir) / "sub.srt"
            srt_path.write_text("\n".join(srt_lines), encoding="utf-8")

            # 4. Tạo giọng nói (Edge-TTS - miễn phí, chất lượng ổn)
            import edge_tts
            import asyncio

            async def generate_tts():
                communicate = edge_tts.Communicate(
                    " ".join([t[2] for t in translated_texts]),
                    voice="vi-VN-HoaiMyNeural" if target_lang == "vi" else "en-US-JennyNeural"
                )
                tts_path = Path(tmpdir) / "tts.mp3"
                await communicate.save(str(tts_path))
                return tts_path

            tts_path = asyncio.run(generate_tts())

            # 5. Ghép lại (đơn giản - thay toàn bộ audio)
            output_path = Path(tmpdir) / "output.mp4"
            subprocess.run([
                "ffmpeg", "-y",
                "-i", str(input_path),
                "-i", str(tts_path),
                "-c:v", "copy",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                str(output_path)
            ], check=True, capture_output=True)

            # Hiển thị kết quả
            st.success("Xong!")
            st.video(str(output_path))
            with open(output_path, "rb") as f:
                st.download_button("Tải video đã lồng tiếng", f, file_name="dubbed.mp4")
