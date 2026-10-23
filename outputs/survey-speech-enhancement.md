# Khảo sát các mô hình Speech Enhancement (SE) dùng để khử nhiễu trước ASR

Tôi chỉ dùng nội dung đã có trong wiki và không mở `raw/`. Wiki có 249 concept và vượt qua bước kiểm tra cấu trúc.

## 1. Câu hỏi chính: có nên khử nhiễu trước ASR không?

Các nguồn mâu thuẫn nhau, nên chưa thể coi khử nhiễu trước ASR là mặc định an toàn ([Speech Enhancement Before ASR](wiki/speech-enhancement-before-asr.md)):

- **Hai nghiên cứu báo là làm hại:**
  - arXiv 2512.17562 dùng MetricGAN+ trước Whisper, Parakeet, Gemini và Parrotlet. Khử nhiễu làm tệ hơn ở cả 40 cấu hình thử. Ví dụ Whisper ở SNR 10 dB tăng từ 8.82% lên 25.83% semWER.
  - arXiv 2603.04710 dùng SAM-Audio trước Whisper. WER tăng ở mọi cấu hình thử, ví dụ tiếng Bengali tăng từ 65.83% lên 77.35%.
- **Một nghiên cứu báo là giúp:** arXiv 2403.06387 dùng ARN và CrossNet trên tập CHiME-4 và thấy WER giảm, kể cả với Whisper.
- **Giới hạn:** cả ba nghiên cứu chỉ được trích lại qua một báo cáo do AI tổng hợp. Bản thân các bài báo không có trong `raw/`. Không nghiên cứu nào làm trên tiếng Việt.
- **Cách làm mà báo cáo đề xuất:**
  - ASR nhận audio gốc đã qua AEC (khử tiếng vọng).
  - Chỉ khử nhiễu nhẹ (RNNoise hoặc DeepFilterNet 3) trên nhánh VAD/barge-in.
  - So sánh A/B bằng WER/CER tiếng Việt ở SNR 0/5/10/20 dB.
  - Xem thêm [Vietnamese Realtime Voice Agent Stack](wiki/vietnamese-realtime-voice-agent-stack.md) và [Vietnamese Speech Pipeline Design](wiki/vietnamese-speech-pipeline-design.md).

## 2. Các nhóm mô hình (cách chia nhóm là suy luận của tôi từ các trang wiki)

| Nhóm | Mô hình | Params / compute | Streaming / tốc độ | Giấy phép | Bằng chứng về ASR |
|---|---|---|---|---|---|
| **A. Siêu nhẹ, causal, mask trên miền thời gian–tần số** (cho CPU/MCU) | [CoFi-Lite](wiki/cofi-lite.md) | 83k, 12.87M MACs/s | RTF 0.033 trên i5 desktop (ONNX) | ? | Không có |
| | [UL-UNAS](wiki/ul-unas.md) | 171k, 35M MACs/s, không look-ahead | Bài báo không báo RTF; bài CoFi-Lite đo được 0.066 | ? | Không có |
| | [FastEnhancer](wiki/fastenhancer.md) T/B/S/M/L | 22k–1.1M | T/B: RTF 0.012–0.022 trên 1 luồng Xeon, 0.006–0.011 trên M5 | ? | Có WER của Whisper trên audio đã khử nhiễu (2.8–3.6%), nhưng **không có dòng audio nhiễu gốc** để so |
| | [Fast-ULCNet](wiki/fast-ulcnet.md) | 0.338M | RTF 0.60–0.66 trên Cortex-A53 / Pi 3 | ? | Không có |
| | GTCRN, LiSenNet, RNNoise (chỉ xuất hiện làm baseline, chưa có trang riêng) | 24–87k | — | — | — |
| **B. Họ DeepFilterNet** (causal, cỡ trung) | [DPDFNet](wiki/dpdfnet.md) (DeepFilterNet2 + DPRNN) | 2.3–3.6M, 1.35–4.37 GMACs | Có API `StreamEnhancer` dùng ONNX; RTF trên NPU Ceva; không có RTF CPU | Apache-2.0 (code) | Không có WER, nhưng tập test 12 ngôn ngữ có tiếng Việt |
| | DeepFilterNet 2/3 (chỉ làm baseline) | ~2.2M, 0.35 G | — | — | — |
| **C. Causal trên miền waveform** | [Facebook Denoiser](wiki/facebook-denoiser.md) (Demucs) | H=48/64 | RTF 0.6–1.2 trên i5 cũ, độ trễ khoảng 41 ms ([live](wiki/denoiser-live-streaming.md)) | **CC-BY-NC** | Không có |
| **D. Ưu tiên chất lượng, offline, đa tác vụ** | [ClearVoice](wiki/clearvoice.md) (FRCRN, MossFormerGAN, MossFormer2) | Không công bố | Không có số liệu streaming hay độ trễ; vài model chạy 48 kHz | ? | Chỉ có PESQ (MossFormerGAN 16k: 3.47 trên VB+DEMAND) |
| | [Resemble Enhance](wiki/resemble-enhance.md) (denoiser + enhancer kiểu generative CFM) | ? | Chỉ xử lý batch, 44.1 kHz | ? | Không có số liệu nào |
| **E. Tách nguồn / trích xuất người nói** | [SAM Audio GGUF](wiki/sam-audio-gguf.md); ClearVoice SS/TSE | SAM: 8.5–18 GB VRAM | SAM: RTF 0.05–0.10 trên RTX 5090 | sam-license | **SAM-Audio làm WER tăng** (2603.04710) |

