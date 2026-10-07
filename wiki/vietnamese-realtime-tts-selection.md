---
type: Synthesis
title: Vietnamese Realtime TTS Selection
description: Shortlist TTS realtime tiếng Việt theo chất lượng bằng chứng, streaming, CPU/GPU và license, so sánh VieNeu v3 Turbo, VoxCPM2, Supertonic 3 cùng các hướng multilingual và fine-tuning.
tags: [tts, vietnamese, streaming, comparison, deployment]
status: draft
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T15:50:00Z }
stale_after: 2027-10-07
sources:
  - id: vieneu-tts-repo
    resource: ../raw/VieNeu-TTS-repo.md
    kind: documentation
    title: VieNeu-TTS repository README snapshot
  - id: vieneu-v3-card
    resource: ../raw/VieNeu-TTS-v3-Turbo.md
    kind: documentation
    title: VieNeu-TTS v3 Turbo model card (SDK 3.7.1)
  - id: vieneu-tts-docs
    resource: ../raw/vieneu-tts-docs/README.md
    scope: ../raw/vieneu-tts-docs/
    kind: documentation
    revision: 85344322b7258b4e25479b692e8e3396baf9db34
    title: VieNeu-TTS supporting docs (streaming guide and Docker Compose)
  - id: voxcpm2-card
    resource: ../raw/VoxCPM2.md
    kind: documentation
    title: VoxCPM2 model card
  - id: supertonic3-card
    resource: ../raw/supertonic-3.md
    kind: documentation
    title: Supertonic 3 model card
  - id: higgs3-card
    resource: ../raw/higgs-audio-v3-tts-4b.md
    kind: documentation
    title: Higgs TTS 3 model card
  - id: fish2-card
    resource: ../raw/s2-pro.md
    kind: documentation
    title: Fish Audio S2 Pro model card
  - id: dots-mf-card
    resource: ../raw/dots.tts-mf.md
    kind: documentation
    title: dots.tts-mf model card
  - id: lgtm-card
    resource: ../raw/LGTM.md
    kind: documentation
    title: LGTM-TTS model card
  - id: omnivoice-card
    resource: ../raw/OmniVoice.md
    kind: documentation
    title: OmniVoice model card
  - id: g-omnivoice-card
    resource: ../raw/g-omnivoice.md
    kind: documentation
    title: G-OmniVoice model card
  - id: gwen-tts-card
    resource: ../raw/gwen-tts-0.6B.md
    kind: documentation
    title: Gwen-TTS 0.6B model card
  - id: qwen3-card
    resource: ../raw/Qwen3-TTS-12Hz-1.7B-CustomVoice.md
    kind: documentation
    title: Official Qwen3-TTS family card
  - id: kokoro-vi-concept
    resource: kokoro-vietnamese.md
    kind: synthesis
    title: Compiled Kokoro Vietnamese
  - id: moss-local-v15-concept
    resource: moss-tts-local-transformer-v1-5.md
    kind: synthesis
    title: Compiled MOSS-TTS-Local-Transformer-v1.5
  - id: moss-v15-concept
    resource: moss-tts-v1-5.md
    kind: synthesis
    title: Compiled MOSS-TTS-v1.5
  - id: sanotts-concept
    resource: sanotts.md
    kind: synthesis
    title: Compiled sanoTTS
  - id: tts-survey
    resource: tts-model-survey.md
    kind: synthesis
    title: Compiled TTS Model Survey
  - id: hf-pipeline
    resource: speech-to-speech-pipeline.md
    kind: synthesis
    title: Compiled HF Speech-to-Speech Pipeline
  - id: vi-stack
    resource: vietnamese-realtime-voice-agent-stack.md
    kind: synthesis
    title: Compiled Vietnamese Realtime Voice Agent Stack (secondary AI report)
  - id: audio-cpp-repo
    resource: ../raw/audio.cpp-repo.md
    kind: documentation
    title: audio.cpp repository README
---

**Khuyến nghị có điều kiện (Synthesis):** dùng [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md) làm baseline triển khai realtime tiếng Việt; A/B với [VoxCPM2](voxcpm2.md) khi ưu tiên cloning/style và có GPU, với [Supertonic 3](supertonic-3.md) khi ưu tiên on-device/CPU. Nếu chấp nhận commercial license riêng và chi phí serving lớn hơn, thử [Higgs TTS 3](higgs-tts-3-4b.md) cùng [Fish S2 Pro](fish-audio-s2-pro.md) cho expressive voice. Đây là thứ tự thử nghiệm theo độ phù hợp triển khai, **không phải bảng xếp hạng chất lượng nghe tiếng Việt**: chưa có matched Vietnamese MOS/CMOS, TTFA và lỗi phát âm giữa các ứng viên trong bằng chứng đã đọc.[^vieneu-tts-repo][^voxcpm2-card][^supertonic3-card][^higgs3-card][^fish2-card][^tts-survey]

## Phạm vi và độ tin cậy

