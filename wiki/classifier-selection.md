---
type: Concept
title: 'Classifier Selection: Build, Buy, or Clone for Decision Tasks'
description: When to use Jev or Jev-likes versus frontier LLMs or fine-tuned specialists, plus the clone landscape and agent-harness uses.
tags: [jev, decision-models, agents, build-vs-buy]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-07T12:00:00Z }
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
  - id: itscuthulhu-jev-alts-2026-09-20
    resource: ../raw/2101491913866055821/index.md
    scope: ../raw/2101491913866055821/
    kind: post
    title: 'Post by @ItsCuthulhu on X'
  - id: fahad-mirza-showdown-2026
    resource: ../raw/DecisionModelShowdownCLMvsLayavsOpenJevvsKevvsJev.md
    kind: video
    title: 'Decision Model Showdown: CLM vs Laya vs OpenJev vs Kev vs Jev'
  - id: vllm-diffusiongemma-jev-2026-09-23
    resource: ../raw/2102670270129647953/index.md
    scope: ../raw/2102670270129647953/
    kind: post
    title: 'Post by @vllm_project on X'
  - id: jev-omni-2026
    resource: ../raw/Jev-Omni/README.md
    scope: ../raw/Jev-Omni/
    kind: model-card
    title: akhilaaa3/Jev-Omni
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
  - id: openjev-sglang-2026
    resource: ../raw/openjev-sglang.md
    kind: documentation
    title: openjev-sglang
  - id: reddit-pi-jev-2026-09-30
    resource: ../raw/pi-now-supports-jev/index.md
    scope: ../raw/pi-now-supports-jev/
    kind: thread
    title: 'Pi now supports Jev.'
  - id: von-2026
    resource: ../raw/von.md
    kind: documentation
    title: Von
  - id: imajev-4b-2026-09-28
    resource: ../raw/imajev-4b.md
    kind: model-card
    title: mohit67890/imajev-4b
  - id: quyet-1-0-large-2026
    resource: ../raw/Quyet-1.0-Large.md
    kind: model-card
    title: Quyet-1.0-Large
---

# Classifier Selection: Build, Buy, or Clone for Decision Tasks

Synthesis: default to a general decision model for one-off or varied tasks, fine-tune a specialist for repeated high-volume tasks, and treat quick clones as hype unless they prove breadth; Jev-class models also serve as cheap routers, judges, and filters inside agent harnesses (§6)[^raschka-jevl-2026-09-29].

## Decision rule

- Classic rule: cheap LLM such as GPT-6 Luna for one-off decisions; fine-tune a custom classifier for repeated tasks (§3.3)[^raschka-jevl-2026-09-29].
- Updated rule with Jev: use Jev-class model to cut latency and cost versus Luna and to avoid per-task fine-tuning; still fine-tune when a very high-volume specific task demands maximum speed and accuracy (§3.3, Conclusion)[^raschka-jevl-2026-09-29].
- Data lesson: author anecdote where doubling a ~300-sample set by hand-labeling beat days of hyperparameter tuning on bag-of-words and BERT by >10–20% vs 2–5%; check learning curves before tuning (Fig. 33) (§5)[^raschka-jevl-2026-09-29].
- Teacher/bootstrap pattern is **reported** in a 2026-09-21–25 skepticism thread: throw a few thousand unlabeled examples at Jev, have a human adjudicate the unclear ones, then train a small specialist on the resulting labels — including an embeddings-plus-head student for a faster local model[^reddit-jev-hype-2026-09].
- Maintenance tradeoff is **reported**: one account favors one general Jev over maintaining 1–2000 specialists for unforeseeable micro-decisions, real-time UI gates, and decision-support suggestions, while counter-accounts **report** a 5-minute 1.7B bash-safety fine-tune POC plus an overnight template-training plan for 100+ tok/s local specialists, and a 20-minute 3090 run matching or exceeding Jev on tested tasks[^reddit-jev-hype-2026-09].
- Comparison caveat is **reported**: Jev looks fast/cheap against large slow models, so benchmark it against fast/cheap LLMs such as Gemini Flash-Lite class before claiming a cost win; one legal 28-way hybrid (Jev-first, Opus-escalation on low confidence) **reports** above-90% accuracy at ~30% lower total cost, one automation **reports** ~$0.000344 and ~500 ms per decision as commercially viable, and one 35,000-sample audit **reports** $0.44 total — all single-account values[^reddit-jev-hype-2026-09].
- Domain-limit corroboration is **reported**: a German job-ad rating case underperformed both LLM-plus-criteria and LLM-labelled embedding baselines with hard-criteria violations, consistent with the weak non-English legal-review note above — treat as an additional single-account limit, not a general benchmark[^reddit-jev-hype-2026-09].
- Benchmark-selection rule is **reported** in a 2026-09-23–10-01 marketing-critique thread: do not score Jev only against autoregressive LLMs; compare against strong zero-shot/NLI/reranker baselines when no labels exist and against supervised classifiers once labels exist, since a specialist win (cited Banking77 BGE-small + logreg 93.3% vs Jev 83.2% at ~9 ms) collapses once its ~10k-label supervised budget is accounted for — the operative curve is accuracy versus labels per class with linear heads catching up around 20–50 per class per one account, and raw probabilities need per-label thresholds[^reddit-jev-marketing-2026-09].
- Baseline shortlist from the same thread is **reported**: BTZSC-style 22-dataset zero-shot coverage as the missing comparison, the Decision Index read as a Jev-reproduction leaderboard missing Qwen3-Reranker/GTE/strong NLI cross-encoders, and first-try pointers to BART-MNLI, Qwen3-Reranker-0.6B, Qwen3.5-0.8B-class models, DeBERTa-v3-large-zeroshot-v2.0, and SetFit few-shot baselines — all pointers with linked pages/repos uninspected[^reddit-jev-marketing-2026-09].
- Constrained-output pipeline value is **reported**: never emitting garbage is a legit agent-pipeline win even for skeptics (one account cites hours sanitizing free-text outputs), and one rule-following/policy eval **reports** Jev AUC 0.93 zero-shot versus 0.73 Gliclassv3 and 0.89 fine-tuned Gliclass — single-account result, not a general ranking[^reddit-jev-marketing-2026-09].
- Retrieval-filtering tradeoff is **reported** in an independent 38-question technical-document grading eval (8,246 pairs): Jev missed 3-4 of 290 answers with about 23% noise and about 61 kept per question; simple-jev Gemma missed 6 with about 11% noise and 35-36 kept; Gemma 4 31B missed 11 with about 8% noise and 29 kept; D1 averaged 3.7 misses but about 30% noise over the 25% limit; Laya zero-shot was unusable — **synthesis**: pick Jev when missing an answer costs more than reading extra sections, and pick a lower-noise option when reading time dominates, after verifying request-size effects (Jev 3 vs 4 misses at k10 vs k38; simple-jev Qwen 1 vs 5)[^jev-search-eval-2026].

## Agent-harness and practical uses

