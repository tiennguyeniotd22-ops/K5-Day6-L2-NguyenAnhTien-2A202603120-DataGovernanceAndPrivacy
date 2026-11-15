# T02 Raw QC Triage — báo cáo cá nhân

## 00 · Thông tin

| Mục | Nội dung |
|---|---|
| Người thực hiện | Nguyễn Anh Tiến |
| Hình thức | Cá nhân; mã cục bộ `IND-T02` (thay nếu giảng viên cấp mã khác) |
| Challenge | T02 — xếp hạng ảnh mờ, lóa, tối hoặc nén lỗi để review |
| Repository | https://github.com/tiennguyeniotd22-ops/K5-Day6-L2-NguyenAnhTien-2A202603120-DataGovernanceAndPrivacy |
| Track / seed | `t02` / `42` |
| Tag demo-180m / final-24h | Chưa tạo; không gắn tag hồi tố cho mốc chưa được ghi nhận |

## 01 · Bài toán và quyết định

Ảnh chất lượng thấp có thể làm hỏng khâu gán nhãn hoặc huấn luyện phía sau. Pipeline xếp hạng ảnh đáng nghi để con người kiểm tra 20 ảnh ưu tiên, sau đó lưu quyết định theo từng ảnh (`KEEP` hoặc `RECAPTURE`) cùng audit log. Quyết định batch hiện tại là `REWORK` vì trong 20 ảnh review vẫn còn ảnh cần chụp lại; đây không phải quyết định phát hành dữ liệu.

Mục tiêu review của cá nhân là nhận diện thô loại vật thể, màu chính và vị trí tương đối. Đọc biển số/chi tiết nhỏ nằm ngoài phạm vi. Quy ước này được ghi riêng trong [`review_guideline_t02.md`](review_guideline_t02.md); phần trăm nhận diện ở đó là ước lượng thủ công, không phải xác suất hoặc metric của mô hình.

## 02 · Dữ liệu và provenance

| Split | Số ảnh | Nguồn | Ghi chú |
|---|---:|---|---|
| Dev | 56 | Fixture tổng hợp trong `fixtures/t02_raw_qc/` | Dùng tính ngưỡng baseline; không đọc nhãn GT |
| Eval | 40 | Fixture tổng hợp trong `fixtures/t02_raw_qc/` | Chỉ chấm bằng evaluator khi có overlay GT của giảng viên |

Tổng cộng 96 ảnh 320×180, chia theo cảnh gốc. Manifest input xác minh thành công; mọi fixture manifest trong repo cũng qua `python -m tools.preflight`. Nguồn ghi trong manifest là `synthetic:tools/make_fixtures.py (seed 42)`, license `CC0-1.0 (synthetic, generated for AI20K Day06)`; không dùng ảnh thật, dữ liệu người dùng hoặc dữ liệu tải về. Ground truth không có trong checkout học viên và pipeline không đọc thư mục `gt/`.

## 03 · Thiết kế

Flow: `images.csv + manifest` → trích xuất đặc trưng → xếp hạng score giảm dần → queue/contact sheet 20 ảnh → review và override → audit log → quyết định batch.

PoC CPU-only trong `src/pipeline.py` tính Laplacian sharpness, độ sáng, tỷ lệ điểm bão hòa, proxy blockiness; score tổng hợp lấy `0.7 × feature rủi ro lớn nhất + 0.3 × trung bình bốn rủi ro`. Loại lỗi chính là feature rủi ro lớn nhất. Mốc score `0.35` và `0.55` trong source là heuristic cố định của PoC; chúng chưa được tối ưu bằng nhãn GT và không được điều chỉnh theo eval. Phân biệt loại lỗi với hành động: ảnh có thể là `blur` nhưng người review vẫn chọn `KEEP` nếu còn dùng được cho mục tiêu thô.

Baseline riêng tại `src/baselines/t02_laplacian.py` dùng một ngưỡng Laplacian toàn ảnh: ngưỡng là percentile 20 của sharpness ở split dev (`n_dev=56`), không dùng nhãn. Score xếp hạng là hàm nghịch biến của sharpness. Cả hai run dùng cùng 96 ảnh, seed 42 và budget 20. Không có model weights hoặc network call.