- Retrieval ban đầu dùng catalog TTS, exact search tiếng Việt và các concept/quan hệ runtime/pipeline; lần cập nhật này đối chiếu thêm các concept mới hoặc đổi trong Git với catalog hiện có 40 dòng model/family TTS (**Observed**). Số dòng là phạm vi catalog, không phải số checkpoint hay xác nhận coverage toàn thị trường; không cần QMD cho lần đối chiếu này.[^tts-survey]
- Đã nghiên cứu nguồn local trong `raw/`: README/card của VieNeu, VoxCPM2, Supertonic 3, Higgs, Fish, dots-mf, LGTM, OmniVoice và phần language/model-family của Qwen3-TTS. Không fetch web/live releases; “hiện tại” là phạm vi snapshot trong repo, phần lớn được compile 2026-10-06, chứ không phải bảo đảm catalog toàn thị trường (**Observed**).
- **Reported** là tuyên bố của tác giả/vendor, kể cả số liệu họ đo. **Observed** là thấy field/API/table trong tài liệu; không chứng minh model thực sự nói tốt. Không tải weights, chạy inference, nghe audio hay reproduce benchmark; không có verification event về chất lượng/latency (**Observed**).
- Giữ `draft`: còn pending matched Vietnamese listening test, target-hardware TTFA/concurrency và rà license deployment. `stale_after` không phải sự xác nhận thông tin vẫn mới (**Synthesis**).

## Model nào có bằng chứng tiếng Việt?

Các khả năng và số liệu trong bảng là **Reported**; phân hạng ưu tiên là **Synthesis**.

| Model | Bằng chứng tiếng Việt | Realtime / triển khai | License và quyết định |
| --- | --- | --- | --- |
| **VieNeu v3 Turbo** | vi/en, ~10k h bilingual, preset Bắc/Trung/Nam, code-switching | frame-level audio streaming, CPU ONNX / GPU PyTorch, API; ~115 ms TTFA RTX 3060 | Apache-2.0 theo FAQ; roadmap còn ghi personal use. Baseline số 1 có điều kiện rà scope.[^vieneu-tts-repo][^vieneu-v3-card] |
| **VoxCPM2** | `vi` nằm trong 30 ngôn ngữ | 2B, 48 kHz, `generate_streaming`; RTF ~0.3 hoặc ~0.13 Nano-vLLM trên 4090; ~8 GB VRAM theo card | Apache-2.0. A/B số 1 cho cloning/style; chưa có TTFA và Vietnamese quality riêng.[^voxcpm2-card] |
| **Supertonic 3** | `vi` trong 31 ngôn ngữ | ~99M ONNX, CPU-first; mẫu `synthesize` trả waveform hoàn chỉnh, không chứng minh frame-level streaming | OpenRAIL-M weights / MIT code. A/B CPU; không lấy RTF v2 làm benchmark v3.[^supertonic3-card] |
| **Higgs TTS 3** | Vietnamese trong tier WER/CER <5 của card | ~4B codec AR, SSE streaming sub-second, SGLang/vLLM-Omni | Research/non-commercial; API hosting/product cần commercial license riêng. Ứng viên expressive mạnh, chưa được chứng minh thắng VieNeu/VoxCPM2 trên tiếng Việt.[^higgs3-card] |
| **Fish S2 Pro** | `vi` trong danh sách Other, không thuộc Tier 1/2 | 4B Slow AR +400M Fast AR, SGLang, ~100 ms TTFA H200 | Research/non-commercial; commercial license riêng. Cần test thanh điệu và prosody tiếng Việt.[^fish2-card] |
| **OmniVoice** | `vi` trong frontmatter (dòng 601) | diffusion LM, RTF thấp nhất công bố 0.025; card dùng `generate` trả full audio | CC-BY-NC weights. Không mặc định true-streaming; handler HF chờ full utterance.[^omnivoice-card][^hf-pipeline] |
| **G-OmniVoice** | held-out vi WER 0.0259 / SIM 0.890 / MOS 7.685, WER thấp nhất trong bảng 4 models của card (base, KhanhTTS, VietNeu) | `omnivoice` runtime, `generate` trả full waveform 24 kHz; chưa có TTFA/streaming/concurrency/VRAM | Card ghi Apache-2.0 + tokenizer Boson Community License; base OmniVoice weights CC-BY-NC nên cần rà lineage trước commercial. Challenger accuracy, chưa phải pick triển khai.[^g-omnivoice-card] |
| **Gwen-TTS 0.6B** | Qwen3-TTS-0.6B-Base finetune, ~1.000 h audio vi crawl TikTok; 9 demo voices kèm ref/infer clips; chưa có benchmark, TTFA/streaming hay review data-rights | `qwen-tts` runtime, `generate_voice_clone` trả full waveform; chưa có TTFA/streaming/concurrency/VRAM | Card ghi MIT; cần rà lineage base Qwen3-TTS và quyền dữ liệu TikTok-crawl trước commercial. Candidate cloning để A/B listening, chưa phải pick triển khai.[^gwen-tts-card] |
| **[Kokoro Vietnamese](kokoro-vietnamese.md)** | Vietnamese finetune, `vig2p` G2P, default và additional voicepacks | PyTorch / ONNX CPU hoặc CUDA CLI; chưa có quality, TTFA, RTF, streaming hay concurrency figures | Apache-2.0 theo capture. Candidate CPU/ONNX để đo và nghe A/B; không suy support của checkpoint này từ upstream Kokoro hay server Kokoro khác.[^kokoro-vi-concept] |
| **[MOSS-TTS Local v1.5](moss-tts-local-transformer-v1-5.md)** | `vi` trong 31 ngôn ngữ; card khuyến nghị explicit language tag, có cloning/pause/duration control | HF và SGLang-Omni; card mô tả audio-output streaming PCM 48 kHz, native codec stereo; chưa có numeric quality/TTFA/RTF/VRAM | Apache-2.0 theo card. Candidate GPU streaming đáng A/B; cookbook/config chưa inspect, phải kiểm tra channel framing và cancellation.[^moss-local-v15-concept] |
| **[MOSS-TTS v1.5](moss-tts-v1-5.md)** | `vi` trong 31 ngôn ngữ; language-tagged cloning, pause/duration control | Flagship MossTTSDelay-8B API, HF `generate` rồi decode; chưa có numeric quality/latency hay streaming path tương ứng trong capture | Apache-2.0 theo card. Research/cloning candidate; không gán streaming hoặc stereo handling của Local cho flagship.[^moss-v15-concept] |
| **[sanoTTS](sanotts.md)** | Voice `vi-vais1000-1p46m/`, 1.46M; Vietnamese quality chưa được chấm | Piper/VITS-distilled piperlite, 22.05 kHz, numpy Python / browser / C paths; chưa có vi TTFA hoặc confirmed chunk-streaming API | GPL-3.0. Ultra-small edge candidate, không zero-shot cloning; không chuyển English nano/ESP32 figures sang voice vi.[^sanotts-concept] |
| **dots.tts-mf / soar** | card đề cập Vietnamese trong nhóm low-resource WER gap, không có danh sách support/điểm vi riêng ở đây | continuous AR + flow head; mf NFE=4; chưa có TTFA/RTF tiếng Việt | Apache-2.0. Research/fine-tune candidate; giữ similarity không đồng nghĩa đọc tiếng Việt đúng.[^dots-mf-card] |
| **LGTM-TTS** | `vi`, Python usage và links hai sample vi | ONNX/PyTorch 44.1 kHz, duration + iterative denoising + vocoder | Thiếu license, size, quality/latency; chưa chọn production.[^lgtm-card] |
| **VieNeu v3 Nano** | vi/en nhưng English/code-switch yếu hơn Turbo | 48M flow matching ONNX, 24 kHz; RTF0.22/0.11 trên desktop i5 ở16/8 steps; chỉ finished-text chunks | Chỉ fallback yếu CPU sau kiểm tra artifacts/license; không thay Turbo khi cần frame-level streaming.[^vieneu-tts-repo] |

