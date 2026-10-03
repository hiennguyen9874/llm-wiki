---
type: Concept
title: Von Decision Model: 395M ModernBERT System One Decisions with Chains and Local Calibration
description: Open-source 395M ModernBERT System One decision model with calibrated Choice/Noul/Score, SystemOne-compatible serving, confidence gating, chain-of-options computation, and local recalibration.
tags: [von, decision-models, open-weights, calibration, serving]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T23:45:00Z }
sources:
  - id: von-2026
    resource: ../raw/von.md
    kind: documentation
    title: Von
---

# Von Decision Model: 395M ModernBERT System One Decisions with Chains and Local Calibration

Synthesis: Von is an open-source, non-autoregressive System One decision model that scores described options in one forward pass from a 395M ModernBERT encoder, serving calibrated `Choice` / `Noul` / `Score` over the TypeSafe `/v1/systemone` wire protocol on CPU (OpenVINO), CUDA, ROCm, and Apple MPS; its durable distinctions are a measured 0.80 confidence gate, a `band` versus `raw` Noul decision rule, deterministic chain-of-options computation for temporal/numeric states, and a frozen-weight local `von calibrate` path[^von-2026].

## Identity and distribution

- **Reported** identity: open-source System One decision model, `wfzyx/von` on Hugging Face, `von-sdk` on PyPI and npm, `ghcr.io/wfzyx/von:cpu` container; weights (~3 GB) fetched from the Hub on first use into `HF_HOME` (container default `/data/huggingface`)[^von-2026].
- **Reported** license: Apache-2.0[^von-2026].
- **Reported** model versions in text: wire example uses `model: "von-1.3.0"`; benchmark table distinguishes Von 1.2 weights from Von 1.3 (same weights plus chains)[^von-2026].
- **Reported** scope limit: English only; other languages get token matching with unearned confidence — do not deploy multilingually on this source alone[^von-2026].
- Container and build note is **reported**: `cpu` / `latest` tags are OpenVINO on `linux/amd64` plus `<version>-cpu` UTC calver; a CUDA image builds from the same `Dockerfile` with `--build-arg TORCH_BACKEND=default` but is not published[^von-2026].

## Architecture and API shape

- **Reported** backbone: 395M ModernBERT encoder, one forward pass, CPU-served; answers Choice (pick one of K described options with full distribution), Noul (probability a condition holds), and Score (calibrated ordinal position) over any JSON or text state without generating tokens[^von-2026].
- **Reported** multi-question efficiency: several questions over one state cost one forward pass via `von.system_one(state, questions)` / `systemOne`, with `von.choice` / `von.noul` / `von.score` constructors and `decide` / `judge` / `rate` conveniences in Python and mirrored TypeScript (`decide`, `judge`, `rate`, `systemOne`)[^von-2026].
- **Reported** usage rule: `judge` without `criteria` is the weakest path (generic holds/is-false descriptions, surface cues win) — pass `criteria` or phrase as a described 3-way Choice[^von-2026].
- Doom demo is **reported**: every action is one forward pass scoring six option descriptions against a text rendering of the depth buffer, using the same shipped weights that answer routing questions with no policy network or RL (header image `assets/von-doom.gif`, pixels not inspected here)[^von-2026].

## Confidence gating (reported measurements)

- Gate helper is **reported**: `von.patterns.confidence_gate(state, questions, threshold=0.80)` splits answers into `automatic` / `escalate`; the 0.80 default is described as measured, not guessed, via `benchmarks/sweep_threshold.py` on held-out jabr v2 plus coding-agent probes with Von 1.2 weights[^von-2026].
- **Reported** Choice gate: at ≥0.80 keeps 25% of items at 92.4% accuracy (90% lower bound 89.4%, n=702; rest at 59%); lowest cutoff clearing 90% kept-accuracy with 90% confidence is 0.82; full curves in `results/threshold_sweep_*.json` (uninspected here)[^von-2026].
- **Reported** Noul gate: keeps 16% at 83%, gated on `noul_raw` (the pre-band probability) — the committed `noul` sits in a fixed band and carries no gate signal[^von-2026].
- **Reported** cascade: with Qwen3.5-4B on JevBench public, Von-first matches the 4B alone from 0.75 up — framed as a cost lever, not an accuracy lever[^von-2026].
- **Reported** out-of-domain failure: ranking itself breaks on judge pairs and agent-shadow probes (kept-accuracy flat at any cutoff) — a threshold cannot rescue that, only labels and a refit can[^von-2026].

