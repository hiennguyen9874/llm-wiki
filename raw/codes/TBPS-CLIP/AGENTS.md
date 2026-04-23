# Repository Guidelines

## Project Structure & Module Organization
- `main.py` trains TBPS-CLIP; `eval.py` runs evaluation.
- `config/` stores runtime configs (`config.yaml`, `s.config.yaml`). Update dataset/checkpoint paths here instead of hardcoding.
- `model/` contains architecture and losses (`tbps_model.py`, transformer blocks, `loss.py`).
- `misc/` contains training utilities: data loading, schedulers, build helpers, and eval helpers.
- `text_utils/` contains tokenization/masking utilities and BPE vocab.
- `shell/` provides runnable scripts (`train.sh`, `eval.sh`) for distributed launch.
- `image/` holds static assets for docs.

## Build, Test, and Development Commands
- Install deps:
  - `pip install -r requirements.txt`
- Train (simplified preset):
  - `bash shell/train.sh`
- Evaluate (simplified preset):
  - `bash shell/eval.sh`
- Full training/eval (non-simplified):
  - `torchrun --nproc_per_node=4 main.py`
  - `torchrun --nproc_per_node=1 eval.py`
- Before running, set valid `anno_dir`, `image_dir`, and `model.checkpoint` in `config/*.yaml`.

## Coding Style & Naming Conventions
- Python code uses 4-space indentation and snake_case for functions/variables.
- Keep modules focused by concern (`model/` for networks, `misc/` for pipeline helpers).
- Prefer explicit config-driven behavior; add new knobs under `config/*.yaml` with clear names.
- No formatter/linter config is currently enforced; follow existing style and keep imports/grouping consistent.

## Testing Guidelines
- There is no dedicated unit-test suite yet.
- Treat evaluation as regression testing:
  - run `bash shell/eval.sh` after model/training/data-pipeline changes,
  - report `Acc@1`, `Acc@5`, `Acc@10`, and `mAP` from stdout.
- For data/config changes, verify one short training smoke run completes without runtime errors.

## Commit & Pull Request Guidelines
- Follow Conventional Commit style seen in history (`feat:`, `fix:`, `docs:`, `chore:`).
- Keep commits scoped (one logical change per commit).
- PRs should include:
  - what changed and why,
  - config/dataset assumptions,
  - commands used for validation,
  - before/after metrics for behavior-impacting changes.
- Link related issues or experiment notes when available.

## Security & Configuration Tips
- Do not commit dataset files, checkpoints, or machine-specific absolute paths.
- Keep secrets/tokens out of configs and scripts; use environment variables where needed.
