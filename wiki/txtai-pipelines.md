---
type: Concept
title: txtai extraction and multimodal pipelines
description: Document conversion, configurable segmentation, tabular and modality pipelines, and their distinct file and model boundaries.
tags: [rag, txtai, ingestion, multimodal]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:18:00Z }
stale_after: 2027-01-24
sources:
  - id: txtai-repo
    resource: ../raw/txtai/README.md
    scope: ../raw/txtai/
    kind: code
    revision: 738aac498ccb
    title: txtai repository
---

**Observed:** `Textractor` extends `Segmentation` with file/URL retrieval, optional document-to-HTML conversion, and HTML-to-Markdown normalization. Chunking is a separate configurable step, not an always-on fixed token window. Image/audio pipelines add captions, labels, hashes, transcription, and stored objects; these are distinct from whatever modality support the selected embedding model provides.[^txtai-repo]

## Extraction flow and backend selection

`Textractor.text` classifies an input through `SafeOpen`, treats non-path inputs as data, retrieves local/remote content, optionally converts a file to HTML, then normalizes HTML to Markdown. A remote file used by the conversion path is downloaded to a temporary file and removed after successful processing. If conversion declines the file, text is read from that local file, not necessarily fetched over the network a second time.[^txtai-repo]

`FileToHTML(backend="available")` selects the first available **Tika → Docling → LiteParse** backend. Explicitly requested unavailable backends can raise `ImportError`; automatic selection with no available backend returns no conversion result. **Synthesis:** missing conversion support is not a guarantee of graceful binary-document extraction—downstream text reading still has to succeed. The legacy `tika=False` flag disables conversion rather than selecting another backend.[^txtai-repo]

- Tika requires its Python module and a runnable Java command (`TIKA_JAVA`); plain text/HTML can bypass conversion.
- Docling exports HTML and normalizes body/list/paragraph markup; HTML input can bypass conversion.
- LiteParse converts its Markdown output into page-wrapped HTML. `HTMLToMarkdown` removes script/style content and normalizes structural markup. Page-wrapper conventions can become form-feed section separators when section splitting is enabled; they are not a universal page-provenance schema.[^txtai-repo]

## Chunking contract

**Observed:** splitting precedence is **third-party chunker → sentences → lines → paragraphs → sections → passthrough**. Every splitter is off by default; cleaning is on. `join=True` rejoins split output. `minlength` can remove short elements when cleaning is enabled; it is a character-length gate, not a tokenizer budget. `tuples=True` retains input/output association.[^txtai-repo]

Sentence splitting requires NLTK; configured third-party chunking requires Chonkie. A name such as `semantic` resolves to `SemanticChunker` with forwarded keyword arguments. Section splitting uses form feeds when present, otherwise three-or-more newlines. **Limit:** parser output fidelity and chunk quality were not measured; these modes do not establish semantic or page-citation correctness.[^txtai-repo]

## Other pipeline families

| Surface | Observed mechanism / constraint |
| --- | --- |
| Tabular | CSV/dict/list-of-dicts to identified text rows; selected columns join into text, with optional structured content |
| Image captioning | Path or PIL image → image processor/model → generated text; default maximum new tokens is 256 |
| Objects | Object detection or classification with a configurable threshold |
| Image hashing | Perceptual/hash comparison, explicitly different from concept-level semantic similarity |
| Image storage | `ImageEncoder` serializes PIL bytes; images lacking a format use PNG |
| Transcription | ASR pipeline with audio chunk/join handling; the rest of the audio toolkit was not exhaustively inspected |
| Pipeline factory | Lowercased class-name configuration resolves reusable callable pipelines |

Do not infer that images must be captioned before embeddings: caption/hash/storage pipelines and multimodal embedding adapters are separate capabilities. See [retrieval](txtai-retrieval.md) for inspected embedding modality handling.[^txtai-repo]

## Fetch and execution limits

**Observed:** library `safeopen` defaults are false; `Application` enables safe opening by default for configured extraction/URL pipelines. Safe opening constrains local paths and remote hosts; [security](txtai-security.md) explains the narrower protected and unprotected paths. Document backends, model loaders, and optional dependency behavior remain separate trust/compatibility boundaries.[^txtai-repo]

## Relationships

- **Feeds:** [Index persistence](txtai-persistence.md) and [RAG context](txtai-rag.md); splitting choices determine what text can be retrieved and post-hoc referenced.
- **Used by:** [Workflow tasks and agent tools](txtai-agents-workflows.md), whose defaults are not always the Application defaults.
- **Part of:** [txtai](txtai.md); see the [source map](txtai-source-map.md) for pending parser, audio, training, examples, and runtime coverage.

[^txtai-repo]: Revision `738aac498ccb`: `src/python/txtai/pipeline/data/textractor.py::Textractor.__init__, text, download`; `pipeline/data/filetohtml.py::FileToHTML.__init__, __call__, Tika.available, Tika.__call__, Docling.__call__, Docling.normalize, LiteParse.__call__`; `pipeline/data/segmentation.py::Segmentation.__init__, parse, clean, createchunker`; `pipeline/data/htmltomd.py::HTMLToMarkdown.__call__, process`; `pipeline/data/tabular.py::Tabular`; `pipeline/image/caption.py::Caption.__init__, __call__`; `pipeline/image/objects.py::Objects`; `pipeline/image/imagehash.py::ImageHash` docstring; `pipeline/audio/transcription.py::Transcription`; `database/encoder/image.py::ImageEncoder`; `pipeline/factory.py::PipelineFactory`; `app/base.py::Application.createpipelines, function`; `docs/pipeline/data/textractor.md`, `docs/pipeline/data/segmentation.md`; sampled declarations in `test/python/testpipeline/testdata/testtextractor.py`, `testsegmentation.py`, `testfiletohtml.py`, and `testurlretrieve.py` (all under that test directory), not executed. Short module paths are relative to `src/python/txtai/`.
