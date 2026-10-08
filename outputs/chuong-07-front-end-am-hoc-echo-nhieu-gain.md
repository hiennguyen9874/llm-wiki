# Chương 7. Front-end âm học: echo, nhiễu, gain 🟡

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần III.
> **Chương trước:** [Chương 6. Capture và playback realtime](chuong-06-capture-va-playback-realtime.md).
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §3 nguyên tắc 3, §5.1 (ba tầng echo), §5.2 (ngưỡng thích ứng), §11 (mâu thuẫn về enhancement).
> **Cơ sở:** phần lý thuyết (đường echo, bộ lọc thích nghi NLMS, ERLE, double-talk, AGC, clipping) là kiến thức DSP giáo trình, không lấy từ nguồn trong wiki. Các tham số và số liệu nghiên cứu lấy từ [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md) và [Speech Enhancement Before ASR](../wiki/speech-enhancement-before-asr.md); cả hai trang đó đều dựa vào **AI report thứ cấp** và là **Reported**, chưa được kiểm chứng trên tiếng Việt. Các mô phỏng ở §7.3.4 và §7.6.2 được chạy bằng Python 3.12.3 thuần (không numpy) trong lúc viết (**Reproduced**, nhưng là **mô hình đồ chơi**: tín hiệu tổng hợp, không nhiễu đo, đường echo cố định, không phải đo trên trình duyệt hay loa thật). Code JavaScript **chưa chạy trên trình duyệt trong repo này**; hành vi AEC khác nhau theo trình duyệt, hệ điều hành và phần cứng, hãy kiểm tra trên môi trường của bạn.

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Giải thích được **echo âm học** sinh ra thế nào, vì sao AEC cần **tín hiệu tham chiếu** và vì sao nó khác hẳn khử nhiễu.
2. Hiểu bộ lọc thích nghi (NLMS) ở mức khái niệm, biết **ERLE**, **double-talk**, **độ trễ đường echo** là gì.
3. Bật, kiểm tra và hiểu giới hạn của `echoCancellation`, `noiseSuppression`, `autoGainControl` trong trình duyệt/WebRTC.
4. Phân biệt **noise suppression** (NS) với **speech enhancement** (RNNoise, DeepFilterNet), và biết vì sao enhancement có thể làm **WER tệ hơn**.
5. Hiểu AGC, loudness, headroom, và vì sao tăng gain quá tay gây clipping.
6. Thiết kế được **kiến trúc hai nhánh** (VAD/barge-in và ASR) và **ngưỡng thích ứng** theo nền nhiễu.
7. Có phương pháp **đo** hiệu quả front-end thay vì tin cảm tính.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. AEC cần tín hiệu tham chiếu nào? Double-talk là gì?
- Q2. Vì sao denoise có thể làm WER tệ hơn?
- Q3. Ba tầng xử lý echo (tắt mic, AEC trình duyệt, AEC WebRTC + so sánh tín hiệu) khác nhau thế nào?

---

## 7.1 Bức tranh tổng: ba vấn đề khác nhau, ba công cụ khác nhau

Mic trong voice agent thu được tín hiệu hỗn hợp:

```text
mic(t) = giọng người dùng (near-end)
       + echo: giọng bot phát từ loa, đi qua phòng, vào lại mic   ← tương quan với tín hiệu ta BIẾT
       + nhiễu nền: quạt, đường phố, tiếng gõ phím, người khác nói ← KHÔNG biết trước
       + méo của chuỗi thiết bị (mức quá nhỏ/quá to, clipping)
```

| Vấn đề | Công cụ | Cần tham chiếu? | Rủi ro chính |
|---|---|---|---|
| Bot nghe lại chính mình | **AEC** | **Có** (tín hiệu đang phát ra loa) | Echo dư kích hoạt barge-in giả; tự ngắt |
| Nhiễu nền ổn định/không ổn định | **NS / enhancement** | Không | Artifact làm ASR sai |
| Mức tín hiệu không ổn | **AGC / chuẩn hoá loudness** | Không | Clipping, khuếch đại nhiễu |

Lưu ý quan trọng: **echo là vấn đề dễ giải hơn nhiễu** về nguyên lý, vì ta có sẵn bản gốc của thứ cần trừ. Nhưng với voice agent, echo là vấn đề **nghiêm trọng hơn** vì nó biến bot thành người tự nói chuyện với chính mình: ASR nhận lại câu bot vừa nói, LLM trả lời lại câu đó, vòng lặp vô hạn.

Mức ưu tiên 🟡: chương này không chặn MVP half-duplex (bot nói thì tắt mic). Nhưng ngay khi muốn **barge-in** hoặc dùng **loa ngoài**, AEC trở thành bắt buộc (**Reported**: wiki ghi AEC "mandatory with loudspeakers").[^speech-enhancement]

---

## 7.2 Acoustic echo: đường loa → mic

### 7.2.1 Đường echo là một hệ tuyến tính (gần đúng)

Gọi `x(t)` là tín hiệu bot đưa ra loa (far-end). Loa phát ra không khí, âm thanh phản xạ trong phòng rồi vào mic. Về mặt tín hiệu, gần đúng:

```text
echo(t) = (h * x)(t)      h = đáp ứng xung của phòng + loa + mic ("echo path")
```

`h` gồm:

- **Trễ thuần** (delay): thời gian truyền âm + buffer phần mềm/phần cứng. Với buffer output + input điển hình, trễ vài chục đến vài trăm ms (xem [Chương 6](chuong-06-capture-va-playback-realtime.md), §6.5). Ở 16 kHz, 100 ms = 1600 mẫu.
- **Đuôi vang** (reverberation): phòng nhỏ trăm ms, phòng lớn hàng trăm ms đến hơn 1 giây. Bộ lọc phải đủ dài để phủ đuôi này.
- **Méo phi tuyến**: loa rẻ, hộp loa rung, khuếch đại bị bão hoà. AEC tuyến tính không trừ được phần này; phải có bộ **khử echo dư** (residual echo suppressor) phía sau.

### 7.2.2 Vì sao cần tín hiệu tham chiếu

NS không thể phân biệt "giọng bot trong mic" với "giọng người" vì cả hai đều là tiếng nói. Chỉ có tham chiếu `x(t)` mới cho biết "thứ này là bản dội của thứ ta vừa phát". Do đó:

- **AEC phải đứng ở nơi nó nhìn thấy cả hai**: tín hiệu mic **và** tín hiệu đang gửi ra loa.
- Trong trình duyệt, trình duyệt tự lấy tham chiếu từ audio nó phát ra (qua `<audio>`, `AudioContext.destination`, hay `RTCPeerConnection`). Nó **không** hoạt động tốt nếu bạn phát audio bằng đường mà trình duyệt không thấy (ví dụ một số cách phát qua thiết bị khác, hoặc Web Audio với `setSinkId` sang thiết bị khác tuỳ trình duyệt). Đây là nguồn bug phổ biến: **AEC bật nhưng không có tác dụng** vì không có tham chiếu đúng.
- Nếu bạn tự làm server-side AEC (hiếm), phải **căn thời gian** (time-align) chính xác giữa mic và tham chiếu: đó là lý do ở [Chương 6](chuong-06-capture-va-playback-realtime.md) có `played_sample_offset` và timestamp capture.

### 7.2.3 Hai điều kiện sống còn

1. **Căn trễ:** bộ lọc thích nghi chỉ mô hình hoá được trễ trong cửa sổ taps của nó, nên phải có bộ **ước lượng trễ** (delay estimator) trước đó. WebRTC AEC3 có phần này; clock drift giữa loa và mic phá vỡ nó (xem [Chương 6](chuong-06-capture-va-playback-realtime.md), §6.8).
2. **Đường echo ổn định tương đối:** người dùng di chuyển, mở cửa, che mic thì `h` đổi; bộ lọc phải **thích nghi lại** và trong lúc đó echo dư tăng.

---

## 7.3 Bộ lọc thích nghi và AEC: khái niệm

### 7.3.1 NLMS trong một đoạn

Bộ lọc FIR `w` ước lượng `h`. Mỗi mẫu:

```text
y(n) = w · [x(n), x(n-1), …, x(n-L+1)]        # echo ước lượng
e(n) = d(n) − y(n)                            # d = mic; e = tín hiệu sau AEC
w   ← w + μ · e(n) · x_vec / (‖x_vec‖² + δ)   # NLMS: chuẩn hoá theo năng lượng x
```

Khi `w ≈ h`, `e(n)` còn lại gần như chỉ là giọng near-end (cộng nhiễu). Điều này cũng giải thích vì sao AEC cần **tín hiệu far-end kích thích đủ phong phú**: nếu bot im lặng thì `x ≈ 0`, bộ lọc không có gì để học và cũng không có echo để trừ.

Thực tế AEC hiện đại (WebRTC AEC3, SpeexDSP) làm trong **miền tần số theo khối** (partitioned-block frequency domain), dùng nhiều bộ lọc, ước lượng coherence, **bộ phát hiện double-talk** và **bộ khử echo dư** phi tuyến. NLMS ở đây chỉ để hiểu cơ chế.

### 7.3.2 ERLE: thước đo hiệu quả

**ERLE** (Echo Return Loss Enhancement) đo mức echo giảm được:

```text
ERLE (dB) = 10·log10( E[d²] / E[e²] )     # đo khi chỉ có far-end, near-end im lặng
```

- Giá trị tham khảo thực tế: vài chục dB là tốt với echo tuyến tính; ERLE cao không đảm bảo near-end giữ nguyên chất lượng (xem double-talk).
- ERLE đo được **chỉ khi near-end im**. Nếu đo lúc người dùng nói, bạn đo lẫn cả giọng người.

### 7.3.3 Double-talk: kẻ phá hoại

**Double-talk** = người dùng và bot nói cùng lúc, chính là tình huống **barge-in**. Lúc này `e(n)` chứa giọng người, mà thuật toán thích nghi lại tưởng đó là "sai số do `w` chưa đúng", nên cập nhật `w` theo giọng người → `w` lệch khỏi `h` → echo dư tăng và/hoặc giọng người bị méo hoặc bị trừ mất.

Cách xử lý:

- **Double-talk detector (DTD):** phát hiện near-end đang nói thì **đóng băng** hoặc giảm `μ`.
- **Bộ lọc kép (two-path/foreground-background):** giữ một bộ lọc "ổn định" để xuất kết quả.
- **Giới hạn suppression:** tránh cắt cụt giọng người khi echo còn dư (đánh đổi: chấp nhận echo dư thay vì mất lời).

