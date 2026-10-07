Tôi đã đọc 3 tài liệu và đối chiếu với `wiki/index.md` và `raw/`. Tôi chưa sửa wiki hay tài liệu nào. Phần lớn model trong PoC đã có trang wiki. Chỗ còn thiếu là tài liệu về cách nối các thành phần: tên cờ, định dạng API và cách xử lý audio. Phần lớn ô TBD ở Day 0 nằm đúng ở chỗ này.

## 1. Thành phần PoC dùng và mức độ có trong wiki

| Thành phần | Vai trò | Trang wiki | Mức cần kiểm |
|---|---|---|---|
| HF speech-to-speech (`serve`, turn tracker, browser demo) | Điều phối | Có [speech-to-speech-pipeline.md](wiki/speech-to-speech-pipeline.md), nhưng chỉ từ README | **Cao nhất.** Thiếu tài liệu con (xem mục 3) |
| Smart Turn v3.2 | Xác định user đã nói xong chưa | Chỉ có [turn-detection-models.md](wiki/turn-detection-models.md) (`draft`), nguồn duy nhất là AI report | **Cao.** Thông số 81.27% / FP 14.84% cho tiếng Việt chưa có nguồn gốc |
| Silero VAD v5 | VAD | Có | Thấp |
| Qwen3-ASR 0.6B/1.7B `-hf` | ASR baseline | Có [qwen3-asr-family.md](wiki/qwen3-asr-family.md) | Trung bình. Thiếu tên cờ ngôn ngữ trong s2s |
| Nemotron 3.5 + NeMo-Speech.cpp `serve` | ASR cho R2 | Có cả hai trang | **Cao.** Chưa có `docs/server.md` và `docs/api.md` (R1) |
| VieNeu v3 Turbo (Docker `api-gpu`) | TTS baseline | Có | Cao. License còn mâu thuẫn; thiếu `docs/streaming.md` và schema `POST /v1/voices` |
| G-OmniVoice qua handler `omnivoice` | TTS cho R4 | Có [g-omnivoice.md](wiki/g-omnivoice.md) và [omnivoice.md](wiki/omnivoice.md) | Trung bình. Chưa biết handler có nạp được checkpoint G-OmniVoice không |
| Gwen-TTS + gói `qwen-tts` | TTS cho R5 | Có [gwen-tts-0.6b.md](wiki/gwen-tts-0.6b.md) | Trung bình. Base model `Qwen3-TTS-12Hz-0.6B-Base` chưa có trang riêng |
| faster-qwen3-tts | Thư viện mà extra `omnivoice` cài kèm | Có | Thấp. Chỉ cần kiểm xung đột Transformers 5.x |
| LLM endpoint (chưa biết model hay server nào) | LLM | Không có | **Cao.** Chưa biết có streaming không, có hủy được không, tắt thinking thế nào (R6) |
| Quy ước OpenAI Audio API (`/v1/audio/speech`, `/v1/audio/transcriptions`, `pcm` 24 kHz) | Định dạng gọi giữa các service | Không có, kế hoạch đánh dấu "Ngoài wiki" | Cao. Quy ước này quyết định R4 |
| `getUserMedia` AEC, yêu cầu HTTPS để dùng mic | Phía client | Chỉ nhắc qua | Thấp đến trung bình (R8) |

Phase 2 sẽ cần: Namo (chỉ có từ AI report), ECAPA/CAM++, DeepFilterNet/RNNoise, Qwen3-ASR qua vLLM Realtime (đang thử nghiệm). Chưa cần làm bây giờ.

Bản thiết kế còn nhắc tới faster-whisper, PhoWhisper, ChunkFormer, VoxCPM2, Supertonic 3, Pipecat, LiveKit… Các model và runtime này đều đã có trang, PoC cũng không dùng, nên không phải việc gấp.

## 2. Chỗ sai hoặc cần sửa trong tài liệu

