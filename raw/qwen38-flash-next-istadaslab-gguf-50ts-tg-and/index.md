---
title: "Qwen3.8 flash next ISTA-DASLab GGUF 50t/s TG and 1500t/s PP with 12GB VRAM and 64GB RAM Laptop on 'Strata' engine"
author: "MLDataScientist"
site: "r/LocalLLaMA"
source: "https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/"
domain: "reddit.com"
language: "en"
description: "I think most people are sleeping on this inference engine. I tried multiple llama.cpp forks and none of them comes close to the inference sp"
word_count: 4986
---

I think most people are sleeping on this inference engine. I tried multiple llama.cpp forks and none of them comes close to the inference speed of Strata. Initial version had some bugs with kv cache, cpu throttling and the developer fixed them.

Inference engine (only runs on Nvidia for now; AMD support is experimental): [https://github.com/Niko1221/Strata](https://github.com/Niko1221/Strata)

Here are some metrics with screenshots. My laptop has 5070ti 12GB VRAM, 64GB ddr5 RAM, Intel 275HX CPU, gen4 SSD.

[Aquarium test (unsloth studio connected via local API)](https://preview.redd.it/kuvpvdsywksh1.png?width=2128&format=png&auto=webp&s=65b3b3f3873b61988b5f2d2a853786ab394deaad)

The model I used was [https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/main/IQ3\_XXS](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/tree/main/IQ3_XXS) which has a good quality for its size. Above, the model generated the aquarium test. At 43k context depth, it was running at 51 t/s. Stock llama.cpp reached only 23t/s with the same quant.

[32k context read at 1500t/s (unsloth studio via local API)](https://preview.redd.it/7dys133vxksh1.png?width=823&format=png&auto=webp&s=d8a4357cc2a94b30b5e63a030b02bedd4994d1a2)

This quant could only reach 100t/s PP with stock llama.cpp using the same quant. Strata was reading 32k context text at 1500t/s. This is way above my expectation. This quant can load with up to 200k context at 8bit. However, I was only using 131k context.

[Memory utilization](https://preview.redd.it/qglw20ynyksh1.png?width=1309&format=png&auto=webp&s=2b86c7a87c5f2d4afa89bbb4311507244e1ed304)

As you can see it is utilizing 11GB VRAM and 56GB RAM (includes system/OS programs).

This engine is specifically built for one model only and only select ggufs (ISTA-DASLab) work with it. You can use IQ3\_S from ISTA-DASLab which they claim recovers full model's performance on coding benchmarks. I tested IQ3\_XXS for some time and I would say it is an excellent model.

I never thought 12GB VRAM would be enough to run frontier models from 6 months ago locally on a laptop. What a time to be alive!

---

## Comments

> **Atretador** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcxp0ni/)
> 
> did anyone validate if it output the exact same tokens in the exact same sequence for the same input compared to llama.cpp? was an unanswered on the author of strata\`s thread

> **LetsGoBrandon4256** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcxry5l/)
> 
> > I cross-compared 2 Blender tests and coding test in JS = identical results. I have not tested other things
> 
> Considering the author doesn't even know what logit and KLD is, yeah...

> **Atretador** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcxsp4m/)
> 
> I mean it was def vibecoded all the way thru, you can build a inference engine with dsv4.1 flash in a couple hours.
> 
> but if we can get some people to validate this and the speed holds up this could be huge for GPU poor people.
> 
> tho Im skeptical, I did see a 60% tg boost on my own llama.cpp fork with a modified expert cache from an old PR that never got in - tho it was 60% over garbage, but at least its somewhat usable now xD
> 
> so Im trying to be positive

> **ForsookComparison** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcxsb91/)
> 
> I'm all for vibe coding useful tools without needing to understand the basics but the only output validation done was 3D model oneshots..?

> **quantanhoi** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd2lbxm/)
> 
> actually from 3D models oneshot you can see attention to details of these models
> 
> Swift 1.5 based on 3.8 27b for example is a less overthinking model that stop once the thing works, there is no attention to detail, it do exactly what you want, what you tell it to do and that's it

> **MLDataScientist** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcxq0fj/)
> 
> there is no mention of this. I can test this if you can share how it is done. Since they are different engines, not sure how to replicate the same conditions for both of them (e.g. the same seed and parameters).

> **Atretador** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcxrr40/)
> 
> you can probably delegate this to an agent to test if you just pass the requirements for it.
> 
> Use the exact same GGUF, tokenizer, prompt/token IDs, context, and deterministic settings (temperature=0, greedy/argmax). Generate 1–10k tokens across short, long, random-token, and multilingual prompts; require zero token mismatches. For logit-level equivalence, additionally compare the raw logits at every step within a defined numerical tolerance.
> 
> since strata is CUDA only I cant really test it on my dinosaur, tho I would expect some divergency - it shouldnt be too egregious.
> 
> If the speed holds with little degradation this would be huge

> **maschayana** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcxwpxu/)
> 
> Wouldn't you want to go for sampled/fixed seed also?

> **EnthusiasmPurple85** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd8jnis/)
> 
> I did it with Claude help, I get the following
> 
> \[1/8\] OK IDENTICAL 37 chars
> 
> prompt: What is the capital of Australia? Answer in one sentence.
> 
> \[2/8\] OK DIVERGES first differing char #219, similarity=0.994
> 
> prompt: Write a Python function that returns the n-th Fibonacci number iterati
> 
> llama : '\`\`\`python\\ndef fibonacci(n: int) -> int:\\n """\\n Returns the n-th Fibonacci number using an iterative appro'
> 
> strata: '\`\`\`python\\ndef fibonacci(n: int) -> int:\\n """\\n Returns the n-th Fibonacci number using an iterative appro'
> 
> \[3/8\] OK DIVERGES first differing char #210, similarity=0.447
> 
> prompt: Explain in three sentences why the sky is blue.
> 
> llama : "Sunlight enters Earth's atmosphere and scatters in all directions, but shorter blue wavelengths are scattered "
> 
> strata: "Sunlight enters Earth's atmosphere and scatters in all directions, but shorter blue wavelengths are scattered "
> 
> \[4/8\] OK IDENTICAL 354 chars
> 
> prompt: Compute 17 \* 23 + 144 / 12 and show the steps briefly.
> 
> \[5/8\] OK IDENTICAL 23 chars
> 
> prompt: List five prime numbers greater than 100, separated by commas.
> 
> \[6/8\] OK IDENTICAL 58 chars
> 
> prompt: Translate to French: 'The quick brown fox jumps over the lazy dog.'
> 
> \[7/8\] OK IDENTICAL 352 chars
> 
> prompt: Summarize the plot of Romeo and Juliet in about 60 words.
> 
> \[8/8\] OK DIVERGES first differing char #310, similarity=0.977
> 
> prompt: Write a haiku-style description of a GPU, then explain your word choic
> 
> llama : 'Silent heat blooms,\\nParallel rivers of light,\\nPainting worlds unseen.\\n\\n### Explanation of Word Choices\\n\\n\* \*\*'
> 
> strata: 'Silent heat blooms,\\nParallel rivers of light,\\nPainting worlds unseen.\\n\\n### Explanation of Word Choices\\n\\n\* \*\*'
> 
> identical: 5/8 within tolerance: 8/8 avg agreeing fraction: 79.50% errors: 0
> 
> VERDICT: PASS - Strata matches llama.cpp within tolerance
> 
> raw answers: results\_strata.json / results\_llamacpp.json
> 
> using the script in the link [https://pastebin.com/EW9mgbiT](https://pastebin.com/EW9mgbiT)

> **Atretador** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd8y6hq/)
> 
> thank you, this is interesting data
> 
> over 95% on most cases but one with a 44% divergency
> 
> Ill have to dig in the code to figure how the speed gains came to be so huge

> **leonbollerup** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd07eij/)
> 
> no, but feel free todo it.. kinda the thing about open-source.. we help each other..

> **Atretador** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd09qx9/)
> 
> I cant, this is CUDA only D:

> **leonbollerup** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0n6ve/)
> 
> ahhhhh.... sorry mate..

> **Lopyhupis** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0hhn8/)
> 
> Apparently the published speed tables on Strata (Look at the methodology notes in bench/results/2026-09-29-speed-0126/README.md, 2026-09-29-speed-0122/README.md and 2026-09-28-speed-0114/README.md on the repo) were measured with greedy decoding, so they're the best case, so I’d expect lower speeds than what is published on the repo.

> **MLDataScientist** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd15bbq/)
> 
> I am not relying on the reported metrics. I ran the model with Strata on my laptop. I shared the performance metrics with screenshots in my post. The model can consistently generate text at 45t/s.

> **ECrispy** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd14zzs/)
> 
> maybe I'm missing something, but llm's are probabilisitc - how can 2 runs in 2 different engines be output token identical? even 2 runs in llama.cpp will not be identical

> **Atretador** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd3i9cg/)
> 
> you can force them to be 'same tokenizer, prompt/token IDs, context, and deterministic settings (temperature=0, greedy/argmax). Generate 1–10k tokens across short, long, random-token, and multilingual prompts; require zero token mismatches' + fixed seed

> **ECrispy** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd3ix9h/)
> 
> I see. There are many many people here with rigs that can do that. I dont really see why the original author has the burden to do this, when they admit they are not an expert in these matters.
> 
> Instead they are being shamed and ridiculed and entire project is being questioned.

> **Atretador** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd3l028/)
> 
> the project is being questioned cause its a extraordinary claim without proper methodology, its hard to believe when you release a fully vibe coded tool which you addimit to not have tested properly nor understand how to test properly and it beats every single other tool used in the industry by 2-3x.
> 
> heck I could make Next Flash run at +100tk/s on an ancient CPU messing with seeds and ngram spec gen, but it wouldnt really be usable.

> **ECrispy** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd3lq3i/)
> 
> yes I understand the skpeticism. what I'm saying is its open source, plenty of people here with monster setups could easily test and validate it and it'd be far more useful than all the posts questioning it. hell if I had that ability I would.
> 
> it just seems a very negative reaction instead of trying to help

> **Atretador** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd3mini/)
> 
> well, I cant run it since its CUDA only, and I didnt even ask the author it was an open question.
> 
> and yea, this wouldnt be hard to test - someone could just task a cloud agent to test and compare the output, and I need a proper comparison to be able to actually recommend this which if it holds like 90% of the quality at this speeds I wouldnt care much if it diverges a bit.

> **truejeffrey** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcy1ime/)
> 
> I'm fairly certain Strata gets its speed from Greedy Decoding (aka always selecting the most probable token) because when I was trying to configure it I found messing with the temperature in any capacity didn't affect the models output.

> **Interpause** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcyce9f/)
> 
> did you also turn off thinking and increase top-p and top-k? otherwise its hard to notice. I managed to get clear difference in sanity between T=0 and T=1.5 with thinking off and top-p and top-k maxed in the web ui. also, I had qwen3.8 flash next overthink and analyze the code thoroughly for any hardcoded greedy thinking and it didnt find anything that would suggest temperature isnt respected.

> **leonbollerup** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd07omj/)
> 
> i changed temp. and it does not change the performance ..

> **iz-Moff** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcz8hk7/)
> 
> It feels almost magical. I would have been happy with a couple extra tokens per second, but this ones runs like 3x as fast as llama.cpp.
> 
> I suppose it's possible that they somehow alter the model's output to achieve this speedup, but i don't know, i tried running this quant in both strata and llama.cpp, and it doesn't feel like the output in strata is noticeably different.
> 
> Which makes me wonder, if it is possible to squeeze so much more performance out of a model, even if it is designed to work with one specific quant, how come no one really does that with other models?

> **imnotzuckerberg** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcz3ksk/)
> 
> I am losing track of all the inference engines, especially as of recently. We should have a wiki or something to aggregate. As few models are becoming key, the improvement is around the inferencing part and optimization for specific hardware, which make a lot of things very promising!

> **leonbollerup** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd07uqc/)
> 
> agree... the top onces right now (atleast for me: Ninfer, strata, llama.ccp and vllm)

> **bring\_back\_the\_v10s** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd1gbhd/)
> 
> exllamav3

> **leonbollerup** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd1jdng/)
> 
> heard about.. but also heard its basiclly the same as llama ccp.. have you tested it ?

> **MLDataScientist** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd16aql/)
> 
> there was a post about custom inference engines. I think this will become the standard for new models. Each popular model will have its own specialized engine that is tuned to squeeze max performance out of hardware. Engines that implement support for all the models will have to sacrifice some performance to be compatible with most models.

> **Interpause** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcy97ef/)
> 
> so far no issues running it connected to vscode copilot, but thus far ive only been doing code auditing only. my setup: `./setup.sh --setup --no-start --build --family qwen --model IQ3_S --kv k8v4 --context 262144 --vision gpu --port 8069 --host 0.0.0.0 --low-ram off --backend cuda`
> 
> So thats the ISTA-DASLab's GSQ-RCO quant, q8 K q4 V cache with rotation (if commits to be trusted), full context and vision on RTX 4090 + 4x16GB of DDR4-3200. At 64K context I get about 1000PP and 70TG
> 
> ill do smth more challenging than code auditing when i feel like it to subjectively check for issues, but so far seems perfectly fine (that said ivent used qwen3.8 flash next at a higher quant on on a stable runtime like llama.cpp so i cant tell)

> **Important\_Drag\_6890** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcypbkt/)
> 
> The 64K result is probably the most useful data point here. If you do compare it with llama.cpp, a deterministic run at temperature 0—ideally checking logits or token sequences rather than just whether the final answer looks good—would be really informative. The speed is exciting, but matching behavior at long context would make the case much stronger.

> **Illustrious\_Grade608** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcz6yt1/)
> 
> Can that sub ban bots ffs

> **FlashyAct** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcxxry7/)
> 
> Im watching this software closely from few days. On my rtx3060-12GB i have 32-40 tk/s on iq3\_xss O.o on 35B A3B i had that amount. Hard to believe. But few days ago it didnt even work properly, but there are many commits daily. Lets give it few weeks and we will have great engine. Cant wait :D

> **AdamFields** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcxsaus/)
> 
> I have 32gb of vram(5090) and (unfortunately) only 32gb DDR5 6000MT/s dram, will this work for me?
> 
> EDIT: I currently run the AtomicChat IQ4\_XS quant at 40t/s generation and 500t/s pp.

> **DOAMOD** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcy43ne/)
> 
> For me 5090 4-4.5k pp 100-130tgs 262k, I need try GP too

> **AdamFields** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0max5/)
> 
> Holy... on 32gb RAM? Which of the artifacts/quants?

> **MLDataScientist** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcxtb9j/)
> 
> There is automated SSD offloading. But I don't know how much it is going to impact your inference speed. If you have no traffic limit, try the engine. It will suggest the right quant model for your system. You could probably try it.

> **MyOldAccountWasAwful** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd33s16/)
> 
> From my experience/testing over the past 24 hours, the SSD offloading provides zero noticable drop in speed. I'm running on an i9-14900kf + 128GB DDR5 (5600) RAM + 1 RTX 3090 Ti. I've hit peaks of 69.1 t/s TG and 2640 t/s PP, and lows of 19.4 t/s TG and 2030 t/s PP. I'm averaging ~37 t/s TG and ~2200 t/s PP. All with context max set to 262144. (Edit: the IQ3\_S quant) (Edit 2: I've been using it for coding all last night and all today in Zed IDE, ~17 hours straight running at this point.)

> **KnownAd4832** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0lgv3/)
> 
> It will work just fine because you can put a lot to 5090 already.

> **Prestigious-Act-1577** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd09zpr/)
> 
> Not well. If you run the small models you are leaving a lot of intelligence on the table. At least iq3xxs is what you need.

> **soyalemujica** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcyg50e/)
> 
> I'm using it with a 7900XTX +64 GB Ram IQ3S model of Qwen 3.8 Flash Next, used it to perform some UI changes and some features C++ wise, and it did it flawlessly, at 45 to 60t/s even at 110k context, way faster than Qwen Dense

> **MLDataScientist** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd194av/)
> 
> exactly! faster than the dense model and better accuracy.

> **brakeline** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcz0bof/)
> 
> When they fix the cache hits and invalidation of cache for concurrent requests... It will. Be golden!
> 
> Unfortunately my opencode decides to many times to send a parallel request and kills the already cached data

> **KnownAd4832** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0okvg/)
> 
> Today or tomorrow (owner of Strata here)

> **brakeline** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd1kg0y/)
> 
> Nice! I'm testing Strata right now and I have a few pointers:
> 
> Tested 2x 3060(1xpcie3x16+1xpcie3x4)
> 
> 16x > 650 pp 4x > 550 pp 16x+4x > 190 pp
> 
> TG between the 3 conditions is within margin of error (30 to 35)
> 
> One thing I would love if real time log of PP speed instead of only writing to log in the end. I know stdout has something but only progress, no tk/s

> **exacly** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcz7hlo/)
> 
> I wish there were some q4 quants, rather than topping out at IQ3\_XXS. My use case depends on both coding and world knowledge, and I'm reluctant to sacrifice a big chunk of that world knowledge. I've got dual 5060ti's and 96 GB DDR5, so I have some hardware to work with, but I can't find an inference engine for Q3.8FN to take advantage of it. Currently running Unsloth's UD-IQ4\_XS under llama.cpp at a fraction of the tok/s and loving the quality of the model.

> **KnownAd4832** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0l3p8/)
> 
> Unsloth quants are coming up next. (Im the owner of Strata btw)

> **MLDataScientist** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd17751/)
> 
> thanks for working on this repo. Yes, unsloth quants would be amazing. Thanks!

> **rpvelloso** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pczwuuj/)
> 
> Exllama V3/tabbyapi

> **RealEddoursul** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcziumx/)
> 
> I doubled throughput (x2 from Strata), will share soon.
> 
> UPD: No karma to post here, see my post in another sub [https://www.reddit.com/r/LocalLLM/comments/1wu6fka/qwen\_38\_flash\_next\_doubled\_strata\_throughput\_on/](https://www.reddit.com/r/LocalLLM/comments/1wu6fka/qwen_38_flash_next_doubled_strata_throughput_on/)?

> **sophosympatheia** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd022to/)
> 
> Strata works. I'm running the IQ3\_S quant at ~90 tok/s on 2 x 3090s and 96 GB of DDR5. I don't know what a higher quant of Qwen3.8-Flash-Next handles like to make a comparison, but I'm not finding anything to complain about so far.
> 
> It's pretty sweet.

> **carteakey** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd3wz4p/)
> 
> This is just insane. I just ran it on my 4070 at 50+ tok/s and 2000tok/s prefill and the same quality as i was getting with a bigger quant at barely 20 tok/s and 300t/s prefill at best. The age of custom inference engines tuned to specific hardwares is here!

> **MLDataScientist** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd7yn2f/)
> 
> Yes, exactly. The speed is amazing and the quality is the same as Q4 quants. I thought my laptop could never reach that speed. But now, I use it daily.

> **HiddenMushroom11** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcxxdfp/)
> 
> Yeah, Strata rocks. I'm currently getting 60 TOK/s with a 3060 12gb + 64gb of DDR4 RAM.

> **Educational-Region98** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcxyfpf/)
> 
> Which quant are you running?

> **HiddenMushroom11** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcxzldj/)
> 
> IQ2\_XS(non-swift) = ~57–60 tok/s decode  
> Coder = ~46–51 tok/s decode
> 
> Currently downloading the swift version to try out.

> **HiddenMushroom11** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcxzur1/)
> 
> And some runs I've gotten up to ~58–64 tok/s. Here's the full table:
> 
> **IQ2\_XS**
> 
> | Engine | KV | max-context | Decode peak |
> | --- | --- | --- | --- |
> | v0.1.20 | int8 | 262k | ~47 |
> | v0.1.20/v0.1.25 | q4\_0 | 262k | ~51–54 |
> | v0.1.25 | k8v4 | 100k | ~50 |
> | v0.1.25 | q4\_0 | 131k | ~52–55 |
> | fork (THP) | q4\_0 | 131k | ~58–60, 63.6 |
> | fork (THP) | q4\_0 | 262k | ~56–61, 61.0 |
> 
> **Coder**
> 
> | Engine | KV | max-context | Decode peak |
> | --- | --- | --- | --- |
> | old mainline | q4\_0 | 262k | ~42 |
> | old mainline | q4\_0 | 100k | ~44 (43.6) |
> | fork (THP) | q4\_0 | 262k | ~46, 51.0 |
> 
> The StrataGP fork ([https://github.com/gputier/StrataGP](https://github.com/gputier/StrataGP)) is a community fork of Strata whose `madvise(MADV_HUGEPAGE)` change backs the ~30 GB expert cache with 2 MB memory pages instead of 4 KB ones, cutting CPU cache/TLB misses enough to boost my decode speed ~15% (~52 → ~58 tok/s) — all with bit-identical output.

> **wisepal\_app** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0072x/)
> 
> any quality difference between int8 and q4\_0 kv? can we add models like qwen 3.8 27b to it?

> **HiddenMushroom11** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0v1c0/)
> 
> Not sure about the quality difference. I think Strata is mainly for MoE models(Flash Next) while 27b is dense.

> **leonbollerup** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd084v0/)
> 
> i tested both.. and with the latest changes to 0.1.26 GP is slower..

> **pmttyji** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd5wvy8/)
> 
> Hi, Could you please share stats using latest version(v0.1.31 or later)? So much updates last couple of days

> **Educational-Region98** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcxzrb3/)
> 
> Dang I need to try this. Wondering if it would beat 27b by a significant margin. (In terms of speed at least)

> **MLDataScientist** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd17txr/)
> 
> multiple independent tests show qwen3.8 FN edges out 27B. And people like me cannot run 27B with 12GB VRAM. So, MOE model gives me the the best of both: speed and accuracy.

> **Educational-Region98** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd1909s/)
> 
> Yeah, it's crazy how good this one seems to be. (I have to try it when I get home from work)
> 
> This is probably the new 35b that I was looking for.

> **HiddenMushroom11** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcy2bd7/)
> 
> You should definitely give it a go!

> **realmintyowl** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcxyzix/)
> 
> Are you using same model as OP and also is your usecase coding? Can you share your rig config?

> **HiddenMushroom11** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcy28jx/)
> 
> The StrataGP fork ([https://github.com/gputier/StrataGP](https://github.com/gputier/StrataGP)) is a community fork of Strata whose `madvise(MADV_HUGEPAGE)` change backs the ~30 GB expert cache with 2 MB memory pages instead of 4 KB ones, cutting CPU cache/TLB misses enough to boost my decode speed ~15% (~52 → ~58 tok/s) — all with bit-identical output.
> 
> \---
> 
> Rig (single-GPU Flash-Next on Strata):
> 
> \- GPU: RTX 3060 12 GB (Ampere, sm\_86)
> 
> \- CPU: i5-12600K — AVX2 only, no AVX-512 (matters: ~82% of experts run on CPU)
> 
> \- RAM: 64 GB DDR4
> 
> \- OS/stack: Linux, Docker
> 
> Model / engine:
> 
> \- Qwen3.8-Flash-Next, IQ2\_XS (ISTA-DASLab base quant)
> 
> \- Strata — specifically the StrataGP fork (github.com/gputier/StrataGP) for its madvise(MADV\_HUGEPAGE) change
> 
> \- KV: q4\_0, streamed to RAM → lets me run 262K context (only a small KV window stays in VRAM; the rest streams from system RAM)
> 
> \- Engine on the 3060; ~11.5 GB VRAM used (weights + ~4,300-expert GPU cache)
> 
> Performance (warm):
> 
> \- Decode ~58 tok/s (63 peak), prefill ~630–660 tok/s
> 
> \- Cold TTFT scales with prompt length; warm/repeated-prefix TTFT is sub-second
> 
> Biggest tip: on an AVX2 CPU the bottleneck is memory-access latency, not raw bandwidth — the StrataGP fork's hugepage (THP) change gave me ~+15% decode (52→58) by killing TLB thrashing on the ~30 GB expert arena, bit-identical output. XMP and CPU-pinning did nothing; the THP fix was the whole win.
> 
> \---
> 
> I have a 2nd 3060 and a V100. The 2nd 3060 is running the mmproj. But you can get all this running on a single 3060 if you have vision off.

> **ConspiracyPhD** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcy8fn2/)
> 
> I was getting 31 t/s decode with a 3060 12gb and Strata. I have the i7-12700k, 80 gb DDR4 (3200). Second 3060 12gb slowed it down to 21 t/s. Same model you were using but not using the original Strata, not StrataGP. Don't know where the bottleneck is in my setup. Was using a windows setup as I'm doing some other things in windows right now so may need to test it later on the linux partition to see if there's any improvements.

> **Chips\_fr\_** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcya0ct/)
> 
> Exactly my setup. Faster than my qwen 27b setup for a bigger model...
> 
> Q4 is possible on a 12GB + 64 GB setup with llama according to this site, would be interesting to see if strata succeed too:
> 
> [https://carteakey.dev/blog/running-qwen3-8-flash-next-locally/](https://carteakey.dev/blog/running-qwen3-8-flash-next-locally/)

> **leonbollerup** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd08cf8/)
> 
> for 27b.. did you try ninfer?.. i just tested the wallawalla fork together.. freaking impressive..

> **HiddenMushroom11** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0q2m5/)
> 
> Can you link us the wallawalla fork? I couldn't find it. Ty

> **leonbollerup** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd15jwb/)
> 
> [https://huggingface.co/wallawalla47/Qwen3.8-27B-NVIDIA-NVFP4-NInferV3](https://huggingface.co/wallawalla47/Qwen3.8-27B-NVIDIA-NVFP4-NInferV3)
> 
> [https://github.com/Wallawalla47/ninfer-custom](https://github.com/Wallawalla47/ninfer-custom)

> **HiddenMushroom11** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd17tm6/)
> 
> Thank you

> **betam4x** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pczx1jl/)
> 
> Me with 32gbDDR4 + 24gb VRAM 😭
> 
> I’ve GOT to get a new AM5 board so I can use my DDR5 again.

> **Prestigious-Act-1577** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd09nyj/)
> 
> Ddr5 doesn't matter. CPU performance and pcie bandwidth/version is more important. Even ddr 2400mhz is enough to saturate pcie 5 16x.

> **betam4x** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0d1ok/)
> 
> I am aware, however I have 64gb of unused DDR5 and a Ryzen 7950X thanks to my board catching on fire. My current system only has 32gb DDR4.

> **leonbollerup** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd07a5r/)
> 
> nope.. working with that engine also.. getting around 110-120 in tg and around 2700 in pp
> 
> its amazing.. but more work can go into getting up pp

> **MLDataScientist** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd19xzd/)
> 
> what hardware do you have? GPU and RAM?

> **leonbollerup** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd1jny1/)
> 
> i have .. some (in my companies)..
> 
> but for my private llm, an Olares One.. i9 with 96gb ram and a 5090M graphics..

> **draconic\_tongue** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd1o1l4/)
> 
> the pp is not gonna get itself up?

> **leonbollerup** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd1to0d/)
> 
> hah.. i'm afraid not..

> **Corosus** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0h8nd/)
> 
> 5070 ti, 13600k, 128gb dual channel DDR4 3200mhz RAM
> 
> Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ2\_XS
> 
> 2000 pp, 80-120 decode t/s, amazing
> 
> Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ3\_XXS
> 
> 60-80+ decode t/s
> 
> i can crank the max context size up to 150k and it doesn't slow it down because it was already all on ram at this speed, aside from 32k if i understand correctly, need to actually pay attention to how it works now that its not just another fork to try and move on from.
> 
> finally found what i need to get flash next running at great speeds to want to use it regularly for random things.
> 
> Also using froggerics chat\_template\_peculiar\_ragdoll\_qwen\_sharp.jinja with it to really streamline its focus
> 
> I passed my pagoda test well enough for something thats been whipped to not overthink: [https://coros.us/ai/testing/pagoda\_1/?compare=1,11](https://coros.us/ai/testing/pagoda_1/?compare=1,11) - right one is the froggeric'd Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ2\_XS. I think the left one was on xhigh, amazing result for that one, if you let flash next just keep goin it makes amazing results.

> **mitirki** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd2dazy/)
> 
> I'm running the Coder version with 256k context, and while it's super fast (75-105 t/s on a 3090), it goes into thought loops frequently, until it maxes out its reasoning budget.  
> Has anyone experienced this?

> **MLDataScientist** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd4gheh/)
> 
> That is a pruned model. You should use the full non pruned model if possible.

> **sonicnerd14** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd2xu24/)
> 
> I did at least once from a couple tests. I lowered the reasoning to medium, and it completed the requests. Clearly not a flawless model, but can still get stuff done.

> **HighSeasArchivist** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0y1he/)
> 
> I wish people would focus on more intelligence at the same tok/s, but it seems like no one cares about that. High speed complete horseshit output seems to be the only thing that gets the clicks.
> 
> ETA: lol this guy below is off his meds.

> **deanpreese** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd10nau/)
> 
> Could not agree more.

> **fallingdowndizzyvr** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcyehlh/)
> 
> I tried it before and only got half the TG t/s that was advertised. But back then, what was it a whole 2 days ago, the PP was only like 600. So if it's 1500 now like in your title then it's time to try it again.

> **MLDataScientist** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd18zrh/)
> 
> I was also amazed when I saw 1500t/s on my 12GB VRAM. MOE model reaching that PP is something I did not think was possible. But yes, I tried it multiple times. It works.

> **KnownAd4832** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0p6su/)
> 
> Try again :))

> **EnthusiasmPurple85** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pczkarz/)
> 
> can confirm swift 1.5 iq3xss working in rtx3090 + 128gb ddr4 3600. t/s at 70 with peaks of 85 and pp ~1200 t/s. on mainline it was at 25t/s and 750pp with ub and b at 4096.
> 
> does anyone have confirmation that it isn't degraded? would be huge

> **KnownAd4832** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0ogo5/)
> 
> Its not degraded… those are standard RCO quants and swift quants…

> **EnthusiasmPurple85** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd8k2bo/)
> 
> I answered the most voted comment with a comparison between strata and llama.cpp

> **araujoluks91** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0qpp4/)
> 
> I did some back and forth with GPT 6.1 last night and optimized the hell out of it. Running ROCm on Windows, 5600X + 9070 XT + 48GB DDR4.
> 
> Prefill is 1030ish and decode very stable at 46 on 32k context.
> 
> I will do a few more rounds of optimizations tonight and see where I can get. Already got double for prefill (500 to 1000), but decode is stuck at 46.
> 
> I might open a PR, not sure if I have enough free time to actually clean it up and get it in a decent shape, but yeah, it runs on Windows and it's running VERY WELL. It runs so much better than llama.
> 
> Ah, model is q2\_0. I might upgrade to 64 or 96GB and try to run Q3

> **bennmann** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0ve5v/)
> 
> I have a 9070 xt and 64GB 3200mhz ddr4, please do make your changes public and remember me :)

> **araujoluks91** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd3uh8v/)
> 
> There you go: [https://github.com/Niko1221/Strata/pull/302](https://github.com/Niko1221/Strata/pull/302)

> **araujoluks91** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0vnk1/)
> 
> will do!

> **sleight42** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcxtfye/)
> 
> Maybe... at the smallest quant. Depends how much room your OS takes up.

> **caetydid** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcy2agm/)
> 
> On rtx3090 pp is more like 1/5th of that 1500, isnt it?

> **MLDataScientist** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd1ajgh/)
> 
> rtx 3090 is 2x more powerful than my 5070ti mobile. You should get more than 1500t/s PP.

> **caetydid** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd55rpo/)
> 
> \[strata\] reading the prompt: 11,664 of 30,765 tokens, 11 s so far
> 
> \[strata\] reading the prompt: 19,856 of 30,765 tokens, 17 s so far
> 
> \[strata\] reading the prompt: 28,048 of 30,765 tokens, 23 s so far
> 
> \[strata\] reading the prompt: 30,760 of 30,765 tokens, 28 s so far
> 
> i get 70-80 tps and ~1000 tps PP. Still impressive - llama.cpp gave ~300.

> **caetydid** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd80wfg/)
> 
> I've tested it on rtx5090 with swift 1.5 xxs and ctx=256k: >6000t/s PP, 160-190t/s gen! Seriously evaluating to switch from the Qwen 27B.

> **Thac0-is-life** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcytiqg/)
> 
> Thanks for this. I was looking at a way to run Qwen Next, I will try on my 7900xtx

> **Thac0-is-life** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcz1z6g/)
> 
> Getting around 50tk/s with a 7900xtx and 64GB Ram, 128k context with the IQ2\_XS, using the regular Strata, not the fork. This is really good!

> **PrimeDirective8** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcz6iod/)
> 
> Intel/Vulkan: Look at all those Nvidia and ROCm kids playing :-(

> **BringTea\_666** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcz8auy/)
> 
> I can confirm that strata is super fast.
> 
> With my RTX5090 i get around 100-120t/s at 0 context using qwen 3.8 Flash Next ISTA-DASLab quant.

> **DeProgrammer99** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd04w9d/)
> 
> Why does it say "The model is a team of 24,576 small specialists ("experts")" when it's 512 experts?

> **MLDataScientist** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd1apu1/)
> 
> each layer has 512 experts. you multiply 512 by layers.

> **Dear\_Training\_4346** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd08aiv/)
> 
> Dual-GPU (32GB VRAM) + 64GB DDR5... No matter the context I choose, always getting this error:
> 
> Error: 400: {"type":"invalid\_request\_error","message":"prompt (45670 tokens) + max tokens (86517) exceeds the context (131072); requests are never truncated"}

> **bsofiato** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0rs4n/)
> 
> Does it work with a unsloth quant ? I saw the docs and it appears that it only works with a handful of ggufs (the coder seens to be ripped)

> **pmttyji** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd5xysr/)
> 
> > Does it work with a unsloth quant ?
> 
> Yep, [v0.1.31](https://github.com/Niko1221/Strata/releases/tag/v0.1.31) onwards

> **ECrispy** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0y87l/)
> 
> how well would this work with 32GB ram?

> **GrumpyCat79** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd4t235/)
> 
> I wish it would support SM70/Tesla V100!

> **Murky-Routine-4255** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pdc9g0j/)
> 
> Up

> **Botoni** · [2026-10-04](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pdt76np/)
> 
> It's impressive. I can run coder-IQ1\_M at a speed close to qwen3.6 35b-a3b (22 vs 30 t/s). Question is, should I? Is coder at iq1 more capable than qwen3.6 35b-a3b at q4\_k\_m?

> **realmintyowl** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcy3crq/)
> 
> Thanks for sharing the rig cfg. Given that you are using 4bit for KV cache, this will struggle to write code. But I could be wrong.

> **fallingdowndizzyvr** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcyeasj/)
> 
> It has an option to use a 8bit KV cache.

> **realmintyowl** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pcyf0x2/)
> 
> the point is what budget hardware can squeeze the max intelligence out of this rig config with enough space for coding context. Trying to understand if this combo is it

> **MLDataScientist** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd1b0r3/)
> 
> I am using 8 bit kv cache.

> **shanehiltonward** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0fynq/)
> 
> A shame it is on Windows...

> **alloyevolutionist** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd0wsa5/)
> 
> running perfectly fine on ubuntu...

> **MLDataScientist** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd1auh7/)
> 
> It is both for linux and windows.

> **shanehiltonward** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wtv43r/qwen38_flash_next_istadaslab_gguf_50ts_tg_and/pd1h5hy/)
> 
> Thanks. I realized after I cloned the repository and ran the ".sh".
