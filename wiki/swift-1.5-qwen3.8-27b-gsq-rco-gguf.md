---
type: Concept
title: Swift 1.5 Qwen3.8-27B GSQ-RCO GGUF
description: Mixed-precision GSQ-RCO GGUFs of thinking-efficient Swift 1.5 post-train with KLD fidelity versus BF16, MTP builds, and llama.cpp serving.
tags: [qwen3.8, swift, gguf, quantization, gsq, rco, llama-cpp, mtp, local-inference]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T20:00:00Z }
stale_after: 2027-04-05
sources:
  - id: swift-gsq-rco
    resource: ../raw/Swift-1.5-Qwen3.8-27B-GSQ-RCO-GGUF.md
    title: Swift 1.5 Qwen3.8-27B GSQ-RCO GGUF model card
---

UkisAI publishes four mixed-precision GSQ-RCO GGUF quantizations of `Swift 1.5 Qwen3.8-27B` that reuse the ISTA-DASLab per-tensor allocations for Qwen3.8-27B with a Swift V1MIX importance matrix plus Swift-specific refinement, reporting KLD fidelity against Swift 1.5 BF16 across prose, code, math, and multilingual text, with optional MTP-head builds and a llama.cpp `llama-server` recipe[^swift-gsq-rco]. **Reported** by the model card throughout; no weights, commands, or benchmarks were executed here.

## Release identity

- Publisher path is `ukisai/Swift-1.5-Qwen3.8-27B-GSQ-RCO-GGUF`; base is `ukisai/Swift-1.5-Qwen3.8-27b` with `base_model_relation: quantized`; frontmatter declares `pipeline_tag: text-generation`, `library_name: gguf`, license `swift-open-license-1.0`, and tags for `gguf`, `llama.cpp`, `qwen3_8`, `gsq`, `rco`, reasoning, efficient-thinking, and token-efficient post-training[^swift-gsq-rco]. **Reported**, with static frontmatter presence **Observed**.
- This is an adaptation by UkisAI of GSQ/RCO methods plus ISTA-DASLab allocations; GSQ and RCO were developed by the Deep Algorithms and Systems Lab at the Institute of Science and Technology Austria[^swift-gsq-rco]. **Reported**.
- Tier names denote mixed-precision allocation profiles, not a uniform type for every tensor; sizes are decimal GB and runtime memory additionally includes context cache plus compute buffers[^swift-gsq-rco]. **Reported**.
- Exact file identities are recorded in `release-manifest.json` and `SHA256SUMS`; both were referenced but not in `raw/` and are uninspected[^swift-gsq-rco]. **Reported** with that limit.

## Base model and thinking efficiency

- Swift 1.5 builds on Swift 1.0 through post-training focused on long-horizon, agentic, and coding tasks, improving overall performance while using fewer thinking tokens; training approach and model-level benchmarks belong to the original card `ukisai/Swift-1.5-Qwen3.8-27b` and are separate from the quantization measurements below[^swift-gsq-rco]. **Reported**.
- Model-level headline, not a quantization result: Swift 1.5 uses **58.5% fewer thinking tokens** while scoring **0.35% higher** than the base, for a **9.18× speed-up** on several tasks[^swift-gsq-rco]. **Reported**; harness, tasks, and baseline for that headline are unstated in this card.
- Per the SCOPE benchmark rule, these vendor figures state no hardware, engine versions, workload shapes, or harness, so they stay **Reported** (**Synthesis** on the rule application).

## Available files

Each tier is one GGUF file; `-mtp` files retain the matching refined tensors and add the MTP head[^swift-gsq-rco]. **Reported**.

| Tier | Standard GGUF | With MTP head | Development KLD ↓ |
| --- | ---: | ---: | ---: |
| IQ2_XS | 8.42 GB | 8.77 GB | 0.189979 |
| IQ2_S | 9.26 GB | 9.61 GB | 0.134751 |
| IQ3_XXS | 10.09 GB | 10.44 GB | 0.097774 |
| IQ3_S | 11.77 GB | 12.12 GB | 0.051265 |

- Full filenames are `Swift-1.5-Qwen3.8-27B-GSQ-RCO-<tier>.gguf` and `Swift-1.5-Qwen3.8-27B-GSQ-RCO-<tier>-mtp.gguf`[^swift-gsq-rco]. **Reported**.
- The `-mtp` files require a runtime with support for this model's MTP implementation; KLD results were measured on the standard files, and MTP decoding speed plus quality were not separately evaluated[^swift-gsq-rco]. **Reported**.

## Evaluation method

