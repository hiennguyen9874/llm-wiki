# Chương 8. Transport mạng cho audio realtime 🟡 (WebSocket 🔴)

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần III.
> **Chương trước:** [Chương 7. Front-end âm học: echo, nhiễu, gain](chuong-07-front-end-am-hoc-echo-nhieu-gain.md).
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §5.1 (client/transport), §5.7 (orchestration, Realtime subset), §9.5 (privacy và bảo mật).
> **Cơ sở:** phần giao thức (TCP/UDP, head-of-line blocking, WebSocket, WebRTC, ICE, SRTP, Opus, jitter buffer, SIP/G.711, SSE) là kiến thức mạng giáo trình, **không** lấy từ nguồn trong wiki. Các chi tiết về giao thức cụ thể của dự án lấy từ [Speech-to-Speech Realtime Engine](../wiki/speech-to-speech-realtime-engine.md), [Speech-to-Speech Browser Demo](../wiki/speech-to-speech-browser-demo.md), [NeMo-Speech.cpp HTTP and Realtime API](../wiki/nemo-speech-http-api.md), [Voice Agent Frameworks](../wiki/voice-agent-frameworks.md), [VieNeu OpenAI-compatible Speech API](../wiki/vieneu-tts-openai-speech-api.md) và [Speech-to-Speech OpenAI-compatible Backends](../wiki/speech-to-speech-openai-compatible-backends.md); các trang đó là **Reported** từ tài liệu của từng dự án, chưa được chạy lại ở đây. Các số ở §8.2.3, §8.3.3 và §8.8.2 được tính/mô phỏng bằng Python 3.12 thuần trong lúc viết (**Reproduced**, nhưng là **mô hình đồ chơi**: không có mạng thật, tỷ lệ mất gói giả định). Mọi đoạn code Python/JavaScript trong chương **chưa được chạy trên server hay trình duyệt trong repo này**; hãy xem chúng là phác thảo để hiểu cấu trúc.

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Giải thích được vì sao audio realtime nhạy với **jitter** và **head-of-line blocking** hơn so với tải file, và vì sao TCP vẫn dùng được cho MVP.
2. Thiết kế được **WebSocket audio protocol**: binary frame, kích thước frame, header/handshake, keepalive, reconnect.
3. Cài đặt **backpressure** và **hàng đợi có chặn** để client chậm không làm server phình bộ nhớ hoặc tăng độ trễ vô hạn.
4. Hiểu WebRTC giải quyết những gì WebSocket không giải quyết (NAT, mất gói, jitter buffer, AEC, mã hoá), và chi phí đổi lại.
5. Chọn được giữa **WebSocket, WebRTC (P2P hoặc SFU), HTTP streaming, telephony** theo ngữ cảnh.
6. Đọc và dùng được tầng ứng dụng: **OpenAI Realtime events**, `/v1/audio/speech`, `/v1/audio/transcriptions`; biết "OpenAI-compatible" nghĩa là gì và không có nghĩa là gì.
7. Hiểu cách **huỷ** (cancel/barge-in) đi qua từng loại transport.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. Vì sao gửi binary frame thay vì base64?
- Q2. WebRTC giải quyết những gì mà WebSocket không làm (packet loss, jitter, NAT, AEC)?
- Q3. Backpressure trên WebSocket xử lý thế nào khi client chậm?

---

## 8.1 Bức tranh tổng: transport nằm ở đâu và cần gì

```text
 Mic ─► [capture, AEC] ─► ENCODE? ─► ┌───────────────┐ ─► DECODE? ─► VAD ─► ASR ─► LLM ─► TTS
                                      │   TRANSPORT   │                                    │
 Loa ◄─ [playback queue] ◄─ DECODE ◄─ └───────────────┘ ◄─ ENCODE? ◄───────────────────────┘
        (Chương 6)                    (Chương 8: chương này)
```

Transport phải chuyển hai luồng ngược chiều, đồng thời, với các yêu cầu **khác nhau**:

| Luồng | Dữ liệu | Yêu cầu chính |
|---|---|---|
| **Uplink** (client → server) | PCM hoặc Opus liên tục, 16 kHz mono (đầu vào ASR) | Đều đặn, trễ thấp, chịu được mất vài gói; ASR chịu được ít nhiều mất mát nhưng không chịu nổi khoảng trống dài |
| **Downlink** (server → client) | Audio TTS 24–48 kHz, tốc độ sinh có thể **nhanh hơn realtime** | Không mất mẫu, đúng thứ tự, **huỷ được ngay**; client có playback queue (Chương 6) |
| **Control** | JSON: bắt đầu/kết thúc lượt nói, `clear`, transcript, lỗi | Đáng tin cậy, đúng thứ tự, liên kết với audio theo `generation_id` |

Hai thông tin quan trọng rút ra:

- Uplink là **luồng thời gian thực thật sự** (mic chạy 1 giây thì sinh ra 1 giây audio). Downlink là luồng **có thể bùng phát** (TTS sinh nhanh hơn tốc độ phát), nên cần **backpressure** và **flush**.
- Control và audio phải **cùng ngữ cảnh thứ tự**. Nếu `client.clear` đi trên kênh khác với audio thì có thể "tới sau" những chunk audio cũ. Đây là lý do thiết kế gắn `generation_id` vào cả hai (xem §8.9).

Ghi chú mức ưu tiên: WebSocket là 🔴 vì cả đường MVP lẫn nhiều backend trong wiki đều dùng nó; WebRTC là 🟡 vì cần cho production qua Internet/mobile nhưng có thể đến sau.

---

## 8.2 Nền tảng mạng: TCP, UDP và vì sao nó quan trọng với audio

### 8.2.1 TCP

TCP cung cấp luồng byte **tin cậy và có thứ tự**: mất gói thì gửi lại, đến lộn xộn thì sắp xếp lại trước khi giao cho ứng dụng.

```text
Gói gửi:   1  2  3  4  5  6
Mạng:      1  2  ✗  4  5  6        (gói 3 bị mất)
TCP nhận:  1  2  ·  ·  ·  ·        gói 4,5,6 đã đến nhưng bị GIỮ LẠI
           ...đợi gửi lại 3 (≥ 1 RTT)...
Giao app:  1  2  3  4  5  6        tất cả cùng đến một lúc
```

Hiện tượng gói 4, 5, 6 bị giữ chờ gói 3 gọi là **head-of-line (HOL) blocking**. Với tải file thì vô hại. Với audio realtime thì đây là điều tệ: dữ liệu mới nhất (có giá trị nhất) bị chặn sau dữ liệu cũ đã mất, và sau đó ứng dụng nhận một cụm lớn trễ.

### 8.2.2 UDP

UDP gửi từng datagram độc lập: **không** đảm bảo đến, **không** đảm bảo thứ tự, **không** gửi lại. Ứng dụng tự quyết định: bỏ qua gói mất, che giấu (PLC), hay sửa bằng FEC. Đây là nền cho RTP/WebRTC.

### 8.2.3 Ước lượng độ trễ do HOL: mô hình đồ chơi

Mô phỏng (Python thuần): luồng frame 20 ms, mất gói 2% độc lập, RTT 80 ms (sau mất gói, mọi frame đến trong lúc chờ retransmit bị giữ lại, mô hình đơn giản hoá bỏ qua cửa sổ tắc nghẽn):

| Chỉ số | Độ trễ thêm do TCP (mô hình đồ chơi) |
|---|---|
| p50 | 0 ms |
| p95 | 40 ms |
| p99 | 80 ms |
| max | 80 ms |
| So với UDP | độ trễ thêm 0, nhưng ~60 trong 3000 frame **mất hẳn** |

