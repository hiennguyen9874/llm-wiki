---
title: "Jev vs. Kev: open-source Jev alternative tested side by side"
author: "facethef"
site: "r/LocalLLaMA"
source: "https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/"
domain: "reddit.com"
language: "en"
description: "We hosted Kev 4B (Jared Palmer's Apache-2.0 fine-tune of Qwen3.5-4B) and ran it side by side with Jev on the same endpoint to see how it com"
word_count: 1319
---

We hosted Kev 4B (Jared Palmer's Apache-2.0 fine-tune of Qwen3.5-4B) and ran it side by side with Jev on the same endpoint to see how it compares.

We built a fresh set of 362 items published after both models shipped (new arXiv papers, Stack Exchange questions, GitHub issues), with answers taken from the source.

A few findings:

\- Accuracy lands within 2 points on every task, inside the noise at this sample size

\- Jev is better calibrated and pulls ahead on paraphrase detection (PAWS 87.0% vs 74.5%)

\- Same list price, but Jev counts a fixed ~257 extra input tokens per request (same count calling TypeSafe directly), so short requests cost up to 12x more

Benchmark code, test items and results are on GitHub if you want to run your own. Both models routed via my startup Opper. Happy to dig into specifics.

---

## Comments

> **Thin\_Pollution8843** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc0t631/)
> 
> Guys I completely miss all that hype. How can I use that model? As a companion for bigger model as example

> **Theio666** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc14ifr/)
> 
> It's an universal classifier, fast one at that. For my app, that's something I'll be adding as a mean to detect prompt injections from the data tools(like precheck web fetch result so it doesn't alter agent behaviour). Cheap fast protection layer.
> 
> Other options - smart mode router - when user types their question, periodically classify and suggest skill/mode.

> **DigThatData** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc1f6qi/)
> 
> all LLMs are universal classifiers.
> 
> EDIT: Downvoting me doesn't change the fact that this was basically the title of the GPT3 paper six years ago. [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165)

> **ReadyAndSalted** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc688sd/)
> 
> Correct, hence kev just being derived from Qwen 4b. The point is though that it's a small non-reasoning model finetuned only for rapid classification. Technically the model is not that different from an LLM, but practically from a dev perspective it's used very differently. It's extremely cheap and fast, meaning if you need to quickly classify something, like "is this email spam?" Or "which button do I press to login?" You get an almost instant and almost free answer. You could just use a structured query to GPT-6 Luna set at low reasoning, but it'd be much slower and more expensive.

> **admnb** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc5g19a/)
> 
> Its a Zero Shot classifier i guess. The goal is only revealed at runtime

> **tribat** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc3p7pr/)
> 
> I’m using it to classify user messages in a chat and call tools without an LLM call.

> **Single-Eye-9788** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pcbhcok/)
> 
> What app have you been working on if you want to share?

> **Theio666** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pcce521/)
> 
> Enterprise shit, so can't really share internal details, sorry. TLDR would be some agentic platform for documents feeling and deep research, so it has a lot of data retrieval from random sites, meaning you'd want a protection of what data goes to agent.
> 
> For myself I've used jev to do some sorting of saved messages in telegram to save actually needed ones to obsidian and clean up the log. Also in the process of testing jev as the cheaper integration for hermes -> obsidian bridge habits, but there it's not a clear win since I have legacy GLM coding plan, so essentially endless 5.3 usage, and it solves the problem perfect, so that one more like a playtest.

> **Single-Eye-9788** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pccmr6s/)
> 
> Sure understandable, still very interesting thanks for sharing🙌

> **LelouchZer12** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc233m9/)
> 
> It's basically a zero shot NLU model, so nothing that is a breakthrough but still can be convenient for simple use cases without the need for finetuning on specific data if the use case is generalist enough.

> **lordchickenburger** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc2zf85/)
> 
> here is what people are using them for [https://capitalandcompute.net/blog/jev-use-cases/](https://capitalandcompute.net/blog/jev-use-cases/)

> **facethef** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc0uz0p/)
> 
> You can host it yourself or use it here it’s so cheap it’s basically free [https://opper.ai/community/kev-4b](https://opper.ai/community/kev-4b)

> **Top-Evidence174** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc1nydf/)
> 
> Could you add Mica to this? It's an open 4B model on the same /v1/systemone API. I made it, so I'd like an outside test. In my runs it beat both Kev and Laya on held-out and JevBench hard, at around 50 ms on a 3090.
> 
> [https://huggingface.co/sky7350/Mica-v0.1-4B](https://huggingface.co/sky7350/Mica-v0.1-4B)

> **facethef** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pcc352z/)
> 
> Thanks for sharing will take a look at get back to you

> **Barry\_22** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc1zlpa/)
> 
> Those names are so dumb

> **NotTodayGlowies** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pcak8ir/)
> 
> I for one can't wait for the inevitable clones, Bev, Dev, Sev, and Lev.

