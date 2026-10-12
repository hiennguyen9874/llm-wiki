# Chương 15. Kiến trúc: cascade, end-to-end full-duplex và lai 🟡

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần V (Ghép pipeline).
> **Chương trước:** [Chương 14. Speaker: embedding, speaker lock, diarization](chuong-14-speaker-embedding-speaker-lock-diarization.md). **Chương tiếp theo:** Chương 16. Dataflow end-to-end và audio contract.
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §2 (cascade hay E2E), §3 nguyên tắc 1 (tách năm tầng), và gián tiếp §10 (gate dùng để đánh giá lại quyết định).
> **Cơ sở:** khái niệm simplex/half-duplex/full-duplex, neural codec, RVQ, kiến trúc Moshi (Mimi, Temporal/Depth Transformer, inner monologue), kiến trúc Thinker–Talker của họ Qwen-Omni và đặc điểm ngữ âm tiếng Việt là **kiến thức nền chung**, không phải claim lấy từ nguồn wiki. Thông tin về từng model và công cụ lấy từ wiki và gắn nhãn bằng chứng: [PersonaPlex 7B](../wiki/personaplex-7b-v1.md), [NemotronLabs VoiceChat 11B](../wiki/nvidia-nemotronlabs-voicechat-11b.md), [Ultravox](../wiki/ultravox.md), [Step-Audio-R1.1](../wiki/step-audio-r1-1.md), [HF Speech-to-Speech](../wiki/speech-to-speech-pipeline.md), [vLLM-Omni](../wiki/vllm-omni.md), [NeMo-Speech.cpp](../wiki/nemo-speech-cpp.md), [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md), [Community STT-LLM-TTS Wiring](../wiki/community-stt-llm-tts-pipeline.md), [So sánh công cụ triển khai speech](../wiki/speech-deployment-tools-comparison.md). Mọi số liệu model là **Reported** (wiki chưa chạy lại model nào). Phép tính ở §15.2.4 và §15.3.7 chạy bằng Python thuần (**Reproduced**, script ở "Phụ lục chương") trên giả định ghi rõ. Đây là mô hình số học, không phải đo model thật. Suy luận của tác giả là **Synthesis**.

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Vẽ được ba họ kiến trúc speech-to-speech (cascade, end-to-end full-duplex, lai) và chỉ ra **ranh giới thông tin** giữa các khối trong từng họ: text, embedding liên tục, hay token audio.
2. Giải thích vì sao latency của cascade "cộng dồn", và các kỹ thuật streaming, overlap, speculative kéo nó xuống tới đâu.
3. Giải thích cơ chế **dual-stream** của model full-duplex kiểu Moshi, và vì sao trong họ này turn-taking là một **hành vi học được** chứ không phải một state machine viết tay.
4. Với mỗi biến thể lai (audio-LLM, omni turn-based, omni kèm TTS riêng), nói được nó bỏ tầng nào, giữ tầng nào, mất gì.
5. Áp dụng **năm tầng tách biệt** (model, runtime, API server, streaming policy, orchestration) để đọc đúng một tuyên bố kiểu "hỗ trợ realtime full-duplex".
6. Lập luận được vì sao thiết kế hiện tại chọn cascade cho tiếng Việt, và liệt kê các **tín hiệu kích hoạt** việc xem lại quyết định đó.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. Full-duplex speech-to-speech (Moshi-style) xử lý turn-taking khác cascade thế nào?
- Q2. Omni/audio-LLM ("direct audio input") bỏ được tầng nào, và đổi lại mất gì?
- Q3. Vì sao cascade tiếng Việt mất ít thông tin về **thanh điệu** nhưng vẫn mất nhiều thông tin về **ngữ điệu và cảm xúc**?
- Q4. Một model full-duplex báo "latency 170 ms". Vì sao không so con số này trực tiếp với ngân sách "0.7–1.2 s voice-to-voice" của cascade?
- Q5. "vLLM-Omni hỗ trợ full-duplex realtime" có nghĩa là PersonaPlex chạy full-duplex được trên vLLM-Omni không? Dùng năm tầng để trả lời.
- Q6. Nêu ba tín hiệu cụ thể khiến bạn nên mở lại quyết định "cascade cho tiếng Việt".

---

## 15.1 Bức tranh: ba họ kiến trúc

```text
(A) CASCADE (turn-based, ranh giới là TEXT)
 mic ─► VAD ─► turn detector ─► ASR ──text──► LLM ──text──► TTS ─► loa
         └──────── gateway/turn tracker sở hữu quyết định lượt ────────┘

(B) END-TO-END FULL-DUPLEX (frame-synchronous, ranh giới là TOKEN AUDIO bên trong 1 model)
 mic ─► codec encoder ─┐                                   ┌─► codec decoder ─► loa
                       ▼   mỗi 80 ms: đọc 1 frame user,    │
                  [ một model duy nhất ]  sinh 1 frame bot ─┘   (bot có thể "nói im lặng")

(C) LAI (một phần tầng gộp vào model, phần còn lại vẫn cascade)
 C1 audio-LLM:   mic ─► VAD/turn ─► [audio encoder + projector + LLM] ──text──► TTS ─► loa
 C2 omni turn:   mic ─► VAD/turn ─► [omni model: nghe + nghĩ + nói] ─────────────────► loa
 C3 omni + TTS:  mic ─► VAD/turn ─► [omni model, chỉ lấy text out] ──text──► TTS ngôn ngữ đích ─► loa
```

Ba câu hỏi cho phép phân loại nhanh mọi hệ thống (**Synthesis**):

| Câu hỏi | Cascade | E2E full-duplex | Lai |
|---|---|---|---|
| Giữa "nghe" và "nói" có ranh giới text không? | Có, bắt buộc | Không (text chỉ là token phụ bên trong) | C1/C3 có ở đầu ra; C2 không |
| Ai quyết định lúc nào bot nói? | Code (gateway, turn tracker) | Trọng số model | Code (vẫn cần VAD/turn) |
| Nghe và nói có đồng thời không? | Không theo nghĩa hiểu nội dung; chỉ nghe để phát hiện ngắt lời | Có, liên tục | Thường không |

Hai thuật ngữ từ viễn thông cần phân biệt (kiến thức nền):

- **Half-duplex:** tại một thời điểm chỉ một bên truyền, như bộ đàm. Cascade cơ bản (MVP "user nói xong, bot trả lời, không ngắt được") là half-duplex.
- **Full-duplex:** hai bên truyền đồng thời, như điện thoại. Cascade có **barge-in** chỉ là "full-duplex một phần": hệ vẫn nghe trong lúc bot nói, nhưng chỉ dùng tín hiệu đó để *dừng* bot, không dùng để *hiểu và phản hồi* trong lúc đang nói. Blueprint trong wiki đề xuất đúng lộ trình này: bắt đầu half-duplex, sau đó mới thêm streaming TTS, `generation_id`, AEC và barge-in (**Reported**).[^blueprint]

---

## 15.2 Cascade: VAD → turn → ASR → LLM → TTS

### 15.2.1 Giải phẫu

| Khối | Đầu vào | Đầu ra | Chương chi tiết |
|---|---|---|---|
| VAD | frame PCM 16 kHz (vd. 512 mẫu = 32 ms) | xác suất speech, sự kiện start/stop | Ch.10 |
| Turn detector | audio lượt hiện tại (+ đôi khi transcript) | "đã hết lượt?" | Ch.10, Ch.17 |
| ASR | audio lượt hoặc chunk streaming | partial/final text, timestamp, confidence | Ch.11 |
| LLM | history + transcript đã commit | stream text, tool call | Ch.12 |
| Cầu text→speech | text stream | mệnh đề đã chuẩn hoá | Ch.19 |
| TTS | mệnh đề | chunk PCM | Ch.13 |
| Gateway/orchestrator | mọi sự kiện trên | quyết định commit, cancel, phát | Ch.16–18 |

Điểm cốt lõi: **mọi giao tiếp giữa "tai" và "miệng" đi qua một nút cổ chai text.** Đây vừa là ưu điểm lớn nhất vừa là nhược điểm lớn nhất của cascade.

### 15.2.2 Ưu điểm

