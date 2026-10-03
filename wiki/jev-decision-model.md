---
type: Concept
title: 'Jev Decision Model: Positioning and Performance'
description: What Jev is, how it positions against frontier LLMs and specialist classifiers, and its reported IMDb accuracy, cost, and latency.
tags: [jev, decision-models, classification]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-03T00:31:59Z }
sources:
  - id: reddit-jev-287-2026-09
    resource: ../raw/i-reviewed-287-opensource-jev-projects-here-are/index.md
    scope: ../raw/i-reviewed-287-opensource-jev-projects-here-are/
    kind: thread
    title: 'I reviewed 287 open-source Jev projects. Here are 20 that actually helped me understand what Jev is good at'
  - id: jev-9b-v08
    resource: ../raw/JEV-9B/README.md
    scope: ../raw/JEV-9B/
    kind: model-card
    title: autotrust/JEV-9B
  - id: jev-omni-2026
    resource: ../raw/Jev-Omni/README.md
    scope: ../raw/Jev-Omni/
    kind: model-card
    title: akhilaaa3/Jev-Omni
  - id: fahad-mirza-showdown-2026
    resource: ../raw/DecisionModelShowdownCLMvsLayavsOpenJevvsKevvsJev.md
    kind: video
    title: 'Decision Model Showdown: CLM vs Laya vs OpenJev vs Kev vs Jev'
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
    title: Jev-Style-Qwen3.5-2B-Decision-v1-GGUF
  - id: julia-1-2026-09-24
    resource: ../raw/Julia-1/README.md
    scope: ../raw/Julia-1/
    kind: code
    revision: df853bf7fe424420011f3d0c47a05d7341aa9eefa7fb9f203ea4aada4ad95b72
    title: Julia 1
  - id: raschka-jevl-2026-09-29
    resource: ../raw/classifier-history-and-jev/index.md
    scope: ../raw/classifier-history-and-jev/
    kind: article
    title: 'Language Models for Text Classification: From Bag-of-Words to Jev'
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
  - id: reddit-learning-jev-2026-09
    resource: ../raw/anyone-here-learning-jev/index.md
    scope: ../raw/anyone-here-learning-jev/
    kind: thread
    title: Anyone here learning JEV?
  - id: reddit-using-jev-2026-09
    resource: ../raw/anyone-here-using-jev/index.md
    scope: ../raw/anyone-here-using-jev/
    kind: thread
    title: Anyone here using Jev?
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
  - id: reddit-jev-prior-art-2026-09
    resource: ../raw/i-literally-built-the-jev-architecture-one-year/index.md
    scope: ../raw/i-literally-built-the-jev-architecture-one-year/
    kind: thread
    title: I literally built the Jev architecture one year back and completely open-sourced it
  - id: reddit-jev-hype-2026-09
    resource: ../raw/i-really-dont-understand-jev-hype/index.md
    scope: ../raw/i-really-dont-understand-jev-hype/
    kind: thread
    title: I really don't understand Jev hype
  - id: reddit-jev-worth-hype-2026-09
    resource: ../raw/is-jev-worth-the-hype/index.md
    scope: ../raw/is-jev-worth-the-hype/
    kind: thread
    title: Is Jev worth the hype?
  - id: reddit-jev-marketing-2026-09
    resource: ../raw/jev-isnt-new-tech-its-marketing-targets-people/index.md
    scope: ../raw/jev-isnt-new-tech-its-marketing-targets-people/
    kind: thread
    title: Jev isn't new tech. Its marketing targets people who think AI started with LLMs
  - id: jev-search-eval-2026
    resource: ../raw/jev-search-eval-report/index.md
    scope: ../raw/jev-search-eval-report/
    kind: article
    title: 'Grading Technical Documents'
  - id: reddit-jev-kev-2026-09
    resource: ../raw/jev-vs-kev-opensource-jev-alternative-tested-side/index.md
    scope: ../raw/jev-vs-kev-opensource-jev-alternative-tested-side/
    kind: thread
    title: 'Jev vs. Kev: open-source Jev alternative tested side by side'
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
  - id: von-2026
    resource: ../raw/von.md
    kind: documentation
    title: Von
---

# Jev Decision Model: Positioning and Performance

Synthesis: Jev is a proprietary TypeSafe AI “System One” decision model with a classifier-style API; its value is general plug-and-play classification that is faster and cheaper than frontier LLMs without per-task fine-tuning, but not superior to a well-tuned specialist on a narrow high-volume task (§3)[^raschka-jevl-2026-09-29].

## Identity and positioning

- Proprietary model from TypeSafe AI, released from stealth weeks before the 2026-09-29 article; author states no affiliation, no free access, and no endorsement (§3.1)[^raschka-jevl-2026-09-29].
- Positioning: frontier GPT/open-weight LLMs can do the same decisions plus general reasoning, but Jev is faster and cheaper for classification; a narrow specialist can still win on accuracy, speed, or cost for one well-defined problem, while Jev is far more general (§intro, §3.3)[^raschka-jevl-2026-09-29].
- Summary metaphor: “ChatGPT moment for classification” — no per-task custom classifier needed for good-enough results; raises the bar for justifying specialist fine-tuning but does not unlock previously unsolvable tasks (§3.1, Conclusion)[^raschka-jevl-2026-09-29].
- Decision-function positioning is **reported** in a 287-project survey: not a chatbot competitor but a general-purpose semantic decision function inside `big model → Jev → code → Jev → tool → Jev → big model` loops, rarely writing code or generating long text and usually answering which-action/which-file/keep-drop/safe-unsafe/route/what-next questions; full pattern catalog in [Jev Project Patterns](jev-project-patterns.md)[^reddit-jev-287-2026-09].

## Community operational framing

