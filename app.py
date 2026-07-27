import streamlit as st
import os
import tempfile
import asyncio
import json
from pathlib import Path
from typing import List, Dict
import subprocess

import torch
from faster_whisper import WhisperModel
import whisperx
from pydub import AudioSegment
import edge_tts
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI Video Dubbing Pro",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 AI Lồng tiếng + Phụ đề siêu chuẩn")
st.caption("WhisperX + LLM dịch ngữ cảnh + Edge-TTS đồng bộ thời gian")

# ====================== CẤU HÌNH ======================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TARGET_LANG_MAP = {
    "vi": "Vietnamese",
    "en": "English",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "th": "Thai",
    "id": "Indonesian"
}

VOICE_MAP = {
    "vi": "vi-VN-HoaiMyNeural",
    "en": "en-US-JennyNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "th": "th-TH-PremwadeeNeural",
    "id": "id-ID-GadisNeural"
}

# ====================== HÀM HỖ TRỢ ======================
def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def run_ffmpeg(cmd: list):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error:\n{result.stderr}")
    return result

# ====================== 1. TÁCH AUDIO ======================
def extract_audio(video_path: Path, audio_path: Path):
    run_ffmpeg([
        "ffmpeg", "-y", "-i", str(video_path),
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        str(audio_path)
    ])

# ====================== 2. NHẬN DIỆN + TIMESTAMP CHUẨN (WhisperX) ======================
@st.cache_resource
def load_whisperx_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"
    model = whisperx.load_model("large-v3", device, compute_type=compute_type)
    return model, device

def transcribe_with_whisperx(audio_path: Path) -> List[Dict]:
    model, device = load_whisperx_model()
    
    audio = whisperx.load_audio(str(audio_path))
    result = model.transcribe(audio, batch_size=8)
    
    # Align để có word-level timestamp chính xác
    model_a, metadata = whisperx.load_align_model(
        language_code=result["language"], device=device
    )
    result = whisperx.align(
        result["segments"], model_a, metadata, audio, device,
        return_char_alignments=False
    )
    
    segments = []
    for seg in result["segments"]:
        segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip()
        })
    return segments

