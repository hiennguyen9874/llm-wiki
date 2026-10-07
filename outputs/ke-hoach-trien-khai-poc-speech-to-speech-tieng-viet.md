# Kế hoạch triển khai PoC speech-to-speech tiếng Việt — Phase 1

> **Loại tài liệu:** kế hoạch triển khai (deliverable trong `outputs/`, không phải tri thức canonical).
> **Ngày:** 2026-10-07.
> **Triển khai cho:** [Spec PoC Phase 1](spec-poc-speech-to-speech-tieng-viet.md). Tham chiếu: [thiết kế pipeline](thiet-ke-pipeline-speech-to-speech-tieng-viet.md), [ASR](lua-chon-va-thiet-ke-asr-stt-tieng-viet-realtime.md), [TTS](lua-chon-va-thiet-ke-tts-tieng-viet-realtime.md). Chi tiết lấy thêm từ wiki: [HF Speech-to-Speech](../wiki/speech-to-speech-pipeline.md), [NeMo-Speech.cpp](../wiki/nemo-speech-cpp.md), [VieNeu-TTS v3 Turbo](../wiki/vieneu-tts-v3-turbo.md), [G-OmniVoice](../wiki/g-omnivoice.md), [Gwen-TTS 0.6B](../wiki/gwen-tts-0.6b.md), [Qwen3-ASR](../wiki/qwen3-asr-family.md), [Nemotron 3.5 ASR](../wiki/nemotron-3.5-asr-streaming-0.6b.md).
> **Nhãn:** **Reported** = nguồn tự công bố; **Synthesis** = đề xuất của kế hoạch; **TBD** = xác minh ở Day 0; **Ngoài wiki** = kiến thức chung chưa được compile vào wiki, phải kiểm tra.
> Kế hoạch không đổi quyết định nào của spec. Những điểm kế hoạch **đề xuất thêm** được đánh dấu `[ĐX]` và gom lại ở mục 11.
> **Đối chiếu `raw/` (2026-10-07):** đã đọc trực tiếp `raw/speech-to-speech.md`, `raw/VieNeu-TTS-repo.md`, `raw/VieNeu-TTS-v3-Turbo.md`, `raw/NeMo-Speech.cpp.md`, `raw/nemotron-3.5-asr-streaming-0.6b.md`, `raw/Qwen3-ASR-0.6B-hf.md`, `raw/g-omnivoice.md`, `raw/gwen-tts-0.6B.md` để chốt các ô TBD. Kết quả ở mục 0.1.
> **Cập nhật sau review (2026-10-07):** theo [review latency](review-ke-hoach-trien-khai-poc-speech-to-speech.md) và [review streaming](review-streaming-ke-hoach-trien-khai-poc-speech-to-speech.md). Thay đổi chính: Day 0 thêm R11/R12 (độ mịn chunk LLM→TTS, TTS có chạy speculative không); thêm `llm-tap` để đo timeline LLM; acceptance M1 yêu cầu TTS nhận mệnh đề đầu trước khi LLM xong; join log theo ID thay vì thứ tự lượt; báo cáo theo loại lượt; thêm D6–D8. Rủi ro "không chunk thêm" ở §12 không còn được chấp nhận mặc định.

---

## 0. Tóm tắt

- **Khối lượng:** ~10.5–12.5 ngày công cho 1 kỹ sư, chia 7 mốc (M0–M6), cộng tối đa ~1 ngày nếu phải vá chunker trong s2s (D6). Day 0 (M0) là go/no-go cho từng run.
- **Code phải viết** (phần còn lại là cấu hình):
  1. `tts-proxy`: một proxy `/v1/audio/speech` đứng trước **mọi** TTS HTTP. Nó làm lớp text→speech tối thiểu (spec §3.5) và chuẩn hóa audio contract về đúng định dạng HF s2s cần (R4) `[ĐX]`.
  2. `clone-tts-server`: một server `/v1/audio/speech` với 2 backend `gwen` và `gomni` (`gomni` chỉ dùng nếu R3 thất bại).
  3. Bộ đo: ghi âm 2 kênh, phân tích voice-to-voice/barge-in, parse log HF s2s, lấy mẫu VRAM, manifest cho mỗi run, tổng hợp báo cáo.
  4. Fixture Day 0: `tone-server` (TTS giả phát tone đã biết) và các script kiểm tra R1–R8, R10–R12.
  5. `llm-tap`: pass-through streaming trước LLM endpoint, chỉ log thời điểm content-free (`req_start`, `llm_first_token`, `llm_done`/`cancelled`) trên cùng clock với `tts-proxy` `[ĐX]`.
- **Thứ tự:** M0 Day 0 → M1 vòng R0 chạy được → M2 bộ đo (song song M1) → M3 các thành phần thay thế → M4 pilot → M5 chạy đủ ma trận → M6 báo cáo.

### 0.1 Kết quả đối chiếu `raw/`

`raw/` chỉ chứa README/card, nên các tài liệu con (`docs/openai-compatible-tts.md`, `docs/openai-compatible-stt.md`, `src/speech_to_speech/STT|TTS/README.md`, `demo/README.md`, `docs/server.md` của NeMo-Speech.cpp, `docs/streaming.md` của VieNeu) **không có** để kiểm. Những gì còn TBD vẫn phải xác minh ở Day 0.

**Đã chốt từ raw (Reported, nguồn gốc):**