## Wire protocol and serving

- **Reported** compatibility: `von serve` exposes `/v1/systemone`, byte-compatible with the TypeSafe specification; anything talking to Jev talks to Von by changing the base URL; SDKs use `VON_BASE_URL`[^von-2026].
- **Reported** response extras: `usage.input_tokens` is the real tokenizer count over every encoder pass; a middle-truncated state carries a `truncation` field plus `X-Von-Truncated` / `Warning` headers; with `--on-overflow refuse` an oversize state returns HTTP 422 mentioning the context window (linked Decision Index no-truncation rule)[^von-2026].
- **Reported** criteria and auth: criteria values may be strings or structured JSON; `VON_API_KEY` enables bearer auth with clients falling back to `TYPESAFE_API_KEY`[^von-2026].
- **Reported** device default: `--device` / `VON_DEVICE` default `auto` (choices `cuda`, `mps`, `openvino:gpu`, `openvino:cpu`, `cpu`), auto preferring OpenVINO CPU over plain torch CPU[^von-2026].
- **Reported** state overflow: `--max-state-tokens` / `VON_MAX_STATE_TOKENS` default 8192, middle-truncated 60% head plus 40% tail so question and options fit; `--on-overflow` / `VON_ON_OVERFLOW` default `truncate`, `refuse` returns 422[^von-2026].
- **Reported** Noul decision rule: `--noul-decision` / `VON_NOUL_DECISION` default `band` maps Noul `P(yes)` to `0.8 + 0.1·(p−0.5)` (mirrored below 0.5) so every answer commits outside the 0.2–0.8 abstention band with argmax and ordering unchanged; `raw` returns the calibrated posterior; edge/slope via `VON_NOUL_BAND_EDGE` / `VON_NOUL_BAND_SLOPE`[^von-2026].
- **Reported** checkpoint knobs: `VON_MODEL_ID` default `wfzyx/von`; `VON_CHECKPOINT_DIR` absolute-path checkpoint (`option_marker.pt` + `marker_calibration.json`), with the relative default `checkpoints/von-1.2` noted as working-directory dependent; `VON_CALIBRATION` pins a `marker_calibration.json`; without a local checkpoint `calibrate` writes to `~/.cache/von/marker_calibration.json` which serve picks up[^von-2026].

## Chain-of-options (reported)

- **Reported** purpose: deterministic multi-step computation for temporal/numeric states, driven by Von's own Choice decisions with zero generated tokens[^von-2026].
- **Reported** trigger rule: fires on computable structure in the state (two dates, a date and a duration, two amounts), never on question wording[^von-2026].
- **Reported** mechanism: a regex proposer lists typed spans; every chain whose typed slots can be filled is bound (Von picks among candidate spans when ambiguous) and executed by a fixed operator library (`add_duration`, `in_zone`, `elapsed_hours`, `prorate`, `cumsum`, `is_leap_year`, …); computed datetimes feed a bounded second round so chains compose; a computed value landing on exactly one option answers through a strict matcher, otherwise Von reads the state plus every computed fact with provenance[^von-2026].
- **Reported** extension point: chains are TOML files in `src/von/chains/library/` — add your own; disabled via `--no-chains` / `VON_CHAINS_DIR=off`, budgeted via `VON_CHAINS_MAX_CALLS` (default 16) and `VON_CHAINS_MAX_STATE_TOKENS` (default 4096, chains stand down on longer states)[^von-2026].
- **Reported** latency cost: lands on the hard tail (hard-tier p50 4.2 s on 4 vCPU, 0.45 s on an A10G); serve chain-heavy loads on GPU or lower `VON_CHAINS_MAX_CALLS`[^von-2026].

## Local recalibration (reported)

- Command is **reported**: `von calibrate labels.jsonl` refits the confidence map on your own labels with frozen weights on CPU in minutes; writes `marker_calibration.json` into the checkpoint dir (preferred by the backend) or `--out` elsewhere[^von-2026].
- **Reported** input and selection: one wire question per line plus `gold` (with `{"state", "instructions", "choices", "gold"}` shorthand); picks scalar versus feature map by k-fold CV and reports NLL/ECE for raw, shipped, scalar, and map[^von-2026].
- **Reported** invariant: temperature never changes an answer, only claimed confidence[^von-2026].
- Training on own labels or another encoder (e.g. German, smaller) is delegated to `docs/finetune.md` (uninspected here)[^von-2026].

