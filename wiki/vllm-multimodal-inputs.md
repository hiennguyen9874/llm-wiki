---
type: Concept
title: vLLM Multimodal Inputs
description: Passing image, video, audio, embedding, and cached UUID inputs to multimodal models offline and via OpenAI-compatible serving.
tags: [vllm, multimodal, inference]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: multimodal-inputs
    resource: ../raw/vllm/features/multimodal_inputs.md
    title: Multimodal Inputs
---

vLLM passes multimodal data as `prompt` plus `multi_modal_data` offline or as OpenAI-style `image_url` / `video_url` / `input_audio` / `image_embeds` chat content online, with per-modality counts gated by `limit_mm_per_prompt`, media loading tuned by `media_io_kwargs`, processor/cache reuse keyed by content hash or user `uuid`, and media-fetch security scoped by allowed domains and redirect policy[^multimodal-inputs].

## Offline schema

- Offline requests use `{"prompt": ..., "multi_modal_data": {...}}` following the `vllm.inputs.PromptType` and `vllm.inputs.MultiModalDataDict` schemas, with `prompt` in the HuggingFace-documented placeholder format[^multimodal-inputs].
- Cap accepted items per prompt with `limit_mm_per_prompt`, for example `LLM(..., limit_mm_per_prompt={"image": 2})` or `{"video": 1}`[^multimodal-inputs].
- `LLM.chat` also accepts inline message content entries such as `image_url`, `image_pil`, `image_embeds`, and text parts[^multimodal-inputs].

## Image inputs

- Single image: `{"image": PIL.Image}`; multiple images in one prompt: `{"image": [image1, image2]}`[^multimodal-inputs].
- Multi-image input can be repurposed for video captioning by sending video frames as an image list, for example base64 `image_url` parts to Qwen2-VL with `limit_mm_per_prompt={"image": 4}`[^multimodal-inputs].
- RGBA images with transparency are converted to RGB; transparent pixels default to white `(255, 255, 255)` and can be changed with `media_io_kwargs={"image": {"rgba_background_color": [R, G, B]}}` offline or `--media-io-kwargs '{"image": {"rgba_background_color": [...]}}'` for serving[^multimodal-inputs].
- Moondream3 (`Moondream3ForCausalLM`) uses task-specific prompt recipes: `query` asks a question about the image and `caption`/`describe` generates a caption with a length argument; native `detect` and `point` skills requiring custom coordinate decoding are not exposed[^multimodal-inputs].

## Video inputs

- Offline `video` field accepts a list of NumPy arrays or `torch.Tensor` instances[^multimodal-inputs].
- For Qwen2.5-VL-like models the source builds the prompt with `AutoProcessor.apply_chat_template` and vision inputs with `process_vision_info`; that helper is noted as applicable only to Qwen2.5-VL and similar models[^multimodal-inputs].
- Video token pruning reduces prefill time and KV-cache use at some accuracy cost via `--video-pruning-rate <q>` and `--video-pruning-method evs|vidcom2`: `evs` drops tokens with lowest temporal dissimilarity and always retains the first frame, while `vidcom2` scores tokens against video/frame centers with per-frame budget sharing and retains at least one token per frame[^multimodal-inputs].
- `evs` is supported by all models implementing multimodal pruning; `vidcom2` is currently Qwen3-VL only, unsupported combinations are rejected at startup, and enabling pruning disables encoder CUDA graphs because retained token counts become data-dependent[^multimodal-inputs].

### Video decoding backends

