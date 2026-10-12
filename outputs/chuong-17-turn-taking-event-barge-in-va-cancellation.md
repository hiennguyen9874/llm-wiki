# Chương 17. Turn-taking, event, barge-in và cancellation 🔴

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần V (Ghép pipeline).
> **Chương trước:** [Chương 16. Dataflow end-to-end và audio contract](chuong-16-dataflow-end-to-end-va-audio-contract.md). **Chương tiếp theo:** [Chương 18. Lập trình async và streaming cho pipeline audio](chuong-18-lap-trinh-async-va-streaming-cho-pipeline-audio.md).
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §3 nguyên tắc 2 (một owner cho mỗi quyết định turn) và 5 (không hành động trên văn bản chưa commit), §5.3 (turn detection, speculative reopen), §7.2 (event schema), §7.3 (barge-in và cancellation), §7.4 (vòng điều khiển). Gián tiếp phục vụ §8.1 (output gate quyết định latency) và §10 gate 5 (không stale audio, không duplicate final).
> **Cơ sở:** state machine, single-writer/actor, race condition kiểu check-then-act, watermark đơn điệu, idempotency key là **kiến thức nền chung** về hệ thống phân tán và lập trình đồng thời, không phải claim lấy từ nguồn wiki. Hành vi của các hệ cụ thể lấy từ wiki và gắn nhãn bằng chứng: [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md), [Speech-to-Speech Realtime Engine](../wiki/speech-to-speech-realtime-engine.md), [HF Speech-to-Speech Pipeline](../wiki/speech-to-speech-pipeline.md), [CLI and Defaults](../wiki/speech-to-speech-cli-and-defaults.md), [OpenAI-Compatible Backends](../wiki/speech-to-speech-openai-compatible-backends.md), [Browser Demo](../wiki/speech-to-speech-browser-demo.md), [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md), [VieNeu OpenAI Speech API](../wiki/vieneu-tts-openai-speech-api.md). Thông tin vendor là **Reported** (wiki chưa chạy lại). Ba script ở "Phụ lục chương" chạy bằng Python 3 thuần ngày 2026-10-07 (**Reproduced** cho logic điều khiển và phép tính của chính script, với độ trễ là tham số giả định, không phải đo model hay mạng). Thiết kế và suy luận của tác giả là **Synthesis**.

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Phân biệt **tín hiệu** (VAD, turn detector, ASR, TTS, client cung cấp) với **quyết định** (close, reopen, commit, cancel), và giải thích vì sao mọi quyết định về lượt chỉ có **một owner**.
2. Vẽ được hai state machine trực giao: **lượt của user** (`IDLE → LISTENING → SOFT_ENDED → COMMITTED`) và **response của bot** (`SPECULATIVE → RELEASED → DONE/CANCELLED`), với bảng chuyển trạng thái đầy đủ: sự kiện, điều kiện, hành động.
3. Định nghĩa chính xác "văn bản đã commit", và xếp được mọi hành động (caption, speculative compute, phát audio, ghi history, gọi tool) vào đúng bậc được phép.
4. Thiết kế event schema có envelope định danh, quy tắc thứ tự và ánh xạ sang OpenAI Realtime / HF s2s.
5. Dùng `generation_id` và `sequence` để **chứng minh** không còn chunk audio cũ nào được phát sau barge-in, kể cả khi cancel chỉ là best-effort và message tới trễ hoặc đảo thứ tự.
6. Thiết kế bộ gating barge-in (duration gate, threshold theo nhiễu, speaker lock, quick ASR, backchannel) và nói rõ đánh đổi giữa độ nhạy và ngắt nhầm.
7. Viết trình tự cancellation xuyên tầng (LLM, TTS, queue, client), đo được hai đại lượng **time-to-silence** và **time-to-release**, cắt history theo played offset, và đóng session sạch.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. Ai được phép close, reopen, commit một lượt? Vì sao chỉ một owner?
- Q2. Trình tự barge-in gồm những bước nào? Làm sao đảm bảo không còn chunk audio cũ nào được phát?
- Q3. Thế nào là "chỉ hành động trên văn bản đã commit"?
- Q4. Khi barge-in, nên tăng `generation_id` trước hay gửi `client.clear` trước? Thứ tự nào thật sự quan trọng?
- Q5. Duration gate 150 ms và 400 ms khác nhau thế nào về trải nghiệm? Có cách nào lấy được ưu điểm của cả hai không?
- Q6. Time-to-silence và time-to-release khác nhau ra sao? Vì sao phải đo cả hai?
- Q7. Bot bị ngắt sau 3,3 s phát. History nên lưu gì? Nếu client không có guard, history đó sai thế nào?
- Q8. User ngắt máy giữa lúc bot đang nói. Gateway phải làm gì, theo thứ tự nào?

---

## 17.1 Bức tranh: hội thoại là một chuỗi quyết định có thể rút lại

Một cuộc hội thoại nói khác một cuộc chat ở chỗ **không có nút Gửi**. Người nói không báo "tôi nói xong rồi". Hệ thống phải đoán, và đoán sai là chuyện thường: Smart Turn v3.2 trên tiếng Việt có FPR khoảng 9 %, tức cỡ 1/10 quyết định "hết lượt" đến khi user vẫn đang nói (**Reported** số liệu vendor, đọc thô là **Synthesis**).[^design] Vì vậy bộ điều khiển lượt nói phải được thiết kế quanh ý tưởng: **mọi quyết định đều có thể rút lại cho tới khi nó được commit, và mọi thứ sinh ra từ một quyết định đã rút lại phải bị huỷ và lọc bỏ**.

Ví dụ dưới đây là trace của script mô phỏng ở Phụ lục (kịch bản A, **Reproduced** cho logic, độ trễ là tham số giả định):

```text
 t(ms)  sự kiện
    32  vad.speech_start → turn=1 rev=1 LISTENING        "Cho em hỏi lịch hẹn…"
  1564  vad.speech_end → SOFT_ENDED                       (user ngừng để nghĩ)
  1574  smart_turn=complete → response gen=1 chạy speculative, output bị giữ
  1932  user nói tiếp → turn.reopen rev=2, huỷ gen=1       (chưa phát gì)
  3064  vad.speech_end → SOFT_ENDED rev=2
  3074  smart_turn=complete → response gen=3 speculative
  3874  hết grace 800 ms → turn.commit(1, 2) → gen=3 được phép phát
  4214  client phát mẫu audio đầu tiên                     (1 214 ms sau khi user thôi nói)
  5448  "(ho)" 150 ms → bị duration gate chặn
  6448  "ừ" 250 ms → bị duration gate chặn
  7448  "Khoan, đổi sang thứ bảy" đủ 400 ms → BARGE-IN: gen 3→4, cancel, clear
  7488  client flush; đã phát 3 284 ms của gen=3
  7528  audio.played → history: "Dạ, em đã kiểm tra lịch hẹn của anh. Lịch hiện tại là … [bị ngắt]"
  9074  turn.commit(2, 1) → gen=5 trả lời yêu cầu mới
```

Trong 9 giây có bốn quyết định bị rút lại hoặc bị từ chối: một lần reopen, hai lần chặn ngắt nhầm, một lần huỷ response đang phát. Chương này là về cơ chế làm cho những lần rút lại đó **sạch**: không có câu trả lời ma, không có audio cũ, không có history sai.

Có ba vòng đời lồng nhau cần quản lý:

```text
session_id ───────────────────────────────────────────────────────────── (kết nối)
  turn_id (lượt user) ──────────────┐   turn_id ────────────────────────
    revision 1 ──┐ revision 2 ──────┤     revision 1 ───────────────────
                 │                  │
  generation_id (response bot):  gen 1 (huỷ)  gen 3 (phát, bị ngắt)   gen 5 ...
    chunk_id / sequence:                       c0 c1 c2 ...
```

[Chương 16 §16.8](chuong-16-dataflow-end-to-end-va-audio-contract.md) đã định nghĩa sáu định danh. Chương này dùng chúng để điều khiển.

---

## 17.2 Tín hiệu và quyết định: một owner duy nhất (Q1)

### 17.2.1 Ai cung cấp gì

| Thành phần | Cung cấp **tín hiệu** | **Không** được tự làm |
|---|---|---|
| VAD (Silero) | `speech_start`, `speech_end`, xác suất theo frame | Commit lượt, ngắt bot |
| Turn detector (Smart Turn) | `complete` / `incomplete`, xác suất | Commit lượt |
| ASR | `partial`, `final`, cờ chất lượng | Mở hay đóng lượt; gọi LLM |
| LLM | text delta, tool call, `done` | Tự ghi history; tự chạy tool có side effect |
| TTS | audio chunk, `done`, lỗi `429` | Tự quyết phát hay không |
| Client | `audio.played`, `audio.done`, nút dừng | Tự quyết lượt (trừ push-to-talk) |
| Timer | "hết hạn" kèm token | Bất cứ hành động nào ngoài báo hết hạn |
| **Turn owner** | — | Là nơi **duy nhất** quyết định: open, soft-end, reopen, commit, tạo response, cancel, cắt history |

Đây là nguyên tắc 2 của tài liệu thiết kế: gateway (hoặc turn tracker của framework) là nơi duy nhất quyết định close, reopen và commit một lượt; VAD, ASR và TTS chỉ cung cấp tín hiệu (**Synthesis**).[^design][^wikidesign] HF s2s làm đúng như vậy: turn tracker sở hữu thứ tự `LISTENING`, `SOFT_ENDED`, `ANSWERING`, `CLOSED`; VAD cung cấp ranh giới, Smart Turn cung cấp timing, còn tracker quyết định reopen (**Reported**).[^hf]

### 17.2.2 Vì sao chỉ một owner: bốn race condition điển hình

Khi hai thành phần cùng có quyền quyết định, chúng sẽ quyết định khác nhau vào những thời điểm gần nhau. Các lỗi sau không lặp lại được khi test thủ công, chỉ xuất hiện dưới tải hoặc với người nói thật (**Synthesis**):

| Race | Hai "owner" | Chuyện gì xảy ra |
|---|---|---|
| **Double commit** | VAD timeout commit lượt; callback `asr.final` cũng commit | LLM được gọi hai lần cho một lượt; hai câu trả lời chồng nhau |
| **Commit sau reopen** | Timer commit của revision 1 bắn ra sau khi user đã nói tiếp | Bot trả lời nửa câu đầu, bỏ qua nửa sau |
| **Hai bộ segmentation** | WhisperLive/RealtimeSTT tự cắt câu; gateway cũng cắt theo VAD | Ranh giới lượt lệch nhau; transcript bị cắt đôi hoặc dính hai lượt. Tài liệu thiết kế ghi rõ: không để hai owner cùng quyết định segmentation[^design] |
| **Cancel không có sentinel** | Client gửi `response.cancel` khi không có response; send loop bật cờ "discarding" | Cờ không bao giờ được xoá; response kế tiếp bị nuốt mất. HF s2s tránh bằng cách **không gọi** `cancel()` khi không có response active (**Reported**)[^engine] |

Chung một gốc: trạng thái lượt bị **ghi từ nhiều nơi**. Cách chữa không phải là thêm khoá (lock) cho từng biến, mà là chỉ cho phép **một nơi ghi**.

### 17.2.3 Hiện thực: single-writer với một inbox

Mẫu thiết kế (kiến thức nền, kiểu actor):

```text
VAD ───────┐
Smart Turn ┤
ASR ───────┤      ┌──────────────────────────────┐      lệnh có gắn định danh
LLM ───────┼────► │ inbox (FIFO) → TurnOwner      │ ───► LLM / TTS / client / history
TTS ───────┤      │ xử lý TUẦN TỰ từng sự kiện    │
client ────┤      │ là nơi duy nhất ghi: turn,    │
timer ─────┘      │ revision, generation_id       │
                  └──────────────────────────────┘
```

Quy tắc (**Synthesis**):

1. Mọi thành phần gửi **sự kiện** vào inbox của session. Không ai gọi thẳng `owner.state = ...`.
2. Owner xử lý từng sự kiện tới hết rồi mới lấy sự kiện kế tiếp. Trong một lần xử lý, không có `await` nào chen giữa "đọc trạng thái" và "ghi trạng thái".
3. Owner phát **lệnh** ra ngoài, mỗi lệnh mang `(turn_id, revision, generation_id)`. Worker thực thi lệnh nhưng không đổi trạng thái lượt.
4. Mọi sự kiện quay về (text, audio, final, timer) mang định danh của lệnh đã sinh ra nó. Owner so định danh với trạng thái hiện tại; lệch thì bỏ.
5. Mỗi session một owner. Owner của các session khác nhau chạy song song được; trong một session thì tuần tự.

Với `asyncio` (Chương 18), mẫu này là một task đọc `asyncio.Queue`. Lợi ích lớn nhất: mọi race ở bảng trên trở thành **câu hỏi thứ tự trong một hàng đợi**, và có thể test bằng cách phát lại một chuỗi sự kiện.

### 17.2.4 Owner nằm ở đâu trong các lựa chọn orchestration

| Lựa chọn | Owner | Ghi chú |
|---|---|---|
| HF s2s | Turn tracker trong mỗi `PipelineUnit`; send loop là consumer duy nhất của output queue | **Reported**[^hf][^engine] |
| Pipecat | Pipeline của framework, có interruption handling sẵn | **Reported** qua AI report, chưa kiểm plugin hiện hành[^frameworks] |
| Gateway tự viết | Lớp `Session` của bạn | Report có reference server với gate 400 ms và `{"type":"clear"}`; cancellation và metrics phải tự làm (**Reported**)[^design] |

Dù chọn gì, hãy trả lời được câu "dòng code nào quyết định commit?" bằng **một** vị trí duy nhất. Nếu câu trả lời là "tuỳ trường hợp", bạn đang có hai owner.

---

## 17.3 State machine của lượt nói

### 17.3.1 Hai máy trạng thái trực giao

Nhiều prototype dùng một biến `state` cho cả "user đang nói" lẫn "bot đang nói". Điều đó không biểu diễn được trường hợp quan trọng nhất: **cả hai cùng nói** (barge-in, backchannel). Tách thành hai máy (**Synthesis**):

- **Máy lượt user** (một instance cho lượt hiện tại): `IDLE → LISTENING → SOFT_ENDED → COMMITTED`.
- **Máy response** (một instance cho mỗi `generation_id`): `SPECULATIVE → RELEASED → DONE | CANCELLED | FAILED | INCOMPLETE`.

"Bot đang nói" là một **thuộc tính suy ra**: tồn tại response ở trạng thái `RELEASED` mà client chưa báo `audio.done`. Không lưu nó thành một biến độc lập dễ lệch.

Ánh xạ sang HF s2s: `LISTENING` ≈ `LISTENING`, `SOFT_ENDED` ≈ `SOFT_ENDED`, `COMMITTED` + response `RELEASED` ≈ `ANSWERING`, `IDLE` sau `audio.done` ≈ `CLOSED` (**Synthesis** về ánh xạ; tên trạng thái HF là **Reported**).[^hf]

### 17.3.2 Máy lượt user

```text
                    speech_start (đủ min_speech)
        ┌──────────┐ ───────────────────────────► ┌───────────┐
        │   IDLE   │                               │ LISTENING │◄──────────────────┐
        └──────────┘ ◄─── audio.done (bot xong)    └───────────┘                   │
             ▲                    │                     │ speech_end (min_silence) │
             │                    │                     ▼                          │
             │              ┌───────────┐         ┌────────────┐  speech_start     │
             │              │ COMMITTED │ ◄────── │ SOFT_ENDED │ ─────────────────►┘
             │              └───────────┘ commit  └────────────┘  (reopen: rev+1,
             │                    │   (grace hết,                  huỷ response
             │                    │    hoặc max_wait)              speculative)
             │                    │ speech_start + vượt gate barge-in
             │                    ▼
             │            turn mới (turn_id+1) ở LISTENING; response cũ → CANCELLED
             └──────────────────────────────────────────────────────────────────────
```

Ý nghĩa từng trạng thái:

- **IDLE:** không ai nói, hoặc bot đang nói mà user chưa nói gì.
- **LISTENING:** user đang nói. Turn buffer đang tích luỹ (pre-roll + audio, Chương 16 §16.5).
- **SOFT_ENDED:** VAD thấy im lặng đủ `min_silence`. Lượt **có thể** đã xong. Được phép chạy ASR/LLM speculative, **không** được phát hay tạo side effect.
- **COMMITTED:** lượt đã chốt ở một `(turn_id, revision)` cụ thể. Không reopen được nữa. Response của revision này được phép phát.

### 17.3.3 Máy response

| Trạng thái | Nghĩa | Được làm | Không được làm |
|---|---|---|---|
| `SPECULATIVE` | Tạo trên `(turn, rev)` đang `SOFT_ENDED` | Chạy ASR final, LLM, chunker; giữ text trong `held` | Phát audio, ghi history, tool có side effect |
| `RELEASED` | Revision của nó đã commit | Đưa chunk vào TTS, phát, chạy tool sau kiểm tra | — |
| `DONE` | Client báo phát hết | Ghi nguyên câu trả lời vào history | — |
| `CANCELLED` | Bị reopen, barge-in, client huỷ, session đóng | Ghi phần đã phát (nếu đã `RELEASED`) | Phát thêm bất cứ thứ gì |
| `FAILED` / `INCOMPLETE` | Provider lỗi / dừng vì giới hạn token, content filter | Ghi trạng thái; quyết định hỏi lại | — |

