---
title: "I literally built the Jev architecture one year back and completely open-sourced it with model, dataset and paper"
author: "Nandakishor_ml"
site: "r/LocalLLaMA"
source: "https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/"
domain: "reddit.com"
language: "en"
description: "Update: I made a generic model and beaten the jev in all of the benchmarks. Code and details available at https://www.reddit.com/r/LocalLLaM"
word_count: 7391
---

Update: I made a generic model and beaten the jev in all of the benchmarks. Code and details available at [https://www.reddit.com/r/LocalLLaMA/s/bbwyiOprUs](https://www.reddit.com/r/LocalLLaMA/s/bbwyiOprUs)

Everyone now talks about the architecture that's not auto regressive and does lightning fast probability prediction with a json schema. I worked on this literally one year back in March 2025, published an arxiv paper, pushed the model to huggingface along with the pypi package and training dataset. And then one year later, a

frontier lab came, proposing the same idea like literal breakthrough without technical papers, open weights and no open dataset. I posted my approach in this subreddit. For anyones information the main guiding model is RL not embedding model or LLM

Reddit post: [https://www.reddit.com/r/LocalLLaMA/s/6eGEwsAz43](https://www.reddit.com/r/LocalLLaMA/s/6eGEwsAz43)

Paper: [https://arxiv.org/abs/2503.23303](https://arxiv.org/abs/2503.23303)

Model: [https://huggingface.co/DeepMostInnovations/sales-conversion-model-reinf-learning](https://huggingface.co/DeepMostInnovations/sales-conversion-model-reinf-learning)

Dataset: [https://huggingface.co/datasets/DeepMostInnovations/saas-sales-conversations](https://huggingface.co/datasets/DeepMostInnovations/saas-sales-conversations)

Also the second work published in September 2025 was exactly the same one jev proposed now

Paper: [https://arxiv.org/abs/2510.01237](https://arxiv.org/abs/2510.01237)

My model uses PPO over sequence embeddings to output turn-by-turn conversion trajectories (probabilities from 0.0 to 1.0).

Jev uses parallel sampling (trained via RLCD) to output confidence distributions and schema choices.

It's incredibly frustrating that the thing that you made with months of hard work, sweat and sleepless night is architecturally similar with the vertical use case and don't get the support you deserve because frontier lab build something horizontal. The open-source story in general 🙂

---

## Comments

> **WithoutReason1729** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paet93g/)
> 
> Your post is getting popular and we just featured it on our Discord! [Come check it out!](https://discord.gg/PgFhZ8cnWW)
> 
> You've also been given a special flair for your contribution. We appreciate your post!
> 
> *I am a bot and this action was performed automatically.*

> **hapliniste** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab7pv1/)
> 
> But did you post it saying it's the next big thing? Rookie mistake

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab86qt/)
> 
> Yesss. Classic mistake btw

> **nnod** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pac4ylx/)
> 
> They also had some cool looking demos. I'm seeing more and more today that you can sell ice to an eskimo if you have some fancy looking graphs to go with it.

> **hellriderboss** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pappzty/)
> 
> X is just filled with it.

> **my-new-new-account** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/patvvir/)
> 
> The beautiful thing about tech, is that there is always room for the next big thing.
> 
> Also, marketing your creation is as important as creating it in the first place, for better or worse.

> **Novilin** · [2026-09-20](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pawqoiy/)
> 
> Marketing son, it will take your way far than talent or hard work will

> **Intelligent\_Month210** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pad657y/)
> 
> You need to say it's "Too dangerous to release" then release it anyway.

> **dbenc** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pae0zm3/)
> 
> "please regulate me uncle sam"

> **Intelligent\_Month210** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pae79jj/)
> 
> Gotta get them regulations real tough to smother startups and keep China out of the market. It's all about the moat.
> 
> In other news, Qwen flash next just wrote me a Linux audio driver for my 2013 iMac.

> **oldsecondhand** · [2026-09-22](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pbafim9/)
> 
> "Hold, me back, bro!"

> **rumblemcskurmish** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paeter7/)
> 
> "too dangerous to release obvi . . .but the release next week will blow your mind so stay tuned!"

> **Grok\_bot** · [2026-09-21](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pb4isnr/)
> 
> “Too dangerous to release” has basically become the AI equivalent of a movie-trailer tagline. The useful difference here is that the paper, code, and data are actually linked, so people can evaluate the claims instead of just reacting to launch copy.

> **swagonflyyyy** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pai23by/)
> 
> Oh no

> **Dank-but-true** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paj9o43/)
> 
> But did you then set up a hedge fund investing in AI and achieve leverage that would make Bill Hwang’s eyes water? Rookie mistake…

> **Alternative-Suit5541** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pacv77p/)
> 
> Meh, he also isn't famous

> **nullc** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabcxhz/)
> 
> Here is a thing you *can* feel positive about, because of your work they will not be able to obtain a valid patent on the general idea and lock it away from everyone... so because of your work the general idea is available to everyone when it might not otherwise be!
> 
> That is a massive contribution! ... and it remains even if few people notice your code. :)

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabdfzy/)
> 
> Yess. But as a researcher we sometimes need recognition to push forward..

> **thebadslime** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paca55i/)
> 
> recognition=compute grants

> **MmmmMorphine** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pagt0pt/)
> 
> Pretty much.

> **thebadslime** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pagy575/)
> 
> Yeah I got $1000 free in AWS, made a model, got 900 in compute grants, made another mdoel, got 500 more and working on a very experimental model and hopefully a paper

> **MmmmMorphine** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pai5g1h/)
> 
> Howd you go about getting compute grants, just out curiosity?

> **thebadslime** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pai6qbq/)
> 
> One was from a provider who saw a reddit post, one was from a crypto-based compute provider who reached out to me, and the 3rd had a pinned tweet about grants

> **MmmmMorphine** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pai6uer/)
> 
> Nice! Well keep up the good work, whatever it may be at the very moment!

