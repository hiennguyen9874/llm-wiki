---
type: Concept
title: 'Kev Decision Models: Open Self-Hostable Jev-Compatible Family'
description: Apache-2.0 Jev-compatible decision-model family from 0.8B to 27B with fitted-temperature calibration, question isolation, fine-tune skill, and self-hosted serving.
tags: [kev, decision-models, open-weights, calibration, fine-tuning]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T15:00:00Z }
sources:
  - id: kev-readme-2026
    resource: ../raw/kev.md
    kind: documentation
    title: Kev
---

# Kev Decision Models: Open Self-Hostable Jev-Compatible Family

Synthesis: Kev is Jared Palmer's Apache-2.0 family of small Jev-like decision models on Qwen bases with a TypeSafe System One-compatible API, per-question isolation, shipped temperatures for calibrated probabilities, and a 0.8B-to-27B range from laptop to datacentre GPU; use the owner's reported numbers for self-host selection and fine-tune planning, not as independent verification[^kev-readme-2026].

## Identity and family

- Family of small decision models built on Qwen3.5 and Qwen3.8 and based on the architecture in Jev's Architecture Unmasked; pretrained weights or own training both supported[^kev-readme-2026].
- API matches TypeSafe System One, so the TypeSafe Python SDK works against a Kev server unchanged[^kev-readme-2026].
- Four sizes released together as Kev 1.0, from 0.8B on a laptop to 27B for a single datacentre GPU; documents up to 65,536 tokens on CUDA and Apple Silicon via MLX, with per-model validated length before accuracy drops[^kev-readme-2026].
- License is **reported** Apache-2.0; Qwen3, Qwen3.5 and Qwen3.8 bases are also **reported** Apache-2.0 with training datasets under their own licenses[^kev-readme-2026].
- Highlights are **reported**: yes/no (`noul`), multiple-choice (`choice`) and rating (`score`) in one request sharing the text but unable to read each other; calibrated probabilities by default; browser demo on Hugging Face Spaces[^kev-readme-2026].

## Models and owner-reported accuracy

- Start guidance is **reported**: start with Kev-4B; move to 9B with a bigger GPU or 27B with an 80 GB GPU for most accuracy; use 0.8B when size matters more than accuracy[^kev-readme-2026].
- Model table is **reported** (Models section)[^kev-readme-2026]:
  - Kev-0.8B on Qwen3.5-0.8B-Base; CUDA L4 / any 4 GB GPU; any Apple Silicon Mac measured to 65k tokens; validated context 8,192; held-out index 23.3.
  - Kev-4B on Qwen3.5-4B-Base; CUDA L40S/H100; 32 GB Mac measured to 65k; validated context 8,192; held-out index 38.0.
  - Kev-9B on Qwen3.5-9B-Base; CUDA L40S/H100; 32 GB Mac or larger expected not measured; validated context 8,192; held-out index 41.0.
  - Kev-27B on Qwen3.8-27B post-trained; CUDA B200/H200/H100 80 GB; 96–128 GB Mac expected not measured; validated context 65,536; held-out index 52.3 versus Jev 54.0.
- Held-out datasets means **reported** chance-corrected community Decision Index on `breadth-v1` test split: 14 public datasets in five areas no Kev trained on; validated context means **reported** longest document in tokens for which CUAD real-contract accuracy stays within 3 points of 8k accuracy at the 95% lower bound[^kev-readme-2026].
- New-vs-trained accuracy is **reported** as development / test (Models second table)[^kev-readme-2026]:
  - Kev-0.8B: new 0.648/0.697, trained 0.827/0.838, Brier new 0.481/0.416.
  - Kev-4B: new 0.817/0.838, trained 0.873/0.865, Brier new 0.269/0.242.
  - Kev-9B: new 0.820/0.852, trained 0.874/0.873, Brier new 0.289/0.217.
  - Kev-27B: new 0.851/0.889, trained 0.865/0.866, Brier new 0.225/0.156.
  - Jev: new 0.857/–, trained 0.845/–, Brier new 0.211/–.
- New sources means **reported** datasets and policy rules Kev never saw during training, framed as closest to own questions; trained sources means held-out examples from training datasets; checkpoints picked on development sets with each test set read once per released model; Jev run only on development sets of these two suites[^kev-readme-2026].
- **Synthesis**: on new sources Kev-27B is within a point of Jev and 4B/9B within about four points in this owner report, but the author notes Jev training data is unknown so this is not a controlled architecture comparison[^kev-readme-2026].
- What-to-expect gaps are **reported**: Kev-27B within three points of or ahead of Jev on 9 of 11 new-source categories; 4B/9B about as close on classification-shaped routing/entailment/science; knowledge questions follow the base model with MMLU Kev-9B 0.73 and Kev-27B 0.90 matching Jev, but MMLU-Pro Kev-27B 0.675 versus Jev 0.840; smaller models trail on day-precision date arithmetic[^kev-readme-2026].

