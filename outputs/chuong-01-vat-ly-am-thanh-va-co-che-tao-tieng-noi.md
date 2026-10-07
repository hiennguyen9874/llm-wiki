# Chương 1. Vật lý âm thanh và cơ chế tạo tiếng nói 🔴

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần I.
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §5.1 (telephony 8 kHz, lệch sample rate), §5.2 (`speech_pad_ms`), §10 (corpus SNR 0/5/10/20 dB).
> **Cơ sở:** phần lớn là kiến thức giáo trình chuẩn về âm học, ngữ âm học và xử lý tín hiệu (không phải claim lấy từ nguồn trong wiki). Các con số "điển hình" là giá trị xấp xỉ, thay đổi theo người nói, thiết bị và tác giả. Những chỗ dẫn từ tài liệu thiết kế hoặc wiki được ghi rõ, giữ nguyên nhãn bằng chứng (**Reported**, **Synthesis**…).

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Mô tả được một tín hiệu âm thanh bằng tần số, biên độ, pha, và đổi qua lại giữa các thang dB khác nhau mà không nhầm.
2. Giải thích tiếng nói được tạo ra thế nào theo mô hình **source–filter**, và từ đó hiểu vì sao waveform, spectrogram, mel features trông như chúng trông.
3. Chỉ ra trên spectrogram: nguyên âm, F0/harmonics, formant, âm xát, âm tắc, khoảng lặng, tiếng vang.
4. Hiểu thanh điệu tiếng Việt là gì về mặt vật lý (đường F0 + chất giọng), và vì sao nó khiến việc cắt đầu/cuối câu nguy hiểm hơn tiếng Anh.
5. Biết vì sao audio telephony 8 kHz "nghe vẫn hiểu" nhưng ASR lại kém.
6. Định nghĩa SNR đúng cách và tự viết được hàm trộn nhiễu theo SNR mục tiêu để dựng corpus kiểm thử §10.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. Tần số, biên độ, pha khác nhau thế nào? dB là thang gì?
- Q2. Vì sao điện thoại 8 kHz vẫn nghe hiểu được, nhưng ASR lại kém hơn?
- Q3. F0, formant và thanh điệu liên quan với nhau thế nào?

---

## 1.1 Sóng âm là gì

### 1.1.1 Áp suất dao động

Âm thanh là **dao động áp suất** (pressure wave) lan truyền trong môi trường đàn hồi (không khí). Loa đẩy không khí tạo vùng nén (compression) và vùng giãn (rarefaction); micro đo **độ lệch áp suất so với áp suất khí quyển** theo thời gian. Thứ mà file audio lưu, sau khi số hoá, chính là chuỗi giá trị độ lệch áp suất đó (đã qua micro, preamp, ADC — Chương 2).

Hệ quả thực tế:

- Giá trị sample có **dấu** (dương = nén, âm = giãn), dao động quanh 0. Một tín hiệu có trung bình khác 0 rõ rệt (**DC offset**) là dấu hiệu phần cứng/quy đổi có vấn đề (ví dụ đọc PCM signed thành unsigned).
- "Im lặng" là giá trị gần 0, **không phải** giá trị nhỏ nhất của kiểu dữ liệu.

### 1.1.2 Các đại lượng cơ bản

Xét sóng sin thuần (pure tone):

```text
x(t) = A · sin(2π · f · t + φ)
```

| Đại lượng | Ký hiệu | Đơn vị | Ý nghĩa | Cảm nhận |
|---|---|---|---|---|
| Tần số (frequency) | f | Hz (lần/giây) | Số chu kỳ mỗi giây | Cao độ (pitch) |
| Chu kỳ (period) | T = 1/f | s | Thời gian một dao động | — |
| Biên độ (amplitude) | A | Pa, hoặc đơn vị số | Độ lệch cực đại | Độ to (loudness) |
| Pha (phase) | φ | rad hoặc độ | Vị trí trong chu kỳ tại t = 0 | Gần như không nghe được với một âm đơn |
| Bước sóng (wavelength) | λ = c/f | m | Khoảng cách một chu kỳ trong không gian | — |

Tốc độ âm trong không khí ở ~20 °C là **c ≈ 343 m/s**. Một vài bước sóng đáng nhớ:

| f | λ | Ghi chú |
|---|---|---|
| 100 Hz | 3.43 m | F0 giọng nam: bước sóng lớn hơn kích thước phòng nhỏ → cộng hưởng phòng (room modes) ảnh hưởng mạnh phần trầm |
| 1 kHz | 34 cm | Cỡ đầu người → hiệu ứng che đầu (head shadow) bắt đầu rõ |
| 4 kHz | 8.6 cm | |
| 8 kHz | 4.3 cm | Cỡ khoảng cách giữa 2 mic trên điện thoại → liên quan beamforming/aliasing không gian |

### 1.1.3 Tín hiệu thật = tổng của nhiều sin (Fourier)

Mọi tín hiệu thực tế có thể phân tích thành tổng các sóng sin với tần số, biên độ, pha khác nhau (**phân tích Fourier**). Đây là lý do ta nói "tín hiệu có năng lượng ở dải 100 Hz–4 kHz": nghĩa là các thành phần sin trong dải đó có biên độ lớn.

- **Tín hiệu tuần hoàn** (periodic) chu kỳ T chỉ chứa các tần số là bội số nguyên của f₀ = 1/T: f₀, 2f₀, 3f₀… gọi là **harmonics** (hài âm). Nguyên âm khi phát âm ổn định gần như tuần hoàn.
- **Tín hiệu không tuần hoàn** (aperiodic) như tiếng "s", tiếng gió, tiếng quạt có phổ liên tục, kiểu nhiễu.

### 1.1.4 Pha: khi nào quan trọng?

Tai người gần như không phân biệt được pha tuyệt đối của một âm ổn định, nên phần lớn đặc trưng ASR (spectrogram biên độ, log-mel) **bỏ pha**. Nhưng pha quan trọng ở các chỗ sau trong pipeline:

- **Cộng tín hiệu:** hai tín hiệu giống nhau lệch pha 180° triệt tiêu nhau. Đây là nguyên lý của **AEC** (trừ ước lượng echo khỏi tín hiệu mic) và cũng là lý do downmix stereo → mono có thể làm mất âm nếu hai kênh ngược pha (Chương 2).
- **Đảo cực** (polarity inversion, nhân −1): tai nghe giống hệt, nhưng so sánh mẫu-theo-mẫu (ví dụ test "audio bot vừa phát có trùng mic không") sẽ hỏng nếu không tính đến.
- **TTS/vocoder:** model sinh mel (chỉ biên độ) thì vocoder phải tự "bịa" lại pha. Vocoder kém pha → tiếng rè, kim loại (phasiness). Chi tiết ở Chương 13.
- **Ranh giới chunk:** nối hai chunk audio mà biên độ nhảy đột ngột (không liên tục pha/biên độ) tạo tiếng "click". Lý do cần fade/crossfade ngắn khi cắt hoặc barge-in (Chương 17).

---

## 1.2 Thang đo: dB, dBFS, SPL, RMS, LUFS

### 1.2.1 Decibel là thang **tỉ số logarit**

dB không phải đơn vị tuyệt đối; nó là **tỉ số** giữa hai đại lượng, lấy log:

```text
Với công suất / năng lượng:  L = 10 · log10(P / P_ref)  dB
Với biên độ (áp suất, điện áp, giá trị sample):  L = 20 · log10(A / A_ref)  dB
```

Vì công suất tỉ lệ với bình phương biên độ, hai công thức cho cùng kết quả. **Lỗi kinh điển:** dùng 10·log10 cho biên độ (sai 2 lần).

Bảng cần thuộc:

| Thay đổi | Biên độ × | Công suất × |
|---|---|---|
| +3 dB | ×1.41 | ×2 |
| +6 dB | ×2 | ×4 |
| +10 dB | ×3.16 | ×10 |
| +20 dB | ×10 | ×100 |
| −6 dB | ×0.5 | ×0.25 |
| −60 dB | ×0.001 | ×10⁻⁶ |

Mẹo cảm nhận: +10 dB thường được nghe "to gấp khoảng 2 lần"; chênh 1 dB là gần ngưỡng phân biệt được.

**Cộng dB của hai nguồn không tương quan** (ví dụ tiếng nói + nhiễu): cộng **công suất**, không cộng dB. Hai nguồn 60 dB cộng lại ra 63 dB, không phải 120 dB.

### 1.2.2 Các mốc tham chiếu khác nhau

| Thang | Tham chiếu (0 dB) | Dùng ở đâu |
|---|---|---|
| **dB SPL** (Sound Pressure Level) | 20 µPa (ngưỡng nghe ~1 kHz) | Âm học vật lý, mức ồn môi trường |
| **dBFS** (decibels relative to Full Scale) | Giá trị số lớn nhất biểu diễn được (int16: 32767; float: 1.0) | Mọi thứ trong file/buffer số. Luôn ≤ 0 nếu không clip |
| **dB (tỉ số)** | Tuỳ phép so sánh | SNR, gain, độ suy giảm |
| **LUFS / LKFS** | Thang loudness theo ITU-R BS.1770 | Chuẩn hoá độ to TTS/playback |

Một số mức SPL điển hình (xấp xỉ): thư viện yên tĩnh ~30–40 dB; nói chuyện bình thường cách 1 m ~55–65 dB; quán café ồn ~70–75 dB; đường phố nhiều xe máy ~75–85 dB; ngưỡng đau ~120–130 dB.

**dBFS không suy ra được dB SPL** nếu không biết độ nhạy mic và gain. Hệ quả: một ngưỡng VAD/barge-in tính theo RMS dBFS chỉ đúng với một cấu hình thiết bị; đổi mic/gain/AGC thì phải chỉnh lại. Đây là lý do tài liệu thiết kế đề xuất **ngưỡng thích ứng** — đo VAD prob và RMS trong 2–3 s đầu trước khi user nói (§5.2, **Reported** từ AI report, cần tune).

### 1.2.3 Peak và RMS

- **Peak** = |x| lớn nhất. Dùng để kiểm tra **clipping** (chạm 0 dBFS) và headroom.
- **RMS** (Root Mean Square) = √(trung bình x²). Đại diện cho **năng lượng trung bình**, gần với cảm nhận độ to hơn peak.

```text
RMS = sqrt( (1/N) · Σ x[n]² )
RMS_dBFS = 20 · log10(RMS / 1.0)        # với float trong [-1, 1]
```

- Sin full-scale có peak 0 dBFS và RMS ≈ −3.01 dBFS (vì RMS của sin = A/√2). Lưu ý: một số công cụ theo quy ước AES17 cộng thêm 3.01 dB để sin full-scale đọc 0 dBFS RMS — so sánh số giữa hai tool cần biết tool dùng quy ước nào.
- **Crest factor** = peak / RMS. Tiếng nói có crest factor cao (~12–20 dB): đỉnh nhọn, năng lượng trung bình thấp. Nên một file tiếng nói "đủ to" thường có RMS khoảng −20 đến −30 dBFS trong khi peak gần −1 đến −6 dBFS.
- RMS của **cả file** bị khoảng lặng kéo xuống. Khi cần mức tiếng nói, đo RMS trên **đoạn có tiếng** (active speech), ví dụ chỉ trên frame VAD = 1. ITU-T P.56 định nghĩa "active speech level" cho mục đích này.

### 1.2.4 Loudness (LUFS)

Tai không nhạy đều theo tần số (nhạy nhất ~2–5 kHz, kém ở tần thấp). **LUFS** (ITU-R BS.1770, EBU R128) đo độ to cảm nhận bằng cách: lọc **K-weighting** (giảm trầm, tăng nhẹ cao) → tính năng lượng theo block 400 ms → **gating** bỏ block quá nhỏ (im lặng) → lấy trung bình.

Mức tham chiếu thường gặp (xấp xỉ): broadcast EBU R128 **−23 LUFS**; podcast ~**−16 LUFS**; streaming nhạc ~**−14 LUFS**.

Trong pipeline: các backend TTS khác nhau (hoặc các voice/clone khác nhau) xuất ra độ to khác nhau. Chuẩn hoá loudness ở tầng playback giúp người dùng không phải chỉnh volume giữa các lượt, và giúp ngưỡng barge-in/echo ổn định hơn (Synthesis của bài viết này).

---

## 1.3 Cơ chế tạo tiếng nói: mô hình source–filter

### 1.3.1 Bộ máy phát âm

```text
Phổi (nguồn năng lượng: luồng khí)
  → Thanh quản / dây thanh (vocal folds)      ← SOURCE: rung tuần hoàn hoặc tạo nhiễu
  → Ống thanh âm (vocal tract):                ← FILTER: cộng hưởng, thay đổi theo vị trí lưỡi, môi, hàm
      hầu (pharynx) → khoang miệng (oral) ± khoang mũi (nasal)
  → Môi / mũi phát xạ ra không khí (radiation)
```

Ống thanh âm người lớn dài khoảng **14–17.5 cm** (nam dài hơn nữ, trẻ em ngắn hơn).

### 1.3.2 Source (nguồn)

Hai loại nguồn chính:

1. **Nguồn tuần hoàn (voicing):** dây thanh đóng–mở theo chu kỳ, tạo chuỗi xung khí. Tần số đóng–mở là **F0** (fundamental frequency). Phổ của nguồn này là các harmonics f₀, 2f₀, 3f₀… với biên độ giảm dần khoảng **−12 dB/octave**.
2. **Nguồn nhiễu (frication / turbulence):** luồng khí đi qua chỗ hẹp (răng–lưỡi, môi) tạo xoáy, sinh nhiễu phổ rộng. Ngoài ra có **burst** (bật hơi) ngắn khi một chỗ tắc được nhả ra.

Hai nguồn có thể đồng thời (ví dụ "v", "d" Bắc [z] là xát hữu thanh).

### 1.3.3 Filter (bộ lọc)

Ống thanh âm là một ống cộng hưởng. Các tần số cộng hưởng của nó gọi là **formant**: F1, F2, F3… Formant **không phải** là harmonics; formant là **đường bao** (envelope) khuếch đại những harmonics nằm gần nó.

Phép tính xấp xỉ quen thuộc: ống đều dài L, đóng một đầu (thanh môn), mở một đầu (môi) — **cộng hưởng phần tư bước sóng**:

```text
Fn = (2n − 1) · c / (4L)
L = 17.5 cm, c = 350 m/s  →  F1 ≈ 500 Hz, F2 ≈ 1500 Hz, F3 ≈ 2500 Hz
```

Đây là formant của nguyên âm trung tính (schwa, [ə]). Khi lưỡi, hàm, môi di chuyển, hình dạng ống thay đổi → formant dịch chuyển → ta nghe ra các nguyên âm khác nhau.

Quy tắc nhớ:

- **F1 ↔ độ mở miệng / độ cao lưỡi:** miệng càng mở (lưỡi thấp, như "a") → F1 càng cao (~700–900 Hz); lưỡi cao (như "i", "u") → F1 thấp (~250–350 Hz).
- **F2 ↔ lưỡi trước/sau và tròn môi:** nguyên âm trước ("i", "ê") → F2 cao (~2000–2500 Hz); nguyên âm sau tròn môi ("u", "ô") → F2 thấp (~600–900 Hz).
- **F3** liên quan đến các nét như uốn lưỡi (retroflex) và chất giọng; ít quyết định nguyên âm hơn.

Formant của một số nguyên âm tiếng Việt (giá trị **minh hoạ, xấp xỉ**, giọng nam; giọng nữ cao hơn khoảng 15–20%):

| Nguyên âm | IPA | Vị trí | F1 (Hz) | F2 (Hz) |
|---|---|---|---|---|
| i / y | [i] | trước, cao | ~300 | ~2200–2400 |
| ê | [e] | trước, vừa | ~450 | ~2000 |
| e | [ɛ] | trước, thấp-vừa | ~600 | ~1800 |
| a | [aː] | thấp | ~750–850 | ~1300 |
| ư | [ɯ] | sau, cao, không tròn | ~350 | ~1300–1500 |
| u | [u] | sau, cao, tròn | ~300 | ~700–800 |
| ô | [o] | sau, vừa, tròn | ~450 | ~850 |
| o | [ɔ] | sau, thấp-vừa, tròn | ~600 | ~1000 |

Đừng học thuộc con số; học **xu hướng** và tự đo trên giọng mình (bài thực hành 1.9).

### 1.3.4 Ghép lại: phổ tiếng nói = nguồn × bộ lọc × phát xạ

Trong miền tần số:

```text
S(f) = G(f) · V(f) · R(f)
  G(f): phổ nguồn (harmonics của F0 hoặc nhiễu), nghiêng −12 dB/oct
  V(f): đáp ứng ống thanh âm (các đỉnh formant)
  R(f): phát xạ ở môi, ~ +6 dB/oct
→ Phổ nguyên âm tổng thể nghiêng khoảng −6 dB/octave (spectral tilt).
```

Hệ quả trực tiếp tới feature engineering:

- Vì phổ nghiêng xuống, nhiều front-end cổ điển dùng **pre-emphasis** `y[n] = x[n] − 0.97·x[n−1]` để nâng tần cao trước khi phân tích (Chương 4).
- Vì F0 (nguồn) và formant (bộ lọc) **tách rời**, ta có thể đổi cao độ mà giữ nguyên âm, hoặc ngược lại. Đây là nền tảng của **vocoder**, **voice conversion**, và của việc **mel spectrogram** đủ để nhận dạng nội dung: mel với cửa sổ ~25 ms làm mờ bớt harmonics và giữ lại đường bao phổ (formant) — thứ mang thông tin "âm gì".
- **Cepstrum / MFCC** chính là kỹ thuật toán học để tách envelope (bộ lọc) khỏi harmonics (nguồn): log biến tích thành tổng, rồi biến đổi thêm một lần để tách thành phần biến thiên chậm (envelope) và nhanh (harmonics).

### 1.3.5 Hữu thanh / vô thanh, xát, tắc, mũi

| Lớp âm | Source | Dấu hiệu trên spectrogram | Ví dụ tiếng Việt (chữ viết → âm, giọng Bắc) |
|---|---|---|---|
| Nguyên âm | Tuần hoàn | Vạch harmonics ngang + dải formant đậm, năng lượng cao | a, ơ, i, u… |
| Âm mũi (nasal) | Tuần hoàn, khí qua mũi | Năng lượng thấp hơn nguyên âm, tập trung tần thấp (~250–300 Hz), có "lỗ" phổ (anti-formant) | m, n, nh [ɲ], ng/ngh [ŋ] |
| Âm xát vô thanh (voiceless fricative) | Nhiễu | Mảng nhiễu tần cao, **không** có vạch harmonics | ph [f], x [s], s [ʂ] (giọng có phân biệt), kh [x], h [h] |
| Âm xát hữu thanh | Nhiễu + tuần hoàn | Nhiễu tần cao + "voice bar" tần thấp | v [v], d/gi/r [z] (Bắc), g/gh [ɣ] |
| Âm tắc (stop/plosive) | Im lặng (closure) → burst | Khoảng trống ngắn rồi một vạch dọc (burst), rồi chuyển formant | b, đ, t, th [tʰ], c/k/q [k], tr/ch |
| Tắc cuối không bật hơi (unreleased) | Đóng mà không nhả | Formant nguyên âm "gãy" đột ngột, gần như không có burst | -p, -t, -c/-ch trong "đẹp", "mát", "các", "sách" |

Các điểm đáng chú ý với tiếng Việt và pipeline:

- **[s] và [ʂ] (x / s), [f] (ph)** có phần lớn năng lượng **trên 4 kHz**, có khi tới 8–10 kHz. Băng hẹp 8 kHz (chỉ giữ đến ~3.4 kHz) cắt gần hết các cue này → "xa"/"sa", "phải"/"hải" khó phân biệt hơn chỉ dựa trên âm học. Tai người bù được bằng ngữ cảnh; ASR một phần cũng bù được bằng language model, nhưng tên riêng, mã số, địa chỉ thì không có ngữ cảnh để bù.
- **Phụ âm cuối tắc không bật hơi** (-p, -t, -c) rất ngắn và năng lượng thấp; dấu hiệu của chúng chủ yếu nằm ở **chuyển động formant cuối nguyên âm** và sự dừng đột ngột. **Âm "h" đầu**, âm xát vô thanh đầu từ cũng có năng lượng thấp. VAD dựa trên năng lượng/xác suất dễ coi các đoạn này là "không phải speech" → nếu không có đệm, đầu/cuối câu bị cắt.
- Đây chính là lý do tài liệu thiết kế đặt **`speech_pad_ms` 100–200** "để giữ phụ âm đầu và cuối", và nhấn mạnh việc này "quan trọng với thanh điệu tiếng Việt" (§5.2, **Reported** từ AI report, cần tune). Lưu ý thêm từ tài liệu thiết kế: default `--speech_pad_ms 500` trong HF s2s (**Observed** trong code theo §5.3). Pad lớn an toàn hơn cho nội dung nhưng thêm độ trễ và kéo thêm nhiễu nền vào ASR — một trade-off phải đo.

---

## 1.4 F0, formant và thanh điệu tiếng Việt

### 1.4.1 F0 (tần số cơ bản) và pitch

