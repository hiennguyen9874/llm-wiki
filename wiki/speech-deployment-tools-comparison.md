---
type: Synthesis
title: So sánh công cụ triển khai speech
description: Phân nhóm và so sánh runtime CPU/edge, engine GPU, API server, pipeline STT streaming và orchestration cho speech, kèm ranh giới streaming, benchmark và license.
tags: [pipeline, stt, tts, vad, serving, deployment, comparison]
status: draft
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T04:37:10Z }
stale_after: 2027-10-07
sources:
  - { id: audio-cpp, resource: audio-cpp-framework.md, kind: synthesis, title: audio.cpp Framework }
  - { id: transcribe-cpp, resource: transcribe-cpp.md, kind: synthesis, title: transcribe.cpp }
  - { id: nemo-cpp, resource: nemo-speech-cpp.md, kind: synthesis, title: NeMo-Speech.cpp }
  - { id: sglang-omni, resource: sglang-omni.md, kind: synthesis, title: SGLang-Omni }
  - { id: vllm-omni, resource: vllm-omni.md, kind: synthesis, title: vLLM-Omni }
  - { id: faster-whisper, resource: faster-whisper.md, kind: synthesis, title: Faster-Whisper }
  - { id: fast-gpu-asr, resource: fast-gpu-asr.md, kind: synthesis, title: Fast GPU ASR }
  - { id: faster-qwen, resource: faster-qwen3-tts.md, kind: synthesis, title: Faster Qwen3-TTS }
  - { id: genie, resource: genie-tts.md, kind: synthesis, title: Genie-TTS }
  - { id: speaches, resource: speaches.md, kind: synthesis, title: Speaches }
  - { id: parakeet-server, resource: parakeet-asr-server.md, kind: synthesis, title: Parakeet ASR Server }
  - { id: parakeet-readme, resource: ../raw/parakeet.md, kind: documentation, title: Parakeet ASR server README }
  - { id: wlk, resource: whisperlivekit.md, kind: synthesis, title: WhisperLiveKit }
  - { id: realtimestt, resource: realtimestt.md, kind: synthesis, title: RealtimeSTT }
  - { id: hf-s2s, resource: speech-to-speech-pipeline.md, kind: synthesis, title: HF Speech-to-Speech Pipeline }
  - { id: voicechat, resource: realtime-voice-chat.md, kind: synthesis, title: RealtimeVoiceChat }
  - { id: frameworks, resource: voice-agent-frameworks.md, kind: synthesis, title: Voice Agent Frameworks }
  - { id: funasr-cpp, resource: fun-asr-nano-gguf.md, kind: synthesis, title: Fun-ASR-Nano GGUF }
  - { id: moss-cpp, resource: moss-transcribe-cpp-gguf.md, kind: synthesis, title: MOSS-Transcribe-Diarize GGUF }
  - { id: omnivoice-cpp, resource: omnivoice-gguf.md, kind: synthesis, title: OmniVoice GGUF }
  - { id: apple-diar, resource: speaker-diarization-coreml.md, kind: synthesis, title: Speaker Diarization Core ML }
  - { id: thestage, resource: thewhisper-large-v3-turbo.md, kind: synthesis, title: TheWhisper-Large-V3-Turbo }
  - { id: whistle, resource: whistle.md, kind: synthesis, title: Whistle }
  - { id: vieneu, resource: vieneu-tts-v3-turbo.md, kind: synthesis, title: VieNeu-TTS v3 Turbo }
  - { id: silero, resource: silero-vad.md, kind: synthesis, title: Silero VAD }
  - { id: turns, resource: turn-detection-models.md, kind: synthesis, title: Turn Detection Models }
  - { id: asr-survey, resource: asr-stt-model-survey.md, kind: synthesis, title: ASR/STT Model Survey }
  - { id: tts-survey, resource: tts-model-survey.md, kind: synthesis, title: TTS Model Survey }
  - { id: cosyvoice, resource: cosyvoice2-0.5b.md, kind: synthesis, title: CosyVoice2-0.5B }
---

