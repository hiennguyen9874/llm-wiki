# Chương 12. LLM trong vòng hội thoại nói 🟡

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần IV.
> **Chương trước:** [Chương 11. ASR: hợp đồng input/output và hành vi streaming](chuong-11-asr-hop-dong-input-output-va-hanh-vi-streaming.md). **Chương tiếp theo:** [Chương 13. TTS: từ văn bản tới waveform](chuong-13-tts-tu-van-ban-toi-waveform.md).
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §5.5 (giao diện LLM), §7.3 (barge-in), §8.1 và §8.3 (latency).
> **Cơ sở:** phần giải thích về LLM serving (TTFT, KV cache, prefix cache, continuous batching, decoding), prompt engineering và hành vi mô hình là kiến thức nền chung, không phải claim lấy từ nguồn wiki. Tham số và quy tắc cụ thể lấy từ wiki và gắn nhãn bằng chứng: [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md), [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md), [Cascaded Voice-Agent Blueprint](../wiki/cascaded-voice-agent-blueprint.md), [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md), [HF Speech-to-Speech Pipeline](../wiki/speech-to-speech-pipeline.md), [Speech-to-Speech Realtime Engine](../wiki/speech-to-speech-realtime-engine.md), [Community STT-LLM-TTS Wiring](../wiki/community-stt-llm-tts-pipeline.md). Số liệu wiki là **Reported** (chưa chạy lại model nào). Mô phỏng ở §12.7 chạy bằng script Python thuần (**Reproduced**, script ở "Phụ lục chương"); nó chỉ kiểm tra logic điều khiển, không đo model thật. Suy luận của tác giả là **Synthesis**.

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Nhìn LLM trong voice loop như một **streaming text service có thể huỷ**, với contract rõ (vào gì, ra sự kiện gì, huỷ thế nào), không phải một "hộp trả lời".
2. Hiểu và đo đúng **TTFT, tokens/s, time-to-first-clause**, biết chúng đóng góp thế nào vào độ trễ nghe được.
3. Viết **system prompt cho hội thoại nói** (khác prompt cho chat hiển thị), và biết vì sao phải tắt thinking.
4. Quản lý **history** đúng khi bị ngắt lời, khi transcript ASR bị revise, và khi hội thoại dài.
5. Biết khi nào được **speculative generation** và khi nào phải discard; vì sao **tool call/side effect chỉ chạy sau commit**.
6. Nhận diện và giảm **contention GPU** khi LLM chạy chung máy với ASR/TTS.
7. Biết LLM **không** quyết định những gì (VAD, turn, echo, normalizer) để không đổ lỗi nhầm tầng.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. TTFT là gì? Vì sao chỉ cần "mệnh đề có nghĩa đầu tiên" chứ không cần cả câu trả lời?
- Q2. Prompt cho câu trả lời để đọc khác prompt cho câu trả lời để hiển thị ra sao?
- Q3. Khi bị ngắt lời, history nên lưu gì? Vì sao không lưu cả câu LLM đã sinh?
- Q4. Vì sao phải tắt thinking, và tắt bằng cách nào tuỳ backend?
- Q5. Speculative generation trên partial/ngưỡng im lặng ngắn là gì? Điều kiện nào buộc discard?
- Q6. Vì sao không chạy tool có side effect trên output speculative?
- Q7. LLM, ASR và TTS cùng một GPU gây ra vấn đề gì? Đo thế nào?

---

## 12.1 Vị trí của LLM trong cascade

Trong cascade, LLM là tầng "hiểu và quyết định": nhận **text đã commit** từ ASR, trả về **luồng text** cho tầng chunker/TTS.

```text
... → ASR → validity/hallucination gate → turn.commit
                                              │
                                              ▼
                              ┌───────────────────────────────┐
                              │ LLM adapter (OpenAI-compatible)│
                              │  in : system + history + user  │
                              │  out: text deltas, tool calls, │
                              │       done | error             │
                              │  cancel: đóng stream           │
                              └───────────────────────────────┘
                                              │ text deltas
                                              ▼
                            clause chunker → normalizer → TTS
```

Thiết kế wiki không chọn model LLM cụ thể: gateway chỉ yêu cầu streaming text, `done`, `error`, `cancel` và correlation theo `generation_id` (**Synthesis**).[^design] Đây là quyết định đúng vì ba lý do:

- LLM thay đổi nhanh nhất trong stack (kích thước, license, hosted vs local).
- Phần speech chỉ cần *hành vi* của nó (streaming, huỷ được, latency), không cần *danh tính* của nó.
- Cô lập contract giúp A/B nhiều LLM mà không đổi gateway.

**Những việc LLM không làm** (dễ gán nhầm lỗi):

| Việc | Tầng chịu trách nhiệm |
|---|---|
| Quyết định người dùng đã nói xong | VAD + turn detection (Chương 10) |
| Biết transcript có đáng tin không | ASR + validity gate (Chương 11) |
| Đọc số/tiền/ngày thành chữ | Normalizer (Chương 19) |
| Tránh bot nghe lại chính mình | AEC (Chương 7) |

LLM chỉ thấy **chuỗi ký tự**: nó không biết người dùng nói giọng gì, ngắt quãng thế nào, ASR confidence bao nhiêu, trừ khi gateway truyền vào (§12.4.4).

---

## 12.2 Contract streaming của LLM

### 12.2.1 API kiểu OpenAI-compatible

Đa số backend (OpenAI, HF Inference Providers, OpenRouter, vLLM, llama.cpp, SGLang) nói chung một dạng **Chat Completions** (`/v1/chat/completions`); một số có thêm **Responses API** (`/v1/responses`). HF speech-to-speech hỗ trợ cả hai và giải thích khác biệt chỉ là đường dẫn cùng cờ kết nối; nó khuyên dùng `chat-completions` khi provider bỏ qua `chat_template_kwargs.enable_thinking` trên đường Responses, hoặc khi streaming tool-call của Responses không ổn định trên một số bản vLLM (**Reported**).[^s2s]

Request tối thiểu cho voice:

```json
{
  "model": "...",
  "messages": [
    {"role": "system", "content": "<prompt nói chuyện>"},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    {"role": "user", "content": "<transcript đã commit>"}
  ],
  "stream": true,
  "temperature": 0.4,
  "max_tokens": 200
}
```

Blueprint đề xuất `temperature` 0.4–0.7, `max_tokens` 200–500, `stream=true`, `thinking=false` (**Reported**, chưa đo).[^blueprint]

Hai chi tiết API cần biết (kiến thức nền, kiểm tra lại theo backend):

- OpenAI hiện dùng `max_completion_tokens` cho Chat Completions (`max_tokens` bị deprecated và không dùng được với model reasoning); vLLM và llama.cpp vẫn nhận `max_tokens`. Adapter nên map tham số theo backend.
- Thêm `"stream_options": {"include_usage": true}` để chunk cuối mang `usage` (prompt tokens, completion tokens, và `prompt_tokens_details.cached_tokens` nếu backend hỗ trợ). Đây là nguồn cho metric trúng prefix cache ở §12.11.1.

### 12.2.2 Chuỗi sự kiện

Stream trả về qua **SSE** (Server-Sent Events). Với Chat Completions, mỗi dòng `data: {...}` chứa một `choices[0].delta`, kết thúc bằng `data: [DONE]`. Responses API thì khác: các sự kiện có kiểu (`response.output_text.delta`, `response.function_call_arguments.delta`, `response.completed`…) và không có `[DONE]`. Nếu vLLM bật reasoning parser, phần suy nghĩ đi riêng vào `delta.reasoning_content`; adapter phải bỏ trường này khỏi luồng TTS, nhưng thời gian sinh nó vẫn cộng vào TTFC (§12.3.5). Gateway nên chuẩn hoá tất cả thành sự kiện nội bộ:

