# Hướng dẫn tự kiểm tra mù T02

Đây là lần tự kiểm tra thủ công để bổ sung bằng chứng cho bài cá nhân, không phải nhãn chuẩn ẩn (ground truth) của giảng viên. Vì bạn làm một mình, hãy ghi kết quả là **solo blind audit** (tự kiểm tra mù một người), không gọi là đánh giá độc lập bởi người thứ hai.

Mẫu gồm 20 ảnh thuộc tập `eval`, được chọn theo seed 42 và không nằm trong queue 20 ảnh đã review lần đầu. Khi điền mẫu, bạn chưa xem gợi ý của pipeline cho các ảnh này. Cách làm này giảm ảnh hưởng từ gợi ý ban đầu, nhưng không tạo ra người đánh giá thứ hai hay bộ nhãn chuẩn chính thức.

## Cách thực hiện

1. Mở từng ảnh theo đường dẫn trong `fixtures/t02_raw_qc/`. Chỉ xem ảnh; không mở điểm số, thứ hạng, hành động gợi ý hoặc kết quả review lần đầu trong lúc gán nhãn.
2. Điền `reviewer`, `defect_type` và `is_defect` theo định nghĩa của bài lab. Chỉ điền `severity` nếu giảng viên đã định nghĩa rõ các mức; nếu chưa, để trống.
3. Điền `recognizability_pct`, `reviewer_action`, `confidence_1_to_5` và `review_note` như nhận xét bổ sung của bạn. Với `reviewer_action`, dùng `KEEP` hoặc `RECAPTURE`. Ghi độ tự tin từ 1 (thấp) đến 5 (cao). Áp dụng phạm vi trong [`review_guideline_t02.md`](../review_guideline_t02.md): nhận diện loại vật thể ở mức khái quát, màu chính và vị trí tương đối.
4. Lưu bản đã điền thành `reports/evidence/t02_solo_blind_audit.csv`; giữ nguyên mẫu gốc và tên các cột tiếng Anh để dữ liệu tương thích với pipeline.
5. Không điều chỉnh ngưỡng pipeline dựa trên 20 ảnh eval này. Khi báo cáo, nói rõ đây là tự kiểm tra mù do một người thực hiện.

> Kết quả này không đo được mức độ đồng thuận giữa nhiều người đánh giá và không thay thế nhãn GT của giảng viên hay kết quả đánh giá chính thức.
