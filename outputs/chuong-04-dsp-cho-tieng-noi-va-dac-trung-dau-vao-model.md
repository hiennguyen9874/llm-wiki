# Chương 4. DSP cho tiếng nói và đặc trưng đầu vào model 🔴 (phần cơ bản) / 🟡 (phần sâu)

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần I.
> **Chương trước:** [Chương 3. Định dạng file, container và codec](chuong-03-dinh-dang-file-container-va-codec.md).
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §5.2 (VAD), §5.3 (turn detection), §5.4.1 (ba nghĩa của "realtime"), §5.4.4 (faster-whisper), §7.1 (audio ingress, reblock 20 ms → 512 samples).
> **Cơ sở:** phần lớn là kiến thức giáo trình về xử lý tín hiệu số và nhận dạng tiếng nói (STFT, mel, MFCC, CMVN, lọc FIR/IIR, Griffin-Lim). Những chỗ lấy từ tài liệu thiết kế hoặc wiki được ghi rõ và giữ nhãn bằng chứng (**Reported**, **Synthesis**…). Tham số mặc định của thư viện (librosa, torchaudio, NeMo, Whisper, faster-whisper, Silero…) là theo hiểu biết chung tại thời điểm viết, **chưa chạy lại trong repo này**; hãy kiểm tra với phiên bản bạn cài. Các con số về độ phân giải mel ở §4.5.2 được tính bằng script Python thuần (**Reproduced**, công thức Slaney như librosa).

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Giải thích được chuỗi biến đổi **waveform → frame → window → FFT → power → mel → log → chuẩn hoá** và tính được kích thước tensor ở từng bước.
2. Chọn và tính được tham số STFT (window, hop, `n_fft`), biết trade-off thời gian–tần số, và biết vì sao 25 ms / 10 ms là mặc định của ASR.
3. Hiểu mel filterbank, log-mel, MFCC, CMVN, pre-emphasis đủ để **đọc một file config preprocessor** và nhận ra chỗ lệch giữa lúc train và lúc chạy.
4. Tính được các đặc trưng đơn giản (RMS/dBFS, zero-crossing rate, F0) và dùng chúng để debug hoặc làm gate rẻ tiền.
5. Dùng được bộ lọc high-pass/low-pass/band-pass theo kiểu **streaming có state**, biết khác biệt FIR/IIR ở mức khái niệm.
6. Nói chính xác mỗi model trong pipeline nhận gì: Silero VAD, Whisper, Smart Turn, FastConformer (Nemotron), và họ Kaldi/WeNet.
7. Suy ra được từ frame rate của encoder: độ phân giải thời gian, chunk size, lookahead và sàn độ trễ của ASR streaming. Giải thích được vì sao VAD, ASR và TTS dùng chunk khác nhau.
8. (Nâng cao) Biết vì sao không thể "đảo log-mel thành audio" một cách sạch sẽ, và vì sao TTS cần vocoder.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. STFT với window 25 ms, hop 10 ms ở 16 kHz cho ra bao nhiêu frame mỗi giây? Mỗi frame có bao nhiêu bin?
- Q2. Whisper nhận input gì: số mel bins, cửa sổ 30 s, padding? Vì sao clip ngắn hoặc im lặng dễ sinh hallucination?
- Q3. Spectrogram của 6 thanh tiếng Việt khác nhau ở đâu?

---

## 4.1 Bức tranh tổng: model "nhìn" audio như thế nào

Model không nhận "âm thanh". Nó nhận một **tensor** mà một đoạn code preprocessor đã tạo ra từ mảng sample. Đoạn code đó là một phần của model, dù nhiều khi nằm trong file khác (`feature_extractor`, `preprocessor` trong YAML, `processor` của Transformers). Mỗi sai lệch ở đây là một sai lệch ở input, và model không báo lỗi; nó chỉ cho kết quả tệ đi.

```text
waveform float32 [-1,1], 16 kHz, mono                       (Chương 2)
   │  (tuỳ model) dither, pre-emphasis, high-pass
   ▼
framing: cắt khung 25 ms (400 mẫu), hop 10 ms (160 mẫu)       §4.2
   ▼
windowing: nhân cửa sổ Hann                                   §4.2.3
   ▼
FFT (n_fft = 400 hoặc 512) → phổ phức                         §4.3
   ▼
|X|² (power) hoặc |X| (magnitude)                             §4.4
   ▼
mel filterbank 80 hoặc 128 bộ lọc                             §4.5
   ▼
log (log10, ln, hoặc dB) với floor                            §4.5.3
   ▼
chuẩn hoá: CMVN / global stats / công thức cố định (Whisper)  §4.5.6
   ▼
tensor (n_mels × T) ở 100 frame/s
   ▼
encoder: conv subsampling 2×/4×/8× → 50/25/12.5 frame/s       §4.9
```

Không phải model nào cũng đi hết chuỗi này:

| Model trong pipeline | Nhận vào | Ai tính đặc trưng |
|---|---|---|
| Silero VAD | Waveform thô, cửa sổ 512 mẫu ở 16 kHz | Bên trong model (lớp đầu tự học/tính biểu diễn phổ) |
| Whisper / faster-whisper / PhoWhisper | Log-mel 80 hoặc 128 bin, đúng 30 s | Feature extractor đi kèm (Python/numpy/CT2) |
| Smart Turn v3.2 | PCM 16 kHz tối đa 8 s → log-mel kiểu Whisper | Code inference của Smart Turn |
| FastConformer/Conformer (Nemotron, Parakeet, Canary) | Log-mel 80/128, 25/10 ms | Preprocessor NeMo (`AudioToMelSpectrogramPreprocessor`) |
| ChunkFormer, ZipFormer, họ Kaldi/WeNet/k2 | Kaldi fbank 80 chiều | `torchaudio.compliance.kaldi` / kaldifeat / sherpa |
| TTS acoustic model + vocoder | Sinh ra mel (hoặc token codec), vocoder biến thành waveform | Chiều ngược, xem §4.10 và Chương 13 |

Câu cần nhớ: **đặc trưng là một hợp đồng giữa lúc train và lúc chạy**. Bạn không chọn tham số STFT cho model đã train. Bạn **đọc** nó và **tái tạo đúng**.

---

## 4.2 Framing, windowing, overlap, hop

### 4.2.1 Vì sao phải cắt khung

Tiếng nói không dừng (non-stationary): ống thanh âm thay đổi liên tục. Nhưng trong khoảng **10–30 ms** nó thay đổi đủ chậm để coi như "gần dừng" (quasi-stationary). Vì thế ta cắt tín hiệu thành các **frame** ngắn, phân tích phổ từng frame, rồi xếp chúng theo thời gian.

- **Frame length / window length / `win_length`:** độ dài mỗi khung. ASR: 25 ms (400 mẫu ở 16 kHz).
- **Hop / stride / `hop_length` / `window_stride`:** khoảng dịch giữa hai khung liên tiếp. ASR: 10 ms (160 mẫu).
- **Overlap** = window − hop = 15 ms (240 mẫu), tức 60%.
- **`n_fft`:** số điểm FFT, ≥ window. Nếu lớn hơn thì frame được zero-pad (§4.3.3).

Lưu ý thuật ngữ (đã gặp ở Chương 2): "frame" ở đây là **khung phân tích DSP**, khác "frame" của audio API (một sample trên mọi kênh) và khác "frame" của Opus (gói 20 ms).

### 4.2.2 Số frame: công thức và chuyện `center`

Với tín hiệu dài `L` mẫu, window `W`, hop `H`:

```text
center=False (Kaldi snip_edges=True, streaming tự nhiên):
    T = 1 + floor((L - W) / H)          (khi L ≥ W)

center=True (librosa, torch.stft, Whisper):
    tín hiệu được pad n_fft//2 mẫu mỗi đầu, frame t có tâm tại t·H
    T = 1 + floor(L / H)
```

Ví dụ 1 s ở 16 kHz, W = 400, H = 160:

- `center=False`: T = 1 + floor(15 600 / 160) = 1 + 97 = **98** frame.
- `center=True`: T = 1 + floor(16 000 / 160) = **101** frame.

Cả hai đều là "100 frame mỗi giây" về tốc độ; khác nhau ở **biên**. Với streaming, `center=True` cần pad cả phía tương lai, nên offline và online lệch nhau ở vài frame đầu/cuối (§4.9.2).

Kiểu pad khi `center=True` cũng là một tham số ẩn: `torch.stft` mặc định `reflect`; librosa từ bản 0.10 chuyển mặc định sang `constant` (zero). Khác biệt chỉ ở biên, nhưng đủ để test parity giữa hai implementation fail.

### 4.2.3 Cửa sổ (window)

Cắt cứng một đoạn = nhân với cửa sổ chữ nhật. Biên đột ngột tạo ra **rò phổ (spectral leakage)**: năng lượng của một sinusoid lan ra nhiều bin. Cửa sổ làm mềm hai đầu frame để giảm rò.

| Cửa sổ | Công thức (n = 0…N−1) | Main lobe | Side lobe cao nhất | Dùng ở |
|---|---|---|---|---|
| Chữ nhật | 1 | Hẹp nhất | ~−13 dB | Gần như không dùng cho phổ |
| Hann | 0.5 − 0.5·cos(2πn/N) | Rộng gấp ~2 | ~−31 dB, giảm nhanh | Whisper, librosa, torchaudio, NeMo |
| Hamming | 0.54 − 0.46·cos(2πn/N) | Như Hann | ~−43 dB, giảm chậm | HTK, nhiều hệ MFCC cổ điển |
| Povey | (Hann)^0.85 | Giữa Hann và Hamming | | Kaldi mặc định |

Hai chi tiết hay gây lệch:

- **Periodic vs symmetric:** cửa sổ cho STFT nên là *periodic* (chia cho N). `torch.hann_window` mặc định periodic; `np.hanning` và `scipy.signal.windows.hann` (mặc định `sym=True`) là *symmetric* (chia cho N−1). Khác nhau rất nhỏ nhưng không bằng nhau.
- **`win_length < n_fft`:** cửa sổ được đặt giữa và pad zero hai bên (torch/librosa). NeMo hay dùng `window_size=0.025` (400) với `n_fft=512`.

### 4.2.4 Chọn hop và overlap

- Hop quyết định **frame rate** của đặc trưng: hop 10 ms → 100 Hz. Đây là độ phân giải thời gian "danh nghĩa".
- Overlap đủ lớn để không bỏ sót sự kiện ngắn (burst của âm tắc dài 5–20 ms) và để tái tạo được tín hiệu (§4.10.1). Với Hann, overlap 50% hoặc 75% thoả điều kiện COLA.
- Hop nhỏ hơn → nhiều frame hơn → tốn compute hơn ở encoder. Đó là lý do encoder hiện đại **subsample** ngay sau đó (§4.9).

---

## 4.3 Fourier: DFT/FFT, biên độ và pha

### 4.3.1 DFT trong một dòng

Với frame `x[n]`, n = 0…N−1:

```text
X[k] = Σ_n x[n] · w[n] · e^(−j·2π·k·n/N),   k = 0…N−1
```

