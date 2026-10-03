---
title: "Jev isn't new tech. Its marketing targets people who think AI started with LLMs."
author: "tiensss"
site: "r/LocalLLaMA"
source: "https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/"
domain: "reddit.com"
language: "en"
description: "I keep seeing Jev presented as some new class of decision model, but most of what’s being advertised is just normal classifier behavior with"
word_count: 9135
---

I keep seeing Jev presented as some new class of decision model, but most of what’s being advertised is just normal classifier behavior with modern zero-shot capabilities.

It outputs probabilities over constrained choices, doesn’t generate autoregressively, can’t output an invalid class, and can use labels defined at inference time. None of that is new. Zero-shot/NLI classifiers, embedding models, cross-encoders and rerankers have been doing variations of this for years.

The weird part is that most of the impressive Jev comparisons are against LLMs. Of course a specialized classifier is faster and cheaper than making an autoregressive LLM generate an answer. That doesn’t establish a new paradigm. The meaningful comparison is against strong existing classifiers. The purpose of this is to mislead.

There are already benchmarks like BTZSC evaluating dozens of zero-shot classifiers across 22 datasets, including NLI models, embedding models and rerankers. I haven’t seen Jev properly benchmarked across that landscape yet.  
([https://proceedings.iclr.cc/paper\_files/paper/2026/hash/417e1c15b3d49852fceded8aa104107d-Abstract-Conference.html](https://proceedings.iclr.cc/paper_files/paper/2026/hash/417e1c15b3d49852fceded8aa104107d-Abstract-Conference.html?utm_source=chatgpt.com))

Where people have compared Jev with conventional classifiers, the story is much less magical. One Banking77 experiment got 93.3% from BGE-small + logistic regression versus 83.2% for Jev, at about 9ms locally.  
([https://github.com/ickma2311/jev-baselines-eval](https://github.com/ickma2311/jev-baselines-eval?utm_source=chatgpt.com))

Some of the marketing also goes into the misleading territory. The “can’t hallucinate” framing is very sus, for example. Their own explanation admits the 0% hallucination figure is not empirical, and what they actually guarantee is that Jev returns an answer matching the allowed schema. That prevents invalid outputs, it does not prevent confidently choosing the wrong valid answer. ([https://typesafe.ai/blog/introducing-system-one-models-and-jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev?utm_source=chatgpt.com))

So color me a skeptic. Look, Jev might even be a good product. Maybe their unpublished architecture or RLCD training method is genuinely novel. But nothing we've seen so far establishes that "System One Models" are a new class of AI. What the public evidence mostly establishes is that using a specialized classifier for classification can be much cheaper and faster than using an autoregressive LLM, which we already knew. It only sounds novel if your idea of AI begins and ends with LLMs.

---

## Comments

> **WithoutReason1729** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbojql3/)
> 
> Your post is getting popular and we just featured it on our Discord! [Come check it out!](https://discord.gg/PgFhZ8cnWW)
> 
> You've also been given a special flair for your contribution. We appreciate your post!
> 
> *I am a bot and this action was performed automatically.*

> **caldazar24** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmn3wz/)
> 
> I've trained classifiers before, but my experience with zero-shot classifiers is that they were just a lot dumber than LLMs. You were far better off prompting an LLM to spit out some JSON then using any of them for any problem I've tried.
> 
> It's possible there's nothing to Jev but "hey, let's put a lot more resources into a big zero-shot classifier, at least within a few orders of magnitude of what we've used to train LLMs". That's still great! It serves a very valuable place in the market, even if it's not breakthrough science.
> 
> GPT-2 and then GPT-3 were also basically just "hey, let's do what other research has done, except way bigger!" More engineering than science, really. It obviously still changed the world, and interesting research problems emerged when you tried to scale it up more.

> **radarsat1** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbn1lbk/)
> 
> exactly. People on both sides of the coin, saying "this is just a classifier" and people saying "this is just a single-token LLM" are both missing the point. The point is not that it's something new per se, it is that it apparently *works really well*. They've clearly cracked something about scaling, training, and calibrating these things. Shame it's not published but I suspect it's all about the data collection methods & distillation they've done so they're probably not that eager.

> **r0ck0** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbpgalf/)
> 
> A monad is just a monoid in the category of endofunctors. What's the problem?

> **ChocomelP** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbrdxpn/)
> 
> You tell me. I've never even seen Ghostbusters.

> **SandySkittle** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbpxpy5/)
> 
> A way to put it: It’s a classifier, but not *just* a classifier.

> **Budget-Juggernaut-68** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbpf2ci/)
> 
> The interesting thing is the CEO did say that ALL their data is synthetic and they Only want to train on synthetic data.
> 
> Edit: source [https://youtu.be/cFx9Z3ZXca0?is=nLtymbwaMRcm8\_bi](https://youtu.be/cFx9Z3ZXca0?is=nLtymbwaMRcm8_bi)

> **bartgrumbel** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbporne/)
> 
> Maybe the data was generated by an LLM, hehe

> **tiensss** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbq1tix/)
> 
> My point isn't that this is just a classifier, but mostly how misleading the Jev team has been.

> **4thepower** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbpsug6/)
> 
> Is there any evidence that Jev is significantly more accurate than other zero-shot classifiers available today?

> **newMoneyStyle** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbxypo5/)
> 
> No solid benchmarks I've seen, so the accuracy claims mostly feel like marketing.

> **Grouchy\_Jicama\_007** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbrrzg3/)
> 
> Haven't seen a bunch of demos from other ZSCs doing what Jev can do, have you?

> **IndigoSeirra** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbswqmh/)
> 
> No, there were open source zscs that are cheaper and just as if not more accurate than Jev before Jev released, Jev was simply the first company to bring the modern AI marketing hype to those types of models.

> **Big\_Performance\_2959** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbx07v2/)
> 
> Weird how you did not name them?

> **Short\_Change** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pcgzzkx/)
> 
> Honestly get your AI to plug into existing video AI params. It is amazingly good. LLMs do not scale well in large contexts. It’s like here is a tool that is right 70% of the time.
> 
> Note Jev does not perform better than its open source counterpart so you can try that instead if you have the machine for it

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmny4o/)
> 
> Possible, but speculative as TypeSafe hasn’t published enough to know whether Jev is just a much larger zero-shot classifier.
> 
> IMO the GPT-2/3 analogy is weak, those models openly documented what was being scaled. Jev’s architecture/training are still largely hidden.

> **No\_Afternoon\_4260** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbnt7x5/)
> 
> could they be using a llm for ingestion and work out of the kv cache itself? for the rlcd part

> **lolxd\_\_** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbplbv2/)
> 
> There’s a lot that point it to being a qwen model

> **tiensss** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbq1vg7/)
> 
> It might just be Qwen3-Reranker-0.6B with different primitives

