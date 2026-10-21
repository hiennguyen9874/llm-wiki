---
type: Concept
title: Fish Audio Drama 3
description: 35B-parameter (3B active) MoE multi-speaker TTS model from Fish Audio with up to 16 speaker tags, voice cloning, inline event tags, edit-as-continuation, and H200 streaming figures of 88.9 ms TTFA at concurrency 1 on SGLang-Omni and vLLM-Omni.
tags: [tts, multi-speaker, voice-cloning, streaming, serving, moe]
status: stable
created: 2026-10-21
generated: { by: llm-wiki-agent/1, at: 2026-10-21T16:00:00Z }
stale_after: 2027-04-21
sources:
  - id: fish-drama3-card
    resource: ../raw/drama-3.md
    kind: documentation
    title: Fish Audio Drama 3 model card
---

Fish Audio Drama 3 is Fish Audio's text-to-speech model for multi-character scenes and long-form content: a 35B-parameter MoE text backbone (3B active per token, hybrid full plus linear attention) with a 10-codebook causal "Codebook-MTP" audio decoder, FP8 MoE experts, up to 16 speakers per text, voice cloning, natural-language/inline control, and edit-by-continuation. The card reports streaming on one H200 with 88.9 ms median time-to-first-audio and RTF 0.131 at one stream, and launch-day serving through SGLang-Omni and vLLM-Omni, under a Fish Audio research-style license (**Reported**).[^fish-drama3-card]

## Model identity and architecture

- Card title is `Fish Audio Drama 3`; frontmatter declares `pipeline_tag: text-to-speech`, tags `fish-audio`, `text-to-speech`, `multi-speaker`, `audio-editing`, `emotional-speech-generation`, and an 83-entry `language` list (**Reported**).[^fish-drama3-card]
- Bullet list states: 35B parameters with 3B active per token (MoE text backbone, hybrid full plus linear attention); a Codebook-MTP audio decoder that decodes 10 codebooks causally over the whole sequence; FP8 MoE experts with remaining weights in bf16 (**Reported**).[^fish-drama3-card]
- Speaker tags `<|speaker:0|>` … `<|speaker:15|>` let one text carry up to 16 characters; long text is chunked automatically and can be streamed per chunk (**Reported**).[^fish-drama3-card]
- Compared with [Fish Audio S2 Pro](fish-audio-s2-pro.md) (4B slow AR + 400M fast AR dense Dual-AR, 10-codebook RVQ), the card describes a different backbone (MoE) and decoder (Codebook-MTP) and does not state a codec frame rate, training data scale, or lineage from S2 Pro (**Synthesis**).[^fish-drama3-card]
- No technical detail beyond this list (codec, training data, RL alignment, quality benchmarks such as WER/SIM) is in the capture; those live in the linked technical report (`arxiv.org/abs/2610.18010`) which was not fetched (**Observed**).[^fish-drama3-card]

## Generation controls

- **Point tags:** event tags such as `[sighs]` and `[laughs]` are written into the text at the position where the event should occur, in a plain `/v1/tts` request with one reference (audio path plus transcript) and no history; the card gives an example sentence and sample audio but no tag list (**Reported**).[^fish-drama3-card]
- **Editing as continuation:** a request carries a `previous_takes` array of earlier text versions along with the modified text; the card says previous VQ tokens are sent "as normal language models do". Its example changes `Wednesday` to `Thursday`, then chains a second edit (`by noon` → `by five`) with both earlier takes in context (**Reported**). Whether the server caches VQ tokens or re-derives them from `previous_takes` text is not stated (**Unverified**).[^fish-drama3-card]
- **Voice cloning:** from one reference clip with transcript, supplied either as an audio path/URL plus text in `references` or as pre-encoded `vq_codes` with transcript (the benchmark setup) (**Reported**).[^fish-drama3-card]
- The capture refers to "the cloning example above", but no such section exists, so the card appears truncated or edited; the audio samples and reference clip (`en0`, 3.9 s) were not inspected (**Observed**).[^fish-drama3-card]

## Serving

| Runtime | Launch command (as printed) | Reference |
| --- | --- | --- |
| [SGLang-Omni](sglang-omni.md) | `sgl-omni serve --model-path fishaudio/drama-3 --port 8000` after `uv pip install --prerelease=allow -v -e ".[fishaudio]"` | Drama 3 Cookbook |
| [vLLM-Omni](vllm-omni.md) | `vllm serve fishaudio/drama-3 --omni --port 8091` after `uv pip install -e .` | Drama 3 vLLM-Omni Recipe |

Both are launched from a cloned repository checkout; the card claims support "from launch day" on SGLang-Omni and states vLLM-Omni support, without version pins (**Reported**).[^fish-drama3-card]

## Production streaming performance

Measured on NVIDIA H200 GPUs with streaming requests on Seed-TTS English prompts; each request clones a voice from one pre-encoded reference; `temperature` 1.0, `top_p` 0.9, `top_k` 30, `max_new_tokens` 500. Throughput is generated acoustic frames per second; TTFA is time to first audio; RTF is request-to-last-chunk time divided by returned audio duration. Each cell in Table 1 is the mean of four runs (**Reported**).[^fish-drama3-card]

