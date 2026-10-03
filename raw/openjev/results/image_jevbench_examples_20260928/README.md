# Image Decisions smoke checks — 2026-09-28

These are **eight published, resized Image JevBench website examples**, not
the full 228-public / 456-sealed benchmark. No full benchmark score or rank is
claimed. No calibration parameters were fitted on these examples.

| Model | Correct | Valid distributions | ECE, 10 bins | Brier | p50 | p95 |
|---|---:|---:|---:|---:|---:|---:|
| OpenJev 4B NLI v5 | 7/8 | 8/8 | 0.11135 | 0.208879 | 0.678 s | 6.864 s |
| OpenJev 0.8B NLI v6, local unpublished checkpoint | 6/8 | 8/8 | 0.3669 | 0.4129 | 0.427 s | 0.796 s |

Measured through the production SGLang V100 FP16 gateways and the patched
JevBench CLI, with unchanged scoring functions. These small latency samples
include possible first-use compilation of new shapes; they are not a throughput
benchmark. Hosting cost was not measured. Zero reserved/charged dollars in the
local ledger does not mean free compute. Summaries are alongside this file.

The public 4B v5 weights are available in this model repository. The 0.8B v6
row documents a local check only; its weights are not part of this publication.

Source examples: `fstandhartinger/model-market-comparison` at
`e28f6fd91cf3f8055f315cef9d85618a25062a2a`,
`lib/image-jev-public-examples.mjs` and `public/image-jev/examples/`.
JevBench base: `fd54ea7dc02bbe29c6ac8f6e015a54cdcff26805`.
The update normalizes per-option entailment probabilities and identifies them
as `normalized_entailment_v1`; it does not assert that they are well calibrated.

Validation: all 16 responses passed strict distribution validation; all stored
raw-response hashes were verified. There were 39 local gateway/API/proxy tests
and 17 unchanged JevBench protocol tests passing. On two image NLI pairs,
SGLang and the Transformers multimodal backbone plus original classification
head agreed on both argmaxes, with maximum probability difference 0.000092583.
The saved parity output is in `image_parity_20260928/`. The pixel control shows
that changing only parcel/receipt image bytes flips the answer on both models.

The official leaderboard requires a separate run by the benchmark maintainer.