- Bounded-decision contract is **reported** in a 2026-09-22–30 practitioner thread: `state + typed question + bounded options → probability distribution / decision` (Choice, Score, Rank, boolean-style), positioned as System-1 judgment rather than open-ended generation[^reddit-learning-jev-2026-09].
- Deterministic sandwich is **reported**: deterministic code constructs the legal action space first (no neural call when only one action is valid), Jev scores only legal candidates, and deterministic policy validates before execution — summarized as `runtime state → eligibility/safety → Jev decision → validation → action → observe result`, applied across context admission, routing, tool-result judgment, retry, ranking, handoffs, completion, and review decisions[^reddit-learning-jev-2026-09].
- Serving shape is **reported**: one generalist plus routed specialists (e.g. abstention-on-weak-evidence, computer-use/forms) with deterministic routing, so most decisions take zero or one inference rather than every model voting on everything[^reddit-learning-jev-2026-09].
- Classifier contrast is **reported**: traditional classification is fixed `input → label` needing retraining for a new question or answer set, while Jev reuses the same model across bounded questions without autoregressive decoding; some practitioners note it is "not very different" when boiled down, and one analogy frames Jev as a learned probabilistic switch expression — score each allowed branch and take the max — versus a hard switch[^reddit-learning-jev-2026-09].

## Community-reported trust limits

- Order sensitivity is **reported**: choice ordering can influence some models, so test decisions for order independence[^reddit-learning-jev-2026-09].
- Repeat variance is **reported**: the same request can return different results on repeat, consistent with serving-scale non-determinism noted above; design with a backup plan and assume "right often enough," not always right[^reddit-learning-jev-2026-09].
- No direct fine-tuning is **reported**: the closest lever described is blind-running Jev over a labeled set to score its accuracy; small-model practitioners note a well-tuned specialist (e.g. BERT-class on local GPU) can beat Jev on its narrow heads[^reddit-learning-jev-2026-09].
- A context envelope of 64k tokens with a 32k cap on input state plus question is a single-commenter **report**; verify against live docs before building[^reddit-learning-jev-2026-09].
- One commenter warns Jev docs mislead on probabilities and links an external confidence explainer; that explainer was not inspected here, so treat the warning as an **unverified** pointer, not a finding[^reddit-learning-jev-2026-09].

## Early PiCodingAgent uses and input lesson

- Input-quality lesson is **reported** from code-quality work (`supercov`): sending whole files with broad "quality" / "maintainability" prompts was bad; narrow mechanical questions (`duplicated_code`, `deep_nesting`) matched coderabbit-style scores at ~100x lower cost; builder estimates ~8h experimentation and points to a Rust source for plumbing[^reddit-using-jev-2026-09].
- Cheap bulk decisions are **reported**: malicious-repo scanner, IMAP mail classifier with plain-English categories and tag/move/flag/webhook actions, npm site-moderation package, LinkedIn `Slop Mop` extension, 607-case `shipwithjev.com` collection, SFT/RL/SCoRe failure taxonomy at a fraction of Fable time/cost, and Godot game-state watch with NPC-behavior discussion — all single-thread accounts with linked repos/pages uninspected[^reddit-using-jev-2026-09].
- Hype markers are **reported** without measurement: 40-tool near-instant voice agent plus Doom play via an uninspected YouTube timestamp, "almost never hallucinate" determinism, AGI-threshold claims, and a "dynamic else-if" analogy; one commenter accuses TypeSafe of spamming Reddit with a paid model, so treat this thread as possibly promotional[^reddit-using-jev-2026-09].

## Hype-skeptic reception and independent field checks

- Novelty dispute is **reported** in a 2026-09-21–25 r/LocalLLaMA skepticism thread: classifiers and zero-shot NLI/BERT systems predate Jev, so the novelty claim is usability — pretrained world knowledge, no per-task training, plain-English task spec, and cheap/fast API — rather than a new task type[^reddit-jev-hype-2026-09].
- Architecture-equivalence debate is **reported**: one explainer frames Jev as non-autoregressive parallel calibrated heads with no KV-cache/token loop versus Qwen-style causal decoding with grammar masks, while counter-commenters argue `max_tokens=1` plus logprobs plus parallel queries over a shared KV-cache (or parallel inference via vLLM) recovers much of the same distribution; one summary holds Jev "carries more information per output out of the box," another holds no public evidence rules out a logprobs wrapper on a fine-tuned LLM[^reddit-jev-hype-2026-09].
- Interchangeability critique is **reported**: Jev and LLMs can emulate each other with efficiency differences, "type-safe" means schema adherence already available via constrained/structured outputs, and game demos (Mario/Doom/Minecraft) do not evidence generality without controls such as disclosed seeds[^reddit-jev-hype-2026-09].
- Legal 28-way field check is **reported**: Opus 5 Low ~95% versus Jev ~70% (~Haiku level) on a couple-thousand-token task, but Jev confidence was "dead on," enabling a Jev-first then Opus-escalation hybrid above 90% at ~30% lower total cost[^reddit-jev-hype-2026-09].
- Chess field check is **reported**: ~400 ms per Choice move over legal moves with total spend $0.07, and 400+ move confidence buckets matching one-ply material-loss checks; the same account notes counting/generative work stays in code per Jev limits doc[^reddit-jev-hype-2026-09].
- Negative field checks are **reported**: German job-ad rating underperformed both LLM-plus-criteria and LLM-labelled embedding-plus-regression baselines with hard-criteria violations noted, and one builder **reports** a 20-minute 3090 training run matching or exceeding Jev on their tests — treat both as single-account domain limits, not general benchmarks[^reddit-jev-hype-2026-09].
- Closed/API-only limit is **reported**: SaaS-only delivery with no downloadable weights drives "not local, don't care" responses and astroturf suspicion, while others point to local clones (DiffusionGemma, Qwen-4B efforts, kev/OpenJev mentions) as the path of interest[^reddit-jev-hype-2026-09].
- Marketing-target critique is **reported** in a 2026-09-23–10-01 r/LocalLLaMA thread: the poster holds Jev's advertised behaviors — probabilities over constrained choices, non-autoregressive scoring, no invalid class, inference-time labels — are normal classifier behavior with modern zero-shot capabilities (NLI, embeddings, cross-encoders, rerankers), and headline Jev-vs-LLM speed/cost wins do not establish a new paradigm; the poster allows the unpublished architecture or RLCD method could be novel but holds public evidence does not establish System One as a new AI class[^reddit-jev-marketing-2026-09].
- Missing-baseline charge is **reported** in the same thread: Jev has not been properly benchmarked across the BTZSC-style landscape (cited as dozens of zero-shot classifiers across 22 datasets including NLI, embedding and reranker models; ICLR 2026 link uninspected), and the community Decision Index is read as a Jev-reproduction leaderboard mixing zero-shot models with Jev-specific fine-tunes without the strongest established baselines (named as Qwen3-Reranker, GTE, strong NLI cross-encoders)[^reddit-jev-marketing-2026-09].
- Banking77 counter-benchmark is **reported** with its own caveat: BGE-small + logistic regression reached 93.3% versus 83.2% for Jev at ~9 ms locally (repo `ickma2311/jev-baselines-eval`, uninspected), but commenters note the supervised head was fit on ~10k same-distribution labels so it is not a zero-shot apples-to-apples comparison; the thread's durable lesson is the curve that matters is accuracy versus labels per class (linear heads catching up around 20–50 per class per one account) with raw probabilities needing per-label thresholds[^reddit-jev-marketing-2026-09].
- Positive zero-shot counterpoint is **reported**: one account testing rule-following/policy adherence got Jev AUC 0.93 zero-shot versus 0.73 for Gliclassv3 and 0.89 for a fine-tuned Gliclass — treat as a single-account domain result, not a general ranking[^reddit-jev-marketing-2026-09].
- Small-model parity pointers are **reported**: Qwen3.5-0.8B matching Jev on some tasks, a Qwen3-Reranker-0.6B pointer as first try, and a DeBERTa-v3-large-zeroshot-v2.0 preference — all single-account pointers with linked models uninspected[^reddit-jev-marketing-2026-09].
- Mechanism speculation is **reported**: one shared-KV-cache plus parallel-forward-pass account of Jev inference, Qwen-backbone and Qwen3-Reranker-primitive guesses, a 100%-synthetic CEO training-data remark (YouTube link uninspected), and a GPT-2/3 scale analogy the poster rejects because GPT documented what was scaled while Jev architecture/training stays closed[^reddit-jev-marketing-2026-09].
- Usage-shift concession is **reported** across the thread: even skeptics grant a fast cheap generalist classifier lowers the barrier from train/fine-tune-a-classifier to call-the-Jev-API, summarized as the If/Case/Switch for AI or breakthrough usage patterns rather than breakthrough science[^reddit-jev-marketing-2026-09].
- Survey reception is **reported** in a 287-project r/LLMDevs thread: source-checked integration catalog praised as more useful than README-mention awesome-lists, but met with slop-ad/astroturf accusations, AI-authorship suspicion over 287-in-2-days throughput, and a "rarely writes code" dispute where commenters hold a typed-decision model never generates by definition[^reddit-jev-287-2026-09].

