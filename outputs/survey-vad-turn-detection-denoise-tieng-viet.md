# Survey: VAD, Turn Detection và Noise Removal / Denoise cho pipeline tiếng Việt

> **Loại tài liệu:** deliverable trong `outputs/`, không phải canonical knowledge. Mọi claim lấy từ các concept đã compile trong `wiki/`; link dẫn về concept để kiểm tra provenance và locator.
> **Ngày lập:** 2026-10-13. **Phạm vi:** VAD, turn detection / endpointing, noise suppression / speech enhancement / denoise. ASR **không** nằm trong phạm vi, trừ khi một model ASR mang sẵn VAD/EOU head (chỉ nhắc để tham chiếu).
> **Phương pháp:** đọc `SCOPE.md`, `wiki/index.md`, 50 dòng đầu `wiki/log.md` (các mục 2026-10-07 → 2026-10-13), toàn bộ concept VAD/turn/denoise và các trang tích hợp liên quan. **Không** mở `raw/`, không fetch upstream, không cài đặt, không chạy inference hay benchmark.
> **Nhãn bằng chứng:** **Reported** (vendor/nguồn tự công bố), **Observed** (đọc tĩnh), **Synthesis** (suy luận của agent từ evidence đã dẫn), **Unverified**. Không có con số nào trong tài liệu này được reproduce.

---

## 1. TL;DR

1. **Chưa có VAD nào trong wiki có số đo riêng cho tiếng Việt.** Mọi so sánh VAD đều là bảng của vendor trên test set của chính họ, và các bảng không dùng chung data/metric. Silero VAD vẫn là default an toàn nhất (MIT, ~2 MB, tài liệu streaming đầy đủ nhất, được hầu hết framework tích hợp). FireRedVAD là ứng viên mạnh nhất *theo bảng vendor* (F1 97.57 vs Silero 95.95 trên FLEURS-VAD-102, test set chưa công bố) và có thêm AED speech/singing/music. Tuy nhiên Stream-VAD của nó **không có metric streaming nào** được công bố.
2. **Turn detection:** [Smart Turn v3.2](../wiki/smart-turn.md) là detector nhỏ (~8M params), license thoáng (BSD-2), duy nhất trong wiki có **benchmark tiếng Việt từ vendor**: accuracy 82.47% (GPU) / 79.38% (CPU), FPR 9.56% / 8.86%, trên 1.004 mẫu. Tiếng Việt cũng là ngôn ngữ **yếu nhất** trong 23 ngôn ngữ của model. Nên luôn có fallback timeout 1.2–1.5 s. Nếu false-interruption > 10% thì cân nhắc Namo (community, có VN build, chỉ có số tác giả tự đo) hoặc fine-tune. TEN Turn Detection và LiveKit **không hỗ trợ tiếng Việt**.
3. **Denoise:** bằng chứng về việc đặt enhancement **trước ASR** đang mâu thuẫn: hai nghiên cứu báo làm *tăng* WER ở mọi cấu hình, một nghiên cứu báo *giảm*. Không có nghiên cứu nào trên tiếng Việt. Thực hành được khuyến nghị: **chỉ denoise nhánh VAD/barge-in**, ASR nhận audio gốc đã qua AEC, rồi A/B ở SNR 0/5/10/20 dB. Model denoise duy nhất có concept riêng là [Facebook Denoiser](../wiki/facebook-denoiser.md), nhưng nó có license **CC-BY-NC** và không có metric chất lượng hay ASR. RNNoise, DeepFilterNet 3, GTCRN… chỉ được nhắc tên qua một AI report thứ cấp.
4. **AEC, speaker lock và duration-gated barge-in** có đòn bẩy lớn hơn denoise trong môi trường ồn (Reported, AI report). Các thành phần này nằm cạnh VAD/turn nên được survey kèm ở §6.

---

## 2. Cập nhật gần đây (từ 50 dòng đầu `wiki/log.md`)

| Ngày | Model / concept | Tầng | Thay đổi chính |
|---|---|---|---|
| 2026-10-13 | [Facebook Denoiser](../wiki/facebook-denoiser.md), [Denoiser Live Streaming](../wiki/denoiser-live-streaming.md) | Denoise | Mới, draft. Causal Demucs waveform enhancer, CC-BY-NC, có RTF CPU, không có PESQ/WER. |
| 2026-10-13 | [CrispASR VAD and Language Identification](../wiki/crispasr-vad-language-id.md) | VAD runtime | Mới. 4 VAD provider: Silero (default), FireRedVAD, MarbleNet, Whisper-VAD. |
| 2026-10-13 | [Resemblyzer](../wiki/resemblyzer.md) | Speaker embedding (liên quan speaker lock) | Mới. Embedding 256 chiều, không có metric hay license. |
| 2026-10-11 | [PulseVAD](../wiki/pulsevad.md) | VAD | Mới. 2.118 params, causal, có C header cho MCU, MIT. |
| 2026-10-11 | [Frame-VAD Multilingual MarbleNet v2.0](../wiki/frame-vad-multilingual-marblenet-v2-0.md) | VAD | Mới. 91.5K params, frame 20 ms, 6 ngôn ngữ, NVIDIA Open Model License. |
| 2026-10-11 | [FireRedVAD](../wiki/firered-vad.md) | VAD + AED | Mới. DFSMN ~0.57–0.59M params, VAD offline + Stream-VAD + AED. |
| 2026-10-08 | [TEN VAD](../wiki/ten-vad.md) | VAD | Mới. Hop 10/16 ms, thư viện ~306 KB, Apache-2.0 "with conditions". |
| 2026-10-08 | [TEN Turn Detection](../wiki/ten-turn-detection.md) | Turn | Mới. Classifier text 3 trạng thái trên Qwen2.5-7B, chỉ en/zh. |
| 2026-10-07 | [Smart Turn v3.2](../wiki/smart-turn.md) | Turn | Mới, có primary capture. Có benchmark tiếng Việt, thay con số thứ cấp cũ. |