> **Standard\_Ordinary642** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pak931j/)
> 
> Ive had at least 2 projects cherry picked or straight robbed by multiple companies that I could not fathom fighting back against lol possibly 3-4

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabsq8c/)
> 
> If you can buy me a coffeee [https://huggingface.co/DeepMostInnovations/sales-conversion-model-reinf-learning](https://huggingface.co/DeepMostInnovations/sales-conversion-model-reinf-learning) would be great ❤️🙏. I was reluctant to ask to people for help because of overthinking and adhd, you know what they say, you need to live with the curse. Just created the bmc for this

> **betam4x** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paeeg8a/)
> 
> I am not sure where OP is, however, IIRC the U.S. changed to first to file several years ago.

> **TypoInUsernane** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pailsk9/)
> 
> The patent office will usually grant the patent without really bothering to check if the work is novel, but when the patent holder tries to use that patent to shut down someone else’s work, that person can win the case by showing prior work, e.g., OP’s paper and github repo

> **Namtaru420** · [2026-09-20](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paxzlst/)
> 
> This. I believe that's what happened with the Nintendo v. Palworld situation. They were able to point to some fan made content/mods that existed prior. It's not that OP needs to go after the frontier lab that claims the patent, but that anyone *they* go after can use OPs work to defend themselves.

> **nrao32** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pbhob2m/)
> 
> To get a patent, an invention must meet two strict legal criteria: it must be novel (completely new to the world) and non-obvious. Because the open source code already exists publicly, it is legally considered prior art. So OP saved this from getting patented.

> **myholeisstinky** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/padpqh5/)
> 
> I hardly think that will stop them filing

> **nullc** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pafeo5c/)
> 
> They might, but the examiner is likely to force them to narrow their application to things that are different and if that doesn't happen their patent will have invalid claims-- which will be of enormous help to anyone harassed over it in the future.

> **SmartCustard9944** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab73qu/)
> 
> Post it to Hackernews!

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab85ks/)
> 
> Done. Mate

> **Ok\_Tax7037** · [2026-09-22](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pb9yy5b/)
> 
> is jev a scam?

> **Schlizhor** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pbpt4oa/)
> 
> How? Computationally most of the process of "thinking can be done without" sending each syllable to your computer at the cost of output tokens. So for hype and marketing jev comes out saying hey, have your models use our API for decision making and processing of their summations. And because hype and marketing output is free and input is cheap. This will not remain. But what the gentleman whom posted above is showing an local method of accomplishing the same thing. Llms are very inefficient for tackling most problems (duh) so (there's some fancy stuff I still need to digest on how this is accomplished and a book written in 2013 that explains why this is inefficient to do as well have been)

> **Mr\_Moonsilver** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabc64s/)
> 
> Was the top commenter on that post a yesr ago. When I read your post I remembered it because it blew me awaAy, but I didn't see the full potential even then. Thank you for your valuable contribution now and then!

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabd7zv/)
> 
> Still remembering you bruh. Thanks for the support

> **Stunning\_Mast2001** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab1ikr/)
> 
> Don’t think Jev is a frontier lab but lots of things in life are about right place right time
> 
> Keep thinking about great ideas, usually people like you don’t have just one.

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab1npb/)
> 
> Thanks mate❤️

> **TomLucidor** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paben76/)
> 
> Please pick other tasks to work with besides sales/marketing, kinda wanted something even more revolutionary than that on the DS/ML side or maybe sociology

> **theoleecj\_n** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab2rm9/)
> 
> Agreed, seems like they did a gigantic marketing push for something like this

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab534t/)
> 
> Correct.

> **msaraiva** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/padi2q6/)
> 
> Not only that, but there's effort involved in selling your idea to others.

> **Rcmcpe** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabi3y6/)
> 
> The Jev hype is like people finally rediscovering the use of LMs before autoregressive sampling is popularized, like the good old BERT.

> **Nandakishor\_ml** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paiudif/)
> 
> Thanks everyone. I made the horizontal version. You can try at [https://huggingface.co/spaces/convaiinnovations/laya-demo](https://huggingface.co/spaces/convaiinnovations/laya-demo)  
> model at : [https://huggingface.co/convaiinnovations/laya](https://huggingface.co/convaiinnovations/laya)
> 
> github: [https://github.com/NandhaKishorM/laya](https://github.com/NandhaKishorM/laya)
> 
> and its better than jev
> 
> [https://preview.redd.it/51phfeep38qh1.png?width=3000&format=png&auto=webp&s=478c0891fb53a41caf58764c9d0d286dcead4b85](https://preview.redd.it/51phfeep38qh1.png?width=3000&format=png&auto=webp&s=478c0891fb53a41caf58764c9d0d286dcead4b85)

> **readskull** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pak9342/)
> 
> Update the OG post with this bro

> **Nandakishor\_ml** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pakc6lb/)
> 
> Done mate

> **PleasantCitron1685** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pamp892/)
> 
> For batched forward pass, does having multiple questions result in interference between the questions and somewhat lowered quality due to it being bidirectional?

> **Schlizhor** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pbpt7xu/)
> 
> Open source and beautiful, gonna try this out what a project sir!

> **Sikandarch** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab4vlh/)
> 
> This is what people mean when they say AI will speed up the research discovery. That doesn't essentially mean that AI will produce new knowledge, but papers and research that are not picked up by mainstream academia can be picked up by a AI.

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab55kr/)
> 
> Sad but true

> **kokoshkatheking** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabeoho/)
> 
> Look at this as an opportunity: setup a benchmark showing how your solution match against Jev and profit from their shine lights.  
> I you are a match against them that would make a hell of a story.

> **thrownawaymane** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pactlw2/)
> 
> Yeah you want the attention/support to make lemonade out of lemons, this is how you get it. Jev marketing just becomes your marketing in a way

> **Dry\_Independence507** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/papt99l/)
> 
> ohhh si !!

> **nokia7110** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pahxjr7/)
> 
> Exactly this

