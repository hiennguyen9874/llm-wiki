---
type: Synthesis
title: Vietnamese Speech Pipeline Design
description: Thiết kế speech pipeline tiếng Việt không chọn LLM chính, ghép VAD/endpointing, ASR, TTS và deploy tools thành năm cấu hình với hợp đồng streaming, cancellation và gate đánh giá.
tags: [pipeline, vietnamese, vad, stt, tts, streaming, deployment, architecture]
status: draft
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T04:54:02Z }
stale_after: 2027-10-07
sources:
  - { id: asr, resource: vietnamese-realtime-asr-selection.md, kind: synthesis }
  - { id: tts, resource: vietnamese-realtime-tts-selection.md, kind: synthesis }
  - { id: deploy, resource: speech-deployment-tools-comparison.md, kind: synthesis }
  - { id: silero, resource: silero-vad.md, kind: synthesis }
  - { id: turns, resource: turn-detection-models.md, kind: synthesis }
  - { id: noise, resource: speech-enhancement-before-asr.md, kind: synthesis }
  - { id: barge, resource: voice-agent-barge-in-and-echo-handling.md, kind: synthesis }
  - { id: hf, resource: speech-to-speech-pipeline.md, kind: synthesis }
  - { id: frameworks, resource: voice-agent-frameworks.md, kind: synthesis }
  - { id: vieneu, resource: vieneu-tts-v3-turbo.md, kind: synthesis }
  - { id: qwen, resource: qwen3-asr-family.md, kind: synthesis }
  - { id: nemo, resource: nemo-speech-cpp.md, kind: synthesis }
  - { id: vox, resource: voxcpm2.md, kind: synthesis }
  - { id: moss, resource: moss-tts-local-transformer-v1-5.md, kind: synthesis }
  - { id: audio, resource: audio-cpp-framework.md, kind: synthesis }
  - { id: diar, resource: nemotron-3-diarization.md, kind: synthesis }
---

**Synthesis, chưa triển khai/benchmark:** với hội thoại tiếng Việt tương tác, thử stack Silero ONNX CPU → endpoint manager (Smart Turn tùy chọn + timeout) → Nemotron 3.5 ASR streaming → giao diện LLM bên ngoài → clause chunker/normalizer → VieNeu v3 Turbo streaming → bounded playback. Dùng NeMo-Speech.cpp hoặc NeMo reference cho ASR, SDK/API VieNeu cho TTS, Pipecat/custom gateway cho orchestration. Nếu cần MVP ít tích hợp, bắt đầu HF speech-to-speech + faster-whisper Turbo + VieNeu API; nếu cần accuracy hơn, A/B Qwen3-ASR single-pass hoặc thêm final-pass có điều kiện. Đây là thứ tự thử theo nhu cầu, không khẳng định một stack thắng quality/latency tiếng Việt.[^asr][^tts][^deploy][^hf][^frameworks]

## Phạm vi và cơ sở quyết định

- Giả định thiết kế: user/bot một-một, mic browser/mobile hoặc call audio; ưu tiên self-host và hội thoại. Không chọn, fine-tune hay budget model LLM chính; vẫn định nghĩa text-stream/cancel boundary để vòng speech chạy hoàn chỉnh (**Synthesis**).
- Đã đọc toàn bộ index/log và bốn trang `type: Synthesis` trước; sau đó hai model surveys, hai pipeline reports và các concept model/runtime/control liên quan. Log ghi các Query selection và Update reconciliation, không phải có các type `Answered`/`Reconciled` riêng. Structural check trước thao tác trả 149 concepts/1 index (**Observed**, kiểm tra session 2026-10-07).
- ASR/TTS capabilities và benchmark là **Reported** qua concepts có locator về nguồn; lựa chọn, cấu hình thử, protocol và topology dưới đây là **Synthesis**. Framework/Smart Turn/noise/barge-in còn nhiều evidence từ AI reports, không primary-verified.[^asr][^tts][^frameworks][^turns][^noise][^barge]
- Chưa có hardware, số phiên, domain, commercial boundary và SLA cụ thể. Không coi các model chưa benchmark là yếu; không gọi snapshot trong repo là khảo sát toàn thị trường (**Synthesis**).

## Năm cấu hình ghép model và deploy tool

