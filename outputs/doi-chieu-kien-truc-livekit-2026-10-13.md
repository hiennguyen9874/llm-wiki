# Đối chiếu kiến trúc speech-to-speech tiếng Việt với LiveKit

> **Ngày:** 2026-10-13 UTC. **Đối tượng:** [thiết kế LiveKit](thiet-ke-pipeline-speech-to-speech-tieng-viet-livekit.md).
> **Phương pháp:** `lk docs` đọc đủ 10 URL được yêu cầu, thêm docs runtime/frontend/turn options/nodes/testing/deployment; code search và changelog. CLI báo docs server 1.5.0/CLI 1.4.x skew.
> **Giới hạn:** đối chiếu tài liệu và source, không kiểm chứng hệ thống chạy. `livekit-agents` và Silero plugin không được cài trong Python environment hiện tại. Không tái kiểm upstream ASR/TTS/Smart Turn, license hoặc benchmark của các model tiếng Việt.

## 1. Kết luận

**Giữ kiến trúc lõi; không cần đổi topology hay fork orchestrator.** Cascade ASR → LLM → TTS, LiveKit Server OSS, một AgentSession/room, Silero local CPU và model services bên ngoài worker phù hợp hướng extension của SDK. Quickstart chính thức cho phép chuyển sang OSS bằng cách bỏ enhanced noise cancellation và dùng model plugins thay Inference.[^quickstart][^nodes]

**Cần sửa implementation contract**, đặc biệt interruption/resume, reasoning filtering, mặc định RoomIO và preload. Các sửa này đã được đưa vào bản thiết kế v1.1; các gate runtime vẫn chưa chạy.

## 2. Những điểm giữ nguyên

| Quyết định | Kết quả đối chiếu |
|---|---|
| Một owner turn là AgentSession | Phù hợp; `Agent` là đơn vị instructions/tools/hooks, không phải media worker hay orchestrator thứ hai.[^sessions][^handoffs] |
| VAD-only explicit cho tiếng Việt | Vẫn đúng: danh sách 14 ngôn ngữ audio detector không có Vietnamese; text multilingual cũng không có và đã deprecated. `v1-mini` local không tự tạo support tiếng Việt.[^detector] |
| Smart Turn là spike | Source vẫn có `_StreamingTurnDetector` nhận audio; interface có `_`, chưa có bằng chứng là plugin API public/stable. Giữ pin/compatibility/fallback, không cam kết integration đã hoạt động.[^turn-source] |
| ASR segment-final HTTP | Default STT node vẫn dùng VAD wrapper cho non-streaming STT. Không đổi nhãn thành whole-turn ASR hay native streaming.[^nodes] |
| Custom PCM48k TTS và một chunker | Phù hợp custom TTS/node; input/output RoomIO trong source vẫn mặc định 24k nên cần cấu hình rate thật. 48k sample rate không đồng nghĩa toàn tuyến có full-bandwidth audio.[^nodes][^roomio] |
| Native history trước ledger riêng | Docs vẫn công bố truncation theo speech; custom normalized text/timing/browser render vẫn cần gate, không phải proof heard-prefix chính xác.[^turns][^text] |
| Preemptive off ở L0, LLM-only sau gate | Docs hiện tại: enabled mặc định, TTS không speculative mặc định. Thiết kế explicit off ở L0 vẫn hợp lý.[^audio] |
| App/worker/model admission riêng | Native worker load không thay semaphore GPU/model services; custom deployment phù hợp OSS.[^options][^deployment] |

## 3. Những cập nhật cần thiết

### P0 — trước khi hiện thực L0

1. **Không hủy vĩnh viễn generation ngay khi VAD phát hiện speech.** Khi false-interruption recovery hoạt động và output hỗ trợ pause, source giữ speech handle/audio để có thể resume. Final transcript hoặc committed replying turn mới kết thúc pause bằng interruption. Cancel stream/drop chunk chỉ theo lifecycle hủy thực, không theo mọi `user_state_changed`/VAD start. Đường ASR của user mới phải tiếp tục chạy.[^activity]
   - Gate: noise không transcript → resume đúng; “không/dừng” với ASR chậm → không resume sai; real interruption → stale audio không phát, backend slot được nhả.