**Reproduced** (mô hình đồ chơi). Cách đọc: trên mạng LAN/loopback (mất gói gần 0), TCP gần như không chậm thêm, nên MVP dùng WebSocket là hợp lý. Trên mạng di động/Wi-Fi yếu, đuôi p95/p99 là chỗ đau: người dùng nghe "khựng rồi tràn ra". TCP còn có thêm độ trễ do hàng đợi gửi (bufferbloat) và thuật toán Nagle/delayed ACK mà mô hình không đo; số trên **không** đại diện cho mạng thật, hãy đo trên đường mạng thực của bạn.

### 8.2.4 Bảng chọn nhanh

| Tiêu chí | TCP (WebSocket, HTTP) | UDP (RTP/WebRTC) |
|---|---|---|
| Mất gói | Sửa bằng gửi lại → tăng trễ | Chấp nhận mất, che bằng PLC/FEC |
| Thứ tự | Đảm bảo | Không (jitter buffer tự sắp xếp) |
| Qua firewall/proxy | Dễ (cổng 80/443) | Khó hơn (cần STUN/TURN) |
| Độ phức tạp | Thấp | Cao |
| Phù hợp | LAN, loopback, MVP, control | Internet, mobile, hội thoại tự nhiên |

---

## 8.3 Băng thông và chọn định dạng trên đường truyền

### 8.3.1 PCM16 tốn bao nhiêu

PCM16 mono: `sample_rate × 16 bit`.

| Sample rate | Bitrate PCM16 mono |
|---|---|
| 8 kHz | 128 kbps |
| 16 kHz | 256 kbps |
| 24 kHz | 384 kbps |
| 48 kHz | 768 kbps |

**Reproduced** (tính toán). Với 16 kHz, 256 kbps ≈ 32 KB/s: rẻ trên LAN, nhưng đáng kể trên mạng di động nếu hàng nghìn kết nối. Opus giọng nói thường dùng khoảng 16–32 kbps (số điển hình theo kiến thức giáo trình, tuỳ cấu hình), tức nhỏ hơn PCM 8–16 lần.

### 8.3.2 Binary frame thay vì base64 (trả lời Q1)

Base64 mã hoá 3 byte thành 4 ký tự, tăng khoảng **33%** kích thước, cộng thêm chi phí encode/decode và bọc JSON. Đo thực tế một frame 20 ms ở 16 kHz:

| Dạng gửi | Kích thước một frame 20 ms @16 kHz |
|---|---|
| Binary PCM16 | 640 byte |
| Base64 | 856 byte (+33,8%) |
| Base64 bọc JSON `input_audio_buffer.append` | 903 byte (+41%) |

**Reproduced.** Ngoài chi phí băng thông còn có: CPU cho encode/decode Base64 ở cả hai đầu, cấp phát chuỗi lớn trong JS/Python (áp lực GC), và độ trễ thêm do parse JSON. Vì vậy thiết kế của tài liệu chính đặt **binary frame 20–32 ms** cho đường MVP.[^design]

Tuy nhiên có một sự thật cần nhớ: **các giao thức Realtime kiểu OpenAI dùng base64 trong JSON** vì chúng dùng một kênh text. Các server trong wiki hỗ trợ cả hai: kênh transcription của NeMo-Speech.cpp chấp nhận binary PCM16 little-endian hoặc base64 trong `input_audio_buffer.append`; engine HF speech-to-speech nhận base64 PCM qua `input_audio_buffer.append`.[^nemo-api][^s2s-engine] Quy tắc thực tế: giao thức của bạn tự thiết kế → dùng binary; cần tương thích SDK có sẵn → chấp nhận base64.

### 8.3.3 Kích thước frame

Frame càng nhỏ thì độ trễ đóng gói càng thấp nhưng overhead header càng lớn.

| Frame | Mẫu @16 kHz | Byte PCM16 | Ghi chú |
|---|---|---|---|
| 10 ms | 160 | 320 | Overhead lớn, ít dùng qua WebSocket |
| 20 ms | 320 | 640 | Chuẩn của Opus/RTP; chunk Silero VAD 512 mẫu = 32 ms |
| 32 ms | 512 | 1024 | Khớp chunk VAD 512 mẫu |
| 100 ms | 1600 | 3200 | Giảm overhead, nhưng thêm 100 ms trễ đóng gói |

Quy tắc: frame uplink **20–32 ms**, khớp kích thước xử lý của VAD để tránh phải ghép/cắt lại. Engine HF cắt audio vào thành chunk 512 mẫu cho VAD ở 16 kHz, và TTS ra của NeMo VoiceChat là gói 80 ms `response.output_audio.delta`.[^s2s-engine][^nemo-api] Downlink thường dùng frame lớn hơn (80–200 ms) vì không cần nhạy như uplink; nhưng chunk lớn khiến thời gian phản ứng khi `clear` kém mịn hơn, hãy cân nhắc khi chọn.

---

## 8.4 WebSocket cho audio hai chiều 🔴

### 8.4.1 WebSocket là gì

WebSocket bắt đầu bằng một HTTP request `Upgrade: websocket`, sau đó chuyển thành kênh **song công, giữ lâu dài** trên cùng một kết nối TCP. Dữ liệu đi theo **message**, mỗi message gồm một hoặc nhiều frame, thuộc loại **text** (UTF-8) hoặc **binary**. Có control frame: ping, pong, close.

Vì chạy trên TCP nên nó thừa hưởng toàn bộ ưu điểm (tin cậy, đúng thứ tự, đi qua proxy/443) và nhược điểm (HOL blocking, không có jitter buffer, không có AEC) ở §8.2.

### 8.4.2 Thiết kế protocol: text cho control, binary cho audio

Mẫu thiết kế đơn giản và hiệu quả:

```text
Client → Server
  text   {"type":"session.start","sample_rate":16000,"encoding":"pcm_s16le","channels":1,"frame_ms":20}
  binary <640 byte PCM16>          ← lặp mỗi 20 ms
  text   {"type":"audio.played","generation_id":7,"played_sample_offset":38400}
  text   {"type":"session.end"}

Server → Client
  text   {"type":"session.ready","session_id":"..."}
  text   {"type":"transcript.partial","text":"..."}
  text   {"type":"transcript.final","text":"..."}
  text   {"type":"tts.start","generation_id":7,"sample_rate":48000}
  binary <audio chunk>             ← chỉ audio, theo generation hiện tại
  text   {"type":"client.clear","generation_id":7}
  text   {"type":"error","code":"...","message":"..."}
```

Điểm thiết kế quan trọng:

1. **Handshake đầu phiên** khai báo `sample_rate`, mã hoá, số kênh. Các engine trong wiki đều xử lý như vậy: engine NeMo yêu cầu `session.update` trước khi audio bắt đầu và cấu hình là bất biến sau frame audio đầu tiên.[^nemo-api] Lý do: nếu đổi định dạng giữa chừng, bạn sẽ có audio sai tốc độ.
2. **Mọi binary frame cùng một định dạng**; không trộn nhiều loại trong một kết nối. Nếu cần header (ví dụ `generation_id`, timestamp), đặt một header cố định 8–16 byte ở đầu frame binary, hoặc gửi một text frame ngay trước binary.
3. **Server khai báo sample rate downlink.** Backend TTS khác nhau trả sample rate khác nhau (ví dụ VieNeu 48 kHz, NeMo VoiceChat bắt buộc PCM16 24 kHz, `/v1/audio/speech` của NanoCodec 22,05 kHz) nên client **không được** hard-code.[^vieneu-api][^nemo-api] Sai sample rate = tiếng "chipmunk" hoặc "ì ì" (Chương 2).
4. **Chặn kích thước message** (ví dụ giới hạn 64 KB cho text, 1 MB cho binary) để chống tài nguyên bị lạm dụng (§8.10).

### 8.4.3 Server WebSocket tối giản (Python, phác thảo)