| Mục | Phát hiện | Nguồn | Ảnh hưởng tới kế hoạch |
|---|---|---|---|
| Cổng s2s | `serve` nghe ở `ws://127.0.0.1:8765/v1/realtime`; Docker compose cũng mở `8765` | `raw/speech-to-speech.md` › Other clients and offline use; Docker | Bỏ TBD cổng 8765 |
| Qwen3-ASR trong s2s | Backend **built-in** (không cần extra) qua Transformers, checkpoint `Qwen/Qwen3-ASR-0.6B-hf` | `raw/speech-to-speech.md` › Supported Components | Dùng checkpoint `-hf` (`0.6B-hf`, `1.7B-hf`); bỏ ý "extra Qwen3-ASR" của spec §3.1. Checkpoint `-hf` cần `transformers>=5.13.0` (wiki Qwen3-ASR) |
| Ép ngôn ngữ Qwen `-hf` | `language="Chinese"` **hoặc mã** `"zh"` | `raw/Qwen3-ASR-0.6B-hf.md` › Forcing the language | Giá trị cho tiếng Việt: `"vi"` hoặc `"Vietnamese"`. **Tên cờ** s2s vẫn TBD (nằm trong STT README chưa capture) |
| Quy ước tên cờ | Mỗi handler STT/TTS có `model_name`, `torch_dtype`, `device` với tiền tố handler (ví dụ `--stt_model_name`, `--qwen3_tts_device`); tham số sinh dùng `<prefix>_gen_` | `raw/speech-to-speech.md` › STT, LLM, and TTS Parameters | Đoán có căn cứ: `--omnivoice_model_name g-group-ai-lab/g-omnivoice` cho R3 (**Synthesis**, vẫn kiểm bằng `-h`) |
| System prompt | Đặt bằng `session.update` → `session.instructions` | `raw/speech-to-speech.md` › Realtime API (ví dụ Python) | Không cần cờ server; cấu hình ở client/demo |
| Barge-in | Ví dụ session đặt `turn_detection: {type: "server_vad", interrupt_response: true}` | như trên | Kiểm browser demo có gửi `interrupt_response: true` không; nếu không, barge-in có thể không chạy |
| Ngôn ngữ STT | `session.audio.input.transcription.language` pin STT; mỗi backend STT có cờ ngôn ngữ riêng (`--language` chỉ cho Whisper) | › Multi-Language Support | Giữ cả hai lớp pin như spec |
| Audio nội bộ s2s | Handler OmniVoice chuyển 24 kHz float sang **khối 16 kHz `int16` của pipeline** | › OmniVoice | Mới (xem rủi ro bên dưới) |
| Buffer phát | 196 ms chỉ áp dụng cho client Python đóng gói; trình duyệt tự quản lý buffer | › Commands | Đo TTFA phía trình duyệt, không giả định 196 ms |
| Kết nối LLM local | Ví dụ dùng `--responses_api_base_url`, `--responses_api_api_key ""`, `--responses_api_stream`, `--responses_api_reasoning_effort none` | › Chat Completions Backend; Combining with llama.cpp | Thêm `--responses_api_api_key ""` và `--responses_api_stream` vào lệnh R0 |
| Chạy offline | Chạy cấu hình một lần khi có mạng để cache STT/LLM/TTS/Silero/NLTK/Smart Turn, sau đó `HF_HUB_OFFLINE=1` | › Offline Operation | Thêm vào bước pre-cache |
| Pool pipeline | `--num_pipelines` = kích thước pool realtime | › Module-Level Parameters | Đặt `1` cho PoC 1 user nếu nó ảnh hưởng VRAM (**Synthesis**, kiểm `-h`) |
| VieNeu API | `docker compose -f docker/docker-compose.yml --profile api-gpu up`; `model="vieneu-v3-turbo"`; `pcm` = **s16le 48 kHz mono**, chunked khi đang sinh; `POST /v1/voices` để clone | `raw/VieNeu-TTS-repo.md` › §3 API Server & Docker | Chốt contract upstream của VieNeu; schema body của `POST /v1/voices` vẫn TBD |
| VieNeu temperature | Tip ~0.8 chỉ có ở SDK/card; README API **không** nêu tham số temperature | `raw/VieNeu-TTS-v3-Turbo.md` dòng ~133 | Không đặt temperature qua API; dùng default server |
| Preset VieNeu theo vùng | Bắc: Minh Đức, Phạm Tuyên, Xuân Vĩnh, Thanh Bình, Ngọc Linh, Đoan Trang, Quỳnh Anh, Quốc Tuấn; Nam: Adam, Thái Sơn, Thục Đoan, Minh Triết, Mỹ Duyên, Đức Trí, Kim Thanh, Thùy Dung | `raw/VieNeu-TTS-repo.md` › Available Voices | Chọn 1 Bắc + 1 Nam từ danh sách này, xác nhận bằng `GET /v1/voices` |
| NeMo-Speech.cpp | `serve --asr-model nemotron-3.5`, mặc định `127.0.0.1:8080`; CLI `transcribe --language <locale>` (ví dụ `en-US`, hoặc `auto`) | `raw/NeMo-Speech.cpp.md` › Local server; `raw/nemotron-3.5-asr-streaming-0.6b.md` › Run locally with NeMo-Speech.cpp | Ở CLI, locale có dạng `vi-VN`. Cờ cổng và field language trên HTTP vẫn TBD (R1) |
| G-OmniVoice / Gwen | G-OmniVoice ra 24000 Hz; Gwen trả `(wavs, sr)`; cả hai card khuyên normalize text và chia câu | `raw/g-omnivoice.md` › Usage, Tips; `raw/gwen-tts-0.6B.md` › How to Use | Khớp thiết kế `clone-tts` (X4) |

**Rủi ro mới từ raw — R10: trần chất lượng 16 kHz.** Nếu mọi TTS trong s2s bị đưa về khối 16 kHz `int16` trước khi gửi xuống client (như handler OmniVoice), thì lợi thế 48 kHz của VieNeu bị mất, và phiếu nghe G3 chỉ đánh giá được chất lượng ở 16 kHz. Việc này ảnh hưởng đều cho cả 3 TTS nên A/B vẫn công bằng, nhưng phải ghi trong báo cáo. Kiểm tra ở Day 0 cùng R4: với tone-server 48 kHz, xem phổ của bản ghi loopback có bị cắt ở ~8 kHz không. Chưa biết client TTS OpenAI-compatible có đi qua cùng đường 16 kHz không (**TBD**).

**Vẫn TBD sau khi đọc raw** (tài liệu chưa có trong `raw/`): selector và cờ ngôn ngữ của Qwen3-ASR trong s2s; cờ của TTS/STT OpenAI-compatible (`base_url`, model, voice, format); cờ model path của omnivoice; browser demo (cách đặt session language và instructions, HTTPS); cổng và field language của `nemo-speech serve`; schema `POST /v1/voices` của VieNeu; định dạng log latency của s2s. Có thể capture các tài liệu này vào `raw/` trước Day 0 (mục 11.3, D5).

---

## 1. Topology và cổng

```text
Máy client (trình duyệt + ghi âm 2 kênh)
   │ HTTPS/WebRTC (R8)
   ▼
Máy GPU 24 GB
 ├─ s2s        speech-to-speech serve           :8765 (/v1/realtime, raw)  env-s2s (venv)
 │    ├─ ASR in-process: Qwen3-ASR 0.6B/1.7B                 (R0,R1,R3–R5)
 │    └─ TTS in-process: handler omnivoice → G-OmniVoice     (R4, nếu R3 OK)
 ├─ nemo       nemo-speech serve nemotron-3.5   :8090        binary native   (chỉ R2)
 ├─ stt-shim   (fallback R1) /v1/audio/transcriptions :8091  env-tools       (chỉ R2, nếu cần)
 ├─ llm-tap    pass-through → LLM endpoint      :8110        env-tools [ĐX]
 ├─ tts-proxy  /v1/audio/speech                 :8100        env-tools
 │    ├──► vieneu        Docker api-gpu         :8000        (R0–R3)
 │    ├──► clone-tts gwen                       :8101        env-gwen (R5)
 │    └──► clone-tts gomni (fallback R3)        :8102        env-gomni (R4)
 └─ vram-sampler (nvidia-smi)
   │ LAN
   ▼
Máy LLM: endpoint OpenAI-compatible  http://<llm-host>:<port>/v1
```

- Tất cả cổng model chỉ bind `127.0.0.1`, trừ cổng s2s phục vụ trình duyệt (**Synthesis**, theo spec §2 và nguyên tắc privacy).
- `nemo-speech serve` mặc định là `127.0.0.1:8080`, còn `qwen-asr-serve` và VieNeu dùng `8000` (**Reported**). Vì vậy kế hoạch đổi cổng như bảng trên. Cờ đổi cổng của `nemo-speech serve` là **TBD**.
- Mỗi run chỉ bật 1 ASR + 1 TTS trên GPU (spec Q29). Script `start_run.sh` dừng hết những gì không thuộc run đó.

### 1.1 Môi trường

| Env | Nội dung | Ghi chú |
|---|---|---|
| `env-s2s` | Python 3.11, `speech-to-speech[omnivoice]`; Qwen3-ASR là backend built-in qua Transformers (raw) | Không cài DeepFilterNet (`numpy<2` xung đột, **Reported**). G-OmniVoice qua handler chạy chung env này. Checkpoint Qwen `-hf` cần `transformers>=5.13`, còn extra `omnivoice` dùng Transformers 5 qua `faster-qwen3-tts>=0.4.0` (raw). Kiểm bản Transformers mà resolver chọn thỏa cả hai |
| `vieneu` | Docker Compose profile `api-gpu`, cổng 8000 | `VIENEU_MAX_STREAMS=2` |
| `nemo` | `nemo-speech` build preset `cuda-server` (hoặc installer + bản prebuilt) | GGUF Nemotron 3.5 Q8 được tải và kiểm SHA-256 ở lần chạy đầu (**Reported**) |
| `env-gwen` | `qwen-tts`, `flash-attn` (tùy chọn), FastAPI | Torch pin riêng |
| `env-gomni` | `torch==2.8.0+cu128`, `omnivoice`, FastAPI | Chỉ tạo khi R3 thất bại |
| `env-tools` | `fastapi`, `uvicorn`, `httpx`, `numpy`, `soundfile`, `soxr`, `silero-vad`, `pandas` | proxy, shim, bộ đo |