Đây là lý do barge-in là tác vụ khó nhất với AEC, và lý do wiki khuyến nghị thêm các **cổng bổ trợ** (thời lượng, speaker lock, so sánh với audio bot đã phát) thay vì tin tuyệt đối vào AEC (**Reported**).[^barge-in]

### 7.3.4 Mô phỏng: NLMS và double-talk (**Reproduced**, mô hình đồ chơi)

Thiết lập: 16 kHz, 4 giây; far-end là nhiễu có màu (AR(1), hệ số 0,9) làm proxy cho tiếng nói; đường echo `h` dài 64 taps, **trễ thuần 20 mẫu**, đuôi suy giảm mũ với dấu ngẫu nhiên; bộ lọc 64 taps, NLMS `μ = 0,5`; không có nhiễu đo, nên kết quả **lạc quan hơn thực tế rất nhiều**. Chỉ lấy xu hướng.

| Điều kiện | Kết quả |
|---|---|
| Chỉ far-end, ERLE 0–0,25 s | 14,6 dB |
| Chỉ far-end, ERLE 0,25–0,5 s | 44,4 dB |
| Chỉ far-end, sau 3 s | hội tụ gần như tuyệt đối (số dư ở mức sai số làm tròn số thực, bỏ qua giá trị cụ thể) |
| Double-talk từ giây 2 (sine 200 Hz biên độ 0,5 + nhiễu), **không** đóng băng thích nghi | `w` lệch: misalignment ≈ −13,5 dB (từ gần −300 dB trước đó); `e − near` có công suất gần bằng chính near-end (≈ −0,5 dB), tức tín hiệu near-end bị méo nặng |
| Double-talk, đóng băng cập nhật khi near-end nói (DTD **lý tưởng**) | `w` giữ nguyên; near-end gần như nguyên vẹn |

Bài học:

1. Thích nghi **nhanh** ở giai đoạn đầu (vài trăm ms) mới đủ tốt: câu mở đầu của bot có thể còn echo; đây là lý do hay có "bot tự ngắt ở câu đầu".
2. **Double-talk không có DTD** làm hỏng bộ lọc. DTD trong thực tế **không lý tưởng**: nó phải đoán near-end đang nói từ tín hiệu, nên có sai sót cả hai chiều.
3. Mô phỏng này không phản ánh phi tuyến, trễ biến thiên, clock drift hay ồn; nó **không** thể dùng để dự đoán số liệu của AEC thật.

---

## 7.4 AEC trong trình duyệt và WebRTC

### 7.4.1 Ba ràng buộc `getUserMedia`

```js
// Chưa chạy trên trình duyệt trong repo này; kiểm tra bằng getSettings().
const stream = await navigator.mediaDevices.getUserMedia({
  audio: {
    echoCancellation: true,   // AEC
    noiseSuppression: true,   // NS (thường của trình duyệt)
    autoGainControl: true,    // AGC
    channelCount: 1,
    // sampleRate: 16000,     // chỉ là gợi ý; thiết bị có thể từ chối
  },
});
const track = stream.getAudioTracks()[0];
console.log(track.getSettings());      // giá trị THỰC sự được áp dụng
console.log(track.getSupportedConstraints());
```

Điểm hay sai:

- Các ràng buộc ở đây là **yêu cầu**, không phải bảo đảm. Luôn đọc `getSettings()` để biết thực tế (trình duyệt có thể bỏ qua một cờ hoặc phần cứng đã xử lý sẵn).
- Với voice agent, ba cờ này được khuyến nghị bật đồng loạt cho "Tầng 2" của ba tầng echo (**Reported**).[^barge-in]
- Các cờ **ảnh hưởng nhau** và có thể thay đổi tuỳ trình duyệt/OS. Ví dụ NS và AGC của trình duyệt là các khối khác với AEC; bạn có thể bật riêng để A/B (§7.9).
- Khi `echoCancellation: true`, nhiều trình duyệt thực hiện AEC chỉ với audio mà **chính trang đó** phát. Audio phát từ tab khác hoặc ứng dụng khác thường **không** có trong tham chiếu.
- Mobile/tai nghe/loa Bluetooth: echo path và độ trễ rất khác; Bluetooth thêm trễ lớn và có thể làm AEC kém. Tai nghe có dây gần như loại bỏ echo vật lý, nên đây là cách đơn giản nhất để test không có echo.

### 7.4.2 WebRTC AEC3

Khi dùng transport WebRTC, AEC3 nằm sẵn trong pipeline xử lý audio (APM: AEC + NS + AGC + HPF). Ưu điểm: tham chiếu và căn trễ được quản lý cùng jitter buffer và playout; đó là lý do WebRTC "tự nhiên" ở Tầng 3. Chi phí: phải dựng ICE/STUN/TURN và signaling (xem Chương 8).

Nếu **WebSocket + AudioWorklet** (MVP), bạn vẫn có thể hưởng AEC của trình duyệt qua `getUserMedia`, **nhưng** chỉ khi audio bot phát ra qua đường mà trình duyệt biết. Kiểm tra thực tế: mở loa ngoài, cho bot nói và xem VAD có nổ không (§7.9.2).

### 7.4.3 Ba tầng xử lý echo