> **Internal\_Sky\_8726** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbqsb4w/)
> 
> Right. Jev might not be breakthrough science. But I do think it will lead to breakthrough usage patterns.

> **matholio** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbwsfsn/)
> 
> I agree, if people start looking for Jev type moments in their pipelines and do so because it's cheaper, that is a genuine shift, which will divert a lot of token costs. Why use an llm to choose a tool, if Jev can for near zero cost. Feels like the equivalent of If/Case/Switch for AI.

> **puzzleheadbutbig** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmb16g/)
> 
> > The weird part is that most of the impressive Jev comparisons are against LLMs
> 
> Oddly enough Jev devs are explicitly saying that Jev is not an LLM (or SLM)
> 
> People who are comparing it to LLMs and thinking that it is a replacement of whatever the model they are using are either just wrong or they were simply using LLMs for wrong tasks.

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmc14f/)
> 
> To be fair, Jev marketing compared it to LLMs as well. Also their marketing knows who they are targeting - people who have no idea about AI, and have only ever known LLMs.

> **Usual-Orange-4180** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmdc2o/)
> 
> Yeah, the comparisons they made with LLMs in terms of cost were super weird, we know classifiers cost penis compared to language models.

> **Beneficial\_Twist\_878** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmfggo/)
> 
> you know what you were doing there

> **Usual-Orange-4180** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmfp22/)
> 
> Me? What was I doing? Hahaha

> **l33t-Mt** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmkryg/)
> 
> You wrote penis.

> **peekdasneaks** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmon2z/)
> 
> Now you wrote penis

> **\_TheWolfOfWalmart\_** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbn8heu/)
> 
> I am also writing penis.

> **True\_Tangerine\_4706** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbosqjc/)
> 
> penis

> **GilloutineBreast** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbq4ww7/)
> 
> penis

> **Usual-Orange-4180** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmoo49/)
> 
> Oh… hahahaha, Freudian Slip. It will remain! Penises are fairly cheap compared to running LLMs 😆

> **ebfortin** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbnkho2/)
> 
> Depends which one.

> **Usual-Orange-4180** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbnwlij/)
> 
> 😢

> **Party\_9001** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbnbuh5/)
> 
> Heh. Penis

> **SkyFeistyLlama8** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbojkbp/)
> 
> What Jev did was a dick move. Heh.

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmediv/)
> 
> They weren't super weird. They were made to mislead and market their product. They knew exactly what they were doing.

> **Usual-Orange-4180** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmfhuo/)
> 
> Absolutely, I flip-flop between being too nice or an absolute asshole, right now I’m in nice mode 😆

> **LocoMod** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmgxyh/)
> 
> Not everything is a conspiracy. They have the best zero shot classifier presumably trained on datasets larger than anyone else and are serving it at scale. That in itself can be valuable. If it was so easy, why didnt anyone do it until now?
> 
> You see, ideas are like assholes. Everyone has one.
> 
> It's the execution that counts. And TypeSafe executed and it executed well.
> 
> I dont have to think about training my own classifier or finding one in HF that fits my use case. I configure the endpoint. Send it the data and get a result. And that's all it needs to be.
> 
> You should start your own service and let us know how it goes for you. Or make an open source clone that matches the zero shot results. Then you have bragging rights. Until then, kindly...

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmhk3h/)
> 
> So I can't point out misleading claims because ... I didn't create a more successful business? lmao, I don't even know how to engage with this braindead logic

> **Zomboe1** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbncud5/)
> 
> Just world fallacy again, imo. Money = virtue in the US. Obviously they are right and you are wrong, cause they made money and you didn't!
> 
> I appreciate you still fighting the good fight. I think at some point it's just a matter of a difference in basic values. More than ever, straight up lying is seen as fine as long as it makes you money.

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbnd0tz/)
> 
> Thanks for the support, brother

> **Persistent\_Dry\_Cough** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbpmbam/)
> 
> There needs to be a bot farm that spams this kind of rational logic instead of the nonsense I see all over the dead internet

> **JustinPooDough** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbqnkfn/)
> 
> True words

> **SuperNintendoDahmer** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pd61pf0/)
> 
> Don't you mean phallus, see?

> **gscjj** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmjgi3/)
> 
> To be fair, I’d say most people who use AI would barely be able describe what an LLM is, how ChatGPT/Claude works at all or even know there’s other types of AI out there.
> 
> Being in this community that might be hard to see.
> 
> It’s not malicious, this is just probably the largest non-chatbot model out there besides embeddings for the average person. Even embeddings 90% of AI users probably couldn’t explain so it all seems magical.

> **puzzleheadbutbig** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmdz1t/)
> 
> > **Is Jev just a smaller LLM?**  
> > Jev is neither small nor an LLM, hence being off the intelligence Pareto curve.
> 
> [Literally from their blog.](https://typesafe.ai/blog/introducing-system-one-models-and-jev) Even the most *too long didn't read* person would scroll down and see the FAQ.
> 
> What they’re doing in this task is showing people that using LLMs for System 1 tasks is just silly and that they should use their product instead. Which makes perfect sense from a marketing standpoint. If I saw everyone hitting a screw with a hammer, and I had created a product called a screwdriver, I would tell them, "Hey, if you use my screwdriver for screwing something, you’ll get 2x the performance for less cost (which is energy in this case)". That, again, makes sense to me.
> 
> And unlike what people say about their expensive marketing etc, I think their marketing department is complete garbage because they failed hard to convey this message in their public blog.

> **bel9708** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbna1kb/)
> 
> If technical docs conflict marketing material a reasonable technical person would trust the technical docs. Right?
> 
> [https://docs.typesafe.ai/introduction/machine-learning-primer#three-post-training-approaches](https://docs.typesafe.ai/introduction/machine-learning-primer#three-post-training-approaches)

> **No\_Afternoon\_4260** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbnsqq8/)
> 
> could they be using a llm for ingestion and work out of the kv cache itself? for the rlcd part

> **bel9708** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbnuvma/)
> 
> That’s exactly what they do they prefill a single kv cache and then they run inference in parallel over that cache.

> **No\_Afternoon\_4260** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbnxgdo/)
> 
> They run inference in parallel? Over that cache? Can you elaborate?

> **bel9708** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbodlsf/)
> 
> When you do prefill you get a kv to do matrix multiplication on to predict the next token. If all you need to do is predict several different decisions that are independent of each other. You can use the same KV to predict all decisions in parallel.

> **Complex\_Educator6444** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbq3r1m/)
> 
> LLMs … operate over everything in parallel—every single operation of the transformer can be described as some parallel operation relative to a KV cache the cache … which producing from the input is like, most of the work of inference. An LLM has basically three ways to interact with data—(spicy multiply, big floor), rinse, lather, repeat until it's time to (be confident). The point when multiplication is spiciest is often producing the hidden layer from the input. Anything that can operate over that output—has been trained in coordination with the LLM, which it will need to always be trained in coordination with forever.
> 
> So it's the classifier equivalent of a diffusion image model; so it's like a diffusion model that returns a yes or no?

