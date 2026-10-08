# Chương 5. Ngữ âm, chữ viết và văn bản tiếng Việt 🔴

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần II.
> **Chương trước:** [Chương 4. DSP cho tiếng nói và đặc trưng đầu vào model](chuong-04-dsp-cho-tieng-noi-va-dac-trung-dau-vao-model.md).
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §5.2 (`speech_pad_ms` và thanh điệu), §5.4.2 (bẫy khi so sánh WER), §5.5 (chunker, normalizer, lexicon), §7.3 (backchannel), §10 (corpus giọng ba miền).
> **Cơ sở:** phần lớn là kiến thức giáo trình về ngữ âm học tiếng Việt, Unicode và xử lý văn bản cho ASR/TTS. Ngữ âm học tiếng Việt có nhiều trường phái phân tích; bảng âm vị ở đây theo cách trình bày phổ biến cho giọng Bắc chuẩn, mang tính sư phạm, không phải kết luận học thuật. Những chỗ lấy từ tài liệu thiết kế hoặc wiki được ghi rõ và giữ nhãn bằng chứng (**Reported**, **Synthesis**…). Các ví dụ Unicode, WER/CER, đặt dấu thanh và đọc số ở §5.5–§5.8 được chạy bằng script Python 3.12.3 thuần (`unicodedata`, Unicode 15.0.0) trong lúc viết (**Reproduced**). Thư viện tách từ, G2P và normalizer bên ngoài (underthesea, VnCoreNLP, pyvi, espeak-ng, NeMo text processing, vig2p) **chưa được cài hay chạy trong repo này**; hãy kiểm tra với phiên bản bạn dùng.

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Phân tích được một âm tiết tiếng Việt thành **âm đầu, âm đệm, âm chính, âm cuối, thanh**, và biết cách chữ Quốc ngữ ghi từng thành phần (kể cả các quy tắc `c/k/q`, `g/gh`, `ng/ngh`, `gi`, `qu`).
2. Giải thích được vì sao thanh điệu tiếng Việt khiến **padding VAD, ranh giới chunk TTS và cách đo lỗi** phải khác tiếng Anh.
3. Nêu được các khác biệt chính giữa giọng **Bắc, Trung, Nam** và loại lỗi ASR mà mỗi khác biệt gây ra.
4. Xử lý đúng **Unicode tiếng Việt**: NFC/NFD, dạng "tổ hợp" lai, vị trí dấu thanh kiểu cũ/mới, biến thể `i/y`, ký tự giống nhau nhưng khác mã.
5. Phân biệt **âm tiết và từ**, biết khi nào cần tách từ, và tính đúng **WER, CER, SER** trên tiếng Việt.
6. Thiết kế được **TN** (text normalization, phía TTS) và **ITN** (inverse text normalization, phía ASR) cho số, tiền, ngày giờ, đơn vị, viết tắt, số điện thoại.
7. Hiểu **G2P** tiếng Việt và vai trò của **lexicon** cho tên riêng, từ mượn, code-switch.
8. Nhận diện được các đặc điểm **hội thoại** tiếng Việt (backchannel, từ đệm, tiểu từ cuối câu, lệnh một âm tiết) và hệ quả cho VAD, turn detection, barge-in và LLM.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. Vì sao CER và WER trên tiếng Việt cho kết quả khác nhau? Một "từ" tiếng Việt là âm tiết hay từ ghép?
- Q2. Vì sao cắt mất 50 ms đầu hoặc cuối âm tiết có thể làm sai thanh?
- Q3. `ộ` dạng NFC và NFD khác nhau thế nào khi so sánh chuỗi hoặc tính WER?

---

## 5.1 Bức tranh tổng: tiếng Việt khác tiếng Anh ở đâu

Hầu hết công cụ speech (VAD, turn detector, normalizer, tokenizer, metric) được thiết kế trước hết cho tiếng Anh. Tiếng Việt khác ở năm điểm, và mỗi điểm chạm vào một tầng của pipeline:

| Đặc thù tiếng Việt | Hệ quả kỹ thuật | Tầng bị ảnh hưởng |
|---|---|---|
| **Đơn lập, đơn âm tiết:** khoảng trắng ngăn cách âm tiết, không ngăn cách từ | "WER" tiếng Việt thường thực chất là lỗi âm tiết. Tách từ là một bước riêng, có lỗi riêng | Đánh giá ASR, tokenization, NLP phía sau |
| **Thanh điệu** quyết định nghĩa, nằm trên toàn âm tiết, phần phân biệt thường ở giữa và cuối | Cắt đuôi âm tiết → sai thanh. Chunk TTS cắt giữa âm tiết → méo thanh | VAD (`speech_pad_ms`), endpoint, chunker TTS, đánh giá |
| **Chữ viết Latin nhiều dấu chồng** (tối đa 2 dấu trên một chữ cái) | Một ký tự nhìn thấy có nhiều cách mã hoá. So chuỗi "giống hệt nhau" vẫn có thể khác | Mọi biên text: ASR output, LLM, TTS input, metric, log |
| **Phương ngữ** khác cả âm đầu, vần và số thanh | Lỗi kiểu "đúng âm, sai chính tả". WER dao động mạnh theo vùng | ASR, TTS (giọng preset), corpus đánh giá |
| **Văn bản viết khác văn bản nói:** số, tiền, ngày, viết tắt, quy ước dấu chấm/phẩy ngược với tiếng Anh | Cần TN trước TTS, ITN (hoặc normalizer chung) sau ASR | Cầu text → speech, đánh giá, hiển thị |

Một nguyên tắc xuyên suốt chương: **tách "text để hiển thị" khỏi "text để đọc" và "text để so sánh"**. Ba dạng này phục vụ ba mục đích khác nhau và được chuẩn hoá theo ba bộ luật khác nhau (§5.7, §5.8).

---

## 5.2 Cấu trúc âm tiết

### 5.2.1 Mô hình năm thành phần

Âm tiết tiếng Việt có cấu trúc cố định:

```text
                     THANH ĐIỆU (phủ lên toàn âm tiết)
   ┌──────────┬───────────────────────────────────────────┐
   │ ÂM ĐẦU   │                  VẦN                      │
   │ (C1)     ├──────────┬──────────────┬─────────────────┤
   │          │ ÂM ĐỆM   │ ÂM CHÍNH     │ ÂM CUỐI         │
   │          │ (w)      │ (V, bắt buộc)│ (C2 hoặc bán âm)│
   └──────────┴──────────┴──────────────┴─────────────────┘
```

Chỉ **âm chính** và **thanh** là bắt buộc. Âm đầu có thể "rỗng" về chữ viết (thực ra là tắc thanh hầu /ʔ/, như trong "ăn", "uống").

| Âm tiết | Âm đầu | Âm đệm | Âm chính | Âm cuối | Thanh |
|---|---|---|---|---|---|
| `a` | (ʔ) | – | a | – | ngang |
| `hoàng` | h | o (/w/) | a | ng | huyền |
| `quốc` | q (/k/) | u (/w/) | uô (/uə/) | c | sắc |
| `nguyễn` | ng | u (/w/) | yê (/iə/) | n | ngã |
| `giường` | gi (/z/) | – | ươ (/ɨə/) | ng | huyền |
| `khuya` | kh | u (/w/) | ya (/iə/) | – | ngang |
| `tay` | t | – | a (/ă/, ngắn) | y (/j/) | ngang |
| `tai` | t | – | a (/a/, dài) | i (/j/) | ngang |

Hai dòng cuối là bẫy chính tả kinh điển: `tay` và `tai` khác nhau ở **độ dài nguyên âm**, nhưng chữ viết ghi bằng cách đổi chữ của âm cuối (`y` vs `i`). Tương tự `au` (ngắn, `sau`) và `ao` (dài, `sao`). Một G2P viết ngây thơ theo từng chữ cái sẽ sai ở đây.

### 5.2.2 Âm đầu

Bảng theo giọng Bắc chuẩn (khoảng 22 âm vị). Cột "Phương ngữ" cho biết chỗ các vùng khác nhau (§5.4).

| Âm vị (IPA) | Chữ viết | Ví dụ | Ghi chú / phương ngữ |
|---|---|---|---|
| /b/ | b | ba | Thường hơi ngạc hoá (implosive) |
| /m/ | m | mẹ | |
| /f/ | ph | pha | |
| /v/ | v | và | Nam thường đọc gần [j] |
| /t/ | t | tôi | |
| /tʰ/ | th | thu | Bật hơi |
| /ɗ/ | đ | đi | Implosive |
| /n/ | n | no | Một số vùng Bắc lẫn n/l |
| /l/ | l | là | |
| /z/ | d, gi | da, gia | Bắc nhập cả `r` vào đây; Nam đọc d/gi gần [j] |
| /s/ | x | xa | |
| /ʂ/ | s | sa | Bắc nhập với `x` → [s] |
| /ʐ/ ~ /r/ | r | ra | Bắc → [z]; Nam nhiều biến thể |
| /c/ | ch | cha | |
| /ʈ/ | tr | tre | Bắc nhập với `ch` |
| /ɲ/ | nh | nhà | |
| /k/ | c, k, q | ca, kê, qua | Xem quy tắc §5.2.6 |
| /x/ | kh | khi | |
| /ŋ/ | ng, ngh | nga, nghe | |
| /ɣ/ | g, gh | ga, ghe | |
| /h/ | h | hè | |
| /ʔ/ | (không viết) | ăn | |
| /p/ | p | pin, pa-tê | Chủ yếu trong từ mượn |

Điểm quan trọng cho ASR: các cặp `d/gi/r`, `s/x`, `tr/ch` là **chữ viết khác nhau nhưng âm giống nhau** trong một phương ngữ. ASR chỉ "nghe" thấy âm. Phần chọn chữ phải dựa vào ngữ cảnh (language model bên trong ASR). Đây là nguồn lỗi chính tả phổ biến nhất: `dì/gì/rì`, `sâu/xâu`, `trăng/chăng`.

### 5.2.3 Âm đệm

Âm đệm là bán nguyên âm /w/ làm tròn môi, viết bằng:

- `o` trước `a`, `ă`, `e`: `hoa`, `hoặc`, `khoe`.
- `u` trong các trường hợp còn lại: `huệ`, `thuỷ`, `uy`.
- Sau `q` luôn viết `u`: `qua`, `quê`, `quý`. Ở đây `qu` thực chất là /k/ + /w/.

Âm đệm ảnh hưởng tới **vị trí dấu thanh** (§5.5.4): trong `hoa`, `o` là âm đệm, âm chính là `a`, nên kiểu bỏ dấu "mới" là `hoà`.

### 5.2.4 Âm chính

