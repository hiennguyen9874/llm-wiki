---
type: Attention Mechanism
title: Reference Sliding Window Attention
description: Reference Sliding Window Attention preserves a fixed reference prefix while restricting generated-token attention to a bounded causal window, bounding decode-side KV-cache growth for a fixed prefix.
tags: [attention, sliding-window-attention, kv-cache, long-horizon, sequence-modeling]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T13:30:03Z }
sources:
  - id: unlimited-ocr-report
    resource: ../raw/2606.23050_Unlimited-OCR/main.tex
    title: Unlimited OCR Works
---

# Reference Sliding Window Attention

Reference Sliding Window Attention (R-SWA) is a causal attention pattern for reference-based generation. A generated token attends to every token in a fixed reference prefix, such as document-image features and a prompt, but only a bounded window of prior generated tokens. It thereby preserves direct access to reference content while making decode-side cache use independent of generated length after the window fills.[^unlimited-ocr-report]

## Mechanism

For a prefix of length $L_m$ and output-window width $n$, output token $t$ attends to all prefix positions and output positions from $\max(L_m+1,L_m+t-n)$ through $L_m+t-1$. The retained KV cache is therefore $L_m + \min(n,T)$ after $T$ output tokens, rather than the $L_m+T$ retained by full causal attention.[^unlimited-ocr-report]

Unlike ordinary sliding-window attention, R-SWA does not evict the reference prefix. The source argues that preserving visual references avoids progressive degradation of the static input while the bounded output window carries local generation state. Its Unlimited OCR implementation uses an output window of 128 tokens by default.[^unlimited-ocr-report]

## Scope and limits

The bounded quantity applies to the generated continuation for a fixed reference prefix, not to total inference cost regardless of input size: a larger document produces a larger visual prefix. The source evaluates the mechanism in document OCR and proposes, but does not test, transfer to ASR and translation.[^unlimited-ocr-report]

## Relationships

- **Implemented by:** [Unlimited OCR](unlimited-ocr.md), which applies R-SWA to every decoder attention layer for long-horizon document parsing.[^unlimited-ocr-report]

[^unlimited-ocr-report]: Yin et al., *Unlimited OCR Works*, local LaTex source at [main.tex](../raw/2606.23050_Unlimited-OCR/main.tex), including [R-SWA attention diagram](../raw/2606.23050_Unlimited-OCR/Figs/1.pdf) and [architecture diagram](../raw/2606.23050_Unlimited-OCR/Figs/3.pdf) (accessed 2026-08-17).