```text
LLMEvent {
  session_id, utterance_id, generation_id   # định danh để huỷ/đối chiếu
  kind: "text_delta" | "tool_call" | "done" | "error"
  text?        # với text_delta
  tool?        # với tool_call (name, arguments đã đủ hay đang stream)
  finish_reason?  # stop | length | tool_calls | cancelled | error
  t_monotonic  # để đo TTFT
}
```

Điểm cần canh:

- **`finish_reason=length`:** bị cắt vì `max_tokens`; câu cuối có thể cụt. Với giọng nói, cắt giữa câu nghe rất tệ. Hãy đặt `max_tokens` dư và dạy bằng prompt giữ ngắn, đừng dùng `max_tokens` như công cụ chính để giữ ngắn.
- **`error` giữa chừng:** TTS có thể đã đọc nửa câu. Cần chính sách: nói câu xin lỗi ngắn đã soạn sẵn, hoặc im lặng và để người dùng hỏi lại. Đừng tự thử lại ngầm và đọc lại từ đầu.
- **Tool call streaming:** `arguments` thường đến rời rạc theo từng mảnh JSON. Chỉ thực thi khi đã đủ và parse được (§12.6).

### 12.2.3 Huỷ (cancel)

Huỷ nghĩa là **đóng kết nối stream** (đóng HTTP response/SSE, hoặc gửi `response.cancel` ở Realtime). Server tốt sẽ dừng decode và giải phóng slot GPU khi phát hiện client ngắt kết nối. Hai việc phải kiểm tra, không giả định:

1. **Client có thật sự đóng stream không?** Một số SDK buffer hoặc chạy trong thread không huỷ được từ bên trong. Thiết kế wiki gọi đây là một **deployment gate**: nếu SDK không cancel được thì không được dùng cho full-duplex (**Synthesis**).[^design]
2. **Server có dừng compute không?** Đóng socket phía client chưa chắc làm backend ngừng sinh token. Hãy đo "thời gian giải phóng compute" tách khỏi "thời gian bot hết phát tiếng" (§12.5.3).

Ngoài huỷ cứng, mọi chunk đến muộn sau khi huỷ phải bị **loại bỏ bằng `generation_id`**: chunk nào mang id cũ thì bỏ (§12.5.1).

---

## 12.3 Latency của LLM trong vòng nói

### 12.3.1 Các đại lượng

| Đại lượng | Ý nghĩa | Vì sao quan trọng với voice |
|---|---|---|
| **Prefill time** | Thời gian xử lý toàn bộ prompt (system + history + user) | Tăng theo độ dài prompt; nằm trong TTFT |
| **TTFT** (time to first token) | Từ lúc gửi request đến token đầu tiên | Thành phần cố định của độ trễ nghe được |
| **Tokens/s (decode rate)** | Tốc độ sinh token sau token đầu | Quyết định TTS có "đói" text hay không (§12.3.3) |
| **Time to first clause (TTFC)** | Từ gửi request đến khi chunker có mệnh đề đầu | **Số cần tối ưu thật sự**; = TTFT + thời gian sinh đủ ~1 mệnh đề |
| **Total generation time** | Đến `done` | Ít quan trọng nếu TTS đã chạy song song; quan trọng với tải GPU |

HF s2s gọi LLM là tầng tốn compute và có latency cao nhất; một forward pass của model lớn có thể chiếm phần lớn thời gian phản hồi (**Reported**).[^s2s] Wiki nêu ngân sách tham khảo "LLM TTFT + chunk đầu" 150–350 ms với **giả định Qwen3-8B AWQ trên vLLM, có prefix cache** — đây là ước lượng của report, chưa đo, và wiki nhấn mạnh LLM là dependency ngoài nên pipeline không cam kết tổng ~1 s khi chưa biết endpoint (**Reported / Synthesis**).[^stack][^design]

### 12.3.2 Vì sao chỉ cần "mệnh đề có nghĩa đầu tiên"

Giả sử LLM trả lời 40 token (~2 câu), decode 40 token/s.

- **Chờ cả câu trả lời rồi mới TTS:** độ trễ = TTFT + 40/40 s = TTFT + 1000 ms (rồi còn TTS first audio).
- **Chunk theo mệnh đề:** mệnh đề đầu ~10 token → TTFT + 250 ms; TTS bắt đầu ngay, trong khi LLM tiếp tục sinh phần sau.

Người nghe chỉ cảm nhận thời điểm **âm thanh đầu tiên**, phần còn lại chỉ cần *không bị đứt*. Blueprint gọi sentence-buffered streaming là tối ưu quan trọng nhất (**Reported**).[^blueprint] (Số 40 token/s ở trên là ví dụ minh hoạ, **Synthesis**.)

Nhưng không phải càng sớm càng tốt:

- **Chunk quá nhỏ (per-token):** prosody gãy, TTS thiếu ngữ cảnh, số request bùng nổ, khe hở nghe được. Wiki loại bỏ per-token; đơn vị tốt thường là một câu hoặc ~20–60 ký tự (**Reported**).[^blueprint]
- **Chunk quá lớn:** mất lợi thế streaming.

Quy tắc chunker khởi điểm của thiết kế (chi tiết ở Chương 19; **Reported**):[^design]

- flush ở `.?!…;:` hoặc xuống dòng;
- với chunk đầu, cắt ở dấu phẩy nếu đã có ≥ ~25 ký tự, để giảm TTFA;
- gộp mảnh < 8 ký tự vào câu sau.

> **Bẫy "chunk đầu quá ngắn".** Câu như "Dạ," dễ được chunker flush rất sớm, nhưng TTS đọc "Dạ," rồi có khe im lặng trước chunk 2. Cần đảm bảo chunk 2 sẵn sàng kịp (§12.3.3).

### 12.3.3 Underrun: khi LLM sinh chậm hơn tốc độ nói

Giọng nói tiếng Việt khoảng 4–6 âm tiết/giây (xấp xỉ, **Synthesis**). Vì tokenizer đa ngôn ngữ thường tách một âm tiết có dấu thành 1–2 token, tốc độ nói tương đương khoảng 5–12 token/giây (ước lượng, đo lại bằng tokenizer thật). Hầu hết LLM interactive đều sinh nhanh hơn nhiều, nên thường không là vấn đề. Nhưng với model lớn/CPU/quá tải GPU, tokens/s có thể thấp. Khi đó:

```text
TTS chunk 1 phát xong → chunk 2 chưa có → khe im lặng → "ngắt quãng"
```

Biện pháp:

- Đo **inter-chunk gap** (khoảng giữa chunk kết thúc phát và chunk kế sẵn sàng) như một metric (underrun).
- Chọn LLM nhỏ hơn hoặc quantized, hoặc MoE với ít tham số hoạt động (report liệt kê Qwen3-30B-A3B cho GPU server vì ~3B active cho TTFT tốt; **Reported**).[^stack]
- Cho phép "buffer trước" nhẹ: chỉ bắt đầu phát khi đã có 1–2 chunk (đổi lấy +TTFC để chống underrun). Đây là trade-off cần cấu hình, không có đáp án chung.

### 12.3.4 Prefix cache cho system prompt

System prompt và (phần) history **giống nhau giữa các lượt**, nên có thể tái dùng KV cache đã tính của phần tiền tố:

- vLLM có **automatic prefix caching**; llama.cpp có prompt cache. Nguyên lý: nếu tiền tố token giống hệt, bỏ qua prefill của phần đó.
- Report khuyến nghị bật prefix cache cho system prompt như một tối ưu (**Reported**).[^stack]

Quy tắc thực hành (**Synthesis**):