| Profile | ASR + runtime | TTS + runtime | Orchestration/transport | Chọn khi nào / gate |
|---|---|---|---|---|
| A — MVP turn-final | Whisper large-v3-turbo + Faster-Whisper/CTranslate2; HF pipeline backend | VieNeu v3 Turbo SDK/API | HF speech-to-speech + OpenAI-compatible external LLM; WS/LAN hoặc WebRTC | Ít adapter hơn; chờ endpoint rồi decode. Không native ASR streaming; phải test TTS schema và cancellation.[^asr][^hf][^vieneu] |
| B — native streaming baseline | Nemotron 3.5 0.6B, `vi-VN`, thử chunk160/320ms; NeMo reference hoặc NeMo-Speech.cpp Q8 | VieNeu v3 Turbo GPU streaming hoặc ONNX CPU | Pipecat/custom gateway; WebRTC khi cần remote barge-in | Thử đầu tiên nếu cần partial sớm; ASR custom adapter có thể cần, không có bằng chứng plug-and-play cho tổ hợp này.[^asr][^nemo][^frameworks][^tts] |
| C — quality-oriented single-pass | Qwen3-ASR0.6B→1.7B; qwen-asr vLLM hoặc WLK windowed | VieNeu; A/B VoxCPM2 bằng `voxcpm.generate_streaming` + service riêng | Gateway/agent framework, transcript revision policy | Chấp nhận buffering/rollback. Toolkit streaming gốc không batch/timestamps; Vietnamese streaming WER chưa có matched result.[^asr][^qwen][^vox] |
| D — two-pass selective | Nemotron live partial + Qwen1.7B hoặc ChunkFormer RNNT large113M final-pass | VieNeu; thay VoxCPM2 nếu listening/cost gate tốt hơn | Gateway sở hữu transcript revisions, commit và cancel | Số/tên/phủ định/domain cần final recheck; thêm compute/lag và logic reconciliation. Chưa benchmark toàn tổ hợp.[^asr][^tts] |
| E — CPU/edge | Nemotron3.5 Q8/NeMo-Speech.cpp; RealtimeSTT/sherpa INT8 là packaging khác cần gate; hoặc Whisper CT2 INT8 turn-final | VieNeu ONNX fp32; INT8 chỉ nếu VNNI phù hợp; A/B Supertonic3/Kokoro vi ONNX, Nano cho weak CPU | Gateway local/embedded, WS loopback; pre-stage models | Không cam kết full stack realtime trên CPU bất kỳ. Không giữ Parakeet final mặc định của RealtimeSTT vì thiếu vi; alternatives có license/streaming limits.[^deploy][^asr][^tts][^nemo][^vieneu] |

**Synthesis:** không triển khai D ngay từ đầu nếu B/C đã đạt domain accuracy. Hai-pass có thể chỉ bật cho critical spans hoặc quality review; final recognizer không phải ground truth. Nếu output phụ thuộc final correction thì chưa phát âm/phát side effect trước commit. Nếu speculation đã chạy trên partial, discard/cancel khi revision đổi.[^asr][^hf][^barge]

## Lựa chọn ASR: quality, latency và checkpoint là các trục riêng

Các số là **Reported**, vai trò là **Synthesis**.[^asr]

| Candidate | Bằng chứng tiếng Việt | Đường deploy / hạn chế |
|---|---|---|
| Nemotron3.5 600M | FLEURS vi-VN WER12.87/12.29 tại chunk160/320ms;11.18 tại1120ms | Native cache-aware RNNT; NeMo/NeMo-Speech.cpp. OpenMDW-1.1; explicit locale tránh default English. Chunk không phải total first-stable-text latency. |
| Qwen3-ASR1.7B /0.6B | Offline FLEURS-vi5.55/8.52; MLC-SLM-vi14.92/17.67 | Apache-2.0; qwen-asr/vLLM, WLK windowed alternative. Paper streaming dùng2s chunk,5-token fallback,bốn chunk unfixed; không vi streaming WER. |
| Whisper Turbo809M | Multilingual vi; chưa matched vi streaming score | CT2/Faster-Whisper final; WLK SimulStreaming/LocalAgreement cho live captions. Giữ VAD, confidence/hallucination checks; không decode độc lập mỗi20/200ms. |
| ChunkFormer RNNT113M | VIVOS2.49/CMV5.18; chuyên vi | Final-pass/ONNX candidate, CC-BY-4.0. CTC110M là NC; small streaming-trained checkpoint availability/license/WER còn chưa rõ. |
| PhoWhisper medium/large | Finetune vi; large VIVOS4.67/CMV8.14 | BSD-3-Clause, turn-final; CT2 conversion cần test parity. Không native streaming evidence. |
| Fun-ASR-MLT800M /Cohere2B | Có vi trong language list | Final challengers, Apache-2.0; thiếu matched vi score/latency. Không chuyển support từ MLT sang Nano zh/en/ja hoặc WLK SenseVoice. |
| ZipFormer30M vi | Compact, author CPU file throughput | Research, NC-ND và chưa native streaming protocol. Không default commercial edge pick. |

