---
type: Synthesis
title: WeKnora Vietnamese-language deployment readiness and roadmap
description: Code-grounded gaps in WeKnora's language resolution, UI locales, prompts, ingestion, keyword retrieval and evaluation for Vietnamese, with a phased configuration-then-patch deployment plan and verification checklist.
tags: [rag, operations, weknora, i18n, vietnamese, roadmap, synthesis]
status: draft
created: 2026-11-04
generated: { by: llm-wiki-agent/1, at: 2026-11-04T04:00:00Z }
stale_after: 2027-02-04
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a2586fd58
    title: WeKnora v0.8.3 repository snapshot
---

**Synthesis:** at `fd7a2586fd58`, WeKnora can answer in Vietnamese as long as the chat LLM can, because its main prompts are English and carry a `{{language}}` slot. It does not support Vietnamese as a first-class language. **Observed:** the six supported locales (zh-CN, zh-TW, en-US, ko-KR, ja-JP, ru-RU) are hard-coded in the backend and frontend; the locale-to-name mapper has no Vietnamese entry; the default rewrite prompt's few-shot examples are Chinese; the chunker's language heuristics know only English, German and Chinese; and the default PostgreSQL BM25 index uses the `chinese_lindera` tokenizer. Even with Vietnamese-capable LLM, embedding, rerank and PaddleOCR-VL services, a Vietnamese deployment needs configuration choices first, then a small set of code changes. Keyword retrieval quality must be measured rather than assumed.[^weknora]

## Readiness summary

| Area | State at this pin | Vietnamese impact | Action class |
| --- | --- | --- | --- |
| Answer language | English prompts + `{{language}}`; env/header resolution | Works if the language value is meaningful | Config, then a one-line mapping patch |
| Locale registry | Six locales hard-coded in Go and TS | `vi-VN` is rejected for IM/embed channels and the UI | Code patch |
| Query rewrite/intent | Default few-shots in Chinese | Possible Chinese drift or weaker intent routing | Prompt override |
| Ingestion text | No encoding detection for Vietnamese legacy code pages, no NFC step found | Possible mojibake and NFC/NFD mismatch | Pre-processing or patch |
| Chunking heuristics | en/de/zh detection, patterns and separators | Vietnamese is treated as English; legal headings unmatched | Config + patch |
| PaddleOCR-VL engine | Fixed request parameters | Orientation/unwarp off; footnotes dropped | Check, optional patch |
| Keyword retrieval | ParadeDB `chinese_lindera`, any-token `\|\|\|` | Behavior on Vietnamese unverified | Measure, then choose an index strategy |
| Local query expansion | zh/en stopwords; whitespace segments | Single-syllable keyword-only variants | Patch |
| Vector index | HNSW partial indexes for dims 798/1024/3584 | Other dims fall back to sequential scan | Model choice or migration |
| Evaluation metrics | Built-in BLEU/ROUGE tokenizer is Han/ASCII only | Vietnamese text-overlap scores corrupted | Use other metrics |

## Language resolution

**Observed:** `middleware.Language` resolves the request language in this order: `WEKNORA_LANGUAGE`, then the first `Accept-Language` tag, then a hard-coded `zh-CN`. `types.DefaultLanguage` also falls back to `zh-CN`. Async workers call `ResolveLanguage`: payload locale first, then context, then the default.[^weknora]

The frontend sends its UI locale as `Accept-Language`. Without `WEKNORA_LANGUAGE`, a user running the UI in English therefore gets English summaries, generated questions, wiki pages and default answers, even for Vietnamese documents. Wiki ingest ops persist the resolved language at enqueue time.[^weknora]

**Observed:** `LanguageLocaleName` maps zh/en/ko/ja/ru/fr/de/es/pt to display names and returns any other value unchanged. With `vi-VN`, prompts therefore receive the literal `vi-VN` rather than "Vietnamese". **Synthesis:** capable LLMs usually understand the tag, but the mapping should be added and the result measured. The MCP usage-instruction generator uses its own six-locale map and falls back to **Simplified Chinese** for any other language.[^weknora]

**Observed:** IM channel locales and embed-channel default locales are validated by `NormalizeSupportedLocale`. `vi-VN` is rejected for IM with an error listing the six locales, and normalized to empty (follow the browser) for embed. IM channels without a locale use `DefaultLanguage()`. In both cases `WEKNORA_LANGUAGE` is the configuration lever.[^weknora]

## UI localization

