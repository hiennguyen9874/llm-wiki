---
type: Concept
title: OpenJev Open-Weights Typed Decision Model
description: Open-weights typed-decision model on Qwen3.8-27B with letter readout, fixed calibration, Jev-compatible API, and reported near-hosted accuracy plus H100 serving recipe.
tags: [open-weights, decision-models, jev, calibration, agents]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T23:50:00Z }
sources:
  - id: openjev-2026
    resource: ../raw/openjev-openjev/README.md
    scope: ../raw/openjev-openjev/
    kind: model-card
    title: OpenJev
  - id: openjev-sglang-2026
    resource: ../raw/openjev-sglang.md
    kind: documentation
    title: openjev-sglang
  - id: openjev-nli-2026
    resource: ../raw/openjev/README.md
    scope: ../raw/openjev/
    kind: model-card
    title: openjev — Qwen3.5 trained as jev model
  - id: razorback16-openjev-2026
    resource: ../raw/razorback16-openjev.md
    kind: documentation
    title: OpenJev
---

# OpenJev Open-Weights Typed Decision Model

Synthesis: OpenJev is an open-weights decision model that answers typed `choice` / `noul` / `score` questions from plain-word request labels in one forward pass per question, with a frozen letter-readout helper and fixed calibration; it is **reported** within 1.4 points of the hosted Jev API on 10,000 text questions and ties it on a matched 100-task MiniWoB run, served on one H100 with a pinned vLLM plus helper recipe[^openjev-2026].

## Identity and license

- Independent project, not affiliated with TypeSafe; Jev is their product; commercial licence via `support@loopai.com`[^openjev-2026].
- Weights: CC BY-NC 4.0 (research / non-commercial with attribution); `helper/` and `serve/` are Apache 2.0; derivative of `Qwen/Qwen3.8-27B` revision `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0` under Apache 2.0 with attribution in `NOTICE` — **observed** in `NOTICE` and `README.md`[^openjev-2026].
- Canonical entry `../raw/openjev-openjev/README.md`, package scope `../raw/openjev-openjev/`, Hugging Face `openjev/openjev`; no immutable commit hash is recorded in the bundle — treat the `SHA256SUMS` / `MANIFEST.json` file hashes as the snapshot identity[^openjev-2026].
- Name-collision warning — **synthesis**: this `openjev/openjev` tuned-weights package is a different project from [SemIf Open Decisions](semif-open-decisions.md) (`TheoLeeCJ/SemIf`, formerly called OpenJev), which is a no-training direct-logit baseline on frozen models; do not merge their accuracy or serving figures[^openjev-2026].
- Card frontmatter declares languages `en/de/fr/hi/zh/ja` with `decision-model` / `zero-shot-classification` / `calibrated-probabilities` / `vllm` tags[^openjev-2026].

## Mechanism (**observed** in `helper/shim.py`, **reported** in `README.md`)

- One score per option at the first output position: each option gets a letter (`A–Z` + `a–z`, 52), the server is asked for a single token, and the helper soft-maxes the letter log-probs into probabilities with fixed calibration[^openjev-2026].
- Measured readout requires `READOUT_TARGETED=1` (exact per-letter scores by token id via `logprob_token_ids`, failing rather than flooring on missing scores), `READOUT_T=0.85`, `READOUT_NOUL_T=1.829074`, `READOUT_NOUL_BIAS=0`, and `READOUT_INSTR_STYLE=pyrepr`; keep the four together to reproduce the card numbers[^openjev-2026].
- `noul` fits a yes/no slope over the two-letter readout: `p = sigmoid(logit(p_yes) / NOUL_T + NOUL_BIAS)`; `score` returns the expected 0-based level plus `legend` / per-level probabilities; `choice` picks the winner before rounding (4-decimal probabilities); confidence follows the TypeSafe adapter formulas (`choice_confidence`, `score_confidence`)[^openjev-2026].
- Above 52 options the helper splits into near-equal chunks of at most 52, runs one pass per chunk plus one pass over chunk winners, and composes `p(i) ∝ p_final(chunk) · p_chunk(i)/p_chunk(winner)` — **reported** approximate and less stable than a single pass[^openjev-2026].
- Request shape is Jev-compatible `POST /v1/systemone` with `{model, state, questions}`; `state` may carry one image as `screenshot`/`image` (data URL or raw base64 PNG/JPEG), the rest becoming text state; `usage` sums prompt tokens with `output_tokens: 0`[^openjev-2026].
- Prompt layouts in code: screenshot plus `state.task` (or `instructions.goal`) uses a trained task / previous-actions / red-letter-marks lane; screenshot plus harness `page`/`elements` shape reuses that lane with unmarked candidates and page/elements as context — the card warns this image-plus-elements combination did not appear in image training, so run a matched check before relying on it; all other shapes use `State / Question / Options` text layout[^openjev-2026].
- Helper defaults that matter: `READOUT_PERMS=1`, `SHIM_POOL=16`, `SHIM_STAGGER=1` with `SHIM_STAGGER_MIN_CHARS=16000` (first question alone to warm prefix cache), `TOKENIZER=<model dir>`; `SHIM_LOOP_BREAK`, `SHIM_COMPACT`, `SHIM_LAYOUT`, `SHIM_PAD` are off in the measured recipe[^openjev-2026].
- Agent tip (**reported**): treat `DONE` as the model's opinion and confirm completion in your own loop (success message, changed URL, saved record) before stopping[^openjev-2026].

