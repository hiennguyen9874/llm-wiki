---
type: Concept
title: Qwen3.5-27B checkpoint architecture and implementation
description: The supplied Qwen3.5-27B checkpoint configuration implements a 64-layer multimodal hybrid of three Gated DeltaNet layers followed by one global GQA layer, with a separate vision encoder.
tags: [qwen3-5, hybrid-attention, gated-deltanet, grouped-query-attention, multimodal, checkpoint]
status: stable
created: 2026-08-15
generated: { by: llm-wiki-agent/1, at: 2026-08-15T03:38:48Z }
sources:
  - id: qwen35-27b-config
    resource: ../raw/Qwen3.5-27B/config.json
    title: "Qwen3.5-27B checkpoint configuration"
  - id: qwen35-modeling
    resource: ../raw/Qwen3.5-27B/modeling_qwen3_5.py
    title: "Qwen3.5 Transformers reference modeling implementation"
  - id: qwen35-modular
    resource: ../raw/Qwen3.5-27B/modular_qwen3_5.py
    title: "Qwen3.5 Transformers modular source"
  - id: qwen35-tokenizer
    resource: ../raw/Qwen3.5-27B/tokenization_qwen3_5.py
    title: "Qwen3.5 Transformers tokenizer implementation"
---

# Qwen3.5-27B checkpoint architecture and implementation

The supplied checkpoint configuration is a multimodal, dense 64-layer text backbone that repeats three recurrent Gated DeltaNet token mixers followed by one global grouped-query-attention (GQA) mixer, plus a 27-block vision encoder. This hybrid bounds the sequence-state growth of 48 text layers but retains ordinary token-growing KV state in the 16 full-attention layers; the bundle documents architecture and reference execution only, not training, quality, or serving results.[^qwen35-27b-config][^qwen35-modeling]

## Text backbone

The provided configuration has hidden width 5,120, a 17,408-wide SiLU-gated MLP, 64 text layers, a 248,320-token vocabulary, BF16 model dtype, and a declared maximum position embedding length of 262,144. Its explicit layer list contains 48 `linear_attention` layers and 16 `full_attention` layers, in a repeating three-to-one schedule.[^qwen35-27b-config]

Each decoder layer applies RMS normalization, one of those token mixers, a residual addition, then a second RMS normalization, SiLU-gated MLP, and another residual addition. The modular source identifies no expert-parallel plan, so this supplied architecture is dense rather than a routed MoE.[^qwen35-modeling][^qwen35-modular]

### Global-attention layers

The full-attention blocks use 24 query heads and four KV heads of width 256: six query heads share each KV head. They apply per-head RMS normalization to Q and K, RoPE to the rotary portion of Q/K, and a sigmoid output gate derived from a second query projection before the output projection.[^qwen35-27b-config][^qwen35-modeling]

These layers update the ordinary per-token KV cache when a cache is supplied. They therefore preserve token-addressable global retrieval, while their state and cache reads still grow with generated-context length.[^qwen35-modeling]

### Recurrent linear-attention layers

The other 48 layers instantiate `Qwen3_5GatedDeltaNet`: 16 key heads and 48 value heads, each with width 128, and a depthwise causal convolution of kernel width four. The implementation projects Q/K/V, applies the short convolution and SiLU, derives a sigmoid write strength $\beta$, and derives a negative, input-dependent decay from `A_log`, `softplus(a + dt_bias)`. It repeats each key/query head three times to align with the 48 value heads, then executes a chunked gated-delta-rule kernel for sequences or a recurrent kernel for cached one-token decoding.[^qwen35-27b-config][^qwen35-modeling]

The cache for a recurrent layer carries convolution and recurrent states, rather than appending a KV entry for every token. This changes the text backbone's memory mix; it does not make the model's end-to-end cache fixed-size because the periodic full-attention layers remain token-cached.[^qwen35-modeling]

## Positions and multimodal input

Text RoPE uses a 10,000,000 base and rotates one quarter of the 256-dimensional attention head. The configuration’s three 11/11/10 M-RoPE sections are interleaved across temporal, height, and width position IDs in the implementation.[^qwen35-27b-config][^qwen35-modeling]

The vision encoder has 27 blocks at width 1,152 with 16 heads. It forms patches through a 3-channel Conv3D with temporal patch size two and spatial patch size 16, performs non-causal vision attention, spatially merges $2\times2$ features, and projects them to the text width of 5,120. Image and video feature vectors replace matching placeholder-token embeddings; multimodal calls require `mm_token_type_ids` so the implementation can construct correct three-dimensional RoPE positions.[^qwen35-27b-config][^qwen35-modeling]

The bundled tokenizer is byte-level BPE with NFC normalization and a Qwen-specific pre-tokenization regex; its default unknown, end-of-sequence, and padding token is `<|endoftext|>`.[^qwen35-tokenizer]

## Relationships

- **Uses:** [Gated DeltaNet architecture and chunkwise training](gated-deltanet-architecture-and-training.md) as the recurrent token mixer, with a three-linear-to-one-global hybrid schedule.[^qwen35-modeling]
- **Uses:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md) in its global layers, at six query heads per KV head.[^qwen35-27b-config]
- **Uses:** [Rotary position embedding (RoPE)](rotary-position-embedding.md) through partial, interleaved multimodal rotary embeddings.[^qwen35-27b-config][^qwen35-modeling]
- **Uses:** [KV caching](kv-caching.md) for its full-attention layers while recurrent layers retain a different state form.[^qwen35-modeling]
- **Contrasts with:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md): only the recurrent portion has bounded recurrent state; periodic global attention remains token-addressable and sequence-growing.[^qwen35-modeling]

## Evidence limits

The source bundle contains configuration and Transformers reference code, but no weights, model card, training data, training procedure, evaluation results, context-quality measurement, or serving benchmark. The directory name identifies the supplied checkpoint as “27B,” but the included configuration does not independently state or derive a total parameter count.

`config.json` sets `mtp_num_hidden_layers` to one, but the supplied `Qwen3_5ForCausalLM` defines no MTP module and ignores unexpected `mtp.*` checkpoint keys. This bundle therefore does not establish that MTP is active for this checkpoint’s inference path.[^qwen35-27b-config][^qwen35-modeling]

`modeling_qwen3_5.py` declares itself generated from `modular_qwen3_5.py`. Both were inspected; the generated file provides the concrete reference implementation used for the claims above, not a production-kernel or deployment specification.[^qwen35-modeling][^qwen35-modular]

[^qwen35-27b-config]: Qwen Team, “Qwen3.5-27B checkpoint configuration,” [source](../raw/Qwen3.5-27B/config.json), text and vision configuration.

[^qwen35-modeling]: Qwen Team and Hugging Face, “Qwen3.5 Transformers reference modeling implementation,” [source](../raw/Qwen3.5-27B/modeling_qwen3_5.py), `Qwen3_5GatedDeltaNet`, `Qwen3_5Attention`, `Qwen3_5TextModel`, `Qwen3_5VisionModel`, and conditional-generation wrappers.

[^qwen35-modular]: Qwen Team and Hugging Face, “Qwen3.5 Transformers modular source,” [source](../raw/Qwen3.5-27B/modular_qwen3_5.py), module header and Qwen3.5 model classes.

[^qwen35-tokenizer]: Qwen Team and Hugging Face, “Qwen3.5 Transformers tokenizer implementation,” [source](../raw/Qwen3.5-27B/tokenization_qwen3_5.py), `Qwen3_5Tokenizer`.
