---
title: "Anyone here learning JEV?"
author: "Impressive_Job_2715"
site: "r/AI_Agents"
source: "https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/"
domain: "reddit.com"
language: "en"
description: "JEV seems to be a pretty hot topic right now, but there aren’t many learning resources available yet. Has anyone here actually learned or is"
word_count: 4790
---

JEV seems to be a pretty hot topic right now, but there aren’t many learning resources available yet. Has anyone here actually learned or is currently learning it?

Would love to know what resources you’re using and how you’re approaching it.

---

## Comments

> **Healthy-Zebra-9856** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbgagm6/)
> 
> I see a lot of confusion so I am going to try to break it down. Those that are offended by the structured text, know this that I am a freaking GenX techie and this is how I format my text using tools like Grammarly & Muse Glimmer so it coveys the message properly. So if it offends you, you don't have to read it. For the rest, here is what it is.
> 
> Jev is basically a neural decision system, not another chatbot or agent.
> 
> Instead of giving an ML/DL model a prompt and asking it to generate prose, you give it some state, a bounded question, and a set of possible decisions. It returns a probability distribution over those decisions. Depending on the implementation, the underlying “model” may be one ML/DL model or a group of specialized ML/DL models selected for different kinds of decisions.
> 
> The important distinction is that Jev is closer to **System-1 judgment** than language generation. Think:
> 
> `state + question + legal choices → probabilities / decision`
> 
> rather than:
> 
> `prompt → arbitrary text`
> 
> The useful primitives are things like **Choice**, **Score**, **Rank**, and a binary/boolean-style decision. So it can answer questions such as: Which tool is appropriate? Which file is most relevant? Is this result sufficient? Should the agent continue, retry, escalate, or stop? Which model/workflow fits this task? Does the evidence support the claimed completion?
> 
> What makes it particularly interesting for an agent system is that I would **not let the ML/DL model define what is legal**. Deterministic code first constructs the allowed action space. If only one action is valid, there is no neural call at all. If there is a genuine semantic choice, Jev evaluates only the legal candidates. Deterministic policy then validates the result before anything is executed.
> 
> So in the architecture I’m working on, Jev becomes more of a **Neural Decision Fabric**:
> 
> `runtime state → deterministic eligibility/safety → Jev decision → deterministic validation → action → observe result`
> 
> It can operate throughout the agent loop rather than only at initial routing. For example it can help with context admission, model/workflow routing, tool-result judgment, retry decisions, evidence ranking, handoffs, completion assessment, and deciding when an independent review is warranted.
> 
> It also does **not mean every ML/DL model votes on every decision**. You might have one general decision ML/DL model and a couple of specialist ML/DL models—for example one that is particularly good at abstaining when evidence is insufficient and another specialized for computer-use/forms. Deterministic routing chooses which one, if any, should be called. Most decisions should require **zero or one neural inference**, not a swarm.
> 
> That is the part I find compelling: LLMs are very good at generating and reasoning through open-ended problems, while Jev-style ML/DL models can act as a much smaller, bounded decision layer around them. The LLM can still write code, investigate, reason, etc.; Jev helps decide **what should happen next**, while ordinary software remains responsible for authority, safety, execution, and verification.
> 
> So the short version is: **Jev is a bounded probabilistic decision layer for software/agents. It may be implemented by a single ML/DL model or a routed group of specialized ML/DL models, but it is not itself another conversational LLM or autonomous agent.**
> 
> # EDIT: TL;DR
> 
> Jev isn’t another chatbot or agent. It’s a **decision layer** around one or more ML/DL models: give it the current state and a set of legal choices, and it helps decide what should happen next, including when it’s unsure.
> 
> The LLM still does the open-ended work. Normal software still controls what’s allowed, executes the action, and verifies the result. Jev just adds fast, bounded judgment in between.
> 
> And it differs from the classic Classifiers/Re-rankers as
> 
> plain classification is usually:
> 
> **input → fixed label**
> 
> Jev is closer to:
> 
> **state + typed question + bounded options → probability distribution / decision**
> 
> The difference is that Jev is **instruction-conditioned and decision-oriented**, not just a classifier trained to recognize one predefined category set. The same ML/DL model—or routed group of ML/DL models—can answer many different bounded questions.

> **no\_spoon** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbhcco9/)
> 
> I’ve been a professional full stack developer for 15 years and I barely understand that.

