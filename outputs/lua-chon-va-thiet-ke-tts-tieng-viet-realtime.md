# Lựa chọn và thiết kế TTS realtime cho tiếng Việt

> **Loại tài liệu:** bài viết tổng hợp (deliverable trong `outputs/`), không phải tri thức canonical của wiki.
> **Ngày cập nhật:** 2026-10-28 (bản đầu: 2026-10-07; bản trước: 2026-10-13).
> **Cơ sở:** chỉ dùng wiki đã compile. Nguồn chính: [Vietnamese Realtime TTS Selection](../wiki/vietnamese-realtime-tts-selection.md) và [TTS Model Survey](../wiki/tts-model-survey.md). Nguồn đã đọc lại trong lần cập nhật này gồm concept của từng model có tiếng Việt: VieNeu v3 Turbo và ba trang vận hành của nó, VoxCPM2, Supertonic 3, MOSS-TTS Local v1.5 và flagship v1.5, Higgs TTS 3, Fish S2 Pro, OmniVoice, G-OmniVoice, Gwen-TTS 0.6B, Qwen3-TTS 0.6B Base, Kokoro Vietnamese, sanoTTS, LGTM-TTS, dots.tts, SeamlessM4T v2. Đọc thêm các trang frontend/normalizer: VietNormalizer, ViSoNorm, Kokoro-82M, Kokoro Python Library, Misaki, eSpeak NG, Phonemizer, StyleTTS 2, CrispASR TTS Engines, Resemblyzer và KVoiceWalk.
> **Cập nhật theo git diff 2026-10-28:** đọc thêm [ZeroTTS](../wiki/zerotts.md), [Audio8 TTS Realistic 0.6B](../wiki/audio8-tts-realistic-0.6b.md), hai bản Preview [0.1B](../wiki/audio8-tts-preview-0.1b.md) / [0.6B](../wiki/audio8-tts-preview-0.6b.md), cùng survey; rà lại [KhanhTTS](../wiki/khanhtts-omnivoice.md), [F5-TTS Vietnamese](../wiki/f5-tts-vietnamese.md) và [Qwen3-TTS 1.7B Vietnamese](../wiki/qwen3-tts-12hz-1.7b-vietnamese.md) vì bản cũ đã lỗi thời. Phần còn lại giữ theo bản trước, không phải rà soát toàn bộ wiki.
> **Phạm vi bằng chứng:** không mở `raw/`, không tải weights, không chạy inference, không nghe audio, không đo benchmark. Mọi con số đều do vendor, tác giả hoặc report công bố (**Reported**). Mọi thứ tự ưu tiên, kiến trúc và tham số đề xuất là suy luận tổng hợp (**Synthesis**). Chưa có phép so sánh MOS, TTFA hay lỗi phát âm tiếng Việt nào được đo trên cùng điều kiện giữa các model.

---

## 0. TL;DR

1. **Baseline triển khai vẫn là [VieNeu-TTS v3 Turbo](../wiki/vieneu-tts-v3-turbo.md).** Lý do: model Vietnamese-first (vi/en, code-switching), có G2P riêng `sea-g2p`, preset giọng ba miền, frame-level streaming, chạy được trên CPU ONNX và GPU PyTorch, kèm server `/v1/audio/speech` kiểu OpenAI và Docker profile. Tài liệu streaming của tác giả (nay đã được compile) cho số đo chi tiết trên RTX 3060: TTFA 89 ms (`max_streams=8`) đến 115 ms (`max_streams=16`) khi có 1 stream, 185 ms median khi có 16 stream.
2. **Các challenger cần A/B:**
   - [ZeroTTS](../wiki/zerotts.md) (202M, ONNX, tiếng Việt, CPU streaming): ứng viên CPU mới; tác giả báo TTFA khoảng 70 ms và RTF khoảng 0.50, chưa được reproduce. Voice encoder không công khai; tạo voice mới cần dịch vụ upload ngoài.
   - [VoxCPM2](../wiki/voxcpm2.md) (2B, Apache-2.0, 48 kHz, có `vi`, có `generate_streaming`, LoRA với 5–10 phút audio): dùng khi ưu tiên cloning/style và có GPU khoảng 8 GB.
   - [Supertonic 3](../wiki/supertonic-3.md) (khoảng 99M, ONNX, có `vi`): dùng khi ưu tiên CPU/on-device. Card chỉ có API trả full waveform và các số đo dạng ảnh.
3. **Challenger GPU streaming thứ ba:** [MOSS-TTS Local v1.5](../wiki/moss-tts-local-transformer-v1-5.md) (Apache-2.0, có `vi`, PCM 48 kHz stream qua SGLang-Omni). Hợp lý khi hạ tầng đã có SGLang-Omni.
4. **Nhóm Vietnamese-finetune cần nghe thử:** [G-OmniVoice](../wiki/g-omnivoice.md) (có bảng WER/SIM/MOS tiếng Việt do vendor công bố, nhưng base weights là CC-BY-NC), [Gwen-TTS 0.6B](../wiki/gwen-tts-0.6b.md) (base Qwen3-TTS 0.6B là Apache-2.0, nhưng dữ liệu crawl từ TikTok chưa rõ quyền; repo chỉ có CLI xuất WAV hoàn chỉnh, không streaming) và [Kokoro Vietnamese](../wiki/kokoro-vietnamese.md) (ONNX + `vig2p`, không có số đo).
5. **Nhóm expressive, chỉ dùng khi có license thương mại riêng:** [Higgs TTS 3](../wiki/higgs-tts-3-4b.md) và [Fish S2 Pro](../wiki/fish-audio-s2-pro.md).
6. **Hệ sinh thái Kokoro gốc không có tiếng Việt.** Mục `lang_code` của Kokoro library, frontend misaki và danh sách ngôn ngữ của Kokoro-FastAPI đều không có `vi`. Kokoro Vietnamese là một artifact riêng, dùng `vig2p`, và phải chạy qua CLI riêng hoặc wrapper tự viết.
7. **Đã có ứng viên cho normalizer tiếng Việt:** [VietNormalizer](../wiki/vietnormalizer.md) (MIT, thuần stdlib, pipeline 19 bước, README báo khoảng 0.6 ms/lần gọi) chuyển văn bản viết sang dạng đọc. [ViSoNorm](../wiki/visonorm-visobert-normalizer.md) làm việc ngược lại: chuẩn hóa văn bản không chuẩn sang văn bản chuẩn. Cả hai đều chưa được kiểm chứng.
8. **Thiết kế quan trọng hơn chọn model.** Chất lượng cảm nhận phụ thuộc vào clause chunker, normalizer + lexicon, hợp đồng audio format, cancellation khi barge-in, warmup, và việc đặt `max_streams` khớp với tải thật.
9. **Audio8 Realistic 0.6B** có `vi`, nhưng số WER tiếng Việt CV3 do card báo là 28.111% và serving H20 chỉ được xác nhận non-streaming; xem là ứng viên nghiên cứu, không thay baseline. Hai bản Audio8 Preview không liệt kê `vi`.
10. **Đây là thứ tự thử nghiệm, không phải bảng xếp hạng chất lượng.** Quyết định cuối phải dựa trên blind listening test tiếng Việt (150–300 prompt) và TTFA P95 đo dưới tải thực trên phần cứng đích.

---

## 1. Cách đọc bài này

| Nhãn | Ý nghĩa |
|---|---|
| **Reported** | Vendor, tác giả hoặc report tự công bố; chưa kiểm chứng độc lập. |
| **Observed** | Thấy được trong tài liệu hoặc code đã capture (API, field, bảng, dòng code), nhưng không chứng minh model thực sự nói tốt. |
| **Synthesis** | Suy luận của bài viết từ các bằng chứng được dẫn. |
| **Unverified** | Chưa có sự kiện kiểm chứng. Điều này không có nghĩa là sai. |

Số liệu từ các card khác nhau **không so sánh trực tiếp được** vì mỗi card dùng GPU, harness, normalizer và ASR judge khác nhau. Bài này áp dụng cảnh báo chung của TTS Model Survey: chênh lệch WER dưới khoảng 0.3 điểm, hoặc chênh latency dưới khoảng 2 lần giữa hai card khác nhau, thì không đủ để tự nó quyết định lựa chọn.

---

## 2. Có gì mới kể từ bản 2026-10-07

Các dòng 2026-10-28 dưới đây phản ánh git diff đang có; phần lịch sử 2026-10-07–2026-10-13 được giữ từ bản trước, không phải danh sách đầy đủ mọi ingest giữa hai mốc.

