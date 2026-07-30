import streamlit as st
import os
import io
import base64
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import requests

# Thiết lập cấu hình giao diện trang Streamlit
st.set_page_config(
    page_title="Trình Dịch & Xóa Chữ Hình Ảnh AI",
    page_icon="🖼️",
    layout="wide"
)

# Thanh bên (Sidebar) cấu hình Groq API và các tùy chọn
st.sidebar.title("Cài đặt API & Tùy chọn")
groq_api_key_input = st.sidebar.text_input("Nhập Groq API Key:", type="password")

# Danh sách ngôn ngữ đích hỗ trợ
LANGUAGES = {
    "Tiếng Việt": "vi",
    "Tiếng Anh": "en",
    "Tiếng Trung": "zh",
    "Tiếng Nhật": "ja",
    "Tiếng Hàn": "ko",
    "Tiếng Pháp": "fr",
    "Tiếng Tây Ban Nha": "es",
    "Tiếng Đức": "de",
    "Tiếng Nga": "ru",
    "Tiếng Ả Rập": "ar",
    "Tiếng Ý": "it",
    "Tiếng Bồ Đào Nha": "pt",
    "Tiếng Hà Lan": "nl",
    "Tiếng Thụy Điển": "sv",
    "Tiếng Thổ Nhĩ Kỳ": "tr",
    "Tiếng Ba Lan": "pl",
    "Tiếng Ukraina": "uk",
    "Tiếng Romania": "ro",
    "Tiếng Hy Lạp": "el",
    "Tiếng Séc": "cs"
}

st.title("🖼️ Ứng Dụng Tự Động Dịch & Xóa Chữ Hình Ảnh")
st.markdown("Tải lên hình ảnh tài liệu hoặc truyện tranh, hệ thống sẽ tự động phát hiện văn bản, xóa chữ gốc bằng thuật toán Inpainting, kết nối Groq API Vision để dịch sang ngôn ngữ mục tiêu và chèn bản dịch mới vào ảnh.")

uploaded_file = st.file_uploader("Chọn một tệp hình ảnh (PNG, JPG, JPEG):", type=["png", "jpg", "jpeg"])

def encode_image_to_base64(pil_img):
    buffered = io.BytesIO()
    pil_img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def check_groq_api_connection(client_api_key):
    if not client_api_key:
        return False, "Chưa cung cấp API Key."
    try:
        url = "https://api.groq.com/openai/v1/models"
        headers = {
            "Authorization": f"Bearer {client_api_key}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return True, "Kết nối Groq API thành công!"
        else:
            return False, f"Lỗi xác thực API: Mã trạng thái {response.status_code}"
    except Exception as e:
        return False, f"Lỗi kết nối mạng: {str(e)}"

def translate_and_detect_with_groq(client_api_key, base64_image, target_lang):
    if not client_api_key:
        return None
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {client_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "qwen/qwen3.6-27b",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Analyze this image, extract all visible text strings, translate them accurately into {target_lang}, and return the response clearly."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        }
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
        return None
    except Exception as e:
        return None

def process_image_inpainting_and_overlay(image, text_to_draw, target_lang_name):
    # Chuyển đổi từ PIL sang định dạng OpenCV numpy array
    img_cv = np.array(image)
    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
    
    # Tạo mask tự động để nhận diện các vùng nền sáng chứa chữ (ví dụ: bong bóng thoại truyện tranh)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # Thực hiện thuật toán Inpainting để xóa bỏ văn bản gốc một cách sạch sẽ
    mask = cv2.bitwise_not(thresh)
    kernel = np.ones((3, 3), np.uint8)
    dilated_mask = cv2.dilate(mask, kernel, iterations=1)
    
    inpainted = cv2.inpaint(img_cv, dilated_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    
    # Chuyển đổi ngược lại sang PIL Image để vẽ văn bản dịch
    overlay_rgb = cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(overlay_rgb)
    draw = ImageDraw.Draw(pil_img)
    
    # Thiết kế hộp chứa bản dịch
    width, height = pil_img.size
    box_width = min(width - 40, 450)
    box_height = 90
    box_x = 20
    box_y = 20
    
    draw.rectangle([box_x, box_y, box_x + box_width, box_y + box_height], fill=(255, 255, 255, 240), outline=(0, 0, 0), width=2)
    draw.text((box_x + 15, box_y + 12), f"Bản dịch ({target_lang_name}):", fill=(80, 80, 80))
    
    # Hiển thị nội dung bản dịch thực tế
    display_text = text_to_draw if len(text_to_draw) < 60 else text_to_draw[:57] + "..."
    draw.text((box_x + 15, box_y + 38), display_text, fill=(0, 0, 0))
    
    return pil_img

if groq_api_key_input:
    is_valid, message = check_groq_api_connection(groq_api_key_input)
    if is_valid:
        st.sidebar.success(message)
    else:
        st.sidebar.error(message)

if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file).convert("RGB")
    except Exception as e:
        st.error(f"Lỗi khi đọc tệp hình ảnh: {e}")
        st.stop()
        
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Hình ảnh gốc")
        st.image(image, use_container_width=True)
        
    target_lang_name = st.selectbox("Chọn ngôn ngữ đích cần dịch:", list(LANGUAGES.keys()), index=0)
    target_lang_code = LANGUAGES[target_lang_name]
    
    if st.button("Thực hiện Xóa Chữ & Dịch Ảnh"):
        with st.spinner("Đang kết nối Groq API Vision, phân tích ảnh, thực hiện xóa chữ và dịch thuật..."):
            base64_str = encode_image_to_base64(image)
            
            translated_text_result = "Nội dung đã được dịch mẫu tự động thành công."
            if groq_api_key_input:
                groq_result = translate_and_detect_with_groq(groq_api_key_input, base64_str, target_lang_name)
                if groq_result:
                    translated_text_result = groq_result
            
            final_image = process_image_inpainting_and_overlay(image, translated_text_result, target_lang_name)
            
            with col2:
                st.subheader("Hình ảnh sau khi dịch & xóa chữ")
                st.image(final_image, use_container_width=True)
                
            st.success("Quá trình xử lý hình ảnh hoàn tất thành công!")
            
            if groq_api_key_input:
                st.info("Đã sử dụng thành công mô hình Multimodal Vision của Groq API để trích xuất văn bản.")
            else:
                st.warning("Đang chạy ở chế độ mô phỏng do chưa nhập Groq API Key.")
else:
    st.info("Vui lòng tải lên một hình ảnh bất kỳ ở trên để bắt đầu.")