- Bin `k` ứng với tần số **f_k = k · sr / N**.
- Với tín hiệu thực, phổ đối xứng: chỉ cần **N/2 + 1** bin (k = 0 là DC, k = N/2 là Nyquist). Đó là `np.fft.rfft`.
- **Khoảng cách bin Δf = sr / N.** Ở 16 kHz: N = 400 → 40 Hz; N = 512 → 31.25 Hz; N = 1024 → 15.6 Hz.
- FFT là thuật toán tính DFT nhanh, O(N log N). Nó nhanh nhất với N là luỹ thừa của 2, nhưng các thư viện hiện đại xử lý N = 400 vẫn tốt.

### 4.3.2 Biên độ, công suất, pha

- `|X[k]|` = **magnitude spectrum**; `|X[k]|²` = **power spectrum**. Whisper và hầu hết preprocessor ASR dùng power (`power=2.0`); một số TTS/vocoder dùng magnitude (`power=1.0`). Dùng nhầm thì log lệch đúng 2 lần (trong dB: 10·log10 vs 20·log10).
- `∠X[k]` = **phổ pha**. Đặc trưng ASR **bỏ pha**. Lý do: tai người ít nhạy với pha tuyệt đối (Chương 1), và pha từng frame rất "nhảy", khó học. Hệ quả: bỏ pha thì không đảo ngược trực tiếp được về waveform (§4.10).

### 4.3.3 Zero-padding không tăng độ phân giải thật

Đặt `n_fft=512` với window 400 nghĩa là pad 112 số 0. Phổ được **nội suy** dày hơn (31.25 Hz thay vì 40 Hz), nhưng khả năng **tách hai thành phần gần nhau** vẫn do độ dài cửa sổ quyết định (~ sr / W, cộng hệ số của cửa sổ). Muốn phân giải tần số thật tốt hơn, phải dùng window dài hơn.

### 4.3.4 Trade-off thời gian–tần số

Một frame dài W mẫu cho độ phân giải tần số ~ sr/W nhưng "nhoè" thời gian trong W/sr giây. Không có cách nào tốt cả hai (nguyên lý bất định Gabor).

| Window ở 16 kHz | Δf danh nghĩa | Thấy rõ | Dùng cho |
|---|---|---|---|
| 5 ms (80 mẫu) | 200 Hz | Formant, burst, nhịp dây thanh (vạch dọc) | Wideband spectrogram, đọc phụ âm |
| 25 ms (400 mẫu) | 40 Hz | Envelope + một phần harmonics ở tần thấp | ASR log-mel |
| 40–64 ms (640–1024 mẫu) | 25–15.6 Hz | Harmonics riêng lẻ, đường F0 | Pitch tracking, đọc thanh điệu |

Đây chính là bảng "wideband vs narrowband spectrogram" của Chương 1 §1.8.2, nhìn từ phía tham số.

---

## 4.4 STFT và spectrogram

### 4.4.1 Định nghĩa và shape

STFT = DFT của từng frame có cửa sổ, xếp theo thời gian. Kết quả là ma trận phức kích thước `(n_fft/2 + 1) × T`. Spectrogram = `|STFT|²` (hoặc `|STFT|`).

Quy ước shape là một nguồn bug kinh điển:

| Thư viện / model | Shape mặc định |
|---|---|
| librosa, torchaudio, `torch.stft` | `(..., freq, time)` |
| Whisper (input encoder) | `(batch, n_mels, 3000)` |
| NeMo preprocessor output | `(batch, n_mels, T)` + `length` |
| Kaldi fbank (`torchaudio.compliance.kaldi.fbank`) | `(T, n_mels)` (thời gian trước) |
| Code numpy "tự viết" | thường `(T, freq)` |

Đưa nhầm `(T, F)` vào chỗ cần `(F, T)` thường **không báo lỗi** nếu T tình cờ khớp kích thước, và cho kết quả rác.

### 4.4.2 Thang hiển thị: dB và floor

Năng lượng phổ trải hàng chục bậc độ lớn, nên luôn xem theo log:

```text
S_dB = 10 · log10(max(P, ε))          với P là power
     = 20 · log10(max(|X|, ε))        với magnitude
```

`ε` (floor) tránh log(0) ở chỗ im lặng số (digital silence). Khi hiển thị, người ta thường kẹp dải động về 80 dB dưới đỉnh (`top_db=80` trong librosa). Whisper làm điều tương tự (kẹp 8 bậc log10 = 80 dB, §4.8.2).

### 4.4.3 Đọc spectrogram: góc nhìn của người debug pipeline

Bảng nhận dạng hiện tượng âm học (nguyên âm, xát, tắc, mũi, hum, reverb…) đã có ở Chương 1 §1.8.3. Ở đây là các dấu hiệu **lỗi xử lý** hay gặp khi debug pipeline:

| Thấy trên spectrogram của input ASR | Nhiều khả năng là |
|---|---|
| Trống trơn trên 4 kHz, file khai báo 16 kHz | Nguồn 8 kHz bị upsample (telephony), hoặc lệch sample rate |
| Mọi thứ bị "nén" xuống nửa dưới, giọng nghe trầm/chậm | Audio 16 kHz bị khai báo là 32 kHz hoặc 48 kHz (xem Chương 2) |
| Ảnh phản chiếu của harmonics đi ngược chiều ở tần cao | Aliasing: downsample không lọc |
| Vạch dọc đều đặn theo chu kỳ cố định (ví dụ mỗi 20 ms hoặc 32 ms) | Ranh giới chunk không liên tục: mất mẫu, chèn mẫu, hoặc header WAV bị phát thành audio |
| Toàn bộ spectrogram một màu "sàn" phẳng, không có cấu trúc | Đọc int16 như float (hoặc ngược lại), sai endianness, hoặc audio toàn 0 |
| Dải năng lượng rất mạnh ở 0 Hz | DC offset (một số mic USB), cần high-pass (§4.7) |
| Vùng "cắt ngang" phẳng ở đỉnh các âm tiết to, kèm năng lượng lan khắp dải tần | Clipping |
| Phổ "sạch bất thường", nền đen tuyền giữa các từ, phụ âm xát bị mờ | Noise suppression quá tay phía client (Chương 7) |

Thói quen tốt: **dump audio ở mỗi cạnh của pipeline** (sau decode, sau resample, trước ASR, sau TTS) và mở spectrogram khi có nghi ngờ. Hầu hết bug "model kém" lộ ra trong 10 giây nhìn ảnh.

### 4.4.4 Spectrogram của 6 thanh tiếng Việt

Chương 1 §1.4.3 mô tả thanh điệu là tổ hợp **đường F0 + chất giọng + trường độ**. Trên spectrogram, ba thành phần này hiện ra như sau (mô tả cho giọng Bắc, đọc âm tiết "ma" với 6 thanh; giọng Nam nhập hỏi–ngã và nặng ít thanh hầu hoá):

| Thanh | Narrowband (window 40–64 ms): harmonics | Chất giọng / thời gian | Trên log-mel 80 bin (25/10 ms) |
|---|---|---|---|
| Ngang (ma) | Các vạch harmonics gần như nằm ngang, ở mức giữa–cao | Modal, đều | Dải năng lượng tần thấp ổn định |
| Huyền (mà) | Vạch thấp, dốc xuống nhẹ; khoảng cách vạch nhỏ hơn ngang | Có thể hơi thở: harmonics trên mờ, nhiễu nhẹ ở tần cao | Năng lượng nghiêng về bin thấp hơn |
| Sắc (má) | Vạch đi lên, khoảng cách vạch giãn dần | Modal; trong âm tiết tắc thì rất ngắn | Đuôi âm tiết dịch lên bin cao hơn |
| Hỏi (mả) | Vạch xuống rồi có thể lên lại (hình chữ V/võng) | Có thể có đoạn kẹt ở đáy | Đường cong khó thấy, chủ yếu qua bin thấp |
| Ngã (mã) | Vạch đi lên nhưng **đứt quãng hoặc nhảy** ở giữa | Glottal stop/creaky giữa âm tiết: harmonics biến mất vài chục ms, các nhịp dọc thưa và không đều, năng lượng tụt | Một "khe" năng lượng giữa âm tiết |
| Nặng (mạ) | Vạch thấp, rơi nhanh, **kết thúc đột ngột** | Ngắn, kết thúc bằng tắc thanh hầu; đuôi creaky | Âm tiết ngắn, cắt gọn, năng lượng tụt cuối |

Điểm mấu chốt cho pipeline:

- **Đường F0 thấy rõ nhất ở narrowband.** Log-mel 25/10 ms làm mờ harmonics ở tần cao, nhưng ở tần thấp các bộ lọc mel hẹp (khoảng cách tâm ~37 Hz với 80 bin, ~23 Hz với 128 bin, §4.5.2) nên vẫn giữ được một phần thông tin harmonics và F0. Model học thanh điệu từ đó cộng với ngữ cảnh. 128 bin (Whisper large-v3) giữ chi tiết tần thấp tốt hơn 80 bin (**Synthesis** từ phép tính ở §4.5.2, chưa đo trên ASR tiếng Việt).
- **Ngã và nặng được nhận ra phần lớn nhờ chất giọng và thời gian**, không chỉ nhờ F0. Phần đó nằm ở **cuối** âm tiết. Cắt mất 50–100 ms cuối (VAD quá gắt, `speech_pad_ms` quá nhỏ, chunk bị cắt đuôi) là xoá đúng bằng chứng phân biệt thanh. Đây là nền tảng DSP cho khuyến nghị `speech_pad_ms` 100–200 ms ở §5.2 tài liệu thiết kế (**Reported** tham số; lý giải là **Synthesis**).
- Pitch tracker (§4.6.3) hay báo "unvoiced" hoặc nhảy quãng tám ở đoạn creaky của ngã/nặng. Đừng coi đó là lỗi của model; đó là bản chất tín hiệu.

---

## 4.5 Mel scale, filterbank, log-mel, MFCC, CMVN, pre-emphasis

### 4.5.1 Mel scale

Tai người phân biệt tần số gần tuyến tính ở dưới ~1 kHz và gần logarit ở trên. Thang mel mô phỏng điều đó. Có hai định nghĩa phổ biến, **không bằng nhau**:

| Biến thể | Công thức | Ai dùng mặc định |
|---|---|---|
| **HTK** | m = 2595 · log10(1 + f / 700) | torchaudio (`mel_scale="htk"`), Kaldi, HTK |
| **Slaney** | Tuyến tính dưới 1 kHz (f / (200/3)), logarit trên 1 kHz (bước log(6.4)/27) | librosa (`htk=False`), Whisper (bảng filter sinh từ librosa) |

Cùng "80 mel bins" nhưng HTK và Slaney đặt tâm bộ lọc khác nhau. Thêm vào đó là chuẩn hoá diện tích bộ lọc (`norm="slaney"` trong librosa; `norm=None` mặc định trong torchaudio). Ba tham số này (`n_mels`, `mel_scale`, `norm`) phải khớp với lúc train.

### 4.5.2 Mel filterbank

