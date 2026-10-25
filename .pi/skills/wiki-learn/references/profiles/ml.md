# Course profile: ml

For machine learning and LLM architecture courses.

## Theory

- Derive formulas in `$$` blocks and explain every symbol, dimension, and tensor shape step by step for a reader who knows only basic math.
- Use tables for variants and text diagrams for data flow.

## Practice

Minimal, inspectable PyTorch. Comment the pairing convention, `rotary_dim`, absolute `position_ids`, and cache shape `(B, H_KV, S, d_h)` per layer when attention is involved; use the `interleaved` RoPE convention unless a source states otherwise. Note where toy code diverges from serving (for example, `torch.cat` caching vs paged blocks): toy code is teaching, not serving.

## Verification

Numbered tests such as identity/norm, matrix match, cache-vs-full logits, and future-leakage. Each test uses `torch.testing.assert_close` with explicit `rtol`/`atol` and a dtype note.

## Trade-offs

Include a benchmark only when performance is claimed. Separate prefill and decode, report raw KV bytes `M_KV = 2 L B S H_KV d_h p`, and state what is not concluded. Evidence limits note what must be verified on target hardware and dtype.

## Vocabulary

Keep keywords in English, for example `RoPE`, `GQA`, `KV cache`, `prefill`, `decode`, `shared experts`, `top-k`.