Không có một engine tốt nhất cho mọi speech workload. Cần tách **model**, **inference runtime** (bộ chạy model), **API server**, **streaming pipeline** và **orchestration** (điều phối hội thoại): audio.cpp thiên về audio đa tác vụ local; transcribe.cpp chuyên STT đa họ; NeMo-Speech.cpp là native runtime NVIDIA; SGLang-Omni/vLLM-Omni thiên về GPU multi-stage serving; Faster-Whisper/Fast GPU ASR/Faster Qwen3-TTS tối ưu họ model cụ thể; WhisperLiveKit/RealtimeSTT quản lý luồng STT; HF speech-to-speech và framework agent nối cả vòng hội thoại. Đây là **Synthesis**, không phải xếp hạng hiệu năng đã đo.[^audio-cpp][^transcribe-cpp][^nemo-cpp][^sglang-omni][^vllm-omni][^faster-whisper][^fast-gpu-asr][^faster-qwen][^wlk][^realtimestt][^hf-s2s][^frameworks]

## 1. Backend nền: không phải server hoàn chỉnh

Các dòng sau là **Reported** từ concept triển khai; đánh giá phù hợp là **Synthesis**. Không coi việc một model có export là toàn bộ backend hỗ trợ mọi model.

| Backend / toolkit | Vai trò và đường speech đã có bằng chứng | Cách sử dụng hợp lý / giới hạn |
|---|---|---|
| PyTorch / Transformers | HF model inference; HF speech-to-speech có backend local Transformers | Baseline tích hợp/checkpoint mới; không tự thay orchestration hoặc chứng minh serving scale.[^hf-s2s] |
| NeMo toolkit | Canary trong WLK; model tham chiếu cho NeMo-Speech.cpp | Khi cần API NVIDIA gốc; WLK ghi nhận dependency stack nặng. Khác NeMo-Speech.cpp.[^wlk][^nemo-cpp] |
| FunASR | WLK SenseVoiceSmall, HF Paraformer | Toolkit ASR; WLK chỉ cam kết SenseVoiceSmall cho backend đó, không mọi FunASR model.[^wlk][^hf-s2s] |
| CTranslate2 | Engine của Faster-Whisper | CPU INT8 hoặc CUDA cho Whisper-compatible weights; cần conversion tương ứng.[^faster-whisper] |
| ONNX Runtime / sherpa-onnx | Go Parakeet server; RealtimeSTT CPU Nemotron partial + Parakeet final | Hướng CPU/đóng gói ONNX; không đánh đồng sherpa-onnx với ONNX Runtime hay suy ra mọi checkpoint streaming.[^parakeet-server][^realtimestt] |
| ggml / GGUF | audio.cpp, transcribe.cpp, NeMo-Speech.cpp | Native C/C++; GGUF là container, không đảm bảo dùng chung file giữa các runtime.[^audio-cpp][^transcribe-cpp][^nemo-cpp] |
| TensorRT / TRT-LLM / Triton | Fast GPU ASR TensorRT; CosyVoice2 ghi nhận Triton TRT-LLM; TheStage Docker dùng Triton ensemble | Phân biệt ba thành phần, không gọi chung là một engine; exporter/hardware/model phải khớp.[^fast-gpu-asr][^cosyvoice][^asr-survey] |
| MLX / MLX Audio / Core ML | HF pipeline Mac; TheStage Apple SDK; FluidAudio diarization | MLX là đường inference khác Core ML conversion; SDK và export có ràng buộc phiên bản riêng.[^hf-s2s][^thestage][^apple-diar] |
| vLLM / SGLang thường | ASR serving trong survey; phần AR của Omni runtime | Không suy ra engine LLM thường bao trọn codec, vocoder, diffusion hoặc realtime duplex của Omni.[^asr-survey][^sglang-omni][^vllm-omni] |

## 2. Runtime native CPU/edge: so sánh cùng tầng

Thông tin khả năng là **Reported**; cột lựa chọn là **Synthesis**.