> **Novaworld7** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbhe0r6/)
> 
> I suppose in english, it gets some input, and tries to figure out from its training what the probablistic outcome will be per the choices.
> 
> I am seeing some people state that the ordering also affects it.

> **Healthy-Zebra-9856** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbhg7e0/)
> 
> Pretty much. It looks at the input and estimates which of the allowed choices best fits what it learned. And yes, choice ordering can influence some models, so a good implementation tests for that and tries to make the decision independent of the order the choices were presented in.

> **slay-aargh** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbih7ah/)
> 
> How is this different from classification algorithms we all knew before we added natural language to classification algorithms?

> **Novaworld7** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbiuhkh/)
> 
> When you boil it down, it's not very different.

> **aliusprime** · [2026-09-25](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbx4xfh/)
> 
> It's that - but with a harness over it. Not an LLM harness though.

> **Greedy-Cat989** · [2026-09-26](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pc67y9s/)
> 
> In traditional classification both the question and the possible set of answers were fixed. If you wanted an answer to a different question or wanted to pick from a different set of answers you would have to retrain the model. Jev offers the flexibility to change the question and possible set of answers but isnt complete free form output like llms (which is why it gets the perfomance boost as theres no autoregressive decoding). So it’s a middle ground between llms and old classification models. Super powerful imo

> **Healthy-Zebra-9856** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbhfxzq/)
> 
> My apologies for not being able to simplify it even further. I do need to work on that as this is machine learning territory. So it's understandable that a full stack programmer such as yourself can't understand it versus a computer science geek. lol.
> 
> Jev is basically a **decision helper for software and AI agents**.
> 
> Instead of asking an AI to write a paragraph, you give it a small set of allowed choices and ask which one makes the most sense.
> 
> For example:
> 
> `Here are 4 tools you’re allowed to use. Which one fits this task best?`
> 
> or:
> 
> `Did this step actually solve the problem, or should we retry, investigate more, or stop?`
> 
> The important part is that **Jev doesn’t get to make up new actions**. Normal software decides what choices are allowed first. Jev just helps pick between them.
> 
> So the rough idea is:
> 
> **software decides what is allowed → Jev helps choose → software decides what actually happens**
> 
> That makes it useful around an LLM because the LLM can still do the big open-ended work, while Jev acts more like a small judgment layer helping answer: **“what should we do next?”**
> 
> And it doesn’t have to be one model. Different small ML models can specialize in different decisions, but usually only one is called for a given question.

> **\_RemyLeBeau\_** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbhy784/)
> 
> So it's Ask Jev and not Ask Jeeves

> **Healthy-Zebra-9856** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbhyzg7/)
> 
> LMFAO. I remember Ask Jeeves.

> **DefinitionSelect3083** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbn90uz/)
> 
> LMAO

> **meganaxx** · [2026-09-27](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pcbqvzz/)
> 
> lol pretty much, a weighted decision maker vs letting a model waste resource deliberating

> **pulkitjain3010** · [2026-09-28](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pciqgqk/)
> 
> Nah man you probably understand all the deep tech stuff. I’ve been an engineer for 5 years, working solely with and using AI for 3 (I have 2 Gemini, 1 ChatGPT and Minimax sub 😆) so I kinda did understand this.

> **Arsa-veck** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbi3zjh/)
> 
> It’s basically like assembly but for agents. I just don’t have enough examples on how to configure it and trigger it within a workflow

> **ToInfinityAndAbove** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbiojnp/)
> 
> It basically sucks, honestly. You essentially need a traditional ML model which still needs training (which needs golden dataset, testing, etc). At the end of the day, you have more points of failure, more work to do, a more limited system overall and more complexity for diminishing returns (if any good returns at all).  
> I’m sorry but I’m totally skeptical, and I used to be a traditional ML engineer for years in the past.  
> IMO, we don’t need crap like JEV, we need proper evals (genai system evals) and that’s it, but none knows how to do them properly and/or are afraid of doing it.  
> Last comment on this: LLMs are getting better, faster and cheaper everyday, we should build infrastructure and systems around that, not waste time and resources on temporary crap that none will use or remember one year from now
> 
> Edit: it seems that JEV is similar to a zero shot traditional classifier model that should not need training, it seems. So it’s very fast, etc. this actually makes sense! I’ve been doing similar patterns for years with normal llms (e.g multi label classification with probabilities, logprobs, etc) but the difference now is that JEV is optimized for that pattern! I was skeptical at first but now I’m actually kinda liking the direction.  
> Btw, this page helped me understand it better: [https://jevals.com/what-is-jev/](https://jevals.com/what-is-jev/)

> **hotnsoursoup86** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbnh1g6/)
> 
> You don't need it. But for quick, adhoc classification (e.g. traders) - and no infrastructure or process to manage, its nice. The input token size is insane, so it COULD include your training set to a degree - and its better with the inference system behind it. Not everything needs to require evals. "Does this next message violate any guidelines or is outside of the support bounds" "Which model could answer this question the best and save me the most tokens"
> 
> \- Openrouter is COOKED

