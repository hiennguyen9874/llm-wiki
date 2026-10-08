# Chương 3. Định dạng file, container và codec 🔴

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần I.
> **Chương trước:** [Chương 2. Số hoá âm thanh: từ sóng tới mảng số](chuong-02-so-hoa-am-thanh-tu-song-toi-mang-so.md).
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §3 nguyên tắc 4 (VieNeu `float32`/`s16le` 48 kHz, Higgs SSE base64 WAV), §5.1 (WebRTC Opus, WebSocket PCM16, telephony 8 kHz), §5.6 (giao diện TTS).
> **Cơ sở:** phần lớn là kiến thức giáo trình và đặc tả chuẩn (RIFF/WAVE, ITU-T G.711/G.722, RFC 6716 Opus, RFC 7845 Ogg Opus, đặc tả SSE của WHATWG, RFC 4648 base64), không phải claim lấy từ nguồn trong wiki. Những chỗ dẫn từ tài liệu thiết kế hoặc wiki được ghi rõ và giữ nhãn bằng chứng (**Reported**, **Synthesis**…). Hành vi mặc định của thư viện (ffmpeg, soundfile, PyAV, torchaudio, librosa…) là theo hiểu biết chung tại thời điểm viết; hãy kiểm tra lại với phiên bản bạn cài.

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Phân biệt được bốn tầng thường bị gọi chung là "định dạng audio": **sample format**, **codec**, **container** và **cách đóng gói khi truyền** (transport framing).
2. Đọc và ghi header WAV bằng tay, xử lý được WAV stream có độ dài "unknown" và WAV có chunk lạ.
3. Biết khi nào dùng raw PCM, WAV, FLAC, Opus, μ-law; tính được bitrate và kích thước mỗi frame 20 ms của từng loại.
4. Hiểu Opus đủ sâu để cấu hình: frame size, 48 kHz nội bộ, độ trễ thuật toán, FEC, DTX, PLC, và cái bẫy "Opus trong WebM của MediaRecorder".
5. Encode và decode G.711 μ-law/A-law, và giải thích vì sao phải **decode trước rồi mới resample**.
6. Viết client nhận TTS stream (HTTP chunked, SSE base64) mà không bị lệch byte, không phát nhầm header thành tiếng click.
7. Biết neural audio codec là gì và tính được bitrate token từ frame rate, số codebook và kích thước codebook.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. Raw PCM, WAV và Opus khác nhau thế nào? Khi nào dùng loại nào?
- Q2. Vì sao stream WAV qua HTTP chunked thì header có thể sai độ dài?
- Q3. G.711 μ-law là gì? Vì sao phải decode trước rồi mới resample?

---

## 3.1 Bốn tầng của "định dạng audio"

Câu "API trả về audio dạng gì?" thật ra hỏi về bốn thứ độc lập. Nhầm tầng là nguồn gốc của hầu hết bug decode.

```text
┌───────────────────────────────────────────────────────────────────────────┐
│ 4. Transport framing  binary WS frame · HTTP chunked · SSE (base64) ·     │
│                       multipart upload · RTP packet                       │
├───────────────────────────────────────────────────────────────────────────┤
│ 3. Container          WAV/RIFF · Ogg · WebM/Matroska · MP4 · (không có)   │
│                       → header, metadata, ranh giới gói, timestamp, seek  │
├───────────────────────────────────────────────────────────────────────────┤
│ 2. Codec              PCM (không nén) · FLAC · MP3 · AAC · Opus · G.711   │
│                       → cách biến sample thành bit và ngược lại           │
├───────────────────────────────────────────────────────────────────────────┤
│ 1. Sample format      s16le · f32le · u8 · mono/stereo · 16/24/48 kHz     │
│                       (Chương 2) → dạng mảng số sau khi decode            │
└───────────────────────────────────────────────────────────────────────────┘
```

| Câu hỏi | Tầng | Ví dụ trả lời |
|---|---|---|
| Sau khi decode, mảng số trông thế nào? | 1 | int16 little-endian, mono, 48 kHz |
| Bit được nén ra sao? | 2 | Opus 24 kbps VBR |
| Metadata nằm ở đâu, biên gói ở đâu? | 3 | Ogg page, có `OpusHead` |
| Byte đi qua mạng thế nào? | 4 | Mỗi WebSocket binary message là một gói Opus |

Một số tổ hợp hay gặp:

- `audio/wav` = container WAV + codec PCM + sample format ghi trong header.
- `.opus` file = container Ogg + codec Opus. Cùng codec Opus đó trong WebRTC thì **không có container**, mỗi gói đi trong một RTP packet.
- `.webm` từ `MediaRecorder` của trình duyệt = container WebM + codec Opus.
- VieNeu `response_format=pcm` = **không container**, codec PCM, s16le mono, tầng 4 là HTTP chunked hoặc SSE base64 (**Reported**, theo [VieNeu OpenAI Speech API](../wiki/vieneu-tts-openai-speech-api.md)).

Quy tắc đọc tài liệu API: tìm đủ bốn câu trả lời. Thiếu câu nào thì đó chính là chỗ cần hỏi lại hoặc đo thử, và là chỗ phải ghi vào **audio contract** (Chương 2 §2.9.3, tài liệu thiết kế §3 nguyên tắc 4).

---

## 3.2 Raw PCM: không header, phải có contract

### 3.2.1 Bản chất

Raw PCM (headerless PCM) là dãy sample nối liền, không có byte nào mô tả chính nó. Muốn đọc đúng phải biết trước **bốn tham số**: sample rate, sample format (dtype + endianness), số kênh, layout (interleaved/planar). Byte 1 giây của PCM16 mono 16 kHz và PCM16 stereo 8 kHz giống nhau về số lượng (32 000 byte), không có cách nào phân biệt chỉ bằng nhìn byte.

Tên gọi chuẩn hoá theo kiểu ffmpeg nên dùng trong contract và log:

| Tên | Nghĩa | Byte/sample |
|---|---|---|
| `s16le` | signed int16 little-endian | 2 |
| `s16be` | signed int16 big-endian | 2 |
| `s24le` | signed int24 packed little-endian | 3 |
| `s32le` | signed int32 little-endian | 4 |
| `f32le` | float32 IEEE little-endian | 4 |
| `u8` | unsigned 8-bit (0 = âm nhất, 128 = 0) | 1 |
| `mulaw` / `alaw` | G.711 (đã nén, xem §3.6), 8-bit | 1 |

### 3.2.2 Metadata đi đường khác

Vì byte không tự mô tả, metadata phải đi qua kênh khác:

- **Header HTTP:** VieNeu trả `X-Sample-Rate` cùng `200` chunked (**Reported**, [VieNeu OpenAI Speech API](../wiki/vieneu-tts-openai-speech-api.md)).
- **MIME type có tham số:** `audio/L16;rate=16000;channels=1`. Bẫy: theo RFC 2586, **L16 là big-endian** (network byte order), ngược với `s16le` của hầu hết API. Nếu một server ghi `audio/L16` mà thực ra gửi little-endian, đừng tin tên MIME, hãy kiểm tra bằng tai hoặc phổ.
- **Message điều khiển:** WebSocket gửi một JSON `{"type":"session.start","sample_rate":16000,"format":"s16le","channels":1}` trước dòng binary.
- **Cấu hình tĩnh:** ví dụ HF s2s cấu hình `--openai_tts_sample_rate` để biết PCM16 nhận về ở rate nào (**Reported**, [Speech-to-Speech OpenAI-Compatible Backends](../wiki/speech-to-speech-openai-compatible-backends.md)).

### 3.2.3 Khi nào dùng raw PCM

- **Trong process và giữa các thành phần realtime cùng máy hoặc LAN:** không tốn CPU encode/decode, độ trễ codec bằng 0, ghép và cắt ở bất kỳ biên sample nào.
- **WebSocket MVP:** tài liệu thiết kế §5.1 chọn PCM16 16 kHz mono, binary frame 20–32 ms, không base64 (**Reported**).
- **Không dùng** để lưu file (không ai đọc lại được nếu mất contract), và không dùng qua Internet di động (256 kbps cho 16 kHz mono, gấp ~10 lần Opus).

### 3.2.4 Bẫy byte lẻ

HTTP chunked, TCP và WebSocket text không đảm bảo ranh giới chunk trùng với ranh giới sample. Một chunk 1 001 byte PCM16 chứa 500 sample và **1 byte thừa** thuộc sample kế tiếp. `np.frombuffer` trên 1 001 byte sẽ báo lỗi; còn nếu cắt bỏ byte thừa thì mọi sample sau đó lệch nửa sample → **nhiễu trắng ầm ĩ** (đọc nhầm byte cao thành byte thấp). Luôn giữ phần dư (carry) giữa các chunk (code ở §3.10.1).

---

## 3.3 WAV/RIFF

### 3.3.1 Cấu trúc

WAV là container RIFF (Resource Interchange File Format, Microsoft/IBM). RIFF là dãy **chunk**, mỗi chunk = `id` 4 byte ASCII + `size` 4 byte uint32 little-endian + `size` byte dữ liệu (+ 1 byte đệm nếu `size` lẻ). WAV tối thiểu có chunk `fmt ` và chunk `data`. Header "chuẩn" 44 byte cho PCM:

| Offset | Size | Trường | Giá trị ví dụ (PCM16 mono 16 kHz) |
|---|---|---|---|
| 0 | 4 | `ChunkID` | `RIFF` |
| 4 | 4 | `ChunkSize` = tổng file − 8 | 36 + data_bytes |
| 8 | 4 | `Format` | `WAVE` |
| 12 | 4 | `Subchunk1ID` | `fmt ` (có dấu cách) |
| 16 | 4 | `Subchunk1Size` | 16 (PCM), 18 hoặc 40 với loại khác |
| 20 | 2 | `AudioFormat` (format tag) | 1 = PCM |
| 22 | 2 | `NumChannels` | 1 |
| 24 | 4 | `SampleRate` | 16000 |
| 28 | 4 | `ByteRate` = rate × block_align | 32000 |
| 32 | 2 | `BlockAlign` = channels × bits/8 | 2 |
| 34 | 2 | `BitsPerSample` | 16 |
| 36 | 4 | `Subchunk2ID` | `data` |
| 40 | 4 | `Subchunk2Size` = số byte audio | 32000 cho 1 giây |
| 44 | … | Dữ liệu sample, interleaved, little-endian | |

Format tag hay gặp:

| Tag | Tên | Ghi chú |
|---|---|---|
| `0x0001` | `WAVE_FORMAT_PCM` | Integer PCM 8/16/24/32 bit. 8-bit là **unsigned**, ≥16-bit là signed |
| `0x0003` | `WAVE_FORMAT_IEEE_FLOAT` | float32/float64 |
| `0x0006` | `WAVE_FORMAT_ALAW` | G.711 A-law |
| `0x0007` | `WAVE_FORMAT_MULAW` | G.711 μ-law |
| `0xFFFE` | `WAVE_FORMAT_EXTENSIBLE` | Format thật nằm ở 2 byte đầu của `SubFormat` GUID (offset 24 trong nội dung `fmt `); dùng khi > 2 kênh, > 16 bit hoặc cần channel mask |

### 3.3.2 Đừng giả định header luôn 44 byte

Lỗi kinh điển: `audio = np.frombuffer(wav_bytes[44:], np.int16)`. Sai khi:

- `fmt ` dài 18 hoặc 40 byte (float WAV, EXTENSIBLE).
- Có chunk khác trước `data`: `LIST` (metadata INFO, do ffmpeg/Audacity ghi), `fact` (bắt buộc với non-PCM), `bext`, `JUNK` (giữ chỗ để nâng lên RF64).
- File là RF64/W64 (WAV > 4 GiB, vì `size` là uint32).

Hậu quả: vài chục đến vài trăm byte metadata bị đọc như audio → **tiếng click hoặc "bụp" ở đầu**, và nếu số byte lệch lẻ thì cả file thành nhiễu. Cách đúng: duyệt chunk tới khi gặp `data` (§3.10.2), hoặc dùng thư viện (`soundfile`, `wave` của Python chỉ đọc integer PCM).

Ngược lại cũng sai: đưa nguyên bytes WAV vào chỗ chờ raw PCM. 44 byte header (`RIFF…WAVEfmt …`) bị phát thành một xung ~1.4 ms ở 16 kHz, nghe như tiếng click ở đầu mỗi câu. Nếu backend trả **mỗi chunk là một WAV hoàn chỉnh**, click lặp lại ở **mỗi** chunk.

### 3.3.3 WAV khi streaming: độ dài không xác định

Header WAV nằm **ở đầu** nhưng chứa **tổng độ dài**, thứ chỉ biết ở **cuối**. Writer ghi file trên đĩa giải quyết bằng cách ghi header tạm, ghi dữ liệu, rồi `seek(0)` để sửa `ChunkSize` và `Subchunk2Size`. Stream qua HTTP thì không seek lại được, nên server phải chọn một trong các cách:

| Cách | Giá trị trong header | Người đọc gặp gì |
|---|---|---|
| Đặt "rất lớn / unknown" | `0xFFFFFFFF` | Player stream (ffplay, trình duyệt) chạy ngay, dừng khi hết byte. Đây là cách VieNeu mô tả: header với độ dài "unknown" để player bắt đầu phát ngay (**Reported**) |
| Đặt 0 | `0` | Parser chặt chẽ coi file rỗng, không có tiếng |
| Ước lượng trước | Số đoán theo độ dài văn bản | Audio thật dài hơn thì bị cắt, ngắn hơn thì parser chờ mãi hoặc báo lỗi "truncated" |
| Buffer cả câu rồi mới gửi | Đúng | Mất toàn bộ lợi ích streaming, TTFA = thời gian sinh cả câu |

Quy tắc cho client của pipeline:

1. Với WAV stream, **parse header một lần** để lấy rate/kênh/dtype, sau đó **bỏ qua `data` size** và coi mọi byte sau là PCM cho tới khi stream đóng.
2. Nếu dùng `soundfile`/`wave` để đọc một WAV stream đã lưu, kết quả có thể bị cắt hoặc lỗi. Hãy "vá" header (ghi lại size đúng) trước khi lưu file để đánh giá.
3. Khi tự **phát** WAV stream (ví dụ gateway trả audio cho client cũ), dùng `0xFFFFFFFF` và ghi rõ trong contract.

### 3.3.4 Khi nào dùng WAV

- **Upload một đoạn utterance hoàn chỉnh** cho STT kiểu HTTP: HF s2s gửi WAV PCM16 mono 16 kHz trong bộ nhớ tới `/v1/audio/transcriptions` (**Reported**, [Speech-to-Speech OpenAI-Compatible Backends](../wiki/speech-to-speech-openai-compatible-backends.md)).
- **Lưu file đánh giá, log audio, dataset:** tự mô tả, mọi công cụ đọc được.
- **Stream tới client "ngây thơ"** (thẻ `<audio>`, `ffplay -i -`) cần biết format mà không có kênh metadata riêng.
- **Không** dùng WAV làm định dạng trao đổi trong vòng realtime nội bộ: header chỉ thêm rủi ro, raw PCM + contract gọn hơn.

---

## 3.4 Codec lossless: FLAC

FLAC (Free Lossless Audio Codec) nén PCM **không mất mát**: decode ra đúng từng bit như trước khi nén.

- **Nguyên lý:** dự đoán tuyến tính (linear prediction) mỗi sample từ các sample trước, rồi mã hoá phần dư (residual) bằng Rice coding. Tiếng nói dễ dự đoán nên tỉ lệ nén thường khoảng 40–60% kích thước gốc (con số kinh nghiệm, phụ thuộc nhiễu nền; audio nhiễu nhiều nén kém).
- **Cấu trúc:** marker `fLaC`, block `STREAMINFO` (rate, kênh, bit depth, tổng sample, MD5), rồi các frame độc lập (thường 4 096 sample/frame). Có `SEEKTABLE` để tua.
- **Dùng cho:** lưu dataset, log audio dài hạn, upload file lớn cho ASR batch. Hầu hết API transcription chấp nhận FLAC.
- **Không dùng cho realtime:** frame lớn (4 096 sample ở 16 kHz = 256 ms) và lợi ích băng thông (~2×) không đáng so với Opus (~10×).

Lossless có ý nghĩa với **đánh giá**: khi so ASR hay TTS, lưu tham chiếu bằng WAV/FLAC, đừng bằng MP3/Opus, để không lẫn artefact của codec vào kết quả đo (Chương 21).

---

## 3.5 Codec lossy: MP3, AAC, Opus

### 3.5.1 Nguyên lý chung của perceptual coding

Codec lossy cho âm nhạc và tiếng nói tổng quát (MP3, AAC, Opus/CELT) cùng một ý tưởng:

1. Chia tín hiệu thành frame và chuyển sang miền tần số, thường bằng **MDCT** (Modified Discrete Cosine Transform), một biến đổi có overlap giữa các frame.
2. Dùng **mô hình tâm lý âm học** (psychoacoustic model): một âm to che (mask) các âm nhỏ ở gần nó về tần số và thời gian. Phần bị che thì lượng tử thô hoặc bỏ.
3. Lượng tử và mã hoá entropy. Bitrate quyết định mức thô.

Codec chuyên cho thoại (SILK trong Opus, AMR, G.729) theo hướng khác: **mô hình nguồn** (source-filter, Chương 1) với linear prediction, chỉ gửi tham số bộ lọc thanh quản và kích thích.

Hệ quả cho pipeline:

- **Độ trễ thuật toán** (algorithmic delay) = kích thước frame + lookahead. Đây là độ trễ bắt buộc, kể cả khi CPU nhanh vô hạn.
- **Encoder delay / priming:** decoder xuất ra một đoạn sample "mồi" ở đầu. MP3 và AAC thường có vài trăm tới hơn 2 000 sample đệm. Không cắt thì audio decode lệch thời gian so với gốc (quan trọng khi căn chỉnh timestamp hoặc AEC).
- **Artefact ảnh hưởng model:** bitrate thấp làm mất dải cao, "nhoè" âm xát và tạo tiếng kim loại. ASR train trên audio sạch có thể giảm chính xác; nên đánh giá ASR trên đúng codec và bitrate sẽ dùng thật (**Synthesis**).
- **Không nối tiếp nhiều lần:** decode → xử lý → encode lại (transcoding) cộng dồn artefact. Mỗi đường audio nên chỉ qua một lần nén lossy.

