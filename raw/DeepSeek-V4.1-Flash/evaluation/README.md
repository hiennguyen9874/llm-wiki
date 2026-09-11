# Running DeepSWE with `dsh-minimal` and `mini-swe-agent`

## 1. Prerequisites

- Docker, running and able to pull images
- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- An endpoint and key for any DeepSeek-API-compatible service (the DeepSeek official API is used as the example below)

```sh
export DEEPSEEK_API_KEY=sk-your-key-here
export DEEPSEEK_BASE_URL=https://api.deepseek.com
```

## 2. Get Pier and DeepSWE

```sh
git clone https://github.com/datacurve-ai/pier.git
git -C pier checkout 0c802fc067a425345b24d1c69411aa98acf61a1d

git clone https://github.com/datacurve-ai/deep-swe.git
git -C deep-swe checkout 0b9fabbb63b9104d678fe965e1632f2dd9eaa2ea
```

## 3. Patch and install Pier

`dsh-minimal.patch` ships next to this document. Treat it as a **reference patch** and adapt it to your own setup.

```sh
cd pier
git apply /path/to/dsh-minimal.patch
uv sync
```

What the patch changes:

- **Adds the `dsh-minimal` agent**, which drives the Harness SDK and folds its event stream into a Pier ATIF trajectory. The SDK artifact is never installed into the image: step 4's `--mounts-json` bind-mounts it read-only into the sandbox, so no trial installs anything.
- **Appends a runtime-constraints section to the task instruction for both agents**: work in `/app`, leave `/tests` alone, no network or package mirror.
- **Passes test-runner concurrency caps into the container**: Docker's `--cpus` is only a quota, so `nproc` inside the container reports the host's core count and test runners size their worker pools from that rather than from the container's share.
- **Enables IPv6 loopback in the container**: Docker disables it by default, so suites that bind `::1` are skipped and scored as failures.
- **Makes `--mounts-json` additive instead of replacing the default mounts**, keeping the `/logs` binds that carry agent logs and collected patches.

## 4. Run the suite

Both agents take the same task set, concurrency, and `--no-delete` (which keeps the task images cached between trials). Repeat each run with a different `--job-name` and average the results.

Each trial's container takes the 2 CPUs and 8 GB its task declares, so size `-n` against the host's cores and memory.

### `mini-swe-agent`

Pier installs it into each task image at trial time, so no host-side preparation is needed.

```sh
uv run pier run \
  -p ../deep-swe/tasks \
  --agent mini-swe-agent \
  --model deepseek/deepseek-flash \
  --ak reasoning_effort=max \
  --ak cost_limit=0 \
  --ae DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY" \
  --ae DEEPSEEK_BASE_URL="$DEEPSEEK_BASE_URL" \
  -n 32 --no-delete -r 2 --job-name deepswe-mini-run1 -y
```

- `--model` takes a litellm-style `provider/model` string.

### `dsh-minimal`

Install the Harness SDK artifact once on the host, then bind-mount it read-only into every container.

```sh
mkdir -p ~/dsh-minimal && cd ~/dsh-minimal
uv pip install --target dsh-dist \
  --python-version 3.12 --python-platform x86_64-manylinux_2_28 \
  'deepseek-harness-sdk==0.1.5.*'
```

```sh
uv run pier run \
  -p ../deep-swe/tasks \
  --agent dsh-minimal \
  --model deepseek-flash \
  --ak reasoning_effort=max \
  --ae DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY" \
  --ae DEEPSEEK_BASE_URL="$DEEPSEEK_BASE_URL" \
  --mounts-json '[{"type":"bind","source":"'"$HOME"'/dsh-minimal/dsh-dist","target":"/opt/dsh-minimal","read_only":true}]' \
  -n 32 --no-delete --job-name deepswe-dsh-run1 -y
```

- In `--mounts-json`, `source` is the absolute path of the `dsh-dist` directory above; `target` is always `/opt/dsh-minimal`.

## 5. Read the results

```
jobs/<job-name>/
  result.json              pass rate and token totals
  <task>__<id>/
    result.json            reward, fail-to-pass / pass-to-pass counts, tokens
    agent/trajectory.json  full ATIF trajectory (dsh-minimal)
    agent/mini-swe-agent.trajectory.json   mini-swe-agent trajectory
    verifier/              reward.json and test output
```

Browse a job with `uv run pier view jobs/<job-name>`.