```python
# Phác thảo, CHƯA chạy trong repo này. Dùng thư viện `websockets`.
import asyncio, json
import websockets

FRAME_BYTES = 640                 # 20 ms @ 16 kHz PCM16 mono
UPLINK_Q_MAX = 50                 # 50 x 20 ms = 1 s tối đa

async def handler(ws):
    uplink: asyncio.Queue[bytes] = asyncio.Queue(maxsize=UPLINK_Q_MAX)
    downlink: asyncio.Queue[bytes | dict] = asyncio.Queue(maxsize=100)
    gen = 0

    async def reader():
        async for msg in ws:                     # msg: str (text) hoặc bytes (binary)
            if isinstance(msg, bytes):
                try:
                    uplink.put_nowait(msg)
                except asyncio.QueueFull:
                    uplink.get_nowait()          # bỏ frame CŨ nhất: uplink ưu tiên dữ liệu mới
                    uplink.put_nowait(msg)
            else:
                ev = json.loads(msg)
                ...                              # session.start, audio.played, ...

    async def writer():
        while True:
            item = await downlink.get()
            await ws.send(item if isinstance(item, bytes) else json.dumps(item))
            # `await ws.send` chỉ trả về khi dữ liệu đã vào buffer gửi → backpressure tự nhiên

    await asyncio.gather(reader(), writer(), pipeline(uplink, downlink))

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765, max_size=1 << 20,
                                ping_interval=20, ping_timeout=20):
        await asyncio.Future()
```

Ba chi tiết đáng chú ý trong phác thảo:

- **Hàng đợi có chặn ở cả hai hướng** (`maxsize`), không bao giờ `Queue()` vô hạn.
- **Chính sách khi đầy khác nhau theo hướng**: uplink bỏ frame **cũ**, vì với audio realtime dữ liệu mới quan trọng hơn (nhưng chỉ nên xảy ra khi server quá tải, và phải ghi metric); downlink không được bỏ chunk tuỳ tiện, thay vào đó **chặn producer** (backpressure, §8.5).
- `ping_interval`, `ping_timeout` bật keepalive (§8.4.5).

### 8.4.4 Client trình duyệt (JavaScript, phác thảo)

```js
// Phác thảo, CHƯA chạy trên trình duyệt trong repo này.
const ws = new WebSocket("wss://host/ws");
ws.binaryType = "arraybuffer";           // nhận binary dạng ArrayBuffer, không phải Blob

ws.onopen = () => ws.send(JSON.stringify({
  type: "session.start", sample_rate: 16000, encoding: "pcm_s16le", channels: 1, frame_ms: 20
}));

// Từ AudioWorklet (Chương 6): port.onmessage nhận Int16Array 320 mẫu
workletNode.port.onmessage = (e) => {
  if (ws.readyState !== WebSocket.OPEN) return;
  if (ws.bufferedAmount > 64 * 1024) return;   // backpressure phía client: bỏ frame khi ứng dụng gửi quá nhanh
  ws.send(e.data);                              // e.data: ArrayBuffer binary
};

ws.onmessage = (ev) => {
  if (typeof ev.data === "string") handleControl(JSON.parse(ev.data));
  else playbackQueue.push(currentGeneration, ev.data);   // Chương 6
};
```

Hai điểm hay quên:

- `binaryType = "arraybuffer"`: mặc định là `blob`, phải đọc bất đồng bộ, rất bất tiện cho audio.
- API `WebSocket` của trình duyệt **không có backpressure thật sự** (không có sự kiện "drain"); phía client chỉ có thể tự kiểm `bufferedAmount`. API `WebSocketStream` (có backpressure) chưa phổ biến trên mọi trình duyệt, hãy kiểm tra hỗ trợ trước khi dựa vào.

### 8.4.5 Keepalive, đóng kết nối, reconnect

- **Ping/pong:** gửi ping định kỳ (10–30 s) để phát hiện kết nối "chết lặng" (NAT timeout, di chuyển mạng) và giữ NAT/proxy không đóng vì rảnh. Không có ping thì có thể nhiều phút mới biết kết nối đã chết.
- **Phân biệt "im lặng" và "đứt":** người dùng không nói **không** có nghĩa là không có gì để gửi. Hãy tiếp tục gửi frame uplink (hoặc ping) ngay cả lúc im lặng, hoặc dùng gate VAD ở client và gửi ping riêng. Engine HF trong wiki có chế độ chỉ gửi audio khi VAD cục bộ báo có tiếng cho STT từ xa (giữ cả pre-speech padding), tức là tình huống này được xử lý chủ động ở tầng ứng dụng.[^backends]
- **Close code:** dùng đúng mã đóng (1000 bình thường, 1001 đi khỏi, 1011 lỗi server) để client biết có nên reconnect không.
- **Reconnect:** dùng **exponential backoff có jitter** (ví dụ 0,5 s → 1 → 2 → 4 s, ± ngẫu nhiên) để tránh "thundering herd". Quan trọng: **reconnect = phiên mới** trừ khi bạn thiết kế resume. Với voice agent, đơn giản nhất là: mất kết nối → xoá playback queue → kết thúc lượt đang chạy → mở phiên mới; đừng cố ghép tiếp audio dở dang.
- **Draining khi đóng:** đóng sạch nên cho server xử lý nốt audio còn đệm và gửi sự kiện kết thúc. Ví dụ NeMo `session.close`: server drain input còn lại, phát sự kiện hoàn tất rồi gửi `session.end` với các bộ đếm (đã nhận, đã gửi, đã bỏ, thời lượng audio).[^nemo-api]

### 8.4.6 Xác thực trên WebSocket

API trình duyệt `WebSocket` **không** cho đặt header tuỳ ý (như `Authorization`). Hệ quả thực tế:

- Dùng token trong query (`?api_key=...`): NeMo-Speech.cpp hỗ trợ cách này, nhưng URL có thể bị ghi vào log proxy, nên chỉ dùng token ngắn hạn.[^nemo-api]
- Hoặc gửi token trong **message đầu tiên** sau khi mở, hoặc dùng cookie phiên cùng origin.
- **Không đặt API key dài hạn vào trang public**: tài liệu NeMo khuyến nghị code trình duyệt dùng giao thức WebSocket của playground thay vì nhúng key.[^nemo-api] Mẫu chuẩn: server của bạn cấp **token tạm** cho client; server mới giữ key thật. Browser demo của HF dùng proxy cùng origin cho bước SDP vì server s2s không có CORS middleware và chỉ chuyển đến URL cố định trong env, không bao giờ đến URL do client chọn, để không thành open proxy.[^browser-demo]

---

## 8.5 Backpressure: khi một bên chậm (trả lời Q3)

### 8.5.1 Vấn đề

TTS sinh audio nhanh hơn thời gian thực (ví dụ 3×), nhưng loa chỉ tiêu thụ 1×; mạng hoặc client có thể còn chậm hơn nữa. Nếu server cứ đẩy:

```text
t = 0 s    TTS sinh 3 s audio, client phát 1 s    → còn 2 s trong buffer
t = 10 s   đã sinh 30 s audio, phát 10 s          → buffer 20 s audio
```

Mô phỏng: nếu không có chặn, sau 10 s sinh 3× với phát 1×, hàng đợi chứa **20 s audio ≈ 1,0 MB** ở 24 kHz PCM16 (**Reproduced**, mô hình đồ chơi). Quan trọng hơn bộ nhớ là **độ trễ**: khi người dùng ngắt lời, 20 s audio đã nằm trong hàng đợi/socket buffer nếu chưa được flush thì sẽ bị phát tiếp, hoặc phải bị loại bỏ. Backpressure vì vậy không chỉ là tiết kiệm RAM mà là điều kiện để barge-in phản ứng nhanh.

### 8.5.2 Ba điểm có thể đầy

```text
 TTS → [queue ứng dụng] → [socket send buffer (kernel, TCP)] → mạng → [socket recv buffer] → [client playback queue] → loa
        (1)                    (2)                                          (3)
```

