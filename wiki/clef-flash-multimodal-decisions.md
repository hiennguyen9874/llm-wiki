---
type: Concept
title: Clef-Flash Multimodal Joint-Schema Decisions
description: Cloudflare Clef-Flash 9B multimodal decision model on Qwen3.5-9B with joint-schema head, Jev-compatible APIs, reported Decision Index and workflow results, and observed loader mechanics.
tags: [clef, decision-models, multimodal, classification, system-one]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T23:30:00Z }
sources:
  - id: clef-flash-2026
    resource: ../raw/clef-flash/README.md
    scope: ../raw/clef-flash/
    kind: model-card
    title: Cloudflare/clef-flash
---

# Clef-Flash Multimodal Joint-Schema Decisions

Synthesis: Clef-Flash is Cloudflare's 9B multimodal decision model that scores every allowed option of every typed question in one forward pass over text, JSON, images, or video — with **observed** Qwen3.5-9B plus joint-schema-head mechanics and a Jev/SystemOne-compatible `systemone` path, and **reported** Decision Index 0.2.1 plus Typesafe-workflow results where it leads tool-use, simulator, and knowledge/reasoning rows but trails on intent-OOS, hallucination, and hard-reasoning rows[^clef-flash-2026].

## Identity and provenance

- Package `../raw/clef-flash/` with canonical entry `README.md`; Hugging Face `Cloudflare/clef-flash`, larger variant `Cloudflare/clef`; announcement on the Cloudflare blog and leaderboard at `clef-evals.workers-ai-mle.workers.dev`[^clef-flash-2026].
- Base **reported** as `Qwen/Qwen3.5-9B` post-train (finetune); frontmatter `base_model_relation: finetune`; license Apache-2.0 following the base model[^clef-flash-2026].
- Contract: `state` plus a schema of typed questions yields one logit per allowed option per question; apply per-question softmax for probabilities; no free-form generation and no output parsing; API fully compatible with Jev and SystemOne[^clef-flash-2026].

## Architecture — observed

- Backbone `config.json`: `Qwen3_5ForConditionalGeneration`, `model_type: qwen3_5`, `dtype: bfloat16`, `transformers_version: 5.10.2`; text tower hidden 4096, 32 layers, vocab 248320, 262144 positions, hybrid `linear_attention` x3 plus `full_attention` x1 repeating, RoPE theta 10M with MRoPE sections, 16 attention heads with 4 KV heads, intermediate 12288; vision encoder `qwen3_5_vision` depth 27, hidden 1152, 16 heads, patch 16, spatial merge 2, temporal patch 2, output 4096; `image_token_id` 248056 and `video_token_id` 248057[^clef-flash-2026].
- Joint head `joint_head_config.json`: `hidden_size` 4096, `width` 1024, `routing_layers` 2, `layers` 4, `heads` 16, `feedforward` 4096[^clef-flash-2026].
- Head mechanics in `joint_schema_model.py::JointSchemaHead`: LayerNorm plus `memory/question/option_question/global/option_context/option_lexical` projections and 3-way `type_embedding`; two `EvidenceRoutingLayer` cross-attention blocks (query/memory LayerNorm, batch-first `MultiheadAttention`, dropout, GELU FFN); per-field option summary by dot-attention; four `TransformerDecoderLayer` passes over backbone memory; `field_norm`/`option_norm` plus scorer `Linear(4*width,width)->GELU->Linear(width,1)` combined with cosine similarity; lexical prior from output-embedding means versus question-plus-global anchor scaled by `exp(prior_logit_scale)`, joint term scaled by `exp(joint_logit_scale)` and gated by `sigmoid(residual_gate)`[^clef-flash-2026].
- Wrapper `joint_schema_model.py::ClefModel`: unwraps `get_base_model`, prefers `language_model` text path when no media, runs with `use_cache=False`, and routes `last_hidden_state` through the head[^clef-flash-2026].
- File ledger: backbone `model-*.safetensors` plus `model.safetensors.index.json`, `config.json`, `generation_config.json`; `joint_head.safetensors` plus `joint_head_config.json`; `joint_schema_model.py` for encoding, batching, model, `load_release_model`, and `systemone`; tokenizer plus image/video processor files; `LICENSE` Apache-2.0[^clef-flash-2026].

## Record encoding and decision API — observed

