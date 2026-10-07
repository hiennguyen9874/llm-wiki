# Lựa chọn và thiết kế TTS realtime cho tiếng Việt

> **Loại tài liệu:** bài viết tổng hợp (deliverable trong `outputs/`), không phải tri thức canonical của wiki.
> **Ngày:** 2026-10-07.
> **Cơ sở:** chỉ dùng wiki đã compile. Nguồn chính: [Vietnamese Realtime TTS Selection](../wiki/vietnamese-realtime-tts-selection.md) và [TTS Model Survey](../wiki/tts-model-survey.md). Nguồn bổ sung: [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md), [VieNeu-TTS v3 Turbo](../wiki/vieneu-tts-v3-turbo.md), [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md) và [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md).
> **Phạm vi bằng chứng:** không mở `raw/`, không tải weights, không chạy inference, không nghe audio, không đo benchmark. Mọi con số đều do vendor, tác giả hoặc report công bố (**Reported**). Mọi thứ tự ưu tiên, kiến trúc và tham số đề xuất là suy luận tổng hợp (**Synthesis**). Chưa có phép so sánh MOS, TTFA hay lỗi phát âm tiếng Việt nào được đo trên cùng điều kiện giữa các model.

---

## 0. TL;DR

1. **Baseline triển khai:** [VieNeu-TTS v3 Turbo](../wiki/vieneu-tts-v3-turbo.md). Đây là model Vietnamese-first (vi/en, code-switching). Model có G2P riêng cho tiếng Việt (`sea-g2p`), preset giọng Bắc/Trung/Nam, frame-level audio streaming, đường chạy CPU ONNX và GPU PyTorch, cùng một server `/v1/audio/speech` kiểu OpenAI. Benchmark do tác giả công bố trên RTX 3060: TTFA khoảng 115 ms với 1 stream, 185 ms median với 16 stream.
2. **Hai challenger cần A/B:**
   - [VoxCPM2](../wiki/voxcpm2.md) (2B, Apache-2.0, 48 kHz, có `vi`, có `generate_streaming`) khi ưu tiên cloning/style và có GPU khoảng 8 GB.
   - [Supertonic 3](../wiki/supertonic-3.md) (khoảng 99M, ONNX, có `vi`) khi ưu tiên CPU/on-device. Lưu ý: card của nó chỉ chứng minh API trả về waveform hoàn chỉnh, chưa chứng minh frame-level streaming.
3. **Nhóm expressive, chỉ dùng khi có license thương mại riêng:** [Higgs TTS 3](../wiki/higgs-tts-3-4b.md) và [Fish S2 Pro](../wiki/fish-audio-s2-pro.md). Cả hai đều mạnh và có streaming qua SGLang, nhưng weights là non-commercial, và chất lượng tiếng Việt chưa được chứng minh là vượt VieNeu.
4. **Nhóm cần nghe thử trước khi dùng:** [G-OmniVoice](../wiki/g-omnivoice.md), [Gwen-TTS 0.6B](../wiki/gwen-tts-0.6b.md), [MOSS-TTS Local v1.5](../wiki/moss-tts-local-transformer-v1-5.md) và [Kokoro Vietnamese](../wiki/kokoro-vietnamese.md). Mỗi model có điểm hứa hẹn riêng nhưng đều thiếu ít nhất một trong các yếu tố: streaming, TTFA, benchmark độc lập, hoặc license/lineage rõ ràng.
5. **Không dùng out-of-box cho tiếng Việt:** Qwen3-TTS chính thức (10 ngôn ngữ, không có vi), CosyVoice2/3, Chatterbox, Pocket, Sopro, Soprano, VibeVoice, Breeze, GLM-TTS, IndexTTS và GPT-SoVITS.
6. **Thiết kế quan trọng hơn chọn model.** Chất lượng cảm nhận phụ thuộc nhiều vào các thành phần bao quanh TTS:
   - clause chunker;
   - Vietnamese normalizer cho số, tiền, ngày, đơn vị, viết tắt;
   - lexicon cho tên riêng;
   - hợp đồng audio format rõ ràng;
   - cancellation sạch khi barge-in;
   - warmup và giới hạn concurrency.

   Model chỉ là một tầng trong pipeline.
7. **Đây là thứ tự thử nghiệm, không phải bảng xếp hạng chất lượng.** Quyết định cuối cùng phải dựa trên blind listening test tiếng Việt (150–300 prompt) và đo TTFA P95 dưới tải thực, trên chính phần cứng sẽ triển khai.

---

## 1. Cách đọc bài này

| Nhãn | Ý nghĩa |
|---|---|
| **Reported** | Vendor, tác giả hoặc report tự công bố; chưa kiểm chứng độc lập. |
| **Observed** | Thấy được trong tài liệu (API, field, bảng), nhưng không chứng minh model thực sự nói tốt. |
| **Synthesis** | Suy luận của bài viết từ các bằng chứng được dẫn. |
| **Unverified** | Chưa có sự kiện kiểm chứng. Điều này không có nghĩa là sai. |

Số liệu từ các card khác nhau **không so sánh trực tiếp được**: mỗi card dùng GPU, harness, normalizer và ASR judge khác nhau. TTS Model Survey có một cảnh báo chung, bài này áp dụng theo: chênh lệch WER dưới khoảng 0.3 điểm, hoặc chênh latency dưới khoảng 2 lần giữa hai card khác nhau, thì không đủ để tự nó quyết định lựa chọn.

---

## 2. Bài toán: "TTS realtime tiếng Việt" đòi hỏi gì?