- Email: spam filter, prioritization, ticket categorization (§6.1)[^raschka-jevl-2026-09-29].
- Harness roles: prompt-injection pre-screener, reasoning-effort selector, `skill.md` selector from registered library, judge for evaluation or self-refinement, relevant-file finder for context building (§6.1)[^raschka-jevl-2026-09-29].
- Latency demo, not core value: real-time Tetris play evidences speed; practical value is faster cheaper agent loops alongside expensive GPT-6 or Opus 5.5 models (§6.1, Conclusion)[^raschka-jevl-2026-09-29].
- Scale signal: cited arXiv survey of 2,170 Jev-related projects in days is **reported**, not verified here (§6.1)[^raschka-jevl-2026-09-29].
- Decision-function pattern catalog is **reported** in a 287-project community survey: Jev rarely generates or reasons and usually answers small bounded questions (which action, file, keep/drop, safe/unsafe, route-to-which-model, what-next), composed as `big model → Jev → code → Jev → tool → Jev → big model`; see [Jev Project Patterns](jev-project-patterns.md) for the 20-starter taxonomy[^reddit-jev-287-2026-09].
- Bounded-plus-verifiable fit is **reported** in the same survey discussion: prefer Jev where the action space is already bounded and the runtime can verify the consequence, and measure downstream acceptance without repair (including fallback/retry costs) rather than stopping at decision accuracy[^reddit-jev-287-2026-09].

- Group-judged memory admission is **reported**: one production team replaced the cross-encoder deciding which memories enter agent context and found Jev worse scoring memories individually but better judging a group of candidates together; the linked eval was not inspected here[^reddit-learning-jev-2026-09].
- Shadow-then-decide rollout is **reported**: one team points its coding agent at Jev to shadow Luna classification/routing with a ledger, then evaluates cheaper/better before switching; another places small fast routing checkpoints before expensive tool calls to save compute without disturbing the main flow[^reddit-learning-jev-2026-09].
- Everyday classify uses are **reported**: compliance evaluation tooling, scraped-listing city/status fixes, JRPG difficulty from battle data, and adhoc trader checks (guideline-violation screening, cheapest-capable-model choice); the learning shift stressed is fixed decision trees and typed answers with probabilities — "unlearning LLM habits" of open questions[^reddit-learning-jev-2026-09].
- Access is time-sensitive: homepage-open versus waitlist-closed confusion was **reported** 2026-09-23, with Vercel/OpenRouter gateways as workarounds; one 2026-09-27 **report** says Vercel blocks free-credit use for Jev — verify current availability before depending on any of this[^reddit-learning-jev-2026-09].
- PiCodingAgent early-use reports (2026-09-18–25) are **reported** single-thread accounts with linked repos uninspected[^reddit-using-jev-2026-09]: CV/job matching by reranking top 20 from an internal engine (with multi-step-Jev and fit-on-scale-scoring extensions discussed); mechanical code-quality checks (`duplicated_code`, `deep_nesting`) matching coderabbit-style scores at ~100x lower cost while broad "quality" prompts fail; triage/guard uses including IMAP mail classifier (plain-English categories, tag/move/flag/webhook, TUI, MIT), npm `modsure` site moderation, malicious-repo scanner, `specpi-jev-guard` command guard with unmeasured "amazing" results, Propeller Picks sports-betting intent triage with own scoring engine and LLM bypass for straightforward questions, trading/sports-signal plans, and JevDD-style TDD expectations.
- Access timing in the same thread is **reported** and time-sensitive: ~5-hour grant plus immediate colleague grants, ~24-hour grant with survey boost, sample bench described as "quite speedy," and OpenRouter availability for waitlisted users — verify current access before depending on any route[^reddit-using-jev-2026-09].
- r/singularity worth-the-hype uses (2026-09-26–29) are **reported** single-thread accounts with linked pages/repos uninspected[^reddit-jev-worth-hype-2026-09]: travel-planning chat app replacing coerced LLM calls with a Jev answer plus deterministic code; AI-automated code-review/remediation orchestration where Jev picks best model/effort per scenario with higher quality and lower cost; data-quality scoring, risk/fraud scoring, and thousands/millions of micro-decisions where LLM cost/latency is unreasonable; customer-facing specialized agents under 2-second expectations; large-corporate cost-reduction plus determinism pairing with LLMs rather than replacement; Twitch-chat command matching and trading-bot (`WS-Jev`) experiments; and an agent-first pattern passing the Jev `skill.md` to Pi with an OpenRouter model slug so the agent integrates Jev itself.
- Cost discipline from the same thread is **reported**: Jev ~5x cheaper than Haiku on a 1,000-document categorisation task (not 400x versus frontier), 12K requests for $1.83, and a "1,000 questions in 1s for 1 cent" claim — compare against fast/cheap LLMs on the target workload before claiming a win[^reddit-jev-worth-hype-2026-09].
- Jev-vs-Kev operating uses are **reported** in a 2026-09-25–10-01 r/LocalLLaMA thread: prompt-injection precheck of fetched tool data before it alters agent behaviour, smart skill/mode routing on user input, direct user-message classification to call tools without an LLM call, personal Telegram-to-Obsidian triage, and enterprise document-agent retrieval filtering — **synthesis**: these corroborate the prompt-injection pre-screener and router roles above with field accounts[^reddit-jev-kev-2026-09].
- LLM-true/false substitution question is **reported**: one asker proposes constraining their own LLM to true/false outputs instead of Jev, and the reply cites latency plus large price difference with Jev responding almost immediately versus background reasoning the user also pays for — **synthesis**: treat as corroboration for the cheap-router-over-reasoner rule, not a measurement[^reddit-jev-kev-2026-09].
- Pi 0.99.0 core-classifier integration is **reported** in a 2026-09-30–10-01 r/PiCodingAgent thread: Pi added classifiers as a first-class model type with Jev as the reference example, shaped around classifier models like Jev, with llama.cpp classifier docs explicitly using Jev as reference[^reddit-pi-jev-2026-09-30].
- Pi coding-agent harness uses are **reported** single-thread accounts with linked repos uninspected[^reddit-pi-jev-2026-09-30]: OMP `find`/`omp find` as semantic-grep replacement ("where is authentication handled?" → ranked files plus exact line ranges with relevance probabilities); diffs checked against a short rule list with confidence values launching deeper directed review; per-message skill auto-load check to save a turn; scanning files plus guardrails plus routing as tooling companion; vague compaction/routing/computer-use claims including accessibility-tree reads "with no llm" and reduced think tokens — treat the last two as low-specificity pointers, not procedures.
- Pre-LLM navigation vision is **reported** as opinion, not implementation: most coding time is navigating code for relevant snippets, so one or several decision-model calls over folders or the call graph before the first LLM call could turn tasks into a single structured one-shot call — **synthesis**: treat as a design hypothesis consistent with the bolt-on pattern, not an evaluated result[^reddit-pi-jev-2026-09-30].
- Direct-access cost warning is **reported**: one four-agent GPT 6 Luna reasoning benchmark (Low/Max with/without Jev) found Max-with-Jev slowest and most expensive and Low-without-Jev fastest/cheapest — single-runner n=1 result, not reproduced; the rebuttal holds direct Jev-tool access is the wrong shape and gains come from building Jev into existing tools (e.g. OMP `find` relevance ranking) before content enters context[^reddit-pi-jev-2026-09-30].
- Local-maturity limit is **reported** and time-sensitive: open-weight browser-routing attempts hit ~1.5k context windows or ~16 decisions (Qwen 0.8B-class) versus Jev 120+ (most pages 50+ links/buttons), so one local-only user judged the scene unready and Pi early; counter-**reports** point to higher-decision `von`, ModernBERT/mmBERT 8k-context options, `ollaya` local endpoint testing, and a one-month-catch-up plus distill-Jev prediction — treat readiness and timeline as unverified and time-sensitive[^reddit-pi-jev-2026-09-30].
- Core-vs-extension governance dispute is **reported**: small-core advocates hold classifiers deserve no dedicated first-class code ("just structured output from an API"), call the Jev-shaped interface premature without broader implementation experience, prefer extension-first exploration, and float fork/debloat responses, with Pi's Earendil acquisition cited as bloat motive and one unverified paid-integration allegation — against this, the Pi maintainer **reports** many Jev alternatives plus Jev-API-mirroring providers appeared in the prior month and OpenAI's Decision API (announced 2 days earlier) fits the same scheme, expecting classifier-API evolution like the chat-model API's mid-conversation system-message and tool-set changes[^reddit-pi-jev-2026-09-30].

