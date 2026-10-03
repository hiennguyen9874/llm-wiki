---
type: Concept
title: 'Jev API Patterns: Choice, Noul, and Score'
description: The three Jev decision APIs, their request and response shapes, when to use each, and the single-head retrofit for DIY clones.
tags: [jev, api, classification]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T23:45:00Z }
sources:
  - id: jev-9b-v08
    resource: ../raw/JEV-9B/README.md
    scope: ../raw/JEV-9B/
    kind: model-card
    title: autotrust/JEV-9B
  - id: raschka-jevl-2026-09-29
    resource: ../raw/classifier-history-and-jev/index.md
    scope: ../raw/classifier-history-and-jev/
    kind: article
    title: 'Language Models for Text Classification: From Bag-of-Words to Jev'
  - id: jev-27b-2026-10-01
    resource: ../raw/JEV-27B/README.md
    scope: ../raw/JEV-27B/
    kind: model-card
    title: autotrust/JEV-27B
  - id: jev-style-v3-gguf-2026
    resource: ../raw/Jev-Style-0.8B-Decision-v3-GGUF/README.md
    scope: ../raw/Jev-Style-0.8B-Decision-v3-GGUF/
    kind: model-card
    title: Jev-Style-0.8B-Decision-v3-GGUF
  - id: jev-style-2b-v1-gguf-2026
    resource: ../raw/Jev-Style-Qwen3.5-2B-Decision-GGUF/README.md
    scope: ../raw/Jev-Style-Qwen3.5-2B-Decision-GGUF/
    kind: model-card
    title: Jev-Style-Qwen3.5-2B-Decision-GGUF
  - id: jev-omni-2026
    resource: ../raw/Jev-Omni/README.md
    scope: ../raw/Jev-Omni/
    kind: model-card
    title: akhilaaa3/Jev-Omni
  - id: julia-1-2026-09-24
    resource: ../raw/Julia-1/README.md
    scope: ../raw/Julia-1/
    kind: code
    revision: df853bf7fe424420011f3d0c47a05d7341aa9eefa7fb9f203ea4aada4ad95b72
    title: Julia 1
  - id: neohorse-jev-4b-2026-09-24
    resource: ../raw/NeoHorse-Jev-4B/README.md
    scope: ../raw/NeoHorse-Jev-4B/
    kind: model-card
    revision: 1.0.0
    title: NeoHorse-Jev-4B
  - id: semif-2026-09-22
    resource: ../raw/SemIf-OpenJev.md
    kind: code
    title: SemIf (formerly OpenJev)
  - id: clef-flash-2026
    resource: ../raw/clef-flash/README.md
    scope: ../raw/clef-flash/
    kind: model-card
    title: Cloudflare/clef-flash
  - id: clef-2026
    resource: ../raw/clef/README.md
    scope: ../raw/clef/
    kind: model-card
    title: Cloudflare/clef
  - id: kev-readme-2026
    resource: ../raw/kev.md
    kind: documentation
    title: Kev
  - id: bespoke-nimble-2026-09
    resource: ../raw/nimble.md
    kind: documentation
    title: Bespoke Nimble
  - id: openjev-2026
    resource: ../raw/openjev-openjev/README.md
    scope: ../raw/openjev-openjev/
    kind: model-card
    title: OpenJev
  - id: openjev-sglang-2026
    resource: ../raw/openjev-sglang.md
    kind: documentation
    title: openjev-sglang
  - id: reddit-pi-jev-2026-09-30
    resource: ../raw/pi-now-supports-jev/index.md
    scope: ../raw/pi-now-supports-jev/
    kind: thread
    title: 'Pi now supports Jev.'
  - id: razorback16-openjev-2026
    resource: ../raw/razorback16-openjev.md
    kind: documentation
    title: OpenJev
  - id: von-2026
    resource: ../raw/von.md
    kind: documentation
    title: Von
---

# Jev API Patterns: Choice, Noul, and Score

Synthesis: use Choice for one-answer multi-class, Noul yes-probabilities for binary or multi-label, and Score for ordinal rubrics; all share a state plus instructed questions pattern, and the same idea retrofits onto BERT/GPT via one shared scalar scoring head (§3.2–§4)[^raschka-jevl-2026-09-29].

## Common invocation