### 2.1. Các trục quyết định

| Trục | Câu hỏi | Vì sao quan trọng với tiếng Việt |
|---|---|---|
| **Ngôn ngữ** | Model có hỗ trợ `vi` chính thức không? Có G2P/frontend tiếng Việt không? | Sáu thanh điệu và dấu; một lỗi G2P đổi nghĩa (`chánh` → `tránh`). Có tên `vi` trong danh sách ngôn ngữ chưa có nghĩa là đọc đúng thanh. |
| **Streaming** | Có phát audio trước khi tổng hợp xong cả câu không? | Voice agent cần tiếng sớm; một API trả full waveform buộc phải chunk theo mệnh đề. |
| **TTFA** | Thời gian đến audio chunk đầu tiên, P50/P95, dưới tải? | Là một phần của critical path voice-to-voice. |
| **RTF mỗi stream** | Sinh audio có nhanh hơn tốc độ phát không? | Nếu RTF lớn hơn 1 thì playback bị giật (underrun). |
| **Concurrency** | Một GPU/CPU chịu được bao nhiêu stream đồng thời mà vẫn giữ P95? | Quyết định chi phí và capacity. |
| **Phần cứng** | GPU consumer, datacenter, CPU, hay edge/MCU? | Loại phần cứng giới hạn ngay danh sách ứng viên. |
| **Giọng** | Preset, cloning zero-shot, LoRA, hay voice design? | Brand voice, sự đồng ý của người được clone (consent), tính nhất quán giọng. |
| **License** | Weights, voicepack, tokenizer và dữ liệu có cho dùng thương mại không? | Đây là **hard gate**, phải xét trước điểm chất lượng. |
| **Code-switch** | Có đọc được từ tiếng Anh xen trong câu tiếng Việt không? | Hội thoại thực tế thường có từ tiếng Anh. |

### 2.2. Hai tầng streaming khác nhau, đừng nhầm

- **Audio-output streaming:** model nhận một đoạn text đã hoàn chỉnh rồi trả audio theo từng chunk/frame trước khi xong câu. VieNeu `infer_stream(text=...)`, VoxCPM2 `generate_streaming(text=...)` và MOSS Local qua SGLang-Omni (`stream=true`, PCM 48 kHz) thuộc loại này (**Reported**).
- **Incremental text-input / bi-streaming:** model nhận tiếp token từ LLM trong khi đang nói. Qwen3-TTS (Dual-Track), CosyVoice và VibeVoice-Realtime quảng cáo khả năng này, nhưng **không checkpoint chính thức nào trong số đó hỗ trợ vi** (**Reported**).

**Hệ quả thiết kế (Synthesis):** với tiếng Việt hiện nay, cầu nối LLM → TTS phải là **clause-level chunking**: gom token thành mệnh đề có nghĩa rồi gọi TTS streaming cho từng mệnh đề. Không nên gọi cách này là native bi-streaming.

### 2.3. Đừng trộn throughput với streaming

Ví dụ điển hình là VieNeu: GPU batched RTF 0.011–0.02 là **tổng audio của nhiều câu trong một batch**, không phải RTF của một stream. RTF của một stream streaming là 0.49–0.59 (**Reported**). Tương tự, RTF rất thấp của OmniVoice (0.025) hay Supertonic không có nghĩa là TTFA thấp, nếu API phải sinh xong cả câu mới trả về.

---

## 3. Bức tranh kiến trúc TTS hiện nay

Catalog trong wiki có 40 dòng model/family TTS. Chúng chia thành bốn nhóm kiến trúc và một nhóm biến thể chuyên tiếng Việt (**Observed** catalog; phân nhóm là **Synthesis** của survey).

### 3.1. Codec-token autoregressive (LLM-style)

- **Cơ chế:** text → LM sinh discrete audio token (multi-codebook RVQ) → codec decoder ra waveform. Ví dụ:
  - Fish S2 Pro: Slow AR 4B theo thời gian + Fast AR 400M cho residual codebook.
  - Higgs TTS 3: 8 codebook, 25 fps, delay pattern.
  - Qwen3-TTS: tokenizer 12.5 Hz, 16 codebook, causal ConvNet decoder.
  - VieNeu v3 Turbo: backbone + codec `MOSS-Audio-Tokenizer-Nano` + acoustic decoder chạy theo từng frame.
- **Ưu điểm (Synthesis):** hợp tự nhiên với audio streaming, và tái dùng được hạ tầng LLM serving (KV cache, continuous batching, SGLang/vLLM).
- **Nhược điểm:** sinh tuần tự nên chi phí cache và concurrency phải đo thực tế; có thể lặp, bỏ chữ hoặc "hallucinate" audio.
- **Điểm cần nhớ cho tiếng Việt:** model to và codec tốt không tự đảm bảo thanh điệu đúng. Frontend/G2P, dữ liệu tiếng Việt và runtime có thể quan trọng hơn kích thước model.

### 3.2. Continuous-latent / diffusion-autoregressive

- **Cơ chế:** LM sinh latent liên tục, sau đó flow-matching hoặc diffusion head giải mã ra audio qua VAE. Ví dụ:
  - VoxCPM2: `LocEnc → TSLM → RALM → LocDiT`, AudioVAE 16→48 kHz, LM rate 6.25 Hz.
  - dots.tts: LLM → flow-matching patch → causal VAE decoder. Bản `mf` được distill xuống NFE 4.
