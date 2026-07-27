import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import io
import zipfile

def get_images_as_zip(url):
    """Tự động cào tất cả các link ảnh trên trang, tải về và đóng gói thành file ZIP"""
    scraper = cloudscraper.create_scraper()
    try:
        res = scraper.get(url, timeout=12)
        if res.status_code != 200:
            return None, f"Không thể truy cập trang (Mã lỗi {res.status_code})"
        
        soup = BeautifulSoup(res.text, 'html.parser')
        img_tags = soup.find_all('img')
        
        image_urls = set()
        for img in img_tags:
            # Lấy link ảnh từ các thuộc tính phổ biến (src, data-src, data-original)
            src = img.get('src') or img.get('data-src') or img.get('data-original')
            if src:
                abs_url = urljoin(url, src)
                parsed = urlparse(abs_url)
                if parsed.scheme in ['http', 'https']:
                    image_urls.add(abs_url)
        
        if not image_urls:
            return None, "Không tìm thấy đường dẫn ảnh nào trên trang này!"
        
        # Tạo file ZIP trong bộ nhớ RAM (In-memory zip file)
        zip_buffer = io.BytesIO()
        success_count = 0
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for idx, img_url in enumerate(image_urls):
                try:
                    img_res = scraper.get(img_url, timeout=6)
                    if img_res.status_code == 200:
                        # Trích xuất tên file từ đường dẫn URL
                        parsed_path = urlparse(img_url).path
                        filename = parsed_path.split('/')[-1]
                        
                        # Nếu tên file không hợp lệ hoặc thiếu định dạng thì đặt tên mới
                        if not filename or '.' not in filename or len(filename) > 50:
                            filename = f"image_{idx+1}.jpg"
                        else:
                            filename = f"{idx+1}_{filename}"
                            
                        zip_file.writestr(filename, img_res.content)
                        success_count += 1
                except Exception:
                    continue
                    
        zip_buffer.seek(0)
        if success_count == 0:
            return None, "Tìm thấy link ảnh nhưng trang web đã chặn quyền tải trực tiếp."
            
        return zip_buffer, f"Đã tải thành công {success_count} tấm ảnh vào file ZIP!"
        
    except Exception as e:
        return None, f"Lỗi kết nối: {str(e)}"
      