| Thay đổi trong wiki | Ảnh hưởng tới lựa chọn TTS tiếng Việt |
|---|---|
| [ZeroTTS](../wiki/zerotts.md) | Thêm challenger Vietnamese-first CPU streaming; voice encoder không công khai và số đo chỉ do vendor báo. |
| [Audio8 Realistic 0.6B](../wiki/audio8-tts-realistic-0.6b.md) và [Preview 0.1B](../wiki/audio8-tts-preview-0.1b.md); cập nhật Preview 0.6B | Realistic bổ sung `vi` so với Preview, nhưng chưa có benchmark streaming; 0.1B không liệt kê `vi`, license có ngưỡng doanh thu. Không chuyển license hay tính năng giữa các checkpoint. |
| Compile tài liệu streaming và Docker của VieNeu (revision `85344322`), tách thành 3 concept: [Streaming Runtime](../wiki/vieneu-tts-streaming-runtime.md), [OpenAI-Compatible API](../wiki/vieneu-tts-openai-speech-api.md), [Docker Compose](../wiki/vieneu-tts-docker-deployment.md) | Baseline có thêm số đo theo `max_streams` 8/16/32, cơ chế codec dùng chung, latency khi GPU nguội, bảng HTTP, quy tắc sizing, hợp đồng API đầy đủ, và tuyên bố "đóng kết nối sẽ giải phóng slot". Các mục 8.4–8.6 được cập nhật theo đây. |
| Compile repo snapshot Gwen-TTS `f0f24d8` | Đã xác định: CLI chỉ ghi một WAV hoàn chỉnh, không có đường streaming, không có normalizer hay server. Đối số `language` bị comment out trong `inference.py`. Môi trường đã test: Python 3.11, CUDA 12.4, VRAM tối thiểu 4 GB. |
| Compile concept [Qwen3-TTS-12Hz-0.6B-Base](../wiki/qwen3-tts-12hz-0.6b-base.md) | Base của Gwen là Apache-2.0 và không có `vi`. Rủi ro license của Gwen vì vậy dồn chủ yếu về quyền dữ liệu, không nằm ở weights base (**Synthesis**). |
| Compile [VietNormalizer](../wiki/vietnormalizer.md) và [ViSoNorm](../wiki/visonorm-visobert-normalizer.md) | Bước normalizer trong pipeline đã có ứng viên cụ thể. |
| Compile [Kokoro-82M](../wiki/kokoro-82m.md), [Kokoro Python Library](../wiki/kokoro-python-library.md), [Kokoro-FastAPI](../wiki/kokoro-fastapi.md), [Misaki](../wiki/misaki.md) và [Misaki Language Frontends](../wiki/misaki-language-frontends.md), [KVoiceWalk](../wiki/kvoicewalk.md), [StyleTTS 2](../wiki/styletts2.md) | Xác nhận hệ Kokoro gốc **không có `vi`**. Misaki chỉ ghi credit cho Viphoneme, không có module tiếng Việt. Không suy được khả năng của Kokoro Vietnamese từ upstream. Catalog survey tăng lên 41 dòng. |
| Compile [eSpeak NG](../wiki/espeak-ng.md), [Phonemizer](../wiki/phonemizer.md) và [Phonemizer Backends](../wiki/phonemizer-backends.md) | Wiki chưa xác lập được độ phủ tiếng Việt của eSpeak NG hay của backend nào trong phonemizer, vì danh sách ngôn ngữ chưa được capture. |
| Compile [Resemblyzer](../wiki/resemblyzer.md) | Có công cụ tạo speaker embedding 256 chiều để làm proxy SIM khi đánh giá cloning. README nói hoạt động tốt nhất với tiếng Anh, chưa có bằng chứng cho tiếng Việt. |
| Compile [CrispASR TTS Engines](../wiki/crispasr-tts-engines.md) | Runtime C++ có `/v1/audio/speech`, gồm các engine voxcpm2-tts (48 kHz, cloning) và omnivoice. Bảng engine đã capture không ghi engine tiếng Việt riêng. |
| Ingest card sanoTTS, G-OmniVoice, MOSS v1.5 (2026-10-07) | Đã có trong bản trước; giữ nguyên, bổ sung chi tiết ở mục 4. |

Không suy rằng các ingest khác giữa hai mốc không ảnh hưởng lựa chọn: chúng không được rà toàn diện trong lần cập nhật theo diff này.

---

## 3. Bài toán: "TTS realtime tiếng Việt" đòi hỏi gì?

### 3.1. Các trục quyết định

| Trục | Câu hỏi | Vì sao quan trọng với tiếng Việt |
|---|---|---|
| **Ngôn ngữ / frontend** | Có hỗ trợ `vi` chính thức không? Có G2P và normalizer tiếng Việt không? | Sáu thanh điệu và dấu; một lỗi G2P đổi nghĩa (`chánh` → `tránh`). Có tên `vi` trong danh sách ngôn ngữ chưa có nghĩa là đọc đúng thanh. |
| **Streaming** | Có phát audio trước khi tổng hợp xong cả câu không? | Voice agent cần tiếng sớm. API trả full waveform buộc phải chunk theo mệnh đề. |
| **TTFA** | Thời gian đến chunk audio đầu tiên, P50/P95, dưới tải? | Nằm trên critical path voice-to-voice. |
| **RTF mỗi stream** | Sinh audio có nhanh hơn tốc độ phát không? | RTF lớn hơn 1 thì playback bị giật (underrun). |
| **Concurrency** | Một GPU/CPU chịu được bao nhiêu stream mà vẫn giữ P95? | Quyết định chi phí và capacity. |
| **Phần cứng** | GPU consumer, datacenter, CPU, hay edge/MCU? | Giới hạn ngay danh sách ứng viên. |
| **Giọng** | Preset, cloning zero-shot, LoRA, hay voice design? | Brand voice, consent của người được clone, tính nhất quán giọng. |
| **License** | Weights, voicepack, tokenizer, dữ liệu huấn luyện có cho thương mại không? | **Hard gate**, xét trước điểm chất lượng. |
| **Code-switch** | Có đọc được từ tiếng Anh xen trong câu tiếng Việt không? | Hội thoại thực tế thường có từ tiếng Anh. |

### 3.2. Hai tầng streaming khác nhau

- **Audio-output streaming:** model nhận một đoạn text hoàn chỉnh rồi trả audio theo từng chunk/frame trước khi xong câu. Thuộc loại này (**Reported**): VieNeu `infer_stream(text=...)`, VoxCPM2 `generate_streaming(text=...)`, MOSS Local qua SGLang-Omni (`stream=true`, PCM 48 kHz), Higgs (SSE), Fish (SGLang).
- **Incremental text-input / bi-streaming:** model nhận tiếp token từ LLM trong khi đang nói. Qwen3-TTS (Dual-Track), CosyVoice và VibeVoice-Realtime quảng cáo khả năng này, nhưng **không checkpoint chính thức nào trong số đó có `vi`** (**Reported**).

**Hệ quả (Synthesis):** với các backend tiếng Việt đã khảo sát ở đây, dùng **clause-level chunking** làm phương án tích hợp: gom token thành mệnh đề có nghĩa rồi gọi TTS cho từng mệnh đề. Đây không phải chứng minh rằng mọi backend tiếng Việt đều thiếu incremental text input.

### 3.3. Đừng trộn throughput với streaming

- VieNeu: GPU batched RTF 0.011–0.02 là **tổng audio của nhiều câu trong một batch**. RTF của một stream streaming là 0.49–0.59 (**Reported**).
- RTF rất thấp của OmniVoice (0.025) hay của Supertonic không có nghĩa là TTFA thấp, nếu API phải sinh xong cả câu mới trả về.
- RTF của sanoTTS (0.03–0.04 cho voice vi trên CPU qua audio.cpp, theo thread của tác giả) cũng là tốc độ sinh của cả câu, không phải TTFA.

---

## 4. Survey các model TTS có tiếng Việt trong wiki

[Catalog TTS](../wiki/tts-model-survey.md) ghi **49 dòng model/family**; danh sách dưới đây là shortlist của bản trước được bổ sung theo diff, không phải danh mục đầy đủ. Các model được chọn có bằng chứng tiếng Việt ở một mức nào đó. Mọi khả năng và số liệu là **Reported**. Cách phân nhóm và đánh giá mức bằng chứng là **Synthesis**.

### 4.1. Bậc thang bằng chứng tiếng Việt

| Mức | Ý nghĩa | Model |
|---|---|---|
| **A. Vietnamese-first** | Huấn luyện chủ yếu cho vi, có frontend/dữ liệu vi riêng, có giọng vi | VieNeu v3 Turbo (và Nano), ZeroTTS, G-OmniVoice, Gwen-TTS 0.6B, Kokoro Vietnamese, KhanhTTS, F5-TTS Vietnamese, Qwen3-TTS 1.7B Vietnamese |
| **B. Multilingual, `vi` nằm trong danh sách hỗ trợ** | `vi` nằm trong bảng ngôn ngữ; chất lượng cần đánh giá riêng | VoxCPM2, Supertonic 3, MOSS Local v1.5, MOSS v1.5 flagship, Fish S2 Pro (nhóm "Other"), OmniVoice, LGTM-TTS, sanoTTS (voice `vi`), Audio8 Realistic 0.6B (có điểm vi do vendor báo) |
| **B+. Multilingual, có tuyên bố chất lượng vi** | Card xếp vi vào một tier chất lượng, nhưng không có điểm số chi tiết | Higgs TTS 3 (tier WER/CER < 5) |
| **C. Tự thừa nhận yếu với vi** | Card nói WER vi cao hơn ngôn ngữ giàu tài nguyên | dots.tts-mf / soar |
| **D. Kề cận** | Có speech output `vie` nhưng là model dịch | SeamlessM4T v2 Large |
| **E. Chưa xác lập** | Engine hoặc frontend có thể có vi nhưng danh sách ngôn ngữ chưa được capture | eSpeak NG, các backend của Phonemizer |
| **F. Không có `vi`** | Danh sách hỗ trợ đã compile không có vi | Qwen3-TTS chính thức (cả Base lẫn CustomVoice), Kokoro-82M / Kokoro library / Kokoro-FastAPI, misaki, CosyVoice2, Fun-CosyVoice3, Audio8 Preview 0.1B / 0.6B, Chatterbox, Pocket, Sopro, Soprano, VibeVoice, Breeze, GLM-TTS, IndexTTS2/2.5, GPT-SoVITS, AuK-Flash, Supertonic v1/v2, Voxtral, MOSS-TTS-Nano, Irodori, Indic Parler, Inflect-Nano |

### 4.2. Bảng so sánh tổng hợp

