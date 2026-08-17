---
type: Concept
title: V-JEPA 2
description: A self-supervised video JEPA scaled for motion understanding and anticipation, then post-trained as a latent action-conditioned world model for image-goal robot planning.
tags: [video, representation-learning, self-supervised-learning, world-models, robotics, video-language]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T13:40:58+07:00 }
sources:
  - id: vjepa2-paper
    resource: ../raw/2506.09985_V-JEPA 2/main.tex
    title: "V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning"
  - id: vjepa21-readme
    resource: ../raw/vjepa2/README.md
    title: V-JEPA 2 official PyTorch repository README
---

# V-JEPA 2

V-JEPA 2 is a family of 300M-to-1B-parameter video encoders trained without action or language labels to predict masked video features. The paper separately freezes its 1B encoder and trains V-JEPA 2-AC, a 300M-parameter action-conditioned latent predictor, on robot videos; image-goal planning then searches for actions whose predicted future representation approaches the goal representation. The reported understanding, anticipation, video-QA, and robot results support these specific training and evaluation systems, not a general-purpose physical world model or long-horizon planner.[^vjepa2-paper]

## Action-free video pretraining

A student ViT encoder receives visible video tubelets while a ViT predictor regresses the masked-position representations produced by an exponential-moving-average teacher encoder. The masked-patch objective uses L1 feature loss, stop-gradient teacher targets, multiblock masking, and 2×16×16 tubelets. V-JEPA 2 replaces absolute positions with axis-factorized 3D rotary position embeddings.[^vjepa2-paper]

The VideoMix22M corpus combines 22M video and image samples, including more than one million hours of video. The recipe scales the encoder from ViT-L (300M) through ViT-H (600M) to ViT-g (1B), lengthens training, and uses a cooldown phase to increase inputs from 16 frames at 256×256 to as many as 64 frames at higher spatial resolution. This progressive schedule is reported to reduce the projected GPU time for 64-frame 384×384 training by 8.4× relative to full-resolution training throughout.[^vjepa2-paper]

## Action-conditioned latent world model

V-JEPA 2-AC freezes the ViT-g encoder and independently encodes each robot-video frame into a 16×16×1408 feature map. A 24-layer, roughly 300M-parameter Transformer interleaves those features with 7D end-effector states and 7D relative actions. Block-causal attention permits each timestep to use current and prior visual, state, and action tokens.[^vjepa2-paper]

Post-training uses less than 62 hours of four-second Droid clips, including successful and failed interactions but no task labels or rewards. The predictor minimizes next-frame teacher-forcing loss plus a two-step autoregressive rollout loss in representation space. This makes the model action-conditioned, but the interaction data and post-training are still robot-specific.[^vjepa2-paper]

## Image-goal planning

At each control step, the planner uses the cross-entropy method to search an action sequence that minimizes L1 distance between the predicted terminal representation and an encoded goal image. It executes only the first action and replans from the next camera observation. The reported robot experiments use horizon one for the evaluated greedy skills; pick-and-place is decomposed into three manually scheduled image subgoals.[^vjepa2-paper]

Across ten trials per task configuration in each of two labs, the source reports V-JEPA 2-AC average success rates of 100% for reaching, 25–65% for grasping, 75% for reaching with an object, and 65–80% for pick-and-place, depending on object type. On one RTX 4090, its stated setup takes 16 seconds per action, compared with four minutes for the tested Cosmos latent-diffusion baseline. These are small, source-reported deployments on Franka arms with monocular fixed-camera views, not real-time or platform-general evidence.[^vjepa2-paper]

## Reported representation transfer

With frozen encoders and four-layer attentive probes, the 1B 384-resolution model reports 77.3 top-1 on Something-Something v2 and 39.7 mean-class action recall@5 on one-second Epic-Kitchens-100 anticipation. The anticipation probe uses both observed encoder tokens and predictor-generated future tokens, but an appendix ablation reports 39.1 recall@5 from encoder tokens alone versus 39.7 from both; this limits how much of the result can be attributed specifically to forecasting.[^vjepa2-paper]

For video QA, the encoder is projected into an LLM and trained on image/video-text data after visual pretraining. In a controlled frozen-encoder comparison using the same Qwen2-7B setup and 18M alignment examples, V-JEPA 2 reports higher average performance than the tested image encoders. A separate 88.5M-example, Llama-3.1-8B system reports leading results among the paper's compared ≤8B systems on five benchmarks, but not on TVBench or MVBench. These results show post-hoc language alignment, not language grounding inherent in the pretrained encoder.[^vjepa2-paper]

## Limits

- Direct encoder pretraining reaches 64 frames, about 16 seconds, and the paper reports no understanding-task improvement from 128 or 256 pretraining frames; this is bounded clip modeling rather than arbitrary-length video memory.
- Action anticipation degrades at longer horizons and is evaluated in a closed kitchen vocabulary.
- Robot rollouts accumulate prediction error, while action-search cost grows rapidly with horizon; the evaluated pick-and-place procedure depends on supplied image subgoals.
- Robot control is sensitive to camera placement because the uncalibrated monocular view must implicitly identify the action coordinate frame.
- Goals are images rather than language, planning is not real time, and robot evidence covers two Franka setups rather than broad embodiment transfer.[^vjepa2-paper]

## Relationships

- **Extended by:** [V-JEPA 2.1](v-jepa-2-1.md), which adds visible-token prediction, intermediate-layer targets, joint image-video training, and a listed 2B encoder while leaving V-JEPA 2-AC as the documented robotics variant.[^vjepa21-readme]
- **Instantiates:** [Video temporal representation learning](video-temporal-representation-learning.md) through masked prediction of EMA-teacher video features.[^vjepa2-paper]
- **Supports:** [Temporal action understanding](temporal-action-understanding.md) through frozen-probe motion classification and one-second action anticipation.[^vjepa2-paper]
- **Depends on:** [Long-video temporal modeling](long-video-temporal-modeling.md) beyond its directly processed 64-frame clips and short-horizon latent rollouts.[^vjepa2-paper]
- **Supports:** [Video-language temporal grounding and reasoning](video-language-temporal-grounding-and-reasoning.md) as a video encoder aligned post hoc with an LLM for temporal QA; it does not predict temporal intervals.[^vjepa2-paper]

[^vjepa2-paper]: [V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning](../raw/2506.09985_V-JEPA%202/main.tex)
[^vjepa21-readme]: [V-JEPA 2 official PyTorch repository README](../raw/vjepa2/README.md)
