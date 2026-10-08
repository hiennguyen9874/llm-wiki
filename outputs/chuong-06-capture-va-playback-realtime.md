# Chương 6. Capture và playback realtime 🔴

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần III.
> **Chương trước:** [Chương 5. Ngữ âm, chữ viết và văn bản tiếng Việt](chuong-05-ngu-am-chu-viet-va-van-ban-tieng-viet.md).
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §4 (client, AudioWorklet), §5.1 (WebSocket PCM16, playback queue), §7.1 (pre-roll), §7.2 (`audio.start`, `audio.played`), §7.3 (`client.clear`, barge-in), §8.3 (playback buffer).
> **Cơ sở:** phần lớn là kiến thức chung về lập trình audio realtime (mô hình callback, ring buffer, jitter buffer, xrun, clock drift) và về Web Audio API, PortAudio/sounddevice. Những chỗ lấy từ tài liệu thiết kế hoặc wiki được ghi rõ và giữ nhãn bằng chứng (**Reported**, **Synthesis**…). Bảng quy đổi buffer, phép tính clock drift và mô phỏng pre-buffer ở §6.7.3 được chạy bằng Python 3.12.3 thuần trong lúc viết (**Reproduced**, nhưng mô phỏng là **mô hình đồ chơi**, không phải đo trên TTS thật). Lớp `PlaybackBuffer` ở §6.9.2 đã được chạy kiểm thử logic với numpy (không có thiết bị âm thanh). Code JavaScript (AudioWorklet) và ví dụ `sounddevice` **chưa chạy trên trình duyệt hay thiết bị thật trong repo này**; API Web Audio thay đổi theo trình duyệt và phiên bản, hãy kiểm tra trên môi trường của bạn.

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Giải thích được **mô hình callback** của audio I/O: vì sao phần cứng là đồng hồ chủ, và vì sao code trong callback không được block.
2. Dựng được **đường capture** trong trình duyệt (getUserMedia → AudioContext → AudioWorklet → WebSocket) và trong Python (PortAudio/sounddevice), biết sample rate thật của thiết bị là bao nhiêu.
3. Tính được **độ trễ** do từng buffer gây ra (buffer thiết bị, render quantum, frame transport, pre-buffer, jitter buffer) và biết cái nào nằm trên critical path.
4. Cài được **ring buffer**, **bounded queue** và hiểu **jitter buffer** dùng để làm gì.
5. Nhận diện và xử lý **underrun, overrun, clock drift**.
6. Thiết kế được **playback queue cho voice agent**: theo `generation_id`, có pre-buffer, flush tức thì khi barge-in, fade chống click, báo `played_sample_offset`.
7. Đo được phía client: **timestamp capture**, **thời điểm mẫu đầu tiên thực sự phát ra loa**, và voice-to-voice mà không cần đồng bộ đồng hồ client–server.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. Vì sao playback phải có queue? Underrun và overrun là gì?
- Q2. Pre-buffer 150–300 ms đổi lại được gì và mất gì?
- Q3. Làm sao flush ngay audio đang phát khi user ngắt lời?

---

## 6.1 Bức tranh tổng: hai đầu realtime của pipeline

Mọi thứ ở giữa pipeline (VAD, ASR, LLM, TTS) có thể chậm, nhanh, chạy theo lô, chờ GPU. Chỉ có **hai đầu** bị ràng buộc cứng bởi thời gian vật lý:

- **Mic (capture):** bộ ADC sinh ra đúng `fs` mẫu mỗi giây, dù code của bạn có sẵn sàng nhận hay không.
- **Loa (playback):** bộ DAC tiêu thụ đúng `fs` mẫu mỗi giây, dù code của bạn có kịp cung cấp hay không.

Chương này là về hai đầu đó: giữ cho dòng mẫu **liên tục**, **trễ thấp**, **không lệch** giữa hai thế giới: thế giới của đồng hồ phần cứng và thế giới "lúc nhanh lúc chậm" của mạng và model.

```text
                 ĐỒNG HỒ PHẦN CỨNG (cứng)                     THẾ GIỚI "BURSTY" (mềm)
mic ─ADC─► [buffer driver/OS] ─► callback/AudioWorklet ─► reblock 20 ms ─► WebSocket/WebRTC ─► gateway
                                                                                                  │
loa ◄─DAC─ [buffer driver/OS] ◄─ callback/AudioWorklet ◄─ playback queue ◄─ mạng ◄─ TTS streaming ┘
                                    ▲                          ▲
                                    │                          └─ pre-buffer, flush theo generation_id
                                    └─ phải trả về đúng N mẫu, đúng hạn, mọi lúc
```

Ở mỗi mũi tên, nhịp độ thay đổi: phần cứng chạy đều 128 hoặc 480 mẫu một lần; transport gửi 20 ms một lần; TTS trả về từng cục 80–320 ms với khoảng cách không đều; mạng thêm jitter. **Buffer là thứ hấp thụ chênh lệch nhịp độ, và mỗi buffer đều trả giá bằng độ trễ.** Toàn bộ nghề audio realtime là chọn đúng buffer, đúng kích thước, ở đúng chỗ.

Trong tài liệu thiết kế, phía client chỉ có hai dòng (**Synthesis**, §4):

```text
Client: mic + AEC (getUserMedia echoCancellation) + capture timestamp
...
bounded client queue (AudioWorklet) → playback → audio.played(offset)
```

Chương này mở hai dòng đó ra.

---

## 6.2 Mô hình callback và luật của audio thread

### 6.2.1 Phần cứng là đồng hồ chủ (pull model)

Hầu hết audio API hiện đại (CoreAudio, WASAPI, ALSA qua PortAudio, JACK, Web Audio) dùng **mô hình kéo (pull)**: driver gọi hàm của bạn mỗi khi cần một khối mới.

- **Output:** "Tôi cần 480 mẫu cho 10 ms tới, đưa ngay." Hàm callback phải điền đủ 480 mẫu và trả về trước khi buffer phần cứng cạn.
- **Input:** "Đây là 480 mẫu vừa thu được." Hàm callback phải lấy đi trước khi khối tiếp theo ghi đè.

**Hạn chót (deadline)** của mỗi callback bằng đúng thời lượng của khối: 480 mẫu @ 48 kHz = 10 ms. Nếu callback mất 12 ms, phần cứng không chờ: output phát ra im lặng hoặc rác (underrun), input mất mẫu (overrun). Hai lỗi này gọi chung là **xrun**.

Ngược lại là **mô hình đẩy (push / blocking I/O)**: code gọi `stream.write(x)` hay `stream.read(n)`, hàm block cho tới khi có chỗ hoặc có dữ liệu. Dễ viết hơn, nhưng cùng ràng buộc: nếu vòng lặp của bạn chậm hơn realtime, xrun vẫn xảy ra, chỉ là được báo dưới dạng exception hoặc cờ.

### 6.2.2 Luật của audio thread

Callback chạy trên một thread **ưu tiên cao, realtime**. Bất kỳ thứ gì có thể chờ một khoảng không xác định đều bị cấm:

| Không được làm trong callback | Vì sao | Thay bằng |
|---|---|---|
| I/O: mạng, đĩa, `print`/`console.log` | Có thể block hàng chục ms | Ghi vào ring buffer, thread khác gửi đi |
| Lấy lock mà thread khác giữ lâu | Priority inversion: audio thread chờ thread ưu tiên thấp | Lock-free SPSC ring buffer, hoặc lock rất ngắn không có I/O bên trong |
| Cấp phát bộ nhớ lớn / liên tục | Allocator và GC có thể dừng thế giới | Cấp phát trước, tái dùng buffer |
| Chạy model (VAD, ASR, resample chất lượng cao cả khối lớn) | Thời gian không xác định, có thể vượt deadline | Chạy ở worker/thread khác, callback chỉ chép mẫu |
| Gửi message dày đặc (mỗi 128 mẫu một `postMessage`) | Tạo áp lực GC, nghẽn main thread | Gom thành frame 20 ms rồi mới gửi |

Với Python, callback của `sounddevice` chạy trên thread của PortAudio nhưng phải lấy GIL; một lần GC hay một thread khác giữ GIL lâu là đủ gây xrun. Vì thế ở Python nên chọn **blocksize ≥ 10–20 ms** và để callback chỉ chép mẫu (§6.4). Trong trình duyệt, `AudioWorkletProcessor.process()` chạy trên rendering thread riêng, tách khỏi main thread. Đó là lý do AudioWorklet thay thế `ScriptProcessorNode` (đã deprecated, chạy trên main thread nên giật khi UI bận).

### 6.2.3 Quy đổi kích thước khối ra độ trễ

`thời_lượng_ms = số_mẫu / fs × 1000` (Chương 2 §2.7). Bảng tra (**Reproduced**, tính bằng Python):

| Khối | fs | Thời lượng | Gặp ở đâu |
|---|---|---|---|
| 128 | 48 kHz | 2.67 ms | Render quantum mặc định của Web Audio |
| 128 | 44.1 kHz | 2.90 ms | Như trên, thiết bị 44.1 kHz |
| 256 | 48 kHz | 5.33 ms | Buffer "low latency" của ứng dụng âm nhạc |
| 480 | 48 kHz | 10.0 ms | Chu kỳ phổ biến của WASAPI/WebRTC (10 ms) |
| 960 | 48 kHz | 20.0 ms | Frame Opus 20 ms; frame transport 20 ms |
| 1024 | 44.1 kHz | 23.2 ms | Mặc định của nhiều ví dụ PyAudio |
| 1024 | 48 kHz | 21.3 ms | Như trên |
| 2048 | 48 kHz | 42.7 ms | Buffer "an toàn" khi máy yếu |
| 512 | 16 kHz | 32.0 ms | Cửa sổ Silero VAD (không phải buffer thiết bị) |

Chú ý dòng cuối: kích thước khối của **model** không có lý do gì phải bằng kích thước khối của **thiết bị** hay của **transport**. Tài liệu thiết kế §7.1 nói rõ: "Không bắt VAD, ASR và TTS dùng chung một chunk length" (**Synthesis**). Giữa các nhịp khác nhau luôn có một **reblocker** (Chương 2 §2.7.4).

---

## 6.3 Capture trong trình duyệt: getUserMedia, AudioContext, AudioWorklet

### 6.3.1 Chuỗi đối tượng

```text
navigator.mediaDevices.getUserMedia({audio: {...}})   → MediaStream (track mic, đã qua AEC/NS/AGC của trình duyệt)
  → AudioContext                                        → đồ thị xử lý, chạy ở sample rate của context
    → MediaStreamAudioSourceNode                        → đưa track vào đồ thị
      → AudioWorkletNode("mic-capture")                 → code của bạn, chạy trên audio rendering thread
           │ port.postMessage(frame 20 ms)
           ▼
       main thread (hoặc Worker) → đổi sang PCM16 → WebSocket.send(binary)
```

Các điều kiện tiên quyết hay làm mất nửa ngày:

- **Secure context.** `getUserMedia()` chỉ chạy trên HTTPS hoặc `localhost`. Trang demo của HF s2s ghi chú `127.0.0.1` và `localhost` dùng được, còn `http://192.168.x.y` thì không (**Reported**, [Speech-to-Speech Browser Demo](../wiki/speech-to-speech-browser-demo.md)). Muốn test từ điện thoại trong LAN thì cần chứng chỉ (self-signed, mkcert) hoặc tunnel HTTPS.
- **Autoplay policy.** `AudioContext` tạo ra trước khi user tương tác sẽ ở trạng thái `suspended`. Phải gọi `ctx.resume()` trong handler của một cú click ("Bắt đầu nói chuyện"). Nếu quên, mọi thứ "chạy" nhưng không có mẫu nào đi qua.
- **Quyền mic.** User có thể từ chối; thiết bị có thể bị app khác giữ; Bluetooth có thể đổi profile giữa chừng (§6.3.5). Bắt lỗi và hiển thị rõ.

### 6.3.2 Constraints của getUserMedia