1. Đặt phần **ổn định lên trước** (system prompt, định nghĩa tool, persona), phần **thay đổi ở cuối** (history gần nhất, câu user).
2. **Không chèn phần động vào đầu prompt** (ví dụ giờ hiện tại, tên người dùng, `session_id`) — chỉ cần một ký tự đổi ở đầu là tiền tố sau đó mất cache. Đưa dữ liệu động vào cuối hoặc vào message user.
3. Giữ **định dạng history ổn định** (đừng viết lại/tóm tắt history mỗi lượt; làm vậy phá cache từ điểm đổi). Nếu phải tóm tắt, làm theo ngưỡng (ví dụ mỗi N lượt) chứ không mỗi lượt.
4. Warm-up: gửi một request giả lúc khởi động để nạp model, kernel và cache; tránh cold-start ở lượt đầu (**Reported** khuyến nghị warm-up mọi model).[^stack]

### 12.3.5 Tắt thinking

Các model có chế độ reasoning (Qwen3, Qwen3.5 và nhiều model khác) có thể sinh hàng trăm đến hàng nghìn token "suy nghĩ" trước khi trả lời. Trong voice, những token đó:

- cộng thẳng vào độ trễ trước mệnh đề đầu tiên;
- nếu rò rỉ vào luồng TTS thì bot **đọc to quá trình suy luận**.

Report nói reasoning mode của Qwen3.5 tốn token nên voice phải dùng non-thinking; với vLLM tắt bằng `extra_body={"chat_template_kwargs": {"enable_thinking": False}}` (**Reported**).[^stack] Cách tắt phụ thuộc backend:

| Backend | Cách thường gặp | Ghi chú |
|---|---|---|
| vLLM chat completions | `chat_template_kwargs.enable_thinking=false` | Cần chat template hỗ trợ; template chèn sẵn khối think rỗng vào prompt |
| Qwen3 (bản hybrid 04/2025) soft switch | `/no_think` trong message | Chỉ là quy ước của Qwen3 hybrid, không áp dụng chung; model vẫn sinh khối `<think></think>` rỗng nên chunker phải lọc |
| Chọn model non-thinking | Ví dụ `Qwen3-*-Instruct-2507` | Bản Instruct-2507 chỉ có chế độ non-thinking (kiến thức nền theo model card, chưa có trong wiki); HF s2s dùng bản này cho cấu hình local[^s2s] |
| OpenAI-style reasoning | Chat Completions: `reasoning_effort`; Responses: `reasoning: {"effort": ...}` | Giá trị thấp nhất (`none`/`minimal`) tuỳ model. HF s2s ghi nhận cần `--responses_api_reasoning_effort none` khi provider bỏ qua `enable_thinking` trên đường Responses (**Reported**)[^s2s] |
| llama.cpp | Tắt reasoning ở server/template | HF s2s ví dụ dùng "reasoning off" (**Reported**)[^s2s] |

Hai lưu ý (**Synthesis**): (1) luôn **kiểm chứng bằng log** rằng output không còn khối `<think>…</think>`; (2) thêm lớp bảo vệ ở chunker: nếu thấy thẻ think, bỏ toàn bộ nội dung trong thẻ, đừng gửi cho TTS.

---

## 12.4 Prompt cho hội thoại nói

### 12.4.1 Khác biệt cốt lõi: người **nghe**, không **đọc**

| Chiều | Chat hiển thị | Hội thoại nói |
|---|---|---|
| Độ dài | Có thể dài, có cấu trúc | **1–3 câu ngắn**; người nghe không "lướt" được |
| Định dạng | Markdown, bảng, bullet, code | **Không** markdown/bảng/emoji/URL |
| Liệt kê | Bullet | Nói "thứ nhất… thứ hai…", tối đa 2–3 ý |
| Số/đơn vị | `1.250.000đ`, `15/03` | Cứ để chuỗi gốc cũng được, nhưng normalizer phải đọc đúng (Chương 19); prompt có thể yêu cầu LLM viết sẵn dạng đọc được nếu domain hẹp |
| Xác nhận | Người dùng đọc lại được | Phải **nhắc lại và xác nhận** thông tin quan trọng |
| Không chắc | Có thể trả lời dài kèm cảnh báo | **Hỏi lại ngắn** |
| Lỗi | Sửa bằng thao tác nhìn | Người nghe không "cuộn lên" được; phải ngắn và rõ ngay lần đầu |

Thiết kế của wiki yêu cầu prompt hệ thống nói chuyện: 1–3 câu ngắn, không markdown/emoji/bảng/URL, hỏi lại khi không chắc đã nghe đúng, tắt thinking (**Reported**).[^design] Blueprint thêm: số và đơn vị phát âm được, không mô tả quá trình suy luận, câu ngắn (**Reported**).[^blueprint]

### 12.4.2 Mẫu system prompt (Synthesis, cần tinh chỉnh theo domain)

```text
Bạn là trợ lý giọng nói tiếng Việt. Câu trả lời của bạn sẽ được ĐỌC TO bằng
giọng nói, không hiển thị trên màn hình.

Quy tắc:
- Trả lời bằng 1–3 câu ngắn, tự nhiên như nói chuyện. Mỗi câu dưới ~25 từ.
- Không dùng markdown, gạch đầu dòng, bảng, emoji, ký hiệu đặc biệt, URL.
- Khi cần liệt kê, nói "một là…, hai là…" và tối đa 3 ý.
- Viết số, tiền, ngày, giờ theo cách người ta nói thành lời.
- Không nhắc lại câu hỏi dài dòng, không mở đầu bằng "Tất nhiên rồi!" kiểu máy móc.
- Nếu câu của người dùng nghe vô nghĩa, quá ngắn, hoặc có thể bị nghe sai,
  hãy hỏi lại ngắn gọn thay vì đoán.
- Với số điện thoại, số tiền, tên riêng, ngày giờ: nhắc lại để xác nhận trước khi hành động.
- Không giải thích quá trình suy nghĩ.
```

### 12.4.3 Vì sao phải "hỏi lại khi không chắc"

ASR sai là nguồn lỗi thật (Chương 11: hallucination, đồng âm khác dấu, số nhầm). LLM không biết nó nhận text sai; nếu không được dặn, nó **đoán và trả lời tự tin** → tệ hơn không trả lời. "Hỏi lại khi không chắc" biến lỗi ASR thành một lượt làm rõ rẻ. Có hai cấp:

1. **Cấp prompt:** dặn LLM.
2. **Cấp gateway (an toàn hơn):** nếu validity gate nghi ngờ transcript (confidence thấp, rơi vào blacklist hallucination, quá ngắn), gateway **không gọi LLM** mà phát câu hỏi lại soạn sẵn (ví dụ "Xin lỗi, bạn nói lại giúp mình được không?"). Cách này không phụ thuộc LLM có nghe lời hay không (**Synthesis**).

### 12.4.4 Truyền metadata để LLM biết mình đang nói chuyện bằng giọng

Có thể thêm vào message user (hoặc system) một tiền tố ngắn như `[giọng nói, ASR confidence thấp]`. Lợi ích: LLM chủ động xác nhận. Rủi ro: tốn token, và mô hình có thể lặp lại tiền tố; cần test. Đây là ý tưởng thiết kế (**Synthesis**, chưa có bằng chứng trong wiki).

### 12.4.5 Bản sắc, giọng điệu, ngôn ngữ

- **Xưng hô tiếng Việt** ("dạ", "ạ", "anh/chị/bạn") là một phần persona; hãy cố định trong system prompt để giọng nhất quán giữa các lượt.
- **Code-switch:** prompt nên nói rõ cách xử lý từ tiếng Anh (giữ nguyên nếu TTS đọc được; VieNeu được báo xử lý được, **Reported**).[^design]
- **Ngôn ngữ trả lời:** nếu nhiều ngôn ngữ, HF s2s mặc định lấy mã ngôn ngữ TTS từ transcript của người dùng, hoặc bật `--detect_llm_output_language` để nhận dạng từng chunk trả lời (**Reported**).[^s2s] Với tiếng Việt thuần, nên **ép cố định** ngôn ngữ TTS và nhắc LLM "luôn trả lời bằng tiếng Việt".

### 12.4.6 Những lỗi prompt thường gặp

