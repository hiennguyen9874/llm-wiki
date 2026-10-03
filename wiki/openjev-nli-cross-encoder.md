---
type: Concept
title: OpenJev NLI Cross-Encoder (AlexWortega)
description: Qwen3.5 NLI cross-encoder family (AlexWortega/openjev) that scores premise–hypothesis entailment for rerank, grading, and order-invariant typed decisions, with reported JevBench, faithfulness, and serving results.
tags: [open-weights, decision-models, nli, cross-encoder, jev]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T18:24:35Z }
sources:
  - id: openjev-nli-2026
    resource: ../raw/openjev/README.md
    scope: ../raw/openjev/
    kind: model-card
    title: openjev — Qwen3.5 trained as jev model
  - id: openjev-v5-2026
    resource: ../raw/openjev/RESULTS-v5.md
    scope: ../raw/openjev/
    kind: documentation
    title: openjev v5 — results
  - id: openjev-train-2026
    resource: ../raw/openjev/qwen3.5-4b-nli-v5/train_result.json
    scope: ../raw/openjev/
    kind: configuration
    title: qwen3.5-4b-nli-v5 training result
  - id: openjev-nvfp4-2026
    resource: ../raw/openjev/qwen3.5-4b-nli-v5-nvfp4/README.md
    scope: ../raw/openjev/
    kind: documentation
    title: openjev qwen3.5-4b-nli-v5 — NVFP4
  - id: openjev-serve-2026
    resource: ../raw/openjev/code/serving/README.md
    scope: ../raw/openjev/
    kind: documentation
    title: OpenJev image Decisions gateway
  - id: openjev-smoke-2026
    resource: ../raw/openjev/results/image_jevbench_examples_20260928/README.md
    scope: ../raw/openjev/
    kind: documentation
    title: Image Decisions smoke checks — 2026-09-28
---

# OpenJev NLI Cross-Encoder (AlexWortega)

Synthesis: `AlexWortega/openjev` turns Qwen3.5 into a *jev* model — one 3-way NLI cross-encoder (contradiction / entailment / neutral) over a premise–hypothesis pair whose argmax-entailment answers rerank, grading, guarding, and game moves with nothing trained per task; the v5 4B checkpoint is the recommended typed-decision build, scoring one forward pass per option and normalising entailment over the closed option set[^openjev-nli-2026].

## Identity and license

- Project `AlexWortega/openjev`, Hugging Face `AlexWortega/openjev` with subfolders `qwen3.5-4b-nli-v5`, `qwen3.5-2b-nli-v5`, `qwen3.5-0.8b-nli-v5`, plus a demo Space; card frontmatter declares MIT licence, `Qwen/Qwen3.5-4B` base, `text-classification` pipeline, `transformers` library, and `nli` / `cross-encoder` / `reranker` tags[^openjev-nli-2026].
- Name-collision warning — **synthesis**: despite the shared `openjev` name, this NLI cross-encoder family is a different project from [OpenJev Open-Weights Typed Decision Model](openjev-decision-model.md) (`openjev/openjev`, Qwen3.8-27B letter readout) and from [SemIf Open Decisions](semif-open-decisions.md) (no-training direct-logit baseline); do not merge their accuracy or serving figures[^openjev-nli-2026].
- Canonical local entry is `../raw/openjev/README.md`, package scope `../raw/openjev/`; `../raw/openjev.md` is a byte-identical duplicate of the README — **observed** by diff — so identity reconciles to the package scope, with no immutable weight revision recorded[^openjev-nli-2026].

## Mechanism (**observed** in `modeling_openjev.py`, **reported** in the card)

