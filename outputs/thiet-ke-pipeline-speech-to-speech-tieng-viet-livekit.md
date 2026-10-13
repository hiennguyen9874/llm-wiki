# Thiết kế pipeline speech-to-speech tiếng Việt dùng LiveKit

> **Loại tài liệu:** thiết kế kiến trúc, deliverable trong `outputs/`, không phải tri thức canonical.
> **Phiên bản:** LiveKit v1.1 — đã bổ sung [đối chiếu docs/skills ngày 2026-10-13](doi-chieu-kien-truc-livekit-2026-10-13.md), chưa kiểm chứng runtime; nhánh thiết kế độc lập đối chiếu với [bản HF s2s](thiet-ke-pipeline-speech-to-speech-tieng-viet-hf-s2s.md) và [bản production v2 gốc](thiet-ke-pipeline-speech-to-speech-tieng-viet.md). Không sửa hay thay thế hai bản đó.
> **Ngày tra cứu:** 2026-10-13 UTC. LiveKit docs tra bằng `lk docs`; source SDK được code search trả ở commit `3f479e242428d5fa9a7208810f036bbb8ccf9a48`. Đây là reference nghiên cứu, không phải lockfile triển khai.
> **Quyết định chính:** LiveKit Server OSS cho media; LiveKit Agents Python cho orchestration; ASR/TTS/LLM nặng chạy bên ngoài worker. VAD local CPU; endpointing tiếng Việt bắt đầu bằng VAD-only, Smart Turn là extension có gate riêng.
> **Nguồn yêu cầu/model:** [Spec PoC Phase 1](spec-poc-speech-to-speech-tieng-viet.md), [ASR](lua-chon-va-thiet-ke-asr-stt-tieng-viet-realtime.md), [TTS](lua-chon-va-thiet-ke-tts-tieng-viet-realtime.md), [VAD/turn/denoise](survey-vad-turn-detection-denoise-tieng-viet.md), [cầu text → speech](survey-cau-text-to-speech-tien-hau-xu-ly-sau-llm.md).
> **Nhãn bằng chứng:** **Reported** = nguồn công bố; **Observed** = thấy trong source được tra cứu, chưa chạy; **Synthesis** = thiết kế đề xuất; **Unverified** = cần kiểm chứng; **Chốt sau PoC** = quyết định từ số đo.
> **Nhãn khả năng:** **Native** = có trong SDK/server được tra cứu; **Adapter** = code ứng dụng/plugin/service phải viết; **Spike** = cần thử tích hợp trước khi cam kết. Native không đồng nghĩa đã kiểm chứng runtime.
> **Phạm vi kiểm chứng:** chưa cài SDK, dựng server, chạy model, kiểm thử hội thoại hoặc đo latency. Đã đọc tài liệu và một số source interfaces; cấu hình, topology và release gates dưới đây là thiết kế, không phải hệ thống đã vận hành.

---

## 0. TL;DR

1. **Thay cả transport lẫn orchestrator HF bằng LiveKit Server + LiveKit Agents.** Không chạy HF turn tracker song song với AgentSession. Browser và agent là hai participant trong một room.[^lk-agents]
2. **Self-host toàn bộ:** media server, agent worker, ASR, TTS, LLM và telemetry. Không dùng LiveKit Inference hoặc Cloud-only features trong profile mặc định.
3. **Service tối thiểu:** app backend/token endpoint, LiveKit Server, Agents worker, ASR service, TTS service và LLM endpoint hiện có. VAD không cần service HTTP; turn detector cũng không mặc định cần service riêng.
4. **VAD:** Silero local CPU, prewarm model; stream/state riêng mỗi session.[^lk-vad]
5. **Tiếng Việt:** không tự chọn LiveKit turn detector mặc định. Cả audio detector hiện tại và text multilingual detector đều không liệt kê tiếng Việt; text detector đã deprecated. Baseline dùng explicit VAD-only; Smart Turn CPU ONNX là adapter/spike sau baseline.[^lk-detector]
6. **TTS 48 kHz phải cấu hình thật:** source RoomIO được tra có input/output mặc định 24 kHz. Thiết kế đặt input 16 kHz, output 48 kHz và kiểm toàn tuyến; không suy ra 48 kHz chỉ từ Opus hoặc endpoint VieNeu.[^lk-roomio]
7. **Chunker ở worker, normalizer/voice policy ở TTS service.** Một nơi sở hữu chunking; text delta không đi qua hai splitter. Custom TTS adapter là đường khuyến nghị để kiểm format/cancel/alignment.
8. **Giữ interruption/history native trước khi viết ledger mới.** LiveKit công bố truncation history và transcript theo speech khi ngắt; độ chính xác với custom TTS, normalized text và browser playback vẫn phải qua gate.[^lk-turns][^lk-text]
9. **Không fork ngay:** dùng pipeline nodes/plugins. Smart Turn chạm interface nội bộ có dấu `_`, nên phải pin SDK, có compatibility tests và fallback VAD-only.[^lk-turn-code]
10. **Latency giữ mục tiêu D1 client P50 ≤ 1.5 s, P95 ≤ 2.5 s, mềm.** Đo cùng false cutoff, interruption và overload; không coi thông số vendor là capacity.

---

## 1. Yêu cầu và phạm vi

### 1.1 Yêu cầu kế thừa

| ID | Yêu cầu | Áp dụng trong bản LiveKit |
|---|---|---|
| FR1 | Hội thoại giọng nói tiếng Việt full-duplex, người dùng ngắt lời được | Browser mic liên tục; AgentSession quản lý barge-in |
| FR2 | Browser WebRTC, AEC/NS/AGC | LiveKit Client SDK; kiểm capture constraints trên browser thật |
| FR3 | Không cắt giữa ngập ngừng, không chờ quá lâu | VAD-only baseline; Smart Turn nếu có lợi trên corpus thật |
| FR4 | LLM OpenAI-compatible, streaming, tắt thinking | Plugin Chat Completions tới host riêng |
| FR5 | Đọc đúng số, tiền, ngày, giờ, tên và viết tắt | Prompt văn nói + normalizer/lexicon theo engine |
| FR6 | Preset Bắc/Nam và clone có consent | Voice registry; client chỉ chọn voice đã được cấp quyền |
| FR7 | Thay ASR/TTS bằng config, A/B từng thành phần | Adapter contract, engine pin theo session |
| FR8 | Nhiều session | Job dispatch + session admission + model admission riêng |
| NFR1 | D1 ở client P50 ≤ 1.5 s, P95 ≤ 2.5 s | Mục tiêu mềm; report theo workload và loại lượt |
| NFR2 | Không gửi audio/text ra ngoài | OSS + local/self-host models; audit egress cả ICE/telemetry |
| NFR3 | Log mặc định content-free | Không lưu transcript/audio/prompt/tool payload mặc định |
| NFR4 | Speech node 1 GPU 24 GB; LLM ở host riêng | Capacity và GPU contention chốt sau load test |
| NFR5 | License gate | Research/commercial profile tách biệt; không né bằng đổi framework |
| NFR6 | Environment riêng cho inference nặng | Worker không load ASR/TTS/LLM weights |
| NFR7 | Warmup, readiness, deadlines, backpressure, rollback | Bắt buộc trong production profile |

Nguồn là spec và bản production/HF liên kết ở đầu tài liệu; multi-session và vận hành production là mở rộng **Synthesis**, không phải scope PoC gốc.

### 1.2 Ngoài phạm vi v1

- Một user/room, một AgentSession active phục vụ user đó. Không diarization hay meeting nhiều người trong critical path.
- Chưa telephony 8 kHz, SIP, two-pass ASR, speaker lock hoặc end-to-end speech model.
- Chưa tool gây side effect. Nếu thêm booking/payment/edit, phải thiết kế state/approval/idempotency riêng, không suy ra an toàn từ speech cancellation.
- Chưa tự migrate session đang sống giữa worker/version.
- Tài liệu này không cung cấp Docker Compose hoặc mã agent chạy được; đó là deliverable triển khai tiếp theo sau spike.

### 1.3 Hai profile, không hai orchestrator

| Chủ đề | L0 — baseline đo được | L1 — production candidate |
|---|---|---|
| Turn policy | Silero + explicit VAD-only | VAD-only đã tune hoặc Smart Turn sau gate |
| ASR | Buffered segment-final HTTP | Cùng đường HTTP; streaming chỉ khi có nhu cầu/số đo |
| TTS text | Theo câu, custom adapter mỏng | Clause chunker + normalize/mapping đã test |
| TTS audio | PCM48k từ engine, output48k explicit | Như L0 + alignment/cancel/capacity gates |
| Preemptive generation | Tắt explicit để làm baseline | Bật LLM-only sau replay; TTS preemptive mặc định tắt |
| History | Native truncation; quan sát và ghi giới hạn | Native + alignment/mapping; extension chỉ khi gate yêu cầu |
| Scale | Một session trước, sau đó load sơ bộ | Admission, bounded queues, failure/soak tests |
| Được gọi production đầy đủ? | Không | Chỉ sau §11; hiện chưa qua gate |

Smart Turn không phải điều kiện bắt buộc để gọi L1 thành công nếu VAD-only đã đạt tiêu chí endpointing của sản phẩm. Không hạ tiêu chí để né lỗi detector.

---

## 2. Quyết định kiến trúc

Mọi lựa chọn trong bảng là **Synthesis**; nền tảng Native có nguồn riêng.

