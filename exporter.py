def generate_report(crawled_urls, web_text):
    """Đóng gói dữ liệu cào được thành một bản báo cáo hoàn chỉnh"""
    report = f"# 📊 BÁO CÁO TRÍ TUỆ NHÂN TẠO - CÀO WEB\n\n"
    report += f"- **Tổng số trang đã quét:** {len(crawled_urls)}\n"
    report += f"- **Tổng dung lượng ký tự:** {len(web_text)} chữ\n\n"
    report += f"## 🌐 Danh sách các đường link nguồn:\n"
    for url in crawled_urls:
        report += f"- {url}\n"
    report += f"\n---\n\n## 📝 Nội dung chi tiết đã tiếp thu:\n\n{web_text}"
    return report
  
