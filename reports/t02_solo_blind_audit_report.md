# Báo cáo tự kiểm tra mù T02

## Thông tin

| Mục | Nội dung |
|---|---|
| Học viên | Nguyễn Anh Tiến |
| MSSV | `2A202603120` |
| Học phần | K5 – Day 6 – L2: Data Governance and Privacy |
| Track | T02 – Raw QC Triage |
| Repository | [K5-Day6-L2-NguyenAnhTien-2A202603120-DataGovernanceAndPrivacy](https://github.com/tiennguyeniotd22-ops/K5-Day6-L2-NguyenAnhTien-2A202603120-DataGovernanceAndPrivacy) |
| Mẫu gán nhãn | [`evidence/t02_independent_review_template.csv`](evidence/t02_independent_review_template.csv) |
| Hướng dẫn | [`review_guideline_t02.md`](review_guideline_t02.md), [`evidence/t02_independent_review_instructions.md`](evidence/t02_independent_review_instructions.md) |
| Tệp kết quả dự kiến | `reports/evidence/t02_solo_blind_audit.csv` |
| Trạng thái | **Chưa hoàn tất gán nhãn; chưa có thống kê kết quả solo audit.** |

## 1. Mục đích và giới hạn

Báo cáo mô tả lần kiểm tra thủ công mù dự kiến cho pipeline T02. Người đánh giá sẽ xem ảnh mà không xem điểm, thứ hạng hay hành động gợi ý của pipeline trong lúc gán nhãn.

Đây là bài cá nhân nên cùng một học viên thực hiện lần kiểm tra thứ hai. Hãy gọi đây là **solo blind audit** (tự kiểm tra mù một người), không gọi là đánh giá độc lập giữa hai người. Kết quả không phải nhãn chuẩn ẩn (**ground truth**, GT) của giảng viên và không đo được mức đồng thuận giữa nhiều người gán nhãn.

## 2. Mẫu và quy trình

Mẫu CSV có 20 `image_id` duy nhất, tất cả thuộc split `eval`. Đối chiếu với queue review lần đầu cho thấy không có ảnh trùng. Tuy nhiên, hiện tại cả 20 dòng vẫn để trống nhãn; tệp kết quả `t02_solo_blind_audit.csv` chưa được tạo. Vì vậy các số liệu audit ở những mục sau chưa thể tính.

Khi gán nhãn, mở ảnh theo đường dẫn trong `fixtures/t02_raw_qc/` và chỉ xem ảnh đó. Không xem `score`, `rank`, hành động gợi ý hoặc kết quả review đầu tiên cho đến khi lưu xong toàn bộ nhãn. Không dùng mẫu này để điều chỉnh threshold trên split `eval`.

Các trường cần ghi trong CSV:

- `defect_type`: dùng đúng một trong các nhãn của đề: `none`, `blur`, `glare`, `dark`, `compression`. Nếu có lỗi phụ, ghi trong `review_note`.
- `is_defect`: ghi có/không có lỗi theo định nghĩa bài lab.
- `severity`: đề có trường `0–2` nhưng không nêu rõ ý nghĩa từng mức. Chỉ điền nếu rubric của giảng viên quy định; nếu không, để trống.
- `recognizability_pct`: ước lượng nội bộ theo guideline, không phải xác suất của mô hình. Guideline chấm bốn tiêu chí — loại vật thể, màu chính, vị trí tương đối, hình dạng/đường biên — mỗi tiêu chí `1`, `0.5` hoặc `0`, rồi tính tổng chia 4 nhân 100.
- `reviewer_action`: `KEEP` nếu ảnh dùng được cho mục tiêu nhận diện thô; `RECAPTURE` nếu không đủ tin cậy. Nếu trường hợp chưa rõ và cần xem xét thêm, ghi `escalate` cùng lý do thay vì tự đoán.
- `confidence_1_to_5` và `review_note`: lần lượt ghi độ tự tin từ 1 đến 5 và lý do quan sát được trên ảnh.

## 3. Kết quả solo audit

**Chưa có kết quả để tổng hợp.** Không điền các ví dụ số như “8 ảnh lỗi”, “13 KEEP”, hay tỷ lệ nhận diện trung bình nếu chưa được tính từ CSV đã hoàn tất.

| Chỉ số cần báo cáo | Kết quả hiện tại |
|---|---|
| Số dòng mẫu | 20 |
| Số dòng đã gán nhãn | 0/20 — mẫu hiện còn trống |
| Số ảnh `is_defect=True/False` | Chưa tính |
| Phân bố `defect_type` | Chưa tính |
| Số hành động `KEEP/RECAPTURE/escalate` | Chưa tính |
| Trung bình, nhỏ nhất, lớn nhất của `recognizability_pct` | Chưa tính |
| Trung bình `confidence_1_to_5` | Chưa tính |
| Ví dụ điển hình từ mẫu solo audit | Chưa có; cần ghi sau khi xem và gán nhãn |

## 4. Bằng chứng review vòng đầu — tách biệt với solo audit

Để cung cấp bối cảnh đã xác minh, queue PoC vòng đầu có 20 ảnh: 17 quyết định `approve` và 3 quyết định `edit` với override `KEEP`. Ba ảnh được giữ lại đều có lý do reviewer ghi nhận rằng vẫn nhận ra vật thể và màu sắc. Đây là bằng chứng định tính của vòng đầu, **không phải kết quả của mẫu solo audit 20 ảnh ở trên** và không có phần trăm nhận diện được ghi lại.

| Ảnh | Lỗi pipeline ghi nhận | Quyết định vòng đầu | Ghi chú reviewer |
|---|---|---|---|
| `img_19_3` | `blur` | `KEEP` | Vẫn nhận ra vật thể và màu sắc. |
| `img_16_2` | `blur` | `KEEP` | Vẫn nhận ra vật thể và màu sắc; đề nghị có guideline thống nhất. |
| `img_14_2` | `blur` | `KEEP` | Vẫn nhận ra vật thể và màu sắc; biển số không rõ nhưng nằm ngoài phạm vi nhận diện thô đã chọn. |

Sau review vòng đầu, còn 17 ảnh `RECAPTURE`; quyết định batch là `REWORK / RECAPTURE_REQUIRED`. Chi tiết từng dòng nằm trong [`t02_review_evidence.csv`](t02_review_evidence.csv) và audit log của PoC ở [`evidence/fresh_clone/poc/audit_log.jsonl`](evidence/fresh_clone/poc/audit_log.jsonl).

## 5. Pipeline, baseline và khả năng tái lập

Thí nghiệm dùng 96 ảnh fixture tổng hợp, 56 ảnh `dev`, 40 ảnh `eval`, seed 42 và ngân sách review `B=20`. Baseline dùng ngưỡng Laplacian lấy từ split `dev`; PoC kết hợp các tín hiệu blur, glare, dark và compression. Kết quả chạy lại trên clone sạch:

| Run | Kết quả đã ghi nhận |
|---|---|
| Baseline Laplacian | Exit 0; ngưỡng dev `186.9665985107422`; queue 20; batch `HOLD / BASELINE_ONLY` |
| PoC T02 | Exit 0; 24 ảnh nghi ngờ; review 20/20; batch `REWORK / RECAPTURE_REQUIRED` |
| So sánh queue | Hai top-20 có 16 ảnh trùng nhau; mỗi pipeline có 4 ảnh riêng. Đây là mức trùng queue, không phải metric chất lượng. |
| Clone sạch | Preflight 0 lỗi; pytest exit 0; các kiểm tra cần GT được skip vì chưa có overlay GT của giảng viên. Ranking CSV khớp byte với lần chạy trước. |

Log, cấu hình, đầu ra và hash của lần tái lập được lưu trong [`evidence/fresh_clone/reproduction.md`](evidence/fresh_clone/reproduction.md). Không dùng thời gian của một lần chạy để kết luận hiệu năng tổng quát.

## 6. Metric chính thức và quyền riêng tư

Metric chính của T02 là **Defect Recall@B** với `B=20`, kèm **Precision@B** và các slice đã khai báo trong [`metric_contract.md`](metric_contract.md). Chưa có overlay GT của giảng viên nên chưa tính các metric này, chưa thể kết luận baseline hay PoC phát hiện lỗi tốt hơn, và không được thay metric bằng số lượng `KEEP/RECAPTURE`.

Fixtures trong repo là dữ liệu tổng hợp; báo cáo này không kết luận pipeline tuân thủ luật hoặc chính sách riêng tư. Nếu chuyển sang ảnh thật, cần xác minh quyền sử dụng, dữ liệu cá nhân, mục đích và thời hạn lưu trước khi đưa ảnh lên repo.

## 7. Việc cần hoàn tất

1. Điền đủ 20 dòng trong mẫu theo hướng dẫn tiếng Việt; giữ nguyên tên cột. Lưu thành `reports/evidence/t02_solo_blind_audit.csv` và không ghi nhãn đoán.
2. Sau khi có CSV đã điền, cập nhật các thống kê ở mục 3 và thêm ví dụ thực tế từ chính 20 ảnh đó. Các ví dụ placeholder trong bản nháp ban đầu đã được loại bỏ.
3. Chỉ tính Recall@B/Precision@B và so sánh chất lượng sau khi giảng viên cung cấp GT.
4. Showcase hiện có dàn ý 5 slide tại [`evidence/showcase_t02.md`](evidence/showcase_t02.md); cần hoàn thiện phần trình bày/minh chứng demo theo yêu cầu lớp.
