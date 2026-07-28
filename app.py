import streamlit as st
from PIL import Image
import os

st.set_page_config(
    page_title="Anime Colorizer AI",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 Anime Colorizer AI")

uploaded = st.file_uploader(
    "Chọn ảnh cần tô màu",
    type=["png","jpg","jpeg"]
)

style = st.selectbox(
    "Phong cách",
    [
        "Soft Anime",
        "High Detail",
        "Illustration",
        "Cinematic",
        "Ultra Quality"
    ]
)

strength = st.slider(
    "Độ mạnh AI",
    0.0,
    1.0,
    0.8
)

if uploaded:

    image = Image.open(uploaded)

    col1,col2 = st.columns(2)

    with col1:
        st.subheader("Ảnh gốc")
        st.image(image,use_container_width=True)

    with col2:

        st.subheader("Kết quả")

        if st.button("Bắt đầu tô màu"):

            with st.spinner("AI đang xử lý..."):

                # Tạm thời chỉ hiển thị ảnh
                result=image

            st.image(result,use_container_width=True)

            st.success("Hoàn thành!")
