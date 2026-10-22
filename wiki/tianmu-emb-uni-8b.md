---
type: Concept
title: Tianmu-Emb-Uni-8B
description: An 8B-scale unified multimodal embedding model combining a Qwen3-VL embedding backbone with a Qwen2.5-Omni audio tower, producing 3,584-dimensional vectors and reporting 53.27 across 190 MMEB-V3 tasks.
tags: [embedding, retrieval, multimodal, multilingual, audio, qwen, mmeb]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-10-22T23:59:55Z }
sources:
  - id: tianmu-emb-uni-8b-card
    resource: ../raw/Tianmu-Emb-Uni-8B.md
    title: Tianmu-Emb-Uni-8B model card
  - id: mmeb-v3-ranking
    resource: ../raw/mmeb_v3_ranking.csv
    title: MMEB v3 ranking CSV
  - id: tianmu-hub-tree
    resource: ../raw/TianmuLab-Tianmu-Emb-Uni-tree-main.md
    kind: web-capture
    title: TianmuLab/Tianmu-Emb-Uni Hugging Face file tree (main, HTML capture)
  - id: tianmu-hub-page
    resource: ../raw/TianmuLab-Tianmu-Emb-Uni.md
    kind: web-capture
    title: TianmuLab/Tianmu-Emb-Uni Hugging Face model page (HTML capture)
---

# Tianmu-Emb-Uni-8B

Tianmu-Emb-Uni-8B is a unified embedding model for text, images, video, visual documents, audio, and agent tasks. It aligns an audio branch initialized from Qwen2.5-Omni-7B with a Qwen3-VL-Embedding-8B representation space. The release is not a standalone full 8B checkpoint: it supplies trained audio-side, connector, projection, adapter, and prototype modules while requiring the two base models separately.[^tianmu-emb-uni-8b-card]

## Model size and architecture

- **Declared scale:** The card expands “8B” as the model scale and names Qwen3-VL-Embedding-8B as the vision-language backbone. It does not report an exact total parameter count for the assembled system, which also uses a Qwen2.5-Omni-7B audio tower.[^tianmu-emb-uni-8b-card]
- **Architecture:** A Qwen3-VL embedding backbone provides the shared embedding space. An audio branch initialized from the Qwen2.5-Omni audio tower connects to that space through trainable connector, projection, adapter, and prototype modules.[^tianmu-emb-uni-8b-card]
- **Output:** 3,584-dimensional embeddings.[^tianmu-emb-uni-8b-card]
- **Released checkpoint:** `stage1b_adapter_proto_retrieval`. The package includes the trained audio-side and alignment modules, not the full Qwen3-VL-Embedding-8B or Qwen2.5-Omni-7B weights, and does not support native `AutoModel.from_pretrained` loading.[^tianmu-emb-uni-8b-card]

## Hugging Face repository contents

The captured `TianmuLab/Tianmu-Emb-Uni` file tree (revision `main`, head commit `89b33e5`, "Update README.md", 2026-08-24) shows what is hosted. Hub metadata is **Reported** by the Hub page; the arithmetic cross-checks are **Synthesis**.[^tianmu-hub-tree]

| Item | Observed in capture |
|---|---|
| Publisher / license | `TianmuLab` (Tianmu Lab org); Apache-2.0 with a `LICENSE` file; `base_model`: Qwen3-VL-Embedding-8B, Qwen2.5-Omni-7B |
| Config | `model_type` `tianmu_emb_uni_adapter_prototype`, architecture `OmniEmbedModel`; `library_name` transformers |
| Directories | `Prototype-adapter`, `base_models`, `eval`, `examples`, `processors`, `tianmu_model`, `weights` (contents not shown in the capture) |
| Top-level files | `README.md`, `FILES.md`, `LICENSE`, `config.json`, `requirements.txt`, `.gitattributes`, `model.safetensors.index.json`, `tianmu_audio_core.safetensors.index.json` |
| Weights | 4 sharded `model-0000X-of-00004.safetensors` (≈16.29 GB total) plus `tianmu_audio_core.safetensors` (≈3.28 GB) |
| Hub parameter count | 8,964,318,448 total: 8,144,793,840 BF16 + 819,524,608 F32; 19.57 GB total file size |
| Activity | Created 2026-08-05; last modified 2026-08-24; 57 commits (single listed contributor); 35 downloads last month, 1,229 all-time; 2 likes; not gated |

Size cross-check (Synthesis): the four shards sum to ≈16.29 GB, equal to 8.145 B BF16 parameters × 2 bytes, and the audio-core file equals 0.8195 B F32 parameters × 4 bytes. The Hub total of **8.96 B** parameters therefore counts both file groups, so the "8B" in the name appears to refer to the vision-language backbone scale rather than the whole hosted tensor set.[^tianmu-hub-tree]