- Metric is KLD of the quantized next-token distribution from **Swift 1.5 BF16**; lower is better[^swift-gsq-rco]. **Reported**.
- Development measurement uses `wiki.test.raw`, 100 chunks, 512-token context; development data informed refinement and is not independent validation[^swift-gsq-rco]. **Reported**.
- Held-out sets use C4 prose, CodeParrot code, GSM8K math text, and multilingual mC4 text; prose/code/math use 100 chunks each and German/French/Spanish/Chinese use 25 chunks each, all at context 512; these are distributional KLD measurements, not task accuracy or math benchmark scores[^swift-gsq-rco]. **Reported**.
- Full table plus error estimates are in `evaluation/heldout-kld.tsv` and exact-identity binding is in `evaluation/report.json`; both were referenced but not in `raw/` and are uninspected[^swift-gsq-rco]. **Reported** with that limit.

## Held-out KLD results

Held-out KLD versus Swift 1.5 BF16 at 512-token context, paired per format and baseline per the quantization domain rule[^swift-gsq-rco]. **Reported**.

| Held-out text | IQ2_XS | IQ2_S | IQ3_XXS | IQ3_S |
| --- | ---: | ---: | ---: | ---: |
| C4 prose | 0.161594 | 0.107438 | 0.080238 | 0.041748 |
| CodeParrot code | 0.120884 | 0.084739 | 0.062546 | 0.035447 |
| GSM8K math text | 0.117467 | 0.096348 | 0.075964 | 0.043916 |
| German | 0.124482 | 0.091422 | 0.074645 | 0.035698 |
| French | 0.166785 | 0.113277 | 0.077791 | 0.046219 |
| Spanish | 0.082313 | 0.056393 | 0.039906 | 0.024186 |
| Chinese | 0.207063 | 0.129485 | 0.103141 | 0.052241 |

- All four refined files improve KLD over their matched Swift starting quantizations on all seven reporting domains[^swift-gsq-rco]. **Reported**.
- Results are not uniformly better than the ISTA comparison quants: math-text KLD is 4.9–7.7% higher, and IQ3_S is higher on five of seven domains[^swift-gsq-rco]. **Reported**.
- ISTA comparisons measure each quant against its own corresponding BF16 model; they are not direct Swift-versus-Qwen task rankings or proof of equivalent capability[^swift-gsq-rco]. **Reported**.
- A lexical overlap screen was applied against calibration/development text; it does not establish semantic deduplication or prove absence of overfitting; these 512-token tests do not establish quality at 32K or longer contexts[^swift-gsq-rco]. **Reported**.

## Usage

Use a llama.cpp build that supports Qwen3.8; authenticate with an account granted access while the repository is private[^swift-gsq-rco]. **Reported** recipes, not reproduced here; no engine version or commit is stated, and flags below are a snapshot covered by `stale_after`.

```bash
hf download ukisai/Swift-1.5-Qwen3.8-27B-GSQ-RCO-GGUF Swift-1.5-Qwen3.8-27B-GSQ-RCO-IQ3_XXS.gguf --local-dir .

llama-server \
  -m Swift-1.5-Qwen3.8-27B-GSQ-RCO-IQ3_XXS.gguf \
  --jinja -fa on -ngl 99 -c 262144 \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --presence-penalty 0.0 --repeat-penalty 1.0 --port 8000
```

- Set context size to fit available memory; the example `262144` setting is not a claim that these quants were evaluated at that length[^swift-gsq-rco]. **Reported**.
- This release provides language-model GGUFs only; a Swift 27B vision projector has not been verified for this release, so no projector or validated vision example is included[^swift-gsq-rco]. **Reported**.

## Quantization procedure

1. Reuse the published ISTA GSQ-RCO per-tensor allocation for each matching Qwen3.8-27B tier[^swift-gsq-rco]. **Reported**.
2. Quantize Swift 1.5 weights with the Swift V1MIX importance matrix and the selected allocation[^swift-gsq-rco]. **Reported**.
3. Apply Swift-specific GSQ refinement: IQ2_XS and IQ3_XXS use the preserved fixed-objective variants; IQ2_S and IQ3_S use their preserved V1MIX variants[^swift-gsq-rco]. **Reported**.
4. Freeze exact file identities, run the reporting evaluations, and preserve the matching MTP packages[^swift-gsq-rco]. **Reported**.
- This release reuses ISTA's allocation search results; it does not claim a new RCO search on Swift[^swift-gsq-rco]. **Reported**.
- Archived recipe records document construction settings plus historical candidates; the release manifest identifies the selected files; the Swift importance matrix is included as `imatrix-swift15-v1mix.gguf`[^swift-gsq-rco]. **Reported**; recipe, manifest, and imatrix were not in `raw/` and are uninspected.
- Per-tensor assignments for all eight files are in `tensor-allocation/`; each dump records the model SHA256, tensor count, and type histogram; MTP dumps contain the 851 model tensors plus 15 head tensors[^swift-gsq-rco]. **Reported**; dumps uninspected.