> **bel9708** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbrk9am/)
> 
> Traditional inference is is described as auto regressive. You need to predict a token before you can predict the next one. Jev changed that and uses one shared cache and parallel forward pass.

> **TheDivinityGod** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbohukw/)
> 
> And it works, some people at my work start saying JEV is next generation of AI or replacement of LLM or some weird shit.
> 
> Better to leave this work

> **Tripartist1** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbp1cwn/)
> 
> From what Im gathering, its the same core, trained differently. People are getting similar results by using the prefill on normal LLMs. I think they took a frontier sized dataset, and genuinely trained it like a language model calibrated for statistical exactness rather than conversation, then tacked on the extra bits tpnextract that exactness from prefill, just like some of the open source projects are doing. Their moat is the training.
> 
> I think its still an LLM when you boil it all down, same world data, same token predicitions, just with its mouth removed. Whether or not their RLCD is enough of a moat to keep oss at bay while they try to claim market share is another question, and thats probably exactly why they were so sudden and liberal with the marketing tbh.
> 
> And as for the OP, your conclusions are exactly the same ones I came to after digging a bit into things like bert and laya. The biggest difference i can find is that Jev is generalized, so it lowers the barrier of entry from "knows how to and has the compute to train/fine tune a classifier" to "can get an agent to call the Jev API". As far as raw capability goes though, nothing ive seen is really new. The generalization does allow it to do things like play games... but thats not really a use case.

> **Space\_Brilliant\_7273** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmdf4d/)
> 
> Having used spaCy and scikit-learn for more than 10 years to classify sentences and words, I find it funny for people to discover NLP classification in 2026.
> 
> Jev is almost the same as spaCy and scikit-learn in my opinion.

> **Asleep\_Document9811** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbndyju/)
> 
> *SmarterChild chuckles from the darkness*

> **mebeast227** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbp5pwi/)
> 
> Holy fuck you just brain blasted me with memories i completely forgot. I remember using the aim chat bots and think about how much I don’t really remember how good/bad they were, but regardless…smarterchild is a wild throwback

> **IntroductionSad1324** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbudhfb/)
> 
> If you want an even wilder throwback (to 1964) check out ELIZA

> **fishhf** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbq14ld/)
> 
> Wait til the jev guys rediscovers embeddings and then combine Jev with RAG. Just imagine the breakthrough! /s

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbme9ui/)
> 
> Right?! Had the same thoughts, haha

> **LatentSpaceLeaper** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmnk30/)
> 
> Can spaCy or scikit-learn do zero-shot classification? Or do they require labeled training data?

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmod5x/)
> 
> Classic spaCy/scikit-learn classifiers generally require task-specific labeled training data. They’re libraries for building/running models, not giant pretrained foundation models. The better comparison for Jev’s zero-shot behavior is pretrained NLI/zero-shot classifiers, which have supported natural-language labels without task-specific training since 2019. ([https://aclanthology.org/D19-1404/](https://aclanthology.org/D19-1404/?utm_source=chatgpt.com))

> **LatentSpaceLeaper** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbms9ts/)
> 
> The following leaderboard contains several such zero-shot classifiers as well as fine-tunes AFAIK: [https://huggingface.co/spaces/multimodalart/jev-decision-index](https://huggingface.co/spaces/multimodalart/jev-decision-index)

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmvmlr/)
> 
> That’s a useful leaderboard, but it is explicitly a leaderboard of Jev reproductions, and it mixes zero-shot models with Jev-specific fine-tunes. I don’t see the strongest established zero-shot baselines like Qwen3-Reranker, GTE or strong NLI cross-encoders. Where people have compared Jev with conventional classifiers - Banking77 experiment got 93.3% from BGE-small + logistic regression versus 83.2% for Jev, at about 9ms locally. (source: [https://github.com/ickma2311/jev-baselines-eval](https://github.com/ickma2311/jev-baselines-eval?utm_source=chatgpt.com))

> **LatentSpaceLeaper** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbnnc8q/)
> 
> > Where people have compared Jev with conventional classifiers - Banking77 experiment got 93.3% from BGE-small + logistic regression versus 83.2% for Jev, at about 9ms locally.
> 
> Yes, but then again, BGE-small + logistic regression is not zero-shot. Or, from the repo you linked:
> 
> > **If you have comparable labeled data (here: 10,003 examples, same distribution)**, a small supervised encoder is the strongest option tested: 0.933, 9ms, no per-call cost. One dataset and one label budget **do not make this a universal rule** \[...\]
> 
> The value of JEV is not that it is the absolutely best classifier (quality, speed, cost). You can get that better with something picked/tuned for your specific task. The value of JEV is that you get an extremely capable classifier along these dimensions that is also extremely easy to use and easily accessible.

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbnqkgt/)
> 
> That’s not the point I’m making. My criticism is that TypeSafe’s own headline benchmarks mostly compare Jev against autoregressive LLMs instead of strong existing classifier baselines, while making broad claims about a new class of decision model.
> 
> BGE+logreg isn’t meant as a zero-shot apples-to-apples comparison. It’s an example of how much less impressive the story can look once you compare Jev to actual classification systems instead of GPT-style models. That benchmark choice is exactly what I’m calling misleading.

> **Former-Ad-5757** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbnith4/)
> 
> The better question is : Can I influence the outcome of the classification to make it fit my need?
> 
> The marketing gimmick is speed so you can have a lot of throughput, but speed by itself makes it just that a one in a million chance just happens every minute.
> 
> It is basically a classifier which classifies by unknown criteria and you just have to hope and pray that it was your criteria.
> 
> A 90% success rate on a benchmark, just basically means that if you ran your task at the exact same time, then you are guaranteed to have 10% error and no way to detect them, no way to fix them. And you aren't even sure if they tinker a bit with the settings (/quants /updates) in the evening so tomorrow you maybe have a 50% error which goes under the radar.
> 
> If i classify something today, will anybody give me any assurances that it will classify in the same ballpark over a month, or any way to check.
> 
> Basically they can never have compute restraints, as a last resort they can always put a randomizer function behind the api during heavy load and who will notice the difference? It wil just temporarily have a bit of less results will be the marketing term.
> 
> People complain about openai and anthropic downgrading their endpoints/responses over time. Here as long as it gives back numbers nobody can complain, they can just say wrong update sorry folks.

> **allanmeter** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbrk649/)
> 
> Graduated uni nearly 20 years ago with a specialisation data mining and ML… you took the words out of my mouth.
> 
> Are they not teaching things like ML basics in Universities any more?
> 
> I thought I had missed something fundamental. Seems maybe not.