**Lưu ý (Synthesis):** synthesis [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md) được viết ngày 2026-10-07, **trước** khi FireRedVAD, MarbleNet, PulseVAD, Facebook Denoiser và CrispASR được ingest. Bảng VAD trong trang đó vì vậy chưa có các ứng viên này. Survey này bổ sung phần còn thiếu.

---

## 3. Phân tầng chức năng

```text
mic → [AEC] → ┬→ [denoise nhẹ, tùy chọn] → VAD (speech presence, frame-level)
              │                               → turn detector (semantic end-of-turn)
              │                               → endpoint owner (commit / reopen / timeout)
              │                               → barge-in gate (duration + speaker lock)
              └→ audio AEC gốc (không enhance) → ASR
```

- **VAD** chỉ trả lời câu hỏi "có tiếng nói không" theo từng frame. Nó không biết người dùng đã nói xong chưa. Mọi VAD trong wiki đều chỉ làm speech presence (Synthesis, từ các concept).
- **Turn detection** quyết định một khoảng lặng có phải là hết lượt hay không. Có ba kiểu: audio/prosody (Smart Turn), text (TEN, LiveKit text), hoặc nhúng trong ASR (Parakeet EOU, Audio8 semantic VAD).
- **Denoise / enhancement** là bước tiền xử lý tín hiệu. Đây là một quyết định riêng cho *từng nhánh*, không áp dụng chung cho cả pipeline (xem §5).

Sơ đồ trên là **Synthesis**, dựa trên [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md) và [Speech Enhancement Before ASR](../wiki/speech-enhancement-before-asr.md).

---

## 4. VAD

### 4.1 Bảng tổng hợp

| Model | Kích thước | Frame / hop | Input | Streaming API | License | Ngôn ngữ / tiếng Việt | Runtime |
|---|---|---|---|---|---|---|---|
| [Silero VAD](../wiki/silero-vad.md) | ~2 MB JIT; nguồn khác ghi 462K–545K params (v5), 309K (v6) | Window cố định 512 samples = 32 ms @16 kHz (256 @8 kHz) từ v5 | 8 / 16 kHz | Có: `VADIterator` stateful, `get_speech_timestamps` | MIT | Train trên corpus "6000+ ngôn ngữ"; **không có số tiếng Việt** | PyTorch, ONNX, C++, ExecuTorch, Web, Rust/Go/Java/C#, OpenVINO, tinygrad, GGUF (CrispASR ~885 KB, NeMo-Speech.cpp) |
| [TEN VAD](../wiki/ten-vad.md) | Thư viện 277–731 KB tùy platform (Linux 306 KB) | Hop 160/256 samples = 10/16 ms | Chỉ 16 kHz | Output per-frame: prob + flag. **Không có** segmenter kiểu `VADIterator` | Apache-2.0 "with additional conditions" (chưa đọc được LICENSE) | Không có bằng chứng tiếng Việt | Prebuilt C lib (Linux/Win/mac/Android/iOS), WASM/JS, Python, Java, Go, ONNX (ORT ≥1.17.1), sherpa-onnx |
| [FireRedVAD](../wiki/firered-vad.md) | ~0.57–0.59M params (2.2 MB fp32), gồm 3 model | Không công bố frame duration (10 ms là giả định, **Unverified**) | 16 kHz mono PCM16 | Có `FireRedStreamVad` (per-frame `is_speech_start/end`), nhưng chỉ có tài liệu cho whole-file `detect_full` | Apache-2.0 (chỉ ghi trên HF card) | Claim "100+ ngôn ngữ"; card chỉ tag en/zh; **không có số tiếng Việt** | PyTorch (`pip install fireredvad`), NCNN runtime (chưa capture), GGUF (CrispASR) |
| [Frame-VAD Multilingual MarbleNet v2.0](../wiki/frame-vad-multilingual-marblenet-v2-0.md) | 91.5K params (~0.37 MB fp32) | 20 ms/frame | 16 kHz mono | Không có tài liệu streaming; chỉ có batch/whole-file | NVIDIA Open Model License (`license: other`) | en, es, fr, de, ru, zh; **không có vi**; card cảnh báo chất lượng có thể giảm với ngôn ngữ ngoài danh sách | NeMo, ONNX (input là feature đã tính sẵn), GGUF (CrispASR 439 KB, audio.cpp) |
| [PulseVAD](../wiki/pulsevad.md) | 2.118 params; ONNX INT8 26.8 KB; weights 2.1 KB; C header 10 KB | Window **200 ms** không chồng lấn, strictly causal | 16 kHz mono, log-mel 64 bin | Có: buffer 3.200 samples rồi gọi `predict_window`; không có recurrent state | MIT | Train trên LibriSpeech (tiếng Anh). Claim "flat" trên các ngôn ngữ Ấn Độ nhưng không có số; **không nhắc tiếng Việt** | ONNX INT8/FP32, TorchScript, C header (Cortex-M/ESP32/STM32), GGUF (audio.cpp `PulseVAD-GGUF`) |
| WebRTC VAD | GMM, pitch-based | — | — | — | — | Chỉ xuất hiện như baseline | RealtimeSTT ([RealtimeSTT](../wiki/realtimestt.md)) |
| FunASR FSMN-VAD | Không rõ | — | — | — | — | Chỉ xuất hiện như baseline trong bảng FireRed, và là `fsmn-vad.gguf` trong [Fun-ASR-Nano GGUF](../wiki/fun-asr-nano-gguf.md) | llama.cpp FunASR runtime |
| Whisper-VAD-EncDec | 22 MB Q4_K | ~1 s/lượt so với ~50 ms của các VAD khác | — | — | — | Train trên ASMR tiếng Nhật; README nói "may not generalise" | CrispASR (thử nghiệm) |

