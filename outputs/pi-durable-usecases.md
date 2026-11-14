# Tổng hợp use case Pi Durable trong wiki

**Pi Durable là agent harness, không phải một ứng dụng cụ thể.** Các use case trong wiki xoay quanh việc lưu trạng thái và checkpoint để công việc có thể tiếp tục sau gián đoạn. Nó có thể chạy ở local hoặc cloud; *nơi chạy* và *khả năng phục hồi* là hai lựa chọn khác nhau. Các mô tả hành vi dưới đây phần lớn là **theo tài liệu dự án**, chưa được kiểm chứng độc lập trong wiki. Xem [Pi Durable Overview](wiki/pi-durable-overview.md) và [Home, Cloud, and Durable Agents](wiki/agent-execution-models-home-cloud-durable.md).

## 1. Điều tra và xử lý sự cố có human approval

**Use case:** Theo dõi log, phát hiện incident, giao agent điều tra và chuẩn bị bản sửa, sau đó chờ người duyệt trước khi deploy.

Wiki có một **demo mô phỏng** của Durable Pi:

1. Classifier đánh giá từng dòng log; code thông thường áp dụng ngưỡng để mở incident.
2. Agent điều tra trên branch riêng; tool kiểm tra test trước khi chấp nhận bản sửa.
3. Deploy chạy qua các phase approval, rollout và verification; tài liệu báo cáo rằng trạng thái chờ duyệt có thể được giữ qua restart.

Đây là ví dụ cụ thể nhất về kết hợp agent, deterministic code và checkpoint trong wiki, nhưng **không chứng minh quy trình đã an toàn cho production**. Nguồn: [Durable Pi Proactive Incident Demo](wiki/durable-pi-proactive-demo.md).

## 2. Job dài hoặc workflow phải chờ nhiều bước

**Use case:** Backfill dữ liệu, migration, release hoặc một quy trình phải dừng để đợi quyết định rồi tiếp tục.

Ví dụ được nêu trong wiki là backfill nhiều triệu dòng theo batch, sau đó deploy và chờ approval. Ý tưởng là lưu tiến độ để khi process chết, host mới có thể tiếp tục từ checkpoint thay vì chỉ dựa vào transcript.

**Lưu ý:** Đây là **kịch bản minh họa**, không phải benchmark hay triển khai đã được kiểm thử trong wiki. Batch và deploy vẫn cần được thiết kế để xử lý việc chạy lại an toàn. Nguồn: [Home, Cloud, and Durable Agents](wiki/agent-execution-models-home-cloud-durable.md), [Pi Durable Tasks](wiki/pi-durable-tasks.md).

## 3. Lập lịch và phản ứng với sự kiện

**Use case:** Đánh thức agent theo giờ, theo dõi repository/PR hoặc đưa event bên ngoài vào một conversation.

- **Pi Pocket:** tài liệu mô tả scheduled messages và PR/repository watches dưới dạng durable tasks. Message đã quá hạn trong downtime được gửi khi khởi động lại; lịch lặp bỏ qua một lượt nếu message trước vẫn đang chờ. [Pi Pocket Linked Sessions and Durable Automation](wiki/pi-pocket-orchestration.md)
- **Cloudflare demo:** một tool tạo task ngủ đến deadline; Durable Object dùng alarm để đánh thức và khôi phục công việc. [Pi Durable on Cloudflare](wiki/pi-durable-on-cloudflare.md)
- **Pi Orbs:** scheduled message dùng job bên ngoài để POST vào webhook của bot; MCP event là một đường tích hợp riêng. Không nên mặc định hai cơ chế này có cùng delivery semantics như task scheduler của Pi Pocket. [Pi Orbs Integrations](wiki/pi-orbs-integrations.md)

## 4. Delegation và phối hợp nhiều agent

**Use case:** Chia một nhiệm vụ thành các phần độc lập hoặc phụ thuộc nhau, chạy song song và tổng hợp kết quả.

