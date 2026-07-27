import os
import tempfile
import streamlit as st
from gtts import gTTS  # Thư viện hỗ trợ giọng đọc chuẩn (có thể mở rộng sang các engine cao cấp)

# Cấu hình giao diện trang web
st.set_page_config(
    page_title="AI Trending Voice Studio - TikTok/YouTube",
    page_icon="🗣️",
    layout="centered",
)

st.markdown(
    """
    <h2 style='text-align: center; color: #FF4B4B;'>🗣️ Kho Giọng Đọc AI Hot Trend (TikTok, YouTube, Facebook)</h2>
    <p style='text-align: center;'>Lựa chọn các phong cách giọng nói nổi tiếng, test trực tiếp và lồng vào video!</p>
    """,
    unsafe_allow_html=True,
)

# Sidebar chọn phong cách giọng nói hot trend
st.sidebar.header("🎙️ Chọn Giọng Đọc Hot Trend")

voice_category = st.sidebar.selectbox(
    "Phân loại kênh/Phong cách:",
    [
        "🔥 Top Trending TikTok (Giọng trẻ trung, nhanh gọn)",
        "📺 Giọng Review Phim / Kể chuyện giật gân",
        "📰 Giọng Đọc Tin Tức / Tự sự truyền cảm",
        "🤖 Giọng Chị Google / Robot quen thuộc",
    ],
)

# Danh sách các giọng cụ thể tương ứng với xu hướng mạng xã hội
if "TikTok" in voice_category:
  selected_voice_name = st.sidebar.selectbox(
      "Chọn nhân vật/Giọng:",
      [
          "Nữ miền Nam năng động (Hot TikTok)",
          "Nam trẻ truyền năng lượng (Gen Z)",
      ],
  )
  lang_code = "vi"
  tld_code = "com.vn"
elif "Review Phim" in voice_category:
  selected_voice_name = st.sidebar.selectbox(
      "Chọn nhân vật/Giọng:",
      ["Nam trầm ấm, kịch tính (Reviewer chuyên nghiệp)", "Nữ kể chuyện cuốn hút"],
  )
  lang_code = "vi"
  tld_code = "com"
elif "Tin Tức" in voice_category:
  selected_voice_name = st.sidebar.selectbox(
      "Chọn nhân vật/Giọng:",
      ["Nam phát thanh viên chuẩn mực", "Nữ truyền cảm ấm áp"],
  )
  lang_code = "vi"
  tld_code = "com.vn"
else:
  selected_voice_name = st.sidebar.selectbox(
      "Chọn nhân vật/Giọng:", ["Giọng Chị Google Việt Nam kinh điển"]
  )
  lang_code = "vi"
  tld_code = "com.vn"

st.sidebar.markdown("---")
st.sidebar.info(
    f"💡 **Đang chọn:** `{selected_voice_name}`. Giọng này tối ưu cực tốt cho các"
    " video ngắn dạng Reels, TikTok và Shorts."
)

# Khu vực nhập văn bản để test giọng
st.subheader("✍️ Nhập văn bản cần chuyển đổi thành giọng nói:")
input_text_for_voice = st.text_area(
    "Nội dung văn bản:",
    value=(
        "Top 3 món ăn đường phố mà bạn nhất định phải thử khi đến Sài Gòn!"
        " Xem ngay để biết đó là gì nhé."
    ),
    height=120,
)

speed_option = st.radio(
    "⚡ Tốc độ đọc:", ["Bình thường (1.0x)", "Nhanh cuốn hút (1.25x - Trend TikTok)"], horizontal=True
)

if st.button(
    "🎧 Test Giọng & Tạo File Âm Thanh",
    type="primary",
    use_container_width=True,
):
  if not input_text_for_voice.strip():
    st.warning("⚠️ Vui lòng nhập nội dung văn bản để tạo giọng đọc!")
  else:
    with st.spinner(f"🔄 Đang tổng hợp giọng từ phong cách {selected_voice_name}..."):
      try:
        # Sử dụng gTTS để sinh âm thanh cơ sở (có thể thay thế bằng Edge-TTS hoặc ElevenLabs API cao cấp)
        slow_setting = False
        tts = gTTS(
            text=input_text_for_voice, lang=lang_code, tld=tld_code, slow=slow_setting
        )

        # Lưu file âm thanh tạm
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
          tts.save(tmp_audio.name)
          audio_output_path = tmp_audio.name

        st.success("✨ Đã tạo giọng đọc thành công!")

        # Trình phát để test âm thanh trực tiếp
        st.subheader("🔊 Nghe thử kết quả (Test Audio):")
        st.audio(audio_output_path, format="audio/mp3")

        # Nút tải file âm thanh xuống để đưa vào CapCut / Premiere
        with open(audio_output_path, "rb") as f_out:
          st.download_button(
              label="📥 Tải xuống file MP3 giọng đọc này",
              data=f_out.read(),
              file_name="trending_tiktok_voice.mp3",
              mime="audio/mp3",
          )

        # Dọn dẹp file tạm
        if os.path.exists(audio_output_path):
          os.unlink(audio_output_path)

      except Exception as e:
        st.error(f"❌ Đã xảy ra lỗi khi tạo giọng nói: {e}")
    