| Triệu chứng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| Bot đọc "sao sao" hay "gạch đầu dòng" | LLM sinh markdown | Prompt + strip ký tự markup ở chunker (blueprint nhắc strip `#`, `**`, bảng, URL; **Reported**)[^blueprint] |
| Trả lời quá dài | Prompt thiếu giới hạn; model "nhiệt tình" | Giới hạn trong prompt; `max_tokens` chỉ là chốt an toàn |
| Bắt đầu bằng đoạn "Chắc chắn rồi!" lặp lại | Style mặc định của model | Cấm trong prompt; few-shot 2–3 ví dụ |
| Bot trả lời lan man khi ASR sai | Không có luật "hỏi lại" | Xem §12.4.3 |
| Đọc nhầm số/ngày | Normalizer/lexicon, không phải LLM | Xem Chương 19; đừng sửa bằng prompt nếu lỗi nằm ở normalizer |

---

## 12.5 Quản lý history và ngắt lời

### 12.5.1 Nguyên tắc: history phải phản ánh **cái người dùng đã nghe**

Khi bị ngắt giữa chừng, LLM có thể đã sinh ra 3 câu nhưng TTS mới phát hết câu 1 và nửa câu 2. Người dùng chỉ nghe nửa đó. Nếu history lưu cả 3 câu, ở lượt sau LLM tin rằng người dùng đã nghe cả ba, và có thể nói "như tôi đã nói ở trên…" về thứ họ chưa nghe. Wiki quy định: **chỉ lưu phần đã thực sự phát**, kèm tag `[bị ngắt]` (**Reported**).[^design][^barge][^stack]

Trình tự khi ngắt (**Reported**, từ §7.3 của thiết kế):[^design]

1. `generation_id++`.
2. Huỷ LLM stream; huỷ request TTS (HTTP/WS); xoá các câu đang xếp hàng.
3. Gửi `{"type":"clear"}` / `audio_cancel` để client flush buffer AudioWorklet.
4. Ghi vào history **phần đã phát** + `[bị ngắt]`.
5. Client bỏ mọi chunk thuộc generation cũ.

Phác thảo async của nguồn blueprint (tóm trong trang barge-in) còn ghi: worker LLM thoát vòng lặp token khi `generation_id` bị supersede và **không append** câu bị bỏ vào history (**Reported**).[^barge]

### 12.5.2 "Đã phát" nghĩa là gì: chỉ chính xác tới đâu?

Có ba mức độ chi tiết, tuỳ độ phức tạp:

| Mức | Nguồn thông tin | Độ chính xác | Ghi chú |
|---|---|---|---|
| **A. Theo chunk** | Server biết chunk nào đã gửi xuống client | Thô; chunk đã gửi ≠ đã phát | Dễ nhất; đủ cho MVP |
| **B. Theo offset phát (played offset)** | Client báo `played_ms` hoặc số sample đã đưa ra loa | Trung bình | Cần giao thức báo ngược |
| **C. Theo từ** | Alignment giữa token/từ và audio (forced alignment hoặc timestamp từ TTS) | Tốt nhất | Hiếm có ở TTS tiếng Việt |

Wiki nhận xét: nếu không có alignment giữa token và audio, **chỉ khẳng định được played offset, không khẳng định được chính xác từ nào đã phát**; `conversation.item.truncate` của OpenAI Realtime (và HF s2s) là điểm nối tự nhiên cho việc này (**Synthesis / Reported**).[^design] Lưu ý thêm: ở HF s2s engine, `conversation.item.truncate` hiện được chấp nhận như **no-op không phản hồi** cho SDK stock vì playback do client sở hữu và việc huỷ đã loại bỏ phần chưa phát (**Reported**).[^engine] Nghĩa là nếu muốn truncate thật ở lớp history, gateway của bạn phải tự làm.

**Hệ quả thực tế (Synthesis):** chiến lược an toàn là *cắt tại ranh giới chunk đã chắc chắn phát xong*. Chunk đang dở nên bị coi là "đã phát một phần": hoặc bỏ hẳn, hoặc cắt theo tỷ lệ `played_ms / chunk_ms` rồi lùi về ranh giới từ gần nhất, cộng `[bị ngắt]`.

### 12.5.3 Đo hai thời điểm khác nhau

Wiki yêu cầu đo cả hai (**Synthesis**):[^design]

1. **User-speech → bot audio dừng** (nghe được) — cảm nhận của người dùng.
2. **Thời gian giải phóng compute** — LLM/TTS thật sự ngừng sinh, slot GPU được trả.

Nếu (2) ≫ (1), hệ thống bị "lãng phí ngầm" và phiên khác trên cùng GPU bị chậm.

### 12.5.4 Đưa tag `[bị ngắt]` vào prompt thế nào

Tag là ký hiệu cho LLM biết câu trước chưa nói hết. Hai lựa chọn:

- Giữ nguyên chuỗi `[bị ngắt]` ở cuối message assistant. Dễ, nhưng LLM có thể nhại lại tag trong câu trả lời mới → TTS đọc "bị ngắt". Cần chunker lọc (**Synthesis**).
- Hoặc dùng một message hệ thống kiểu "Lượt trước của bạn bị người dùng ngắt sau câu '…'" đặt trước lượt user mới. Ít rò rỉ hơn.

Dù chọn gì, mô tả trong system prompt: "Nếu lượt trước bị ngắt, đừng lặp lại toàn bộ; trả lời trực tiếp điều người dùng vừa nói".

### 12.5.5 Ngắt vì sao? Ý định khác nhau

Không phải ngắt nào cũng giống nhau (**Synthesis**):

| Loại | Ví dụ | Hành vi gợi ý |
|---|---|---|
| **Backchannel** | "ừ", "vâng", "ok" | Không ngắt bot; cũng không đưa vào history như một lượt. Nhưng wiki cảnh báo đừng mặc định coi mọi "ừ/vâng/ok" là backchannel; trong một số domain đó chính là lời **xác nhận** (**Synthesis**)[^design] |
| **Ngắt để sửa** | "không, ý tôi là…" | Huỷ, trả lời lượt mới |
| **Ngắt để dừng** | "thôi, dừng lại" | Huỷ, có thể không cần trả lời dài |
| **Ngắt nhầm** (nhiễu, echo, người khác) | tiếng TV, tiếng nói xung quanh | Gating (duration gate, speaker lock) để tránh; nếu vẫn lọt, đã mất lượt — cần cơ chế "tiếp tục" |

Gating chống ngắt nhầm thuộc Chương 17; ở đây chỉ cần nhớ: **mọi lần ngắt nhầm đều ghi một `[bị ngắt]` giả vào history**, và có thể làm LLM hiểu sai bối cảnh. Nếu hệ thống phát hiện ngắt nhầm sau đó (ví dụ ASR cho transcript rỗng/bị lọc), cân nhắc **khôi phục** (resume) hoặc không ghi `[bị ngắt]`.

### 12.5.6 Transcript revision và history

ASR có thể revise (Chương 11): partial thay đổi, final khác partial. Quy tắc (**Synthesis**, khớp với tư tưởng turn tracker của HF s2s):

- **History chỉ chứa transcript đã commit**, không bao giờ partial.
- Nếu người dùng **nói tiếp** sau một lần commit chưa phát đầu ra (reopen), phải **thay** (supersede) message user cũ bằng transcript gộp mới, thay vì thêm hai message liên tiếp.
- Nếu LLM đã bắt đầu trả lời lượt đã bị supersede: huỷ, và message assistant dở dang **không** vào history.

HF s2s hiện thực ý này qua turn tracker `LISTENING/SOFT_ENDED/ANSWERING/CLOSED`: turn complete bắt đầu STT/LLM ngay với speculative reopen 800 ms; nói tiếp thì mở lại turn như revision mới và bỏ việc chưa commit (**Reported**).[^design]

### 12.5.7 Độ dài history và tóm tắt

