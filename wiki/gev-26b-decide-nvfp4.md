---
type: Concept
title: GEV-26B-Decide Adaptive Thinking and NVFP4 Quantization
description: AutoTrust GEV-26B-Decide on Gemma-4-26B-A4B with System 1 plus adaptive-thinking typed decisions and an NVFP4 expert-quantized variant fitting 17 GiB, with reported Decision Index, puzzle, vision-agent, and serving results.
tags: [gev, decision-models, adaptive-thinking, nvfp4, calibration, vllm, system-one]
status: stable
created: 2026-10-07
stale_after: 2027-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T09:36:51Z }
sources:
  - id: gev-26b-decide-2026
    resource: ../raw/GEV-26B-Decide.md
    kind: model-card
    title: autotrust/GEV-26B-Decide
  - id: jev-gemma4-2026
    resource: ../raw/JEV-Gemma4-26B-A4B.md
    kind: model-card
    title: autotrust/JEV-Gemma4-26B-A4B
  - id: gev-26b-nvfp4-2026
    resource: ../raw/GEV-26B-Decide-NVFP4.md
    kind: model-card
    title: autotrust/GEV-26B-Decide-NVFP4
---

# GEV-26B-Decide Adaptive Thinking and NVFP4 Quantization

Synthesis: `autotrust/GEV-26B-Decide` is AutoTrust AI's Gemma-4-26B-A4B-based typed-decision model with one-pass System 1 `noul` / `choice` / `score` plus opt-in adaptive thinking that folds System 2 reasoning into calibrated probabilities, and `autotrust/GEV-26B-Decide-NVFP4` is its NVFP4-quantized build — cutting vLLM weight memory from 51.1 GiB to 17.1 GiB with **reported** near-parity on GPQA Diamond and HLE spot checks, **reported** Decision Index 0.2.1 62.48 with adaptive thinking on Knowledge & Reasoning, and **reported** 45 ms System 1 decisions, 256K context, 2–256 options, and vision-agent demos[^gev-26b-decide-2026][^gev-26b-nvfp4-2026]. The same weights were first published as `autotrust/JEV-Gemma4-26B-A4B` with a **reported** System-1-only Decision Index 0.2.1 of 58.05, the baseline the adaptive 62.48 builds on[^jev-gemma4-2026].

## Identity and provenance

- Package is the bf16 model card `../raw/GEV-26B-Decide.md` (canonical entry for `autotrust/GEV-26B-Decide`) plus the NVFP4 card `../raw/GEV-26B-Decide-NVFP4.md` whose body reproduces the bf16 card plus NVFP4 sections; upstream `https://huggingface.co/autotrust/GEV-26B-Decide` and `https://huggingface.co/autotrust/GEV-26B-Decide-NVFP4`; bf16 frontmatter `base_model: google/gemma-4-26B-A4B-it`, `base_model_relation: adapter`, `pipeline_tag: text-classification`; base `autotrust/GEV-26B-Decide`, previously `autotrust/JEV-Gemma4-26B-A4B` with the same weights[^gev-26b-decide-2026][^gev-26b-nvfp4-2026][^jev-gemma4-2026].
- Original `JEV-Gemma4` bundle shipped base weights plus `adapter/` (System 1 LoRA), `head.safetensors`, `judge_config.json`, calibration tables, and `reports/` with no `adapter_vllm/`/serve/patch layout yet; the GEV rename keeps the weights and adds the vLLM server, adaptive-thinking, vision-agent, puzzle, and NVFP4 material[^jev-gemma4-2026][^gev-26b-decide-2026].
- Creator AutoTrust AI, independent open-weights builder; explicitly not affiliated with, endorsed by, or a product of TypeSafe AI, maker of hosted TypeSafe Jev 1.13[^gev-26b-nvfp4-2026].
- Backbone `google/gemma-4-26B-A4B-it` (26B parameters, about 4B active per token); System 2 is that backbone unmodified in Gemma-4 thinking mode for text and images[^gev-26b-nvfp4-2026].
- License Apache-2.0 for adapter, head, and calibration files; base model under Gemma 4 terms; English-centric[^gev-26b-nvfp4-2026].