Không xếp Qwen5.55 trước Nemotron12.29 như cùng realtime protocol; không xếp VIVOS trước FLEURS. Qwen92ms TTFT là decode request có audio~2min sẵn ở concurrency1, không mic latency và không capacity128 cùng92ms. Name0.6B/1.7B của Qwen chưa gồm toàn encoder/projectors/cache (**Reported/Synthesis**).[^asr][^qwen]

Parakeet25-European/derivatives, Distil-Whisper English, Voxtral compiled language lists, Audio8 Infinite zh/en và English EOU không đủ Vietnamese scope để thay baseline. Confucius4-R2T2 chưa explicit vi evidence. Không chọn model chỉ vì English leaderboard hoặc chữ multilingual.[^asr]

## Lựa chọn TTS và đường phục vụ

Capabilities là **Reported**; deployment priority là **Synthesis**.[^tts]

| Candidate | Model + deploy path | Tradeoff/gate |
|---|---|---|
| VieNeu v3 Turbo | Vietnamese-first vi/en; ONNX CPU/PyTorch GPU; SDK `infer_stream` hoặc API `/v1/audio/speech` | Baseline triển khai,48kHz, preset/cloning. `style` ignored; đọc theo reference. FAQ Apache/commercial nhưng roadmap personal-use: rà use scope trước release.[^vieneu] |
| VoxCPM2 | 30languages có vi, cloning/design/style; `voxcpm` Python streaming, API adapter tự làm | ~8GB VRAM và RTF~0.3 RTX4090 theo card, không TTFA/vi MOS. Apache; GPU quality challenger. Nano-vLLM là accelerator pointer chưa inspect.[^vox] |
| Supertonic3 | ~99M, vi trong31languages, ONNX SDK | CPU challenger, OpenRAIL-M. `synthesize` trả full waveform trong capture; short-clause synthesis không đồng nghĩa frame streaming; không dùng RTFv2 cho v3. |
| Kokoro Vietnamese | ONNX/PyTorch, vig2p và voicepacks | CPU A/B; Apache card, chưa numeric quality/TTFA/streaming. Kokoro support trong Speaches/HF không chứng minh checkpoint vi compatible. |
| MOSS-TTS Local v1.5 | vi trong31, HF/SGLang-Omni, language tags/cloning/pause | GPU streaming challenger, Apache card, thiếu numbers. Native48kHz stereo nhưng PCM example mono: xác nhận channels/framing; không gán cùng path cho flagship8B.[^moss] |
| Higgs3 /Fish S2 Pro | Expressive, vi scope; SGLang-Omni; Higgs còn vLLM-Omni | Chỉ research hoặc commercial agreement phù hợp. H100/H200 claims không chứng minh vi TTFA hoặc thắng listening. |
| G-OmniVoice /Gwen-TTS | Vietnamese finetunes; `omnivoice`/`qwen-tts` | Cloning/listening challengers; chưa streaming/latency. G-OmniVoice base-NC/tokenizer lineage và Gwen TikTok data rights còn pending. MOS7.685 trong G card thiếu scale/protocol nên không chuyển thành MOS1–5 winner. |
| VieNeu Nano /sanoTTS vi | Nano48M ONNX24kHz finished chunks; sano voicevi1.46M piperlite22.05kHz | Edge tradeoff; Nano English/code-switch yếu hơn; sano GPL và vi unscored. Không chuyển English MCU benchmarks sang voice vi. |

Official Qwen3-TTS không có vi trong10-language support; Faster Qwen3-TTS/vLLM-Omni không tự thêm Vietnamese. Fine-tune Gwen là checkpoint khác và cần runtime/streaming parity riêng.[^tts]

