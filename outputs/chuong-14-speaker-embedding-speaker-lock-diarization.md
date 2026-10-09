# Chương 14. Speaker: embedding, speaker lock, diarization 🟢

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần IV.
> **Chương trước:** [Chương 13. TTS: từ văn bản tới waveform](chuong-13-tts-tu-van-ban-toi-waveform.md). **Chương tiếp theo:** Chương 15. Kiến trúc: cascade, end-to-end full-duplex và lai.
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §7.3 (gating barge-in, speaker lock), §7.5 (diarization), §9.5 (quyền riêng tư).
> **Cơ sở:** phần giải thích về speaker embedding (i-vector, x-vector, ECAPA-TDNN, CAM++), chấm điểm cosine/PLDA, FAR/FRR/EER, clustering và DER là kiến thức nền chung, không phải claim lấy từ nguồn wiki. Tham số và hành vi cụ thể lấy từ wiki và gắn nhãn bằng chứng: [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md), [Nemotron 3 Diarization](../wiki/nemotron-3-diarization.md), [Streaming Sortformer Diarizer 4spk v2.1](../wiki/diar-streaming-sortformer-4spk-v2-1.md), [Multitalker Parakeet Streaming 0.6B v1](../wiki/multitalker-parakeet-streaming-0.6b-v1.md), [Speaker Diarization Core ML](../wiki/speaker-diarization-coreml.md), [Community-Reported Open STT and Realtime Diarization Selection](../wiki/community-open-stt-diarization.md). Số liệu wiki là **Reported** (chưa chạy lại model nào). Mô phỏng ở §14.4 và ví dụ DER ở §14.6.2 chạy bằng Python thuần (**Reproduced**, script ở "Phụ lục chương") trên dữ liệu **tổng hợp**, chỉ minh hoạ logic và số học, không đo model thật. Suy luận của tác giả là **Synthesis**.

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Giải thích speaker embedding là gì, vì sao so sánh bằng cosine, và nó khác gì với embedding của ASR hay của text.
2. Phân biệt ba bài toán hay bị gộp: **verification** (có phải người này?), **identification** (là ai trong tập đã biết?), **diarization** (ai nói khi nào?).
3. Thiết kế **speaker lock** cho barge-in: enrollment, cập nhật dần, ngưỡng, xử lý đoạn ngắn, và nói rõ vì sao nó không phải xác thực.
4. Đọc được kết quả diarization (ma trận activity `T × S`, kênh theo arrival-order, RTTM/SegLST) và tính được **DER** bằng tay.
5. Quyết định khi nào diarizer nằm ngoài critical path, khi nào dùng track riêng theo participant.
6. Xử lý embedding/reference giọng như dữ liệu sinh trắc học.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. Speaker embedding (ECAPA, CAM++) là gì? Cosine similarity được dùng để làm gì?
- Q2. Vì sao speaker lock không phải là xác thực?
- Q3. DER đo gì? Khi nào diarizer nên nằm ngoài critical path?
- Q4. Vì sao đoạn nói 200 ms cho embedding kém tin cậy hơn đoạn 2 s, và pipeline xử lý thế nào?
- Q5. "Arrival-order" nghĩa là gì và giải quyết vấn đề nào của diarization end-to-end?

---

## 14.1 Ba bài toán về người nói

```text
Verification     1 đoạn audio  +  1 người đã đăng ký   →  có / không        (so 1-1, cần ngưỡng)
Identification   1 đoạn audio  +  N người đã đăng ký   →  người thứ k / lạ  (so 1-N)
Diarization      1 bản ghi dài (không biết ai)         →  [(bắt đầu, kết thúc, speaker_i), ...]
```

Điểm khác biệt then chốt (**Synthesis**):

| | Verification / lock | Diarization |
|---|---|---|
| Có enrollment? | Có (hoặc lấy từ lượt đầu) | Không; nhãn chỉ là "speaker1, speaker2…" |
| Nhãn có ý nghĩa ngoài phiên? | Có thể (so với người đã biết) | Không: nhãn chỉ nhất quán trong một bản ghi |
| Đầu ra | điểm số → quyết định nhị phân | các đoạn thời gian gắn nhãn |
| Dùng trong pipeline | gating barge-in, chọn người điều khiển | meeting, call có nhiều người, transcript có speaker tag |

Hai thứ này dùng chung "nguyên liệu" là biểu diễn giọng người nói, nhưng đánh giá bằng thước đo khác nhau (EER/FAR/FRR cho verification, DER cho diarization).

## 14.2 Speaker embedding

### 14.2.1 Ý tưởng

Speaker embedding là vector cố định chiều (thường 192–512 số) tóm tắt **ai đang nói**, bất kể **nói gì**. Mạng được huấn luyện trên rất nhiều speaker với mục tiêu: các đoạn của cùng một người gần nhau, của người khác xa nhau trong không gian vector (**Synthesis**, kiến thức nền).

Chuỗi tính:

```text
waveform 16 kHz → log-mel/fbank (Ch.4) → mạng frame-level (TDNN/ResNet/CAM++)
              → pooling theo thời gian (mean+std, attentive statistics)
              → lớp tuyến tính → embedding (vd. 192 hoặc 512 chiều)
```

Pooling là bước quan trọng: nó biến chuỗi frame độ dài bất kỳ thành một vector, nên **độ dài đoạn ảnh hưởng chất lượng** (xem §14.3.4).

### 14.2.2 Các họ model

