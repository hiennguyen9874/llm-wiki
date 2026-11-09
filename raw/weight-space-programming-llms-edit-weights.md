## Quick verdict

A frontier model, GPT-6 Astra, opened up a small open-weight model called Qwen3.5-0.8B, changed about 131,000 of its numbers directly, and pushed its MATH-500 score from 7.9% to 48.1%. No training, no gradient descent, just a model reading and rewriting another model's weights like a programmer editing a config file. That is the headline that went around, and it set off a wave of "models can now improve each other" takes. The more careful reading, which came from people who went through the actual logs, is less dramatic and more useful: Astra found a bug that made the little model loop forever until it ran out of tokens, and it turned that bug off. The math ability was already in there. It just could not finish a sentence. That is a real and interesting result. It is not a model teaching another model new math.

## What actually happened

The idea picked up the name "weight-space programming," and the clearest write-up is a blog from researcher Rikiya Takehi that several groups then tried to reproduce. The claim is that today's best models can look at the raw weights of a small neural network, reason about what those numbers do, and edit them toward a goal, without any of the usual training machinery.

A few of those reproductions landed in the same couple of days, which is part of why the story spread:

- Simon Willison ran the weight-reading version on his own laptop with Qwen 3.8 27B and got it to work after about 45 minutes.
- Hugging Face reproduced the paper with its open research harness and published both the model and a demo.
- Alex Krentsel re-ran an earlier MIT experiment across model generations and saw a sharp jump: the newest models generated small game-playing networks that scored up to 22 times an RL-trained baseline.
- One person had a Claude model hand-write a 100,000-parameter network from scratch to tell real legal citations from fake ones, and reported it beat a trained version.

So the basic capability, a model manipulating another network's parameters and getting a working result, shows up across several independent attempts. That part is not hype.

## The Qwen result, reconstructed

The number everyone quoted was the math jump, so it is worth seeing what was under it. A reconstruction from the run logs, picked apart on both Twitter and the r/LocalLLaMA threads, lays out the mechanism:

- Astra edited 131,072 weights, about 0.016% of the model. It did not touch most of the network.
- It located a "repetition direction," the pattern that made the model spiral into repeating itself, mostly in the feed-forward layers 15 and 19.
- It subtracted that direction from the top 64 neurons in each of those layers. That is the whole edit.

Here is the tell. Before the edit, 93% of the model's answers on MATH-500 were hitting the 32,768-token limit, because the model looped instead of stopping. Of the answers the edit "repaired," 576 out of 579 had originally failed by running into that cap. After the edit, the share of answers slamming into the token limit dropped from 93% to about 33%. On a held-out set of problems the model had not been tuned against, accuracy rose from 10.6% to 60.4%.

Read that honestly and it says: the model could already do a lot of this math, but a decoding pathology kept it from ever writing down the answer. Astra found the off switch for the loop. The same intervention did nothing for Gemma 3 270M, a model that did not have the looping problem in the first place, which is the cleanest evidence that this was bug removal, not capability injection.

| Benchmark | Before edit | After edit |
| --- | --- | --- |
| MATH-500 | 7.9% | 48.1% |
| GSM8K | 13.8% | 67.1% |
| IFEval | 21.0% | 62.3% |
| Answers hitting token cap | 93% | 33.1% |

## Why the skeptics have a point

The loudest pushback was not "this is fake." It was "this is a smaller claim than the framing suggests," and the critics were specific about why.

One line of criticism is about baselines. If you fit weights directly against a benchmark, you can make almost any number go up, which is close to meaningless as a measure of general ability. Another reading of the broader results argues the early experiments mostly worked because the first and last layers of a small network have a legible, almost spatial structure that a model can describe like reading a heat map. A third, from people who looked at the harder internal-representation tests, is that the model leaned on its own probes and ablations, which looks a lot like an AI doing agentic interpretability research with a Python sandbox rather than natively "reading weights."

None of that makes the work boring. "A coding agent can act like a competent interpretability researcher, generate hypotheses about a network, test edits, and keep the ones that help" is a genuinely notable thing for a model to do. It is just a different and more grounded claim than "models now rewrite each other to be smarter."

## Why it matters for anyone picking models

Two practical things fall out of this, even if you never touch a weight tensor yourself.

