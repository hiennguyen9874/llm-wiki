---
title: "Qwen3.8-Flash-Next on 12GB VRAM - 65 tokens per second"
author: "KnownAd4832"
site: "r/LocalLLaMA"
source: "https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/"
domain: "reddit.com"
language: "en"
description: "A while ago I posted 15 tok/s output and 100-120 tok/s prompt processing with the IQ3_XXS quant on a 12GB RTX 5070 using llama.cpp. Since th"
word_count: 8092
---

A while ago I posted 15 tok/s output and 100-120 tok/s prompt processing with the IQ3\_XXS quant on a 12GB RTX 5070 using llama.cpp. Since then I built my own inference engine for this one model and this kind of PC. The same IQ3\_XXS now runs at **~65 tok/s output** and **~430 tok/s prompt processing**, and the 2-bit quants run faster still using RCO-GSQ quantization.

**Using:**

64GB DDR5 (5600)  
12GB RTX 5070 SFF (Gigabyte)  
Ryzen 5 7600 CPU  
Windows

**Output (tokens/s) on 128K context:**

Q2\_0 (equivalent to unsloth Q3): 65.1  
IQ2\_XS (equivalent to unsloth Q4): 52.0  
IQ3\_XXS (equivalent to unsloth Q5): 44.8

**Prompt processing (tokens/s) on 128K:**

Q2\_0: 543  
IQ2\_XS: 472  
IQ3\_XXS: 414

Requirements:

Q2\_0 = 37.6GB minimum in RAM+VRAM

IQ2\_XS = 39.2GB minimum in RAM+VRAM

IQ3\_XXS = 47GB minimum in RAM+VRAM

Vision encoder = 0.91GB additionally

You can now one click install and run the engine with low cost hardware (currently only optimized for CUDA).

GitHub: [https://github.com/Niko1221/Strata](https://github.com/Niko1221/Strata)

Model: [https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF)

---

## Comments

> **nasone32** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbt9p54/)
> 
> have you verified it is logit-identical to a normal inference engine? I am a bit skeptical about the results, there are shortcuts that can make things fast but make model diverge a lot from the original.  
> EDIT: I don't want to diminish your results in any way, congrats for your engine, if it works it's really impressive numbers, I am just applying some scientifical skepticism based on the results of other inference engines.

> **cezarducatti** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbzy61v/)
> 
> I'm in on this too, I'd love to believe it, but there's no such thing as a free lunch... I'll be following along. Congratulations to the team for their hard work 👏👏👏

> **Most-Trainer-8876** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcyfnaf/)
> 
> Only people who are using this engine are the ones who are GPU poor. How can they perform this test when they can't even run the original model.

> **eihns** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc4p1zc/)
> 
> do u know if that is the reason some variants offer code like RDNA/RDNA/RDNA/RDNA/RDNA/RDNA/RDNA/RDNA/RDNA/RDNA/RDNA/RDNA/RDNA/RDNA/RDNA/RDNA/RDNA/RDNA/RDNA/RDNA/RDNA/RDNA/ (like for ever spamming something random?)

> **Designer\_Elephant227** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtt2vj/)
> 
> Qwen3.8-Flash-Next runs for me on ExLlamaV3 at 5.05 bpw via TabbyAPI on the RTX 5070 Ti and 85gb ddr5 (of 96), with the experts offloaded to the CPU. Context is 199,936 tokens. Kv at q8 Generation: ~21.5 tok/s Prompt processing: ~1,740 tok/s
> 
> [https://huggingface.co/turboderp/Qwen3.8-Flash-Next-exl3](https://huggingface.co/turboderp/Qwen3.8-Flash-Next-exl3)
> 
> | Quant | bpw | KL vs bf16 |
> | --- | --- | --- |
> | EXL3 | 6.05 | 0.0031 |
> | **EXL3 (my setup)** | 5.05 | 0.0040 |
> | EXL3 | 4.05 | 0.0067 |
> | NVFP4 W4A16 | 4.00 | 0.0100 |
> | UD-IQ4\_XS (GGUF) | ~4.25 | 0.0165 |
> | EXL3 | 3.05 | 0.0177 |
> | UD-IQ3\_XXS (GGUF) | ~3.2 | 0.0349 |

> **KnownAd4832** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbwsd47/)
> 
> Looking into EXL3 next because it seems to be the best compression method out there.

> **wisepal\_app** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbxgv85/)
> 
> interesting. What is your setup? Can you share please.

> **albuz** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pby2tgo/)
> 
> is there MPT support for this model?

> **Designer\_Elephant227** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbyc0cc/)
> 
> Yes but it runs slower with mtp on my system

> **jafarykos** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc5tw5r/)
> 
> I've had Astra running a number of tests, and the EXL3 is so far the winner for Qwen Flash Next. Last night it got MTP working on Flash Next - GSQ-RCO (3.065bpw core + BF16 Embeddings + MTP4) and the test suite took 51minutes to finish versus Flash Next - EXL3 (4.05 + 6bit ngram + MTP4) taking only 19 minutes. We changed the EXL3 to use FP16 for the ngram and MTP and the timing shot up quite a bit, but then again I'm loading the ngram from my nvme.
> 
> Anywhooo, as it iterates on configurations I'll let you know if anything fun falls out. This is 4x3090 though not a 5070TI. I do have a 5070ti but only 64gb ram in that computer.
> 
> Currently getting 122 tok/s decode, 1.5k tok/s prefill.
> 
> Next up is for Astra to iterate on engine changes and see if it can do anything interesting.

> **lllll03l** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbt5loi/)
> 
> I dont understand how your IQ3 XXS is equivalent to unsloth Q5?

> **vacon04** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbt9zou/)
> 
> The ISTA-DASLab quants are highly regarded. They're not that different to Unsloth in the sense that they don't uniformly quantize a model, but instead prioritize keeping higher precision on sensitive tensors while compressing more some of the more resilient ones.
> 
> Is their IQ3\_XXS the same as Unsloth Q5? Not really, they've been quantized with different recipes. Is it most likely way better than a generic, uniform quant? Most likely yes, while also being more efficient in terms of the size vs quality balance.
> 
> So what I would say is, don't think of this IQ3\_XXS as a generic IQ3 quant, this has been quantized in a mor sophisticated way and may retain better quality than your typical IQ3 quant.

> **Certain\_Yam\_5824** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbthdp5/)
> 
> WSB has fried my brain bc idk how to interpret the first sentence above

> **Lallis** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbuiyl6/)
> 
> I was very confused because I personally held the quants in very high regard. And here this guy is saying they are highly regarded. Wow!

> **OverWhelmsKlamm** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtycbu/)
> 
> Haha yes... messed with my parsing way to long into the comment ;) anyways, gonna head back to Wendy's (dumpster) now, those GPUs don't earn themselves :\*

> **zizn** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtqmo7/)
> 
> Did a Linus, did you? Oh wait… lmao

> **vacon04** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtizik/)
> 
> LLM = a bunch of tensors (multidimensional matrices filled with numbers).
> 
> Some of these tensors can be compressed by reducing their precision, without fucking up the model output too much. Some of these tensors, however, are very sensitive, and reducing their precision means they fuck up the model quite dramatically.
> 
> Fancy recipes (Unsloth, ISTA-DASLab, etc) find which tensors can be compressed without fucking the model too much, so they compress those, saving weight while keeping high quality. Tensors that are sensitive are kept in high precision, even if they're heavier. Generic recipes (uniform quantizations) just compress all the tensors the same way, which makes the modes smaller but can also severely reduce their quality.

> **t3rmina1** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtknyc/)
> 
> [r/whoosh](https://www.reddit.com/r/whoosh)

> **vacon04** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtmkoz/)
> 
> Nah, I got the joke, unfortunately I am quite familiar with wsb, there is some real degeneracy there lol. My girlfriend just rolls her eyes when I send her some of the memes that come from that damn sub. Still, I might as well explain how this works for the people that are actually interested.
> 
> LLMs are very interesting but there are so many misconceptions and just misinformation around tjem. If I can help people to understand them a little bit better then why wouldn't I do it.