## Methods and acknowledgements

- **GSQ:** paper `arXiv:2604.18556` plus code `github.com/IST-DASLab/GSQ`[^swift-gsq-rco]. **Reported**.
- **RCO:** paper `arXiv:2605.00649` plus code `github.com/IST-DASLab/RCO`[^swift-gsq-rco]. **Reported**.
- **GGUF runtime and conversion:** `llama.cpp` (`github.com/ggml-org/llama.cpp`)[^swift-gsq-rco]. **Reported**.
- Acknowledgements: Qwen team for the original model, ISTA-DASLab for methods plus published allocations, and NVIDIA Innovation Lab, AWS, and Google Cloud for supporting Swift development[^swift-gsq-rco]. **Reported**.

## License and access

- Adapted weights under Swift Open License v1.0; original Qwen components retain Apache 2.0 plus `NOTICE`; see the Swift license for terms and enterprise licensing[^swift-gsq-rco]. **Reported**.
- Private-repository authentication note is an access boundary, not a credential; no sensitive values were found in the source.

## Relationships

- Uses [ISTA-DASLab Qwen3.8-27B GSQ-RCO GGUF](ista-qwen3.8-27b-gsq-rco-gguf.md) — reuses that release's per-tensor GSQ-RCO allocations tier-for-tier for a Swift 1.5 post-train instead of base Qwen3.8-27B; see there for the authoritative GSQ/RCO method summary, BF16 vision projector, and Unsloth Dynamic comparison absent here.
- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 27B dense family local path; this page is the thinking-efficient Swift 1.5 alternative with its own 8.42–11.77 GB ladder and no verified vision projector.
- Uses [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — KLD-against-BF16 plus leakage-controlled held-out design used here is the same fidelity signal that page recommends over accuracy or perplexity alone.
- Uses [Unsloth MTP Local Inference](unsloth-mtp-local-inference.md) — the `-mtp` builds preserve the MTP head for speculative decoding with the same extra-file planning shape documented there, though MTP speed and quality are unevaluated here.

## Coverage limits

- Entry point `../raw/Swift-1.5-Qwen3.8-27B-GSQ-RCO-GGUF.md` inspected statically (**Observed**); no commands executed, so install/run recipes and KLD figures are **Reported**, not reproduced.
- Referenced local artifacts absent from `raw/` and uninspected: `release-manifest.json`, `SHA256SUMS`, `evaluation/heldout-kld.tsv`, `evaluation/report.json`, `RECIPE.txt`, `tensor-allocation/` dumps, `imatrix-swift15-v1mix.gguf`, banner image, `LICENSE`, `LICENSE-APACHE-2.0`, and `NOTICE`.
- External evidence uninspected: `ukisai/Swift-1.5-Qwen3.8-27b` original card and BF16 weights, `ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF` allocations, GSQ/RCO papers and code, llama.cpp builds, and Hugging Face file bytes.
- No publication or revision date, eval harness version, hardware, or uncertainty figures appear beyond the stated KLD error-estimate pointer; benchmark claims therefore stay **Reported** under the SCOPE benchmark rule.

[^swift-gsq-rco]: Swift 1.5 Qwen3.8-27B GSQ-RCO model card — `../raw/Swift-1.5-Qwen3.8-27B-GSQ-RCO-GGUF.md` (UkisAI; Swift Open License v1.0 plus Apache-2.0/NOTICE for Qwen components; base `ukisai/Swift-1.5-Qwen3.8-27b`; frontmatter plus sections Available quantizations / Evaluation / Usage / Quantization procedure / Methods and acknowledgements / License and access): Swift 1.5 thinking-efficiency headline (58.5% fewer thinking tokens, +0.35%, 9.18× speed-up) kept separate from quantization evidence; four-tier 8.42–11.77 GB ladder plus `+0.35 GB -mtp` builds with development KLD 0.189979–0.051265; KLD-vs-Swift-BF16 method (`wiki.test.raw` dev plus C4/CodeParrot/GSM8K/multilingual-mC4 held-out at 512 tokens) with seven-domain KLD table, matched-Swift-improvement plus ISTA-comparison limits, non-independent-dev plus lexical-screen plus short-context caveats; Qwen3.8 llama.cpp `hf download` plus `llama-server` recipe with private-access auth, context-sizing note, and no verified vision projector; four-step reuse-quantize-refine-freeze procedure with no new RCO search, V1MIX versus fixed-objective refinement split, and manifest/recipe/imatrix plus 851+15-tensor allocation dumps; GSQ `arXiv:2604.18556` / RCO `arXiv:2605.00649` plus llama.cpp and Qwen/ISTA/cloud acknowledgements.
