import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from groq import Groq
import io
import os

# ==================== CẤU HÌNH ====================
st.set_page_config(
    page_title="Image Translator - Dịch & Xóa chữ trên ảnh",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 Image Translator AI")
st.markdown("""
**Tự động dịch hình ảnh + xóa chữ + chèn tiếng Việt (hoặc 100+ ngôn ngữ)**  
Sử dụng **EasyOCR** (OCR) + **OpenCV** (xóa chữ) + **Groq API** (dịch siêu nhanh)
""")

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("⚙️ Cài đặt")
    
    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        help="Lấy miễn phí tại https://console.groq.com/keys"
    )
    
    model = st.selectbox(
        "Model Groq",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "gemma2-9b-it",
            "qwen/qwen3-32b"
        ],
        index=0
    )
    
    st.markdown("---")
    st.subheader("Ngôn ngữ")
    
    # Danh sách ngôn ngữ EasyOCR (80+)
    OCR_LANGS = {
        "Tự động / English": "en",
        "Tiếng Việt": "vi",
        "Chinese (Simplified)": "ch_sim",
        "Chinese (Traditional)": "ch_tra",
        "Japanese": "ja",
        "Korean": "ko",
        "Thai": "th",
        "Arabic": "ar",
        "French": "fr",
        "German": "de",
        "Spanish": "es",
        "Russian": "ru",
        "Portuguese": "pt",
        "Italian": "it",
        "Indonesian": "id",
        "Malay": "ms",
        "Hindi": "hi",
        "Bengali": "bn",
        "Turkish": "tr",
        "Dutch": "nl",
        "Polish": "pl",
        "Ukrainian": "uk",
        "Persian": "fa",
        "Urdu": "ur",
        "Tamil": "ta",
        "Telugu": "te",
        "Kannada": "kn",
        "Gujarati": "gu",  # một số có thể cần kiểm tra
    }
    
    source_lang = st.selectbox("Ngôn ngữ nguồn (OCR)", list(OCR_LANGS.keys()), index=0)
    target_lang = st.selectbox(
        "Ngôn ngữ đích (Dịch)",
        ["Tiếng Việt", "English", "Chinese (Simplified)", "Japanese", "Korean", 
         "Thai", "French", "German", "Spanish", "Russian", "Indonesian", 
         "Arabic", "Hindi", "Portuguese", "Italian", "Turkish", "Other..."],
        index=0
    )
    
    if target_lang == "Other...":
        target_lang = st.text_input("Nhập tên ngôn ngữ đích", value="Vietnamese")
    
    padding = st.slider("Padding mask (pixel)", 5, 30, 12)
    font_size = st.slider("Cỡ chữ vẽ lại", 12, 60, 28)
    
    st.markdown("---")
    st.info("💡 Tip: Ảnh rõ, chữ to → kết quả tốt hơn. Streamlit Cloud có giới hạn RAM nên ảnh quá lớn có thể chậm.")

# ==================== HÀM XỬ LÝ ====================
@st.cache_resource
def load_ocr(lang_list):
    return easyocr.Reader(lang_list, gpu=False)

def create_mask(image, boxes, padding=10):
    """Tạo mask từ bounding boxes của EasyOCR"""
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    for box in boxes:
        pts = np.array(box, dtype=np.int32)
        # Mở rộng box một chút
        x_min = max(0, np.min(pts[:, 0]) - padding)
        y_min = max(0, np.min(pts[:, 1]) - padding)
        x_max = min(image.shape[1], np.max(pts[:, 0]) + padding)
        y_max = min(image.shape[0], np.max(pts[:, 1]) + padding)
        cv2.rectangle(mask, (x_min, y_min), (x_max, y_max), 255, -1)
    return mask

def inpaint_image(image, mask):
    """Xóa chữ bằng OpenCV inpainting"""
    return cv2.inpaint(image, mask, 7, cv2.INPAINT_TELEA)

def translate_texts(texts, target_lang, api_key, model):
    """Dịch danh sách text bằng Groq"""
    if not api_key:
        return [f"[Cần API Key] {t}" for t in texts]
    
    client = Groq(api_key=api_key)
    results = []
    
    for text in texts:
        if not text.strip():
            results.append("")
            continue
        try:
            prompt = f"""Translate the following text to {target_lang}.
Only return the translated text, nothing else. Keep the meaning accurate and natural.

Text: {text}"""
            
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=512
            )
            results.append(completion.choices[0].message.content.strip())
        except Exception as e:
            results.append(f"[Lỗi dịch: {str(e)[:50]}]")
    return results