- **Ưu điểm (Synthesis):** tốt cho cloning và prosody, và cho phép đánh đổi quality–latency qua số bước flow.
- **Lưu ý:** diffusion không bắt buộc phải sinh hết cả câu (VoxCPM2 có API streaming). Tuy vậy, số bước flow là một phần ngân sách compute phải quản lý. Con số 6.25 Hz là token rate của LM, không phải TTFA.

### 3.3. Diffusion-LM (non-AR) đa ngôn ngữ rộng

- **Ví dụ:** OmniVoice (600+ ngôn ngữ, RTF thấp nhất được công bố là 0.025) và finetune tiếng Việt G-OmniVoice.
- **Lưu ý:** card và API đã inspect chỉ trả về full waveform (`generate`). Handler OmniVoice trong HF speech-to-speech phải chờ cả utterance xong mới phát (**Reported**). Vì vậy model này không tự động là true-streaming.

### 3.4. Lightweight / ONNX / edge

- **Ví dụ:** Supertonic 3 (khoảng 99M), VieNeu v3 Nano (48M flow matching, 24 kHz), Kokoro Vietnamese (ONNX + `vig2p`), LGTM-TTS (duration predictor + iterative denoising + vocoder), sanoTTS (Piper/VITS-distilled, 1.46M cho voice vi).
- **Lưu ý (Synthesis):** ONNX là **định dạng runtime**, không phải một kiến trúc. Phần lớn các model nhóm này tổng hợp xong cả chunk rồi mới trả. Một short-clause chunker có thể giảm thời gian chờ câu đầu, nhưng đổi lại là prosody ở ranh giới chunk kém hơn và tốn thêm overhead mỗi lần gọi.

### 3.5. Chọn kiến trúc theo yêu cầu (Synthesis)

| Yêu cầu chính | Hướng kiến trúc ưu tiên |
|---|---|
| Streaming thấp trễ trên GPU, nhiều phiên | Codec-AR có frame-level streaming và server có giới hạn stream (VieNeu, MOSS Local, Higgs/Fish nếu có license) |
| Cloning/style chất lượng cao, chấp nhận tốn GPU | Continuous-latent diffusion-AR (VoxCPM2; dots là hướng nghiên cứu) |
| CPU/on-device | ONNX nhỏ (VieNeu ONNX int8/fp32, Supertonic 3, Kokoro vi, VieNeu Nano) |
| MCU / siêu nhỏ | sanoTTS (GPL-3.0) |
| Phủ ngôn ngữ cực rộng | OmniVoice, Higgs, Fish: đều non-commercial |

**Không nên bắt đầu production bằng việc tự huấn luyện một multilingual foundation model** khi đã có baseline tiếng Việt triển khai được. Chỉ nên fine-tune (LoRA) sau khi đã xác định được failure case cụ thể và đã có quyền dữ liệu (**Synthesis**).

---

## 4. Ứng viên tiếng Việt: bằng chứng và phân tầng

Khả năng và số liệu là **Reported**. Phân tầng là **Synthesis**.

### 4.1. Bảng tổng hợp

| Tầng | Model | Bằng chứng tiếng Việt | Realtime / triển khai | License | Vai trò |
|---|---|---|---|---|---|
| **Baseline** | [VieNeu v3 Turbo](../wiki/vieneu-tts-v3-turbo.md) | vi/en, khoảng 10k giờ bilingual, preset Bắc/Trung/Nam, code-switch, `sea-g2p` | Frame-level streaming, 48 kHz; CPU ONNX / GPU PyTorch + CUDA graph; `/v1/audio/speech`; TTFA khoảng 115 ms trên RTX 3060 | Apache-2.0 theo FAQ, **nhưng** roadmap ghi "on-device, personal use" | Pick số 1, có điều kiện rà license |
| **Challenger GPU** | [VoxCPM2](../wiki/voxcpm2.md) | `vi` trong 30 ngôn ngữ | 2B, 48 kHz, `generate_streaming`; RTF khoảng 0.3 (khoảng 0.13 với Nano-vLLM) trên 4090; khoảng 8 GB VRAM; chưa có TTFA | Apache-2.0 | A/B cho cloning/style |
| **Challenger CPU** | [Supertonic 3](../wiki/supertonic-3.md) | `vi` trong 31 ngôn ngữ | khoảng 99M ONNX, CPU-first; `synthesize` trả full waveform; số đo chỉ có dạng ảnh | OpenRAIL-M (weights) / MIT (code) | A/B cho on-device |
| **Challenger GPU streaming** | [MOSS-TTS Local v1.5](../wiki/moss-tts-local-transformer-v1-5.md) | `vi` trong 31; nên gắn language tag | HF + SGLang-Omni, PCM 48 kHz stream; codec native stereo nhưng ví dụ stream là mono | Apache-2.0 theo card | A/B; kiểm tra số kênh, framing, cancellation |
| **Expressive (NC)** | [Higgs TTS 3](../wiki/higgs-tts-3-4b.md) | vi nằm trong tier WER/CER < 5 của card | khoảng 4B, SSE streaming sub-second, SGLang/vLLM-Omni | Research/NC + Creator Use Grant | Chỉ khi có license thương mại |
| **Expressive (NC)** | [Fish S2 Pro](../wiki/fish-audio-s2-pro.md) | `vi` trong nhóm "Other" (không thuộc Tier 1/2) | 4B + 400M Dual-AR, SGLang, khoảng 100 ms TTFA trên H200 | Fish Research License (NC) | Chỉ khi có license; cần test thanh điệu |
| **Cần nghe thử** | [G-OmniVoice](../wiki/g-omnivoice.md) | Held-out vi: WER 0.0259 / SIM 0.890 / MOS 7.685, tốt nhất trong bảng 4 model của chính card | `generate` trả full waveform 24 kHz; không có TTFA/streaming | Card ghi Apache-2.0, nhưng base OmniVoice là CC-BY-NC và tokenizer theo Boson license | Challenger về độ chính xác, chưa phải pick triển khai |
| **Cần nghe thử** | [Gwen-TTS 0.6B](../wiki/gwen-tts-0.6b.md) | Finetune Qwen3-TTS-0.6B-Base trên khoảng 1.000 giờ audio vi crawl từ TikTok; 9 demo voice | `generate_voice_clone` trả full waveform; không có benchmark | MIT theo card; lineage và quyền dữ liệu TikTok chưa rõ | Ứng viên cloning |
| **CPU A/B** | [Kokoro Vietnamese](../wiki/kokoro-vietnamese.md) | Finetune vi, `vig2p`, voicepacks | PyTorch/ONNX CPU/CUDA CLI; không có số đo chất lượng/TTFA/streaming | Apache-2.0 theo capture | Đo và nghe A/B |
| **Edge** | VieNeu v3 Nano | vi/en (đọc tiếng Anh và code-switch yếu hơn Turbo) | 48M ONNX, 24 kHz; RTF 0.22/0.11 (16/8 steps) trên i5; chỉ trả chunk đã hoàn chỉnh | như VieNeu | Fallback cho CPU yếu |
| **MCU** | [sanoTTS](../wiki/sanotts.md) | Voice `vi-vais1000-1p46m`, chưa được chấm điểm | Piperlite 22.05 kHz; Python numpy / browser / C | GPL-3.0 | Thử nghiệm siêu nhỏ |
| **Nghiên cứu** | MOSS-TTS v1.5 (flagship 8B), dots.tts-mf, LGTM | Có vi (MOSS, LGTM); dots tự thừa nhận khoảng cách WER với vi | MOSS flagship chỉ có batch `generate`; LGTM thiếu license | — | Không đưa vào production |