## Benchmarks (reported, JevBench v1.4)

- Board scope is **reported**: JevBench v1.4, the last revision before Von's Noul band rule; v1.5.1 numbers, sealed-tier breakdowns, Decision Index, and jabr v2 live on the model card (uninspected here); I/C/S/K are Intelligence, Calibration, Speed, Cost with composite as their geometric mean under a generalization gate[^von-2026].
- **Reported** table (see source Benchmarks table): Jev 1.13 (TypeSafe, closed) composite 63.3 (I 53.1, C 76.3, S 83.3, K 52.0; hard 0.741, sealed 0.367, p50 0.65 s); hopper (Qwen3.5-4B + LoRA) 59.4; jeff (GLiFormer-large ~400M) 30.6; Laya (ModernBERT-large 421M) 30.3; Von 1.2 (395M) 27.5 (I 34.5, C 75.7, S 70.5, K 77.8; hard 0.373, sealed 0.279, p50 0.34 s, cpu); Von 1.3 (same weights + chains, local run) hard 0.441, S 88.4, p50 0.36 s[^von-2026].
- **Reported** speed remeasure: raw p50 0.096 s on 4-vCPU Xeon 8488C (OpenVINO) and 0.023 s on A10G, both inside the Jev-class line (`results/speed_remeasure.md`, uninspected)[^von-2026].
- **Reported** chains effect: on 111 public hard items, chains on versus off gives 2 vs 9 discordant with McNemar p = 0.065; zero discordant on easy, standard, and jabr v2[^von-2026].
- **Reported** statistical gate: every accuracy claim passes through `benchmarks/stat_gate.py` (paired exact McNemar plus minimum detectable effect); below the MDE it is reported as UNRESOLVABLE, not a win; older tables in `docs/benchmarks.md` (uninspected)[^von-2026].

## Relationships

- Implements decisions for [Jev Decision Model](jev-decision-model.md) as an open CPU-served encoder comparator.
- Uses [Jev API Patterns](jev-api-patterns.md) SystemOne `choice` / `noul` / `score` shapes with Von's band/raw and truncation extensions.
- Uses [Classifier Calibration](classifier-calibration.md) for local refit and threshold-gated deployment.
- Informs [Classifier Selection](classifier-selection.md) self-host and fine-tune-versus-buy choices.

## Coverage limits

- Static inspection only of `../raw/von.md`; no weights, SDK runs, serving, calibration, or benchmark reproduction was performed here.
- Linked code, docs, configs, and results (`docs/finetune.md`, `docs/benchmarks.md`, `benchmarks/sweep_threshold.py`, `benchmarks/stat_gate.py`, `results/threshold_sweep_*.json`, `results/speed_remeasure.md`, `src/von/chains/library/`, model card, Hub/npm/container registries) were not inspected; all mechanism, latency, accuracy, and calibration figures above are **reported** vendor/README values.
- Header GIF `assets/von-doom.gif` covered via caption only, not pixel inspection.
- Freshness: version strings (`von-1.3.0`, Von 1.2/1.3, JevBench v1.4/v1.5.1) describe this snapshot; verify flags and numbers against live docs before building.
- No credentials, keys, tokens, or PII were found; `VON_API_KEY` / `TYPESAFE_API_KEY` / `HF_HOME` mentions are variable names, not live secrets.

[^von-2026]: Von project, "Von," canonical local entry `../raw/von.md`, upstream `https://huggingface.co/wfzyx/von` via model-card link, package links `https://pypi.org/project/von-sdk/` and `https://www.npmjs.com/package/von-sdk`. Locators in text: header tagline and Doom caption; Install; Use (single- and multi-question examples); Acting on confidence (0.80 gate, Choice/Noul keeps, 0.82 cutoff, Qwen cascade, out-of-domain limit); Wire protocol (route, extras, auth); CLI table (serve/calibrate plus flags/env rows); Chain-of-options; Benchmarks table and footnotes 1–2; License.
