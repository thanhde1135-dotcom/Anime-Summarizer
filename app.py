import streamlit as st
import os
import tempfile
import asyncio
from pathlib import Path
from pydub import AudioSegment
import edge_tts
from openai import OpenAI
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import subprocess

load_dotenv()

st.set_page_config(page_title="AI Lồng Tiếng Nhẹ", page_icon="🎬", layout="centered")
st.title("🎬 AI Lồng Tiếng + Dịch Phụ Đề (Bản Nhẹ)")
st.caption("Phiên bản tối ưu cho Streamlit Cloud")

# ================== CẤU HÌNH ==================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VOICE_MAP = {
    "vi": "vi-VN-HoaiMyNeural",
    "en": "en-US-JennyNeural",
    "zh-CN": "zh-CN-XiaoxiaoNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "th": "th-TH-PremwadeeNeural",
    "id": "id-ID-GadisNeural"
}

LANG_NAME = {
    "vi": "Tiếng Việt",
    "en": "English",
    "zh-CN": "中文",
    "ja": "日本語",
    "ko": "한국어",
    "th": "ไทย",
    "id": "Indonesia"
}

# ================== HÀM HỖ TRỢ ==================
def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result

def extract_audio(video_path, audio_path):
    run_cmd([
        "ffmpeg", "-y", "-i", str(video_path),
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        str(audio_path)
    ])

def transcribe_openai(audio_path):
    """Dùng OpenAI Whisper API (nhanh + chính xác, không cần torch)"""
    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json"
        )
    
    segments = []
    for seg in transcript.segments:
        segments.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip()
        })
    return segments

def translate_segments(segments, target_lang):
    translator = GoogleTranslator(source="auto", target=target_lang)
    result = []
    for seg in segments:
        try:
            translated = translator.translate(seg["text"])
        except:
            translated = seg["text"]
        result.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": translated
        })
    return result

async def tts_segment(text, voice, path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(path))

def create_dubbed_audio(segments, voice, output_path):
    final = AudioSegment.silent(duration=0)
    current = 0.0

    with tempfile.TemporaryDirectory() as tmp:
        for i, seg in enumerate(segments):
            start = seg["start"]
            end = seg["end"]
            duration_ms = int((end - start) * 1000)

            tts_file = Path(tmp) / f"seg_{i}.mp3"
            asyncio.run(tts_segment(seg["text"], voice, tts_file))

            audio = AudioSegment.from_file(tts_file)

            # Căn chỉnh độ dài
            if len(audio) > duration_ms:
                audio = audio[:duration_ms]
            else:
                audio += AudioSegment.silent(duration=duration_ms - len(audio))

            if start > current:
                silence = AudioSegment.silent(duration=int((start - current) * 1000))
                final += silence

            final += audio
            current = start + (len(audio) / 1000)

    final.export(output_path, format="wav")

def create_srt(segments, srt_path):
    def ts(t):
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = int(t % 60)
        ms = int((t % 1) * 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    lines = []
    for i, seg in enumerate(segments, 1):
        lines.append(str(i))
        lines.append(f"{ts(seg['start'])} --> {ts(seg['end'])}")
        lines.append(seg["text"])
        lines.append("")
    srt_path.write_text("\n".join(lines), encoding="utf-8")

def merge_video(video_path, audio_path, srt_path, output_path, burn=True):
    if burn:
        run_cmd([
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-vf", f"subtitles={srt_path}:force_style='FontSize=20,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=3'",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
            "-c:a", "aac", "-b:a", "128k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest",
            str(output_path)
        ])
    else:
        run_cmd([
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "128k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest",
            str(output_path)
        ])

# ================== GIAO DIỆN ==================
uploaded = st.file_uploader("Upload video", type=["mp4", "mov", "mkv", "webm"])

col1, col2 = st.columns(2)
with col1:
    target_lang = st.selectbox("Ngôn ngữ đích", list(LANG_NAME.keys()), format_func=lambda x: LANG_NAME[x])
with col2:
    burn_sub = st.checkbox("Đốt phụ đề vào video", value=True)

if uploaded and st.button("Bắt đầu xử lý", type="primary"):
    if not os.getenv("OPENAI_API_KEY"):
        st.error("Thiếu OPENAI_API_KEY. Hãy thêm vào Secrets của Streamlit.")
        st.stop()

    with st.status("Đang xử lý...", expanded=True) as status:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            video_path = tmp / "input.mp4"
            audio_path = tmp / "audio.wav"
            dubbed_path = tmp / "dubbed.wav"
            srt_path = tmp / "sub.srt"
            output_path = tmp / "output.mp4"

            video_path.write_bytes(uploaded.read())
            st.write("1. Đã nhận video")

            extract_audio(video_path, audio_path)
            st.write("2. Đã tách audio")

            st.write("3. Đang nhận diện giọng nói (OpenAI Whisper)...")
            segments = transcribe_openai(audio_path)
            st.write(f"   → {len(segments)} đoạn")

            st.write("4. Đang dịch phụ đề...")
            translated = translate_segments(segments, target_lang)
            st.write("   → Dịch xong")

            create_srt(translated, srt_path)
            st.write("5. Đã tạo file phụ đề")

            st.write("6. Đang tạo giọng lồng tiếng...")
            voice = VOICE_MAP.get(target_lang, "en-US-JennyNeural")
            create_dubbed_audio(translated, voice, dubbed_path)
            st.write("   → Lồng tiếng xong")

            st.write("7. Đang ghép video...")
            merge_video(video_path, dubbed_path, srt_path, output_path, burn_sub)

            status.update(label="Hoàn tất!", state="complete")

            st.success("Xử lý thành công!")
            st.video(str(output_path))

            with open(output_path, "rb") as f:
                st.download_button("Tải video", f, file_name="dubbed.mp4")

            with open(srt_path, "rb") as f:
                st.download_button("Tải phụ đề .srt", f, file_name="subtitle.srt")