1. **Hàng đợi ứng dụng**: do bạn kiểm soát hoàn toàn. Đặt `maxsize` và để producer **chờ** (`await queue.put`) khi đầy.
2. **Buffer gửi của kernel/thư viện**: `await ws.send()` trong thư viện async chỉ hoàn thành khi dữ liệu được chấp nhận vào buffer, nên `await` đúng chỗ cho backpressure tự nhiên. Nếu dùng `send` kiểu "fire-and-forget" thì buffer phình mà bạn không thấy.
3. **Hàng đợi phát ở client**: ứng dụng chỉ có thể điều khiển nó gián tiếp, bằng cách client **báo về** vị trí đã phát (`audio.played`, `played_sample_offset`, Chương 6). Server dựa vào đó giới hạn "lượng audio đang bay" (in-flight audio), ví dụ không gửi vượt quá `played + 1–2 s`.

### 8.5.3 Cơ chế "credit" dựa trên vị trí đã phát

```python
# Phác thảo, CHƯA chạy. Không cho gửi quá xa so với vị trí client đã phát.
MAX_LEAD_SAMPLES = 2 * 24000          # tối đa 2 s audio chưa phát

async def send_tts(ws, chunks, state):
    async for pcm in chunks:           # chunks sinh từ TTS
        while state.sent_samples - state.played_samples > MAX_LEAD_SAMPLES:
            await state.progress.wait()    # chờ client báo audio.played
            state.progress.clear()
        await ws.send(pcm)
        state.sent_samples += len(pcm) // 2
```

Lợi ích: lượng audio chưa phát bị chặn trên (≈ 2 s) → khi barge-in, tối đa 2 s cần flush; đồng thời TTS có thể bị **dừng sinh** (tiết kiệm GPU) vì producer bị chặn ngược lên trên. Đổi lại: nếu mạng jitter nặng, 2 s có thể không đủ để che, hãy tune.

### 8.5.4 Chính sách khi hàng đợi đầy: bỏ gì?

| Hướng | Nên làm | Lý do |
|---|---|---|
| Uplink (mic → ASR) | Bỏ frame **cũ** nhất, ghi metric `uplink_dropped` | Dữ liệu cũ đã mất giá trị; giữ dữ liệu mới để VAD/ASR bắt kịp |
| Downlink (TTS → loa) | **Chặn producer**, không bỏ giữa câu | Bỏ chunk giữa câu gây nhảy tiếng nghe được |
| Control | **Không bao giờ bỏ** | `clear`, `error` phải đến |
| Client chậm kéo dài | Đóng kết nối với mã lỗi rõ ràng | Tránh một client làm nghẽn tài nguyên của cả pool |

Gợi ý quan sát: các engine trong wiki có bộ đếm đã bỏ (NeMo `session.end` báo received/sent/dropped) và chặn kích thước hàng đợi theo từng pipeline; ngoài ra HF s2s ghi rõ không có hàng đợi admission dùng chung hay ngân sách đồng thời toàn endpoint.[^nemo-api][^backends] Nghĩa là nếu bạn triển khai nhiều phiên, tự thêm giới hạn đồng thời (xem §8.10).

---

## 8.6 WebRTC 🟡

### 8.6.1 WebRTC thực chất là một bộ giao thức

WebRTC không phải một giao thức đơn lẻ mà là tập hợp, được trình duyệt cài sẵn:

| Thành phần | Vai trò |
|---|---|
| **Signaling** (do bạn tự làm: HTTP/WebSocket) | Trao đổi SDP offer/answer và ICE candidate. WebRTC **không** quy định kênh signaling |
| **ICE** (+ STUN, TURN) | Tìm đường đi giữa hai đầu qua NAT/firewall |
| **DTLS** | Bắt tay mã hoá, trao đổi khoá |
| **SRTP** | Mã hoá media (audio) trên RTP |
| **RTP/RTCP** | Đóng gói audio theo thời gian, đánh số thứ tự, đồng hồ, báo cáo chất lượng |
| **Opus** | Codec audio mặc định (6–510 kbps, 2,5–60 ms frame), FEC trong băng và PLC |
| **Jitter buffer, PLC, NetEq** | Hấp thụ jitter và che mất gói |
| **AEC, NS, AGC** | Xử lý front-end tích hợp (Chương 7) |
| **DataChannel** (SCTP over DTLS) | Kênh dữ liệu, có thể cấu hình tin cậy hoặc không, có thứ tự hoặc không |

### 8.6.2 ICE, STUN, TURN: vì sao cần

Hầu hết thiết bị nằm sau NAT, không có địa chỉ công khai trực tiếp.

```text
Client (192.168.1.5, sau NAT) ──?──► Server (203.0.113.10)
```

- **Host candidate:** địa chỉ nội bộ. Chỉ dùng được trong cùng mạng.
- **STUN:** server giúp client biết **địa chỉ công khai (server-reflexive)** của mình. Đủ với đa số NAT.
- **TURN:** **relay** toàn bộ media qua server trung gian khi không thể đi thẳng (NAT đối xứng, firewall chặn UDP). Tốn băng thông relay nhưng chắc chắn thông.
- **ICE:** quy trình thử tất cả candidate theo ưu tiên và chọn đường tốt nhất.

Thực tế trong wiki: server HF cấu hình ICE bằng env JSON `SPEECH_TO_SPEECH_ICE_SERVERS`; mặc định aiortc dùng host candidate cộng STUN của Google; nơi client không với tới server trực tiếp (NAT đối xứng, container không mở UDP) **cần TURN**. Demo trình duyệt dùng host candidate mặc định và **không có TURN relay dự phòng**.[^s2s-engine][^browser-demo] Hệ quả: một demo chạy tốt trên LAN có thể không kết nối được qua mạng công ty hoặc 4G nếu không cấu hình TURN. Hãy lên kế hoạch TURN ngay nếu mục tiêu là Internet.

### 8.6.3 Luồng kết nối điển hình

```text
Browser                         Signaling (HTTP)                  Server
  │  tạo RTCPeerConnection, thêm track mic, mở DataChannel "oai-events"
  │  createOffer() → SDP offer
  │ ───────── POST /v1/realtime/calls (SDP offer) ─────────────────►│
  │ ◄──────── 201 Created + SDP answer + Location: .../calls/{id} ───│
  │  setRemoteDescription(answer)
  │ ◄══════ ICE + DTLS ═══════════════════════════════════════════►│
  │ ══════ RTP/SRTP Opus (mic) ═══════════════════════════════════►│
  │ ◄═════ RTP/SRTP Opus (giọng bot) ═══════════════════════════════│
  │ ◄═════ DataChannel: JSON events (cùng giao thức như WebSocket) ►│
```

Trích từ wiki (Reported): handshake GA là `POST /v1/realtime/calls` với SDP offer, trả `201` cùng header `Location: /v1/realtime/calls/{call_id}`; audio chạy trên RTP (Opus 48 kHz, được resample về/từ 16 kHz của pipeline bằng resampler có trạng thái); mọi sự kiện JSON đi qua data channel `oai-events`; transport phát frame RTP 20 ms và phát im lặng khi rảnh.[^s2s-engine] Điểm cần chú ý khi chuyển từ WebSocket sang WebRTC:

- `input_audio_buffer.append` **bị từ chối** (`invalid_event_for_transport`) vì audio đã đi qua media track.[^s2s-engine]
- Có sự kiện chỉ dành cho WebRTC, `output_audio_buffer.clear`, để flush audio đã đệm phía server khi barge-in.[^s2s-engine]
- `session.created` gửi khi data channel mở chứ không phải khi kết nối.[^s2s-engine]
- Demo trình duyệt: noise gate nằm trong worklet của WebSocket, nên WebRTC gửi mic thô; replay ghi âm chỉ dùng được với WebSocket; chế độ load-balancer chỉ có WebSocket.[^browser-demo] Nghĩa là **hai transport không hoàn toàn tương đương về tính năng**; đừng giả định chúng hoán đổi được mà không kiểm thử.

### 8.6.4 Những gì WebRTC làm thay bạn (trả lời Q2)