**Observed:** vue-i18n registers six locale bundles of roughly 8,800 lines each. The built-in default is `zh-CN`. `DEFAULT_LOCALE` and `VITE_DEFAULT_LOCALE` accept only the six tags, and the Docker entrypoint filters on the same list. Adding `vi-VN` touches at least:

- `frontend/src/i18n/locales/`
- the `index.ts`, `resolveDefaultLocale.ts`, `localeKeyAudit.ts` and `embed.ts` bundles and supported-locale lists
- TDesign locale imports in `App.vue`
- language pickers in `GeneralSettings.vue`, `Login.vue`, `IMChannelPanel.vue` and `AgentEmbedChannelPanel.vue`
- locale union types in `api/agent` and `api/embed`
- `docker-entrypoint.sh`, `public/config.js` and the widget documentation
- backend `types/locale.go` and the IM locale error message[^weknora]

Whether `tdesign-vue-next` ships a Vietnamese locale was not checked, because `node_modules` is absent from the snapshot.

Some backend-originated labels bypass vue-i18n. Agent tool-hint display names (`agent/act.go::toolDisplayNames`) and IM tool labels (`im/tool_display.go::imToolNameLabels`, documented as zh-CN) are Chinese literals. A grep found quoted Han-script literals in 212 non-test Go files under `internal/`, including Swagger annotations and comments inside strings. Which of these reach users was not audited.[^weknora]

## Prompts

**Observed:** all 12 prompt-template files are English-bodied, with `{{language}}` in answer, keyword-extraction, question-generation, graph-extraction and rewrite prompts. Han text in the other template files appears only in i18n `name`/`description` labels. `rewrite.yaml` is the exception: the default rewrite-with-intent template carries Chinese intent examples and few-shot input/output pairs.

The `standard_rewrite` and `strict_rewrite` templates say the rewritten question "MUST be in {{language}}". The default template instead keeps the user's language unless translation is requested. Templates load from `config/prompt_templates`, and agents expose `rewrite_prompt_system` overrides. Compose mounts only `config/config.yaml` by default.[^weknora]

**Synthesis:** replace or extend the rewrite few-shots with Vietnamese examples (greeting, follow-up, kb_search, doc/image-only). If a forced-language rewrite template is used with a mixed English/Vietnamese corpus, measure whether translation hurts recall on English documents.

## Ingestion and chunking

### Encoding and normalization

**Observed:** the Go simple reader passes `.txt`/`.md` bytes through as a string without decoding. Docreader's `decode_bytes` tries utf-8, gb18030, gb2312, gbk, big5, ascii, then latin-1. No Unicode NFC normalization was found on ingestion or query paths. The only hits were product docs and an NFKC comparison helper in docreader's source locator.

**Synthesis/Unverified:** Windows-1258 or TCVN3/VNI legacy files are likely to decode as gb18030 or latin-1 mojibake. Decomposed (NFD) diacritics will not match NFC queries lexically. Convert sources to UTF-8 NFC before upload, or add a normalization step at both ingest and query time. Legacy-font PDFs whose text layer is garbled need OCR routing rather than text extraction.[^weknora]

### Language heuristics

**Observed:** `chunker.DetectLanguage` counts CJK runes and ASCII a–z/A–Z only, with a German umlaut/stopword bias. Vietnamese is therefore labelled `en`, and diacritic letters are not counted. Its 4.0 chars/token ratio is used for `CharsForTokenLimit` when `token_limit` is set, and for reported token estimates.

Defaults are 512 chars, 80 overlap, and separators `\n\n`, `\n`, `。`. Chapter patterns cover Kapitel/Chapter/第…章. `AllCapsHeadingPattern` allows only A–Z plus ÄÖÜ, and the page-footer pattern knows Seite/Page/页. Structures such as `Chương`, `Mục`, `Điều`, `Khoản` and uppercase headings with Ư/Đ/Ơ are not matched unless the parser already emits Markdown headings.

**Synthesis:** measure actual chars/token with the chosen embedding tokenizer. Set separators (`. `, `; `, `\n`) and size through the knowledge base's `ChunkingConfig`, or patch the patterns. Embedding settings also expose `max_input_chars` and truncation fields as a provider-side guard.[^weknora]

### PaddleOCR-VL and other parsers

**Observed:** the self-hosted PaddleOCR-VL reader posts to `{endpoint}/layout-parsing` with fixed parameters:

