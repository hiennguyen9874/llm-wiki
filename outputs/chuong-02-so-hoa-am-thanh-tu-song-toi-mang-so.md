# Chương 2. Số hoá âm thanh: từ sóng tới mảng số 🔴

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần I.
> **Chương trước:** [Chương 1. Vật lý âm thanh và cơ chế tạo tiếng nói](chuong-01-vat-ly-am-thanh-va-co-che-tao-tieng-noi.md).
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §3 nguyên tắc 4 (audio contract), §5.1 (lỗi lệch sample rate, telephony 8 kHz), §7.1 (reblock 20 ms → 512 samples).
> **Cơ sở:** phần lớn là kiến thức giáo trình chuẩn về xử lý tín hiệu số (DSP) và thực hành lập trình audio, không phải claim lấy từ nguồn trong wiki. Những chỗ dẫn từ tài liệu thiết kế hoặc wiki được ghi rõ và giữ nguyên nhãn bằng chứng (**Reported**, **Synthesis**…). Hành vi mặc định của thư viện (numpy, soundfile, librosa, torchaudio, soxr…) là theo hiểu biết chung tại thời điểm viết; hãy kiểm tra lại với phiên bản bạn cài đặt.

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Nhìn một buffer audio (bytes hoặc mảng numpy) và nói chính xác nó chứa gì: sample rate, dtype, số kênh, layout, endianness, thời lượng.
2. Tính nhẩm được quy đổi **ms ↔ samples ↔ bytes** cho mọi định dạng gặp trong pipeline.
3. Giải thích Nyquist, aliasing, sai số lượng tử, dynamic range, clipping, và biết hậu quả cụ thể của từng thứ lên VAD/ASR/TTS.
4. Quy đổi int16 ↔ float32 đúng, không clip sai, không lệch thang.
5. Chọn và dùng đúng resampler, đặc biệt phân biệt **resample stream có state** với resample từng chunk độc lập.
6. Viết được lớp "audio ingress" tối thiểu cho gateway: ghép bytes → samples, resample về 16 kHz mono, reblock 20 ms → 512 samples cho Silero VAD.
7. Chẩn đoán nhanh các lỗi kinh điển (giọng chipmunk, nhiễu trắng ầm ĩ, tiếng lách tách ở biên chunk, transcript rác) từ triệu chứng.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. 1 giây PCM16 mono 16 kHz nặng bao nhiêu byte? Cùng thời lượng đó ở 48 kHz stereo float32 thì sao?
- Q2. 512 samples ở 16 kHz là bao nhiêu ms? 20 ms ở 48 kHz là bao nhiêu samples?
- Q3. Upsample 8 kHz lên 16 kHz có khôi phục được thông tin không? Vì sao?
- Q4. Đọc int16 thành float32 mà quên chia 32768 thì chuyện gì xảy ra?

---

## 2.1 Chuỗi số hoá: từ áp suất tới mảng số

```text
áp suất ──► micro ──► preamp/gain ──► lọc anti-alias (analog) ──► ADC ──► số nguyên PCM
 (Ch.1)      (điện áp)  (AGC có thể ở đây)   (cắt > fs/2)         │
                                                                ├─ lấy mẫu (sampling): rời rạc hoá THỜI GIAN
                                                                └─ lượng tử (quantization): rời rạc hoá BIÊN ĐỘ
```

Hai phép rời rạc hoá độc lập:

| Phép | Tham số | Quyết định | Mất gì nếu chọn thấp |
|---|---|---|---|
| **Sampling** | sample rate `fs` (Hz) | Tần số cao nhất biểu diễn được = `fs/2` | Mất dải cao (âm xát, độ trong); sai thì sinh aliasing |
| **Quantization** | bit depth `N` | Độ phân giải biên độ, dynamic range ≈ 6 dB × N | Tăng nhiễu nền lượng tử; tín hiệu nhỏ bị "nhoè" |

Sau ADC, mọi thứ chỉ còn là **một dãy số**. Dãy số đó **không tự mang** thông tin về sample rate, dtype hay số kênh — các thông tin đó nằm ở header file (WAV, Chương 3), ở metadata của API, hoặc… chỉ trong đầu lập trình viên. Đó là gốc rễ của hầu hết bug trong chương này, và là lý do tài liệu thiết kế §3 đặt nguyên tắc 4: **mỗi backend khai báo rõ audio contract** (sample rate, dtype, số kênh, framing, cách cancel) (**Synthesis**).

---

## 2.2 Sampling: sample rate, Nyquist, aliasing

### 2.2.1 Sample rate

**Sample rate** `fs` là số mẫu mỗi giây mỗi kênh. Khoảng cách giữa hai mẫu là `Ts = 1/fs`:

| fs | Ts | Ghi chú |
|---|---|---|
| 8 kHz | 125 µs | Telephony narrowband |
| 16 kHz | 62.5 µs | Đầu vào chuẩn của ASR/VAD |
| 24 kHz | ~41.7 µs | Nhiều TTS neural, OpenAI Realtime PCM |
| 44.1 kHz | ~22.7 µs | CD, nhiều mic/sound card |
| 48 kHz | ~20.8 µs | Mic laptop/điện thoại, WebRTC/Opus, video |

### 2.2.2 Định lý Nyquist–Shannon

Một tín hiệu **giới hạn băng** (không có thành phần nào ≥ `fmax`) được khôi phục **hoàn hảo** từ các mẫu nếu:

```text
fs > 2 · fmax        ⇔        fmax < fs / 2   (fs/2 gọi là tần số Nyquist)
```

"Hoàn hảo" là thật, không phải xấp xỉ: tín hiệu liên tục giữa hai mẫu được nội suy chính xác bằng tổng các hàm `sinc`. Hai điều kiện ngầm hay bị quên:

1. Tín hiệu **phải** giới hạn băng trước khi lấy mẫu → cần **lọc anti-alias**.
2. Khôi phục cần bộ lọc lý tưởng (sinc dài vô hạn) → thực tế dùng bộ lọc hữu hạn, chấp nhận một dải chuyển tiếp (transition band) ngay dưới Nyquist. Vì thế audio 16 kHz thường chỉ có nội dung hữu ích tới ~7–7.6 kHz chứ không đủ 8 kHz.

### 2.2.3 Aliasing (chồng phổ)

Nếu có thành phần tần số `f > fs/2`, sau khi lấy mẫu nó **không biến mất** mà **gập** (fold) xuống dải `[0, fs/2]`:

```text
f_alias = | f − k · fs |   với k là số nguyên sao cho kết quả nằm trong [0, fs/2]
```

Ví dụ:

- Sin 6 kHz lấy mẫu ở 8 kHz → xuất hiện ở |6 − 8| = **2 kHz**. Trên mảng số, nó *giống hệt* một sin 2 kHz; không có cách nào phân biệt sau đó.
- Hạ 48 kHz → 16 kHz bằng cách **lấy 1 mẫu bỏ 2** (không lọc): năng lượng 8–24 kHz gập xuống 0–8 kHz. Tiếng "s" có năng lượng 6–10 kHz → phần 8–10 kHz gập thành 6–8 kHz; tiếng xì, hơi thở, nhiễu quạt cao tần thành tạp âm nằm *trong* băng ASR.

Aliasing đặc biệt độc vì:

- Nó **không đảo ngược được**: sau khi gập, tín hiệu thật và alias đã trộn vào nhau.
- Tai có thể không nhận ra ngay (nghe chỉ hơi "xì", "kim loại"), nhưng spectrogram cho thấy rõ: các vệt phổ **đi ngược chiều** (tần số thật đi lên thì alias đi xuống), hoặc vệt lạ không có harmonics đi kèm.

### 2.2.4 Lọc anti-alias

- **Phần cứng:** ADC hiện đại (sigma-delta oversampling) đã có lọc anti-alias số bên trong; khi bạn mở mic ở 16 kHz qua driver, thường đã an toàn.
- **Phần mềm:** mọi lần **giảm** sample rate (downsample) bạn tự làm thì **bạn** chịu trách nhiệm lọc. Resampler đúng chuẩn (soxr, libsamplerate, torchaudio, ffmpeg) đã gộp bộ lọc thông thấp vào; code tự viết kiểu `x[::3]` hoặc nội suy tuyến tính thì **không**.