### 3.5.2 MP3 và AAC (biết để nhận diện)

| | MP3 (MPEG-1 Layer III) | AAC-LC |
|---|---|---|
| Sample/frame | 1 152 | 1 024 |
| Độ trễ thực tế | Lớn (frame + bit reservoir + priming) | Lớn; biến thể AAC-LD/ELD giảm còn khoảng 15–20 ms |
| Dùng ở đâu | File, podcast, output TTS cho người dùng tải về | Video MP4, iOS/Android ghi âm (`.m4a`) |
| Vai trò trong pipeline | Input người dùng upload; **không** dùng realtime | Input upload từ mobile; **không** dùng realtime |

VieNeu không hỗ trợ `mp3`/`opus`/`aac`/`flac`: yêu cầu các format này trả về `400` (**Reported**, [VieNeu OpenAI Speech API](../wiki/vieneu-tts-openai-speech-api.md)). Nếu client cần Opus, gateway phải tự encode.

### 3.5.3 Opus

Opus (RFC 6716) là codec mặc định của WebRTC và là lựa chọn production cho audio realtime qua Internet (tài liệu thiết kế §5.1, **Reported**).

**Cấu tạo lai:**

- **SILK** (gốc từ Skype): linear prediction, giỏi cho thoại ở bitrate thấp, băng hẹp tới băng rộng.
- **CELT**: MDCT, độ trễ thấp, giỏi cho băng rộng và âm nhạc.
- **Hybrid**: SILK cho dải dưới 8 kHz, CELT cho dải trên. Encoder tự chọn chế độ theo bitrate và `application` (`VOIP`, `AUDIO`, `RESTRICTED_LOWDELAY`).

**Thông số cần thuộc:**

| Thông số | Giá trị |
|---|---|
| Sample rate API | 8, 12, 16, 24, 48 kHz. **Nội bộ và chuẩn tham chiếu là 48 kHz**; trong SDP luôn ghi `opus/48000/2` bất kể rate thật |
| Băng thông mã hoá | NB 4 kHz · MB 6 kHz · WB 8 kHz · SWB 12 kHz · FB 20 kHz |
| Frame size | 2.5, 5, 10, 20, 40, 60 ms (một packet có thể ghép nhiều frame, tối đa 120 ms) |
| Bitrate | 6–510 kbps. Thoại wideband nghe tốt từ khoảng 16–24 kbps; 32 kbps gần trong suốt cho thoại (con số kinh nghiệm) |
| Độ trễ thuật toán | Mặc định 26.5 ms với frame 20 ms (20 ms + 6.5 ms lookahead); `RESTRICTED_LOWDELAY` giảm lookahead còn 2.5 ms nhưng bỏ SILK |
| Pre-skip trong Ogg | Thường 312 sample @ 48 kHz = 6.5 ms, phải cắt bỏ khi decode file `.opus` |

**Tính năng chống mất gói:**

- **PLC** (Packet Loss Concealment): khi một gói không tới, decoder **tự sinh** đoạn audio thay thế (ngoại suy) thay vì im lặng hoặc click. Gọi decoder với "gói rỗng" để kích hoạt.
- **In-band FEC** (Forward Error Correction, LBRR của SILK): gói thứ *n* mang thêm bản mã hoá chất lượng thấp của gói *n−1*. Nếu mất gói *n−1* mà gói *n* tới, decoder khôi phục được. Cần bật ở encoder và báo tỉ lệ mất gói dự kiến; tốn thêm bitrate.
- **DTX** (Discontinuous Transmission): khi im lặng, chỉ gửi gói rất thưa → tiết kiệm băng thông. Phía nhận cần comfort noise. Lưu ý: DTX làm VAD phía server thấy "khoảng trống" giả nếu không xử lý đúng.

**Packet là đơn vị độc lập:** mỗi gói Opus bắt đầu bằng byte **TOC** (table of contents) ghi chế độ, băng thông và frame size, nên decoder biết cách giải từng gói. Tuy nhiên decoder **có state** (bộ lọc, overlap MDCT): phải decode các gói **theo thứ tự**, **một decoder cho mỗi stream**, không chia sẻ decoder giữa các session và không tạo decoder mới cho mỗi gói (tương tự resampler có state ở Chương 2 §2.8.4).

**Container của Opus:**

| Môi trường | Đóng gói | Ghi chú |
|---|---|---|
| WebRTC | RTP, 1 gói Opus / packet | Không container. Thường gói 20 ms. Jitter buffer, PLC, FEC do stack WebRTC lo (Chương 8) |
| File `.opus` / `.ogg` | Ogg pages, header `OpusHead` + `OpusTags` | Có pre-skip, granule position |
| `MediaRecorder` trình duyệt | WebM (Matroska) | **Bẫy:** chỉ chunk đầu có header khởi tạo (EBML + Tracks). Chunk sau **không tự decode được** riêng lẻ |
| Gửi qua WebSocket tự thiết kế | Gói Opus thô, mỗi message một gói | Cần contract: rate, kênh, frame size. Có thể encode bằng WebCodecs `AudioEncoder` ở trình duyệt |

Bẫy MediaRecorder rất hay gặp khi làm MVP: client gọi `recorder.start(250)`, gửi từng blob 250 ms lên server; server decode từng blob bằng ffmpeg → blob đầu chạy, các blob sau báo lỗi "invalid data". Cách sửa: hoặc nối tất cả blob thành **một** stream đưa vào **một** decoder chạy suốt session (§3.9.2), hoặc bỏ MediaRecorder, lấy PCM từ AudioWorklet (Chương 6), hoặc dùng WebRTC.

---

## 3.6 Codec thoại: G.711 μ-law/A-law, G.722

### 3.6.1 G.711: companding 8 bit

G.711 (ITU-T, 1972) là codec của mạng điện thoại số: **8 kHz, 8 bit/sample, 64 kbps**, không có frame và không có độ trễ thuật toán (từng sample mã hoá độc lập). Nó không "nén" theo kiểu MDCT mà dùng **companding** (compress + expand): lượng tử **logarit** thay vì tuyến tính.

Lý do: tiếng nói có dynamic range lớn. Lượng tử tuyến tính 8 bit chỉ cho ~48 dB (Chương 2 §2.3.2), câu nói nhỏ sẽ chìm trong nhiễu lượng tử. Lượng tử logarit dành nhiều mức cho biên độ nhỏ và ít mức cho biên độ lớn, giữ **tỉ số tín hiệu/nhiễu lượng tử gần như không đổi** trên dải rộng. Kết quả: 8 bit G.711 cho chất lượng tương đương khoảng 13–14 bit tuyến tính đối với tiếng nói.

Đường cong μ-law (Bắc Mỹ, Nhật; μ = 255), với `x` chuẩn hoá trong [−1, 1]:

```text
F(x) = sgn(x) · ln(1 + μ|x|) / ln(1 + μ)
```

A-law (châu Âu và quốc tế; A = 87.6) dùng đường cong tương tự, gồm một đoạn tuyến tính quanh 0 và đoạn logarit phía ngoài. Trong thực tế cả hai được cài bằng xấp xỉ **8 đoạn thẳng** (segment): 1 bit dấu + 3 bit segment (exponent) + 4 bit vị trí trong segment (mantissa). Thêm vài chi tiết hay làm sai:

- μ-law đảo toàn bộ bit sau khi mã hoá (`~byte`). Giá trị im lặng là `0xFF` (hoặc `0x7F`), **không phải 0**. Một buffer μ-law toàn byte `0x00` là **tín hiệu cực đại âm**, nghe như tiếng "bụp" lớn.
- A-law XOR với `0x55`. Im lặng là `0xD5`.
- Với G.711, mất đi biên độ sample tuyến tính 16 bit: μ-law mã hoá dải 14 bit, A-law 13 bit.

Ở đâu gặp G.711 trong pipeline voice agent:

- **SIP/RTP, tổng đài:** payload type 0 (PCMU = μ-law) và 8 (PCMA = A-law), gói 20 ms = **160 byte**.
- **Twilio Media Streams và các CPaaS tương tự:** gửi μ-law 8 kHz, base64 trong JSON qua WebSocket, mỗi message thường 20 ms (theo tài liệu chung của nhà cung cấp; kiểm tra lại với provider cụ thể).
- **WAV** tag 7 (μ-law) hoặc 6 (A-law).

### 3.6.2 Vì sao phải decode trước rồi mới resample

Byte μ-law là **mã logarit**, không phải biên độ. Resample là phép **tuyến tính** (lọc + nội suy, tức tổng có trọng số của các sample). Áp phép tuyến tính lên mã phi tuyến cho ra kết quả vô nghĩa:

```text
Ví dụ: hai sample liên tiếp có biên độ tuyến tính  +100   và  +8000
       byte μ-law (đã đảo bit, như trên dây)        0xF2   và  0xA0   (242 và 160)
Nội suy điểm giữa trên MÃ:      (242 + 160)/2 = 201 = 0xC9  → giải mã = +1 308
Nội suy điểm giữa trên BIÊN ĐỘ: (100 + 8000)/2             =    +4 050
```

