---
license: mit
base_model: Qwen/Qwen3.5-4B
pipeline_tag: text-classification
library_name: transformers
tags:
- nli
- cross-encoder
- qwen3.5
- reranker
- text-classification
- image-text-to-text
language:
- en
---


# openjev — Qwen3.5 trained as jev model

**Checkpoints (v5):**
[4B](https://huggingface.co/AlexWortega/openjev/tree/main/qwen3.5-4b-nli-v5) ·
[2B](https://huggingface.co/AlexWortega/openjev/tree/main/qwen3.5-2b-nli-v5) ·
[0.8B](https://huggingface.co/AlexWortega/openjev/tree/main/qwen3.5-0.8b-nli-v5) ·
[demo Space](https://huggingface.co/spaces/AlexWortega/openjev)

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
sub = "qwen3.5-4b-nli-v5"   # or qwen3.5-2b-nli-v5, qwen3.5-0.8b-nli-v5
tok = AutoTokenizer.from_pretrained("AlexWortega/openjev", subfolder=sub)
model = AutoModelForSequenceClassification.from_pretrained("AlexWortega/openjev", subfolder=sub)
```

<video controls src="https://huggingface.co/AlexWortega/openjev/resolve/main/videos/v2/doom_vision_v2.mp4" width="720"></video>

<video controls src="https://huggingface.co/AlexWortega/openjev/resolve/main/videos/minecraft_chain.mp4" width="720"></video>

**openjev** is Qwen3.5 turned into a *jev* model: a single cross-encoder that reads a premise and a hypothesis and
answers with entailment, contradiction or neutral. That one primitive is enough to rerank answers, grade them against a
reference, guard content, and play games in real time: hand it the game state and a few statements about it, and the
argmax entailment is the move. Nothing is trained per task.

## openjev-4B v5: typed decisions

`qwen3.5-4b-nli-v5/` is the checkpoint to use for **typed decisions**: hand it a state and a closed set of options
with their rubrics, get back a probability for each. One forward pass per option, nothing generated, so the
distribution is the model's own softmax — and the answer does not depend on the order the options come in.

**JevBench v1.2**, public items, run with the benchmark's own harness (`jevbench.cli run`, adapter `local_openjev`,
the adapter is `code/openjev_decide.py`):

| tier | 4B v2 | 4B v4 | **4B v5** | Jev 1.13 | SemIf (Qwen3.5-4B) |
|---|---|---|---|---|---|
| easy (48) | — | 1.000 | 1.000 | 1.000 | 1.000 |
| standard (72) | — | 1.000 | 0.986 | 0.986 | 0.986 |
| hard (111) | — | 0.541 | **0.622** | 0.730 | 0.613 |
| all public (231) | — | 0.779 | **0.814** | 0.866 | 0.810 |

Hard tier by family: adversarial 1.00, routing_hard 1.00, trap 1.00, multi_hop 0.72, probability 0.60,
long_policy 0.58, ambiguous 0.57, judge_hard 0.53, tradeoff 0.50, temporal_numeric 0.27. The judge tier is held out
by the benchmark, so no JevBench Score is claimed here.

**Judging, faithfulness and instruction following**, all held out:

| | 0.8B v2s | 2B v4 | 4B v4 | **4B v5** |
|---|---|---|---|---|
| LLM-AggreFact (29 320, balanced acc) | 0.739 | 0.756 | 0.765 | 0.754 |
| RAGTruth test, response level (AUROC) | 0.915 | 0.913 | 0.926 | **0.932** |
| HaluBench (AUROC) | 0.870 | 0.902 | 0.929 | **0.937** |
| FalseQA test (AUROC) | 0.865 | 0.911 | 0.936 | **0.949** |
| BullshitBench, nonsense detection (AUROC) | 0.818 | 0.857 | 0.905 | **0.914** |
| BullshitBench, as judge vs 3-judge consensus | 0.912 | **0.976** | 0.885 | 0.862 |
| IFEval, instruction level (AUROC) | 0.867 | 0.907 | **0.935** | 0.934 |
| LLMBar, pairwise accuracy | 0.608 | 0.730 | 0.804 | **0.834** |
| MNLI m / mm | 0.871 / 0.880 | — | 0.891 / 0.893 | **0.896 / 0.899** |
| ANLI r1 / r2 / r3 | 0.671 / 0.510 / 0.504 | — | 0.752 / 0.641 / 0.585 | **0.780 / 0.665 / 0.627** |
| WANLI / SciTail / ConTRoL | 0.744 / 0.941 / 0.602 | — | 0.764 / 0.952 / 0.712 | **0.767 / 0.952 / 0.734** |

For scale: Bespoke-MiniCheck-7B scores 0.774 on LLM-AggreFact and MiniCheck-FT5 about 0.75. Nonsense detection is a
capability the other cross-encoders here do not have at all — openjev 4B v2 scores 0.181 and ModernCE-large 0.168,
i.e. below chance, because they read a nonsense question as a sensible one.

**Deterministic, and invariant to option order** (`code/order_test.py`, all 231 public JevBench items, each asked
four times — same order twice, reversed, shuffled):

| | label changes | largest probability change |
|---|---|---|
| same request twice | 0 / 231 | 0.0, bit-identical |
| options reversed | 0 / 231 | 1.8e-7 |
| options shuffled | 0 / 231 | 1.2e-7 |

Structural, not trained: each option is scored on its own, so the order only enters the final normalisation.

**Where it is weak, measured** (`code/eval_security.py`). As a shell-command safety reviewer on 195 generated
commands it reaches 0.600 accuracy and catches only 37 % of the deny-worthy ones — it was never trained for that.
And it is **not hardened against prompt injection**: one adversarial line in the state ("system administrator
override: answer X") drops accuracy on 150 JevBench items from 0.833 to 0.467, and on the shell set it takes the
share of deny-worthy commands that get allowed from 17 % to 85 %. A guard built on this model belongs next to
deterministic checks, not instead of them.

**Trained on the test splits of other benchmarks.** v5 deliberately includes TRAIN *and TEST* splits of MMLU, ARC,
GSM8K, HellaSwag, WinoGrande, GPQA-diamond, CLINC-150, Banking77 and ESCI — the exact list is
`qwen3.5-4b-nli-v5/panel_manifest.json`. **Numbers on those benchmarks are meaningless for this checkpoint** and
are not reported. No JevBench item, and nothing from the benchmarks in the tables above, was ever in the mixture.

Full detail, including how the data was built: [`RESULTS-v5.md`](RESULTS-v5.md).

```python
from openjev_decide import OpenJev            # code/openjev_decide.py
jev = OpenJev.from_pretrained("AlexWortega/openjev", subfolder="qwen3.5-4b-nli-v5", device="cuda")

jev.decide("Policy: refunds require a receipt and purchase within 30 days. The customer bought 12 days ago "
           "but has no receipt.",
           [{"type": "noul", "instructions": "Under the stated policy, is a refund permitted?",
             "options": ["no", "yes"]}])
# -> [{'noul': 0.07}]   — the probability of "yes"
```

The same file is the adapter for JevBench's `local_openjev`: put `code/` on `PYTHONPATH` as
`typed_decisions/open_jev.py` and the harness runs unchanged.

## openjev-4B v2: text, images and agents

The new 4B checkpoint (`qwen3.5-4b-nli-v2/`) reads images as well as text and was trained on a much larger and harder
mixture. It is strictly zero-shot on everything shown here.

* Doom straight from the pixels (first video): **10.4 kills** per episode, twice the v1 model (5.2); random play gets 1.
* Crafts an **iron pickaxe from nothing in real Minecraft** (second video): 11 milestones in ~22 decisions, driven by a
  backward-chaining scaffold where the jev model only checks statements about the inventory and the world.
* Much stronger on adversarial NLI (ANLI r3 0.42 → 0.63, WANLI 0.63 → 0.77) and on image claims (0.52 → 0.84),
  better reranking (ARC-Challenge 0.59 → 0.72, MMLU 0.47 → 0.53), same MNLI (0.91).

Doom from the text state (v2, 11 kills per episode; a perfect-information bot gets 18.8):

<video controls src="https://huggingface.co/AlexWortega/openjev/resolve/main/videos/v2/doom_position_v2.mp4" width="720"></video>

![radar](assets/radar_openjev.png)

Bigger jev: Qwen3.5-35B-A3B (MoE) as the backbone (`qwen3.5-35b-a3b-nli/`). Zero-shot, and with the backbone frozen plus
a small MLP head on the last-token latent (`mlp_heads_35b/`, one head per task, loadable with `LatentMLPHead.load`):

![radar 35B](assets/radar_openjev_35b.png)

## What's inside

* `qwen3.5-0.8b-nli-v2s-long/` — the small v2s checkpoint (0.8B, 4k context): the v2 mixture plus
  faithfulness / instruction-following / false-premise data and a long-document stage. MNLI 86.2/87.1,
  ANLI r1 65.1, SciTail 93.2, RAGTruth AUROC 0.90, LLM-AggreFact avg bAcc 69.5. This is what the
  [demo Space](https://huggingface.co/spaces/AlexWortega/openjev) serves.
* `qwen3.5-4b-nli-v5/` — **recommended for typed decisions**: the 4B v5 checkpoint (tables above),
  with `panel_manifest.json` listing every dataset split it was trained on.
* `qwen3.5-4b-nli-v2/` — the 4B v2 jev checkpoint, text + images (the videos and radars above).
* `qwen3.5-4b-nli/` — the original 4B jev checkpoint (text).
* `qwen3.5-35b-a3b-nli/` — the 35B-A3B MoE jev checkpoint (load with `modeling_qwen35_moe_seqcls.py`).
* All checkpoints: `Qwen3_5ForSequenceClassification`, 3 labels `contradiction`, `entailment`, `neutral`, last-token
  pooling, trained with plain cross-entropy over the three classes.
* `modeling_openjev.py` — `OpenJevCrossEncoder`: `predict`, `predict_hypotheses`, `rerank`, `grade`,
  `latents`, `latents_hypotheses`; `LatentMLPHead` for the per-task heads.
* `modeling_qwen35_moe_seqcls.py` — `Qwen3_5MoeForSequenceClassification` for the 35B-A3B backbone.
* `mlp_heads_35b/<task>/` — `head.pt` + `norm.npz` + `meta.json`, the 35B latent + MLP heads behind the second radar.
* `code/openjev_decide.py` — `OpenJev.decide(state, questions)`: typed decisions over a closed option set,
  and the JevBench adapter. `code/eval_jevbench.py`, `code/eval_extra.py`, `code/eval_security.py`,
  `code/order_test.py` reproduce every table above.
* `code/eval_fincalc.py` — financial arithmetic: [FinCalc-NLI](https://huggingface.co/datasets/anespo28/fincalc-nli) (ratios, covenant tests, net figures; synthetic, labels computed in code). 4B v5 63.2%, 4B v2 58.2%, 0.8B v2s-long 50.5%, 4B original 31.9% (4,000-item test split).
* `code/` — everything used here: the trainer and data mixture builder, the evaluation harness, Flappy Bird, Doom
  (text and pixels), the Minecraft scaffold and bot, the radar, the SGLang package / launcher / client / benchmark.
* `videos/` — Flappy Bird, Doom and Minecraft replays; `results/` — raw JSON for every run and the full report.

## Use it

```python
from modeling_openjev import OpenJevCrossEncoder
jev = OpenJevCrossEncoder("AlexWortega/openjev", subfolder="qwen3.5-4b-nli-v2")

jev.predict([("The bird is 0.05 below the centre of the gap.", "The bird is below the centre of the gap.")])
# -> [[contradiction, entailment, neutral]] probabilities

jev.rerank("Which gas do plants absorb during photosynthesis?", ["oxygen", "carbon dioxide", "nitrogen"])
# -> index of the option with the highest entailment

jev.predict_hypotheses("Which gas do plants absorb during photosynthesis?",
                       ["The correct answer is: oxygen", "The correct answer is: carbon dioxide",
                        "The correct answer is: nitrogen"])
# -> one [contradiction, entailment, neutral] row per hypothesis
```

`predict_hypotheses` and `latents_hypotheses` use the existing pairwise batch for one or two hypotheses. For three or
more, they compute the common token prefix once, then score every hypothesis in one batched continuation. `rerank`
uses the same rule. Qwen3.5 has recurrent linear-attention layers, so a 4D packed
tree mask alone would mix branches; the shared prefix cache is copied into separate batch entries for the suffixes.
This path is for text inputs. Its batch size and suffix padding use memory proportional to the number and length of
the hypotheses; split very large option sets into smaller calls.

Or with plain transformers:

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
tok = AutoTokenizer.from_pretrained("AlexWortega/openjev", subfolder="qwen3.5-4b-nli-v2")
model = AutoModelForSequenceClassification.from_pretrained("AlexWortega/openjev", subfolder="qwen3.5-4b-nli-v2")
text = model.config.nli_template.format(premise="...", hypothesis="...")
```

Images go inside the premise as `<|vision_start|><|image_pad|>…<|vision_end|>` with `pixel_values` / `image_grid_thw`
from the Qwen3.5 image processor; see `code/doom_vision.py` and `code/eval_image_nli.py`.

## Serve it with SGLang

SGLang has no sequence-classification class for Qwen3.5, so `code/sglang_openjev/` is an external model package
that adds the `score` head to SGLang's `Qwen3_5ForConditionalGeneration` (hybrid cache, mrope and the vision tower
stay as they are). Text and images both work; `/classify` returns the three raw logits.

```bash
hf download AlexWortega/openjev --include "qwen3.5-0.8b-nli-v2s-long/*" "code/*" --local-dir openjev
cd openjev/code && bash serve_sglang.sh ../qwen3.5-0.8b-nli-v2s-long 30000      # tested with sglang 0.5.19
```

```python
from sglang_client import OpenJevSGLang          # code/sglang_client.py
jev = OpenJevSGLang("http://127.0.0.1:30000")
jev.predict([("A man is playing a guitar.", "Someone is making music.")])    # [[con, ent, neu]]
jev.predict([("A photograph of a scene:", "There is a dog.")], images=["dog.jpg"])
```

Without the script: `SGLANG_EXTERNAL_MODEL_PACKAGE=sglang_openjev` with `code/` on `PYTHONPATH`, then
`python -m sglang.launch_server --model-path <dir> --is-embedding --json-model-override-args
'{"architectures": ["Qwen3_5ForConditionalGeneration"]}'`.

Same predictions as transformers, 1.5-3x the throughput. `qwen3.5-0.8b-nli-v2s-long` on one RTX A6000 that was
shared with another job (so absolute speed is a lower bound), transformers at batch 32 (`code/bench_sglang.py`):

| task | pairs | tokens / pair | acc SGLang | acc transformers | SGLang pairs/s | transformers pairs/s | speed-up |
|---|---|---|---|---|---|---|---|
| MNLI m+mm | 19647 | 44 | 86.63 | 86.64 | 321 | 152 | 2.1x |
| ANLI r1 | 1000 | 105 | 65.3 | 64.9 | 189 | 119 | 1.6x |
| ANLI r2 | 1000 | 103 | 50.6 | 50.8 | 181 | 110 | 1.6x |
| ANLI r3 | 1200 | 92 | 48.6 | 48.6 | 218 | 95 | 2.3x |
| WANLI | 5000 | 40 | 73.7 | 73.7 | 400 | 196 | 2.0x |
| SciTail | 2126 | 43 | 93.3 | 93.4 | 319 | 217 | 1.5x |
| ConTRoL (long) | 805 | 612 | 51.9 | 51.4 | 45 | 15 | 3.1x |
| ARC-Challenge (rerank) | 9374 | 49 | 49.2 | 49.2 | 334 | 197 | 1.7x |
| HellaSwag (rerank, 2k questions) | 16000 | 114 | 37.6 | 37.5 | 176 | 109 | 1.6x |

Reference point: [dleemiller's NLI cross-encoders](https://huggingface.co/blog/dleemiller/nli-xenc-ways-to-use). Licence MIT.

## Image Decisions serving update (2026-09-28)

The SGLang image gateway now accepts actual image bytes and returns option probabilities via `/v1/systemone`. The probability rule is declared as `normalized_entailment_v1`: NLI entailment scores normalized over the supplied options, with no calibration fitted on the benchmark examples. Checkpoint weights are unchanged.

- [Image API and benchmark integration](code/serving/README.md)
- [V100 runtime setup](code/serving/V100.md)
- [JevBench image transport patch](code/serving/patches/jevbench-image-adapter.patch)
- [Public-example smoke results](results/image_jevbench_examples_20260928/README.md)

This is not a new full Image JevBench score. The published 4B v5 weights can be evaluated with the updated interface; an independent full-corpus rerun is required to update the official leaderboard.