| Vấn đề | WebSocket | WebRTC |
|---|---|---|
| **Mất gói** | TCP gửi lại → tăng trễ, dồn cục | Opus **PLC** che mất gói; **FEC** (in-band FEC, RED) sửa nhẹ; không chờ |
| **Jitter** | Không có jitter buffer; tự cài ở client | **NetEq/jitter buffer** thích ứng sẵn |
| **NAT/firewall** | Dễ (HTTP/443) nhưng kết nối đi qua server | **ICE/STUN/TURN**; P2P hoặc qua SFU |
| **AEC/NS/AGC** | Tuỳ `getUserMedia` constraints, vẫn dùng được | Tích hợp, và AEC có **tín hiệu tham chiếu chính xác** từ đường phát WebRTC |
| **Mã hoá** | `wss://` (TLS) | DTLS-SRTP bắt buộc |
| **Điều chỉnh bitrate** | Không | Có (congestion control: GCC, REMB/TWCC) |
| **Độ phức tạp** | Thấp | Cao (signaling, ICE, TURN, SFU) |

Điểm AEC đáng nhấn mạnh với Chương 7: AEC hoạt động tốt nhất khi audio phát ra loa đi qua **cùng một đường audio của trình duyệt** để tín hiệu tham chiếu chính xác và đồng bộ. Với WebSocket + AudioWorklet phát tự quản, trình duyệt có thể không dùng audio đó làm tham chiếu đúng cách hoặc độ trễ khác nhau; tài liệu thiết kế vì vậy xếp "AEC ở tầng WebRTC" vào tầng production.[^design] Điều này là **Synthesis** từ nguyên lý AEC; hãy kiểm tra trên trình duyệt thực tế của bạn.

### 8.6.5 Cái giá của WebRTC cho voice agent

- **Server phải xử lý media**: giải mã Opus, resample 48 kHz → 16 kHz, mã hoá Opus ngược lại. Với Python có thể dùng aiortc (như wiki mô tả) và cần extra cài thêm; thiếu thì endpoint `/v1/realtime/calls` trả `501`.[^s2s-engine][^browser-demo]
- **Resample và codec thêm độ trễ nhỏ** (frame Opus 20 ms + jitter buffer 20–100 ms thích ứng).
- **Audio Opus là lossy**: audio đến ASR đã qua nén. Với giọng nói ở bitrate hợp lý tác động thường nhỏ, nhưng nó **không phải** audio gốc; nếu bạn so sánh WER giữa đường WebSocket-PCM và WebRTC-Opus, hãy coi đó là một biến số riêng, không phải giả định "giống nhau" (chưa có số đo trong wiki).
- **Gỡ lỗi khó hơn**: ICE thất bại có nhiều nguyên nhân; cần `chrome://webrtc-internals`, log ICE, thử TURN.
- Docker: WebRTC được dial **phía server** từ trong container nên `host.docker.internal` hoạt động, còn WebSocket được dial **phía trình duyệt** nên không; một `SPEECH_TO_SPEECH_URL` duy nhất chỉ làm một transport chạy được.[^browser-demo] Đây là bài học vận hành hay gặp, đáng nhớ khi triển khai container.

### 8.6.6 P2P, SFU và MCU

```text
P2P:  Client ◄──────────► Server (agent)       1-1, đơn giản; agent là một "peer"
SFU:  Client ──► [SFU] ──► Agent               SFU chuyển tiếp (không trộn); mở rộng, ghi âm, nhiều người
MCU:  trộn media phía server                    tốn CPU, hiếm cho voice agent
```

- **P2P với agent làm peer** (cách engine HF làm): đơn giản nhất cho 1 người – 1 bot.
- **SFU** (LiveKit, Daily): hợp khi có nhiều người tham gia, cần ghi âm, phân phối theo vùng, tích hợp SIP. Wiki ghi LiveKit Agents dùng WebRTC SFU và SIP, Pipecat dùng WebRTC (Daily, SmallWebRTC), WebSocket và telephony; FastRTC chạy WebRTC qua Gradio.[^frameworks] Route MVP mà báo cáo đề xuất là Pipecat + SmallWebRTC.[^frameworks]
- Dùng framework đồng nghĩa với việc **thuê** việc làm signaling, TURN, jitter handling và xử lý barge-in; đổi lại bạn phải tuân theo mô hình service/frame của nó.

---

## 8.7 HTTP streaming, SSE và huỷ request 🟡

### 8.7.1 Khi nào HTTP đủ dùng

Không phải mọi phần đều cần socket hai chiều. Giữa các service nội bộ trong **cascade** (client ↔ orchestrator ↔ ASR/TTS/LLM), HTTP thường đơn giản hơn:

| Kiểu | Cơ chế | Ví dụ dùng |
|---|---|---|
| **Request/response thường** | Gửi cả file, nhận cả kết quả | `POST /v1/audio/transcriptions` cho một lượt nói đã cắt xong |
| **Chunked transfer** | Server trả body từng mảnh, không biết trước Content-Length | `POST /v1/audio/speech` trả PCM chunked |
| **SSE (Server-Sent Events)** | Luồng sự kiện `text/event-stream` một chiều, giữ kết nối | TTS trả sự kiện chứa audio base64; token LLM streaming |
| **WebSocket** | Hai chiều | ASR streaming, voice chat |

### 8.7.2 Streaming TTS qua HTTP

VieNeu `POST /v1/audio/speech` trả **audio raw chunked hoặc SSE**; các framework như Pipecat, LiveKit Agents có thể dùng bằng cách đổi `base_url`, `response_format="pcm"`, và thêm `sample_rate` nếu framework giả định 24 kHz trong khi VieNeu mặc định 48 kHz.[^vieneu-api] Ngược lại, tập con tương thích của NeMo-Speech.cpp **đệm toàn bộ audio rồi mới trả HTTP response**, nên **không** stream TTS qua `/v1/audio/speech`; các route phát trực tiếp nằm ở WebSocket VoiceChat.[^nemo-api] Điều này cho thấy: "OpenAI-compatible" không bảo đảm có streaming; phải đọc chi tiết từng backend.

### 8.7.3 Huỷ request = đóng connection

Với HTTP, cách huỷ là **đóng kết nối** (client abort). Hệ quả cần thiết kế:

- Server phải **phát hiện** client ngắt (ví dụ ASGI `request.is_disconnected()`, hủy task) và **dừng sinh** audio. Nếu không, GPU vẫn chạy cho một audio không ai nghe.
- Việc huỷ phải xuyên suốt: engine HF ghi rõ huỷ vẫn hoạt động trong lúc thiết lập kết nối, upload và đọc phản hồi, và dọn dẹp transport hoàn tất trước khi tái sử dụng worker để upload bị kẹt không làm chậm phiên mới đến hết timeout HTTP.[^backends]
- Giới hạn: đóng connection **chậm** hơn một sự kiện `response.cancel` rõ ràng, vì cần được phát hiện qua tầng mạng và phụ thuộc vào buffer phía trên.
- Với `fetch` ở trình duyệt, dùng `AbortController`; với Python `httpx`/`aiohttp` huỷ task hoặc đóng response.

### 8.7.4 HTTP/2, HTTP/3

HTTP/2 ghép nhiều stream trên một kết nối TCP, nhưng vẫn có HOL ở tầng TCP; HTTP/3 (QUIC, UDP) loại bỏ HOL giữa các stream. Với voice agent, ít khi đây là điểm nghẽn đầu tiên; hãy biết để đọc tài liệu, không cần tối ưu sớm.

---

## 8.8 Telephony 🟡 (mức khái niệm)

Nếu agent trả lời điện thoại, đường audio đi qua mạng viễn thông:

