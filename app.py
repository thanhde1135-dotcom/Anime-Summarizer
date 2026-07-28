import streamlit as st
from PIL import Image
import io
from huggingface_hub import InferenceClient

st.set_page_config(
    page_title="Free Smart AI Comic Colorizer",
    page_icon="🎨",
    layout="centered"
)

st.title("🎨 Free Smart AI Comic Colorizer")
st.markdown("Sử dụng mô hình AI thông minh qua Hugging Face API hoàn toàn miễn phí!")

# Nhập Token miễn phí từ Hugging Face
st.sidebar.header("🔑 Cấu hình API Miễn Phí")
hf_token = st.sidebar.text_input("Nhập Hugging Face Token:", type="password")
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
                st.warning("⚠️ Vui lòng nhập Hugging Face Token ở thanh bên trái để sử dụng!")
            else:
                with st.spinner("AI đang xử lý và tô màu tự động..."):
                    try:
                        # Khởi tạo client miễn phí
                        client = InferenceClient(token=hf_token)
                        
                        # Chuyển đổi ảnh sang dạng bytes
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format='PNG')
                        img_bytes = img_byte_arr.getvalue()
                        
                        # Gọi mô hình AI chuyên dụng xử lý ảnh (Image-to-Image / Colorization)
                        # Sử dụng mô hình xử lý hình ảnh mã nguồn mở miễn phí trên Hugging Face
                        image_result_bytes = client.image_to_image(
                            image=img_bytes,
                            prompt="professional comic book colorization, vibrant colors, detailed shading, high quality",
                            model="runwayml/stable-diffusion-v1-5" 
                        )
                        
                        colored_image = Image.open(io.BytesIO(image_result_bytes))
                        st.image(colored_image, use_container_width=True)
                        st.success("🎉 Hoàn tất tô màu thông minh bằng AI!")
                        
                    except Exception as e:
                        st.error(f"Đã xảy ra lỗi: {e}")
                        st.info("💡 Mẹo: Hãy đảm bảo Token của bạn chính xác và mô hình đang hoạt động.")
else:
    st.info("💡 Hãy tải lên một hình ảnh truyện tranh để bắt đầu.")
    