**Không chọn out-of-box cho vi (theo catalog):** Qwen3-TTS chính thức, CosyVoice2/Fun-CosyVoice3, Audio8 Preview, Chatterbox V3/Turbo/Nano, Pocket, Sopro, Soprano, VibeVoice, Breeze, GLM-TTS, IndexTTS2/2.5, GPT-SoVITS, AuK-Flash, Supertonic v1/v2, Irodori và Indic Parler. Đây là **thiếu `vi` trong phạm vi hỗ trợ đã compile**, không phải bằng chứng rằng mọi community adaptation đều bất khả thi. Ví dụ: Gwen-TTS là một adaptation của Qwen3-TTS, nhưng là một checkpoint khác và cần bằng chứng riêng.

**Chỉ là pointer thứ cấp:** F5-TTS-Vietnamese, viXTTS, ShiniChien Qwen3-TTS-VN và KhanhTTS-OmniVoice chưa có nguồn primary trong wiki. VieNeu v4 là API proprietary, chưa có số liệu chất lượng, TTFA, SLA hay giá.

### 4.2. Vì sao VieNeu được chọn làm baseline?

Lý do là **bằng chứng phù hợp với triển khai**, không phải MOS vượt trội (**Synthesis**):

1. **Chuyên tiếng Việt từ frontend:** có `sea-g2p`, dữ liệu vi/en, preset giọng theo vùng miền và code-switching.
2. **Có số đo streaming kèm điều kiện cụ thể** trên phần cứng consumer: RTX 3060 12 GB, i5 thế hệ 12, Windows 11, torch 2.8 cu128 bf16, ORT 1.24 6 threads, SDK 3.8.x, tháng 9/2026.
3. **Đường vận hành đầy đủ:** SDK `infer_stream`, server `apps/openai_speech.py` (`POST /v1/audio/speech`, pcm/wav, chunked hoặc SSE), Docker Compose profile `api-gpu`/`api-cpu`, giới hạn `VIENEU_MAX_STREAMS` và trả HTTP 429 khi vượt.
4. **Chạy được cả CPU và GPU** với cùng một API.

Benchmark streaming do tác giả công bố (**Reported**, chưa reproduce):

| Chế độ | TTFA | RTF mỗi stream |
|---|---|---|
| GPU, 1 stream | khoảng 115 ms (106 ms qua HTTP) | 0.49 |
| GPU, 8 stream | 164 ms | 0.56 |
| GPU, 16 stream | 185 ms median; tối đa 339 ms khi tất cả bắt đầu cùng lúc | 0.59 |
| GPU, 32 stream | khoảng 450 ms | 0.93, gần hết biên an toàn |
| CPU fp32, 1 stream | 260–400 ms | 0.55–0.61; 2 stream đồng thời lên 1.19 (giật) |
| CPU int8, 1 stream | 140–195 ms | khoảng 0.35; 2 stream 0.58–0.67 |

Các lưu ý vận hành, tác giả công bố và bài này tổng hợp:

- CPU int8 cần **VNNI**. Trên CPU cũ có thể ra audio méo.
- Lần gọi đầu tiên cho mỗi batch size tốn khoảng 0.5 s để capture CUDA graph, nên gọi `warm_fused()` khi khởi động. GPU nghỉ vài giây sẽ hạ clock, request đầu tiên sau đó trả thêm 100–300 ms.
- 16 stream tương ứng khoảng 45–80 user voice-chat đang hoạt động, vì một stream chỉ tồn tại khi bot đang nói. Con số này **không** có nghĩa là 16 user đồng thời của toàn pipeline.
- Mỗi slot `max_streams` được dự trữ làm mỗi lần gọi codec chậm thêm khoảng 2.5 ms. Hãy đặt giá trị theo tải thật, đừng đặt dư.
- Tham số `style` đã deprecated và bị bỏ qua: giọng và cách đọc đi theo reference/preset. Emotion tag (`[cuoi]`, `[tho dai]`, `[hang giong]`) vẫn đang experimental. Temperature khoảng 0.8 cho kết quả ổn định nhất.

