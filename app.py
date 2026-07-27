import asyncio
import os
import tempfile
from deep_translator import GoogleTranslator
import edge_tts
import streamlit as st

# Cấu hình giao diện trang web
st.set_page_config(
    page_title="AI Video & Text Studio (ZH-VI)", page_icon="🚀", layout="wide"
)

# Khởi tạo bộ nhớ tạm để lưu log trạng thái AI ở dưới cùng
if "logs" not in st.session_state:
  st.session_state["logs"] = []


def add_log(message: str):
  """Thêm thông tin trạng thái hoạt động của AI vào danh sách log"""
  st.session_state["logs"].append(message)
  if len(st.session_state["logs"]) > 10:
    st.session_state["logs"].pop(0)


# Tiêu đề ứng dụng
st.title("🚀 Siêu Ứng Dụng AI: Dịch Trung - Việt & Đọc Giọng AI")
st.markdown(
    "Hệ thống tối ưu hóa chạy trên **Streamlit Cloud** — Không cần API Key,"
    " chuyên sâu dịch thuật Trung - Việt và tổng hợp giọng đọc phong cách"
    " TikTok/YouTube."
)

# Menu chọn tính năng ở Sidebar
st.sidebar.header("🎛️ Bảng Điều Khiển AI")
app_mode = st.sidebar.selectbox(
    "Chọn tính năng hoạt động:",
    [
        "🔤 Dịch Thuật Trung - Việt Tốc Độ Cao",
        "🎙️ Tạo Giọng Đọc AI (TikTok/YouTube Style)",
        "🎬 Trợ Lý Phụ Đề Video (SRT Generator)",
    ],
)

# --- TÍNH NĂNG 1: DỊCH THUẬT TRUNG - VIỆT ---
if app_mode == "🔤 Dịch Thuật Trung - Việt Tốc Độ Cao":
  st.header("🔤 Mô Hình Dịch Thuật Chuyên Sâu Trung -> Việt")
  zh_text = st.text_area(
      "Nhập văn bản hoặc kịch bản tiếng Trung cần dịch:",
      "欢迎使用人工智能视频翻译与配音系统。我们将为您提供最高质量的中文到越南文转换服务。",
      height=150,
  )

  if st.button("🚀 Thực Hiện Dịch Thuật"):
    if not zh_text.strip():
      st.warning("Vui lòng nhập nội dung tiếng Trung cần dịch!")
    else:
      add_log(
          "⚙️ [AI Core]: Khởi động mô hình dịch thuật chuyên sâu Trung - Việt."
      )
      with st.spinner("AI đang phân tích ngữ cảnh và dịch..."):
        try:
          add_log(
              "🔄 [Translation Engine]: Đang xử lý bóc tách cú pháp và dịch"
              " sang Tiếng Việt..."
          )
          translated_text = GoogleTranslator(
              source="zh-CN", target="vi"
          ).translate(zh_text)
          add_log(
              "✅ [Translation Engine]: Dịch thành công hoàn toàn văn bản."
          )

          st.success("Kết quả dịch thuật:")
          st.text_area("Bản dịch tiếng Việt chuẩn:", translated_text, height=150)
        except Exception as e:
          add_log(f"❌ [Error]: Lỗi dịch thuật: {str(e)}")
          st.error(f"Đã xảy ra lỗi: {e}")