- Blueprint của report: giữ khoảng **10–20 lượt gần nhất** và tóm tắt các lượt cũ hơn (**Reported**).[^stack]
- HF s2s có cờ `--chat_size` (mặc định 30) cho kích thước hội thoại giữ lại (**Reported**).[^s2s]
- Lưu ý về tương tác với prefix cache (§12.3.4): tóm tắt làm đổi tiền tố → mất cache. Tóm tắt theo ngưỡng, không mỗi lượt.
- Với thoại, tóm tắt cần giữ **thực thể** (tên, số, lựa chọn đã chốt) hơn là giữ văn phong.
- **Không** ghi transcript vào log vận hành mặc định; HF s2s mặc định content-free, `--log_transcripts` là opt-in (**Reported**).[^design] Xem Chương 23.

---

## 12.6 Speculative generation, tool call và commit

### 12.6.1 Ý tưởng speculative

Độ trễ lớn nhất phía trước LLM là chờ xác nhận hết lượt nói (endpoint). **Speculative generation** là bắt đầu chạy ASR/LLM *trước* khi chắc chắn lượt đã kết thúc, rồi huỷ nếu người dùng nói tiếp. Wiki có hai biến thể (**Reported**):

- Preemptive ASR + LLM khi VAD im khoảng **200 ms**, huỷ nếu user nói tiếp.[^stack]
- Smart Turn "complete" → chạy STT/LLM ngay, với **speculative reopen 800 ms** trước khi commit output.[^design]

Thiết kế cảnh báo: preemptive có thể ẩn một phần latency nhưng **phải cancel khi user nói tiếp** (**Synthesis**).[^design]

### 12.6.2 Ba trạng thái của đầu ra LLM

```text
SPECULATIVE  : LLM đang chạy trên transcript chưa chắc kết thúc
               → có thể chuẩn bị sẵn text/TTS, chưa phát (hoặc giữ ở "gate")
COMMITTED    : turn đã chốt (hết cửa sổ reopen, hoặc turn tracker đóng)
               → được phát audio, được ghi history, được chạy tool
DISCARDED    : revision đổi / user nói tiếp / ngắt
               → huỷ stream, bỏ buffer, không ghi gì
```

Quy tắc bất biến (**Synthesis**):

1. **Không phát audio từ đầu ra SPECULATIVE** trừ khi bạn chấp nhận rủi ro "nói rồi phải im giữa chừng". HF s2s gate output đến khi hết grace (max wait 2 s với turn incomplete) (**Reported**).[^design]
2. **Không ghi history** từ đầu ra SPECULATIVE.
3. **Không chạy tool có side effect** từ đầu ra SPECULATIVE (§12.6.3).
4. Khi revision đổi (transcript khác), **huỷ chứ đừng "sửa tiếp"**: LLM không thể biên tập một câu trả lời đang sinh dựa trên transcript cũ.

**Output gate quyết định latency thay cho tốc độ LLM.** Khi LLM chạy speculative trong grace trước commit, thiết kế ước lượng (**Synthesis**):[^design]

```text
v2v ≈ (cuối tiếng user → soft-end) + max(output-hold, ASR + LLM tới mệnh đề đầu)
      + TTS tới audio đầu + transport/playback
```

Với default HF s2s, output-hold là 800 ms cho lượt complete và tới 2 s cho lượt incomplete. Hệ quả cho LLM: nếu ASR + TTFC đã nhỏ hơn output-hold, đổi sang LLM nhanh hơn **không** giảm độ trễ nghe được. Hãy đo riêng output-hold và thời điểm response sẵn sàng trước khi đổi model; chunker phải nằm ở consumer của LLM stream chứ không chia câu sau khi đã nhận đủ câu trả lời.[^design]

### 12.6.3 Tool call và side effect

Tool call (hàm do LLM gọi: tra cứu, đặt lịch, ghi CRM, chuyển tiền) là nơi sai lầm tốn kém nhất. Phân loại:

| Loại tool | Ví dụ | Chạy trên SPECULATIVE? |
|---|---|---|
| **Read-only, idempotent, rẻ** | tra thời tiết, tra giờ mở cửa | Có thể, nếu kết quả chỉ cache và bỏ được |
| **Read-only nhưng đắt/giới hạn tần suất** | gọi API tính phí | Không |
| **Write / side effect** | tạo lịch hẹn, gửi tin, ghi CRM, thanh toán | **Tuyệt đối không** — chỉ sau commit |

Lý do kỹ thuật (**Synthesis**):

- Partial/speculative transcript có thể sai ("năm triệu" thành "mười lăm triệu"; hallucination).
- User có thể nói tiếp ("…à khoan, đổi sang thứ bảy").
- Tool không huỷ được sau khi chạy.

**Mẫu an toàn:**

1. Với tool ghi: đòi **xác nhận bằng lời** ("Mình đặt lịch thứ sáu lúc chín giờ, đúng không ạ?") rồi chạy khi người dùng đồng ý. Đây là chỗ mà "ừ/vâng" **không** được coi là backchannel (§12.5.5).
2. Dùng **idempotency key** = `(session_id, utterance_id, revision_id, tool_call_index)` để chống chạy lặp khi retry.
3. Chỉ chạy khi `commit` và `generation_id` hiện hành khớp với `generation_id` của tool call.
4. Sau khi chạy, trả **kết quả** vào history dưới vai trò tool, và để LLM nói kết quả.
5. Thời gian chạy tool là độ trễ cộng thêm; bot nên nói câu đệm ngắn ("Đợi mình kiểm tra một chút nhé") nếu tool > ~1 s (**Synthesis**).

**An toàn dữ liệu nhạy cảm:** số điện thoại, số tiền và tên riêng là các thực thể ASR hay sai nhất; Chương 11 §11.9 nêu vì sao cần gate/xác nhận. Nên **bắt buộc xác nhận lại** các thực thể này trước tool ghi.

### 12.6.4 Streaming tool call và độ trễ

Khi LLM quyết định gọi tool, nó thường không sinh text trước. Nghĩa là TTFC ≈ thời gian đến tool call + thời gian chạy tool + thời gian sinh câu trả lời. Hai cách giảm:

- Cho LLM sinh câu đệm trước tool call (một chunk ngắn), đặt trong prompt.
- Chạy song song tool read-only độc lập nếu LLM phát nhiều tool call cùng lúc.

---

## 12.7 Mô phỏng vòng điều khiển (Reproduced)

Script ở phụ lục dựng đúng các cơ chế ở trên với LLM giả: stream token, chunker 2 luật, `generation_id`, hàng đợi TTS, và ngắt lời giữa chừng. Kết quả đã chạy:

```text
  first chunk @ 355 ms: 'Dạ, bạn có thể đổi lịch hẹn sang thứ sáu.'
history: [('user', 'đổi lịch giúp tôi'),
          ('assistant', 'Dạ, bạn có thể đổi lịch hẹn sang thứ sáu. Khung giờ còn trống là chín giờ sáng và hai giờ chiều. [bị ngắt]')]
```

Đọc kết quả:

- LLM giả chờ 150 ms rồi sinh ~20 ms/token (token đầu ra ở ~170 ms). Chunk đầu (10 token) được flush sau **~355 ms** (chạy lại 3 lần: 353–354 ms) thay vì phải chờ cả câu trả lời (29 token, xong ở ~730 ms). Đây chỉ minh hoạ nguyên lý, không phải số của model thật.
- "Dạ," không bị flush riêng vì luật dấu phẩy chỉ áp dụng khi dấu phẩy nằm sau ký tự thứ 15, nên bẫy "chunk đầu quá ngắn" ở §12.3.2 được tránh.
- Sau khi ngắt ở 900 ms, history chỉ chứa hai chunk đã phát xong (kết thúc ~855 ms) cùng tag `[bị ngắt]`. Chunk 3 ("Bạn muốn chọn khung giờ nào ạ?") đang phát dở lúc ngắt nên bị bỏ hẳn.
- Giới hạn của mô phỏng: nó chấm "đã phát" theo **chunk** (mức A ở §12.5.2), và thời gian phát chunk là hằng số; không có mạng, buffer client hay alignment.

