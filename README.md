Project này fine-tune model ViT5 cho nhiệm vụ chuyên sửa lỗi của PaddleOCR khi làm việc với văn bản pháp luật Việt Nam
+ stage 1: vô 2 trang web lớn chứa văn bản pháp luật (vbpl.vn với thuvienphapluat.vn) để crawl dữ liệu về, làm sạch, chuẩn hoá và ghép thành 1 câu hoàn chỉnh để làm corpus
+ stage 2: chia nhỏ các câu văn bản chuẩn và mô phỏng các lỗi của PaddleOCR khi làm việc với tiếng việt để làm bộ dataset train model ViT5
+ stage 3: fine-tune model ViT5
+ tạo frontend bằng streamlit để demo kết quả thực hiện được
---

Đây là video demo kết quả:


[![Tên video](https://img.youtube.com/vi/rrxfTMUDpOk/0.jpg)](https://www.youtube.com/watch?v=rrxfTMUDpOk)

---

Đây là bộ dữ liệu chứa các câu văn bản sạch sau khi hoàn thành stage 1:

![abc](images/6.jpg)

---

Đây là bộ dữ liệu mô phỏng các lỗi sai tiếng Việt của PaddleOCR sau khi hoàn thành stage 2:

![abc](images/5.jpg)

Dữ liệu này sẽ được dùng để fine-tune model ViT5 cho nhiệm vụ sửa lỗi sai tiếng Việt của PaddleOCR

---

Đây là kết quả sau khi chia dataset thành bộ train, valid, test: 

![abc](images/7.jpg)

---

Đây là kết quả sau khi hoàn thành stage 3:

![abc](images/1.jpg)

---

Dùng matlotlib để theo dõi quá trình model học trong 3 epoch

![abc](images/2.jpg)

---

Đây là kết quả khi cho cả 3 epoch làm việc với tập validation để chọn ra epoch tốt nhất:

![abc](images/3.jpg)

---

Đây là kết quả khi cho epoch tốt nhất (epoch 3) làm việc với tập test:

![abc](images/4.jpg)