Tất cả các ô là **Reported** theo concept tương ứng. Kích thước Silero có nhiều con số mâu thuẫn, xem §8.

**VAD nhúng trong ASR** (ngoài phạm vi, chỉ để tham chiếu):
- [Parakeet Ultra](../wiki/parakeet-ultra.md): có VAD head trên subsampler để cắt long-form.
- [Audio8 ASR Infinite](../wiki/audio8-asr-infinite.md): có "semantic VAD" 8 lớp, chỉ zh/en.
- NeMo-Speech.cpp: Silero dùng để mask feature trước encoder ([NeMo-Speech.cpp ASR Configuration](../wiki/nemo-speech-asr-configuration.md)).

### 4.2 Benchmark: ai thắng ai, theo bảng của ai

Không có hai concept nào dùng chung một benchmark. Mỗi dòng dưới đây đúng **trong phạm vi** test set của vendor đó.

| Benchmark (chủ nhân) | Dữ liệu | Kết quả chính | Hạn chế |
|---|---|---|---|
| FLEURS-VAD-102 (FireRed) | ~100 file/ngôn ngữ × 102 ngôn ngữ (9.443 file), read speech, gán nhãn tay, **chưa công bố** | F1: FireRed **97.57** > Silero 95.95 > TEN 95.19 > FunASR 90.91 > WebRTC 52.30. False alarm: FireRed 2.69%, Silero 9.41%, TEN 15.47%. Miss rate thấp nhất thuộc FunASR (0.42%) và TEN (2.95%), FireRed 3.62% | Cùng team vừa làm benchmark vừa làm model; không nêu threshold; chỉ đo non-streaming; read speech, không có call hay far-field; không tách số theo ngôn ngữ |
| PulseVAD head-to-head (PulseVAD) | ~82 phút LibriSpeech dev-clean + DEMAND noise + GTZAN music; window 200 ms, threshold sweep | Clean F1: PulseVAD 99.3 > Silero 96.9. Mean F1: Silero **93.6** > PulseVAD 90.1 ≈ kiloVAD ≈ WebRTC 90.0. FAR nhạc: Silero 15.7% < PulseVAD 33.3% | Nhãn train lấy từ output của Silero; ground truth của benchmark không nêu; Silero chạy trong setup do PulseVAD tự dựng |
| AUC held-out (PulseVAD) | 2.000 window/loại | Silero v5 tốt nhất hoặc ngang ở hầu hết các loại; MarbleNet 0.970 clean / 0.910 windy | Phiên bản MarbleNet trong bảng không khớp card v2.0 (xem §8) |
| PR curve + RTF (TEN) | LibriSpeech, GigaSpeech, DNS; PR curve là ảnh, không có số | Claim precision cao hơn Silero và WebRTC; RTF 0.0086 vs Silero 0.0127 (chỉ đo trên **một** CPU); lib nhỏ hơn ~86% | Không có F1 dạng số; claim Silero "chậm vài trăm ms" ở chỗ chuyển speech→non-speech không có protocol |
| NOVA-VAD (cộng đồng, qua AI report) | UrbanSound8K noise | Silero F1 **91.9%** vs TEN 69.2% | Benchmark nhỏ, nguồn thứ cấp |
| ROC-AUC (MarbleNet) | 7 tập diarization-style, chỉ zh/en | 92.27 (AISHELL4) đến 97.59 (VoxConverse-dev), trung bình ≈ 95.65 | Không có baseline nào; chỉ ROC-AUC, không có operating point; có thể trùng train/eval |