## r/singularity worth-the-hype reception (2026-09-26–29)

- Mental models are **reported**: "classifier on crack" for pipeline slices that cost thousands in LLM/compute versus single-digit dollars (with hype exceeding reality), countered as "just a classifier" that understands language; generalized instruction-tuned BERT/classifier guess, CLIP-for-LLM analogy (no per-task head), and single-prefill single-token choice versus paying for dozens/hundreds of tokens[^reddit-jev-worth-hype-2026-09].
- Independent categorisation check is **reported**: 1,000 documents on Jev and Haiku with ~40% disagreement; manual review of 100 differences found Jev right ~70%, cost ~5x lower than Haiku (not the published 400x versus a frontier model), and 200,000 records in under 5 minutes[^reddit-jev-worth-hype-2026-09].
- Cost/speed points are **reported**: 12K weekend requests for $1.83, "pennies on the dollar" with minutes-to-seconds framing, and one "1,000 questions in 1s for 1 cent" claim distinguishing cost/speed from new functionality[^reddit-jev-worth-hype-2026-09].
- Jevons-paradox limit is **reported**: cutting usage costs may leave frontier models just as big, with Jev upgrades added on top[^reddit-jev-worth-hype-2026-09].

## Reported capabilities and vendor claims

- Vendor benchmark claims parity with GPT-5.6 Luna on decision-making at orders-of-magnitude lower cost and latency; treat as **reported** vendor evidence (Fig. 24) (§3.1)[^raschka-jevl-2026-09-29].
- Demonstrated breadth: same model categorizes support tickets and plays real-time Tetris via Choice API, used by author to evidence latency and generality (§3.1–§3.2)[^raschka-jevl-2026-09-29].
- Training facts are sparse: CEO quote says “100% synthetic” data, qualified as not naive LLM exhaust; architecture guessed by author as small ModernBERT-like for low latency; training method named “Reinforcement Learning for Calibrated Decisions (RLCD)” with no public details — all **unverified synthesis** (§5)[^raschka-jevl-2026-09-29].

## IMDb measurement

- Choice API: 96.47% (24,117/25,000), 22 min 24 s, 15,456,663 input tokens, $0.6492 total (§3.3)[^raschka-jevl-2026-09-29].
- Noul API: 96.20% (24,050/25,000), 23 min 3 s, 15,106,663 input tokens, $0.6345 total; Choice-vs-Noul gap may be random fluctuation (§3.3)[^raschka-jevl-2026-09-29].
- Repeat Choice run gave slightly different results; attributed to serving-scale non-determinism from batch-dependent GPU kernels changing floating-point order, citing Horace He 2025 post (Fig. 29) (§3.3)[^raschka-jevl-2026-09-29].
- Caveat: unknown whether IMDb test set was in Jev training data (§3.3)[^raschka-jevl-2026-09-29].
- ModernBERT comparison: similar accuracy with minimal tuning (plus possible 1–2%); cost was 23 min fine-tune plus 7 min eval on DGX Spark, improvable with quantization and faster hardware; unlike Jev it cannot do Tetris or other tasks without refitting (Fig. 30) (§3.3)[^raschka-jevl-2026-09-29].

## Independent showdown spot check

- Same angry-customer routing task as four open rivals: **reported** Jev 1.13 at 100% confidence on Billing with very-angry call; all five picked Billing, so the difference is confidence level, with Jev highest and Open Jev lowest at 54.7% in this run[^fahad-mirza-showdown-2026].
- Same-video security probe (emergency production-data demand with unverified approval and $50,000/hour urgency claim): **reported** Jev flagged critical risk / escalate with ~93% social-engineering suspicion and passed alongside CLM (~70%), while Kev, Laya, and Open Jev granted access; **synthesis**: treat routing correctness and privilege-escalation robustness as separate test targets[^fahad-mirza-showdown-2026].
- Benchmark caveat from the same author: Jev leads Jev Bench, but that is TypeSafe's own benchmark, so discount it relative to independent checks; CLM instead reports DeepSWE / Terminal-Bench for agentic verification while Open Jev and Kev are described as competitive on Jev Bench[^fahad-mirza-showdown-2026].
- Cost and deployment contrast in the same video: Jev is the only closed, pay-per-call cloud model in the lineup versus four open, locally runnable models; CLM's 24 ms local run is described as ~6x faster than Jev cloud in this anecdotal run, not a controlled latency benchmark[^fahad-mirza-showdown-2026].