- Endpoint pattern: `POST https://api.typesafe.ai/v1/systemone` with model such as `jev-1.13.0`, a `state` text, and a `questions` map; curl and Python clients shown (§3.2–§3.3)[^raschka-jevl-2026-09-29].
- Auth in examples uses placeholder `TYPESAFE_API_KEY="YOUR_API_KEY"` — no live credential is stored here (§3.3)[^raschka-jevl-2026-09-29].
- Usage accounting returns `input_tokens` and `output_tokens` per call (§3.3)[^raschka-jevl-2026-09-29].

## Choice API

- Purpose: multi-class or binary task needing exactly one answer (§3.2, Figs. 25, 28)[^raschka-jevl-2026-09-29].
- Request: per question supply `type: choice`, `instructions` (e.g. “What is overall sentiment?”), and `criteria` mapping each label to its description (e.g. negative vs positive) (§3.3)[^raschka-jevl-2026-09-29].
- Response: `choice` label plus `confidence` and per-class `probabilities`; confidence summarizes distribution concentration and differs from winning-class probability; documented as well-calibrated (see calibration concept) (§3.3)[^raschka-jevl-2026-09-29].

## Noul API

- Purpose: binary yes-probability; ask one Noul question per class for multi-label where probabilities need not sum to 1, e.g. finance, politics, technology article tags (§3.2–§3.3, Figs. 26, 28)[^raschka-jevl-2026-09-29].
- Request: `type: noul` with `instructions` (e.g. “Does this review express positive opinion?”) and `true`/`false` criteria descriptions (§3.3)[^raschka-jevl-2026-09-29].
- Response: `noul` scalar such as 0.98 for the same review Choice scored 1.0 positive; prefer Choice when exactly one final label is wanted (§3.3)[^raschka-jevl-2026-09-29].

## Score API