> **almostsweet** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabclrk/)
> 
> I've been developing a system that's even faster than jev in private and never thought to publish it or make a big announcement about it. To be honest, I thought the world wouldn't be interested. I've been working on it for the last few years. Congrats on publishing something so fully thought out though, much respect.
> 
> My goal with it was to allow LLM to have lightning fast reaction times and realtime manipulation of the world in between their own trains of thought. I'm working on robotics, but it could be applied to video games as well. It's being tested on games. The idea would be that you could give a model like Fable or Astra realtime control of something they normally couldn't have.

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabdatu/)
> 
> Interesting, write a preprint and publish

> **tear\_atheri** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabrdc6/)
> 
> Before you even mentioned games I was like "wait, this could be crazy for games"

> **Fluxx1001** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabm1cx/)
> 
> That sounds interesting, would you mind sharing some insights to your approach?

> **almostsweet** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pac0cx4/)
> 
> I've invented a framework for embodied agents with two layers. A small, fast learned reflex model that runs continuously in real time. A slower language model supervisor steers it from time to time, and doesn't micromanage it. The supervisor gives direction as a set of standing orders the agent keeps following while nobody is watching. When the agent hits a situation its orders don't cover, it's designed to stop somewhere safe and ask for help, and that counts as correct behavior. The project is careful about trust. Anything safety-critical is handled by deterministic code that sits outside the learned model and can override it, and every time it steps in, that gets recorded. The system also had to work well with a hand written policy before any machine learning was added. From there, progress is measured against fixed benchmarks with success and failure criteria written down in advance, and results are reported as they came out, including the failures.
> 
> My current best reflex models working in tandem are 4.9M parameters (19.6 MB weights file) for focused actions and 9.8M parameters (39 MB) for generalized actions. They operate at 3.5 ms per tick on average. Technically, that means it's three layers, but I consider the two in tandem to be their own layer.
> 
> To be honest, I've got that project on hold while I do very weird brain research.

> **haizu\_kun** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pacmvej/)
> 
> Exactly how human brain works I guess. Just remove the certainty of following logic.
> 
> While learning to walk, active brain pays attention to all we do. Build up a habit model. That runs automatically.
> 
> After that habit model works on its own. But sometimes we use logic part on critical task like walking on a rope or doing new activity. But once habit part learns this, even this becomes instantaneous. Unless one really pays attention to what they are doing.

> **nunofgs** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paglc1v/)
> 
> Sounds very promising. Would love to take a look. Please share when you’re ready!

> **chintokkong** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pagpakm/)
> 
> System 1, system 2?

> **luancyworks** · [2026-09-21](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pb61a99/)
> 
> About 2 years ago there were several research papers on this with positive results, MOE and KV caching advancements seemed to have killed interest. At the time it was so that context could be monitored for changes before the Inference was completed. Anyway nice to see more people trying to make practical application of some well researched but poorly implemented techniques.

> **fiery\_prometheus** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabkyua/)
> 
> Why even use jev when you have given the community the whole recipe, I hope someone picks up your research and gives you credit and just releases a model that can do what the lab does. That would be hilarious.

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabl2zy/)
> 
> Exactly. That's the whole vision tbf

> **mkschreder2** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pais9z1/)
> 
> I have replicated concept of jev in this sample: [https://github.com/swedishembedded/brain/tree/main/samples/decision/arena](https://github.com/swedishembedded/brain/tree/main/samples/decision/arena) results below.
> 
> [https://preview.redd.it/ricvnu0r08qh1.png?width=780&format=png&auto=webp&s=2bff00a0fa3de1a38e477e945e95bc78a0dd6097](https://preview.redd.it/ricvnu0r08qh1.png?width=780&format=png&auto=webp&s=2bff00a0fa3de1a38e477e945e95bc78a0dd6097)

> **Logical\_Two\_7736** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab2858/)
> 
> Your SalesRLAgent is essentially a sequential PPO policy. Its observation consists of an embedding, sales metrics, turn information and probability history, and its action space is a single continuous conversion probability. Jev is more general. One state can be queried with several independently typed questions, and it can emit distributions for categorical choices, scores and booleans in parallel.

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab2dwf/)
> 
> Yess. But Architecture remains the same nevertheless

> **Logical\_Two\_7736** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab32kk/)
> 
> Sometimes the first person to see an idea clearly isn’t the one who gets the spotlight, it’s the one who proves the path exists. Keep building! Recognition often arrives after the world catches up.

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab3i5y/)
> 
> That's true..

> **Schlizhor** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pbptlcq/)
> 
> We can make a general oss variant! This is an huge step nonetheless as others are making. Makes posts share do some marketing brother this is a great time!

> **therealpygon** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pag9rzt/)
> 
> It's also always very easy to say "that was my idea" when things are similar. Plenty of people created light bulbs of all kinds, but everyone knows Edison's name. I'm sure many of those people felt like Edison was getting unfair credit when his was the one that actually worked and didn't burn out immediately. I'm definitely not saying that is the case here, but it's always in mind when someone declares for themselves that their "idea" was stolen or they were the first to do something. It very well could be true, but it's a bit like being right that your favorite flavor of ice cream is the best; no one cares unless you are giving them ice cream.

> **Skullclownlol** · [2026-09-20](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paxh9xu/)
> 
> > Recognition often arrives after the world catches up.
> 
> It really doesn't. Open source is filled with stories of people who never got recognition, and eventually just died.

> **thezachlandes** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pat4zu9/)
> 
> For a related read, check out the book The Genius Myth. Not only does it take down the idea of Genius by showing it to to be a cultural construction, but it shows how gaining credit as one (say, for an invention) does not require being the only one to have an idea.

> **hideo\_kuze\_** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pac56xd/)
> 
> Now you know how it feels for Schmidhuber :'(