| Tầng | Cơ chế | Barge-in | Độ phức tạp | Khi nào |
|---|---|---|---|---|
| 1. Tắt mic | Ngừng gửi audio mic khi bot nói | **Không** | Thấp nhất | MVP half-duplex, môi trường yên |
| 2. AEC trình duyệt | `echoCancellation/noiseSuppression/autoGainControl = true`, VAD vẫn chạy | Có, bị giới hạn bởi chất lượng AEC | Thấp | MVP có barge-in, tai nghe hoặc loa vừa phải |
| 3. AEC WebRTC + so sánh | WebRTC AEC3 và giữ audio bot vừa phát để so sánh với mic; chỉ barge-in khi tiếng mới **khác đáng kể** audio TTS | Có, bền nhất | Cao | Production, loa ngoài, mobile |

Nguồn mô tả đúng ba tầng này (**Reported**).[^barge-in] Tầng 3 "so sánh với audio đã phát" là gợi ý ở mức ý tưởng, chưa có thuật toán cụ thể trong nguồn (**Reported**; giới hạn), nên chi tiết triển khai bên dưới là **Synthesis**:

- So sánh năng lượng/phổ: mic có mức tương quan cao với tham chiếu (đã căn trễ) thì nhiều khả năng là echo, không phải người.
- Cổng quyết định: barge-in chỉ khi **năng lượng mic vượt phần giải thích được bởi echo** một biên độ nhất định, trong ≥ N ms.

Wiki ghi nhận nguồn khuyến nghị: làm half-duplex trước, rồi mới thêm streaming TTS, `generation_id`, AEC và full-duplex barge-in (**Reported**).[^barge-in]

---

## 7.5 Noise suppression và speech enhancement

### 7.5.1 Hai họ

| Họ | Ví dụ | Nguyên lý | Đặc điểm |
|---|---|---|---|
| NS cổ điển | NS trong WebRTC APM, SpeexDSP | Ước lượng phổ nhiễu, trừ phổ (spectral subtraction), Wiener | Rất nhẹ; "musical noise" khi quá tay |
| NS bằng học máy | **RNNoise** (RNN nhẹ, chạy CPU), **DeepFilterNet 2/3**, GTCRN, DTLN | Học mặt nạ/bộ lọc theo từng băng | Hiệu quả hơn với nhiễu không ổn định; có thể tạo artifact |
| Enhancement/separation hạng nặng | MetricGAN+, SAM-Audio, ClearerVoice-Studio (FRCRN, MossFormer2), Resemble Enhance (offline) | Mô hình sinh/tách nguồn lớn | Chất lượng nghe tốt hơn nhưng nặng, thường trễ cao; không phải để realtime |

Danh sách tuỳ chọn mã nguồn mở trên là từ wiki (**Reported**); RNNoise là CPU-light, Krisp là đóng/thương mại, diarization chỉ khi có nhiều người nói.[^speech-enhancement]

### 7.5.2 Vì sao "nghe sạch hơn" không có nghĩa "ASR đọc đúng hơn"

Mục tiêu của enhancement thường tối ưu cho **tai người** (PESQ/STOI/DNSMOS). Mục tiêu của ASR là **phân biệt âm vị**. Hai mục tiêu này lệch nhau vì:

1. **Artifact:** mask học máy xoá cả thành phần yếu của tiếng nói: phụ âm xát/tắc (s, x, t, k), đuôi phụ âm cuối, năng lượng ở tần số cao. Đây chính là thứ ASR cần. Tiếng Việt có hệ phụ âm cuối (-p, -t, -c, -ch) và **thanh điệu** dựa vào đường nét F0 và độ vang (xem [Chương 5](chuong-05-ngu-am-chu-viet-va-van-ban-tieng-viet.md)); phá vỡ chúng dễ gây lỗi dấu. Đây là suy luận (**Synthesis**), chưa có nghiên cứu nào trong wiki đo trên tiếng Việt.
2. **Lệch phân phối (domain mismatch):** ASR hiện đại (Whisper và tương tự) được huấn luyện trên dữ liệu **nhiễu thật** nên có độ bền sẵn có với nhiễu; đầu vào "sạch nhân tạo" có artifact nằm ngoài phân phối nó đã thấy.
3. **Ảo giác tăng khi tín hiệu bị phá:** artifact và đoạn bị xoá dễ làm decoder tự bịa (xem [Whisper Hallucination Mitigation](../wiki/whisper-hallucination-mitigation.md)).
4. **Cộng dồn lỗi:** AEC → NS của trình duyệt → enhancement của bạn → resample → ASR: mỗi tầng thêm méo.

### 7.5.3 Bằng chứng trong wiki: mâu thuẫn, không chọn bên

(Mọi số liệu dưới đây là **Reported** và là bản thứ cấp qua AI report; paper chưa nằm trong `raw/`, chưa kiểm chứng.)[^speech-enhancement]

| Nghiên cứu | Enhancer / ASR | Kết luận |
|---|---|---|
| arXiv 2512.17562 (12/2025) | MetricGAN+ → Whisper, Parakeet, Gemini Flash 2.0, Parrotlet-a; 500 bản ghi y tế, 9 điều kiện nhiễu | Enhancement **làm tệ** ASR ở cả 40 cấu hình; semWER tăng 1,1–46,6 % tuyệt đối; Whisper ở 10 dB SNR từ 8,82 % lên 25,83 % |
| arXiv 2603.04710 | SAM-Audio → Whisper; tiếng Bengali và Anh | WER/CER **tăng** ở mọi cấu hình; ví dụ Whisper large-v3 Bengali 65,83 % → 77,35 % |
| arXiv 2403.06387 | ARN, CrossNet → ASR; CHiME-4 | Enhancement **cải thiện** ASR (3,32 % mô phỏng, 4,44 % thật khi backend huấn luyện trên tiếng sạch) |

