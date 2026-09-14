---
type: Concept
title: vLLM Text Watermarking
description: Statistical generation-time watermarking with Gumbel-max and dual-key variants, Philox PRF, context deduplication, speculative-decoding rules, and separate token-ID detection.
tags: [vllm, watermarking, inference, sampling]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: watermarking
    resource: ../raw/vllm/features/watermarking.md
    title: Text watermarking
---

vLLM embeds a statistical signal in generated token choices that a detector knowing the generation parameters can test without model weights[^watermarking].

## Configuration

- Enable with `--watermark-config '{"algorithm":"gumbel","key":42}'`; omitted means disabled[^watermarking].
- Within an enabled `WatermarkConfig`, Gumbel-max is the default algorithm[^watermarking].
- When configured, watermarking is enabled for requests by default; opt out per request with `SamplingParams(watermarking=False)` or OpenAI-compatible `watermarking: false`[^watermarking].
- Deployments requiring watermarking must restrict that request field to trusted callers, or strip and validate it at ingress, so untrusted clients cannot opt out[^watermarking].
- `context_width` controls how many prior tokens seed each decision and defaults to 4; larger values are less robust to edits because one insertion, deletion, or substitution changes more subsequent contexts; values above 16 are allowed but warn[^watermarking].
- `allow_target_only_watermarking` defaults to `false` and only matters with speculative decoding; it permits an algorithm without native speculative support at the cost of weaker detectability[^watermarking].

## Architecture

- `WatermarkConfig` selects an algorithm and PRF; Model Runner V2 constructs the corresponding `Watermarker`, and `GPUWatermarkSampler` invokes it for final stochastic token selection after temperature, min-p, top-k, and top-p[^watermarking].
- A watermarker either selects a token directly or transforms logits and delegates to vLLM's random sampler[^watermarking].
- Detection is separate from generation; vLLM provides detector primitives for the reference algorithms, and `WatermarkDetector` consumes token IDs, leaving callers responsible for matching tokenizer and watermark profile to generation[^watermarking].

## Speculative decoding

- Requires probabilistic draft sampling, standard rejection sampling, and an autoregressive model-based method: `dspark`, `eagle`, `eagle3`, or `mtp`; only `dspark` supports parallel drafting[^watermarking].
- An algorithm without native speculative support is rejected before model loading; `"allow_target_only_watermarking": true` allows it, leaving accepted draft tokens unwatermarked while target-side rejection recovery and bonus sampling remain watermarked[^watermarking].
- Signal dilution is proportional to the share of output tokens supplied by accepted drafts; rejected drafts do not dilute because recovery tokens are watermarked[^watermarking].
- Speculative token paths do not support generation-side context deduplication; configured `deduplicate_contexts` is not applied to accepted drafts, rejection-recovery tokens, or bonus tokens[^watermarking].
- For `dual_key_gumbel`, `alpha` has no effect under speculative decoding because the protocol selects the key per token[^watermarking].

## Gumbel-max

- Derives deterministic pseudorandom values from key, prior-token context, and every candidate token, then uses the resulting Gumbel noise for categorical sampling[^watermarking].
- Requires stochastic sampling; greedy requests (`temperature=0`) bypass watermarking and warn once per worker[^watermarking].
- Repeated token contexts use ordinary sampling for that occurrence to preserve single-sequence non-distortion; the detector independently deduplicates contexts so generation-time deduplication does not reduce signal unless output is tampered to remove the first occurrence while leaving an unwatermarked repetition[^watermarking].
- `deduplicate_contexts`[^watermarking]:
  - `"none"`: disables deduplication.
  - `"single_turn"`, default: searches tokens generated for the current request, giving single-turn non-distortion.
  - `"all"`: also searches the prompt, extending non-distortion across conversation turns; the first `context_width` generated tokens use ordinary sampling and contexts already in the prompt are not watermarked. This can leave little watermarked output when prior turns or prompt material such as tool results already contain the answer structure, and costs more because sampling scans more history. Use only when multi-turn non-distortion is required.
- `deduplicate_contexts_max_history` limits search to the most recent positions, default 8,192; each position compares the `context_width` tokens before it, so the token window read is that much longer; smaller values reduce cost but only guarantee within that window; `null` searches to the start of generation for `"single_turn"` or start of request for `"all"` at growing cost; no effect when `deduplicate_contexts` is `"none"`; values below 1,024 warn because short windows can miss repetition loops[^watermarking].
- Example checking prompt and completion history within the default window[^watermarking]:

```bash
vllm serve MODEL \
  --watermark-config \
  '{"algorithm":"gumbel","key":42,"deduplicate_contexts":"all"}'
```

## Dual-key Gumbel-max

- Derives independent keys A and B from one configured master key; during ordinary generation each token uses key A with probability `1 - alpha` and key B with probability `alpha`; `alpha` defaults to 0.1; detection scores every token against both keys[^watermarking].
- The same two key streams support speculative decoding without changing acceptance rate: the protocol selects the key instead of `alpha`, with draft tokens using key A and rejection-recovery plus bonus tokens using key B; the ordinary target-to-draft probability-ratio test is unchanged[^watermarking].
- Select with probabilistic drafting[^watermarking]:

```bash
vllm serve MODEL \
  --speculative-config \
  '{"method":"mtp","num_speculative_tokens":3,"draft_sample_method":"probabilistic"}' \
  --watermark-config '{"algorithm":"dual_key_gumbel","key":42,"alpha":0.1}'
```

## Other algorithms and PRFs

- [SynthID-Text](https://www.nature.com/articles/s41586-024-08025-4) is planned but not implemented[^watermarking].
- A watermark PRF turns secret key, token context, and candidate token into reproducible random values; generation and detection must match across devices and releases, with values uniform and independent enough for sampling and detector statistics; PRF selection is an advanced compatibility and performance setting and most users should keep the default[^watermarking].
- Currently supported: `philox`, based on counter-based Philox4x32-10; parallel, vectorizes on accelerators, avoids CPU transfers, but is not cryptographic and provides no key-recovery or forgery resistance; vLLM versions its input mapping and provides compatibility vectors for interoperable generation and detection[^watermarking].

## Detection

- Detector primitives operate on token IDs without model weights[^watermarking]:

```python
from transformers import AutoTokenizer

from vllm.v1.watermarking import GumbelWatermarkDetector

tokenizer = AutoTokenizer.from_pretrained(MODEL)
token_ids = tokenizer.encode(text, add_special_tokens=False)
result = GumbelWatermarkDetector(key=42, prf="philox").detect(token_ids)
print(result.p_value, result.is_watermarked)
```

- Detection configuration must match generation, including tokenizer, PRF, algorithm, algorithm-specific configuration, and key; because this is often unavailable when inspecting text, retain served candidate configurations, test against each, and correct for multiple testing, for example with Bonferroni correction[^watermarking].
- Gumbel-max detection scores repeated contexts once by default so identical PRF vectors are not treated as independent evidence; keep `deduplicate_contexts=True` unless detector calibration was adjusted for correlated scores[^watermarking].
- The p-value assumes scored PRF inputs are independent; one fixed deployment key means repeated structures across documents reuse the same PRF values and can make the realized false-positive rate key-dependent even with within-document deduplication; measure false-positive rate on representative unwatermarked traffic with the deployed key before relying on `is_watermarked`[^watermarking].
- A minimal HTTP detector is available at `examples/basic/online_serving/watermark_detection_server.py`, not inspected here[^watermarking]:

```bash
python examples/basic/online_serving/watermark_detection_server.py \
  --tokenizer MODEL --key 42 --prf philox
```

```bash
curl http://localhost:8000/detect \
  -H 'Content-Type: application/json' \
  -d '{"text":"Text to inspect"}'
```

- Scores and p-values leak per-token signal information; repeated queries can be used to imitate watermarked output or edit watermarked text to evade detection[^watermarking].

## Limitations

- Only available with Model Runner V2[^watermarking].
- Not all algorithms have native speculative-decoding support[^watermarking].
- Beam search expands candidates from model log probabilities and does not apply Gumbel-max watermarking[^watermarking].
- Models replacing the vLLM sampler with a custom sampler cannot use configured watermarking[^watermarking].

## Coverage limits

- RFC discussion, Aaronson presentation, SynthID-Text materials, and Random123 paper were treated as external identifiers and not fetched[^watermarking].
- The example detection-server script and tokenizer behavior were outside `raw/` and not inspected[^watermarking].

## Relationships

- Uses [vLLM Model Runner V2](vllm-model-runner-v2.md) — runner constructs the `Watermarker` and `GPUWatermarkSampler` performs watermarked stochastic selection.
- Uses [vLLM Entrypoints](vllm-entrypoints.md) — configured at engine startup via `vllm serve` and controlled per request through `SamplingParams` or the OpenAI-compatible `watermarking` field.

[^watermarking]: Text watermarking — `../raw/vllm/features/watermarking.md`, full page.