First, be careful with single benchmark numbers, especially huge before-and-after jumps. A score that moves from 7.9% to 48.1% sounds like a new capability. Here it was mostly a broken model being unbroken. This is the same reason we keep saying one leaderboard figure is a starting point, not a verdict, in [how to read AI model benchmarks in 2026](https://admix.software/blog/ai-model-benchmarks-2026). The interesting question is almost never the headline number. It is what changed underneath it.

Second, this is a story about the gap between frontier models and small open ones, and about how quickly tools now move between them. The thing doing the editing was a top closed model. The thing being edited was a tiny open model you can run yourself. A lot of the real action in AI right now lives in that handoff, where a strong model fixes, distills, or improves a cheaper one you actually deploy. We get into which open models are worth running in [the best open-source AI models of 2026](https://admix.software/blog/open-source-ai-models-2026), and into why no single model wins every job in [why no one AI model is best at everything](https://admix.software/blog/best-ai-model). If you want to compare a frontier model and an open one side by side on your own prompts instead of trusting a chart, that is exactly what running [several models through one app](https://admix.software/blog/best-app-multiple-ai-models) is for.

## Video: can an AI really rewrite another model's weights?

A short walkthrough of the weight-space programming result, what GPT-6 Astra actually changed in Qwen, and why the math jump is smaller than it looks.

![](https://www.youtube.com/watch?v=Ec3tKFkSZeU)

## FAQ

### Did an AI really improve another model with no training?

It edited the weights directly, with no gradient training, yes. But "improve" is doing heavy lifting. For the Qwen math result, it removed a looping bug that was stopping the model from finishing its answers, which let existing ability show up on the scoreboard. It did not teach the model new math.

### Is this recursive self-improvement or AI building better AI?

Not in any strong sense. A frontier model fixed a specific defect in a much smaller, unrelated model. The same edit failed on a model that did not have that defect. That is targeted repair, not a model bootstrapping itself to higher intelligence.

### Can I try weight-space programming myself?

The reading version has been reproduced on consumer hardware. Simon Willison ran it on a laptop with an open Qwen model in under an hour, and Hugging Face released a model and demo. The dramatic weight-editing result is harder to reproduce and still basically one group's reported finding.

### Should this change which model I pay for?

Not directly. The useful takeaway is to distrust giant single-benchmark jumps and to compare models on your own work. The easiest way to do that is to [run several models in one place](https://admix.software/blog/best-app-multiple-ai-models) rather than committing to one vendor on the strength of a chart.

## Sources

- [r/LocalLLaMA - Sparks of Weight-Space Programming, with the primary blog and the main critique](https://www.reddit.com/r/LocalLLaMA/comments/1xm6jow/sparks_of_weightspace_programming_llms_can/)
- [@ZhihuFrontier - log reconstruction showing the gain was mostly a looping fix](https://x.com/ZhihuFrontier/status/2117541464158921136)
- [@simonw - reproducing the weight-reading feat on a laptop with Qwen 3.8 27B](https://x.com/simonw/status/2117655816581071203)
- [@NielsRogge - Hugging Face reproduction with a released model and demo](https://x.com/NielsRogge/status/2117541532827848972)
- [@jacsebl - a model hand-writing a 100K-parameter classifier](https://x.com/jacsebl/status/2117606206764175543)
- [@paul\_cal - why the Qwen result is bug-fixing, not recursive self-improvement](https://x.com/paul_cal/status/2117536456491024470)
- [@dbreunig - fitting weights directly against a benchmark is close to meaningless](https://x.com/dbreunig/status/2117768883889476076)

## Further Reading

- [How to read AI model benchmarks in 2026](https://admix.software/blog/ai-model-benchmarks-2026)
- [The best open-source AI models of 2026](https://admix.software/blog/open-source-ai-models-2026)
- [Why no one AI model is best at everything](https://admix.software/blog/best-ai-model)
- [The best app for running multiple AI models](https://admix.software/blog/best-app-multiple-ai-models)

### Try all the models mentioned in this article

Admix gives you GPT-5, Claude, Gemini, and 300+ AI models in one app. Compare responses side by side. Try it for 7 days for $1.99.

[Try Admix for $1.99](https://admix.software/pricing)