```js
const stream = await navigator.mediaDevices.getUserMedia({
  audio: {
    echoCancellation: true,     // AEC: bắt buộc nếu muốn barge-in khi dùng loa ngoài (Chương 7)
    noiseSuppression: true,     // NS: A/B test, có thể hại ASR (Chương 7)
    autoGainControl: true,      // AGC
    channelCount: 1,
    // sampleRate: 16000,       // chỉ là gợi ý; nhiều trình duyệt bỏ qua
  },
});
const settings = stream.getAudioTracks()[0].getSettings();
console.log(settings);          // xem trình duyệt THỰC SỰ áp dụng gì
```

Ba constraint `echoCancellation`, `noiseSuppression`, `autoGainControl` chính là tầng "tốt hơn" trong ba tầng chống echo của tài liệu thiết kế §5.1 (**Reported**, [Barge-in & Echo](../wiki/voice-agent-barge-in-and-echo-handling.md)). Demo của HF s2s cũng bật cả ba (**Reported**, [Browser Demo](../wiki/speech-to-speech-browser-demo.md)); report Claude khuyến nghị bật `echoCancellation` và A/B test `noiseSuppression` (**Reported**, [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md)). Chi tiết vì sao NS có thể làm ASR kém hơn để ở Chương 7.

Constraint là **yêu cầu**, không phải **cam kết**. Luôn đọc `getSettings()` và log lại; nhiều bug "ASR tệ trên máy A nhưng tốt trên máy B" hoá ra là AEC/NS bị tắt hoặc bật khác nhau.

### 6.3.3 Sample rate của thiết bị và của AudioContext

Mic trên laptop/điện thoại gần như luôn chạy ở **44.1 kHz hoặc 48 kHz**. `AudioContext` mặc định lấy sample rate của thiết bị output (thường 48 kHz). Bạn có ba lựa chọn để ra 16 kHz cho ASR:

| Cách | Ưu | Nhược |
|---|---|---|
| (a) `new AudioContext({sampleRate: 16000})`, trình duyệt tự resample mic | Không phải viết resampler; băng thông uplink nhỏ | Hỗ trợ và chất lượng khác nhau giữa trình duyệt/phiên bản; có trình duyệt từng không cho nối MediaStream vào context khác rate. Context 16 kHz cũng dùng cho playback thì TTS 24/48 kHz bị hạ băng thông |
| (b) Context ở rate thiết bị, resample **trong worklet/Worker** về 16 kHz | Kiểm soát được; một context dùng cho cả capture lẫn playback | Phải viết resampler có lọc anti-alias và **có state** (Chương 2 §2.8.4); `x[::3]` là sai |
| (c) Gửi nguyên 48 kHz (PCM16 hoặc Opus) lên, server resample bằng soxr | Client đơn giản nhất; server dùng resampler tốt | PCM16 48 kHz tốn 768 kbps (gấp 3 lần 16 kHz); ổn trên LAN, phí trên mobile |

Demo HF s2s chọn kiểu (b): worklet `mic-capture` resample từ rate của `AudioContext` về **24 kHz**, đóng gói Int16 LE, và client **chờ worklet báo đúng version và đúng rate 24 kHz** trước khi mở session (**Reported**, [Browser Demo](../wiki/speech-to-speech-browser-demo.md)). Chi tiết đáng học: **rate output của worklet là một phần của contract**, được kiểm tra trước khi gửi byte nào, và có cache key (`audio-24k-v2`) phải tăng cùng `AUDIO_WORKLET_VERSION` mỗi khi contract audio đổi (**Reported**). Đây chính là "audio contract tường minh" của tài liệu thiết kế §3 nguyên tắc 4, áp dụng ở client.

Với MVP Profile A (WebSocket PCM16 16 kHz mono, tài liệu thiết kế §5.1), lựa chọn mặc định hợp lý là (b) hoặc (c), chọn (a) chỉ khi đã test trên đúng các trình duyệt mục tiêu (**Synthesis**).

### 6.3.4 AudioWorklet cho capture

Mỗi lần `process()` được gọi, bạn nhận **một render quantum** (mặc định 128 frames mỗi kênh). Worklet gom quantum thành frame 20 ms, gắn số thứ tự mẫu, rồi gửi về main thread. Trong `AudioWorkletGlobalScope` có sẵn các biến toàn cục `sampleRate`, `currentFrame`, `currentTime`.

```js
// mic-capture.worklet.js  — chạy trên audio rendering thread
class MicCapture extends AudioWorkletProcessor {
  constructor(options) {
    super();
    const { frameMs = 20 } = options.processorOptions || {};
    this.frameLen = Math.round(sampleRate * frameMs / 1000);   // 960 @ 48 kHz
    this.pool = [];                                              // tái dùng buffer, giảm GC
    this.buf = new Float32Array(this.frameLen);
    this.n = 0;
    this.frameStart = -1;                                        // currentFrame của mẫu đầu frame
    this.port.onmessage = (e) => { if (e.data?.recycle) this.pool.push(e.data.recycle); };
  }
  process(inputs) {
    const ch = inputs[0]?.[0];
    if (!ch) return true;                  // chưa có input (mic chưa chạy) — vẫn giữ node sống
    for (let i = 0; i < ch.length; i++) {
      if (this.n === 0) this.frameStart = currentFrame + i;
      this.buf[this.n++] = ch[i];
      if (this.n === this.frameLen) {
        const full = this.buf;
        this.port.postMessage({ pcm: full, startFrame: this.frameStart, sr: sampleRate }, [full.buffer]);
        this.buf = this.pool.pop() || new Float32Array(this.frameLen);
        this.n = 0;
      }
    }
    return true;                           // trả false thì node có thể bị dừng
  }
}
registerProcessor("mic-capture", MicCapture);
```

Main thread:

```js
const ctx = new AudioContext({ latencyHint: "interactive" });
await ctx.audioWorklet.addModule("mic-capture.worklet.js");
const src = ctx.createMediaStreamSource(stream);
const cap = new AudioWorkletNode(ctx, "mic-capture", {
  numberOfInputs: 1, numberOfOutputs: 0, processorOptions: { frameMs: 20 },
});
src.connect(cap);
// Lưu ý: ở một số trình duyệt, node không nối tới destination có thể không được "kéo".
// Nếu process() không chạy: dùng numberOfOutputs: 1 và nối qua GainNode gain=0 tới ctx.destination.

const resampler = makeStreamResampler(ctx.sampleRate, 16000);    // có state, có lọc (lựa chọn b)
cap.port.onmessage = ({ data }) => {
  const x16k = resampler.push(data.pcm);                         // Float32 @ 16 kHz, độ dài thay đổi được
  ws.send(floatToPcm16(x16k));                                   // binary frame, không base64
  cap.port.postMessage({ recycle: data.pcm }, [data.pcm.buffer]); // trả buffer về pool
  captureClock.note(data.startFrame, data.sr);                   // §6.10
};

function floatToPcm16(x) {
  const out = new Int16Array(x.length);
  for (let i = 0; i < x.length; i++) {
    const v = Math.max(-1, Math.min(1, x[i]));
    out[i] = v < 0 ? Math.round(v * 32768) : Math.round(v * 32767);
  }
  return out.buffer;                     // little-endian trên mọi máy client phổ biến
}
```

Ghi chú:

- `makeStreamResampler` là chỗ bạn cắm resampler thật (thư viện WASM của libsamplerate/soxr, hoặc FIR polyphase tự viết). Đừng dùng nội suy tuyến tính để **hạ** 48 → 16 kHz: không có lọc anti-alias thì phụ âm xát `s/x` bị gập phổ (Chương 2 §2.2.3).
- `postMessage` với danh sách transfer `[buffer]` chuyển quyền sở hữu, không chép; buffer phía gửi trở thành rỗng. Vì vậy worklet phải lấy buffer mới (pool).
- Muốn tránh hoàn toàn `postMessage` trên audio thread, dùng `SharedArrayBuffer` làm ring buffer giữa worklet và Worker. Cách này yêu cầu trang ở trạng thái cross-origin isolated (header `Cross-Origin-Opener-Policy: same-origin` và `Cross-Origin-Embedder-Policy: require-corp`). Với frame 20 ms (50 message/s) thì `postMessage` là đủ cho MVP.
- Không dùng `MediaRecorder` cho đường realtime: nó cho ra blob container (WebM/Opus) chứ không phải PCM, và cắt blob ra decode từng cái là bẫy kinh điển (Chương 3 §3.5).

### 6.3.5 Những thứ trình duyệt và OS làm sau lưng bạn

- **Xử lý tín hiệu ẩn:** AEC/NS/AGC của trình duyệt, cộng thêm "voice processing" của OS (macOS, Windows có "audio enhancements", điện thoại có chế độ cuộc gọi). Hai lớp AEC chồng nhau có thể làm méo tiếng.
- **Bluetooth:** tai nghe Bluetooth khi mở mic thường chuyển từ profile nghe nhạc (A2DP) sang profile cuộc gọi (HFP/HSP), mic và loa đều tụt xuống **băng hẹp/băng rộng** (8 hoặc 16 kHz, tuỳ codec), chất lượng TTS nghe rõ là kém đi. Output Bluetooth còn thêm độ trễ lớn (thường cỡ 100–300 ms, tuỳ thiết bị, đây là con số kinh nghiệm chung, không đo trong repo này), làm barge-in "chậm" và làm AEC khó hơn.
- **Đổi thiết bị giữa chừng:** cắm tai nghe, rút tai nghe, đổi output. Sample rate của thiết bị mới có thể khác. Chrome/Edge cho đổi output trực tiếp bằng `AudioContext.setSinkId`, các trình duyệt khác giữ mặc định hệ thống (**Reported**, [Browser Demo](../wiki/speech-to-speech-browser-demo.md)). Nghe sự kiện `devicechange` và kiểm tra lại contract.
- **Tab bị ẩn / máy ngủ:** trình duyệt có thể giảm ưu tiên hoặc dừng xử lý. Một session voice cần xử lý khi tab mất focus.

---

## 6.4 Capture và playback trong Python: PortAudio/sounddevice

Client Python (CLI, robot, kiosk, edge box) thường dùng **PortAudio** qua `sounddevice` hoặc `PyAudio`. Trên Linux cần cài thư viện hệ thống: HF s2s ghi `libportaudio2` cộng `libsndfile1` trên Ubuntu; RealtimeSTT cần `portaudio19-dev`; script `record_and_predict.py` của Smart Turn cần PortAudio cho PyAudio (**Reported**, [Speech-to-Speech Pipeline](../wiki/speech-to-speech-pipeline.md), [RealtimeSTT](../wiki/realtimestt.md), [Smart Turn](../wiki/smart-turn.md)).

### 6.4.1 Tầng bên dưới

PortAudio là lớp trừu tượng trên "host API" của từng OS:

| OS | Host API | Ghi chú |
|---|---|---|
| Linux | ALSA (PulseAudio/PipeWire thường lộ ra dưới dạng thiết bị ALSA "pulse"/"pipewire"/"default"), JACK | Mở thẳng thiết bị `hw:` thì trễ thấp nhưng chiếm độc quyền và chỉ nhận rate phần cứng hỗ trợ; qua sound server thì được mix và resample |
| macOS | CoreAudio | Trễ thấp, ổn định |
| Windows | MME, DirectSound, WASAPI, WDM-KS | Ưu tiên WASAPI; chế độ exclusive trễ thấp hơn nhưng chiếm thiết bị và không tự resample |

Tham số quan trọng:

- `samplerate`: nên **hỏi thiết bị** (`sd.query_devices(kind="input")["default_samplerate"]`) rồi mở đúng rate đó, tự resample sang 16 kHz bằng soxr. Mở 16 kHz trực tiếp có khi được (sound server resample hộ), có khi báo lỗi "Invalid sample rate".
- `blocksize`: số frame mỗi callback. `0` để host tự chọn (có thể thay đổi mỗi lần). Chọn cố định (ví dụ 20 ms) để đơn giản hoá reblock.
- `latency`: `"low"`, `"high"` hoặc số giây; đây là **gợi ý** về độ trễ buffer của driver. Đọc lại `stream.latency` sau khi mở để biết giá trị thật.

### 6.4.2 Full-duplex với một stream