| Khái niệm | Nội dung |
|---|---|
| **PSTN/SIP** | SIP (Session Initiation Protocol) là giao thức báo hiệu cuộc gọi VoIP; audio đi qua RTP |
| **G.711** | Codec mức 8 kHz, 64 kbps, hai biến thể **μ-law** (Mỹ/Nhật) và **A-law** (châu Âu và nhiều nơi khác); nén phi tuyến 8 bit/mẫu |
| **Băng hẹp** | 8 kHz → thông tin tới ~4 kHz; mất nhiều dải trên 4 kHz (Chương 2); âm xát như /s/, /f/ kém rõ |
| **Đa kênh** | Có thể mono hai chiều hoặc stereo mỗi phía một kênh |
| **Cổng** | Cần SIP trunk hoặc nhà cung cấp (Twilio, LiveKit SIP...) để nối PSTN với agent |

Tác động lên pipeline:

1. **ASR phải xử lý 8 kHz.** Các model huấn luyện ở 16 kHz cần **upsample** đầu vào (không thêm thông tin, nhưng đúng định dạng); chất lượng thường giảm so với 16 kHz băng rộng. Wiki có nhóm nội dung cộng đồng về STT cuộc gọi nhiễu; chi tiết nên xem ở [Community Noisy-Call STT](../wiki/community-noisy-call-stt.md).
2. **μ-law/A-law cần giải nén** về PCM16 tuyến tính trước khi đưa vào model.
3. **TTS** có thể cần hạ sample rate về 8 kHz và mã hoá lại. Lưu ý một số engine chỉ nhận 8000–96000 Hz đầu vào (ví dụ NeMo hỗ trợ WAV 8–96 kHz và bước chuẩn hoá nội bộ).[^nemo-api]
4. **Độ trễ cộng thêm** của mạng điện thoại và gateway làm ngân sách latency chặt hơn.

Phần này chỉ ở mức khái niệm; tài liệu thiết kế chưa chọn telephony làm profile MVP.

---

## 8.9 Giao thức tầng ứng dụng: OpenAI Realtime và REST audio

### 8.9.1 Hai họ giao diện

| Họ | Ví dụ | Đặc điểm |
|---|---|---|
| **REST theo từng chức năng** | `POST /v1/audio/transcriptions`, `POST /v1/audio/speech` | Mỗi call một việc; dễ ghép cascade; có thể stream chunked |
| **Realtime session (WebSocket/WebRTC)** | OpenAI Realtime API | Một phiên giữ lâu; sự kiện hai chiều; chứa VAD, ngắt lời, tool call |

### 8.9.2 `/v1/audio/transcriptions` và `/v1/audio/speech`

Theo tài liệu NeMo-Speech.cpp (Reported):

- `/v1/audio/transcriptions`: multipart, trường `file` là WAV; `response_format` gồm `json` (mặc định), `verbose_json`, `text`, `srt`, `vtt`; `verbose_json` thêm `words[]` với thời gian và độ tin cậy.[^nemo-api]
- `/v1/audio/speech`: JSON với `input`, `model`, `voice`, `speed`, `response_format` (`wav`/`pcm`); trong tập con này `speed` chỉ nhận `1.0`, và `model` được chấp nhận để tương thích nhưng server chỉ có một model đang tải.[^nemo-api]

Những chi tiết này minh hoạ điều cốt lõi: tham số `model` **không** chuyển model; `voice: "alloy"` **không** cho giọng OpenAI mà là bí danh tới giọng mặc định cục bộ.[^nemo-api]

### 8.9.3 Thế nào gọi là "OpenAI-compatible"

Tương thích là một **phổ**, không phải nhị phân:

| Mức | Nghĩa là | Ví dụ trong wiki |
|---|---|---|
| Đường dẫn + JSON schema | SDK gọi được, đổi `base_url` | Cả NeMo và VieNeu |
| Tập tham số | Chỉ nhận một **tập con**, tham số khác bị bỏ hoặc trả 400 | `speed` ≠ 1.0 trả 400 ở NeMo |
| Hành vi streaming | Có/không stream | NeMo đệm hết; VieNeu chunked/SSE |
| Định dạng audio mặc định | Sample rate/format khác nhau | VieNeu 48 kHz, NeMo 22,05 kHz hoặc 24 kHz |
| Ngữ nghĩa sự kiện | Sự kiện Realtime có đủ và đúng thứ tự không | HF s2s: Realtime **GA** cho phiên bản của họ; NeMo VoiceChat: giao thức Riva VoiceChat |

Lời khuyên thực dụng: viết một **bộ kiểm tra tương thích tối thiểu** (contract test) cho từng backend: gọi với `response_format=pcm`, kiểm sample rate thật, kiểm streaming bằng cách đo thời điểm byte đầu tiên, kiểm cancel. Engine HF còn tự **kiểm tra lúc khởi động** bằng cách phiên âm 1 s im lặng qua endpoint cấu hình, để lỗi endpoint/auth/model/format ngăn nhận phiên ngay từ đầu thay vì vỡ giữa cuộc hội thoại.[^backends]

### 8.9.4 Hai giao thức realtime khác nhau trong wiki: đừng nhầm

Tài liệu thiết kế nhấn mạnh (§5.7): giao thức transcription realtime của NeMo-Speech.cpp **không phải** OpenAI Realtime API.[^nemo-api] Cụ thể:

| Đặc tính | NeMo `/v1/audio/transcriptions/realtime` | NeMo VoiceChat `/v1/realtime` | HF s2s Realtime (GA) |
|---|---|---|---|
| Mục đích | Chỉ ASR streaming | Hội thoại song công đầy đủ | Pipeline cascade qua giao thức Realtime |
| Audio vào | Binary PCM16 hoặc base64 append, kết thúc bằng `commit` | binary hoặc base64 append; PCM16 16–48 kHz | `input_audio_buffer.append` (base64 PCM, WebSocket) hoặc media track (WebRTC) |
| Audio ra | Không | base64 PCM16 24 kHz, gói 80 ms | `response.output_audio.delta` |
| Sự kiện chính | `...input_audio_transcription.delta/completed` | `response.*`, `input_audio_buffer.speech_started/stopped` | `response.*`, `speech_started/stopped`, tool call |
| Huỷ | `input_audio_buffer.clear`, `response.cancel` | — | `response.cancel`, VAD tự huỷ (`turn_detected`) |

Nguồn: [NeMo API](../wiki/nemo-speech-http-api.md) và [Realtime Engine](../wiki/speech-to-speech-realtime-engine.md) (Reported). Cột cuối của hàng "Huỷ" của VoiceChat để trống vì trang wiki không mô tả cụ thể, đây là giới hạn bằng chứng, không phải kết luận rằng nó không có.

### 8.9.5 Các sự kiện Realtime đáng biết

Từ engine HF (Reported):[^s2s-engine]

```text
Client → Server:  session.update | input_audio_buffer.append | conversation.item.create
                  conversation.item.truncate | response.create | response.cancel
Server → Client:  session.created/updated | input_audio_buffer.speech_started/stopped
                  conversation.item.input_audio_transcription.delta/completed
                  response.created | response.output_audio.delta/done
                  response.output_audio_transcript.delta/done
                  response.function_call_arguments.done | response.done | error
```

Một vài quy ước cần nhớ khi viết client:

- **Transcript completed là nguồn đúng**: delta chỉ thêm vào (append-only), không có sự kiện rút lại; khi nhận `completed`, thay hẳn phần đã hiển thị theo `item_id`.[^s2s-engine]
- **Thứ tự kết thúc phản hồi:** `response.output_audio.done` → `response.output_audio_transcript.done` → `response.done`.[^s2s-engine]
- **Huỷ:** khi VAD thấy người dùng nói trong lúc bot đang nói, server phát lần lượt `response.output_audio.done`, transcript `.done`, `response.done(status="cancelled", reason="turn_detected")`, `input_audio_buffer.speech_started`, rồi mới tăng generation và xả hàng đợi.[^s2s-engine] Thứ tự được quy định rõ để client biết **chắc** khi nào ngừng phát.
- `conversation.item.truncate` trong engine HF chỉ được nhận như **no-op** (lịch sử phía server không bị cắt), vì phát lại do client quản lý; client demo vẫn gửi truncate dựa trên số mẫu đã render thật để tương thích SDK.[^s2s-engine][^browser-demo]