| Model | Kích thước / kiến trúc | Sample rate | Giọng | Streaming | Latency/tốc độ đã công bố | Phần cứng / runtime | License |
|---|---|---|---|---|---|---|---|
| [VieNeu v3 Turbo](../wiki/vieneu-tts-v3-turbo.md) | Không công bố số tham số; backbone + acoustic decoder + codec `MOSS-Audio-Tokenizer-Nano`; G2P `sea-g2p`; khoảng 10k giờ vi/en | 48 kHz | 25 preset (ba miền), cloning 3–8 s, LoRA, emotion tag thử nghiệm | **Frame-level** (frame 80 ms) | GPU RTX 3060: 115 ms / RTF 0.49 (1 stream), 185 ms / 0.59 (16 stream); CPU int8: 140–195 ms / RTF 0.35 | CPU ONNX không cần torch; GPU PyTorch + CUDA graph; SDK, `/v1/audio/speech`, Docker | Apache-2.0 theo FAQ của card; roadmap ghi "on-device, personal use" (mâu thuẫn) |
| VieNeu v3 Nano | 48M, flow matching, ONNX | 24 kHz | 11 preset + cloning | Chỉ chunk đã hoàn chỉnh | CPU i5: RTF 0.22 (16 step), 0.11 (8 step); tải 282 MB, load khoảng 3 s | CPU, không cần torch | Như VieNeu |
| [ZeroTTS](../wiki/zerotts.md) | 202M, ONNX, speaker latent | 48 kHz | 8 preset; voice encoder không công khai | `synthesize_stream`, float32 | CPU: 53–89 ms first audio, RTF 0.47–0.53; 1 request, 8 core, phần cứng không nêu | CPU/browser; khoảng 900 MB fp32 | MIT code/weights, codec Apache-2.0 theo README; license text chưa kiểm tra |
| [Audio8 Realistic 0.6B](../wiki/audio8-tts-realistic-0.6b.md) | 601M + codec, DualAR | 44.1 kHz | Zero-shot cloning + reference-free | H20 SGLang test **non-streaming**; chưa có benchmark streaming | CV3 vi WER 28.111%; MiniMax vi CER 7.966%, khác dataset/metric; không có TTFA | CUDA khuyến nghị; SGLang Omni | Apache-2.0 theo card; license/NOTICE chưa inspect |
| [VoxCPM2](../wiki/voxcpm2.md) | 2B, diffusion-AR không tokenizer (`LocEnc → TSLM → RALM → LocDiT`), backbone MiniCPM-4 | 48 kHz | Voice design, cloning có điều khiển và "ultimate", LoRA 5–10 phút | Có `generate_streaming` | RTX 4090: RTF khoảng 0.3 (0.13 với Nano-vLLM); chưa có TTFA | GPU khoảng 8 GB; CUDA ≥ 12; có GGUF trong audio.cpp và engine trong CrispASR | Apache-2.0 |
| [Supertonic 3](../wiki/supertonic-3.md) | Khoảng 99M, ONNX | Chưa ghi nhận | Preset + Voice Builder (trả phí), tag `<laugh>` `<breath>` `<sigh>` | Ví dụ trả full waveform | Chỉ có biểu đồ dạng ảnh, không có số | CPU-first, on-device; có GGUF trong audio.cpp | OpenRAIL-M (weights), MIT (code) |
| [MOSS-TTS Local v1.5](../wiki/moss-tts-local-transformer-v1-5.md) | Local Transformer trên codec MOSS-Audio-Tokenizer-v2, 12 codebook | 48 kHz stereo | Cloning, `[pause X.Ys]`, điều khiển độ dài theo token, khuyến nghị gắn language tag | PCM stream qua SGLang-Omni | Chưa có số | HF Transformers, SGLang-Omni; GGUF BF16/Q8 trong audio.cpp | Apache-2.0 theo card |
| [MOSS-TTS v1.5 flagship](../wiki/moss-tts-v1-5.md) | MossTTSDelay-8B | Chưa ghi | Cloning, pause, duration | Chỉ batch `generate` trong capture | Chưa có số | GPU lớn | Apache-2.0 theo card |
| [Higgs TTS 3](../wiki/higgs-tts-3-4b.md) | Khoảng 4B, codec AR, 8 codebook, 25 fps | — | Cloning, inline emotion/style/prosody/SFX | SSE, chunk là WAV base64 | H100, c=1: 617 ms là **toàn bộ response**, RTF 0.147 | SGLang-Omni, vLLM-Omni | Boson Research/NC + Creator Use Grant |
| [Fish S2 Pro](../wiki/fish-audio-s2-pro.md) | 4B Slow AR + 400M Fast AR, codec RVQ 10 codebook khoảng 21 Hz | — | Free-form inline tag | SGLang | H200: khoảng 100 ms TTFA, RTF 0.195; không có protocol | SGLang | Fish Research License (NC) |
| [OmniVoice](../wiki/omnivoice.md) | Diffusion-LM, 600+ ngôn ngữ | 24 kHz | Cloning, voice design theo thuộc tính | Card trả full audio; handler HF chờ hết utterance | RTF 0.025 (không ghi phần cứng) | Python; omnivoice.cpp GGUF | CC-BY-NC (weights), Apache-2.0 (code) |
| [G-OmniVoice](../wiki/g-omnivoice.md) | Finetune OmniVoice (backbone Qwen3-0.6B + codec Higgs Audio 2) | 24 kHz | Cloning 3–10 s, voice design theo thuộc tính (ví dụ "northern Vietnamese accent") | `generate` trả full waveform | Không có TTFA; held-out vi: WER 0.0259 / SIM 0.890 / MOS 7.685 | GPU, torch 2.8 cu128, fp16 | Card ghi Apache-2.0; tokenizer theo Boson license; base weights CC-BY-NC |
| [Gwen-TTS 0.6B](../wiki/gwen-tts-0.6b.md) | Finetune Qwen3-TTS-12Hz-0.6B-Base trên khoảng 1.000 giờ crawl TikTok | Chưa ghi | Cloning (ref audio + transcript), 9 demo voice | CLI ghi WAV hoàn chỉnh, **không có streaming** | Không có số | Python 3.11, CUDA 12.4, VRAM ≥ 4 GB (mức tối thiểu tuyên bố); `qwen-tts` | MIT theo card; base Apache-2.0; quyền dữ liệu TikTok chưa rõ |
| [Kokoro Vietnamese](../wiki/kokoro-vietnamese.md) | Kokoro `KModel` finetune; G2P `vig2p` | Chưa ghi | Voicepack mặc định + bổ sung (chỉ thấy tên `diem_trinh`); không cloning | Không có API streaming | Không có số | PyTorch / ONNX Runtime CLI, CPU hoặc CUDA | Apache-2.0 theo capture |
| [sanoTTS](../wiki/sanotts.md) (voice vi) | `vi-vais1000-1p46m`, 1.46M, piperlite (chưng cất từ Piper/VITS) | 22.05 kHz | Một voice cố định; không zero-shot | Chưa có API chunk-streaming được xác nhận | audio.cpp CPU: RTF voice piperlite 0.032–0.039 (thread tác giả); voice vi chưa được chấm điểm | numpy, WASM browser, C | GPL-3.0 |
| [LGTM-TTS](../wiki/lgtm-tts.md) | Text encoder + duration predictor + vector estimator lặp + vocoder | 44.1 kHz | 10 preset + cloning cross-lingual 5–15 s | Không | Không có số | PyTorch / ONNX (4 graph) | **Không ghi license** |
| [dots.tts-mf / soar](../wiki/dots-tts-mf.md) | 2B continuous AR + flow head; mf distill xuống NFE 4 | 48 kHz | Cloning | Chưa có TTFA | Chỉ có số cho en/zh | GPU | Apache-2.0 |
| [SeamlessM4T v2](../wiki/seamless-m4t-v2-large.md) | 2.3B UnitY2 (dịch) | — | Không cloning | — | — | — | CC-BY-NC |

### 4.3. Ghi chú theo từng model