Filterbank là `n_mels` bộ lọc tam giác đặt cách đều trên thang mel, chồng nhau 50%. Áp vào power spectrum bằng một phép nhân ma trận:

```text
mel[m, t] = Σ_k  F[m, k] · P[k, t]       F: (n_mels × (n_fft/2+1))
```

Kết quả: 201 (hoặc 257) bin tuyến tính → 80 hoặc 128 giá trị mel. Bộ lọc **hẹp ở tần thấp, rộng ở tần cao**: chi tiết ở vùng formant thấp và F0 được giữ, chi tiết harmonics ở tần cao bị gộp lại thành envelope.

Độ phân giải cụ thể với thang Slaney, 0–8 kHz (tính bằng script, **Reproduced**):

| | 80 bin | 128 bin |
|---|---|---|
| Khoảng cách tâm ở vùng < 1 kHz | ~37.2 Hz | ~23.4 Hz |
| Số bộ lọc có tâm dưới 1 kHz | 26 | 42 |
| Khoảng cách tâm ở đỉnh dải (~8 kHz) | ~301 Hz | ~191 Hz |
| Bộ lọc rỗng với `n_fft=400` (bin 40 Hz) | 0 | 0 |

Đọc bảng này: harmonics của giọng nam (F0 ~100–150 Hz) cách nhau ~100–150 Hz, nên dưới 1 kHz cả 80 và 128 bin đều có vài bộ lọc giữa hai harmonic, tức là F0 vẫn "để lại dấu". Nhưng với `n_fft=400` thì bin FFT cách 40 Hz, nên ở 128 bin nhiều bộ lọc tần thấp chỉ phủ 1–2 bin FFT: tăng `n_mels` không vượt được giới hạn của STFT (§4.3.3).

`fmin`/`fmax` cũng là tham số: ASR 16 kHz thường 0–8000 Hz; TTS 22.05 kHz hay dùng `fmax=8000` dù Nyquist là 11 025 Hz.

### 4.5.3 Log và floor

Sau mel là log, vì: (1) cảm nhận độ to gần logarit, (2) nén dải động, (3) biến tích nguồn × bộ lọc (Chương 1 §1.3.4) thành tổng, dễ học hơn.

Các biến thể đều có mặt trong thực tế: `log10` (Whisper), `ln` (NeMo, Kaldi), `10·log10` dB (librosa `power_to_db`). Và mỗi cái có floor riêng: `1e-10` (Whisper), `log_zero_guard_value=2^-24` (NeMo, theo hiểu biết chung), hoặc `ε = machine epsilon` (Kaldi). Floor quan trọng ở **im lặng số tuyệt đối** (toàn mẫu 0, ví dụ padding, mute, gap trong transport): nếu floor khác lúc train thì vùng đó cho giá trị lạ. Đây là lý do nhiều preprocessor thêm **dither** (nhiễu cực nhỏ, ví dụ 1e-5) để không bao giờ có 0 tuyệt đối.

### 4.5.4 MFCC

MFCC = DCT (loại II) của log-mel, giữ 13 (hoặc 20–40) hệ số đầu, thường kèm delta và delta-delta.

- DCT **khử tương quan** giữa các bin mel liền kề và tách "envelope" (hệ số thấp) khỏi "chi tiết" (hệ số cao). Bỏ hệ số cao = bỏ phần lớn thông tin harmonics/F0.
- Thời GMM-HMM, MFCC là chuẩn vì GMM cần đặc trưng ít tương quan. Mạng neural hiện đại học tốt trực tiếp từ log-mel, nên **ASR/VAD/turn detector hiện đại gần như đều dùng log-mel hoặc waveform**, không dùng MFCC.
- MFCC vẫn có ích: speaker embedding đời cũ, đặc trưng nhanh cho bài toán phân loại nhỏ, và để đọc paper cũ.
- Với ngôn ngữ thanh điệu như tiếng Việt, MFCC 13 hệ số bỏ đi nhiều thông tin F0; hệ cổ điển phải ghép thêm đặc trưng pitch riêng (**Synthesis**).

### 4.5.5 Pre-emphasis

```text
y[n] = x[n] − α · x[n−1],     α ≈ 0.97
```

Đây là một high-pass bậc 1 rất nhẹ, nâng tần cao khoảng +6 dB/octave, bù độ nghiêng phổ tự nhiên của tiếng nói (nguồn dây thanh ~−12 dB/oct, phát xạ ở môi ~+6 dB/oct, Chương 1). Mục đích: phụ âm xát và formant cao không bị chìm.

Model nào dùng phụ thuộc lúc train: Kaldi fbank và NeMo preprocessor mặc định có pre-emphasis 0.97 (theo hiểu biết chung, xem `preemph` trong config); Whisper **không** dùng. Thêm hay bỏ nhầm pre-emphasis làm cả log-mel nghiêng đi vài dB, model vẫn chạy nhưng WER tăng.

### 4.5.6 Chuẩn hoá: CMVN và các kiểu khác

Mục đích: đưa đặc trưng về phân phối ổn định, khử ảnh hưởng của gain mic và kênh truyền (một bộ lọc kênh cố định là một phép **cộng hằng số** trong miền log-phổ, nên trừ trung bình theo thời gian sẽ khử được nó).

| Kiểu | Cách làm | Streaming? | Gặp ở |
|---|---|---|---|
| **Per-utterance CMVN** (`normalize: per_feature`) | Trừ mean, chia std theo từng bin trên **cả câu** | Không: cần thấy hết câu | NeMo model offline |
| **Global CMVN** | Mean/std tính trước trên tập train, lưu file | Có | WeNet, k2/icefall, nhiều model streaming |
| **Sliding-window CMVN** | Mean/std trên cửa sổ trượt vài giây | Có, nhưng đầu câu kém ổn định | Kaldi online |
| **Không chuẩn hoá** (`normalize: NA`) | Để model tự học (thường có LayerNorm/BatchNorm sau) | Có | Nhiều model cache-aware streaming của NeMo (theo hiểu biết chung, kiểm tra config) |
| **Công thức cố định** | Kẹp dải động và scale bằng hằng số | Có | Whisper: `(max(log, max−8) + 4) / 4` |

Bẫy: dùng model train với per-utterance CMVN trong chế độ streaming bằng cách tính CMVN trên từng chunk nhỏ. Chunk 160 ms có mean/std rất khác cả câu; kết quả tệ hơn hẳn mà không có lỗi nào được báo. Đây là một lý do vì sao model streaming thật (§5.4.1 tài liệu thiết kế) phải được **thiết kế và train** cho streaming, không chỉ bọc lại.

### 4.5.7 Hợp đồng đặc trưng: danh sách phải khớp

Khi tự viết feature extractor (ví dụ để chạy model ONNX/GGUF ngoài framework gốc, hoặc làm streaming), checklist sau phải khớp **từng dòng** với lúc train:

| Tham số | Giá trị điển hình | Hậu quả khi lệch |
|---|---|---|
| Sample rate | 16 000 | Mọi thứ sai (Chương 2) |
| Thang biên độ | float [-1, 1] **hoặc** int16 [-32768, 32767] | Log lệch hằng số lớn (xem dưới) |
| Dither | 0 hoặc 1e-5 | Khác ở im lặng |
| Pre-emphasis | 0 hoặc 0.97 | Phổ nghiêng |
| Window, periodic/symmetric | Hann periodic / Povey | Sai số nhỏ |
| `win_length`, `hop_length`, `n_fft` | 400 / 160 / 400 hoặc 512 | Sai tần số bin, sai frame rate |
| `center`, `pad_mode`, `snip_edges` | Tuỳ | Lệch biên, lệch số frame |
| `power` | 2.0 hoặc 1.0 | Log lệch 2× |
| `n_mels`, `fmin`, `fmax` | 80/128, 0, 8000 | Sai shape hoặc sai vị trí bin |
| `mel_scale`, `norm` | Slaney/HTK, slaney/None | Lệch tâm và độ cao bộ lọc |
| Log: cơ số, floor | log10/ln, 1e-10 / 2^-24 | Lệch thang |
| Chuẩn hoá | per_feature / global / NA / Whisper | Lệch phân phối |
| Layout | (F, T) hay (T, F) | Rác |

**Ví dụ định lượng về thang biên độ:** nhân waveform với 32 768 thì power nhân với 32 768² ≈ 1.07 × 10⁹, tức log10 cộng thêm **9.03**, hay ln cộng thêm **20.8**. Với chuẩn hoá của Whisper (chia 4), đó là dịch **+2.26** trên mọi giá trị. Nhiều model họ Kaldi/WeNet được train với waveform ở thang int16 (theo hiểu biết chung; kiểm tra code inference của ChunkFormer/sherpa trước khi dùng), còn Whisper và NeMo dùng float [-1, 1]. Đưa nhầm thang là lỗi im lặng, không crash.

Thực hành tốt: viết **test parity** so extractor của bạn với extractor gốc trên cùng file, sai số tuyệt đối tối đa nên ở mức 1e-4–1e-3 trên log-mel (§4.11.2).

---

## 4.6 Đặc trưng đơn giản: energy/RMS, ZCR, F0

Các đặc trưng này rẻ, giải thích được, và rất hữu ích cho **gate, debug, monitoring**. Chúng không thay được model.

### 4.6.1 Energy, RMS, dBFS

```text
RMS(frame) = sqrt(mean(x²))
dBFS       = 20 · log10(RMS + ε)          (0 dBFS = sóng vuông full scale; sin full scale ≈ −3 dBFS)
```

Dùng cho:

- **Ngưỡng thích ứng** ở §5.2 tài liệu thiết kế: đo VAD prob và RMS trong 2–3 s đầu để ước lượng sàn nhiễu (**Reported**). RMS sàn nhiễu điển hình: phòng yên tĩnh qua mic laptop khoảng −60 đến −50 dBFS; quán cà phê có thể −40 dBFS (ước lượng, phụ thuộc thiết bị).
- **Gate barge-in** rẻ: chỉ chạy kiểm tra ngắt lời khi RMS mic vượt sàn nhiễu một khoảng (ví dụ +10 dB). Kết hợp với VAD, không thay VAD.
- **Monitoring:** phát hiện mic tắt (RMS ≈ −∞), clipping, gain quá nhỏ.
- **Phát hiện im lặng số** trước khi gửi vào Whisper: một clip toàn sàn nhiễu gần như chắc chắn không nên đi vào ASR (§4.8.2).

Năng lượng khung là đặc trưng VAD đời đầu (energy VAD). Nó thất bại với nhiễu không dừng (tiếng người khác, nhạc, tiếng va đập) vì những thứ đó cũng có năng lượng. Đó là lý do dùng Silero.

### 4.6.2 Zero-crossing rate (ZCR)

Tỉ lệ số lần tín hiệu đổi dấu trong một frame. Tín hiệu nhiều thành phần tần cao đổi dấu nhiều.

- Âm xát vô thanh (s, x, ph, kh): ZCR **cao**, năng lượng thấp–vừa.
- Nguyên âm: ZCR **thấp**, năng lượng cao.
- Im lặng có nhiễu trắng: ZCR cao, năng lượng rất thấp.