```python
import queue
import numpy as np
import sounddevice as sd

from playback import PlaybackBuffer          # lớp ở §6.9.2

dev_in = sd.query_devices(kind="input")
SR = int(dev_in["default_samplerate"])      # thường 48000 hoặc 44100
BLOCK = SR // 50                             # 20 ms

player = PlaybackBuffer(SR, prebuffer_ms=200)
cap_q: queue.Queue = queue.Queue(maxsize=50) # bounded: tối đa 1 s audio chờ gửi
stats = {"in_overflow": 0, "out_underflow": 0, "cap_drop": 0}
frames_captured = 0                          # đồng hồ capture tính bằng mẫu

def callback(indata, outdata, frames, time, status):
    global frames_captured
    if status.input_overflow:
        stats["in_overflow"] += 1
    if status.output_underflow:
        stats["out_underflow"] += 1
    # 1) capture: chỉ CHÉP, kèm số thứ tự mẫu và thời điểm ADC (có thể = 0 trên một số host API)
    try:
        cap_q.put_nowait((frames_captured, time.inputBufferAdcTime, indata[:, 0].copy()))
    except queue.Full:
        stats["cap_drop"] += 1               # consumer chậm: bỏ frame, KHÔNG block callback
    frames_captured += frames
    # 2) playback: luôn điền đủ `frames` mẫu
    outdata[:, 0] = player.pull(frames)

stream = sd.Stream(samplerate=SR, blocksize=BLOCK, channels=1, dtype="float32",
                   latency="low", callback=callback)
with stream:
    print("latency thật (in, out):", stream.latency)
    while True:
        idx, adc_t, x = cap_q.get()          # thread khác: resample → PCM16 → gửi lên server
        ...
```

Những điểm nên để ý:

- **Callback chỉ chép.** Không resample, không gửi mạng, không chạy VAD trong callback.
- **`queue.Full` thì bỏ frame và đếm**, không block. Mất 20 ms audio khi hệ thống quá tải còn tốt hơn làm toàn bộ audio thread đứng.
- **Một stream duplex** (cùng `sd.Stream`) đảm bảo input và output chạy cùng đồng hồ thiết bị khi chúng cùng một card. Mic USB và loa HDMI là hai đồng hồ khác nhau (§6.8).
- **Không phát từng chunk bằng `sd.play()`.** Mỗi lần gọi mở/đóng stream mới, tạo khoảng hở và tiếng click giữa các chunk. Wiki ghi nhận: helper `StreamPlayer` của faster-qwen3-tts giữ **một** output stream mở và xếp hàng chunk, còn `sounddevice.play(audio_chunk, sr)` cho mỗi chunk "có thể gây gap" (**Reported**, [Faster Qwen3-TTS](../wiki/faster-qwen3-tts.md)).
- **Client Python của HF s2s** (`local --tts openai`) mặc định đệm 196 ms trước khi phát, `--playback-buffer-ms` ghi đè, `0` tắt hẳn; buffer này nằm sau TTS và không đổi request TTS (**Reported**, [OpenAI-Compatible Backends](../wiki/speech-to-speech-openai-compatible-backends.md), [Speech-to-Speech Pipeline](../wiki/speech-to-speech-pipeline.md)).

---

## 6.5 Buffer và độ trễ thiết bị

### 6.5.1 Các lớp buffer từ mic tới server

| Lớp | Kích thước điển hình | Ai quyết định | Có thể giảm? |
|---|---|---|---|
| Buffer driver/phần cứng (input) | 1–3 period × 2.5–20 ms | OS, driver, `latency` hint | Một phần (exclusive mode, `latency="low"`) |
| Render quantum / block callback | 2.67 ms (Web Audio) hoặc blocksize của bạn | API / bạn | Có |
| Gom thành frame transport | 20 ms (thiết kế: 20–32 ms, §5.1) | Bạn | Có, nhưng frame nhỏ hơn thì overhead mạng lớn hơn |
| Resampler (độ trễ nhóm của bộ lọc) | Vài ms, tuỳ chất lượng | Thư viện | Chọn chế độ "low latency" nếu cần |
| Mạng | RTT/2 + jitter | Mạng | Không (chỉ chọn transport) |
| Reblock ở gateway (20 ms → 512 mẫu) | Trung bình ~8 ms, tối đa 16 ms (Chương 2 §2.7.4) | Bạn | Ít |

### 6.5.2 Các lớp buffer từ server tới loa

| Lớp | Kích thước điển hình | Ghi chú |
|---|---|---|
| Kích thước chunk TTS | 80–320 ms (VieNeu: chunk đầu 2 frame = 160 ms trên GPU, sau đó 4 frame = 320 ms, **Reported**) | Chunk lớn → pre-buffer bị "lượng tử hoá" (§6.7.3) |
| Mạng + jitter | 30–80 ms hoặc 50–200 ms theo hai report (**Reported**, tài liệu thiết kế §8.2) | |
| **Pre-buffer / jitter buffer của client** | 0–300 ms (§6.7) | Trực tiếp cộng vào thời gian tới âm thanh đầu tiên |
| Buffer output của trình duyệt/OS | `ctx.baseLatency` + `ctx.outputLatency` | Thường vài ms tới vài chục ms; Bluetooth lớn hơn nhiều |

Để biết độ trễ output thật trong trình duyệt:

```js
console.log("baseLatency", ctx.baseLatency, "outputLatency", ctx.outputLatency); // giây; không phải trình duyệt nào cũng báo đáng tin
```

### 6.5.3 Buffer nhỏ hay lớn?

- **Buffer thiết bị nhỏ** → trễ thấp, nhưng mỗi lần CPU bận (GC, tab khác, model chạy cùng máy) là xrun. Với voice agent, phần trễ quyết định nằm ở endpointing, ASR, LLM, TTS (hàng trăm ms, tài liệu thiết kế §8.2), không phải ở vài ms buffer thiết bị. **Đừng tối ưu buffer thiết bị xuống dưới 10 ms cho voice agent**; ổn định quan trọng hơn (**Synthesis**).
- **Buffer playback (pre-buffer)** thì khác: nó nằm trực tiếp trên critical path "mẫu speech cuối của user → mẫu audio nghe được đầu tiên" (tài liệu thiết kế §8.1). Mỗi ms pre-buffer là một ms voice-to-voice.

---

## 6.6 Ring buffer, bounded queue, jitter buffer

Ba cấu trúc này hay bị dùng lẫn tên. Phân biệt theo **mục đích**:

| Cấu trúc | Mục đích | Ở đâu trong pipeline |
|---|---|---|
| **Ring buffer** | Chuyển mẫu giữa hai thread/nhịp khác nhau với bộ nhớ cố định; giữ "N ms gần nhất" | Callback ↔ thread mạng; pre-roll 200–300 ms (§6.11); gateway "ring buffer 20 ms" (tài liệu thiết kế §4); playback worklet |
| **Bounded queue** | Giới hạn lượng việc tồn đọng giữa producer và consumer; tạo **backpressure** hoặc chính sách drop | Hàng đợi frame capture; hàng đợi câu cho TTS; queue playback |
| **Jitter buffer** | Hấp thụ thời điểm đến **không đều** của gói, phát ra dòng đều; có thể sắp lại thứ tự, che gói mất | Phía nhận của WebRTC (tự có); pre-buffer playback của client WebSocket (dạng đơn giản) |

### 6.6.1 Ring buffer

Mảng kích thước cố định, hai chỉ số đọc/ghi quay vòng. Cách cài ít bug nhất: giữ **bộ đếm tuyệt đối** (tổng số mẫu đã ghi, tổng số mẫu đã đọc), chỉ lấy modulo khi truy cập mảng.

```text
cap = 8
w (tổng đã ghi) = 11, r (tổng đã đọc) = 6  → có 5 mẫu chờ, vị trí đọc = 6 % 8 = 6
 index:  0  1  2  3  4  5  6  7
         ■  ■  ■  .  .  .  ■  ■        ■ = mẫu chưa đọc (6,7 rồi quay về 0,1,2)
```

Lợi ích của bộ đếm tuyệt đối:

- `w - r` là số mẫu đang chờ, không cần cờ "đầy/rỗng".
- `r` **chính là số mẫu đã phát**, nên `played_sample_offset` có sẵn (§6.10).
- `w` của ring buffer capture là **đồng hồ capture theo mẫu**, dùng để gắn timestamp cho VAD và pre-roll mà không phụ thuộc wall clock.

Với một producer và một consumer (SPSC), có thể cài lock-free: producer chỉ ghi `w`, consumer chỉ ghi `r`, mỗi bên đọc chỉ số của bên kia (trong JS dùng `Atomics` trên `SharedArrayBuffer`). Trong Python, GIL làm lock-free kém ý nghĩa; một `threading.Lock` giữ trong vài micro-giây là đủ (§6.9.2).

**Khi đầy thì sao?** Phải có chính sách rõ ràng:

- Ring buffer **pre-roll/lịch sử**: ghi đè cái cũ nhất (đó là mục đích của nó).
- Ring buffer **playback**: **không bao giờ ghi đè phần chưa phát**. Đầy nghĩa là producer quá nhanh hoặc capacity quá nhỏ → drop phần mới và đếm, hoặc báo backpressure (§6.6.2).

### 6.6.2 Bounded queue và backpressure

Một hàng đợi **không giới hạn** giữa producer nhanh và consumer realtime là một **rò rỉ độ trễ**: nếu consumer chậm hơn một chút, hàng đợi dài dần, độ trễ tăng mãi và không ai báo lỗi. Đó là lý do tài liệu thiết kế viết "**bounded** client queue" và "bounded playback" (§0, §4).

Hai chính sách khi queue đầy:

| Chính sách | Dùng khi | Ví dụ |
|---|---|---|
| **Drop** (cũ nhất hoặc mới nhất) | Dữ liệu chỉ có giá trị khi còn tươi | Frame capture khi gateway nghẽn: bỏ để bắt kịp hiện tại |
| **Backpressure** (producer chờ) | Mất dữ liệu là lỗi, và producer có thể chậm lại | TTS streaming: server không nên đẩy audio nhanh vô hạn |

Một điểm thiết kế đáng cân nhắc cho TTS: TTS GPU tốt có RTF ~0.5 (VieNeu 1 stream RTF 0.49, **Reported**, [VieNeu Streaming Runtime](../wiki/vieneu-tts-streaming-runtime.md)), tức sinh audio nhanh gấp đôi thời gian phát. Nếu server đẩy hết ngay khi có, client có thể đang giữ **vài giây** audio chưa phát. Khi barge-in:

- Client phải xoá vài giây đó (bắt buộc dù thế nào).
- Server đã tốn compute cho vài giây audio sẽ bị vứt.
- "Phần đã gửi" khác xa "phần đã phát", nên server **không được** dùng "đã gửi" để ghi history.

Phương án: server **pacing**, chỉ gửi trước một lượng "lead" giới hạn (ví dụ 0.5–1 s) so với vị trí phát mà client báo về qua `audio.played`. Đây là **Synthesis**, chưa đo; nó đổi một chút phức tạp lấy compute bị phí ít hơn khi ngắt và history chính xác hơn. MVP có thể bỏ qua, miễn là client flush đúng.

### 6.6.3 Jitter buffer

Gói mạng 20 ms gửi đều đặn, nhưng tới nơi lúc 18 ms, lúc 45 ms, lúc hai gói dồn một lần. Jitter buffer giữ lại một lượng D ms trước khi phát để dòng ra luôn đều:

- **Cố định:** D không đổi. Đơn giản.
- **Thích ứng:** đo jitter gần đây, tăng D khi mạng xấu, giảm D khi mạng tốt (rút ngắn bằng cách phát hơi nhanh hoặc cắt bớt khoảng lặng). Bộ NetEq của WebRTC làm việc này, kèm che gói mất (PLC); chi tiết ở Chương 8.

Với WebRTC, bạn **không tự viết** jitter buffer: nó nằm trong stack, và demo HF s2s ghi rõ tuỳ chọn startup buffer "không ảnh hưởng WebRTC" (**Reported**, [Browser Demo](../wiki/speech-to-speech-browser-demo.md)). Với WebSocket (TCP), gói không mất và không đảo thứ tự, nhưng **TCP head-of-line blocking** làm jitter có đuôi dài: một gói mất phải chờ gửi lại, các gói sau dồn lại. Pre-buffer của client WebSocket đóng vai jitter buffer đơn giản (cố định, chỉ ở đầu mỗi lượt).

