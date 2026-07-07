import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import os

# Cấu hình API (Thay dòng dưới bằng API Key bạn lấy từ Google AI Studio)
genai.configure(api_key="AQ.Ab8RN6J1v6Njve17VqM2A7JCLx9aVgOh2whNpiSxS4cYl_VqfQ")

st.title("Anime Summarizer (Free)")
ten_anime = st.text_input("Tên Anime:")

if st.button("Tóm tắt"):
    # 1. Tóm tắt bằng Gemini
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f"Tóm tắt nội dung anime {ten_anime} trong 100 chữ")
    tom_tat = response.text
    st.write(tom_tat)

    # 2. Chuyển thành giọng nói
    tts = gTTS(text=tom_tat, lang='vi')
    tts.save("audio.mp3")

    # 3. Phát trên web
    st.audio("audio.mp3", format='audio/mp3')
  