> **Dany0** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtghrv/)
> 
> ... yes they're highly regarded indeed 🤨

> **KnownAd4832** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtl8v0/)
> 
> Even Swift explicitly released RCO quant just an hour ago… of course they are highly regarded. Their naming is just confusing

> **Choice\_Celery9481** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbt8sjz/)
> 
> you know slop? always claim big and validating everything by vibe-eval XD

> **Chips\_fr\_** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbu0uto/)
> 
> i need to try this

> **sleight42** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcsdia5/)
> 
> Only way to know would be to compute KLD for both... I think?

> **BringTea\_666** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbuzv6v/)
> 
> I used deepseekv4.1 to a bit modify it and now i am running with RTX5090 and 64GB RAM:
> 
> 130t/s with 700k context + vision with Q3 version, 600t/s prefill  
> 160t/s with 900k context + vision with Q2 version, 650t/s prefill
> 
> Insane stuff. Gratz mate. Literally i can run much better model at higher t/s with higher context than Qwen 3.8 27B. (120t/s with 550k context + vision).
> 
> The only downside is prefill which is slow. Around 600t/s vs qwen27b 1kt/s int8 and around 4kt/s for nvfp4.

> **Glittering-Call8746** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbwb5s5/)
> 
> Github repo Pls

> **Glittering-Call8746** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbww3zi/)
> 
> So dual 5090 ? 64gb vram only ? Not single ?

> **Glittering-Call8746** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbwy279/)
> 
> Amazing speeds so this is using Strata right ?

> **BringTea\_666** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbx3vth/)
> 
> yes, Also currently strata does not have cache history. So each new prompt is loading whole prefil. Ask deepseekv4.1 to add it and it will add it no problem. Using it right now with no issues.

> **sleight42** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcpvfgx/)
> 
> So what you're saying is this strata arrangement can work on any moe model so... what... as long as we can fit at least one expert in vram.... ? Just with some tweaks which we can have a smarter model make?

> **KnownAd4832** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pccz6r0/)
> 
> [https://preview.redd.it/7499hk8ja2sh1.jpeg?width=2048&format=pjpg&auto=webp&s=9b7b7a8c42e56d3f42d4f41fec8af4867a40a223](https://preview.redd.it/7499hk8ja2sh1.jpeg?width=2048&format=pjpg&auto=webp&s=9b7b7a8c42e56d3f42d4f41fec8af4867a40a223)
> 
> Strata now comes with easy to navigate UI + many improvements across the board. Enjoy

> **overand** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcqpdmu/)
> 
> I do love the dashboard, but I wish the dash (and log) showed prompt processing speed!

> **MLDataScientist** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcddy27/)
> 
> Thank you! You are doing an amazing job! I can finally run qwen3.8 flash next at 50t/s TG and 500t/s PP on my laptop with 12GB VRAM and 64GB ddr5 RAM on Windows. No other engine reaches this speed. Llama.cpp could only reach 23t/s TG and 100t/s PP with the same quant. So, what you did is a massive upgrade! Thanks!

> **rorowhat** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtc1t6/)
> 
> What do you get if you just use the same quants via llama.cpp?

> **MLDataScientist** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcdah3z/)
> 
> I get 23t/s TG and 100t/a PP with llama.cpp. In comparison, with strata, I get 50t/s TG and 500t/s PP with the same quant on my 12gb VRAM laptop with 64GB ddr5 RAM.

> **Danmoreng** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbv2g7r/)
> 
> You throw away the KV cache for every prompt, makes it pretty terrible for agentic use.

> **MLDataScientist** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcdaows/)
> 
> They fixed it now. KV cache is stays on every turn.

> **sleight42** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcq5xji/)
> 
> Why does this post not have all of the upvotes? We not GPU rich people can now run decent models at decent speed!
> 
> [https://preview.redd.it/7tehm6cd1esh1.jpeg?width=1561&format=pjpg&auto=webp&s=8f2de480d6f0eefaffdc50dd68d9e431ebcf42ab](https://preview.redd.it/7tehm6cd1esh1.jpeg?width=1561&format=pjpg&auto=webp&s=8f2de480d6f0eefaffdc50dd68d9e431ebcf42ab)

> **KnownAd4832** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcqvfux/)
> 
> It seems to good to be true 🤫

> **sleight42** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcsc9a7/)
> 
> Computed the KLDs at these quants? I'm here running 2 bit and it seems... good?

> **brakeline** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtokyb/)
> 
> Does it support tensor parallelism?

> **Prestigious-Act-1577** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pct889o/)
> 
> The model you linked uses Q4 engram table. You can download the Q8 engram for free intelligence.
> 
> [https://huggingface.co/sleepyeldrazi/Qwen3.8-Flash-Next-GSQ-RCO-Q8\_0-PLE-GGUF](https://huggingface.co/sleepyeldrazi/Qwen3.8-Flash-Next-GSQ-RCO-Q8_0-PLE-GGUF)

> **KnownAd4832** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pctav8g/)
> 
> That my friend is a prestigious act indeed. Thanks

> **KnownAd4832** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pca1bch/)
> 
> New GSQ-RCO (IQ3\_S) quant is now also available running at 52tps (should be in same category as BF16 - per their claims).
> 
> P.s: Who is sending me an AMD GPU so I can make them work? (Europe) 🤝

> **Prestigious-Act-1577** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcorztb/)
> 
> Got it to work on a 2070 8gb, after asking MiMo 2.6 Flash to fix the 2000 series support. Runs 3x faster than 3.8 27b!!!
> 
> Anyone interested as of version 0.1.24
> 
> **Now — 0.1.24 base: 2 files changed** (just verified by MD5-hashing all 348 base files: 346 identical, 0 missing):
> 
> 1. [`setup.py`](http://setup.py/) — 4 lines: `<80`→`<75` + "RTX 20 series" message, fail-msg 30→20 series, RAM-gate default `"n"`→`"y" if a.model else "n"`
> 2. `CMakeLists.txt` — 1 line: `LESS 80`→`LESS 75` on the upstream `STRATA_EXPERIMENTAL_SM75` gate

> **ntkgt** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcpdlcm/)
> 
> Exactly. Nowadays, you get better results by having an LLM generate a patch tailored to your specific environment.

> **sn2006gy** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbt6ksu/)
> 
> TPS is always fun, but uh, how does it do with actual work?

> **silenceimpaired** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbt704l/)
> 
> Depends on the work ;) I get a perfect response and 1000 tokens a second if I ask a model with MTP to just type the number 1 over and over again

> **pilibitti** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbwn2o0/)
> 
> that will only make a difference if you are using mtp so you are predicting multiple tokens at once and they are all accepted. without mtp, the task won't make a difference as there is a fixed amount of compute per token.

> **KnownAd4832** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbt75sa/)
> 
> Its consistend and snappy. For 12GB vram i think its better than anything you can run in that size normal way :)

> **sn2006gy** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbt7hbl/)
> 
> well , i mean, i understand your goal - but can it do anything useful at this quantization? can it complete tasks with an actual harness vs hit some perf benchmark?

> **KnownAd4832** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbt7sl6/)
> 
> yes… otherwise I wouldnt spend time and money on Claude+Codex to optimize kernels..

> **Fancy-Snow7** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbz3yak/)
> 
> What do you do differently to llama.cpp that makes it faster. Like what can't whatever you do be built into llama.cpp?

> **MLDataScientist** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcdatjf/)
> 
> Expert caching.