Ngoài SE, wiki còn ghi các biện pháp chống nhiễu mà báo cáo đánh giá là hiệu quả hơn ([Barge-in & Echo](wiki/voice-agent-barge-in-and-echo-handling.md)):

- AEC (WebRTC AEC3, SpeexDSP), bắt buộc khi dùng loa ngoài.
- Speaker lock bằng embedding (ECAPA, CAM++).
- Barge-in có ngưỡng thời lượng, lọc theo confidence, blacklist chống hallucination.

## 3. Nhận xét so sánh (phần lớn là suy luận từ các trang wiki)

- **Không so được số giữa các bài báo.** Chính GTCRN có PESQ 2.87 trong bài FastEnhancer/UL-UNAS, nhưng chỉ 2.60 trong DPDFNet vì DPDFNet lọc high-pass 70 Hz. Mỗi bài cũng dùng tập test, cách huấn luyện lại baseline và phần cứng khác nhau.
- **MACs không dự đoán được tốc độ.**
  - FastEnhancer-B có số MACs gấp 6.5 lần GTCRN nhưng chạy nhanh hơn 2.7 lần.
  - UL-UNAS có MACs gần bằng GTCRN nhưng RTF cao nhất trong bảng của CoFi-Lite.
  - Vì vậy hãy tự đo RTF trên phần cứng của mình.
- **Rủi ro khi chạy liên tục.**
  - Fast-ULCNet bị trôi trạng thái RNN sau khoảng 60 s ([Comfi-FastGRNN](wiki/comfi-fastgrnn-state-drift.md)).
  - DPDFNet bản gốc bị cắt mất tiếng nói sau 3–4 s im lặng, và đã sửa bằng fine-tune trên chuỗi dài.
  - Nên chạy thử liên tục nhiều phút, không chỉ trên clip 10 s.
- **Không mô hình nào có A/B WER giữa audio nhiễu và audio đã khử nhiễu**, và không có kết quả riêng cho tiếng Việt. Tất cả số liệu đều do tác giả tự báo và chưa ai chạy lại.
- **Gợi ý chọn:**
  - Cho nhánh VAD chạy CPU: FastEnhancer-T/B, CoFi-Lite, hoặc DPDFNet-2 (có API streaming sẵn).
  - Cần chất lượng offline: ClearVoice MossFormerGAN.
  - Tránh Facebook Denoiser nếu dùng thương mại (CC-BY-NC).

## 4. Phần wiki còn thiếu

- DeepFilterNet, GTCRN, RNNoise, DTLN và Krisp chưa có trang riêng. Phần lớn chỉ xuất hiện làm baseline; Krisp chỉ được nhắc là sản phẩm đóng/thương mại.
- Ba bài về tác động của SE lên ASR (2512.17562, 2603.04710, 2403.06387) chưa có trong `raw/`.
- Hầu hết các mô hình chưa xác minh giấy phép.

Đây là câu trả lời chỉ đọc nên wiki và log không thay đổi. Bảng so sánh có giá trị dùng lại, nên tôi có thể lưu nó thành trang `type: Synthesis` (ví dụ `speech-enhancement-model-comparison.md`). Nếu bạn thêm PDF ba bài báo ASR hoặc README của DeepFilterNet/GTCRN vào `raw/`, tôi có thể đưa chúng vào wiki để bổ sung những chỗ còn thiếu.

## 5. Ứng viên với pipeline vad, asr, llm, tts

Đây là đánh giá của tôi dựa trên các trang wiki, chưa có số đo trên dữ liệu thật.

### Bước 0: Baseline không khử nhiễu, bắt buộc phải có
- ASR nhận audio gốc đã qua **AEC** (WebRTC AEC3 hoặc SpeexDSP).
- Đo WER/CER tiếng Việt trên audio này trước. Mọi mô hình phía sau đều phải thắng được baseline này.