Tham khảo: [OpenCV Image Filtering — Laplacian operator](https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html) mô tả toán tử đạo hàm bậc hai dùng làm proxy độ nét; [Blur image detection using Laplacian operator and Open-CV (IEEE)](https://ieeexplore.ieee.org/document/7894491/) trình bày việc dùng Laplacian cho phát hiện ảnh mờ. Đây là cơ sở kỹ thuật, không phải chứng minh ngưỡng phù hợp cho mọi camera/ánh sáng.

## 04 · Chạy và kết quả cục bộ

Lệnh PoC:

```powershell
.\.venv\Scripts\python.exe -m src.main --track t02 --input fixtures/t02_raw_qc --config configs/lab.yaml --output out/poc --offline --seed 42 --run-name poc
```

Lệnh baseline:

```powershell
.\.venv\Scripts\python.exe -m src.main --track t02 --pipeline src.baselines.t02_laplacian --input fixtures/t02_raw_qc --config configs/lab.yaml --output out/baseline --offline --seed 42 --run-name baseline
```

| Run | Kết quả kỹ thuật | Kết quả review / quyết định |
|---|---|---|
| Baseline Laplacian | exit 0; 96 ảnh; ngưỡng dev `186.9666`; runtime `3.625 s` trong một lần chạy | queue 20; `HOLD / BASELINE_ONLY` |
| PoC đa đặc trưng | exit 0; 96 ảnh; 24 ảnh bị đánh dấu nghi ngờ; runtime `2.7424 s` trong một lần chạy | review đủ 20/20; 17 approve, 3 edit thành `KEEP`; còn 17 ảnh `RECAPTURE`, nên `REWORK / RECAPTURE_REQUIRED` |

### So sánh vận hành trên clone sạch

Đây là so sánh đầu ra và thời gian chạy của đúng một lần chạy trên cùng máy, không phải metric chất lượng phát hiện lỗi:

| Chỉ số vận hành | Baseline Laplacian | PoC đa đặc trưng |
|---|---:|---:|
| Ảnh đầu vào / ngân sách review | 96 / 20 | 96 / 20 |
| Số ảnh trong top-20 | 20 | 20 |
| Thời gian chạy clone sạch | 0.9754 s | 2.0317 s |
| Quyết định batch | `HOLD / BASELINE_ONLY` | `REWORK / RECAPTURE_REQUIRED` |

Hai queue top-20 có 16 ảnh trùng nhau (80%); mỗi pipeline có 4 ảnh riêng. Thời gian chỉ là một lần đo nên không dùng để kết luận pipeline nào nhanh hơn nói chung. Chưa có overlay GT nên chưa thể kết luận pipeline nào phát hiện lỗi tốt hơn; Recall@B/Precision@B vẫn chờ nhãn chuẩn.

Đây là thời gian của một lần chạy trên Windows, Python 3.11.5 và CPU; không phải benchmark trung bình. Review queue PoC có 10 ảnh dev và 10 ảnh eval. Người review đã xem những ảnh eval này, nhưng không sửa score, không dùng nhãn GT và không thay ngưỡng dựa trên eval; cần khai báo việc đã xem ảnh khi nộp để giữ minh bạch.

Đã clone lại commit `fa71e62` vào thư mục tạm, tạo virtual environment mới, cài `requirements.txt`, chạy preflight/tests và chạy lại cả hai pipeline. Preflight: 0 lỗi; pytest: exit 0, chỉ skip các test cần GT. Hai file ranking khớp byte với lần chạy trước; hash và run metadata ở [`evidence/fresh_clone/reproduction.md`](evidence/fresh_clone/reproduction.md).

Ba quyết định `edit` là các trường hợp reviewer cho rằng ảnh còn dùng được cho mục tiêu nhận diện thô. Chúng là ví dụ pipeline có thể đề nghị chụp lại quá mức; ghi chú reviewer là bằng chứng định tính, không phải nhãn ground truth. Bản export review có trong [`t02_review_evidence.csv`](t02_review_evidence.csv); audit JSONL, decision, run-info và prediction CSV của clone sạch được lưu trong [`evidence/fresh_clone/`](evidence/fresh_clone/). Contact sheet offline tự chứa: [`evidence/t02_contact_sheet.html`](evidence/t02_contact_sheet.html).

## 05 · Metric và giới hạn kết luận

Metric chính thức là **Defect Recall@B**, với `B=20`: số ảnh lỗi GT trong top-20 của split eval chia cho tổng ảnh lỗi GT trong eval. Kèm theo là Precision@B; báo cáo thêm false alarm theo `light` và recall theo `defect_type`. Contract đã điền tại [`metric_contract.md`](metric_contract.md).

Không thể báo Recall@B, Precision@B, defect-type accuracy hoặc so sánh baseline/PoC vì thư mục GT của giảng viên chưa có trong repo. Không thay thế metric bằng số quyết định `KEEP/RECAPTURE`, không đoán nhãn và không tạo file metrics giả. Khi giảng viên cung cấp overlay GT, chạy:

```powershell
.\.venv\Scripts\python.exe -m src.evaluate --track t02 --pred out/baseline/ranked_review.csv --run-name baseline --out reports/metrics_baseline.json
.\.venv\Scripts\python.exe -m src.evaluate --track t02 --pred out/poc/ranked_review.csv --run-name poc --out reports/metrics_poc.json
.\.venv\Scripts\python.exe -m src.compare reports/metrics_baseline.json reports/metrics_poc.json --out reports/table1_baseline_vs_poc.md
```

Sau đó bổ sung ít nhất hai slice theo `light`/`defect_type`, failure case có đối chiếu GT, và độ bất định cho N nhỏ. Không tune lại theo eval.

## 06 · Review, audit và privacy

Queue là top-20 theo score, tie-break bằng `image_id`. Human override chỉ đổi `pred_action`; score dùng evaluator không bị sửa. `audit_log.jsonl` lưu actor, hành động, ảnh, lý do và thời gian. Người sở hữu run là Nguyễn Anh Tiến. Batch `REWORK` không có nghĩa tự động xóa hoặc thay ảnh nguồn.

Dữ liệu hiện tại là fixture tổng hợp. Không kết luận tuân thủ pháp luật hoặc chính sách riêng tư từ pipeline này. Trước khi dùng ảnh thực cần kiểm tra quyền sử dụng, PII, mục đích xử lý, thời hạn lưu và người có quyền truy cập.

## 07 · Kiểm tra và phần cần hoàn tất

- `.\.venv\Scripts\python.exe -m tools.preflight`: 0 lỗi; 2 cảnh báo chỉ về gói ảnh thật/model tùy chọn không cần cho T02.
- `.\.venv\Scripts\python.exe -m pytest -q`: exit 0, 0 failed; các test yêu cầu overlay GT được skip vì overlay chưa có.
- Clone sạch với Python 3.11.5 và virtual environment mới cũng preflight 0 lỗi, pytest exit 0; ranking baseline/PoC khớp byte với lần chạy trước. Log đầy đủ ở [`evidence/fresh_clone/reproduction.md`](evidence/fresh_clone/reproduction.md).
- Còn chờ để hoàn tất đánh giá chính thức: overlay GT của giảng viên; sau đó chạy evaluate/compare và bổ sung metric + failure case đã đối chiếu nhãn.
- Còn chờ review thủ công: mẫu 20 ảnh eval và hướng dẫn solo blind audit tiếng Việt có tại [`evidence/t02_independent_review_template.csv`](evidence/t02_independent_review_template.csv), [`evidence/t02_independent_review_instructions.md`](evidence/t02_independent_review_instructions.md) và [báo cáo tự kiểm tra mù T02](t02_solo_blind_audit_report.md). Mẫu hiện còn trống; chưa có thống kê solo audit.
- Showcase có contact sheet và dàn ý 5 slide tại [`evidence/showcase_t02.md`](evidence/showcase_t02.md); cần người học trình bày trực tiếp hoặc chuyển dàn ý thành slide.
- Mã cá nhân trong report là mã cục bộ. Nếu lớp yêu cầu mã nhóm chính thức hoặc tag mốc, thay/cấp từ giảng viên; không tự suy đoán.
