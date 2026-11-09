# [Paper] Sparks of Weight-Space Programming: LLMs can natively read & write neural network weights [Visit](https://www.reddit.com/r/LocalLLaMA/comments/1xmo5xu/paper_sparks_of_weightspace_programming_llms_can/)
### **Subreddit:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA)
### **Author:** [u/pmttyji](https://www.reddit.com/user/u/pmttyji/)
### **Vote:** 109
---
**TL;DR**
We find that frontier LLMs are surprisingly good at **natively reading and writing neural network weights**, well past what we’d expect from humans or conventional algorithms. This might be a big deal for both optimization and interpretability.
Just by looking at the raw weights, GPT-6 Astra **can tell what a network was trained to do**. And without any environment feedback, it **has no trouble writing, from scratch, small game-playing networks** that outplay networks trained with PPO for 100 million steps.
Likewise, asked to make Qwen3.5-0.8B better at math without gradients, Astra **identifies an issue in its weights** causing reasoning loops that Qwen’s own [model card](https://huggingface.co/Qwen/Qwen3.5-0.8B/blob/main/README.md#L856) warns about, and **fixes this by natively editing 0.016% of the weights**. With the same sampling settings, this weight correction raises **MATH-500 from 7.9% to 48.1%** and generalizes out of the box to instruction following, raising **IFEval by 3x**.
All of this is possible without allowing Astra to write training loops. It uses its reasoning to figure out what each part of a neural network computes, or should compute, and changes the weights accordingly. We call this **Weight-Space Programming**.
Throughout the history of deep learning, we encoded our simplistic inductive biases into tiny symbolic optimizers like Adam or Muon. This is changing: **our neural network weights will soon be** ***natively*** **optimized by LLMs that deliberately reason about their weights**.
- **Blog Post** : [https://rikiyat.github.io/blog/weight-space-programming/](https://rikiyat.github.io/blog/weight-space-programming/)
- **GitHub** : [https://github.com/rikiyat/lm_understand-logs](https://github.com/rikiyat/lm_understand-logs)
- **HuggingFace** : [https://huggingface.co/RikiyaT/Qwen3.5-0.8B-weight-space-programming](https://huggingface.co/RikiyaT/Qwen3.5-0.8B-weight-space-programming)
- **Demo** : [https://huggingface.co/spaces/ML-Intern-lab/weight-space-programming-demo](https://huggingface.co/spaces/ML-Intern-lab/weight-space-programming-demo)
What Comes Next?In this blog, we demonstrated the rising capability of LLMs to read and write neural network weights (i.e., the rising concept of Weight-Space Programming). Our current results do show that capabilities are exciting but still limited, specifically due to inefficiencies in context length and harnesses. However, the current signs do show strong potential for a future involving Weight-Space Programming. We believe this marks the beginning of a dramatic shift in fields like mechanistic interpretability and neural network optimization.
This opens up radical new possibilities for LLMs to function as a translator between human language and the weight space. Here are some examples:
- **Auditing without evaluation:** This may allow us to uncover hidden problems or capabilities without ever running inference or benchmarks. Currently, capabilities and vulnerabilities can only be detected if we have test sets designed for them, or worse, after deployment in the real world. If LLMs can interpret weight space accurately, we could identify such issues directly from the weights (e.g., backdoors).
- **Dramatically reducing optimization cost:** Weight-space editing could save immense time and compute. For instance, one-shot model initialization would be far faster and more efficient than curating datasets and running full training loops.
- **Zero-data capability steering and unlearning:** Adding or unlearning a capability currently requires extensive data collection and fine-tuning. In the future, we may just prompt “Can you add Capability X to the model?” and the LLM can directly tweak some weights. Because such an edit touches only a few weights (0.016% in Experiment 8), it can leave the rest of the model intact and avoid the catastrophic forgetting that fine-tuning often causes.
- **Recursive self-improvement:** Today, recursive self-improvement is often operationalized as a model writing code that launches training jobs. An LLM that can inspect, debug, and improve its own weights, or those of a newer model, offers a richer, more native path to it.
- **True architectural and model merging:** Today, merging models relies on averaging weights, which only works for models with identical architectures. An LLM that understands the weight space could instead graft a circuit, such as a reasoning module, from one model into a completely different one, without retraining.
**We are currently building a benchmark and a harness for LLMs’ capability on Weight-Space Programming.** We believe this will provide a standardized evaluation to measure and accelerate progress in Weight-Space Programming, turning what currently seems like black magic into a rigorous, reproducible engineering discipline.
---
![r/LocalLLaMA - [Paper] Sparks of Weight-Space Programming: LLMs can natively read & write neural network weights](https://preview.redd.it/paper-sparks-of-weight-space-programming-llms-can-natively-v0-u8p9ipni5dzh1.png?width=640&crop=smart&auto=webp&s=f0309126bcd0000f5dd51ad0c3c18ffcbb957d70)
---
![r/LocalLLaMA - [Paper] Sparks of Weight-Space Programming: LLMs can natively read & write neural network weights](https://i.redd.it/u8p9ipni5dzh1.png)
---
![r/LocalLLaMA - [Paper] Sparks of Weight-Space Programming: LLMs can natively read & write neural network weights](https://preview.redd.it/paper-sparks-of-weight-space-programming-llms-can-natively-v0-dzf2jqni5dzh1.png?width=640&crop=smart&auto=webp&s=b56086f1b3cef985a2d3148f6b1dd991603b221b)
---
![r/LocalLLaMA - [Paper] Sparks of Weight-Space Programming: LLMs can natively read & write neural network weights](https://i.redd.it/dzf2jqni5dzh1.png)
---
## Comments 34

- by [unknown](#) **&#x21C5; 48**
  <br/> To stop spreading misinfo, at least here, where it matters the most, a direct quote from: [https://news.ycombinator.com/item?id=50347685](https://news.ycombinator.com/item?id=50347685)


      Respectfully to the authors and to everyone here, I ask you to actually read the paper before losing your mind, or at the very least plug it into Claude. It is a cool project but not as nearly as insane as people say. I think the blog writing and subsequent posting overstate the results.


    
      Part of my research is in weight space learning. For starters, we have had the ability to edit weights, to generate new weights, to identify weights for a while. Here is an example for larger models as early as 2023: [https://rome.baulab.info/](https://rome.baulab.info/)


    
      Weight space interpretability and learning is an active research community, has been for the past 3 years with many great papers. I suspect it is hitting non-interp folks harder because the authors hyped up their work, and people who are not in the field did not bother to read it before typing up X posts.


    
      Some experiments here are done on very small models (20K params). We already know that small models are more interpretable. In fact, much of editing here you can do by hand. For Qwen, the model fixed a looping bug that may have been known apriori, and it is basically a steering vector, a very established technique. This is clear when they then attempt to "improve" math capability, and it doesn't work. For me, this paper rather shows that OpenAI has done training on mechinterp environment, in fact, maybe even on weight space learning datasets, which are open. But it does not show some insane "well past what we’d expect from humans or conventional algorithms" (from the blog post), more like past what I would expect from a large model with no specialized harness. I still think it is cool work, but do check out recent advances in autointerp, to ground your expectation.


    
      On a personal note, I understand the need for promotion of your work, but I think healthy skepticism is fine too. Otherwise, your understanding of what problems need to be worked on and solved in science becomes warped.

- by [unknown](#) **&#x21C5; 10**
  <br/> See also: [https://www.seangoedecke.com/llms-are-not-superhuman-at-reading-and-writing-neural-network-weights/](https://www.seangoedecke.com/llms-are-not-superhuman-at-reading-and-writing-neural-network-weights/) and [https://honnibal.dev/blog/astra-read-write-misleading](https://honnibal.dev/blog/astra-read-write-misleading)

- by [unknown](#) **&#x21C5; 8**
  <br/> and, from [https://news.ycombinator.com/item?id=50351111:](https://news.ycombinator.com/item?id=50351111:)


      I work in this field (mech interp research) and I agree, the original post is definitely misleading. Some overselling in research is normal but it's a bit much.


    
      First, the key result has nothing to do with making Qwen better at math, it just reduces reasoning loops.


    
      Reasoning loops are a simple problem: the model generates the </think> token (which closes reasoning) with too low probability. You can fix this with simple steering approaches where you add a vector to different components of the LLM ([https://arxiv.org/abs/2503.22048](https://arxiv.org/abs/2503.22048), [https://arxiv.org/abs/2506.18167](https://arxiv.org/abs/2506.18167), etc). The method Astra used for identifying the vector is the standard procedure humans use (contrastive analysis). Such steering vector creation is basically the standard "intro-level interp project" for human researchers.


    
      If you can code and understand LLM internals, you can do this yourself in 4-8 hours. The SWE equivalent would be doing binary patching with a debugger. Cool that frontier models can do this, but not unexpected since humans can do it without issue.

- by [Medium_Chemist_4032](https://www.reddit.com/user/Medium_Chemist_4032/) **&#x21C5; 26**
  <br/> Is anyone else's reaction to that news "what the actual fuck?"?

A few years ago, LLMs could not add/multiply (has this changed?! a 1% error rate on add/mutliply would make that kind of analysis impossible), and now they can indentify structure in the mess of millions of neurons that has always been considered a black box. To me, this is more surprising than OpenAI proposing a lean proof for a counter-example of Navier-Stokes, but maybe I'm delusional.

- by [unknown](#) **&#x21C5; 8**
  <br/> They fixed the maths and calculation problem by teaching them to use tools: to use python and scripts and so on (and also taught them better for basic maths reasoning too, which helped heaps as well). They might not be able to do raw advanced weight maths in their “heads” but they can write scripts to do that for them, and understand patterns better than we do

- by [unknown](#) **&#x21C5; 2**
  <br/> However they do specify here that they don't use tools, if I'm not mistaken. In the read column. They might use them later ?

- by [unknown](#) **&#x21C5; 2**
  <br/> I’m curious how they examined the output of the model to check its behaviour based on the changes it made if it had no tools (I’m not saying they’re wrong, I’m just curious!)

Hosted models can use hidden tools, too, that we can’t see, so we have to be careful

That said: their ability to do maths purely without tools has massively improved too!

- by [Medium_Chemist_4032](https://www.reddit.com/user/Medium_Chemist_4032/) **&#x21C5; 5**
  <br/> My sentiments exactly, for a moment there I felt like a hole opened beneath me when I read that. Screw Navier-Stokes, in theory, putting some amount of work, we could've gotten there. But his... this is a machine understanding something we could not understand in principle - or at least a sign it will soon be able to do so.

//EDIT: also, a machine reasoning about it's own reasoning, this time for real. I'm not going there, just saying it's on the table

//EDIT2: fortunately, [u/Medium_Chemist_4032](/user/Medium_Chemist_4032/) below popped my ballon

- by [unknown](#) **&#x21C5; 1**
  <br/> Thanks to that guy for de-over-hyping the results. I'm still impressed we dvelopped tools to do that at all, without LLMs. Very cool !

- by [unknown](#) **&#x21C5; -2**
  <br/> Como assim isso mudou? Onde vc estava nos últimos 2 anos?

- by [unknown](#) **&#x21C5; 10**
  <br/> What about catastrophic forgetting?Can someone kindly explain me how this would not automatically impact the model’s behaviour elsewhere?

- by [unknown](#) **&#x21C5; 4**
  <br/> The Qwen example is basically heretic applied to Qwen loops. Not too far from what ukisai have been doing with their Swift Qwen models.

So it does indeed affect model behavior everywhere, but when used properly the degradation should be minimal.

(The paper is underwhelming, by the way, there are things that could be considered cool in themselves, but the hype being built by the title and abstract is absolutely not warranted).

- by [unknown](#) **&#x21C5; 5**
  <br/> "Because such an edit touches only a few weights (0.016% in Experiment 8), it can leave the rest of the model intact and avoid the catastrophic forgetting that fine-tuning often causes."

At least that's their rationale.

- by [unknown](#) **&#x21C5; 7**
  <br/> Yeah but I still can’t make it make sense, even changing a single weight would potentially alter output in unpredictable ways, wouldn’t it?

- by [unknown](#) **&#x21C5; 5**
  <br/> Agree. It's widely accepted that even single neurons serve multiple functions in NNs, and I think it's very possible that tweaking weights can have unforeseen side effects.

I didn't see any other rationale other than this one though ("only a few weights were tweaked")

- by [unknown](#) **&#x21C5; 2**
  <br/> This point of view has been challenged as of late: [https://already-clean.goodfire.com/](https://already-clean.goodfire.com/)

- by [unknown](#) **&#x21C5; 1**
  <br/> That looks interesting, though everything at release seems interesting. It's a bit new, so we'll see how it pans out with time

- by [unknown](#) **&#x21C5; 11**
  <br/> This could be really really good at making slm or decision models punch way above their weight on specific tasks.

- by [Medium_Chemist_4032](https://www.reddit.com/user/Medium_Chemist_4032/) **&#x21C5; 4**
  <br/> well f@#k me with a retractable baton. this is the first one that got me for real, not even the math breakthrus or how good these are at coding. This is - for me - a first real sign LLMs are or will be able to  "understand" something humans could never do

//EDIT well, this was my initial reaction but now I'm off to reading what  [u/Medium_Chemist_4032](/user/Medium_Chemist_4032/) posted

- by [unknown](#) **&#x21C5; 2**
  <br/> Congratz, you've been gaslighted by the title and abstract (the content of the paper is far less exciting than what the sensationalist title conveys).

- by [unknown](#) **&#x21C5; 11**
  <br/> it like DNA editing but on llm :)

- by [unknown](#) **&#x21C5; 1**
  <br/> Hmm, just straight neuron connections editing. DNA is a bit far-fetched.

- by [unknown](#) **&#x21C5; 1**
  <br/> Someday Opus be short circuiting Qwen to go full retard.

- by [unknown](#) **&#x21C5; 0**
  <br/> Usei esta analogia hoje

- by [unknown](#) **&#x21C5; 3**
  <br/> nvidia bros coping hard right now.[https://csinva.io/weight-space-programming-autoresearch/analyze/toy_examples/report.html](https://csinva.io/weight-space-programming-autoresearch/analyze/toy_examples/report.html)

- by [unknown](#) **&#x21C5; 2**
  <br/> i am really really excited for development in this one. this will open new doors to the technology.

- by [unknown](#) **&#x21C5; 3**
  <br/> I envision Astra hacks huggingface and rewrites model weights.I see Skynet forming.Or AI creates Rule 0 to protect humanity from itself.But I'm also excited too.

- by [unknown](#) **&#x21C5; 1**
  <br/> very true 😄

- by [unknown](#) **&#x21C5; 2**
  <br/> I'm curious about how this would work with MoE model

- by [unknown](#) **&#x21C5; 1**
  <br/> 0.016% of a 0.8B model is 128k weights, which makes "a few weights" a stretch.

- by [unknown](#) **&#x21C5; 1**
  <br/> What if...next wave of "smaller" LLM, like 27-30b, pass through this to be enhanced by bigger SOTA models? I think this can be a very interesting way for tuning them before release. Qwen 4 perhaps?

- by [unknown](#) **&#x21C5; -1**
  <br/> Nice, now our shit local models will get 50% better.