**Đọc chéo (Synthesis):**
- Silero và TEN mâu thuẫn trực tiếp: TEN tự claim thắng, trong khi cả benchmark cộng đồng lẫn bảng của FireRed đều xếp Silero trên TEN về F1 và false alarm. Ba nguồn này có protocol khác nhau nên chưa ngã ngũ.
- Lợi thế thật của FireRed trong bảng của chính họ đến từ **false alarm** (2.69% so với 9.41% của Silero), không phải từ miss rate. Với voice agent trong môi trường ồn như TV hay quán café, false alarm chính là thứ gây barge-in giả. Đây là trục đáng A/B nhất.
- PulseVAD rất mạnh trên speech sạch, gần mic, nhưng yếu với nhạc (FAR 33%) và far-field. Granularity 200 ms của nó cũng cộng thêm độ trễ endpoint.

### 4.3 Hỗ trợ tiếng Việt cho VAD

- **Không model nào** trong wiki có metric VAD tách riêng cho tiếng Việt (Observed, qua tất cả concept VAD).
- Bộ FLEURS gốc có 102 ngôn ngữ và, theo kiến thức ngoài wiki, có tiếng Việt. Wiki không ghi số per-language, nên nếu FireRed công bố FLEURS-VAD-102 thì đây là nguồn đáng ingest để lấy số tiếng Việt (**Unverified**).
- Rủi ro riêng cho tiếng Việt (Reported, AI report qua [Silero VAD](../wiki/silero-vad.md)): `speech_pad_ms` 100–200 giúp giữ phụ âm đầu và cuối, vốn quan trọng cho nhận diện thanh điệu. VAD cắt quá sát có thể làm hỏng âm tiết đầu hoặc cuối.
- Silero v6 tự nhận còn yếu với "giọng rất cao" và nhạc cụ giống giọng nói (Reported). Với tiếng Việt cũng cần test giọng nữ cao và TV hoặc nhạc nền.

### 4.4 Chọn VAD theo kịch bản (Synthesis)

| Kịch bản | Chọn đầu | Lý do / điều kiện |
|---|---|---|
| Default server/desktop, voice agent tiếng Việt | **Silero VAD v6.x ONNX** | MIT, tài liệu streaming đầy đủ, mọi framework đều hỗ trợ, có benchmark độc lập nhỏ thuận lợi |
| Nền có nhạc, TV, hát; cần giảm false alarm | **FireRedVAD** (thêm AED) | Phải tự đo Stream-VAD; tự viết hoặc đọc code cho incremental call; tune `speech_threshold` và `min_silence_frame` |
| Browser/mobile, cần hop 10 ms, lib nhỏ | **TEN VAD** | Kiểm tra "additional conditions" của license; tự build segmenter / hysteresis |
| Vi điều khiển, wake-gating, < 30 KB | **PulseVAD** | Chỉ dùng cho near-mic; chấp nhận độ trễ 200 ms; yếu với nhạc |
| Stack NeMo/NVIDIA, front-end cho diarization | **MarbleNet v2.0** | Không có vi; đọc license NVIDIA; ONNX cần tự tái tạo feature extraction |
| Runtime C++ một binary | Silero hoặc FireRed qua CrispASR / NeMo-Speech.cpp; PulseVAD qua audio.cpp | Parity của bản port với bản gốc chưa được kiểm |

---

## 5. Turn detection / endpointing

### 5.1 Bảng tổng hợp

| Detector | Modality | Kích thước | Ngôn ngữ | Tiếng Việt | Latency | License |
|---|---|---|---|---|---|---|
| [Smart Turn v3.2](../wiki/smart-turn.md) (Pipecat) | Audio (prosody), 16 kHz, window 8 s | ~8M params; CPU int8 8 MB / GPU fp32 32 MB | 23 | **Có số vendor:** GPU acc 82.47%, P 0.814, R 0.840, F1 0.826, FPR 9.56%, FNR 7.97%; CPU acc 79.38%, F1 0.786, FPR 8.86%, FNR 11.75% (n = 1.004) | 10 ms trên một số CPU; < 100 ms trên cloud; ~65 ms trên Pipecat Cloud | BSD-2; mở weights, data và script train |
| [TEN Turn Detection](../wiki/ten-turn-detection.md) | Text (transcript) → `finished` / `unfinished` / `wait` | Qwen2.5-7B (~15 GB bf16, ước tính) | en, zh | **Không** | Không công bố | Apache-2.0 trên HF vs "with additional restrictions" trên GitHub (chưa giải quyết) |
| LiveKit Turn Detector (text, multilingual) | Text | < 500 MB RAM | 14 | **Không** | ~25 ms | License riêng của LiveKit |
| LiveKit Turn Detector v1 (audio) | Audio | — | 14 | **Không** | — | Free trên LiveKit Cloud; khả năng self-host chưa được kiểm |
| Namo Turn Detector (`dangvansam`) | — | ~200 MB (bản VN) | VN + đa ngữ | **Có**, nhưng chỉ do tác giả tự đo | 4–36 ms | Plugin LiveKit; không có benchmark độc lập |
| [Parakeet Realtime EOU 120M](../wiki/parakeet-realtime-eou-120m-v1.md) | Token `<EOU>` nằm trong ASR streaming | 120M | Chỉ en | Không | EOU P50 160 / P90 280 / P95 320 ms (audio TTS + 3 s silence) | NVIDIA Open Model License |
| NeMo-Speech.cpp endpointing ([config](../wiki/nemo-speech-asr-configuration.md)) | Token-silence hoặc dựa trên Silero VAD timeline | — | Theo ASR | Theo ASR (ví dụ Nemotron 3.5 có vi-VN) | `stop_history_eou_ms` = 800 | — |
| Silence-only (VAD + timeout) | Acoustic | — | Mọi ngôn ngữ | Mọi ngôn ngữ | = `min_silence` | — |