VieNeu reported RTX3060 warm streaming1:~115ms TTFA,RTF0.49;16:185ms median,RTF0.59,max339ms khi start đồng loạt. CPU fp32:260–400ms,RTF0.55–0.61;CPU INT8:140–195ms,RTF~0.35 và cần VNNI. Bulk RTF0.011–0.02 không đại diện một stream,16streams không bằng16 concurrent toàn pipelines. Tất cả chưa reproduce.[^vieneu]

## Kiến trúc hoàn chỉnh đề xuất

Sơ đồ là **Synthesis**, không implementation đã test.[^asr][^tts][^noise][^barge][^hf]

```text
Client mic + AEC + capture timestamp
  → WebRTC Opus / WS PCM
  → decode/resample/ring buffer tại gateway
      ├→ optional light denoise → Silero CPU → endpoint/barge-in policy
      ├→ AEC-processed, otherwise unenhanced audio → ASR streaming state
      └→ turn audio buffer → optional final recognizer
  → transcript revisions + validity/entity checks
  → COMMITTED user turn → external LLM interface (không chọn model)
  → meaningful clause buffer → Vietnamese spoken-text normalizer
  → TTS router/adapter → audio stream metadata + chunks
  → bounded client queue → playback + played-offset acknowledgement
                        ↖ cancel generation trên toàn đường
```

### 1. Audio ingress và privacy

**Synthesis:** browser capture dùng AEC khi loa ngoài, noise suppression/AGC A/B thay vì cho là luôn giúp. Transport20ms frames có thể reblock512samples/32ms ở16k cho Silero; không bắt VAD/ASR/TTS dùng cùng chunk length. Gateway canonical ASR audio16k mono; telephony8k decode đúng rồi resample, không coi upsampling khôi phục thông tin mất. Output giữ native sample rate đến playback adapter; chỉ resample khi transport yêu cầu.[^silero][^barge][^hf]

Giữ200–300ms pre-roll là **starting design**, không cutoff measured. Một VAD/ASR state riêng mỗi session; không dùng cache người này cho người kia. Audio thiếu packet/gap cần policy rõ, không concatenate lệch timeline. Denoise optional ở VAD branch; ASR baseline là AEC audio, A/B enhancer riêng vì compiled evidence conflicting và không vi studies.[^silero][^noise]

**Synthesis privacy requirements:** TLS/auth tại gateway, service ports private, giới hạn upload/reference duration và request size; không cho client tùy ý trỏ reference URL/path. Logs mặc định metadata không audio/transcript; nếu cần corpus đánh giá phải opt-in, access controls, retention và consent. Speaker embeddings/cloning refs cũng có disclosure boundary, không ghi vào operational log. HF pipeline có content-free default nhưng optional LLM proxy không có auth/throttling riêng: giữ proxy off hoặc bảo vệ bằng gateway.[^hf][^barge][^tts]

### 2. VAD, endpointing và turn ownership

Silero detects speech, không hiểu end-of-turn. Smart Turn là candidate prosodic detector có Vietnamese scope qua secondary AI report; Namo là candidate A/B nhưng primary/license/eval chưa đủ; LiveKit framework transport không có nghĩa detector compiled14languages có vi.[^silero][^turns][^frameworks]

Starting settings **Synthesis**, không API copy-paste hoặc production defaults:[^silero][^turns][^asr][^barge]

| Policy | Điểm bắt đầu để tune |
|---|---|
| Input |16kHz mono;20ms transport;512samples VAD blocks |
| Silero |threshold~0.5;noise threshold tune riêng, không raise tự động theo một số cố định |
| End candidate có Smart Turn |200–300ms silence rồi classifier; nếu incomplete tiếp tục giữ turn |
| Không semantic detector |500–800ms silence, tune theo tốc độ nói và pause |
| Fallback |1.2–1.5s silence như upper-wait candidate; không phải cộng thêm sau mỗi positive |
| ASR |Nemotron `vi-VN`,160/320ms trial;Qwen separate buffered policy |
| Barge-in |clean:thử150–200ms;noisy:thử300–500ms speech evidence; preserve short intentional commands |