> **Usual-Orange-4180** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmaide/)
> 
> I would say the news is that is generalized and with good enough performance where is very easy to prototype and also use it in scenarios where training a traditional classifier doesn’t justify the cost. I think the key of why people like it is right there on your first paragraph; with modern zero shot capabilities.
> 
> It not may be super novel, but it has a lot of engineers without ML experience finding novel scenarios for classification.

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmbwdx/)
> 
> That still describes things we already had years ago. NLI-based zero-shot classification has handled arbitrary natural-language labels without task-specific training since 2019, and Hugging Face made it basically one-line UX years ago. Sentence-transformer and reranker workflows are similarly easy to prototype with and often very strong.
> 
> So "engineers without ML expertise can now use generalized zero-shot classification" is an adoption/marketing story.
> 
> ([https://aclanthology.org/D19-1404/](https://aclanthology.org/D19-1404/))  
> ([https://huggingface.co/tasks/zero-shot-classification](https://huggingface.co/tasks/zero-shot-classification))

> **32SkyDive** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmh03j/)
> 
> While there are embeddings/rerankers/classifiers, do any of those combine the Natural context understanding of LLMs with the classifier Output?
> 
> Like from my understanding one Advantage of Jev is its ability to understand both the content provided and Natural language classifier descriptions

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmhs11/)
> 
> Yep, that’s basically exactly what NLI zero-shot classifiers do. They take arbitrary text as the premise and a natural-language description as the hypothesis, then score entailment. So they already combine language understanding of the context with language-defined classes.
> 
> ([https://huggingface.co/facebook/bart-large-mnli](https://huggingface.co/facebook/bart-large-mnli))
> 
> ([https://huggingface.co/docs/transformers/main\_classes/pipelines](https://huggingface.co/docs/transformers/main_classes/pipelines))

> **32SkyDive** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbn0d5c/)
> 
> Are those also able to Play for example Computergames fairly effectively in Realtime?
> 
> I would have thought that would have been bigger News.
> 
> If Not, were exactly ist that Gap coming from?

> **Usual-Orange-4180** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmdmn9/)
> 
> Sure, that’s part of the hustle, the question HuggingFace should ask itself is why they didn’t own this moment.

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbme1mg/)
> 
> If part of the hustle has to be misleading people, then I'm gonna point it out.

> **Usual-Orange-4180** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmf6dd/)
> 
> I’m not attacking you or your observations, I was just trying to say exposure is also necessary for a business to succeed, not just capability. May not be as interesting to you since you sound highly technical, but is always good to question why someone else is getting all the money if one was first.

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmgro0/)
> 
> Sure? Not sure what you're trying to say. That's always true? But I thought especially this subreddit would understand that misleading customers is not good and try to correct the record?

> **Ithian021** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbnnqid/)
> 
> Personally I think this JEV thing is great. It’s telling me exactly who to block on YouTube for being a paid off shill.

> **Last\_Track\_2058** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbrocj8/)
> 
> What about shills on reddit

> **GenAIDataScientist** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbo6lfp/)
> 
> This pushback on Jev is odd to me. I'm a genai data scientist, I build AI products every day for a big company. Also I did a deep learning PhD before chatgpt. So here's what I would call an informed opinion.
> 
> Jev *is* a game changer for me. The speed, price and intelligence point is a huge outlier. Therefore, it unlocks many use cases that were not feasible before. We've been using LLMs as orchestrators, for re-ranking, and other use cases where it makes a decision, classifies some data (and lots of judges in evals). We can now (or will be when they or a competitor are a mature vendor) do things like re-rank a page of results in response to feedback in realt time as a page renders, which would just have been too expensive before.
> 
> All the comparisons to simple encoders and embeddings ("this is just scikit") and so on are missing the point that the model still understands natural language inputs as well as a smart LLM. This goes way beyond a simplistic embedding vector search, which is reflected in the benchmarks. The outputs are as good as you'd get from Terra if you explained the problem in detail and asked for a class or score, but you also get uncertainties which actually mean something. So it's much more trustworthy as part of a deterministic flow.
> 
> If it's not new tech, how come there's no competitor that's as good that I can use or download? Clearly TypeSafe have some secret sauce, how wide their moat is I do not know.
> 
> Edit: Also it's way different to building a classifier - that could still work fine, but the whole point is you get a very usable zero-shot out of the box for almost free now. The generalist is valuable, training your own classifier is still non-trivial.

> **Short\_Change** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pch0p7b/)
> 
> Their competitor is free and if anyone can replicate your work, it’s harder to monetise it.

> **yaq-cc** · [2026-09-28](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pcjzj6g/)
> 
> Julia-1 is a recently released decision model to check out.
> 
> The differentiator for me is generalization and the lack for dependency management. That makes Jev much more interesting to me. I can get a no effort classification with reasonable accuracy and no extra dependencies.
> 
> If I reach for Nomic / granite / modernbert, I need huggingface, transformers, sentence-transformers, einops, torch, etc... and then I need to train a classification head and either host the stack or deal with fat containers to host it bundled.
> 
> Jev IS cool. It would be even cooler if they trained it to do some of the older school non-generative NLP technoques as well... QA, extractive, etc...

> **tiensss** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbq0ibh/)
> 
> As stated many times - I am not saying it's not useful. I did want to point out their misleading claims.

> **clduab11** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmewkl/)
> 
> No, classifiers aren't new. No, a softmax over constrained options isn't new. Yes, a finetuned ModernBERT or GLiClass classifer (GLiner) can still beat Jev on accuracy per $.
> 
> But what people need to understand is that lots of folks value interfaces, and Jev has a snazzy one. And even though that's usually not enough for people in tech discussions to pass muster (usually it goes something like "reeee MaRkeTiNg"), what SHOULD be enough is that Jev has a very easy, very cheap way of returning calibrated probablities across a HUGE tranche of data, zero-shot style, even with the most arbitrary of configs and schemas (which is where Jev's secret sauce actually lies).
> 
> Just because you see a bunch of use-cases using Jev to play Doom or whatever doesn't mean that that's what the tool was designed for.
> 
> Otherwise, folks can finetune their own encoder and probably beat Jev out. Dunno why people have to complain about it instead of putting code to paper and actually ***doing it.***

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmghu5/)
> 
> I’m not saying Jev is useless, I’m saying the marketing and some user claims massively overstate what’s actually new and superior to existing tech.

> **jonnyboyrebel** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmrvrp/)
> 
> I just like the idea that we can start educating “ leadership” at LLM’s aren’t the right tool for every project. We have the option to start using Bert again for classification and not get shouted down.

> **Material\_Policy6327** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmcjsu/)
> 
> I’ve been talking with colleagues about JEV and we’ve come to the same conclusion. Is it neat? Sure. Is it really  
> Novel and new? Eh hard to tell. Can def do similar with other techniques. I’m still curious how general it is because feels like many enterprises will use this blindly and it won’t perform on their use cases as well