---

## 12.8 Contention GPU khi LLM chạy chung ASR/TTS

### 12.8.1 Bản chất vấn đề

Ba workload cùng dùng một GPU, nhưng có profile khác nhau (**Synthesis**):

| Workload | Profile | Nhạy cảm gì |
|---|---|---|
| **ASR streaming** | Nhiều tác vụ nhỏ, đều, theo chunk (80–1120 ms) | Jitter: chunk đến mà GPU bận → trễ partial |
| **LLM** | Prefill nặng + decode bộ nhớ bị chặn (memory-bound) | KV cache chiếm VRAM; prefill dài làm "chặn" các tác vụ khác |
| **TTS** | Decode tự hồi quy hoặc diffusion; cần đều để không underrun | Gián đoạn → khe im lặng |

Khi chúng cạnh tranh:

- **VRAM:** weights + KV cache + activations cộng lại. Report ước lượng với GPU 24 GB: Whisper turbo fp16 ~2–3 GB, VieNeu GPU ~2–3 GB, phần còn lại cho LLM và KV cache; trên 12 GB dùng `int8_float16` (**Reported**, chưa đo).[^design]
- **Compute:** kernel LLM prefill dài có thể làm chậm kernel TTS; TTS bị trễ → underrun.
- **Queue:** continuous batching của vLLM tối ưu throughput LLM nhưng không biết deadline thời gian thực của TTS/ASR.

Wiki lưu ý rõ: external LLM nằm ngoài scope nhưng phải tính contention nếu cùng GPU, và shared-GPU ASR/TTS/LLM nằm trong gate đánh giá tải (**Reported / Synthesis**).[^design]

### 12.8.2 Các cấu hình đặt GPU (từ wiki)

- **Một GPU nhỏ:** Silero trên CPU, Whisper nhỏ trên GPU, LLM quantized qua llama.cpp hoặc vLLM, TTS 0.6B trên GPU; đừng co-host Whisper lớn + LLM lớn + TTS lớn khi chưa đo (**Reported**).[^blueprint]
- **Ba GPU:** tách Whisper+Silero, LLM, TTS lên thiết bị riêng (**Reported**).[^blueprint]
- **Community:** một cấu hình 3090 giữ TTS trên CPU để nhường card 24 GB cho phần còn lại — khác phương án all-GPU của report (**Reported**, anecdote).[^community]
- Docker Compose, mỗi model một process/owner, tách environment để tránh xung đột torch/CUDA (**Synthesis**).[^design]

### 12.8.3 Giảm contention (Synthesis)

1. **Tách thiết bị** khi có thể; quy tắc hiệu quả nhất.
2. **Giới hạn chia sẻ VRAM** của LLM (ví dụ `--gpu-memory-utilization` ở vLLM) để chừa chỗ cho ASR/TTS; tránh OOM ở thời điểm tải đỉnh.
3. **Giới hạn độ dài prompt và `max_tokens`**: prefill ngắn, decode ngắn.
4. **Ưu tiên theo deadline:** GPU không có scheduler theo deadline giữa các process. Các công cụ có sẵn chỉ gần đúng: CUDA stream priority (chỉ trong cùng process), MPS với giới hạn % SM cho từng client, hoặc MIG chia cứng GPU (chỉ trên GPU datacenter). Vì vậy tách GPU thường đơn giản và chắc chắn hơn.
5. **Hạ độ chính xác LLM** (AWQ/GPTQ/GGUF Q4) để giảm VRAM và băng thông.
6. **Đo trong tải thật:** concurrency 1/4/8/16, warm/cold, sustained và simultaneous start; chỉ tăng concurrency khi P95 và cadence vẫn đạt, đừng suy từ throughput H100 trong paper (**Reported** gate đánh giá tải).[^design]

### 12.8.4 Hosted LLM: đổi contention lấy network và privacy

Dùng LLM hosted (OpenAI, OpenRouter, HF providers) loại bỏ contention GPU nhưng thêm:

- RTT mạng và biến thiên của provider (TTFT P95 thường xấu hơn P50);
- quyền riêng tư: HF s2s ghi nhận chế độ "local speech with hosted LLM" **gửi transcript, instructions và history tới provider** trong khi audio micro và tổng hợp ở local (**Reported**);[^s2s]
- rate limit, lỗi 429/5xx cần retry/backoff và câu fallback.

Không có con số universal; hãy đo TTFT P50/P95 từ chính vị trí triển khai.

---

## 12.9 Hướng khác: đưa audio thẳng vào LLM, và model full-duplex

Để hiểu giới hạn của cascade, cần biết hai hướng thay thế (chỉ tham khảo; thiết kế chính chọn cascade cho tiếng Việt):

1. **Direct audio input:** HF s2s hỗ trợ `--stt none --llm_backend chat-completions`, gửi từng đoạn VAD thẳng tới LLM nhận audio. Không hỗ trợ với `responses-api`; model mặc định chỉ nhận text/ảnh nên phải đặt `--model_name` là model nhận audio (**Reported**).[^s2s] Với tiếng Việt, khả năng hiểu giọng nói của LLM audio phải được **đo riêng**; cộng đồng cũng báo có người bỏ STT bằng một Omni model trong llama.cpp, đổi lại phải dùng LLM nhỏ hơn (**Reported**, anecdote).[^design]
2. **End-to-end full-duplex:** [PersonaPlex 7B](../wiki/personaplex-7b-v1.md) và [NemotronLabs VoiceChat 11B](../wiki/nvidia-nemotronlabs-voicechat-11b.md) khai báo `language: en`; Qwen3-Omni nghe được tiếng Việt nhưng không nói được tiếng Việt (**Reported**).[^design] Trong họ này, turn-taking nằm *bên trong* model, không qua cơ chế cancel của cascade.

Vì vậy, với tiếng Việt, cascade vẫn là con đường đề xuất, và chương này mô tả đúng cách giữ LLM "tuân thủ" kỷ luật của cascade.

---

## 12.10 Chọn kích thước và backend (tham khảo ngắn)

Đề cương dặn chương này không đi sâu vào việc chọn model. Để hoàn chỉnh, đây là những gì wiki ghi nhận (đều **Reported**, nằm ngoài phạm vi thiết kế chính):

| Phần cứng | Gợi ý của report | Ghi chú |
|---|---|---|
| GPU 24 GB | Qwen3-8B AWQ hoặc Qwen3.5-9B 4-bit | Qua vLLM, thinking off[^stack] |
| GPU 12 GB | Qwen3-4B hoặc Qwen3.5-4B | [^stack] |
| GPU server nhiều phiên | Qwen3-30B-A3B (MoE, ~3B active) | TTFT tốt với continuous batching[^stack] |
| Local trong HF s2s | `Qwen/Qwen3-4B-Instruct-2507` FP16 qua `transformers`, ~8 GB weights | Cấu hình đầy đủ cần ~24 GB VRAM cho cả LLM + speech[^s2s] |
| llama.cpp | Ví dụ Gemma 4 `Q4_0` (~4.6 GB), context 8k, reasoning off | Ghép qua `--responses_api_base_url`[^s2s] |

**Cảnh báo:** các kích thước trên chưa được benchmark tiếng Việt trong wiki; chất lượng tiếng Việt, tuân thủ prompt "nói chuyện" và tỷ lệ rò rỉ markdown phải được **đo bằng bộ prompt riêng** (§12.12). Backend và model có `stale_after: 2027-10-06`.

---

## 12.11 Gắn vào pipeline