| Họ | Ý chính (kiến thức nền) |
|---|---|
| i-vector | Cổ điển, GMM-UBM + phân tích nhân tố. Hiếm dùng mới. |
| x-vector | TDNN + statistics pooling, huấn luyện phân loại speaker. Nền cho nhiều hệ sau. |
| ECAPA-TDNN | x-vector cải tiến: Res2Net block, squeeze-excitation, attentive statistics pooling, multi-layer feature aggregation. Chuẩn phổ biến cho verification. |
| CAM++ | Backbone D-TDNN + context-aware masking và pooling đa mức; ít tham số và nhanh hơn ECAPA ở độ chính xác tương đương, hợp với CPU/độ trễ thấp. |
| ResNet (WeSpeaker) | ResNet 2D trên fbank; WeSpeaker là **toolkit** cung cấp nhiều checkpoint mở (ResNet, ECAPA, CAM++), không phải một kiến trúc. Trang Core ML trích WeSpeaker cho bước embedding và giữ các artifact legacy `wespeaker*.mlmodelc` (**Reported**).[^coreml] |

Wiki nhắc ECAPA/CAM++ như lựa chọn cho speaker lock trong tài liệu hướng dẫn barge-in (**Reported**, nguồn là báo cáo do LLM sinh nên chưa được kiểm chứng độc lập).[^barge] Wiki **không** có trang riêng cho ECAPA hay CAM++, nên chưa có số EER, kích thước hay license tiếng Việt cho chúng: đó là việc phải tự đo trước khi chọn.

### 14.2.3 Cosine similarity

So hai embedding **a**, **b**:

```text
cos(a, b) = (a · b) / (‖a‖ ‖b‖)         ∈ [-1, 1]
```

- Mạng thường được huấn luyện (loss kiểu AAM-softmax) để **góc** giữa các vector mang thông tin người nói, nên cosine phù hợp hơn khoảng cách Euclid.
- Nếu đã chuẩn hoá L2 (`‖a‖ = 1`) thì cosine bằng tích vô hướng, rẻ để tính.
- Giá trị cosine **không** là xác suất và không có ý nghĩa tuyệt đối giữa các model: 0.6 ở model A có thể là "chắc cùng người", ở model B là "chưa chắc". Vì vậy phải **calibrate ngưỡng cho từng model, từng kênh thu** (§14.3.3).
- PLDA (Probabilistic LDA) là phương pháp chấm điểm khác, truyền thống đi cùng x-vector (Kaldi, clustering VBx). Bản Core ML của pyannote Community-1 có artifact `PLDA`, `PldaRho` (từ `plda.npz`, `xvec_transform.npz`) và trích VBx cho bước clustering (**Reported**).[^coreml]
- Trong thực tế verification còn dùng **score normalization** (s-norm/AS-norm: chuẩn hoá điểm theo một cohort impostor) để ngưỡng ổn định hơn giữa các kênh thu (kiến thức nền).

### 14.2.4 Embedding mang gì và không mang gì

Mang: âm sắc đường thanh, đặc trưng giọng, một phần phong cách nói. Bị ảnh hưởng bởi: kênh thu (mic, codec, điện thoại 8 kHz), nhiễu, tiếng vang, cảm xúc, bệnh, tuổi, nói thì thầm, và **độ dài**. Embedding *không* chứng minh danh tính, và với TTS/voice-cloning hiện đại có thể bị giả (xem §14.3.5).

## 14.3 Speaker lock cho barge-in

### 14.3.1 Bài toán

Khi bot đang nói, VAD thấy có giọng người và pipeline cân nhắc ngắt bot. Nhưng nguồn giọng có thể là: user thật, TV/radio, người khác trong phòng, hoặc tiếng bot lọt lại qua loa (echo, xem Ch.7). Speaker lock thêm một cổng: **chỉ ngắt nếu đoạn nói giống giọng user chủ**.

Wiki mô tả cơ chế này như một tầng trong gating chống ngắt nhầm, cùng với duration gate và quick ASR (**Reported**):[^design][^barge]

| Cơ chế | Giá trị khởi điểm (**Reported**) |
|---|---|
| Duration gate (môi trường sạch) | 100–200 ms speech liên tục |
| Duration gate (môi trường ồn) | threshold 0.7 và ≥300–500 ms |
| Speaker lock | cosine embedding ECAPA/CAM++ so với embedding user (từ lượt đầu, cập nhật dần); bỏ nếu < ~0.5–0.6, cần calibrate |
| Quick ASR (tuỳ chọn) | ≥2 từ và không trùng câu bot đang phát |

### 14.3.2 Enrollment

Ba cách lấy embedding tham chiếu, từ ít ma sát đến nhiều:

1. **Từ lượt đầu (implicit):** lấy embedding của lượt nói đầu tiên của user trong phiên; wiki dùng cách này (**Reported**).[^barge] Ưu: không cần user làm gì. Nhược: nếu lượt đầu là người khác/nhiễu/TV thì khoá nhầm; **Synthesis**: nên yêu cầu lượt đầu đủ dài và VAD confidence cao, và chỉ khoá sau khi ASR cho ra văn bản có nghĩa.
2. **Explicit enrollment:** user đọc một câu ngắn. Chính xác hơn, nhưng thêm bước UX.
3. **Hồ sơ lưu lâu dài:** nhận ra user cũ giữa các phiên. Đây đã là **dữ liệu sinh trắc học lưu trữ**, kéo theo yêu cầu đồng ý và xoá (§14.6).

### 14.3.3 Cập nhật dần và calibrate ngưỡng

**Cập nhật dần** (**Synthesis**, một thiết kế hợp lý): giữ một centroid `c`; với mỗi đoạn mới `e` đã *được chấp nhận chắc chắn* (cosine cao, đủ dài):

```text
c ← normalize( (1 - α)·c + α·e )     α nhỏ, vd. 0.05–0.1
```