- `OpenJevCrossEncoder` is `Qwen3_5ForSequenceClassification`: Qwen3.5 backbone plus a linear `score` head over the last non-pad token, three labels in dleemiller order (0 contradiction, 1 entailment, 2 neutral), input `"Premise: {premise}\nHypothesis: {hypothesis}"` (template in `config.nli_template`), right-padded, trained with plain cross-entropy over the three classes[^openjev-nli-2026].
- Public surface: `predict`, `predict_hypotheses`, `rerank`, `grade`, `latents`, `latents_hypotheses`, plus `LatentMLPHead` per-task heads; `predict_hypotheses` / `latents_hypotheses` compute the shared token prefix once for three or more hypotheses, then score every continuation in one batched pass, and `rerank` reuses that rule[^openjev-nli-2026].
- Qwen3.5-specific constraint (**reported**): recurrent linear-attention layers mean a 4D packed tree mask alone would mix branches, so the shared prefix cache is copied into separate batch entries for suffixes; this path is text-only, with memory proportional to hypothesis count and length — split very large option sets[^openjev-nli-2026].
- Plain-transformers use renders `model.config.nli_template.format(premise, hypothesis)`; images travel inside the premise as `<|vision_start|><|image_pad|>…<|vision_end|>` with `pixel_values` / `image_grid_thw` from the Qwen3.5 image processor (see `code/doom_vision.py`, `code/eval_image_nli.py`)[^openjev-nli-2026].

## Typed decisions (**observed** in `code/openjev_decide.py`)

- `OpenJev.decide(state, questions)` takes JevBench-shaped `{"type": "noul"|"choice"|"score", "instructions", "options"}` and returns `{"noul": p}` or `{"probabilities": {...}}`; each option becomes one hypothesis (`The answer to "{instr}" is {label}: {crit}`), scored as P(entailment) normalised over the options — the model's own softmax, one forward pass per option, nothing generated, so option order only enters the final normalisation[^openjev-nli-2026].
- The same file is the JevBench `local_openjev` adapter (`typed_decisions/open_jev.py` on `PYTHONPATH`); long states are windowed (24,000 chars, 2,000 overlap) rather than silently cut, and `collator.max_state` reports truncation[^openjev-nli-2026].

## Checkpoints (**reported**)

| checkpoint | use |
|---|---|
| `qwen3.5-4b-nli-v5/` | recommended typed decisions; `panel_manifest.json` lists every training split |
| `qwen3.5-0.8b-nli-v2s-long/` | small 0.8B 4k-context build (v2 mixture + faithfulness / IF / false-premise + long-doc stage); serves the demo Space |
| `qwen3.5-4b-nli-v2/` | text + images build behind the Doom/Minecraft videos and radars |
| `qwen3.5-4b-nli/` | original text-only 4B |
| `qwen3.5-35b-a3b-nli/` | 35B-A3B MoE build (load with `modeling_qwen35_moe_seqcls.py`); `mlp_heads_35b/<task>/` holds frozen-latent MLP heads (`head.pt` + `norm.npz` + `meta.json`) |

- v5 training stages (**reported** in `RESULTS-v5.md`): v2 recipe (hard NLI, long docs, image premises, agentic traces, ~1.3M rows); v2s adds faithfulness / IF / false-premise data; v4 adds 27k teacher-distilled rows plus complex IF formats and value-and-format adequacy; v5 adds 5,998 gpt-5.5 computation-heavy items (temporal, long policy, multi-hop, judge); teacher self-agreement 0.921[^openjev-v5-2026].
- Training lineage (**observed** in `qwen3.5-4b-nli-v5/train_result.json`, architecture **observed** in `qwen3.5-4b-nli-v5/config.json`): v5 resumes from `ckpt/qwen3.5-4b-nli-v4`, full fine-tune (no LoRA), 1 epoch, lr 1e-5, batch 8 × grad-accum 2, `max_len` 2048, seed 42, `group_by_length`, gradient checkpointing, image processor `Qwen/Qwen3.5-4B`; final mix loss 0.283 / accuracy 0.942 and MNLI eval loss 0.710 / accuracy 0.888[^openjev-train-2026].
- Architecture snapshot (**observed**): 32 text layers (`hidden 2560`, hybrid `linear_attention`/`full_attention` every 4th layer, 16 heads / 4 KV, 262,144 max positions, vocab 248,320, bf16) plus 24-layer 1024-wide vision tower (`spatial_merge_size` 2); template `"Premise: {premise}\nHypothesis: {hypothesis}"`, labels 0 contradiction / 1 entailment / 2 neutral[^openjev-train-2026].
- 35B contrast (**observed** in `results/train_qwen3.5-35b-a3b.json`, inspected for this file only): `Qwen/Qwen3.5-35B-A3B` LoRA r16, 60k train / 2k val, `max_len` 256, bs 8 × accum 4, lr 2e-5, 1 epoch, eval loss 0.266 / accuracy 0.9065[^openjev-train-2026].

