---
type: Concept
title: Clef Multimodal Joint-Schema Decisions
description: Cloudflare Clef 27B multimodal decision model on Qwen3.8-27B with joint-schema head, Jev-compatible APIs, reported Decision Index and workflow results, and observed loader mechanics.
tags: [clef, decision-models, multimodal, classification, system-one]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T23:30:00Z }
sources:
  - id: clef-2026
    resource: ../raw/clef/README.md
    scope: ../raw/clef/
    kind: model-card
    title: Cloudflare/clef
---

# Clef Multimodal Joint-Schema Decisions

Synthesis: Clef is Cloudflare's 27B multimodal decision model that scores every allowed option of every typed question in one forward pass over text, JSON, images, or video — with **observed** Qwen3.8-27B plus joint-schema-head mechanics shared with Clef-Flash and a Jev/SystemOne-compatible `systemone` path, and **reported** Decision Index 0.2.1 plus Typesafe-workflow results where it leads intent-OOS, hallucination, and invoice/security rows but trails its smaller sibling on tool-use, simulator, and knowledge/reasoning rows at higher latency[^clef-2026].

## Identity and provenance

- Package `../raw/clef/` with canonical entry `README.md`; Hugging Face `Cloudflare/clef`, smaller variant `Cloudflare/clef-flash`; announcement on the Cloudflare blog and leaderboard at `clef-evals.workers-ai-mle.workers.dev`[^clef-2026].
- Base **reported** as `Qwen/Qwen3.8-27B` post-train (finetune); frontmatter `base_model_relation: finetune`; license Apache-2.0 following the base model[^clef-2026].
- Contract: `state` plus a schema of typed questions yields one logit per allowed option per question; apply per-question softmax for probabilities; no free-form generation and no output parsing; API fully compatible with Jev and SystemOne[^clef-2026].

## Architecture — observed

- Backbone `config.json`: `Qwen3_5ForConditionalGeneration`, `model_type: qwen3_5`, `dtype: bfloat16`, `transformers_version: 5.10.2`; text tower hidden 5120, 64 layers, vocab 248320, 262144 positions, hybrid `linear_attention` x3 plus `full_attention` x1 repeating, RoPE theta 10M with MRoPE sections, 24 attention heads with 4 KV heads, intermediate 17408; vision encoder `qwen3_5_vision` depth 27, hidden 1152, 16 heads, patch 16, spatial merge 2, temporal patch 2, output 5120; `image_token_id` 248056 and `video_token_id` 248057[^clef-2026].
- Joint head `joint_head_config.json`: `hidden_size` 5120, `width` 1024, `routing_layers` 2, `layers` 4, `heads` 16, `feedforward` 4096 — identical to Clef-Flash except `hidden_size` (4096 on Flash) tracking the larger backbone[^clef-2026].
- Head mechanics in `joint_schema_model.py::JointSchemaHead`: LayerNorm plus `memory/question/option_question/global/option_context/option_lexical` projections and 3-way `type_embedding`; two `EvidenceRoutingLayer` cross-attention blocks (query/memory LayerNorm, batch-first `MultiheadAttention`, dropout, GELU FFN); per-field option summary by dot-attention; four `TransformerDecoderLayer` passes over backbone memory; `field_norm`/`option_norm` plus scorer `Linear(4*width,width)->GELU->Linear(width,1)` combined with cosine similarity; lexical prior from output-embedding means versus question-plus-global anchor scaled by `exp(prior_logit_scale)`, joint term scaled by `exp(joint_logit_scale)` and gated by `sigmoid(residual_gate)` — **observed** byte-identical to the Clef-Flash copy of this file[^clef-2026].
- Wrapper `joint_schema_model.py::ClefModel`: unwraps `get_base_model`, prefers `language_model` text path when no media, runs with `use_cache=False`, and routes `last_hidden_state` through the head[^clef-2026].
- File ledger: backbone `model-*.safetensors` plus `model.safetensors.index.json`, `config.json`, `generation_config.json`; `joint_head.safetensors` plus `joint_head_config.json`; `joint_schema_model.py` for encoding, batching, model, `load_release_model`, and `systemone`; tokenizer plus image/video processor files; `LICENSE` Apache-2.0[^clef-2026].

