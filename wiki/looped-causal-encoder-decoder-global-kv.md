---
type: Concept
title: Looped causal encoder-decoder and global KV refinement
description: Looped CED places recurrent computation around an encoder global KV source, trading extra prefill for improved long-context modeling in small controlled experiments.
tags: [looped-models, kv-cache, recurrent-transformers]
status: draft
created: 2026-11-22
generated: { by: llm-wiki-agent/1, at: 2026-11-22T10:18:48Z }
sources:
  - id: leng2026ced
    resource: ../raw/arXiv-2611.13378v1/main.tex
    scope: ../raw/arXiv-2611.13378v1/
    kind: paper
    revision: arXiv-2611.13378v1
    title: "Looping Deeper Without Growing the KV Cache: Recurrent Depth for Causal Encoder-Decoders"
---

# Looped causal encoder-decoder and global KV refinement

Looped CED places a tied recurrent block in a causal encoder–decoder (CED) encoder so that each pass recomputes a long-range key–value (KV) source; it combines cross-layer KV sharing with [last-round KV caching](last-round-kv-caching-for-looped-ced.md). **Reported:** in the authors' small dense-model experiments, this placement closely matched a looped full-KV transformer on validation bits per byte (BPB), but its prefill is more expensive than a decoder-only loop. These findings are not a general proof that global-KV refinement is necessary for all architectures.[^leng2026ced]

## Architecture and placement

In the 12-layer controlled model, layers 0–5 form the encoder and 6–11 the decoder. Each layer has a 128-token sliding window; layer 2 supplies global KV to later encoder layers, and layer 6 projects the encoder output into global KV shared by the decoder. The encoder loop repeats layers 2–5 eight times, while the decoder-loop ablation repeats layers 7–10. With a loop in the encoder, full prompt prefill must execute the recurrent core before boundary projection; a decoder loop can skip decoder work except for the local-window tail. Decode executes the whole model in either case.[^leng2026ced]

## Reported comparisons

- The controlled runs train dense 90M, 150M and 340M non-embedding-parameter models from scratch on FineWeb-Edu for 3.4B, 6.0B and 13.6B tokens, with 2,048-token context; a 150M run extends to 29.6B tokens. Comparisons match parameters and tokens, not training FLOPs. The dense comparator uses full-causal KV at every layer and no sliding window.[^leng2026ced]
- At matched model size, token budget, loop placement and eight rounds, encoder-loop CED is within 0.001 validation BPB of the dense loop while storing one-sixth of its global KV; it captures 89%, 86% and 93% of the respective dense-loop improvement at 90M, 150M and 340M. At 150M/6B tokens, validation BPB is 0.8468 for CED encoder loop, 0.8461 for dense loop and 0.8648 for CED decoder loop. This is global KV, not total serving memory or a measured speedup.[^leng2026ced]
- On PG19, FinePDFs and GovReport long documents, the authors report the encoder-loop versus dense-loop BPB gap remains approximately constant with context. A YOCO-U-style local-only encoder loop looks competitive in aggregate but loses 30% of the CED encoder-loop long-range gain in the 1,024–2,048-token bin. A repeated-text recall test similarly favors the encoder loop over decoder or local-only loops at smaller scales; results narrow at 340M. These are natural-text and constructed-copy tests within the tested context, not broad long-context reasoning benchmarks.[^leng2026ced]

## Limitations and coverage

Quality experiments are limited to dense models up to 340M; frontier MoE experiments measure serving costs with weights not trained to loop. No experiments were independently executed. The local package's main TeX, section/appendix text and generated numerical macros were inspected; bibliography and style files are supporting references or presentation, not independently validated. Figure captions and text were used, but ten PDF plots were not visually inspected, so figure-only detail remains pending. The numbers file points to unavailable `data/numbers.json` and collection scripts; underlying code and data were not supplied. License not established from the inspected entry point. No source code was executed.[^leng2026ced]

## Relationships

- Uses: [Last-round KV caching for looped CED](last-round-kv-caching-for-looped-ced.md) to avoid retaining a historical cache per round.
- Related: [Parcae stable looped transformers](parcae-stable-looped-transformers.md) also studies stable recurrent language-model training; the paper includes a middle-loop dense comparator.

[^leng2026ced]: Leng et al., *Looping Deeper Without Growing the KV Cache*, arXiv:2611.13378v1, `main.tex`, §§2–5 and limitations; `sections/appendix.tex` long-context and recall; `data/numbers.tex` keys `bpb/x40/1024/*`, `frac/x40/*`; `sections/09_ai_disclosure.tex`.