## Kev 1.0 pinning

- Kev 1.0 trains nothing new; it fixes checkpoints, cards, suites and serving code for future comparison, with `v1.0` Hub tags and GitHub `kev-1.0` release holding 0.8B/4B/9B checksums while 51 GB 27B weights are Hub-only[^kev-readme-2026].
- Pinned revisions, temperatures and training lengths are **reported** (Kev 1.0 table)[^kev-readme-2026]:
  - 0.8B `9a45d25e`, T=2.35, states to 7,552 tokens.
  - 4B `139fdd94`, T=2.41, states to 7,552 tokens.
  - 9B `b5d8c18e` (v2), T=2.19, states to 7,552 tokens.
  - 27B `28be62e9` (v2 full weights), T=1.32, states to 32,768 tokens.
- 0.8B/4B/9B start from Qwen base models with one shared recipe: small adapter on frozen base; 27B starts from Qwen post-trained release of unknown training data with every weight fine-tuned, shipping as 51 GB full weights rather than adapter[^kev-readme-2026].

## API and question isolation

- `state` is the text to evaluate; each question has instructions and where needed answers to choose from; one request may carry any number of questions[^kev-readme-2026].
- Types are **reported** (API table)[^kev-readme-2026]: `noul` answers probability of yes; `choice` answers most-likely option plus probabilities and confidence over 1–255 options; `score` answers mean level index from 0 plus legend, probabilities and confidence over 1–255 ordered levels.
- Confidence formulas follow TypeSafe reference adapter 0.2.1 and are **reported** as distribution statistics, not measured accuracy rates: Choice `(p_max − 1/K)/(1 − 1/K)`; Score `max(0, 1 − E|level − mode|/D)` with uniform spread giving 0[^kev-readme-2026].
- Server runs questions a token budget at a time (one maximal 16,384-token row per forward pass, counting cached document once per question in that pass), so memory does not grow with question count and answers do not depend on the split; every response carries `x-typesafe-request-id`[^kev-readme-2026].
- Limits are **reported**: server accepts states to 65,536 tokens plus 8,192 per question and refuses longer ones with 422 instead of silent truncation; objects/arrays become labeled text; delimiter-like input is escaped; `usage.output_tokens` counts serialized answers, not generated tokens[^kev-readme-2026].
- Endpoints are **reported**: `GET /v1/models`, `POST /v1/systemone`, `POST /v1/systemone/permute` (1–64 orders, default 6), `POST /v1/systemone/separate` (each question alone)[^kev-readme-2026].
- Environment overrides are **reported**: `KEV_TEMPERATURE=1.0` for raw probabilities; `KEV_DATE_FACTS=1` to append day counts between dates; `KEV_TRUNCATE_STATES=1` to read first 65,536 tokens with `truncated` plus token-use fields; `KEV_DTYPE=fp32` for eval-exact path; `KEV_API_KEY` to require bearer on `/v1/*`[^kev-readme-2026].

## Architecture

- Each checkpoint is **reported** as rank-16 LoRA adapter plus small pointer head on a Qwen base, except 27B full weights; training uses cross-entropy on the correct answer with adapter plus head together and base frozen (27B trains all); no Jev outputs used for training[^kev-readme-2026].
- Sequence is **reported** as `<state> …state… <q> instructions <opt> option … </opt> … <decide>` per question with mask letting a token read the state and its own question but not other questions or future tokens, and position IDs restarting after the state so the state is processed once[^kev-readme-2026].
- Qwen3.5/3.8 Gated DeltaNet layers are recurrent and ignore attention masks, so every current Kev runs each question as its own row (state plus that question) with isolation exact and state cache reused; `forward()` keeps plain rows and runs state once per question while server and `DecisionModel.probs()` reuse the cache, agreeing to fp32 rounding[^kev-readme-2026].
- Pointer head scores each option `</opt>` hidden state against its `<decide>` state with softmax into probabilities; `<decide>` comes last so it can attend the full option list[^kev-readme-2026].
- Parity notes are **reported**: packed versus separate within 4e-6 in fp32 tests, but option order can still change an answer; served bf16 versus fp32 eval path differs by at most about 0.03 on GPU and 0.05 on Mac with top answer changing about 1 in 300[^kev-readme-2026].

## Training and fine-tuning on own data

