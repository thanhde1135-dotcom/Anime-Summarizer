import streamlit as st
from PIL import Image
from utils import process_image

st.set_page_config(page_title="Manga Translator Lite")

st.title("Manga Translator Lite")

uploaded = st.file_uploader(
    "Upload ảnh",
    type=["png","jpg","jpeg"]
)

if uploaded:

    image = Image.open(uploaded)

    st.image(image)

    if st.button("Dịch"):

        result = process_image(image)

        st.image(result)

        result.save("output.png")

        with open("output.png","rb") as f:

            st.download_button(
                "Download",
                f,
                "translated.png"
            )