Sai lệch lớn và phụ thuộc biên độ → méo nặng, cộng thêm việc bit dấu và bit đảo khiến nội suy giữa sample dương và âm cho giá trị nhảy lung tung → tiếng rè rất to. Thêm vào đó, nếu coi byte μ-law như `u8` hoặc `s8` tuyến tính, đường cong logarit bị "mở" sai → tín hiệu bị nén méo nặng, nhiễu nền phóng lớn.

Thứ tự đúng (tài liệu thiết kế §5.1, **Synthesis**; nhắc lại từ Chương 2):

```text
bytes μ-law 8 kHz ─► decode G.711 (bảng tra 256 phần tử) ─► int16/float32 tuyến tính 8 kHz
                  ─► resample có lọc (soxr) lên 16 kHz ─► VAD/ASR
TTS 24/48 kHz ─► resample có lọc xuống 8 kHz ─► encode G.711 ─► bytes μ-law ─► telephony
```

Chiều ngược lại cũng vậy: **resample xuống 8 kHz trước, encode μ-law sau**. Nhớ thêm: dải băng thoại là 300–3 400 Hz, nên audio ASR nhận được dù đã ở 16 kHz vẫn rỗng phía trên ~3.4 kHz (Chương 2, Q3).

### 3.6.3 G.722 và các codec thoại khác

- **G.722:** wideband 16 kHz (dải ~50–7 000 Hz), 64 kbps, dùng SB-ADPCM (chia hai băng con). Chất lượng thoại tốt hơn G.711 rõ rệt, phổ biến trong điện thoại IP "HD voice". Bẫy lịch sử: trong RTP/SDP, G.722 khai báo **clock rate 8000** dù sample rate thật là 16 kHz (do lỗi trong đặc tả cũ, giữ lại để tương thích). Timestamp RTP vì thế tăng 160 mỗi 20 ms chứ không phải 320.
- **G.729, AMR-NB, AMR-WB, EVS:** codec di động và VoIP nén mạnh (8–24 kbps). Thường gặp sau gateway của nhà mạng; pipeline nhận được bản đã chuyển sang G.711 hoặc Opus. Biết tên để nhận ra khi đọc SDP.

---

## 3.7 Đóng gói trên mạng (transport framing)

Chương 8 bàn transport (WebSocket, WebRTC). Ở đây chỉ xét **byte audio được gói thế nào** bên trong.

### 3.7.1 Binary frame

WebSocket có hai loại message: text (UTF-8) và binary. Gửi audio bằng **binary message**, mỗi message một frame audio cố định (ví dụ 20 ms PCM16 = 640 byte ở 16 kHz mono). WebSocket bảo toàn ranh giới message, nên nếu client luôn gửi đúng 640 byte thì server nhận đúng 640 byte. Vẫn nên kiểm tra `len % block_align == 0` ở biên. Metadata và event điều khiển đi bằng text message JSON xen kẽ.

### 3.7.2 Base64: thêm ~33%

Base64 (RFC 4648) biểu diễn 3 byte bằng 4 ký tự ASCII → kích thước tăng **4/3 ≈ +33.3%**, cộng padding `=` và phần JSON bao quanh. Ngoài băng thông còn tốn CPU encode/decode và tạo rác bộ nhớ (chuỗi lớn) ở tần số 50 message/giây mỗi session.

```text
len_base64 = 4 · ceil(n_bytes / 3)
20 ms PCM16 16 kHz mono:  640 B → 856 ký tự  (+34%)
20 ms μ-law 8 kHz:        160 B → 216 ký tự  (+35%)
```

Dùng base64 khi kênh **chỉ truyền được text**: SSE, JSON-RPC, API Realtime kiểu OpenAI, Twilio Media Streams. Có kênh binary thì gửi binary (tài liệu thiết kế §5.1: "Gửi binary, không dùng base64", **Reported**).

### 3.7.3 SSE (Server-Sent Events)

SSE là HTTP response `Content-Type: text/event-stream` giữ mở, server ghi các event dạng text:

```text
event: speech.audio.delta          ← tuỳ chọn
data: {"type":"speech.audio.delta","audio":"UklGRiQAAABXQVZF..."}
                                   ← dòng trống kết thúc event
data: {"type":"speech.audio.done","usage":{...}}

```

Quy tắc parse theo đặc tả: các dòng `data:` liên tiếp trong cùng event được nối bằng `\n`; event kết thúc ở dòng trống; dòng bắt đầu bằng `:` là comment (thường dùng làm heartbeat). Đừng `split("\n\n")` trên từng chunk HTTP: một event có thể bị cắt giữa hai chunk (cần buffer, code ở §3.10.3).

Trong pipeline:

- **VieNeu** `stream_format=sse`: các event `speech.audio.delta` mang base64 PCM s16le, event cuối `speech.audio.done` có `usage` (`output_samples`, `sample_rate`, `seconds`). Nếu `response_format=wav` thì event đầu tiên là **header WAV** dạng base64 (**Reported**, [VieNeu OpenAI Speech API](../wiki/vieneu-tts-openai-speech-api.md)).
- **Higgs TTS 3** với `"stream": true`: SSE mang **base64 WAV chunks** trong `audio.data` khi vocoder sinh ra, event cuối có `finish_reason: "stop"` (**Reported**, [Higgs TTS 3](../wiki/higgs-tts-3-4b.md)). Wiki không ghi rõ mỗi chunk có header WAV riêng hay chỉ chunk đầu. Client nên **kiểm tra magic `RIFF` ở đầu mỗi chunk** đã decode, nếu có thì parse và bỏ header (**Synthesis**).

### 3.7.4 HTTP chunked transfer encoding

`Transfer-Encoding: chunked` cho phép server gửi body khi chưa biết tổng độ dài: mỗi chunk gồm độ dài hex + dữ liệu. Đây là cách VieNeu (`stream_format=audio`) và MOSS/SGLang (`stream: true`, `response_format: pcm`) trả audio dần (**Reported**, [VieNeu OpenAI Speech API](../wiki/vieneu-tts-openai-speech-api.md), [MOSS-TTS-Local v1.5](../wiki/moss-tts-local-transformer-v1-5.md)).

Hai điều cần biết:

1. **Biên chunk HTTP không có ý nghĩa audio.** Proxy, gzip, HTTP/2 framing hay thư viện client (`iter_content(chunk_size=...)`) có thể gộp hoặc cắt lại. Phải xử lý byte lẻ (§3.2.4).
2. **Buffering ở giữa** phá streaming: reverse proxy (nginx `proxy_buffering on`), nén gzip, hoặc client đọc `.content` thay vì iterate đều làm audio tới thành một cục ở cuối → TTFA tăng vọt. Khi đo TTFA (Chương 20), đo ở **client cuối**, không chỉ ở server.

### 3.7.5 Multipart upload

`/v1/audio/transcriptions` kiểu OpenAI nhận `multipart/form-data` với một phần `file` (thường WAV/FLAC/MP3) và các field (`model`, `language`, `response_format`). Đây là **batch theo utterance**: thích hợp khi VAD đã cắt xong lượt nói. Nếu dùng nó để giả lập streaming (gửi lại toàn bộ utterance tích luỹ mỗi lần) thì số request và chi phí tăng theo bình phương độ dài lượt (**Reported** về việc tăng request volume, [Speech-to-Speech OpenAI-Compatible Backends](../wiki/speech-to-speech-openai-compatible-backends.md); phần "theo bình phương" là **Synthesis**).

### 3.7.6 Bảng băng thông

| Định dạng | Bitrate payload | Byte / 20 ms | Ghi chú |
|---|---|---|---|
| PCM16 mono 16 kHz | 256 kbps | 640 | MVP WebSocket |
| … qua base64 | ~341 kbps | 856 ký tự | + JSON |
| PCM16 mono 24 kHz | 384 kbps | 960 | Nhiều TTS, OpenAI Realtime |
| PCM16 mono 48 kHz | 768 kbps | 1 920 | VieNeu mặc định |
| float32 mono 48 kHz | 1 536 kbps | 3 840 | Web Audio, VieNeu SDK |
| G.711 μ-law 8 kHz | 64 kbps | 160 | Telephony |
| Opus wideband thoại | ~16–32 kbps | ~40–80 | WebRTC; thêm ~40 B header IP/UDP/RTP mỗi gói, chưa tính SRTP |

Với Opus 20 ms, header mạng (~40 byte) xấp xỉ bằng payload. Vì thế frame ngắn hơn (10 ms) giảm trễ nhưng gần như gấp đôi overhead; frame dài hơn (40–60 ms) tiết kiệm băng thông nhưng tăng trễ và khiến mỗi gói mất "đau" hơn.

---

## 3.8 Neural audio codec (giới thiệu, chi tiết ở Chương 13)

### 3.8.1 Ý tưởng

Neural audio codec là mạng **encoder → lượng tử vector → decoder** được train để tái tạo audio. Encoder biến waveform thành chuỗi vector ở **frame rate thấp** (12.5–86 Hz); mỗi vector được lượng tử thành một hoặc nhiều **token rời rạc** bằng **RVQ** (Residual Vector Quantization): codebook 1 lượng tử vector, codebook 2 lượng tử phần dư, và cứ thế. Decoder biến token ngược lại thành waveform.

Với pipeline, ý nghĩa chính **không phải nén để truyền** mà là: TTS hiện đại (và model speech-to-speech end-to-end) **sinh token codec** như LLM sinh token chữ, rồi decoder codec đóng vai trò **vocoder**. Codec quyết định sample rate đầu ra, số kênh, và độ hạt (granularity) của streaming.