| Âm vị | Chữ viết | Ví dụ |
|---|---|---|
| /i/ | i, y | đi, ý, kỹ/kĩ |
| /e/ | ê | kê |
| /ɛ/ | e | xe |
| /ɨ/ | ư | tư |
| /ə/ (dài) | ơ | bơ |
| /ə̆/ (ngắn) | â | tân |
| /a/ (dài) | a | ba |
| /ă/ (ngắn) | ă; và `a` trong `au`, `ay`, `anh`, `ach` | ăn, tay, sau |
| /u/ | u | thu |
| /o/ | ô | cô |
| /ɔ/ | o; `oo` trong vài từ (`xoong`, `boong`) | to, xoong |
| /iə/ | iê, yê, ia, ya | tiên, yêu, mía, khuya |
| /ɨə/ | ươ, ưa | lương, mưa |
| /uə/ | uô, ua | muốn, mua |

Ba nguyên âm đôi có **hai cách viết tuỳ có âm cuối hay không**: có âm cuối thì `iê/ươ/uô` (`tiên`, `lương`, `muốn`), không có thì `ia/ưa/ua` (`mía`, `mưa`, `mua`). Đây là lý do "mua" và "muốn" cùng nguyên âm dù chữ viết khác.

### 5.2.5 Âm cuối

| Loại | Chữ viết | Ví dụ |
|---|---|---|
| Mũi | m, n, ng, nh | làm, lan, lang, lanh |
| Tắc vô thanh | p, t, c, ch | lắp, lát, lạc, lách |
| Bán nguyên âm | u/o (/w/), i/y (/j/) | sau, sao, tai, tay |

- `nh` và `ch` chỉ đứng sau `i`, `ê`, `a` (`inh`, `ênh`, `anh`, `ích`, `ếch`, `ách`). Nhiều tác giả phân tích chúng là biến thể của /ŋ/ và /k/ sau nguyên âm hàng trước; trong giọng Bắc, `anh` được đọc gần [ăjŋ]. Hai cách phân tích này dẫn tới hai bộ phoneme khác nhau trong G2P; chọn một và giữ nhất quán giữa train và chạy.
- **Âm tiết tắc** (cuối `p/t/c/ch`) chỉ mang thanh **sắc** hoặc **nặng**, ngắn và tắt đột ngột (xem [Chương 1 §1.4.3](chuong-01-vat-ly-am-thanh-va-co-che-tao-tieng-noi.md)).

### 5.2.6 Quy tắc chính tả cần thuộc

| Âm | Viết | Điều kiện | Ví dụ |
|---|---|---|---|
| /k/ | `k` | trước `i, y, e, ê` | kí, kẻ, kê |
| /k/ | `q` | trước âm đệm /w/ (viết `qu`) | qua, quyết |
| /k/ | `c` | còn lại | ca, cô, cũng |
| /ɣ/ | `gh` | trước `i, e, ê` | ghi, ghe, ghế |
| /ŋ/ | `ngh` | trước `i, e, ê` | nghỉ, nghe, nghề |
| /z/ | `gi` | trước nguyên âm khác `i` | gia, giữ, giường |
| /z/ + /i/ | `gi` (một `i`) | khi âm chính là /i/ | gì, gìn (= gi + in) |

Hệ quả cho parser âm tiết (G2P, đặt dấu thanh, kiểm tra chính tả):

- Trong `qu` + nguyên âm, `u` là âm đệm, **không phải âm chính**: `quý` có âm chính `y`.
- Trong `gi` + nguyên âm, `i` thuộc âm đầu: `giữ` có âm chính `ư`. Nhưng trong `gì`, `i` là âm chính.
- Hai chỗ này là nguồn bug phổ biến nhất của code đặt dấu thanh và G2P tự viết.

### 5.2.7 Âm tiết là tập hữu hạn

Do cấu trúc cố định, số âm tiết viết được là hữu hạn: cỡ vài nghìn (các con số hay được nêu nằm trong khoảng 6–7 nghìn, tuỳ cách đếm và có tính âm tiết hiếm/từ mượn hay không; **Unverified**). Hệ quả:

- ASR tiếng Việt có thể dùng **từ vựng mức âm tiết** (output unit = âm tiết) mà không bị bùng nổ vocabulary. Nhiều hệ tiếng Việt thời Kaldi làm vậy.
- Kiểm tra "âm tiết có hợp lệ không" là một **gate rẻ** để phát hiện output rác (hallucination ngôn ngữ khác, mojibake, từ tiếng Anh). Không hợp lệ không có nghĩa là sai (tên riêng, từ mượn), nhưng là tín hiệu.
- Corpus TTS có thể đo **độ phủ âm tiết và độ phủ (vần × thanh)** để biết giọng nào thiếu dữ liệu ở đâu.

---

## 5.3 Hệ sáu thanh và hệ quả cho pipeline

### 5.3.1 Nhắc lại phần vật lý

Chi tiết về đường F0, chất giọng và trường độ đã có ở [Chương 1 §1.4.3](chuong-01-vat-ly-am-thanh-va-co-che-tao-tieng-noi.md); cách chúng hiện trên spectrogram ở [Chương 4, đáp án Q3](chuong-04-dsp-cho-tieng-noi-va-dac-trung-dau-vao-model.md). Tóm tắt cho giọng Bắc:

| Thanh | Dấu | Unicode (combining) | F0 | Chất giọng / độ dài | Phần phân biệt nằm ở đâu |
|---|---|---|---|---|---|
| Ngang | (không) | – | bằng, giữa-cao | modal | toàn âm tiết |
| Huyền | `` ` `` | U+0300 | thấp, xuống nhẹ | có thể hơi thở | toàn âm tiết |
| Sắc | `´` | U+0301 | đi lên | modal | nửa sau (độ dốc lên) |
| Hỏi | `̉` | U+0309 | xuống rồi lên lại | có thể kẹt ở đáy | **nửa sau** (đoạn lên lại) |
| Ngã | `~` | U+0303 | lên, đứt quãng thanh hầu | glottalized | **giữa** âm tiết |
| Nặng | `.` dưới | U+0323 | thấp, rơi nhanh | **tắc thanh hầu ở cuối**, ngắn | **cuối** âm tiết |

### 5.3.2 Hệ quả cho VAD và endpoint

- Phần phân biệt hỏi/ngã/nặng nằm ở giữa và cuối âm tiết, đúng vùng **năng lượng thấp và không tuần hoàn** (creaky). VAD có thể coi vùng này là "im lặng", và nếu không có padding thì đoạn audio gửi ASR mất đúng phần mang thanh.
- Phụ âm đầu vô thanh (`s`, `x`, `kh`, `th`, `ph`, `h`) có năng lượng thấp, phổ giống nhiễu. Thiếu pre-roll thì mất phụ âm đầu: "sáng" thành "áng", "khó" thành "ó".
- Vì vậy tài liệu thiết kế đặt `speech_pad_ms` 100–200 và nhấn mạnh rằng điều này "quan trọng với thanh điệu tiếng Việt" (§5.2, **Reported**, cần tune), cộng với pre-roll 200–300 ms ở audio ingress (§7.1). HF s2s dùng `--speech_pad_ms 500` (**Observed** trong code qua wiki). Con số đúng phải đo: chạy thực hành 6 của Chương 4 (cắt 50/100/150 ms đuôi rồi cho ASR nhận dạng).
- Câu kết thúc bằng thanh **nặng** hoặc **huyền** có F0 đi xuống giống ngữ điệu kết câu. Turn detector dựa trên prosody (Smart Turn) có thể nhầm "F0 xuống vì thanh" thành "F0 xuống vì hết lượt", hoặc ngược lại. Đây là một giả thuyết hợp lý (**Synthesis**) để giải thích vì sao tiếng Việt là ngôn ngữ yếu nhất trong benchmark của Smart Turn v3.2 (accuracy CPU int8 79.38%, **Reported**, §5.3 tài liệu thiết kế); chưa có bằng chứng nhân quả.

### 5.3.3 Hệ quả cho TTS

- **Không bao giờ cắt chunk text giữa một âm tiết.** Chunker hoạt động trên text nên tự nhiên cắt ở khoảng trắng; nhưng nếu có bước nào cắt theo số ký tự hoặc số token BPE, nó có thể cắt giữa chữ và tách dấu thanh khỏi nguyên âm (đặc biệt với text NFD).
- **Ranh giới chunk audio:** TTS streaming phát audio theo frame. Nếu bạn ghép các câu riêng lẻ, nối ở khoảng lặng giữa câu (TTS thường sinh sẵn), đừng cắt bỏ đuôi câu để "giảm độ trễ". Đuôi câu thường là thanh nặng/ngã với tắc thanh hầu, và cắt nó làm thanh nghe sai.
- **Prosody qua ranh giới chunk:** gọi TTS theo mệnh đề làm mất ngữ cảnh ngữ điệu giữa các mệnh đề. Quy tắc khởi điểm của tài liệu thiết kế (cắt ở dấu phẩy khi đã có ≥ ~25 ký tự cho chunk đầu, gộp mảnh < 8 ký tự, đơn vị 20–60 ký tự; §5.5, **Reported**) là trade-off giữa TTFA và prosody.
- **Vocoder/codec nén mạnh** có thể làm mờ giọng kẹt, khiến ngã/nặng nghe giống sắc/huyền (Chương 1 §1.4.4). Vì thế §10 tài liệu thiết kế yêu cầu chấm riêng "thanh điệu, phát âm" trong MOS/CMOS.

### 5.3.4 Đo lỗi thanh riêng

WER/CER không nói lỗi nằm ở thanh hay ở âm. Với tiếng Việt, nên đo thêm **Tone Error Rate (TER)**: căn chỉnh hai chuỗi âm tiết như khi tính WER, rồi trên các cặp âm tiết cùng "khung" (giống nhau khi bỏ thanh), đếm tỷ lệ khác thanh. Tách thanh khỏi âm tiết bằng cách phân rã NFD rồi lấy ra năm combining mark (code ở §5.5.6).

```python
>>> split_tone("người")
('ngươi', 'huyền')
>>> split_tone("khuỷu")
('khuyu', 'hỏi')
```

Ma trận nhầm lẫn thanh (6 × 6) theo phương ngữ người nói là cách nhanh nhất để thấy ASR yếu ở đâu: ví dụ nhầm hỏi ↔ ngã nhiều trên giọng Nam là đúng như dự đoán (§5.4), không hẳn là lỗi model.

---

## 5.4 Phương ngữ Bắc, Trung, Nam

### 5.4.1 Khác biệt chính

Mô tả dưới đây là khái quát giáo trình. Thực tế mỗi vùng có nhiều biến thể, giọng thành thị và nông thôn khác nhau, và người nói hay điều chỉnh giọng theo tình huống (nói chậm, đọc to, nói với máy thường "chuẩn" hơn).

| Khía cạnh | Bắc (Hà Nội) | Trung (Huế, Nghệ Tĩnh…) | Nam (Sài Gòn) |
|---|---|---|---|
| Số thanh (âm học) | 6, phân biệt hỏi/ngã | Thường ít hơn: nhiều vùng Bắc Trung Bộ nhập ngã với nặng; Huế có đường nét thanh khác hẳn | Thường 5: **hỏi và ngã nhập làm một**; nặng ít tắc thanh hầu, xuống rồi lên |
| `d / gi / r` | đều → [z] | phân biệt nhiều hơn (`r` thường giữ) | `d/gi` → [j]; `r` nhiều biến thể |
| `s / x`, `tr / ch` | nhập: [s], [c] | thường phân biệt | phân biệt trong lời nói cẩn thận, nhập trong lời nói nhanh |
| `v` | [v] | [v] | thường gần [j] |
| Âm cuối | phân biệt `n/ng`, `t/c` | khác theo vùng | `-n` và `-ng`, `-t` và `-c` nhập ở nhiều vần (`lan` ~ `lang`, `mát` ~ `mác`) |
| Vần | chuẩn chính tả | biến đổi nguyên âm nhiều | `-inh` ~ [-ɨn], `-ênh` ~ [-ən], `anh` ~ [an] |
| Âm đệm, `qu` | giữ /kw/ | | `qu` → [w] (`quá` ~ "wá"), `ho-` → [w] (`hoa` ~ "wa") |
| Từ vựng | cốc, thìa, lợn, quả, hoa | | ly, muỗng, heo, trái, bông |

### 5.4.2 Hệ quả cho ASR

- **Lỗi "đúng âm, sai chính tả":** ASR nghe giọng Bắc có thể ghi `ra` thành `da`, giọng Nam có thể ghi `lan` thành `lang`, `mã` thành `mả`. Về âm học, model không sai; nó thiếu ngữ cảnh để chọn chữ. Những lỗi này làm WER tăng nhưng thường không ảnh hưởng hiểu nghĩa khi đưa vào LLM, trừ khi rơi vào **tên riêng, số, phủ định** (critical span).
- **WER trung bình che mất chênh lệch vùng.** Một model đạt 8% trên tập chủ yếu giọng Bắc có thể 15% trên giọng Trung. Vì thế corpus của §10 tài liệu thiết kế yêu cầu Bắc/Trung/Nam riêng và báo cáo theo vùng (**Synthesis** của tài liệu thiết kế từ các gate trong wiki). Phần lớn tập công khai (VIVOS, CommonVoice, FLEURS) không cân bằng vùng và không ghi nhãn vùng đầy đủ; kiểm tra metadata trước khi dùng làm bằng chứng.
- **Từ vựng vùng miền** (`heo/lợn`, `trái/quả`) không phải lỗi ASR. Đừng đưa chúng vào normalizer đánh giá (đổi `heo` thành `lợn` sẽ che lỗi thật khi user nói `heo` mà ASR ra `lợn`).
- **Hotword và tên riêng** phát âm khác theo vùng: kiểm tra hotwords/`initial_prompt` (§5.4.4 thiết kế) trên cả ba giọng.

### 5.4.3 Hệ quả cho TTS và LLM

- **TTS:** chọn giọng preset theo vùng của người dùng mục tiêu. VieNeu v3 Turbo có preset Bắc/Trung/Nam (**Reported**, [Vietnamese Realtime TTS Selection](../wiki/vietnamese-realtime-tts-selection.md)). Giọng clone từ reference sẽ mang phương ngữ của reference; đánh giá thanh điệu theo chuẩn của phương ngữ đó, không theo giọng Bắc.
- **G2P** (nếu TTS dùng phoneme, §5.9) phải biết phương ngữ: cùng chữ `r`, giọng Bắc cần [z].
- **LLM:** câu trả lời viết theo từ vựng chuẩn Bắc ("cốc", "thìa") đọc bằng giọng Nam nghe lệch. Có thể đưa vùng vào system prompt nếu biết trước (**Synthesis**).

---

## 5.5 Chữ Quốc ngữ và Unicode

### 5.5.1 Hai lớp dấu

Chữ tiếng Việt có hai lớp dấu độc lập:

- **Dấu phụ (diacritic chữ cái)** tạo ra chữ cái mới: `ă â ê ô ơ ư đ`. Đây là phần của "khung" âm tiết.
- **Dấu thanh** (5 dấu) đặt trên hoặc dưới nguyên âm âm chính.

Một chữ cái có thể mang cả hai, ví dụ `ộ` = `o` + mũ + nặng, `ở` = `o` + móc + hỏi. Cả **144 dạng** nguyên âm tiếng Việt (12 nguyên âm × 6 thanh × hoa/thường) đều có ký tự dựng sẵn trong Unicode (**Reproduced**: NFC của cả 144 tổ hợp đều ra 1 code point). Điều quan trọng là **mỗi chữ có dấu còn có ít nhất một cách viết khác bằng ký tự tổ hợp**.

### 5.5.2 NFC và NFD

Unicode định nghĩa các dạng chuẩn tắc (normalization form):

- **NFC** (Composed): dùng ký tự dựng sẵn khi có.
- **NFD** (Decomposed): tách thành chữ cơ sở + các combining mark, sắp theo thứ tự chuẩn (canonical ordering theo combining class).

Kết quả chạy thật (**Reproduced**, Python 3.12.3, Unicode 15.0.0):

```text
NFC 1 ['U+1ED9 LATIN SMALL LETTER O WITH CIRCUMFLEX AND DOT BELOW']
NFD 3 ['U+006F LATIN SMALL LETTER O', 'U+0323 COMBINING DOT BELOW', 'U+0302 COMBINING CIRCUMFLEX ACCENT']
NFC == NFD ? False
```

Lưu ý thứ tự trong NFD: **dấu nặng (U+0323) đứng trước dấu mũ (U+0302)**, vì combining class của dấu dưới (220) nhỏ hơn dấu trên (230). Code nào giả định "dấu mũ luôn đi ngay sau chữ cái" sẽ sai.

Hệ quả:

- `"ộ" == "ộ"` có thể là `False` dù trông giống hệt. `len()` khác nhau (1 vs 3). Regex `[ộ]`, `str.find`, key dictionary, lexicon lookup, hotword match đều có thể trượt.
- Tokenizer BPE thấy hai chuỗi byte khác nhau. Model hầu như được train trên text NFC (phần lớn web tiếng Việt là NFC), nên NFD là **phân phối lạ** với nó: nhiều token hơn, và có thể đọc/sinh kém hơn (**Synthesis**, chưa đo trong repo).
- Metric: xem §5.7.2 (một câu NFD so với ref NFC cho WER 0.80 dù đúng hoàn toàn).

### 5.5.3 Text tiếng Việt ngoài đời đến từ đâu, và vì sao không phải lúc nào cũng NFC

| Nguồn | Dạng thường gặp |
|---|---|
| Web, phần lớn bộ gõ hiện đại (Unikey/EVKey chế độ "Unicode dựng sẵn"), mobile | NFC |
| macOS: tên file trên HFS+ (cũ), một số app copy/paste | NFD |
| Bộ gõ chế độ "Unicode tổ hợp" (giống Windows-1258) | **Lai:** chữ có dấu phụ dựng sẵn (`ô` U+00F4) + dấu thanh rời (U+0323). Không phải NFC, cũng không phải NFD |
| Văn bản cũ mã TCVN3 (ABC), VNI-Windows | Không phải Unicode. Đọc sai encoding sẽ ra mojibake (chuỗi ký tự Latin-1 vô nghĩa); phải chuyển mã trước |
| PDF trích xuất | Thường lẫn nhiều dạng, có thể có ký tự dấu tách rời bằng khoảng trắng |
| Output model (ASR, LLM) | Thường NFC, nhưng **không được giả định**; byte-level BPE có thể sinh bất kỳ chuỗi byte hợp lệ nào |

Dạng lai được NFC sửa đúng (**Reproduced**): `"\u00f4\u0323"` (2 code point) → NFC cho `ộ` (1 code point). Vì vậy **NFC là bước đầu tiên ở mọi biên nhận text**.

### 5.5.4 Vị trí dấu thanh: kiểu cũ và kiểu mới

NFC **không** giải quyết vấn đề này, vì `hòa` và `hoà` là hai chuỗi khác nhau về mặt chữ, không phải hai cách mã hoá của cùng chữ:

| Vần (không âm cuối) | Kiểu "cũ" (dấu trên chữ đầu) | Kiểu "mới" (dấu trên âm chính) |
|---|---|---|
| `oa` | hòa, tọa | hoà, toạ |
| `oe` | khỏe, xòe | khoẻ, xoè |
| `uy` | thúy, lũy | thuý, luỹ |

Có âm cuối thì hai kiểu trùng nhau (`hoàng`, `thuyền`, `toán`). Sau `qu`, `u` là âm đệm của âm đầu nên `quý`, `quả` không đổi. Cả hai kiểu đều đang được dùng rộng rãi trong báo chí, sách, dữ liệu train. ASR có thể ra kiểu này trong khi ref dùng kiểu kia.

Quy tắc đặt dấu thanh tổng quát (đủ dùng cho chuẩn hoá):

1. Bỏ `u` của `qu` và `i` của `gi` (khi theo sau là nguyên âm khác) khỏi cụm nguyên âm.
2. Nếu cụm có chữ mang dấu phụ (`ă â ê ô ơ ư`), dấu thanh đặt lên chữ đó (với `ươ` thì đặt lên `ơ`: `người`, `mười`).
3. Nếu cụm chỉ có một nguyên âm: đặt lên nó.
4. Nếu cụm có ba nguyên âm (`oai`, `oay`, `uyu`…): đặt lên chữ giữa (`ngoái`, `khuỷu`).
5. Nếu có âm cuối: đặt lên nguyên âm thứ hai (`hoàng`, `xoóng`).
6. Còn lại (hai nguyên âm, không âm cuối): với `oa/oe/uy` thì kiểu mới đặt lên chữ thứ hai, kiểu cũ lên chữ thứ nhất; các cụm khác (`ai, ao, au, ay, eo, ia, iu, oi, ua, ui, ưa, ưu`…) đặt lên chữ thứ nhất (`mía`, `múa`, `mứa`).

Kết quả của code §5.5.6 trên các ca khó (**Reproduced**):

```text
hòa     → new: hoà    old: hòa
khỏe    → new: khoẻ   old: khỏe
thúy    → new: thuý   old: thúy
quý     → new: quý    old: quý      (qu: u là âm đệm)
giữ     → new: giữ    old: giữ      (gi: i thuộc âm đầu)
gì      → new: gì     old: gì       (i là âm chính)
người   → new: người  old: người    (ươ → ơ)
khuỷu   → new: khuỷu  old: khuỷu    (3 nguyên âm → giữa)
ngoái   → new: ngoái  old: ngoái
xoóng   → new: xoóng  old: xoóng    (có âm cuối)
gịa     → new: giạ    old: giạ      (sửa dấu đặt sai chỗ)
```

Chọn **một** kiểu cho toàn hệ thống (khuyến nghị: kiểu nào trùng với dữ liệu ref của bạn) và áp dụng cho cả ref lẫn hyp khi đánh giá.

### 5.5.5 Các biến thể khác Unicode không sửa

| Vấn đề | Ví dụ | Cách xử lý |
|---|---|---|
| Biến thể `i/y` | `kỹ/kĩ`, `lý/lí`, `mỹ/mĩ`, `quý` (không đổi) | Danh sách ánh xạ theo từ, chỉ dùng trong **normalizer đánh giá**; không tự đổi text hiển thị |
| Chữ giống nhau khác mã | `ð` (U+00F0, eth Iceland) / `Ð` (U+00D0) thay cho `đ` (U+0111) / `Đ` (U+0110) | NFC **không** sửa (**Reproduced**: `NFC("ð") != "đ"`). Thêm bảng thay thế riêng |
| Combining mark khác mã | U+0340/U+0341 (dấu thanh "cũ") | NFC sửa thành U+0300/U+0301 |
| Ký tự vô hình | zero-width space U+200B, BOM U+FEFF, soft hyphen U+00AD, NBSP U+00A0 | Xoá hoặc đổi thành khoảng trắng thường |
| Dấu câu "thông minh" | `“ ” ‘ ’ – —` | Đổi về ASCII trong text so sánh; giữ trong text hiển thị |
| Hoa/thường | `Hà Nội` / `hà nội` | Lowercase trong text so sánh (Python `str.lower()` xử lý đúng chữ có dấu) |

### 5.5.6 Code tham khảo

Script dưới đây là bản đã chạy để tạo các kết quả **Reproduced** trong chương. Chỉ dùng thư viện chuẩn. Viết cho chữ thường; normalizer gọi `lower()` trước.

```python
import unicodedata as ud, re