- **Pi Agents:** extension cho phép tạo nhóm agent có dependency graph; các node độc lập có thể chạy song song. Tài liệu báo cáo node đã hoàn thành không chạy lại khi session được khôi phục, nhưng tool effects vẫn có thể lặp và kết quả đang chờ có thể được gửi hơn một lần sau crash. [Pi Agents Graphs](wiki/pi-agents-graphs.md), [Overview and Recovery](wiki/pi-agents-overview.md)
- **Pi Pocket:** linked sessions có thể được tạo và nhắn tin để phối hợp công việc. Tuy nhiên, tài liệu nêu một cửa sổ crash có thể làm mất báo cáo cuối tự động từ session con; không nên coi báo cáo đó là bảo đảm delivery tuyệt đối. [Pi Pocket Orchestration](wiki/pi-pocket-orchestration.md)
- **Cloudflare demo:** một subagent tìm kiếm lịch sử các conversation và chỉ trả kết quả cuối cho agent cha; ví dụ này minh họa cả delegation lẫn thiết kế replay-safe. [Pi Durable on Cloudflare](wiki/pi-durable-on-cloudflare.md)

## 5. Ứng dụng agent cá nhân và cộng tác

**Use case:** Xây ứng dụng có session agent được lưu bền, cho phép người dùng theo dõi hoặc tiếp tục công việc từ nhiều client.

| Ứng dụng | Use case được wiki mô tả |
|---|---|
| [Pi Pocket](wiki/pi-pocket-overview.md) | Ứng dụng self-hosted, mobile-first với multiplayer sessions, lưu trạng thái agent bằng Pi Durable. |
| [Durable Pi](wiki/durable-pi-network.md) | Mạng agent có backend và storage trên từng thiết bị; hub, terminal và HTTP client theo dõi hoặc điều khiển. Đóng client tự nó không dừng công việc trên backend. |
| [Pi Orbs](wiki/pi-orbs-overview.md) | Các bot có conversation riêng, cùng chạy trên một Fly.io Sprite và dùng chung workspace/model. |
| [Cloudflare demo](wiki/pi-durable-on-cloudflare.md) | Chat agent nhiều người dùng, mỗi session gắn với một Durable Object và SQLite riêng; đây là demo, không phải production template. |

## 6. Browser agent

**Use case:** Để agent đọc và tương tác với trang web, đồng thời lưu lịch sử conversation cục bộ.

[Pi Tab](wiki/pi-tab-overview.md) dùng Pi Durable cho browser agent, có bookmarklet và Chrome extension. Hai mode có storage và phạm vi hoạt động khác nhau.

**Giới hạn quan trọng:** Khôi phục conversation không đồng nghĩa với việc vẫn được phép thao tác trên tài liệu web mới. Với extension, reload hoặc navigation thu hồi quyền trên document cũ; đóng tab của task sẽ dừng task. Nguồn: [Pi Tab Recovery and Storage](wiki/pi-tab-recovery.md).

## 7. Giám sát coding agent

**Use case:** Gắn một lớp supervision vào session Pi Durable để kiểm tra và can thiệp khi agent lập trình.

Tài liệu [Foreman Attached Hooks](wiki/foreman-attached-hooks.md) mô tả bridge chuyển các event từ Pi Durable sang Foreman. Foreman có thể dùng hook để chặn tool hoặc dừng công việc, nhưng các tool khác trong một batch song song có thể đã chạy; bridge cũng cần host hỗ trợ subprocess và không chạy trong Cloudflare Worker theo tài liệu được khảo sát.

## Khi nào nên cân nhắc Pi Durable?

**Tổng hợp từ các use case trên:** phù hợp nhất khi mất tiến độ là tốn kém, workflow kéo dài hoặc phải chờ, hay host có thể restart/hibernate. Nếu chỉ là một lượt hỏi đáp ngắn, chi phí thiết kế storage, recovery và replay có thể không đáng đổi. [Nguồn](wiki/agent-execution-models-home-cloud-durable.md)

**Ranh giới bắt buộc:** durability **không bảo đảm exactly-once cho tác động bên ngoài**. `requestId` có thể chống nhận trùng submission, nhưng gửi email, tạo PR, deploy hoặc chạy migration vẫn cần idempotency key, reconciliation hoặc bước xác nhận riêng. [Pi Durable Replay Safety](wiki/pi-durable-replay-safety.md).

## Phạm vi và độ tin cậy

- Tổng hợp dựa trên các concept hiện có trong wiki; nhiều trang ứng dụng còn **draft**, implementation và tests chưa được kiểm tra đầy đủ.
- Các mô tả phần lớn là **reported**, không phải kết quả tôi chạy lại. Một số trang có `stale_after` do API và nền tảng có thể thay đổi.
- Không nghiên cứu thêm `raw/` trong lượt này. Kiểm tra cấu trúc chạy thành công: **43 concept, 1 index**.
- Tôi để bản tổng hợp này ở dạng trả lời tạm thời, **không sửa wiki hoặc log**.