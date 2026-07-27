import os
import csv

KNOWLEDGE_DIR = "knowledge"
DEFAULT_FILE = os.path.join(KNOWLEDGE_DIR, "general.csv")

def init_database():
    """Tự động tạo thư mục và file mẫu nếu chưa có"""
    if not os.path.exists(KNOWLEDGE_DIR):
        os.makedirs(KNOWLEDGE_DIR)
    if not os.path.exists(DEFAULT_FILE):
        with open(DEFAULT_FILE, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["cau_hoi", "cau_tra_loi"])
            writer.writerow(["xin chào", "Dạ chào anh/chị, hệ thống chuyên nghiệp đã sẵn sàng! 🚀"])

def load_all_knowledge():
    """Đọc và gộp toàn bộ dữ liệu từ TẤT CẢ các file CSV trong thư mục knowledge"""
    init_database()
    knowledge = {}
    for filename in os.listdir(KNOWLEDGE_DIR):
        if filename.endswith(".csv"):
            file_path = os.path.join(KNOWLEDGE_DIR, filename)
            try:
                with open(file_path, mode="r", encoding="utf-8") as file:
                    reader = csv.reader(file)
                    next(reader, None)
                    for row in reader:
                        if len(row) >= 2:
                            q = row[0].strip().lower()
                            a = row[1].strip()
                            knowledge[q] = a
            except Exception:
                pass
    return knowledge

def save_knowledge(question, answer, filename="general.csv"):
    """Lưu kiến thức mới vào một file chỉ định"""
    init_database()
    file_path = os.path.join(KNOWLEDGE_DIR, filename)
    file_exists = os.path.exists(file_path)
    
    with open(file_path, mode="a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["cau_hoi", "cau_tra_loi"])
        writer.writerow([question, answer])
                          