> 🔴 **Quy tắc:** không bao giờ downsample bằng slicing (`x[::k]`) hay `np.interp` trên audio thật. Chỉ dùng resampler có lọc.

---

## 2.3 Quantization: bit depth, sai số, dynamic range, dither

### 2.3.1 Lượng tử hoá

Với bit depth `N`, ADC chỉ có `2^N` mức. Mỗi mẫu được làm tròn về mức gần nhất; phần chênh lệch là **sai số lượng tử** (quantization error), tối đa ±½ bước (LSB).

| Định dạng | Số mức | Dải giá trị |
|---|---|---|
| int8 (u8 trong WAV) | 256 | 0…255, im lặng = 128 |
| int16 | 65 536 | −32 768 … 32 767 |
| int24 | 16 777 216 | −8 388 608 … 8 388 607 |
| int32 | ~4.3 tỉ | −2 147 483 648 … 2 147 483 647 |

### 2.3.2 Dynamic range ~6 dB mỗi bit

Với tín hiệu đủ "bận" (sai số coi như nhiễu trắng phân bố đều), tỉ số tín hiệu/nhiễu lượng tử cho một sin full-scale là:

```text
SQNR ≈ 6.02 · N + 1.76  dB
```

| N | SQNR lý thuyết | Thực tế |
|---|---|---|
| 8 | ~50 dB | Nghe rõ nhiễu "sạn"; chỉ dùng kèm companding (μ-law/A-law, Chương 3) |
| 16 | ~98 dB | Thừa cho tiếng nói; nhiễu mic/phòng (thường 40–70 dB dưới full scale) lớn hơn nhiễu lượng tử nhiều |
| 24 | ~146 dB | Vượt xa ADC thật (~100–120 dB); dùng để có headroom khi thu |
| float32 | ~144 dB *ở mọi mức* | Mantissa 24 bit, độ chính xác tương đối không đổi theo biên độ |

Ý nghĩa thực hành:

- **int16 là đủ** cho transport và lưu trữ tiếng nói. Không cần 24 bit cho ASR.
- Nhưng 98 dB chỉ đạt khi tín hiệu **dùng hết** thang. Một mic thu quá nhỏ, đỉnh chỉ −40 dBFS, chỉ còn ~58 dB dải hữu ích — vẫn đủ cho ASR, nhưng nếu sau đó gain số lên +40 dB thì nhiễu lượng tử cũng lên theo.
- **float32** gần như không có nhiễu lượng tử đáng kể và cho phép giá trị **vượt** ±1.0 tạm thời (headroom ảo) — tiện cho xử lý trung gian (mix, gain, filter). Vì thế pipeline thường: transport **int16**, xử lý nội bộ **float32**.

### 2.3.3 Dither

Khi giảm bit depth (ví dụ float32 → int16) với tín hiệu rất nhỏ, sai số lượng tử **tương quan** với tín hiệu và nghe như méo. **Dither** là cộng một nhiễu rất nhỏ (thường TPDF, ±1 LSB) trước khi làm tròn để biến méo thành nhiễu nền phẳng.

- Với pipeline speech → ASR: **gần như không quan trọng** (tín hiệu ở mức bình thường, nhiễu môi trường lớn hơn nhiều).
- Với TTS xuất int16 phát cho người nghe, tín hiệu fade-out rất nhỏ: dither có thể cải thiện chút ít. Nhiều thư viện (soxr, ffmpeg) có tuỳ chọn dither; không bật cũng không phải bug.

---

## 2.4 Clipping và headroom

**Clipping** xảy ra khi tín hiệu vượt mức tối đa biểu diễn được (0 dBFS): đỉnh sóng bị "cắt phẳng".

| Loại | Xảy ra ở đâu | Đảo ngược được? |
|---|---|---|
| **Analog clipping** | Preamp/ADC khi gain quá cao hoặc người nói sát mic | Không |
| **Digital clipping** | Ép float > 1.0 về int16; cộng hai tín hiệu int16 bị tràn | Không |
| **Integer overflow (wrap-around)** | Cộng int16 trong numpy mà không đổi kiểu: 30000 + 10000 → −25536 | Không; tệ hơn clip vì tạo xung đổi dấu, nghe như tiếng nổ |

Hậu quả:

- Clipping sinh **harmonics giả** trải khắp phổ → ASR giảm chính xác, VAD có thể kích hoạt sai; TTS bị clip nghe rè rõ ràng.
- Clipping là phi tuyến → AEC (Chương 7) mô hình hoá echo tuyến tính sẽ kém đi khi loa hoặc mic bị clip.

**Headroom** là khoảng cách từ đỉnh tín hiệu tới 0 dBFS. Thực hành:

- Thu âm: đặt gain để đỉnh lời nói khoảng **−12 … −6 dBFS**, chừa chỗ cho tiếng cười/la to.
- Xử lý nội bộ bằng float32; chỉ **clip đúng một lần** ở bước cuối khi quy đổi về int.
- Trộn nhiễu theo SNR (Chương 1 §1.7): nếu hỗn hợp vượt 1.0, **scale cả hỗn hợp** chứ không clip.
- Đầu ra TTS: chuẩn hoá đỉnh khoảng −1 dBFS (hoặc theo loudness) trước khi gửi ra client.
- Theo dõi tỉ lệ mẫu clip trong production:

```python
def clip_ratio(x: np.ndarray, thresh: float = 0.999) -> float:
    """x là float32 trong [-1, 1]. Trả tỉ lệ mẫu chạm (gần) full scale."""
    return float(np.mean(np.abs(x) >= thresh))
# > ~0.1% trên một lượt nói: đáng cảnh báo (ngưỡng gợi ý, tự tune).
```

---

## 2.5 Biểu diễn mẫu trong bộ nhớ

### 2.5.1 Integer PCM

**PCM** (Pulse-Code Modulation) tuyến tính = lưu trực tiếp giá trị lượng tử của từng mẫu. Các biến thể:

| Tên ffmpeg | Ý nghĩa | Byte/mẫu | numpy dtype |
|---|---|---|---|
| `u8` | unsigned 8 bit, im lặng = 128 | 1 | `uint8` |
| `s16le` | signed 16 bit little-endian | 2 | `'<i2'` |
| `s16be` | signed 16 bit big-endian | 2 | `'>i2'` |
| `s24le` | signed 24 bit packed (3 byte) | 3 | không có sẵn, phải tự giải nén |
| `s32le` | signed 32 bit | 4 | `'<i4'` |
| `f32le` | IEEE float 32 bit | 4 | `'<f4'` |
| `f64le` | IEEE float 64 bit | 8 | `'<f8'` |

Các đuôi `p` (`s16p`, `fltp`) trong ffmpeg nghĩa là **planar** (xem §2.6).

**int24 packed** hay gặp ở card âm thanh/WAV chuyên nghiệp. Giải nén thủ công:

```python
def s24le_to_int32(b: bytes) -> np.ndarray:
    a = np.frombuffer(b, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
    v = a[:, 0] | (a[:, 1] << 8) | (a[:, 2] << 16)
    v = np.where(v & 0x800000, v - 0x1000000, v)  # mở rộng dấu
    return v  # dải −8_388_608 … 8_388_607
```

### 2.5.2 Float32 trong khoảng [-1, 1]

Quy ước của hầu hết thư viện ML/DSP (librosa, torchaudio, Silero VAD, Whisper preprocess, Web Audio API): **float32, 1.0 = full scale**, im lặng = 0.0.

- Model nhận float32 (Silero VAD nhận tensor 1-D float32 theo [Silero VAD](../wiki/silero-vad.md), **Reported**) **ngầm định** thang [-1, 1]. Model không kiểm tra; nó chỉ cho ra kết quả sai.
- float64 tốn gấp đôi bộ nhớ và hầu như không cần cho audio; nhiều thư viện trả float64 mặc định (xem §2.5.5) → nhớ ép về float32.