Pin mọi version (`uv.lock` / `requirements.lock`, digest Docker image, commit/tag `nemo-speech`, HF revision của từng checkpoint). Pre-download weights trước M5 để không tải trong lúc đo.

---

## 2. Cấu trúc repo PoC

Code đặt trong repo riêng (ví dụ `poc-s2s-vi/`), **không** đặt trong repo wiki. Báo cáo kết quả cuối cùng copy về `outputs/` (spec §7).

```text
poc-s2s-vi/
  README.md                    cách dựng + chạy 1 run
  runs.yaml                    R0..R5: asr, tts, voice, cờ s2s (nguồn duy nhất của cấu hình)
  compose.yaml                 vieneu, tts-proxy, clone-tts-*
  config/
    system_prompt.txt          prompt spec §3.2
    abbrev.yaml                từ điển viết tắt
    lexicon.yaml               thay thế tên riêng/thuật ngữ (gồm chánh/tránh)
    voices.yaml                voice_id → preset VieNeu / clone ref (đường dẫn ngoài repo)
  services/
    tts_proxy/                 app.py, normalize.py, audio.py, tests/
    clone_tts/                 app.py, backends/{gwen,gomni}.py
    stt_shim/                  (fallback R1)
    tone_server/               fixture Day 0
  scripts/
    day0/                      r1_nemo.sh, r2_flags.sh, r3_gomni.py, r4_contract.md, r6_llm_cancel.py, r7_hook.sh, r8_https.md
    run/                       start_run.sh, stop_all.sh, warmup.py, manifest.py, vram_sampler.sh
    measure/                   record_stereo.sh, analyze_audio.py, parse_s2s_log.py, aggregate.py
  protocol/
    kich_ban.md                kịch bản ~21 lượt (mục 7)
    phieu_quan_sat.csv         template (spec §5.4)
    phieu_nghe_tts.csv
  runs/                        (gitignored) R0/C1/{audio,logs,sheet.csv,manifest.json}
  reports/
```

Dữ liệu cá nhân (reference clone, consent, bản ghi giọng tester, log có transcript) để **ngoài** repo, trong thư mục có quyền truy cập hạn chế (spec §3.4, §2).

---

## 3. Mốc M0 — Day 0: xác minh R1–R8, R10–R12 (1–1.5 ngày)

Mục tiêu: chốt tên cờ, audio contract và các phương án dự phòng **trước khi** viết code. Kết quả ghi vào `docs/day0.md` và cập nhật các ô TBD trong `runs.yaml`.

| # | Việc | Cách làm cụ thể | Pass khi | Nếu fail |
|---|---|---|---|---|
| R2 | Cờ s2s | `speech-to-speech serve -h`, rồi `serve --stt <x> -h` và `serve --tts <x> -h` cho từng selector: Qwen3-ASR, STT OpenAI-compatible, TTS OpenAI-compatible, `omnivoice`. Lưu output vào `docs/flags/`. Đã biết từ raw: quy ước `--<handler>_model_name`, cổng 8765, `--num_pipelines` | Có cờ: chọn checkpoint `Qwen/Qwen3-ASR-{0.6B,1.7B}-hf`, ép ngôn ngữ (`vi`/`Vietnamese`), `base_url`/model/voice/format cho STT và TTS HTTP, model path cho omnivoice | Tra mã nguồn (`src/speech_to_speech/arguments_classes/`, chưa capture vào raw) |
| R7 | Hook text trước TTS | `grep` trong mã s2s xem có bước tiền xử lý text trước khi gọi handler TTS không | Có hook cắm được `normalize()` | Dùng `tts-proxy` (đã là thiết kế mặc định của kế hoạch) |
| R4 | Audio contract TTS HTTP | Chạy `tone-server`: trả 1.0 s sine 440 Hz, khai báo lần lượt 24k/48k, `pcm`/`wav`. Trỏ TTS HTTP của s2s vào đó, ghi loopback ở client, đo tần số và độ dài. Thêm một sweep 0–20 kHz để kiểm R10 (băng thông bị cắt ở ~8 kHz?) | Ra 440 Hz, dài 1.0 s; ghi lại băng thông thực tế | Xác định định dạng s2s thực sự chấp nhận; `tts-proxy` resample/đổi định dạng về đúng định dạng đó. Nếu pipeline là 16 kHz thì proxy xuất thẳng 16 kHz để tránh resample hai lần |
| R1 | Nemotron `vi-VN` qua HTTP | `nemo-speech serve --asr-model nemotron-3.5`; gửi 1 file wav tiếng Việt 16 kHz mono tới `/v1/audio/transcriptions` với `language=vi-VN`, `language=vi`, và không truyền language | Ra chữ tiếng Việt đúng khi có `vi-VN` (hoặc auto) | (a) `stt-shim` đổi `vi`→`vi-VN`; (b) shim bọc NeMo Python `target_lang=vi-VN`; (c) bỏ R2 khỏi ma trận |
| R3 | G-OmniVoice qua handler | Thử `--omnivoice_model_name g-group-ai-lab/g-omnivoice` (đoán theo quy ước tên cờ trong raw), sinh 1 câu tiếng Việt kèm ref | Nghe ra tiếng Việt với giọng ref | `clone-tts` backend `gomni` đặt sau `tts-proxy` |
| R6 | LLM hủy được | `r6_llm_cancel.py`: stream một câu trả lời dài, đóng kết nối sau 1 s, theo dõi log hoặc GPU util của server LLM | Server ngừng sinh trong ≤ 1–2 s | Ghi nhận là giới hạn; barge-in vẫn dừng âm thanh nhưng phí compute |
| R8 | Mic trong trình duyệt từ máy khác | Mở browser demo từ máy client qua `http://<gpu-ip>`. Đồng thời kiểm demo có gửi `session.update` kèm `instructions`, `transcription.language` và `turn_detection.interrupt_response: true` không | Trình duyệt cho dùng mic; ba field trên đặt được | Reverse proxy TLS tự ký (Caddy/nginx) trước cổng s2s; hoặc chạy trình duyệt ngay trên máy GPU |
| R5 | VRAM | Đo sơ bộ ở M3/M4 bằng `vram_sampler.sh` | Peak < ~22 GB | Giảm precision; giữ 1 ASR + 1 TTS |
| R11 | Độ mịn chunk LLM → TTS | s2s trỏ TTS vào `tone-server`, LLM qua `llm-tap`. Prompt buộc trả lời ≥ 3 câu. Ghi số request TTS mỗi response, nội dung độ dài (ký tự), và thời điểm request đầu so với `llm_done`. Raw cho biết s2s có "assistant text chunk" (dùng cho `--detect_llm_output_language`), và có cache NLTK, nên nhiều khả năng chia theo câu (**Synthesis**) | ≥ 2 request mỗi response nhiều câu, và request đầu tới trước `llm_done` | D6: vá chunker theo mệnh đề ở consumer LLM trong s2s, hoặc ghi giới hạn. Chia lại ở proxy không lấy lại thời gian chờ LLM |
| R12 | TTS speculative trong grace | Nói một câu, dừng, nói tiếp sau ~500 ms (trong grace 800 ms). Xem `tone-server` có nhận request TTS của revision bị bỏ không; so thời điểm request TTS với sự kiện commit trong log s2s (nếu có) | Biết TTS chạy trước hay sau output commit | Không sửa; ghi vào `day0.md` để đọc đúng timeline v2v (spec §1) |