### NVFP4 quant variant (**reported**)

- `qwen3.5-4b-nli-v5-nvfp4/` is W4A4 NVFP4 (FP8 block scales, group 16) via NVIDIA Model-Optimizer 0.47 `export_hf_checkpoint` (`quant_method: modelopt`); 3-way `score` head, embeddings, vision tower and GDN `in_proj_a/b` / `conv1d` stay bf16; 3.95 GB vs 9.1 GB bf16; same template and label order[^openjev-nvfp4-2026].
- Recipe: PTQ `mtq.quantize` (`NVFP4_DEFAULT_CFG`, `score` excluded, max-calibration on 512 v5-mix rows) then QAD distillation (NVFP4 student on 30k v5-mix rows, KL teacher||student over 3 logits, teacher bf16 v5, lr 1e-5 cosine, bs 16, 1 epoch, scales frozen, ~40 min on RTX PRO 6000); plain PTQ without QAD loses up to 4 pts on hard sets (ANLI r3 0.585, ConTRoL 0.698)[^openjev-nvfp4-2026].
- Accuracy (SGLang, real FP4 kernels, RTX PRO 6000 Blackwell, same flags): MNLI 0.894 vs 0.898 bf16/fp8; ANLI r1/r2/r3 0.771/0.675/0.618 vs 0.782/0.665/0.626 bf16; WANLI 0.761 vs 0.766; SciTail 0.948 vs 0.952; ConTRoL 0.722 vs 0.735[^openjev-nvfp4-2026].
- Speed (SGLang 0.5.18, `--chunked-prefill-size 16384 --max-prefill-tokens 65536 --disable-radix-cache`, saturated random-token throughput): e.g. 1k tokens 69.0k tok/s NVFP4 vs 51.4k fp8 vs 37.5k bf16; 16k tokens 48.7k vs 39.2k vs 30.7k; single-request p50 at 4k/16k: 67/351 ms vs 86/434 ms fp8 vs 119/547 ms bf16; raw `bench/` JSON retained[^openjev-nvfp4-2026].
- Serving constraint: needs Blackwell sm100/sm120; launch with `SGLANG_EXTERNAL_MODEL_PACKAGE=sglang_openjev ... --is-embedding --json-model-override-args '{"architectures": ["Qwen3_5ForConditionalGeneration"]}' --attention-backend triton`; `modelopt_fp4` from `hf_quant_config.json`; flashinfer JIT needs matching `CUDA_HOME` nvcc (13.0 worked)[^openjev-nvfp4-2026].

## Reported accuracy (all **reported**, not reproduced here)

