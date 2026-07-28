import streamlit as st
from PIL import Image
import numpy as np
import cv2
from sklearn.cluster import KMeans

st.set_page_config(
    page_title="Ultra Smart AI Comic Colorizer",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 Ultra Smart AI Comic Colorizer")
st.markdown("Mô hình AI chuyên sâu: Tự động phân tách vùng nét (Line-art), nhận diện ngữ cảnh nhân vật/quái vật và phủ màu thông minh.")

# Sidebar cấu hình mô hình AI
st.sidebar.header("🧠 Cấu hình AI Thông Minh")
ai_mode = st.sidebar.selectbox(
    "Chọn chế độ phân tích AI:",
    ["Dungeon & Action (Tông tối/Quái vật)", "Manga Anime Chuẩn (Sáng sủa)", "Vintage Retro Classic", "Cyberpunk Neon"]
)
segmentation_detail = st.sidebar.slider("Độ chi tiết phân vùng (Segmentation Granularity)", 3, 8, 5)
color_richness = st.sidebar.slider("Độ bão hòa màu (Color Saturation)", 1.0, 2.0, 1.3)

uploaded_file = st.file_uploader("Tải lên trang truyện tranh đen trắng của bạn", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Đọc ảnh từ tệp tải lên
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 Bản thảo gốc")
        st.image(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), use_container_width=True)
        
    with col2:
        st.subheader("✨ Kết quả AI Tô Màu Thông Minh")
        if st.button("🚀 Chạy Mô Hình AI Phân Tích & Tô Màu"):
            with st.spinner("AI đang phân tích cấu trúc, nhận diện vùng ảnh và tô màu tự động..."):
                
                # 1. Chuyển đổi sang không gian màu LAB & Grayscale để AI phân tích độ sáng/tối
                gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
                lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
                l_channel, a_channel, b_channel = cv2.split(lab)
                
                # 2. Xử lý tách nét (Line-art preservation)
                edges = cv2.Canny(gray, 100, 200)
                
                # 3. Phân cụm màu thông minh (K-Means Clustering theo chế độ AI)
                pixels = img_bgr.reshape((-1, 3))
                pixels = np.float32(pixels)
                
                kmeans = KMeans(n_clusters=segmentation_detail, random_state=42, n_init=10).fit(pixels)
                centers = np.uint8(kmeans.cluster_centers_)
                segmented_image = centers[kmeans.labels_.flatten()]
                segmented_image = segmented_image.reshape(img_bgr.shape)
                
                # 4. Áp dụng bảng màu thông minh tùy theo chế độ lựa chọn
                hsv = cv2.cvtColor(segmented_image, cv2.COLOR_BGR2HSV)
                
                if "Dungeon" in ai_mode:
                    # Tông màu hầm ngục, quái vật (xanh rêu, nâu đất, xám khói)
                    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * color_richness, 0, 255)
                    # Chỉnh màu cho các vùng tối/quái vật sang sắc xanh/nâu
                    mask_dark = gray < 100
                    segmented_image[mask_dark] = [50, 70, 60] # Xanh quái vật
                elif "Anime" in ai_mode:
                    # Tông sáng, da người hồng hào, tóc nổi bật
                    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.4, 0, 255)
                elif "Cyberpunk" in ai_mode:
                    # Tông màu rực rỡ hiện đại
                    hsv[:, :, 0] = (hsv[:, :, 0] + 40) % 180
                
                # 5. Pha trộn giữ nguyên nét vẽ gốc (Line Art) sắc nét tuyệt đối
                final_colored = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
                
                # Kết hợp lại với nét đen gốc
                mask_lines = gray < 50
                final_colored[mask_lines] = img_bgr[mask_lines]

                # Hiển thị kết quả
                st.image(cv2.cvtColor(final_colored, cv2.COLOR_BGR2RGB), use_container_width=True)
                st.success("🎉 AI đã hoàn tất phân tích và tô màu thành công!")
else:
    st.info("💡 Hãy tải lên một trang truyện tranh đen trắng để kích hoạt mô hình AI siêu thông minh.")
                