Thêm 3 việc Day 0 `[ĐX]`:

- **TTS HTTP của s2s gửi gì:** bật log request ở `tone-server` để ghi lại body/headers mà s2s gửi (`model`, `voice`, `response_format`, `speed`, có `stream` không, có gửi theo câu hay theo mệnh đề không). Từ đó làm `tts-proxy` và `clone-tts` khớp đúng (spec §3.4, TBD).
- **STT HTTP của s2s gửi gì:** tương tự, dùng một stub `/v1/audio/transcriptions` ghi lại định dạng audio (wav? sample rate?) và các field (`language`, `model`).
- **Lưu ý ngoài wiki:** quy ước `pcm` của OpenAI TTS API là s16le 24 kHz mono (**Ngoài wiki**). Nếu client s2s ngầm giả định như vậy thì PCM 48 kHz của VieNeu sẽ phát sai tốc độ/cao độ. Đây chính là thứ R4 phải bắt được.

**Đầu ra M0:** `docs/day0.md` (pass/fail + bằng chứng cho từng mục), `runs.yaml` đã điền cờ thật, danh sách run nào bị bỏ hoặc đổi phương án. Nếu Day 0 đổi kiến trúc (ví dụ bỏ R2), cập nhật spec trước khi sang M1.

---

## 4. Mốc M1 — Vòng R0 chạy được (2 ngày)

### 4.1 VieNeu (TTS-VIE)

1. `docker compose -f docker/docker-compose.yml --profile api-gpu up -d` (trong repo VieNeu) với `VIENEU_MAX_STREAMS=2`; pin image digest. Upstream contract (raw): `model="vieneu-v3-turbo"`, `response_format="pcm"` trả s16le 48 kHz mono, chunked khi đang sinh.
2. Lấy danh sách preset bằng `GET /v1/voices` hoặc `list_preset_voices()`; chọn 1 giọng Bắc và 1 giọng Nam, ghi vào `voices.yaml`. Pin phiên bản SDK vì roster thay đổi giữa 3.7.1 và 3.8.x (**Reported**).
3. Warmup: `warmup.py` gửi 3 câu mẫu ngắn/vừa/dài. Server chỉ được coi là ready sau warmup (spec §3.4). Tùy chọn: khóa clock GPU (`nvidia-smi -lgc`, cần root) để tránh phạt 100–300 ms sau khi GPU nghỉ (**Reported**).
4. Kiểm tra trực tiếp: `curl -X POST :8000/v1/audio/speech -d '{"model":...,"input":"Xin chào, tôi là trợ lý.","voice":"<preset>","response_format":"pcm"}' --output a.pcm`, rồi phát lại ở 48 kHz.
5. Temperature ~0.8 chỉ là tip của SDK/card; README API không có tham số này (raw), nên dùng default của server.
6. Chọn preset từ danh sách theo vùng trong raw (mục 0.1), ví dụ Bắc `Ngọc Linh` / Nam `Thùy Dung`, rồi xác nhận bằng `GET /v1/voices`.

### 4.2 `tts-proxy`

**Hợp đồng vào** (khớp với những gì s2s gửi, xác định ở Day 0):

```text
POST /v1/audio/speech   { model, input, voice, response_format, ... }
GET  /health            200 chỉ khi upstream /health OK và đã warmup
GET  /v1/models         (nếu s2s gọi)
```

**Xử lý:**

```text
input ─► normalize() ─► upstream (UPSTREAM_URL, voice map) ─► stream audio
       └ log content-free                                    └ convert: dtype / sample rate / channels về OUT_FORMAT (R4)
```

- `normalize.py` cài đúng 5 rule của spec §3.5:
  1. Unicode NFC.
  2. Bỏ markdown (`**`, `#`, backtick, bullet `-`/`*`/`1.` đầu dòng, bảng), emoji, URL; giữ dấu câu.
  3. `abbrev.yaml`: `TP.HCM`, `TP`, `UBND`, `km/h`, `%`, `đ`/`VND`. Match theo ranh giới từ, xử lý `TP.HCM` trước `TP`.
  4. `lexicon.yaml`: thay thế theo ranh giới từ; bắt đầu với case `chánh` (**Reported/Unverified**, cách thay cụ thể chọn sau khi nghe thử).
  5. Đếm chữ số còn sót (`\d`), **chỉ log** số lượng, không đọc thành chữ.
- `audio.py`: chuyển đổi streaming (float32↔s16le, resample bằng `soxr` streaming, downmix về mono). Khi upstream đã đúng định dạng đích thì pass-through.
- **Cancellation:** client (s2s) ngắt kết nối thì đóng luôn stream tới upstream (`httpx` stream context). Ghi lại upstream có thật sự ngừng tính toán không. Đây là kiểm tra TTS tương tự R6.
- **Log mỗi request (content-free):** `req_id, run_id, t_recv (wall + monotonic), chars_in, chars_out, rules_hit{md,emoji,url,abbrev,lexicon}, digits_left, upstream_ttfb_ms, proxy_ttfb_ms, total_ms, audio_s, cancelled, t_upstream_end`. `t_recv` dùng để đặt request TTS lên cùng timeline với `llm-tap`; `t_upstream_end` sau `cancelled` cho biết backend có hết compute không. Cờ `--log-content` chỉ bật trong phiên test và ghi ra file nằm ngoài repo.
- **Test:** `tests/test_normalize.py` với khoảng 30 case (markdown, emoji, URL, mỗi viết tắt, lexicon, chuỗi số còn sót, NFC so với NFD). `tests/test_audio.py`: tone 440 Hz 48k→đích, kiểm tra tần số và độ dài.
- **Test giữ streaming** `[ĐX]` (rủi ro thật là proxy vô tình biến streaming thành buffered, không phải chi phí một hop localhost): upstream giả trả chunk cách nhau 200 ms; client phải nhận byte đầu trước khi upstream xong (không gom body); resampler giữ state qua chunk (không click/lệch độ dài ở biên); không resample hai lần.

Chi phí proxy phải nhỏ: `proxy_ttfb_ms − upstream_ttfb_ms` P95 < ~10 ms (**Synthesis**). Đo ở M4.

### 4.3 HF s2s + LLM + browser

1. Cài `env-s2s`. Chạy mỗi cấu hình run một lần khi có mạng để cache STT/TTS/Silero/NLTK/Smart Turn, sau đó chạy đo với `HF_HUB_OFFLINE=1`. Có thể dùng thêm `--smart_turn_model_path` (**Reported**, raw › Offline Operation).
2. Kiểm tra LLM trước: `curl <llm>/v1/chat/completions` với `stream: true` và system prompt; xác nhận thinking đã tắt (output không có khối reasoning).
3. Ghép lệnh R0 từ `runs.yaml` (tên cờ có `<…>` lấy từ Day 0):

```bash
HF_HUB_OFFLINE=1 speech-to-speech serve --host 0.0.0.0 \
  --stt <qwen3-asr-selector> --<prefix>_model_name Qwen/Qwen3-ASR-0.6B-hf <qwen-lang-flag> vi \
  --llm_backend chat-completions \
  --responses_api_base_url http://<llm-host>:<port>/v1 --responses_api_api_key "" \
  --model_name <llm-model> --responses_api_stream --responses_api_reasoning_effort none \
  --tts <openai-compatible-tts-selector> <tts-base-url-flag> http://127.0.0.1:8100/v1 <tts-voice-flag> <preset-bac> \
  [--num_pipelines 1]
# System prompt: gửi qua session.update → session.instructions từ client (raw › Realtime API).
# Trình duyệt kết nối tới :8765 (/v1/realtime).
# VAD/turn: giữ default (--thresh 0.6, --min_silence_ms 64, --speculative_reopen_ms 800,
#           Smart Turn v3.2, 600 ms / 2 s / 0.5) — spec Q30. Không truyền các cờ này.
# Không bật --enable_llm_proxy, không bật --detect_llm_output_language.
```

