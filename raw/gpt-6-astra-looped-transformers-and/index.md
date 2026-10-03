---
title: "GPT-6 Astra, Looped Transformers, and Hidden Reasoning"
author: "Sebastian Raschka, PhD"
site: "Ahead of AI"
published: 2026-09-09T11:14:25+00:00
source: "https://magazine.sebastianraschka.com/p/gpt-6-astra-looped-transformers-and"
domain: "magazine.sebastianraschka.com"
language: "en"
description: "A Look at Recurrent Depth, Hidden Chains of Thought, and Recent Research on Looping Transformer Blocks"
word_count: 6407
---

### A Look at Recurrent Depth, Hidden Chains of Thought, and Recent Research on Looping Transformer Blocks

A lot has happened in the last few weeks. I am sure that OpenAI’s GPT-6 Astra is top of mind for everyone right now. In particular, thoughts on its performance, the looped transformer/recurrent depth aspects, and rumors that Astra is “hiding” its reasoning trace (i.e., chain of thought).

So, in this article, I want to start with some brief impressions of Astra and some thoughts on where all this is headed. Then, I will discuss, in detail, what “looped transformers” are, and how (or rather, if) this relates to hiding chains of thought.

Lastly, after covering the basics of the looped transformer, I wanted to highlight some new insights from recent research papers on the topic.

PS: I also have a shorter video version here that I recorded before writing this more extended article:

![](assets/watch.img)

## 1\. GPT-6 Astra impressions

First things first. Before getting into the architecture rumors and related research literature, let me briefly summarize some GPT-6 Astra observations and tidbits.

Last week, OpenAI’s new GPT-6 Astra was released with a big fanfare. I used it over the past couple of days, and it’s an exceptionally good model, likely the best I’ve used as of this writing. But what, exactly, has it improved, and how?

### 1.1 Astra benchmarks

Astra is the best model I’ve used so far, and it’s disproportionately good at 3D rendering and animation tasks (relative to other models). With that, I mean that while it leapfrogs its GPT-5.6 predecessor in practically all categories (writing, math, coding, and more), it especially does so when it comes to graphical demos.

We can see this also reflected in the benchmarks. For instance, GPT-6 Astra is really good at math and coding, as shown below.

![benchmarks-1](assets/c7647174-392d-4637-a1ab-baf3b24a3704_8765x7510.png)

Figure 1: Selection of three popular coding benchmarks and one challenging math benchmark. More benchmarks are shared on the Astra release blog: https://openai.com/index/gpt-6-astra/

