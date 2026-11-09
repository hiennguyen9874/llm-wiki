---
type: Concept
title: LLM-directed neural weight editing
description: Reported neural policy construction, classification, and model repair by directly changing weights.
tags: [ml, optimization, interpretability]
status: draft
created: 2026-11-09
generated: { by: llm-wiki-agent/1, at: 2026-11-09T08:29:40Z }
sources:
  - id: video-cAGCH19xgU8
    resource: ../raw/cAGCH19xgU8.md
    kind: video
    title: "Video discussion of weight-space programming"
  - id: legal-summary-2117695754278142357
    resource: ../raw/x-2117695754278142357-legoras-cto-says-claude-fable-hand-wrote-the-weights-of-a-100k-parameter.md
    kind: article
    title: "Summary of reported legal citation classifier"
  - id: williams-weight-edit
    resource: ../raw/weight-space-programming-what-0016-edit-means-ai-junior-williams-3nbgc.md
    kind: article
    title: "Junior Williams on the 0.016% weight edit"
  - id: admix-weight-space
    resource: ../raw/weight-space-programming-llms-edit-weights.md
    kind: article
    title: "Admix article on weight-space programming"
  - id: itecs-explainer
    resource: ../raw/weight-space-programming-explained/index.md
    scope: ../raw/weight-space-programming-explained/
    kind: article
    title: "Weight-Space Programming: How LLMs Edit Model Weights"
  - id: kingy-weight-space
    resource: ../raw/weight-space-programming-ai-agent-model-weights/index.md
    scope: ../raw/weight-space-programming-ai-agent-model-weights/
    kind: article
    title: "Weight-Space Programming: GPT-6 Astra Edits Qwen"
  - id: takehi2026
    resource: ../raw/weight-space-programming.md
    kind: article
    title: "Sparks of Weight-Space Programming: LLMs can natively read & write neural network weights"
  - id: mindstudio-weight-space
    resource: ../raw/gpt-5-astra-weight-space-programming/index.md
    scope: ../raw/gpt-5-astra-weight-space-programming/
    kind: article
    title: "Can AI Edit Another Model's Weights? Inside the MIT Experiment"
  - id: datacamp-weight-space
    resource: ../raw/datacamp-weight-space-programming.md
    kind: article
    title: "DataCamp article on weight-space programming"
  - id: community1412375
    resource: ../raw/1412375/index.md
    scope: ../raw/1412375/
    kind: article
    title: "Weight Space Programming (or How to Write LLM Weights Directly using an LLM)"
  - id: critique2117416640132366570
    resource: ../raw/2117416640132366570.md
    kind: article
    title: "Critique of weight-space programming experiments"
  - id: summary2117422816438145164
    resource: ../raw/2117422816438145164.md
    kind: article
    title: "Situation explained: direct weight editing"
  - id: citation2117606206764175543
    resource: ../raw/2117606206764175543.md
    kind: article
    title: "Post on hand-written legal citation classifier weights"
  - id: post2117782732654658047
    resource: ../raw/2117782732654658047.md
    kind: article
    title: "Post on Fable 5.1 and legal citation classification"
  - id: post2117808859691811216
    resource: ../raw/2117808859691811216.md
    kind: article
    title: "Post on Qwen3.8-27B thinking-token efficiency"
  - id: critique2118072016670732400
    resource: ../raw/2118072016670732400.md
    kind: article
    title: "Post criticizing hype around weight writing"
  - id: post2119416808273019037
    resource: ../raw/2119416808273019037.md
    kind: article
    title: "Post on injecting profile facts into Qwen weights"
  - id: reddit-sparks-discussion
    resource: ../raw/paper_sparks_of_weightspace_programming_llms_can.md
    kind: article
    title: "Reddit discussion of Sparks of Weight-Space Programming"
  - id: reddit-legal-citations
    resource: ../raw/claude_writes_a_neural_networks_weights_by_hand.md
    kind: article
    title: "Reddit discussion of hand-written legal citation classifier weights"
---

**Reported:** A blog describes GPT-6 Astra directly constructing or editing neural network weights without gradient training, ranging from one-shot game policies to a tool-assisted edit of a small language model. Outcomes depend on architecture, task information, permitted feedback, and evaluation settings; they do not establish a general ability to add missing capabilities.[^takehi2026]