- Base training set `decision-v7` is **reported** as 10,000 examples from ten public datasets plus 896 generated policy examples plus 1,680 examples from 60 generated rule structures; 0.8B/4B/9B train two epochs LoRA rank 16 with lr `1e-4` for 0.8B and `5e-5` for 4B/9B, adapter covering attention/MLP/DeltaNet projections[^kev-readme-2026].
- Follow-ups from released checkpoints via `--init_from` add stated-day-count or evidence-removed cases plus real documents and skill data; 27B fine-tunes every weight one epoch on eight H200s (`--full_ft 1`, lr `2e-6`) on a 145,840-record corpus to 32,768-token states, then averages 0.85/0.15 with the earlier adapter 27B[^kev-readme-2026].
- Fine-tune JSONL shape is one request per line plus per-question `label`: Choice option name, noul boolean, score zero-based level index; keep 10–20% for evaluation; start from released checkpoint with `--init_from` to keep prior knowledge[^kev-readme-2026].
- `--init_from` lesson is **reported**: starting from base instead throws away prior knowledge, scoring 0.33 on Kev's own eval versus 0.84 for the released model in one 836-decision test, while `--init_from` kept 0.83 there and reached 0.88 on the new domain; use smaller lr such as `2e-5` and matching `--base` with rank/head checks[^kev-readme-2026].
- Gains are **reported** as in-distribution only: example support workload (3 questions, 1,050 generated records, 15 min H100) took 4B 67.7%→73.6% and 34%→48% automation at 5% error budget, while 400 records stayed inside noise; real 5,219-label consumer-finance complaints took 4B 0.804→0.904 on unseen complaints[^kev-readme-2026].
- Two routes are **reported**: coding-agent `kev-finetune` skill (`npx skills add jaredpalmer/kev@kev-finetune`) that interviews, finds Jev/TypeSafe questions, labels or generates data, trains on Modal, fits temperature on held-out slice, scores versus untouched model, deploys and tears down for about $1 per 4B H100 run; or by-hand six-script plus one-Modal-app recipe with `kev.train`, `kev.benchmark` and `kev.serve` commands[^kev-readme-2026].

## Evaluation, calibration and serving

- Frozen suites are **reported** (Benchmarks table): `decision-v7` for trained sources, `transfer-v4` (764 records: QNLI, SciQ, PAWS, MMLU, Emotion, TweetEval plus held-out policies/rules) for new sources, `transfer-v9` adding 10-way MMLU-Pro, buried-in-text and unknowable evidence-removed records; manifests record versions/checksums with Hub mirror and CI `docs/claims.json` verification[^kev-readme-2026].
- Calibration is **reported**: each checkpoint stores a temperature applied on load; 4B/0.8B fitted on in-distribution dev (refit on held-out tested and kept neither), 9B/27B on held-out never-trained sets; temperature never changes the winner; 9B ECE 0.103→0.041 on new sources with confident errors (≥0.9 wrong) 8.2%→2.4% below Jev 3.7%; published Brier uses raw probabilities[^kev-readme-2026].
- Confidence-use numbers are **reported**: at 5% error budget 4B/9B/27B automate 0.52–0.69 of new-source decisions versus 0.14 for 0.8B and 0.70 for Jev; on unknowable records 9B still answers ≥0.9 on 0% versus Jev 9%; check thresholds on own data[^kev-readme-2026].
- Dates are **reported**: Kev cannot subtract dates reliably but can use a given day count; `KEV_DATE_FACTS=1` takes 9B 0.80→0.90 on deadline-policy questions versus Jev 0.93; no tables use it[^kev-readme-2026].
- External SemIf check is **reported** as 144 authored decisions with Jev 0.965 versus Kev-9B 0.917 at `v7-base`, read as near-saturated sanity check since every 27B checkpoint gets 130/144; three other external sets were removed as gates with reasons in model cards (templated support tickets, WANLI annotator disagreement, TypeSafe averaged-frontier gold)[^kev-readme-2026].
- Local run is **reported**: Python 3.12/3.13 plus `uv`, `uv sync --extra serve`, `python -m kev.serve --run jaredpalmer/kev-4b --port 8009` with CUDA/ROCm or Apple MLX and first-run adapter plus base download[^kev-readme-2026].
- Modal HTTPS deploy is **reported** as `pip install modal && modal setup` plus `kev_serve.py` with `KEV_API_KEY`, serving 4B on L40S scale-to-zero with ~35 s cold start and ~65 ms same-region network extra; `KEV_MODEL` selects another model with 27B on B200 falling back to H200/H100; agent `kev-deploy` skill wires URL into code; own-machine hosting is `kev.serve --host 0.0.0.0` behind own proxy[^kev-readme-2026].
- GPU model times are **reported** medians of 20 (new / cached text): 0.8B L4 22.7/16.1 ms short and 108.6/32.3 ms at 2,200 tokens with 62.8 req/s; 4B L40S 41.5/27.7 and 145.2/43.0 with 51.4 req/s, H100 18.1/12.9 and 89.4/22.5 with 100.8 req/s; 9B L40S 66.4/42.7 and 235.6/57.5 with 32.7 req/s, H100 24.0/16.6 and 88.5/26.4 with 79.5 req/s; 27B B200 46.5/32.2 and 178.0/52.1 with 44.2 req/s, H200 67.2/50.0 and 274.8/73.8 with 28.6 req/s, H100 75.0/52.0 and 277.5/79.3 with 28.9 req/s[^kev-readme-2026].
- Mac MLX times for ~270-token five-question text on M5 32 GB are **reported**: 0.8B 149 ms new / 28 ms cached; 4B 721 ms / 136 ms; long 65k-document cache fills 1,024 tokens at a time with 0.8B 21.2 s then 202 ms at 3.8 GB peak and 4B 84.5 s then 716 ms at 13.0 GB[^kev-readme-2026].
- Memory notes are **reported**: 9B needs about 17 GB GPU; 27B 51 GB weights about 66 GB with batching buffers and compute-bound per-request cost similar across B200/H200/H100; adapter fold briefly holds second weight copy while full-weight 27B loads as saved (4B full-write peaked 8.4 GB for 8.4 GB weights versus 15.9 GB adapter path with exact match once bf16-equal and within 0.015 of fp32 on 60 questions); 27B on Mac needs about 51 GB plus working memory so 64 GB borderline and 96–128 GB expected but unmeasured[^kev-readme-2026].