### 2.5.3 Quy đổi int16 ↔ float32

int16 bất đối xứng: −32768 … +32767. Quy ước phổ biến nhất:

```python
import numpy as np

INT16_SCALE = 32768.0

def int16_to_f32(x: np.ndarray) -> np.ndarray:
    assert x.dtype == np.int16, x.dtype
    return x.astype(np.float32) / INT16_SCALE        # dải [-1.0, 0.99997]

def f32_to_int16(x: np.ndarray) -> np.ndarray:
    y = np.round(x * INT16_SCALE)
    return np.clip(y, -32768, 32767).astype(np.int16)  # clip TRƯỚC khi ép kiểu
```

Lưu ý:

- Một số thư viện nhân/chia 32767 thay vì 32768. Chênh ~0.003% (≈ 0.0003 dB) — **vô hại**. Điều có hại là: quên chia, chia hai lần, hoặc **ép kiểu trước khi clip** (`(x*32768).astype(np.int16)` với x = 1.0 → 32768 tràn thành −32768: một xung đổi dấu).
- `astype(np.int16)` **cắt phần thập phân** (truncate về 0), không làm tròn. Dùng `np.round` trước để tránh lệch nhỏ (gây DC offset cỡ ½ LSB).
- Phép chia luôn làm trên float: `x / 32768` với `x` là int16 thì numpy tự đổi sang float64 → nhớ `astype(np.float32)`.

**Quy đổi giữa các bit depth nguyên:** int16 → int32 là dịch trái 16 bit (`x.astype(np.int32) << 16`), không phải ép kiểu giữ nguyên giá trị (giữ nguyên giá trị thì tín hiệu nhỏ đi 96 dB so với thang int32).

### 2.5.4 Endianness, signed và unsigned

- **Endianness** là thứ tự byte trong một mẫu nhiều byte. Giá trị int16 `0x1234`:
  - little-endian (`le`): byte `34 12` — WAV, x86, ARM, Web Audio, hầu hết mọi thứ hiện nay.
  - big-endian (`be`): byte `12 34` — AIFF, một số giao thức mạng/định dạng cũ.
- Đọc nhầm endianness → mỗi mẫu bị hoán đổi byte → nghe như **nhiễu trắng to**, vẫn thoáng nghe "nhịp" lời nói phía sau.
- **Signed vs unsigned:** u8 WAV có im lặng = 128. Đọc u8 như int8 (hoặc s16 như u16) → DC offset khổng lồ và "gập" dạng sóng, nghe như méo nặng (Chương 1 §1.1.1: trung bình khác 0 là dấu hiệu sai).

Trong numpy luôn **ghi rõ** endianness khi đọc bytes thô từ mạng/file: `np.frombuffer(buf, dtype='<i2')`, không dùng `np.int16` trơn (native order) nếu code có thể chạy trên máy big-endian — dù hiếm, ghi rõ cũng là tài liệu hoá contract.

### 2.5.5 Mặc định của các thư viện (bẫy thường gặp)

| Thư viện / hàm | dtype mặc định | Thang | Shape | Bẫy |
|---|---|---|---|---|
| `soundfile.read` | **float64** | [-1, 1] | `(frames,)` hoặc `(frames, channels)` | Truyền `dtype='float32'` hoặc `'int16'` |
| `scipy.io.wavfile.read` | dtype gốc của file (int16…) | **không chuẩn hoá** | `(frames, channels)` | Phải tự chia 32768 |
| `librosa.load` | float32 | [-1, 1] | `(samples,)` | **Mặc định `sr=22050`, `mono=True`** → tự resample + downmix. Dùng `sr=None` để giữ gốc |
| `torchaudio.load` | float32 | [-1, 1] (`normalize=True`) | **`(channels, frames)`** | Ngược chiều với soundfile |
| `np.frombuffer(buf)` | **float64** | — | 1-D | Không truyền `dtype` → diễn giải bytes thành float64 → rác |
| `sounddevice` / PyAudio | theo tham số (`'int16'`, `paInt16`, `'float32'`) | theo dtype | `(frames, channels)` | Mở stream float32 nhưng gửi bytes int16 |
| Web Audio API / AudioWorklet | float32 | [-1, 1] | planar, 1 mảng/kênh | Render quantum **128 frames**, sample rate theo `AudioContext` (thường 48 kHz) |

Silero VAD có ghi chú rằng `read_audio` qua torchcodec resample bằng FFmpeg thay vì `torchaudio.transforms.Resample`, nên file đã resample có thể lệch ~1e-3 giữa hai đường (**Reported**, [Silero VAD](../wiki/silero-vad.md)). Bài học chung: **hai đường đọc/resample khác nhau cho ra mảng khác nhau**; test hồi quy so sánh mảng phải có dung sai.

---

## 2.6 Kênh: mono, stereo, interleaved và planar

### 2.6.1 Layout

Với stereo L/R và 4 frame:

```text
Interleaved (packed):  L0 R0 L1 R1 L2 R2 L3 R3      ← WAV, PCM s16le, hầu hết socket/stream
Planar:                L0 L1 L2 L3 | R0 R1 R2 R3    ← Web Audio, ffmpeg fltp, torchaudio (channels, frames)
```

Trong numpy: interleaved bytes → `np.frombuffer(buf, '<i2').reshape(-1, C)` cho shape `(frames, C)`; muốn planar thì `.T` (nhớ `np.ascontiguousarray` nếu thư viện tiếp theo cần bộ nhớ liên tục).

### 2.6.2 Downmix và upmix

- **Downmix stereo → mono:** dùng **trung bình** `(L + R) / 2`, không dùng tổng (tổng có thể vượt full scale).
  - Cẩn thận: nếu L và R **ngược pha** (mic hỏng dây, hiệu ứng stereo), trung bình có thể triệt tiêu gần hết tiếng nói (Chương 1 §1.1.4). Kiểm tra tương quan L/R khi thấy mono nhỏ bất thường.
  - **Ghi âm call center 2 kênh** (agent một kênh, khách một kênh): **đừng downmix** — xử lý từng kênh riêng. Kênh riêng chính là "diarization miễn phí" (Chương 14).
- **Upmix mono → stereo:** nhân bản kênh. Cần khi thiết bị phát chỉ nhận stereo.
- **Mảng nhiều mic** (2–8 kênh) cho beamforming/AEC: giữ nguyên tới bước xử lý không gian rồi mới ra mono.

### 2.6.3 Frame có kênh

Khi API nói "1024 frames stereo int16" thì đó là 1024 × 2 mẫu = 4096 byte (xem §2.7). Nhầm "frames" với "samples" là nguồn lỗi gấp đôi/gấp nửa thời lượng.

---

## 2.7 Đơn vị thời gian và công thức quy đổi

### 2.7.1 Một từ, nhiều nghĩa

| Từ | Nghĩa trong audio API (PortAudio, ALSA, Web Audio, ffmpeg) | Nghĩa trong DSP/ML | Nghĩa trong codec/transport |
|---|---|---|---|
| **sample** | Một giá trị của **một kênh** tại một thời điểm | Như bên trái | — |
| **frame** | Một thời điểm, **gồm mọi kênh** (stereo: 2 sample) | **Cửa sổ phân tích** N sample, ví dụ 25 ms với hop 10 ms (Chương 4) | Một gói codec: Opus 20 ms; WebRTC xử lý theo khối 10 ms |
| **chunk** | Khối dữ liệu đẩy qua một lần gọi/một message | Đơn vị model xử lý: Silero 512 samples, Nemotron chunk 160/320 ms (tài liệu thiết kế §6) | Message WebSocket |
| **block / buffer / period** | Khối callback của driver (`frames_per_buffer`, `blocksize`, ALSA period) | — | — |
| **window / hop** | — | Độ dài cửa sổ / bước nhảy giữa hai cửa sổ | — |

