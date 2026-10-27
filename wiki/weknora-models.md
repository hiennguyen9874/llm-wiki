---
type: Concept
title: WeKnora model types, bindings and configuration surfaces
description: Five model types as encrypted tenant-scoped rows, per-knowledge-base and per-agent bindings, provider and catalog overlays, and which pipeline stages actually call a model.
tags: [ml, weknora, models, configuration]
status: draft
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T10:20:00Z }
stale_after: 2027-01-27
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a2586fd58
    title: WeKnora v0.8.3 repository snapshot
---

WeKnora treats a model as a **database row**, not a hard-coded client: five types (chat/KnowledgeQA, embedding, rerank, VLM, ASR) are created by an administrator, a startup YAML loader, or the CLI, store AES-encrypted credentials, and are then referenced by ID from knowledge bases, agents, and workspace settings. **Observed:** only four stages call a model on the ingestion path — embedding, image caption/OCR through a VLM, and post-chunk enrichment through the summary model — while the docreader parser and the chunker make **no model calls at all**. Parser "models" such as MinerU or PaddleOCR-VL are external services configured on the parser engine, not rows in the `models` table.[^weknora]

## Model types and rows

**Observed:** `internal/types/model.go` declares `KnowledgeQA`, `Embedding`, `Rerank`, `VLLM`, and `ASR`, and `internal/models/model_type.go::ParseModelType` accepts the frontend spellings `chat`, `embedding`, `rerank`, `vlm`/`vllm`, `asr` as aliases. A row carries `Type`, `Source`, `Parameters`, `IsDefault`, `IsBuiltin`, `ManagedBy`, and a `Status` whose non-active values are `downloading` and `download_failed`, so local model acquisition is modelled as row state rather than only as a process concern.[^weknora]

`ModelParameters` includes `base_url`, `api_key`, provider name, embedding parameters (`dimension`, `truncate_prompt_tokens`), `context_window`, `max_concurrency`, `supports_vision`, and an optional per-row catalog `Spec` override. **Observed:** `ModelParameters.Value` encrypts `api_key`/`app_secret` with the system AES key before persisting and `Scan` decrypts them, treating legacy plaintext as valid — the row-level complement to the [configuration and key management](weknora-configuration.md) behaviour.[^weknora]

## Where a model is bound

**Observed** bindings, resolved by ID through `model.list`:

| Scope | Fields | Purpose |
| --- | --- | --- |
| Knowledge base (`internal/types/knowledgebase.go`) | `embedding_model_id` | Index and query embeddings; **cannot be changed once the KB has documents** |
| Knowledge base | `summary_model_id` | Document summaries, KB profile/AI description, and the default for auto-tagging |
| Knowledge base | `vlm_config.model_id` | Image captions |
| Knowledge base | `image_processing_config.model_id` | Per-image describe model; empty falls back to the KB caption model |
| Knowledge base | `asr_config.model_id` | Audio transcription |
| Knowledge base | `wiki_config.synthesis_model_id` | Wiki page generation; empty falls back to the summary model |
| Knowledge base | `auto_tag_config.model_id` | Automatic tagging; empty falls back to the summary model |
| Knowledge base | `question_generation_config` | Has **no** model field — enabling per-chunk question generation does not let a KB pick a different model |
| Agent (`internal/types/custom_agent.go`) | `model_id`, `rerank_model_id`, `vlm_model_id`, `asr_model_id`, `query_understand_model_id`, `question_suggestions.follow_ups.model_id` | Chat loop, retrieval reranking, tool images, audio, query-understanding override, follow-up suggestions |
| Workspace (`internal/types/retrieval_config.go`, `memory.go`) | `rerank_model_id` (required for search), `memory_config.extract_model_id` | Retrieval reranking; memory distillation, where empty means "the model the conversation itself used" |

**Observed:** `internal/application/repository/model_usage.go` derives these references per KB and per agent, and `ModelUsageDetails` blocks deletion of an in-use model while listing at most `ModelUsageListLimit` (50) blocking resources plus separate totals. **Synthesis:** the guard makes model identity a lifecycle dependency, which is why the embedding-model immutability rule cannot be worked around by deleting and re-creating rows.[^weknora]

## Configuration surfaces

Three surfaces exist and are not interchangeable:[^weknora]