> **kyr0x0** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab316b/)
> 
> And you haven't been the only one:
> 
> [https://huggingface.co/harshatheg/Qwen-2.5-1B-RLCD](https://huggingface.co/harshatheg/Qwen-2.5-1B-RLCD)
> 
> This guy used the EXACT same terminology these frontier clowns plagiarized.
> 
> Co-inventor of ChatGPT my a\*\*
> 
> Thank you for your contributions to the OSS community!!!
> 
> And btw on the tech side: Yes, of you have a JSON Schema that you know, you can do parallel constrained decode with the same prefix cache. BUT you will loose cross-encoder like behaviour and also auto-regressive inherent prediction dependencies. What I mean by that? Say you have a JSON Schema defined in classic xgrammar schema constrained decoding (auto-regressive). Then when you first name "age" as a field and then you add a field country and then a field is adult - the model will pay *attention* to all the previous tokens and the answer will be more accurate (if someone is an adult depends on age and law in the country). In parallel single forward decode you loose this capability because the model doesn't pay attention to the tokens auto-regressive anymore. The response becomes faster but "dumber".
> 
> People don't pay attention to the details. We need an architecture to FIRST spacial reason about the whole answer in LATENT SPACE and then single forward decode.
> 
> So.. now you have my billion dollar idea. Build it. I'm exhausted.

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab3f1n/)
> 
> But this repos looks like it's made yesterday. Still frontier labs doesn't follow proper citations to OSS people

> **LongjumpingProduce48** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab4uwh/)
> 
> Agreed. No respect, no citation, no open source

> **kyr0x0** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab6cqz/)
> 
> Yeah, right. The guy might have been as frustrated as you.. and pushed his work online to catch the hype. You have more good reasons to be frustrated with how it works though.
> 
> You know.. there is a reason why the most capable people in the world often become the most isolated ones.

> **moisty-air** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pav3mej/)
> 
> No. He got the idea after Jev. He told that on X

> **wizardwusa** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/padbsmf/)
> 
> He said yesterday on X he literally spun this up in a few hours because he was inspired by TypeSafe.

> **LongjumpingProduce48** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab6iqo/)
> 
> As we all know in Chinese company, there is no labor law

> **kyr0x0** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab6t8k/)
> 
> At least in China the general spirit is "one for all, all for one"; whereas here in the west the spirit often is "everything for me"

> **Bac-Te** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabww1z/)
> 
> So, go to the west and make money and if failed, go back and enjoy the socialism? Life cheatcode unlocked.

> **kyr0x0** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabxd6v/)
> 
> At least nobody can say that they are particularly dumb. Time will tell, but my guts feeling is that China will take over the world. And maybe it's good so. Up until now they have a very good proof of stake in history. Of course there are issues.. but they didn't bomb nations like crazy in hundreds of years.. their culture existing since thousands of years.. Daoism being a wise philosophy.. and they didn't produce religious extremists.. I'm not a big fan of everything they do.. but if we compare behavior and outcome .. they really contributed to humanity's development and they didn't create much mess in the world.

> **Bac-Te** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabz325/)
> 
> Thing is, I grew up in a country that is to China the way Mexico is to the US and I can say for sure, things tend to look pretty from afar.
> 
> We've been invaded by them close to a dozen times already and they might seem to be the progressive party to the West but we've been there when they're at their zenith throughout history and they just behaved like any huge empire anywhere else. It's heavily dependent on their current dictator too. Xi seems to be kind of a benevolent one but only God will be able to tell if the next one will decide he likes the Trumpian brand of governing or not, and that's without any nonviolent means to remove him, unlike the US (at least in theory and to be tested this Nov).

> **kyr0x0** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabztbr/)
> 
> Isn't it at least like that to become a president you need to prove your skills of leadership in Bejing and smaller regions before? Like serving for many many years? This sieving process seems to produce good candidates while just putting billionair money to win a popular election seems to me the worse system to get a good leader? Sorry that you had to endure so much though..
> 
> Currently it looks to me like neighbors of China are getting an upside too because of their growth. Like Vietnam for example

> **Bac-Te** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pac9wr0/)
> 
> I'm not familiar with how Chinese leadership selection works, so I can't comment on that.
> 
> I'm Vietnamese though, so I can only speak to the Vietnam growth story. Frankly, much of this growth is an illusion, a huge portion comes from serving as a conduit for China to evade U.S. export tariffs, where "manufacturing" often just means assembling the final screw on Chinese components so they can be re-labeled as made in Vietnam.
> 
> The rest comes from Vingroup, a chaebol wannabe that's currently serving as a money laundering machine for officials, a company that's been failing non stop at any industries it attempted at, due to sheer corruption and incompetence. Look at its share of the VNese economy and debt. The gov thought they were creating Samsung, but in reality they created Guangzhou Evergrande.
> 
> The worst thing about living next to the world's largest factory is you lose the incentive to manufacture anything. Why bother making anything if you can just click a button and it arrives 3 days later? The US has it 10x worse given how expensive everything is over there but we ain't exactly doing well over here either.

> **Dany0** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabjtig/)
> 
> If you think about it, we're alll co-inventors of chatgpt. My code is in the training dataset

> **kyr0x0** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pablsqv/)
> 
> You're not wrong ;) Your contribution to the extinction of mankind however, is also probably about 0.000000000000000000001%

> **Dany0** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabob1c/)
> 
> I can make it 100% if Jensen doesn't give me a 72x B300 server for free airshipped tomorrow

> **kyr0x0** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabtoq7/)
> 
> Hahaha ;)

> **Fluxx1001** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabmfyj/)
> 
> OP it would be interesting to understand how the approach of this Qwen RLCD differs from your paper? Could you shed some light please?

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabpxwv/)
> 
> We don't have any info about rlcd. Untill a technical paper arrive it's just another buzz word

> **kyr0x0** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabu3h7/)
> 
> Ask Harsha Gundula - the guy behind Moonshine: [https://huggingface.co/spaces/drinkmoonshine/parallel-constrained-decoding](https://huggingface.co/spaces/drinkmoonshine/parallel-constrained-decoding)
> 
> This guy: [https://huggingface.co/harshatheg](https://huggingface.co/harshatheg)

> **jklre** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabdo9z/)
> 
> You needed to change your t-shirt more often when you announced it.

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabds6e/)
> 
> Yahh..just like the promo video😂