Quy tắc an toàn: chỉ cập nhật bằng đoạn **điểm cao** (cao hơn ngưỡng chấp nhận một biên), nếu không sẽ "trôi" sang giọng người khác (drift poisoning). Có thể giữ cả vài embedding riêng (nhiều giọng/tư thế mic) thay vì một centroid.

**Calibrate ngưỡng:** thu hai tập điểm cosine trên **đúng điều kiện triển khai**:

- target: cùng người, nhiều đoạn, nhiều độ dài, nhiều môi trường;
- impostor: người khác, TV, giọng bot lọt qua.

Với ngưỡng `t`:

```text
FRR(t) = tỉ lệ target bị từ chối  (user thật bị từ chối → không ngắt được bot; gây bực)
FAR(t) = tỉ lệ impostor được nhận (TV ngắt bot nhầm)
EER    = giá trị tại FRR = FAR
```

Với voice agent, hai lỗi **không cân xứng** (**Synthesis**): từ chối user thật rất khó chịu (user nói mà bot cứ đọc tiếp, user mất quyền điều khiển), còn TV ngắt nhầm làm bot dừng và mất lượt nhưng có thể giảm hậu quả (ví dụ hỏi lại hoặc cho phép nói tiếp phần bị cắt). Mặc định hợp lý là đặt ngưỡng thiên về **FRR thấp**; ở môi trường TV/nhiều người thường trực thì phải dịch điểm vận hành về phía FAR thấp. Dù chọn thế nào, coi speaker lock là một trong nhiều cổng (kết hợp duration gate) chứ không là cổng duy nhất. Khoảng "0.5–0.6" của wiki là **điểm khởi đầu chưa kiểm chứng**, không phải hằng số.

### 14.3.4 Đoạn ngắn

Barge-in cần quyết định trong 100–500 ms, nhưng embedding trên đoạn ngắn rất nhiễu vì statistics pooling có ít frame (**Synthesis**):

- Đoạn ≲ 0.5 s: điểm cosine dao động mạnh, cả target lẫn impostor trải rộng hơn, phần chồng lấn tăng.
- Giải pháp thực dụng: tích luỹ buffer, **chấm điểm lại khi đoạn dài thêm** (vd. lúc 300 ms, 600 ms, 1 s) thay vì chấm một lần; hoặc dùng duration gate làm cổng chính và speaker lock làm cổng "veto" muộn hơn chút.
- Chạy embedding trên **audio sau front-end** hay **audio thô**? Echo canceller/denoise (Ch.7) làm đổi phổ. Wiki nêu chỉ áp denoise cho nhánh VAD (**Reported**).[^barge] Nên chọn một nguồn nhất quán giữa lúc enrollment và lúc so sánh, và calibrate trên nguồn đó (**Synthesis**).

### 14.3.5 Vì sao speaker lock không phải là xác thực

Tài liệu thiết kế khẳng định speaker lock **không phải là xác thực** (**Synthesis** trong thiết kế).[^design] Lý do cụ thể:

1. **Xác suất, không bảo chứng.** Cosine vượt ngưỡng chỉ nghĩa "giống", không nghĩa "đúng". Luôn có FAR > 0.
2. **Ngưỡng mềm, đặt thiên về tiện dụng.** Ngưỡng được chọn để giảm bực bội, không phải để chống kẻ tấn công.
3. **Dễ giả.** Replay bản ghi, voice conversion và TTS cloning (Ch.13) có thể tạo giọng vượt ngưỡng; verification nghiêm túc cần anti-spoofing/liveness (nằm ngoài phạm vi chương).
4. **Enrollment implicit không có gốc tin cậy.** "Người nói đầu tiên" chưa chắc là chủ tài khoản.
5. **Mục đích khác.** Speaker lock trả lời "đây có vẻ là giọng đang trò chuyện không?", để quyết định ngắt bot. Nó **không** được dùng để mở khoá hành động nhạy cảm (chuyển tiền, xoá dữ liệu); các hành động đó cần xác thực riêng (OTP, đăng nhập, xác nhận).

### 14.3.6 Những chỗ speaker lock hỏng

| Tình huống | Hệ quả | Cách giảm |
|---|---|---|
| User cảm lạnh / thì thầm / nói to | Cosine tụt, FRR tăng | Cập nhật dần, nhiều centroid, ngưỡng mềm |
| Đổi mic / đổi phòng | Dịch phân phối | Calibrate theo thiết bị; re-enroll khi lệch kéo dài |
| Hai người cùng dùng một thiết bị | Chỉ một người ngắt được bot | Cho phép chế độ tắt lock |
| Nói chồng với tiếng bot lọt | Embedding lẫn | AEC tốt (Ch.7), ưu tiên duration gate |
| Backchannel ngắn ("ừ", "vâng") | Embedding vô nghĩa vì quá ngắn | Không dùng lock cho đoạn quá ngắn; xem lưu ý backchannel ở thiết kế §7.3 |

## 14.4 Mô phỏng: cosine, enrollment, ngưỡng (Reproduced, dữ liệu tổng hợp)

Script ở Phụ lục tạo 40 "người" là vector ngẫu nhiên chuẩn hoá 64 chiều; mỗi đoạn nói là tâm người cộng nhiễu Gauss độ lệch `s`; enrollment là trung bình 3 đoạn; đo cosine target (20 đoạn/người) và impostor (5 người khác × 8 đoạn).

Kết quả đã chạy:

| Nhiễu `s` | cosine target TB | cosine impostor TB | ngưỡng tại EER | FRR | FAR | FRR @0.5 | FRR @0.6 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.06 | 0.87 | −0.01 | 0.38 | 0.000 | 0.000 | 0.000 | 0.000 |
| 0.10 | 0.71 | −0.00 | 0.41 | 0.000 | 0.000 | 0.000 | 0.029 |
| 0.15 | 0.53 | −0.01 | 0.29 | 0.004 | 0.006 | 0.360 | 0.812 |