- `useDocOrientationClassify=false`, `useDocUnwarping=false` and `useOcrForImageBlock=false`
- `mergeTables`, `relevelTitles` and `restructurePages` set to true
- `markdownIgnoreLabels` covering header, footer, number, **footnote** and aside_text
- temperature 0 and a 1000 s timeout

There is no language parameter, and PDF/images are distinguished by `fileType`. **Synthesis:** rotated phone scans may degrade, footnote text is discarded (material for legal or academic documents), and the deployed service must accept these parameter names. Verify against your PaddleOCR/PaddleX version.

MinerU converters default `language` to `ch`, which matters only if MinerU is a fallback engine. The VLM caption/attribute prompts use `VLMConfig.DescriptionLanguage`, else the request language. The VLM OCR prompts preserve the source language. ASR accepts a per-KB language hint.[^weknora]

## Retrieval

### Keyword index

**Observed:** PostgreSQL migration 000002 creates the BM25 index on `embeddings.content` with tokenizer `chinese_lindera`. Keyword search uses `content ||| ?`, which matches any token.

**Unverified:** how `chinese_lindera` tokenizes Vietnamese, including syllable splitting, case folding and diacritic handling. **Synthesis:** with syllable-level tokens, an any-token query lets frequent function syllables match many chunks, relying on BM25 IDF for ranking.

Other drivers differ:

- **Elasticsearch v8:** creates indexes without mappings (dynamic/standard analysis).
- **OpenSearch:** maps `content` with the `standard` analyzer.
- **Milvus:** routes text with ASCII letters and no Han characters to its English analyzer, with ICU only as a fallback.
- **Qdrant:** uses a multilingual text index but tokenizes queries with jieba and drops tokens shorter than two runes.
- **SQLite Lite:** FTS5 `unicode61`.

**Unverified:** that jieba splits diacritic syllables. This must be tested before choosing Qdrant keyword search.[^weknora]

**Synthesis:** for production, either create a Vietnamese-appropriate ParadeDB index (lowercase, optional accent-folded field, stopword handling, optional word segmentation), or pre-create an Elasticsearch/OpenSearch index with an explicit Vietnamese/ICU analyzer. Gate the change on keyword-recall evaluation. Both are fork or ops changes, because the shipped migration and mapping are fixed.

### Query expansion and dedup

**Observed:** `expandQueries` removes zh/en stopwords and Chinese question prefixes. It also adds every whitespace-delimited segment longer than 5 bytes as a keyword-only variant, up to five variants. **Synthesis:** for Vietnamese this produces single-syllable searches such as "nghiệp". Add Vietnamese stopwords and question words (`là gì`, `như thế nào`, `bao nhiêu`, …) and skip single-syllable segments.

Result dedup uses whitespace tokens for non-Chinese text, which is script-safe. See [hybrid retrieval](weknora-hybrid-retrieval.md) for fusion and rerank behavior; no language-specific rerank code was found in the inspected paths.[^weknora]

### Embedding

**Observed:** PostgreSQL vector search depends on partial HNSW expression indexes per dimension. Migrations create them for 3584, 798 and 1024. Asymmetric query/passage handling is passed only through a vendor `input_type_field`/`input_type_values` setting. No text-prefix instruction mechanism was found in the inspected embedding settings.

**Synthesis:** prefer a 1024-dimensional Vietnamese-capable model, or add a matching index migration. For instruction-prefixed models, apply prefixes in the serving layer or choose a symmetric model. Never mix embedding models in one knowledge base without re-indexing.[^weknora]

## Wiki, channels and evaluation

- **Wiki:** `slugify` is applied to knowledge IDs, not titles. Wiki dedup uses Unicode-letter bigrams. PostgreSQL title search uses `pg_trgm` on `lower(title)`. **Unverified:** trigram behavior for Vietnamese depends on the database character-type locale; check `lc_ctype`.[^weknora]
- **Channels:** IM tool labels are Chinese. No Zalo connector was found by a name search.[^weknora]
- **Evaluation:** the built-in BLEU/ROUGE word splitter matches Han blocks, ASCII runs and punctuation, so Vietnamese diacritic letters are dropped or split. Use ID-based retrieval metrics (recall, MRR, NDCG) plus a pinned external judge, for example via [Ragas](ragas-rag-metrics.md), for Vietnamese answers.[^weknora]
- **Ops defaults:** `.env.example` sets `TZ=Asia/Shanghai`.[^weknora]

## Phased roadmap

