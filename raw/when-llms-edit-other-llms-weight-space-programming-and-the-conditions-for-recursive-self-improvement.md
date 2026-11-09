---
title: 'When LLMs Edit Other LLMs: Weight-Space Programming and the Conditions for Recursive Self-Improvement'
subtitle: The evidence behind GPT-6 Astra’s Qwen weight edits, their relationship to fine-tuning, and the conditions for continual learning and…
tags:
- Weight Space Programming
- Llm Fine Tuning
- Continual Learning
- Knowledge Distillation
- Ai Self Improvement
published: '2026-11-04'
free: false
freedium_url: https://freedium-mirror.cfd/https://medium.com/@adnanmasood/when-llms-edit-other-llms-weight-space-programming-and-the-conditions-for-recursive-2dceaec05403
source_url: https://medium.com/@adnanmasood/when-llms-edit-other-llms-weight-space-programming-and-the-conditions-for-recursive-2dceaec05403
---

# When LLMs Edit Other LLMs: Weight-Space Programming and the Conditions for Recursive Self-Improvement

*The evidence behind GPT-6 Astra’s Qwen weight edits, their relationship to fine-tuning, and the conditions for continual learning and…*

*Published Nov 04, 2026 · Free: No*

#### The evidence behind GPT-6 Astra's Qwen weight edits, their relationship to fine-tuning, and the conditions for continual learning and recursive self-improvement.

