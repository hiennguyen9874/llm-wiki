---
type: Concept
title: ISTA-DASLab Qwen3.8-27B GSQ-RCO GGUF
description: Non-uniform GSQ-RCO GGUF quantizations of Qwen3.8-27B at 2.5–3.5 bpw with MTP speculative builds and BF16 vision projector, plus card-reported fidelity versus BF16 and Unsloth Dynamic.
tags: [qwen3.8, gguf, quantization, gsq, rco, llama-cpp, vision, mtp, local-inference]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T14:00:00Z }
sources:
  - id: gsq-rco
    resource: ../raw/Qwen3.8-27B-GSQ-RCO-GGUF.md
    title: Qwen3.8-27B GSQ-RCO GGUFs (ISTA-DASLab model card)
---

ISTA-DASLab publishes four non-uniform GGUF quantizations of `Qwen/Qwen3.8-27B` built with GSQ per-tensor scalar quantization plus RCO per-tensor bit allocation under a size budget, reporting near-base quality down to 2.5 bpw with standard llama.cpp, Ollama, and LM Studio compatibility and optional MTP speculative-decoding builds[^gsq-rco]. **Reported** by the model card unless noted; no run verification was performed here.

## Release identity

- Base is `Qwen/Qwen3.8-27B` with `base_model_relation: quantized`; frontmatter declares `pipeline_tag: image-text-to-text`, `library_name: gguf`, and `license: apache-2.0`[^gsq-rco]. **Reported**, with static frontmatter presence **Observed**.
- Publisher is the Hugging Face repo `ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF`; methods come from the Deep Algorithms and Systems Lab (DASLab), Institute of Science and Technology Austria — spelled `IST-DASLab` in prose and `ISTA-DASLab` in repo/badge names, preserved as written[^gsq-rco]. **Reported**.
- Quantized weights inherit the base-model license (`Qwen3.8-27B`); GSQ-RCO tooling is under its repository license[^gsq-rco]. **Reported**.
- Compute acknowledgement: Verda plus Scientific Computing at the Institute of Science and Technology Austria[^gsq-rco]. **Reported**.

## Method summary

- Unlike uniform quantization with one quantization type for all tensors, each file assigns a separate quantization type to every tensor via a gradient-based search that allocates precision by per-tensor sensitivity under a total size budget; outputs are standard GGUF and run unmodified in llama.cpp, Ollama, and LM Studio[^gsq-rco]. **Reported**.
- GSQ (Gumbel-Softmax Quantization, arXiv:2604.18556) is post-training scalar quantization that jointly learns per-coordinate grid assignments and per-group scales via a Gumbel-Softmax relaxation, closing most of the scalar-versus-vector gap at 2–3 bits while staying deployable in standard scalar formats such as GGUF[^gsq-rco]. **Reported**.
- RCO (Riemannian Constrained Optimization, arXiv:2605.00649) assigns one of K quantization types to each of N tensors under a total size budget by reformulating the budget constraint as a smooth Riemannian manifold in logit space, permitting gradient-based optimization directly on task loss while enforcing the budget exactly without constraint-specific hyperparameter tuning[^gsq-rco]. **Reported**.
- Build pipeline in three steps: quantize each weight tensor at every candidate GGUF type with GSQ into a searchable per-tensor database; run the budget-constrained Riemannian search to assign one type per tensor for the target whole-file average bit-width; stitch the selected variants into one standard GGUF[^gsq-rco]. **Reported**.

## Available files

Naming is `<model>-GSQ-RCO-<type>.gguf`; the table lists true whole-file average bit-width[^gsq-rco]. **Reported**.

| File | bpw | Size | Notes |
| --- | --- | --- | --- |
| `Qwen3.8-27B-GSQ-RCO-IQ2_XS.gguf` | 2.50 | 8.4 GB | Smallest; zero-shot above the BF16 baseline |
| `Qwen3.8-27B-GSQ-RCO-IQ2_S.gguf` | 2.75 | 9.3 GB | Matches the base model on AIME25 |
| `Qwen3.8-27B-GSQ-RCO-IQ3_XXS.gguf` | 3.00 | 10.1 GB | Strong all-round operating point |
| `Qwen3.8-27B-GSQ-RCO-IQ3_S.gguf` | 3.50 | 11.8 GB | Recommended; task-lossless |
| `mmproj-Qwen3.8-27B-BF16.gguf` | 16 | 0.9 GB | Vision encoder + projector, for multimodal use |