All phases, gates and priorities are **Synthesis / proposals**, not observed product results. Run them as one feature flag per mechanism, following the [selective fork roadmap](weknora-fork-roadmap.md).

| Phase | Work | Acceptance gate |
| --- | --- | --- |
| 0. Baseline | Pin version; choose retrieval backend and 1024-dim embedding (or add an index); build a reviewed Vietnamese dev/held-out set covering scans, tables, legal headings, acronyms, accent-less queries, vi/en mix and no-answer cases | Baseline recall/answer/latency recorded with configuration and model versions |
| 1. Config-only | `WEKNORA_LANGUAGE=vi-VN`, `TZ=Asia/Ho_Chi_Minh`, `DEFAULT_LOCALE=en-US`; register models (input limits/truncation); per KB: PaddleOCR-VL parser rules, VLM `description_language=Vietnamese`, ASR `language=vi`, separators and size or parent-child; mount Vietnamese rewrite few-shots; check `lc_ctype`; convert sources to UTF-8 NFC | Vietnamese summaries, questions, wiki and answers on the sample set; no Chinese drift in rewrite logs |
| 2. Minimal backend patch | Map `vi`/`vi-VN` to "Vietnamese"; add `vi-VN` to supported locales and the MCP map; Vietnamese detection, chars/token, heading/footer/all-caps patterns and sentence separators; Vietnamese stopwords/question words and no single-syllable expansion; NFC at ingest and query; legacy-encoding handling; localized tool labels | Unit tests for each mapping and pattern; chunk-boundary and token-limit regression cases pass |
| 3. Keyword retrieval | Compare current `chinese_lindera` against a Vietnamese tokenizer or analyzer (with and without accent folding or word segmentation); migrate the index via a parity-preserving migration | Keyword recall and hybrid answer quality improve on held-out data without latency regressions; rollback tested |
| 4. UI and channels | `vi-VN` locale bundle (~8.8k lines), registration everywhere listed above, TDesign fallback, locale-audit tests; IM/embed locale | Locale-key audit passes; manual UI pass; IM/embed accept `vi-VN` |
| 5. Go-live and monitoring | Release gate on the held-out set; trace degraded retrieval paths; periodic re-evaluation after model changes | Thresholds agreed with users; regression set rerun on every upgrade |

## Verification checklist

- Confirm the effective language in logs and prompts, for both a header-only path and an env path. Confirm async workers (summary, questions, wiki, VLM) inherit it.
- Send the same question with and without diacritics, in NFC and NFD forms, in mixed vi/en, and with acronyms, legal references (`Điều 5 Khoản 2`), dates and Vietnamese number formats. Compare keyword-only, vector-only and hybrid hits.
- Inspect chunks of a real legal document, a scanned PDF and a large table for heading boundaries, token limits, footnote loss and table merges.
- Upload a non-UTF-8 text file to confirm the failure mode before relying on pre-conversion.
- Check `SHOW lc_ctype`, the ParadeDB extension version, the BM25 index definition and the HNSW index used (`EXPLAIN`) for the chosen dimension.
- Evaluate with retrieval ID metrics and a pinned judge, not built-in BLEU/ROUGE.

## Contradictions

- `.env.example` documents the language priority as `Accept-Language` > `WEKNORA_LANGUAGE` > built-in `en-US`. The inspected middleware and `DefaultLanguage` implement `WEKNORA_LANGUAGE` > `Accept-Language` > `zh-CN`. **Observed code is preferred for deployment planning**, but runtime behavior was not executed.[^weknora]

## Relationships

- **Depends on:** [model types and bindings](weknora-models.md), [parsing and chunking](weknora-document-ingestion.md), [hybrid retrieval](weknora-hybrid-retrieval.md), [wiki compilation](weknora-wiki-compilation.md), [publishing channels](weknora-publishing-channels.md), [deployment](weknora-deployment.md) and [configuration](weknora-configuration.md).
- **Uses:** the [selective fork roadmap](weknora-fork-roadmap.md) release discipline. It refines that roadmap's Vietnamese/English terminology gate into concrete phases.
- **Audited by:** [WeKnora source map](weknora-source-map.md), where this follow-up's inspected files are reconciled.

## Evidence and coverage limits

Static, targeted inspection only. No WeKnora build, test, migration, tokenizer, model, OCR or query was executed, and no Vietnamese benchmark exists. Statements about how ParadeDB, jieba, pg_trgm or legacy Vietnamese encodings behave are external expectations, labelled **Unverified** or **Synthesis**. TDesign Vietnamese locale availability, the user-visibility of backend Han literals, Elasticsearch v7 mappings, Doris, Weaviate, Tencent VectorDB, web-search language settings and every format-specific parser body remain unreviewed. The user-supplied premise that the LLM, embedding, reranker and PaddleOCR-VL support Vietnamese was taken as given, not verified.

