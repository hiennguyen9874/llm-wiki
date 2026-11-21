---
type: Concept
title: Compositional generalization in LM harnesses
description: How context offloading, programmatic tools, and sub-calls can help language-model harnesses transfer learned strategies to new tasks.
tags: [language-models, agents, generalization]
status: draft
created: 2026-11-21
generated: { by: llm-wiki-agent/1, at: 2026-11-21T16:58:32Z }
sources:
  - id: compositional-harnesses
    resource: ../raw/LanguageModelHarnessesCanBeCompositionalGeneralizers/LanguageModelHarnessesCanBeCompositionalGeneralizers.md
    scope: ../raw/LanguageModelHarnessesCanBeCompositionalGeneralizers/
    kind: paper
    title: Language Model Harnesses Can Be Compositional Generalizers
  - id: zhang-harness-post
    resource: ../raw/2123774098241147225/index.md
    scope: ../raw/2123774098241147225/
    kind: article
    title: Post by @a1zhang on X
  - id: omarsar0-harness-post
    resource: ../raw/2123863490800828830/index.md
    scope: ../raw/2123863490800828830/
    kind: article
    title: Post by @omarsar0 on X
---

A harness may generalize compositionally by turning a globally novel task into familiar orchestration steps and individually manageable model calls. Zhang, Chakraborty and Khattab call this hypothesized property **locally in-distribution** (LID). Their experiments provide evidence for the hypothesis, not a proof that the prompts actually belong to the model's training distribution or that all decompositions generalize. **Reported**, not independently reproduced.[^compositional-harnesses]

## Perspective on stronger models

In a post introducing the paper, @a1zhang argues that harnesses are not merely a crutch for weaker models: they can compose stronger models' capabilities, and the possibility that models will absorb and make harnesses obsolete has not been established. This is the author's **opinion**, not an experimental forecast.[^zhang-harness-post]

@omarsar0 similarly recommends custom harnesses and cites RLMs as an example of abstractions that extend existing model capabilities. The author reports early personal success using post-training to co-evolve harnesses and models, including a dynamic-workflow variant in a meta harness, and speculates this might help explain the effect. The post supplies no implementation or evaluation details and calls for more research; neither the reported success nor the proposed explanation is independently established. See also [training recursive language models](training-recursive-language-models.md) for distinct, documented experiments.[^omarsar0-harness-post]

## Mechanism and diagnostics

The paper contrasts growing trajectory-as-prompt context with three complementary abstractions: offloading context to an environment and retrieving slices; calling tools programmatically so intermediate state stays outside the model's prompt; and delegating to sub-agents with fresh contexts. The tested [RLM](recursive-language-models.md) combines these. A task can transfer if the root reuses an effective decomposition and the delegated subproblems are reliably solvable; similarity of the root's text alone is insufficient.[^compositional-harnesses]

The authors compare root trajectories using weighted Jaccard similarity and, where intermediate ground truth exists, measure sub-call performance rather than establish actual training-distribution membership. For OOLONG, checkpoint subtask label accuracy is 85.6% on train and 83.7% on evaluation; OBLIQ writing-to-math document relevance AUC is 79.3 versus 67.3. Not every task has per-call labels, and correctness is not guaranteed.[^compositional-harnesses]

## Reported transfer experiments

- **Length:** GRPO-trained Qwen3-30B-A3B-Instruct-2507 on short splits of six environments was tested on longer variants, with length ratios from 2× to 64×. The RLM generally transfers better than the direct model and the other tested harnesses; graph and retrieval tasks can also transfer via code alone, while dense semantic tasks benefit from sub-calls. Some evaluations change other properties too, such as MRCRv2's number of needles, so this is not a pure length intervention in every case.[^compositional-harnesses]
- **Strategy:** training on one domain and evaluating on another with related solution structure includes OOLONG question classification to spam and OBLIQ writing-to-math or social-post-to-transcript ranking. The authors report strongest transfer for the RLM among tested harnesses; similar trajectory text did not rescue Pi when its learned procedure did not scale.[^compositional-harnesses]
- **Conditions:** the reported experiments use one 8×H100 node, default seed 0, one evaluation rollout per example, and different training loss treatment for Pi and RLM. Results are task- and model-specific, not a universal harness ranking. Checkpoint selection and plots do not establish general statistical significance.[^compositional-harnesses]

## Relationships

- **Synthesis:** [Code mode for agent tool orchestration](code-mode-agent-tool-orchestration.md) illustrates programmatic tool batching in a separate reported cost comparison.
- **Uses:** [Recursive language models](recursive-language-models.md) supply one tested offloading and sub-call scaffold.
- **Enables:** [Surrogate harness training](surrogate-harness-training.md) targets local orchestration behavior based on the proposed transfer mechanism.
- **Synthesis:** [Training recursive language models](training-recursive-language-models.md) describes related root-orchestration training experiments.

## Source and coverage

The supplied English paper is by Alex L. Zhang, Souradip Chakraborty and Omar Khattab, MIT CSAIL; publication date, revision, upstream URL and license are not established by this local capture. The Markdown entry point and its appendix structure were inventoried; main text, training setup, selected appendices and tables were inspected. Figures 2, 3, 4's OOLONG panel, and 6 were visually inspected. The package's 55 JPEG assets were inventoried; remaining figures and embedded examples, much of the appendix and bibliography remain pending visual or detailed inspection. Captions and text are used where image data was not inspected. No external code, data, license or reported experiments were checked or executed. Draft status records these limits.[^compositional-harnesses]

The X post is an English local capture attributed to @a1zhang, dated 2026-11-20 in its metadata. Its single file was inspected; the shortened link to the paper, logs, code and data was not followed, and the post's license and capture date are not specified. It summarizes the same research rather than providing independent corroboration.[^zhang-harness-post]

The English X capture attributed to @omarsar0 is dated 2026-11-20 in its metadata; its sole local file was inspected. The referenced research and personal implementation are not linked or specified in this capture; the upstream post was not checked, and capture date and license are unspecified. The post is commentary and an anecdotal report, not independent experimental corroboration.[^omarsar0-harness-post]

[^omarsar0-harness-post]: [Post by @omarsar0](../raw/2123863490800828830/index.md), metadata and post body, paragraphs 3–8.

[^zhang-harness-post]: [Post by @a1zhang](../raw/2123774098241147225/index.md), metadata and post body, first and final paragraphs.

[^compositional-harnesses]: [Paper](../raw/LanguageModelHarnessesCanBeCompositionalGeneralizers/LanguageModelHarnessesCanBeCompositionalGeneralizers.md), §§1–3, Tables 1–2, Figures 2–5, Appendix A and Table 7, Appendix D.3–D.5 and Table 19; `images/image-000003.jpg`, `images/image-000004.jpg`, `images/image-000005.jpg`, `images/image-000009.jpg`.