| Runtime | Phạm vi | Hardware / interface | Khi nên shortlist | Giới hạn quan trọng |
|---|---|---|---|---|
| [audio.cpp](audio-cpp-framework.md) | TTS, ASR, VAD, diarization, alignment, processing; README v0.9.0 nói 100+ model, 170+ variant gồm cả ngoài speech | CPU/CUDA/HIP/Vulkan/Metal; CLI/server/WebUI; experimental JSON workflow | Cần một runtime local cho nhiều tác vụ audio | CUDA tối ưu nhất; backend và streaming phụ thuộc model; số model không phải số model speech hoặc streaming.[^audio-cpp] |
| [transcribe.cpp](transcribe-cpp.md) | 20 họ STT trong bảng + Sortformer streaming diarizer | CPU/tinyBLAS, Metal/Vulkan/CUDA/ROCm; CLI; Python/TS/Rust/Swift bindings | Cần engine STT đa họ, nhúng vào ứng dụng | Header nói 16 họ, bảng 20 STT + 1 diarizer; catalog kiểm chứng là tuyên bố upstream, chưa tái chạy.[^transcribe-cpp] |
| [NeMo-Speech.cpp](nemo-speech-cpp.md) | Nemotron/Parakeet ASR, diarization, MagpieTTS, translation, VoiceChat | CPU/CUDA/Metal/Vulkan build paths; CLI, HTTP/WS, C SDK; Riva gRPC binary riêng | Ưu tiên native runtime NVIDIA chính thức | Không phải runtime speech mọi vendor; BENCHMARK.md và model-card Magpie/NanoCodec chưa có.[^nemo-cpp] |
| [FunASR llama.cpp runtime](fun-asr-nano-gguf.md) | Fun-ASR-Nano | CPU/edge; llama-funasr-cli; encoder + decoder + VAD GGUF | Muốn ASR Nano zero-Python | Không đồng nhất với llama.cpp generic; guide/code/prebuilt chưa kiểm tra.[^funasr-cpp] |
| [moss-transcribe.cpp](moss-transcribe-cpp-gguf.md) | Joint transcription + diarization + timestamps | CPU C++/ggml; self-contained GGUF, CLI | Offline biên bản có speaker trên CPU | Bằng chứng quant parity chỉ JFK 11 s; không chứng minh DER dài hạn hay realtime streaming.[^moss-cpp] |
| [omnivoice.cpp](omnivoice-gguf.md) | OmniVoice cloning/design | CPU/CUDA/Vulkan/Metal, README cũng nêu ROCm; cặp base + tokenizer GGUF | Cần port native đúng OmniVoice | Khác package audio.cpp; weights CC-BY-NC; card không cung cấp TTFA/throughput để xếp hạng.[^omnivoice-cpp] |
| Needle / [Whistle](whistle.md) | STT, embeddings, keyword biasing; cùng CPU engine với Needle LLM | .cact, Python/CLI/C API; 16.9 MB model | Tiny on-device STT và tool calling chung engine | Đây là model + runtime đi kèm; 7 ngôn ngữ không có vi; benchmark số nằm ở SVG chưa đọc.[^whistle] |

**Lựa chọn:** audio.cpp cho breadth audio; transcribe.cpp cho breadth STT; NeMo-Speech.cpp cho NVIDIA-native. Trong các nguồn đã đối chiếu, chưa có matched benchmark chứng minh runtime nào nhanh nhất trên cùng checkpoint, cùng GPU/CPU, precision và concurrency (**Synthesis**).[^audio-cpp][^transcribe-cpp][^nemo-cpp]

## 3. Engine GPU serving và optimizer theo họ model

| Công cụ | Cơ chế / phạm vi | Điểm nổi bật | Không nên suy ra |
|---|---|---|---|
| [SGLang-Omni](sglang-omni.md) | Multi-stage; scheduler theo stage; shared-memory/NCCL/NIXL/Mooncake; ASR/TTS/omni | Router multi-worker; rõ danh sách Qwen3/Fun/ARK/Nemotron/MOSS ASR và nhiều TTS; CUDA full coverage | Apple Qwen3-ASR, Intel XPU vẫn experimental; không có matched speed comparison với vLLM-Omni.[^sglang-omni] |
| [vLLM-Omni](vllm-omni.md) | KV cache vLLM, OmniConnector disaggregation, AR/DiT paged KV, distributed parallelism | Qwen3-TTS/AuK/Breeze/CosyVoice3; full-duplex engine-owned sessions cho model được nêu | Full-duplex không áp dụng tự động cho mọi TTS/ASR; backend được nêu theo release không phải coverage matrix mọi model.[^vllm-omni] |
| [Faster-Whisper](faster-whisper.md) | Whisper trên CTranslate2; CPU/CUDA, INT8, batch, VAD, word timestamps | Conversion Whisper finetune; Python integration | Generator segments không biến Whisper thành native mic-streaming; cần wrapper/policy.[^faster-whisper][^wlk] |
| [Fast GPU ASR](fast-gpu-asr.md) | Zipformer/Parakeet TensorRT + GPU beam search | Throughput offline batch, FP32/FP16/BF16, word timestamps | Không phải streaming engine; engine build theo GPU/TRT/plugin và batch-duration profile; decoder có thể khác transcript upstream.[^fast-gpu-asr] |
| [Faster Qwen3-TTS](faster-qwen3-tts.md) | Torch CUDA graphs/static KV; GGML qwentts.cpp CUDA/Metal experimental | Clone/custom/design, streaming, cache reference, OpenAI API example | Không phải runtime TTS mọi họ; static/dynamic cache không luôn bit-exact; wheel/dependency cần pin.[^faster-qwen] |
| [Genie-TTS](genie-tts.md) | GPT-SoVITS V2/V2ProPlus → ONNX, CPU-first | Model conversion + Python + FastAPI; gọn | Không hỗ trợ mặc nhiên V3/V4/v5; 1.13 s là first-inference latency, không documented streaming TTFA.[^genie] |

