---
type: Concept
title: 'Laya Decision Models: Open Multilingual Typed Decisions with RLCD and Router Runtime'
description: Open-weight Jev-compatible decision-model family with three calibrated checkpoints, per-option [MASK] scoring, RLCD training, and script-routed multilingual serving.
tags: [laya, decision-models, open-weights, calibration, fine-tuning]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T23:30:00Z }
sources:
  - id: laya-2026-10-02
    resource: ../raw/laya/README.md
    scope: ../raw/laya/
    kind: code
    title: Laya
---

# Laya Decision Models: Open Multilingual Typed Decisions with RLCD and Router Runtime

Synthesis: Laya is Convai Innovations' Apache-2.0 family of non-autoregressive System 1 decision models that answers typed `choice`/`score`/`noul` questions in a single forward pass (~33 ms), trained with reinforcement learning against strictly proper scoring rules (RLCD), with a `Router` that picks one of three checkpoints per request by script and language[^laya-2026-10-02].

## Identity and checkpoints

- Family hub is `convaiinnovations/laya` with the English checkpoint at the repo root and the other two as subfolders; only the requested checkpoint is downloaded[^laya-2026-10-02].
- Checkpoint table is **reported** (README "This repo holds all three checkpoints")[^laya-2026-10-02]:
  - `convaiinnovations/laya` on ModernBERT-large, 421M, 512 context, for English text, guardrails and email triage.
  - `convaiinnovations/laya-multilingual` on mmBERT-base, 322M, 1024 context (up to 8,192), for 100+ languages at ~2.2x speed.
  - `convaiinnovations/laya-typed-decisions` on ModernBERT-large, 421M, 1024 context, for four typed-decisions workflows at 0.766 accuracy.
- License is **reported** Apache 2.0; runtime is `pip install laya` on Python 3.10+, with extras for serve, MCP, LangChain/LangGraph, LlamaIndex, CrewAI, ONNX and TileLang fast path[^laya-2026-10-02].
- It never generates text, so there is nothing to parse and nothing to hallucinate[^laya-2026-10-02].

## Architecture (observed)

- Each checkpoint is **observed** as a pretrained bidirectional encoder plus a from-scratch decision head: 2 transformer layers, per-option marker scorer (`LayerNorm`-`Linear`-`GELU`-`Linear`), question-type embedding, and an act/escalate head (`rl_common.py::DecisionModel`) [^laya-2026-10-02].
- Request encoding is **observed** as `[CLS] <type> instructions [SEP] [MASK] opt0 [MASK] opt1 ... [SEP] state [SEP]`, with one `[MASK]` marker per option scored then softmaxed over that question's options (`rl_common.py::build_sequence`, `render_options`) [^laya-2026-10-02].
- Option text is capped at 48 tokens per option with even shrinking when the head budget overflows, and over-long options cause training rows to be skipped rather than trained truncated (`rl_common.py::build_sequence`, `encode_record`) [^laya-2026-10-02].
- `noul` is always two slots in `[false, true]` order with `p[1]` returned as `noul`; `choice` renders `key` or `key: description`; `score` renders `level i: description` (`rl_common.py::render_options`) [^laya-2026-10-02].
- Inference entry `RLAgent.system_one(state, questions)` packs every question into one collated batch, runs one forward pass, applies per-bucket temperature, and returns `{model, answers, usage}` with `input_tokens` and zero `output_tokens` (`rl_agent_api.py::RLAgent.system_one`) [^laya-2026-10-02].
- Confidence is 1 minus normalized entropy of the answer distribution (`rl_common.py::confidence_from_probs`); empty question sets return `{"answers": {}}` with zero tokens and no forward pass[^laya-2026-10-02].

## Training with RLCD (observed plus reported)