Khi hai phân phối tách hẳn (FRR = FAR = 0), mọi ngưỡng trong khoảng trống đều đạt EER; script báo ngưỡng **nhỏ nhất** trên lưới 0.01, nên cột "ngưỡng tại EER" ở hai dòng đầu không duy nhất.

Ba bài học (**Synthesis** từ mô phỏng):

1. Nhiễu tăng làm cosine target **tụt** (0.87 → 0.53) mà impostor vẫn quanh 0: ngưỡng tốt **dịch theo điều kiện**, không có ngưỡng tuyệt đối.
2. Ở `s = 0.15`, cosine target trung bình ≈ 0.53 nằm ngay trong vùng "bỏ nếu < 0.5–0.6" của wiki: ngưỡng 0.5 đã từ chối 36% target, ngưỡng 0.6 từ chối 81%, trong khi ngưỡng EER của chính dữ liệu này là 0.29. Đó là minh hoạ cho "cần calibrate".
3. Dữ liệu tổng hợp **quá dễ** (impostor độc lập hoàn toàn nên cosine ≈ 0). Người thật, nhất là cùng giới/vùng miền hoặc TV có giọng giống, cho phân phối impostor rộng hơn nhiều. Đừng đọc EER ≈ 0 ở đây như hiệu năng thật.

## 14.5 Diarization

### 14.5.1 Bài toán và đầu ra

Diarization trả lời "who spoke when" trên audio **không biết trước số người hay danh tính**. Đầu ra chuẩn là danh sách đoạn `(start, end, speaker_label)`; hay lưu dạng **RTTM** (đoạn theo speaker) hoặc **SegLST** (đoạn kèm transcript, dùng cho multitalker ASR).[^multi] Nhãn như `speaker1` chỉ có nghĩa trong phạm vi một bản ghi.

Có **overlap** (hai người nói đồng thời) là khó nhất: hệ gán một nhãn mỗi frame sẽ bỏ sót người thứ hai.

### 14.5.2 Kiến trúc pipeline cổ điển (cascade)

```text
audio → VAD / speaker segmentation → cắt đoạn → embedding mỗi đoạn
      → clustering (agglomerative, spectral, VBx…) → gán nhãn → (tuỳ chọn) xử lý overlap, resegment
```

Điểm mạnh: mô-đun, dễ thay từng khối; chạy tốt offline vì clustering nhìn được toàn bản ghi. Điểm yếu: clustering cần thấy đủ dữ liệu, nên **online khó**, và overlap xử lý kém. Ví dụ trong wiki: pyannote Community-1 có segmentation + embedding + PLDA (đã chuyển Core ML cho Apple, 16 kHz mono, iOS 17/macOS 14+) (**Reported**).[^coreml] Thảo luận cộng đồng gọi pyannote là chuẩn, diart chạy live, và nói live diarization "noticeably worse than offline", với batch pass (WhisperX + pyannote) cho nhãn sạch hơn (**Reported**, một thread, không có DER).[^community]

### 14.5.3 End-to-end neural: họ Sortformer

Thay vì cluster, mạng dự đoán trực tiếp **hoạt động của từng speaker theo từng frame**:

- Đầu ra là ma trận `T × S` xác suất trong [0, 1]; model Nemotron 3 Diarization xuất `[T, 8]` với 8 kênh, mặc định bước 10 ms (**Reported**).[^nemo3] Streaming Sortformer v2.1 xuất `T × 4` ở 1 frame mỗi 0.08 s (**Reported**).[^sort]
- Vì mỗi frame có xác suất độc lập theo kênh nên **overlap được biểu diễn tự nhiên** (nhiều kênh cùng cao).
- **Vấn đề permutation:** kênh nào là người nào? Nếu nhãn kênh tuỳ ý thì loss không xác định. Sortformer giải bằng cách **sắp kênh theo thời điểm xuất hiện (arrival-order)**: người nói đầu tiên ở kênh 0, người thứ hai ở kênh 1,… (**Reported**).[^nemo3][^sort] Nhờ đó huấn luyện có supervision ổn định và kênh có thứ tự dự đoán được.
- **Streaming:** model giữ **Arrival-Order Speaker Cache (AOSC)** cộng một FIFO queue để nhớ speaker đã gặp qua các chunk, nên nhãn nhất quán khi xử lý dần (**Reported**).[^nemo3][^sort]
- Giới hạn cứng: số kênh output cố định theo kiến trúc (4 cho Sortformer 4spk, 8 cho Nemotron 3) (**Reported**). Model không báo lỗi khi có nhiều người hơn, mà **suy giảm âm thầm**: card v2.1 nói rõ "degraded performance on 5 or more speakers", ví dụ DIHARD III ≥5 speaker DER 41.42 so với 15.09 ở ≤4 speaker (**Reported**).[^sort] Vì vậy chọn model theo số người tối đa của tình huống là quyết định thiết kế, không sửa được bằng tinh chỉnh tham số (**Synthesis**).

Quy trình hậu xử lý (**Synthesis** từ mô tả đầu ra của wiki): ngưỡng hoá xác suất → loại đoạn rất ngắn → gộp khoảng lặng nhỏ → xuất `(start, end, speaker_index)`. Hậu xử lý có tham số tối ưu theo từng tập dev, wiki nói điều này với model offline (**Reported**).[^sort]

### 14.5.4 Latency của diarization streaming

Input buffer latency = (`CHUNK_LEN` + `RIGHT_CONTEXT`) × 80 ms, **chưa tính thời gian tính toán** (**Reported**).[^nemo3]