1. **Kiểm soát và quan sát được.** Text đọc được, log được (sau khi redact), diff được, test hồi quy được. Lỗi khoanh vùng được theo tầng: nghe sai (WER), hiểu sai (LLM), hay đọc sai (TTS/normalizer).
2. **RAG, tool, guardrail đều là bài toán text.** Mọi hạ tầng LLM text (prompt, function calling, retrieval, content filter) dùng lại nguyên vẹn. Các AI report trong wiki nêu đúng điểm này: omni/E2E "khó kiểm soát, khó gắn RAG/tool, khó thay từng thành phần" (**Reported**).[^stack][^design]
3. **Thay từng phần.** Đổi ASR từ faster-whisper sang Nemotron streaming, hay đổi TTS, mà không phải đụng LLM. Sáu profile A–F trong tài liệu thiết kế chỉ tồn tại được nhờ tính chất này (**Synthesis**).[^design]
4. **Ghép được ngôn ngữ.** Chỉ cần mỗi tầng hỗ trợ tiếng Việt *riêng rẽ*: ASR `vi`, LLM đa ngữ, TTS `vi`. Pipeline HF s2s nói rõ độ phủ ngôn ngữ do STT và TTS được chọn quyết định, không phải do pipeline (**Reported**).[^hfs2s]
5. **Phần cứng linh hoạt.** Từ CPU/edge (sherpa-onnx + llama.cpp + TTS ONNX) tới multi-GPU, mỗi tầng một pool riêng, scale độc lập.[^stack]
6. **License tách rời.** Mỗi tầng một license, thay được tầng có license xấu. Cái giá là phải rà license từng tầng (Ch.23).

### 15.2.3 Nhược điểm

1. **Latency cộng dồn** trên critical path (xem §15.2.4).
2. **Mất thông tin cận ngôn ngữ (paralinguistic)** ở nút cổ chai text (xem §15.2.5).
3. **Lỗi lan truyền.** ASR nghe "không" thành "có" thì LLM trả lời sai một cách tự tin. LLM không có cơ hội "nghe lại". Vì vậy thiết kế cần validity gate, hallucination filter, và prompt dặn LLM hỏi lại khi không chắc (Ch.11, Ch.12).
4. **Turn-taking là kỹ thuật thủ công.** Endpointing, reopen, barge-in, chống ngắt nhầm do echo hay TV đều do code và ngưỡng quyết định. Chương 10 và 17 tồn tại chính vì điều này.
5. **Không có backchannel và overlap tự nhiên.** Cascade khó nói "ừ, ừ" trong khi user đang kể, vì mọi đầu ra đều phải đi qua một lượt LLM đầy đủ.
6. **TTS không biết ngữ cảnh hội thoại.** TTS chỉ thấy text của một mệnh đề, nên prosody có thể đúng ở mức câu nhưng lạc ở mức hội thoại: đọc câu xin lỗi bằng giọng vui vẻ, đọc câu hỏi lại như câu khẳng định.

### 15.2.4 Latency cộng dồn, và cách cascade "giả" song song

Ngân sách tham khảo từ AI report stack tiếng Việt (ước lượng kỹ thuật, **Reported**, chưa đo):[^stack]

| Tầng | Ngân sách |
|---|---|
| Network + jitter buffer | 30–80 ms |
| VAD silence | 200–300 ms |
| Smart Turn | 10–65 ms |
| ASR turn-final (GPU, câu 3–5 s) | 100–300 ms |
| LLM TTFT + chunk đầu | 150–350 ms |
| TTS TTFA | 64–300 ms |
| **Report ghi voice-to-voice** | **~0.7–1.2 s** |

Kết quả phép tính trong phụ lục (**Reproduced**, mô hình số học):

| Kịch bản | Critical path |
|---|---|
| 1a. Cộng thẳng sáu dòng ngân sách | 554–1395 ms |
| 1b. Không stream LLM/TTS (chờ 40 token ở 50 tok/s, rồi TTS cả 3 s audio với RTF 0.3) | 2040–2445 ms |
| 1c. ASR streaming, chunk 160 ms (endpoint→final ≈ ½–1 chunk) | 534–1255 ms |
| 1c'. ASR streaming, chunk 320 ms | 614–1415 ms |
| 1d. Preemptive ASR+LLM ngay khi VAD báo im lặng, đoán đúng (bỏ Smart Turn khỏi path) | 544–1330 ms |

Đọc kết quả (**Synthesis**):

- **Streaming ở hạ nguồn (LLM → chunker → TTS) là đòn bẩy lớn nhất.** Kịch bản 1b cho thấy nếu chờ LLM sinh xong rồi mới TTS cả câu, latency tăng gần gấp đôi. Vì vậy blueprint nhấn mạnh "không bao giờ chờ LLM trả lời xong rồi mới TTS".[^blueprint]
- **ASR streaming không tự động nhanh hơn với câu ngắn.** Ở đầu thấp, ASR turn-final trên GPU (100 ms) đã ngang một chunk streaming. Lợi ích thật của ASR streaming nằm ở câu dài (thời gian turn-final tăng theo độ dài) và ở partial cho caption/speculative.
- **Sàn của cascade bị khoá bởi khoảng im lặng dùng để chốt lượt** (200–300 ms VAD + turn detector). Chỉ một model *đoán trước* được lúc user sắp dừng mới hạ được sàn này. Đây chính là chỗ full-duplex có lợi thế cấu trúc.
- Các tầng chạy chồng thời gian, nên **không được cộng P95 của từng tầng** để ra P95 tổng (nguyên tắc 6 trong thiết kế; Ch.20).[^design]

```text
Cascade tuần tự (không stream)        Cascade có overlap (stream + chunk)
user ███████|                         user ███████|
VAD         ▒▒▒|                      VAD         ▒▒▒|
ASR            ████|                  ASR            ██|
LLM                ██████████|        LLM              ██▓▓▓▓▓▓▓▓  (▓ = sinh tiếp khi TTS đã phát)
TTS                          ██████|  TTS                ██▓▓▓▓▓▓
bot                                ▶  bot                  ▶ (nghe thấy sớm hơn nhiều)
```

### 15.2.5 Thông tin bị mất ở nút cổ chai text

| Thông tin trong audio | Còn sau ASR? | Hệ quả nếu mất | Cách vá trong cascade |
|---|---|---|---|
| Từ vựng và **thanh điệu** tiếng Việt | **Có**, vì dấu thanh nằm trong chính tả (ma/má/mà/mả/mã/mạ là sáu từ khác nhau) | Chỉ mất khi ASR nhận sai | WER/CER có NFC (Ch.5, Ch.11) |
| Ngữ điệu câu (lên giọng hỏi, xuống giọng khẳng định) | Một phần, qua dấu câu nếu ASR có PnC | Câu hỏi không có tiểu từ nghi vấn có thể bị hiểu thành câu kể | ASR có PnC; prompt LLM hỏi lại khi mơ hồ |
| Cảm xúc (bực, gấp, vui), mỉa mai | Không | Bot trả lời lạc tông | Thêm bộ phân loại cảm xúc (SER) chạy song song, đưa tag vào prompt; TTS có `instruct` |
| Nhấn mạnh ("tôi nói **thứ Ba** cơ mà") | Không | Mất trọng tâm sửa sai | Khó vá; có thể dùng ASR có word timestamp + năng lượng |
| Do dự, ậm ừ, tự sửa | Thường bị ASR lọc | Không biết user chưa chắc | Giữ disfluency trong transcript nếu ASR cho phép |
| Ai nói, giọng gì, môi trường | Không | Không biết nhiều người, không biết bối cảnh ồn | Speaker lock/diarization (Ch.14), metadata SNR |
| Thời điểm nói (pause, nhịp) | Chỉ khi có timestamp | Không biết user đang ngập ngừng hay đã xong | Turn detector đọc audio, không đọc text |

Vì sao tiếng Việt khác tiếng Anh ở điểm này (**kiến thức nền + Synthesis**): thanh điệu tiếng Việt là **thanh điệu từ vựng** (lexical tone), được mã hoá trong chữ viết. Khi ASR đúng, cascade giữ trọn thông tin thanh điệu. Câu hỏi tiếng Việt cũng thường được đánh dấu bằng từ ("không", "chưa", "à", "hả", "nhỉ", "đúng không") chứ không chỉ bằng ngữ điệu, nên mất ngữ điệu ít gây hại cho việc nhận diện câu hỏi hơn so với câu hỏi lên giọng kiểu tiếng Anh. Nhưng cảm xúc, nhấn mạnh và thái độ thì cascade mất hoàn toàn, như mọi ngôn ngữ khác.

---

## 15.3 End-to-end full-duplex

### 15.3.1 Từ "lượt" sang "thời gian"