**VieNeu v3 Turbo (mức A, baseline).**
- Điểm mạnh là **độ đầy đủ của đường triển khai**, không phải MOS vượt trội. Có SDK, server OpenAI-compatible, Docker, giới hạn stream, 429, health check, watermark, số đo kèm điều kiện cụ thể (RTX 3060 12 GB, i5 thế hệ 12, Windows 11, torch 2.8 cu128 bf16, ORT 1.24, SDK 3.8.x, tháng 9/2026).
- Cố tình thiết kế cho phần cứng consumer. Tác giả ước lượng (không đo) rằng GPU lớn hơn không giảm TTFA nhiều, vì chi phí bị chi phối bởi launch overhead chứ không phải FLOPS.
- Điểm yếu: license chưa nhất quán, corpus bị gated, lỗi G2P `chánh` → `tránh` (issue #207, chỉ có report thứ cấp nhắc lại), danh sách voice khác nhau giữa các phiên bản (card 3.7.1: 23 voice, mặc định Minh Quân; README 3.8.x: 25 voice, mặc định Hải Đăng).
- Có community port C++ `vieneu_v3_turbo` (GGUF, 48 kHz) trong audio.cpp. Chưa ai kiểm tra parity hay streaming của port này.

**ZeroTTS (mức A, challenger CPU streaming).**
- Vendor báo ZeroBench raw-text WER 1.03% và CPU TTFA 53/66/89 ms cho 26/77/227 ký tự, RTF 0.51/0.47/0.53: một request, tám thread pin core, mỗi mẫu sáu lần bỏ hai lần đầu; không nêu model CPU. Không suy ra P95, concurrency hay latency end-to-end. Trang wiki là **draft**; benchmark, code và weights chưa kiểm tra.
- `synthesize_stream` trả float32 48 kHz; API `synthesize()` không tự normalize, trong khi CLI/UI bật mặc định. Cần test tránh normalize hai lần. Voice mới cần tạo latent bằng dịch vụ ngoài; upload reference là ranh giới privacy/consent, không phải cloning hoàn toàn offline. Preset được mô tả là dành cho demo/đánh giá; rà quyền trước production. Dataset benchmark CC-BY-NC-4.0 tách biệt MIT code/weights và Apache-2.0 codec theo README.

**Audio8 Realistic 0.6B (mức B, nghiên cứu).**
- Card liệt kê 23 ngôn ngữ gồm `vi`, không giống hai Preview. CV3 tiếng Việt WER 28.111% trên 500 mẫu; MiniMax CER 7.966% trên 100 mẫu. Hai số khác dataset và metric, không so trực tiếp hoặc xếp hạng với model khác.
- H20 BF16 chỉ xác nhận API non-streaming, không benchmark streaming/throughput; không có TTFA, VRAM hoặc hiệu năng CPU. `trust_remote_code=True` cần review code; license/NOTICE chưa inspect. Không giả định ONNX hoặc streaming của Preview hoạt động với Realistic.

**VoxCPM2 (mức B, challenger GPU).**
- License sạch nhất trong nhóm chất lượng cao (Apache-2.0), 48 kHz, có streaming API, LoRA chỉ cần 5–10 phút audio.
- Chưa có TTFA và chưa có điểm tiếng Việt riêng. Card thừa nhận chất lượng thay đổi theo lượng dữ liệu của từng ngôn ngữ. Voice design có thể cần sinh lại 1–3 lần.
- Phải tự viết service: card không mô tả server, giới hạn stream hay cancellation.

**Supertonic 3 (mức B, challenger CPU).**
- Nhỏ (khoảng 99M), CPU-first, phủ 31 ngôn ngữ, có expression tag.
- Mọi số đo hiệu năng và chất lượng chỉ ở dạng ảnh không có trong raw. Giọng tùy chỉnh phải đi qua Voice Builder trả phí. Không lấy RTF của Supertonic 2 để suy cho bản 3.

**MOSS-TTS Local v1.5 (mức B, challenger GPU streaming).**
- `vi` mới được thêm ở v1.5. Card khuyến nghị luôn đặt language tag; nếu bỏ trống, một số ngôn ngữ có thể kém hơn v1.0.
- Codec native stereo, nhưng ví dụ streaming dùng `ffmpeg -ac 1`. Adapter phải xác nhận số kênh thực tế. Cookbook SGLang chưa được inspect.

**Higgs TTS 3 và Fish S2 Pro (mức B+/B, expressive, NC).**
- Mạnh về điều khiển cảm xúc bằng inline tag và có streaming qua SGLang.
- Weights non-commercial. Muốn host API hoặc nhúng vào sản phẩm cần license thương mại riêng.
- Higgs xếp vi vào tier < 5 nhưng không có điểm số vi. Fish xếp vi vào nhóm "Other", không thuộc Tier 1/2.

**OmniVoice và G-OmniVoice (mức B và A).**
- G-OmniVoice có **bảng số đo tiếng Việt** (WER, SIM, MOS) so với các model khác, nhưng đây là số vendor tự đo, không có protocol, dataset hay judge, và ảnh `wer_vs_sim.png` không có trong raw.
- Nhãn `VietNeu/v3turbo` trong bảng không khớp với tên VieNeu đã compile. Không dùng con số này để kết luận VieNeu kém hơn.
- Card ghi Apache-2.0, nhưng base OmniVoice có weights CC-BY-NC và tokenizer theo Boson license. Cần rà lineage trước khi dùng thương mại.
- Cả hai chỉ trả full waveform. Muốn dùng realtime phải chunk theo mệnh đề và đo TTFA.
- Base OmniVoice có bản omnivoice.cpp GGUF. Việc convert được weights của G-OmniVoice sang đó là **Unverified**.

**Gwen-TTS 0.6B (mức A, ứng viên cloning).**
- Base [Qwen3-TTS-12Hz-0.6B-Base](../wiki/qwen3-tts-12hz-0.6b-base.md) là Apache-2.0. Rủi ro license vì vậy tập trung ở dữ liệu khoảng 1.000 giờ crawl từ TikTok (không rõ cách thu thập, lọc hay consent).
- Repo `f0f24d8`: `inference.py` có `# language=language` bị comment out, nên tùy chọn `--language` không có tác dụng; CLI tự fallback sang `sdpa` khi không có `flash_attn`; repo không có normalizer hay server, dù demo online có (**Observed**).
- Sampling khuyến nghị khá "chặt": `temperature=0.3`, `repetition_penalty=2.0`.
- Cùng kiến trúc với Qwen3-TTS, nên về lý thuyết có thể thử qua các runtime streaming của Qwen3-TTS (vLLM-Omni, Faster Qwen3-TTS). Đây chỉ là giả thuyết (**Synthesis/Unverified**). Wiki chưa có bằng chứng nào về việc các runtime đó load được finetune này.

**Kokoro Vietnamese (mức A, ứng viên CPU).**
- Có ONNX export, `vig2p`, nhiều voicepack. Không có sample rate, kích thước, dữ liệu huấn luyện hay số đo nào trong capture.
- Hệ Kokoro gốc không có `vi`: Kokoro-82M (8 ngôn ngữ, StyleTTS 2 decoder-only, 24 kHz), `KPipeline` không có `lang_code` vi, misaki không có module vi, Kokoro-FastAPI không có vi. Không thể triển khai Kokoro Vietnamese bằng cách trỏ Kokoro-FastAPI hay CrispASR `--backend kokoro` vào nó (**Synthesis**).
- KVoiceWalk tìm voice tensor mới cho Kokoro-82M. Chưa có bằng chứng nó áp dụng được cho voicepack tiếng Việt.

**sanoTTS (mức B, MCU/edge).**
- Voice vi 1.46M, 22.05 kHz, chạy bằng numpy thuần, WASM hoặc C. Chưa được chấm SCOREQ/UTMOS.
- Các số đo ESP32 và điểm nano INT8 là của voice tiếng Anh, không áp dụng cho voice vi.
- Pipeline dùng phoneme của espeak-ng. Điều này gợi ý rằng espeak-ng có đường xử lý tiếng Việt, nhưng concept eSpeak NG trong wiki vẫn để mở độ phủ vi (**Synthesis**).
- GPL-3.0.

**LGTM-TTS, dots.tts, MOSS flagship (nghiên cứu).**
- LGTM có `vi`, 44.1 kHz, ONNX, cloning, nhưng không ghi license và card tự nói được "Claude Opus 5.5" xây dựng. Không đưa vào production.
- dots tự thừa nhận khoảng cách WER với tiếng Việt.
- MOSS flagship 8B không có đường streaming trong capture.

---

## 5. Bức tranh kiến trúc

Phân nhóm là **Synthesis** của survey. Cơ chế của từng model là **Reported**.

| Hướng kiến trúc | Ví dụ có vi | Ưu điểm | Lưu ý cho tiếng Việt |
|---|---|---|---|
| **Codec-token AR** | VieNeu v3 Turbo, MOSS Local, Higgs, Fish, Audio8 Realistic | Hợp với audio streaming; tái dùng hạ tầng LLM serving (KV cache, continuous batching) | Model to và codec tốt không đảm bảo thanh điệu đúng. Frontend, dữ liệu vi và runtime quan trọng hơn kích thước. Có thể lặp hoặc bỏ chữ. |
| **Continuous-latent diffusion-AR** | VoxCPM2, dots.tts | Tốt cho cloning và prosody; đánh đổi quality–latency qua số bước flow | VoxCPM2 có streaming API. 6.25 Hz là token rate của LM, không phải TTFA. |
| **Diffusion-LM non-AR** | OmniVoice, G-OmniVoice | Phủ ngôn ngữ rộng, RTF thấp | API đã inspect chỉ trả full waveform. |
| **Discrete multi-codebook LM** | Gwen-TTS (trên Qwen3-TTS 12 Hz) | Kiến trúc gốc có streaming ở tầng serving | Checkpoint chính thức không có vi. Finetune vi hiện chỉ có đường xuất full WAV. |
| **Lightweight / ONNX / StyleTTS-lineage** | ZeroTTS, Supertonic 3, VieNeu Nano, Kokoro Vietnamese, LGTM | Chạy CPU, footprint nhỏ | ONNX là **định dạng runtime**, không phải kiến trúc. Phần lớn sinh xong cả chunk rồi mới trả. |
| **Piper/VITS chưng cất siêu nhỏ** | sanoTTS | Chạy được trên MCU | GPL-3.0, không cloning, voice vi chưa được chấm. |

**Chọn kiến trúc theo yêu cầu (Synthesis):**

| Yêu cầu chính | Hướng ưu tiên |
|---|---|
| Streaming thấp trễ trên GPU, nhiều phiên | Codec-AR có frame-level streaming và server có giới hạn stream (VieNeu, MOSS Local; Higgs/Fish nếu có license) |
| Cloning/style chất lượng cao, chấp nhận tốn GPU | VoxCPM2; G-OmniVoice/Gwen nếu thắng blind test và giải quyết được streaming + quyền |
| CPU/on-device | VieNeu ONNX (int8 nếu có VNNI), Supertonic 3, Kokoro vi, VieNeu Nano |
| MCU | sanoTTS (GPL-3.0) |
| Phủ ngôn ngữ cực rộng | OmniVoice, Higgs, Fish (đều non-commercial) |

**Không nên bắt đầu production bằng việc tự huấn luyện một multilingual foundation model** khi đã có baseline tiếng Việt triển khai được. Chỉ fine-tune (LoRA của VieNeu hoặc VoxCPM2) sau khi đã xác định được failure case cụ thể và có quyền dữ liệu (**Synthesis**).

---

## 6. Frontend tiếng Việt: G2P, phonemizer và normalizer

Đây là tầng quyết định đọc đúng thanh, số và tên riêng. Hiện trạng trong wiki:

| Thành phần | Loại | Trạng thái với tiếng Việt |
|---|---|---|
| `sea-g2p` | G2P tích hợp của VieNeu v3 Turbo | Có; giữ notice riêng khi redistribute. Có một lỗi được report thứ cấp (`chánh` → `tránh`). |
| `vig2p` | G2P tích hợp của Kokoro Vietnamese | Có theo README; package và phoneme inventory chưa được inspect. |
| [eSpeak NG](../wiki/espeak-ng.md) | Formant TTS và front-end phoneme | Tuyên bố hơn 100 ngôn ngữ; danh sách chưa được capture nên **độ phủ vi chưa xác lập**. sanoTTS dùng nó làm phonemizer (gợi ý có vi, **Synthesis**). GPL-3.0-or-later. |
| [Phonemizer](../wiki/phonemizer.md) | Wrapper (backend espeak, espeak-mbrola, festival, segments) | Chưa xác lập backend nào hỗ trợ vi. GPL-3.0-or-later. |
| [Misaki](../wiki/misaki-language-frontends.md) | G2P của Kokoro | **Không có module vi**, chỉ có một link credit tới Viphoneme. |
| StyleTTS 2 PL-BERT đa ngôn ngữ | Text encoder cho StyleTTS 2 | README nói phủ 14 ngôn ngữ; wiki không ghi vi có trong đó hay không. |
| [VietNormalizer](../wiki/vietnormalizer.md) | Normalizer theo luật, viết → đọc | Có; MIT; 19 bước; hơn 17K mục từ điển CSV; khoảng 0.6 ms/lần gọi (không ghi phần cứng); output lowercase; có mâu thuẫn ví dụ transliteration (`database` → `đa-ta-bâi` hay `đa-ta-bê`). |
| [ViSoNorm](../wiki/visonorm-visobert-normalizer.md) | Normalizer neural, không chuẩn → chuẩn | Có; cần `trust_remote_code`; không có license, benchmark hay latency; confidence dao động (ví dụ 0.7056 khi phục hồi dấu). |

**Hệ quả thiết kế (Synthesis):**

- Ưu tiên các backend có G2P tiếng Việt **tích hợp và đã được tác giả kiểm thử cùng model** (VieNeu, Kokoro-vi). Đừng thay G2P của một model bằng eSpeak NG hay phonemizer khi chưa xác lập chúng hỗ trợ vi.
- Chuỗi normalizer đề xuất: (tùy chọn) ViSoNorm cho text kiểu chat hoặc thiếu dấu → **VietNormalizer** sang dạng đọc → **lexicon riêng cho từng backend**. Lý do cần lexicon riêng: cách phiên âm từ tiếng Anh là quy ước của thư viện normalizer, không phải của model TTS. VieNeu đọc được một phần code-switch, nên có thể tắt transliteration (`enable_transliteration=False`) và chỉ giữ thay thế theo từ điển.
- VietNormalizer lowercase output và bỏ emoji/URL. Cần kiểm tra xem điều này có làm mất tín hiệu prosody mà TTS dùng hay không. Giữ dấu câu.
- Cả G-OmniVoice lẫn Gwen đều khuyến nghị normalize và chia chunk trước khi gọi model, nhưng repo của chúng không kèm normalizer.

---

## 7. Phân tầng và lựa chọn

### 7.1. Shortlist (Synthesis)

| Tầng | Model | Vai trò |
|---|---|---|
| **Baseline** | VieNeu v3 Turbo | Pick số 1, có điều kiện rà license |
| **Challenger GPU (cloning/style)** | VoxCPM2 | A/B về chất lượng nghe và cloning |
| **Challenger CPU** | ZeroTTS, Supertonic 3, Kokoro Vietnamese | A/B on-device, cạnh VieNeu ONNX; ZeroTTS cần kiểm tra voice encoder/consent và rights preset |
| **Challenger GPU streaming** | MOSS-TTS Local v1.5 | A/B khi đã có SGLang-Omni |
| **Accuracy/cloning challenger** | G-OmniVoice, Gwen-TTS 0.6B | Chỉ nghe thử; cần giải quyết streaming + quyền |
| **Expressive (NC)** | Higgs TTS 3, Fish S2 Pro | Chỉ khi có license thương mại |
| **Edge fallback** | VieNeu v3 Nano | CPU yếu; chấp nhận chất lượng thấp hơn, nhất là code-switch |
| **MCU** | sanoTTS | Thử nghiệm siêu nhỏ, GPL-3.0 |
| **Nghiên cứu** | Audio8 Realistic, MOSS flagship, dots.tts, LGTM, OmniVoice, F5-TTS Vietnamese, KhanhTTS, Qwen3-TTS 1.7B Vietnamese | Chưa được chứng minh sẵn sàng production |

**Nguồn primary mới hơn bản trước:** [F5-TTS Vietnamese](../wiki/f5-tts-vietnamese.md) có license NC và ví dụ CLI chưa hoàn chỉnh; [KhanhTTS](../wiki/khanhtts-omnivoice.md) có card vi/en, 24 kHz, nhưng lineage base CC-BY-NC chưa giải quyết; [Qwen3-TTS 1.7B Vietnamese](../wiki/qwen3-tts-12hz-1.7b-vietnamese.md) có 30 preset và ví dụ non-streaming, chưa có benchmark. Chúng chưa chứng minh realtime. **Chỉ là pointer thứ cấp:** viXTTS và ShiniChien Qwen3-TTS-VN chưa được rà lại trong lần cập nhật này. VieNeu v4 là API proprietary, chưa có số liệu chất lượng, TTFA, SLA hay giá. Các cloud TTS ngoài catalog chưa được khảo sát.

### 7.2. Vì sao VieNeu được chọn làm baseline?

Lý do là **bằng chứng phù hợp với triển khai**, không phải MOS vượt trội (**Synthesis**):

1. **Chuyên tiếng Việt từ frontend:** `sea-g2p`, dữ liệu vi/en, preset theo vùng miền, code-switching.
2. **Số đo streaming có điều kiện cụ thể và có giải thích cơ chế:** mục 8.5 tóm tắt.
3. **Đường vận hành đầy đủ:** SDK `infer_stream`, server `apps/openai_speech.py`, Docker profile `api-gpu`/`api-cpu` có healthcheck, `VIENEU_MAX_STREAMS`, hàng đợi có giới hạn, 429 kèm `Retry-After`.
4. **CPU và GPU dùng chung một API.**

### 7.3. Khi nào chuyển sang challenger? (Synthesis)

| Tình huống | Hướng xử lý |
|---|---|
| VieNeu không đạt chất lượng nghe, hoặc cần clone tốt hơn, và có GPU từ khoảng 8 GB | **VoxCPM2** nếu vẫn đạt SLO TTFA/RTF. Phải tự viết API adapter. |
| Chỉ có CPU, hoặc on-device | **VieNeu ONNX** trước (int8 nếu CPU có VNNI), A/B với **ZeroTTS**, **Supertonic 3** và **Kokoro vi**. Dùng **Nano** cho CPU yếu. |
| Đã có SGLang-Omni | Thử **MOSS Local v1.5**. |
| Cần cảm xúc mạnh và inline tag, có ngân sách license | **Higgs TTS 3** hoặc **Fish S2 Pro**, sau khi qua test tiếng Việt. |
| License thương mại phải sạch ngay | **VoxCPM2** (Apache-2.0) hoặc **MOSS Local** (Apache theo card), cho tới khi mâu thuẫn license của VieNeu được giải quyết. |
| Blind test cho thấy G-OmniVoice hoặc Gwen thắng rõ | Chỉ chuyển sau khi đã: (a) có đường chunk theo mệnh đề và đo TTFA, (b) rà xong lineage (G-OmniVoice) hoặc quyền dữ liệu (Gwen). |
| MCU | **sanoTTS**, nếu chấp nhận GPL-3.0 và chất lượng vi chưa được chấm. |

---

## 8. Thiết kế hệ thống TTS realtime

Phần này là **Synthesis**: kiến trúc được ghép từ các trang pipeline và tài liệu vận hành của VieNeu. Kiến trúc chưa được triển khai và chưa được test.

### 8.1. Vị trí của TTS trong vòng hội thoại

```text
LLM token stream (generation_id)
  → [1] Clause chunker
  → [2] (tùy chọn) ViSoNorm → VietNormalizer → lexicon theo backend
  → [3] TTS router / backend adapter  ──→  TTS service (VieNeu | VoxCPM2 | MOSS | ONNX ...)
  → [4] Audio stream (metadata + chunks, sequence)
  → [5] Bounded client playback queue (AudioWorklet, pre-buffer 150–300 ms) → loa
         ↑ audio.played(offset)                       ↓
  ← barge-in: generation_id++ → cancel LLM + đóng request TTS → flush queues → lưu phần đã phát
```

Nguyên tắc:

- Tách **model**, **runtime**, **API server**, **streaming policy** và **orchestration** thành các tầng riêng.
- Mỗi backend khai báo rõ sample rate, dtype, số kênh, kiểu framing và khả năng cancellation.
- Đổi backend chỉ là thay URL và adapter, không sửa logic hội thoại.

### 8.2. Clause chunker

Không gửi từng token, cũng không chờ LLM trả lời xong. Quy tắc khởi điểm do AI report đề xuất (**Reported**, cần tune):

- Flush khi gặp `. ? ! … ; :` hoặc xuống dòng.
- **Chunk đầu tiên** được cắt ở dấu phẩy khi đã có khoảng 25 ký tự trở lên, để giảm TTFA.
- Mảnh ngắn hơn 8 ký tự thì gộp vào câu sau.
- Không cắt giữa một số, ngày, viết tắt hay tên riêng đang viết dở (ví dụ `1.250.` khi LLM chưa sinh `000đ`).

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

Ghi chú:

- Server VieNeu tự chia `input` (tối đa 20.000 ký tự) thành các đoạn không vượt quá `max_chars` (mặc định 256, cho phép 64–512) tại ranh giới câu (**Reported**). Clause chunker phía gateway vẫn cần thiết, vì nó quyết định **khi nào** gửi request đầu tiên.
- Chunk đầu ngắn giúp có tiếng sớm nhưng prosody ở ranh giới có thể gãy. Cần A/B riêng.

### 8.3. Normalizer và lexicon

Tách **display text** (hiện cho người dùng) khỏi **spoken text** (gửi cho TTS).

| Loại | Ví dụ | Spoken form (theo VietNormalizer hoặc quy ước đề xuất) |
|---|---|---|
| Tiền | `50.000đ`, `1.250.000đ` | "năm mươi nghìn đồng", "một triệu hai trăm năm mươi nghìn đồng" |
| Số điện thoại | `0912 345 678` | đọc từng chữ số |
| Thập phân / % | `6,5%`, `3-5%` | "sáu phẩy năm phần trăm", "ba đến năm phần trăm" |
| Ngày / giờ | `25/12/2023, lúc 14:30`, `25-26/12` | đọc ngày/tháng/năm, "mười bốn giờ ba mươi phút"; khoảng ngày đọc là "hai mươi lăm đến hai mươi sáu tháng mười hai" |
| Thứ | `thứ 2` | "thứ hai" |
| Đơn vị | `120km/h`, `500m2` | "một trăm hai mươi ki-lô-mét trên giờ", "năm trăm mét vuông" |
| Viết tắt | `TV`, `AI`, `TP.HCM`, `UBND` | "ti vi", "trí tuệ nhân tạo"; TP.HCM/UBND cần có trong từ điển |
| Từ ngoại | `container`, `Singapore` | "công-tê-nơ", "xin-ga-po"; giữ nguyên tiếng Anh nếu backend đọc được |
| Ký hiệu | `&`, `@` | "và", "a còng" |
| Tên riêng / thuật ngữ | `chánh văn phòng` | substitution dictionary nếu G2P đọc sai |

Các yêu cầu khác:

- Chuẩn hóa Unicode NFC.
- Loại bỏ markdown, emoji, bảng, URL theo một spoken policy.
- Giữ dấu câu.
- Ràng buộc phía LLM: system prompt yêu cầu câu ngắn, không markdown/emoji/bảng/URL (**Reported**).
- **Bắt buộc có bộ regression riêng**, vì VietNormalizer chưa được chạy hay kiểm chứng trong wiki (ngày tháng mơ hồ, cách đọc số theo vùng miền, tên riêng).

### 8.4. Hợp đồng backend adapter

```text
synthesize_stream(spoken_text, voice_id, generation_id, deadline) -> AsyncIterator[AudioChunk]
cancel(generation_id)
describe() -> { sample_rate, dtype, channels, framing, supports_cancel, max_streams }
```

Khác biệt đã biết giữa các backend (**Reported**):

| Backend | Định dạng ra |
|---|---|
| VieNeu SDK | `np.float32`, 48 kHz, theo chunk |
| VieNeu HTTP | `pcm` (s16le mono, không header) hoặc `wav` (header với độ dài "unknown"); chunked hoặc SSE (`speech.audio.delta` chứa base64 PCM, kết thúc bằng `speech.audio.done`). `sample_rate` có thể là 48000/24000/16000/8000, resample theo chunk bằng soxr. `mp3`/`opus` trả về 400. |
| VieNeu Nano | 24 kHz, từng chunk đã hoàn chỉnh |
| ZeroTTS | float32 `(1, n)`, 48 kHz theo ví dụ streaming; cancellation chưa xác lập |
| Audio8 Realistic | 44.1 kHz codec; ví dụ SGLang được xác nhận non-streaming, framing streaming chưa xác lập |
| MOSS Local (SGLang) | PCM 48 kHz; codec native stereo nhưng ví dụ dùng mono, phải xác nhận số kênh |
| Higgs | SSE chứa WAV base64, không phải raw PCM |
| G-OmniVoice / OmniVoice | full waveform 24 kHz |
| Gwen-TTS | full waveform; sample rate do `qwen-tts` trả về |
| sanoTTS vi | 22.05 kHz |
| LGTM | 44.1 kHz mono |
| Qwen3-TTS (tham chiếu) | 24 kHz |

Chi tiết tích hợp VieNeu (**Reported**):

- Server VieNeu **bỏ qua** `speed` và `instructions` (có header `X-VieNeu-Ignored` báo điều này). Muốn đổi tốc độ phải làm ở nơi khác.
- Pipecat, LiveKit Agents và Vercel AI SDK dùng plugin OpenAI TTS: đổi `base_url`, đặt `response_format="pcm"`, rồi thêm `sample_rate: 24000` vào body nếu framework mặc định 24 kHz (hoặc chỉnh framework sang 48 kHz).
- Watermark Perth bật mặc định (`VIENEU_WATERMARK=1`), áp dụng theo chunk.
- Mặc định server chỉ bind `127.0.0.1`. Docker profile đặt `HOST=0.0.0.0`, nên khi đó phải đặt `VIENEU_API_KEY`.

Một route "OpenAI-compatible" **không** đảm bảo schema hay cách chia chunk giống nhau giữa các server. Client phải biết sample rate của từng backend. Không đổi giọng giữa chừng một utterance; nếu backend lỗi, retry ở mệnh đề mới.

### 8.5. Concurrency, backpressure và warmup (theo tài liệu streaming của VieNeu)

**Cơ chế GPU (Reported):** một CUDA graph chứa B slot (`max_streams`) và continuous batching. Cứ mỗi 4 frame, toàn bộ stream đi qua **một lần gọi codec dùng chung**. Chi phí lần gọi này là khoảng 65 ms cộng khoảng 2.5 ms cho **mỗi slot được dự trữ**, kể cả slot đang trống. Hệ quả: đặt `max_streams` dư thì mọi request đều chậm đi.

| `max_streams` | 1 stream: TTFA / RTF | Đầy tải: TTFA median (max) / RTF | VRAM idle / peak |
|---|---|---|---|
| 8 | 89 ms / 0.39 | 8 stream: 162 ms / 0.45 | 0.64 / 0.72 GB |
| 16 (mặc định) | 115 ms / 0.49 | 16 stream: 185 (339) ms / 0.59 | 0.91 / 1.10 GB |
| 32 | 141 ms / 0.70 | 32 stream: 456 (629) ms / 0.93; lead âm từ 24 stream | 1.45 / 1.82 GB |

Qua HTTP trên cùng máy (**Reported**):

- 1 request: 106 ms (`pcm`), 99 ms (`sse`).
- 16 client đồng thời: 197 ms (max 336).
- 40 client với 16 slot + 16 hàng đợi: 32 request thành công, 8 request nhận 429; request phải xếp hàng có TTFA 1.5–3 s.

Thêm: TTFA max cao hơn nhiều so với median (339 so với 185) là do prefill dồn lại khi mọi request bắt đầu cùng lúc. Traffic thực tế rải đều gần median hơn: khoảng 135 ms ở mức 16 stream.

**CPU (Reported):**

- fp32: **đúng 1 stream** (RTF 0.55–0.61; 2 stream đồng thời lên RTF 1.19 và cả hai bị giật).
- int8: **2 stream** trên 6 core (RTF khoảng 0.65 mỗi stream), nhưng cần CPU có **VNNI** (Cascade Lake, Ice Lake, Alder Lake, Zen 4). Không có VNNI thì audio bị méo.
- Laptop 4 core: TTFA fp32 khoảng 400–600 ms, int8 khoảng 200–300 ms.
- Muốn thêm stream mà không có GPU: chạy nhiều container pin bằng `--cpuset-cpus`.

**GPU nguội (Reported):**

- Sau khoảng 2 s idle, driver hạ GPU về trạng thái tiết kiệm điện. Request tiếp theo chậm thêm 100–300 ms (đo được: 118 ms khi nóng, 403 ms sau 8 s idle).
- Giữ GPU nóng từ trong process **không hiệu quả**. Cách khắc phục nằm ở host: `nvidia-smi -lgc 1500,2100`, hoặc trên Windows chọn chế độ "Prefer maximum performance".

**Quy tắc vận hành (Synthesis từ các điểm Reported trên):**

- **Một process sở hữu model** (một uvicorn worker). Scale out bằng cách chạy nhiều container, mỗi container một GPU.
- Đặt `max_streams` bằng số stream **đồng thời** thực sự cần. Stream không phải là user: một user voice chat chỉ giữ stream khoảng 20–35% thời gian, nên 16 stream tương ứng khoảng 45–80 user đang hoạt động.
- `VIENEU_QUEUE` và `VIENEU_QUEUE_TIMEOUT` (mặc định 10 s) quyết định khi nào trả 429. Gateway cần có chiến lược xử lý 429: retry, câu đệm, hoặc thông báo.
- **Warmup:** server tự synthesize một câu ngắn khi khởi động (khoảng 12 s nếu model đã có trong cache). Chỉ gửi traffic khi `/health` trả `ok`. Docker healthcheck có `start_period` 120 s (GPU) hoặc 180 s (CPU).
- `/health` trả 503 khi GPU scheduler chết. Scheduler không tự phục hồi; healthcheck sẽ restart container.
- **Client pre-buffer** 150–300 ms (GPU) hoặc ít nhất 300 ms (CPU, đúng bằng 4-frame lead-in).
- **Chung GPU với ASR và LLM:** đo TTS **dưới tải chung**. Số VRAM khoảng 1.1 GB ở 16 stream là của harness tác giả; report thứ cấp ước tính 2–3 GB. Chưa ai đo lại.
- Turing/Pascal không có bf16 nên fallback sang fp16, và đường này **chưa được kiểm chứng chất lượng**.
- Các GPU khác (4090, T4, GTX 1650...) chỉ có **ước lượng** của tác giả, không phải số đo. Ví dụ: 4090 khoảng 90–110 ms và 24–32 stream; T4 khoảng 150–220 ms và 8–12 stream.
- **Pin phiên bản và checksum** của SDK, weights, G2P, voicepack và normalizer.

### 8.6. Cancellation và barge-in

Trình tự đề xuất (**Reported** từ trang barge-in):

1. Gắn `generation_id` vào mọi chunk text và audio.
2. Khi người dùng ngắt lời: tăng `generation_id`, cancel stream LLM, **đóng** request TTS (HTTP/WS), xóa các câu đang chờ.
3. Gửi `{"type":"clear"}` để client flush buffer AudioWorklet.
4. Chỉ lưu vào history **phần đã thực sự phát**, kèm tag `[bị ngắt]`; client báo lại `played_sample_offset`.
5. Bỏ mọi chunk đến muộn mang `generation_id` cũ.

Tài liệu streaming của VieNeu nói rằng **đóng response sẽ đóng generator và giải phóng GPU slot ở tick kế tiếp**, và nguồn ghi rằng điều này đã được kiểm tra (**Reported**; wiki chưa reproduce). Với các backend khác (VoxCPM2, MOSS/SGLang, Gwen, G-OmniVoice), wiki chưa có bằng chứng tương ứng.

Cần kiểm chứng (**Synthesis**):

- Đo cả *user nói → hết tiếng bot* và *user nói → giải phóng compute*.
- Backend không hỗ trợ cancel giữa chừng là một **deployment gate**.
- Không có alignment giữa token và audio thì chỉ biết offset theo sample, không biết chính xác những từ nào đã được nghe.

### 8.7. Runtime / đường phục vụ

| Lựa chọn | Phù hợp | Ranh giới bằng chứng |
|---|---|---|
| VieNeu SDK / `apps/openai_speech.py` / Docker `api-gpu`, `api-cpu` | Baseline, từ MVP tới production nhỏ | `docs/streaming.md` và compose **đã compile**; mã nguồn `apps/openai_speech.py`, Dockerfile và client mẫu **chưa inspect** |
| VoxCPM2 Python + service tự viết | Challenger GPU | Chưa inspect tài liệu Nano-vLLM accelerator |
| SGLang-Omni | MOSS Local, Higgs, Fish | Chưa có recipe cho VieNeu/VoxCPM2; cookbook MOSS chưa inspect |
| vLLM-Omni / Faster Qwen3-TTS | Higgs, Qwen3-TTS | Không có vi chính thức; khả năng chạy Gwen là **Unverified** |
| ONNX Runtime service | ZeroTTS, Supertonic 3, Kokoro vi, VieNeu Nano, LGTM | ZeroTTS có API stream được báo; cancellation/concurrency chưa xác lập. ONNX không tự chứng minh realtime. |
| [audio.cpp](../wiki/audio-cpp-framework.md) GGUF | Native C++ | Có community port `vieneu_v3_turbo`, cùng package VoxCPM2, Supertonic-3, MOSS Local v1.5, OmniVoice, Higgs, Fish. Chưa inspect parity/streaming của port VieNeu. |
| [CrispASR](../wiki/crispasr-tts-engines.md) | C++ một binary, `/v1/audio/speech` | Có engine voxcpm2-tts và omnivoice. README ghi mặc định server xử lý tuần tự, không hỗ trợ batched multi-stream. Mọi output có watermark. |
| Pipecat custom `TTSService` / plugin OpenAI | Orchestration | Đổi `base_url` sang VieNeu, `pcm`, `sample_rate` (**Reported**) |
| HF speech-to-speech | MVP nhanh | Đổi TTS mặc định (Qwen3-TTS, không có vi) sang backend OpenAI-compatible trỏ tới VieNeu |

Port C++/GGUF **không thay đổi license** của weights, và việc có port không chứng minh chất lượng hay latency trên máy đích.

---

## 9. Ngân sách độ trễ

TTFA 115 ms của TTS **không** phải voice-to-voice 115 ms. Critical path thực tế:

```text
user ngừng nói → endpoint commit → ASR final → LLM chunk đầu có nghĩa
              → chunker + normalizer → TTS first playable sample → network/jitter + pre-buffer → loa phát
```

Ngân sách tham khảo từ report (**Reported**, chưa đo; không phải target):

| Stage | Ước lượng |
|---|---|
| Network + jitter buffer (WebRTC) | 30–80 ms |
| VAD silence | 200–300 ms |
| Smart Turn | 10–65 ms |
| ASR turn-final | 100–300 ms |
| LLM TTFT + chunk đầu | 150–350 ms |
| Normalizer (VietNormalizer, theo README) | khoảng 0.6 ms |
| **TTS TTFA** | **64–300 ms** (VieNeu: 89–115 ms ở 1 stream trên RTX 3060, cộng 100–300 ms nếu GPU nguội) |
| Client pre-buffer | 150–300 ms (GPU), ≥ 300 ms (CPU) theo khuyến nghị của VieNeu |
| Voice-to-voice | khoảng 0.7–1.2 s |

**Synthesis:**

- Không cộng các phép đo chồng lấp như thể chúng chạy tuần tự. Hãy đo critical path thực.
- Pre-buffer phía client là một khoản trễ thật, thường bị quên khi so sánh TTFA.
- Phần TTS kiểm soát được: độ dài chunk đầu, warmup, khóa clock GPU, `max_streams`, pre-buffer.
- SLO khởi điểm có thể là **TTS TTFA P95 ≤ 250–400 ms** và **RTF P95 ≤ 0.7** dưới tải thực. Đây là SLO đề xuất, chưa phải khả năng đã chứng minh. Tài liệu VieNeu cũng khuyến nghị RTF max nên ≤ 0.7, và giảm `max_streams` nếu `--bench N` cho RTF > 0.8.

---

## 10. Protocol đánh giá và gate chọn model

Đây là protocol đề xuất (**Synthesis**), chưa phải benchmark đã chạy.

### 10.1. Bộ prompt (150–300 câu tiếng Việt)

- Đủ sáu thanh, có cặp tối thiểu về thanh điệu.
- Câu hỏi, câu cảm thán, hội thoại ngắn và dài.
- Tiền, ngày, khoảng ngày, số điện thoại, đơn vị, viết tắt, địa danh, tên riêng.
- Code-switch Anh–Việt (test cả khi bật và tắt transliteration của normalizer).
- Giọng ba miền (preset), và test riêng với một reference đã được phép clone.
- Chunk boundary nhân tạo để test prosody ở ranh giới.
- Regression case đã biết: `chánh`/`tránh`, ví dụ `database` của VietNormalizer, lỗi ngắt nghỉ.
- Lưu cả raw text và normalized spoken text.

### 10.2. Chất lượng

- Blind pairwise preference và MOS/CMOS với 10–20 người nghe Việt. Chấm độ tự nhiên, thanh điệu/phát âm, prosody hội thoại, độ nhất quán giọng.
- ASR round-trip WER/CER **chỉ là proxy**, phải audit thủ công.
- Speaker similarity: có thể dùng embedding của [Resemblyzer](../wiki/resemblyzer.md) làm proxy, nhưng README nói nó tốt nhất với tiếng Anh và chưa có bằng chứng cho tiếng Việt. Không dùng SIM làm tiêu chí duy nhất.
- **Không** chọn model theo Seed-TTS tiếng Anh, theo SIM đơn lẻ, hay theo MOS của vendor. Ví dụ: MOS 7.685 của G-OmniVoice không rõ thang đo và protocol.

### 10.3. Hiệu năng

- Đo normalization → first byte **và** normalization → first audible sample (tính cả pre-buffer).
- Đo queue delay, TTFA P50/P95, cadence giữa các chunk, số lần stall, RTF P95 mỗi request, RAM/VRAM.
- Đo ở trạng thái warm và cold (GPU sau hơn 2 s idle), với concurrency 1/4/8/16, **khi toàn stack ASR + LLM + TTS chạy đồng thời**.
- Với VieNeu: dùng `examples/openai_speech_client.py --bench N` của tác giả làm điểm khởi đầu, rồi đo trong harness của chính mình.
- Test cancellation giữa chunk, disconnect/reconnect, timeout, OOM, 429.

### 10.4. Hợp đồng và quyền

- Contract test: 48k/24k/22.05k/44.1k/sample rate không xác định, mono/stereo, dtype, PCM vs WAV/SSE, sequence tăng đơn điệu. Không phát audio cũ sau cancel.
- Rights: xét riêng license của runtime, weights, voicepack, tokenizer và lineage dữ liệu. Ví dụ: G-OmniVoice có tokenizer Boson và base CC-BY-NC; Gwen có dữ liệu TikTok; VieNeu có mâu thuẫn roadmap/FAQ; sanoTTS là GPL; LGTM không có license.
- Consent cho reference clone. Log không chứa nội dung (content-free).
- Có watermark hay không (VieNeu bật Perth mặc định; CrispASR watermark mọi output), và việc này có phù hợp chính sách sản phẩm không.

### 10.5. Luật quyết định

License và lỗi nghiêm trọng là **hard gate**. Điểm preference chỉ xét sau khi đã qua các gate này.

1. **VieNeu** nếu thắng về khả năng triển khai và đạt ngưỡng chất lượng.
2. **VoxCPM2** nếu cải thiện có ý nghĩa về nghe/cloning mà vẫn đạt SLO.
3. **ZeroTTS**, **Supertonic 3** hoặc **Kokoro vi** nếu footprint CPU, chất lượng, quyền voice và cancellation đạt; ZeroTTS cần xét riêng việc upload reference khi tạo voice.
4. **MOSS Local** nếu có SGLang-Omni và qua được test số kênh, cancellation.
5. **Higgs/Fish** chỉ sau khi qua test chất lượng tiếng Việt **và** có thỏa thuận thương mại.
6. **G-OmniVoice/Gwen** chỉ khi thắng rõ trong blind test **và** giải quyết được streaming (chunk theo mệnh đề, đo TTFA) cùng lineage/quyền dữ liệu.

---

## 11. Lộ trình triển khai đề xuất

| Giai đoạn | Việc chính |
|---|---|
| **1 — MVP** | VieNeu v3 Turbo qua `/v1/audio/speech` (Docker `api-gpu` hoặc `api-cpu`), chạy sau Pipecat hoặc HF speech-to-speech. Làm ngay từ đầu: clause chunker; VietNormalizer + lexicon riêng + bộ regression; adapter khai báo audio format (`pcm`, `sample_rate`); chờ `/health` ok; `max_streams` theo tải (8 nếu ít hơn hoặc bằng 8 stream); khóa clock GPU; `VIENEU_API_KEY` khi bind `0.0.0.0`; `generation_id` + đóng request khi barge-in; client pre-buffer; log latency theo từng turn. |
| **2 — Beta** | A/B VieNeu với VoxCPM2 (GPU), và VieNeu ONNX với ZeroTTS / Supertonic 3 / Kokoro vi (CPU). Nghe thử G-OmniVoice và Gwen song song nhưng tách khỏi quyết định triển khai. Chạy protocol mục 10. Mỗi lần chỉ đổi một thành phần. Tune chunk đầu. Thêm MOSS Local nếu đã dùng SGLang-Omni. |
| **3 — Production** | Tách TTS thành service/GPU pool riêng, quan sát P95, admission control, circuit breaker, healthcheck restart. LoRA cho brand voice (VieNeu: 10–30 phút audio sạch của một speaker, khoảng 6 GB GPU theo tác giả; VoxCPM2: 5–10 phút) sau khi có consent. Chỉ chuyển sang audio.cpp/native sau khi qua gate về parity output và latency. |

---

## 12. Mâu thuẫn và giới hạn còn mở

- **License VieNeu:** FAQ ghi Apache-2.0 và cho phép thương mại; roadmap ghi "on-device, personal use". Chưa giải quyết. Corpus `VieNeu-TTS-10k-ENVI` bị gated. Consent chỉ áp dụng cho preset voice, không áp dụng cho reference do người dùng đưa vào.
- **Số liệu VieNeu:** chỉ RTX 3060 là được đo. Bảng cho GPU khác là ước lượng của tác giả. Mã nguồn `stream.py`, `fused.py`, `onnx_runtime_lite.py` và `apps/openai_speech.py` chưa được inspect; cơ chế được mô tả là tuyên bố của tài liệu.
- **Higgs:** xếp vi vào tier < 5 nhưng không có điểm, dataset hay normalizer riêng cho vi. Con số 617 ms trên H100 là **gửi request → nhận đủ response**, không phải TTFA.
- **Fish:** khoảng 100 ms TTFA đo trên H200, không có protocol.
- **Supertonic 3:** biểu đồ hiệu năng chỉ có dạng ảnh và ảnh không có trong raw.
- **G-OmniVoice:** không có protocol, judge hay uncertainty. Nhãn `VietNeu/v3turbo` không khớp với VieNeu đã compile. Lineage license (base CC-BY-NC, tokenizer Boson) chưa giải quyết.
- **Gwen-TTS:** chưa rõ quy trình crawl, lọc và consent dữ liệu TikTok. Frontmatter ghi `library_name: transformers` nhưng code dùng `qwen_tts`. CLI không truyền `language` vào model; ảnh hưởng tới chất lượng chưa được test.
- **Kokoro Vietnamese:** weights, config, voicepack và `vig2p` chưa được inspect; không có số đo nào. Không suy được gì từ Kokoro-82M hay Kokoro-FastAPI.
- **MOSS Local:** cookbook/config chưa inspect; số kênh thực tế của stream chưa xác nhận. Không gán đường streaming của Local cho flagship 8B.
- **ZeroTTS:** wiki draft; CPU model, protocol benchmark đầy đủ, code và weights chưa được inspect. Encoder không công khai, dịch vụ tạo latent yêu cầu upload; rights preset, cancellation và concurrency cần xác minh. MIT/Apache là mô tả trong README, không phải rà license.
- **Audio8 Realistic:** số vi do vendor báo trên hai bộ test khác nhau; H20 validation non-streaming, chưa có TTFA hay benchmark streaming. Không chuyển tính năng, license hoặc độ phủ ngôn ngữ giữa các bản Audio8.
- **sanoTTS:** voice vi chưa được chấm; số đo MCU là của voice tiếng Anh.
- **Frontend:** độ phủ vi của eSpeak NG và Phonemizer chưa xác lập. VietNormalizer có mâu thuẫn ví dụ transliteration trong README. ViSoNorm không có license.
- **Không có so sánh khớp điều kiện** về MOS, TTFA hay lỗi phát âm tiếng Việt giữa bất kỳ cặp ứng viên nào. Trang selection trong wiki giữ trạng thái `draft` cho tới khi có listening test và đo trên phần cứng đích.
- Đây là snapshot tài liệu trong repo, bản trước đến 2026-10-13 và bổ sung theo git diff đến 2026-10-28; không rà toàn bộ các ingest giữa hai mốc, không phải khảo sát toàn thị trường. Cloud TTS ngoài catalog chưa được khảo sát.

---

## 13. Tài liệu tham chiếu trong wiki

- **Tổng hợp:** [Vietnamese Realtime TTS Selection](../wiki/vietnamese-realtime-tts-selection.md), [TTS Model Survey](../wiki/tts-model-survey.md) (catalog 49 dòng theo survey), [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md), [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md).
- **Baseline VieNeu:** [VieNeu-TTS v3 Turbo](../wiki/vieneu-tts-v3-turbo.md), [Streaming Runtime and Performance](../wiki/vieneu-tts-streaming-runtime.md), [OpenAI-Compatible Speech API](../wiki/vieneu-tts-openai-speech-api.md), [Docker Compose Deployment](../wiki/vieneu-tts-docker-deployment.md).
- **Bổ sung 2026-10-28:** [ZeroTTS](../wiki/zerotts.md), [Audio8 Realistic 0.6B](../wiki/audio8-tts-realistic-0.6b.md), [Audio8 Preview 0.1B](../wiki/audio8-tts-preview-0.1b.md), [Audio8 Preview 0.6B](../wiki/audio8-tts-preview-0.6b.md); thêm [KhanhTTS](../wiki/khanhtts-omnivoice.md), [F5-TTS Vietnamese](../wiki/f5-tts-vietnamese.md), [Qwen3-TTS 1.7B Vietnamese](../wiki/qwen3-tts-12hz-1.7b-vietnamese.md).
- **Model có vi:** [VoxCPM2](../wiki/voxcpm2.md), [Supertonic 3](../wiki/supertonic-3.md), [MOSS-TTS Local v1.5](../wiki/moss-tts-local-transformer-v1-5.md), [MOSS-TTS v1.5](../wiki/moss-tts-v1-5.md), [Higgs TTS 3](../wiki/higgs-tts-3-4b.md), [Fish Audio S2 Pro](../wiki/fish-audio-s2-pro.md), [OmniVoice](../wiki/omnivoice.md), [G-OmniVoice](../wiki/g-omnivoice.md), [Gwen-TTS 0.6B](../wiki/gwen-tts-0.6b.md), [Kokoro Vietnamese](../wiki/kokoro-vietnamese.md), [sanoTTS](../wiki/sanotts.md), [LGTM-TTS](../wiki/lgtm-tts.md), [dots.tts-mf](../wiki/dots-tts-mf.md), [SeamlessM4T v2 Large](../wiki/seamless-m4t-v2-large.md).
- **Lineage / không có vi:** [Qwen3-TTS-12Hz-0.6B-Base](../wiki/qwen3-tts-12hz-0.6b-base.md), [Kokoro-82M](../wiki/kokoro-82m.md), [Kokoro Python Library](../wiki/kokoro-python-library.md), [Kokoro-FastAPI](../wiki/kokoro-fastapi.md), [StyleTTS 2](../wiki/styletts2.md).
- **Frontend và normalizer:** [VietNormalizer](../wiki/vietnormalizer.md), [ViSoNorm](../wiki/visonorm-visobert-normalizer.md), [Misaki Language Frontends](../wiki/misaki-language-frontends.md), [eSpeak NG](../wiki/espeak-ng.md), [Phonemizer Backends](../wiki/phonemizer-backends.md).
- **Đánh giá:** [Resemblyzer](../wiki/resemblyzer.md), [KVoiceWalk](../wiki/kvoicewalk.md).
- **Runtime và pipeline:** [audio.cpp Framework](../wiki/audio-cpp-framework.md), [CrispASR TTS Engines](../wiki/crispasr-tts-engines.md), [SGLang-Omni](../wiki/sglang-omni.md), [So sánh công cụ triển khai speech](../wiki/speech-deployment-tools-comparison.md), [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md).