**Synthesis:** chọn SGLang-Omni/vLLM-Omni khi cần nhiều request/model stages và cơ sở GPU serving; chọn optimizer chuyên dụng khi chỉ phục vụ Whisper, Qwen3-TTS hoặc Parakeet/Zipformer. Đây là định hướng kiến trúc, không kết luận optimizer đơn họ luôn chậm hơn Omni ở concurrency cao.[^sglang-omni][^vllm-omni][^faster-whisper][^fast-gpu-asr][^faster-qwen]

## 4. API server: thuận tiện vận hành không đồng nghĩa native streaming

| Server / SDK | Cung cấp | Khi shortlist | Giới hạn |
|---|---|---|---|
| [Speaches](speaches.md) | faster-whisper STT + Piper/Kokoro TTS; OpenAI-compatible; SSE, Realtime API; Docker CPU/GPU | Muốn self-host STT/TTS cùng bề mặt API, dynamic load/offload | Capture chỉ overview; thiếu API schema, license, version, benchmark; không xác nhận full Realtime equivalence.[^speaches] |
| [Parakeet ASR Server](parakeet-asr-server.md) | Go + ONNX Runtime Parakeet TDT V3; REST/SSE; auth; CPU/CUDA Docker | Drop-in cho client Whisper API, fixed model | **Upload toàn bộ audio trước**, rồi stream text khi decode; model/prompt/temperature bị bỏ qua. Không phải native audio-input streaming.[^parakeet-server][^parakeet-readme] |
| [VieNeu SDK/API](vieneu-tts-v3-turbo.md) | CPU ONNX, GPU PyTorch fused CUDA graphs; infer_stream; /v1/audio/speech, voice enrollment, Docker | TTS tiếng Việt, muốn SDK hoặc service chuyên dụng | Pin v3 Turbo; v2 LMDeploy/remote deprecated, không phục vụ v3; int8 CPU cần VNNI; xem mâu thuẫn phạm vi commercial-use.[^vieneu] |
| [TheStage SpeechKit/Apple SDK](thewhisper-large-v3-turbo.md) | Compressed TheWhisper S/M/L/XL, NVIDIA Docker và Apple Core ML | STT Apple on-device hoặc deployment theo vendor | Apple cần online token initialization mỗi process, dù inference local; không phải air-gap hoàn toàn; SDK yêu cầu OS/device riêng.[^thestage] |

OpenAI-compatible thường là **subset API**. Cần test model selection, language, response schema, cancellation, PCM/WAV encoding, sample rate, auth và event ordering trước khi gọi một server là drop-in (**Synthesis**). Parakeet bỏ qua một số field; HF s2s công bố core subset; NeMo công bố subset; Speaches thiếu schema trong capture.[^parakeet-readme][^hf-s2s][^nemo-cpp][^speaches]

## 5. STT streaming pipeline

| Công cụ | Thiết kế | Lợi thế theo tài liệu | Giới hạn |
|---|---|---|---|
| [WhisperLiveKit](whisperlivekit.md) | SimulStreaming/AlignAtt hoặc LocalAgreement; nhiều ASR backend; VAD/VAC, diarization, translation | Meeting/live captions; native WS, OpenAI REST và Deepgram WS subsets; backend Mac/CUDA | Qwen causal tower hiện English-only; HF windowed path khuyên 1 realtime session/GPU; timestamps Qwen HF ước lượng; không bảo đảm overlap speaker output.[^wlk] |
| [RealtimeSTT](realtimestt.md) | Mic/fed-audio recorder, VAD, partial + final, wake words; authenticated production server | App Python, dictation/assistant; CPU profile sherpa-onnx Nemotron partial + Parakeet final | Hai model hai lượt; check target language của cả hai. Recorder VAD không sở hữu finalization của versioned production WS; production guide chưa có.[^realtimestt] |