Security scans at capture: antivirus "safe" on small text files; ProtectAI/JFrog "safe" on the shards; pickle-import and VirusTotal scans "unscanned".[^tianmu-hub-tree]

Limits: the capture lists only the top level, so the contents of `base_models/`, `weights/`, `Prototype-adapter/`, and `tianmu_model/` and the tensor names in the index files are not established. The README text, `FILES.md`, and eval scripts were not part of this capture.[^tianmu-hub-tree]

## Intended use and limitations

The card positions the release for **research and evaluation** of unified multimodal embeddings. Listed use cases: text-to-image, image-to-text, text-to-video, and audio-to-text retrieval; audio classification and audio retrieval; visual-document retrieval; multimodal RAG retrieval backbones; and cross-modal candidate recall. Stated limitations: base-model weights are not bundled; there is no integrated `AutoModel.from_pretrained` interface; performance may vary outside the MMEB-V3 distribution; and open-ended audio retrieval remains harder than audio classification in this checkpoint (consistent with the 38.94 audio score below). All are **Reported**.[^tianmu-hub-page]

## Loading procedure

The model page reproduces the card's loading recipe (**Reported**; not executed here). Prepare Qwen3-VL-Embedding-8B and Qwen2.5-Omni-7B separately, put the repository on `sys.path`, instantiate the project class `tianmu_model.modeling.OmniEmbedModel` with `audio_encoder_type="omni"`, `audio_model_path`, `vl_model_name`, `freeze_vl=True`, and `freeze_audio_encoder=True`, then load `model.safetensors` with `load_file(...)` and `model.load_state_dict(state_dict, strict=False)`. The `strict=False` call implies the checkpoint need not cover every module of the assembled model (**Synthesis**). `examples/load_weights.py` is the shipped minimal example; it was not inspected.[^tianmu-hub-page]

The card's file list names `model.safetensors`, `model.safetensors.index.json`, `config.json`, `weights/final_audio_weights.pt`, `tianmu_model/`, `processors/`, `eval/mmeb_v3_eval/`, `requirements.txt`, and `examples/load_weights.py`. It states that `model.safetensors` is converted from `weights/final_audio_weights.pt` and holds the same final state dict in safetensors format, with the `.pt` kept for the original training/evaluation scripts. The evaluation command is `bash code/scripts/run_omni_stage1b_adapter_proto_retrieval.sh`.[^tianmu-hub-page]

Hub-page rendering (**Reported**): the page shows "Model size 9B params" with BF16 and F32 tensors, and its model tree lists Qwen2.5-Omni-7B as base with this model as one of 80 finetunes. Only Qwen2.5-Omni-7B carries a `base_model:finetune:` tag; Qwen3-VL-Embedding-8B appears in `cardData.base_model` but not as a tagged finetune parent.[^tianmu-hub-page]

Licensing and third-party terms: the Tianmu adapter/audio-side code and weights are Apache-2.0 "unless otherwise specified"; Qwen3-VL-Embedding, Qwen2.5-Omni, and libraries (PyTorch, Transformers, safetensors, NumPy, librosa, soundfile, Pillow) remain under their own licenses, so effective terms depend on the base models.[^tianmu-hub-page]

## Language support

The model-card metadata declares Chinese and English. It does not enumerate broader language coverage, explain whether support differs by modality, or report language-specific benchmark results. Multilingual capability beyond Chinese and English is therefore not established by this source.[^tianmu-emb-uni-8b-card]

## Training data

The card does not identify training datasets, sample counts, language or modality distributions, filtering, objectives, or training schedule. It identifies the released checkpoint as a stage-1b adapter/prototype retrieval checkpoint and lists which modules are trained, but that is not enough to characterize its training data.[^tianmu-emb-uni-8b-card]

## Reported benchmarks

The model card reports evaluation on a 190-task MMEB-V3 setting: 37 image tasks including MCMR, 18 video, 24 visual-document, 11 audio, 53 text, and 47 agent tasks. Metrics differ by group, so the reported all-task aggregate combines mixed primary metrics. These are author-reported results without an independent reproduction in the local source.[^tianmu-emb-uni-8b-card]

| Modality | Tasks | Primary metric | Score |
|---|---:|---|---:|
| Image | 37 | hit@1 | 73.83 |
| Video | 18 | hit@1 | 59.37 |
| Visual document | 24 | ndcg_linear@5 | 72.03 |
| Audio | 11 | hit@1 | 38.94 |
| Text | 53 | ndcg_linear@5 | 43.62 |
| Agent | 47 | hit@1 | 39.42 |
| **All** | **190** | mixed primary metrics | **53.27** |