- **Model rows (runtime).** UI/API/CLI (`cli/cmd/model/{create,list,view,update,delete}.go`) create ordinary rows with `managed_by=""`.
- **`config/builtin_models.yaml` (startup, row-creating).** Copied from `builtin_models.yaml.example`, path overridable through `BUILTIN_MODELS_CONFIG`. Entries are upserted by `id` with `is_builtin=true` and become visible to every tenant; string fields interpolate `${VAR}` and leave unset variables as literal text so misconfiguration surfaces in the upstream call. `internal/types/builtin_models_config.go` documents the lifecycle: only `managed_by="yaml"` rows are modified, `is_default=true` clears the flag on other rows in the same `(tenant_id, type)` bucket, removed entries are soft-deleted, and a missing/malformed file is a no-op rather than a wipe.
- **`config/models.json` (catalog overlay, not rows).** Copied from `models.json.example`, path overridable through `MODELS_CONFIG`. This patches or declares **vendors** (base URL, auth header shape, icons, `model_types`, and per-model metadata such as `reasoning`, `input` modalities, `context_window`, `compat`), rejects unknown keys at startup, and interpolates `${ENV}`. It changes what the picker knows about a model, not which model a KB runs.

**Observed provider set:** `internal/models/providers/providers_test.go::expectedIDs` pins **30** vendor IDs — `generic`, `weknoracloud`, `huggingface_tei`, `aliyun`, `zhipu`, `volcengine`, `hunyuan`, `siliconflow`, `deepseek`, `minimax`, `moonshot`, `mimo`, `modelscope`, `qianfan`, `qiniu`, `longcat`, `lkeap`, `openai`, `azure_openai`, `anthropic`, `gemini`, `openrouter`, `litellm`, `requesty`, `pinecone`, `jina`, `nvidia`, `novita`, `gpustack`, `cohere`. `source: local` routes through Ollama instead of a vendor, and embedding and chat can share one Ollama process.[^weknora]

## Stage-by-stage: which stages call which model

| Stage | Model call | Detail |
| --- | --- | --- |
| Parse (docreader) | **None** | `docreader/parser/base_parser.py` and `parser.py` state that chunking, OCR, and VLM captioning are done in Go; `pdf_parser.py` only renders page/chart regions for the Go side to read |
| Parse (external engines) | External service, not a model row | `ParserEngineConfig` (tenant) and `parser_engine_rules` (per KB) select MinerU self-hosted/cloud (`mineru_model`: `pipeline`, `vlm-*`, `hybrid-*`; cloud `model_version`: `pipeline`, `vlm`, `MinerU-HTML`), PaddleOCR-VL self-hosted or AI Studio cloud (e.g. `PaddleOCR-VL-1.6`), and OpenDataLoader hybrid backends (`docling-fast`, `hancom-ai`) |
| Image caption / OCR | **VLM** | `runOCRAction` calls the VLM with a system-owned prompt (`scanned_pdf` or default), validates the text, and maps truncation to `OCR_TRUNCATED`; the default pipeline captions then OCRs, `smartocr` observes and captions first, then decides whether OCR is worth a call (`ocr_on_unobserved` defaults to true) |
| Chunk | **None** | `ChunkingConfig` is character/token-approximate and strategy-based (`auto`, `heading`, `heuristic`, `recursive`, `legacy`); `internal/infrastructure/chunker` references no model package |
| Post-chunk enrichment | Summary model | Document summary, KB profile/description, auto-tagging, chunk/graph extraction, table summary, and generated questions run after chunking |
| Embed (index + query) | Embedding model | Bound per KB; multi-KB search rejects differing embedding models; optional image vectors use a KB embedding model that accepts images |
| Retrieve / rerank | Rerank model | Bound on retrieval config or agent; model failure degrades to retrieval order instead of inventing scores |
| Chat / agent | Chat model | Agent-level `model_id`, optional query-understanding override, follow-up suggestion model |
| Graph extraction | Chat model | `internal/application/service/graph.go` builds entities/relations through `chatModel.Chat` with the extraction prompts |
| Wiki compilation | Synthesis model | Falls back to the summary model when unset |
| Memory distillation | Extract model | Background only; `Recall` makes no model call |

**Synthesis:** this is the sharpest difference from platforms that document one "VLM" or "embedding" client per feature — WeKnora's model choice is data, so the same deployment can mix vendors per knowledge base, and the code path that reads an image is always the VLM role regardless of which vendor serves it.[^weknora]

## Capability catalog versus provider behavior