Cascade nghĩ theo **lượt** (turn): chờ lượt user kết thúc, rồi tạo lượt bot. Model full-duplex nghĩ theo **thời gian**: cứ mỗi bước cố định (ví dụ 80 ms), model đọc một frame audio của user và sinh một frame audio của chính nó. Trong frame đó, "nói" có thể là im lặng, một tiếng "ừ", hay một âm tiết của câu trả lời. **Không có khái niệm "end of turn" tường minh**; thời điểm bot bắt đầu hay ngừng nói chỉ là một chuỗi quyết định token theo thời gian (**kiến thức nền**).

### 15.3.2 Kiến trúc kiểu Moshi

PersonaPlex 7B được phát triển từ Moshi (trọng số Moshiko). Card mô tả đường đi: Mimi speech encoder (ConvNet + Transformer) → Moshi Temporal Transformer + Depth Transformer → Mimi speech decoder (Transformer + ConvNet). Audio vào/ra đều 24 kHz. Model dự đoán tự hồi quy **cả token text và token audio**. Audio user được mã hoá tăng dần và đưa vào model **trong khi** model đang sinh tiếng nói (**Reported**).[^pp]

Các thành phần, theo kiến thức nền về Moshi (paper Kyutai 2024, mà card PersonaPlex trích dẫn):

```text
Mimi codec: waveform 24 kHz ──► 12.5 frame/s (80 ms/frame), mỗi frame = 8 token RVQ
            codebook 1 ≈ "semantic" (chưng cất từ mô hình SSL), codebook 2–8 ≈ "acoustic"

Tại bước thời gian t (mỗi 80 ms):
  ┌─────────────── Temporal Transformer (~7B) ───────────────┐
  │ ngữ cảnh: mọi bước < t của 3 luồng:                       │
  │   text bot (inner monologue) | audio bot | audio user     │
  └──────────────────────┬────────────────────────────────────┘
                         ▼  vector trạng thái z_t
  ┌─────────── Depth Transformer (nhỏ) ───────────┐
  │ sinh lần lượt: text_t → cb1_t → cb2_t … cb8_t   │  (chỉ cho luồng bot)
  └────────────────────────────────────────────────┘
  Luồng user ở bước t không sinh, chỉ được *quan sát* (lấy từ encoder).
```

Ba ý tưởng cần nhớ (kiến thức nền):

1. **Dual-stream (đa luồng):** audio của user và audio của bot là hai luồng token song song, cùng trục thời gian. Model luôn "thấy" cả hai, nên biết khi nào hai bên nói chồng.
2. **Inner monologue:** trước token audio của mỗi frame, model sinh một token text căn theo thời gian. Text làm "giàn giáo" ngôn ngữ, giúp nội dung mạch lạc hơn so với chỉ sinh audio. Đây cũng là lý do card nói model xuất cả "agent text" lẫn "agent speech".[^pp]
3. **RQ-Transformer (Temporal + Depth):** mô hình lớn chỉ chạy **một lần mỗi frame** (12.5 lần/giây). Mô hình nhỏ lo 8 codebook bên trong frame. Nhờ đó 7B tham số vẫn kịp realtime.

Latency lý thuyết của Moshi theo paper gốc là khoảng 160 ms (80 ms frame + 80 ms acoustic delay), khoảng 200 ms trong thực tế trên GPU. Đây là kiến thức nền về Moshi, **không** phải số đo của PersonaPlex hay của tiếng Việt.

PersonaPlex bổ sung **điều kiện hoá persona**: trước hội thoại, model nhận một voice prompt (token audio quy định giọng và phong cách) và một text prompt (vai trò, bối cảnh) (**Reported**).[^pp] So với cascade: voice prompt ≈ voice cloning của TTS, text prompt ≈ system prompt của LLM, nhưng gộp vào một model.

### 15.3.3 Turn-taking nằm trong trọng số

Card PersonaPlex mô tả cấu hình dual-stream: nghe và nói diễn ra đồng thời, trạng thái nội bộ được cập nhật từ lời user trong khi vẫn phát ra audio. Nhờ vậy model xử lý được ngắt lời, barge-in, nói chồng và đổi lượt nhanh (**Reported**).[^pp]

So sánh trực tiếp (trả lời Q1, **Synthesis**):

| Tình huống | Cascade | Full-duplex kiểu Moshi |
|---|---|---|
| User dừng giữa câu để nghĩ | VAD báo im lặng → turn detector đoán "chưa xong" → chờ timeout. Đoán sai = cắt ngang | Model thấy ngữ cảnh, tự quyết định tiếp tục im (sinh token im lặng). Sai = bot chen vào |
| User nói xong | Phải có ≥200–300 ms im lặng + quyết định của turn detector | Model có thể bắt đầu nói ngay, thậm chí *trước* khi user dứt hẳn, giống người thật |
| User ngắt lời bot | VAD/duration gate/speaker lock phát hiện → `generation_id++` → cancel LLM+TTS → flush queue (Ch.17) | Model nghe thấy luồng user có tiếng, tự ngừng sinh tiếng nói trong vài frame |
| Backchannel ("ừ", "vâng") của user | Phải phân biệt với barge-in bằng ngưỡng thời lượng | Model học được rằng "ừ" không cần dừng |
| Bot backchannel | Gần như không làm được | Có thể (FullDuplexBench đo cả tần suất backchannel) |
| Echo bot lọt vào mic | Nguồn ngắt nhầm chính; cần AEC + gating | Vẫn cần AEC: model không phân biệt được tiếng mình phát ra loa bị thu lại với tiếng user, trừ khi được huấn luyện cho trường hợp đó |
| Ai chịu trách nhiệm khi sai? | Một ngưỡng/tham số cụ thể, sửa được trong config | Hành vi của trọng số; chỉ sửa được bằng prompt hoặc fine-tune |

Hệ quả kỹ thuật: với full-duplex, **Chương 10 và một nửa Chương 17 gần như biến mất khỏi code**. Đổi lại, bạn mất khả năng tune từng tham số. Bạn không có `min_silence_ms` để chỉnh khi bot hay chen ngang người nói chậm.

### 15.3.4 Một biến thể khác: VoiceChat 11B

NemotronLabs VoiceChat 11B cũng là full-duplex end-to-end, nhưng ghép từ các khối khác (**Reported**):[^vc]

```text
user speech 16 kHz ─► Fast Conformer encoder (từ Nemotron-Speech-Streaming-En-0.6b)
                         │ embedding audio
                         ▼
               Nemotron Nano v2 9B (Hybrid Mamba/Transformer) ── dự đoán text token
                         │                        └──► kênh riêng: script tool call
                         ▼
               NVIDIA TTS decoder + codec ─► agent speech 22.05 kHz
               (+ transcript của user ở đầu ra)
```

Khác Moshi ở chỗ: đầu vào là **embedding liên tục** từ encoder ASR (không phải token codec), backbone là một LLM text có sẵn, và có **kênh tool call riêng**. Model còn có cơ chế "on-hold message": với mỗi tool, định nghĩa trước một câu để bot nói ngay khi LLM sinh text kích hoạt tool, giữ mạch hội thoại trong lúc tool chạy (**Reported**).[^vc]

Điểm cực kỳ quan trọng với tiếng Việt: card yêu cầu **system prompt và tool response phải chỉ dùng ASCII** (không em dash, không ký hiệu độ, không emoji, không Unicode khác) (**Reported**).[^vc] Tiếng Việt có dấu là Unicode. Nghĩa là ngay cả khi bỏ qua `language: en`, model này cũng không được thiết kế để nhận prompt tiếng Việt có dấu (**Synthesis**).

### 15.3.5 Đọc benchmark full-duplex

FullDuplexBench đo **động lực hội thoại** chứ không đo WER hay MOS. Theo caption trong card PersonaPlex: success rate dùng Takeover Rate (TOR) cho Smooth Turn-Taking và User Interruption, dùng 1−TOR cho Pause Handling. Smooth turn-taking latency đo từ lúc user dừng tới lúc agent bắt đầu nói. Interruption latency đo từ lúc user ngắt tới lúc agent dừng (**Reported**).[^pp]

| Chỉ số (chiều tốt) | PersonaPlex 7B | VoiceChat 11B |
|---|---|---|
| Pause Handling Synthetic TOR (↓) | 0.358 | 0.153 |
| Pause Handling Candor TOR (↓) | 0.431 | 0.255 |
| Smooth Turn Taking TOR (↑) | 0.908 | 0.82 |
| Smooth Turn Taking Latency (↓) | 0.170 | 448 ms |
| User Interruption TOR (↑) | 0.950 | 1 |
| User Interruption Latency (↓) | 0.240 | 480 ms |
| User Interruption GPT-4o (↑) | 4.290 | 4.33 |

