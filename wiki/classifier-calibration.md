---
type: Concept
title: 'Classifier Calibration: Temperature Scaling and Calibration Rewards'
description: How calibration aligns predicted probabilities with observed frequencies via temperature scaling and RL-style calibration rewards such as RLCR and Jev RLCD.
tags: [calibration, evaluation, reinforcement-learning]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-07T00:00:00Z }
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
  - id: imajev-4b-2026-09-28
    resource: ../raw/imajev-4b.md
    kind: model-card
    title: mohit67890/imajev-4b
---

# Classifier Calibration: Temperature Scaling and Calibration Rewards

Synthesis: calibration makes stated probabilities match empirical frequencies; temperature scaling fixes this post-hoc without changing predicted classes, while RL with calibration rewards adds a Brier penalty so models learn both correctness and honest confidence (§5.1–§5.3)[^raschka-jevl-2026-09-29].

## What calibration means

- Definition: adjust probability estimates to match observed class frequencies; among many reviews assigned ~74% positive, about 74% should be positive (§5.1, Fig. 34)[^raschka-jevl-2026-09-29].
- Why it matters: 74% vs 54% positive give the same 50%-threshold label but very different confidence; uncalibrated values mislead production thresholds and Jev-style confidence fields (§5.1)[^raschka-jevl-2026-09-29].
- Recommended practice: calibrate on held-out validation data and consult scikit-learn calibration docs for method choice (§5.1)[^raschka-jevl-2026-09-29].

## Temperature scaling