- **F0** là đại lượng vật lý (Hz) = tần số rung của dây thanh. **Pitch** là cảm nhận cao độ; gần với F0 nhưng phi tuyến (tai cảm nhận cao độ gần theo thang log/mel).
- Dải F0 điển hình (xấp xỉ): nam ~85–180 Hz; nữ ~165–255 Hz; trẻ em ~250–400 Hz trở lên. Trong một câu, F0 của một người dao động khoảng 1 octave.
- F0 chỉ tồn tại ở đoạn **hữu thanh**. Ở đoạn vô thanh (âm xát vô thanh, khoảng lặng), F0 "không xác định" — các thuật toán trích F0 (YIN, pYIN, CREPE, RAPT, Praat) trả về cờ voiced/unvoiced kèm giá trị.
- Lỗi thường gặp khi trích F0: **octave error** (ra 2×F0 hoặc F0/2), đặc biệt ở đoạn **creaky voice** (giọng kẹt) — mà tiếng Việt lại có hai thanh dùng giọng kẹt (xem dưới).

**Hiện tượng "missing fundamental":** nếu loại bỏ hẳn thành phần F0 (ví dụ điện thoại cắt dưới 300 Hz, mà F0 giọng nam chỉ ~120 Hz), não vẫn nghe ra đúng cao độ nhờ **khoảng cách giữa các harmonics** còn lại (2f₀, 3f₀…). Đây là lý do thanh điệu vẫn nghe được qua điện thoại.

### 1.4.2 Formant ≠ F0

| | F0 | Formant |
|---|---|---|
| Sinh ra bởi | Source (dây thanh) | Filter (ống thanh âm) |
| Trên spectrogram băng hẹp | Khoảng cách giữa các vạch harmonics | Vùng các harmonics được tô đậm |
| Mang thông tin | Thanh điệu, ngữ điệu, cảm xúc, giới tính/tuổi, danh tính | Nguyên âm, phụ âm (qua chuyển động formant), danh tính |
| Thay đổi độc lập? | Có — hát một nguyên âm ở nhiều nốt | Có — nói nhiều nguyên âm ở cùng cao độ |

Lưu ý kỹ thuật: khi F0 cao (giọng nữ, trẻ em), harmonics thưa → formant bị "lấy mẫu" thưa → ước lượng formant khó và kém chính xác hơn. Đây là một nguồn chênh lệch chất lượng ASR/TTS theo giới tính và tuổi.

### 1.4.3 Thanh điệu tiếng Việt = đường F0 + chất giọng + trường độ

Tiếng Việt là ngôn ngữ **có thanh điệu** (tonal): cùng chuỗi phụ âm–nguyên âm, đổi thanh là đổi nghĩa ("ma, mà, má, mả, mã, mạ"). Về vật lý, thanh điệu là tổ hợp:

1. **Đường nét F0** theo thời gian (bằng, lên, xuống, gãy).
2. **Chất giọng (phonation):** bình thường (modal), thở (breathy), kẹt/thanh hầu hoá (creaky / glottalized).
3. **Trường độ và cường độ:** một số thanh ngắn hơn, tắt đột ngột.

Mô tả xấp xỉ cho **giọng Bắc chuẩn** (thang Chao 1–5, 5 là cao nhất; các tác giả ghi số hơi khác nhau):

| Thanh | Ví dụ | Đường F0 (xấp xỉ) | Chất giọng / ghi chú |
|---|---|---|---|
| Ngang | ma | 33–44, bằng, ở giữa-cao | Modal |
| Huyền | mà | 21–31, thấp, đi xuống nhẹ | Có thể hơi thở (breathy) |
| Sắc | má | 35–45, đi lên | Modal; trong âm tiết tắc (-p/-t/-c/-ch) thì ngắn và lên nhanh |
| Hỏi | mả | 313–214, xuống rồi (có thể) lên lại | Có thể có giọng kẹt ở đáy |
| Ngã | mã | 3ˀ5 / 4ˀ5, lên nhưng bị **ngắt quãng thanh hầu** ở giữa | Glottalized: F0 có thể "đứt" hoặc nhảy |
| Nặng | mạ | 21ˀ / 32ˀ, thấp, xuống nhanh, **kết thúc bằng tắc thanh hầu** | Glottalized, ngắn; trong âm tiết tắc thì rất ngắn |

Biến thể phương ngữ quan trọng cho ASR/TTS:

- **Giọng Nam** thường **nhập hỏi và ngã** (còn 5 thanh về mặt âm học), và nặng ít/không thanh hầu hoá, đi xuống rồi lên.
- **Giọng Trung** (Huế, Nghệ Tĩnh…) có hệ thống đường nét khác hẳn; một số vùng có ít thanh hơn.
- Đây là lý do corpus đánh giá §10 yêu cầu **giọng Bắc/Trung/Nam** riêng.

**Âm tiết tắc** (kết thúc bằng -p, -t, -c, -ch) chỉ mang thanh **sắc** hoặc **nặng**. Chúng ngắn, kết thúc đột ngột — trùng với vùng mà VAD dễ cắt.

### 1.4.4 Hệ quả cho pipeline

- **Cắt mất 50–100 ms cuối âm tiết** có thể xoá chính phần F0 phân biệt hỏi/ngã/nặng (phần "gãy", "lên lại", hay tắc thanh hầu) → ASR nhầm thanh, TTS round-trip CER tăng. Vì thế `speech_pad_ms`, pre-roll buffer và không cắt audio trước khi endpoint thực sự xảy ra là những quyết định có nền tảng ngữ âm, không chỉ là tham số kỹ thuật.
- **Giọng kẹt (creaky)** có năng lượng thấp, không tuần hoàn đều → một VAD hoặc pitch tracker có thể coi là unvoiced/nhiễu. Kiểm tra VAD trên câu kết thúc bằng thanh nặng/ngã là test case đáng có.
- **Ngữ điệu câu chồng lên thanh điệu:** câu hỏi, nhấn mạnh, cảm xúc làm dịch toàn bộ đường F0. Model end-of-turn dùng prosody (Smart Turn và các detector khác — Chương 10) phải học phân biệt "F0 đi xuống vì thanh huyền/nặng" với "F0 đi xuống vì hết câu". Đây là một lý do hợp lý để nghi ngờ detector huấn luyện chủ yếu trên ngôn ngữ không thanh điệu và phải đo false-cutoff riêng cho tiếng Việt (Synthesis; xem ngưỡng "false-interruption tiếng Việt > 10%" ở §10 tài liệu thiết kế).
- **TTS:** thanh điệu sai là lỗi bị người Việt nghe ra ngay, nên §10 yêu cầu chấm riêng "thanh điệu, phát âm" trong MOS/CMOS. Vocoder/codec nén mạnh có thể làm mờ giọng kẹt → ngã/nặng nghe giống sắc/huyền.

---

## 1.5 Dải tần của tiếng nói; narrowband và wideband

### 1.5.1 Năng lượng nằm ở đâu