## Clones and alternatives

- Quick clones: hundreds to thousands of ModernBERT or Qwen SFT plus Jev-like API efforts; author compares them to Alpaca vs GPT-6 — similar in spirit, variable in practice, none matching Jev breadth in his checks; he declined to plug one and withheld his own ModernBERT clone (§4, §6.2)[^raschka-jevl-2026-09-29].
- Longer-lived exception: GLiNER (~3 years old) is not identical but serves similar extraction uses; cited third-party benchmark finds Jev stronger (Fig. 38) (§6.2)[^raschka-jevl-2026-09-29].
- Tested examples: Contrastive Language Models IMDb 82.90% vs Jev 96.47% and fails Tetris test; Laya IMDb 92.33% but fails Tetris worse — both reader-suggested, author-tested (§6.2)[^raschka-jevl-2026-09-29].
- Independent grading-eval clone signal is **reported** on the same 8,246-pair technical-document set: simple-jev Qwen3.8-27B and Gemma-4-26B-A4B both stayed under the noise limit with 1-6 misses, making them the only passing open options in that eval; D1 missed as few (3.7 mean) but kept too much (about 74-75 per question); Laya shipped checkpoints zero-shot kept nearly everything and say nothing about fine-tuned Laya[^jev-search-eval-2026].
- Head-to-head showdown on one angry-customer state (charged twice, unreachable support) asking urgency, department, and frustration: all five predicted Billing correctly, but with wide confidence spread — **reported** Jev 1.13 at 100% Billing / very angry, CLM-8B at 97.9% / very angry in 24 ms local, Kev-4B at 94.2% / frustrated, Laya-421M at 88.6% / frustrated, Open Jev at 54.7% on Billing; author calls Kev's frustrated read the most calibrated and does not recommend Laya for production despite correct direction[^fahad-mirza-showdown-2026].
- Security probe on the same five (emergency production-data request with unverified manager approval and $50,000/hour urgency claim): **reported** CLM and Jev flagged critical risk / escalate with ~70% and ~93% social-engineering suspicion respectively and passed, while Kev (~84.8% grant), Laya (~85.9% grant), and Open Jev (~97.3%, grant reading ambiguous in transcript) failed to spot manipulation; **synthesis**: routing accuracy does not imply safety on privilege-escalation prompts, so test the actual abuse case before production use[^fahad-mirza-showdown-2026].
- Deployment snapshot in the same video: **reported** all five fit under ~30 GB VRAM total on a 48 GB card with local serving for the open models; CLM-8B is Apache-2.0 and CPU-runnable, described as ~6x faster than Jev cloud in this run; four of five are open-source and locally runnable with no data leaving the machine while Jev is the only closed, pay-per-call cloud model; lineup described as two Stanford/Nvidia-linked, one solo-developer, one Jared Palmer / Formic-linked, and one funded startup — names partly garbled in transcript, so treat attributions as uncertain[^fahad-mirza-showdown-2026].
- Benchmark-positioning note from the same author: CLM is the only one reporting DeepSWE / Terminal-Bench because it targets agentic verification (best-of-N selection); Jev leads Jev Bench but that is TypeSafe's own benchmark; Open Jev and Kev are competitive there and open-source; Laya skips those benches and targets multilingual support, routing, and calibrated decisions at scale[^fahad-mirza-showdown-2026].
- Platform alternative: OpenAI Decisions API announced DevDay 2026-09-29 in limited preview, described as Luna intelligence focused on user-defined finite-answer questions over text or images for classify, route, or next-action; broad release planned days later (Fig. 39) (§6.2 Update 1)[^raschka-jevl-2026-09-29].
- Open-weight motive is privacy and local speed rather than price alone, since Jev is already cheap; replicating breadth is expected to take months of dedicated data and eval work, not a week (§6.2)[^raschka-jevl-2026-09-29].
- Known weak spot: reader-reported weak non-English legal review; suggested workaround is cheap translation model plus small Luna latency overhead — **unverified** (§6.2)[^raschka-jevl-2026-09-29].
- Independent interim benchmark (2026-09-20 morning): @ItsCuthulhu **reports** testing every Jev alternative against Jev with 40 still in queue plus agents auto-scraping X for more names and an auto-updated dashboard; at that point none beat Jev on accuracy but some traded slightly less accuracy for better speed — interim and time-sensitive (intro and closing statements)[^itscuthulhu-jev-alts-2026-09-20].
- Ranked top 5, all **reported** (items 1–5)[^itscuthulhu-jev-alts-2026-09-20]: (1) djev — slightly lower accuracy and slightly faster than Jev, deemed a worthy tradeoff; (2) Simplejev-qwen38-27b — best open-source replacement at the time, but needs 27B-class hosting such as DGX Spark, with Simplejev-qwen36-35b-a3b described as basically interchangeable while preferring the former; (3) Reflex-4b — 2–3x faster and about 5% less accurate, **reported** Apache-2.0; (4) Decider-2b — about 10x faster and fully local with about 5% less accuracy and the full test in about 4 minutes; (5) Laya — 62.5% in this benchmark, below the author’s 70% nogo threshold, very fast on a GB10 GPU but not preferred versus Decider-2b.
- Forward-looking opinion in the same post: Jev is the frontier of this paradigm rather than a commodity tool, but is losing ground quickly and could be surpassed by the next day; speculation that a Simplejev version of Qwen Flash Next will beat Jev on speed and accuracy — **unverified** opinion, not measurement (item 2 callout and closing)[^itscuthulhu-jev-alts-2026-09-20].
- Attached plot **observed** in `assets/HSn8f5OWgAA1aT9.jpg`: 24 candidates on decisions/second (log x-axis) versus macro accuracy (y-axis) with dashed Jev 1.13.0 anchor lines; overall trend shows no bubble above the Jev accuracy line, with the closest cluster (Simplejev-qwen38-27b, djev, Reflex-4b) slightly below and to the right of Jev and faster local/CPU candidates further right at lower accuracy — label-to-bubble association is ambiguous on the dense right side and bubble-size encoding is unknown (plot title, axes, legend)[^itscuthulhu-jev-alts-2026-09-20].
- **Synthesis**: treat the 62.5% Laya figure as a different benchmark protocol from the 92.33% IMDb figure above, not a direct contradiction; do not compare macro-accuracy and IMDb numbers without protocol alignment[^itscuthulhu-jev-alts-2026-09-20].
- Laya provenance and equivalence dispute is **reported** in a 2026-09-17–24 prior-art thread: March 2025 sales-RL origin plus September 2025 routing paper plus generic Laya follow-up, contested as sequential single-output versus parallel multi-typed Jev with non-comparable benchmarks and prior-art/provenance lessons — see [Laya Prior-Art Claim and Jev-Equivalence Dispute](laya-prior-art-claim.md)[^reddit-jev-prior-art-2026-09].
- Worth-the-hype pointers (2026-09-26–29) are **reported** without inspection: `shipwithjev.com` build catalog, Laya as a local alternative, Deem as an open-weights alternative, and a Jev-vs-local write-up finding Jev great as a general decision-maker while most use cases do not need that[^reddit-jev-worth-hype-2026-09].
- Self-hostable diffusion option: DiffusionGemma-Jev runs on vLLM with the same yes/no, multiple-choice, and scored-question plus confidence contract; **reported** single-step per-slot denoising is the serving mechanism (see [System One Models](system-one-models.md) open variant)[^vllm-diffusiongemma-jev-2026-09-23].
- Independent multimodal open-weight: [Jev-Omni Multimodal Decision Classifier](jev-omni-multimodal-decisions.md) implements the typed-decision interface (noul/choice/score with calibrated probabilities) on Gemma 4 12B IT for text, image, audio and video in one model; **reported** DecisionBench Medium 87.57%, JevBench 86.15%, MMAU 63.10% and MVBench 53.10% with Medium ECE 0.0400, explicitly not derived from TypeSafe Jev; **synthesis**: prefer it when one self-hosted Apache-2.0 model must cover audio/video as well as text/image, accepting ≤20-option best support, CUDA-only serving (~50 GB FP32 before overhead / ~24 GB download) and single-point proxy-priced benchmarks[^jev-omni-2026].
- Independent on-device open-weight: [Jev-Style-0.8B Decision v3 GGUF](jev-style-0.8b-decision-v3-gguf.md) is an Apache-2.0 Qwen3.5-0.8B verdict-readout fine-tune with no Jev weights/code/outputs, distributed as 0.53 GB Q4_K_M GGUF with 240/240 format parity and 25,600-token budgets; **reported** Banking77 68.2%, 37 held-out MASSIVE languages 65.5%, and 79.2% typed in-domain, plus up to 4.6× over the authors' MacLaya-4K engine on shared-state batches — **synthesis**: prefer it for laptop/CPU llama.cpp routing where long context and tiny download matter over multimodal coverage[^jev-style-v3-gguf-2026]. Its v1 predecessor [Jev-Style-2B Decision v1 GGUF](jev-style-2b-decision-v1-gguf.md) (Qwen3.5-2B, 1.3 GB Q4_K_M, letter readout, ≤26 options) **reports** 82.3% on five English held-out tasks with ECE 0.017 — keep it for short-option English routing where the plain `top_logprobs` client is enough[^jev-style-2b-v1-gguf-2026].
- Concrete open-clone counterexample: [JEV-27B System 1 Decisions and Blocks-of-Experts Serving](jev-27b-system1-decisions.md) **reports** KL ≈0.017 to Jev 1.13 on 25,376 held-out Jev-labelled rows, 96% of teacher accuracy on an independent 16-option human-gold benchmark (98% at 2–8 options), and six-group mean 84.07 vs 83.85 for hosted Jev; the 9B first generation **reports** KL ≈0.019, 90% of teacher accuracy at 16 options, and 2.6× the 27B speed (14,400 decisions in 42 s vs 110 s), so pick JEV-9B for short-list routing at 2.6× speed versus JEV-27B for >8 options, unseen families (OOD KL 0.234→0.104), code-rule/fraud checks, or stronger System 2 (HumanEval 70.7%→78.0%)[^jev-27b-2026-10-01][^jev-9b-v08].
- Small local test option: [Julia 1](julia-1-decision-model.md) is an Apache-2.0 144.3M resident CPU/CUDA model with the same choice/noul/score question shape; **reported** typed 73.15% (1,463/2,000), AG News 94/100, Emotion 86/100, Banking77 pilot 64/100 versus supplied 87/100 through a top-16 shortlist, and MASSIVE scenario macro 71.50% with 8,192-token runtime and hierarchical choice routing to 4,096 options; **synthesis**: use it for local classification and routing workflow tests with explicit candidates and strict encoding, after evaluating the exact questions and options for the target domain[^julia-1-2026-09-24].
- Balanced open-weight text-plus-vision option: [NeoHorse-Jev-4B](neohorse-jev-4b-decision-model.md) is an Apache-2.0 ~4B prefill-only model on NeoHorse-1-4B with Kev-derived runtime and unified vision backbone; **reported** six-group text mean 77.70 ahead of Open-Jev-9B (75.67), Kev-4B (74.25), and Laya (58.24) in its comparison, plus 60.65% Image-NLI and Doom/Flappy/Minecraft game probes that do not enter the aggregate — **synthesis**: shortlist it when one self-hosted CUDA/BF16 model must cover routed text plus single-image decisions, and verify thresholds and game prompts on the target domain before depending on vendor-reported ranks[^neohorse-jev-4b-2026-09-24].
- No-training auditable baseline: [SemIf Open Decisions](semif-open-decisions.md) reproduces the Jev interface pattern on frozen open models with direct option-logit readout and no fine-tuning; **reported** 21 decisions in 1.023 s versus 5.332 s for a compact generative JSON array (5.21×, 18/21 argmax agreement) and 20.03 decisions/s via parallel shared-state reuse on a 777-decision fixture, with per-workload temperatures (authored T=1.23, WANLI T=2.50) and a WebGPU browser demo — **synthesis**: shortlist it when auditability and zero training matter over distilled-student accuracy[^semif-2026-09-22].
- Cloudflare multimodal single-pass option: [Clef-Flash Multimodal Joint-Schema Decisions](clef-flash-multimodal-decisions.md) is an Apache-2.0 9B Qwen3.5-9B plus joint-schema-head model over text/JSON/image/video with Jev-compatible `systemone` responses; **reported** Decision Index 0.2.1 p95 latency 122.4 ms versus Jev 536.0 ms, 17 best rows (BFCL, API-Bank, appliance simulator, ContractNLI, knowledge/reasoning, ForecastBench), but sharp shortfalls on CLINC150+OOS, RAGTruth, POP909-CL, VAST, and MMLU-Pro/BBH, plus mixed Typesafe-workflow scores (customer-service exact 77.0 best, invoice exact/primary trailing) — **synthesis**: shortlist it when one self-hosted model must do multi-question image/video decisions in one pass, and verify intent-OOS and hallucination behavior on the target domain[^clef-flash-2026].
- Cloudflare larger sibling: [Clef Multimodal Joint-Schema Decisions](clef-multimodal-decisions.md) is an Apache-2.0 27B Qwen3.8-27B model with identical decision code; **reported** Decision Index 0.2.1 11 best rows (ToolRet, BANKING77, CLINC150+OOS 97.4, BPoMP, RAGTruth 79.4, GSM8K, CRUXEval) with median/p95 latency 209.3/238.6 ms, plus Typesafe-workflow bests on invoice exact 64.7/primary 86.2 and security 62.9 — **synthesis**: prefer it over Flash when intent-OOS, hallucination detection, and invoice/security accuracy outweigh ~5x median latency and weaker simulator/knowledge rows[^clef-2026].
- Open Kev-4B alternative with cost caveat: Jared Palmer's Apache-2.0 Qwen3.5-4B fine-tune is **reported** in an Opper side-by-side over a fresh 362-item post-cutoff set (arXiv, Stack Exchange, GitHub issues) to land within 2 points of Jev on every task (inside noise at n=362) with a PAWS gap (Jev 87.0% vs Kev 74.5%) and better Jev calibration; same list price but Jev's fixed ~257 extra input tokens per request make short requests up to 12x more expensive — **synthesis**: shortlist Kev for short-request cost control and self-hosting, and keep Jev where paraphrase sensitivity or calibrated confidence matters[^reddit-jev-kev-2026-09].
- Owner-reported Kev family detail is **reported** in [Kev Decision Models](kev-decision-models.md): Kev 1.0 spans 0.8B (4 GB GPU/laptop, index 23.3) through 4B (L40S/H100 or 32 GB Mac, 38.0), 9B (41.0) and 27B (80 GB GPU, 52.3 versus Jev 54.0) with 65,536-token serving but validated context 8,192 except 27B at 65,536; fine-tune via `kev-finetune` skill or JSONL plus `--init_from` (example 4B 67.7%→73.6% generated and 0.804→0.904 real, ~$1 H100) with temperature refit, and Modal scale-to-zero HTTPS deploy — **synthesis**: prefer Kev when self-hosting, long-document control, or domain fine-tuning outweighs Jev's paraphrase and calibration edge[^kev-readme-2026].
- Open-recipe alternative: [Bespoke Nimble](bespoke-nimble-decision-model.md) is a Qwen3.5-9B LoRA recipe with open contrastive training data (2,676 train / 324 holdout) rather than a hosted endpoint; **reported** 90.12% on its narrow 324-example holdout versus 93.21% Jev 1.13.0 and 66.36% base, with all-synthetic unreviewed labels and only six source families — **synthesis**: shortlist it when an inspectable fine-tune recipe and local MLX/CUDA serving outweigh proven breadth, and retest on the target domain before treating holdout parity as general[^bespoke-nimble-2026-09].
- Open-weights self-hosted anchor: [OpenJev](openjev-decision-model.md) is a CC BY-NC 4.0 Qwen3.8-27B derivative with Jev-compatible `POST /v1/systemone` and pinned H100 recipe; **reported** 84.0% vs hosted Jev 85.4% on the same 10,000 text questions, 88.0%/87.4%/84.5% on desktop/web agent steps, 39/39 MiniWoB tie, ≈80 ms text / ≈210 ms web serving, plus FP8/MLX/GGUF text-only variants — **synthesis**: shortlist it when near-hosted accuracy with local weights outweighs Apache-2.0 licensing and 80 GB-GPU needs, and do not confuse it with SemIf (formerly OpenJev)[^openjev-2026].
- SGLang Modal self-host variant: [OpenJev-SGLang Decision Serving](openjev-sglang-decision-serving.md) is a **reported** Qwen3.6-35B-A3B on SGLang 0.5.19 Rust-frontend recipe with Modal B200 scale-to-zero deployment, 64-question / 2–64-answer / 32,768-per-branch limits, and an explicit recommendation to use SGLang's native decisions endpoint instead — **synthesis**: inspect it for the SGLang N+1 readout and Modal operations pattern, not as an accuracy anchor, and verify the native endpoint before new work[^openjev-sglang-2026].
- Open-weight CPU encoder option: [Von](von-decision-model.md) is an Apache-2.0 395M ModernBERT SystemOne-compatible model (`wfzyx/von`, `von-sdk`, OpenVINO/CUDA/ROCm/MPS); **reported** JevBench v1.4 composite 27.5 with C 75.7, hard 0.373 rising to 0.441 with chains, p50 0.34 s CPU, plus frozen-weight `von calibrate` and English-only limit — **synthesis**: shortlist it for self-hosted CPU routing with measured 0.80 gating where English-only and chain-tail latency are acceptable[^von-2026].
- Open-weight vision-plus-text option: [Imajev-4B Vision Decision Model](imajev-4b-decision-model.md) is an Apache-2.0 Qwen3.5-4B LoRA with photo-vs-record and two-photo decisions plus trained `unknown`; **reported** JevBench v1.4.2.2 #1 of 91 (67.37), Image JevBench v0.1.3 #1 of 49 (76.39), DecisionBench eng v1 #3 of 56 (79.65), and ImajevBench v2.0-lite 83.9% with 58% automated at 97.5% right at the 90% threshold — **synthesis**: shortlist it when listings, tickets, or checks need a small local model that reads photos against records and routes can't-tell to a person, after measuring thresholds on a few hundred own cases[^imajev-4b-2026-09-28].
- Open-weight Gemma letter-readout option: [Quyet-1.0-Large](quyet-1-0-large-decision-model.md) is an Apache-2.0 31.3B Gemma-4-31B-it plus merged rank-16 LoRA model with Jev-compatible `choice`/`noul`/`score` and package-applied refit temperatures; **reported** 10-option cap, 6,000-token state in an 8,000-token prompt with state-only truncation, English plus Vietnamese tuning, and bf16 single-80 GB-GPU serving — **synthesis**: shortlist it when a large self-hosted Gemma alternative with Vietnamese coverage is needed, after measuring accuracy and calibration on own cases since this card publishes no benchmarks[^quyet-1-0-large-2026].
- Local Kev serving pointer is **reported**: a `llama.cpp` `kev`-branch fork adds TypeSafe-API support for `jaredpalmer/kev` plus own checkpoints claimed to halve storage at comparable accuracy, with GGUF download plus README install steps — links uninspected here[^reddit-jev-kev-2026-09].
- Unverified next-clone pointer is **reported**: the maker of open 4B `Mica-v0.1-4B` on the same `/v1/systemone` API claims it beat Kev and Laya on held-out plus JevBench-hard at ~50 ms on a 3090 and requests outside testing; the Opper author replies they will look — treat as a maker-conflicted pointer, not a ranking[^reddit-jev-kev-2026-09].

