import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def crawl_website(url_input, max_pages=20):
    """Hàm cào web tự động liên tục qua các link"""
    visited = set()
    to_visit = [url_input]
    crawled_urls = []
    combined_text = ""
    error_log = ""
    
    scraper = cloudscraper.create_scraper()
    
    while to_visit and len(crawled_urls) < max_pages:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue
        visited.add(current_url)
        
        try:
            res = scraper.get(current_url, timeout=8)
            if res.status_code == 200:
                crawled_urls.append(current_url)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # Xóa rác
                for el in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    el.decompose()
                    
                page_text = soup.get_text(separator=' ', strip=True)
                combined_text += f"\n--- NGUỒN: {current_url} ---\n" + page_text
                
                # Quét link con
                for link in soup.find_all('a', href=True):
                    abs_url = urljoin(current_url, link['href'])
                    parsed = urlparse(abs_url)
                    if parsed.scheme in ['http', 'https']:
                        clean_url = abs_url.split('#')[0]
                        if clean_url not in visited and clean_url not in to_visit:
                            to_visit.append(clean_url)
            else:
                error_log = f"Trang từ chối truy cập (Mã lỗi {res.status_code})"
        except Exception as e:
            error_log = f"Lỗi kết nối: {str(e)}"
            
    return combined_text, crawled_urls, error_log
          