| Quyết định trong thiết kế | Cơ sở trong chương này |
|---|---|
| §5.5: giao diện LLM = streaming text + `done` + `error` + `cancel` + `generation_id` | §12.2 |
| §5.5: system prompt cho nói chuyện | §12.4 |
| §5.5 / §7.3: chỉ lưu phần đã phát, tag `[bị ngắt]` | §12.5 |
| §7.3: cancel LLM, TTS, queue, client buffer | §12.2.3, §12.5.1 |
| §8.1: critical path "final ASR → mệnh đề có nghĩa đầu tiên → TTS"; output gate speculative | §12.3, §12.6.2 |
| §8.4: metric `asr_done→llm_first_token`, `first_sentence→tts_first_byte` | §12.11.1 |
| §8.3: prefix cache, preemptive ASR+LLM, warm-up | §12.3.4, §12.6 |
| §9.2 / §10: VRAM và tải shared GPU | §12.8 |

### 12.11.1 Metric cần log mỗi lượt (đề xuất)

```text
llm.request_sent_t, llm.first_token_t, llm.first_clause_t, llm.done_t
llm.ttft_ms, llm.ttfc_ms, llm.tokens_out, llm.tokens_per_s
llm.prompt_tokens, llm.cached_prompt_tokens         # tỷ lệ trúng prefix cache
llm.finish_reason                                   # stop | length | tool_calls | cancelled | error
llm.cancel_requested_t, llm.compute_released_t      # (2) ở §12.5.3
llm.was_speculative, llm.discarded                  # tỷ lệ lãng phí speculative
tts.inter_chunk_gap_ms                              # underrun
history.interrupted_flag, history.played_chars
```

Wiki đã đề xuất monitoring per-turn `vad_end→asr_done`, `asr_done→llm_first_token`, `first_sentence→tts_first_byte` (**Reported**);[^stack] danh sách trên mở rộng cho phần LLM (**Synthesis**).

### 12.11.2 Vòng điều khiển rút gọn (Synthesis)

```text
on turn.soft_end(transcript, utt_id, rev_id):       # có thể chạy speculative
    gen = ++generation_id; state[gen] = SPECULATIVE
    messages = build(system, history, transcript)   # history chỉ gồm lượt đã commit
    for ev in llm.stream(messages):                 # SSE
        if gen != generation_id: llm.cancel(); return
        if ev.kind == text_delta:
            for chunk in chunker.feed(ev.text):     # lọc markup, <think>
                held[gen].append(chunk)             # giữ ở output gate
        elif ev.kind == tool_call: pending_tools[gen].append(ev)   # chưa chạy
        elif ev.kind == done: held[gen].append(chunker.flush())
        if state[gen] == COMMITTED: tts_queue.put_all(gen, held[gen].drain())
on turn.commit(gen):                                # hết grace, không reopen
    state[gen] = COMMITTED
    history.append(user, transcript)
    tts_queue.put_all(gen, held[gen].drain())
    for t in pending_tools[gen]: run_tool(t, idem_key(utt_id, rev_id, t.index))  # tool ghi: sau xác nhận bằng lời
on turn.reopen:                                     # user nói tiếp
    generation_id += 1; llm.cancel(); held.clear(); pending_tools.clear()
on barge_in:
    generation_id += 1; llm.cancel(); tts.cancel(); tts_queue.clear()
    client.send({"type": "clear"})
    history.append(assistant, played_text + " [bị ngắt]")
```

---

## 12.12 Quy trình thử một LLM mới cho voice

1. **Contract:** có streaming SSE ổn định không? Huỷ được thật không (compute dừng)? `finish_reason` đúng không? Tool-call streaming ổn định không?
2. **Thinking:** tắt được bằng cách nào? Log có `<think>` rò rỉ không?
3. **Latency:** TTFT, TTFC, tokens/s ở P50/P95, có/không có prefix cache, prompt 500/2000/4000 token, concurrency 1/4/8.
4. **Tuân thủ prompt nói chuyện:** bộ ≥ 50 prompt (tiếng Việt, tiếng lóng, số, tên riêng, code-switch, câu ASR hỏng). Đếm: tỷ lệ có markdown/emoji/URL, độ dài trung bình, tỷ lệ "hỏi lại" đúng chỗ, tỷ lệ đọc lại tag `[bị ngắt]`.
5. **Ngắt lời:** mô phỏng ngắt ở nhiều điểm, kiểm tra history và hành vi lượt sau.
6. **Tool:** idempotency, từ chối chạy khi chưa commit, xử lý lỗi tool.
7. **Tải chung GPU:** chạy cùng ASR + TTS thật, đo underrun và partial delay.
8. **Chất lượng tiếng Việt:** ngữ pháp, xưng hô, độ tự nhiên khi đọc to (nghe thử, không chỉ đọc).

---

## 12.13 Lỗi thường gặp (checklist)

| Triệu chứng | Nguyên nhân thường gặp | Chương liên quan |
|---|---|---|
| Độ trễ lượt đầu rất lớn | Cold start, chưa warm-up, model đang load | §12.3.4 |
| Lượt sau chậm dần | History dài, mất prefix cache, prefill tăng | §12.3.4, §12.5.7 |
| Bot đọc "suy nghĩ" | Thinking bật hoặc `<think>` rò rỉ | §12.3.5 |
| Đọc markdown, URL | Prompt thiếu, chunker không lọc | §12.4, Ch.19 |
| Bot nói tiếp nội dung cũ sau khi bị ngắt | Stream không huỷ hoặc chunk cũ lọt qua | §12.2.3, Ch.17 |
| Bot nhắc "như tôi đã nói" về thứ chưa phát | History lưu cả câu sinh ra | §12.5.1 |
| Bot đọc "bị ngắt" | Tag lọt sang output | §12.5.4 |
| Khe im lặng giữa các câu | Underrun: LLM chậm hoặc contention | §12.3.3, §12.8 |
| Đặt lịch/ghi CRM theo câu người dùng chưa nói xong | Tool chạy trên speculative | §12.6.3 |
| Trả lời tự tin trên transcript sai | Không có luật hỏi lại / gate | §12.4.3 |
| Hai lượt user liên tiếp trong history | Không supersede khi reopen | §12.5.6 |
| OOM ngẫu nhiên giờ cao điểm | KV cache + ASR + TTS vượt VRAM | §12.8 |
| Transcript nhạy cảm nằm trong log | Log bật mặc định | §12.5.7, Ch.23 |

---

## Đáp án tự kiểm tra

**Q1.** TTFT là thời gian từ lúc gửi request đến token đầu tiên. Người nghe chỉ cảm nhận **thời điểm âm đầu tiên**, nên thứ cần tối ưu là *time to first clause* (TTFT + thời gian sinh đủ ~1 mệnh đề), vì TTS có thể bắt đầu từ chunk đầu trong khi LLM sinh tiếp. Chờ cả câu trả lời cộng thêm toàn bộ thời gian decode vào độ trễ. Chunk đầu cũng không nên quá nhỏ (per-token) vì prosody gãy và khe hở nghe được.

**Q2.** Prompt nói chuyện: 1–3 câu ngắn, không markdown/emoji/bảng/URL, số/đơn vị đọc được, nhắc lại để xác nhận thực thể quan trọng, hỏi lại khi không chắc, không kể quá trình suy luận. Prompt hiển thị cho phép dài, có cấu trúc, liệt kê và định dạng, vì người đọc có thể lướt và cuộn.

**Q3.** Chỉ lưu phần đã thực sự phát, kèm `[bị ngắt]`, để history phản ánh điều người dùng đã nghe. Lưu cả câu sinh ra khiến LLM tin người dùng đã nghe phần chưa phát. Nếu không có alignment token↔audio thì chỉ chắc chắn ở mức chunk hoặc played offset.

**Q4.** Thinking thêm hàng trăm tới hàng nghìn token trước câu trả lời (tăng TTFC), và nếu rò rỉ thì TTS đọc ra. Cách tắt tuỳ backend: `chat_template_kwargs.enable_thinking=false` (vLLM chat), `/no_think`, `reasoning_effort`/`reasoning.effort` mức thấp nhất (API kiểu OpenAI), chọn bản model non-thinking, hoặc tắt reasoning ở server llama.cpp; luôn kiểm bằng log và lọc thẻ ở chunker.