## Reported accuracy (all **reported** project measurements, not reproduced here)

- Protocol: every set held out from fine-tuning (checked by id and content); the 10,000-question text table mixes 6,922 fresh additions/replacements with 3,078 development-used questions, with the fresh-only gap stated; at most 26 options per question so all four arms fit Nimble's 2,048-token limit on identical state/question/options/order; one attempt, no retries; three invalid/failed hosted responses (one HTTP 520, two non-argmax picks) count as incorrect[^openjev-2026].
- Headline text: hosted Jev 85.4% (8,540/10,000), OpenJev **84.0%** (8,403), same base before tuning 80.4% (8,036), Nimble 9B 75.7% (7,574) — 1.4 points behind hosted (1.2 on the 6,922 fresh), +3.7 over base, +8.3 over Nimble[^openjev-2026].
- By kind (OpenJev vs hosted vs before tuning): intent/routing/topic 92.8/92.8/93.2 (1,218); sentiment/stance 82.1/81.5/78.3 (1,214); spam/hate 80.4/81.2/80.1 (695); legal 78.9/78.8/77.8 (1,305); ethics/policy 78.1/75.8/65.5 (877); commonsense 85.8/88.3/80.3 (2,260); science/facts/claims 82.5/89.0/81.0 (1,558); reading+language 89.2/89.3/83.3 (873); within 2 points on five of eight kinds, ahead on three[^openjev-2026].
- Legal native-expert slice: 613 merger-agreement clauses from 151 contracts, OpenJev 76.7% vs hosted 73.7% vs before-tuning 75.4% — held-out pairs, not unseen contracts[^openjev-2026].
- Agent/language tuning gaps (before → OpenJev): desktop next-action from screenshot 76.5%→**88.0%** (2,000); web unseen websites 68.5%→**87.4%** (975); web unseen domains 65.7%→**84.5%** (1,000); option-shuffle flip rate 18.5%→**2.3%** (2,000)[^openjev-2026].
- End-to-end MiniWoB: 100 task types, one attempt, same open text-only client — OpenJev **39**, hosted Jev 39, base before tuning 38; about a quarter need colour/shapes/drag the client cannot do, so compare arms, not the absolute level[^openjev-2026].
- Languages/long docs (before → OpenJev): XNLI de/fr/hi/zh 72.5%→**82.5%** (240); MASSIVE intent de/fr/hi/ja 80.4%→**85.8%** (240); QuALITY 2.6k–8.5k-token articles 91.7%→91.7% (120)[^openjev-2026].
- Quantized-format deltas (**reported**, each with its own held-out basis): FP8 checkpoint (~29 GB) +0.17 points on the same 10,000 (95% interval −0.13 to +0.45) and +0.05 on the same 2,000 desktop screenshots, ~2% answers change; MLX 8-bit (~27 GB, text only) same 8,403/10,000 as served 16-bit (72 each way; interval −0.24 to +0.22), 1.5% change; MLX 4-bit (~15 GB, text only) 84.3% vs 84.9% served vs 84.7% MLX-8-bit on the first 4,692; GGUF Q4_K_M (16.5 GB) −0.34 (−1.06 to +0.39) and Q8_0 (28.6 GB) −0.61 (−1.17 to −0.11) on a separate 1,789-question held-out set (not the full 10,000), 3–4% change; MLX/GGUF builds here take no screenshot input[^openjev-2026].

## Reported speed (one H100, FP8; **reported**, not reproduced)

- Short text ≈80 ms; isolated web step (≈1,460 prompt tokens, ≈23 options) ≈210 ms; desktop screenshot step median 176 ms[^openjev-2026].
- First-read vs cached-new-question medians: 1.1k tokens 227/118 ms; 4.1k 477/162; 8.1k 923/213; 12.2k 1,433/246; 15.1k 1,758/257[^openjev-2026].
- Batch (not sequential latency): 100 questions over one 4.1k-token page in 3.9 s at queue concurrency 16 (39 ms average); 7 requests/s on distinct 1.2k-token pages at concurrency 8, single GPU[^openjev-2026].

## Serving recipe (**observed** in `serve/SERVE.md` plus static `helper/shim.py` read)