Với TTS streaming, "jitter" có **hai nguồn**: mạng, và **tốc độ sinh không đều** của model (chunk sau có thể tới muộn vì GPU bận phục vụ stream khác). Nguồn thứ hai thường lớn hơn nguồn thứ nhất (§6.7).

---

## 6.7 Underrun, overrun và pre-buffer

### 6.7.1 Định nghĩa

- **Underrun (buffer cạn):** consumer cần mẫu nhưng buffer rỗng. Ở playback: phát ra im lặng giữa câu → nghe "giật", "cà lăm", hoặc click nếu tín hiệu bị cắt đột ngột. Ở capture: không áp dụng.
- **Overrun (buffer tràn):** producer cần ghi nhưng buffer đầy. Ở capture: mẫu mới bị mất hoặc ghi đè mẫu chưa đọc → âm tiết bị "nuốt", timeline lệch. Ở playback: audio TTS bị drop (nếu bounded) hoặc độ trễ phình (nếu unbounded).

Cách phát hiện:

| Nơi | Cờ có sẵn | Tự đếm |
|---|---|---|
| sounddevice/PortAudio | `status.input_overflow`, `status.output_underflow` trong callback | Số frame bị drop ở `queue.Full` |
| Web Audio | Không có cờ underrun cho worklet của bạn | Đếm số lần `process()` không đủ mẫu; so `currentFrame` giữa các lần gọi để phát hiện quantum bị bỏ |
| Server | — | Gap trong số thứ tự frame uplink; chênh lệch giữa thời lượng audio nhận được và wall clock |

Tài liệu thiết kế §10 liệt kê "TTS underrun" và "frame bị rớt" là metric phải theo dõi (**Reported**). Nghĩa là client phải **gửi các bộ đếm này về** server (cùng `audio.played` hoặc event riêng).

### 6.7.2 Vì sao underrun xảy ra với TTS streaming

Điều kiện để một lượt phát không bị giật: mọi chunk tới **trước** khi phần audio trước nó phát hết. VieNeu định nghĩa đúng đại lượng này là **lead**: audio đã nhận trừ wall time kể từ chunk đầu; lead âm nghĩa là có khoảng hở (**Reported**, [VieNeu Streaming Runtime](../wiki/vieneu-tts-streaming-runtime.md)). Các con số VieNeu báo:

- Lead tối thiểu đo được **+80 ms** trên GPU ở mọi mức tải ≤ 16 stream, **+320 ms** trên CPU (lead-in 4 frame) (**Reported**).
- Khuyến nghị client **pre-buffer 150–300 ms** để hấp thụ jitter mạng (GPU), **≥ 300 ms** trên CPU vì các tiến trình khác tranh CPU (**Reported**).
- Ở 24 và 32 stream, lead tối thiểu thành âm (−1 ms, −28 ms) (**Reported**).
- Triệu chứng "audio giật ở client" có hai nguyên nhân: không pre-buffer, hoặc RTF > 1 (**Reported**).

Ba nguyên nhân gốc của underrun TTS:

1. **RTF ≥ 1 kéo dài.** Không lượng pre-buffer hữu hạn nào cứu được: model sinh chậm hơn phát thì sớm muộn buffer cạn. Demo HF s2s nói đúng điều này: không reserve hữu hạn nào ngăn được mọi underrun khi việc sinh chậm hơn realtime kéo dài (**Reported**, [Browser Demo](../wiki/speech-to-speech-browser-demo.md)). Cách chữa là ở server (giảm tải, int8, thêm GPU), không phải ở client.
2. **RTF < 1 nhưng biến động.** Chunk sau tới muộn hơn trung bình (GPU phục vụ prefill của request khác, GC, mạng). Pre-buffer hấp thụ được.
3. **Chunk lớn, chunk đầu nhỏ.** Chunk đầu 160 ms, chunk thứ hai 320 ms cần ~160 ms để sinh ở RTF 0.5. Phát ngay chunk đầu thì chunk thứ hai phải tới trong đúng 160 ms: sát nút.

### 6.7.3 Pre-buffer mua được gì: một mô phỏng đồ chơi

Để thấy hình dạng của đánh đổi, mô phỏng một lượt TTS dài ~3.8 s (**Reproduced** bằng Python thuần, 4000 lượt mỗi ô, seed cố định; đây là **mô hình đồ chơi**, không phải VieNeu hay bất kỳ TTS thật nào):

- Thời gian sinh mỗi chunk = thời lượng chunk × RTF × (1 + nhiễu Gauss σ = 25%).
- Mạng: 20 ms cố định + jitter phân phối mũ trung bình 30 ms; giữ thứ tự (giống TCP).
- Client bắt đầu phát khi đã nhận ≥ pre-buffer ms audio (hoặc khi đã hết lượt), không rebuffer.
- "P(underrun)" = xác suất một lượt có ít nhất một khoảng hở; "chờ thêm" = thời gian trung bình từ chunk đầu tới lúc bắt đầu phát.

**Kịch bản A: chunk đầu 160 ms, các chunk sau 320 ms**

| RTF | Pre-buffer | P(underrun) | Chờ thêm |
|---|---|---|---|
| 0.5 | 0 ms | 0.507 | 0 ms |
| 0.5 | 150 ms | 0.507 | 0 ms |
| 0.5 | 300 ms | 0.000 | 161 ms |
| 0.5 | 500 ms | 0.000 | 321 ms |
| 0.9 | 0 ms | 0.966 | 0 ms |
| 0.9 | 300 ms | 0.089 | 289 ms |
| 0.9 | 500 ms | 0.000 | 577 ms |

**Kịch bản B: chunk đều 40 ms**

| RTF | Pre-buffer | P(underrun) | Chờ thêm |
|---|---|---|---|
| 0.5 | 0 ms | 0.421 | 0 ms |
| 0.5 | 100 ms | 0.024 | 52 ms |
| 0.5 | 150 ms | 0.005 | 73 ms |
| 0.5 | 300 ms | 0.000 | 154 ms |
| 0.9 | 0 ms | 0.863 | 0 ms |
| 0.9 | 100 ms | 0.222 | 79 ms |
| 0.9 | 150 ms | 0.073 | 115 ms |
| 0.9 | 300 ms | 0.000 | 258 ms |

Các bài học (**Synthesis** từ mô phỏng, cần đo lại trên hệ thật):

1. **Không pre-buffer gần như chắc chắn giật** khi có bất kỳ biến động nào, kể cả ở RTF 0.5. "Phát ngay chunk đầu" chỉ an toàn khi server đã tự giữ lead (như lead-in 4 frame của VieNeu CPU).
2. **Pre-buffer bị lượng tử hoá theo kích thước chunk.** Ở kịch bản A, pre-buffer 150 ms bằng 0 ms (chunk đầu đã 160 ms), và 300 ms thực chất là "chờ chunk thứ hai" (chờ thêm ~160 ms ở RTF 0.5). Đặt pre-buffer mà không biết kích thước chunk của backend là đặt mò.
3. **Chunk nhỏ cho đánh đổi mịn hơn**: ở B, 100–150 ms đã kéo P(underrun) xuống vài phần trăm ở RTF 0.5.
4. **RTF gần 1 đòi hỏi pre-buffer lớn hơn nhiều** cho cùng độ an toàn. Đó là lý do gate SLO đề xuất RTF P95 ≤ 0.7 (tài liệu thiết kế §8.4, **Synthesis**) có ý nghĩa với client: RTF quyết định cả pre-buffer cần thiết.
5. **Chờ thêm cộng thẳng vào voice-to-voice.** 300 ms pre-buffer có thể ăn một phần ba ngân sách ~1 s.

### 6.7.4 Chính sách pre-buffer thực tế

Từ nguồn trong wiki:

- Demo HF s2s: đếm **mẫu PCM**, không đếm thời gian trôi; sau khi đạt ngưỡng, các chunk sau phát ngay **không rebuffer**; lượt ngắn đã hoàn tất thì xả phần còn lại dù chưa đạt ngưỡng; ngắt, huỷ, lỗi, mất kết nối thì bỏ audio đang chờ. Mặc định 0 ms; issue #557 dùng 1200 ms để hết giật trong một setup TTS cục bộ, được nói rõ là ví dụ tinh chỉnh chứ không phải tối ưu chung (**Reported**, [Browser Demo](../wiki/speech-to-speech-browser-demo.md)).
- VieNeu: 150–300 ms GPU, ≥ 300 ms CPU (**Reported**).
- Client Python HF s2s: 196 ms mặc định khi dùng TTS OpenAI-compatible qua HTTP (**Reported**).

Gợi ý khởi điểm (**Synthesis**, phải đo lại):

- Pre-buffer **theo backend**, không một số cho tất cả: lấy từ `audio.start` (format, sample rate) cộng cấu hình theo `model_id`. Tối thiểu bằng kích thước chunk đầu nếu chunk đầu nhỏ hơn chunk sau.
- **"Kết thúc" mở cổng sớm:** khi server gửi `audio.end` (hoặc tương đương) mà chưa đủ pre-buffer, phát luôn. Lượt "Dạ." 400 ms không nên chờ 300 ms.
- **Thích ứng nhẹ:** mỗi underrun thì tăng pre-buffer của session thêm một bậc (ví dụ +50 ms, trần 400 ms), sau N lượt sạch thì giảm dần.
- **Không rebuffer giữa câu** là mặc định hợp lý cho voice (rebuffer tạo khoảng lặng dài hơn underrun ngắn); nhưng nếu RTF > 1 kéo dài, một lần rebuffer tại ranh giới câu nghe tự nhiên hơn một chuỗi giật. Có thể rebuffer **chỉ** khi gặp underrun ở ranh giới chunk trùng ranh giới câu.

---

## 6.8 Clock drift

### 6.8.1 Vấn đề

"48 kHz" của mic, "48 kHz" của loa, và đồng hồ của server là các bộ dao động khác nhau. Sai lệch của tinh thể thạch anh thông thường cỡ vài chục ppm (phần triệu). Quy đổi (**Reproduced**):

| Sai lệch | Mẫu lệch mỗi giây @ 48 kHz | Lệch sau 10 phút |
|---|---|---|
| 20 ppm | 0.96 | 12 ms |
| 50 ppm | 2.4 | 30 ms |
| 100 ppm | 4.8 | 60 ms |

### 6.8.2 Khi nào drift quan trọng, khi nào không

Với cascade voice agent, phần lớn trường hợp drift **vô hại** nếu bạn dùng đúng đồng hồ (**Synthesis**):

| Luồng | Có bị drift tích luỹ? | Vì sao |
|---|---|---|
| Uplink mic → server (WebSocket) | Không, nếu server tiêu thụ theo nhịp đến | Server không phát lại uplink theo đồng hồ của nó; nó chỉ xử lý mẫu khi tới |
| Timestamp trên server theo wall clock | **Có** | Server gắn "giây thứ t" bằng wall clock sẽ lệch dần khỏi số mẫu thực. Dùng **số mẫu** làm đồng hồ chính |
| Downlink TTS → loa | Không đáng kể | Mỗi lượt vài giây, và TTS sinh nhanh hơn realtime; buffer tự hấp thụ vài mẫu lệch |
| Stream liên tục hai chiều (WebRTC call, model full-duplex E2E) | **Có** | Producer và consumer chạy liên tục theo hai đồng hồ → buffer dần đầy hoặc dần cạn |
| AEC (tham chiếu loa so với mic) | **Có**, nhạy | Mic và loa khác card (USB mic + loa HDMI) → tham chiếu trôi, AEC hỏng dần (Chương 7) |

### 6.8.3 Cách xử lý khi cần

1. **Đồng hồ bằng số mẫu.** Mọi timestamp trong pipeline (VAD start/end, pre-roll, `played_sample_offset`) tính bằng chỉ số mẫu của stream tương ứng; chỉ quy ra wall clock ở biên khi cần log.
2. **Điều khiển mức buffer.** Với stream liên tục: đo mức buffer trung bình trượt; lệch khỏi mục tiêu thì chèn/bỏ một mẫu trong đoạn im lặng, hoặc resample với tỉ lệ biến đổi nhẹ (adaptive resampling, ví dụ tỉ lệ 1 ± 100 ppm).
3. **Dùng thứ đã có sẵn.** WebRTC, CoreAudio aggregate device, PipeWire đều có cơ chế bù drift. Tự viết chỉ khi tự làm audio I/O ở mức thấp.
4. **Một thiết bị cho cả mic và loa** khi có thể (§6.4.2), đặc biệt khi cần AEC.