**Observed:** `internal/models/catalog` is "an immutable model index for one provider" with "no provider behavior or global registry", loaded from `data/models.generated.json`, `data/overrides.json`, and `data/seed.json`. `ModelsByType` hides deprecated and pattern-only entries, and the VLM picker lists **chat models that accept images** — so a vision-capable chat row can serve the image stages without a separate VLLM row. Entries carry vendor-documented `match` patterns, `reasoning`, input modalities, and `compat` switches (for example `thinking_always_send`, `thinking_disable_on_non_stream` for Aliyun Qwen families). **Limit:** only the catalogue head and structure were sampled, so the full vendor/model inventory is *not* reproduced here.[^weknora]

## Contradictions

- **Vendor count.** The README's current feature table says 29 model vendors, its v0.8.2 note and architecture SVG say 27, and the v0.8.3 test-enforced provider list contains 30 IDs. The counting rule is not established in the inspected files (`generic` and the Tencent-hosted entries may or may not be counted as vendors), so no single number is presented as the verified catalogue size. See the [source map](weknora-source-map.md), which already records this drift.

## Relationships

- Feeds [document parsing and chunking](weknora-document-ingestion.md): parsing and chunking are model-free, but image caption/OCR and embedding are not.
- Feeds [hybrid retrieval and reranking](weknora-hybrid-retrieval.md), where the embedding model is a cross-KB constraint and rerank failure degrades.
- Supplies the chat model to the [agent runtime](weknora-agent-runtime.md) and the [wiki compilation](weknora-wiki-compilation.md) synthesis role.
- Supplies the extract model to [cross-session memory](weknora-memory.md).
- Depends on [configuration and key management](weknora-configuration.md) for credential encryption and environment interpolation.
- Constrained by [security boundaries](weknora-security.md): credentials live in model rows and outbound lockdown can block external providers.
- Per-model background concurrency is governed by [task queue](weknora-task-queues.md) settings.

## Coverage limits

Static inspection only: no model, provider, parser engine, or OCR call was executed, and no configuration file was validated against the loader. Read selectively: model types and row schema, both YAML/JSON examples, the provider ID list, catalog structure, KB/agent/workspace binding fields, the usage guard, `ParserEngineConfig`, the image action registry and smartocr pipeline, `ChunkingConfig`, and the graph builder's chat call. Not established: end-to-end precedence when an agent, KB, and tenant default disagree; how each provider adapter maps a given model to a protocol; the full catalog contents; whether every ASR/embedding adapter honours the same capability flags; and which model actually serves generated questions. See the [source map](weknora-source-map.md).

[^weknora]: Snapshot `fd7a2586fd58`: `internal/types/model.go::ModelType`, `ModelUsageBinding`, `ModelSource`, `ModelParameters.Value`, `Scan`; `internal/models/model_type.go::ParseModelType`, `frontendTypes`; `internal/types/knowledgebase.go::ChunkingConfig`, `ImageProcessingConfig`, `QuestionGenerationConfig`, `ExtractConfig`, `ASRConfig`, `KnowledgeBase`; `internal/types/custom_agent.go::Config` model fields; `internal/types/retrieval_config.go::RerankModelID`; `internal/types/memory.go::MemoryConfig.ExtractModelID`; `internal/types/wiki_page.go::WikiConfig.SynthesisModelID`; `internal/types/tenant.go::ParserEngineConfig` MinerU/PaddleOCR-VL/OpenDataLoader fields; `internal/types/builtin_models_config.go::LoadBuiltinModelsConfig` lifecycle comment; `internal/application/repository/model_usage.go::knowledgeBaseModelUsageBindings`, `customAgentModelUsageBindings`; `internal/application/service/image_action_registry.go::runOCRAction`, `buildVLMOCRPrompt`, `validateOCRText`; `image_pipeline_default.go`, `image_pipeline_smartocr.go`; `internal/application/service/graph.go::NewGraphBuilder`, extraction `chatModel.Chat` calls; `internal/models/vlm/vlm.go::VLM.Predict`, `PredictOptions.Thinking`; `internal/models/catalog/catalog.go::ModelsByType`; `internal/models/providers/providers_test.go::expectedIDs`; `config/builtin_models.yaml.example` header and entries; `config/models.json.example` comments; `config/config.yaml` conversation/extraction prompt ids; `.env.example` model sections; `docreader/parser/base_parser.py` module docstring, `pdf_parser.py` OCR/VLM handoff comments. Package entry: [README](../raw/WeKnora/README.md), “Architecture” model-catalog panel and “Features.”