**Adjacent:** [SeamlessM4T v2 Large](seamless-m4t-v2-large.md) có Vietnamese speech output (`vie`) nhưng là hướng translation/UnitY2, non-commercial, chưa có cloning/TTFA evidence tương ứng; không đưa vào shortlist dedicated voice-agent TTS.[^tts-survey]

**Không chọn out-of-box cho vi theo catalog đã đọc:** Qwen3-TTS chính thức (10 languages không vi; finetune [Gwen-TTS 0.6B](gwen-tts-0.6b.md) đã có concept riêng với evidence card nhưng chưa benchmark/streaming nên chỉ là candidate A/B); CosyVoice2/Fun-CosyVoice3, Audio8 Preview, Chatterbox V3/Turbo/Nano, Pocket, Sopro, Soprano, VibeVoice/realtime, Breeze, GLM-TTS, IndexTTS2/2.5, GPT-SoVITS, AuK-Flash, Supertonic v1/v2, Irodori và Indic Parler. Đây là thiếu vi trong support scope đã compile, **không phải chứng minh mọi community adaptation đều bất khả thi**.[^qwen3-card][^tts-survey]

**Chỉ secondary pointers:** ShiniChien Qwen3-TTS Vietnamese/VN-Style, F5-TTS-Vietnamese và viXTTS chưa có primary source và benchmark thích hợp trong evidence đã truy hồi. [G-OmniVoice](g-omnivoice.md) và [Gwen-TTS 0.6B](gwen-tts-0.6b.md) đã có primary card nên ra khỏi nhóm này; KhanhTTS-OmniVoice và VietNeu/v3turbo mới chỉ xuất hiện qua bảng số của card G-OmniVoice, chưa đối chiếu nguồn gốc.[^g-omnivoice-card][^gwen-tts-card] Đặc biệt không suy commercial permission của derivative OmniVoice từ một AI report trong khi upstream weights là NC; phải kiểm tra lineage/license riêng. VieNeu v4 là proprietary API theo README nhưng chưa có quality/TTFA/SLA/giá để xếp hạng. Các cloud TTS ngoài catalog chưa được khảo sát trong phiên này.[^vi-stack][^omnivoice-card][^vieneu-tts-repo]

## Vì sao VieNeu là lựa chọn triển khai đầu tiên?