---

## 6.9 Playback cho voice agent

Đây là phần riêng của voice agent, khác với trình phát nhạc: audio đến theo **lượt** (generation), có thể bị **huỷ giữa chừng**, và server cần biết **đã phát tới đâu**.

### 6.9.1 Yêu cầu và state machine

Yêu cầu, gộp từ tài liệu thiết kế §7.2–§7.3 (**Reported/Synthesis**) và demo HF s2s (**Reported**):

1. Mọi `audio.chunk` mang `generation_id` (và `sequence`). Client **bỏ** mọi chunk thuộc generation cũ, kể cả chunk tới **sau** lệnh clear (chúng đang bay trên mạng lúc server gửi clear).
2. `audio.start(generation_id, format, sample_rate, channels)` tới trước chunk đầu; client cấu hình resampler và pre-buffer theo đó. Output giữ sample rate gốc tới tận playback adapter (tài liệu thiết kế §7.1); VieNeu 48 kHz, Qwen3-TTS 24 kHz, nên client phải biết rate của từng backend (**Reported**, [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md)).
3. Có pre-buffer (§6.7.4), cổng mở sớm khi lượt kết thúc.
4. `client.clear(generation_id)` dừng âm thanh **ngay**, có fade ngắn, xoá toàn bộ phần chưa phát.
5. Báo `audio.played(generation_id, played_sample_offset)` định kỳ và ngay khi clear.
6. Fade-in/fade-out ở mọi chỗ tín hiệu bắt đầu hoặc dừng đột ngột (§6.9.3).

State machine tối thiểu cho một generation:

```text
             audio.start(g)                 đủ pre-buffer hoặc audio.end
   IDLE ───────────────────► BUFFERING ──────────────────────────────► PLAYING
    ▲                            │                                       │   │
    │                            │ client.clear                          │   │ hết mẫu, chưa end
    │                            ▼                                       │   ▼
    │◄──────────────────────── (xoá) ◄──────────── client.clear ─────────┘ UNDERRUN (phát im lặng,
    │                                                                         đếm, fade-out/fade-in)
    └──────────────────────── hết mẫu và đã audio.end ◄──────────────────────── PLAYING
```

### 6.9.2 Cài đặt tham khảo (Python)

Lớp dưới dùng cho client Python (§6.4.2); logic giống hệt cho AudioWorklet. Đã chạy kiểm thử logic với numpy (không có thiết bị): pre-buffer giữ im lặng tới đủ ngưỡng; fade-in ở mẫu đầu; underrun được đếm; chunk generation cũ bị bỏ; `clear` trả về offset đã phát và fade-out 5 ms; lượt ngắn đã `end` phát ngay dù dưới ngưỡng (**Reproduced**, kiểm thử logic).

```python
import threading
import numpy as np

class PlaybackBuffer:
    """Hàng đợi phát cho MỘT thiết bị output.
    Producer (thread mạng/asyncio) gọi start/push/end/clear; consumer (audio callback) gọi pull.
    Mọi bộ đếm là số mẫu tuyệt đối, vị trí trong mảng = đếm % cap."""

    IDLE, BUFFERING, PLAYING = "idle", "buffering", "playing"

    def __init__(self, sr: int, capacity_s: float = 20.0,
                 prebuffer_ms: float = 200.0, fade_ms: float = 5.0):
        self.sr = sr
        self.cap = int(capacity_s * sr)
        self.buf = np.zeros(self.cap, dtype=np.float32)
        self.r = 0                      # tổng số mẫu đã đọc (đã giao cho thiết bị)
        self.w = 0                      # tổng số mẫu đã ghi
        self.lock = threading.Lock()    # giữ rất ngắn, không I/O bên trong
        self.prebuf = int(sr * prebuffer_ms / 1000)
        self.fade = max(1, int(sr * fade_ms / 1000))
        self.state = self.IDLE
        self.gen = -1                   # generation đang phát / đang nhận
        self.min_gen = 0                # generation < min_gen bị chặn (sau clear)
        self.ended = False              # server báo hết audio của generation
        self.gen_start_r = 0            # r tại lúc bắt đầu generation
        self.need_fade_in = True
        self.stats = {"underrun": 0, "overflow_drop": 0, "stale_drop": 0}

    # ---------- phía producer ----------
    def start(self, gen: int) -> None:
        with self.lock:
            if gen <= self.gen or gen < self.min_gen:   # cũ hoặc lặp: bỏ qua
                return
            self.gen = gen
            self.r = self.w              # bỏ mọi thứ còn lại (nếu có)
            self.gen_start_r = self.r
            self.ended = False
            self.state = self.BUFFERING
            self.need_fade_in = True

    def push(self, gen: int, x: np.ndarray) -> bool:
        x = np.asarray(x, dtype=np.float32)   # đã resample về rate của thiết bị
        with self.lock:
            if gen != self.gen or gen < self.min_gen:
                self.stats["stale_drop"] += len(x)
                return False
            free = self.cap - (self.w - self.r)
            if len(x) > free:            # bounded: không bao giờ ghi đè phần chưa phát
                self.stats["overflow_drop"] += len(x) - free
                x = x[:free]
            i = self.w % self.cap
            k = min(len(x), self.cap - i)
            self.buf[i:i + k] = x[:k]
            self.buf[:len(x) - k] = x[k:]
            self.w += len(x)
            return True

    def end(self, gen: int) -> None:
        with self.lock:
            if gen == self.gen:
                self.ended = True        # cho phép phát dù chưa đủ pre-buffer

    def clear(self, new_gen: int) -> int:
        """Barge-in: chặn mọi generation < new_gen, giữ `fade` mẫu để fade-out.
        Trả về played offset của generation bị ngắt."""
        with self.lock:
            played = self.r - self.gen_start_r
            self.min_gen = max(self.min_gen, new_gen)
            if self.state == self.PLAYING:
                tail = min(self.fade, self.w - self.r)
                idx = (self.r + np.arange(tail)) % self.cap
                self.buf[idx] *= np.linspace(1.0, 0.0, tail, dtype=np.float32)
                self.w = self.r + tail   # phần còn lại bị bỏ
            else:
                self.w = self.r
            self.ended = True
            return played

    def played_samples(self) -> tuple[int, int]:
        with self.lock:
            return self.gen, self.r - self.gen_start_r

    # ---------- phía consumer (audio callback) ----------
    def pull(self, n: int) -> np.ndarray:
        out = np.zeros(n, dtype=np.float32)
        with self.lock:
            avail = self.w - self.r
            if self.state == self.BUFFERING:
                if avail >= self.prebuf or (self.ended and avail > 0):
                    self.state = self.PLAYING
                else:
                    return out
            if self.state != self.PLAYING:
                return out
            m = min(n, avail)
            idx = (self.r + np.arange(m)) % self.cap
            out[:m] = self.buf[idx]
            if self.need_fade_in and m:
                f = min(self.fade, m)
                out[:f] *= np.linspace(0.0, 1.0, f, dtype=np.float32)
                self.need_fade_in = False
            self.r += m
            if m < n:                        # hết dữ liệu
                if self.ended:
                    self.state = self.IDLE   # kết thúc bình thường
                else:
                    self.stats["underrun"] += 1
                    f = min(self.fade, m)    # fade-out phần cuối để không "click"
                    if f:
                        out[m - f:m] *= np.linspace(1.0, 0.0, f, dtype=np.float32)
                    self.need_fade_in = True # lần phát lại sẽ fade-in
                    # chính sách: tiếp tục PLAYING (không rebuffer); đổi thành
                    # self.state = self.BUFFERING nếu muốn rebuffer sau underrun
        return out
```

Ghi chú về thiết kế:

- `pull` cấp phát `np.zeros` và `np.arange` mỗi lần gọi. Với block 20 ms trong Python thì chấp nhận được; bản tối ưu nên cấp phát trước.
- `played_samples()` là số mẫu đã **giao cho thiết bị**, chưa phải đã **ra loa**: còn cộng thêm độ trễ output (`stream.latency[1]`, `ctx.outputLatency`). Khi báo `audio.played`, nên trừ phần đang nằm trong buffer thiết bị nếu cần chính xác (§6.10).
- Offset tính bằng mẫu ở **rate của thiết bị**. Contract nên quy ước `played_sample_offset` theo **rate của generation** (rate trong `audio.start`), vì server và TTS nghĩ theo rate đó. Quy đổi: `offset_src = round(offset_dev × sr_src / sr_dev)` (**Synthesis**). Demo HF s2s báo số PCM đã render theo item/content part, **không tính** startup delay và im lặng do underrun (**Reported**).

### 6.9.3 Fade và cross-fade: chống tiếng click

Một tín hiệu nhảy đột ngột từ 0.4 xuống 0 là một bước nhảy, có phổ trải rộng mọi tần số → nghe thành **click/bụp**. Các chỗ phát sinh:

| Chỗ | Cách xử lý |
|---|---|
| Bắt đầu phát một generation | Fade-in vài ms |
| Clear (barge-in) | Fade-out 5–10 ms thay vì cắt (vẫn cảm nhận là "dừng ngay") |
| Underrun giữa câu | Fade-out phần cuối có sẵn, fade-in khi có lại |
| Nối hai chunk của **cùng** stream TTS | Thường **không cần**: decoder streaming tốt nối liền mẫu. VieNeu báo streamed audio khớp decode toàn phần tới 6e-4 trên GPU và decoder CPU bit-exact, "không click ở biên chunk" (**Reported**, [VieNeu Streaming Runtime](../wiki/vieneu-tts-streaming-runtime.md)) |
| Nối hai **request** TTS độc lập (mỗi mệnh đề một request) | Mỗi request có thể bắt đầu/kết thúc với mức tín hiệu khác 0. Fade ngắn ở mỗi đầu, hoặc chèn khoảng lặng ngắn có chủ đích (như ngắt nghỉ giữa câu) |
| Đổi thiết bị/resampler giữa chừng | Fade-out, đổi, fade-in |

Độ dài fade: worklet playback của demo HF s2s dùng fade 32 frame (**Reported**, [Browser Demo](../wiki/speech-to-speech-browser-demo.md)), tức ~0.67 ms ở 48 kHz. Fade 2–10 ms là khoảng hay dùng; quá ngắn vẫn nghe "tách" nhẹ, quá dài bắt đầu ăn vào âm tiết. Fade dạng tuyến tính đủ cho fade-out/in về 0; **cross-fade** giữa hai đoạn có tín hiệu thì dùng equal-power (`cos`/`sin`) để không hụt âm lượng ở giữa.

Một cảnh báo với tiếng Việt: fade-out khi clear là đúng, nhưng **đừng fade/cắt cuối chunk** trong trường hợp bình thường; cắt đuôi âm tiết làm sai thanh (Chương 5 §5.3).

### 6.9.4 Resample downlink

Context/thiết bị 48 kHz, TTS 24 kHz (Qwen3-TTS) hoặc 48 kHz (VieNeu): cần một resampler **có state theo generation** (tạo mới ở `audio.start`, flush ở `audio.end`, vứt ở `clear`). Demo HF s2s nội suy tuyến tính 24 → 48 trong worklet (**Reported**). Nội suy tuyến tính khi **tăng** rate chấp nhận được cho thoại (ảnh phổ nhỏ, ở vùng cao), nhưng resampler có lọc tốt hơn; khi **giảm** rate (TTS 48 kHz ra thiết bị 16 kHz của tai nghe Bluetooth HFP) thì bắt buộc có lọc (Chương 2 §2.8).

### 6.9.5 AudioWorklet cho playback (phác thảo)

