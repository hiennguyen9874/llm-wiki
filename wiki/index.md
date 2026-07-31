---
okf_version: "0.2"
---

# LLM Wiki

The complete retrieval map for compiled knowledge. See [LLM Wiki Contract](../LLM-WIKI.md) for storage and maintenance rules.

## Concepts

- [Attention Residuals](attention-residuals.md) — Attention Residuals replace uniform residual accumulation with learned retrieval over earlier depth-wise representations.
- [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — Delta-rule memory corrects selected key-value associations, while learned decay adds broader eviction and per-channel capacity control.
- [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) — Kimi K3 combines bounded recurrent memory, periodic softmax retrieval, sparse expert capacity, and depth-wise residual retrieval.
- [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md) — Linear attention trades token-addressable KV storage for a fixed-size associative state, reducing decode-state growth while introducing capacity interference.