- Procedure used in author’s AI-detector project: freeze model weights, learn scalar temperature `T` by minimizing cross-entropy on calibration set, then divide logits by `T` before softmax (§5.1)[^raschka-jevl-2026-09-29].
- Effect: `T > 1` lowers top-class confidence, `0 < T < 1` raises it; ordering is preserved so argmax class is unchanged (§5.1)[^raschka-jevl-2026-09-29].
- Distillation example: [JEV-27B System 1 Decisions and Blocks-of-Experts Serving](jev-27b-system1-decisions.md) **reports** distilling full teacher distributions with KL (+ RPS for `score`) gives fitted per-kind temperatures 1.014 / 1.016 / 1.004 and ECE 0.0009 with no post-hoc correction — calibration falling out of the objective rather than a separate fix[^jev-27b-2026-10-01]. The 9B first generation **reports** the same effect at smaller scale — per-kind temperatures 1.002 / 0.984 / 1.012 and ECE 0.0007[^jev-9b-v08].
- Independent multimodal point: [Jev-Omni](jev-omni-multimodal-decisions.md) **reports** Medium ECE 0.0400 (10 bins; plot uses five bins for readability) on DecisionBench Medium; **synthesis**: do not rank this against the JEV 0.0007–0.0009 figures without protocol alignment, since datasets, binning and temperature handling differ[^jev-omni-2026].
- Independent grouped-temperature point: [Jev-Style-0.8B Decision v3 GGUF](jev-style-0.8b-decision-v3-gguf.md) ships global `T=0.88` plus 20 family × type × option-bucket temperatures fitted on 15,655 calibration-pool rows, **reported** NLL 0.3775→0.3667 and ECE 0.0329→0.0114 with shrinkage `k=100` and clamp `[0.3, 5.0]`; default no-category use is global `T`[^jev-style-v3-gguf-2026].
- Independent folded-temperature point: [Jev-Style-2B Decision v1 GGUF](jev-style-2b-decision-v1-gguf.md) fits one temperature on 4,366 held-out examples and folds it into the final RMSNorm weight, so logits arrive calibrated with nothing to apply at inference; **reported** 5-task ECE 0.065→0.017, NLL 0.786→0.418, Brier 0.446→0.242[^jev-style-2b-v1-gguf-2026].
- Independent per-workload point: [SemIf Open Decisions](semif-open-decisions.md) fits one temperature per workload on labeled decisions without changing the selected option; **reported** authored ECE 0.068→0.038 out of fold (T=1.23), WANLI 0.208→0.069 (T=2.50), Every judgments 0.050→0.047 (T=1.71) with the clear gain on WANLI and overlapping intervals elsewhere[^semif-2026-09-22].
- Independent shipped-temperature point: [Kev Decision Models](kev-decision-models.md) ships fitted temperatures 2.35/2.41/2.19/1.32 for 0.8B/4B/9B/27B applied on load without changing the winner; **reported** 9B ECE 0.103→0.041 on new sources with confident errors (≥0.9 wrong) 8.2%→2.4% below Jev 3.7%, and fine-tune refits temperature on a held-out slice — **synthesis**: do not rank these single-temperature ECE gains against per-kind or grouped-temperature schemes without protocol alignment[^kev-readme-2026].
- Independent fitted-temperature point: [Bespoke Nimble](bespoke-nimble-decision-model.md) fits T=2.179 on the original release without changing winners; **reported** second-set (300) ECE 0.128→0.066, log loss 0.692→0.555, Brier 0.348→0.295 with holdout (324) ECE 0.052→0.054, log loss 0.318→0.259, Brier 0.154→0.144, plus a rating-only ECE regression 0.105→0.177 on 64 questions — **synthesis**: do not rank this single-temperature gain against per-kind or grouped schemes without protocol alignment, and the latest checkpoint reverts to uncalibrated T=1.0[^bespoke-nimble-2026-09].
- Independent fixed-temperature point: [OpenJev](openjev-decision-model.md) pins `READOUT_T=0.85` for choice/score plus noul `T=1.829074/BIAS=0` with `READOUT_TARGETED=1` and `pyrepr` instruction style as one fitted set; **observed** in `serve/SERVE.md` plus static `helper/shim.py` read that file defaults differ (`T=1.1`, noul `3.0/-0.4`, targeted off, JSON style), so the four must stay together — **synthesis**: do not rank this pinned recipe against fitted-per-workload ECE figures without protocol alignment[^openjev-2026].
- Independent local-refit plus measured-gate point: [Von](von-decision-model.md) refits its confidence map with frozen weights via `von calibrate labels.jsonl` (scalar vs feature map by k-fold CV, NLL/ECE for raw/shipped/scalar/map; temperature never changes the answer); **reported** Choice ≥0.80 keeps 25% at 92.4% (90% lower bound 89.4%, n=702), Noul gated on `noul_raw` keeps 16% at 83%, lowest 90%-accurate cutoff 0.82, and out-of-domain gates go flat so only labels plus refit help — **synthesis**: use it as the only here-measured 0.80-gate precedent, not a transferable threshold[^von-2026].
- Uncalibrated contrast: [Julia 1](julia-1-decision-model.md) **reports** `calibration: null` in `inference-policy.json`, so its probabilities arrive without a fitted temperature; **observed** `julia/model.py` registers a per-type temperature buffer that the inspected forward pass does not apply, and `julia/probabilities.py` collapses decisive legacy distributions to 1.0/0.0 and floors sub-0.01 values before renormalizing — treat that display rule as presentation, not calibration[^julia-1-2026-09-24].
- Uncalibrated contrast: [NeoHorse-Jev-4B](neohorse-jev-4b-decision-model.md) **reports** no NLL, Brier, or ECE results and documents `confidence` as a local distribution statistic rather than a calibrated P(correct); **synthesis**: set thresholds on independent data and do not rank its Choice/Score `confidence` against fitted-temperature ECE figures such as JEV-9B/27B, Jev-Style, or Jev-Omni without protocol alignment[^neohorse-jev-4b-2026-09-24].
- Independent single-temperature point: [Imajev-4B](imajev-4b-decision-model.md) ships one temperature 1.305 for every type × option-count bucket fitted on 150 template-generated JevBench-style items; **reported** JevBench hard single-pass ECE 0.113→0.082 and pooled 231-item ECE 0.064→0.046 with `unknown` offsets 0, and warns the same temperature over-softens photo-only verification (previous-version 0.038→0.062) so photo-against-record traffic should serve without calibration or fit its own temperature[^imajev-4b-2026-09-28].

## Field calibration corroboration