Chỉ một owner (gateway hoặc tracker framework) quyết định turn close/reopen/commit. VAD/ASR/TTS servers cung cấp signals, không mỗi service tự finalization. HF tracker mô tả soft-end/reopen/revision/output-gating; có thể học control design nhưng không chép default64ms/800ms/2s thành cùng policy với bảng trên (**Reported/Synthesis**).[^hf]

### 3. Transcript revisions và safety boundary

**Synthesis schema proposal**, không vendor event schema:[^asr][^hf]

```text
session_id, turn_id, revision, generation_id, sequence
asr.partial(text, stable_prefix_if_available)
asr.final(text, model_id, language, quality_flags)
turn.commit(turn_id, revision)
text.chunk(generation_id, chunk_id, raw_text, spoken_text)
audio.start(generation_id, format, sample_rate, channels)
audio.chunk(generation_id, chunk_id, sequence, payload)
audio.played(generation_id, played_sample_offset)
response.cancel(generation_id)
```

- Partial dùng captions; chỉ speculative compute trước commit, không side effects. Stable prefix không tự là confidence hoặc final truth.
- Final-pass D chạy lại turn audio giữ nguyên, không đổ full transcript lên partial stream gây duplicate; final event thay một revision, chỉ commit once. Critical ambiguity ở số/tên/phủ định → ask-back interface, không majority vote thành sự thật.
- Confidence scales giữa ASR models không calibrated; missing confidence giữ unknown. Whisper blacklist chỉ là signal kết hợp acoustic evidence, không xóa mọi câu chứa `subscribe` hay reject mọi short turn: user có thể nói thật từ đó hoặc nói “không/dừng”.
- Session closed/disconnected → release ASR cache, cancel inference nếu hỗ trợ, flush queues và không dispatch stale callbacks.

### 4. Text→speech bridge tiếng Việt

**Synthesis:** external LLM adapter chỉ yêu cầu streaming text/done/error/cancel và generation correlation, không model choice. Chunker flush meaningful clauses/sentences, không từng token và không chờ full answer. Keep incomplete number/date/abbreviation/entity together; first short clause giảm wait nhưng nghe A/B boundary prosody. Strip markup/URLs theo spoken policy, giữ punctuation phục vụ prosody.[^tts][^hf]

Normalizer tách display/raw text khỏi spoken text: tiền,số điện thoại,số đếm/ngày/giờ,%,units,abbreviations,tên riêng và code-switch. Đọc số điện thoại từng digit khác số tiền; ngày ambiguity cần domain rule, không tự đoán. Unicode NFC/diacritics, domain pronunciation dictionary và regression prompts là requirement đề xuất; wiki chưa chọn thư viện Vietnamese normalizer đã verified.[^tts]

Audio-output streaming ≠ incremental text-input. VieNeu/VoxCPM2 APIs nhận text sẵn rồi output chunks; clause-level calls là bridge đề xuất, không gọi đó là native bi-streaming. Adapter declares dtype/sample_rate/channels/framing: VieNeu SDKfloat32/48k vs HTTPs16le/48k; MOSS native stereo vs examplemono cần contract test. OpenAI-compatible path không đủ để chỉ đổi URL.[^tts][^vieneu][^moss]

### 5. Barge-in, cancellation và history

**Synthesis:** giữ mic on + AEC; speech during bot output mở candidate interrupt. Sau calibrated gate, increment generation, cancel external LLM/TTS requests, clear text/server/client queues, drop mọi late chunks của old generation. Đo cả user-speech→stop-audible và time-to-release-compute, không chỉ request disconnect. SDK có thể không cancellable bên trong; đó là deployment gate, không capability đã chứng minh.[^barge][^hf]

Noisy gating và speaker lock optional phải tune; embedding match không phải authentication và diarization không phải biết user danh tính. Không mặc định mọi “ừ/vâng/ok” là backchannel: domain có thể coi đó là xác nhận quan trọng. Save only played portion/offset cho dialogue history, không append toàn generated text khi user chỉ nghe phần đầu. Không có token/audio alignment thì chỉ claim played offset, không exact words (**Synthesis**).[^barge][^diar]

### 6. Diarization chỉ khi nhiệm vụ cần

Một-user agent: chưa thêm diarizer vào critical path. Meeting/multi-user: giữ separate tracks nếu đã có participant identity; audio-mix fallback thử Nemotron3Diarization/NeMo-Speech.cpp,up-to8speakers,0.32/0.64/1.04s input-buffer profiles theo card. Những numbers không gồm compute hay speaker identity verification; vi/overlap DER riêng chưa established (**Reported/Synthesis**).[^diar][^nemo]

