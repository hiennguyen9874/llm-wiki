---
type: Concept
title: Jev-27B-VL Vision-Capable System 1 Decisions and Serving
description: JEV-27B-VL adds zero-shot vision to JEV-27B System 1 decisions, with reported robot-arm and computer-use control plus video-recommendation, agent-judge and multimodal-judge results, 256-option, 256K-context and vLLM serving details.
tags: [jev, vision, multimodal, recommendation, judge, vllm, agents]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-07T17:00:00Z }
sources:
  - id: jev-27b-vl-2026-10-01
    resource: ../raw/JEV-27B-VL/README.md
    scope: ../raw/JEV-27B-VL/
    kind: model-card
    title: autotrust/JEV-27B-VL
  - id: jev-27b-vl-2026-10-03
    resource: ../raw/JEV-27B-VL.md
    kind: model-card
    title: autotrust/JEV-27B-VL — 3 October 2026 update
---

# Jev-27B-VL Vision-Capable System 1 Decisions and Serving

Synthesis: `autotrust/JEV-27B-VL` is JEV-27B with vision — the same text System 1 plus zero-shot image decisions whose head never saw images in training — served as calibrated `noul` / `choice` / `score` probabilities over text and images via `POST /v1/decide`, with **reported** 3-October-2026 robot-arm and computer-use control loops alongside recommendation and judge results at frontier level and **observed** vLLM adapter, bias plus temperature, wide-label, and adaptive-thinking mechanics[^jev-27b-vl-2026-10-01][^jev-27b-vl-2026-10-03].

## Identity and provenance

- Package `../raw/JEV-27B-VL/` with canonical entry `README.md` and supporting release post `blog/JEV-27B-VL.md`; release notes dated 1 October 2026, blog dated 30 September 2026; no commit hash is captured locally, so identity is the package scope[^jev-27b-vl-2026-10-01].
- Base is stated as `Qwen/Qwen3.8-27B` unchanged (frontmatter `base_model`, Apache-2.0 `LICENSE`); **observed** `config.json` uses `model_type: qwen3_5` and `Qwen3_5ForConditionalGeneration` with 64 text layers, 262,144 native context, plus a 27-layer vision encoder — report both strings without resolving the 3.5 versus 3.8 naming[^jev-27b-vl-2026-10-01].
- Contract: System 1 gives a calibrated probability for every option in one forward pass over text and images; System 2 is the unmodified base thinking step by step with image input[^jev-27b-vl-2026-10-01].
- License Apache-2.0: Qwen weights unchanged plus the JEV System 1 adapter and decision head from `autotrust/JEV-27B`[^jev-27b-vl-2026-10-01].

## Zero-shot vision claim

- Decision head was trained on text only; image decisions are zero-shot with ordering demonstrated but image-task calibration not systematically measured — a stated limitation[^jev-27b-vl-2026-10-01].
- Text parity is **reported**: on 1,000 answer-checking decisions the mean probability difference to JEV-27B is 0.010 and 99.8% fall on the same side of 0.5[^jev-27b-vl-2026-10-01].
- Demo vignettes are single-pass action probabilities per frame: Mario movement plus jump about 150 ms, Rubik's Cube 11-formula choice about 46 ms, Tetris column plus orientation about 122 ms, Quick Draw 16-way about 270 ms, Snake direction about 300 ms; Quick Draw detail is 88% when finished and 62% at 60% of strokes on 320 sketches versus 6% random[^jev-27b-vl-2026-10-01].

## Embodied and computer-use control — reported 3 October 2026 update