| Model / profile | Latency buffer | Nguồn |
|---|---:|---|
| Nemotron 3 Diarization, ultra-low | 0.32 s | **Reported**[^nemo3] |
| Nemotron 3 Diarization, very low | 0.64 s | **Reported**[^nemo3] |
| Nemotron 3 Diarization, low | 1.04 s | **Reported**[^nemo3] |
| Nemotron 3 Diarization, offline-style | 30.4 s | **Reported**[^nemo3] |
| Streaming Sortformer v2.1, low | 1.04 s (RTF 0.093 trên RTX 6000 Ada) | **Reported**[^sort] |
| Streaming Sortformer v2.1, very high | 30.4 s (RTF 0.002) | **Reported**[^sort] |

Quy luật chung: **latency thấp → ít future context → DER cao hơn**; latency cao → DER thấp nhưng nhãn đến muộn. Với Nemotron 3, mức suy giảm khá thoải: CALLHOME-Part2 full DER 9.10 (30.4 s) → 10.29 (1.04 s) → 10.66 (0.64 s) → 11.32 (0.32 s) (**Reported**).[^nemo3] Wiki ghi DER của v2.1 ở latency 1.04 s, ví dụ DIHARD III full 20.21, CALLHOME-part2 full 11.19, CH109 5.09 (**Reported**).[^sort] Model được huấn luyện chủ yếu trên tiếng Anh công khai, card cảnh báo có thể suy giảm với ngôn ngữ khác và audio nhiễu (**Reported**).[^sort] **Chưa có DER tiếng Việt** trong wiki (**Reported** từ thiết kế §7.5).[^design]

### 14.5.5 Diarization + ASR: multitalker

Hai hướng ghép (**Synthesis** dựa trên wiki):

1. **ASR rồi gán nhãn:** chạy ASR thường, sau đó map từng từ/đoạn sang speaker theo timestamp diarization. Đơn giản, nhưng sai khi overlap và khi timestamp ASR lệch.
2. **Multitalker ASR:** Multitalker Parakeet Streaming 0.6B v1 triển khai **một instance ASR cho mỗi speaker**, mỗi instance nhận cùng audio trộn cộng activity của speaker đó từ diarizer, tiêm "speaker kernel" vào encoder và xuất transcript riêng, cho ra transcript SegLST (**Reported**).[^multi] Ưu: không cần enrollment, xử lý overlap. Giá: tài nguyên nhân theo số speaker; model fine-tune từ base tiếng Anh (Nemotron Speech Streaming EN 0.6B) (**Reported**),[^multi] nên **không dùng trực tiếp cho tiếng Việt**.

Chuỗi này cũng cho thấy diarizer có thể là **tầng trước ASR** (cung cấp activity) chứ không chỉ hậu xử lý.

## 14.6 DER: đo diarization

### 14.6.1 Định nghĩa

```text
DER = (Missed speech + False alarm + Speaker confusion) / Tổng thời gian speech tham chiếu
```

- **Missed speech:** có người nói (theo tham chiếu) mà hệ không gán ai.
- **False alarm:** hệ gán speaker khi tham chiếu là im lặng/không speech.
- **Speaker confusion:** hệ gán sai người. Trước khi đếm, **ánh xạ tối ưu** giữa nhãn hệ và nhãn tham chiếu (vì nhãn chỉ là tên tuỳ ý).
- **Overlap** tính theo từng người: hai người cùng nói tính 2 đơn vị thời gian speech tham chiếu.
- **Collar:** vùng đệm quanh ranh giới đoạn bị bỏ qua khi chấm, vì ranh giới thủ công không chính xác. Wiki ghi collar 0.25 s cho CALLHOME-part2 và CH109, 0.0 s cho DIHARD III, AliMeeting, AMI, NOTSOFAR1 (**Reported**).[^sort] So DER giữa các bộ chỉ có nghĩa khi **cùng collar và cùng cách xử lý overlap**.

### 14.6.2 Ví dụ tính tay (Reproduced)

Tham chiếu (60 s bản ghi, tổng speech tham chiếu 52 s): A nói 0–20 s; B nói 20–40 s; A nói 38–50 s (A và B chồng nhau 38–40 s).
Hệ đoán: `x` 0–20; `y` 21–35; `x` 35–45; `y` 45–50.

Ánh xạ tối ưu: A→x, B→y. Script cho: missed 3.0 s, false alarm 0.0 s, confusion 8.0 s, DER = 11.0 / 52.0 = **0.212** (21.2%).

Đọc kết quả (**Synthesis**): missed 3.0 s = 1 s ở 20–21 s (hệ chưa thấy B) + 2 s ở 38–40 s (overlap A/B, hệ chỉ gán một người). Confusion 8.0 s = 3 s ở 35–38 s (hệ gán `x`=A trong khi B còn nói) + 5 s ở 45–50 s (hệ gán `y`=B trong khi A nói). Lỗi dồn ở **ranh giới đổi người và overlap**, đúng chỗ voice agent hay cần chính xác.

### 14.6.3 DER không nói gì về

- **Chất lượng transcript:** diarization đúng không đảm bảo ASR đúng. Thước đo ghép là cpWER (concatenated minimum-permutation WER); wiki ghi cpWER của Multitalker Parakeet là 21.26 trên AMI IHM và 37.44 trên AMI SDM với frontend Streaming Sortformer v2, latency 1.12 s; ở chế độ một người nói, WER trung bình bộ benchmark tiếng Anh là 7.44 (**Reported**).[^multi]
- **Đếm đúng số speaker:** cần thước đo riêng, ví dụ SCA (tỉ lệ buổi đếm đúng) và MAE số speaker mà card Nemotron 3 công bố (**Reported**).[^nemo3]
- **Độ trễ:** DER thường báo cho một profile latency, phải đọc kèm.
- **Dữ liệu tiếng Việt, mic/điện thoại thực tế của bạn:** phải tự đo.