> **rif-** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbhe2wb/)
> 
> Your explanation truly help me at some point, but now I have question.
> 
> So in implementation, is it close to skill? Or what? Can I kinda "attach" it into my current agentic workflow?

> **Healthy-Zebra-9856** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbhh5tf/)
> 
> Yeah, pretty much. I wouldn’t think of it as a skill though.
> 
> A skill says how to do this task. Jev is more like a little decision layer you can plug into your existing workflow.
> 
> So your agent does its normal thing, hits a point where there are a few valid next moves, and asks Jev something like: “Given what just happened, should I retry, use another tool, keep going, ask for review, or stop?”
> 
> Your normal code still decides what options are actually allowed and still executes the action. Jev just helps choose between them.
> 
> So you can bolt it onto an existing agent workflow at the decision points without rebuilding the whole thing around it.

> **rif-** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbhp201/)
> 
> In a glance, looks like rules but deeper in architecture.
> 
> In my case, probably I already have it with similar flow, but with me deciding things.
> 
> So with jev it's like added layer for it.

> **Healthy-Zebra-9856** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbhu3tv/)
> 
> So I think I have cracked a puzzle, I am actually able to achieve this same accuracy rate of what JEV is claiming. I still got a ton more tests to do, if this is successful, I’ll open source it

> **Akash\_Rajvanshi** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbhiijo/)
> 
> Yes, I have the same question: how can I use JEV with my agents? When I plan something in my code, I have a state and decide which decision would be better or which the agent should pick next.

> **Winter-Conclusion750** · [2026-09-27](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pcew10o/)
> 
> I had a similar question when looking at adding this to an existing LangChain/LlamaIndex setup. If you end up trying it, where in your loop are you planning to slot it in...tool routing or state validation??? Ive found that using small fast routing checkpoints right before expensive tool calls usually saves the most compute without messing up the main execution flow...

> **BrilliantEmotion4461** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbitoni/)
> 
> Use case: difficulty setting in a jrpg. Takes user battle data and decisions and decides on difficulty.

> **haslo** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbi0fqs/)
> 
> Thank you for the very clear and structured explanation!

> **dca12345** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbi6y5r/)
> 
> Any thought on the use of Jev with world models?

> **Healthy-Zebra-9856** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbib6z2/)
> 
> Personally, I’ve already been moving in this direction in my own products, started this around 8 or 9 months ago. It really started because I couldnt find coding harnesses that didnt eventually run into architectural problems, and I kept seeing software being produced without enough architectural discipline. I havent seen that reliably solved by skills, [`AGENTS.md`](http://agents.md/), prompts, or simply adding more agents.
> 
> So I built this kind of bounded decision layer into both **Terminal Agent** and \*\*SWFoundry (\*\*governed software engineering foundry with observation), and both will be used while interacting with world models. In Terminal Agent, it can sit around those interactions to help decide what context is relevant, which tools or workflows are appropriate, what to do next, whether to retry, fork, review, or stop, while deterministic code still controls what is actually allowed to happen. In SWFoundry, the same general idea is used at a higher supervisory level for architecture selection, implementation-blueprint construction, next-step guidance, evidence assessment, and keeping the work inside the governed architecture.
> 
> That’s why I think Jev and world models fit together very naturally. The world model can provide the richer understanding and prediction of state and possible outcomes, while Jev-style models make fast bounded semantic decisions over that state. Then deterministic software still owns legality, execution, governance, and verification. I do plan on open-sourcing this portion to hook into any agent. Let's see where my tests lead me.

> **grimorg80** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbjigzm/)
> 
> Yep. People are also getting tricked by super codes platforms that use Jev sparsely for logical routing but make them look like Jev made and runs the whole thing. It's scammy as hell.

> **DefinitionSelect3083** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbn92a8/)
> 
> 👍