### Ứng viên 1: **DPDFNet-2 (16 kHz)**, nên thử đầu tiên
Lý do:
- Đã có sẵn `pip install dpdfnet` và `StreamEnhancer` có giữ trạng thái RNN, nên cắm vào pipeline realtime gần như ngay được.
- Code có giấy phép Apache-2.0. Giấy phép của weights chưa kiểm tra.
- Tập test có 12 ngôn ngữ ở SNR thấp, **trong đó có tiếng Việt**. Không mô hình nào khác trong wiki có điểm này.
- Bản fine-tune trên chuỗi dài đã sửa lỗi cắt mất tiếng nói sau khoảng lặng, rất quan trọng với voice agent chạy liên tục. Tuy vậy, chưa xác minh weights công khai đã có bản sửa này.
- Có tham số `--attn-limit-db` (hiện chưa có tài liệu). Tôi đoán nó giới hạn mức khử nhiễu; nếu đúng thì hữu ích cho ASR, vì khử nhiễu quá tay thường sinh artifact.

Điểm cần đo: wiki chưa có RTF trên CPU, cần tự đo. Model khá nặng (2.5M params, 1.35 GMACs).

### Ứng viên 2: **FastEnhancer-B** (hoặc Tiny), khi CPU bị giới hạn
- Nhanh nhất trên CPU trong các mô hình có trong wiki: RTF khoảng 0.01–0.02 trên 1 luồng, chất lượng ngang hoặc hơn GTCRN.
- Nhược điểm: chưa xác minh giấy phép; chưa có wrapper streaming dạng gói pip như DPDFNet; chưa có đánh giá trên tiếng Việt.

### Baseline tham chiếu: **RNNoise** và **DeepFilterNet 3**
- Đây là hai mô hình báo cáo pipeline gốc khuyên dùng. RNNoise rất nhẹ, DeepFilterNet 3 phổ biến.
- Nên đưa vào để biết DPDFNet và FastEnhancer có thực sự hơn không.
- Lưu ý: trong HF speech-to-speech, DeepFilterNet cần `numpy<2` và xung đột với Pocket TTS.

### Chỉ dùng để đo trần chất lượng (offline): **ClearVoice `MossFormerGAN_SE_16K`**
- Đây là mô hình có PESQ cao nhất mà wiki ghi nhận.
- Nếu ngay cả mô hình này cũng làm WER tăng, có thể kết luận gần như chắc chắn là không nên khử nhiễu trên nhánh ASR.

### Không nên thử
- **Facebook Denoiser**: giấy phép CC-BY-NC, không dùng thương mại được.
- **SAM-Audio**: đã có nghiên cứu báo làm WER tăng; model nặng và cần GPU.
- **Resemble Enhance**: chỉ chạy batch ở 44.1 kHz, không có bất kỳ số liệu nào.

## Cách đặt vào pipeline
```
mic → AEC ─┬→ [DPDFNet / FastEnhancer] → Silero VAD → turn/barge-in
           └→ (mặc định: không enhance) → ASR
```
Chỉ cho audio đã khử nhiễu vào ASR khi A/B chứng minh WER giảm. Nếu có thử, nên thêm biến thể **trộn dry/wet** (ví dụ 70% audio đã khử nhiễu + 30% audio gốc) hoặc giới hạn mức suy giảm. Đây là giả thuyết của tôi, các nguồn chưa kiểm chứng.

## Cách đo
1. **WER/CER tiếng Việt** ở SNR 0/5/10/20 dB, với nhiễu quán café, xe máy, TV, có và không khử nhiễu.
2. **Nhánh VAD**: tỷ lệ ngắt nhầm (false-interruption), tỷ lệ cắt nhầm khi người dùng chưa nói xong (false-cutoff), và độ trễ endpoint.
3. **RTF và độ trễ** trên đúng phần cứng sẽ triển khai. MACs không dự đoán được tốc độ thật.
4. **Chạy liên tục 10–30 phút** để phát hiện lỗi trôi trạng thái hoặc cắt mất tiếng nói của các mô hình RNN.

**Tóm lại:** dùng DPDFNet-2 cho nhánh VAD, FastEnhancer-B làm phương án nhẹ hơn, và RNNoise/DeepFilterNet 3 làm baseline. ASR mặc định nhận audio gốc cho đến khi A/B tiếng Việt chứng minh điều ngược lại.

Bạn có muốn tôi lưu kế hoạch thử nghiệm này vào wiki (cập nhật trang [Speech Enhancement Before ASR](wiki/speech-enhancement-before-asr.md) hoặc tạo trang mới) không?