### 3.8.2 Tính bitrate và độ hạt

```text
bitrate (bps)   = frame_rate × số_codebook × log2(kích_thước_codebook)
độ hạt (ms)     = 1000 / frame_rate        (audio ứng với một bước token)
samples/frame   = sample_rate / frame_rate
```

| Codec | Sample rate | Frame rate | Codebook | Bitrate | Nguồn |
|---|---|---|---|---|---|
| EnCodec 24 kHz | 24 kHz | 75 Hz (320 sample/frame) | 2–32 × 1 024 | 1.5–24 kbps | Kiến thức chung (Meta, 2022) |
| DAC 44.1 kHz | 44.1 kHz | ~86 Hz | 9 × 1 024 | ~7.7 kbps | Kiến thức chung (Descript, 2023) |
| Mimi | 24 kHz | 12.5 Hz | 8 × 2 048 (bản Moshi dùng) | ~1.1 kbps | Kiến thức chung (Kyutai, 2024); có distillation ngữ nghĩa vào codebook đầu |
| Qwen3-TTS-Tokenizer-12Hz | — | 12.5 Hz | 16 codebook, decoder causal ConvNet | Không ghi trong wiki | **Reported**, [Qwen3-TTS Tokenizer](../wiki/qwen3-tts-tokenizer-12hz.md) |
| MOSS-Audio-Tokenizer-v2 | 48 kHz **stereo** | 12.5 Hz | 12 RVQ | Không ghi trong wiki | **Reported**, [MOSS-TTS-Local v1.5](../wiki/moss-tts-local-transformer-v1-5.md) |
| Codec của Higgs TTS 3 | 24 kHz | 25 fps | 8 × 1 026 (delay pattern) | ≈ 25 × 8 × 10 ≈ 2 kbps (**Synthesis**, tính từ thông số) | **Reported**, [Higgs TTS 3](../wiki/higgs-tts-3-4b.md) |
| Codec của Audio8 TTS | 44.1 kHz | ~21.5 fps (2 048 sample/frame) | 10 × 4 096 | ≈ 21.5 × 10 × 12 ≈ 2.6 kbps (**Synthesis**) | **Reported**, [Audio8 TTS Preview](../wiki/audio8-tts-preview-0.6b.md) |

Hệ quả cho streaming (**Synthesis**):

- Frame rate 12.5 Hz → mỗi bước token = **80 ms** audio. Chunk audio đầu ra là bội số của 80 ms (thường nhiều bước gộp lại).
- Decoder **causal** (như Qwen3-TTS-Tokenizer) có thể xuất audio ngay khi có token; decoder không causal cần thêm token "tương lai" → thêm trễ.
- Codec stereo (MOSS) trả tensor `[channels, samples]`; nhưng ví dụ stream của MOSS lại pipe `-ac 1` (mono) vào ffmpeg (**Reported**). Nghĩa là "stereo" ở model và "mono" ở endpoint có thể cùng tồn tại; phải kiểm tra contract endpoint, không suy từ model card (tài liệu thiết kế §3 nguyên tắc 4).
- Một số TTS không dùng token rời rạc mà dùng **latent liên tục** (AudioVAE 48 kHz của dots.tts, VoxCPM2). Khái niệm frame rate và decoder vẫn áp dụng, chỉ không có codebook (**Reported**, [dots.tts-mf](../wiki/dots-tts-mf.md)).

Neural codec gần như **không** được dùng làm định dạng trao đổi giữa các thành phần trong pipeline cascade. Ranh giới TTS → gateway vẫn là PCM. Codec là chi tiết bên trong TTS hoặc model E2E (Chương 13, Chương 15).

---

## 3.9 Công cụ decode/encode

### 3.9.1 Bảng chọn công cụ

| Công cụ | Mạnh ở | Lưu ý |
|---|---|---|
| **ffmpeg** (CLI, subprocess) | Đọc mọi thứ, resample, đổi kênh, pipe stdin/stdout | Process riêng; probe input gây trễ; phải đọc stdout song song với ghi stdin để tránh deadlock |
| **soundfile** (libsndfile) | WAV/FLAC/Ogg-Vorbis/Ogg-Opus; bản libsndfile mới có MP3 | Trả `float64` mặc định (truyền `dtype="float32"`); không resample; cần file hoặc file-like có seek cho nhiều format |
| **PyAV** (bind libav của ffmpeg) | Decode/encode **theo packet**, trong process, có state, dùng được cho Opus/WebM stream | API thấp hơn; khác nhau giữa các phiên bản |
| **torchaudio** | Tích hợp tensor PyTorch | Các bản gần đây chuyển phần I/O sang TorchCodec; kiểm tra phiên bản trước khi dựa vào `torchaudio.load` |
| **librosa** | Phân tích | `librosa.load` mặc định **resample về 22 050 Hz và downmix mono**: luôn truyền `sr=None` hoặc `sr=16000` có chủ đích |
| **`wave`** (stdlib) | Đọc/ghi WAV integer PCM, không phụ thuộc | Không đọc float WAV (tag 3) và EXTENSIBLE phức tạp |
| **`audioop`** (stdlib cũ) | `ulaw2lin`, `lin2ulaw`, `ratecv` | **Deprecated từ Python 3.11, bị xoá ở 3.13** (PEP 594). Dùng numpy (§3.10.4) hoặc gói thay thế |
| **libopus / opuslib** | Encode/decode Opus packet thô | Dùng khi tự đóng gói Opus qua WebSocket |

### 3.9.2 Decode file khác decode stream

| | Decode file | Decode stream |
|---|---|---|
| Input | Có đủ byte, seek được | Byte tới dần, không seek |
| Header | Đọc ở đầu, có thể đọc cả trailer/index ở cuối | Chỉ có những gì đã tới; MP4 có `moov` ở cuối thì **không** stream được |
| Decoder state | Tạo, dùng, huỷ | Sống suốt session; mất state = lỗi hoặc click |
| Độ trễ | Không quan trọng | Probe/buffer của decoder cộng vào critical path |
| Lỗi giữa chừng | Báo lỗi cả file | Phải phục hồi (PLC, bỏ gói hỏng) và tiếp tục |

Ví dụ decode stream WebM/Opus từ MediaRecorder bằng **một** process ffmpeg cho mỗi session:

```bash
ffmpeg -hide_banner -loglevel error \
       -fflags nobuffer -probesize 32 -analyzeduration 0 \
       -f webm -i pipe:0 \
       -f s16le -acodec pcm_s16le -ac 1 -ar 16000 pipe:1
```

- `-f webm` khai báo format input để bỏ bước đoán; `-probesize`/`-analyzeduration` nhỏ giảm trễ khởi động.
- Output là raw PCM16 16 kHz mono: ffmpeg vừa decode vừa downmix vừa resample (có state) trong một bước.
- Phía Python ghi blob vào `stdin` và đọc `stdout` ở **hai task/thread riêng**; nếu ghi xong mới đọc, pipe đầy sẽ treo.

---

## 3.10 Code tham khảo

Các đoạn dưới đây là code minh hoạ (**Synthesis**). Đã chạy thử offline (**Reproduced**, Python 3.12 + numpy, 2026-10-07): `wav_header` cho ra 44 byte trùng với module `wave` của stdlib; `PcmAssembler` và `_AudioSink` tái tạo đúng từng sample khi stream bị cắt thành mảnh 3 hoặc 7 byte, cả ba trường hợp raw PCM, WAV stream có size `0xFFFFFFFF`, và mỗi chunk là một WAV riêng. Phần HTTP/SSE thật (httpx, server VieNeu/Higgs) **chưa** được chạy; hãy test với server thật trước khi dùng.

### 3.10.1 Ghép byte thành sample, xử lý byte lẻ

```python
import numpy as np

class PcmAssembler:
    """Nhận bytes tuỳ ý (HTTP chunk, WS message), trả mảng sample nguyên vẹn."""

    def __init__(self, dtype: str = "<i2", channels: int = 1):
        self.dtype = np.dtype(dtype)
        self.block = self.dtype.itemsize * channels   # BlockAlign
        self.channels = channels
        self.carry = b""

    def push(self, data: bytes) -> np.ndarray:
        buf = self.carry + data
        n = len(buf) - len(buf) % self.block
        self.carry = buf[n:]                          # giữ phần dư cho lần sau
        x = np.frombuffer(buf[:n], dtype=self.dtype)
        return x.reshape(-1, self.channels)           # (frames, channels), interleaved

    def close(self) -> None:
        if self.carry:
            raise ValueError(f"stream kết thúc với {len(self.carry)} byte lẻ: sai contract?")
```

### 3.10.2 Đọc và ghi header WAV