- Every step is one System 1 decision: a camera image or screenshot in, a probability for every action out, in a single forward pass[^jev-27b-vl-2026-10-03].
- Robot-arm pick and place from a camera image (MuJoCo simulation): at each step System 1 answers two questions from the top camera image — is the target left or right of the gripper, and above or below it — the arm moves accordingly and halves its step whenever an answer flips; it grasps the cube, carries it, and drops it in the tray[^jev-27b-vl-2026-10-03].
- **Reported** result: 75% of 20 random scenes completed, the best of the JEV family; every grasped cube ended in the tray (15 of 15) and every miss was a grasp 3.0–3.7 cm off target; about 240 ms per decision (239 ms in the family table)[^jev-27b-vl-2026-10-03].
- Computer use on a real browser (headless Chromium): every clickable element gets a numbered box, System 1 picks the next click (or "the task is complete"), the browser clicks it, and the loop repeats[^jev-27b-vl-2026-10-03].
- **Reported** result: 95% of 60 random multi-step tasks completed (shop, settings, mail; 3–7 clicks each), about 0.26 s per click; the colour-swatch click carries no text so it is decided from the screenshot alone[^jev-27b-vl-2026-10-03].
- Same scenes and tasks for every model in the family (**reported**): robot pick-and-place JEV-27B-VL 75% versus [JEV-9B](jev-9b-system1-decisions.md) 50% versus GEV-26B-Decide 40%; computer use with numbered boxes plus element text 95% for all three; numbered boxes only 10% versus 37% versus 15%; time per robot-arm decision 239 ms versus 163 ms versus 61 ms[^jev-27b-vl-2026-10-03].
- Negative results and guidance: asking System 1 to pick one of 8 motor commands directly completed 0 of 10 scenes — use it for simple visual questions inside a control loop; with numbered boxes alone it often declares the task complete too early, so supply the element text as an accessibility tree would[^jev-27b-vl-2026-10-03].
- Provenance: demo code is the JEV-9B `vl/demos/` tree (point `JEV_URL` at this server) and per-episode results are under `reports/demos/`; the two demo videos are remote HF links and were not inspected locally[^jev-27b-vl-2026-10-03].

## Reported applied results

- Short-video recommendation on MicroLens-100k covers: 200 users, each true next video hidden among 19 others watched within ±3 days; covers-only AUC 0.727, HR@5 0.590, NDCG@10 0.498 versus titles-only 0.649 / 0.455 / 0.399, TF-IDF 0.602, and item-based CF 0.728 / 0.490 / 0.503 learned from 59,045 users; gap to CF 0.000 with 95% interval −0.041 to +0.040, covers beat titles by +0.078 with interval +0.031 to +0.126; 20 covers scored in about 2.6 s; offline single-dataset cold-start evidence only[^jev-27b-vl-2026-10-01].
- Plan-RewardBench ACL 2026 agent trajectories: 73.2% macro-average on 1,171 planning, error-recovery, refusal, and tool-irrelevance pairs, top of the paper table versus Qwen-Plus 70.0, DeepSeek-V3.2 69.6, Inf-ORM 69.2, Gemini-3-Flash 69.1, GPT-5 68.5[^jev-27b-vl-2026-10-01].
- AgentRewardBench with screenshots: 1,302 trajectories, higher precision than every leaderboard judge at that judge's own recall, e.g. rule-based 83.8→86.2 at recall 55.9 and GPT-4o 69.8→72.9 at recall 83.1; at threshold 0.5 precision 78.4 and recall 70.2 with AUROC 0.91 in about 4 minutes on one GPU[^jev-27b-vl-2026-10-01].
- VL-RewardBench CVPR 2025: 78.3% overall on 1,247 pairs (general 58.0, hallucination 83.2, reasoning 78.2, macro 73.1), above all 26 May-2025 leaderboard models including Skywork-VL-Reward-7B 73.3 and GPT-4o 65.8; 2,494 orderings in 163 s[^jev-27b-vl-2026-10-01].
- Multimodal RewardBench 2 December 2025: average 63.8 with text-to-image 69.2, interleaved 67.8, reasoning 60.4, and editing 57.8 as the weak task; text-to-image within 1.3 points of GPT-5 while GPT-5 and Gemini 3 Pro stay ahead overall[^jev-27b-vl-2026-10-01].
- Text benchmarks measured with JEV-27B except the image rows: six-group mean 84.07 (JevBench 88.70, Kev 83.75, OpenJev text 73.89, Nimble 92.91, VitaminC 77.46, MASSIVE-en 87.71) versus hosted TypeSafe Jev 1.13 at 83.85, both run in full 27 September 2026 while other rows reuse NeoHorse-Jev-4B reported values; fidelity on held-out `test_set_30k` is KL ≈0.017, yes/no AUROC 0.995, choice agreement 95.8%, rating MAE 0.098, ECE 0.0009, unseen-family KL 0.104; independent `decision-models-under-pressure` gold-label check trails TypeSafe by 1–3 points at 2–16 options[^jev-27b-vl-2026-10-01].
- Other **reported** text applications: PubMedQA 77.8% versus human 78.0%, RewardBench 89.9 versus Gemini 1.5 Pro 88.2, TriviaQA trusted-half 96.4% versus 71.2% answering everything, MIND news AUC 0.642 versus trained LightGBM 0.616, TREC-COVID nDCG@10 0.858 versus bge-reranker 0.793, System 1→System 2 escalation at 0.70 giving 0.892 with 70% in 0.11 s, and HumanEval 78.0% identical to the base[^jev-27b-vl-2026-10-01].

