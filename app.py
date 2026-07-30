import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from groq import Groq
import io
import time
import os

st.set_page_config(page_title="Image Translator + Groq", page_icon="🌐", layout="wide")

st.title("🌐 Image Translator (OCR + Xóa chữ + Dịch Groq)")

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("🔑 Groq API")
    groq_api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    
    model = st.selectbox("Model Groq", [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "gemma2-9b-it"
    ])
    
    st.markdown("---")
    source_lang = st.selectbox("Ngôn ngữ nguồn", [
        "English", "Tiếng Việt", "Chinese", "Japanese", "Korean", "Thai", "Other"
    ])
    
    target_lang = st.selectbox("Ngôn ngữ đích", [
        "Vietnamese", "English", "Chinese", "Japanese", "Korean", "Thai", "French", "Spanish"
    ])
    
    padding = st.slider("Padding mask", 5, 30, 12)
    font_size = st.slider("Cỡ chữ", 16, 50, 28)

# ==================== CACHE OCR ====================
@st.cache_resource(show_spinner="Đang tải model OCR (lần đầu hơi lâu)...")
def get_reader():
    # Chỉ load English + Vietnamese để nhẹ hơn
    return easyocr.Reader(['en', 'vi'], gpu=False, verbose=False)

def create_mask(img, boxes, pad=12):
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    for box in boxes:
        pts = np.array(box, np.int32)
        x1 = max(0, int(np.min(pts[:,0]) - pad))
        y1 = max(0, int(np.min(pts[:,1]) - pad))
        x2 = min(img.shape[1], int(np.max(pts[:,0]) + pad))
        y2 = min(img.shape[0], int(np.max(pts[:,1]) + pad))
        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
    return mask

def translate_texts(texts, target, api_key, model_name):
    if not api_key:
        return [f"[Cần API Key] {t}" for t in texts]
    
    client = Groq(api_key=api_key)
    results = []
    
    for text in texts:
        if not text.strip():
            results.append("")
            continue
        try:
            prompt = f"Translate this text to {target}. Only return the translation, nothing else:\n\n{text}"
            res = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300
            )
            results.append(res.choices[0].message.content.strip())
        except Exception as e:
            results.append(f"[Lỗi] {str(e)[:40]}")
    return results

def draw_text(img, boxes, texts, size=28):
    pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except:
        font = ImageFont.load_default()
    
    for box, text in zip(boxes, texts):
        if not text or text.startswith("["):
            continue
        pts = np.array(box)
        x, y = int(np.min(pts[:,0])), int(np.min(pts[:,1]))
        bbox = draw.textbbox((x, y), text, font=font)
        draw.rectangle([bbox[0]-4, bbox[1]-2, bbox[2]+4, bbox[3]+2], fill=(255,255,255))
        draw.text((x, y), text, fill=(0,0,0), font=font)
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

# ==================== MAIN ====================
uploaded = st.file_uploader("Upload ảnh", type=["jpg", "jpeg", "png", "webp"])

if uploaded:
    file_bytes = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Ảnh gốc")
        st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), use_container_width=True)
    
    if st.button("🚀 Bắt đầu dịch", type="primary", use_container_width=True):
        with st.spinner("Đang xử lý..."):
            reader = get_reader()
            results = reader.readtext(image)
            
            if not results:
                st.warning("Không tìm thấy chữ")
                st.stop()
            
            boxes = [r[0] for r in results]
            texts = [r[1] for r in results]
            
            mask = create_mask(image, boxes, padding)
            cleaned = cv2.inpaint(image, mask, 7, cv2.INPAINT_TELEA)
            translated = translate_texts(texts, target_lang, groq_api_key, model)
            final = draw_text(cleaned, boxes, translated, font_size)
            
            with col2:
                st.subheader("Đã xóa chữ")
                st.image(cv2.cvtColor(cleaned, cv2.COLOR_BGR2RGB), use_container_width=True)
            
            with col3:
                st.subheader("Đã dịch")
                st.image(cv2.cvtColor(final, cv2.COLOR_BGR2RGB), use_container_width=True)
            
            st.dataframe({
                "#": list(range(1, len(texts)+1)),
                "Gốc": texts,
                "Dịch": translated
            }, use_container_width=True)
            
            buf = io.BytesIO()
            Image.fromarray(cv2.cvtColor(final, cv2.COLOR_BGR2RGB)).save(buf, "PNG")
            st.download_button("⬇️ Tải ảnh đã dịch", buf.getvalue(), "translated.png", "image/png")

else:
    st.info("Upload ảnh rồi nhấn nút xanh để bắt đầu")