- JevBench v1.2 public items (231), official harness: 4B v5 reaches easy 1.000 (48), standard 0.986 (72), hard **0.622** (111), all-public **0.814**, versus 4B v4 1.000/1.000/0.541/0.779, Jev 1.13 1.000/0.986/0.730/0.866, and SemIf (Qwen3.5-4B) 1.000/0.986/0.613/0.810; the judge tier is held out so no JevBench Score is claimed[^openjev-nli-2026].
- Hard-tier families (v5): adversarial 1.00, routing_hard 1.00, trap 1.00, multi_hop 0.72, probability 0.60, long_policy 0.58, ambiguous 0.57, judge_hard 0.53, tradeoff 0.50, temporal_numeric 0.27[^openjev-nli-2026].
- `RESULTS-v5.md` adds same-231 published systems: gemini-3.1-flash-lite 0.87, open-alternative-jev 0.74, system-one-open 0.73, open-jev-deberta-v3-large 0.52; the judge tier is 28% of the Intelligence axis and unmeasured[^openjev-v5-2026].
- Faithfulness / IF / NLI holdouts: RAGTruth response AUROC **0.932**, HaluBench **0.937**, FalseQA **0.949**, BullshitBench nonsense detection **0.914**, IFEval instruction AUROC 0.934, LLMBar pairwise **0.834**, MNLI m/mm **0.896/0.899**, ANLI r1/r2/r3 **0.780/0.665/0.627**, WANLI **0.767** / SciTail **0.952** / ConTRoL **0.734**; LLM-AggreFact balanced accuracy dips 0.765 (v4) → 0.754 (v5), and BullshitBench judge-vs-consensus drops 0.885 → 0.862 (2B v4 peaks 0.976); scale anchors Bespoke-MiniCheck-7B 0.774 and MiniCheck-FT5 ~0.75[^openjev-nli-2026].
- Nonsense detection is a capability the compared cross-encoders lack: openjev 4B v2 scores 0.181 and ModernCE-large 0.168, below chance, because they read nonsense questions as sensible[^openjev-nli-2026].
- Financial arithmetic (`code/eval_fincalc.py`, FinCalc-NLI 4,000-item test): 4B v5 63.2%, 4B v2 58.2%, 0.8B v2s-long 50.5%, original 4B 31.9%[^openjev-nli-2026].
- Agentic / multimodal (**reported**, zero-shot): Doom from pixels 10.4 kills/episode (v1 5.2, random 1); Doom from text state 11 kills (perfect-info bot 18.8); Minecraft iron pickaxe from nothing in 11 milestones / ~22 decisions via a backward-chaining scaffold where the model only checks inventory/world statements; v2 gains on adversarial NLI (ANLI r3 0.42→0.63, WANLI 0.63→0.77), image claims (0.52→0.84), ARC-Challenge rerank (0.59→0.72), MMLU (0.47→0.53), MNLI flat at 0.91[^openjev-nli-2026].

## Determinism and order invariance (**reported**)

- All 231 public JevBench items asked four times (same order twice, reversed, shuffled): 0/231 label changes in every condition; largest probability shift 0.0 bit-identical on repeat, 1.8e-7 reversed, 1.2e-7 shuffled — structural (independent per-option forward passes), not trained; `RESULTS-v5.md` notes fp32-on-V100 measurement and ~1e-3 bf16 rounding with still no flips[^openjev-nli-2026][^openjev-v5-2026].

## Weaknesses and trust limits (measured, not guessed)

- Contamination warning (**reported**): v5 deliberately includes TRAIN *and* TEST splits of MMLU, ARC-Easy/Challenge, GSM8K, HellaSwag, WinoGrande, GPQA-diamond, CLINC-150, Banking77, ESCI (exact list in `panel_manifest.json`), so benchmark numbers on those sets are meaningless and unreported; earlier strict-zero-shot claims do not carry to v5; no JevBench item and nothing from the faithfulness/IF/judge tables was ever in the mixture (`data_mix.py` refuses JevBench by name; `jevfmt --no-jevbench`)[^openjev-nli-2026][^openjev-v5-2026].
- Shell-command safety review (`code/eval_security.py`, 195 generated commands, generator-assigned gold): 0.600 accuracy, catches only 37% of deny-worthy commands — never trained for this[^openjev-nli-2026].
- Prompt injection: one adversarial state line drops 150-item JevBench accuracy 0.833→0.467 and lifts deny-worthy allowed share 17%→85%; the full injection table (pre-approval note 0.415/0.853 allowed, fake policy 0.436/0.760, fake admin override 0.456/0.733, threat 0.564/0.373, fake tool output 0.523/0.240) plus cited Jev audits (Octomind P(block) 0.76→0.48; `jagged` 96.5%→26.5%) mean a guard on this model belongs next to deterministic checks, not instead of them[^openjev-nli-2026][^openjev-v5-2026].
- WebQL null detection (1,200 pages): 0.8B v2s 0.826 and 4B v2 0.831 ROC AUC versus Jev 1.13 0.983; v5 unmeasured[^openjev-v5-2026].

