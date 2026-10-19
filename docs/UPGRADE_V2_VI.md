# CaseLens 2.0 — Những gì đã bổ sung

Mục tiêu của bản nâng cấp là giúp giám khảo kiểm tra được một quá trình điều tra:
nguồn nào tạo ra kết luận, kết luận thay đổi vì sao, chỗ nào chưa đủ căn cứ và
người phụ trách cần xác minh điều gì. Không bảo đảm thứ hạng hoặc điểm số.

## 1. So với bản 1.0

| Phần | Bản 1.0 | Bản 2.0 |
| --- | --- | --- |
| Kiểm chứng | Kiểm tra mã nguồn và câu trích | Thêm một lượt AI đánh giá ý nghĩa từng claim |
| Bằng chứng | Mở từng trích dẫn | Ma trận claim–source, nguồn chưa được trích, văn bản lặp |
| Thay đổi dữ liệu | Một email đính chính mẫu | Thêm nguồn tùy ý và bật/tắt từng nguồn khỏi phạm vi |
| Lịch sử | Tóm tắt trước/sau đơn giản | Tối đa 10 snapshot mỗi dự án, so sánh nguồn và cam kết |
| Chuyển case | Reset báo cáo | Giữ dữ liệu và báo cáo trong tab đang mở |
| Nhập dữ liệu | JSON | JSON, CSV, email EML dạng text/plain |
| Lưu hồ sơ | Export Markdown | File hồ sơ JSON có nguồn, phiên bản, nhận xét; có khôi phục |
| Bản bàn giao | Markdown | Thêm HTML in được, chứa cả bằng chứng gốc và phần review |
| Người kiểm duyệt | Chưa có | Accepted / Needs follow-up / Disputed và ghi chú riêng |
| Demo | Tự tìm chức năng | Hướng dẫn 3 phút dành cho giám khảo ngay trong giao diện |
| Đánh giá | Bốn trạng thái mẫu | Thêm bộ live stress về injection, trùng nguồn, timezone và thứ tự |

## 2. Luồng gây ấn tượng nên dùng

1. Mở **The missing receipt** và chạy điều tra.
2. Cho thấy ứng dụng trả lời chưa đủ bằng chứng, không tự kết luận giao trễ.
3. Thêm **correction email**, điều tra lại.
4. Mở **Versions**: trước chưa xác minh, sau có receipt và xác nhận đúng hạn.
5. Mở **Evidence map**: các kết luận mới liên kết với nguồn `CDR-E03`.
6. Bỏ chọn nguồn đó rồi chạy lại: kết luận quay về chưa xác minh.
7. Mở nguồn `CDR-E03` trong Evidence room và bấm Include để đưa nó trở lại.
8. Nếu đã cấu hình API: dùng **Live AI**, sau đó vào **Review** và chạy lượt
   kiểm chứng ý nghĩa. Đọc các điểm partial/unsupported/uncertain nếu có.
9. Ghi nhận xét của bạn, tải **Printable brief** hoặc **Save case file**.

Bước loại nguồn kiểm tra độ phụ thuộc của báo cáo vào dữ liệu được cung cấp;
nó không chứng minh quan hệ nhân quả trong thực tế.

## 3. Hai lớp kiểm chứng có ý nghĩa khác nhau

### Lớp 1: kiểm tra bằng code

- Nguồn có thuộc dự án này không?
- Source ID có tồn tại không?
- Câu trích có đúng nguyên văn trong nguồn không?
- Dữ liệu báo cáo có đúng cấu trúc không?
- Mốc thời gian có timezone không và đã sắp đúng thứ tự chưa?

Lớp này xác minh nguồn gốc trích dẫn, không thể chứng minh diễn giải của AI đúng.

### Lớp 2: semantic review bằng AI

Một API call khác đọc lại báo cáo và các nguồn rồi đánh giá từng claim:

| Kết quả | Ý nghĩa |
| --- | --- |
| supported | Nguồn hỗ trợ nội dung ở mức khẳng định đang dùng |
| partial | Một phần đúng nhưng còn khẳng định chưa được hỗ trợ |
| unsupported | Khẳng định vượt bằng chứng hoặc bị nguồn phản bác |
| uncertain | Chưa thể đánh giá chắc từ nguồn hiện có |

Code yêu cầu đủ mọi claim ID, không cho claim trùng hoặc nguồn lạ. Review cũng
phải có trích dẫn nguyên văn, trừ đánh giá uncertain. Lượt review không tự sửa
báo cáo gốc. Bạn quyết định cần xác minh hoặc chỉnh quy trình thế nào.

`OPENAI_REVIEW_MODEL` có thể cấu hình riêng; để trống thì dùng model phân tích.
Hai lượt của cùng model có thể mắc lỗi giống nhau. Kể cả model khác cũng không
thay thế người kiểm tra nghiệp vụ.

## 4. Cách dùng nhập dữ liệu

### Project JSON

Dùng `examples/custom-project.json`. Nội dung gồm `project` và danh sách
`sources`. Tất cả nguồn phải cùng `project_id`, ID không trùng.

### CSV

Dùng `examples/custom-project.csv`, nhập metadata của dự án với ID `demo-import`.
Header bắt buộc:

```text
id,project_id,kind,author,sent_at,title,body
```

Trường có dấu phẩy hoặc xuống dòng cần đặt trong dấu nháy kép theo chuẩn CSV.
Không bỏ cột hoặc thêm cột không được hỗ trợ. Thời gian cần timezone.

### EML

Dùng `examples/delivery-correction.eml`. Chọn định dạng EML, nhập ID/tên/customer
cho dự án mới. Parser đọc From, Subject, Date và text/plain body. Không mở link,
không tải attachment, không chuyển HTML-only thành văn bản.

Nhập dữ liệu gửi nội dung đến server của ứng dụng để kiểm tra định dạng. Việc
này chưa gọi AI; bấm Live AI mới gửi tiếp nội dung đến nhà cung cấp model.

## 5. Lưu và khôi phục

- **Save case file:** tải JSON gồm nguồn đang có, phạm vi chọn, các snapshot và
  nhận xét thủ công. Có tối đa 10 snapshot gần nhất trong tab.
- **Restore case file:** kiểm tra lại cấu trúc và nguồn trích của từng báo cáo.
- Báo cáo nhập lại được ghi `IMPORTED / ORIGIN UNVERIFIED`. Trường `mode=live`
  trong file không được coi là bằng chứng báo cáo thật sự do AI tạo.
- Nhận xét của người dùng được giữ, nhưng không được coi là phê duyệt có định danh.
- Kết quả AI review cũ không tự được tin cậy khi khôi phục: phải chạy review lại.
- Nếu phục hồi cùng project ID, hồ sơ trong tab được thay bằng bản bạn chọn.
  Hãy lưu hồ sơ đang làm trước nếu cần giữ cả hai.
- Reload trang sẽ mất dữ liệu trong tab chưa được tải xuống. Không có tự động
  lưu vào database, localStorage hay hệ thống khách hàng.

## 6. Xuất tài liệu

- **Export brief:** Markdown, phù hợp repo hoặc bàn giao nhanh.
- **Printable brief:** HTML đầy đủ nguồn gốc, review và nội dung source. Mở file
  bằng trình duyệt, dùng Print → Save as PDF nếu cần gửi bản PDF.
- **Save case file:** dùng để tiếp tục điều tra và giữ lịch sử, không thay bằng
  bản brief vì brief không phải định dạng khôi phục.

## 7. Những phần vẫn cần bạn cấu hình

1. API key và quyền truy cập model.
2. Chạy live evaluation, đọc kết quả và điều chỉnh nếu AI diễn giải sai.
3. Repository public trên tài khoản GitHub của bạn.
4. Host có HTTPS và URL live hoạt động từ trình duyệt mới.
5. Đối chiếu brief đầy đủ trong portal và hoàn tất Submit.

Các bước này chưa được thực hiện chỉ bằng việc tải source. Bản demo authored
không được trình bày như một lượt AI chạy thật.