> 🔴 Khi đọc tài liệu một backend, luôn hỏi: "frame/chunk này tính bằng **samples**, **frames** (đa kênh), **bytes** hay **ms**? Ở sample rate nào?"

### 2.7.2 Công thức

```text
samples_per_channel = fs · t_ms / 1000
t_ms                = samples_per_channel · 1000 / fs
bytes               = samples_per_channel · channels · bytes_per_sample
bitrate (bit/s)     = fs · channels · bits_per_sample
```

```python
def ms_to_samples(ms: float, sr: int) -> int:
    n = sr * ms / 1000
    assert n == int(n), f"{ms} ms ở {sr} Hz không ra số nguyên samples ({n})"
    return int(n)

def samples_to_ms(n: int, sr: int) -> float:
    return n * 1000 / sr

def nbytes(n_samples: int, channels: int = 1, bytes_per_sample: int = 2) -> int:
    return n_samples * channels * bytes_per_sample
```

Lưu ý `assert`: 10 ms ở 44.1 kHz = 441 samples (nguyên), nhưng 1 ms ở 44.1 kHz = 44.1 (không nguyên); 32 ms ở 22.05 kHz = 705.6. Chọn kích thước khối là **số nguyên samples** ở mọi sample rate liên quan, nếu không sẽ có trôi thời gian (drift) do làm tròn tích luỹ.

### 2.7.3 Bảng tra nhanh

**Kích thước theo thời lượng (mono):**

| Thời lượng | 8 kHz | 16 kHz | 24 kHz | 44.1 kHz | 48 kHz |
|---|---|---|---|---|---|
| 10 ms | 80 | 160 | 240 | 441 | 480 |
| 20 ms | 160 | **320** | 480 | 882 | **960** |
| 32 ms | **256** | **512** | 768 | 1411.2 ✗ | 1536 |
| 100 ms | 800 | 1600 | 2400 | 4410 | 4800 |
| 1 s | 8 000 | 16 000 | 24 000 | 44 100 | 48 000 |

(✗ = không nguyên.)

**Bytes cho 1 giây:**

| Định dạng | Bytes/giây | Bitrate |
|---|---|---|
| PCM16 mono 8 kHz | 16 000 | 128 kbps |
| PCM16 mono 16 kHz | **32 000** | 256 kbps |
| PCM16 mono 24 kHz | 48 000 | 384 kbps |
| PCM16 mono 48 kHz | 96 000 | 768 kbps |
| float32 mono 16 kHz | 64 000 | 512 kbps |
| float32 stereo 48 kHz | **384 000** | 3 072 kbps |
| G.711 μ-law 8 kHz (Chương 3) | 8 000 | 64 kbps |
| Opus thoại điển hình (Chương 3) | ~2 000–4 000 | ~16–32 kbps |

Thêm: **base64** làm phình dữ liệu thêm ~33% (4 ký tự cho 3 byte). Tài liệu thiết kế §5.1 khuyên WebSocket gửi **binary, không base64** (**Reported**); một số API (SSE của VieNeu, Higgs) vẫn bắt buộc base64 — tính vào ngân sách băng thông.

### 2.7.4 Ví dụ gắn pipeline: frame transport 20 ms vào Silero 512 samples

Tài liệu thiết kế §7.1: frame transport 20 ms được **reblock** thành 512 samples (32 ms) cho Silero (256 samples ở 8 kHz); không bắt VAD, ASR và TTS dùng chung chunk length (**Synthesis**). Theo [Silero VAD](../wiki/silero-vad.md), từ v5 cửa sổ cố định 512 samples ở 16 kHz hoặc 256 ở 8 kHz (**Reported**).

- 20 ms @ 16 kHz = 320 samples = 640 byte PCM16.
- Bội chung nhỏ nhất của 320 và 512 là 2560 samples = **160 ms** = 8 frame transport = 5 cửa sổ VAD.
- Độ trễ do chờ đủ cửa sổ (tính từ lúc mẫu cuối của cửa sổ có mặt tới khi frame chứa nó tới nơi):

| Cửa sổ VAD | Kết thúc ở (ms audio) | Có đủ khi frame thứ | Thời điểm có | Chờ thêm |
|---|---|---|---|---|
| 1 | 32 | 2 | 40 ms | 8 ms |
| 2 | 64 | 4 | 80 ms | 16 ms |
| 3 | 96 | 5 | 100 ms | 4 ms |
| 4 | 128 | 7 | 140 ms | 12 ms |
| 5 | 160 | 8 | 160 ms | 0 ms |

Trung bình chờ ~8 ms, tối đa 16 ms — nhỏ, nhưng là một mục trong ngân sách latency (Chương 20) và minh hoạ vì sao không nên "ép" mọi tầng cùng một chunk length.

---

## 2.8 Resampling

### 2.8.1 Lý thuyết tối thiểu

Đổi sample rate theo tỉ số hữu tỉ `L/M` (đã rút gọn):

```text
x[n] ──► chèn (L−1) số 0 giữa các mẫu (upsample ×L)
     ──► lọc thông thấp, cắt tại min(fs_in, fs_out)/2   ← vừa chống ảnh phổ (imaging) vừa chống alias
     ──► giữ 1 mẫu trong M (downsample ÷M)
```

| Chuyển đổi | L/M | Loại |
|---|---|---|
| 48 kHz → 16 kHz | 1/3 | Nguyên (decimation) |
| 16 kHz → 48 kHz | 3/1 | Nguyên (interpolation) |
| 8 kHz → 16 kHz | 2/1 | Nguyên |
| 24 kHz → 16 kHz | 2/3 | Phân số |
| 44.1 kHz → 16 kHz | 160/441 | Phân số "xấu" |
| 22.05 kHz → 16 kHz | 320/441 | Phân số "xấu" |
| 44.1 kHz → 48 kHz | 160/147 | Phân số "xấu" |

Làm ngây thơ theo sơ đồ trên rất lãng phí (chèn hàng trăm số 0 rồi bỏ đi hàng trăm mẫu). Resampler thực tế dùng:

- **Polyphase filter:** tách bộ lọc thành L pha con, chỉ tính những mẫu đầu ra thực sự cần. `scipy.signal.resample_poly` là ví dụ dễ đọc.
- **Windowed-sinc / bandlimited interpolation:** tính trực tiếp giá trị tại vị trí thời gian thực bất kỳ bằng sinc có cửa sổ (Kaiser, Hann…), hỗ trợ cả tỉ lệ tuỳ ý và thay đổi theo thời gian. libsamplerate, soxr, torchaudio dùng họ kỹ thuật này.

### 2.8.2 Chất lượng ↔ độ trễ ↔ CPU

Bộ lọc càng dài thì:

- dải chuyển tiếp càng hẹp (giữ được nội dung gần Nyquist hơn), chặn alias càng sâu;
- tốn CPU hơn;
- **trễ nhóm** (group delay) càng lớn: FIR pha tuyến tính dài N tap trễ (N−1)/2 mẫu. Với resampler chất lượng cao, con số này thường ở mức vài ms — không đáng kể so với ngân sách voice loop, nhưng không bằng 0.

| Mức | Khi nào dùng |
|---|---|
| Linear / zero-order hold | Không dùng cho audio vào model (alias, méo cao tần) |
| Sinc "fast"/"low" quality | Nhánh VAD trên CPU yếu, nơi chỉ cần biết có tiếng nói |
| Sinc "medium/high" (soxr `HQ`, libsamplerate `SINC_MEDIUM/BEST`) | Mặc định cho ASR và TTS |
| "Very high" | Offline, mastering; thừa cho speech realtime |

### 2.8.3 Thư viện