- RLCD is **reported** as: the policy reports a distribution, exploration adds zero-mean Gaussian noise to logits, reward is a strictly proper scoring rule (log plus spherical, plus ranked probability score for ordinal questions), so expected reward is maximised only by honest probabilities; updates are REINFORCE with a group-mean baseline (GRPO-style), and multi-turn conversations use TD(λ=1.0) over prefix slices[^laya-2026-10-02].
- Reward and TD mechanics are **observed** in `rl_common.py::proper_reward` (log score plus 0.5 spherical, minus RPS for `score`) and `td_lambda_targets` with per-record episode groups, prefix lengths (`episode_prefix_lengths`), and token-budgeted group packing (`pack_groups`, `make_token_batches`) [^laya-2026-10-02].
- Shipped training metadata is **observed** in the three `rl_agent_config.json` files: English 7,313 updates / 1 epoch / 1.96 h fine-tuned from checkpoint; multilingual 15,987 updates / 4 epochs / 4.97 h from scratch; typed-decisions 7,313 updates with gradient checkpointing and `max_tokens_per_batch` 4096, flagged `fine_tuned: true`[^laya-2026-10-02].
- Encoder configs are **observed**: English and typed-decisions ModernBERT-large (hidden 1024, 28 layers, vocab 50,368, 8,192 max positions); multilingual mmBERT-base (hidden 768, 22 layers, vocab 256,000, 8,192 max positions, RoPE)[^laya-2026-10-02].

## Router and inference controls

- `Router` is the recommended entry point: sub-millisecond script/language detection dispatches English to `english` and non-English to `multilingual`, with full `{model, repo, reason}` metadata per result (README "Quickstart: Route Mode") [^laya-2026-10-02].
- Routing evidence is **reported** on 17,416 shared questions on one T4: Router keeps English MASSIVE 0.783 and XNLI 0.860 while taking multilingual 0.451 on 13 other languages and 0.731 on 14 other XNLI languages, usable in 45–48 of 51 languages versus 23 for English alone; English collapses on non-Latin scripts (Khmer 0.000 accuracy at 0.952 confidence raw), so confidence gating cannot replace pre-pass routing[^laya-2026-10-02].
- Caller controls are **reported**: explicit `model`/`task`/`lang` win, then `lang_guess` code or callable (with `None`/unknown falling through to detection), then built-in detection, then `default` (`english` unless set to `multilingual`); `LAYA_DEFAULT_MODEL` sets the same fallback for servers[^laya-2026-10-02].
- Memory modes are **reported**: lazy default keeps two checkpoints resident (LRU); `max_loaded=1` rebuilds on every switch (~7.4 s CPU, ~10.3 s T4 median); `preload=True` loads all three for 32.8 ms GPU / 193–464 ms CPU per request with no reloads[^laya-2026-10-02].
- Batch and long-document handling are **reported**: `predict_batch` routes first, groups by checkpoint plus schema plus budget, shares forward passes and restores input order; `predict_long` windows with per-type aggregation (`noul` strongest window, `choice`/`score` most-confident window, `usage["windows"]` counting); `predict_shortlist` keeps top-`k` labels by embedding cosine then one forward pass, with `cached_embed_fn` and `option_order` rotations to average position bias[^laya-2026-10-02].
- Abstention is opt-in via `min_confidence` on `answer_confidence`, reporting `abstention` (`passed`/`abstained`/`unevaluated`) and `low_confidence` flags; with no threshold the payload is unchanged[^laya-2026-10-02].
- Token budgets are per call: English `max_len=512` with `head_max_len=192`; multilingual and typed-decisions `max_len=1024` with `head_max_len=256`; multilingual reads to 8,192 with `max_len=8192`; the HTTP server caps 100 choice options per question (413) and rejects over-window requests with 422[^laya-2026-10-02].

## Calibration (observed)

- English ships fitted per-type temperatures `[1.637, 1.251, 1.983]` plus six `temperature_by_options` buckets (e.g. `choice:11+` 0.101, `noul:2` 1.983); typed-decisions reuses the same buckets with near-1.0 per-type values; multilingual ships `[1.0, 1.0, 1.0]` with no buckets, so fit before trusting its probabilities (`rl_agent_config.json`, `eval/results.json`) [^laya-2026-10-02].
- Bucket lookup is **observed** via `rl_common.py::temp_bucket` (`noul:2`, `choice:2/3-5/6-10/11+`, `score:3-5`), applied in `rl_agent_api.py::system_one`; load clamps numeric entries to `[0.5, 5.0]` with neutral 1.0 fallback and raw values kept in `temperature_raw` fields[^laya-2026-10-02].
- Calibration gain is **reported**: refitting one temperature per (type, option count) moves mean ECE 0.466→0.081 (English) and 0.314→0.106 (multilingual); raw base ECE is 0.213 versus Jev 0.144, so the 0.081 comes after domain fitting, not out of box[^laya-2026-10-02].

