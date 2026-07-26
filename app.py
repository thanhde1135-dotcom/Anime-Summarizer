import streamlit as st
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(
    page_title="AI 18+ Generator",
    page_icon="🔥",
    layout="centered"
)

st.title("🔥 AI 18+ Image Generator")
st.caption("Nhập mô tả → AI tạo ảnh (hỗ trợ nội dung 18+)")

# Prompt
prompt = st.text_area(
    "Mô tả ảnh bạn muốn (càng chi tiết càng tốt)",
    placeholder="Ví dụ: beautiful anime girl, nude, detailed face, bedroom, soft lighting, highly detailed...",
    height=120
)

# Tùy chọn
col1, col2 = st.columns(2)
with col1:
    width = st.selectbox("Chiều rộng", [512, 768, 1024], index=1)
with col2:
    height = st.selectbox("Chiều cao", [512, 768, 1024], index=1)

negative_prompt = st.text_input(
    "Negative prompt (những gì không muốn)",
    value="low quality, blurry, deformed, bad anatomy, text, watermark"
)

if st.button("Tạo ảnh 🔥", type="primary", use_container_width=True):
    if not prompt.strip():
        st.warning("Hãy nhập mô tả trước!")
    else:
        with st.spinner("Đang tạo ảnh..."):
            try:
                # Dùng Pollinations.ai (miễn phí, khá thoáng với 18+)
                url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}"
                params = {
                    "width": width,
                    "height": height,
                    "nologo": "true",
                    "enhance": "true"
                }
                
                response = requests.get(url, params=params, timeout=60)
                
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    st.image(img, caption="Kết quả", use_container_width=True)
                    
                    # Nút tải về
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button(
                        "Tải ảnh về",
                        data=buf.getvalue(),
                        file_name="ai_18plus.png",
                        mime="image/png"
                    )
                else:
                    st.error(f"Lỗi: {response.status_code}")
            except Exception as e:
                st.error(f"Có lỗi xảy ra: {str(e)}")

st.markdown("---")
st.markdown("**Lưu ý:** App này chạy trên cloud, nội dung 18+ có thể bị giới hạn tùy thời điểm.")