**Q5.** Speculative generation là chạy ASR/LLM sớm (khi VAD im 200 ms, hoặc turn được đánh giá complete với reopen 800 ms) để ẩn latency. Phải discard khi người dùng nói tiếp, khi transcript revision đổi, hoặc khi bị ngắt; output speculative không được phát, ghi history, hay chạy tool trước commit.

**Q6.** Transcript speculative có thể sai hoặc chưa đủ; user có thể sửa ngay sau đó; tool có side effect không huỷ được. Chỉ chạy sau commit, có xác nhận bằng lời cho tool ghi, kèm idempotency key và kiểm tra `generation_id`.

**Q7.** Tranh chấp VRAM (weights + KV cache) và compute: prefill dài của LLM làm trễ partial ASR hoặc làm TTS underrun; batching của LLM không biết deadline realtime. Giảm bằng tách GPU, giới hạn VRAM LLM, prompt ngắn, quantization và đo dưới tải thực P95 (concurrency, warm/cold, underrun, độ trễ partial).

---

## Hạn chế và phạm vi bao phủ

- Toàn bộ số liệu về model LLM (kích thước, latency, VRAM) là **Reported** từ wiki và chưa được đo lại; không có benchmark tiếng Việt trên cùng stack.
- Wiki không chọn LLM chính và không có trang primary-source cho Qwen3/Qwen3.5; các khuyến nghị kích thước là report chưa neo vào nguồn gốc (**Synthesis**).
- Kiến thức về TTFT, prefix cache, continuous batching, hành vi thinking và quản lý tool call là kiến thức nền chung, không phải claim lấy từ nguồn wiki.
- Mô phỏng §12.7 dùng LLM giả với chunk tính theo ký tự và thời gian phát hằng số; không đo mạng, client buffer, alignment hay model thật.
- `conversation.item.truncate` được mô tả theo wiki về HF s2s (no-op cho SDK stock); chưa kiểm tra mã nguồn gốc.
- Giá trị số trong §12.4.2 (độ dài câu) và §12.6.3 (ngưỡng câu đệm 1 s) là đề xuất của tác giả, cần calibrate.
- Phần diarization/đa người nói, đa ngôn ngữ phức tạp và RAG không thuộc phạm vi chương này.

---

## Phụ lục chương

### Script mô phỏng vòng LLM → chunker → TTS có ngắt (`/tmp/ch12/llm_loop.py`, đã chạy)

```python
import asyncio, re, time

CLAUSE_END = re.compile(r'[.?!…;:\n]')
def chunker(buf, first):
    """Trả (chunk, phần còn lại) hoặc (None, buf)."""
    m = CLAUSE_END.search(buf)
    if m and m.end() >= 8:
        return buf[:m.end()].strip(), buf[m.end():]
    if first and len(buf) >= 25 and ',' in buf[15:]:
        i = buf.index(',', 15) + 1
        return buf[:i].strip(), buf[i:]
    return None, buf

async def fake_llm(text, gen_id, ttft=0.15, tps=0.02):
    await asyncio.sleep(ttft)
    for tok in text.split(' '):
        await asyncio.sleep(tps)
        yield tok + ' '

class Session:
    def __init__(s):
        s.gen = 0; s.history = []; s.tts_q = asyncio.Queue(); s.played = []
    async def respond(s, user, reply):
        s.gen += 1; my = s.gen
        s.history.append(("user", user))
        buf, first, produced = "", True, []
        t0 = time.perf_counter()
        async for tok in fake_llm(reply, my):
            if my != s.gen: return            # bị supersede -> dừng, không ghi history
            buf += tok
            c, buf = chunker(buf, first)
            if c:
                if first: print(f"  first chunk @ {1000*(time.perf_counter()-t0):.0f} ms: {c!r}")
                first = False
                await s.tts_q.put((my, c)); produced.append(c)
        if buf.strip(): await s.tts_q.put((my, buf.strip()))
    async def tts_worker(s, per_chunk=0.25):
        while True:
            g, c = await s.tts_q.get()
            if g != s.gen: continue           # stale
            await asyncio.sleep(per_chunk)    # "phát" chunk
            if g == s.gen: s.played.append(c)
    def interrupt(s):
        s.gen += 1
        while not s.tts_q.empty(): s.tts_q.get_nowait()
        txt = " ".join(s.played)
        s.history.append(("assistant", txt + " [bị ngắt]"))
        s.played = []

async def main():
    s = Session(); w = asyncio.create_task(s.tts_worker())
    reply = ("Dạ, bạn có thể đổi lịch hẹn sang thứ sáu. Khung giờ còn trống là chín giờ sáng và hai giờ chiều. "
             "Bạn muốn chọn khung giờ nào ạ?")
    r = asyncio.create_task(s.respond("đổi lịch giúp tôi", reply))
    await asyncio.sleep(0.9)                  # user ngắt lời giữa chừng
    s.interrupt(); await r
    print("history:", s.history)
    w.cancel()
asyncio.run(main())
```

Điểm cần tự thử: đổi `per_chunk` và thời điểm ngắt để xem history thay đổi; thử bỏ kiểm tra `g != s.gen` ở `tts_worker` để thấy chunk cũ lọt qua sau ngắt.

### Liên kết sang chương khác

- Chương 10 (VAD, endpointing, turn detection): cơ chế quyết định `turn.commit` và speculative reopen.
- Chương 11 (ASR): transcript revision, gate và confidence, đầu vào của LLM.
- Chương 13 (TTS) và Chương 19 (cầu text→speech): chunker, normalizer, lexicon — nơi đầu ra LLM trở thành âm thanh.
- Chương 17 (turn-taking và cancellation): gating ngắt lời, `generation_id` toàn pipeline.
- Chương 18 (async/streaming): hàng đợi, backpressure, huỷ task.
- Chương 20 (latency): ngân sách và đo end-to-end.
- Chương 23 (license, privacy, bảo mật): log transcript, hosted LLM, tool và quyền.

[^design]: [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) — §5.5 (giao diện LLM, chunker, prompt), §7.3 (barge-in, gating, played offset), §8.1 (critical path, output gate speculative), §8.2–8.4 (latency, monitoring), §9.2 (VRAM), §10 (gate tải). Dựa trên [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md).
[^blueprint]: [Cascaded Voice-Agent Blueprint](../wiki/cascaded-voice-agent-blueprint.md) — Turn flow and defaults (LLM call, sentence-buffered TTS); Hardware tiers and placement; Common failures and fixes. Nguồn: LLM-generated report, chưa đo.
[^stack]: [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md) — LLM choice and invocation (kích thước, `enable_thinking`, history 10–20 lượt, `[bị ngắt]`); latency budget (LLM TTFT + chunk đầu 150–350 ms); optimizations (prefix cache, preemptive ASR+LLM, warm-up); hardware tiers; monitoring.
[^barge]: [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md) — Interruption procedure (`generation_id`, LLM worker thoát khi superseded, không append history); duration-gated barge-in.
[^s2s]: [HF Speech-to-Speech Pipeline](../wiki/speech-to-speech-pipeline.md) — LLM backend selection (`responses-api` vs `chat-completions`, thinking, direct audio input); Quickstart configurations (privacy khi hosted LLM, VRAM); `--chat_size`; language detection.
[^engine]: [Speech-to-Speech Realtime Engine](../wiki/speech-to-speech-realtime-engine.md) — Realtime event surface: `conversation.item.truncate` (no-op cho SDK stock), `response.cancel`, per-session pipeline threads và commit revision.
[^community]: [Community-Reported STT-LLM-TTS Pipeline Wiring](../wiki/community-stt-llm-tts-pipeline.md) — cấu hình HTTP-service split trên một GPU 24 GB (anecdote, chưa kiểm chứng).