## 14.7 Khi nào diarizer nên ở ngoài critical path

Tài liệu thiết kế: agent một-user **không** đặt diarizer vào critical path; với meeting hoặc nhiều user ưu tiên **track riêng theo participant**; nếu chỉ có audio trộn, thử Nemotron 3 Diarization (**Reported** / **Synthesis**).[^design] Lập luận (**Synthesis**):

| Tình huống | Khuyến nghị | Lý do |
|---|---|---|
| Voice agent 1 user, 1 mic | Không diarizer trong vòng realtime; dùng VAD + (tuỳ chọn) speaker lock | Thêm 0.3–1 s buffer và tài nguyên GPU/CPU mà không đổi quyết định cốt lõi (turn-taking) |
| Cuộc họp nhiều người, mỗi người một kênh (WebRTC participant) | **Track riêng theo participant**, không cần diarize | Danh tính đã biết từ kênh, rẻ và chính xác hơn diarize audio trộn; vẫn cần VAD/AEC theo từng kênh vì tiếng người khác có thể lọt vào mic (cùng phòng, loa ngoài) |
| Nhiều người chung một mic phòng | Diarizer streaming nhưng chạy **song song/nhánh phụ** để gắn nhãn transcript | Lỗi nhãn không được chặn phản hồi |
| Cần transcript chất lượng cao sau cuộc gọi | Batch offline sau cuộc gọi | Offline thấy toàn bản ghi, cluster tốt hơn; cộng đồng báo offline sạch hơn live (**Reported**)[^community] |
| Cần biết ai nói để LLM trả lời đúng người | Diarizer trong đường LLM nhưng **chịu trễ nhãn** | Cân nhắc: dùng nhãn tạm, sửa khi nhãn chốt |

Nguyên tắc: **một thành phần chỉ nằm trên critical path khi quyết định realtime phụ thuộc vào kết quả của nó.** Diarization thường chỉ làm giàu dữ liệu, không quyết định ngắt hay tiếp tục nói.

Hệ quả sizing (**Synthesis**): diarizer nhánh phụ không được làm tăng latency end-to-end; cần hàng đợi giới hạn và nhãn đến trễ phải được xử lý bằng cơ chế "gắn nhãn sau" ở tầng transcript. Khi quá tải, **đừng bỏ lẹ tẻ từng khung** audio: diarizer streaming giữ speaker cache/FIFO liên tục, mất khung làm nhãn đảo hoặc sinh speaker mới. Nên hạ cấp có kiểm soát: đánh dấu đoạn đó là `unknown`, hoặc tắt nhánh live và chuyển sang diarize batch sau cuộc gọi.

## 14.8 Quyền riêng tư và sinh trắc học

- **Speaker embedding và reference giọng là dữ liệu sinh trắc học** (tài liệu thiết kế §9.5 nói embedding và reference dùng để clone giọng là dữ liệu nhạy cảm; không ghi chúng vào operational log) (**Reported**).[^design] Có thể nhận dạng cá nhân nên nhiều khung pháp lý coi là dữ liệu nhạy cảm (**Synthesis**; cần tư vấn pháp lý cho từng địa phương, ngoài phạm vi chương).
- Thực hành tối thiểu (**Synthesis**):
  1. Giữ embedding **trong RAM theo phiên**, xoá khi kết thúc phiên, trừ khi có đồng ý rõ ràng để lưu.
  2. Không ghi embedding, vector, hay audio enrollment vào log, trace, hoặc analytics.
  3. Mã hoá khi lưu; tách khỏi định danh tài khoản nếu có thể; đặt thời hạn lưu và đường xoá theo yêu cầu.
  4. Thông báo cho người dùng khi bật speaker lock/diarization, nhất là với **người thứ ba** bị thu giọng (TV, khách).
  5. Nếu dùng clone giọng ở TTS (Ch.13, Ch.23): reference audio cần có sự đồng ý của chủ giọng.
  6. Nhớ ràng buộc license: các model diarization có license khác nhau, ví dụ Nemotron 3 Diarization `openmdw-1.1`, Streaming Sortformer v2.1 NVIDIA Open Model License, bản Core ML Community-1 CC-BY-4.0 với phạm vi ghi trong NOTICE (**Reported**).[^nemo3][^sort][^coreml] Cần đọc kỹ trước khi dùng thương mại.
- Nhãn diarization (`speaker1`…) có thể kém nhạy cảm hơn embedding, nhưng khi gắn với transcript và thời gian vẫn có thể nhận diện người (**Synthesis**).

## 14.9 Chọn công cụ: bảng quyết định nhanh

| Nhu cầu | Gợi ý | Ghi chú |
|---|---|---|
| Speaker lock trong voice agent | Embedding nhỏ (ECAPA/CAM++-class), tự calibrate | Chưa có bằng chứng tiếng Việt trong wiki; tự đo EER trên dữ liệu thật |
| Diarization streaming, ≤ 8 người | [Nemotron 3 Diarization](../wiki/nemotron-3-diarization.md) | 100M tham số, 16 kHz mono, NeMo trên GPU NVIDIA; **Reported**; chưa có DER tiếng Việt |
| Diarization streaming, ≤ 4 người | [Streaming Sortformer 4spk v2.1](../wiki/diar-streaming-sortformer-4spk-v2-1.md) | 117M; card giới thiệu Nemotron 3 là bản kế nhiệm nhưng không nêu ngày deprecate |
| Trên Apple, on-device | [Speaker Diarization Core ML](../wiki/speaker-diarization-coreml.md) | pyannote Community-1 chuyển Core ML, FluidAudio |
| Chạy trong runtime C++ | [audio.cpp framework](../wiki/audio-cpp-framework.md), [Nemotron 3 Diarization GGUF](../wiki/nemotron-3-diarization-gguf.md) | Xem trang tương ứng |
| Transcript nhiều người, tiếng Anh | [Multitalker Parakeet Streaming 0.6B v1](../wiki/multitalker-parakeet-streaming-0.6b-v1.md) | English only (theo wiki) |
| Chất lượng cao hậu kỳ | Offline (WhisperX + pyannote theo cộng đồng) | **Reported**, một thread |