**Synthesis:** WLK ưu tiên policy transcription, captions, diarization/translation; RealtimeSTT ưu tiên recorder/callbacks/wake words và partial-final engine selection. Cả hai bổ sung tầng streaming trên backend, không thay thế model runtime. Không trộn hai pipeline ở cùng nhánh nếu chưa phân định ai sở hữu segmentation, commit và endpointing.[^wlk][^realtimestt]

## 6. Orchestration và pipeline hoàn chỉnh

Các dòng Pipecat/LiveKit/TEN/FastRTC là **Reported qua báo cáo AI**, chưa đối chiếu primary project docs; khuyến nghị là **Synthesis có điều kiện**.[^frameworks]

| Công cụ | Trọng tâm | Phù hợp | Cảnh báo |
|---|---|---|---|
| Pipecat | VAD/STT/LLM/TTS services, Smart Turn, interruptions; WebRTC/WS/telephony | Custom cascaded voice agent; report đề xuất MVP SmallWebRTC | Qwen3-TTS/VieNeu custom adapter theo snapshot; chưa kiểm tra plugin hiện hành.[^frameworks] |
| LiveKit Agents | WebRTC SFU/SIP, plugin/custom services | Voice agent cần RTC/SIP | Plugin STT/TTS, turn detector và self-host boundary cần primary docs.[^frameworks] |
| TEN Framework | Extension-based, TEN VAD, Agora RTC/WS | Đã dùng Agora/TEN extensions | License ghi Apache-2.0 “with conditions”, điều kiện chưa rõ.[^frameworks] |
| FastRTC | WebRTC qua Gradio; vLLM-Omni demo | Demo/MVP browser | Không có benchmark operational scale trong wiki.[^frameworks] |
| [HF speech-to-speech](speech-to-speech-pipeline.md) | Thread/queue VAD→STT→LLM→TTS; WS/WebRTC core OpenAI Realtime event subset | Đường đi trọn vòng với backend swappable, Mac/GPU/local/hosted LLM | Default Parakeet/Qwen3-TTS không tự tạo stack tiếng Việt; OmniVoice handler chờ cả utterance; LLM proxy bật thêm không có auth/throttling riêng.[^hf-s2s] |
| [RealtimeVoiceChat](realtime-voice-chat.md) | Browser WS + RealtimeSTT + Ollama/OpenAI + RealtimeTTS; barge-in, Docker | Demo hội thoại local tích hợp sẵn | Early preview, tác giả không còn phát triển feature/support chủ động; DeepSpeed/Windows fragile.[^voicechat] |

HF speech-to-speech có README gốc trong kho, còn bảng framework dựa nguồn AI thứ cấp; độ tin cậy provenance khác nhau, không suy ra HF tốt hơn về production chỉ vì nguồn tốt hơn (**Synthesis**).[^hf-s2s][^frameworks]

## 7. Thành phần bổ trợ và công cụ mới chỉ được nhắc

- [Silero VAD](silero-vad.md): PyTorch/ONNX, C++/browser/ExecuTorch và các community wrapper được README nêu; là detector chứ không phải ASR engine hay semantic endpointing. WebRTC VAD và wake-word Porcupine/OpenWakeWord được RealtimeSTT tích hợp (**Reported**).[^silero][^realtimestt]
- [Smart Turn/LiveKit/Namo/TEN turn detection](turn-detection-models.md): quyết định pause có phải end-of-turn; bằng chứng hiện qua AI report. Không dùng số ms classifier thay tổng timeout turn (**Reported/Synthesis**).[^turns]
- [FluidAudio + Core ML diarization](speaker-diarization-coreml.md): iOS17/macOS14+, segmentation/embedding/PLDA; không trả transcript. Legacy artifacts ngoài Community-1 provenance/license scope; chưa có DER/latency số (**Reported**).[^apple-diar]
- whisper.cpp, WhisperX, Whisper-Streaming, WhisperLive, LocalAI, LMDeploy, Photon, mlx-whisper, nano-parakeet, RealtimeTTS có xuất hiện qua integrations/packagings, nhưng chưa đủ primary runtime coverage để lập bảng độc lập ngang audio.cpp/NeMo (**coverage limit**, không có nghĩa tool thiếu năng lực). LocalAI chỉ là production pointer của MOSS port; LMDeploy là legacy VieNeu v2; Photon xuất hiện với Parakeet Redux/Ultra trong ASR survey.[^faster-whisper][^moss-cpp][^vieneu][^asr-survey][^hf-s2s][^voicechat]