One of the highlights (not shown in the figure) is that Astra also achieves 99.9% on the [ARC-AGI-3 benchmark](https://arcprize.org/arc-agi/3) (GPT-5.6 Sol only 7.8%), which measures a mix of solving logic puzzles and generalization. However, the math, coding, and computer use benchmarks are more interesting because they are closer to real-world use. (However, there was then also an [article](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores/) by OpenAI describing two further changes to the harness that also tripled GPT 5.6 Sol’s performance from to 13.3% to 38.3%.)

Coming back to the [Artificial Analysis Coding Agent Index v1.4](https://artificialanalysis.ai/agents/coding-agents#coding-agents-index) (lower right in the previous figure), which blends several agentic coding tasks, GPT-6 Astra is clearly at the frontier, but it doesn’t pull ahead by leaps and bounds. This can also be seen in the general [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index) shown below, which blends different types of tasks, not just coding tasks.

![artificial-intelligence](assets/d02ced21-56da-4b5b-a520-33f0a20567cf_8058x5120.png)

Figure 2: Artificial Analysis Intelligence Index via https://artificialanalysis.ai/#intelligence

Now, the big advantage of Artificial Analysis benchmarks is that they are independent and thus may be a bit more trustworthy than self-evaluated benchmarks by model developers.

The [harness setup depends on the benchmark](https://artificialanalysis.ai/methodology/intelligence-benchmarking). For example, GDPval-AA and AA-Briefcase use their open-source, minimal [Stirrup](https://github.com/ArtificialAnalysis/Stirrup) harness across the different LLMs they compare. In the Intelligence Index v4.2 shown above, Terminal-Bench v2.1 uses Terminus 2, and τ³-Banking uses the τ-Bench harness. The separate Coding Agent Index also compares different coding-agent harnesses.

For evaluations that use a shared harness, this makes it more of an apples-to-apples comparison. At the same time, during model training, models are typically developed with one primary harness in mind (and fine-tuned less on other harnesses). Plus, the primary harness is often developed to suit and amplify a model’s strengths.

So, some of the agentic evaluations might underestimate how well Astra performs in its primary harness. How much this affects its Intelligence Index score would need to be tested by comparing Astra across harnesses on the same tasks.

As a side note, as a colleague recently suggested to me (as also recommended by the Claude Code lead), it’s maybe not a bad idea to delete (/archive) some of your existing `AGENTS.md` contents and `SKILL.md` files, as newer LLMs have become more efficient at understanding the prompt and solving the problem at hand. The extra hand-holding could unnecessarily constrain newer models and lead to worse solutions.

Of course, I am not suggesting never using `SKILL.md` files again, but for some workflows, because they can improve efficiency upon reuse, since the model doesn’t have to rediscover them. But what I am suggesting is that some workflows don’t need describing, and “old” descriptions may no longer be ideal, and the LLM may be able to come up with better solutions. So, it’s perhaps time to update or regenerate said instruction files.

### 1.2 Computer use capabilities

GPT-6 Astra seems to be exceptionally strong in image and rendering tasks. When these tasks involve interacting with graphical user interfaces, they also demonstrate computer-use capabilities, meaning the model operates software on your local computer through the Codex/ChatGPT app.

Computer use is where the model really shines compared to others, and anything graphic-related also makes for interesting and intuitive demos on social media platforms. There are tons of examples of impressive demos out there, from modeling [rendering New York City in blender](https://x.com/higgsfield_ai/status/2096495974734794840?s=20) to [virtual open house tours](https://x.com/Dimillian/status/2095596700815516004?s=20).

To pick one example, below is a comparison where I had GPT-6 Astra Medium and High redraw a picture of me in a [browser version of MS Paint](https://jspaint.app/#local:aa1757d4bc6008) using the mouse on my computer (not Extra High and Max, because I didn’t want to waste all my tokens:)).

This highlights not only the model’s artistic capabilities but, more importantly, its ability to use tools on one’s computer (in this case, Paint; you can see the model using the interface via the mouse cursor).

This is not the first model that, inside a harness, is capable of general computer use. For example, I successfully used GPT models for some UI tasks (e.g., expense-related tasks in Excel) and so on since earlier this year. However, computer use is a relatively new capability, enabled by the harness, and usually feels not quite as mature yet. This makes sense. LLMs are text models, so naturally the lower-hanging fruit is writing and coding and using APIs and CLIs.

At the same time, there are many tools and software that don’t expose CLIs (yet), and instead of waiting until someone designs that interface, why not improve models to use graphical user interfaces (and, as mentioned before, this makes for pretty and impressive demos, anyway)? This is somewhat analogous to the emerging humanoid robot developments. Sure, humanoid robots are not the most efficient robots, for example, at the assembly line, where special-purpose machines exist. But they are versatile.

So, I expect the upcoming months (or years) also to be an era of computer use refinement on both the LLM and the agent harness layer. I.e., in addition to the current capabilities, and expanding their math and coding capabilities, models will be trained with an increasing amount of computer use in mind. And this will also make LLMs more accessible for everyday computer tasks outside the tech world (”Hey ChatGPT, please do my tax return”:))

### 1.3 Computer use training

The computer usage trend is also consistent with the [recent reporting](https://finance.yahoo.com/technology/ai/articles/apple-suddenly-ai-infrastructure-stock-130223938.html) that OpenAI purchased tens of thousands of Mac Minis and Mac Studios for Reinforcement Learning. So, here the Macs are not used to literally train the models (it’s better to use GPUs for that) but rather to expose macOS during the model training for the model to learn to use said operating system and the tools therein.

So, how does computer-use training on said Macs work? In short, the Macs (or their macOS operating system, to be precise) serve as an environment that the model can interact with during training.

The basic workflow looks like this:

1. Prompt the model by giving it a task, such as “open an app xyz and do abc”.
2. Provide it with screenshots of the macOS interface (this is usually done by the harness).
3. The LLM then predicts mouse/keyboard actions (click, key presses, scrolling, and so on).
4. Execute those actions on the Mac (again, this is done by the harness).
5. Feed new screenshots of the updated environment after performing the actions in the previous step.
6. Repeat steps 2-5 until the task succeeds or fails.
7. Use success/failure signals and verifiers (or graders) as training feedback, including reinforcement learning during post-training; this is analogous to regular Reinforcement Learning with Verifiable Rewards (RLVR).

![computer-use-flow](assets/105c079e-822e-4de9-bd16-2afe56286541_4879x2744.png)

Figure 3: Overview of a computer-use training workflow.

Again, the Mac is mostly the environment here and not the machine for running or updating the model during training. The model likely sits on NVIDIA GPUs and is fed via API to said Mac. By the way, [NVIDIA’s CEO mentioned](https://x.com/JensenHuang/status/2096700264569090384?s=20) that GPT-6 Astra was being trained on ~100,000 Grace Blackwell GPUs.

### 1.4 GPT-6 Astra is still a reasoning model

The focus on computer-use training discussed in the previous section is not a fundamental paradigm shift in the training pipeline. GPT-6 Astra (and likely any LLM in the foreseeable future) is still a reasoning model. This means the LLM is trained with reinforcement learning with verifiable rewards (RLVR) and produces intermediate reasoning traces (chains of thought)

But I will discuss the reasoning model aspects of GPT-6 Astra (especially regarding hiding chains of thought) a bit later in this article.

## 2\. Looped transformers

That being said, about two days before the official model, the news magazine The Information published an [article](https://www.theinformation.com/articles/secret-technique-behind-openais-astra-model-sparks-security-concerns) reporting that, according to some inside information, Astra is using a concept called “recurrent depth” or “looped transformers.”

![the-information](assets/b5611bff-b063-4082-8ed5-bed48619cd1b_3674x3073.png)

Figure 4: Quote from The Information (Source: https://www.theinformation.com/articles/secret-technique-behind-openais-astra-model-sparks-security-concerns )

Since LLM architectures are within my area of expertise and my passion, I created a short lecture video explaining the general looped transformer mechanism and addressing the comment about hidden reasoning chains, which you can find below.

![](assets/watch.img)

In the following subsections, I’ll first explain what looped transformers are, and I’ll revisit the comment about the hidden chains of thought later in this article.

(The looped transformer explanation may seem a bit long, but I really think that it helps with establishing a foundational understanding of the technique, which is then useful to judging the claim that it obscures the reasoning traces or chains of thought.)

### 2.1 Reusing transformer blocks

So, what’s a looped transformer?

A Looped Transformer is essentially an architectural tweak, with the main idea being to pass the intermediate representations through the same transformer blocks multiple times (instead of just once). Compared to just adding more blocks, the “trick” here is that the weights stay the same across these passes.

---

**Definitions & Jargon**

Throughout this article, I’ll use the following terms:

- A **transformer block** is a unit containing attention, a feedforward module, normalization, and shortcut connections. These blocks are often called “transformer layers” in papers.
- A **stack** is a sequence of transformer blocks.
- A **block application** means running an input through a transformer block once.

---

The looped transformer is nothing new, and the basic idea already appeared in the [Universal Transformers](https://arxiv.org/abs/1807.03819) paper from 2018. But before discussing Universal Transformer, let’s start with a simpler example, [Nanbeige4.2-3B](https://arxiv.org/abs/2607.22083), a recent open-weight LLM that came out in July and that I covered on Substack [Notes](https://substack.com/@rasbt/note/c-302083551) and in my [LLM Architecture Gallery](https://www.sebastianraschka.com/llm-architecture-gallery/looped-depth-sharing/) earlier this summer.

The Nanbeige architecture, shown below, essentially looks like a regular transformer. However, notice that it has an extra (orange) arrow looping back to the beginning of the transformer stack.

![nanbeige](assets/d41d18af-38d4-4925-97c3-175a1b9443cd_2682x2664.png)

Figure 5. Nanbeige4.2-3B applies the same stack of 22 transformer blocks twice. The orange arrow shows where the intermediate representations are passed back into the stack.

Let’s walk through this from the bottom up. First, as in any other transformer-based LLM, the input text is tokenized and converted into embedding vectors. These vectors then pass through 22 transformer blocks, and each of these 22 blocks has its own weights.

However, the looping transformer aspect here is that after the first pass, the hidden states are fed back through the same 22 blocks. So, block 1 is applied again, followed by block 2, and so on up to block 22.

If we were to unroll this computation, we would have 44 transformer block applications. However, compared to a conventional transformer with 44 distinct blocks, the second stack of 22 block applications reuses the weights from the first stack. For example, block application 23 uses the weights of block 1, block application 24 uses the weights of block 2, and so on.

![nanbeige-two-passes](assets/6c447af3-6466-473a-8ba3-0759b798e187_1867x3427.png)

Figure 6. Nanbeige4.2-3B unrolled into two passes through the same 22 transformer blocks, giving 44 block applications.

So, the whole idea here is that we increase the effective depth from 22 to 44 block applications without adding another set of transformer weights.

By the way, why 2 rounds, not 3, 4, or more? There are not many details in the Nanbeige paper, but they say that this was essentially the most efficient setup. Increasing the loops from 2 to 3 can increase modeling performance, but the extra computational cost wasn’t worth it.

### 2.2 Looping costs

So, why would we do this looping in general? This is essentially an alternative to just making the model bigger by adding more transformer blocks.

So, for instance, a model that uses 22 transformer blocks twice has roughly half as many (transformer-block) parameters compared to a model with 44 conventional blocks.

This then reduces the memory needed to store the weights. As a side note, note that the embedding and output layers, which are usually large and make up a substantial portion of the total, are separate from this comparison. (In the case of Nanbeige 4.2 3B, the embedding and output layers make up ~25% of the total 3B parameters; with weight sharing between those two, we could reduce that to 12.5%.)

![hypothetical-size](assets/1c43d5a9-a977-49ef-a3f8-6e643c381f13_4708x2488.png)

Figure 7: Side-by-side comparison showing how many parameters would be required in traditional versus looping scenarios.

Of course, reusing the same blocks in a loop still requires computation. More precisely, we pass the intermediate inputs through 44 block applications during the forward pass. And, during training, gradients flow backward through both repetitions of the shared stack. So, compared to using the 22 blocks only once, this adds substantial work. Actually, it’s similarly expensive as having 44 distinct blocks (except the optimizer has fewer distinct parameters to update; backprop still runs through all 44 block applications).

There is also the KV cache, which stores the attention keys and values of previous tokens for reuse in conventional and looped transformers in each next-token generation step. By the way, I have a standalone article on KV caching here if useful:

But back to the topic. Even though there is weight-sharing in looped transformers, the intermediate states that enter a block are different on the second pass. Consequently, in KV caching, the resulting keys and values are also different between these two transformer stacks (just like in the no-looping case). So, there are no KV cache-related savings either.

To make this more concrete, for example, consider block applications 1 and 23, which both use block 1 in the looped transformer setup. But each application still needs its own KV cache entries. So, since we have to keep separate caches for both passes, the repeated stack of 22 blocks has the same KV cache requirements as a conventional transformer with 44 distinct blocks.

Interestingly, the Nanbeige researchers reported in the paper that they tried sharing the KV cache between passes. This, of course, halved the KV cache size, but the model performed worse than the version with separate caches (which is the version they released).

Just to complete the Nanbeige discussion before moving on and looking at some other looped transformer designs, their [technical report](https://arxiv.org/html/2607.22083v1#S2.SS1) also discusses two other choices or trade-offs.

1. Training the looped architecture from scratch worked better than converting an already pre-trained transformer through upcycling.
2. And two passes gave their preferred trade-off, as mentioned in the previous section. More passes brought only small additional gains while slowing training and making optimization less stable.

So, the number of passes is another architectural choice we have to make. As mentioned before, in Nanbeige, this is fixed at two. But we can also make it depend on the token, as we will see next.

### 2.3 Universal Transformers and flexible loop counts

Now, let’s come back to [Universal Transformers](https://arxiv.org/abs/1807.03819). In Nanbeige, we apply a stack of 22 transformer blocks twice. In the Universal Transformer paper from 2018, we repeatedly apply the same transformer block instead of repeating a stack of transformer blocks. The main idea is similar, though.

Also, the number of steps can be fixed, but the paper also explores adaptive halting. For example, a token at a particular position may only go through one or two loops. Another may go through three or four loops, and so on. This gives the model flexibility to allocate the compute to those tokens that benefit from extra computation.

How is the looping number decided? Here, the model uses a small, trained function that outputs a so-called halting probability for each position at each step. It adds up these probabilities over these successive loops and then stops looping at a given position once the sum exceeds a threshold value. In addition, a maximum loop count also limits the computation just in case.

![adaptive-halting](assets/2a0d4a0f-621b-4f6e-a7cd-7778c7346efb_4694x2256.png)

Figure 8: Adaptive halting in a Universal Transformer.

Another example of a looped transformer is ByteDance’s [Ouro](https://arxiv.org/abs/2510.25741), which I also covered in my [LLM Architecture Gallery](https://sebastianraschka.com/llm-architecture-gallery/looped-depth-sharing/). For instance, Ouro-Thinking 2.6B applies the same stack of 48 transformer blocks four times. That’s 192 block applications while storing weights for 48 distinct blocks. Basically, that’s a more extreme case than Nanbeige. Additionally, a learned exit gate assigns probabilities to the different exits, and a threshold on the cumulative probability determines which pass supplies the output. So, it’s also borrowing the adaptive halting idea from Universal Transformer, which Nanbeige didn’t use. (However, there is a practical caveat here. The released [Hugging Face implementation](https://huggingface.co/ByteDance/Ouro-2.6B-Thinking/blob/main/modeling_ouro.py) computes all configured passes before selecting an output, so it seems like the number of loops is effectively hard-coded to 4).

### 2.4 Routing flexible loop counts

Another approach is [Mixture-of-Recursions](https://arxiv.org/abs/2507.10524), a paper from 2025 that is essentially a more sophisticated version of the Universal Transformer discussed earlier. Similar to the Universal Transformer, individual tokens pass the transformer blocks one or more times as illustrated in the figure below. However, the innovation is how this looping number is determined on a per-token basis.

In the following figure from the paper, the looped (repeated) stack is called a recursion block here. This contains several transformer blocks, and it sits between separate first and last transformer blocks (labeled Layer 0 and Layer L-1).

![mor](assets/b9850015-07f9-4f73-9034-5d7a3224d767_6922x4628.png)

Figure 9. Mixture-of-Recursions applies a shared stack a different number of times at different token positions. The highlighted text shows an example with 1, 2, or 3 passes. Figure adapted from the Mixture-of-Recursions paper.

How does the model decide how many times a token should go through the recursion block? In the previously discussed Universal Transformer, it’s based on a learned halting probability at each step. This Mixture-of-Recursion approach here uses a small, learned router. This is similar to the routing idea in a mixture-of-experts model, except that here the routing decision determines how many times to apply the shared stack.

The router operates on a token’s hidden representation, which also contains information about its context. So, we shouldn’t think of this as assigning every occurrence of a particular token the same number of passes (i.e., the word “People” in the figure above doesn’t always go through a loop of 3). The decision can change depending on where that word appears and what came before it.

Now, how does the routing work exactly? The paper explores two ways to make this routing decision, as illustrated below.

![mor-routing](assets/971afd67-da8b-4d14-8aac-36279754b7c5_6312x2851.png)

Figure 10. Two ways to choose the recursion depth. On the left, routers select which tokens continue at each step. On the right, a single router assigns the number of passes at the beginning. Figure from the Mixture-of-Recursions paper.

In *expert-choice routing*, which is shown in the left subpanel in the figure above, each recursion step selects which tokens it will process. Tokens that exit are excluded from later steps. In *token-choice routing*, shown on the right, the router makes one decision at the beginning, assigning each token to a path with one, two, or three passes.

In both cases, the transformer weights are reused across passes, similar to Nanbeige, etc. But the additional flexibility comes from choosing how much computation each token receives. The model and its routers are trained together, so the model learns to work with these different paths during training.

### 2.5 How well does this work?

The plot from the Mixture-of-Recursions paper below compares a regular transformer (Vanilla), a transformer with fixed recursion (Recursive), and Mixture-of-Recursions (MoR) for different model sizes and compute budgets (x-axis).

![mor-results](assets/a7d21ed3-cf75-45a1-ac2f-dc1a0ba705fb_8617x2565.png)

Figure 11. Validation loss across four model scales and three training compute budgets. Figure from the Mixture-of-Recursions paper.

At the smallest model scale, the regular transformer performs best. For the larger models, Mixture-of-Recursions catches up and often performs better, especially at the smaller training budgets. At the largest budget, several of the curves are very close. So, the advantage depends on the model size and how much compute we spend on training.

Another detail here is that equal training compute doesn’t necessarily mean an equal number of training tokens. By skipping some computation, Mixture-of-Recursions can process more tokens within the same budget.

I think this is an interesting example because it shows that there are several choices within the looped-transformer idea, that is, how many loops there are at each position and how that’s decided.

So, in short, we can say that using looped transformers can improve model quality at a fixed compute budget if the model is large enough. (It also illustrates the importance of running some experiments at scale; e.g., just looking at the smaller 135M parameter model, we would have drawn the opposite conclusion.)

## 3\. Side note: Recurrent Neural Networks (RNNs)

By the way, if you have a background in deep learning (or even artificial neural networks in the 1990s), the looping or “recurrent depth” idea should be somewhat familiar. Remember recurrent neural networks (RNNs)? The whole idea in RNNs is to reuse the layers (weights) from a previous iteration.

![rnn](assets/b12eda20-8fb1-4c5c-a9fa-6212d0abb759_4088x3398.png)

Figure 12: Illustration of an RNN (from my 2022 “Machine Learning with PyTorch and Scikit-Learn book”, https://amzn.to/3YzRnPR )

The main distinction is that RNNs reuse their weights across time steps. That is, the hidden state is carried forward from one token to the next. In the looped transformer, the looping of a token is across the architecture depth.

Or, in other words, in a conventional RNN, each step takes the next element in the input sequence and the hidden state from the previous step. So, when the RNN is processing a chunk of text, it reads one word or token at a time and carries information from the earlier words forward in its hidden state.

In a looped transformer, the intermediate representation of a given token goes through the transformer stack multiple times. The model still uses attention to pass information between tokens.

If this analogy is a bit too confusing, don’t worry about it too much. A perhaps simpler way to think about looped transformers is to think of them as reusing transformer blocks, similar to making the model bigger but with weight sharing.

![rnn-vs-looped-transformer](assets/7a37b812-26b3-4d55-846a-2c86c28e518a_5055x2663.png)

Figure 13: Side-by-side comparison of the “recurrence” in an RNN and a looped transformer.

## 4\. Does Astra even use looped transformers?

Before we discuss whether the looped transformer mechanism obscured reasoning traces, as rumored in The Information quote from earlier, does GPT-6 Astra even use the looped transformer concepts?

![the-information-2](assets/59a0eb95-7843-40d9-bd59-ee79f0cf2022_3674x3073.png)

Figure 14: Quote from The Information (Source: https://www.theinformation.com/articles/secret-technique-behind-openais-astra-model-sparks-security-concerns )

We have to keep in mind that this is still just a rumor or scoop, with no official confirmation. If the model were open-weight, we could double-check this ourselves, of course, but in this case we have to rely on unverified reporting.

However, I think it’s highly likely that GPT-6 Astra uses looped transformer aspects. First, there is the reporting mentioned above. Second, it’s a technique that has shown promise in past studies (as discussed earlier), so why not? Third, OpenAI’s chief scientist [said the following](https://x.com/merettm/status/2095023204993490967?s=20).

> \[...\] The depth of the computation graph for our present frontier models, including Astra, is within a factor of two of GPT-4. \[...\]

However, this doesn’t confirm the looped transformer architecture explicitly, and it could also just mean they use twice as many regular transformer blocks.

In my opinion, the success (i.e., good modeling performance) behind Astra is likely primarily due to other reasons, namely improved training recipes and training data.

The looped transformer tweak might help a bit, but I think that The Information is overestimating its contribution.

## 5\. Hiding chains of thought

Next, let’s finally address the elephant in the room: does looped transformer obscure the reasoning traces?

First, OpenAI has been hiding (most of) the reasoning traces from users from the very beginning, since OpenAI o1, anyway. So, for the end-user, there shouldn’t be a big difference.

So, the interpretation-concern is mostly with respect to the model developers.

Either way, I don’t think that looped transformers are significant contributors towards hiding or obscuring chains of thought. To explain my own reasoning (no pun intended), let’s take a step back and explain how reasoning models work.

### 5.1 Reasoning in brief

Reasoning models typically generate intermediate steps before producing a final answer. These steps use regular text token (that are optionally hidden from the user in some user interfaces) and called a reasoning trace or chain of thought.

For example, say we ask for two numbers whose sum is 10 and whose product is 21. In the figure below, the model tries 5 and 5 at first. While the sum is correct, the product is 25, not 21. Next, it then tries 3 and 7 and checks both conditions again.

![backtracking](assets/5e45da87-e3ca-47cd-b84f-c1a10c102e34_2942x1521.png)

Figure 15. An illustrative LLM response annotated to show intermediate steps, backtracking, and the final answer.

The figure illustrates how a reasoning model “reasons,” including backtracking. That is, the model notices a mistake, then revisits an earlier choice, and then continues with a different approach.

Note that the model still generates one token at a time, using the prompt and previous tokens as context. So, these intermediate steps work as a scratch pad and add computation before the final answer.

The final answer can then be much shorter than the reasoning trace that preceded it, as shown in the example above. (OpenAI tends to hide most of the reasoning traces from the users.)

For more details on understanding and developing reasoning models, I recommend my book [Build a Reasoning Model From Scratch](https://amzn.to/4aAKiFY).

![reasoning-book](assets/8e53a1b1-4d0d-47f1-baa8-e9a0f0269d27_4545x3015.png)

Figure 16: My Build a Reasoning Model From Scratch book covers the fundamentals of reasoning models.

### 5.2 Token usage and shorter chains of thought

Now, extra tokens in the reasoning trace add more computation. Looped transformers add more computation, because the tokens go through more transformer blocks. One might argue that a model with looping uses more computation internally, it doesn’t need as many external thinking tokens.

Below is a selection of the [GPT-6 benchmarks](https://openai.com/index/gpt-6-astra/) with the output token number on the x-axis.

![output-tokens](assets/3faf505f-8ea7-477b-af46-d7b355f5e3d4_7645x6659.png)

Figure 17: Selected GPT-6 Astra benchmarks from https://openai.com/index/gpt-6-astra/

We can see that GPT-6 Astra doesn’t necessarily use fewer tokens than its GPT 5.6 Sol predecessor across effort levels overall. However, at a fixed accuray, it is true that GPT-6 Astra uses fewer tokens than GPT 5.6 Sol.

Is this a concern for interpretability? Not necessarily. Using fewer tokens could just mean that the model is more capable and makes fewer mistakes, uses less backtracking, and so on. I.e., it might just get more things right on the first try. To me, that doesn’t raise an immediate concern regarding interpretability.

I mean, the same is true for previous models. I don’t think that anyone has strong concerns that GPT 5.6 Sol is so much less interpretable than the smaller GPT 5.6 Luna model, which uses many more tokens for the same task performance, as shown below.

![luna-sol-token-usage](assets/1e048a54-2b50-423c-a7e7-87edd933cb1f_5324x2149.png)

Figure 18: Token usage in Luna and Sol at similar task performance levels. Numbers from the Artificial Intelligence Index v4.3.

In fact, as we can see that Luna uses 80% more tokens than Sol at similar modeling performance. Does that make Sol that much less interpretable?

Rather, the more plausible answer here is that more capable (bigger, well-trained models that use more compute) can solve problems more efficiently, where “efficient” here means fewer tokens.

It’s also worth keeping in mind that a reasoning trace is [not guaranteed to faithfully describe](https://arxiv.org/abs/2305.04388) everything that happens inside the model. In my view, the only valid concern is that looped transformers purposefully mislead users by presenting “fake” reasoning traces more often than conventional transformers. But I don’t think we have any strong evidence that this is happening.

Now, Astra’s system card does state that there is also evidence of reduced monitorability of their reasoning traces, and there is a bit of regression relative to Sol. It’s mostly associated with shorter, less informative traces. But again, this doesn’t establish looping as the root cause. It could just be due to the shorter length in general, similar to the Luna vs Sol example above.

A few hours after I shared [my thoughts](https://x.com/rasbt/status/2095141254958858496?s=20) about looped transformers with respect to hiding reasoning chains, Jakub Pachocki (OpenAI’s Chief Scientist) also [shared the following clarification](https://x.com/merettm/status/2095023204993490967?s=20):

> I want to prevent a race into unmonitorability kicked off by confused reporting. The depth of the computation graph for our present frontier models, including Astra, is within a factor of two of GPT-4. OpenAI has worked to preserve and utilize chain-of-thought monitoring since our very first reasoning models. We deeply care about this technique, as it can give us a view into how model alignment generalizes from its training distribution. I do think it is fragile and unfortunately trending in a negative direction, for reasons not contingent on architecture changes that I will write about soon. But there are things we can do to strengthen it, and it’s a core goal of our current research program.

The “confused reporting” likely refers to The Information’s aforementioned paragraph here, implying that the looping aspect does not have anything to do with chain-of-thought changes.

## 6\. Looped transformer research

Lastly, I want to share some interesting papers related to looped transformer architectures beyond the ones we already discussed.

### 6.1 Latent reasoning

Related to the Universal Transformer, the 2025 [Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach](https://arxiv.org/abs/2502.05171) paper studies how a model can use additional loops at inference time. For this, they trained a relatively modest but also not super tiny 3.5B-parameter model on 800B tokens.

Instead of reusing the same block over and over again as in the Universal Transformer, it repeats a stack like in Nanbeige; however, in contrast to Nanbeige, it sandwiches this shared stack of four blocks between 2 initial and 2 final blocks.

Also, what’s different from Nanbeige is that the shared stack receives the output of the initial blocks at the start of every loop, in addition to the previous loop’s hidden state. These are concatenated and passed through a learned linear projection before entering the four shared blocks. You can think of this as giving the stack access to the same initial input representation on every pass. This whole layout is summarized in the figure below.

So, in short, this is an additional and interesting looped transformer variant.

![latent-reasoning](assets/825fc53f-1111-40a6-b264-17bc092c6ea0_7393x3148.png)

Figure 19. Conceptual summary of the latent reasoning model in Geiping et al..

An interesting detail is that the researchers vary the number of loops during training. This prepares the model to work with different amounts of computation at inference time.

Here, during training, the loop count is randomly sampled. At inference, a fixed budget is chosen by whoever runs the model, such as 8, 32, or 64 loops. Additionally, they have an adaptive stopping mechanism for each token based on the next-token probability distribution. If the KL-divergence between 2 successive rounds is below a certain threshold, i.e., if the distributions are too similar, the looping is halted.

The overall benefit depends on the task. In their evaluations, HellaSwag performance largely levels off after about eight loops, while GSM8K and HumanEval benefit from more.

However, while the title of the paper mentions “latent reasoning”, the model can still generate a textual chain of thought. Looping just gives it additional computation before each output token.

### 6.2 Knowledge retrieval vs reasoning

There’s a useful distinction between storing information and using it to solve a problem. For instance, the [Beyond Parameters: Exploring Virtual Logic Depth for Scaling Laws](https://arxiv.org/abs/2506.18233) paper from June 2025 investigates this by measuring memorization and reasoning in an LLM separately.

First, in the memorization experiments, looping leaves the amount of stored information nearly unchanged when the parameter count stays fixed. Increasing the number of distinct parameters does increase this capacity. From this, we can conclude that looping doesn’t add or let’s the model retrieve more knowledge. This makes sense. Information retrieval is a relatively simple task once the information is stored. Also, looping in itself is computing not “storing” mechanism.

Second, in separate reasoning experiments, reusing the blocks improves performance on multi-step math problems without adding parameters. This is interesting. Here, we can conclude that extra computation can help a model solve problems even when it doesn’t have more space to store information. But again, bigger models can also improve reasoning (although they add parameters as well).

![capacity](assets/92b8a84b-b032-45b7-bdfe-8bc0ea30dc39_8185x5312.png)

Figure 20. In this memorization test, capacity grows with parameter count but changes little with additional block applications. Annotated figure from Zhu et al.

### 6.3 Looping at a matched compute budget

The just-released [SMELT: Scaling Laws for Compute-Matched MoE Looped Transformers](https://arxiv.org/abs/2609.01343) paper from September 2026 comes back to the cost comparison from section 2.2. What happens if we compare looped and conventional transformers with approximately the same compute per token, total non-embedding parameters, and KV cache requirements?

The researchers use a mixture-of-experts architecture and apply the middle half of the transformer blocks twice, kind of similar to Nanbeige except with the sandwiching in Latent Reasoning.

However, they narrow the hidden dimension to compensate for the compute needed for the extra block applications. And then, because that makes the parameter count smaller, they then add experts to recover the total parameter count. They also adjust the attention head configuration to keep the KV cache comparable.

![SMELT worked example comparing model width, experts, block applications, parameters, compute, and KV cache](assets/4fb8b33b-9a12-4a86-97fd-62e9ce4a4637_6724x2983.png)

Figure 21. SMELT overview from the example given in SMELT, section 3.2.

The experiments scale up to 54B non-embedding parameters and so on. Then, from fitted scaling curves, the researchers estimate that SMELT requires about 6.8-18% less training compute to reach the same validation loss within the studied compute range.

So, this answers the question of whether looped transformers are worth it computationally: Yes! They give us a slightly better model when using the same compute budget.

### 6.4 Full-bandwidth transformer

Finally, the also very recent [Full-bandwidth transformer](https://arxiv.org/abs/2608.08888) paper from August 2026 studies recurrence across token positions. At each decoding step, it combines the previous token’s final hidden state with the newly sampled token’s embedding through a learned gate. This becomes the input for the next forward pass.

So, the next token’s computation has access to the previous token’s final representation from the bottom of the stack, which is somewhat similar to Latent Reasoning.

When using a 1B base model, they found that their latent feedback approach outputs shorter reasoning traces on MATH500 while maintaining or improving accuracy. However, the shortening effect disappears after instruction tuning.

![length](assets/4d348be9-2792-4405-9325-adab29ce5323_7946x4070.png)

Figure 22. Latent feedback shortens reasoning traces in the base model, but this effect disappears after instruction tuning. Adapted from Wang et al., Figure 6, CC BY 4.0. Definitions and caveats added.

Anyway, this is interesting because this connects directly to the earlier discussion about whether looping results in shorter reasoning traces. The result depends on both the feedback mechanism and how the model is trained, of course. Also, the experiment doesn’t establish whether those shorter traces are less faithful.

Also, the big caveat of the study is that they didn’t test whether increasing the size of the model in conventional ways (adding more transformer blocks instead of looping) has a similar effect on the reasoning trace lengths.

## Conclusion

To wrap it all up, we can say that yes, OpenAI GPT-6 Astra is a very strong model. And it’s making a particularly large leap in computer use. I believe computer use will be the next big focus area for open-source and proprietary harnesses in the upcoming months. I find open-source especially important when it comes to computer use, as “with great power come great responsibilities”, and it’s nice to be able to audit the harness before giving it access to my main computer.

Besides, GPT-6 Astra is likely to use a variant of the looped transformer. Looped transformers simply give better modeling performance at a fixed compute budget.

Also, better modeling performance may decrease in shorter reasoning chains. But this is not a new trend. We have always seen that within a model family with models of different sizes (e.g., GPT 5.6 Luna versus Sol).

In my opinion, shorter reasoning traces are a side effect of more “intelligent” or capable models that make fewer mistakes and can access more compute internally inside their architecture versus using a reasoning trace as a scratchpad. In a sense, the same is true for humans. During an in-person college math exam, a smart and well-prepared student likely requires less use of the notepaper and needs to backtrack less often, and so on.

---

**Thanks for reading and supporting my work!**

If you’d like to learn how to build reasoning models yourself, check out my book [Build a Reasoning Model (From Scratch)](https://amzn.to/4aAKiFY). We start with a pre-trained LLM and add reasoning capabilities step by step, with code you can run and experiment with. It’s both fun and rewarding, and a good investment in future-self to build the fundamentals to keep up with the AI field.

Also, if you’ve read one of my books, I’d appreciate a short, honest review on Amazon. Reviews help other readers decide whether a book is right for them and are a simple way to support authors.

![scratch](assets/e6fb7c68-790c-47c7-8324-05f100efb90b_4410x2252.png)

Figure 23: Selected illustrations from my Build a Reasoning Model (From Scratch) book, covering inference-time scaling, distillation, and reinforcement learning.