Giải thích tương thích (**Synthesis**): hai nghiên cứu đầu dùng ASR **đã robust sẵn** (huấn luyện trên dữ liệu đa dạng) và enhancer tổng quát; nghiên cứu thứ ba dùng enhancer **được thiết kế/tinh chỉnh cho bài toán** và ASR **chưa nhìn thấy nhiễu**. Quy tắc rút ra: *enhancement có thể giúp một ASR yếu với nhiễu và có thể hại một ASR đã robust*. Không nghiên cứu nào nói về tiếng Việt, và wiki ghi điều này như giới hạn.

### 7.5.4 Quy tắc thực hành

- **Mặc định: không denoise nhánh ASR.** Đưa vào ASR audio **sau AEC**, không qua enhancement (nguyên tắc 3 trong tài liệu thiết kế).
- Denoise **nhẹ** (RNNoise/DeepFilterNet 3) chỉ ở nhánh VAD/barge-in, nơi artifact không làm mất chữ.
- Muốn bật enhancement cho ASR phải **A/B bằng WER/CER tiếng Việt** ở SNR 0/5/10/20 dB (**Reported**).[^speech-enhancement]
- Biện pháp **đòn bẩy cao hơn** denoise, theo wiki: AEC, speaker lock (ECAPA-TDNN/WeSpeaker/CAM++/TitaNet), barge-in có cổng thời lượng, gate theo confidence, danh sách đen ảo giác (**Reported**).[^speech-enhancement]

---

## 7.6 AGC, loudness và clipping

### 7.6.1 Các khái niệm

- **Biên độ và dBFS:** mẫu float trong [−1, 1]; `dBFS = 20·log10(|biên độ|)`. Sine biên độ 0,3 có RMS ≈ −13,5 dBFS (**Reproduced**, tính trong lúc viết).
- **Headroom:** khoảng cách tới 0 dBFS. Tiếng nói có **crest factor** (đỉnh/RMS) lớn (thường 12–20 dB), nên RMS −20 dBFS vẫn có đỉnh gần 0 dBFS.
- **AGC** (Automatic Gain Control): tự điều gain theo mức vào. Hai loại: **analog AGC** (chỉnh gain mic phần cứng/OS) và **digital AGC** (nhân hệ số trong APM, có limiter).
- **Chuẩn hoá loudness:** đưa mức về chuẩn (ví dụ theo RMS/LUFS) trước khi đưa vào model; thường dùng cho **file offline**, ít cần với stream realtime nếu model robust với mức.

### 7.6.2 Clipping: mô phỏng (**Reproduced**, mô hình đồ chơi)

Sine 200 Hz, biên độ gốc 0,3, nhân gain rồi **cắt cứng** ở ±1; đo méo hài tổng (THD) theo hài bậc 2–10 bằng DFT:

| Gain | Đỉnh sau gain | THD |
|---|---|---|
| 0 dB | 0,30 | 0,0 % |
| +6 dB | 0,60 | 0,0 % |
| +12 dB | 1,19 (bắt đầu cắt) | 7,1 % |
| +18 dB | 2,38 | 27,0 % |
| +24 dB | 4,75 | 37,2 % |

Bài học: méo tăng **đột ngột** khi đỉnh vượt 1,0; hài mới sinh ra không phân biệt được với âm vị thật. Clipping thường **không sửa được** sau khi đã xảy ra, vì thông tin đã mất. Tín hiệu tiếng nói thật có phổ phức tạp hơn sine, nên con số chỉ minh hoạ xu hướng.

### 7.6.3 Rủi ro của AGC với voice agent

1. **Khuếch đại nhiễu khi im lặng:** AGC tăng gain lúc không ai nói → nền ồn lên → VAD thấy "xác suất nền" cao. Đây liên quan trực tiếp đến ngưỡng thích ứng (§7.7).
2. **Pumping:** gain đổi nhanh làm mức không ổn định giữa đầu và cuối câu.
3. **Tương tác với AEC:** gain đổi làm đường echo "thay đổi" (tỷ lệ), buộc AEC thích nghi lại. Trong WebRTC APM, thứ tự xử lý được thiết kế để giảm vấn đề này; nếu bạn tự thêm AGC **trước** AEC thì dễ phá vỡ.
4. **Gain thủ công ở client:** nếu tự nhân gain trong AudioWorklet, hãy dùng **limiter** hoặc kiểm tra đỉnh trước, và ghi log số lần clipping.

Khuyến nghị (**Synthesis**): giữ `autoGainControl: true` ở Tầng 2 như wiki ghi, nhưng khi có A/B thấy VAD/ASR tệ trong phòng ồn, thử tắt riêng cờ này. Không đặt chuẩn hoá loudness nặng trong đường realtime nếu chưa đo lợi ích.

---

## 7.7 Kiến trúc hai nhánh và ngưỡng thích ứng

### 7.7.1 Hai nhánh