The card identifies the evaluated checkpoint and evaluation script but gives no comparator table, confidence intervals, or per-task results. It therefore supports reporting these scores, not a benchmark-leadership claim.[^tianmu-emb-uni-8b-card]

## Contradictions

- The model card reports an all-task MMEB-V3 score of **53.27** over 190 tasks.[^tianmu-emb-uni-8b-card] The separate [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md) reports Tianmu-Emb-Uni at **52.83 Overall** and **40.50 Overall-V3**, with matching Audio (**38.94**) and Agent (**39.42**) but a different Text value (**41.77** rather than **43.62**).[^mmeb-v3-ranking] The ranking artifact does not define its metrics or task composition, so the discrepancy cannot be resolved from the persisted evidence.
- The model card says the release does **not** include full base-model weights and does **not** support native `AutoModel.from_pretrained` loading.[^tianmu-emb-uni-8b-card] The Hub tree capture instead lists ≈16.29 GB of top-level BF16 `model-0000X-of-00004.safetensors` shards (8.145 B parameters), reports `transformersInfo.auto_model = AutoModel` with `library_name: transformers`, and displays an `AutoModel.from_pretrained("TianmuLab/Tianmu-Emb-Uni")` snippet.[^tianmu-hub-tree] Hub metadata and snippets are plausibly auto-generated from `library_name`, and the shards' contents (a copy of the Qwen3-VL backbone versus trained modules only) are not visible without the index file, so neither claim is chosen. The later model-page capture repeats the card's "no full base weights / no native `AutoModel`" statements verbatim, yet shows the same `AutoModel.from_pretrained("TianmuLab/Tianmu-Emb-Uni", device_map="auto")` Hub snippet and a "9B params" size badge, and the card's own file list names a single `model.safetensors` where the tree shows four shards.[^tianmu-hub-page] Synthesis, unverified: the 8.14B BF16 parameter count is close to an 8B vision-language backbone, which would be consistent with the "final state dict" containing more than adapter modules (and with `strict=False` loading), but this cannot be confirmed without tensor names.

## Relationships

- **Uses:** [Qwen3-VL-Embedding-8B](qwen3-vl-embedding-8b.md) as its vision-language embedding backbone.
- **Recipe reused by:** [Sentio](sentio.md), which applies the frozen-embedder + frozen-audio-tower + trained-connector approach (with prototype loss) to WeMM-Embedding 9B, per its own card.
- **Recipe also reused by:** [Wianmu-3B](wianmu-3b.md), which applies it to WeMM-Embedding-2B, and [Wianmu-5B](wianmu-5b.md), which applies it to WeMM-Embedding-4B (Reported).
- **Hosted at:** `TianmuLab/Tianmu-Emb-Uni` on Hugging Face; see [Hugging Face repository contents](#hugging-face-repository-contents).
- **Evaluated in:** [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md), subject to the score discrepancy above.

[^tianmu-emb-uni-8b-card]: [Tianmu-Emb-Uni-8B model card](../raw/Tianmu-Emb-Uni-8B.md). Architecture, language, release, and benchmark claims are author-reported; its remote image was not needed to cover the requested fields.
[^tianmu-hub-tree]: [TianmuLab/Tianmu-Emb-Uni file tree capture](../raw/TianmuLab-Tianmu-Emb-Uni-tree-main.md). Locators: embedded `ModelHeader` props (`model.safetensors`, `cardData`, `config`, `transformersInfo`, `downloads`, `createdAt`, `lastModified`), `ViewerHeader` (`numCommits`), `LastCommit`, and `ViewerIndexTreeList` entries (`path`, `size`, `securityFileStatus`). Unauthenticated HTML capture; no files were downloaded or executed.
[^tianmu-hub-page]: [TianmuLab/Tianmu-Emb-Uni model page capture](../raw/TianmuLab-Tianmu-Emb-Uni.md). Locators: rendered README sections “Intended Use”, “Files”, “Loading”, “Limitations”, “Third-Party Components”, “License”; `ModelHeader`/`ModelTensorsParams` props (`safetensors`, `transformersInfo`, `cardData`); “Model tree” panel. The README text duplicates [the model card](../raw/Tianmu-Emb-Uni-8B.md); the capture adds Hub metadata only. Unauthenticated HTML; scripts, navigation, and the `UnsafeBanner` UI prop (no scan result) were excluded; no files were downloaded or executed.
[^mmeb-v3-ranking]: [MMEB v3 ranking CSV](../raw/mmeb_v3_ranking.csv). This unauthenticated snapshot does not define its metric semantics or evaluation configuration.