- Record shape: `state` any string or JSON value; optional `images` (PIL) and `videos` (frame arrays) plus `media_kwargs`; `questions` mapping IDs to `{type, instructions, criteria}` where `type` is `noul`, `choice`, or `score`; `instructions` optional with question ID as fallback; `criteria` is optional true/false descriptions for `noul`, option-ID to description map for `choice` (sorted), and indexed description list for `score`[^clef-flash-2026].
- `encode_record`: renders `STATE` then `SCHEMA FIELDS` with `FIELD n / ID / TYPE / INSTRUCTION / ALLOWED OPTIONS / OPTION n {"option_id","description"} / END FIELD`; system prompt is `Read the complete state and schema. Decide every field jointly. Each answer must be exactly one of that field's allowed options.`; suffix is `<|im_end|> assistant <think> </think> JOINT SCHEMA DECISIONS:`; media placeholder IDs are spliced after the system/user prefix with `token_offset`; state is compact sorted JSON; defaults `max_length` 16384 with optional `max_state_tokens`; oversize schema raises and state is truncated to fit; empty input raises; question and option spans are shifted to final offsets[^clef-flash-2026].
- `collate_records`: pads to batch max with `pad_token_id`, builds `attention_mask`, concatenates `pixel_values/image_grid_thw/pixel_values_videos/video_grid_thw`, and offsets `mm_token_type_ids`; text-only and multimodal rows can mix in one batch[^clef-flash-2026].
- `systemone`: validates `model` string, `state` presence, nonempty `questions`, known types, and nonempty `choice`/`score` criteria; encodes, runs one forward pass, per-question softmax, and returns `{model, answers, usage:{input_tokens, output_tokens:0}}`; `systemone_answer` gives `noul` true probability, `choice` with `choice/confidence/probabilities`, and `score` with expected `score/confidence/legend/probabilities`, all rounded to 4 decimals[^clef-flash-2026].
- Loader `load_release_model`: tested with `torch` 2.11 and `transformers` 5.10.2 on one H200 plus `pillow` for media; `snapshot_download("Cloudflare/clef-flash")`, `Qwen3_5ForConditionalGeneration.from_pretrained` with `device_map`, disables `use_cache`, loads `joint_head.safetensors` strictly, moves head to device/dtype, and returns `(ClefModel.eval, AutoProcessor)`[^clef-flash-2026].

## Multimodal handling — observed

- `_encode_media`: no media yields no IDs; otherwise requires a processor, formats `IMAGE_PLACEHOLDER` x images plus `VIDEO_PLACEHOLDER` x videos, calls the processor with `images/videos` and `media_kwargs`, and keeps batch media keys plus first-row `mm_token_type_ids`[^clef-flash-2026].
- Processor `processor_config.json`: `Qwen3VLProcessor` with `Qwen2VLImageProcessor` (rescale, resize, normalize mean/std 0.5, patch 16, merge 2, temporal patch 2) and `Qwen3VLVideoProcessor` sampling at 2 fps with `min_frames` 4 and `max_frames` 768[^clef-flash-2026].
- Tokenizer `tokenizer_config.json`: `Qwen2Tokenizer`, `model_max_length` 262144, pad `<|endoftext|>`, eos `<|im_end|>`, vision delimiters `<|vision_start/end|>` plus image/video/audio pad tokens[^clef-flash-2026].
- `chat_template.jinja` implements vision counting (`Picture N` / `Video N`), tool, multi-step-tool, and `<think>` branches for conversational backbone use; the decision path in `encode_record` builds its own `<|im_start|>` prompt instead of calling this template[^clef-flash-2026].

## Reported Decision Index results

- Suite is the authors' internal run of Decision Index 0.2.1; scores are percentages except ForecastBench Brier (lower better) and request-latency rows in ms (lower better); best per row is bold in source[^clef-flash-2026].
- Clef-Flash best on 17 rows: BFCL 98.8, API-Bank 93.1, home-appliance simulator 97.7, ContractNLI 84.3, Humicroedit 75.1, MMLU 91.8, ARC-Easy 99.5, ARC-Challenge 98.3, WinoGrande 97.5, HellaSwag 98.6, MuSR 86.0, SATA-Bench 36.7, FinEntity 97.1, CLadder 97.7, ForecastBench Brier 10.6, Habermas Machine 71.8, and p95 latency 122.4 ms[^clef-flash-2026].
- Larger Clef best on ToolRet 69.2, BANKING77 94.2, CLINC150+OOS 97.4, BPoMP 96.9, cfcolor 66.0, GSM8K 80.8, ChessBench 24.7, Amazon ESCI 57.5, ACOS 33.3, and CRUXEval 86.7; Jev best on ANLI 74.8, POP909-CL 18.1, GPQA Diamond 78.3, BRIGHT 47.5, VAST 64.6, NLI4CT 84.1, MMLU-Pro 82.7, BBH 92.9, HoVer 72.9, When2Call 81.0, and New Yorker 70.1; Kev 9B best on RouterBench 80.0 and SGD/SGD-X 64.0; DiffusionGemma Jev best on PhishNChips 85.4; Laya best only on median latency 5.8 ms versus Clef-Flash 38.8 ms, Jev 524.1 ms, and Clef 209.3 ms[^clef-flash-2026].
- Sharp gaps to note before selection: CLINC150+OOS Clef-Flash 66.8 versus Clef 97.4 and Jev 89.3; RAGTruth hallucination-F1 35.6 versus Clef 79.4 and Jev 76.5; POP909-CL 1.6 versus Jev 18.1; VAST 49.6 versus Jev 64.6; MMLU-Pro 65.3 and BBH 68.9 versus Jev 82.7 and 92.9; When2Call 65.6 versus Jev 81.0[^clef-flash-2026].