## Record encoding and decision API — observed

- Record shape: `state` any string or JSON value; optional `images` (PIL) and `videos` (frame arrays) plus `media_kwargs`; `questions` mapping IDs to `{type, instructions, criteria}` where `type` is `noul`, `choice`, or `score`; `instructions` optional with question ID as fallback; `criteria` is optional true/false descriptions for `noul`, option-ID to description map for `choice` (sorted), and indexed description list for `score`[^clef-2026].
- `encode_record`: renders `STATE` then `SCHEMA FIELDS` with `FIELD n / ID / TYPE / INSTRUCTION / ALLOWED OPTIONS / OPTION n {"option_id","description"} / END FIELD`; system prompt is `Read the complete state and schema. Decide every field jointly. Each answer must be exactly one of that field's allowed options.`; suffix is `<|im_end|> assistant <think> </think> JOINT SCHEMA DECISIONS:`; media placeholder IDs are spliced after the system/user prefix with `token_offset`; state is compact sorted JSON; defaults `max_length` 16384 with optional `max_state_tokens`; oversize schema raises and state is truncated to fit; empty input raises; question and option spans are shifted to final offsets[^clef-2026].
- `collate_records`: pads to batch max with `pad_token_id`, builds `attention_mask`, concatenates `pixel_values/image_grid_thw/pixel_values_videos/video_grid_thw`, and offsets `mm_token_type_ids`; text-only and multimodal rows can mix in one batch[^clef-2026].
- `systemone`: validates `model` string, `state` presence, nonempty `questions`, known types, and nonempty `choice`/`score` criteria; encodes, runs one forward pass, per-question softmax, and returns `{model, answers, usage:{input_tokens, output_tokens:0}}`; `systemone_answer` gives `noul` true probability, `choice` with `choice/confidence/probabilities`, and `score` with expected `score/confidence/legend/probabilities`, all rounded to 4 decimals[^clef-2026].
- Loader `load_release_model`: tested with `torch` 2.11 and `transformers` 5.10.2 on one H200 plus `pillow` for media; `snapshot_download("Cloudflare/clef")`, `Qwen3_5ForConditionalGeneration.from_pretrained` with `device_map`, disables `use_cache`, loads `joint_head.safetensors` strictly, moves head to device/dtype, and returns `(ClefModel.eval, AutoProcessor)`[^clef-2026].

## Multimodal handling — observed

- `_encode_media`: no media yields no IDs; otherwise requires a processor, formats `IMAGE_PLACEHOLDER` x images plus `VIDEO_PLACEHOLDER` x videos, calls the processor with `images/videos` and `media_kwargs`, and keeps batch media keys plus first-row `mm_token_type_ids`[^clef-2026].
- Processor `processor_config.json`: `Qwen3VLProcessor` with `Qwen2VLImageProcessor` (rescale, resize, normalize mean/std 0.5, patch 16, merge 2, temporal patch 2) and `Qwen3VLVideoProcessor` sampling at 2 fps with `min_frames` 4 and `max_frames` 768 — identical to Clef-Flash[^clef-2026].
- Tokenizer `tokenizer_config.json`: `Qwen2Tokenizer`, `model_max_length` 262144, pad `<|endoftext|>`, eos `<|im_end|>`, vision delimiters `<|vision_start/end|>` plus image/video/audio pad tokens — identical to Clef-Flash[^clef-2026].
- `chat_template.jinja` implements vision counting (`Picture N` / `Video N`), tool, multi-step-tool, and `<think>` branches for conversational backbone use; the decision path in `encode_record` builds its own `<|im_start|>` prompt instead of calling this template. **Observed** difference from Clef-Flash: this copy adds `reasoning_effort` (`xhigh` default, `medium`, `low`) with injected reasoning instructions, a `preserve_thinking` gate, an empty-arguments guard, and string-vs-JSON argument rendering, while the Flash copy instead recovers embedded `<think>` content from the message body[^clef-2026].
- `generation_config.json` differs from Clef-Flash (`bos_token_id` 248044, `do_sample` true, `eos_token_id` [248046, 248044], `pad_token_id` 248044, `temperature` 1.0, `top_k` 20, `top_p` 0.95 versus Flash `_from_model_config` plus single eos and `use_cache`); the decision path does not sample — one forward pass plus per-question softmax — so this config governs conversational backbone use, not `systemone` scoring[^clef-2026].