## 14.10 Checklist thực hành

**Speaker lock**

- [ ] Chọn một nguồn audio nhất quán cho enrollment và so sánh; ghi lại.
- [ ] Thu tập target/impostor trên thiết bị thật; vẽ đường FRR/FAR theo độ dài đoạn (0.3/0.6/1/2 s).
- [ ] Đặt ngưỡng thiên về FRR thấp; kết hợp duration gate; có chế độ tắt lock.
- [ ] Cập nhật centroid chỉ với đoạn điểm cao; có cơ chế re-enroll.
- [ ] Không dùng lock cho hành động cần xác thực.

**Diarization**

- [ ] Xác định có thật sự cần không; nếu có track theo participant thì dùng.
- [ ] Đặt ngoài critical path nếu quyết định realtime không phụ thuộc nó.
- [ ] Ghi đúng profile latency, collar, cách xử lý overlap khi báo DER.
- [ ] Đo DER/cpWER trên **audio tiếng Việt thực tế** của bạn; wiki chưa có số.
- [ ] Kiểm tra số speaker tối đa của model so với tình huống thật.

**Quyền riêng tư**

- [ ] Embedding/reference không vào log; xoá theo phiên hoặc có đồng ý lưu.
- [ ] Kiểm tra license của từng model.

## 14.11 Lỗi thường gặp

| Triệu chứng | Nguyên nhân thường gặp |
|---|---|
| Bot không bao giờ bị ngắt trong phòng ồn | Ngưỡng cosine quá cao, hoặc enrollment nhiễu, hoặc AEC làm đổi phổ |
| TV ngắt bot | Không có duration gate; ngưỡng quá thấp; TV trùng giọng với user |
| Khoá nhầm người sai từ đầu | Implicit enrollment từ lượt đầu không kiểm tra |
| Điểm cosine "tự nhiên" tụt dần trong phiên | Đổi mic/tư thế; không cập nhật centroid |
| Nhãn speaker đảo chéo giữa các chunk | Streaming không giữ speaker cache; hoặc ghép nhãn thủ công sai |
| DER tốt trên báo cáo nhưng tệ thực tế | Khác ngôn ngữ, kênh, collar, overlap; chỉ có số tiếng Anh |
| Thêm diarizer làm bot trả lời chậm | Diarizer nằm trên critical path không cần thiết |
| Embedding xuất hiện trong log | Log nguyên request/payload |

## 14.12 Đáp án các câu hỏi

**Q1.** Speaker embedding là vector cố định chiều, mạng tạo ra từ giọng nói sao cho đoạn cùng người gần nhau, khác người xa nhau (ECAPA-TDNN, CAM++ là hai kiến trúc phổ biến). Cosine similarity đo góc giữa hai vector để quyết định "giống giọng" hay không: trong speaker lock so đoạn mới với embedding user; trong diarization cluster các đoạn. Điểm cosine không phải xác suất và cần calibrate ngưỡng theo model và điều kiện (§14.2–14.4).

**Q2.** Vì nó chỉ cho điểm tương đồng xác suất với ngưỡng nới để tiện dùng, enrollment implicit không có gốc tin cậy, dễ bị replay/cloning đánh lừa, và mục đích của nó là lọc barge-in chứ không bảo vệ tài nguyên. Hành động nhạy cảm cần xác thực riêng (§14.3.5).

**Q3.** DER đo tỉ lệ thời gian speech tham chiếu bị sai, gồm missed speech, false alarm, speaker confusion (sau ánh xạ nhãn tối ưu và có/không collar). Diarizer nên ở ngoài critical path khi quyết định realtime (ngắt, tiếp tục nói) không phụ thuộc kết quả của nó, ví dụ agent một user hoặc khi đã có track riêng theo participant (§14.6–14.7).

**Q4.** Statistics pooling trên ít frame cho thống kê nhiễu; điểm target và impostor chồng lấn mạnh. Pipeline xử lý bằng duration gate làm cổng chính, chấm điểm lặp lại khi buffer dài thêm, và không dùng lock cho backchannel ngắn (§14.3.4).

**Q5.** Arrival-order là quy ước sắp kênh output theo thời điểm mỗi speaker xuất hiện đầu tiên, nhờ đó loại bỏ mơ hồ hoán vị trong huấn luyện và cho nhãn ổn định qua chunk khi kết hợp speaker cache (§14.5.3).

---

## Phụ lục chương: script mô phỏng

File: `/tmp/c14/sim.py` (Python thuần, không phụ thuộc). Sao chép nguyên văn dưới đây để chạy lại.

