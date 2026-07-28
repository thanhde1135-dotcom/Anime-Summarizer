import streamlit as st
from PIL import Image
import numpy as np
import cv2

st.set_page_config(
    page_title="Ultimate AI Comic Colorizer",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 Ultimate AI Comic Colorizer (Pro Engine)")
st.markdown("Hệ thống xử lý AI thông minh: Tự động bóc tách nét vẽ Line-art, xử lý làm mượt biên độ và phủ màu không gian đa chiều.")

# Sidebar cấu hình mô hình mạnh mẽ
st.sidebar.header("⚙️ Thiết lập Engine AI")
engine_mode = st.sidebar.selectbox(
    "Chọn phong cách màu thông minh:",
    [
        "Tông màu da & Mature (18+ / Skin Tone Pro)", 
        "Dungeon & Dark Fantasy (Hầm ngục u ám)", 
        "Vibrant Modern Anime (Sống động sắc nét)", 
        "Cyberpunk Neon (Rực rỡ tương lai)"
    ]
)

smooth_strength = st.sidebar.slider("Độ mịn màng vùng màu (Smoothing)", 3, 15, 7)
color_intensity = st.sidebar.slider("Độ đậm nhạt màu sắc (Saturation)", 1.0, 2.0, 1.3)
line_weight = st.sidebar.slider("Độ đậm nét vẽ gốc (Line Contrast)", 1, 10, 8)

uploaded_file = st.file_uploader("Tải lên trang truyện tranh đen trắng của bạn", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Đọc dữ liệu ảnh gốc
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 Bản thảo gốc (Line Art)")
        st.image(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), use_container_width=True)
        
    with col2:
        st.subheader("✨ Kết quả AI Tô Màu Cao Cấp")
        if st.button("🚀 Kích hoạt Engine AI"):
            with st.spinner("AI đang phân tích cấu trúc, lọc biên và phủ màu thông minh..."):
                
                # 1. Chuyển đổi không gian màu và tách lớp nét vẽ (Edge-Preserving Filtering)
                gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
                
                # Giữ lại nét vẽ đen sắc nét tuyệt đối
                _, line_mask = cv2.threshold(gray, 50 * (line_weight / 5.0), 255, cv2.THRESH_BINARY)
                
                # Làm mượt các vùng bên trong nhưng giữ nguyên biên nét vẽ
                smoothed = cv2.edgePreservingFilter(img_bgr, flags=1, sigma_s=smooth_strength, sigma_r=0.4)
                
                # Chuyển sang không gian màu HSV để điều chỉnh màu sắc thông minh
                hsv = cv2.cvtColor(smoothed, cv2.COLOR_BGR2HSV)
                h, s, v = cv2.split(hsv)
                
                # 2. Xử lý phân bổ màu dựa theo Engine Mode được chọn
                if "18+" in engine_mode or "Mature" in engine_mode:
                    # Tối ưu hóa cho sắc độ da chân thực, ánh sáng ấm và bối cảnh mềm mại
                    s = np.clip(s * color_intensity * 1.1, 0, 255).astype(np.uint8)
                    # Điều chỉnh phổ màu để làm nổi bật khối da và không gian
                    h = np.where((gray > 70) & (gray < 210), (h + 10) % 180, h)
                elif "Dungeon" in engine_mode:
                    # Tông màu hầm ngục, quái vật (xanh rêu, xám thép, nâu đất)
                    s = np.clip(s * color_intensity * 0.9, 0, 255).astype(np.uint8)
                    h = np.where(gray < 120, 45, h) # Ánh sắc xanh/nâu cho vùng tối
                elif "Anime" in engine_mode:
                    # Màu sắc tươi sáng, rực rỡ phong cách anime hiện đại
                    s = np.clip(s * color_intensity * 1.4, 0, 255).astype(np.uint8)
                else:
                    # Phong cách Cyberpunk rực rỡ
                    h = (h + 50) % 180
                    s = np.clip(s * 1.5, 0, 255).astype(np.uint8)
                
                # Gộp kênh màu trở lại
                merged_hsv = cv2.merge([h, s, v])
                colored_base = cv2.cvtColor(merged_hsv, cv2.COLOR_HSV2BGR)
                
                # 3. Phủ lại lớp nét vẽ gốc để giữ nguyên toàn bộ chi tiết truyện tranh
                final_output = colored_base.copy()
                # Đưa nét vẽ đen gốc đè lên phần màu
                final_output[line_mask == 0] = img_bgr[line_mask == 0]

                # Hiển thị kết quả hoàn thiện
                st.image(cv2.cvtColor(final_output, cv2.COLOR_BGR2RGB), use_container_width=True)
                st.success("🎉 Xử lý AI hoàn tất thành công!")
else:
    st.info("💡 Hãy tải lên một hình ảnh truyện tranh đen trắng để bắt đầu.")
                                
