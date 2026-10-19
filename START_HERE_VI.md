# Chạy CaseLens 2.3 và đưa lên GitHub

## Chạy trên Windows

1. Giải nén toàn bộ bản mới vào thư mục riêng; đóng server cũ bằng Ctrl+C.
2. Máy cần Python 3.11 trở lên. Nhấp `start_windows.bat`.
3. Mở http://127.0.0.1:8000 và kiểm tra /api/config hiện version 2.3.0.
4. Sample replay chạy không cần key. Để dùng AI thật, chọn **API settings**,
   chọn provider/model, nhập key riêng trên máy, bấm **Use my key**.
5. Chọn Live AI, chạy Atlas hoặc Cedar. Không gửi key vào chat.

Key khách được dùng cho điều tra/hỏi đáp/review. Chỉ giữ trong bộ nhớ tab,
qua server app rồi gửi provider; không nằm trong case export. Clear my key
hoặc tải lại trang sẽ xóa. HTTPS bắt buộc cho host công khai.

Nếu dùng key server: sao chép `.env.example` thành `.env` (không phải .env.txt),
điền key và để ALLOW_SERVER_AI=true. Nếu không muốn dùng key của bạn làm
fallback: ALLOW_SERVER_AI=false. Khởi động lại sau khi sửa file. Biến môi
trường hệ thống được ưu tiên hơn .env. Các key từng dán vào chat cần thu hồi.

Nếu cổng 8000 bận, sửa PORT=8001 trong .env rồi mở địa chỉ tương ứng.

## Kiểm tra trước khi nộp

- Atlas: delivery overdue cùng condition not_met; không kết luận tự động vi phạm.
- Beacon: overdue dựa trên dữ liệu vẫn thiếu sau hạn, không căn cứ ticket Done.
- Cedar: chưa có receipt vẫn not_verified; thêm email → fulfilled → Versions.
- Các báo cáo cũ khôi phục vẫn được giữ; các trường điều kiện chưa có sẽ ghi
  chưa đánh giá, không tự tạo sự thật. Chạy Live AI lại để có đánh giá mới.
- Nguồn có thể chứng minh trích dẫn tồn tại, chưa chắc diễn giải đúng.

## Đưa lên GitHub

Tạo repo PUBLIC tên `caselens-investigator`, chưa tạo README trên GitHub.
Mở Terminal trong thư mục chứa server.py và README.md:

```bash
git init
git add .
git status
```

Kiểm tra danh sách không có `.env`, key, node_modules hay artifacts. Sau đó:

```bash
git commit -m "Build CaseLens evidence-first investigator"
git branch -M main
git remote add origin https://github.com/TEN_CUA_BAN/caselens-investigator.git
git push -u origin main
```

Thay TEN_CUA_BAN bằng username. Nếu đã có repo/remote thì dùng repo đó,
không chạy lại bước thêm remote. Đăng nhập GitHub khi Git yêu cầu.
Chỉ đưa nội dung thư mục dự án lên repo; không tải ZIP hay các bản cũ vào repo.

Tiếp tục theo [DEPLOY_VI.md](docs/DEPLOY_VI.md), rồi [SUBMISSION.md](docs/SUBMISSION.md).