> **Asleep\_Document9811** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbndu4a/)
> 
> Side note, but Embedding Models and Vector DBs are fucking awesome and I wish they were used more frequently on their own. I was able to use a multilingual version of `embeddinggemma` to create a searchable database of text in three languages (English, Arabic, Persian), and when you would search in English, it would return relevant concepts in Arabic and Persian.
> 
> that can make for a really fast and innovative in-site search engine for a lot of projects, but it's passed over for summary tools and RAG agents instead. 😩

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbnetkb/)
> 
> Yeah, vector DBs rule and are super cheap and easy to build

> **ApplePenguinBaguette** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pd63j1p/)
> 
> Absolutely, I just wish they were used for ''super fuzzy search'' more, finding things that are phrased differently but mean the same. I don't need an LLM to then summarise, just give me good results.
> 
> I'd kill to be able to search all documents, folders, images, etc. on my PC and their contents like this

> **kaneua** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbol2r2/)
> 
> Why are we discussing Jev here if it's not locally runnable?

> **tiensss** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbq25cc/)
> 
> I agree. I made this post due to so many other posts and comments about it, a lot being misleading.

> **donotfire** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pc1uzex/)
> 
> Because this is the best subreddit for discussing it

> **Relevant-Yak-9657** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbm9uqb/)
> 
> I mean, the same could have been said about GPT 3.5 as well. I think people are overreacting in both ways. Jev is here to stay and clearly has its usecases, so what is the problem?

> **Reasonable-Height704** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbma36g/)
> 
> the endless fucking hype

> **Smallpaul** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmlvwt/)
> 
> I find it fascinating that people get so bothered by hype rather than just tuning it out and focusing on what’s relevant to them.

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmxuwq/)
> 
> I was bothered by the misleading claims. I think pointing those out is always good. The AI/ML/LLM communities not being littered with misleading claims is relevant to me.

> **Reasonable-Height704** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbq0iqd/)
> 
> We get bothered by it being pushed into our awareness by the algorithm and concerted marketing campaigns against our will.

> **DrunkenRobotBipBop** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbma926/)
> 
> Oh. The usecase exists but not for Jev and it's business model.

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbma99d/)
> 
> Where did I say it's a problem? I made this post for people who are calling it novel and a new paradigm due to its performance against LLMs. There are better classifiers that have existed for years, if not a decade, that are open source, tested, faster, cheaper, more accurate.
> 
> What existed years before GPT 3.5 that was open source, tested, faster, cheaper, more accurate?

> **GodKing\_ButtStuff** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmcyop/)
> 
> This is the most pedantic use of "where did I say its a problem" I've ever seen.
> 
> Yes, you didn't actually use the word problem, but the entire context of your post is a problem statement and criticism of the conversation around Jev vs where Jev actually lives in the AI / ML ecosystem. If there wasn't some conflict (problem) between expectation and reality there wouldn't be a post.

> **Relevant-Yak-9657** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbme2a4/)
> 
> Thank you. You expressed it more eloquently than I could have.

> **DuanesKrasner** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pcwd7zh/)
> 
> It's like OP is completely unaware of his own tone and pretends us to do exactly the same.

> **Bird\_ee** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmcalc/)
> 
> At this point I’ve seen far more people whining about people being excited for Jev than I have seen people actually being excited for Jev.

> **Viktri1** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbrv6uf/)
> 
> I think it is because the mods are deleting the Jev shilling posts. When Jev first came out there were so many threads on it. It's all over social media too. I saw a mod earlier confirm that they've deleted the obvious Jev shills which his why we're left with the people complaining about it lol

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmcrai/)
> 
> Can you point out the whining in this post?

> **\-Cubie-** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbnb4qh/)
> 
> [https://github.com/huggingface/setfit](https://github.com/huggingface/setfit) is great for few-shot classifiers. It's where that Banking77 BGE + Logistic Regression baseline is from.

> **repolevedd** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbniewq/)
> 
> From my perspective, the hype around Jev highlights a couple of things: 1) the public's limited understanding of the different kinds of ML models that exist and what they're useful for, 2) and the fact that demand for classifiers actually exists.
> 
> Turns out, even for people who work with LLMs every day, the idea of using a dedicated model to make fast, fixed-choice decisions is surprisingly easy to overlook. And this idea turned out to be so "innovative" that people started attributing magical properties to it. I'll quote one such claim:
> 
> > You can't just compare Jev with any other "classifier", the whole point is that it's **generally smart**, that it can make decisions, *intelligently*, without being trained for a narrow task only.
> 
> Give it a month or two and we'll probably have a much clearer picture from benchmarks. But knowing you can classify things quickly isn't going away, and it might spawn a new class of products. Something like ready-made SDKs with APIs for training and faster processing of certain stages in pipelines, maybe. Previously, some of these ideas would only come from ML engineers who, when looking at a problem, would recognize that it was something ML could solve. Now, people with less ML expertise may recognize these opportunities themselves and bring in specialists afterwards, rather than waiting for an ML engineer to look at the problem and say, "this needs a neural network." And that's not a bad thing.