## Deploy tools: chọn đúng tầng, không ép một engine phục vụ tất cả

| Tầng | Lựa chọn / vai trò | Evidence boundary |
|---|---|---|
| CPU VAD |Silero ONNX |Model/runtime detector, không dialogue orchestrator.[^silero] |
| Nemotron inference/server |NeMo reference;NeMo-Speech.cpp native HTTP/WS/C SDK |Q8 runtime compatibility phải test;27ms CPU/160ms chunk figure là EN,không3.5vi.[^nemo] |
| Qwen ASR |qwen-asr/vLLM;WLK windowed alternative |Exact streaming protocol/cache/concurrency path cần riêng;WLK causal English-only, không vi.[^asr][^qwen] |
| Whisper inference/live policy |Faster-Whisper CT2;WLK SimulStreaming/LocalAgreement hoặc RealtimeSTT |WLK không phải LiveKit Agents; không hai segmentation owners.[^deploy] |
| Vietnamese TTS |VieNeu SDK/API;VoxCPM2 Python adapter;ONNX TTS service |Không tài liệu generic vLLM-Omni phục vụ VieNeu/VoxCPM2 trực tiếp; model-specific recipes trước.[^tts][^vieneu][^vox] |
| Multi-stage GPU serving |SGLang-Omni cho MOSS Local/Higgs/Fish;vLLM-Omni khi exact checkpoint recipe có evidence |Không cần cả hai mặc định;ASR HTTP transcription support không chứng minh native audio WS path.[^deploy][^moss] |
| Native multi-model |audio.cpp;transcribe.cpp STT-centric |Alternate implementation sau reference parity. VieNeu community port guide/parity chưa inspect;GGUF artifacts khác runtime có thể khác layout.[^audio][^deploy] |
| Orchestration |HF s2s cho MVP;Pipecat custom cascade;LiveKit Agents cho RTC/SIP |Pipecat/LiveKit comparison secondary;plugins hiện hành chưa inspect, custom ASR/TTS adapters có thể cần.[^hf][^frameworks] |

**Synthesis deployment plan:** Docker Compose đầu tiên, một model owner/process thay vì mỗi gateway worker load weights. Tách environment ASR/TTS/ONNX để tránh torch/transformers/CUDA dependency conflicts. Containers đề xuất: public RTC/gateway; private asr-service; optional final-asr-service; tts-service; telemetry. External LLM endpoint nằm ngoài model deployment scope nhưng phải tính contention nếu cùng GPU.[^deploy][^hf][^vieneu]

Pin revision/checksum của runtime/weights/G2P/voicepack/normalizer, pre-stage offline, warm models/graphs và health/readiness chỉ ready sau warmup. Admission cap/max_streams, bounded queues/backpressure/429, per-session rate-limit/deadlines/circuit breaker và cleanup là requirements đề xuất. Không scale gateway workers thành GPU copies; service split qua GPU trước khi Kubernetes/disaggregated Omni trở thành cần thiết (**Synthesis**).[^vieneu][^deploy][^hf]

Khi load/cost tăng, tách streaming ASR và TTS/final-pass sang pools riêng; ưu tiên audio cadence thay batch throughput. CPU ASR/headroom, VRAM/cache/workspace/session và cold start phải đo; không gán1.1GB TTS claim thành total speech budget. Mid-utterance TTS fallback có thể đổi voice: ưu tiên retry/new-clause có báo trạng thái thay stitch hai voices im lặng (**Synthesis**).[^asr][^tts][^vieneu]

## Latency, evaluation và release gates

**Synthesis:** đo critical path, không cộng full audio capture vào endpoint response latency và không double-count compute đã overlap:

```text
last user speech sample
  → endpoint commit
  → accepted final ASR
  → external LLM first meaningful clause
  → TTS first playable samples
  → client first audible sample
```

Đo cả từng edge và tổng last-speech→first-audible,clock/timestamp boundaries rõ. LLM latency là external dependency,speech pipeline không cam kết tổng~1s khi chưa biết endpoint đó. QwenTTFT,VieNeuTTFA,batchRTFx,chunk size và classifier compute là metrics khác nhau.[^asr][^tts][^hf]

