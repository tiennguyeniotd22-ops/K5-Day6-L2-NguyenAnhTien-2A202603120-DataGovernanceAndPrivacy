# T02 Human Review Guideline — quy ước bổ sung của nhóm

**Phiên bản:** 1
**Phạm vi:** Review ảnh cho mục tiêu nhận diện loại vật thể chính, màu sắc và vị trí tương đối. Đọc biển số hoặc phân biệt chi tiết nhỏ không thuộc mục tiêu hiện tại của nhóm.

> Đây là quy ước do nhóm bổ sung sau lượt review đầu tiên, không phải ngưỡng chính thức trong đề T02. Đề chỉ nêu `defect_type`, `severity 0–2` và `is_defect`; không quy định phần trăm nhận diện hay cách hiểu cụ thể của từng mức severity.

## 1. Phân biệt loại lỗi và hành động

- `defect_type` mô tả **lỗi nhìn thấy được**: `blur`, `dark`, `glare`, `compression` hoặc `none`.
- `pred_action` mô tả **việc nên làm**: `KEEP` hoặc `RECAPTURE`.
- Ảnh có thể bị mờ hoặc tối nhưng vẫn được `KEEP` nếu còn dùng được cho mục tiêu nhận diện thô. Không đổi loại lỗi thành `none` chỉ vì quyết định giữ ảnh.
- Nếu có nhiều lỗi, chọn lỗi chính làm `pred_defect_type`; ghi lỗi phụ trong `review_note`.

## 2. Quy tắc KEEP / RECAPTURE

### KEEP

Chọn `KEEP` khi reviewer có thể xác định loại vật thể chính, màu chủ đạo và vị trí tương đối mà không phải đoán. Mờ hoặc tối nhẹ không tự động buộc phải chụp lại.

### RECAPTURE

Chọn `RECAPTURE` khi vật thể chính chỉ còn đoán được, không phân biệt chắc loại hoặc màu, hoặc hình dạng/vị trí không đủ tin cậy cho mục tiêu nhận diện của nhóm.

### Escalate

Nếu reviewer không thống nhất hoặc không chắc ảnh còn dùng được hay không, chọn `escalate`. Không dùng `approve` để thay cho việc ghi rõ sự không chắc chắn.

## 3. Ước lượng mức nhận diện nội bộ

Phần trăm dưới đây là **ước lượng của reviewer về khả năng nhận diện thô**, không phải tỷ lệ pixel nhìn thấy, xác suất của mô hình hay metric chính thức.

Chấm bốn tiêu chí, mỗi tiêu chí: rõ = `1`, một phần = `0.5`, không nhận ra = `0`:

1. Loại vật thể chính.
2. Màu chủ đạo.
3. Vị trí tương đối trong ảnh.
4. Hình dạng/đường biên đủ dùng cho nhận diện thô.

`recognizability_pct = tổng điểm / 4 × 100`

- `80–100%`: có thể `KEEP` cho mục tiêu nhận diện thô.
- `60–79%`: cần reviewer thứ hai hoặc `escalate`.
- `<60%`: `RECAPTURE`.

Nếu về sau bài toán yêu cầu đọc biển số, biển báo hoặc chi tiết nhỏ, mục tiêu đã thay đổi: bổ sung tiêu chí đó trước khi review và không áp dụng ngưỡng KEEP ở trên cho ảnh không đọc được chi tiết bắt buộc.

## 4. Mức severity nội bộ

Đề T02 không định nghĩa ý nghĩa cụ thể của `severity 0–2`. Nếu nhóm cần ghi severity trong ghi chú, dùng quy ước nội bộ sau và ghi rõ đây không phải định nghĩa của giảng viên:

- `0`: không thấy lỗi ảnh hưởng chất lượng.
- `1`: có lỗi nhưng vật thể chính/màu sắc vẫn nhận diện được; có thể KEEP.
- `2`: lỗi khiến vật thể chính chỉ còn đoán được hoặc không dùng được; RECAPTURE.

## 5. Cách ghi review

Trong contact sheet hiện tại, `edit` hoặc `reject` cần `override_value` chính xác là `KEEP` hoặc `RECAPTURE` (chữ hoa). Ghi phần trăm và lý do vào `review_note`, ví dụ:

```text
defect=blur; secondary=dark; recognizability_pct=87.5; target=coarse object/color; plate=out of scope; action=KEEP
```

Pipeline hiện chỉ áp dụng override cho hành động `KEEP/RECAPTURE`; nội dung phần trăm trong `review_note` phục vụ audit/báo cáo, không được evaluator dùng để chấm.

## 6. Lượt review đầu tiên

Lượt đầu đã có 20 quyết định: 17 `approve` và 3 `edit` thành `KEEP`. Ghi chú của ba ảnh edit cho biết reviewer vẫn nhận ra vật thể/màu sắc; một ghi chú nói biển số không đọc rõ. File export không ghi phần trăm nhận diện, vì vậy không gán hồi tố phần trăm chính xác cho các ảnh này.

Từ đây, áp dụng cùng một quy tắc cho các lượt review tiếp theo. Không điều chỉnh score/threshold dựa trên nhãn hoặc kết quả của split `eval`; các ngưỡng mô hình phải được chốt trên `dev`.