Nguồn: hai card, đều **Reported**.[^pp][^vc] Cách đọc (**Synthesis**):

- **Trade-off "nhanh vs kiên nhẫn" hiện rõ:** PersonaPlex vào lượt nhanh hơn (latency thấp, Smooth TOR cao) nhưng cũng hay chen vào lúc user chỉ tạm dừng (Pause TOR cao hơn). VoiceChat kiên nhẫn hơn nhưng chậm hơn. Đây chính là trade-off endpointing ở Chương 10, chỉ khác là nó nằm trong trọng số.
- **Đơn vị:** bảng PersonaPlex không ghi đơn vị cho 0.170/0.240. Theo định nghĩa trong caption thì đây là thời gian, nhiều khả năng tính bằng giây. VoiceChat ghi ms. Không có bằng chứng hai card dùng cùng phiên bản bench, cùng phần cứng hay cùng cách đo, nên **không xếp hạng chéo** (VoiceChat ghi rõ Full-Duplex-Bench 1.0; PersonaPlex chỉ ghi FullDuplexBench).
- **Latency 170 ms không cùng loại với 0.7–1.2 s của cascade** (trả lời Q4): nó đo từ "user dừng" theo nhãn của benchmark, không gồm network, jitter buffer, capture/playback buffer của client, và đo trên audio tiếng Anh với phần cứng của vendor. Ngân sách cascade thì là ước lượng voice-to-voice gồm cả network. Muốn so phải đo cả hai trên cùng một harness (Ch.20).

### 15.3.6 Giới hạn của họ end-to-end

| Giới hạn | Bằng chứng trong wiki | Ý nghĩa với dự án |
|---|---|---|
| **Ngôn ngữ** | PersonaPlex `language: en`, use case "English speech response for English speech input", dữ liệu Fisher English <10k giờ. VoiceChat `language: en` (**Reported**).[^pp][^vc] | Hard gate cho tiếng Việt |
| **Dữ liệu huấn luyện** | Full-duplex cần hội thoại hai kênh tách người nói (như Fisher) hoặc dữ liệu tổng hợp. VoiceChat dùng ~550k giờ, có cả speech tổng hợp từ TTS (**Reported**).[^vc] | Dữ liệu hội thoại hai kênh tiếng Việt công khai hiếm (kiến thức nền), nên tự huấn luyện là dự án nghiên cứu, không phải việc tích hợp |
| **Phần cứng** | PersonaPlex thử trên A100 80 GB, Ampere/Hopper. VoiceChat chạy vLLM trên H100 và các GPU datacenter (**Reported**).[^pp][^vc] | Không có đường CPU/edge |
| **Kiểm soát, RAG, tool** | VoiceChat có tool calling nhưng prompt phải ASCII. PersonaPlex chỉ điều khiển qua persona prompt (**Reported**). | RAG tiếng Việt, guardrail trên text, audit: khó hoặc không làm được |
| **Thay thành phần** | Một khối trọng số | Không đổi được "chỉ giọng" hay "chỉ não" như cascade |
| **Quan sát, debug** | Có text đầu ra (inner monologue/transcript) nhưng không có chuỗi quyết định turn tường minh | Khó giải thích vì sao bot chen ngang |
| **Kiểm thử** | Cả hai card yêu cầu kiểm thử theo use case (V-model) trước khi triển khai (**Reported**).[^pp][^vc] | Vendor tự nói chưa sẵn sàng drop-in |

### 15.3.7 Chi phí compute "luôn bật"

Một hệ quả ít được nói: model frame-synchronous phải chạy **mỗi bước, kể cả khi không ai nói**. Phép tính trong phụ lục (**Reproduced**, giả định ghi rõ):

| Đại lượng | Giá trị |
|---|---|
| Token mỗi bước (1 text + 8 codebook × 2 luồng, theo cấu hình Moshi) | 17 |
| Token/giây | 212.5 |
| Hạn chót cho mỗi bước của mô hình lớn | 80 ms |
| Hội thoại 5 phút: số forward pass của mô hình lớn (duplex) | 3750 |
| Cùng hội thoại, cascade: token decode của LLM (giả định bot nói 30% thời gian, ~5 âm tiết/s, ~1.3 token/âm tiết) + 20 lần prefill | ≈ 585 token + 20 prefill |
| Tỉ lệ bước lớn duplex/cascade | ≈ 6.4× |

Ý nghĩa (**Synthesis**): mỗi session full-duplex chiếm một "khe" GPU cố định suốt cuộc gọi, và **vi phạm hạn chót 80 ms là lỗi nghe được** (audio bị giật). Cascade thì có tải theo đợt: LLM rảnh khi user nói, nên batch được nhiều session hơn. Đây là lý do vLLM-Omni phải xây riêng cơ chế "engine-owned sessions" cho full-duplex (xem §15.5).[^vllmomni] Hai phép so sánh này là thứ tự độ lớn để định hướng. Chi phí thật còn phụ thuộc kích thước model, batching và phần cứng.

---

## 15.4 Lai: audio-LLM và omni model

### 15.4.1 Phổ kiến trúc: bỏ tầng nào?

| Biến thể | Bỏ/gộp tầng | Còn giữ | Ví dụ trong wiki |
|---|---|---|---|
| **C1. Audio-LLM** (speech-in, text-out) | ASR gộp vào LLM | VAD, turn, cầu text→speech, TTS | [Ultravox](../wiki/ultravox.md) (projector audio→embedding LLM, audio in/streaming text out); HF s2s `--stt none --llm_backend chat-completions`; [Step-Audio-R1.1](../wiki/step-audio-r1-1.md) (`audio-text-to-text`) |
| **C2. Omni turn-based** (speech-in, speech-out) | ASR + LLM + TTS gộp | VAD, turn, transport | Qwen3-Omni (nghe 19 ngôn ngữ có vi, nói 10 ngôn ngữ không có vi, theo report); anecdote Nemotron Nano Omni trong llama.cpp[^stack][^community] |
| **C3. Omni + TTS riêng** | ASR + LLM gộp; TTS tách | VAD, turn, TTS ngôn ngữ đích | Chưa có triển khai trong wiki; là suy luận từ C2 cho tiếng Việt |
| **C4. Omni full-duplex trên runtime chung** | Mọi thứ, như họ B | Transport, session | MiniCPM-o 4.5 trên vLLM-Omni (full-duplex, engine-owned sessions)[^vllmomni] |
| **C5. Cascade + kênh phụ** | Không bỏ gì; thêm metadata | Tất cả | ASR + nhận diện cảm xúc → tag trong prompt → TTS có `instruct` (Synthesis) |

Ở mức kiến thức nền, các omni model kiểu Qwen-Omni thường theo mẫu **Thinker–Talker**: "Thinker" là LLM nhận audio/text và sinh text cùng hidden state; "Talker" nhận hidden state đó và sinh token tiếng nói. Biến thể C3 về bản chất là lấy đầu ra của Thinker và bỏ Talker.

### 15.4.2 Audio-LLM bỏ được gì và mất gì (Q2)

Cơ chế của Ultravox minh hoạ rõ: một **multimodal projector** chuyển audio thẳng vào không gian embedding của LLM, không cần tầng ASR riêng. Huấn luyện đóng băng cả LLM lẫn audio encoder, chỉ train adapter. README tuyên bố cách ghép trực tiếp này phản hồi nhanh hơn nhiều so với ghép ASR + LLM riêng (**Reported**).[^ultravox]

```text
Cascade:     audio ─► [ASR encoder ─► ASR decoder] ─► text ─► tokenizer ─► [LLM]
Audio-LLM:   audio ─► [audio encoder] ─► projector ─► embedding ──────────► [LLM]
                                       (không có text ở giữa)
```

**Bỏ được (Synthesis):**

- Một bước decode tuần tự (ASR decoder) trên critical path.
- Lỗi lan truyền "ASR chốt sai rồi LLM tin theo". LLM nhận biểu diễn giàu hơn một chuỗi text cứng.
- Một phần thông tin cận ngôn ngữ có thể đi tới LLM. Ultravox tự ghi việc hiểu tự nhiên các tín hiệu timing và cảm xúc là *hướng tương lai*, chưa phải năng lực hiện tại (**Reported**).[^ultravox] Step-Audio-R1.1 đi xa hơn với "acoustic-grounded reasoning": lập luận trực tiếp trên biểu diễn âm học thay vì transcript (**Reported**).[^step]
- Một model và một service cần vận hành.

