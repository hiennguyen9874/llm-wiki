# Images on eva01

Both existing localhost listeners accept `image_data` on `POST /v1/systemone`
(and the existing Decisions aliases): 31000 for 4B v5, 31001 for 0.8B v6.
The engine remains the pinned SGLang V100 fork with the existing OpenJev head.

```python
import base64, requests
image = base64.b64encode(open("photo.png", "rb").read()).decode()
r = requests.post("http://localhost:31000/v1/systemone", json={
    "model": "openjev/qwen3.5-4b-nli-v5",
    "state": "An image: <<IMG>>",
    "image_data": image,
    "questions": {"decision": {
        "type": "choice", "instructions": "Is the parcel visibly damaged?",
        "criteria": {"A": "yes", "B": "no"}
    }}
}, timeout=180)
r.raise_for_status()
print(r.json()["answers"])
```

One image per request, shared by all questions/options. JPEG/PNG/WebP, base64
or an image data URI; 4 MiB decoded, 12 million pixels, 8 MiB total request.
URLs and server file paths are not accepted. `<<IMG>>` is optional (appended
when absent). The gateway sends actual pixels separately to SGLang, not an
image caption. Image options are dispatched in batches of at most four and
bounded by encoded size. Text request batching is unchanged.

For each option `e_i = softmax([contradiction, entailment, neutral])_entailment`.
The API forecasts `p_i = e_i / sum(e)` over mutually exclusive answer options;
all-zero scores fall back to a uniform distribution. It declares
`probability_method: normalized_entailment_v1`. This is an explicit categorical
forecast, not a claim of empirically calibrated confidence. No temperature or
other parameters were fitted on these benchmark examples. Text-only decisions
already used this normalization. The API's `confidence` field is normalized
entropy; ECE is computed from the top categorical probability, not that field.

## Image JevBench integration

`patches/jevbench-image-adapter.patch` adds `--adapter openjev_image` to
fstandhartinger/jevbench at `fd54ea7dc02bbe29c6ac8f6e015a54cdcff26805`.
The patched checkout on eva01 is `data/jevbench_image_20260928`. It uses the
unchanged runner, ledger, schema checks, Brier and ECE metrics. Probabilities
are labelled `normalized_entailment_v1`, not silently relabelled as calibrated.
The task state is `{text: "An image: <<IMG>>", image_data: "<base64>"}` so
the existing dataset hash covers the image bytes. Gold stays in `expected`.

Example from the eva01 runtime directory:

```sh
PYTHONPATH=data/jevbench_image_20260928 venv/bin/python -m jevbench.cli run \
  --tasks tmp/image-jev-tasks.jsonl --adapter openjev_image \
  --endpoint http://localhost:31000 --model openjev/qwen3.5-4b-nli-v5 \
  --key-env '' --reserve-usd 0 --delay-s 0 \
  --cost-basis self_hosted_compute_cost_not_measured \
  --results results/my-image-run/results.jsonl \
  --ledger results/my-image-run/ledger.jsonl \
  --raw-dir results/my-image-run/raw --manifest results/my-image-run/manifest.json
```

`image_jevbench.py` also provides a standalone bridge for the published example
schema (`question`, `options`, `image`, `correctLabel`). It does not send
`correctLabel`, `alt`, titles or source descriptions to the model.

The public website repository only supplies eight resized example images and
their questions. This integration was run on those eight, not the full 228
public / 456 sealed benchmark. Neither the private Image JevBench evaluator nor
the upstream leaderboard was modified. Acceptance/re-evaluation on that board
requires its maintainer to run the updated model interface.

## Operations

The existing systemd restart/watchdog/socket activation configuration remains.
`OPENJEV_VISION_WARMUP=1` warms vision at two resolutions with batches 1 and 4
before the worker supervisor announces readiness. Existing workers were also
warmed before gateway rollout. `OPENJEV_READY_DIR` on the gateways gates routing
on per-port markers written after warmup; workers remove them on startup/exit.
New token lengths can still trigger V100 JIT;
image cold latency can be several seconds, so warm numbers are not cold SLAs.
Worker watchdog probes still verify real text classification; startup additionally
checks finite image logits. A single 0.8B backend still has downtime while restarting.

Before rollout, previous gateway/supervisor scripts and worker units were saved
on eva01 under `app/backups/pre-image-20260928/`. Restore those files and restart
the gateways to revert the API; worker unit changes take effect at next restart.
