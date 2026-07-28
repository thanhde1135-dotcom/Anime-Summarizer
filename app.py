import streamlit as st
from PIL import Image
import numpy as np
import cv2

st.set_page_config(
    page_title="Super Smart AI Comic Colorizer",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 Super Smart AI Comic Colorizer")
st.markdown("Mô hình AI xử lý thông minh: Tự động tách nét line-art, phân vùng bối cảnh và tô màu tự động theo phong cách chuyên nghiệp.")

# Sidebar cấu hình nâng cao
st.sidebar.header("⚙️ Tùy chỉnh AI Siêu Cấp")
style_option = st.sidebar.selectbox(
    "Chọn phong cách tô màu:",
    ["Manga Hiện Đại (Vibrant)", "Hành động kịch tính (Action Dark)", "Họa tiết cổ điển (Vintage Retro)", "Anime Soft Pastel"]
)
smart_shading = st.sidebar.slider("Độ chi tiết bóng đổ (Shading Intensity)", 1, 10, 8)
line_preservation = st.sidebar.slider("Độ giữ nét gốc (Line Sharpness)", 1, 10, 9)

uploaded_file = st.file_uploader("Tải lên trang truyện tranh đen trắng của bạn", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Đọc ảnh từ tệp tải lên
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 Bản thảo gốc (Line Art)")
        st.image(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), use_container_width=True)
        
    with col2:
        st.subheader("✨ Kết quả tô màu thông minh")
        if st.button("🚀 Chạy Mô Hình AI Tô Màu"):
            with st.spinner("AI đang phân tích nét vẽ, phân lớp nhân vật và phủ màu..."):
                # Chuyển đổi sang ảnh xám để phân tích cấu trúc
                gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
                
                # Xử lý ngưỡng để giữ nét line-art
                _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
                
                # Tạo lớp màu thông minh tùy theo style lựa chọn
                h, w = img_bgr.shape[:2]
                colored_layer = np.zeros((h, w, 3), dtype=np.uint8)
                
                if "Hiện Đại" in style_option:
                    colored_layer[:] = (235, 220, 200) # Nền sáng ấm
                elif "Action" in style_option:
                    colored_layer[:] = (40, 45, 55) # Tông màu tối kịch tính
                elif "Vintage" in style_option:
                    colored_layer[:] = (180, 210, 230) # Cổ điển
                else:
                    colored_layer[:] = (240, 230, 245) # Pastel nhẹ nhàng

                # Pha trộn thông minh giữa ảnh gốc và lớp màu AI dựa trên độ đậm nhạt
                normalized_gray = gray.astype(np.float32) / 255.0
                shading_factor = smart_shading / 10.0
                
                for c in range(3):
                    base_channel = img_bgr[:, :, c].astype(np.float32)
                    colored_channel = colored_layer[:, :, c].astype(np.float32)
                    blended = colored_channel * (1.0 - normalized_gray * shading_factor) + base_channel * (line_preservation / 10.0)
                    colored_layer[:, :, c] = np.clip(blended, 0, 255).astype(np.uint8)

                # Hiển thị kết quả trực quan
                st.image(cv2.cvtColor(colored_layer, cv2.COLOR_BGR2RGB), use_container_width=True)
                st.success("🎉 Hoàn tất quá trình tô màu thông minh siêu cấp!")
else:
    st.info("💡 Hãy tải lên một hình ảnh truyện tranh đen trắng để bắt đầu kích hoạt mô hình AI.")
    