2. **Chặn reasoning trước history/caption fan-out.** `tts_text_transforms` chỉ được tài liệu hóa là sửa text trước TTS; không phải cam kết scrub chat context/UI. ThinkFilter phải ở nhánh LLM output đã kiểm, chẳng hạn `llm_node`, trước khi text được phân phối; giữ tool calls/usage/terminal ordering. Tắt hoặc cấu hình explicit built-in Markdown/emoji transforms để không xử lý hai lần.[^nodes][^text]
3. **Đặt modality explicit.** RoomIO bật text input mặc định; `lk.chat` từ linked participant ngắt speech và tạo reply. L0 voice-only nên `text_input=False`, nhưng giữ transcription output. Nếu sản phẩm cần typed chat, mở profile hybrid riêng, kiểm text/audio hook paths và dùng `conversation_item_added` cho committed messages.[^roomio][^text]
4. **Đặt AGC và pre-connect policy explicit.** Worker Python có built-in AGC; browser cũng có AGC nên phải A/B chuỗi hai tầng. Source tự disable AGC khi noise cancellation được cấu hình trực tiếp nếu không override; không dựa vào implicit behavior. Pre-connect audio là input bổ sung trước media bình thường, cần consent/timeout/no-duplicate gate; baseline có thể tắt cả client và worker.[^audio][^roomio]
5. **Đừng mặc định VAD-only nghĩa là không preload EOT.** Source `_preload.py` có thể preload local EOT (~244 MB theo comment) trong forkserver dù session không dùng detector. Với source/version tương ứng, `LIVEKIT_AGENTS_PRELOAD_LOCAL_INFERENCE=0` bỏ preload cả bundled VAD lẫn EOT; custom Silero vẫn cần setup riêng. Đây là opt-out preload, không phải global cấm inference/network. Đo RSS/startup/no-egress trên image pin.[^preload]

### P1 — frontend và độ rõ của thiết kế

6. **Dùng frontend Session APIs nếu version pin hỗ trợ.** `Session` + endpoint/custom `TokenSource` quản lý connect/dispatch/cleanup; lower-level `Room.connect` vẫn hợp lệ. Không dùng Cloud sandbox token server trong no-egress profile. Backend vẫn authorize request và phải có một đường dispatch duy nhất. Phân biệt frontend Session với Python AgentSession.[^frontend][^auth]
7. **Caption renderer cần xử lý interim/final và lỗi stream.** Dùng text streams, không `TranscriptionReceived`/`useTrackTranscriptions` deprecated. Upsert theo identity/track/`lk.segment_id`, replace interim khi `lk.transcription_final=true`; catch abort/reconnect để không nhân đôi hoặc giữ caption lỗi. Nếu bật JSON timing, client phải decode JSON; không giả mọi chunk có timestamps.[^text]
8. **Bổ sung prompt contract tiếng Việt.** Identity/goal/guardrails, trả lời plain text 1–3 câu, hỏi một câu mỗi lần, giữ corrections/phủ định, không lặp acknowledgment hoặc hỏi lại fact đã biết. Không copy SSML/emotion tags/phoneme syntax của vendor vào engine local chưa hỗ trợ. Python modality-aware `Instructions` còn beta, chỉ cần khi mở hybrid.[^prompting][^instructions]
9. **Sửa mô hình prewarm theo docs/source.** `setup_fnc` warm job processes trước khi nhận job; `num_idle_processes` ảnh hưởng RAM và startup. Không mô tả mọi asset đều được parent worker load một lần rồi chia sẻ. SDK forkserver preload là cơ chế riêng, phụ thuộc OS/start method.[^options][^preload]

### P2 — L1 hoặc workflow mở rộng

