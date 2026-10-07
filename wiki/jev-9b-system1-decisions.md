---
type: Concept
title: JEV-9B System 1 Decisions and Blocks-of-Experts Serving
description: autotrust/JEV-9B distills TypeSafe Jev 1.13 into calibrated noul/choice/score decisions on a frozen Qwen3.5-9B via Blocks of Experts, with reported KL fidelity, speed, JEV-27B comparison, zero-shot vision control, and vLLM serving details.
tags: [jev, decision-models, distillation, calibration, vllm, system-one, vision, multimodal]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-07T18:00:00Z }
sources:
  - id: jev-9b-v08
    resource: ../raw/JEV-9B/README.md
    scope: ../raw/JEV-9B/
    kind: model-card
    title: autotrust/JEV-9B
  - id: jev-9b-2026-10-03
    resource: ../raw/JEV-9B.md
    kind: model-card
    title: autotrust/JEV-9B \u2014 3 October 2026 update
---

# JEV-9B System 1 Decisions and Blocks-of-Experts Serving

Synthesis: `autotrust/JEV-9B` is AutoTrust's first integrated System 1 + System 2 open model — a frozen Qwen3.5-9B backbone plus a 40.2 M trained System 1 block that reproduces TypeSafe Jev 1.13 output distributions at mean KL ≈0.019 with fitted temperatures ≈1.00 and ECE 0.0007 — served per request from one vLLM engine as calibrated `noul` / `choice` (2–16) / `score` probabilities, with **reported** speed and benchmark parity, **reported** 3-October-2026 zero-shot vision decisions for robot-arm and computer-use control, and **observed** adapter, bias-plus-temperature, and routing mechanics[^jev-9b-v08][^jev-9b-2026-10-03].

## Identity and provenance

- Package `../raw/JEV-9B/` with canonical entry `README.md`; upstream `https://huggingface.co/autotrust/JEV-9B`; released checkpoint v0.8.0 (4,750 steps ≈0.93 epoch ≈608 k rows); no commit hash captured locally so identity is the package scope plus version[^jev-9b-v08].
- Creator AutoTrust AI, independent student of TypeSafe Jev 1.13; explicitly not affiliated with, endorsed by, or sharing weights/code with TypeSafe AI[^jev-9b-v08].
- Base `Qwen/Qwen3.5-9B` text tower only (vision tower and MTP head dropped), bf16, frozen and bit-identical; license Apache-2.0 for weights and `SargeDev/jev-distill-corpus-v3` corpus, with `openjev_v2` stream additionally CC0[^jev-9b-v08].
- Corpus 740,957 rows (`train` 655,806): `yuri_v3` 498,010 rows TypeSafe Jev 1.13 full distributions via OpenRouter, `openjev_v2` 94,801 rows Open-Jev programmatic labels, `yuri_v1` 148,154 rows placeholder labels down-weighted ×0.05 and excluded from temperature fitting[^jev-9b-v08].
- Held-out `test_set_30k` 29,955 rows: 25,376 Jev-labelled `yuri_v3`, 2,319 Open-Jev ground-truth `openjev_v2`, 2,260 placeholder `yuri_v1`; OOD split 13,058 Open-Jev rows from unseen task families with programmatic labels[^jev-9b-v08].

## Blocks-of-Experts recipe — observed