4. Pin ngôn ngữ: cờ ngôn ngữ của backend STT, cộng với `session.audio.input.transcription.language` trong session của browser demo (cách đặt trong demo là **TBD**). Checkpoint Qwen `-hf` nhận cả tên (`"Chinese"`) lẫn mã (`"zh"`) (**Reported**, raw), nên dùng `vi` hoặc `Vietnamese`. Nếu đúng là tiếng Việt, Qwen đã ghi lại ngôn ngữ nhận được trong output `language ...<asr_text>`, có thể dùng để kiểm.
5. System prompt: đặt qua `session.update` → `session.instructions` (**Reported**, raw › Realtime API). Nếu browser demo không cho sửa, sửa nhỏ JS của demo.
6. Dự phòng cho Qwen nếu backend in-process không ép được vi: chạy `qwen-asr-serve` (vLLM) và trỏ STT OpenAI-compatible của s2s vào đó (**Reported** là có route `audio.transcriptions`). Nhưng như vậy lại có thêm process, cần ghi rõ trong báo cáo.

7. Trỏ `--responses_api_base_url` vào `llm-tap` (`http://127.0.0.1:8110/v1`), tap forward tới máy LLM. Tap phải pass-through SSE từng event và đóng upstream khi client đóng. Chạy R6 cả có và không có tap để chắc tap không làm hỏng cancel `[ĐX]`.

**Acceptance M1:**

- Từ máy client, chạy 10 lượt R0/C1 liên tiếp không lỗi. Transcript là tiếng Việt, bot trả lời bằng tiếng Việt, ngắt lời bot thì bot im. Log s2s có latency STT/LLM/first-TTS-audio cho từng response.
- **LLM → TTS theo mệnh đề** `[ĐX]`: với câu trả lời ≥ 2 câu, request TTS đầu (`tts-proxy` `t_recv`) tới **trước** `llm_done` của `llm-tap`. Chunk không cắt giữa số tiền, ngày, viết tắt hoặc ý dang dở (kiểm bằng `--log-content` trong phiên test). Nếu fail thì áp dụng D6 trước M4.
- `tts-proxy` forward audio đầu khi VieNeu vẫn đang sinh (`proxy_ttfb_ms` ≪ `total_ms`).

---

## 5. Mốc M2 — Bộ đo (1.5 ngày, song song M1)

### 5.1 Ghi âm 2 kênh (voice-to-voice phía client)

Đề xuất `[ĐX]` ghi bằng phần mềm trên máy client (**Ngoài wiki**, cần thử):

- Kênh 1: mic thô (thiết bị mic mà trình duyệt dùng). Kênh 2: monitor/loopback của thiết bị phát.
- Linux/PipeWire: ghi cả hai nguồn bằng **một** lệnh `ffmpeg -f pulse -i <mic> -f pulse -i <sink>.monitor -filter_complex amerge=inputs=2` ra WAV 48 kHz. macOS cần thiết bị loopback (ví dụ BlackHole + Aggregate Device). Windows dùng WASAPI loopback.
- **Hiệu chuẩn offset** mỗi phiên: phát một click qua loa (C2/C4) hoặc một click ngắn ở đầu file, đo độ lệch giữa 2 kênh, rồi trừ đi khi phân tích.
- Phương án dự phòng: audio interface 2 input (mic + line-out loopback bằng cáp).

### 5.2 `analyze_audio.py`

1. Chạy Silero VAD offline riêng từng kênh, ra các đoạn speech.
2. **Voice-to-voice:** với mỗi lượt, lấy điểm kết thúc đoạn speech của user trên kênh 1 mà ngay sau đó là đoạn bot trên kênh 2. v2v = `bot_onset(ch2) − user_offset(ch1)`.
3. **Barge-in:** user bắt đầu nói (kênh 1) trong lúc kênh 2 đang có tiếng → thời gian tới khi kênh 2 im. Nếu kênh 2 không im, ghi là "ngắt trượt".
4. **Ngắt nhầm:** kênh 2 dừng giữa chừng trong khi không có user speech thật.
5. Ở C2/C4 (loa ngoài), kênh 1 có cả tiếng bot. Chỉ chấp nhận đoạn speech ở kênh 1 khi kênh 2 im, hoặc khi năng lượng kênh 1 vượt mức echo đã hiệu chuẩn. Mọi trường hợp mơ hồ được xuất thành **label track Audacity** để người đo xác nhận bằng tai, sau đó phân tích lại từ label đã sửa (**Synthesis**: bán tự động thay vì tin hoàn toàn vào VAD).
6. Output: `runs/<R>/<C>/turns.csv` với các cột `turn, type, user_offset_s, bot_onset_s, v2v_ms, bargein_ms, flags`.

### 5.3 Log server

- `parse_s2s_log.py`: rút latency STT, LLM, first-TTS-audio, speech-to-audio cho từng response, cộng các sự kiện turn (soft-end, kết quả Smart Turn complete/incomplete, reopen/revision, commit) từ log s2s (định dạng log **TBD**, xem ở M1). Mốc nào log không có thì ghi là thiếu, không suy ra.
- **Join** `[ĐX]`:
  - Phía server (s2s, `llm-tap`, `tts-proxy`, `clone-tts` cùng chạy trên máy GPU) dùng chung một clock. Join theo ID (`response_id`/`item_id` nếu s2s log, `req_id`) và timestamp để dựng timeline mỗi lượt: `soft_end → stt_done → llm_first_token → tts_req_first → llm_done → commit → tts_first_byte`.
  - Client ↔ server: clock khác nhau nên chỉ join theo thứ tự lượt làm fallback. Đối chiếu chéo số response, reopen và cancel ở hai phía; lượt lệch được đánh dấu và loại khỏi phân tích stage, vẫn giữ cho v2v. Nếu đã sửa JS demo (R8), log thêm `response_id` kèm `performance.now()` của event audio đầu để join theo ID.
- `vram_sampler.sh`: `nvidia-smi --query-gpu=timestamp,memory.used,utilization.gpu --format=csv -lms 500` chạy suốt run, lấy peak.
- `manifest.py`: ghi `run_id`, thời điểm, git commit của repo PoC, version pip, image digest, commit `nemo-speech`, HF revision và checksum của checkpoint, preset/voice, các cờ s2s đầy đủ, driver/CUDA, thời gian warmup.

### 5.4 Phiếu

- `phieu_quan_sat.csv`: đúng cột của spec §5.4 (`run | điều kiện | lượt | loại lượt | v2v_ms | cắt lời sớm? | barge-in kết quả | lỗi ASR | lỗi TTS | ghi chú`). `v2v_ms` được điền tự động từ `turns.csv`. `loại lượt` thêm nhãn timing: `normal`, `incomplete` (Smart Turn), `reopen`, `bargein`, `post-idle`, và cờ `filler` nếu audio đầu chỉ là tiếng đệm `[ĐX]`.
- `phieu_nghe_tts.csv`: `run, lượt, lỗi thanh điệu, đọc sai số/tên, ngắt nghỉ lạ, giật/underrun, điểm 1–5, ghi chú`.
- Mã lỗi cố định để phân loại được ở M6:
  - ASR: `A-NUM`, `A-NAME`, `A-NEG`, `A-CS` (code-switch), `A-HALLU`, `A-TRUNC`.
  - TTS: `T-TONE`, `T-NUM`, `T-NAME`, `T-PROS`, `T-GLITCH`.
  - Turn: `E-CUT` (cắt lời sớm), `E-SLOW` (chờ > ~2 s), `B-MISS`, `B-FALSE`.