10. **Thử native flush trước scheduler mới.** `FlushSentinel` trong `llm_node` có thể kết thúc speech segment nhưng giữ một SpeechHandle/assistant message; từ Python 1.6.0 có per-segment playout. Dùng spike để xem có đáp ứng clause policy không; nó không thay normalizer mapping hay custom PCM adapter.[^nodes]
11. **Handoff phải truyền context/state tường minh.** Agent mới mặc định có LLM history mới; session history vẫn là lịch sử tổng. Chọn `chat_ctx.copy(exclude_instructions=True)` hoặc summary/facts phù hợp, không coi handoff tự bảo toàn knowledge. Typed `session.userdata` là state chung; task nhận quyền tạm thời rồi trả typed result. Không tạo thêm participant/worker cho mỗi role. Per-agent model/turn overrides cũng phải tuân no-egress, voice và endpoint policy.[^handoffs][^tasks]
12. **Alignment là integration có version gate.** Docs có `use_tts_aligned_transcript=True`, sentence timing qua StreamAdapter và `TextOutputOptions.json_format=True`. `transcription_node`/`TimedString` được đánh dấu experimental; custom timing/mapping phải test cả transcription lẫn history, không chỉ UI.[^text]

## 4. Agent Builder không thay SDK trong profile này

Builder triển khai trực tiếp lên LiveKit Cloud, dùng các model Inference; limitations hiện tại bao gồm model plugins, workflows/handoffs/tasks, realtime models và tests. Vì vậy **không đưa Builder vào data/control plane OSS/no-egress**. Có thể dùng như tham khảo prompting nếu chấp nhận Cloud, nhưng export code không chứng minh custom ASR/TTS, privacy hay latency parity.[^builder]

Cloud là hai trục riêng: nơi host agent và media transport. Enhanced noise cancellation phụ thuộc Cloud transport, không phải chỉ vị trí worker; browser WebRTC AEC/NS vẫn dùng được trong OSS. Giữ profile entirely self-host, không bật Cloud-only capability từ sample code.[^noise][^quickstart]

## 5. Version và phạm vi kiểm chứng

- Changelog được tra trả **Python Agents 1.8.6, phát hành 2026-10-09**. Đây là candidate nghiên cứu, không phải version triển khai đã pass. Có fix liên quan spoken history khi TTS lỗi, preload local inference và event-loop shutdown — phải có regression tương ứng.[^release]
- Code search trả cùng commit `3f479e242428d5fa9a7208810f036bbb8ccf9a48` như tài liệu gốc. Không suy ra commit này chính là release 1.8.6.
- Comment `TurnDetectionMode` trong source vẫn mô tả auto-selection cũ khác docs. Không dựa vào comment/default; explicit `turn_detection="vad"` và startup/no-egress test tránh ambiguity.[^turn-source][^detector]
- Skill vận hành nói parent prewarm rồi children inherit quá khái quát. Đối chiếu job-process setup trong docs và OS-specific SDK preload trong source thay vì biến lời khuyên đó thành invariant triển khai.[^options][^preload]
- Giữ G1–G7. Bổ sung gate pause/resume, reasoning trong history/captions, text-input rejection, AGC/pre-connect, transcript upsert và preload/RSS. Chưa gate nào được chạy trong review này.

## 6. Nguồn và locator