- Locked versions: `vllm==0.29.0`, `torch==2.13.0` (measured `2.13.0+cu130`), `transformers==5.17.0`, `peft==0.21.0`, `openai==3.16.2`, `httpx==0.28.1`; public machine runs `openai 3.15.0`, so install the measured set to reproduce[^openjev-2026].
- vLLM flags exactly as measured: `--served-model-name qwen --enable-prefix-caching --max-model-len 16384 --gpu-memory-utilization 0.90 --limit-mm-per-prompt '{"image":1}' --trust-remote-code --max-num-seqs 256 --max-logprobs 64 --gdn-prefill-backend triton --quantization fp8`; the first three load-bearing items for the helper are the model name, `--max-logprobs 64` (up to 52 letters in one request), and the 16,384-token / one-image limits[^openjev-2026].
- Helper env exactly as measured: `VLLM`, `TOKENIZER=<model dir>`, `READOUT_T=0.85`, `READOUT_NOUL_T=1.829074`, `READOUT_NOUL_BIAS=0`, `READOUT_TARGETED=1`, `READOUT_INSTR_STYLE=pyrepr`, `SHIM_STAGGER=1` on loopback `--host 127.0.0.1`; helper file sha256 `81a22f1b1b8912a465059207ef9f60b7c6c16b4de6372305d867efbe38a1987a`; without `--host`/`--port` it binds `127.0.0.1:8765`[^openjev-2026].
- Security boundary (**observed**): `SHIM_TOKEN` gates every route (`/v1/systemone`, `/v1/prewarm`, `/v1/chat/completions`, `GET /v1/version`) with `Authorization: Bearer <token>` when set, but when empty/unset there is no check at all and the helper still serves — including the open chat pass-through — so the `SHIM_TOKEN=...` prefix guard plus loopback/firewall posture is the operator's job; helper is plain HTTP (no TLS) with plain string comparison and no rate limit; the vLLM backend on port 8000 has no auth in this setup, so keep it on loopback even when the helper is exposed[^openjev-2026].
- Other routes: `GET /v1/version` pins model dir plus calibration/constants/flags/helper sha; `POST /v1/prewarm` caches one state; `POST /v1/chat/completions` passes through with thinking forced off[^openjev-2026].
- Known helper behaviours kept as measured: >52-option chunking (above); 4-decimal rounding can miss a sum of exactly 1 (check `probabilities[choice]` with tolerance on near-ties); malformed JSON / non-object body / list-form noul criteria / model-server failure drops the connection without a JSON body; no caps on option count or score levels; 401 vs 422 error shapes[^openjev-2026].
- Architecture (**observed** in `config.json`): `Qwen3_5ForConditionalGeneration`, bf16, 64 text layers (`hidden 5120`, hybrid `linear_attention`/`full_attention`, 24 heads / 4 KV, 262,144 max positions, vocab 248,320) plus a 27-layer 1152-wide vision tower with spatial merge 2; served context is capped to 16,384 by the recipe flag[^openjev-2026].
- Apple-silicon path: `helper/shim_mlx.py` reuses the frozen `shim.py` prompts/readout/temperatures with an MLX stand-in for the single TARGETED `logprob_token_ids` call (text only, asserts helper sha prefix `81a22f1b`) plus `--selfcheck`[^openjev-2026].

## Formats (**reported**)

| format | size | note |
|---|---|---|
| bf16 `openjev/openjev` | ~54 GB | this bundle; serve with `--quantization fp8` on one 80 GB GPU (primary measured recipe) |
| FP8 `openjev/openjev-FP8` | ~29 GB | same-10,000 +0.17, same-desktop +0.05 (above) |
| MLX 8-bit `openjev/openjev-MLX` | ~27 GB | text only, same-count parity (above) |
| MLX 4-bit `openjev/openjev-MLX-4bit` | ~15 GB | text only, smallest Mac fit, subset parity (above) |
| GGUF `openjev/openjev-GGUF` Q4_K_M–Q8_0 | 16.5–28.6 GB | text only, Q4_K_M fits 24 GB cards; 1,789-question validation only so far (above) |

## Relationships

