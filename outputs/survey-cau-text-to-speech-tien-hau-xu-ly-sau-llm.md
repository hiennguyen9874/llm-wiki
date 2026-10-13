# Survey công cụ tiền/hậu xử lý giữa LLM và TTS: cầu text → speech (không gồm model TTS)

**Cách tra cứu.** Wiki đang ở trạng thái populated, khoảng 212 concept. Tôi đã đọc `SCOPE.md`, `wiki/index.md` và Chương 19 để lấy ngữ cảnh, rồi grep theo các nhóm từ khóa: normaliz, G2P/phonemi, chunk/sentence, SSML/markup, think, Lingua/LID, watermark, resample, playback/buffer, caption/timestamp, round-trip, WeTextProcessing/ttsfrd. Sau đó tôi đọc khoảng 35 concept liên quan. **Tôi không mở `raw/`.** Mọi claim bên dưới lấy từ wiki và là **Reported**, trừ chỗ ghi khác. Không có verification event nào mới.

Khung tham chiếu theo Chương 19: `LLM stream → ThinkFilter → Chunker → pre-lexicon → Normalizer → post-lexicon → TTS adapter → hậu xử lý audio → playback/barge-in`.

---

## 1. Kiểm soát output LLM (trước chunker)

| Thành phần | Nội dung trong wiki | Nguồn |
|---|---|---|
| Tắt thinking | HF s2s có `responses_api_disable_thinking` và `responses_api_reasoning_effort` (gửi `extra_body.reasoning_effort` cho provider bỏ qua `enable_thinking`). Qwen3 dùng `enable_thinking=False` hoặc `/no_think` | [CLI and Defaults](../wiki/speech-to-speech-cli-and-defaults.md), [VN Stack](../wiki/vietnamese-realtime-voice-agent-stack.md) |
| Prompt kiểu văn nói | 1–3 câu ngắn. Không markdown, emoji, bảng, URL. Số và ngày viết bằng chữ, hoặc để normalizer xử lý. Đặt `max_tokens` | [Blueprint](../wiki/cascaded-voice-agent-blueprint.md), [VN Stack](../wiki/vietnamese-realtime-voice-agent-stack.md) |
| Chỉ định ngôn ngữ trả lời | HF s2s `--enable_lang_prompt` thêm lệnh yêu cầu trả lời bằng ngôn ngữ X vào mỗi lượt | [HF s2s](../wiki/speech-to-speech-pipeline.md) |

**Chỗ trống:** wiki không có thư viện ThinkFilter hay markdown-stripper riêng nào. Phần này mới chỉ là khuyến nghị thiết kế.

## 2. Chunker / sentence segmentation

| Công cụ | Cơ chế | Ghi chú |
|---|---|---|
| HF s2s | `stream_batch_sentences=3`, đặt `1` để stream từng câu (**Observed** trong dataclass) | Chính sách gom 3 câu; ở Chương 19 đây là chính sách `3sent` |
| Kokoro-FastAPI | Chunker theo ranh giới câu với `TARGET_MIN/MAX/ABSOLUTE_MAX_TOKENS` = 175/250/450. Model nhận tối đa 510 phonemized token; chạy sát giới hạn này thì giọng bị "rushed" | [Performance](../wiki/kokoro-fastapi-performance.md) |
| `kokoro` library | Tham số `split_pattern` là regex, ví dụ `\n+` | [Kokoro Python Library](../wiki/kokoro-python-library.md) |
| VieNeu API | Server tự chia `input` (≤ 20.000 ký tự) thành đoạn ≤ `max_chars`, mặc định 256, cho phép 64–512 | [VieNeu API](../wiki/vieneu-tts-openai-speech-api.md) |
| CrispASR server | "Long-form sentence chunking for TTS" | [CrispASR server](../wiki/crispasr-streaming-http-server.md) |
| CosyVoice2 bi-streaming | Nhận text generator nhưng vẫn khuyên giữ sentence splitting | [CosyVoice2](../wiki/cosyvoice2-0.5b.md) |
| Wyoming / Home Assistant | Stream theo ranh giới câu (cộng đồng kể lại) | [Community wiring](../wiki/community-stt-llm-tts-pipeline.md) |
| Luật khởi điểm | Cắt ở `.?!…;:` hoặc xuống dòng. Chunk đầu cắt ở dấu phẩy khi ≥ 25 ký tự. Gộp mảnh < 8 ký tự. Đơn vị nói chung khoảng 20–60 ký tự | [VN Stack](../wiki/vietnamese-realtime-voice-agent-stack.md), [Blueprint](../wiki/cascaded-voice-agent-blueprint.md) |

