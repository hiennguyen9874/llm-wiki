# Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt

> **Loại tài liệu:** đề cương học tập (deliverable trong `outputs/`, không phải tri thức canonical).
> **Ngày:** 2026-10-07.
> **Mục đích:** hệ thống hoá những kiến thức cần nắm trước khi implement pipeline trong [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md). Tài liệu này chỉ liệt kê và chia chương. Mỗi chương sẽ được viết chi tiết riêng sau.
> **Cơ sở:** tài liệu thiết kế nói trên, các trang wiki liên quan, và kiến thức nền chung về xử lý tín hiệu, ngữ âm và ML. Phần kiến thức chung là giáo trình chuẩn, không phải claim lấy từ nguồn trong wiki.

---

## 0. Cách dùng đề cương

### 0.1 Cấu trúc mỗi chương

Mỗi chương có 5 mục:

- **Mục tiêu:** học xong thì làm được gì.
- **Câu hỏi phải trả lời được:** dùng để tự kiểm tra.
- **Nội dung:** danh sách chủ đề cần viết.
- **Gắn với pipeline:** chương này phục vụ phần nào của tài liệu thiết kế (§).
- **Đọc thêm trong wiki:** trang wiki làm điểm xuất phát.

### 0.2 Mức ưu tiên

- 🔴 **Bắt buộc:** thiếu thì không implement được, hoặc sẽ gặp bug khó tìm.
- 🟡 **Nên biết:** cần để tune, đo và chọn model đúng.
- 🟢 **Nâng cao:** cần khi tối ưu, mở rộng hoặc fine-tune.

### 0.3 Bản đồ toàn cục

```text
PHẦN I   Âm thanh & tín hiệu số      Ch.1 Vật lý tiếng nói → Ch.2 Số hoá → Ch.3 Định dạng/codec → Ch.4 DSP & đặc trưng
PHẦN II  Ngôn ngữ                     Ch.5 Ngữ âm & chữ viết tiếng Việt
PHẦN III Audio I/O realtime           Ch.6 Capture/playback → Ch.7 Echo/noise front-end → Ch.8 Transport mạng
PHẦN IV  Model: input/output          Ch.9 Nền ML cho speech → Ch.10 VAD & turn → Ch.11 ASR → Ch.12 LLM trong voice loop
                                      → Ch.13 TTS → Ch.14 Speaker (embedding, diarization)
PHẦN V   Ghép pipeline                Ch.15 Kiến trúc cascade vs E2E → Ch.16 Dataflow & audio contract
                                      → Ch.17 Turn-taking & cancellation → Ch.18 Lập trình async/streaming → Ch.19 Cầu text→speech
PHẦN VI  Đo lường & vận hành          Ch.20 Latency → Ch.21 Đánh giá chất lượng → Ch.22 Runtime & triển khai → Ch.23 License, privacy, bảo mật
Phụ lục                               A. Glossary  B. Công cụ thực hành  C. Ma trận chương ↔ tài liệu thiết kế
```

### 0.4 Thứ tự học đề xuất

```text
Lộ trình tối thiểu trước MVP (Profile A):
  1 → 2 → 3 → 4 (phần cơ bản) → 5 → 6 → 9 (phần cơ bản) → 10 → 11 → 13 → 16 → 17 → 18 → 19 → 20

Học song song hoặc sau MVP:
  7, 8 (WebRTC), 12, 14, 15, 21, 22, 23
```

---

# PHẦN I — ÂM THANH VÀ TÍN HIỆU SỐ

## Chương 1. Vật lý âm thanh và cơ chế tạo tiếng nói 🔴

**Mục tiêu:** hiểu tiếng nói là tín hiệu gì, để đọc được waveform và spectrogram và hiểu vì sao model dùng các đặc trưng đó.

**Câu hỏi phải trả lời được**

- Tần số, biên độ, pha khác nhau thế nào? dB là thang gì?
- Vì sao điện thoại 8 kHz vẫn nghe hiểu được, nhưng ASR lại kém hơn?
- F0, formant và thanh điệu liên quan với nhau thế nào?

**Nội dung**

- Sóng âm: áp suất, tần số (Hz), chu kỳ, biên độ, pha, bước sóng.
- Thang đo: dB, dBFS, SPL, loudness (LUFS), RMS.
- Mô hình source–filter: dây thanh (nguồn) và ống thanh quản (bộ lọc).
- Âm hữu thanh và vô thanh (voiced/unvoiced), âm xát, âm tắc.
- Tần số cơ bản F0 (pitch) và formant F1/F2/F3.
- Dải tần tiếng nói: năng lượng chính ~100 Hz–4 kHz, phụ âm xát lên tới 8 kHz trở lên. Băng hẹp (narrowband) và băng rộng (wideband).
- Âm học phòng: reverberation, far-field và near-field, nhiễu nền (stationary và non-stationary).
- SNR: định nghĩa và cách trộn nhiễu theo SNR mục tiêu.

**Gắn với pipeline:** §5.1 (telephony 8 kHz), §5.2 (`speech_pad_ms` giữ phụ âm), §10 (corpus SNR 0/5/10/20 dB).

**Đọc thêm trong wiki:** [Speech Enhancement Before ASR](../wiki/speech-enhancement-before-asr.md).

---

## Chương 2. Số hoá âm thanh: từ sóng tới mảng số 🔴

**Mục tiêu:** biết chính xác một buffer audio chứa gì và tính toán được kích thước, thời lượng, sample rate.

**Câu hỏi phải trả lời được**

- 1 giây PCM16 mono 16 kHz nặng bao nhiêu byte? Cùng thời lượng đó ở 48 kHz stereo float32 thì sao?
- 512 samples ở 16 kHz là bao nhiêu ms? 20 ms ở 48 kHz là bao nhiêu samples?
- Upsample 8 kHz lên 16 kHz có khôi phục được thông tin không? Vì sao?
- Đọc int16 thành float32 mà quên chia 32768 thì chuyện gì xảy ra?

**Nội dung**

