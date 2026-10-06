# Voice chat realtime mã nguồn mở trong môi trường ồn: khảo sát mô hình (10/2026) và cách ghép Silero VAD + Whisper + Qwen3 + Qwen3-TTS

Ghép Silero VAD + Whisper + Qwen3 + Qwen3-TTS thành một voice chat realtime là làm được, nhưng sản phẩm cho người Việt sẽ vướng ở khâu TTS: Qwen3-TTS bản chính thức chỉ hỗ trợ 10 ngôn ngữ và **không có tiếng Việt**. Vì vậy, với tiếng Việt nên dùng VieNeu-TTS v3 Turbo, hoặc một bản Qwen3-TTS fine-tune tiếng Việt từ cộng đồng (chưa được kiểm chứng). Qwen3-TTS nên giữ lại cho tiếng Anh, tiếng Trung và các ngôn ngữ nó hỗ trợ. Kiến trúc nên dựng sao cho đổi TTS chỉ là đổi endpoint `/v1/audio/speech`.

## TL;DR

- **Stack khuyến nghị (máy 1 GPU 24GB):**
  - Lọc ồn chỉ cho nhánh VAD/barge-in; ASR vẫn nghe audio gốc đã qua AEC.
  - VAD: Silero VAD v6.2 (thay thẳng cho v5, cùng API).
  - Turn detection: Smart Turn v3.x (có tiếng Việt).
  - STT: faster-whisper large-v3-turbo với `language="vi"`, bật bộ tham số chống hallucination và lọc câu rác.
  - LLM: Qwen3-8B (hoặc Qwen3.5-9B) tắt thinking, serve bằng vLLM, stream theo câu.
  - TTS: VieNeu-TTS v3 Turbo cho tiếng Việt, Qwen3-TTS 12Hz qua vLLM-Omni (stream PCM/WebSocket) cho ngôn ngữ khác.
  - Framework: Pipecat. Nó có sẵn Silero VAD, faster-whisper, Smart Turn và LLM OpenAI-compatible; riêng Qwen3-TTS phải tự viết service.
- **Những thông tin đã kiểm tra lại đến 10/2026:**
  - Silero đã ra v6 (25/08/2025), hãng công bố "16% less errors on noisy real-life data". Bản mới nhất là v6.2.1.
  - Qwen3-TTS mở mã từ 22/01/2026, license Apache-2.0, có hai cỡ 0.6B và 1.7B, tokenizer 12Hz. Repo chính thức tự nó không stream; muốn stream phải qua vLLM-Omni hoặc fork cộng đồng.
  - Qwen3-ASR (30 ngôn ngữ, có tiếng Việt, Fleurs-vi WER 5.55 với bản 1.7B) đã open và là ứng viên mạnh để thay Whisper.
  - Parakeet TDT v3 **không** có tiếng Việt. Nemotron 3.5 ASR streaming thì có.
- **Môi trường ồn:** đừng mặc định đặt denoise trước ASR.
  - Paper "When De-noising Hurts" (arXiv 2512.17562, 12/2025) thử MetricGAN-plus-voicebank trên Whisper, Parakeet, Gemini Flash 2.0 và Parrotlet-a với 500 bản ghi y khoa ở 9 điều kiện nhiễu, và kết luận "speech enhancement preprocessing degrades ASR performance across all noise conditions and models". Riêng Whisper ở SNR 10dB, semWER tăng từ 8.82% lên 25.83% sau khi enhance.
  - Thứ thật sự quyết định chất lượng là AEC, speaker lock, ngưỡng barge-in theo thời lượng, confidence gating và blacklist hallucination tiếng Việt (kiểu "Hãy subscribe cho kênh…").

## Key Findings