**Chỗ trống:** wiki chưa có thư viện tách câu tiếng Việt nào, cũng chưa ghi lại cách Pipecat gom text trước khi gửi sang TTS.

## 3. Text normalization (dạng viết → dạng nói)

| Công cụ | Hướng / ngôn ngữ | Trạng thái |
|---|---|---|
| [VietNormalizer](../wiki/vietnormalizer.md) | Viết → nói, tiếng Việt. Pipeline luật 19 bước, CSV hơn 17K mục, khoảng 0,6 ms mỗi lần gọi, MIT | Ứng viên đúng vị trí normalizer nhưng **chưa chạy**. Output bị lowercase. Phiên âm tiếng Anh bật mặc định. README tự mâu thuẫn ở ví dụ `database` |
| [ViSoNorm](../wiki/visonorm-visobert-normalizer.md) | Văn bản không chuẩn → văn bản chuẩn (teencode, thêm dấu). ViSoBERT, cần `trust_remote_code` | Draft. Chưa có license hay benchmark. Hợp với text người dùng gõ hơn là output LLM |
| WeTextProcessing / `ttsfrd` | Normalizer tích hợp sẵn trong [CosyVoice2](../wiki/cosyvoice2-0.5b.md), [Fun-CosyVoice3](../wiki/fun-cosyvoice3-0.5b-2512.md), [VoxCPM-0.5B](../wiki/voxcpm-0.5b.md) (tắt đi khi đưa input phoneme), [MOSS-TTS-Nano](../wiki/moss-tts-nano.md) (cài `pynini` hay lỗi) | Hướng zh/en. Wiki không có bằng chứng hỗ trợ vi |
| Kokoro-FastAPI `normalization_options` | Normalizer phía server | Known issue: có thể làm rơi hoặc đổi cụm từ. Cách tránh là `{"normalize": false}` |
| NeMo-Speech.cpp | Liệt kê "text normalization" trong nhóm speech processing | Chưa rõ đây là TN cho TTS hay ITN cho ASR. Phần ITN/PnC đã ghi nhận nằm ở phía ASR ([NeMo-Speech.cpp](../wiki/nemo-speech-cpp.md)) |
| Gợi ý trong model card | [Sopro](../wiki/sopro-v2-turbo.md) ghi frontend tối giản và khuyên đặt normalizer riêng phía trước. [G-OmniVoice](../wiki/g-omnivoice.md) khuyên normalize rồi chia câu | Chỉ là khuyến nghị |

**Chỗ trống:** wiki chưa compile NeMo WFST TN, cũng chưa có normalizer dựa trên LLM.

## 4. G2P, lexicon và điều khiển phát âm

| Công cụ | Vai trò | Giới hạn |
|---|---|---|
| [Misaki](../wiki/misaki.md) / [frontends](../wiki/misaki-language-frontends.md) | G2P cho Kokoro, có fallback espeak. Cú pháp override `[word](/IPA/)` | **Không có module vi**. Chỉ có một link tới Viphoneme. License không nêu |
| [eSpeak NG](../wiki/espeak-ng.md) | Xuất phoneme để làm frontend, có SSML không đầy đủ | GPL-3.0+. Chưa xác lập có hỗ trợ vi |
| [Phonemizer](../wiki/phonemizer.md) / [backends](../wiki/phonemizer-backends.md) | Bốn backend: espeak (IPA, giữ word token và dấu câu), espeak-mbrola, festival, segments | GPL-3.0+. Nhãn tốc độ chỉ là thứ bậc, chưa đo. Chưa xác lập hỗ trợ vi |
| `vig2p` ([Kokoro Vietnamese](../wiki/kokoro-vietnamese.md)), `sea-g2p` ([VieNeu](../wiki/vieneu-tts-v3-turbo.md)) | G2P tiếng Việt gắn liền với từng model | Chưa có concept riêng, chưa kiểm tra |
| Kokoro-FastAPI `/dev/phonemize`, `/dev/generate_from_phonemes` | Cho phép tách bước G2P ra ngoài | Chỉ hỗ trợ tiếng Anh |
| Pronunciation control trong input TTS | Fun-CosyVoice3 có Pinyin/CMU inpainting. IndexTTS-2.5 dùng `<word\|reading>`. GLM-TTS có `--phoneme`. MOSS dùng Pinyin/IPA | Không có cái nào được ghi nhận dùng cho vi |

