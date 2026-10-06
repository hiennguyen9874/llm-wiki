Bạn có thể kết hợp bốn mô hình thành một **voice agent dạng pipeline**:

```text
Microphone
   ↓ PCM audio
Silero VAD
   ↓ phát hiện lượt nói hoàn chỉnh
Whisper
   ↓ văn bản người dùng
Qwen3
   ↓ câu trả lời dạng text streaming
Qwen3-TTS
   ↓ audio streaming
Loa
```

## 1. Vai trò từng mô hình

- **Silero VAD v5**: xác định lúc người dùng bắt đầu và kết thúc nói; không dùng để nhận dạng nội dung.
- **Whisper**: chuyển đoạn âm thanh vừa thu được thành văn bản.
- **Qwen3**: hiểu hội thoại, gọi công cụ, tạo phản hồi.
- **Qwen3-TTS**: đọc phản hồi của Qwen3 thành giọng nói.

Whisper hỗ trợ nhận dạng giọng nói đa ngôn ngữ nhưng bản gốc hoạt động tự nhiên hơn theo từng đoạn audio hơn là token streaming thực sự. [GitHub](https://github.com/openai/whisper?utm_source=chatgpt.com) Qwen3 có cả chế độ thinking và non-thinking; với voice chat nên ưu tiên non-thinking hoặc giới hạn thinking budget để giảm độ trễ. [GitHub](https://github.com/QwenLM/Qwen3?utm_source=chatgpt.com) Qwen3-TTS được thiết kế cho TTS đa ngôn ngữ, voice cloning và streaming; báo cáo kỹ thuật công bố khả năng phát gói âm thanh đầu tiên với độ trễ rất thấp trong cấu hình phù hợp. [GitHub](https://github.com/QwenLM/Qwen3-TTS/blob/main/README.md?utm_source=chatgpt.com)

## 2. Kiến trúc sản phẩm nên dùng

```text
┌────────────── Client: Web / Mobile ───────────────┐
│ Microphone → AudioWorklet → WebSocket             │
│ Speaker    ← PCM/Opus chunks ← WebSocket          │
└──────────────────────┬────────────────────────────┘
                       │
┌──────────────────── Voice Gateway ────────────────┐
│ Session manager                                     │
│ Audio buffer                                        │
│ VAD state machine                                   │
│ Barge-in / cancel                                   │
└───────┬──────────────┬───────────────┬─────────────┘
        │              │               │
   Silero VAD      Whisper ASR      Conversation
                                         ↓
                                     Qwen3 LLM
                                         ↓ text chunks
                                     Sentence buffer
                                         ↓
                                     Qwen3-TTS
                                         ↓ audio chunks
                                      WebSocket
```

Nên tách thành các service:

```text
gateway-service
vad-service
asr-service
llm-service
tts-service
```

Với MVP chạy trên một máy, chúng có thể nằm trong cùng một Python process. Khi tải tăng, mới tách thành process hoặc container riêng.

## 3. Luồng xử lý một lượt nói

### Bước 1: Client gửi audio

Trình duyệt thu microphone dưới dạng:

```text
mono
16 kHz
PCM signed int16
frame 20–32 ms
```

Mỗi frame được gửi qua WebSocket:

```json
{
  "type": "audio",
  "sequence": 120
}
```

Phần PCM nên gửi dưới dạng binary WebSocket frame, không nên base64 vì làm tăng kích thước dữ liệu.

### Bước 2: Silero VAD phát hiện speech

Gateway giữ một state machine:

```text
IDLE
  ↓ speech probability vượt threshold
SPEAKING
  ↓ im lặng đủ lâu
END_OF_UTTERANCE
  ↓
TRANSCRIBING
```

Thông số khởi đầu hợp lý:

```python
VAD_THRESHOLD = 0.5
MIN_SPEECH_MS = 250
MIN_SILENCE_MS = 500
PRE_ROLL_MS = 200
MAX_UTTERANCE_MS = 30_000
```

`pre-roll` rất quan trọng: giữ lại khoảng 200–300 ms audio trước khi VAD báo speech để tránh mất âm tiết đầu.

Silero có thể chạy TorchScript hoặc ONNX; tài liệu dự án cho biết ONNX có thể nhanh hơn trong một số cấu hình. [GitHub](https://github.com/snakers4/silero-vad?utm_source=chatgpt.com)

### Bước 3: Gửi đoạn hoàn chỉnh sang Whisper

Khi có khoảng 500–700 ms im lặng:

```python
utterance = pre_roll_audio + speech_audio
transcript = whisper.transcribe(
    utterance,
    language="vi",
    task="transcribe",
)
```

Không nên gọi Whisper trên từng frame 20 ms. Hãy gọi theo utterance hoặc dùng cửa sổ trượt dài hơn.

Để giảm độ trễ, có thể dùng:

```text
faster-whisper / CTranslate2
Whisper small hoặc medium
FP16 trên GPU
INT8 nếu chạy CPU
```

Đây là lớp triển khai thay thế; bản thân model Whisper chính thức vẫn là nguồn model nền. [GitHub](https://github.com/openai/whisper?utm_source=chatgpt.com)

### Bước 4: Gửi transcript sang Qwen3

Prompt nên cho Qwen3 biết đầu ra sẽ được đọc thành tiếng:

```text
Bạn là trợ lý hội thoại bằng giọng nói.

Quy tắc:
- Trả lời tự nhiên, ngắn gọn.
- Không dùng Markdown phức tạp.
- Không đọc URL dài, ký hiệu hoặc bảng.
- Viết số và đơn vị theo cách dễ phát âm.
- Không mô tả quá trình suy luận.
- Mỗi câu nên tương đối ngắn.
```

Ví dụ messages:

```python
messages = [
    {
        "role": "system",
        "content": VOICE_SYSTEM_PROMPT,
    },
    *conversation_history,
    {
        "role": "user",
        "content": transcript,
    },
]
```

Đối với voice chat, nên đặt:

```text
thinking = false
temperature = 0.4–0.7
max_tokens = 200–500
stream = true
```

Qwen3 hỗ trợ nhiều kích thước dense và MoE; lựa chọn model nên dựa vào VRAM và yêu cầu độ trễ. [arXiv](https://arxiv.org/abs/2505.09388?utm_source=chatgpt.com)

## 4. Không đợi Qwen3 trả lời xong mới chạy TTS

Đây là tối ưu quan trọng nhất.

Sai:

```text
Qwen3 sinh toàn bộ 300 từ
→ Qwen3-TTS sinh toàn bộ audio
→ bắt đầu phát
```

Đúng:

```text
Qwen3 token stream
→ gom thành câu
→ gửi từng câu sang TTS
→ phát audio ngay khi câu đầu hoàn tất
```

Ví dụ:

```python
sentence_buffer = ""

async for token in qwen_stream(messages):
    sentence_buffer += token

    while has_complete_sentence(sentence_buffer):
        sentence, sentence_buffer = pop_sentence(sentence_buffer)
        await tts_queue.put(sentence)

if sentence_buffer.strip():
    await tts_queue.put(sentence_buffer)
```

Không nên cắt TTS theo từng token vì:

- âm điệu thiếu tự nhiên;
- TTS không có đủ ngữ cảnh;
- tạo quá nhiều request nhỏ;
- dễ nghe thấy khoảng ngắt.

Đơn vị tốt nhất thường là một câu hoặc khoảng 20–60 ký tự.

## 5. Pipeline async mẫu

```python
import asyncio
from dataclasses import dataclass, field


@dataclass
class VoiceSession:
    audio_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    utterance_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    text_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    tts_queue: asyncio.Queue = field(default_factory=asyncio.Queue)

    generation_id: int = 0
    assistant_speaking: bool = False


async def audio_receiver(websocket, session: VoiceSession):
    async for message in websocket:
        if isinstance(message, bytes):
            await session.audio_queue.put(message)


async def vad_worker(session: VoiceSession, vad):
    speech_buffer = bytearray()
    pre_roll = RingBuffer(milliseconds=250)
    speaking = False
    silence_ms = 0

    while True:
        pcm = await session.audio_queue.get()
        pre_roll.append(pcm)

        probability = vad.predict(pcm)

        if probability >= 0.5:
            if not speaking:
                speaking = True
                speech_buffer.extend(pre_roll.bytes())

                # Người dùng chen ngang khi bot đang nói.
                if session.assistant_speaking:
                    session.generation_id += 1

            speech_buffer.extend(pcm)
            silence_ms = 0

        elif speaking:
            speech_buffer.extend(pcm)
            silence_ms += frame_duration_ms(pcm)

            if silence_ms >= 550:
                await session.utterance_queue.put(bytes(speech_buffer))
                speech_buffer.clear()
                speaking = False
                silence_ms = 0


async def asr_worker(session: VoiceSession, whisper):
    while True:
        audio = await session.utterance_queue.get()

        text = await asyncio.to_thread(
            whisper.transcribe,
            audio,
            language="vi",
        )

        text = text.strip()
        if text:
            await session.text_queue.put(text)


async def llm_worker(session: VoiceSession, qwen, history):
    while True:
        user_text = await session.text_queue.get()
        request_generation = session.generation_id

        history.append({"role": "user", "content": user_text})
        response_text = ""
        sentence_buffer = ""

        async for token in qwen.stream(history, enable_thinking=False):
            if request_generation != session.generation_id:
                break

            response_text += token
            sentence_buffer += token

            for sentence in extract_complete_sentences(sentence_buffer):
                sentence_buffer = remove_prefix(
                    sentence_buffer, sentence
                )
                await session.tts_queue.put(
                    (request_generation, sentence)
                )

        if request_generation != session.generation_id:
            continue

        if sentence_buffer.strip():
            await session.tts_queue.put(
                (request_generation, sentence_buffer.strip())
            )

        history.append({
            "role": "assistant",
            "content": response_text,
        })


async def tts_worker(session: VoiceSession, tts, websocket):
    while True:
        generation_id, text = await session.tts_queue.get()

        if generation_id != session.generation_id:
            continue

        session.assistant_speaking = True

        async for audio_chunk in tts.stream(text):
            if generation_id != session.generation_id:
                await websocket.send_json({
                    "type": "audio_cancel",
                })
                break

            await websocket.send(audio_chunk)

        session.assistant_speaking = False
```

Đoạn trên là kiến trúc minh họa; interface thực tế của từng package sẽ khác.

## 6. Barge-in: người dùng ngắt lời bot

Một voice agent tốt phải cho phép:

```text
Bot đang nói
→ người dùng bắt đầu nói
→ dừng audio bot
→ hủy LLM/TTS cũ
→ nghe câu mới
```

Cách triển khai:

1. Client vẫn mở microphone khi bot đang phát.
2. Silero tiếp tục kiểm tra speech.
3. Khi speech probability vượt ngưỡng trong khoảng 100–200 ms:
   - tăng `generation_id`;
   - xóa TTS queue cũ;
   - gửi `audio_cancel` về client;
   - hủy request Qwen3 đang chạy nếu backend hỗ trợ;
   - bắt đầu buffer lượt nói mới.

Mọi chunk LLM và TTS phải mang theo `generation_id`:

```json
{
  "type": "audio_chunk",
  "generation_id": 42
}
```

Client bỏ qua chunk thuộc generation cũ.

## 7. Tránh bot nghe lại chính giọng của mình

Có ba phương án:

### Phương án đơn giản

Tắt gửi microphone trong lúc bot nói.

Ưu điểm: dễ làm.  
Nhược điểm: không có barge-in.

### Phương án tốt hơn

Dùng Acoustic Echo Cancellation của trình duyệt:

```javascript
navigator.mediaDevices.getUserMedia({
  audio: {
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true
  }
});
```

Sau đó vẫn dùng VAD để phát hiện người dùng chen ngang.

### Phương án production

Dùng AEC ở tầng WebRTC, đồng thời:

- lưu audio bot vừa phát;
- so sánh với microphone;
- chỉ kích hoạt barge-in khi speech mới khác đáng kể audio TTS.

WebRTC phù hợp hơn WebSocket khi cần:

- jitter buffer;
- echo cancellation;
- packet loss handling;
- truyền Opus;
- kết nối mobile ổn định.

MVP có thể dùng WebSocket; production voice call nên cân nhắc WebRTC.

## 8. Chọn model theo phần cứng

Một cấu hình MVP:

```text
Silero VAD: ONNX, CPU
Whisper: small/medium, GPU
Qwen3: 4B hoặc 8B quantized
Qwen3-TTS: 0.6B
```

Một cấu hình chất lượng cao:

```text
Silero VAD: CPU
Whisper: large-v3 hoặc biến thể tối ưu inference
Qwen3: 14B / 30B-A3B
Qwen3-TTS: 1.7B
```

Qwen3-TTS chính thức có các biến thể Base phục vụ voice cloning; repository mô tả việc truyền `ref_audio` cùng transcript `ref_text` để tạo giọng theo mẫu. [GitHub](https://github.com/QwenLM/Qwen3-TTS/blob/main/README.md?utm_source=chatgpt.com)

Nếu dùng một GPU duy nhất, không nên giữ đồng thời Whisper lớn, Qwen3 lớn và TTS lớn trên VRAM mà không đo trước. Có thể:

```text
GPU 0: Whisper + Silero
GPU 1: Qwen3
GPU 2: Qwen3-TTS
```

Hoặc với một GPU:

```text
Silero: CPU
Whisper: GPU, model nhỏ
Qwen3: llama.cpp/vLLM quantized
TTS: GPU, model 0.6B
```

## 9. API giữa các service

### ASR

```http
POST /transcribe
Content-Type: audio/wav
```

Response:

```json
{
  "text": "Thời tiết hôm nay thế nào?",
  "language": "vi",
  "duration_ms": 2130
}
```

### LLM

```http
POST /v1/chat/completions
```

Dùng Server-Sent Events hoặc streaming HTTP.

### TTS

```http
POST /synthesize
```

```json
{
  "text": "Hôm nay trời khá mát.",
  "language": "vi",
  "voice": "assistant_default",
  "stream": true
}
```

Response nên là streaming PCM hoặc Opus.

## 10. Latency mục tiêu

Một trải nghiệm tương đối tự nhiên có thể đặt ngân sách:

```text
VAD end-of-speech:       400–600 ms
Whisper:                 200–700 ms
Qwen3 first token:       100–500 ms
Tách câu đầu:            100–400 ms
TTS first audio:         100–500 ms
Network/buffering:        50–200 ms
```

Tổng từ lúc người dùng ngừng nói đến lúc nghe bot:

```text
Khoảng 1–2 giây cho MVP tốt
```

Để đạt thấp hơn, cần:

- speculative/partial ASR;
- LLM streaming;
- TTS streaming thật;
- kết nối giữ nóng;
- model luôn nằm trong VRAM;
- không load model theo request;
- tránh ghi WAV tạm ra ổ đĩa.

## 11. Những lỗi thường gặp

**Cắt câu quá sớm:** VAD thấy một khoảng nghỉ ngắn rồi gửi Whisper.  
Khắc phục: `min_silence` khoảng 500–800 ms, linh hoạt theo tốc độ nói.

**Whisper tạo chữ khi chỉ có tiếng ồn:** chỉ gọi ASR khi VAD xác nhận đủ speech; kiểm tra `no_speech_prob`, độ dài transcript và confidence. Whisper có thể tạo nội dung không có thật trong những điều kiện âm thanh xấu hoặc khoảng lặng, vì vậy không nên coi transcript là tuyệt đối chính xác trong các nghiệp vụ rủi ro cao. [GitHub](https://github.com/openai/whisper?utm_source=chatgpt.com)

**TTS đọc Markdown:** loại bỏ các ký hiệu như `#`, `**`, bảng và URL trước khi đưa vào TTS.

**Bot trả lời quá dài:** system prompt giới hạn 2–4 câu, đồng thời đặt `max_tokens`.

**Không hủy được lượt cũ:** dùng `generation_id` hoặc cancellation token xuyên suốt ASR → LLM → TTS → client.

**Âm thanh bị giật:** client nên duy trì một playback queue, không phát từng chunk ngay khi nhận được.

## 12. Stack triển khai đề xuất

```text
Frontend:
- React / Next.js
- AudioWorklet
- WebSocket hoặc WebRTC

Backend:
- Python 3.11+
- FastAPI
- asyncio
- PyTorch / ONNX Runtime

Inference:
- Silero VAD ONNX
- faster-whisper
- Qwen3 qua vLLM, SGLang hoặc llama.cpp
- Qwen3-TTS service riêng

Infrastructure:
- Redis cho session/event
- Prometheus + Grafana
- Docker Compose cho MVP
- Kubernetes khi cần scale
```

Mẫu tổ chức repository:

```text
voice-agent/
├── frontend/
├── gateway/
│   ├── websocket.py
│   ├── session.py
│   ├── vad_state.py
│   └── cancellation.py
├── services/
│   ├── asr/
│   ├── llm/
│   └── tts/
├── shared/
│   ├── protocols.py
│   └── audio.py
└── docker-compose.yml
```

Kiến trúc thực tế nên bắt đầu bằng **half-duplex MVP**: người dùng nói xong, hệ thống trả lời, chưa hỗ trợ ngắt lời. Sau khi pipeline ổn định, thêm streaming TTS, `generation_id`, AEC và full-duplex barge-in.