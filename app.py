import os
import json
import asyncio
import tempfile
import ffmpeg
import streamlit as st
import pandas as pd
from groq import Groq
import edge_tts

st.set_page_config(
    page_title="Vietsub Tool v5.0 - Professional Studio",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stTextInput>div>div>input { background-color: #262730; color: #ffffff; border: 1px solid #4f4f4f; }
    .stSelectbox>div>div>select { background-color: #262730; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #ff4b4b; color: white; border: none; padding: 0.6rem; }
    .stButton>button:hover { background-color: #ff2b2b; }
    div.block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

st.title("🎬 Vietsub Tool v5.0 - Professional Studio")
st.caption("Công cụ tự động hóa video, dịch thuật AI, lồng tiếng chuyên nghiệp với bảng chỉnh sửa trực quan.")

with st.sidebar:
    st.header("⚙️ Cấu Hình API & AI")
    groq_api_key = st.text_input("Groq API Key (gsk_...):", type="password", help="Dùng cho Whisper STT & Llama Translation")
    
    st.markdown("---")
    st.header("🌐 Ngôn Ngữ & Giọng Đọc")
    target_language = st.selectbox("Ngôn ngữ đích cần dịch:", ["Tiếng Việt", "English", "日本語", "한국어", "Français", "Español"])
    
    voice_selection = st.selectbox(
        "Giọng đọc AI (Edge-TTS):",
        options=[
            ("Nữ Miền Bắc - Hoài My (Khuyên dùng)", "vi-VN-HoaiMyNeural"),
            ("Nam Miền Nam - Minh Nhật", "vi-VN-NamMinhNeural"),
            ("Nữ Miền Nam - Nam Phương", "vi-VN-NamPhươngNeural") if "vi-VN-NamPhươngNeural" else ("Nữ Miền Nam - Linh Ân", "vi-VN-LinhAnNeural")
        ],
        format_func=lambda x: x[0]
    )[1]
    speech_speed = st.select_slider("Tốc độ đọc:", options=["-10%", "+0%", "+10%", "+15%", "+20%"], value="+0%")

    st.markdown("---")
    st.header("🎨 Tùy Chỉnh Giao Diện Phụ Đề")
    sub_color = st.selectbox("Màu sắc chữ phụ đề:", ["white", "yellow", "cyan", "green"])
    sub_fontsize = st.slider("Cỡ chữ phụ đề:", 16, 32, 22)
    enable_blur_box = st.checkbox("Che/Làm mờ vùng phụ đề cũ", value=True)

    st.markdown("---")
    st.header("🎵 Âm Thanh & Hình Ảnh Phụ")
    bgm_file = st.file_uploader("Tải nhạc nền (BGM - MP3/WAV)", type=["mp3", "wav"])
    watermark_file = st.file_uploader("Tải Logo / Watermark (PNG)", type=["png", "jpg"])
    orig_audio_vol = st.slider("Âm lượng gốc video gốc (%):", 0, 100, 15)
    bgm_vol = st.slider("Âm lượng nhạc nền (%):", 0, 100, 20)

uploaded_single_file = st.file_uploader("📥 Tải lên tệp video chính cần xử lý (MP4, MKV, AVI, MOV)", type=["mp4", "mkv", "avi", "mov"])

if uploaded_single_file is not None:
    st.video(uploaded_single_file)
    
    if st.button("🚀 BẮT ĐẦU PHÂN TÍCH & DỊCH THUẬT TỰ ĐỘNG", type="primary"):
        if not groq_api_key:
            st.error("❌ Vui lòng nhập Groq API Key ở thanh bên trái!")
        else:
            status_box = st.status("🔄 Đang xử lý quy trình thông minh...", expanded=True)
            
            with tempfile.TemporaryDirectory() as work_dir:
                orig_cwd = os.getcwd()
                os.chdir(work_dir)
                
                try:
                    in_video = "input.mp4"
                    audio_wav = "audio.wav"
                    output_video = "output_final.mp4"
                    generated_srt = "subs.srt"
                    generated_tts = "voiceover.mp3"
                    
                    with open(in_video, "wb") as f:
                        f.write(uploaded_single_file.read())
                        
                    status_box.write("1️⃣ **Trích xuất âm thanh chuẩn hóa bằng FFmpeg...**")
                    ffmpeg.input(in_video).output(audio_wav, acodec='pcm_s16le', ac=1, ar='16000').overwrite_output().run(capture_stdout=True, capture_stderr=True)
                    
                    status_box.write("2️⃣ **Nhận diện giọng nói (Whisper Large V3)...**")
                    client = Groq(api_key=groq_api_key)
                    with open(audio_wav, "rb") as af:
                        transcript = client.audio.transcriptions.create(
                            file=(audio_wav, af.read()),
                            model="whisper-large-v3",
                            response_format="verbose_json"
                        )
                    
                    raw_segments = getattr(transcript, 'segments', [])
                    segments_data = []
                    for s in raw_segments:
                        txt = s.get('text', '').strip() if isinstance(s, dict) else getattr(s, 'text', '').strip()
                        st_t = s.get('start', 0.0) if isinstance(s, dict) else getattr(s, 'start', 0.0)
                        en_t = s.get('end', 0.0) if isinstance(s, dict) else getattr(s, 'end', 0.0)
                        if txt:
                            segments_data.append({"start": st_t, "end": en_t, "text": txt})
                            
                    if not segments_data:
                        st.error("Không tìm thấy lời thoại nào trong video này.")
                        os.chdir(orig_cwd)
                        st.stop()
                        
                    status_box.write(f"3️⃣ **Dịch thuật thông minh sang {target_language} (Llama 3.3)...**")
                    payload = [{"id": i, "orig": seg["text"]} for i, seg in enumerate(segments_data)]
                    prompt = f"""Dịch danh sách phụ đề sau sang {target_language} thật trôi chảy, tự nhiên, phù hợp làm phụ đề video.
YÊU CẦU: Trả về ĐÚNG định dạng đối tượng JSON có khóa "data" chứa danh sách gồm "id" và "translated".
Dữ liệu: {json.dumps(payload, ensure_ascii=False)}"""

                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        response_format={"type": "json_object"}
                    )
                    trans_map = {item["id"]: item["translated"] for item in json.loads(response.choices[0].message.content).get("data", [])}
                    
                    for i, seg in enumerate(segments_data):
                        seg["translated"] = trans_map.get(i, seg["text"])
                        
                    status_box.update(label="✨ Đã hoàn tất bóc tách & dịch thuật!", state="complete")
                    
                    # Lưu trữ vào Session State để hiển thị bảng chỉnh sửa
                    st.session_state['segments_data'] = segments_data
                    st.session_state['ready_to_edit'] = True
                    os.chdir(orig_cwd)
                    st.rerun()

                except Exception as e:
                    os.chdir(orig_cwd)
                    status_box.update(label="❌ Lỗi xử lý!", state="error")
                    st.error(f"Chi tiết: {str(e)}")

# Khu vực hiển thị bảng tinh chỉnh phụ đề (Interactive Editor)
if st.session_state.get('ready_to_edit', False):
    st.markdown("---")
    st.subheader("✏️ Kiểm Tra & Tinh Chỉnh Phụ Đề (Interactive Editor)")
    st.info("Bạn có thể chỉnh sửa trực tiếp các câu dịch bên dưới trước khi bấm nút Render Video hoàn chỉnh.")
    
    df_subs = pd.DataFrame(st.session_state['segments_data'])
    edited_df = st.data_editor(
        df_subs[['start', 'end', 'translated']],
        column_config={
            "start": "Bắt đầu (s)",
            "end": "Kết thúc (s)",
            "translated": "Nội dung phụ đề dịch hoàn thiện"
        },
        use_container_width=True,
        num_rows="dynamic"
    )
    
    if st.button("🎬 XUẤT BẢN VIDEO HOÀN CHỈNH (RENDER)", type="primary"):
        render_status = st.status("🛠️ Đang tiến hành lồng tiếng và tổng hợp video...", expanded=True)
        
        with tempfile.TemporaryDirectory() as work_dir:
            orig_cwd = os.getcwd()
            os.chdir(work_dir)
            
            try:
                in_video = "input.mp4"
                output_video = "output_final.mp4"
                generated_srt = "subs.srt"
                generated_tts = "voiceover.mp3"
                
                with open(in_video, "wb") as f:
                    f.write(uploaded_single_file.read())
                    
                updated_segments = edited_df.to_dict('records')
                
                srt_lines = []
                full_tts_text = []
                for idx, row in enumerate(updated_segments):
                    st_t = float(row['start'])
                    en_t = float(row['end'])
                    txt = str(row['translated'])
                    full_tts_text.append(txt)
                    
                    ms1 = int((st_t - int(st_t)) * 1000)
                    h1, m1, s1 = int(st_t // 3600), int((st_t % 3600) // 60), int(st_t % 60)
                    t1 = f"{h1:02d}:{m1:02d}:{s1:02d},{ms1:03d}"
                    
                    ms2 = int((en_t - int(en_t)) * 1000)
                    h2, m2, s2 = int(en_t // 3600), int((en_t % 3600) // 60), int(en_t % 60)
                    t2 = f"{h2:02d}:{m2:02d}:{s2:02d},{ms2:03d}"
                    
                    srt_lines.append(f"{idx+1}\n{t1} --> {t2}\n{txt}\n\n")
                    
                with open(generated_srt, "w", encoding="utf-8") as f:
                    f.writelines(srt_lines)
                    
                render_status.write("🔊 Tổng hợp giọng đọc AI cao cấp...")
                async def create_tts():
                    comm = edge_tts.Communicate(" ".join(full_tts_text), voice_selection, rate=speech_speed)
                    await comm.save(generated_tts)
                asyncio.run(create_tts())
                
                render_status.write("🎨 Xử lý đồ họa, ghép phụ đề & nhạc nền qua FFmpeg...")
                v_stream = ffmpeg.input(in_video).video
                
                if enable_blur_box:
                    v_stream = ffmpeg.filter(v_stream, 'drawbox', x=0, y="ih*0.75", w="iw", h="ih*0.25", color="black", t="fill")
                
                # Định dạng phụ đề nâng cao qua bộ lọc phụ đề
                v_stream = ffmpeg.filter(v_stream, 'subtitles', generated_srt, force_style=f"FontSize={sub_fontsize},PrimaryColour=&H00{sub_color}&")
                
                # Xử lý Watermark nếu có
                if watermark_file is not None:
                    watermark_path = "watermark.png"
                    with open(watermark_path, "wb") as wf:
                        wf.write(watermark_file.read())
                    w_stream = ffmpeg.input(watermark_path).filter('scale', 120, -1)
                    v_stream = ffmpeg.overlay(v_stream, w_stream, x="W-w-30", y=30)
                
                # Trộn âm thanh (Original Audio + TTS Voice + BGM nếu có)
                audio_orig = ffmpeg.input(in_video).audio.filter('volume', orig_audio_vol / 100.0)
                audio_voice = ffmpeg.input(generated_tts)
                
                if bgm_file is not None:
                    bgm_path = "bgm.mp3"
                    with open(bgm_path, "wb") as bf:
                        bf.write(bgm_file.read())
                    audio_bgm = ffmpeg.input(bgm_path).filter('volume', bgm_vol / 100.0)
                    mixed_audio = ffmpeg.filter([audio_orig, audio_voice, audio_bgm], 'amix', inputs=3, duration='first')
                else:
                    mixed_audio = ffmpeg.filter([audio_orig, audio_voice], 'amix', inputs=2, duration='first')
                
                ffmpeg.output(v_stream, mixed_audio, output_video, vcodec='libx264', acodec='aac', preset='ultrafast').overwrite_output().run(capture_stdout=True, capture_stderr=True)
                
                with open(output_video, "rb") as f_out:
                    final_bytes = f_out.read()
                    
                os.chdir(orig_cwd)
                render_status.update(label="🎉 Xuất bản video thành công xuất sắc!", state="complete")
                st.success("Video của bạn đã sẵn sàng tải xuống!")
                st.video(final_bytes)
                st.download_button("📥 Tải Xuống Video Pro Ngay", data=final_bytes, file_name="vietsub_pro_output.mp4", mime="video/mp4")
                
            except Exception as err:
                os.chdir(orig_cwd)
                render_status.update(label="❌ Lỗi trong quá trình render!", state="error")
                st.error(f"Chi tiết lỗi: {str(err)}")
  