Kết hợp energy + ZCR là cách cổ điển để không cắt mất phụ âm xát đầu/cuối câu. Bẫy: DC offset làm ZCR về gần 0 (tín hiệu không cắt qua 0), nên high-pass trước (§4.7).

### 4.6.3 Pitch tracking (F0)

| Thuật toán | Ý tưởng | Ghi chú |
|---|---|---|
| Autocorrelation | Tìm độ trễ τ tại đó tín hiệu giống chính nó nhất; F0 = sr/τ | Đơn giản; dễ lỗi quãng tám |
| YIN / pYIN | Hàm hiệu chuẩn hoá + ngưỡng; pYIN thêm HMM cho chuỗi voiced/unvoiced | `librosa.yin`, `librosa.pyin`; tốt cho phân tích offline |
| RAPT / Praat | Cổ điển, ổn định | `parselmouth` (Praat trong Python) |
| CREPE, các mạng neural | CNN trên waveform | Chính xác hơn với nhiễu, cần GPU để nhanh |

Tham số quan trọng:

- `fmin`/`fmax`: giọng người ~60–500 Hz. Đặt `fmin` quá cao thì giọng nam trầm bị lỗi; quá thấp thì cửa sổ phải dài.
- **Cửa sổ phải chứa ít nhất 2 chu kỳ của `fmin`:** 2 / 60 Hz ≈ 33 ms. Vì vậy pitch tracker hay dùng window 40–64 ms, dài hơn window ASR.
- Đầu ra luôn có cờ **voiced/unvoiced**. Đoạn creaky của thanh ngã/nặng hay bị đánh unvoiced hoặc nhảy quãng tám (F0 × 2 hoặc ÷ 2).

Dùng F0 trong pipeline ở đâu: phân tích lỗi ASR theo thanh, kiểm tra TTS có đúng thanh không (so contour F0 của TTS với giọng người, Chương 21), thống kê giọng nam/nữ trong corpus đánh giá. Turn detector như Smart Turn **ngầm** dùng prosody (F0, năng lượng, nhịp) vì nó nhận audio thô (**Reported**: "audio-native… can use prosody"), nhưng ta không cần trích F0 cho nó.

---

## 4.7 Lọc: low-pass, high-pass, band-pass; FIR và IIR

### 4.7.1 Bốn loại theo đáp ứng tần số

| Loại | Giữ | Dùng trong pipeline |
|---|---|---|
| **Low-pass** | Dưới tần số cắt | Anti-alias trước downsample (Chương 2); mô phỏng băng hẹp |
| **High-pass** | Trên tần số cắt | Bỏ DC offset, hum 50 Hz, tiếng rung bàn/gió: cắt ~60–100 Hz |
| **Band-pass** | Trong một dải | Mô phỏng điện thoại 300–3400 Hz để tạo dữ liệu test (§10 tài liệu thiết kế) |
| **Band-stop / notch** | Loại một dải hẹp | Khử hum 50 Hz và hài của nó |

Không nên high-pass quá cao: F0 giọng nam ~85–180 Hz. Cắt ở 200 Hz không làm mất thanh điệu (nhờ missing fundamental, Chương 1) nhưng làm lệch phân phối so với dữ liệu train. Mức an toàn cho ASR là ≤ 80–100 Hz (**Synthesis**).

### 4.7.2 FIR và IIR ở mức khái niệm

| | FIR (Finite Impulse Response) | IIR (Infinite Impulse Response) |
|---|---|---|
| Công thức | y[n] = Σ b_k · x[n−k] | y[n] = Σ b_k · x[n−k] − Σ a_k · y[n−k] (có hồi tiếp) |
| Pha | Có thể **tuyến tính** (đối xứng hệ số) → mọi tần số trễ như nhau | Pha phi tuyến |
| Độ trễ | (N−1)/2 mẫu với FIR tuyến tính; cắt dốc cần N lớn → trễ lớn | Rất ít, vài mẫu |
| Chi phí | Cần nhiều hệ số cho đáp ứng dốc | Đáp ứng dốc với ít hệ số (biquad bậc 2) |
| Ổn định | Luôn ổn định | Có thể mất ổn định nếu thiết kế/số học kém; dùng dạng SOS |
| Gặp ở | Resampler (polyphase sinc, Chương 2), anti-alias chất lượng cao | High-pass DC, EQ, notch, AEC/AGC nội bộ |

Pre-emphasis ở §4.5.5 là một FIR bậc 1. Bộ lọc Butterworth thiết kế bằng `scipy.signal.butter(..., output="sos")` là IIR dạng chuỗi biquad.

### 4.7.3 Lọc streaming: state là bắt buộc

Một bộ lọc có "bộ nhớ" (các mẫu x, y trước đó). Lọc từng chunk độc lập = reset bộ nhớ mỗi chunk = **click ở mỗi biên chunk**, đúng y như lỗi resample stream không giữ state (Chương 2 §2.8.4).

- Dùng `scipy.signal.sosfilt(sos, x, zi=state)` và giữ `state` giữa các chunk (code ở §4.11.5).
- Một instance filter cho **mỗi session, mỗi kênh**. Không dùng chung giữa user.
- **Không** dùng `filtfilt`/`sosfiltfilt` trong streaming: chúng lọc xuôi rồi ngược để có pha 0, nghĩa là cần thấy tương lai. Chỉ dùng cho xử lý offline.

---

## 4.8 Đầu vào cụ thể của các model trong pipeline

### 4.8.1 Silero VAD

- **Input:** waveform float32 trong [-1, 1], mono, 16 kHz hoặc 8 kHz. Từ v5, cửa sổ cố định **512 mẫu (32 ms) ở 16 kHz** hoặc **256 mẫu ở 8 kHz**, và `window_size_samples` bị deprecate (**Reported**, [Silero VAD](../wiki/silero-vad.md) qua report thứ cấp).
- **Output:** một xác suất speech cho mỗi cửa sổ, tức 31.25 quyết định mỗi giây.
- **State:** model là mạng có trạng thái (hồi quy), vì vậy cần một `VADIterator`/state riêng cho mỗi session và `reset_states()` khi hết lượt (**Reported**, §5.2 tài liệu thiết kế).
- **Context:** theo code wrapper ONNX chính thức (hiểu biết chung, chưa có trong `raw/`), mỗi lần gọi còn ghép thêm một đoạn ngữ cảnh ngắn từ cuối cửa sổ trước (64 mẫu ở 16 kHz). Nếu tự gọi ONNX không qua wrapper, phải tái tạo đúng điều này hoặc kết quả lệch. Kiểm tra code của phiên bản bạn dùng.
- **Không cần tính mel:** biểu diễn phổ nằm bên trong model. Việc của bạn là đưa đúng sample rate, đúng dtype, đúng độ dài cửa sổ.

Hệ quả: transport gửi frame 20 ms (320 mẫu) nhưng Silero cần 512. Gateway phải **reblock** qua một ring buffer: 8 frame 20 ms = 160 ms = 2 560 mẫu = đúng 5 cửa sổ Silero (§7.1 tài liệu thiết kế, **Synthesis**; tính toán chi tiết ở Chương 2 §2.7.4). Mỗi quyết định VAD vì thế có độ trễ thuật toán tối thiểu 32 ms cộng thời gian chờ đủ cửa sổ.

### 4.8.2 Whisper (openai-whisper, faster-whisper, PhoWhisper)

Tham số feature extractor của Whisper (hiểu biết chung về code gốc; `n_mels` lấy từ wiki):

| Tham số | Giá trị |
|---|---|
| Sample rate | 16 000 Hz, mono, float32 |
| Window / hop / n_fft | Hann 400 (25 ms) / 160 (10 ms) / 400 → 201 bin |
| `center` | True (pad reflect), bỏ frame cuối |
| Power | 2.0 |
| Mel | Slaney, 0–8 kHz. **80 bin** cho tiny…large-v2; **128 bin** cho large-v3 (**Reported**, [Whisper Large v3](../wiki/whisper-large-v3.md)) và large-v3-turbo (kế thừa v3) |
| Log | `log10(max(mel, 1e-10))` |
| Chuẩn hoá | `log = max(log, log.max() − 8.0)` rồi `(log + 4.0) / 4.0` |
| Độ dài | **Đúng 30 s** = 480 000 mẫu → **3 000 frame**; ngắn hơn thì **pad zero**, dài hơn thì cắt |
| Encoder | 2 lớp conv, lớp sau stride 2 → **1 500 vị trí**, mỗi vị trí 20 ms; positional embedding cố định cho 1 500 vị trí |

Vì sao **đúng 30 s**: encoder được train với positional embedding cố định cho 1 500 vị trí và luôn thấy đầu vào 30 s, nên nó **bắt buộc** nhận đúng 3 000 frame. Audio dài hơn cần thuật toán long-form (sequential hoặc chunked với `chunk_length_s=30`, **Reported**, Whisper card). Audio ngắn hơn thì phần còn lại là padding.

Hệ quả cho turn-final ASR: một câu trả lời 1.5 s vẫn tốn compute encoder như 30 s. Đây là một lý do faster-whisper/CT2 và batching quan trọng, và là lý do Whisper "không phải streaming" (§5.4.1 tài liệu thiết kế).

**Vì sao clip ngắn hoặc im lặng dễ sinh hallucination** (lý giải là **Synthesis** dựa trên kiến trúc; hiện tượng là **Reported** trong Whisper card và [Whisper Hallucination Mitigation](../wiki/whisper-hallucination-mitigation.md)):

1. **Decoder là một language model có điều kiện.** Khi bằng chứng âm học yếu (ít tiếng nói, nhiều padding, nhiễu), xác suất của token tiếp theo bị **prior của LM** chi phối. Whisper card tự giả thuyết rằng hai mục tiêu "dự đoán từ tiếp theo" và "phiên âm" cạnh tranh nhau (**Reported**).
2. **Dữ liệu train là weak supervision từ Internet**, nhiều phụ đề video. Ở những đoạn im lặng hoặc nhạc trong video, phụ đề thường là câu kết video ("cảm ơn đã xem", "đăng ký kênh", tên nhóm làm phụ đề). Model học rằng "khi không có tiếng nói rõ, hãy viết những câu này". Blacklist tiếng Việt ở §5.4.4 tài liệu thiết kế là dấu vết trực tiếp của điều đó (**Reported**).
3. **Không có VAD bên trong.** Cơ chế chống duy nhất là token `<|nospeech|>` và các ngưỡng heuristics (`no_speech_threshold`, `log_prob_threshold`, `compression_ratio_threshold`). Chúng là ngưỡng mềm, không phải đảm bảo.
4. **Clip ngắn nghĩa là tỉ lệ padding cao.** Clip 1 s = 100 frame thật + 2 900 frame padding. Phần padding sau chuẩn hoá thành giá trị sàn phẳng (`(log.max() − 8 + 4) / 4`); model đã thấy padding khi train, nhưng một tiếng "ừ" ngắn giữa biển padding cho rất ít bằng chứng, và decoder dễ "bịa thêm".
5. **Chuẩn hoá cố định, không có AGC.** Audio rất nhỏ (far-field, gain thấp) cho log-mel thấp hơn phân phối train vài đơn vị; tương đương với "gần như im lặng" trong mắt model. Kết hợp với điểm 1 là hallucination.
6. **Điều kiện trên văn bản trước** (`condition_on_previous_text=True`) cho phép một hallucination lan sang segment sau và gây lặp vòng; vì vậy tài liệu thiết kế đặt `False` (**Reported**).