## Independent section-grading eval

- Task is **reported** as per-question section relevance grading over two technical documents (170 + 47 sections, about 15,000 words) with 38 questions and 8,246 question-section pairs; four labels where only unrelated hides the section (direct, tangential, and reference are kept)[^jev-search-eval-2026].
- Reference labels are **reported** as a Gemini 3.5 flash-lite judge over all pairs plus Claude Opus 5.5 blind correction in three rounds on disagreements; final split is 290 direct (3.5%), 247 tangential (3.0%), 40 reference (0.5%), and 7,669 unrelated (93.0%)[^jev-search-eval-2026].
- Headline result is **reported**: Jev missed 4 at k=38 and 3 at k=10 of 290 direct answers with 22.8%/22.7% noise (16.4%/16.3% after correction); simple-jev Qwen3.8-27B missed 5/1 with 14.1%/15.6% noise; simple-jev Gemma-4-26B-A4B missed 6/6 with 10.9%/11.4% noise; Gemma 4 31B LLM baseline missed 11 with 8.1% noise (3.8% corrected) — so Jev-likes missed fewer answers but kept more sections (Jev about 61 per question versus 29-46 for the LLM and simple-jev)[^jev-search-eval-2026].
- Comparators are **reported**: Liquid D1 averaged 3.7 misses but 29.5-30.1% noise, over the 25% limit, with a stricter cutoff passing only at 4-8 misses (AUC 0.95 direct-vs-unrelated versus 0.98 for Jev); Laya shipped checkpoints zero-shot kept almost everything (English 0 misses with 100% noise, multilingual 28 misses with 77% noise); three small local SLMs failed a 480-pair screening pilot and were excluded[^jev-search-eval-2026].
- Speed and cost are **reported**: Jev 18.8 s (k38) and 26.4 s (k10) per question at $0.065/$0.077 per full 38-question run from measured API token counts; D1, simple-jev, and Gemma times ran on free tiers or demos with queueing so are indicative only; Laya ran 4.2-4.5 s on a local GPU; Gemma 31B has no paid Google price so $0.06-0.44 was estimated from third-party host prices — **synthesis**: Jev was the fastest system to clear both bars here but is not clearly cheaper than the LLM baseline[^jev-search-eval-2026].

## Opper side-by-side: Kev-4B vs Jev

- Identity and routing are **reported**: Kev-4B is Jared Palmer's Apache-2.0 fine-tune of Qwen3.5-4B, run side by side with Jev on the same Opper endpoint by the author's startup Opper[^reddit-jev-kev-2026-09].
- Method is **reported**: fresh 362-item set published after both models shipped (new arXiv papers, Stack Exchange questions, GitHub issues) with answers taken from the source; benchmark code, items, and results are claimed on GitHub without a captured link here[^reddit-jev-kev-2026-09].
- Headline parity is **reported**: accuracy lands within 2 points on every task, described as inside noise at n=362; Jev is better calibrated and pulls ahead on paraphrase detection (PAWS 87.0% vs 74.5%)[^reddit-jev-kev-2026-09].
- Cost mechanism is **reported**: same list price, but Jev counts a fixed ~257 extra input tokens per request (same count calling TypeSafe directly), so short requests cost up to 12x more — **synthesis**: compare effective per-request tokens, not list price, for short classification calls[^reddit-jev-kev-2026-09].
- Owner-reported family context is **reported** in [Kev Decision Models](kev-decision-models.md): Kev 1.0 spans 0.8B/4B/9B/27B on Qwen3.5/3.8 with held-out Decision Index 23.3/38.0/41.0/52.3 versus Jev 54.0, new-source accuracy 0.697/0.838/0.852/0.889 on test versus Jev 0.857 dev-only, and validated context 8,192 for 0.8B–9B versus 65,536 for 27B; knowledge-gap caveat is MMLU-Pro 0.675 for Kev-27B versus 0.840 for Jev[^kev-readme-2026].

- Open-recipe comparison point is **reported** in [Bespoke Nimble](bespoke-nimble-decision-model.md): Bespoke-Nimble-9B (Qwen3.5-9B LoRA, contrastive 2,676/324 split) matched 292/324 holdout labels (90.12%) versus Jev 1.13.0 at 302/324 (93.21%) and its base at 215/324 (66.36%), explicitly not distilled from Jev; holdout covers 162 pairs from six source families with synthetic unreviewed labels, so do not treat the 3.09-point gap as a general ranking[^bespoke-nimble-2026-09].

## Open student head-to-head

- Prior-art dispute is **reported** in a 2026-09-17–24 r/LocalLLaMA thread: the poster claims a March 2025 sales-conversion PPO system plus a September 2025 routing paper anticipated Jev and follows with generic Laya; commenters counter that a sequential single-probability policy and a routing wrapper around autoregressive LLMs are not the parallel multi-typed Jev interface, and that the "beats Jev" headline compares a benchmark-fine-tuned Laya checkpoint against third-party Jev figures — see [Laya Prior-Art Claim and Jev-Equivalence Dispute](laya-prior-art-claim.md)[^reddit-jev-prior-art-2026-09].

