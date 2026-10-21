---
type: Synthesis
title: OmniVoice Deployment Comparison
description: Comparison of five compiled OmniVoice deployment routes, three checkpoint choices, quantization, streaming limits, and unresolved license lineage.
tags: [tts, deployment, comparison, omnivoice]
status: draft
created: 2026-10-15
generated: { by: llm-wiki-agent/1, at: 2026-10-21T18:00:00Z }
stale_after: 2027-04-15
sources:
  - { id: base, resource: omnivoice.md, kind: synthesis, title: OmniVoice }
  - { id: gguf, resource: omnivoice-gguf.md, kind: synthesis, title: OmniVoice GGUF }
  - { id: audio, resource: audio-cpp-framework.md, kind: synthesis, title: audio.cpp Framework }
  - { id: catalog, resource: audio-cpp-gguf-packages.md, kind: synthesis, title: audio.cpp GGUF Model Packages }
  - { id: crisp, resource: crispasr-tts-engines.md, kind: synthesis, title: CrispASR TTS Engines }
  - { id: server, resource: crispasr-streaming-http-server.md, kind: synthesis, title: CrispASR Streaming and HTTP Server }
  - { id: pipeline, resource: speech-to-speech-pipeline.md, kind: synthesis, title: HF Speech-to-Speech Pipeline }
  - { id: args, resource: speech-to-speech-cli-and-defaults.md, kind: synthesis, title: Speech-to-Speech CLI and Defaults }
  - { id: g, resource: g-omnivoice.md, kind: synthesis, title: G-OmniVoice }
  - { id: khanh, resource: khanhtts-omnivoice.md, kind: synthesis, title: KhanhTTS-OmniVoice }
  - { id: vi, resource: omnivoice-vietnamese.md, kind: synthesis, title: OmniVoice Vietnamese (splendor1811) }
---

Five compiled deployment/integration routes cover direct Python inference, two distinct native runtimes, CrispASR, and a complete voice-agent pipeline. Recommendations below are **Synthesis**, capabilities and performance remain **Reported** rather than independently reproduced. This is a catalog-bounded comparison, not an exhaustive current-web survey.[^base][^gguf][^audio][^crisp][^pipeline]

## Deployment routes

| Route | Interfaces and hardware evidence | Recommended role / limits (Synthesis) |
| --- | --- | --- |
| Python `omnivoice` | `from_pretrained` plus `generate`; CUDA example and Apple Silicon installation | Baseline for original and finetuned checkpoints; complete-waveform example, not a supplied production API service.[^base] |
| `omnivoice.cpp` | C++17/GGML; CPU/CUDA/Vulkan/Metal, ROCm also claimed; separate base and tokenizer GGUFs; example design/cloning scripts | Focused native OmniVoice deployment; no compiled HTTP-server, concurrency, or matched performance evidence.[^gguf] |
| `audio.cpp` | CLI, HTTP speech endpoint, embedded WebUI, Docker; CPU/CUDA/HIP/Vulkan/Metal with CUDA optimized | Broad native audio service and UI; OmniVoice package lists BF16/F16/Q8. Generic runtime interface coverage does not establish every OmniVoice-specific option or streaming path.[^audio][^catalog] |
| CrispASR | `omnivoice` cloning engine; CLI and speech HTTP endpoint; Docker/prebuilt CUDA server options | Existing unified speech-service users; watermarking and cloning-rights flag reported. Default single-model inference serialized; batched multi-stream inference unsupported. No OmniVoice-specific performance evidence.[^crisp][^server] |
| HF Speech-to-Speech | `--tts omnivoice`; CUDA/MPS/XPU/NPU support; device argument also includes CPU; Realtime WebSocket/WebRTC voice pipeline | End-to-end VAD→STT→LLM→TTS integration rather than a different inference engine. Handler waits for full generated utterance before yielding 16 kHz blocks from 24 kHz output.[^pipeline][^args] |

## Checkpoint choice

- Base `k2-fsa/OmniVoice`: 600+ languages, cloning and voice design; pretrained weights CC-BY-NC, code Apache-2.0.[^base]
- `g-group-ai-lab/g-omnivoice`: Vietnamese-focused cloning/design; its own held-out table reports Vietnamese WER 2.59%, versus base 7.12% and KhanhTTS 3.75%. Protocol and checkpoint revisions are missing; not a latency ranking.[^g]
- `kjanh/KhanhTTS-OmniVoice`: Vietnamese-English finetune, reported ~1,500 training hours; direct Python example. Own card gives no quality/latency benchmark.[^khanh]
- `splendor1811/omnivoice-vietnamese`: Vietnamese finetune on the 1,000 h Dolly-Audio corpus; its card gives the only compiled Python serving recipe (cached voice prompt, `torch.compile`, `num_step=8`) with self-reported L4 RTF ~0.07, ~210 ms short-sentence TTFB, and ~1.26 s P95 TTFB at four concurrent users, but no quality metric, no TTFB definition, and a dataset-versus-model license conflict (see [OmniVoice Vietnamese](omnivoice-vietnamese.md)); the figures are not comparable with the RTX 5090 audio.cpp numbers (**Synthesis**).[^vi]
- Both derivatives use the Python library in their cards; native GGUF compatibility or conversion availability for those finetunes is not established. Their Apache labels do not resolve inherited base-weight restrictions (**Synthesis**).[^g][^khanh][^gguf]