- Backbone 7.9 B + System 2 block = original `lm_head` (248,320×4096) untrained + System 1 block = LoRA r=16 α=32 dropout 0.05 on 10 projection types (40.1 M, shipped unmerged in `adapter/`) plus 24-slot fp32 decision head 98 k; total trained 40.2 M (0.5% of backbone), ≈3 B200-hours[^jev-9b-v08].
- **Observed** configs: `adapter/adapter_config.json` r=16; `adapter_vllm/adapter_config.json` same adapter zero-padded to r=32 with `lm_head` in targets; `judge_config.json` `bare-v1`, hidden 4096, slots `noul` 0–2 / `score` 2–8 / `choice` 8–24, verbalizers `false/true`, `0`–`5`, `A`–`P`, token ids 3721/1802/15–20/32–47, `weights_mode: unmerged`; `adapter_vllm/decision_head.json` holds 24-bias plus verbalizer ids with note `logprobs + bias, / temperature`; `calibration.json` per-kind `noul` 1.0022 (n=4363) / `choice` 0.9840 (n=3418) / `score` 1.0122 (n=3173)[^jev-9b-v08].
- Template is one string `[kind]/[state]/[question]/[options]/[decision]:`; last-token final-norm state goes through linear fp32 head `H→24`, inactive slots masked, per-kind temperature applied, softmax aligned with caller `options`; one prefill pass, no decoding[^jev-9b-v08].
- Head initialised from backbone `lm_head` rows so step-0 output equals pretrained zero-shot restricted distribution (**observed** gate |Δp| 8.6e-07 < 1e-5 in card); before any label it already gives 53% `choice` agreement and `noul` AUROC 0.82, distillation takes it to 90% / 0.996[^jev-9b-v08].
- Loss KL(target‖model) over active slots + 0.5·RPS for `score`; 30% `choice` option-permutation augmentation; 128 rows/step kind-stratified (≥1/6 per primitive), length-bucketed, 24 k-token micro-batch cap, gradient checkpointing; AdamW fused β=(0.9,0.98), head lr 2e-4 / LoRA 1e-4, cosine with warmup 3% and clip 1.0 for 2,500 steps, then continued on the unseen remainder with fresh AdamW state (warmup 2%, lr ×0.9→cosine) for 2,250 more steps to lr ≈×0.07 — 4,750 steps ≈0.93 epoch total[^jev-9b-v08].
- Training trajectory **reported**: fixed-subset val KL 0.094 at 64 k rows → 0.019 at 608 k (`test_set_30k` KL 0.081→0.0210); untrained baseline KL 0.510, choice top-1 0.532, `noul` AUROC 0.824, score MAE 1.130, ECE 0.094; annealing mattered twice (v0.7.0 500-step cool-down −25% KL; v0.8.0 continuation −24% and +1.4 pts choice agreement)[^jev-9b-v08].
- Why separate blocks: folding the System 1 LoRA into the backbone scored 61.6% HumanEval vs 70.7% base (−9 pts, perplexity 3.15→3.30); keeping the backbone pristine removes the trade-off; decision serving merges in memory at start-up so latency matches a merged bundle[^jev-9b-v08].

## System 1 fidelity — reported

- Mean KL(Jev‖model) on 25,376 Jev-labelled rows ≈0.019 nats (≈54 sampled decisions per nat); all-target KL 0.0210; by slice `noul` 0.005 (n=8,537, ≈200/nat), `choice` 0.028 (n=8,312, ≈36/nat), `score` 0.023 (n=8,527, ≈43/nat)[^jev-9b-v08].
- `test_set_30k` with temperature: `noul` AUROC 0.996 (0.994 Jev-labelled), Brier 0.0015 vs target probability, choice top-1 0.898–0.902 (0.954 on teacher-decisive rows gap ≥0.1, near chance where gap <0.05 because teacher median top-1 is 0.70; student captures 97.7% of achievable mass 0.693 vs 0.709), score MAE 0.103, RPS 0.0085, ECE 0.0007, fitted T 1.002/0.984/1.012 (no post-hoc correction needed)[^jev-9b-v08].
- Release acceptance in `reports/eval_v08_bundle.md`: choice top-1 0.8975 misses the ≥0.9 gate while AUROC, Brier, MAE, KL, and ECE pass[^jev-9b-v08].
- Order robustness: top-1 flip under shuffle 3.9% (vs 38% before distillation), mean max |Δp| 0.024, p90 0.055 on 1,000 rows ×4 permutations[^jev-9b-v08].
- OOD unseen families vs programmatic truth: KL 0.234, top-1 0.918, `noul` AUROC 0.989; `choice` KL 0.351 / top-1 0.837 with game-state decisions hardest; in-distribution Open-Jev `choice` KL 0.176[^jev-9b-v08].
- Fidelity includes mistakes: poker shove 0.70 vs teacher 0.62 where a solver checks 100%, and 11.5% of 16-option answers flip on order alone vs 7.0% for the teacher (JEV-27B 7.4%)[^jev-9b-v08].

## Speed vs hosted API — reported with limits