Lỗi đã biết: VieNeu được báo đọc `chánh` thành `tránh` (#207), mới ở mức **Reported/Unverified**. Đây là loại lỗi respelling không sửa được.

## 5. Markup, SSML và inline control (định dạng của `spoken_text`)

- **[Kokoro-FastAPI Voice and Markup](../wiki/kokoro-fastapi-voice-and-markup.md):**
  - Dịch SSML sang token: `<break>` → `[pause:Xs]`, `<prosody rate>` → `[rate:]`, `<phoneme>`, `<sub alias>`.
  - Có `/dev/ssml` để xem kết quả dịch.
  - Phải bật cả `ssml:true` và `allow_voice_tags:true`.
- **Inline tag do model quy định:**
  - VieNeu: `[cuoi]`, `[tho dai]`, `[hang giong]`. Đây là bộ duy nhất cho tiếng Việt.
  - MOSS: `[pause 3.2s]`.
  - Higgs: `<|prosody:pause|>`.
  - Fish: `[pause]` và các tag tự do.
  - Breeze: `(laugh)`.
  - Supertonic 3: `<laugh>`.
- **Hệ quả cho thiết kế (Synthesis):** stage lọc markup trong normalizer cần một whitelist tag riêng cho từng backend, nếu không sẽ xóa mất control hợp lệ. VieNeu bỏ qua `speed` và `instructions`, nên dấu câu gần như là núm duy nhất để chỉnh ngắt nghỉ.

## 6. Nhận diện ngôn ngữ và định tuyến TTS

- **Lingua** trong HF s2s (`--detect_llm_output_language`): đoạn ngắn hơn 20 ký tự hoặc mơ hồ thì dùng lại ngôn ngữ phát hiện gần nhất. Lingua chưa có concept riêng.
- **Text LID của CrispASR:** CLD3 (109 nhãn, 440 KB, Apache), GlotLID-V3 (2.102 nhãn, 250 MB), LID-176 (CC-BY-NC). Xem [CrispASR VAD & LID](../wiki/crispasr-vad-language-id.md).
- Lưu ý từ Chương 19 §19.8.3: định tuyến theo từng chunk dễ làm đổi giọng giữa câu khi có code-switch Việt–Anh.

## 7. TTS adapter và serving contract (dịch vụ, không phải model)

| Service | Điểm đáng chú ý cho tầng cầu |
|---|---|
| [VieNeu API](../wiki/vieneu-tts-openai-speech-api.md) | Trả `pcm`/`wav` dạng chunked hoặc SSE. Resample bằng `soxr` theo từng chunk. Trả `429` kèm `Retry-After` khi hết slot. Có `temperature`/`top_k` |
| [HF s2s `--tts openai`](../wiki/speech-to-speech-openai-compatible-backends.md) | Chuyển 24 kHz sang 16 kHz int16, block 512 mẫu. Cancel phía server chỉ là best-effort |
| [NeMo-Speech.cpp](../wiki/nemo-speech-http-api.md) | `/v1/audio/speech` **buffer toàn bộ** trước khi trả, không streaming. `speed` chỉ nhận 1.0 |
| [CrispASR](../wiki/crispasr-streaming-http-server.md) | Mặc định suy luận tuần tự trên một model |
| [Speaches](../wiki/speaches.md), [Kokoro-FastAPI](../wiki/kokoro-fastapi.md) | OpenAI-compatible, nhưng các trường mở rộng nằm ngoài schema |
| [SGLang-Omni](../wiki/sglang-omni.md), [vLLM-Omni](../wiki/vllm-omni.md) | Phục vụ TTS trên GPU. Theo AI report (nguồn thứ cấp), vLLM-Omni có WebSocket `input.text`/`input.done`, tức là nhận text tăng dần ở tầng serving |

[So sánh công cụ](../wiki/speech-deployment-tools-comparison.md) ghi chú rằng "OpenAI-compatible" thường chỉ là một **subset**. Cần test schema, format, cancellation và sample rate trước khi coi là thay thế trực tiếp.

## 8. Hậu xử lý audio, playback và ngắt lời

- **Resample và format:**
  - VieNeu dùng soxr.
  - Browser demo của HF s2s nội suy tuyến tính 24 → 48 kHz, thêm fade 32 frame để chống tiếng click.
  - Supertonic đi từ 44,1 xuống 16 kHz trong HF s2s.
  - audio.cpp có sẵn tiện ích resample.
  - Cộng đồng ghi nhận lệch sample rate là nguồn bug phổ biến.
- **Watermark:**
  - VieNeu: Perth, áp theo từng chunk (`VIENEU_WATERMARK=1`). Các số đo latency qua HTTP được chạy khi watermark bật.
  - Chatterbox: PerTh, kèm API phát hiện của `perth`.
  - CrispASR: có `--detect-watermark`.
  - Irodori: SilentCipher.
  - VibeVoice: chèn disclaimer nghe được.
  - Sopro: cố ý không watermark và có giải thích lý do.
- **Playback buffer:**
  - Client của HF s2s mặc định 196 ms cho TTS qua HTTP, chỉnh bằng `--playback-buffer-ms`.
  - Browser demo mặc định 0 ms. Issue #557 dùng 1200 ms làm ví dụ tuning.
  - VieNeu khuyên pre-buffer 150–300 ms trên GPU và ≥ 300 ms trên CPU.
- **Barge-in:**
  - HF s2s dùng `CancelScope` với generation counter. WebRTC có `output_audio_buffer.clear`.
  - Browser demo gửi `conversation.item.truncate` theo số mẫu PCM đã render, nhưng server hiện coi đó là no-op.
  - Thiết kế dùng `generation_id` và chỉ lưu phần đã phát kèm tag `[bị ngắt]` ([Barge-in](../wiki/voice-agent-barge-in-and-echo-handling.md)).
- **Caption và alignment:**
  - Kokoro-FastAPI `/dev/captioned_speech` trả word timestamp. Header `X-Timing-Path` trỏ tới timing theo chunk.
  - HF s2s phát `response.output_audio_transcript.delta`.

## 9. Orchestration (nơi đặt tầng cầu)

- Các framework: Pipecat, LiveKit Agents, TEN, FastRTC ([Frameworks](../wiki/voice-agent-frameworks.md)). Phần so sánh này dựa trên AI report thứ cấp.
- Các pipeline hoàn chỉnh: [HF s2s](../wiki/speech-to-speech-pipeline.md), [RealtimeVoiceChat](../wiki/realtime-voice-chat.md) (RealtimeTTS chưa có concept riêng).
- Với VieNeu, Pipecat chỉ cần viết một `TTSService` gọi `/v1/audio/speech`.
- Cách tự viết gateway asyncio được mô tả trong [VN Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md).

## 10. Đánh giá và quan sát

- [Latency instrumentation](../wiki/speech-to-speech-latency-instrumentation.md): `tts_ttfa` tính từ lúc bắt đầu tổng hợp segment đầu tới khi nhận mẫu audio đầu tiên. Các stage chồng lấn nhau, không được cộng dồn.
- Kokoro-FastAPI đo round-trip WER bằng faster-whisper. Đây chỉ là proxy cho độ dễ nghe.
- VieNeu có `openai_speech_client.py --bench N`.
- Metric `first_sentence→tts_first_byte` ([VN Stack](../wiki/vietnamese-realtime-voice-agent-stack.md)).
- [Resemblyzer](../wiki/resemblyzer.md) có thể dùng để đo độ nhất quán giọng giữa các chunk. Đây là **Synthesis**, wiki chưa có nguồn dùng nó cho mục đích này.

---

## Tóm tắt cho pipeline tiếng Việt

| Bước | Ứng viên tốt nhất trong wiki | Mức bằng chứng |
|---|---|---|
| Chunker | Tự viết theo luật ở VN Stack / Chương 19. Đặt `hard_max` < `max_chars` của VieNeu | Reported + Synthesis |
| Normalizer | VietNormalizer, bọc như verbalizer cho segment `plain` | Reported, chưa chạy |
| Lexicon / G2P | Lexicon riêng cho từng backend. `sea-g2p`/`vig2p` nằm trong model | Chưa kiểm tra |
| Control | Inline cue của VieNeu, dấu câu | Reported |
| Adapter | VieNeu `/v1/audio/speech` qua Pipecat hoặc HF s2s | Reported |
| Playback | Pre-buffer 150–300 ms, flush khi barge-in | Reported |

**Những gì wiki chưa compile:** NeMo WFST TN, thư viện tách câu tiếng Việt, Lingua, RealtimeTTS, Piper/Wyoming, Viphoneme, `vig2p`/`sea-g2p` dưới dạng concept riêng, và text aggregator của Pipecat. "Không có trong wiki" chỉ có nghĩa là chưa được compile, không có nghĩa là công cụ không tồn tại.

Tôi để kết quả này ở dạng tạm (wiki và log không thay đổi). Nếu bạn muốn, tôi có thể lưu nó thành trang `type: Synthesis` (ví dụ `wiki/text-to-speech-bridge-tooling-survey.md`) bằng `wiki-ingest`, kèm citation tới các concept ở trên.