| Thư viện | Ghi chú dùng trong pipeline |
|---|---|
| **soxr** (`python-soxr`, libsoxr) | Nhanh, chất lượng cao, có **API stream** (`soxr.ResampleStream`). Mức chất lượng `QQ/LQ/MQ/HQ/VHQ`. VieNeu API resample từng chunk bằng soxr khi client xin `sample_rate` khác 48 kHz (**Reported**, [VieNeu OpenAI Speech API](../wiki/vieneu-tts-openai-speech-api.md)) |
| **libsamplerate** (`samplerate` Python) | Converter `SINC_BEST/MEDIUM/FASTEST`, `LINEAR`, `ZERO_ORDER_HOLD`; hỗ trợ stream và tỉ lệ thay đổi theo thời gian (hữu ích cho bù clock drift) |
| **torchaudio** (`functional.resample`, `transforms.Resample`) | Chạy trên tensor, GPU được; tiện trong training/batch. `transforms.Resample` cache kernel. **Không có state giữa các lần gọi** → không dùng trực tiếp cho stream |
| **ffmpeg** (`aresample`, swr; hoặc `aresample=resampler=soxr`) | Dùng khi decode file/stream + đổi định dạng một lần: `ffmpeg -i in.mp3 -ar 16000 -ac 1 -f s16le out.raw` |
| **scipy** (`resample_poly`) | Tốt cho phân tích/offline; `scipy.signal.resample` (dùng FFT) giả định tín hiệu tuần hoàn → méo ở biên, tránh cho audio dài/stream |

### 2.8.4 Resample stream (có state) khác resample cả file

Bộ lọc resampler nhìn **cả mẫu quá khứ lẫn tương lai** quanh điểm cần tính. Khi resample cả file, resampler thấy toàn bộ tín hiệu. Khi audio tới **từng chunk**, nếu gọi resample **độc lập** cho mỗi chunk:

1. **Hiệu ứng biên:** mỗi chunk bị coi như có số 0 (hoặc phản xạ) ở hai đầu → xuất hiện **tiếng lách tách** (click) mỗi 20 ms, nghe như tiếng "rè" đều; trên spectrogram là các vạch dọc cách đều.
2. **Trôi độ dài:** 20 ms @ 44.1 kHz = 882 samples → 320 samples @ 16 kHz (nguyên, may mắn); nhưng khối 1024 frames @ 44.1 kHz → 371.5… samples. Làm tròn mỗi chunk → sau vài phút lệch hàng trăm ms so với timeline thật → timestamp VAD/ASR và đồng bộ barge-in sai dần.
3. **Mất pha phân số:** với tỉ lệ phân số, vị trí lấy mẫu đầu ra của chunk sau phải nối tiếp đúng pha phân số của chunk trước.

Giải pháp: **một resampler có state cho mỗi stream (mỗi session, mỗi chiều)**, giữ lịch sử bộ lọc và pha phân số; flush ở cuối stream.

```python
import numpy as np
import soxr

class StreamResampler:
    """Một instance cho MỖI session và MỖI chiều (uplink/downlink). Không dùng chung."""
    def __init__(self, in_rate: int, out_rate: int, channels: int = 1, quality: str = "HQ"):
        self.passthrough = in_rate == out_rate
        if not self.passthrough:
            self.rs = soxr.ResampleStream(in_rate, out_rate, channels,
                                          dtype="float32", quality=quality)

    def push(self, x: np.ndarray, last: bool = False) -> np.ndarray:
        x = np.ascontiguousarray(x, dtype=np.float32)
        if self.passthrough:
            return x
        return self.rs.resample_chunk(x, last=last)   # last=True để flush đuôi bộ lọc
```

Hệ quả cần biết: resampler stream **giữ lại vài mẫu** chờ tương lai → chunk ra đầu tiên có thể ngắn hơn kỳ vọng, và tổng số mẫu ra chỉ khớp khi flush. Code phía sau (reblocker) phải chịu được chunk có độ dài **thay đổi**.

### 2.8.5 Clock drift (giới thiệu, chi tiết ở Chương 6–7)

"48 kHz" của mic và "48 kHz" của loa là hai thạch anh khác nhau; thực tế có thể là 48 003 Hz và 47 998 Hz. Lệch vài chục ppm → sau 10 phút trôi vài chục ms. Ảnh hưởng tới AEC (căn chỉnh tín hiệu tham chiếu loa với mic) và tới buffer phát (underrun/overrun). Cách xử lý: resampler có tỉ lệ thay đổi nhẹ (adaptive resampling) — thường đã có sẵn trong WebRTC/hệ điều hành; nếu tự làm audio I/O thì phải biết vấn đề này tồn tại.

---

## 2.9 Sample rate trong pipeline

### 2.9.1 Bảng tổng hợp

| Vị trí | Sample rate thường gặp | Nguồn |
|---|---|---|
| Mic laptop/điện thoại, `getUserMedia`, `AudioContext` | 44.1 / **48 kHz** | Kiến thức chung |
| Transport WebRTC/Opus | **48 kHz** nội bộ codec (Opus hỗ trợ 8/12/16/24/48 kHz đầu vào) | Kiến thức chung (Chương 3, 8) |
| Transport WebSocket MVP | PCM16 **16 kHz** mono, frame 20–32 ms | Tài liệu thiết kế §5.1 (**Reported**) |
| Telephony PSTN/SIP (G.711) | **8 kHz** | Kiến thức chung; tài liệu thiết kế §5.1 |
| Silero VAD | 8 hoặc **16 kHz** | [Silero VAD](../wiki/silero-vad.md) (**Reported**) |
| ASR (Whisper, Qwen3-ASR, Nemotron…) | **16 kHz** mono | Kiến thức chung; gateway chuẩn hoá 16 kHz mono (tài liệu thiết kế §7.1, **Synthesis**) |
| HF s2s, STT qua `/v1/audio/transcriptions` | WAV PCM16 mono 16 kHz trong bộ nhớ | [s2s OpenAI-compatible backends](../wiki/speech-to-speech-openai-compatible-backends.md) (**Reported**) |
| OpenAI Realtime transcription | PCM **24 kHz** (s2s resample từ 16 kHz) | Như trên (**Reported**) |
| VieNeu v3 Turbo | **48 kHz** gốc; API có thể xin 24/16/8 kHz | [VieNeu OpenAI Speech API](../wiki/vieneu-tts-openai-speech-api.md) (**Reported**) |
| VieNeu v3 Nano / sanoTTS | 24 kHz / 22.05 kHz | Tài liệu thiết kế §5.6 (**Reported**) |
| Kokoro, Qwen3-TTS và nhiều TTS neural | **24 kHz** | Kiến thức chung; Qwen3-TTS 24 kHz theo s2s docs (**Reported**) |
| MOSS-TTS Local v1.5 | codec stereo 48 kHz, ví dụ stream mono | Tài liệu thiết kế §3, §5.6 (**Reported**) |
| AudioWorklet phát ở client | theo `AudioContext` (thường 48 kHz) | Kiến thức chung |

### 2.9.2 Nguyên tắc chuyển đổi trong gateway (Synthesis, theo tài liệu thiết kế)

```text
UPLINK (mic → model)
  client 48 kHz float32 ──[resample có lọc, ở client hoặc gateway]──► 16 kHz mono
     ├─► int16/float32 16 kHz ─► reblock 512 ─► Silero VAD
     └─► 16 kHz ─► ASR (streaming chunk riêng, hoặc buffer cả lượt + pre-roll)

DOWNLINK (model → loa)
  TTS ở sample rate GỐC (24/48 kHz) ──[giữ nguyên tới playback adapter]──► resample một lần về rate của AudioContext
```

- **Chuẩn hoá một lần, ở một chỗ.** Mỗi lần resample là một lần mất chất lượng và thêm trễ; tránh chuỗi 48 → 16 → 24 → 48.
- **Downlink giữ sample rate gốc** tới tận playback adapter (§7.1). Có một ngoại lệ đáng biết: HF s2s chuyển audio TTS bên ngoài thành khối **16 kHz mono int16 512 samples**, nên trần băng thông của cả pipeline đó là 16 kHz (tài liệu thiết kế §3 nguyên tắc 4; [s2s OpenAI-compatible backends](../wiki/speech-to-speech-openai-compatible-backends.md), **Reported**). TTS 48 kHz đi qua đó sẽ mất toàn bộ dải trên 8 kHz — nghe "đục" hơn, không phải lỗi model.
- **Telephony:** decode đúng codec (μ-law/A-law → PCM) ở 8 kHz **trước**, rồi mới resample lên 16 kHz cho ASR (tài liệu thiết kế §5.1). Resample trên bytes μ-law chưa decode là cộng trừ trên số đã nén phi tuyến → rác.
- **Client JS downsample** 48 → 16 kHz trong AudioWorklet: nhiều đoạn code mẫu trên mạng chỉ lấy 1 mẫu bỏ 2 → aliasing (§2.2.3). Hoặc dùng `new AudioContext({sampleRate: 16000})` để trình duyệt tự resample, hoặc gửi 48 kHz lên và resample đúng chuẩn ở gateway, hoặc tự viết bộ lọc thông thấp trước khi decimate.

