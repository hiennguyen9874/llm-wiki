---
type: Concept
title: Triton Speculative Decoding with vLLM Backend
description: Serve EAGLE and draft-model speculative decoding in Triton via the vLLM backend with model-repository setup, Docker serving, generate requests, and GenAI-Perf evaluation.
tags: [triton, vllm, speculative-decoding, eagle]
status: stable
created: 2026-09-16
generated: { by: llm-wiki-agent/1, at: 2026-09-16T05:18:09Z }
sources:
  - id: triton-spec-decode-vllm
    resource: ../raw/Speculative_Decoding/index.md
    title: Speculative Decoding with vLLM — NVIDIA Triton Inference Server
---

Triton Inference Server serves vLLM speculative decoding on a single node with one GPU through a vLLM-backend model repository, with the source demonstrating EAGLE in detail and a draft-model variant by swapping the repository entry[^triton-spec-decode-vllm].

## Scope

This covers only the vLLM-backend path; the source points to a parent Speculative Decoding page for other supported Triton backends, which was not compiled here[^triton-spec-decode-vllm]. The source cites Spec-Bench as ranking EAGLE the current top-performing speedup approach across tasks, and points to vLLM's speculative-decoding blog and feature docs for backend internals[^triton-spec-decode-vllm].

## EAGLE mechanism in the source

EAGLE predicts future tokens from contextual features extracted from the target LLM's second-top layer: a lightweight auto-regression head predicts the next feature vector, which the frozen LLM classification head turns into tokens, reported at 2x–3x over vanilla decoding while preserving output quality and distribution consistency[^triton-spec-decode-vllm].

## Models and EAGLE conversion rule

The worked example pairs `yuhuili/EAGLE-LLaMA3-Instruct-8B` with base `meta-llama/Meta-Llama-3-8B-Instruct`, with more EAGLE checkpoints under the `yuhuili` Hugging Face account; both are fetched with `git-lfs` clones, and Llama 3 downloads require Hugging Face access approval plus login[^triton-spec-decode-vllm].

EAGLE checkpoints load directly in vLLM after vLLM PR 12304; on older vLLM use the linked conversion script and point `speculative_model` at the converted path[^triton-spec-decode-vllm]. For Triton specifically: container version `<= 25.02` requires running that conversion script inside the folder containing both models, while container `>= 25.03` uses vLLM `>= 0.7.3` which already contains the PR[^triton-spec-decode-vllm].

## Model repository and serving

A Triton model repository carries each model plus its metadata (configurations, version files); the source provides an EAGLE plus base template under `model_repository` to copy and edit, setting `num_speculative_tokens` to 5 for `eagle_model` following the vLLM example, with other values allowed at possible performance cost[^triton-spec-decode-vllm].

Serve by mounting the downloaded models to `/hf-models` and the repository to `/model_repository`, using the `-vllm-python-py3` container (source recommends the latest tag from the NGC catalog)[^triton-spec-decode-vllm]:

```bash
docker run --gpus all -it --net=host --rm -p 8001:8001 --shm-size=1G \
    --ulimit memlock=-1 --ulimit stack=67108864 \
    -v </path/to/model_repository>:/model_repository \
    -v </path/to/eagle/and/base/model>:/hf-models \
    nvcr.io/nvidia/tritonserver:<xx.yy>-vllm-python-py3 \
    tritonserver --model-repository /model_repository \
    --model-control-mode explicit --load-model eagle_model
```

## Inference request

Send generation to the `generate` endpoint with explicit model selection; streaming off and temperature zero in the example[^triton-spec-decode-vllm]:

```bash
curl -X POST localhost:8000/v2/models/eagle_model/generate -d '{"text_input": "What is Triton Inference Server?", "parameters": {"stream": false, "temperature": 0}}' | jq
```

The source's expected reply identifies `model_name: eagle_model`, `model_version: "1"`, and a `text_output` beginning with a Triton Inference Server description[^triton-spec-decode-vllm].

## Evaluation with GenAI-Perf

GenAI-Perf measures generative-AI throughput and latency through the inference server[^triton-spec-decode-vllm]. The source procedure is:

1. Prepare HumanEval questions from the EAGLE repo (`eagle/data/humaneval/question.jsonl`), converted for GenAI-Perf with the sibling `dataset-converter.py`; other convertible datasets are allowed, but MT-bench is excluded because GenAI-Perf does not yet support multiturn input[^triton-spec-decode-vllm].
2. Install with `pip install genai-perf` on Ubuntu 24.04 with Python 3.10+ and preinstalled CUDA 12[^triton-spec-decode-vllm].
3. Profile with concurrency 1 against the Triton gRPC port, passing the converted input file, base-model tokenizer path, and export file[^triton-spec-decode-vllm]:

```bash
genai-perf \
  profile \
  -m ensemble \
  --service-kind triton \
  --backend tensorrtllm \
  --input-file /path/to/converted/dataset/converted_humaneval.jsonl \
  --tokenizer /path/to/hf-models/Meta-Llama-3-8B-Instruct/ \
  --profile-export-file my_profile_export.json \
  --url localhost:8001 \
  --concurrency 1
```

Benchmark speculative decoding against the base model at `--concurrency 1`: the source argues this avoids saturating hardware with multiple requests, since the technique trades extra computation for lower single-request token latency, so low concurrency reflects real-world latency gains[^triton-spec-decode-vllm]. The source's sample table (single node, one RTX 5880 48GB) is reference-only and hardware-dependent[^triton-spec-decode-vllm].

To serve the baseline, relaunch with `--load-model base_model` instead of `eagle_model` and rerun the same GenAI-Perf command[^triton-spec-decode-vllm].

## vLLM-side EAGLE speedup caveat

The source relays a vLLM documentation warning: EAGLE-based speculators in vLLM currently show lower speedup than the EAGLE reference implementation, under investigation in `vllm-project/vllm#9565`; use EAGLE with care[^triton-spec-decode-vllm].

## Draft-model variant

Draft-model speculative decoding is the earlier alternative: a smaller faster LLM drafts multiple tokens ahead in a chain-like draft-and-verify structure, versus EAGLE's feature-level extrapolation with tree-based attention; the source characterizes it as generally slower, harder to implement well for smaller targets because it needs a separate draft model, and variable in draft accuracy versus EAGLE's reported ~0.8[^triton-spec-decode-vllm].

Triton execution mirrors the EAGLE steps except for the repository: copy and edit the `model_repository/opt_model` template following the vLLM draft-model example, then serve it explicitly (source pins `26.08-vllm-python-py3` in this command)[^triton-spec-decode-vllm]:

```bash
docker run --gpus all -it --net=host --rm -p 8001:8001 --shm-size=1G \
    --ulimit memlock=-1 --ulimit stack=67108864 \
    -v </path/to/model_repository>:/model_repository \
    nvcr.io/nvidia/tritonserver:26.08-vllm-python-py3 \
    tritonserver --model-repository /model_repository \
    --model-control-mode explicit --load-model opt_model
```

## Relationships

- Uses [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — EAGLE/Eagle3 draft-target mechanism, `speculative_config` shape, and conversion guidance behind the Triton `eagle_model` repository entry.
- Uses [vLLM Draft-Model Speculative Decoding](vllm-draft-model.md) — separate-draft configuration behind the Triton `opt_model` repository variant.
- Related to [Speculative Decoding Foundations](speculative-decoding-foundations.md) — draft-verify-accept proof and speedup math underlying both the EAGLE and draft-model Triton paths.
- Related to [Speculative Decoding Workload Fit and Tuning](speculative-decoding-practice-guide.md) — concurrency-1 benchmarking rationale and K-tuning context for the GenAI-Perf comparison and `num_speculative_tokens` setting above.

## Coverage limits

- Parent Speculative Decoding page covering non-vLLM Triton backends, linked vLLM blog and feature docs, EAGLE paper/GitHub/blog, Hugging Face model pages, conversion-script gist, vLLM PR 12304 and issue 9565, model-repository templates, NGC catalog tags, generate-endpoint protocol page, and GenAI-Perf docs were not inspected beyond this source's description.
- `dataset-converter.py` and the converted HumanEval files were not present in `raw/` and were not inspected, so conversion details are not compiled here.
- Sample GenAI-Perf latency/throughput numbers are source-reported on one RTX 5880 and are not independently verified.

[^triton-spec-decode-vllm]: Speculative Decoding with vLLM — NVIDIA Triton Inference Server — `../raw/Speculative_Decoding/index.md` (docs.nvidia.com), covering single-node single-GPU vLLM-backend scope, Spec-Bench EAGLE ranking, EAGLE feature-level mechanism with 2x–3x claim, EAGLE-LLaMA3 plus Llama-3-8B model pair with git-lfs fetch and HF access note, PR-12304 / Triton 25.02 vs 25.03 conversion rule, model-repository template with `num_speculative_tokens: 5`, Docker serve with explicit model load, generate-endpoint curl plus sample reply, GenAI-Perf HumanEval preparation with MT-bench exclusion, install prerequisites, concurrency-1 profile command and rationale, base-model comparison via `--load-model` switch, vLLM EAGLE speedup caveat with issue 9565, and draft-model versus EAGLE differences with `opt_model` repository and serve command.