Từ tài liệu thiết kế (§5, sơ đồ dataflow) và wiki:[^barge-in] [^speech-enhancement]

```text
mic → [AEC của trình duyệt/WebRTC (+NS/AGC theo cờ)] ──► audio "AEC gốc"
                                                          │
                          ┌───────────────────────────────┤
                          ▼                               ▼
          [denoise nhẹ, tùy chọn]                 ASR (streaming/chunked)
                 │                                (KHÔNG enhancement)
                 ▼
        Silero VAD → endpoint/turn → barge-in gate
```

Lý do thiết kế:

- Nhánh **VAD/barge-in** cần **độ nhạy** và **ít báo động giả**; artifact vô hại vì không ai "đọc" nó.
- Nhánh **ASR** cần **độ trung thực** của phụ âm và thanh điệu.
- Nhánh VAD có thể cắt audio ra một **bản sao** (copy) trước khi denoise, tránh việc sửa tại chỗ làm ảnh hưởng nhánh ASR.

Hệ quả cần nhớ: **VAD quyết định khi nào ASR nhận audio**, nên nhánh VAD "nghe" khác ASR, và lệch này có thể gây cắt nhầm biên (đầu câu). Do đó giữ **pre-roll** và `speech_pad_ms` 100–200 ms (tài liệu thiết kế §5.2) để tránh mất phụ âm đầu.

### 7.7.2 Ngưỡng thích ứng theo nền nhiễu

Tham số khởi điểm theo wiki/tài liệu thiết kế (**Reported**, cần tune):[^barge-in]

- Đo **xác suất VAD** và **RMS** trong **2–3 giây đầu**, trước khi user nói.
- Nếu **xác suất nền trung bình > 0,3** thì nâng ngưỡng Silero lên **0,65–0,7** và nâng luôn gate barge-in.
- Mặc định `threshold = 0,5`; nâng 0,6–0,7 khi nền rất ồn.

Phác code (**chưa chạy**, chỉ minh hoạ logic; không phải code thật của repo):

```python
class AdaptiveGate:
    def __init__(self, base=0.5, noisy=0.7, calib_ms=2500, frame_ms=32):
        self.base, self.noisy = base, noisy
        self.n_calib = calib_ms // frame_ms
        self.probs, self.rms = [], []
        self.threshold = base
        self.barge_gate_ms = 300          # nâng lên 400-500 khi ồn

    def feed_calibration(self, vad_prob, frame_rms):
        if len(self.probs) < self.n_calib:
            self.probs.append(vad_prob); self.rms.append(frame_rms)
            if len(self.probs) == self.n_calib:
                self._decide()

    def _decide(self):
        mean_p = sum(self.probs) / len(self.probs)
        if mean_p > 0.3:                  # nền ồn (giá trị Reported, cần tune)
            self.threshold = self.noisy
            self.barge_gate_ms = 500
```

Cảnh báo thiết kế (**Synthesis**):

1. **Giả định 2–3 s đầu yên tĩnh** thường sai: người dùng có thể nói ngay, hoặc bot chào trước và echo lọt vào. Hãy chỉ hiệu chuẩn khi **không có bot đang phát** và không có speech rõ; nếu đang có lời nói thì **hoãn**.
2. **Nền thay đổi theo thời gian** (xe chạy qua, bật quạt): nên **cập nhật chậm** (EMA) trong các đoạn im lặng thay vì cố định một lần.
3. **Nâng ngưỡng làm giảm độ nhạy**: người nói nhỏ bị cắt. Cần đo cả **tỉ lệ bỏ sót** (miss rate) lẫn **báo động giả**.
4. Wiki ghi hai trigger window **mâu thuẫn**: ChatGPT báo cáo 100–200 ms, Claude báo cáo ≥ 300–500 ms ở ngưỡng 0,7 (reference server dùng 400 ms). Cả hai là giá trị chưa đo, cho hai ưu tiên khác nhau (đáp ứng nhanh vs. chống ngắt giả), nên chưa chọn bên (**Reported**).[^barge-in]

### 7.7.3 Các cổng bổ trợ ngoài front-end

Echo và nhiễu còn lọt qua front-end; các lớp sau chặn tiếp (**Reported**):[^barge-in]

- **Cổng thời lượng:** chặn ho, gõ phím (tiếng ngắn).
- **Speaker lock:** so cosine embedding ECAPA/CAM++ của đoạn mới với embedding người dùng; bỏ đoạn dưới ~0,5–0,6 (ngưỡng phải hiệu chuẩn trên dữ liệu của mình). Đây là cách chặn **giọng nền** (người khác nói), điều mà AEC và NS đều không làm được.
- **Backchannel:** "ừ", "vâng", "ok" khi bot nói thì **không** ngắt.
- **Soft half-duplex:** khi bot nói, nâng ngưỡng Silero lên 0,7 và đòi ≥ 300–500 ms nói liên tục; tuỳ chọn thêm ASR nhanh ≥ 2 từ khác với câu đang phát.

---

## 7.8 Nhìn từ phía lập trình: front-end ở đâu trong code

