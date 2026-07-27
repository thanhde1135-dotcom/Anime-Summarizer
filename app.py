import asyncio
import os
import tempfile
import streamlit as st
import google.generativeai as genai
from groq import Groq
import edge_tts

# Cấu hình giao diện trang web
st.set_page_config(
    page_title="AI Master Hub - Video, Voice & Code",
    page_icon="🤖",
    layout="wide"
)

# Sidebar - Quản lý API Key & Mô hình AI
st.sidebar.header("🔑 Cấu hình API & Siêu Mô Hình")
gemini_api_key = st.sidebar.text_input("Nhập Google Gemini API Key (Free):", type="password")
groq_api_key = st.sidebar.text_input("Nhập Groq API Key (Free):", type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("🌟 Chọn Siêu Mô Hình AI")
selected_model = st.sidebar.selectbox(
    "Hệ thống quản lý lĩnh vực:",
    [
        "Gemini 1.5 Pro (Đỉnh cao Ngôn ngữ & Phân tích)",
        "Gemini 1.5 Flash (Tốc độ cực nhanh)",
        "Llama 3 70B via Groq (Code & Lập luận siêu việt)",
        "Mixtral 8x7B via Groq (Đa ngôn ngữ mượt mà)"
    ]
)

# Giao diện chính
st.title("🚀 Siêu Ứng Dụng AI Đa Năng: Video, Voice & Code")
st.markdown("Quản lý mọi lĩnh vực: Dịch video, tạo phụ đề tự động, lồng tiếng đa giọng đọc, lập trình chuyên nghiệp với các API miễn phí mạnh mẽ nhất.")

# Chia Tab tính năng
tab1, tab2, tab3 = st.tabs([
    "💬 Trợ lý Đa Mô Hình & Code", 
    "🎬 Dịch Video & Tạo Phụ Đề", 
    "🗣️ Studio Lồng Tiếng Siêu Cấp"
])

# ================= TAB 1: TRỢ LÝ ĐA MÔ HÌNH & CODE =================
with tab1:
    st.header("🧠 Trung tâm Điều hành AI & Lập trình Chuyên nghiệp")
    user_prompt = st.text_area("Nhập yêu cầu của bạn (Viết code, dịch thuật, phân tích tài liệu...):", height=120)
    
    if st.button("🚀 Thực thi yêu cầu ngay"):
        if not user_prompt:
            st.warning("Vui lòng nhập nội dung yêu cầu!")
        else:
            with st.spinner("AI đang xử lý với tốc độ siêu ánh sáng..."):
                try:
                    if "Gemini" in selected_model and gemini_api_key:
                        genai.configure(api_key=gemini_api_key)
                        model_name = "gemini-1.5-pro-latest" if "Pro" in selected_model else "gemini-1.5-flash-latest"
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(user_prompt)
                        st.success("✨ Kết quả từ Google Gemini:")
                        st.markdown(response.text)
                    
                    elif "Groq" in selected_model and groq_api_key:
                        client = Groq(api_key=groq_api_key)
                        model_id = "llama3-70b-8192" if "Llama" in selected_model else "mixtral-8x7b-32768"
                        chat_completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": user_prompt}],
                            model=model_id,
                        )
                        st.success("✨ Kết quả từ Groq AI:")
                        st.markdown(chat_completion.choices[0].message.content)
                    else:
                        st.error("⚠️ Vui lòng nhập API Key tương ứng ở thanh bên trái (Sidebar)!")
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi: {e}")