## Policies

- **Repair:** Given a Kinetix car policy, scene description, and one recorded failure, Astra reportedly changed 3.5% of weights in one tool-free attempt; the edited policy succeeded in 1,024 episodes, versus no successes in 256 baseline episodes. The authors describe an added path that backs the car up before handing control back to the original policy.[^takehi2026]
- **One-shot construction:** For three MinAtar games, Astra received rules, source code, and input/output layout and wrote weights from zero without tools, rollouts, gradients, or data. Reported scores exceeded best-of-3-to-10-seed PPO at 100 million steps in all three games, but not PPO at 500 million steps in Seaquest or Asterix. Evaluation used 1,000 episodes with sampled actions and sticky actions of 0.1. For MinAtar Breakout specifically, the reported score was 517.4 versus 25.3 for 500M-step PPO, about 20 times as much; Astra was also given the game's source code, not only its rules.[^takehi2026] [^summary2117422816438145164]
- **Go:** A 9×9 Go policy was written into a larger zero-initialized network using Python. At zero forward passes it reportedly beat two smaller PPO policies more than half the time; with 50 passes it reportedly beat an equal-sized PPO network trained on 20 million games. The article also specifies scoring against two small held-out PPO networks, but does not clearly reconcile that scoring description with the equal-sized comparison. Forward passes allowed practice games or position outputs, and edits could be selected on feedback.[^takehi2026]

**Reported by a secondary explainer:** In the Go test, the zero-pass policy won 42.6%, 26.3%, and 36.3% against three same-size PPO seeds; the 50-pass policy won 74.2%, 70.0%, and 78.5%. It separately reports results against two smaller held-out opponents, with 2,000 games per opponent seed and one run per budget. These comparisons involve distinct opponents, not an equal-sized baseline at zero passes beating all seeds.[^itecs-explainer]

## Legal citation classification

**Reported:** A post says Fable hand-wrote the weights of an approximately 100,000-parameter neural network to classify legal citations as real or fake. Its attached table reports the following test accuracies; the first hand-written version saw no labels, whereas the revision saw 5,062. These are source-reported comparisons, not a general demonstration that hand-writing beats training.[^citation2117606206764175543]

| Weights | Labels seen | Non-zero parameters | Test accuracy |
| --- | ---: | ---: | ---: |
| Hand-written | 0 | 3,793 | 97.8% |
| Hand-written, one revision | 5,062 | 3,828 | 98.9% |
| Trained | 512 | 107,745 | 76.5% |
| Trained | 5,062 | 107,745 | 92.9% |
| Trained | 8,192 | 107,745 | 94.6% |

**Reported:** A separate post identifies the model as Fable 5.1 and characterizes the trained comparator as backprop-trained. Its attached table repeats the same numbers; this does not independently verify the model identity or training method. The post's prediction of a world-changing breakthrough is opinion, not an experimental result.[^post2117782732654658047]

**Reported:** A Reddit headline attributes the 97.8% and 94.6% comparison to Claude. Its attached screenshot juxtaposes two posts: one attributes that exact accuracy table to Fable, while another separately claims Claude wrote a zero-training citation checker. The screenshot does not establish that the two posts describe the same experiment or that Claude produced the table. The Claude post reports catching 31 of 31 fake citations and flagging 1 of 983 real citations on a LePhantomCite held-out set; these are reported counts, not an independently checked evaluation. It also claims 50 μs per citation on an M5 Pro and 1.8 million citations/s using ANE plus GPU, without enough detail to reconcile the measurements.[^reddit-legal-citations]

**Reported by another summary:** Jacob Lauritzen, identified as Legora's CTO, is said to have reported the table above; the summary calls the model “Anthropic's Claude Fable.” That combined model attribution is not established by the separately captured posts and screenshot, which distinguish Fable and Claude claims. The summary does not explain the model identity or demonstrate that those claims refer to the same experiment.[^legal-summary-2117695754278142357] [^reddit-legal-citations] [^citation2117606206764175543]

**Synthesis:** Overall accuracy alone does not determine the false-citation rate or the false-positive rate. A comment's interpretation of 97.8% accuracy as a 2.2% false-citation rate is therefore not supported without the class-specific confusion matrix and evaluation population.[^reddit-legal-citations]

