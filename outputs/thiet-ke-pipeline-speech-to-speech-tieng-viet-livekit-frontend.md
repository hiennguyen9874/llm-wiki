# Vietnamese Voice Lab

**Mình đề xuất làm một “Vietnamese Voice Lab”: Next.js + Agents UI, kết nối với pipeline L0 self-host trong `outputs/thiet-ke-pipeline-speech-to-speech-tieng-viet-livekit.md`.** Demo vừa đủ đẹp để trải nghiệm, vừa đủ thông tin để kiểm chứng pipeline — không chỉ là một màn hình chatbot có microphone.

Đây là đề xuất kiến trúc; chưa dựng hoặc kiểm chứng runtime.

## 1. Chọn starter, không viết frontend từ đầu

Dùng [React starter chính thức](https://github.com/livekit-examples/agent-starter-react), vì đã có:

- Next.js và TypeScript.
- Voice conversation, audio visualizer.
- Connect/disconnect và media controls.
- Transcript và text chat.
- Agents UI có source nằm trong project, thuận tiện Việt hóa và chỉnh sửa.

[React quickstart](https://docs.livekit.io/frontends/start/react-quickstart.md) phù hợp để hiểu luồng tối thiểu. Nhưng với demo của bạn, starter tiết kiệm công xử lý session, layout và controls hơn.

**Giữ:** voice, transcript, device selection, dark/light theme.  
**Bỏ khỏi bản đầu:** camera, screen sharing, avatar, upload file và voice cloning.

### Lưu ý quan trọng về self-host

Source starter hiện có fallback tới **LiveKit homepage agent** khi thiếu cấu hình. Vì yêu cầu no-egress của thiết kế, mình sẽ **xóa fallback này và báo lỗi cấu hình rõ ràng**, không chỉ điền `.env`.

Đồng thời:

- Không dùng Cloud development token server.
- Không dùng public ASR/TTS/LLM.
- API secret chỉ tồn tại phía server.
- Không tải font, analytics hoặc tài nguyên bên ngoài trong profile no-egress.

Nguồn: [`app/page.tsx`](https://github.com/livekit-examples/agent-starter-react/blob/main/app/page.tsx).

## 2. Giao diện nên có hai chế độ

### Chế độ “Trải nghiệm”

Một màn hình đơn giản:

```text
┌──────────────────────────────────────────────────────┐
│ Vietnamese Voice Lab             L0 · Self-hosted    │
├──────────────────────────────────────────────────────┤
│ Giọng: Bắc / Nam*       Microphone: [Thiết bị ▼]      │
│                                                      │
│                  [Audio visualizer]                  │
│                    Đang lắng nghe                    │
│                                                      │
│       Bạn có thể nói và ngắt lời trợ lý bất cứ lúc nào│
│                                                      │
│ [Bắt đầu]       [Bật/tắt mic]       [Kết thúc]         │
├──────────────────────────────────────────────────────┤
│ Hội thoại                                            │
│ Bạn: ...                                             │
│ Trợ lý: ...                                          │
├──────────────────────────────────────────────────────┤
│ [Nhập tin nhắn để kiểm tra riêng đường text...] [Gửi] │
│                                       [Chẩn đoán ▼] │
└──────────────────────────────────────────────────────┘
```

`*` Chỉ hiển thị các voice thực sự đã được backend cấp quyền và sẵn sàng.

Các hành vi mình sẽ chốt:

- Người dùng bấm **Bắt đầu** mới mở session/mic; không tự kết nối khi tải trang.
- Mic giữ hoạt động khi agent đang nói hoặc suy nghĩ, trừ khi người dùng tự mute.
- Hiển thị “Đang kết nối / Đang khởi tạo / Đang nghe / Đang xử lý / Đang nói”.
- Khi autoplay bị chặn, hiện nút **Bật âm thanh**.
- Khi lỗi, phân biệt: quyền mic, kết nối room, agent chưa vào, dịch vụ model lỗi.
- Transcript chỉ giữ trong memory mặc định; không tự lưu `localStorage`.

Điểm quan trọng: `canListen` trong docs bao gồm cả lúc agent `thinking` và `speaking`. **Không biến trạng thái “Đang nói” thành lý do khóa microphone**, vì sẽ phá full-duplex/barge-in.

Nguồn: [Agent state](https://docs.livekit.io/frontends/build/agent-state.md), [Media controls](https://docs.livekit.io/frontends/agents-ui/media-controls.md).

### Chế độ “Chẩn đoán”

Panel mở rộng dành cho người thử PoC:

| Nhóm | Thông tin |
|---|---|
| Session | ID vô danh, profile, phiên bản pipeline |
| Cấu hình thực tế | ASR/TTS/voice/turn policy do backend xác nhận |
| Kết nối | Room connected, agent connected, mic published, audio playback |
| Pipeline | ASR latency, LLM TTFT, TTS TTFA, lỗi/timeout/429 |
| Interruption | Số lần ngắt, false interruption, trạng thái cancellation |
| Đánh giá | “Nghe sai”, “Cắt câu sớm”, “Phản hồi chậm”, “Đọc sai”, “Ngắt lời không được” |

**Các metric pipeline này phải do worker/backend cung cấp.** Không suy đoán “ASR đang chạy” hoặc “TTS mất bao lâu” chỉ từ animation hay agent state.

## 3. Giữ đúng ranh giới kiến trúc

```text
Next.js browser
   ├─ HTTPS → app backend: auth / config / token
   └─ WebRTC → LiveKit Server OSS
                         ↕
                 LiveKit Agents worker
                    ├─ ASR service
                    ├─ LLM endpoint
                    └─ TTS service
```

Frontend chỉ sở hữu:

- Session UI.
- Microphone, thiết bị và audio playback.
- Transcript/text input.
- Hiển thị telemetry và feedback.

Frontend **không** sở hữu:

- VAD/endpointing quyết định lượt.
- Chunker/normalizer.
- ASR/TTS inference.
- Conversation history authoritative.
- Cancellation state machine thứ hai.

Điều này bám sát quyết định của tài liệu: **AgentSession là owner duy nhất của turn và speech lifecycle.**

Cũng không cần browser tự chuyển mic thành WAV 16 kHz rồi POST vào ASR. Audio đi bằng WebRTC; contract input 16 kHz/output 48 kHz được xử lý và kiểm chứng ở worker/adapters. Dropdown trên UI không chứng minh downlink thật sự giữ 48 kHz.

## 4. Kết nối bằng Session API và token endpoint riêng

Dùng các primitive đã được docs xác nhận:

- `TokenSource.endpoint(...)`.
- `useSession(...)`.
- `session.start()` / `session.end()`.
- `AgentSessionProvider` cho Agents UI.
- `useAgent(...)` để đọc state.
- `useSessionMessages(...)` để đọc transcript và gửi text.

Nguồn: [Session management](https://docs.livekit.io/frontends/build/sessions.md).

Các component phù hợp:

| Chức năng | Component |
|---|---|
| Session context và audio playback | `AgentSessionProvider` |
| Mic, thiết bị, disconnect | `AgentControlBar` |
| Transcript | `AgentChatTranscript` |
| Visualizer | Chọn kiểu Bar hoặc Wave |
| Xử lý autoplay | `StartAudioButton` |

**Không lắp thêm renderer audio thứ hai một cách máy móc:** docs của `AgentSessionProvider` cho biết nó đã đảm bảo remote audio được phát. Cần kiểm source phiên bản pin trước khi thêm `RoomAudioRenderer`.

Nguồn: [Agents UI](https://docs.livekit.io/frontends/agents-ui.md), [AgentSessionProvider](https://docs.livekit.io/reference/components/agents-ui/component/agent-session-provider.md).

### Backend tối thiểu

Mình đề xuất hai endpoint ứng dụng:

**`GET /api/demo-config` — contract tự thiết kế**

Trả về profile và voice được phép, cấu hình mặc định và capabilities. Không trả secret, reference audio path hoặc địa chỉ private model APIs.

**`POST /api/token` — theo schema chuẩn LiveKit**

Backend thực hiện:

1. Xác thực người dùng/quyền truy cập demo.
2. Kiểm admission.
3. Tạo room và participant identity riêng.
4. Validate profile/voice/agent dispatch.
5. Cấp token scoped cho room.
6. Trả `201` với `server_url` và `participant_token`.

**Không ký nguyên `room_config` do client gửi mà không kiểm quyền.**

Có một khác biệt cần xử lý: route trong starter hiện trả field camelCase như `serverUrl`, `participantToken`, trong khi tài liệu endpoint chuẩn dùng snake_case. Vì vậy phải thống nhất client/server contract hoặc viết adapter — không ghép hai ví dụ rồi kỳ vọng tự tương thích.

Ngoài ra, route starter tự cảnh báo chưa có authentication và chặn production mặc định. Nó chỉ là điểm xuất phát, không phải backend an toàn sẵn có.

Nguồn: [Endpoint token generation](https://docs.livekit.io/frontends/build/authentication/endpoint.md), [`app/api/token/route.ts`](https://github.com/livekit-examples/agent-starter-react/blob/main/app/api/token/route.ts).

## 5. Bản đầu chỉ dùng profile L0

Mình sẽ cố định:

- Silero + VAD-only.
- Preemptive generation tắt.
- ASR Qwen baseline theo tài liệu.
- TTS adapter PCM48k.
- Một voice đã qua readiness/authorization.
- Một user và một agent trong mỗi room.

**Không đưa Smart Turn hoặc mọi tham số VAD lên UI ngay.** Quá nhiều nút chỉnh sẽ khiến các lần thử không còn so sánh được.

Sau khi L0 ổn mới thêm:

- Chọn voice Bắc/Nam.
- A/B ASR giữa các session.
- A/B VAD-only và Smart Turn đã qua integration gate.
- So sánh latency theo profile.

Mọi lựa chọn engine/voice được **pin khi bắt đầu session**; đổi cấu hình thì tạo session mới.

Theo skill building, demo này chỉ có một trách nhiệm hội thoại nên chưa cần multi-agent/handoff. Prompt cũng nên nhỏ, trả lời tiếng Việt ngắn, khoảng 1–3 câu.

## 6. Đo latency trung thực, không làm dashboard “đẹp nhưng sai”

Trong panel nên tách rõ:

- **Backend metrics:** ASR latency, LLM TTFT, TTS TTFA.
- **Client estimate:** khoảng phản hồi ước lượng, có công bố cách đo.
- **D1 đã kiểm chứng:** chỉ xuất hiện khi có harness đo phù hợp.

Không gọi các mốc sau là D1:

- Agent chuyển sang `speaking`.
- Nhận được transcript.
- TTS trả PCM đầu tiên.
- Worker enqueue audio.

D1 mục tiêu của tài liệu là **âm tiết người dùng cuối → audio bot nghe được ở client**. Bản đầu có thể chỉ báo backend metrics và ghi “Chưa đo D1”; sau đó bổ sung client audio-analysis/replay harness, không tạo thêm playback pipeline.

Telemetry gửi tới frontend nên content-free: IDs vô danh, duration, status, version. Transcript phục vụ UI là một luồng riêng, không tự động đi vào telemetry hoặc export.

## 7. Thứ tự triển khai mình chọn

| Bước | Deliverable | Điều kiện xong |
|---|---|---|
| 1 — Media | Starter kết nối OSS, token endpoint, agent phát audio thử | Một room đúng một agent; mic/audio hoạt động |
| 2 — L0 voice | Kết nối cascade thật, Việt hóa, transcript, lỗi cơ bản | Nói tiếng Việt nhiều lượt và ngắt lời được |
| 3 — Diagnostics | Backend metrics, cấu hình thực tế, feedback | Không metric giả, không log nội dung mặc định |
| 4 — Browser hardening | Permissions, autoplay, reconnect, TURN, mobile layout | Chạy trên browser/thiết bị mục tiêu |
| 5 — A/B | Voice/profile selector và report theo session | Mỗi lần chỉ đổi một thành phần |

Bộ thử tối thiểu:

- “Không”, “dừng”, “vâng”.
- Nói rồi ngập ngừng và tiếp tục.
- Ngắt bot giữa câu.
- Số tiền, ngày giờ, tên riêng.
- Loa ngoài so với tai nghe.
- ASR/TTS timeout hoặc overload.
- Agent crash, mất mạng, reconnect.
- Kiểm egress và kiểm transcript sau interruption.

Các skill LiveKit cũng nhấn mạnh: text tests không kiểm được VAD/audio. Debugger audio dùng Cloud Inference nên **không mặc định áp dụng cho profile no-egress này**; browser E2E và replay self-host mới là đường kiểm chứng chính.

### Chốt lại

**Mình sẽ làm demo như một “voice playground có chế độ lab”, không làm dashboard production và không làm chatbot gọi ASR/TTS trực tiếp từ browser.**

Deliverable đầu tiên nên là: **Next.js starter đã loại bỏ Cloud fallback + token/auth riêng + giao diện tiếng Việt + full-duplex voice/transcript + panel metrics tối thiểu**, kết nối đúng L0 hiện có. Khi đường này chạy ổn mới thêm Smart Turn, A/B và đo D1 chuẩn.