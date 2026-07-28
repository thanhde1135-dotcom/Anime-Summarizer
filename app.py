import streamlit as st
from PIL import Image
import io
import requests
import time

st.set_page_config(
    page_title="Free Smart AI Comic Colorizer",
    page_icon="🎨",
    layout="centered"
)

st.title("🎨 Free Smart AI Comic Colorizer")
st.markdown("Hệ thống AI tô màu truyện tranh tự động qua Hugging Face API.")

# Nhập Token miễn phí từ Hugging Face
st.sidebar.header("🔑 Cấu hình API Miễn Phí")
hf_token = st.sidebar.text_input("Nhập Hugging Face Token:", type="password", value="Hf_LdTAZnVqiMlyRzzePwamLRCqrrDlzUxYEC")
st.sidebar.markdown("""
*Cách lấy Token miễn phí:*
1. Đăng ký tài khoản trên [Hugging Face](https://huggingface.co/)
2. Vào **Settings** -> **Access Tokens** -> Tạo một **New Token** (chọn quyền Read).
""")

uploaded_file = st.file_uploader("Tải lên trang truyện tranh đen trắng của bạn", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📥 Ảnh gốc")
        st.image(image, use_container_width=True)
        
    with col2:
        st.subheader("✨ Kết quả AI Tô Màu")
        if st.button("🚀 Chạy AI Tô Màu Thông Minh"):
            if not hf_token:
                st.warning("⚠️ Vui lòng nhập Hugging Face Token!")
            else:
                with st.spinner("AI đang xử lý, vui lòng chờ trong giây lát..."):
                    try:
                        # Sử dụng mô hình Stable Diffusion v1-5 chuyên xử lý ảnh
                        API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
                        headers = {"Authorization": f"Bearer {hf_token.strip()}"}
                        
                        # Chuyển đổi ảnh sang bytes
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format='JPEG')
                        img_bytes = img_byte_arr.getvalue()
                        
                        payload = {
                            "inputs": "professional comic book colorization, vibrant colors, detailed shading, high quality manga art",
                            "image": img_bytes
                        }
                        
                        # Gửi request lên server Hugging Face
                        response = requests.post(API_URL, headers=headers, files={"image": img_bytes}, data={"inputs": "manga comic colorization, high quality, vibrant colors"})
                        
                        # Kiểm tra nếu mô hình đang khởi động (503) thì tự động chờ và thử lại
                        if response.status_code == 503:
                            st.info("⏳ Mô hình đang khởi động trên máy chủ, đang tự động đợi 15 giây...")
                            time.sleep(15)
                            response = requests.post(API_URL, headers=headers, files={"image": img_bytes}, data={"inputs": "manga comic colorization, high quality"})
                        
                        if response.status_code == 200:
                            colored_image = Image.open(io.BytesIO(response.content))
                            st.image(colored_image, use_container_width=True)
                            st.success("🎉 Hoàn tất tô màu thông minh bằng AI!")
                        else:
                            st.error(f"Lỗi từ máy chủ AI (Mã lỗi: {response.status_code})")
                            st.text(response.text)
                            
                    except Exception as e:
                        st.error(f"Đã xảy ra lỗi kết nối: {e}")
else:
    st.info("💡 Hãy tải lên một hình ảnh truyện tranh để bắt đầu.")
                            
