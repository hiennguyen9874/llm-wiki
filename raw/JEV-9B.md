---
license: apache-2.0
base_model: Qwen/Qwen3.5-9B
base_model_relation: finetune
datasets:
  - SargeDev/jev-distill-corpus-v3
language:
  - en
library_name: transformers
pipeline_tag: text-classification
tags:
  - system-one
  - system-two
  - blocks-of-experts
  - typed-decisions
  - decision-model
  - calibrated-probabilities
  - knowledge-distillation
  - jev
  - noul
  - choice
  - score
  - lora
  - qwen3_5
  - text-generation
  - dual-head
  - vllm
  - multimodal
  - vision
  - computer-use
  - robotics
metrics:
  - kl
  - auroc
  - brier
  - ece
model-index:
  - name: autotrust/JEV-9B (student of TypeSafe Jev 1.13)
    results:
      - task:
          type: text-classification
          name: typed decisions (noul / choice / score) — agreement with the TypeSafe Jev 1.13 teacher
        dataset:
          type: SargeDev/jev-distill-corpus-v3
          name: jev-distill-corpus-v3 · test_set_30k
          split: test_set_30k
        metrics:
          - type: kl_divergence
            name: mean KL(target ‖ model), all test rows (25,376 of 29,955 targets are TypeSafe Jev 1.13 distributions)
            value: 0.0210
          - type: auroc
            name: noul AUROC
            value: 0.996
          - type: brier
            name: noul Brier (vs. target probability, all rows)
            value: 0.0015
          - type: mae
            name: score expected-value MAE (0–5 scale)
            value: 0.103
          - type: ece
            name: ECE (15 bins, after temperature)
            value: 0.0007
          - type: accuracy
            name: choice top-1 agreement (all rows)
            value: 0.898
          - type: accuracy
            name: choice top-1 agreement (decisive-target rows, top-2 gap ≥ 0.1)
            value: 0.954
      - task:
          type: text-generation
          name: code generation — System 2 path (base lm_head, adapter off)
        dataset:
          type: openai/openai_humaneval
          name: HumanEval
          split: test
        metrics:
          - type: pass@1
            name: pass@1 (greedy, completion-style prompt)
            value: 0.707
---

# autotrust/JEV-9B

### AutoTrust's first integrated System 1 + System 2 open model, built with the Blocks of Experts recipe