**Reported by a secondary article:** An Admix article attributes a roughly 100,000-parameter legal-citation classifier outperforming a trained version to Claude. Its account does not establish that this was the Fable experiment or provide a protocol; the separate Reddit screenshot described above does not justify merging the two claims.[^admix-weight-space] [^reddit-legal-citations]

## Language-model repair

**Reported:** For Qwen3.5-0.8B, with 50 forward passes on practice data and no gradients, Astra subtracted a direction from 64 output columns in each of MLP layers 15 and 19, changing 131,072 weights. Under the article's sampling settings and 32,768-token limit, MATH-500 rose from 7.9% to 48.1%, GSM8K from 13.8% to 67.1%, and IFEval from 21.0% to 62.3%; the fraction of MATH-500 answers hitting the token limit fell from 93.0% to 33.1%. The reported improvement is associated with reducing loops, not proof of newly learned math. Smaller 10- and 25-pass budgets produced much smaller math gains.[^takehi2026]

**Reported:** A separate post says Astra edited Qwen3.8-27B to make a purported “done thinking” signal twice as strong, at roughly $100 GPU cost. It claims 40% fewer thinking tokens on average on the pelican-on-a-bicycle test. An attached illustration labels a before/after pair as 30,699 and 2,352 tokens; it does not establish that these are the averages underlying the 40% claim. The capture does not establish the edit method or whether answer quality was preserved.[^post2117808859691811216]

**Reported by a secondary article:** Ahsen Khaliq reconstructed the edited Qwen checkpoint from logs and obtained 51.0% on MATH-500 using the same settings. Neither the reconstruction nor the claimed settings or evaluation were inspected here, so this is not a verification event for this wiki.[^datacamp-weight-space]

**Reported, preliminary side-effect test:** A video speaker says their own test of the math-improved model found worse performance on a copying task. They say the result needs confirmation and give no task details, counts, baseline settings, or artifacts. This is a possible trade-off, not established catastrophic forgetting or evidence that the same neurons caused both behaviors.[^video-cAGCH19xgU8]

**Reported negative result:** On Gemma 3 270M, which rarely looped under its different sampling settings, edits across 5–50 forward passes did not establish a math improvement: MATH-500 ranged from 7.0% to 7.7% against a 6.8% baseline. The authors characterize the residual failures as ordinary reasoning errors, not a single removable obstacle.[^takehi2026]

**Reported by a secondary article:** An Admix account describes a held-out accuracy increase from 10.6% to 60.4% and says 576 of 579 repaired answers had originally reached the token cap. The same counts appear in another account's analysis of 1,152 held-out practice items; this is not established as an item-level analysis of the final benchmark. The Admix account also reports that Alex Krentsel reran an earlier MIT experiment across model generations and that the newest models scored up to 22 times an RL-trained baseline; it provides no linked report or evaluation details for this claim.[^admix-weight-space] [^kingy-weight-space]

## Qwen intervention and comparison details

**Reported by a secondary account:** The two edited MLP output matrices have shape 1,024 × 3,584. For a layer-specific estimated repetition direction `u`, the account gives `W_new = W_original - 6 × outer(u, mask64 × (u @ W_original))`. Thus the intervention is a sixfold scaled adjustment to 64 selected columns per layer, not simply removal of an unscaled projection. Of 131,072 targeted entries, the reported manifest counts 130,188 bitwise different after bfloat16 rounding; the small edited fraction does not establish behavioral preservation.[^kingy-weight-space]

**Reported:** Among 1,152 paired held-out practice items, the original was correct on 122 and the edit on 696; 579 were rescued and five regressed, with 576 rescues originally truncated. This practice analysis supports a completion-related interpretation but is not an item-level analysis of the final benchmark. IFEval extracts the answer after the thinking section closes, so improved completion can also affect its score.[^kingy-weight-space]

**Reported external comparisons:** A separate baseline study using a different grader found untouched Qwen at 43.95% on 2,000 non-thinking MATH-500 generations, counting 232 grader-undecided cases as wrong. Its configuration differs from the original and lacks a matched edited-model arm, so it cannot determine the edit's incremental effect. Another project reports original-edit versus untouched MATH scores of 42.0% versus 46.4% with thinking off, and 52.4% versus 8.4% with thinking on; sample sizes and token caps differ across modes, and significance is not established. The article says that project's underlying generations and patches were absent from its inspected repository, and its grading dependency was unpinned.[^kingy-weight-space]