> **Sid3effect** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcdhyfc/)
> 
> Loving the new update Strata-v0.1.8. It built without errors and this time I enabled the Vision model and moved up to the IQ3\_S model. It fits on my system (5080 with 64GB RAM) and I am getting 81.3 tok/s compared to 94.6 tok/s with the smaller build and no Vision. Chat GPT evaluated the output from IQ3\_S as being better so I am going to continue to use it. 80 tok/s is more than I could have hoped for with my single GPU setup using such a large model.
> 
> I really like the changes to the web interface as well.

> **ntkgt** · [2026-09-28](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcl7s0p/)
> 
> I also used Strata 0.1.18. While I think it's excellent, the decoding TPS seems to have dropped by about 20% compared to version 0.1.4?.
> 
> However, the K/V cache now persists, which has sped up the invocation of small tools. That is truly great.

> **Interpause** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcuxf5f/)
> 
> plugged it into vscode copilot cuz i didnt trust the PP and TG numbers i was getting... suffice to say, damn you can get a lot of mileage stacking all the MoE optimization ideas rotting in PRs + using frontier AIs to optimize... qwen 4 flash really is going to change everything i guess

> **danielfrances** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcvuguu/)
> 
> What did you tell the frontier models to do? Did you literally just instruct them to optimize or did you guide them more?

> **Interpause** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcxg203/)
> 
> no im describing what i assumed niko, strata's main author, did

> **circumcised\_hobbit** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtbwge/)
> 
> I might be dumb, but the model is 75GB how are you even loading it? Do you stream it from SSD?

> **KnownAd4832** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtfsko/)
> 
> Model weights are less(written in post), only n-gram table is streamed from SSD.

> **Budkovsky** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtnrm3/)
> 
> Can I run it on 2x RTX 5060Ti 16GB VRAM and 48GB RAM with iQ3\_XXS quants?

> **carteakey** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbv2zxk/)
> 
> dude this is amazing. fine tuned engine targeting specific hardware and specific models. I tried optimizing for my config (very similar except 4070) and managed to get 20 tps. 65 is insane, i will run some tests and report  
> [https://carteakey.dev/blog/running-qwen3-8-flash-next-locally/](https://carteakey.dev/blog/running-qwen3-8-flash-next-locally/)
> 
> Question: are your quants required for running inference or it supports other quants too?

> **carteakey** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pd3x80v/)
> 
> I guess this wasn't snake oil. I am now running 50 tok/s and 2000t/s prefill, too good to be true.

> **laser50** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbzlt9t/)
> 
> God I wish I had upgraded to PCIe 5/64GB RAM when it didn't yet cost me an organ and/or my unborn child.
> 
> I've got 16GB VRAM and 32GB RAM.. If I had some decent uplinks I could use llama-rpc to combine my other pc, but running that over Gbit was just the same as running it on a single PC.