| Concurrency | Throughput (frames/s) | TTFA p50 | TTFA p95 | RTF (mean) |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 166.7 | 88.9 ms | 90.8 ms | 0.131 |
| 2 | 287.0 | 96.2 ms | 130.1 ms | 0.152 |
| 4 | 467.6 | 108.2 ms | 156.4 ms | 0.186 |
| 8 | 678.1 | 153.2 ms | 210.9 ms | 0.256 |
| 16 | 927.6 | 210.1 ms | 287.2 ms | 0.373 |
| 32 | 1,244.7 | 304.6 ms | 396.1 ms | 0.551 |
| 64 | 1,687.3 | 450.9 ms | 1,020.1 ms | 0.801 |

**Vocoder placement (Table 2).** In SGLang-Omni, grouping of pipeline stages into processes and GPU placement is deployment configuration rather than per-model code. The card compares the vocoder on the engine's GPU against a second GPU at higher concurrency (default vocoder GPU share, 1,088 requests per level, mean of six server starts; throughput also counts the end-of-speech frame) (**Reported**).[^fish-drama3-card]

| Vocoder placement | Concurrency | Throughput (frames/s) | TTFA p50 | TTFA p95 |
| --- | ---: | ---: | ---: | ---: |
| Engine's GPU | 128 | 2,177 | 685 ms | 1,412 ms |
| Engine's GPU | 256 | 2,422 | 3,403 ms | 4,255 ms |
| Second GPU | 128 | 3,692 | 401 ms | 995 ms |
| Second GPU | 256 | 4,160 | 2,146 ms | 2,469 ms |

- Card interpretation: at 256 streams the colocated vocoder is fully loaded and new streams' first audio waits in its queue; a second GPU gives about 72% more throughput and 37% lower median TTFA at 256 streams, so use that layout for many concurrent streams plus short TTFA (**Reported**).[^fish-drama3-card]
- Arithmetic check: 4,160 / 2,422 ≈ 1.72× and 2,146 / 3,403 ≈ 0.63 (−37%), matching the prose; the card's "about 2.7× faster than playback at concurrency 16" equals 1 / 0.373 (**Observed**).[^fish-drama3-card]
- Table 1 TTFA/RTF rise monotonically with concurrency; at 64 streams p95 TTFA exceeds 1 s, and at 256 streams colocated p50 TTFA is 3.4 s, so the sub-100 ms claim holds only for a single stream (**Synthesis**).[^fish-drama3-card]
- Voice-loop relevance: TTFA is measured against pre-encoded reference codes, so reference-encoding time is excluded; figures are not comparable to S2 Pro's unprotocolled "~100 ms" or other cards' harnesses, and no consumer-GPU or Vietnamese figures exist (**Synthesis**).[^fish-drama3-card]

## License and access

- Frontmatter says `license: other`, `license_name: fish-audio-research-license`, `license_link: LICENSE.md`, while the body License section names the "Fish Audio Community License" linking the Hugging Face `LICENSE` file; the two names differ and the license text was not available, so terms (commercial use) are unresolved (**Observed**).[^fish-drama3-card]

## Relationships

- Sibling and predecessor in the same vendor line: [Fish Audio S2 Pro](fish-audio-s2-pro.md) covers the dense Dual-AR model with free-form `[tag]` control and unprotocolled H200 ~100 ms TTFA; Drama 3 adds multi-speaker tags, edit-by-continuation, and a concurrency-sweep protocol (**Synthesis**).[^fish-drama3-card]
- Served by [SGLang-Omni](sglang-omni.md) and [vLLM-Omni](vllm-omni.md); the vocoder-placement result shows stage placement as a deployment lever in the SGLang-Omni design (**Synthesis**).[^fish-drama3-card]
- Not yet a row in the [TTS Model Survey](tts-model-survey.md) catalog (which covers S2 Pro); consult this page for Drama 3 until the survey is extended (**Synthesis**).[^fish-drama3-card]

## Coverage and limits

- Entire single capture (YAML frontmatter, feature list, both serving sections, three examples, Tables 1 and 2, links, license) inspected statically; no weights downloaded, no server launched, no request sent, no audio listened to, and no latency, throughput, or quality claim reproduced (**Synthesis**).[^fish-drama3-card]
- Four embedded audio samples, the reference clip, the technical report, both cookbook/recipe pages, the Fish Speech repository, the playground, the license file, and the Hugging Face dataset reference WAV were linked but not fetched; model revision, checkpoint size on disk, VRAM requirement, supported-language quality, and tag vocabulary are absent from the capture (**Synthesis**).[^fish-drama3-card]
- No voice-loop (VAD/STT/LLM) integration, barge-in, or edge/GGUF packaging evidence; hardware reported is H200 only (**Synthesis**).[^fish-drama3-card]
- Performance and release claims carry `stale_after: 2027-04-21` per the `tts` domain rule (**Synthesis**).[^fish-drama3-card]

[^fish-drama3-card]: [Fish Audio Drama 3 model card](../raw/drama-3.md) — locators: frontmatter (`language` 83 entries, `license`, `license_name`, `license_link`, `pipeline_tag`, `tags`); H1 intro plus feature bullets (35B/3B active MoE, Codebook-MTP, FP8 experts, speaker tags 0–15, chunked long text); `Launch with SGLang Omni`; `Launch with vLLM-Omni`; `Example Usage` (reference clip `en0`, `Point tags`, `Editing as continuation` incl. chained K5 edit); `Production Serving` (protocol paragraph, Table 1, Table 2, interpretation paragraphs); `Links` (technical report arXiv 2610.18010, playground, cookbook/recipe); `License` section.