Từ đó, các biện pháp ở §5.4.4 tài liệu thiết kế có nền DSP rõ ràng: **lọc bằng VAD trước** (không gửi clip không có tiếng nói), **gate theo năng lượng/thời lượng** (turn < 400 ms VAD mà ra < 2 từ thì nghi ngờ), `language="vi"` (auto-detect trên clip ngắn kém), và **lọc sau decode** bằng `no_speech_prob`/`avg_logprob`/`compression_ratio`.

### 4.8.3 Smart Turn v3.2

- **Backbone:** encoder Whisper Tiny + một lớp phân loại tuyến tính, ~8M tham số (**Reported**, [Smart Turn v3.2](../wiki/smart-turn.md)).
- **Input:** PCM mono 16 kHz, **tối đa 8 s**, khuyến nghị đưa **toàn bộ lượt nói hiện tại**. Dài hơn 8 s thì **cắt từ đầu**; ngắn hơn thì **pad zero ở đầu** để audio nằm ở **cuối** vector input (**Reported**).
- **Đặc trưng:** vì backbone là encoder Whisper Tiny, audio được chuyển thành log-mel kiểu Whisper (Whisper Tiny dùng 80 bin), với cửa sổ 8 s thay vì 30 s: 8 s × 100 = 800 frame mel → khoảng 400 vị trí encoder (**Synthesis** từ kiến trúc; xác minh trong `inference.py` của Smart Turn trước khi tự viết extractor).
- **Vì sao pad ở đầu:** quyết định "đã nói xong chưa" phụ thuộc vào **phần cuối** lượt nói (ngữ điệu đi xuống, âm tiết cuối kéo dài hay cụt, khoảng lặng sau). Đặt phần cuối ở vị trí cố định giúp model luôn nhìn cùng một vùng.
- **Gọi lại trên toàn lượt:** nếu user nói tiếp trước khi inference xong, chạy lại trên **toàn bộ** bản ghi của lượt, không chỉ đoạn mới (**Reported**). Hệ quả DSP: gateway phải giữ buffer audio của lượt hiện tại (tối đa 8 s là đủ cho Smart Turn), tách biệt với buffer cho ASR.
- **Liên hệ tiếng Việt:** model học prosody từ audio, và ở tiếng Việt F0 cuối câu vừa mang thanh điệu vừa mang ngữ điệu (Chương 1 §1.4.4). Vietnamese là ngôn ngữ yếu nhất trong 23 ngôn ngữ của benchmark vendor (accuracy GPU 82.47%, CPU 79.38%, **Reported**). Giải thích một phần bằng xung đột thanh điệu–ngữ điệu là **Synthesis**, chưa kiểm chứng.

### 4.8.4 Conformer / FastConformer (Nemotron 3.5, Parakeet, Canary)

Preprocessor NeMo (`AudioToMelSpectrogramPreprocessor`), giá trị điển hình theo hiểu biết chung (luôn đọc `preprocessor:` trong `model_config.yaml` của checkpoint):

| Tham số NeMo | Điển hình | Ghi chú |
|---|---|---|
| `sample_rate` | 16000 | |
| `window_size` / `window_stride` | 0.025 / 0.01 | Tính bằng **giây**, không phải mẫu |
| `n_fft` | 512 | → 257 bin |
| `window` | hann | |
| `features` | 80 hoặc 128 | Tuỳ checkpoint |
| `normalize` | `per_feature` (offline) / `NA` (nhiều model streaming) | Xem §4.5.6 |
| `dither` | ~1e-5 | Thường tắt khi eval |
| `preemph` | 0.97 | |
| `log` | true, ln với zero guard | |

**Subsampling:** Conformer gốc giảm 4× (40 ms/frame encoder). **FastConformer giảm 8×** bằng các lớp conv (depthwise) có stride, nên mỗi frame encoder = **80 ms** (12.5 Hz). Điều này khớp với bảng `att_context_size` của Nemotron 3.5 tính theo "80 ms frames" (**Reported**, [Nemotron 3.5 ASR Streaming](../wiki/nemotron-3.5-asr-streaming-0.6b.md)). Qwen3-ASR cũng giảm 8× xuống 12.5 Hz trong encoder AuT (**Reported**, [Qwen3-ASR family](../wiki/qwen3-asr-family.md)).

Vì sao 8× là đủ (**Synthesis**): tiếng Việt nói thường khoảng 4–6 âm tiết mỗi giây (ước lượng), tức ~170–250 ms mỗi âm tiết, vẫn tương ứng 2–3 frame encoder 80 ms. CTC/RNNT cần số frame ≥ số token, nên còn dư. Giảm mạnh hơn nữa (16×) bắt đầu chạm giới hạn đó với nói nhanh và tokenizer chi tiết.

### 4.8.5 Họ Kaldi/WeNet (ChunkFormer, ZipFormer)

`torchaudio.compliance.kaldi.fbank` / kaldifeat là chuẩn của họ này: 25/10 ms, cửa sổ Povey, pre-emphasis 0.97, `snip_edges=True` (tương đương `center=False`), mel HTK, log tự nhiên, 80 bin (giá trị mặc định của hàm là 23, các recipe đặt 80). Hai bẫy: `num_mel_bins` mặc định không phải 80, và thang biên độ int16 như đã nói ở §4.5.7 (kiểm tra recipe của model cụ thể).

### 4.8.6 Bảng tổng hợp

| Model | Đơn vị input | Đặc trưng | Bước thời gian của đầu ra model | Có state giữa các lần gọi? |
|---|---|---|---|---|
| Silero VAD v5/v6 | 512 mẫu @16 kHz | Waveform (phổ bên trong) | 32 ms / xác suất | Có (per session) |
| Whisper large-v3/turbo | 30 s cố định | Log-mel 128, Slaney, log10, chuẩn hoá cố định | Encoder 20 ms; timestamp 20 ms | Không (mỗi cửa sổ độc lập) |
| Whisper ≤ v2, PhoWhisper (fine-tune từ Whisper) | 30 s | Log-mel 80 (kiểm tra `num_mel_bins` của checkpoint) | 20 ms | Không |
| Smart Turn v3.2 | ≤ 8 s, pad đầu | Log-mel kiểu Whisper (Tiny, 80) | 1 xác suất / lượt | Không; gọi lại trên toàn lượt |
| Nemotron 3.5 (FastConformer cache-aware) | Chunk 80–1 120 ms | Log-mel NeMo | 80 ms | Có (cache attention + conv) |
| ChunkFormer / ZipFormer | Chunk hoặc câu | Kaldi fbank 80 | 40–80 ms (tuỳ model) | Tuỳ chế độ |

---

## 4.9 Từ frame rate của encoder tới chunk size và lookahead

### 4.9.1 Thang frame rate trong pipeline

```text
Tầng                               Tốc độ        Mỗi bước
waveform 48 kHz (mic/WebRTC)       48 000 Hz     20.8 µs
waveform 16 kHz (ASR)              16 000 Hz     62.5 µs
frame transport                    50 Hz         20 ms
cửa sổ Silero VAD                  31.25 Hz      32 ms
log-mel (hop 10 ms)                100 Hz        10 ms
encoder Whisper (stride 2)         50 Hz         20 ms
encoder Conformer (4×)             25 Hz         40 ms
encoder FastConformer / AuT (8×)   12.5 Hz       80 ms
âm tiết tiếng Việt (ước lượng)     ~4–6 Hz       ~170–250 ms
mel TTS 22.05 kHz, hop 256         ~86.1 Hz      ~11.6 ms
mel TTS 24 kHz, hop 256            93.75 Hz      ~10.7 ms
token codec Qwen3-TTS              12.5 Hz      80 ms
```

Mỗi tầng có "đồng hồ" riêng. Đây là câu trả lời ngắn cho "vì sao VAD, ASR, TTS dùng chunk khác nhau": **mỗi model chỉ xử lý được bội số của bước thời gian riêng của nó**, cộng với ngữ cảnh nó cần nhìn.

### 4.9.2 Feature extraction khi streaming

Khi audio đến theo chunk, STFT phải "nối" các chunk:

- Frame cuối cùng có thể tính được là frame có cửa sổ 400 mẫu nằm trọn trong dữ liệu đã nhận. Với chunk 320 ms (5 120 mẫu), từ một buffer rỗng bạn tính được 1 + (5 120 − 400) / 160 = **30.5 → 30** frame, và giữ lại **phần dư** (5 120 − 30 × 160 = 320 mẫu, trong đó 240 mẫu là phần chồng của frame kế tiếp) cho lần sau.
- Như vậy, ngay cả trước encoder, đặc trưng đã có **lookahead tự nhiên = window − hop = 15 ms**: frame có tâm tại t cần audio tới t + 12.5 ms (với `center=True`).
- `center=True` offline pad phản xạ ở đầu và cuối file; streaming không thể pad phía tương lai. Các frame giữa câu khớp hoàn toàn; chỉ vài frame ở biên lệch. Model streaming được train đúng cách sẽ chịu được, nhưng **test parity offline vs streaming** phải loại trừ biên hoặc dùng `center=False` cả hai phía.
- Chuẩn hoá phải là loại streaming được (§4.5.6).
- Code mẫu: `StreamingLogMel` ở §4.11.3.

### 4.9.3 Chunk, lookahead và sàn độ trễ của ASR streaming

Với ASR streaming chunk-based (như cache-aware FastConformer), độ trễ tối thiểu để có token cho một sự kiện âm thanh:

```text
độ trễ ≥ thời gian chờ đủ chunk (≤ chunk size)
        + lookahead phải (right context)
        + lookahead của STFT (~15 ms) và của conv subsampling
        + compute + transport + chính sách commit (§5.4.1 tài liệu thiết kế)
```

Với Nemotron 3.5, `att_context_size = [56, R]` tính theo frame 80 ms (**Reported**):

| `att_context_size` | Chunk = (R+1) frame | Thời lượng chunk | Left context |
|---|---|---|---|
| [56, 0] | 1 | 80 ms | 56 × 80 ms = 4.48 s |
| [56, 1] | 2 | 160 ms | 4.48 s |
| [56, 3] | 4 | 320 ms | 4.48 s |
| [56, 6] | 7 | 560 ms | 4.48 s |
| [56, 13] | 14 | 1 120 ms | 4.48 s |

(Cột left context 4.48 s là phép nhân, **Synthesis**.)

Đọc bảng: chunk lớn hơn → model thấy nhiều "tương lai" hơn trong cùng chunk → WER tiếng Việt FLEURS giảm từ 13.41 (80 ms) xuống 11.18 (1 120 ms) (**Reported**). Đó là trade-off chunk/độ chính xác, cùng bản chất với trade-off thời gian–tần số: muốn quyết định chắc hơn thì phải chờ nhiều dữ liệu hơn.