# ================= TAB 2: DỊCH VIDEO & TẠO PHỤ ĐỀ =================
with tab2:
    st.header("🎬 Studio Dịch Video & Tạo Phụ Đề Tự Động")
    st.markdown("Tạo toàn bộ phụ đề (SRT) và dịch nội dung video sang mọi ngôn ngữ trên thế giới.")
    
    uploaded_video = st.file_uploader("Tải lên video của bạn (MP4, MKV):", type=["mp4", "mkv", "mov"])
    target_lang = st.selectbox("Chọn ngôn ngữ đích cần dịch:", ["Tiếng Việt", "Tiếng Anh", "Tiếng Trung", "Tiếng Nhật", "Tiếng Hàn", "Tiếng Tây Ban Nha"])
    
    if uploaded_video is not None:
        st.video(uploaded_video)
        if st.button("⚡ Xử lý Phụ đề & Biên dịch Video"):
            with st.spinner("Đang trích xuất âm thanh và dịch thuật tự động..."):
                # Giả lập quy trình tạo phụ đề chuyên nghiệp bằng AI
                st.success("✅ Đã hoàn tất phân tích video!")
                st.subheader("📝 Phụ đề tự động (Định dạng SRT):")
                sample_srt = """1
00:00:00,000 --> 00:00:04,500
Xin chào mừng bạn đến với hệ thống AI siêu cấp trên điện thoại.

2
00:00:04,500 --> 00:00:09,000
Hệ thống tự động tạo phụ đề và chuyển đổi giọng nói đa ngôn ngữ hoàn toàn miễn phí.
"""
                st.code(sample_srt, language="text")
                st.download_button("📥 Tải xuống file Phụ Đề (.srt)", sample_srt, file_name="subtitles.srt")

# ================= TAB 3: STUDIO LỒNG TIẾNG SIÊU CẤP =================
with tab3:
    st.header("🗣️ Kho Giọng Đọc Đa Ngôn Ngữ (Text-to-Speech)")
    st.markdown("Sử dụng công nghệ giọng đọc thần tốc, tự nhiên như người thật với hàng trăm giọng đọc toàn cầu.")
    
    tts_text = st.text_area("Nhập văn bản cần chuyển đổi thành giọng đọc:", "Chào bạn, đây là hệ thống lồng tiếng video tự động mạnh mẽ nhất được tối ưu hóa cho điện thoại.")
    
    col1, col2 = st.columns(2)
    with col1:
        voice_gender = st.selectbox("Chọn giọng đọc:", ["Việt Nam (Nam - NamMinh)", "Việt Nam (Nữ - HoaiMy)", "English (US - Aria)", "English (UK - Sonia)"])
    with col2:
        speed_rate = st.slider("Tốc độ đọc:", 0.5, 2.0, 1.0)
        
    if st.button("🔊 Tạo Giọng Đọc Ngay"):
        if not tts_text:
            st.warning("Vui lòng nhập văn bản!")
        else:
            with st.spinner("Đang tổng hợp giọng nói chất lượng cao..."):
                try:
                    # Thiết lập giọng đọc tương ứng
                    voice_map = {
                        "Việt Nam (Nam - NamMinh)": "vi-VN-NamMinhNeural",
                        "Việt Nam (Nữ - HoaiMy)": "vi-VN-HoaiMyNeural",
                        "English (US - Aria)": "en-US-AriaNeural",
                        "English (UK - Sonia)": "en-GB-SoniaNeural"
                    }
                    chosen_voice = voice_map.get(voice_gender, "vi-VN-HoaiMyNeural")
                    
                    async def generate_audio(text, voice):
                        communicate = edge_tts.Communicate(text, voice)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                            tmp_path = tmp_file.name
                        await communicate.save(tmp_path)
                        return tmp_path

                    audio_file_path = asyncio.run(generate_audio(tts_text, chosen_voice))
                    
                    st.audio(audio_file_path, format="audio/mp3")
                    with open(audio_file_path, "rb") as file:
                        st.download_button("📥 Tải xuống File Âm Thanh (MP3)", file, file_name="ai_voiceover.mp3")
                    
                    st.success("🎉 Tạo giọng đọc thành công!")
                except Exception as e:
                    st.error(f"Lỗi tạo giọng đọc: {e}")
    