- Có Vietnamese-specific frontend `sea-g2p`, codec `MOSS-Audio-Tokenizer-Nano`, dữ liệu vi/en và voice assets theo vùng; API frame-level streaming cùng benchmark consumer GPU/CPU có điều kiện khá cụ thể. Đây là lợi thế **bằng chứng phù hợp triển khai**, không phải MOS vượt trội (**Reported/Synthesis**).[^vieneu-tts-repo][^vieneu-v3-card]
- Không gán kích thước0.3B/0.5B của v1/v2 cho v3 Turbo: card v3 không công bố parameter count đầy đủ. Tuyên bố original/from-scratch là của tác giả; tài liệu đã đọc chưa đủ xác nhận toàn bộ topology/backbone (**Reported/Unverified**).[^vieneu-v3-card][^tts-survey]
- `style` đã deprecated/ignored; chọn character qua reference/preset. Emotion cues còn experimental. Khi cần một brand voice, thử preset hoặc enroll reference một lần trước; LoRA10–30min audio một speaker là bước kế tiếp do tác giả hướng dẫn, không phải bảo đảm MOS/domain pronunciation (**Reported/Synthesis**).[^vieneu-tts-repo]
- G2P bug `chánh`→`tránh`/issue207 chỉ được relayed bởi AI report, chưa mở issue hay reproduce; dùng nó như regression case cần kiểm tra, không gọi là lỗi đã xác minh (**Reported/Unverified**).[^vi-stack]

### Không trộn throughput với streaming

Số liệu sau từ **§4 Benchmarks** của VieNeu README: RTX3060 12GB/i5 12th gen, Windows11, torch2.8 cu128 bf16, ORT1.24 6threads, SDK3.8.x, September2026 (**Reported**, chưa reproduce).[^vieneu-tts-repo]

| Chế độ | TTFA | RTF |
| --- | --- | --- |
| GPU streaming1 | ~115ms |0.49 |
| GPU streaming8 |164ms |0.56 |
| GPU streaming16 |185ms median; max339ms nếu tất cả bắt đầu đồng thời |0.59 |
| GPU streaming32 |~450ms |0.93, gần hết margin |
| CPU fp32,1 |260–400ms |0.55–0.61;2 cùng lúc lên1.19 |
| CPU int8 |140–195ms |~0.35;2 streams0.58–0.67 |

GPU batched RTF0.011–0.02 là tổng audio nhiều texts/batch, **không phải RTF một stream**. VRAM1.1GB peak/16streams cũng chỉ là claim trong harness này; không suy16 users hoặc capacity toàn voice stack. CPU int8 cần VNNI, có thể garbled trên CPU cũ; GPU cold/idle và CUDA-graph capture có extra latency, cần warmup (**Reported/Synthesis**).[^vieneu-tts-repo]

## So sánh hướng kiến trúc

### 1. Codec-token autoregressive

Fish: Slow AR theo thời gian dự đoán semantic codebook, Fast AR dự đoán residual codebooks; Higgs:8 codebooks25fps delay pattern; Qwen: multi-codebook LM/causal decoder. Các mô hình AR này có đường serving/cache/continuous batching được tài liệu mô tả. VieNeu v3 cũng dùng codec/backbone/acoustic decoder và loop từng frame nhưng chưa xác lập topology tương đương Fish hay Qwen (**Reported**).[^fish2-card][^higgs3-card][^qwen3-card][^vieneu-tts-repo]

**Synthesis:** lợi thế là hợp audio streaming và reuse tối ưu LLM serving; chi phí tuần tự/cache/concurrency vẫn phải đo. Với vi, chuyên hóa frontend/data/voice và runtime có thể quan trọng hơn size model. Không tự suy codec tốt hoặc GPU lớn sẽ cho thanh điệu tốt nhất.

### 2. Continuous-latent diffusion-autoregressive

VoxCPM2: `LocEnc→TSLM→RALM→LocDiT`, AudioVAE16→48kHz, LM rate6.25Hz; dots: BPE LLM→flow-matching patch→causal VAE decoder, không discrete codec token. dots-mf distilled từ soar, NFE4 thay teacher10; NFE2/3 giảm WER/SIM theo bảng en/zh (**Reported**).[^voxcpm2-card][^dots-mf-card]

**Synthesis:** hướng hợp cloning/prosody và nghiên cứu quality–latency, không có nghĩa diffusion bắt buộc full-utterance. VoxCPM2 có API streaming cụ thể; số bước flow làm budget compute cần quản lý. 6.25Hz không phải TTFA; tokenizer-free không có nghĩa không text tokenizer. Chọn VoxCPM2 làm quality challenger trước dots cho vi vì language support và streaming evidence rõ hơn.

### 3. Lightweight ONNX / whole-chunk synthesis

ONNX là runtime/export format, **không phải kiến trúc**. Supertonic3 card chưa đủ topology; LGTM có text encoder/duration predictor/vector-estimator/vocoder; VieNeu Nano là48M flow matching với finished-chunk output (**Reported**).[^supertonic3-card][^lgtm-card][^vieneu-tts-repo]