Nguồn: [Turn Detection Models](../wiki/turn-detection-models.md). Các hàng LiveKit và Namo **chỉ đến từ AI report thứ cấp**, không có primary docs trong `raw/` (Reported).

### 5.2 Nhận xét cho tiếng Việt (Synthesis, trừ chỗ ghi khác)

- Smart Turn mất **~11 điểm accuracy** cho tiếng Việt so với mức chung (82.47 vs 93.71 trên GPU) và ~13 điểm trên CPU (79.38 vs 92.63). Tính trên GPU, khoảng **1/10** lần model báo "hết lượt" xảy ra khi người dùng vẫn đang nói.
- Bản CPU int8 và GPU fp32 cho ra **kiểu lỗi khác nhau** trên tiếng Việt. CPU có FNR cao hơn (11.75%, tức chờ thừa) và FPR thấp hơn (8.86%, ít cắt lời hơn). Nên chọn variant theo lỗi mà sản phẩm ít chịu được hơn.
- Smart Turn **dựa trên audio** nên không phụ thuộc chất lượng ASR. Đây là lợi thế với tiếng Việt, nơi ASR streaming còn yếu. Ngược lại, TEN và LiveKit text cần transcript và không có tiếng Việt.
- Ngoài con số vendor, wiki chưa có detector tiếng Việt nào được đo độc lập. Namo là ứng viên thay thế duy nhất được nêu tên.
- Có hai trường phái điều khiển mâu thuẫn nhau (ghi ở §8):
  - **HF s2s:** `min_silence_ms` 64, speculative reopen 800 ms, Smart Turn chờ incomplete 600 ms, max wait 2 s, turn tracker có reopen/revision.
  - **AI report:** Silero silence 200–300 ms, Smart Turn, fallback 1.2–1.5 s, commit cứng.

### 5.3 Tham số khởi điểm (cần tune, không phải default đã đo)

| Tham số | Giá trị khởi điểm | Nguồn |
|---|---|---|
| Silero `threshold` | 0.5 (0.6–0.7 khi nền rất ồn); HF s2s mặc định 0.6 | AI report; [HF s2s CLI defaults](../wiki/speech-to-speech-cli-and-defaults.md) |
| Silero `min_silence_duration_ms` | 200–300 khi có Smart Turn; 500–800 khi không có semantic detector | AI report; [Cascaded Blueprint](../wiki/cascaded-voice-agent-blueprint.md) |
| `speech_pad_ms` | 100–200 (giữ phụ âm cho thanh điệu); HF s2s mặc định 500 | AI report; HF s2s |
| `min_speech_duration_ms` | 250; HF s2s dùng 384 / continuation 192 | AI report; HF s2s |
| Smart Turn | Gọi sau 200 ms silence (`stop_secs=0.2`), threshold 0.5, cho toàn bộ turn ≤ 8 s | [Smart Turn v3.2](../wiki/smart-turn.md); HF s2s |
| Fallback commit | 1.2–1.5 s silence | [Turn Detection Models](../wiki/turn-detection-models.md) |
| Adaptive threshold | Đo VAD prob và RMS trong 2–3 s đầu; nếu nền > 0.3 thì nâng threshold lên 0.65–0.7 | [Barge-in](../wiki/voice-agent-barge-in-and-echo-handling.md) |
| FireRed Stream-VAD | `speech_threshold` 0.4 (HF card cũ ghi 0.3), `min_silence_frame` 20, `pad_start_frame` 5, `smooth_window_size` 5 | [FireRedVAD](../wiki/firered-vad.md) |
| NeMo-Speech.cpp | VAD masker onset/offset 0.5/0.3, pad 200 ms; EOU 800 ms | [NeMo ASR config](../wiki/nemo-speech-asr-configuration.md) |

---

## 6. Noise removal / denoise / speech enhancement

### 6.1 Model và công cụ đang có trong wiki