```python
import struct

WAVE_FORMAT_PCM, WAVE_FORMAT_FLOAT, WAVE_FORMAT_ALAW, WAVE_FORMAT_MULAW = 1, 3, 6, 7
WAVE_FORMAT_EXTENSIBLE = 0xFFFE
UNKNOWN = 0xFFFFFFFF

def wav_header(sample_rate: int, channels: int = 1, bits: int = 16,
               fmt_tag: int = WAVE_FORMAT_PCM, data_bytes: int = UNKNOWN) -> bytes:
    """Header 44 byte. data_bytes=UNKNOWN cho WAV stream."""
    block_align = channels * bits // 8
    riff_size = UNKNOWN if data_bytes == UNKNOWN else 36 + data_bytes
    return struct.pack("<4sI4s4sIHHIIHH4sI",
                       b"RIFF", riff_size, b"WAVE",
                       b"fmt ", 16, fmt_tag, channels, sample_rate,
                       sample_rate * block_align, block_align, bits,
                       b"data", data_bytes)

def parse_wav_header(buf: bytes):
    """Trả (fmt, data_offset) hoặc None nếu chưa đủ byte. Bỏ qua size của 'data'."""
    if len(buf) < 12:
        return None
    if buf[0:4] not in (b"RIFF", b"RF64") or buf[8:12] != b"WAVE":
        raise ValueError("không phải WAV")
    pos, fmt = 12, None
    while True:
        if len(buf) < pos + 8:
            return None
        cid = buf[pos:pos + 4]
        size = struct.unpack_from("<I", buf, pos + 4)[0]
        if cid == b"data":
            if fmt is None:
                raise ValueError("chunk 'data' xuất hiện trước 'fmt '")
            return fmt, pos + 8                  # size có thể là 0 / 0xFFFFFFFF khi stream
        if len(buf) < pos + 8 + size:
            return None                          # chunk chưa tới đủ
        if cid == b"fmt ":
            tag, ch, sr, _byte_rate, block_align, bits = struct.unpack_from("<HHIIHH", buf, pos + 8)
            if tag == WAVE_FORMAT_EXTENSIBLE and size >= 40:
                tag = struct.unpack_from("<H", buf, pos + 8 + 24)[0]   # 2 byte đầu SubFormat GUID
            fmt = {"tag": tag, "channels": ch, "sample_rate": sr,
                   "block_align": block_align, "bits": bits}
        pos += 8 + size + (size & 1)             # chunk RIFF được đệm tới số chẵn
```

Ánh xạ sang dtype numpy: tag 1 + 16 bit → `<i2`; tag 1 + 8 bit → `u1` (unsigned, trừ 128); tag 3 + 32 bit → `<f4`; tag 7 → μ-law (§3.10.4).

### 3.10.3 Client TTS stream: chunked hoặc SSE

```python
import base64, json
import httpx

async def tts_stream(url: str, body: dict, on_pcm):
    """on_pcm(np.ndarray int16 (frames, ch), sample_rate). Chấp nhận pcm, wav, SSE."""
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", url, json=body) as r:
            r.raise_for_status()
            rate = int(r.headers.get("X-Sample-Rate", body.get("sample_rate", 0)) or 0)
            ctype = r.headers.get("content-type", "")
            sink = _AudioSink(rate, on_pcm)
            if ctype.startswith("text/event-stream"):
                await _read_sse(r, sink)
            else:
                async for chunk in r.aiter_bytes():
                    sink.push(chunk)
            sink.close()

class _AudioSink:
    """Tự nhận diện header WAV ở đầu stream (hoặc đầu mỗi chunk), phần còn lại là PCM."""
    def __init__(self, rate, on_pcm):
        self.rate, self.on_pcm = rate, on_pcm
        self.head = b""            # byte chờ phân loại (có phải WAV không)
        self.asm = None

    def push(self, data: bytes, chunk_is_unit: bool = False):
        if self.asm is None or (chunk_is_unit and data[:4] == b"RIFF"):
            self.head += data
            if len(self.head) >= 4 and self.head[:4] == b"RIFF":
                parsed = parse_wav_header(self.head)
                if parsed is None:
                    return                         # chờ thêm byte
                fmt, off = parsed
                self.rate = fmt["sample_rate"]
                self.asm = self.asm or PcmAssembler("<i2", fmt["channels"])
                data, self.head = self.head[off:], b""
            elif len(self.head) >= 4 or chunk_is_unit:
                if not self.rate:
                    raise ValueError("raw PCM nhưng không biết sample rate: thiếu contract")
                self.asm = self.asm or PcmAssembler("<i2", 1)
                data, self.head = self.head, b""
            else:
                return
        x = self.asm.push(data)
        if len(x):
            self.on_pcm(x, self.rate)

    def close(self):
        if self.asm:
            self.asm.close()

async def _read_sse(r, sink: _AudioSink):
    data_lines = []
    async for line in r.aiter_lines():            # httpx ghép dòng qua biên chunk, trả "" cho dòng trống
        if line == "":                            # hết một event
            if data_lines:
                ev = json.loads("\n".join(data_lines))
                data_lines = []
                audio = ev.get("audio")              # VieNeu: chuỗi; Higgs: {"data": ...}
                b64 = audio.get("data") if isinstance(audio, dict) else audio
                if b64:
                    sink.push(base64.b64decode(b64), chunk_is_unit=True)
            continue
        if line.startswith(":"):
            continue                              # comment / heartbeat
        if line.startswith("data:"):
            data_lines.append(line[5:].lstrip(" "))
```

Điểm chính: sample rate lấy từ header WAV hoặc `X-Sample-Rate`, **không** lấy từ cấu hình mặc định; byte lẻ được giữ lại; header WAV ở đầu stream (VieNeu `wav`) hoặc ở đầu từng chunk SSE (khả năng ở Higgs) đều bị bóc ra thay vì phát thành tiếng click. Tên trường JSON (`audio` là chuỗi ở VieNeu, `audio.data` ở Higgs) là theo wiki; kiểm tra lại với server thật.

### 3.10.4 G.711 μ-law bằng numpy

```python
import numpy as np

_BIAS, _CLIP = 0x84, 32635

def _build_ulaw_decode_table() -> np.ndarray:
    u = (~np.arange(256, dtype=np.int32)) & 0xFF
    sign = u & 0x80
    exponent = (u >> 4) & 0x07
    mantissa = u & 0x0F
    mag = (((mantissa << 3) + _BIAS) << exponent) - _BIAS
    return np.where(sign != 0, -mag, mag).astype(np.int16)   # dải ±32 124

ULAW_TO_LINEAR = _build_ulaw_decode_table()

def ulaw_decode(b: bytes) -> np.ndarray:
    """bytes μ-law → int16 tuyến tính, cùng sample rate (8 kHz)."""
    return ULAW_TO_LINEAR[np.frombuffer(b, dtype=np.uint8)]

def ulaw_encode(x: np.ndarray) -> bytes:
    """int16 tuyến tính (đã resample xuống 8 kHz) → bytes μ-law."""
    x = x.astype(np.int32)
    sign = np.where(x < 0, 0x80, 0)
    mag = np.minimum(np.abs(x), _CLIP) + _BIAS                # 132 … 32 767
    exponent = np.frexp(mag)[1] - 1 - 7                       # floor(log2(mag)) − 7 ∈ [0, 7]
    mantissa = (mag >> (exponent + 3)) & 0x0F
    u = ~(sign | (exponent << 4) | mantissa) & 0xFF
    return u.astype(np.uint8).tobytes()

# Tự kiểm tra
assert ulaw_encode(np.zeros(1, np.int16)) == b"\xff"                         # im lặng = 0xFF
assert np.array_equal(ulaw_decode(ulaw_encode(ULAW_TO_LINEAR)), ULAW_TO_LINEAR)  # round-trip trên 256 mức
```

Đã chạy thử (**Reproduced**, Python 3.12 + numpy, 2026-10-07): hai assert đúng; bảng decode trùng khớp hoàn toàn với `audioop.ulaw2lin`; encode trùng `audioop.lin2ulaw` trên ~99.4% giá trị int16 được quét (bước 7), phần lệch nằm ở ranh giới làm tròn giữa hai mã kề nhau. Lưu ý mã `0x7F` và `0xFF` cùng giải ra 0, nên round-trip đúng theo giá trị chứ không theo byte. Pipeline telephony đầy đủ:

```python
pcm8k = ulaw_decode(payload).astype(np.float32) / 32768.0         # decode trước
pcm16k = stream_resampler_8k_to_16k.process(pcm8k)                # resampler có state (Ch.2 §2.8.4)
```

---

## 3.11 Bản đồ định dạng trên từng cạnh của pipeline

Tổng hợp theo tài liệu thiết kế và wiki (**Reported** cho các thông số backend; cột "Việc gateway phải làm" là **Synthesis**):