**Reported constraints on replication:** The successful investigation used 50 harness-defined passes, 80 Python executions and 158 agent turns; a pass could include a batch rather than one example. The account says the release lacks the editing harness, some grader modules and intermediate artifacts, and discloses omitted earlier prompt trials. It reports a separate 51.0% MATH-500 checkpoint evaluation, but its base smoke test covered only 25 problems; this does not establish a full matched improvement ratio.[^kingy-weight-space]

## Baseline configuration and completion

**Reported by a secondary article:** Qwen's model card warns of looping in thinking mode, which the article says is not the model's default, and the experiment used thinking mode at a lower temperature than recommended. It also cites separate research associating lower temperatures with more loops. These claims about the model card and research have not been checked against those sources. The article reports that most practice answers fixed by the edit had previously exhausted the output limit and interprets the score gain primarily as improved completion rather than newly acquired mathematics.[^mindstudio-weight-space]

**Reported recommendation:** When evaluating a low score, inspect completion and repetition as well as correctness; the article suggests considering mode, temperature, or output limits before editing weights. These alternatives are hypotheses to test, not established fixes for every failure. The article notes that the Gemma comparison is not controlled across models and that trials apparently were not repeated; neither point establishes a general impossibility of adding capabilities.[^mindstudio-weight-space]

**Reported recommendation:** The ITECS explainer recommends recording an open-weight model's source, version, and checksum, then rerunning a fixed test set after changes. It presents this as governance advice, not as an experimentally validated guarantee of safety.[^itecs-explainer]

## Efficiency and model integrity

**Reported analysis:** Junior Williams distinguishes the 0.016% edit size from the cost of discovering it: diagnostic-model compute is not reported, so an efficiency comparison with fine-tuning remains open. He treats the result as consistent with, but not a test of, his hypothesis that algorithmic improvements can raise performance at fixed hardware; one edit does not establish compounding gains or a validated innovation metric.[^williams-weight-edit]

**Reported security recommendations:** Williams recommends pinning and verifying checkpoint hashes and signatures, comparing checkpoints against recorded provenance, and rerunning behavioral regression tests including refusal and policy behavior after changes. He presents malicious behavior insertion as plausible, not demonstrated by this experiment; the sycophancy test also illustrates a limit of weights-only detection. These controls are advice, not a validated guarantee of detection or safety.[^williams-weight-edit]

## Replaying a weight-reading experiment

**Reported procedure:** The secondary article describes replaying experiment 1 with the `lm_understand-logs` repository: use a run's `prompt.txt`, containing the network description and 17,253 weights, and compare the answer with `answer.md` and the `eval/` scoring and answer key. It says the original runs used Codex CLI with built-in tools disabled and high reasoning effort, explicitly selecting the model and effort because the harness configuration has different defaults. It estimates about 73,700 input and fewer than 2,000 output tokens per run. The repository, configuration, and procedure were not inspected or executed; availability and pricing are time-sensitive.[^datacamp-weight-space]

## Injecting profile facts

**Reported:** A post says an agent edited a Qwen 0.8B model to answer questions about the author's profile and projects without training or gradients. It reports changing 5 of 488 tensors, described as 2% of the network; that is a fraction of tensor count, not necessarily of individual parameters. The author claims other knowledge was untouched, but provides no evaluation supporting that broad preservation claim. The example is presented as a glimpse of continual learning, not evidence of sustained learning across a sequence of updates.[^post2119416808273019037]

## Critical interpretation and disputed results

**Reported by an unidentified critic, not independently verified:** A claimed test puts unedited Qwen in non-thinking mode at 47% on MATH-500 versus 48% for Astra's edit; the critic argues the edit primarily suppresses looping and reports trial-and-error selection over thousands of answers. The post does not document the comparison's settings, samples, or code, so it cannot establish equivalence between modes. The original authors also acknowledge that loop removal reveals existing ability rather than establishing improved reasoning.[^critique2117416640132366570] [^takehi2026]

**Reported critique:** The car edit allegedly drives ten weights as high as 876 and succeeds on a single repeated level, limiting generalization. For Breakout, the critic describes a sparse, hand-coded ball-landing rule and reports a stronger short-script comparator. The original article explicitly supplies game source and describes the same ball-landing strategy; its table reports that Astra loses to 500M-step PPO on the other two games while beating its 100M-step comparators. The critic's additional magnitudes, level variation, and comparator results are unverified.[^critique2117416640132366570] [^takehi2026]