---

## 8.10 Huỷ, thứ tự và `generation_id` xuyên qua transport

Barge-in đòi hỏi **cả server và client** loại bỏ audio cũ. Transport quyết định cách làm:

| Transport | Cách flush audio đang bay | Rủi ro |
|---|---|---|
| WebSocket | Server gửi `client.clear(generation_id)`; client xoá playback queue và bỏ chunk có generation cũ đến muộn | Chunk đã ở socket buffer vẫn đến sau `clear` → phải lọc theo `generation_id` |
| WebRTC | Server xoá buffer gửi (`output_audio_buffer.clear`); RTP đã gửi đi vẫn nằm trong jitter buffer của trình duyệt | Còn một đuôi ngắn (jitter buffer) không flush được từ xa |
| HTTP | Đóng connection | Phát hiện chậm hơn; chunk đã nhận phải được client xoá riêng |

Nguyên tắc:

1. **Mọi chunk audio phải mang (hoặc thuộc về) `generation_id`.** Engine HF gắn `cancel_generation` vào mỗi chunk và sự kiện; send loop bỏ output cũ khi đang `discarding`.[^s2s-engine] Cơ chế này là mô hình tham khảo tốt: bộ đếm generation tăng khi huỷ, mọi producer kiểm tra "đã cũ chưa" cho từng token/chunk.
2. **Control và audio đi chung ngữ cảnh thứ tự** (cùng một WebSocket) để `clear` không vượt mặt audio; nếu tách kênh thì cần `generation_id` làm khoá phân xử.
3. **Client là nơi cuối cùng quyết định "đã phát đến đâu".** Gửi `audio.played` (offset mẫu thực đã render) để server biết phần người dùng đã **thực sự nghe** (Chương 6), dùng cho cắt lịch sử hội thoại và cho credit backpressure ở §8.5.3.
4. **Huỷ không chỉ là xoá buffer**: còn phải dừng LLM và TTS đang sinh (tiết kiệm tài nguyên); xem Chương 17 (turn-taking và cancellation).

---

## 8.11 Bảo mật và vận hành transport (liên quan §9.5)

- **Luôn dùng `wss://` và HTTPS** ngoài loopback. Micro trên trình duyệt (`getUserMedia`) còn yêu cầu **secure context** (HTTPS hoặc localhost); không có HTTPS thì không xin được quyền mic ở hầu hết trường hợp.
- **Xác thực:** token ngắn hạn do server cấp; đừng nhúng khoá dài hạn vào client (§8.4.6).
- **Giới hạn tài nguyên:** số phiên đồng thời, kích thước message tối đa, thời lượng phiên tối đa, tốc độ frame tối đa; rate-limit theo IP/tài khoản. Engine HF trả lỗi `session_limit_reached` khi hết slot trong pool.[^s2s-engine]
- **CORS và Origin:** WebSocket **không** bị chính sách CORS chặn; hãy kiểm tra header `Origin` ở server nếu cần chống cross-site WebSocket hijacking. (Kiến thức bảo mật chung, không từ wiki.)
- **Riêng tư audio:** audio là dữ liệu cá nhân (có thể suy ra danh tính qua giọng). Không ghi log audio thô; che giá trị nhạy cảm trong log; xem §9.5 của tài liệu thiết kế.
- **Giám sát:** log và metric theo phiên: số frame uplink/downlink, số frame bị bỏ, `bufferedAmount`, RTT, thời gian từ `speech_stopped` đến byte audio đầu tiên (xem Chương 20 về latency).

---

## 8.12 Cây quyết định chọn transport

```text
Mục tiêu hiện tại?
├─ MVP, LAN/loopback, một người dùng, cần chạy nhanh
│     → WebSocket, PCM16 16 kHz mono, binary 20–32 ms, playback queue + generation_id (Profile A)
├─ Web qua Internet / mobile, cần barge-in, loa ngoài
│     → WebRTC (Opus, AEC, jitter buffer) + TURN; control qua DataChannel
│        ├─ 1 người – 1 bot, tự dựng → P2P với aiortc/Pipecat SmallWebRTC
│        └─ nhiều người, ghi âm, SIP, mở rộng → SFU (LiveKit/Daily)
├─ Gọi điện thoại
│     → SIP trunk + G.711 8 kHz; upsample trước ASR; chấp nhận chất lượng băng hẹp
├─ Giữa các service nội bộ (orchestrator ↔ ASR/TTS)
│     → HTTP streaming (chunked/SSE) hoặc WebSocket; huỷ bằng đóng connection / sự kiện cancel
└─ Cần tương thích SDK OpenAI Realtime
      → Realtime GA subset qua WebSocket hoặc WebRTC; viết contract test cho từng backend
```

Gợi ý lộ trình: bắt đầu bằng WebSocket vì dễ gỡ lỗi (xem được frame bằng công cụ); thiết kế tầng "transport adapter" tách khỏi pipeline để sau này thêm WebRTC mà không sửa ASR/LLM/TTS. Engine HF làm đúng như vậy: cùng một `RealtimeService` và `PipelineUnit` phục vụ cả WebSocket lẫn WebRTC, chỉ khác lớp truyền.[^s2s-engine]

---

## 8.13 Lỗi thường gặp

| Triệu chứng | Nguyên nhân thường gặp | Cách kiểm |
|---|---|---|
| Giọng bot nhanh/chậm bất thường | Sai sample rate downlink (ví dụ 48 kHz phát như 24 kHz) | In sample rate khai báo vs thực tế; Chương 2 |
| Bot khựng, rồi tràn ra một cục | HOL trên TCP, mạng mất gói | Đo `bufferedAmount`, so thời gian đến chunk; thử WebRTC |
| Bot vẫn nói sau khi người dùng ngắt | `clear` đến sau chunk cũ; thiếu lọc `generation_id`; audio đã nằm trong jitter buffer | Log generation từng chunk và thời điểm `clear` |
| RAM server tăng dần khi client chậm | Hàng đợi không chặn; `send` không `await` | Đặt `maxsize`, theo dõi độ sâu hàng đợi |
| Kết nối "chết lặng" sau vài phút | NAT/proxy đóng kết nối rảnh, thiếu ping | Bật ping/pong, theo dõi close code |
| WebRTC chạy ở LAN nhưng không kết nối ở nơi khác | Thiếu TURN, NAT đối xứng, chặn UDP | `webrtc-internals`, thử với TURN |
| `501` ở `/v1/realtime/calls` | Chưa cài extra webrtc | Kiểm cài đặt server |
| Demo trong Docker: một transport chạy, một transport không | `host.docker.internal` phân giải khác nhau ở server và ở trình duyệt | Dùng URL riêng cho từng transport |
| SDK gọi được nhưng không stream | Backend "compatible" nhưng đệm toàn bộ | Đo thời điểm byte đầu tiên |
| Chunk TTS bị "click" | Cắt chunk không ở ranh giới mẫu, hoặc bỏ chunk giữa câu | Kiểm độ dài chunk chẵn byte; không bỏ giữa câu |
| Chuyển WebSocket → WebRTC, tính năng biến mất | Hai transport không tương đương (replay, noise gate, load balancer) | Đọc bảng khác biệt §8.6.3 |

---

## 8.14 Bài tập