## Choice scale, prompts, and context

- `choice` takes 2–256 options in one question; first 16 labels A–P are the trained head, beyond-16 continues Q–Z then single-token AA and AB forms with `adaptation: native` versus `wide-labels` and no retraining; zero-shot intent accuracy reaches CLINC150-150 89.5% names-only and 93.8% with one-line descriptions, and one `choice` beats one yes/no per option at one forward pass instead of one per option[^jev-27b-vl-2026-10-01].
- Calibration at 150 options on CLINC150 is ECE 0.079 names-only (mean confidence 0.84 against 89.5% accuracy, slightly under-confident) and 0.034 with descriptions; 150-option latency median is 1.4 s names-only and 2.6 s with descriptions on one B200, with two-pass readout above 128 options reusing cached prompt[^jev-27b-vl-2026-10-01].
- Prompt rules that survived measurement: facts in `state` with one question in `question` where JSON and plain text tie; one `choice` over per-candidate yes/no; one-line neighbour-separating use-when descriptions as the only clear win (+4.8 BANKING77-64, +2.5 CLINC150-64, +4.3 CLINC150-150) while longer do-not-use clauses, examples, and generic descriptions add nothing; wording, JSON shape, extra instructions, and alphabetical order stay within ±1.5 points inside ±1.8 sampling noise; phrase `noul` so true is the wanted outcome; one option per line; about 7% of 16-option answers flip on order alone so average both orders for pairs; act on validated thresholds and route the rest to System 2 or a person[^jev-27b-vl-2026-10-01].
- Long context: 256K native; single-fact yes/no plus 16-option needle over concatenated PubMedQA abstracts scores 20 of 20 at 4K, 32K, 64K, 128K, 192K, and 250K with mean correct-option probability 0.997–0.999 and single-stream latency 0.6–28.7 s; KV cache about 65 KB per token so full 256K needs about 17 GB over 52 GB weights, with 131072 advised on 80 GB GPUs; harder long-document and long image-document reasoning are unmeasured[^jev-27b-vl-2026-10-01].

## Serving mechanics — observed

- `serve.sh` plus `serve_decide.py` add `POST /v1/decide` to the vLLM OpenAI server: `{kind, state, question, options}` with `state` as string, JSON object, or text-plus-image list using data URLs or https URLs; `GET /v1/decide/info` reports limits and temperatures; canonical flags include `--enable-lora --max-lora-rank 32 --lora-modules jev-decision=adapter_vllm --logprobs-mode processed_logprobs --limit-mm-per-prompt '{"image": 8}' --max-num-seqs 8 --trust-request-chat-template`[^jev-27b-vl-2026-10-01].
- Decision math is **observed** in code and configs: `decision_head.json` slots `noul` 0–2 (`false`, `true`), `score` 2–8 (`0`–`5`), `choice` 8–24 (`A`–`P`) under `template_version: bare-v1`; readout is `lm_head`-LoRA log-probability plus `bias` divided by per-kind temperature from `calibration.json` (`noul` 1.0143 on n=4363, `choice` 1.0161 on n=3418, `score` 1.0036 on n=3173); callers bypassing `/v1/decide` must pass `top_k: 0` and `top_p: 1.0` because `generation_config.json` defaults `top_k: 20` and `top_p: 0.95` would otherwise truncate processed log-probs[^jev-27b-vl-2026-10-01].
- Hard serving limits: `--max-num-seqs 8` is required because a vLLM LoRA path for this multimodal class returns wrong System 1 probabilities above 8, while text-only JEV-27B is unaffected; throughput on one B200 is 24 short text decisions in about 1.4 s and 4,000 six-image decisions in 316 s; downscale large images to about 448 px to save vision tokens; September-2026 vLLM dev build is needed for `logprob_token_ids`[^jev-27b-vl-2026-10-01].
- Adaptive thinking in `serve_decide.py` extends the card: `thinking off` by default with `auto` below `threshold` 0.8 and `on` always, mixing `p = (1−w)·p1 + w·p2` at `w = 0.5` to preserve System 1 calibration; `strategy single` is default for this Qwen profile with `tournament` and `permute` available; `score` does not support thinking and `system2_only`, `think_budget`, `return_reasoning`, and `debug` are extra controls[^jev-27b-vl-2026-10-01].