| Cạnh | Định dạng | Việc gateway phải làm |
|---|---|---|
| Browser → gateway (MVP) | WS binary PCM16 16 kHz mono, 20–32 ms | Kiểm tra `len % 2`, assembler, reblock 512 cho Silero |
| Browser → gateway (production) | WebRTC Opus 48 kHz, gói 20 ms qua RTP | Stack WebRTC decode + jitter buffer + PLC → resample 48→16 kHz một lần |
| Browser `MediaRecorder` (tránh nếu được) | WebM/Opus, chunk không độc lập | Một decoder stream cho cả session |
| Telephony → gateway | μ-law 8 kHz, base64 JSON 20 ms | base64 → G.711 decode → resample 8→16 kHz |
| Gateway → VAD | float32 16 kHz mono, cửa sổ 512 sample | Quy đổi int16 → float32 (Ch.2 §2.5.3) |
| Gateway → ASR in-process | float32 16 kHz mono numpy | — |
| Gateway → ASR HTTP (OpenAI-compat) | Multipart WAV PCM16 16 kHz mono | Ghi header 44 byte với size đúng (đã có đủ utterance) |
| Gateway → ASR Realtime (OpenAI) | PCM 24 kHz, base64 qua WS | Resample 16→24 kHz; HF s2s báo lỗi setup nếu rate khác 24 000 |
| VieNeu HTTP → gateway | `pcm` s16le mono 48 kHz (mặc định) hoặc `wav` header unknown length; chunked hoặc SSE base64 | Đọc `X-Sample-Rate`; xử lý byte lẻ; bóc header WAV |
| VieNeu SDK → gateway | float32 48 kHz | Không chia 32768 lần nữa |
| Higgs TTS 3 → gateway | SSE base64 WAV chunks, 24 kHz | Decode base64, bóc header nếu có |
| MOSS-TTS Local (SGLang) → gateway | Raw PCM 48 kHz chunked; model gốc stereo | Xác nhận số kênh thực tế của endpoint |
| HF s2s `--tts openai` | Nhận PCM16 theo `--openai_tts_sample_rate`, đổi thành khối int16 16 kHz mono 512 sample | Lưu ý: trần băng thông cả pipeline là 16 kHz |
| Gateway → browser | WS binary PCM16 ở rate gốc của TTS (khai báo trong event) hoặc WebRTC Opus | Playback queue AudioWorklet resample về rate của AudioContext |
| Gateway → telephony | μ-law 8 kHz base64 | Resample xuống 8 kHz rồi mới encode |

Nguyên tắc chung (**Synthesis**, khớp tài liệu thiết kế §3 và §5.1):

1. **Decode ở biên, xử lý bằng PCM, encode ở biên.** Bên trong gateway chỉ có PCM với contract rõ.
2. **Mỗi đường audio chỉ nén lossy một lần**, không transcode Opus → MP3 → Opus.
3. **Sample rate đi kèm dữ liệu**, không đi kèm cấu hình mặc định: lấy từ header WAV, `X-Sample-Rate`, `usage.sample_rate`, hoặc event `session.start`.
4. **Log định dạng** của mỗi cạnh lúc khởi tạo session (rate, format, kênh, container, framing) để chẩn đoán từ log.

---

## 3.12 Hướng dẫn chọn định dạng

```text
Có đang ở trong một process hoặc giữa hai service cùng máy/LAN?
 ├─ Có → raw PCM (s16le hoặc f32le) + contract.        (WAV nếu cần tự mô tả cho một utterance)
 └─ Không, đi qua Internet tới người dùng:
     ├─ Trình duyệt/mobile, cần barge-in, mạng không ổn định → WebRTC + Opus 20 ms (FEC bật).
     ├─ Prototype, mạng tốt → WebSocket binary PCM16 16 kHz (uplink) / PCM16 rate TTS (downlink).
     └─ Điện thoại PSTN/SIP → G.711 μ-law/A-law 8 kHz (do nhà mạng quyết định).

Lưu trữ / đánh giá?
 ├─ Tham chiếu chất lượng, dataset → WAV hoặc FLAC (lossless).
 └─ Log khối lượng lớn, chỉ để nghe lại → Opus trong Ogg (~24 kbps), ghi rõ là đã nén.

Kênh chỉ truyền text (SSE, JSON API)?
 └─ base64, chấp nhận +33%; giữ message nhỏ và đều (20–100 ms).
```

---

## 3.13 Lỗi kinh điển: triệu chứng → nguyên nhân → cách sửa

| Triệu chứng | Nguyên nhân hay gặp | Cách sửa |
|---|---|---|
| Tiếng "click/bụp" ngắn ở đầu mỗi câu TTS | Header WAV 44 byte bị phát như audio | Parse header (§3.10.2), hoặc yêu cầu `response_format=pcm` |
| Click lặp lại ở mỗi chunk | Server trả mỗi chunk là một WAV hoàn chỉnh | Kiểm tra `RIFF` ở mỗi chunk và bóc header |
| Nhiễu trắng ầm ĩ, thỉnh thoảng nghe ra giọng | Lệch 1 byte do byte lẻ giữa chunk; hoặc sai endianness (`audio/L16` big-endian) | Assembler giữ carry; kiểm tra endianness trong contract |
| Đọc WAV đúng nhưng đầu file có "bụp", hoặc cả file nhiễu | Cắt cứng `[44:]` trên file có `LIST`/`fact`/`fmt ` 18 byte | Duyệt chunk tới `data` |
| `soundfile` báo file hỏng hoặc chỉ đọc được 0 giây từ bản ghi TTS stream | Header WAV stream có size 0/`0xFFFFFFFF` | Vá header trước khi lưu, hoặc đọc như raw PCM sau `data` |
| Giọng chậm, trầm, hoặc nhanh, the thé | Sai rate: VieNeu trả 48 kHz nhưng phát ở 24/16 kHz (hoặc ngược lại) | Lấy rate từ `X-Sample-Rate`/header, không hard-code |
| Audio điện thoại rè cực mạnh, gần như không nghe được | Resample hoặc coi byte μ-law như PCM tuyến tính | Decode G.711 trước rồi mới resample |
| Một buffer "im lặng" μ-law phát ra tiếng bụp lớn | Điền im lặng bằng `0x00` thay vì `0xFF` | Im lặng μ-law = `0xFF`, A-law = `0xD5` |
| Blob MediaRecorder thứ hai trở đi decode lỗi | Chunk WebM không độc lập | Một decoder stream cho mỗi session |
| Audio Opus decode lệch vài ms so với gốc, AEC/timestamp sai | Không cắt pre-skip/priming | Tôn trọng `pre_skip` trong `OpusHead`; dùng decoder chuẩn |
| Tiếng "lạo xạo" kim loại ở downlink, ASR kém trên log | Bitrate Opus quá thấp hoặc transcoding nhiều lần | Tăng bitrate, chỉ nén một lần |
| TTFA đo ở server ~150 ms nhưng người dùng nghe sau ~1 s | Proxy buffer, gzip, hoặc client đọc hết body | Tắt buffering/nén cho route audio; iterate stream |
| Rác bộ nhớ, CPU cao khi nhiều session | base64 + JSON 50 lần/giây/session | Dùng binary frame nếu kênh cho phép |
| `librosa.load` cho mảng ngắn hơn mong đợi, ASR kém | Mặc định resample về 22 050 Hz | `librosa.load(path, sr=None)` hoặc `sr=16000` có chủ đích |
| `import audioop` lỗi sau khi nâng Python | `audioop` bị xoá ở Python 3.13 | Dùng numpy (§3.10.4) hoặc gói thay thế |

---

## 3.14 Thực hành

1. **Hex dump header WAV.** Ghi 1 giây tiếng nói bằng `ffmpeg -ar 16000 -ac 1 -c:a pcm_s16le a.wav`, mở bằng `xxd a.wav | head -4`. Đọc từng trường theo bảng §3.3.1. Sau đó ghi bằng Audacity, thêm metadata, và tìm chunk `LIST`.
2. **WAV stream.** `ffmpeg -i a.wav -f wav pipe:1 | xxd | head -3`: xem ffmpeg ghi gì vào các trường size khi output không seek được. Đọc lại bằng `parse_wav_header`.
3. **Click do header.** Nối 5 file WAV bằng `cat` rồi phát như raw PCM (`ffplay -f s16le -ar 16000 -ac 1 -i out.raw`). Nghe click; sau đó bóc header và so sánh.
4. **μ-law.** Encode/decode một câu bằng §3.10.4 và bằng `ffmpeg -c:a pcm_mulaw -ar 8000`. So waveform và nghe. Thử "sai cách": resample trực tiếp mảng `uint8` μ-law lên 16 kHz rồi decode, nghe kết quả.
5. **Opus.** `ffmpeg -i a.wav -c:a libopus -b:a 16k -frame_duration 20 a16.opus` với `-b:a` 8k/16k/32k/64k. So kích thước, nghe, và chạy ASR (faster-whisper `language="vi"`) để so WER/CER với bản gốc (Chương 11, 21).
6. **Base64.** Đo kích thước base64 của 20 ms PCM16 16 kHz và 20 ms μ-law; so với công thức §3.7.2.
7. **TTS stream.** Gọi VieNeu `/v1/audio/speech` với `response_format` `pcm` và `wav`, `stream_format` `audio` và `sse`. Dùng §3.10.3 lưu ra file, kiểm tra không có click, và in sample rate nhận được.
8. **MediaRecorder.** Tạo trang web ghi `recorder.start(250)`, gửi blob lên WebSocket server. Thử decode từng blob riêng (thấy lỗi), rồi thử một ffmpeg stream cho cả session (§3.9.2).

---

## 3.15 Đáp án các câu hỏi tự kiểm tra

**Q1. Raw PCM, WAV và Opus khác nhau thế nào? Khi nào dùng loại nào?**