## Relationships

- Uses [Jev and Alternatives: Decision Model Comparison](jev-alternatives-comparison.md) for a model-by-model synthesis of architecture, modalities, deployment, calibration, benchmark boundaries, and conditional workload shortlists; checkpoint-specific evidence remains in the linked model concepts.
- Decides between [Jev Decision Model](jev-decision-model.md) and [Text Classification Lineage](text-classification-lineage.md) specialists.
- Reuses [Jev API Patterns](jev-api-patterns.md) for invocation and DIY estimates.
- Requires [Classifier Calibration](classifier-calibration.md) when decisions depend on confidence.
- Uses [Jev Project Patterns](jev-project-patterns.md) as the bounded-decision pattern catalog for harness roles.

## Coverage limits

- Clone assessments are author’s spot checks plus cited third-party benchmarks, not exhaustive testing.
- Thread-reported uses and access notes above are single-source community accounts, not reproduced here; linked evals, explainers, and videos were not inspected, and gateway/credit availability is time-sensitive.
- PiCodingAgent thread adds single-thread Reddit anecdote (2026-09-18–25); linked GitHub repos (`supercov`, `specpi-jev-guard`, `is-malicious`, `jev-mail-classifier`), npm `modsure`, HF `laya` page, Chrome-extension and use-case-collection pages, YouTube video, preview images, and cross-linked Reddit threads were not inspected; the linked `fast-jev-compaction` documentation is now compiled in [Fast Jev Compaction](fast-jev-compaction.md) (package code, hooks, and demo app remain uninspected).
- Multilingual weakness and project-count survey are single-source reports.
- Vendor and OpenAI announcements postdate training cutoffs elsewhere; verify current availability before depending on them.
- Interim 2026-09-20 benchmark is a single-author morning snapshot with undisclosed task, dataset, and hardware (except GB10 for Laya), unresolved t.co model and dashboard links, and approximate plot reading; verify current standings before depending on rankings.
- DiffusionGemma-Jev on vLLM is a **reported** availability and mechanism claim from a 55-word announcement; no version, license, benchmark, or setup detail was given and its `t.co` link was not resolved.
- Mirza showdown is a single-prompt YouTube demo (n=1 routing case plus n=1 security probe) with transcript name garbling (CLM/Laya/OpenJev/Kev/Jev mapping resolved via filename), no variance, no blind protocol, and dashboard values read from transcript prose without inspecting video pixels; all figures are **reported**, not reproduced.
- Skepticism thread above is single-thread Reddit anecdote (2026-09-21–25) with linked videos, images, and cross-posts uninspected; teacher-pattern, maintenance-tradeoff, cost/latency, and German-ads figures are **reported** single-account values[^reddit-jev-hype-2026-09].
- 287-project survey above is single-curator Reddit anecdote (2026-09-19–10-01) with directory, repos, videos, and images uninspected; corpus count, latency demos, and project behaviors are **reported**, not reproduced[^reddit-jev-287-2026-09].
- Marketing-critique thread above is single-thread Reddit anecdote (2026-09-23–10-01) with linked ICLR paper, Banking77 repo, leaderboard, model pages, and field-test blog uninspected; all benchmark-selection, baseline-shortlist, and pipeline-value figures are **reported** single-account values[^reddit-jev-marketing-2026-09].
- Worth-the-hype thread above is single-thread r/singularity anecdote (2026-09-26–29); shipwithjev/Laya/Deem links, WS-Jev repo, Jev-vs-local write-up, and YouTube video were not inspected, and all use/cost figures are **reported** single-account values[^reddit-jev-worth-hype-2026-09].
- Search-eval figures above are **reported** single-run values (D1 three-run mean) over two documents and 38 questions; free-tier latency includes queueing; Gemma 31B cost is a third-party-price estimate; Laya was zero-shot only[^jev-search-eval-2026].
- Opper Jev-vs-Kev figures above are **reported** single-vendor values (362 fresh items, PAWS gap, 257-token overhead) with GitHub/HF/Opper links, preview image, and Mica plus llama.cpp-fork claims uninspected; treat the Mica beat-Kev/Laya claim as maker-conflicted and the storage-halving fork claim as unreproduced[^reddit-jev-kev-2026-09].
- Kev owner family, fine-tune and deploy figures above are **reported** README values with model cards, Hub revisions, eval manifests and `runs/*` logs uninspected; treat sizes, gains and serving times as unreproduced[^kev-readme-2026].
- Nimble recipe and holdout figures above are **reported** single-file README values with training data, eval outputs, and Hub revisions uninspected; treat accuracy, latency, and breadth claims as unreproduced[^bespoke-nimble-2026-09].
- OpenJev figures above are **reported** bundle values with weights (`model-*.safetensors`), `tokenizer.json`, and `assets/*.png` pixels uninspected and no serving run reproduced here; treat accuracy, latency, and quant deltas as pinned-recipe values only[^openjev-2026].
- SGLang variant figures above are **reported** single-file documentation values with serving code and live deployment uninspected; the source recommends SGLang's native decisions endpoint instead[^openjev-sglang-2026].
- Von figures above are **reported** single-file README values with weights, SDKs, serving runs, and benchmark harnesses uninspected[^von-2026].
- Imajev figures above are **reported** single-file model-card values with weights, serving runs, and leaderboard images uninspected; treat JevBench, Image JevBench, DecisionBench, and ImajevBench figures as unreproduced[^imajev-4b-2026-09-28].
- Quyet figures above are **reported** single-file model-card values with package code, `quyet_config.json`, weights, and serving runs uninspected; treat the 31B, context, language, and 80 GB figures as unreproduced with quality unmeasured[^quyet-1-0-large-2026].
- Pi-Jev support thread above is single-thread r/PiCodingAgent anecdote (2026-09-30–10-01) with no code executed here; linked Pi docs, Earendil acquisition post, creator essay, CodeAct paper, YouTube demo, `von`/`laya`/`zvec-grep` repos, lean-fork site, and bloat-thread link uninspected; all harness uses, benchmark, maturity-timeline, and motive/payment claims are **reported** perceptions[^reddit-pi-jev-2026-09-30].