TONE_MARKS = {"\u0300": "huyền", "\u0301": "sắc", "\u0309": "hỏi",
              "\u0303": "ngã", "\u0323": "nặng"}
MARK_OF = {v: k for k, v in TONE_MARKS.items()}
VOWELS = set("aăâeêioôơuưy")
MODIFIED = set("ăâêôơư")

def split_tone(syl: str):
    """Trả (âm tiết không thanh, tên thanh). Giữ nguyên dấu mũ/móc/trăng."""
    d = ud.normalize("NFD", syl)
    tone, out = "ngang", []
    for ch in d:
        if ch in TONE_MARKS:
            tone = TONE_MARKS[ch]
        else:
            out.append(ch)
    return ud.normalize("NFC", "".join(out)), tone

def _nucleus_span(base: str):
    low = base.lower()
    i = 0
    while i < len(low) and low[i] not in VOWELS:
        i += 1
    j = i
    while j < len(low) and low[j] in VOWELS:
        j += 1
    if i >= len(low):
        return None
    onset = low[:i]
    if onset == "q" and low[i] == "u" and j - i > 1:   # qu: u là âm đệm
        i += 1
    if onset == "g" and low[i] == "i" and j - i > 1:   # gi + nguyên âm: i thuộc âm đầu
        i += 1
    return i, j

def place_tone(syl: str, style: str = "new") -> str:
    base, tone = split_tone(syl)
    if tone == "ngang":
        return ud.normalize("NFC", syl)
    span = _nucleus_span(base)
    if span is None:
        return ud.normalize("NFC", syl)
    i, j = span
    v = base[i:j].lower()
    has_coda = j < len(base)
    mods = [k for k, c in enumerate(v) if c in MODIFIED]
    if mods:
        pos = mods[-1]                       # ươ -> ơ, uyê -> ê
    elif len(v) == 1:
        pos = 0
    elif len(v) == 3:
        pos = 1                              # oai, oay, uyu
    elif has_coda:
        pos = 1                              # oan, oong
    elif v in ("oa", "oe", "uy"):
        pos = 1 if style == "new" else 0     # hoà/hòa, khoẻ/khỏe, thuý/thúy
    else:
        pos = 0                              # ai, ao, ia, ua, ưa, ui...
    k = i + pos
    return ud.normalize("NFC", base[:k+1] + MARK_OF[tone] + base[k+1:])

def norm_for_wer(text: str, tone_style: str = "new") -> str:
    t = ud.normalize("NFC", text).lower()
    t = t.replace("\u00f0", "đ")             # eth nhầm thành đ
    t = re.sub(r"[^\w\s]", " ", t)            # bỏ dấu câu
    return " ".join(place_tone(w, tone_style) for w in t.split())
```

Giới hạn đã biết: chưa xử lý chữ hoa trong `place_tone`, không kiểm tra âm tiết có hợp lệ không, và không đụng tới biến thể `i/y` hay số (để normalizer số ở §5.8 lo).

---

## 5.6 Âm tiết, từ và tokenization

### 5.6.1 Âm tiết không phải từ

Trong tiếng Việt, khoảng trắng ngăn cách **âm tiết** (tiếng), không ngăn cách **từ**. Phần lớn từ có hai âm tiết trở lên:

```text
âm tiết:  học | sinh | trường | đại | học | bách | khoa
từ:       học_sinh | trường | đại_học | bách_khoa
```

Tách từ (word segmentation) có nhập nhằng thật:

```text
"học sinh học sinh học"  →  học_sinh | học | sinh_học
"ông già đi nhanh quá"   →  ông_già | đi | nhanh | quá     (hoặc: ông | già_đi | ...)
```

### 5.6.2 Công cụ tách từ

Các công cụ phổ biến (kiến thức chung, **chưa chạy trong repo này**): VnCoreNLP (RDRSegmenter, Java), underthesea (Python), pyvi (Python, CRF). Output quy ước nối âm tiết của một từ bằng `_` (`học_sinh`). Một số model NLP tiếng Việt (ví dụ PhoBERT) **yêu cầu** input đã tách từ theo đúng bộ tách lúc train; các LLM đa ngữ và các ASR/TTS thì **không** dùng tách từ.

Trong pipeline speech-to-speech, bạn gần như **không cần tách từ** ở đường chính: ASR ra chuỗi âm tiết, LLM nhận chuỗi đó, TTS nhận text thường. Tách từ chỉ xuất hiện khi:

- Tính **word-level WER** để so với paper dùng giao thức đó.
- Chạy NLP phía sau (NER, intent classifier) yêu cầu input tách từ.
- Chunker muốn tránh cắt giữa từ ghép (hiếm khi cần, vì chunker cắt ở dấu câu).

### 5.6.3 Tokenization trong model

| Model | Đơn vị | Ghi chú tiếng Việt |
|---|---|---|
| ASR CTC/RNNT kiểu cũ | ký tự hoặc âm tiết | Vocab âm tiết vài nghìn đơn vị là khả thi (§5.2.7) |
| ASR hiện đại (Conformer + SentencePiece, Whisper byte-level BPE) | subword | Một âm tiết có dấu có thể thành 1–3 token tuỳ tokenizer |
| LLM đa ngữ | byte-level BPE | Tokenizer thiên tiếng Anh tốn nhiều token cho tiếng Việt hơn cho cùng lượng nội dung |
| TTS | ký tự, phoneme hoặc BPE của LLM nền | Xem §5.9.4 |

Hệ quả (**Synthesis**, chưa đo trong repo): số token cho mỗi giây lời nói tiếng Việt quyết định chi phí và độ trễ decode của ASR dạng attention (Whisper) và tốc độ sinh text của LLM. Khi so model, đếm token thật trên câu tiếng Việt bằng tokenizer của chính model đó; đừng dùng "1 token ≈ 0.75 từ" của tiếng Anh. NFD làm số token tăng thêm (§5.5.2).

### 5.6.4 WER, CER và SER trên tiếng Việt

- **WER** (word error rate) = (S + D + I) / N trên đơn vị "từ". Hầu hết paper và benchmark ASR tiếng Việt tách theo **khoảng trắng**, nên WER tiếng Việt **thực chất là lỗi âm tiết**. Có người gọi rõ là **SER** (syllable error rate). Trong giao thức đầy đủ, ghi rõ đơn vị.
- **WER theo từ thật** (sau tách từ): mỗi từ hai âm tiết sai một âm tiết tính là một lỗi trên một đơn vị lớn hơn, nên tỷ lệ thường **cao hơn** SER, và còn phụ thuộc vào bộ tách từ.
- **CER** (character error rate): tính trên ký tự, thường bỏ khoảng trắng. Một lỗi thanh trong âm tiết dài bị "pha loãng" trên nhiều ký tự.

Ví dụ (**Reproduced**, edit distance Levenshtein, NFC):

```text
ref: "học sinh đi học"   hyp: "học xinh đi học"
  SER (khoảng trắng)            = 1/4 = 0.25
  WER theo từ ("học_sinh"...)   = 1/3 = 0.33

ref: "hôm nay trời đẹp quá"   hyp: "hôm nay trời đep quá"   (mất dấu nặng)
  WER = 0.20,  CER = 0.062    (1 ký tự sai trên 16)
ref: "hôm nay trời đẹp quá"   hyp: "hôm nay chời đẹp quá"   (tr → ch)
  WER = 0.20,  CER = 0.125    (2 ký tự sai)