- One B200 single-decision median ≈90 ms (87 ms) vs hosted Jev 238 ms mean (29,600 calls, pressure author) and 291–301 ms median on three workloads (Open-Jev); throughput on pressure set ≈340/s (14,400 in 42 s) vs 23/s against hosted API (≈15×); batched 128/batch 2.5 ms/decision (≈400/s)[^jev-9b-v08].
- Offline batch 29,955 test questions: 75 s PyTorch (398/s) vs 80 s vLLM (374/s) — at 9 B vLLM mainly buys serving, not batch speed; System 2 generation 164 HumanEval in 165 s PyTorch vs 3.3 s vLLM (≈50×); HTTP 150/205 req/s at 64/256 clients; vLLM fidelity matches PyTorch (KL 0.0211, mean |Δp| 0.0008)[^jev-9b-v08].
- Prefix caching: Gated-DeltaNet+attention mixes cache in 528-token blocks so only >528-token shared prefixes reuse; template puts `[kind]` before `[state]` so only same-kind questions share; measured 293 states×7.7 questions (≈480-token states) served 19.6% tokens from cache (+14–20% throughput) with identical outputs[^jev-9b-v08].
- Read with caveats: local timings exclude network/TLS/queueing, hosted include them and depend on concurrency/rate limits; Jev latency ≈flat in questions/request so bundling narrows gap; local figures self-reported while hosted are third-party; call sets not identical above 16 options[^jev-9b-v08].
- System 2 no-degradation **reported**: HumanEval greedy 70.7% (116/164) with all 164 completions byte-identical to base[^jev-9b-v08].

## Benchmarks and JEV-9B vs JEV-27B — reported

- Same recipe/code/hyper-parameters/API/packaging as JEV-27B; only backbone (Qwen3.5-9B→Qwen3.8-27B) and memory changed; same held-out set and independent benchmark; 9B weights 18 GB vs 54 GB[^jev-9b-v08].
- 27B lowers KL to Jev ≈0.019→≈0.017 (−11%), OOD KL 0.234→0.104 (−56%), OOD top-1 0.918→0.942, choice agreement 90.2%→90.5%, score MAE 0.103→0.098, shuffle flips 3.9%→2.9%, AUROC 0.994→0.995, ECE 0.0007→0.0009 (both <0.001)[^jev-9b-v08].
- Pressure detail (same items to 16-option limit, orderings seeded differently so compare aggregates): 2/4/8/16-option 0.868/0.774/0.735/0.694 vs teacher 0.890/0.801/0.782/0.769 (97%/97%/94%/90%); 16-option CLINC/DBpedia/GoEmotions/MTOP 0.875/0.855/0.325/0.720; near-miss vs unrelated 0.875 vs 0.975 (teacher 0.912 vs 0.985); shuffle-only changes 11.5% vs 7.0%; 14,400 decisions 42 s vs 110 s (2.6× faster)[^jev-9b-v08].
- Open-reproduction context: only JEV models publish distribution-level KL, with 9B second after 27B; on the pressure set 9B is level with the best other models measured there (Laya and DeBERTa-v3-large zero-shot also 90% at 16 options; JEV rows are AutoTrust re-runs, others run by the benchmark author); not yet on Decision Index or JevBench, so do not claim closest by every measure; distinct from unrelated `denis-pplx/autojev-27b`[^jev-9b-v08].
- Fresh HN/V2EX illustrations (hand-written expected answers, not a benchmark; inputs from public APIs 25 Sep 2026; per-example outputs in `reports/realworld_9b.json`): 19 HN stories topic + AI-about 38/38, 12 heated comments 22/24, 10 Chinese V2EX posts 18/19, community code-rule/injection/routing/phishing/diff/urgency 14/15; misses are a branded-range-checked-int TypeScript port (0.33; 27B 0.93), CEO wire-fraud at 0.56 (27B 0.84), a comment-intent misread (0.66), and a Chinese paid-tool post at 0.44 (27B 0.77); counting, dates, and an injected instruction were handled on handful-only evidence[^jev-9b-v08].
- **Synthesis**: pick 9B for routing/moderation/short lists at 2.6× speed with a third of the weight memory; pick 27B for >8 options, unfamiliar families, code-rule/fraud checks, or when System 2 matters (HumanEval 70.7%→78.0%)[^jev-9b-v08].

## Vision: zero-shot images, robot arm and computer use — reported 3 October 2026 update