## Benchmark: đọc đúng, không xếp hạng chéo

Tất cả số dưới đây là **Reported**, chưa chạy lại:

| Tool | Đo cái gì / điều kiện | Figure | Không đại diện cho |
|---|---|---|---|
| Faster-Whisper | Large-v2, RTX3070Ti, CUDA12.4, beam5, 13 min file | INT8 59 s/2926 MB; batch8 16 s/4500 MB | Partial latency, endpointing hay cùng GPU với NeMo4090.[^faster-whisper] |
| Fast GPU ASR | B300, FP16, beam6, batch256, 157.8 h English | Zipformer 25,108.6 RTFx; Parakeet V3 19,398.7 RTFx | Một người dùng latency thấp hoặc Vietnamese WER.[^fast-gpu-asr] |
| Faster Qwen3-TTS | RTX4090, 0.6B, chunk8, tokenization + inference | TTFA156 ms; source “RTF”4.78 nghĩa tốc độ audio/wall | RTF wall/audio4.78; không so trực tiếp với T4/H100/concurrency khác.[^faster-qwen] |
| NeMo-Speech.cpp ASR | Nemotron EN Q8_0, RTX4090, chunk160 ms | 2.3 ms compute/chunk, 67× realtime | 2.3 ms end-to-final latency; không phải số của Nemotron3.5.[^nemo-cpp] |
| NeMo-Speech.cpp TTS | Magpie Q8_0, RTX4090, audio chunk186 ms | TTFA9 ms; CPU203 ms (CPU không nêu tên) | Chất lượng/TTFA tiếng Việt hoặc matched win trước Qwen.[^nemo-cpp] |
| VieNeu v3 Turbo | RTX3060, streaming1/8/16 streams | TTFA115/164/185 ms median; RTF0.49/0.56/0.59 | Batched offline RTF0.011–0.02; 16stream max339 ms khi đồng loạt bắt đầu.[^vieneu] |
| Genie | i7-13620H, 100 câu Nhật ~20 ký tự | First-inference latency1.13 s | Streaming time-to-first-playable chunk.[^genie] |

**Quy ước đề xuất (Synthesis):** lưu RTF = wall_seconds/audio_seconds, RTFx = audio_seconds/wall_seconds; ghi TTFA riêng và thời điểm bắt đầu timer. Faster Qwen gọi RTF theo chiều RTFx; VieNeu/audio.cpp gọi theo wall/audio. Không so con số cùng tên mà chưa đọc định nghĩa.[^faster-qwen][^vieneu][^audio-cpp][^fast-gpu-asr]

## Shortlist theo bài toán (Synthesis, chưa benchmark)

| Bài toán | Shortlist / đường triển khai | Điều kiện |
|---|---|---|
| Local đa tác vụ | audio.cpp | Check từng model/backend/package/streaming.[^audio-cpp] |
| Nhúng STT đa vendor | transcribe.cpp | Chọn GGUF đúng Handy runtime, kiểm tra bindings.[^transcribe-cpp] |
| NVIDIA native speech | NeMo-Speech.cpp | Model/license của ASR/TTS/VoiceChat vẫn xét riêng.[^nemo-cpp] |
| Whisper CPU/GPU | Faster-Whisper; thêm WLK hoặc RealtimeSTT nếu live input | Không lấy batch throughput làm realtime guarantee.[^faster-whisper][^wlk][^realtimestt] |
| Offline bulk Zipformer/Parakeet | Fast GPU ASR | NVIDIA Linux, target-GPU export và batch profile.[^fast-gpu-asr] |
| TTS GPU nhiều model/stages | SGLang-Omni hoặc vLLM-Omni | Chọn theo model recipe, rồi benchmark target concurrency; chưa có winner chung.[^sglang-omni][^vllm-omni] |
| Qwen3-TTS chuyên dụng | Faster Qwen3-TTS | CUDA-graphs/GGML đúng wheel; tiếng Việt không tự được thêm nhờ engine.[^faster-qwen][^tts-survey] |
| Voice agent tiếng Việt | HF s2s hoặc Pipecat + STT vi + VieNeu API | Đổi default nếu không có vi; xét giấy phép và schema; framework report chưa primary-verified.[^hf-s2s][^frameworks][^vieneu][^asr-survey][^tts-survey] |
| Apple on-device | MLX Audio qua HF pipeline; transcribe.cpp Metal; TheStage Core ML; FluidAudio diarization | TheStage có online-init; FluidAudio chỉ diarization; kiểm tra từng export, OS và language.[^hf-s2s][^transcribe-cpp][^thestage][^apple-diar] |