- Closest open student by distribution match: [JEV-27B System 1 Decisions and Blocks-of-Experts Serving](jev-27b-system1-decisions.md) **reports** KL ≈0.017 to Jev 1.13 on 25,376 held-out Jev-labelled rows, six-group mean 84.07 vs 83.85 for hosted Jev (+0.22, higher on 4/6), and 96–98% of teacher accuracy on an independent 16-option human-gold pressure set with the same order-sensitivity weakness (7.4% vs 7.0% flips); not submitted to Decision Index 0.2 or JevBench v1.4.2, so do not treat it as closest by every leaderboard measure[^jev-27b-2026-10-01]. The fast first generation [JEV-9B](jev-9b-system1-decisions.md) **reports** KL ≈0.019 on the same Jev-labelled rows, 90% of teacher accuracy at 16 options (97–98% at 2–8), and 2.6× the 27B speed with a third of the weight memory[^jev-9b-v08].
- Independent (non-student) open alternative: [Jev-Omni Multimodal Decision Classifier](jev-omni-multimodal-decisions.md) implements the same typed-decision interface on Gemma 4 12B IT but explicitly **reports** no TypeSafe affiliation, endorsement, or Jev-output training; it trades text-only fidelity for native text/image/audio/video coverage with **reported** DecisionBench Medium 87.57% vs Jev 1.13 90.48% on the same cost-accuracy plot, JevBench 86.15%, MMAU 63.10% and MVBench 53.10%[^jev-omni-2026].
- Independent (non-student) on-device alternative: [Jev-Style-0.8B Decision v3 GGUF](jev-style-0.8b-decision-v3-gguf.md) is a Qwen3.5-0.8B verdict-readout fine-tune with explicitly no Jev weights/code/outputs, shipped as 0.53 GB Q4_K_M GGUF with 25,600-token budgets; **reported** Banking77 68.2% and 37 held-out MASSIVE languages 65.5% ahead of the best official Laya checkpoint, JevBench v1.4.1 64.1% as a point-estimate lead, and 79.2% typed in-domain[^jev-style-v3-gguf-2026]. Its v1 predecessor [Jev-Style-2B Decision v1 GGUF](jev-style-2b-decision-v1-gguf.md) is a Qwen3.5-2B letter-readout fine-tune (1.3 GB Q4_K_M) with the temperature folded into RMSNorm; **reported** 82.3% 5-task accuracy vs 65.9% zero-shot base and ECE 0.017, superseded by v3 on typed accuracy and context but simpler to serve via plain `top_logprobs`[^jev-style-2b-v1-gguf-2026].
- Independent small open-weight alternative: [Julia 1](julia-1-decision-model.md) is an Apache-2.0 144.3M mmBERT-small encoder plus decision head with a Jev-compatible choice/noul/score interface; **reported** typed decisions 73.15% (1,463/2,000) versus supplied 72.70% Jev reference, AG News 94/100, Emotion 86/100, Banking77 pilot 64/100 versus supplied 87/100 through a ranking shortlist, and MASSIVE scenario macro 71.50% across 52 locales; **synthesis**: prefer it for small local CPU classification/routing tests with explicit candidates, not as a Jev-accuracy substitute on long label lists or new domains[^julia-1-2026-09-24].
- Balanced open-weight text-plus-vision alternative: [NeoHorse-Jev-4B](neohorse-jev-4b-decision-model.md) is an Apache-2.0 ~4B prefill-only model on NeoHorse-1-4B with a Kev-derived runtime and unified vision backbone; **reported** six-group text mean 77.70 (Kev 81.92 and Nimble 87.23 leads) and three-benchmark mean 83.26% (+11.50 over its base), plus 60.65% Image-NLI over 8,000 examples and single-image single-question serving — **synthesis**: prefer it when one self-hosted model must cover routed text decisions plus light vision without audio/video, accepting CUDA/BF16 serving and vendor-reported benchmarks[^neohorse-jev-4b-2026-09-24].
- Independent no-training baseline: [SemIf Open Decisions](semif-open-decisions.md) reads typed option logits from frozen open models with no fine-tuning; **reported** Qwen3.5-4B direct logits reach 0.813 authored and 0.637 WANLI balanced accuracy with 0.845 modal agreement on the aligned 102-row TypeSafe subset versus published Jev 0.883, while the quantized 27B EXL3 bridge reaches 0.958 on the same 144 authored rows as a system-level (not controlled-ablation) comparison[^semif-2026-09-22].
- Open-weights tuned anchor: [OpenJev](openjev-decision-model.md) is a CC BY-NC 4.0 Qwen3.8-27B derivative with Jev-compatible `POST /v1/systemone` and frozen letter-readout helper; **reported** 84.0% on the same 10,000 text questions as hosted Jev 85.4% (base 80.4%, Nimble 75.7%), 88.0%/87.4%/84.5% on desktop/web agent steps with shuffle flips 18.5%→2.3%, 39/39 MiniWoB tie, and pinned H100 serving (≈80 ms text, ≈210 ms web) — **synthesis**: prefer it as the self-hosted accuracy anchor when non-commercial weights and an 80 GB GPU (or quantized Mac/GGUF text-only builds) are acceptable, and do not confuse it with SemIf (formerly OpenJev)[^openjev-2026].
- Independent open-weight CPU encoder alternative: [Von](von-decision-model.md) is an Apache-2.0 395M ModernBERT System One model with calibrated Choice/Noul/Score over `/v1/systemone`; **reported** JevBench v1.4 composite 27.5 (C 75.7, hard 0.373, sealed 0.279, p50 0.34 s CPU) with chains lifting hard to 0.441 (McNemar p = 0.065 on 111 items), plus a measured 0.80 confidence gate and English-only limit[^von-2026].
- Cloudflare first-party multimodal alternative: [Clef-Flash Multimodal Joint-Schema Decisions](clef-flash-multimodal-decisions.md) is a 9B Qwen3.5-9B plus joint-schema-head model with a Jev/SystemOne-compatible API; **reported** Decision Index 0.2.1 leads Jev on 17 rows including BFCL 98.8, API-Bank 93.1, home-appliance simulator 97.7, MMLU 91.8 and ForecastBench Brier 10.6 with p95 latency 122.4 ms versus Jev 536.0 ms, but trails sharply on CLINC150+OOS 66.8 versus Jev 89.3, RAGTruth 35.6 versus 76.5, and MMLU-Pro/BBH/GPQA hard-reasoning rows[^clef-flash-2026]. Its larger sibling [Clef Multimodal Joint-Schema Decisions](clef-multimodal-decisions.md) is a 27B Qwen3.8-27B model with identical decision code; **reported** leads on 11 rows including CLINC150+OOS 97.4, RAGTruth 79.4, GSM8K 80.8 and CRUXEval 86.7 with median/p95 latency 209.3/238.6 ms, plus Typesafe-workflow bests on invoice exact/primary and security incidents[^clef-2026].

## Relationships

