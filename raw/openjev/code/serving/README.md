# OpenJev image Decisions gateway

This update adds image transport to the existing SGLang Decisions gateway.
The checkpoint and SGLang classification head are unchanged. The public model
tested here is `AlexWortega/openjev`, subfolder `qwen3.5-4b-nli-v5`.

## Setup

Use a working SGLang installation with the external `sglang_openjev` package
next to these scripts. Our tested V100 runtime is
`haohervchb/sglang-V100@dca488908ee4e3f1bc676c3bf5dcd26ff049cfc3`,
FP16, PyTorch 2.9.1 cu126. See [V100.md](V100.md) for runtime preparation and
the required dynamic-paged patch. This directory is not an automatic installer
for an unconfigured GPU host.

Download the model weights and prepare the missing processor configurations:

```python
from huggingface_hub import snapshot_download
snapshot_download(
    "AlexWortega/openjev", revision="a298f274886c4676c42f1a4262401b6aa9653e6d",
    allow_patterns=["qwen3.5-4b-nli-v5/*"], local_dir="openjev_weights",
)
```

```sh
python prepare_v100_model.py openjev_weights/qwen3.5-4b-nli-v5 model-overlay
# On the configured V100 runtime described in V100.md:
bash serve_sglang_v100.sh "$PWD/model-overlay" 30000
# In a second shell, from this directory, using the serving Python environment:
SGLANG_URL=http://127.0.0.1:30000 SERVED_MODEL=openjev/qwen3.5-4b-nli-v5 \
  python -m uvicorn decisions_server:app --host 127.0.0.1 --port 31000
```

The gateway additionally imports FastAPI, httpx, NumPy and Pillow. Wait for
the SGLang process to finish loading before sending requests.

## Request

```python
import base64, requests
with open("photo.png", "rb") as f:
    image = base64.b64encode(f.read()).decode()
response = requests.post("http://localhost:31000/v1/systemone", json={
    "model": "openjev/qwen3.5-4b-nli-v5",
    "state": "An image: <<IMG>>",
    "image_data": image,
    "questions": {"decision": {
        "type": "choice", "instructions": "Is the parcel visibly damaged?",
        "criteria": {"A": "yes", "B": "no"}
    }}
}, timeout=180)
response.raise_for_status()
print(response.json()["answers"]["decision"]["probabilities"])
```

`image_data` accepts a single base64 image or image data URI; JPEG, PNG or
WebP; at most 4 MiB decoded and 12 million pixels. It never fetches a URL or
reads a server file path. All questions/options share the image. The gateway
sends the pixels to the vision tower, without an auxiliary captioning model.

## Probabilities and benchmark adapter

For each option, `e_i` is the NLI softmax probability of entailment. Return
`p_i = e_i / sum(e)`, or uniform when all `e_i` are zero. The API declares
`probability_method: normalized_entailment_v1`. This is an option distribution;
its calibration must be measured. No temperature was fitted on benchmark data.
The separate `confidence` field is entropy-based, not the top probability used
for ECE.

Apply [the adapter patch](patches/jevbench-image-adapter.patch) to
`fstandhartinger/jevbench@fd54ea7dc02bbe29c6ac8f6e015a54cdcff26805` with
`git apply`. It adds `--adapter openjev_image` to the existing CLI. Canonical
tasks use `state: {"text": "An image: <<IMG>>", "image_data": "<base64>"}`;
the ordinary task question, labels and expected answer fields are unchanged.
Image bytes are therefore covered by the existing dataset hash. Scoring is
unchanged, and the probability source is explicitly recorded.

`image_jevbench.py` is a separate example runner for the website's public
example schema. Neither path sends gold labels or descriptive alt text.
See [the smoke results](../../results/image_jevbench_examples_20260928/README.md).

First-use V100 compilation can take tens of seconds. `warmup_vision.py` primes
common sizes. The included supervisor/HA code gates routing on completion of
startup warmup; these operations are described in [IMAGE-SERVING.md](IMAGE-SERVING.md).