Kokoro Vietnamese cũng có ONNX/PyTorch cùng Vietnamese G2P nhưng chưa có streaming API hay performance figures trong capture. sanoTTS voice vi là piperlite 1.46M/22.05 kHz, không phải nano INT8 English dùng cho ESP32; đây là hai hướng CPU/edge bổ sung cần benchmark riêng (**Reported/Synthesis**).[^kokoro-vi-concept][^sanotts-concept]

**Synthesis:** dùng short-clause chunker nếu backend không frame-streaming có thể giảm first-response wait, đổi lại boundary prosody và overhead. Không dùng RTF rất thấp để suy TTFA thấp: full-chunk, network và playback buffer vẫn tồn tại. Supertonic3 là CPU challenger, Nano là quality-for-speed fallback, LGTM còn thiếu license.

### 4. Mass multilingual hoặc tự fine-tune

OmniVoice diffusion-LM có coverage rộng nhưng card/API đã inspect không chứng minh incremental audio; HF handler full-utterance. Qwen official chưa vi; community adaptation mới là một checkpoint khác. VieNeu/VoxCPM2 có LoRA pointers, dots base/soar có training pointers (**Reported**).[^omnivoice-card][^hf-pipeline][^qwen3-card][^vi-stack][^vieneu-tts-repo][^voxcpm2-card][^dots-mf-card]

**Synthesis:** không bắt đầu production bằng tự huấn luyện multilingual foundation model khi có baseline vi deployable. Fine-tune sau khi xác định failure cases, có consent/data rights và baseline. API có thể giảm vận hành local nhưng cần đánh giá privacy, network, SLA và cancellation; chưa có matched cloud evidence để chọn vendor.

## Triển khai realtime: hai tầng streaming khác nhau

**Audio-output streaming** (có tiếng trước khi xong utterance) khác **incremental text-input/bi-streaming** (nhận tiếp tokens khi nói). `infer_stream(text=...)` của VieNeu và `generate_streaming(text=...)` của VoxCPM2 chứng minh tài liệu mô tả loại thứ nhất, không tự chứng minh loại thứ hai. Qwen family quảng cáo Dual-Track nhưng không có vi official; CosyVoice bi-streaming cũng không thêm vi vào checkpoint (**Reported/Synthesis**).[^vieneu-tts-repo][^voxcpm2-card][^qwen3-card][^tts-survey]

MOSS-TTS Local v1.5 card cũng mô tả audio-output streaming qua SGLang-Omni (`stream=true`, PCM 48 kHz), không chứng minh incremental text-input hay TTFA đạt SLO. Cookbook/config chưa inspect; HF codec native stereo nhưng stream example dùng mono, nên adapter phải xác nhận channel count. Flagship MOSS-TTS v1.5 chỉ có HF batch generation trong capture được compile, không được gán cùng streaming path (**Reported/Synthesis**).[^moss-local-v15-concept][^moss-v15-concept]

Thiết kế đề xuất (**Synthesis**, chưa triển khai): độ trễ end-of-user-speech→first audible sample còn gồm endpointing + ASR + LLM first meaningful chunk + TTS TTFA + transport/playback. Con số115ms của TTS không phải115ms voice-to-voice. Không cộng các phép đo overlap như thể tất cả tuần tự; đo critical path thực.

1. LLM streaming → chunker theo cụm/câu có nghĩa → Vietnamese text normalizer → TTS audio streaming → bounded playback queue. Không chờ full LLM reply, không gửi từng token rời rạc.
2. Normalize tiền/số/ngày/giờ/units/abbreviations/tên riêng; không cắt giữa một giá trị còn đang hoàn thành. Dùng regression cases thanh điệu, địa danh, từ tiếng Anh xen kẽ; reference một speaker sạch và cache/enroll một lần.[^vi-stack][^vieneu-tts-repo]
3. Pin SDK/weights/voice IDs: VieNeu card3.7.1 có23voices/default Minh Quân, README3.8.x có25/default Hải Đăng; introspection của bản cài mới là authoritative (**Reported**).[^vieneu-v3-card][^vieneu-tts-repo]
4. Warm model/graphs, giới hạn concurrent streams và queue, backpressure/429; đo dưới shared-GPU load ASR/LLM, không chỉ TTS độc lập.[^vieneu-tts-repo]
5. Backend adapter khai báo format/sample-rate/stream framing/cancellation. VieNeu SDK float32 48kHz khác HTTP s16le48kHz; Higgs SSE base64 WAV khác raw PCM. OpenAI-compatible route không bảo đảm schema/chunk decoding giống nhau (**Reported/Synthesis**).[^vieneu-tts-repo][^higgs3-card]
6. Cancel LLM/TTS/server work và flush client queue khi barge-in; kiểm tra server có thật sự ngừng compute sau disconnect. Tài liệu pipeline mới là starting design, không phải cancellation đã được test ở từng backend.[^vi-stack]