| ID | Quyết định | Lý do / phương án loại |
|---|---|---|
| AD1 | Cascade STT → LLM → TTS | Thay engine tiếng Việt độc lập; chưa có end-to-end model qua gate |
| AD2 | LiveKit Server OSS + LiveKit Agents Python | Tái sử dụng media, room, dispatch, pipeline và interruption; không chỉ thay aiortc bằng SFU |
| AD3 | AgentSession là miền điều khiển lượt duy nhất | Không HF tracker/SessionActor/endpoint owner thứ hai |
| AD4 | ASR/TTS/LLM ngoài worker | Không nhân bản weights theo job/session; cách ly dependency và admission |
| AD5 | Silero CPU local, config explicit | Tránh network hop trên từng frame; không dựa vào auto-selection |
| AD6 | VAD-only cho tiếng Việt baseline | Native detectors không có vi trong danh sách hỗ trợ hiện tại |
| AD7 | Smart Turn qua streaming-detector adapter spike | Model nhận audio, không nhét vào interface detector chỉ nhận text |
| AD8 | Chunker trong worker; normalizer/voice ở TTS service | Worker có LLM stream/lifecycle; service giữ policy theo engine và trả mapping |
| AD9 | Custom TTS adapter giữ PCM48k | Không giả định plugin OpenAI tùy ý hiểu PCM source/rate khác |
| AD10 | Giữ native history/interruption; test trước extension | Không xây ledger riêng ngay và tranh quyền với native state |
| AD11 | Embedded TURN; Redis cho production | Ít service transport dư thừa; Redis bắt buộc khi LiveKit phân tán |
| AD12 | Tắt speculation L0; LLM-only L1 sau gate | Dễ xác định ordering; giảm waste và rủi ro effects |
| AD13 | OTel/metrics self-host với whitelist dữ liệu | Cloud Agent Insights không phục vụ deployment entirely self-host |
| AD14 | Pin SDK/server/client/adapters, không fork đầu tiên | Extension nhỏ, nâng cấp qua CI/canary/drain; private interfaces là rủi ro cụ thể |

