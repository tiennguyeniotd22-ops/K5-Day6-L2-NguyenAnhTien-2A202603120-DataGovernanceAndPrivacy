# T02 showcase — dàn ý 3 phút

> Dàn ý để trình bày trực tiếp hoặc chuyển thành 5 slide. Không có metric GT chính thức trong checkout; không phát biểu score chất lượng hoặc tuyên bố baseline thắng PoC.

## Slide 1 — Bài toán T02
- Xếp hạng ảnh mờ, lóa, tối hoặc nén lỗi để reviewer tìm ảnh cần xử lý.
- Input: 96 ảnh synthetic; 56 dev, 40 eval; B=20; seed 42.
- Phạm vi quyết định của reviewer: loại vật thể, màu chính, vị trí tương đối; biển số không thuộc mục tiêu hiện tại.

**Lời nói:** “Tôi làm pipeline QC ảnh nhẹ chạy CPU. Mục tiêu là ưu tiên ảnh đáng xem cho người review, không tự động phát hành ảnh.”

## Slide 2 — Quy trình 5 bước
1. Đọc ảnh, metadata và xác minh manifest.
2. Tính sharpness, brightness, saturation và blockiness.
3. Ghép rủi ro, xếp hạng score và tạo queue 20 ảnh.
4. Review ảnh, ghi quyết định/override và audit log.
5. Đưa quyết định batch `GO/HOLD/REWORK` kèm reason code.

**Ảnh cần chụp:** terminal cho lệnh chạy thành công và contact sheet 20 ảnh.

## Slide 3 — Baseline và PoC
- Baseline: một ngưỡng Laplacian; cutoff lấy percentile 20 trên dev, không đọc nhãn.
- PoC: bốn tín hiệu blur/glare/dark/compression; score tổng hợp ưu tiên rủi ro lớn nhất.
- Cả hai chạy cùng pool, seed 42 và budget 20.
- Trong clone sạch, hai queue top-20 trùng 16/20 ảnh; mỗi pipeline chọn riêng 4 ảnh. Đây chỉ là mức giống nhau của queue, không đo chất lượng phát hiện lỗi.
- Thời gian clone sạch: baseline 0.9754 s; PoC 2.0317 s, mỗi bên một lần chạy. Không dùng một lần đo để kết luận tốc độ tổng quát.

**Lời nói:** “Đã chạy và lưu hai đầu ra. Tôi chưa kết luận model nào tốt hơn vì chưa có GT để tính Defect Recall@B.”

## Slide 4 — Human review và risk gate
- 20 quyết định review: 17 approve, 3 edit thành `KEEP`.
- Reviewer giữ ảnh khi vẫn nhận ra mục tiêu thô; ba chỉnh sửa là bằng chứng định tính về trường hợp pipeline có thể yêu cầu chụp lại quá mức.
- Sau review: 17 ảnh `RECAPTURE`; batch `REWORK / RECAPTURE_REQUIRED`.
- Score xếp hạng không bị sửa bởi override hành động.

**Ảnh cần chụp:** review CSV, audit log, `decision.json`.

## Slide 5 — Giới hạn và bước tiếp
- Preflight 0 lỗi; pytest exit 0; test cần GT được skip do overlay chưa có.
- Chờ overlay GT của giảng viên để tính Recall@B, Precision@B và bảng baseline/PoC.
- Tôi có thể tự hoàn tất mẫu solo blind audit 20 ảnh eval chưa xem ở queue đầu; phải ghi rõ một người đánh giá, không thay thế reviewer thứ hai hay GT của giảng viên.
- Không tuyên bố tuân thủ pháp lý/privacy từ PoC.

**Câu debate:** “Khi ảnh tối nhưng còn nhận ra vật thể và màu, có nên recapture?” Trả lời theo scope đã chốt: giữ nếu mục tiêu chỉ nhận diện thô; nếu cần biển số/chi tiết thì phải đổi tiêu chí trước khi review.

## Checklist minh chứng trước khi trình bày
- [ ] Ảnh terminal chạy baseline và PoC.
- [ ] Contact sheet và review CSV.
- [ ] Audit log cùng decision JSON.
- [ ] Run info/commit SHA và kết quả clone sạch.
- [ ] Bổ sung metric chính thức sau khi có GT; không điền số ước lượng vào bảng metric.