> **LelouchZer12** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc0wu2t/)
> 
> No comparison with [https://huggingface.co/fastino/GLiNER2.5-Decide](https://huggingface.co/fastino/GLiNER2.5-Decide) ?

> **Dry-Chemistry4487** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc14g4p/)
> 
> we added laya, could look into GLINER [https://opper.ai/community/laya](https://opper.ai/community/laya)

> **BalorNG** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc1rdep/)
> 
> At first I've read "Deicide", and thought "do they pretend to have ASI", lol

> **ggPeti** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc0idwz/)
> 
> Why did you do it on 3.5?

> **wFXx** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc0z8ju/)
> 
> there is no small qwen after 3.5

> **facethef** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc0k4gw/)
> 
> You'd have to ask Jared Palmer: [https://huggingface.co/jaredpalmer/kev-4b](https://huggingface.co/jaredpalmer/kev-4b)

> **mehow333** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc0y4cx/)
> 
> Because he wanted to use Base model

> **\_\_JockY\_\_** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc0oeya/)
> 
> Just be glad his clanker didn’t use 2.5.

> **hellomistershifty** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc1tdhc/)
> 
> the hottest new local model: llama 3.1 8b

> **MalabaristaEnFuego** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc5gxqx/)
> 
> [https://preview.redd.it/xx5ghxvxnurh1.png?width=220&format=png&auto=webp&s=d22375185854c627e5014f7f685a03734d5a4798](https://preview.redd.it/xx5ghxvxnurh1.png?width=220&format=png&auto=webp&s=d22375185854c627e5014f7f685a03734d5a4798)

> **simcop2387** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc0omui/)
> 
> My guess is that it's because 3 is very well known to finetune nicely but also that there's a LOT of large models out there that recommend training 2.5 and 3 depending on their cut off date and will sometimes refuse to acknowledge that 3.5, 3.6, and 3.8 actually even exist.
> 
> I'd also suspect that given the specific task for this that the combined instruction tuned and reasoning model setup makes the training a little more difficult to setup without lobotomizing things. Not too hard probably but it'd definitely be another concern in training the newer models. I'm betting we're going to start seeing some more kev-style models in the coming weeks though based off gemma-4, qwen-3.5 (i'd actually love to see a 0.8B version for comparison) and some of the other SLMs.

> **Operation6370** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc33xp8/)
> 
> A 4B fine-tune matching proprietary within noise on held-out data is less about Jev being bad and more about open base models getting absurdly good.

> **Charming\_Support726** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc0u2nw/)
> 
> Great. BTW: Did anybody tried to create a Decision Model based on a bidirectional model like a T5 or BERT style? Like T5Gemma or similar. Thought it could bring additional efficiency?

> **harrro** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc27ugz/)
> 
> Laya, gliner and nli are BERT/Modernbert base

> **Charming\_Support726** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc4cj77/)
> 
> Thx for the info. I always wonder about the "Jev-Marketing-Train", but never dived deep into the topic.

> **peachy-pandas** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc98ilu/)
> 
> GLiNER models are bidirectional encoders.

> **r16051studio** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc2mj5h/)
> 
> waiting for Jevon.

> **SpicyWangz** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc4cxxs/)
> 
> What about Jevv

> **release\_the\_kraken\_1** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pccn19l/)
> 
> What is with the naming convention bro, Kev is my fking nickname.

> **XtremeHammond** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc46oam/)
> 
> BERT NLU re-invented in 2026 😄

> **peachy-pandas** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc98okb/)
> 
> BERT + $40M seed round 😂

> **XtremeHammond** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pcdnjv5/)
> 
> T5 re-invention coming up next 😂

> **Dry-Chemistry4487** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc149y8/)
> 
> Laya is on opper as well [https://opper.ai/community/laya](https://opper.ai/community/laya)

> **shakshukinha** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc7bfiy/)
> 
> [u/facethef](https://www.reddit.com/u/facethef) thanks for sharing the post. In case it helps, I've been stress-testing Jev and Kev, and so I decided to give Kev more of an actual performance baseline that's comparable to Jev, so I forked `llama.cpp` to add support for the TypeSafe API with Kev.
> 
> For now, it supports `jaredpalmer/kev` model and my own checkpoints which keep comparable accuracy while halving storage use. To use it:
> 
> 1. Install the latest release from [https://github.com/espetro/llama.cpp](https://github.com/espetro/llama.cpp) (`kev` branch)
> 2. Download the Kev GGUF model, link in the README.md too.
> 
> If you found it useful, leave a ⭐ so we get it upstream asap!

> **EnjoysFiction** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pcyi6g9/)
> 
> Genuine question, why couldn't i just have my llm itself restrict itself to true/false outputs in the system prompt instead of using JEV? Is it pricing, or something else?

> **kukly-** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pd8d8yc/)
> 
> Latency and insane price difference, jev responds almost immediately compared to your model starting to think on background and reasoning (which I believe you also pay for)

> **WorriedBlock2505** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc25mj6/)
> 
> I never liked kevin in ed ed n eddy so I'ma stick with jev tyvm.

> · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc0xzs4/)
> 
> \[deleted\]

> **CodingWithSatyam** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wq2hfc/jev_vs_kev_opensource_jev_alternative_tested_side/pc45zwl/)
> 
> Every upvote in this post and every down vote on your comment did care about it