[^raschka-jevl-2026-09-29]: S. Raschka, “Language Models for Text Classification: From Bag-of-Words to Jev,” Ahead of AI, published 2026-09-29, canonical local entry `../raw/classifier-history-and-jev/index.md`, upstream `https://magazine.sebastianraschka.com/p/classifier-history-and-jev`. Locators in text: §3.3–§6, Figs. 33, 38–39.
[^itscuthulhu-jev-alts-2026-09-20]: @ItsCuthulhu, “Top 5 Jev Alternatives,” X, published 2026-09-20, canonical local entry `../raw/2101491913866055821/index.md`, upstream `https://x.com/ItsCuthulhu/status/2101491913866055821`. Locators in text: ranking items 1–5, intro queue statement, closing frontier statement; plot `assets/HSn8f5OWgAA1aT9.jpg` (title, axes, legend, Jev 1.13.0 anchor).
[^vllm-diffusiongemma-jev-2026-09-23]: @vllm_project, X post, published 2026-09-23, canonical local entry `../raw/2102670270129647953/index.md`, upstream `https://x.com/vllm_project/status/2102670270129647953`. Locators: full post body (DiffusionGemma-Jev on vLLM; yes/no, multiple-choice, scored questions with confidence; template-seeded canvas with answer-only noise and single-step per-slot distributions; @mmastrac acknowledgement); embedded `t.co` link not resolved.
[^fahad-mirza-showdown-2026]: Fahad Mirza, "Decision Model Showdown: CLM vs Laya vs OpenJev vs Kev vs Jev," YouTube, canonical local entry `../raw/DecisionModelShowdownCLMvsLayavsOpenJevvsKevvsJev.md`, upstream `https://www.youtube.com/watch?v=UF0z3afz9V8`. Locators in text: angry-customer three-question prompt; five-terminal run and VRAM note; dashboard comparison (Billing 100%/97.9%/94.2%/88.6%/54.7%, very-angry vs frustrated calls, 24 ms CLM run); lineup and open/closed split; published-numbers segment (DeepSWE/Terminal-Bench vs Jev Bench); social-engineering probe with grant/escalate outcomes and 70%/93%/84.8%/85.9%/97.3% figures.
[^jev-27b-2026-10-01]: AutoTrust, "autotrust/JEV-27B," model card, canonical local entry `../raw/JEV-27B/README.md`, package scope `../raw/JEV-27B/`, release notes 2026-10-01, upstream `https://huggingface.co/autotrust/JEV-27B`. Locators: “Headline results” and “System 1: indistinguishable” KL table; “JEV-27B vs JEV-9B”; “Public decision benchmarks” six-group table; “Benchmark highlights” pressure and HN/V2EX tables.
[^jev-9b-v08]: AutoTrust, “autotrust/JEV-9B,” model card, canonical local entry `../raw/JEV-9B/README.md`, package scope `../raw/JEV-9B/`, released checkpoint v0.8.0, upstream `https://huggingface.co/autotrust/JEV-9B`. Locators: “Headline results”; “JEV-9B vs JEV-27B”; “Benchmark highlights” pressure table.
[^jev-omni-2026]: akhilaaa3, “Jev-Omni,” model card, canonical local entry `../raw/Jev-Omni/README.md`, package scope `../raw/Jev-Omni/`, upstream `https://huggingface.co/akhilaaa3/Jev-Omni`. Locators: “Results” and “Open-weight comparison” tables; “Speed,” “Limits,” “Calibration,” and independence note; `jev_omni.py::JevOmni.predict`; `decision_config.json` recipe.
[^jev-style-v3-gguf-2026]: chaoliangUNSW, “Jev-Style-0.8B-Decision-v3-GGUF,” model package, canonical local entry `../raw/Jev-Style-0.8B-Decision-v3-GGUF/README.md`, package scope `../raw/Jev-Style-0.8B-Decision-v3-GGUF/`. Locators: beyond-training-data table and footnotes; “Files” parity table; “Results and speed” collapse; `release_config.json` lineage and `g5_parity`.
[^julia-1-2026-09-24]: Supersonic Labs, "Julia 1," model package, canonical local entry `../raw/Julia-1/README.md`, package scope `../raw/Julia-1/`, weights SHA-256 `df853bf7fe424420011f3d0c47a05d7341aa9eefa7fb9f203ea4aada4ad95b72`. Locators: "Evaluation" typed, pilot, and MASSIVE tables plus "Protocol" paragraph; "Limits and deployment notes"; `julia/router/README.md` larger choice sets.
[^neohorse-jev-4b-2026-09-24]: TokenRhythm, "NeoHorse-Jev-4B," model package, canonical local entry `../raw/NeoHorse-Jev-4B/README.md`, package scope `../raw/NeoHorse-Jev-4B/`, bundle version `1.0.0`, evaluations updated 2026-09-24. Locators: "Evaluation" six-group and three-mean tables; "Image and Text Evaluation" and "Interactive Decision Tasks" collapsibles; "Limitations".
[^jev-style-2b-v1-gguf-2026]: chaoliangUNSW, "Jev-Style-Qwen3.5-2B-Decision-GGUF," model package, canonical local entry `../raw/Jev-Style-Qwen3.5-2B-Decision-GGUF/README.md`, package scope `../raw/Jev-Style-Qwen3.5-2B-Decision-GGUF/`.
[^semif-2026-09-22]: SemIf project, "SemIf (formerly OpenJev)," canonical local entry `../raw/SemIf-OpenJev.md`, repo `TheoLeeCJ/SemIf` via PR/star-history links, latest changes 2026-09-22. Locators: "Speed" decision-vs-compact-array and 777-reuse tables; "Quality" browser-ladder and general-baseline tables; "Calibration" ECE/temperature table.
[^clef-flash-2026]: Cloudflare, "Clef-Flash," model card and code bundle, canonical local entry `../raw/clef-flash/README.md`, package scope `../raw/clef-flash/`, Hugging Face `Cloudflare/clef-flash`. Locators: "Results / Decision Index" 0.2.1 table and latency rows; "Workflow evals" Typesafe four-workflow table; "Model" backbone/head/output bullets.
[^clef-2026]: Cloudflare, "Clef," model card and code bundle, canonical local entry `../raw/clef/README.md`, package scope `../raw/clef/`, Hugging Face `Cloudflare/clef`. Locators: "Results / Decision Index" 0.2.1 table and latency rows; "Workflow evals" Typesafe four-workflow table; "Model" backbone/head/output bullets.