- Uses [Jev API Patterns](jev-api-patterns.md) for Choice, Noul, and Score invocation.
- Uses [Classifier Calibration](classifier-calibration.md) for confidence and calibration behavior.
- Contrasts with [Text Classification Lineage](text-classification-lineage.md) fine-tuned specialists.
- Informs [Classifier Selection](classifier-selection.md) build-vs-buy and clone decisions.
- Exemplified by [Jev Project Patterns](jev-project-patterns.md) across 20 starter integrations.

## Contradictions

- Choice response example shows confidence 1.0 with probabilities 1.0/0.0 while Noul on the same review gives 0.98 — article notes the discrepancy without resolving it; do not treat the two APIs’ scores as interchangeable (§3.3)[^raschka-jevl-2026-09-29].

## Coverage limits

- Performance, price, and latency are single-point author measurements plus one vendor chart; not independently reproduced here.
- Community framing and limits above are **reported** single-thread practitioner accounts, not reproduced here; linked external evals and explainers (memory-admission eval, Jev explainers, videos) were not inspected.
- PiCodingAgent thread above is single-thread Reddit anecdote (2026-09-18–25); linked GitHub repos, npm package, HF `laya` page, YouTube video, preview images, and cross-linked Reddit threads were not inspected, and access/availability notes are time-sensitive.
- Architecture, dataset, and RLCD details are unknown; guesses are labeled as such.
- Prior-art thread above is single-thread Reddit anecdote with linked papers, models, datasets, repos, and plots uninspected; all equivalence and benchmark-win figures are **reported**, with detail in [Laya Prior-Art Claim](laya-prior-art-claim.md)[^reddit-jev-prior-art-2026-09].
- Skepticism thread above is single-thread Reddit anecdote (2026-09-21–25); YouTube videos, preview images, KDnuggets explainer, HF zero-shot-classification page, and LovingOpenSourceAI cross-link were not inspected, and all accuracy/cost/latency figures are **reported** single-account values[^reddit-jev-hype-2026-09].
- Image figures were covered via captions, not independent visual inspection.
- Showdown figures are single-prompt **reported** YouTube demo values (n=1 routing plus n=1 security probe), read from transcript prose without video-pixel verification; transcript names are garbled and identities are resolved via the filename (CLM / Laya / OpenJev / Kev / Jev)[^fahad-mirza-showdown-2026].
- 287-project survey above is single-curator Reddit anecdote (2026-09-19–10-01) with directory, repos, videos, and images uninspected; corpus count, latency demos, and project behaviors are **reported**, not reproduced[^reddit-jev-287-2026-09].
- Marketing-critique thread above is single-thread Reddit anecdote (2026-09-23–10-01) with linked ICLR paper, Banking77 repo, launch blog, docs primer, leaderboard, model pages, video, and field-test blog uninspected; all benchmark, mechanism, and motive figures are **reported** single-account values[^reddit-jev-marketing-2026-09].
- Worth-the-hype thread above is single-thread r/singularity anecdote (2026-09-26–29); shipwithjev/Laya/Deem links, WS-Jev repo, Jev-vs-local write-up, and YouTube video were not inspected, and all cost/accuracy/latency figures are **reported** single-account values[^reddit-jev-worth-hype-2026-09].
- Search-eval figures above are **reported** single-run values (D1 is a three-run mean) over 38 questions and 290 answering pairs from two documents with all misses in 8 questions; reference labels are an LLM judge plus blind review, not a full human-expert pass; latency compares paid Jev against queued free tiers; the 25% noise limit is author judgement; the report says D1 mean of three runs in Results but mean of two in Limitations, treated here as an unresolved minor inconsistency[^jev-search-eval-2026].
- Opper Jev-vs-Kev figures above are **reported** single-vendor values over a 362-item fresh set with no variance table inspected here; GitHub code/items/results, HF `jaredpalmer/kev-4b`, Opper community pages, preview image, and capitalandcompute use-case link were not inspected, and the 257-token overhead plus PAWS gap are unreproduced[^reddit-jev-kev-2026-09].
- Kev owner figures above are **reported** README values with linked model cards, Hub revisions, eval manifests and `runs/*` logs uninspected; treat Decision Index, validated-context and MMLU-Pro gaps as unreproduced[^kev-readme-2026].
- Nimble comparison figures above are **reported** single-file README values with dataset files, eval outputs, and Hub revisions uninspected; treat the 324-example gap and narrowness caveat as unreproduced[^bespoke-nimble-2026-09].
- Von figures above are **reported** single-file README values with weights, SDKs, serving, calibration scripts, and benchmark harnesses uninspected; treat JevBench, gate, and latency figures as unreproduced[^von-2026].
- OpenJev figures above are **reported** bundle values with weights (`model-*.safetensors`), `tokenizer.json`, and `assets/*.png` pixels uninspected and no serving run reproduced here; treat accuracy, latency, and quant deltas as pinned-recipe values only[^openjev-2026].