def draw_text_on_image(image, boxes, translated_texts, font_size=28):
    """Vẽ text đã dịch lên ảnh đã xóa chữ"""
    img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    # Cố gắng load font hỗ trợ tiếng Việt
    try:
        # Trên Linux (Streamlit Cloud) thường có DejaVu
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    for box, text in zip(boxes, translated_texts):
        if not text:
            continue
        pts = np.array(box)
        x = int(np.min(pts[:, 0]))
        y = int(np.min(pts[:, 1]))
        
        # Vẽ nền trắng mờ để dễ đọc
        bbox = draw.textbbox((x, y), text, font=font)
        draw.rectangle(
            [bbox[0]-4, bbox[1]-2, bbox[2]+4, bbox[3]+2],
            fill=(255, 255, 255, 220)
        )
        draw.text((x, y), text, fill=(0, 0, 0), font=font)
    
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

# ==================== MAIN ====================
uploaded_file = st.file_uploader(
    "📤 Upload ảnh (JPG, PNG, WEBP...)",
    type=["jpg", "jpeg", "png", "webp", "bmp"]
)

if uploaded_file:
    # Đọc ảnh
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    if image is None:
        st.error("Không đọc được ảnh!")
        st.stop()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Ảnh gốc")
        st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), use_container_width=True)
    
    # Nút xử lý
    if st.button("🚀 Bắt đầu dịch & xóa chữ", type="primary", use_container_width=True):
        with st.spinner("Đang OCR + xóa chữ + dịch..."):
            # 1. Load OCR
            lang_code = OCR_LANGS.get(source_lang, "en")
            lang_list = [lang_code, "en"] if lang_code != "en" else ["en"]
            
            try:
                reader = load_ocr(lang_list)
            except Exception as e:
                st.error(f"Lỗi load EasyOCR: {e}")
                st.stop()
            
            # 2. OCR
            results = reader.readtext(image)
            
            if not results:
                st.warning("Không phát hiện được chữ nào trên ảnh!")
                st.stop()
            
            boxes = [r[0] for r in results]
            texts = [r[1] for r in results]
            confidences = [r[2] for r in results]
            
            # 3. Tạo mask & inpaint
            mask = create_mask(image, boxes, padding=padding)
            cleaned = inpaint_image(image, mask)
            
            # 4. Dịch bằng Groq
            translated = translate_texts(texts, target_lang, groq_api_key, model)
            
            # 5. Vẽ lại chữ
            final_img = draw_text_on_image(cleaned, boxes, translated, font_size=font_size)
            
            # Hiển thị kết quả
            with col2:
                st.subheader("Đã xóa chữ")
                st.image(cv2.cvtColor(cleaned, cv2.COLOR_BGR2RGB), use_container_width=True)
            
            with col3:
                st.subheader("Đã dịch")
                st.image(cv2.cvtColor(final_img, cv2.COLOR_BGR2RGB), use_container_width=True)
            
            # Bảng chi tiết
            st.markdown("---")
            st.subheader("📋 Chi tiết text")
            
            data = []
            for i, (orig, trans, conf) in enumerate(zip(texts, translated, confidences)):
                data.append({
                    "#": i+1,
                    "Gốc": orig,
                    "Dịch": trans,
                    "Độ tin cậy OCR": f"{conf:.2f}"
                })
            
            st.dataframe(data, use_container_width=True)
            
            # Download
            st.markdown("---")
            buf = io.BytesIO()
            Image.fromarray(cv2.cvtColor(final_img, cv2.COLOR_BGR2RGB)).save(buf, format="PNG")
            st.download_button(
                "⬇️ Tải ảnh đã dịch",
                data=buf.getvalue(),
                file_name="translated_image.png",
                mime="image/png"
            )
            
            buf2 = io.BytesIO()
            Image.fromarray(cv2.cvtColor(cleaned, cv2.COLOR_BGR2RGB)).save(buf2, format="PNG")
            st.download_button(
                "⬇️ Tải ảnh đã xóa chữ (không text)",
                data=buf2.getvalue(),
                file_name="cleaned_image.png",
                mime="image/png"
            )

else:
    st.info("👆 Upload một ảnh để bắt đầu. Ảnh manga, meme, screenshot, biển báo đều được.")

# Footer
st.markdown("---")
st.caption("Made for Streamlit Cloud + GitHub | OCR: EasyOCR | Inpaint: OpenCV | Translate: Groq API")