Native pipeline extension points và custom STT/TTS được tài liệu hóa ở [Pipeline nodes and hooks](https://docs.livekit.io/agents/logic/nodes/).[^lk-nodes]

**Ba lớp SDK, không ba orchestrator:** `AgentServer` đăng ký/nhận jobs và quản lý job processes; `AgentSession` quản lý pipeline/media/lượt trong một cuộc hội thoại; `Agent` chứa instructions/tools/hooks và reasoning role đang active. Handoff đổi Agent trong cùng session, không cần thêm worker hay room participant.[^lk-options][^lk-handoffs]

**Không dùng Agent Builder trong profile OSS/no-egress:** Builder deploy lên Cloud, chưa hỗ trợ model plugins, workflows/handoffs/tasks và tests như SDK. Quickstart Cloud chỉ là scaffold; bản OSS bỏ enhanced noise cancellation và dùng explicit model plugins/adapters thay Inference.[^lk-start]

---

## 3. Topology và service boundaries

### 3.1 Data plane và control plane

```text
Browser
  LiveKit Client SDK + mic AEC/NS/AGC + captions
     │ HTTPS: xin room token / config đã authorize
     ▼
App backend
  auth → session admission → room/identity → agent dispatch
     │                         │
     │ token/server URL        │ Server SDK / token room_config
     ▼                         ▼
Browser ◄──── WebRTC ────► LiveKit Server OSS + embedded TURN
                                  ▲
                                  │ WebRTC: agent participant
                                  │ WS: worker đăng ký/nhận job
                           LiveKit Agents worker — CPU
                             job process / AgentSession
                               ├─ Silero VAD local
                               ├─ endpointing / optional Smart Turn
                               ├─ STT adapter ───► asr-service → engine
                               ├─ LLM plugin ────► llm-host
                               └─ clause chunker + TTS adapter
                                                   │
                                                   ▼
                                             tts-service → engine
                                             normalize / voice / mapping
```

Audio không đi qua HTTP token backend. Worker không cần public inbound port để nhận dispatch; nó chủ động đăng ký với LiveKit qua WebSocket (**Reported**). Health endpoint chỉ mở mạng riêng.[^lk-deploy]

### 3.2 Danh sách service

| Service / module | Placement | Trách nhiệm | Không làm |
|---|---|---|---|
| `app-backend` | CPU, public HTTPS | Auth, token ngắn hạn, room/voice/profile authorization, admission | Endpointing; proxy toàn bộ audio |
| `livekit-server` | CPU/network | Signaling, rooms/SFU, media, dispatch coordination, embedded TURN | ASR/TTS inference; conversation history |
| `redis` | Private CPU | Shared store/message bus cho cluster | Lưu audio/transcript mặc định; GPU semaphore tùy tiện |
| `agent-worker` | CPU | Job lifecycle, AgentSession, adapters, chunker, context, cancel/playout | Load weights speech/LLM nặng |
| `silero-vad` | Module local | Frame speech/silence, segmentation, interruption signal | Tự quyết định ý nghĩa/xác nhận business |
| `smart-turn-adapter` | Module local, optional | Audio buffer + prediction lifecycle trong session | Tự phát reply hay commit ngoài AgentSession |
| `asr-service` | Speech node | API facade, ép vi, NFC/filter, admission/deadline → engine | Sở hữu turn/history |
| `tts-service` | Speech node | Normalize/lexicon, voice/cache, mapping, admission → engine | Sở hữu hội thoại/playback/history |
| `llm-service` | Host riêng | Chat Completions streaming | Sở hữu audio turns |
| `voice/config-registry` | File/config + storage private lúc đầu | Model/version/license/voice consent/policy manifests | Tự đổi engine giữa utterance |
| `observability` | Private CPU/storage | Metrics/trace/log whitelist | Thu payload hội thoại mặc định |

Registry có thể chỉ là versioned config và encrypted object storage; không cần thêm microservice ở PoC. API facade và engine có thể cùng container/environment nếu không xung đột; vẫn giữ ranh giới logic để thay engine.

**TURN:** dùng embedded TURN trước; coturn ngoài chỉ khi có yêu cầu vận hành cụ thể. **Redis:** single-node lab có thể đơn giản hơn; bản production này đưa Redis vào topology, và multi-node LiveKit bắt buộc Redis.[^lk-server][^lk-distributed]

### 3.3 Job lifecycle

1. Backend xác thực user, authorize profile/voice và cấp identity/room riêng; giới hạn một session active theo policy.
2. Backend chọn một đường dispatch tường minh, qua `room_config` trong token hoặc Server API. Không đồng thời auto-dispatch và explicit dispatch làm hai agent vào cùng room.
3. Agent worker nhận job; khởi tạo async clients trong job event loop, pin engine/voice/policy, tạo AgentSession.
4. Link input với participant đã authorize; không mặc định nghe bất kỳ participant nào tới trước nếu room có thể có khách khác.
5. Bắt đầu media sau setup/readiness; VAD/STT nghe liên tục, reply được phát qua native session output.
6. Disconnect/timeout: đóng streams/tasks, finalize metrics, giải phóng admission lease và RAM audio; backend có TTL/reconciler cho trường hợp crash.

Token endpoint chuẩn trả `server_url` và `participant_token`; request có thể chứa `room_config` để dispatch (**Reported**). Schema client không thay quyền kiểm tra của backend: room/identity/agent/metadata/voice phải validate hoặc reject, không ký mù payload client.[^lk-auth]

---

## 4. Audio contract, browser và networking

### 4.1 Contract đề xuất

| Cạnh | Format / policy | Khả năng |
|---|---|---|
| Browser ↔ LiveKit ↔ agent | WebRTC audio track; codec/publish options được pin và kiểm | Native transport |
| RoomIO input → worker | PCM mono 16 kHz, explicit input options | Native option + kiểm runtime |
| VAD / Smart Turn | Audio mono16k; state/buffer riêng session | Native VAD / Adapter turn |
| Worker → ASR | WAV PCM `s16le` 16k mono, bounded duration | Adapter HTTP |
| LLM → chunker | Ordered UTF-8 text deltas; không raw reasoning | Native stream + Adapter filter |
| TTS service → adapter | PCM `s16le` 48k mono, framed/bounded + optional metadata | Adapter |
| RoomIO output | 48k mono explicit; không hạ băng thông qua 24/16k | Native option + conformance |
| Telephony | Ngoài scope; không suy ra support chỉ vì Silero nhận8k | Gate riêng |

**Observed:** `AudioInputOptions.sample_rate` và `AudioOutputOptions.sample_rate` trong source reference đều mặc định `24000`; `num_channels=1`. Bản này yêu cầu đặt input `16000`, output `48000` bằng RoomIO options. Đây là khả năng cấu hình, **không phải bằng chứng downlink đã giữ48k toàn tuyến**.[^lk-roomio]

Conformance phải inspect cả TTS decoder/reframer, RoomIO AudioSource và output track. Sai rate làm thay đổi tốc độ/cao độ, không chỉ chất lượng. Không hard-code số mẫu từ pipeline HF. Frame20ms tại48k có960 samples/channel; HTTP chunk boundary có thể chia giữa PCM sample, adapter phải reframe đúng.

### 4.2 Browser và AEC

- HTTPS/localhost cho mic; bật AEC/NS/AGC ở capture, kiểm thiết bị/headset/loa ngoài thật.
- Client dùng LiveKit SDK; captions qua transcription streams, không giữ protocol `oai-events` của HF. Dùng text stream handlers/`useTranscriptions`, không `TranscriptionReceived` hay `useTrackTranscriptions` đã deprecated. Upsert interim/final theo identity/track/`lk.segment_id`, replace khi `lk.transcription_final=true`; catch stream abort/reconnect, không append thành hai lượt.[^lk-text]
- Worker Python cũng có built-in AGC. L0 đặt `AudioInputOptions.auto_gain_control=False` explicit làm điểm đo với browser AGC bật; A/B bật worker AGC nếu cần, không giả hai tầng luôn tốt hơn. Đây là policy **Synthesis**, không default SDK. Source tự disable AGC khi noise cancellation được cấu hình trực tiếp nếu không override.[^lk-audio][^lk-roomio]
- L0 voice-only đặt `RoomOptions.text_input=False`, giữ text output/captions. SDK bật text input mặc định; `lk.chat` từ linked participant có thể interrupt và tạo reply. Hybrid chat là profile opt-in, phải test ordering/audio-text paths, không chỉ ẩn textbox ở UI.[^lk-text]
- Không tự viết AudioWorklet playback thứ hai ở baseline cạnh native audio track. Harness PCM riêng có thể phục vụ đo offline nhưng không chứng minh browser WebRTC parity.
- Barge-in có đuôi network/jitter/device buffer; không tuyên bố clear phía server xóa audio đã tới thiết bị.
- Transcript hiển thị là dữ liệu UI, không tự động đồng nghĩa dữ liệu được lưu vào log hoặc bằng chứng đã nghe.

Native transcript topic là `lk.transcription`; text input là `lk.chat`; sync transcription và truncation khi interruption được tài liệu hóa (**Reported**).[^lk-text]

**Frontend lifecycle:** ưu tiên frontend `Session` + endpoint/custom `TokenSource` khi client version pin hỗ trợ; lower-level `Room.connect` vẫn hợp lệ. Frontend Session không phải Python AgentSession. Backend authorize token/room_config, giữ một đường dispatch; không dùng Cloud sandbox token server trong no-egress profile. Observe agent state (`lk.agent.state`/Session APIs) để hiển thị UI, không tắt mic khi bot speaking vì FR1 full-duplex.[^lk-frontends]

**Pre-connect audio:** docs có instant connect gửi buffer qua `lk.agent.pre-connect-audio-buffer`; source worker mặc định nhận buffer. L0 tắt client buffering và `AudioInputOptions.pre_connect_audio=False` để baseline dễ replay. Chỉ bật sau consent, bounded timeout và gate không mất/nhân đôi opening speech; không dùng buffer này như endpoint owner thứ hai.[^lk-audio][^lk-roomio]

48k là sample-rate contract, không chứng minh codec bitrate/bandwidth hay thiết bị phát giữ toàn bộ phổ; conformance phải đo cả capture/encode/decode/playout.

### 4.3 ICE, STUN/TURN và privacy

LiveKit có embedded TURN, TURN/TLS cần domain/certificate phù hợp; reverse proxy HTTPS không thay cho UDP media hay L4 TURN routing.[^lk-server]

- Chỉ advertise ICE/STUN/TURN thuộc hạ tầng được phép. Không thêm public STUN trong browser config.
- **Audit server nữa:** tài liệu `rtc.use_external_ip: true` mô tả dùng STUN để khám phá IP. Không sao chép config này trước khi xác nhận destination STUN hoặc phương án advertise IP trên version pin.
- Kiểm candidates và packet/network egress từ cả browser, server, worker; TURN failover qua mạng chặn UDP phải test.
- Chỉ app HTTPS, signaling/media/TURN cần lộ ra ngoài; Redis/model APIs/health/OTel giữ private.
- Pin server config theo release thật; không coi một port list duy nhất đúng cho mọi topology/LB.

---

## 5. VAD, endpointing và turn detector tiếng Việt

### 5.1 Silero VAD local

Silero plugin chạy local CPU; supports8/16k và prewarm hook (**Reported**).[^lk-vad]

- Dùng explicit Silero plugin/config để baseline ổn định, không dựa vào bundled default thay đổi theo SDK.
- Prewarm model qua hook đúng version. Mỗi session tạo stream/state riêng; không share mutable recurrent state giữa user.
- Không gọi HTTP service trên từng VAD frame.
- Không chạy blocking ONNX hoặc generator trên event loop. Nếu inference gây lag, executor/process bounded và đo queue wait.
- Prewarm model read-only qua `AgentServer.setup_fnc`, dùng lại `ctx.proc.userdata` trong job. Docs mô tả warm **job processes** trước khi nhận job; không giả mọi resource được parent worker load đúng một lần rồi chia sẻ. `num_idle_processes` phải pin theo RAM/startup budget. SDK forkserver preload là cơ chế riêng, khác setup hook.[^lk-options][^lk-preload]
- Async HTTP clients tạo trong job loop. Không tạo client gắn event loop trước khi job chạy.
- Explicit VAD-only không bảo đảm SDK bỏ preload local EOT. Source reference có `LIVEKIT_AGENTS_PRELOAD_LOCAL_INFERENCE=0` để bỏ preload bundled VAD/EOT; L0 đề xuất opt-out rồi setup custom Silero. Flag này không cấm mọi inference hay network. Kiểm trên SDK image pin, OS/start method, đo RSS/startup và egress; không coi đây là public/stable API bất biến.[^lk-preload]

### 5.2 Bộ cấu hình baseline

Giá trị default dưới đây là **Reported** từ docs; giá trị đề xuất là **Synthesis**, không phải copy default HF.[^lk-vad][^lk-turns][^lk-tuning]

| Option Python | Default tra cứu | L0 đề xuất | Ghi chú |
|---|---|---|---|
| `turn_handling.turn_detection` | Có thể auto-select | `"vad"` explicit | Không tự dùng detector không hỗ trợ vi |
| VAD `sample_rate` / `force_cpu` | 16000 / true | 16000 / true | |
| VAD `min_speech_duration` | 0.05s | 0.05s | Test “không”, “dừng”, nói nhỏ |
| VAD `min_silence_duration` | 0.55s | 0.30s khởi điểm | Cắt segment ASR, không đồng nghĩa commit turn |
| VAD `prefix_padding_duration` | 0.5s | 0.25s khởi điểm | Kiểm đầu âm và mọi lớp padding |
| VAD `activation_threshold` | 0.5 | 0.5 khởi điểm | Tune theo false/missed speech |
| Endpointing `mode` | fixed | fixed | Dynamic thử sau baseline |
| Endpointing `min_delay` / `max_delay` | 0.5s / 3.0s | 0.60s / 2.50s | Không diễn giải thành grace HF |
| Interruption `mode` | Theo môi trường/khả năng | `"vad"` explicit | Không Cloud adaptive ở profile OSS |
| Interruption `min_duration` / `min_words` | 0.5s / 0 | 0.20s / 0 khởi điểm | A/B0.2/0.3/0.5s; min_words không chặn lệnh một từ |
| `resume_false_interruption` / timeout | true / 2.0s | true / 2.0s khởi điểm | Kiểm ASR chậm không bị coi là false |
| Preemptive `enabled` / `preemptive_tts` | true / false | false / false | L0 đặt explicit |

Đơn vị bảng là giây theo Python; Node.js sử dụng millisecond cho nhiều turn options, không copy số nguyên xi.

Trong VAD mode, docs mô tả endpoint delay hiệu dụng là `max(VAD silence, min_delay)`, **không cộng hai số một cách cơ học**. Tuy nhiên ASR phải có final transcript để pipeline trả lời; delay thực còn phụ thuộc segment-final HTTP. `max_delay` không tự bảo đảm mọi loại lượt đều chờ tới số đó. Replay đo timeline thật.[^lk-turns]

### 5.3 LiveKit native turn detector: không chọn làm mặc định tiếng Việt

Theo docs được tra (**Reported**):[^lk-detector]

- Audio detector có `v1` remote trên LiveKit Inference và `v1-mini` local CPU; danh sách14 ngôn ngữ không có tiếng Việt.
- Text `MultilingualModel` cũng không liệt kê tiếng Việt, đã deprecated và dự kiến bỏ trong SDK2.0.
- SDK mới có thể tự chọn audio detector nếu không explicit config. Vì vậy L0/L1 phải ghi rõ VAD-only hoặc adapter đã được phê duyệt.
- Local execution hoặc tên “multilingual” không chứng minh chất lượng tiếng Việt. Không ép `vi` thành `en`/`id` để báo support.

**Adaptive interruption khác end-of-turn detector.** Adaptive barge-in được tài liệu hóa là tính năng LiveKit Cloud; không bật nó trong OSS/no-egress profile. End-of-turn Smart Turn cũng không tự giải quyết backchannel “ừ/vâng”.[^lk-adaptive]

### 5.4 Smart Turn — extension spike

[Smart Turn v3.2](../wiki/smart-turn.md) công bố tiếng Việt, input mono16k, cửa sổ tối đa8s; CPU int8 Vietnamese accuracy79.38%, FPR8.86%, FNR11.75% trên1.004 mẫu (**Reported**, chưa đo độc lập). Đây là challenger, không phải cam kết chất lượng sản phẩm.

**Observed từ SDK source:**[^lk-turn-code]

- `_TurnDetector.predict_end_of_turn(chat_ctx, ...)` chỉ nhận chat context; không phù hợp để giả vờ truyền audio qua text.
- `_StreamingTurnDetector.stream()` có stream protocol với `push_audio`, `predict`, `cancel_inference`, `flush`, `end_input`, `aclose` và `TurnDetectionEvent`.
- Các tên có `_` là interface nội bộ. Source cho thấy điểm tích hợp khả thi, không xác nhận public/stable plugin API.

**Spike đề xuất (Adapter, Unverified):**

1. Viết `SmartTurnAdapter` theo streaming protocol của SDK pin; buffer input audio16k trong session, inference CPU ngoài event loop.
2. Prediction tại pause dùng cửa sổ theo contract model; giữ đủ context8s và reset theo lifecycle turn, không reset mỗi VAD segment.
3. Chuẩn hóa ý nghĩa probability/threshold và `supports_language("vi")`; không đảo complete/incomplete hoặc bịa backchannel score.
4. Gắn revision/inference token nội bộ; speech tiếp diễn/cancel/reset làm prediction cũ vô hiệu. Không commit turn trong adapter.
5. Map `flush`/`end_input`/`cancel_inference` đúng lifecycle quan sát trong SDK; semantics này phải inspect/test, không suy ra từ tên hàm.
6. Timeout → fallback VAD-only theo policy đo được; fail-open/forced endpoint phải được log bằng metric, không giả model dự đoán chắc chắn.
7. Kiểm adapter không thêm owner endpointing hoặc lặp inference vô hạn; bounded latest-relevant work.

Nếu private interface không ổn định, giữ VAD-only đã tune hoặc làm integration patch nhỏ có pin/CI; không thêm một manual turn state machine song song chỉ để “ghép được”. Tách `turn-service` chỉ khi CPU/dependency/load yêu cầu; cancellation/validity vẫn nằm ở agent.

---

## 6. ASR service và STT adapter

### 6.1 Không đánh đồng segment-final và turn-final

L0 dùng ASR HTTP batch trên speech segments do VAD phát hiện. Engine không native-stream audio; adapter trả final cho segment. AgentSession có thể gộp nhiều segment thành một user turn.

LiveKit default STT node bọc non-streaming STT bằng VAD (**Reported**). Đây là khả năng tái sử dụng; phải kiểm số request, audio overlap và ordering với endpointing thực tế.[^lk-nodes]

```text
VAD segment A → HTTP ASR → final A ─┐
VAD segment B → HTTP ASR → final B ─┴→ AgentSession user turn
                                       → on_user_turn_completed → LLM reply
```

Không hứa “một request cho cả lượt” nếu adapter đang dùng segmentation wrapper. Muốn whole-turn ASR cần thiết kế buffer/flush adapter khác và replay riêng, không âm thầm đổi semantics.

### 6.2 Contract facade đề xuất

```text
POST /v1/audio/transcriptions
multipart: file=<WAV PCM16 16k mono>, model=<pinned>, language=<engine-valid>,
           response_format=json
200: {"text": "..."}
429: Retry-After + overload code
```

Contract riêng có version có thể thêm quality flags/request IDs, nhưng plugin OpenAI không mặc nhiên đọc các fields đó. Native OpenAI compatibility và custom base URL được docs nêu; mọi engine vẫn phải qua conformance.[^lk-models]

- Ép tiếng Việt bằng giá trị engine thực sự chấp nhận; pin mapping `vi`/`Vietnamese`/`vi-VN` ở adapter, không đoán.
- NFC; punctuation nếu engine thiếu; filter no-speech/hallucination theo engine, không loại phủ định/entity chỉ để “sạch”.
- Model API có semaphore chung, queue bounded và deadline. Queue per job không giới hạn GPU concurrency toàn hệ thống.
- Đóng HTTP chỉ best-effort; stale response không tạo reply và backend slot release phải đo.
- Custom quality result cần mapped handler/hook trong worker. Empty/no-speech không reply; suspicious/truncated hỏi lại ngắn qua native speech lifecycle.

### 6.3 Lựa chọn engine

| Engine | Vai trò | Gate |
|---|---|---|
| Qwen3-ASR0.6B | Baseline đầu tiên | Chất lượng entity, latency theo độ dài, VRAM/admission |
| Qwen3-ASR1.7B | A/B chất lượng | Đổi đúng ASR, giữ TTS/voice/turn policy |
| Nemotron3.5 | Challenger; HTTP batch trước | Native WS protocol cần adapter riêng; không trỏ vào OpenAI realtime một cách mù quáng |
| faster-whisper large-v3-turbo | Đối chứng | Hallucination filter và executor |
| Gipformer / ChunkFormer | CPU/domain/final-pass candidates | License/runtime/punctuation; chưa two-pass v1 |

Model facts, license và benchmark kế thừa [tài liệu ASR](lua-chon-va-thiet-ke-asr-stt-tieng-viet-realtime.md); đây là lựa chọn **Synthesis**, không xếp hạng từ WER khác protocol.

---

## 7. TTS, cầu text → speech và voice

### 7.1 Một chunker, hai loại text

```text
LLM stream trong worker
  → stateful ThinkFilter
  → markup/emoji/URL policy
  → ClauseChunker (owner duy nhất)
  → TTS adapter gửi display_text + IDs
       │
       ▼
tts-service
  pre-lexicon → normalizer → post-lexicon/tag whitelist
  → validate max text → engine → PCM48k
  → mapping metadata + optional audio timing
       │
       ▼
TTS adapter → native session output / transcript synchronization
```

- Worker giữ filter/chunker state theo speech generation; **actual cancellation** vứt state, không flush tail; provisional pause để false-interruption resume không tự hủy state.
- ThinkFilter phải chặn reasoning **trước history/caption fan-out**, chẳng hạn ở custom `llm_node` đã qua conformance; chỉ đặt trong `tts_node`/`tts_text_transforms` không chứng minh history/UI sạch. Giữ tool-call/usage/terminal ordering khi lọc LLM stream. `tts_text_transforms` mặc định filter Markdown/emoji; cấu hình explicit hoặc `None` khi worker đã sở hữu policy để không transform hai lần.[^lk-nodes][^lk-text]
- `display_text`: text sạch dành cho UI/history; `spoken_text`: bản engine thực sự đọc; raw reasoning không đi vào cả hai.
- TTS service sở hữu normalize/voice policy theo engine để A/B không nhân bản rules trong worker.
- Giới hạn chunk dựa trên text **sau normalize**. Service validate trước gọi engine; nếu vượt trần, trả lỗi typed để worker split lại an toàn. Không silent split/reorder thành một chunker thứ hai.
- Model prompt trả1–3câu ngắn, văn nói; tắt thinking theo LLM backend. Prompt không thay thế filter an toàn token-split.

LiveKit cho phép custom `tts_node`, pronunciation rules và stream transforms. Non-streaming TTS mặc định dùng sentence tokenizer để incremental synthesis (**Reported**).[^lk-nodes][^lk-text]

**Không chạy đồng thời** default sentence splitter và clause chunker cho cùng output. L0 có thể chỉ dùng sentence policy; L1 custom streaming adapter/node sở hữu việc flush clause. Khả năng đầu câu được synthesize trước khi LLM xong phải được trace, không suy ra từ chữ “streaming”. Spike thêm `FlushSentinel` tại `llm_node` nếu native speech segmentation đáp ứng clause policy: docs mô tả một SpeechHandle/assistant message với per-segment playout/truncation từ Python1.6.0. Đây là đường cần thử trước khi thêm scheduler; không thay PCM48k adapter, normalizer mapping hoặc timing gate.[^lk-nodes]

### 7.2 Chunk policy khởi điểm

**Synthesis, chốt sau PoC:**

- Clause đầu ưu tiên ranh giới tự nhiên sau khoảng25ký tự; không chờ cả câu quá dài.
- Gộp mảnh rất ngắn; cap text/duration theo manifest engine, không dùng một `max_chars` cho mọi model.
- Không cắt trong `1.250.000đ`, `3,5`, `14:30`, `TP.HCM`, viết tắt hay tên riêng được bảo vệ.
- Fuzz token boundaries cho `<think>`, markdown, URL, số/date/unit; output policy phải độc lập cách LLM chia token.
- Một request engine active/speech generation; prefetch tối đa một clause khi còn credit. Đo gap/underrun rồi mới tăng synthesis-ahead.
- ThinkFilter đóng lỗi theo policy khi markup reasoning không cân bằng; không đọc reasoning để “đỡ im lặng”.

VietNormalizer và lexicon pin version; policy code-switch theo voice/engine. Không dùng neural normalizer chưa qua semantic-fidelity/license gate để tự sửa câu LLM.

### 7.3 TTS adapter và API

**L0:** HTTP facade text → chunked PCM48k. Custom adapter mỏng khai đúng sample rate/channels, reframe bytes, deadline, close body khi cancel và emit events đúng SDK pin.

**L1:** API riêng có version mang metadata; không giả metadata đi trong raw PCM OpenAI response. Contract logic **Synthesis**, chưa là protobuf/SDK API:

```text
SynthesizeChunk(request_id, speech_generation_id, chunk_id, voice_id,
                display_text, policy_version)
  → TextMapping(display_text, spoken_text, segment_map, warnings, versions)
  → AudioFrame(seq, sample_offset, rate=48000, channels=1, pcm_s16le)*
  → ChunkEnd(total_samples, optional_audio_timing)
  → Done | Error(code, retry_after)
```

Có thể dùng HTTP streaming framed hoặc gRPC server-streaming; chọn một sau transport conformance. Không cần bidi text-delta RPC ở v1 vì worker đã chunk text. LLM/worker không gửi delta trực tiếp tới engine nhận cả câu.

**Capability manifest:** rate/channels/encoding, streaming audio, streaming text input, max text, cancel behavior, timestamp precision, voice mode, license, warmup/readiness. Khai hai loại streaming tách biệt.

### 7.4 Engine và voice registry

| Engine | Vai trò | Gate |
|---|---|---|
| VieNeu v3 Turbo | Research baseline PCM48k | License còn mâu thuẫn; commercial bị chặn tới legal review |
| VoxCPM2 / MOSS-TTS | Commercial/cloning challengers | TTFA/cadence, cancellation, rate/channels và license thực tế |
| Gwen / G-OmniVoice | Research đối chứng | Full waveform không phải low-TTFA streaming; license/lineage |
| CPU engines | Edge/degraded profile | Chất lượng và SLO riêng; không silent fallback khác giọng |

Chi tiết engine/API/giới hạn giữ ở [tài liệu TTS](lua-chon-va-thiet-ke-tts-tieng-viet-realtime.md) và [bản HF §5.6](thiet-ke-pipeline-speech-to-speech-tieng-viet-hf-s2s.md#56-tts-service-phần-2-engine-giọng-và-capacity); các claims đó không được tái kiểm upstream trong bản LiveKit.

- `voice_id` ổn định ánh xạ engine/preset/reference/region/lexicon/sampling/watermark policy.
- Clone reference có consent, retention và quyền truy cập; không upload tùy ý từ URL/path client.
- Voice clone chỉ tồn tại trong memory của engine phải được re-register sau restart trước readiness, như giới hạn VieNeu đã ghi trong bản HF.
- Fixed-phrase cache hỏi lại/lỗi theo `(voice_id, engine_version, policy_version, phrase_id)`; phát qua native speech handle, không bypass cancellation/history bằng raw track riêng.
- Retry trước audio đầu nếu còn deadline; sau audio đầu không retry toàn chunk làm user nghe lặp.

---

## 8. Session runtime, interruption, history và LLM

### 8.1 Quyền sở hữu

| State / effect | Owner |
|---|---|
| Room/media/participants | LiveKit Server |
| Turn endpoint, speech scheduling, interruption, chat context | AgentSession/native activity |
| ASR result validity, service retries, quality mapping | Adapter trong lifecycle session |
| Filter/chunker state | Worker, scoped theo speech generation |
| Inference slot/queue/voice policy | Model service |
| Session authorization/admission | App backend; lease/reconciler |
| Business records/approvals nếu bổ sung | Application state/store, không model service |

Internal `session_id/turn_id/revision/speech_generation_id/chunk_id` là IDs ứng dụng cần map với job/room/participant/speech handle native, **không phải fields LiveKit tự cấp đầy đủ**. Không direct-mutate private history để enforce một counter ngoài session.

### 8.2 LLM và context

Dùng OpenAI plugin với `base_url` tới endpoint Chat Completions self-host; không nhầm với Responses/realtime protocol (**Reported**).[^lk-llm]

- Explicit model/base URL/API key; không để fallback credential/provider public.
- Deadline connect/TTFT/inter-token/overall; close stream khi cancel; retry giới hạn trước token đầu.
- System prompt nhỏ, cấu trúc identity/output rules/goals/guardrails: tiếng Việt plain text,1–3câu, hỏi một câu mỗi lần, giữ corrections/phủ định và facts user đã cung cấp, không lộ reasoning/tool internals. Chỉ tools của workflow hiện tại. Không copy SSML/emotion/phoneme tags của vendor vào local TTS chưa hỗ trợ. Context dài hoặc quá nhiều tools làm tăng TTFT.[^lk-prompting]
- Một Agent cho trách nhiệm hiện tại; khi có intake/resolution/billing, handoff theo reasoning/permission boundary, không mang toàn bộ tools qua mọi phase. Agent mới mặc định có LLM history mới; phải truyền selected `chat_ctx`/summary/facts explicit, có thể copy với `exclude_instructions=True`. `session.history` vẫn là lịch sử tổng, không đồng nghĩa prompt Agent mới nhận mọi history. Typed `session.userdata` giữ state chung; task nhận quyền tạm thời rồi trả typed result. Kiểm per-agent model/turn overrides không bật Cloud hoặc đổi voice/policy ngoài authorization.[^lk-handoffs]
- Summarization tường minh có metric; không hidden LLM call trong run latency. Giữ phủ định/corrections/facts quan trọng.
- `on_user_turn_completed` là hook voice-turn trước reply để kiểm validity/context; không tự phát một response thứ hai song song nếu native pipeline đã scheduled reply. Text/audio có thể đi hook paths khác nhau; listener ghi committed user messages dùng public `conversation_item_added`, bind trước start và test đúng input mode. Khi mở hybrid, modality-aware `Instructions` của Python còn beta; không giả đổi prompt theo input cũng tự tắt TTS output.[^lk-nodes][^lk-text][^lk-prompting]

### 8.3 Speculation/preemptive generation

Docs mô tả preemptive LLM khi final transcript tới trước turn confirmation; preemptive TTS là option riêng (**Reported**).[^lk-tuning]

| Mức | Policy đề xuất | Điều kiện |
|---|---|---|
| L0 | Disable preemptive explicit | Đo ordering và baseline trước |
| L1 mặc định sau gate | LLM-only preemptive, bounded attempts | Final đổi → cancel response cũ; không audio/effects trước commit |
| TTS preemptive | Off, chỉ thử sau | GPU spare budget; đo waste/reopen và cadence |

Không đồng nhất native preemptive behavior với máy trạng thái SOFT_ENDED/reopen/grace của HF. Replay phải kiểm các mốc native thật. Tool side effects không được phép trên speculative transcript; đừng coi close LLM stream như rollback database.

### 8.4 Barge-in/cancellation

Native có automatic interruption, explicit interruption và false-interruption recovery (**Reported**).[^lk-turns]

Conformance yêu cầu:

1. User speech khi bot nói đi qua native interruption handling (có thể pause trước khi actual interruption); không listener phụ vừa cancel vừa gọi `generate_reply` nhân đôi turn.
2. Phân biệt **provisional pause** và **actual interruption**. Source reference giữ speech handle/audio khi false-interruption recovery có thể pause/resume; không close TTS/LLM hoặc vứt chunker ngay ở mọi VAD start. Khi native lifecycle thực sự interrupt/cancel generation, work cũ mất quyền publish, native xử lý playout/truncation và adapter đóng streams liên quan. Không cancel ASR đang nhận dạng lượt user mới chỉ vì bot bị ngắt.[^lk-activity]
3. Async generator bị cancel phải đóng HTTP/gRPC stream trong `finally`; không flush filter/chunker còn dang dở.
4. Model slot release đo độc lập; stale compute có thể còn chạy nhưng không được phát audio/event có nội dung.
5. Giữ pre-roll/lệnh ngắn; xác nhận “vâng/không” không bị keyword filter coi là backchannel và bỏ đi.
6. False-interruption resume phải kiểm với ASR batch chậm; không resume trước khi user phủ định/correction final tới.

Đo `T_silence` (user speech start → bot im ở client) và `T_release` (cancel → backend slot nhả). Giảm cái thứ nhất không chứng minh đã giảm cái thứ hai.

### 8.5 History và playback

LiveKit công bố tự truncation history đến phần speech user đã nghe; transcript sync cũng dừng/cắt khi ngắt (**Reported**). TTS-aligned word timestamps phụ thuộc provider; non-streaming TTS qua StreamAdapter có thể chỉ có sentence timing.[^lk-turns][^lk-text]

**Đề xuất best practice:** giữ native behavior trước, không copy playback ledger H1 của HF như yêu cầu fork mặc định. Nhưng phải test:

- Ngắt giữa chunk, giữa số tiền/date span đã rewrite; history/UI không chứa phần chưa nói theo policy đã phê duyệt.
- Native text đi vào history là display hay spoken text khi TTS transforms chạy; đừng giả normalizer service tự cập nhật history.
- Text segment offsets không phải audio timestamps. Mapping `display_text ↔ spoken_text` cần thêm timing mới cắt trong chunk đáng tin.
- TTS không timing: công bố granularity/estimate; nếu release cần strict heard-prefix, thêm alignment hoặc conservative completed-chunk policy qua integration đã test. Không tự tuyên bố word-accurate.
- Server playout completion không chứng minh remote device đã render hết; browser jitter/output latency và disconnect phải vào failure tests.
- Caption sync tốt hơn không thay client D1 measurement hay privacy consent.
- Docs có `use_tts_aligned_transcript=True` và `TextOutputOptions.json_format=True` để gửi timed chunks; timestamps chỉ có khi provider/adapter thực sự emit timing. `transcription_node`/`TimedString` được đánh dấu experimental: thêm compatibility gate. JSON mode cần frontend decoder tương ứng; không giả plain-text handler vẫn đúng. Cached speech nên gửi text+audio qua `session.say` nếu cần history/captions; audio-only không thêm text vào context.[^lk-text][^lk-audio]

Nếu native không đủ gate, làm spike adapter/output integration cho timing/mapping; extension client ACK chỉ là phương án nghiên cứu, chưa API sẵn có. Nếu phải thay toàn bộ history/control, đánh giá lại kiến trúc trước khi fork.

---

## 9. Admission, backpressure, degradation và vận hành

### 9.1 Admission ba tầng

1. **App session admission:** quota theo tenant/user, capacity budget, lease TTL, reject trước token/dispatch khi đầy.
2. **Worker load:** job dispatch/load threshold theo CPU/RAM/loop lag/active jobs. Native load balancing không biết mọi giới hạn GPU services.
3. **Model admission:** ASR inflight và TTS active streams toàn endpoint; queue bounded, 429/deadline/circuit breaker.

Docs có balanced job dispatch, load function/threshold và graceful drain; mỗi job ở subprocess (**Reported**). Không suy ra một job tương đương một TTS stream, hoặc capacity vendor trên4CPU/8GB đúng cho custom Smart Turn/bridge.[^lk-deploy]

### 9.2 Queue budgets đề xuất

| Cạnh | Budget / policy (Synthesis) |
|---|---|
| Audio vào / turn buffer | Trần thời lượng/byte theo session; overflow có gap marker và hỏi lại/invalidate, không mất âm thầm |
| ASR pending | Trần per session + shared endpoint; giữ ordering, bỏ work superseded |
| Smart Turn | Latest-relevant prediction, bounded executor; speech continuation vô hiệu prediction cũ |
| LLM → chunker | Lookahead/bytes bounded; không buffer toàn reply vô hạn |
| Worker → TTS | 1active + tối đa1pending clause/generation khởi điểm |
| TTS → native output | Audio lead khởi điểm1–2s + byte ceiling; đo queue thật của SDK/RTC |
| Control/terminal | Không drop cancel/end/error khi đầy data queue |
| Opt-in recording | Async bounded; storage chậm không chặn audio critical path |

Budget ở đây là requirement triển khai, **không khẳng định mọi internal queue native đã bounded**. SDK API không expose queue nào thì inspect source/spike trước, không thêm buffer vô hạn bên ngoài để che.

Native `user_turn_limit` là bộ đếm tích lũy giữa các user turns cho tới khi agent nói, không phải trần RAM mỗi ASR request. Adapter phải có cap audio độc lập.[^lk-turns]

### 9.3 Shared GPU24GB

- Qwen ASR và TTS có thể chung GPU ở PoC; LLM không chung node.
- Giới hạn VRAM preallocation của vLLM và ASR inflight; TTS stream slots đo dưới tải chung.
- Đo TTS codec/step cadence khi ASR burst. VRAM còn trống không chứng minh P95/underrun tốt.
- Nếu contention làm vỡ cadence: giảm ASR inflight, dùng CPU challenger, hoặc tách GPU/service.
- Scale model replicas độc lập worker/SFU; node capacity là min của CPU/job, ASR throughput, TTS streams/cadence và network budget.
- Cold/idle test có khoảng nghỉ6–20s; warmup không đồng nghĩa GPU giữ clock mãi.

### 9.4 Degradation

| Sự cố | Policy |
|---|---|
| Session capacity đầy | Reject trước dispatch; UI retry/backoff, không mở room vô hạn |
| ASR empty/no-speech | Không reply; tiếp tục nghe theo native lifecycle |
| ASR suspicious/timeout/429 | Hỏi lại ngắn nếu còn usable output; không bịa transcript |
| LLM timeout trước text | Cached phrase/lỗi + retry bounded theo deadline |
| TTS429 trước audio | Retry replica cùng engine/voice nếu còn budget; không loop vô hạn |
| TTS lỗi sau audio | Stop/fail speech, history bảo thủ; không đọc lại toàn chunk |
| Model service chết | Circuit breaker/restart; voice/cache restore trước readiness |
| Worker/job crash | Client báo mất agent/reconnect policy; không claim migrate context tự động |
| Input gap dài | Invalidate/hỏi lại; threshold theo replay, không nối hai đoạn thành câu sai |
| Smart Turn timeout | VAD-only fallback có metric; không giữ turn vô hạn |

Cached fallback phải đi qua session speech lifecycle và voice đúng. Không silent đổi TTS engine/giọng giữa utterance.

### 9.5 Readiness, async và rollout

- ASR ready sau model warmup + audio tiếng Việt thật; TTS ready sau voice re-register/cache/warmup. Health process sống chưa đủ.
- Worker setup kiểm backend contract/version và pin config; không nạp weights theo user request.
- Không `asyncio.run()` hay synchronous I/O trong job loop; async clients đóng cùng job, tránh object gắn loop khác.
- Drain worker: ngừng nhận jobs mới, để sessions kết thúc trong timeout; orchestration grace period phải tương thích. Test ở production startup mode, không chỉ dev.[^lk-deploy]
- Rolling update theo versioned agent/config; active sessions giữ version cũ tới drain. Rollback image+policy+adapter đồng bộ.
- SDK upgrade qua branch: changelog, adapter compatibility, audio/history replay, load smoke và canary; không dùng floating `latest`.

---

## 10. Privacy, telemetry và latency

### 10.1 Content-free mặc định

- API secret chỉ backend/worker secret store; JWT client scope room/identity/grants và hạn dùng phù hợp.
- Không log tokens, audio bytes, transcript, prompt, `spoken_text`, reference path, embedding hoặc tool payload.
- OTel spans cũng có thể chứa nội dung. Whitelist ID/duration/length/status/version, scrub request URL/headers/exceptions/exporter attributes; không bật exporter mặc định rồi cho rằng content-free.
- Không persist toàn `session report`/chat history. Recording/transcript opt-in có consent, retention, ACL và storage private.
- Offline models/wheels và deny-by-default egress; kiểm startup/download/telemetry/ICE destinations.
- Clone reference ngoài repo, có revoke/expiry; voice registry enforce authorization server-side.

Cloud Agent Insights/PII-redaction không có cho entirely self-host media; dùng SDK data hooks/OTel tới hạ tầng riêng (**Reported**). Không coi Cloud redaction là lá chắn cho log OSS.[^lk-observability]

### 10.2 Timeline/metrics

Join app session/job/room/participant/speech handle IDs với adapter request/chunk IDs. Không log tên người hoặc room name chứa PII.

Mốc cần đo:

```text
last user speech sample → VAD pause/segment end
  → ASR dispatch/final → turn confirmed
  → LLM first token → first usable clause
  → TTS request/first PCM → first native output enqueue
  → first audible bot sample tại client
```

ASR/LLM có thể overlap endpointing khi profile cho phép; report trace thực, không áp công thức serial cố định.

| Metric | Mục tiêu / cách báo |
|---|---|
| D1 client | P50≤1.5s, P95≤2.5s mềm; theo profile, turn type, noise, load, cold |
| End-of-turn latency | Last speech → commit, tách ASR wait/detector/endpoint delay |
| ASR | Queue/compute/final latency theo duration; WER/CER/entity |
| LLM | TTFT, first usable clause, context size, cancellation |
| TTS | Queue, TTFA, RTF, inter-clause gap, underrun, active streams |
| Interruption | T_silence/T_release, false/missed interruption, short command loss |
| Control/history | Stale/precommit audio, discarded text/chunks, alignment granularity |
| Infrastructure | Job CPU/RAM/loop lag, sessions, dispatch latency,429, network/TURN use |

Duration đo local mỗi host; không trừ monotonic timestamps giữa máy. D1 phải có mốc speech cuối và audible sample trên cùng clock client, hoặc phương pháp estimate với sai số công bố. First PCM/server enqueue không phải D1.

### 10.3 Ưu tiên tối ưu

1. Đo endpoint/ASR first, rồi LLM first-clause và TTS TTFA; tránh tối ưu tầng không nằm critical path.
2. Tune pause/min_delay bằng false-cutoff corpus; không hạ delay chỉ để đẹp P50.
3. Clause chunking và policy đọc giúp câu đầu dài; streaming audio không lấy lại thời gian đợi cả câu.
4. Bật LLM-only preemptive sau correctness gate, đo waste và reuse thực tế.
5. Tăng synthesis-ahead chỉ khi gap/underrun cần và queue budget còn đủ.
6. Giữ context nhỏ; không tool calls/summary ẩn gây lệch latency report.

---

## 11. Kiểm thử và release gates

Không có gate runtime nào dưới đây đã được chạy. Lint tài liệu không thay cho agent test.

### 11.1 Test pyramid

| Tầng | Nội dung | Chứng minh / không chứng minh |
|---|---|---|
| Deterministic unit | Chunker/filter/normalizer/mapping/lease/deadline/queue | Logic exact; không chứng minh model hiểu tiếng Việt |
| Adapter conformance | HTTP/gRPC formats, rates, partial bytes,429/cancel/close/release | Wiring và backend behavior |
| SDK text-turn tests | AgentSession, reply, hook, future tools/handoffs với providers local/scripted | Conversation/event behavior; không kiểm VAD/audio |
| Audio replay | Pause/continuation/barge-in, async races, delays và stale results | Turn/audio/history mechanics |
| Browser E2E | Mic/speaker/AEC/WebRTC/TURN/caption/playback/D1 | Client experience trên thiết bị thật |
| Load/fault/soak | Bursts, slow peers, crashes, cold GPU, teardown/drain | Capacity và degradation |

LiveKit có SDK unit-test harness dùng pytest/Vitest, multi-turn/assertions/mocking (**Reported**). Dùng scripted provider cho wiring và LLM self-host thật cho meaning; không gọi remote judge nếu trái privacy profile.[^lk-tests]

Không mặc định dùng Cloud simulations/managed observability trong pipeline OSS. Local text tests và self-host audio replay/browser harness là đường gate chính; mọi công cụ đánh giá thêm phải qua no-egress audit.

### 11.2 L0 acceptance

1. Một browser/user/room, đúng một agent, mic continuously active; ASR/LLM/TTS chạy đúng self-host endpoints.
2. Audio input16k/output48k thật, không hidden24/16k downlink; PCM conformance và voice đúng.
3. Explicit VAD-only/interruption options, no Cloud detector/adaptive requests, preemptive off; text input tắt, AGC/pre-connect policy và preload/RSS được kiểm theo manifest.
4. “Không/dừng/vâng”, ngập ngừng, echo/noise, interruption giữa response; ghi limitations history.
5. D1/client timeline + request counts/VRAM; warm/cold report, không claim production.
6. Auth/consent/license research, network egress và content-free exception/log audit; reasoning không xuất hiện trong history/caption, transcript renderer không nhân đôi interim/final.

### 11.3 L1 production gates bắt buộc

| Gate | Acceptance |
|---|---|
| G1 — ASR tiếng Việt | Corpus Bắc/Trung/Nam, code-switch/số/tên/địa chỉ/phủ định/noise; WER/CER/entity và latency theo duration |
| G2 — TTS fidelity | Golden normalization, fuzz token split, blind listening/prosody/code-switch; mapping đúng, source/output48k thật |
| G3 — Turn correctness | Pause→continuation, segment final đến muộn, transcript change, short command, cancel/prediction cùng tick; provisional pause→resume và real interrupt→cancel không xung đột; no stale/precommit output |
| G4 — History/playback | Ngắt giữa rewritten span/chunk, missing timing, jitter/disconnect, fallback/cache; không claim độ chính xác vượt granularity được đo |
| G5 — Browser/transport | HTTPS/mic/AEC, AGC A/B, UDP bị chặn→TURN/TLS, reconnect/playback bị chặn, caption interim/final upsert, text-input rejection, pre-connect consent/no-duplicate, participant authorization |
| G6 — Capacity/failure | Concurrency1/4/8/16 tới capacity đích, ASR/TTS shared GPU bursts/cold,429/timeout/slow client/crash; bounded RAM/queues; soak1000sessions và drain |
| G7 — Security/license/ops | Token grants/metadata auth, no-egress kể cả startup/preload, log/trace payload scrub, reasoning không vào history/caption/log, idle-process RAM, clone consent/re-register, promote/rollback và SDK upgrade suite |

Nếu bật Smart Turn, thêm compatibility suite cho streaming-detector private protocol, probability semantics, reset/cancel/timeout và native prediction ordering. Không promote chỉ vì classifier chạy ra một con số.

**L1 release:** qua cả7gate trên phiên bản pin, SLO/false-cutoff/capacity có workload định nghĩa và product owner chấp nhận granularity history. Không dùng native feature docs như bằng chứng đã pass.

---

## 12. Manifest, versioning và lộ trình triển khai

### 12.1 Manifest logic minh họa

**Synthesis:** YAML dưới là config ứng dụng, không phải file config LiveKit Server hay constructor SDK copy-paste. Placeholder phải được thay bằng version/checksum đã qua smoke test; không chứa secrets.

```yaml
profile: L0
privacy: self_host_no_egress
license_profile: research
livekit:
  server_image_digest: <locked-digest>
  agents_python_version: <exact-tested-version>
  client_sdk_version: <exact-tested-version>
  transport: oss
  turn_policy: vad_only
  adaptive_interruptions: false
  cloud_inference: false
worker:
  env: {LIVEKIT_AGENTS_PRELOAD_LOCAL_INFERENCE: "0"} # source/version-gated
room_io:
  input: {sample_rate: 16000, channels: 1, auto_gain_control: false, pre_connect_audio: false}
  output: {sample_rate: 48000, channels: 1}
  text_input: false
  text_output: {sync_transcription: true, json_format: false}
turn_handling:
  endpointing: {mode: fixed, min_delay: 0.60, max_delay: 2.50}
  interruption: {mode: vad, min_duration: 0.20, min_words: 0}
  preemptive_generation: {enabled: false, preemptive_tts: false}
vad:
  engine: silero_cpu
  min_silence_duration: 0.30
  prefix_padding_duration: 0.25
asr:
  adapter: segment_final_http
  endpoint: http://asr-api:8101/v1
  engine: qwen3-asr-0.6b
  language: vi
  model_revision: <locked-revision>
tts:
  adapter: custom_pcm48
  endpoint: http://tts-api:8103
  engine: vieneu-v3-turbo
  license_status: disputed
  voice_id: vi-north-01
  policy_version: <locked-policy>
text_bridge:
  owner: agent_worker
  chunk_policy: sentence_baseline
  reasoning_filter_stage: llm_output_before_history_and_captions
  sdk_tts_text_transforms: disabled_when_worker_owns_filtering
  normalization_owner: tts_service
llm:
  api_mode: chat_completions
  endpoint: http://llm-host:8000/v1
  model: <existing-model>
  thinking: disabled_by_backend_specific_config
```

Production manifest thêm weights/runtime checksums, adapter protocol version, lexicon/normalizer, voicepack/reference consent, waveform encoding, cancellation/timestamp capabilities và measured limits. `max_inflight`, `max_streams`, job/session caps là số đo, không lấy trực tiếp từ số core hay GPU VRAM.

### 12.2 Phases và deliverables

| Phase | Công việc | Điều kiện xong |
|---|---|---|
| P0 — Media spike | OSS server/TURN/backend token/client, agent participant phát test audio | Auth+dispatch một agent, network/ICE và output48k conformance |
| P1 — L0 cascade | Silero, Qwen HTTP adapter, LLM plugin, VieNeu PCM adapter, sentence policy | §11.2; có timeline và limitations |
| P2 — Text/audio hardening | Clause chunker, normalizer/mapping/voice/cache, cancellation/history tests | G2/G3/G4 mini-suite; không double splitter |
| P3 — Turn spike | So VAD-only đã tune với Smart Turn adapter CPU | Chất lượng/latency có lợi; private API suite và fallback |
| P4 — L1 production | Admission/queues/telemetry/load/security/license/canary/drain | Cả7gate; workload/capacity công bố |
| P5 — Optional | Streaming ASR, preemptive TTS, scale replicas, SIP/two-pass/tools | Gate riêng; không làm mất single owner |

Deliverable triển khai tiếp theo: project Python có lockfile, adapter conformance tests, agent entrypoint, frontend/backend token endpoint, Docker Compose cho lab, production network/readiness/runbook và local audio replay suite. Không cần dựng registry/turn microservices/Kubernetes trước khi P1 đo được.

---

## 13. So sánh với HF và các điểm còn mở

### 13.1 Mapping kiến trúc

| Chủ đề | HF H0/H1 | LiveKit L0/L1 |
|---|---|---|
| Transport | HF realtime API/aiortc, optional coturn | LiveKit rooms/SFU/Client SDK, embedded TURN |
| Owner lượt | Native HF turn tracker | Native AgentSession/activity |
| Session capacity | `num_pipelines` + edge admission | Worker jobs/load + app/model admission |
| ASR | HTTP remote turn-final theo HF | VAD-wrapped segment-final HTTP baseline; native streaming sau |
| TTS bridge | H1 fork delta handler + bidi RPC | Worker custom TTS node/adapter; service normalize/mapping |
| Audio | H0 internal16k, H1 patch48k | RoomIO default24k reference; explicit48k + adapter/conformance |
| History | H0 truncate no-op; H1 fork ledger | Native truncation trước; alignment/mapping extension nếu gate cần |
| Turn tiếng Việt | Smart Turn mặc định HF capture | VAD-only explicit; Smart Turn adapter spike |
| Speculation | Grace/reopen state machine HF | Native preemptive generation, không bảo đảm semantics giống HF |
| Upgrade cost | Maintain production fork | Maintain adapters/private Smart Turn interface nếu bật |

### 13.2 Điểm cần xác minh khi triển khai

- Exact SDK/server/client release phù hợp source reference. Docs và source comment auto-selection có thể khác nhau; explicit config và startup tests là cách tránh phụ thuộc default.
- STT segmentation/final ordering và số request khi user pause/continue, đặc biệt preemptive reuse.
- Smart Turn `flush/reset/cancel` integration và deadline; source protocol không chứng minh plugin hoàn chỉnh.
- LLM→TTS first-clause scheduling, clause flush semantics và giữ native tool/usage/terminal ordering.
- Native history/transcription precision khi display/spoken text khác nhau hoặc TTS thiếu timestamps.
- RoomIO/source/track thực sự giữ48k; output options không thay decoder/rate contract sai trong plugin.
- Shared GPU cadence, cold-start/clock, worker RAM/CPU/job footprint và actual queue bounds.
- ICE/STUN egress từ server IP discovery, Cloud feature auto-selection, default telemetry có payload.
- VieNeu license commercial, cloning lineage/consent và retry/cancel slot behavior theo version engine thật.

### 13.3 Khi nào dừng extension/fork

Nếu Smart Turn/private interfaces không ổn định nhưng VAD-only đạt tiêu chí, giữ VAD-only. Nếu audio/history correctness đòi thay phần lớn native control, làm quyết định kiến trúc mới và so lại [orchestrator riêng](thiet-ke-pipeline-speech-to-speech-tieng-viet.md), không âm thầm thêm một owner song song với AgentSession.

Tài liệu này khuyến nghị LiveKit vì có extension points và native realtime abstractions phù hợp; **không tuyên bố LiveKit đã đạt production parity hoặc miễn phí maintenance**.

---

## 14. Nguồn và giới hạn tra cứu

### 14.1 Nguồn nội bộ

- [Spec PoC Phase1](spec-poc-speech-to-speech-tieng-viet.md), [bản production v2](thiet-ke-pipeline-speech-to-speech-tieng-viet.md), [bản HF s2s](thiet-ke-pipeline-speech-to-speech-tieng-viet-hf-s2s.md).
- [ASR](lua-chon-va-thiet-ke-asr-stt-tieng-viet-realtime.md), [TTS](lua-chon-va-thiet-ke-tts-tieng-viet-realtime.md), [survey VAD/turn/denoise](survey-vad-turn-detection-denoise-tieng-viet.md), [Smart Turn v3.2](../wiki/smart-turn.md).
- [Chương16 audio contract](chuong-16-dataflow-end-to-end-va-audio-contract.md), [17 turn/cancel](chuong-17-turn-taking-event-barge-in-va-cancellation.md), [18 async/streaming](chuong-18-lap-trinh-async-va-streaming-cho-pipeline-audio.md), [19 bridge](chuong-19-cau-text-to-speech-chunker-normalizer-lexicon.md), [20 latency](chuong-20-latency-dinh-nghia-critical-path-do-luong.md).

### 14.2 LiveKit tra trong phiên này

Nguồn docs là trang online được `lk docs` render ngày2026-10-13, không immutable snapshot trong `raw/`. CLI báo docs server1.5.0/CLI1.4.x skew; dùng nội dung nguồn, không suy ra version SDK từ hai số đó. Không có SDK cài/lockfile để đối chiếu runtime. Source code search chỉ đọc một số interfaces/config types, không audit toàn control plane. Review v1.1 đã đọc đủ10URL user yêu cầu và bổ sung frontend/auth, sessions, server options, tasks, multimodal instructions, noise cancellation, turn options, deployment/testing/observability và changelog. Tra cứu trả Python Agents1.8.6 (2026-10-09), chỉ là candidate để smoke/pin, không phải release đã test; source commit không được xác nhận khớp release. Đã kiểm Python environment hiện tại không có `livekit-agents`/Silero plugin. Chi tiết kết luận/locator/giới hạn ở [báo cáo đối chiếu](doi-chieu-kien-truc-livekit-2026-10-13.md).

[^lk-agents]: [LiveKit Agents introduction](https://docs.livekit.io/agents/) — Framework overview; How agents connect to LiveKit: agent server đăng ký, job subprocess và room participant; STT-LLM-TTS framework.
[^lk-vad]: [Silero VAD plugin](https://docs.livekit.io/agents/logic/turns/vad/) — Requirements, Prewarm, Configuration: local CPU, sample rates, defaults và prewarm pattern. Chưa chạy model.
[^lk-detector]: [LiveKit turn detector](https://docs.livekit.io/agents/logic/turns/turn-detector/) — Audio turn detector/Supported languages/Default model selection; Text turn detector/Deprecated/Supported languages. Hai danh sách không có Vietnamese tại ngày tra cứu.
[^lk-turns]: [Turns overview](https://docs.livekit.io/agents/logic/turns/) — VAD only; STT endpointing; Manual turn control; Interruptions; Interruption mode; False interruptions; User turn limit. Native claims là Reported, không runtime certification.
[^lk-text]: [Text and transcriptions](https://docs.livekit.io/agents/multimodality/text/) — Transcriptions, Synchronized transcription forwarding, TTS-aligned transcriptions, Timed transcripts, Text transforms. Timing granularity phụ thuộc provider/adapter.
[^lk-nodes]: [Pipeline nodes and hooks](https://docs.livekit.io/agents/logic/nodes/) — STT node, LLM node, TTS node, Transcription node, On user turn completed; custom engine/chunking và non-streaming wrappers. Chưa kiểm scheduling trên implementation thật.
[^lk-roomio]: [RoomIO types source](https://github.com/livekit/agents/blob/3f479e242428d5fa9a7208810f036bbb8ccf9a48/livekit-agents/livekit/agents/voice/room_io/types.py) — `AudioInputOptions`, `AudioOutputOptions`, `RoomOptions`: sample_rate24000 default, configurable channels/rates và participant identity. Observed qua code search; không chứng minh end-to-end audio quality.
[^lk-turn-code]: [Turn interfaces source](https://github.com/livekit/agents/blob/3f479e242428d5fa9a7208810f036bbb8ccf9a48/livekit-agents/livekit/agents/voice/turn.py) — `_TurnDetector`, `_StreamingTurnDetector`, `_StreamingTurnDetectorStream`, `TurnDetectionEvent`, `TurnDetectionMode`. Observed interface; underscore/private compatibility phải kiểm theo SDK pin.
[^lk-tuning]: [Turn-taking tuning](https://docs.livekit.io/agents/logic/turns/tuning/) — All options/Python; preemptive generation defaults, interruption thresholds và endpointing semantics. Recommended Cloud/model config không được copy nguyên vào tiếng Việt OSS profile.
[^lk-adaptive]: [Adaptive interruption handling](https://docs.livekit.io/agents/logic/turns/adaptive-interruption-handling/) — Availability, How to use, Aligned transcripts support: Cloud feature, khác end-of-turn detector; không default OSS.
[^lk-server]: [Deploying LiveKit](https://docs.livekit.io/transport/self-hosting/deployment/) — Domain/SSL/LB, Embedded TURN, TURN/TLS, Configuration (`rtc.use_external_ip` dùng STUN), Resources. Port/cert/IP config phải kiểm theo topology/version thật.
[^lk-distributed]: [Distributed multi-region](https://docs.livekit.io/transport/self-hosting/distributed/) — Overview/Multi-node routing: Redis required shared data store/message bus, cấu hình Redis chuyển sang distributed setup. Tra qua search excerpt.
[^lk-deploy]: [Self-hosted agent deployments](https://docs.livekit.io/deploy/custom/deployments/) — Overview, Networking, Memory and CPU, Rollout, Load balancing, Agent server availability, Job crashes. Vendor capacity không áp trực tiếp custom pipeline.
[^lk-auth]: [Endpoint token generation](https://docs.livekit.io/frontends/build/authentication/endpoint/) — Overview, Endpoint schema, Agent dispatch, Request/Response: custom authentication, room_config và server_url/participant_token.
[^lk-models]: [Models overview](https://docs.livekit.io/agents/models/) — OpenAI API compatibility: custom API key/base URL cho model interfaces; conformance vẫn cần khi backend chỉ tương thích một phần. Tra qua search excerpt.
[^lk-llm]: [OpenAI-compatible LLMs](https://docs.livekit.io/agents/models/llm/openai-compatible-llms/) — Overview/Using a custom endpoint: `openai.LLM`, Chat Completions và custom base_url/API key.
[^lk-observability]: [Observability overview](https://docs.livekit.io/testing/observability/) — Only available in LiveKit Cloud; components Data hooks/OpenTelemetry traces và self-host distinction. Payload scrub là yêu cầu thiết kế bổ sung.
[^lk-start]: [Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md) — Requirements/LiveKit Cloud: chuyển OSS bỏ enhanced noise cancellation, dùng plugins; [Agent Builder](https://docs.livekit.io/agents/start/builder.md) — Overview/Limitations: Cloud deployment, SDK-only workflows/plugins/tests.
[^lk-options]: [Agent server options](https://docs.livekit.io/agents/server/options.md) — Prewarm function: setup_fnc, job processes, num_idle_processes; Agent server load, Health check endpoint, Drain timeout.
[^lk-handoffs]: [Agents & handoffs](https://docs.livekit.io/agents/logic/agents-handoffs.md) — Passing state/Context preservation/Per-agent configuration; [Tasks](https://docs.livekit.io/agents/logic/tasks.md) — temporary session control và typed result.
[^lk-audio]: [Speech and audio](https://docs.livekit.io/agents/multimodality/audio.md) — Instant connect, Automatic gain control, Preemptive generation, session.say/SpeechHandle. AGC/pre-connect policy L0 là Synthesis.
[^lk-frontends]: [Frontends](https://docs.livekit.io/frontends/) — Building frontends; [Sessions](https://docs.livekit.io/frontends/build/sessions.md) — lifecycle/messages; [Authentication](https://docs.livekit.io/frontends/build/authentication.md) — TokenSource; [Agent state](https://docs.livekit.io/frontends/build/agent-state.md) — lk.agent.state.
[^lk-prompting]: [Prompting guide](https://docs.livekit.io/agents/start/prompting.md) — Prompt design/Voice realism/Testing; [Modality-aware instructions](https://docs.livekit.io/agents/multimodality/instructions.md) — Python beta, input variants. Vietnamese prompt rules là Synthesis từ guidance, chưa behavioral test.
[^lk-activity]: [Agent activity source](https://github.com/livekit/agents/blob/3f479e242428d5fa9a7208810f036bbb8ccf9a48/livekit-agents/livekit/agents/voice/agent_activity.py) — _interrupt_by_audio_activity, _start_false_interruption_timer, _cancel_speech_pause: pause/resume khác actual interruption. Observed, không gọi private methods trực tiếp.
[^lk-preload]: [SDK preload source](https://github.com/livekit/agents/blob/3f479e242428d5fa9a7208810f036bbb8ccf9a48/livekit-agents/livekit/agents/ipc/_preload.py) — module docstring, ENV_PRELOAD_LOCAL_INFERENCE, _local_inference_models: forkserver/spawn và opt-out local VAD/EOT preload. Observed; flag phải kiểm trên image pin.
[^lk-tests]: [Unit tests](https://docs.livekit.io/testing/unit-tests/) — Overview/test setup/result assertions/mocking/multi-turn SDK harness. Chỉ tra/đọc docs, chưa viết hoặc chạy test agent.
