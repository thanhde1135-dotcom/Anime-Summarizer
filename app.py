import streamlit as st
from orchestrator import SystemOrchestrator

# Cấu hình giao diện trang web
st.set_page_config(
    page_title="AI Video Studio - 100+ Features",
    page_icon="🚀",
    layout="wide",
)

# Khởi tạo trung tâm điều phối hệ thống
@st.cache_resource
def get_system():
  return SystemOrchestrator()


app_system = get_system()

# Tiêu đề ứng dụng
st.title("🚀 Hệ Thống Dịch Video & Đa AI (100+ Tính Năng)")
st.markdown(
    "Nền tảng xử lý video, dịch thuật chuyên sâu Trung - Việt và quản lý tác"
    " vụ AI tự động."
)

# Sidebar quản lý tính năng
st.sidebar.header("🎛️ Bảng Điều Khiển Hệ Thống")
total_features = app_system.get_total_features_count()
st.sidebar.success(
    f"✅ Trạng thái: Đã kích hoạt **{total_features} tính năng** trong hệ thống."
)

feature_category = st.sidebar.selectbox(
    "Chọn nhóm tính năng hoạt động:",
    [
        "🔤 Nhóm Dịch Thuật & Ngôn Ngữ",
        "🎙️ Nhóm Âm Thanh & AI Voice",
        "🎬 Nhóm Xử Lý Video & Phụ Đề",
        "⚙️ Nhóm Hệ Thống Mở Rộng",
    ],
)

# Giao diện tương ứng theo nhóm tính năng
if feature_category == "🔤 Nhóm Dịch Thuật & Ngôn Ngữ":
  st.subheader("🔤 Dịch Thuật Chuyên Sâu (Trung - Việt)")
  zh_input = st.text_area(
      "Nhập văn bản tiếng Trung cần dịch:",
      "欢迎使用人工智能视频翻译系统，打造全球领先的短视频本地化工作流。",
  )
  if st.button("Thực hiện dịch thuật (TRANS_01)"):
    try:
      result = app_system.execute_feature("TRANS_01", zh_input)
      st.success("Kết quả dịch thành công:")
      st.code(result, language="text")
    except Exception as e:
      st.error(f"Lỗi thực thi: {e}")

elif feature_category == "⚙️ Nhóm Hệ Thống Mở Rộng":
  st.subheader("⚙️ Kiểm Thử Kho Lưu Trữ Tính Năng Mở Rộng")
  feature_code = st.text_input(
      "Nhập mã tính năng cần gọi (Ví dụ: SYS_FEATURE_85):", "SYS_FEATURE_85"
  )
  payload_input = st.text_input("Nhập dữ liệu đầu vào:", "Test Data Payload")
  if st.button("Chạy tính năng hệ thống"):
    try:
      result = app_system.execute_feature(feature_code, payload_input)
      st.success("Kết quả phản hồi từ hệ thống:")
      st.code(result, language="text")
    except Exception as e:
      st.error(f"Lỗi thực thi: {e}")

else:
  st.info(
      "Vui lòng chọn nhóm tính năng tương ứng ở menu bên trái để bắt đầu thao"
      " tác."
  )
  
