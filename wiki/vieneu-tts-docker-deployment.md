---
type: Concept
title: VieNeu-TTS Docker Compose Deployment
description: The VieNeu-TTS `docker/docker-compose.yml` profiles — Web UI `cpu`/`gpu`, OpenAI-compatible API `api-gpu`/`api-cpu`, and the legacy v2 LMDeploy `serve` profile — with ports, GPU reservation, healthchecks, Hugging Face cache volume, and environment defaults.
tags: [tts, vietnamese, docker, deployment, api]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T15:34:00Z }
stale_after: 2027-10-07
sources:
  - id: vieneu-tts-docs
    resource: ../raw/vieneu-tts-docs/README.md
    scope: ../raw/vieneu-tts-docs/
    kind: documentation
    revision: 85344322b7258b4e25479b692e8e3396baf9db34
    title: VieNeu-TTS supporting docs (streaming guide and Docker Compose)
---

The captured `docker/docker-compose.yml` defines five services across four active profiles plus a legacy one: `cpu` and `gpu` run the Gradio Web UI on the ONNX/torch-free or CUDA/PyTorch build, `api-gpu` and `api-cpu` run the OpenAI-compatible speech server `apps/openai_speech.py` on port 8000 with a `/health` healthcheck and `restart: unless-stopped`, and `serve` keeps the deprecated v1/v2 LMDeploy API server on port 23333 (**Reported**).[^vieneu-tts-docs] All services share a named `huggingface_cache` volume for model downloads, and the two API services explicitly set `HOST=0.0.0.0` because the server otherwise binds loopback; the captured streaming guide pairs that exposure with `VIENEU_API_KEY` (**Reported**).[^vieneu-tts-docs]

## Profiles

| Profile | Service | Image/build | Command | Port | Purpose |
|---|---|---|---|---|---|
| `cpu` | `cpu` | `docker/Dockerfile.cpu` | `python apps/gradio_main.py` | `${PORT:-7860}` → 7860 | Web UI, v3 Turbo (ONNX) + v3 Nano, torch-free |
| `gpu` | `gpu` | `docker/Dockerfile.gpu` target `dev` | `python apps/gradio_main.py` | 7860 | Web UI, v3 Turbo on CUDA (PyTorch) + v3 Nano |
| `api-gpu` | `api-gpu` | `docker/Dockerfile.gpu` target `prod` | `python -m apps.openai_speech` | `${API_PORT:-8000}` → 8000 | OpenAI-compatible streaming API, 16 streams default |
| `api-cpu` | `api-cpu` | `docker/Dockerfile.cpu` | `python -m apps.openai_speech` | `${API_PORT:-8000}` → 8000 | OpenAI-compatible streaming API, 1–2 streams |
| `serve` (legacy) | `serve` | `docker/Dockerfile.serve` | `--model ${MODEL:-pnnbao-ump/VieNeu-TTS-v2}` … `--port 23333 --memory-util ${MEMORY_UTIL:-0.3}` | `${SERVE_PORT:-23333}` → 23333 | Deprecated v1/v2 LMDeploy server |

Launches: `docker compose -f docker/docker-compose.yml --profile api-gpu up` or `--profile api-cpu up` for the API, `--profile cpu`/`--profile gpu` for the Web UI (**Reported**).[^vieneu-tts-docs]

## Shared configuration

The `cpu`/`gpu` Web UI services extend a YAML anchor `x-base-config` that mounts `./:/workspace`, the named `huggingface_cache` at `/home/app/.cache/huggingface`, and `./output_audio:/workspace/output_audio`; it loads an optional `.env` (`required: false`) and sets `HF_HOME`, `PYTHONUNBUFFERED=1`, and the Gradio variables `PORT`/`GRADIO_SERVER_PORT` (7860), `GRADIO_SERVER_NAME=0.0.0.0`, and `GRADIO_SHARE=0`, with `stdin_open`/`tty` on (**Reported**).[^vieneu-tts-docs]

API profile environment (**Reported**).[^vieneu-tts-docs]

| Variable | `api-gpu` | `api-cpu` |
|---|---|---|
| `HOST` / `PORT` | `0.0.0.0` / 8000 | `0.0.0.0` / 8000 |
| `VIENEU_BACKEND` | (auto → PyTorch on CUDA) | `onnx` |
| `VIENEU_PRECISION` | — | `${VIENEU_PRECISION:-fp32}` (int8 ≈ 2x faster, needs VNNI) |
| `VIENEU_MAX_STREAMS` | `${VIENEU_MAX_STREAMS:-16}` | (server default 1 fp32 / 2 int8) |
| `VIENEU_QUEUE` | `${VIENEU_QUEUE:-16}` | `${VIENEU_QUEUE:-4}` |
| `VIENEU_QUEUE_TIMEOUT` | `${VIENEU_QUEUE_TIMEOUT:-10}` | `${VIENEU_QUEUE_TIMEOUT:-10}` |
| `VIENEU_API_KEY` | `${VIENEU_API_KEY:-}` | `${VIENEU_API_KEY:-}` |
| `VIENEU_WATERMARK` | `${VIENEU_WATERMARK:-1}` | `${VIENEU_WATERMARK:-1}` |
| `HF_HOME`, `PYTHONUNBUFFERED` | set | set |

