import os
import tempfile
import time
import streamlit as st
from groq import Groq

st.set_page_config(page_title="Live Speech Streaming", page_icon="🎙️")

st.markdown("<h2>🎙️ AI Dịch Trực Tiếp & Streaming Thời Gian Thực</h2>", unsafe_allow_html=True)

groq_api_key = st.sidebar.text_input(
    "Nhập Groq API Key:", type="password", key="l_key"
)
target_lang = st.sidebar.selectbox(
    "Ngôn ngữ:", ["Tiếng Việt", "Tiếng Anh", "Tiếng Trung", "Tiếng Nhật"]
)

input_method = st.radio(
    "Phương thức:", ["Ghi âm trực tiếp", "Tải file âm thanh"], horizontal=True
)
audio_to_process = None

if input_method == "Ghi âm trực tiếp":
  audio_file_recorded = st.audio_input("Nói gì đó...")
  if audio_file_recorded:
    audio_to_process = audio_file_recorded
    st.audio(audio_file_recorded)
else:
  uploaded_live_file = st.file_uploader(
      "Tải file:", type=["mp3", "wav", "m4a"]
  )
  if uploaded_live_file:
    audio_to_process = uploaded_live_file
    st.audio(uploaded_live_file)

if audio_to_process and st.button("🚀 Bắt đầu Dịch Trực Tiếp", type="primary"):
  if not groq_api_key:
    st.error("⚠️ Nhập API Key!")
  else:
    ext = getattr(audio_to_process, "name", "audio.wav").split(".")[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
      tmp.write(audio_to_process.read())
      tmp_path = tmp.name

    with st.spinner("🔄 Đang xử lý..."):
      try:
        client = Groq(api_key=groq_api_key)
        with open(tmp_path, "rb") as f_audio:
          transcription = client.audio.transcriptions.create(
              file=(os.path.basename(tmp_path), f_audio.read()),
              model="whisper-large-v3",
              response_format="json",
          )
        os.unlink(tmp_path)
        original_text = getattr(transcription, "text", "")
        st.info(original_text)

        prompt = f"Translate into {target_lang}:\n\n{original_text}"
        stream = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            stream=True,
        )

        def generate_response():
          for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
              yield content
              time.sleep(0.01)

        st.write_stream(generate_response())
      except Exception as e:
        st.error(f"Lỗi: {e}")
        if os.path.exists(tmp_path):
          os.unlink(tmp_path)
          