## NVFP4 quantization — reported

- What is quantized: 3,840 routed expert MLPs (30 layers × 128 experts) to NVFP4; attention, dense MLP of every layer, routers, vision tower, `lm_head`, System 1 adapter, decision head, and temperatures stay bf16[^gev-26b-nvfp4-2026].
- Why only experts: routed experts hold most weights (about 22 GB of FP4-able bf16 in 24B parameters), and the System 1 adapter does not touch them, so `adapter_vllm/` is unchanged from bf16 and System 1 needs no retraining; attention, dense MLP, and router carry the LoRA or are small, so quantizing them saves little[^gev-26b-nvfp4-2026].
- Format: NVIDIA FP4 E2M1 values in groups of 16 with FP8 E4M3 scale per group plus FP32 scale per tensor; per expert gate, up, and down projections quantized with gate and up sharing one tensor scale as vLLM fuses them; expert activations use static scales calibrated on 3,072 System 1 prompts from GEV's own calibration splits[^gev-26b-nvfp4-2026].
- Layout uses ModelOpt NVFP4 layout and the same exclusion list as `nvidia/Gemma-4-26B-A4B-NVFP4` (`quant_method: modelopt`), so vLLM loads it with no flag, logging `modelopt_fp4` and the selected NVFP4 MoE kernel from `config.json` / `hf_quant_config.json`[^gev-26b-nvfp4-2026].

| | GEV-26B-Decide bf16 | GEV-26B-Decide-NVFP4 |
|---|---:|---:|
| download weights | 49.5 GB | 18 GB |
| vLLM weight memory | 51.1 GiB | 17.1 GiB (−66%) |

- **Reported** spot parity only: GPQA Diamond System 1 43.9% bf16 `transformers` vs 44.9% NVFP4 vLLM (198 questions); HLE text multiple-choice System 1 8.4% vs 9.7% (513 questions); card notes differences are within run-to-run noise (about ±7 points on 198)[^gev-26b-nvfp4-2026].
- **Synthesis**: treat NVFP4 as a deployment compression with two-point parity evidence, not a full-benchmark re-evaluation — the full Decision Index below ran with bf16, and adaptive thinking on NVFP4 experts was not re-evaluated[^gev-26b-nvfp4-2026].

## System 1 and adaptive thinking

- System 1: typed decisions yes/no, pick one of 2–256 options, rate 0–5, over text and images in prompts up to 256K tokens, returning a calibrated probability for every option in one forward pass in about 45 ms[^gev-26b-nvfp4-2026].
- Adaptive thinking (`thinking: "auto"`): System 1 first returning p1; below threshold default 0.8 System 2 reasons in Gemma-4 thinking mode over the same state, question, and options up to `think_budget` (evaluations used 8,192); when the thinking channel closes the answer-letter distribution p2 is read in one step and the result is p = ½ p1 + ½ p2, keeping reasoning accuracy with System 1 calibration since p2 alone is near one-hot and over-confident[^gev-26b-nvfp4-2026].
- Threshold and mix were chosen on 1,754 questions from six public sets outside the Decision Index (300 each; AQuA-RAT 254): **reported** System 1 73.3% vs adaptive 83.4% vs always-think 83.8%, thinking on 47.8%, ECE 0.035 for both System 1 and adaptive, reaching 96% of the always-think gain while thinking on 48%; median 2,282 thinking tokens, p90 7,573, 91.6% finishing within 8,192[^gev-26b-nvfp4-2026].

## Decision Index 0.2.1 — reported