[^raschka-jevl-2026-09-29]: S. Raschka, “Language Models for Text Classification: From Bag-of-Words to Jev,” Ahead of AI, published 2026-09-29, canonical local entry `../raw/classifier-history-and-jev/index.md`, upstream `https://magazine.sebastianraschka.com/p/classifier-history-and-jev`. Locators in text: §3, §5, Figs. 24, 29–30.
[^fahad-mirza-showdown-2026]: Fahad Mirza, "Decision Model Showdown: CLM vs Laya vs OpenJev vs Kev vs Jev," YouTube, canonical local entry `../raw/DecisionModelShowdownCLMvsLayavsOpenJevvsKevvsJev.md`, upstream `https://www.youtube.com/watch?v=UF0z3afz9V8`. Locators in text: angry-customer three-question prompt; dashboard comparison (Jev 1.13 100% Billing / very angry); social-engineering probe (Jev critical-risk/escalate ~93%); published-numbers segment (Jev Bench own-benchmark caveat); open/closed and latency contrast.
[^jev-27b-2026-10-01]: AutoTrust, "autotrust/JEV-27B," model card, canonical local entry `../raw/JEV-27B/README.md`, package scope `../raw/JEV-27B/`, release notes 2026-10-01, upstream `https://huggingface.co/autotrust/JEV-27B`. Locators: “System 1: indistinguishable” KL table; “Public decision benchmarks” six-group table; “Benchmark highlights” pressure table.
[^jev-9b-v08]: AutoTrust, “autotrust/JEV-9B,” model card, canonical local entry `../raw/JEV-9B/README.md`, package scope `../raw/JEV-9B/`, released checkpoint v0.8.0, upstream `https://huggingface.co/autotrust/JEV-9B`. Locators: “Headline results”; “JEV-9B vs JEV-27B”; “Benchmark highlights” pressure table.
[^jev-omni-2026]: akhilaaa3, “Jev-Omni,” model card, canonical local entry `../raw/Jev-Omni/README.md`, package scope `../raw/Jev-Omni/`, upstream `https://huggingface.co/akhilaaa3/Jev-Omni`. Locators: “Results” table; cost-plot `assets/medium-accuracy.svg` values; independence note.
[^jev-style-v3-gguf-2026]: chaoliangUNSW, “Jev-Style-0.8B-Decision-v3-GGUF,” model package, canonical local entry `../raw/Jev-Style-0.8B-Decision-v3-GGUF/README.md`, package scope `../raw/Jev-Style-0.8B-Decision-v3-GGUF/`. Locators: beyond-training-data table and footnotes; “Files” parity table; independence and Laya-convention notes.
[^julia-1-2026-09-24]: Supersonic Labs, "Julia 1," model package, canonical local entry `../raw/Julia-1/README.md`, package scope `../raw/Julia-1/`, weights SHA-256 `df853bf7fe424420011f3d0c47a05d7341aa9eefa7fb9f203ea4aada4ad95b72`. Locators: "Evaluation" typed, pilot, and MASSIVE tables plus "Protocol" paragraph; "Where Julia is accurate" limits.
[^neohorse-jev-4b-2026-09-24]: TokenRhythm, "NeoHorse-Jev-4B," model package, canonical local entry `../raw/NeoHorse-Jev-4B/README.md`, package scope `../raw/NeoHorse-Jev-4B/`, bundle version `1.0.0`, evaluations updated 2026-09-24. Locators: "Evaluation" six-group and three-mean tables plus JevBench/Kev/OpenJev details; "Image and Text Evaluation" Image-NLI; "Download Model" composition.
[^jev-style-2b-v1-gguf-2026]: chaoliangUNSW, "Jev-Style-Qwen3.5-2B-Decision-GGUF," model package, canonical local entry `../raw/Jev-Style-Qwen3.5-2B-Decision-GGUF/README.md`, package scope `../raw/Jev-Style-Qwen3.5-2B-Decision-GGUF/`.
[^semif-2026-09-22]: SemIf project, "SemIf (formerly OpenJev)," canonical local entry `../raw/SemIf-OpenJev.md`, repo `TheoLeeCJ/SemIf` via PR/star-history links, latest changes 2026-09-22. Locators: "Quality" browser-ladder, general-baseline, and EXL3-bridge tables plus 102-row Jev-alignment caveat.
[^clef-flash-2026]: Cloudflare, "Clef-Flash," model card and code bundle, canonical local entry `../raw/clef-flash/README.md`, package scope `../raw/clef-flash/`, Hugging Face `Cloudflare/clef-flash`. Locators: "Results / Decision Index" 0.2.1 table and latency rows; "Workflow evals" Typesafe four-workflow table; "Model" backbone/head/output bullets.
[^clef-2026]: Cloudflare, "Clef," model card and code bundle, canonical local entry `../raw/clef/README.md`, package scope `../raw/clef/`, Hugging Face `Cloudflare/clef`. Locators: "Results / Decision Index" 0.2.1 table and latency rows; "Workflow evals" Typesafe four-workflow table; "Model" backbone/head/output bullets.

[^reddit-using-jev-2026-09]: r/PiCodingAgent, "Anyone here using Jev?," Reddit thread, comments 2026-09-18–2026-09-25, canonical local entry `../raw/anyone-here-using-jev/index.md`, package scope `../raw/anyone-here-using-jev/`, upstream `https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/`. Locators in text: `supercov` input-quality and mechanical-question remarks; bulk-decision project links (malicious scanner, mail classifier, modsure, Slop Mop, shipwithjev, failure taxonomy, Godot/NPC); voice-agent/Doom YouTube timestamp and determinism/AGI remarks; promotion-spam dispute.