- Sampling: sample rate, định lý Nyquist–Shannon, aliasing, lọc anti-alias.
- Quantization: bit depth, sai số lượng tử, dynamic range (~6 dB mỗi bit), dither.
- Clipping và headroom.
- Biểu diễn mẫu:
  - Integer PCM: int16/int24/int32.
  - Float32 trong khoảng [-1, 1].
  - Quy đổi int16 ↔ float32.
  - Endianness (`s16le`), signed và unsigned.
- Kênh: mono, stereo, interleaved và planar, downmix/upmix.
- Đơn vị thời gian: sample, frame (theo nghĩa audio API và theo nghĩa DSP), chunk, block, buffer. Công thức quy đổi ms ↔ samples ↔ bytes.
- Resampling:
  - Tỉ lệ nguyên và phân số, bộ lọc polyphase/sinc, chất lượng và độ trễ.
  - Thư viện: soxr, libsamplerate, torchaudio, ffmpeg.
  - Resample stream (có state) khác resample cả file.
- Bảng sample rate gặp trong pipeline: mic 44.1/48 kHz, ASR 16 kHz, telephony 8 kHz, TTS 22.05/24/48 kHz, Opus 48 kHz.
- Lỗi kinh điển: lệch sample rate, sai dtype, sai số kênh, đọc header WAV như audio.

**Gắn với pipeline:** §3 nguyên tắc 4 (audio contract), §5.1 (lỗi lệch sample rate), §7.1 (reblock 20 ms → 512 samples).

**Đọc thêm trong wiki:** [Community STT-LLM-TTS Wiring](../wiki/community-stt-llm-tts-pipeline.md), [VieNeu OpenAI Speech API](../wiki/vieneu-tts-openai-speech-api.md), [Silero VAD](../wiki/silero-vad.md).

---

## Chương 3. Định dạng file, container và codec 🔴

**Mục tiêu:** decode và encode đúng mọi dạng audio mà các thành phần trao đổi với nhau.

**Câu hỏi phải trả lời được**

- Raw PCM, WAV và Opus khác nhau thế nào? Khi nào dùng loại nào?
- Vì sao stream WAV qua HTTP chunked thì header có thể sai độ dài?
- G.711 μ-law là gì? Vì sao phải decode trước rồi mới resample?

**Nội dung**

- Raw PCM: không có header. Metadata phải truyền qua kênh khác (cần một contract).
- WAV/RIFF: header, chunk `fmt`/`data`, WAV dùng khi streaming (độ dài không xác định).
- Codec lossless: FLAC.
- Codec lossy: MP3, AAC, Opus.
  - Opus: frame 2.5–60 ms, 48 kHz nội bộ, có FEC và PLC.
- Codec thoại: G.711 μ-law/A-law (8 kHz, 8 bit companding), G.722.
- Đóng gói trên mạng: binary frame, base64 (tốn thêm ~33%), SSE, HTTP chunked transfer, multipart upload.
- Công cụ decode: ffmpeg, libsndfile/soundfile, PyAV. Decode stream khác decode file.
- Neural audio codec (giới thiệu, chi tiết ở Ch.13): EnCodec/DAC/MOSS/Mimi, token rời rạc ở 12.5–75 Hz.

**Gắn với pipeline:** §3 nguyên tắc 4 (VieNeu `float32`/`s16le` 48 kHz, Higgs SSE base64 WAV), §5.1 (WebRTC Opus và WS PCM16).

**Đọc thêm trong wiki:** [VieNeu OpenAI Speech API](../wiki/vieneu-tts-openai-speech-api.md), [Speech-to-Speech OpenAI-Compatible Backends](../wiki/speech-to-speech-openai-compatible-backends.md), [Qwen3-TTS Tokenizer 12Hz](../wiki/qwen3-tts-tokenizer-12hz.md).

---

## Chương 4. DSP cho tiếng nói và đặc trưng đầu vào model 🔴 (phần cơ bản) / 🟡 (phần sâu)

**Mục tiêu:** hiểu model "nhìn" audio như thế nào. Từ waveform ra log-mel, và vì sao kích thước chunk của VAD, ASR, TTS lại khác nhau.

**Câu hỏi phải trả lời được**

- STFT với window 25 ms, hop 10 ms ở 16 kHz cho ra bao nhiêu frame mỗi giây? Mỗi frame có bao nhiêu bin?
- Whisper nhận input gì: số mel bins, cửa sổ 30 s, padding? Vì sao clip ngắn hoặc im lặng dễ sinh hallucination?
- Spectrogram của 6 thanh tiếng Việt khác nhau ở đâu?

**Nội dung**

- Framing, windowing (Hann/Hamming), overlap, hop size.
- Fourier: DFT/FFT, phổ biên độ và phổ pha, độ phân giải thời gian–tần số.
- STFT và spectrogram. Đọc spectrogram thực hành: formant, pitch harmonics, khoảng lặng, nhiễu.
- Mel scale, mel filterbank, log-mel (80/128 bins), MFCC, CMVN, pre-emphasis.
- Đặc trưng đơn giản: energy/RMS, zero-crossing rate, pitch tracking (F0).
- Lọc: low-pass, high-pass, band-pass. Bộ lọc FIR và IIR (mức khái niệm).
- Đầu vào cụ thể của các model trong pipeline:
  - Silero VAD: waveform, cửa sổ 512 samples ở 16 kHz.
  - Whisper: log-mel, 30 s, padding.
  - Smart Turn: Whisper Tiny encoder trên đoạn audio cuối lượt.
  - Conformer/FastConformer: mel + subsampling (8×).
- Liên hệ: frame rate của encoder → độ phân giải thời gian → chunk size và lookahead của ASR streaming.
- (Nâng cao) Inverse STFT, Griffin-Lim, vì sao cần vocoder (dẫn sang Ch.13).

**Gắn với pipeline:** §5.2, §5.3, §5.4.1, §7.1.