```js
// pcm-player.worklet.js — ring buffer Float32 ở rate của context
class PcmPlayer extends AudioWorkletProcessor {
  constructor(opts) {
    super();
    const o = opts.processorOptions;
    this.cap = Math.round(sampleRate * (o.capacityS ?? 20));
    this.buf = new Float32Array(this.cap);
    this.r = 0; this.w = 0;                      // bộ đếm tuyệt đối
    this.gen = -1; this.minGen = 0; this.genStartR = 0;
    this.state = "idle"; this.ended = false;
    this.prebuf = 0; this.fade = Math.round(sampleRate * 0.005);
    this.needFadeIn = true; this.underruns = 0; this.lastReport = 0;
    this.port.onmessage = ({ data: m }) => {
      if (m.type === "start" && m.gen > this.gen && m.gen >= this.minGen) {
        this.gen = m.gen; this.r = this.w; this.genStartR = this.r; this.ended = false;
        this.prebuf = Math.round(sampleRate * m.prebufferMs / 1000);
        this.state = "buffering"; this.needFadeIn = true;
      } else if (m.type === "chunk" && m.gen === this.gen && m.gen >= this.minGen) {
        const x = m.pcm, free = this.cap - (this.w - this.r), n = Math.min(x.length, free);
        for (let i = 0; i < n; i++) this.buf[(this.w + i) % this.cap] = x[i];
        this.w += n;
      } else if (m.type === "end" && m.gen === this.gen) {
        this.ended = true;
      } else if (m.type === "clear") {
        const played = this.r - this.genStartR;
        this.minGen = Math.max(this.minGen, m.newGen);
        if (this.state === "playing") {
          const tail = Math.min(this.fade, this.w - this.r);
          for (let i = 0; i < tail; i++) this.buf[(this.r + i) % this.cap] *= 1 - i / tail;
          this.w = this.r + tail;
        } else this.w = this.r;
        this.ended = true;
        this.port.postMessage({ type: "cleared", gen: this.gen, played, frame: currentFrame });
      }
    };
  }
  process(_, outputs) {
    const out = outputs[0][0]; out.fill(0);
    const avail = this.w - this.r;
    if (this.state === "buffering" && (avail >= this.prebuf || (this.ended && avail > 0))) {
      this.state = "playing";
      this.port.postMessage({ type: "first_sample", gen: this.gen, frame: currentFrame });
    }
    if (this.state === "playing") {
      const m = Math.min(out.length, avail);
      for (let i = 0; i < m; i++) out[i] = this.buf[(this.r + i) % this.cap];
      if (this.needFadeIn && m) { const f = Math.min(this.fade, m); for (let i = 0; i < f; i++) out[i] *= i / f; this.needFadeIn = false; }
      this.r += m;
      if (m < out.length) {
        if (this.ended) this.state = "idle";
        else { this.underruns++; this.needFadeIn = true; }   // fade-out phần cuối: lược bớt cho gọn
      }
    }
    if (currentFrame - this.lastReport >= sampleRate / 10) {  // báo ~10 lần/giây, không phải mỗi quantum
      this.lastReport = currentFrame;
      this.port.postMessage({ type: "played", gen: this.gen, played: this.r - this.genStartR,
                              underruns: this.underruns, frame: currentFrame });
    }
    return true;
  }
}
registerProcessor("pcm-player", PcmPlayer);
```

Main thread (rút gọn): nhận message WebSocket, phân loại JSON điều khiển và binary audio, resample theo generation, chuyển cho worklet, và chuyển tiếp báo cáo `played` lên server.

```js
ws.binaryType = "arraybuffer";
let curGen = -1, rs = null;
ws.onmessage = ({ data }) => {
  if (typeof data === "string") {
    const ev = JSON.parse(data);
    if (ev.type === "audio.start") {
      curGen = ev.generation_id;
      rs = makeStreamResampler(ev.sample_rate, ctx.sampleRate);           // state mới mỗi generation
      player.port.postMessage({ type: "start", gen: curGen, prebufferMs: prebufferFor(ev) });
    } else if (ev.type === "audio.end") {
      flushResampler(rs, curGen);
      player.port.postMessage({ type: "end", gen: ev.generation_id });
    } else if (ev.type === "client.clear" || ev.type === "clear") {
      player.port.postMessage({ type: "clear", newGen: ev.generation_id + 1 });
    }
    return;
  }
  // binary: [uint32 generation_id][uint32 sequence][PCM16 LE ...]  (framing ví dụ, xem Chương 8/16)
  const dv = new DataView(data), gen = dv.getUint32(0, true);
  if (gen !== curGen) return;                                              // chunk của generation cũ
  const pcm16 = new Int16Array(data, 8);
  const f32 = Float32Array.from(pcm16, (v) => v / 32768);
  const y = rs.push(f32);
  player.port.postMessage({ type: "chunk", gen, pcm: y }, [y.buffer]);
};
player.port.onmessage = ({ data }) => {
  if (data.type === "played" || data.type === "cleared")
    ws.send(JSON.stringify({ type: "audio.played", generation_id: data.gen,
                             played_sample_offset: toSourceRate(data.played) /* §6.9.2 */,
                             underruns: data.underruns }));
  if (data.type === "first_sample") metrics.markFirstAudible(data);        // §6.10
};
```

### 6.9.6 Flush khi barge-in: ai làm gì, theo thứ tự nào

Trình tự trong tài liệu thiết kế §7.3 (**Reported**, gộp từ hai report): `generation_id++` → cancel LLM → cancel TTS → xoá câu xếp hàng → gửi `{"type":"clear"}`/`audio_cancel` để client flush buffer AudioWorklet → history chỉ lưu phần đã phát, tag `[bị ngắt]` → client bỏ chunk thuộc generation cũ. Phía client, ba chi tiết quyết định chất lượng:

1. **Clear phải đi đường nhanh.** Gửi `clear` trên cùng kết nối với audio (không xếp sau hàng đợi audio phía server). Phía client, xử lý `clear` ngay khi nhận, không chờ chunk audio đang decode.
2. **Lọc theo generation ở cả hai chỗ:** main thread (không tốn công resample chunk cũ) và worklet (chặn chunk đã nằm trong hàng đợi `postMessage`).
3. **Đo cái user nghe, không đo cái server quyết định.** Barge-in latency gồm phát hiện **cộng** flush playback buffer; nên đo lúc âm thanh thật sự dừng chứ không đo sự kiện phát hiện (**Reported**, [Community Usable STT](../wiki/community-usable-stt-voice-agents.md)). Tài liệu thiết kế §7.3 cũng yêu cầu đo "user-speech → âm thanh bot dừng (nghe được)" tách khỏi thời gian giải phóng compute (**Synthesis**).

Một tối ưu tuỳ chọn (**Synthesis**, chưa đo): client có VAD nhẹ cục bộ có thể **giảm âm lượng (duck)** ngay khi thấy user nói, trước khi có quyết định barge-in từ server; nếu server xác nhận thì clear, nếu không (ho, tiếng gõ) thì khôi phục âm lượng. Cách này tiết kiệm một vòng RTT cho phản hồi cảm nhận, nhưng tạo thêm một nguồn sự thật thứ hai; đừng để client tự **huỷ** generation.

Với WebRTC, audio của bot đi trên media track, flush khi barge-in nằm **phía server** (**Reported**, [Browser Demo](../wiki/speech-to-speech-browser-demo.md)); jitter buffer của WebRTC ở client vẫn còn vài chục ms audio, thường chấp nhận được.

### 6.9.7 Từ played offset tới history

`played_sample_offset` cho biết **đã phát bao nhiêu mẫu**, không cho biết **đã nói tới chữ nào**. Tài liệu thiết kế §7.3 nói rõ: nếu không có alignment giữa token và audio, chỉ khẳng định được "played offset"; `conversation.item.truncate` của HF s2s là điểm nối tự nhiên (**Synthesis**). Demo HF s2s gửi `conversation.item.truncate` cho phần chưa nghe dựa trên số PCM worklet báo, nhưng server cục bộ hiện **nhận sự kiện truncate mà không đổi history** (**Reported**, [Browser Demo](../wiki/speech-to-speech-browser-demo.md)). Bài học: báo offset đúng ở client mới là một nửa; server phải thực sự dùng nó. Cách ước lượng text đã phát (theo chunk mệnh đề: mệnh đề nào đã phát hết; hoặc theo alignment của TTS nếu có) để ở Chương 17 và 19.

---

## 6.10 Đo phía client

### 6.10.1 Các đồng hồ trong trình duyệt

| Đồng hồ | Đơn vị | Dùng cho |
|---|---|---|
| `currentFrame` (trong worklet) | Mẫu, theo đồng hồ audio | Đánh dấu chính xác mẫu nào ở đâu |
| `ctx.currentTime` | Giây, theo đồng hồ audio | Như trên, ở main thread |
| `performance.now()` | ms, đồng hồ đơn điệu của trang | Log sự kiện, so với thời điểm nhận message mạng |
| `ctx.getOutputTimestamp()` | `{contextTime, performanceTime}` | **Cầu nối** hai đồng hồ trên |
| `ctx.outputLatency` / `baseLatency` | Giây | Từ "mẫu được render" tới "mẫu ra loa" |
| `Date.now()` | ms, wall clock | Chỉ để log; có thể nhảy (NTP) |

Nguyên tắc: đo **khoảng thời gian** trên **một** đồng hồ của **một** máy. So timestamp client với timestamp server cần đồng bộ đồng hồ (Chương 20); tránh được thì tránh.

### 6.10.2 Ba mốc cần có

1. **Capture timestamp.** Mỗi frame uplink mang `startFrame` (chỉ số mẫu đầu frame trong stream capture, §6.3.4). Quy ra thời gian client: `t = performanceTime_ref + (startFrame − frame_ref)/fs × 1000`, với cặp tham chiếu lấy từ `getOutputTimestamp()` (cùng đồng hồ audio của context). Mẫu thật sự vào mic sớm hơn một chút (độ trễ input), chênh lệch này gần như cố định nên không ảnh hưởng tới **so sánh** giữa các lượt.
2. **Mẫu đầu tiên của generation được phát.** Worklet báo `first_sample` kèm `currentFrame` (§6.9.5). Thời điểm **nghe được** ≈ thời điểm render + `outputLatency`.
3. **Played offset** định kỳ và lúc clear (§6.9.2).

### 6.10.3 Voice-to-voice không cần đồng bộ đồng hồ

Định nghĩa trong tài liệu thiết kế §8.1: từ "mẫu speech cuối của user" tới "client: mẫu audio nghe được đầu tiên". Mẫu speech cuối của user do **server** quyết định (VAD/endpoint), mẫu nghe được đầu tiên do **client** quan sát. Cách đo không cần đồng bộ (**Synthesis**):

1. Server đánh chỉ số mọi mẫu uplink (đã quy về rate gốc của client, hoặc client gửi `startFrame` trong header frame).
2. Khi VAD xác định kết thúc tiếng nói, server gửi trong `turn.commit` (hoặc event riêng) **chỉ số mẫu** của mẫu speech cuối theo stream capture, không phải wall clock của server.
3. Client quy chỉ số đó ra `performance.now()` bằng ánh xạ capture (mốc 1), quy `first_sample` ra cùng đồng hồ (mốc 2), trừ nhau.

Kết quả là voice-to-voice đo hoàn toàn trên đồng hồ client, gồm cả mạng, pre-buffer, độ trễ output. Đây là con số các panel phía server **không** cho bạn: panel "Server timings" của demo HF s2s ghi rõ đo ở server, **không gồm** buffer và playback trên trình duyệt, các stage chồng lấn nên không được cộng (**Reported**, [Browser Demo](../wiki/speech-to-speech-browser-demo.md)). `e2e` của HF s2s là từ cuối tiếng nói *ước lượng* tới audio TTS đầu tiên, không gồm playback (**Reported**, tài liệu thiết kế §5.7).

### 6.10.4 Đo độ trễ thiết bị bằng loopback

Để biết độ trễ thật của mic + loa (con số API báo không phải lúc nào cũng đúng):

- **Loopback vật lý:** phát một xung/chirp ra loa, thu bằng mic, tìm độ lệch bằng cross-correlation giữa tín hiệu phát và tín hiệu thu. Kết quả là round-trip latency của thiết bị (output + input + quãng đường âm học).
- **Vỗ tay hai nguồn:** ghi đồng thời bằng mic hệ thống và một máy ghi ngoài; so thời điểm.

Con số này cũng là đầu vào cho AEC (Chương 7) và cho việc hiểu vì sao Bluetooth làm mọi thứ chậm.

### 6.10.5 Metric client nên gửi về