1. **Đo overhead.** Viết script đo kích thước một frame 20 ms ở 16 kHz theo ba dạng: binary, base64, base64 bọc JSON. So với bảng §8.3.2 và giải thích chênh lệch.
2. **Echo server.** Dựng server WebSocket nhận frame binary 20 ms và gửi lại; ở client đo RTT trung bình, p95, p99 trên loopback, rồi thử giả lập mất gói/trễ bằng `tc netem` (Linux) để quan sát đuôi trễ của TCP. So với mô hình đồ chơi §8.2.3.
3. **Backpressure.** Cho một "TTS giả" sinh audio 3× realtime, và client phát 1×. (a) Không chặn: quan sát độ sâu hàng đợi; (b) chặn bằng `maxsize`; (c) chặn bằng credit theo `audio.played`. Đo độ trễ từ lúc gửi `clear` đến lúc client im.
4. **Contract test.** Viết bộ test cho `/v1/audio/speech` của một backend: kiểm sample rate thật của `response_format=pcm`, thời gian đến byte đầu, đóng connection giữa chừng và xác nhận server dừng sinh.
5. **Bảng so sánh sự kiện.** Lập bảng ánh xạ giữa sự kiện của NeMo VoiceChat và OpenAI Realtime GA (HF s2s): sự kiện nào có tương đương, sự kiện nào không.
6. **Thiết kế adapter.** Phác interface `Transport` (nhận frame vào, gửi audio ra, gửi control, huỷ theo generation) sao cho cùng một pipeline chạy được cả WebSocket lẫn WebRTC.

---

## 8.15 Đáp án

**Q1. Vì sao gửi binary frame thay vì base64?**
Base64 tăng 33% dữ liệu (đo thực tế: frame 20 ms @16 kHz từ 640 lên 856 byte, và 903 byte khi bọc JSON, +41%), tốn CPU encode/decode và cấp phát chuỗi ở hai đầu, và thêm bước parse JSON. WebSocket hỗ trợ sẵn binary frame nên không cần mã hoá lại. Base64 chỉ đáng dùng khi buộc phải đi qua kênh text hoặc tương thích SDK Realtime có sẵn; các server trong wiki hỗ trợ cả hai cách.

**Q2. WebRTC giải quyết những gì mà WebSocket không làm?**
- **Mất gói:** chạy trên UDP/RTP, Opus có PLC và FEC thay vì đợi gửi lại như TCP → không có HOL blocking.
- **Jitter:** jitter buffer thích ứng (NetEq) tích hợp sẵn.
- **NAT/firewall:** ICE với STUN/TURN; có thể P2P hoặc relay (WebSocket không cần vì đi qua server HTTP/443 nhưng mọi traffic đều phải vào server có địa chỉ công khai).
- **AEC/NS/AGC:** tích hợp, với tín hiệu tham chiếu chính xác từ đường phát WebRTC (Synthesis).
- Ngoài ra: mã hoá bắt buộc (DTLS-SRTP), điều chỉnh bitrate theo mạng.
Đổi lại: phức tạp hơn, cần signaling và có thể cần TURN, server phải xử lý media (Opus, resample), và audio là lossy.

**Q3. Backpressure trên WebSocket xử lý thế nào khi client chậm?**
Ba lớp: (1) **hàng đợi ứng dụng có chặn** (`maxsize`) để producer phải chờ; (2) **`await ws.send()`** đúng chỗ để buffer gửi của thư viện/kernel tự chặn producer; (3) **credit theo `audio.played`**: không gửi vượt quá `played + N giây`. Chính sách khi đầy: uplink bỏ frame cũ (kèm metric), downlink chặn producer thay vì bỏ chunk giữa câu, control không bao giờ bỏ; client chậm kéo dài thì đóng kết nối kèm mã lỗi. Phía trình duyệt, `WebSocket` không có backpressure thật nên chỉ tự kiểm `bufferedAmount`.

---

## 8.16 Tóm tắt chương

- Audio realtime yêu cầu **trễ thấp và ổn định**. **TCP** cho độ tin cậy nhưng có **HOL blocking**, **UDP/RTP** chấp nhận mất để giữ độ trễ.
- **WebSocket** là đường MVP: text cho control, **binary** cho audio, handshake khai báo định dạng, frame 20–32 ms, hàng đợi **có chặn**, ping/keepalive, reconnect với backoff.
- **Backpressure** là bắt buộc ở downlink: hàng đợi có chặn + `await send` + credit dựa trên `audio.played`; lượng audio đang bay càng nhỏ thì barge-in càng nhạy.
- **WebRTC** cho Internet/mobile: ICE/STUN/TURN, SRTP, Opus, jitter buffer, PLC/FEC, AEC; đổi lại phức tạp, cần TURN và server xử lý media. Dùng **SFU** (LiveKit, Daily) khi nhiều người/ghi âm/SIP.
- **HTTP streaming** (chunked, SSE) hợp giữa các service nội bộ; huỷ bằng đóng connection, nhưng chậm hơn sự kiện cancel rõ ràng.
- **Telephony** là 8 kHz G.711: upsample cho ASR, chấp nhận chất lượng băng hẹp.
- "**OpenAI-compatible**" là một phổ: kiểm từng backend về tham số, streaming, sample rate và sự kiện; viết contract test. Giao thức realtime của NeMo-Speech.cpp khác OpenAI Realtime API.
- Mọi chunk audio mang `generation_id`; control và audio chung ngữ cảnh thứ tự để huỷ chắc chắn.

**Chương tiếp theo:** Chương 9. Nền tảng ML cho speech, đủ để đọc model card (Phần IV).

---

## Giới hạn và điểm chưa kiểm chứng

- Các mô tả giao thức của HF s2s và NeMo-Speech.cpp là **Reported** từ tài liệu dự án qua wiki; chưa chạy server hay client ở đây. Trạng thái chủ đề có thể đổi theo phiên bản (các trang wiki gắn `stale_after`).
- Mô phỏng ở §8.2.3, §8.3.2, §8.5.1 là **mô hình đồ chơi/tính toán**: mất gói độc lập, RTT cố định, không có congestion control hay bufferbloat. Không dùng để dự báo độ trễ mạng thật.
- Trang wiki không có số đo WER/độ trễ giữa WebSocket-PCM và WebRTC-Opus; mọi khẳng định về chênh lệch là **Unverified**.
- Mô tả VoiceChat của NeMo về cơ chế huỷ chỉ ở mức wiki cung cấp; chưa đối chiếu với đặc tả Riva VoiceChat.
- Các con số về bitrate Opus, thông số SIP/G.711, hành vi API trình duyệt (`WebSocket`, `WebSocketStream`, secure context) là kiến thức giáo trình/nền tảng, nên kiểm lại với tài liệu hiện hành.
- Code Python/JavaScript chưa chạy; thư viện (`websockets`, aiortc) và API có thể khác theo phiên bản.

---

[^design]: [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md), §5.1 (bảng transport: WebRTC Opus cho production, WebSocket PCM16 16 kHz mono binary 20–32 ms cho MVP; "tầng 3: AEC ở WebRTC").
[^s2s-engine]: [Speech-to-Speech Realtime Engine](../wiki/speech-to-speech-realtime-engine.md), các mục "Architecture and flow", "Protocol event surface", "Interruption handling", "WebRTC transport" (Reported).
[^browser-demo]: [Speech-to-Speech Browser Demo](../wiki/speech-to-speech-browser-demo.md), các mục về transport WebSocket/WebRTC, proxy `/api/calls`, Docker và playback buffer (Reported).
[^nemo-api]: [NeMo-Speech.cpp HTTP and Realtime API](../wiki/nemo-speech-http-api.md), các mục "Conventions", "Realtime transcription WebSocket", "VoiceChat WebSocket", "POST /v1/audio/speech", "Client integration" (Reported).
[^vieneu-api]: [VieNeu-TTS OpenAI-compatible Speech API](../wiki/vieneu-tts-openai-speech-api.md), phần mở đầu và mục tích hợp client Pipecat/LiveKit/Vercel AI SDK (Reported).
[^backends]: [Speech-to-Speech OpenAI-compatible Backends](../wiki/speech-to-speech-openai-compatible-backends.md), các mục về kiểm tra khởi động, huỷ trong lúc kết nối/upload, `--stt openai-realtime`/`vllm-realtime` qua WebSocket và giới hạn hàng đợi (Reported).
[^frameworks]: [Voice Agent Frameworks](../wiki/voice-agent-frameworks.md), bảng so sánh framework (cột transport) và mục MVP route (Reported).