- Legal-task confidence check is **reported**: on a 28-category legal task where Jev reached ~70% against Opus 5 Low ~95%, the reporter calls Jev confidence estimates "dead on accurate" and uses an 80%+ keep threshold with Opus escalation for the rest[^reddit-jev-hype-2026-09].
- Chess confidence check is **reported**: 400+ moves bucketed by claimed confidence versus one-ply material-loss outcomes is described as mostly holding, supporting narrow-domain threshold use[^reddit-jev-hype-2026-09].
- LLM-confidence contrast is **reported**: cheap-LLM confidence is characterized as hallucinated because the model "can't look inside themselves for an actual number," versus Jev's distribution-derived scores — treat as a commenter mental model, not a measured comparison[^reddit-jev-hype-2026-09].
- Threshold-guess warning is **reported** across a 287-project survey discussion: nearly every project gates on confidence (route above 0.8, escalate below), which asserts ~80%-correct among 0.8 calls, yet no reliability diagram has been published — so every threshold in the corpus is currently a guess wearing a number[^reddit-jev-287-2026-09].
- Afternoon calibration check is **reported**: bucket a few hundred decisions with known outcomes by reported confidence and plot per-bucket accuracy against the diagonal, watching for mid-range overconfidence where most production traffic sits[^reddit-jev-287-2026-09].
- Silent-failure logging rule is **reported**: when the decision model routes wrong the large model never sees the case, so log every decision with confidence plus eventual outcome and sample both sides of the threshold; measure downstream acceptance without repair including fallback/retry costs rather than decision accuracy alone[^reddit-jev-287-2026-09].
- Mid-range variance is **reported** in a 2026-09-26–29 r/singularity thread: one account finds repeated runs differ in confidence/probability with noticeable answer flips except on near-certain facts, and a 1,000-document reviewer **reports** variance concentrated in the 40–60% probability range — treat mid-range thresholds as the least trustworthy band until a per-workload reliability check exists[^reddit-jev-worth-hype-2026-09].
- Probabilities-are-not-calibration warning is **reported** in a 2026-09-23–10-01 marketing-critique thread: a spam-detection account found systematically high spam probabilities even on clearly non-spam messages, and the thread holds a nice probability output that is systematically biased is just confidently wrong — set per-label thresholds on labeled data rather than trusting raw zero-shot probabilities[^reddit-jev-marketing-2026-09].
- Threshold-guess corroboration from the same thread is **reported**: below ~20–50 labels per class zero-shot is fine, but a linear head usually catches up beyond that, so treat every unplotted threshold as a guess until a per-workload reliability check exists[^reddit-jev-marketing-2026-09].
- Opper calibration gap is **reported** in a 2026-09-25 r/LocalLLaMA side-by-side: Jev is better calibrated than Kev-4B on a fresh 362-item set and pulls ahead on paraphrase detection (PAWS 87.0% vs 74.5%) while overall accuracy stays within 2 points — **synthesis**: do not use the near-parity accuracy to assume interchangeable thresholds; verify PAWS-like and per-workload reliability separately[^reddit-jev-kev-2026-09].

## Why cross-entropy alone is not enough in practice

- Theory: cross-entropy (and Brier) optimum recovers true probabilities — e.g. 80/20 biased coin — so no extra penalty is needed at the ideal optimum, per Gneiting and Raftery 2007 (§5.3)[^raschka-jevl-2026-09-29].
- Practice: finite-data training can overfit negative log-likelihood without overfitting 0/1 loss (Guo et al. 2017); after most training examples are correct, minimizing cross-entropy further mainly increases confidence, which generalizes poorly, so test accuracy can rise while test cross-entropy worsens (§5.3)[^raschka-jevl-2026-09-29].
- Implication: whether added Brier loss helps must be checked on held-out data; author’s CE-plus-Brier ModernBERT test gave only small average gain and should not be assumed universal (§5.2–§5.3, Fig. 37)[^raschka-jevl-2026-09-29].

## RLCR and hypothesized RLCD