> **thicket** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmd477/)
> 
> Can you explain some more about the architectural similarities between Jev & classifiers to me?
> 
> Here's my weak understanding: Back in the pre-LLM days, if I wanted to predict, say, local temperature at 4pm from readings of several nearby weather stations at 8am, I could put together a dataset with a bunch of correct answers, and train a classifier-- maybe something fancy like a neural network, but also something trivial like a linear regression. And then I'd have a somewhat reliable classifier/predictor system for a particular question.
> 
> But-- and this is where it sounds like my understanding of zero-shot classifiers is weak, so maybe you can correct me-- if I want to ask about temperatures at 11pm, or instead predict barometric pressure or any even relatively small disturbance in my question, I'll have to train another classifier, or expand my datasets and try something else.
> 
> The appeal of Jev-style models is that, without any particular training besides the context I feed in when asking the question, I can get out some kind of somewhat reliable classification/prediction out. I don't know how accurate that classification would be, or how much I should trust the model's confidence ratings. But as far as developer experience, it sounds like this offers reconfigurable classifiers without the hassle of training my own.
> 
> I speak from some ignorance here, so I wonder if:  
> 1) Jev just isn't gonna be very accurate for lots of cases, or  
> 2) Some other zero-shot classification system is and has been more accurate for some time.
> 
> Do you think both of those statements are true? Can you point to a system that would provide a similar turnkey developer experience but return better results?

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmfbtf/)
> 
> I think your weather example mixes two different things. Predicting a continuous temperature is regression, not classification, and changing from "4pm temperature" to "11pm pressure" changes the underlying prediction problem. JEV doesn't magically remove the need to have learned some relationship between inputs and outputs.
> 
> The relevant comparison is semantic zero-shot classification. Here, reconfigurable classifiers absolutely existed before JEV. NLI-based zero-shot classifiers take arbitrary text plus a natural-language hypothesis/label and score whether the text supports it. A 2019 paper explicitly evaluated the "fully unseen" setting: new labels, new domains, no task-specific training data. ([https://aclanthology.org/D19-1404/](https://aclanthology.org/D19-1404/?utm_source=chatgpt.com))
> 
> And the developer experience is already basically what you describe. Hugging Face exposes zero\_shot\_classification(text, candidate\_labels) as an API: provide arbitrary text and runtime-defined labels, get labels and scores back. No classifier training required. ([https://huggingface.co/docs/inference-providers/tasks/zero-shot-classification](https://huggingface.co/docs/inference-providers/tasks/zero-shot-classification?utm_source=chatgpt.com))
> 
> So I wouldn't claim that some older system is universally more accurate than JEV as that needs proper benchmarking (which the Jev team didn't fucking do, but act like they did for marketing reasons). My point is that reconfigurable classifier without training your own model is not the novel part of JEV at all. We've had that for years.
> 
> And regarding architecture, we actually can't make strong architectural claims about JEV because TypeSafe has reported nothing on the architecture, it's fully closed-code. Functionally, though, context + natural-language decision/labels -> scores/probabilities is very well-established territory.

> **thicket** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmqmwm/)
> 
> Thanks, mate! Much appreciated

> **BP041** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbngfty/)
> 
> Honestly yeah, it's zero-shot classification with a fresh coat of paint. But the one thing I'll give them: constrained output is *huge* for agent pipelines — I've burned more hours sanitizing Claude Code's free-text outputs than I care to admit. Specialized tool that never emits garbage is a legit product even if the marketing pretends they invented the wheel.

> **ebfortin** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbnskk6/)
> 
> I've been less than convinced too. Their paper gives example that doesn't show much. One is a question from a client and the context added to answer the question is pretty much the answer to the question. Seems to me you still need an LLM to search possible answers before going to Jev. Which kind of beat the purpose.

> **Hackerjurassicpark** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbnze11/)
> 
> This is why I find myself not trusting Jev and the company behind it at all. If they’d come out and compared to best in class zero shot classifiers on huggingface right now like GliNER2 class of models, it would’ve been more trustworthy than the current imo misleading marketing trying to showcase Jev as something new.

> **buttplugs4life4me** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pboi27i/)
> 
> One of my friends was really big into AI even before me, and recently he posted something on Facebook about how Jev is the futur for AI and I just died inside.
> 
> Everyone wants to make the next ClaudeBot grift and it's getting old. I feel like a grumpy grandpa

> **AWizardWhoCodes** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbpey6p/)
> 
> jev fatigue…

> **Protopia** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbp1kld/)
> 
> In the AI world, if there isn't an underlying secret sauce i.e. USP, duplication is trivial. So, if this is just a very well marketed new API layered into existing classifier technology it will be duplicated in minutes and delivered even cheaper and JEV will become just another name on the AI memorial wall.
> 
> But if they genuinely have an underlying secret sauce that genuinely makes Jev something different, it might take weeks rather than minutes to create a rival service. That is still not a lot of time to establish a large base that won't be bothered to switch to a competing service for trivial cost reductions, so I am not sure you can blame them for keeping stuff secret for as long as possible.
> 
> But in the end, if they raise awareness amongst the masses for classifiers and make it easy to start using one, and thus create a market and an ecosystem, that feels like a good thing to me.
> 
> Equally, benchmarks, analysis, comparisons etc. to cut through the marketing hype and provide realistic expectations are also a good thing.
> 
> TL;DR Unlike many Reddit threads, this post is largely a useful debate to cut through the hype and bring some realism too the pros and cons of Jev.

> **AWizardWhoCodes** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbpedo9/)
> 
> who is jev and what does he want from me

> **ImpossibleCreme** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pcaimin/)
> 
> Yep

> **takenforgranteddd** · [2026-09-28](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pclkfek/)
> 
> The key test seems to be whether Jev beats strong zero-shot/NLI/embedding baselines, not just LLMs. “Constrained output” also isn’t the same as being hallucination-proof. Would be interesting to see a broad benchmark before calling it a new model class.

> **ndkjann** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pcrrquj/)
> 
> I can completely second your opinion. Its crazy. Most have probably never picked up an ML book either. I did a deep dive on Jev. Spoiler it barely holds up. [https://www.drborchers.com/en/blog/jev-field-test/](https://www.drborchers.com/en/blog/jev-field-test/)

> **KeepYourRobotClean** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pcxzz6c/)
> 
> This tells you more about the state of the industry. Crazy how even the sophisticated VCs/SV scene falls for it. Tells you a lot about the opinion leaders you find online.

> **Superb-Pair-2000** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmdncl/)
> 
> With as much hype as it's getting it's probably trash. Quantity of spam over quality.

> **Hornstinger** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmartc/)
> 
> Not to be a dick but does it really matter?
> 
> Does the tool work and is useful? If yes = use it
> 
> If you disagree with how we got to this tool from a historical categorisation and classification standpoint = use it or don't depending on what makes you feel good about yourself

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmbn72/)
> 
> It matters because claims about novelty and superiority affect what people choose, fund, and build around. If better-performing classifiers have existed for years, then presenting JEV as a new superior model class is misleading.

> **JAlbrethsen** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmeph1/)
> 
> I agree with your core premise that this is not purely novel and the marketing is annoying, but I would argue it is a significant step up from any zero shot classification I have tried previously. I have been looking at it for rule-following and policy adherence, it got an AUC of 0.93 zero shot on my eval set. For reference Gliclassv3 got 0.73 and my finetuned version of gliclass got 0.89.

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmfx8t/)
> 
> I mean, Jev may well be better than some existing classifiers on some tasks, of course. That’s completely plausible - I believe it is probably a good classifier.

> **Hornstinger** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmcibv/)
> 
> Think of it like a gateway drug. Those people would never have tried that tech in the first place if it wasn't for marketing and usually after trying a gateway drug they'll branch out into other drugs...if you catch the comparison.
> 
> Not everyone lands on the optimal path first try. Remove perfectionism from your expectations.

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmczsp/)
> 
> I have no problem with people using the tech. I have problems when what is spread about it, by their team as well, is misleading.

