---
okf_version: "0.2"
---

# LLM Wiki

The complete retrieval map for compiled knowledge. See [LLM Wiki Contract](../LLM-WIKI.md) for storage and maintenance rules.

## Concepts

- [Attention Residuals](attention-residuals.md) — Attention Residuals replace uniform residual accumulation with learned retrieval over earlier depth-wise representations.
- [BERT bidirectional transfer learning](bert-bidirectional-transfer-learning.md) — BERT pre-trains a bidirectional Transformer encoder, then fine-tunes all of its parameters with a small task-specific output layer.
- [BERT masked-language and next-sentence pre-training](bert-masked-language-and-next-sentence-pre-training.md) — BERT learns bidirectional token representations by predicting selected corrupted tokens and jointly classifying whether paired text spans are consecutive.
- [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — Delta-rule memory corrects selected key-value associations, while learned decay adds broader eviction and per-channel capacity control.
- [GPT generative pre-training and task adaptation](gpt-generative-pre-training-and-task-adaptation.md) — GPT pre-trains a decoder-only Transformer language model on contiguous text, then transfers it through discriminative fine-tuning with serialized task inputs.
- [GPT-2 WebText pre-training and architecture](gpt-2-webtext-pre-training-and-architecture.md) — GPT-2 scales a causal Transformer language model on WebText with byte-level BPE, a 1,024-token context, pre-layer normalization, and depth-scaled residual initialization.
- [GPT-2 zero-shot multitask evaluation and overlap auditing](gpt-2-zero-shot-multitask-evaluation-and-overlap-auditing.md) — GPT-2 uses natural-language task cues and demonstrations for zero-shot evaluation, while auditing n-gram overlap to qualify possible training-data contamination.
- [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) — Kimi K3 combines bounded recurrent memory, periodic softmax retrieval, sparse expert capacity, and depth-wise residual retrieval.
- [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md) — Linear attention trades token-addressable KV storage for a fixed-size associative state, reducing decode-state growth while introducing capacity interference.
- [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) — Scaled dot-product attention retrieves weighted values from query–key compatibility, while multiple projected heads retrieve from distinct representation subspaces in parallel.
- [Self-attention computational profile](self-attention-computational-profile.md) — Full self-attention offers constant sequential depth and direct token-to-token paths at quadratic full-sequence cost, while restricted attention trades cost for longer paths.
- [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md) — The original Transformer replaces sequence-aligned recurrence and convolution with stacked self-attention, cross-attention, and position-wise feed-forward layers.