## Limitations

- Single-temperature calibration cannot reorder confidences, leaving new-source automation at 5% error (0.52–0.69 for 4B/9B/27B) below Jev 0.70; test thresholds on own data[^kev-readme-2026].
- Knowledge questions follow the base model: MMLU 0.73 for 9B versus Jev 0.90 and MMLU-Pro 0.59 versus 0.84 in Limitations wording[^kev-readme-2026].
- Fine-tuning can worsen individual tasks with date arithmetic as clearest case; stated-day-count training plus `KEV_DATE_FACTS=1` recovers it[^kev-readme-2026].
- Option-order changes can change an answer despite question isolation; Mac answers take hundreds of milliseconds; 27B needs 80 GB GPU or about 51 GB plus working memory on Mac; 0.8B/4B/9B trained mostly to 384 state tokens (1,024 state-plus-question, document/skill follow-ups to 7,552) and 27B to 32,768 while serving allows 65,536, so respect validated-context column; 27B post-trained base training data is unknown[^kev-readme-2026].
- Previous generation (Qwen3 0.6B/4B/8B) and Qwen2.5-0.5B prototype stay published but are no longer developed, with first-family table and model-card pointers kept for reference[^kev-readme-2026].

## Relationships

- Implements decisions for [Jev Decision Model](jev-decision-model.md) as an open self-hostable comparator.
- Uses [Jev API Patterns](jev-api-patterns.md) System One shapes with Kev isolation and confidence details.
- Uses [Classifier Calibration](classifier-calibration.md) fitted-temperature mechanism.
- Informs [Classifier Selection](classifier-selection.md) build-vs-buy and self-host choices.

## Coverage limits

- All model, accuracy, calibration, speed and cost figures above are **reported** owner README values, not reproduced here; no code execution, API calls, weight downloads or benchmark reruns were performed.
- Linked model cards, Hub revisions, release notes, skill READMEs, eval manifests and `runs/*` measurement logs were not inspected; treat per-length CUAD, fine-tune cost and cold-start figures as unreproduced.
- Playground, chess demo, Modal apps, training commands and GPU/Mac tables are **reported** procedures and point measurements; verify current flags, prices and availability before building.
- No credentials, keys, tokens or PII were found; example `api_key="local"` and `KEV_API_KEY` variable name are not live secrets.

[^kev-readme-2026]: Jared Palmer, "Kev," canonical local entry `../raw/kev.md`, upstream `https://github.com/jaredpalmer/kev`. Locators in text: Highlights; Models tables; Kev 1.0 table; Quick Start; Fine-Tune on Your Own Data; Deploy Your Own Endpoint; What to Expect; Playground; API; How It Works; Training; Benchmarks; Serving Performance; Limitations; Previous generation detail.