C++/GGUF là deployment alternative, không đổi language/weight license: audio.cpp README có community port `vieneu_v3_turbo` (vi/en,48kHz, GGUF), nhưng guide/weights/parity/streaming chưa inspect; ưu tiên SDK reference trước rồi A/B port. Catalog cũng có VoxCPM2/Supertonic3/Fish/Higgs packagings; port existence không xác nhận quality/latency trên máy đích (**Reported/Synthesis**).[^audio-cpp-repo][^tts-survey]

## Gate chọn model sau A/B

Đề xuất protocol (**Synthesis**, không phải benchmark đã chạy):

- **150–300 prompts tiếng Việt**, gồm sáu thanh, câu hỏi, hội thoại ngắn/dài, tiền/ngày/số điện thoại/đơn vị, tên riêng, code-switch, vùng giọng và các chunk boundaries. Test preset và cùng authorized reference separately; lưu raw text và normalized spoken text.
- Blind pairwise preference/MOS với người Việt; chấm naturalness, tone/pronunciation, conversational prosody, voice consistency. ASR round-trip WER/CER chỉ là proxy và phải manual-audit lỗi; không chọn theo English Seed-TTS hay SIM đơn độc.
- Measure normalization→first byte **và** normalization→first audible sample; queue delay, TTFA P50/P95, chunk cadence/stalls, per-request RTF P95, RAM/VRAM, warm/cold và concurrency1/4/8/16. Test cancellation và recovery, trên toàn stack chạy đồng thời.
- Starting targets có thể chọn TTFA P95≤250–400ms và RTF P95≤0.7 dưới tải thực, nhưng đây là **SLO đề xuất**, không phải khả năng đã chứng minh. Failures/rights là hard gates trước preference score.
- Quyết định: **VieNeu** nếu thắng deployability và đủ quality; **VoxCPM2** nếu cải thiện nghe/cloning có ý nghĩa và vẫn đạt SLO; **Supertonic3** nếu CPU footprint/quality đạt; **Higgs/Fish** chỉ sau quality test vi và commercial agreement.

## Contradictions và giới hạn còn mở

- VieNeu FAQ cho phép commercial artifacts/preset voices nhưng roadmap vẫn personal use; không tự chọn cách diễn giải. SDK23/25 voices là khác version, không đồng nhất default. Training corpus gated/collection undisclosed, consent claim không thay user-cloning rights.[^vieneu-v3-card][^vieneu-tts-repo]
- Higgs card đặt vi tier<5 nhưng thiếu exact score/dataset/normalizer/matched baseline riêng vi. H100617ms là **send-to-full-response**, không TTFA; Fish100ms là H200 thiếu protocol. Không làm matched quality/latency leaderboard từ các con số này.[^higgs3-card][^fish2-card]
- Supertonic3 plots relative `img/metrics/` không có trong raw; không ghi số quality/latency tưởng tượng. VoxCPM2 full evaluation/accelerator docs chưa inspect. VieNeu `docs/streaming.md` nay đã compile trong [VieNeu-TTS Streaming Runtime and Performance](vieneu-tts-streaming-runtime.md), [VieNeu-TTS OpenAI-Compatible Speech API](vieneu-tts-openai-speech-api.md) và [VieNeu-TTS Docker Compose Deployment](vieneu-tts-docker-deployment.md), nhưng `apps/openai_speech.py`, Dockerfiles và weights vẫn chưa inspect. LGTM license missing; dots-mf vi quality/TTFA pending.[^supertonic3-card][^voxcpm2-card][^vieneu-tts-repo][^vieneu-tts-docs][^lgtm-card][^dots-mf-card]
- Gwen-TTS 0.6B: card tự báo finetune ~1.000 h audio vi crawl TikTok nhưng thiếu phương pháp thu thập/lọc/consent, hyperparameters và protocol đánh giá; 9 demo voices chỉ là qualitative clips chưa nghe hay reproduce; `library_name: transformers` trong frontmatter mâu thuẫn với `qwen_tts` import ở usage; chưa có TTFA/streaming nên chưa đổi baseline.[^gwen-tts-card]
- G-OmniVoice: card tự báo held-out vi set nhưng thiếu protocol/dataset/judge/uncertainty; `wer_vs_sim.png` không có trong raw; competitor rows là số in lại, nhãn `VietNeu/v3turbo` chưa khớp naming VieNeu đã compile; chưa có TTFA/streaming nên chưa đổi baseline.[^g-omnivoice-card]
- Kokoro Vietnamese: weights/config/voicepacks và `vig2p` chưa inspect; chưa có training-data details, quality/latency/streaming benchmarks trong capture. ONNX không tự chứng minh realtime.[^kokoro-vi-concept]
- MOSS v1.5: language-tag gains và cloning/prosody improvements là qualitative claims; chưa có matched vi evaluation. Local SGLang cookbook/config/implementation chưa inspect; HF native stereo nhưng streaming example dùng `ffmpeg -ac 1`, nên phải xác nhận channel count thực của stream. Flagship là checkpoint/API riêng, không thừa hưởng streaming evidence của Local.[^moss-local-v15-concept][^moss-v15-concept]
- sanoTTS: Vietnamese piperlite voice chưa được SCOREQ/UTMOS chấm; scorecard English và nano MCU figures không đánh giá voice vi. Không zero-shot cloning; cần rà GPL deployment và test các period-pause/sibilant reports (chưa reproduce, chưa xác lập cho vi).[^sanotts-concept]
- Coverage bổ sung: lần cập nhật này chỉ đọc bốn compiled concepts Kokoro/MOSS Local/MOSS flagship/sanoTTS cùng survey, không mở raw hoặc fetch upstream; coverage ledger và artifact limits của các concept đó được giữ làm giới hạn, không coi là verification mới.[^kokoro-vi-concept][^moss-local-v15-concept][^moss-v15-concept][^sanotts-concept]
- Coverage: local docs chỉ được static-inspect như trên; linked weights, code, tests, figure assets, demo audio, license texts, training data và papers ngoài captures còn pending/unavailable theo model concepts; decorative images/boilerplate không dùng để suy performance. Không model install, audio listening, inference, external live research hay independent corroboration trong phiên này.