**Acceptance M2:** trên một phiên thử 5 lượt, `turns.csv` khớp với đo tay bằng Audacity trong khoảng ±50 ms (**Synthesis**). Log s2s join đúng lượt.

---

## 6. Mốc M3 — Thành phần thay thế (2.5–3 ngày)

### 6.1 ASR-Q17 (R1)

Chỉ đổi checkpoint sang `Qwen/Qwen3-ASR-1.7B` trong `runs.yaml`. Đo peak VRAM cùng VieNeu.

### 6.2 ASR-NEM (R2)

- `nemo-speech serve --asr-model nemotron-3.5 <port-flag> 8090`. Ngôn ngữ đặt theo kết quả R1: field request, cờ server, hoặc `stt-shim`. Ở CLI, dạng locale là `--language vi-VN` (hoặc `auto`) (**Reported**, raw card Nemotron). Dùng `nemo-speech transcribe file.wav --language vi-VN` làm mốc đối chiếu cho R1.
- `stt-shim` (nếu cần, khoảng 0.5 ngày): nhận `/v1/audio/transcriptions` từ s2s, ép `language=vi-VN`, forward sang `nemo`, và bỏ tag `<vi-VN>` nếu có (**Reported**: chế độ auto gắn tag sau dấu câu cuối).
- Trỏ STT OpenAI-compatible của s2s vào `:8090` hoặc `:8091`. Nhắc lại trong báo cáo: R2 là turn-final qua HTTP, **không** phản ánh lợi thế streaming (spec §3.3).

### 6.3 Reference clone + VieNeu clone (R3)

- Thu 1 reference **có consent bằng văn bản**: 8–10 s, phòng yên tĩnh, 1 người nói, kèm transcript chính xác từng chữ. 8–10 s nằm trong vùng hợp lệ của cả ba model: VieNeu 3–8 s (tự cắt về ≤ 8 s), G-OmniVoice 3–10 s, Gwen "vài giây" (**Reported**). Nên cắt sẵn **≤ 8 s** để cả ba dùng đúng cùng một file `[ĐX]`.
- VieNeu: đăng ký giọng bằng `POST /v1/voices` (clone từ file upload, **Reported**), ghi `voice_id` vào `voices.yaml`. Nếu API không clone được thì R3 bị bỏ và R4/R5 so với R0 (spec §4).
- File ref và consent lưu ngoài repo. Không ghi đường dẫn hay embedding vào log.

### 6.4 `clone-tts` server (R5 Gwen; R4 fallback G-OmniVoice) — khoảng 1 ngày

```text
POST /v1/audio/speech  {model, input, voice, response_format: pcm|wav}
   → header X-Sample-Rate / X-Channels / X-Dtype; body pcm s16le hoặc wav
GET  /health → 200 sau khi load + warmup 2 câu
```

- **Backend `gwen`:** `Qwen3TTSModel.from_pretrained("g-group-ai-lab/gwen-tts-0.6B", device_map="cuda:0", dtype=bfloat16[, attn_implementation="flash_attention_2"])`, rồi `generate_voice_clone(text, language="Vietnamese", ref_audio, ref_text, **cfg)` với cfg khuyến nghị (`temperature=0.3, top_k=20, top_p=0.9, repetition_penalty=2.0, subtalker_*`, **Reported**). Sample rate lấy từ `sr` model trả về.
- **Backend `gomni`:** `OmniVoice.from_pretrained("g-group-ai-lab/g-omnivoice", device_map="cuda:0", dtype=float16)`, rồi `generate(text, ref_audio, ref_text)`, ra 24 kHz (**Reported**).
- **Giả-streaming theo câu** `[ĐX]`: tách `input` theo `.?!…;:`, sinh từng câu và stream audio của câu đó ngay khi xong. Cả hai card đều khuyên chia câu (**Reported**). Nếu s2s đã gửi theo mệnh đề (Day 0) thì bước này gần như không làm gì.
- Mỗi lúc chỉ 1 request (`asyncio.Lock`, model chạy trong thread). Kiểm tra client disconnect **giữa các câu** để hủy; không hủy được giữa một lần `generate` (**Synthesis**, ghi vào báo cáo như một giới hạn).
- Hệ quả barge-in: bot phải im ngay ở client (s2s `response.cancel`/clear) mà không chờ `generate` kết thúc. Nhưng lock vẫn bị giữ tới hết câu đang sinh, nên lượt mới có thể phải chờ GPU. Log `lock_wait_ms` cho mỗi request và đo riêng **user onset → bot im** với **cancel → hết compute** (spec §5.3).
- Đặt sau `tts-proxy` để dùng chung lớp text rule và audio contract.

### 6.5 G-OmniVoice qua handler (R4, nếu R3 pass)

`--tts omnivoice --omnivoice_device cuda --omnivoice_ref_audio <ref.wav> --omnivoice_ref_text "<transcript>"` + model path, nhiều khả năng là `--omnivoice_model_name g-group-ai-lab/g-omnivoice` (**Synthesis** từ quy ước tên cờ trong raw; kiểm ở R3). Handler phải chờ hết câu mới phát, rồi chuyển sang khối 16 kHz `int16` (**Reported**).

> **Điểm cần chốt (D1):** nếu R7 cho thấy s2s **không có hook text**, R4 qua handler sẽ **không** đi qua lớp text rule, trong khi R0/R3/R5 có. Như vậy kết quả bị lẫn yếu tố. Đề xuất: khi đó chạy R4 qua `clone-tts gomni` + `tts-proxy`. Chi phí gần bằng 0 vì cùng codebase với Gwen. Việc này lệch khỏi Q19, cần người quyết định.

**Acceptance M3:** mỗi thành phần pass smoke test (1 câu tiếng Việt end-to-end qua s2s ở C1), có peak VRAM của tổ hợp, và `runs.yaml` đủ R0–R5.

---

## 7. Kịch bản hội thoại (protocol/kich_ban.md)

Thứ tự cố định, cùng một tester đọc cho mọi run. Mọi entity là **hư cấu**, không dùng số hay tên thật. Đây là bản nháp (**Synthesis**), được chỉnh ở M4.