License runtime không cấp quyền weights, preset voices hay voice cloning. transcribe.cpp MIT, NeMo/vLLM-Omni/Fast GPU ASR Apache-2.0 được nguồn nêu; Speaches và identifier license SGLang-Omni chưa rõ trong capture; không tự điền từ trí nhớ. OmniVoice GGUF NC và mâu thuẫn phạm vi commercial VieNeu giữ nguyên (**Reported/Synthesis**).[^transcribe-cpp][^nemo-cpp][^vllm-omni][^fast-gpu-asr][^speaches][^sglang-omni][^omnivoice-cpp][^vieneu]

## Relationships

- Uses: [ASR/STT Model Survey](asr-stt-model-survey.md) và [TTS Model Survey](tts-model-survey.md) để nối lựa chọn runtime với language/weights; trang này so sánh công cụ, không thay survey model (**Synthesis**).[^asr-survey][^tts-survey]
- Contrasts with: [Voice Agent Frameworks](voice-agent-frameworks.md) chỉ tập trung orchestration, còn trang này tách các tầng runtime/server/streaming/orchestration và độ mạnh provenance (**Synthesis**).[^frameworks]

## Coverage và giới hạn

- Retrieval: đọc catalog và các concept runtime/server/pipeline/framework, traversal các package native, Apple SDK/diarization, VAD/turn detector, VieNeu và serving/edge sections của hai survey. Không dùng QMD vì catalog và exact search đã tìm các nhóm cần so sánh; không tuyên bố mọi tool ngoài wiki đã được tìm.
- Research raw thực hiện: `raw/sglang-omni.md` News/About/What Serves/Hardware/Quick Start; `raw/vllm-omni.md` Latest News/About/Getting Started; `raw/NeMo-Speech.cpp.md` Models/Performance; `raw/parakeet.md` API Reference/Streaming; `raw/faster-qwen3-tts.md` intro/Install. Đây là static reading các capture local, không live web research hoặc inspect implementation. Nguồn nguyên bản tương ứng đã có trên concept; phát hiện full-upload SSE được trích trực tiếp và fold lại Parakeet page.[^parakeet-readme]
- Không cài package, build runtime, tải weights, mở server, nghe audio, đo RAM/VRAM/latency hay tái lập benchmark. Các capability/compatibility/benchmark ở đây giữ **Reported**; lựa chọn là **Synthesis**; không có verification event để đặt `verified`.
- `draft` vì so sánh framework còn dựa AI report, chưa có primary docs/API detail/concurrency benchmark đồng điều kiện cho mọi runtime. Recipe/code/test/weights và benchmark figures chưa có ở những concept được dẫn vẫn chưa inspect; ledger giới hạn kế thừa theo từng concept, không quảng bá thành hỗ trợ đã chạy được.
- Nhạc/video thuần và model catalog ngoài vòng speech bị loại khỏi shortlist; count100+ của audio.cpp chỉ là framework-wide, không coverage speech riêng. Không chép credential/contact; input audio và cloning references nếu triển khai cần boundary riêng.