- Every step is one System 1 decision: camera image or screenshot in, a probability for every action out, in a single forward pass (about 0.2 s on one GPU); run with `bash vl/serve.sh`[^jev-9b-2026-10-03].
- Robot-arm pick and place from a top camera image (MuJoCo simulation): at each step System 1 answers two questions — is the target left or right of the gripper, above or below it — and the arm moves accordingly, halving its step whenever an answer flips; it grasps the cube, carries it, and drops it in the tray[^jev-9b-2026-10-03].
- **Reported** result: 10 of 20 random scenes completed (50%); every cube grasped ended in the tray and every miss was a grasp 3–5 cm off target; about 165 ms per decision; asking it to choose one of 8 motor commands directly did not work — a fast visual judge, not an end-to-end controller[^jev-9b-2026-10-03].
- Computer use on a real browser (headless Chromium): every clickable element gets a numbered box; System 1 picks the next click (or "the task is complete"), the browser clicks it, and the loop repeats[^jev-9b-2026-10-03].
- **Reported** result: 95% of 60 random multi-step tasks completed (shop, settings, mail; 3–7 clicks each), about 0.2 s per click; colour swatches and switches carry no text, so those clicks are decided from the screenshot alone; with numbered boxes only (no element text) 37% completed; failures skipped a step (the colour) and then checked out an empty cart[^jev-9b-2026-10-03].
- Image judging, briefly **reported**: VL-RewardBench 74.3%, AgentRewardBench AUROC 0.91, zero-shot short-video recommendation from covers AUC 0.72; code in `vl/demos/`, details in `reports/vl/`[^jev-9b-2026-10-03].
- How vision serving works **reported**: language weights are bit-identical to Qwen3.5-9B, so `vl/serve.sh` serves the unmodified multimodal Qwen3.5-9B (with its vision encoder) with the System 1 adapter (`vl/adapter_vllm`, the same weights with layer names moved); text decisions match the text-only model (300 test decisions: largest probability difference 0.011); System 2 also reads images; keep `--max-num-seqs 8`; decisions over images are zero-shot[^jev-9b-2026-10-03].
- Images quick start (**observed** interface, unexecuted): `hf download autotrust/JEV-9B --include "vl/*"` then `bash vl/serve.sh` serving both systems on `:8000`; `POST /v1/decide` takes `kind`/`question`/`options` plus `state` as a text-plus-image list with `{"image": "data:image/png;base64,..."}` entries[^jev-9b-2026-10-03].

## Serving mechanics — observed

- One vLLM engine serves both systems from pristine weights: base `lm_head` for System 2, LoRA module `jev-decision` (`adapter_vllm/`) for System 1; decision is single prefill `max_tokens=1` constrained to option tokens via `allowed_token_ids` read as log-probs, then + head `bias` / per-kind T from `calibration.json` client-side (the log-softmax normaliser cancels, so the result is exactly the calibrated head distribution)[^jev-9b-v08].
- Canonical flags `--enable-lora --max-lora-rank 32 --lora-modules jev-decision=adapter_vllm --logprobs-mode processed_logprobs --max-model-len 4096` (raise to 16384 for long thinking); `processed_logprobs` is required so log-probs respect `allowed_token_ids`; add `--enable-prefix-caching --mamba-cache-mode align` for many-questions-per-state; needs a September-2026 vLLM dev build (Qwen3.5 support, `lm_head` LoRA, `logprobs-mode`, `allowed_token_ids`), start-up 3–8 min with CUDA-graph+LoRA[^jev-9b-v08].
- Values can differ in the third decimal between runs (bf16 plus batch-dependent batching)[^jev-9b-v08].
- Offline Python path **observed** in card: `LLM(..., enable_lora=True, max_lora_rank=32, logprobs_mode=..., max_model_len=4096)` + per-request `LoRARequest` (`None` System 2, `decision` System 1, mixed batches allowed); plain `transformers`+`peft` path must `merge_and_unload` for speed but then breaks System 2 unless run under `disable_adapter()`[^jev-9b-v08].
- `options` are validated: `noul` must be `["false","true"]`, `score` must be `["0".."5"]`, `choice` takes 2–16 free-text options; inputs longer than 1,024 tokens are truncated (state only, head 60% / tail 40%) unless the limit is raised[^jev-9b-v08].
- Confidence-gated escalation (System 1 first, System 2 thinking on low confidence) is a usage pattern, not a benchmarked configuration — validate the threshold locally and serve with a `--max-model-len` large enough for the reasoning budget[^jev-9b-v08].

## Relationships