**Đọc thêm trong wiki:** [Whisper Large v3](../wiki/whisper-large-v3.md), [Smart Turn v3.2](../wiki/smart-turn.md), [Nemotron 3.5 ASR Streaming](../wiki/nemotron-3.5-asr-streaming-0.6b.md).

---

# PHẦN II — NGÔN NGỮ

## Chương 5. Ngữ âm, chữ viết và văn bản tiếng Việt 🔴

**Mục tiêu:** hiểu những đặc thù tiếng Việt làm ASR, TTS và đánh giá khó hơn tiếng Anh.

**Câu hỏi phải trả lời được**

- Vì sao CER và WER trên tiếng Việt cho kết quả khác nhau? Một "từ" tiếng Việt là âm tiết hay từ ghép?
- Vì sao cắt mất 50 ms đầu hoặc cuối âm tiết có thể làm sai thanh?
- `ộ` dạng NFC và NFD khác nhau thế nào khi so sánh chuỗi hoặc tính WER?

**Nội dung**

- Cấu trúc âm tiết: âm đầu, âm đệm, âm chính, âm cuối, thanh.
- Hệ 6 thanh: đường nét F0, độ dài, chất giọng (thanh hỏi/ngã, glottalization). Ảnh hưởng lên VAD padding và chunk TTS.
- Phương ngữ Bắc, Trung, Nam: khác biệt về âm đầu, vần, thanh (ví dụ hỏi/ngã ở miền Nam). Ảnh hưởng lên WER.
- Chữ Quốc ngữ và Unicode: dấu tổ hợp, NFC/NFD, kiểu bỏ dấu cũ và mới (`hoà`/`hòa`), chuẩn hoá trước khi so sánh.
- Ranh giới từ: âm tiết và từ, word segmentation, ảnh hưởng lên tokenization và WER.
- Code-switch Việt–Anh, tên riêng, từ mượn.
- Văn bản viết khác văn bản nói:
  - Số, tiền, ngày giờ, đơn vị, viết tắt, số điện thoại.
  - TN (text normalization, phía TTS) và ITN (inverse text normalization, phía ASR).
- G2P tiếng Việt: chữ viết gần với âm, nhưng vẫn có ngoại lệ (tên riêng, từ mượn, phương ngữ). Lexicon.
- Đặc điểm hội thoại: backchannel ("ừ", "vâng", "dạ"), từ đệm, câu ngắn, ngắt quãng giữa câu.

**Gắn với pipeline:** §5.2 (`speech_pad_ms` cho thanh điệu), §5.4.2 (bẫy so sánh WER), §5.5 (normalizer, lexicon), §7.3 (backchannel), §10 (corpus giọng ba miền).

**Đọc thêm trong wiki:** [Vietnamese Realtime ASR Selection](../wiki/vietnamese-realtime-asr-selection.md), [Vietnamese Realtime TTS Selection](../wiki/vietnamese-realtime-tts-selection.md), [Kokoro Vietnamese](../wiki/kokoro-vietnamese.md) (vig2p).

---

# PHẦN III — AUDIO I/O REALTIME

## Chương 6. Capture và playback realtime 🔴

**Mục tiêu:** đưa audio từ mic vào code và từ code ra loa không giật, không trễ, không lệch.

**Câu hỏi phải trả lời được**

- Vì sao playback phải có queue? Underrun và overrun là gì?
- Pre-buffer 150–300 ms đổi lại được gì và mất gì?
- Làm sao flush ngay audio đang phát khi user ngắt lời?

**Nội dung**

- Audio API: Web Audio (getUserMedia, AudioContext, AudioWorklet), PortAudio/sounddevice (Python). Sample rate của thiết bị.
- Buffer và độ trễ thiết bị: buffer size, latency của input và output.
- Ring buffer, jitter buffer, bounded queue.
- Underrun, overrun, clock drift giữa thiết bị và nguồn.
- Playback: queue theo `generation_id`, pre-buffer, flush/clear, cross-fade tránh tiếng "click".
- Đo phía client: timestamp lúc capture, thời điểm phát mẫu đầu tiên, `played_sample_offset`.

**Gắn với pipeline:** §4 (client, AudioWorklet), §7.2 (`audio.played`), §7.3 (`client.clear`), §8.3 (playback buffer).

**Đọc thêm trong wiki:** [Speech-to-Speech Browser Demo](../wiki/speech-to-speech-browser-demo.md), [VieNeu Streaming Runtime](../wiki/vieneu-tts-streaming-runtime.md).

---

## Chương 7. Front-end âm học: echo, nhiễu, gain 🟡

**Mục tiêu:** hiểu AEC, NS, AGC làm gì, đặt chúng ở đâu, và vì sao không đưa audio đã denoise vào ASR.

**Câu hỏi phải trả lời được**

- AEC cần tín hiệu tham chiếu nào? Double-talk là gì?
- Vì sao denoise có thể làm WER tệ hơn?
- Ba tầng xử lý echo (tắt mic, AEC trình duyệt, AEC WebRTC + so sánh tín hiệu) khác nhau thế nào?

**Nội dung**

- Acoustic echo: đường loa → mic, tín hiệu tham chiếu, adaptive filter (khái niệm).
- AEC trong trình duyệt và WebRTC (`echoCancellation`, `noiseSuppression`, `autoGainControl`).
- Noise suppression và speech enhancement: RNNoise, DeepFilterNet. Artifact và ảnh hưởng lên ASR.
- AGC, chuẩn hoá loudness, clipping khi tăng gain.
- Chiến lược hai nhánh: nhánh VAD/barge-in có thể denoise, nhánh ASR giữ audio AEC gốc.
- Ngưỡng thích ứng theo nền nhiễu (đo trong 2–3 s đầu).

**Gắn với pipeline:** §3 nguyên tắc 3, §5.1, §5.2 (ngưỡng thích ứng), §11 (mâu thuẫn về enhancement).

**Đọc thêm trong wiki:** [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md), [Speech Enhancement Before ASR](../wiki/speech-enhancement-before-asr.md).

---