## Serving (**reported**)

- SGLang external package (`code/sglang_openjev/`) adds the `score` head to `Qwen3_5ForConditionalGeneration` (hybrid cache, mrope, vision tower unchanged); text and images work; `/classify` returns three raw logits; launch via `serve_sglang.sh` (tested sglang 0.5.19) or `SGLANG_EXTERNAL_MODEL_PACKAGE=sglang_openjev` with `code/` on `PYTHONPATH`; client `code/sglang_client.py`[^openjev-nli-2026].
- Same predictions as transformers at 1.5–3.1× throughput on one shared RTX A6000 (lower bound): e.g. MNLI 2.1×, ANLI r3 2.3×, ConTRoL-long 3.1×, SciTail 1.5×; full 9-row bench table in the card[^openjev-nli-2026].
- Image-decisions update 2026-09-28: the SGLang image gateway accepts image bytes and returns option probabilities via `/v1/systemone` under rule `normalized_entailment_v1` (entailment normalised over options, no benchmark-fitted calibration); weights unchanged; explicitly not a new full Image JevBench score — a full-corpus rerun is required for the leaderboard[^openjev-nli-2026][^openjev-serve-2026][^openjev-smoke-2026].

### Image gateway operations (**observed** in `code/serving/decisions_server.py` and `prompt_templates.py`, **reported** in `code/serving/README.md` and `IMAGE-SERVING.md`)

- Stack: pinned SGLang V100 fork plus `decisions_server.py` FastAPI gateway speaking `POST /api/alpha/decisions`, `/api/v1/systemone`, `/v1/systemone` with `GET /health` 503 until SGLang ready; env `SGLANG_URL`, `API_KEY` (unset = no auth, local only), `SERVED_MODEL`, `PRICE_PER_MTOK` (default 0), `MAX_INFLIGHT` (default 64), `CLASSIFY_BS` (default 32); Bearer check via `hmac.compare_digest`; 8 MiB request cap; template `Premise/Hypothesis` must match training[^openjev-serve-2026].
- Batching and usage: one `/classify` call per `CLASSIFY_BS` pairs, concurrent; image options dispatched in batches of at most 4 bounded by encoded size; usage `input_tokens` from SGLang `meta_info.prompt_tokens` or `chars//4` fallback, `output_tokens` 0, `cost = tokens*PRICE_PER_MTOK/1e6`; response declares `probability_method: normalized_entailment_v1`, `provider: openjev`[^openjev-serve-2026].
- Prompt styles (`prompt_templates.py::STYLES`): production default `trained`; `unquoted` and `direct_noul` are explicit alternatives; `direct_noul` scores the bare assertion with `P(true)=max entailment`, neutral mass outside `P(true)`, no gold-derived temperature or calibration[^openjev-serve-2026].
- Image transport: one image per request shared by all questions/options; JPEG/PNG/WebP base64 or data URI; 4 MiB decoded, 12 M pixels, 8 MiB total; no URL fetch or server-path read; `<<IMG>>` optional (appended when absent); pixels go to the vision tower, not a captioning model; `p_i = e_i/sum(e)` with uniform fallback; `confidence` is normalized entropy, not the ECE top probability; no temperature fitted on benchmark examples[^openjev-serve-2026].
- JevBench adapter: patch `fstandhartinger/jevbench@fd54ea7...` adds `--adapter openjev_image`; canonical state `{text:"An image: <<IMG>>", image_data:"<base64>"}` keeps the existing dataset hash covering image bytes; gold/`correctLabel`/`alt`/titles never sent; scoring, ledger, Brier/ECE unchanged[^openjev-serve-2026].
- Operations: systemd restart/watchdog/socket activation over two replicas; `OPENJEV_VISION_WARMUP=1` warms vision at two resolutions (batches 1 and 4) before readiness; `OPENJEV_READY_DIR` per-port markers gate routing; worker watchdog probes real text classification plus finite image logits; new token lengths can still trigger V100 JIT (image cold latency seconds, warm numbers are not cold SLAs); revert via `app/backups/pre-image-20260928/`[^openjev-serve-2026].
- Pinned serving revision (**reported**): weights `AlexWortega/openjev` rev `a298f274886c4676c42f1a4262401b6aa9653e6d` (`qwen3.5-4b-nli-v5/*`), overlay adds missing processor configs from pinned `Qwen/Qwen3.5-4B` with hash checks; listeners 31000 (4B v5) and 31001 (0.8B v6)[^openjev-serve-2026].

