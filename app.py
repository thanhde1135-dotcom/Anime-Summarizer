import re
import io
import os
import hashlib
import tempfile
import urllib.parse
import ipaddress
import socket
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from PIL import Image as PILImage
import gradio as gr

TMP_DIR = Path(tempfile.gettempdir()) / "image_stream_scraper"
TMP_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
}

AD_URL_PATTERNS = [
    "doubleclick.net", "googlesyndication", "googleadservices",
    "adservice.google", "amazon-adsystem", "taboola", "outbrain",
    "scorecardresearch", "/ads/", "adserver", "advert", "banner",
    "promo", "tracking", "pixel",
]

AD_TEXT_PATTERNS = [
    r"\bads?\b", r"advert", r"banner", r"promo", r"sponsor",
    r"tracking", r"pixel", r"logo", r"icon", r"avatar", r"favicon",
]

MIN_DIMENSION = 20
MIN_AREA = 300

stop_event = threading.Event()
session = requests.Session()
session.headers.update(HEADERS)


def is_private_host(hostname: str) -> bool:
    if not hostname:
        return True
    if hostname.lower() in {"localhost", "127.0.0.1", "::1"}:
        return True
    try:
        infos = socket.getaddrinfo(hostname, None)
        for info in infos:
            ip = info[4][0]
            ip_obj = ipaddress.ip_address(ip)
            if (ip_obj.is_private or ip_obj.is_loopback or
                ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved):
                return True
    except Exception:
        return True
    return False


def safe_join_url(base_url: str, maybe_url: str) -> str | None:
    if not maybe_url:
        return None
    maybe_url = maybe_url.strip()
    if maybe_url.startswith("data:"):
        return None
    abs_url = urllib.parse.urljoin(base_url, maybe_url)
    parsed = urllib.parse.urlparse(abs_url)
    if parsed.scheme not in {"http", "https"}:
        return None
    if not parsed.hostname or is_private_host(parsed.hostname):
        return None
    return abs_url


def url_relevant_for_ads(url: str) -> bool:
    return any(p in url.lower() for p in AD_URL_PATTERNS)


def text_relevant_for_ads(*texts) -> bool:
    joined = " ".join([t for t in texts if t]).lower()
    return any(re.search(p, joined) for p in AD_TEXT_PATTERNS)


def extract_best_from_srcset(srcset: str) -> str | None:
    if not srcset:
        return None
    best_url = None
    best_score = -1
    for part in srcset.split(","):
        part = part.strip()
        if not part:
            continue
        pieces = part.split()
        url = pieces[0].strip()
        score = 0
        if len(pieces) > 1:
            desc = pieces[1].strip().lower()
            if desc.endswith("w"):
                try: score = int(desc[:-1])
                except: pass
            elif desc.endswith("x"):
                try: score = int(float(desc[:-1]) * 1000)
                except: pass
        if score > best_score:
            best_score = score
            best_url = url
    return best_url


def fetch_html(url: str, referer: str | None = None) -> str:
    headers = {}
    if referer:
        headers["Referer"] = referer
    r = session.get(url, headers=headers, timeout=25)
    r.raise_for_status()
    return r.text