## Chương 8. Transport mạng cho audio realtime 🟡 (WebSocket 🔴)

**Mục tiêu:** chọn và implement đúng kênh truyền audio hai chiều.

**Câu hỏi phải trả lời được**

- Vì sao gửi binary frame thay vì base64?
- WebRTC giải quyết những gì mà WebSocket không làm (packet loss, jitter, NAT, AEC)?
- Backpressure trên WebSocket xử lý thế nào khi client chậm?

**Nội dung**

- TCP và UDP, head-of-line blocking, ảnh hưởng lên audio realtime.
- WebSocket: binary và text frame, framing 20–32 ms, ping/keepalive, backpressure, reconnect.
- WebRTC: ICE/STUN/TURN, SRTP, Opus, jitter buffer, PLC/FEC, DataChannel. SFU (LiveKit, Daily) và peer-to-peer.
- HTTP streaming: chunked transfer, SSE, cancel request (đóng connection).
- Telephony: SIP, 8 kHz, G.711 (mức khái niệm).
- Giao thức tầng ứng dụng: OpenAI Realtime API events, `/v1/audio/speech`, `/v1/audio/transcriptions`. Thế nào thì gọi là "OpenAI-compatible".

**Gắn với pipeline:** §5.1, §5.7 (Realtime subset, giao thức NeMo-Speech.cpp khác OpenAI Realtime), §9.5.

**Đọc thêm trong wiki:** [Speech-to-Speech Realtime Engine](../wiki/speech-to-speech-realtime-engine.md), [NeMo-Speech.cpp HTTP and Realtime API](../wiki/nemo-speech-http-api.md), [Voice Agent Frameworks](../wiki/voice-agent-frameworks.md).

---

# PHẦN IV — CÁC TẦNG MODEL: INPUT VÀ OUTPUT

## Chương 9. Nền tảng ML cho speech, đủ để đọc model card 🔴 (cơ bản) / 🟢 (sâu)

**Mục tiêu:** đọc hiểu kiến trúc, kích thước, chế độ decode và yêu cầu tài nguyên của các model speech.

**Câu hỏi phải trả lời được**

- CTC, RNN-T/TDT và attention encoder-decoder (Whisper) khác nhau thế nào? Loại nào streaming tự nhiên?
- "Cache-aware streaming" nghĩa là gì?
- Model 0.6B ở BF16 cần khoảng bao nhiêu VRAM cho weights? Ngoài weights còn cần gì?

**Nội dung**

- Khối kiến trúc: CNN subsampling, Transformer, Conformer/FastConformer, attention, causal và non-causal, lookahead.
- Họ ASR:
  - CTC.
  - Transducer (RNN-T, TDT).
  - Attention encoder-decoder (Whisper).
  - LLM-based ASR (audio encoder → projector → LLM decoder, ví dụ Qwen3-ASR).
- Tokenization: BPE/SentencePiece, token đặc biệt (language, timestamp, task).
- Decoding: greedy, beam search, temperature fallback, hotword/context biasing, language model fusion.
- Khái niệm streaming ở mức model: chunked attention, cache encoder/decoder, latency do lookahead.
- Độ chính xác số và lượng tử hoá: fp32/fp16/bf16/int8/int4, GGUF/ggml, `int8_float16`.
- Tài nguyên: params × bytes, KV cache, activation, batch, CUDA graph, warmup.
- Đọc model card: language list, license, benchmark nào, giao thức đo nào.

**Gắn với pipeline:** §5.4, §5.6, §5.8, §9.2.

**Đọc thêm trong wiki:** [ASR/STT Model Survey](../wiki/asr-stt-model-survey.md), [Phân nhóm ASR/STT và shortlist realtime](../wiki/realtime-asr-selection.md), [TTS Model Survey](../wiki/tts-model-survey.md).

---

## Chương 10. VAD, endpointing và turn detection 🔴

**Mục tiêu:** biết khi nào user đang nói, khi nào user đã nói xong, và ai là người quyết định.

**Câu hỏi phải trả lời được**

- Input và output của Silero VAD là gì? State của nó nằm ở đâu?
- `threshold`, `min_silence_duration_ms`, `min_speech_duration_ms`, `speech_pad_ms` mỗi cái tác động thế nào?
- VAD (âm học) khác semantic turn detection thế nào? FPR/FNR của Smart Turn trên tiếng Việt có ý nghĩa gì với trải nghiệm?

**Nội dung**

- VAD: xác suất theo frame, threshold, hysteresis, smoothing, state machine speech/silence.
- Tham số endpoint: min speech, min silence, padding, pre-roll, timeout.
- Hai triết lý: commit cứng sau timeout, và speculative + revision (`LISTENING → SOFT_ENDED → ANSWERING → CLOSED`).
- Semantic/prosodic EOU: Smart Turn (input là audio cuối lượt, output là xác suất complete), Namo, LiveKit.
- Ma trận nhầm lẫn: accuracy, FPR (cắt ngang lời user) và FNR (chờ quá lâu). Đánh đổi bằng threshold.
- VAD trên kênh có echo: bot tự kích hoạt barge-in.
- Phân biệt VAD dùng làm filter cho ASR (`vad_filter` của faster-whisper) với VAD dùng điều khiển lượt nói.

**Gắn với pipeline:** §5.2, §5.3, §7.1, §11.

**Đọc thêm trong wiki:** [Silero VAD](../wiki/silero-vad.md), [Smart Turn v3.2](../wiki/smart-turn.md), [Turn Detection Models](../wiki/turn-detection-models.md), [Speech-to-Speech CLI and Defaults](../wiki/speech-to-speech-cli-and-defaults.md).

---

## Chương 11. ASR: hợp đồng input/output và hành vi streaming 🔴

**Mục tiêu:** dùng ASR như một thành phần có contract rõ ràng: vào gì, ra gì, khi nào ra, tin được tới đâu.

**Câu hỏi phải trả lời được**