## Reported Decision Index results

- Suite is the authors' internal run of Decision Index 0.2.1; scores are percentages except ForecastBench Brier (lower better) and request-latency rows in ms (lower better); best per row is bold in source[^clef-2026].
- Clef best on 11 rows: ToolRet 69.2, BANKING77 94.2, CLINC150+OOS 97.4, BPoMP 96.9, cfcolor 66.0, GSM8K 80.8, ChessBench 24.7, RAGTruth hallucination-F1 79.4, Amazon ESCI 57.5, ACOS 33.3, and CRUXEval 86.7[^clef-2026].
- Clef-Flash best on 17 rows: BFCL 98.8, API-Bank 93.1, home-appliance simulator 97.7, ContractNLI 84.3, Humicroedit 75.1, MMLU 91.8, ARC-Easy 99.5, ARC-Challenge 98.3, WinoGrande 97.5, HellaSwag 98.6, MuSR 86.0, SATA-Bench 36.7, FinEntity 97.1, CLadder 97.7, ForecastBench Brier 10.6, Habermas Machine 71.8, and p95 latency 122.4 ms; Jev best on ANLI 74.8, POP909-CL 18.1, GPQA Diamond 78.3, BRIGHT 47.5, VAST 64.6, NLI4CT 84.1, MMLU-Pro 82.7, BBH 92.9, HoVer 72.9, When2Call 81.0, and New Yorker 70.1; Kev 9B best on RouterBench 80.0 and SGD/SGD-X 64.0; DiffusionGemma Jev best on PhishNChips 85.4; Laya best only on median latency 5.8 ms versus Clef 209.3 ms, Clef-Flash 38.8 ms, and Jev 524.1 ms[^clef-2026].
- Tradeoffs to note before selection: Clef trails Flash sharply on home-appliance simulator 83.0 versus 97.7, Humicroedit 66.7 versus 75.1, and ForecastBench Brier 13.9 versus 10.6, plus knowledge/reasoning rows MMLU 90.3 versus 91.8, GPQA Diamond 48.0 versus Jev 78.3, MMLU-Pro 65.9 versus Jev 82.7, and BBH 73.7 versus Jev 92.9; its advantages over Flash concentrate in intent-OOS (CLINC150+OOS 97.4 versus 66.8), hallucination detection (RAGTruth 79.4 versus 35.6), and math/code rows (GSM8K 80.8 versus 67.3, CRUXEval 86.7 versus 86.1), at roughly 5x median latency (209.3 ms versus 38.8 ms) and 2x p95 (238.6 ms versus 122.4 ms)[^clef-2026].

## Reported workflow evals

- Four end-to-end business workflows from Typesafe Evals, scored against consensus reference labels on the same dataset revision and case cohort[^clef-2026].
- Invoice exact actions: Clef 64.7, Jev 61.8, Clef-Flash 57.1; invoice primary action: Clef 86.2, Jev 83.1, Clef-Flash 73.3[^clef-2026].
- Customer-service exact actions: Clef-Flash 77.0, Clef 76.3, Jev 76.0; security-incident exact actions: Clef 62.9, Clef-Flash 61.7 tied with Jev 61.7; agent-trace observability primary action: Jev 71.6, Clef-Flash 69.8, Clef 68.5[^clef-2026].

## Relationships