**Mất hoặc phải trả (Synthesis):**

| Mất | Hệ quả | Cách bù |
|---|---|---|
| Transcript tường minh | Không có caption, log, audit, query RAG, không đo được WER | Yêu cầu model xuất transcript (tốn token, tăng latency), hoặc chạy ASR song song ngoài critical path |
| Partial transcript | Không speculative trên partial, không caption realtime | ASR streaming song song chỉ để hiển thị |
| Tự do chọn LLM | Chỉ dùng được backbone đã có adapter. Anecdote cộng đồng: bỏ STT bằng Omni đổi lấy LLM nhỏ hơn (**Reported**)[^community] | Train lại adapter (Ultravox hỗ trợ `--text-model`) |
| Ngữ cảnh | Audio chiếm nhiều token hơn text tương đương, context đầy nhanh, prefill lâu hơn | Lưu history dạng text (cần transcript), chỉ giữ audio lượt hiện tại |
| Kiểm chứng tiếng Việt | Năng lực hiểu tiếng Việt của audio-LLM chưa được đo trong wiki. Ultravox README không có danh sách ngôn ngữ (**Synthesis**)[^ultravox] | Đo riêng trên corpus §10 của thiết kế |
| Hợp đồng API | Direct audio input của HF s2s chỉ chạy với `chat-completions`, không với `responses-api`. Model mặc định không nhận audio nên phải đổi `--model_name` (**Reported**)[^hfs2s] | Contract test (Ch.16) |

Lưu ý: **audio-LLM vẫn là turn-based.** HF s2s gửi *từng đoạn VAD đã hoàn tất* tới model (**Reported**).[^hfs2s] VAD, turn detector, barge-in và cancellation vẫn y như cascade. Audio-LLM chỉ rút ngắn đoạn giữa, không đổi bản chất turn-taking.

Một điểm thú vị cho tiếng Việt: Ultravox ghi đường thêm ngôn ngữ mới bằng cách chuẩn bị mẫu có trường `audio` và `continuation`, rồi huấn luyện adapter. Chi phí v0.4 được báo là 2–3 giờ trên 8×H100 cho 14K bước (**Reported**, không rõ cho ngôn ngữ nào).[^ultravox] Vì chỉ train adapter, đây là đường fine-tune rẻ hơn nhiều so với tự huấn luyện một model full-duplex (**Synthesis**). Nhưng nó vẫn cần dữ liệu và một vòng đánh giá đầy đủ.

### 15.4.3 Omni turn-based, và mẫu "tai omni, miệng TTS Việt"

Theo report stack tiếng Việt, Qwen3-Omni-30B-A3B nhận 19 ngôn ngữ giọng nói đầu vào (có vi) nhưng chỉ phát 10 ngôn ngữ (không có vi) (**Reported**).[^stack] Biến thể C3 tận dụng đúng sự bất đối xứng này (**Synthesis**, chưa ai thử trong wiki):

```text
mic ─► VAD/turn ─► Qwen3-Omni (audio in, TEXT out) ─► chunker + normalizer VI ─► VieNeu TTS ─► loa
                    ▲ thay cho ASR + LLM               ▲ giữ nguyên cầu text→speech và TTS tiếng Việt
```

Điều kiện để mẫu này đáng làm (**Synthesis**):

1. Model hiểu tiếng Việt *qua audio* đạt độ chính xác ngữ nghĩa không thua cascade (ASR tốt nhất + LLM) trên corpus giọng Bắc/Trung/Nam, tên riêng, số.
2. TTFT với audio đầu vào thấp hơn tổng "ASR final + LLM TTFT" của cascade.
3. Text đầu ra vẫn đi qua normalizer, chunker và lexicon tiếng Việt như cascade (Ch.19).
4. License và VRAM của model 30B-A3B chấp nhận được cho profile mục tiêu.

### 15.4.4 Bản đồ "điểm cắt"

```text
                   ┌──── ranh giới text ────┐
audio ─► VAD ─► turn ─► ASR ─► │ LLM │ ─► chunker ─► TTS ─► audio
          │       │      └──C1──┘       │
          │       │      └──────── C2 ──────────────────┘
          │       │      └──── C3 ─────┘ (TTS riêng)
          └───────┴──────────────── B / C4 (full-duplex) ───────────┘
Càng gộp nhiều về phải: càng ít latency nối tầng, càng giữ nhiều cận ngôn ngữ,
càng mất kiểm soát, quan sát và khả năng thay từng phần. (Synthesis)
```

---

## 15.5 Năm tầng tách biệt

Nguyên tắc 1 của thiết kế: tách **model, inference runtime, API server, streaming policy, orchestration**. Lý do: runtime hỗ trợ GGUF không có nghĩa mọi checkpoint đều streaming; endpoint "OpenAI-compatible" không có nghĩa là drop-in; license của runtime không thay cho license của weights (**Synthesis**).[^design][^tools]

| Tầng | Câu hỏi nó trả lời | Ví dụ trong wiki |
|---|---|---|
| **1. Model (weights)** | Học được gì: ngôn ngữ, kiến trúc, streaming *về mặt toán học* (causal? chunk?), license weights | PersonaPlex, VoiceChat 11B, Ultravox, Nemotron 3.5 ASR, VieNeu v3 Turbo |
| **2. Inference runtime** | Chạy model trên phần cứng nào, precision nào, có KV cache, CUDA graph không | PyTorch, vLLM, CTranslate2, ONNX Runtime, ggml (audio.cpp, NeMo-Speech.cpp) |
| **3. API server** | Lộ ra bề mặt gì: REST, SSE, WebSocket, gRPC, OpenAI-compatible subset nào, auth | Speaches, Parakeet ASR Server, VieNeu `/v1/audio/speech`, NeMo-Speech.cpp HTTP/WS |
| **4. Streaming policy** | Cắt audio/text thế nào, khi nào phát partial/final, buffer bao nhiêu | WhisperLiveKit (SimulStreaming/LocalAgreement), RealtimeSTT, chunker mệnh đề |
| **5. Orchestration** | Ai sở hữu lượt, cancel, history, tool, session | HF s2s turn tracker, Pipecat, LiveKit Agents, gateway tự viết |

Nguồn bảng: [So sánh công cụ triển khai speech](../wiki/speech-deployment-tools-comparison.md) (**Synthesis** trên các concept **Reported**).[^tools]

### 15.5.1 Ba kiến trúc trải lên năm tầng như thế nào

| Tầng | Cascade | E2E full-duplex | Audio-LLM (C1) |
|---|---|---|---|
| 1 Model | 3–5 model riêng (VAD, turn, ASR, LLM, TTS) | 1 model | 1 audio-LLM + VAD + turn + TTS |
| 2 Runtime | Mỗi model một runtime phù hợp | Runtime phải hỗ trợ vòng lặp frame-synchronous | Runtime LLM có hỗ trợ đầu vào audio |
| 3 API server | Nhiều endpoint, mỗi endpoint một contract | 1 WebSocket hai chiều (VoiceChat: container NVIDIA, WebSocket hai chiều có function calling)[^vc] | chat-completions có audio + TTS endpoint |
| 4 Streaming policy | **Do bạn viết** (VAD frame, ASR chunk, chunker, TTS chunk) | **Phần lớn nằm trong model** (bước 80 ms là chính sách cố định) | Một nửa do bạn viết (VAD segment, chunker) |
| 5 Orchestration | **Dày**: turn tracker, generation_id, cancel, history, tool | **Mỏng**: session, transport, thực thi tool, log | Như cascade |

Điểm mấu chốt (**Synthesis**): E2E **không xoá** năm tầng mà **dời** tầng 4 và phần lớn tầng 5 vào trong tầng 1. Bạn vẫn phải lo transport, AEC phía client, giới hạn session, auth, logging, thực thi tool thật, và đo latency.

### 15.5.2 Đọc đúng tuyên bố bằng năm tầng (Q5)

Ví dụ: "vLLM-Omni hỗ trợ full-duplex realtime".

