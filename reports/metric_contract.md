# Metric contract — T02 cá nhân

Chốt trước khi mở nhãn eval: **2026-11-14 · Nguyễn Anh Tiến**. Đây là contract của thí nghiệm cá nhân; không sửa evaluator chuẩn trong `src/metrics/tracks.py`.

| Mục | Khai báo |
|---|---|
| Track | T02 Raw QC Triage |
| Primary metric | `Defect Recall@B` |
| Hướng tốt | Cao hơn |
| Đơn vị | Một `image_id` |
| Công thức | Số ảnh có `is_defect=1` trong top-B của eval / tổng số ảnh lỗi trong eval |
| Ghép prediction và GT | Ghép chính xác theo `image_id`; mỗi ảnh một score; score giảm dần |
| Candidate pool | 96 ảnh fixture tổng hợp: 56 dev, 40 eval; split theo cảnh gốc |
| Review budget | B = 20 |
| Seed | 42 |
| Eval split | `eval`; không dùng nhãn để chọn threshold/feature |
| Baseline threshold | Percentile 20 của Laplacian sharpness trên dev, không dùng nhãn |
| PoC thresholds | Heuristic score 0.35 (loại nghi lỗi), 0.55 (gợi ý RECAPTURE); giữ cố định, không tối ưu theo eval |
| Lỗi cần theo dõi | Missed defect ngoài top-20; false alarm trong top-20 |
| Slices | False alarm theo `light`; recall trong top-20 theo `defect_type` |
| Bất định | Báo Wilson 95% CI cho recall/precision khi có GT; ghi mẫu số từng slice |
| Overlay GT | Chưa được cung cấp trong checkout học viên; chưa tính metric |

Secondary metrics từ evaluator: `Precision@B`, defect-type accuracy (nếu prediction có `pred_defect_type`) và false alarm top-B theo light. Không tính phần trăm cải thiện khi chưa có cả hai kết quả baseline và PoC. Human review có thể đổi hành động `KEEP/RECAPTURE`, nhưng không thay score xếp hạng dùng để tính Recall@B.