### V100 recipe and agreement (**reported** in `code/serving/V100.md`, not reproduced)

- Isolated runtime: `haohervchb/sglang-V100@dca4889...`, FlashInfer `c3c40a7...` + `sm70` patch, PyTorch 2.9.1 cu126 + private CUDA 12.6.3 (official cu128 omits SM70), FP16, TileLang V100 attention + GDN prefill, 8192-token server context (benchmark truncates at 4096), disabled CUDA graphs, `SGLANG_V100_DYNAMIC_PAGED=1` runtime-dims paged kernel (math/tiling unchanged), LPM scheduling with 16 running requests, `extra_buffer` prefix cache with Mamba-to-KV ratio 3 (503 recurrent slots + 135,008 KV tokens at 80% budget vs 317 slots at 0.9 with eviction)[^openjev-serve-2026].
- Verified agreement 2026-09-26 (eva01, V100-SXM2-32GB, FP16, `/classify`, batches of 32 × 4 workers, median of 3 after warmup): all 867 NLI argmax labels agree with Transformers FP16 reference; max entailment diff 0.012851; among 291 same-premise/instruction groups (793 rows) no strict winner change (2 cold-cache exact ties); first-use JIT 202.7 s excluded from medians (additional JIT outliers retained); controlled throughput, not production p99[^openjev-serve-2026].
- Throughput medians: G 303 pairs 24.928 s uncached / 13.417 s cleared / 2.697 s warm; T 564 pairs 47.618 / 29.635 / 4.732 s; fresh-set cache gain 1.86x/1.61x, repeated-set 9.24x/10.06x; Mamba ratio 0.9→3 cut warm larger-set median 28.801→4.732 s; Sept-27 tuning attempt contaminated by concurrent v6 jobs (warm G 6.28–7.30 s vs prior 2.70 s, only 192 slots) and must not rank configs[^openjev-serve-2026].

### Image smoke checks, 8 examples (**reported**, not a benchmark)

- Scope: eight published resized website examples only, not the full 228-public / 456-sealed Image JevBench; no score, rank, or fitted calibration claimed; public 4B v5 weights available, 0.8B v6 row is a local unpublished checkpoint[^openjev-smoke-2026].
- Through production SGLang V100 FP16 gateways + patched JevBench CLI, unchanged scoring: 4B v5 7/8 correct, 8/8 valid, ECE 0.11135 (10 bins), Brier 0.208879, p50 0.678 s / p95 6.864 s; 0.8B v6 6/8, 8/8 valid, ECE 0.3669, Brier 0.4129, p50 0.427 s / p95 0.796 s; latencies include possible first-use compilation, not throughput; cost unmeasured (zero ledger ≠ free)[^openjev-smoke-2026].
- Validation: 16/16 strict distribution checks, raw-response hashes verified, 39 local gateway/API/proxy + 17 JevBench protocol tests passing; SGLang vs Transformers multimodal agreement on 2 image NLI pairs (both argmaxes, max diff 0.000092583); pixel control (parcel/receipt bytes only) flips the answer on both models; leaderboard update requires maintainer rerun[^openjev-smoke-2026].

## Relationships