### 2.9.3 Audio contract: viết ra, kiểm tra ở biên

Mọi chỗ audio đi qua ranh giới (client ↔ gateway, gateway ↔ backend) nên có một mô tả tường minh và được assert:

```python
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class AudioFormat:
    sample_rate: int                              # Hz
    channels: int                                 # 1 = mono
    sample_format: Literal["s16le", "f32le"]      # dtype + endianness
    layout: Literal["interleaved", "planar"] = "interleaved"

    @property
    def bytes_per_sample(self) -> int:
        return {"s16le": 2, "f32le": 4}[self.sample_format]

    def bytes_for_ms(self, ms: float) -> int:
        return ms_to_samples(ms, self.sample_rate) * self.channels * self.bytes_per_sample

# Ví dụ khai báo (theo tài liệu thiết kế §3, §5.1 và trang wiki VieNeu API — Reported):
WS_UPLINK      = AudioFormat(16_000, 1, "s16le")    # MVP WebSocket
VAD_IN         = AudioFormat(16_000, 1, "f32le")    # Silero nhận float32 [-1, 1]
VIENEU_HTTP    = AudioFormat(48_000, 1, "s16le")    # response_format=pcm, mặc định
VIENEU_SDK     = AudioFormat(48_000, 1, "f32le")    # SDK trả float32 48 kHz
```

Khi backend trả header như `X-Sample-Rate` (VieNeu API có header này, **Reported**), **đọc và so sánh** với contract thay vì tin cấu hình tĩnh.

---

## 2.10 Lớp audio ingress tối thiểu (code tham khảo)

Ghép các phần trên thành đường uplink của gateway: bytes WebSocket → int16 → float32 → (resample nếu cần) → reblock 512 → VAD. Đây là code minh hoạ (**Synthesis**), chưa phải implementation đã test trong dự án.

```python
import numpy as np

class PcmBytesToSamples:
    """Ghép bytes s16le từ transport thành mẫu int16.
    Message WebSocket/TCP KHÔNG đảm bảo chia đúng biên 2 byte; giữ lại byte lẻ."""
    def __init__(self) -> None:
        self._rem = b""

    def push(self, data: bytes) -> np.ndarray:
        data = self._rem + data
        n = (len(data) // 2) * 2
        self._rem = data[n:]
        return np.frombuffer(data[:n], dtype="<i2")


class Reblocker:
    """Nhận mảng độ dài tuỳ ý, trả các khối đúng `block` mẫu (vd 512 cho Silero 16 kHz)."""
    def __init__(self, block: int) -> None:
        self.block = block
        self._buf = np.zeros(0, dtype=np.float32)

    def push(self, x: np.ndarray) -> list[np.ndarray]:
        self._buf = np.concatenate([self._buf, x.astype(np.float32, copy=False)])
        k = len(self._buf) // self.block
        out = [self._buf[i * self.block:(i + 1) * self.block] for i in range(k)]
        self._buf = self._buf[k * self.block:]
        return out


class UplinkIngress:
    """Một instance cho mỗi session. Dùng số mẫu làm đồng hồ, không dùng wall-clock."""
    def __init__(self, in_rate: int = 16_000, model_rate: int = 16_000, vad_block: int = 512):
        self.bytes2s = PcmBytesToSamples()
        self.resampler = StreamResampler(in_rate, model_rate)   # §2.8.4
        self.reblock = Reblocker(vad_block)
        self.model_rate = model_rate
        self.samples_out = 0          # timeline ở model_rate: t = samples_out / model_rate

    def on_message(self, data: bytes):
        x = int16_to_f32(self.bytes2s.push(data))               # §2.5.3
        x = self.resampler.push(x)
        for block in self.reblock.push(x):
            t_start = self.samples_out / self.model_rate
            self.samples_out += len(block)
            yield t_start, block                                # → VAD, ring buffer, ASR
```

Ba điểm thiết kế đáng nhớ:

1. **State theo session**: bytes dư, lịch sử resampler, buffer reblock, bộ đếm mẫu — tất cả là state riêng của từng session (tài liệu thiết kế §7.1: không bao giờ dùng chung cache giữa các user).
2. **Đồng hồ bằng số mẫu**: timestamp suy ra từ `samples_out / sr` khớp chính xác với audio, không bị jitter mạng. Nếu transport có gói mất/gap, phải có policy rõ ràng (chèn im lặng đúng thời lượng hay đánh dấu gap) chứ không nối lệch timeline (§7.1).
3. **Tách độ dài khối theo tầng**: VAD 512, ASR streaming theo chunk của nó, buffer lượt nói giữ pre-roll 200–300 ms (§7.1, **Synthesis**) — 300 ms @ 16 kHz = 4 800 samples = 9 600 byte PCM16.

---

## 2.11 Lỗi kinh điển: triệu chứng → nguyên nhân → cách sửa

Tài liệu thiết kế §5.1 nhắc lại nhận xét cộng đồng rằng transcript rác "9/10 lần" là do lệch sample rate ở đâu đó trong chuỗi chứ không phải do model (**Reported**, anecdote; [Community STT-LLM-TTS Wiring](../wiki/community-stt-llm-tts-pipeline.md)). Bảng dưới giúp chẩn đoán từ triệu chứng:

| Triệu chứng | Nguyên nhân hay gặp | Cách kiểm tra / sửa |
|---|---|---|
| Giọng **cao và nhanh** ("chipmunk"), thời lượng ngắn đi | Phát/khai báo ở rate **cao hơn** thật (24 kHz phát như 48 kHz → nhanh ×2, cao 1 octave); hoặc mono bị coi là stereo | So `len(x)/sr` với thời lượng mong đợi; đọc `X-Sample-Rate`/header |
| Giọng **trầm và chậm** ("slow-mo"), thời lượng dài ra | Rate khai báo **thấp hơn** thật (48 kHz đưa vào như 16 kHz → chậm ×3); hoặc stereo interleaved bị coi là mono (dài ×2) | Như trên; kiểm tra `channels` |
| ASR ra transcript rác/hallucination dù audio nghe "được" | Audio 48 kHz đưa vào model 16 kHz không resample; hoặc 8 kHz không resample | Assert sample rate ở biên ASR; log `len(x)/sr` của mỗi lượt |
| **Nhiễu trắng to**, thoáng nghe nhịp lời nói phía sau | Sai dtype (float32 bytes đọc như int16 hoặc ngược lại), sai endianness, hoặc lệch 1 byte (byte lẻ của int16 bị tách sang message sau) | `PcmBytesToSamples`; khai báo `dtype='<i2'`/`'<f4'` rõ ràng; không gọi `np.frombuffer` thiếu `dtype` |
| Tiếng **"tách" ở đầu** mỗi file/stream | Header WAV (thường 44 byte, nhưng có thể dài hơn khi có chunk `LIST`/`fact`/extensible) bị đọc như audio | Parse header bằng thư viện (`soundfile`, `wave`), không cắt cứng 44 byte; với stream WAV "unknown length" (VieNeu `wav`, **Reported**) chỉ bỏ header ở **chunk đầu** |
| **Lách tách đều** mỗi 10–20 ms | Resample từng chunk độc lập; hoặc playback buffer underrun | `StreamResampler` theo session; tăng jitter buffer phía client (Chương 6) |
| Âm thanh **cực to, vuông, rè** (nguy hiểm cho tai/loa) | int16 → float32 quên chia 32768 rồi đưa ra playback float | Assert `np.abs(x).max() <= 1.0` trước playback; luôn có limiter/clip cuối |
| VAD **không bao giờ** thấy tiếng nói | Chia 32768 **hai lần** (tín hiệu nhỏ đi ~90 dB); hoặc đưa int16 thô vào model float mà model tự chuẩn hoá khác | Log RMS dBFS mỗi khối; im lặng thật ở mic tốt vẫn khoảng −60 … −40 dBFS, không phải −150 |
| VAD **luôn** báo có tiếng nói, xác suất bão hoà | Quên chia 32768; DC offset lớn (u8/s16 nhầm signed) | Log min/max/mean mỗi khối |
| Tiếng "xì", "kim loại", phụ âm s/x lạ | Downsample không lọc (`x[::3]`) → aliasing | Dùng resampler chuẩn; xem spectrogram tìm vệt phổ gập |
| TTS nghe "đục", thiếu độ trong | Pipeline ép downlink về 16 kHz (ví dụ HF s2s) hoặc xin `sample_rate=16000` từ TTS 48 kHz | Kiểm tra trần băng thông ở từng chặng (§2.9.2) |
| Timestamp VAD/ASR **trôi dần** so với thực tế, barge-in lệch | Làm tròn độ dài mỗi chunk khi resample tỉ lệ phân số; dùng wall-clock thay số mẫu | Resampler có state; đồng hồ bằng số mẫu |
| Stereo downmix nhỏ bất thường, "rỗng" | Hai kênh ngược pha bị trung bình triệt tiêu | Kiểm tra tương quan L/R; chọn một kênh |
| Nổ "bụp" khi tín hiệu to | Cộng int16 bị tràn số (wrap-around), hoặc `astype(int16)` trước khi clip | Xử lý bằng float32; clip trước khi ép kiểu |