| Model / công cụ | Loại | Mức độ có trong wiki | Realtime / latency | License | Evidence chất lượng | Tiếng Việt |
|---|---|---|---|---|---|---|
| [Facebook Denoiser](../wiki/facebook-denoiser.md) (dns48 / dns64 / master64) | Causal waveform enhancer (Demucs encoder-LSTM-decoder) | Concept riêng (draft) | RTF CPU i5 2 GHz: H48 0.8 (1 thread) / 0.6 (4 thread); H64 1.2 / 1.0. Total lag 41.3 ms, stride 16 ms ([Live Streaming](../wiki/denoiser-live-streaming.md)) | **CC-BY-NC 4.0** | **Không có** PESQ/STOI/SI-SDR/DNSMOS/WER trong README | Không |
| RNNoise | Noise suppression nhẹ trên CPU | Chỉ có tên (AI report) | "CPU-light" | — | — | Không |
| DeepFilterNet 2/3 | Noise suppression | Có tên; là flag `audio_enhancement` trong HF s2s (mặc định off, cần `numpy<2`, xung đột Pocket TTS) | — | — | — | Không |
| GTCRN, DTLN | Noise suppression | Chỉ có tên | — | — | — | Không |
| ClearerVoice-Studio (FRCRN, MossFormer2, target-speaker extraction) | Enhancement / TSE | Chỉ có tên | — | — | — | Không |
| Resemble Enhance | Enhancement offline | Chỉ có tên | Offline | — | — | Không |
| Krisp | Noise suppression | Chỉ có tên | — | Closed / thương mại | — | — |
| `noisereduce` + high-pass + compressor; Ultimate Vocal Remover | Front-end do cộng đồng tự ghép | [Community Noisy Call STT](../wiki/community-noisy-call-stt.md) | — | — | Chỉ có giai thoại | Không |
| [SAM Audio GGUF](../wiki/sam-audio-gguf.md) | Tách nguồn theo prompt | Concept riêng | RTX 5090 | SAM license | Một nghiên cứu báo **WER tăng** khi dùng trước Whisper | Không |
| HTDemucs (audio.cpp) | Tách nhạc 6 stem | Catalog | — | MIT | Không phải speech denoise | — |
| Tiện ích denoise / enhancement có sẵn trong [audio.cpp](../wiki/audio-cpp-framework.md) | Utility + tab WebUI (v0.9.0) | Chỉ một dòng mô tả | — | — | — | — |

### 6.2 Denoise trước ASR: bằng chứng mâu thuẫn

Nguồn: [Speech Enhancement Before ASR](../wiki/speech-enhancement-before-asr.md). Cả ba nghiên cứu đều được dẫn **thứ cấp** qua AI report; các paper không có trong `raw/`.

| Nghiên cứu | Enhancer | ASR | Kết quả |
|---|---|---|---|
| "When De-noising Hurts" (arXiv 2512.17562) | MetricGAN+ | Whisper, Parakeet, Gemini Flash 2.0, Parrotlet-a; 500 bản ghi y tế, 9 điều kiện nhiễu | **Tệ hơn ở cả 40/40 cấu hình** (semWER tăng 1.1–46.6 điểm; Whisper @10 dB: 8.82% → 25.83%) |
| Islam et al. (arXiv 2603.04710) | SAM-Audio | Whisper, tiếng Bengali và tiếng Anh | **WER/CER tăng ở mọi cấu hình** (Whisper base EN: 10.53% → 21.66%) |
| Yang, Pandey, Wang (arXiv 2403.06387) | ARN, CrossNet | Backend sạch + Whisper, CHiME-4 | **Tốt hơn** (3.32% simulated, 4.44% real) |

**Đọc (Synthesis):** đây không phải "denoise tốt hay xấu" nói chung. Kết quả phụ thuộc vào cặp enhancer × ASR × domain. ASR lớn hiện đại đã được train với nhiễu, nên artifact của enhancer thường gây hại nhiều hơn phần nhiễu được loại bỏ. Hiện không có nghiên cứu nào trên tiếng Việt.

### 6.3 Thực hành khuyến nghị (Reported, AI report; trừ chỗ ghi khác)

1. **Không denoise nhánh ASR** ở baseline. ASR nhận audio gốc đã qua AEC.
2. **Denoise nhẹ** (RNNoise hoặc DeepFilterNet 3) **chỉ trên nhánh VAD/barge-in** để giảm false trigger.
3. A/B WER/CER tiếng Việt ở SNR 0/5/10/20 dB, có và không có denoise, với nhiễu café, xe máy và TV.
4. Với Facebook Denoiser cụ thể (Synthesis): license NC chặn dùng thương mại. Lag ~41 ms cộng với RTF gần 1 trên CPU yếu sẽ chồng thêm độ trễ vào nhánh VAD và tranh CPU với các thành phần khác. Model này cũng **không xử lý echo**.

---

## 7. Các thành phần cạnh VAD: AEC, speaker lock, barge-in

Nguồn: [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md). Cả hai nguồn đều là LLM-generated, nên mọi tham số dưới đây là giá trị thiết kế chưa đo.

- **AEC:** bắt buộc khi dùng loa ngoài. Các lựa chọn: WebRTC AEC3 qua `getUserMedia({echoCancellation:true})` của trình duyệt, hoặc SpeexDSP. Chiến lược production: AEC ở tầng WebRTC, kết hợp so sánh với audio bot vừa phát (Reported).
- **Speaker lock:** tính cosine giữa embedding ECAPA-TDNN / CAM++ / WeSpeaker / TitaNet của segment mới và embedding của user; bỏ qua segment dưới ~0.5–0.6 (cần calibrate). [Resemblyzer](../wiki/resemblyzer.md) là một encoder 256 chiều có trong wiki, nhưng không có metric hay license (Reported).
- **Barge-in gate:** có hai giá trị mâu thuẫn. ChatGPT đề xuất 100–200 ms speech để ưu tiên độ nhạy. Claude đề xuất threshold 0.7 và ≥ 300–500 ms (server tham chiếu dùng 400 ms) để ưu tiên chống ồn. Tùy chọn thêm: yêu cầu quick ASR ra ≥ 2 từ không trùng câu bot đang phát.
- **Backchannel** "ừ / vâng / ok": AI report đề xuất bỏ qua. Synthesis trong [Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md) **không** mặc định bỏ qua, vì trong một số domain đây là xác nhận quan trọng.
- TEN Turn Detection có trạng thái `wait` ("đừng nói nữa"), nhưng chỉ cho en/zh.