def is_ehentai_gallery(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    host = (parsed.hostname or "").lower()
    return host in {"e-hentai.org", "exhentai.org"} and "/g/" in parsed.path


def get_ehentai_image_page_links(gallery_url: str):
    links = []
    page = 0
    while True:
        if stop_event.is_set():
            break
        page_url = gallery_url if page == 0 else f"{gallery_url}?p={page}"
        try:
            html = fetch_html(page_url)
        except Exception:
            break
        soup = BeautifulSoup(html, "lxml")
        found = False
        for a in soup.select("#gdt a, .gdtm a, .gdtl a"):
            href = a.get("href")
            if href and "/s/" in href:
                abs_link = safe_join_url(gallery_url, href)
                if abs_link and abs_link not in links:
                    links.append(abs_link)
                    found = True
        if not found:
            break
        page += 1
        time.sleep(0.25)
        if page > 60:
            break
    return links


def extract_full_image_from_eh_page(page_url: str) -> str | None:
    try:
        html = fetch_html(page_url, referer=page_url)
        soup = BeautifulSoup(html, "lxml")
        img = soup.select_one("#img") or soup.select_one("#i3 img")
        if img and img.get("src"):
            return img["src"]
    except Exception:
        pass
    return None


def download_image(url: str, referer: str | None = None) -> str | None:
    try:
        headers = {"Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"}
        if referer:
            headers["Referer"] = referer
        r = session.get(url, headers=headers, timeout=25, stream=True)
        r.raise_for_status()

        content_type = r.headers.get("content-type", "").lower()
        if "image" not in content_type and not url.lower().split("?")[0].endswith(
            (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".avif")
        ):
            return None

        raw = r.content
        if len(raw) < 200:
            return None

        try:
            img = PILImage.open(io.BytesIO(raw))
            img.load()
        except Exception:
            return None

        h = hashlib.sha1(url.encode()).hexdigest()[:16]
        ext = {
            "jpeg": ".jpg", "jpg": ".jpg", "png": ".png",
            "webp": ".webp", "gif": ".gif", "bmp": ".bmp", "avif": ".avif"
        }.get((img.format or "").lower(), ".jpg")

        path = TMP_DIR / f"{h}{ext}"
        with open(path, "wb") as f:
            f.write(raw)
        return str(path)
    except Exception:
        return None


def process_one_eh_image(page_link: str):
    if stop_event.is_set():
        return None
    img_url = extract_full_image_from_eh_page(page_link)
    if not img_url:
        return None
    img_url = img_url.split("#")[0]
    return download_image(img_url, referer=page_link)


def stream_images(page_url: str):
    stop_event.clear()
    page_url = (page_url or "").strip()
    if not page_url:
        yield [], "Vui lòng nhập URL."
        return

    if not page_url.startswith(("http://", "https://")):
        page_url = "https://" + page_url

    parsed = urllib.parse.urlparse(page_url)
    if not parsed.hostname or is_private_host(parsed.hostname):
        yield [], "URL không hợp lệ."
        return

    gallery = []
    seen = set()

    yield gallery, "Đang tải trang..."

    if is_ehentai_gallery(page_url):
        yield gallery, "Đang lấy danh sách trang ảnh..."
        try:
            image_pages = get_ehentai_image_page_links(page_url)
        except Exception as e:
            yield gallery, f"Lỗi: {e}"
            return

        if stop_event.is_set():
            yield gallery, "Đã dừng."
            return

        total = len(image_pages)
        if total == 0:
            yield gallery, "Không tìm thấy trang ảnh."
            return

        yield gallery, f"Tìm thấy {total} ảnh → bắt đầu tải nhanh hơn..."

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {executor.submit(process_one_eh_image, link): link for link in image_pages}

            done = 0
            for future in as_completed(futures):
                if stop_event.is_set():
                    for f in futures:
                        f.cancel()
                    yield gallery, f"Đã dừng. Đã tải {len(gallery)} ảnh."
                    return

                result = future.result()
                done += 1
                if result and result not in seen:
                    seen.add(result)
                    gallery.append(result)
                    yield gallery, f"Đã tải {len(gallery)}/{total} ảnh..."

                time.sleep(0.15)

        yield gallery, f"Hoàn tất! Tổng: {len(gallery)} ảnh"
        return

    try:
        html = fetch_html(page_url)
    except Exception as e:
        yield gallery, f"Không tải được trang: {e}"
        return

    items = []
    soup = BeautifulSoup(html, "lxml")
    for img in soup.find_all("img"):
        src = (img.get("src") or img.get("data-src") or img.get("data-lazy-src")
               or img.get("data-original") or img.get("data-url"))
        srcset = img.get("srcset") or img.get("data-srcset")
        if not src and srcset:
            src = extract_best_from_srcset(srcset)
        abs_url = safe_join_url(page_url, src)
        if abs_url:
            items.append({
                "url": abs_url,
                "alt": img.get("alt", ""),
                "cls": " ".join(img.get("class", []) or []),
                "width": img.get("width"),
                "height": img.get("height"),
            })

    clean_items = []
    for item in items:
        url = item["url"]
        if url in seen:
            continue
        if url_relevant_for_ads(url) or text_relevant_for_ads(url, item["alt"], item["cls"]):
            continue
        w, h = item.get("width"), item.get("height")
        try:
            w = int(w) if w and str(w).isdigit() else None
            h = int(h) if h and str(h).isdigit() else None
        except:
            w = h = None
        if w and h and (w < MIN_DIMENSION or h < MIN_DIMENSION or w*h <= MIN_AREA):
            continue
        clean_items.append(item)
        seen.add(url)

    if not clean_items:
        yield gallery, "Không tìm thấy ảnh."
        return

    yield gallery, f"Tìm thấy {len(clean_items)} ảnh → đang tải..."

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(download_image, item["url"], page_url): item["url"]
            for item in clean_items
        }
        for future in as_completed(futures):
            if stop_event.is_set():
                yield gallery, f"Đã dừng. Đã tải {len(gallery)} ảnh."
                return
            path = future.result()
            if path:
                gallery.append(path)
                yield gallery, f"Đã tải {len(gallery)} ảnh..."

    yield gallery, f"Xong! Tổng: {len(gallery)} ảnh"


def stop_scraping():
    stop_event.set()
    return "Đang dừng..."


with gr.Blocks(title="Image Stream Scraper") as demo:
    gr.Markdown("### Quét ảnh nhanh (tối ưu điện thoại)")

    url_in = gr.Textbox(
        label="URL",
        placeholder="https://e-hentai.org/g/xxxxx/yyyyy/",
        lines=1
    )

    with gr.Row():
        go_btn = gr.Button("Bắt đầu", variant="primary", size="lg")
        stop_btn = gr.Button("Dừng", variant="stop", size="lg")

    gallery = gr.Gallery(
        label="Ảnh",
        columns=2,
        height=500,
        object_fit="contain",
        show_label=True
    )
    status = gr.Textbox(label="Trạng thái", interactive=False, lines=1)

    go_btn.click(fn=stream_images, inputs=url_in, outputs=[gallery, status], show_progress="hidden")
    url_in.submit(fn=stream_images, inputs=url_in, outputs=[gallery, status], show_progress="hidden")
    stop_btn.click(fn=stop_scraping, outputs=status)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=port)
    