```python
import random, math, itertools
random.seed(7)
D=64
def norm(v):
    n=math.sqrt(sum(x*x for x in v)); return [x/n for x in v]
def cos(a,b): return sum(x*y for x,y in zip(a,b))
def rnd(): return norm([random.gauss(0,1) for _ in range(D)])
def utt(c,s): return norm([c[i]+random.gauss(0,s) for i in range(D)])
def mean(vs): return norm([sum(v[i] for v in vs)/len(vs) for i in range(D)])
centers=[rnd() for _ in range(40)]
for s in (0.06,0.10,0.15):
    tgt,imp=[],[]
    for k,c in enumerate(centers):
        enr=mean([utt(c,s) for _ in range(3)])
        for _ in range(20): tgt.append(cos(enr,utt(c,s)))
        for j in range(5):
            o=centers[(k+1+j)%40]
            for _ in range(8): imp.append(cos(enr,utt(o,s)))
    best=None
    for t in [i/100 for i in range(-20,100)]:
        frr=sum(x<t for x in tgt)/len(tgt); far=sum(x>=t for x in imp)/len(imp)
        if best is None or abs(frr-far)<best[0]: best=(abs(frr-far),t,frr,far)
    frr_at=[sum(x<t for x in tgt)/len(tgt) for t in (0.5,0.6)]
    print(s, sum(tgt)/len(tgt), sum(imp)/len(imp), best[1:], frr_at)

def der(ref,hyp,T=60.0,dt=0.01):
    n=int(T/dt)
    def lab(segs):
        a=[set() for _ in range(n)]
        for s,e,k in segs:
            for i in range(int(s/dt),int(e/dt)): a[i].add(k)
        return a
    R,H=lab(ref),lab(hyp)
    rs=sorted({k for _,_,k in ref}); hs=sorted({k for _,_,k in hyp})
    total=sum(len(r) for r in R); best=None
    for perm in itertools.permutations(hs+[None]*len(rs),len(rs)):
        m=dict(zip(rs,perm)); miss=fa=conf=0
        for r,h in zip(R,H):
            nr,nh=len(r),len(h); c=sum(1 for x in r if m[x] in h)
            miss+=max(0,nr-nh); fa+=max(0,nh-nr); conf+=min(nr,nh)-c
        e=(miss+fa+conf)/total
        if best is None or e<best[0]: best=(e,miss*dt,fa*dt,conf*dt,total*dt)
    return best
ref=[(0,20,'A'),(20,40,'B'),(38,50,'A')]
hyp=[(0,20,'x'),(21,35,'y'),(35,45,'x'),(45,50,'y')]
print(der(ref,hyp))
```

Điểm cần tự thử: tăng `s`, giảm số đoạn enrollment về 1, thêm impostor có tâm gần tâm target (trộn 50% vector của target) để thấy EER tăng; thử đổi `hyp` để thấy missed/confusion thay đổi thế nào.

### Liên kết sang chương khác

- Chương 4 (DSP): fbank/log-mel là đầu vào của embedding và diarizer.
- Chương 7 (front-end): AEC/denoise đổi phổ, ảnh hưởng embedding; echo là nguồn gây ngắt nhầm.
- Chương 9 (nền ML): pooling, contrastive/margin loss, FastConformer/Transformer ở mức đọc model card.
- Chương 10 (VAD, turn): duration gate đi cùng speaker lock.
- Chương 11 (ASR): multitalker, speaker tag, cpWER.
- Chương 13 (TTS): cloning giọng dùng embedding/reference; rủi ro giả giọng.
- Chương 17 (turn-taking, cancellation): quyết định ngắt, `generation_id`.
- Chương 21 (đánh giá): DER, cpWER, EER.
- Chương 23 (license, privacy, bảo mật): dữ liệu sinh trắc, consent, license model.

[^design]: [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) — §7.3 (bảng gating chống ngắt nhầm, lưu ý speaker lock không phải xác thực), §7.5 (Diarization), §9.5 (embedding/reference là dữ liệu nhạy cảm).
[^barge]: [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md) — phần duration-gated barge-in với speaker lock (ECAPA/CAM++, ngưỡng ~0.5–0.6); nguồn gốc là báo cáo do LLM sinh (chưa kiểm chứng).
[^nemo3]: [Nemotron 3 Diarization](../wiki/nemotron-3-diarization.md) — Identity and release (license), Architecture and I/O (output `[T, 8]`, arrival-order, 10 ms), Streaming latency configurations (bảng 0.32/0.64/1.04/30.4 s), bảng DER theo latency (CALLHOME-Part2 full), SCA/MAE.
[^sort]: [Streaming Sortformer Diarizer 4spk v2.1](../wiki/diar-streaming-sortformer-4spk-v2-1.md) — Architecture and streaming mechanism (AOSC, output `T × 4`, 0.08 s), Streaming configurations (bảng latency/RTF), Limitations (tối đa 4 speaker, suy giảm ≥5 speaker và ngoài tiếng Anh), bảng DER (collar, DIHARD III ≤4/≥5/full, CALLHOME-part2, CH109).
[^multi]: [Multitalker Parakeet Streaming 0.6B v1](../wiki/multitalker-parakeet-streaming-0.6b-v1.md) — Architecture (speaker-kernel injection, một instance mỗi speaker), Inference and usage (SegLST output), Evaluation (cpWER AMI IHM/SDM, frontend Streaming Sortformer v2, latency 1.12 s; bảng WER single-speaker), Relationships (fine-tune từ base EN 0.6B).
[^coreml]: [Speaker Diarization Core ML](../wiki/speaker-diarization-coreml.md) — Supported Community-1 artifacts (Segmentation, FBank, Embedding, PLDA), Legacy compatibility artifacts (wespeaker), Technical specifications, Citations (WeSpeaker, VBx).
[^community]: [Community-Reported Open STT and Realtime Diarization Selection](../wiki/community-open-stt-diarization.md) — "Realtime versus diarization split" (pyannote, diart, NeMo streaming, live kém hơn offline); trang status draft, chỉ một thread cộng đồng.