- Selectable backends: `opencv` default on CPU, `torchcodec` on CPU, `pynvvideocodec` on GPU, and `deepstream` on GPU[^multimodal-inputs].
- CPU backends are FFmpeg-backed; `torchcodec` allows choosing the FFmpeg version while `opencv` uses its linked FFmpeg build[^multimodal-inputs].
- Select with `--media-io-kwargs '{"video": {"backend": "torchcodec"}}'` or `VLLM_VIDEO_LOADER_BACKEND`[^multimodal-inputs].
- `torchcodec` options: `num_ffmpeg_threads` with `0` meaning FFmpeg default `min(cpu_count + 1, 16)`, and `seek_mode: exact` default frame-accurate scan versus `approximate` faster metadata-based seeking[^multimodal-inputs].
- `pynvvideocodec` option: `hw_decoders` positive integer default `2`, reserved at startup and not overridable per request[^multimodal-inputs].
- `pynvvideocodec` uses NVIDIA NVDEC in the API-server process, requires CUDA Multi-Process Service because decoding and serving run in different CUDA processes, and requires `--mm-ipc-gpu-memory-gb > 0` carved from KV-cache budget to bound frontend decode allocations; exhausted budget waits rather than consuming engine headroom[^multimodal-inputs].
- `deepstream` is the recommended GPU backend for streaming sources, installable on Linux x86-64 with `pip install vllm[deepstream]` plus system GStreamer/PyGObject/CUDA packages, with `pool_size` clamped to `[1, 16]` defaulting to `VLLM_MEDIA_LOADING_THREAD_COUNT` and process-wide singleton semantics where the first request wins[^multimodal-inputs].

### Frame recovery and client-extracted frames

- Optional `frame_recovery: true` in `media_io_kwargs` recovers a failed target frame from the next successfully grabbed frame before the next target, handling mid-video corruption and end truncation; supported with common formats such as MP4 on OpenCV backends[^multimodal-inputs].
- When frames are extracted client-side and sent as `video/jpeg` base64-concatenated frames, preserve temporal context with `media_io_kwargs.video`: `fps`, `frames_indices`, `total_num_frames`, `duration`, and `do_sample_frames`[^multimodal-inputs].

## Audio inputs

- Offline `audio` field takes `(array, sampling_rate)`[^multimodal-inputs].
- Long-audio transcription for 30-second-limited models such as Whisper uses `vllm.multimodal.audio.split_audio` to split mono 1D audio at quiet points: `max_clip_duration_s`, `overlap_duration_s` search window, and `min_energy_window_size` for RMS energy, preserving all samples without data loss[^multimodal-inputs].
- vLLM auto-converts multi-channel audio to mono for Whisper and Whisper-based models, Qwen2-Audio, Qwen2.5-Omni / Qwen3-Omni, and Ultravox, handling both torchaudio `(channels, time)` and soundfile `(time, channels)` layouts via feature-extractor detection and channel averaging[^multimodal-inputs].
- Selectable audio decoding backends via `--media-io-kwargs '{"audio": {"audio_backend": ...}}'`: `auto` default soundfile then torchcodec then PyAV, plus pinned `soundfile`, `pyav`, and `torchcodec`[^multimodal-inputs].
- `pyav` uses a per-frame Python generator that contends on the GIL under concurrency; `torchcodec` decodes per stream in one GIL-releasing call and is preferred for concurrent workloads; `auto` prefers soundfile for supported formats to preserve decoding behavior including encoder padding, while video-container audio can fall through to torchcodec[^multimodal-inputs].
- `torchcodec` ships as a requirement on CUDA/CPU/XPU builds and must be installed manually elsewhere; it also needs system FFmpeg, otherwise `auto` uses soundfile then PyAV[^multimodal-inputs].

## Embedding inputs

- Pass precomputed `(..., LM hidden_size)` tensors directly per modality with `enable_mm_embeds=True` offline or `--enable-mm-embeds` for serving; wrong shapes may crash the engine, so enable only for trusted users[^multimodal-inputs].
- Model-specific extra fields are required for some models: Qwen2-VL needs `image_grid_thw` for positional encoding, MiniCPM-V-2_6 needs per-image `image_embeds` list plus `image_sizes`, and Qwen3-VL image embeds should include base embedding plus deepstack features[^multimodal-inputs].
- Unlike offline batched embedding dicts, online embeddings must be passed separately per item so placeholder tokens are applied correctly by the chat template, as base64 tensors via `tensor2base64` in `image_embeds` content parts[^multimodal-inputs].

## Cached inputs and UUIDs