| Dải | Chứa gì |
|---|---|
| < 80–100 Hz | Ít thông tin tiếng nói; chủ yếu nhiễu: rung bàn, gió, hum điện lưới **50 Hz** (Việt Nam dùng lưới 50 Hz) và hài 100/150 Hz |
| ~100–300 Hz | F0 và vài harmonics đầu; voice bar của âm hữu thanh; âm mũi |
| ~300 Hz–1 kHz | F1; phần lớn **năng lượng** tiếng nói |
| ~1–3.5 kHz | F2, F3; phần lớn **độ dễ hiểu** (intelligibility); tai người nhạy nhất ở ~2–5 kHz |
| ~3.5–8 kHz | Âm xát (s, x, ph), burst của âm tắc, độ "trong" và tự nhiên |
| > 8 kHz | Phần trên của s/x, hơi thở, độ "sáng" (air); quan trọng cho chất lượng TTS, ít quan trọng cho ASR |

Câu ghi nhớ của đề cương: năng lượng chính ~100 Hz–4 kHz; phụ âm xát lên tới 8 kHz trở lên.

### 1.5.2 Các băng chuẩn

Với sample rate fs, tần số cao nhất biểu diễn được là fs/2 (Nyquist — Chương 2).

| Tên | Băng thông âm thanh (xấp xỉ) | Sample rate | Ví dụ |
|---|---|---|---|
| **Narrowband (NB)** | 300–3400 Hz | 8 kHz | PSTN, G.711 μ-law/A-law, AMR-NB, nhiều tổng đài SIP |
| **Wideband (WB)** | 50–7000 Hz | 16 kHz | G.722, AMR-WB ("HD Voice"), **đầu vào chuẩn của phần lớn ASR** (Whisper, Silero VAD 16 kHz) |
| **Super-wideband (SWB)** | 50–14000 Hz | 32 kHz | EVS, Opus SWB |
| **Fullband (FB)** | 20–20000 Hz | 44.1 / 48 kHz | Mic laptop/điện thoại, Opus, đầu ra TTS chất lượng cao (ví dụ VieNeu 48 kHz theo §3 tài liệu thiết kế) |

Whisper nhận log-mel 16 kHz (80 bin; large-v3 dùng 128 bin — theo trang wiki [Whisper Large v3](../wiki/whisper-large-v3.md)), nghĩa là dải mel của nó trải đến **8 kHz**. Khi đưa audio 8 kHz upsample lên 16 kHz vào, toàn bộ các bin mel trên ~4 kHz **gần như rỗng** — một phân bố feature model hiếm khi thấy lúc train trên audio wideband.

### 1.5.3 Vì sao upsample không cứu được

Tài liệu thiết kế §5.1: "Với telephony 8 kHz: decode đúng rồi mới resample. Upsample không khôi phục được thông tin đã mất" (**Synthesis**). Lý do vật lý: thông tin trên 4 kHz đã bị lọc anti-alias loại bỏ **trước** khi số hoá ở 8 kHz; resample chỉ đổi cách biểu diễn, không thêm tần số mới. (Các model **bandwidth extension** có thể "đoán" lại phần cao, nhưng đó là sinh dữ liệu, không phải khôi phục — có thể sinh sai phụ âm.)

---

## 1.6 Âm học phòng và môi trường nhiễu

### 1.6.1 Lan truyền và khoảng cách

- Trong trường tự do, mức âm giảm **~6 dB mỗi lần gấp đôi khoảng cách** (luật nghịch đảo bình phương). Người nói cách mic 25 cm so với 1 m: tiếng nói trực tiếp yếu hơn ~12 dB, trong khi nhiễu phòng gần như không đổi → SNR tụt ~12 dB.
- **Near-field** (mic cầm tay, headset, cách miệng vài cm): SNR cao, ít vang; mic định hướng có **proximity effect** (tăng trầm khi rất gần). **Far-field** (loa thông minh, laptop đặt bàn, mic hội nghị cách 1–5 m): SNR thấp, vang nhiều, echo từ loa của chính thiết bị mạnh.
- Corpus §10 tách riêng "far-field" vì đây là một điều kiện suy giảm độc lập với nhiễu.

### 1.6.2 Reverberation (vang)

Trong phòng, mic nhận: **âm trực tiếp** → **phản xạ sớm** (early reflections, < ~50 ms, làm tiếng "dày" hơn, ít hại) → **vang muộn** (late reverberation, đuôi suy giảm theo hàm mũ, làm nhoè các âm sau).

- **RT60:** thời gian để năng lượng vang giảm 60 dB sau khi nguồn tắt. Công thức Sabine: `RT60 ≈ 0.161 · V / A` (V: thể tích m³, A: tổng diện tích hấp thụ tương đương m²). Giá trị điển hình (xấp xỉ): phòng thu/xe hơi ~0.1–0.3 s; phòng ngủ có đồ đạc ~0.3–0.5 s; phòng họp tường kính, sảnh ~0.8–1.5 s trở lên.
- **DRR** (Direct-to-Reverberant Ratio) và **critical distance**: vượt quá một khoảng cách nhất định, năng lượng vang lớn hơn năng lượng trực tiếp. Far-field thường nằm trong vùng này.
- Mô phỏng: tín hiệu vang = tiếng nói sạch **convolve** với **RIR** (Room Impulse Response). Có thể dùng RIR đo thật (bộ dữ liệu công khai) hoặc mô phỏng (image-source method, ví dụ `pyroomacoustics`).

Ảnh hưởng tới pipeline:

- **Vang không giống nhiễu cộng:** nó là bản sao trễ của chính tiếng nói, nên **denoiser** thường xử lý kém; cần dereverberation riêng (ví dụ WPE) hoặc chấp nhận.
- **Đuôi vang kéo dài "speech"** sau khi người nói dừng → VAD báo kết thúc muộn hơn → tăng endpoint latency; và đuôi vang của **giọng bot** quay lại mic là một phần lý do AEC khó (Chương 7).
- Vang làm nhoè chuyển động formant và tắc cuối → tác động lên chính các cue mà tiếng Việt cần (phụ âm cuối, thanh nặng/ngã).

### 1.6.3 Nhiễu nền: stationary và non-stationary

| Loại | Đặc điểm | Ví dụ | Xử lý dễ/khó |
|---|---|---|---|
| **Stationary** (dừng) | Thống kê phổ gần như không đổi theo thời gian | Quạt, điều hoà, hiss mic, hum 50 Hz | Dễ: ước lượng phổ nhiễu lúc im lặng rồi trừ (spectral subtraction, Wiener); VAD ngưỡng thích ứng làm tốt |
| **Non-stationary** (không dừng) | Thay đổi nhanh, xuất hiện đột ngột | Còi/xe máy, cửa đóng, bát đũa, gõ phím, ho, chó sủa | Khó: dễ gây false trigger VAD/barge-in |
| **Babble / speech-like** | Tiếng người khác, TV, radio | Quán café, văn phòng mở, TV nền | **Khó nhất**: có cấu trúc phổ–thời gian giống tiếng nói; VAD bắt nhầm, ASR có thể chép lời người khác. Đòi hỏi speaker lock/target-speaker (Chương 14) |
| **Echo của chính bot** | Tiếng TTS phát ra loa quay lại mic | Loa ngoài, loa thông minh | Bắt buộc AEC khi dùng loa (Chương 7) |

Thêm hai hiệu ứng thực tế mà trộn nhiễu tổng hợp **không** mô phỏng được:

- **Lombard effect:** người nói trong môi trường ồn tự động nói to hơn, F0 cao hơn, nguyên âm dài hơn, phổ nghiêng ít hơn. Tiếng nói sạch + nhiễu ≠ tiếng nói thật trong quán ồn. Corpus nên có cả bản ghi thật, không chỉ bản trộn.
- **Xử lý của thiết bị:** điện thoại/trình duyệt đã chạy AGC, noise suppression, AEC (`echoCancellation`, `noiseSuppression`, `autoGainControl` — §5.1 tài liệu thiết kế) trước khi audio tới server. Đầu vào thật của bạn đã là tín hiệu "đã xử lý".

Về việc có nên khử nhiễu trước ASR: wiki ghi nhận bằng chứng **mâu thuẫn** — hai nghiên cứu báo enhancement làm Whisper và các ASR khác tệ hơn trong mọi cấu hình thử, một nghiên cứu khác báo cải thiện trên CHiME-4; không nghiên cứu nào trên tiếng Việt. Thực hành được đề xuất là không denoise nhánh ASR, chỉ denoise nhẹ nhánh VAD/barge-in, và A/B test bằng WER/CER tiếng Việt ở SNR 0/5/10/20 dB (**Reported**, xem [Speech Enhancement Before ASR](../wiki/speech-enhancement-before-asr.md)). Hiểu biết vật lý ở chương này giải thích **vì sao** điều đó có lý: denoiser có thể xoá chính các cue năng lượng thấp (âm xát, tắc cuối, giọng kẹt) hoặc thêm artifact mà ASR chưa từng thấy (Synthesis).

---

## 1.7 SNR: định nghĩa và trộn nhiễu theo SNR mục tiêu

### 1.7.1 Định nghĩa

```text
SNR_dB = 10 · log10( P_signal / P_noise )
       = 20 · log10( RMS_signal / RMS_noise )
P = (1/N) · Σ x[n]²   (công suất trung bình = RMS²)
```

Đọc nhanh: SNR 20 dB = tiếng nói mạnh gấp 100 lần nhiễu về công suất (văn phòng yên tĩnh); 10 dB ≈ ×10 (quán café vừa); 5 dB ≈ ×3.2 (ồn); 0 dB = ngang nhau (rất ồn, đường phố cạnh xe máy); SNR âm = nhiễu lớn hơn tiếng nói. Đây là bốn mức của corpus §10.

Những chỗ định nghĩa dễ sai:

1. **Tính P_signal trên toàn file hay chỉ đoạn có tiếng?** Nếu clip có 50% im lặng, công suất trung bình toàn file thấp hơn ~3 dB so với active speech → SNR "danh nghĩa" lệch 3 dB. Chọn một quy ước (khuyến nghị: active speech, theo VAD hoặc P.56), ghi vào metadata corpus, và dùng nhất quán.
2. **SNR toàn cục vs SNR theo đoạn (segmental SNR):** nhiễu non-stationary có thể có SNR trung bình 10 dB nhưng có đoạn −5 dB (lúc còi xe). Báo cáo SNR toàn cục là đủ cho corpus, nhưng khi phân tích lỗi cần nhìn cục bộ.
3. **Trọng số tần số:** SNR thuần không tính đến việc nhiễu ở tần thấp (hum) ít hại tới độ hiểu hơn nhiễu ở 1–4 kHz. Hai nhiễu cùng SNR có thể gây WER rất khác nhau → corpus cần **nhiều loại nhiễu** ở mỗi mức SNR.

### 1.7.2 Công thức trộn

Cần hệ số α để `y = s + α·n` đạt SNR mục tiêu:

```text
SNR_target = 10·log10( P_s / (α² · P_n) )
⇒ α = sqrt( P_s / ( P_n · 10^(SNR_target / 10) ) )
```

### 1.7.3 Code tham khảo

```python
import numpy as np

def power(x: np.ndarray, mask: np.ndarray | None = None) -> float:
    """Công suất trung bình; mask (bool) để chỉ tính trên đoạn có tiếng."""
    x = x if mask is None else x[mask]
    return float(np.mean(x.astype(np.float64) ** 2))

def rms_dbfs(x: np.ndarray, eps: float = 1e-12) -> float:
    """x là float trong [-1, 1]."""
    return 10.0 * np.log10(power(x) + eps)

def fit_noise_length(noise: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    """Cắt ngẫu nhiên hoặc lặp nhiễu cho đủ n mẫu."""
    if len(noise) >= n:
        start = rng.integers(0, len(noise) - n + 1)
        return noise[start:start + n]
    reps = int(np.ceil(n / len(noise)))
    return np.tile(noise, reps)[:n]   # lặp có thể tạo click ở điểm nối; tốt hơn là crossfade

def mix_at_snr(speech: np.ndarray, noise: np.ndarray, snr_db: float,
               speech_mask: np.ndarray | None = None,
               rng: np.random.Generator | None = None,
               peak_limit: float = 0.99) -> tuple[np.ndarray, dict]:
    """Trộn nhiễu vào tiếng nói ở SNR mục tiêu.

    Giả định: cùng sample rate, mono, float32 trong [-1, 1].
    speech_mask: bool theo mẫu, True ở đoạn có tiếng (để đo active-speech power).
    """
    rng = rng or np.random.default_rng()
    noise = fit_noise_length(noise, len(speech), rng)
    p_s = power(speech, speech_mask)
    p_n = power(noise)
    if p_n == 0.0:
        raise ValueError("noise is digital silence")
    alpha = np.sqrt(p_s / (p_n * 10.0 ** (snr_db / 10.0)))
    mix = speech + alpha * noise

    # Tránh clipping: scale CẢ hỗn hợp (giữ nguyên SNR), không clip cứng.
    peak = float(np.max(np.abs(mix)))
    gain = peak_limit / peak if peak > peak_limit else 1.0
    mix = (mix * gain).astype(np.float32)

    # Kiểm tra lại SNR thực tế
    achieved = 10.0 * np.log10(p_s / power(alpha * noise))
    return mix, {"alpha": float(alpha), "gain": gain, "snr_achieved_db": float(achieved)}
```

Checklist khi dựng corpus SNR cho §10:

- [ ] Tiếng nói và nhiễu **cùng sample rate, cùng số kênh, cùng dtype** trước khi trộn (lệch sample rate là lỗi số 1, xem Chương 2).
- [ ] Chọn và ghi lại quy ước P_signal (toàn file hay active speech).
- [ ] Tránh clipping bằng cách scale cả hỗn hợp; ghi lại `gain` vì nó làm đổi mức tuyệt đối (ảnh hưởng ngưỡng VAD theo RMS).
- [ ] Mỗi mức SNR dùng **nhiều loại nhiễu** (café/babble, xe máy/đường phố, TV, quạt) và offset ngẫu nhiên có seed cố định để tái lập được.
- [ ] Nhiễu dùng cho test **không trùng** nhiễu dùng cho augmentation khi train/fine-tune.
- [ ] Giữ bản sạch tương ứng để tách lỗi do nhiễu khỏi lỗi do model.
- [ ] Bổ sung một ít bản ghi **thật** trong môi trường ồn (Lombard, xử lý của thiết bị) — trộn tổng hợp không thay thế được.
- [ ] Nếu mô phỏng far-field: convolve tiếng nói với RIR **trước**, rồi mới cộng nhiễu ở SNR mục tiêu (nhiễu thật cũng bị vang, nên tốt nhất là nhiễu cũng qua RIR hoặc dùng nhiễu ghi trong phòng).