- Uses [Jev API Patterns](jev-api-patterns.md) `noul` / `choice` / `score` shapes through the `openjev_decide.py` adapter, but the underlying mechanism is NLI entailment scoring, not letter-readout or joint-schema heads[^openjev-nli-2026].
- Informs [Classifier Selection](classifier-selection.md) as a small open-weights NLI rerank/judge option with explicit injection and shell-review limits[^openjev-nli-2026].
- Requires [Classifier Calibration](classifier-calibration.md) context: v5 probabilities are raw entailment softmaxes with no fitted calibration reported, unlike fixed-temperature letter-readout builds[^openjev-nli-2026].
- Contrasts with [OpenJev Open-Weights Typed Decision Model](openjev-decision-model.md): different `openjev` project, backbone (Qwen3.5 here vs Qwen3.8-27B), and readout (NLI entailment vs letter log-prob); do not merge figures[^openjev-nli-2026].
- Contrasts with [OpenJev-SGLang Decision Serving](openjev-sglang-decision-serving.md): different base model and serving stack (Qwen3.6-35B-A3B N+1 readout there vs Qwen3.5 cross-encoder `/classify` here)[^openjev-nli-2026].
- Informs [Jev Decision Model](jev-decision-model.md) as a near-hosted open comparator on JevBench public items (0.814 vs 0.866) with a stated contamination boundary[^openjev-v5-2026].

## Coverage limits

- Inspected by static read: `README.md`, `RESULTS-v5.md`, `modeling_openjev.py`, `code/openjev_decide.py`, `qwen3.5-4b-nli-v5/train_result.json` + `config.json` (+ `results/train_qwen3.5-35b-a3b.json` for the 35B contrast), `qwen3.5-4b-nli-v5-nvfp4/README.md` (+ `bench/` filenames only), `code/serving/README.md`, `IMAGE-SERVING.md`, `V100.md`, `decisions_server.py`, `prompt_templates.py`, and `results/image_jevbench_examples_20260928/README.md`; no code was executed and no benchmark, serving run, or video was reproduced[^openjev-nli-2026][^openjev-v5-2026][^openjev-train-2026][^openjev-nvfp4-2026][^openjev-serve-2026][^openjev-smoke-2026].
- Excluded with reason: weight shards / safetensors, `tokenizer.json` / processor configs (beyond hash-checked overlay mention), `panel_manifest.json` contents beyond the panel list, `mlp_heads_35b/*.pt/*.npz` (binary; one `meta.json` sample only), `videos/` (Git LFS pointers, unavailable locally), `assets/*.png` radars (not pixel-inspected), bulk `results/*.json` run files and `results/v2/` (generated, uninspected beyond `summary.md` spot check and smoke summaries), and most of `code/` (trainer `train.py`, `data_mix.py`, `distill_teacher.py`, `hard_gen.py`, eval harnesses beyond reported tables, Doom/Minecraft/Flappy/bot/radar/SGLang client/bench, `code/serving/` checks/proxies/patches beyond the gateway/V100/image docs, `test_shared_prefix.py`) plus all Hugging Face, demo-Space, and eva01 (`~/storage/...`, `results_v100/`, systemd units) remotes — uninspected and potentially material[^openjev-nli-2026].
- All accuracy, latency, speedup, and agent figures are **reported** project measurements under stated harnesses; changing flags, dtype, or temperature voids them; v5 numbers on panel benchmarks are meaningless by the author's own contamination statement[^openjev-v5-2026].
- MIT licence stated in card frontmatter; upstream teacher/compute provenance (gpt-5.5 items, reasoning teacher) is **reported** without independent verification[^openjev-v5-2026].

