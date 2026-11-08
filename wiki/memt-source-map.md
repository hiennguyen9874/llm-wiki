---
type: SourceMap
title: MemT-1.0 source map and coverage limits
description: Package identity, inspected material, pending research-paper attachments, and reproducibility limits for the MemT-1.0 source snapshot.
tags: [agent-memory, source-map, native-memory]
status: draft
created: 2026-11-08
generated: { by: llm-wiki-agent/1, at: '2026-11-08T02:52:52Z' }
sources:
  - id: memt-paper
    resource: ../raw/arXiv-2610.26825v2-MemT-1.0/paper.tex
    scope: ../raw/arXiv-2610.26825v2-MemT-1.0/
    kind: paper
    revision: arXiv-2610.26825v2
    title: 'MemT-1.0: Towards Memory-Native Evolution'
---

This is a **partial, draft** compilation of the MemTensor Team's local arXiv-v2 LaTeX package and its two model cards, not a complete research-paper review. `paper.tex` is the package entry point identified in `00README.json`; the local snapshot carries no independently verified upstream checksum. The cards identify Nano weights as Apache-2.0 and Flash weights as MIT, with separate backbone and third-party terms; the paper package's own license was not established.[^memt-paper]

## Coverage ledger

- **Inspected:** `00README.json`, `paper.tex`; both `MemT-1.0-Nano.md` and `MemT-1.0-Flash.md`; `sections/model_architecture.tex`, `sections/evaluation.tex`, `sections/application.tex`, `sections/scaling.tex`, `sections/infra.tex`, `sections/discussion.tex`; `sections/training.tex` lines 1–100; `appendix/adaptation_backbone.tex` lines 1–95; `appendix/infra_experiment_details.tex` lines 1–100; `tables/memory_major_result.tex` lines 1–100. Inspected source text is the authors' report, not an independent verification.[^memt-paper]
- **Pending text:** `sections/introduction.tex`, `sections/conclusion.tex`, remainder of `sections/training.tex`; `appendix/author_list.tex`, `appendix/case_studies.tex`, `appendix/detail_of_application.tex`, `appendix/evaluation_details.tex`, `appendix/stable_gdn.tex`, remaining portions of the two sampled appendices; remainder of `tables/memory_major_result.tex`, `tables/ablation_study.tex`, `tables/application_result.tex`, `tables/general_major_result.tex`; `reference.bib` where needed for attribution. Further extraction may change or qualify the compiled findings.[^memt-paper]
- **Pending visual review:** `figures/application.pdf`; `figures/application/fig_swe_v1_v2_combined.pdf`, `metis_ce_training_logs.png`, `metis_kd_training_logs.png`, `training_data_construction.pdf`; `figures/eval_efficiency.pdf`, `eval_low_rank.pdf`, `eval_storage.pdf`, `figure_efficiency.pdf`, `figure_moe.pdf`, `figure_performance.pdf`, `memory_capacity.pdf`, `memt-arc.pdf`, `memt-mos.pdf`, `scaling_data.pdf`, `stable_gdn2_erase_geometry.pdf`. Text surrounding some figures summarizes conclusions, but their complete axes and diagram details have not been checked.
- **Excluded:** `logo/github_logo.png`, `logo/huggingface_logo.png`, `logo/memory.png`, `logo/MemT_logo.png` as branding; `memtensor.cls` as typesetting, not substantive evidence.
- **Unavailable:** both model cards reference an absent local `assets/` directory. External repository, weights, code, benchmarks and dependencies were not fetched or executed; model-card examples and paper measurements were not reproduced.

## Navigation

[Architecture](memt-native-memory-architecture.md) · [Training and scaling](memt-training-and-scaling.md) · [Evaluation](memt-evaluation-and-efficiency.md) · [Coding application](memt-experience-guided-coding.md) · [Model cards and API](memt-models-and-session-api.md).

[^memt-paper]: `00README.json` key `sources`; `paper.tex` title, abstract and `\\input`/`\\bibliography` closure; model cards §§ License and Quick Start; package inventory and the listed files and sections.