**Checklist assert ở mỗi biên** (rẻ, nên bật cả ở production dưới dạng metric/log mẫu):

```python
def check_block(x: np.ndarray, fmt: AudioFormat, expect_len: int | None = None) -> None:
    assert x.dtype == np.float32, x.dtype
    assert x.ndim == 1 if fmt.channels == 1 else x.shape[-1] == fmt.channels, x.shape
    if expect_len is not None:
        assert x.shape[0] == expect_len, (x.shape, expect_len)
    peak = float(np.abs(x).max(initial=0.0))
    assert peak <= 1.0 + 1e-6, f"peak {peak}: quên chuẩn hoá hoặc chưa clip?"
    assert abs(float(x.mean())) < 0.1, "DC offset lớn: signed/unsigned hoặc endianness?"
```

---

## 2.12 Thực hành

Công cụ: `numpy`, `soundfile`, `soxr`, `scipy`, `librosa` (chỉ để vẽ), `ffmpeg`, Audacity/Sonic Visualiser (Phụ lục B của đề cương).

1. **Tính nhẩm.** Không dùng máy tính, điền: (a) 30 ms @ 8 kHz bao nhiêu samples, bytes PCM16? (b) 1 phút PCM16 mono 16 kHz bao nhiêu MB? (c) 960 samples stereo float32 bao nhiêu bytes, ở 48 kHz là bao nhiêu ms? (Đáp số: 240 samples/480 B; 1.92 MB; 7 680 B, 20 ms.)
2. **Aliasing.** Tạo chirp 0 → 20 kHz trong 2 s ở 48 kHz. Hạ xuống 16 kHz bằng (a) `x[::3]`, (b) `soxr.resample`. Vẽ spectrogram cả hai: ở (a) bạn sẽ thấy vệt đi lên tới 8 kHz rồi **gập xuống**, đi lên lại; ở (b) vệt dừng ở ~8 kHz.
3. **Sai dtype/endianness/rate.** Lấy một file WAV tiếng Việt, đọc bytes thô (bỏ header bằng `soundfile`) và cố tình diễn giải sai: `'>i2'`, `'<f4'`, rate ×2, rate ×½, mono↔stereo. Nghe từng trường hợp và đối chiếu với bảng §2.11 — mục tiêu là nhận ra lỗi bằng tai trong 2 giây.
4. **Quên chia 32768.** Đưa cùng một câu vào Silero VAD dưới ba dạng: đúng chuẩn, quên chia, chia hai lần. So sánh đường xác suất VAD. (Cẩn thận âm lượng nếu nghe thử dạng thứ hai.)
5. **Resample từng chunk vs stream.** Cắt một file 44.1 kHz thành khối 1024 frames. Resample về 16 kHz bằng (a) `soxr.resample` độc lập từng khối, (b) `soxr.ResampleStream`, (c) cả file một lần. So độ dài tổng và hiệu `(a)−(c)`, `(b)−(c)`; nghe (a) để nhận tiếng lách tách.
6. **Bit depth.** Lượng tử một câu xuống 8, 12, 16 bit (làm tròn trên thang 2^(N−1)), có và không có dither, ở mức −40 dBFS. Đo SNR so với bản gốc và chạy thử một ASR: từ bao nhiêu bit thì WER bắt đầu tăng?
7. **8 kHz → 16 kHz.** Lấy câu 16 kHz, hạ 8 kHz rồi nâng lại 16 kHz. So spectrogram và log-mel (Chương 4) với bản gốc; chạy ASR trên cả hai và so transcript (liên hệ Chương 1 §1.5.3).
8. **Ingress.** Dựng `UplinkIngress` (§2.10), bắn vào nó các message có độ dài ngẫu nhiên (kể cả số byte lẻ) cắt từ một file PCM16; xác nhận output ghép lại **bằng từng bit** với đường đọc cả file (khi in_rate = model_rate), và đúng số khối 512.

---

## 2.13 Đáp án các câu hỏi tự kiểm tra

**Q1. 1 giây PCM16 mono 16 kHz nặng bao nhiêu byte? Cùng thời lượng đó ở 48 kHz stereo float32 thì sao?**

- PCM16 mono 16 kHz: 16 000 samples × 1 kênh × 2 byte = **32 000 byte** (~31.25 KiB), bitrate 256 kbps.
- 48 kHz stereo float32: 48 000 × 2 × 4 = **384 000 byte** (~375 KiB), bitrate 3.072 Mbps — gấp **12 lần** (×3 rate, ×2 kênh, ×2 byte/mẫu).
- Hệ quả: gửi audio thô từ client ở định dạng của Web Audio (48 kHz float32) tốn băng thông gấp 12 lần PCM16 16 kHz mono mà ASR không được lợi gì; vì vậy MVP chuẩn hoá về PCM16 16 kHz mono binary (tài liệu thiết kế §5.1), và production dùng Opus (~16–32 kbps, Chương 3).

**Q2. 512 samples ở 16 kHz là bao nhiêu ms? 20 ms ở 48 kHz là bao nhiêu samples?**

- 512 / 16 000 = **32 ms** (đúng cửa sổ Silero VAD v5+; ở 8 kHz cửa sổ tương ứng là 256 samples = 32 ms).
- 48 000 × 0.020 = **960 samples** mỗi kênh (stereo: 1 920 giá trị; int16 stereo: 3 840 byte). Đây cũng là kích thước frame Opus 20 ms ở 48 kHz.
- Liên hệ §7.1: frame 20 ms @ 16 kHz = 320 samples không chia hết cho 512, nên cần reblocker; cứ 160 ms thì hai lưới thẳng hàng một lần; độ trễ chờ trung bình ~8 ms, tối đa 16 ms (§2.7.4).

**Q3. Upsample 8 kHz lên 16 kHz có khôi phục được thông tin không? Vì sao?**