| # | Loại | Tester nói | Kiểm tra |
|---|---|---|---|
| 1 | thường | "Chào bạn, bạn giúp được tôi những việc gì?" | v2v, giọng |
| 2 | thường | "Mùa này Đà Lạt thường có thời tiết thế nào?" | |
| 3 | thường | "Gợi ý cho tôi một món ăn sáng đơn giản." | |
| 4 | thường | "Làm sao để ngủ ngon hơn?" | |
| 5 | thường | "Giải thích ngắn gọn trí tuệ nhân tạo là gì." | |
| 6 | thường | "Nói thêm về ý thứ hai đi." | ngữ cảnh |
| 7 | entity: tiền + tên | "Tôi muốn chuyển một triệu hai trăm năm mươi nghìn đồng cho anh Nguyễn Văn Bình." | A-NUM, A-NAME |
| 8 | entity: SĐT | "Số của tôi là không chín một hai, ba bốn năm, sáu bảy tám. Nhắc lại giúp tôi." | A-NUM, T-NUM |
| 9 | entity: ngày giờ | "Đặt lịch lúc hai giờ rưỡi chiều thứ Sáu, ngày mười bốn tháng mười một." | A-NUM |
| 10 | entity: địa danh | "Tôi đang ở Thành phố Hồ Chí Minh, muốn đi Buôn Ma Thuột." | A-NAME, T-NAME |
| 11 | code-switch | "Gửi giúp tôi email về buổi meeting với team marketing." | A-CS |
| 12 | phủ định | "Đừng hủy lịch hẹn đó." | A-NEG |
| 13 | sửa lời | "Không, không phải thứ Sáu, là thứ Bảy." | A-NEG, ngữ cảnh |
| 14 | lệnh ngắn | "Dừng lại." | từ ngắn bị nuốt |
| 15 | ngập ngừng | "Tôi muốn hỏi về… *(nghỉ 1.5 s)* …cách đăng ký học lái xe." | E-CUT |
| 16 | ngập ngừng | "Cho tôi biết, ừm… *(nghỉ 2 s)* …giá vé tàu đi Hà Nội." | E-CUT |
| 17 | barge-in | "Kể cho tôi nghe về lịch sử Hà Nội." → sau ~2 s bot nói: "Thôi, nói ngắn thôi." | B-MISS, thời gian bot im |
| 18 | barge-in | "Kể tên các tỉnh miền Tây." → "Khoan đã." | |
| 19 | barge-in | "Kể một câu chuyện cổ tích." → "Đổi chuyện khác đi." | |
| 20 | đọc số | "Một trăm hai mươi lăm nhân tám bằng bao nhiêu?" | prompt viết số bằng chữ, `digits_left` |
| 21 | đọc số | "Ba phần trăm của hai triệu đồng là bao nhiêu?" | T-NUM |
| — | sự kiện nhiễu | Trong lúc bot đang trả lời lượt 2 và lượt 5: ho một tiếng, gõ phím ~2 s | B-FALSE (không tính là lượt) |
| — | idle `[ĐX]` | Im lặng ~30 s trước lượt 20 (không phát audio) | Nhãn `post-idle`: đo phạt sau GPU idle thay vì chỉ che bằng warmup |

---

## 8. Mốc M4 — Pilot (0.5 ngày)

- Chạy R0 × C1–C4 một lượt đầy đủ: đủ kịch bản, đủ thiết bị, đủ phiếu.
- Sửa harness, kịch bản, vị trí nguồn nhiễu và âm lượng. Chốt và **ghi lại** setup âm thanh: thiết bị, mức âm lượng hệ thống, khoảng cách loa và nguồn nhiễu, nội dung nhiễu (cùng một file TV/nhạc lặp lại).
- Đo overhead của `tts-proxy`. Kiểm tra `--log_transcripts` ghi ra đúng thư mục ngoài repo.
- Đo buffer playback thực của browser demo: khoảng từ `tts_first_byte` (server) tới bot onset (loopback), sau khi trừ network ước lượng. Ghi underrun/giật. Chỉ ghi nhận ở Phase 1; buffer nhỏ nhất chưa chắc tốt nhất, tune ở Phase 2.
- Dữ liệu pilot **không** dùng cho kết quả.

---

## 9. Mốc M5 — Chạy ma trận (1.5–2 ngày)

Quy trình cho mỗi run (tự động hóa bằng `start_run.sh <R>`):

```text
stop_all → start ASR/TTS của run → health OK → warmup (TTS câu mẫu + 3 lượt hội thoại bỏ đi)
→ manifest.json → vram_sampler on → [C1 → C2 → C3 → C4]: record_stereo + kịch bản + phiếu
→ vram_sampler off → copy log s2s/proxy/clone-tts → analyze_audio → kiểm label mơ hồ
```

- Thứ tự run: R0, R1, R2, R3, R4, R5, rồi **R0′** (R0 lặp lại, chỉ C1) để phát hiện drift do tester mệt, mạng hoặc nhiệt GPU `[ĐX]`.
- Nghỉ giữa các điều kiện. Một phiên mỗi điều kiện khoảng 10 phút, mỗi run khoảng 1–1.5 giờ tính cả chuyển đổi, nên ~2 run mỗi buổi.
- Bật `--log_transcripts` trong mọi phiên đo, vì G2 cần transcript. Log có nội dung chỉ nằm trên máy GPU và được xóa theo retention sau khi báo cáo xong (spec §2).
- Không sửa code hay cấu hình giữa các run. Nếu buộc phải sửa (bug), chạy lại mọi run đã chạy trước đó với bản sửa, hoặc ghi rõ trong báo cáo.

---

## 10. Mốc M6 — Phân tích và báo cáo (1.5 ngày)

`aggregate.py` sinh các bảng. Báo cáo viết vào `outputs/ket-qua-poc-speech-to-speech-tieng-viet-phase-1.md`.

1. **Latency (G1):** v2v P50/P95 cho mỗi run, **gộp C1–C4** (n ≈ 80). Theo từng điều kiện chỉ báo median + max. Với n ≈ 20, P95 thực chất gần bằng max (**Synthesis**) `[ĐX]`. Thêm latency từng stage (STT, LLM, first-TTS-audio) từ log s2s. So với mục tiêu mềm P50 ≤ 1.5 s / P95 ≤ 2.5 s.
   - Tách theo loại lượt (`normal`, `incomplete`, `reopen`, `bargein`, `post-idle`); báo tỷ lệ lượt `incomplete` vì nó quyết định P95 (spec §1).
   - **Phân rã output-hold vs compute** từ timeline server: với mỗi lượt, `commit − soft_end` so với `tts_req_first − soft_end`. Nếu phần lớn lượt có response sẵn sàng trước khi gate mở thì nút thắt là turn tracker, không phải model. Đây là căn cứ cho A/B grace (D7) và Nemotron streaming (D8).
2. **ASR (G2):** đếm lỗi theo mã trên các lượt 7–14, cho mỗi run.
3. **TTS (G3):** đếm lỗi theo mã, điểm 1–5 trung bình, `digits_left` trung bình mỗi lượt (đo mức LLM tuân thủ prompt).
4. **Endpointing / barge-in (G4):** `E-CUT`, `E-SLOW`, `B-MISS`, `B-FALSE` theo run × điều kiện; thời gian tới khi bot im (median/max).
5. **A/B (G5):** chênh lệch của mỗi run so với baseline của nó (R1/R2 so với R0; R4/R5 so với R3). Ghi chú R0′ so với R0 (drift).
6. **Tài nguyên:** peak VRAM, thời gian warmup.
7. **Giới hạn:** R2 là turn-final; G-OmniVoice và Gwen không stream; n nhỏ; một tester; các phương án fallback đã kích hoạt ở Day 0; băng thông audio thực tế tới client (R10); độ mịn chunk LLM→TTS thực tế và việc có vá s2s hay không (R11/D6); buffer playback thực của trình duyệt.
8. **Đề xuất Phase 2:** dựa trên số liệu, đối chiếu backlog trong spec §8 (ví dụ: chuyển sang Namo nếu tỷ lệ cắt lời sai > 10%).

---

## 11. Lịch, phụ thuộc và các điểm cần chốt

### 11.1 Lịch dự kiến (1 kỹ sư)

| Ngày | Việc |
|---|---|
| 1 | M0: R2, R7, R4 (tone-server), R8, R6; dựng `llm-tap` (~0.25 ngày) |
| 1.5 | M0: R1, R3, R11, R12; chốt `runs.yaml`; cập nhật spec nếu cần; quyết D6 nếu R11 fail |
| 2–3 | M1: VieNeu, tts-proxy (+test), s2s + LLM + browser, R0 chạy được · M2 song song: ghi âm, hiệu chuẩn |
| 4 | M2: analyze_audio, parse log, manifest, phiếu |
| 5–6.5 | M3: Q17, NEM (+shim), reference + VieNeu clone, clone-tts (gwen/gomni), handler omnivoice |
| 7 | M4 pilot |
| 8–9 | M5 R0–R5 + R0′ |
| 10–11 | M6 phân tích + báo cáo |

