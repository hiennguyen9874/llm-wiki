# Chương 18. Lập trình async và streaming cho pipeline audio 🔴

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần V (Ghép pipeline).
> **Chương trước:** [Chương 17. Turn-taking, event, barge-in và cancellation](chuong-17-turn-taking-event-barge-in-va-cancellation.md). **Chương tiếp theo:** Chương 19. Cầu text → speech: chunker, normalizer, lexicon.
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §5.4.4 (materialize generator của faster-whisper trong `asyncio.to_thread`), §7.4 (vòng điều khiển), §8.3 (đòn bẩy: chạy faster-whisper trong thread, nối stage bằng async queue), §9.1 (admission cap, bounded queue, backpressure/429, deadline, circuit breaker), §9.3 (ưu tiên cadence hơn throughput batch), §10 mục 4–5 (tải, contract test: cancel giữa chunk, disconnect, timeout, 429).
> **Cơ sở:** mô hình event loop của `asyncio`, GIL, thread pool, structured concurrency, backpressure, circuit breaker là **kiến thức nền chung** về lập trình đồng thời và Python (CPython 3.11+), không phải claim lấy từ nguồn wiki. Hành vi của các hệ cụ thể lấy từ wiki và gắn nhãn bằng chứng: [Whisper Hallucination Mitigation](../wiki/whisper-hallucination-mitigation.md), [Faster-Whisper](../wiki/faster-whisper.md), [Voice Agent Frameworks](../wiki/voice-agent-frameworks.md), [Speech-to-Speech Realtime Engine](../wiki/speech-to-speech-realtime-engine.md), [OpenAI-Compatible Backends](../wiki/speech-to-speech-openai-compatible-backends.md), [CLI and Defaults](../wiki/speech-to-speech-cli-and-defaults.md), [VieNeu OpenAI Speech API](../wiki/vieneu-tts-openai-speech-api.md), [VieNeu Streaming Runtime](../wiki/vieneu-tts-streaming-runtime.md), [Silero VAD](../wiki/silero-vad.md), [NeMo-Speech.cpp Server](../wiki/nemo-speech-server.md), [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md), [Cascaded Voice-Agent Blueprint](../wiki/cascaded-voice-agent-blueprint.md), [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md). Thông tin vendor là **Reported** (wiki chưa chạy lại). Tám script ở "Phụ lục chương" chạy bằng Python 3.12.3 thuần (không numpy, không httpx) ngày 2026-10-07 trên máy 12 lõi: **Reproduced** cho hành vi của `asyncio`/thread/GIL và cho phép tính của chính script. Các "model" trong script là giả lập bằng `time.sleep` hoặc vòng lặp số học, mọi độ trễ là tham số giả định, không phải đo model hay mạng thật. Thiết kế và suy luận của tác giả là **Synthesis**.

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Giải thích được mô hình event loop đủ để dự đoán **khi nào** một dòng code làm đứng cả session, và đo được điều đó bằng **loop lag**.
2. Xếp mọi việc trong pipeline vào đúng chỗ chạy: ngay trên loop, trong thread (`asyncio.to_thread` / executor riêng), trong process pool, hay trong một worker service riêng. Biết vai trò của GIL trong lựa chọn này.
3. Dùng `Task`, `CancelledError`, `asyncio.timeout`, `TaskGroup` để viết code **huỷ được sạch**, và phân biệt "task đã huỷ" với "compute đã dừng".
4. Thiết kế producer/consumer với **bounded queue**, chọn đúng **drop policy** cho từng cạnh (uplink, text, audio downlink, control), và truyền backpressure ngược lên tới nơi sinh dữ liệu.
5. Viết stage streaming bằng async generator, đọc LLM qua SSE và TTS qua HTTP chunked, đóng connection để huỷ, đặt timeout đúng loại.
6. Giữ **cadence** audio đều: pacing theo lịch tuyệt đối, chọn continuous batching thay vì static batching, và hiểu vì sao phục vụ nhiều request hơn có thể đồng nghĩa với trải nghiệm tệ hơn.
7. Thiết kế admission control, xử lý `429`/`Retry-After` theo deadline, circuit breaker và fallback cho voice.
8. Test được pipeline realtime mà không cần mic: replay theo thời gian thực, giả lập jitter, disconnect, backend chậm, và kiểm tra không rò task sau teardown.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. Vì sao lặp generator của faster-whisper trên event loop làm đứng cả pipeline? Vì sao `await asyncio.to_thread(model.transcribe, audio)` **vẫn chưa** sửa được lỗi?
- Q2. Bounded queue và backpressure ngăn được lỗi gì?
- Q3. Huỷ một task đang chờ I/O khác gì huỷ một inference đang chạy trên GPU?
- Q4. Khi nào dùng `asyncio.to_thread`, khi nào dùng process pool, khi nào tách thành worker service riêng?
- Q5. Uplink đầy thì bỏ gì? Downlink đầy thì làm gì? Vì sao "chặn producer" ở uplink không giải quyết được gì?
- Q6. Vì sao ưu tiên nhịp audio đều (cadence) hơn throughput batch? Cho một ví dụ hệ thống phục vụ được nhiều request hơn nhưng trải nghiệm tệ hơn.
- Q7. TTS trả `429` đúng lúc user đang chờ câu trả lời. Gateway nên làm gì?
- Q8. Làm sao test một pipeline realtime mà không cần mic và người nói thật?

---

## 18.1 Bức tranh: một session là một nhóm task có nhịp

[Chương 16](chuong-16-dataflow-end-to-end-va-audio-contract.md) vẽ dataflow: dữ liệu gì đi trên cạnh nào. [Chương 17](chuong-17-turn-taking-event-barge-in-va-cancellation.md) vẽ quyết định: ai được close, commit, cancel. Chương này trả lời câu hỏi còn lại: **code nào chạy ở đâu, khi nào, và dừng thế nào**.

Một session trong gateway asyncio, nhìn dưới góc runtime:

```text
                        ┌──────────────────────── event loop (1 thread, mọi session) ─────────────────────────┐
 client ──WS/RTC──►  ws_reader ──► uplink q (bounded, drop-oldest) ──► vad/asr feed ──► inbox ──► OWNER       │
                     │                                                                    ▲         │         │
                     │      client.played / cancel / disconnect ──────────────────────────┘         │ lệnh    │
                     │                                                                              ▼         │
                     │   response scope (TaskGroup, huỷ được):  llm_stream ─► chunker ─► tts_stage  │         │
                     │                                              (async gen, SSE)    │          │         │
                     │                                                                  ▼          │         │
 client ◄──WS/RTC──  send_loop (writer DUY NHẤT) ◄── out (control ưu tiên) ◄── pacer (credit) ◄── audio q     │
                     └───────────────────────────────────────────────┬───────────────────────────────────────┘
                                         run_in_executor / to_thread │  call_soon_threadsafe
                                     ┌───────────────────────────────▼──────────────────────┐
                                     │ thread: faster-whisper turn-final, TTS in-process     │  (nhả GIL khi chạy kernel)
                                     └───────────────────────────────┬──────────────────────┘
                                                        HTTP / WS    │
                                     ┌───────────────────────────────▼──────────────────────┐
                                     │ worker service riêng: ASR streaming, TTS, LLM (GPU)    │  (process khác, env khác)
                                     └──────────────────────────────────────────────────────┘
```

Có ba loại việc, mỗi loại một chỗ chạy (**Synthesis**, áp dụng kiến thức nền):

| Loại việc | Ví dụ | Chạy ở đâu | Vì sao |
|---|---|---|---|
| **I/O-bound** (chủ yếu chờ) | Đọc/ghi WebSocket, gọi HTTP tới LLM/TTS/ASR service, timer | Coroutine trên event loop | Chờ không tốn CPU; một thread phục vụ được hàng nghìn kết nối |
| **CPU ngắn** (≪ 1 ms mỗi lần) | Parse JSON nhỏ, cập nhật state owner, reblock vài trăm mẫu | Trên loop | Chuyển sang thread tốn hơn chính việc đó |
| **CPU/GPU dài** (≥ vài ms) | faster-whisper decode, TTS in-process, resample cả turn, Silero VAD nếu nhiều session | Thread, process, hoặc service riêng | Chạy trên loop thì mọi session khác đứng chờ |

Nguyên tắc xuyên suốt chương: **event loop là tài nguyên dùng chung của mọi session trong process; mỗi mili giây bạn chiếm nó là một mili giây mọi session khác không nhận được audio, không gửi được audio, không huỷ được gì.**

---

## 18.2 Event loop: mô hình đủ dùng

### 18.2.1 Một thread, nhiều coroutine, nhường ở điểm `await`

Mô hình (kiến thức nền):

- Event loop là **một vòng lặp trên một thread**. Mỗi vòng, nó lấy các callback đã sẵn sàng (task có thể chạy tiếp, socket có dữ liệu, timer đến hạn) và chạy **lần lượt** từng cái.
- Một coroutine chỉ nhường quyền chạy ở **điểm `await`** thực sự phải chờ. Giữa hai điểm `await`, nó chạy liền một mạch, không ai ngắt được.
- Đây là **đa nhiệm hợp tác** (cooperative): không có preemption. Một coroutine không chịu nhường thì cả loop đứng.

Hệ quả có lợi: giữa hai `await` không có race. Đó là lý do mẫu "single-writer + inbox" của Chương 17 §17.2.3 an toàn mà không cần lock, và lý do "kiểm generation rồi gửi" (§17.6.3) là nguyên tử nếu không có `await` xen giữa.

Hệ quả có hại: **một lời gọi đồng bộ chậm ở bất cứ đâu, trong bất cứ session nào, làm trễ mọi thứ khác**. `time.sleep(0.3)`, `requests.post(...)`, `model.transcribe(...)` lặp trên loop, `json.dumps` một history 2 MB, `np.concatenate` một turn 30 s, ghi log đồng bộ ra đĩa chậm: tất cả đều là "một callback chạy lâu".

### 18.2.2 Ngân sách thời gian giữa hai `await`

Gọi **loop lag** là độ trễ giữa thời điểm một callback lẽ ra được chạy và thời điểm nó thực sự chạy. Với audio realtime, ngân sách được suy từ nhịp nhỏ nhất trong hệ thống (**Synthesis**):

| Nhịp | Giá trị | Loop lag chịu được |
|---|---|---|
| Frame transport | 20 ms | P99 vài ms; lag ≥ 20 ms là trễ một frame |
| Frame VAD Silero | 32 ms (512 mẫu @16 kHz) | Lag 50 ms làm quyết định barge-in đến muộn ~2 frame |
| Pacing downlink | 20 ms | Lag cộng dồn thành trôi lịch nếu pacing sai cách (§18.7.2) |
| Quantum AudioWorklet | 2,67 ms @48 kHz | Chạy ở client, không trên loop server |

Một phép tính đáng làm trước khi đặt bất cứ thứ gì "inline" trên loop. Silero VAD được báo là tốn **dưới 1 ms cho mỗi chunk 30+ ms** trên một thread CPU (**Reported**).[^silero] Lấy cận trên 1 ms cho mỗi chunk 32 ms:

```text
mỗi session:  31,25 chunk/s × ≤1 ms  = ≤31 ms CPU mỗi giây  ≈ ≤3 % một lõi
N session trên MỘT loop: N × 3 %
  N = 10  → ≤31 % thời gian loop chỉ để chạy VAD
  N = 30  → ≤94 %  → loop bão hoà, mọi thứ khác trễ
```

Con số thật có thể thấp hơn nhiều (ONNX được báo nhanh hơn 4–5 lần trong một số điều kiện, **Reported**),[^silero] nhưng bài học là **chi phí inline nhân với số session**. Khi số session trên một process tăng, hãy đo, rồi chọn: chạy VAD trong thread riêng, gom batch VAD của nhiều session mỗi 32 ms, hoặc chạy nhiều process gateway (mỗi process một loop) (**Synthesis**).

### 18.2.3 Đo loop lag

Hai công cụ, cả hai nên có từ ngày đầu:

**1. Task giám sát.** Ngủ 10 ms, đo thời gian thật trôi qua, phần dư là lag. Đẩy P50/P99/max ra metric theo process.

```python
async def lag_monitor(period=0.010):
    while True:
        t0 = time.perf_counter()
        await asyncio.sleep(period)
        LOOP_LAG_MS.observe((time.perf_counter() - t0 - period) * 1000)
```

**2. Debug mode của asyncio.** `asyncio.run(main(), debug=True)` (hoặc biến môi trường `PYTHONASYNCIODEBUG=1`) cảnh báo mọi callback chạy lâu hơn `loop.slow_callback_duration` (mặc định 0,1 s). Script 8 ở Phụ lục cố ý đặt `time.sleep(0.3)` trong coroutine và nhận được (**Reproduced**):

```text
WARNING asyncio: Executing <Task finished name='Task-1' coro=<main() done, ...> took 0.300 seconds
```

Debug mode tốn chi phí, dùng trong test và staging. Task giám sát thì chạy cả production.

---

## 18.3 Code blocking: faster-whisper, GIL và chỗ chạy của từng việc (Q1, Q4)

### 18.3.1 Generator lười của faster-whisper

`WhisperModel.transcribe` của faster-whisper trả về `(segments, info)`, trong đó `segments` là **generator**: việc transcribe chỉ bắt đầu khi bạn lặp nó, và chạy tới hết khi bạn gom vào list hoặc lặp bằng `for`. README ghi rõ dòng `segments = list(segments)` là nơi transcription thực sự chạy (**Reported**).[^fw]