- **Không.** Ở 8 kHz, theo Nyquist chỉ biểu diễn được tới 4 kHz, và lọc anti-alias đã **loại bỏ** mọi thứ trên ~3.4–4 kHz **trước** khi số hoá. Upsample chỉ là nội suy: chèn mẫu mới và lọc thông thấp ở 4 kHz để xoá ảnh phổ — nó đổi *cách biểu diễn* (nhiều mẫu hơn) chứ không thêm *nội dung tần số* nào. Dải 4–8 kHz của kết quả rỗng (hoặc chứa ảnh phổ giả nếu resampler kém).
- Vẫn phải upsample, vì model ASR/VAD 16 kHz yêu cầu **định dạng** 16 kHz; nếu đưa 8 kHz vào như thể 16 kHz, mọi thứ chậm ×2 và trầm 1 octave → rác. Nhưng sau upsample, các bin mel trên 4 kHz gần như rỗng, khác phân bố lúc train → ASR kém hơn trên audio wideband thật (Chương 1, Q2). Muốn tốt hơn: đánh giá/fine-tune trên audio 8 kHz thật; hoặc dùng bandwidth extension — nhưng đó là **sinh** nội dung đoán, không phải khôi phục (tài liệu thiết kế §5.1: "Upsample không khôi phục được thông tin đã mất", **Synthesis**).
- Thứ tự đúng với telephony: **decode codec (μ-law/A-law) → PCM 8 kHz → resample có lọc lên 16 kHz** (§5.1).

**Q4. Đọc int16 thành float32 mà quên chia 32768 thì chuyện gì xảy ra?**

- Biên độ lớn gấp 32 768 lần thang mong đợi, tức **+90.3 dB** (20·log10 32768). Một câu nói bình thường có đỉnh ~0.3 sẽ thành ~10 000.
- Hậu quả theo thành phần (model không báo lỗi, chỉ cho kết quả sai):
  - **Playback float32:** driver/Web Audio clip ở ±1.0 → gần như sóng vuông full scale, **cực to và rè** — nguy hiểm cho tai và loa. Đây là lý do cần assert/limiter trước playback.
  - **Silero VAD:** đầu vào nằm ngoài phân bố train → xác suất vô nghĩa (thường bão hoà, coi cả nhiễu nền là tiếng nói), làm hỏng endpointing và barge-in.
  - **Whisper và các model dùng log-mel:** công suất phổ tăng ×2^30 ≈ 10^9 → log10 tăng ~**+9**. Whisper clamp động theo max (max − 8) nên hình dạng spectrogram phần nào giữ được, nhưng bước chuẩn hoá cố định `(x + 4) / 4` khiến mọi feature lệch ~+2.26 đơn vị so với lúc train (**Synthesis**, suy từ công thức preprocess) → dễ ra transcript sai hoặc hallucination. Model có chuẩn hoá theo utterance (CMVN) chịu được tốt hơn, nhưng không nên trông vào đó.
  - **Ghi ra file float WAV** rồi mở bằng phần mềm khác: clip hoặc tự normalize tuỳ phần mềm → hành vi không nhất quán, bug khó tìm.
- Lỗi ngược (chia hai lần, hoặc chia một tín hiệu đã là float) làm tín hiệu nhỏ đi ~90 dB → VAD thấy im lặng mãi mãi, ASR trả rỗng.
- Phòng ngừa: một hàm quy đổi duy nhất (§2.5.3), assert `peak ≤ 1.0` và log RMS dBFS ở mỗi biên (§2.11).

---

## 2.14 Tóm tắt một trang

- Số hoá = **sampling** (rời rạc thời gian, `fs`) + **quantization** (rời rạc biên độ, `N` bit). Mảng số không tự mang metadata → mọi biên phải có **audio contract** (rate, dtype, kênh, layout, framing).
- **Nyquist:** chỉ biểu diễn được tới `fs/2`. Thành phần cao hơn **gập** xuống (aliasing), không đảo ngược được. Downsample **luôn** qua bộ lọc; không bao giờ `x[::k]`.
- **Bit depth:** ~6 dB/bit; int16 ≈ 98 dB là đủ cho speech. Transport int16, xử lý float32, clip **một lần** ở cuối. Dither gần như không quan trọng cho ASR.
- **Clipping** không đảo ngược được; giữ headroom (đỉnh −12…−6 dBFS khi thu), scale hỗn hợp thay vì clip, cẩn thận tràn số int16.
- **int16 ↔ float32:** chia/nhân 32768, `round` rồi `clip` rồi mới ép kiểu. Quên chia = +90 dB; chia hai lần = −90 dB.
- **Layout:** little-endian `s16le`/`f32le` là mặc định; interleaved `(frames, C)` vs planar `(C, frames)`; downmix bằng trung bình, đừng downmix call 2 kênh.
- **"Frame"** có ít nhất 3 nghĩa. Công thức: `samples = fs·ms/1000`, `bytes = samples·C·bytes_per_sample`. Thuộc: 512 @16k = 32 ms; 20 ms @16k = 320; 20 ms @48k = 960; 1 s PCM16 mono 16k = 32 000 B.
- **Resampling:** polyphase/windowed-sinc; chất lượng ↔ trễ ↔ CPU; dùng soxr/libsamplerate/ffmpeg/torchaudio. **Stream cần resampler có state theo session**; resample từng chunk độc lập gây click và trôi timeline.
- **Pipeline:** mic 48k → chuẩn hoá một lần về 16 kHz mono cho VAD/ASR; reblock 20 ms → 512 cho Silero; TTS giữ rate gốc (24/48k) tới playback adapter; telephony decode trước rồi mới resample; upsample không khôi phục thông tin.
- **Lỗi kinh điển** đoán được từ triệu chứng: chipmunk/slow-mo = sai rate/kênh; nhiễu trắng = sai dtype/endianness/byte lẻ; click đầu file = header WAV; click đều = resample không state; quá to/vuông = quên chia 32768.

## 2.15 Liên kết

**Chương sau:** Chương 3 (WAV/header, μ-law/A-law, Opus, container), Chương 4 (STFT, cửa sổ/hop, mel, MFCC), Chương 6 (capture/playback, buffer, jitter, clock drift), Chương 7 (AEC — cần căn chỉnh sample chính xác), Chương 10 (VAD và turn), Chương 16 (dataflow và audio contract toàn pipeline), Chương 20 (latency).

**Tài liệu thiết kế:** [§3 nguyên tắc 4, §5.1, §5.6, §7.1](thiet-ke-pipeline-speech-to-speech-tieng-viet.md).

**Wiki:**

- [Community STT-LLM-TTS Wiring](../wiki/community-stt-llm-tts-pipeline.md) — lệch sample rate (mic 48 kHz, Whisper 16 kHz, TTS 22–24 kHz) là nguồn bug sớm phổ biến nhất (**Reported**, anecdote).
- [VieNeu OpenAI Speech API](../wiki/vieneu-tts-openai-speech-api.md) — `pcm` là s16le mono không header; `sample_rate` 48 000/24 000/16 000/8 000 resample bằng soxr; header `X-Sample-Rate`; WAV stream với độ dài "unknown"; SSE base64.
- [Silero VAD](../wiki/silero-vad.md) — 8/16 kHz, cửa sổ cố định 512/256 samples từ v5, đầu vào tensor 1-D float32, khác biệt ~1e-3 giữa các đường resample.
- [Speech-to-Speech OpenAI-Compatible STT/TTS Backends](../wiki/speech-to-speech-openai-compatible-backends.md) — STT nhận WAV PCM16 mono 16 kHz; OpenAI Realtime cần 24 kHz; TTS ngoài bị chuyển về khối int16 16 kHz 512 samples.

**Đọc thêm ngoài wiki (giáo trình/tài liệu chuẩn, gợi ý):** Oppenheim & Schafer, *Discrete-Time Signal Processing* (sampling, multirate); Smith, *Digital Audio Resampling Home Page* (bandlimited interpolation, ccrma.stanford.edu/~jos/resample); Lyons, *Understanding Digital Signal Processing*; tài liệu libsoxr, libsamplerate (Secret Rabbit Code), ffmpeg `aresample` và danh sách sample format (`ffmpeg -sample_fmts`); đặc tả Web Audio API (AudioWorklet, render quantum); Microsoft/IBM RIFF WAVE specification (cấu trúc header, `WAVE_FORMAT_EXTENSIBLE`).