- The `mmproj` file carries vision encoder plus projector at BF16; one copy serves all quantizations; it was converted directly from the base checkpoint and verified against these quantizations[^gsq-rco]. **Reported**.
- Each quantization also ships an optional `-mtp` build about 0.35 GB larger carrying the Multi-Token Prediction head for speculative decoding in llama.cpp; weights are otherwise identical so quality is unchanged[^gsq-rco]. **Reported**.

## Card-reported results

Evaluated against the BF16 base and Unsloth Dynamic (UD) quantizations of the same base; metrics are wikitext2/C4/FineWeb-Edu perplexity (lower is better), average over five zero-shot tasks (`arc_easy`, `arc_challenge`, `hellaswag`, `winogrande`, `piqa`), recovery as zero-shot average relative to BF16, and AIME25, GPQA-Diamond, and LiveCodeBench v6; sizes are as-evaluated files[^gsq-rco]. **Reported**.

| Variant | bpw | GB | wiki↓ | c4↓ | fw↓ | ZS avg↑ | recovery | AIME25↑ | GPQA-D↑ | LCB v6↑ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BF16 | 16.00 | 53.8 | 7.05 | 11.45 | 8.14 | 74.34 | 100.0% | 100.00 | 89.90 | 85.71 |
| GSQ-RCO IQ2_XS | 2.50 | 8.4 | 7.69 | 12.98 | 9.19 | 74.54 | 100.3% | 96.67 | 84.85 | 76.57 |
| GSQ-RCO IQ2_S | 2.75 | 9.3 | 7.39 | 12.40 | 8.80 | 75.70 | 101.8% | 100.00 | 86.36 | 82.29 |
| GSQ-RCO IQ3_XXS | 3.00 | 10.1 | 7.20 | 12.13 | 8.59 | 74.81 | 100.6% | 100.00 | 88.89 | 84.57 |
| GSQ-RCO IQ3_S | 3.50 | 11.8 | 7.07 | 11.76 | 8.34 | 74.47 | 100.2% | 100.00 | 89.39 | 85.71 |
| UD-IQ2_S | 2.49 | 8.4 | 8.02 | 12.78 | 9.08 | 73.80 | 99.3% | 86.67 | 76.26 | 72.00 |
| UD-Q2_K_XL | 2.88 | 9.8 | 7.54 | 12.25 | 8.69 | 74.37 | 100.0% | 100.00 | 86.87 | 82.28 |
| UD-IQ3_S | 3.52 | 12.0 | 7.16 | 11.75 | 8.34 | 75.49 | 101.5% | 96.67 | 89.90 | 84.00 |

- IQ3_S at 3.50 bpw is the card's task-lossless point: exact base match on AIME25 (100.00) and LiveCodeBench v6 (85.71), 0.51-point trail on GPQA-Diamond, task average 91.70 versus base 91.87 (99.8%) at 11.8 GB — a 4.6x size reduction; versus UD-IQ3_S it leads by 3.33 on AIME25 and 1.71 on LiveCodeBench while 0.2 GB smaller, with UD holding GPQA-Diamond by 0.51[^gsq-rco]. **Reported**.
- At 3.00 bpw IQ3_XXS already matches the base on AIME25 at 10.1 GB; at matched 8.4 GB, IQ2_XS leads UD-IQ2_S by 10.00 on AIME25, 8.59 on GPQA-Diamond, and 4.57 on LiveCodeBench v6; IQ2_S at 2.75 bpw also matches the base 100.00 on AIME25[^gsq-rco]. **Reported**.
- Per the SCOPE benchmark rule, these comparisons state no hardware, engine versions, workload shapes, harness, or protocol beyond benchmark names, so they stay **Reported** with that limit (**Synthesis** on the rule application).

## Usage

llama.cpp text and vision paths, plus Ollama and LM Studio pointers[^gsq-rco]. **Reported** recipes, not reproduced here.

```bash
# download (requires: pip install -U "huggingface_hub[cli]")
hf download ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF Qwen3.8-27B-GSQ-RCO-IQ3_XXS.gguf --local-dir .

llama-cli -m Qwen3.8-27B-GSQ-RCO-IQ3_XXS.gguf -p "Explain mixed-precision quantization." -ngl 99
```

```bash
hf download ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF mmproj-Qwen3.8-27B-BF16.gguf --local-dir .

llama-mtmd-cli -m Qwen3.8-27B-GSQ-RCO-IQ3_XXS.gguf \
  --mmproj mmproj-Qwen3.8-27B-BF16.gguf \
  --image photo.jpg -p "Describe this image."
```