1. **Nemotron có thể stream được ngay ở Phase 1.** Spec §2.1/§3.3 cho rằng Nemotron đi qua HTTP nên không stream được. Nhưng `raw/speech-to-speech.md` (dòng 237–266) liệt kê STT backend "OpenAI Realtime transcription — compatible WebSocket server" và nhắc tới "stateful streaming STT" có "partial transcripts". `raw/NeMo-Speech.cpp.md` (dòng 134–135) cũng có "realtime WebSocket transcription". Nếu hai bên khớp giao thức thì có thể stream Nemotron mà không phải tự viết handler. Nên kiểm trước khi chốt D8.
2. **Checkpoint 1.7B bị ghi sai tên.** Kế hoạch §6.1 ghi `Qwen/Qwen3-ASR-1.7B`. Backend built-in của s2s chạy qua Transformers nên phải dùng `Qwen/Qwen3-ASR-1.7B-hf`, đúng như §0.1 của chính kế hoạch đã ghi.
3. **License G-OmniVoice không thống nhất.** Card G-OmniVoice khai `apache-2.0`, nhưng weights gốc OmniVoice là CC-BY-NC (`raw/OmniVoice.md:783`). PoC nội bộ vẫn dùng được, nhưng nên ghi rõ là "mâu thuẫn license từ model gốc" thay vì chỉ ghi "CC-BY-NC".
4. **Gwen nhận tham số `language="Vietnamese"` hay không chưa rõ.** Qwen3-TTS gốc không có tiếng Việt, nên cần kiểm gói `qwen-tts` có chấp nhận giá trị này không, hay phải dùng `auto`.
5. **License VieNeu vẫn mâu thuẫn trong cùng README:** dòng 565 ghi "personal use", dòng 579 ghi "Apache 2.0". PoC không bị ảnh hưởng, nhưng không được đưa kết quả này ra ngoài.

## 3. Nên đưa vào `raw/` rồi ingest vào wiki (theo thứ tự ưu tiên)

| # | Nguồn cần lấy | Giải quyết | Trang wiki được cập nhật |
|---|---|---|---|
| 1 | HF s2s: `docs/openai-compatible-stt.md` (có phần stateful streaming), `docs/openai-compatible-tts.md`, `docs/response-latency.md`, `src/speech_to_speech/STT/README.md`, `TTS/README.md`, `demo/README.md`, `arguments_classes/` | R2, R4, R7, R8, R10, R11, R12; điểm 1 ở mục 2 | speech-to-speech-pipeline |
| 2 | NeMo-Speech.cpp `docs/server.md`, `docs/api.md` | R1, cổng, giao thức WebSocket realtime | nemo-speech-cpp |
| 3 | Card hoặc repo gốc của Smart Turn v3.2 (pipecat-ai/smart-turn) | Kiểm số liệu tiếng Việt; đây là bộ phận giữ output 800 ms / 2 s nên quyết định sàn latency | turn-detection-models, có thể thêm trang `smart-turn` |
| 4 | VieNeu `docs/streaming.md` và tài liệu API cho `/v1/voices` | R3 clone, định dạng audio, cách warmup | vieneu-tts-v3-turbo |
| 5 | Tài liệu tham chiếu OpenAI Audio API (speech/transcriptions/realtime) | Thay mục "Ngoài wiki" bằng nguồn có dẫn chứng | Trang mới về quy ước OpenAI-compatible audio |
| 6 | Card `Qwen/Qwen3-TTS-12Hz-0.6B-Base` và README `qwen-tts` | Điểm 4 ở mục 2, lineage của Gwen | Trang mới hoặc mở rộng gwen-tts-0.6b |
| 7 | Tài liệu của server LLM đang dùng (vLLM / llama.cpp / …), khi đã biết | R6 (hủy được không), cách tắt thinking | Trang mới, domain `llm` |

**Không nên đưa vào wiki:** ffmpeg, PipeWire, BlackHole, soxr, Audacity, Caddy/nginx, `nvidia-smi`. Đây là công cụ dùng để đo, không phải tri thức về voice pipeline; chỉ cần ghi trong README của repo PoC. Kết quả đo của PoC sau Phase 1 thì nên ingest, vì đó sẽ là số đo tiếng Việt đầu tiên có điều kiện đo giống nhau giữa các cấu hình.

Bạn có muốn tôi tải nguồn #1–#3 về `raw/` rồi chạy `wiki-ingest` không? Ba nguồn này gỡ được nhiều TBD nhất trước Day 0.