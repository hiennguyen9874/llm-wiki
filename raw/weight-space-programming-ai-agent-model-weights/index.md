---
title: "Weight-Space Programming: GPT-6 Astra Edits Qwen"
author: "Curtis Pyke"
site: "Kingy AI"
published: 2026-11-02T21:30:52+00:00
source: "https://kingy.ai/blog/weight-space-programming-ai-agent-model-weights/"
domain: "kingy.ai"
language: "en-US"
description: "GPT-6 Astra edited Qwen’s weights and raised MATH-500 from 7.9% to 48.1% in author-run tests. How weight-space programming works—and its limits."
word_count: 3791
---

GPT-6 Astra changed two matrices inside Qwen3.5-0.8B and, in the authors’ evaluation, its MATH-500 score rose from 7.9% to 48.1%. GSM8K went from 13.8% to 67.1%, and strict instruction-following on IFEval rose from 21.0% to 62.3%.

**Update, November 3:** A separate baseline evaluation by Carlos Toledo reports 43.95% for untouched Qwen3.5-0.8B across 2,000 generations, counting grader-undecided cases as wrong, under non-thinking settings and a different grader. The sixfold figure describes the original study configuration; it does not establish the gain over other configurations. [See the baseline follow-up and its limits below.](#sampling-baseline-followup)

The result comes from [a November 2, 2026 research report](https://rikiyat.github.io/blog/weight-space-programming/) by Rikiya Takehi, Jayden Teoh, Alex Zhang and Omar Khattab, all listed with MIT CSAIL affiliations. They call the approach **weight-space programming**: using an AI model to inspect, reason about and directly edit another network’s weights.

The agent touched 131,072 weight entries, about 0.016% of the model’s nominal 800 million parameters. It used Python to calculate the replacement values, then submitted the edited tensors for testing. The target model was not fine-tuned with gradients during this editing process. [The released results](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/eval/p50c/merged.json) and [edit manifest](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p50c/edit/manifest.json) make the claim unusually concrete: there are weight changes, run logs and benchmark files to inspect.

The most convincing explanation is also more specific than “the agent taught a model math.” In this setup, the original model often got trapped in long stretches of reasoning and failed to produce a final answer. The edit substantially reduced that failure. Many answers that had been cut off became correct answers. That is a valuable result in its own right: a capability hidden behind a bad failure mode can be as inaccessible to a user as a capability the model lacks.

The important shift is the agent’s job. It analyzes and edits the numerical machinery that will run future requests. A saved weight change can persist across deployment, rather than requiring the editing agent to answer every question. That possibility makes the result interesting even before claims about replacing conventional training enter the discussion.

## What it means to program weights

A neural network stores what it has learned in arrays of numbers called weights. During inference, the model repeatedly applies those arrays to its current internal state. In a language model, those operations help determine which token comes next and how the model carries information forward through its layers.

A prompt influences the computation by changing the input. Fine-tuning typically changes weights through a training procedure that measures an error and uses gradients to adjust parameters. A direct weight edit changes selected values through a calculation chosen by the researcher or an agent. These are descriptions of different workflows; direct edits can still use data, feedback and optimization.

For a developer, imagine diagnosing a server that repeatedly enters a retry loop. You could write a better client request, retrain a policy to avoid the loop, or investigate the internal state and change a component implicated in the failure. Weight-space programming attempts something closer to the third approach, except the “component” is a set of numbers distributed through a neural network, and their behavior is much harder to interpret than a conventional function.

The editing agent had a persistent Python environment, the target model’s tensors, practice problems and tools to run controlled inference. Python did the array arithmetic; Astra did not print hundreds of millions of weights into a chat response. The human-designed task also advised it to diagnose failures, test causal interventions and confirm gains on held-out practice items. The [initial task instructions](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p50c/turns/t001/prompt.txt) describe the permitted tools and the protected parts of the model.

## Following the repetition signal

The successful run began with a practical symptom. On many math problems, Qwen generated reasoning until it reached a 32,768-token ceiling without finishing. The authors’ [completed MATH-500 evaluation](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/eval/unedited/merged.json) records 93.0% of original responses hitting that ceiling. A ceiling hit is not, by itself, a perfect loop detector, but it is a serious obstacle when the grader needs a final answer.

The agent’s [final submission](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p50c/final_answer.md) describes comparing internal activity from productive and repetitive contexts, estimating directions associated with repetition and finding components that wrote strongly along them. Its final edit targeted selected columns in the output weights of two feedforward, or MLP, layers. Each selected column corresponds to one MLP neuron’s contribution to a 1,024-dimensional residual stream, the shared representation carried through the model.

The [run’s final report](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p50c/work_notes/final_report.md) expresses the operation as:

```
W_new = W_original - 6 × outer(u, mask64 × (u @ W_original))
```

Here, `u` is the estimated unit repetition direction for that layer; `u @ W_original` measures how strongly the columns write along it; and `mask64` retains the 64 selected columns for that layer. The outer product constructs an adjustment from those pieces. The factor of six matters: this was a scaled intervention, not merely the removal of one unscaled projection.

The [experiment history](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p50c/work_notes/experiment_history.md) records intervention and control tests before the final choice was frozen. Those tests support the authors’ interpretation within this run, although they do not prove that a single universal “loop direction” exists in language models. Kingy has inspected the released records and recalculated the figures, but has not replayed the model or the intervention experiments.

The selected matrices are at zero-based layers 15 and 19. Each has shape `[1024, 3584]`, and 64 columns were targeted in each. The arithmetic is:

```
2 layers × 64 columns × 1,024 entries = 131,072 touched entries
131,072 ÷ 800,000,000 × 100 ≈ 0.016%
```

The denominator uses the model’s nominal 0.8 billion parameters. The [released edit manifest](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p50c/edit/manifest.json) counts 130,188 entries bitwise different after bfloat16 conversion; some calculated changes rounded back to the original. The [frozen-weight manifest](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p50c/work_notes/frozen_weights_manifest.json) also reports relative changes of roughly 10.6% and 8.1% across the two edited matrices. A small count of changed entries says where the edit landed; it does not establish that its effect was small or that every other behavior was preserved.

## The results behind the 6× and 3× claims

The headline multipliers come from dividing the edited score by the original score. On MATH-500, 48.1 divided by 7.9 is approximately 6.1. On IFEval, 62.3 divided by 21.0 is approximately 3.0. The absolute scores and evaluation setup matter more than either multiplier.

| Measure | Original | 50-pass edit | Evaluation size |
| --- | --- | --- | --- |
| MATH-500 accuracy | 7.9% | 48.1% | 500 questions, four samples each |
| GSM8K accuracy | 13.8% | 67.1% | 1,319 questions, two samples each |
| IFEval strict prompt accuracy | 21.0% | 62.3% | 541 prompts, two samples each |
| MATH-500 responses reaching token cap | 93.0% | 33.1% | 500 questions, four samples per version |

The [aggregation code](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/code/merge.py) calculates mean accuracy across sampled responses, rather than pass-at-k or majority voting. The gains are 40.2 percentage points on MATH-500, 53.3 points on GSM8K and 41.3 points on IFEval, using rounded scores. The [original results](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/eval/unedited/merged.json), [edited results](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/eval/p50c/merged.json) and [evaluation code](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/code/evaluate.py) provide the underlying measurements.

The same release reports gains on AMC23, Minerva Math, OlympiadBench, a 1,000-question MMLU-Pro subset and GPQA Diamond. Its additional AIME evaluations remained weak: 0.625% on AIME 2024 and 2.292% on AIME 2025 after editing. Those results limit any sweeping description of the model as a newly strong mathematician. They also show why a relative improvement needs a baseline.

The IFEval result is particularly interesting because the agent was working on math failures. But “strict prompt accuracy” means every checked constraint in a prompt must pass; it is not the percentage of individual instructions followed. The grading protocol also matters. The evaluation checks the answer after the model closes its thinking section. If thinking never closes, the answer is empty. A model that finishes more often can therefore gain instruction-following points without acquiring every instruction-following skill anew. The [IFEval paper](https://arxiv.org/abs/2311.07911) describes the benchmark’s verifiable constraints; the project’s evaluation code specifies how the model’s answer is extracted.

The authors’ held-out practice analysis gives a more direct view of the recovery. Across 1,152 paired GSM8K and MATH practice items, the original was correct on 122 and the edited model on 696. The saved analysis reports 579 items rescued and five regressions; 576 of the rescues had originally been truncated. This is an author-reported analysis of practice items, rather than an independent replay or an item-level analysis of the final benchmark. It strongly supports the narrower explanation that finishing previously unfinished answers drove much of the improvement. [Submission evidence](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p50c/work_notes/submission_evidence.json).

## No gradients still required feedback

The target edit did not use gradient-based training. That is meaningful, but it does not mean the agent worked without examples or experiments. It had math practice data, inference outputs and access to internal model information. Both the editor and Qwen were already trained models.

The successful investigation used [GPT-6 Astra through Codex CLI at `max` reasoning effort](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p50c/turns/t001/run.json), with 50 harness-defined forward passes, 80 Python executions and 158 agent turns across four conversations. A pass was an accounting unit for a potentially substantial batch: the instructions allowed up to 512 generated responses, or up to 1,024 texts in a teacher-forced read of internal information. A paired comparison could include up to 256 examples per model. One pass should not be pictured as a single example or a single generated token. [Run state](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p50c/state.json), [task instructions](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p50c/turns/t001/prompt.txt).

The authors report 20.3 hours from the first to the last turn, including 4.7 hours waiting for an unavailable model. That elapsed time is not a compute bill. The release does not establish that this approach is cheaper than fine-tuning, a sampling change or another loop-control method. [Experiment README](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/README.md).

The practice set included training examples from GSM8K and MATH, plus historical AIME problems. The authors’ preprocessing filtered normalized exact matches and shared 13-word windows against the math evaluation sets. That is a useful contamination precaution, not proof that semantic near-duplicates or pretraining exposure were absent. The benchmark test sets were not exposed to the editing agent. [Practice builder](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/code/practice35.py).

The release also contains [10-pass](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p10c/final_answer.md) and [25-pass](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p25c/final_answer.md) investigations with different final edits. These are separate attempts under different budgets, not checkpoints in one continuous training run.

## What would make the comparison stronger?

The [published Qwen evaluation profile](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/code/profiles.py) used thinking mode, temperature 0.6, top-p 0.95, top-k 20, a presence penalty of 1.5 and a 32,768-new-token limit. As of November 2, the [Qwen model card](https://huggingface.co/Qwen/Qwen3.5-0.8B) warns about thinking loops and lists different recommended thinking-mode sampling, including temperature 1.0. Its reported benchmark scores use different conditions and cannot be compared directly to this experiment’s numbers.

A useful next test would run the original and edited models under matched recommended sampling, alongside practical loop controls, with the same prompts, seeds where appropriate, grading and token limits. That would help determine how much improvement the edit adds over changes a developer can make without touching weights.

The edit did not eliminate all failure. One-third of edited MATH-500 responses still reached the cap, and the [final run state](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p50c/state.json) records whitespace-tail degeneration in 51 of the 1,152 edited practice outputs. Wrong arithmetic and missing answers remained. Aggregate gains across benchmarks also do not establish that every individual response improved or that unmeasured capabilities were unaffected. The five paired practice regressions are a reminder to look at the cases behind the averages.

A follow-up on Gemma 3 270M IT is just as useful for setting expectations. That model rarely reached its shorter token limit in the baseline, and the same editor did not establish a meaningful math improvement. Format-agnostic MATH-500 accuracy was 6.8% before editing and ranged from 7.0% to 7.7% across the tested budgets. Gemma used a different architecture and evaluation setup, so the result does not prove direct editing can only recover loop-suppressed ability. It does show that the Qwen outcome did not automatically carry over. [Gemma follow-up](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/gemma_followup/README.md).

## A baseline rerun tests the sampling caveat

On November 3, Carlos Toledo [reported a fresh baseline evaluation](https://github.com/RikiyaT/lm_understand-logs/issues/4). His [later pinned record](https://github.com/carlostoledo1891/cert-machine/blob/76805430d50e396cae81a704bd17dc68152414fc/certs/wsp-baseline.json) records three completed conditions for **untouched Qwen3.5-0.8B**, each with 500 MATH-500 problems × four samples. Kingy recounted the stored verdict labels:

| Baseline condition | Correct / 2,000 | Grader undecided | Accuracy counting undecided as wrong | Hit output cap |
| --- | --- | --- | --- | --- |
| Original study settings, thinking on, 32,768-token cap | 144 | 7 | 7.20% | 93.10% |
| Card thinking sampling, 81,920-token cap | 445 | 23 | 22.25% | 74.95% |
| Card non-thinking sampling, 32,768-token cap | 879 | 232 | 43.95% | 0.30% |

“Undecided” means Toledo’s grader could not settle the answer’s correctness. It does not mean the model refused the question. Excluding those cases gives the non-thinking arm 879 / 1,768 = **49.72%**, on a smaller denominator. That conditional score should not be presented as accuracy over all 2,000 generations.

The two card-based arms use temperature 1.0. The non-thinking arm also uses top-p 1.0 and presence penalty 2.0; the thinking arm uses top-p 0.95 and presence penalty 1.5. Both retain top-k 20 and seed 0. The listed sampling values match the [model card’s text-task guidance](https://huggingface.co/Qwen/Qwen3.5-0.8B/blob/2fc06364715b967f1860aea9cf38778875588b17/README.md). The card recommends 81,920 output tokens for competition math; the non-thinking arm keeps the shorter 32,768-token cap used in its text example. Several conditions change together.

This makes the baseline concern concrete: the reported untouched model performs much better under another configuration. It does **not** establish the edit’s added value under matched recommended settings. The pinned record contains no completed edited-model arm under those settings, and Toledo uses a custom grader rather than the study’s math-verify. His [report and protocol](https://carlostoledo.co/reports/weight-space-programming.html) remain a separate evaluation. Kingy checked label arithmetic, not model execution or the underlying answer judgments; the original 48.1% and later 51.0% results retain their original attribution.

## The broader project and earlier work

The project also asks whether weights reveal what a network does. In a controlled test, Astra identified the training corpus of three small character models—Python, romaji or English—from their middle transformer blocks, in two attempts per model. Input and output layers were withheld, and forward passes were forbidden. That supports a limited but intriguing interpretability result, rather than unrestricted access to a model’s knowledge. [Language-identification experiment](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp3_language/README.md).

In one controlled car experiment, an agent received an environment description and a recorded failure, then edited a policy that went from zero successes in 256 trials to 1,024 successes in 1,024 trials. That is an impressive result for that specific environment, not evidence that arbitrary driving systems can be repaired this way. [Car experiment](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp4_fix_car/README.md).

For 9×9 Go, the 50-pass written policy won 74.2%, 70.0% and 78.5% against three seeds of a same-size PPO baseline, over 2,000 games per seed. That baseline was tuned across three learning rates and trained for 20.48 million games. The zero-pass written policy lost to those same-size seeds, despite narrowly beating two smaller PPO policies. The distinction matters when judging the benefit of feedback and the strength of the comparison. [Go experiment](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp6_go_from_scratch/README.md).

The inspection experiments had limits too. In a small sycophancy test, four rounds of inspecting paired Gemma variants’ weights produced no reliable discrimination; providing attention patterns led to three correct identifications out of three, with one final confidence only 55%. Those were deliberately trained toy variants, not audits of commercial systems. [Sycophancy experiment](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp7_sycophancy/README.md).

Direct intervention in model weights has precedents. [ROME](https://arxiv.org/abs/2202.05262) studied targeted edits to factual associations in transformer feedforward weights. Other researchers have investigated [direction-based interventions](https://arxiv.org/abs/2406.11717), and [Tracr](https://arxiv.org/abs/2301.05062) compiled specified programs into transformer weights. The distinctive proposal here is to use a general-purpose frontier AI agent as investigator and editor. In the Qwen case, it developed a numerical intervention in the model’s computation rather than writing code that trained the target with an optimizer. Some smaller experiments allowed no feedback at all. The project does not establish recursive self-improvement or make prior model-editing research obsolete.

### Further weight-reading and policy-writing reports

Simon Willison’s [November 3 local-model report](https://simonwillison.net/2026/Nov/3/qwen-can-interpret-model-weights/) covers **Experiment 1**, identifying a small policy’s game from its weights. He reports that Qwen 3.8 27B, running through LM Studio, identified Pac-Man, Pong and Breakout, but missed Freeway. He links the responses and reasoning traces. Those four reported attempts concern reading weights; they do not reproduce the Qwen3.5-0.8B math edit or the task of writing a new policy. Kingy has not rerun them.

The separate [alan-turing-institute/weights\_editing repository](https://github.com/alan-turing-institute/weights_editing/blob/0ad312cbc365536f28a3445557b9ad3133c9614b/README.md) adds repeated trials and controls for Experiments 1, 2 and 5. It reports shuffled-weight tests for reading, and modified Breakout tasks with swapped left/right actions or an upside-down board for writing. Its three GPT-6 Astra Seaquest policies, generated at `xhigh` effort, averaged **25.5**, versus **53.1** in the original release; each submitted policy was scored over 1,000 episodes. Kingy recomputed that mean from the [released run summaries](https://github.com/alan-turing-institute/weights_editing/tree/0ad312cbc365536f28a3445557b9ad3133c9614b/runs/exp5/gpt-6-astra), without rerunning the game. This illustrates variation between generated policies, rather than uniform reproduction of every original score.

These are different tests of different abilities. [Matthew Honnibal’s critique](https://honnibal.dev/blog/astra-read-write-misleading) argues that combining raw-weight, no-tool demonstrations with Python-assisted model investigations can imply a single capability that the experiments do not establish. The useful question is what each agent saw, which tools and feedback it received, and which exact task was reproduced. None of these reading or game-writing reports supplies another MATH-500 or IFEval evaluation.

## Another harness reports an Opus edit and a thinking-off comparison

The separate [weightspace project reports new Experiment 8 tests](https://github.com/leofmarciano/weightspace/blob/a0391973d1a24a4c8582473c2763bbe0a5ebedd3/README.md#results-exp-8-replication). It describes an **Opus 5.5 edit affecting 4,096 weights in four MLP neurons**, using seven of a 12-pass budget. These are the project’s reported results; Kingy has not rerun them.

The project reports a thinking-on evaluation of the first **250 problems from each benchmark**, one answer per problem, with a 32,768-token cap. Its thinking-off evaluation covers **500 MATH-500 problems and the first 500 GSM8K test problems**, again one answer each, with an 8,192-token cap. “Thinking” in the columns below refers to the target Qwen model; “high-thinking editor” describes the separate Opus editing session. Selected reported accuracy percentages are:

| Model or edit | Target thinking: MATH | Target thinking: GSM8K | Target no thinking: MATH | Target no thinking: GSM8K |
| --- | --- | --- | --- | --- |
| Untouched Qwen | 8.4% | 12.4% | 46.4% | 56.6% |
| Original researchers’ released edit | 52.4% | 61.6% | 42.0% | 57.2% |
| Opus 5.5, high-thinking editor | 40.0% | 53.2% | 41.8% | 54.4% |

This adds a report of a separately generated edit and a direct thinking-off comparison. The released edit’s MATH score is lower than the untouched model’s in that configuration; these point estimates alone do not establish statistical significance. The changed sample counts and decoding settings also prevent treating the thinking-on and thinking-off columns as a controlled test of thinking mode alone.

The sampling label needs care. The project calls its non-thinking setup model-card sampling. Its [pinned code](https://github.com/leofmarciano/weightspace/blob/a0391973d1a24a4c8582473c2763bbe0a5ebedd3/experiments/exp8/common.py) specifies temperature **0.7**, top-p **0.8**, top-k **20** and presence penalty **1.5**. Those values appear in the pinned Qwen card’s non-thinking benchmark footnote and vision-language preset, but differ from its text-task recommendation discussed above: **1.0, 1.0, 20 and 2.0**, respectively. The [evaluation code](https://github.com/leofmarciano/weightspace/blob/a0391973d1a24a4c8582473c2763bbe0a5ebedd3/experiments/exp8/evaluate.py) implements first-N sample selection and these token caps, but the inspected repository tree contains no underlying experiment generations or edit patches. Its grading code also imports `math_verify` without pinning a version in the experiment’s installation instructions. Kingy checked the published table and code; the scores and executed settings remain unverified reports. This is partial benchmark coverage and supplies no independent IFEval result.

## A reported replication on Breakout

On November 2, Alex Krentsel [reported a separate reproduction and a comparison across model generations](https://x.com/AlexKrentsel/status/2117376683724660898). His [follow-up identifies the experiment](https://x.com/AlexKrentsel/status/2117379728063799532) as Experiment 5: each model specifies the weights of a roughly 20,000-parameter Breakout policy in one reply, without training or tools. He says he used the original experiment’s prompts and scoring.

His chart sets the original PPO policy trained for 500 million steps to 1×. It labels GPT-6.1 Sol at 18×, GPT-6 Astra at 22× and Opus 5.5 at 20× that baseline, with earlier versions generally lower. These are his reported game-score ratios. Kingy has inspected the posts and chart, but has not rerun his tests.

The reported replication covers writing a small policy from scratch; it supplies no verification of the two-matrix Qwen edit or the MATH-500 and IFEval gains. The cross-version pattern warrants repeated runs with matched prompting and reasoning budgets; the chart alone cannot establish when a general ability emerged. Krentsel also [emphasizes the small target network](https://x.com/AlexKrentsel/status/2117376696211091894), which has 20,486 parameters in the original experiment.

## A downloadable checkpoint and a separate MATH-500 rerun

The edited [Qwen checkpoint is now available on Hugging Face](https://huggingface.co/RikiyaT/Qwen3.5-0.8B-weight-space-programming/tree/d1671a178705bcab7644806d23c535517f35723b). Its model card credits **akhaliq with ML Intern** for rebuilding the edit and running a separate evaluation on November 2, 2026. According to the card, this release includes the vision tower, while the original evaluation used a text-only export; it reports matching language-model tensor hashes. These are the publisher’s provenance claims, rather than a checkpoint comparison performed by Kingy.

The [released rerun scores](https://huggingface.co/RikiyaT/Qwen3.5-0.8B-weight-space-programming/blob/d1671a178705bcab7644806d23c535517f35723b/eval/scores_edited_math500.json) report **51.0% on MATH-500**, with 31.6% of generations reaching the token limit. Kingy recounted the stored correctness flags: 1,020 successes across 500 problems × four samples, or 2,000 generations. That verifies the arithmetic in the artifact, not the model execution or every answer’s grading.

The stated setup used thinking, temperature 0.6, top-p 0.95, top-k 20, presence penalty 1.5, a 32,768-token output cap and seed 0, with vLLM 0.33.0, Transformers 5.20.2 and math-verify 0.9.0. Keep this separately attributed 51.0% result alongside the original 48.1%; they are different runs.

The accompanying [base-model smoke test](https://huggingface.co/RikiyaT/Qwen3.5-0.8B-weight-space-programming/blob/d1671a178705bcab7644806d23c535517f35723b/eval/scores_base_math500.json) covers only 25 problems × four samples. It cannot establish a matched full-benchmark improvement ratio. This release also does not supply independent GSM8K or IFEval replications, or resolve the sampling-control question above. Kingy has not run either model.

## How to inspect and rebuild the released edit

Developers can inspect the edit without rerunning Astra. Use the public Qwen3.5-0.8B base revision `2fc06364715b967f1860aea9cf38778875588b17`, retaining the `model.language_model.*` tensor names. The released application script needs its neighboring `st_numpy.py` dependency and checks original and reconstructed tensor hashes. [Patch application script](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/code/apply_edit.py).

After obtaining the repository and the matching base `model.safetensors`, the following is the released script’s basic invocation. **Kingy has not run this command:**

```bash
python exp8_math/code/apply_edit.py \
  /path/to/base/model.safetensors \
  exp8_math/runs/p50c/edit \
  /path/to/edited/model.safetensors
```

A `.safetensors` output copies the base and replaces edited tensors; a directory output writes evaluated bfloat16 values as float32 `.npy` files. Keep the original checkpoint for comparison and reversal.

Rebuilding tensors is only the first part of reproducing a score. A meaningful comparison also needs a compatible model configuration, tokenizer, thinking template, numerical precision, decoding settings, prompts and graders. The [experiment’s release notes](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/README.md) show why this is not a turnkey recreation: the editing harness and some grader modules are absent, evaluation scripts retain internal paths, and many intermediate activations and generated practice files are omitted. The authors also disclose that earlier prompt trials are not included, which limits assessment of selection effects. [Repository disclosure](https://github.com/RikiyaT/lm_understand-logs).

The immediate research opportunity is a controlled comparison across more models and failure modes: preserve the released edit, measure per-item gains and regressions, and test it against simpler decoding and loop interventions under the same conditions. That would show when an agent’s access to the weights earns its extra complexity.

Chart: Kingy.ai, using author-reported results from the released evaluation files. Reporting and source inspection: November 2, 2026.
