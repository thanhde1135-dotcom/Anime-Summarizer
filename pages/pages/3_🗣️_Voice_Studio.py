import os
import tempfile
import streamlit as st
from gtts import gTTS

st.set_page_config(page_title="AI Trending Voice Studio", page_icon="🗣️")

st.markdown("<h2>🗣️ Kho Giọng Đọc AI Hot Trend</h2>", unsafe_allow_html=True)

voice_category = st.sidebar.selectbox(
    "Phân loại:", ["Top Trending TikTok", "Review Phim", "Tin Tức"]
)
text_input = st.text_area(
    "Nhập văn bản:", value="Chào bạn, chúc bạn một ngày tốt lành!"
)

if st.button("🎧 Tạo Giọng Đọc", type="primary"):
  if not text_input.strip():
    st.warning("Nhập văn bản!")
  else:
    with st.spinner("🔄 Đang tổng hợp..."):
      try:
        tts = gTTS(text=text_input, lang="vi", tld="com.vn")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
          tts.save(tmp.name)
          out_path = tmp.name
        st.success("Xong!")
        st.audio(out_path)
        with open(out_path, "rb") as f:
          st.download_button(
              "📥 Tải MP3", f.read(), file_name="voice.mp3", mime="audio/mp3"
          )
        if os.path.exists(out_path):
          os.unlink(out_path)
      except Exception as e:
        st.error(f"Lỗi: {e}")