- Jev’s “Reinforcement Learning for Calibrated Decisions (RLCD)” is proprietary with no public algorithm; any link to RLCR below is author hypothesis, not established fact (§5)[^raschka-jevl-2026-09-29].
- RLVR baseline: reward 1 for correct, 0 for incorrect, ignoring formatting and length terms (§5.2)[^raschka-jevl-2026-09-29].
- RLCR (2025 “Beyond Binary Rewards”): model emits reasoning, answer, uncertainty analysis, and confidence `q`; reward `R = c − (q − c)²` where `c` is 1/0 correctness; squared term is the Brier penalty (§5.2, Fig. 35)[^raschka-jevl-2026-09-29].
- Worked rewards: incorrect at 0.9 confidence → −0.81; incorrect at 0.2 → −0.04; correct at 0.9 → 0.99 (§5.2)[^raschka-jevl-2026-09-29].
- Uncertainty analysis: same Qwen2.5-7B model writes missing evidence, ambiguous wording, questionable assumptions, or reasoning errors; `q` in tags is the estimated P(correct) (§5.2)[^raschka-jevl-2026-09-29].
- Reported results: HotpotQA expected calibration error 0.37→0.03 at similar accuracy (63.0%→62.1%); six-dataset average ECE 0.46→0.21 with accuracy 53.9%→56.2% (Table 1(a), Fig. 36); “RLVR + Classifier” baseline uses supervised correctness predictor (§5.2)[^raschka-jevl-2026-09-29].
- Jev adaptation hypothesis: apply calibration rewards directly to typed decisions with a classification head, training backbone plus head jointly, without emitting reasoning text; author’s ModernBERT CE-plus-Brier test is an inspired analogue with modest average benefit and one of nine datasets worsened on ECE (§5.2, Fig. 37)[^raschka-jevl-2026-09-29].
- RL motive: Brier term is more direct in RL (correctness-only rewards) than in supervised CE training where CE already pressures probabilities (§5.3)[^raschka-jevl-2026-09-29].

## Relationships

- Calibrates outputs of [Jev API Patterns](jev-api-patterns.md) and [Jev Decision Model](jev-decision-model.md).
- Applies after [Text Classification Lineage](text-classification-lineage.md) training.
- Informs [Classifier Selection](classifier-selection.md) when comparing calibrated confidence across vendors.
- Constrains [Jev Project Patterns](jev-project-patterns.md) thresholds until per-workload reliability is checked.

## Coverage limits

- Von calibration and gate figures above are **reported** README plus uninspected `benchmarks/sweep_threshold.py` and `results/threshold_sweep_*.json` values with no live refit reproduced here[^von-2026].
- RLCR numbers are **reported** paper results via the article, not re-verified; RLCD mechanics are unknown.
- Author's Brier-plus-CE finding is a single setup observation; do not generalize without held-out checks.
- Field checks above are single-thread Reddit anecdotes (2026-09-21) with no bucket tables or ECE values inspected; treat as threshold-use corroboration, not calibration measurement[^reddit-jev-hype-2026-09].
- 287-survey warnings above are single-thread Reddit anecdotes (2026-09-19–10-01) with no reliability plots or outcome logs inspected; treat the afternoon-check and log-both-sides rules as **reported** procedures, not reproduced measurements[^reddit-jev-287-2026-09].
- Marketing-critique thread above is single-thread Reddit anecdote (2026-09-23–10-01); spam-bias and labels-per-class figures are **reported** single-account values with no bucket table inspected[^reddit-jev-marketing-2026-09].
- Worth-the-hype variance above is single-thread r/singularity anecdote (2026-09-26–29) with no bucket table inspected; treat as variance corroboration, not calibration measurement[^reddit-jev-worth-hype-2026-09].
- Opper Jev-vs-Kev calibration gap above is a **reported** vendor summary with no reliability table or ECE inspected here; treat the PAWS 87.0%/74.5% split as task-specific, not a general calibration ranking[^reddit-jev-kev-2026-09].
- Kev temperature and ECE figures above are **reported** owner README values with calibration scripts and eval reports uninspected; treat refit and confident-error gains as unreproduced[^kev-readme-2026].
- Nimble temperature and ECE figures above are **reported** single-file README values with calibration sets and merged-weight behavior uninspected; treat the fitted-versus-latest and rating-regression figures as unreproduced[^bespoke-nimble-2026-09].
- OpenJev temperatures above are pinned-recipe values from **observed** `serve/SERVE.md` plus static helper read with no ECE table or live calibration check in this bundle; treat them as reproduction constants, not a ranked calibration result[^openjev-2026].
- Imajev temperature and ECE figures above are **reported** single-file model-card values with calibration files and eval harness uninspected; treat the 150-item fit and photo-traffic warning as unreproduced[^imajev-4b-2026-09-28].

