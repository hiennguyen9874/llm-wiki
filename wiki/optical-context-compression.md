---
type: Concept
title: Optical Context Compression
description: Optical context compression is the proposal to render text into images and retain compressed vision tokens, trading fidelity for a smaller long-context representation.
tags: [context-compression, long-context, vision-language-models, memory]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T10:41:06Z }
sources:
  - id: deepseek-ocr-paper
    resource: ../raw/2510.18234_DeepSeek-OCR/main.tex
    title: "DeepSeek-OCR: Contexts Optical Compression"
---

# Optical Context Compression

Optical context compression is a proposed long-context mechanism: render prior text as images, encode those images as a smaller sequence of vision tokens, and later use a vision-language decoder to reconstruct or use the information. It intentionally permits increasing loss for older material by lowering image resolution, unlike a lossless text codec.[^deepseek-ocr-paper]

## Proposed mechanism

The proposal treats OCR as an encode-decode testbed. A rendered document is encoded into $n$ vision tokens and decoded into $N$ text tokens, where $n \le N$; its stated compression ratio is ground-truth text-token count divided by vision-token count. In the source's envisioned dialogue application, older conversational turns would be rendered and progressively resized, causing smaller visual-token counts and increasingly blurred text while recent material remains higher fidelity.[^deepseek-ocr-paper]

[DeepSeek-OCR](deepseek-ocr.md) is the paper's prototype. Its reported Fox-subset results show high OCR precision near 7--10x compression and degradation at higher ratios, but are not evidence that an LLM can reliably preserve and retrieve arbitrary multi-turn context through this mechanism.[^deepseek-ocr-paper]

## Design implications

- **Retention policy becomes visual resolution allocation.** A system can reserve higher resolution (and more vision tokens) for recent or high-value context and use lower resolution for older context.
- **Fidelity is task- and layout-dependent.** Dense, complex, or long documents need more tokens in the paper's OCR evaluation; newspaper pages especially required dynamic high-resolution modes to reach acceptable reported edit distance.[^deepseek-ocr-paper]
- **The representation is lossy and modality-dependent.** It requires a renderer, a compatible visual encoder, and a decoder that can recover or reason from the retained visual representation. Non-textual conversational state, exact formatting, and retrieval addressing require separate design and evaluation.

## Evidence boundary

The source reports OCR on rendered document pages rather than end-to-end dialogue-history or retrieval experiments. It proposes future digital-optical interleaved pretraining and needle-in-a-haystack evaluation, so claims of unlimited context, effective memory management, or a human-like forgetting mechanism remain hypotheses rather than demonstrated system properties.[^deepseek-ocr-paper]

## Relationships

- **Prototyped by:** [DeepSeek-OCR](deepseek-ocr.md), which tests vision-token compression through OCR reconstruction.

[^deepseek-ocr-paper]: Wei, Sun, and Li, *DeepSeek-OCR: Contexts Optical Compression*, local LaTeX source at [main.tex](../raw/2510.18234_DeepSeek-OCR/main.tex), including `figures/4.pdf` and `figures/precision_compression_chart.pdf` (accessed 2026-08-17).