- Input chuẩn là gì (16 kHz mono float32)? Output gồm những gì (text, segment, timestamps, `avg_logprob`, `no_speech_prob`, language)?
- Partial, stable prefix và final khác nhau thế nào? Vì sao không hành động trên partial?
- Ba nghĩa của "realtime" (native, buffered, turn-final) là gì? RTF < 1 có nghĩa là "có text sớm" không?
- Whisper hallucinate trong điều kiện nào? Lọc bằng tín hiệu gì?

**Nội dung**

- Contract: audio vào, text và metadata ra. Ép ngôn ngữ (`language="vi"`, `vi-VN`) và rủi ro của auto LangID.
- Streaming taxonomy: native cache-aware, buffered/policy, turn-final. Chunk size, lookahead, first partial, first stable text.
- Revision và stable prefix. Two-pass (partial + final-pass) và cách reconcile.
- Chất lượng output: punctuation, casing, ITN, hotwords/initial prompt.
- Hallucination: nguyên nhân (im lặng, nhạc, prompt), cờ decode, filter sau decode, blacklist tiếng Việt.
- Confidence: không được calibrate giữa các model. Dùng "unknown" khi thiếu.
- Metric: WER/CER, normalizer khi đánh giá, RTF và RTFx, TTFT và độ trễ thực từ mic.
- Bẫy benchmark: tập dữ liệu khác nhau, giao thức offline và streaming khác nhau, concurrency khác nhau.

**Gắn với pipeline:** §5.4 (toàn bộ), §6, §7.2.

**Đọc thêm trong wiki:** [Vietnamese Realtime ASR Selection](../wiki/vietnamese-realtime-asr-selection.md), [Faster-Whisper](../wiki/faster-whisper.md), [Whisper Hallucination Mitigation](../wiki/whisper-hallucination-mitigation.md), [Qwen3-ASR family](../wiki/qwen3-asr-family.md), [Community Usable STT for Voice Agents](../wiki/community-usable-stt-voice-agents.md).

---

## Chương 12. LLM trong vòng hội thoại nói 🟡

**Mục tiêu:** nối LLM vào pipeline như một streaming text service có thể huỷ, không đi sâu vào việc chọn model.

**Câu hỏi phải trả lời được**

- TTFT là gì? Vì sao chỉ cần "mệnh đề có nghĩa đầu tiên" chứ không cần cả câu trả lời?
- Prompt cho câu trả lời để đọc khác prompt cho câu trả lời để hiển thị ra sao?
- Khi bị ngắt lời, history nên lưu gì?

**Nội dung**

- API streaming kiểu OpenAI-compatible: SSE token, `done`, `error`, cancel bằng cách đóng stream.
- TTFT, tokens/s, prefix cache cho system prompt.
- Prompt cho hội thoại nói: câu ngắn, không markdown/emoji/URL, hỏi lại khi không chắc, tắt thinking.
- Quản lý history: chỉ lưu phần đã phát, tag `[bị ngắt]`, transcript revision.
- Speculative generation trên partial và discard khi revision đổi.
- Tool call và side effect chỉ chạy sau commit.
- Contention GPU khi LLM chạy chung máy với ASR/TTS.

**Gắn với pipeline:** §5.5 (giao diện LLM), §7.3, §8.1, §8.3.

**Đọc thêm trong wiki:** [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md), [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md).

---

## Chương 13. TTS: từ văn bản tới waveform 🔴

**Mục tiêu:** hiểu chuỗi xử lý bên trong TTS hiện đại, contract input/output và hai nghĩa của "streaming TTS".

**Câu hỏi phải trả lời được**

- Text đi qua những bước nào để thành mẫu audio: normalization → G2P → acoustic model → vocoder hoặc codec decoder?
- Neural codec token ở 12.5 Hz nghĩa là gì? TTFA phụ thuộc vào đâu?
- Audio-output streaming khác incremental text-input (bi-streaming) thế nào?
- TTS trả 48 kHz float32, pipeline cần 16 kHz int16. Chuyển đổi ở đâu, và mất gì?

**Nội dung**

- Pipeline cổ điển: text frontend → acoustic model (mel) → vocoder (HiFi-GAN…).
- TTS dựa trên LLM/codec: text → token codec rời rạc (RVQ, nhiều codebook) → codec decoder → waveform.
- Các họ khác: non-autoregressive, flow matching, diffusion. Đánh đổi chất lượng, tốc độ và khả năng streaming.
- Điều khiển: preset voice, voice cloning (reference audio + transcript, speaker embedding), prosody, tốc độ, pause.
- Output contract: sample rate, kênh, dtype, kích thước chunk, framing (pcm/wav/SSE), tín hiệu kết thúc, cancel.
- Streaming: audio-output streaming và bi-streaming. TTFA, RTF một stream và RTF throughput batch. Số stream đồng thời.
- Vận hành: warmup, CUDA graph, idle clock-down, giới hạn stream (429).
- Chất lượng: MOS/CMOS, round-trip CER (chỉ là proxy), lỗi phát âm và thanh điệu, tính nhất quán giọng giữa các chunk.

**Gắn với pipeline:** §5.5, §5.6, §8.2, §9.4.

**Đọc thêm trong wiki:** [Vietnamese Realtime TTS Selection](../wiki/vietnamese-realtime-tts-selection.md), [VieNeu-TTS v3 Turbo](../wiki/vieneu-tts-v3-turbo.md), [VieNeu Streaming Runtime](../wiki/vieneu-tts-streaming-runtime.md), [TTS Model Survey](../wiki/tts-model-survey.md), [Qwen3-TTS Tokenizer 12Hz](../wiki/qwen3-tts-tokenizer-12hz.md).

---

## Chương 14. Speaker: embedding, speaker lock, diarization 🟢

**Mục tiêu:** biết khi nào cần nhận diện người nói và giới hạn của nó.

**Câu hỏi phải trả lời được**

- Speaker embedding (ECAPA, CAM++) là gì? Cosine similarity được dùng để làm gì?
- Vì sao speaker lock không phải là xác thực?
- DER đo gì? Khi nào diarizer nên nằm ngoài critical path?