- The GPU-requesting services (`gpu`, `api-gpu`, and the legacy `serve`) declare `deploy.resources.reservations.devices` (driver `nvidia`, `count: all`, capability `gpu`); `api-cpu` carries **no** GPU reservation and builds `docker/Dockerfile.cpu`, so CPU-only hosts use it unchanged (**Observed** from the capture).[^vieneu-tts-docs]
- The legacy `serve` service uses `/root/.cache/huggingface` as `HF_HOME` and mounts the same `huggingface_cache` volume there, so its cache path differs from the API/Web-UI services (**Observed**).[^vieneu-tts-docs]

## Healthchecks and lifecycle

- Both API services healthcheck with `python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).status == 200 else 1)"`, `interval: 15s`, `timeout: 5s`, `retries: 3`, and `start_period: 120s` (`api-gpu`) or `180s` (`api-cpu`), matching the longer CPU warm-up; both use `restart: unless-stopped` and the comment records that the GPU stream scheduler does not recover from death, so the healthcheck restarts the container (**Reported**).[^vieneu-tts-docs]
- The compose comment records the intent: RTX ≈ 16 streams for `api-gpu`, "no GPU: 1–2 streams" for `api-cpu`, and it points readers to `docs/streaming.vi.md` for request examples (**Reported**).[^vieneu-tts-docs]

## Relationships

- Deploys [VieNeu-TTS OpenAI-Compatible Speech API](vieneu-tts-openai-speech-api.md): the `api-gpu`/`api-cpu` commands, environment, port, and healthcheck target that server's contract (**Synthesis**).[^vieneu-tts-docs]
- Configures [VieNeu-TTS Streaming Runtime and Performance](vieneu-tts-streaming-runtime.md) through `VIENEU_MAX_STREAMS`/`VIENEU_QUEUE` and the backend/precision settings that determine GPU stream capacity or CPU stream count (**Synthesis**).[^vieneu-tts-docs]
- Serves [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md) Web UI and API; the `serve` profile is that family's legacy v2 LMDeploy path (**Synthesis**).[^vieneu-tts-docs]
- Packaging comparison: [Speech Deployment Tools Comparison](speech-deployment-tools-comparison.md) groups container/API deployment options; this concept adds VieNeu's Compose profiles as one concrete instance (**Synthesis**).

## Coverage and limits

- Inspected statically as the captured `docker/docker-compose.yml` (SHA-256 `1329dee3…`, 5,614 bytes, matching `checksums.json`) plus the package README ledger; no image was built, no container started, and no GPU reservation, healthcheck, or port was exercised (**Observed** static inspection only).[^vieneu-tts-docs]
- The referenced Dockerfiles (`docker/Dockerfile.cpu`, `Dockerfile.gpu`, `Dockerfile.serve`), `apps/gradio_main.py`, `apps/openai_speech.py`, and `.env` handling are not in `raw/` and were not inspected, so base images, Python/torch pins, entrypoints, and user IDs are unknown (**Synthesis**).[^vieneu-tts-docs]
- GPU reservations, ports, healthcheck timing, and the profile comments are read directly from the capture and were not runtime-verified (**Synthesis**).[^vieneu-tts-docs]
- Profile names, ports, and defaults are release-specific and carry `stale_after: 2027-10-07` per the `tts` domain rule (**Synthesis**).[^vieneu-tts-docs]

[^vieneu-tts-docs]: [VieNeu-TTS supporting docs](../raw/vieneu-tts-docs/README.md) — locators: package README coverage ledger; `docker/docker-compose.yml` (`x-base-config` anchor: volumes, `env_file` `.env` optional, `HF_HOME`/`PYTHONUNBUFFERED`/`GRADIO_*`, ports, `stdin_open`/`tty`; services `cpu`, `gpu`, `api-gpu`, `api-cpu`, `serve` with build contexts/targets, commands, ports, environment, healthchecks, `restart`, GPU `deploy.resources.reservations.devices`, `huggingface_cache` volume; comments naming 16 vs 1–2 streams and `docs/streaming.vi.md`); SHA-256 and byte length in `checksums.json`.