[^quickstart]: [Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md), Requirements → LiveKit Cloud/self-host adaptation; Agent code; Server startup modes.
[^builder]: [Agent Builder](https://docs.livekit.io/agents/start/builder.md), Overview, Models, Other features, Convert to code, Limitations.
[^prompting]: [Prompting guide](https://docs.livekit.io/agents/start/prompting.md), Prompt design, Output formatting, Voice realism, Testing and validation.
[^frontend]: [Frontends](https://docs.livekit.io/frontends/), Building frontends; [Session management](https://docs.livekit.io/frontends/build/sessions.md), Overview, Session lifecycle, Session messages.
[^auth]: [Authentication](https://docs.livekit.io/frontends/build/authentication.md), TokenSource; [Token endpoint](https://docs.livekit.io/frontends/build/authentication/endpoint.md), Endpoint schema → Request/Response, Sending authentication headers.
[^sessions]: [Agent sessions](https://docs.livekit.io/agents/logic/sessions.md), Overview, Session lifecycle/RoomIO.
[^audio]: [Speech and audio](https://docs.livekit.io/agents/multimodality/audio.md), Instant connect, Automatic gain control, Preemptive speech generation, session.say, SpeechHandle.
[^text]: [Text and transcriptions](https://docs.livekit.io/agents/multimodality/text.md), Text input, Text transforms, Accessing from AgentSession, TTS-aligned transcriptions, Timed transcripts, Receiving text streams.
[^turns]: [Turns overview](https://docs.livekit.io/agents/logic/turns.md), VAD only, Interruption mode, False interruptions; [Silero](https://docs.livekit.io/agents/logic/turns/vad.md), Prewarm, Configuration.
[^detector]: [Turn detector](https://docs.livekit.io/agents/logic/turns/turn-detector.md), Supported languages, Default model selection, Text turn detector → Deprecated/Supported languages.
[^nodes]: [Pipeline nodes](https://docs.livekit.io/agents/logic/nodes.md), On user turn completed, STT node, LLM node → flushing/per-segment playout, TTS node.
[^handoffs]: [Agents & handoffs](https://docs.livekit.io/agents/logic/agents-handoffs.md), Passing state, Context preservation, Per-agent configuration.
[^tasks]: [Tasks & task groups](https://docs.livekit.io/agents/logic/tasks.md), Overview, Defining a task.
[^instructions]: [Modality-aware instructions](https://docs.livekit.io/agents/multimodality/instructions.md), Overview → Beta in Python, How variants are applied.
[^noise]: [Noise & echo cancellation](https://docs.livekit.io/transport/media/noise-cancellation.md), Overview, Agents → Cloud transport requirement; WebRTC cancellation.
[^options]: [Agent server options](https://docs.livekit.io/agents/server/options.md), Prewarm function, Agent server load, Health check endpoint, Drain timeout.
[^deployment]: [Custom deployments](https://docs.livekit.io/deploy/custom/deployments.md), Networking, Memory and CPU, Rollout/Load balancing.
[^roomio]: [RoomIO source](https://github.com/livekit/agents/blob/3f479e242428d5fa9a7208810f036bbb8ccf9a48/livekit-agents/livekit/agents/voice/room_io/types.py), `AudioInputOptions`, `AudioOutputOptions`, `RoomOptions`, `_default_text_input_cb`. **Observed**, không runtime proof.
[^turn-source]: [Turn source](https://github.com/livekit/agents/blob/3f479e242428d5fa9a7208810f036bbb8ccf9a48/livekit-agents/livekit/agents/voice/turn.py), `_StreamingTurnDetectorStream`, `_StreamingTurnDetector`, `TurnDetectionMode`, options defaults. **Observed**.
[^activity]: [Agent activity source](https://github.com/livekit/agents/blob/3f479e242428d5fa9a7208810f036bbb8ccf9a48/livekit-agents/livekit/agents/voice/agent_activity.py), `_interrupt_by_audio_activity`, `_start_false_interruption_timer`, `_cancel_speech_pause`. **Observed**; private implementation không phải public API để gọi trực tiếp.
[^preload]: [SDK preload source](https://github.com/livekit/agents/blob/3f479e242428d5fa9a7208810f036bbb8ccf9a48/livekit-agents/livekit/agents/ipc/_preload.py), module docstring, `ENV_PRELOAD_LOCAL_INFERENCE`, `_local_inference_models`. **Observed**; pin/compatibility gate trước áp dụng.
[^release]: [Agents 1.8.6 release](https://github.com/livekit/agents/releases/tag/livekit-agents%401.8.6), What's Changed: TTS failure spoken history, local inference preload opt-out, job-loop close. **Reported** qua `lk docs changelog`.