**Nội dung**

- Speaker embedding, enrollment, cập nhật dần, calibrate ngưỡng.
- Speaker lock để chống barge-in nhầm (TV, người khác nói).
- Diarization: offline và streaming, arrival-order, DER. Track riêng theo participant khi có thể.
- Quyền riêng tư: embedding và reference giọng là dữ liệu sinh trắc học.

**Gắn với pipeline:** §7.3, §7.5, §9.5.

**Đọc thêm trong wiki:** [Nemotron 3 Diarization](../wiki/nemotron-3-diarization.md), [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md).

---

# PHẦN V — GHÉP PIPELINE: DỮ LIỆU ĐI NHƯ THẾ NÀO

## Chương 15. Kiến trúc: cascade, end-to-end full-duplex và lai 🟡

**Mục tiêu:** hiểu vì sao chọn cascade cho tiếng Việt, và khi nào nên xem lại quyết định đó.

**Câu hỏi phải trả lời được**

- Full-duplex speech-to-speech (Moshi-style) xử lý turn-taking khác cascade thế nào?
- Omni/audio-LLM ("direct audio input") bỏ được tầng nào, và đổi lại mất gì?

**Nội dung**

- Cascade VAD → turn → ASR → LLM → TTS: ưu điểm (kiểm soát, RAG/tool, thay từng phần) và nhược điểm (latency cộng dồn, mất thông tin cảm xúc và ngữ điệu).
- End-to-end full-duplex: dual-stream, tự turn-taking, giới hạn ngôn ngữ.
- Lai: audio-LLM nhận audio trực tiếp, omni model.
- Năm tầng tách biệt: model, runtime, API server, streaming policy, orchestration.

**Gắn với pipeline:** §2, §3 nguyên tắc 1.

**Đọc thêm trong wiki:** [PersonaPlex 7B](../wiki/personaplex-7b-v1.md), [NemotronLabs VoiceChat 11B](../wiki/nvidia-nemotronlabs-voicechat-11b.md), [Ultravox](../wiki/ultravox.md), [So sánh công cụ triển khai speech](../wiki/speech-deployment-tools-comparison.md).

---

## Chương 16. Dataflow end-to-end và audio contract 🔴

**Mục tiêu:** lần theo một khung audio từ mic tới loa, biết tại mỗi cạnh dữ liệu có dạng gì, kích thước bao nhiêu, ai sở hữu nó.

**Câu hỏi phải trả lời được**

- Vẽ được sơ đồ: tại mỗi cạnh là sample rate nào, dtype nào, chunk bao nhiêu ms, ai giữ state?
- Vì sao VAD (32 ms), transport (20 ms), ASR (160–320 ms), text (theo mệnh đề) và TTS (chunk audio) dùng đơn vị khác nhau, và nối với nhau ra sao?
- Pre-roll lấy từ đâu? Turn audio buffer giữ bao lâu?

**Nội dung**

- Sơ đồ luồng: client → transport → decode → resample → ring buffer → các nhánh (VAD, ASR streaming, turn buffer) → transcript → LLM → chunker → normalizer → TTS → adapter → client queue.
- Bảng audio contract cho từng cạnh: format, rate, channels, dtype, framing, cancel.
- Reblocking và buffering: ring buffer, pre-roll 200–300 ms, turn audio buffer, giải phóng bộ nhớ.
- Timeline và timestamps: sample index và wall clock, sequence number, xử lý gap hoặc packet thiếu.
- State theo session: VAD state, ASR cache, history. Không bao giờ dùng chung giữa các user.
- Định danh: `session_id`, `turn_id`, `revision`, `generation_id`, `chunk_id`, `sequence`.
- Tại sao trần băng thông của pipeline có thể bị khoá ở 16 kHz (ví dụ HF s2s `--tts openai`).

**Gắn với pipeline:** §3 nguyên tắc 4, §4, §7.1, §7.2.

**Đọc thêm trong wiki:** [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md), [HF Speech-to-Speech Pipeline](../wiki/speech-to-speech-pipeline.md), [Cascaded Voice-Agent Blueprint](../wiki/cascaded-voice-agent-blueprint.md).

---

## Chương 17. Turn-taking, event, barge-in và cancellation 🔴

**Mục tiêu:** thiết kế bộ điều khiển lượt nói: một owner duy nhất, có revision, huỷ được sạch.

**Câu hỏi phải trả lời được**

- Ai được phép close, reopen, commit một lượt? Vì sao chỉ một owner?
- Trình tự barge-in gồm những bước nào? Làm sao đảm bảo không còn chunk audio cũ nào được phát?
- Thế nào là "chỉ hành động trên văn bản đã commit"?

**Nội dung**

- State machine của lượt nói, speculative reopen, revision.
- Event schema: `asr.partial/final`, `turn.commit`, `text.chunk`, `audio.start/chunk/played`, `response.cancel`, `client.clear`.
- `generation_id` và chống dữ liệu cũ (stale). Thứ tự và tính đơn điệu của sequence.
- Barge-in: duration gate, threshold theo nhiễu, speaker lock, quick ASR, backchannel.
- Cancellation xuyên tầng: LLM, TTS, queue, client. Thời gian tới khi âm thanh dừng và thời gian giải phóng compute.
- Cắt history theo phần đã phát (`conversation.item.truncate`, played offset).
- Kết thúc session: giải phóng cache, bỏ callback đến trễ.

**Gắn với pipeline:** §3 nguyên tắc 2 và 5, §5.3, §7.2–7.4.

**Đọc thêm trong wiki:** [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md), [Speech-to-Speech Realtime Engine](../wiki/speech-to-speech-realtime-engine.md).

---

## Chương 18. Lập trình async và streaming cho pipeline audio 🔴

**Mục tiêu:** viết được code đồng thời không block event loop, có backpressure và huỷ đúng cách.

**Câu hỏi phải trả lời được**