---

## 8. Mâu thuẫn và câu hỏi mở (ghi lại, không chọn phía)

| Chủ đề | Phía A | Phía B | Trang |
|---|---|---|---|
| TEN vs Silero | TEN tự claim precision cao hơn, RTF thấp hơn 32% | NOVA-VAD: Silero F1 91.9 vs TEN 69.2; bảng FireRed: Silero 95.95 > TEN 95.19 | [Silero](../wiki/silero-vad.md), [TEN](../wiki/ten-vad.md) |
| Kích thước Silero | ~2 MB JIT / 2.16–2.22 MB | PulseVAD ghi lúc 545K params, lúc 462.594 params (2.328 KB), và v6 309K (~1.2 MB) | [PulseVAD](../wiki/pulsevad.md) |
| MarbleNet | Card v2.0: 91.5K, frame 20 ms, "ready for commercial use" | PulseVAD: 91K, 630 ms latency, "non-commercial" | [MarbleNet](../wiki/frame-vad-multilingual-marblenet-v2-0.md) |
| CLI FireRed | GitHub: `speech_threshold` 0.4, `min_silence_frame` 20 | HF card: 0.3 / 10 | [FireRedVAD](../wiki/firered-vad.md) |
| Smart Turn tiếng Việt | AI report: 81.27% / FP 14.84% / FN 3.88% | Primary v3.2: 82.47 / 9.56 / 7.97 (GPU) | [Turn Detection Models](../wiki/turn-detection-models.md) |
| Dataset Smart Turn | GitHub: data v3.2 | HF card: data v3.1 | [Smart Turn](../wiki/smart-turn.md) |
| License TEN Turn | HF: Apache-2.0 | GitHub: "with additional restrictions" | [TEN Turn](../wiki/ten-turn-detection.md) |
| Denoise trước ASR | 2 nghiên cứu: hại | 1 nghiên cứu: giúp | [Speech Enhancement](../wiki/speech-enhancement-before-asr.md) |
| Endpoint policy | HF s2s: 64 ms + reopen 800 ms + max wait 2 s | Report: 200–300 ms + fallback 1.2–1.5 s | [Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md) |
| Facebook Denoiser STFT loss | Paper: 0.5 | README: 0.1 cho các model causal | [Facebook Denoiser](../wiki/facebook-denoiser.md) |

---

## 9. Ma trận tích hợp: framework/runtime nào hỗ trợ gì

| Framework / runtime | VAD | Turn | Denoise | Trang |
|---|---|---|---|---|
| HF speech-to-speech | Silero (mặc định, thresh 0.6), FireRed Stream-VAD (`fireredvad`) | Smart Turn v3.2 CPU (mặc định bật) + turn tracker | DeepFilterNet (`audio_enhancement`, mặc định off) | [Pipeline](../wiki/speech-to-speech-pipeline.md), [CLI](../wiki/speech-to-speech-cli-and-defaults.md) |
| Pipecat | `SileroVADAnalyzer` | `LocalSmartTurnAnalyzerV3` | — | [Voice Agent Frameworks](../wiki/voice-agent-frameworks.md) |
| TEN Framework | TEN VAD | TEN Turn Detection | — | [Frameworks](../wiki/voice-agent-frameworks.md) |
| LiveKit Agents | — | LiveKit turn detectors (không có vi), plugin Namo | — | [Turn Detection Models](../wiki/turn-detection-models.md) |
| CrispASR | Silero (mặc định), FireRed, MarbleNet, Whisper-VAD | — | — | [CrispASR VAD/LID](../wiki/crispasr-vad-language-id.md) |
| audio.cpp | Silero, MarbleNet, `PulseVAD-GGUF` | `Smart-Turn-v3-GGUF` (F32, BSD-2) | Tiện ích denoise; SAM Audio, HTDemucs | [audio.cpp](../wiki/audio-cpp-framework.md), [GGUF packages](../wiki/audio-cpp-gguf-packages.md) |
| NeMo-Speech.cpp | Silero v6.2 GGUF (masking + VAD-driven EOU) | Endpointing token-silence / VAD, 800 ms | — | [ASR config](../wiki/nemo-speech-asr-configuration.md) |
| sherpa-onnx | TEN VAD (theo news của TEN) | — | — | [TEN VAD](../wiki/ten-vad.md) |
| faster-whisper | Silero `vad_filter` (mặc định cắt silence > 2 s) | — | — | [Faster-Whisper](../wiki/faster-whisper.md), [Hallucination](../wiki/whisper-hallucination-mitigation.md) |
| RealtimeSTT / RealtimeVoiceChat | WebRTC + Silero | `turndetect.py` dựa trên pause | — | [RealtimeSTT](../wiki/realtimestt.md), [RealtimeVoiceChat](../wiki/realtime-voice-chat.md) |
| WhisperLiveKit | VAC/VAD (không nên tắt) | Pause segmentation 5 s | — | [WhisperLiveKit](../wiki/whisperlivekit.md) |
| Confucius4-R2T2 server | FireRed Stream-VAD | — | — | [Confucius4-R2T2](../wiki/confucius4-r2t2.md) |
| Fun-ASR-Nano GGUF | `fsmn-vad.gguf` | — | — | [Fun-ASR-Nano GGUF](../wiki/fun-asr-nano-gguf.md) |

