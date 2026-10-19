# Triển khai CaseLens lên Render

Đề xuất: **Render Docker Web Service**, vì app đang có server Python và
Dockerfile, không cần DB hoặc build frontend. Không chọn Static Site hay chỉ
GitHub Pages: các API backend sẽ không chạy.

Render Free phù hợp chạy thử nhưng ngủ sau 15 phút không có truy cập và có
thời gian khởi động lại. Với bài dự thi, chọn instance không miễn phí nếu
ngân sách cho phép, xem giá hiện tại trên dashboard trước khi xác nhận.
Không có tài khoản hosting được cấu hình trong gói này; chưa triển khai thay bạn.

## Cách dễ nhất: tạo Web Service

1. Đẩy source lên GitHub public theo START_HERE_VI.md.
2. Đăng nhập https://dashboard.render.com bằng tài khoản của bạn.
3. New → Web Service → kết nối repo caselens-investigator.
4. Chọn branch main, runtime **Docker**; Dockerfile ở repo root.
5. Chọn region gần người dùng trong các region dashboard cung cấp.
6. Chọn instance plan: Free để thử, hoặc non-Free để giảm nguy cơ chờ khởi động
   khi giám khảo mở link. Kiểm tra chi phí trước Create Web Service.
7. Thêm biến môi trường:

| Tên | Giá trị |
| --- | --- |
| HOST | 0.0.0.0 |
| AI_PROVIDER | gemini |
| GEMINI_MODEL | gemini-3.8-flash, hoặc model project bạn có quyền/quota |
| ALLOW_SERVER_AI | false nếu yêu cầu khách tự nhập key; true nếu bạn cấp key demo |
| AI_DAILY_CALL_LIMIT | 50, điều chỉnh theo quota thực tế |

Render cung cấp PORT; không cần ép cổng 8000. Health Check Path: `/health`.
Nếu dùng key demo, thêm GEMINI_API_KEY vào Environment secret; không commit.
Người dùng vẫn có thể override bằng key riêng. Nếu ALLOW_SERVER_AI=false,
giám khảo cần key có quota để dùng Live AI; ghi rõ điều này trong bài nộp.
Để demo ít thao tác, một key server dành riêng có quota thường thuận tiện hơn,
nhưng bạn chịu chi phí và cần đặt kiểm soát tại provider.

8. Create Web Service và đợi build/deploy thành công.
9. Sao chép URL thực tế, ví dụ https://caselens-investigator-xxxx.onrender.com.
10. Thêm PUBLIC_ORIGIN đúng URL HTTPS đó, không thêm đường dẫn; lưu/redeploy.

Không nhập secret vào build command, Dockerfile, README hoặc source.

## Cách khác: Blueprint

Repo có render.yaml. Chọn New → Blueprint → repo → xem lại cấu hình và plan
trước khi tạo. Mặc định là Free và ALLOW_SERVER_AI=false; không tự cấp key.
Sau khi có URL, thêm PUBLIC_ORIGIN trong dashboard. Không cần làm cả hai cách.

## Xác minh trên URL công khai

Mở cửa sổ ẩn danh:

- `/health` trả status ok.
- `/api/config` trả version 2.3.0, không chứa secret.
- Giao diện tải đầy đủ, API settings mở được.
- Sample Cedar → correction → Versions hoạt động.
- Nhập key riêng hoặc dùng key server, chạy một Live AI; kiểm tra dẫn chứng.
- Thử Ask/Review một lần nếu quota cho phép; không bấm liên tục.
- Save case file, Restore, Printable brief hoạt động.
- Kiểm tra điện thoại hoặc DevTools 390px; nút API settings không bị che.
- Mở URL repo không đăng nhập vẫn thấy full source.

Có thể kiểm tra từ máy bằng:

```bash
python scripts/preflight.py --url https://URL_THAT --repo https://github.com/USER/REPO
```

Preflight không chứng nhận chất lượng AI, không nộp portal và không tạo hosting.

## Khắc phục

- Deploy fail: gửi phần build log không chứa secret; xác nhận Dockerfile ở root.
- POST bị chặn Origin: PUBLIC_ORIGIN phải khớp chính xác HTTPS URL đang mở.
- AI timeout: kiểm tra mạng outbound, quota/model; thử Cedar ít nguồn.
- HTTP 429: phân biệt giới hạn app với provider; key mới không tạo thêm quota.
- Server key không dùng: kiểm tra ALLOW_SERVER_AI và key/provider cùng prefix.
- Mất dữ liệu sau reload: đúng thiết kế; Save case file trước khi tải lại.

## Nguồn chính thức

- https://render.com/docs/web-services
- https://render.com/docs/docker
- https://render.com/docs/free
- https://render.com/docs/blueprint-spec
- https://render.com/pricing

Đối chiếu 19 October 2026. Gói và UI có thể thay đổi; giá trên dashboard là
thông tin cần xem trước khi mua.