```bash
ollama run hf.co/ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF   # pick the file matching your memory budget
```

- LM Studio: search the repo name, then pick a `GSQ-RCO-*` build from the file list[^gsq-rco]. **Reported**.

## Reproducibility artifacts

- Each GGUF ships audit files: `tensor-allocation/<model>.rco-allocation.txt` with the per-tensor quantization-type assignment plus quant-type histogram and target bit-width (inspectable without opening the model), and `imatrix-qwen3.8-27b.gguf` importance matrix built from 1000 chunks of 4096 tokens[^gsq-rco]. **Reported**.
- `-mtp` builds have their own allocation dumps listing the same per-tensor assignment as the base model plus the 15 tensors of the MTP head[^gsq-rco]. **Reported**.
- Card cites both methods with bibtex for GSQ (`gsq2026`, arXiv:2604.18556) and RCO (`rco2026`, arXiv:2605.00649); publication template notes instruct copying the folder, swapping frontmatter/model/filenames, and regenerating plots via `tools/make_plots.py` on `tools/results/<model>.json`[^gsq-rco]. **Reported**; the tools, results JSON, and generated plots were not in `raw/` and are uninspected.

## Relationships

- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 27B dense base; that page covers the Unsloth GGUF/NVFP4 local path while this is the ISTA-DASLab non-uniform GGUF alternative with its own 8.4–11.8 GB ladder and BF16 vision projector.
- Related to [Dirk Qwen3.8-27B Sharp-Template GGUF](dirk-qwen3.8-27b-gguf.md) — community re-templating whose sub-3-bpw tiers reuse these GSQ-RCO files and whose quality deltas are ISTA's measurements reused secondhand; see here for the authoritative file table and results.
- Uses [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — the UD-IQ2_S/Q2_K_XL/IQ3_S rows in the results table are the comparison baseline against which GSQ-RCO leads at matched size and converges near 3.5 bpw.
- Uses [Unsloth MTP Local Inference](unsloth-mtp-local-inference.md) — the `-mtp` builds preserve the MTP head for multi-token-prediction speculative decoding with the same ~0.35 GB extra-file planning figure documented there.

## Coverage limits

- Entry point `../raw/Qwen3.8-27B-GSQ-RCO-GGUF.md` inspected statically (**Observed**); no commands executed, so install/run recipes and quality figures are **Reported**, not reproduced.
- Remote banner, badge links, and four plot images (task-average, MTP speculative decoding, AIME25, GPQA-Diamond, LiveCodeBench) referenced by Hugging Face URLs were not in `raw/` and are uninspected; the tables above carry the durable numbers.
- External evidence uninspected: GSQ/RCO arXiv papers and GitHub code, `ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF` weight files, `Qwen/Qwen3.8-27B` base checkpoint, `tools/results/<model>.json` plus `tools/make_plots.py`, per-tensor `tensor-allocation/` dumps, and `imatrix-qwen3.8-27b.gguf`.
- No publication or revision date, eval harness/protocol, hardware, or uncertainty figures appear in the card; benchmark claims therefore stay **Reported** under the SCOPE benchmark rule.

[^gsq-rco]: Qwen3.8-27B GSQ-RCO GGUF model card — `../raw/Qwen3.8-27B-GSQ-RCO-GGUF.md` (ISTA-DASLab; Apache-2.0; base `Qwen/Qwen3.8-27B`; frontmatter plus sections Overview / Available files / Results / Usage / Quantization procedure / Reproducibility artifacts / Citation / Acknowledgements / License): GSQ per-coordinate grid plus per-group scale via Gumbel-Softmax and RCO per-tensor type assignment on a Riemannian budget manifold; three-step database-search-assembly pipeline; four-file 2.50–3.50 bpw ladder (8.4–11.8 GB) plus 0.9 GB BF16 `mmproj` and `+0.35 GB -mtp` speculative builds with unchanged quality; eight-row BF16/GSQ-RCO/UD results table (wiki/C4/FineWeb-Edu PPL, five-task ZS average plus recovery, AIME25, GPQA-Diamond, LiveCodeBench v6) with task-lossless IQ3_S and matched-size IQ2_XS deltas; llama.cpp/`llama-mtmd-cli`, Ollama, and LM Studio recipes; per-tensor allocation dumps plus 1000×4096-token imatrix; GSQ/RCO bibtex, Verda plus ISTA Scientific Computing acknowledgement, and base-license inheritance.