Ngược lại với Whisper: không có chunk nhỏ tự nhiên. Bọc nó trong cửa sổ trượt (WhisperLiveKit) là **buffered/policy streaming**: mỗi lần chạy lại encoder trên 30 s (padding phần thiếu), rồi dùng chính sách ổn định prefix để commit (§5.4.1 tài liệu thiết kế, **Synthesis** từ wiki). Chi phí và độ trễ vì thế không giảm theo chunk nhỏ.

### 4.9.4 Vì sao không ép VAD, ASR, TTS dùng chung chunk

Tài liệu thiết kế §7.1 ghi: "Không bắt VAD, ASR và TTS dùng chung một chunk length" (**Synthesis**). Lý giải theo DSP:

- **VAD** muốn phản ứng nhanh: 32 ms là đơn vị nhỏ nhất của Silero.
- **ASR streaming** muốn chunk là bội của 80 ms (FastConformer) và có thể đổi 160/320 ms để đổi độ chính xác; ASR turn-final thì muốn **cả lượt**.
- **Turn detector** muốn **cả lượt tới 8 s**, gọi lại khi có audio mới.
- **TTS** sinh audio theo bước vocoder/codec (hop 256 mẫu ở 22.05/24 kHz, hoặc 80 ms/token codec) và trả về theo chunk của server (Chương 3, Chương 13); playback lại muốn khối 10–20 ms ở 48 kHz.

Chọn một chunk chung nghĩa là ép ít nhất một thành phần chạy sai điểm tối ưu. Kiến trúc đúng: transport 20 ms vào **ring buffer** theo thời gian của session, mỗi consumer (VAD, ASR, turn) **đọc theo nhịp riêng** từ buffer đó, với timestamp tính bằng mẫu (Chương 16).

---

## 4.10 (Nâng cao) Inverse STFT, Griffin-Lim, vì sao cần vocoder

### 4.10.1 Inverse STFT

Nếu giữ **cả biên độ và pha**, STFT đảo ngược được hoàn hảo bằng **overlap-add**: IFFT từng frame, nhân cửa sổ tổng hợp, cộng chồng theo hop. Điều kiện để tổng cửa sổ phẳng là COLA (constant overlap-add): Hann với overlap 50% hoặc 75% thoả. Đây là nền của mọi hệ "phân tích → sửa phổ → tổng hợp": denoiser miền phổ (Chương 7), vocoder kiểu iSTFT.

### 4.10.2 Mất pha và mất chi tiết

Log-mel mất ba thứ: **pha**, **độ phân giải tần số** (201 bin gộp thành 80), và **thông tin dưới floor**. Từ log-mel:

1. Đảo mel → phổ tuyến tính: dùng pseudo-inverse hoặc NNLS của filterbank, chỉ là xấp xỉ (vùng tần cao bị "nhoè").
2. Đoán pha: **Griffin-Lim** lặp giữa "STFT nhất quán" và "biên độ cho trước", hội tụ dần về một pha hợp lý.

Kết quả Griffin-Lim nghe được nhưng **"kim loại", rè, có tiếng vang pha (phasiness)**, và tốn nhiều vòng lặp (thường 32–100). Không dùng được cho sản phẩm realtime chất lượng.

### 4.10.3 Vocoder

Vocoder neural (WaveNet, WaveRNN → HiFi-GAN, BigVGAN, Vocos…) học ánh xạ **mel → waveform** trực tiếp, tự sinh pha và chi tiết hợp lý. Hai họ chính:

- **Sinh waveform bằng upsampling conv** (HiFi-GAN, BigVGAN): từ mel ở ~86–94 Hz upsample ×256 lên tốc độ mẫu.
- **Sinh hệ số STFT rồi iSTFT** (Vocos và các vocoder kiểu iSTFT): mạng dự đoán biên độ và pha, rồi dùng iSTFT ở §4.10.1. Nhanh hơn vì phần upsampling nặng được thay bằng FFT.

TTS hiện đại thường bỏ qua mel: model sinh **token của neural codec** (12.5–86 Hz, Chương 3 §3.8) và **decoder của codec** đóng vai trò vocoder. Hệ quả cho streaming: vocoder/decoder cần **ngữ cảnh** ở biên chunk (receptive field của conv), nên TTS streaming phải chồng lấn hoặc giữ state ở biên, nếu không sẽ nghe "tách" giữa các chunk. Chi tiết ở Chương 13.

---

## 4.11 Code tham khảo

Code dưới đây cần `numpy` (và `scipy`, `librosa`, `soundfile` cho một số phần). Mục đích là **hiểu và test parity**, không thay thế extractor chính thức của từng model. Chưa chạy trong repo này (môi trường hiện tại không có numpy); hãy chạy và so sánh với thư viện gốc trước khi tin.

### 4.11.1 STFT và mel filterbank từ đầu

```python
import numpy as np

def hann_periodic(n: int) -> np.ndarray:
    # Periodic Hann, giống torch.hann_window(n) mặc định
    return (0.5 - 0.5 * np.cos(2 * np.pi * np.arange(n) / n)).astype(np.float32)

def stft_power(x: np.ndarray, n_fft=400, hop=160, center=True, pad_mode="reflect") -> np.ndarray:
    """Trả về power spectrogram shape (T, n_fft//2 + 1)."""
    x = np.asarray(x, dtype=np.float32)
    if center:
        x = np.pad(x, n_fft // 2, mode=pad_mode)
    if len(x) < n_fft:
        return np.zeros((0, n_fft // 2 + 1), np.float32)
    n_frames = 1 + (len(x) - n_fft) // hop
    idx = np.arange(n_fft)[None, :] + hop * np.arange(n_frames)[:, None]
    frames = x[idx] * hann_periodic(n_fft)
    spec = np.fft.rfft(frames, n=n_fft, axis=1)
    return (np.abs(spec) ** 2).astype(np.float32)

def _hz_to_mel_slaney(f):
    f = np.asarray(f, dtype=np.float64)
    f_sp, min_log_hz = 200.0 / 3, 1000.0
    min_log_mel, logstep = min_log_hz / f_sp, np.log(6.4) / 27.0
    return np.where(f >= min_log_hz,
                    min_log_mel + np.log(np.maximum(f, 1e-10) / min_log_hz) / logstep,
                    f / f_sp)

def _mel_to_hz_slaney(m):
    m = np.asarray(m, dtype=np.float64)
    f_sp, min_log_hz = 200.0 / 3, 1000.0
    min_log_mel, logstep = min_log_hz / f_sp, np.log(6.4) / 27.0
    return np.where(m >= min_log_mel,
                    min_log_hz * np.exp(logstep * (m - min_log_mel)),
                    f_sp * m)

def mel_filterbank(sr=16000, n_fft=400, n_mels=80, fmin=0.0, fmax=None) -> np.ndarray:
    """Slaney mel + norm='slaney', tương đương librosa.filters.mel mặc định. Shape (n_mels, n_fft//2+1)."""
    fmax = fmax or sr / 2
    mel_pts = np.linspace(_hz_to_mel_slaney(fmin), _hz_to_mel_slaney(fmax), n_mels + 2)
    hz_pts = _mel_to_hz_slaney(mel_pts)
    fft_freqs = np.linspace(0, sr / 2, n_fft // 2 + 1)
    fdiff = np.diff(hz_pts)
    ramps = hz_pts[:, None] - fft_freqs[None, :]
    lower = -ramps[:-2] / fdiff[:-1, None]
    upper = ramps[2:] / fdiff[1:, None]
    weights = np.maximum(0, np.minimum(lower, upper))
    enorm = 2.0 / (hz_pts[2:n_mels + 2] - hz_pts[:n_mels])   # chuẩn hoá diện tích (slaney)
    return (weights * enorm[:, None]).astype(np.float32)

# Kiểm tra kích thước (Q1):
sr = 16000
x = np.random.randn(sr).astype(np.float32) * 0.01      # 1 s
P = stft_power(x, 400, 160, center=True)
print(P.shape)            # (101, 201)
print(stft_power(x, 400, 160, center=False).shape)    # (98, 201)
M = mel_filterbank(sr, 400, 80)
print((P @ M.T).shape)    # (101, 80)

# Parity với librosa (nếu có): sai số nhỏ cỡ 1e-6
# import librosa
# assert np.allclose(M, librosa.filters.mel(sr=sr, n_fft=400, n_mels=80), atol=1e-6)
```

### 4.11.2 Log-mel kiểu Whisper và test parity

```python
SR, N_FFT, HOP, CHUNK_S = 16000, 400, 160, 30
N_SAMPLES = SR * CHUNK_S            # 480 000
N_FRAMES = N_SAMPLES // HOP         # 3 000

def whisper_log_mel(audio: np.ndarray, n_mels=80) -> np.ndarray:
    """audio: float32 [-1,1], 16 kHz mono. Trả về (n_mels, 3000).
    n_mels=128 cho large-v3/turbo. Đây là bản tái tạo để học; biên có thể lệch nhẹ
    so với implementation gốc (pad audio trước hay pad mel sau)."""
    audio = np.asarray(audio, np.float32)[:N_SAMPLES]
    audio = np.pad(audio, (0, N_SAMPLES - len(audio)))           # pad zero tới 30 s
    P = stft_power(audio, N_FFT, HOP, center=True)[:-1]          # 3001 → 3000 frame
    mel = P @ mel_filterbank(SR, N_FFT, n_mels).T                # (3000, n_mels)
    log_spec = np.log10(np.maximum(mel, 1e-10))
    log_spec = np.maximum(log_spec, log_spec.max() - 8.0)        # kẹp dải động 80 dB
    return ((log_spec + 4.0) / 4.0).T.astype(np.float32)

# Test parity (cần transformers):
# from transformers import WhisperFeatureExtractor
# fe = WhisperFeatureExtractor(feature_size=80)
# ref = fe(audio, sampling_rate=16000, return_tensors="np").input_features[0]
# mine = whisper_log_mel(audio, 80)
# print(np.abs(ref - mine).max())        # kỳ vọng ~1e-4 hoặc nhỏ hơn, lệch lớn hơn ở biên

# Thí nghiệm quan sát lỗi thang biên độ (§4.5.7):
# m1 = whisper_log_mel(audio); m2 = whisper_log_mel(audio * 32768)
# print((m2 - m1)[:, :100].mean())       # ≈ +2.26 trên vùng có tiếng
```

### 4.11.3 Log-mel streaming có state