```

Cùng một âm tiết sai, WER không phân biệt "sai thanh" và "sai cả âm đầu"; CER thì có. Trên tiếng Việt, **CER luôn thấp hơn WER nhiều** và hai con số không quy đổi được cho nhau. Báo cả hai, và báo thêm TER (§5.3.4) và exact accuracy của critical span.

---

## 5.7 Chuẩn hoá cho đánh giá: tránh bẫy so sánh WER

### 5.7.1 Bẫy

Tài liệu thiết kế §5.4.2 đã liệt kê (**Reported/Synthesis**): đừng so VIVOS với FLEURS vì khác tập **và khác normalizer**; đừng đặt Qwen FLEURS 5.55 cạnh Nemotron 12.29 vì khác giao thức. Wiki [Vietnamese Realtime ASR Selection](../wiki/vietnamese-realtime-asr-selection.md) nói thêm: phải dùng "cùng ground truth/normalizer Unicode, dấu, số, punctuation", và "tránh normalizer che mất critical errors" (**Synthesis**).

Chênh lệch normalizer một mình có thể lớn hơn chênh lệch giữa hai model. Ví dụ đúng y nội dung nhưng khác dạng (**Reproduced**):

| hyp so với ref `"hôm nay trời đẹp quá"` | WER thô | CER thô | WER sau `norm_for_wer` |
|---|---|---|---|
| giống hệt (NFC) | 0.00 | 0.000 | 0.00 |
| `"hôm nay trời đẹp qúa"` (dấu đặt sai chỗ) | 0.20 | 0.125 | 0.00 |
| cùng câu nhưng **NFD** | **0.80** | 0.562 | 0.00 |
| `"tôi muốn đặt 1 bàn cho 4 người"` so với ref viết chữ "một", "bốn" | 0.25 | 0.222 | (cần normalizer số) |

### 5.7.2 Bộ chuẩn hoá đề xuất cho đánh giá

Áp dụng **giống hệt** cho ref và hyp, theo thứ tự:

1. NFC.
2. Thay ký tự giống nhau khác mã (`ð` → `đ`), xoá ký tự vô hình.
3. Lowercase.
4. Bỏ dấu câu (giữ dấu chấm/phẩy **bên trong số** cho tới bước 6).
5. Chuẩn hoá vị trí dấu thanh về một kiểu (§5.5.4).
6. Chuẩn hoá số: **đưa cả hai về dạng chữ đọc** (dùng TN ở §5.8) hoặc cả hai về dạng chữ số (dùng ITN). Dạng chữ đọc an toàn hơn, vì "1 bàn" và "một bàn" khớp nhau mà không cần ITN đoán.
7. (Tuỳ chọn, báo cáo riêng) biến thể `i/y`, từ vựng tiếng Anh có nhiều cách viết (`email/e-mail/i-meo`).

**Không** làm trong normalizer đánh giá:

- Bỏ dấu thanh (trừ khi bạn đang cố ý đo "WER không dấu" như một chỉ số phụ). Bỏ dấu sẽ che đúng loại lỗi quan trọng nhất của tiếng Việt.
- Đổi từ vựng vùng miền (`heo` → `lợn`).
- Xoá từ đệm ("ờ", "à") **ở cả hai phía** nếu ground truth có ghi; nếu ground truth không ghi thì phải biết rõ policy của bộ dữ liệu.

### 5.7.3 Critical span

WER trung bình không đủ cho voice agent. Đo **exact accuracy** trên các span gắn nhãn: số (tiền, số điện thoại, ngày giờ, số lượng), tên riêng, địa chỉ, **phủ định** ("không", "chưa", "chẳng", "đừng"). Một lỗi "có" ↔ "không" chỉ là 1 âm tiết trong WER nhưng đảo nghĩa câu. Tài liệu thiết kế §5.4.3 yêu cầu: khi mơ hồ ở số, tên riêng hay phủ định thì hỏi lại user.

---

## 5.8 Văn bản viết và văn bản nói: TN và ITN

### 5.8.1 Hai chiều

```text
                 TN (text normalization)
"1.250.000đ"  ─────────────────────────────▶  "một triệu hai trăm năm mươi nghìn đồng"
 (text viết, LLM ra)                            (text đọc, TTS nhận)

"một triệu hai trăm năm mươi nghìn đồng"  ──▶  "1.250.000 đ"
 (ASR ra dạng nói)            ITN (inverse TN)   (hiển thị, trích xuất entity)
```

Vị trí trong pipeline:

```text
mic → VAD → ASR ──(ITN tuỳ chọn, cho UI/entity)──▶ LLM ──▶ chunker ──▶ TN + lexicon ──▶ TTS
                     └─ text gốc ASR giữ lại cho log/đánh giá
```

- **TN là bắt buộc** cho TTS, trừ khi TTS tự có frontend tiếng Việt đã kiểm chứng. Tài liệu thiết kế §5.5 ghi rõ: wiki **chưa chọn được thư viện Vietnamese normalizer nào đã kiểm chứng**.
- **ITN thường không bắt buộc cho LLM** (LLM hiểu "hai trăm nghìn"), nhưng cần cho hiển thị caption, cho trích xuất entity bằng regex, và cho đánh giá nếu ref viết bằng chữ số. Whisper và các model train trên phụ đề thường tự ra chữ số; model train trên transcript dạng nói có thể ra chữ. Kiểm tra từng model.
- **Tách text hiển thị khỏi text đọc** (§5.5 thiết kế): UI hiện `1.250.000đ`, TTS đọc dạng chữ. Lưu cả hai, vì history hội thoại nên lưu phần đã phát (§7.3 thiết kế) ở dạng hiển thị.

### 5.8.2 Các lớp cần chuẩn hoá (semiotic class)

| Lớp | Ví dụ viết | Đọc | Bẫy |
|---|---|---|---|
| Số đếm | `2024` | hai nghìn không trăm hai mươi tư | Quy tắc mốt/tư/lăm/linh (§5.8.3) |
| Số thứ tự | `thứ 2`, `hạng 1` | thứ hai, hạng nhất | `thứ 1` → "thứ nhất"; `thứ 4` → "thứ tư"; `thứ 2` trong ngữ cảnh ngày là thứ Hai |
| Thập phân | `3,5` | ba phẩy năm | Tiếng Việt dùng **phẩy** cho thập phân, **chấm** cho nghìn: ngược tiếng Anh |
| Tiền | `1.250.000đ`, `50k`, `2tr`, `$10`, `10 USD` | ... đồng, năm mươi nghìn, hai triệu, mười đô (la) | `k`, `tr`, `củ`, `lít` là tiếng lóng; `$` đứng trước |
| Phần trăm | `15%` | mười lăm phần trăm | `0,5%` |
| Đơn vị | `km/h`, `5kg`, `30°C` | ki-lô-mét trên giờ, năm ki-lô-gam, ba mươi độ C | `m` là mét hay phút? `ph` = phút |
| Ngày | `1/5`, `01/05/2025`, `ngày 1-5` | mùng một tháng năm | `1/5` có thể là phân số; ngày 1–10 thường đọc "mùng"; `tháng 4` → "tháng tư"; âm lịch: tháng giêng, tháng chạp |
| Giờ | `14h30`, `14:30`, `2h chiều` | mười bốn giờ ba mươi (phút) | `2h` có thể là "hai giờ" hoặc "hai tiếng" (thời lượng) |
| Số điện thoại | `0912 345 678` | không chín một hai, ba bốn năm, sáu bảy tám | Đọc từng chữ số, nhóm theo cách viết (§5.5 thiết kế) |
| Mã, ID, biển số | `30A-123.45`, `ĐH123` | đọc từng ký tự/nhóm | Không được đọc như số đếm |
| Số La Mã | `thế kỷ XXI`, `Chương V` | thế kỷ hai mươi mốt | `V` có thể là chữ cái |
| Viết tắt | `TP.HCM`, `UBND`, `ĐH`, `v.v.`, `PGS.TS` | thành phố Hồ Chí Minh, uỷ ban nhân dân, đại học, vân vân, phó giáo sư tiến sĩ | Có viết tắt **đọc thành chữ** (UBND) và viết tắt **đánh vần** (VTV, USB) |
| Ký hiệu | `&`, `+`, `/`, `-` | và, cộng, trên/hoặc, (nối) | `-` là gạch nối, dấu trừ hay khoảng (`5-7 ngày` → năm đến bảy ngày)? |
| URL, email | `abc@xyz.vn` | a bê xê a còng... | Tốt nhất: system prompt LLM không xuất URL (§5.5 thiết kế) |

### 5.8.3 Quy tắc đọc số tiếng Việt

| Hiện tượng | Quy tắc | Ví dụ |
|---|---|---|
| 10 vs hàng chục | `mười` cho 10–19; `mươi` cho 20–90 | 15 = mười lăm; 50 = năm mươi |
| `một` → `mốt` | hàng đơn vị 1 sau `mươi` | 21 = hai mươi mốt; nhưng 11 = mười một |
| `bốn` → `tư` | hàng đơn vị 4 sau `mươi` (phổ biến, không bắt buộc) | 24 = hai mươi tư; 14 = mười bốn |
| `năm` → `lăm` (`nhăm`) | hàng đơn vị 5 sau `mười`/`mươi` | 15 = mười lăm; 25 = hai mươi lăm (nhăm) |
| Hàng chục bằng 0 | `linh` (Bắc) / `lẻ` (Nam) | 105 = một trăm linh năm / lẻ năm |
| Nhóm sau có hàng trăm bằng 0 | đọc `không trăm` | 1.005 = một nghìn không trăm linh năm |
| Nghìn | `nghìn` (Bắc) / `ngàn` (Nam) | |
| Đơn vị lớn | nghìn, triệu, tỷ; nghìn tỷ | 10^12 = một nghìn tỷ |
| Nói tắt | `hai mốt` (21), `ba lăm` (35), `hai trăm rưỡi` (250), `một nghìn hai` (1.200) | Phổ biến trong hội thoại, **ASR sẽ gặp**, ITN phải hiểu |

Code (rút gọn, đọc tới < 10^12):

```python
DIG = "không một hai ba bốn năm sáu bảy tám chín".split()

def read_lt1000(n, full, north=True):
    h, t, u = n // 100, n // 10 % 10, n % 10
    out = []
    if full or h:
        out += [DIG[h], "trăm"]
    if t == 0:
        if u and out:
            out.append("linh" if north else "lẻ")
        if u:
            out.append(DIG[u])
        return out
    out += ["mười"] if t == 1 else [DIG[t], "mươi"]
    if u == 1 and t > 1:   out.append("mốt")
    elif u == 5:           out.append("lăm")
    elif u == 4 and t > 1: out.append("tư")
    elif u:                out.append(DIG[u])
    return out

def read_int(n, north=True):
    if n == 0:
        return "không"
    units = ["", "nghìn" if north else "ngàn", "triệu", "tỷ"]
    groups = []
    while n:
        groups.append(n % 1000); n //= 1000
    out, started = [], False
    for idx in range(len(groups) - 1, -1, -1):
        g, unit = groups[idx], units[idx]
        if g == 0:
            continue
        out += read_lt1000(g, full=started, north=north)
        if unit:
            out.append(unit)
        started = True
    return " ".join(out)