- Purpose: ordinal classification against rubric levels, e.g. 0, 1, 2 (§3.2, Figs. 27–28)[^raschka-jevl-2026-09-29].
- Rule of thumb: Choice for single answer, Noul for independent yes/no or multi-label, Score for graded levels (Fig. 28)[^raschka-jevl-2026-09-29].
- Local self-hosted variant: [JEV-27B System 1 Decisions and Blocks-of-Experts Serving](jev-27b-system1-decisions.md) serves the same three kinds over HTTP via `POST /v1/decide` (`{kind,state,question,options}` → calibrated per-option probabilities), with `choice` extended to 2–256 options in one pass (`native` ≤16, `wide-labels` beyond) and measured prompt rules (facts in `state`, one `choice` over per-candidate yes/no, one-line `use when` per similar option)[^jev-27b-2026-10-01]. The 9B first generation serves the same three kinds with `choice` limited to 2–16: one vLLM prefill (`max_tokens=1`, `allowed_token_ids`, log-probs plus head bias over temperature) or a plain `transformers`+`peft` head-only path; see [JEV-9B](jev-9b-system1-decisions.md)[^jev-9b-v08].
- Independent multimodal variant: [Jev-Omni Multimodal Decision Classifier](jev-omni-multimodal-decisions.md) exposes `predict(state, question, options, media, modality)` → `{prediction, prediction_index, confidence, probabilities}` for 2–256 options across text/image/audio/video (16 video frames, 30 s audio cap); **observed** single numbered-option prompt plus 256-logit masked head and per-option softmax, implementing noul/choice/score semantics without the hosted endpoint shapes[^jev-omni-2026].
- Independent on-device variant: [Jev-Style-0.8B Decision v3 GGUF](jev-style-0.8b-decision-v3-gguf.md) implements choice/score/noul via verdict readout (`logit(" yes")-logit(" no")` at one ` ->` slot per option) with 25,600-token inputs, 2,048-token heads, token-balanced option chunks for over-budget lists, and `decide` / `decide_many(exact|batched)` over a `jev-score` slot-logit server[^jev-style-v3-gguf-2026].
- Independent letter-readout predecessor: [Jev-Style-2B Decision v1 GGUF](jev-style-2b-decision-v1-gguf.md) implements choice/bool/score via a single option-letter token renormalised from `top_logprobs`, with the calibration temperature folded into the final RMSNorm weight; up to 26 options by letter (20 through server `top_logprobs`), stdlib-only `decide`/`decide_bool`/`decide_score` over `/v1/chat/completions`, and LM Studio/llama.cpp serving[^jev-style-2b-v1-gguf-2026].
- Independent local encoder-head variant: [Julia 1](julia-1-decision-model.md) exposes the same choice/noul/score semantics through a resident `predict(state=..., questions=...)` named-question API plus a legacy `predict([{state, question, options, type}])` list API; **observed** 2–20 native options with per-option `[MASK]` scoring, strict encoding with 48-token option and 8,192-token combined limits, full-softmax named answers versus display-collapsed legacy probabilities, and hierarchical choice routing to 4,096 options with final-only conditional probabilities[^julia-1-2026-09-24].
- Independent unified-backbone variant: [NeoHorse-Jev-4B](neohorse-jev-4b-decision-model.md) serves the same three kinds via native `POST /v1/decision` plus System One-style `POST /v1/systemone` over `DecisionEngine.predict({state, questions})` with up to 16 text questions per request, single-image single-question vision, and HTTP-added local-statistic `confidence`; **observed** 2,048-token state, 8,192-token branches, 32,768-token expanded cap, and System One Score limited to 2–10 levels[^neohorse-jev-4b-2026-09-24].
- Independent no-training direct-logit variant: [SemIf Open Decisions](semif-open-decisions.md) reproduces the runtime-criteria plus typed-options pattern with one forward pass reading declared option logits and no answer sampling; **reported** `{id, state, question, options}` input where `state` may be text or nonempty JSON, shared-state prefill reuse across criteria, per-row scores plus timing/revision/prompt-hash, and per-workload temperature calibration applied downstream[^semif-2026-09-22].
- Cloudflare joint-schema variant: [Clef-Flash Multimodal Joint-Schema Decisions](clef-flash-multimodal-decisions.md) scores all options of all questions jointly in one pass via `encode_record` plus `collate_records` and answers Jev/SystemOne `POST /v1/systemone` bodies through `systemone`; **observed** `state` plus `questions` record with `noul`/`choice`/`score` types, `instructions` defaulting to question ID, per-type `criteria` shapes, `max_length` 16384 default with schema-size guard and state truncation, and `systemone_answer` mapping to `noul`/`choice` with `confidence`+`probabilities` or `score` with expected `score`+`confidence`+`legend`[^clef-flash-2026]. The larger sibling [Clef Multimodal Joint-Schema Decisions](clef-multimodal-decisions.md) shares byte-identical decision code with a 5120-wide head on Qwen3.8-27B and the same `systemone` shapes via `snapshot_download("Cloudflare/clef")`[^clef-2026].
- Self-hostable System One-compatible variant: [Kev Decision Models](kev-decision-models.md) exposes TypeSafe-compatible `POST /v1/systemone` plus `permute`/`separate` and `GET /v1/models`; **reported** 65,536-token state plus 8,192 per question with 422 refusal, per-question isolation with 16,384-token rows, TypeSafe-adapter confidence formulas, and `KEV_TEMPERATURE`/`KEV_DATE_FACTS`/`KEV_TRUNCATE_STATES`/`KEV_DTYPE`/`KEV_API_KEY` overrides[^kev-readme-2026].

- Open flat-schema variant: [Bespoke Nimble](bespoke-nimble-decision-model.md) takes context plus a flat schema of enum (1–255 choices, latest) or boolean fields; **reported** each answer maps to one token code scored from logits with softmax, `scorer.score(context, schema)` returns typed output plus per-field scores/logits, fields are scored independently with no cross-field visibility, and ordered scales support expected-level math[^bespoke-nimble-2026-09].
- Open-weights Jev-compatible variant: [OpenJev](openjev-decision-model.md) serves hosted-shaped `POST /v1/systemone` (`{model, state, questions}` → typed `answers` plus `usage`) from vLLM plus a frozen helper; **observed** one forward pass per question over up to 52 lettered options (`A–Z`/`a–z`, chunked above 52), `READOUT_TARGETED=1` exact scores, `T=0.85` / noul `1.829074,0.0` / `pyrepr` instruction style, 16,384-token / one-image limits, and `GET /v1/version` / `POST /v1/prewarm` / chat pass-through routes[^openjev-2026].
- SGLang Jev-compatible variant: [OpenJev-SGLang Decision Serving](openjev-sglang-decision-serving.md) serves the same three kinds over `POST /v1/systemone` from Qwen3.6-35B-A3B on SGLang 0.5.19; **reported** N+1 one-token calls per request (shared-prefix warmup plus one branch each), `token_ids_logprob` with `logprob_start_len=-1`, up to 64 letter-combination labels (`A–Z` then `AA`, `AB`, …) verified at startup, and text-only chat-template state handling[^openjev-sglang-2026].
- Open-encoder SystemOne-compatible variant: [Von](von-decision-model.md) serves `POST /v1/systemone` with `decide`/`judge`/`rate` plus multi-question `system_one` in one forward pass; **reported** `band` versus `raw` Noul control, 8192-token middle-truncation with `truncation` field and 422 `refuse` mode, real `usage.input_tokens`, and `confidence_gate(threshold=0.80)` splitting `automatic`/`escalate`[^von-2026].
- Diffusion-canvas Jev-compatible variant: [OpenJev Diffusion Decision Server (razorback16)](openjev-diffusion-decision-server.md) serves the same three kinds over `POST /v1/systemone` by reading one masked label token per question from a DiffusionGemma 26B-A4B canvas in a read-only pass; **reported** `yes`/`no`, `A`/`B`/`C`, `0`/`1`/`2` single-token labels, `1 − H(p)/ln K` confidence, ~12-question parallel chunks with entropy-triggered re-reads, plus `images`/`steps`/`samples`/`think`/`sequential` extensions and routed `laya-1.0`/`verdict-1.4`/`clm-v0.1`/`jevk5-0.2` models[^razorback16-openjev-2026].

