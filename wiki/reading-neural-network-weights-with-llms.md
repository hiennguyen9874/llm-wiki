---
type: Concept
title: Reading neural network weights with LLMs
description: Reported experiments using an LLM to infer learned behavior and circuits from weights, sometimes with restricted activation evidence.
tags: [ml, interpretability]
status: draft
created: 2026-11-09
generated: { by: llm-wiki-agent/1, at: 2026-11-09T08:26:00Z }
sources:
  - id: itecs-explainer
    resource: ../raw/weight-space-programming-explained/index.md
    scope: ../raw/weight-space-programming-explained/
    kind: article
    title: "Weight-Space Programming: How LLMs Edit Model Weights"
  - id: takehi2026
    resource: ../raw/weight-space-programming.md
    kind: article
    title: "Sparks of Weight-Space Programming: LLMs can natively read & write neural network weights"
  - id: mindstudio-reading
    resource: ../raw/gpt6-astra-weight-space-programming/index.md
    scope: ../raw/gpt6-astra-weight-space-programming/
    kind: article
    title: "GPT-6 Astra and Weight-Space Programming: Can AI Read a Model's Weights?"
  - id: qwen-local-reading
    resource: ../raw/qwen-can-interpret-model-weights.md
    kind: article
    title: "Qwen can interpret model weights"
  - id: critique2117416640132366570
    resource: ../raw/2117416640132366570.md
    kind: article
    title: "Critique of weight-space programming experiments"
---

**Reported:** In the article's weight-reading experiments, GPT-6 Astra inferred some small networks' tasks and attention-head properties using weight structure, but failed to identify a sycophantic language model from weights alone. The cases differ substantially in permitted tools and evidence, so they are not a single uniform test of interpretability.[^takehi2026]

## Experiments

- **Game policies:** Four same-shaped PPO policies for grid versions of Breakout, Pong, Pac-Man, and Freeway were identified correctly from text weights, given the grid and actions but not the game options. The authors attribute this to spatial first-layer and action-output patterns.[^takehi2026]
- **Diffusion models:** With text weights and no tools or forward passes, Astra named circle, square, and triangle generators. It drew outlines rather than the filled shapes actually generated, a meaningful limitation.[^takehi2026]
- **Character transformers:** Given only four middle blocks, Python analysis, and no forward passes, Astra correctly classified three models trained on Python, romaji, or English in two attempts each. The article reports that its named copying heads exactly matched heads measured using repeated random strings; the labels, prompts, and selection are specific to this test.[^takehi2026]
- **Sycophancy:** Weights alone did not distinguish the sycophant in four attempts. With attention patterns elicited by up to 16 self-authored texts, but without model outputs, Astra identified the sycophant in three separately trained model pairs. This is an activation-assisted result, not a weights-only success.[^takehi2026]

## Reported local weight-reading test

**Reported firsthand:** The author describes running Qwen 3.8 27B locally on four self-contained game-identification prompts: it named Pac-Man, Pong, and Breakout, but misidentified Freeway as a Pac-Man-like grid game. Reported elapsed times were 46m 12s for Pac-Man, 1h 4m 54s for Pong, and 52m 25s for Breakout; Pac-Man reportedly used 43,506 reasoning tokens. The author says the prompts differed only in weights. These are selected reported runs, not a measured general success rate.[^qwen-local-reading]

**Reported setup:** The author used a Qwen3.8-27B Q4_K_M GGUF (described as 17 GB), LM Studio, and the `llm-lmstudio` plugin. The default 8,192-token context produced errors; a longer context and `LMSTUDIO_TIMEOUT=900` were used. The prompt instructed the model not to use tools or a calculator. The linked prompts, model file, and transcripts were not inspected or run here.[^qwen-local-reading]

**Discrepancy:** The MindStudio secondary account attributes the same four-game outcome to Willison but describes Qwen 3 27B via Ollama and about 26 GB VRAM on a 48 GB GPU. The firsthand capture instead describes Qwen 3.8 27B through LM Studio on a laptop and does not give those GPU specifications. Whether the secondary account conflates runs or misreports the setup cannot be established from these captures.[^mindstudio-reading] [^qwen-local-reading]