- By default vLLM hashes each media item by content for cross-request caching; offline callers can instead pass `multi_modal_uuids` with stable IDs to avoid rehashing[^multimodal-inputs].
- `multi_modal_uuids` must include every modality present in `multi_modal_data`, match list lengths, and may use `None` per item to fall back to content hashing[^multimodal-inputs].
- With a UUID expected to hit cache, media data may be omitted entirely such as `{"image": [None, img_b]}`; the request fails if skipped media lacks a UUID or misses cache[^multimodal-inputs].
- User-provided UUIDs are ignored when both multimodal-processor caching and prefix caching are disabled[^multimodal-inputs].
- Online, media parts accept an optional `uuid` and cache-hit-only requests send null/empty media such as `"image_url": None`, `"image_embeds": None`, `"input_audio": None`, or `"video_url": {}` with the UUID[^multimodal-inputs].

## Online serving

- The OpenAI-compatible server accepts multimodal data through the Chat Completions API and requires a chat template: HF default from `chat_template.json`/`tokenizer_config.json`, then built-in fallback in `vllm/transformers_utils/chat_templates/registry.py`, then `--chat-template` or an error; some models use alternative templates under `examples/`, for example VLM2Vec with Phi-3-Vision[^multimodal-inputs].
- Image content follows the OpenAI Vision API as `image_url` parts; no `<image>` placeholder is needed in text because the server inserts it, and text/image parts may be interleaved to place images mid-text[^multimodal-inputs].
- Video uses `video_url`; audio uses OpenAI `input_audio` with base64 `data` plus `format`, or vLLM's `audio_url` counterpart to `image_url`[^multimodal-inputs].
- Local file access uses `file://` URLs and requires launching the server/engine with `--allowed-local-media-path`[^multimodal-inputs].
- Fetch timeouts default to 5s images via `VLLM_IMAGE_FETCH_TIMEOUT`, 30s videos via `VLLM_VIDEO_FETCH_TIMEOUT`, and 10s audio via `VLLM_AUDIO_FETCH_TIMEOUT`[^multimodal-inputs].

## Security and media access

- When serving multimodal models, restrict fetchable domains with `--allowed-media-domains`, for example `upload.wikimedia.org github.com www.bogotobogo.com`, to reduce Server-Side Request Forgery risk, especially for containerized vLLM pods with broad internal-network access[^multimodal-inputs].
- Set `VLLM_MEDIA_URL_ALLOW_REDIRECTS=0` to prevent HTTP redirects from bypassing domain restrictions[^multimodal-inputs].

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — offline `LLM.generate`/`LLM.chat` versus `vllm serve` Chat Completions paths for the same modalities.
- Uses [vLLM Multimodal Data Processing](vllm-multimodal-processing.md) — user-supplied images, video, audio, and embeddings feed the placeholder-to-input correspondence and processor-output caching path.
- Uses [vLLM Prefix Caching](vllm-prefix-caching.md) — content-hash and UUID media caching complements prefix reuse; UUIDs are ignored when processor and prefix caching are both off.
- Uses [vLLM Encoder CUDA Graphs for Vision Transformers](vllm-encoder-cuda-graphs.md) — video token pruning disables encoder CUDA graphs because retention is data-dependent.

## Coverage limits

- Referenced `../models/supported_models.md`, `../models/generative_models.md`, `vllm/transformers_utils/chat_templates/registry.py`, `examples/` offline/online clients and pooling templates, and `vllm.inputs` / `vllm.multimodal` / `vllm.assets` / `vllm.utils.serial_utils` code symbols were absent from `raw/` or are code paths and were not inspected[^multimodal-inputs].
- External RFC 4194, GitHub issue links, OpenAI Vision/Audio/Chat API docs, model repos such as Phi-3.5-Vision, Qwen2-VL, Qwen2.5-VL, Qwen3-VL, LLaVA-OneVision, Ultravox, MiniCPM-V, Moondream3, Whisper, public asset URLs, and install/system packages for DeepStream, torchcodec, FFmpeg, NVDEC, MPS, GStreamer, and CUDA were not inspected[^multimodal-inputs].

[^multimodal-inputs]: Multimodal Inputs — `../raw/vllm/features/multimodal_inputs.md`, covering offline `prompt`/`multi_modal_data` and `LLM.chat` content, `limit_mm_per_prompt`, image/video/audio/embedding/UUID inputs, Moondream3 recipes, RGBA background, video pruning/decoding/frame-recovery/client-frame metadata, audio split/normalization/decoding backends, online Chat Completions templates/media types/local paths/timeouts, and allowed-domains/redirect security.