---

## 10. Khuyến nghị cho pipeline tiếng Việt (Synthesis, chưa đo)

**Baseline:**

```text
Client AEC (WebRTC AEC3) → Silero VAD v6 ONNX (512-sample, per-session VADIterator)
  → Smart Turn v3.2 (GPU fp32 nếu ưu tiên ít chờ thừa; CPU int8 nếu ưu tiên ít cắt lời) + fallback 1.2–1.5 s
  → một endpoint owner duy nhất (commit / reopen)
  → barge-in: threshold 0.7 + ≥300–500 ms + speaker lock (ECAPA/CAM++) khi bot đang nói
Denoise: tắt ở baseline; nếu bật thì RNNoise/DeepFilterNet 3 CHỈ trên nhánh VAD/barge-in
```

**A/B tiếp theo, mỗi lần đổi một thành phần:**
1. Silero vs **FireRed Stream-VAD** trên audio tiếng Việt có TV/nhạc nền. Metric chính: false alarm và barge-in giả.
2. Smart Turn v3.2 vs **Namo VN** vs silence-only (500–800 ms). Metric chính: false-cutoff và độ trễ commit.
3. Nhánh VAD có và không có denoise (RNNoise vs DeepFilterNet 3). Nhánh ASR có và không có denoise ở SNR 0/5/10/20 dB.
4. TEN VAD chỉ thử khi chạy trên browser/mobile cần hop 10 ms. PulseVAD chỉ dùng cho thiết bị MCU near-mic.

**Bộ test tiếng Việt tối thiểu:**
- Giọng Bắc / Trung / Nam.
- Pause dài giữa câu (đang nghĩ, đang đọc số điện thoại hay địa chỉ).
- "không / dừng / thôi" ngắn có chủ đích; backchannel "ừ / vâng".
- Ho, gõ phím, TV, nhạc có lời tiếng Việt, xe máy.
- Echo của bot; user nói đè lên bot.
- 8 kHz call vs 16 kHz mic; giọng nữ cao.

Metric cần đo: VAD false alarm và miss; turn false-cutoff và missed-end; false-interrupt; stop-audible latency; P50/P95 latency từ `vad_end` đến commit. Ngưỡng thay Smart Turn: false-interruption tiếng Việt > 10% (Reported).

---

## 11. Khoảng trống: nguồn nên ingest tiếp

| Ưu tiên | Nguồn | Lý do |
|---|---|---|
| Cao | Namo Turn Detector (README/card `dangvansam`) | Ứng viên turn detector tiếng Việt duy nhất ngoài Smart Turn; hiện chỉ có dẫn thứ cấp |
| Cao | DeepFilterNet 3, RNNoise, GTCRN (README/paper) | Là các denoiser được khuyến nghị cho nhánh VAD nhưng chưa có concept nào |
| Cao | FLEURS-VAD-102 khi được công bố; FireRedASR2S tech report (arXiv 2603.10420) | Có thể chứa số VAD tiếng Việt và metric Stream-VAD |
| Trung bình | LiveKit turn detector docs; Silero Quality/Performance Metrics wiki | Hiện chỉ có dẫn qua AI report hoặc link chưa fetch |
| Trung bình | ClearerVoice-Studio (FRCRN, MossFormer2, TSE); WebRTC AEC3 / SpeexDSP | Enhancement và target-speaker extraction; AEC là thành phần có đòn bẩy cao nhất |
| Trung bình | Ba paper denoise-vs-ASR (2512.17562, 2603.04710, 2403.06387) | Thay dẫn thứ cấp bằng primary |
| Thấp | Smart Turn v3.0/v3.1 benchmarks; FunASR FSMN-VAD | Giải mâu thuẫn số liệu; baseline |

---

## 12. Giới hạn của survey này

- Chỉ dùng wiki đã compile, không mở `raw/`. Mọi số liệu đều kế thừa nhãn evidence và locator từ concept nguồn.
- Rất nhiều claim (LiveKit, Namo, RNNoise/DeepFilterNet, tham số Silero streaming, ba nghiên cứu denoise, barge-in) đến từ **AI-generated report thứ cấp** (`raw/Claude-pipeline-recommend.md`, `raw/ChatGPT-pipeline-recommend.md`).
- Sự vắng mặt của một model trong wiki nghĩa là "chưa compile hoặc chưa được retrieve", không có nghĩa là model đó không tồn tại hay kém.
- Diarization (Sortformer, Nemotron 3 Diarization, DiarizationLM) và LID nằm ngoài phạm vi yêu cầu, nên không được survey.
- Survey này chưa được file vào `wiki/` và chưa có log entry. Nếu muốn giữ làm canonical, có thể file thành `type: Synthesis` qua `wiki-ingest`, đồng thời cập nhật bảng VAD/denoise trong [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md).