> **Genaforvena** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmj7hm/)
> 
> This is exactly the kind of work I was hoping someone would do, and I starred the repo mostly because the claim is actually falsifiable.
> 
> I genuinely don't care which way the result lands. If Jev turns out to be “just a good zero-shot classifier”, great - that is still useful. If there is some genuinely different reliability/latency/applicability regime here, also great. What matters to me is being able to measure where that boundary actually is.
> 
> And honestly, the openness here means a lot more to me than the current headline numbers. The repo pre-registers kill/go criteria, publishes the raw results and analysis, and then documents several rounds of corrections when review found problems - including one where tightening the cascade target to exact frontier parity flips the result entirely. That is basically how I want claims about new infrastructure to behave.
> 
> The result that interests me most is actually this one: on CLINC150 Jev gets 87% standalone accuracy, but at exact Terra parity the Jev→Terra cascade has to escalate 100% of traffic, versus 73% for nano→Terra. At a 1pp margin below Terra it looks completely different: 22% vs 48.5%. So “is Jev good?” seems like the wrong question. The useful question is: **what does the reliability/applicability frontier look like?**
> 
> For my own use case, that frontier is everything. If I am going to let something route work in a production system, I care much less whether it beats another model by 5–10pp on average than whether I can define a domain in which it reaches something like 99.8/99.9% and know when I have left that domain.
> 
> Maybe that number turns out to be impossible for an open-ended semantic router. If so, that is also a useful result: the scope contracts until the thing becomes a fancy classifier with a bounded domain. Fine. I would much rather learn that from a reproducible experiment than from either marketing or anti-marketing.
> 
> This repo is a good start precisely because it makes both outcomes acceptable.

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmju3g/)
> 
> Yeah, this is pretty much where I land too. I’m not arguing Jev can’t be useful or even excellent - anyone who wants to use it is a-o-k. But I don't like the misleading claims that I'm seeing from the team and the users of this sub.

> **Genaforvena** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmogm5/)
> 
> honestly appreciate this interaction and discussion, like for real.
> 
> i’m reading a Zen book from a discount pile right now — Russian translation of a Chinese collection of koans. I’m not Zen at all; I’m more into just appreciating *idk, living*, and letting weird Reddit interactions like this become part of my own little lossy-compressed version of human writing.
> 
> there’s one story that feels weirdly relevant here. students are asked to take care of a Zen master’s orchids. they screw up and destroy them, and the master basically says: I didn’t plant and care for the orchids for the purpose of becoming angry at someone if they died.
> 
> which is kind of how I feel about this. if Jev turns out to be brilliant, great. if it turns out to be a narrower tool than advertised, also great. the interesting part is finding out which world we actually live in.
> 
> but yeah, “over-promise and under-deliver” has become such a default industry posture that I’ve basically given up expecting otherwise. Wise Wakka warned us 16 years ago:  
> [https://www.youtube.com/watch?v=yedS2mocj5Q](https://www.youtube.com/watch?v=yedS2mocj5Q)

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmps45/)
> 
> Yeah, these are good stories to live by. And I don't even mind the over-promising so much, I just dislike being misleading.

> **ThinkExtension2328** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbvtgjl/)
> 
> Here is the thing it’s not technically new but the part that’s new is the generalised pre trained nature of it. Yes yes it’s just a classifier and we could train them all the way back in 2010 with tools like weka.
> 
> The concept of JEV “is new” in the fact it’s a pre trained generalised clasifier. I can ask the same model is “cat dog” or “is hotdog a potato” without needing new training.
> 
> Now your going to probably hit me with the ai bias question to which I will say 🤷‍♂️

> **tiensss** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbxc80c/)
> 
> That part isn’t new either. Pretrained generalized zero-shot classifiers have existed for around 7 years. NLI-based models were already doing classification over unseen, natural-language-defined labels without task-specific retraining by 2019.
> 
> Eg: [https://aclanthology.org/D19-1404/](https://aclanthology.org/D19-1404/)

> **ThinkExtension2328** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pby6tw2/)
> 
> Oooo fascinating , are there any models I can play with in that case?

> **tiensss** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbyan1z/)
> 
> Yep. Easiest place to start is BART-MNLI on Hugging Face. You give it text plus arbitrary candidate labels and it scores them zero-shot, no retraining: [https://huggingface.co/facebook/bart-large-mnli](https://huggingface.co/facebook/bart-large-mnli)
> 
> There’s also a ready-made zero-shot classification API/pipeline: [https://huggingface.co/docs/inference-providers/tasks/zero-shot-classification](https://huggingface.co/docs/inference-providers/tasks/zero-shot-classification)

> **ThinkExtension2328** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pc1djja/)
> 
> Thanks man

> **BemusedOptimist** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmvges/)
> 
> When I learn about new things, I try to reframe them in a somewhat condensed version.
> 
> For Jev (rightly or not), that became "multiple choice for a given state with confidence ratings".
> 
> I would guess that at least some of the hype comes from not remembering (or knowing) that an LLM is only one hammer in the toolbox, and everything has looked like a nail to most people the past few years.
> 
> It seems like quality and governance concerns are finally to the point where more companies are taking them seriously, and something *like* Jev would go a long way towards helping cut the judge on judge on judge on judge bills.
> 
> The only part I object a bit to is the hallucination framing.
> 
> Saying that it can't pick Q when presented with A, B, and C seems a little disingenuous because it can still be spectacularly wrong when assessing A, B, and C for the context.

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmwgho/)
> 
> Yeah, I generally agree. I’m not against Jev as a tool, and I can absolutely see why people would use it to replace a pile of expensive LLM-as-judge calls. My issue is with the claims around it.
> 
> Their claims on hallucinations are very sus. They advertise Jev as something that can’t hallucinate. Then their own nuance section says the 0% figure is not empirical, what is guaranteed is schema matching. A model can return a perfectly schema-valid answer and still be completely wrong. Calling that can’t hallucinate is misleading af.

> **BemusedOptimist** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbn0sd7/)
> 
> Given that which subreddit this is, this probably won't make you feel any better, but I would be shocked if the big labs aren't looking for older base models to slap "new" decision heads on so they can provide something similar. :D
> 
> Offer it as a separate service, charge next to nothing for it because it would be cheap to host *and* the real win is becoming stickier because you're built into corporate infra.
> 
> \</tinfoil hat>

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbn13bg/)
> 
> Oh, I definitely agree that some are doing this, absolutely. It's a quick way to score some buck.

> **JohnLebleu** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmbf5v/)
> 
> But is it just a classical classifier or can it also reason about a situation and classify based on that reasoning?

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmcex1/)
> 
> NLI models and cross-encoders have been doing semantic inference (what you call reasoning) over arbitrary text for years.

> **JohnLebleu** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmdgc5/)
> 
> Gotcha, any API we could use that is as easy as using Jev?

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbme7em/)
> 
> Yep. Hugging Face already exposes this as a simple API: send text + candidate labels, get labels + scores back. No training required. They even recommend BART-MNLI and ModernBERT zero-shot models directly for this use case. ([https://huggingface.co/docs/inference-providers/tasks/zero-shot-classification](https://huggingface.co/docs/inference-providers/tasks/zero-shot-classification?utm_source=chatgpt.com))

> **JohnLebleu** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmg3sv/)
> 
> Would it work as well on question like "I need to eat healthier and I can choose between chips and salads, which one should I pick?"
> 
> The example on hugging face shows more of a basic classification example.

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmh9ha/)
> 
> Yes. That’s exactly the kind of thing NLI zero-shot models can do. You just phrase the choices as hypotheses, e.g. "Salad is the healthier choice" vs "Chips are the healthier choice," and score entailment. The HF demo is basic, but the underlying model isn’t limited to topic labels.