## Quantization and speed

For `omnivoice.cpp`, Q8_0 is the card recommendation: 656 MB base + 289 MB tokenizer, approximately 945 MB combined files. Q4_K_M is 407 + 252 MB, approximately 659 MB; BF16 is 1.23 GB + 373 MB, approximately 1.60 GB; F32 is 2.46 GB + 734 MB, approximately 3.19 GB. These are file-size sums, not peak RAM/VRAM. Tokenizer quants retain selected tensors at F32/F16.[^gguf]

The audio.cpp author reports RTX 5090 generation of 357 s audio in 11.38 s BF16, 10.25 s Q8, or 8.28 s Q8 with performance mode (31.37x/34.82x/43.10x realtime). Base card RTF 0.025 (~40x) has no matched comparison here; neither number establishes TTFA or a runtime winner.[^audio][^base]

The audio.cpp author also reports OmniVoice streaming, with 213–280 ms TTFT for 50-character chunks depending on chunk size, no stated hardware, and a note that the memory-saver mode cannot yet be combined with the performance mode. It is a chunked-text TTFT, not a frame-level first-audio latency, so it does not rank audio.cpp against the other routes (**Synthesis**).[^audio]

## Relationships and deployment cautions

- Uses [OmniVoice](omnivoice.md), [OmniVoice GGUF](omnivoice-gguf.md), [audio.cpp](audio-cpp-framework.md), [CrispASR TTS](crispasr-tts-engines.md), and [HF Speech-to-Speech](speech-to-speech-pipeline.md) as the deployment candidates above.[^base][^gguf][^audio][^crisp][^pipeline]
- GGUF is not a universal adapter: the audio.cpp package is distinct from the Serveurperso omnivoice.cpp pair; compatibility with each other or generic llama.cpp is not established.[^gguf][^audio]
- Do not equate block delivery or sentence splitting with native incremental generation. Measure warm/cold TTFA, cancellation, memory and concurrent load on the actual target (**Synthesis**).[^pipeline][^server]
- License conflict remains unresolved: CrispASR lists OmniVoice as Apache, but upstream distinguishes Apache code from CC-BY-NC weights; G-OmniVoice and the GGUF card also give different tokenizer-license descriptions. No commercial clearance is established.[^crisp][^base][^g][^gguf]

## Coverage and limits

Populated wiki at retrieval; structural check initially reported 217 concepts. Catalog plus case-insensitive OmniVoice search and related deployment concepts inspected; no raw research, upstream fetching, installation, model execution, or benchmarks. Source concepts retain uninspected code, checkpoint, guide and license limits. Status draft because matched performance, native derivative compatibility and license lineage remain unresolved. Linked base-card Space/Colab demos are demonstrations, not established production hosting options.[^base][^gguf][^audio][^g][^khanh]

[^base]: [OmniVoice](omnivoice.md) — Requirements and installation; Inference usage; Performance; Model identity and release; Coverage and limits.
[^gguf]: [OmniVoice GGUF](omnivoice-gguf.md) — Files and variants; Usage; Backends; Quantization policy; Licensing; Relationships; Coverage and limits.
[^audio]: [audio.cpp Framework](audio-cpp-framework.md) — Runtime, backends, and builds; Distribution and model management; Interfaces; Performance and quantization; Complementary author-thread snapshot (07/21 OmniVoice Q8 figures); Release 0.3 launch thread (OmniVoice streaming TTFT and memory notes); Coverage and limits.
[^catalog]: [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) — OmniVoice-GGUF table row.
[^crisp]: [CrispASR TTS Engines](crispasr-tts-engines.md) — Invocation; Engine matrix; Licensing and gating; Trust controls; Coverage and limits.
[^server]: [CrispASR Streaming and HTTP Server](crispasr-streaming-http-server.md) — HTTP server; Concurrency; Coverage and limits.
[^pipeline]: [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md) — Supported components; TTS notes: OmniVoice, Pocket, and logging; Coverage and limits.
[^args]: [Speech-to-Speech CLI and Defaults](speech-to-speech-cli-and-defaults.md) — OmniVoice TTS arguments; Coverage and limits.
[^g]: [G-OmniVoice](g-omnivoice.md) — Benchmark; Requirements and inference usage; Licensing; Coverage and limits.
[^vi]: [OmniVoice Vietnamese (splendor1811)](omnivoice-vietnamese.md) — Usage; Performance; Licensing and data constraints; Coverage and limits.
[^khanh]: [KhanhTTS-OmniVoice](khanhtts-omnivoice.md) — Inference surface; Quality evidence; Licensing and responsible use; Coverage and limits.