## DIY single-head retrofit

- Idea: replace BERT/GPT/T5 output with one scalar head shared across candidates instead of fixed N-way head (Fig. 31) (§4)[^raschka-jevl-2026-09-29].
- Forward pass: for each candidate, feed input text plus task instructions plus that candidate’s description; head maps pooled representation `h_i` to scalar `s_i`; softmax over N scalars gives distribution; argmax is the Choice answer (Fig. 32) (§4)[^raschka-jevl-2026-09-29].
- Pooling: BERT uses final `[CLS]` state (optionally pooled); autoregressive GPT uses last non-padding token because only it attends to all prior context (§4)[^raschka-jevl-2026-09-29].
- Training: jointly fine-tune backbone and shared head with cross-entropy against correct option; shared weights allow changing number and wording of options without architecture change; generalization to unseen tasks depends on training-data breadth (§4)[^raschka-jevl-2026-09-29].
- Why transformers: scale to large pre-training and exploit in-context instruction plus candidate text via attention better than RNN/CNN; method still works mechanically on RNN/CNN (§4)[^raschka-jevl-2026-09-29].
- Author note: built an unreleased ModernBERT Jev-like to show API retrofit is trivial while broad task quality is not (§4)[^raschka-jevl-2026-09-29].
- Pi 0.99.0 wire-format reuse is **observed** via commenter static inspection of a local install (not reproduced here): `pi-ai/dist/api/llama-cpp-classify.js:144` implements TypeSafe-documented choice confidence `(n * peak - 1) / (n - 1)` clamped to [0, 1] via `peakConfidence(probabilities)`; `pi-ai/dist/api/system-one-shared.js:108` maps public `bool` questions to wire-level `noul`; `pi-coding-agent/docs/llama-cpp.md:91` frames classifiers as answering typed choice/bool/score questions about JSON state "like TypeSafe's Jev models"; parsing parity is **reported** as choice → `choice`/`probabilities`/`confidence` and score → `score`/`confidence` on both paths, with bool diverging as `noul` → `probability` (Jev path) versus direct `probability` (llama.cpp path)[^reddit-pi-jev-2026-09-30].
- Generalization dispute is **reported**: one side reads the above plus Jev-named docs as "all about jev, nothing general," another holds Pi intends classifiers in general not just Jev and asks what alternative wire format should be used instead, and a third holds first-mover inheritance is how standards form (JSON, OpenAI API format) so Jev-shaped interop is expected; the Pi maintainer **reports** many Jev alternatives plus Jev-API-mirroring providers and OpenAI's Decision API fitting the same scheme, expecting classifier-API evolution as happened with chat-model mid-conversation system messages and tool-set changes — **synthesis**: treat Pi's current classifier API as Jev-compatible-first with claimed generality, not proven generality[^reddit-pi-jev-2026-09-30].

## Relationships

- Implements decisions for [Jev Decision Model](jev-decision-model.md).
- Uses [Classifier Calibration](classifier-calibration.md) for interpreting confidence and probabilities.
- Uses [Text Classification Lineage](text-classification-lineage.md) backbone heads it generalizes.
- Informs [Classifier Selection](classifier-selection.md) clone effort estimates.

## Coverage limits

