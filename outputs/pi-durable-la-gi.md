## Pi Durable là gì?

`@earendil-works/pi-durable` là một **agent harness** (lớp khung chạy agent) viết bằng TypeScript, hiện vẫn đang thử nghiệm. Nó lưu (commit) conversation, model turn, tool call và state của ứng dụng vào storage **trước khi hiển thị**. Nếu process chết, chỉ cần mở lại storage là agent làm tiếp từ đúng chỗ đã dừng, không phải gõ "continue" và không mất tool result.
→ [Pi Durable Overview](wiki/pi-durable-overview.md)

**Cơ chế chính:**
- **Effect sandwich**: mỗi bước làm theo ba nhịp. Lưu *intent* (định làm gì), chạy *effect* (thực thi), rồi lưu *result* (kết quả). Gọi model hay chạy tool đều theo khuôn này. → [Effect Sandwich](wiki/pi-durable-effect-sandwich.md)
- **Task**: là một state machine bền, checkpoint sau mỗi bước. Task có thể tạo child task và chờ nó, và có thể "ngủ" (`sleepUntil`) qua nhiều lần restart. → [Tasks](wiki/pi-durable-tasks.md)
- **Document**: state của host lưu dạng JSON có type, nằm cạnh transcript và được commit atomic cùng nó. → [Documents](wiki/pi-durable-documents.md)
- **Storage**: có SQLite, JSONL, IndexedDB, Cloudflare Durable Objects và bản in-memory. → [Storage](wiki/pi-durable-storage.md)
- Tác giả cố ý làm nó thành một **primitive** nhỏ, tổng quát (họ nói khoảng 12k dòng), không gắn với sản phẩm nào. Họ cũng nói rõ là **không dùng event sourcing**.

**Điểm cần hiểu đúng:** durability là **một lớp harness**, không phải "chỗ chạy" agent. Nó gắn được vào agent chạy trên máy cá nhân hay trên cloud. Nó không làm model thông minh hơn, chỉ giúp công việc không bị mất âm thầm.
→ [Home, Cloud, and Durable Agents](wiki/agent-execution-models-home-cloud-durable.md)

## Dùng để làm gì?

- Cho agent sống sót qua crash, restart, VM bị evict hay laptop gập lại.
- Lưu và resume được lịch sử rất dài mà không phải nạp cả cây conversation vào memory.
- Resume từ **state đã ghi gần nhất**, thay vì bắt agent đọc lại toàn bộ transcript.
- Chống gửi trùng: client dùng lại cùng `requestId` thì một request chỉ thành một submission.

## Một số use case (theo các nguồn trong wiki)

1. **Task nhiều bước, chạy lâu.** Ví dụ một bản release game: thêm cột, backfill 5 triệu dòng, deploy, chờ duyệt, rồi mở server. Ledger ghi "batch 3000/5000 done", nên process mới sẽ chạy tiếp từ batch 3001 thay vì phải vào DB kiểm tra tay.
2. **Workflow chờ quyết định của người trong nhiều ngày.** Task "ngủ" bền qua restart, đến lúc có approval thì chạy tiếp.
3. **Bot sống lâu trong workspace**, ví dụ Slack bot chạy nhiều năm với lịch sử khổng lồ.
4. **Cloud agent tự kích hoạt** bởi issue, CI fail, alert hoặc lịch chạy. Ví dụ sự cố lúc 3 giờ sáng: agent điều tra và mở PR, sáng ra người chỉ cần review.
5. **Chat agent nhiều người dùng chung trên Cloudflare Durable Objects.** Mỗi session là một Durable Object, ngủ (hibernate) khi rảnh và thức dậy khi có request, WebSocket hoặc alarm. Tin nhắn gửi lúc agent đang bận sẽ xếp hàng trong inbox bền. → [Pi Durable on Cloudflare](wiki/pi-durable-on-cloudflare.md)
6. **Background subagent** sống lâu hơn lệnh foreground đã tạo ra nó (task tạo với `background: true`).
7. **Code mode**: model chạy JavaScript trong sandbox, mỗi lần gọi tool được ghi journal, nên script resume được một cách deterministic sau restart. → [Code Mode](wiki/pi-durable-code-mode.md)

**Khi nào đáng dùng:** khi agent bắt buộc phải sống sót, khi run rất dài, hoặc khi có bước phải chờ. Cái giá là hệ thống phức tạp hơn, vì mọi bước đều đi qua lớp ghi chép.

## Giới hạn quan trọng

**Durable không có nghĩa là exactly-once.** Nếu process chết giữa lúc đang gửi email, tạo PR, deploy hay chuyển tiền, harness không biết action đó đã xảy ra hay chưa. Những tool có side effect vẫn cần idempotency key hoặc phải đối chiếu với hệ thống bên ngoài trước khi chạy lại. Mặc định harness coi tool là `unsafe` và không tự chạy lại tool bị gián đoạn.
→ [Replay Safety](wiki/pi-durable-replay-safety.md)

## Mức độ tin cậy

- Mọi thông tin trên là **Reported**, lấy từ README, các bài viết và talk. Không có code hay crash test nào được chạy trong repo này.
- API có thể thay đổi giữa các phiên bản. Các trang trong wiki đánh dấu `stale_after: 2027-01-25`.
- Câu trả lời chỉ dựa trên wiki, không mở `raw/`. Wiki không thay đổi gì.

Muốn tự kiểm chứng thì xem [Build and Crash-Test Recipe](wiki/pi-durable-build-crash-test.md): dựng một agent SQLite tối giản, kill rồi restart để thấy nó replay.