- vLLM-Omni là **tầng 2–3** (runtime + server). Release 0.30.0 nêu một framework full-duplex hợp nhất quanh engine-owned sessions **cho MiniCPM-o 4.5 và AURA**. Bản 0.26.0/0.28.0 nêu runtime full-duplex cho họ MiniCPM-o (**Reported**).[^vllmomni]
- Concept vLLM-Omni trong wiki ghi rõ full-duplex không tự áp dụng cho mọi TTS/ASR; danh sách backend theo release không phải ma trận phủ mọi model (**Synthesis**).[^tools]
- PersonaPlex là **tầng 1** với `library_name: moshi`, runtime PyTorch (**Reported**).[^pp] Wiki không có bằng chứng vLLM-Omni phục vụ PersonaPlex.
- Kết luận: tuyên bố ở tầng 2–3 **không** truyền sang một model ở tầng 1 khác. Muốn biết PersonaPlex chạy được ở đâu, phải đọc card của nó. Trong wiki có hai đường: PyTorch upstream, và một gói `PersonaPlex-GGUF` trong catalog audio.cpp. Gói này là đóng gói khác, không khẳng định dùng chung file weights (**Synthesis**).[^pp]

Tương tự: NeMo-Speech.cpp (tầng 2–3) nêu phục vụ VoiceChat 11B full-duplex qua WebSocket realtime (**Reported**).[^nemocpp] Nhưng license, ngôn ngữ và prompt ASCII-only của VoiceChat vẫn là thuộc tính tầng 1, runtime không đổi được.

### 15.5.3 Checklist khi đánh giá một hệ "voice AI"

1. **Model:** ngôn ngữ in/out khai báo trong card? license weights? dữ liệu huấn luyện? streaming về mặt kiến trúc?
2. **Runtime:** phần cứng tối thiểu? precision? đã có ai chạy *đúng checkpoint này* trên runtime này chưa?
3. **Server:** giao thức? subset API nào? cancel được không? sample rate, dtype in/out?
4. **Streaming policy:** đơn vị thời gian (frame, chunk, segment)? ai quyết định partial/final?
5. **Orchestration:** ai sở hữu lượt? barge-in làm ở đâu? tool chạy ở đâu? history lưu dạng gì?

Nếu một câu trả lời là "model tự lo", hãy ghi lại rằng bạn **mất nút điều chỉnh** ở tầng đó.

---

## 15.6 Vì sao chọn cascade cho tiếng Việt

### 15.6.1 Hard gate trước, điểm số sau

Thiết kế áp dụng thứ tự: gate bắt buộc (ngôn ngữ, license, phần cứng) loại trước, rồi mới so chất lượng (**Synthesis**).[^design]

| Gate | Cascade | E2E full-duplex (PersonaPlex, VoiceChat) | Audio-LLM (C1) | Omni nói (C2) | Omni + TTS Việt (C3) |
|---|---|---|---|---|---|
| Nghe tiếng Việt | ✅ ASR có `vi` (Qwen3-ASR, Nemotron 3.5, Whisper, PhoWhisper…)[^stack] | ❌ `language: en` | ❓ chưa đo | ✅ theo report (Qwen3-Omni) | ✅ theo report |
| Nói tiếng Việt | ✅ VieNeu, VoxCPM2… | ❌ | ✅ qua TTS riêng | ❌ không có vi đầu ra | ✅ qua TTS riêng |
| Prompt/RAG tiếng Việt | ✅ | ❌ (VoiceChat ASCII-only) | ✅ | ❓ | ✅ |
| CPU/edge | ✅ có profile E | ❌ | ❓ phụ thuộc kích thước | ❌ thực tế | ❌ thực tế |
| Đo được theo tầng (WER, MOS, TTFT) | ✅ | ⚠️ chỉ đo tổng | ⚠️ mất WER nếu không xuất transcript | ⚠️ | ⚠️ |
| **Kết luận** | **Chọn** | Loại (ngôn ngữ) | Thử nghiệm | Loại (không nói vi) | Ứng viên nghiên cứu |

Kết luận của thiết kế (**Synthesis**): chọn cascade **không phải vì cascade tốt hơn về bản chất**, mà vì trong snapshot của wiki chỉ cascade ghép được một vòng tiếng Việt hoàn chỉnh. Nếu có model full-duplex hỗ trợ tiếng Việt kèm bằng chứng, hãy đánh giá lại bằng cùng các gate ở §10.[^design]

### 15.6.2 Những gì cascade buộc phải bù

Chọn cascade nghĩa là chấp nhận viết tay những thứ full-duplex "học" được. Đây là danh sách việc của các chương sau:

| Năng lực full-duplex có sẵn | Cascade bù bằng | Chương |
|---|---|---|
| Biết lúc nào user nói xong | VAD + Smart Turn + timeout + reopen | 10, 17 |
| Ngừng nói khi bị ngắt | `generation_id`, cancel LLM/TTS, flush queue, `client.clear` | 17, 18 |
| Phản hồi sớm | Stream mọi tầng + chunker mệnh đề + speculative | 18, 19, 20 |
| Giọng nhất quán với ngữ cảnh | Prompt văn nói, `instruct` TTS, lexicon | 12, 13, 19 |
| Không bị echo của chính mình đánh lừa | AEC client + duration gate + speaker lock | 7, 14 |

---

## 15.7 Khi nào xem lại quyết định

### 15.7.1 Tín hiệu kích hoạt (Q6)

1. **Có model full-duplex hoặc omni nói được tiếng Việt** (card khai báo `vi` ở *đầu ra*), có license chấp nhận được.
2. **Có số đo tiếng Việt độc lập** cho audio-LLM/omni: độ chính xác hiểu trên corpus đa phương ngữ, tốt hơn hoặc ngang cascade.
3. **Cascade đã tối ưu mà vẫn không đạt mục tiêu latency** và sàn nằm ở khoảng im lặng chốt lượt (P95 endpoint chiếm phần lớn voice-to-voice dù đã tune Smart Turn).
4. **Yêu cầu sản phẩm cần backchannel, nói chồng, cảm xúc** mà kênh phụ (C5) không đáp ứng được.
5. **Runtime phục vụ full-duplex trưởng thành** cho model đó (session, batching, cancel), có số concurrency trên phần cứng mục tiêu.
6. **Tool calling và RAG trong model E2E** hỗ trợ Unicode/tiếng Việt và có audit trail đủ cho yêu cầu tuân thủ.

### 15.7.2 Quy trình đánh giá lại

```text
1. Gate cứng: ngôn ngữ in/out, license weights + runtime, phần cứng, privacy (Ch.23)
2. Đặt ứng viên sau CÙNG transport + AEC + harness đo như cascade hiện tại
3. Chạy corpus §10: ASR-equivalent (độ chính xác hiểu), TTS (MOS người Việt),
   turn & barge-in (false-cutoff, missed/false interrupt, thời gian dừng), tải (concurrency 1/4/8/16)
4. So P50/P95 voice-to-voice đo trên cùng harness (không dùng số trong card)
5. Chỉ chuyển nếu thắng ở gate quan trọng mà KHÔNG thua ở kiểm soát/tuân thủ
```

### 15.7.3 Thiết kế cascade "sẵn sàng thay não"

Để việc thử lai hay E2E sau này rẻ, cascade nên giữ các ranh giới sau (**Synthesis**):

- **Event contract không phụ thuộc kiến trúc:** `turn.commit`, `audio.start/chunk/played`, `generation_id`, `barge_in` (Ch.17). Một backend E2E cũng phải phát được các event này, thì client và hệ thống đo không phải sửa.
- **Interface "brain" trừu tượng:** đầu vào là audio lượt + transcript (tuỳ chọn) + history; đầu ra là text stream *hoặc* audio stream. Cascade dùng nhánh text→TTS, C1/C3 cắm vào cùng chỗ, C2 bỏ qua TTS.
- **Transport và AEC tách khỏi model** (Ch.6–8): mọi kiến trúc đều cần.
- **History lưu dạng text kèm tag `[bị ngắt]`** để đổi backend không làm mất ngữ cảnh.
- **Harness đo latency gắn timestamp ở cạnh, không trong model** (Ch.20), để so được các kiến trúc với nhau.

---

## 15.8 Lỗi tư duy thường gặp