# --- TÍNH NĂNG 2: TẠO GIỌNG ĐỌC AI ---
elif app_mode == "🎙️ Tạo Giọng Đọc AI (TikTok/YouTube Style)":
  st.header("🎙️ Trình Tạo Giọng Nói AI Đa Giọng Đọc")

  tts_text = st.text_area(
      "Nhập văn bản cần chuyển thành giọng đọc:",
      "Xin chào các bạn, đây là hệ thống tạo giọng đọc AI siêu thực phỏng theo"
      " các kênh TikTok và YouTube triệu view.",
      height=120,
  )

  voice_selection = st.selectbox(
      "Chọn giọng đọc AI nổi tiếng:",
      {
          "Tiếng Việt - Nữ miền Bắc (HoangMai)": "vi-VN-HoangMaiNeural",
          "Tiếng Việt - Nam miền Nam (NamMinh)": "vi-VN-NamMinhNeural",
          "Tiếng Trung - Nam trầm ấm, phổ biến TikTok (Yunxi)": (
              "zh-CN-YunxiNeural"
          ),
          "Tiếng Trung - Nữ phát thanh viên (Xiaoxiao)": (
              "zh-CN-XiaoxiaoNeural"
          ),
          "Tiếng Anh - Trợ lý thông minh (Aria)": "en-US-AriaNeural",
      },
  )

  voice_dict = {
      "Tiếng Việt - Nữ miền Bắc (HoangMai)": "vi-VN-HoangMaiNeural",
      "Tiếng Việt - Nam miền Nam (NamMinh)": "vi-VN-NamMinhNeural",
      "Tiếng Trung - Nam trầm ấm, phổ biến TikTok (Yunxi)": (
          "zh-CN-YunxiNeural"
      ),
      "Tiếng Trung - Nữ phát thanh viên (Xiaoxiao)": "zh-CN-XiaoxiaoNeural",
      "Tiếng Anh - Trợ lý thông minh (Aria)": "en-US-AriaNeural",
  }
  selected_voice = voice_dict[voice_selection]

  if st.button("🔊 Tổng Hợp Âm Thanh AI"):
    if not tts_text.strip():
      st.warning("Vui lòng nhập văn bản!")
    else:
      add_log(
          f"⚙️ [TTS Engine]: Kích hoạt mô hình âm thanh với giọng:"
          f" {selected_voice}"
      )
      with st.spinner("AI đang tổng hợp giọng đọc..."):
        try:
          temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
          temp_path = temp_file.name
          temp_file.close()

          async def generate_speech():
            communicate = edge_tts.Communicate(tts_text, selected_voice)
            await communicate.save(temp_path)

          add_log(
              "🔄 [Audio Synthesizer]: Đang kết nối mô hình phát âm để tạo"
              " file MP3..."
          )
          asyncio.run(generate_speech())
          add_log("✅ [Audio Synthesizer]: Tạo file âm thanh thành công.")

          st.audio(temp_path, format="audio/mp3")
          with open(temp_path, "rb") as f:
            st.download_button(
                "📥 Tải xuống file MP3",
                f,
                file_name="ai_voice_output.mp3",
                mime="audio/mpeg",
            )
        except Exception as e:
          add_log(f"❌ [Error]: Lỗi tạo giọng đọc: {str(e)}")
          st.error(f"Lỗi: {e}")

# --- TÍNH NĂNG 3: TRỢ LÝ PHỤ ĐỀ VIDEO ---
elif app_mode == "🎬 Trợ Lý Phụ Đề Video (SRT Generator)":
  st.header("🎬 Trình Dịch và Tạo Phụ Đề SRT Tự Động")
  st.info(
      "Dán kịch bản video tiếng Trung của bạn vào đây, AI sẽ tự động dịch và"
      " định dạng thành file phụ đề chuẩn (.srt) để bạn chèn trực tiếp vào video."
  )

  script_input = st.text_area(
      "Nhập nội dung kịch bản video (mỗi dòng là một câu phụ đề):",
      "大家好，今天我们来测试人工智能视频自动翻译功能。\n希望大家喜欢并关注我们的频道。",
      height=150,
  )

  if st.button("📝 Tạo Phụ Đề SRT Tiếng Việt"):
    if not script_input.strip():
      st.warning("Vui lòng nhập kịch bản video!")
    else:
      add_log("⚙️ [Subtitles Engine]: Bắt đầu phân đoạn và dịch phụ đề video...")
      try:
        lines = script_input.split("\n")
        srt_output = ""
        for idx, line in enumerate(lines, 1):
          if not line.strip():
            continue
          translated_line = GoogleTranslator(
              source="zh-CN", target="vi"
          ).translate(line)
          start_t = f"00:00:{idx*3-3:02},000"
          end_t = f"00:00:{idx*3:02},000"
          srt_output += (
              f"{idx}\n{start_t} --> {end_t}\n{translated_line}\n\n"
          )

        add_log(
            "✅ [Subtitles Engine]: Hoàn tất tạo mã nguồn phụ đề SRT tiếng"
            " Việt."
        )
        st.success("Tạo phụ đề thành công!")
        st.text_area("Mã nguồn Phụ đề SRT:", srt_output, height=200)
        st.download_button(
            "📥 Tải xuống file phụ đề (.srt)",
            srt_output,
            file_name="video_subtitles_vi.srt",
            mime="text/plain",
        )
      except Exception as e:
        add_log(f"❌ [Error]: Lỗi tạo phụ đề: {str(e)}")
        st.error(f"Lỗi: {e}")

# --- BẢNG THÔNG TIN TRẠNG THÁI (LIVE STATUS PANEL) Ở DƯỚI CÙNG ---
st.markdown("---")
st.markdown("### 📊 Bảng Thông Tin Trạng Thái AI (Live Activity Panel)")
log_box = st.container()
with log_box:
  if st.session_state["logs"]:
    for log_msg in reversed(st.session_state["logs"][-4:]):
      st.info(log_msg)
  else:
    st.write(
        "⏳ Hệ thống AI đang ở trạng thái chờ lệnh. Thực hiện thao tác ở trên"
        " để theo dõi hoạt động."
      )
  