## Relationships

- Used by [Vietnamese Speech Pipeline Design](vietnamese-speech-pipeline-design.md): ghép shortlist này với ASR và deployment tools, thêm clause/normalizer, audio-format contract, cancellation và release gates; không bổ sung benchmark hay quality ranking TTS.

- Uses [TTS Model Survey](tts-model-survey.md) để map toàn catalog, nhưng thêm Vietnamese-specific deployment gates và sửa thiếu sót shortlist rộng.[^tts-survey]
- Uses [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md), [VoxCPM2](voxcpm2.md), [Supertonic 3](supertonic-3.md) làm ba baseline deployable có điều kiện; quyết định là synthesis từ support/runtime/license claims.[^vieneu-tts-repo][^voxcpm2-card][^supertonic3-card]
- Depends on [VieNeu-TTS Streaming Runtime and Performance](vieneu-tts-streaming-runtime.md) cho số `max_streams`/TTFA/RTF và điều kiện CPU int8/VNNI của baseline đầu tiên, và trên [VieNeu-TTS Docker Compose Deployment](vieneu-tts-docker-deployment.md) cho profile triển khai `api-gpu`/`api-cpu`; đây là bằng chứng vận hành của tác giả, chưa reproduce (**Reported/Synthesis**).[^vieneu-tts-docs]
- Uses [Kokoro Vietnamese](kokoro-vietnamese.md) và [sanoTTS](sanotts.md) để bổ sung CPU/ultra-small edge candidates, chưa nâng thành realtime baseline vì thiếu Vietnamese quality/TTFA/streaming evidence (**Synthesis**).[^kokoro-vi-concept][^sanotts-concept]
- Uses [MOSS-TTS Local v1.5](moss-tts-local-transformer-v1-5.md) như GPU streaming challenger có Vietnamese support; [MOSS-TTS v1.5](moss-tts-v1-5.md) là sibling cloning/control candidate, không đồng nhất serving path (**Synthesis**).[^moss-local-v15-concept][^moss-v15-concept]
- Complements [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md): primary local TTS cards bổ sung cho AI-report routing, không xác minh toàn end-to-end stack.[^vi-stack]
- Depends on [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md) cho design interruption; phải test cancellation trên backend thực.[^vi-stack]