1. **Qwen3-TTS và tiếng Việt.**
   - README chính thức ghi 10 ngôn ngữ: Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian.
   - Cộng đồng đã mở thảo luận xin tiếng Việt (GitHub Discussion #274 tháng 3/2026, cùng một thread trên HF model card), nhưng đến nay chưa có phản hồi chính thức về việc bổ sung.
   - Có các bản fine-tune cộng đồng như `ShiniChien/Qwen3-TTS-12Hz-1.7B-Vietnamese` và `-VN-Style`, train từ `Qwen3-TTS-12Hz-1.7B-Base`. Chất lượng chưa có benchmark độc lập, license dữ liệu train cũng chưa rõ.
2. **Streaming của Qwen3-TTS là ở tầng serving.**
   - Hãng công bố "first audio packet immediately after a single character", "latency as low as 97ms". Đây là con số do hãng đưa ra.
   - Gói `qwen-tts` chính thức trả về waveform hoàn chỉnh. Streaming thật nằm ở:
     - vLLM-Omni: stream PCM qua HTTP và WebSocket. Tài liệu hiệu năng của vLLM-Omni ghi TTFP 64 ms ở concurrency 1; đây là số của dự án serving, không phải benchmark độc lập.
     - Các fork cộng đồng: `faster-qwen3-tts` (CUDA Graphs, RTF 5.6 trên RTX 4090 theo tác giả) và `dffdeeq/Qwen3-TTS-streaming` (chunk đầu khoảng 0.17s trên RTX 5090 theo tác giả).
3. **STT tiếng Việt.**
   - Whisper large-v3 dùng được nhưng không phải tốt nhất cho tiếng Việt. Paper VietASR đo Whisper large-v3 có WER trung bình 16.44% trên ba bộ test tiếng Việt.
   - Qwen3-ASR-1.7B đạt Fleurs-vi 5.55 và MLC-SLM-vi 14.92, theo tech report của hãng.
   - Các model chuyên tiếng Việt như PhoWhisper và ChunkFormer-large-vie cho WER thấp hơn trên benchmark tiếng Việt.
   - Parakeet TDT 0.6B v3 chỉ hỗ trợ 25 ngôn ngữ châu Âu.
4. **Turn detection có tiếng Việt.**
   - Smart Turn v3 (Pipecat/Daily): 8MB, 23 ngôn ngữ trong đó có tiếng Việt, khoảng 12ms trên CPU. Với tiếng Việt, hãng đo accuracy 81.27% và false positive 14.84%, thấp hơn trung bình các ngôn ngữ khác.
   - LiveKit turn detector (cả bản text lẫn bản audio v1) **chỉ có 14 ngôn ngữ, không có tiếng Việt**.
5. **Omni end-to-end chưa thay được cascade cho tiếng Việt.** Qwen3-Omni nhận giọng nói tiếng Việt làm input, nhưng 10 ngôn ngữ speech output **không có tiếng Việt**.

## Details — PHẦN 1: Khảo sát mô hình và sản phẩm

### 1. VAD

| Model | Phiên bản / ngày | License | Frame @16kHz | Kích thước / tốc độ | Ghi chú cho môi trường ồn |
|---|---|---|---|---|---|
| **Silero VAD** | v5.0 (27/06/2024) → **v6.0 (25/08/2025)** → v6.2 (12/2025) → v6.2.1 (24/02/2026, ONNX Runtime thành tùy chọn) | MIT | Cố định 512 mẫu = 32ms (8kHz: 256 mẫu) | README GitHub snakers4/silero-vad ghi "JIT model is around two megabytes in size". Theo hãng, một chunk 30ms+ xử lý dưới 1ms trên 1 luồng CPU | v6 theo hãng: "16% less errors on noisy real-life data", "11% less errors on multi-domain". Hãng tự nêu lỗi còn tồn tại: nhạc có nhạc cụ giống giọng người, giọng rất cao. whisper.cpp đã có `silero-v6.2.0` |
| **TEN VAD** (Agora/TEN) | 2025 | Apache-2.0 kèm điều kiện (cần đọc kỹ) | hop 160/256 mẫu = 10/16ms | Hãng công bố RTF thấp hơn 32% và thư viện nhỏ hơn 86% so với Silero | Hãng nói chính xác hơn Silero và WebRTC, phát hiện chuyển speech→silence nhanh hơn. Một benchmark cộng đồng nhỏ (NOVA-VAD, tiếng ồn UrbanSound8K) lại cho Silero F1 91.9% so với TEN-VAD 69.2%. Kết quả trái ngược nhau, cần tự đo trên dữ liệu của mình |
| **WebRTC VAD** | cũ | BSD | 10/20/30ms | Siêu nhẹ | Dựa trên GMM, nhiều false positive khi có ồn. Chỉ nên làm baseline |
| **pyannote segmentation** | 3.x | MIT (model cần chấp nhận điều khoản trên HF) | offline/cửa sổ | Nặng hơn | Hợp cho xử lý offline hoặc phát hiện giọng chồng lấn hơn là realtime |
| **NVIDIA MarbleNet / Frame-VAD, FireRedVAD, Cobra** | — | MarbleNet: NeMo; Cobra (Picovoice): **thương mại, không open source** | — | — | Chưa kiểm tra lại trong đợt này |

**Kết luận VAD:** Silero v6.2 là lựa chọn mặc định vì cùng API với v5, có sẵn trong Pipecat, LiveKit, faster-whisper và whisper.cpp, và chạy được trên trình duyệt qua `@ricky0123/vad-web` (đã hỗ trợ v6 từ 09/2026). Chỉ cân nhắc TEN VAD khi cần frame 10ms để bắt đầu/kết thúc lượt nói nhanh hơn, và phải A/B test trước khi chuyển.

### 2. Tiền xử lý cho môi trường ồn

| Hạng mục | Lựa chọn open source | Ghi chú |
|---|---|---|
| AEC (khử vọng) | WebRTC AEC3 (dùng `echoCancellation: true` trong getUserMedia ở trình duyệt), SpeexDSP | **Bắt buộc** nếu loa ngoài. Ở trình duyệt, AEC hệ thống là phương án rẻ và tốt nhất |
| Noise suppression | RNNoise (siêu nhẹ, CPU), DeepFilterNet 2/3, GTCRN, DTLN, ClearerVoice-Studio (FRCRN, MossFormer2), Resemble Enhance (offline) | Krisp là closed (Pipecat có tích hợp Krisp VIVA nhưng là thương mại) |
| Target speaker / voice isolation | ClearerVoice-Studio (có target speaker extraction), personal VAD | Nhiều nghiên cứu 2025–2026 về "foreground VAD" nhưng chưa có gói production phổ biến |
| Speaker verification (speaker lock) | ECAPA-TDNN (SpeechBrain), WeSpeaker, CAM++ (3D-Speaker), TitaNet (NeMo) | Dùng embedding của người nói chính ở lượt đầu để loại giọng nền và TV |
| Diarization | pyannote, NVIDIA Sortformer streaming, diart | Chỉ cần khi có nhiều người nói |

**Phát hiện quan trọng:** paper "When De-noising Hurts" (arXiv 2512.17562, 12/2025) thử MetricGAN-plus-voicebank trên 4 hệ ASR (Whisper, Parakeet, Gemini Flash 2.0, Parrotlet-a) với 500 bản ghi y khoa ở 9 điều kiện nhiễu, và kết luận "speech enhancement preprocessing degrades ASR performance across all noise conditions and models". Riêng Whisper ở SNR 10dB, semWER tăng từ 8.82% lên 25.83%. Kết quả: "Original noisy audio achieves lower semWER than enhanced audio in all 40 tested configurations", với mức tệ đi từ 1.1% đến 46.6% semWER tuyệt đối. Một nghiên cứu khác của Islam, Nahar và Hamid (ĐH Rajshahi, arXiv 2603.04710) dùng SAM-Audio với Whisper trên tiếng Bengali và tiếng Anh, và ghi nhận "WER and CER increase in every evaluated model–dataset configuration": trên bộ Bengali, WER của Whisper large-v3 tăng từ 65.83% lên 77.35%; trên bộ tiếng Anh, WER của Whisper base tăng từ 10.53% lên 21.66%. Ngược lại, nghiên cứu của Yang, Pandey và DeLiang Wang (arXiv 2403.06387) kết luận "ARN and CrossNet enhanced speech both translate to improved ASR results", đạt WER 3.32% (simulated) và 4.44% (real) trên CHiME-4 đơn kênh. Các kết quả CHiME-4 chính này dùng backend ASR train trên giọng sạch; paper cũng thử thêm Whisper và thấy ARN giúp Whisper cải thiện ở hầu hết cấu hình. Như vậy denoise trước ASR **tùy thuộc vào model enhancement và dữ liệu**, nên luôn A/B test.

### 3. Turn detection / semantic endpointing

| Model | Kích thước | Ngôn ngữ | Tiếng Việt | Độ trễ | License |
|---|---|---|---|---|---|
| **Pipecat Smart Turn v3 / v3.1 / v3.2** | ~8M tham số. Bản CPU int8 8MB, bản GPU fp32 32MB | 23 | **Có**: accuracy 81.27%, FP 14.84%, FN 3.88% (theo hãng, 1,004 mẫu) | 12ms trên CPU hiện đại, khoảng 60–65ms trên instance cloud (theo hãng) | BSD-2, open weights, data và training script |
| LiveKit Turn Detector (text, multilingual) | <500MB RAM | 14 | **Không** | ~25ms | Open weights, license riêng của LiveKit |
| LiveKit Turn Detector v1 (audio) | — | 14 | **Không** | — | Miễn phí trên LiveKit Cloud. Chưa xác minh được có self-host hoàn toàn được hay không |
| Namo Turn Detector (cộng đồng VN, `dangvansam`) | ~200MB (bản VN) | VN và đa ngữ | **Có**, tác giả tự đo | 4–36ms | Plugin cho LiveKit, chưa có benchmark độc lập |
| TEN Turn Detection | — | — | Chưa kiểm tra | — | — |

Smart Turn chạy sau khi VAD báo im lặng (Pipecat khuyến nghị `stop_secs=0.2`) và nhìn vào 8 giây audio cuối. Model này dựa trên prosody, không dựa transcript, nên không phụ thuộc chất lượng STT. Tuy vậy, FP 14.84% với tiếng Việt nghĩa là cứ khoảng 1/7 lần nó báo "đã nói xong" trong khi người dùng chưa xong. Nên đặt thêm một timeout dự phòng, khoảng 1.2–1.5s im lặng thì chốt lượt.

### 4. STT/ASR

| Model | Cỡ | Streaming | Tiếng Việt | Số liệu (nguồn) | License |
|---|---|---|---|---|---|
| Whisper large-v3 / **large-v3-turbo** (qua faster-whisper/CTranslate2, whisper.cpp) | 1.55B / ~809M | Không native; làm theo kiểu segment sau VAD hoặc SimulStreaming/WhisperLive | Có | Whisper large-v3 WER trung bình 16.44% trên 3 bộ test VN (VietASR, arXiv 2505.21527, đo độc lập với OpenAI) | MIT |
| **Qwen3-ASR-1.7B / 0.6B** (01/2026) | 1.7B / 0.6B | **Có, native**, nhưng chỉ qua backend vLLM (`pip install qwen-asr[vllm]`) | **Có** (30 ngôn ngữ + 22 phương ngữ) | Fleurs-vi: **5.55** (1.7B) / 8.52 (0.6B). MLC-SLM-vi: 14.92 / 17.67 (tech report của hãng). Open ASR Leaderboard: mean WER 5.76 (tiếng Anh) | Apache-2.0. ForcedAligner **không** có tiếng Việt |
| PhoWhisper (VinAI) tiny→large | 39M–1.55B | Như Whisper | Chuyên tiếng Việt | Large: CMV-vi 8.14, VIVOS 4.67, VLSP2020-T1 13.75, VLSP2020-T2 26.68 (paper của tác giả) | BSD-3 |
| ChunkFormer-large-vie | 110M | Chunk/long-form | Chuyên tiếng Việt (~25K giờ) | N-WER 6.89 trên benchmark revisit (arXiv 2603.14779, nhóm khác đánh giá) | CC-BY-NC (cần kiểm tra lại) |
| Zipformer (sherpa-onnx, k2) VN 6000h | ~30M | **Streaming thật**, chạy CPU/edge | Có (cộng đồng) | Chưa có số WER độc lập | Apache-2.0 |
| NVIDIA **Nemotron 3.5 ASR streaming 0.6B** (06/2026) | 0.6B | Cache-aware, chunk 80ms–1.12s | **Có** (nhóm "transcription-ready") | FLEURS-vi WER 13.41 (80ms) → 11.18 (1.12s), theo hãng | OpenMDW-1.1 |
| NVIDIA Parakeet TDT 0.6B v3 | 0.6B | Có | **Không** (25 ngôn ngữ châu Âu) | — | CC-BY-4.0 |
| SenseVoice, FunASR/Paraformer, Fun-ASR-MLT-Nano, FireRedASR, Kyutai STT, Moonshine, Voxtral, Granite Speech, Vosk | — | — | Chưa kiểm tra lại trong đợt này (đa số tập trung vào zh/en) | Fun-ASR-MLT-Nano Fleurs đa ngữ 10.03 so với Qwen3-ASR-1.7B 4.90 (bảng của Qwen) | — |

**Hallucination của Whisper với tiếng Việt** là lỗi đã ghi nhận nhiều lần. Khi audio im lặng hoặc có nhạc, Whisper chèn những câu kiểu "Hãy subscribe cho kênh La La School Để không bỏ lỡ những video hấp dẫn" (whisperX issue #1086, xảy ra với large, large-v2 và large-v3) hay "Hãy subscribe cho kênh Ghiền Mì Gõ…" (whisper.cpp #1051). Cách giảm thiểu được trình bày ở Phần 2.

### 5. LLM

| Dòng | Kích cỡ | License | Ghi chú cho voice |
|---|---|---|---|
| **Qwen3** (04/2025) | Dense 0.6B, 1.7B, 4B, 8B, 14B, 32B; MoE 30B-A3B, 235B-A22B | Apache-2.0 | Có chế độ thinking và non-thinking. Tắt bằng `enable_thinking=False` trong chat template hoặc soft switch `/no_think`. Hỗ trợ 119 ngôn ngữ |
| **Qwen3.5** (16/02 → 02/03/2026) | 0.8B, 2B, 4B, 9B, 27B, 35B-A3B, 122B-A10B, 397B-A17B | Apache-2.0 | Natively multimodal, công bố 201 ngôn ngữ. Theo Artificial Analysis, bản 4-bit của 9B cần khoảng 6GB và 4B khoảng 3GB. Bản Reasoning tốn rất nhiều token, nên với voice phải dùng non-thinking |
| Qwen3.6 / Qwen3.8 | — | — | Chỉ thấy ở nguồn thứ cấp (Wikipedia, blog). Chưa kiểm chứng ở nguồn chính thức nên không dùng làm căn cứ |
| Gemma 3, Llama, Phi-4 | — | — | Dùng được qua cùng endpoint OpenAI-compatible. Với tiếng Việt, Qwen thường là lựa chọn an toàn hơn (đánh giá định tính, chưa có benchmark nào được kiểm tra trong đợt này) |

Serving: vLLM hoặc SGLang (GPU, streaming, prefix caching, phù hợp nhiều phiên), llama.cpp/Ollama (máy đơn, edge), MLX (Mac). Mọi khâu trong pipeline đều dùng API kiểu OpenAI nên có thể đổi backend mà không phải sửa code.

### 6. TTS streaming

| Model | Cỡ | Tiếng Việt | Streaming / độ trễ | License |
|---|---|---|---|---|
| **Qwen3-TTS** (22/01/2026): `Qwen3-TTS-12Hz-1.7B-{CustomVoice, VoiceDesign, Base}`, `Qwen3-TTS-12Hz-0.6B-{CustomVoice, Base}`, `Qwen3-TTS-Tokenizer-12Hz`. Các bản 25Hz và 1.7B-VoiceEditing có trong tech report (arXiv 2601.15621) nhưng README ghi là "will be released in the near future" | 0.6B / 1.7B | **Không** (10 ngôn ngữ). Có bản fine-tune VN từ cộng đồng | Hãng công bố 97ms. Gói `qwen-tts` không stream; vLLM-Omni stream PCM/WebSocket ở 24kHz, có demo FastRTC (WebRTC) | Apache-2.0 |
| Qwen3-TTS-Flash / realtime | — | — | Chỉ có qua API DashScope (đóng) | Thương mại |
| **VieNeu-TTS v3 Turbo** (Phạm Nguyễn Ngọc Bảo) | Backbone AR + codec MOSS-Audio-Tokenizer-Nano; GGUF Q8 170MB | **Chuyên VN** (Bắc/Trung/Nam, 23 giọng preset, chuyển mã En–Vi, clone từ 3–5s audio) | Tác giả công bố first audio khoảng 115ms và 16 luồng đồng thời trên một RTX 3060; có server OpenAI-compatible `/v1/audio/speech`; chạy CPU qua ONNX | Kiểm tra trên HF card (tác giả ghi phiên bản "on-device, personal use", nên phải kiểm tra điều khoản thương mại) |
| VieNeu-TTS v3 Nano (preview) | 48M, flow-matching | VN | CPU-only | — |
| KhanhTTS-OmniVoice (cộng đồng) | backbone Qwen3-0.6B | VN + En (~1.500h) | Chạy được trên GPU 4GB | Apache-2.0 (theo repo) |
| CosyVoice 2/3, Fish Speech S2 Pro, IndexTTS-2, VoxCPM2, Voxtral-4B-TTS, MOSS-TTS-Nano, GLM-TTS, OmniVoice | — | Phần lớn chưa xác minh có tiếng Việt | Đều có trong danh sách TTS online của vLLM-Omni (CosyVoice3 không có online example) | Đa dạng (Voxtral bị gated) |
| Kokoro, Piper, F5-TTS(-Vietnamese), viXTTS, XTTS-v2, Chatterbox, Orpheus, Sesame CSM, Dia, Kyutai TTS, Spark-TTS, MeloTTS, VibeVoice, Higgs Audio, NeuTTS | — | Chưa kiểm tra lại trong đợt này. XTTS-v2/viXTTS dính Coqui Public Model License (phi thương mại) | — | — |

### 7. Speech-to-speech / omni

- **Qwen3-Omni-30B-A3B:** hỗ trợ 19 ngôn ngữ speech input (có tiếng Việt) và 10 ngôn ngữ speech output (**không có tiếng Việt**). Hợp làm "tai" đa phương thức, nhưng chưa nói được tiếng Việt.
- **Moshi/Unmute (Kyutai), MiniCPM-o, GLM-4-Voice, Ultravox, LFM2-Audio:** chưa kiểm tra lại trong đợt này. Theo hiểu biết chung, các model này chủ yếu mạnh ở tiếng Anh và tiếng Trung.
- **Ưu điểm của omni:** độ trễ thấp, giữ được cảm xúc và prosody.
- **Nhược điểm:** khó kiểm soát nội dung, khó gắn RAG/tool, khó thay từng thành phần, ít hỗ trợ tiếng Việt khi nói ra.
- **Kết luận:** với sản phẩm tiếng Việt năm 2026, **cascade vẫn là lựa chọn đúng**.

### 8. Framework / sản phẩm hoàn chỉnh

| Framework | Stars (giữa 2026, theo blog bên thứ ba) | License | Silero VAD | Whisper local | Qwen (OpenAI-compatible) | Qwen3-TTS | Transport |
|---|---|---|---|---|---|---|---|
| **Pipecat** (Daily) | ~13–14k; v1.0 ra 04/2026 | BSD-2 | ✅ `SileroVADAnalyzer` | ✅ `WhisperSTTService` (faster-whisper), MLX | ✅ | ❌ chưa có service chính thức (issue #2126 còn mở). Có repo cộng đồng Qwen3-TTS-OpenAI-FastAPI kèm pipeline Pipecat | WebRTC (Daily, SmallWebRTC), WebSocket, telephony |
| **LiveKit Agents** | ~11–14k | Apache-2.0 | ✅ | Qua plugin OpenAI-compatible hoặc tự viết | ✅ | ❌ tự viết | WebRTC SFU, SIP |
| **TEN Framework** | ~11k | Apache-2.0 "with conditions" | TEN VAD | extension | ✅ | ❌ | Agora RTC, WebSocket |
| FastRTC (HF) | — | MIT | ✅ | ✅ | ✅ | vLLM-Omni có sẵn demo FastRTC | WebRTC qua Gradio |
| Bolna, Dograh, Vocode | — | — | — | — | — | — | Thiên về telephony |
| RealtimeSTT/TTS/VoiceChat (KoljaB), HF speech-to-speech, Unmute, Open WebUI voice, Wyoming/Home Assistant, sherpa-onnx, Speaches, LocalAI, OpenVoiceOS, xiaozhi-esp32(-server) | Chưa kiểm tra lại số liệu trong đợt này | | | | | | |

Với stack yêu cầu, **Pipecat là lựa chọn ít phải code nhất**: chỉ cần viết một `TTSService` cho Qwen3-TTS và VieNeu, và việc đó đơn giản vì cả hai đều đã có server kiểu `/v1/audio/speech`.

## Details — PHẦN 2: Ghép Silero VAD v5/v6 + Whisper + Qwen3 + Qwen3-TTS

### Kiến trúc tổng thể

```mermaid
flowchart LR
  C[Client browser/mobile<br/>getUserMedia: echoCancellation, noiseSuppression=false/true A/B<br/>WebRTC Opus hoặc WebSocket PCM16 16kHz mono] --> G[Gateway asyncio]
  G --> R[Resample 16k + ring buffer 20ms]
  R --> NS[Denoise nhẹ RNNoise/DFN3<br/>CHỈ cho nhánh VAD]
  NS --> V[Silero VAD v6.2<br/>512 mẫu/32ms]
  V --> T[Smart Turn v3 + timeout 1.2s]
  R -->|audio gốc đã AEC| A[faster-whisper large-v3-turbo<br/>language=vi]
  T -->|end of turn| A
  A --> F[Lọc rác: no_speech, avg_logprob,<br/>compression_ratio, blacklist VN, speaker lock]
  F --> L[Qwen3 qua vLLM<br/>enable_thinking=False, stream]
  L --> S[Sentence chunker + text normalizer VN]
  S --> TTS[TTS router: VieNeu (vi) / Qwen3-TTS vLLM-Omni (en, zh…)]
  TTS -->|PCM 24k/48k chunks| G --> C
  V -->|user speech ≥300ms khi bot nói| B[Barge-in: cancel LLM+TTS, gửi clear]
```

Client nên dùng WebRTC (Opus, có AEC của trình duyệt) khi chạy production qua Internet, vì WebRTC chịu mất gói tốt và có jitter buffer. WebSocket với PCM16 16kHz thì đơn giản, hợp cho MVP hoặc mạng LAN. Audio trả về là PCM 24kHz (Qwen3-TTS) hoặc 48kHz (VieNeu), client phát qua AudioWorklet.

### Silero VAD: tham số đề xuất

- **Phiên bản:** dùng `pip install silero-vad` bản ≥6.2. API giữ nguyên như v5 (`load_silero_vad`, `VADIterator`, `get_speech_timestamps`). Từ v5 trở đi, cửa sổ cố định là 512 mẫu ở 16kHz (256 mẫu ở 8kHz) và `window_size_samples` đã bị deprecate.
- **ONNX hay JIT:** nên dùng `load_silero_vad(onnx=True)`. README GitHub snakers4/silero-vad ghi "Under certain conditions ONNX may even run up to 4-5x faster", và dùng ONNX thì không phải nạp torch ở worker CPU. Mỗi phiên cần một `VADIterator` riêng vì model có trạng thái; gọi `reset_states()` mỗi khi kết thúc lượt.
- **Tham số cho môi trường ồn:**
  - `threshold=0.5`, nâng lên 0.6–0.7 nếu ồn nền nhiều. Ngưỡng tắt nên thấp hơn ngưỡng bật khoảng 0.15 (hysteresis; `VADIterator` đã tự làm việc này).
  - `min_silence_duration_ms=200–300` để Smart Turn quyết định nhanh.
  - `speech_pad_ms=100–200` để không cắt mất phụ âm đầu và cuối, vốn quan trọng với dấu thanh tiếng Việt.
  - `min_speech_duration_ms=250` (dùng cho `get_speech_timestamps`; trong streaming thì tự áp ngưỡng này).
- **Ngưỡng thích ứng:** đo xác suất VAD và RMS trong 2–3 giây đầu khi người dùng chưa nói. Nếu nhiễu nền làm xác suất trung bình trên 0.3 thì nâng threshold lên 0.65–0.7 và tăng ngưỡng barge-in.

### Whisper: cấu hình chống hallucination

- **Chọn model:**
  - Mặc định: `large-v3-turbo` (faster-whisper hỗ trợ alias `turbo`), `compute_type="float16"` trên GPU hoặc `int8_float16` khi thiếu VRAM.
  - Nếu cần chất lượng tiếng Việt cao hơn: PhoWhisper-large (phải convert sang CTranslate2) hoặc Qwen3-ASR-1.7B.
- **Tham số cho từng lượt nói đã cắt sẵn bằng VAD:**
  - `language="vi"`: bắt buộc, vì tự nhận diện ngôn ngữ trên đoạn ngắn và ồn rất dễ sai.
  - `beam_size=1–3`: greedy nhanh nhất, 3 cho kết quả tốt hơn với chi phí trễ khoảng 30–50%.
  - `condition_on_previous_text=False`: chặn lỗi lặp lan từ đoạn trước.
  - `vad_filter=True` với `vad_parameters=dict(min_silence_duration_ms=500)`. Đây là lớp lọc thứ hai; mặc định của faster-whisper chỉ cắt khoảng im lặng dài trên 2 giây.
  - `no_speech_threshold=0.6`, `log_prob_threshold=-1.0`, `compression_ratio_threshold=2.4`.
  - `temperature=0.0`: tắt fallback nhiệt độ để không tốn thêm độ trễ.
  - `hotwords="tên sản phẩm, thương hiệu…"` hoặc `initial_prompt` ngắn có dấu câu chuẩn tiếng Việt. **Không** đưa các câu kiểu "cảm ơn đã xem" vào prompt.
- **Lọc sau khi transcribe:**
  - Loại segment có `no_speech_prob > 0.6` và `avg_logprob < -1.0`.
  - Loại cả lượt nếu `compression_ratio > 2.4`, hoặc nếu lượt đó dài dưới 2 từ mà VAD lại báo dưới 400ms.
  - Áp blacklist regex: `subscribe`, `đăng k[ýí] (cho )?kênh`, `để không bỏ lỡ những video`, `cảm ơn (các bạn )?đã (xem|theo dõi)`, `La La School`, `Ghiền Mì Gõ`, và mọi câu lặp nguyên văn 3 lần (dự án opencode-voice dùng đúng heuristic này).

### Qwen3: chọn cỡ và cách gọi

- **Chọn cỡ theo phần cứng:**
  - GPU 24GB: Qwen3-8B-AWQ hoặc Qwen3.5-9B (4-bit).
  - GPU 12GB: Qwen3-4B hoặc Qwen3.5-4B.
  - Server lớn: Qwen3-30B-A3B. Là MoE với khoảng 3B tham số active nên TTFT và tốc độ sinh token tốt; chọn khi cần thông minh hơn mà vẫn nhanh.
- **Tắt thinking** bằng `extra_body={"chat_template_kwargs": {"enable_thinking": False}}` khi gọi vLLM, hoặc thêm `/no_think` vào cuối tin nhắn user.
- **System prompt cho hội thoại nói:**
  - Trả lời 1–3 câu ngắn, không dùng markdown, emoji, bảng hay URL.
  - Viết số, ngày, giờ thành chữ, hoặc để bước normalizer xử lý.
  - Hỏi lại khi không chắc đã nghe đúng.
- **Sentence chunking:**
  - Gửi sang TTS ngay khi gặp `.?!…;:` hoặc xuống dòng.
  - Riêng cụm đầu tiên được cắt ở dấu phẩy nếu đã đủ khoảng 25 ký tự, để giảm thời gian đến âm thanh đầu tiên.
  - Gom câu quá ngắn (dưới 8 ký tự) vào câu sau.
- **Lịch sử hội thoại:**
  - Giữ khoảng 10–20 lượt gần nhất, phần cũ hơn thì tóm tắt lại.
  - Khi bị ngắt lời, **chỉ lưu phần câu trả lời đã thực sự phát** cho người dùng nghe, kèm ghi chú "[bị ngắt]".

### Qwen3-TTS: chọn model và cách dùng

- **Chọn model:**
  - `Qwen3-TTS-12Hz-0.6B-CustomVoice` cho độ trễ thấp và VRAM nhỏ.
  - `1.7B-CustomVoice` khi cần điều khiển giọng bằng `instruct`.
  - `1.7B-Base` (hoặc 0.6B-Base) khi cần clone giọng. Chỉ bản Base có `create_voice_clone_prompt` và `generate_voice_clone`; gọi hai hàm này trên CustomVoice hoặc VoiceDesign sẽ báo `ValueError`.
- **API thư viện chính thức** (`pip install -U qwen-tts`): `Qwen3TTSModel.from_pretrained(...)`, rồi gọi `generate_custom_voice(text, language, speaker, instruct)`, `generate_voice_design(...)` hoặc `generate_voice_clone(text, language, ref_audio, ref_text | voice_clone_prompt)`. Các hàm này trả về `(wavs, sr)` sau khi sinh xong, **không stream**.
- **Muốn stream:**
  - vLLM-Omni: `vllm-omni serve Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice --omni --port 8091`. Dùng `POST /v1/audio/speech` với `response_format="pcm"`, `stream_format="audio"` (yêu cầu `async_chunk: true`, mặc định đã bật trong `qwen3_tts.yaml`), hoặc dùng WebSocket với các message `session.config` / `input.text` / `input.done` → `audio.start` / PCM nhị phân / `audio.done`. Tham số `speed` không dùng được khi stream.
  - `faster-qwen3-tts`: hàm `generate_voice_clone_streaming(chunk_size=8)`.
- **Tiếng Việt:** Qwen3-TTS chính thức không hỗ trợ. Có ba hướng:
  - (a) VieNeu-TTS v3 Turbo qua server `/v1/audio/speech`. Đây là khuyến nghị.
  - (b) Bản fine-tune cộng đồng `ShiniChien/Qwen3-TTS-12Hz-1.7B-Vietnamese`. Cùng API `qwen_tts`, `language="Vietnamese"`, nhưng phải tự đánh giá MOS và CER.
  - (c) Tự fine-tune từ bản Base bằng thư mục `finetuning/` trong repo chính thức.
- **Chuẩn hóa văn bản tiếng Việt** trước khi gửi sang TTS:
  - Số → chữ ("1.250.000đ" → "một triệu hai trăm năm mươi nghìn đồng").
  - Ngày ("06/10/2026" → "ngày sáu tháng mười năm hai nghìn không trăm hai mươi sáu").
  - Giờ, phần trăm, đơn vị.
  - Viết tắt: TP.HCM, UBND, km/h.
  - Từ tiếng Anh: giữ nguyên nếu TTS đọc được code-switch (VieNeu đọc được), nếu không thì phiên âm.
- **Lỗi G2P đã biết:** VieNeu v3 Turbo đọc "chánh" thành "tránh" (issue #207). Cần có từ điển thay thế cho tên riêng và thuật ngữ trong domain của mình.

### Barge-in và echo

1. **Echo:** dùng AEC ở client và bán song công mềm. Khi bot đang nói, nâng ngưỡng VAD lên 0.7 và yêu cầu giọng người dùng kéo dài **≥300–500ms liên tục** mới tính là ngắt lời. Có thể thêm điều kiện ASR nhanh trên đoạn đó ra ít nhất 2 từ và không trùng với câu bot đang phát.
2. **Khi xác nhận người dùng ngắt lời:**
   - Hủy task LLM (đóng stream).
   - Hủy request TTS (đóng HTTP/WS).
   - Xóa hàng đợi câu đang chờ.
   - Gửi `{"type":"clear"}` để client xóa buffer AudioWorklet.
   - Ghi lại phần đã phát vào lịch sử hội thoại.
3. **False interruption do ồn:**
   - Tiếng ồn ngắn kiểu ho hay tiếng gõ thì ngưỡng thời lượng ở bước 1 đã chặn được.
   - Với giọng nền, dùng speaker lock: so cosine similarity giữa embedding ECAPA/CAM++ của đoạn mới và embedding người dùng (lấy ở lượt đầu, cập nhật dần). Dưới khoảng 0.5–0.6 thì bỏ qua (ngưỡng cần hiệu chỉnh trên dữ liệu của mình).
   - Backchannel như "ừ", "vâng", "ok" khi bot đang nói thì không ngắt.

### Ngân sách độ trễ (ước tính, phải tự đo trên phần cứng của mình)

| Khâu | Mục tiêu | Ghi chú |
|---|---|---|
| Mạng và jitter buffer | 30–80ms | WebRTC |
| VAD im lặng | 200–300ms | `stop_secs=0.2` theo Pipecat |
| Smart Turn | 10–65ms | Số của hãng |
| ASR (turbo, GPU, câu 3–5s) | 100–300ms | Ước tính, chưa có benchmark độc lập |
| LLM TTFT và cụm đầu tiên | 150–350ms | Qwen3-8B AWQ, vLLM, prefix cache |
| TTS TTFA | 64–300ms | Theo vLLM-Omni và fork cộng đồng; VieNeu khoảng 115ms theo tác giả |
| **Tổng voice-to-voice** | **~0.7–1.2s** | |

**Kỹ thuật tối ưu:**
- Warm-up mọi model khi khởi động và giữ model nằm sẵn trong VRAM.
- vLLM: prefix caching cho system prompt.
- Pipecat từng có lỗi (PR #5931): `transcribe` của faster-whisper trả về generator lười, nếu duyệt nó trên event loop thì chặn cả pipeline. Phải gom segment ngay bên trong `asyncio.to_thread`.
- Preemptive generation: khi VAD báo im lặng 200ms thì chạy ASR và LLM luôn; nếu người dùng nói tiếp thì hủy.
- Các bước nối với nhau qua queue bất đồng bộ.

**VRAM trên 1 GPU 24GB (ước tính):**
- Whisper turbo fp16: ~2–3GB.
- Qwen3-8B-AWQ cộng KV cache cho vài phiên: ~8–10GB (`--gpu-memory-utilization 0.4`).
- Qwen3-TTS 1.7B: ~5–7GB. Bản 0.6B thấp hơn.
- VieNeu GPU: ~2–3GB.
- Tổng nằm trong 24GB nhưng không còn nhiều dư. Với GPU 12GB, dùng Qwen3-4B 4-bit, Qwen3-TTS 0.6B hoặc VieNeu, và turbo `int8_float16`.

### Code mẫu (FastAPI + WebSocket, asyncio)

```python
# server.py — pip install fastapi uvicorn silero-vad faster-whisper openai httpx numpy
import asyncio, re, json
import numpy as np, httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from silero_vad import load_silero_vad, VADIterator
from faster_whisper import WhisperModel
from openai import AsyncOpenAI

SR, WIN = 16000, 512                      # Silero v5/v6: cố định 512 mẫu @16kHz
VAD_MODEL = load_silero_vad(onnx=True)
ASR = WhisperModel("large-v3-turbo", device="cuda", compute_type="float16")
LLM = AsyncOpenAI(base_url="http://vllm:8000/v1", api_key="none")
LLM_MODEL = "Qwen/Qwen3-8B-AWQ"
# Mọi TTS đều sau một endpoint /v1/audio/speech → đổi backend chỉ là đổi URL
TTS = {"vi": ("http://vieneu:8000/v1/audio/speech", "Trúc Ly", None),
       "en": ("http://qwen3tts:8091/v1/audio/speech", "Vivian", "English")}
SYSTEM = ("Bạn là trợ lý giọng nói. Trả lời tiếng Việt, 1-3 câu ngắn, không markdown, "
          "không emoji, viết số thành chữ. Nếu không nghe rõ, hãy hỏi lại.")
BLACKLIST = re.compile(r"subscribe|đăng k[ýí].{0,10}kênh|bỏ lỡ những video|"
                       r"cảm ơn (các bạn )?đã (xem|theo dõi)|la la school|ghiền mì gõ", re.I)
SENT_END = re.compile(r"([.!?…;:]\s|\n)")

def transcribe(audio: np.ndarray):
    segs, _ = ASR.transcribe(audio, language="vi", beam_size=2, temperature=0.0,
        condition_on_previous_text=False, vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
        no_speech_threshold=0.6, log_prob_threshold=-1.0,
        compression_ratio_threshold=2.4, hotwords="Pipecat, Qwen")
    segs = list(segs)                      # giải mã generator NGAY trong thread
    good = [s for s in segs if not (s.no_speech_prob > 0.6 and s.avg_logprob < -1.0)
            and s.compression_ratio < 2.4]
    text = " ".join(s.text.strip() for s in good).strip()
    return "" if (not text or BLACKLIST.search(text)) else text

class Session:
    def __init__(self, ws: WebSocket):
        self.ws = ws
        self.vad = VADIterator(VAD_MODEL, threshold=0.5, sampling_rate=SR,
                               min_silence_duration_ms=300, speech_pad_ms=150)
        self.pending = np.zeros(0, np.float32)
        self.turn, self.in_speech, self.speech_ms = [], False, 0
        self.history = [{"role": "system", "content": SYSTEM}]
        self.reply: asyncio.Task | None = None
        self.bot_speaking = False

    async def on_audio(self, pcm16: bytes):
        self.pending = np.concatenate([self.pending,
                       np.frombuffer(pcm16, np.int16).astype(np.float32) / 32768])
        while len(self.pending) >= WIN:
            chunk, self.pending = self.pending[:WIN], self.pending[WIN:]
            ev = self.vad(chunk)           # {'start':..} | {'end':..} | None
            if self.in_speech or ev and "start" in ev:
                self.turn.append(chunk)
            if ev and "start" in ev:
                self.in_speech, self.speech_ms = True, 0
            if self.in_speech:
                self.speech_ms += 32
                # Barge-in: chỉ ngắt khi người dùng nói liên tục ≥400ms
                if self.bot_speaking and self.speech_ms >= 400:
                    await self.interrupt()
            if ev and "end" in ev:
                self.in_speech = False
                audio = np.concatenate(self.turn); self.turn = []
                if len(audio) / SR >= 0.3:  # (chỗ gắn Smart Turn v3 / speaker lock)
                    asyncio.create_task(self.handle_turn(audio))

    async def interrupt(self):
        if self.reply and not self.reply.done():
            self.reply.cancel()
        self.bot_speaking = False
        await self.ws.send_text(json.dumps({"type": "clear"}))

    async def handle_turn(self, audio):
        text = await asyncio.to_thread(transcribe, audio)
        if not text:
            return
        await self.ws.send_text(json.dumps({"type": "user", "text": text}))
        await self.interrupt()
        self.history.append({"role": "user", "content": text})
        self.reply = asyncio.create_task(self.respond())

    async def respond(self, lang="vi"):
        spoken, buf = [], ""
        q: asyncio.Queue = asyncio.Queue()
        tts_task = asyncio.create_task(self.tts_worker(q, lang, spoken))
        try:
            stream = await LLM.chat.completions.create(model=LLM_MODEL,
                messages=self.history[-21:], stream=True, temperature=0.6, max_tokens=200,
                extra_body={"chat_template_kwargs": {"enable_thinking": False}})
            async for ch in stream:
                buf += ch.choices[0].delta.content or ""
                m = SENT_END.search(buf)
                first_cut = not spoken and q.empty() and "," in buf and len(buf) > 25
                if m or first_cut:
                    cut = m.end() if m else buf.index(",") + 1
                    sent, buf = buf[:cut].strip(), buf[cut:]
                    if len(sent) > 1:
                        await q.put(normalize_vi(sent))
            if buf.strip():
                await q.put(normalize_vi(buf.strip()))
            await q.put(None)
            await tts_task
        except asyncio.CancelledError:
            tts_task.cancel()
            spoken.append("[bị ngắt]")
            raise
        finally:
            self.bot_speaking = False
            self.history.append({"role": "assistant", "content": " ".join(spoken)})

    async def tts_worker(self, q, lang, spoken):
        url, voice, language = TTS[lang]
        async with httpx.AsyncClient(timeout=30) as http:
            while (sent := await q.get()) is not None:
                body = {"input": sent, "voice": voice, "response_format": "pcm",
                        "stream_format": "audio"}
                if language: body["language"] = language   # Qwen3-TTS cần language
                self.bot_speaking = True
                async with http.stream("POST", url, json=body) as r:
                    async for pcm in r.aiter_bytes(4800):
                        await self.ws.send_bytes(pcm)       # client phát ở 24k/48k
                spoken.append(sent)

def normalize_vi(s: str) -> str:
    # TODO: số/ngày/giờ/đơn vị/viết tắt → chữ (dùng thư viện TN tiếng Việt hoặc luật riêng)
    return s.replace("TP.HCM", "Thành phố Hồ Chí Minh").replace("%", " phần trăm")

app = FastAPI()

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    s = Session(ws)
    try:
        while True:
            msg = await ws.receive()
            if msg.get("bytes"):
                await s.on_audio(msg["bytes"])     # PCM16 mono 16kHz, ~20ms/khung
    except WebSocketDisconnect:
        await s.interrupt()
```

Lưu ý khi dùng code này:
- Body JSON của TTS stream theo tài liệu vLLM-Omni. Server VieNeu có thể dùng tên trường khác, cần kiểm tra `docs/streaming.md` trong repo VieNeu.
- Client cần biết sample rate của audio trả về: 24kHz với Qwen3-TTS, 48kHz với VieNeu v3 Turbo.
- Nếu đi theo **Pipecat**, thay toàn bộ phần trên bằng: `SileroVADAnalyzer()` + `LocalSmartTurnAnalyzerV3` + `WhisperSTTService` (faster-whisper) + `OpenAILLMService(base_url=vLLM)` + một `TTSService` tự viết, trong đó `run_tts()` gọi `/v1/audio/speech` và yield các frame audio. Bộ này nhận được ngắt lời, metrics TTFB và transport WebRTC sẵn có.

### Triển khai

```yaml
# docker-compose.yml (khung — kiểm tra tag image/flag trên tài liệu từng dự án)
services:
  vllm:
    image: vllm/vllm-openai:latest
    command: ["--model","Qwen/Qwen3-8B-AWQ","--max-model-len","8192",
              "--gpu-memory-utilization","0.40","--enable-prefix-caching"]
    deploy: {resources: {reservations: {devices: [{capabilities: [gpu]}]}}}
  qwen3tts:
    build: ./qwen3tts            # pip install vllm-omni
    command: ["vllm-omni","serve","Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice","--omni",
              "--port","8091","--gpu-memory-utilization","0.25"]
    deploy: {resources: {reservations: {devices: [{capabilities: [gpu]}]}}}
  vieneu:
    build: ./vieneu              # profile api-gpu theo repo VieNeu-TTS
  app:
    build: ./app                 # server.py: Silero + faster-whisper (GPU) 
    ports: ["8080:8080"]
    depends_on: [vllm, qwen3tts, vieneu]
```

- **Scale nhiều phiên:**
  - Mỗi phiên giữ VAD state riêng trên CPU.
  - ASR chạy qua một worker pool có batch (faster-whisper có `BatchedInferencePipeline`). Theo Qwen3-ASR Technical Report (arXiv 2601.21337), bản 0.6B chạy qua vLLM "can achieve an average TTFT as low as 92ms and transcribe 2000 seconds speech in 1 second at a concurrency of 128" (RTF 0.064); con số này là của bản 0.6B, không phải 1.7B.
  - LLM và TTS gom batch liên tục (continuous batching) trong vLLM / vLLM-Omni. Theo tác giả, VieNeu chạy được 16 luồng trên một RTX 3060.
  - Khi số phiên lớn, tách ASR, LLM và TTS ra các GPU riêng.
- **Giám sát:** log theo từng lượt các mốc `vad_end→asr_done`, `asr_done→llm_first_token`, `first_sentence→tts_first_byte` và `voice-to-voice` (đo phía client), cùng tỉ lệ transcript bị lọc, tỉ lệ barge-in và tỉ lệ ngắt lời sai. Pipecat có sẵn metrics TTFB cho từng service. vLLM-Omni có trang Production Metrics.
- **Đánh giá chất lượng:**
  - WER/CER tiếng Việt trên bộ test nội bộ có trộn ồn ở SNR 0/5/10/20dB (quán cà phê, xe máy, TV). Chạy với và không có denoise.
  - MOS/CMOS cho TTS với 10–20 người nghe, và CER khi đưa audio TTS qua lại ASR để đo độ rõ.
  - False-cutoff rate của turn detection và false-interruption rate khi phát nhiễu nền.
  - Voice-to-voice P50/P95.

## Recommendations

**Stack theo cấu hình:**

| Cấu hình | VAD/Turn | STT | LLM | TTS |
|---|---|---|---|---|
| **GPU server (đa phiên)** | Silero v6.2 + Smart Turn v3.2 (CPU) | Qwen3-ASR-1.7B qua vLLM (streaming), hoặc faster-whisper turbo kiểu batched | Qwen3-30B-A3B hoặc Qwen3.5-35B-A3B qua vLLM/SGLang | VieNeu v3 Turbo GPU server (vi) + Qwen3-TTS 1.7B qua vLLM-Omni (đa ngữ) |
| **1 GPU 12–24GB** | Silero v6.2 + Smart Turn v3 | faster-whisper large-v3-turbo fp16/int8, hoặc PhoWhisper | Qwen3-8B-AWQ (24GB) / Qwen3-4B hoặc Qwen3.5-4B 4-bit (12GB) | VieNeu v3 Turbo (vi); Qwen3-TTS 0.6B-CustomVoice (en/zh) |
| **CPU / edge** | Silero ONNX + Smart Turn int8 | sherpa-onnx Zipformer VN streaming, hoặc whisper.cpp small/turbo q5 | Qwen3.5-2B/4B hoặc Qwen3-1.7B GGUF qua llama.cpp | VieNeu v3 Turbo ONNX/GGUF hoặc v3 Nano |

**Lộ trình:**
1. **MVP (1–2 tuần):** Pipecat + SmallWebRTC; Silero + Smart Turn + WhisperSTTService(turbo, `vi`) + Qwen3-8B qua vLLM + TTS service tự viết gọi VieNeu. Đo voice-to-voice và WER ngay từ ngày đầu.
2. **Beta:**
   - Bổ sung blacklist hallucination, confidence gating và ngưỡng barge-in theo thời lượng.
   - Thêm speaker lock bằng CAM++/ECAPA.
   - Xây bộ chuẩn hóa văn bản tiếng Việt.
   - A/B test denoise trước ASR, và mặc định là **không** denoise trên nhánh ASR.
3. **Production:**
   - Tách dịch vụ theo GPU, chạy batch liên tục.
   - Quan sát đủ các mốc độ trễ P95.
   - Thay ASR bằng Qwen3-ASR (streaming) nếu nó thắng Whisper trên bộ test tiếng Việt có ồn của mình.
   - Cân nhắc fine-tune Qwen3-TTS Base cho tiếng Việt nếu cần một model TTS dùng cho mọi ngôn ngữ.

**Khi nào nên thay thành phần:**
- **Thay Whisper** khi WER tiếng Việt trong ồn cao hơn khoảng 15%, khi hallucination vẫn lọt qua bộ lọc, hoặc khi cần partial transcript để làm preemptive generation. Lựa chọn thay: Qwen3-ASR, PhoWhisper hoặc ChunkFormer. **Không** chọn Parakeet v3 vì nó không có tiếng Việt.
- **Thay Qwen3-TTS** cho tiếng Việt ngay từ đầu. Với ngôn ngữ khác, thay khi cần chạy trên CPU (lúc đó dùng Kokoro hoặc Piper) hoặc khi cần license, voice clone khác (CosyVoice, Fish S2 Pro; phải kiểm tra license từng model).
- **Thay Smart Turn** bằng Namo hoặc một model tự fine-tune nếu tỉ lệ ngắt lời sai trên tiếng Việt vẫn trên 10%.

## Caveats

- **Số liệu do hãng hoặc tác giả công bố, chưa có benchmark độc lập:** Qwen3-TTS 97ms; TTFP 64ms của vLLM-Omni; RTF và TTFA của faster-qwen3-tts; 115ms và 16 luồng của VieNeu; độ chính xác của Smart Turn; số WER của Qwen3-ASR và Nemotron; mức cải thiện 16% của Silero v6; so sánh TEN VAD với Silero.
- **Số liệu từ bên thứ ba:** WER Whisper large-v3 16.44% (paper VietASR); các nghiên cứu cho thấy denoise làm giảm ASR (không có nghiên cứu nào trên tiếng Việt); benchmark NOVA-VAD (quy mô nhỏ).
- **Số GitHub stars của framework** lấy từ các blog so sánh giữa năm 2026, có chênh lệch giữa các nguồn.
- **Các thông tin về Qwen3.6/3.8** chỉ thấy ở nguồn thứ cấp nên không đưa vào khuyến nghị.
- **Chưa kiểm tra lại trong đợt này:** FireRedVAD, MarbleNet, Cobra, Kyutai, Moshi/Unmute, MiniCPM-o, GLM-4-Voice, Ultravox, LFM2-Audio, CosyVoice 3, F5-TTS-Vietnamese, viXTTS và các framework nhỏ (Bolna, Dograh, Speaches, LocalAI, xiaozhi). Thông tin về các mục này nên được xác minh trước khi ra quyết định.
- **License cần kiểm tra trước khi thương mại hóa:** VieNeu v3 Turbo (ghi "personal use"), ChunkFormer, các model trong TEN, các bản fine-tune Qwen3-TTS tiếng Việt từ cộng đồng (dữ liệu train), XTTS/viXTTS (CPML).
- **Code mẫu:** tên hàm của silero-vad, faster-whisper, qwen-tts và vLLM-Omni đã đối chiếu với tài liệu chính thức. Riêng body JSON stream của server VieNeu và tag Docker image của vLLM-Omni cần kiểm tra lại theo phiên bản bạn cài.
- **Ngân sách độ trễ và VRAM** là ước tính kỹ thuật, phải đo lại trên phần cứng thật.