> **daniel** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbkziro/)
> 
> Sounds cool. Seems like it's waitlisted though? Despite saying it's open on the homepage.

> **Healthy-Zebra-9856** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbl8952/)
> 
> They’re gonna be others that’ll come out. Personally I have my own, which I’m gonna open source for sure. I was able to get approved in a matter of minutes.

> **Technical\_Draft\_1346** · [2026-09-24](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbq1jwh/)
> 
> So it’s a glorified switch statement.

> **Healthy-Zebra-9856** · [2026-09-24](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbsln1v/)
> 
> That would be closer to the old classifiers or re-rankers.
> 
> Using a C# analogy, Jev may be closer to a **switch expression**.
> 
> Classifiers / traditional switch:
> 
> \`\`\`csharp switch (state) { case X: return A;
> 
> ```
> case Y: return B;
> ```
> 
> } \`\`\`\`
> 
> Jev:
> 
> \`\`\`text Given this semantic state, score A, B, C, and D
> 
> → A: 0.08 → B: 0.71 → C: 0.16 → D: 0.05 \`\`\`
> 
> Now using a switch-expression analogy:
> 
> `csharp var result = semanticState switch { _ when Score(A) == 0.08 => A, _ when Score(B) == 0.71 => B, _ when Score(C) == 0.16 => C, _ when Score(D) == 0.05 => D }; `
> 
> Conceptually, though, it is really more like:
> 
> `code semantic state → score each allowed branch → compare the scores → select the highest-scoring branch → B `
> 
> So the shorthand is like:
> 
> **Jev is closer to a learned probabilistic switch expression over a constrained set of choices.**

> **neuralSalmonNet** · [2026-09-27](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pcbsb88/)
> 
> > So the short version is: Jev is a bounded probabilistic decision layer for software/agents. It may be implemented by a single ML/DL model or a routed group of specialized ML/DL models, but it is not itself another conversational LLM or autonomous agent.
> 
> In case you want to fine tune your understanding of the probabilities. Jev docs are misleading.
> 
> [https://bernoulli.app/articles/is-jev-confident](https://bernoulli.app/articles/is-jev-confident)

> **Winter-Conclusion750** · [2026-09-27](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pcevk1e/)
> 
> That distinction between setting the legal choice space deterministically versus letting the model select from them hits the nail on the head for me.. well in practice, how are you handling edge cases where the deterministic boundary misses a valid move....do you fallback to an llm evaluator or just fail fast?
> 
> also when you run this in your pipeline... are you seeing any noticeable latency penalties from calculating candidate probabilities before execution?

> **onebit** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbif8no/)
> 
> Yes 82%

> **Rifadm** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbi4lbu/)
> 
> you see people like this in 2026. Absolutely crazy

> **Glittering812** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbhzrz0/)
> 
> Honest take: "learning Jev" is a weird frame because there's almost nothing to learn the traditional way. No prompting tricks, no persona engineering. You write a state, define question types, get typed answers back with probabilities. The hard part is unlearning LLM habits — stop asking it open questions, start thinking in fixed decision trees.

> **ivoras** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbjcaeg/)
> 
> It's mystified / hyped to infinity and beyond. Here's an example of what it does (example from [my blog](https://ivoras.substack.com/p/jev-is-great)):
> 
> Just to recap, Jev-like models take an input like:
> 
> **“In front of me is a small animal with fluffy fur and a bushy tail”**
> 
> and some options together with instructions what triggers them like:
> 
> - “what\_animal”: choice
> 	- “shark”: Big fish, big teeth, predator
> 		- “spider”: Has 8 legs, insect-like, some are venomous
> 		- “squirrel”: Small mammal, furry, notoriously bushy tails, herbivore, can carry diseases
> 		- “crocodile”: Big lizard, unexpectedly fast, carnivore
> - “is\_dangerous”: Can the animal seriously injure or kill a man
> - “should\_run\_away”: Should I run away from it if I encounter it, to avoid death of injury
> 
> And then it outputs a result like:
> 
> - what\_animal: squirrel, confidence: 0.9
> - is\_dangerous: confidence: 0.05 (interpretation: NO)
> - should\_run\_away: confidence: 0.02 (interpretation: NO)
> 
> So if you can fold your inputs into that shape, it's much more strict and useful than even trying to shoe-horn JSON formatting onto a LLM. If not - skip it.

> **Different\_Pain5781** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pben4ai/)
> 
> s JEV actually a language or am I missing something?

> **chrissz** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbh3p2n/)
> 
> Jev isn’t a language. It’s a decision model. It evaluates things that you provide to it and replies with a structured JSON response with one of three types of responses.  
> I used it tonight to build a compliance evaluation tool. It’s incredibly fast.

> **Novaworld7** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbhe7x4/)
> 
> Yes it is, but it doesnt mean its right either. I trained a small model on some data and its more right than jev. Probably not on as many heads as Jev but that doesnt technically matter if im not using them.

> **OperationAble2918** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbfc7vl/)
> 
> yeah i am confused too

> **Wooden-Television437** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbflaak/)
> 
> 1 minute of silence for lack of will to Google. Feel very sorry for your loss

> **National-Parsnip1516** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbifi40/)
> 
> jev is cool but the learning curve is steep. i've been playing with it for a bit now. actually found a few hidden gems in the docs. i have a logic setup for jev agents i'm building. dm if u want to collab or see the resource.

> **skylinedev** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbj1ljt/)
> 
> I have curated these contents that are worth to watch or read:
> 
> Jev CEO: I made ChatGPT, now I'm building what's next  
> [https://www.youtube.com/watch?v=cJ0EOzey--o](https://www.youtube.com/watch?v=cJ0EOzey--o)
> 
> Why We Made Jev — Diogo Almeida, TypeSafe Co-founder & CEO  
> [https://www.youtube.com/watch?v=cFx9Z3ZXca0](https://www.youtube.com/watch?v=cFx9Z3ZXca0)
> 
> RLCD vs RLHF: What Is Typesafe's Jev Model Actually Claiming?  
> [https://www.mindstudio.ai/blog/typesafe-jev-rlcd-vs-rlhf](https://www.mindstudio.ai/blog/typesafe-jev-rlcd-vs-rlhf)
> 
> Jev’s Architecture Unmasked — archerhume  
> [https://archerhume.com/posts/jevs-architecture-unmasked/](https://archerhume.com/posts/jevs-architecture-unmasked/)
> 
> System vision the founder has shared:  
> \- Programmable AI, interoperable, to be embedded with any software  
> \- System One Model, beyond decision model  
> \- Optimized for code-as-consumer, intelligence-per-dollar, contrast with LLM + chatgpt + RHLF  
> \- The downside of RLHF vs their RLCD (a training model to reward how likely confidence-based decision is right.)

> **frappuccinoCoin** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbh7llp/)
> 
> This is the best interactive Jev explainer I came across: [https://jevals.com/what-is-jev/](https://jevals.com/what-is-jev/)

> **ILLinndication** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbhoics/)
> 
> What am I missing? In the example, Gemini already answered the question. What did jev do?

> **ILLinndication** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbhoop3/)
> 
> Oh, it’s two different examples

> **tobbe2064** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbivd6v/)
> 
> How are you guys getting access to jev? I thought it was a wait list

> **aniketmaurya** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbjcajk/)
> 
> You can use with Vercel or OpenRouter gateway

> **Robertyouidiot** · [2026-09-27](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pcfcrur/)
> 
> vercel now blocks using it with the free credits they give, youll have to pay for it

> **daniel** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbkzpcb/)
> 
> Same. Their homepage says it's open but when I try to sign up it says it's closed lol.

> **florinandrei** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbjt22z/)
> 
> You could soon get a doctorate at the School of Jev. I'm setting it up as we speak.

> **yunsheng31** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbkkqik/)
> 
> good(òωó)👍

> **LetterheadUnlucky421** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbktizg/)
> 
> how does one access JEV?

> **Western\_Machine** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbkznad/)
> 
> Its a zero shot classification model, that doesn’t need specific fine tuning. Ofc you can give examples in context.

> **free\_podcast** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbmcvj6/)
> 
> I use it everyday on forsale.bz to fix scraped listings to have correct cities and status changes to listings. Works amazing.

> **hotnsoursoup86** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbnggqh/)
> 
> I REALLY WISH I SIGNED UP EARLIER - I deferred it because I had some priorities but when I went to sign up yesterday, it was gone.... DAMMIT. I have SOOOO many good use cases.
> 
> Basically for those that still don't get it --> Before jev, classification required training a model to properly classify something. That step by itself made it inaccessible or not cost effective for the general public. Enter Jev -> No training required, classification can happen within the bounded context using inference -> You can hand it 20 files that touch a specific piece of code and say "Are there security concerns in my code" (or 20 other questions, given the same input) - just wanted to give a simple one, but theres wayyyyy better ones. People are probably spamming it for trading though because of response time.

> **Nice-Engineer-3648** · [2026-09-27](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pcg5k63/)
> 
> So you can ask it 'is there a mistake in my code' and it will give you yes/no then you hand the code to an agent to fix?

> **Admirable\_Swim\_6856** · [2026-09-24](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbpt0l3/)
> 
> I like the idea of using it as part of an agentic system where you can increase determinism and speed. I've been having trouble with the limits but perhaps thats just me still learning where its most useful. Limits being small context, no tool calls and of course that it can't output reasoning.

> **Dramatic-Coach-6347** · [2026-09-24](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbvdtvn/)
> 
> My name is jev

> **Dorcelessness\_** · [2026-09-25](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbvsfwq/)
> 
> Kill me

> **Salt-Stranger-802** · [2026-09-25](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbwe9ti/)
> 
> Jevってローカルで使えないの？

> **anandpodila** · [2026-09-25](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbxaw6e/)
> 
> Know about Jev: [https://youtu.be/hbeY94u0Zi4?si=8cfObJM9k2lRviCG](https://youtu.be/hbeY94u0Zi4?si=8cfObJM9k2lRviCG)

> **AdThis3819** · [2026-09-25](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbzposq/)
> 
> 我想知道它和laya的差别在哪里

> **B2B\_Live** · [2026-09-25](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pc1hzcs/)
> 
> What are the top resources that you would use for Jev

> **powerOfAI** · [2026-09-26](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pc48y57/)
> 
> [https://youtu.be/0QDBYsG3Lgo?si=2zSdIDqljOm2K0Rl](https://youtu.be/0QDBYsG3Lgo?si=2zSdIDqljOm2K0Rl) hope this helps

> **Budget-Juggernaut-68** · [2026-09-26](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pc6a7di/)
> 
> There's nothing to learn. It just a good classifier. It just tells you yes no.

> **Fc\_coolx** · [2026-09-30](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pd0xxf6/)
> 
> I'm curious about JEV too. There don't seem to be many beginner-friendly resources yet.

> **slay-aargh** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbf9vkb/)
> 
> Its BS, it can do stuff, but this "stuff" have already been there, just for classification there have already been ton of DS models, since when are people spending tokens for classification, like wdym "for less money" ? Classification have always been a free thing.

> **skylinedev** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbiytv3/)
> 
> I kind of agree with you. However, i believe Jev has introduced this "RLCD" (compared with "RLHF").  
> I am guessing... they want to build this primitive in AI automation (type-safe decision for code as consumers), not human as consumer.

> **sixwax** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbgb62p/)
> 
> Congrats! You've missed the point.

> **tinyyellowbathduck** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbey2y2/)
> 
> I read learning JEW and I was confused

> **tototoru** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbewcnh/)
> 
> Nothing ground breaking but it's good, you can already achieve the speed using small models, the type safety out of the box is good since small models tend to have issues respecting the schema, but nothing Instructor or similar can't fix.

> **joeymcgly** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbhd17t/)
> 
> Its very ground breaking. You arent training it on when to choose an outcome..it is basically pretrained. We are testing for accuracy now

> **king\_of\_gazorpazorp** · [2026-09-28](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pciss33/)
> 
> MF i was using bert like models for zeroshot classification in 2022

> **FabulousJuicer** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbe2lb4/)
> 
> I get that at its core its a classifier, but the part that I cant figure is what happens if it gets something wrong, is there a way to fine tune it?

> **\_RemyLeBeau\_** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbf5wvn/)
> 
> It's never wrong. Superior Intelligence is never wrong, just misunderstood. 🫠

> **East-Reputation-9488** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbh6hw9/)
> 
> That's the best part. You never know if it's wrong. Instead you assume it's something you did if you can detect the failure at all.

> **\_SirPunsALot\_** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbgcx3k/)
> 
> The idea is that you provide the required context to the model so it has what it needs to provide the answer (or correct classification). Its context window is 64k tokens and it enforces a cap of 32k tokens for input state & question.
> 
> Beyond that, you accept that is not a truth machine and can be wrong. You design around it.

> **Novaworld7** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbhetak/)
> 
> You cannot finetune jev directly. The closest thing you could do is get a training set of data, say idk 100K data points, run Jev on it blind, and have the answers, you can then score Jev against it to determine its accuracy.
> 
> Part\* of the appeal of jev is that its ultra cheap. I happen to be cheaper... you can train your own 149M para model and it can be very fast as well. There are sample sets on kaggle / hugging face you can find and or you can make your own... have another model make one from api's etc. Your accuracy will only ever be as good as how you label and teach + the pretraining of the original model unless you stand up your own.
> 
> But small models like Bert for example are great at this and on a 1070 it doesnt take too long to train, and they fit right on it.
> 
> \---
> 
> The only way to know its wrong is to have the answers
> 
> \---  
> Edit: Party = Part

> **zer00eyz** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbi0byf/)
> 
> Wait till you figure out that it can return different results for the same request if repeated.
> 
> It's still a non deterministic system - you dont depend on it to be right all the time, you depend on it to be right often enough and have a "back up plan" if its wrong.

> **Impressive\_Job\_2715** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbehcoi/)
> 
> Honestly, I have no idea either 😅 That’s one of the things I’m trying to figure out.

> **open\_seriousness** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbe29h9/)
> 
> I tried piecing it together from random github repos and a few scattered medium posts but it’s still pretty patchy, feels like half the time I’m just guessing at the syntax rules. The docs are sparse which makes me wonder if I’m even doing it right.

> **Impressive\_Job\_2715** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbeh1ce/)
> 
> Are you trying to get it running locally? I’ve come across a few reverse-engineered articles and some open-source repos, but I haven’t tried any of them myself yet. I'm so confused actually.

> **Flat-Principle9832** · [2026-09-26](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pc7am31/)
> 
> Thats usually the problem with learning from scattered sources. You can collect a bunch of examples but still miss the actual concepts behind them.

> **AutoModerator** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbe0487/)
> 
> Thank you for your submission, for any questions regarding AI, please check out our wiki at [https://www.reddit.com/r/ai\_agents/wiki](https://www.reddit.com/r/ai_agents/wiki) (this is currently in test and we are actively adding to the wiki)
> 
> *I am a bot, and this action was performed automatically. Please [contact the moderators of this subreddit](https://www.reddit.com/message/compose/?to=/r/AI_Agents) if you have any questions or concerns.*

> **Lopsided\_Manner\_7602** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbelreq/)
> 
> I just experimented with Jev — turned it into a router instead of the usual classifier/gate.  
> Working well so far — worth trying if you're already using Jev for something similar.

> **Swiftwing21** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbeo9s0/)
> 
> Noul's have been interesting to learn about.
> 
> I saw "invalidate" from the creator of headroom. Im curious to see how computer use and machine first tooling can improve with a decision model and decision trees with fallback to language models.

> **ejstembler** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbf4fvg/)
> 
> I cannot say I learned it per se; maybe superficially. I have successfully directed my coding agent (DeepSeek V4.1 Flash) to use it for two different tasks. Both worked out well. 👍🏻

> **Indaflow** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbfb8wi/)
> 
> What is it?

> **FormalWave** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbg6hzy/)
> 
> I just pointed my codex agent at it and the skill that they shipped. I have it shadowing some classification / routing tasks that are currently being done with Luna.
> 
> The shadowing work prints in the Phoenix ledger and then we will evaluate if it does anything either better, cheaper or a combination of the two over the current Luna model.

> **dennisatBB** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbhlzwy/)
> 
> We're using it in production at Unblocked now. We replaced the cross-encoder that decides which memories make it into the agent's context.
> 
> Wrote up the eval here if it's useful: [https://getunblocked.com/blog/jev-in-production-vs-cross-encoder/](https://getunblocked.com/blog/jev-in-production-vs-cross-encoder/)
> 
> Biggest surprise was that JEV was worse when we scored memories individually, but better when we let it judge a group of candidates together

> **tiensss** · [2026-09-22](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbg1dwe/)
> 
> What do you mean, learn JEV? What are the current classifiers lacking for your use cases?

> **IngenuityDry** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbh2gm8/)
> 
> Awesome jev

> **mpigsley** · [2026-09-23](https://www.reddit.com/r/AI_Agents/comments/1wndjk7/anyone_here_learning_jev/pbheehz/)
> 
> Yes! I’ve been using it to replace some legacy workflows. In my evals it’s been on par with smaller models from the leading labs while being an order of magnitude cheaper and faster. I’m able to run my pipeline more often for an overall cheaper end result.
> 
> I’d say it’s a tool I will be reaching for often.
