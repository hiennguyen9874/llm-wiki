---
type: Concept
title: Symbol-equivariant recurrent reasoning models
description: SE-RRMs use a symbol axis and axial attention to guarantee equivariance for interchangeable symbols, reporting strong small-model Sudoku results and mixed extrapolation beyond training grid sizes.
tags: [arc-agi, equivariance, recurrent-reasoning, sudoku, transformers]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T13:09:29Z }
sources:
  - id: freinschlag2026serrm
    resource: ../raw/arXiv-2603.02193v1/main_icml2026.tex
    title: "Symbol-Equivariant Recurrent Reasoning Models"
---

# Symbol-equivariant recurrent reasoning models

Symbol-Equivariant Recurrent Reasoning Models (SE-RRMs) are recurrent Transformer-style neural solvers for structured symbolic tasks. They represent every position across a separate symbol axis and apply shared position- and symbol-axis attention, so permuting intended-interchangeable symbols permutes the prediction correspondingly. The source reports materially better 9×9 Sudoku results than its HRM/TRM baselines with 2M parameters, but only partial accuracy—not solved instances—on larger unseen Sudoku sizes; its results are an under-review manuscript's self-reported evaluations.[^freinschlag2026serrm]

## Architecture and symmetry boundary

- A vanilla recurrent reasoning model (RRM) holds a $D \times I$ state over $I$ positions and uses a symbol-specific embedding plus position-wise output projection. Because its embedding and output dimensions are tied to the known alphabet, the paper says it cannot directly accommodate an enlarged symbol set at inference.[^freinschlag2026serrm]
- SE-RRM instead represents embeddings and recurrent state as $D \times I \times K$, where $K$ is the symbol/color cardinality. An input's present ordinary symbol gets the same learned feature vector in its corresponding symbol slot; absent symbols get zero vectors. Each recurrent layer applies attention across positions, then attention across symbols, followed by token-wise MLP and RMS normalization; its output head maps features to one logit per position-symbol pair.[^freinschlag2026serrm]
- The source's symbol-equivariance proposition relies on uniform operations across the symbol axis and omitting task-type embeddings. It explicitly allows distinct embeddings for special tokens such as masks, and says learned task-type embeddings may depart from initially identical columns when symbol equivariance is inappropriate for an individual task. Thus the guarantee applies to the intended set of interchangeable symbols, not automatically to every label in every task.[^freinschlag2026serrm]
- With efficient attention, the stated SE-RRM complexity is $O(I^2K + K^2I)$ time and $O(IK)$ memory, versus $O(I^2)$ time and $O(I)$ memory for the position-only attention framing. It is therefore costlier by roughly $K$ when $I \gg K$ and may be impractical when $K \gg I$.[^freinschlag2026serrm]

## Reported evaluation

- The source trains all reported RRMs with deep supervision and uses 16 recurrent steps at evaluation; SE-RRM uses stochastic early termination of training-time supervision rather than the HRM/TRM Q-learning stopping policy. The paper's Sudoku SE-RRM has 2M parameters, compared with the listed 7M TRM and 27M HRM configurations.[^freinschlag2026serrm]
- Trained on 9×9 Sudoku, SE-RRM reportedly reached 93.73% fully solved rate (FSR) and 97.58% unfilled-cell accuracy, versus 71.94%/89.80% for TRM and 63.53%/86.11% for HRM. On 4×4 puzzles without fine-tuning, it reports 95.46% FSR; the listed HRM and TRM FSRs are zero.[^freinschlag2026serrm]
- Enlarging the grid also enlarges the alphabet. SE-RRM could run on 16×16 and 25×25 grids, where HRM and TRM could not accommodate new symbols, but it solved none of the evaluated puzzles: reported unfilled-cell accuracies were 51.95% and 31.49%, respectively. Architectural compatibility is therefore not evidence of reliable solution-level extrapolation.[^freinschlag2026serrm]
- On 9×9 Sudoku, source-reported SE-RRM FSR rose from 16.05% at one recurrent step to 93.73% at 16 and 98.84% at 128, exceeding the listed HRM/TRM values at each tested depth. This is a single task and model configuration, not a general inference-time scaling law.[^freinschlag2026serrm]
- With eight dihedral augmentations per ARC puzzle rather than the 1,000 color augmentations attributed to HRM/TRM, the source reports ARC-AGI pass@2 of 45.3% on ARC-AGI-1 and 7.1% on ARC-AGI-2, compared with listed TRM values of 44.6% and 7.8%. On Maze, where it intentionally assigns different symbol embeddings and breaks symbol equivariance, it reports 88.8% FSR versus 85.3% for TRM.[^freinschlag2026serrm]

## Trust boundary and limitations

The manuscript is cited in its bibliography as “Under Review”; no independent replication was inspected. Its HRM and TRM ARC/Maze reference values are taken from their respective publications, while its own results, baselines, datasets, and augmentation regimes are source-reported. The source evaluates compact task-specific neural solvers on Sudoku, ARC-AGI, and mazes; it does not establish that symbol equivariance transfers to general language reasoning, or that it replaces symbolic search/program synthesis on these tasks.[^freinschlag2026serrm]

## Relationships

- **Related to**: [Depth-recurrent transformers for compositional generalization](depth-recurrent-transformers-for-compositional-generalization.md) — both reuse a Transformer block to increase latent computation at fixed parameter count, but SE-RRM adds an explicit symbol dimension and uses intermediate deep supervision rather than that study's final-step-only objective.[^freinschlag2026serrm]
- **Related to**: [Recurrent-depth systematic generalization and extrapolation](recurrent-depth-systematic-generalization-and-extrapolation.md) — both report task-specific benefits from added inference recurrence, while SE-RRM tests representation-level symbol symmetry rather than synthetic fact composition.[^freinschlag2026serrm]

[^freinschlag2026serrm]: Freinschlag, Bertram, Kobler, Mayr, and Klambauer, *Symbol-Equivariant Recurrent Reasoning Models*, under-review manuscript, abstract, §§2–4, and appendix (2026; compiled from `raw/arXiv-2603.02193v1/main_icml2026.tex`; figures were visually inspected).