```python
class StreamingLogMel:
    """Log-mel tương đương offline center=False. Mỗi session một instance.
    Chuẩn hoá: không làm ở đây (dùng global stats hoặc theo model)."""
    def __init__(self, sr=16000, n_fft=400, hop=160, n_mels=80, log_floor=1e-10):
        self.n_fft, self.hop = n_fft, hop
        self.win = hann_periodic(n_fft)
        self.fb = mel_filterbank(sr, n_fft, n_mels)
        self.log_floor = log_floor
        self.buf = np.zeros(0, np.float32)
        self.frames_emitted = 0          # để gắn timestamp: frame i có tâm tại (i*hop + n_fft/2)/sr

    def push(self, pcm: np.ndarray) -> np.ndarray:
        self.buf = np.concatenate([self.buf, np.asarray(pcm, np.float32)])
        if len(self.buf) < self.n_fft:
            return np.zeros((0, self.fb.shape[0]), np.float32)
        n = 1 + (len(self.buf) - self.n_fft) // self.hop
        idx = np.arange(self.n_fft)[None, :] + self.hop * np.arange(n)[:, None]
        spec = np.fft.rfft(self.buf[idx] * self.win, n=self.n_fft, axis=1)
        mel = (np.abs(spec) ** 2) @ self.fb.T
        self.buf = self.buf[n * self.hop:]       # giữ phần dư (≥ n_fft - hop mẫu chồng lấn)
        self.frames_emitted += n
        return np.log10(np.maximum(mel, self.log_floor)).astype(np.float32)

    def reset(self):
        self.buf = np.zeros(0, np.float32)
        self.frames_emitted = 0

# Test: ghép output streaming phải bằng offline center=False
# x = ...; s = StreamingLogMel()
# out = np.concatenate([s.push(c) for c in np.array_split(x, 37)])
# ref = np.log10(np.maximum(stft_power(x, 400, 160, center=False) @ s.fb.T, 1e-10))
# assert np.allclose(out, ref, atol=1e-5)
```

Bài học trong code: số frame mỗi lần `push` **không cố định** (phụ thuộc phần dư), nên consumer phải xử lý số frame thay đổi, và timestamp tính từ `frames_emitted`, không phải từ số lần gọi.

### 4.11.4 RMS, ZCR, F0 và ảnh 6 thanh

```python
import numpy as np, soundfile as sf, librosa, librosa.display
import matplotlib.pyplot as plt

def frame_rms_dbfs(x, win=400, hop=160):
    n = 1 + max(0, len(x) - win) // hop
    idx = np.arange(win)[None, :] + hop * np.arange(n)[:, None]
    rms = np.sqrt(np.mean(x[idx] ** 2, axis=1))
    return 20 * np.log10(rms + 1e-12)

def frame_zcr(x, win=400, hop=160):
    n = 1 + max(0, len(x) - win) // hop
    idx = np.arange(win)[None, :] + hop * np.arange(n)[:, None]
    s = np.signbit(x[idx])
    return np.mean(s[:, 1:] != s[:, :-1], axis=1)

# Ghi âm "ma mà má mả mã mạ" (mỗi âm tiết một file hoặc một file có khoảng lặng)
y, sr = sf.read("sau_thanh.wav", dtype="float32")
if y.ndim > 1: y = y.mean(axis=1)
if sr != 16000: y = librosa.resample(y, orig_sr=sr, target_sr=16000); sr = 16000

f0, voiced, _ = librosa.pyin(y, fmin=60, fmax=500, sr=sr, frame_length=1024, hop_length=160)
t = librosa.times_like(f0, sr=sr, hop_length=160)

fig, ax = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
# (1) Narrowband: window 64 ms → thấy harmonics và đường F0
S_nb = librosa.amplitude_to_db(np.abs(librosa.stft(y, n_fft=1024, hop_length=160)), ref=np.max)
librosa.display.specshow(S_nb, sr=sr, hop_length=160, x_axis="time", y_axis="hz", ax=ax[0])
ax[0].plot(t, f0, color="w", lw=2); ax[0].set_ylim(0, 2000); ax[0].set_title("Narrowband + F0 (pYIN)")
# (2) Wideband: window 5 ms → thấy formant, burst, nhịp dọc của giọng kẹt
S_wb = librosa.amplitude_to_db(np.abs(librosa.stft(y, n_fft=256, win_length=80, hop_length=40)), ref=np.max)
librosa.display.specshow(S_wb, sr=sr, hop_length=40, x_axis="time", y_axis="hz", ax=ax[1])
ax[1].set_title("Wideband")
# (3) Thứ model nhìn thấy: log-mel 80, 25/10 ms
M = librosa.power_to_db(librosa.feature.melspectrogram(y=y, sr=sr, n_fft=400, hop_length=160, n_mels=80))
librosa.display.specshow(M, sr=sr, hop_length=160, x_axis="time", y_axis="mel", ax=ax[2])
ax[2].set_title("Log-mel 80 (đầu vào kiểu ASR)")
plt.tight_layout(); plt.savefig("sau_thanh.png", dpi=120)
```

Quan sát cần ghi lại: (a) contour F0 của từng thanh; (b) chỗ pYIN báo unvoiced hoặc nhảy quãng tám ở ngã/nặng; (c) cái gì còn và cái gì mất khi chuyển từ (1) sang (3).

### 4.11.5 High-pass streaming có state

```python
from scipy.signal import butter, sosfilt

class StreamingHighPass:
    """Butterworth high-pass, giữ state giữa các chunk. Mỗi session/kênh một instance."""
    def __init__(self, sr=16000, cutoff_hz=80.0, order=2):
        self.sos = butter(order, cutoff_hz, btype="highpass", fs=sr, output="sos")
        self.zi = np.zeros((self.sos.shape[0], 2))

    def process(self, x: np.ndarray) -> np.ndarray:
        y, self.zi = sosfilt(self.sos, x, zi=self.zi)
        return y.astype(np.float32)

    def reset(self):
        self.zi[:] = 0.0

# Sai: y = sosfilt(sos, chunk) cho từng chunk (reset state mỗi chunk → click ở biên)
# Sai trong streaming: sosfiltfilt (không causal, cần thấy tương lai)
```

---

# Tự kiểm tra

## 4.12 Lỗi kinh điển: triệu chứng → nguyên nhân → cách sửa

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| Model ONNX/GGUF tự port cho WER tệ hơn bản gốc nhiều, không lỗi | Feature extractor lệch một tham số (mel scale, norm, `center`, pre-emphasis, log base) | Test parity với extractor gốc trên cùng file (§4.11.2), đi qua checklist §4.5.7 |
| Log-mel lệch đều một hằng số lớn | Thang biên độ int16 vs float | Thống nhất float [-1, 1] ở gateway; nhân 32 768 chỉ khi model yêu cầu |
| Lỗi shape hoặc output rác dù shape "đúng" | `(F, T)` vs `(T, F)` | Assert shape rõ ràng tại biên model |
| Streaming tệ hơn offline rõ rệt với cùng model | CMVN per-utterance tính trên từng chunk; hoặc model không phải streaming | Dùng global/streaming CMVN; chọn model streaming thật (§5.4.1 thiết kế) |
| Click/vạch dọc định kỳ ở chunk boundary trên spectrogram | Filter/resampler/STFT không giữ state giữa chunk | Một instance có state per session (§4.7.3, §4.11.3) |
| Whisper trả "cảm ơn các bạn đã xem" cho đoạn im lặng | Clip không có tiếng nói đi vào ASR; decoder dùng prior | VAD trước, gate năng lượng/thời lượng, lọc `no_speech_prob`, blacklist (§4.8.2) |
| Whisper encoder báo lỗi shape với clip ngắn | Không pad tới 3 000 frame | Pad 30 s (feature extractor làm sẵn) |
| ASR nhầm thanh ngã/nặng, nhất là cuối câu | Cắt đuôi âm tiết: `speech_pad_ms` nhỏ, chunk cắt cứng | Tăng pad 100–200 ms, pre-roll 200–300 ms (§5.2, §7.1 thiết kế) |
| Silero VAD xác suất "kỳ lạ" khi gọi ONNX trực tiếp | Sai độ dài cửa sổ, thiếu context, sai sample rate, không giữ state | Dùng wrapper chính thức hoặc tái tạo đúng; 512 mẫu @16 kHz |
| Smart Turn dự đoán kém với lượt dài | Đưa 8 s **đầu** thay vì 8 s **cuối**, hoặc pad ở cuối | Cắt từ đầu, pad zero ở đầu (§4.8.3) |
| Pitch tracker cho F0 nhảy đôi/nhảy nửa | Octave error, creaky voice, `fmin`/`fmax` sai | Dùng pYIN, đặt dải hợp lý, cửa sổ ≥ 2 chu kỳ `fmin` |
| ZCR luôn ~0 với một thiết bị | DC offset | High-pass 60–80 Hz trước |
| Số frame mel lệch 2–3 giữa hai thư viện | `center`/`snip_edges` khác | Chọn một quy ước, document vào audio contract |

## 4.13 Thực hành

1. **Tính tay rồi kiểm bằng code:** với 1 s ở 16 kHz, window 25 ms, hop 10 ms, `n_fft` 400 và 512, `center` True/False: số frame, số bin, Δf. So với output `stft_power`.
2. **Mel filterbank:** vẽ 80 và 128 bộ lọc Slaney trên cùng trục; vẽ thêm 80 bộ lọc HTK. Đếm số bộ lọc dưới 1 kHz và đối chiếu với bảng §4.5.2.
3. **Parity Whisper:** so `whisper_log_mel` với `WhisperFeatureExtractor` (80 và 128). Ghi sai số tối đa, chỉ ra sai số tập trung ở đâu (biên?).
4. **Thang biên độ:** đưa cùng một file vào extractor Whisper ở thang float và int16. Đo độ lệch trung bình, so với con số 2.26.
5. **6 thanh:** ghi âm "ma mà má mả mã mạ" (giọng của bạn và nếu được, một giọng khác vùng). Chạy §4.11.4. Viết 6 dòng mô tả khác biệt trên narrowband, wideband và log-mel. Đánh dấu chỗ pYIN thất bại.
6. **Cắt đuôi:** cắt bỏ 50, 100, 150 ms cuối của từng âm tiết "mã", "mạ". Nghe lại, và (nếu có ASR) cho Whisper/PhoWhisper nhận dạng từng phiên bản. Ghi lại khi nào thanh bị nhận sai.
7. **Hallucination:** đưa vào faster-whisper `language="vi"`: 1 s im lặng số, 3 s tiếng quạt, 5 s nhạc, 0.4 s "ừ". Ghi output, `no_speech_prob`, `avg_logprob`, `compression_ratio` (gợi ý ở Phụ lục B đề cương).
8. **Streaming:** chạy `StreamingLogMel` với chunk ngẫu nhiên 1–700 mẫu; assert bằng offline `center=False`. Thử bỏ dòng giữ phần dư và quan sát spectrogram.
9. **Lọc:** thêm DC offset 0.05 và hum 50 Hz vào một file; quan sát spectrogram và ZCR; áp `StreamingHighPass` 80 Hz theo chunk 20 ms; so với lọc từng chunk không giữ state.
10. **Đọc config:** mở `model_config.yaml` của một checkpoint NeMo (Nemotron 3.5 hoặc Parakeet) và `preprocessor_config.json` của một checkpoint Whisper/PhoWhisper. Điền bảng §4.5.7 cho từng model.

## 4.14 Đáp án các câu hỏi tự kiểm tra