- Shapes reflect article examples for `jev-1.13.0`; API may have changed since 2026-09-29 — verify against live docs before building.
- No live calls were executed here; behavior is **reported**, not reproduced.
- Kev shapes above are **reported** owner README values with serving code uninspected; verify limits and env overrides before building[^kev-readme-2026].
- Nimble shapes above are **reported** single-file README values with scorer code uninspected; verify schema limits and temperature handling before building[^bespoke-nimble-2026-09].
- OpenJev shapes above combine **observed** static `helper/shim.py` plus `serve/SERVE.md` reads with **reported** card numbers; weights and live serving were not reproduced — verify `GET /v1/version` before building[^openjev-2026].
- SGLang shapes above are **reported** single-file documentation values with serving code and live deployment uninspected; the source itself recommends SGLang's native decisions endpoint instead — verify current SGLang docs before building[^openjev-sglang-2026].
- Diffusion-server shapes above are **reported** single-file documentation values with serving code and live deployment uninspected — verify flags and limits against the live repo before building[^razorback16-openjev-2026].
- Von shapes above are **reported** single-file README values with SDKs and live serving uninspected — verify band/raw, truncation headers, and gate numbers before building[^von-2026].
- Pi wire-format claims above are **observed** commenter readings of installed `node_modules` files plus docs prose, not reproduced here; installed-code version, Pi revision, and live docs were not verified, and linked Pi classification docs were not inspected beyond the quoted lines[^reddit-pi-jev-2026-09-30].