**Reported critique:** In a Reddit capture, commenters quoting attributed Hacker News criticism argue that weight editing and steering vectors predate this work, and characterize the Qwen edit as a conventional contrastive steering approach that reduces loops rather than adding mathematical ability. These are commenters' interpretations, not independently checked method comparisons. Other commenters question whether changing a small fraction of weights prevents unintended effects; the fraction alone cannot establish behavioral preservation.[^reddit-sparks-discussion]

**Reported critique:** Another post argues that weight-writing demonstrations can be overhyped because selected problems admit small deterministic programs, which are then encoded into neural weights. Its author says they replicated the work, but the captured opening gives no method or results; this claim is not an independently checked replication.[^critique2118072016670732400]

**Reported opinion:** A short summary quotes @theojaffee as regarding the result as meaningful but not evidence of imminent recursive self-improvement through a model editing its own weights. This is a judgment, not a demonstrated forecast.[^summary2117422816438145164]

## Anecdotal speech-model attempts

**Reported, anecdotal:** A community participant said iterative attempts to construct an automatic speech recognition model from scratch using Astra and then Sol 6.1 performed poorly. In a separate attempt to edit Pocket TTS weights to imitate a voice, they reported 1 of 20 samples with a good ECAPA-TDNN similarity score, contrasting this with a voice-context KV-cache approach they said worked well. The capture does not specify the full protocol, similarity threshold, or a controlled comparison; these remarks do not establish general success rates.[^community1412375]

## Relationships

- [Model adaptation mechanisms](model-adaptation-mechanisms.md) compares editing with training, distillation and retrieval; [continual learning and recursive improvement](continual-learning-and-recursive-improvement.md) explains why a single repair does not establish either.
- The [Italian translation weight-edit experiment](italian-translation-weight-edit-experiment.md) reports a sparse translation preference edit with related and unrelated controls.

- The [clinical decision network weight audit](clinical-decision-network-weight-audit.md) reports sparse synthetic-network repairs and numerical-safety limits.
- The [coarse normalization-weight editing experiment](coarse-normalization-weight-editing-experiment.md) reports a different model and intervention, including a no-op measurement failure and negative code-repair results.
- This is the intervention side of [weight-space programming](weight-space-programming.md); [reading neural network weights with LLMs](reading-neural-network-weights-with-llms.md) describes related diagnostic experiments.
- The [Writing Weights Index](writing-weights-index.md) reports cross-model comparisons for a weight-writing task, with important protocol limits.

## Evidence limits

The standalone English video transcript links to YouTube but gives no full creator identity, date, license, timestamps, test protocol, or local attachments. The video, the speaker's social-media post and the underlying research artifacts were not inspected for this ingest; transcription errors may affect model names and technical detail. No experiment was reproduced. The speaker's proposed internal mechanisms and recursive improvement are speculation; the legal-classifier anecdote does not resolve the separate attribution ambiguity above.[^video-cAGCH19xgU8]

The results are the authors' reports. External code, logs, benchmark data, model card, and edited model were not inspected; no training or evaluation was reproduced. In particular, small edit size does not demonstrate absence of side effects or catastrophic forgetting.[^takehi2026]

The standalone English article by Junior Williams is a secondary analysis; its capture gives no article publication date, canonical article URL, capture date, or license. Its three “Article content” captions describe illustrative figures, but no figure files or local attachment references appear in the capture. The original research, referenced studies, external logs and checkpoints were not inspected for this ingest, and no experiment was reproduced. Its authorization-testing anecdote and personal promotion were excluded; no sensitive values or executable content were identified.[^williams-weight-edit]

The standalone English Admix article is a secondary account with no byline, publication date, canonical article URL, capture date, or license in the local text. Its linked social posts, Reddit discussion, model/demo, and embedded video were not inspected for this ingest; the video is described as a walkthrough but its content remains unavailable here. The article's promotion and pricing were excluded; no local attachments, sensitive values, or executable instructions were identified. No experiment was reproduced. Its broad claims of independent reproduction do not establish replication of the specific Qwen weight edit.[^admix-weight-space]