| Metric | Đơn vị | Ý nghĩa |
|---|---|---|
| `v2v_client_ms` | ms | Voice-to-voice thật (§6.10.3) |
| `prebuffer_wait_ms` | ms | Thời gian chờ đủ pre-buffer mỗi lượt |
| `underrun_count`, `underrun_ms` | lần, ms | Chất lượng phát |
| `stale_chunk_drop` | mẫu | Chunk generation cũ bị bỏ (đo độ "bẩn" của cancel) |
| `barge_stop_ms` | ms | Từ lúc nhận clear tới lúc tín hiệu ra bằng 0 (sau fade) |
| `capture_drop`, `input_overflow` | frame | Mất mẫu uplink |
| `device_sr_in/out`, `outputLatency`, AEC/NS/AGC settings | — | Ngữ cảnh để chẩn đoán |

---

## 6.11 Pre-roll: đừng để mất âm tiết đầu

VAD cần vài chục tới vài trăm ms để "chắc chắn" có tiếng nói; khi nó báo `speech_start`, phần đầu âm tiết đầu tiên đã trôi qua. Nếu turn buffer chỉ bắt đầu từ `speech_start`, ASR nhận "...ông ơi" thay vì "Anh ơi", và với tiếng Việt, âm đầu và phần đầu vần mất là mất thông tin phân biệt (Chương 5 §5.3).

Giải pháp: một **ring buffer pre-roll** luôn giữ N ms gần nhất; khi VAD báo bắt đầu, turn buffer khởi tạo bằng nội dung ring buffer. Tài liệu thiết kế đặt pre-roll **200–300 ms** ở gateway (§4, §7.1), ghi rõ là thiết kế khởi điểm, chưa phải cutoff đã đo (**Synthesis**).

Pre-roll nên đặt ở **gateway** (cùng chỗ với VAD, cùng đồng hồ mẫu) chứ không ở client, trừ khi client chỉ gửi audio khi có tiếng nói (client-side VAD gating để tiết kiệm băng thông). Trong trường hợp đó, client **bắt buộc** gửi kèm pre-roll, nếu không gateway không bao giờ thấy phần đầu (**Synthesis**).

```python
import numpy as np

class PreRoll:
    """Giữ `ms` gần nhất của stream 16 kHz; ghi đè cái cũ nhất."""
    def __init__(self, sr: int = 16000, ms: int = 300):
        self.cap = sr * ms // 1000
        self.buf = np.zeros(self.cap, dtype=np.float32)
        self.w = 0                                   # tổng số mẫu đã ghi = đồng hồ mẫu
    def push(self, x: np.ndarray) -> None:
        x = x[-self.cap:]
        i = self.w % self.cap
        k = min(len(x), self.cap - i)
        self.buf[i:i + k] = x[:k]
        self.buf[:len(x) - k] = x[k:]
        self.w += len(x)
    def snapshot(self) -> tuple[int, np.ndarray]:
        """(chỉ số mẫu đầu tiên trong snapshot, mẫu theo thứ tự thời gian)."""
        n = min(self.w, self.cap)
        idx = (self.w - n + np.arange(n)) % self.cap
        return self.w - n, self.buf[idx].copy()
```

Chỉ số mẫu trả về cùng snapshot là thứ cho phép turn buffer, ASR timestamp và đo voice-to-voice (§6.10.3) nói cùng một ngôn ngữ thời gian.

---

## 6.12 Gắn với pipeline: client tham khảo

```text
┌──────────────────────────── Browser client ─────────────────────────────┐
│ [Bắt đầu] click → ctx.resume()                                          │
│ getUserMedia(AEC on, NS A/B, AGC on) → getSettings() → log              │
│   → MediaStreamSource → mic-capture worklet (frame 20 ms, startFrame)   │
│       → main/Worker: StreamResampler(ctx.sr→16k) → PCM16 → ws.send()    │
│                                                                         │
│ ws.onmessage:                                                           │
│   audio.start(gen, sr) → resampler(sr→ctx.sr), prebuffer theo backend   │
│   binary(gen, seq, pcm) → bỏ nếu gen cũ → resample → pcm-player worklet │
│   audio.end(gen)       → flush resampler, mở cổng pre-buffer            │
│   clear(gen)           → worklet: fade 5 ms, xoá, chặn gen cũ           │
│ pcm-player → played/first_sample/underruns → ws.send(audio.played)      │
│ metrics: v2v_client, prebuffer_wait, underrun, barge_stop               │
└─────────────────────────────────────────────────────────────────────────┘
```

Ánh xạ tới tài liệu thiết kế:

| Mục thiết kế | Phần trong chương |
|---|---|
| §4 Client: mic + AEC + capture timestamp | §6.3, §6.10.2 |
| §4 bounded client queue (AudioWorklet) → playback → `audio.played(offset)` | §6.6, §6.9 |
| §5.1 WebSocket PCM16 16 kHz mono, binary 20–32 ms, playback queue, biết sample rate từng backend | §6.3.3–§6.3.4, §6.9.1, §6.9.4 |
| §7.1 pre-roll 200–300 ms; gap/packet thiếu cần policy | §6.11, §6.7.1 |
| §7.2 `audio.start`, `audio.chunk`, `audio.played`, `client.clear` | §6.9 |
| §7.3 flush AudioWorklet, bỏ chunk generation cũ, đo âm thanh dừng | §6.9.6 |
| §8.3 playback buffer 196 ms / 0 ms / 150–300 ms | §6.7 |
| §10 TTS underrun, frame bị rớt | §6.7.1, §6.10.5 |

---

## 6.13 Lỗi kinh điển: triệu chứng → nguyên nhân → cách sửa

| Triệu chứng | Nguyên nhân hay gặp | Cách kiểm tra / sửa |
|---|---|---|
| Không có mẫu nào từ mic, không báo lỗi | `AudioContext` đang `suspended` (autoplay policy); trang không phải secure context; worklet không được "kéo" | Log `ctx.state`; `resume()` trong click; HTTPS/localhost; nối worklet tới destination qua gain 0 |
| Giọng bot nhanh/cao hoặc chậm/trầm | Phát TTS 24 kHz như 48 kHz hoặc ngược lại; bỏ qua `sample_rate` trong `audio.start` | Resampler theo generation; assert rate (Chương 2 §2.11) |
| Giật đều ở đầu mỗi câu trả lời | Không pre-buffer; chunk đầu nhỏ hơn chunk sau | Pre-buffer ≥ chunk đầu (§6.7.3) |
| Giật ngẫu nhiên giữa câu, nặng hơn khi nhiều user | RTF của TTS gần/vượt 1 dưới tải | Xem RTF/lead phía server; giảm `max_streams`, int8, thêm GPU (VieNeu troubleshooting, **Reported**) |
| Tiếng click mỗi lần bắt đầu/dừng phát | Không fade; nối request TTS độc lập | Fade-in/out 2–10 ms (§6.9.3) |
| Lách tách đều 10–20 ms | Resample từng chunk không state; hoặc `sd.play()` mỗi chunk | Resampler có state; một output stream mở suốt (§6.4.2) |
| Ngắt lời xong bot vẫn nói thêm 0.5–2 s | Client không flush; hoặc chỉ flush hàng đợi main thread, quên ring buffer worklet; chunk cũ đang bay vẫn được phát | Clear trong worklet; lọc `generation_id` ở main thread **và** worklet (§6.9.6) |
| Sau ngắt lời, câu trả lời mới bị chặn không phát | Logic chặn generation quá rộng (chặn cả generation mới) | Tách `min_gen` (chặn) khỏi `gen` (đang phát) như §6.9.2 |
| Bot tự ngắt lời chính nó trên loa ngoài | Không AEC, hoặc AEC không thấy tín hiệu tham chiếu; Bluetooth trễ lớn | Bật `echoCancellation`; test loa ngoài; Chương 7 |
| History ghi cả câu dù user ngắt giữa chừng | Server dùng "đã gửi" hoặc "đã sinh" thay vì "đã phát" | Dùng `audio.played` offset; server phải áp dụng truncate (§6.9.7) |
| Âm tiết đầu của user bị mất, ASR sai chữ đầu | Không pre-roll; client VAD-gating không gửi kèm pre-roll | Pre-roll 200–300 ms ở gateway (§6.11) |
| Timestamp VAD/endpoint trôi dần trong session dài | Dùng wall clock thay vì số mẫu; resample làm tròn mỗi chunk | Đồng hồ bằng số mẫu (§6.8.3) |
| Độ trễ tăng dần theo thời gian session | Hàng đợi không giới hạn ở đâu đó (capture queue, playback queue, socket buffer) | Bounded queue + đếm drop; log độ dài hàng đợi |
| Python client lâu lâu "bụp" | GC/GIL làm callback trễ; blocksize quá nhỏ; làm việc nặng trong callback | Blocksize 20 ms; callback chỉ chép; xem `status.output_underflow` |
| Chất lượng TTS tụt hẳn khi mở mic với tai nghe Bluetooth | Tai nghe chuyển sang profile cuộc gọi băng hẹp | Dùng mic riêng hoặc tai nghe có dây; log thiết bị và rate (§6.3.5) |
| "Máy A tốt, máy B tệ" | AEC/NS/AGC khác nhau, rate thiết bị khác nhau | Log `getSettings()`, `ctx.sampleRate`, `outputLatency` theo session |

---

## 6.14 Thực hành

Công cụ: trình duyệt Chrome/Firefox, `python -m http.server` hoặc Vite cho trang tĩnh (localhost), `sounddevice`, `soxr`, `numpy`, một server WebSocket tối giản (FastAPI/`websockets`), Audacity.

1. **Đọc thiết bị.** In `sd.query_devices()`, `default_samplerate` của mic/loa mặc định, và `stream.latency` sau khi mở với `latency="low"` và `"high"`. Trong trình duyệt, in `ctx.sampleRate`, `baseLatency`, `outputLatency`, `track.getSettings()`. So sánh với tai nghe có dây và Bluetooth.
2. **Echo test loopback.** Dựng client Python full-duplex (§6.4.2) phát lại chính mic với độ trễ D (ring buffer). Tăng/giảm blocksize, chạy một tác vụ CPU nặng song song, đếm `input_overflow`/`output_underflow`.
3. **Capture worklet.** Dựng §6.3.4, gửi PCM16 16 kHz lên server, server ghi file WAV. Mở trong Audacity: đúng tốc độ? có click đều không? So resampler có lọc với `x[::3]` trên spectrogram (phụ âm `s/x`).
4. **Pre-buffer.** Server giả lập TTS: đọc một file WAV tiếng Việt, gửi chunk 160 ms rồi 320 ms với thời gian sinh = RTF × thời lượng × nhiễu, thêm jitter. Đo underrun và thời gian chờ ở client với pre-buffer 0/150/300/500 ms; so với bảng §6.7.3. Lặp lại với chunk 40 ms.
5. **Barge-in.** Thêm nút "ngắt" gửi lên server; server tăng `generation_id`, gửi `clear`, tiếp tục bắn vài chunk của generation cũ (mô phỏng chunk đang bay). Xác nhận không chunk cũ nào phát ra; đo `barge_stop_ms`; ghi âm loa bằng điện thoại để nghe có click không khi bỏ fade.
6. **Played offset.** Phát một câu TTS 24 kHz trên context 48 kHz, ngắt ở giây thứ 1.5. Kiểm tra `played_sample_offset` báo về ≈ 36 000 (theo rate nguồn 24 kHz) cộng/trừ độ trễ output.
7. **Đo voice-to-voice phía client.** Cài §6.10.3 với một server giả (endpoint cố định 500 ms sau tiếng nói cuối, TTS giả TTFA 150 ms). Kiểm tra con số client đo ≈ 500 + 150 + mạng + pre-buffer + outputLatency.
8. **Loopback latency.** Phát chirp ra loa, thu bằng mic, cross-correlation để tìm round-trip latency của máy bạn, với loa trong, tai nghe có dây, Bluetooth.

---

## 6.15 Đáp án các câu hỏi tự kiểm tra

**Q1. Vì sao playback phải có queue? Underrun và overrun là gì?**