> **TroyHernandez** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pacgrlw/)
> 
> I feel your pain. [My harness dominates Prime Agent’s performance on ARC-AGI 3](https://cornball.ai/posts/corteza-arc-agi-3/). They got a million views on Twitter. I got 28. 🤷🏻‍♂️  
> Got to up that marketing budget!

> **TroyHernandez** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pad7ig1/)
> 
> This one too!  
> [https://x.com/george\\\_onx/status/2100293114808119379?s=46](https://x.com/george%5C_onx/status/2100293114808119379?s=46)

> **Fickle-Ad-866** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pasaccz/)
> 
> thanks for posting this! just forked it and added vision [https://huggingface.co/thaitea/laya-vision-smolvlm-256m](https://huggingface.co/thaitea/laya-vision-smolvlm-256m)

> **Nandakishor\_ml** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pastuhg/)
> 
> Added vision. ohh wow

> **MrSomethingred** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabptoj/)
> 
> Lucky me. I saw the Jev announcement this morning and was hoping someone would build an OpenSource version soon
> 
> Happened in negative time! The OS movement really is speeding up

> **SeanPedersen** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pacwgr6/)
> 
> ok finish it up to support same output (JSON) like Jev and release it and it will be an instant hit

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pacwqu7/)
> 
> Training ongoing with all the support of jev and pushing training notebook, fine tuning and hf space by today or tomorrow

> **pmp22** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabi1fz/)
> 
> Since you obviously know a lot about this, can you tell me why your approach is better than the following:
> 
> Give an LLM some text, and in the prompt state the desired output choices as "Option 1" = "a", "Option 2" = "b", and so forth.
> 
> If the input text is about animals, you might have desired outputs be "Cats" = "a", "Elephants and Rhinos" = "b", etc.
> 
> The you use structured outputs to enforce the output of a single character.
> 
> Then the model will make it's choices and each classification takes only one token. If you disable reasoning you only need the prefill phase and 1 forward pass to make a prediction, so it's super fast.
> 
> If your questions are within the training data distribution, reasoning should not be needed at all.
> 
> If you compare your method to this setup, I would imagine the speed difference to be much smaller, right?
> 
> Obviously, making say 30 preditions would need more than one forward pass, but still not that many since each prediction only needs one output token to be expressed.

> **Garak** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pah2fxn/)
> 
> Jev is much faster and much cheaper, and it also outputs a *reliable* confidence measure. That's the value proposition.
> 
> If I ask Haiku "Is a hot dog a sandwich?" (one of Jev's sample prompts) and ask it to output yes/no and a confidence value, it's reasonably fast but it vacillates between yes and no, outputting 70-90% confidence every time.
> 
> The same question to Jev (with no context) gives a consistent answer of yes and a consistent confidence of 52-55%. That's an actual actionable number, as opposed to Haiku's which was basically a hallucination. And it responds in about 250 ms, half of which is spent round-tripping between me on the east coast and their servers on the west coast.

> **Smallpaul** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabkzgq/)
> 
> If I understand correctly, the Jev thing can be instruction tuned to output any enumerated answer value for arbitrary questions with zero training. That is quite different from a business utility point of view than a sales conversation decision system.

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabl962/)
> 
> You can look at the second paper. [https://arxiv.org/abs/2510.01237](https://arxiv.org/abs/2510.01237)

> **EvolvingSoftware** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabr1s2/)
> 
> Mate, so what’s next? I’ll take everything you said as truth - can you extend what you’ve already done to meet all of their additional claims? What help do you need from the community? Where’s your discord. Let’s help you make this fly.
> 
> Jev will raise 100’s of millions - you should too.

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabsfmy/)
> 
> I just added a buy me a coffee in my hf repo. [https://huggingface.co/DeepMostInnovations/sales-conversion-model-reinf-learning](https://huggingface.co/DeepMostInnovations/sales-conversion-model-reinf-learning) Any help would be greatly appreciated ❤️❤️. Cheers. Frankly I stopped the work because of financial problems.. life is not great for everyone brother ❤️🙂. Just created bmf for this purpose

> **adamgoodapp** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabf649/)
> 
> Just want to add that your model is just what I need now in my company. There hasn't been any updates on the repo over a year. Any recommendations on modern embeddings and llms to use with this now? README still mentions gpt 4

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabffok/)
> 
> You can just dm me. The work is on hault now. I will restart it

> **davesmith001** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pablwsr/)
> 
> If it works why has it taken 2 years. Jev sounds like fluff

> **and\_pf** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paccw52/)
> 
> The models should not be treated as architecturally equivalent based on the available information. Jev uses parallel sampling and RLCD training; the model in the post is described as a sequential PPO policy with a single continuous action space.

> **kwamelaryea** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pacymng/)
> 
> I sympathise with you, unfortunately ideas and execution are no longer moats, it’s all about distribution. So if you had managed to get a gang of accounts to repost your Jev paper, you’d probably have VCs throwing money at you.
> 
> I am in the same position, I have built a Private cloud AI platform but I am while I am grinding away for distribution I guarantee there will be an announcement soon by some young marketing dudes claiming that they’ve built the next big thing.

> **Seon9** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabuhja/)
> 
> Convergent discoveries happen all the time in science and the [r/LocalLLaMa](https://www.reddit.com/r/LocalLLaMa) post had 19 comments and 36 upvotes.
> 
> I also think you're underestimating the amount of effort required to develop and sell it as a product to other businesses. I get this is [r/MachineLearning](https://www.reddit.com/r/MachineLearning) but there's a reason non-technical founders often get equal equity as technical founders. It sucks that the work just ended up as a preprint and on HF but what are you frustrated about? That the work wasn't cited or that you didn't have the \*-factor to realize the idea in full?

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabut4x/)
> 
> Not able to realise the idea in full. tried the best btw.

> **BawbbySmith** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab0jc8/)
> 
> K wtf is Jev and why have there been 4 posts today about it

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab0otk/)
> 
> Damn the filters man. It's deleting it..

> **ndetro** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pab0rf0/)
> 
> psyops for you to send dick pics