HF s2s có cùng bộ trạng thái kết thúc: hết token hoặc content filter cho `incomplete`, lỗi provider cho `failed`, huỷ cho `cancelled` với lý do `turn_detected` hoặc `client_cancelled`. Với `incomplete` và `failed`, pipeline **rollback history** dù một phần output có thể đã tới client (**Reported**).[^engine]

Có nên chạy TTS khi response còn `SPECULATIVE`? Được, nếu chấp nhận lãng phí compute khi reopen, nhưng audio phải bị giữ ở server và gắn generation. Tài liệu thiết kế giả định TTS chỉ chạy sau commit, nên TTS nằm ngoài phần được "giấu" trong grace (**Synthesis**).[^design] Chương này theo giả định đó.

### 17.3.4 Bảng chuyển trạng thái

Đây là phần lõi để implement. Mỗi dòng là một trường hợp phải có test (**Synthesis**, tham số theo HF s2s là **Observed**/**Reported**).[^cli][^hf]

| Trạng thái lượt | Sự kiện | Điều kiện | Hành động |
|---|---|---|---|
| IDLE | `speech_start` | speech ≥ `min_speech` (HF: 384 ms) | `turn_id+1`, `revision=1`, mở turn buffer từ `speech_start − pre-roll` → LISTENING |
| LISTENING | `speech_end` | im ≥ `min_silence` | → SOFT_ENDED; gọi turn detector trên audio cuối |
| SOFT_ENDED | `eou=complete` | `(turn, rev)` khớp | Tạo response `SPECULATIVE` (gen mới); hẹn timer commit sau `speculative_reopen_ms` (800) |
| SOFT_ENDED | `eou=incomplete` | khớp | Hẹn bắt đầu ASR/LLM sau `incomplete_delay` (600); hẹn commit ở `max_wait` (2 000) |
| SOFT_ENDED | `speech_start` | speech ≥ `min_speech_continuation` (HF: 192 ms) | **Reopen**: cancel response speculative (gen+1), `revision+1`, phát lại audio đã tích luỹ cho ASR → LISTENING |
| SOFT_ENDED | `timer(commit, turn, rev)` | token khớp `(turn, rev)` hiện tại | → COMMITTED; response → `RELEASED`; thả `held` vào TTS; phát `turn.commit` |
| bất kỳ | `timer(...)` | token **không** khớp | Bỏ qua (timer của revision cũ tự vô hiệu) |
| COMMITTED, bot nghe được | `speech_start` | chưa qua gate barge-in | Không làm gì; tiếp tục đo |
| COMMITTED, bot nghe được | speech kéo dài qua gate (+ speaker lock, quick ASR nếu bật) | `interrupt_response` bật | **Barge-in** (§17.8); `turn_id+1` → LISTENING, turn buffer từ **đầu đoạn nói** − pre-roll |
| COMMITTED | `audio.done(gen)` | gen là response hiện hành | Response → DONE; ghi history; → IDLE |
| bất kỳ | `text/audio(gen)` | `gen ≠ generation_id` hiện hành | Bỏ (stale) |
| bất kỳ | `session.close` | — | Teardown (§17.10) |

Ba chi tiết hay bị bỏ sót:

1. **Ngưỡng nói tiếp thấp hơn ngưỡng mở lượt.** HF s2s dùng `min_speech_ms=384` cho lượt mới **và cho barge-in**, nhưng chỉ `min_speech_continuation_ms=192` cho speech nối tiếp một lượt soft-ended chưa commit (**Observed** trong argument class).[^cli] Lý do (**Synthesis**): khi lượt chưa commit, ngắt nhầm chỉ tốn một lần reopen, không mất gì với user; còn khi bot đang nói, ngắt nhầm làm bot im.
2. **Barge-in phải lấy audio từ đầu đoạn nói, không phải từ lúc quyết định.** Quyết định barge-in đến sau 400 ms. Nếu turn buffer mở lúc quyết định, ASR mất "Khoan," và user phải nói lại. Ring buffer của Chương 16 phải đủ dài để lùi lại `gate + pre-roll` (**Synthesis**).
3. **Đồng hồ của timer.** HF s2s tính trần "unanswered reopen" theo **thời gian audio đã stream** (để push-to-talk không gửi audio thì trần không chạy), còn processing hold và output hold theo **wall clock** (**Reported**).[^hf] Khi viết timer, ghi rõ timer nào theo đồng hồ nào.

### 17.3.5 Speculative reopen và revision

Revision là "phiên bản của cùng một lượt". Một lượt có nhiều revision khi user ngừng giữa câu rồi nói tiếp. Quy tắc (HF s2s là **Reported**, phần còn lại là **Synthesis**):

- Reopen **không tạo lượt mới**. `turn_id` giữ nguyên, `revision+1`. Lý do: LLM phải thấy một câu hỏi liền mạch "Cho em hỏi lịch hẹn của em vào thứ sáu ấy", không phải hai message user liên tiếp.
- Khi reopen, ASR nhận lại **toàn bộ audio đã tích luỹ** của lượt (HF: "re-emits accumulated audio"), không chỉ phần mới. Transcript của revision mới thay thế transcript cũ.[^hf]
- Mọi công việc chưa commit của revision cũ bị bỏ. Công việc **đã** được chấp nhận (accepted output) có thể chạy nốt (HF: "starting a newer turn drops older uncommitted work but accepted output may finish").[^hf]
- Phía client, HF s2s **giữ lại** `speech_stopped` và final transcript trong lúc lượt còn reopen được; khi commit, client nhận đúng một stop, một buffer commitment, một user item và một final transcript (**Reported**).[^hf] Bài học: đừng để client thấy các trạng thái tạm có thể bị rút lại, trừ khi client hiểu revision.
- Có trần cho việc reopen: HF có `unanswered_reopen_ms=7000`, một giới hạn an toàn cho lượt soft-ended speculative chưa được trả lời (**Observed**).[^cli]

### 17.3.6 Biến thể commit cứng

Kiến trúc "commit cứng sau timeout" (Chương 10 §10.5.1) là cùng state machine với **grace = 0**: SOFT_ENDED chuyển ngay sang COMMITTED khi turn detector nói complete hoặc hết fallback 1.2–1.5 s. Không có reopen. User nói tiếp sau commit trở thành barge-in vào response. Đơn giản hơn, nhưng mọi lỗi "hết lượt sớm" biến thành "bot cắt ngang rồi phải tự ngắt" (**Synthesis**).[^design]

Đừng trộn tham số: `min_silence 64 ms` của HF chỉ an toàn vì có reopen phía sau. Đặt 64 ms vào kiến trúc commit cứng sẽ cắt ngang user liên tục (**Synthesis**).[^design]

---

## 17.4 "Chỉ hành động trên văn bản đã commit" (Q3)

### 17.4.1 Định nghĩa

**Văn bản đã commit** là transcript gắn với một cặp `(turn_id, revision)` thoả cả hai điều kiện:

1. Owner đã phát `turn.commit(turn_id, revision)`: lượt không thể reopen nữa.
2. Transcript là **final** của revision đó (hoặc final-pass đã thay thế nó, nếu dùng two-pass), đã qua validity gate.

Partial, stable prefix, transcript của revision cũ, transcript của lượt đang SOFT_ENDED đều **chưa commit**, dù chúng có thể giống hệt bản cuối cùng.

### 17.4.2 Thang hành động

Nguyên tắc 5 của tài liệu thiết kế: partial dùng cho caption và tính toán speculative; side effect (tool call, phát âm thanh đã cam kết) chỉ chạy sau `turn.commit` (**Synthesis**).[^design] Cụ thể hoá thành thang (**Synthesis**):

| Hành động | Partial | Speculative (SOFT_ENDED) | Committed | Lý do |
|---|---|---|---|---|
| Caption / hiển thị | ✅ | ✅ | ✅ | Sửa được trên màn hình |
| Prefetch rẻ, đọc-only, idempotent (tra giờ mở cửa) | ⚠️ | ✅ | ✅ | Kết quả bỏ được |
| Chạy LLM | ❌ | ✅ (giữ output) | ✅ | Huỷ được |
| TTS | ❌ | ⚠️ (giữ audio ở server) | ✅ | Huỷ được, nhưng tốn slot |
| **Phát audio cho user** | ❌ | ❌ | ✅ | Không thu hồi được âm thanh đã nghe |
| Ghi history | ❌ | ❌ | ✅ (chỉ phần đã phát) | History sai làm hỏng các lượt sau |
| Tool đọc-only nhưng tốn tiền/giới hạn tần suất | ❌ | ❌ | ✅ | Chi phí không hoàn lại |
| **Tool ghi** (đặt lịch, gửi tin, thanh toán) | ❌ | ❌ | ✅ + xác nhận bằng lời + idempotency key | Không huỷ được sau khi chạy |

Ô "phát audio" là ranh giới cứng. Âm thanh user đã nghe **không thể rút lại**; một câu trả lời cho câu hỏi user chưa nói xong là lỗi trải nghiệm tệ nhất của voice agent.

### 17.4.3 Output gate và giá của nó

Output gate là chỗ response `SPECULATIVE` chờ commit. Nó **quyết định latency** thay cho tốc độ model khi model đủ nhanh. Công thức của tài liệu thiết kế (**Synthesis**):[^design]

```text
v2v ≈ (cuối tiếng user → soft-end) + max(output-hold, ASR + LLM tới mệnh đề đầu)
      + TTS tới audio đầu + transport/playback
```

Kịch bản A ở Phụ lục cho đúng con số này (**Reproduced** với tham số giả định): `64 (min_silence) + 10 (smart turn) + max(800, 150 + 300) + 150 (TTFA) + 40 (downlink) + 150 (pre-buffer) = 1 214 ms`, khớp mẫu audio đầu tiên ở 4 214 ms khi user thôi nói ở 3 000 ms. ASR + LLM (450 ms) nằm gọn trong grace 800 ms: đổi sang LLM nhanh gấp đôi **không** giảm được mili giây nào. Muốn nhanh hơn thì phải giảm grace, và trả giá bằng nhiều lần nói đè hơn. Đây là quyết định sản phẩm, không phải tối ưu kỹ thuật.

### 17.4.4 Final-pass, idempotency và tool

- **Final-pass** (Profile D) chạy lại turn audio đã giữ; kết quả thay thế một revision và **commit một lần**. Không đổ full transcript vào luồng partial, sẽ bị trùng lặp (**Synthesis**).[^design]
- **Idempotency key** cho tool: `(session_id, turn_id, revision, tool_call_index)`. Retry cùng key không chạy lại tool (kiến thức nền; Chương 12 §12.6.3).
- **Kiểm generation ngay trước khi chạy tool:** tool call chỉ chạy nếu `generation_id` của nó vẫn là hiện hành. Một tool call tới sau barge-in thuộc response đã bị huỷ.
- HF s2s ghi "response thuộc generation input của nó" lên conversation item và tool call được chấp nhận. Tool follow-up giữ lượt gốc, trừ khi một message user mới gán lại; response không được "mượn" danh tính của speech **đang ghi** (**Reported**).[^hf] Phía client SDK: response bị huỷ hoặc incomplete thì huỷ các kết quả tool chưa gửi (**Reported**).[^engine]

---

## 17.5 Event schema

### 17.5.1 Envelope chung

Mọi sự kiện, cả nội bộ lẫn trên dây, có chung một envelope (**Synthesis**, mở rộng §7.2 của tài liệu thiết kế):[^design]

```json
{
  "type": "audio.chunk",
  "session_id": "s-7f3a",
  "turn_id": 17,
  "revision": 2,
  "generation_id": 42,
  "chunk_id": 1,
  "sequence": 3,
  "w": 214720,
  "t_wall_ms": 1760000014760
}
```

- Trường nào không áp dụng thì bỏ, đừng điền 0 (0 có thể là giá trị hợp lệ).
- `w` là chỉ số mẫu trên timeline uplink (Chương 16 §16.6), chỉ có ở sự kiện gắn với audio user.
- Audio downlink trên WebSocket đi bằng binary frame có header nhỏ chứa `generation_id`, `sequence`; JSON chỉ cho control (Chương 16).

### 17.5.2 Danh mục sự kiện

**Tín hiệu vào owner** (nội bộ):

| Sự kiện | Producer | Trường bắt buộc | Ghi chú |
|---|---|---|---|
| `vad.speech_start` / `vad.speech_end` | Nhánh VAD | `w` | Vị trí theo mẫu, không theo giờ nhận gói |
| `turn.eou` | Turn detector | `turn_id`, `revision`, `complete`, `p` | Kết quả cho đúng revision đã hỏi |
| `asr.partial` | ASR | `turn_id`, `revision`, `text`, `stable_prefix?` | Chỉ caption và speculation; `stable_prefix` không phải confidence |
| `asr.final` | ASR | `turn_id`, `revision`, `text`, `model_id`, `language`, `quality_flags` | Confidence thiếu thì để unknown |
| `llm.delta` / `llm.done` | LLM adapter | `generation_id`, `status` | `done` có status: completed / cancelled / failed / incomplete |
| `tts.audio` / `tts.done` | TTS adapter | `generation_id`, `chunk_id`, `sequence` | |
| `timer` | Scheduler | token `(kind, turn_id, revision)` | Token lệch thì owner bỏ |
| `client.played` / `client.done` | Client | `generation_id`, `played_sample_offset` | Xem §17.9 |

**Owner phát ra** (client, log, worker):

| Sự kiện | Khi nào | Trường |
|---|---|---|
| `turn.open` / `turn.reopen` / `turn.commit` | Chuyển trạng thái lượt | `turn_id`, `revision` |
| `response.created` | Tạo response (speculative) | `generation_id`, `turn_id`, `revision` |
| `text.chunk` | Mệnh đề từ chunker | `generation_id`, `chunk_id`, `raw_text`, `spoken_text` |
| `audio.start` | Trước chunk audio đầu của một generation | `generation_id`, `format`, `sample_rate`, `channels` |
| `audio.chunk` | Mỗi chunk | `generation_id`, `chunk_id`, `sequence`, payload |
| `audio.end` | Đã gửi hết audio của generation | `generation_id`, `last_sequence` |
| `client.clear` | Barge-in, cancel | `generation_id` **bị huỷ** |
| `response.done` | Kết thúc response | `generation_id`, `status`, `reason` |
| `error` | Lỗi giao thức hoặc backend | `code`, `message`, định danh liên quan |

### 17.5.3 Quy tắc thứ tự

1. **`sequence` tăng chặt trong mỗi luồng** (một hướng của một kết nối, hoặc một generation, tuỳ quy ước đã chọn ở Chương 16 §16.8.2).
2. **Trong một generation:** `response.created` < mọi `text.chunk`/`audio.chunk` < `audio.end` < `response.done`. Terminal luôn đến **sau cùng**. HF s2s bảo đảm điều này bằng cách đặt mọi phần text/tool, usage và input TTS tương ứng vào **một queue duy nhất**, nên phần sau và terminal không vượt được phần trước (**Reported**).[^engine]
3. **Transcript của bot:** HF phát `response.output_audio_transcript.delta`, rồi đúng một `.done` **sau** `response.output_audio.done` và **trước** `response.done`, kể cả khi bị huỷ (**Reported**).[^engine]
4. **Phía user:** `speech_started` < `speech_stopped` < `committed` < `item.created` < `transcription.completed`, mỗi loại đúng một lần cho một lượt đã commit (HF giữ stop và final trong lúc còn reopen được, **Reported**).[^hf]
5. **Nhân quả:** response của `(turn, rev)` không được tạo trước `soft_end` của revision đó, và không được `RELEASED` trước `turn.commit` của revision đó (**Synthesis**).
6. **Một response active tại một thời điểm.** HF trả lỗi `conversation_already_has_active_response` khi client yêu cầu response thứ hai (**Reported**).[^engine]

### 17.5.4 Ánh xạ sang OpenAI Realtime / HF s2s

Nếu muốn dùng SDK có sẵn, schema nội bộ phải ánh xạ được sang giao thức ngoài. Bảng dưới là ánh xạ gần đúng (**Synthesis**; tên sự kiện HF là **Reported**).[^engine][^hf]

| Schema chương này | OpenAI Realtime (HF s2s hỗ trợ) | Khác biệt cần nhớ |
|---|---|---|
| `vad.speech_start` | `input_audio_buffer.speech_started` | HF dùng sự kiện này để kích hoạt cancel khi đang có response |
| `vad.speech_end` | `input_audio_buffer.speech_stopped` | HF **giữ lại** khi lượt còn reopen được |
| `turn.commit` | `input_audio_buffer.committed` + `conversation.item.created` | |
| `asr.partial` | `conversation.item.input_audio_transcription.delta` | HF chỉ phát phần tăng trưởng **đã xác nhận** (append-only, giữ lại từ mới nhất); không có sự kiện rút lại transcript |
| — | `speech_to_speech.input_audio_transcription.snapshot` | Extension opt-in, chỉ để hiển thị, theo `item_id` |
| `asr.final` | `...input_audio_transcription.completed` | Client coi đây là **authoritative**, thay partial cùng `item_id` |
| `response.created` | `response.created` | |
| `text.chunk` | `response.output_audio_transcript.delta` | |
| `audio.chunk` | `response.output_audio.delta` | |
| `audio.end` | `response.output_audio.done` | |
| `response.done(status, reason)` | `response.done` | `cancelled` + `turn_detected` / `client_cancelled` |
| `client.clear` | WS: client tự flush khi nhận `speech_started`/cancel; WebRTC: `output_audio_buffer.clear` | `output_audio_buffer.clear` chỉ có ở WebRTC, xoá audio **server** còn giữ |
| `client.played` | `conversation.item.truncate` | HF chấp nhận như **no-op**, không cắt history phía server |
| `response.cancel` | `response.cancel` | |

Hai điểm khác cốt lõi: (1) OpenAI Realtime không có trường `revision`; HF thay bằng việc giữ sự kiện cho tới commit. (2) Giao thức không có sự kiện **rút lại** transcript đã phát, nên HF chỉ phát phần đã ổn định (**Reported**).[^engine] Nếu bạn tự viết gateway, có `revision` trong schema thì client được phép hiển thị cả phần chưa ổn định.

---

## 17.6 `generation_id`, dữ liệu cũ và tính đơn điệu

### 17.6.1 Hai cơ chế khác nhau: dừng việc và lọc kết quả

Cancellation có hai nửa, và hệ thống cần **cả hai** (**Synthesis**):

| | **Dừng việc** (cancel) | **Lọc kết quả** (stale guard) |
|---|---|---|
| Mục đích | Giải phóng compute, slot, kết nối | Bảo đảm không gì cũ đến tai user hay vào history |
| Cách làm | Đóng stream HTTP/WS, huỷ task, gửi lệnh abort | So `generation_id` của dữ liệu với generation hiện hành |
| Có chắc chắn không | **Không.** Thường chỉ best-effort | **Có**, nếu kiểm ở đúng chỗ |
| Hỏng thì sao | Lãng phí GPU, có thể dính `429` | Bot nói tiếp câu cũ |

Vì sao không thể chỉ dựa vào cancel: HF s2s ghi rõ cancel phía server là best-effort. Đóng kết nối client **không bảo đảm** server dừng tính trên GPU, nên "stale-result filtering stays required". Với TTS `/v1/audio/speech`, giao diện chuẩn **không có** thao tác huỷ phía server (**Reported**).[^backends] Luôn có một khoảng thời gian mà backend vẫn sinh dữ liệu cho một generation đã chết. Script ở Phụ lục mô phỏng TTS còn chạy 120 ms sau lệnh cancel: gateway bắt được 2 chunk rò (**Reproduced**).

### 17.6.2 Kiểm ở đâu

Quy tắc: **kiểm ở mọi ranh giới mà dữ liệu đổi chủ, và luôn kiểm ở chặng cuối**.

| Điểm kiểm | Bỏ cái gì | Nếu thiếu |
|---|---|---|
| Vòng lặp token của LLM worker | Token sau khi gen bị supersede; thoát vòng lặp | Tốn compute; text cũ đi tiếp vào chunker |
| Chunker → TTS queue | Mệnh đề của gen cũ | TTS tổng hợp câu không ai nghe |
| TTS worker, trước mỗi request | Câu xếp hàng của gen cũ | Tốn slot TTS |
| **Send loop (điểm publish ra client)** | Chunk audio/text của gen cũ | Chunk rò từ TTS best-effort tới client |
| **Client (chặng cuối)** | Chunk đang trên đường mạng | Bot nói tiếp sau khi đã `clear` |
| Ghi history | Text của gen không phải hiện hành | History có câu bot chưa nói |

Nguồn ChatGPT trong wiki mô tả đúng mẫu này: worker LLM thoát vòng lặp token khi generation bị supersede và **không** append câu bị bỏ vào history; worker TTS bỏ câu xếp hàng của generation cũ và phát `audio_cancel` nếu bị supersede giữa chừng (**Reported**). Wiki cũng ghi nhận sketch đó tăng `generation_id` ngay ở frame đầu vượt ngưỡng (chưa có duration gate) và không tự xoá TTS queue, nên bản thật phải bổ sung cả hai (**Observed**).[^barge]

### 17.6.3 Check-then-act: race nằm giữa "kiểm" và "gửi"

```python
# SAI: giữa hai dòng, owner có thể đã tăng generation (ở thread/task khác)
if chunk.gid == session.gid:
    await ws.send(chunk)          # await nhường quyền → barge-in chen vào được
```

Có hai cách chữa (kiến thức nền):

1. **Một consumer duy nhất cho output, và kiểm trong cùng bước gửi.** HF s2s: send loop là consumer duy nhất của output queue (cả WebSocket lẫn WebRTC), và chính nó thực hiện chuỗi huỷ khi có `speech_started` (**Reported**).[^engine] Không ai khác đổi generation giữa lúc nó kiểm và lúc nó gửi.
2. **Kiểm nguyên tử cùng lúc với publish.** HF s2s gắn **session generation** vào kết quả STT và kiểm "atomically with queue publication", để kết quả cũ không xuất hiện sau teardown hay trong session dùng lại slot (**Reported**).[^backends]

Và vì sao vẫn cần guard ở client: dù server kiểm hoàn hảo, chunk đã **ra khỏi socket** trước barge-in vẫn đang trên mạng hoặc trong buffer của client.

### 17.6.4 Nghiên cứu cấu trúc: `CancelScope` của HF s2s

Thiết kế ngắt lời của HF s2s là ví dụ tốt để học (**Reported**).[^engine]

- Một `CancelScope` dùng chung giữa VAD, send loop và LLM/TTS, gồm **bộ đếm generation** và **cờ discarding**. Nó thay cho thiết kế cũ "cancel event + discard flag".
- Thread pipeline ghi lại generation lúc bắt đầu response và gọi `is_stale(gen)` **trên từng token**.
- `cancel()` tăng generation, làm mọi generation trước đó thành stale.
- `response_done(gen)` chỉ xoá cờ discarding khi sentinel có **cùng generation**; `new_response()`/`reset()` cũng xoá cờ.
- Output mang `cancel_generation`; send loop bỏ output stale hoặc không hiện hành khi đang discarding, nhưng **giữ lại usage** để tính tiền.
- Một response speculative bị thay thế vẫn gửi một **terminal chỉ mang lifecycle** (không nội dung) để router đóng được response active mà không lộ nội dung cũ.

Ba bài học tổng quát (**Synthesis**):

1. **Bộ đếm tốt hơn cờ boolean.** Cờ "cancelled" phải được reset, và reset sai thời điểm là bug. Bộ đếm chỉ tăng, so sánh `==` là đủ.
2. **Cờ nào được bật thì phải có sentinel để tắt.** Đó là lý do HF không gọi `cancel()` khi không có response active: bật discarding mà không có sentinel nào tới xoá nó.
3. **Huỷ nội dung, không huỷ kế toán.** Usage, sentinel điều khiển và sự kiện phía user phải sống sót qua flush.

### 17.6.5 Guard phía client: floor đơn điệu

Guard ở Chương 16 §16.11 đổi `generation_id` khi nhận `clear(new_gid)`. Schema của tài liệu thiết kế lại gửi `client.clear(generation_id)` với generation **bị huỷ**. Guard an toàn cho cả hai cách, và cho cả khi message đảo thứ tự, dựa trên hai số **chỉ tăng** (**Synthesis**):

```text
cur   = generation đang phát (chỉ tăng)
floor = mọi generation ≤ floor đã bị clear (chỉ tăng)

clear(g)        : floor = max(floor, g); nếu cur ≤ floor → flush worklet (fade ngắn)
audio.start(g)  : nhận nếu g > floor và g > cur → cur = g, last_seq = −1
audio.chunk(g,s): phát nếu g == cur và g > floor và s > last_seq → last_seq = s
```

Bất biến: sau khi client xử lý `clear(g)`, mọi chunk có `gid ≤ g` bị bỏ **vĩnh viễn**, vì `floor` không bao giờ giảm. Một generation mới chỉ được phát sau `audio.start` của nó, và generation đó phải lớn hơn mọi thứ đã thấy.

Property test ở Phụ lục (10 000 lần chạy cho mỗi mức đảo thứ tự, TTS rò 0–2 chunk sau mỗi lần huỷ) so ba loại guard (**Reproduced**):

| Guard | Không đảo thứ tự: chunk vi phạm (số lần chạy có vi phạm) | Đảo 15 %: chunk vi phạm (số lần chạy) |
|---|---|---|
| Naive (phát mọi chunk, clear chỉ flush) | 26 875 (9 140) | 52 988 (9 967) |
| Chỉ so `gid == cur`, clear không đổi `cur` | 26 875 (9 140) | 48 075 (9 931) |
| **Floor + cur + seq** | **0 (0)** | **0 (0)** |

Guard "chỉ so `gid == cur`" **không tốt hơn naive** khi không có đảo thứ tự: chunk rò sau clear vẫn mang `gid == cur`. Đây là bug phổ biến nhất: clear chỉ xoá buffer hiện có mà không nâng "sàn".

Giá phải trả của guard floor: nếu `audio.chunk` đầu tiên tới **trước** `audio.start` của nó (đảo thứ tự giữa hai kênh), chunk đó bị bỏ. Đó là mất dữ liệu, không phải phát sai. Muốn tránh, cho mỗi chunk mang đủ metadata để tự đóng vai `audio.start`, hoặc đi cùng một kênh có thứ tự.

### 17.6.6 Quy tắc cho định danh

- Không bao giờ reset `generation_id` về 0 khi sang lượt mới. Chunk muộn của lượt trước có thể trùng số với generation mới.
- Cancel **cũng tăng** generation (không chỉ response mới). Trong kịch bản A, gen 1 bị huỷ thì generation nhảy lên 2, response kế tiếp là gen 3. Khoảng trống là bình thường; điều cần là đơn điệu.
- Không có response active thì cancel là no-op, **không** tăng generation (để khớp với quy tắc sentinel ở trên).

---

## 17.7 Barge-in: phát hiện và gating

### 17.7.1 Chuỗi cổng

Barge-in là bài toán phân loại: trong lúc bot nói, đoạn âm thanh vừa thu là (a) user muốn ngắt, (b) user phản hồi ngắn không muốn ngắt, (c) nhiễu, (d) người khác, hay (e) chính giọng bot lọt lại? Mỗi cổng loại một nhóm:

```text
mic (sau AEC) ─► [denoise nhẹ, chỉ nhánh này] ─► VAD p ≥ ngưỡng(nhiễu nền)
   ─► duration gate (speech liên tục ≥ G ms)        loại (c) tiếng ngắn: ho, gõ phím
   ─► [speaker lock: cosine ≥ τ]                    loại (d) TV, người bên cạnh
   ─► [quick ASR: ≥ 2 từ, không trùng câu bot]      loại (e) echo, một phần (b)
   ─► phân loại backchannel / lệnh dừng             tách (b) khỏi (a)
   ─► interrupt | ghi nhận không ngắt | bỏ qua
```

Các cổng trong ngoặc vuông là tuỳ chọn. Nguồn: [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md) (**Reported**, cả hai nguồn là AI report thứ cấp chưa đo).[^barge]

### 17.7.2 Duration gate và đánh đổi

Giá trị khởi điểm trong wiki (**Reported**):[^barge][^wikidesign]

| Ngữ cảnh | Gate | Ưu tiên |
|---|---|---|
| Môi trường sạch | 100–200 ms speech liên tục (thiết kế gợi ý thử 150–200) | Nhạy |
| Môi trường ồn | threshold 0.7 và ≥ 300–500 ms (reference server: 400 ms) | Chống ngắt nhầm |
| HF s2s | Barge-in luôn cần `min_speech_ms` = 384 ms (**Observed**)[^cli] | |

Hai nguồn mâu thuẫn (100–200 ms so với 300–500 ms); wiki không chọn bên.[^barge] Mô phỏng ở Phụ lục cho thấy đánh đổi cụ thể trên cùng một kịch bản (**Reproduced**, tham số giả định):

| | Gate 400 ms (A) | Gate 150 ms (B) |
|---|---|---|
| "(ho)" 150 ms | Chặn | Chặn (cần 5 frame = 160 ms) |
| "ừ" 250 ms | Chặn | **Ngắt nhầm**: bot im sau 2 028 ms |
| Từ lúc user mở miệng tới lúc owner quyết định | 448 ms | 192 ms |
| Time-to-silence (tới lúc client im) | 498 ms | 242 ms |

Phép tính: quyết định = 32 ms (VAD thấy frame đầu) + `ceil(G / 32) × 32`. Với G = 400: 32 + 416 = 448 ms. Time-to-silence cộng thêm 40 ms downlink và 10 ms fade.

Kịch bản B còn cho thấy hậu quả thứ hai của ngắt nhầm: "ừ" trở thành một lượt mới; 750 ms sau user nói "Khoan, đổi sang thứ bảy" trong grace nên lượt đó **reopen** thành revision 2, và LLM nhận "ừ Khoan, đổi sang thứ bảy". Ngắt nhầm không chỉ làm bot im, nó còn làm bẩn transcript lượt sau.

### 17.7.3 Ngưỡng theo nhiễu

Đo xác suất VAD và RMS trong 2–3 s đầu, trước khi user nói. Nếu xác suất nền trung bình > 0.3, nâng threshold lên 0.65–0.7 và nâng luôn gate barge-in (**Reported**). Thiết kế thêm: không tự động nâng theo một số cố định khi chưa calibrate (**Synthesis**).[^wikidesign] Denoise (RNNoise, DeepFilterNet 3) chỉ cho nhánh VAD/barge-in, không cho ASR.[^barge]

### 17.7.4 Speaker lock và quick ASR

- **Speaker lock:** so cosine embedding ECAPA/CAM++ của đoạn mới với embedding user (lấy từ lượt đầu, cập nhật dần), bỏ nếu dưới khoảng 0.5–0.6; ngưỡng phải calibrate (**Reported**).[^barge] Speaker lock **không phải xác thực** (**Synthesis**).[^design] Embedding trên 400 ms audio kém tin cậy hơn nhiều so với trên vài giây; chi tiết ở [Chương 14](chuong-14-speaker-embedding-speaker-lock-diarization.md).
- **Quick ASR:** yêu cầu ≥ 2 từ và không trùng câu bot đang phát (**Reported**).[^barge] Điều kiện "không trùng câu bot" là lưới cuối chống echo còn sót sau AEC. Với tiếng Việt, "2 từ" nên hiểu là 2 âm tiết, vì ASR xuất âm tiết (**Synthesis**, xem Chương 5). Quick ASR cộng thêm thời gian vào quyết định, nên chỉ hợp với gate dài.

### 17.7.5 Echo: bot tự ngắt chính mình

Lỗi phổ biến nhất của prototype dùng loa ngoài: VAD thấy giọng bot qua mic và bot tự ngắt. Ba tầng phòng thủ (**Reported**):[^barge]

1. Tắt mic khi bot nói: hết echo, nhưng cũng hết barge-in.
2. AEC trình duyệt (`echoCancellation`, `noiseSuppression`, `autoGainControl`), VAD vẫn chạy.
3. AEC tầng WebRTC, cộng so sánh audio bot vừa phát với tín hiệu mic; chỉ ngắt khi tiếng mới khác đáng kể audio TTS.

Chi tiết AEC ở [Chương 7](chuong-07-front-end-am-hoc-echo-nhieu-gain.md), hiện tượng VAD trên kênh có echo ở [Chương 10 §10.8](chuong-10-vad-endpointing-va-turn-detection.md).

### 17.7.6 Backchannel tiếng Việt

Report khuyến nghị: "ừ", "vâng", "ok" trong lúc bot nói thì không ngắt (**Reported**).[^barge] Thiết kế cảnh báo ngược lại: đừng mặc định coi mọi "ừ/vâng/ok" là backchannel, vì trong một số domain đó chính là lời xác nhận (**Synthesis**).[^design] Hai ý không mâu thuẫn nếu tách **ba kết cục** thay vì hai (**Synthesis**):

| Kết cục | Bot | Lượt user | Khi nào |
|---|---|---|---|
| **Ngắt** | Huỷ response | Lượt mới | Lệnh dừng, sửa, câu hỏi mới |
| **Ghi nhận, không ngắt** | Tiếp tục | Ghi vào history như phản hồi của user | Xác nhận trong lúc bot đang đọc lại thông tin |
| **Bỏ qua** | Tiếp tục | Không ghi | Tiếng ậm ừ thuần nhịp |

HF s2s có cơ chế gần với kết cục thứ hai: khi `turn_detection.interrupt_response` tắt, speech trong lúc response đang phát vẫn được **transcribe**, nhưng response tiếp tục (**Reported**).[^engine]

Danh sách tham khảo để bắt đầu (kiến thức nền về hội thoại tiếng Việt, cần kiểm trên dữ liệu thật; **Synthesis**):

| Nhóm | Ví dụ | Xử lý gợi ý |
|---|---|---|
| Ậm ừ theo nhịp | ừ, ừm, ờ, à, dạ (ngắn, đều giọng), ừa (Nam) | Bỏ qua khi bot đang trình bày |
| Xác nhận | vâng, dạ vâng, đúng rồi, ok, được | Ghi nhận; **ngắt** nếu bot vừa hỏi và đang nói tiếp câu khác |
| Ngạc nhiên / hỏi lại | thế à, vậy hả, sao cơ, hả | Thường nên ngắt: user không theo kịp |
| **Lệnh dừng / sửa** | thôi, dừng, khoan, đợi đã, không phải, sai rồi, ý tôi là | Ngắt ngay; có thể dùng làm đường tắt bỏ qua phần còn lại của gate |

"Dạ" và "vâng" là trường hợp khó: chúng vừa là ậm ừ lịch sự, vừa là xác nhận. Phân biệt cần ngữ cảnh: câu bot vừa nói có phải câu hỏi không, và domain có hành động cần xác nhận không. Với tool ghi, đừng bao giờ coi "dạ" chen ngang là xác nhận; hãy hỏi lại một câu riêng (Chương 12 §12.6.3).

### 17.7.7 Gating hai pha (tuỳ chọn)

Bảng §17.7.2 cho thấy không có một gate nào vừa nhạy vừa chống ngắt nhầm. Một thiết kế lấy được một phần cả hai (**Synthesis**, không có trong nguồn wiki, chưa đo):

1. **Pha 1 (~150–200 ms):** client **giảm âm lượng** bot (duck, ví dụ −12 dB) hoặc tạm dừng phát, nhưng **giữ** queue. LLM/TTS vẫn chạy.
2. **Pha 2 (~400 ms + speaker lock/quick ASR):** nếu xác nhận là ngắt → cancel đầy đủ như §17.8. Nếu không → khôi phục âm lượng, phát tiếp.

User cảm thấy bot "nhường lời" sau ~200 ms, nhưng response chỉ bị huỷ khi chắc chắn. Giá phải trả: thêm hai lệnh client (`client.duck`, `client.resume`), compute chưa được giải phóng trong pha 1, và nếu chọn tạm dừng thay vì giảm âm lượng thì ngắt nhầm để lại một khoảng lặng nghe thấy được.

---

## 17.8 Trình tự barge-in và cancellation xuyên tầng (Q2, Q4)

### 17.8.1 Trình tự

Trình tự gốc của tài liệu thiết kế (**Reported**, gộp từ hai report): mic luôn mở có AEC → phát hiện user nói đủ lâu → `generation_id++` → cancel LLM, cancel request TTS, xoá câu xếp hàng → `{"type":"clear"}` để client flush AudioWorklet → history chỉ lưu phần đã phát kèm `[bị ngắt]` → client bỏ mọi chunk của generation cũ.[^design][^barge]

Chương này chi tiết hoá và sắp xếp lại theo **lý do** của từng bước (**Synthesis**):

| # | Bước | Ai | Vì sao ở vị trí này |
|---|---|---|---|
| 0 | Quyết định barge-in (qua mọi cổng) | Owner | Từ đây trở đi không quay lại |
| 1 | `old = gid; gid += 1` | Owner, nguyên tử | Từ giây phút này **mọi** dữ liệu của `old` là stale ở mọi điểm kiểm. Các bước sau dù chậm hay lỗi cũng không làm audio cũ lọt ra từ server |
| 2 | Gửi `client.clear(old)` trên kênh control, **trước** mọi thứ khác ra client | Send loop | Đường ngắn nhất tới im lặng. Không xếp sau audio đang chờ gửi |
| 3 | Cancel LLM stream của `old` | LLM adapter | Ngừng sinh text; giải phóng compute |
| 4 | Cancel request TTS của `old`; xoá câu xếp hàng | TTS adapter | Giải phóng slot TTS |
| 5 | Flush output queue phía server: bỏ nội dung của `old`, **giữ** sentinel điều khiển, usage, sự kiện phía user | Send loop | Không mất kế toán và không mất sự kiện user |
| 6 | Mở lượt mới: `turn_id+1`, turn buffer từ **đầu đoạn nói barge-in** − pre-roll | Owner | Không mất "Khoan," |
| 7 | Phát `response.done(old, cancelled, turn_detected)` | Send loop | Client và log biết vòng đời đã đóng |
| 8 | Khi nhận `client.played(old, offset)`: cắt history | Owner | Cần số liệu từ client, nên đến sau cùng |

Ở bước 2, "trước mọi thứ khác" có nghĩa là: nếu send loop có một hàng đợi audio chờ gửi, `clear` phải **vượt hàng** (kênh ưu tiên), hoặc hàng đợi đó phải được flush trước. Trên WebSocket, mọi thứ đi chung một luồng TCP: nếu server đã dồn vài giây audio vào socket buffer, `clear` phải xếp sau chúng. Vì vậy downlink nên được **pace** gần thời gian thực với một trần nhỏ (Chương 16 §16.5.4), thay vì đẩy hết audio TTS ra ngay khi có (**Synthesis**).

### 17.8.2 Q4: tăng generation trước hay clear trước?

Trả lời ngắn: **thứ tự quan trọng là "tăng generation" phải xảy ra trước bất kỳ lần publish nào tiếp theo**, và việc đó phải nguyên tử với điểm publish. Còn `clear` đi trước hay sau `response.done` là chuyện phụ.

HF s2s làm theo thứ tự khác chương này, khi `speech_started` đến lúc response đang active (**Reported**):[^engine]

```text
response.output_audio.done → (transcript .done nếu đã có text) → response.done(cancelled, turn_detected)
→ input_audio_buffer.speech_started → tăng generation → flush output/text queue (giữ usage, sentinel,
   sự kiện phía user) → xoá response_playing
```

HF phát các terminal **trước** khi tăng generation, nhưng vẫn an toàn vì **chính send loop** làm toàn bộ chuỗi này: không có publisher nào khác chen vào giữa. Bài học (**Synthesis**): nếu publish đi qua một consumer duy nhất, thứ tự nội bộ là tự do. Nếu có nhiều publisher (nhiều task cùng `ws.send`), hãy tăng generation **đầu tiên**.

### 17.8.3 Cancel ở từng tầng: thật sự dừng được gì

| Tầng | Cơ chế huỷ | Thật sự dừng | Phần còn sót | Guard bù |
|---|---|---|---|---|
| ASR speculative (reopen) | Huỷ request/progressive window | HF: final huỷ progressive đang chạy; revision mới vô hiệu hoá việc cũ đã xếp hàng và huỷ request cũ đang chạy, kiểm "relevance" trước và trong khi chạy (**Reported**)[^backends] | Inference GPU đang chạy (best-effort) | Bỏ kết quả lệch `(turn, rev)` |
| LLM | Đóng stream HTTP/SSE; huỷ task | Client ngừng nhận ngay | Server có thể sinh thêm vài token; việc server có abort khi client ngắt hay không tuỳ engine (**Unverified** trong wiki) | `is_stale(gen)` mỗi token |
| TTS `/v1/audio/speech` | Đóng HTTP response | Client ngừng nhận; HF ngừng publish audio cục bộ | Giao diện chuẩn **không có** huỷ phía server; server có thể tính tiếp (**Reported**)[^backends] | Kiểm gen ở send loop |
| VieNeu GPU | Như trên | — | Slot giải phóng khi request gặp EOS hoặc frame cap (**Reported**)[^vieneuapi]; việc ngắt kết nối có giải phóng slot sớm không, wiki không ghi (**Unverified**) | Theo dõi `/health` (`active`, `waiting`); dự phòng `429` |
| Queue server | Flush | Mọi thứ đang chờ | — | Giữ sentinel/usage |
| Mạng | Không huỷ được | — | Chunk đang bay | Guard floor ở client |
| Client WS | Flush AudioWorklet + fade ngắn | Âm thanh dừng sau ≤ 1 render quantum + fade | — | — |
| Client WebRTC | `output_audio_buffer.clear` xoá audio server còn giữ (**Reported**)[^engine] | Audio chưa gửi | Audio đã trong jitter buffer của trình duyệt (cỡ vài chục ms, kiến thức nền) | Chấp nhận |

Fade khi flush: cắt ngang một sóng đang phát tạo tiếng click (Chương 1). HF browser demo dùng fade 32 frame khi phát (**Reported**).[^demo] Fade vài ms là đủ.

**Deployment gate:** nếu một SDK không cho huỷ từ bên trong (gọi đồng bộ, không trả quyền cho tới khi xong), đó là một **gate triển khai**, không phải chi tiết (**Synthesis**).[^design] Hệ quả thực tế: response bị huỷ vẫn giữ slot TTS tới hết câu. Với `VIENEU_MAX_STREAMS` nhỏ, vài lần barge-in liên tiếp có thể làm request của lượt mới nhận `429` (**Synthesis** từ hành vi `429` khi hết slot, **Reported**).[^vieneuapi]

### 17.8.4 Time-to-silence và time-to-release (Q6)

Thiết kế yêu cầu đo cả hai: user-speech → âm thanh bot dừng (nghe được), và thời gian giải phóng compute (**Synthesis**).[^design]

```text
T_silence = t(client im hẳn) − t(user bắt đầu nói)
          = phát hiện VAD + duration gate (+ speaker lock, quick ASR)
            + xử lý ở owner + clear trên downlink (+ chờ sau audio đã dồn trong socket)
            + flush worklet + fade

T_release = t(backend cuối cùng ngừng tính cho gen cũ) − t(user bắt đầu nói)
          = phần quyết định + max(độ trễ dừng của LLM, của TTS, của ASR speculative)
```

Mô phỏng (**Reproduced**, tham số giả định: downlink 40 ms, TTS còn chạy 120 ms sau cancel, LLM 50 ms):

| | Quyết định | T_silence | T_release | Chunk rò bị gateway bỏ | Audio cũ được phát sau clear |
|---|---|---|---|---|---|
| A. Có guard, gate 400 ms | 448 ms | 498 ms | 546 ms | 2 | 0 ms |
| B. Có guard, gate 150 ms | 192 ms | 242 ms | 244 ms | 1 | 0 ms |
| C. **Không guard**, gate 400 ms | 448 ms | **1 130 ms** | 546 ms | 0 | **640 ms** |

Hai quan sát:

- Ở A, duration gate chiếm 416/498 ms của T_silence. Muốn bot im nhanh hơn, đòn bẩy lớn nhất là gate (hoặc gating hai pha), không phải mạng hay worklet.
- Ở C, quyết định và cancel giống hệt A, nhưng 2 chunk rò (do TTS chạy trước playback, chúng thuộc **mệnh đề thứ tư** "Hoặc anh chọn…") đi tới client sau `clear` và được phát. User nghe bot ngừng, rồi 2 ms sau nói tiếp một câu **khác**, kéo dài 640 ms. T_silence tăng gấp đôi.

Nếu T_release ≫ T_silence, hệ thống đang "lãng phí ngầm": user nghe thấy bot dừng, nhưng GPU vẫn bận, và session khác trên cùng GPU chậm đi (Chương 12 §12.5.3).

### 17.8.5 Chứng minh không còn chunk cũ nào được phát (Q2)

Lập luận (**Synthesis**), dựa trên ba lớp phòng thủ:

1. **Server:** sau bước 1, `gid` hiện hành > `old`. Mọi điểm publish kiểm `chunk.gid == gid` nguyên tử với việc gửi (§17.6.3). Vậy sau bước 1, server không gửi thêm chunk nào của `old`.
2. **Mạng:** các chunk của `old` đã gửi **trước** bước 1 có thể còn đang bay. Số lượng hữu hạn, chặn trên bởi trần downlink.
3. **Client:** `clear(old)` nâng `floor ≥ old`. `floor` không bao giờ giảm. Mọi chunk có `gid ≤ floor` bị bỏ, bất kể nó tới trước hay sau. Chunk đã có trong worklet bị flush khi xử lý clear.

Vậy sau khi client xử lý `clear(old)`, không có chunk nào của `old` được phát. Khoảng "đang phát" chỉ còn từ lúc user bắt đầu nói tới lúc client xử lý clear: đó chính là T_silence. Property test ở §17.6.5 kiểm bất biến này trên 20 000 lần chạy có rò và đảo thứ tự (**Reproduced**).

Một lỗ hổng cần đóng: nếu `clear` bị **mất** (kết nối rớt đúng lúc), client không bao giờ nâng floor. Cách chữa: `audio.start(new)` của generation mới cũng ngầm nâng `cur` lên, nên chunk cũ (`gid < cur`) vẫn bị bỏ; và khi reconnect, client bắt đầu với `floor = generation hiện hành của server` (**Synthesis**).

### 17.8.6 Một hàm cancel, nhiều lý do

Các lý do cancel khác nhau nhưng nên đi qua **một** hàm (**Synthesis**):

| Lý do | Nguồn | Response đã phát chưa | Cần `client.clear` | Ghi history |
|---|---|---|---|---|
| `reopen` | Owner (user nói tiếp trong grace) | Chưa (SPECULATIVE) | Không | Không |
| `turn_detected` | Barge-in | Có | Có | Phần đã phát + `[bị ngắt]` |
| `client_cancelled` | Client gửi `response.cancel` | Có thể | Có | Phần đã phát |
| `session_end` | Disconnect, timeout | Có thể | Không cần (client đã đi) | Tuỳ chính sách lưu trữ |
| `failed` / `incomplete` | Backend lỗi, hết token | Có thể | Tuỳ | HF rollback history (**Reported**)[^engine] |

Với `client_cancelled`, HF s2s làm cùng chuỗi huỷ khi có response active hoặc đang xếp hàng, xoá các request model đang xếp hàng nhưng giữ sentinel điều khiển, kết thúc response với `status="cancelled", reason="client_cancelled"` và bật lại nghe (**Reported**).[^engine]

---

## 17.9 Cắt history theo phần đã phát (Q7)

### 17.9.1 Nguyên tắc

History phải phản ánh **cái user đã nghe**, không phải cái LLM đã sinh. LLM có thể đã sinh bốn câu, TTS đã tổng hợp ba câu (vì chạy nhanh hơn thời gian thực), client đã nhận ba câu, nhưng user chỉ nghe một câu rưỡi. Nếu history lưu bốn câu, lượt sau LLM sẽ nói "như em đã nói…" về điều user chưa nghe (Chương 12 §12.5.1).

### 17.9.2 Giao thức played offset

1. Client đếm số mẫu **thực sự render** ra loa cho mỗi generation. HF browser demo đếm PCM đã render, **không tính** độ trễ khởi động và im lặng do underrun, và dùng số đó thay cho "đồng hồ lúc nhận sự kiện ngắt" của SDK (**Reported**).[^demo]
2. Khi xử lý `clear(old)`, client gửi `client.played(old, played_sample_offset)`.
3. Owner tra bảng `chunk_id → [mẫu đầu, mẫu cuối)` của generation đó (Chương 16 §16.6.4): mệnh đề phát hết thì lưu nguyên, mệnh đề phát dở thì lưu phần ước lượng kèm `[bị ngắt]`, mệnh đề chưa phát thì bỏ.

Ví dụ trong kịch bản A (**Reproduced**): đã phát 3 284 ms; mệnh đề 1 dài 2 160 ms (phát hết), mệnh đề 2 dài 3 240 ms (phát được 1 124 ms ≈ 35 %, tức khoảng 18 trên 54 ký tự). History:

```text
assistant: "Dạ, em đã kiểm tra lịch hẹn của anh. Lịch hiện tại là … [bị ngắt]"
```

Ở kịch bản C (không guard), client cũng báo 3 284 ms vì đó là con số lúc clear. Nhưng sau đó client phát thêm 640 ms của mệnh đề 4. **History sai**: user đã nghe "Hoặc anh chọn một…" mà history không có. Guard không chỉ bảo vệ tai user, nó còn bảo vệ tính đúng của history.

### 17.9.3 Độ chính xác: offset không phải là từ

Không có alignment giữa token và audio thì chỉ khẳng định được played offset, không khẳng định được chính xác từ nào đã phát (**Synthesis**).[^design] Cắt theo tỷ lệ ký tự trong mệnh đề rồi lùi về ranh giới từ là ước lượng. Chính sách an toàn: lưu mệnh đề phát dở dưới dạng "đã bắt đầu nói: …" và để LLM hiểu đó là xấp xỉ. Cách đưa tag `[bị ngắt]` vào prompt mà không để LLM nhại lại: Chương 12 §12.5.4.

### 17.9.4 `conversation.item.truncate`

Trong OpenAI Realtime API, `conversation.item.truncate` cho client báo phần audio của một item assistant đã thực sự được nghe (theo `item_id`, `content_index`, `audio_end_ms`), để server cắt phần chưa nghe khỏi ngữ cảnh. Mô tả này là kiến thức nền về API công khai, **không có** trong wiki; hãy kiểm với tài liệu hiện hành (**Unverified**). Trong HF s2s, sự kiện này được chấp nhận như một **no-op không phản hồi**, vì playback do client sở hữu và việc cancel đã loại bỏ generation tạm (**Reported**).[^engine] Demo của HF vẫn gửi truncate với số PCM đã render, nhưng server không đổi history (**Reported**).[^demo] Hệ quả: nếu dùng HF s2s và cần history khớp với cái user đã nghe, bạn phải tự cắt.

### 17.9.5 Khi ngắt nhầm

Mỗi lần ngắt nhầm ghi một `[bị ngắt]` giả vào history (Chương 12 §12.5.5). Nếu sau đó hệ thống phát hiện ngắt nhầm (quick ASR rỗng, bị lọc hallucination, hoặc chỉ là ậm ừ), có hai lựa chọn (**Synthesis**):

- **Không ghi tag**, coi như bot đã nói xong phần đã phát, và để LLM trả lời lượt mới bình thường.
- **Tiếp tục:** tạo response mới có chỉ dẫn "nói tiếp từ chỗ bị ngắt". Chỉ khả thi khi phần chưa phát còn được giữ, nên phải quyết định trước khi xoá text của generation cũ.

---

## 17.10 Kết thúc session (Q8)

Một session kết thúc vì client đóng, mất kết nối, timeout im lặng, vượt thời lượng tối đa, hoặc server shutdown. Thứ tự teardown (**Synthesis**, các ý HF là **Reported**):

1. **Đánh dấu đóng nguyên tử:** tăng **session generation** và `generation_id`. Từ đây mọi callback cũ đều stale. HF s2s gắn session generation vào kết quả và kiểm nó nguyên tử khi publish vào queue, để kết quả cũ không xuất hiện sau teardown hay trong một session dùng lại slot.[^backends]
2. **Ngừng nhận input:** bỏ audio uplink còn tới; huỷ timer của session.
3. **Huỷ mọi việc đang chạy:** LLM, TTS, ASR speculative và final, tool async. HF huỷ cả việc STT đang chạy lẫn đang chờ khi session kết thúc, và huỷ các tool handler async còn dở khi disconnect.[^backends][^engine]
4. **Flush queue,** bỏ callback đến trễ (thiết kế §7.2).[^design]
5. **Giải phóng tài nguyên theo session:** ASR streaming cache (GPU), state VAD, turn buffer, ring buffer, bảng `chunk_id`, speaker embedding. Danh sách đầy đủ: bảng state ở Chương 16 §16.7.1.
6. **Dọn transport trước khi dùng lại worker:** HF giữ cancellation hoạt động suốt lúc thiết lập kết nối, upload và đọc response, và dọn transport xong mới cho worker phục vụ session khác, để một upload cũ bị treo không làm session mới chờ tới HTTP timeout.[^backends]
7. **Ghi log vận hành tối thiểu:** metadata và latency, không audio và transcript theo mặc định (HF content-free, `--log_transcripts` là opt-in).[^design] Speaker embedding không vào log (Chương 23).
8. **Đóng kết nối.**

Hai tình huống cần test riêng:

- **Disconnect giữa lúc bot nói:** không cần `client.clear`; vẫn phải cancel LLM/TTS để giải phóng slot. Response kết thúc `cancelled` với lý do `session_end`.
- **Reconnect nhanh vào cùng `session_id`:** coi là session mới về mặt state âm thanh (ring buffer, VAD, resampler), nhưng có thể giữ history. Client bắt đầu với `floor` = generation hiện hành của server, để chunk của kết nối cũ không bao giờ được phát.

---

## 17.11 Khung code tham khảo

Đây là phần lõi của `turn_owner.py` (Python thuần, **Synthesis**, chỉ minh hoạ, đã chạy smoke test ở Phụ lục). Nó hiện thực: owner một luồng với hai máy trạng thái, timer có token, cancel một hàm với no-op khi không có response, output gate, guard stale ở gateway, cắt history theo played offset, và guard floor ở client. Không có `asyncio` (Chương 18) và không gọi model thật.

```python
class TurnOwner:
    # turn: IDLE | LISTENING | SOFT_ENDED | COMMITTED ; gid: chỉ owner được tăng
    def _cancel(self, reason):
        r = self.resp
        if r is None or r.state in (Resp.DONE, Resp.CANCELLED):
            return                                   # không có gì để huỷ: no-op, KHÔNG tăng gid
        old, was_released = r.gid, r.state is Resp.RELEASED
        self._new_generation()                       # 1. stale hoá trước mọi thứ khác
        r.state = Resp.CANCELLED
        if was_released:
            self.out.append(("client.clear", old))   # 2. đường nhanh nhất tới im lặng
        self.out += [("llm.cancel", old), ("tts.cancel", old), ("queues.flush", old),
                     ("response.done", old, "cancelled", reason)]

    def on_speech_start(self, speech_ms, bot_audible):
        if self.turn is Turn.SOFT_ENDED:             # reopen: cùng turn_id, revision+1
            self._cancel("reopen"); self.revision += 1; self.turn = Turn.LISTENING
            self.out.append(("turn.reopen", self.turn_id, self.revision)); return
        if self.turn is Turn.COMMITTED and bot_audible:
            if speech_ms < self.barge_ms: return     # chưa qua gate: chưa quyết
            self._cancel("turn_detected")
        if self.turn is not Turn.LISTENING:
            self.turn_id, self.revision, self.turn = self.turn_id + 1, 1, Turn.LISTENING
            self.out.append(("turn.open", self.turn_id))

    def on_soft_end(self, complete):
        if self.turn is not Turn.LISTENING: return
        self.turn = Turn.SOFT_ENDED
        g = self._new_generation()
        self.resp = Response(g, self.turn_id, self.revision)            # SPECULATIVE
        self.out.append(("response.create", g, self.turn_id, self.revision))
        self.out.append(("timer", self.reopen_ms if complete else 2000,
                         ("commit", self.turn_id, self.revision)))

    def on_timer(self, token):
        kind, turn_id, rev = token
        if kind != "commit" or (self.turn, self.turn_id, self.revision) != (Turn.SOFT_ENDED, turn_id, rev):
            return                                   # timer của revision cũ: tự vô hiệu
        self.turn = Turn.COMMITTED
        self.out.append(("turn.commit", turn_id, rev))
        self.resp.state = Resp.RELEASED              # mở output gate
        for c in self.resp.held: self.out.append(("tts.enqueue", self.resp.gid, *c))
        self.resp.held.clear()

    def on_text_chunk(self, gid, chunk_id, text):
        r = self.resp
        if r is None or gid != self.gid or r.gid != gid:
            self.out.append(("drop.stale_text", gid, chunk_id)); return
        if r.state is Resp.SPECULATIVE: r.held.append((chunk_id, text)); return
        self.out.append(("tts.enqueue", gid, chunk_id, text))

    def on_audio_chunk(self, gid, chunk_id, seq, n):
        if gid != self.gid:                          # kiểm ở điểm publish
            self.out.append(("drop.stale_audio", gid, seq)); return
        self.out.append(("client.audio", gid, chunk_id, seq, n))


class ClientGuard:                                   # cur, floor chỉ tăng
    def on_clear(self, gid):
        self.floor = max(self.floor, gid)
        return self.cur <= self.floor                # True → flush worklet + fade
    def on_audio_start(self, gid):
        if gid <= self.floor or gid <= self.cur: return False
        self.cur, self.last_seq = gid, -1; return True
    def on_chunk(self, gid, seq):
        if gid != self.cur or gid <= self.floor or seq <= self.last_seq: return False
        self.last_seq = seq; return True
```

Những gì khung này **cố ý chưa làm**:

- Gate barge-in chỉ có duration. Speaker lock, quick ASR, backchannel là các hàm thêm vào trước `_cancel("turn_detected")`.
- `on_speech_start` được gọi nhiều lần với `speech_ms` tăng dần; trong hệ thật đó là bộ đếm speech liên tục của nhánh VAD.
- Timer, LLM, TTS là "lệnh" trong `self.out`. Một runtime `asyncio` đọc `out`, thực thi và đưa sự kiện kết quả về inbox (Chương 18).
- Chưa có phần ghi history khi `audio.done` và chưa có teardown.

---

## 17.12 Contract tests và kịch bản kiểm thử

Đây là bộ test tối thiểu trước khi coi phần điều khiển lượt là xong. Tài liệu thiết kế đặt "không stale audio", "không duplicate final", "sequence/revision đơn điệu", "cancel giữa chunk" và "disconnect/reconnect" vào release gate 5 (**Synthesis**).[^wikidesign] Mỗi dòng nên là một test phát lại chuỗi sự kiện có timestamp vào owner (không cần model thật).

| Nhóm | Kịch bản | Kỳ vọng |
|---|---|---|
| Reopen | Ngừng 300 ms giữa câu, nói tiếp | Một `turn_id`, `revision` 1→2, response rev 1 bị huỷ, **không có audio nào phát**, LLM thấy một câu liền mạch |
| Reopen | Nói tiếp **sau** grace | Commit rev 1; câu sau thành barge-in hoặc lượt mới, tuỳ bot còn nói hay không |
| Timer | Timer commit của rev 1 bắn sau reopen | Bị bỏ qua |
| Commit | `asr.final` tới trễ sau commit | Không commit lần hai; không gọi LLM lần hai |
| Gate | Ho 150 ms, gõ phím, "ừ" 250 ms khi bot nói | Không ngắt (với gate đã chọn); log `rejected` |
| Barge-in | User nói 1,2 s khi bot nói | Một lần cancel; `client.clear(old)`; lượt mới chứa cả phần đầu câu (pre-roll tính từ đầu đoạn nói) |
| Stale | TTS rò 0–3 chunk sau cancel; mạng trễ 0–200 ms | 0 ms audio cũ phát sau khi client xử lý clear |
| Thứ tự | Đảo `clear` và `audio.chunk` | Không phát chunk cũ; chấp nhận mất chunk mới nếu tới trước `audio.start` |
| Cancel rỗng | `response.cancel` khi không có response | No-op; response kế tiếp phát bình thường |
| Cancel lặp | Hai barge-in sát nhau | Generation tăng đơn điệu; không response nào bị kẹt |
| History | Ngắt ở 0 %, giữa mệnh đề, đúng ranh giới mệnh đề, sau khi phát hết | History đúng phần đã nghe; không có `[bị ngắt]` khi đã phát hết |
| Tool | Tool call trong response bị huỷ | Không chạy; không gửi kết quả |
| Echo | Phát audio bot qua loa, không có user | 0 barge-in (với AEC bật) |
| Session | Disconnect giữa câu; reconnect | LLM/TTS bị huỷ; slot TTS về 0; không callback muộn vào session mới |
| Đo | Mọi kịch bản barge-in | Log T_silence, T_release, lý do cancel, `(turn, rev, gen)` |

---

## 17.13 Lỗi thường gặp: triệu chứng → nguyên nhân → cách sửa

| Triệu chứng | Nguyên nhân hay gặp | Cách sửa |
|---|---|---|
| Bot nói tiếp câu cũ vài trăm ms sau khi bị ngắt | Client không có guard, hoặc clear không nâng floor; chunk đang bay | Guard floor (§17.6.5) |
| Bot ngừng rồi "nhảy" sang một câu sau đó | TTS chạy trước playback; chunk rò của mệnh đề sau đi tới client (kịch bản C) | Guard ở send loop và client; pace downlink |
| Bot tự ngắt khi dùng loa ngoài | Echo lọt vào VAD | AEC; quick ASR so với câu bot; gate dài hơn khi bot nói |
| Bot ngắt khi user nói "ừ" | Gate quá ngắn; không có chính sách backchannel | Gate 300–500 ms trong môi trường ồn; ba kết cục §17.7.6; gating hai pha |
| User phải nói lại câu sau khi ngắt | Turn buffer mở lúc **quyết định** barge-in | Mở từ đầu đoạn nói − pre-roll; ring đủ dài |
| Hai câu trả lời chồng nhau | Hai owner; hoặc commit hai lần (timer + final) | Một owner; timer có token; commit kiểm trạng thái |
| Bot trả lời nửa câu đầu, bỏ nửa sau | Commit không bị huỷ khi reopen; timer cũ không kiểm `(turn, rev)` | Timer token |
| Tool chạy hai lần, hoặc chạy trên câu user chưa nói xong | Chạy tool trên speculative; thiếu idempotency key | Thang hành động §17.4.2 |
| History có câu bot chưa nói | Append nguyên câu trả lời khi `llm.done` | Ghi khi `audio.done`, hoặc theo played offset khi bị huỷ |
| Response mới bị nuốt sau một lần bấm Dừng | Cờ discard bật khi không có response, không có sentinel tắt | Cancel là no-op khi không có response active |
| `429` từ TTS sau vài lần ngắt liên tiếp | Request TTS bị huỷ vẫn giữ slot (cancel best-effort) | Đo T_release; định cỡ slot có dư; theo dõi `/health` |
| Transcript session cũ xuất hiện ở session mới | Callback muộn; worker dùng lại khi transport chưa dọn | Session generation; dọn transport trước khi dùng lại |
| Click khi ngắt | Flush không fade | Fade vài ms |
| Played offset lớn hơn thực tế | Đếm theo giờ nhận chunk, tính cả pre-buffer và underrun | Đếm mẫu đã render (như HF demo) |
| Chunk lượt trước lọt qua guard | Reset `generation_id` về 0 mỗi lượt | Generation đơn điệu cả session |

---

## 17.14 Bài tập thực hành

1. **Chạy `turn_sim.py`.** Đổi `tts_abort` từ 120 lên 500 ms và chạy lại kịch bản C. Có bao nhiêu ms audio cũ được phát? Giải thích vì sao A vẫn bằng 0.
2. **Grace và latency.** Đổi `reopen` từ 800 xuống 400 ms trong kịch bản A. Mẫu audio đầu tiên sớm hơn bao nhiêu? Bây giờ thêm một đoạn ngừng 500 ms giữa hai nửa câu của user: chuyện gì xảy ra?
3. **Gating hai pha.** Mở rộng `Sim`: ở 160 ms phát `client.duck`, ở 416 ms mới cancel. Đo "thời gian tới khi bot nhỏ tiếng" và số lần ngắt nhầm trên cùng kịch bản.
4. **Backchannel.** Viết hàm `classify(transcript, bot_last_clause_is_question) → interrupt | record | ignore` theo bảng §17.7.6. Viết 15 test case tiếng Việt, gồm "dạ", "dạ vâng", "khoan đã", "thế à", "ừ đúng rồi đổi sang thứ bảy".
5. **Guard phía client.** Sửa `guard_prop.py` để `clear` bị mất với xác suất 5 %. Guard floor còn đúng không? Thêm quy tắc "`audio.start(new)` ngầm loại mọi gen < new" và kiểm lại.
6. **Teardown.** Viết test: session đóng khi `asr.final` của lượt cuối đang chạy, rồi một session mới được gán cùng worker. Khẳng định transcript cũ không xuất hiện.
7. **Đo thật (Reproduced nếu bạn làm).** Với HF s2s hoặc gateway của bạn: phát một câu dài, ngắt ở giây thứ 2, ghi timestamp `speech_start`, quyết định, `client.clear` gửi, worklet flush, `/health` của VieNeu về `active=0`. Tính T_silence và T_release.

---

## 17.15 Đáp án các câu hỏi tự kiểm tra

**Q1.** Chỉ **turn owner** (gateway, hoặc turn tracker của framework) được close, reopen, commit. VAD, turn detector, ASR, TTS, client và timer chỉ gửi tín hiệu vào inbox của owner. Lý do: khi hai nơi cùng ghi trạng thái lượt, sẽ có race không lặp lại được: double commit (timeout và final cùng commit), commit sau reopen (timer cũ), hai bộ segmentation lệch nhau, cờ discard bị kẹt. Một owner xử lý tuần tự biến mọi race thành câu hỏi thứ tự trong một hàng đợi, test được bằng cách phát lại sự kiện.

**Q2.** Trình tự: (0) owner quyết định qua các cổng; (1) `generation_id++` nguyên tử; (2) gửi `client.clear(old)` vượt hàng; (3) huỷ LLM; (4) huỷ TTS, xoá câu xếp hàng; (5) flush queue server, giữ sentinel và usage; (6) mở lượt mới từ đầu đoạn nói − pre-roll; (7) `response.done(cancelled)`; (8) cắt history khi nhận played offset. Bảo đảm không còn chunk cũ nhờ ba lớp: server kiểm generation nguyên tử ở điểm publish (không gửi thêm chunk cũ sau bước 1); chunk đang bay có số lượng hữu hạn; client nâng `floor` đơn điệu khi clear và bỏ mọi chunk `gid ≤ floor`. Cancel chỉ là best-effort, nên không thể dựa vào nó; lọc mới là thứ bảo đảm.

**Q3.** Văn bản đã commit là transcript final (hoặc final-pass) của một `(turn_id, revision)` mà owner đã phát `turn.commit`, nên không thể reopen. "Chỉ hành động trên văn bản đã commit" nghĩa là: partial chỉ dùng cho caption; speculative chỉ được tính (LLM, prefetch đọc-only) và giữ kết quả; còn phát audio, ghi history và chạy tool có side effect thì chỉ sau commit, với tool ghi còn cần xác nhận bằng lời và idempotency key.

**Q4.** Điều bắt buộc là việc tăng generation xảy ra trước mọi lần publish tiếp theo và nguyên tử với điểm publish. Nếu nhiều task cùng gửi ra client, tăng generation **trước tiên**. Nếu chỉ có một send loop làm cả chuỗi huỷ (như HF s2s), thứ tự nội bộ là tự do; HF phát terminal `response.done(cancelled)` trước rồi mới tăng generation và flush. `client.clear` nên được gửi càng sớm càng tốt và không xếp sau audio đang chờ.

**Q5.** Gate 150 ms: bot im nhanh (mô phỏng: T_silence 242 ms) nhưng ngắt nhầm khi user "ừ" 250 ms, làm bot im giữa câu và làm bẩn transcript lượt sau. Gate 400 ms: chặn được ho và "ừ", nhưng T_silence 498 ms, trong đó gate chiếm 416 ms. Lấy ưu điểm cả hai bằng gating hai pha: giảm âm lượng ở ~150–200 ms, chỉ huỷ ở ~400 ms sau khi qua speaker lock/quick ASR; nếu không phải ngắt thì khôi phục. Đây là thiết kế chưa đo.

**Q6.** Time-to-silence là từ lúc user bắt đầu nói tới lúc client im hẳn: cái user cảm nhận. Time-to-release là tới lúc backend cuối cùng ngừng tính cho generation cũ: cái hệ thống trả giá. Hai đại lượng tách rời vì cancel phía server là best-effort. T_silence tốt mà T_release dở thì GPU vẫn bận vô ích, slot TTS bị giữ và session khác chậm đi hoặc nhận `429`.

**Q7.** Lưu các mệnh đề đã phát hết nguyên văn, mệnh đề phát dở dưới dạng phần ước lượng kèm `[bị ngắt]` (hoặc "đã bắt đầu nói: …"), bỏ các mệnh đề chưa phát. Trong mô phỏng: "Dạ, em đã kiểm tra lịch hẹn của anh. Lịch hiện tại là … [bị ngắt]". Nếu client không có guard, sau clear nó còn phát 640 ms của mệnh đề 4. User đã nghe "Hoặc anh chọn một…" mà history không ghi, nên ở lượt sau LLM không biết user đã nghe gợi ý chọn ngày khác.

**Q8.** (1) Tăng session generation và `generation_id` để mọi callback cũ thành stale; (2) ngừng nhận input, huỷ timer; (3) huỷ LLM, TTS, ASR, tool async; (4) flush queue, bỏ callback muộn; (5) giải phóng ASR cache, state VAD, các buffer, speaker embedding; (6) dọn transport trước khi worker phục vụ session khác; (7) ghi log metadata, không nội dung; (8) đóng kết nối. Không cần `client.clear` vì client đã đi, nhưng vẫn phải huỷ backend để giải phóng slot.

---

## 17.16 Tóm tắt một trang

- **Tín hiệu khác quyết định.** VAD, Smart Turn, ASR, TTS, client, timer chỉ phát tín hiệu. Một owner duy nhất cho mỗi session quyết định open, soft-end, reopen, commit, cancel, xử lý tuần tự một inbox.
- **Hai máy trạng thái trực giao:** lượt user (`IDLE → LISTENING → SOFT_ENDED → COMMITTED`) và response (`SPECULATIVE → RELEASED → DONE/CANCELLED`). "Bot đang nói" là thuộc tính suy ra.
- **Reopen giữ `turn_id`, tăng `revision`,** phát lại audio tích luỹ cho ASR, huỷ việc chưa commit. Timer mang token `(turn, rev)` và tự vô hiệu khi lệch.
- **Commit là ranh giới cứng:** phát audio, ghi history, tool có side effect chỉ sau commit. Output gate thường quyết định latency hơn tốc độ model.
- **Cancel thì best-effort, lọc thì bắt buộc.** `generation_id` đơn điệu cả session; kiểm ở mọi chỗ dữ liệu đổi chủ, nguyên tử ở điểm publish, và ở client bằng `floor` chỉ tăng.
- **Barge-in là phân loại:** duration gate, ngưỡng theo nhiễu, speaker lock, quick ASR, backchannel với ba kết cục. Gate là thành phần lớn nhất của time-to-silence.
- **Đo hai con số:** time-to-silence (user cảm nhận) và time-to-release (hệ thống trả giá).
- **History = cái user đã nghe,** tính từ số mẫu đã render. HF s2s nhận `conversation.item.truncate` nhưng không cắt history; muốn đúng thì tự làm.
- **Teardown:** stale hoá trước, huỷ, flush, giải phóng, dọn transport, rồi mới đóng.

---

## Hạn chế và phạm vi bao phủ

- Chương không chạy HF s2s, Pipecat hay backend thật nào. Mọi hành vi của HF s2s là **Reported** qua wiki (capture README và tài liệu con ở một revision cố định); default tham số là **Observed** trong argument class đã capture. Implementation source của HF không có trong capture.
- Tham số barge-in (100–200 ms, 300–500 ms, 400 ms, speaker lock 0.5–0.6, quick ASR ≥ 2 từ, ngưỡng thích ứng) đến từ hai AI report thứ cấp, chưa đo, và mâu thuẫn nhau.
- Ba script chỉ kiểm logic điều khiển và phép tính. Độ trễ (TTFT 300 ms, TTFA 150 ms, downlink 40 ms, TTS còn chạy 120 ms sau cancel…) là **giả định** chọn cho dễ đọc. Thời lượng audio tính theo 60 ms/ký tự, không phải TTS thật.
- Danh sách backchannel tiếng Việt, gating hai pha, ba kết cục backchannel, chính sách reconnect và guard floor là thiết kế của chương (**Synthesis**), chưa thử với người dùng thật.
- Mô tả `conversation.item.truncate` của OpenAI và hành vi abort của các LLM server khi client ngắt kết nối là kiến thức nền, không có trong wiki (**Unverified**).
- Việc VieNeu giải phóng slot sớm khi client đóng kết nối chưa được wiki ghi nhận (**Unverified**).

---

## Phụ lục chương

### Script 1: mô phỏng vòng điều khiển (`/tmp/ch17/turn_sim.py`, đã chạy)

Mô phỏng sự kiện rời rạc theo mili giây: turn tracker một owner, speculative reopen, output gate, duration gate, cancel best-effort (LLM còn chạy 50 ms, TTS 120 ms sau lệnh huỷ), guard ở gateway và client, cắt history theo played offset. Kịch bản: user nói hai nửa câu cách nhau 400 ms; trong lúc bot nói có tiếng ho 150 ms, "ừ" 250 ms và một câu ngắt thật dài 1,2 s. Ba cấu hình: A có guard + gate 400 ms, B có guard + gate 150 ms, C không guard + gate 400 ms.

```python
# Chương 17 — mô phỏng sự kiện rời rạc: turn tracker một owner, speculative reopen,
# generation_id, barge-in có duration gate, cancel xuyên tầng, guard downlink, cắt history.
# Python thuần. Mọi độ trễ là THAM SỐ GIẢ ĐỊNH, không đo model/mạng thật.
import heapq, itertools, math

FRAME = 32                      # Silero 512 mẫu @16 kHz
P = dict(min_silence=64, smart_turn=10, reopen=800, incomplete_delay=600, max_wait=2000,
         asr=150, ttft=300, clause_gap=250, tts_ttfa=150, tts_rtf=0.3, chunk=320,
         ms_per_char=60, down=40, up=40, prebuffer=150, fade=10,
         llm_abort=50, tts_abort=120)          # cancel best-effort: còn chạy thêm bao lâu
CLAUSES = ["Dạ, em đã kiểm tra lịch hẹn của anh.",
           "Lịch hiện tại là chín giờ sáng thứ sáu, ngày mười bốn.",
           "Nếu anh muốn đổi, em có thể chuyển sang thứ bảy.",
           "Hoặc anh chọn một ngày khác trong tuần sau cũng được ạ."]


class Sim:
    def __init__(self, segs, gate_ms, guarded=True, verbose=True):
        self.q, self.n = [], itertools.count()
        self.segs, self.gate, self.guarded, self.v = segs, gate_ms, guarded, verbose
        # --- owner (gateway) state ---
        self.state, self.turn, self.rev, self.gen = "IDLE", 0, 0, 0
        self.resp = {}                 # gen -> dict(turn, rev, committed, held, cancel_t, ...)
        self.history, self.log = [], []
        # --- client state ---
        self.c_cur, self.c_floor, self.c_end = 0, 0, 0
        self.sched = []                # [gid, clause, start, dur, cut]
        self.first_play, self.c_cleared = {}, 0
        self.stats = dict(drop_gw=0, drop_client=0, false_barge=0, rejected=0,
                          stale_played=0, barge=[])
        for s in segs:
            self.at(s["start"] + FRAME, "vad_start", s)
            self.at(s["end"] + P["min_silence"], "vad_end", s)

    def at(self, t, kind, *a): heapq.heappush(self.q, (t, next(self.n), kind, a))
    def p(self, t, msg):
        self.log.append((t, msg))
        if self.v: print(f"{t:6d}  {msg}")

    def run(self):
        while self.q:
            t, _, kind, a = heapq.heappop(self.q)
            getattr(self, kind)(t, *a)
        return self

    # ================= OWNER: turn tracker =================
    def vad_start(self, t, s):
        if self.state == "ANSWERING":                     # bot đang nói → ứng viên barge-in
            s["cand"] = True
            need = math.ceil(self.gate / FRAME) * FRAME
            self.at(s["start"] + need + FRAME, "barge_check", s)
            return
        if self.state == "SOFT_ENDED":                    # nói tiếp trong grace → reopen
            old = self.gen
            self.rev += 1
            self.cancel(t, "reopen")
            self.state = "LISTENING"
            self.p(t, f"turn.reopen turn={self.turn} rev={self.rev} (huỷ gen={old}, chưa phát gì)")
            return
        self.turn, self.rev, self.state = self.turn + 1, 1, "LISTENING"
        self.p(t, f"vad.speech_start → turn={self.turn} rev=1 LISTENING  [{s['text']}]")

    def barge_check(self, t, s):
        if s["end"] < t - FRAME:                          # chưa đủ gate thì đã im
            self.stats["rejected"] += 1
            self.p(t, f"barge-in bị chặn bởi gate {self.gate} ms  [{s['text']}, {s['end']-s['start']} ms]")
            s["ignored"] = True
            return
        if s.get("false"): self.stats["false_barge"] += 1
        self.p(t, f"BARGE-IN chấp nhận  [{s['text']}]")
        self.interrupt(t, s)
        self.turn, self.rev, self.state = self.turn + 1, 1, "LISTENING"
        self.p(t, f"  → turn={self.turn} rev=1 LISTENING")

    def vad_end(self, t, s):
        if s.get("ignored") or (s.get("cand") and self.state == "ANSWERING"):
            return
        if self.state != "LISTENING": return
        self.state = "SOFT_ENDED"
        self.p(t, f"vad.speech_end → SOFT_ENDED turn={self.turn} rev={self.rev}")
        self.at(t + P["smart_turn"], "smart_turn", self.turn, self.rev, s["complete"])

    def smart_turn(self, t, turn, rev, complete):
        if (self.state, self.turn, self.rev) != ("SOFT_ENDED", turn, rev): return
        if complete:
            self.p(t, f"smart_turn=complete → speculative ngay, commit sau {P['reopen']} ms nếu im")
            self.start_response(t, turn, rev)
            self.at(t + P["reopen"], "commit_timer", turn, rev)
        else:
            self.p(t, f"smart_turn=incomplete → chờ {P['incomplete_delay']} ms, trần {P['max_wait']} ms")
            self.at(t + P["incomplete_delay"], "late_start", turn, rev)
            self.at(t + P["max_wait"], "commit_timer", turn, rev)

    def late_start(self, t, turn, rev):
        if (self.state, self.turn, self.rev) == ("SOFT_ENDED", turn, rev):
            self.start_response(t, turn, rev)

    def commit_timer(self, t, turn, rev):
        if (self.state, self.turn, self.rev) != ("SOFT_ENDED", turn, rev): return
        self.state = "ANSWERING"
        r = self.resp[self.gen]
        r["committed"] = True
        self.p(t, f"turn.commit turn={turn} rev={rev} → gen={self.gen} được phép phát")
        for i in r.pop("held"): self.tts_enqueue(t, self.gen, i)

    # ================= response / cancel =================
    def start_response(self, t, turn, rev):
        self.gen += 1
        g = self.gen
        self.resp[g] = dict(turn=turn, rev=rev, committed=False, held=[], cancel_t=None,
                            tts_free=0, chunks={}, last_compute=t)
        self.p(t, f"response.create gen={g} (turn={turn} rev={rev}, speculative)")
        for i in range(len(CLAUSES)):
            self.at(t + P["asr"] + P["ttft"] + i * P["clause_gap"], "llm_clause", g, i)

    def cancel(self, t, reason):
        g = self.gen
        if g in self.resp and self.resp[g]["cancel_t"] is None:
            self.resp[g]["cancel_t"] = t
            self.resp[g]["reason"] = reason
        self.gen += 1                                     # mọi thứ của g thành stale

    def interrupt(self, t, s):
        old = self.gen
        self.stats["barge"].append(dict(gid=old, t_user=s["start"], t_decide=t))
        self.cancel(t, "turn_detected")
        self.p(t, f"  gen {old}→{self.gen}; response.cancel({old}); client.clear({old}) gửi đi")
        self.at(t + P["down"], "client_clear", old)

    def alive(self, g, t, lag):
        c = self.resp[g]["cancel_t"]
        return c is None or t <= c + lag

    def llm_clause(self, t, g, i):
        r = self.resp[g]
        if not self.alive(g, t, P["llm_abort"]): return  # LLM đã dừng thật
        r["last_compute"] = max(r["last_compute"], t)
        if self.guarded and g != self.gen:
            self.stats["drop_gw"] += 1
            self.p(t, f"  [gateway] bỏ text.chunk stale gen={g} clause={i}")
            return
        if not r["committed"]: r["held"].append(i); return
        self.tts_enqueue(t, g, i)

    def tts_enqueue(self, t, g, i):
        r = self.resp[g]
        dur = len(CLAUSES[i]) * P["ms_per_char"]
        n = math.ceil(dur / P["chunk"])
        start = max(t, r["tts_free"])
        for k in range(n):
            d = min(P["chunk"], dur - k * P["chunk"])
            ready = start + P["tts_ttfa"] + int(k * P["chunk"] * P["tts_rtf"])
            final = (i == len(CLAUSES) - 1 and k == n - 1)
            self.at(ready, "tts_chunk", g, i, k, d, final)
            r["tts_free"] = ready

    def tts_chunk(self, t, g, i, k, d, final):
        r = self.resp[g]
        if not self.alive(g, t, P["tts_abort"]): return
        r["last_compute"] = max(r["last_compute"], t)
        if self.guarded and g != self.gen:
            self.stats["drop_gw"] += 1
            self.p(t, f"  [gateway] bỏ audio.chunk stale gen={g} c{i}.{k} (TTS chưa dừng kịp)")
            return
        self.at(t + P["down"], "client_chunk", g, i, k, d, final)

    # ================= CLIENT =================
    def client_chunk(self, t, g, i, k, d, final):
        if self.guarded:
            if g <= self.c_floor:
                self.stats["drop_client"] += 1
                self.p(t, f"  [client] bỏ chunk stale gen={g} c{i}.{k} (floor={self.c_floor})")
                return
            if g > self.c_cur: self.c_cur, self.c_end = g, t + P["prebuffer"]
        elif g != self.c_cur:
            self.c_cur, self.c_end = g, max(self.c_end, t + P["prebuffer"])
        start = max(t, self.c_end)
        self.c_end = start + d
        self.first_play.setdefault(g, start)
        if not self.guarded and g <= self.c_cleared:
            self.p(t, f"  [client] PHÁT chunk stale gen={g} c{i}.{k} lúc {start}–{start + d} ms")
        e = [g, i, start, d, None]
        self.sched.append(e)
        if final: self.at(self.c_end, "client_done", g, e)

    def client_clear(self, t, g):
        self.c_floor = max(self.c_floor, g) if self.guarded else self.c_floor
        self.c_cleared = max(self.c_cleared, g)
        played = 0
        for e in self.sched:
            if e[0] != g: continue
            if e[2] >= t: e[4] = 0                     # chưa phát: bỏ
            elif e[2] + e[3] > t: e[4] = t - e[2] + P["fade"]   # đang phát: cắt + fade
        for e in self.sched:
            if e[0] == g:
                played += e[3] if e[4] is None else e[4]
        self.c_end = t
        b = [x for x in self.stats["barge"] if x["gid"] == g][-1]
        b["t_clear"] = t
        self.p(t, f"  [client] clear({g}): flush; đã phát {played} ms của gen={g}")
        self.at(t + P["up"], "played_ack", g, played)

    def client_done(self, t, g, e):
        if e[4] is None and g == self.gen:
            self.at(t + P["up"], "audio_done", g)

    # ================= OWNER: history =================
    def played_ack(self, t, g, played):
        text, acc = [], 0
        for i, c in enumerate(CLAUSES):
            dur = len(c) * P["ms_per_char"]
            if played >= acc + dur: text.append(c)
            elif played > acc:
                frac = (played - acc) / dur
                cut = c[:int(len(c) * frac)].rsplit(" ", 1)[0]
                text.append(cut + " … [bị ngắt]")
                break
            else: break
            acc += dur
        self.history.append(("assistant", g, " ".join(text)))
        self.p(t, f"audio.played(gen={g}, {played} ms) → history: \"{' '.join(text)}\"")

    def audio_done(self, t, g):
        if self.state == "ANSWERING" and g == self.gen:
            self.state = "IDLE"
            self.history.append(("assistant", g, " ".join(CLAUSES)))
            self.p(t, f"audio.done gen={g} → IDLE, history đủ 4 mệnh đề")

    # ================= metrics =================
    def report(self):
        out = []
        for b in self.stats["barge"]:
            g = b["gid"]
            last_audible = b["t_clear"]
            for e in self.sched:
                if e[0] == g and e[4] != 0:                 # chunk thực sự phát (toàn bộ/một phần)
                    end = e[2] + (e[3] if e[4] is None else e[4])
                    if e[2] >= b["t_clear"]:
                        self.stats["stale_played"] += e[3] if e[4] is None else e[4]
                    last_audible = max(last_audible, end)
            r = self.resp[g]
            stop = r["cancel_t"]
            out.append(dict(gid=g, t_silence=last_audible - b["t_user"],
                            decide=b["t_decide"] - b["t_user"],
                            t_release=max(r["last_compute"], stop) - b["t_user"]))
        return out

    def first_audio(self):
        return {g: t for g, t in self.first_play.items()}


def scenario():
    return [
        dict(start=0,    end=1500, text="Cho em hỏi lịch hẹn…", complete=True),
        dict(start=1900, end=3000, text="…của em vào thứ sáu ấy", complete=True),
        dict(start=5000, end=5150, text="(ho)", complete=True, false=True),
        dict(start=6000, end=6250, text="ừ", complete=True, false=True),
        dict(start=7000, end=8200, text="Khoan, đổi sang thứ bảy", complete=True),
    ]


if __name__ == "__main__":
    print("=== A. guarded, gate 400 ms ===")
    a = Sim(scenario(), 400).run()
    print("metrics:", a.report(), {k: v for k, v in a.stats.items() if k != "barge"})
    print("mẫu audio đầu tiên được phát (theo gen):", a.first_audio())
    for runs in (("B. guarded, gate 150 ms", 150, True), ("C. naive (không guard), gate 400 ms", 400, False)):
        print(f"\n=== {runs[0]} ===")
        s = Sim(scenario(), runs[1], guarded=runs[2], verbose=False).run()
        for t, m in s.log:
            if any(x in m for x in ("BARGE", "chặn", "clear(", "history", "commit", "reopen", "PHÁT", "client]")): print(f"{t:6d}  {m}")
        print("metrics:", s.report(), {k: v for k, v in s.stats.items() if k != "barge"})
```

Output (Python 3, 2026-10-07):

```text
=== A. guarded, gate 400 ms ===
    32  vad.speech_start → turn=1 rev=1 LISTENING  [Cho em hỏi lịch hẹn…]
  1564  vad.speech_end → SOFT_ENDED turn=1 rev=1
  1574  smart_turn=complete → speculative ngay, commit sau 800 ms nếu im
  1574  response.create gen=1 (turn=1 rev=1, speculative)
  1932  turn.reopen turn=1 rev=2 (huỷ gen=1, chưa phát gì)
  3064  vad.speech_end → SOFT_ENDED turn=1 rev=2
  3074  smart_turn=complete → speculative ngay, commit sau 800 ms nếu im
  3074  response.create gen=3 (turn=1 rev=2, speculative)
  3874  turn.commit turn=1 rev=2 → gen=3 được phép phát
  5448  barge-in bị chặn bởi gate 400 ms  [(ho), 150 ms]
  6448  barge-in bị chặn bởi gate 400 ms  [ừ, 250 ms]
  7448  BARGE-IN chấp nhận  [Khoan, đổi sang thứ bảy]
  7448    gen 3→4; response.cancel(3); client.clear(3) gửi đi
  7448    → turn=2 rev=1 LISTENING
  7450    [gateway] bỏ audio.chunk stale gen=3 c3.7 (TTS chưa dừng kịp)
  7488    [client] clear(3): flush; đã phát 3284 ms của gen=3
  7528  audio.played(gen=3, 3284 ms) → history: "Dạ, em đã kiểm tra lịch hẹn của anh. Lịch hiện tại là … [bị ngắt]"
  7546    [gateway] bỏ audio.chunk stale gen=3 c3.8 (TTS chưa dừng kịp)
  8264  vad.speech_end → SOFT_ENDED turn=2 rev=1
  8274  smart_turn=complete → speculative ngay, commit sau 800 ms nếu im
  8274  response.create gen=5 (turn=2 rev=1, speculative)
  9074  turn.commit turn=2 rev=1 → gen=5 được phép phát
 21034  audio.done gen=5 → IDLE, history đủ 4 mệnh đề
metrics: [{'gid': 3, 't_silence': 498, 'decide': 448, 't_release': 546}] {'drop_gw': 2, 'drop_client': 0, 'false_barge': 0, 'rejected': 2, 'stale_played': 0}
mẫu audio đầu tiên được phát (theo gen): {3: 4214, 5: 9414}

=== B. guarded, gate 150 ms ===
  1574  smart_turn=complete → speculative ngay, commit sau 800 ms nếu im
  1932  turn.reopen turn=1 rev=2 (huỷ gen=1, chưa phát gì)
  3074  smart_turn=complete → speculative ngay, commit sau 800 ms nếu im
  3874  turn.commit turn=1 rev=2 → gen=3 được phép phát
  5192  barge-in bị chặn bởi gate 150 ms  [(ho), 150 ms]
  6192  BARGE-IN chấp nhận  [ừ]
  6192    gen 3→4; response.cancel(3); client.clear(3) gửi đi
  6232    [client] clear(3): flush; đã phát 2028 ms của gen=3
  6272  audio.played(gen=3, 2028 ms) → history: "Dạ, em đã kiểm tra lịch hẹn của … [bị ngắt]"
  6324  smart_turn=complete → speculative ngay, commit sau 800 ms nếu im
  7032  turn.reopen turn=2 rev=2 (huỷ gen=5, chưa phát gì)
  8274  smart_turn=complete → speculative ngay, commit sau 800 ms nếu im
  9074  turn.commit turn=2 rev=2 → gen=7 được phép phát
 21034  audio.done gen=7 → IDLE, history đủ 4 mệnh đề
metrics: [{'gid': 3, 't_silence': 242, 'decide': 192, 't_release': 244}] {'drop_gw': 1, 'drop_client': 0, 'false_barge': 1, 'rejected': 1, 'stale_played': 0}

=== C. naive (không guard), gate 400 ms ===
  1574  smart_turn=complete → speculative ngay, commit sau 800 ms nếu im
  1932  turn.reopen turn=1 rev=2 (huỷ gen=1, chưa phát gì)
  3074  smart_turn=complete → speculative ngay, commit sau 800 ms nếu im
  3874  turn.commit turn=1 rev=2 → gen=3 được phép phát
  5448  barge-in bị chặn bởi gate 400 ms  [(ho), 150 ms]
  6448  barge-in bị chặn bởi gate 400 ms  [ừ, 250 ms]
  7448  BARGE-IN chấp nhận  [Khoan, đổi sang thứ bảy]
  7448    gen 3→4; response.cancel(3); client.clear(3) gửi đi
  7488    [client] clear(3): flush; đã phát 3284 ms của gen=3
  7490    [client] PHÁT chunk stale gen=3 c3.7 lúc 7490–7810 ms
  7528  audio.played(gen=3, 3284 ms) → history: "Dạ, em đã kiểm tra lịch hẹn của anh. Lịch hiện tại là … [bị ngắt]"
  7586    [client] PHÁT chunk stale gen=3 c3.8 lúc 7810–8130 ms
  8274  smart_turn=complete → speculative ngay, commit sau 800 ms nếu im
  9074  turn.commit turn=2 rev=1 → gen=5 được phép phát
 21034  audio.done gen=5 → IDLE, history đủ 4 mệnh đề
metrics: [{'gid': 3, 't_silence': 1130, 'decide': 448, 't_release': 546}] {'drop_gw': 0, 'drop_client': 0, 'false_barge': 0, 'rejected': 2, 'stale_played': 640}
```

Đọc kết quả: (A) gen 1 speculative bị huỷ khi reopen nên generation nhảy 1 → 3; mẫu audio đầu tiên ở 4 214 ms, tức 1 214 ms sau khi user thôi nói, đúng bằng công thức output gate ở §17.4.3. Ho và "ừ" bị gate chặn; câu ngắt thật được quyết định ở 448 ms, client im ở 498 ms; gateway bỏ 2 chunk TTS rò. (B) gate 150 ms ngắt nhầm ở "ừ", rồi "ừ" và câu sau bị gộp thành revision 2 của cùng một lượt. (C) không guard: 2 chunk rò của mệnh đề 4 được phát 640 ms sau clear, T_silence tăng lên 1 130 ms, và history (3 284 ms) không còn khớp với cái user đã nghe.

### Script 2: property test cho guard phía client (`/tmp/ch17/guard_prop.py`, đã chạy)

```python
# Chương 17 — property test cho guard downlink phía client.
# Server phát audio.start/audio.chunk theo generation; barge-in phát clear(g) rồi chuyển g+1,
# nhưng TTS còn "rò" 0–2 chunk của g sau clear (cancel best-effort). Mạng có thể đảo thứ tự
# (vd WebRTC: audio đi RTP, clear đi data channel). Kiểm bất biến trên 3 loại guard.
import random

def server_stream(rng, n_gen=5):
    msgs, g = [], 1
    while g <= n_gen:
        msgs.append(("start", g, None))
        n = rng.randint(3, 10)
        cut = rng.randint(1, n) if rng.random() < 0.7 else None   # barge-in?
        for s in range(n):
            if cut is not None and s == cut:
                msgs.append(("clear", g, None))
                for s2 in range(s, min(n, s + rng.randint(0, 2))):  # chunk rò sau cancel
                    msgs.append(("chunk", g, s2))
                break
            msgs.append(("chunk", g, s))
        g += 1
    return msgs

def deliver(rng, msgs, p_swap):
    m = msgs[:]
    for i in range(len(m) - 1):
        if rng.random() < p_swap: m[i], m[i + 1] = m[i + 1], m[i]
    return m

class Naive:          # phát mọi chunk; clear chỉ flush hàng đợi hiện tại
    def __init__(s): s.played = []
    def on(s, kind, g, seq):
        if kind == "chunk": s.played.append((g, seq))

class CurOnly:        # chỉ nhận chunk của gen "hiện tại" = gen của audio.start mới nhất
    def __init__(s): s.cur, s.played = 0, []
    def on(s, kind, g, seq):
        if kind == "start": s.cur = g
        elif kind == "chunk" and g == s.cur: s.played.append((g, seq))

class Floor:          # đề xuất của chương: floor đơn điệu + cur đơn điệu + seq tăng chặt
    def __init__(s): s.cur, s.floor, s.last, s.played = 0, 0, -1, []
    def on(s, kind, g, seq):
        if kind == "clear":
            s.floor = max(s.floor, g)
        elif kind == "start":
            if g > s.floor and g > s.cur: s.cur, s.last = g, -1
        elif kind == "chunk":
            if g == s.cur and g > s.floor and seq > s.last:
                s.last = seq; s.played.append((g, seq))

def violations(msgs_in_order, guard):
    cleared, started_max, bad, last = set(), 0, 0, {}
    for kind, g, seq in msgs_in_order:
        n_before = len(guard.played)
        guard.on(kind, g, seq)
        if kind == "clear": cleared.add(g)
        if kind == "start": started_max = max(started_max, g)
        if len(guard.played) > n_before:
            pg, ps = guard.played[-1]
            if pg in cleared or pg < started_max or ps <= last.get(pg, -1):
                bad += 1                      # stale / gen cũ / trùng-lùi
            last[pg] = ps
    return bad

rng = random.Random(17)
for p_swap in (0.0, 0.15):
    tot = {"Naive": 0, "CurOnly": 0, "Floor": 0}
    trials_bad = {k: 0 for k in tot}
    for _ in range(10_000):
        msgs = deliver(rng, server_stream(rng), p_swap)
        for name, cls in (("Naive", Naive), ("CurOnly", CurOnly), ("Floor", Floor)):
            v = violations(msgs, cls())
            tot[name] += v; trials_bad[name] += v > 0
    print(f"p_swap={p_swap}: số chunk vi phạm {tot} | số lần chạy có vi phạm /10000 {trials_bad}")
```

Output:

```text
p_swap=0.0: số chunk vi phạm {'Naive': 26875, 'CurOnly': 26875, 'Floor': 0} | số lần chạy có vi phạm /10000 {'Naive': 9140, 'CurOnly': 9140, 'Floor': 0}
p_swap=0.15: số chunk vi phạm {'Naive': 52988, 'CurOnly': 48075, 'Floor': 0} | số lần chạy có vi phạm /10000 {'Naive': 9967, 'CurOnly': 9931, 'Floor': 0}
```

Đọc kết quả: guard "chỉ so `gid == cur`" vi phạm y hệt naive khi không đảo thứ tự, vì chunk rò sau clear vẫn mang `gid == cur`. Guard floor không vi phạm lần nào trong 20 000 lần chạy. Một vi phạm được tính khi chunk được phát thuộc generation đã bị clear, thuộc generation cũ hơn generation mới nhất đã bắt đầu, hoặc có sequence không tăng.

### Script 3: khung `TurnOwner` + `ClientGuard` (`/tmp/ch17/turn_owner.py`, đã chạy smoke test)

```python
# Chương 17 — khung tham khảo: TurnOwner (một owner, xử lý tuần tự một inbox) + ClientGuard.
# Không asyncio (để Chương 18). Không gọi model thật. Side effect đi qua `out` (danh sách lệnh).
from dataclasses import dataclass, field
from enum import Enum


class Turn(Enum):
    IDLE = "IDLE"; LISTENING = "LISTENING"; SOFT_ENDED = "SOFT_ENDED"; COMMITTED = "COMMITTED"


class Resp(Enum):
    SPECULATIVE = "SPECULATIVE"; RELEASED = "RELEASED"
    DONE = "DONE"; CANCELLED = "CANCELLED"


@dataclass
class Response:
    gid: int
    turn_id: int
    revision: int
    state: Resp = Resp.SPECULATIVE
    held: list = field(default_factory=list)      # text.chunk chờ commit
    chunks: dict = field(default_factory=dict)    # chunk_id -> (text, n_samples)


@dataclass
class TurnOwner:
    reopen_ms: int = 800
    barge_ms: int = 400
    turn: Turn = Turn.IDLE
    turn_id: int = 0
    revision: int = 0
    gid: int = 0                                   # generation hiện hành, chỉ owner được tăng
    resp: Response | None = None
    out: list = field(default_factory=list)        # lệnh gửi cho LLM/TTS/client/history

    # ---------- helpers ----------
    def _new_generation(self) -> int:
        self.gid += 1
        return self.gid

    def _cancel(self, reason: str) -> None:
        r = self.resp
        if r is None or r.state in (Resp.DONE, Resp.CANCELLED):
            return                                  # không có gì để huỷ: no-op, KHÔNG tăng gid
        old, was_released = r.gid, r.state is Resp.RELEASED
        self._new_generation()                      # 1. stale hoá trước mọi thứ khác
        r.state = Resp.CANCELLED
        if was_released:                            # 2. đường nhanh nhất tới im lặng
            self.out.append(("client.clear", old))  #    (speculative chưa phát gì: khỏi clear)
        self.out += [("llm.cancel", old), ("tts.cancel", old), ("queues.flush", old),
                     ("response.done", old, "cancelled", reason)]

    # ---------- signals (VAD / turn detector / timers / backends / client) ----------
    def on_speech_start(self, speech_ms: int, bot_audible: bool) -> None:
        if self.turn is Turn.SOFT_ENDED:            # nói tiếp trong grace → reopen
            self._cancel("reopen")
            self.revision += 1
            self.turn = Turn.LISTENING
            self.out.append(("turn.reopen", self.turn_id, self.revision))
            return
        if self.turn is Turn.COMMITTED and bot_audible:
            if speech_ms < self.barge_ms:           # gate: chưa đủ dài thì chưa quyết
                return
            self._cancel("turn_detected")
        if self.turn is not Turn.LISTENING:
            self.turn_id, self.revision, self.turn = self.turn_id + 1, 1, Turn.LISTENING
            self.out.append(("turn.open", self.turn_id))

    def on_soft_end(self, complete: bool) -> None:
        if self.turn is not Turn.LISTENING:
            return
        self.turn = Turn.SOFT_ENDED
        g = self._new_generation()
        self.resp = Response(g, self.turn_id, self.revision)
        self.out.append(("response.create", g, self.turn_id, self.revision))   # speculative
        wait = self.reopen_ms if complete else 2000
        self.out.append(("timer", wait, ("commit", self.turn_id, self.revision)))

    def on_timer(self, token) -> None:
        kind, turn_id, rev = token
        if kind != "commit" or (self.turn, self.turn_id, self.revision) != (Turn.SOFT_ENDED, turn_id, rev):
            return                                   # timer của revision cũ: tự vô hiệu
        self.turn = Turn.COMMITTED
        self.out.append(("turn.commit", turn_id, rev))
        r = self.resp
        r.state = Resp.RELEASED
        for c in r.held:
            self.out.append(("tts.enqueue", r.gid, *c))
        r.held.clear()

    def on_text_chunk(self, gid: int, chunk_id: int, text: str) -> None:
        r = self.resp
        if r is None or gid != self.gid or r.gid != gid:
            self.out.append(("drop.stale_text", gid, chunk_id)); return
        if r.state is Resp.SPECULATIVE:
            r.held.append((chunk_id, text)); return
        self.out.append(("tts.enqueue", gid, chunk_id, text))

    def on_audio_chunk(self, gid: int, chunk_id: int, seq: int, n: int) -> None:
        if gid != self.gid:                          # kiểm ở điểm publish, ngay trước khi gửi
            self.out.append(("drop.stale_audio", gid, seq)); return
        self.out.append(("client.audio", gid, chunk_id, seq, n))

    def on_audio_done(self, gid: int) -> None:     # client báo đã phát hết generation
        if self.resp and self.resp.gid == gid == self.gid and self.resp.state is Resp.RELEASED:
            self.resp.state, self.turn = Resp.DONE, Turn.IDLE
            self.out.append(("response.done", gid, "completed", None))

    def on_played(self, gid: int, played_samples: int, chunk_table: dict) -> None:
        heard, acc = [], 0
        for cid in sorted(chunk_table):
            text, n = chunk_table[cid]
            if played_samples >= acc + n: heard.append(text)
            elif played_samples > acc: heard.append(f"(đã bắt đầu nói: {text[:max(1, len(text) * (played_samples - acc) // n)]}…) [bị ngắt]"); break
            else: break
            acc += n
        self.out.append(("history.assistant", gid, " ".join(heard)))


@dataclass
class ClientGuard:
    cur: int = 0          # generation đang phát (chỉ tăng)
    floor: int = 0        # mọi gid <= floor đã bị clear (chỉ tăng)
    last_seq: int = -1

    def on_clear(self, gid: int) -> bool:
        self.floor = max(self.floor, gid)
        return self.cur <= self.floor               # True → flush worklet (kèm fade ngắn)

    def on_audio_start(self, gid: int) -> bool:
        if gid <= self.floor or gid <= self.cur: return False
        self.cur, self.last_seq = gid, -1
        return True

    def on_chunk(self, gid: int, seq: int) -> bool:
        if gid != self.cur or gid <= self.floor or seq <= self.last_seq: return False
        self.last_seq = seq
        return True


if __name__ == "__main__":
    o = TurnOwner()
    o.on_speech_start(32, False); o.on_soft_end(True)          # rev1 speculative gen1
    o.on_text_chunk(1, 0, "Dạ, em kiểm tra rồi ạ.")             # bị giữ
    o.on_speech_start(32, False)                                # reopen → cancel gen1, gid=2
    o.on_text_chunk(1, 1, "câu muộn của gen 1")                 # stale
    o.on_timer(("commit", 1, 1))                                # timer cũ: bỏ qua
    o.on_soft_end(True)                                         # rev2 → gen3
    o.on_text_chunk(3, 0, "Dạ, lịch của anh là thứ sáu.")
    o.on_timer(("commit", 1, 2))                                # commit → thả chunk 0
    o.on_audio_chunk(3, 0, 0, 7680)
    o.on_speech_start(200, True)                                # dưới gate: không ngắt
    o.on_speech_start(416, True)                                # barge-in → gen4
    o.on_audio_chunk(3, 0, 1, 7680)                             # TTS rò: bỏ ở gateway
    o.on_played(3, 9000, {0: ("Dạ, lịch của anh là thứ sáu.", 7680), 1: ("Anh muốn đổi không ạ?", 7680)})
    o._cancel("client_cancelled")                               # không có response active: no-op
    for x in o.out: print(x)
    print("state:", o.turn, "turn_id", o.turn_id, "rev", o.revision, "gid", o.gid)

    c = ClientGuard()
    seq = [("start", 3), ("chunk", 3, 0), ("clear", 3), ("chunk", 3, 1),
           ("start", 3), ("start", 5), ("chunk", 5, 0), ("chunk", 5, 0), ("chunk", 5, 1)]
    for m in seq:
        r = c.on_audio_start(m[1]) if m[0] == "start" else c.on_clear(m[1]) if m[0] == "clear" else c.on_chunk(m[1], m[2])
        print(m, "→", r)
```

Output:

```text
('turn.open', 1)
('response.create', 1, 1, 1)
('timer', 800, ('commit', 1, 1))
('llm.cancel', 1)
('tts.cancel', 1)
('queues.flush', 1)
('response.done', 1, 'cancelled', 'reopen')
('turn.reopen', 1, 2)
('drop.stale_text', 1, 1)
('response.create', 3, 1, 2)
('timer', 800, ('commit', 1, 2))
('turn.commit', 1, 2)
('tts.enqueue', 3, 0, 'Dạ, lịch của anh là thứ sáu.')
('client.audio', 3, 0, 0, 7680)
('client.clear', 3)
('llm.cancel', 3)
('tts.cancel', 3)
('queues.flush', 3)
('response.done', 3, 'cancelled', 'turn_detected')
('turn.open', 2)
('drop.stale_audio', 3, 1)
('history.assistant', 3, 'Dạ, lịch của anh là thứ sáu. (đã bắt đầu nói: Anh…) [bị ngắt]')
state: Turn.LISTENING turn_id 2 rev 1 gid 4
('start', 3) → True
('chunk', 3, 0) → True
('clear', 3) → True
('chunk', 3, 1) → False
('start', 3) → False
('start', 5) → True
('chunk', 5, 0) → True
('chunk', 5, 0) → False
('chunk', 5, 1) → True
```

Đọc kết quả: reopen huỷ gen 1 mà **không** gửi `client.clear` (chưa phát gì); text muộn của gen 1 bị bỏ; timer commit của rev 1 tự vô hiệu; commit rev 2 thả chunk đang giữ; speech 200 ms khi bot nói không ngắt, 416 ms thì ngắt; chunk TTS rò bị bỏ ở gateway; history ghi mệnh đề đầu và phần dở của mệnh đề sau; `response.cancel` khi không còn response active là no-op (không có dòng output nào). Phía client: chunk sau clear, `audio.start` lặp lại của gen cũ và chunk trùng sequence đều bị từ chối.

### Liên kết sang chương khác

- Chương 1 (vật lý âm thanh): vì sao cắt ngang sóng tạo tiếng click, và cần fade khi flush.
- Chương 5 (ngữ âm, hội thoại tiếng Việt): backchannel, từ đệm, lệnh một âm tiết; "2 từ" là 2 âm tiết.
- Chương 6 (capture, playback): AudioWorklet queue, pre-buffer, đếm mẫu đã render cho played offset.
- Chương 7 (front-end âm học): AEC là điều kiện để mic mở khi bot nói.
- Chương 8 (transport): head-of-line blocking trên WebSocket, kênh `oai-events` của WebRTC, huỷ HTTP stream.
- Chương 10 (VAD, turn): hai triết lý commit, `min_speech_continuation_ms`, VAD trên kênh có echo.
- Chương 11 (ASR): partial, stable prefix, revision; ASR phải huỷ được khi reopen.
- Chương 12 (LLM): history phản ánh cái đã nghe, tag `[bị ngắt]` trong prompt, speculative generation, tool và idempotency.
- Chương 14 (speaker): speaker lock cho barge-in và giới hạn của nó.
- Chương 16 (dataflow): sáu định danh, ring buffer, pre-roll, bảng `chunk_id → khoảng mẫu`, state theo session.
- Chương 18 (async): hiện thực inbox, task huỷ được, `asyncio.to_thread`, bounded queue và pacing downlink.
- Chương 19 (cầu text → speech): chunker sinh `chunk_id` theo mệnh đề, đơn vị để cắt history.
- Chương 20 (latency): output gate, T_silence, T_release, join log theo `(turn, rev, gen)`.
- Chương 21 (đánh giá): đo false-interruption rate, barge-in rate dưới nhiễu nền.

[^design]: [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) — §3 nguyên tắc 2 (gateway hoặc turn tracker là owner duy nhất của close/reopen/commit; VAD, ASR, TTS chỉ cung cấp tín hiệu) và 5 (partial cho caption và speculative; side effect chỉ sau `turn.commit`); §5.3 (FPR Smart Turn v3.2 tiếng Việt 8,86–9,56 %, đọc thô "1/10"; turn tracker HF `LISTENING → SOFT_ENDED → ANSWERING → CLOSED`, speculative reopen 800 ms, incomplete 600 ms, max wait 2 s; không trộn default HF với bảng tham số report); §5.7 (reference server gate 400 ms, `{"type":"clear"}`, cancellation và metrics tự làm); §5.8 (không để hai owner cùng quyết định segmentation); §6.1 (huỷ speculation khi revision đổi); §7.2 (event schema và quy tắc; final-pass thay một revision, commit một lần; giải phóng khi session đóng); §7.3 (trình tự barge-in **Reported**; bảng gating; speaker lock không phải xác thực; không mặc định "ừ/vâng/ok" là backchannel; đo stop-audible và time-to-release; SDK không huỷ được là deployment gate; played offset khi không có alignment); §7.4 (pseudo-code vòng điều khiển); §8.1 (công thức output gate); §5.7 và §9.5 (log content-free mặc định, `--log_transcripts` opt-in).
[^wikidesign]: [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md) — "Hợp đồng điều khiển chi tiết" §2 (bảng policy: adaptive threshold, barge-in clean 150–200 ms, noisy 0.7 và 300–500 ms, reference 400 ms; một owner quyết định turn close/reopen/commit), §3 (schema đề xuất), §4 (barge-in, cancellation, history); "Latency, monitoring và release gates" (gate 5 contract tests: sequence/revision đơn điệu, cancel giữa chunk, disconnect/reconnect, không stale audio, không duplicate final). Trang `status: draft`.
[^barge]: [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md) — "Interruption procedure" (mic mở, VAD chấm điểm khi bot nói, 100–200 ms, `generation_id` trên mọi chunk, client bỏ chunk cũ, propagate end to end; sketch LLM thoát vòng lặp và không append history, TTS bỏ câu cũ và phát `audio_cancel`; sketch thiếu duration gate và không xoá TTS queue, **Observed**); "Echo-avoidance tiers"; "Noise-robust gating (Claude report)" (threshold 0.7 và ≥ 300–500 ms, quick ASR ≥ 2 từ, ngưỡng thích ứng, speaker lock ECAPA/CAM++ 0.5–0.6, backchannel "ừ/vâng/ok" không ngắt, trình tự huỷ và `[bị ngắt]`, reference server 400 ms, denoise chỉ nhánh VAD/barge-in); "Contradictions" (100–200 ms so với 300–500 ms). Cả hai nguồn là câu trả lời do LLM sinh, chưa đo; trang `status: draft`.
[^hf]: [HF Speech-to-Speech Pipeline](../wiki/speech-to-speech-pipeline.md) — "Endpointing and turn-taking": cờ VAD và reopen (`--min_speech_continuation_ms`, `--speculative_reopen_ms`, `--unanswered_reopen_ms`); Smart Turn complete chạy STT/LLM ngay với grace 800 ms, incomplete chờ 600 ms, output gate 2 s; reopen thành revision mới, phát lại audio tích luỹ, bỏ việc chưa commit; tracker sở hữu thứ tự trạng thái; trần unanswered reopen theo thời gian audio đã stream, processing/output hold theo wall clock; việc chưa commit cũ bị bỏ nhưng output đã chấp nhận có thể chạy nốt; response thuộc generation input, ghi trên item và tool call, không mượn danh tính của speech đang ghi; server giữ `speech_stopped` và final transcript khi lượt còn reopen được, khi commit client nhận đúng một stop, một commitment, một item, một final.
[^engine]: [Speech-to-Speech Realtime Engine](../wiki/speech-to-speech-realtime-engine.md) — "Architecture and flow" (`LMOutputProcessor` một queue để phần sau và terminal không vượt; send loop); "Protocol event surface" (sự kiện client/server; `conversation.item.truncate` là no-op; lỗi `conversation_already_has_active_response`); terminal statuses (`incomplete`, `failed`, `cancelled` với `turn_detected`/`client_cancelled`; rollback history với incomplete/failed); "Transcription semantics" (delta append-only chỉ phần đã xác nhận, không có sự kiện rút lại, `completed` là authoritative, snapshot opt-in; transcript `.done` sau `output_audio.done` và trước `response.done`); "Tool calling" (huỷ kết quả chưa gửi khi response bị huỷ; huỷ handler async khi disconnect); "Interruption handling" (`CancelScope` với bộ đếm generation và cờ discarding, `is_stale(gen)` mỗi token, `response_done(gen)` chỉ xoá cờ khi khớp generation, output mang `cancel_generation`, giữ usage, terminal chỉ lifecycle cho response speculative bị thay; thứ tự khi `speech_started`; cờ `interrupt_response`; `response.cancel` không gọi `cancel()` khi không có response active); "WebRTC transport" (send loop là consumer duy nhất; `output_audio_buffer.clear` chỉ ở WebRTC).
[^cli]: [Speech-to-Speech CLI and Defaults](../wiki/speech-to-speech-cli-and-defaults.md) — VAD arguments: `min_speech_ms=384`, `min_speech_continuation_ms=192` (lượt mới và barge-in luôn cần `min_speech_ms`), `min_silence_ms=64`; reopen: `speculative_reopen_ms=800`, `unanswered_reopen_ms=7000` (trần an toàn cho lượt soft-ended speculative chưa trả lời). **Observed** trong argument class đã capture.
[^backends]: [Speech-to-Speech OpenAI-Compatible STT/TTS Backends](../wiki/speech-to-speech-openai-compatible-backends.md) — "STT turn and session lifecycle" (huỷ inference phía server là best-effort, cần lọc kết quả stale; final huỷ progressive đang chạy; revision mới vô hiệu hoá việc cũ, kiểm relevance trước và trong khi chạy; session end huỷ việc đang chạy và chờ; session generation kiểm nguyên tử khi publish; cancellation hoạt động suốt kết nối/upload/đọc, dọn transport trước khi dùng lại worker); "OpenAI-compatible TTS" (huỷ TTS chỉ best-effort, `/v1/audio/speech` không có thao tác huỷ phía server).
[^demo]: [Speech-to-Speech Browser Demo](../wiki/speech-to-speech-browser-demo.md) — "Audio pipeline notes" (playback fade 32 frame; ngắt/huỷ/lỗi/disconnect bỏ audio đang chờ; worklet báo số PCM đã render, không tính độ trễ khởi động và underrun; client gửi `conversation.item.truncate` theo số đó, thay đồng hồ lúc nhận sự kiện của SDK; server cục bộ nhận truncate mà không đổi history).
[^vieneuapi]: [VieNeu-TTS OpenAI-Compatible Speech API](../wiki/vieneu-tts-openai-speech-api.md) — lỗi `429` khi hết slot (kèm `Retry-After`); `/health` (`active`, `waiting`, `max_streams`); `VIENEU_MAX_STREAMS`, `VIENEU_QUEUE`, `VIENEU_QUEUE_TIMEOUT`. Việc slot giải phóng khi request gặp EOS hoặc frame cap lấy từ trang liên kết [VieNeu-TTS Streaming Runtime](../wiki/vieneu-tts-streaming-runtime.md) ("Continuous batching").
[^frameworks]: [Voice Agent Frameworks](../wiki/voice-agent-frameworks.md) — Pipecat cung cấp interruption handling, per-service TTFB metrics và WebRTC transport khi ghép `SileroVADAnalyzer` + `LocalSmartTurnAnalyzerV3` + `WhisperSTTService` + `OpenAILLMService` + `TTSService` tuỳ biến (**Reported** qua AI report).