- Implements the typed-decision contract in [Jev API Patterns](jev-api-patterns.md) via a joint multi-question `state+questions` shape and `systemone` adapter rather than one-question hosted Choice/Noul/Score calls.
- Extends [Jev Decision Model](jev-decision-model.md) as a Cloudflare first-party multimodal alternative with Decision Index evidence on both sides of Jev.
- Pairs with [Clef-Flash Multimodal Joint-Schema Decisions](clef-flash-multimodal-decisions.md) as the larger 27B sibling: identical `joint_schema_model.py` decision code, larger Qwen3.8-27B backbone and 5120-wide head, stronger intent-OOS/hallucination and invoice/security workflow rows, weaker simulator/knowledge rows, and higher latency.
- Informs [Classifier Selection](classifier-selection.md) when one self-hosted model must cover text/JSON plus image/video with single-pass multi-question scoring and the accuracy/latency tradeoff between Clef and Clef-Flash matters.
- Contrasts with [Jev-Omni Multimodal Decision Classifier](jev-omni-multimodal-decisions.md), which natively covers audio as well as text/image/video on Gemma 4 12B, whereas Clef covers text/JSON/image/video with no audio path and a joint-schema multi-question head.
- Contrasts with [Jev-27B-VL Vision-Capable System 1 Decisions and Serving](jev-27b-vl-multimodal-decisions.md), whose vision is zero-shot from a text-trained head, whereas Clef ships a vision backbone plus joint head with explicit image/video encoding.
- Uses [System One Models and Jev Launch Claims](system-one-models.md) SystemOne-compatible response framing for `model/answers/usage`.

## Coverage limits

- Static inspection only; no GPU execution, API calls, or benchmark reproduction, so architecture, interfaces, and configs are **observed** while benchmarks, latencies, and workflow scores are **reported**.
- Inspected `README.md`, `joint_schema_model.py` (byte-identical to the Clef-Flash copy), `config.json`, `joint_head_config.json`, `generation_config.json`, `tokenizer_config.json`, `processor_config.json`, `chat_template.jinja`, `LICENSE`, `.gitattributes`, and `model.safetensors.index.json` metadata (27,356,728,560 parameters / ~54.7 GB across 12 shards); weight shards (`model-*-of-00012.safetensors`, `joint_head.safetensors`) are absent locally.
- `tokenizer.json` is a Git-LFS pointer (`sha256:06b9509352d2af50381ab2247e083b80d32d5c0aba91c272ca9ff729b6a0e523`, 19,989,325 bytes) and its bytes were not inspected; excluded decorative repetition and full 42-row table prose in favor of best-row plus gap summary with the source table as authority.
- No commit hash or release date is captured locally, so identity is the package scope; smaller `Cloudflare/clef-flash` results are cited only as table comparators with static config/code diffs, not a re-ingest of that package.
- No calibration (ECE/temperature/Brier) or training-data/method detail is reported here; do not rank its probabilities against temperature-fitted concepts without independent calibration checks.

[^clef-2026]: Cloudflare, "Clef," model card and code bundle, canonical local entry `../raw/clef/README.md`, package scope `../raw/clef/`, Hugging Face `Cloudflare/clef` with base `Qwen/Qwen3.8-27B`, upstream announcement `https://blog.cloudflare.com/clef-decision-models` and leaderboard `https://clef-evals.workers-ai-mle.workers.dev`. Locators: "Model" backbone/head/output bullets; "Files" table; "Usage" torch/transformers/H200 plus invoice/choice-noul and Jev/SystemOne `systemone` examples; "Images and video" PIL record; "Input format" state/media/questions and per-type criteria; `encode_record(max_length,max_state_tokens)` limits; "Results / Decision Index" 0.2.1 table including latency rows; "Workflow evals" Typesafe four-workflow table; "License" Apache-2.0 line; `joint_schema_model.py::SYSTEM_PROMPT/render/question_options/EncodedQuestion/EncodedRecord/_tokens/_encode_media/encode_record/collate_records/EvidenceRoutingLayer/JointSchemaHead/ClefModel/load_release_model/systemone_answer/systemone`; `config.json` architectures/dtype/text/vision/token IDs; `joint_head_config.json` hidden/width/layers/heads/feedforward; `processor_config.json` Qwen3VL/image/video keys; `tokenizer_config.json` class/limits/special tokens; `chat_template.jinja` reasoning-effort/preserve-thinking/tool branches; `generation_config.json` sampling keys; `model.safetensors.index.json` total-parameters/size metadata.