**Fast, calibrated System 1 decisions that are indistinguishable from the closed TypeSafe Jev 1.13 by KL, and
deliberate System 2 generation and reasoning from an untouched Qwen3.5-9B — one set of weights, one vLLM engine,
routed per request. The fastest model of the family: it answers a single decision in about a third of the time the
hosted API takes. Its successor, [autotrust/JEV-27B](https://huggingface.co/autotrust/JEV-27B), is closer to Jev,
transfers better to unseen tasks and has a stronger System 2.**

## New (3 October 2026): JEV-9B can see — robot arm and computer use

JEV-9B now takes images. Every step below is **one System 1 decision**: camera image or screenshot in, a probability
for every action out, in a single forward pass (about 0.2 s on one GPU). Run it with `bash vl/serve.sh` (see
[Images: quick start](#images-quick-start)).

**Robot arm: pick and place from camera images.** The arm sees a top camera image; at every step System 1 answers two
questions (is the target left or right of the gripper, above or below it), and the arm moves accordingly, halving its
step whenever an answer flips. It grasps the cube, carries it and drops it in the tray (MuJoCo simulation).

<video src="https://huggingface.co/autotrust/JEV-9B/resolve/main/videos/robot_arm_pick_place.mp4" controls autoplay loop muted playsinline width="100%"></video>

On 20 random scenes it completed the task 10 times; every cube it grasped ended in the tray, and every miss was a grasp
3–5 cm off target. About 165 ms per decision. Asking it to choose one of 8 motor commands directly did not work: this
model is a fast visual judge, not an end-to-end controller.

**Computer use: screenshot → which element to click.** A real browser (headless Chromium). Every clickable element gets
a numbered box; System 1 picks the next click (or "the task is complete"), the browser clicks it, and the loop repeats.

<video src="https://huggingface.co/autotrust/JEV-9B/resolve/main/videos/computer_use_shop.mp4" controls autoplay loop muted playsinline width="100%"></video>

<video src="https://huggingface.co/autotrust/JEV-9B/resolve/main/videos/computer_use_settings.mp4" controls autoplay loop muted playsinline width="100%"></video>

<video src="https://huggingface.co/autotrust/JEV-9B/resolve/main/videos/computer_use_mail.mp4" controls autoplay loop muted playsinline width="100%"></video>

**95% of 60 random multi-step tasks completed** (shop, settings, mail; 3–7 clicks each), about 0.2 s per click. The
colour swatches and switches carry no text, so those clicks are decided from the screenshot alone. With the numbered
boxes only (no element text) it completed 37%. The failures skipped a step (the colour) and then checked out an empty cart.

Code for both demos: [`vl/demos/`](vl/demos). Image judging, briefly: VL-RewardBench 74.3%, AgentRewardBench AUROC 0.91,
zero-shot short-video recommendation from covers AUC 0.72 (details in [`reports/vl/`](reports/vl)).

### Images: quick start

```bash
hf download autotrust/JEV-9B --include "vl/*" --local-dir JEV-9B
bash JEV-9B/vl/serve.sh     # downloads Qwen/Qwen3.5-9B (with its vision encoder) and serves both systems on :8000
```

```python
import base64, requests

def image(path):
    return {"image": "data:image/png;base64," + base64.b64encode(open(path, "rb").read()).decode()}

r = requests.post("http://localhost:8000/v1/decide", json={
    "kind": "choice",
    "state": ["Top camera image:", image("scene.png"), "\nTask: put the red cube in the tray."],
    "question": "Is the red cube to the left or to the right of the gripper?",
    "options": ["left", "right"]}).json()
print(dict(zip(r["options"], r["probabilities"])))
```

How it works: JEV-9B's language weights are bit-identical to Qwen3.5-9B's, so `vl/serve.sh` serves the unmodified
multimodal Qwen3.5-9B with JEV-9B's System 1 adapter (`vl/adapter_vllm`, the same weights with the layer names moved).
Text decisions match the text-only model (300 test decisions: largest probability difference 0.011). System 2 also reads
images. Keep `--max-num-seqs 8` (set in `serve.sh`); decisions over images are zero-shot.

## At a glance

**Integrated System 1 + System 2, first generation.** JEV-9B is AutoTrust's first open model to serve both modes of
thinking from a single set of weights; the second generation is
[autotrust/JEV-27B](https://huggingface.co/autotrust/JEV-27B). *System 1* answers typed questions (`noul` yes/no ·
`choice` over 2–16 options · `score` on a 0–5 scale) in one forward pass and returns a calibrated probability
distribution. *System 2* is ordinary text generation with step-by-step reasoning (thinking mode). Both run on the
same backbone in the same engine, and a request chooses its system.

**Blocks of Experts recipe.** Rather than fine-tuning one monolithic model, the Blocks of Experts (BoE) recipe keeps a
strong pretrained model as a frozen expert block and adds a small, detachable expert block trained for one capability.
In JEV-9B the System 2 block is Qwen3.5-9B, bit-identical to the release; the System 1 block is 40.2 M trained
parameters (0.5 % of the backbone), trained in ≈ 3 hours on one B200. Because the blocks stay separate, adding
System 1 costs System 2 nothing: HumanEval is 70.7 % before and after, with all 164 completions byte-identical. Folding
the same block into the backbone instead would have cost 9 points (61.6 %).

**Indistinguishable from the closed original on System 1, by KL.** On the 25,376 held-out questions (53 domains)
whose labels are TypeSafe Jev 1.13's own output distributions, the mean KL divergence is **≈ 0.019** (0 = identical).
An observer who sees sampled decisions gains on average 0.019 nats of evidence per decision about which model produced
it, so it takes about 54 decisions to gather a single nat. The fidelity extends to the teacher's mistakes (see
[System 1: indistinguishable from TypeSafe Jev 1.13](#system-1-indistinguishable-from-typesafe-jev-113-by-kl)).
Among the open Jev reproductions we could find, only the JEV models publish this distribution-level measure
(see [How JEV-9B compares with other open Jev reproductions](#how-jev-9b-compares-with-other-open-jev-reproductions)).

**Faster than the hosted API.** On one B200, a single decision takes a median ≈ 90 ms, against 238–301 ms measured
independently for the hosted TypeSafe Jev 1.13 API, and one GPU sustains about 15× the decisions per second an
independent benchmark achieved against that API (see [Speed](#speed-vs-the-hosted-typesafe-jev-113)).

**The fast member of the family; JEV-27B is the closer one.** Same recipe, same API: JEV-9B is 2.6× faster than
JEV-27B on the same benchmark and its weights are a third of the size (18 GB vs 54 GB). JEV-27B lowers mean KL to Jev's
distributions from ≈ 0.019 to ≈ 0.017, more than halves KL on unseen task families (0.234 → 0.104), keeps 96 % instead
of 90 % of the teacher's accuracy on an independent 16-option benchmark, and scores 78.0 % instead of 70.7 % on
HumanEval (see [JEV-9B vs JEV-27B](#jev-9b-vs-jev-27b)).

> **Two models, two organisations.** **TypeSafe Jev 1.13** is the hosted, closed-source model made by TypeSafe AI; it
> is the *teacher* whose published output distributions this model was trained on. **autotrust/JEV-9B** (this
> repository) is an independent open-weights *student* built by AutoTrust AI from the Apache-2.0 corpus
> [`SargeDev/jev-distill-corpus-v3`](https://huggingface.co/datasets/SargeDev/jev-distill-corpus-v3). It is not
> affiliated with, endorsed by, or a product of TypeSafe AI, and shares no weights or code with it.

## Headline results

System 1 numbers are on the held-out `test_set_30k` of `jev-distill-corpus-v3`. Its 29,955 rows come from three
sources: 25,376 rows labelled with TypeSafe Jev 1.13's own output distributions (`yuri_v3`), 2,319 Open-Jev rows with
programmatic ground-truth labels (`openjev_v2`), and 2,260 placeholder rows (`yuri_v1`). Rows marked *Jev-labelled* use
only the first group.

| | What is measured | autotrust/JEV-9B | How to read it |
|---|---|---|---|
| **System 1** | Mean KL divergence from TypeSafe Jev 1.13's distributions, Jev-labelled rows, 0 = identical | **≈ 0.019** | Indistinguishable from the teacher's decisions at this resolution: ≈ 54 sampled decisions to gather one nat of evidence |
| | Mean KL to all test targets (Jev, programmatic and placeholder labels) | **0.021** | The figure in the model index above |
| | Yes/no AUROC (`noul`), Jev-labelled rows | **0.994** | Ranks true vs. false almost perfectly (0.996 over all rows) |
| | Choice top-1 agreement with Jev, Jev-labelled rows | **90.2 %** | 95.4 % over all rows where the target's top two options differ by ≥ 0.1; on near ties any faithful copy agrees about half the time |
| | Rating error (`score`, 0–5 scale), mean absolute error of the expected rating | **0.103** | About one tenth of a rating step |
| | Expected calibration error | **0.0007** | A stated 80 % is an 80 %; fitted temperatures ≈ 1.00, no post-hoc correction needed |
| | KL to the programmatic labels of task families never seen in training (Open-Jev OOD split) | **0.234** | Transfer to new tasks; these labels are ground truth, not Jev's outputs. JEV-27B: 0.104 |
| | Independent benchmark with human gold labels, 16 options | **90 % of the teacher** (0.694 vs 0.769) | 94–97 % of the teacher at 2, 4 and 8 options; see [Benchmark highlights](#benchmark-highlights) |
| **System 2** | HumanEval pass@1, greedy | **70.7 %** | Identical to Qwen3.5-9B (116/164); all 164 completions byte-identical to the base model |
| **Speed** | Single decision, median, one B200 | **≈ 90 ms** | Hosted TypeSafe Jev 1.13, measured independently: 238 ms mean, 291–301 ms median |
| | Decisions per second on the independent benchmark, one B200 | **≈ 340** | ≈ 15× the 23 per second measured against the hosted API; see [Speed](#speed-vs-the-hosted-typesafe-jev-113) |
| | Batched, 128 decisions per batch | **2.5 ms** per decision | With vLLM: 205 decisions/s over HTTP at 256 concurrent clients, text generation ≈ 50× faster than the PyTorch path |
| **Efficiency** | Trained parameters | **40.2 M** (0.5 % of 7.9 B) | ≈ 3 B200-hours, 0.93 epoch ≈ 608 k rows |

## JEV-9B vs JEV-27B

JEV-9B was AutoTrust's first integrated System 1 + System 2 model.
[autotrust/JEV-27B](https://huggingface.co/autotrust/JEV-27B), the second generation, uses the same recipe, code,
hyper-parameters, API and two-block packaging; only the backbone and memory settings changed. Both are evaluated on the
same held-out test set and the same independent benchmark.

<p align="center">
  <a href="https://huggingface.co/autotrust/JEV-27B/blob/main/27b-2.jpg"><img src="https://huggingface.co/autotrust/JEV-27B/resolve/main/27b-2.jpg" alt="JEV family benchmark highlights: KL to TypeSafe Jev 1.13 by question type, accuracy as a percentage of Jev on an independent benchmark, HumanEval for the System 2 path, and speed against the hosted API, for JEV-9B (light bars) and JEV-27B (dark bars)" width="100%"></a>
  <br>
  <sub><b>JEV family benchmark highlights</b> (chart from the JEV-27B repository; light bars = JEV-9B). A · KL to Jev by question type · B · accuracy as % of Jev on an independent benchmark · C · System 2 unchanged · D · speed vs the hosted API · click to enlarge</sub>
</p>

| | **JEV-9B** | JEV-27B | JEV-27B vs JEV-9B |
|---|---|---|---|
| Backbone | Qwen3.5-9B | Qwen3.8-27B | |
| **System 1** — mean KL to TypeSafe Jev 1.13, Jev-labelled rows | ≈ 0.019 | **≈ 0.017** | ≈ −11 % |
| Mean KL to all test targets | 0.021 | **0.019** | −11 % |
| KL to ground-truth labels, unseen task families (OOD) | 0.234 | **0.104** | −56 % |
| Top-1 accuracy, unseen task families (OOD) | 0.918 | **0.942** | +2.4 pts |
| Choice top-1 agreement with Jev, Jev-labelled rows | 90.2 % | **90.5 %** | +0.3 pts |
| Rating error (`score` MAE, all Jev-labelled) | 0.103 | **0.098** | −5 % |
| Top-1 flips under option shuffle (test set) | 3.9 % | **2.9 %** | −1.0 pt |
| Yes/no AUROC (`noul`), Jev-labelled rows | 0.994 | **0.995** | +0.001 |
| Calibration error (ECE) | **0.0007** | 0.0009 | JEV-9B slightly lower; both below 0.001 |
| Independent benchmark, 16 options — % of teacher accuracy | 90 % | **96 %** | +6 pts |
| Independent benchmark — answers changed by option order alone (teacher: 7.0 %) | 11.5 % | **7.4 %** | JEV-27B is close to the teacher's 7.0 % |
| **System 2** — HumanEval pass@1 (greedy) | 70.7 % | **78.0 %** | +7.3 pts |
| Latency on one B200 — single request / batched | **≈ 90 ms / 2.5 ms** | 137 ms / 4.2 ms | JEV-9B is faster |
| Benchmark throughput — 14,400 decisions on one B200 | **42 s** | 110 s | JEV-9B is 2.6× faster |
| Download size (backbone + adapter) | **18 GB** | 54 GB | |
| Trained parameters / compute | 40.2 M / ≈ 3 B200-hours | 108.9 M / ≈ 9.2 B200-hours | |

On the fresh Hacker News, V2EX and community examples (illustrations, not a benchmark), JEV-9B got 92 of 96 decisions
right against 95 of 96 for JEV-27B. The difference is on the harder tasks: JEV-9B misses a TypeScript port that
breaks a "branded, range-checked integer" rule (0.33; JEV-27B 0.93) and flags a CEO wire-transfer fraud message with
less confidence (0.56; JEV-27B 0.84).

**Which to pick.** For routing, moderation, topic triage and short option lists, JEV-9B gives nearly the same answers
2.6× faster (14,400 benchmark decisions in 42 s vs 110 s on one B200) with a third of the weight memory. For long option lists
(more than about 8), unfamiliar task families, code-rule checks, fraud screening, or when the System 2 path matters, use
[autotrust/JEV-27B](https://huggingface.co/autotrust/JEV-27B).

## How JEV-9B compares with other open Jev reproductions

Dozens of open reproductions of TypeSafe Jev appeared within weeks of its launch; the community
[Jev Decision Index](https://huggingface.co/spaces/multimodalart/jev-decision-index) (formerly the Jev Reproductions
Tracker) evaluates 55 of them. Most are trained on human or programmatic gold labels, or on their own synthetic data, so
they aim to match or beat Jev's accuracy rather than reproduce its probabilities. "Closest to Jev" therefore depends on
how closeness is measured:

| measure of closeness to TypeSafe Jev 1.13 | published results (snapshot of 25 September 2026) | where JEV-9B stands |
|---|---|---|
| **Distribution level:** KL to Jev's own output distributions on held-out rows | JEV-27B ≈ 0.017 and JEV-9B ≈ 0.019 on 25,376 Jev-labelled rows. We found no other open reproduction that publishes this measure. | Second lowest published, after JEV-27B |
| **Accuracy relative to Jev** on [`decision-models-under-pressure`](https://github.com/gazelle93/decision-models-under-pressure), 16 options, human gold labels | JEV-27B 96 % · JEV-9B 90 % · Laya 90 % · DeBERTa-v3-large zero-shot 90 % · DeBERTa-v3-base zero-shot 83 % · GLiClass-large 81 % · bge-large 73 % · gte-large 69 % | Level with the best of the other models measured there; JEV-27B is closer (JEV rows are AutoTrust re-runs of the same items; the others were run by the benchmark's author) |
| **Score parity on community leaderboards** | [Decision Index 0.2](https://huggingface.co/spaces/multimodalart/jev-decision-index): Jev 51.67, AutoJev-27B 50.94. [JevBench v1.4.2](https://github.com/fstandhartinger/jevbench): decider-4b v2 64.13, Jev 63.29, JevK5 62.04. [Open-Jev](https://zefan-cai.github.io/open-jev/benchmarks/) public JevBench subset: Jev 200/231, Open-Jev 27B v1.1 197/231 | Not yet evaluated |

On the evidence published today, the two JEV models are the closest open models to TypeSafe Jev 1.13 at the level of
output distributions, with JEV-9B second to JEV-27B. On the independent benchmark JEV-9B is level with the best of the
other models measured there, not ahead of them. It has not yet been run on the Decision Index or JevBench, where
AutoJev-27B scores within about one point of Jev and decider-4b v2 edges ahead of it, so we do not claim it is the
closest by every measure. Note that some reproductions report beating Jev on their own test sets (AutoJev-27B reports
84.60 % against Jev's 82.79 %); that is a different goal from reproducing Jev's behaviour.

*Not to be confused with AutoJev-27B (`denis-pplx/autojev-27b`), an unrelated Qwen3.8-27B decision model trained with
full-weight SFT on its own data.*

## Speed vs the hosted TypeSafe Jev 1.13

TypeSafe does not publish Jev's size or hardware; it reports 70–500 ms end to end. Independent measurements, and ours:

| | TypeSafe Jev 1.13, hosted API | **JEV-9B, one B200** | JEV-27B, one B200 |
|---|---|---|---|
| One decision, single request | 238 ms mean over 29,600 calls ([`decision-models-under-pressure`](https://github.com/gazelle93/decision-models-under-pressure)); 291–301 ms median on three workloads ([Open-Jev](https://zefan-cai.github.io/open-jev/benchmarks/)) | **≈ 90 ms** median (87 ms) | 137 ms median |
| Decisions per second on `decision-models-under-pressure` | 23, with 5 client workers and one question per call | **≈ 340** (14,400 in 42 s) | ≈ 130 (14,400 in 110 s) |
| Batched, 128 decisions per batch | — | **2.5 ms** per decision | 4.2 ms per decision |

So JEV-9B answers a single decision in roughly a third of the time (JEV-27B in roughly half), and one GPU sustains
about 15× (JEV-27B: about 6×) the throughput the benchmark's author achieved against the hosted API. Read these with
the caveats: our latencies are measured on the serving host with no network hop, while the hosted numbers include
internet, TLS and queueing; hosted throughput depends on client concurrency and the API's rate limits; Jev's latency is
roughly flat in the number of questions per request, so bundling questions narrows the throughput gap; and our figures
are self-reported while Jev's come from third parties. The two throughput runs use the same benchmark but not an
identical call set (ours stops at 16 options).

## System 1: indistinguishable from TypeSafe Jev 1.13, by KL

**What the number means.** KL(Jev ‖ model) is the expected log-likelihood ratio, per sampled decision, between
TypeSafe Jev 1.13 and the student when the decision comes from Jev. On the 25,376 held-out rows whose targets are
Jev's own output distributions, the mean is ≈ 0.019 nats (computed from the per-slice values below, which are
published to three decimals): one decision carries almost no evidence about which of the two models produced it, and
an observer needs about 1 / KL ≈ 54 independent decisions to accumulate one nat (a likelihood ratio of about e ≈ 2.7 : 1).

For scale, Jev is not deterministic itself: an independent study found it changes its answer on 4.3 % of repeated,
identical 64-option calls, and it returns probabilities rounded to two decimals, which is the resolution of the
targets used here.

| Jev-labelled slice (`yuri_v3`, `test_set_30k`) | n | KL | ≈ decisions to gather one nat (1 / KL) |
|---|---|---|---|
| `noul` | 8,537 | 0.005 | ≈ 200 |
| `choice` | 8,312 | 0.028 | ≈ 36 |
| `score` | 8,527 | 0.023 | ≈ 43 |
| **all Jev-labelled rows** | **25,376** | **≈ 0.019** | **≈ 54** |

JEV-27B reaches ≈ 0.017 (≈ 60 decisions per nat) on the same rows.

The other test rows are not labelled by Jev and are not part of this claim: Open-Jev rows carry programmatic ground
truth (in-distribution KL 0.004 for `noul`, 0.176 for `choice`; 0.234 on the OOD split of unseen task families), and
the `yuri_v1` rows carry placeholder labels. No Jev-labelled out-of-distribution set exists in the corpus, so the claim
is established on the 53 training domains; outside them, the independent benchmark with human labels (90–97 % of Jev's
accuracy) is the best available evidence.

**Fidelity includes the teacher's mistakes.** On a poker spot where a solver always checks, TypeSafe Jev 1.13 shoves
with 0.62 in a published test; JEV-9B shoves too, with 0.70 (JEV-27B 0.63). A faithful copy of System 1 is also a
faithful copy of its blind spots. At 9 B the student also adds some of its own: on an independent benchmark 11.5 % of
its 16-option answers change when only the option order changes, against 7.0 % for the teacher (JEV-27B 7.4 %).

## The Blocks of Experts recipe

```
                          ┌── System 2 block: lm_head (248,320 × 4096) ───────► text generation and reasoning
Request ─► Router ─► Qwen3.5-9B backbone (frozen, bit-identical to the base)   (adapter off; HumanEval 70.7 % = base)
            per      │
          request    └── + System 1 block: LoRA (40.1 M) + 24-slot head (98 k) ─► calibrated typed decision
                         (adapter on, decision path only)                          (one prefill pass; KL ≈ 0.019 to Jev)
```

| block | what it is | parameters | trained? | used for |
|---|---|---|---|---|
| Backbone | `Qwen/Qwen3.5-9B` text tower (vision tower and MTP head dropped), bf16 | 7.9 B | no — bit-identical to the base | both systems |
| **System 2 block** | the original `lm_head` (248,320 × 4096) | part of the base | no | text generation and step-by-step reasoning |
| **System 1 block** | LoRA r=16 on the decoder projections + a 24-slot fp32 decision head initialised from `lm_head` rows | 40.1 M + 98 k | yes, ≈ 3 B200-hours | calibrated typed decisions |
| Router | per request: the vLLM LoRA module `jev-decision`, or `peft` adapter on/off | — | — | chooses the system |

**Why separate blocks rather than one merged fine-tune.** Folding the System 1 LoRA into the backbone would let a
single weight set serve both heads, but it costs generation quality: the merged backbone with the original `lm_head`
scores 61.6 % (101/164) on HumanEval against 70.7 % for the base, a 9-point drop, even though prose perplexity barely
moves (3.15 → 3.30). Keeping the backbone pristine and applying the System 1 block only on the decision path removes
that trade-off. For decision serving the adapter is merged *in memory* at start-up, so decision latency matches a
merged bundle.

**Why the recipe is this efficient.**

1. **Pretraining does most of the work; distillation sharpens.** The decision head is initialised from the backbone's
   own `lm_head` rows for the verbalizer tokens (`false/true`, `0`–`5`, `A`–`P`), so at step 0 its output equals the
   pretrained model's zero-shot restricted next-token distribution (verified to |Δp| < 1e-5; measured 8.6e-07). Before
   seeing a single label it already agrees with the test targets on 53 % of `choice` questions with `noul` AUROC 0.82;
   distillation takes it to 90 % / 0.996.
2. **Small trainable footprint.** 40.2 M parameters — 0.5 % of the backbone. Validation KL was already below 0.10 after
   the first 64 k rows, test KL reached 0.028 after 0.49 epoch (≈ 1.7 B200-hours) and 0.021 after 0.93 epoch.
3. **Transfer to unseen tasks.** The pretrained backbone reads the *content* of a new task instead of matching surface
   patterns of the training domains: KL 0.234 and top-1 0.918 against the programmatic labels of the OOD split. It
   also reads real, long, structured states (prose, JSON game states, policy documents; up to 856 tokens in the corpus).
4. **Reads options, not positions.** With 30 % option-permutation augmentation, the top-1 flip rate under shuffled
   `choice` options is 3.9 %; the same backbone before distillation flips 38 % of the time.
5. **Calibration falls out of the objective.** Distilling full teacher distributions with KL (plus an ordinal RPS term
   for `score`) gives fitted temperatures of 1.002 / 0.984 / 1.012 and ECE 0.0007 with no post-hoc correction.
6. **It scales without code changes, and scale pays off.** The same code, hyper-parameters and packaging produced the
   second-generation JEV-27B; only `model_path` and memory settings changed (the head-initialisation identity holds
   there too, 4.5e-07). Going from 9 B to 27 B lowers KL to Jev from ≈ 0.019 to ≈ 0.017, halves OOD KL
   (0.234 → 0.104), and raises the System 2 path from 70.7 % to 78.0 % on HumanEval.

## Benchmark highlights

### Independent benchmark: side by side with TypeSafe Jev 1.13

[`gazelle93/decision-models-under-pressure`](https://github.com/gazelle93/decision-models-under-pressure) (published
25 Sep 2026) asks decision models to pick the right label for real texts from CLINC-150, MTOP, GoEmotions, DBpedia and
financial tweets under three kinds of pressure: more options, near-miss options, and shuffled option order. The labels
are human gold labels, none of this data is in our training set, and TypeSafe Jev 1.13's results are published with it.
We re-ran the same items with autotrust/JEV-9B and autotrust/JEV-27B, up to our 16-option limit.

| | TypeSafe Jev 1.13 (published) | **autotrust/JEV-9B** | autotrust/JEV-27B |
|---|---|---|---|
| Accuracy with 2 / 4 / 8 / 16 options (800 items, 4 domains) | 0.890 / 0.801 / 0.782 / 0.769 | **0.868 / 0.774 / 0.735 / 0.694** | 0.876 / 0.784 / 0.767 / 0.740 |
| 16 options — CLINC / DBpedia / GoEmotions / MTOP | 0.945 / 0.900 / 0.470 / 0.760 | **0.875 / 0.855 / 0.325 / 0.720** | 0.930 / 0.885 / 0.415 / 0.730 |
| 16 options, near-miss vs. unrelated wrong options (CLINC + MTOP, 400 items) | 0.912 vs 0.985 | **0.875 vs 0.975** | 0.907 vs 0.983 |
| Answers changed by shuffling the options alone (16 options, 5 orderings) | 7.0 % | **11.5 %** | 7.4 % |
| Time for 14,400 decisions on one B200 | — | **42 s** | 110 s |

On data it was never trained on, JEV-9B reaches 97 % of the teacher's accuracy with 2 and 4 options, 94 % with 8 and
90 % with 16: it falls behind faster than JEV-27B (96–98 %) as the option list grows, loses a little more on near-miss
options, and is more sensitive to option order than the teacher. Our run follows the benchmark's published method (gold
plus the first K−1 distractors of a pool, shuffled per item); the orderings are seeded differently, so compare
aggregates, not individual items.

### Fresh examples (Hacker News and V2EX, 23–25 September 2026)

Expected answers were written by hand before the model was run. These are illustrations (≈ 110 decisions), not a
benchmark.

| task | autotrust/JEV-9B | autotrust/JEV-27B |
|---|---|---|
| Topic of 19 HN front-page stories (10 options) + "is it about AI?" | **38 / 38** | 38 / 38 |
| 12 comments from a heated HN thread: "insults or attacks someone?" + "what is it mainly doing?" (6 options) | **22 / 24** | 23 / 24 |
| 10 V2EX hot posts in **Chinese**: "contains a referral / invite code?" + "promotes a product or paid offer?" | **18 / 19** | 19 / 19 |
| Community use cases: code-rule checks in the style of `adhere`, injection filtering, ticket routing, phishing, code-review diffs, urgency scores | **14 / 15** | 15 / 15 |

| input | question | autotrust/JEV-9B |
|---|---|---|
| HN: "Two-tier encryption in the UK" | topic (10 options) | security & privacy · 0.87 |
| HN: "Using LLMs to trace alchemical knowledge and decode 17th century letters" | about AI? | P(true) = 0.88 |
| HN comment: "Please stop this. We've asked you before to observe the guidelines…" | what is it mainly doing? | moderating the discussion · 0.78 |
| V2EX: "一个不需要 gemini pro 的完全免费的注册 Muse 的方法 … 邀请码：…" | contains a referral / invite code? | P(true) = 1.00 |
| V2EX: "今天中秋节，还要加班的有吗？来报道下" | promotes a product or paid offer? | P(true) = 0.01 |
| Diff replacing a parameterised query with `"… WHERE id = " + request.args["id"]` | introduces a security vulnerability? | P(true) = 0.93 (0.17 for a variable rename) |
| "I'm not happy with the fit. What are my options here?" | asking for a refund? | P(true) = 0.17 (TypeSafe's docs report 0.22 for Jev on this exact text) |

Where it failed or wavered:

* **Code-rule check**: missed a TypeScript file that declares `const port: number = Number(process.env.PORT)` against
  the rule "a port must be a branded, range-checked integer" (0.33); JEV-27B flags it (0.93).
* **Fraud screening**: a CEO wire-transfer (business-email-compromise) message is flagged, but only at 0.56 (JEV-27B 0.84).
* **Comment intent**: "Because it's not a real argument. It's a deflection people use." read as attacking another
  commenter (0.66) rather than arguing a point.
* **Chinese promotion**: a V2EX post launching a paid HTTPS debugging tool was not flagged as promotional (0.44;
  JEV-27B 0.77).
* **A poker spot with the nuts** (check or shove four times the pot; a solver checks 100 %): shoves with 0.70; the
  teacher shoved with 0.62, so this mistake comes from the teacher.
* Counting ("more than 3 fruits?" / "more than 5?" for a list of 4: 0.84 / 0.37), date comparisons and an instruction
  injected inside the state were handled correctly, but on a handful of examples only.

Per-example outputs and the benchmark aggregates are in `reports/realworld_9b.json` (the HN and V2EX inputs came from
their public APIs on 25 September 2026).

## Quickstart with vLLM (recommended)

**One vLLM engine serves both systems from the same pristine weights.** Ordinary requests go through the base
`lm_head` (System 2, exactly Qwen3.5-9B); requests addressed to the LoRA module `jev-decision` go through the decision
head (System 1). `adapter_vllm/` contains the backbone LoRA plus the 24-slot decision head re-expressed as an `lm_head`
LoRA (only the 24 verbalizer rows change), so a typed decision is a single prefill step with `max_tokens=1`,
constrained to the option tokens and read back as log-probabilities.

### 1 — Start the server (OpenAI-compatible)

```bash
hf download autotrust/JEV-9B --local-dir JEV-9B            # ~18 GB
vllm serve JEV-9B --served-model-name autotrust/JEV-9B \
    --enable-lora --max-lora-rank 32 --lora-modules jev-decision=JEV-9B/adapter_vllm \
    --logprobs-mode processed_logprobs --max-model-len 4096
```

`--logprobs-mode processed_logprobs` is required: it makes the returned log-probabilities respect `allowed_token_ids`.
`--max-model-len 4096` is sized for decisions; raise it (for example to 16384) if System 2 requests will think at
length. Add `--enable-prefix-caching --mamba-cache-mode align` if you ask many questions about the same state.

### 2 — System 2: generation and reasoning (the unmodified base model)

```bash
curl -s localhost:8000/v1/chat/completions -H 'content-type: application/json' -d '{
  "model": "autotrust/JEV-9B",
  "messages": [{"role": "user", "content": "In one sentence, what is safety stock?"}],
  "max_tokens": 60, "chat_template_kwargs": {"enable_thinking": false}}'
```

Set `"enable_thinking": true` for deliberate, step-by-step reasoning. This path is Qwen3.5-9B unchanged; see the
[Qwen3.5-9B model card](https://huggingface.co/Qwen/Qwen3.5-9B) for its reasoning benchmarks and recommended sampling
settings.

### 3 — System 1: typed decisions (Python, only `requests` + two small JSON files)

```python
import json, math, requests
from huggingface_hub import hf_hub_download

REPO, URL = "autotrust/JEV-9B", "http://localhost:8000"
dh = json.load(open(hf_hub_download(REPO, "adapter_vllm/decision_head.json")))  # bias + verbalizer token ids
T  = json.load(open(hf_hub_download(REPO, "calibration.json")))["per_kind"]       # per-kind temperatures

def decide(kind, state, question, options=None):
    options = {"noul": ["false", "true"], "score": [str(i) for i in range(6)]}.get(kind, options)
    lines = options if kind != "choice" else [f"{'ABCDEFGHIJKLMNOP'[i]}) {o}" for i, o in enumerate(options)]
    prompt = f"[kind] {kind}\n[state] {state}\n[question] {question}\n[options]\n" + "\n".join(lines) + "\n[decision]:"
    s = dh["slots"]["ranges"][kind][0]
    ids = dh["verbalizer_ids"][s : s + len(options)]              # the option tokens of this kind
    r = requests.post(f"{URL}/v1/completions", json={
        "model": "jev-decision", "prompt": prompt, "max_tokens": 1, "temperature": 1.0,
        "logprobs": len(options), "allowed_token_ids": ids,
        "add_special_tokens": False, "return_tokens_as_token_ids": True}).json()
    lp = {int(k.split(":")[1]): v for k, v in r["choices"][0]["logprobs"]["top_logprobs"][0].items()}
    z = [(lp.get(t, -1e9) + dh["bias"][s + i]) / T[kind] for i, t in enumerate(ids)]   # + head bias, / temperature
    e = [math.exp(x - max(z)) for x in z]
    return {o: x / sum(e) for o, x in zip(options, e)}

print(decide("choice", "SKU AX-330 stock at 8% of safety level; supplier late twice this quarter.",
             "Supplier response for this scenario.", ["issue_warning", "renegotiate", "dual_source", "maintain"]))
# ≈ {'issue_warning': 0.33, 'renegotiate': 0.14, 'dual_source': 0.53, 'maintain': 0.001}
print(decide("noul", "Customer says the parcel arrived damaged and wants their money back.",
             "Is the customer asking for a refund?"))
```

Values can differ in the third decimal between runs: vLLM computes in bf16 and results depend slightly on which
requests are batched together. The head bias and the temperature are applied client-side; the log-softmax normaliser
that vLLM applies cancels out, so the result is exactly the decision head's calibrated distribution.

### 4 — System 1 → System 2: confidence-gated escalation

Because both systems live in one engine, a common pattern is to let System 1 answer when it is confident and hand the
rest to System 2. This is a usage pattern, not a configuration we have benchmarked; pick the threshold on your own
validation data, and serve with a `--max-model-len` large enough for the reasoning budget.

```python
def solve(state, question, options, threshold=0.90):
    p = decide("choice", state, question, options)             # System 1: one prefill pass
    best = max(p, key=p.get)
    if p[best] >= threshold:
        return {"system": 1, "answer": best, "distribution": p}
    prompt = (f"{state}\n\nQuestion: {question}\nOptions: " + "; ".join(options)
              + "\nThink it through, then give exactly one option on the last line.")
    r = requests.post(f"{URL}/v1/chat/completions", json={        # System 2: same engine, base lm_head
        "model": "autotrust/JEV-9B",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 8192, "chat_template_kwargs": {"enable_thinking": True}}).json()
    return {"system": 2, "reply": r["choices"][0]["message"]["content"], "system1_distribution": p}
```

### Offline / batch (Python API)

```python
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest

llm = LLM("JEV-9B", enable_lora=True, max_lora_rank=32, logprobs_mode="processed_logprobs", max_model_len=4096)
decision = LoRARequest("jev-decision", 1, "JEV-9B/adapter_vllm")

gen = llm.generate(["..."], SamplingParams(temperature=0.0, max_tokens=256))            # System 2, no LoRA
dec = llm.generate([prompt], [SamplingParams(max_tokens=1, temperature=1.0,             # System 1
                                              allowed_token_ids=ids, logprobs=len(ids))],
                   lora_request=decision)                                               # then + bias, / T as above
```

Mixed batches work too: pass a per-request `lora_request` list (`None` for System 2, `decision` for System 1) and both
systems are served in the same `generate` call.

### Measured on one B200

| workload | PyTorch path | **vLLM** |
|---|---|---|
| System 2 — 164 HumanEval completions (greedy, ≤ 384 new tokens) | 165 s | **3.3 s** (≈ 50×) |
| System 1 — offline batch, 29,955 test questions | 75 s (398 q/s) | 80 s (374 q/s) |
| System 1 over HTTP — 64 / 256 concurrent clients | — | 150 / 205 req/s |
| System 1 fidelity vs. the PyTorch path | test KL 0.0210 | test KL 0.0211; mean \|Δp\| 0.0008 over HTTP |
| Many questions about one state, `--enable-prefix-caching` | — | +14–20 % throughput |

Notes:
* The big win is on System 2: generation is ≈ 50× faster. A decision is a single prefill pass with no decoding, so at
  9 B offline batch throughput is about the same as the PyTorch path (at 27 B vLLM is 1.7× faster); for System 1 vLLM
  mainly buys serving: continuous batching under concurrency, an OpenAI-compatible API, and one engine for both systems.
* Prefix caching: this architecture mixes Gated DeltaNet and attention layers, and vLLM caches it in blocks of 528
  tokens, so only shared prefixes longer than 528 tokens are reused. The template puts `[kind]` before `[state]`, so
  only questions of the same kind share a prefix. On 293 real states × 7.7 yes/no questions each (≈ 480-token states),
  prefix caching served 19.6 % of prompt tokens from cache (+14–20 % throughput) with identical outputs.
* Requires a vLLM build with Qwen3.5 (`qwen3_5`) support, LoRA on `lm_head`, `--logprobs-mode` and
  `allowed_token_ids`; tested with a vLLM development build from September 2026. Start-up takes 3–8 minutes
  (CUDA-graph capture with LoRA enabled).

## What System 1 does

| kind | question | returns |
|---|---|---|
| `noul` | "Is this statement true?" | `[P(false), P(true)]` |
| `choice` | "Which of these 2–16 options?" | one probability per option, aligned with your `options` |
| `score` | "Where on this ordered 0–5 scale?" | a distribution over the six levels (+ expected score) |

```
[kind] choice
[state] SKU AX-330 stock at 8% of safety level; supplier late twice this quarter.
[question] Supplier response for this scenario.
[options]
A) issue_warning
B) renegotiate
C) dual_source
D) maintain
[decision]:
```

The template is tokenised as one string; the last token's final-norm hidden state goes through a
**linear fp32 head `H → 24 slots`** (`noul` → slots 0–1, `score` → 2–7, `choice` → 8–23). Inactive slots are masked,
a per-kind temperature is applied, and a softmax yields the distribution aligned with your `options`. One prefill
pass, no decoding.

## Other ways to run it

### Plain `transformers` + `peft`

```python
import json, torch
from huggingface_hub import hf_hub_download
from peft import PeftModel
from safetensors.torch import load_file
from transformers import AutoModelForCausalLM, AutoTokenizer

repo = "autotrust/JEV-9B"
tok = AutoTokenizer.from_pretrained(repo)
base = AutoModelForCausalLM.from_pretrained(repo, dtype=torch.bfloat16, device_map="cuda")  # == Qwen3.5-9B text model

# --- System 2: the pristine base model, no adapter ----------------------------------------------
msgs = [{"role": "user", "content": "In two sentences, what is safety stock?"}]
enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True).to("cuda")
out = base.generate(**enc, max_new_tokens=80)
print(tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True))

# --- System 1: attach the LoRA adapter (merged here for speed) + the 24-slot head ---------------
model = PeftModel.from_pretrained(base, repo, subfolder="adapter").merge_and_unload()
head = load_file(hf_hub_download(repo, "head.safetensors"))
cfg  = json.load(open(hf_hub_download(repo, "judge_config.json")))
temp = json.load(open(hf_hub_download(repo, "calibration.json")))["per_kind"]
W, b = head["proj.weight"].cuda(), head["proj.bias"].cuda()

def decide(kind, state, question, options):
    letters = "ABCDEFGHIJKLMNOP"
    lines = options if kind != "choice" else [f"{letters[i]}) {o}" for i, o in enumerate(options)]
    text = f"[kind] {kind}\n[state] {state}\n[question] {question}\n[options]\n" + "\n".join(lines) + "\n[decision]:"
    ids = tok(text, return_tensors="pt", add_special_tokens=False).to("cuda")
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        h = model.model(**ids).last_hidden_state[0, -1].float()          # backbone only, last token
    z = (W @ h + b) / temp[kind]
    s, _ = cfg["slots"]["ranges"][kind]
    p = torch.softmax(z[s : s + len(options)], 0)
    return dict(zip(options, p.tolist()))

print(decide("noul", "Customer says the parcel arrived damaged and wants their money back.",
             "Is the customer asking for a refund?", ["false", "true"]))
# {'false': 0.009, 'true': 0.991}
```

`options` are validated: `noul` must be `["false","true"]`, `score` must be `["0".."5"]`, `choice` takes 2–16
free-text options. Note that `merge_and_unload()` above changes the backbone for the rest of the process; to keep both
systems in one process, leave the adapter unmerged and run System 2 inside `with model.disable_adapter():`.

## Evaluation details

### Additional System 1 metrics (`test_set_30k`, temperature applied)

| metric | autotrust/JEV-9B |
|---|---|
| `noul` Brier score against the target probability, all rows (lower is better) | 0.0015 |
| `score` ranked probability score (lower is better) | 0.0085 |
| Fitted temperatures noul / choice / score | 1.002 / 0.984 / 1.012 |
| Top-1 flip rate when `choice` options are shuffled (1,000 rows × 4 permutations) | 3.9 % |
| Out-of-distribution split — top-1 agreement · `noul` AUROC | 0.918 · 0.989 |
| Throughput — batch of 128 requests on one B200 | 2.5 ms per decision (≈ 400 decisions/s) |
| Single request on one B200 (median) | 87 ms |

### System 2 — no-degradation check (HumanEval, greedy pass@1, completion-style prompt)

| weights | pass@1 | note |
|---|---|---|
| Qwen3.5-9B (base) | 70.7 % (116/164) | same loader and protocol as below |
| **autotrust/JEV-9B — System 2 path (backbone + `lm_head`, adapter off)** | **70.7 % (116/164)** | all 164 completions byte-identical to the base model |
| System 1 LoRA folded into the backbone + base `lm_head` (*not shipped*) | 61.6 % (101/164) | why the blocks are kept separate |

### Per source × primitive (`test_set_30k`, temperature applied)

| source | kind | n | KL | top-1 | ECE | noul AUROC | score MAE |
|---|---|---|---|---|---|---|---|
| yuri_v3 — synthetic operational scenarios, labelled by TypeSafe Jev 1.13 | noul | 8,537 | 0.005 | 0.961 | 0.001 | 0.994 | — |
| yuri_v3 | choice | 8,312 | 0.028 | 0.902 | 0.002 | — | — |
| yuri_v3 | score | 8,527 | 0.023 | 0.883 | 0.002 | — | 0.103 |
| openjev_v2 — Open-Jev programmatic tasks, ground-truth labels (not Jev) | noul | 1,432 | 0.004 | 0.998 | 0.003 | 1.000 | — |
| openjev_v2 | choice | 887 | 0.176 | 0.857 | 0.020 | — | — |
| yuri_v1 — placeholder `[0.5, 0.5]` labels (see Limitations) | noul | 2,260 | 0.000 | — | 0.005 | — | — |

OOD split (13,058 Open-Jev rows from task families not in training, programmatic labels): KL 0.234, top-1 0.918, noul
AUROC 0.989; `choice` KL 0.351 / top-1 0.837 (game-state decisions are the hardest slice).

Choice option-permutation consistency (1,000 rows × 4 random permutations): mean max |Δp| 0.024, p90 0.055, top-1
flip rate 3.9 %.

### Training trajectory (most recent first)

Validation KL on a fixed 4 k-row subset; `test_set_30k` metrics after calibration.

| stage | rows seen | val KL | t30k KL | choice top-1 | score MAE | noul AUROC | ECE |
|---|---|---|---|---|---|---|---|
| **autotrust/JEV-9B v0.8.0 — released weights (4,750 steps ≈ 0.93 epoch, LR annealed to ≈ 0.07×)** | 608 k | **0.019** | **0.0210** | **0.898** | **0.103** | **0.996** | **0.0007** |
| v0.7.0 (step 2000 + 500-step LR cool-down) | 320 k | 0.026 | 0.0276 | 0.884 | 0.119 | 0.994 | 0.0014 |
| step 2000 | 256 k | 0.0325 | 0.037 | 0.865 | 0.143 | 0.992 | 0.004 |
| step 1500 | 192 k | 0.038 | 0.040 | 0.861 | 0.151 | 0.991 | 0.0025 |
| step 500 | 64 k | 0.094 | 0.081 | 0.817 | 0.224 | 0.977 | 0.022 |
| untrained backbone with the initialised head (reference point, not the model) | 0 | 0.485 | 0.510 | 0.532 | 1.130 | 0.824 | 0.094 |

Annealing matters: the v0.7.0 cool-down (500 steps, lr ×0.9 → ×0.02 from step 2000) lowered KL by 25 %; continuing on
the unseen remainder of the epoch with the learning rate decayed to ≈ 0.07× (v0.8.0) lowered it by another 24 % and
added 1.4 points of choice agreement. JEV-27B folds this into a single cosine schedule.

## Training details

| item | value |
|---|---|
| teacher / data | `SargeDev/jev-distill-corpus-v3` (740,957 rows; `train` 655,806) with three streams: `yuri_v3` (498,010 rows, TypeSafe Jev 1.13 full output distributions via OpenRouter), `openjev_v2` (94,801 rows, Open-Jev programmatic labels, CC0), `yuri_v1` (148,154 rows, placeholder labels, down-weighted) |
| backbone | `Qwen/Qwen3.5-9B` text tower only (vision tower and MTP head dropped), bf16, frozen |
| System 1 block (trainable) | LoRA r=16, α=32, dropout 0.05 on `in_proj_qkv, in_proj_z, out_proj, q/k/v/o_proj, gate/up/down_proj` (40.1 M, shipped unmerged in `adapter/`) + 24-slot head (98 k, fp32, initialised from `lm_head` rows) |
| System 2 block | the original `lm_head`, not trained |
| loss | KL(target ‖ model) over active slots + 0.5 · RPS (ranked probability score) for `score` |
| augmentation | 30 % random permutation of `choice` options (targets permuted consistently) |
| batching | 128 rows / step, kind-stratified (≥ 1/6 per primitive), length-bucketed, micro-batches capped at 24 k padded tokens, gradient checkpointing |
| optimiser | AdamW (fused), β=(0.9, 0.98), lr head 2e-4 / LoRA 1e-4, cosine, warmup 3 %, grad-clip 1.0 for 2,500 steps; then continued on the unseen remainder of the epoch (fresh AdamW state, warmup 2 %, lr ×0.9 → cosine) and stopped after 2,250 more steps at lr ≈ ×0.07 — 4,750 steps ≈ 0.93 epoch in total |
| label hygiene | `yuri_v1` rows carry exact-uniform `[0.5, 0.5]` placeholder labels (137,203 rows, 100 %); down-weighted ×0.05 in training and excluded from temperature fitting |
| calibration | per-kind scalar temperature (L-BFGS on the `calibration` split, 10,954 rows): noul 1.002 · choice 0.984 · score 1.012 |
| compute | 1× NVIDIA B200 (183 GB); ≈ 1.4 h (2,500 steps) + ≈ 1.5 h (2,250 steps) ≈ 3 GPU-hours; ≈ 7–9 k tokens/s |
| software | torch 2.13 + cu130, transformers 5.16, peft 0.21, flash-linear-attention 0.5.2 |

## Limitations

* **System 1 mirrors TypeSafe Jev 1.13, including its mistakes.** This is a distillation, not an independent judge:
  where the teacher was wrong or uncalibrated, so is autotrust/JEV-9B. Published evaluations of the teacher show it is
  unreliable for multi-hop reasoning, arithmetic, dates, counting and adversarial inputs, and the student inherits all
  of that. Confirmed on fresh inputs: the poker shove (0.70 vs the teacher's 0.62).
* **At 9 B it adds some blind spots of its own.** 11.5 % of its 16-option answers change with option order alone
  (teacher 7.0 %), it keeps 90 % rather than 96 % of the teacher's accuracy at 16 options, and it missed a code-rule
  violation that JEV-27B catches. Prefer [autotrust/JEV-27B](https://huggingface.co/autotrust/JEV-27B) for long option
  lists, unfamiliar task families and code-rule checks.
* **The two systems are integrated in serving, not in knowledge.** System 1 cannot explain its decisions, and System 2
  is the unmodified base model: it knows nothing about the decisions it is packaged with and was not trained to agree
  with System 1. If you escalate from System 1 to System 2, expect them to disagree sometimes.
* **"Indistinguishable" is a KL statement on Jev-labelled rows from the 53 training domains.** The corpus has no
  Jev-labelled out-of-distribution set; the OOD figures (KL 0.234, 0.351 for game-state `choice`) are measured against
  programmatic ground truth, and on the independent benchmark the student reaches 90–97 % of Jev's accuracy, not 100 %.
* **Speed comparisons with the hosted API are not like for like.** Our timings exclude network time; the hosted
  figures are third-party measurements that include it and depend on client concurrency and rate limits.
* **Choice agreement is capped by teacher ambiguity.** The teacher's `choice` distributions are soft (median top-1
  probability 0.70). On the 14 % of rows where the teacher's top two options are within 0.1 of each other, argmax
  agreement is near chance for *any* faithful mimic (0.46 where the gap is < 0.05). On teacher-decisive rows agreement
  is 0.954, and the student's argmax captures 97.7 % of the teacher probability mass a perfect mimic could (0.693 vs
  0.709).
* **Fixed option sets.** `noul` and `score` accept only their canonical options; `choice` accepts 2–16 options. Inputs
  longer than 1,024 tokens are truncated (state only, head 60 % / tail 40 %) at serving unless you raise the limit.
* **English-centric.** The corpus is English; multilingual behaviour is inherited from the backbone and was not
  systematically measured (the Chinese V2EX examples above are illustrations only).
* **Placeholder labels in the corpus.** The `yuri_v1` memory-relevance stream is 100 % exact-uniform `[0.5, 0.5]` —
  those rows teach nothing about relevance. The model outputs ≈ 0.5 on them by design; do not use it for
  memory-relevance scoring without further training.
* **Not for high-stakes decisions.** Use confidence gating: act automatically only above a threshold you validated on
  your own data, and route the rest to System 2, a stronger model, or a human.

## Files

```
model-0000{1..5}-of-00005.safetensors   Qwen3.5-9B text backbone incl. lm_head — bit-identical to the base model
                                        (bf16; GDN A_log / gated-norm weights fp32 as in the original), 17.9 GB
model.safetensors.index.json · config.json
adapter/                                System 1 LoRA (peft format, r=16, 40.1 M params, 154 MB) — apply only for decisions
head.safetensors                        24-slot decision head (fp32): proj.weight [24, 4096], proj.bias [24]
judge_config.json                       slot layout, verbalizer token ids, template version, weights_mode=unmerged, provenance
calibration.json                        per-kind temperatures (+ fit diagnostics)
adapter_vllm/                           the same adapter for vLLM: backbone LoRA (zero-padded to r=32) + decision head as an
                                        lm_head LoRA, plus decision_head.json (head bias, verbalizer token ids)
tokenizer.json · tokenizer_config.json · chat_template.jinja
reports/                                evaluation reports: test-set evaluation, bundle checks, HumanEval per-problem
                                        results, vLLM measurements, real-world tests, training-milestone reviews
vl/                                     vision: serve.sh (multimodal Qwen3.5-9B + System 1), serve_decide.py (POST /v1/decide),
                                        adapter_vllm/ (layer names for the multimodal model), calibration.json, demos/
videos/                                 robot-arm and computer-use demo videos
reports/vl/                             image evaluations and demo results
```

## License and acknowledgements

Weights: **Apache-2.0** (base model `Qwen/Qwen3.5-9B` is Apache-2.0; training corpus
`SargeDev/jev-distill-corpus-v3` is Apache-2.0, its `openjev_v2` stream additionally CC0). The System One framing and
the `noul` / `choice` / `score` primitives originate with TypeSafe AI's Jev; autotrust/JEV-9B is an independent
student model trained on public data and shares no weights, code or affiliation with TypeSafe AI.

```bibtex
@misc{autotrust_jev9b_2026,
  title  = {autotrust/JEV-9B: the first integrated System 1 + System 2 open model built with the Blocks of Experts recipe (Qwen3.5-9B; System 1 distilled from TypeSafe Jev 1.13)},
  author = {{AutoTrust AI}},
  year   = {2026},
  url    = {https://huggingface.co/autotrust/JEV-9B}
}
```