The English Kingy AI article by Curtis Pyke is dated 2026-11-02 and includes a November 3 update. Its single local file was inspected; it has no local attachments. Its many external studies, code, checkpoint, model card, experiment records and article-linked evidence were not independently inspected here. The article reports checking some artifacts and arithmetic, not replaying models; those checks are not this wiki's verification. Its patch command was not executed. Capture date and license are unspecified; draft status preserves these limits.[^kingy-weight-space]

The MindStudio English secondary article by Luis Chavez-Mattos is dated 2026-11-04 and identifies its original URL in the capture. Both local images were inspected and excluded as decorative promotional illustrations; promotional copy was also excluded. The underlying paper logs, Qwen model card, separate looping research, and editorial standards were not inspected for this ingest; the capture supplies no license or capture date. Its model-card and evaluation claims are reported, not independently verified, and no experiment was run. Draft status retains these limits.[^mindstudio-weight-space]

The DataCamp article is a standalone English secondary account; its capture supplies no byline, publication date, URL, license, or local attachments. It cites external experiment logs, a checkpoint and model card, and a demo, none inspected for this ingest. The reported replication and replay instructions remain unverified; promotional links and per-run price estimates are omitted as time-sensitive. No sensitive values or executable content were identified.[^datacamp-weight-space]

The profile-edit post is a standalone text with no identified author, date, model revision, license, editing procedure, prompts, or evaluation protocol. It refers to a reproduction repository in comments, but neither comments nor a repository link are included in the capture; the repository was not inspected. No experiment was reproduced. No sensitive values or executable content were identified.[^post2119416808273019037]

The hype-critique capture contains only an opening marked “1/n”; any continuation is unavailable in this source. It gives no author, date, URL, license, replication protocol, results, or linked artifacts. No executable content or sensitive values were identified.[^critique2118072016670732400]

The critique is a standalone local text with no stated author, date, methodology, license, or linked test artifacts; its claims of inspecting logs and performing tests were not independently checked, and its polemical personal attacks are excluded. No attachments or executable instructions were identified.[^critique2117416640132366570]

The short summary is a standalone local text with no stated author, date, original URL, license, or linked artifacts; its quotation and descriptions were not independently verified. It omits the game source code supplied for Breakout, which is specified in the experimental article. No local attachments or executable content were identified.[^summary2117422816438145164] [^takehi2026]

The community thread and its local image were inspected; the image repeats the original article's examples. The thread's linked benchmark and external report were not independently inspected for this ingest, and the speech-model attempts were not reproduced. The capture provides no license or detailed speech evaluation protocol.[^community1412375]

The Reddit Sparks capture is a standalone English post by u/pmttyji with comments, including quotations attributed to Hacker News; it supplies no publication date, capture date, or license. The body repeats the original blog's claims rather than independently corroborating them. The linked blog, repository, checkpoint, demo, model card, criticism, and remote images were not inspected for this ingest; the images may contain additional evidence. No experiment was reproduced. Speculative forecasts and unrelated comments were excluded. No sensitive values or executable content were identified.[^reddit-sparks-discussion]

The Reddit capture and both linked preview images were inspected: the main screenshot contains the two posts and a table; the comment image is a decorative meme. The screenshot's truncated Hugging Face link and other external links were not inspected. The capture gives no publication date, license, underlying code, dataset construction, split, evaluation protocol, or uncertainty; its claims were not reproduced. Reddit comments include speculation rather than evidence of mechanisms or general capabilities. No sensitive values or executable content were identified.[^reddit-legal-citations]

The standalone English legal-classifier summary was inspected. It provides no byline, publication date, original URL, license, links to the underlying experiment, dataset, or code, and has no local attachment references. Its figures are explicitly unverified; no experiment was reproduced. No sensitive values or executable content were identified.[^legal-summary-2117695754278142357]

The citation-classifier post and its remotely linked table image were inspected; the shortened link redirects to the post's photo. The image is not locally archived and may become unavailable. The capture does not specify dataset construction, test split, architecture, training baseline, revision procedure, uncertainty, date, or license; no code or evaluation was inspected or reproduced. No sensitive values or executable content were identified.[^citation2117606206764175543]