[^raschka-jevl-2026-09-29]: S. Raschka, "Language Models for Text Classification: From Bag-of-Words to Jev," Ahead of AI, published 2026-09-29, canonical local entry `../raw/classifier-history-and-jev/index.md`, upstream `https://magazine.sebastianraschka.com/p/classifier-history-and-jev`. Locators in text: §3.2–§4, Figs. 25, 28, 31–32.
[^jev-27b-2026-10-01]: AutoTrust, "autotrust/JEV-27B," model card, canonical local entry `../raw/JEV-27B/README.md`, package scope `../raw/JEV-27B/`, release notes 2026-10-01, upstream `https://huggingface.co/autotrust/JEV-27B`. Locators: “Quickstart with vLLM” `/v1/decide`; “Choice questions with up to 256 options”; “Writing System 1 prompts”.
[^jev-9b-v08]: AutoTrust, “autotrust/JEV-9B,” model card, canonical local entry `../raw/JEV-9B/README.md`, package scope `../raw/JEV-9B/`, released checkpoint v0.8.0, upstream `https://huggingface.co/autotrust/JEV-9B`. Locators: “Quickstart with vLLM” completions plus client-side math; “What System 1 does”; “Other ways to run it”.
[^jev-omni-2026]: akhilaaa3, “Jev-Omni,” model card, canonical local entry `../raw/Jev-Omni/README.md`, package scope `../raw/Jev-Omni/`, upstream `https://huggingface.co/akhilaaa3/Jev-Omni`. Locators: “Quick start” `predict` example; `jev_omni.py::JevOmni.predict/_prompt/_Head256`.
[^jev-style-v3-gguf-2026]: chaoliangUNSW, “Jev-Style-0.8B-Decision-v3-GGUF,” model package, canonical local entry `../raw/Jev-Style-0.8B-Decision-v3-GGUF/README.md`, package scope `../raw/Jev-Style-0.8B-Decision-v3-GGUF/`. Locators: “Quick start” CLI/Python; `jev-score` mechanics, budgets and “Long option lists”; `jev_style_decision_gguf.py` header.
[^julia-1-2026-09-24]: Supersonic Labs, "Julia 1," model package, canonical local entry `../raw/Julia-1/README.md`, package scope `../raw/Julia-1/`, weights SHA-256 `df853bf7fe424420011f3d0c47a05d7341aa9eefa7fb9f203ea4aada4ad95b72`. Locators: "Start here" named-question and legacy APIs; `julia/data.py::validate_row/sequence`, `julia/typed.py::predict_typed`, `julia/probabilities.py::display_probabilities`, `julia/router/router.py::Router`.
[^neohorse-jev-4b-2026-09-24]: TokenRhythm, "NeoHorse-Jev-4B," model package, canonical local entry `../raw/NeoHorse-Jev-4B/README.md`, package scope `../raw/NeoHorse-Jev-4B/`, bundle version `1.0.0`. Locators: `DEPLOYMENT.md` §§3–7 (service, text/image requests, responses/confidence, limits/errors); `package/src/neohorse_decision/systemone.py::MODEL_NAMES/validate_request/with_confidence` and `server.py::create_app`.
[^jev-style-2b-v1-gguf-2026]: chaoliangUNSW, "Jev-Style-Qwen3.5-2B-Decision-GGUF," model package, canonical local entry `../raw/Jev-Style-Qwen3.5-2B-Decision-GGUF/README.md`, package scope `../raw/Jev-Style-Qwen3.5-2B-Decision-GGUF/`.
[^semif-2026-09-22]: SemIf project, "SemIf (formerly OpenJev)," canonical local entry `../raw/SemIf-OpenJev.md`, repo `TheoLeeCJ/SemIf` via PR/star-history links, latest changes 2026-09-22. Locators: "How it works" interface bullets; "Input" JSON contract; "Quick start" backends and `semif-score` modes.
[^clef-flash-2026]: Cloudflare, "Clef-Flash," model card and code bundle, canonical local entry `../raw/clef-flash/README.md`, package scope `../raw/clef-flash/`. Locators: "Input format" state/questions/criteria table; `joint_schema_model.py::encode_record/collate_records/systemone/systemone_answer`.
[^clef-2026]: Cloudflare, "Clef," model card and code bundle, canonical local entry `../raw/clef/README.md`, package scope `../raw/clef/`. Locators: "Input format" state/questions/criteria table; `joint_schema_model.py::encode_record/collate_records/systemone/systemone_answer`; `joint_head_config.json` hidden-size 5120.
[^kev-readme-2026]: Jared Palmer, "Kev," canonical local entry `../raw/kev.md`, upstream `https://github.com/jaredpalmer/kev`. Locators in text: API; How It Works.
[^bespoke-nimble-2026-09]: Bespoke Labs, "Bespoke Nimble," canonical local entry `../raw/nimble.md`, repo `https://github.com/bespokelabsai/nimble`, model `https://huggingface.co/bespokelabs/Bespoke-Nimble-9B`. Locators in text: Capabilities (flat schema, one-token codes, scorer split, field isolation); Quickstart (typed decision example, temperature defaults).
[^openjev-2026]: OpenJev project, "OpenJev," model and serving bundle, canonical local entry `../raw/openjev-openjev/README.md`, package scope `../raw/openjev-openjev/`. Locators: `serve/SERVE.md` `POST /v1/systemone` shapes and env knobs; `helper/shim.py::LETTERS/_readout_once/readout/_distribution/answer_choice/answer_score/answer_noul`.
[^openjev-sglang-2026]: openjev-sglang project, "openjev-sglang," canonical local entry `../raw/openjev-sglang.md`. Locators: "Request" route table and state rendering; "How inference works" N+1 calls, token_ids_logprob, 64-label AA scheme; "Limits and configuration" and "Run on Modal".
[^reddit-pi-jev-2026-09-30]: u/Apprehensive_Bed7502 plus commenters, "Pi now supports Jev.," r/PiCodingAgent, post with comments 2026-09-30–2026-10-01, canonical local entry `../raw/pi-now-supports-jev/index.md`, package scope `../raw/pi-now-supports-jev/`, upstream `https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/`. Locators in text: `node_modules/@earendil-works/pi-ai/dist/api/llama-cpp-classify.js:144` `peakConfidence` quote; `node_modules/@earendil-works/pi-coding-agent/docs/llama-cpp.md:91` typed-choice/bool/score quote; `node_modules/@earendil-works/pi-ai/dist/api/system-one-shared.js:108` bool-to-`noul` quote plus choice/score parsing table; generality dispute (`neuronexmachina` pd1sh25/pd3swyq, `Apprehensive_Bed7502` pd21m44, `_reg1z` pdaz4ie) and maintainer evolution reply (`badlogicgames` pd9uh5p).
[^razorback16-openjev-2026]: razorback16, "OpenJev," project documentation, canonical local entry `../raw/razorback16-openjev.md`, upstream `https://github.com/razorback16/openjev`. Locators: "API" routes, question types, confidence/usage/errors, Jev differences; "Extensions" fields table; "How it works" canvas readout with entropy-0.1 re-reads; "Models" routed-model table.
[^von-2026]: Von project, "Von," canonical local entry `../raw/von.md`, upstream `https://huggingface.co/wfzyx/von`. Locators in text: Use (single- and multi-question examples); Acting on confidence; Wire protocol; CLI flag/env table.