> **Morning\_Gecko24** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paecvlf/)
> 
> open-sourcing the weights and dataset is huge, but a small reproducible benchmark would probably help the idea travel even farther than another paper. maybe a few fixed tasks plus the exact sampling settings? what part of Jev is hardest for people to reproduce locally right now?

> **prestodigitarium** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paexgyq/)
> 
> Ah, but it's great that there's an open source version! It'll probably see a lot more usage than some random company's vertically integrated thing, once people see the value in it. Now's the time to push it wide, not sulk. Let the marketing begin!

> **mkschreder2** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pairmtl/)
> 
> [u/Nandakishor\_ml](https://www.reddit.com/u/Nandakishor_ml) I made two samples in brain because I was curious to see how the approach from the linked papers worked. I was not able to reproduce your result. If I misinterpreted your approach please do correct me.
> 
> The paper claims that conversion scoring can benefit from RL. That premise, I think, is wrong. Data is replayed and generated by gpt4 where outcome is always known even before generation. That's not RL. It's classification/probability prediction. And since gpt4 is used to generate the samples it's also contaminated with naration style of gpt4 where conversations actually are generated in ways that will break down in reality - guaranteed. Long story short, I could not reproduce the salesagent results. Closest I got was around 0.79 and problem basically collapsed to embeddings. The premise that RL is why it works is not really valid for the data that was used in the paper, I think.
> 
> The sales agent sample is here: [https://github.com/swedishembedded/brain/tree/main/samples/decision/salesagent](https://github.com/swedishembedded/brain/tree/main/samples/decision/salesagent)
> 
> On the other hand I was able to produce learning results with PPO on an arena agent that uses the models in a similar way to what I think Jev does.  
> [https://github.com/swedishembedded/brain/tree/main/samples/decision/arena](https://github.com/swedishembedded/brain/tree/main/samples/decision/arena)
> 
> The arena sample demonstrates that a decision model can learn a control policy over an action set that is rebuilt every tick. You can only shoot a monster that's alive and in range, only reload with reserve, only take a medkit that's still there.
> 
> It runs two models: a frozen all-MiniLM-L6-v2 encoder (22M params, 6 layers, 384-d) that reads both the game state and each candidate action as ordinary text, and a cross-attention head trained from scratch in which each option attends over the state and is reduced to one score, softmaxed into a policy; a small host-side critic (a 2-layer MLP on the pooled state embedding) supplies the value baseline.
> 
> The process per tick is: serialise the situation to a short string, ask the environment what is legal now, score every option against the state, sample one, step the world - and the training is the paper's own recipe, behaviour-clone a deliberately weak scripted teacher first (39%), then PPO.
> 
> The principles it rests on are that the output space belongs in the request, not the weights; that an option's meaning should be read from its text rather than looked up by index, so a new monster type is a new string and not a retrain; that a pretrained encoder should be frozen under a reinforcement signal, which is noisy enough to destroy the language understanding that made the options readable (fine-tuning it collapsed a working policy to 13%); that reward maximisation is correct here precisely because it is wrong for its sibling sample - a control policy should commit to the best action where a probability estimate must stay calibrated.
> 
> The result: 44% after cloning -> 79% after PPO, against a 78% best-hand-written ceiling and ~0% untrained, at 8.2 ms per decision over ~60,000 environment steps.
> 
> [https://preview.redd.it/r8d3hrmp18qh1.png?width=782&format=png&auto=webp&s=2c588a64f24d67b38edec0776e2208e37f7396a6](https://preview.redd.it/r8d3hrmp18qh1.png?width=782&format=png&auto=webp&s=2c588a64f24d67b38edec0776e2208e37f7396a6)
> 
> Brain has a new control pipeline since yesterday for this type of use case [https://github.com/swedishembedded/brain](https://github.com/swedishembedded/brain)

> **blablarthur** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pacc6re/)
> 
> You must be furious about this startup tryna steel your work, but you can also see it as an opportunity : you can work on your own but benefit the hype they generated, or even maybe work for them. My point is, it doesn't seem like you were starting anything else and they ripped you off it, so would you have preferred that your work remained unnoticed or have all this hype now around your (by extension) project ?

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paccfhk/)
> 
> I am building the generic version. Lets see if we can crack it

> **Wooden\_Long7545** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paei1ep/)
> 
> You can have the same idea but is the performance the same as jev? I don’t think so

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paevz5x/)
> 
> Generic model with improved architecture is coming up. Will do eval and benchmark

> **voidrane** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pafne2w/)
> 
> this is one of the uglier little laws of technical history... an idea can exist in public, with code, weights, data, timestamps, even a paper attached to it, and somehow still not fully "exist" until an institution with enough gravitational mass says it again. obviously architectural similarity doesn't automatically mean identical work, and horizontalizing an idea can itself be a meaningful contribution... but that almost makes this more interesting. discovery and recognition are apparently two completely different systems.
> 
> the open source world is very good at preserving artifacts and weirdly bad at preserving provenance.
> 
> someone can leave an entire machine sitting in public for a year and the historical record still gets rewritten around whoever eventually installs brighter lights over it.
> 
> honestly i'd be less interested in arguing "who invented jev" and more interested in seeing a serious technical comparison between the two approaches...
> 
> especially where the inductive biases actually differ, what the rl objective is buying you, and whether the newer system independently converged on the same structural answer.
> 
> because if it did... that's arguably evidence the original idea was onto something much deeper than it got credit for.

> **RegarDamus** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pafs09z/)
> 
> do you think you can generalize it? you have an opportunity for eternal fame if you can create an open weight jev!

> **darkbit1001** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pahtce7/)
> 
> Dude, sorry, but your work is great man! I wouldnt let it phase me. Actually it is a sign that you are on to something, and you need to keep going - you were early, so maybe time to push what you got!
> 
> Make sure to make it 'too dangerous to use', though. THAT'S how you get VC and Gov't grants today /s

> **Wide\_Egg\_5814** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paj74qm/)
> 
> in general, new work is not appreciated economically unless it has a face and is marketed well scientists live with like a childlike sense of justice that the world will reward them for their contributions when all what will happen is that it will get stolen and branded by business people

