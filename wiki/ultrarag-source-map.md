---
type: SourceMap
title: UltraRAG repository coverage and evidence ledger
description: Snapshot identity, inspected and excluded artifact families, compilation destinations, and outstanding runtime and coverage limits.
tags: [ml, ultrarag, source-map]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:55:24Z }
stale_after: 2027-01-26
sources:
  - id: ultrarag
    resource: ../raw/UltraRAG/README.md
    scope: ../raw/UltraRAG/
    kind: code
    revision: 185e203
    title: UltraRAG repository
---

UltraRAG was compiled through three Explore subagents covering orchestration, feature servers, and UI/deployment/security, with curator reconciliation, selected direct checks, and an additional read-only semantic reviewer. Review corrections distinguish demo streaming from normal MCP generation, file parameter replacement from runtime overrides, fractional `stringem` scoring, and configured versus fallback chunk overlap. **Observed:** the source checkout is at commit `185e203`, package version `0.3.0.2`, with 426 non-`.git` files. The synthesis is static, not a verified running installation. This ledger stays **draft** because material helper/page/template bodies remain selectively inspected and external runtime assets were unavailable.[^ultrarag]

## Identity and repeat-ingest key

- Canonical entry: [repository README](../raw/UltraRAG/README.md); scope: `raw/UltraRAG/`.
- Source identity: normalized `raw/UltraRAG/` plus the full revision above. Supporting files belong to this package, not separate sources.
- Upstream identified by README: `https://github.com/OpenBMB/UltraRAG`; authors/collaborators: THUNLP, NEUIR, OpenBMB, AI9stars; Apache-2.0 license.
- Commit date observed through Git: `2026-10-13T17:00:37+08:00`; capture/inspection date: 2026-10-26. Code/configuration is chiefly Python, YAML, TypeScript/TSX, Jinja, and English/Chinese documentation.
- Snapshot fingerprint: `1195fbafd2d2daa335174119c0c66dfd26399b9e111bd5ab9c904ea3301836cb`. Computed over sorted non-`.git` file paths: update SHA-256 with UTF-8 relative path, NUL, then binary SHA-256 of each file's bytes. This detects local supporting-artifact changes beyond the Git revision.
- No prior concepts cited this identity: the initial wiki had zero concepts, valid index/log, and the structural check passed. A repeat ingest must reconcile remaining coverage below; it is not automatically complete merely because all top-level directories are represented.[^ultrarag]

## Coverage status vocabulary

**Inspected** means read statically for the cited claims, not independently verified. **Sampled** means structure/signatures and selected consequential regions were read; unreviewed bodies remain a coverage limit. **Excluded** names the reason a discovered artifact was not compiled. No project code was imported or executed, and no raw file was modified. Nested `.git` objects are excluded as repository mechanics; Git revision/status metadata was inspected.[^ultrarag]

## Complete package inventory by family

Counts below partition the 426 files. Patterns refer to the inspected snapshot only; they do not silently grant coverage to future files.[^ultrarag]

| Family | Files | Coverage and disposition |
| --- | ---: | --- |
| Root files | 12 | `README.md`, `pyproject.toml`, `Dockerfile`, `Dockerfile.base-cpu`, `Dockerfile.base-gpu`, `.dockerignore`, `.gitignore`, `.env.dev`, `AGENTS.md`, `CLAUDE.md` inspected; `LICENSE.txt` license identified, legal boilerplate not synthesized; `uv.lock` excluded from deep dependency audit as generated resolution output. Source-local agent instructions treated as evidence, not governing instructions. |
| `src/ultrarag/*.py` | 8 | `client.py`, `server.py`, `api.py`, `cli.py`, `mcp_logging.py`, `mcp_exceptions.py`, `utils.py`, `__init__.py`: architecture/registration/API/launch paths inspected; large `client.py` selectively covered, not every execution branch. Cosmetic CLI rendering and unused helpers excluded from standalone concepts. |
| `servers/**` | 36 | See server ledger below; all server parameter files inspected. Router has no parameter file. |
| `examples/**/*.yaml` | 78 | Server/step graphs and configuration shapes inspected across the collection; representative RAG, loop/branch, hybrid, reasoning, multimodal, evaluation, and demo configs read in detail. Generated `parameter/` and `server/` companions are supporting metadata snapshots, not separate source identities. Repetitive parameter/tool listings excluded from prose. |
| `prompt/*.jinja` | 55 | All inventoried and reference relationships checked; eight bodies specifically reviewed: `qa_rag_boxed`, `qa_rag_citation`, `IRCoT`, `surveycpm_write`, `webnote_init_page`, `webnote_fill_page`, `search_r1_append`, `search_o1_reasoning`; `qa_boxed` also read by architecture exploration. Remaining bodies sampled by family/structure, not fully synthesized. |
| `docs/*` | 13 | `llms.txt` packed documentation sampled/reconciled for setup, DSL, API, UI; `debug_rag_workflows_zh.md`, `frontend_mobile_chat_baseline.md`, `CONTRIBUTING.md`, `SECURITY.md` inspected or sampled for relevant claims; `README_zh.md` treated as translated/redundant overview; `CODE_OF_CONDUCT.md` excluded as governance boilerplate. `architecture.png` visually inspected; `chat_menu.png` not inspected visually, UI claims grounded in code instead. QR PNGs and logo SVGs excluded as decorative/contact assets. |
| `script/*` | 7 | `api_usage_example.py`, `case_study.py`, `deploy_retriever_server.py`, `deploy_retriever_config.json`, `vllm_serve.sh`, `vllm_serve_emb.sh`, `vllm_serve_vlm.sh` inspected. No launches performed. |
| `tests/**/*.py` | 7 | All statically inspected: two client-launch/remote-config tests; FAISS padding, Serply web search, query extraction, normalization, and key-map alignment regressions. Not executed. |
| `.github/**` | 7 | Two workflows and `dependabot.yml` inspected; `SECURITY.md` policy and three issue templates inspected at policy/title level, excluded from product-feature synthesis. |
| `data/*.jsonl` | 2 | `sample_nq_10.jsonl`, `corpus_example.jsonl` inspected for schema; sample content excluded as illustrative rather than reusable personal knowledge or benchmark results. |
| `ui/**` | 201 | See UI ledger below; generated bundles, vendored styles, and fonts excluded from semantic compilation. |

