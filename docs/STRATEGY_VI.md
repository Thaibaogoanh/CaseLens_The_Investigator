# Chiến lược hoàn thiện và trình bày bài thi

## Định vị sản phẩm

**CaseLens giúp Customer Success điều tra một escalation và bảo vệ kết luận
bằng nguồn có thể kiểm tra, đồng thời cập nhật kết luận khi dữ liệu thay đổi.**

Khách hàng mục tiêu của demo là người xử lý escalation, người quản lý Customer
Success và người nhận bàn giao giữa CS/Engineering/Operations. Trong một lần
điều tra, họ cần biết: diễn biến, người chịu trách nhiệm, cam kết, tình trạng hiện
tại và điều chưa rõ. Đầu ra cần đủ ngắn để hành động, nhưng truy ngược được về
nguồn chi tiết khi có tranh luận.

## Tiêu chí chính thức và bằng chứng nên mang ra

Nguồn: https://cybernetics.anduin.tech/agent-in-the-shell

| Tiêu chí | Trọng số | Chức năng nên demo | Bằng chứng nên chuẩn bị |
| --- | ---: | --- | --- |
| Depth of solution | 30% | Cam kết có điều kiện; Done nhưng chưa recovery; thiếu receipt rồi có đính chính | Mở source chứng minh từng phát hiện; so sánh hai snapshot |
| Architecture | 20% | Normalize → analyze → validate → optional review → human decision | Sơ đồ, schema, negative tests, xử lý lỗi provider |
| Product quality | 20% | One-click case, xem nguồn, giữ trạng thái, nhập/export, phục hồi | App live; thử mới hoàn toàn; không cần giám khảo nhập key |
| Challenge complexity | 15% | Mâu thuẫn, event time khác sent time, loại nguồn, nguồn lặp | Stress cases có kỳ vọng và kết quả thật |
| Use of AI | 15% | Phân tích nguồn mới và review claim | Chạy Live AI; câu hỏi chưa lập trình sẵn; chỉ ra giới hạn |

Đây là cách ánh xạ sản phẩm vào rubric, không phải dự đoán điểm ban giám khảo.

## Ba điểm khác biệt nên nhấn mạnh

### 1. Một kết luận có thể kiểm tra được

Chọn một claim cụ thể. Mở đúng nguồn và highlight đúng câu trích. Giải thích rằng
hệ thống không chỉ hiển thị citation hình thức: backend đã kiểm tra source ID và
đoạn text tồn tại. Sau đó chủ động nói giới hạn: trích dẫn đúng vẫn có thể bị
diễn giải sai, nên có lượt review thứ hai và người đánh giá.

### 2. Kết luận thay đổi có lịch sử

Case Cedar cho thấy một năng lực thiết yếu trong vận hành: hệ thống không bám
chặt kết luận cũ. Khi receipt mới tới, nó cập nhật trạng thái nhưng vẫn giữ câu
hỏi ban đầu của khách và snapshot cũ để kiểm tra.

### 3. Có thể kiểm tra phụ thuộc vào nguồn

Loại email đính chính rồi chạy lại. Giám khảo thấy trực tiếp kết luận dựa trên
bằng chứng nào. Nhấn mạnh đây là kiểm tra trên phạm vi dữ liệu, không phải một
thí nghiệm nhân quả thực tế.

## Demo 3 phút để người xem hiểu ngay

| Khoảng thời gian | Việc làm |
| --- | --- |
| 0:00–0:20 | Nêu câu hỏi: “File được giao đúng hạn chưa, và bằng chứng đâu?” |
| 0:20–0:50 | Cedar trước correction: thiếu receipt nên chưa xác minh |
| 0:50–1:25 | Thêm correction, chạy lại, mở citation về 17:22 UTC |
| 1:25–2:00 | Versions: nguồn mới và kết luận trước/sau |
| 2:00–2:30 | Evidence map: bỏ nguồn để kiểm tra phụ thuộc |
| 2:30–3:00 | Review/human note và xuất brief; chỉ ra app/repo live |

Trong demo dài 10 phút, bổ sung Atlas, Beacon, kiến trúc và đánh giá. Nếu model
chậm, giải thích đang chờ phân tích; đừng chạy hiệu ứng “AI đang suy nghĩ” giả
hoặc dùng kết quả mẫu nhưng gọi là live. Có thể chuẩn bị sẵn phiên đã phân tích,
nhưng phải nói khi kết quả lấy từ cache.

## Đo chất lượng thế nào cho thuyết phục

### Độ đúng

Chạy `scripts/evaluate.py --mode live --stress --review` sau khi bật API. Bộ có
tám scenario, gồm bốn trạng thái chính và bốn biến thể khó. Kết quả lưu cả report
để bạn đọc, không chỉ hiện PASS. Canary test chỉ kiểm tra một dạng injection;
không được suy rộng thành miễn nhiễm với mọi prompt injection.