> **gpt872323** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmjdfy/)
> 
> Well it is gimmick too and I did rough calculation and more accurate result. Use any model even frontier with structured output and only one word response of what option. It is very fast. Essentially open jev is doing that. I still have my doubts that without proper training how can a model be so capable to know with 3 or 4 lines. For gaming maybe yes or behind the scenes it is doing exactly that.

> **Open-Adhesiveness-86** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmrm0z/)
> 
> the banking77 number isn't apples to apples though, bge+logreg is fit on ~10k labeled examples and the zero-shot side sees none. the curve that matters is accuracy vs labels per class, and a linear head usually catches up somewhere around 20-50 each. below that zero-shot is fine, just don't trust the raw probabilities without per-label thresholds.

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmu865/)
> 
> I agree, it's not apple-to-apple. But my point was that Jev shouldn’t be benchmarked against LLMs, the interesting comparison is against strong zero-shot/NLI/reranker baselines when no labels are available, and supervised classifiers once labels are available.

> **TournamentCarrot0** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbnhewt/)
> 
> Why is it everywhere all the sudden

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbnjrxr/)
> 
> Marketing, astroturfing, bots

> **bowdoin-yale** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbni1if/)
> 
> It is indeed deceptive marketing, but what else is new in corporate AI? And I would wager that a majority of the people using mainstream LLMs are using them for the wrong things. Literally every normal person who has described their AI usage to me could have accomplished their task with older, faster, cheaper tech.
> 
> But here's the thing: if this particular hype fest brings about a renaissance of classifiers, I'm here for it, because it's a step in the direction of using the right tool for the job, and more specifically, a tool that's much less expensive in terms of computation and energy. There are already lots of "Open Jev" models out there, and the thing is, while you and I knew about BERT and MNLI and such, that lineage had received relatively little investment or development in the years since ChatGPT took off, and the context windows of the older models really are kind of limiting. So while I absolutely agree with you on calling out the hype, I'm okay with it if it puts classifiers on people's radars again.

> **Lesser-than** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pboel97/)
> 
> I refuse to be the victim of jev astroturfing by a man who wears what looks like the pink carpet in my grandma's bathroom as a jacket.

> **bakatristan** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbpb78d/)
> 
> Novel or not, getting a fast, cheap, general purpose classifier that works well out of the box is still pretty useful.

> **tiensss** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbq00by/)
> 
> I don't disagree on its usefulness, I just dislike their misleadingness.

> **psayre23** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbprbhj/)
> 
> For some tasks, I’m getting the same perf with better results from Qwen3.5-0.8b. Tiny little model, great decision making.

> **tiensss** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbq2de6/)
> 
> Try out Qwen3-Reranker-0.6B.

> **redditrasberry** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbpvlif/)
> 
> the hype around it is amazing for what it is
> 
> as you say, it's far from original, but also the use cases are quite narrow. not zero but far from the level of the hype.

> **EatTFM** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbpwspw/)
> 
> Jev clearly adresses a real problem: LLMs are weak at classification tasks as they are not trained discriminatively and cannot output probabilities. On the other hand we want to use them due to their capability of natural language understanding.
> 
> When I tested it, however, I got the impression that it does not work well, as Jev seemed always heavily biased towards the given task, e.g. spam detection: no matter the message, it always got assigned a high probability for spam, even if the message was clearly non-spam.

> **tiensss** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbq2jdy/)
> 
> LLMs are not what you compare Jev to. You compare it to years-old zero-shot/NLI classifiers, cross-encoders and rerankers that were already built for exactly this kind of task.
> 
> And your spam example is actually why the confidence-score marketing bothers me. A model returning probabilities is not the same thing as those probabilities being well calibrated or trustworthy. If it systematically assigns high spam probability to non-spam, then the nice probability output is just confidently wrong.

> **CyberBlaed** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbq3gqg/)
> 
> To me, AI started in Videogames… Those Enemy Characters and NPC’s… :)

> · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbq6amh/)
> 
> \[deleted\]

> **Wooly\_Wooly** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbqnvdb/)
> 
> So when's China gonna distill and open source it? Laya is neat too, but fine tuned qwen instead of built from scratch, but it's by a small Indian team so that's fair.

> **bigh-aus** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbsu5vq/)
> 
> Marketing + hype making it sound like it's a new tech. This is the worst part of tech imo. False hype, marketing and ads.

> **Delicious\_Week\_6344** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pcyhgfs/)
> 
> My first reaction was also that its just a 0-shot classifier (AI MSc specializing in NLP). But after actually using it for a few projects... Damn this thing is smart and easy to use. No examples needed, just does what you want it to do and it just works. Even for more obscure tasks like information density scoring it works out of the box.

> **tiensss** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pcyi2hx/)
> 
> Why do you think they didn't benchmark it against other pretrained generalized zero-shot/NLI classifiers and other similar models? To me it seemed so misleading to do it vs LLMs where of course Jev will come out on top.

> · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pd42q2p/)
> 
> \[deleted\]

> **tiensss** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pd5v6h6/)
> 
> Jev is perfectly usable and I never claimed it isn't. I said what the team was claiming about it was misleading

> · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pd874lu/)
> 
> \[deleted\]

> **tiensss** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pdaf4bm/)
> 
> I like MoritzLaurer/deberta-v3-large-zeroshot-v2.0

> **itb206** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmh9d7/)
> 
> Actually it targets people like me who have trained bert classifiers and run them over hundreds of millions of documents before and don't want to deal with managing any of that pipeline anymore. Something something normal distribution meme.

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmi4f8/)
> 
> But the alternative isn’t to train BERT and manage a giant pipeline yourself. Existing zero-shot classifiers, NLI models and rerankers are already available through simple hosted APIs, and some are stronger than Jev on proper classification benchmarks. If you prefer Jev’s API, great, no shade on you.

> **itb206** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmrc8t/)
> 
> Sure, but they didn't succeed at both dev-ex and marketing that's part of being a successful product. This seems like a classic trap from technical people. You need the whole package not just be technically good and available.

> **tiensss** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmtjw1/)
> 
> Where did I say they weren't successful? I said they were being misleading. What trap did I catch myself into by saying that?

> **Technical-Will-2862** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmhu6k/)
> 
> I actually use it to make every decision for me now. You’ll get there eventually.

> **GTHell** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/pbmhj8l/)
> 
> No shit Sherlock!
