import io
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from PIL import Image
import streamlit as st

st.set_page_config(
    page_title="Trích xuất & Tải Ảnh", page_icon="🖼️", layout="centered"
)

st.title("🖼️ Trích xuất Ảnh từ Website")
st.write("Nhập đường link website bên dưới để quét và tải tất cả hình ảnh.")

# Ô nhập đường link
url_input = st.text_input("Nhập URL website:", placeholder="https://example.com")


# Hàm tải dữ liệu ảnh an toàn
def download_image(img_url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
    }
    try:
        res = requests.get(img_url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.content
    except Exception:
        pass
    return None


if url_input:
    if not (
        url_input.startswith("http://") or url_input.startswith("https://")
    ):
        url_input = "https://" + url_input

    with st.spinner("Đang quét và lấy danh sách ảnh..."):
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                    " AppleWebKit/537.36 (KHTML, like Gecko)"
                    " Chrome/115.0.0.0 Safari/537.36"
                )
            }
            response = requests.get(url_input, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            # Tìm tất cả thẻ <img>
            img_tags = soup.find_all("img")
            img_urls = []

            for img in img_tags:
                src = img.get("src") or img.get("data-src")
                if src:
                    # Chuyển link tương đối thành link tuyệt đối
                    full_url = urljoin(url_input, src)
                    if full_url not in img_urls and not full_url.startswith(
                        "data:image"
                    ):
                        img_urls.append(full_url)

            st.success(f"Tìm thấy **{len(img_urls)}** hình ảnh!")
            st.divider()

            # Hiển thị từng ảnh và nút tải tương ứng
            for idx, img_url in enumerate(img_urls, start=1):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.image(img_url, use_column_width=True)

                with col2:
                    st.write(f"**Ảnh #{idx}**")
                    img_data = download_image(img_url)

                    if img_data:
                        # Lấy đuôi file ảnh hoặc mặc định là jpg
                        ext = (
                            img_url.split(".")[-1]
                            .split("?")[0]
                            .lower()[:4]
                        )
                        if ext not in ["jpg", "jpeg", "png", "webp", "gif"]:
                            ext = "jpg"

                        st.download_button(
                            label="📥 Tải ảnh này",
                            data=img_data,
                            file_name=f"image_{idx}.{ext}",
                            mime=f"image/{ext}",
                            key=f"btn_{idx}",
                        )
                    else:
                        st.caption("⚠️ Không thể tải trực tiếp ảnh này.")

                st.divider()

        except Exception as e:
            st.error(f"Không thể kết nối tới website. Lỗi: {e}")
                