| Vị trí | Việc | Lưu ý |
|---|---|---|
| Client, `getUserMedia` | Bật AEC/NS/AGC, đọc `getSettings()` | Gửi cờ thực tế lên server để log/chẩn đoán |
| Client, AudioWorklet capture | Gắn **timestamp capture**, gửi PCM16 | Không tự thêm AGC/enhancement ở đây nếu chưa cần |
| Server, nhánh VAD | (Tuỳ chọn) RNNoise/DeepFilterNet trên bản sao, Silero VAD | Đo trễ thêm của denoise; chạy CPU |
| Server, nhánh ASR | Nhận audio AEC gốc, resample 16 kHz | Không enhancement mặc định |
| Server, barge-in gate | Cổng thời lượng, speaker lock, backchannel | Lưu `generation_id`, xem Chương 17 |

Trách nhiệm tách biệt: **front-end không quyết định turn-taking**, nó chỉ cung cấp tín hiệu sạch hơn và số đo (RMS, VAD prob) cho tầng quyết định.

---

## 7.9 Đo lường: đừng tin cảm tính

### 7.9.1 Bộ chỉ số

| Thứ cần đo | Cách đo | Ghi chú |
|---|---|---|
| **Echo lọt qua** | Cho bot phát một câu dài, người dùng im lặng, ghi mic sau AEC; tính năng lượng/ERLE | Phải làm ở **cả loa ngoài và tai nghe** |
| **Tự ngắt (false barge-in)** | Số lần VAD/barge-in kích hoạt khi chỉ bot nói | Mục tiêu 0 trong nhiều phút phát liên tục |
| **Miss rate** | Người dùng thật ngắt nhưng không được nhận | Đánh đổi với ngưỡng |
| **Tỉ lệ barge-in thành công, trễ ngắt** | Thời gian từ lúc user bắt đầu nói tới lúc audio bot dừng | Wiki: barge-in timing và endpointing là metric production |
| **WER/CER theo SNR** | Trộn nhiễu vào tập tiếng Việt ở 0/5/10/20 dB, so có/không enhancement | Đây là A/B bắt buộc trước khi bật enhancement ở nhánh ASR |
| **Tỉ lệ clipping** | Đếm mẫu |x| ≥ 0,99 | Theo từng thiết bị |

### 7.9.2 Quy trình thử nhanh

1. **Tai nghe có dây, phòng yên:** baseline không echo. Mọi lỗi ở đây là lỗi không thuộc front-end.
2. **Loa ngoài laptop, phòng yên:** bot nói câu dài. Có tự ngắt/ASR nghe lại bot không? Nếu có: kiểm tra `getSettings().echoCancellation`, đường phát audio, độ trễ.
3. **Loa ngoài + nhiễu nền phát lại** (quạt, đường phố, quán cà phê): đo false-interruption rate và miss rate.
4. **A/B enhancement:** cùng tập audio, với và không có denoise ở nhánh ASR; so WER/CER.
5. **Ghi âm lại** (ghi mic sau xử lý) trong test: nghe bằng tai và so phổ; log luôn.

Quy ước chung: ghi lại cấu hình (cờ, thiết bị, trình duyệt+phiên bản, hệ điều hành, khoảng cách), vì kết quả phụ thuộc mạnh vào chúng.

---

## 7.10 Lỗi thường gặp và cách chẩn đoán

| Triệu chứng | Nguyên nhân hay gặp | Cách kiểm tra |
|---|---|---|
| Bot tự trả lời chính nó | AEC không hoạt động (không có tham chiếu, cờ bị bỏ qua, loa Bluetooth) | `getSettings()`, ghi mic khi bot nói, thử tai nghe |
| Bot tự ngắt ở câu đầu | AEC chưa hội tụ ở vài trăm ms đầu | Thêm cổng thời lượng; bật mic sau chút ít; xem mô phỏng §7.3.4 |
| Barge-in không bao giờ nhận | AEC/suppressor cắt giọng người trong double-talk; ngưỡng quá cao | Hạ ngưỡng; test double-talk; xem cổng thời lượng |
| ASR sai nhiều dấu/phụ âm sau khi thêm denoise | Artifact của enhancement | Tắt denoise ở nhánh ASR; A/B WER |
| VAD luôn "có tiếng" | AGC nâng nền; ngưỡng thấp; quạt/ồn nền | Đo xác suất nền; ngưỡng thích ứng |
| Giọng người bị méo/rè | Clipping, AGC quá tay | Đếm clipping; tắt AGC thử |
| Echo mạnh dần theo thời gian | Clock drift hoặc đường echo đổi | Xem Chương 6 §6.8; xem lại cờ AEC |
| Lỗi chỉ ở một thiết bị/trình duyệt | AEC phụ thuộc phần cứng/OS | Log `getSettings()` và user agent |
| Giọng người nền (TV, đồng nghiệp) kích hoạt bot | AEC/NS không chặn được giọng người | Speaker lock, cổng thời lượng |

---

## 7.11 Giới hạn và điều chưa biết (đọc trước khi tin chương này)