- Vì sao lặp generator của faster-whisper trên event loop làm đứng cả pipeline?
- Bounded queue và backpressure ngăn được lỗi gì?
- Huỷ một task đang chờ I/O khác gì huỷ một inference đang chạy trên GPU?

**Nội dung**

- asyncio: task, queue, cancellation, timeout, TaskGroup/CancelScope.
- Code CPU-bound và GPU-bound: `asyncio.to_thread`, process pool, worker service riêng.
- Producer/consumer, bounded queue, backpressure, drop policy cho audio realtime.
- Streaming I/O: async generator, iterator cho HTTP/SSE/WS, đóng connection để huỷ.
- Cadence và throughput: ưu tiên nhịp audio đều hơn batch lớn.
- Admission control, 429, circuit breaker, deadline theo session.
- Test: replay file audio theo thời gian thực, giả lập jitter và disconnect.

**Gắn với pipeline:** §5.4.4 (`asyncio.to_thread`), §7.4, §9.1, §9.3, §10 mục 5.

**Đọc thêm trong wiki:** [Whisper Hallucination Mitigation](../wiki/whisper-hallucination-mitigation.md), [Speech-to-Speech Realtime Engine](../wiki/speech-to-speech-realtime-engine.md), [Voice Agent Frameworks](../wiki/voice-agent-frameworks.md).

---

## Chương 19. Cầu text → speech: chunker, normalizer, lexicon 🔴

**Mục tiêu:** biến token stream của LLM thành các đoạn văn bản đọc được, để TTS bắt đầu sớm mà vẫn giữ ngữ điệu.

**Câu hỏi phải trả lời được**

- Flush theo token, theo mệnh đề hay theo câu? Mỗi cách đánh đổi gì?
- Vì sao phải tách text hiển thị và text để đọc?
- Normalizer tiếng Việt xử lý số, tiền, ngày, viết tắt, code-switch thế nào?

**Nội dung**

- Clause chunker: quy tắc theo dấu câu, ngưỡng ký tự cho chunk đầu, gộp mảnh ngắn.
- Text normalization tiếng Việt: Unicode NFC, số, tiền, ngày giờ, đơn vị, số điện thoại, viết tắt, URL, markup.
- Lexicon và substitution dictionary cho tên riêng, thuật ngữ.
- Code-switch: giữ nguyên hay phiên âm.
- Bộ regression prompts cho normalizer và TTS.

**Gắn với pipeline:** §5.5, §8.1 (chunker nằm ở consumer của LLM stream).

**Đọc thêm trong wiki:** [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md), [Cascaded Voice-Agent Blueprint](../wiki/cascaded-voice-agent-blueprint.md), [Community STT-LLM-TTS Wiring](../wiki/community-stt-llm-tts-pipeline.md).

---

# PHẦN VI — ĐO LƯỜNG VÀ VẬN HÀNH

## Chương 20. Latency: định nghĩa, critical path, đo lường 🔴

**Mục tiêu:** đo đúng và không cộng nhầm các con số khác loại.

**Câu hỏi phải trả lời được**

- Voice-to-voice latency bắt đầu từ đâu, kết thúc ở đâu? Đo ở client hay server?
- Vì sao các stage chạy chồng lấn thì không cộng được với nhau? Output gate quyết định latency khi nào?
- TTFT, TTFA, RTF, RTFx, first partial, first stable text, endpoint→final: định nghĩa của từng cái?

**Nội dung**

- Critical path từ mẫu speech cuối của user tới mẫu audio đầu tiên nghe được.
- Ngân sách latency theo stage. Đọc ngân sách tham khảo một cách phê phán.
- Công thức có output-hold: `max(output-hold, ASR + LLM)`.
- Phân vị P50/P95/P99, warm và cold, theo concurrency.
- Đồng bộ đồng hồ client/server, join log theo các ID.
- Đòn bẩy tối ưu: warmup, resident model, prefix cache, preemptive ASR/LLM, clause chunking, playback buffer.

**Gắn với pipeline:** §3 nguyên tắc 6, §8.

**Đọc thêm trong wiki:** [Speech-to-Speech Latency Instrumentation](../wiki/speech-to-speech-latency-instrumentation.md), [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md).

---

## Chương 21. Đánh giá chất lượng và release gate 🟡

**Mục tiêu:** dựng được bộ đánh giá tiếng Việt cho ASR, TTS, turn-taking và contract.

**Câu hỏi phải trả lời được**

- Tính WER/CER thế nào cho đúng (alignment, normalizer, NFC)? Critical-span accuracy là gì?
- Thiết kế listening test MOS/CMOS ra sao cho có ý nghĩa thống kê?
- Đo false-cutoff và false-interrupt bằng cách nào?

**Nội dung**

- ASR: WER/CER (edit distance), normalizer khi đánh giá, độ chính xác số/tên/phủ định, tỉ lệ partial bị sửa, độ trễ.
- Corpus: giọng ba miền, 8 kHz và 16 kHz, far-field, trộn nhiễu theo SNR, im lặng/nhạc để đo hallucination.
- TTS: MOS, CMOS, blind pairwise, số người nghe, round-trip CER, test riêng thanh điệu.
- Turn và barge-in: kịch bản test, metric.
- Load test và contract test (sample rate, cancel, reconnect, 429).
- Nguyên tắc A/B: mỗi lần đổi một thành phần, cùng ground truth, cùng điều kiện.

**Gắn với pipeline:** §10, §12.

**Đọc thêm trong wiki:** [Community Usable STT for Voice Agents](../wiki/community-usable-stt-voice-agents.md), [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md).

---

## Chương 22. Runtime, serving và triển khai 🟡

**Mục tiêu:** chạy model ổn định và có thể đo được trên phần cứng thật.

**Câu hỏi phải trả lời được**

- PyTorch, ONNX Runtime, CTranslate2, vLLM, SGLang và ggml/GGUF khác nhau thế nào? Chọn cái nào cho tầng nào?
- Vì sao GGUF giữa các runtime không thay thế cho nhau được? Parity test là gì?
- Ước lượng VRAM cho ASR + TTS + LLM trên một GPU 12/24 GB thế nào?