[^openjev-nli-2026]: AlexWortega openjev project, "openjev — Qwen3.5 trained as jev model," canonical local entry `../raw/openjev/README.md`, package scope `../raw/openjev/` (duplicate `../raw/openjev.md` verified identical by diff). Locators: checkpoints (v5) links; jev-model definition; "openjev-4B v5: typed decisions" JevBench table, hard-tier families, judging/faithfulness table, scale/nonsense paragraph, order-invariance table, shell/injection weakness, train-on-test panel paragraph, `RESULTS-v5.md` link, `decide` example; "openjev-4B v2" Doom/Minecraft/radar paragraphs; "What's inside" checkpoint/modeling/code/`eval_fincalc`/videos/results list; "Use it" `OpenJevCrossEncoder`/prefix-cache/transformers/image paragraphs; "Serve it with SGLang" package/`/classify`/script/client/bench table; "Image Decisions serving update (2026-09-28)" rule and doc links.
[^openjev-v5-2026]: AlexWortega openjev project, "openjev v5 — results," canonical local entry `../raw/openjev/RESULTS-v5.md`, package scope `../raw/openjev/`. Locators: one-pass-per-option definition; "What went into v5" stage table and teacher agreement; "Contamination, stated plainly" panel list, meaningless-numbers rule, JevBench exclusion (`data_mix.py`, `jevfmt --no-jevbench`); "JevBench v1.2" table, hard families, published-systems line, judge-tier note; "Faithfulness" table and scale/BullshitBench paragraphs; "Determinism" table and fp32/bf16 note; "Where it is weak" shell/injection/WebQL paragraphs and audit citations; "Reproducing" snippet and `code/` file list.
[^openjev-train-2026]: Training lineage, canonical local entry `../raw/openjev/qwen3.5-4b-nli-v5/train_result.json`, package scope `../raw/openjev/`. Locators: `args` (resume `ckpt/qwen3.5-4b-nli-v4`, full FT `lora:false`, 1 epoch, lr 1e-5, bs 8 × accum 2, `max_len` 2048, seed 42, `group_by_length`, `grad_ckpt`, image processor) and `final_eval` (mix loss/accuracy, MNLI loss/accuracy); supporting `qwen3.5-4b-nli-v5/config.json` (32 layers, hidden 2560, hybrid attention, 16/4 heads, 262144 positions, vocab 248320, bf16, 24-layer vision, template, 0/1/2 labels) and `results/train_qwen3.5-35b-a3b.json` (35B-A3B LoRA r16, 60k/2k, max_len 256, eval loss/accuracy).
[^openjev-nvfp4-2026]: NVFP4 variant, canonical local entry `../raw/openjev/qwen3.5-4b-nli-v5-nvfp4/README.md`, package scope `../raw/openjev/`. Locators: NVFP4 size/template paragraph; "How it was made" PTQ+QAD steps and plain-PTQ loss; "Accuracy" bf16/fp8/NVFP4 table; "Speed" SGLang 0.5.18 throughput and p50 table plus `bench/` note; "Serving" Blackwell/SGLang/`hf_quant_config.json`/CUDA_HOME paragraph.
[^openjev-serve-2026]: Image gateway serving package, canonical local entry `../raw/openjev/code/serving/README.md`, package scope `../raw/openjev/`. Locators: README Setup/Request/Probabilities sections (revision `a298f27...`, overlay, `serve_sglang_v100.sh`, uvicorn gateway, `image_data` limits, `p_i=e_i/sum(e)`, `normalized_entailment_v1`, adapter patch, `warmup_vision.py`); `IMAGE-SERVING.md` (listeners 31000/31001, one-image rule, MIME/size caps, `<<IMG>>`, batch ≤4, entropy confidence, JevBench CLI example, systemd/`OPENJEV_VISION_WARMUP`/`OPENJEV_READY_DIR`/watchdog/backup); `V100.md` (runtime revisions, cu126/SM70, FP16/TileLang/GDN/8192 context, dynamic-paged patch, Mamba ratio 3, 2026-09-26 G/T medians and agreement audit, 2026-09-27 contamination); `decisions_server.py::SGLANG_URL/API_KEY/SERVED_MODEL/PRICE_PER_MTOK/MAX_INFLIGHT/CLASSIFY_BS/TEMPLATE/classify/authorized/health/decisions` and `prompt_templates.py::STYLES/build_prompt_plan/finish_answers`.
[^openjev-smoke-2026]: Smoke checks, canonical local entry `../raw/openjev/results/image_jevbench_examples_20260928/README.md`, package scope `../raw/openjev/`. Locators: 8-example scope paragraph; 4B-v5 vs 0.8B-v6 Correct/Valid/ECE/Brier/p50/p95 table and gateway/CLI/cost notes; Validation paragraph (16/16 checks, hashes, 39+17 tests, 2-pair parity max diff, pixel control, maintainer-rerun rule).