## Reported workflow evals

- Four end-to-end business workflows from Typesafe Evals, scored against consensus reference labels on the same dataset revision and case cohort[^clef-flash-2026].
- Invoice exact actions: Clef 64.7, Jev 61.8, Clef-Flash 57.1; invoice primary action: Clef 86.2, Jev 83.1, Clef-Flash 73.3[^clef-flash-2026].
- Customer-service exact actions: Clef-Flash 77.0, Clef 76.3, Jev 76.0; security-incident exact actions: Clef 62.9, Clef-Flash 61.7 tied with Jev 61.7; agent-trace observability primary action: Jev 71.6, Clef-Flash 69.8, Clef 68.5[^clef-flash-2026].

## Relationships

- Implements the typed-decision contract in [Jev API Patterns](jev-api-patterns.md) via a joint multi-question `state+questions` shape and `systemone` adapter rather than one-question hosted Choice/Noul/Score calls.
- Extends [Jev Decision Model](jev-decision-model.md) as a Cloudflare first-party multimodal alternative with Decision Index evidence on both sides of Jev.
- Informs [Classifier Selection](classifier-selection.md) when one self-hosted model must cover text/JSON plus image/video with single-pass multi-question scoring.
- Pairs with [Clef Multimodal Joint-Schema Decisions](clef-multimodal-decisions.md) as the smaller 9B sibling: identical decision code, smaller Qwen3.5-9B backbone and 4096-wide head, stronger tool-use/simulator/knowledge rows and lower latency, weaker intent-OOS/hallucination and invoice/security workflow rows.
- Contrasts with [Jev-Omni Multimodal Decision Classifier](jev-omni-multimodal-decisions.md), which natively covers audio as well as text/image/video on Gemma 4 12B, whereas Clef-Flash covers text/JSON/image/video with no audio path and a joint-schema multi-question head.
- Contrasts with [Jev-27B-VL Vision-Capable System 1 Decisions and Serving](jev-27b-vl-multimodal-decisions.md), whose vision is zero-shot from a text-trained head, whereas Clef-Flash ships a vision backbone plus joint head with explicit image/video encoding.
- Uses [System One Models and Jev Launch Claims](system-one-models.md) SystemOne-compatible response framing for `model/answers/usage`.

## Coverage limits

- Static inspection only; no GPU execution, API calls, or benchmark reproduction, so architecture, interfaces, and configs are **observed** while benchmarks, latencies, and workflow scores are **reported**.
- Inspected `README.md`, `joint_schema_model.py`, `config.json`, `joint_head_config.json`, `generation_config.json`, `tokenizer_config.json`, `processor_config.json`, `chat_template.jinja`, `LICENSE`, and `model.safetensors.index.json`; weight shards (`model-*-of-00004.safetensors`, `joint_head.safetensors`) are absent locally and only the 9,409,813,744-parameter / ~18.8 GB index metadata was read.
- `tokenizer.json` is a Git-LFS pointer and its bytes were not inspected; excluded decorative repetition and full 42-row table prose in favor of best-row plus gap summary with the source table as authority.
- No commit hash or release date is captured locally, so identity is the package scope; larger `Cloudflare/clef` results are now covered in [Clef Multimodal Joint-Schema Decisions](clef-multimodal-decisions.md) and are cited here only as table comparators.
- No calibration (ECE/temperature/Brier) or training-data/method detail is reported here; do not rank its probabilities against temperature-fitted concepts without independent calibration checks.

[^clef-flash-2026]: Cloudflare, "Clef-Flash," model card and code bundle, canonical local entry `../raw/clef-flash/README.md`, package scope `../raw/clef-flash/`, Hugging Face `Cloudflare/clef-flash` with base `Qwen/Qwen3.5-9B`, upstream announcement `https://blog.cloudflare.com/clef-decision-models` and leaderboard `https://clef-evals.workers-ai-mle.workers.dev`. Locators: "Model" backbone/head/output bullets; "Files" table; "Usage" torch/transformers/H200 plus invoice/choice-noul and Jev/SystemOne `systemone` examples; "Images and video" PIL record; "Input format" state/media/questions and per-type criteria; `encode_record(max_length,max_state_tokens)` limits; "Results / Decision Index" 0.2.1 table including latency rows; "Workflow evals" Typesafe four-workflow table; "License" Apache-2.0 line; `joint_schema_model.py::SYSTEM_PROMPT/render/question_options/EncodedQuestion/EncodedRecord/_tokens/_encode_media/encode_record/collate_records/EvidenceRoutingLayer/JointSchemaHead/ClefModel/load_release_model/systemone_answer/systemone`; `config.json` architectures/dtype/text/vision/token IDs; `joint_head_config.json` hidden/width/layers/heads/feedforward; `processor_config.json` Qwen3VL/image/video keys; `tokenizer_config.json` class/limits/special tokens; `chat_template.jinja` vision-count/tool/think branches; `model.safetensors.index.json` total-parameters/size metadata.