## Relationships

- Extends [Jev Decision Model](jev-decision-model.md) text results with vision parity, six-benchmark mean, and fidelity numbers.
- Extends [Jev API Patterns](jev-api-patterns.md) hosted shapes with local `/v1/decide`, wide-label choice, and prompt rules.
- Uses [Classifier Calibration](classifier-calibration.md) per-kind temperatures and ECE limits.
- Uses [System One Models](system-one-models.md) System 1 versus System 2 framing for image decisions.
- Informs [Classifier Selection](classifier-selection.md) cold-start recommendation and judge-versus-frontier choices.
- Compared with [JEV-9B System 1 Decisions and Blocks-of-Experts Serving](jev-9b-system1-decisions.md) and [GEV-26B-Decide Adaptive Thinking and NVFP4 Quantization](gev-26b-decide-nvfp4.md) on the same robot-arm scenes and computer-use tasks, where JEV-27B-VL leads on grasp success while trailing on per-decision latency.

## Coverage limits

- Inspected `README.md`, `blog/JEV-27B-VL.md`, `config.json`, `calibration.json`, `adapter_vllm/adapter_config.json`, `adapter_vllm/decision_head.json`, `serve_decide.py`, `serve.sh`, `generation_config.json`, preprocessor configs, and `model.safetensors.index.json` metadata by static reading; no server execution, API calls, or benchmark reproduction was performed, so performance numbers are **reported** while interfaces and configs are **observed**.
- Additionally inspected `../raw/JEV-27B-VL.md` statically (the 3 October 2026 update: robot-arm and computer-use section plus family table); the two demo videos and the referenced JEV-9B `vl/demos/` code and `reports/demos/` per-episode files are remote and were not inspected or executed, so those control-loop figures are **reported** with small-sample limits (20 scenes, 60 tasks).
- Excluded with reason: `tokenizer.json` and `videos/*.mp4` are Git-LFS pointers whose bytes are unavailable locally; `vocab.json` and `tokenizer_config.json` special-token detail beyond vision delimiters was not needed for retrieval; weight shards are not present, only the 1,199-entry index totalling about 55.6 GB.
- PNG figures were treated as redundant because their tables are reproduced in prose; two blog images are LFS placeholders and were not visually inspected.
- Consequential trust limits persist in prose: zero-shot image calibration, single-dataset video recommendation, single-dataset wide-label calibration, and single-fact text-only long-context coverage.

[^jev-27b-vl-2026-10-01]: AutoTrust, “autotrust/JEV-27B-VL,” model card, canonical local entry `../raw/JEV-27B-VL/README.md`, package scope `../raw/JEV-27B-VL/`, release notes 2026-10-01 with blog `blog/JEV-27B-VL.md` 2026-09-30, upstream `https://huggingface.co/autotrust/JEV-27B-VL`. Locators in text: frontmatter and System 1/2 table; “Highlight” video-recommendation, agent-judge, and multimodal-judge tables; “Benchmarks” six-group, fidelity, pressure, and applied-task tables; “Quick start” plus “System 1: POST /v1/decide” and client-side readout; “Choice questions,” “Writing System 1 prompts,” “Context length,” “Serving notes,” and “Limitations”; `adapter_vllm/decision_head.json` slots and bias, `calibration.json` per_kind, `config.json` model_type, `serve_decide.py::PROFILES/READ/s1_dist/s2_dist/decide`, and `serve.sh` flags.
[^jev-27b-vl-2026-10-03]: AutoTrust, “autotrust/JEV-27B-VL — 3 October 2026 update,” model card, canonical local entry `../raw/JEV-27B-VL.md`, upstream `https://huggingface.co/autotrust/JEV-27B-VL`. Locators in text: “New (3 October 2026): robot arm and computer use” section, family comparison table, control-loop guidance bullets, and demo-code / `reports/demos/` pointer.
