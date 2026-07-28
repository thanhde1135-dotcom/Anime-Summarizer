import cv2
import numpy as np
import streamlit as st

st.title("Ứng dụng Tô màu Loang (Flood Fill) trực tuyến")

# Nút bấm để thực hiện
if st.button("Chạy thuật toán tô màu"):
  # 1. Tạo ảnh trắng và vẽ hình tròn khung
  img = np.ones((400, 400, 3), dtype=np.uint8) * 255
  cv2.circle(img, (200, 200), 100, (0, 0, 0), 3)

  # 2. Điểm neo và màu mới (BGR)
  seed_point = (200, 200)
  new_color = (255, 0, 0)  # Xanh dương trong OpenCV

  # 3. Tạo mặt nạ và thực hiện Flood Fill
  h, w = img.shape[:2]
  mask = np.zeros((h + 2, w + 2), np.uint8)
  cv2.floodFill(
      img,
      mask,
      seed_point,
      new_color,
      (10, 10, 10),
      (10, 10, 10),
      cv2.FLOODFILL_FIXED_RANGE,
  )

  # 4. OpenCV dùng chuẩn BGR, cần đổi sang RGB để trình duyệt hiển thị đúng màu
  img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

  # 5. Hiển thị kết quả lên trang web
  st.image(img_rgb, caption="Kết quả tô màu trên web", use_container_width=True)
else:
  st.info('Nhấn vào nút bên trên để xem kết quả xử lý từ mã nguồn.')
    