```text
M0 ─► M1 ─► M3 ─► M4 ─► M5 ─► M6
  └──► M2 ──────┘
```

Có thể chạy R0/R1 sớm ngay sau M2 trong khi M3 làm tiếp phần NEM/Gwen. Nhưng mọi run phải dùng cùng một bản harness đã chốt ở M4.

### 11.2 Đề xuất thêm so với spec `[ĐX]`

| # | Đề xuất | Lý do |
|---|---|---|
| X1 | Đặt **mọi** TTS HTTP (cả VieNeu) sau `tts-proxy` | Spec đã cho phép khi R7 fail. Làm vậy cho cả 3 backend có chung text rule, audio contract và log, giúp A/B công bằng |
| X2 | `tone-server` + stub STT ở Day 0 | Biết chính xác s2s gửi/nhận gì, thay vì đoán (R4, Gwen contract) |
| X3 | Reference clone ≤ 8 s dùng chung | Nằm trong vùng hợp lệ của cả 3 model |
| X4 | Giả-streaming theo câu trong `clone-tts` | Giảm TTFA cho input nhiều câu, rất ít rủi ro |
| X5 | Chạy R0′ ở cuối | Phát hiện drift |
| X6 | Báo P95 trên dữ liệu gộp C1–C4 | n = 20 mỗi điều kiện không đủ cho P95 |
| X7 | Phân tích audio bán tự động (label Audacity) | Ở chế độ loa ngoài, VAD không phân biệt được user với echo |
| X8 | `llm-tap` + timeline server theo ID | Thiếu mốc LLM thì không tách được output-hold với compute; join theo thứ tự dễ gán sai khi có reopen/cancel |
| X9 | Acceptance M1 về LLM→TTS theo mệnh đề + test giữ streaming của proxy | Đây có thể là tối ưu lớn nhất mà chưa cần đổi model |
| X10 | Nhãn loại lượt (`incomplete`, `reopen`, `post-idle`, `filler`) + lượt idle trong kịch bản | P95 gộp che mất nhánh chậm; warmup che mất phạt sau idle |

### 11.3 Điểm cần người quyết định

| # | Câu hỏi | Mặc định nếu không chốt |
|---|---|---|
| D1 | R7 fail: chạy R4 qua handler (lệch text rule) hay qua `clone-tts gomni` + proxy? | Qua proxy (X1) |
| D2 | Máy/OS client để ghi âm 2 kênh? | Linux + PipeWire |
| D3 | Một tester cho mọi run? Ai là người cho reference clone? | Một tester; ref là người khác, có consent |
| D4 | Nơi lưu và thời hạn giữ bản ghi, log có transcript, ref/consent | Trên máy GPU, ngoài repo, xóa sau 30 ngày kể từ khi có báo cáo |
| D5 | Capture trước vào `raw/` các tài liệu con còn thiếu (s2s `docs/openai-compatible-tts.md`, `docs/openai-compatible-stt.md`, `src/speech_to_speech/STT/README.md`, `TTS/README.md`, `demo/README.md`, `docs/response-latency.md`; NeMo-Speech.cpp `docs/server.md`, `docs/api.md`; VieNeu `docs/streaming.md`) rồi ingest, để Day 0 chỉ còn việc chạy thử? | Có. Tiết kiệm khoảng nửa ngày Day 0 và làm wiki đầy đủ hơn |
| D6 | R11 fail (s2s gửi cả câu trả lời một lần, hoặc chỉ sau khi LLM xong): vá chunker theo mệnh đề ở consumer LLM trong s2s (lệch nhẹ khỏi "chỉ cấu hình"), hay ghi là giới hạn? | Vá trước M4 nếu ≤ ~1 ngày, áp dụng cho mọi run nên A/B vẫn công bằng; pin commit bản vá trong manifest. Nếu lớn hơn thì ghi giới hạn và đưa lên đầu Phase 2 |
| D7 | Thêm run tùy chọn **R0-G** (R0 với `--speculative_reopen_ms` 600 rồi 400, chỉ C1/C2) sau M5 nếu còn thời gian? Lệch Q30 nên cần người quyết | Không. Để Phase 2, dựa trên phân rã output-hold ở M6 |
| D8 | Nếu timeline R0 cho thấy STT sau soft-end chiếm phần lớn v2v (vượt grace), kéo Nemotron streaming về cuối Phase 1? | Không. Ghi làm ưu tiên Phase 2; chưa thêm two-pass |

---

## 12. Rủi ro triển khai (bổ sung cho spec §6)

| Rủi ro | Dấu hiệu | Xử lý |
|---|---|---|
| Client TTS HTTP của s2s gửi cả câu trả lời một lần, không theo mệnh đề, hoặc chỉ gửi sau khi LLM xong (R11) | Log `tone-server` chỉ thấy 1 request mỗi response; request đầu tới sau `llm_done` | **Không chấp nhận mặc định là giới hạn:** áp dụng D6. Chia câu ở proxy sau khi đã nhận cả câu trả lời không lấy lại thời gian chờ LLM, và với VieNeu (đã stream audio) lợi ích rất nhỏ. Giả-streaming theo câu (X4) chỉ giảm phần synthesis cho Gwen/G-Omni |
| Output gate là nút thắt chính | Response sẵn sàng (`tts_req_first`) trước khi commit; nhiều lượt `incomplete` gần mốc 2 s | Không tune ở Phase 1 (Q30); báo phân rã ở M6 và đề xuất A/B grace (D7) |
| `llm-tap` làm sai kết quả đo | Khác biệt TTFT hoặc cancel khi có/không có tap | Kiểm ở M1 (R6 hai cách); nếu lệch thì bỏ tap, dùng log server LLM |
| Browser demo không cho đặt session language hay instructions | Không thấy field trong demo | Sửa nhỏ JS của demo, hoặc dùng cờ server; ghi lại thay đổi |
| Drift clock client giữa 2 nguồn ghi | Offset click đầu và cuối phiên lệch > 20 ms | Ghi bằng audio interface 2 kênh |
| Echo loa ngoài làm VAD offline sai | Nhiều label mơ hồ ở C2/C4 | Rà tay (X7); giảm âm lượng theo setup đã chốt |
| Weights tải lại giữa run | Warmup lâu bất thường | Pre-cache, `HF_HUB_OFFLINE=1` (**Reported** cho s2s) |
| Phạt clock GPU sau khi nghỉ | Lượt đầu mỗi điều kiện chậm hơn rõ | 3 lượt warmup trước mỗi điều kiện, không chỉ đầu run; tùy chọn khóa clock |

---

## 13. Definition of done (trùng tiêu chí của spec §7)

- [ ] `docs/day0.md` có kết quả R1–R8, R10–R12; spec đã được cập nhật theo các cờ và fallback thật; D6 đã quyết nếu R11 fail.
- [ ] `runs.yaml`, manifest và log đủ cho R0–R5 × C1–C4 (cộng R0′).
- [ ] Bảng P50/P95 voice-to-voice và latency từng stage, tách theo loại lượt, kèm phân rã output-hold vs compute.
- [ ] Danh sách lỗi ASR/TTS/turn đã phân loại theo mã.
- [ ] Báo cáo `outputs/ket-qua-poc-speech-to-speech-tieng-viet-phase-1.md` có đề xuất Phase 2 dựa trên số liệu.
- [ ] Dữ liệu cá nhân nằm ngoài repo, có hạn xóa (D4).