**Nội dung**

- Runtime và định dạng weights. Lượng tử hoá và ảnh hưởng lên chất lượng.
- GPU: CUDA, VRAM, batching và continuous batching, CUDA graph, idle clock-down.
- CPU: ONNX, INT8/VNNI, thread.
- Serving: OpenAI-compatible endpoints, health và readiness sau warmup, giới hạn stream.
- Docker Compose, tách environment theo service, pin revision và checksum, pre-stage offline.
- Topology: gateway public, model service private, tách GPU theo service.
- Observability: log theo turn, metric, content-free logging.

**Gắn với pipeline:** §5.8, §6, §9.

**Đọc thêm trong wiki:** [So sánh công cụ triển khai speech](../wiki/speech-deployment-tools-comparison.md), [VieNeu-TTS Docker Deployment](../wiki/vieneu-tts-docker-deployment.md), [NeMo-Speech.cpp Server](../wiki/nemo-speech-server.md), [audio.cpp Framework](../wiki/audio-cpp-framework.md).

---

## Chương 23. License, privacy và bảo mật 🟡

**Mục tiêu:** không chọn nhầm thành phần mà sau này không dùng được, và không để lộ dữ liệu giọng nói.

**Câu hỏi phải trả lời được**

- License của runtime khác license của weights thế nào? NC, ND, GPL, OpenRAIL-M hạn chế những gì?
- Voice cloning cần consent gì?
- Log nào được phép chứa transcript hoặc audio?

**Nội dung**

- Các loại license: MIT, BSD, Apache, CC-BY, CC-BY-NC(-ND), GPL, OpenRAIL-M, license riêng của vendor. Lineage dữ liệu.
- License là hard gate, xét trước chất lượng.
- Privacy: audio, transcript, speaker embedding, reference giọng. Retention, consent, access control.
- Bảo mật: TLS, auth ở gateway, cổng model để private, giới hạn upload, proxy không có auth.

**Gắn với pipeline:** §3 nguyên tắc 7, §6 (Profile F), §9.5, §11.

**Đọc thêm trong wiki:** [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md), [VieNeu-TTS v3 Turbo](../wiki/vieneu-tts-v3-turbo.md).

---

# PHỤ LỤC

## A. Glossary cần có (viết dần cùng các chương)

| Nhóm | Thuật ngữ |
|---|---|
| Tín hiệu | sample, sample rate, bit depth, PCM, dBFS, RMS, SNR, Nyquist, aliasing, resampling, mono/stereo, interleaved |
| DSP | frame, window, hop, FFT, STFT, spectrogram, mel, log-mel, MFCC, F0, formant |
| Codec / transport | WAV, Opus, G.711, base64, SSE, chunked, WebSocket, WebRTC, jitter buffer, PLC, AEC, NS, AGC |
| Control | VAD, EOU, endpointing, turn, revision, commit, barge-in, backchannel, `generation_id`, pre-roll |
| ASR | CTC, RNN-T, TDT, AED, partial, stable prefix, final, LangID, hotword, ITN, hallucination, WER, CER |
| TTS | TN, G2P, lexicon, vocoder, neural codec, RVQ, voice cloning, prosody, TTFA, bi-streaming, MOS, CMOS |
| Hiệu năng | latency, TTFT, TTFA, RTF, RTFx, P95, throughput, concurrency, cadence, warmup, VRAM, quantization |

## B. Công cụ thực hành gợi ý cho từng chương

| Chương | Công cụ / bài tập ngắn |
|---|---|
| 1–4 | Audacity hoặc Sonic Visualiser (xem spectrogram), `ffmpeg`/`sox`, `numpy` + `soundfile` + `librosa`/`torchaudio`: ghi âm 6 thanh rồi so sánh F0 và spectrogram; resample 48k→16k→8k→16k và nghe lại |
| 3 | Tự viết/đọc header WAV; encode/decode Opus và μ-law; đo kích thước base64 |
| 6, 8 | AudioWorklet playback queue; WebSocket echo server gửi PCM16 20 ms |
| 10 | Chạy Silero VAD trên file có nhiễu, vẽ xác suất theo thời gian, thử thay đổi các tham số |
| 11 | faster-whisper `language="vi"` trên clip im lặng hoặc nhạc để quan sát hallucination; tính WER/CER bằng `jiwer` có và không có NFC |
| 13, 19 | Gọi VieNeu `/v1/audio/speech` ở chế độ stream, đo TTFA; đưa câu có số, tiền, viết tắt qua normalizer rồi nghe |
| 17, 18 | Mô phỏng barge-in: phát audio dài, ngắt giữa chừng, kiểm tra không còn chunk cũ |
| 20 | Gắn timestamp ở từng cạnh, vẽ waterfall latency cho một lượt |

## C. Ma trận chương ↔ tài liệu thiết kế

| § tài liệu thiết kế | Chương cần học trước |
|---|---|
| §2 Cascade hay E2E | 15 |
| §3 Nguyên tắc thiết kế | 2, 15, 16, 17, 20, 23 |
| §4 Kiến trúc tổng thể | 6, 7, 8, 16 |
| §5.1 Transport, AEC | 2, 3, 6, 7, 8 |
| §5.2 VAD | 4, 5, 10 |
| §5.3 Turn detection | 10, 17 |
| §5.4 ASR | 4, 5, 9, 11 |
| §5.5 Cầu text→speech | 5, 12, 19 |
| §5.6 TTS | 3, 9, 13 |
| §5.7–5.8 Orchestration, deploy | 8, 18, 22 |
| §6 Profiles | 9, 11, 13, 22, 23 |
| §7 Control contracts | 16, 17, 18 |
| §8 Latency | 20 |
| §9 Triển khai, privacy | 14, 22, 23 |
| §10 Đánh giá | 5, 21 |
| §11 Mâu thuẫn mở | 7, 10, 13, 23 |