- Preceded by nothing in this repo; succeeded by [JEV-27B System 1 Decisions and Blocks-of-Experts Serving](jev-27b-system1-decisions.md) using the same recipe on a larger backbone.
- Extends [Jev Decision Model](jev-decision-model.md) with the fast open student by KL and head-to-head pressure results.
- Extends [Jev API Patterns](jev-api-patterns.md) hosted shapes with local completions-plus-`allowed_token_ids` and the 2–16-option `transformers` path.
- Uses [Classifier Calibration](classifier-calibration.md) per-kind temperatures near 1.00 and ECE limits.
- Uses [System One Models](system-one-models.md) System 1 vs System 2 framing for the two-block serving.
- Informs [Classifier Selection](classifier-selection.md) open-clone choice and 9B-vs-27B routing.
- Compared with [Jev-27B-VL Vision-Capable System 1 Decisions and Serving](jev-27b-vl-multimodal-decisions.md) on the same robot-arm scenes and computer-use tasks: JEV-9B 50% vs 75% grasp success, both 95% computer-use with boxes plus text, 37% vs 10% boxes-only, about 165 ms vs 239 ms per robot-arm decision; demo lineage is JEV-9B `vl/demos/`[^jev-9b-2026-10-03].

## Coverage limits

- Inspected `README.md` (full), `config.json`, `calibration.json`, `judge_config.json`, `adapter/adapter_config.json`, `adapter_vllm/adapter_config.json`, `adapter_vllm/decision_head.json`, `tokenizer_config.json`, `chat_template.jinja` header, `model.safetensors.index.json` metadata, and report samples `eval_v08_bundle.md`, `eval_s2_9b.md`, and `data_audit.md` by static reading; no server execution, API calls, or benchmark reproduction, so performance numbers are **reported** while interfaces and configs are **observed**.
- Inspected `adapter/README.md` only to exclude it as an unfilled PEFT template (`[More Information Needed]`).
- Additionally inspected `../raw/JEV-9B.md` statically (frontmatter tags plus "New (3 October 2026)" vision section, "Images: quick start," and updated `Files` listing); `vl/`, `videos/`, and `reports/vl/` contents and the three demo videos are remote and were not inspected or executed, so robot-arm (20 scenes), computer-use (60 tasks), and image-judge figures are **reported** with small-sample limits.
- Excluded with reason: per-problem `humaneval_*.json`, per-example `realworld_*.json` beyond card aggregates, `vllm_*.json` and `fanout_*.json` beyond card aggregates, remaining `eval_s2_*.md`, `b0/m0_*.md`, and `review/*.md` as raw-evidence detail not needed for retrieval.
- Unreadable/unavailable: `tokenizer.json` is a 133-byte Git-LFS pointer; weight shards absent (index only: 5 files, 17.9 GB); `head.safetensors` absent locally though documented in `Files`.
- Consequential trust limits persist in prose: no Jev-labelled OOD set (53 training domains only), single-dataset calibration, English-centric corpus, `yuri_v1` placeholders teach nothing about memory relevance, escalation threshold unvalidated, and speed comparisons not like-for-like.

[^jev-9b-v08]: AutoTrust, “autotrust/JEV-9B,” model card, canonical local entry `../raw/JEV-9B/README.md`, package scope `../raw/JEV-9B/`, released checkpoint v0.8.0, upstream `https://huggingface.co/autotrust/JEV-9B`. Locators in text: frontmatter and “At a glance”/“Headline results”; “JEV-9B vs JEV-27B”; “How JEV-9B compares” and “Speed vs the hosted TypeSafe Jev 1.13”; “System 1: indistinguishable” KL table; “The Blocks of Experts recipe” and “Training details”; “Benchmark highlights” pressure plus HN/V2EX tables; “Quickstart with vLLM” completions plus client-side math; “What System 1 does,” “Other ways to run it,” “Evaluation details,” “Limitations,” “Files”; `judge_config.json` slots/ids, `calibration.json` per_kind, `adapter_vllm/decision_head.json` bias/ids, `config.json` hidden/vocab, `model.safetensors.index.json` total_size, `reports/eval_v08_bundle.md`, `reports/eval_s2_9b.md`, `reports/data_audit.md`.
[^jev-9b-2026-10-03]: AutoTrust, “autotrust/JEV-9B — 3 October 2026 update,” model card, canonical local entry `../raw/JEV-9B.md`, upstream `https://huggingface.co/autotrust/JEV-9B`. Locators in text: frontmatter `tags` (`multimodal`, `vision`, `computer-use`, `robotics`); “New (3 October 2026): JEV-9B can see — robot arm and computer use” plus “Images: quick start” (`vl/serve.sh`, `POST /v1/decide` example, `--max-num-seqs 8`, 300-decision text parity); “Files” `vl/` / `videos/` / `reports/vl/` rows.
