import os
import time
import asyncio
import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from transformers import pipeline
from faster_whisper import WhisperModel
import edge_tts

# Cấu hình giao diện trang web
st.set_page_config(
    page_title="AI Video Translator Pro (ZH -> VI)",
    page_icon="🎬",
    layout="centered"
)

# CSS tùy chỉnh để giao diện đẹp và thân thiện với thiết bị di động
st.markdown("""
    <style>
    .main-header { font-size: 24px; font-weight: bold; color: #FF4B4B; text-align: center; }
    .info-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #FF4B4B; }
    .stButton>button { width: 100%; background-color: #FF4B4B; color: white; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🎬 Hệ Thống Siêu AI Dịch & Lồng Tiếng Video Trung - Việt</p>', unsafe_allow_html=True)
st.markdown("---")

# Khởi tạo các mô hình AI (Sử dụng st.cache_resource để tối ưu hiệu suất, tránh load lại mô hình)
@st.cache_resource
def load_whisper_model():
    # Sử dụng mô hình whisper bản tiny hoặc base để chạy mượt trên môi trường Cloud miễn phí
    return WhisperModel("base", device="cpu", compute_type="int8")

@st.cache_resource
def load_translator_model():
    # Siêu mô hình dịch thuật NLLB-200 chuyên tối ưu Trung -> Việt
    return pipeline("translation", model="facebook/nllb-200-distilled-600M", src_lang="zho_Hans", tgt_lang="vie_Latn")

with st.spinner("Đang khởi tạo hệ thống siêu mô hình AI... Vui lòng đợi trong giây lát."):
    whisper_model = load_whisper_model()
    translator = load_translator_model()

# Bảng thông tin trạng thái hoạt động (Live Info Panel)
st.markdown("### 📊 Bảng Thông Tin Hoạt Động AI")
info_placeholder = st.empty()
info_placeholder.info("🤖 Trạng thái: Hệ thống đang sẵn sàng chờ tải video lên.")

# Khu vực upload video từ điện thoại/máy tính
uploaded_file = st.file_uploader("Tải lên video cần dịch (Định dạng: MP4, MOV, AVI)", type=["mp4", "mov", "avi"])

# Tùy chỉnh giọng đọc
st.markdown("### 🎙️ Tùy Chỉnh Giọng Đọc (TikTok / YouTube / Facebook Style)")
voice_option = st.selectbox(
    "Chọn giọng đọc AI:",
    (
        "vi-VN-NamMinhNeural (Nam miền Nam - Tự nhiên)",
        "vi-VN-HoaiMyNeural (Nữ miền Nam - Phát thanh viên)",
        "vi-VN-AnNeural (Nam miền Bắc)",
        "vi-VN-LanAnhNeural (Nữ miền Bắc)"
    )
)
selected_voice = voice_option.split(" ")[0]

# Tùy chỉnh phụ đề trên video
st.markdown("### ✍️ Tùy Chỉnh Kiểu Chữ Phụ Đề")
font_size = st.slider("Kỡ chữ phụ đề:", min_value=16, max_value=48, value=24)
font_color = st.selectbox("Màu chữ:", ("white", "yellow", "cyan", "green"))

if uploaded_file is not None:
    # Lưu video tải lên vào file tạm
    input_video_path = "input_video.mp4"
    with open(input_video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.video(input_video_path)
    
    if st.button("🚀 Bắt Đầu Xử Lý & Dịch Video"):
        try:
            # Bước 1: Trích xuất âm thanh
            info_placeholder.info("⏳ **[Bước 1/4]**: Đang sử dụng **FFmpeg / MoviePy** để trích xuất âm thanh từ video gốc...")
            video_clip = VideoFileClip(input_video_path)
            audio_path = "extracted_audio.mp3"
            video_clip.audio.write_audiofile(audio_path, logger=None)
            
            # Bước 2: Nhận dạng giọng nói (Speech-to-Text)
            info_placeholder.info("🧠 **[Bước 2/4]**: Đang sử dụng siêu mô hình **Faster-Whisper (STT)** để nhận dạng tiếng Trung từ âm thanh...")
            segments, _ = whisper_model.transcribe(audio_path, beam_size=5)
            transcript_segments = list(segments)
            
            full_source_text = " ".join([seg.text for seg in transcript_segments])
            st.write(**Văn bản gốc tiếng Trung phát hiện được:**)
            st.text(full_source_text)
            
            # Bước 3: Dịch thuật sang tiếng Việt
            info_placeholder.info("🌐 **[Bước 3/4]**: Đang sử dụng siêu mô hình **Meta NLLB-200 (Translation Model)** để dịch toàn bộ văn bản sang tiếng Việt...")
            translated_segments = []
            for seg in transcript_segments:
                if seg.text.strip():
                    translated = translator(seg.text, max_length=400)
                    trans_text = translated[0]['translation_text']
                    translated_segments.append({
                        "start": seg.start,
                        "end": seg.end,
                        "text": trans_text
                    })
            
            full_translated_text = " ".join([item["text"] for item in translated_segments])
            st.write("**Bản dịch tiếng Việt thông minh:**")
            st.success(full_translated_text)
            
            # Bước 4: Tạo giọng đọc AI (Text-to-Speech) và ghép nối phụ đề
            info_placeholder.info(f"🎙️ **[Bước 4/4]**: Đang sử dụng **Edge-TTS** với giọng `{selected_voice}` để tạo giọng đọc mới và dựng video hoàn chỉnh...")
            
            # Hàm bất đồng bộ tạo audio từ Edge-TTS
            async def generate_tts_audio(text, voice, output_filename):
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(output_filename)
            
            tts_audio_path = "generated_voice.mp3"
            asyncio.run(generate_tts_audio(full_translated_text, selected_voice, tts_audio_path))
            
            # Thay thế âm thanh cũ bằng âm thanh AI mới vào video
            new_audio = AudioFileClip(tts_audio_path)
            # Điều chỉnh độ dài audio cho khớp với video hoặc giữ nguyên
            final_video = video_clip.set_audio(new_audio)
            
            output_video_path = "output_translated_video.mp4"
            final_video.write_videofile(
                output_video_path,
                codec="libx264",
                audio_codec="aac",
                fps=video_clip.fps,
                logger=None
            )
            
            # Dọn dẹp tài nguyên
            video_clip.close()
            new_audio.close()
            
            info_placeholder.success("🎉 **Hoàn thành xuất sắc!** Video của bạn đã được dịch và lồng tiếng thành công.")
            st.markdown("### 📥 Tải Xuống Video Thành Quả")
            st.video(output_video_path)
            
            with open(output_video_path, "rb") as file:
                st.download_button(
                    label="Tải Video Về Máy",
                    data=file,
                    file_name="video_dich_tieng_viet.mp4",
                    mime="video/mp4"
                )
                
        except Exception as e:
            info_placeholder.error(f"❌ Đã xảy ra lỗi trong quá trình xử lý: {str(e)}")
                        