- Tham số và số liệu nghiên cứu ở §7.5 và §7.7 là **Reported**, đến từ hai AI report thứ cấp; paper không nằm trong `raw/`, chưa được kiểm chứng ở đây. Không có nghiên cứu nào đề cập tiếng Việt.[^speech-enhancement] [^barge-in]
- Không có AEC, VAD hay đường hủy nào được triển khai hay đo ở repo này; mô phỏng ở §7.3.4 và §7.6.2 là mô hình đồ chơi.
- Hành vi AEC của trình duyệt phụ thuộc trình duyệt, hệ điều hành, thiết bị; tài liệu này không đo trên thiết bị thật.
- Các cách làm "Tầng 3" (so sánh tín hiệu với audio bot đã phát) mới ở mức ý tưởng trong nguồn; thuật toán cụ thể trong §7.4.3 là **Synthesis**.
- Mâu thuẫn trigger window (100–200 ms vs 300–500 ms) và mâu thuẫn enhancement (hại vs giúp ASR) **chưa được giải quyết**; đo trên dữ liệu của bạn.

---

## Tóm tắt chương

1. Echo, nhiễu và mức tín hiệu là **ba vấn đề khác nhau** với công cụ khác nhau; AEC là công cụ duy nhất dùng được tín hiệu tham chiếu.
2. AEC cần **tham chiếu đúng và căn trễ**; **double-talk** (chính là barge-in) là tình huống khó nhất.
3. Ba tầng echo: tắt mic → AEC trình duyệt → AEC WebRTC + so sánh với audio bot; mỗi tầng đánh đổi giữa barge-in và độ phức tạp.
4. Denoise **không phải mặc định an toàn** cho ASR: bằng chứng mâu thuẫn; chỉ dùng ở nhánh VAD/barge-in, A/B bằng WER tiếng Việt trước khi bật cho ASR.
5. AGC và gain thủ công có thể gây clipping và khuếch đại nhiễu nền; đo, đừng đoán.
6. Ngưỡng VAD thích ứng theo nền nhiễu 2–3 s đầu (nền > 0,3 thì nâng lên 0,65–0,7) là giá trị khởi điểm **Reported**, cần tune.
7. Cổng thời lượng, speaker lock và backchannel xử lý những gì front-end không xử lý được.

---

## Đáp án các câu hỏi

**Q1. AEC cần tín hiệu tham chiếu nào? Double-talk là gì?**
Tham chiếu là **tín hiệu đang gửi ra loa** (audio bot phát, far-end), được căn trễ chính xác với mic. Không có nó, hệ thống không phân biệt được giọng bot dội lại với giọng người. **Double-talk** là lúc người dùng và bot nói cùng lúc (tình huống barge-in): phần dư `e(n)` chứa giọng người, làm bộ lọc thích nghi tự cập nhật sai nếu không có detector, khiến echo dư hoặc giọng người bị méo (§7.3.3, §7.3.4).

**Q2. Vì sao denoise có thể làm WER tệ hơn?**
Vì mục tiêu của enhancement (nghe sạch) khác mục tiêu ASR (phân biệt âm vị). Enhancement có thể xoá thành phần yếu (phụ âm, đuôi từ, chi tiết thanh điệu), tạo artifact lạ, và đưa đầu vào ra ngoài phân phối mà ASR robust đã quen. Hai nghiên cứu trong wiki ghi nhận WER tăng ở mọi cấu hình, nhưng một nghiên cứu khác ghi nhận cải thiện, nên kết quả phụ thuộc cặp enhancer–ASR–dữ liệu và phải A/B (§7.5). Phần này là **Reported** và **Synthesis**, chưa kiểm trên tiếng Việt.

**Q3. Ba tầng xử lý echo khác nhau thế nào?**
Tầng 1 **tắt mic** khi bot nói: đơn giản nhưng không có barge-in. Tầng 2 **AEC của trình duyệt** qua ba cờ `getUserMedia` với VAD vẫn chạy: có barge-in, chất lượng phụ thuộc trình duyệt/thiết bị. Tầng 3 **AEC WebRTC** cộng với **so sánh audio bot vừa phát với mic** và chỉ barge-in khi tiếng mới khác đáng kể audio TTS: bền nhất, tốn công nhất (§7.4.3).

---

## Liên kết và nguồn

**Tài liệu trong repo**

- [Đề cương](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), [Chương 6](chuong-06-capture-va-playback-realtime.md), [Thiết kế pipeline](thiet-ke-pipeline-speech-to-speech-tieng-viet.md).
- Wiki: [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md), [Speech Enhancement Before ASR](../wiki/speech-enhancement-before-asr.md), [Silero VAD](../wiki/silero-vad.md), [Turn Detection Models](../wiki/turn-detection-models.md).

**Chương tiếp theo:** Chương 8. Transport mạng cho audio realtime (WebSocket, WebRTC, Opus, jitter buffer).

[^barge-in]: [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md): `## Echo-avoidance tiers` (bảng ba tầng), `## Noise-robust gating (Claude report)` (ngưỡng 0,7, 300–500 ms, ngưỡng thích ứng, speaker lock, backchannel), `## Contradictions` (cửa sổ trigger), `## Coverage and limits`. Nguồn gốc: `raw/ChatGPT-pipeline-recommend.md` §6–7 và `raw/Claude-pipeline-recommend.md` mục `Ngưỡng thích ứng`, `Barge-in và echo`.

[^speech-enhancement]: [Speech Enhancement Before ASR](../wiki/speech-enhancement-before-asr.md): `## Evidence that enhancement hurts ASR`, `## Evidence that enhancement helps ASR`, `## Practice`, `## Contradictions`, `## Coverage and limits`. Nguồn gốc: `raw/Claude-pipeline-recommend.md`, `PHẦN 1` §2 `Tiền xử lý cho môi trường ồn`.