## Server closure

| Paths under `servers/` | Coverage |
| --- | --- |
| `retriever/parameter.yaml`; `retriever/src/{retriever,bm25_tokenizer}.py`; `retriever/src/index_backends/{__init__,base,faiss_backend,milvus_backend,qdrant_backend}.py`; `retriever/src/websearch_backends/{__init__,base,exa_backend,tavily_backend,zhipuai_backend,serply_backend}.py`; `retriever/tests/test_litellm_embedding.py` | Feature/index/provider contracts and major bodies inspected; embedding test read, not run. External library/service behavior remains unverified. |
| `generation/parameter.yaml`; `generation/src/{generation,local_generation}.py`; `generation/tests/test_litellm_backend.py` | All backend branches, retry paths, image conversion and separate UI streaming helper inspected; test read only. |
| `reranker/parameter.yaml`; `reranker/src/reranker.py` | Backend dispatch, input checks, and score-dropping output contract inspected. |
| `corpus/parameter.yaml`; `corpus/src/corpus.py` | All five tools and output schemas inspected; Office-conversion and normalization helper internals sampled. |
| `prompt/parameter.yaml`; `prompt/src/prompt.py` | Template path/rendering and family registrations inspected; task-note formatter helpers sampled. |
| `custom/parameter.yaml`; `custom/src/custom.py` | Extraction, citations, SurveyCPM states/action constraints/bounds inspected; position/task-note formatting helpers sampled. |
| `benchmark/parameter.yaml`; `benchmark/src/benchmark.py` | Loading, mapping, dropped-row alignment, shuffle/limit semantics inspected. |
| `evaluation/parameter.yaml`; `evaluation/src/evaluation.py` | Normalization, QA metrics, TREC and p-value paths inspected; no scores computed. |
| `memory/parameter.yaml`; `memory/src/memory.py` | Filesystem root/user validation/template/save semantics inspected. |
| `sayhello/parameter.yaml`; `sayhello/src/sayhello.py`; `router/src/router.py` | Greeting and router wrapped-record/state contracts inspected. |

All 36 server-family files are accounted for by these rows. Imports into third-party packages are external dependencies described by manifests, not vendored source audited here.[^ultrarag]

## UI closure (201 files)

| Paths | Files | Coverage |
| --- | ---: | --- |
| `ui/__init__.py`; `ui/backend/*.py` | 8 | Empty initializers accounted for; `app.py`, `auth.py`, `chat_store.py`, `kb_visibility_store.py`, `storage_paths.py` inspected; large `pipeline_manager.py` sampled at execution, parameter, KB, and storage boundaries. |
| `ui/frontend/src/**` | 46 | Routing/providers, API modules, hooks, canvas/auth/shared UI components, markdown rendering and utility surfaces inspected or sampled; `ChatPage.tsx`, `BuilderPage.tsx`, CSS and low-level presentation helpers selectively inspected. No complete UI/HTML-sink audit. |
| `ui/frontend/{.gitignore,README.md,eslint.config.js,index.html,package-lock.json,package.json,tsconfig.app.json,tsconfig.json,tsconfig.node.json,vite.config.ts}` | 10 | Manifest/build/proxy/conventions inspected; lockfile inventoried as generated, not dependency-audited. |
| `ui/frontend/public/theme/**` | 35 | Includes 26 font binaries, four vendor CSS files, logos/icons, locale JS, and theme CSS. Fonts/vendor assets excluded; first-party locale/theme structure sampled, cosmetic content not synthesized. |
| `ui/frontend/public/{favicon,vite}.svg` | 2 | Excluded decorative icons. |
| `ui/frontend/dist/**` | 99 | Excluded generated frontend output and duplicated theme/font/vendor artifacts; HTML head sampled only. No assertion that committed build matches source. |
| `ui/storage/ext/.gitkeep` | 1 | Excluded empty directory placeholder; no runtime user storage was supplied. |