> **TL;DR:** Weight-space programming uses a language model to inspect another model and directly change the numerical weights that control its behavior. In the reported Qwen experiment, GPT-6 Astra edited about 0.016% of the weights and raised MATH-500 accuracy from 7.9% to 48.1%. The evidence points mainly to fixing repetitive reasoning that prevented answers from finishing, while a [Gemma follow-up](https://github.com/RikiyaT/lm_understand-logs/blob/main/exp8_math/gemma_followup/README.md) produced much smaller gains. Fine-tuning usually learns weight updates through gradients; this procedure used a language model to design them, supported by practice data and repeated evaluations. The relationship is between an editor and a target, while teacher-student distillation trains one model to imitate another model's behavior. Continual learning would require successive edits to add capabilities while preserving earlier ones, and recursive self-improvement would require improved models to become better at producing further improvements. I would treat this as a promising tool for model repair and test its reliability before deploying an autonomous editor.

### **Weight-Space Programming Explained: How LLMs Edit Neural Network Weights**

On November 2, Rikiya Takehi and colleagues at the Massachusetts Institute of Technology's Computer Science and Artificial Intelligence Laboratory released _Sparks of Weight-Space Programming_. Their report describes a **large language model (LLM)**, a neural network trained to generate language, inspecting other networks and writing changes to their **weights**, the numerical parameters that determine how those networks compute. In its most striking experiment, GPT-6 Astra edited approximately 0.016% of Qwen3.5-0.8B's weights. The researchers reported a roughly sixfold increase in its MATH-500 score. [1] [rikiyat.github.io](https://rikiyat.github.io/blog/weight-space-programming/?utm_source=chatgpt.com)

<picture>
  <source media="(max-width: 768px)" srcset="/img/medium/700/1*VtLHGBFKPTahs4c4CiQOyw.png 1x">
  <source media="(min-width: 769px)" srcset="/img/medium/2000/1*VtLHGBFKPTahs4c4CiQOyw.png 1x">
  <img src="/img/medium/700/1*VtLHGBFKPTahs4c4CiQOyw.png" alt="None" width="1588" height="774" loading="lazy" data-zoom-src="/img/medium/4000/1*VtLHGBFKPTahs4c4CiQOyw.png" class="prose-image" data-caption="[https://rikiyat.github.io/blog/weight-space-programming/](https://rikiyat.github.io/blog/weight-space-programming/)"/>
</picture>

The small percentage attracts attention. I find the diagnosis more consequential. The edited model had a severe tendency to repeat its reasoning until it exhausted its generation budget. Astra identified a direction in the model's internal computation associated with that repetition and changed two layers to suppress it. A large amount of previously unusable performance became available.

My reading is that this is a credible early demonstration of automated model repair. It introduces another way for an AI system to participate in model development: inspect a network, form a hypothesis about a failure, and author a targeted intervention. Its implications for continual learning and recursive self-improvement depend on whether that process can acquire new capabilities and preserve them through repeated changes.

<picture>
  <source media="(max-width: 768px)" srcset="/img/medium/700/1*GgMtKLqGQVUR_-TvjFeWqw.png 1x">
  <source media="(min-width: 769px)" srcset="/img/medium/2000/1*GgMtKLqGQVUR_-TvjFeWqw.png 1x">
  <img src="/img/medium/700/1*GgMtKLqGQVUR_-TvjFeWqw.png" alt="None" width="1626" height="1262" loading="lazy" data-zoom-src="/img/medium/4000/1*GgMtKLqGQVUR_-TvjFeWqw.png" class="prose-image" data-caption="[https://rikiyat.github.io/blog/weight-space-programming/](https://rikiyat.github.io/blog/weight-space-programming/)"/>
</picture>

As of November 3, the public release consists of a research report, experimental records, editing artifacts, and a reconstructed checkpoint. A **checkpoint** is a saved set of model parameters. I would evaluate the work through those artifacts while treating its broader claims as research hypotheses. [1], [2]

### The Qwen result is largely a repair to how reasoning terminates

The main experiment used Qwen3.5-0.8B with thinking enabled. The model frequently continued generating repetitive reasoning until it reached the limit of 32,768 new **tokens**, the pieces of text a language model processes. [3] A mathematical answer buried inside an unfinished generation has limited practical value. The relevant measure is whether the model returns a usable, correct answer.

<picture>
  <source media="(max-width: 768px)" srcset="/img/medium/700/1*Df-5O1oEH9l90VlRw3atew.png 1x">
  <source media="(min-width: 769px)" srcset="/img/medium/2000/1*Df-5O1oEH9l90VlRw3atew.png 1x">
  <img src="/img/medium/700/1*Df-5O1oEH9l90VlRw3atew.png" alt="A circular arrow depicts repeated reasoning. Before the repair, 93% of Qwen&#39;s MATH-500 generations reached the token limit." width="1920" height="1080" loading="lazy" data-zoom-src="/img/medium/4000/1*Df-5O1oEH9l90VlRw3atew.png" class="prose-image"/>
</picture>

The released benchmark files report the following results for the original model and the successful edit produced with a budget of 50 feedback requests. MATH-500 tests competition-style mathematics. Grade School Math 8K (GSM8K) tests grade-school word problems, while Instruction-Following Evaluation (IFEval) measures compliance with verifiable instructions. [4]

```plaintext
Measure                                        Original model  Edited model  Change
MATH-500 accuracy                              7.9%            48.1%         +40.2 percentage points
GSM8K accuracy                                 13.8%           67.1%         +53.3 percentage points
IFEval accuracy                                21.0%           62.3%         +41.3 percentage points
MATH-500 generations reaching the token limit  93.0%           33.1%         -59.9 percentage points
```

The sixfold figure is approximately 48.1 divided by 7.9. It describes the change in MATH-500 accuracy under the reported settings. The researchers averaged correctness across sampled responses, including four samples per MATH-500 problem. Every unsuccessful response counted against that average. [4]

<picture>
  <source media="(max-width: 768px)" srcset="/img/medium/700/1*Z2TyJUG5IvHRo9BU5iIukg.png 1x">
  <source media="(min-width: 769px)" srcset="/img/medium/2000/1*Z2TyJUG5IvHRo9BU5iIukg.png 1x">
  <img src="/img/medium/700/1*Z2TyJUG5IvHRo9BU5iIukg.png" alt="Two bars compare the original Qwen score of 7.9% with the edited score of 48.1% on MATH-500." width="1920" height="1080" loading="lazy" data-zoom-src="/img/medium/4000/1*Z2TyJUG5IvHRo9BU5iIukg.png" class="prose-image"/>
</picture>

The strongest explanation comes from a separate analysis of 1,152 held-out practice problems. The edit rescued 579 answers and introduced five regressions. Of those 579 rescues, 576 had previously been truncated. Aggregate accuracy on answers that the original model had finished was essentially unchanged. These practice results are separate from the benchmark scores in the table. [5]

That pattern supports a specific interpretation: the intervention helped Qwen complete computations it could already perform. The closest analogy is releasing a stuck brake. The improvement in motion is real, and the cause tells us which other vehicles might benefit from the same repair.

This distinction matters for the claim that an LLM can teach another LLM mathematics by editing its weights. Acquiring a new procedure would require evidence that the edited model can solve a class of problems beyond its previous competence. The Qwen experiment provides stronger evidence for recovering usable performance from a model whose reasoning control was malfunctioning.

The researchers' Gemma follow-up helps separate those explanations. Gemma 3-270M-IT had far fewer looping failures. Under the follow-up's lenient, format-independent grading, its MATH-500 score began at 6.8%; edits produced 7.0%, 7.6%, 7.7%, and 7.0% across the tested feedback budgets. The largest increase was 0.9 percentage points. Gemma's architecture and evaluation setup differ from Qwen's, so this is an informative follow-up with imperfect experimental matching. The small gains, considered alongside Qwen's practice analysis, support the interpretation that repairing loops explains much of Qwen's improvement. [6]

### Astra authored a structured intervention in two layers

**Weight-space programming** is the researchers' term for using an LLM to reason about neural computation and produce weight changes directly. In the Qwen run, Astra used diagnostic observations to identify internal patterns associated with repetitive versus productive reasoning. It then wrote code that modified selected parts of two matrices. [7]

Those matrices belong to **multilayer perceptrons (MLPs)**, the feedforward components within the **transformer**, a neural-network architecture for processing sequences. An MLP's down-projection maps its expanded internal representation back into the shared representation passed through the network. The final patch targeted 64 columns of the MLP down-projection in each of layers 15 and 19, covering 131,072 parameter entries, approximately 0.016% of the model. [7]

<picture>
  <source media="(max-width: 768px)" srcset="/img/medium/700/1*ucb65c33RerDXdQPt4YBxg.png 1x">
  <source media="(min-width: 769px)" srcset="/img/medium/2000/1*ucb65c33RerDXdQPt4YBxg.png 1x">
  <img src="/img/medium/700/1*ucb65c33RerDXdQPt4YBxg.png" alt="Stacked grids highlight the 64 selected columns in each of layers 15 and 19, covering 0.016% of Qwen&#39;s weights." width="1920" height="1080" loading="lazy" data-zoom-src="/img/medium/4000/1*ucb65c33RerDXdQPt4YBxg.png" class="prose-image"/>
</picture>

For readers comfortable with linear algebra, the intervention can be expressed as:

<picture>
  <source media="(max-width: 768px)" srcset="/img/medium/700/1*kn3Glrn1qm34LMY3Sufb-A.png 1x">
  <source media="(min-width: 769px)" srcset="/img/medium/2000/1*kn3Glrn1qm34LMY3Sufb-A.png 1x">
  <img src="/img/medium/700/1*kn3Glrn1qm34LMY3Sufb-A.png" alt="W_edited = W_original − αu((uᵀ W_original) ⊙ m)." width="1600" height="170" loading="lazy" data-zoom-src="/img/medium/4000/1*kn3Glrn1qm34LMY3Sufb-A.png" class="prose-image"/>
</picture>

Here, _W_ is one selected weight matrix. The vector _u_ represents a diagnosed repetition direction for that layer, _m_ selects the columns to change, and _α_ controls the intervention's strength. The released edit uses a strength of six. The operator ⊙ means element-by-element multiplication. [7]

The practical meaning is simpler: reduce selected neurons' contribution along a direction associated with looping. This is a **sparse edit**, because it touches a small fraction of parameter entries, and a **rank-one update** within each selected matrix, because the change is constructed from an outer product of two vectors.

Parameter coverage and behavioral impact are different quantities. A change to a small set of weights can affect many inputs because those weights participate in computations reused throughout the model. The 0.016% figure describes where the intervention was applied; its consequences still require broad evaluation.

The word "native" also deserves a precise reading. Astra was a general-purpose model carrying out the investigation and generating editing code. An external execution setup ran Python and returned results. This was an interactive computational process, with the model acting as an investigator and programmer. [8] [github.com](https://github.com/RikiyaT/lm_understand-logs/?utm_source=chatgpt.com)

### Gradient-free editing still requires evidence and computation

Conventional **fine-tuning** adapts a pretrained model by optimizing its parameters on additional examples. A **gradient** tells the optimizer how a small change to each trainable parameter would affect a chosen objective. **Backpropagation** is the procedure used to compute those gradients through the network.

The Qwen editing experiment prohibited backpropagation, optimizers, and iterative loss fitting. Astra had access to practice data and could request feedback from the target. It proposed and tested interventions using its existing knowledge and the observations returned by its tools. [3]

That is a meaningful algorithmic difference. In ordinary fine-tuning, an optimizer supplies the update direction from a differentiable objective. Here, an LLM designed a structured transformation using a diagnosis of the network's behavior. The process remains empirical: observations determine whether a proposed change is useful.

<picture>
  <source media="(max-width: 768px)" srcset="/img/medium/700/1*uSKf-sorVlG0ngAEV6Z4Tw.png 1x">
  <source media="(min-width: 769px)" srcset="/img/medium/2000/1*uSKf-sorVlG0ngAEV6Z4Tw.png 1x">
  <img src="/img/medium/700/1*uSKf-sorVlG0ngAEV6Z4Tw.png" alt="Two panels compare a gradient-based update learned from a loss with a targeted weight transformation designed by a reasoning model." width="1920" height="1080" loading="lazy" data-zoom-src="/img/medium/4000/1*uSKf-sorVlG0ngAEV6Z4Tw.png" class="prose-image"/>
</picture>

The terminology depends on scope. If fine-tuning means gradient-based adaptation, the two procedures differ. If it means any persistent post-training change, direct editing falls within that broader category. For an engineering comparison, I would specify the update rule and the evidence used to choose it.

The experiment's "50 passes" also needs context. A pass was a batched feedback request. Depending on its type, a request could generate answers for up to 512 practice problems or inspect internal information for up to 1,024 texts. The successful run involved 158 turns and 80 Python executions, taking about 20.3 hours, including a reported 4.7-hour outage. Both the editor and the target brought their prior training into that process. [3] [github.com](https://github.com/RikiyaT/lm_understand-logs/blob/main/exp8_math/README.md?utm_source=chatgpt.com)

For an engineering team, the relevant cost is the entire successful repair. That includes editor **inference**, the computation used to run the model, alongside target evaluations and unsuccessful candidates. Verification adds further expense. The size of the final patch tells us little about the cost of discovering it.

### The evidence supports a promising intervention with a narrow demonstrated scope

The release includes final edits and enough reconstruction information to test them. A Hugging Face checkpoint card reports an external reconstruction that achieved 51.0% on the full edited MATH-500 evaluation. Its original-model comparison used a 25-problem smoke test. This strengthens confidence that the released patch works while leaving the autonomous discovery process and a complete matched baseline comparison for further replication. [2] [huggingface.co](https://huggingface.co/RikiyaT/Qwen3.5-0.8B-weight-space-programming?utm_source=chatgpt.com)

The discovery record also matters. The principal feedback-budget results represent individual runs. Earlier prompt variants and unsuccessful attempts existed, and broader evaluation was applied to selected promising edits. **Survivorship bias** arises when successful candidates receive most of the attention while the search that produced them becomes less visible. The release supports exploratory findings; estimating reliability will require repeated fresh runs and an accounting of failures. [9]

The broader report includes another useful demonstration: constructing small game-playing networks from known rules. In three MinAtar games, the generated policies outperformed the reported reinforcement-learning baseline trained for 100 million steps. Against the 500-million-step baseline, the generated policy won on one of the three games. **Reinforcement learning** trains a policy through rewards from an environment. The rule-informed construction setup gives the LLM a different source of information, which matters when interpreting the comparison. [10] [github.com](https://github.com/RikiyaT/lm_understand-logs/blob/main/exp5_write_from_scratch/README.md?utm_source=chatgpt.com)

These results suggest a potential route from explicit domain knowledge to a compact executable network. They give researchers a concrete hypothesis to test in small controllers and constrained tasks.

### Fine-tuning already includes selective parameter updates

A common misunderstanding in the discussion is that fine-tuning requires retraining an entire model. **Parameter-efficient fine-tuning** adapts a model by training a limited set of parameters or added modules.

The best-known example is **Low-Rank Adaptation (LoRA)**. In their 2021 paper, Edward Hu and colleagues describe freezing the original weights and training small matrices whose product supplies an update. LoRA can greatly reduce the number of trainable parameters. Once merged, its low-rank update can change many entries in an original weight matrix. [11] [arxiv.org](https://arxiv.org/abs/2106.09685?utm_source=chatgpt.com)

This makes two distinctions useful. A sparse edit changes relatively few entries. A low-rank update has a compact mathematical representation. The Qwen patch has both properties within the edited matrices; LoRA's defining property is low rank.

The methods can be compared along the information used to choose an update:

<picture>
  <source media="(max-width: 768px)" srcset="/img/medium/700/1*Ja8R_I96yFG8F2Y7GwRZng.png 1x">
  <source media="(min-width: 769px)" srcset="/img/medium/2000/1*Ja8R_I96yFG8F2Y7GwRZng.png 1x">
  <img src="/img/medium/700/1*Ja8R_I96yFG8F2Y7GwRZng.png" alt="None" width="1672" height="941" loading="lazy" data-zoom-src="/img/medium/4000/1*Ja8R_I96yFG8F2Y7GwRZng.png" class="prose-image"/>
</picture>

```plaintext
Approach                        How the adaptation is chosen                              What changes
Full fine-tuning                Gradients computed from training examples                 A broad set of model weights
LoRA                            Gradients train small added matrices                      A compact parameterization of a weight update
Targeted model editing          A specified correction and an editing procedure           Selected internal computations or associations
Weight-space programming        An LLM investigates behavior and authors an intervention  Parameters chosen by the editor
Retrieval-augmented generation  Relevant information is selected at query time            The material supplied to the model
Knowledge distillation          A student learns from a teacher’s behavior                The student’s parameters
```

**Retrieval-augmented generation (RAG)** supplies retrieved documents or records as context when the model answers. Its usual advantage is that changing a document can change the information available to the system without a parameter update. Weight edits provide a different kind of persistence: the changed behavior resides in the model checkpoint.

The appropriate choice depends on the failure. A changing company policy may be best represented in an accessible document store. A recurrent computational defect may justify an internal intervention. A broad new skill may benefit from training on representative examples. An adaptation system can use all of these mechanisms.

### Targeted model editing has a substantial research history

The technical precedent for editing weights is well established. The new work extends that history by putting a general-purpose LLM in charge of the investigation.

<picture>
  <source media="(max-width: 768px)" srcset="/img/medium/700/1*F9AfrA-8IAInlkKdz_Y_tg.png 1x">
  <source media="(min-width: 769px)" srcset="/img/medium/2000/1*F9AfrA-8IAInlkKdz_Y_tg.png 1x">
  <img src="/img/medium/700/1*F9AfrA-8IAInlkKdz_Y_tg.png" alt="Four panels show LoRA low-rank adapters, ROME and MEMIT factual edits, the learned MEND editor, and an LLM-authored weight edit." width="1920" height="1080" loading="lazy" data-zoom-src="/img/medium/4000/1*F9AfrA-8IAInlkKdz_Y_tg.png" class="prose-image"/>
</picture>

In _Locating and Editing Factual Associations in GPT_, Kevin Meng and colleagues introduced **Rank-One Model Editing (ROME)**, which changes a selected internal association through a targeted matrix update. The final weight write is analytical, while the original implementation uses gradient optimization to find a target internal representation. Calling the complete ROME procedure gradient-free would therefore be inaccurate. [12] [arxiv.org](https://arxiv.org/abs/2202.05262?utm_source=chatgpt.com)

The same research group later introduced **Mass-Editing Memory in a Transformer (MEMIT)** to update many factual associations. Eric Mitchell and colleagues' **Model Editor Networks using Gradient Decomposition (MEND)** trains an auxiliary editor that transforms gradients into useful parameter changes. These approaches differ in the editor's training and the structure of the update. [13], [14] [arxiv.org](https://arxiv.org/abs/2210.07229?utm_source=chatgpt.com)

An earlier line of work, **HyperNetworks**, uses one neural network to generate weights for another. David Ha, Andrew Dai, and Quoc Le described that architecture in 2016. The existence of a network writing another network's parameters therefore predates the current report. [15] [arxiv.org](https://arxiv.org/abs/1609.09106?utm_source=chatgpt.com)

What distinguishes weight-space programming is the use of a general-purpose LLM to select and implement an intervention through an open-ended reasoning process. The editor can inspect evidence, write diagnostic code, and revise its hypothesis. Its competence comes from broad prior training, with the current task specified through instructions and feedback.

The strongest counterargument is that this repackages known model-editing operations that a skilled researcher could select more efficiently. At the level of an individual matrix update, that criticism has merit. The research-automation claim depends on whether an LLM can repeatedly identify useful interventions for unfamiliar failures at an acceptable cost. A comparison with researcher-designed edits under recorded resource budgets would help establish its value.

### Prompt Baking uses a different adaptation mechanism

**Prompt Baking**, described by Aman Bhargava and colleagues in 2024, is a separate technique that also moves behavior into model parameters. It aims to make a model behave as though it had received a particular prompt, even when that prompt is omitted from later use. [16]

<picture>
  <source media="(max-width: 768px)" srcset="/img/medium/700/1*HXRyfWxGkZDjSwmh_a_jew.png 1x">
  <source media="(min-width: 769px)" srcset="/img/medium/2000/1*HXRyfWxGkZDjSwmh_a_jew.png 1x">
  <img src="/img/medium/700/1*HXRyfWxGkZDjSwmh_a_jew.png" alt="Prompt Baking diagram. A prompt conditions behavior, distillation learns from it using gradients, and parameters retain the behavior." width="1920" height="1080" loading="lazy" data-zoom-src="/img/medium/4000/1*HXRyfWxGkZDjSwmh_a_jew.png" class="prose-image"/>
</picture>

The procedure optimizes the adapted model to match the output distribution of the original model conditioned on the prompt. In effect, the prompted model supplies behavior that the adapted model learns to reproduce. The paper uses gradient-based optimization. [arxiv.org](https://arxiv.org/abs/2409.13697?utm_source=chatgpt.com)

That gives the two approaches different starting points. Prompt Baking begins with behavior induced by text and trains that behavior into weights. The Qwen weight-space experiment begins with a diagnosed computational failure and applies a directly authored transformation.

An instruction that works consistently in context might be a candidate for baking. A loop associated with a particular internal direction might be a candidate for weight editing. Their shared destination, persistent parameter changes, leaves room for different ways to discover those changes.

### Teacher, student, parent, and editor describe different relationships

**Knowledge distillation** trains a student model to reproduce useful behavior from a teacher. Geoffrey Hinton, Oriol Vinyals, and Jeff Dean's 2015 paper formalized an influential version using the teacher's output probabilities. A teacher can also supply examples or reasoning traces that become training data. [17] [arxiv.org](https://arxiv.org/abs/1503.02531?utm_source=chatgpt.com)

That is a relationship defined by supervision. The teacher supplies behavior the student learns from. In weight-space programming, the editor supplies a change to the target's implementation.

<picture>
  <source media="(max-width: 768px)" srcset="/img/medium/700/1*4nfVR4pAtNil0gSCxF3G7Q.png 1x">
  <source media="(min-width: 769px)" srcset="/img/medium/2000/1*4nfVR4pAtNil0gSCxF3G7Q.png 1x">
  <img src="/img/medium/700/1*4nfVR4pAtNil0gSCxF3G7Q.png" alt="Three diagrams contrast teacher-to-student supervision, parent-to-child lineage, and an editor&#39;s intervention on a target." width="1920" height="1080" loading="lazy" data-zoom-src="/img/medium/4000/1*4nfVR4pAtNil0gSCxF3G7Q.png" class="prose-image"/>
</picture>

"Parent" and "child" usually describe lineage: one model or agent version was derived from another. A parent can also act as a teacher, but lineage alone tells us little about the update mechanism. The same-sized model can teach a successor; a more capable editor can repair a smaller target; several peers can exchange supervision.

Several established topologies illustrate the distinction:

```plaintext
Relationship                            What moves between participants                      Purpose
Teacher to student                      Predictions, examples, or probability distributions  Transfer behavior or compress a model
Teacher to assistant to student         Supervision through an intermediate model            Bridge a capacity gap
Peer to peer                            Predictions used for mutual supervision              Improve jointly trained models
Earlier generation to later generation  Supervision from a preceding model                   Improve a successor, sometimes at the same size
Weight generator to target              Parameters generated by another network              Produce a target’s weights through a learned mapping
Editor to target                        Code or parameter changes                            Alter the target’s internal computation
Proposer and evaluator                  Candidate changes and measured outcomes              Search for improvements under external tests
```

Teacher-assistant distillation explicitly studies an intermediate model between teacher and student. **Deep Mutual Learning** trains peers using one another's predictions. **Born-Again Networks** demonstrates that a student can match the teacher's architecture and still improve through distillation. Each was established in its own experimental setting. [18], [19], [20] [arxiv.org](https://arxiv.org/abs/1902.03393?utm_source=chatgpt.com)

The table also separates who proposes a change from who evaluates it. That division becomes more consequential as adaptation becomes autonomous. A candidate-generating model can be persuasive about its own work. Held-out tests need to establish whether the target improved.

For an enterprise implementation, I would design around an editor, a versioned target, and an evaluation process with its own evidence. The same architecture can accommodate a LoRA update or a direct matrix patch.

### Continual learning requires useful history to survive the next update

**Continual learning** means acquiring useful knowledge or capabilities over time while retaining what remains relevant from earlier experience. A single successful edit establishes adaptation at one point in time. A continual-learning system must survive a sequence.

Consider an illustrative support model that receives a policy correction, learns a new troubleshooting procedure, and later adapts to a revised product. Each change can interact with previous behavior. A policy correction may make an earlier response obsolete; a new procedure may accidentally damage performance on older products. The system needs a way to distinguish intended replacement from unintended forgetting.

<picture>
  <source media="(max-width: 768px)" srcset="/img/medium/700/1*1KGA-2JAufPNvSELTWlGVA.png 1x">
  <source media="(min-width: 769px)" srcset="/img/medium/2000/1*1KGA-2JAufPNvSELTWlGVA.png 1x">
  <img src="/img/medium/700/1*1KGA-2JAufPNvSELTWlGVA.png" alt="Four successive model versions illustrate testing retention of earlier capabilities after each update." width="1920" height="1080" loading="lazy" data-zoom-src="/img/medium/4000/1*1KGA-2JAufPNvSELTWlGVA.png" class="prose-image"/>
</picture>

Sparse updates help make changes smaller and potentially easier to track. Parameter count alone provides no guarantee that edits will compose. A neuron selected for one intervention may contribute to several capabilities, and the useful direction for one failure may overlap with computations needed elsewhere.

There is direct evidence for this concern in earlier editing research. In _Model Editing at Scale Leads to Gradual and Catastrophic Forgetting_, Akshat Gupta and colleagues examined sequences of ROME and MEMIT edits and found deterioration in previously edited facts and downstream performance. Subsequent work on revised ROME also showed that implementation details could account for some abrupt failures. The practical lesson is to measure sequential behavior for the specific editing procedure under consideration. [21], [22] [arxiv.org](https://arxiv.org/abs/2401.07453?utm_source=chatgpt.com)

I would evaluate continual learning through a history of updates. After each edit, the target should face fresh examples of the new task and a retained set of earlier tasks. That record should distinguish new knowledge acquired, previous capabilities preserved, and intentional changes to outdated information.

Several complementary technologies address parts of this problem. External memory keeps facts and experiences accessible through retrieval. **Replay** reintroduces earlier examples during adaptation to help preserve previous behavior. Modular adaptations can isolate some changes, while routing determines when each module should be used. Those choices require evaluation of their own, especially where tasks overlap.

**Titans**, introduced by Ali Behrouz and colleagues, studies neural memory that can adapt at test time. Google Research's **Nested Learning** work studies learning processes operating at different update timescales. Both offer approaches to managing adaptation and memory within a system. Their contribution concerns how information is learned and retained; weight-space programming concerns how an external reasoning model can design a parameter intervention. [23], [24] [arxiv.org](https://arxiv.org/abs/2501.00663?utm_source=chatgpt.com)

**Self-Adapting Language Models (SEAL)** supplies another useful connection. Adam Zweiger and colleagues train a model to generate its own adaptation data and update instructions, then use downstream performance to reward effective self-adaptation. The resulting weight updates use supervised fine-tuning. SEAL demonstrates how an LLM can direct an adaptation process that still relies on conventional gradients. [25] [arxiv.org](https://arxiv.org/abs/2506.10943?utm_source=chatgpt.com)

My expectation is that useful continual-learning systems will combine mechanisms. Retrieval can handle frequent factual changes. Training can consolidate experience into reusable behavior. Targeted editing may repair particular defects. The unresolved engineering work is deciding when to use each mechanism and maintaining evidence that the accumulated system still performs its intended tasks.

### Recursive self-improvement requires the improvement process to get better

**Recursive self-improvement** means that a system's improvements increase its ability to produce further improvements. The object that improves could be the model's weights, its surrounding software, or the procedure used to search for better versions.

The Qwen experiment contains an editor and a separate target. The target's mathematical performance increased while the editor remained fixed. To establish recursion through weight editing, a subsequent experiment would need to show that an improved model becomes a more effective editor, then produces a successor that improves the process again.

<picture>
  <source media="(max-width: 768px)" srcset="/img/medium/700/1*7rWpk7QW8j_6OBhq6A9JVg.png 1x">
  <source media="(min-width: 769px)" srcset="/img/medium/2000/1*7rWpk7QW8j_6OBhq6A9JVg.png 1x">
  <img src="/img/medium/700/1*7rWpk7QW8j_6OBhq6A9JVg.png" alt="A cycle links a new candidate, an improved target, verification, and an improved editor. The next generation must produce better edits." width="1920" height="1080" loading="lazy" data-zoom-src="/img/medium/4000/1*7rWpk7QW8j_6OBhq6A9JVg.png" class="prose-image"/>
</picture>

That distinction allows us to be precise about existing progress. In **Self-Taught Optimizer (STOP)**, Eric Zelikman and colleagues used a language-model-based program improver to improve its own scaffolding code, the software organizing calls to the model. The underlying language model remained unchanged. The work demonstrated a bounded form of recursive improvement in code generation. [26] [arxiv.org](https://arxiv.org/abs/2310.02304?utm_source=chatgpt.com)

The **Darwin Gödel Machine**, introduced by Jenny Zhang and colleagues, explores and evaluates modifications to an agent's own code. The later **Hyperagents** work makes the modification procedure itself editable, combining a task-solving agent with an agent responsible for changes. Its reported improvements include changes to memory and performance tracking that transfer across domains. These experiments provide evidence about self-improving software systems in their tested settings. [27], [28] [arxiv.org](https://arxiv.org/abs/2505.22954?utm_source=chatgpt.com)

Google DeepMind's **AlphaEvolve** offers another route. It combines language-model-generated programs with automated evaluation and evolutionary search. Improvements to algorithms or computing infrastructure can make subsequent AI work more effective even when the language model's weights remain fixed. [29] [deepmind.google](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/?utm_source=chatgpt.com)

Weight-space programming adds a further option: improving the underlying network through directly authored edits. Whether that creates sustained acceleration depends on several conditions. The system must identify improvements that transfer beyond its immediate tests. It must preserve the capabilities that make further research possible. It also needs access to enough compute and sufficiently informative evaluation to distinguish progress from measurement error.

The hardest requirement may be evaluation. A correct numerical answer or a passing software test gives a useful signal. Better scientific judgment, stronger long-horizon planning, or improved research taste is harder to score. A system that optimizes an incomplete measure can become more successful at satisfying that measure while making less useful progress.

I would reserve a claim of sustained recursive improvement for experiments showing successive generations becoming better improvers under controlled resource budgets. If later generations receive more compute, more human guidance, or easier tasks, those contributions need to be separated.

### The immediate applications are model maintenance and research automation

The clearest near-term application is repairing identifiable failures in models an organization can inspect and modify. Repetition is one example. Other candidates could include unwanted behavioral tendencies or brittle responses associated with a measurable internal mechanism. Those are proposed applications, each requiring a separate demonstration.

A second application is automating parts of interpretability research. **Mechanistic interpretability** studies how internal computations produce a model's behavior. An LLM that can formulate a hypothesis, instrument a network, and test an intervention could help researchers examine more failure cases. The usefulness of that assistant would depend on whether its explanations survive causal tests.

Constructing small networks from explicit rules may also be valuable where a compact, predictable controller is useful. The game-policy experiments suggest that a language model's domain knowledge can sometimes be compiled into a network. Extending that approach to practical control tasks would require careful treatment of uncertainty and situations outside the supplied rules.

More speculative applications include transferring capabilities between models and **machine unlearning**, removing a specified influence from a trained model. Both require stronger evidence than a successful behavioral repair. A model may stop producing a response while retaining related information elsewhere, and a parameter change may transfer a behavior without preserving its reliability.

Small edits also have implications for model integrity. In _Refusal in Language Models Is Mediated by a Single Direction_, Andy Arditi and colleagues demonstrated how interventions associated with one internal direction could substantially change refusal behavior. A small parameter footprint can therefore carry a large behavioral consequence. [30] [arxiv.org](https://arxiv.org/abs/2406.11717?utm_source=chatgpt.com)

For a team deploying editable models, I would keep a record of each patch's origin, the model version it targets, and its measured effects on capabilities and safety behavior. The ability to reverse a patch is useful, but recovering a previous checkpoint also reverses any later changes built on it. Sequential editing makes version management a research concern as well as an operational one.

The public evidence also gives us no basis for concluding that frontier laboratories already use this exact technique privately. That proposition would need its own source. It should carry no weight in an investment or architecture decision.

### I would fund a bounded program with explicit promotion criteria

I would begin with a reproducible failure in a small open model and a clear measure of the desired behavior. The initial comparison would include conventional fine-tuning, a parameter-efficient update, and simpler inference controls. Every approach would receive a recorded budget covering discovery and evaluation.

<picture>
  <source media="(max-width: 768px)" srcset="/img/medium/700/1*EuZntVGOlhIyBzuPQOnR6Q.png 1x">
  <source media="(min-width: 769px)" srcset="/img/medium/2000/1*EuZntVGOlhIyBzuPQOnR6Q.png 1x">
  <img src="/img/medium/700/1*EuZntVGOlhIyBzuPQOnR6Q.png" alt="A model patch review checks new-task gains, earlier skills, reproducibility, and total cost before promotion." width="1920" height="1080" loading="lazy" data-zoom-src="/img/medium/4000/1*EuZntVGOlhIyBzuPQOnR6Q.png" class="prose-image"/>
</picture>

The next experiment would repeat the discovery process from fresh starts. A reliable editor should produce useful repairs across different models and failure cases, including cases where its first hypothesis is wrong. The record should include unsuccessful attempts so that a team can estimate cost and success rate.

I would then test a new capability and a long sequence of updates. The new capability should require generalization to unseen examples. The sequence should expose interference between edits and measure how much useful earlier behavior survives. Evaluation problems should remain outside the editor's working data.

A recursive experiment would follow when the repaired model can participate in editing. It would compare that model's ability to produce improvements against its predecessor under the same conditions. Repeating that comparison across generations would establish whether better task performance translates into better improvement capability.

For a deployment decision, I would require reproducible gains on fresh tasks, acceptable performance on retained tasks, and a measured advantage in total cost or reliability over the alternatives. Those results would justify expanding the role of an autonomous editor. Until then, weight-space programming earns a place in a controlled research and model-maintenance program.

### Frequently Asked Questions: Weight-Space Programming and Recursive Self-Improvement

#### 1. What is weight-space programming, and how does it work?

Weight-space programming is an approach in which a large language model examines another neural network's internal parameters and directly modifies them to change its behavior. Rather than relying on gradient descent, the editing model analyzes weights, identifies potential causes of errors, and constructs targeted mathematical interventions. The November 2026 MIT CSAIL research demonstrates this approach on small neural networks and Qwen3.5-0.8B. Its significance lies in making model diagnosis and repair a task that a general-purpose LLM can perform.

#### 2. Is weight-space programming genuinely new, or have researchers been editing model weights for years?

Direct weight editing is not new. Techniques such as ROME, MEMIT, MEND, and hypernetworks have explored targeted parameter modifications or networks that generate other networks' weights. What distinguishes the recent MIT work is using a general-purpose LLM to investigate model internals, diagnose failures, and devise an intervention without separately training a specialized editor. The novelty is primarily in automating the discovery and implementation of the edit, rather than inventing parameter editing itself.

#### 3. How did GPT-6 Astra improve Qwen's math performance by changing only 0.016% of its weights?

Astra identified a recurring failure in Qwen3.5-0.8B: the model repeatedly generated reasoning without reaching a final answer. It traced the behavior to a particular internal direction associated with two MLP layers and modified 131,072 weight entries to suppress it. MATH-500 accuracy increased from 7.9% to 48.1%, while GSM8K rose from 13.8% to 67.1%. The edit primarily restored the model's ability to complete reasoning rather than demonstrating the acquisition of entirely new mathematical knowledge.

#### 4. How is weight-space programming different from fine-tuning, LoRA, and Prompt Baking?

The main difference is how parameter updates are determined. Conventional fine-tuning uses gradients calculated from training examples. LoRA trains smaller, low-rank matrices while keeping the base model frozen. Prompt Baking uses gradient-based self-distillation to make behavior induced by a prompt persist in the model's weights. Weight-space programming instead asks an LLM to diagnose the target and construct a numerical intervention directly. All four can produce persistent behavioral changes, but they use different mechanisms and are suited to different kinds of adaptation.

#### 5. Does gradient-free model editing mean AI can improve without training data or computational expense?

No. Gradient-free means the target's weight changes are not calculated through conventional backpropagation during the editing process. It does not eliminate the editor's prior training or the need for diagnostic evidence. The Qwen experiment used thousands of available practice problems, repeated evaluations, Python executions, and substantial inference computation. Whether this approach is cheaper than fine-tuning depends on the full cost of finding, testing, and validating a successful edit.

#### 6. How does the editor–target relationship differ from traditional teacher–student learning?

In teacher–student distillation, a student learns to imitate a teacher's outputs, probability distributions, or other representations, usually through training. In an editor–target relationship, one model investigates another model's internal computation and changes its parameters directly. Parent–child terminology describes model lineage rather than a particular learning algorithm. These relationships are compatible: a model could inherit weights from a parent, learn through distillation, and subsequently receive targeted edits. They describe different aspects of how models evolve.

#### 7. Can weight-space programming give an LLM entirely new knowledge or reasoning capabilities?

That remains unproven at the scale suggested by the Qwen results. Removing a failure that prevents an existing capability from working differs from creating a capability the model never possessed. The researchers' follow-up with Gemma 3 270M, which did not suffer from the same severe reasoning loops, produced no established mathematical improvement. More convincing evidence would involve acquiring unfamiliar procedures, generalizing to new problem structures, and outperforming appropriate fine-tuning baselines. Targeted repair is demonstrated; broad capability acquisition needs further testing.

#### 8. Could weight-space programming solve continual learning and catastrophic forgetting?

It could become one mechanism within a continual-learning system, but a successful isolated edit does not establish continual learning. A system must accumulate useful changes while preserving earlier knowledge and capabilities. Catastrophic forgetting occurs when adaptation damages previously learned behavior. Small edits may reduce the amount of parameter modification, but they can still interfere with widely shared internal representations. Demonstrating continual learning would require long sequences of edits, retention tests, interference measurements, and reliable methods for resolving conflicting updates.

#### 9. Does this bring us closer to recursive self-improvement or artificial general intelligence?

Potentially, but the demonstrated experiment involves a fixed, capable editor improving a separate target model. Recursive self-improvement requires the resulting system to become better at producing subsequent improvements. That might involve changing model weights, modifying agent code, improving training procedures, or developing better evaluation methods. Research such as STOP, the Darwin Gödel Machine, and Hyperagents investigates related forms of self-improving software. Weight-space programming adds direct parameter modification to the possibilities, but sustained recursive improvement remains an open empirical question. It does not establish artificial general intelligence (AGI).

#### 10. What are the practical applications, and what evidence would justify enterprise adoption?

The strongest near-term applications are targeted model repair, automated interpretability research, and the construction of specialized small networks. An enterprise might eventually use an LLM editor to identify a recurring failure, propose a parameter patch, and validate the resulting checkpoint. Adoption should depend on reproducibility across models, comparison with simpler alternatives, measured total cost, retention of existing capabilities, and independent safety evaluations. The most important milestone is a reliable process for discovering and validating useful edits — not merely another impressive benchmark improvement.

### References & Further Reading

[1] R. Takehi, J. Teoh, A. Zhang, and O. Khattab, "Sparks of Weight-Space Programming: LLMs can natively read & write neural network weights," Nov. 2, 2026. [Research report](https://rikiyat.github.io/blog/weight-space-programming/).

[2] RikiyaT, "Qwen3.5-0.8B-weight-space-programming," Hugging Face model card, 2026. [Checkpoint and reconstruction evaluation](https://huggingface.co/RikiyaT/Qwen3.5-0.8B-weight-space-programming).

[3] R. Takehi et al., "Experiment 8: Math," experimental documentation, 2026. [Protocol and run details](https://github.com/RikiyaT/lm_understand-logs/blob/main/exp8_math/README.md).

[4] R. Takehi et al., "Experiment 8 evaluation results," 2026. [Original model](https://github.com/RikiyaT/lm_understand-logs/blob/main/exp8_math/eval/unedited/merged.json); [edited model](https://github.com/RikiyaT/lm_understand-logs/blob/main/exp8_math/eval/p50c/merged.json).

[5] R. Takehi et al., "Final answer, p50c run," experimental artifact, 2026. [Practice analysis](https://github.com/RikiyaT/lm_understand-logs/blob/main/exp8_math/runs/p50c/final_answer.md).

[6] R. Takehi et al., "Gemma follow-up," 2026. [Experimental documentation](https://github.com/RikiyaT/lm_understand-logs/blob/main/exp8_math/gemma_followup/README.md).

[7] R. Takehi et al., "Final report, p50c run," experimental artifact, 2026. [Intervention and ablations](https://github.com/RikiyaT/lm_understand-logs/blob/main/exp8_math/runs/p50c/work_notes/final_report.md).

[8] R. Takehi et al., "Weight-space programming logs and artifacts," GitHub repository, 2026. [Release documentation](https://github.com/RikiyaT/lm_understand-logs/).

[9] R. Takehi et al., "Results excerpt," 2026. [Selection and evaluation notes](https://github.com/RikiyaT/lm_understand-logs/blob/main/exp8_math/eval/RESULTS_excerpt.md).

[10] R. Takehi et al., "Experiment 5: Write from scratch," 2026. [Game-policy experiments](https://github.com/RikiyaT/lm_understand-logs/blob/main/exp5_write_from_scratch/README.md).

[11] E. J. Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models," arXiv:2106.09685, 2021. [Paper](https://arxiv.org/abs/2106.09685).

[12] K. Meng et al., "Locating and Editing Factual Associations in GPT," arXiv:2202.05262, 2022. [Paper](https://arxiv.org/abs/2202.05262); [target-representation optimization code](https://github.com/kmeng01/rome/blob/main/rome/compute_v.py).

[13] K. Meng et al., "Mass-Editing Memory in a Transformer," arXiv:2210.07229, 2022. [Paper](https://arxiv.org/abs/2210.07229).

[14] E. Mitchell et al., "Fast Model Editing at Scale," arXiv:2110.11309, 2021. [Paper](https://arxiv.org/abs/2110.11309).

[15] D. Ha, A. Dai, and Q. V. Le, "HyperNetworks," arXiv:1609.09106, 2016. [Paper](https://arxiv.org/abs/1609.09106).

[16] A. Bhargava et al., "Prompt Baking," arXiv:2409.13697, 2024. [Paper](https://arxiv.org/abs/2409.13697).

[17] G. Hinton, O. Vinyals, and J. Dean, "Distilling the Knowledge in a Neural Network," arXiv:1503.02531, 2015. [Paper](https://arxiv.org/abs/1503.02531).

[18] S. I. Mirzadeh et al., "Improved Knowledge Distillation via Teacher Assistant," arXiv:1902.03393, 2019. [Paper](https://arxiv.org/abs/1902.03393).

[19] Y. Zhang et al., "Deep Mutual Learning," arXiv:1706.00384, 2017. [Paper](https://arxiv.org/abs/1706.00384).

[20] T. Furlanello et al., "Born Again Neural Networks," arXiv:1805.04770, 2018. [Paper](https://arxiv.org/abs/1805.04770).

[21] A. Gupta, A. Rao, and G. Anumanchipalli, "Model Editing at Scale leads to Gradual and Catastrophic Forgetting," arXiv:2401.07453, 2024. [Paper](https://arxiv.org/abs/2401.07453).

[22] A. Gupta et al., "Rebuilding ROME: Resolving Model Collapse during Sequential Model Editing," arXiv:2403.07175, 2024. [Paper](https://arxiv.org/abs/2403.07175).

[23] A. Behrouz et al., "Titans: Learning to Memorize at Test Time," arXiv:2501.00663, 2025. [Paper](https://arxiv.org/abs/2501.00663).

[24] Google Research, "Introducing Nested Learning: A new ML paradigm for continual learning," Nov. 7, 2025. [Research overview](https://research.google/blog/introducing-nested-learning-a-new-ml-paradigm-for-continual-learning/).

[25] A. Zweiger et al., "Self-Adapting Language Models," arXiv:2506.10943, 2025. [Paper](https://arxiv.org/abs/2506.10943).

[26] E. Zelikman et al., "Self-Taught Optimizer (STOP): Recursively Self-Improving Code Generation," arXiv:2310.02304, 2023; published at COLM, 2024. [Paper](https://arxiv.org/abs/2310.02304).

[27] J. Zhang et al., "Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents," arXiv:2505.22954, 2025. [Paper](https://arxiv.org/abs/2505.22954).

[28] J. Zhang et al., "Hyperagents," arXiv:2603.19461, 2026, revised Nov. 1, 2026. [Paper](https://arxiv.org/abs/2603.19461).

[29] Google DeepMind, "AlphaEvolve: A Gemini-powered coding agent for designing advanced algorithms," May 14, 2025. [Research overview](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/).

[30] A. Arditi et al., "Refusal in Language Models Is Mediated by a Single Direction," arXiv:2406.11717, 2024. [Paper](https://arxiv.org/abs/2406.11717).