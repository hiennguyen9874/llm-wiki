---
library_name: transformers
license: openrail
license_link: LICENSE
tags:
  - pdf
  - extraction
  - structured-data
  - json
---

<p align="center">
  <img src="datalab-logo.png" alt="Datalab Logo" width="150"/>
</p>

# lift

lift is a structured extraction model from [Datalab](https://www.datalab.to) that pulls structured JSON out of PDFs and images. Pass any JSON schema and lift returns a JSON object matching it, using schema-constrained decoding to guarantee valid, well-typed output.

<p align="center">
  <img src="accuracy.png" alt="Extraction accuracy benchmark" width="720"/>
</p>

Try lift in the [free playground](https://www.datalab.to/playground), or use the [hosted API](https://www.datalab.to/) for higher accuracy, per-field verification, and citations.

## Features

- Extract structured data from documents
- Pass any JSON schema
- Handles multi-page documents in a single pass, including values that span pages
- Two inference modes: local (HuggingFace) and remote (vLLM server)
- CLI for single files, inline schemas, or whole directories
- Schema Studio: a Streamlit app to build, save, and test schemas against your documents

## Quickstart

```shell
pip install lift-pdf

# With vLLM (recommended, lightweight install)
lift_vllm
lift_extract input.pdf ./output --schema schema.json

# With HuggingFace (requires torch)
pip install lift-pdf[hf]
lift_extract input.pdf ./output --schema schema.json --method hf
```

A schema is standard JSON Schema. Keep it simple — `string`, `number`, `integer`, `boolean`, arrays of those, arrays of objects, and nested objects are all supported. Write a `description` for any field whose name isn't self-explanatory, and mark a field `required` only when it must appear; fields genuinely absent from a document come back `null`.

```json
{
  "type": "object",
  "properties": {
    "invoice_number": {"type": "string", "description": "Invoice identifier"},
    "total": {"type": "number", "description": "Total amount due"},
    "line_items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "description": {"type": "string"},
          "amount": {"type": "number"}
        }
      }
    }
  },
  "required": ["invoice_number", "total"]
}
```

## Usage

### With vLLM (recommended)

```python
from lift import extract
from lift.model import InferenceManager

# Start the vLLM server first with: lift_vllm
model = InferenceManager(method="vllm")
result = extract("document.pdf", "schema.json", model=model)
print(result.extraction)
```

### With HuggingFace Transformers

```python
from lift import extract
from lift.model import InferenceManager

# Loads datalab-to/lift in-process (requires: pip install lift-pdf[hf])
model = InferenceManager(method="hf")
result = extract("document.pdf", "schema.json", model=model)
print(result.extraction)
```

`extract` accepts the schema as a dict, a path to a `.json` file, an inline JSON string, or the name of a saved schema. Pass `page_range="0-5"` to limit PDF pages, and set `VLLM_API_BASE` to target a remote server.

## Benchmarks

Evaluated on a 225-document extraction benchmark (6–64 pages per document, ~11,000 scored fields) with adversarial cases planted throughout: cross-page values, exhaustive lists, fields that must be left null, near-miss distractors, multi-source aggregation. Scoring is deterministic exact-match against ground truth (numeric tolerance, normalized strings).

All models receive the same rendered page images, and extract each document in a single pass.

| Model | Size | Field accuracy | Full-document accuracy | Median latency* | Features |
|---|---|---|---|---|---|
| Datalab API | — | 95.9% | 44.4% | 30.8s | Citations + Verification |
| Gemini Flash 3.5 | — | 91.3% | 40.0% | 28.1s | |
| **lift** | 9B | **90.2%** | 20.9% | 9.5s | |
| Azure Content Understanding | — | 83.4% | 22.2% | 73.7s | |
| NuExtract3 | 4B | 81.5% | 8.4% | 8.3s | |
| Qwen3.5-9B | 9B | 76.3% | 24.0% | 16.8s | |

\* Per document, 8 concurrent requests. Local models (lift, Qwen3.5-9B, NuExtract3) served with vLLM on a single GPU; Gemini, Datalab, and Azure via API. Latency varies with hardware and load — treat as relative, not absolute.

<p align="center">
  <img src="latency.png" alt="Latency benchmark" width="720"/>
</p>

- **Field accuracy** — fraction of individual schema fields extracted correctly.
- **Full-document accuracy** — fraction of documents where *every* field is correct.

Hosted models with verification, citations, and confidence scores are available via the [Datalab API](https://www.datalab.to) — test in the [playground](https://www.datalab.to/playground).

## Commercial Usage

Code is Apache 2.0. Model weights use a modified OpenRAIL-M license: free for research, personal use, and startups under $5M funding/revenue. Cannot be used competitively with our API. For broader commercial licensing, see [pricing](https://www.datalab.to/pricing?utm_source=hf-lift).

## Credits

- [Huggingface Transformers](https://github.com/huggingface/transformers)
- [vLLM](https://github.com/vllm-project/vllm)
- [Qwen 3.5](https://github.com/QwenLM/Qwen3)