Starting gate **Synthesis**, không năng lực đã đo: TTS TTFA P95~250–400ms và RTF P95≤0.7 dưới tải thực; end-to-end mục tiêu theo SLA sản phẩm và external LLM, không derived từ riêng115ms. ProfileC/D có thể chậm hơnB vì buffered/final pass;CPU profile chưa cam kết cùng gate.[^tts][^asr]

1. **ASR corpus:** Bắc/Trung/Nam,tên/số/địa chỉ/phủ định/code-switch,8k call vs16k mic,far-field/noise/silence. Cùng ground truth/normalizer;reportWER/CER và exact critical-span accuracy,tỷ lệ partial sửa,first-stable-text,endpoint→finalP50/P95.
2. **TTS150–300prompts:** blind pairwise Vietnamese listeners,tone/pronunciation/naturalness/voice consistency,cloning và presets riêng;test normalizer/chunk boundaries. Round-trip ASR chỉ proxy,không thay listening.
3. **Turn/barge-in:**pause dài giữa câu,“không/dừng”ngắn,backchannels,background TV,bot echo,user nói đè,cough/keyboard;false-cutoff,missed/false-interrupt,stop-audible và recovery.
4. **Load:**warm/cold,sustained+simultaneous starts,concurrency1/4/8/16,memory/session,queue/stalls,dropped frames,TTS underrun;shared-GPU ASR/TTS/external LLM load. Chỉ nâng concurrency khi đạt P95/cadence,không từ H100 throughput paper.
5. **Contract tests:**48k/24k/unknown rate,mono/stereo,dtype,PCM-vs-WAV/SSE,sequence/revision monotonicity,cancel mid-chunk,disconnect,reconnect,timeouts,OOM,429;no stale audio/no duplicate final/no action on uncommitted text.
6. **Rights/security:**license/runtime/weights/voicepack/data lineage riêng;consent reference,TLS/auth,private model ports,content-free logs;commercial gates VieNeu ambiguity,Fish/Higgs/Omni NC,G finetune lineage,GPL/RAIL/vendor terms.

Các gate tổng hợp từ ASR/TTS/control/server evidence; chưa chạy corpus hay release tests.[^asr][^tts][^barge][^hf][^deploy]

## Quyết định và lộ trình

- **Phase1:**A (HF+WhisperTurbo+VieNeu) để có measurable whole loop;B nếu partial là requirement ngay từ đầu. Warmup,normalizer,explicit audio contracts và logs trước optimizer (**Synthesis**).[^hf][^asr][^tts]
- **Phase2:**A/B Nemotron160/320/560ms vsQwen0.6/1.7B với đúng streaming/turn-final policy;TTS VieNeu vsVoxCPM2,CPU VieNeu vsSupertonic3/Kokoro. Không đổi nhiều component đồng thời (**Synthesis**).[^asr][^tts]
- **Phase3:**thêmD nếu entity-error gain đáng compute/latency;SmartTurn/barge-in sau calibrated false-interruption tests;multi-user mới thêmdiarization. Đổi runtime sangaudio.cpp/native chỉ sau output/latency/parity gate (**Synthesis**).[^asr][^barge][^turns][^audio][^diar]

## Relationships

- Uses [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md) và [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md): ghép shortlist thành profiles/control/deployment, không thay bảng source-specific quality.[^asr][^tts]
- Uses [So sánh công cụ triển khai speech](speech-deployment-tools-comparison.md): phân tầng runtime/API/policy/orchestration, không treat generic server như native streaming.[^deploy]
- Depends on [Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md), [Turn Detection Models](turn-detection-models.md), [Speech Enhancement Before ASR](speech-enhancement-before-asr.md): các starting policies còn secondary và phải tune.[^barge][^turns][^noise]
- Complements [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md) và [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md): thay defaults không vi và giữ LLM model out-of-scope; không supersede lịch sử AI reports.[^hf][^asr][^tts]

## Coverage và giới hạn