**Q1. STFT với window 25 ms, hop 10 ms ở 16 kHz cho ra bao nhiêu frame mỗi giây? Mỗi frame có bao nhiêu bin?**

- Window 25 ms = 400 mẫu, hop 10 ms = 160 mẫu → **100 frame mỗi giây** (frame rate = sr / hop = 16 000 / 160).
- Số frame chính xác cho đúng 1 s phụ thuộc biên: **101** với `center=True` (librosa/torch/Whisper), **98** với `center=False` (Kaldi `snip_edges`).
- Số bin = `n_fft/2 + 1`: **201** bin với `n_fft=400` (Δf = 40 Hz, như Whisper); **257** bin với `n_fft=512` (Δf = 31.25 Hz, như NeMo; phần pad zero không tăng độ phân giải thật).
- Sau mel filterbank còn **80 hoặc 128** giá trị mỗi frame. Encoder sau đó subsample: Whisper còn 50 frame/s, Conformer 25, FastConformer 12.5.

**Q2. Whisper nhận input gì? Vì sao clip ngắn hoặc im lặng dễ sinh hallucination?**

- Input: audio 16 kHz mono float32 → log-mel Hann 400/160, `n_fft=400`, mel Slaney 0–8 kHz, **80 bin** (≤ large-v2, nhiều fine-tune như PhoWhisper; kiểm tra checkpoint) hoặc **128 bin** (large-v3, large-v3-turbo; **Reported**), `log10` với floor 1e-10, kẹp 8 đơn vị dưới đỉnh, `(x+4)/4`.
- Cửa sổ **đúng 30 s** = 3 000 frame mel → 1 500 vị trí encoder × 20 ms. Ngắn hơn thì **pad zero** tới 30 s; dài hơn thì phải dùng thuật toán long-form (sequential hoặc chunked 30 s, **Reported**).
- Hallucination (**Synthesis** về cơ chế, hiện tượng **Reported**): decoder là LM có điều kiện, train trên phụ đề Internet có những câu "kết video" ở đoạn im lặng; khi bằng chứng âm học ít (clip ngắn chìm trong padding, im lặng, nhạc, nhiễu, audio quá nhỏ) thì prior của LM thắng; không có VAD bên trong, chỉ có ngưỡng mềm `no_speech`; và `condition_on_previous_text` có thể lan lỗi. Phòng bằng VAD trước, gate năng lượng/thời lượng, `language="vi"`, `temperature=0`, lọc sau decode và blacklist (§5.4.4 tài liệu thiết kế).

**Q3. Spectrogram của 6 thanh tiếng Việt khác nhau ở đâu?**

- **Đường F0**, thấy rõ nhất trên narrowband spectrogram là độ cao và độ dốc của các vạch harmonics: ngang bằng ở mức giữa–cao; huyền thấp, xuống nhẹ; sắc đi lên; hỏi xuống rồi có thể lên lại; ngã đi lên nhưng đứt quãng; nặng thấp, rơi nhanh.
- **Chất giọng**: huyền có thể hơi thở (harmonics trên mờ); ngã có glottal stop/creaky **giữa** âm tiết (harmonics biến mất, nhịp dọc thưa và không đều, năng lượng tụt); nặng có tắc thanh hầu/creaky **cuối** âm tiết.
- **Trường độ**: nặng (và sắc trong âm tiết tắc -p/-t/-c/-ch) ngắn và kết thúc đột ngột.
- Trên log-mel 80 bin, harmonics tần cao bị gộp, nhưng bộ lọc tần thấp hẹp (~37 Hz; ~23 Hz với 128 bin) còn giữ dấu vết F0; khe năng lượng và độ dài vẫn thấy rõ. Giọng Nam nhập hỏi–ngã và nặng ít thanh hầu hoá, nên các khác biệt trên đổi theo phương ngữ.
- Hệ quả: phần phân biệt ngã/nặng nằm ở giữa và cuối âm tiết. Không được cắt đuôi (pad VAD, pre-roll), và phải đo ASR/TTS riêng theo thanh và theo vùng.

---

## 4.15 Tóm tắt một trang

- **Đặc trưng là hợp đồng giữa train và chạy.** Đừng chọn tham số cho model đã train; đọc config và tái tạo đúng. Lệch đặc trưng là lỗi im lặng.
- **Chuỗi chuẩn:** waveform → frame 25 ms/hop 10 ms → Hann → FFT (`n_fft` 400/512 → 201/257 bin) → power → mel 80/128 → log (+floor) → chuẩn hoá → 100 frame/s → encoder subsample 2×/4×/8×.
- **Trade-off thời gian–tần số:** window ngắn thấy formant/burst; window dài thấy harmonics/F0. Zero-pad (`n_fft` > window) không tăng độ phân giải thật.
- **Mel:** HTK (torchaudio, Kaldi) ≠ Slaney (librosa, Whisper); `norm` cũng khác. 80 bin Slaney 0–8 kHz: ~37 Hz giữa các tâm dưới 1 kHz; 128 bin: ~23 Hz.
- **MFCC** = DCT(log-mel), bỏ phần lớn thông tin F0; model hiện đại dùng log-mel hoặc waveform.
- **Pre-emphasis 0.97**: có ở Kaldi/NeMo, không có ở Whisper. **CMVN per-utterance** không dùng được khi streaming; dùng global/sliding hoặc model `normalize: NA`.
- **int16 vs float**: lệch log10 +9.03 (ln +20.8; Whisper +2.26 sau chuẩn hoá).
- **Đặc trưng đơn giản** (RMS/dBFS, ZCR, F0) cho gate, sàn nhiễu thích ứng, monitoring, phân tích thanh điệu. Pitch cần window ≥ 2 chu kỳ `fmin`.
- **Lọc streaming phải giữ state**; high-pass 60–100 Hz bỏ DC/hum; không `filtfilt` khi streaming.
- **Model trong pipeline:** Silero = waveform 512 mẫu @16 kHz, có state; Whisper = log-mel 80/128, **đúng 30 s**, pad zero, encoder 20 ms; Smart Turn = ≤ 8 s, **cắt đầu, pad đầu**, gọi lại trên toàn lượt; FastConformer = log-mel NeMo, **8× → 80 ms/frame**, chunk Nemotron = (R+1) × 80 ms; Kaldi/WeNet = fbank Povey, `snip_edges`, coi chừng thang int16.
- **Mỗi tầng có đồng hồ riêng** (32 ms VAD, 10 ms mel, 20/40/80 ms encoder, ~11 ms mel TTS, 80 ms codec) → không ép chung chunk; dùng ring buffer + timestamp theo mẫu.
- **Sàn độ trễ ASR streaming** = chờ chunk + lookahead + ~15 ms STFT + compute + commit. Chunk lớn hơn = chính xác hơn, chậm hơn (Nemotron vi FLEURS 13.41 → 11.18 từ 80 → 1 120 ms, **Reported**).
- **Log-mel không đảo ngược sạch được** (mất pha, mất chi tiết): Griffin-Lim nghe "kim loại"; TTS dùng vocoder neural hoặc decoder của codec.

## 4.16 Liên kết

**Chương sau:** Chương 5 (ngữ âm và chữ viết tiếng Việt: thanh điệu ở phía văn bản), Chương 7 (front-end: denoise miền phổ, AEC, AGC), Chương 9 (encoder, subsampling, CTC/RNNT/attention), Chương 10 (VAD, endpointing, turn detection chi tiết), Chương 11 (hành vi streaming của ASR), Chương 13 (vocoder, neural codec), Chương 16 (audio contract, ring buffer, timestamp), Chương 21 (đánh giá thanh điệu trong TTS/ASR).

**Chương trước:** [Chương 1](chuong-01-vat-ly-am-thanh-va-co-che-tao-tieng-noi.md) (source–filter, F0, formant, thanh điệu, đọc spectrogram), [Chương 2](chuong-02-so-hoa-am-thanh-tu-song-toi-mang-so.md) (sample rate, dtype, reblock 20 ms → 512 mẫu, resample có state), [Chương 3](chuong-03-dinh-dang-file-container-va-codec.md) (codec, neural codec).

**Tài liệu thiết kế:** [§5.2, §5.3, §5.4.1, §5.4.4, §7.1](thiet-ke-pipeline-speech-to-speech-tieng-viet.md).

**Wiki:**

- [Whisper Large v3](../wiki/whisper-large-v3.md): 128 mel bin (so với 80), cửa sổ tiếp nhận 30 s, long-form sequential/chunked, hallucination và lặp.
- [Whisper Large v3 Turbo](../wiki/whisper-large-v3-turbo.md): cắt decoder 32 → 4 lớp, kế thừa input của v3.
- [Whisper Hallucination Mitigation](../wiki/whisper-hallucination-mitigation.md): tham số decode, lọc sau decode, blacklist tiếng Việt.
- [Faster-Whisper](../wiki/faster-whisper.md): runtime CT2, `vad_filter`.
- [Smart Turn v3.2](../wiki/smart-turn.md): encoder Whisper Tiny, 16 kHz, ≤ 8 s, cắt/pad ở đầu, gọi lại trên toàn lượt, benchmark tiếng Việt.
- [Silero VAD](../wiki/silero-vad.md): 8/16 kHz, cửa sổ 512/256 mẫu từ v5, `VADIterator` per session, tham số khởi điểm.
- [Nemotron 3.5 ASR Streaming](../wiki/nemotron-3.5-asr-streaming-0.6b.md): FastConformer cache-aware, frame 80 ms, `att_context_size`, đường cong WER tiếng Việt theo chunk.
- [Qwen3-ASR family](../wiki/qwen3-asr-family.md): encoder AuT giảm 8× về 12.5 Hz.
- [NeMo Speech ASR Configuration](../wiki/nemo-speech-asr-configuration.md): masker VAD trên log-mel, endpointing theo im lặng.
- [Qwen3-TTS Tokenizer 12Hz](../wiki/qwen3-tts-tokenizer-12hz.md): codec 12.5 Hz phía TTS.

**Đọc thêm ngoài wiki (giáo trình và tài liệu chuẩn, gợi ý):** Rabiner & Schafer, *Theory and Applications of Digital Speech Processing*; Jurafsky & Martin, *Speech and Language Processing* (chương về ASR và đặc trưng); Oppenheim & Schafer, *Discrete-Time Signal Processing* (DFT, cửa sổ, FIR/IIR); Davis & Mermelstein (1980) về MFCC; Griffin & Lim (1984), *Signal estimation from modified short-time Fourier transform*; de Cheveigné & Kawahara (2002) YIN; Mauch & Dixon (2014) pYIN; Gulati et al. (2020) Conformer; Rekesh et al. (2023) Fast Conformer; Radford et al. (2022) Whisper; Kong et al. (2020) HiFi-GAN; Siuzdak (2023) Vocos; tài liệu librosa (`stft`, `filters.mel`, `pyin`), torchaudio (`transforms.MelSpectrogram`, `compliance.kaldi.fbank`), NeMo (`AudioToMelSpectrogramPreprocessor`), SciPy (`signal.butter`, `sosfilt`).