| Lỗi | Vì sao sai | Đúng là |
|---|---|---|
| "E2E luôn nhanh hơn cascade" | So số bench (từ lúc user dừng, không có network) với ngân sách voice-to-voice | Đo cùng harness. Cascade có stream tốt có thể chấp nhận được |
| "Model omni nghe được tiếng Việt thì dùng được cho voice tiếng Việt" | Đầu vào và đầu ra là hai danh sách ngôn ngữ khác nhau | Kiểm tra riêng ngôn ngữ đầu ra (Qwen3-Omni: không có vi) |
| "Runtime X hỗ trợ full-duplex nên model Y full-duplex được" | Nhầm tầng 2–3 với tầng 1 | Đọc card model + recipe runtime cho đúng checkpoint |
| "Bỏ ASR là bỏ được VAD/turn" | Audio-LLM vẫn nhận *đoạn VAD đã hoàn tất* | Audio-LLM chỉ thay tầng ASR (và gộp với LLM) |
| "Cascade mất thanh điệu tiếng Việt" | Thanh điệu nằm trong chữ viết | Mất ngữ điệu, cảm xúc, nhấn mạnh; thanh điệu chỉ mất khi ASR sai |
| "E2E không cần AEC" | Model vẫn nghe tiếng loa của chính nó | Giữ AEC phía client cho mọi kiến trúc |
| "E2E thì không cần orchestration" | Vẫn cần session, transport, tool, log, giới hạn tải | Orchestration mỏng đi, không biến mất |
| "Full-duplex rẻ vì chỉ một model" | Compute luôn bật, hạn chót 80 ms mỗi bước | Đo concurrency trên GPU mục tiêu |

---

## 15.9 Bài tập thực hành

1. **Vẽ critical path.** Lấy ngân sách §15.2.4, vẽ waterfall cho ba kịch bản: half-duplex không stream, cascade stream đầy đủ, cascade + preemptive. Đánh dấu khoảng nào là sàn không giảm được.
2. **Sửa script.** Trong phụ lục, đổi giả định "bot nói 30%" thành 10% và 60%, quan sát tỉ lệ compute duplex/cascade. Thêm tham số batch: nếu GPU batch được N session cascade nhưng chỉ M session duplex, cần bao nhiêu GPU cho 100 cuộc gọi đồng thời?
3. **Phân loại.** Với mỗi hệ sau, xếp vào A/B/C1–C5 và chỉ ra ai sở hữu lượt: HF s2s mặc định; HF s2s với `--stt none`; PersonaPlex; VoiceChat 11B trên NeMo-Speech.cpp; Ultravox + VieNeu; Pipecat + Smart Turn + faster-whisper + VieNeu.
4. **Năm tầng.** Chọn một sản phẩm/README bất kỳ quảng cáo "realtime voice AI", điền checklist §15.5.3, đánh dấu mọi chỗ "model tự lo".
5. **Thí nghiệm nhỏ (cần GPU, tuỳ chọn).** Chạy HF s2s ở chế độ direct audio input với một model nhận audio, đọc 20 câu tiếng Việt có số và tên riêng. So câu trả lời với cascade faster-whisper `language="vi"` + cùng LLM. Ghi lại: model có hiểu đúng số và tên riêng không? TTFT khác bao nhiêu?

---

## 15.10 Đáp án các câu hỏi

**Q1.** Cascade xử lý turn-taking *bên ngoài* model, bằng state machine: VAD phát hiện im lặng, turn detector đoán hết lượt, gateway commit lượt, và barge-in kích hoạt cancel theo `generation_id`. Mọi quyết định là tham số chỉnh được. Full-duplex kiểu Moshi xử lý *bên trong* model: hai luồng token (user và bot) chạy song song mỗi 80 ms, model tự quyết định mỗi frame là nói, im hay backchannel. Ngắt lời, nói chồng và đổi lượt là hành vi học được, không có "end of turn" tường minh. Đổi lại, không còn núm vặn để tune, và sai thì phải sửa bằng prompt hoặc fine-tune (§15.3.1–15.3.3).

**Q2.** Audio-LLM bỏ tầng ASR riêng (và ranh giới text giữa ASR và LLM): ít một bước decode, ít lỗi lan truyền, có thể giữ một phần cận ngôn ngữ. Nó **không** bỏ VAD/turn (vẫn nhận đoạn VAD hoàn tất), không bỏ TTS (nếu text-out). Đổi lại mất transcript tường minh (log, caption, RAG, WER), mất partial, bị giới hạn LLM backbone, context đầy nhanh hơn, và năng lực tiếng Việt phải đo riêng. Omni nói được (C2) bỏ thêm TTS, nhưng với tiếng Việt thì đầu ra là gate (Qwen3-Omni không nói vi) (§15.4.2–15.4.3).

**Q3.** Thanh điệu tiếng Việt là thanh điệu từ vựng, được mã hoá bằng dấu trong chữ viết. ASR đúng thì thanh điệu đi qua nút cổ chai text nguyên vẹn. Ngữ điệu câu, cảm xúc, nhấn mạnh, do dự thì không có ký hiệu chữ viết tương ứng (ngoài dấu câu thô), nên bị mất. Câu hỏi tiếng Việt thường có tiểu từ nghi vấn, nên mất ngữ điệu ít ảnh hưởng tới việc nhận ra câu hỏi hơn ở tiếng Anh (§15.2.5).

**Q4.** Vì hai con số khác định nghĩa và điều kiện. Latency của benchmark full-duplex đo từ "user dừng" (theo nhãn benchmark) tới "agent bắt đầu nói", trên audio tiếng Anh, phần cứng vendor, không gồm network, jitter buffer và buffer playback của client. 0.7–1.2 s của cascade là ước lượng voice-to-voice có cả network, và cũng chưa đo. Đơn vị bảng PersonaPlex còn không ghi rõ. Chỉ so được khi đo cả hai trên cùng harness (§15.3.5, Ch.20).

**Q5.** Không suy ra được. vLLM-Omni là runtime + server (tầng 2–3); tuyên bố full-duplex của nó gắn với các model cụ thể (MiniCPM-o 4.5, AURA) qua engine-owned sessions. PersonaPlex là tầng 1, `library_name: moshi`, runtime PyTorch theo card. Wiki không có bằng chứng vLLM-Omni phục vụ PersonaPlex. Khả năng của runtime không truyền sang model khác (§15.5.2).

**Q6.** Bất kỳ ba trong số: (1) có model full-duplex/omni khai báo tiếng Việt ở đầu ra, license chấp nhận được; (2) có số đo độc lập về độ chính xác hiểu tiếng Việt của audio-LLM/omni, ngang hoặc hơn cascade; (3) cascade đã tối ưu nhưng sàn latency nằm ở khoảng im lặng chốt lượt; (4) sản phẩm cần backchannel, nói chồng, cảm xúc; (5) runtime full-duplex có số concurrency trên phần cứng mục tiêu; (6) tool/RAG trong E2E hỗ trợ Unicode và có audit trail (§15.7.1).

---

## Phụ lục chương: script mô phỏng

File: `/tmp/c15/sim.py` (Python thuần, không phụ thuộc). Sao chép nguyên văn dưới đây để chạy lại.

```python
# Chương 15 — mô hình số học minh hoạ (không đo model thật)
# 1) Cascade: critical path tuần tự vs có overlap/streaming
stages = [  # (tên, thấp ms, cao ms) — ngân sách ước lượng của AI report (Reported)
    ("network+jitter", 30, 80),
    ("VAD silence", 200, 300),
    ("Smart Turn", 10, 65),
    ("ASR turn-final", 100, 300),
    ("LLM TTFT+chunk1", 150, 350),
    ("TTS TTFA", 64, 300),
]
lo = sum(s[1] for s in stages); hi = sum(s[2] for s in stages)
print("1a. cộng thẳng ngân sách:", lo, "-", hi, "ms")
# Không streaming: chờ LLM sinh hết câu trả lời (vd. 40 token @ 50 tok/s) rồi TTS cả câu (3 s audio, RTF 0.3)
full_llm = 40/50*1000; full_tts = 3000*0.3
print("1b. không streaming LLM/TTS:", round(lo-150-64+full_llm+full_tts), "-", round(hi-350-300+full_llm+full_tts), "ms")
# Streaming ASR: phần lớn audio đã decode trong lúc user nói; endpoint->final chỉ còn ~1 chunk
for chunk in (160, 320):
    lo2 = lo-100+chunk*0.5; hi2 = hi-300+chunk
    print(f"1c. streaming ASR chunk {chunk} ms: {lo2:.0f} - {hi2:.0f} ms")
# Preemptive: khởi động ASR+LLM ngay khi VAD 200 ms, song song với Smart Turn → bỏ Smart Turn khỏi path nếu đoán đúng
print("1d. preemptive (đoán đúng):", lo-10, "-", hi-65, "ms")

# 2) Full-duplex frame-synchronous: chi phí compute luôn bật
frame_hz = 12.5          # Mimi/Moshi: 80 ms mỗi bước (kiến thức nền)
codebooks = 8            # số codebook mỗi stream (kiến thức nền, Moshi)
streams_per_step = 1 + codebooks*2   # text + audio agent + audio user
print("2a. token/bước:", streams_per_step, " token/s:", frame_hz*streams_per_step)
print("2b. hạn chót mỗi bước temporal:", 1000/frame_hz, "ms")
conv_s = 300  # cuộc hội thoại 5 phút
duplex_steps = conv_s*frame_hz
# Cascade: LLM chỉ chạy khi trả lời. Giả định bot nói 30% thời gian, ~5 âm tiết/s, ~1.3 token/âm tiết
bot_speech_s = 0.3*conv_s; tok = bot_speech_s*5*1.3
turns = 20
print("2c. duplex: forward pass mô hình lớn =", int(duplex_steps))
print("2d. cascade: token decode LLM ≈", int(tok), "+ prefill", turns, "lần")
print("2e. tỉ lệ bước lớn duplex/cascade ≈", round(duplex_steps/tok, 1))
```