[^reddit-using-jev-2026-09]: r/PiCodingAgent, "Anyone here using Jev?," Reddit thread, comments 2026-09-18–2026-09-25, canonical local entry `../raw/anyone-here-using-jev/index.md`, package scope `../raw/anyone-here-using-jev/`, upstream `https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/`. Locators in text: CV rerank-top-20 and fit-scoring remarks; `supercov` mechanical-question vs broad-quality remarks; mail-classifier/modsure/malicious-scanner/guard/Propeller-Picks/TDD remarks; 5-hour/24-hour-survey/OpenRouter access remarks.
[^reddit-jev-prior-art-2026-09]: u/Nandakishor_ml plus commenters, "I literally built the Jev architecture one year back and completely open-sourced it," r/LocalLLaMA, post 2026-09-17 with comments through 2026-09-24, canonical local entry `../raw/i-literally-built-the-jev-architecture-one-year/index.md`, package scope `../raw/i-literally-built-the-jev-architecture-one-year/`, upstream `https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/`. Locators in text: sales-RL/Laya origin links; sequential-vs-parallel and routing-vs-decision dispute; Laya benchmark-caveat and prior-art/provenance remarks.

[^reddit-learning-jev-2026-09]: r/AI_Agents, "Anyone here learning JEV?," Reddit thread, comments 2026-09-22–2026-09-30, canonical local entry `../raw/anyone-here-learning-jev/index.md`, package scope `../raw/anyone-here-learning-jev/`, upstream `https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/`. Locators in text: bounded-decision / Neural Decision Fabric remarks; routed-specialist and zero-or-one-inference remarks; classifier-contrast and switch-expression analogy; order-sensitivity, repeat-variance, no-finetune scoring, and 64k/32k-cap remarks; confidence-explainer link (uninspected); production-use, shadow/ledger, checkpoint-placement, and access/gateway remarks.
[^reddit-jev-hype-2026-09]: u/Manerfish plus commenters, "I really don't understand Jev hype," r/LocalLLaMA, post 2026-09-21 with comments through 2026-09-25, canonical local entry `../raw/i-really-dont-understand-jev-hype/index.md`, package scope `../raw/i-really-dont-understand-jev-hype/`, upstream `https://www.reddit.com/r/LocalLLaMA/comments/1wm65le/i_really_dont_understand_jev_hype/`. Locators in text: teacher/bootstrap remarks (`Refinery73` pb4pgq1/pb5ooiw, `DistanceAlert5706` pb59km1, `Asly97` pb6r7xg); maintenance tradeoff (`No_Veterinarian742` pbf3nvs, `Undreren` pb6zbtu/pb8urt2, `harrro` pb8aohi, `575_Inverse` pb8rncz); comparison caveat and field costs (`ideadude` pb5gkqy, `Smallpaul` pb76l40, `Sea-Requirement-5375` pb4m469, `c-linder` pb5llsi, `GasBond` pb4pxot); German-ads limit (`Geriny` pbbi77k).
[^reddit-jev-worth-hype-2026-09]: u/beasthunterr69 plus commenters, "Is Jev worth the hype?," r/singularity, post with comments 2026-09-26–2026-09-29, canonical local entry `../raw/is-jev-worth-the-hype/index.md`, package scope `../raw/is-jev-worth-the-hype/`, upstream `https://www.reddit.com/r/singularity/comments/1wqs5d9/is_jev_worth_the_hype/`. Locators in text: travel-app (`tribat` pc9738u) and code-review orchestration (`BuddyNathan` pc6mvro) uses; data-quality/risk and micro-decision remarks (`BuddyNathan` pc6mvro); customer-facing latency (`Dull_Wind6642` pcdzu5k) and corporate-pairing (`Raveyard2409` pcu5lxi) remarks; Twitch/trading uses (`Kanawanagasaki` pcgbvwo, `Wanderspor` pc6ivsz); Pi skill.md plus OpenRouter remark (`ih8csh` pcahxtp); 5x-Haiku and 12K/$1.83 cost remarks (`Existing_Scallion_66` pcuz4k9, `slackmaster2k` pcmsclc); Deem/shipwithjev/Laya pointers (`Pokenhagen` pc6q9uq, `-Akos-` pc6nl1r, `allisonmaybe` pc6qbx2).
[^reddit-jev-287-2026-09]: u/chenrongwei plus commenters, "I reviewed 287 open-source Jev projects," r/LLMDevs, post with comments 2026-09-19–2026-10-01, canonical local entry `../raw/i-reviewed-287-opensource-jev-projects-here-are/index.md`, package scope `../raw/i-reviewed-287-opensource-jev-projects-here-are/`, upstream `https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/`. Locators in text: decision-function framing and `big model → Jev → code → Jev → tool → Jev → big model` loop; 14→287 source-review claim; bounded-plus-verifiable (`jonah_omninode` pb6tzns) and downstream-acceptance remarks.
[^reddit-jev-marketing-2026-09]: u/tiensss plus commenters, "Jev isn't new tech. Its marketing targets people who think AI started with LLMs," r/LocalLLaMA, post 2026-09-23 with comments through 2026-10-01, canonical local entry `../raw/jev-isnt-new-tech-its-marketing-targets-people/index.md`, package scope `../raw/jev-isnt-new-tech-its-marketing-targets-people/`, upstream `https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/`. Locators in text: benchmark-selection and supervised-10k replies; accuracy-vs-labels and per-label-threshold remarks; BTZSC, Decision Index-mix, BART-MNLI, Qwen3-Reranker, Qwen3.5-0.8b, DeBERTa and SetFit pointers; constrained-output and Gliclass-AUC remarks.
[^jev-search-eval-2026]: 95pctAI, "Grading Technical Documents," web eval report, canonical local entry `../raw/jev-search-eval-report/index.md`, package scope `../raw/jev-search-eval-report/`, upstream `https://95pctai.github.io/jev-search-eval-report/`. Locators in text: Metrics (missed answers, noise, 25% limit); Systems tested; Results and Table 2; Speed and cost and Table 3; Screening pilot; Limitations.
[^reddit-jev-kev-2026-09]: u/facethef plus commenters, "Jev vs. Kev: open-source Jev alternative tested side by side," r/LocalLLaMA, post with comments 2026-09-25–2026-10-01, canonical local entry `../raw/jev-vs-kev-opensource-jev-alternative-tested-side/index.md`, package scope `../raw/jev-vs-kev-opensource-jev-alternative-tested-side/`, upstream `https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/`. Locators in text: post body (Kev-4B identity, 362-item fresh set, within-2-points finding, PAWS 87.0%/74.5%, +257-token overhead and 12x short-request cost); Opper routing and GitHub pointer; injection/router/tool-call uses (`Theio666` pc14ifr, `tribat` pc1rdep); LLM true/false question (`EnjoysFiction` pcyi6g9); Mica request (`Top-Evidence174` pc1nydf); llama.cpp fork (`shakshukinha` pc7bfiy).
[^kev-readme-2026]: Jared Palmer, "Kev," canonical local entry `../raw/kev.md`, upstream `https://github.com/jaredpalmer/kev`. Locators in text: Models and Kev 1.0 tables; Fine-Tune on Your Own Data; Deploy Your Own Endpoint; Serving Performance.
[^bespoke-nimble-2026-09]: Bespoke Labs, "Bespoke Nimble," canonical local entry `../raw/nimble.md`, repo `https://github.com/bespokelabsai/nimble`, model `https://huggingface.co/bespokelabs/Bespoke-Nimble-9B`. Locators in text: Capabilities and limits; Methodology (contrastive curation, dataset tables, finetuning, 324-example eval, latency); Quickstart and Updates.
[^openjev-2026]: OpenJev project, "OpenJev," model and serving bundle, canonical local entry `../raw/openjev-openjev/README.md`, package scope `../raw/openjev-openjev/`. Locators: "Results" 10,000-question, agent, MiniWoB, language and "Speed" tables; "Formats" deltas; `serve/SERVE.md` pinned recipe and `SHIM_TOKEN` boundary.
[^openjev-sglang-2026]: openjev-sglang project, "openjev-sglang," canonical local entry `../raw/openjev-sglang.md`. Locators: Qwen3.6-35B-A3B on SGLang 0.5.19 plus Modal B200 recipe; "How inference works" N+1 readout; "Limits and configuration" defaults and env table; top NOTE native-endpoint recommendation.
[^von-2026]: Von project, "Von," canonical local entry `../raw/von.md`, upstream `https://huggingface.co/wfzyx/von`. Locators in text: Benchmarks table; Acting on confidence gate figures; Chain-of-options; CLI calibrate row.
[^imajev-4b-2026-09-28]: mohit67890, "imajev-4b," model card, canonical local entry `../raw/imajev-4b.md`, upstream `https://huggingface.co/mohit67890/imajev-4b`. Locators in text: header tier/board links plus sub-caption; "Automate what is clear" threshold table; "Results (2026-09-26)" table.
[^quyet-1-0-large-2026]: Chinh Nguyen, "Quyet-1.0-Large," model card, canonical local entry `../raw/Quyet-1.0-Large.md`, upstream `https://huggingface.co/chinhnc/Quyet-1.0-Large`. Locators in text: family plus spec table (Architecture, Parameters, Languages, Input, Weights); "How to use" serving and prompt-version-2 paragraphs.
[^reddit-pi-jev-2026-09-30]: u/Apprehensive_Bed7502 plus commenters, "Pi now supports Jev.," r/PiCodingAgent, post with comments 2026-09-30–2026-10-01, canonical local entry `../raw/pi-now-supports-jev/index.md`, package scope `../raw/pi-now-supports-jev/`, upstream `https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/`. Locators in text: Pi 0.99.0 classifier claim plus docs/llama.cpp references (post body); premature-abstraction and extension-first remarks (`Ok-Hippo9182` pczbbf5); maintainer alternatives-plus-Decision-API reply (`badlogicgames` pd9uh5p); OMP `find` semantic-grep remarks (`Electronic-Pie-1879` pczik4h, `Suspicious_Echidna53` pczkmew); code-review diffs remark (`gscjj` pczhtl9); skill auto-load remark (`debackerl` pd58li2); pre-LLM navigation remarks (`ArthurOnCode` pczi260/pd2ubm2/pd6ikum); direct-tool benchmark plus embed-in-tools rebuttal (`Mechanical_Monk` pd02hlz/pd0edw2, `BurnerDev` pd0ax8h); local-maturity remarks (`Zestyclose839` pd0aw2c/pd25g96, `addiktion` pd0oym3, `debackerl` pd58tmx); core-vs-extension and acquisition/payment remarks (`gscjj` pczhtl9, `Apprehensive_Bed7502` pczk4ln/pd21m44/pczcxrb, `blakeman8192` pd4zpgz, `neuronexmachina` pd1sh25/pd3swyq, `_reg1z` pdaz4ie).