---

## 1.8 Đọc waveform và spectrogram

### 1.8.1 Waveform

Trục ngang thời gian, trục dọc biên độ. Đọc được:

- Đoạn có tiếng vs im lặng; mức to/nhỏ; **clipping** (đỉnh bị cắt phẳng ở ±1.0); DC offset (cả dạng sóng lệch khỏi 0).
- Ranh giới âm tiết thô (tiếng Việt đơn lập, mỗi âm tiết thường là một "cục" năng lượng).
- Không đọc được: âm gì, cao độ bao nhiêu (trừ khi zoom vào để đếm chu kỳ).

### 1.8.2 Spectrogram

Trục ngang thời gian, trục dọc tần số, độ đậm = năng lượng (thường theo dB). Được tính bằng STFT: chia tín hiệu thành các cửa sổ ngắn chồng lên nhau, FFT từng cửa sổ (chi tiết ở Chương 4). Độ dài cửa sổ quyết định bạn nhìn thấy gì — **trade-off thời gian–tần số**:

| | Wideband spectrogram | Narrowband spectrogram |
|---|---|---|
| Cửa sổ | Ngắn, ~3–5 ms (ngắn hơn một chu kỳ F0) | Dài, ~25–50 ms (nhiều chu kỳ F0) |
| Thấy rõ | **Formant** (dải đậm ngang), burst, các vạch dọc theo từng nhịp dây thanh | **Harmonics** (các vạch ngang song song), đường F0 |
| Dùng để | Đọc nguyên âm/phụ âm | Đọc thanh điệu, ngữ điệu |

Lưu ý thuật ngữ: "wideband/narrowband spectrogram" nói về **độ phân giải phân tích**, khác hẳn "wideband/narrowband audio" (sample rate) ở mục 1.5.

Feature ASR điển hình (log-mel, cửa sổ ~25 ms, hop 10 ms ở 16 kHz) nằm **ở giữa** hai cực: đủ dài để ổn định, nhưng nhờ các bộ lọc mel rộng ở tần cao nên harmonics bị làm mờ, chủ yếu giữ envelope. Ở tần thấp, bin mel hẹp nên vẫn còn một phần thông tin harmonics/F0 — điều có ích cho thanh điệu (Synthesis; chi tiết Chương 4).

### 1.8.3 Bảng nhận dạng nhanh

| Bạn thấy trên spectrogram | Khả năng là |
|---|---|
| Vạch ngang song song đều, có 2–4 dải đậm | Nguyên âm (hữu thanh); khoảng cách vạch = F0, dải đậm = formant |
| Các vạch harmonics cong lên/xuống theo thời gian | Thanh điệu hoặc ngữ điệu đang thay đổi F0 |
| Harmonics mờ, các nhịp dọc thưa và không đều ở cuối âm tiết | Giọng kẹt (creaky) — thường gặp ở thanh nặng/ngã giọng Bắc |
| Mảng nhiễu tần cao (> 3–4 kHz), không có vạch ngang | Âm xát vô thanh (s, x, ph, kh) hoặc tiếng xì, gió |
| Khoảng trắng ngắn (~50–100 ms) rồi một vạch dọc mảnh | Âm tắc: closure rồi burst |
| Năng lượng thấp, tập trung dưới ~500 Hz, nối liền nguyên âm | Âm mũi (m, n, ng, nh) |
| Dải ngang mảnh, cố định ở 50/100/150 Hz suốt file | Hum điện lưới 50 Hz |
| Nhiễu phủ đều mọi lúc, mọi tần số | Nhiễu stationary (quạt, hiss) |
| Âm tiết như bị "kéo đuôi" mờ sang phải | Reverberation |
| Không có gì trên ~4 kHz (cắt phẳng), hoặc trên ~8 kHz | Audio từng ở 8 kHz (hoặc 16 kHz) rồi bị upsample |
| Năng lượng đều ở mọi tần số tại một thời điểm (vạch dọc đậm, dài toàn dải) | Click, pop, clipping, ranh giới chunk không liên tục |

Dòng "cắt phẳng ở 4 kHz" là cách **chẩn đoán nhanh** lỗi lệch sample rate hoặc nguồn telephony: mở spectrogram của audio đầu vào ASR, nếu file khai báo 16 kHz mà phía trên 4 kHz trống trơn, audio đã từng đi qua 8 kHz.

---

## 1.9 Thực hành

Công cụ: Audacity hoặc Sonic Visualiser hoặc Praat (xem spectrogram, đo F0/formant); `numpy`, `soundfile`, `librosa` (Phụ lục B của đề cương).

1. **Sáu thanh điệu.** Ghi âm "ma, mà, má, mả, mã, mạ" (và nếu được, nhờ một người giọng Nam đọc lại). Trong Praat: vẽ đường F0 cho mỗi âm tiết, so với bảng 1.4.3. Quan sát chỗ F0 bị đứt ở ngã/nặng (giọng Bắc). Ghi lại dải F0 của chính bạn.
2. **Formant.** Ghi "i, ê, e, a, ư, u, ô, o" kéo dài ~1 s. Đo F1/F2, vẽ lên mặt phẳng F2 (trục ngang, đảo chiều) – F1 (trục dọc, đảo chiều). Bạn sẽ thấy "tam giác nguyên âm".
3. **Âm xát và băng hẹp.** Ghi "xa, sa, pha, kha, ha". Xem spectrogram tới 8 kHz. Sau đó resample 16k → 8k → 16k (sox/ffmpeg), nghe lại và xem lại spectrogram: phần nào biến mất?
4. **Cắt cuối âm tiết.** Ghi "đẹp", "mát", "bạc", "mã", "mạ". Cắt bớt 50 ms, 100 ms, 150 ms cuối, nghe lại. Từ mức nào bạn bắt đầu nghe sai thanh hoặc mất phụ âm cuối? Liên hệ với `speech_pad_ms`.
5. **dB.** Tạo sin 1 kHz biên độ 0.5. Tính peak dBFS và RMS dBFS bằng tay rồi bằng code (đáp số: −6.02 dBFS và −9.03 dBFS). Cộng hai nhiễu trắng độc lập cùng RMS −30 dBFS — kết quả bao nhiêu? (≈ −27 dBFS.)
6. **SNR.** Dùng `mix_at_snr` trộn một câu với nhiễu quạt và nhiễu babble ở 0/5/10/20 dB. Nghe so sánh: cùng SNR, loại nào khó hiểu hơn? Thử tính SNR theo toàn file và theo active speech để thấy chênh lệch.
7. **Vang.** Ghi cùng một câu ở cự ly 10 cm và 2 m trong phòng tắm hoặc phòng trống. So sánh spectrogram và đo thời gian đuôi năng lượng sau âm tiết cuối.

---

## 1.10 Đáp án các câu hỏi tự kiểm tra

**Q1. Tần số, biên độ, pha khác nhau thế nào? dB là thang gì?**

