import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urlparse

# --- DANH SÁCH LINK CẦN CRAWL ---
list_urls = [
    "https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=184082",
    "https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=184062",
    'https://thuvienphapluat.vn/van-ban/Xay-dung-Do-thi/Luat-Xay-dung-2025-so-135-2025-QH15-675213.aspx',
    'https://thuvienphapluat.vn/van-ban/Cong-nghe-thong-tin/Luat-Chuyen-doi-so-2025-so-148-2025-QH15-675262.aspx',
    # .... (rất nhiều link)
]
# --------------------------
# Hàm fetch HTML dùng chung
# --------------------------
def fetch_html(url):
    headers = {
        # user-agent để giảm nguy cơ bị chặn / trả về HTML khác thường
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }
    # vbpl.vn hay lỗi SSL => verify=False
    resp = requests.get(url, headers=headers, verify=False, timeout=20)
    resp.raise_for_status()
    return resp.text
# --------------------------
# Hàm trích nội dung theo từng site
# --------------------------
def extract_text_vbpl(soup: BeautifulSoup) -> str | None:
    content_div = soup.find('div', {"id": "toanvancontent"})
    if not content_div:
        return None
    return content_div.get_text(separator=' ', strip=True)

def extract_text_thuvienphapluat(soup: BeautifulSoup) -> str | None:
    """
    thuvienphapluat có thể thay đổi cấu trúc theo thời gian => thử nhiều selector phổ biến, lấy cái nào có text dài nhất
    """
    candidates = []
    selectors = [
        # Các vùng nội dung hay gặp
        "div#divContentDoc",          # thường gặp ở nhiều trang
        "div#content",                # một số template cũ
        "div.content",                # dự phòng
        "div[class*='content']",      # dự phòng rộng hơn
        "article",                    # nếu bọc nội dung trong article
        "div#ctl00_ContentPlaceHolder1_Panel1",  # một số trang ASP.NET
    ]
    for sel in selectors:
        for node in soup.select(sel):
            txt = node.get_text(separator=' ', strip=True)
            if txt and len(txt) > 500:     # ngưỡng để tránh bắt nhầm menu/header
                candidates.append(txt)
    if not candidates:
        return None
    # lấy khối có nội dung dài nhất
    return max(candidates, key=len)

def extract_text_by_domain(url: str, html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    domain = urlparse(url).netloc.lower()
    if "vbpl.vn" in domain:
        return extract_text_vbpl(soup)
    if "thuvienphapluat.vn" in domain:
        return extract_text_thuvienphapluat(soup)
    return None

# --- PHẦN 1: HÀM CRAWL DỮ LIỆU ---
def crawl_data(urls):
    print(f"Bắt đầu cào dữ liệu từ {len(urls)} đường link")
    raw_content = ""
    for i, url in enumerate(urls):
        try:
            print(f"   [{i+1}/{len(urls)}] Đang tải: {url} ...")
            html = fetch_html(url)
            text = extract_text_by_domain(url, html)
            if text:
                raw_content += text + "\n"
                print(f"Lấy được {len(text)} ký tự.")
            else:
                print(f"Không tìm thấy vùng nội dung phù hợp cho link này.")
            time.sleep(1)
        except Exception as e:
            print(f"Lỗi ngoại lệ: {e}")
    return raw_content

# --- PHẦN 2: HÀM XỬ LÝ & LÀM SẠCH ---
def process_and_clean(text):
    print("\n Đang xử lý và làm sạch dữ liệu...")
    # Xóa các thẻ rác / chuẩn hóa khoảng trắng (FIX nhỏ: '\ ' là pattern không cần thiết)
    text = re.sub(r'[ \t]+', ' ', text)
    # Xóa các ký tự trang trí thừa
    text = re.sub(r'-{3,}', ' ', text)
    # Nối các dòng bị ngắt quãng
    text = text.replace('\n', ' ')
    # Chuẩn hóa khoảng trắng
    text = re.sub(r'\s+', ' ', text).strip()
    # Tách câu dựa trên dấu chấm câu (. ! ?)
    raw_sentences = re.split(r'(?<=[.!?])\s+', text)
    clean_sentences = []
    unique_set = set()
    garbage_patterns = [
        r'^CỘNG HÒA XÃ HỘI', r'^Độc lập - Tự do',
        r'^LUẬT', r'^NGHỊ ĐỊNH', r'^THÔNG TƯ', r'^QUYẾT ĐỊNH',
        r'^Số:?\s?\d+', r'^Nơi nhận:', r'^Lưu:', r'Hà Nội, ngày',
        r'^Điều \d+', r'^Chương \d+', r'^Mục \d+', r'^Phụ lục',
        r'^\d+\.$', r'^[a-z]\)$'
    ]
    bullet_pattern = r'^(\d+\.|[a-z]\)|-|–|\+)\s+'
    for s in raw_sentences:
        s = s.strip()
        if len(s.split()) < 5:
            continue
        s = re.sub(bullet_pattern, '', s).strip()
        is_garbage = False
        for pattern in garbage_patterns:
            if re.search(pattern, s, re.IGNORECASE):
                is_garbage = True
                break
        if is_garbage:
            continue
        if s and s[0].islower():
            s = s[0].upper() + s[1:]
        if s and not s.endswith(('.', '!', '?', '”', '"')):
            s = s + '.'
        if s not in unique_set:
            unique_set.add(s)
            clean_sentences.append(s)
    return clean_sentences

# --- PHẦN 3: CHẠY CHƯƠNG TRÌNH CHÍNH ---
def main():
    raw_data = crawl_data(list_urls)
    if not raw_data:
        print("Không thu thập được dữ liệu nào. Kiểm tra lại link.")
        return
    final_sentences = process_and_clean(raw_data)
    output_file = '/content/drive/MyDrive/Colab Notebooks/DA2-v2/final_corpus_perfect_2.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in final_sentences:
            f.write(line + '\n')
    print("\n" + "="*40)
    print(f"XONG GIAI ĐOẠN 1")
    print(f"Tổng số câu sạch thu được: {len(final_sentences)}")
    print(f"File đã lưu: {output_file}")
    print("="*40)
    print("Xem trước 5 câu:")
    for i in range(min(5, len(final_sentences))):
        print(f"{i+1}. {final_sentences[i]}")

if __name__ == "__main__":
    main()