- Uses [Jev API Patterns](jev-api-patterns.md) `choice` / `noul` / `score` shapes with a Jev-compatible `POST /v1/systemone`.
- Requires [Classifier Calibration](classifier-calibration.md) fixed temperatures and noul slope; keep them pinned to reproduce card numbers.
- Informs [Classifier Selection](classifier-selection.md) self-hosted open-weights option versus hosted Jev and distilled students.
- Informs [Jev Decision Model](jev-decision-model.md) as the closest open-weights accuracy anchor in this bundle.
- Contrasts with [SemIf Open Decisions](semif-open-decisions.md): same former name, different mechanism (tuned weights vs no-training baseline).
- Contrasts with [OpenJev-SGLang Decision Serving](openjev-sglang-decision-serving.md): distinct Qwen3.6-35B-A3B on SGLang N+1 readout plus Modal B200 recipe; do not merge its limits or serving figures with this Qwen3.8-27B vLLM recipe[^openjev-sglang-2026].
- Contrasts with [OpenJev NLI Cross-Encoder (AlexWortega)](openjev-nli-cross-encoder.md): same `openjev` name, different project and mechanism (Qwen3.5 NLI entailment scoring vs Qwen3.8-27B letter readout); do not merge its accuracy or serving figures[^openjev-nli-2026].
- Contrasts with [OpenJev Diffusion Decision Server (razorback16)](openjev-diffusion-decision-server.md): same `OpenJev` name, different project and mechanism (razorback16 DiffusionGemma diffusion-canvas server with routed Laya/Verdict/CLM/JevK5 models vs this `openjev/openjev` Qwen3.8-27B letter readout); do not merge its latency or serving figures[^razorback16-openjev-2026].

## Coverage limits

- Inspected by static read: `README.md`, `serve/SERVE.md`, `helper/shim.py`, `helper/shim_mlx.py`, `config.json`, `generation_config.json`, `processor_config.json`, `tokenizer_config.json` (head), `chat_template.jinja`, `NOTICE`, `LICENSE` / `LICENSE-APACHE-2.0`, `MANIFEST.json`, `SHA256SUMS`, `model.safetensors.index.json`; no code was executed and no serving run was reproduced[^openjev-2026].
- Excluded with reason: twelve `model-*.safetensors` shards (~54 GB weights, binary/uninspected beyond the index), `tokenizer.json` (~20 MB, uninspected), five `assets/*.png` figures (not pixel-inspected; tables in prose already carry the durable numbers)[^openjev-2026].
- All accuracy, latency, and quant-delta figures are **reported** project measurements under the pinned recipe; changing any flag or temperature voids the numbers; verify `GET /v1/version` before depending on a deployment[^openjev-2026].
- CC BY-NC 4.0 weights limit commercial reuse; email `support@loopai.com` for a commercial licence; helper/serve code is Apache 2.0[^openjev-2026].

[^openjev-2026]: OpenJev project, "OpenJev," model and serving bundle, canonical local entry `../raw/openjev-openjev/README.md`, package scope `../raw/openjev-openjev/`, Hugging Face `openjev/openjev` with `openjev-FP8`, `openjev-MLX`, `openjev-MLX-4bit`, `openjev-GGUF` variants. Locators in bundle: "Why it is different" labels-in-request / first-position readout / shuffle 2.3% vs 18.5%; "Results" 10,000-question, agent/desktop/web, MiniWoB, language/long-doc, and "Speed" tables plus `assets/` plots; "Formats" and "Request limits" rows; "How it works, in one paragraph" letter readout; `serve/SERVE.md` locked versions, vLLM/helper commands, env-knob and `SHIM_TOKEN` sections, `POST /v1/systemone` shapes and known-helper-behaviour list; `helper/shim.py::LETTERS/TARGETED/_readout_once/readout/_distribution/answer_choice/answer_score/answer_noul/choice_confidence/score_confidence/with_image/_task/loop_break/VERSION`; `helper/shim_mlx.py` TARGETED stand-in plus selfcheck; `config.json` architecture; `NOTICE` Qwen3.8-27B rev `1d4bf0f2...` plus licence split.
[^openjev-sglang-2026]: openjev-sglang project, "openjev-sglang," canonical local entry `../raw/openjev-sglang.md`. Locators: top NOTE (early experiment, native SGLang endpoint recommendation); "How inference works" (N+1 one-token calls, A–Z/AA labels); "Run on Modal" (B200 recipe); Qwen3.6-35B-A3B on SGLang 0.5.19 distinction from this Qwen3.8-27B vLLM recipe.
[^openjev-nli-2026]: AlexWortega openjev project, "openjev — Qwen3.5 trained as jev model," canonical local entry `../raw/openjev/README.md`, package scope `../raw/openjev/` (duplicate `../raw/openjev.md` verified identical by diff). Name-collision locator: checkpoints (v5) links and Qwen3.5 NLI cross-encoder definition, distinct from this `openjev/openjev` Qwen3.8-27B letter-readout bundle.
[^razorback16-openjev-2026]: razorback16, "OpenJev," project documentation, canonical local entry `../raw/razorback16-openjev.md`, upstream `https://github.com/razorback16/openjev`. Name-collision locators: "Models" table (DiffusionGemma 26B-A4B plus routed `laya-1.0`/`verdict-1.4`/`clm-v0.1`/`jevk5-0.2`); "How it works" diffusion-canvas masked-slot readout, distinct from this bundle's Qwen3.8-27B letter readout.