## Benchmarks and local eval (reported plus observed)

- Speed is **reported** on Tesla T4 for byte-identical questions: 1 question 39.5 ms English / 32.8 ms multilingual; 10 questions 158.6 / 72.3 ms; 50 questions 771 / 337 ms; 103–332 questions/s batched; third-party Jev p50 is 236–276 ms, so ~6–8x faster per single question[^laya-2026-10-02].
- Routed Laya versus third-party Jev is **reported** (Jev figures never measured here, protocols differ): typed-decisions 0.766 vs 0.727 (+0.039, above 0.735 teacher ceiling); AG News 0.950 vs 0.910; DAIR Emotion 0.595 vs 0.480 (Jev zero on true label for 16%); Banking77 0.425 vs 0.870 (Jev leads past ~20 options); ECE 0.081 vs 0.246; 45–48 of 51 languages usable; Apache-2.0 weights versus closed API; $0 self-hosted[^laya-2026-10-02].
- Typed-decisions split is **reported**: fine-tuned checkpoint 0.766 accuracy (invoice 0.804, security 0.766, service 0.764, agent-trace 0.730; `noul` 0.857, `choice` 0.733, `score` 0.723) versus base 0.362/0.342–0.352 below 0.461 majority and near 0.318 random; Jev leads on soft accuracy (0.580 vs 0.471)[^laya-2026-10-02].
- English held-out tasks are **reported**: AG News 0.947, BoolQ 0.830 (in mix); DAIR Emotion 0.573, prompt-injection 0.698 (held out, n=116), SST-5 ordinal 0.372 (weakest)[^laya-2026-10-02].
- Committed local eval is **observed** in `eval/results.json`/`results.md` after calibration: in-task 23,024 questions at accuracy 0.753, ECE 0.030, Brier 0.308 (intent/routing 0.991, moderation 0.967, sentiment 0.442 with ECE 0.438); zero-shot 2,400 at 0.651, ECE 0.204; latency p50 38.4 ms (1q), 156.0 ms (10q), 721.4 ms (50q); act policy automates 100% in this slice[^laya-2026-10-02].

## Honest limits and failure modes

