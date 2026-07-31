---
okf_version: "0.2"
---

# LLM Wiki

The complete retrieval map for compiled knowledge. See [LLM Wiki Contract](../LLM-WIKI.md) for storage and maintenance rules.

## Concepts

- [Attention Residuals](attention-residuals.md) — Attention Residuals replace uniform residual accumulation with learned retrieval over earlier depth-wise representations.
- [BERT bidirectional transfer learning](bert-bidirectional-transfer-learning.md) — BERT pre-trains a bidirectional Transformer encoder, then fine-tunes all of its parameters with a small task-specific output layer.
- [BERT masked-language and next-sentence pre-training](bert-masked-language-and-next-sentence-pre-training.md) — BERT learns bidirectional token representations by predicting selected corrupted tokens and jointly classifying whether paired text spans are consecutive.
- [Chinchilla compute-optimal training allocation](chinchilla-compute-optimal-training-allocation.md) — Chinchilla’s fitted loss law reallocates fixed pretraining compute nearly evenly between dense-model parameters and training tokens, yielding an approximate 20-token-per-parameter heuristic.
- [Chinchilla training validation and evaluation](chinchilla-training-validation-and-evaluation.md) — At roughly Gopher’s training-compute budget, the 70B-parameter Chinchilla model trained on about 1.3–1.4T tokens outperformed the 280B-parameter, 300B-token Gopher model on reported loss and downstream evaluations.
- [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — Delta-rule memory corrects selected key-value associations, while learned decay adds broader eviction and per-channel capacity control.
- [Empirical language-model loss scaling laws](empirical-language-model-loss-scaling-laws.md) — Kaplan et al. report power-law cross-entropy scaling with non-embedding parameters, dataset tokens, and batch-adjusted training compute for decoder-only Transformer language models.
- [GPT generative pre-training and task adaptation](gpt-generative-pre-training-and-task-adaptation.md) — GPT pre-trains a decoder-only Transformer language model on contiguous text, then transfers it through discriminative fine-tuning with serialized task inputs.
- [GPT-2 WebText pre-training and architecture](gpt-2-webtext-pre-training-and-architecture.md) — GPT-2 scales a causal Transformer language model on WebText with byte-level BPE, a 1,024-token context, pre-layer normalization, and depth-scaled residual initialization.
- [GPT-2 zero-shot multitask evaluation and overlap auditing](gpt-2-zero-shot-multitask-evaluation-and-overlap-auditing.md) — GPT-2 uses natural-language task cues and demonstrations for zero-shot evaluation, while auditing n-gram overlap to qualify possible training-data contamination.
- [GPT-3 benchmark contamination audit](gpt-3-benchmark-contamination-audit.md) — GPT-3’s report uses conservative n-gram overlap tests and clean-subset evaluation to qualify web-scale benchmark leakage, while documenting a failed pre-training filter and residual uncertainty.
- [GPT-3 in-context learning evaluation and results](gpt-3-in-context-learning-evaluation-and-results.md) — GPT-3 evaluates zero-, one-, and few-shot task behavior through text-only conditioning and completion scoring, reporting scale-sensitive but task-dependent gains without weight updates.
- [GPT-3 limitations and social risk](gpt-3-limitations-and-social-risk.md) — GPT-3’s report documents generation, reasoning, calibration, bias, cost, and misuse limitations alongside a preliminary human study showing realistic synthetic news is difficult to identify.
- [GPT-3 scaled causal language model](gpt-3-scaled-causal-language-model.md) — GPT-3 scales the GPT-2-style causal Transformer to 175B parameters, a 2,048-token context, 300B training tokens, and a quality-weighted web-and-books corpus.
- [Kaplan compute-optimal training allocation](kaplan-compute-optimal-training-allocation.md) — Under Kaplan et al.’s fitted laws, compute-efficient training scales model size much faster than serial training steps and stops well before convergence.
- [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) — Kimi K3 combines bounded recurrent memory, periodic softmax retrieval, sparse expert capacity, and depth-wise residual retrieval.
- [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md) — Linear attention trades token-addressable KV storage for a fixed-size associative state, reducing decode-state growth while introducing capacity interference.
- [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) — Scaled dot-product attention retrieves weighted values from query–key compatibility, while multiple projected heads retrieve from distinct representation subspaces in parallel.
- [Self-attention computational profile](self-attention-computational-profile.md) — Full self-attention offers constant sequential depth and direct token-to-token paths at quadratic full-sequence cost, while restricted attention trades cost for longer paths.
- [The Pile data governance](the-pile-data-governance.md) — The Pile’s heterogeneous public sources create unresolved component-level licensing, privacy, harmful-content, and English-coverage limits that cannot be inferred away by calling the aggregate dataset open.
- [The Pile training corpus](the-pile-training-corpus.md) — The Pile is a 22-source, predominantly English pretraining mixture whose static sampling weights favor a deliberately diverse mix of web, scientific, code, legal, book, and conversational text.
- [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md) — The original Transformer replaces sequence-aligned recurrence and convolution with stacked self-attention, cross-attention, and position-wise feed-forward layers.