| | Raw PCM | WAV | Opus |
|---|---|---|---|
| Tầng | Chỉ sample format, không container | Container RIFF + (thường) codec PCM | Codec lossy; container Ogg/WebM hoặc không có (RTP) |
| Tự mô tả? | Không, cần contract | Có (rate, kênh, bit, format tag) | Gói có TOC; rate/kênh nằm ở container hoặc SDP |
| Kích thước 1 s thoại 16 kHz mono | 32 000 B | 32 044 B | ~2–4 KB (16–32 kbps) |
| Độ trễ codec | 0 | 0 | ~26.5 ms mặc định (frame 20 ms + lookahead) |
| Cắt ghép | Bất kỳ biên sample nào | Như raw sau header; header gây click nếu bị phát | Theo gói; decoder có state |
| Chịu mất gói | Không | Không | PLC, FEC, DTX |
| Dùng khi | Trong process, giữa service cùng máy/LAN, WS MVP | Một utterance hoàn chỉnh (upload STT), file đánh giá, client "ngây thơ" | Qua Internet tới người dùng (WebRTC), log nén |

Tóm lại: PCM để **xử lý**, WAV để **trao đổi file có tự mô tả**, Opus để **truyền qua mạng thật** (tài liệu thiết kế §5.1: WebRTC Opus cho production, WS PCM16 cho MVP).

**Q2. Vì sao stream WAV qua HTTP chunked thì header có thể sai độ dài?**

- Header WAV nằm ở **đầu** nhưng ghi **tổng độ dài** (`ChunkSize`, `Subchunk2Size`), thứ chỉ biết khi TTS sinh xong. Ghi file thì có thể `seek(0)` để sửa; stream HTTP thì byte đầu đã gửi đi rồi, không sửa được.
- Vì vậy server streaming ghi giá trị giữ chỗ: `0xFFFFFFFF` ("unknown", như VieNeu mô tả, **Reported**), `0`, hoặc một con số ước lượng. Cả ba đều "sai" so với độ dài thật.
- Hệ quả: parser chặt chẽ có thể báo lỗi, đọc thiếu (cắt audio) hoặc chờ thêm byte; player stream thì bỏ qua và phát tới khi hết byte. Client của pipeline nên **parse header lấy format, bỏ qua size, đọc tới khi stream đóng**; khi lưu file để đánh giá thì vá lại size.
- Liên quan: nếu server trả **mỗi chunk là một WAV**, header xuất hiện giữa stream, bị phát thành click nếu không bóc.

**Q3. G.711 μ-law là gì? Vì sao phải decode trước rồi mới resample?**

- G.711 μ-law là codec thoại ITU-T: 8 kHz, **8 bit/sample lượng tử logarit** (companding với μ = 255, cài bằng 8 segment: 1 bit dấu, 3 bit exponent, 4 bit mantissa, rồi đảo bit), 64 kbps, không frame, không trễ thuật toán. Nhờ lượng tử logarit, 8 bit đạt chất lượng thoại tương đương ~13–14 bit tuyến tính. A-law là biến thể châu Âu.
- Byte μ-law là **mã phi tuyến**, không phải biên độ. Resample là phép **tuyến tính** trên biên độ (lọc, nội suy). Áp lên mã thì nội suy giữa hai mã không ra nội suy giữa hai biên độ, cộng thêm bit dấu và bit đảo → méo nặng, nghe rè (ví dụ số ở §3.6.2).
- Vì vậy: **G.711 decode (bảng 256 phần tử) → PCM tuyến tính 8 kHz → resample có lọc lên 16 kHz → VAD/ASR**. Chiều ra thì ngược lại: resample xuống 8 kHz → encode μ-law. Và nhớ rằng upsample lên 16 kHz không khôi phục dải trên 3.4–4 kHz (Chương 2, Q3).

---

## 3.16 Tóm tắt một trang

- "Định dạng audio" gồm 4 tầng độc lập: **sample format**, **codec**, **container**, **transport framing**. Contract phải trả lời đủ cả 4.
- **Raw PCM** không tự mô tả: rate/dtype/kênh đi qua header HTTP (`X-Sample-Rate`), event JSON hoặc cấu hình. `audio/L16` là big-endian. Luôn giữ **byte lẻ** giữa các chunk.
- **WAV** = RIFF chunk. Header "44 byte" chỉ là trường hợp phổ biến; hãy duyệt chunk tới `data`. Format tag 1 PCM, 3 float, 6 A-law, 7 μ-law, `0xFFFE` EXTENSIBLE. WAV stream có size `0xFFFFFFFF`/0: parse format, bỏ qua size. Header bị phát = click.
- **FLAC** lossless (~2× nén): dataset, tham chiếu đánh giá; không dùng realtime.
- **Lossy** (MP3/AAC/Opus): MDCT + tâm lý âm học; có độ trễ thuật toán và priming; chỉ nén một lần; đánh giá ASR trên đúng codec dùng thật.
- **Opus:** SILK + CELT, 48 kHz nội bộ, frame 2.5–60 ms, 6–510 kbps, trễ mặc định 26.5 ms @ 20 ms; PLC, FEC, DTX; decoder có state, một decoder mỗi stream. WebRTC dùng RTP không container; MediaRecorder dùng WebM với chunk **không độc lập**.
- **G.711:** 8 kHz, 8 bit logarit, 64 kbps, 160 byte/20 ms. Im lặng μ-law = `0xFF`. **Decode trước, resample sau**; chiều ra resample trước, encode sau. G.722 = 16 kHz nhưng RTP clock 8000.
- **Transport:** binary frame là mặc định; base64 +33% chỉ khi kênh là text (SSE, JSON); SSE parse theo dòng trống; HTTP chunked không giữ biên audio và dễ bị proxy buffer.
- **Neural codec:** encoder → RVQ token ở 12.5–86 Hz → decoder (vocoder). Bitrate = fps × codebook × log2(size). 12.5 Hz = 80 ms mỗi bước. Là chi tiết bên trong TTS/E2E, không phải định dạng trao đổi giữa các thành phần.
- **Công cụ:** ffmpeg (mọi thứ, chạy như stream), soundfile (file), PyAV (packet, có state). `librosa.load` mặc định 22 050 Hz; `audioop` đã bị xoá ở Python 3.13.
- **Nguyên tắc gateway:** decode ở biên, xử lý PCM, encode ở biên; sample rate đi kèm dữ liệu; log định dạng mọi cạnh.

## 3.17 Liên kết

**Chương sau:** Chương 4 (STFT, mel, đầu vào model), Chương 6 (capture/playback, AudioWorklet), Chương 8 (WebSocket, WebRTC, RTP, jitter buffer), Chương 13 (TTS, vocoder, neural codec chi tiết), Chương 16 (audio contract toàn pipeline), Chương 20 (đo TTFA ở client), Chương 21 (đánh giá trên đúng codec).

**Tài liệu thiết kế:** [§3 nguyên tắc 4, §5.1, §5.6](thiet-ke-pipeline-speech-to-speech-tieng-viet.md).

**Wiki:**

- [VieNeu OpenAI Speech API](../wiki/vieneu-tts-openai-speech-api.md): `pcm` s16le mono headerless; `wav` với độ dài "unknown"; chunked hoặc SSE base64 (`speech.audio.delta`/`speech.audio.done`, header WAV là event đầu khi `wav`+`sse`); `X-Sample-Rate`; `mp3`/`opus`/`aac`/`flac` → `400`.
- [Speech-to-Speech OpenAI-Compatible STT/TTS Backends](../wiki/speech-to-speech-openai-compatible-backends.md): STT upload WAV PCM16 mono 16 kHz; OpenAI Realtime cần 24 kHz; TTS nhận PCM16 thô hoặc WAV, chuyển về khối int16 16 kHz 512 sample; `stream_format=audio` chuẩn và `stream=true` của vLLM-Omni.
- [Qwen3-TTS Tokenizer 12Hz](../wiki/qwen3-tts-tokenizer-12hz.md): codec rời rạc 12.5 Hz, 16 codebook, decoder causal ConvNet.
- [Higgs TTS 3](../wiki/higgs-tts-3-4b.md): SSE base64 WAV chunks, codec 24 kHz 25 fps 8 × 1 026.
- [MOSS-TTS-Local v1.5](../wiki/moss-tts-local-transformer-v1-5.md): codec 48 kHz stereo 12 RVQ, stream PCM 48 kHz.
- [Audio8 TTS Preview 0.6B](../wiki/audio8-tts-preview-0.6b.md): codec 44.1 kHz, 2 048 sample/frame, 10 × 4 096.
- [Barge-in & Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md): vì sao WebRTC (Opus + AEC) cho production.

**Đọc thêm ngoài wiki (đặc tả và tài liệu chuẩn, gợi ý):** Microsoft *Multimedia Programming Interface and Data Specifications 1.0* (RIFF/WAVE) và tài liệu `WAVE_FORMAT_EXTENSIBLE`; EBU Tech 3306 (RF64); ITU-T G.711 và G.722; RFC 6716 (Opus), RFC 7587 (RTP payload cho Opus), RFC 7845 (Ogg Opus); RFC 3551 (RTP A/V profile, payload type 0/8/9); RFC 2586 (`audio/L16`); RFC 4648 (base64); WHATWG HTML Living Standard, mục *Server-sent events*; RFC 9112 (HTTP/1.1 chunked transfer coding); tài liệu ffmpeg (`-f s16le`, `-sample_fmts`, `libopus`); W3C MediaRecorder và WebCodecs; bài báo EnCodec (Défossez et al., 2022), DAC (Kumar et al., 2023), Moshi/Mimi (Kyutai, 2024).