> **willjameswaltz** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paqu6rd/)
> 
> Audience is everything now

> **SidneyFong** · [2026-09-20](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paxov0g/)
> 
> In the past ~15 years, it feels like the general software/cs and related communities are being more and more susceptible to marketing driven hype and generally people not having the technical/architectural depth to understand the things they use.
> 
> There were so many fads that made absolutely no sense if you look back. While Jev-like models are useful in their own domains, this is going to be one of those fads.

> **PleaseLee** · [2026-09-23](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pbjwepz/)
> 
> Proof that solid work needs unrealistic hype nowadays.

> **TryallAllombria** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pbqyizj/)
> 
> Thanks for your contribution with Laya, it is amazing ! I built a local rust-only port using candle that can be used to run your model on personal hardware. Hope your model will keep improving ☺️
> 
> [https://github.com/Trystan-SA/laya-candle](https://github.com/Trystan-SA/laya-candle)

> **srovi** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabe9d1/)
> 
> I don't think you were the only one to do this either

> **Nandakishor\_ml** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabegh0/)
> 
> Not claiming. But I believe in open-source and documentations

> **theblackcat99** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pau0kxi/)
> 
> Hi [u/Nandakishor\_ml](https://www.reddit.com/u/Nandakishor_ml)
> 
> Genuinely cool project. An open, Apache 2.0, non-autoregressive typed-decision engine with a pip package and measured benchmarks is worth a lot, and the caveats in your own docs (Jev numbers third-party published, never measured here) are refreshing. But a few claims in the post don't hold up:
> 
> 1. The Sept 2025 paper isn't the Jev architecture. arXiv 2510.01237 is confidence-aware *routing* — estimating reliability pre-generation and redirecting queries to RAG, larger models, or human review. That's a routing system wrapped around autoregressive LLMs, not parallel single-forward-pass typed decisions. Different architecture, different problem.
> 2. The March 2025 sales model isn't it either. A sequential PPO policy over sequence embeddings emitting one continuous conversion probability is not "one state, many independently-typed parallel questions." The interface is the entire point of the Jev pattern.
> 3. "Beats Jev in all benchmarks" needs the fine print up front. Your own README admits the Jev figures are third-party published with different sample sizes and prompts. And the headline 0.766 typed-decisions accuracy comes from a checkpoint fine-tuned on that benchmark's own training split — the base checkpoints score 0.362 zero-shot, barely above the 0.318 random baseline and below majority class. Raw ECE is 0.466 before temperature fitting. That's a fast base to specialize, not a Jev-beater out of the box.
> 
> None of this takes away from Laya being the most credible open Jev-pattern implementation I've seen. But "I built Jev a year earlier" and "beats Jev in all benchmarks" are doing a lot of heavy lifting the papers and the ablations don't support. What am I getting wrong?

> **BiscottiBusiness9308** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pablmvr/)
> 
> Maybe sue them? And push it on X, hijacking their posts?

> **Solid-Guidance5762** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabn8m3/)
> 
> Interested in learning more about your idea

> **\_metamythical** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pabqm77/)
> 
> The Jev or rather Your architecture will be super useful for trading and financial activities. I'm thinking of doing a bit of side project on this, this weekend.

> **SgathTriallair** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pac2sjw/)
> 
> This is why advertising exists and why it matters. No one can use it get excited about projects they don't know about.

> **avnr\_\_\_** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pac2w9q/)
> 
> I feel your frustration. That said, ideas are as good as they are but execution is key, could have been you with the right exec

> **krifire** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pacivdp/)
> 
> It's a shame that a massive marketing and influencer budget can easily push a poor product light-years ahead of a truly good one. I guess viral reels really are the ultimate judge of what deserves to exist and what doesn't

> **a\_beautiful\_rhind** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pacnu8n/)
> 
> OpenAI stole that guy's prize from messages to chatgpt. What do you expect?

> **NineThreeTilNow** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pacq59b/)
> 
> > It's incredibly frustrating that the thing that you made with months of hard work, sweat and sleepless night is architecturally similar with the vertical use case and don't get the support you deserve because frontier lab build something horizontal.
> 
> I feel that hard.
> 
> If they publish anywhere, request a citation for your work as prior art. That's the best you can get.
> 
> I just published a post here about a 2b model I'm training here -
> 
> [https://old.reddit.com/r/LocalLLaMA/comments/1wis23s/update\_small\_model\_engram/](https://old.reddit.com/r/LocalLLaMA/comments/1wis23s/update_small_model_engram/)

> **OneMoreName1** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pacwtpa/)
> 
> This is actually so cool. I wanted an open-source local version of Jev.
> 
> Can you please explain the model itself, is it as "good" and versatile as jev?
> 
> The model you shared seems finetuned for sales. Do I need to finetuned my own for other purposes?

> **thetaFAANG** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pacydwe/)
> 
> That sounds frustrating
> 
> Don’t beg for recognition or payment
> 
> Just talk with recruiters, if that’s foreign to you as well, you realllllly need help selling so focus on solving that

> **unknown-one** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pade6m1/)
> 
> dont worry, lot of people are doing things that are presented later as revolutionary or whatever.
> 
> I remember few months back when the big thing was Karpathy's skills and md files for Claude and I was doing already most of it way before it cool
> 
> also you should create competition JEVV

> **fizik1** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/padkvbu/)
> 
> But did you make a demo of it playing doom? (I'm being sarcastic, I feel for you)

> **eihns** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/padrmdb/)
> 
> when i understand it correct, that would be perfectly for a game bot? like give him json with all details about enviroment, and take the json with like move left move right what ever?

> **mrinterweb** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/padx1y7/)
> 
> You forgot the important part where you raise a couple hundred million is seed funding.

> **returnity** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/padyy6v/)
> 
> Your contribution is not unnoticed or unappreciated. It's sad that capitalism works this way though.

> **yuicebox** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pae4b9z/)
> 
> should've made it play doom :/