[^audio-cpp]: [audio.cpp Framework](audio-cpp-framework.md) — Framework identity; Runtime, backends, and builds; Interfaces; Performance; Coverage; Notes về GGUF.
[^transcribe-cpp]: [transcribe.cpp](transcribe-cpp.md) — Supported models; Build; Bindings; License; Contradictions; Coverage.
[^nemo-cpp]: [NeMo-Speech.cpp](nemo-speech-cpp.md) — Models; Performance Q8 tables; Server, SDK, and source build; Coverage.
[^sglang-omni]: [SGLang-Omni](sglang-omni.md) — Served model coverage; Architecture; Hardware; Coverage/license identifier limit.
[^vllm-omni]: [vLLM-Omni](vllm-omni.md) — Release line; Architecture; Hardware; Community, license; Coverage.
[^faster-whisper]: [Faster-Whisper](faster-whisper.md) — Usage/generator; Benchmarks; Model conversion; Community integrations; Fair-comparison guidance.
[^fast-gpu-asr]: [Fast GPU ASR](fast-gpu-asr.md) — Scope; Requirements; Export workflow; Benchmarks; Implementation decoder differences; License.
[^faster-qwen]: [Faster Qwen3-TTS](faster-qwen3-tts.md) — Backends; Interfaces; Streaming design; Performance0.6B/1.7B; Parity; Coverage.
[^genie]: [Genie-TTS](genie-tts.md) — Model compatibility; Performance claims; Usage/model conversion; Roadmap; Coverage.
[^speaches]: [Speaches](speaches.md) — Engines; Features; Coverage and limits (version, license, schema unavailable).
[^parakeet-server]: [Parakeet ASR Server](parakeet-asr-server.md) — Identity; Footprint; Requirements; Long-audio; API reference; Coverage.
[^parakeet-readme]: [Parakeet README](../raw/parakeet.md) — API Reference > Transcribe parameter table (model/prompt/temperature ignored); Streaming, lines469–473 (audio uploaded in full, incremental SSE decoding).
[^wlk]: [WhisperLiveKit](whisperlivekit.md) — Streaming policies; Backend selector; Backend notes; Serving APIs; Diarization; Coverage.
[^realtimestt]: [RealtimeSTT](realtimestt.md) — Recommended engine profiles; Recorder; Capabilities; Production server/turn-state note; Coverage.
[^hf-s2s]: [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md) — Architecture; Supported components; Starting configurations; Realtime API; LLM proxy; TTS OmniVoice; Coverage.
[^voicechat]: [RealtimeVoiceChat](realtime-voice-chat.md) — Identity and maintenance; Pipeline architecture; Deployment; Coverage.
[^frameworks]: [Voice Agent Frameworks](voice-agent-frameworks.md) — Comparison(mid-2026); Pipecat composition; Coverage (AI report, no primary docs).
[^funasr-cpp]: [Fun-ASR-Nano GGUF](fun-asr-nano-gguf.md) — Architecture/runtime; Files; Usage; Coverage.
[^moss-cpp]: [MOSS-Transcribe-Diarize GGUF](moss-transcribe-cpp-gguf.md) — Package identity; Variants/JFK protocol; Usage; LocalAI serving pointer; Coverage.
[^omnivoice-cpp]: [OmniVoice GGUF](omnivoice-gguf.md) — Files; Backends; Quantization; Licensing; distinct audio.cpp distribution relationship.
[^apple-diar]: [Speaker Diarization Core ML](speaker-diarization-coreml.md) — Supported artifacts; Provenance; Legacy; Technical specifications; Coverage.
[^thestage]: [TheWhisper-Large-V3-Turbo](thewhisper-large-v3-turbo.md) — Access Token Setup; System requirements; Apple SDK; NVIDIA paths; Serving; Coverage.
[^whistle]: [Whistle](whistle.md) — Capabilities; Needle engine; Python; Deploy; Benchmarks/image-only limit.
[^vieneu]: [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md) — Runtime/SDK; Serving API; Benchmarks/streaming versus offline; Contradictions; Coverage.
[^silero]: [Silero VAD](silero-vad.md) — Requirements; Deployment/ecosystem; Coverage.
[^turns]: [Turn Detection Models](turn-detection-models.md) — Comparison; Operating practice; Coverage (secondary report).
[^asr-survey]: [ASR/STT Model Survey](asr-stt-model-survey.md) — Edge deployment; Serving runtimes (TheStage Triton ensemble, Photon); Vietnamese selection; Coverage/missing primary runtime concepts.
[^tts-survey]: [TTS Model Survey](tts-model-survey.md) — Edge deployment; Serving runtimes; Vietnamese selection; Licensing; Coverage.
[^cosyvoice]: [CosyVoice2-0.5B](cosyvoice2-0.5b.md) — Model identity/Roadmap vLLM and Triton TRT-LLM; Capabilities; Coverage.