[^weknora]: Snapshot `fd7a2586fd58`, canonical [README](../raw/WeKnora/README.md). Locators (paths package-relative):
    - **Language resolution:** `internal/middleware/language.go::Language`; `internal/types/context_helpers.go::DefaultLanguage`, `ResolveLanguage`, `LanguageLocaleName`; `internal/types/locale.go::supportedLocales`; `internal/types/embed_channel.go::NormalizeEmbedDefaultLocale`; `internal/handler/im.go::normalizeIMLocale`; `internal/im/service.go` channel-locale context; `internal/handler/mcp_usage_instructions.go` language map; `internal/application/service/wiki_ingest.go::newWikiIngestPendingOp`.
    - **Env and deployment:** `.env.example` `TZ`, `WEKNORA_LANGUAGE`, `DEFAULT_LOCALE` comments; `docker-compose.yml::services.app.volumes`.
    - **Frontend:** `frontend/src/i18n/index.ts`, `resolveDefaultLocale.ts::SUPPORTED_LOCALES`, `BUILT_IN_DEFAULT`, `localeKeyAudit.ts::LOCALE_BUNDLES`, `embed.ts::SUPPORTED_LOCALES`; `frontend/src/App.vue` TDesign imports; `frontend/src/utils/request.ts` `Accept-Language`; `frontend/docker-entrypoint.sh` locale filter.
    - **Backend labels:** `internal/agent/act.go::toolDisplayNames`, `formatToolHint`; `internal/im/tool_display.go::imToolNameLabels`; Han-literal count from a grep over non-test `internal/**/*.go`.
    - **Prompts:** `config/prompt_templates/*.yaml` `{{language}}` and Han-script grep; `rewrite.yaml` templates `default_rewrite`, `standard_rewrite`, `strict_rewrite`; `internal/config/config.go::loadPromptTemplates`, `LocalizeTemplates`; `internal/types/custom_agent.go` `RewritePromptSystem`.
    - **Ingestion:** `internal/infrastructure/docparser/builtin_converter.go::SimpleFormatReader.Read`; `docreader/utils/endecode.py::decode_bytes`; NFC grep over `internal/` and `docreader/`.
    - **Chunking:** `internal/infrastructure/chunker/tokens.go::DetectLanguage`, `charsPerToken`, `CharsForTokenLimit`; `patterns.go` chapter, all-caps, footer and sentence patterns; `strategy.go::ensureDefaults`; `splitter.go` defaults; `internal/types/knowledgebase.go::ChunkingConfig`, `VLMConfig.DescriptionLanguage`, `ASRConfig.Language`.
    - **Parsers and VLM:** `internal/infrastructure/docparser/paddleocr_vl_converter.go::paddleOCRVLRecognitionParams`, `callLayoutParsing`; `mineru_converter.go`, `mineru_cloud_converter.go` language default; `internal/application/service/image_multimodal.go::buildVLMCaptionPrompt`, `buildVLMOCRPrompt`.
    - **Keyword retrieval:** `migrations/versioned/000002_embeddings.up.sql` BM25 tokenizer; `internal/application/repository/retriever/postgres/repository.go::KeywordsRetrieve`; `milvus/analyzer.go::detectAnalyzerName`; `opensearch/mapping.go` content analyzer; `elasticsearch/v8/repository.go` index creation; `qdrant/repository.go::tokenizeQuery` and text index; `sqlite/repository.go::initFTS5`.
    - **Expansion and dedup:** `internal/application/service/chat_pipeline/query_expansion.go::expandQueries`, `stopwords`, `questionWords`, `splitByDelimiters`; `internal/searchutil/textutil.go::TokenizeSimple`.
    - **Vector indexes and embedding:** HNSW in `000002` and `000059_embeddings_hnsw_1024.up.sql`; `internal/models/api/embeddings_settings.go::EmbeddingsCompat`; `internal/models/embedding/protocol.go::BatchEmbed`.
    - **Wiki and evaluation:** `000041_task_queue_and_wiki_indexes.up.sql` trigram index; `internal/application/repository/wiki_page.go` similarity query; `internal/application/service/metric/common.go::splitIntoWords`.