Đọc thủ công tối thiểu các assertion: ai hứa, hạn nào, điều kiện nào, nguồn có
đủ chứng minh hoàn thành không, sự kiện có bị nhầm với giờ gửi không. Đánh dấu
accepted/needs follow-up/disputed và ghi lý do.

### Hiệu quả công việc

Chỉ nói giảm thời gian khi đã đo. Quy trình đo gọn:

1. Nhờ một người không thuộc nhóm đọc một case và viết timeline/commitment.
2. Ghi thời gian họ hoàn thành và các lỗi so với đáp án chuẩn.
3. Với case tương đương, cho họ dùng CaseLens rồi kiểm tra source.
4. Ghi cả thời gian chờ AI lẫn thời gian kiểm duyệt và sửa kết quả.
5. Báo cáo quy mô mẫu, cách chọn case, kết quả thô và giới hạn học trước dữ liệu.

Nếu chỉ có một người hoặc ba case giả lập, trình bày như pilot nhỏ; không tuyên
bố một mức tiết kiệm đại diện cho doanh nghiệp.

### Chi phí và tốc độ

- `elapsed_ms` đo thời gian xử lý phía server của lượt đó.
- Chạy sample nhanh không chứng minh AI thật nhanh.
- Cache phải được ghi rõ, không đưa chung với lượt gọi model mới.
- Kiểm tra chi phí thực tế trong tài khoản API; source hiện chưa tính giá token.
- `AI_DAILY_CALL_LIMIT` giới hạn lượt thử trong một process, không thay thế giới
  hạn billing của nhà cung cấp và reset khi process khởi động lại.

## Hoàn tất theo thứ tự ưu tiên

| Mức | Việc | Tiêu chuẩn hoàn tất |
| --- | --- | --- |
| P0 | Đọc brief portal | Không bỏ yêu cầu đầu vào/đầu ra bắt buộc |
| P0 | API thật | Investigate, Ask và Review chạy được trên host |
| P0 | Live evaluation | Đọc report; xử lý thất bại quan trọng; lưu kết quả thật |
| P0 | Repo public | Source nằm đúng root; không có secret; CI đạt |
| P0 | App live | Trình duyệt mới mở được, có dữ liệu để thử ngay |
| P0 | Submit | Portal xác nhận trạng thái đã nộp |
| P1 | Video ngắn | Ghi lại một luồng live dự phòng |
| P1 | Pilot thời gian | Có phép đo nhỏ và mô tả giới hạn |
| P2 | Connector thật | Chỉ thêm nếu brief bắt buộc hoặc toàn bộ P0 đã xong |

## Các câu hỏi khó nên trả lời thẳng

**“Đây có phải chỉ là chatbot bọc API?”**

AI tạo report có schema, nhưng sản phẩm còn quản lý nguồn, phân biệt mốc sự
kiện, xác minh provenance, giữ snapshot, so sánh và hỗ trợ quyết định kiểm duyệt.
Hãy demo chức năng thực tế thay vì tranh luận về tên gọi.

**“Tại sao không dùng nhiều agent?”**

Một lượt analysis có giới hạn cộng một lượt reviewer tùy chọn dễ kiểm tra và
phù hợp thời gian. Tách nhiều agent chỉ có ý nghĩa khi phân công giúp cải thiện
kết quả đo được. Không khẳng định sản phẩm có multi-agent orchestration.

**“Nếu nguồn sai thì sao?”**

Provenance chứng minh nguồn đã nói gì, không chứng minh nguồn nói đúng. Mâu
thuẫn và unknown cần hiển thị. Người có thẩm quyền vẫn xác minh thực tế.

**“Làm sao chống prompt injection?”**

Nguồn được coi là untrusted data; model không có công cụ hành động; output có
schema, source scope và quote checks. Có stress test nhưng chưa có bằng chứng
miễn nhiễm với mọi tấn công. Semantic prompt injection vẫn là giới hạn cần đo.

**“Có sẵn cho dữ liệu khách hàng thật chưa?”**

Chưa. Bản demo dùng dữ liệu giả lập. Cần SSO, tenant authorization, quản lý quyền
connector, lưu trữ bền vững, audit có danh tính, retention policy và triển khai
server phù hợp trước khi đưa dữ liệu doanh nghiệp vào.

## Điều cần tránh khi thuyết trình

- Gọi sample replay là AI thật hoặc che trạng thái cache.
- Nêu tỷ lệ chính xác, tiết kiệm thời gian hoặc điểm thi chưa đo được.
- Đồng nhất citation coverage với độ đúng.
- Coi review AI hoặc checkbox thủ công là phê duyệt có định danh.
- Trình bày tính năng kế hoạch như đã có trong source.
- Đổi phạm vi sang nhiều connector vào sát hạn mà làm hỏng luồng cốt lõi.