[^reddit-learning-jev-2026-09]: r/AI_Agents, "Anyone here learning JEV?," Reddit thread, comments 2026-09-22–2026-09-30, canonical local entry `../raw/anyone-here-learning-jev/index.md`, package scope `../raw/anyone-here-learning-jev/`, upstream `https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/`. Locators in text: bounded-decision / Neural Decision Fabric remarks; routed-specialist and zero-or-one-inference remarks; classifier-contrast and switch-expression analogy; order-sensitivity, repeat-variance, no-finetune scoring, and 64k/32k-cap remarks; confidence-explainer link (uninspected); production-use, shadow/ledger, checkpoint-placement, and access/gateway remarks.
[^reddit-jev-prior-art-2026-09]: u/Nandakishor_ml plus commenters, "I literally built the Jev architecture one year back and completely open-sourced it," r/LocalLLaMA, post 2026-09-17 with comments through 2026-09-24, canonical local entry `../raw/i-literally-built-the-jev-architecture-one-year/index.md`, package scope `../raw/i-literally-built-the-jev-architecture-one-year/`, upstream `https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/`. Locators in text: post body prior-art and Laya links; sequential-PPO vs parallel-typed and routing-vs-decision dispute; benchmark fine-tune versus third-party-Jev caveat.
[^reddit-jev-hype-2026-09]: u/Manerfish plus commenters, "I really don't understand Jev hype," r/LocalLLaMA, post 2026-09-21 with comments through 2026-09-25, canonical local entry `../raw/i-really-dont-understand-jev-hype/index.md`, package scope `../raw/i-really-dont-understand-jev-hype/`, upstream `https://www.reddit.com/r/LocalLLaMA/comments/1wm65le/i_really_dont_understand_jev_hype/`. Locators in text: novelty remarks (`FreakyRefrigerator` pb4egwx, `Automatic-Boot665` pb543xb, `vintageballs` pbcfz9i, `pooquipu` pbcirb4); Qwen/logprobs architecture debate (`SnooPaintings8639` pb4ipz0, `puzzleheadbutbig` pb4jg1y/pb640r3/pb64hhj, `RevolutionaryGold325` pb4lyon/pb4qvml, `dimbledumf` pb4nrvg/pb59rd3, `james_pic` pb519sv, `MR_-_501` pb4nmz1, `HelloMyNameIsAmanda` pb6uosw, `ECrispy` pb5by4v); interchangeability and game-generality dispute (`JiminP` pb4obbh, `quiteconfused1` pb4ilr0/pb62uld, `HiddenoO` pb5zi90/pb60uig, `Stepfunction` pb5vj7h); legal 28-way hybrid (`Sea-Requirement-5375` pb4m469) with Flash-Lite (`ideadude` pb5gkqy) and LLM-confidence (`PyrrhicArmistice` pb5c2wt, `scorchypoo` pb7r0z2) replies; chess calibration (`LateDon` pb6ty8q); German-ads (`Geriny` pbbi77k) and 20-minute-3090 (`harrro` pb8aohi) negatives; closed/API-only (`575_Inverse` pb51etf, `SamSlate` pb667b5, `IngwiePhoenix` pb97o9e, `porkminer` pb618wc).
[^reddit-jev-worth-hype-2026-09]: u/beasthunterr69 plus commenters, "Is Jev worth the hype?," r/singularity, post with comments 2026-09-26–2026-09-29, canonical local entry `../raw/is-jev-worth-the-hype/index.md`, package scope `../raw/is-jev-worth-the-hype/`, upstream `https://www.reddit.com/r/singularity/comments/1wqs5d9/is_jev_worth_the_hype/`. Locators in text: classifier framing (`kuberwt` pc6gh5o, `Time_Entertainer_319` pc6k30l, `FirstOrderCat` pc71npx/pc9uxrh, `Moreh` pc9ss51); CLIP plus single-prefill remarks (`you-get-an-upvote` pcqv4yc); 1,000-doc Haiku comparison plus 40–60% variance (`Existing_Scallion_66` pcuz4k9/pcuziy3); cost/speed remarks (`slackmaster2k` pcmsclc, `mobydikc` pc7fjjc, `stpfun` pc95hj0); Jevons-paradox remark (`chaosfire235` pc7wsfj).
[^reddit-jev-287-2026-09]: u/chenrongwei plus commenters, "I reviewed 287 open-source Jev projects," r/LLMDevs, post with comments 2026-09-19–2026-10-01, canonical local entry `../raw/i-reviewed-287-opensource-jev-projects-here-are/index.md`, package scope `../raw/i-reviewed-287-opensource-jev-projects-here-are/`, upstream `https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/`. Locators in text: decision-function framing and loop composition; 14→287 source-review claim; `jev-ultrafast`, `json-render`, and 20-pattern taxonomy; source-review praise (`QuanTradin` pas8l9d); "rarely writes code" dispute and AI-authorship/astroturf remarks.
[^reddit-jev-marketing-2026-09]: u/tiensss plus commenters, "Jev isn't new tech. Its marketing targets people who think AI started with LLMs," r/LocalLLaMA, post 2026-09-23 with comments through 2026-10-01, canonical local entry `../raw/jev-isnt-new-tech-its-marketing-targets-people/index.md`, package scope `../raw/jev-isnt-new-tech-its-marketing-targets-people/`, upstream `https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/`. Locators in text: post body (constrained-choice behaviors, LLM comparison, BTZSC 22-dataset, Banking77 93.3%/83.2%/9ms, 0%-hallucination nuance); NLI-2019 and HF-pipeline replies; Decision Index reproduction-mix reply; supervised-10k and accuracy-vs-labels replies; Gliclass AUC 0.93/0.73/0.89 remark; Qwen3-Reranker/GTE, Qwen3.5-0.8b, DeBERTa, BART-MNLI and SetFit pointers; synthetic-data, Qwen-guess, shared-KV and GPT-scale remarks; If/Case/Switch and constrained-output-for-agents remarks; spam-bias remark.
[^jev-search-eval-2026]: 95pctAI, "Grading Technical Documents," web eval report, canonical local entry `../raw/jev-search-eval-report/index.md`, package scope `../raw/jev-search-eval-report/`, upstream `https://95pctai.github.io/jev-search-eval-report/`. Locators in text: Core question; TL;DR; How section grading works and Figure 1; Reference labels and Table 1; Metrics; Systems tested and Figure 2; Screening pilot; Results, Figure 3, and Table 2; Speed and cost and Table 3; Limitations; Conclusion.
[^reddit-jev-kev-2026-09]: u/facethef plus commenters, "Jev vs. Kev: open-source Jev alternative tested side by side," r/LocalLLaMA, post with comments 2026-09-25–2026-10-01, canonical local entry `../raw/jev-vs-kev-opensource-jev-alternative-tested-side/index.md`, package scope `../raw/jev-vs-kev-opensource-jev-alternative-tested-side/`, upstream `https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/`. Locators in text: post body (Kev-4B identity, 362-item fresh set, within-2-points finding, PAWS 87.0%/74.5%, +257-token overhead and 12x short-request cost); Opper routing and GitHub pointer.
[^kev-readme-2026]: Jared Palmer, "Kev," canonical local entry `../raw/kev.md`, upstream `https://github.com/jaredpalmer/kev`. Locators in text: Models tables; Kev 1.0 table; What to Expect.
[^bespoke-nimble-2026-09]: Bespoke Labs, "Bespoke Nimble," canonical local entry `../raw/nimble.md`, repo `https://github.com/bespokelabsai/nimble`, model `https://huggingface.co/bespokelabs/Bespoke-Nimble-9B`. Locators in text: Methodology (contrastive curation, dataset tables, finetuning, 324-example eval table); Capabilities.
[^openjev-2026]: OpenJev project, "OpenJev," model and serving bundle, canonical local entry `../raw/openjev-openjev/README.md`, package scope `../raw/openjev-openjev/`, Hugging Face `openjev/openjev`. Locators: "Results" 10,000-question, agent/desktop/web, MiniWoB, language/long-doc and "Speed" tables; "Formats" deltas; `serve/SERVE.md` pinned recipe; `helper/shim.py` readout.
[^von-2026]: Von project, "Von," canonical local entry `../raw/von.md`, upstream `https://huggingface.co/wfzyx/von`. Locators in text: Benchmarks table and footnotes; Acting on confidence gate figures; Chain-of-options; Wire protocol and CLI tables.