Tài liệu thiết kế và report yêu cầu materialize generator này (`list(segs)`) **bên trong worker thread** (`asyncio.to_thread`), vì lặp generator lười ngay trên event loop sẽ block cả pipeline; Pipecat từng gặp đúng lỗi này (PR #5931) (**Reported**).[^whisper][^frameworks][^design]

Script 1 ở Phụ lục tái hiện ba cách viết, với một `FakeWhisper` có cùng hình dạng API: 6 segment, mỗi segment 150 ms "kernel native" giả lập bằng `time.sleep` (nhả GIL như kernel CTranslate2/PyTorch). Trong lúc đó, một task giả lập nhánh VAD cần xử lý frame 32 ms theo đồng hồ (**Reproduced**):

| Cách viết | Wall | Loop lag max | Frame VAD muộn > 50 ms |
|---|---|---|---|
| A. `segs, _ = model.transcribe(a)` rồi `[s for s in segs]` **trên loop** | 901 ms | **899 ms** | **26** |
| B. `segs, _ = await asyncio.to_thread(model.transcribe, a)` rồi lặp **trên loop** | 906 ms | **903 ms** | **26** |
| C. `await asyncio.to_thread(lambda: list(model.transcribe(a)[0]))` | 902 ms | 1,9 ms | 0 |

Cách A là lỗi hiển nhiên. **Cách B là lỗi tinh vi, và là lý do câu hỏi Q1 tồn tại**: `to_thread(model.transcribe, …)` chỉ đưa *việc tạo generator* sang thread. Việc tạo generator gần như tức thì, nên thread trả về ngay. Toàn bộ decode xảy ra lúc lặp, và việc lặp lại nằm trên loop. Nhìn code thì "có `to_thread` rồi", nhưng loop vẫn đứng 0,9 s: 26 frame VAD liên tiếp đến muộn, quyết định barge-in của **mọi session** trong process trễ gần một giây.

Quy tắc tổng quát (**Synthesis**): **khi đẩy việc sang thread, hãy đẩy cả phần tiêu thụ kết quả lười**. Generator, iterator, `DataFrame.apply` lười, `map()` của Python 3: thứ gì trả về một đối tượng "sẽ tính khi lặp" thì phải được lặp trong thread.

```python
# ĐÚNG: mọi việc tốn thời gian đều nằm trong hàm chạy ở thread
def _transcribe_turn(model, audio_f32_16k):
    segs, info = model.transcribe(audio_f32_16k, language="vi", beam_size=1,
                                  condition_on_previous_text=False, temperature=0.0,
                                  vad_filter=True)
    segs = list(segs)                       # decode chạy Ở ĐÂY, trong thread
    return segs, info

segs, info = await loop.run_in_executor(ASR_EXECUTOR, _transcribe_turn, model, audio)
```

Tham số decode ở trên lấy theo tài liệu thiết kế §5.4.4 (**Reported**);[^design] lọc hậu kỳ (`no_speech_prob`, `compression_ratio`, blacklist) cũng nên chạy trong cùng hàm, vì nó rẻ và giữ loop sạch.

### 18.3.2 GIL: vì sao thread đủ cho model, nhưng không đủ cho Python thuần

CPython có **GIL** (global interpreter lock): tại mỗi thời điểm chỉ một thread chạy bytecode Python. Hai hệ quả (kiến thức nền):

- Thư viện native (CTranslate2, ONNX Runtime, PyTorch, numpy cho phép toán lớn) **thường nhả GIL** trong lúc chạy kernel. Thread chạy kernel không chặn loop. Nhưng phần Python bao quanh kernel (tokenizer, ghép segment, hậu xử lý) vẫn giữ GIL trong những khoảnh khắc ngắn. Đừng giả định, hãy đo loop lag.
- Code **Python thuần** tốn CPU (vòng lặp xử lý mẫu bằng tay, parse lớn, thuật toán viết bằng Python) giữ GIL. Đặt nó trong thread thì loop vẫn phải giành GIL với nó: CPython chuyển GIL theo `sys.getswitchinterval()` (mặc định 5 ms).

Script 1, phần D–F, chạy một vòng lặp số học thuần Python ~0,8 s (**Reproduced**):

| Cách chạy CPU thuần Python | Loop lag p50 | Loop lag max | Frame VAD muộn |
|---|---|---|---|
| D. Trên loop | 0,3 ms | **770 ms** | 22 |
| E. Trong `to_thread` | **5,2 ms** | 10,7 ms | 0 |
| F. Trong `ProcessPoolExecutor` | 0,3 ms | 1,4 ms | 0 |

E không làm đứng loop, nhưng đẩy lag trung vị lên đúng cỡ switch interval: mỗi lần loop muốn chạy, nó chờ thread nhả GIL. Một thread như vậy chấp nhận được; mười thread như vậy cạnh tranh GIL với loop thì không. F tách hẳn sang process khác có GIL riêng, nên loop sạch. Python 3.13 có bản build free-threaded thử nghiệm bỏ GIL; với stack ML hiện tại, đừng thiết kế dựa vào nó (**Synthesis**).

### 18.3.3 Executor: đừng dùng chung một cái cho mọi thứ

`asyncio.to_thread(f)` chạy `f` trong **default executor** của loop: một `ThreadPoolExecutor` dùng chung cho cả process, mặc định `min(32, số CPU + 4)` thread (kiến thức nền, Python 3.8+). Ba vấn đề khi pipeline lớn lên (**Synthesis**):

1. **Bão hoà chéo:** 12 lượt ASR turn-final dài cùng lúc chiếm hết thread; một lời gọi `to_thread` nhỏ khác (đọc file cấu hình, DNS đồng bộ của thư viện nào đó) phải xếp hàng sau chúng.
2. **Song song quá mức trên GPU:** 16 thread cùng gọi một model trên một GPU không làm nhanh hơn, chỉ tranh nhau VRAM và kernel launch. Model có số "đồng thời hiệu quả" của nó.
3. **Không đo được:** không biết hàng chờ trong executor dài bao nhiêu.

Cách làm: **mỗi model một executor riêng**, kích thước bằng số đồng thời model chịu được, và một semaphore phía async để đếm và giới hạn hàng chờ:

```python
ASR_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="asr")   # đo rồi mới chọn số
ASR_SLOTS = asyncio.Semaphore(2 + 4)        # 2 đang chạy + tối đa 4 chờ; quá nữa → từ chối/fallback

async def transcribe_turn(audio):
    if ASR_SLOTS.locked():
        raise Overloaded("asr")             # admission ở tầng model (§18.8)
    async with ASR_SLOTS:
        return await loop.run_in_executor(ASR_EXECUTOR, _transcribe_turn, MODEL, audio)
```

Một ví dụ cực đoan của nguyên tắc này: server VieNeu dùng **một worker thread sở hữu GPU**; `infer_stream` từ N thread HTTP chỉ là N hàng đợi audio, server không fork (**Reported**).[^vieneurt] Mọi request đi qua một chỗ, và chỗ đó gom batch (§18.7.3).

### 18.3.4 Cầu nối thread → loop

Đối tượng của `asyncio` (`Queue`, `Event`, `Future`) **không thread-safe**. Từ một worker thread, không bao giờ gọi `queue.put_nowait(x)` trực tiếp. Có hai cầu nối chuẩn (kiến thức nền):

| Từ thread muốn… | Dùng | Ghi chú |
|---|---|---|
| Đẩy một sự kiện, không cần chờ | `loop.call_soon_threadsafe(q.put_nowait, x)` | Không có backpressure: nếu `q` bounded và đầy, `QueueFull` nổ **trên loop** |
| Đẩy và chờ đến khi có chỗ (backpressure) | `asyncio.run_coroutine_threadsafe(q.put(x), loop).result(timeout)` | Thread bị chặn tới khi consumer lấy bớt; phải kiểm cờ stop khi timeout để không treo vĩnh viễn |

Script 7 dùng cách thứ hai cho TTS in-process, với vòng `result(timeout=0.05)` kiểm cờ stop mỗi 50 ms. Cách thứ nhất dùng cho thông báo "thread đã xong" (`on_gpu_exit`). Chiều ngược lại, loop → thread, dùng `threading.Event` (cờ stop) hoặc `queue.Queue` của thư viện chuẩn.

### 18.3.5 Process pool và worker service riêng

| Lựa chọn | Hợp với | Giá phải trả |
|---|---|---|
| `to_thread` / executor riêng | Model native nhả GIL, chạy trong cùng process gateway (MVP: faster-whisper turn-final) | Model nằm trong process gateway: crash/OOM của model giết mọi session; phải load model trong mọi process gateway nếu chạy nhiều worker |
| `ProcessPoolExecutor` | CPU thuần Python nặng, ngắn, không cần state lớn | Pickle tham số và kết quả qua IPC; process con không chia sẻ model đã load; khó huỷ giữa chừng |
| **Worker service riêng** (HTTP/WS/gRPC) | Model GPU dùng chung giữa nhiều gateway; môi trường phụ thuộc khác nhau | Thêm một hop mạng (localhost ~sub-ms), thêm contract và health check; đổi lại cô lập lỗi, scale độc lập |

Tài liệu thiết kế §9.1 chọn hướng thứ ba cho triển khai: mỗi model một owner process, đừng để mỗi gateway worker tự load weights; tách environment ASR/TTS/ONNX để tránh xung đột torch/transformers/CUDA; container `gateway`, `asr-service`, `tts-service`… (**Synthesis** của tài liệu thiết kế).[^design] Khi đó, phần lớn "việc nặng" của gateway trở thành **I/O-bound**: gọi HTTP/WS tới service. Gateway chỉ còn VAD, resample, owner, pacing, và đó là lý do gateway asyncio thuần chạy được nhiều session.

Chi phí IPC cho audio nhỏ hơn bạn nghĩ: 1 s audio 16 kHz float32 là 64 KB; một turn 5 s là 320 KB (Chương 16 §16.5.5). Gửi qua localhost hay pickle sang process khác đều không đáng kể so với decode.

### 18.3.6 Bảng quyết định (Q4)

| Câu hỏi | Nếu "có" |
|---|---|
| Việc này chỉ chờ (socket, HTTP, timer)? | Coroutine trên loop |
| Mỗi lần < ~0,5 ms và số session nhỏ? | Inline trên loop, nhưng đo lại khi số session tăng |
| Gọi thư viện native nhả GIL, model nhỏ, cùng process chấp nhận được? | Executor **riêng** cho model đó, có semaphore |
| CPU thuần Python nặng? | Process pool, hoặc viết lại bằng numpy/native |
| Model GPU, dùng chung giữa nhiều gateway, hoặc dependency xung đột? | Worker service riêng; gateway gọi bằng client async |
| Thư viện chỉ có API đồng bộ và **không** huỷ được từ bên trong? | Thread + cờ stop nếu có callback; nếu không, đó là **deployment gate** (Chương 17 §17.8.3) |

---

## 18.4 Task, cancellation, timeout, structured concurrency (Q3)

### 18.4.1 Vòng đời một task

```python
task = asyncio.create_task(run_response(gid, text))     # chạy song song với code hiện tại
```

Ba bẫy kinh điển (kiến thức nền):

1. **Mất tham chiếu.** Loop chỉ giữ tham chiếu yếu tới task. Task không ai giữ có thể bị garbage collect giữa chừng. Luôn lưu task vào một chỗ (thuộc tính session, set, hoặc `TaskGroup`).
2. **Exception không ai lấy.** Task nổ exception mà không ai `await` thì lỗi chỉ hiện thành log "Task exception was never retrieved", thường là khi đã muộn. Hệ quả kiểu: `tts_stage` chết vì lỗi decode, response im lặng mãi mãi, owner vẫn nghĩ bot đang nói.
3. **Fire-and-forget không có owner.** Task không thuộc scope nào thì không ai huỷ nó khi session đóng. Đây là nguồn chính của callback muộn rơi vào session khác (Chương 17 §17.10).

### 18.4.2 Ngữ nghĩa của huỷ

`task.cancel()` **không dừng task ngay**. Nó đánh dấu task, và ở lần tới task dừng tại một điểm `await`, `asyncio.CancelledError` được ném ra **tại điểm đó**. Từ đó (kiến thức nền):

- Code giữa hai `await` không bị ngắt. Một vòng lặp đồng bộ dài thì không huỷ được cho tới khi nó tự `await`.
- `finally` và `async with` chạy khi huỷ: đây là nơi đóng HTTP stream, trả slot, set cờ stop.
- Từ Python 3.8, `CancelledError` kế thừa `BaseException`, không phải `Exception`. `except Exception:` không bắt nó, đúng như mong muốn. Nhưng `except BaseException:` hoặc `except:` trần **nuốt** nó.

Script 2 phần 3 cố ý viết một worker bắt `BaseException` trong vòng lặp. Kết quả (**Reproduced**): sau `cancel()`, worker in "nuốt CancelledError, chạy tiếp", chạy đủ 5 vòng, và `task.cancelled()` trả về `False`. Trong pipeline thật, đó là một `tts_stage` tiếp tục đẩy audio sau barge-in. Quy tắc: nếu buộc phải bắt rộng (để log), **ném lại** `CancelledError`:

```python
try:
    await step()
except asyncio.CancelledError:
    raise                                   # luôn ném lại
except Exception:
    log.exception("step failed")            # lỗi thật thì xử lý
```

Hai công cụ ít dùng, dùng thì phải hiểu:

- `asyncio.shield(aw)`: giữ `aw` chạy tiếp khi task bên ngoài bị huỷ. Dùng cho việc phải xong bất kể huỷ (ví dụ ghi bản ghi latency cuối lượt). Đừng shield inference: shield inference là cố ý làm T_release dài ra.
- `Task.uncancel()` (3.11+): rút lại một yêu cầu huỷ. Chỉ thư viện cấp thấp (như `asyncio.timeout`) cần. Code ứng dụng gần như không bao giờ cần.

### 18.4.3 Q3: huỷ task chờ I/O và huỷ inference đang chạy

Script 2 đo ba trường hợp (**Reproduced**; "inference" là 10 bước × 100 ms trong thread):

| Trường hợp | `await task` trả về sau `cancel()` | Compute thật sự dừng sau `cancel()` |
|---|---|---|
| 1. Task chờ socket (`await` I/O) | 0 ms; `finally` đóng connection chạy ngay | 0 ms |
| 2. Task `await to_thread(infer)`, **không** cờ stop | 0 ms (`task.cancelled() = True`) | **765 ms** (thread chạy hết 10 bước, kết quả không ai nhận) |
| 3. Như 2, **có** cờ `threading.Event` kiểm giữa các bước | 0 ms | 50 ms (dừng ở ranh giới bước kế tiếp) |

Đây là cốt lõi của Q3. Với task chờ I/O, "huỷ task" và "dừng việc" là một: không có gì đang chạy cả, chỉ có một lời chờ. Với inference trong thread, huỷ task chỉ huỷ **asyncio future bọc ngoài**. Python không có cách an toàn để giết một thread đang chạy native code. Thread vẫn chiếm GPU tới khi:

- nó tự kiểm một cờ stop ở ranh giới bước (frame TTS, chunk ASR, token LLM): độ trễ dừng ≤ một bước;
- hoặc nó chạy xong.

Inference ở service khác (qua HTTP) có thêm một tầng nữa: đóng connection làm client ngừng nhận ngay, nhưng server có dừng tính hay không là chuyện của server. HF s2s ghi rõ: huỷ inference phía server là best-effort, đóng connection không bảo đảm server dừng GPU, nên vẫn phải lọc kết quả stale; với `/v1/audio/speech`, giao diện chuẩn không có thao tác huỷ phía server (**Reported**).[^backends]

Gom lại thành bảng của Chương 17 §17.8.4: **time-to-silence** phụ thuộc vào việc lọc (generation + guard), còn **time-to-release** phụ thuộc vào độ mịn của điểm kiểm cờ stop trong compute. Muốn T_release nhỏ, compute phải được thiết kế **chia bước và hợp tác**:

```python
def tts_blocking(text, stop: threading.Event, push):
    for frame in engine.frames(text):       # mỗi bước = 80 ms audio
        if stop.is_set():
            return "stopped"                # ≤ 1 bước sau khi gateway set cờ
        push(frame)
```

Nếu thư viện không cho chia bước (một lời gọi `synthesize(text)` trả full waveform), T_release bằng thời gian sinh cả câu. Đó là lý do chunker theo mệnh đề (Chương 19) còn có lợi cho cancellation: đơn vị không huỷ được nhỏ lại.

### 18.4.4 Timeout và deadline

Python 3.11+ có `asyncio.timeout(delay)` và `asyncio.timeout_at(when)` dạng context manager; khi hết giờ, task bên trong bị huỷ và `TimeoutError` được ném ra ở ngoài khối (kiến thức nền). `asyncio.wait_for(aw, t)` là dạng cũ hơn, cùng ý nghĩa.

```python
async with asyncio.timeout_at(turn_deadline):    # deadline TUYỆT ĐỐI của lượt
    async for clause in llm_clauses(...):
        ...
```

Với streaming, một con số "timeout" là không đủ. Cần bốn loại khác nhau (**Synthesis**):

| Timeout | Đo gì | Ví dụ khởi điểm (phải tune) | Hết giờ thì |
|---|---|---|---|
| Connect | Thiết lập TCP/TLS tới service | 1–2 s cho service nội bộ | Lỗi kết nối, đếm vào circuit breaker |
| First byte (TTFT/TTFA) | Từ gửi request tới byte nội dung đầu | Theo SLO, ví dụ TTFA P95 + biên | Fallback (§18.8.3) |
| Idle giữa hai chunk | Stream "treo" giữa chừng | Vài lần chunk period, ví dụ 1–2 s | Huỷ, coi như lỗi giữa câu |
| Tổng | Cả request | Theo độ dài câu tối đa | Huỷ |

Ưu tiên **deadline tuyệt đối** hơn timeout tương đối: deadline của lượt được tính một lần (ví dụ "audio đầu tiên phải ra trước `commit + 1,5 s`"), rồi mỗi stage nhận phần còn lại. Ba lần retry, mỗi lần timeout 1 s, không thể biến thành 3 s chờ nếu deadline là 1,5 s. Script 6 dùng đúng cách này (§18.8.2).

### 18.4.5 Structured concurrency: `TaskGroup`

`asyncio.TaskGroup` (3.11+) là một scope: mọi task tạo trong `async with TaskGroup() as tg:` phải kết thúc trước khi ra khỏi khối. Nếu một task con nổ exception (không phải `CancelledError`), các task anh em bị huỷ, và khối ném ra `ExceptionGroup` mà bạn bắt bằng `except*` (kiến thức nền). Nếu task chứa khối bị huỷ, mọi task con bị huỷ theo.

Đây đúng là hình dạng của một voice session (**Synthesis**):

```text
session scope (TaskGroup): ws_reader, uplink/vad, owner, pacer, send_loop, lag_monitor
   └─ response scope (TaskGroup, mỗi generation một scope): llm_stream+chunker, tts_stage
```

- **Huỷ response** = huỷ task chứa response scope. Mọi con (LLM stream, TTS) bị huỷ cùng lúc, `finally` của chúng đóng connection. Không cần nhớ từng handle.
- **Kết thúc session** = thoát session scope. Script 7 làm bằng cách owner ném `SessionEnd`; `TaskGroup` huỷ mọi task còn lại; `except* SessionEnd` bắt nó ở ngoài.
- **Lỗi trong một response không được giết session.** `run_response` phải tự bắt lỗi của nó, chuyển thành sự kiện `response.failed` gửi vào inbox, chứ không để exception lan lên session scope. Ngược lại, lỗi của `ws_reader` (client mất kết nối) **nên** kết thúc session.

Hai cái tên dễ nhầm:

- **AnyIO/Trio `CancelScope`:** một scope huỷ được theo kiểu structured concurrency, cùng họ với `TaskGroup` và `asyncio.timeout`.
- **HF s2s `CancelScope`:** một bộ đếm generation cộng cờ `discarding`, dùng chung giữa các thread của pipeline; các thread chụp generation lúc bắt đầu response và kiểm `is_stale(gen)` mỗi token (**Reported**).[^engine] Nó là cơ chế **lọc**, không phải cơ chế **dừng**. Cần cả hai (Chương 17 §17.6.1).

### 18.4.6 Trình tự cancel của Chương 17, viết bằng asyncio

Chương 17 §17.8.1 đặt thứ tự: stale hoá trước, clear vượt hàng, huỷ LLM, huỷ TTS, flush. Ánh xạ sang code (Script 7, `cancel_response`):

```python
async def cancel_response(self, reason, clear=True):
    old = self.gid
    self.gid += 1                                   # 1. stale hoá: không await trước dòng này
    if clear:
        await self.send_ctrl(("clear", old))        # 2. clear vào hàng ưu tiên 0, vượt audio
    if self.resp_stop:
        self.resp_stop.set()                        # 3. cờ cho thread compute (T_release)
    if self.resp_task and not self.resp_task.done():
        self.resp_task.cancel()                     # 4. huỷ cả response scope (LLM + TTS)
        await asyncio.wait({self.resp_task})        #    chờ finally chạy xong
    while not self.audio_q.empty():
        self.audio_q.get_nowait()                   # 5. flush; cũng mở chỗ cho thread đang chặn
```

Chú ý dòng 4. Cách viết hay gặp là `with contextlib.suppress(CancelledError): await self.resp_task`. Nó có một lỗ hổng: nếu **chính owner** bị huỷ đúng lúc đang chờ (ví dụ session scope đang đóng), `CancelledError` của owner cũng bị `suppress` nuốt, và owner chạy tiếp như chưa có gì. `await asyncio.wait({task})` chờ task con kết thúc mà **không** ném lỗi của task con, nhưng vẫn để `CancelledError` của owner lan ra bình thường. Phiên bản đầu của Script 7 dùng `suppress`; bản ở Phụ lục đã đổi sang `asyncio.wait`.

---

## 18.5 Producer/consumer, bounded queue, backpressure (Q2, Q5)

### 18.5.1 Vì sao phải bounded: một mô phỏng

Script 3 mô phỏng uplink: frame 20 ms đến đều; consumer (nhánh VAD + feed ASR) tốn 25 ms mỗi frame trong 5 s đầu (ví dụ GPU bị LLM tranh), sau đó 15 ms mỗi frame (**Reproduced**, mô hình rời rạc):

| Policy | Trễ max | Trễ ở t = 5 s | Hồi phục (< 60 ms) lúc | Frame bỏ |
|---|---|---|---|---|
| Queue không giới hạn | 1 020 ms | 1 020 ms | 7,89 s | 0 |
| Bounded 5 + **drop-oldest** | 120 ms | 120 ms | 5,13 s | 46 |
| Bounded 5 + **chặn producer** | 1 020 ms | 1 020 ms | 7,89 s | 0 |

Đọc bảng:

- **Queue không giới hạn** biến 5 s chậm tạm thời thành 1 s trễ, và cái trễ đó **kéo dài thêm 2,9 s** sau khi consumer đã nhanh trở lại, vì backlog phải được tiêu hết với phần dư (1/15 − 1/20 frame/ms). Trong 2,9 s đó, VAD đang phán xét audio của 1 s trước: user đã ngắt lời mà bot vẫn nói, user đã im mà hệ thống chưa biết.
- **Drop-oldest** giữ trễ ≤ 120 ms suốt thời gian chậm và hồi phục ngay. Cái giá: 46 frame (0,92 s audio) không được phân tích. Cái giá này phải được **đánh dấu** (gap trên timeline, Chương 16 §16.6.3) và **đếm** (metric `uplink_dropped`).
- **Chặn producer** không giúp gì. Producer của uplink là `ws_reader`; chặn nó thì frame nằm chờ trong socket buffer của kernel, rồi trong buffer gửi của client. Trễ y hệt queue không giới hạn, chỉ là **chuyển chỗ** ra ngoài tầm nhìn của bạn. Mic không chờ ai.

Đây là câu trả lời cho Q2: bounded queue chặn trên **độ trễ** (và bộ nhớ), biến "chậm tạm thời" thành "mất dữ liệu có kiểm soát" thay vì "trễ vĩnh viễn". Backpressure đúng nghĩa (làm producer chậm lại) chỉ có ích khi producer **chậm lại được** mà không mất ý nghĩa: LLM sinh text, TTS sinh audio. Mic, và người nói, thì không.

### 18.5.2 Policy cho từng cạnh

| Cạnh | Producer chậm lại được? | Policy | Ghi chú |
|---|---|---|---|
| Uplink audio → VAD/ASR | Không (mic) | **Drop-oldest**, đánh dấu gap, đếm | Không bao giờ để VAD phân tích audio cũ hơn vài trăm ms (Chương 8 §8.5.4)[^ch8] |
| Partial ASR (progressive window) | Có, và chỉ cái mới nhất có giá trị | **Latest-only** (gộp): giữ đúng một cửa sổ đang chờ | HF s2s: một request progressive active mỗi pipeline, chỉ giữ cửa sổ tích luỹ mới nhất đang chờ; final huỷ progressive đang chạy (**Reported**)[^backends] |
| Final ASR theo lượt | Không nên bỏ | Bounded, **từ chối có thông báo** khi đầy | HF s2s: tối đa 8 final chờ cộng 1 đang chạy mỗi pipeline; quá thì trả `TranscriptionFailure` không upload (**Reported**)[^backends] |
| Inbox của owner (control) | — | **Không bao giờ bỏ**; không giới hạn nhưng phải được tiêu thụ nhanh | Mất `turn.commit`, `client.clear` là bug logic (Chương 16 §16.2.2) |
| LLM text → chunker → TTS | Có | **Chặn producer** (`await q.put`) với queue nhỏ (1–2 mệnh đề) | LLM sinh trước quá xa chỉ tốn compute khi bị ngắt |
| TTS audio → downlink | Có | **Chặn producer** + **credit** theo played offset | Không bỏ giữa câu: nhảy tiếng nghe được (Chương 8 §8.5.4)[^ch8] |
| Send loop: control vs audio | — | **Hàng ưu tiên**: control (prio 0) vượt audio (prio 1) | `clear` không được xếp sau audio đang chờ (Chương 17 §17.8.1) |

### 18.5.3 Hiện thực trong asyncio

`asyncio.Queue(maxsize=n)` có sẵn hai hành vi: `await put()` chờ khi đầy (chặn producer), `put_nowait()` ném `QueueFull`. Hai policy còn lại phải tự viết, và vì asyncio chạy một thread, chúng không cần lock (**Synthesis**):

```python
def put_drop_oldest(q: asyncio.Queue, item, on_drop):
    if q.full():
        q.get_nowait()                     # bỏ phần tử cũ nhất
        on_drop()                          # đếm + đánh dấu gap
    q.put_nowait(item)

class LatestOnly:                          # một ô; giá trị mới ghi đè giá trị chưa được lấy
    def __init__(self):
        self._v, self._ev = None, asyncio.Event()
    def put(self, v):
        self._v = v; self._ev.set()
    async def get(self):
        await self._ev.wait(); self._ev.clear()
        v, self._v = self._v, None
        return v
```

Hàng ưu tiên cho send loop: `asyncio.PriorityQueue` với khoá `(prio, seq)`, trong đó `seq` là bộ đếm tăng dần để giữ FIFO trong cùng mức ưu tiên và để không bao giờ phải so sánh hai payload. Python 3.13 có thêm `Queue.shutdown()` để đánh thức mọi bên đang chờ khi đóng; với 3.11–3.12, dùng huỷ task là đủ.

### 18.5.4 Chuỗi backpressure downlink, và bẫy worker dùng chung

Chuỗi trong Script 7, từ loa ngược về nguồn:

```text
loa kéo 80 ms ──► client báo played ──► credit (sent − played < 480 ms) ──► pacer chờ
     ──► audio_q (maxsize 4) đầy ──► thread TTS chặn ở run_coroutine_threadsafe(...).result()
     ──► TTS ngừng sinh frame mới
```

Lợi ích: lượng audio chưa phát bị chặn trên (≤ 480 ms + 4 chunk), nên barge-in chỉ phải flush chừng đó; và TTS không sinh trước quá xa những thứ có thể bị huỷ.

**Bẫy quan trọng (Synthesis):** trong Script 7, thread TTS là **một thread dùng chung** (executor 1 worker, như "một thread sở hữu GPU"). Với một session thì ổn. Với nhiều session, một client chậm sẽ chặn thread đó, và **mọi session khác** ngừng nhận audio. Quy tắc:

> Đừng để backpressure của một session chặn một worker dùng chung. Backpressure phải dừng ở biên của tài nguyên dùng chung, bằng một buffer **theo session** có giới hạn.

Áp dụng cho TTS service có slot (VieNeu): slot được giữ cho tới khi request gặp EOS hoặc frame cap (**Reported**, qua Chương 17).[^vieneurt] Nếu gateway đọc HTTP response theo tốc độ phát (vì credit), thời gian giữ slot kéo dài từ "thời gian sinh" (RTF ~0,5) thành "thời gian phát" (RTF 1,0), tức **gần gấp đôi**, và sức chứa của server giảm tương ứng. Wiki không ghi server VieNeu xử lý thế nào khi client đọc chậm (hàng đợi audio theo request có giới hạn hay không): **Unverified**. Vì vậy, với TTS dùng chung, khuyến nghị (**Synthesis**):

- Gateway **đọc HTTP response hết tốc độ** vào một buffer theo generation, giới hạn theo độ dài mệnh đề tối đa (ví dụ ≤ 15 s audio ≈ 480 KB ở 16 kHz int16).
- Credit chỉ áp ở **downlink** (gateway → client), không áp ngược vào TTS service.
- Khi buffer theo generation chạm trần (mệnh đề quá dài), đó là lỗi của chunker, không phải chỗ để chặn TTS.

### 18.5.5 Ba con số phải đưa ra metric

Mỗi queue một bộ ba: **độ sâu hiện tại** (gauge), **số phần tử bị bỏ hoặc từ chối** (counter, theo lý do), **thời gian nằm trong queue** (histogram). Queue nào không có ba con số này thì sẽ là nơi bạn mất một tuần để tìm ra "vì sao bot phản ứng chậm vào giờ cao điểm".

---

## 18.6 Streaming I/O: async generator, HTTP/SSE, WebSocket

### 18.6.1 Async generator làm giao diện của stage

Một stage streaming tự nhiên nhất trong Python là async generator: `async def f(...): ... yield x`. Chunker đọc LLM stream, TTS adapter đọc chunk HTTP, tất cả là `async for`. Một chi tiết hay bị bỏ qua (kiến thức nền, PEP 525/533):

> `break` khỏi `async for` **không** đóng async generator ngay. `finally` của generator, nơi bạn đóng HTTP stream, chỉ chạy khi ai đó gọi `aclose()`, hoặc khi generator bị garbage collect và loop dọn nó.

Script 2 phần 4 (**Reproduced**): sau `break`, generator còn được biến giữ thì vẫn mở sau 50 ms, connection "LLM" vẫn mở; chỉ khi gọi `await gen.aclose()` thì `finally` mới chạy. Với `contextlib.aclosing(...)`, `finally` chạy **trước** dòng code ngay sau khối. Quy tắc: **mọi async generator bọc tài nguyên mạng đều được tiêu thụ trong `async with aclosing(...)`**:

```python
async with contextlib.aclosing(llm_stream(messages, gid)) as stream:
    async for delta in stream:
        ...
# tới đây: HTTP stream đã đóng, kể cả khi break, return, exception hay bị huỷ
```

### 18.6.2 LLM qua SSE (phác thảo, chưa chạy)

API kiểu OpenAI-compatible trả streaming dưới dạng Server-Sent Events: mỗi sự kiện là dòng `data: {...}`, kết thúc bằng `data: [DONE]` (Chương 12 §12.2). Phác thảo với `httpx` (thư viện client HTTP async phổ biến; không có trong môi trường chạy script nên đoạn này **chưa chạy**):

```python
async def llm_stream(client: httpx.AsyncClient, messages, gid):
    body = {"model": MODEL, "messages": messages, "stream": True}
    async with client.stream("POST", "/v1/chat/completions", json=body,
                             timeout=httpx.Timeout(connect=2.0, read=2.0, write=2.0, pool=1.0)) as r:
        r.raise_for_status()
        async for line in r.aiter_lines():           # read timeout = idle giữa hai dòng
            if not line.startswith("data: "):
                continue
            data = line[6:]
            if data == "[DONE]":
                return
            delta = json.loads(data)["choices"][0]["delta"].get("content")
            if delta:
                yield delta
    # thoát khối `async with` (kể cả do huỷ) = đóng response = đóng stream phía client
```

Ba điểm thiết kế:

- `read` timeout của httpx áp cho **mỗi lần đọc**, tức gần với "idle giữa hai chunk", không phải tổng. TTFT và tổng phải bọc thêm bằng `asyncio.timeout_at`.
- Dùng **một** `AsyncClient` dùng chung cho cả process (connection pool, keep-alive), không tạo mới mỗi request: handshake TLS mỗi lượt là latency thừa.
- Huỷ task đang chờ `aiter_lines()` là huỷ I/O: tức thì. Server LLM có dừng sinh hay không thì tuỳ engine; wiki chưa ghi nhận (**Unverified**, như Chương 17 §17.8.3).

### 18.6.3 TTS qua HTTP chunked: ranh giới byte lẻ

VieNeu `/v1/audio/speech` trả `200` với `Transfer-Encoding: chunked`, kèm header `X-Request-Id` và `X-Sample-Rate` (**Reported**).[^vieneuapi] Ranh giới chunk HTTP **không** được bảo đảm trùng ranh giới mẫu PCM16 (2 byte), càng không trùng ranh giới 20 ms. Một adapter đúng phải mang phần dư:

```python
async def pcm_frames(resp, frame_samples):
    sr = int(resp.headers["X-Sample-Rate"])           # đừng giả định; đọc từ header
    need = frame_samples * 2                          # PCM16 mono
    buf = bytearray()
    async for chunk in resp.aiter_bytes():
        buf += chunk
        while len(buf) >= need:
            yield sr, bytes(buf[:need]); del buf[:need]
    if len(buf) >= 2:
        yield sr, bytes(buf[: len(buf) // 2 * 2])     # đuôi: cắt về số chẵn byte
```

Nếu bỏ qua phần dư lẻ một byte, toàn bộ phần sau bị lệch byte: mỗi mẫu được ghép từ byte thấp của mẫu này và byte cao của mẫu kia, nghe như tiếng rè lớn. Đây là bug kiểu "chạy được trên máy dev (chunk luôn chẵn) và vỡ trên production (proxy cắt chunk khác)" (**Synthesis**). Contract của cạnh này (rate, kênh, dtype) đã có ở Chương 16 §16.3.5.

### 18.6.4 WebSocket: một reader, một writer

Mẫu cho kết nối client (**Synthesis**, khớp với HF s2s nơi `_send_loop` là consumer duy nhất của output queue, **Reported**):[^engine]

- **Một task đọc** (`ws_reader`): nhận frame, phân loại: binary → uplink (drop-oldest), JSON control → inbox. Khi kết nối đóng (bình thường hay lỗi), đẩy `session.end` vào inbox rồi kết thúc.
- **Một task ghi** (`send_loop`): là nơi **duy nhất** gọi `ws.send`. Hai task cùng gọi `send` trên một socket có thể xen kẽ frame tuỳ thư viện, và quan trọng hơn: phá vỡ điểm kiểm generation nguyên tử (Chương 17 §17.6.3).
- `await ws.send(...)` trong các thư viện WS async thường chỉ trả về khi dữ liệu được nhận vào buffer gửi (có high-water mark), nên `await` đúng chỗ cho backpressure tự nhiên; đừng dùng kiểu gửi "fire-and-forget" làm buffer phình ngầm (Chương 8 §8.5.2).[^ch8] Hãy kiểm tài liệu của thư viện bạn dùng.
- Keepalive (ping/pong) và timeout đóng kết nối để phát hiện client "chết im" (Chương 8 §8.4.5).

### 18.6.5 "Đóng connection để huỷ": bảo đảm được gì

| Đóng ở đâu | Bảo đảm | Không bảo đảm |
|---|---|---|
| Client đóng stream LLM (SSE) | Gateway ngừng nhận token ngay | Server ngừng sinh (tuỳ engine) |
| Client đóng `/v1/audio/speech` | Gateway ngừng nhận audio; HF s2s ngừng publish audio cục bộ (**Reported**)[^backends] | Server dừng compute; không có thao tác huỷ phía server chuẩn (**Reported**)[^backends] |
| Gateway đóng WS của user | User không nhận thêm gì | Các backend đang chạy cho user đó tự dừng: gateway phải tự huỷ (Chương 17 §17.10) |
| HF s2s huỷ STT HTTP | Cancellation còn hiệu lực trong suốt lúc thiết lập kết nối, upload và đọc response; dọn transport xong mới tái dùng worker (**Reported**)[^backends] | — |

Hệ quả: **đóng connection là điều kiện cần để huỷ, không phải điều kiện đủ để giải phóng compute**. Lọc theo generation vẫn bắt buộc, và T_release phải được đo, không được suy ra.

---

## 18.7 Cadence và throughput (Q6)

### 18.7.1 Định nghĩa

- **Throughput:** bao nhiêu đơn vị việc (giây audio, request) hệ thống hoàn thành mỗi giây, trung bình.
- **Cadence:** các đơn vị audio đến **đều đặn** đúng nhịp mà người nghe cần. Đo bằng phân phối khoảng cách giữa hai chunk, số lần underrun, và độ lệch so với lịch.

Ràng buộc realtime cho mỗi stage streaming (kiến thức nền, **Synthesis** khi áp vào đây): **P99 thời gian xử lý một chunk phải nhỏ hơn chu kỳ chunk, có biên**. Trung bình nhỏ hơn chu kỳ là không đủ: một stage trung bình 60 ms cho chunk 80 ms nhưng thỉnh thoảng 300 ms sẽ underrun đúng những lúc đó, trừ khi client pre-buffer lớn hơn 300 ms. Tài liệu thiết kế §9.3 đặt nguyên tắc: ưu tiên nhịp audio đều hơn throughput batch; và §10 mục 4: chỉ tăng concurrency khi vẫn đạt P95 và cadence (**Synthesis** của tài liệu thiết kế).[^design][^wikidesign]

### 18.7.2 Pacing: lịch tương đối trôi, lịch tuyệt đối thì không

Gửi frame 20 ms ra client bằng `await asyncio.sleep(0.02)` trong vòng lặp là cách viết tự nhiên và sai. Mỗi lần thức dậy trễ một chút (loop lag, độ phân giải timer), và độ trễ đó **cộng dồn**. Script 4 gửi 250 frame (5 s audio) trong khi trên loop có một task "ồn" chiếm 3 ms mỗi 7 ms (**Reproduced**):

| Cách pacing | Trôi sau 5 s | Lệch lịch max | Khoảng cách frame min / max |
|---|---|---|---|
| `await asyncio.sleep(0.02)` | **148,9 ms** | 148,9 ms | 20,2 / 21,0 ms |
| Lịch tuyệt đối: ngủ tới `t0 + k × 20 ms` | −2,8 ms | 3,0 ms | 17,3 / 21,1 ms |

Lịch tương đối gửi chậm hơn thời gian thực 3 %. Client phát đúng 1×, nên buffer của client cạn 149 ms mỗi 5 s; với pre-buffer 150 ms, câu trả lời dài hơn 5 s bắt đầu giật. Lịch tuyệt đối tự bù: frame nào trễ thì frame sau ngủ ít hơn, nên không trôi. Quy tắc (**Synthesis**): **mọi vòng lặp có nhịp (pacer, replay, timer định kỳ) đều tính hạn chót từ một mốc cố định**, dùng `time.monotonic()`/`perf_counter()` hoặc `loop.time()`, không bao giờ dùng đồng hồ tường (`time.time()` có thể nhảy khi NTP chỉnh).

Pacing theo thời gian là một nửa. Nửa kia là credit theo played offset (§18.5.4, Chương 8 §8.5.3): pacing giữ nhịp, credit giữ **trần**.

### 18.7.3 Batching: static batch hại cadence, continuous batching giữ được

GPU hiệu quả hơn khi gom nhiều stream vào một lần chạy. Câu hỏi là gom **thế nào**. Script 5 mô phỏng một GPU worker TTS: mỗi bước sinh một frame 80 ms cho mọi stream trong batch, tốn `c(B) = 30 + 3·B` ms (tham số giả định, chỉ giữ hình dạng "chi phí cố định lớn, phần theo B nhỏ"); mỗi response 4 s audio; client pre-buffer 160 ms; 10 phút mô phỏng (**Reproduced**):

| Chính sách | Tải | Phục vụ | Từ chối | TTFA p50 / p95 | Stream bị giật |
|---|---|---|---|---|---|
| A. Continuous batching, S = 16 slot | ~1,5 req/s | 882 | 0 | **60 / 86 ms** | 0 % |
| B. Static batch 8, chờ tối đa 300 ms | ~1,5 req/s | 882 | 0 | 1 013 / 2 010 ms | 0 % |
| C. Static batch 4, chờ tối đa 100 ms | ~1,5 req/s | 882 | 0 | 1 384 / 3 983 ms | 0 % |
| D. Continuous, S = 32, **không admission** | ~5 req/s | **2 988** | 0 | 899 / 5 033 ms | **98,1 %** (giật TB 1,8 s/stream) |
| E. Continuous, S = 14, queue 14, timeout 1 s | ~5 req/s | 2 308 | 680 | 649 / 1 039 ms | 0 % |
| F. Continuous, S = 14, queue 4, timeout 300 ms | ~5 req/s | 2 228 | 760 | 115 / 334 ms | 0 % |

Ba bài học:

1. **Static batching** (gom đủ batch rồi chạy batch đó tới hết) làm request mới phải chờ cả batch đang chạy kết thúc: TTFA cỡ giây dù GPU dư sức (B, C). Batch nhỏ hơn còn tệ hơn vì backlog. **Continuous batching** cho request mới vào batch ở bước kế tiếp: TTFA ≈ một bước (A). VieNeu GPU dùng đúng mô hình này: một CUDA graph với B slot, mỗi frame 80 ms là một lần replay cho mọi slot (**Reported**).[^vieneurt]
2. **D là câu trả lời cho ví dụ của Q6**: phục vụ nhiều request nhất (2 988), throughput cao nhất, nhưng 98 % stream bị giật trung bình 1,8 s. Lý do: với 20 stream đồng thời, `c(B) = 90 ms > 80 ms`, tức RTF > 1: mỗi stream nhận audio chậm hơn thời gian thực. Mọi người đều được phục vụ, và không ai nghe được trọn vẹn.
3. **Admission biến quá tải thành từ chối có kiểm soát** (E, F): giới hạn S sao cho `c(S) < 80 ms`, phần dư nhận `429`. F với hàng chờ ngắn cho TTFA p95 334 ms cho những ai được nhận, đổi lại 25 % bị từ chối và cần fallback (§18.8). Đây là cùng hình dạng với số đo VieNeu được báo trên RTX 3060: 32 stream đạt RTF 0,93 không giật nhưng audio đầu mất ~450 ms, không còn biên; 40 client (16 slot + 16 chờ) thì 32 thành công, 8 nhận `429`, request phải chờ trong hàng thấy TTFA 1,5–3 s (**Reported**).[^vieneurt]

Đối với ASR, câu chuyện khác một chút: ASR turn-final không có cadence (nó trả một lần mỗi lượt), nên gom batch qua `BatchedInferencePipeline` của faster-whisper cho một pool turn-final là hợp lý, miễn cửa sổ chờ gom nhỏ so với ngân sách endpoint→final (report gợi ý dùng nó cho turn-final, **Reported**).[^design][^fw] ASR streaming thì có cadence như TTS.

### 18.7.4 Quy tắc cadence

- Đo **P95/P99** thời gian xử lý một chunk, không đo trung bình. Đặt cảnh báo khi P99 tiến tới 70 % chu kỳ chunk (**Synthesis**, cùng tinh thần "RTF ≤ 0,6–0,7 để có biên" của VieNeu, **Reported**).[^vieneurt]
- Pacing theo lịch tuyệt đối; credit theo played offset; pre-buffer ở client cỡ 150–300 ms (Chương 6, Chương 16 §16.5.4).
- Gom batch kiểu continuous; không bao giờ để request mới chờ batch cũ chạy xong.
- Giới hạn số slot theo **tải thật** chứ không theo VRAM: VieNeu ghi mỗi slot thừa cộng ~2,5 ms vào **mọi** lần gọi codec của **mọi** người (**Reported**).[^vieneurt]

---

## 18.8 Admission control, 429, circuit breaker, deadline (Q7)

### 18.8.1 Ba tầng admission

| Tầng | Câu hỏi | Ví dụ trong wiki | Khi từ chối |
|---|---|---|---|
| **Session** | Nhận thêm cuộc hội thoại không? | HF s2s: `num_pipelines` là số pipeline cô lập trong pool, cũng là số session WS đồng thời tối đa; kết nối thêm bị từ chối (**Observed** trong argument class);[^cli] lỗi `session_limit_reached` (**Reported**)[^engine] | Báo bận ngay lúc kết nối, trước khi user nói |
| **Model / service** | Model này còn chạy thêm được một việc không? | VieNeu `VIENEU_MAX_STREAMS` (GPU 16, CPU 1), `VIENEU_QUEUE` (= max_streams), `VIENEU_QUEUE_TIMEOUT` 10 s; hết slot và hàng → `429` kèm `Retry-After` (**Reported**);[^vieneuapi] NeMo-Speech.cpp: inference chạy trên worker pool có giới hạn `--threads` (**Reported**)[^nemo] | `429`; gateway quyết định retry hay fallback |
| **Request** | Việc này còn kịp deadline không? | — (thiết kế) | Không gửi; fallback ngay |

Một điều HF s2s nói rõ và bạn nên mang theo: hàng đợi phía client của nó là **theo pipeline**, không có hàng admission dùng chung hay ngân sách đồng thời cho cả endpoint; sức chứa của STT server, định tuyến và quota thuộc về inference service hoặc proxy dùng chung (**Reported**).[^backends] Tức là: nếu bạn chạy 4 gateway cùng gọi 1 TTS service, giới hạn đồng thời phải đặt ở TTS service (hoặc một proxy trước nó), không thể trông vào từng gateway.

Admission theo session nên tính theo **stream đang dùng**, không theo **user**: VieNeu ước một user voice chat chỉ giữ stream TTS 20–35 % thời gian, nên 16 stream ≈ 45–80 user đang hoạt động (**Reported**).[^vieneurt] Cap session quá thấp lãng phí; cap quá cao thì giờ cao điểm mọi người cùng nhận `429`.

### 18.8.2 Retry theo deadline

Script 6 cho 8 session cùng xin TTS một lúc, server giả có 2 slot, 2 chỗ chờ, chờ tối đa 0,5 s, mỗi câu giữ slot 0,6 s, `429` kèm `Retry-After: 0,4 s` (**Reproduced**):

| Chiến lược client | Request tới server | Kết quả |
|---|---|---|
| Retry vô hạn, mỗi 50 ms | **94** | Ai cũng có audio, người cuối sau **2,1 s** |
| Deadline 1,2 s, tôn trọng `Retry-After` có jitter ±20 % | **19** | 4 session có audio trong 0,8 s; 4 session fallback (2 vì retry sẽ vượt deadline, 2 vì timeout) |

Retry vô hạn làm hai việc xấu: dội gấp 5 lần request vào server đang quá tải (làm nó chậm thêm cho mọi người), và để user chờ 2 s trong im lặng, quá ngưỡng mà một câu trả lời còn có giá trị hội thoại. Chiến lược deadline biết lúc nào nên dừng. Quy tắc (**Synthesis**):

```text
khi nhận 429 (Retry-After = r):
    nếu now + r ≥ deadline_audio_đầu_tiên:  fallback ngay
    ngược lại: ngủ r × uniform(0,8; 1,2) rồi thử lại     # jitter để các client không dội cùng lúc
khi lỗi kết nối/5xx: đếm vào circuit breaker, không retry ngay
```

### 18.8.3 Fallback trong hội thoại nói

Fallback cho voice khác fallback cho web: im lặng là một thông điệp tồi. Các lựa chọn, theo thứ tự ưu tiên thường gặp (**Synthesis**):

1. **Audio đệm dựng sẵn**: một vài câu ngắn đã tổng hợp từ trước với đúng giọng ("Dạ, anh chờ em một chút ạ."), phát từ cache, không cần TTS. Mua thêm 1–2 s để retry.
2. **Hỏi lại / xin lỗi ngắn** dựng sẵn khi chắc chắn không kịp.
3. **Text-only** nếu client có màn hình.
4. Đừng đổi sang TTS dự phòng **giữa câu**: giọng sẽ đổi. Tài liệu thiết kế §9.4: retry hoặc chuyển sang mệnh đề mới kèm thông báo trạng thái thay vì ghép hai giọng (**Synthesis** của tài liệu thiết kế).[^design]

Câu đệm cũng đi qua owner như một response bình thường: có `generation_id`, có thể bị barge-in, có played offset. Đừng ghi câu đệm vào history như thể LLM đã nói, hoặc ghi kèm nhãn để LLM biết.

### 18.8.4 Circuit breaker và health

Khi một service sập, mỗi lời gọi tới nó tốn trọn connect timeout trước khi thất bại. Circuit breaker cắt chuỗi đó (kiến thức nền):

```text
CLOSED ──(N lỗi liên tiếp)──► OPEN ──(hết cooldown)──► HALF-OPEN ──(1 request thử OK)──► CLOSED
                                 │ fail-fast, không gọi           └──(thử lỗi)──► OPEN
```

Script 6 phần 3 (**Reproduced**): TTS "sập", mỗi lần gọi mất 300 ms rồi lỗi. Lượt đầu mất 902 ms (3 lần thử) rồi breaker mở; ba lượt sau fallback trong **0 ms**, server không nhận thêm request nào. Sau 1,1 s, TTS phục hồi, breaker cho một request thử, thành công trong 81 ms, và đóng lại.

Breaker phối hợp với health check của service: VieNeu `/health` trả `active`, `waiting`, `max_streams`, và `503` khi bộ lập lịch GPU đã chết (không tự phục hồi; healthcheck Docker khởi động lại container) (**Reported**);[^vieneuapi] NeMo-Speech.cpp `/health` và `/ready` trả `503` khi engine chưa sẵn sàng (**Reported**).[^nemo] Readiness chỉ báo sẵn sàng **sau warmup** (tài liệu thiết kế §9.1).[^design] Một breaker tốt dùng cả hai tín hiệu: lỗi thực tế của request và trạng thái health.

### 18.8.5 Deadline theo session

Ngoài deadline theo lượt, mỗi session cần các giới hạn để tài nguyên không bị giữ vô hạn (**Synthesis**):

- **Thời lượng tối đa:** NeMo-Speech.cpp mặc định nhận 300 s audio input cho một session VoiceChat (`s2s.max_session_seconds`); socket đọc/ghi timeout 30 s (**Reported**).[^nemo]
- **Idle timeout:** không có speech trong X phút → đóng session.
- **Rate limit theo session:** số lượt, số request TTS mỗi phút; chống một client lỗi (hoặc độc hại) chiếm hết slot.
- **Kích thước turn buffer tối đa** (Chương 16 §16.5.3).

Mọi giới hạn khi chạm đều đi qua owner như một sự kiện (`session.end` với lý do), để teardown chạy đúng trình tự của Chương 17 §17.10.

---

## 18.9 Ghép lại: khung runtime cho một session

Hai report trong wiki có phác thảo gateway asyncio, và đều đáng đọc như **dàn ý**, không như code chạy được. Blueprint phác thảo một `VoiceSession` giữ bốn `asyncio.Queue` (audio, utterance, text, TTS) cùng `generation_id`, chạy bởi năm coroutine (`audio_receiver`, `vad_worker`, `asr_worker` gọi Whisper qua `asyncio.to_thread`, `llm_worker`, `tts_worker`) (**Reported**); đọc tĩnh thì phác thảo đó không xoá TTS queue khi ngắt, tăng `generation_id` ngay ở frame đầu vượt ngưỡng, và truyền bytes PCM thô vào `whisper.transcribe` (**Observed**).[^blueprint] Report stack tiếng Việt có reference server FastAPI + WebSocket asyncio (`VADIterator` mỗi session, gate barge-in 400 ms, transcription qua `asyncio.to_thread`, LLM stream sang TTS queue worker, message `{"type":"clear"}`) và khuyên nối các stage bằng async queue (**Reported**).[^stack] Theo mô tả trong wiki, không phác thảo nào nói tới drop policy theo cạnh, credit downlink, cờ stop cho compute, admission hay kiểm rò task (**Synthesis**, chỉ dựa trên phần wiki tóm tắt, chưa đọc code gốc).

Script 7 ở Phụ lục ghép mọi thứ của chương thành một runtime chạy thật theo thời gian thực (~4,4 s), với backend giả:

```text
session TaskGroup
 ├─ replay        frame 20 ms theo lịch tuyệt đối + jitter 0–8 ms → uplink (drop-oldest) + sự kiện VAD
 ├─ vad_consumer  tiêu thụ uplink (~2 ms/frame)
 ├─ owner         inbox → quyết định (commit, barge-in, session.end); MỘT nơi tăng generation
 ├─ pacer         audio_q → out, theo credit (≤ 480 ms chưa phát)
 ├─ send_loop     writer DUY NHẤT; control prio 0 vượt audio; kiểm generation ngay trước khi gửi
 ├─ lag_monitor
 └─ client.playback (client giả: mạng 20–40 ms giữ thứ tự, guard floor, loa kéo 80 ms, báo played)
response task (mỗi generation): TaskGroup{ llm_chunker (async gen + aclosing), tts_stage (executor "GPU") }
```

Trace (**Reproduced**, độ trễ backend là tham số giả định; jitter mạng giả lập nên các mốc lệch vài ms giữa các lần chạy):

```text
  1102 ms   turn.commit → response gen 1: «Cho em hỏi lịch hẹn thứ sáu»
  2705 ms   BARGE-IN (đã qua gate) khi gen 1 đang phát
  2706 ms   cancel gen 1 (turn_detected); generation hiện hành = 2
  2728 ms   thread GPU nhả gen 1 (thấy cờ stop)
  3309 ms   turn.commit → response gen 3: «Khoan, đổi sang thứ bảy»
  4306 ms   session.end → teardown
  4306 ms   cancel gen 3 (session_end); generation hiện hành = 4
  4307 ms   thread GPU nhả gen 3 (thấy cờ stop)

--- kiểm tra sau teardown ---
generation cuối = 4; client đã phát (ms) theo gen: {1: 1237, 3: 640}
barge-in: owner quyết định 2705 ms → client nhận clear 2735 ms → mẫu cuối gen 1 phát xong 2735 ms; thread GPU nhả 2728 ms
guard=bật: server bỏ 4 chunk stale; chunk generation cũ được phát sau clear: 0
task còn sống ngoài main: 0; thread GPU bận: False; uplink frame bị bỏ: 0
loop lag p99 1.4 ms, max 2.3 ms
```

Chạy lại với `--no-guard` (tắt kiểm generation ở pacer, send loop và client):

```text
barge-in: owner quyết định 2705 ms → client nhận clear 2735 ms → mẫu cuối gen 1 phát xong 2901 ms; thread GPU nhả 2728 ms
guard=TẮT: server bỏ 0 chunk stale; chunk generation cũ được phát sau clear: 2
```

Đọc kết quả:

- **Time-to-silence** (từ quyết định) là 30 ms khi có guard: đúng bằng độ trễ mạng của `clear`, vì `clear` vượt hàng và client flush cả chunk đang phát. Không có guard, 2 chunk (160 ms) đang nằm trong `out`/đang bay vẫn tới client sau `clear` và được phát: bot im tới 2901 ms, muộn hơn 166 ms. (Một lần chạy khác của phiên bản trước cho 3 chunk, muộn 241 ms: số chunk rò phụ thuộc lúc barge-in rơi vào đâu trong nhịp pacer, nhưng cả hai lần chạy không guard đều có chunk cũ lọt ra loa.) Cùng hiện tượng với kịch bản C của Chương 17 §17.8.4, nay tái hiện trên runtime asyncio thật.
- **Time-to-release** là 23 ms: thread GPU thấy cờ stop ở ranh giới bước 30 ms kế tiếp (hoặc khi đang chặn ở `push`, trong vòng 50 ms). Không có cờ stop, thread sẽ chạy hết mệnh đề.
- **Teardown sạch:** không còn task nào ngoài `main`, thread GPU rảnh. Generation tăng đơn điệu cả session (1 → 2 khi huỷ, 3 cho lượt mới, 4 khi đóng).
- **Loop lag** p99 1,4 ms: không có việc nặng nào trên loop.

**Một bug thật gặp khi viết script này.** Phiên bản đầu của `Client.playback` tạo task con `asyncio.ensure_future(asyncio.sleep(0.08))` để phát một chunk và có thể huỷ nó khi `clear` tới. Khi session đóng, `TaskGroup` huỷ `playback`, nhưng task con `sleep` thì không ai huỷ: kiểm tra sau teardown báo **"task còn sống ngoài main: 1"** (**Reproduced**). Sửa bằng `try/finally` huỷ task con. Đây chính là loại rò rỉ chỉ lộ ra khi bạn **kiểm `asyncio.all_tasks()` sau teardown trong test**, và là lý do mục đó có trong bảng test ở §18.10.

Những gì khung này **cố ý chưa làm** (**Synthesis**):

- Owner commit ngay khi `vad.end`, không có speculative reopen và output gate (đã có ở `TurnOwner` của Chương 17; ghép vào bằng cách thay hàm `owner`).
- Thread TTS là một thread dùng chung và bị backpressure chặn: đúng cho engine in-process một session, **sai** cho nhiều session (§18.5.4).
- `client.played` gửi mỗi chunk; thật thì gửi định kỳ (ví dụ mỗi 100–200 ms).
- Lỗi trong response (LLM/TTS ném exception) chưa được chuyển thành sự kiện `response.failed`; hiện tại nó sẽ lan lên `run_response` và kết thúc task đó.
- Không có VAD, ASR, mạng hay model thật.

---

## 18.10 Test pipeline realtime mà không cần mic (Q8)

### 18.10.1 Ba tầng test

| Tầng | Đồng hồ | Dùng để | Ví dụ |
|---|---|---|---|
| **Unit / logic** | Không có đồng hồ thật: sự kiện có timestamp, hoặc đồng hồ giả tiêm vào | State machine, guard, policy queue, retry | `TurnOwner` và `ClientGuard` của Chương 17; `queue_sim.py`, `batching_sim.py` |
| **Runtime asyncio** | Đồng hồ thật, tốc độ 1× (hoặc nhanh hơn khi không đo cadence) | Huỷ, timeout, backpressure, rò task, loop lag | `session_runtime.py` |
| **Hệ thống** | Thật, với model và mạng thật | Latency, T_silence, T_release, cadence dưới tải | Replay file audio thật qua WS tới gateway thật, concurrency 1/4/8/16 |

Tầng thứ nhất nhanh và tất định: hãy đẩy càng nhiều logic xuống đó càng tốt. Để làm được, code phải **nhận đồng hồ làm tham số** (một hàm `now()` hoặc đối tượng clock) thay vì gọi `time.monotonic()` rải rác (**Synthesis**).

### 18.10.2 Replay theo thời gian thực

Replay một file WAV thành frame 20 ms gửi qua WS **theo lịch tuyệt đối** (§18.7.2): frame k gửi lúc `t0 + k × 20 ms`. Gửi cả file một lúc là test sai: gateway nhận 10 s audio trong 50 ms, VAD và turn detector chạy trên timeline không giống thật, và mọi lỗi phụ thuộc thời gian biến mất.

Các biến thể cần có (**Synthesis**):

| Biến thể | Cách tạo | Bắt được lỗi gì |
|---|---|---|
| Jitter | Mỗi frame trễ thêm `uniform(0, J)` ms, giữ thứ tự (WS/TCP) | Pre-buffer thiếu, giả định frame đến đều |
| Burst | Giữ 300 ms rồi xả một lúc | Reblock sai, VAD "ăn" nhiều frame một lần |
| Gap | Bỏ hẳn 200 ms giữa chừng | Policy gap (Chương 16 §16.6.3), timeline lệch |
| Disconnect | Đóng WS giữa lượt, giữa câu bot | Teardown, huỷ backend, callback muộn |
| Reconnect | Mở lại ngay cùng `session_id` | State cũ rò sang (Chương 17 §17.10) |
| Backend chậm | Stub LLM/TTS có TTFT/TTFA điều chỉnh được, hoặc treo giữa stream | Timeout first-byte và idle, fallback |
| `429` / `503` | Stub trả lỗi theo kịch bản | Retry theo deadline, breaker |
| Client chậm | Client giả phát chậm hơn 1× hoặc ngừng báo played | Credit, trần downlink, đóng kết nối client "chết" |
| Loop bị chiếm | Chèn một task chiếm loop 50–100 ms định kỳ | Hệ thống có xuống cấp êm không; cảnh báo loop lag có bắn không |

### 18.10.3 Bất biến kiểm sau mỗi kịch bản

Mỗi kịch bản kết thúc bằng một loạt `assert`, không phải bằng việc "nghe thử" (**Synthesis**; nhóm cuối khớp gate 5 của tài liệu thiết kế: cancel giữa chunk, disconnect/reconnect, timeout, 429, không stale audio, không duplicate final).[^design][^wikidesign]

- Không chunk nào của generation đã clear được phát sau khi client xử lý `clear` (đếm như Script 7).
- Sau teardown: `asyncio.all_tasks()` chỉ còn task của test; thread worker rảnh; executor không còn việc chờ; số file descriptor/socket về mức ban đầu.
- Mọi queue có độ sâu ≤ `maxsize`; số phần tử bị bỏ khớp với kịch bản (ví dụ 0 khi không có tải).
- Generation, sequence, revision tăng đơn điệu.
- Loop lag P99 dưới ngưỡng (ví dụ 5 ms) trong kịch bản không có tải nhân tạo.
- T_silence, T_release được ghi cho mọi barge-in.

### 18.10.4 Soak test cho rò rỉ

Chạy 1 000 session ngắn liên tiếp (mỗi session vài lượt, có barge-in, có disconnect), rồi so: số task, số thread, RSS, số socket mở, VRAM của service. Bất cứ thứ gì tăng tuyến tính theo số session là một rò rỉ. Rò rỉ trong voice agent hiếm khi là bộ nhớ audio (Chương 16 §16.5.5); thường là task, callback giữ tham chiếu session, hoặc slot backend không được trả.

---

## 18.11 Quan sát vận hành: metric tối thiểu cho runtime

| Metric | Loại | Vì sao |
|---|---|---|
| `loop_lag_ms` P50/P99/max theo process | Histogram | Chỉ báo sớm nhất của code blocking |
| `queue_depth{queue}`, `queue_dropped_total{queue,reason}`, `queue_wait_ms{queue}` | Gauge / counter / histogram | §18.5.5 |
| `executor_active{model}`, `executor_waiting{model}` | Gauge | Bão hoà executor, hàng chờ model |
| `tasks_per_session`, `sessions_active` | Gauge | Rò task |
| `backend_requests_total{service,status}` gồm `429`, timeout, lỗi kết nối | Counter | Admission, breaker |
| `breaker_state{service}` | Gauge | Service nào đang bị cắt |
| `retry_total`, `fallback_total{reason}` | Counter | Tần suất user nghe câu đệm |
| `downlink_lead_ms` (sent − played) | Histogram | Credit có hoạt động không |
| `client_underrun_total` (client báo về) | Counter | Cadence nhìn từ phía người nghe |
| `time_to_silence_ms`, `time_to_release_ms` | Histogram | Chương 17 §17.8.4 |

Log content-free theo mặc định (tài liệu thiết kế §9.5, HF s2s `--log_transcripts` là opt-in).[^design] Metric runtime không cần nội dung hội thoại.

---

## 18.12 Lỗi thường gặp: triệu chứng → nguyên nhân → cách sửa

| Triệu chứng | Nguyên nhân hay gặp | Cách sửa |
|---|---|---|
| Mọi session cùng "đơ" ~1 s khi một user nói xong | Lặp generator faster-whisper trên loop, hoặc `to_thread(model.transcribe)` rồi lặp trên loop | Gom `list(segments)` **trong** thread (§18.3.1) |
| Loop lag trung vị ~5 ms, tăng theo tải | CPU thuần Python trong thread tranh GIL | Process pool, numpy/native, hoặc tách service |
| Bot vẫn nói tiếp sau barge-in dù đã `cancel()` | Worker nuốt `CancelledError` (`except:` / `except BaseException`) | Ném lại `CancelledError` (§18.4.2) |
| Owner không dừng khi session đóng, dù đã bị huỷ | `suppress(CancelledError)` quanh `await task_con` nuốt luôn lệnh huỷ của owner | `await asyncio.wait({task_con})` (§18.4.6) |
| User nghe bot im, nhưng GPU vẫn bận, session khác chậm hoặc nhận `429` | Huỷ task không dừng thread/service; không có cờ stop | Cờ stop hợp tác theo bước; đo T_release (§18.4.3) |
| Connection tới LLM/TTS vẫn mở sau khi đã `break` | Async generator không được `aclose()` | `async with aclosing(...)` (§18.6.1) |
| Tiếng rè lớn giữa chừng câu TTS, chỉ trên production | Chunk HTTP lẻ byte; adapter không mang phần dư | Buffer phần dư, cắt về số chẵn byte (§18.6.3) |
| VAD phản ứng chậm dần vào giờ cao điểm rồi "mãi không hồi" | Uplink queue không giới hạn; backlog | Bounded + drop-oldest + đánh dấu gap (§18.5.1) |
| Câu trả lời dài bắt đầu giật sau vài giây | Pacing bằng `sleep(0.02)` tương đối, trôi | Lịch tuyệt đối (§18.7.2) |
| Một client mạng yếu làm mọi session giật | Backpressure của một session chặn worker dùng chung | Buffer theo session ở biên tài nguyên dùng chung (§18.5.4) |
| Sức chứa TTS chỉ bằng một nửa tính toán | Gateway đọc TTS theo tốc độ phát, slot bị giữ gấp đôi | Đọc hết tốc độ vào buffer theo generation; credit chỉ ở downlink |
| `clear` đến muộn hàng trăm ms | `clear` xếp sau audio trong cùng hàng | Hàng ưu tiên trong send loop; pace downlink (§18.5.2) |
| Giờ cao điểm: TTFA vài giây, rồi mọi stream đều giật | Không admission; slot quá nhiều, RTF > 1 | Cap slot theo `c(S) < chu kỳ`; `429` + fallback (§18.7.3) |
| Server bị dội request khi đang quá tải | Retry vô hạn, không jitter | Retry theo deadline, tôn trọng `Retry-After`, jitter (§18.8.2) |
| Mỗi lượt chờ đúng connect timeout khi TTS sập | Không có circuit breaker | Breaker + health (§18.8.4) |
| "Task exception was never retrieved" trong log, response im lặng | Task fire-and-forget nổ lỗi, không ai `await` | `TaskGroup`; response tự bắt lỗi và báo về owner |
| Số task tăng dần theo số session đã phục vụ | Task con không thuộc scope nào (như bug ở §18.9) | `TaskGroup`/`try-finally`; assert `all_tasks()` sau teardown |
| `RuntimeError`/hành vi lạ khi thread đẩy vào queue | Gọi `asyncio.Queue` trực tiếp từ thread | `call_soon_threadsafe` / `run_coroutine_threadsafe` (§18.3.4) |
| Executor mặc định nghẽn, việc nhỏ chờ việc lớn | Mọi `to_thread` dùng chung một pool | Executor riêng cho từng model, có semaphore (§18.3.3) |

---

## 18.13 Bài tập thực hành

1. **Bẫy `to_thread`.** Chạy `blocking_demo.py`. Sửa `FakeWhisper` để `transcribe()` tự gọi `list()` trước khi trả về. Cách B bây giờ cho kết quả thế nào? Vì sao bản thật của faster-whisper không làm vậy (gợi ý: lợi ích của generator khi audio dài)?
2. **GIL dưới tải.** Trong `blocking_demo.py`, chạy cùng lúc 4 lời gọi `e_pycpu_to_thread` bằng `asyncio.gather`. Loop lag p50 thay đổi ra sao? So với 4 lời gọi qua `ProcessPoolExecutor(4)`.
3. **Độ mịn của cờ stop.** Trong `cancel_demo.py`, đổi bước inference từ 100 ms thành 20 ms và 500 ms. Ghi lại thời gian từ `stop.set()` đến lúc thread rảnh. Viết công thức cận trên.
4. **Policy uplink.** Trong `queue_sim.py`, thêm policy "bounded 5 + drop-newest". So độ trễ và ý nghĩa với drop-oldest. Khi nào drop-newest lại hợp lý (gợi ý: nghĩ về một hàng đợi lệnh, không phải audio)?
5. **Pacing dưới tải nặng hơn.** Trong `pacing.py`, đổi task ồn thành 15 ms mỗi 20 ms. Lịch tuyệt đối còn giữ được không? Khoảng cách frame max là bao nhiêu? Pacer nên làm gì khi đã trễ hơn một chu kỳ (gửi dồn hay bỏ lịch)?
6. **Chọn S.** Trong `batching_sim.py`, quét `S` từ 8 tới 24 với tải 5 req/s, queue 4, timeout 300 ms. Vẽ TTFA p95, tỷ lệ từ chối và tỷ lệ giật theo S. Điểm gãy nằm ở đâu, và nó khớp với `c(S) = 80 ms` không?
7. **Breaker chia sẻ.** Trong `admission.py`, cho 8 session dùng chung một `Breaker` khi TTS sập. Bao nhiêu request tới server trước khi breaker mở? So với mỗi session một breaker riêng.
8. **Response lỗi.** Trong `session_runtime.py`, cho `fake_llm` ném `RuntimeError` sau 5 token. Sửa `run_response` để lỗi thành sự kiện `("response.failed", gid)` gửi vào inbox, session không chết, lượt sau vẫn chạy. Thêm assert.
9. **Nhiều session.** Chạy 4 `Session` trên cùng loop và cùng executor "GPU". Cho client của session 2 phát chậm 0,5×. Quan sát các session khác. Sửa theo §18.5.4 (buffer theo session, không chặn thread dùng chung) và chứng minh bằng số đo.
10. **Đo thật (Reproduced nếu bạn làm).** Dựng faster-whisper `turbo` thật trong executor riêng, chạy 4 session replay file WAV tiếng Việt 1× qua WS. Ghi loop lag, hàng chờ executor, endpoint→final P50/P95. Sau đó cố ý đổi sang cách B và ghi lại.

---

## 18.14 Đáp án các câu hỏi tự kiểm tra

**Q1.** `transcribe()` của faster-whisper trả về generator; decode chỉ chạy khi lặp. Lặp trên event loop nghĩa là toàn bộ decode (hàng trăm ms tới vài giây) chạy giữa hai điểm `await`, nên loop không phục vụ được gì khác: VAD của mọi session trễ, audio downlink ngừng, `clear` không gửi được. Script 1: loop lag max 899 ms, 26 frame VAD liên tiếp muộn. `await asyncio.to_thread(model.transcribe, audio)` chưa sửa được vì nó chỉ đưa việc **tạo** generator sang thread (tức thì), còn việc **lặp** (tức decode) vẫn ở trên loop: loop lag max 903 ms, y như không có thread. Sửa: đưa cả `list(segments)` vào hàm chạy trong thread (loop lag max 1,9 ms).

**Q2.** Bounded queue chặn trên độ trễ và bộ nhớ: một lần chậm tạm thời không biến thành trễ kéo dài. Không giới hạn, 5 s consumer chậm 25 % tạo 1 s backlog và kéo dài thêm 2,9 s sau khi đã hết chậm (Script 3); trong lúc đó hệ thống ra quyết định trên audio cũ, barge-in đến muộn, và khi bị ngắt phải flush cả đống audio. Backpressure (làm producer chậm lại) ngăn LLM/TTS sinh trước quá xa những thứ sẽ bị huỷ và giữ lượng audio chưa phát ở mức nhỏ để barge-in nhanh. Với nguồn không chậm lại được (mic), bounded queue phải đi kèm policy bỏ (drop-oldest) có đếm và đánh dấu gap.

**Q3.** Task chờ I/O không có gì đang chạy: `cancel()` ném `CancelledError` ở điểm `await`, `finally` đóng connection, xong ngay (Script 2: 0 ms). Inference đang chạy trong thread hoặc trên GPU không thể bị ngắt từ ngoài: `cancel()` chỉ huỷ asyncio future bọc ngoài, `await` trả về ngay, nhưng thread chạy tiếp tới khi xong (765 ms) hoặc tới khi tự kiểm cờ stop ở ranh giới bước (50 ms). Inference ở service khác thì đóng connection chỉ bảo đảm phía client ngừng nhận; server dừng hay không là best-effort. Vì vậy: lọc theo generation để bảo đảm time-to-silence, và thiết kế compute chia bước có cờ stop để rút ngắn time-to-release.

**Q4.** Coroutine trên loop cho việc chỉ chờ (socket, HTTP, timer). Inline cho việc CPU rất ngắn, nhưng tính chi phí nhân với số session. Executor riêng cho từng model (qua `run_in_executor`/`to_thread`) khi thư viện native nhả GIL và chấp nhận model nằm chung process với gateway (MVP). Process pool cho CPU thuần Python nặng (GIL làm thread không đủ: Script 1 E đẩy loop lag p50 lên 5,2 ms). Worker service riêng khi model GPU dùng chung nhiều gateway, cần cô lập lỗi/OOM, hoặc dependency xung đột (tài liệu thiết kế §9.1): gateway khi đó chủ yếu là I/O-bound.

**Q5.** Uplink đầy: bỏ frame **cũ nhất**, đếm, đánh dấu gap; audio cũ đã mất giá trị cho VAD. Chặn producer ở uplink chỉ đẩy backlog ra socket buffer và client: trễ y như queue không giới hạn (Script 3: 1 020 ms), chỉ là không nhìn thấy. Downlink đầy: **chặn producer** (TTS) và áp credit theo played offset, không bỏ giữa câu vì nhảy tiếng nghe được; riêng TTS dùng chung thì đọc hết tốc độ vào buffer theo session và áp credit ở downlink để không giữ slot lâu. Control: không bao giờ bỏ, và vượt hàng audio.

**Q6.** Người nghe cần audio đến đúng nhịp; một khoảng trống 300 ms giữa câu là lỗi nghe được, dù trung bình hệ thống nhanh. Throughput là trung bình, cadence là phân phối đuôi. Ví dụ (Script 5, D): continuous batching không admission ở tải 5 req/s phục vụ 2 988 response, nhiều nhất trong mọi cấu hình, nhưng 98 % stream bị giật trung bình 1,8 s vì batch 20 stream làm mỗi bước 90 ms > 80 ms (RTF > 1). Cap 14 slot kèm hàng chờ ngắn phục vụ ít hơn (2 228) và từ chối 25 %, nhưng không ai bị giật và TTFA p95 334 ms. Static batching còn tệ hơn: TTFA cỡ giây ngay ở tải vừa vì request mới chờ batch cũ.

**Q7.** Không retry mù. Tính deadline cho audio đầu tiên của lượt; nếu `now + Retry-After` vượt deadline thì fallback ngay, nếu không thì chờ `Retry-After` có jitter rồi thử lại. Fallback cho voice: phát một câu đệm dựng sẵn bằng đúng giọng ("Dạ, anh chờ em một chút ạ.") để mua thời gian, hoặc câu xin lỗi ngắn, hoặc text-only; không đổi TTS giữa câu. Đếm `429` vào metric; nếu là lỗi kết nối/5xx thì đếm vào circuit breaker để fail-fast. Về lâu dài: `429` thường xuyên nghĩa là cap session quá cao so với slot TTS, cần chỉnh admission ở tầng session hoặc thêm GPU (Script 6: retry vô hạn dội 94 request và để người cuối chờ 2,1 s; chiến lược deadline dùng 19 request và mọi người có câu trả lời hoặc fallback trong ≤ 1,2 s).

**Q8.** Ba tầng. Logic (owner, guard, policy) test bằng sự kiện có timestamp hoặc đồng hồ giả, không cần thời gian thật. Runtime asyncio test bằng replay file audio theo **lịch tuyệt đối** 20 ms qua WS tới gateway, với backend stub có TTFT/TTFA, lỗi `429`/`503`, treo giữa stream; thêm biến thể jitter, burst, gap, disconnect, reconnect, client chậm, loop bị chiếm. Mỗi kịch bản kết thúc bằng assert: không chunk cũ nào phát sau `clear`, không còn task/thread/socket sau teardown, queue không vượt `maxsize`, generation đơn điệu, loop lag dưới ngưỡng, có T_silence/T_release. Thêm soak test 1 000 session để bắt rò rỉ, và load test concurrency 1/4/8/16 cho cadence.

---

## 18.15 Tóm tắt một trang

- **Event loop là tài nguyên dùng chung.** Mỗi mili giây chiếm loop là một mili giây mọi session đứng chờ. Đo loop lag từ ngày đầu; bật debug mode trong test.
- **Đẩy cả phần tiêu thụ lười sang thread.** `to_thread(model.transcribe)` rồi lặp trên loop vẫn block (899–903 ms). Đúng: `list(segments)` trong thread.
- **GIL:** native nhả GIL → thread được; Python thuần → process pool hoặc service. Mỗi model một executor riêng có semaphore.
- **Huỷ task ≠ dừng compute.** I/O dừng ngay; thread/GPU chạy tiếp tới khi tự kiểm cờ stop hoặc xong. Lọc theo generation cho time-to-silence; cờ stop theo bước cho time-to-release. Không bao giờ nuốt `CancelledError`.
- **Structured concurrency:** session scope và response scope bằng `TaskGroup`; huỷ response là huỷ một scope; lỗi response không giết session; kiểm `all_tasks()` sau teardown.
- **Mọi queue đều bounded, mỗi cạnh một policy:** uplink drop-oldest có đánh dấu gap; partial ASR latest-only; text/audio chặn producer + credit; control không bao giờ bỏ và vượt hàng.
- **Backpressure dừng ở biên tài nguyên dùng chung.** Đừng để một client chậm chặn thread GPU chung hay giữ slot TTS gấp đôi.
- **Streaming I/O:** async generator trong `aclosing`; bốn loại timeout (connect, first byte, idle, tổng) dưới một deadline tuyệt đối; PCM chunked phải mang phần dư byte lẻ; một reader, một writer cho mỗi WS.
- **Cadence trước throughput:** pacing theo lịch tuyệt đối (lịch tương đối trôi 149 ms/5 s); continuous batching, không static; cap slot sao cho bước < chu kỳ chunk.
- **Admission ba tầng** (session, model, request); `429` xử lý theo deadline với jitter; fallback bằng câu đệm dựng sẵn; circuit breaker + health.
- **Test không cần mic:** replay theo lịch tuyệt đối với jitter, gap, disconnect, backend stub; assert bất biến; soak test cho rò rỉ.

---

## Hạn chế và phạm vi bao phủ

- Chương không chạy faster-whisper, VieNeu, LLM, HF s2s hay Pipecat thật. Tám script dùng model giả lập (`time.sleep` cho kernel native nhả GIL, vòng lặp số học cho CPU thuần Python). Hành vi của `asyncio`, thread, GIL, `TaskGroup`, `aclosing`, debug mode là **Reproduced** trên CPython 3.12.3; con số độ trễ phụ thuộc máy và chỉ có ý nghĩa so sánh giữa các cách viết.
- Giả định "thư viện native nhả GIL khi chạy kernel" là kiến thức nền; mức độ nhả GIL của từng phiên bản CTranslate2/ONNX Runtime/PyTorch, và lượng việc Python giữ GIL quanh kernel, chưa được đo ở đây. Hãy xác nhận bằng loop lag trên stack thật (bài tập 10).
- Mô hình batching (`c(B) = 30 + 3·B`) và server TTS giả (2 slot, `Retry-After` 0,4 s) là tham số chọn để minh hoạ hình dạng hành vi, không phải mô hình của VieNeu. Số đo VieNeu dẫn trong chương là **Reported** từ tài liệu của tác giả, chỉ đo trên RTX 3060.
- PR #5931 của Pipecat được dẫn qua AI report thứ cấp; PR không có trong `raw/`. Generator semantics của faster-whisper thì có trong README đã capture (**Reported**).
- Phác thảo LLM qua SSE dùng `httpx` **chưa chạy** (thư viện không có trong môi trường). Tên tham số timeout của httpx và hành vi `send` của thư viện WebSocket là kiến thức nền, cần kiểm với phiên bản bạn dùng.
- Hành vi server LLM khi client đóng stream, và việc VieNeu xử lý client đọc chậm (hàng đợi audio theo request có giới hạn hay không, slot có giải phóng sớm khi ngắt kết nối không) chưa được wiki ghi nhận (**Unverified**).
- Khuyến nghị "đọc TTS hết tốc độ, credit chỉ ở downlink", các giá trị timeout khởi điểm, chính sách fallback bằng câu đệm, và bảng metric là thiết kế của chương (**Synthesis**), chưa đo trên hệ thật.

---

## Phụ lục chương

Tất cả script nằm ở `/tmp/ch18/`, chạy bằng `python3 <tên>.py` (Python 3.11+ vì dùng `TaskGroup`, `asyncio.timeout_at`, `except*`). Không cần thư viện ngoài.

### Script 1: code blocking làm đứng event loop (`/tmp/ch18/blocking_demo.py`, đã chạy)

Sáu cách chạy cùng một việc nặng trong khi một task giám sát đo loop lag mỗi 10 ms và một task giả lập nhánh VAD cần xử lý frame 32 ms theo đồng hồ tuyệt đối. A–C: `FakeWhisper` có generator lười (6 × 150 ms `time.sleep`, nhả GIL). D–F: vòng lặp số học thuần Python ~0,8 s (giữ GIL). Dùng ở §18.3.1 và §18.3.2.

```python
# Chương 18 — Script 1: code blocking làm đứng event loop.
# Mô phỏng faster-whisper: transcribe() trả về (generator lười, info); việc decode thật
# chạy khi LẶP generator. Decode native được giả lập bằng time.sleep (nhả GIL như
# CTranslate2/ONNX/PyTorch khi chạy kernel). CPU thuần Python giả lập bằng vòng lặp số học.
# Đo: độ trễ của event loop (loop lag) và số frame VAD 32 ms bị xử lý muộn > 50 ms.
import asyncio, time, statistics, concurrent.futures as cf

SEG_S, N_SEG = 0.15, 6                        # 6 segment × 150 ms = 0.9 s decode

class FakeWhisper:
    def transcribe(self, audio):
        def segments():
            for i in range(N_SEG):
                time.sleep(SEG_S)             # "kernel native", nhả GIL
                yield f"seg{i}"
        return segments(), {"language": "vi"}

def py_cpu(n=25_000_000):                       # CPU thuần Python, GIỮ GIL
    s = 0
    for i in range(n):
        s += i * i
    return s

async def lag_monitor(stop, out, period=0.010):
    while not stop.is_set():
        t0 = time.perf_counter()
        await asyncio.sleep(period)
        out.append((time.perf_counter() - t0 - period) * 1000)

async def vad_frames(stop, late):
    # frame 32 ms đến theo đồng hồ tuyệt đối; ghi frame nào được xử lý muộn > 50 ms
    t0, k = time.perf_counter(), 0
    while not stop.is_set():
        k += 1
        due = t0 + k * 0.032
        await asyncio.sleep(max(0, due - time.perf_counter()))
        if (time.perf_counter() - due) * 1000 > 50:
            late.append(k)

async def run(name, work):
    stop, lag, late = asyncio.Event(), [], []
    mon = asyncio.create_task(lag_monitor(stop, lag))
    vad = asyncio.create_task(vad_frames(stop, late))
    await asyncio.sleep(0.1)
    t = time.perf_counter()
    await work()
    wall = time.perf_counter() - t
    await asyncio.sleep(0.1); stop.set(); await mon; await vad
    lag.sort()
    p99 = lag[int(len(lag) * 0.99) - 1]
    print(f"{name:<44} wall {wall*1000:6.0f} ms | loop lag p50 {statistics.median(lag):6.1f}"
          f"  p99 {p99:6.1f}  max {lag[-1]:6.1f} ms | VAD frame muộn {len(late):3d}")

model = FakeWhisper()

async def a_iterate_on_loop():
    segs, _ = model.transcribe(b"")
    return [s for s in segs]                   # SAI: decode chạy trên loop

async def b_to_thread_then_iterate():
    segs, _ = await asyncio.to_thread(model.transcribe, b"")   # trả generator ngay
    return [s for s in segs]                   # SAI tinh vi: decode vẫn chạy trên loop

async def c_to_thread_materialize():
    def job():
        segs, info = model.transcribe(b"")
        return list(segs), info                # ĐÚNG: list() trong worker thread
    return await asyncio.to_thread(job)

async def d_pycpu_on_loop():
    return py_cpu()

async def e_pycpu_to_thread():
    return await asyncio.to_thread(py_cpu)     # thread nhưng tranh GIL

POOL = cf.ProcessPoolExecutor(1)
async def f_pycpu_process_pool():
    return await asyncio.get_running_loop().run_in_executor(POOL, py_cpu)

async def main():
    await asyncio.get_running_loop().run_in_executor(POOL, int)   # warm process
    for name, w in [("A. lặp generator trên loop", a_iterate_on_loop),
                    ("B. to_thread(transcribe) rồi lặp trên loop", b_to_thread_then_iterate),
                    ("C. to_thread(list(segments))", c_to_thread_materialize),
                    ("D. CPU thuần Python trên loop", d_pycpu_on_loop),
                    ("E. CPU thuần Python trong to_thread", e_pycpu_to_thread),
                    ("F. CPU thuần Python trong ProcessPool", f_pycpu_process_pool)]:
        await run(name, w)
    POOL.shutdown()

asyncio.run(main())
```

Output:

```text
A. lặp generator trên loop                   wall    901 ms | loop lag p50    0.4  p99    1.7  max  898.9 ms | VAD frame muộn  26
B. to_thread(transcribe) rồi lặp trên loop   wall    906 ms | loop lag p50    0.3  p99    0.7  max  902.9 ms | VAD frame muộn  26
C. to_thread(list(segments))                 wall    902 ms | loop lag p50    0.4  p99    1.6  max    1.9 ms | VAD frame muộn   0
D. CPU thuần Python trên loop                wall    773 ms | loop lag p50    0.3  p99    0.8  max  770.1 ms | VAD frame muộn  22
E. CPU thuần Python trong to_thread          wall    786 ms | loop lag p50    5.2  p99   10.7  max   10.7 ms | VAD frame muộn   0
F. CPU thuần Python trong ProcessPool        wall    804 ms | loop lag p50    0.2  p99    1.3  max    1.4 ms | VAD frame muộn   0
```

Đọc kết quả: A và B giống hệt nhau (loop đứng ~0,9 s, 26 frame VAD muộn) dù B "có `to_thread`"; C sạch. D đứng loop; E không đứng nhưng lag trung vị bằng switch interval 5 ms của GIL; F sạch. p50 của A, B, D thấp vì phần lớn mẫu lag được lấy lúc loop rảnh, trước và sau việc nặng; con số quyết định là `max` và số frame muộn.

### Script 2: huỷ I/O, huỷ thread, nuốt CancelledError, aclosing (`/tmp/ch18/cancel_demo.py`, đã chạy)

Bốn thí nghiệm: (1) huỷ task chờ I/O; (2a) huỷ task `await to_thread(infer)` không có cờ stop; (2b) có cờ `threading.Event`; (3) worker bắt `BaseException` nuốt `CancelledError`; (4) `break` khỏi `async for` có và không có `contextlib.aclosing`. Dùng ở §18.4.2, §18.4.3, §18.6.1.

```python
# Chương 18 — Script 2: huỷ task chờ I/O vs huỷ inference đang chạy trong thread.
# "Inference" giả lập: 10 bước × 100 ms (time.sleep, nhả GIL như kernel native).
import asyncio, threading, time, contextlib

T0 = time.perf_counter()
def ms(): return f"{(time.perf_counter() - T0) * 1000:7.0f} ms"

# ---- 1. Huỷ task đang chờ I/O: dừng ở điểm await kế tiếp ----
async def fake_stream():
    try:
        while True:
            await asyncio.sleep(0.1)           # chờ "byte tiếp theo từ socket"
    finally:
        print(f"{ms()}  [I/O]    finally chạy: đóng connection")

# ---- 2. Huỷ task đang await to_thread(...): future bị huỷ, THREAD CHẠY TIẾP ----
busy = threading.Event()
def gpu_infer(n=10, stop: threading.Event | None = None):
    busy.set()
    for i in range(n):
        if stop is not None and stop.is_set():
            print(f"{ms()}  [thread] thấy cờ stop ở bước {i}, thoát sớm")
            busy.clear(); return None
        time.sleep(0.1)                        # một "bước" inference, không ngắt được giữa chừng
    print(f"{ms()}  [thread] inference chạy XONG {n} bước (kết quả không ai nhận)")
    busy.clear(); return "text"

async def main():
    global T0
    # 1
    T0 = time.perf_counter()
    t = asyncio.create_task(fake_stream()); await asyncio.sleep(0.25)
    print(f"{ms()}  cancel() task I/O"); t.cancel()
    with contextlib.suppress(asyncio.CancelledError): await t
    print(f"{ms()}  task I/O đã kết thúc\n")

    # 2a: không cooperative
    T0 = time.perf_counter()
    t = asyncio.create_task(asyncio.to_thread(gpu_infer))
    await asyncio.sleep(0.25)
    print(f"{ms()}  cancel() task to_thread"); t.cancel()
    with contextlib.suppress(asyncio.CancelledError): await t
    print(f"{ms()}  await trả về ngay (task cancelled={t.cancelled()}), thread còn bận={busy.is_set()}")
    while busy.is_set(): await asyncio.sleep(0.01)
    print(f"{ms()}  thread mới thật sự rảnh (time-to-release)\n")

    # 2b: cooperative — cờ threading.Event kiểm giữa các bước
    T0 = time.perf_counter()
    stop = threading.Event()
    t = asyncio.create_task(asyncio.to_thread(gpu_infer, 10, stop))
    await asyncio.sleep(0.25)
    print(f"{ms()}  cancel() + stop.set()"); stop.set(); t.cancel()
    with contextlib.suppress(asyncio.CancelledError): await t
    while busy.is_set(): await asyncio.sleep(0.01)
    print(f"{ms()}  thread rảnh\n")

    # 3: nuốt CancelledError làm task không huỷ được
    T0 = time.perf_counter()
    async def bad_worker():
        n = 0
        while n < 5:
            try:
                await asyncio.sleep(0.1); n += 1
            except BaseException:               # SAI: bắt cả CancelledError
                print(f"{ms()}  [bad] nuốt CancelledError, chạy tiếp")
        return "bad worker chạy tới cùng"
    t = asyncio.create_task(bad_worker()); await asyncio.sleep(0.15); t.cancel()
    r = await t
    print(f"{ms()}  kết quả: {r!r}; cancelled={t.cancelled()}\n")

    # 4: async generator — break khỏi async for KHÔNG đóng generator ngay
    async def llm_stream(tag):
        try:
            for i in range(100):
                await asyncio.sleep(0.01); yield i
        finally:
            print(f"{ms()}  [{tag}] generator đóng → đóng HTTP stream")
    T0 = time.perf_counter()
    gen = llm_stream("không aclosing")
    async for x in gen:
        if x == 2: break
    print(f"{ms()}  sau break (không aclosing) — generator CHƯA đóng")
    await asyncio.sleep(0.05)
    print(f"{ms()}  … vẫn chưa, cho tới khi ai đó gọi aclose() hoặc GC/loop dọn")
    await gen.aclose()
    async with contextlib.aclosing(llm_stream("aclosing")) as g:
        async for x in g:
            if x == 2: break
    print(f"{ms()}  sau khối aclosing — generator đã đóng trước dòng này")

asyncio.run(main())
```

Output:

```text
    251 ms  cancel() task I/O
    251 ms  [I/O]    finally chạy: đóng connection
    251 ms  task I/O đã kết thúc

    251 ms  cancel() task to_thread
    251 ms  await trả về ngay (task cancelled=True), thread còn bận=True
   1005 ms  [thread] inference chạy XONG 10 bước (kết quả không ai nhận)
   1016 ms  thread mới thật sự rảnh (time-to-release)

    251 ms  cancel() + stop.set()
    301 ms  [thread] thấy cờ stop ở bước 3, thoát sớm
    304 ms  thread rảnh

    151 ms  [bad] nuốt CancelledError, chạy tiếp
    553 ms  kết quả: 'bad worker chạy tới cùng'; cancelled=False

     31 ms  sau break (không aclosing) — generator CHƯA đóng
     82 ms  … vẫn chưa, cho tới khi ai đó gọi aclose() hoặc GC/loop dọn
     82 ms  [không aclosing] generator đóng → đóng HTTP stream
    113 ms  [aclosing] generator đóng → đóng HTTP stream
    113 ms  sau khối aclosing — generator đã đóng trước dòng này
```

Đọc kết quả: (1) dừng ngay. (2a) `await` trả về ngay nhưng thread chạy thêm 765 ms. (2b) thread dừng sau 50 ms, ở ranh giới bước. (3) worker chạy tới cùng, `cancelled=False`. (4) generator chỉ đóng khi gọi `aclose()`; với `aclosing`, đóng trước dòng kế tiếp.

### Script 3: uplink với consumer chậm tạm thời (`/tmp/ch18/queue_sim.py`, đã chạy)

Mô phỏng rời rạc (không dùng thời gian thật, tất định). Dùng ở §18.5.1.

```python
# Chương 18 — Script 3: mô phỏng rời rạc uplink khi consumer chậm tạm thời.
# Frame 20 ms đến đều. Consumer (VAD+ASR feed) tốn 25 ms/frame trong 5 s đầu
# (ví dụ GPU bị LLM tranh), sau đó 15 ms/frame. Đo độ trễ "frame đến → xử lý xong".
from collections import deque

FRAME, T_SLOW, SLOW, FAST, T_END = 20, 5000, 25, 15, 12000

def simulate(policy, maxsize=None):
    q, lat, drops = deque(), [], 0
    upstream = deque()          # với 'block': frame bị giữ ở phía trước (socket/client)
    arrivals = [k * FRAME for k in range(T_END // FRAME)]
    i, t = 0, 0.0
    while i < len(arrivals) or q or upstream:
        # đưa các frame đã đến vào hàng đợi theo policy
        while i < len(arrivals) and arrivals[i] <= t:
            a = arrivals[i]; i += 1
            if policy == "block":
                upstream.append(a)          # producer bị chặn: frame nằm chờ ngoài queue (FIFO)
            elif policy == "unbounded" or len(q) < maxsize:
                q.append(a)
            elif policy == "drop_oldest":
                q.popleft(); drops += 1; q.append(a)
        while policy == "block" and upstream and len(q) < maxsize:
            q.append(upstream.popleft())
        if q:
            a = q.popleft()
            start = max(t, a)
            cost = SLOW if start < T_SLOW else FAST
            t = start + cost
            lat.append((t, t - a))
        else:
            t = arrivals[i] if i < len(arrivals) else t
    worst = max(l for _, l in lat)
    at5 = max(l for tt, l in lat if tt <= T_SLOW + 50)
    rec = next((tt for tt, l in lat if tt > T_SLOW and l < 60), None)
    return worst, at5, rec, drops

print(f"{'policy':<28}{'trễ max':>9}{'trễ ở t=5s':>12}{'hồi phục (<60ms) lúc':>22}{'frame bỏ':>10}")
for name, pol, m in [("unbounded", "unbounded", None),
                     ("bounded 5 + drop-oldest", "drop_oldest", 5),
                     ("bounded 5 + chặn producer", "block", 5)]:
    w, a5, rec, d = simulate(pol, m)
    rec_s = f"{rec/1000:.2f} s" if rec else "—"
    print(f"{name:<28}{w:>7.0f} ms{a5:>9.0f} ms{rec_s:>22}{d:>10}")
```

Output:

```text
policy                        trễ max  trễ ở t=5s  hồi phục (<60ms) lúc  frame bỏ
unbounded                      1020 ms     1020 ms                7.89 s         0
bounded 5 + drop-oldest         120 ms      120 ms                5.13 s        46
bounded 5 + chặn producer      1020 ms     1020 ms                7.89 s         0
```

Đọc kết quả: chặn producer cho đúng cùng độ trễ với queue không giới hạn, vì backlog chỉ chuyển ra phía trước; drop-oldest giữ trễ ≤ 120 ms và hồi phục ngay khi consumer nhanh lại, đổi lấy 46 frame bị bỏ.

### Script 4: pacing tương đối và tuyệt đối (`/tmp/ch18/pacing.py`, đã chạy)

Gửi 250 frame 20 ms trong khi một task ồn chiếm loop 3 ms mỗi 7 ms. Chạy thật ~10 s. Dùng ở §18.7.2.

```python
# Chương 18 — Script 4: pacing downlink 20 ms. sleep(0.02) tương đối vs lịch tuyệt đối.
# Trên loop có một task "ồn" chiếm 3 ms mỗi 7 ms (JSON, base64, log…) để mô phỏng tải.
import asyncio, time

FRAME, N = 0.020, 250                           # 250 frame = 5 s audio

async def noise(stop):
    while not stop.is_set():
        t = time.perf_counter()
        while time.perf_counter() - t < 0.003: pass   # 3 ms việc đồng bộ trên loop
        await asyncio.sleep(0.007)

async def naive():
    sent = []
    for _ in range(N):
        sent.append(time.perf_counter())
        await asyncio.sleep(FRAME)              # trôi: cộng dồn độ trễ thức dậy
    return sent

async def absolute():
    sent, t0 = [], time.perf_counter()
    for k in range(N):
        due = t0 + k * FRAME
        await asyncio.sleep(max(0.0, due - time.perf_counter()))
        sent.append(time.perf_counter())
    return sent

async def run(name, fn):
    stop = asyncio.Event(); nt = asyncio.create_task(noise(stop))
    sent = await fn(); stop.set(); await nt
    t0 = sent[0]
    drift = (sent[-1] - t0) - (N - 1) * FRAME
    err = [abs((s - t0) - k * FRAME) * 1000 for k, s in enumerate(sent)]
    gaps = [(b - a) * 1000 for a, b in zip(sent, sent[1:])]
    print(f"{name:<22} trôi sau 5 s: {drift*1000:6.1f} ms | lệch lịch max {max(err):6.1f} ms"
          f" | khoảng cách frame min/max {min(gaps):5.1f}/{max(gaps):5.1f} ms")

async def main():
    await run("sleep(0.02) tương đối", naive)
    await run("lịch tuyệt đối", absolute)

asyncio.run(main())
```

Output:

```text
sleep(0.02) tương đối  trôi sau 5 s:  148.9 ms | lệch lịch max  148.9 ms | khoảng cách frame min/max  20.2/ 21.0 ms
lịch tuyệt đối         trôi sau 5 s:   -2.8 ms | lệch lịch max    3.0 ms | khoảng cách frame min/max  17.3/ 21.1 ms
```

Đọc kết quả: lịch tương đối trôi ~3 % (149 ms sau 5 s), lịch tuyệt đối lệch tối đa 3 ms và không cộng dồn.

### Script 5: cadence và throughput của GPU worker TTS (`/tmp/ch18/batching_sim.py`, đã chạy)

Mô phỏng rời rạc 10 phút với tham số giả định `c(B) = 30 + 3·B` ms mỗi bước 80 ms audio. Tất định nhờ seed cố định. Dùng ở §18.7.3.

```python
# Chương 18 — Script 5: cadence vs throughput cho một GPU worker TTS (mô hình đồ chơi).
# Mỗi bước GPU sinh 1 frame 80 ms cho MỌI stream trong batch, tốn c(B) = 30 + 3·B ms
# (tham số GIẢ ĐỊNH, chỉ giữ hình dạng "chi phí cố định lớn + phần theo B nhỏ").
# Mỗi response dài 50 frame = 4 s audio. Client pre-buffer 2 frame (160 ms).
import random, statistics

FR, F, PRE = 80.0, 50, 2
def cost(b): return 30 + 3 * b

def arrivals(lam, T, seed):
    rnd, t, out = random.Random(seed), 0.0, []
    while True:
        t += rnd.expovariate(lam / 1000)
        if t > T: return out
        out.append(t)

def playback(times):
    clock, stalls, stall_ms = times[PRE - 1], 0, 0.0
    for p in times:
        if p > clock: stalls += 1; stall_ms += p - clock; clock = p
        clock += FR
    return stalls, stall_ms

def continuous(arr, S, qcap=None, qtimeout=None):
    t, i, active, wait, done, rejected = 0.0, 0, [], [], [], 0
    while i < len(arr) or active or wait:
        while i < len(arr) and arr[i] <= t:
            if qcap is not None and len(wait) >= qcap and len(active) >= S: rejected += 1
            else: wait.append({"a": arr[i], "ts": []})
            i += 1
        if qtimeout is not None:
            keep = [r for r in wait if t - r["a"] <= qtimeout]; rejected += len(wait) - len(keep); wait = keep
        while wait and len(active) < S: active.append(wait.pop(0))
        if not active:
            t = arr[i] if i < len(arr) else t; continue
        t += cost(len(active))
        for r in active: r["ts"].append(t)
        done += [r for r in active if len(r["ts"]) == F]
        active = [r for r in active if len(r["ts"]) < F]
    return done, rejected

def static(arr, Bmax, W):
    t, i, done = 0.0, 0, []
    while i < len(arr):
        t = max(t, arr[i]); deadline = arr[i] + W
        batch = []
        while i < len(arr) and len(batch) < Bmax and arr[i] <= max(t, deadline):
            batch.append({"a": arr[i], "ts": []}); i += 1
        t = max(t, deadline if len(batch) < Bmax else batch[-1]["a"])
        for _ in range(F):
            t += cost(len(batch))
            for r in batch: r["ts"].append(t)
        done += batch
    return done, 0

def report(name, res):
    done, rej = res
    ttfa = sorted(r["ts"][0] - r["a"] for r in done)
    st = [playback(r["ts"]) for r in done]
    bad = sum(1 for s, _ in st if s > 0)
    p95 = ttfa[int(0.95 * len(ttfa)) - 1]
    print(f"{name:<40} n={len(done):4d} từ chối={rej:3d} | TTFA p50 {statistics.median(ttfa):6.0f}"
          f" p95 {p95:6.0f} ms | stream bị giật {100*bad/len(done):5.1f}%"
          f" | giật TB {statistics.mean(m for _, m in st):6.0f} ms/stream")

T = 600_000                                     # 10 phút mô phỏng
arr = arrivals(1.5, T, 1)                       # ~1,5 response/s → ~6 stream đồng thời
print("Tải vừa (~1,5 response/s):")
report("A. continuous batching, S=16", continuous(arr, 16))
report("B. static batch 8, chờ tối đa 300 ms", static(arr, 8, 300))
report("C. static batch 4, chờ tối đa 100 ms", static(arr, 4, 100))
arr = arrivals(5.0, T, 2)                       # quá tải: ~20 stream muốn chạy cùng lúc
print("Quá tải (~5 response/s):")
report("D. continuous, S=32 (không admission)", continuous(arr, 32))
report("E. continuous, S=14, queue 14, timeout 1 s", continuous(arr, 14, qcap=14, qtimeout=1000))
report("F. continuous, S=14, queue 4, timeout 300 ms", continuous(arr, 14, qcap=4, qtimeout=300))
```

Output:

```text
Tải vừa (~1,5 response/s):
A. continuous batching, S=16             n= 882 từ chối=  0 | TTFA p50     60 p95     86 ms | stream bị giật   0.0% | giật TB      0 ms/stream
B. static batch 8, chờ tối đa 300 ms     n= 882 từ chối=  0 | TTFA p50   1013 p95   2010 ms | stream bị giật   0.0% | giật TB      0 ms/stream
C. static batch 4, chờ tối đa 100 ms     n= 882 từ chối=  0 | TTFA p50   1384 p95   3983 ms | stream bị giật   0.0% | giật TB      0 ms/stream
Quá tải (~5 response/s):
D. continuous, S=32 (không admission)    n=2988 từ chối=  0 | TTFA p50    899 p95   5033 ms | stream bị giật  98.1% | giật TB   1825 ms/stream
E. continuous, S=14, queue 14, timeout 1 s n=2308 từ chối=680 | TTFA p50    649 p95   1039 ms | stream bị giật   0.0% | giật TB      0 ms/stream
F. continuous, S=14, queue 4, timeout 300 ms n=2228 từ chối=760 | TTFA p50    115 p95    334 ms | stream bị giật   0.0% | giật TB      0 ms/stream
```

Đọc kết quả: xem bảng ở §18.7.3. D phục vụ nhiều nhất nhưng gần như mọi stream bị giật; E, F từ chối một phần để giữ RTF < 1 cho phần được nhận.

### Script 6: admission, 429 + Retry-After, deadline, circuit breaker (`/tmp/ch18/admission.py`, đã chạy)

Server TTS giả bắt chước hình dạng hành vi slot + hàng chờ + timeout → `429` (số nhỏ cho dễ đọc). Chạy thật ~5 s. Có thành phần ngẫu nhiên (jitter) với seed cố định; thứ tự kết quả của các session có thể khác chút giữa các lần chạy. Dùng ở §18.8.2 và §18.8.4.

```python
# Chương 18 — Script 6: admission control, 429 + Retry-After, deadline, circuit breaker.
# FakeTTS bắt chước HÌNH DẠNG hành vi VieNeu API (slot + hàng chờ + timeout → 429),
# với số nhỏ cho dễ đọc: 2 slot, 2 chỗ chờ, chờ tối đa 0,5 s, mỗi câu sinh 0,6 s.
import asyncio, random, time

class Http429(Exception):
    def __init__(self, retry_after): self.retry_after = retry_after
class Unavailable(Exception): pass

class FakeTTS:
    def __init__(self, slots=2, queue=2, qtimeout=0.5, gen_s=0.6):
        self.sem, self.queue, self.qtimeout, self.gen_s = asyncio.Semaphore(slots), queue, qtimeout, gen_s
        self.waiting, self.calls, self.down = 0, 0, False
    async def speech(self, text):
        self.calls += 1
        if self.down:
            await asyncio.sleep(0.3); raise Unavailable()          # connect timeout giả lập
        if self.sem.locked() and self.waiting >= self.queue: raise Http429(0.4)
        self.waiting += 1
        try:
            await asyncio.wait_for(self.sem.acquire(), self.qtimeout)
        except TimeoutError:
            raise Http429(0.4)
        finally:
            self.waiting -= 1
        try:
            await asyncio.sleep(0.08)                              # TTFA
            return "audio"
        finally:
            asyncio.get_running_loop().call_later(self.gen_s, self.sem.release)  # slot bận hết câu

class Breaker:
    def __init__(self, fails=3, cooldown=1.0):
        self.fails, self.cooldown, self.n, self.open_until = fails, cooldown, 0, 0.0
    def allow(self):
        return time.monotonic() >= self.open_until                # hết cooldown → half-open
    def ok(self): self.n = 0
    def fail(self):
        self.n += 1
        if self.n >= self.fails: self.open_until, self.n = time.monotonic() + self.cooldown, self.fails - 1

async def naive(tts, text):
    while True:                                                    # SAI: retry vô hạn, không deadline
        try: return await tts.speech(text)
        except Http429: await asyncio.sleep(0.05)

async def deadline_aware(tts, text, budget_s, breaker):
    deadline = time.monotonic() + budget_s
    while True:
        if not breaker.allow(): return "fallback(breaker mở)"
        try:
            async with asyncio.timeout_at(asyncio.get_running_loop().time() + (deadline - time.monotonic())):
                r = await tts.speech(text)
            breaker.ok(); return r
        except Http429 as e:
            wait = e.retry_after * random.uniform(0.8, 1.2)       # jitter, tránh dồn cục
            if time.monotonic() + wait >= deadline: return "fallback(hết deadline)"
            await asyncio.sleep(wait)
        except Unavailable:
            breaker.fail()
        except TimeoutError:
            return "fallback(timeout)"

async def burst(label, fn, n=8):
    tts = FakeTTS(); t0 = time.monotonic()
    async def one(i):
        r = await fn(tts, f"câu {i}")
        return f"{r}@{(time.monotonic()-t0)*1000:.0f}ms"
    res = await asyncio.gather(*(one(i) for i in range(n)))
    print(f"{label}: {tts.calls} request tới server")
    for i, r in enumerate(res): print(f"   session {i}: {r}")

async def main():
    random.seed(7)
    await burst("1. retry vô hạn", naive)
    br = Breaker()
    await burst("2. deadline 1,2 s + Retry-After + jitter", lambda t, x: deadline_aware(t, x, 1.2, br))
    # 3. TTS sập: breaker biến 300 ms chờ mỗi lần thành fail-fast
    tts = FakeTTS(); tts.down = True; br = Breaker(fails=3, cooldown=1.0); t0 = time.monotonic()
    for i in range(6):
        if i == 4:
            await asyncio.sleep(1.1); tts.down = False                  # hết cooldown, TTS đã sống lại
            print("   (… 1,1 s sau, TTS phục hồi; breaker cho một request thử: half-open)")
        ts = time.monotonic()
        r = await deadline_aware(tts, "x", 2.0, br)
        print(f"3. TTS sập, lượt {i}: {r:<22} mất {(time.monotonic()-ts)*1000:5.0f} ms, server nhận tổng {tts.calls}")

asyncio.run(main())
```

Output:

```text
1. retry vô hạn: 94 request tới server
   session 0: audio@81ms
   session 1: audio@81ms
   session 2: audio@2125ms
   session 3: audio@2125ms
   session 4: audio@762ms
   session 5: audio@762ms
   session 6: audio@1445ms
   session 7: audio@1445ms
2. deadline 1,2 s + Retry-After + jitter: 19 request tới server
   session 0: audio@81ms
   session 1: audio@81ms
   session 2: fallback(hết deadline)@1162ms
   session 3: fallback(hết deadline)@892ms
   session 4: audio@783ms
   session 5: audio@804ms
   session 6: fallback(timeout)@1201ms
   session 7: fallback(timeout)@1201ms
3. TTS sập, lượt 0: fallback(breaker mở)   mất   902 ms, server nhận tổng 3
3. TTS sập, lượt 1: fallback(breaker mở)   mất     0 ms, server nhận tổng 3
3. TTS sập, lượt 2: fallback(breaker mở)   mất     0 ms, server nhận tổng 3
3. TTS sập, lượt 3: fallback(breaker mở)   mất     0 ms, server nhận tổng 3
   (… 1,1 s sau, TTS phục hồi; breaker cho một request thử: half-open)
3. TTS sập, lượt 4: audio                  mất    81 ms, server nhận tổng 4
3. TTS sập, lượt 5: audio                  mất    80 ms, server nhận tổng 5
```

Đọc kết quả: retry vô hạn tạo 94 request và người cuối chờ 2,1 s; chiến lược deadline dùng 19 request, mọi session có audio hoặc fallback trong ≤ 1,2 s. Breaker biến 300 ms chờ mỗi lần gọi service sập thành fail-fast 0 ms và tự đóng lại khi service phục hồi.

### Script 7: khung runtime asyncio cho một session (`/tmp/ch18/session_runtime.py`, đã chạy)

Ghép toàn bộ chương: owner một inbox, uplink drop-oldest, response = `TaskGroup` huỷ được, LLM giả là async generator trong `aclosing`, TTS giả trong executor một thread với cờ stop và cầu thread→loop có backpressure, send loop một writer với control ưu tiên, credit theo played offset, client giả có jitter và guard, teardown bằng `TaskGroup` + `except*`. Tuỳ chọn `--no-guard` tắt kiểm generation ở pacer, send loop và client. Chạy thật ~4,4 s. Dùng ở §18.9.

```python
# Chương 18 — Script 7: khung runtime asyncio cho MỘT session (chạy thật theo thời gian thực ~5 s).
# Ghép: inbox một owner (Chương 17) · uplink bounded drop-oldest · response = TaskGroup huỷ được ·
# LLM giả = async generator (đóng bằng aclosing) · TTS giả chạy trong executor 1 thread ("GPU")
# có cờ stop hợp tác và cầu thread→loop có backpressure · send loop một writer, control vượt hàng ·
# credit theo played offset · client giả có jitter mạng, guard floor, playback thời gian thực ·
# teardown bằng TaskGroup + except*. Không gọi model hay mạng thật; mọi độ trễ là GIẢ ĐỊNH.
import asyncio, contextlib, itertools, random, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

SR, CH_MS = 16000, 80
CH_SAMPLES = SR * CH_MS // 1000                 # 1280 mẫu / chunk
GUARD = "--no-guard" not in sys.argv              # tắt để thấy chuyện gì xảy ra khi thiếu guard
LEAD_MS = 480                                   # credit: tối đa 480 ms audio chưa phát đang "bay"
T0 = time.perf_counter()
def now(): return (time.perf_counter() - T0) * 1000
def log(*a): print(f"{now():6.0f} ms  ", *a)

GPU = ThreadPoolExecutor(max_workers=1, thread_name_prefix="tts-gpu")   # một thread sở hữu GPU
gpu_busy = threading.Event()

class SessionEnd(Exception): pass

# ---------------- backend giả ----------------
async def fake_llm(prompt):
    await asyncio.sleep(0.20)                                        # TTFT
    for w in ("Dạ, lịch hẹn của anh là chín giờ sáng thứ sáu. Anh có muốn đổi "
              "sang ngày khác không ạ? Em có thể kiểm tra giúp anh." if "lịch" in prompt
              else "Dạ được, em đổi sang thứ bảy cho anh nhé. Anh chờ em một chút.").split():
        await asyncio.sleep(0.025); yield w + " "

def tts_blocking(gid, cid, text, stop, push, on_exit):              # chạy trong thread GPU
    gpu_busy.set(); r = "error"
    try:
        n = max(2, len(text) * 60 // CH_MS)                          # ~60 ms audio / ký tự
        for i in range(n):
            if stop.is_set(): r = "stopped"; return r
            time.sleep(0.030)                                        # 1 bước = 80 ms audio (RTF ~0,4)
            if not push((gid, cid, i, CH_SAMPLES), stop): r = "stopped"; return r
        r = "done"; return r
    finally:
        gpu_busy.clear(); on_exit(gid, r)                            # báo về loop (thread-safe)

# ---------------- mạng + client giả ----------------
class Client:
    def __init__(self, inbox_put):
        self.cur = self.floor = 0; self.q = asyncio.Queue(); self.inbox_put = inbox_put
        self.played = {}; self.stale_after_clear = 0; self.clear_at = {}; self.stopped_at = {}
        self.cur_sleep = None
    def deliver(self, msg):                                          # gọi khi message tới client
        kind = msg[0]
        if kind == "clear":
            g = msg[1]; self.floor = max(self.floor, g); self.clear_at[g] = now()
            if self.cur <= self.floor:
                while not self.q.empty(): self.q.get_nowait()        # flush (thật: + fade vài ms)
                if self.cur_sleep: self.cur_sleep.cancel()           # dừng chunk đang phát
        elif kind == "audio":
            g = msg[1]
            if GUARD and g <= self.floor: return                     # guard: bỏ chunk generation đã clear
            if g > self.cur: self.cur = g
            if g == self.cur: self.q.put_nowait(msg)
    async def playback(self):
        try:
            await self._playback()
        finally:
            if self.cur_sleep: self.cur_sleep.cancel()               # không để rơi task con khi bị huỷ

    async def _playback(self):
        while True:
            m = await self.q.get(); g = m[1]
            if GUARD and g <= self.floor: continue
            if g in self.clear_at: self.stale_after_clear += 1       # đang phát chunk của gen đã clear!
            t = time.perf_counter()
            self.cur_sleep = asyncio.ensure_future(asyncio.sleep(CH_MS / 1000))   # loa "kéo" 80 ms
            await asyncio.wait({self.cur_sleep})                     # không nuốt CancelledError của chính task
            frac = min(1.0, (time.perf_counter() - t) / (CH_MS / 1000))
            self.played[g] = self.played.get(g, 0) + int(m[4] * frac)
            self.stopped_at[g] = now()
            self.inbox_put(("client.played", g, self.played[g]))     # (thật: gửi định kỳ, không mỗi chunk)

class Net:                                                           # WebSocket = TCP: giữ thứ tự
    def __init__(self, client): self.client, self.last = client, 0.0
    async def send(self, msg):
        t = max(self.last, time.perf_counter() + random.uniform(0.020, 0.040)); self.last = t
        asyncio.get_running_loop().call_at(asyncio.get_running_loop().time() + (t - time.perf_counter()),
                                           self.client.deliver, msg)
        await asyncio.sleep(0)                                       # điểm await như ws.send()

# ---------------- session ----------------
class Session:
    def __init__(self):
        self.loop = asyncio.get_running_loop()
        self.inbox = asyncio.Queue()                                 # control: không bao giờ bỏ
        self.uplink = asyncio.Queue(maxsize=8)                       # 8 × 20 ms; đầy → bỏ frame cũ nhất
        self.audio_q = asyncio.Queue(maxsize=4)                      # TTS → pacer (backpressure)
        self.out = asyncio.PriorityQueue()                           # (prio, seq, msg); control prio 0
        self.seq = itertools.count()
        self.gid = 0; self.resp_task = None; self.resp_stop = None
        self.sent = self.played = 0; self.credit = asyncio.Event()
        self.client = Client(self.inbox.put_nowait); self.net = Net(self.client)
        self.dropped_uplink = self.dropped_stale = 0; self.lag = []; self.t_barge = None; self.t_release = None

    # --- cầu thread → loop: KHÔNG gọi asyncio.Queue từ thread; dùng run_coroutine_threadsafe ---
    def push_from_thread(self, item, stop):
        fut = asyncio.run_coroutine_threadsafe(self.audio_q.put(item), self.loop)
        while True:
            try: fut.result(timeout=0.05); return True               # chờ chỗ trống = backpressure
            except TimeoutError:
                if stop.is_set(): fut.cancel(); return False

    def put_uplink(self, frame):                                     # policy uplink: drop-oldest
        if self.uplink.full():
            self.uplink.get_nowait(); self.dropped_uplink += 1
        self.uplink.put_nowait(frame)

    async def send_ctrl(self, msg): await self.out.put((0, next(self.seq), msg))

    # --- các task dài hạn ---
    async def owner(self):                                           # MỘT nơi quyết định
        while True:
            ev = await self.inbox.get()
            k = ev[0]
            if k == "vad.start":
                if self.bot_audible():
                    self.t_barge = now(); log(f"BARGE-IN (đã qua gate) khi gen {self.gid} đang phát")
                    await self.cancel_response("turn_detected")
            elif k == "vad.end":
                self.gid += 1; self.sent = self.played = 0
                log(f"turn.commit → response gen {self.gid}: «{ev[1]}»")
                self.resp_task = asyncio.create_task(self.run_response(self.gid, ev[1]))
            elif k == "client.played":
                if ev[1] == self.gid: self.played = max(self.played, ev[2]); self.credit.set()
            elif k == "session.end":
                log("session.end → teardown"); await self.cancel_response("session_end", clear=False)
                raise SessionEnd()

    def bot_audible(self):
        return (self.resp_task is not None and not self.resp_task.done()) or self.sent > self.played

    async def cancel_response(self, reason, clear=True):
        old = self.gid
        self.gid += 1                                                # 1. stale hoá trước tiên
        if clear: await self.send_ctrl(("clear", old))               # 2. clear vượt hàng (prio 0)
        if self.resp_stop: self.resp_stop.set()                      # 3. cờ cho thread GPU
        if self.resp_task and not self.resp_task.done():
            self.resp_task.cancel()                                  # 4. huỷ cây task của response
            await asyncio.wait({self.resp_task})                     #    chờ finally chạy xong; KHÔNG nuốt
                                                                     #    CancelledError của chính owner
        while not self.audio_q.empty(): self.audio_q.get_nowait()    # 5. flush, mở chỗ cho thread
        self.sent = self.played = 0; self.credit.set()
        log(f"cancel gen {old} ({reason}); generation hiện hành = {self.gid}")

    async def run_response(self, gid, user_text):
        stop = threading.Event(); self.resp_stop = stop
        clauses = asyncio.Queue(maxsize=2)
        try:
            async with asyncio.TaskGroup() as tg:                    # con lỗi → anh em bị huỷ
                tg.create_task(self.llm_chunker(gid, user_text, clauses))
                tg.create_task(self.tts_stage(gid, clauses, stop))
            log(f"response gen {gid} sinh xong")
        finally:
            stop.set()

    async def llm_chunker(self, gid, text, clauses):
        buf, cid = "", 0
        async with contextlib.aclosing(fake_llm(text)) as stream:    # huỷ → aclose → đóng HTTP
            async for tok in stream:
                buf += tok
                if buf.rstrip()[-1] in ".?!" or (cid == 0 and buf.rstrip()[-1] == "," and len(buf) >= 3):
                    await clauses.put((cid, buf.strip())); cid += 1; buf = ""
        if buf.strip(): await clauses.put((cid, buf.strip()))
        await clauses.put(None)

    async def tts_stage(self, gid, clauses, stop):
        while (c := await clauses.get()) is not None:
            cid, text = c
            await self.loop.run_in_executor(GPU, tts_blocking, gid, cid, text, stop,
                                            self.push_from_thread, self.on_gpu_exit_threadsafe)
            # ↑ huỷ task ở đây chỉ huỷ asyncio future bọc ngoài; thread vẫn chạy tới khi thấy `stop`

    def on_gpu_exit_threadsafe(self, gid, r):                        # gọi TỪ thread GPU
        self.loop.call_soon_threadsafe(self.on_gpu_exit, gid, r)

    def on_gpu_exit(self, gid, r):                                   # chạy trên loop
        if r == "stopped":
            self.t_release = self.t_release or now(); log(f"thread GPU nhả gen {gid} (thấy cờ stop)")

    async def pacer(self):                                           # audio_q → out, theo credit
        while True:
            item = await self.audio_q.get()
            while self.sent - self.played >= LEAD_MS * SR // 1000:
                self.credit.clear(); await self.credit.wait()
            if GUARD and item[0] != self.gid: self.dropped_stale += 1; continue   # stale: bỏ sớm
            self.sent += item[3]
            await self.out.put((1, next(self.seq), ("audio",) + item))

    async def send_loop(self):                                       # writer DUY NHẤT ra socket
        while True:
            _, _, msg = await self.out.get()
            if GUARD and msg[0] == "audio" and msg[1] != self.gid:    # kiểm stale NGAY trước khi gửi,
                self.dropped_stale += 1; continue                    # không có await xen giữa
            await self.net.send(msg)

    async def vad_consumer(self):                                    # đại diện nhánh VAD/ASR
        while True:
            await self.uplink.get(); await asyncio.sleep(0.002)      # ~2 ms / frame

    async def lag_monitor(self):
        while True:
            t = time.perf_counter(); await asyncio.sleep(0.01)
            self.lag.append((time.perf_counter() - t - 0.01) * 1000)

    async def replay(self):                                          # phát lại "file" theo thời gian thực
        script = {100: ("vad.start",), 1100: ("vad.end", "Cho em hỏi lịch hẹn thứ sáu"),
                  2700: ("vad.start",), 3300: ("vad.end", "Khoan, đổi sang thứ bảy"),
                  4300: ("session.end",)}
        t0 = time.perf_counter()
        for k in range(0, 4400 // 20):                               # frame 20 ms, lịch tuyệt đối
            due = t0 + k * 0.020 + random.uniform(0, 0.008)          # jitter mạng uplink 0–8 ms
            await asyncio.sleep(max(0, due - time.perf_counter()))
            self.put_uplink(b"\0" * 640)
            if k * 20 in script: self.inbox.put_nowait(script[k * 20])

    async def run(self):
        try:
            async with asyncio.TaskGroup() as tg:
                for coro in (self.owner(), self.pacer(), self.send_loop(), self.vad_consumer(),
                             self.lag_monitor(), self.replay(), self.client.playback()):
                    tg.create_task(coro)
        except* SessionEnd:
            pass                                                     # các task còn lại đã bị TaskGroup huỷ

async def main():
    random.seed(3)
    s = Session()
    await s.run()
    while gpu_busy.is_set(): await asyncio.sleep(0.005)
    c = s.client
    print("\n--- kiểm tra sau teardown ---")
    print(f"generation cuối = {s.gid}; client đã phát (ms) theo gen:",
          {g: n * 1000 // SR for g, n in c.played.items()})
    g1 = 1
    if g1 in c.clear_at:
        print(f"barge-in: owner quyết định {s.t_barge:.0f} ms → client nhận clear {c.clear_at[g1]:.0f} ms"
              f" → mẫu cuối gen 1 phát xong {c.stopped_at[g1]:.0f} ms; thread GPU nhả {s.t_release:.0f} ms")
    print(f"guard={'bật' if GUARD else 'TẮT'}: server bỏ {s.dropped_stale} chunk stale;"
          f" chunk generation cũ được phát sau clear: {c.stale_after_clear}")
    print(f"task còn sống ngoài main: {len([t for t in asyncio.all_tasks() if t is not asyncio.current_task()])};"
          f" thread GPU bận: {gpu_busy.is_set()}; uplink frame bị bỏ: {s.dropped_uplink}")
    lag = sorted(s.lag); print(f"loop lag p99 {lag[int(len(lag)*.99)-1]:.1f} ms, max {lag[-1]:.1f} ms")
    GPU.shutdown(wait=True)

asyncio.run(main())
```

Output:

```text
$ python3 session_runtime.py
  1102 ms   turn.commit → response gen 1: «Cho em hỏi lịch hẹn thứ sáu»
  2705 ms   BARGE-IN (đã qua gate) khi gen 1 đang phát
  2706 ms   cancel gen 1 (turn_detected); generation hiện hành = 2
  2728 ms   thread GPU nhả gen 1 (thấy cờ stop)
  3309 ms   turn.commit → response gen 3: «Khoan, đổi sang thứ bảy»
  4306 ms   session.end → teardown
  4306 ms   cancel gen 3 (session_end); generation hiện hành = 4
  4307 ms   thread GPU nhả gen 3 (thấy cờ stop)

--- kiểm tra sau teardown ---
generation cuối = 4; client đã phát (ms) theo gen: {1: 1237, 3: 640}
barge-in: owner quyết định 2705 ms → client nhận clear 2735 ms → mẫu cuối gen 1 phát xong 2735 ms; thread GPU nhả 2728 ms
guard=bật: server bỏ 4 chunk stale; chunk generation cũ được phát sau clear: 0
task còn sống ngoài main: 0; thread GPU bận: False; uplink frame bị bỏ: 0
loop lag p99 1.4 ms, max 2.3 ms

$ python3 session_runtime.py --no-guard | tail -6
--- kiểm tra sau teardown ---
generation cuối = 4; client đã phát (ms) theo gen: {1: 1398, 3: 640}
barge-in: owner quyết định 2705 ms → client nhận clear 2735 ms → mẫu cuối gen 1 phát xong 2901 ms; thread GPU nhả 2728 ms
guard=TẮT: server bỏ 0 chunk stale; chunk generation cũ được phát sau clear: 2
task còn sống ngoài main: 0; thread GPU bận: False; uplink frame bị bỏ: 0
loop lag p99 1.4 ms, max 1.9 ms
```

Đọc kết quả: xem §18.9. Phiên bản đầu của script để rò một task con của `playback` (báo "task còn sống ngoài main: 1"); bản dưới đây đã sửa bằng `try/finally`.

### Script 8: debug mode của asyncio (`/tmp/ch18/debug_mode.py`, đã chạy)

Một `time.sleep(0.3)` lọt vào coroutine, chạy với `debug=True` và `slow_callback_duration = 0.05`. Dùng ở §18.2.3.

```python
# Chương 18 — Script 8: asyncio debug mode bắt callback chạy lâu trên loop.
import asyncio, time, logging
logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
async def bad():
    time.sleep(0.3)                    # blocking call lọt vào coroutine
async def main():
    asyncio.get_running_loop().slow_callback_duration = 0.05   # mặc định 0,1 s
    await bad()
asyncio.run(main(), debug=True)
```

Output:

```text
WARNING asyncio: Executing <Task finished name='Task-1' coro=<main() done, defined at /tmp/ch18/debug_mode.py:6> result=None created at /usr/lib/python3.12/asyncio/runners.py:100> took 0.300 seconds
```

Đọc kết quả: asyncio chỉ ra đúng task đã chiếm loop và thời gian chiếm.

### Liên kết sang chương khác

- Chương 6 (capture, playback): callback audio thread, AudioWorklet, pre-buffer, underrun: đầu kia của cadence.
- Chương 8 (transport): TCP/HOL, `await ws.send()` và backpressure, credit theo played offset (§8.5), huỷ HTTP bằng đóng connection (§8.7.3).
- Chương 11 (ASR): turn-final và streaming khác nhau về cadence; partial progressive là latest-only.
- Chương 12 (LLM): SSE và sự kiện streaming (§12.2), huỷ LLM (§12.2.3), contention GPU khi chạy chung ASR/TTS (§12.8).
- Chương 13 (TTS): audio-output streaming, TTFA, RTF; vì sao TTS chia bước giúp huỷ.
- Chương 16 (dataflow): ba mặt phẳng dữ liệu, push/pull, ring buffer, gap, bộ nhớ theo session.
- Chương 17 (turn-taking): owner một inbox, generation, trình tự cancel, T_silence/T_release, teardown; chương này hiện thực chúng bằng asyncio.
- Chương 19 (cầu text → speech): chunker là consumer của LLM stream; mệnh đề là đơn vị không huỷ được của TTS.
- Chương 20 (latency): loop lag và hàng chờ executor là thành phần ẩn của critical path; đo P95/P99.
- Chương 21 (đánh giá): load test concurrency 1/4/8/16, gate cadence.
- Chương 22 (runtime, triển khai): worker service, executor theo model, `max_streams`, health/readiness, scale theo GPU.

[^design]: [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) — §5.4.4 (tham số decode faster-whisper `language="vi"`, `beam_size`, `condition_on_previous_text=False`, `temperature=0.0`, `vad_filter`; materialize generator `list(segs)` trong `asyncio.to_thread`, lặp lazy generator trên event loop block cả pipeline, Pipecat PR #5931, **Reported**); §5.7 và §9.5 (log content-free mặc định, `--log_transcripts` opt-in); §8.3 (chạy faster-whisper trong `asyncio.to_thread`; preemptive ASR+LLM; playback buffer; **Reported**); §9.1 (mỗi model một owner process, tách environment ASR/TTS/ONNX, danh sách container, readiness sau warmup; admission cap, bounded queue, backpressure/429, deadline theo session, circuit breaker và cleanup; **Synthesis**); §9.3 (`BatchedInferencePipeline` cho ASR turn-final, continuous batching cho LLM/TTS, **Reported**; ưu tiên cadence hơn throughput batch, **Synthesis**); §9.4 (không ghép hai giọng giữa câu; retry hoặc mệnh đề mới kèm thông báo); §10 mục 4 (tải: warm/cold, concurrency 1/4/8/16, stall, frame rớt, TTS underrun; chỉ tăng concurrency khi đạt P95 và cadence) và mục 5 (contract tests: cancel giữa chunk, disconnect/reconnect, timeout, OOM, 429; không stale audio, không duplicate final).
[^wikidesign]: [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md) — "Deploy tools: chọn đúng tầng", đoạn sau bảng (admission cap/`max_streams`, bounded queues/backpressure/429, per-session rate-limit/deadlines/circuit breaker và cleanup là requirements đề xuất; ưu tiên audio cadence hơn batch throughput); "Latency, monitoring và release gates" mục 4 (Load) và 5 (Contract tests). Trang `status: draft`.
[^whisper]: [Whisper Hallucination Mitigation for Vietnamese](../wiki/whisper-hallucination-mitigation.md) — "Post-transcription filters", gạch đầu dòng cuối (materialize segment generator ngay bằng `list(segs)` trong worker thread; lặp lazy generator của faster-whisper trên asyncio event loop block pipeline, Pipecat PR #5931). **Reported** từ AI report thứ cấp; PR không có trong `raw/`. Trang `status: draft`.
[^fw]: [Faster-Whisper](../wiki/faster-whisper.md) — generator semantics (`segments` là generator, transcription chỉ bắt đầu khi lặp, `segments = list(segments)` là nơi transcription thực sự chạy); batched transcription (`BatchedInferencePipeline`, `batch_size=16`, VAD filter bật mặc định khi batch); Relationships (cảnh báo materialize generator trong `asyncio.to_thread`, PR #5931). Nguồn: README faster-whisper đã capture.
[^frameworks]: [Voice Agent Frameworks](../wiki/voice-agent-frameworks.md) — "Pipecat composition for the recommended stack", gạch đầu dòng "Known pitfall" (Pipecat từng block event loop khi lặp generator `transcribe` lười của faster-whisper; segment phải được gom trong `asyncio.to_thread`, PR #5931). **Reported** qua AI report.
[^silero]: [Silero VAD](../wiki/silero-vad.md) — "Speed": một chunk audio 30+ ms tốn dưới 1 ms trên một thread CPU; batching hoặc GPU cải thiện thêm; ONNX có thể nhanh hơn 4–5 lần trong một số điều kiện (**Reported** theo README).
[^engine]: [Speech-to-Speech Realtime Engine](../wiki/speech-to-speech-realtime-engine.md) — "Protocol event surface" (lỗi `session_limit_reached`); "Interruption handling" (`CancelScope` gồm bộ đếm generation `cancel_scope.generation` và cờ `cancel_scope.discarding`; thread pipeline chụp generation lúc bắt đầu response và kiểm `is_stale(gen)` mỗi token); "WebRTC transport" (send loop của mỗi unit là consumer duy nhất của output queue). **Reported**, capture tại revision `f9c23282…`.
[^backends]: [Speech-to-Speech OpenAI-Compatible STT/TTS Backends](../wiki/speech-to-speech-openai-compatible-backends.md) — "OpenAI-compatible STT" (huỷ inference phía server là best-effort, đóng connection không bảo đảm server dừng GPU, vẫn phải lọc kết quả stale; sức chứa server, định tuyến, quota thuộc inference service hoặc proxy dùng chung, không thuộc queue bound phía client); "STT turn and session lifecycle" (kết quả giao bất đồng bộ để HTTP không chặn teardown; tối đa 8 final chờ + 1 đang chạy mỗi pipeline, quá thì `TranscriptionFailure` không upload; một progressive active, chỉ giữ cửa sổ tích luỹ mới nhất đang chờ, final huỷ progressive đang chạy, revision mới vô hiệu hoá việc cũ; cancellation còn hiệu lực qua kết nối/upload/đọc, dọn transport trước khi tái dùng worker; queue bound theo pipeline, không có admission queue hay ngân sách đồng thời dùng chung); "OpenAI-compatible TTS" (huỷ TTS chỉ best-effort: barge-in và teardown đóng HTTP response và ngừng publish audio cục bộ, nhưng `/v1/audio/speech` không có thao tác huỷ phía server). **Reported**.
[^cli]: [Speech-to-Speech CLI and Defaults](../wiki/speech-to-speech-cli-and-defaults.md) — `num_pipelines=1`: số pipeline cô lập trong pool; server định tuyến mỗi client tới pipeline rảnh kế tiếp; số session WebSocket đồng thời tối đa bằng `num_pipelines`, kết nối thêm bị từ chối (**Observed** trong argument class đã capture).
[^vieneuapi]: [VieNeu-TTS OpenAI-Compatible Speech API](../wiki/vieneu-tts-openai-speech-api.md) — response thành công `200` với `Transfer-Encoding: chunked`, header `X-Request-Id`, `X-Sample-Rate`; lỗi kiểu OpenAI, `429` khi hết slot kèm `Retry-After`; `/health` (`active`, `waiting`, `max_streams`; `503` khi bộ lập lịch GPU đã chết, không tự phục hồi, healthcheck Docker khởi động lại); biến môi trường `VIENEU_MAX_STREAMS` (GPU 16, CPU 1, int8 2), `VIENEU_QUEUE` (= `MAX_STREAMS`, quá thì `429` ngay), `VIENEU_QUEUE_TIMEOUT` (10 s, quá thì `429`). **Reported**.
[^vieneurt]: [VieNeu-TTS Streaming Runtime and Performance](../wiki/vieneu-tts-streaming-runtime.md) — "GPU: how streaming works" (một CUDA graph B slot, mỗi frame 80 ms một lần replay cho mọi slot; một worker thread sở hữu GPU, `infer_stream` từ N thread HTTP chỉ là N hàng đợi audio, server không fork; slot giải phóng khi gặp EOS hoặc frame cap); bảng HTTP (40 client với 16 slot + 16 chờ: 32 OK, 8 × `429`, request chờ thấy TTFA 1,5–3 s); "Choosing `max_streams`" (32 stream RTF 0,93 không giật nhưng audio đầu ~450 ms không còn biên; mỗi slot thừa cộng ~2,5 ms vào mọi lần gọi codec của mọi người; stream ≠ user, một user voice chat giữ stream 20–35 % thời gian, 16 stream ≈ 45–80 user); "Measuring it" (RTF max phải < 1, lý tưởng ≤ 0,7); planning formulas (giữ RTF ≤ 0,6–0,7 để có biên). Chỉ đo trên RTX 3060. **Reported**.
[^nemo]: [NeMo-Speech.cpp Server](../wiki/nemo-speech-server.md) — "Limits and lifecycle" (upload và audio tích luỹ trên realtime WS giới hạn 512 MiB; socket đọc/ghi timeout 30 s; inference chạy trên worker pool có giới hạn `--threads`; session VoiceChat nhận 300 s audio mặc định, `s2s.max_session_seconds`); `/health` và `/ready` trả `503` khi chưa có engine sẵn sàng. **Reported**, capture tại revision `8642eaa5…`.
[^blueprint]: [Cascaded Voice-Agent Blueprint](../wiki/cascaded-voice-agent-blueprint.md) — đoạn mô tả `VoiceSession` (bốn `asyncio.Queue`, `generation_id`, `assistant_speaking`, năm coroutine, `asr_worker` gọi Whisper qua `asyncio.to_thread`; **Reported**) và đoạn đọc tĩnh liền sau (không áp `MIN_SPEECH_MS`/`MAX_UTTERANCE_MS`, tăng `generation_id` ở frame đầu vượt ngưỡng, không xoá TTS queue, truyền bytes PCM thô vào `whisper.transcribe`; coi là dàn ý luồng điều khiển, không phải code chạy được; **Observed**). Nguồn là câu trả lời do LLM sinh.
[^stack]: [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md) — kiến trúc: gateway asyncio, reference server FastAPI + WebSocket asyncio (`Session` với `VADIterator` mỗi session, gate barge-in 400 ms, transcription qua `asyncio.to_thread`, LLM stream sang TTS queue worker, message `{"type":"clear"}`; body VieNeu và Docker tag cần kiểm lại); "Optimizations" (chạy generator `transcribe` lười tới hết trong `asyncio.to_thread`, PR #5931; nối các stage bằng async queue). **Reported** từ AI report thứ cấp.
[^ch8]: [Chương 8. Transport mạng cho audio realtime](chuong-08-transport-mang-cho-audio-realtime.md) — §8.4.5 (keepalive, đóng kết nối), §8.5.2 (ba điểm có thể đầy; `await ws.send()` và backpressure tự nhiên), §8.5.3 (credit theo played offset), §8.5.4 (chính sách khi đầy: uplink bỏ frame cũ, downlink chặn producer, control không bao giờ bỏ). Tài liệu cùng bộ, không phải nguồn wiki.
