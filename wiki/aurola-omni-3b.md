---
type: Concept
title: AuroLA-Omni-3B
description: A 4.70B-parameter BF16 Qwen2.5-Omni Thinker-based omni-modal embedding checkpoint for text, image, audio, and video retrieval, with a self-reported 46.7 average on MMEB-V3.
tags: [embedding, retrieval, multimodal, omni-modal, audio, qwen]
status: draft
created: 2026-10-22
generated: { by: llm-wiki-agent/1, at: 2026-10-22T23:30:00Z }
stale_after: 2027-01-20
sources:
  - id: auro-la-omni-3b-page
    resource: ../raw/Jazzcharles-AuroLA-Omni-3B.md
    kind: model-card
    title: Jazzcharles/AuroLA-Omni-3B Hugging Face page capture (HTML)
---

# AuroLA-Omni-3B

AuroLA-Omni-3B (Hub repo `Jazzcharles/AuroLA-Omni-3B`) is a BF16 omni-modal embedding model that its card says is "built from both Qwen2.5-Omni-3B and AuroLA-3B"; it accepts text, image, audio, and video through a Sentence Transformers-compatible layout. The page tags the audio-text retrieval paper arXiv:2602.18010, "Scaling Audio-Text Retrieval with Multimodal Large Language Models" (Xu, Thomé, Horak, Xie, Zisserman). Neither that paper nor an AuroLA-3B card was supplied, so the training method, data, losses, and the relationship between the two checkpoints are undocumented here. Every score is **Reported** by the card. [^auro-la-omni-3b-page]

## Model facts

| Field | Value |
|---|---|
| Backbone | Qwen2.5-Omni-3B (Hub tag: finetune); architecture class `Qwen2_5OmniThinkerForConditionalGeneration` (Thinker only, no speech output) |
| Parameters | 4,702,358,528, all BF16; sharded safetensors, 9,404,995,092 bytes (Hub metadata) |
| Pooling / output | Final-layer hidden state at the last non-padding token (left padding), L2-normalized; cosine similarity |
| Output width | Not stated (see below) |
| Modalities | text, image, audio, video |
| Library / pipeline | `sentence-transformers`, `feature-extraction`; not gated |
| License | Not stated on the page (no license tag or section) |
| Repo dates | Created 2026-08-23; last modified 2026-08-23 |
| Popularity at capture | 83 downloads last month, 204 all time, 3 likes |

- The 4.702B count is about 1.1M below the 4.703B of [e5-omni](e5-omni.md) 3B and [Omni-Embed-Nemotron-3B](omni-embed-nemotron-3b.md), consistent with the same Qwen2.5-Omni-3B Thinker plus small differences (Synthesis). By the same inference the width would be 2,048, as for Omni-Embed-Nemotron and [Ovis-Omni-Embedding-3B](ovis-omni-embedding-3b.md), but the page never states it (Unverified). [^auro-la-omni-3b-page]
- The "3B" name understates size by roughly 1.57× because it refers to the base model, not the Thinker's total count (Synthesis). [^auro-la-omni-3b-page]

## Retrieval interface

- **Sentence Transformers:** `pip install "sentence_transformers[image,audio,video]" "transformers>=5.6.0" qwen-omni-utils`; load with `torch_dtype=bfloat16` and `attn_implementation="sdpa"` (`flash_attention_2` if installed). Queries use `encode_query`, candidates use `encode_document`, and `model.similarity` scores them. The example caps video at `max_pixels = 64*28*28` with frame sampling at 1 fps. [^auro-la-omni-3b-page]
- **Raw Transformers:** load `Qwen2_5OmniThinkerForConditionalGeneration` with `AutoProcessor`, and apply the `sentence_transformers` chat template explicitly (`add_generation_prompt=True`), then append `<|endoftext|>`. Use left padding, `use_audio_in_video=False`, video `max_pixels = 128*28*28` at 1 fps, take the last non-padding token's final hidden state, and L2-normalize. [^auro-la-omni-3b-page]
- **Prompt template:** the `sentence_transformers` chat template in the page's tokenizer metadata emits a fixed system prompt, then the input, then a modality-specific suffix: "Summarize above sentence / image / audio / video in one word:". Text queries carry no instruction prefix in the examples, unlike the "Query: " prefix in the [e5-omni](e5-omni.md) Transformers example. The template is an observed property of the capture; its role in training is not documented. [^auro-la-omni-3b-page]
- Examples show only single query-to-candidate similarity calls with placeholder paths and no output values, so they are not evidence of quality. [^auro-la-omni-3b-page]

## Reported evaluation (MMEB-V3)

The card's table (benchmark version, task count, date, and baselines are not given): [^auro-la-omni-3b-page]

| Group | Metric | Score |
|---|---|---:|
| Image | hit@1 | 65.1 |
| Video | hit@1 | 48.9 |
| VisDoc | ndcg_linear@5 | 69.2 |
| Text | hit@1 | 32.4 |
| Audio | hit@1 | 46.8 |
| Agentic | hit@1 | 36.5 |
| Average | – | 46.7 |

- The unweighted mean of the six group scores is 49.8, not 46.7, so the "Average" is not a simple macro mean of the groups; it may weight by task or subset, but the card does not say (Synthesis). [^auro-la-omni-3b-page]
- The values are not on a stated scale shared with other pages. [Ovis-Omni-Embedding-3B](ovis-omni-embedding-3b.md) reports 58.46 on 190 datasets, [Sentio](sentio.md) 61.69 on its own 190-task snapshot, and the local [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md) lists [e5-omni](e5-omni.md) 3B at Overall 44.03 with Text 24.38, Audio 30.76, and Agent 36.85. AuroLA-Omni-3B appears in neither the snapshot nor a ranking, so do not place 46.7 beside them without confirming a common protocol. Its Text (32.4), Audio (46.8), and Agentic (36.5) values are, as numbers only, above, above, and slightly below (36.5 vs 36.85) the snapshot's e5-omni-3B values (Synthesis; protocol equivalence Unverified).

## Limits

- The capture is a model page only. No paper, technical report, training data, loss, or hyperparameters were supplied; the AuroLA-3B parent is not described.
- No license, output dimensionality, context length, language coverage, Matryoshka support, or quantizations are stated.
- No independent reproduction of the benchmark values. Page metadata, download counts, and likes are time-sensitive; the capture date is not recorded in the file.
- Excluded as non-informative: site chrome, scripts, fonts, social-card metadata, and the generic `SentenceTransformer` snippet in the "Use this model" panel.

## Relationships

- **Fine-tunes:** Qwen2.5-Omni-3B, the same base as [e5-omni](e5-omni.md) 3B, [Omni-Embed-Nemotron-3B](omni-embed-nemotron-3b.md), and [Ovis-Omni-Embedding-3B](ovis-omni-embedding-3b.md). [^auro-la-omni-3b-page]
- **Compared in:** [Multimodal embedding model comparison](multimodal-embedding-model-comparison.md).
- **Benchmark family:** [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md) (not listed there).

[^auro-la-omni-3b-page]: [Jazzcharles/AuroLA-Omni-3B Hugging Face page capture](../raw/Jazzcharles-AuroLA-Omni-3B.md), HTML (378 lines) inspected statically: model-card sections "AuroLA-Omni-3B", "MMEB-V3 Results", "Usage" (SentenceTransformers, Transformers), "Citation"; embedded page metadata JSON (`safetensors`, `createdAt`, `lastModified`, `downloads`, `likes`, `tags`, `tokenizer_config.chat_template_jinja`, `additional_chat_templates.sentence_transformers`). Author-reported and not independently reproduced; no code was executed.
