---
type: Concept
title: RAG-Anything audio and video processing
description: Opt-in local transcription and scene-keyframe analysis produce timestamped text windows for LightRAG indexing.
tags: [ml, rag, audio, video, multimodal]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:07:43Z }
stale_after: 2027-01-24
sources:
  - id: rag-anything-3a14ecb
    resource: ../raw/RAG-Anything/README.md
    scope: ../raw/RAG-Anything/
    kind: code
    revision: 3a14ecb
    title: RAG-Anything repository
---

**Observed:** audio/video support is opt-in: audio becomes timestamped faster-whisper transcripts, while video combines mid-scene VLM descriptions with audio-track transcription. Both produce ordered textual sections for LightRAG rather than audio/video embeddings. **Synthesis:** retrieval fidelity is bounded by ASR accuracy and sparse visual sampling, not by access to the full original media at answer time.[^rag-anything-3a14ecb]

## Enablement and routing

**Observed:** install the relevant `audio`/`video` extras and set `enable_audio_processing` / `enable_video_processing` (environment `ENABLE_AUDIO_PROCESSING` / `ENABLE_VIDEO_PROCESSING`). Defaults are false. The video stack also needs ffmpeg on PATH. Missing dependencies warn and fall back to generic processing; enabling a flag alone does not prove media analysis is active.[^rag-anything-3a14ecb]

Direct media inputs bypass document parsers: `parse_document` creates a one-item content list with media path, empty caption, page index 0, and SHA-256 of media bytes. Content-list insertion also accepts `type="audio"` / `"video"`. The synthetic page 0 is not a real page-level media location.[^rag-anything-3a14ecb]

## Audio mechanism

**Observed:** `AudioModalProcessor` lazily loads faster-whisper. Model selection uses the explicit setting or `WHISPER_MODEL` (default `base`); device/compute defaults are `auto`, language is auto or `WHISPER_LANGUAGE`. Blocking transcription runs through `asyncio.to_thread`, with VAD enabled and 500 ms minimum silence.[^rag-anything-3a14ecb]

- Segments retain start/end/text; blank segments are discarded. Default minimum segment length is zero, retaining short factual utterances.
- `_group_segments_by_tokens` groups complete utterances under the LightRAG chunk budget (fallback 1200 tokens); an oversized utterance remains a single window rather than being split.
- Section names/order are deterministic (`audio_<file>_partK`); summaries use timestamps and transcript prefixes, not an additional LLM-written audio summary.
- **Observed limits:** no diarization, word-level timestamps, stored confidence scores, or native audio embedding retrieval in this implementation.[^rag-anything-3a14ecb]

## Video mechanism

1. **Observed:** SceneDetect `ContentDetector` defaults to threshold 27.0; scenes shorter than 5 seconds are filtered. If no retained scene exists, OpenCV can provide a whole-video fallback scene. Initialization reads `VIDEO_SCENE_THRESHOLD`, `VIDEO_MIN_SCENE_DURATION`, `VIDEO_MAX_SCENES`, and `VIDEO_MAX_WINDOWS` to override the scene/window defaults.
2. Extract one approximate mid-scene frame; describe it with the vision function. A per-video semaphore uses `max_parallel_insert` (fallback 2) for frame calls.
3. Extract the audio track to a unique temporary WAV and transcribe it once; temporary media is removed through cleanup/error paths.
4. Merge visual descriptions with overlapping speech into timestamped rows. Audio outside retained scenes is kept as audio-only rows, including leading/intermediate/trailing gaps.
5. Plan ordered windows using scene count and token budget; defaults are 50 scenes per window and at most 100 windows. If the window count exceeds the cap, redistribute scenes rather than dropping them.[^rag-anything-3a14ecb]

**Synthesis:** the window cap can relax earlier per-window bounds through redistribution; it is a chunk-count bound, not a guarantee that every final window fits a strict token budget. The planner counts visual description text, so final merged speech can further increase size.[^rag-anything-3a14ecb]

## Quality, cost, and security limits

- **Observed:** frame seeking is approximate; only a middle frame is described. **Synthesis:** fast events, transient on-screen text, or filtered short scenes can be missed even when audio gaps are preserved.
- **Observed:** visual descriptions are generated model prose and temporal speech alignment uses segment overlap, not forced audiovisual alignment. No execution established factual accuracy.
- **Synthesis:** vision calls scale with retained scenes; concurrent files, media items, and frame semaphores can multiply total model concurrency. Use [batch concurrency guidance](rag-anything-batch-processing.md), not a single semaphore value as a global rate limit.
- **Observed:** video frames are passed to the configured vision function; ASR runs locally with faster-whisper. **Synthesis:** local transcription does not make the entire video pipeline local if the vision adapter is remote.
- **Observed:** retrieved-image VLM answering scans `Image Path:` fields; audio/video chunks use `Source:`. The query path therefore consumes their descriptions/transcripts rather than automatically inspecting original media again.[^rag-anything-3a14ecb]

## Relationships

- **Uses:** [Multimodal grounding](rag-anything-multimodal-grounding.md) to store window chunks/entities.
- **Used by:** [Document ingestion](rag-anything-ingestion.md) and [batch processing](rag-anything-batch-processing.md).
- **Depends on:** [Runtime stack](rag-anything-stack-operations.md), especially optional packages and `av<19` compatibility.
- **Enables:** text-mediated [retrieval](rag-anything-query-retrieval.md), not native media replay.

## Evidence limits

No media models downloaded, audio transcribed, frames rendered, or tests run. The sampled tests establish intended cleanup/gap behavior only as inspected assertions; [source map](rag-anything-source-map.md) records coverage.

[^rag-anything-3a14ecb]: Revision `3a14ecb`: `raganything/modalprocessors_audio.py::AudioModalProcessor` (47), `transcribe` (146), `_group_segments_by_tokens` (206), section generation (266–375); `modalprocessors_video.py::VideoModalProcessor` (74), `_detect_scenes` (180), `_extract_frame_at` (228), `_extract_audio_track` (263), frame-description semaphore (345), `_transcribe_audio_track` (386), `_add_audio_only_segments` (401), `_merge_channels` (440), `_plan_windows` (480), `_redistribute` (523), section generation (603–720); `modalprocessors.py::_chunk_token_budget` (544); `processor.py` media routing (709–731) and audio/video chunk templates (1453–1478); `raganything.py::_initialize_processors` (222–304); `config.py` audio/video flags; `pyproject.toml` audio/video extras; README “Processing Requirements”; `tests/test_media_file_routing.py`, `tests/test_video_audio_cleanup.py`, sampled `tests/test_video_processor.py` (not executed).