- **Tần số** là số chu kỳ mỗi giây (Hz), quyết định cao độ; **biên độ** là độ lệch cực đại so với 0, quyết định độ to; **pha** là vị trí trong chu kỳ tại một mốc thời gian — gần như không nghe được với một âm đơn, nhưng quyết định kết quả khi **cộng** tín hiệu (triệt tiêu, AEC, downmix), và là thứ vocoder phải tái tạo.
- **dB** là thang **logarit của tỉ số**: 10·log10 cho công suất, 20·log10 cho biên độ. Nó luôn cần một tham chiếu: dB SPL (20 µPa, vật lý), dBFS (full-scale số, ≤ 0), dB tỉ số thuần (SNR, gain). LUFS là thang độ to cảm nhận có trọng số tần số và gating. dBFS không đổi ra được dB SPL nếu không biết chuỗi thiết bị.

**Q2. Vì sao điện thoại 8 kHz vẫn nghe hiểu được, nhưng ASR lại kém hơn?**

- **Nghe hiểu được** vì: F1–F3 (thông tin nguyên âm và phần lớn chuyển động formant) nằm trong 300–3400 Hz; não tái tạo cao độ từ khoảng cách harmonics dù F0 bị cắt (**missing fundamental**), nên thanh điệu vẫn nghe ra; và người nghe bù phần mất bằng ngữ cảnh.
- **ASR kém hơn** vì:
  1. **Mất thông tin thật** trên ~3.4–4 kHz: cue của âm xát (s/x/ph), burst âm tắc; dưới ~300 Hz: F0 và voice bar. Các cặp tối thiểu, tên riêng, mã số mất cue không có ngữ cảnh để bù.
  2. **Lệch phân bố (domain mismatch):** phần lớn ASR train trên audio 16 kHz wideband; audio 8 kHz upsample để lại các bin mel trên 4 kHz gần như rỗng — model hiếm khi thấy lúc train. Upsample không khôi phục được thông tin (§5.1 tài liệu thiết kế, **Synthesis**).
  3. **Codec và kênh:** G.711/AMR-NB thêm méo lượng tử, packet loss, xử lý AGC/NS của mạng, thường kèm môi trường ồn và mic chất lượng thấp.
  4. **Lỗi kỹ thuật:** decode sai hoặc resample sai (khai báo nhầm sample rate) làm hỏng hẳn transcript. Tài liệu thiết kế ghi nhận cộng đồng cho rằng phần lớn transcript rác là do lệch sample rate chứ không phải model (**Reported**, anecdote).
  - Vì thế corpus §10 có trục riêng "call 8 kHz so với mic 16 kHz", và một model ASR cho kênh telephony nên được đánh giá (hoặc fine-tune) trên audio 8 kHz thật.

**Q3. F0, formant và thanh điệu liên quan với nhau thế nào?**

- Theo mô hình **source–filter**: **F0** là tần số rung của dây thanh (source), quyết định cao độ; **formant** là tần số cộng hưởng của ống thanh âm (filter), quyết định âm sắc nguyên âm/phụ âm. Hai thứ **độc lập** về mặt sinh lý: đổi F0 không đổi nguyên âm và ngược lại. Trên spectrogram, F0 là khoảng cách giữa các harmonics, formant là đường bao tô đậm các harmonics.
- **Thanh điệu tiếng Việt** chủ yếu là **đường nét F0 theo thời gian**, cộng thêm **chất giọng** (breathy ở huyền, creaky/glottalized ở hỏi–ngã–nặng giọng Bắc) và **trường độ**. Nó không nằm ở formant — nhưng vì creaky voice và độ ngắn của thanh nặng/sắc trong âm tiết tắc cũng làm thay đổi phổ và năng lượng, model phải nhìn cả F0 lẫn chất giọng.
- Hệ quả pipeline: feature/model phải giữ đủ thông tin F0 (không chỉ envelope); VAD không được cắt phần cuối âm tiết nơi thanh điệu "quyết định"; TTS phải tái tạo đúng cả đường F0 lẫn giọng kẹt; turn detector phải phân biệt F0 đi xuống do thanh điệu với F0 đi xuống do kết thúc lượt.

---

## 1.11 Tóm tắt một trang

- Âm thanh = dao động áp suất; file audio = chuỗi giá trị có dấu quanh 0.
- dB = log của tỉ số; 20·log10 cho biên độ, 10·log10 cho công suất; luôn hỏi "so với cái gì?". +6 dB = ×2 biên độ; nguồn không tương quan cộng công suất.
- Tiếng nói = **source** (F0 hoặc nhiễu) × **filter** (formant) × phát xạ; phổ nghiêng ~−6 dB/oct. Mel/MFCC giữ envelope (nội dung); F0 mang thanh điệu.
- Tiếng Việt: 6 thanh (Bắc), 5 (Nam, hỏi≈ngã); thanh = đường F0 + chất giọng + trường độ. Phụ âm cuối tắc, giọng kẹt và âm xát đầu có năng lượng thấp → dễ bị VAD cắt → cần `speech_pad_ms`/pre-roll.
- Năng lượng tiếng nói chủ yếu 100 Hz–4 kHz; âm xát tới 8 kHz+. NB 8 kHz (300–3400 Hz) đủ cho tai nhưng thiếu cho ASR train ở 16 kHz; upsample không khôi phục thông tin.
- Môi trường: vang (RT60, far-field), nhiễu stationary/non-stationary/babble, echo bot, Lombard. Babble và echo là khó nhất.
- SNR = 10·log10(P_s/P_n); trộn bằng α = √(P_s / (P_n·10^(SNR/10))); quy ước P_s phải nhất quán; tránh clip bằng scale cả hỗn hợp.

## 1.12 Liên kết

**Chương sau:** Chương 2 (số hoá: sample rate, Nyquist, bit depth, quy đổi ms ↔ samples ↔ bytes), Chương 4 (STFT, mel, MFCC, F0 tracking), Chương 5 (ngữ âm và chữ viết tiếng Việt), Chương 7 (AEC/noise front-end), Chương 10 (VAD và turn), Chương 21 (đánh giá).

**Tài liệu thiết kế:** [§5.1, §5.2, §10](thiet-ke-pipeline-speech-to-speech-tieng-viet.md).

**Wiki:**

- [Speech Enhancement Before ASR](../wiki/speech-enhancement-before-asr.md) — bằng chứng mâu thuẫn về denoise trước ASR, thực hành chỉ denoise nhánh VAD.
- [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md) — AEC và các tầng xử lý echo.
- [Silero VAD](../wiki/silero-vad.md) — cửa sổ 512 samples ở 16 kHz, các tham số pad/silence.
- [Whisper Large v3](../wiki/whisper-large-v3.md) — đầu vào log-mel 128 bin.
- [Turn Detection Models](../wiki/turn-detection-models.md) — độ chính xác end-of-turn tiếng Việt.

**Đọc thêm ngoài wiki (giáo trình chuẩn, gợi ý):** Stevens, *Acoustic Phonetics*; Johnson, *Acoustic and Auditory Phonetics*; Ladefoged & Johnson, *A Course in Phonetics*; Rabiner & Schafer, *Theory and Applications of Digital Speech Processing*; tài liệu Praat (praat.org); ITU-R BS.1770 (loudness), ITU-T P.56 (active speech level); các nghiên cứu ngữ âm thanh điệu tiếng Việt (ví dụ của Michaud, Brunelle, Kirby) cho mô tả F0 và chất giọng theo phương ngữ.