## External and unavailable evidence

- Dependencies in `uv.lock` and `package-lock.json` were not installed or vulnerability-audited; constraints and CI definitions are observed, successful resolution/build is not.
- Hugging Face/model-provider weights, CUDA runtime/driver availability, vector databases, API accounts, linked external blogs/papers/videos, and full benchmark corpora were not fetched. Local model paths and service URLs in configs are deployment assumptions, not confirmed reachable assets.
- No browser, UI screenshot equivalence, document conversion, OCR, index build, model call, benchmark, concurrency test, or security exploit was run.
- The architecture image's component/control-flow drawing agrees at overview level with the code. Its score chart lacks a reproducible protocol in the image; numeric results were deliberately not promoted to measured wiki knowledge.
- The unreviewed UI/template/formatting bodies and protocol-specific provider failure behavior remain follow-up work. No unusable local text file blocked this ingestion; excluded binary/generated assets are not represented as fully inspected.[^ultrarag]

## Actual checks and trust

1. Initial structural check: valid empty wiki, zero concepts, one index.
2. Source safety screen: no likely live secret in inspected first-party text; empty environment template and placeholder config keys. Generated CSS/JS pattern hits are not treated as proof of credentials; bundles/fonts were excluded from deep inspection. Fixed development auth defaults are documented without copying values.
3. Standard-library `ast.parse` over all 52 `.py` files: zero syntax errors, no imports or source execution.
4. Git showed no source working-tree modifications before compilation. After compilation, all 426 non-`.git` files matched the pre-ingest SHA-256 fingerprint, and source Git status remained clean.
5. Post-compilation `python3 tools/wiki_check.py` passed. Direct checks parsed all 12 UltraRAG frontmatters, confirmed exact index-title/description matches, resolvable source resource/scope paths, pinned revision, citation joins, and exactly one UltraRAG ingest log entry. A bounded credential-shape screen found no matches in the 12 compiled pages; this is not a comprehensive privacy audit. Concurrent non-UltraRAG wiki changes were preserved.

These check results are session-local observations, not verification of model quality or repository test success. `verified` metadata is intentionally omitted.[^ultrarag]

## Compilation destinations and idempotency

- [Architecture/feature map](ultrarag.md)
- [Pipeline DSL](ultrarag-pipelines.md)
- [Retrieval/reranking](ultrarag-retrieval.md)
- [Generation](ultrarag-generation.md)
- [Corpus processing](ultrarag-corpus.md)
- [Research prompts and memory](ultrarag-research-workflows.md)
- [Benchmark/evaluation](ultrarag-evaluation.md)
- [UI/persistence](ultrarag-ui.md)
- [Authentication/ACLs](ultrarag-auth.md)
- [Deployment/CI](ultrarag-deployment.md)
- [Security](ultrarag-security.md)

**Synthesis:** these boundaries answer distinct retrieval questions without making each script/config its own concept. Boilerplate, cosmetics, sample narrative content, repetitive configs, and unverified marketing/benchmark performance are excluded. No existing concept was superseded and no new domain was required (`ml` already covers the package). Doc/code discrepancies are retained on the affected concept rather than resolved by silently trusting prose. Repeat ingestion should change only newly inspected, changed, or newly connected knowledge and preserve this package identity.[^ultrarag]

[^ultrarag]: Local revision `185e203`: `README.md` About/Installation/UI; `pyproject.toml`; `LICENSE.txt`; path inventories for every family above; `docs/architecture.png` panels; declared code symbols and configuration keys are located in the linked concept footnotes. Session inspection: Git `rev-parse`, `show -s`, `status --short`; `Path('raw/UltraRAG').rglob('*')` inventory/hash excluding `.git`; credential-pattern scan of first-party text; AST-only parse of all 52 Python files; initial `python3 tools/wiki_check.py` output `OK: 0 concept(s), 1 index file(s)`. Three read-only Explore reports supplied detailed static coverage; a fourth Explore review checked generation/demo overrides, parameter precedence, corpus settings, evaluation, and auth gates. Neither agent reports nor CI definitions are runtime verification.