```

Kết quả (**Reproduced**):

```text
21        hai mươi mốt
24        hai mươi tư
101       một trăm linh một            | một trăm lẻ một (Nam)
115       một trăm mười lăm
1005      một nghìn không trăm linh năm
2024      hai nghìn không trăm hai mươi tư
30500     ba mươi nghìn năm trăm
1250000   một triệu hai trăm năm mươi nghìn
1000005   một triệu không trăm linh năm
1001001   một triệu không trăm linh một nghìn không trăm linh một
```

Giới hạn: nhóm 0 ở giữa bị bỏ qua (`1.000.005` không đọc "không nghìn"), là cách nói phổ biến nhưng không phải cách duy nhất; chưa xử lý số âm, thập phân, số rất lớn.

### 5.8.4 Dấu chấm, dấu phẩy và LLM

LLM đa ngữ thường sinh số kiểu tiếng Anh (`1,250,000`, `3.5`) ngay cả khi trả lời tiếng Việt. `1.250` có thể là "một nghìn hai trăm năm mươi" (kiểu Việt) hoặc "một phẩy hai lăm" (kiểu Anh). Ba lớp phòng vệ (**Synthesis**):

1. System prompt yêu cầu viết số theo quy ước Việt, hoặc **viết số bằng chữ** cho câu trả lời giọng nói (đơn giản nhất cho TTS, nhưng làm text hiển thị dài).
2. Heuristic: nhóm 3 chữ số sau dấu phân cách lặp lại (`1.250.000`) chắc chắn là phân cách nghìn; `3.5` (một chữ số sau dấu chấm) nhiều khả năng là thập phân kiểu Anh.
3. Regression test với các ca mơ hồ, chấm bằng tai.

### 5.8.5 Viết tắt và đánh vần

Hai loại viết tắt:

- **Đọc thành cụm từ đầy đủ:** `UBND` → "uỷ ban nhân dân", `TP.HCM` → "thành phố Hồ Chí Minh", `GS` → "giáo sư". Cần từ điển; nhiều viết tắt mơ hồ theo domain (`BS`: bác sĩ hay biển số?).
- **Đánh vần:** `VTV`, `USB`, `ATM`. Có hai kiểu đánh vần: theo tên chữ cái tiếng Việt và theo tiếng Anh (`USB` → "u ét bê" hoặc "iu ét bi"). Người Việt thường dùng kiểu tiếng Anh cho thuật ngữ công nghệ và kiểu Việt cho tên cơ quan (`VTV` → "vê tê vê"). Đây là quyết định lexicon, không có quy tắc chung.

Tên chữ cái tiếng Việt thường dùng: a, bê, xê, dê, đê, e, ép (f), giê, hát, i, gi (j), ca, e-lờ, em-mờ, en-nờ, o, pê, quy, e-rờ, ét-xì, tê, u, vê, vê kép (w), ích-xì, i dài / i-cờ-rét (y), dét (z). Biến thể theo vùng và thế hệ rất nhiều; chốt bảng cho sản phẩm và kiểm tra bằng tai.

### 5.8.6 Thiết kế normalizer

- **Kiến trúc thực dụng:** pipeline luật có thứ tự (regex + hàm đọc), chạy theo thứ tự cụ thể → chung: URL/email → mã/ID → ngày giờ → tiền → đơn vị → phần trăm → số điện thoại → số thập phân → số đếm → viết tắt → ký hiệu. Sai thứ tự sẽ có lỗi kiểu `14h30` bị đọc thành "mười bốn h ba mươi".
- **WFST** (kiểu NeMo text processing, Kestrel/Sparrowhawk) là cách công nghiệp làm TN/ITN có cấu trúc. Có ngữ pháp tiếng Việt cho ITN trong một số bộ công cụ mã nguồn mở, nhưng mức độ hoàn thiện cần kiểm tra (**Unverified**).
- **Dùng LLM để normalize:** linh hoạt với ngữ cảnh mơ hồ, nhưng thêm độ trễ và có thể "sửa" nội dung (đổi số!). Nếu dùng, đặt sau luật, chỉ cho các span mà luật không xử lý được, và kiểm tra số trong output khớp số trong input.
- **Streaming:** normalizer chạy trên chunk của chunker. Không được cắt giữa một giá trị còn đang được sinh (`1.250.` chưa xong). Wiki TTS selection nhấn mạnh "không cắt giữa một giá trị còn đang hoàn thành" (**Synthesis**, [Vietnamese Realtime TTS Selection](../wiki/vietnamese-realtime-tts-selection.md)). Cách làm: chunker giữ lại token cuối nếu nó trông như số/viết tắt chưa kết thúc.
- **Bộ regression:** mỗi lớp ở §5.8.2 có ít nhất 5 ca, gồm các ca mơ hồ. Lưu cả raw text và normalized spoken text (wiki TTS selection, **Synthesis**). Chạy mỗi lần đổi luật.

---

## 5.9 G2P và lexicon

### 5.9.1 G2P tiếng Việt: gần như quy tắc, theo từng âm tiết

Chữ Quốc ngữ được thiết kế gần với âm, nên G2P tiếng Việt chủ yếu là **phân tích âm tiết** (§5.2) rồi tra bảng:

```text
"nguyễn"  →  âm đầu ng /ŋ/ | đệm u /w/ | chính yê /iə/ | cuối n /n/ | thanh ngã
          →  /ŋ w iə n/ + T4   (ký hiệu thanh tuỳ bộ phoneme)
"giường"  →  gi /z/ (Bắc) hoặc /j/ (Nam) | ươ /ɨə/ | ng /ŋ/ | huyền
"tay"     →  t | a /ă/ | y /j/ | ngang     (không phải /a/ dài như "tai")
```

Các điểm phải xử lý đúng: `qu`, `gi` (§5.2.6), `a` ngắn trong `au/ay/anh/ach`, nguyên âm đôi viết hai kiểu (§5.2.4), `nh/ch` cuối, `oo` (xoong), và **tham số phương ngữ** (§5.4).

Công cụ (kiến thức chung, **chưa chạy trong repo**): espeak-ng có giọng `vi` và các biến thể vùng; một số thư viện Python chuyển chữ Việt sang IPA. Kokoro Vietnamese dùng `vig2p`, được mô tả là khớp với code inference và training (**Reported**, [Kokoro Vietnamese](../wiki/kokoro-vietnamese.md)); bộ phoneme của vig2p chưa được kiểm tra trong wiki.

### 5.9.2 Ngoại lệ: nơi G2P quy tắc thất bại

| Loại | Ví dụ | Vấn đề |
|---|---|---|
| Từ mượn đã Việt hoá | `pin`, `ga`, `xăng`, `cà phê` | Thường ổn, vì đã viết theo âm Việt |
| Từ tiếng Anh giữ nguyên | `email`, `meeting`, `deadline`, `Facebook` | Không phải âm tiết Việt hợp lệ; G2P Việt đọc từng chữ cái hoặc đọc sai |
| Tên riêng nước ngoài | `Nguyễn Văn John`, `Shopee`, `Samsung` | Như trên |
| Địa danh dân tộc thiểu số | `Đắk Lắk`, `Krông Pắc`, `Ea H'leo`, `Kon Tum` | Cụm phụ âm, dấu nháy, âm cuối `k` không có trong chính tả chuẩn |
| Viết tắt | `UBND`, `VTV` | Thuộc TN (§5.8.5), phải xử lý trước G2P |
| Từ cũ / Hán Việt đặc biệt | (hiếm) | Hầu như không có, khác tiếng Anh hay tiếng Trung |

Từ đồng tự khác âm (homograph) rất hiếm trong tiếng Việt, khác hẳn tiếng Anh (`read`, `live`). Đây là ưu điểm lớn: phần lớn lỗi phát âm TTS tiếng Việt đến từ **ngoại lệ ở bảng trên** và từ **lỗi model**, không phải từ nhập nhằng ngữ cảnh.

### 5.9.3 Lexicon

Lexicon là bảng thay thế ưu tiên cao cho từ đặc biệt. Hai kiểu:

- **Respelling** (viết lại theo chính tả Việt): `email` → `i-meo`, `Shopee` → `sóp-pi`. Dùng được với mọi TTS nhận text. Đơn giản, kiểm tra được bằng tai.
- **Phoneme override:** gán thẳng chuỗi phoneme. Chỉ dùng được với TTS nhận phoneme (§5.9.4) và cần biết bộ phoneme của model.

Thiết kế:

- Khớp **sau NFC, không phân biệt hoa thường, theo ranh giới âm tiết/từ** (đừng thay `pin` bên trong `Pinterest`).
- Thứ tự: TN (viết tắt, số) → lexicon → G2P/TTS. Lexicon có thể chứa cả viết tắt domain (`KH` → "khách hàng" trong domain CSKH).
- Version hoá lexicon cùng normalizer; mỗi mục có ca test.
- Tài liệu thiết kế §5.5: VieNeu v3 Turbo được báo đọc `chánh` thành `tránh` (issue #207, chưa reproduce, **Reported/Unverified**) và đề xuất substitution dictionary cho tên riêng và thuật ngữ domain. Lưu ý: nếu lỗi nằm ở model (đọc sai một âm tiết tiếng Việt hợp lệ), respelling chỉ né được bằng cách tìm một chuỗi khác cho ra âm đúng; có khi không có.

### 5.9.4 TTS nhận gì?

| Kiểu frontend | Ví dụ | Hệ quả |
|---|---|---|
| Phoneme (qua G2P ngoài) | Kokoro Vietnamese dùng `vig2p` (**Reported**) | Lỗi G2P = lỗi phát âm; lexicon phoneme kiểm soát chính xác; phải dùng **đúng** G2P như lúc train |
| Grapheme (ký tự/BPE trực tiếp) | Nhiều TTS dựa trên LLM hoặc codec | Model tự học G2P; lexicon chỉ bằng respelling; NFC càng quan trọng |

Trước khi tích hợp một TTS, xác định nó thuộc kiểu nào bằng code hoặc tài liệu của chính model, đừng đoán.

---

## 5.10 Code-switch, tên riêng, từ mượn

Lời nói tiếng Việt thực tế, nhất là ở môi trường văn phòng và công nghệ, chen nhiều từ tiếng Anh: "gửi email", "họp online", "check lại deadline", "app bị lỗi".

**Phía ASR:**

- Output cùng một từ có thể ở nhiều dạng: `email`, `e-mail`, `i-meo`, `i meo`. Ground truth phải có quy ước, và đánh giá nên có danh sách dạng chấp nhận được (§5.7.2 bước 7).
- Model đa ngữ (Whisper, Qwen3-ASR) có thể nhảy sang ghi cả câu bằng tiếng Anh hoặc dịch, nhất là khi không ép `language="vi"` (§5.4.4 thiết kế). Cohere Transcribe được ghi là code-switch không ổn định (**Reported**, wiki ASR selection).
- Tên riêng: dùng hotwords/`initial_prompt` ngắn (§5.4.4 thiết kế); với model streaming, xem có hỗ trợ context biasing không.
- Corpus đánh giá §10 thiết kế có mục code-switch riêng.

**Phía TTS:**

- VieNeu v3 Turbo được báo xử lý được code-switch (**Reported**, §5.5 thiết kế), VieNeu Nano yếu hơn ở English/code-switch (**Reported**, wiki TTS selection). Nếu TTS không xử lý được: phiên âm qua lexicon (§5.9.3).
- Một câu trộn hai ngôn ngữ thường bị đọc với ngữ điệu "gãy" ở chỗ chuyển. Đưa ca này vào bộ 150–300 prompts.

**Phía LLM:** có thể yêu cầu trong system prompt dùng từ thuần Việt khi có từ tương đương phổ biến, để giảm rủi ro TTS (**Synthesis**). Không nên ép quá mức: "email" tự nhiên hơn "thư điện tử" trong hội thoại.

---

## 5.11 Đặc điểm hội thoại tiếng Việt

### 5.11.1 Backchannel và từ đệm

| Loại | Ví dụ | Vai trò |
|---|---|---|
| Backchannel đồng ý/đang nghe | ừ, ờ, ừm, vâng, dạ, ạ, ok, ừ hử, đúng rồi | Báo "đang nghe", không xin lượt |
| Backchannel phản ứng | thế à, thật à, ồ, hả | Có thể là câu hỏi thật |
| Từ đệm (filler) | ờ, à, ừm, kiểu, kiểu như, thì, cái, là, nói chung là | Giữ lượt khi đang nghĩ |
| Tiểu từ cuối câu | nhé, nhỉ, ạ, à, hả, chứ, đấy, mà, cơ | Thường báo **kết thúc** câu (và lượt) |
| Liên từ treo | thì..., là..., mà..., nhưng mà..., với lại... | Thường báo **chưa xong** |
| Lệnh ngắn | không, dừng, thôi, rồi, được, có | Một âm tiết, **mang nghĩa đầy đủ** |

### 5.11.2 Hệ quả cho turn-taking và barge-in

- **Backchannel trong lúc bot nói:** "ừ", "vâng" của user không nên làm bot dừng trong đa số trường hợp. Nhưng tài liệu thiết kế §7.3 cảnh báo: "đừng mặc định coi mọi ừ/vâng/ok là backchannel để bỏ qua. Trong một số domain, đó chính là lời xác nhận" (**Synthesis**). Quyết định phụ thuộc trạng thái hội thoại: bot vừa hỏi "anh xác nhận đặt lịch không?" thì "vâng" là câu trả lời.
- **Lệnh một âm tiết** như "không", "dừng" dài khoảng 200–400 ms. Các gate độ dài có thể nuốt mất: `min_speech_duration_ms` 250 (§5.2 thiết kế), `min_speech_ms=384` của HF s2s (**Synthesis** của tài liệu thiết kế: có thể không thành lượt, cần thử), luật "turn < 2 từ khi VAD < 400 ms" trong bộ lọc hallucination Whisper (§5.4.4). Đây là xung đột thật giữa chống hallucination/ngắt nhầm và nghe lệnh ngắn; phải tune trên dữ liệu thật với test case "không", "dừng" (§10 thiết kế).
- **Ngắt quãng giữa câu:** người nói tiếng Việt hay dừng sau "thì", "là" để nghĩ ("cho em hỏi là... cái đơn hàng hôm qua ấy"). Timeout im lặng ngắn sẽ cắt lượt ở đây. Tiểu từ cuối/liên từ treo là tín hiệu ngôn ngữ hữu ích cho endpoint dựa trên text (partial ASR); một heuristic khởi điểm (**Synthesis**, chưa đo): partial kết thúc bằng liên từ treo thì kéo dài timeout, kết thúc bằng "nhé/ạ/nhỉ" kèm ngữ điệu đi xuống thì có thể rút ngắn.
- **ASR và từ đệm:** model có thể bỏ hoặc giữ "ờ", "à" tuỳ dữ liệu train; Whisper có xu hướng bỏ. Ảnh hưởng tới WER nếu ref có ghi (§5.7.2) và tới bộ lọc "số từ tối thiểu".

### 5.11.3 Hệ quả cho LLM và TTS

- **Xưng hô** (anh/chị/em/cô/chú/bác/mình/bạn/quý khách) là quyết định của LLM và system prompt, gắn với persona; đổi xưng hô giữa chừng nghe rất mất tự nhiên.
- **Câu ngắn, có tiểu từ lịch sự** ("ạ", "nhé") làm giọng bot tự nhiên hơn, nhưng "ạ" ở cuối mỗi câu nghe máy móc. Tài liệu thiết kế §5.5 yêu cầu 1–3 câu ngắn, không markdown (**Reported**).
- **TTS và tiểu từ cuối câu:** "ạ", "nhé", "nhỉ" mang ngữ điệu riêng; đưa vào bộ prompts đánh giá TTS.

---

## 5.12 Gắn với pipeline: checklist theo tầng

| Tầng | Việc phải làm vì đặc thù tiếng Việt | Tham chiếu thiết kế |
|---|---|---|
| VAD | `speech_pad_ms` 100–200 (hoặc lớn hơn), pre-roll 200–300 ms; test câu kết thúc bằng nặng/ngã, phụ âm đầu vô thanh | §5.2, §7.1 |
| Turn detection | Đo false-cutoff riêng tiếng Việt; test pause sau "thì/là"; lệnh ngắn | §5.3, §10 |
| ASR | Ép `language="vi"`; NFC output; hotwords tên riêng; đo theo vùng, theo thanh, critical span | §5.4, §10 |
| Gate hallucination | Luật số từ tối thiểu không được nuốt "không"/"dừng" | §5.4.4 |
| ITN | Tuỳ chọn cho UI/entity; giữ text gốc | §5.5 |
| LLM | Quy ước số kiểu Việt hoặc số bằng chữ; xưng hô; không markdown/URL | §5.5 |
| Chunker | Cắt ở dấu câu; không cắt giữa số/viết tắt chưa xong | §5.5 |
| TN + lexicon | NFC, số/tiền/ngày/giờ/đơn vị/viết tắt, respelling tên riêng/từ Anh; regression tests | §5.5 |
| TTS | Preset theo vùng; chấm thanh điệu riêng; test ranh giới chunk, code-switch | §5.6, §10 |
| Barge-in | Phân biệt backchannel với xác nhận theo trạng thái hội thoại | §7.3 |
| Đánh giá | Một normalizer chung cho ref/hyp; báo SER/WER, CER, TER, critical span theo vùng | §5.4.2, §10 |

---

## 5.13 Lỗi kinh điển: triệu chứng → nguyên nhân → cách sửa

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| WER cao bất thường dù nghe transcript thấy đúng | Ref và hyp khác dạng Unicode (NFD/lai) hoặc khác kiểu bỏ dấu | NFC + chuẩn hoá vị trí dấu ở cả hai phía (§5.7.2) |
| Lexicon/hotword không khớp dù từ "giống hệt" | Text NFD hoặc dạng lai; `ð` thay `đ` | NFC ở mọi biên; bảng ký tự giống nhau |
| ASR nhầm thanh ngã/nặng ở cuối câu | Cắt đuôi âm tiết (pad nhỏ, endpoint sớm) | Tăng `speech_pad_ms`, pre-roll; đo bằng thực hành cắt đuôi |
| Mất phụ âm đầu ("áng" thay "sáng") | Thiếu pre-roll, VAD bắt đầu muộn | Pre-roll 200–300 ms |
| WER giọng Nam/Trung cao hơn hẳn | Phương ngữ; lỗi "đúng âm sai chữ" | Báo cáo theo vùng; xem ma trận thanh; cân nhắc model/fine-tune; tập trung critical span |
| TTS đọc `1.250` thành "một phẩy hai trăm năm mươi" (hoặc ngược lại) | LLM viết số kiểu Anh, normalizer giả định kiểu Việt | System prompt quy ước số; heuristic nhóm 3 chữ số; test |
| TTS đọc "hai mươi một" thay vì "hai mươi mốt", "một trăm không năm" | Normalizer port từ tiếng Anh, thiếu luật mốt/lăm/linh | Luật §5.8.3 + regression |
| TTS đánh vần `UBND` thay vì đọc "uỷ ban nhân dân" | Thiếu từ điển viết tắt | Từ điển theo domain, TN trước G2P |
| TTS đọc từ tiếng Anh như chữ Việt | TTS không hỗ trợ code-switch | Respelling qua lexicon |
| Bot bỏ qua lệnh "không" hoặc "dừng" | Gate độ dài/số từ quá chặt | Ngoại lệ cho từ khoá lệnh; tune trên dữ liệu thật |
| Bot dừng giữa câu mỗi khi user "ừ" | Mọi tiếng nói đều kích hoạt barge-in | Duration gate, speaker lock, quick ASR + danh sách backchannel theo trạng thái (§7.3) |
| Bot ngắt lời khi user dừng sau "thì..." | Timeout im lặng ngắn, không có tín hiệu ngôn ngữ | Semantic endpoint; kéo dài timeout khi partial kết thúc bằng liên từ treo |
| Text cắt chunk làm dấu thanh rơi sang chunk sau | Cắt theo số ký tự trên text NFD hoặc theo token BPE | NFC trước chunker; chỉ cắt ở khoảng trắng/dấu câu |

## 5.14 Thực hành

1. **Phân tích âm tiết:** viết hàm `parse_syllable(s) -> (onset, glide, nucleus, coda, tone)`. Test với: `quốc, nguyễn, giường, gì, khuya, tay, tai, xoong, oanh, khuỷu, uỷ, ạ`. Đối chiếu với bảng §5.2.1.
2. **Unicode:** lấy một đoạn tiếng Việt, tạo 4 phiên bản (NFC, NFD, lai "ô + dấu nặng rời", kiểu bỏ dấu cũ). In `len()`, so `==`, đếm token bằng tokenizer của Whisper và của một LLM bạn dùng.
3. **Normalizer đánh giá:** cài `norm_for_wer`, thêm bước số (§5.8.3) và bảng `i/y`. Chạy lại bảng §5.7.1. Thêm 20 ca test gồm phủ định và từ vùng miền; xác nhận normalizer **không** che lỗi `có ↔ không`, `heo ↔ lợn`.
4. **SER vs WER vs CER:** lấy 50 câu output ASR thật, tính SER, WER theo từ (dùng một bộ tách từ), CER, TER. Giải thích vì sao bốn con số khác nhau.
5. **Ma trận thanh:** ghi âm (hoặc lấy từ corpus) 60 âm tiết đơn, 10 cho mỗi thanh, ở hai giọng vùng khác nhau. Cho ASR nhận dạng, vẽ ma trận nhầm lẫn 6 × 6 cho mỗi giọng.
6. **Đọc số:** mở rộng `read_int` cho thập phân (`3,5`), số âm, tiền (`1.250.000đ`, `50k`, `2tr`), giờ (`14h30`), ngày (`1/5`, `01/05/2025`), số điện thoại. Viết ≥ 5 ca test cho mỗi lớp, gồm ca mơ hồ.
7. **ITN ngược:** viết hàm đổi "hai mươi mốt", "một trăm linh năm", "hai trăm rưỡi", "một nghìn hai" về chữ số. Chạy trên output ASR có số.
8. **Lexicon:** lập 30 mục cho domain của bạn (tên sản phẩm, từ Anh, viết tắt). Cho TTS đọc trước và sau lexicon; chấm bằng tai.
9. **Lệnh ngắn:** ghi âm "không", "dừng", "thôi", "ừ", "vâng" ở 3 tốc độ. Đưa qua VAD + gate của pipeline với tham số §5.2 và tham số HF s2s; ghi lại cái nào bị nuốt.
10. **Pause giữa câu:** ghi 20 câu có pause 500–1 500 ms sau "thì", "là", "mà". Đo tỷ lệ bị cắt lượt bởi timeout im lặng và bởi Smart Turn.

## 5.15 Đáp án các câu hỏi tự kiểm tra

**Q1. Vì sao CER và WER trên tiếng Việt cho kết quả khác nhau? Một "từ" tiếng Việt là âm tiết hay từ ghép?**

- Về ngôn ngữ học, **từ** có thể gồm một hoặc nhiều âm tiết (`học_sinh`, `đại_học`), và khoảng trắng chỉ ngăn cách **âm tiết**. Trong benchmark ASR tiếng Việt, "từ" để tính WER **thường là âm tiết** (tách theo khoảng trắng), tức WER thực chất là SER. Nếu tách từ trước thì WER theo từ thường cao hơn (ví dụ **Reproduced**: một lỗi trong "học sinh đi học" cho SER 0.25 nhưng WER theo từ 0.33) và phụ thuộc bộ tách từ.
- **CER** đếm lỗi trên ký tự. Một âm tiết tiếng Việt dài 1–7 ký tự; lỗi chỉ sai dấu thanh là 1 ký tự sai (trên NFC), lỗi sai cả âm đầu là 2–3 ký tự, trong khi WER tính cả hai là 1 lỗi. Nên CER thấp hơn WER nhiều và nhạy với *mức độ* sai, còn WER thì không (ví dụ **Reproduced**: mất dấu nặng → WER 0.20, CER 0.062; `tr → ch` → WER 0.20, CER 0.125).
- Cả hai còn phụ thuộc mạnh vào normalizer (Unicode, kiểu bỏ dấu, số, dấu câu) và vào dạng mã hoá (NFD làm CER đếm combining mark như ký tự riêng). Vì vậy chỉ so con số khi cùng tập, cùng normalizer, cùng đơn vị; báo cả SER/WER, CER, TER và critical span.

**Q2. Vì sao cắt mất 50 ms đầu hoặc cuối âm tiết có thể làm sai thanh?**

- Thanh điệu tiếng Việt là tổ hợp đường F0, chất giọng và trường độ, trải trên **toàn âm tiết**, và phần phân biệt các thanh dễ nhầm nằm ở giữa và cuối: hỏi phân biệt bằng đoạn F0 **lên lại ở cuối**; ngã bằng **đứt quãng thanh hầu ở giữa** rồi lên; nặng bằng **rơi nhanh và tắc thanh hầu ở cuối**; sắc trong âm tiết tắc rất ngắn. Cắt 50 ms cuối có thể xoá đúng đoạn đó: hỏi còn lại giống huyền/nặng, nặng mất tắc thanh hầu nghe giống huyền.
- Vùng cuối âm tiết lại có năng lượng thấp, không tuần hoàn (creaky), nên VAD và gate năng lượng dễ coi là im lặng và cắt đi. Âm tiết ngắn (nặng, âm tiết tắc) chỉ dài 100–200 ms, nên 50 ms là phần lớn của nó.
- Ở đầu âm tiết, phụ âm vô thanh (`s, x, kh, th, ph, h`) có năng lượng thấp; cắt mất làm ASR thiếu manh mối âm đầu, và F0 khởi đầu (điểm xuất phát của đường nét) cũng giúp phân biệt thanh.
- Vì vậy cần `speech_pad_ms` 100–200 (thiết kế §5.2, **Reported**), pre-roll 200–300 ms, không cắt audio trước khi endpoint thực sự xảy ra, và chunk TTS không được cắt đuôi câu.

**Q3. `ộ` dạng NFC và NFD khác nhau thế nào khi so sánh chuỗi hoặc tính WER?**

- **NFC:** 1 code point U+1ED9 (LATIN SMALL LETTER O WITH CIRCUMFLEX AND DOT BELOW). **NFD:** 3 code point `o` U+006F + U+0323 (dấu nặng) + U+0302 (dấu mũ); dấu nặng đứng trước do canonical ordering (**Reproduced**).
- Hai dạng hiển thị giống hệt nhưng `==` trả `False`, `len()` là 1 vs 3, byte UTF-8 khác nhau. Mọi so sánh chuỗi, tra lexicon, hotword, regex, key dictionary đều có thể trượt; tokenizer sinh token khác (thường nhiều hơn).
- Khi tính WER, mọi âm tiết có dấu ở dạng NFD bị tính là **sai** so với ref NFC: câu "hôm nay trời đẹp quá" ở NFD so với ref NFC cho WER 0.80 và CER 0.56 dù đúng hoàn toàn (**Reproduced**). Còn dạng "lai" (`ô` dựng sẵn + dấu nặng rời) là dạng thứ ba, cũng khác cả hai.
- Cách sửa: `unicodedata.normalize("NFC", s)` ở **mọi biên nhận text** và trong normalizer đánh giá. NFC không sửa được khác biệt vị trí dấu (`hòa`/`hoà`), biến thể `i/y` và ký tự giống nhau khác mã (`ð`/`đ`); những cái đó cần bước chuẩn hoá riêng.

---

## 5.16 Tóm tắt một trang

- **Âm tiết** = âm đầu + (âm đệm) + âm chính + (âm cuối) + thanh. Âm chính và thanh bắt buộc. Tập âm tiết hữu hạn (cỡ vài nghìn).
- **Chính tả cần thuộc:** `c/k/q`, `g/gh`, `ng/ngh` trước `i/e/ê`; `qu` = /k/ + /w/; `gi` + nguyên âm thì `i` thuộc âm đầu; `ay/au` có `a` ngắn; `ia/iê`, `ưa/ươ`, `ua/uô` là cùng nguyên âm đôi.
- **Sáu thanh** khác nhau ở F0, chất giọng, trường độ; hỏi/ngã/nặng phân biệt ở **giữa và cuối** âm tiết → pad VAD, pre-roll, không cắt đuôi chunk.
- **Phương ngữ:** Bắc nhập `d/gi/r`, `s/x`, `tr/ch`; Nam nhập hỏi/ngã, `-n/-ng`, `-t/-c`; Trung khác thanh. Lỗi "đúng âm sai chữ". Báo cáo theo vùng.
- **Unicode:** NFC ở mọi biên. `ộ` NFC = 1 code point, NFD = 3 (`o` + U+0323 + U+0302). NFD so với NFC: WER 0.80 cho câu đúng. NFC **không** sửa kiểu bỏ dấu cũ/mới (`hòa`/`hoà`), `i/y`, `ð`/`đ`.
- **Âm tiết ≠ từ.** "WER" tiếng Việt thường là SER. CER thấp hơn WER nhiều. Báo SER/WER, CER, TER, critical span.
- **Normalizer đánh giá** áp dụng giống nhau cho ref và hyp: NFC → ký tự lạ → lowercase → dấu câu → vị trí dấu thanh → số. Không bỏ dấu thanh, không đổi từ vùng miền.
- **TN** (trước TTS, bắt buộc) và **ITN** (sau ASR, tuỳ chọn). Số: mốt, tư, lăm, linh/lẻ, không trăm, nghìn/ngàn. Chấm = nghìn, phẩy = thập phân (ngược tiếng Anh). Tách text hiển thị khỏi text đọc.
- **G2P** tiếng Việt gần như theo quy tắc từng âm tiết + tham số vùng; lỗi đến từ từ mượn, tên riêng, viết tắt, địa danh dân tộc. **Lexicon** respelling dùng được cho mọi TTS.
- **Hội thoại:** backchannel không phải lúc nào cũng bỏ qua được; lệnh một âm tiết dễ bị gate nuốt; pause sau "thì/là" dễ bị cắt lượt; tiểu từ cuối câu là tín hiệu kết lượt.

## 5.17 Liên kết

**Chương sau:** Chương 6 (capture/playback, pre-roll ở client), Chương 10 (VAD, endpoint, turn detection chi tiết), Chương 11 (ASR: decoding, hotwords, streaming), Chương 12 (LLM trong voice loop: prompt cho văn nói), Chương 13 (TTS: frontend, G2P, vocoder), Chương 17 (turn-taking, backchannel, cancellation), Chương 19 (cầu text → speech: chunker, normalizer, lexicon), Chương 21 (đánh giá: WER/CER/TER, MOS thanh điệu, corpus ba miền).

**Chương trước:** [Chương 1](chuong-01-vat-ly-am-thanh-va-co-che-tao-tieng-noi.md) (thanh điệu ở mức vật lý, §1.4.3–§1.4.4), [Chương 4](chuong-04-dsp-cho-tieng-noi-va-dac-trung-dau-vao-model.md) (spectrogram của 6 thanh, thực hành cắt đuôi).

**Tài liệu thiết kế:** [§5.2, §5.3, §5.4.2, §5.4.4, §5.5, §7.3, §10](thiet-ke-pipeline-speech-to-speech-tieng-viet.md).

**Wiki:**

- [Vietnamese Realtime ASR Selection](../wiki/vietnamese-realtime-asr-selection.md): không so WER khác tập/normalizer; corpus Bắc/Trung/Nam, tên riêng, số, phủ định, code-switch; cùng ground truth/normalizer.
- [Vietnamese Realtime TTS Selection](../wiki/vietnamese-realtime-tts-selection.md): chunker → normalizer → TTS; không cắt giữa giá trị đang hoàn thành; 150–300 prompts gồm sáu thanh, số, tên riêng, code-switch, vùng giọng; ASR round-trip chỉ là proxy.
- [Kokoro Vietnamese](../wiki/kokoro-vietnamese.md): TTS dựa trên phoneme với `vig2p`.
- [Whisper Hallucination Mitigation](../wiki/whisper-hallucination-mitigation.md): `language="vi"`, blacklist tiếng Việt, luật số từ tối thiểu.
- [Smart Turn v3.2](../wiki/smart-turn.md): benchmark tiếng Việt của turn detector.
- [Silero VAD](../wiki/silero-vad.md): `speech_pad_ms`, `min_speech_duration_ms`.

**Đọc thêm ngoài wiki (giáo trình và tài liệu chuẩn, gợi ý):** Đoàn Thiện Thuật, *Ngữ âm tiếng Việt*; Cao Xuân Hạo, *Tiếng Việt: Mấy vấn đề ngữ âm, ngữ pháp, ngữ nghĩa*; Mai Ngọc Chừ, Vũ Đức Nghiệu, Hoàng Trọng Phiến, *Cơ sở ngôn ngữ học và tiếng Việt*; Kirby (2011), *Vietnamese (Hanoi Vietnamese)*, Journal of the International Phonetic Association; Brunelle (2009) về thanh điệu và chất giọng tiếng Việt; Unicode Standard Annex #15 (*Unicode Normalization Forms*); Sproat et al. (2001), *Normalization of non-standard words*; Ebden & Sproat (2015), *The Kestrel TTS text normalization system*; tài liệu VnCoreNLP, underthesea, espeak-ng.