The Fable 5.1 post and its remote table image were inspected; the image is not locally archived and repeats the earlier table. The capture provides no author, date, license, underlying code, or evaluation protocol. Its model-version and backpropagation claims were not independently checked; no evaluation was reproduced.[^post2117782732654658047]

The Qwen3.8-27B post and remote before/after image were inspected; the image is not locally archived. The shortened link resolves to the post itself. The capture does not state its author, date, license, test sample size, sampling conditions, baseline, quality metric, edit details, or underlying code. The experiment was not independently verified or reproduced; its claimed mechanism and average reduction remain reported only. No sensitive values or executable content were identified.[^post2117808859691811216]

The English ITECS AI explainer by the ITECS Team, dated 2026-11-04, says it checked the primary post and experiment logs but did not reproduce experiments. The article and lead image were inspected; the lead image repeats the summary, and its SVG logo and inline illustrations are decorative or repeat text. External logs, model, and linked business guidance were not inspected for this ingest; the capture supplies no license or local capture date. Promotional material was excluded.[^itecs-explainer]

[^video-cAGCH19xgU8]: Local transcript, passages beginning “Of course, there are skeptics” and “It turns out that the same part of the network”; no timestamps available.
[^legal-summary-2117695754278142357]: Local summary, sole paragraph, attribution and reported classifier results.
[^williams-weight-edit]: Junior Williams, “What the researchers reported,” “Confirmed, claimed and not yet known,” “Verify model integrity,” and “Where this fits my own work.”
[^admix-weight-space]: Admix article, “What actually happened,” “The Qwen result, reconstructed,” “FAQ,” and “Sources.”
[^itecs-explainer]: ITECS Team, “Experiment 6: Working past the context window with tools,” “What this means for IT and business leaders,” and “Sources And Trust Signals.”
[^kingy-weight-space]: Curtis Pyke, Kingy AI, “Following the repetition signal,” “The results behind the 6× and 3× claims,” “No gradients still required feedback,” “A baseline rerun tests the sampling caveat,” “Another harness reports an Opus edit and a thinking-off comparison,” “A downloadable checkpoint and a separate MATH-500 rerun,” and “How to inspect and rebuild the released edit.”
[^reddit-sparks-discussion]: Reddit capture, “TL;DR,” “What Comes Next?,” and comments beginning “To stop spreading misinfo,” “I work in this field,” and “What about catastrophic forgetting?”
[^mindstudio-weight-space]: Luis Chavez-Mattos, MindStudio, “Where does the 6x math gain actually come from?”, “Why does Qwen’s own documentation matter here?”, “Does weight editing add new capabilities or just remove blockers?”, and “Is this result reliable and what should builders take away from it?”
[^datacamp-weight-space]: Local DataCamp article, “Fixing reasoning loops in Qwen3.5-0.8B” and “How to Try Weight-Space Programming Yourself.”
[^reddit-legal-citations]: Reddit capture, headline and comment beginning “Big user of legal AI”; linked main preview image, Alex post and Jacob Lauritzen post with accuracy table.
[^post2119416808273019037]: Local post, opening paragraph, “Result,” and “Reproduce” paragraph.
[^critique2118072016670732400]: Local post, opening paragraph and replication claim ending “1/n.”
[^post2117808859691811216]: Local post, three paragraphs; linked `HWP2vT6a4AAGz5E.jpg`, before/after token labels.
[^post2117782732654658047]: Local post, opening paragraph and forecast; linked `HWPgLAyXAAEp2Eq.jpg`, accuracy table.
[^citation2117606206764175543]: Local post text and linked `HWM_n5IWQAAymo0.jpg`, table columns “Weights,” “Labels seen,” “Non-zero params,” and “Test accuracy.”
[^summary2117422816438145164]: Local summary, bullets beginning “Given only the rules” and “On a model that didn't have the looping problem,” and final quotation.
[^takehi2026]: Takehi et al., experiments 4–6 and 8, including “Setup,” benchmark tables, “Raising math capability of a model that does not loop,” and “What Comes Next?”.
[^critique2117416640132366570]: Local critique, paragraphs beginning “Math up to 6x,” “only 0.016% of weights,” “To the car,” and “20x higher than PPO.”
[^community1412375]: OpenAI Developer Community, “Weight Space Programming,” replies beginning “I haven’t tried your benchmark” and “Then I took Pocket TTS weights”; local image, read/fix/improve panels.
