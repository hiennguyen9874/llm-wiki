---
type: Concept
title: Clinical decision network weight audit
description: A synthetic radiotherapy study reports weight-based flaw detection and sparse repairs, alongside testing and numerical-safety limits.
tags: [ml, interpretability, safety]
status: draft
created: 2026-11-09
generated: { by: llm-wiki-agent/1, at: 2026-11-09T08:24:31Z }
sources:
  - id: nusrat-clinical-audit
    resource: ../raw/arXiv-2611.05341v1/main.tex
    scope: ../raw/arXiv-2611.05341v1/
    kind: paper
    revision: arXiv-2611.05341v1
    title: "Weight-space programming for auditing clinical decision networks"
---

**Reported:** Nusrat and Nusrat's unreviewed 2026 preprint tests whether an LLM can diagnose and repair small synthetic radiotherapy decision networks from their weights and a protocol. It reports sparse repairs for planted confounds and a threshold shift, but unreliable clearance of healthy networks, missed triggers, and dangerous 16-bit failures. This is not a clinical validation or certification method.[^nusrat-clinical-audit]

## Task and evaluation

**Reported:** Two-layer ReLU networks use eight scaled dose, volume, and missing-structure inputs to decide whether to escalate a planning request. Four protocol rules cover a hot-spot cap, mandible overlap, a cord limit below its feasible floor, and a missing structure. Disagreements within 0.3 Gy or 0.3 cc of thresholds were excluded. The main networks have 433 parameters; size tests use 1,377 and 4,801. Synthetic training planted four kinds of rule confound, a 3 Gy cord-threshold shift, or a trigger; healthy controls had no planted flaw.[^nusrat-clinical-audit]

**Reported:** Claude Opus 5.5 received the protocol and rounded weights with tools disabled; audits used an undated model alias and uncontrolled sampling. The panel scoring rules were fixed before answers were read: a detection required a deviating verdict and verified claimed regions covering at least half the planted-region failures. Verification required at least 100 matching requests and either 80% deviation or 30% deviation at least 20 times the outside rate. Edits were successful when planted-region error fell to at most 5%. Test pools combined family, uniform and trigger-window requests; this is empirical sampling, not proof over the input domain.[^nusrat-clinical-audit]

## Findings and comparisons

- **Reported:** The auditor detected 16 of 18 flawed panel networks: all 12 confounds, all three shifts, and one of three triggers. The strict 80% claim criterion detected 14 of the 15 confounds and shifts. All 16 detected flaws had zero planted-region error after editing, with a median of three parameters changed; 14 edits caused no newly wrong decisions on the test pool, and the other two caused 2 and 18.[^nusrat-clinical-audit]
- **Reported:** Only two of five healthy networks were cleared without a forced verdict; one more was tentatively cleared when forced, one received a false alarm whose edit made 2,018 decisions wrong, and one received no verdict. A forced trigger-network edit left the trigger and made 1,181 correct decisions wrong. The pilot audits also missed an unplanted missing-structure flaw.[^nusrat-clinical-audit]
- **Reported:** Simple flaw-type-informed first-layer column norms identified all 20 confounded pilot, panel and larger networks; a unit switch-on statistic found the three shifted thresholds. The LLM was not told the flaw type, but its named mechanisms were not tested by unit ablation. The study was not preregistered, and some comparisons were selected after flaw types were known.[^nusrat-clinical-audit]
- **Reported:** Testing against the exact protocol separated all 21 panel networks in 0.4 seconds; LLM-guided black-box testing found each confound and shift tested, one network per condition, in 1.8–3.0 minutes. Trigger detection depended on dense window sampling. Fine-tuning on 200,000 protocol-labeled examples repaired all 18 flawed networks in five runs each, changing 432 or 433 parameters with the original schedule; it was given examples of the hidden family. Formal verification and verification-based repair were not compared.[^nusrat-clinical-audit]
- **Reported:** Every edit introducing weights of at least 10⁵ failed in 16-bit floating point. In most, overflow yielded undefined scores and sent all requests to automated planning, missing escalations. The paper recommends testing repairs in deployment arithmetic and recommissioning; a small edit count does not establish safety.[^nusrat-clinical-audit]

## Relationships

- This is a synthetic diagnostic and repair application of [weight-space programming](weight-space-programming.md), combining [weight reading](reading-neural-network-weights-with-llms.md) with [direct weight editing](llm-directed-neural-weight-editing.md).

## Evidence and coverage limits

The English preprint is dated 3 November 2026, version 1, and says it is not peer reviewed. Its authors report synthetic data, no specific funding or conflicts, and AI assistance in analysis code and manuscript preparation. No patient data or deployed clinical network was studied. The source gives an external repository for code, networks, answers and scripts, but these were not inspected or run. The local package's LaTeX entry point, manuscript, manifest, reading guide and three PNG figures were inspected; CSV table files and the edit CSV were inspected, while the larger figure-data CSVs were sampled only. PDF figures duplicate the local PNG figures and were not separately rendered; the bibliography is reproduced in the manuscript and the separate BibTeX file was not inspected. The local license is unspecified. Findings remain author-reported and no experiment was independently reproduced; draft status retains these coverage limits.[^nusrat-clinical-audit]

[^nusrat-clinical-audit]: Nusrat and Nusrat, `main.tex`, Methods §§2.1–2.5; Results §§3.1–3.8, Tables 1–3, Figures 1–3; Discussion, Ethics, Funding, Use of AI tools, Data availability, and Appendix A. The equivalent `anc/paper.md` and `anc/figures/` figures were also inspected.