Đầu ra khi chạy (Python 3, 2026-10-07):

```text
1a. cộng thẳng ngân sách: 554 - 1395 ms
1b. không streaming LLM/TTS: 2040 - 2445 ms
1c. streaming ASR chunk 160 ms: 534 - 1255 ms
1c. streaming ASR chunk 320 ms: 614 - 1415 ms
1d. preemptive (đoán đúng): 544 - 1330 ms
2a. token/bước: 17  token/s: 212.5
2b. hạn chót mỗi bước temporal: 80.0 ms
2c. duplex: forward pass mô hình lớn = 3750
2d. cascade: token decode LLM ≈ 585 + prefill 20 lần
2e. tỉ lệ bước lớn duplex/cascade ≈ 6.4
```

Giới hạn: phép so 2e chỉ đếm *số lần chạy*, không tính kích thước model (LLM cascade có thể lớn hơn hay nhỏ hơn 7B), không tính prefill dài, không tính batching. Mục đích là cho thấy hình dạng tải (luôn bật so với theo đợt), không phải chi phí tuyệt đối.

### Liên kết sang chương khác

- Chương 4 (DSP) và Chương 9 (nền ML): codec, RVQ, encoder Conformer, projector là nền để đọc phần E2E và audio-LLM.
- Chương 5 (ngữ âm tiếng Việt): thanh điệu từ vựng và tiểu từ nghi vấn, cơ sở cho §15.2.5.
- Chương 7 (front-end): AEC cần cho mọi kiến trúc.
- Chương 10 (VAD, turn): phần full-duplex "học được" mà cascade phải viết tay.
- Chương 11 (ASR), Chương 12 (LLM), Chương 13 (TTS): các khối của cascade; §12.9 tóm tắt ngắn các hướng thay thế.
- Chương 16 (dataflow, audio contract): sample rate in/out khác nhau giữa các kiến trúc (PersonaPlex 24/24 kHz, VoiceChat 16/22.05 kHz).
- Chương 17 (turn-taking, cancellation): event contract nên giữ ổn định để đổi backend.
- Chương 20 (latency): harness đo chung để so kiến trúc.
- Chương 21 (đánh giá): gate dùng khi xem lại quyết định.
- Chương 22 (runtime, serving): năm tầng ở mức triển khai; compute luôn bật của full-duplex.
- Chương 23 (license): license weights so với runtime; OpenMDW, NVIDIA Open Model License, CC-BY-4.0 của base Moshiko.

[^design]: [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) — §2.1 (bảng hai họ kiến trúc, kết luận chọn cascade), §2.2 (biến thể lai direct audio input, anecdote Omni), §3 nguyên tắc 1 (tách năm tầng) và 6 (không cộng con số khác loại), §10 (release gates).
[^stack]: [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md) — "Vietnamese coverage by component" (dòng Qwen3-Omni-30B-A3B: 19 ngôn ngữ vào có vi, 10 ngôn ngữ ra không có vi; các ASR có vi); "Latency budget (report estimates)"; "Deployment tiers"; nhận định omni/E2E chưa thay được cascade cho tiếng Việt (qua thiết kế §2.1). Nguồn là AI report thứ cấp.
[^blueprint]: [Cascaded Voice-Agent Blueprint](../wiki/cascaded-voice-agent-blueprint.md) — đoạn tóm tắt (không chờ LLM trả lời xong mới TTS, mục tiêu 1–2 s); "Recommended rollout" (half-duplex MVP trước, sau đó streaming TTS, `generation_id`, AEC, barge-in full-duplex). Nguồn là câu trả lời ChatGPT, chưa kiểm chứng.
[^hfs2s]: [HF Speech-to-Speech Pipeline](../wiki/speech-to-speech-pipeline.md) — "LLM backend selection" (direct audio input `--stt none --llm_backend chat-completions`, gửi từng đoạn VAD hoàn tất, không hỗ trợ `responses-api`, model mặc định không nhận audio); "Multilingual behavior" (độ phủ ngôn ngữ do STT/TTS quyết định).
[^pp]: [PersonaPlex 7B v1](../wiki/personaplex-7b-v1.md) — Model identity and release (`language: en`, base `kyutai/moshiko-pytorch-bf16`, `library_name: moshi`, license); Architecture and conversational behavior (Mimi encoder/decoder, Temporal + Depth Transformer, token text + audio, dual-stream, voice prompt + text prompt); Inputs and outputs (24 kHz); Software and hardware integration (PyTorch, A100 80 GB, V-model); Training data (Fisher English, <10k giờ); Evaluation results (bảng FullDuplexBench, caption định nghĩa TOR và latency); Relationships (gói PersonaPlex-GGUF của audio.cpp).
[^vc]: [NVIDIA NemotronLabs VoiceChat 11B](../wiki/nvidia-nemotronlabs-voicechat-11b.md) — Model identity (`language: en`, OpenMDW-1.1); Architecture and I/O (Fast Conformer, Nano v2 9B, TTS decoder + codec, kênh tool, on-hold message, 16 kHz vào / 22.05 kHz ra, transcript user); Software and hardware integration (vLLM, GPU datacenter, V-model); Training data (~550k giờ, có speech tổng hợp); Evaluation results (Full-Duplex-Bench 1.0, 448/480 ms); Inference and deployment (container, WebSocket hai chiều); Function-calling prompt contract (ASCII-only).
[^ultravox]: [Ultravox](../wiki/ultravox.md) — Architecture and I/O (projector audio→embedding LLM, tuyên bố nhanh hơn ASR+LLM, cận ngôn ngữ là hướng tương lai, audio in/streaming text out); Model identity (không có danh sách ngôn ngữ, license); Training and adaptation (đóng băng LLM + encoder, chỉ train adapter, 2–3 giờ 8×H100 cho v0.4, `--text-model`/`--audio-model`, dữ liệu `audio` + `continuation` cho ngôn ngữ mới).
[^step]: [Step-Audio-R1.1](../wiki/step-audio-r1-1.md) — Model identity (`pipeline_tag: audio-text-to-text`); Architecture and reasoning (Dual-Brain Mind-Paced Speaking, acoustic-grounded reasoning thay vì lập luận trên transcript); Requirements (4 GPU, vLLM tuỳ biến).
[^community]: [Community-Reported STT-LLM-TTS Pipeline Wiring](../wiki/community-stt-llm-tts-pipeline.md) — bình luận bỏ tầng STT → LLM bằng Omni model trong llama.cpp, đổi lại LLM nhỏ hơn (Nemotron Nano Omni); đoạn "Cascade versus Omni shortcut" (không có số đo). Một thread cộng đồng.
[^vllmomni]: [vLLM-Omni](../wiki/vllm-omni.md) — Release line 0.26.0/0.28.0/0.30.0 (full-duplex runtime cho MiniCPM-o 4.5, AURA, engine-owned sessions); voice-loop runtime advances; tài liệu realtime duplex API được link nhưng chưa có trong `raw/`.
[^nemocpp]: [NeMo-Speech.cpp](../wiki/nemo-speech-cpp.md) — bảng Models and applications (dòng Full-duplex voicechat → VoiceChat 11B); Local server (realtime VoiceChat khi load model); Relationships (Serves VoiceChat 11B).
[^tools]: [So sánh công cụ triển khai speech](../wiki/speech-deployment-tools-comparison.md) — đoạn mở đầu (tách model, runtime, API server, streaming pipeline, orchestration); §3 (vLLM-Omni: full-duplex không áp dụng tự động cho mọi TTS/ASR); §4 (OpenAI-compatible thường là subset); §6 (orchestration). Trang status draft.