> **Sid3effect** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc66ie0/)
> 
> This is great thank you @[KnownAd4832](https://www.reddit.com/user/KnownAd4832/). I had some issues which I was able to work through and i left notes below. I am still tweaking performance.
> 
> My system is Nvidia 5080 (Gen5x16), X870 Tomahawk, 9800X3D, 64GB 6200MT/s DDR5.
> 
> I am using IQ3\_XXS, 64K context, MTP spec 3, and performance is around 2285 generated in 23754 ms (96.2 tok/s) which is 4x faster than llama cpp.
> 
> Edit - I increased the context and asked it to analyse 2417 lines of YAML and got the below.
> 
> - **Context:** 100,352 tokens
> - **Prompt:** 21,559 tokens
> - **Prompt processing:** **622.7 tok/s**
> - **Generation:** **94.6 tok/s**
> 
> # \`\`\`Strata setup summary
> 
> 1. **Model was downloaded manually and was rejected by the START-HERE.bat**
> 	- The Qwen3.8-Flash-Next **IQ3\_XXS** GGUF files were downloaded manually rather than through the setup script.
> 		- We therefore started Strata with the model location explicitly specified: `START-HERE.bat --model IQ3_XXS --gguf-dir "V:\Strata-main\models\IQ3_XXS"`
> 2. **Fixed** `_paths.py`
> 	- `tools/_paths.py` assumed a deeper directory structure and hit an `IndexError` on our flat Windows checkout.
> 		- We changed the `ENGINE.parents[1]` fallback so it was only evaluated safely inside a `try/except IndexError`.
> 3. **Fixed** `mtp_rt.py`
> 	- `tools/mtp_rt.py` also assumed the repository was nested deeper than ours.
> 		- Changed: `Path(__file__).resolve().parents[3]` → `Path(__file__).resolve().parents[1]`
> 4. **MTP setup**
> 	- The MTP runtime was prepared from the original Qwen checkpoint.
> 		- This produced: `V:\Strata-main\mtp\mtp-q2_0.gguf`
> 		- The `q2_0` setting applies to the **MTP draft/expert pack**, not the main IQ3\_XXS model.
> 5. **Initial VRAM/cache problem**
> 	- `--expert-cache auto` was too aggressive.
> 		- It selected about **5229 slots / 8.48 GB VRAM**, leaving almost no VRAM free — around 0–200 MB depending on the run.
> 		- This contributed to the inference lock-ups/stalls.
> 6. **Explicit expert-cache value**
> 	- We tested:
> 		- `--expert-cache 4000` → about **15.5 GB VRAM**
> 				- `--expert-cache 3500` → about **14.8 GB VRAM**
> 		- **3500 currently appears to give enough headroom and has eliminated the lock-ups.**
> 7. **Worker configuration**
> 	- We also changed the CPU expert-pool configuration to: `--pool-workers 8 --no-host-worker`\`\`\`

> **ntkgt** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcbnxno/)
> 
> Hello. I am using a similar configuration as well.
> 
> I am interested in the MTP settings. If possible, could you share the procedure or the files located under `Strata-main\mtp`?

> **MLDataScientist** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc749ki/)
> 
> this is impressive! I am getting over 50 t/s TG with intel 275HX (no avx512; only avx2), 12GB VRAM (5070ti) and 64GB DDR5 laptop. PP is around 600t/s.

> **nok01101011a** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbt8aga/)
> 
> Interesting, I’m using the same q3 model in lmstudio with just 80ts on my dual5090FE also tried a llama fork yesterday which lead to only 70ts. I’m kind of frustrated when ppl report higher numbers on slower hardware, but I’m just trying to get into the LLM topic. Hope I’ll achieve faster speeds with your fork/engine. Thx

> **DOAMOD** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbv483v/)
> 
> strata serve: 17707 prompt tokens in 19521 ms (907.1 tok/s), 1039 generated in 7780 ms (133.5 tok/s)
> 
> strata serve: 18792 prompt tokens in 20658 ms (909.7 tok/s), 563 generated in 4616 ms (122.0 tok/s)
> 
> strata serve: 19546 prompt tokens in 23398 ms (835.4 tok/s), 162 generated in 1507 ms (107.5 tok/s)
> 
> strata serve: 28694 prompt tokens in 30899 ms (928.7 tok/s), 644 generated in 5094 ms (126.4 tok/s)
> 
> One 5090 crazy but the big problem is that you have to reprocess the cache, so it's not very useful, only for quick chats.

> **Muted-Celebration-47** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbx7bs5/)
> 
> cache hit 0% but we can improve the engine to cache the prompt, right?

> **KnownAd4832** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbt91dn/)
> 
> For your dual5090 I would actually advise you go EXL3 route. Way faster and better for that kind of hardware. As this engine uses specific quant.

> **SomeoneInHisHouse** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtj2bz/)
> 
> How exactly is your inference engine faster than llamacpp?, what's the trick?, the maths ain't "mathing", you can't get 400 PP on 128K with 35 GB of the model layers on slow RAM, even if PP is compute expensive, you either:
> 
> \- move the router requested experts to the GPU and compute the matrices multiplications on GPU (system RAM bandwidth expensive),
> 
> \- or you compute the layers on CPU which is also extremely slow (maybe 64-core Threadripper can give surprising good TP for 35 GB of model weights computations)
> 
> The only way I would trust this numbers is on an octa-channel RAM motherboard

> **KnownAd4832** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtkki1/)
> 
> Llama.cpp is do it for all engine which makes sense why its simple and you can run anything. But if you really want to get your hardware running to max you need optimized kernels and own barebone engine

> **blackal1ce** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pby6u57/)
> 
> This is incredible, first time I've had a model I can run locally that I can throw poorly written prompts at it "gets it". Had to get Codex to fix the install, as it got stuck a few times - but otherwise it's running nicely!
> 
> 4080 16GB + 9950x3d + 96GB of RAM on the IQ3\_XXS model with vision and 128k context.

> **KnownAd4832** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pby7k1q/)
> 
> If I may ask how much tps are you getting and why not 250K context? 👌

> **blackal1ce** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbzloik/)
> 
> Between 40 and 70. 128k context because it felt like enough for what I want to do, and I'd like some ram for other things! This isn't just acting as a server, this is also a machine I'm working on.

> **Subject\_Mix\_8339** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbznt36/)
> 
> How long are you waiting for prompt processing?

> **BringTea\_666** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbthffv/)
> 
> THNAKS mate ! I'll port it to my 5090. I hope i can run this model.

> **DiscipleofDeceit666** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtiqy7/)
> 
> 65tg and 400 prefill is as usable as it gets for that hardware. Nice job!

> **gpt872323** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtlttf/)
> 
> This is amazing. Can you try some benchmarks on accuracy? If this seriously is possible I have a use case for lora. I assume this is MoE model.

> **\_\_Maximum\_\_** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbuoatr/)
> 
> Is this based on llama.cpp or what engine?

> **Enough-Advice-8317** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc09puk/)
> 
> the 600 t/s prefill penalty is where it hurts for agentic loops. if you're flushing the kv cache every step, multi-turn tool calling turns into a crawl real fast regardless of the 65 t/s decode.

> **KnownAd4832** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc0bhyw/)
> 
> Correct. But it is still better than 100 ppts.

> **Icy\_Butterscotch6661** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcbuaj9/)
> 
> Cries in 350 t/s prefill

> **MLDataScientist** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcdbr5h/)
> 
> I see KV cache was fixed. There is no dropping of kv cache anymore

> **XeonG8** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc0ff61/)
> 
> high cpu% usage doing nothing 50% cores just sitting maxed, how to get kv cache not being flushed away? also if the strata folder is at root drive it will have some python errors in the model setup

> **MLDataScientist** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcdbz6g/)
> 
> I see KV cache was fixed. CPU usage was also fixed. There is no dropping of kv cache anymore. Check the latest version on GitHub.

> **Content-Customer-679** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc5ink3/)
> 
> It's just ENORMOUS what you've managed to achieve! I have a mini PC with 4 old used 3060s connected via OCuLink and USB4. With my 12GB 3060 on OCuLink I already reach 27 t/s with the IQ3-XS at 64k context (I didn't think that was possible), and 22 t/s with 256k context. But then I tinkered to make your program compatible with 2 and 4 GPUs (which share USB4 ports — yes, it's far from optimal) and not only does it work, but with 2 GPUs (the OCuLink one + 1 USB4) the throughput actually increased to over 30 t/s (64k ctx)! (With all 4 active the speeds drop back down, but with shared USB4 I wasn't expecting better anyway). So for someone with a similar setup on PCIe it could be even better than with my eGPUs all crammed onto my little mini PC...
> 
> It proves in any case that small configurations can run large models at "okay" speeds for local development.
> 
> BRAVO!!!

> **KnownAd4832** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc5jka6/)
> 
> Engine itself really isnt yet optimized for multi gpu as I dont have capability to test it myself but hopefully soon 👌

> **Content-Customer-679** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc61dil/)
> 
> I can share you my patches for multiple GPUs (with a little cache transfert optimisation bonus) if you want

> **Easy-Try-4414** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc8y889/)
> 
> Thank you for this! The one click install is such a time-saver for me.

> **Lazy-Document4457** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcblv8d/)
> 
> This seems very promising but I always get this warning, anyway to fix this? I’m on windows with a 5070ti and 64GB ram.
> 
> strata generate: \*\*\* WARNING: --expert-cache is enabled and the GPU hit path is NOT CORRECT. The generated tokens diverge from a cache-off run (measured: first difference at token 40 at 2.97% hits, token 0 at 54.4%). Any timing from this run is real; any OUTPUT from it is not. \*\*\* PROFILE, ranked by routing frequency, no eviction.

> **Right-Band3478** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcdtq1a/)
> 
> Strata is amazing
> 
> On my Laptop HP OMEN MAx 16 - RTX5090 24GB Vram i9 ultra 275HX 64 GB Ram - I got 54 token/sec in summarizin a 10k token/s text generation and 600 pp using Qwen3.8 FN Istalab IQ3S
> 
> For reference here are my trials with other stacks with IQ3\_XXS
> 
> \- Unsloth 30 token /s PP  
> \- llamacpp 25 token/s  
> \- exl3 15 token/s  
> \- Free token 12 token/s
> 
> Kudos to creator
> 
> Also results on the summarization are very similar to the other stack
> 
> Edit: the true difference vs other stacks is that both my CPU and my GPU are working above 85%+ at the same time !

> **KnownAd4832** · [2026-09-28](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pckffy1/)
> 
> Run Qwen3.8-Flash-Next-GSQ-RCO-Coder on 32GB of RAM (64GB RAM+VRAM needed for full 265K context)
> 
> 44 tps output / 1,300 ppts - Enjoy coding fast on consumer hardware!
> 
> [https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF)
> 
> [https://github.com/Niko1221/Strata](https://github.com/Niko1221/Strata)

> **\-InformalBanana-** · [2026-09-28](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pclb19z/)
> 
> Are you vibecoding this without any real programming experience cause I noticed you said --host was implemented but in version 0.1.12 it still doesn't work. Had to manually edit the setup.py (edit: had mistakenly written setup.sh instead of setup.py) to set host to 0.0.0.0? Otherwise, your idea is good. Although I personally couldn't get more than 30t/s with swift iq3xxs maybe cause I'm using docker wsl. (Update: with strata 0.1.38 which has its own docker build I'm getting about 80 t/s decode and 1300 t/s prefill) It is amazing that other ppl are getting 50t/s or 60t/s with your app. Pozdrav iz Srbije.

> **KnownAd4832** · [2026-09-28](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcll3l3/)
> 
> E brate hvala puno! A lot of PR’s and Issues were merged together, will be cleaned up later. Now warp speed ahead for better throughput ;)

> **UNO10100f** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcwnkcn/)
> 
> I have 4070 12gb and v100 16gb, and 32gb ddr4, will it be someone alright for me? I get 15.7tps on iq3xxs from unsloth, Im on linux.

> **KnownAd4832** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcz1dbk/)
> 
> Enough :))

> **UNO10100f** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pd5f7uc/)
> 
> So can I run Strata, with v100 and 4070?

> **KnownAd4832** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pd5g6i5/)
> 
> Yes

> **playX281** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcx4r4w/)
> 
> How well will it run with 8GB VRAM and 64GB DDR5? I did get 7-10t/s with regular llama and the quant of ISTA-DASLab

> **Most-Trainer-8876** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcyfwcw/)
> 
> I personally got 5x speed bump. It's literally black magic. Jumping from 7tk/s to straight 50-60tk/s.
> 
> I hope someone does KLD/Logit test, whatever it is called.

> **DarkJanissary** · [2026-09-30](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pd31hzs/)
> 
> Getting 40tk/s on 8GB VRAM and 64GB DDR4

> **Feeling-Bid8885** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pd7c7r2/)
> 
> IQ3\_XXS 8 bit KV, very impressive!
> 
> [https://preview.redd.it/47irtkupwush1.png?width=1904&format=png&auto=webp&s=c8a388db54abd2183b91ac827c4780f223662708](https://preview.redd.it/47irtkupwush1.png?width=1904&format=png&auto=webp&s=c8a388db54abd2183b91ac827c4780f223662708)

> **i-dm** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pde9ny8/)
> 
> Okay, what determines whether you have a higher hit rate or not? I'm kind of averaging between 57 and 63%. Any idea how I can improve that?

> **Sid3effect** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pdf2nva/)
> 
> The hit rate is the experts that were in VRAM when you needed them. The program puts the most popular experts into VRAM and also swaps them out as it learns what you are using so over a session your hit rate should improve. I noticed your VRAM in picture you shared was only 14.6GB out of 19GB. make sure Windows has released your VRAM from WDM before you start strata so that you can get as many experts into VRAM as possible which will improve your hit rate.
> 
> I use a stand alone copy of chrome with hardware acceleration disabled when using local Ai so that it doesn't steal VRAM from Strata.
> 
> If you remove "--open" from run-iq3\_s.bat it won't open the browser on load and you can use a script to start your own browser as an app something like below.
> 
> [u/echo](https://www.reddit.com/u/echo) off
> 
> set CHROME\_PATH=C:\\chrome.exe  
> set URL=[http://127.0.0.1:8080](http://127.0.0.1:8080/)
> 
> start "" "%CHROME\_PATH%" ^  
> \--disable-gpu ^  
> \--disable-software-rasterizer ^  
> \--no-first-run ^  
> \--no-default-browser-check ^  
> \--disable-extensions ^  
> \--disable-infobars ^  
> \--app="%URL%"

> **i-dm** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pdfdcvv/)
> 
> [https://preview.redd.it/byq2wuh5l2th1.png?width=951&format=png&auto=webp&s=96a11f9f8dab321220f4e02af2562a5da0b96ed2](https://preview.redd.it/byq2wuh5l2th1.png?width=951&format=png&auto=webp&s=96a11f9f8dab321220f4e02af2562a5da0b96ed2)
> 
> That's currently how my setup is running.

> **i-dm** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pdaf9il/)
> 
> 128gb ECC DDR5 5600 265k ultra 7, rtx 4000 Ada 20gb (18.5gb usable).
> 
> Should be okay to run this right?

> **king0fsweet** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pdasf4m/)
> 
> Is there a Discord?

> **i-dm** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pddsfpx/)
> 
> Yeah, this would be cool if you had a Discord

> **i-dm** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pdb04p3/)
> 
> [https://preview.redd.it/bf4mfxlytxsh1.png?width=788&format=png&auto=webp&s=f62424bb68b1b57f77f4e2ff6440c385cf8de837](https://preview.redd.it/bf4mfxlytxsh1.png?width=788&format=png&auto=webp&s=f62424bb68b1b57f77f4e2ff6440c385cf8de837)
> 
> Finally nice to be able to use my hardware.
> 
> - Ultra 7 265k
> - RTX 4000 Ada SFF 20GB (HP)
> - 128GB ECC (32 x 4) 5600
> - Dell 1250 FCS, Win 11 Pro

> **i-dm** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pdb07ft/)
> 
> [https://preview.redd.it/dhavmr13uxsh1.png?width=1209&format=png&auto=webp&s=90bf1d05941abdbb05e13c0010955375fd8fac46](https://preview.redd.it/dhavmr13uxsh1.png?width=1209&format=png&auto=webp&s=90bf1d05941abdbb05e13c0010955375fd8fac46)
> 
> Decent enough to get started. Niko this is great!!

> **i-dm** · [2026-10-01](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pdb8hr6/)
> 
> This also solves the question I had about how to heat my room this winter. Now I'll just run models on my machine locally and make use of all that extra heat output. Win-win... 👊🏽

> **i-dm** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pddrb7c/)
> 
> I've noticed that when I use the API, I'm getting around 24 to 28 tokens per second. And when I'm using the browser, the strata local browser chat, I get significantly more, up to 50% more tokens per second. I'm using open code and I'm connecting to the API.

> **tetsuzankou** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pdgrl8m/)
> 
> running on 64gb ddr5 and a 5090... I know not exactly low end but I run AI alongside work and gaming applications so I need the VRAM headroom. This actually allowed me to run 130t/s on a 64k context window
> 
> very impressive and I'll probably use it as my main engine going forward.
> 
> not sure if already being worked on but a way to fine tune the amount of experts loaded to VRAM to better manage VRAM headroom would be the icing on the cake.
> 
> congrats

> **No-Marionberry-772** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbt5pwj/)
> 
> how did you build it?

> **KnownAd4832** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbt60p4/)
> 
> Check GH, there’s a script and a builder to run everything easily.

> **No-Marionberry-772** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbt7vlp/)
> 
> no, i mean how did you code it.

> **KnownAd4832** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbt87mv/)
> 
> Claude+Codex for 7-10 days and testing a lot myself. I did it for my own use and just shared it here anyways

> **Early-Peace-5504** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtehp6/)
> 
> Sorry you’ve had such a response. I will check out your repo on my hardware. Fingers crossed. Sorry about this cess pool of a community. Even if you had messed up, people should discover how instead of just being jerks. Looking at it I find your numbers plausible but I will need to check myself.

> **buttplugs4life4me** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbuueu8/)
> 
> Hey! I feel relevant with my last post on this sub again!
> 
> So its not a fork, that's nice.... I think? The C++ source code keeps referencing a `ref/gdn.py` for example, which doesn't exist in the repo? Maybe it was taken from vLLM or SGLang?
> 
> Ah well, at least ~~you prompted~~ Claude could plan well:
> 
> > The plan is explicit: "experts are dequantized lazily per (layer, expert) - do not materialize 120B parameters"
> 
> With how many different engines now implemented (copied from each other) the "hot experts in your ~~area~~ GPU" concept, I'm at least a little surprised llama.cpp/vLLM/SGLang haven't implemented something similar.
> 
> I couldn't find any online quantisation in your project, so that's nice.
> 
> I like how "you" wrote a Paper about it as well. It's such innovation it definitely deserves one. Especially the fact that you contradict yourself in it, where your Readme says the CPU is handling any experts not cached, the paper says the experts are streamed to the GPU per layer per token batch at first, but later says the experts are computed on the CPU. Which is it?
> 
> It also mentions dequantisation to BF16, while your reference assumes dequantisation to FP32.
> 
> Your benchmark is a 88 tok/sec decode over a 256 token window. That's a little short.
> 
> Your paper mentions loading a 5GB MTP GGUF file into VRAM, but at the same time also only 0.8GB MTP layer in VRAM.
> 
> Your paper lists ~3,25 tok/round, which I assume is the 1 token from the big model plus the 3 drafted tokens put together. That'd be an acceptance rate of ~0.8, which is pretty high for quantised models IMHO.
> 
> Claude concludes enabling EXPO/XMP for your RAM is a nice speed boost and I agree with Claude on that.
> 
> I don't want to diss you too hard, cause the engine seems fine overall, no fork, no weirdo bullshit. But the fact you don't know what logit verification is makes it seem more like you told Claude to build something and it made something good, so really its Claude i should applaud and basically everyone with a Claude subscription can build the same.
> 
> Bonus points: I couldn't find exact copies of the code Claude produced anywhere on GitHub, so I guess it's not a straight copy from someone else.
> 
> Edit: Since the commenter deleted its comment before I could reply: I know I'm on an AI sub. AI is a *force multiplier*. Using it as "Make me something" is bad, using it as "Hey, can you do this specific thing" is good. They've become a lot better at one-shotting stuff, but that doesn't mean their result is always good.

> **trowawayLOL1** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbv00ux/)
> 
> You're on an AI focused subreddit trying to deduct points and remove credit from work because it was coded with AI - so you feel the need to applaud Claude? What? Ridiculous. Okay his paper has write up errors, get over it. You arent that important to hand out pass and fail marks especially when you failed to prove your unbased allegations that it was stolen or something. Weirdo.

> **Inevitable\_Ad\_711** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc4t736/)
> 
> Did you write this with claude?

> **KnownAd4832** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbv0z76/)
> 
> I used Claude for last bit, majority work was done by Astra + Deepseek Flash fyi
> 
> Only deepseek flash: 7B tokens spent on TESTING

> **buttplugs4life4me** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbvobwa/)
> 
> I use 7B tokens for one review round, i would expect there to be more usage in all testing.
> 
> And honestly everything sounds like Claude in there, so idk what the last bit is. There's only one commit as well.

> **KnownAd4832** · [2026-09-28](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcj4js6/)
> 
> To improve Qwen3.8-Flash-Next engine I need:
> 
> \- A person with AMD GPU + at least 40GB RAM  
> \- A person with dual GPU setup + at least 32GB RAM
> 
> All I need is SSH or TeamViewer access for a day on each to pin-test the engine and adapt it for dual gpu’s and amd rocm.
> 
> Please share, if you’re not the one! 🫡

> **tranCe-addiCted** · [2026-09-28](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcknals/)
> 
> I am running an rtx 5080 + an rx 9060xt 16gb, with 64gb ddr5 ram. Would it be good? :)

> **Feeling-Bid8885** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pdd07vt/)
> 
> Hey OP, are you still looking for a dual GPU setup?
> 
> I’m running on a 3090 + 48GB of RAM atm, I can get another 3090 plugged in

> **fallingdowndizzyvr** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtlzjd/)
> 
> Sweet. I'll try it.

> **hk\_modd** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtsezg/)
> 
> Crazy to think that I can run this on my 5070 Ti + 64GB DDR5 notebook and not on my desktop with 4080 16GB because it only has 32GB of RAM.. lol

> **KnownAd4832** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtuqa0/)
> 
> Swift1.5 incoming 👀

> **brakeline** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbv5fwa/)
> 
> Swift has error in packs

> **Desther** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtvsh4/)
> 
> Can you run it with 32gb system ram and 12gb vram? Your github says it needs 48gb ram

> **KnownAd4832** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbtyquh/)
> 
> IQ2\_XS - you need something left for context and kv cache

> **fallingdowndizzyvr** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbuh32d/)
> 
> I'm stuck at.
> 
> "loading the model (the first start takes a minute or two) ..."
> 
> It's been more than a minute or two. It's also churning and burning my machine.
> 
> " load average: 31776.03, 31350.84, 24150.84"

> **SandySkittle** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbuhop0/)
> 
> Please put quantization in title.

> **thestillwind** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbujaqb/)
> 
> Oh that’s interesting

> **Subject-Ad-9934** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbuz2jd/)
> 
> Dang I just tried ssd streaming today with my 4090 and 64gb ram and was getting 200 refill and 7 tokens a second lol using llama.cpp

> **oldshed83** · [2026-09-24](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbvejnk/)
> 
> has anyone perhaps tested on 10gb vram and 32gb ram?

> **Deep-Combination-988** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbw57bs/)
> 
> Tried this UD IQ3 xxs on my rtx 3060 12gb with 40gb ram, it loaded and ran on 8k context but not properly as i realised it's completely using ram to make it freeze but when I switched to Ubuntu, model only loaded in vram, nothing in ram and it was running 10tok/s, with only 8gb vram and remaining everything on SSD with 90k(q8) context. It was using 50% gpu and 50% CPU.

> **KnownAd4832** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbws25g/)
> 
> Try using one lower quant as you need room for kv-cache

> **wisepal\_app** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbx1fdc/)
> 
> it's increadible. i have a laptop with i7-12800h, a4500 rtx 16 gb gpu, 96 gb ddr5 4800h and win 10 os. i got these speeds with swift 1.5 iq3\_xxs and 128k:
> 
> \[strata\] answering: 3736 of max 8192 tokens, 35.5 tok/s, 125 s
> 
> \[strata\] answering: 4277 of max 8192 tokens, 35.5 tok/s, 140 s
> 
> other metrics from txt files:  
> strata-vision: warmed up at 1024 image tokens
> 
> strata generate: expert arena: cudaHostRegister PORTABLE ok; large pages refused (GetLargePageMinimum=2097152, VirtualAlloc error 87 - needs SeLockMemoryPrivilege); using 4 KB pages
> 
> strata generate: loaded 39.97 GiB at 3.35 GiB/s
> 
> strata mtp: draft layer loaded, 949 MiB of VRAM (experts 675, dense 111)
> 
> strata generate: profile D:\\Strata-main\\data\\expert-profile.bin: 8000 ranked pairs, built for 8000 slots
> 
> strata generate: expert cache auto: 8.74 GiB free, 700 MiB reserved -> 3712 slots
> 
> strata generate: expert cache 3703 slots, 6.04 GiB of VRAM; policy is
> 
> strata generate: \*\*\* WARNING: --expert-cache is enabled and the GPU hit path is NOT
> 
> CORRECT. The generated tokens diverge from a cache-off run (measured:
> 
> first difference at token 40 at 2.97% hits, token 0 at 54.4%). Any
> 
> strata generate: pre-filled 3703 of 3703 slots from the profile; slot 0 verified
> 
> strata generate: R4 hit path ON - resident experts are computed on the GPU
> 
> strata generate: 13 expert-pool workers + the host thread
> 
> strata generate: experimental native Q5\_K head, 437043200 bytes
> 
> strata generate: token graph hit path: 3703 resident experts, decided on the device
> 
> strata serve: the prompt path borrows 956 cache slots (1.53 GiB)
> 
> strata mtp: draft head over 40525 tokens (68.0 MiB)
> 
> strata serve: 1257 MiB of VRAM free with everything loaded
> 
> strata serve: 19 prompt tokens in 1590 ms (11.9 tok/s), 1193 generated in 34596 ms (34.5 tok/s)
> 
> strata serve: 2066 prompt tokens in 8267 ms (249.9 tok/s), 3681 generated in 110522 ms (33.3 tok/s)
> 
> strata serve: 4786 prompt tokens in 19741 ms (242.4 tok/s), 6892 generated in 198293 ms (34.8 tok/s)
> 
> strata serve: 9291 prompt tokens in 36375 ms (255.4 tok/s), 2641 generated in 84892 ms (31.1 tok/s)
> 
> system usage:  
> cpu: %100  
> ram around 40 gb i have left 43 gb  
> vram: 14,3/16 dedicated vram
> 
> the problem is, it freezes laptop alot i can barely use laptop when it generates. even biggest quants did not freeze my laptop ever. and it stopped at 4277 token as you see. does not continue. but i have to say never saw these speeds with qwen 3.8 flash next my laptop ever. my top speed was around 16 t/s. how can i solve freeze and generation stop problem?  
> another thing, can we use or adapt it to other models? for example 27b.  
> EDIT: to clean up mess on this post, i pruned some rows.

> **KnownAd4832** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbx50jm/)
> 
> It seems that your CPU has too much usage… can you verify his for me?

> **wisepal\_app** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbx5glc/)
> 
> with the help of chatgpt i solved the problem. it's because of --pool-workers setting in the setup.py. changed to: args = \[ "--pack", str(pack), "--native", str(shards\[0\]), "--ple-gguf", str(ple),
> 
> ```
> "--expert-profile", str(ROOT / "data" / "expert-profile.bin"), "--expert-cache", "auto", "--pool-workers", "8", "--no-host-worker", "--prefill", "2048", "--spec", "4", "--spec-min-p", "0.5", "--mtp", str(rt), "--max-context", str(ctx)
> ```
> 
> \] and added to strata-swift-iq3\_xxs.json this: "--expert-cache", "auto", "--pool-workers", "8", "--no-host-worker", "--prefill", "2048", now it does not freeze. another thing is no speed lost.

> **ntkgt** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc4m1tu/)
> 
> Thank you. Thanks to this message, it's working now. God bless you.

> **Green-Ad-3964** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbxc4ls/)
> 
> What quant can I run on a 32+32? Will it beat 27b q6?

> **Bingeljell** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pbxoccf/)
> 
> Oh nice! I'm wondering if there's a way to port this with similar results on apple silicon. Will look up your repo!

> **blast1987** · [2026-09-25](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc1gvc0/)
> 
> Isn't q4km of qwen3.8-27b better than this? I run qwen3.8-27b on a dual gpu setup, getting 30 toks. I don't understand how you can run a monster like Qwen3.8-flash-next on 12 gb vram . For me it was a pain running the 27b. I will try that on my setup. I have 64gb ram + 12 gb gpu + 16 gb gpu. So total 28 gb vram. But are you sure it is better to have a "normal" quant of the 27b instead of using a "dumb" flash gguf? I mean... Is that flash model at iq3 or iq2 quant smart enough ? I use llm for agent coding with a lot of mcp servers and 256k context.

> **KnownAd4832** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc4fpfv/)
> 
> 27b is dense - you have to have all in your vram. Qwen Flash is MoE, only small portion is in the GPU - rest lies on optimizations with RAM, CPU, SSD

> **snorlaxgangs** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc4z457/)
> 
> This was achieve a while ago, i can even run Q4 K XL 40~50 t/s 100k ctx  
> [https://github.com/GenerelSchwerz/llama.cpp/wiki](https://github.com/GenerelSchwerz/llama.cpp/wiki)

> **wisepal\_app** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc54o7r/)
> 
> With which system are you talking about? And with which fork?

> **snorlaxgangs** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcan1ld/)
> 
> My bad.  
> 5080 96GB Qwen next Q4 K XL.  
> moe-expert-cache-size 48. No MTP.  
> U probably can do q3  
> my config:  
> #!/usr/bin/env bash
> 
> set -euo pipefail
> 
> BIN=/home/anon/llama-generel/build/bin
> 
> M=/home/anon/Models/Qwen3.8-27B
> 
> export CUDA\_VISIBLE\_DEVICES=0
> 
> export LD\_LIBRARY\_PATH="$BIN:${LD\_LIBRARY\_PATH:-}"
> 
> cd "$BIN"
> 
> ./llama-server --offline \\
> 
> \-m "$M/Qwen3.8-Flash-Next-UD-Q4\_K\_XL-00001-of-00004.gguf" \\
> 
> \-c 105000 -b 512 -ub 512 -np 1 \\
> 
> \-ngl all -fa on \\
> 
> \--load-mode none --lazy-mode on \\
> 
> \--moe-expert-cache-size 48 --moe-early-router \\
> 
> \-ctk q8\_0 -ctv q8\_0 \\
> 
> \--cache-ram 0 --jinja --no-warmup \\
> 
> \--decode-overlap --decode-boundary-overlap \\
> 
> \--ple-prefetch --phase-aware-workspace --live-context-workspace \\
> 
> \--reasoning on --reasoning-preserve \\
> 
> \--temp 1.0 --top-k 20 --top-p 0.95 --min-p 0.0 --presence-penalty 0.0 --repeat-penalty 1.05 \\
> 
> \--threads 8 \\
> 
> \--host [127.0.0.1](http://127.0.0.1/) --port 9191 --metrics

> **MLDataScientist** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc7p33m/)
> 
> yes, very important part of your message is missing: what system GPU/RAM/CPU are you using?
> 
> I tried generel's fork but I could not get more than 23t/s TG. Meanwhile, strata on my laptop reaches 50t/s for the same quant. 12GB VRAM + 64GB RAM DDR5, intel 275HX

> **alex\_bit\_** · [2026-09-26](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc9btoq/)
> 
> Is it possible to use more than one GPU?

> **KnownAd4832** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pc9yju8/)
> 
> Not yet, a bit more to wait 🙏

> **Normal\_Guard\_8207** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcbpa1d/)
> 
> No Qwen flash next uncensored/abliterated/heretic GSQ-RCO GGUF :(

> **patricio272** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcbry6s/)
> 
> Nice, have you tried tabbyAPI ? I got dense Qwen 3.8 27B Q3 running at 80 t/s
> 
> RTX 4080 32 GB RAM i7 13th Gen

> · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcd5mkn/)
> 
> \[deleted\]

> **KnownAd4832** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcd66dm/)
> 
> Because of context length it reserves vram for kv cache…

> **PestiferousGamer** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcfdzqi/)
> 
> rtx 3060 12gb, 48gb ddr4 ram, hitting crazy speeds at 64k context rn.
> 
> [https://preview.redd.it/c2rzlrr954sh1.png?width=900&format=png&auto=webp&s=eb282ad2f0512fb76d0ba3b0d8fb0ad6d3108b44](https://preview.redd.it/c2rzlrr954sh1.png?width=900&format=png&auto=webp&s=eb282ad2f0512fb76d0ba3b0d8fb0ad6d3108b44)

> **XeonG8** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcfhio6/)
> 
> in 2 days this project has improved much

> **Evildude42** · [2026-09-27](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcgr9xu/)
> 
> So how are people doing this and what is the output complete gibberish?

> **KnownAd4832** · [2026-09-28](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcj4t4v/)
> 
> See it for yourself ;)

> **UltraFOV** · [2026-09-28](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pch7ido/)
> 
> Maybe I will try it on my Unicorn laptop (Acer ConceptD 9 Pro) with the RTX 5000 and 32GB ram

> **Oleszykyt** · [2026-09-28](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcisg0n/)
> 
> What about context length though?

> **rrrrex** · [2026-09-28](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pckfn1a/)
> 
> [https://preview.redd.it/b72spanqc9sh1.png?width=2144&format=png&auto=webp&s=002e8fc0526fbc212095a03e5d6363a989fd67b7](https://preview.redd.it/b72spanqc9sh1.png?width=2144&format=png&auto=webp&s=002e8fc0526fbc212095a03e5d6363a989fd67b7)
> 
> Does it duplicate weights? Total VRAM is already contains all weights (iq2\_xs), 15.3 GB (GPU VRAM) + 23 GB (shared VRAM), meanwhile strata.exe takes extra 36 GB.

> **rrrrex** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcq5nuo/)
> 
> @[KnownAd4832](https://www.reddit.com/user/KnownAd4832/) the same behavior with the latest engine  
> does it mean that it's impossible to load model bigger than VRAM+Shared VRAM budget?

> **ductoan266** · [2026-09-28](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcknoqr/)
> 
> Specs
> 
> - OS: Omarchy / Arch Linux
> - CPU: Xeon E5-2696 v3 — 18 cores / 36 threads, AVX2
> - RAM: 128 GB DDR3
> - GPU used by Strata: RTX 3080 20 GB, 240 W power limit
> - Other GPUs: 2× Tesla V100 SXM2 16 GB
> - Storage: Fanxiang S500Pro 512 GB NVMe
> - Driver / CUDA: NVIDIA 580.178.04 / CUDA 12.8
> - Model: Qwen3.8-Flash-Next 125B MoE Q2\_0
> - Engine: Strata 0.1.14
> - Context: 262K, int8 KV with 32K resident in VRAM
> - Vision: GPU BF16 encoder enabled
> - Expert cache: 9,458 experts / 12,469 MiB
> - VRAM usage: 19,435 / 20,480 MiB
> 
> Performance
> 
> - 100K-token prefill: 1,014 tok/s — 99.2 seconds
> - Before Strata 0.1.14: 609 tok/s — 165.3 seconds
> - Upgrade improvement: 1.67×
> - Decode: approximately 40–60 tok/s
> - 100K-context decode: 58.3 tok/s
> - 3.4K-context decode: 45.6 tok/s
> - 100K retrieval test: 8/8 correct
> - Vision test: 478-token image prompt processed in ~2.3 seconds; OCR values 2/2 correct
> - Vision overhead: ~3% lower text-prefill speed and ~1,058 fewer resident experts

> **Most-Trainer-8876** · [2026-09-28](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcmk288/)
> 
> WOAAAH, I cannot believe my eyes.
> 
> Btw I got 5070ti + 5060ti Dual GPU + 64GB ram (It's DDR4 tho)  
> So combined is 96 GB memory. obviously Windows uses some of the pie so... Can I run it? Utilize both GPU??

> **KnownAd4832** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcqvxzo/)
> 
> Yes

> **orangeswim** · [2026-09-28](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcnt68z/)
> 
> Based on my early testing, it seems feasible for low context needs on my setup.  
> I haven't done too much checking on result quality. But what I do check is recall ability.  
> For my setup below I'm running tests from another PC -> 3090 machine via ssh + llm api.
> 
> Strata on a 32 GB RAM / RTX 3090 box — Qwen3.8-Flash-Next 125B Coder IQ1\_M
> 
> Hardware
> 
> \- GPU: NVIDIA GeForce RTX 3090 24 GB (sm\_86), driver 596.36  
> \- CPU: AMD Ryzen 7 5800X (8 cores / 16 threads)  
> \- RAM: 32 GB DDR4-3200 (4×8 GB, dual channel)  
> \- Storage: model on SSD  
> \- OS: Windows 11
> 
> Setup
> 
> \- Strata engine v0.1.18 (prebuilt, CUDA 13.0)  
> \- Model: Qwen3.8-Flash-Next Coder IQ1\_M (ISTA-DASLab GSQ-RCO, 256/512 experts kept), context 131,072, int8 KV, no vision encoder  
> \- Install: START-HERE.bat --family coder --model IQ1\_M --context 131072 --vision no --yes  
> \- Load: experts → RAM 23.42 GiB in 86 s; GPU expert cache 7,982 experts / 15.19 GiB  
> \- Steady state: 23.8/24.5 GB VRAM · ~0.5 GB free RAM · strata.exe commit 49.6 GB (pagefile absorbs it)  
> \- Nothing else runs alongside on this box; 131k is the context ceiling at 32 GB RAM (262k needs 64 GB; setup auto-caps)
> 
> Measured results (119k-token prompts, ~370 KB wiki haystack)
> 
> \- Cold prefill: ~1,170 tok/s (118,751 tokens in ~104 s; 104–105 s on every run)  
> \- Decode @ 119k ctx: ~75 tok/s with thinking off · ~29 tok/s with thinking on · ~90–100 tok/s at short context  
> \- Prompt cache: full 118k re-request in 1.9 s  
> \- 26-needle retrieval @ 118.8k (temp 0, thinking off), 12 seeds: 3× 26/26, 5× 25/26, one 24/26, one 23/26 → 300/312 needles (96.2%)  
> \- Misses scattered across mid-document depths, no consistent positional pattern; missed keys were omitted, never hallucinated  
> \- Follow-up fact-check: CORRECT on all 12 runs  
> \- Output discipline: valid JSON in the exact requested format every time  
> \- One cold-start quirk: the first long request after load page-thrashed (~4 tok/s) while Windows settled the working set; the identical warm request ran 16× faster
> 
> Context ceiling — capability comparison on this same machine
> 
> \- Strata Coder (125B): max 131k context on 32 GB RAM  
> \- Our llama.cpp setup — Swift-Qwen3.8-27B Q4\_ context (verified 26/26 needles @ 197.9k, ~44t/s decode)  
> \- The two are mutually exclusive on this hardware (RAM); we switch between them per workload  
> \- llama.cpp baseline @ 100k: 894 tok/s prefiller is +31% prefill / +38% decode at 4.6× theparameter count, at the cost of the context ceiling

> **sleight42** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcpulog/)
> 
> Ok. I love you. 3090 here and happy.

> **ntkgt** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcri4j0/)
> 
> I used version 0.1.21 on Ubuntu. The calibration feature is very convenient.
> 
> I also tested the SM75 support (PR#87). When building with SM75 on Ubuntu, I had to manually apply the following diff to `setup.py`, build completes successfully and is usable, but I am unsure if this is the correct procedure.
> 
> ```
> diff --git a/setup.py b/setup.py index 6c1bc4d..7ceed2e 100644 --- a/setup.py +++ b/setup.py @@ -284,7 +284,7 @@ def cc(g) -> str: def gpu_problem(g, together=False): """Why Strata cannot use this card, in plain words (None: it can).""" - if int(g["arch"]) < 80: + if int(g["arch"]) < 75: return (f"not supported - older than the RTX 30 series (compute capability {cc(g)}; Strata needs 8.0 or " "newer)") if together and g["vram_gb"] < SPLIT_MIN_VRAM_GB - 0.5: @@ -813,6 +813,7 @@ def cmake_build(src, bdir, target, defs, vcvars, bat_name): if cmake is None or ninja is None: fail("cmake / ninja not found after installing them", "run: .venv python -m pip install cmake ninja") conf = [cmake, "-G", "Ninja", f"-DCMAKE_MAKE_PROGRAM={ninja}", "-S", str(src), "-B", str(bdir), + "-DSTRATA_EXPERIMENTAL_SM75=ON", "-DCMAKE_BUILD_TYPE=Release", *defs] build = [cmake, "--build", str(bdir), "--target", target, "-j", str(max(2, (os.cpu_count() or 4) // 2))] # A failed build is tried once more: CUDA 13.0's ptxas now and then fails to parse a PTX file it just wrote, and
> ```

> **\_ggsa** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcrioky/)
> 
> really impressive numbers. do the 37.6–47GB minimums include the full 128K KV cache, or only the model and runtime? for comparison, DS4 Q4 at 262K on my 96GB M3 Ultra plans 80GB while streaming the 95GB n-gram table from SSD, so i’m curious how much of the gap is context vs quantization

> **CraftyEmployee181** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pcsy6p4/)
> 
> AMD gpu?  
> I have a 12gb amd gpu + 8gb nvidia gpu.  
> I combine them with layer splitting currently with llama.cpp
> 
> I I’ll your tool work with this type of vulkan splitting?

> **KnownAd4832** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pctaxma/)
> 
> In 1h

> **MLGcannon5000** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pctnj6l/)
> 
> Would you be open to me opening a PR into Strata allowing for permanent allocation of some experts into VRAM, with a launch flag?  
> Implementation would be that the top x% of experts by usage (adjustable by config) do not sit in RAM at all and are permanently in VRAM. Currently they are being copied over from RAM and kept resident in VRAM, duplicating some amount of memory footprint. `data/expert-profile.bin` already has the expert ranking, though I understand things like prefill borrowing cache slots would need adjusting too. This could be very beneficial for certain types of systems such as mine (32GB VRAM but only 48GB system RAM).  
> Would you be interested in something like this?

> **KnownAd4832** · [2026-09-29](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pctz77k/)
> 
> Open a PR

> **Wrong\_Wind\_1806** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wp7zyb/qwen38flashnext_on_12gb_vram_65_tokens_per_second/pdf3shq/)
> 
> I tested it on a rtx 2060 12Gb vram and 48Gb ram, model qwen-3.8 flash next IQ2\_XS and the result on a simple question is:
> 
> \* Speed:
> 
> generation avg. 4.9 tps (max 6.5) and pp 12 tps.
> 
> \* Resources used:
> 
> gpu load 49%, cpu load 25 %, disk read 0,3 Mb/s, PCIE Gen3 x8
> 
> Any way to improve its speed via configuration?
