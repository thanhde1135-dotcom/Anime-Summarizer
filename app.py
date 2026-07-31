import streamlit as st

st.set_page_config(
    page_title="AI Image Translator",
    page_icon="🌎",
    layout="wide"
)

st.title("🌎 AI Image Translator")

st.write("Upload ảnh")

uploaded = st.file_uploader(
    "Upload",
    type=["png","jpg","jpeg","webp"]
)

if uploaded:

    st.image(uploaded)

    if st.button("Dịch"):
        st.success("Đang xử lý...")
