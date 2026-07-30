import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from groq import Groq
import io

st.set_page_config(page_title="Image Translator", page_icon="🌐", layout="wide")
st.title("🌐 Image Translator + Groq")

with st.sidebar:
    st.header("🔑 Groq API Key")
    api_key = st.text_input("API Key", type="password")
    model = st.selectbox("Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    target_lang = st.selectbox("Ngôn ngữ đích", ["Vietnamese", "English", "Chinese", "Japanese", "Korean", "Thai"])
    padding = st.slider("Padding", 5, 25, 12)
    font_size = st.slider("Cỡ chữ", 16, 40, 26)

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en', 'vi'], gpu=False)

def create_mask(img, boxes, pad=12):
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    for box in boxes:
        pts = np.array(box, np.int32)
        x1 = max(0, int(np.min(pts[:, 0]) - pad))
        y1 = max(0, int(np.min(pts[:, 1]) - pad))
        x2 = min(img.shape[1], int(np.max(pts[:, 0]) + pad))
        y2 = min(img.shape[0], int(np.max(pts[:, 1]) + pad))
        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
    return mask

def translate(texts, target, key, model):
    if not key:
        return [f"[Cần API Key] {t}" for t in texts]
    client = Groq(api_key=key)
    results = []
    for t in texts:
        try:
            res = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": f"Translate to {target}. Only return translation:\n{t}"}],
                temperature=0.1,
                max_tokens=256
            )
            results.append(res.choices[0].message.content.strip())
        except:
            results.append("[Lỗi dịch]")
    return results

def draw_text(img, boxes, texts, size=26):
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
        x, y = int(np.min(pts[:, 0])), int(np.min(pts[:, 1]))
        bbox = draw.textbbox((x, y), text, font=font)
        draw.rectangle([bbox[0]-3, bbox[1]-2, bbox[2]+3, bbox[3]+2], fill=(255,255,255))
        draw.text((x, y), text, fill=(0,0,0), font=font)
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

uploaded = st.file_uploader("Upload ảnh", type=["jpg", "jpeg", "png", "webp"])

if uploaded:
    img = cv2.imdecode(np.asarray(bytearray(uploaded.read()), dtype=np.uint8), 1)
    st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), use_container_width=True, caption="Ảnh gốc")

    if st.button("🚀 Dịch ảnh", type="primary"):
        with st.spinner("Đang xử lý..."):
            reader = load_ocr()
            results = reader.readtext(img)
            if not results:
                st.warning("Không tìm thấy chữ")
            else:
                boxes = [r[0] for r in results]
                texts = [r[1] for r in results]
                mask = create_mask(img, boxes, padding)
                cleaned = cv2.inpaint(img, mask, 7, cv2.INPAINT_TELEA)
                translated = translate(texts, target_lang, api_key, model)
                final = draw_text(cleaned, boxes, translated, font_size)

                col1, col2 = st.columns(2)
                with col1:
                    st.image(cv2.cvtColor(cleaned, cv2.COLOR_BGR2RGB), use_container_width=True, caption="Đã xóa chữ")
                with col2:
                    st.image(cv2.cvtColor(final, cv2.COLOR_BGR2RGB), use_container_width=True, caption="Đã dịch")

                st.dataframe({"Gốc": texts, "Dịch": translated})
else:
    st.info("Upload ảnh để bắt đầu")