[^vieneu-tts-repo]: [VieNeu README](../raw/VieNeu-TTS-repo.md) — v3 Turbo NOTE; §2 SDK `Streaming`, `v3 Nano`, CUDA-graph/VNNI paragraphs; §3 API Server; §4 Benchmarks throughput/streaming tables + machine protocol; §5 LoRA; §6 Model Overview; §7 Roadmap.
[^vieneu-v3-card]: [VieNeu v3 card](../raw/VieNeu-TTS-v3-Turbo.md) — frontmatter vi/en; Overview/Architecture & Credits; Using SDK streaming/style; Preset Voices23; Usage Rights & Licensing FAQ (artifact scope, commercial use, speaker consent, gated corpus, authoritative SDK list).
[^vieneu-tts-docs]: [VieNeu supporting docs](../raw/vieneu-tts-docs/README.md) — package ledger; `docs/streaming.md` (API field/format/SSE contract, env table, TTFA/RTF/lead, GPU CUDA-graph vs CPU ONNX mechanism, RTX 3060 `max_streams`/HTTP/cold-GPU/other-machine tables, CPU precision table, troubleshooting); `docker/docker-compose.yml` (profiles, env, healthchecks, GPU reservations).
[^voxcpm2-card]: [VoxCPM2 card](../raw/VoxCPM2.md) — frontmatter/Supported Languages vi; Highlights; Quick Start Streaming; Model Details (architecture,6.25Hz,~8GB); Fine-tuning; Limitations; License.
[^supertonic3-card]: [Supertonic3 card](../raw/supertonic-3.md) — frontmatter/Supported Languages vi; Quick Start; Custom Voices and Audio Samples/Voice Builder; Performance Highlights four image-only subsections; License.
[^higgs3-card]: [Higgs3 card](../raw/higgs-audio-v3-tts-4b.md) — Component Spec; Supported Languages under5 tier vi; Control Tokens; Evaluation Benchmarks; Usage Streaming/Throughput definitions; Creator Use/License.
[^fish2-card]: [Fish S2 Pro card](../raw/s2-pro.md) — Architecture; Supported Languages Other vi; Fine-Grained Inline Control; Production Streaming Performance H200; License.
[^dots-mf-card]: [dots-mf card](../raw/dots.tts-mf.md) — family table; Architecture; Recommended sampling settings; Performance NFE table; Risks and Limitations low-resource Vietnamese WER gap; License.
[^lgtm-card]: [LGTM card](../raw/LGTM.md) — frontmatter/Languages vi; Samples vi_F3/vi_M3; PyTorch Vietnamese example; Options; Files/ONNX graph I/O and sampling loop; no license/performance declaration in inspected card.
[^omnivoice-card]: [OmniVoice card](../raw/OmniVoice.md) — frontmatter `language` line601 vi; Key Features; Usage Python API full waveform; License (CC-BY-NC weights vs Apache code).
[^qwen3-card]: [Qwen3-TTS official card](../raw/Qwen3-TTS-12Hz-1.7B-CustomVoice.md) — Overview Introduction and Released Models Description and Download table (all5 checkpoints share10languages without vi); primary section inspected, not the full1316-line card.
[^tts-survey]: [TTS survey](tts-model-survey.md) — Scope and method; Master catalog (40 model/family rows at this update); Multilingual coverage; Streaming and latency; Edge/packaged deployment; Adjacent concepts; Contradictions/Coverage. Compiled synthesis, not independent verification.
[^hf-pipeline]: [HF pipeline](speech-to-speech-pipeline.md) — TTS notes: OmniVoice, Pocket, and logging (full-utterance handler); Commands (playback buffer). Compiled README claims, implementation not executed.
[^vi-stack]: [Vietnamese stack](vietnamese-realtime-voice-agent-stack.md) — Source and trust; TTS routing and Vietnamese text normalization; Architecture; Evaluation; Coverage and limits. Draft AI-report evidence for community checkpoints/G2P/cancellation, not primary verification.
[^audio-cpp-repo]: [audio.cpp README](../raw/audio.cpp-repo.md) — community models table, row `vieneu_v3_turbo` (vi/en,TTS Clone,GGUF,48kHz,docs/community_models/vieneu_v3_turbo.md); guide/port not inspected.
[^g-omnivoice-card]: [G-OmniVoice model card](../raw/g-omnivoice.md) — intro (Vietnamese OmniVoice finetune, cloning/design); `## Benchmark` (held-out vi WER/SIM/MOS 4-row table, `wer_vs_sim.png` plot reference); `## Usage` (full-waveform `generate`, 24 kHz); `## License` (Apache-2.0 claim, Higgs Audio 2 Community License tokenizer).
[^kokoro-vi-concept]: [Kokoro Vietnamese](kokoro-vietnamese.md) — Artifact layout; Install and runtimes; Inference commands; Relationships; Coverage and limits. Compiled README claims: vi/vig2p/voicepacks, PyTorch/ONNX CPU/CUDA, Apache-2.0; no numeric performance or streaming evidence, artifacts uninspected.
[^moss-local-v15-concept]: [MOSS-TTS Local v1.5](moss-tts-local-transformer-v1-5.md) — Supported languages (vi); v1.5 improvements (language-tag caveat); Hugging Face inference (12-codebook stereo); SGLang-Omni serving (PCM stream request, 48 kHz, `ffmpeg -ac 1` example); License and citation; Coverage and limits. Compiled card claims; cookbook/config and implementation uninspected, numeric benchmarks absent.
[^moss-v15-concept]: [MOSS-TTS v1.5](moss-tts-v1-5.md) — Model identity and lineage (MossTTSDelay-8B API); Supported languages (vi); v1.5 improvements; Hugging Face inference (`generate` then decode); License; Relationships; Coverage and limits. Compiled card claims, not Local serving evidence or independent verification.
[^sanotts-concept]: [sanoTTS](sanotts.md) — Voice roster (`vi-vais1000-1p46m/`, unscored); Two lineages, two graphs (vi piperlite at 22.05 kHz versus nano MCU); Install and deployment paths; License (GPLv3); Extension, cloning posture, and language backlog (no zero-shot, streaming limits); Limitations and open reports; Coverage and limits. Compiled card/thread assertions, no reproduced vi measurements.
[^gwen-tts-card]: [Gwen-TTS 0.6B model card](../raw/gwen-tts-0.6B.md) — frontmatter (`base_model: Qwen/Qwen3-TTS-12Hz-0.6B-Base`, `license: mit`, 11-code `language` with `vi`, `library_name: transformers` vs `qwen_tts` usage); intro plus `Key highlights` (~1.000 h TikTok-crawl finetune, few-second cloning); `## How to Use` (full `generation_config` dict, `generate_voice_clone` with `language="Vietnamese"`/`ref_audio`/`ref_text`, normalization-plus-chunking note); `## Voice Samples` (9 speaker tables, `ref_audio/` plus `infer-audio/` URLs); `## Supported Languages` (Vietnamese primary, non-Vietnamese caveat); `## License` (MIT). No benchmarks, latency, or streaming figures stated.