- Loa tiêu thụ mẫu theo **đồng hồ phần cứng**, đều đặn, mỗi callback một khối cố định (128 frames trong Web Audio; blocksize của bạn trong PortAudio), với deadline bằng thời lượng khối. Audio TTS tới theo **nhịp khác hẳn**: từng cục 80–320 ms, khoảng cách không đều do tốc độ sinh biến động và jitter mạng, đôi khi dồn vài chunk một lần. Queue (ring buffer) là chỗ **hấp thụ chênh lệch nhịp**: producer ghi khi có, consumer đọc đúng lượng cần mỗi callback.
- Không có queue, chỉ còn cách phát mỗi chunk ngay khi nó tới (ví dụ `sd.play()` từng chunk): mỗi lần mở/đóng stream tạo khoảng hở và click (**Reported**, [Faster Qwen3-TTS](../wiki/faster-qwen3-tts.md)); chunk tới sớm đè lên chunk đang phát hoặc phải chờ không kiểm soát. Wiki ghi nhận audio giật được sửa bằng hàng đợi playback phía client thay vì phát từng chunk ngay khi tới (**Reported**, [Barge-in & Echo](../wiki/voice-agent-barge-in-and-echo-handling.md)).
- Queue còn là **điểm điều khiển** của voice agent: nơi lọc theo `generation_id`, nơi flush khi barge-in, nơi đếm `played_sample_offset`. Nó phải **bounded** để độ trễ không phình vô hạn.
- **Underrun:** consumer cần mẫu nhưng buffer rỗng (playback: TTS chưa kịp tới → im lặng giữa câu, giật, click). **Overrun:** producer cần ghi nhưng buffer đầy (capture: callback không được đọc kịp → mất mẫu mic, âm tiết bị nuốt; playback bounded: audio TTS bị drop). Gọi chung là xrun. PortAudio báo bằng `output_underflow`/`input_overflow`; Web Audio thì bạn tự đếm.

**Q2. Pre-buffer 150–300 ms đổi lại được gì và mất gì?**

- **Được:** khả năng chịu biến động. Bắt đầu phát khi đã có X ms trong buffer nghĩa là chunk sau được phép tới muộn tới X ms so với "đúng lúc" mà không gây khoảng hở. Nó hấp thụ cả jitter mạng lẫn biến động tốc độ sinh của TTS. Trong mô phỏng đồ chơi §6.7.3, ở RTF 0.5 với chunk 40 ms, pre-buffer 150 ms kéo xác suất giật mỗi lượt từ ~42% xuống ~0.5% (**Reproduced** trên mô hình tổng hợp, không phải hệ thật). VieNeu khuyến nghị 150–300 ms trên GPU, ≥ 300 ms trên CPU (**Reported**).
- **Mất:** độ trễ, một-đổi-một. Pre-buffer nằm trên critical path voice-to-voice (tài liệu thiết kế §8.1): 300 ms pre-buffer là 300 ms user chờ thêm trước khi nghe tiếng bot, cỡ một phần ba ngân sách ~0.7–1.2 s (§8.2, **Reported**). Đó là lý do demo HF s2s để mặc định 0 ms và client Python để 196 ms chỉ cho backend HTTP (**Reported**), và tài liệu thiết kế tóm lại "bớt giật nhưng chậm bắt đầu hơn" (§8.3).
- **Không mua được:** chống giật khi RTF ≥ 1 kéo dài (buffer nào cũng cạn), như demo HF s2s nói rõ (**Reported**). Và nếu chunk của backend lớn, pre-buffer bị lượng tử hoá theo chunk: với chunk đầu 160 ms, đặt 150 ms không khác gì 0 ms (§6.7.3).
- **Giảm chi phí:** mở cổng ngay khi lượt đã kết thúc (câu ngắn không phải chờ); chỉnh theo backend; tăng thích ứng khi gặp underrun; ưu tiên backend có chunk đầu nhỏ và lead dương (§6.7.4).

**Q3. Làm sao flush ngay audio đang phát khi user ngắt lời?**

1. Server quyết định barge-in (VAD + gate, Chương 10/17), tăng `generation_id`, cancel LLM/TTS, và gửi `client.clear(generation_id)` / `{"type":"clear"}` trên đường nhanh (tài liệu thiết kế §7.3, **Reported**).
2. Client nhận clear, chuyển thẳng tới **playback worklet/callback** (không chỉ hàng đợi ở main thread): giữ 5–10 ms tiếp theo để **fade-out** (tránh click), vứt toàn bộ phần chưa phát còn lại bằng cách dời chỉ số ghi về chỉ số đọc, chặn mọi generation cũ hơn (§6.9.2, §6.9.5).
3. Bỏ mọi chunk thuộc generation cũ tới **sau** clear: lọc ở main thread (không tốn công decode/resample) và ở worklet (đã nằm trong hàng đợi message).
4. Báo về `audio.played(generation_id, played_sample_offset)` ngay lúc clear, theo rate của generation, không tính pre-buffer và im lặng underrun, để server chỉ lưu **phần đã phát** vào history kèm `[bị ngắt]`.
5. Đo `barge_stop_ms` (nhận clear → tín hiệu ra bằng 0) và barge-in latency theo âm thanh **nghe được dừng**, không theo sự kiện phát hiện (**Reported**, [Community Usable STT](../wiki/community-usable-stt-voice-agents.md)).
6. Với WebRTC, flush nằm phía server; với server pacing (§6.6.2), lượng cần flush ở client nhỏ đi.

---

## 6.16 Tóm tắt một trang

- **Hai đầu realtime:** mic và loa chạy theo đồng hồ phần cứng; mọi thứ ở giữa "bursty". Buffer hấp thụ chênh lệch nhịp, và **mỗi buffer trả giá bằng độ trễ**.
- **Mô hình callback:** phần cứng kéo khối, deadline = thời lượng khối. Callback chỉ **chép mẫu**: không I/O, không lock dài, không cấp phát liên tục, không chạy model. Python: blocksize ≥ 10–20 ms.
- **Trình duyệt:** HTTPS/localhost; `ctx.resume()` sau click; constraints là gợi ý, đọc `getSettings()`; capture bằng **AudioWorklet** (128 frames/quantum), gom 20 ms, gắn `startFrame`; resample có lọc và có state (trong worklet/Worker hoặc ở server). Không dùng ScriptProcessor, không dùng MediaRecorder cho realtime.
- **Python:** PortAudio/sounddevice; mở **đúng rate thiết bị**, tự resample; một duplex stream; một output stream mở suốt, không `sd.play()` từng chunk; đếm `input_overflow`/`output_underflow`.
- **Ring buffer** với bộ đếm tuyệt đối: `w − r` = chờ, `r` = đã phát, `w` = đồng hồ mẫu. **Bounded queue**: drop cho dữ liệu cần tươi, backpressure cho dữ liệu không được mất; hàng đợi không giới hạn = rò rỉ độ trễ. **Jitter buffer**: WebRTC có sẵn; WebSocket thì pre-buffer đóng vai đó.
- **Underrun** (buffer cạn → giật) và **overrun** (buffer tràn → mất mẫu). Underrun TTS do RTF ≥ 1 (không buffer nào cứu), biến động RTF/mạng (pre-buffer cứu), chunk đầu nhỏ (pre-buffer ≥ chunk đầu).
- **Pre-buffer 150–300 ms:** đổi độ trễ một-đổi-một lấy khả năng chịu biến động; lượng tử hoá theo chunk; mở cổng sớm khi lượt kết thúc; chỉnh theo backend.
- **Clock drift** vài chục ppm (50 ppm = 30 ms/10 phút): vô hại với cascade nếu dùng **số mẫu làm đồng hồ**; quan trọng với stream liên tục và AEC.
- **Playback voice agent:** queue theo `generation_id`; `audio.start` mang rate; pre-buffer; `clear` = fade 5–10 ms + xoá + chặn generation cũ ở cả main thread và worklet; fade-in/out mọi chỗ gián đoạn; báo `played_sample_offset` theo rate nguồn, không tính pre-buffer và underrun.
- **Đo phía client:** `currentFrame` + `getOutputTimestamp()` + `outputLatency`; voice-to-voice đo trọn trên đồng hồ client nhờ server báo **chỉ số mẫu** của tiếng nói cuối. Panel server không gồm playback.
- **Pre-roll 200–300 ms** ở gateway (hoặc client nếu client gate bằng VAD) để không mất âm tiết đầu.

## 6.17 Liên kết

**Chương sau:** Chương 7 (AEC, NS, AGC: tín hiệu tham chiếu loa, drift giữa hai card, vì sao không đưa audio denoise vào ASR), Chương 8 (WebSocket vs WebRTC, Opus, RTP, jitter buffer thích ứng, PLC, framing binary), Chương 10 (VAD và quyết định barge-in), Chương 16 (dataflow và audio contract toàn pipeline), Chương 17 (turn-taking, cancellation, truncate history), Chương 18 (async/streaming, backpressure ở server), Chương 19 (chunker mệnh đề và cách ước lượng text đã phát), Chương 20 (latency: đo, đồng bộ đồng hồ, ngân sách).

**Chương trước:** [Chương 2](chuong-02-so-hoa-am-thanh-tu-song-toi-mang-so.md) (đơn vị thời gian, reblock 20 ms → 512, resampler có state, clock drift §2.8.5), [Chương 3](chuong-03-dinh-dang-file-container-va-codec.md) (PCM16 binary, bẫy MediaRecorder), [Chương 5](chuong-05-ngu-am-chu-viet-va-van-ban-tieng-viet.md) (vì sao không cắt đuôi/đầu âm tiết: pre-roll, fade).

**Tài liệu thiết kế:** [§4, §5.1, §7.1, §7.2, §7.3, §8.1–§8.3, §10](thiet-ke-pipeline-speech-to-speech-tieng-viet.md).

**Wiki:**

- [Speech-to-Speech Browser Demo](../wiki/speech-to-speech-browser-demo.md): HTTPS/localhost cho `getUserMedia`; worklet `mic-capture` resample về 24 kHz Int16 LE và contract version `audio-24k-v2`; worklet `audio-playback` dùng ring buffer, nội suy 24 → 48, fade 32 frame; startup buffer mặc định 0 ms, đếm theo mẫu, không rebuffer; issue #557 (1200 ms, không phải tối ưu chung); barge-in xoá queue, đếm PCM đã render, `conversation.item.truncate`; server timings không gồm playback; WebRTC flush phía server.
- [VieNeu Streaming Runtime](../wiki/vieneu-tts-streaming-runtime.md): định nghĩa TTFA, RTF, lead; frame 80 ms, chunk đầu 2 frame (GPU) / 4 frame (CPU), chunk sau 4 frame; lead tối thiểu +80 ms GPU, +320 ms CPU; pre-buffer 150–300 ms GPU, ≥ 300 ms CPU; giật do không pre-buffer hoặc RTF > 1.
- [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md): `generation_id` end-to-end, client bỏ chunk cũ, ba tầng chống echo, `{"type":"clear"}` flush AudioWorklet, hàng đợi playback chống giật, WebRTC vs WebSocket.
- [Speech-to-Speech OpenAI-Compatible Backends](../wiki/speech-to-speech-openai-compatible-backends.md) và [Speech-to-Speech Pipeline](../wiki/speech-to-speech-pipeline.md): `--playback-buffer-ms`, 196 ms mặc định cho `local --tts openai`; PortAudio trên Ubuntu.
- [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md): getUserMedia với AEC, ring buffer 20 ms ở gateway, client phải biết rate từng backend (24/48 kHz).
- [Community-Reported Usable STT for Voice Agents](../wiki/community-usable-stt-voice-agents.md): barge-in latency = phát hiện + flush playback buffer; đo lúc âm thanh dừng.
- [Faster Qwen3-TTS](../wiki/faster-qwen3-tts.md): giữ một output stream mở; `sounddevice.play` từng chunk gây gap.

**Đọc thêm ngoài wiki (tài liệu chuẩn, gợi ý):** W3C *Web Audio API* (AudioWorklet, render quantum, `getOutputTimestamp`, `outputLatency`); W3C *Media Capture and Streams* (getUserMedia, constraints); MDN về AudioWorklet, autoplay policy, cross-origin isolation và `SharedArrayBuffer`; tài liệu PortAudio và python-sounddevice (callback, `CallbackFlags`, `latency`); Ross Bencina, *Real-time audio programming 101: time waits for nothing* (luật của audio thread); tài liệu WebRTC NetEq (jitter buffer thích ứng, PLC).