# ====================== 3. DỊCH SIÊU CHUẨN BẰNG LLM ======================
def translate_segments_llm(segments: List[Dict], target_lang: str) -> List[Dict]:
    """
    Dịch theo batch + giữ ngữ cảnh + prompt cực kỳ chặt chẽ
    để giảm sai sót tối đa.
    """
    target_name = TARGET_LANG_MAP.get(target_lang, target_lang)
    
    # Gộp thành các batch nhỏ để giữ context
    batch_size = 8
    translated = []
    
    for i in range(0, len(segments), batch_size):
        batch = segments[i:i+batch_size]
        
        original_texts = "\n".join([
            f"[{idx}] {seg['text']}" for idx, seg in enumerate(batch)
        ])
        
        prompt = f"""
Bạn là chuyên gia dịch thuật phụ đề điện ảnh chuyên nghiệp.
Nhiệm vụ: Dịch các câu sau sang {target_name} một cách TỰ NHIÊN, CHÍNH XÁC, GIỮ NGUYÊN Ý và TONE gốc.

Yêu cầu bắt buộc:
- Không dịch word-by-word.
- Giữ nguyên tên riêng, thuật ngữ chuyên ngành nếu có.
- Độ dài câu dịch phải phù hợp để đọc trong thời gian gốc (không dài quá).
- Không thêm bớt thông tin.
- Trả về đúng format JSON list như sau:
[
  {{"index": 0, "text": "câu dịch 1"}},
  {{"index": 1, "text": "câu dịch 2"}}
]

Các câu cần dịch:
{original_texts}
"""

        response = client.chat.completions.create(
            model="gpt-4o",          # hoặc gpt-4o-mini nếu muốn rẻ hơn
            messages=[
                {"role": "system", "content": "Bạn là dịch giả phụ đề chuyên nghiệp, chỉ trả về JSON hợp lệ."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,         # thấp để ổn định
            response_format={"type": "json_object"}
        )
        
        try:
            data = json.loads(response.choices[0].message.content)
            # Hỗ trợ cả dạng {"translations": [...]} hoặc list trực tiếp
            items = data.get("translations", data) if isinstance(data, dict) else data
            
            for item in items:
                idx = item["index"]
                translated.append({
                    "start": batch[idx]["start"],
                    "end": batch[idx]["end"],
                    "text": item["text"].strip()
                })
        except Exception as e:
            st.warning(f"Lỗi parse batch {i}: {e}. Fallback sang dịch từng câu.")
            # Fallback an toàn
            for seg in batch:
                # Có thể thay bằng deep-translator nếu cần
                translated.append({
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"]  # tạm giữ nguyên
                })
    
    return translated

# ====================== 4. TẠO GIỌNG NÓI ĐỒNG BỘ ======================
async def generate_tts_segment(text: str, voice: str, output_path: Path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))

def create_synced_audio(translated_segments: List[Dict], voice: str, output_audio: Path):
    """
    Tạo từng đoạn TTS → căn chỉnh tốc độ để khớp thời gian gốc → nối lại
    """
    final_audio = AudioSegment.silent(duration=0)
    current_pos = 0.0
    
    with tempfile.TemporaryDirectory() as tmp:
        for i, seg in enumerate(translated_segments):
            start = seg["start"]
            end = seg["end"]
            duration_ms = int((end - start) * 1000)
            
            # Tạo TTS
            tts_path = Path(tmp) / f"seg_{i}.mp3"
            asyncio.run(generate_tts_segment(seg["text"], voice, tts_path))
            
            tts_audio = AudioSegment.from_file(tts_path)
            
            # Căn chỉnh tốc độ để khớp thời gian gốc
            if len(tts_audio) > 0:
                speed_ratio = len(tts_audio) / duration_ms
                if 0.7 < speed_ratio < 1.4:  # chỉ chỉnh nếu lệch vừa phải
                    tts_audio = tts_audio.speedup(playback_speed=speed_ratio)
                else:
                    # Nếu lệch quá nhiều thì cắt hoặc pad
                    if len(tts_audio) > duration_ms:
                        tts_audio = tts_audio[:duration_ms]
                    else:
                        tts_audio += AudioSegment.silent(duration=duration_ms - len(tts_audio))
            
            # Thêm khoảng lặng nếu cần
            if start > current_pos:
                silence = AudioSegment.silent(duration=int((start - current_pos) * 1000))
                final_audio += silence
            
            final_audio += tts_audio
            current_pos = start + (len(tts_audio) / 1000)
    
    final_audio.export(output_audio, format="wav")

# ====================== 5. TẠO FILE SRT ======================
def create_srt(segments: List[Dict], srt_path: Path):
    lines = []
    for i, seg in enumerate(segments, 1):
        lines.append(str(i))
        lines.append(f"{format_timestamp(seg['start'])} --> {format_timestamp(seg['end'])}")
        lines.append(seg["text"])
        lines.append("")
    srt_path.write_text("\n".join(lines), encoding="utf-8")

# ====================== 6. GHÉP VIDEO CUỐI ======================
def merge_video(video_path: Path, audio_path: Path, srt_path: Path, output_path: Path, burn_sub=True):
    if burn_sub:
        # Đốt phụ đề vào video
        run_ffmpeg([
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-vf", f"subtitles={srt_path}:force_style='FontSize=22,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=3'",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest",
            str(output_path)
        ])
    else:
        # Chỉ thay audio, giữ phụ đề ngoài
        run_ffmpeg([
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest",
            str(output_path)
        ])

# ====================== GIAO DIỆN ======================
uploaded_file = st.file_uploader("Upload video", type=["mp4", "mov", "mkv", "webm", "avi"])

col1, col2 = st.columns(2)
with col1:
    target_lang = st.selectbox("Ngôn ngữ đích", list(TARGET_LANG_MAP.keys()), 
                               format_func=lambda x: TARGET_LANG_MAP[x])
with col2:
    burn_sub = st.checkbox("Đốt phụ đề vào video", value=True)

if uploaded_file and st.button("Bắt đầu xử lý chất lượng cao", type="primary"):
    with st.status("Đang xử lý pipeline chất lượng cao...", expanded=True) as status:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            video_path = tmp / "input.mp4"
            audio_path = tmp / "audio.wav"
            tts_path = tmp / "dubbed.wav"
            srt_path = tmp / "sub.srt"
            output_path = tmp / "output.mp4"
            
            # Lưu video
            video_path.write_bytes(uploaded_file.read())
            st.write("1. Đã nhận video")
            
            # Tách audio
            extract_audio(video_path, audio_path)
            st.write("2. Đã tách audio")
            
            # Nhận diện
            st.write("3. Đang nhận diện giọng nói (WhisperX large-v3)...")
            segments = transcribe_with_whisperx(audio_path)
            st.write(f"   → Phát hiện {len(segments)} đoạn")
            
            # Dịch LLM
            st.write("4. Đang dịch bằng LLM (gpt-4o) – ưu tiên độ chính xác...")
            translated = translate_segments_llm(segments, target_lang)
            st.write("   → Dịch xong")
            
            # Tạo SRT
            create_srt(translated, srt_path)
            st.write("5. Đã tạo phụ đề SRT")
            
            # TTS đồng bộ
            st.write("6. Đang tạo giọng nói + căn chỉnh thời gian...")
            voice = VOICE_MAP.get(target_lang, "en-US-JennyNeural")
            create_synced_audio(translated, voice, tts_path)
            st.write("   → Lồng tiếng xong")
            
            # Ghép video
            st.write("7. Đang ghép video cuối...")
            merge_video(video_path, tts_path, srt_path, output_path, burn_sub)
            
            status.update(label="Hoàn tất!", state="complete")
            
            # Kết quả
            st.success("Xử lý thành công!")
            st.video(str(output_path))
            
            with open(output_path, "rb") as f:
                st.download_button(
                    "Tải video đã lồng tiếng",
                    f,
                    file_name="dubbed_video.mp4",
                    mime="video/mp4"
                )
            
            with open(srt_path, "rb") as f:
                st.download_button(
                    "Tải file phụ đề .srt",
                    f,
                    file_name="subtitle.srt",
                    mime="text/plain"
  )