Điểm yếu và rủi ro của VieNeu:

- **License chưa nhất quán:** FAQ của card ghi Apache-2.0 cho mọi artifact và cho phép dùng preset voice thương mại, nhưng roadmap trong README ghi "on-device, personal use". Wiki không chọn bên nào; cần review pháp lý.
- **Corpus huấn luyện bị gated và không công bố.** Phần xác nhận consent chỉ áp dụng cho preset voice, không áp dụng cho reference do người dùng tự đưa vào để clone.
- **Lỗi G2P `chánh` → `tránh` (issue #207)** chỉ được một AI report nhắc lại, chưa có ai reproduce. Nên coi đây là một regression case cần test.
- Card SDK 3.7.1 có 23 voice (mặc định Minh Quân), README 3.8.x có 25 voice (mặc định Hải Đăng). Hãy pin phiên bản và dùng `list_preset_voices()` làm nguồn đúng.
- Card v3 không công bố số tham số. Không nên lấy con số 0.3B/0.5B của v1/v2 gán cho v3.

### 4.3. Khi nào chuyển sang challenger? (Synthesis)

| Tình huống | Hướng xử lý |
|---|---|
| VieNeu không đạt chất lượng nghe, hoặc cần clone giọng tốt hơn, và có GPU khoảng 8 GB trở lên | Chuyển sang **VoxCPM2** nếu vẫn đạt SLO TTFA/RTF. Phải tự viết API adapter. |
| Chỉ có CPU, hoặc chạy on-device | **VieNeu ONNX** trước (int8 nếu có VNNI), A/B với **Supertonic 3** / **Kokoro vi**. Dùng **Nano** cho CPU yếu. |
| Đã có SGLang-Omni trong hạ tầng | Thử **MOSS Local v1.5**: Apache-2.0, có streaming PCM. |
| Cần cảm xúc mạnh và inline tag, có ngân sách license | **Higgs TTS 3** hoặc **Fish S2 Pro**, nhưng chỉ sau khi qua test tiếng Việt. |
| License thương mại phải tuyệt đối sạch ngay | **VoxCPM2** (Apache-2.0) hoặc **MOSS Local** (Apache theo card) cho tới khi mâu thuẫn license của VieNeu được giải quyết. |
| MCU / microcontroller | **sanoTTS**, nếu chấp nhận GPL-3.0 và chất lượng vi chưa được chấm. |

---

## 5. Thiết kế hệ thống TTS realtime

Phần này là **Synthesis**: bài viết ghép kiến trúc từ các trang pipeline. Kiến trúc này chưa được triển khai và chưa được test.

### 5.1. Vị trí của TTS trong vòng hội thoại

```text
LLM token stream (generation_id)
  → [1] Clause chunker
  → [2] Vietnamese spoken-text normalizer + lexicon
  → [3] TTS router / backend adapter  ──→  TTS service (VieNeu | VoxCPM2 | ONNX ...)
  → [4] Audio stream (metadata + chunks, sequence)
  → [5] Bounded client playback queue (AudioWorklet)  → loa
         ↑ audio.played(offset)                       ↓
  ← barge-in: generation_id++ → cancel LLM + TTS → flush queues → lưu phần đã phát
```

Nguyên tắc:

- Tách **model**, **runtime**, **API server**, **streaming policy** và **orchestration** thành các tầng riêng.
- Mỗi backend phải khai báo rõ sample rate, dtype, số kênh, kiểu framing và khả năng cancellation.
- Đổi backend chỉ nên là thay URL và adapter, không phải sửa logic hội thoại.

### 5.2. Clause chunker

Không gửi từng token, cũng không chờ LLM trả lời xong. Quy tắc khởi điểm được AI report đề xuất (**Reported**, cần tune):

- Flush khi gặp `. ? ! … ; :` hoặc xuống dòng.
- **Chunk đầu tiên** được cắt ở dấu phẩy khi đã có từ khoảng 25 ký tự trở lên, để giảm TTFA.
- Mảnh ngắn hơn 8 ký tự thì gộp vào câu sau.
- Không cắt giữa một số, ngày, viết tắt hay tên riêng đang viết dở (ví dụ `1.250.` khi LLM chưa sinh `000đ`).

Pseudocode minh hoạ (Synthesis):

```python
TERMINATORS = set(".?!…;:\n")
FIRST_CHUNK_MIN = 25   # ký tự, chỉ áp dụng cho chunk đầu
MIN_FRAGMENT = 8

def chunk_stream(tokens):
    buf, first = "", True
    for tok in tokens:
        buf += tok
        if ends_inside_entity(buf):          # số/ngày/tiền/viết tắt chưa xong
            continue
        cut = find_cut(buf, first)           # vị trí terminator, hoặc dấu phẩy nếu first và len>=25
        if cut is not None and len(buf[:cut].strip()) >= MIN_FRAGMENT:
            yield buf[:cut].strip()
            buf, first = buf[cut:], False
    if buf.strip():
        yield buf.strip()
```

Chunk đầu ngắn giúp có tiếng sớm, nhưng prosody ở ranh giới có thể gãy. Cần A/B riêng điểm này.

### 5.3. Vietnamese normalizer và lexicon

Tách **display text** (hiện cho người dùng) khỏi **spoken text** (gửi cho TTS). Các lớp cần có (**Reported** từ report; danh sách cụ thể là **Synthesis**):

| Loại | Ví dụ | Spoken form |
|---|---|---|
| Tiền | `1.250.000đ` | "một triệu hai trăm năm mươi nghìn đồng" |
| Số điện thoại | `0912 345 678` | đọc từng chữ số |
| Số đếm / thập phân | `3,5` | "ba phẩy năm" |
| Ngày / giờ | `07/10`, `14h30` | cần quy tắc theo domain (ngày/tháng hay tháng/ngày) |
| % / đơn vị | `60 km/h`, `15%` | "sáu mươi ki-lô-mét trên giờ", "mười lăm phần trăm" |
| Viết tắt | `TP.HCM`, `UBND` | "thành phố Hồ Chí Minh", "ủy ban nhân dân" |
| Tên riêng / domain term | `chánh văn phòng` | substitution dictionary nếu G2P đọc sai |
| Code-switch | `meeting`, `email` | giữ tiếng Anh nếu backend đọc được (VieNeu có); nếu không thì phiên âm |

Các yêu cầu khác:

- Chuẩn hóa Unicode NFC và kiểm tra vị trí dấu.
- Loại bỏ markdown, emoji, bảng, URL theo một spoken policy.
- **Giữ dấu câu** vì TTS dùng dấu câu để quyết định prosody.
- Ràng buộc từ phía LLM: system prompt yêu cầu câu ngắn, không markdown/emoji/bảng/URL, và hỏi lại khi không chắc đã nghe đúng (**Reported**).
- Wiki **chưa chọn** thư viện normalizer tiếng Việt nào đã được kiểm chứng. Cần một bộ regression riêng.

### 5.4. Hợp đồng backend adapter

Mỗi TTS backend được bọc bởi một adapter có cùng interface:

```text
synthesize_stream(spoken_text, voice_id, generation_id, deadline) -> AsyncIterator[AudioChunk]
cancel(generation_id)
describe() -> { sample_rate, dtype, channels, framing, supports_cancel, max_streams }
```

Những khác biệt đã biết giữa các backend (**Reported**), adapter phải xử lý tường minh:

| Backend | Định dạng ra |
|---|---|
| VieNeu SDK | `np.float32`, 48 kHz, theo chunk |
| VieNeu HTTP | PCM `s16le` 48 kHz, chunked hoặc SSE |
| VieNeu Nano | 24 kHz, từng chunk đã hoàn chỉnh |
| Higgs | SSE chứa WAV base64, không phải raw PCM |
| MOSS Local | 48 kHz; codec native stereo nhưng ví dụ stream dùng `ffmpeg -ac 1`, phải xác nhận số kênh thực tế |
| Qwen3-TTS (tham chiếu) | 24 kHz |

Một route "OpenAI-compatible" **không** đảm bảo schema hay cách chia chunk giống nhau giữa các server.

**Client phải biết sample rate của từng backend.** Chỉ resample ở playback adapter khi transport yêu cầu. Không đổi giọng giữa chừng một utterance: nếu backend lỗi giữa câu, ưu tiên retry ở mệnh đề mới và báo trạng thái, thay vì ghép hai giọng khác nhau.

### 5.5. Concurrency, backpressure và warmup

- **Một process sở hữu model.** Không để mỗi gateway worker tự load weights riêng.
- **Admission cap:** đặt `max_streams` (VieNeu: `VIENEU_MAX_STREAMS`, mặc định 16 trên GPU và 1 trên CPU) theo tải đo được. Hàng đợi nhỏ có giới hạn, quá tải thì trả 429 và gateway có chiến lược xử lý (retry, câu đệm, hoặc thông báo).
- **Ưu tiên nhịp audio (cadence) hơn throughput batch.** Theo dõi chunk stall và underrun phía client.
- **Warmup:** gọi `warm_fused()` hoặc một câu mẫu cho mỗi batch size dự kiến. Readiness probe chỉ báo "ready" sau khi warmup xong. Cân nhắc khóa clock GPU để tránh 100–300 ms phạt khi GPU vừa nghỉ.
- **Chung GPU với ASR và LLM:** đo TTS **dưới tải chung**, không chỉ đo riêng. Report ước tính VieNeu GPU dùng khoảng 2–3 GB VRAM; README ghi đỉnh 1.1 GB ở 16 stream. Đây là hai claim khác nhau và đều chưa được đo lại.
- **Pin phiên bản và checksum** của SDK, weights, G2P, voicepack và normalizer. Pre-stage offline.

### 5.6. Cancellation và barge-in

Trình tự đề xuất (**Reported** từ trang barge-in):

1. Gắn `generation_id` vào mọi chunk text và audio.
2. Khi người dùng ngắt lời: tăng `generation_id`, cancel stream LLM, cancel request TTS (HTTP/WS), xóa các câu đang chờ trong hàng đợi.
3. Gửi `{"type":"clear"}` (hoặc `audio_cancel`) để client flush buffer AudioWorklet.
4. Chỉ lưu vào history **phần đã thực sự phát**, kèm tag `[bị ngắt]`. Client báo lại `played_sample_offset`.
5. Bỏ mọi chunk đến muộn mang `generation_id` cũ.

Các điểm cần kiểm chứng (**Synthesis**):

- Server có **thực sự ngừng tính toán** sau khi client disconnect không? Đo cả *user nói → hết tiếng bot* và *user nói → giải phóng compute*.
- Nếu SDK không hỗ trợ cancel giữa chừng, đó là một **deployment gate**.
- Không có alignment giữa token và audio thì chỉ biết được offset theo sample, không biết chính xác những từ nào đã được nghe.

### 5.7. Lựa chọn runtime / đường phục vụ

| Lựa chọn | Phù hợp | Ranh giới bằng chứng |
|---|---|---|
| VieNeu SDK / `apps/openai_speech.py` / Docker `api-gpu`, `api-cpu` | Baseline, MVP đến production nhỏ | Có số đo của tác giả; chưa inspect `docs/streaming.md` |
| VoxCPM2 Python + service tự viết | Challenger GPU | Chưa inspect tài liệu Nano-vLLM accelerator |
| SGLang-Omni | MOSS Local, Higgs, Fish | Chưa có recipe cho VieNeu/VoxCPM2 |
| vLLM-Omni | Higgs, Qwen3-TTS (không có vi) | Không có tài liệu phục vụ VieNeu/VoxCPM2 trực tiếp |
| ONNX Runtime service | Supertonic 3, Kokoro vi, VieNeu Nano | ONNX không tự chứng minh realtime |
| [audio.cpp](../wiki/audio-cpp-framework.md) GGUF | Triển khai native C++ | Có community port `vieneu_v3_turbo` (vi/en, 48 kHz) nhưng chưa inspect parity/streaming; chỉ chuyển sang sau khi A/B với SDK tham chiếu |
| Pipecat custom `TTSService` | Orchestration | Chỉ cần viết `run_tts()` gọi `/v1/audio/speech` của VieNeu (**Reported**) |
| HF speech-to-speech | MVP nhanh | Đổi TTS mặc định (Qwen3-TTS, không có vi) sang OpenAI-compatible trỏ tới VieNeu |

Port C++/GGUF **không thay đổi license** của weights, và việc có port không chứng minh chất lượng hay latency trên máy đích.

---

## 6. Ngân sách độ trễ

TTFA 115 ms của TTS **không** phải voice-to-voice 115 ms. Critical path thực tế:

```text
user ngừng nói → endpoint commit → ASR final → LLM chunk đầu có nghĩa
              → chunker + normalizer → TTS first playable sample → network/jitter → loa phát
```

Ngân sách tham khảo từ report (**Reported**, chưa đo; không phải target):

| Stage | Ước lượng |
|---|---|
| Network + jitter buffer (WebRTC) | 30–80 ms |
| VAD silence | 200–300 ms |
| Smart Turn | 10–65 ms |
| ASR turn-final | 100–300 ms |
| LLM TTFT + chunk đầu | 150–350 ms |
| **TTS TTFA** | **64–300 ms** (VieNeu khoảng 115 ms theo tác giả) |
| Voice-to-voice | khoảng 0.7–1.2 s |

**Synthesis:**

- Không cộng các phép đo chồng lấp như thể chúng chạy tuần tự. Hãy đo critical path thực.
- Phần TTS kiểm soát được gồm: độ dài chunk đầu, warmup, admission cap và playback buffer phía client.
- SLO khởi điểm có thể là **TTS TTFA P95 ≤ 250–400 ms** và **RTF P95 ≤ 0.7** dưới tải thực. Đây là SLO đề xuất, chưa phải khả năng đã được chứng minh.

---

## 7. Protocol đánh giá và gate chọn model

Đây là protocol đề xuất (**Synthesis**), chưa phải benchmark đã chạy.

### 7.1. Bộ prompt (150–300 câu tiếng Việt)

- Đủ sáu thanh, có cặp tối thiểu (minimal pair) về thanh điệu.
- Câu hỏi, câu cảm thán, hội thoại ngắn và dài.
- Tiền, ngày, số điện thoại, đơn vị, viết tắt, địa danh, tên riêng.
- Code-switch Anh–Việt.
- Giọng ba miền (preset) và cùng một reference đã được phép clone (test riêng).
- Các chunk boundary nhân tạo để test prosody ở ranh giới.
- Regression case đã biết: `chánh`/`tránh`, các lỗi ngắt nghỉ.
- Lưu cả raw text và normalized spoken text.

### 7.2. Chất lượng

- Blind pairwise preference và MOS/CMOS với 10–20 người nghe Việt. Chấm: độ tự nhiên, thanh điệu/phát âm, prosody hội thoại, độ nhất quán giọng.
- ASR round-trip WER/CER **chỉ là proxy**, phải audit thủ công các lỗi.
- **Không** chọn model theo Seed-TTS tiếng Anh, theo SIM đơn lẻ, hay theo MOS của vendor (MOS 7.685 của G-OmniVoice không rõ thang đo và protocol).

### 7.3. Hiệu năng

- Đo cả normalization → first byte **và** normalization → first audible sample.
- Đo thêm: queue delay, TTFA P50/P95, cadence giữa các chunk, số lần stall, RTF P95 mỗi request, RAM/VRAM.
- Đo ở cả trạng thái warm và cold, với concurrency 1/4/8/16, **khi toàn bộ stack (ASR + LLM + TTS) chạy đồng thời**.
- Test cancellation giữa chunk, disconnect/reconnect, timeout, OOM và 429.

### 7.4. Hợp đồng và quyền

- Contract test: 48k/24k/sample rate không xác định, mono/stereo, dtype, PCM vs WAV/SSE, sequence tăng đơn điệu. Không được phát audio cũ (stale audio) sau cancel.
- Rights: license runtime, weights, voicepack, tokenizer và lineage dữ liệu xét riêng từng thứ; consent cho reference clone; log không chứa nội dung (content-free).

### 7.5. Luật quyết định

License và các lỗi nghiêm trọng là **hard gate**. Điểm preference chỉ xét sau khi đã qua các gate này.

1. **VieNeu** nếu thắng về khả năng triển khai và đạt ngưỡng chất lượng.
2. **VoxCPM2** nếu cải thiện có ý nghĩa về nghe/cloning mà vẫn đạt SLO.
3. **Supertonic 3** (hoặc Kokoro vi) nếu footprint CPU và chất lượng đạt yêu cầu.
4. **Higgs/Fish** chỉ sau khi qua test chất lượng tiếng Việt **và** đã có thỏa thuận thương mại.
5. **G-OmniVoice/Gwen** chỉ khi thắng rõ ràng trong blind test **và** giải quyết được streaming (chunk theo mệnh đề, đo TTFA) cùng lineage/quyền dữ liệu.

---

## 8. Lộ trình triển khai đề xuất

| Giai đoạn | Việc chính |
|---|---|
| **1 — MVP** | VieNeu v3 Turbo qua `/v1/audio/speech` (Docker `api-gpu` hoặc `api-cpu`), chạy sau Pipecat hoặc HF speech-to-speech. Làm ngay từ đầu: clause chunker, normalizer + lexicon, adapter khai báo audio format, warmup, `max_streams` theo tải, `generation_id` + cancel, log latency theo từng turn. |
| **2 — Beta** | A/B VieNeu với VoxCPM2 (GPU), và VieNeu ONNX với Supertonic 3 / Kokoro vi (CPU). Chạy protocol mục 7. Mỗi lần chỉ đổi một thành phần. Tune chunk đầu (độ dài, cắt ở dấu phẩy). Có thể thêm MOSS Local nếu đã dùng SGLang-Omni. |
| **3 — Production** | Tách TTS thành service/GPU pool riêng, có quan sát P95, admission control và circuit breaker. LoRA cho brand voice (10–30 phút audio sạch của một speaker, khoảng 6 GB GPU theo tác giả) sau khi đã có consent. Chỉ chuyển sang audio.cpp/native sau khi qua gate về parity output và latency. |

---

## 9. Mâu thuẫn và giới hạn còn mở

- **License VieNeu:** FAQ ghi Apache-2.0 thương mại; roadmap ghi "on-device, personal use". Chưa giải quyết.
- **Higgs:** card xếp vi vào tier < 5 nhưng không có điểm số, dataset hay normalizer riêng cho vi. Con số 617 ms trên H100 là thời gian **gửi request → nhận đủ response**, không phải TTFA.
- **Fish:** con số khoảng 100 ms TTFA đo trên H200 và không có protocol đo.
- **Supertonic 3:** các biểu đồ hiệu năng chỉ có dạng ảnh và ảnh không có trong raw. Không lấy RTF của v2 để suy cho v3.
- **G-OmniVoice:** không có protocol, judge hay uncertainty. Nhãn "VietNeu/v3turbo" trong bảng của card không khớp với tên VieNeu đã compile.
- **Gwen-TTS:** chưa rõ phương pháp crawl, lọc và consent dữ liệu TikTok. Frontmatter ghi `library_name: transformers` nhưng phần usage lại import `qwen_tts`.
- **MOSS Local:** chưa inspect cookbook/config; số kênh thực tế của stream chưa xác nhận. Không gán đường streaming của bản Local cho flagship 8B.
- **Không có so sánh khớp điều kiện** (matched comparison) về MOS, TTFA hay lỗi phát âm tiếng Việt giữa bất kỳ cặp ứng viên nào. Wiki ở trạng thái `draft` cho trang selection, và giữ nguyên trạng thái đó tới khi có listening test và đo trên phần cứng đích.
- Toàn bộ là snapshot tài liệu trong repo (phần lớn compile ngày 2026-10-06/07), không phải khảo sát toàn thị trường. Các cloud TTS ngoài catalog chưa được khảo sát.

---

## 10. Tài liệu tham chiếu trong wiki

- [Vietnamese Realtime TTS Selection](../wiki/vietnamese-realtime-tts-selection.md): shortlist, bảng bằng chứng, gate A/B.
- [TTS Model Survey](../wiki/tts-model-survey.md): catalog 40 dòng, kiến trúc, streaming, license, runtime.
- [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md): chunker, normalizer, profile triển khai, latency, release gates.
- [VieNeu-TTS v3 Turbo](../wiki/vieneu-tts-v3-turbo.md): SDK, server, Docker, benchmark, license.
- [VoxCPM2](../wiki/voxcpm2.md), [Supertonic 3](../wiki/supertonic-3.md), [MOSS-TTS Local v1.5](../wiki/moss-tts-local-transformer-v1-5.md), [Higgs TTS 3](../wiki/higgs-tts-3-4b.md), [Fish Audio S2 Pro](../wiki/fish-audio-s2-pro.md), [G-OmniVoice](../wiki/g-omnivoice.md), [Gwen-TTS 0.6B](../wiki/gwen-tts-0.6b.md), [Kokoro Vietnamese](../wiki/kokoro-vietnamese.md), [sanoTTS](../wiki/sanotts.md).
- [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md): report thứ cấp về chunker, normalizer và latency budget.
- [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md): `generation_id`, clear/flush, gating.
- [So sánh công cụ triển khai speech](../wiki/speech-deployment-tools-comparison.md) và [audio.cpp Framework](../wiki/audio-cpp-framework.md): các tầng runtime.