- Score edition 0.2.1 with the kit's `score --edition 0.2.1`, own scoring not a board entry: balanced skill **62.48**, balanced raw 70.66, breadth skill 62.00, vs TypeSafe Jev 1.13 board 57.91[^gev-26b-nvfp4-2026].
- Area skills: Knowledge & Reasoning 0.602, Language 0.636, Retrieval & Classification 0.679, Tools & Automation 0.697, Arts & Taste 0.415[^gev-26b-nvfp4-2026].
- Method: Knowledge & Reasoning all ten benchmarks with adaptive thinking; other four areas System 1 only from the complete System 1 run of these weights (all 150,759 requests, 0 errors) in `autotrust/jev-decision-index-results` (`runs/jev-gemma4-26b-a4b`, the weights' previous name); thinking was tried on five other-area benchmarks and is not used there[^gev-26b-nvfp4-2026].
- Predecessor System-1-only baseline under the `JEV-Gemma4` name: **reported** balanced skill **58.05**, balanced raw 67.35, breadth skill 56.98 vs TypeSafe Jev 1.13 board 57.91 and `autotrust/JEV-27B` 53.30 (raw 64.32, breadth 52.21); area skills Knowledge & Reasoning 0.430, Language 0.636, Retrieval & Classification 0.679, Tools & Automation 0.697, Arts & Taste 0.415; complete run of all 150,759 suite-0.2 requests (150,317 scored; 0 errors, 0 unsupported) scored with the kit's `score --edition 0.2.1`, same results dataset under `runs/jev-gemma4-26b-a4b`; reference engine `submissions/jev/jev_engine.py` in the Decision Index kit[^jev-gemma4-2026]. **Synthesis**: the adaptive 62.48 gain over the 58.05 System-1 baseline concentrates in Knowledge & Reasoning (0.430 → 0.602); other areas carry over the System-1 run[^jev-gemma4-2026][^gev-26b-nvfp4-2026].
- Latency gate context: board requires median at most 1,000 ms per request on RTX PRO 6000; System 1 answers in about 45 ms on B200 while adaptive thinking is far slower on Knowledge & Reasoning (see Latency)[^gev-26b-nvfp4-2026].

| benchmark | chance | System 1 | adaptive | thought |
|---|---:|---:|---:|---:|
| GPQA Diamond | 25.0 | 42.9 | 78.6 | 87% |
| CRUXEval | 37.0 | 67.5 | 90.7 | 42% |
| CLadder | 50.0 | 71.0 | 86.6 | 51% |
| GSM8K | 25.0 | 97.6 | 99.1 | 5% |
| SATA-Bench case exact | 1.3 | 34.2 | 35.5 | 21% |
| MuSR | 37.1 | 67.3 | 67.6 | 51% |
| ChessBench | 8.2 | 23.7 | 23.6 | 88% |
| HLE | 16.4 | 8.4 | 17.8 | 88% |
| MMLU-Pro | 11.1 | 65.0 | 84.6 | 78% |
| BBH | 31.0 | 75.0 | 92.0 | 60% |

Accuracy in %; Decision Index skill rescales chance to 0; Knowledge & Reasoning area skill 0.429 → 0.602[^gev-26b-nvfp4-2026].

- Real gains on science, code, causal, and multi-step reasoning (GPQA, CRUXEval, CLadder, MMLU-Pro, BBH); HLE only returns to chance because confident no-think answers are almost all wrong (1.6% correct) and thinking lifts 8.4% to 17.8% near guessing; chess does not benefit because two-thirds of thoughts hit the 8,192 budget and truncated-thought answers are no better (17.0% vs 17.7%) plus over-confident, while finished thoughts gain a little (19.8% → 22.7%)[^gev-26b-nvfp4-2026].
- Outside Knowledge & Reasoning (same adaptive settings, run stopped after five): **reported** BFCL 94.4 → 96.0, API-Bank 84.3 → 86.0, CLINC150+OOS macro-F1 93.3 → 94.4, ToolRet nDCG@10 66.8 → 66.9, BANKING77 macro-F1 88.0 → 85.0 loss on a task whose training split System 1 trained on; **synthesis**: use thinking for reasoning questions, keep it off for classification, retrieval, and tool routing[^gev-26b-nvfp4-2026].

## Latency — reported

- Over the ten area benchmarks 66% of requests thought at least once; thinking length median 8,192 tokens (the budget) on GPQA/HLE/ChessBench, about 5,400 on MMLU-Pro, 3,300 on BBH, 900 on GSM8K[^gev-26b-nvfp4-2026].
- Estimated single-request latency on one idle B200 at System 1 about 45 ms plus thinking about 250 tokens/s: about 0.05 s without thinking and up to about 33 s with an 8,192-token thought; median 13.4 s, p90 33 s; with speculative decoding at about 438 tokens/s median 7.7 s, p90 19 s; lower `threshold` or `think_budget`, or `thinking: "off"`, to trade accuracy for speed[^gev-26b-nvfp4-2026].
- MMLU-Pro and BBH except six questions ran with speculative decoding without changing the output distribution; six 18-option BBH questions hit a vLLM error in the speculative read-out path and were answered without it; current `serve_decide.py` reads answers through a path that works with speculative decoding[^gev-26b-nvfp4-2026].

## Puzzles, games, and vision agents — reported

- One-move puzzles, 200 generated per game, threshold 0.8, budget 8,192, text except chess board image plus FEN: Minesweeper 21.0% → 86.0%, Wordle 52.0% → 100%, Connect Four 54.0% → 99.5%, Sudoku 76.0% → 99.5%, 24-game 89.0% → 100%, Maze 48.5% → 68.0%, Lichess mate-in-one 46.5% → 78.0%[^gev-26b-nvfp4-2026].
- Whole games and perception where thinking helps little: Snake 3 food/18 steps vs 11/90 (about 21 s/step), full Connect Four 1 win/5 losses vs 1/4/1, 2048 1,476 vs 1,016, Flappy Bird 0 pipes both, Quick Draw 320 sketches 46.9/73.1/94.4% vs 40.3/72.8/95.0%; **synthesis**: thinking pays when the answer is checkable step by step against explicit rules, not for perception, reflexes, or long-horizon play[^gev-26b-nvfp4-2026].
- Computer use from 3 October 2026, fastest vision of the family, every step one System 1 decision on one B200: screenshot plus numbered boxes plus element text → next click, 95% of 60 multi-step tasks (shop/settings/mail, 3–7 clicks) at about 85 ms per click, same rate as JEV-27B-VL at 3× speed; boxes alone complete 15% and often declare done too early, so supply element text as an accessibility tree would[^gev-26b-nvfp4-2026].
- Robot arm pick-and-place from a top camera image, two questions per step (left/right, above/below) with step halving on flip: 61 ms per decision, 4–8 s model time per pick-place, 40% of 20 scenes vs 75% JEV-27B-VL and 50% JEV-9B, close-range left/right less precise so more grasps miss, 8 of 9 grasped cubes ended in the tray; asking for one of 8 motor commands directly completed 0 of 10[^gev-26b-nvfp4-2026].

## Images, context, and many options — reported

- Checkpoint holds Gemma-4 vision encoder without audio encoder; System 1 and System 2 accept images but the decision head trained on text, so image decisions are zero-shot: synthetic colour/shape/printed-number/red-object checks 100% each on 30 images; VL-RewardBench 1,247 pairs both orders averaged 78.4% overall (general 55.8, hallucination 84.9, reasoning 76.0, macro 72.2) vs JEV-27B-VL 78.3 same protocol[^gev-26b-nvfp4-2026].
- Native context 262,144 tokens (256K); tested single-sentence-at-depth in concatenated PubMedQA abstracts, yes/no plus 16-option, 10 each per length on one B200: 4K/32K/64K/128K all 10/10 with mean right-answer probability 0.999–1.000 and median latency 0.15/1.6/5.0/17.8 s; above 128K untested[^gev-26b-nvfp4-2026].
- `choice` takes 2–256 options: up to 16 read in one pass with labels A–P, more in groups of at most 16 in parallel plus a final of 16 with every option read and none pruned (`strategy: "tournament"` default); **reported** zero-shot intent on 400 utterances per row: MASSIVE-en 59 options 91.2%, BANKING77 77 options 81.5%, CLINC150 150 options 95.5%, merged 255-intent CLINC 89.0% and BANKING 75.2% with near-duplicate labels part of the drop; `strategy: "single"` beyond P is about 3× faster but less accurate (CLINC150 88.5% vs 95.2%), so not default[^gev-26b-nvfp4-2026].

## Serving and engine — reported

- NVFP4 deploy: `hf download autotrust/GEV-26B-Decide-NVFP4 --local-dir GEV-26B-Decide-NVFP4`, then `MODEL_DIR=... bash .../serve.sh` for vLLM on :8000; one GPU with 24 GB or more, whole model fits 24 GB short-context and 32 GB RTX 5090 or 48 GB long-context with many concurrent requests; set `--gpu-memory-utilization` and `MAX_MODEL_LEN` such as 32768 to fit[^gev-26b-nvfp4-2026]. Bf16 deploy from the canonical card is `hf download autotrust/GEV-26B-Decide --local-dir GEV-26B-Decide` then `bash GEV-26B-Decide/serve.sh` on one GPU with 80 GB or more[^gev-26b-decide-2026].
- `serve.sh` runs `serve_decide.py`: standard vLLM OpenAI server plus `POST /v1/decide` route, backbone loaded once with plain requests as System 2 and LoRA module `jev-decision` (`adapter_vllm/`: backbone LoRA plus head as `lm_head` LoRA) as System 1; needs vLLM build with Gemma-4 support plus `patches/vllm-gemma4-lm-head-lora.patch` for LoRA on tied `lm_head` vocab 262,144, tested September 2026 dev build[^gev-26b-nvfp4-2026].
- `POST /v1/decide` fields: `kind` (`noul` false/true, `score` 0–5, `choice` options), `state` string/JSON/list mixing text and `{"image": "https://… or data:…"}` images, `question`, `options` 2–256 for choice, `thinking` off/auto/on, `threshold` 0.8, `think_budget`, `chat_template_kwargs` without `reasoning_effort`, `strategy` tournament/single/permute, `return_reasoning`/`debug`; response carries `options`, `probabilities`, `choice`, `choice_index`, `usage`, plus `thinking: {used, think_tokens, think_seconds, finished_within_budget}`; `GET /v1/decide/info` lists defaults[^gev-26b-nvfp4-2026].
- Speed on one B200: System 1 median 45 ms single request, 257 decisions/s at 64 clients, vLLM matching `transformers` to mean largest-probability difference 0.015 on 300 held-out decisions; adaptive thinking adds about 1 s per 250 thinking tokens[^gev-26b-nvfp4-2026].
- Faster thinking with speculative decoding: `MTP=1 bash .../serve.sh` adds 0.9 GB draft `google/gemma-4-26B-A4B-it-assistant` with 4 speculative tokens, speeding System 2 about 1.8–1.9× (247 → 438 tokens/s single, 7,072 → 13,505 tokens/s at 128 concurrent, acceptance 3.5–3.7/4) while System 1 high-concurrency throughput drops 257 → 140/s, so use it when mostly thinking; needs `--max-logprobs 256`[^gev-26b-nvfp4-2026].
- Manual System 1 via `/v1/completions` must start the prompt with `<bos>` and pass `top_k: 0`, `top_p: 1.0` because generation config `top_k=64`/`top_p=0.95` would otherwise truncate probabilities; `serve_decide.py` handles the System 1 prompt prefix for `/v1/decide`[^gev-26b-nvfp4-2026].
- `transformers` plus `peft` System 1 path needs the bf16 weights (`autotrust/GEV-26B-Decide`), merges adapter in memory, then applies 24-slot fp32 head with 30 softcap, masking, per-kind temperature, and softmax; reads up to 16 options per pass, using the server or grouped reads plus final for more[^gev-26b-nvfp4-2026][^jev-gemma4-2026].
- Engine: template `bare-v1` prefixed with `<bos>` (`[kind] … [state] … [question] … [options] A) … [decision]:`); read-out takes final-norm hidden state of the last token through linear fp32 head 2,816 → 24 slots, soft-capped at 30, masks inactive slots, divides by per-kind temperature, and softmaxes with nothing generated[^gev-26b-nvfp4-2026][^jev-gemma4-2026].

## Temperatures, training disclosure, and limits

- `calibration.json` default used in the Decision Index run: noul 1.003, choice 1.017, score 0.999; `calibration_gold.json` against ground truth: 1.214, 1.098, 1.000; use gold when gating automatic actions on confidence[^gev-26b-nvfp4-2026][^jev-gemma4-2026].
- Training disclosure: System 1 trained on teacher distributions plus ground-truth decision data including public training splits of some datasets whose test splits the Decision Index uses (among them BANKING77 and CLINC150); no test split used, suite items excluded before training, list supplied to Decision Index maintainers; MMMU/MMMU-Pro are not valid evaluations; adaptive settings chosen outside the suite[^gev-26b-nvfp4-2026][^jev-gemma4-2026].
- Limits: teacher-wrong often means System 1 confidently wrong (HLE no-think 1.6% correct); thinking does not help classification/retrieval and can hurt trained tasks (BANKING77 88.0 → 85.0) or slightly lower commonsense (CommonsenseQA 86.7 → 85.0); thinking is slow on hard inputs and misses the Decision Index latency limit; own scoring not a board result; weaker than JEV-27B on long structured inputs such as Home appliance simulator and POP909; HLE below chance with System 1 like every open board entry; image decisions zero-shot; contexts above 128K untested; one-engine vLLM needs the bundled patch; `noul`/`score` accept only their canonical options; English-centric and not for high-stakes decisions without confidence gating[^gev-26b-nvfp4-2026][^jev-gemma4-2026].

## Relationships

- Uses [Jev API Patterns](jev-api-patterns.md) `noul` / `choice` / `score` semantics through a distinct `POST /v1/decide` API with `thinking`, `threshold`, `think_budget`, and `strategy` controls.
- Uses [Classifier Calibration](classifier-calibration.md) per-kind temperatures plus a ground-truth-gated gold table.
- Extends [Jev Decision Model](jev-decision-model.md) with an independent open-weights Gemma-4 alternative and NVFP4 self-hosting point.
- Informs [Classifier Selection](classifier-selection.md) when reasoning accuracy must be weighed against thinking latency and 24 GB self-hosting.
- Compared with [Jev-27B-VL Vision-Capable System 1 Decisions and Serving](jev-27b-vl-multimodal-decisions.md) on computer-use parity at 3× speed and weaker robot-arm grasp precision, and with [JEV-9B System 1 Decisions and Blocks-of-Experts Serving](jev-9b-system1-decisions.md) for demo-code reuse.

## Coverage limits

- Inspected three single-file cards by static reading: `../raw/JEV-Gemma4-26B-A4B.md` (predecessor System-1-only card) plus `../raw/GEV-26B-Decide.md` (bf16, canonical) and `../raw/GEV-26B-Decide-NVFP4.md`; diff confirms the NVFP4 card reproduces the bf16 body plus NVFP4 frontmatter/sections, and the GEV bf16 card supersedes the JEV-Gemma4 card on the same weights — keeping its System-1-only 58.05 run, `bare-v1`/24-slot/temperature/transformers mechanics, and training/limits disclosure while adding adaptive thinking, vLLM serving, vision-agent/puzzle/context/many-option evidence, and the 80 GB vs 24 GB serve requirement with the `transformers`-needs-bf16 note[^jev-gemma4-2026][^gev-26b-decide-2026][^gev-26b-nvfp4-2026], with no weight download, server run, API call, or benchmark reproduction, so all performance, latency, and parity figures are **Reported** vendor/model-card evidence under `decision-models` rules, while file layouts and API shapes are card-stated interfaces[^gev-26b-nvfp4-2026].
- Excluded with reason: embedded `<video>` demos as illustrative (results captured via prose tables, pixels not inspected); `reports/*.json` and `reports/demos/` per-episode files, `serve_decide.py`/`serve.sh`/`patches/` code, `nvfp4_activation_amax.json`, tokenizer/processor/chat-template artifacts, and upstream Hugging Face datasets/repos as uninspected linked evidence; NVFP4-only `nvfp4_activation_amax.json` and `hf_quant_config.json` covered via the NVFP4 card prose without file inspection[^gev-26b-nvfp4-2026].
- Consequential limits persist in prose: full Decision Index is bf16-only; NVFP4 comparison is two System 1 spot checks with different engines; System 2 on NVFP4 experts unevaluated; SM12x and SM80–90 kernels untested here; speculative-decoding BBH workaround; training-split contamination disclosure for BANKING77/CLINC150; and time-sensitive `stale_after` 2027-10-07 for release, API, and leaderboard figures[^gev-26b-nvfp4-2026].

[^gev-26b-decide-2026]: AutoTrust, "autotrust/GEV-26B-Decide," model card, canonical local entry `../raw/GEV-26B-Decide.md`, upstream `https://huggingface.co/autotrust/GEV-26B-Decide`. Locators: Decision Index 0.2.1 62.48 header and balanced/area tables; "New (3 October 2026)" computer-use/robot-arm demos; "Overview" System 1/adaptive/System 2 table; "Watch it think" puzzles; "Adaptive thinking" validation, ten-benchmark, five-benchmark, latency; "Images," "Context length," "Many options"; "Quick start (vLLM)" 80 GB serve.sh, `POST /v1/decide` fields, System 2 example, speed/speculative-decoding; "Usage (transformers + peft)"; "Engine and read-out," "Temperatures," "Training data (disclosure)," "Limitations," "Files," frontmatter `base_model`/`base_model_relation`/`license`/`model-index`.

[^jev-gemma4-2026]: AutoTrust, "autotrust/JEV-Gemma4-26B-A4B," model card, canonical local entry `../raw/JEV-Gemma4-26B-A4B.md`. Locators: header Decision Index 0.2.1 58.05; "Decision Index 0.2.1" complete-run sentence, balanced/breadth table, JEV-27B comparison row, five-area skill table, results dataset `runs/jev-gemma4-26b-a4b`, reference engine `submissions/jev/jev_engine.py`; System 1/System 2 bundle paragraph, `noul`/`choice` 2–16 plus grouped final/`score` 0–5 list, two-models-two-organisations note; "Engine and read-out" `bare-v1`, 2,816 → 24 fp32 head, softcap 30, per-kind temperature; "Temperatures" default vs gold table; "Usage (transformers + peft)" adapter-merge code; "Training data (disclosure)" training-split/test-split/suite-exclusion/MMMU sentences; "Limitations" teacher/long-input/HLE/canonical-options/English bullets; "Files" adapter/head/judge/calibration/reports layout; frontmatter `base_model`/`base_model_relation`/`license`/`model-index` 58.05.

[^gev-26b-nvfp4-2026]: AutoTrust, “autotrust/GEV-26B-Decide-NVFP4,” model card, canonical local entry `../raw/GEV-26B-Decide-NVFP4.md`, upstream `https://huggingface.co/autotrust/GEV-26B-Decide-NVFP4`. Locators in text: “NVFP4 version” memory/comparison table, “What is quantized and how,” “Why only the experts,” “Deploy the NVFP4 version” GPU table plus memory/patch/prompt/`transformers` bullets; “Decision Index” balanced/area tables and scoring bullets; “New (3 October 2026)” computer-use/robot-arm table and bullets; “Overview” System 1/adaptive/System 2 table; “Watch it think” puzzle tables; “Adaptive thinking” 1,754-question, Knowledge & Reasoning ten-benchmark, outside-area five-benchmark, and latency subsections; “Images,” “Context length,” “Many options” tables; “Quick start (vLLM)” `POST /v1/decide` field table, response shape, System 2 example, speed and speculative-decoding bullets; “Usage (transformers + peft)” code; “Engine and read-out,” “Temperatures,” “Training data (disclosure),” “Limitations,” “Files,” frontmatter `base_model`/`license`/`model-index`.