[^raschka-jevl-2026-09-29]: S. Raschka, "Language Models for Text Classification: From Bag-of-Words to Jev," Ahead of AI, published 2026-09-29, canonical local entry `../raw/classifier-history-and-jev/index.md`, upstream `https://magazine.sebastianraschka.com/p/classifier-history-and-jev`. Locators in text: §5–§5.3, Figs. 34–37.
[^jev-27b-2026-10-01]: AutoTrust, "autotrust/JEV-27B," model card, canonical local entry `../raw/JEV-27B/README.md`, package scope `../raw/JEV-27B/`, release notes 2026-10-01, upstream `https://huggingface.co/autotrust/JEV-27B`. Locators: “Blocks of Experts recipe” efficiency point 5; `calibration.json` per_kind; “Evaluation details” ECE row.
[^jev-9b-v08]: AutoTrust, “autotrust/JEV-9B,” model card, canonical local entry `../raw/JEV-9B/README.md`, package scope `../raw/JEV-9B/`, released checkpoint v0.8.0, upstream `https://huggingface.co/autotrust/JEV-9B`. Locators: “Evaluation details” ECE row; `calibration.json` per_kind.
[^jev-omni-2026]: akhilaaa3, “Jev-Omni,” model card, canonical local entry `../raw/Jev-Omni/README.md`, package scope `../raw/Jev-Omni/`, upstream `https://huggingface.co/akhilaaa3/Jev-Omni`. Locators: “Calibration” ECE line and `assets/medium-calibration.svg`.
[^jev-style-v3-gguf-2026]: chaoliangUNSW, “Jev-Style-0.8B-Decision-v3-GGUF,” model package, canonical local entry `../raw/Jev-Style-0.8B-Decision-v3-GGUF/README.md`, package scope `../raw/Jev-Style-0.8B-Decision-v3-GGUF/`. Locators: `readout_config.json` temperatures, clamp, fit quality and family/bucket keys.
[^julia-1-2026-09-24]: Supersonic Labs, "Julia 1," model package, canonical local entry `../raw/Julia-1/README.md`, package scope `../raw/Julia-1/`, weights SHA-256 `df853bf7fe424420011f3d0c47a05d7341aa9eefa7fb9f203ea4aada4ad95b72`. Locators: `inference-policy.json` calibration field; `julia/model.py::JuliaDecisionModel` temperature buffer and forward; `julia/probabilities.py::display_probabilities`.
[^neohorse-jev-4b-2026-09-24]: TokenRhythm, "NeoHorse-Jev-4B," model package, canonical local entry `../raw/NeoHorse-Jev-4B/README.md`, package scope `../raw/NeoHorse-Jev-4B/`, bundle version `1.0.0`. Locators: "Limitations" calibration line; `DEPLOYMENT.md` §5 confidence formulas and headers plus `package/src/neohorse_decision/systemone.py::with_confidence`.
[^jev-style-2b-v1-gguf-2026]: chaoliangUNSW, "Jev-Style-Qwen3.5-2B-Decision-GGUF," model package, canonical local entry `../raw/Jev-Style-Qwen3.5-2B-Decision-GGUF/README.md`, package scope `../raw/Jev-Style-Qwen3.5-2B-Decision-GGUF/`.
[^semif-2026-09-22]: SemIf project, "SemIf (formerly OpenJev)," canonical local entry `../raw/SemIf-OpenJev.md`, repo `TheoLeeCJ/SemIf` via PR/star-history links, latest changes 2026-09-22. Locators: "Calibration" ECE/temperature table.
[^reddit-jev-hype-2026-09]: u/Manerfish plus commenters, "I really don't understand Jev hype," r/LocalLLaMA, post 2026-09-21 with comments through 2026-09-25, canonical local entry `../raw/i-really-dont-understand-jev-hype/index.md`, package scope `../raw/i-really-dont-understand-jev-hype/`, upstream `https://www.reddit.com/r/LocalLLaMA/comments/1wm65le/i_really_dont_understand_jev_hype/`. Locators in text: legal confidence (`Sea-Requirement-5375` pb4m469) with cheap-LLM-confidence replies (`PyrrhicArmistice` pb5c2wt, `scorchypoo` pb7r0z2); chess buckets (`LateDon` pb6ty8q).
[^reddit-jev-worth-hype-2026-09]: u/beasthunterr69 plus commenters, "Is Jev worth the hype?," r/singularity, post with comments 2026-09-26–2026-09-29, canonical local entry `../raw/is-jev-worth-the-hype/index.md`, package scope `../raw/is-jev-worth-the-hype/`, upstream `https://www.reddit.com/r/singularity/comments/1wqs5d9/is_jev_worth_the_hype/`. Locators in text: repeat-run differences and flips (`Aqwart` pckivg2) with setup counter-remark (`damhack` pckmgxe); 40–60% variance note (`Existing_Scallion_66` pcuziy3).
[^reddit-jev-287-2026-09]: u/chenrongwei plus commenters, "I reviewed 287 open-source Jev projects," r/LLMDevs, post with comments 2026-09-19–2026-10-01, canonical local entry `../raw/i-reviewed-287-opensource-jev-projects-here-are/index.md`, package scope `../raw/i-reviewed-287-opensource-jev-projects-here-are/`, upstream `https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/`. Locators in text: `nitish-kmr` pb3zi2m reliability-diagram/threshold-guess plus log-and-sample-both-sides remarks; `jonah_omninode` pb6tzns downstream-acceptance remark.
[^reddit-jev-marketing-2026-09]: u/tiensss plus commenters, "Jev isn't new tech. Its marketing targets people who think AI started with LLMs," r/LocalLLaMA, post 2026-09-23 with comments through 2026-10-01, canonical local entry `../raw/jev-isnt-new-tech-its-marketing-targets-people/index.md`, package scope `../raw/jev-isnt-new-tech-its-marketing-targets-people/`, upstream `https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/`. Locators in text: spam-bias remark; accuracy-vs-labels and per-label-threshold remarks.
[^reddit-jev-kev-2026-09]: u/facethef plus commenters, "Jev vs. Kev: open-source Jev alternative tested side by side," r/LocalLLaMA, post with comments 2026-09-25–2026-10-01, canonical local entry `../raw/jev-vs-kev-opensource-jev-alternative-tested-side/index.md`, package scope `../raw/jev-vs-kev-opensource-jev-alternative-tested-side/`, upstream `https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/`. Locators in text: post body (better-calibrated claim, PAWS 87.0%/74.5%, within-2-points parity).
[^kev-readme-2026]: Jared Palmer, "Kev," canonical local entry `../raw/kev.md`, upstream `https://github.com/jaredpalmer/kev`. Locators in text: Kev 1.0 table; Benchmarks Calibration; Fine-Tune on Your Own Data.
[^bespoke-nimble-2026-09]: Bespoke Labs, "Bespoke Nimble," canonical local entry `../raw/nimble.md`, repo `https://github.com/bespokelabsai/nimble`, model `https://huggingface.co/bespokelabs/Bespoke-Nimble-9B`. Locators in text: Probability temperature (fit method, second-set and holdout tables, rating regression, T=1.0 latest and v2 transferred default, merge gap).
[^openjev-2026]: OpenJev project, "OpenJev," model and serving bundle, canonical local entry `../raw/openjev-openjev/README.md`, package scope `../raw/openjev-openjev/`. Locators: `serve/SERVE.md` env-knob table (`READOUT_T`, `READOUT_NOUL_T/BIAS`, `READOUT_TARGETED`, `READOUT_INSTR_STYLE`); `helper/shim.py::TEMP/NOUL_T/TARGETED`.
[^von-2026]: Von project, "Von," canonical local entry `../raw/von.md`, upstream `https://huggingface.co/wfzyx/von`. Locators in text: Acting on confidence (sweep method, Choice/Noul keeps, cascade, out-of-domain limit); CLI `von calibrate` row.
[^imajev-4b-2026-09-28]: mohit67890, "imajev-4b," model card, canonical local entry `../raw/imajev-4b.md`, upstream `https://huggingface.co/mohit67890/imajev-4b`. Locators in text: "Calibration" temperature paragraph plus ECE table.