- Base checkpoints are a fast base to specialise, not a zero-shot engine: 0.362/0.352 on typed-decisions versus 0.461 majority; the 0.766 belongs to the checkpoint fine-tuned on that benchmark's own split[^laya-2026-10-02].
- High-cardinality choices share `head_max_len` (192/256 tokens), so 77 options get ~3–4 tokens each; fix by raising `max_len`/`head_max_len`, hierarchical coarse-to-fine choice, or `predict_shortlist` (one reporter: BANKING77 54.3%→60.8% top-20 shortlist, unremeasured here)[^laya-2026-10-02].
- `noul` can follow its `false:`/`true:` labels instead of the state on the English checkpoint; criteria-less `noul` answers "no" regardless of state there; workarounds are explicit `true`/`false` criteria, `labels` remap (e.g. A/B), or a two-option `choice` with neutral keys — validate on served data (issues #156, #377) [^laya-2026-10-02].
- `action.act_probability` carries no signal (1.0 almost always, AUROC 0.30 against correctness on 396 decisions); gate on `confidence` instead (AUROC 0.77); multilingual has `score` position bias (rarely picks first level, #131); avoid boolean-word `choice` keys and negation-sensitive labels without checks[^laya-2026-10-02].

## Email, serving, and fine-tuning

- Email helpers are **observed** in `email_utils.py`: `clean_email_body` strips quoted history, `>` quotes, sign-offs, disclaimers and truncates to 3,000 chars; `email_state` builds `{subject, body, from}`; `email_questions` fans out to category, spam, phishing, urgency, needs-reply and sentiment[^laya-2026-10-02].
- Serving is **reported** as Jev-compatible `POST /v1/systemone` plus 64-state `/v1/systemone/batch` via `laya-serve` (`LAYA_HOST/PORT/DEVICE/PRELOAD/MODELS/THREADS/AUTO_TASK/DEFAULT_MODEL/MAX_LOADED/API_KEY/MAX_TOKEN_BUDGET`), with `laya[serve]` example server, CLI (`--predict/--model/--lang/--lang-guess/--preset/--batch/--questions/--max-len/--head-max-len/--min-confidence/--json`), MCP tools, LangChain/LangGraph/LlamaIndex/CrewAI wrappers, TypeScript `laya-client` over HTTP, ONNX export with per-tensor INT8 default, `laya.evals` gates, and TileLang fast path with `warmup()`[^laya-2026-10-02].
- Fine-tuning is **reported** as the accuracy path: Kaggle 2xT4 notebook plus Apple-Silicon MPS script (build dataset, RLCD train, fit temperatures, evaluate, push to Hub; ~4–5 h on 2xT4 for 4 epochs over ~30k questions), with temperature-persistence fix (fit per-type, drop inherited buckets) and a browser-agent worked example moving element top-1 0.10→0.66 and task success 0%→62% at 17–23 ms/step[^laya-2026-10-02].

## Relationships

- Details the technical system behind [Laya Prior-Art Claim and Jev-Equivalence Dispute](laya-prior-art-claim.md) prior-art and benchmark-caveat discussion.
- Implements decisions for [Jev Decision Model](jev-decision-model.md) as an open multilingual comparator.
- Uses [Jev API Patterns](jev-api-patterns.md) typed `choice`/`score`/`noul` interface with Laya's marker-scoring mechanics.
- Uses [Classifier Calibration](classifier-calibration.md) per-bucket temperature mechanism.
- Informs [Classifier Selection](classifier-selection.md) fine-tune-versus-buy and shortlist-versus-large-option choices.

## Coverage limits

- Static inspection only: three `rl_*.py` plus `email_utils.py` compile (`py_compile` passes); no model runs, training, downloads, or latency remeasurement were performed.
- Inspected: `README.md`, `README-GITHUB.md` prose and tables, three `rl_agent_config.json`, three `encoder/config.json`, three `tokenizer_config.json`, `eval/results.md` plus `eval/results.json`.
- Excluded with reason: `model.safetensors` weights absent (Git-LFS pointers only); `tokenizer/tokenizer.json` and `typed-decisions/tokenizer/tokenizer.json` (~3.5 MB each) and multilingual LFS pointer unparsed as vocab dumps; `assets/` and `eval/*.png` binary/plots covered via captions and surrounding tables, not pixel inspection.
- Unavailable here: linked `BENCHMARKS.md`, notebooks, `docs/`, `research/`, `examples/`, `laya-ts/`, SDK sources, Hub repos/demos, issue threads (#102/#131/#156/#185/#377/#394/#649/#812), and external benchmark links; Jev figures are third-party published with different samples/prompts, so do not rank Laya headlines against Jev without protocol alignment.
- No credentials, keys, tokens, or PII were found; `token`/`tokenizer` hits are tokenizer fields, and `YOUR_API_KEY`-style placeholders are not live secrets.
- Freshness: runtime 0.3.21–0.3.23 notes and `max_len=8192` long-document table describe this snapshot; verify flags and limits against live docs before building.

[^laya-2026-10-02]: Convai Innovations, "Laya," Hugging Face model card plus code bundle, canonical local entry `../raw/laya/README.md`, package scope `../raw/laya/`, upstream `https://huggingface.co/convaiinnovations/laya` with GitHub `https://github.com/NandhaKishorM/laya`. Locators in text: `README.md` (identity, quickstart, router evidence, architecture, training, speed and Laya-vs-Jev tables, typed-decisions table, honest limits); `README-GITHUB.md` (installation, CLI, server/MCP/evals, decision primitives and `option_order`, shortlist, calibration clamp, honest limits, fine-tuning); `rl_common.py::DecisionModel/build_sequence/render_options/proper_reward/td_lambda_targets/confidence_from_probs/temp_bucket`; `rl_agent_api.py::RLAgent.system_one`; `email_utils.py::clean_email_body/email_state/email_questions`; `rl_agent_config.json` plus `multilingual/rl_agent_config.json` plus `typed-decisions/rl_agent_config.json`; `encoder/config.json` trio; `eval/results.md` plus `eval/results.json`.