**Reported critique:** The article attributes to Willison the concern that combining tool-free weight reading with Python-assisted analysis obscures what each setup establishes. The original experiments explicitly differ in allowed tools and evidence, as summarized above; the critique should not be read as showing every experiment used tools.[^mindstudio-reading] [^takehi2026]

## Critique and unresolved disagreement

**Reported critique:** The game's spatial input weights allegedly draw recognizable maps, making identification easier than a general interpretation task. The critic says a Frogger answer was counted as Freeway, disputing the authors' description of all four identifications as correct. A secondary explainer says the answer was “Frogger” and the scoring rule accepted it as Freeway in advance; the response and scoring logs were not inspected here, so the rule's timing is not independently established and whether this constitutes a correct identification depends on the scoring criterion.[^itecs-explainer][^critique2117416640132366570] [^takehi2026]

**Reported critique:** On sycophancy, the critic says three of four weights-only attempts were coin flips and that changing the implicated components did not change behavior. The original article reports four failures with weights alone and identifies the successful follow-up as based on attention patterns, not model outputs. The post's characterization as simply watching behavior and its intervention claim need underlying logs to assess.[^critique2117416640132366570] [^takehi2026]

## Relationships

- The [dataset-prior audit](weight-reading-dataset-prior-audit.md) reports a distinct tool-free CNN study that tests class-order and dataset-familiarity effects.
- The [clinical decision network weight audit](clinical-decision-network-weight-audit.md) reports detection and clearance limits on synthetic radiotherapy networks.

- These experiments test the reading side of [weight-space programming](weight-space-programming.md); [LLM-directed neural weight editing](llm-directed-neural-weight-editing.md) concerns intervention rather than identification.

## Evidence limits

All results above are reported by the blog authors, not reproduced here. External logs and datasets were not inspected, and the article's quantitative claims and model identities were not independently verified.[^takehi2026] The standalone critique has no stated author, date, methods, license, or linked test artifacts; its claimed testing was not independently verified. No attachments or executable instructions were identified.[^critique2117416640132366570]

The MindStudio English secondary article by Luis Chavez-Mattos, published 2026-11-04, was inspected along with its local image, a decorative promotional illustration excluded from the synthesis. The capture supplies no license or capture date. Promotional copy and speculative applications were excluded.[^mindstudio-reading]

The standalone English local test capture provides no explicit byline, publication date, original article URL, license, or model revision. Its external prompts, game repository, response and reasoning transcripts, model file, original paper, and linked critiques were not inspected for this ingest; there are no local attachments. The article's shell examples were inspected but not executed; no experiment was reproduced. A secondary article attributes the testing to Simon Willison, but its setup details conflict as noted above. Draft status retains these limitations.[^qwen-local-reading] [^mindstudio-reading]

The English ITECS AI explainer, by the ITECS Team and published 2026-11-04, reports checking the research post and logs but not reproducing the experiments. Its text and lead image were inspected; the image repeats its summary, and the SVG logo and inline illustrations are decorative or repeat text. External logs and other linked sources were not inspected for this ingest. The capture gives no license or local capture date.[^itecs-explainer]

[^itecs-explainer]: ITECS Team, “Experiment 1: Naming the game from 17,253 numbers” and “Sources And Trust Signals.”
[^qwen-local-reading]: Local article, “Weight-Space Programming” and “Trying it out with Qwen 3.8 27B and other models.”
[^mindstudio-reading]: Luis Chavez-Mattos, MindStudio, “TL;DR,” “How does a model read another model’s weights?”, and “Is weight-space programming reliable right now?”
[^critique2117416640132366570]: Local critique, paragraphs beginning “correctly named all four” and “Sycophancy.”
[^takehi2026]: Takehi et al., experiments 1–3 and 7, including the corresponding “Setup” lists and copying-head table.