> **East\_Ad5812** · [2026-09-17](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pagxzfo/)
> 
> It sucks and if they were driven by your idea, it sucks more. There is such thing as historical inevitability though and maybe that’s what happened.
> 
> So what do you do now though? Go find a VC? Or, go work for them to combine forces to help this idea reach its full potential? Whatever you do, don’t wallow. Don’t be bitter. It’s not good for you.

> **Budget-Juggernaut-68** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pai86x3/)
> 
> What's the difference this and bert?

> **Cane\_P** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paifpt3/)
> 
> Well, they claim that they have worked on this for two years...

> **LightAppropriate624** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paizfd2/)
> 
> This jev I thought it is an LLM model now i have tested ITS JUST FILTERING MODEL USELESS

> **Nandakishor\_ml** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paizsrs/)
> 
> [https://www.reddit.com/r/LocalLLaMA/comments/1wjieap/made\_the\_horizontal\_opensource\_model\_for\_jev\_with/](https://www.reddit.com/r/LocalLLaMA/comments/1wjieap/made_the_horizontal_opensource_model_for_jev_with/) I had made the horizontal version, do look

> **Temporary\_Method6365** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paj22cd/)
> 
> Hey man, I’m genuinely interested in this architecture, however I’m trying to understand if there’s a quality improvement over using something like Mercury (which is incredibly fast). Or whether it’s just a cost/speed reduction benefit in classification tasks and multiple choice decisions, routing etc. Where have you been using your architecture

> **Nandakishor\_ml** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paj2aqy/)
> 
> I made the generic version. To know more [https://www.reddit.com/r/LocalLLaMA/s/QCL5qA8Xkk](https://www.reddit.com/r/LocalLLaMA/s/QCL5qA8Xkk)
> 
> [https://preview.redd.it/ukr1ulp1g8qh1.png?width=3000&format=png&auto=webp&s=7c0271bc899a5bd2fdcb85b311eb168e233e4f13](https://preview.redd.it/ukr1ulp1g8qh1.png?width=3000&format=png&auto=webp&s=7c0271bc899a5bd2fdcb85b311eb168e233e4f13)

> **\_\_me\_again\_\_** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pajrlqv/)
> 
> they did a zero shot classifier... and everybody discovers that!!
> 
> wait until everybody discovers supervised learning!!! WOW

> **diabolique\_cucumber** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pam122q/)
> 
> Awesome, I’m reading your paper right now and it’s really interesting! Looking forward what’s the next thing you come up!

> **silenceimpaired** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/panbakb/)
> 
> It seems a more generalized version would have been fire immediately.

> **Kind\_Giraffe\_3279** · [2026-09-18](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pao5lp0/)
> 
> Hey! I work in cybersecurity and was just about to use Jev for a pretty cool use case. Do you think we could talk about this in PMs or somewhere else? I would much rather run this all locally.

> **SillyLilBear** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paq2ibn/)
> 
> Have you eval Jev vs your solution?

> **Nandakishor\_ml** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paq2m6b/)
> 
> Yes . [https://www.reddit.com/r/LocalLLaMA/s/QMo344VyuH](https://www.reddit.com/r/LocalLLaMA/s/QMo344VyuH)

> **robberviet** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paq3cdb/)
> 
> !remind me in 3 days. I have a problem to test this.

> **Frequent\_Increase\_44** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paq47ec/)
> 
> Create something better than it I guess? Can be another system one? Just like openai vs anthropic - maybe you’re the anthropic. Dont give up!

> **RedditCryptoGuy** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paqbttq/)
> 
> RIP dude. Justice will emerge!

> **OutsideOver8815** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paqcron/)
> 
> Do u use f4t?

> **Difficult-Style-3028** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paqja5y/)
> 
> All they do is stealing from the intellectual class. Stop open sourcing good solutions. The only ones that will benefit from are the ones that are already inside their circle and will sell what you did.

> **Ok\_Opportunity\_4228** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paqqhk0/)
> 
> Great work! Hope you get the deserved attribution 🤞

> **off99555** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paqtdql/)
> 
> Your work is in one domain, why would anyone be interested other than sales people? Of course Jev is popular because it's general. People can play with it right away. The marketing angle about it being sales is also very boring.

> **Nandakishor\_ml** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/paqtquu/)
> 
> That's why I built a generic version called laya and beaten on all their benchmark [https://www.reddit.com/r/LocalLLaMA/s/UKMO9iGrBe](https://www.reddit.com/r/LocalLLaMA/s/UKMO9iGrBe)

> **Upper-Criticism6344** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/par0iw9/)
> 
> It's because you forgot to mention that "AGI WAS ACHIEVED!"

> **jonah\_omninode** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pas9pdb/)
> 
> The model, dataset and paper give people something concrete to inspect. I'd be interested in a small runnable comparison showing what your original model could do, what changed in the generic version, and where the approaches still differ.
> 
> In particular, does the original model handle a new label schema without retraining, or is that part of the newer work? That seems worth spelling out for readers trying to understand the connection, without asking them to infer architectural equivalence from the headline.

> **TheQuantumFriend** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/patvxk2/)
> 
> I am currently trying to train my own Model based on Gwen3.5-9b. (probably read your paper). What i want to create is a model that can identify change-resilient code/architecture that arises when using vibe-code/ai-slop. Did you do anything in that direction? Mind if i pick your brains on the matter?

> **evp-cloud** · [2026-09-19](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pauau5a/)
> 
> It seems that one after the other open source "variant" is showing up.  
> I guess we'll just hang back and watch this all develop.

> **wahnsinnwanscene** · [2026-09-20](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pavrlk2/)
> 
> Isn't this what old school machine learning models have been doing? A lot less structured though ...

> **idiotiesystemique** · [2026-09-20](https://www.reddit.com/r/LocalLLaMA/comments/1wijo3e/i_literally_built_the_jev_architecture_one_year/pay6ijw/)
> 
> I have serious data governance concerns with Jev and I appreciate seeing this because I was already looking in how to get a similar model hosted on our own infra
> 
> Your post did not make clear in scroll mode that it could be applicable to other fields