- Session chỉ compiled-wiki retrieval và structural check; không mở `raw/`,fetch upstream,install/build,tải weights,nghe audio,inference hoặc benchmark. Source resources ở đây là stable local concepts;footnotes chỉ locator vào section đã đọc,chain raw vẫn nằm trên từng concept.
- Inspected map: index/log,bốn syntheses,ASR/TTS surveys,pipeline reports,HF s2s,WLK,RealtimeSTT,Silero,turn/noise/barge-in/Whisper filters,Nemotron3.5/Qwen/Faster-Whisper/ChunkFormer,VieNeu/VoxCPM2/Supertonic3/Kokoro/MOSS Local,NeMo-Speech.cpp/SGLang/vLLM-Omni/audio.cpp và Nemotron3Diarization. Source-dependent claims ở bảng dựa declared concepts;không claim đọc toàn149concepts/raw artifact closure.
- Secondary AI-report evidence còn trên framework/turn/noise/control,missing implementation/recipe/API docs và quyền weights/voices được kế thừa. Không có model compatibility event được verified;transport/interface propositions không phải deployed APIs. `draft` vì chưa target-hardware load/latency,matched Vietnamese quality/cancellation tests và license review;không đặt `verified`.

[^asr]: [Vietnamese ASR selection](vietnamese-realtime-asr-selection.md) — Định nghĩa realtime; Shortlist và bằng chứng tiếng Việt; Qwen streaming/efficiency; Kiến trúc và hướng triển khai; Chọn runtime; Loại khỏi shortlist; Gate đánh giá; Coverage.
[^tts]: [Vietnamese TTS selection](vietnamese-realtime-tts-selection.md) — Model nào có bằng chứng tiếng Việt; Không trộn throughput; Triển khai realtime hai tầng streaming; Gate chọn model; Contradictions và giới hạn còn mở (G/Gwen,Kokoro,MOSS,sano).
[^deploy]: [Deploy comparison](speech-deployment-tools-comparison.md) — Backend nền; Runtime native; Engine GPU; API server; STT streaming; Orchestration; Benchmark; Shortlist; Coverage/license limits.
[^silero]: [Silero VAD](silero-vad.md) — Key characteristics; Versions and streaming configuration (secondary report); Requirements; Contradictions; Coverage.
[^turns]: [Turn Detection Models](turn-detection-models.md) — Comparison; Operating practice; Coverage (AI-report provenance,primary docs unavailable).
[^noise]: [Speech Enhancement Before ASR](speech-enhancement-before-asr.md) — Practice; Contradictions; Coverage (secondhand studies,not Vietnamese).
[^barge]: [Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md) — Interruption procedure; Echo-avoidance tiers; Noise-robust gating; Transport; Contradictions; Coverage.
[^hf]: [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md) — Architecture; Supported components; Commands; Realtime API/LLM proxy; Endpointing and turn-taking; Multilingual behavior; TTS notes/content-free logging; Coverage.
[^frameworks]: [Voice Agent Frameworks](voice-agent-frameworks.md) — Comparison; Pipecat composition; Coverage (secondary report,plugins/license conditions unresolved).
[^vieneu]: [VieNeu v3 Turbo](vieneu-tts-v3-turbo.md) — Model identity; Runtime and SDK; Serving API and Docker; Benchmarks; Licensing and use rights; Contradictions; Coverage.
[^qwen]: [Qwen3-ASR family](qwen3-asr-family.md) — Inference and serving; Primary-paper clarification (2s chunks,rollback,92ms concurrency1,encoder sizes); Language and audio coverage (aligner no vi); Coverage.
[^nemo]: [NeMo-Speech.cpp](nemo-speech-cpp.md) — Supported applications/models; Performance (Nemotron EN benchmark,not3.5); Server,SDK,source build; Coverage (API/build/benchmark guides unavailable).
[^vox]: [VoxCPM2](voxcpm2.md) — Architecture/training (~8GB); Languages; Capabilities `generate_streaming`; Requirements/inference; License; Coverage (Nano-vLLM pointer uninspected).
[^moss]: [MOSS-TTS Local v1.5](moss-tts-local-transformer-v1-5.md) — Languages; HF inference (stereo48k,12RVQ); SGLang-Omni serving (PCM stream with mono example); Coverage (missing recipe and numbers).
[^audio]: [audio.cpp Framework](audio-cpp-framework.md) — Runtime/backends; Interfaces; Performance/quantization; Coverage (community guide and code missing); GGUF not interchangeable.
[^diar]: [Nemotron 3 Diarization](nemotron-3-diarization.md) — Architecture/I-O; Streaming configurations (buffer latency excludes compute); Inference; Evaluation protocol; Coverage (no matched Vietnamese verification).
