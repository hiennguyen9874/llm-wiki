---
title: "Strata on a power limited 5090 and 96GB of DDR5-6400 is cranking out 150-200 tok/s decode and 5-6k prefill! Qwen3.8-Flash-Next at IQ3_S, CTX at 128k tokens (8-bit)."
author: "z0_o6"
site: "r/LocalLLaMA"
source: "https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/"
domain: "reddit.com"
language: "en"
description: "submitted by /u/z0_o6 [link] [comments]"
word_count: 5456
---

| [![Strata on a power limited 5090 and 96GB of DDR5-6400 is cranking out 150-200 tok/s decode and 5-6k prefill! Qwen3.8-Flash-Next at IQ3_S, CTX at 128k tokens (8-bit).](assets/hmr77h6in2th1.png "Strata on a power limited 5090 and 96GB of DDR5-6400 is cranking out 150-200 tok/s decode and 5-6k prefill! Qwen3.8-Flash-Next at IQ3_S, CTX at 128k tokens (8-bit).")](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/) | submitted by [/u/z0\_o6](https://www.reddit.com/user/z0_o6)   [\[link\]](https://i.redd.it/hmr77h6in2th1.png) [\[comments\]](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/) |
| --- | --- |

---

## Comments

> **giveen** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfjh5o/)
> 
> Strata's work is something I have been following for design ideas for my own engine. While I use nvfp4 for my serving of Qwen3.8-Flash, I've been very impressed with their speed.

> **z0\_o6** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfkm92/)
> 
> I'm blown away by the speed. I also downloaded UD-Q4\_K\_XL to do some quality comparisons, as well as seeing if I can run the Unsloth weights in Strata successfully, and comparing with QwFNfer, BeeLlama and mainline llama.cpp.

> **veigatmv** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg3m1u/)
> 
> I managed to have UD working on strata, thats what i'm running at the moment.  
> I was using it with Exllmav3 and i just asked claude to set it up, since I had the weights he got it working.

> **z0\_o6** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg41s6/)
> 
> When you used UD weights, were there any hiccups to overcome?

> **veigatmv** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg85e2/)
> 
> My agents do reports after doing any changes I just pasted them over to Claude and had him draft this reply:
> 
> A few, nothing blocking:
> 
> - The UD GGUF doesn't ship the MTP head in the form Strata wants, so I pulled the official MTP tensors separately and packed them for spec decoding.
> - Every boot prints a big "GPU hit path is NOT CORRECT" warning. That's stale text from an older non-native kernel; upstream already replaced it (closed issue #23). Outputs matched llama.cpp 64/64 on top-1 for me.
> - Don't use --max-context 262144. It loads fine, then every request hangs silently (qsa\_block\_topk: unsupported geometry or cap in the log). 262136 is the max that works, by literally 8 tokens.
> - \--expert-cache auto eats VRAM down to ~700 MiB free, so I added --vram-reserve-mib 1600 to get headroom for vision.
> - On a 3090 + 5090 setup, putting the 3090 as main and the 5090 as the expert tier was noticeably faster than the reverse.
> - Mainline llama.cpp won't load these weights (unknown arch), so for your comparison you'll need Unsloth's build.
> 
> Once sorted, I get ~80–100 tok/s decode and ~2.6k tok/s prefill, vs ~29 / ~285 on llama.cpp and ~32 / ~1.3k on EXL3. It also needs ~74 GB of RAM pinned while loaded, so keep that in mind.

> **source-drifter** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfr12z/)
> 
> oh let us know if you do please. i'm also curious

> **z0\_o6** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg1zsi/)
> 
> Is there anything in particular you want to see? It's worth me asking now while I'm still putting shit together. :)

> **fallingdowndizzyvr** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg60ss/)
> 
> > I also downloaded UD-Q4\_K\_XL to do some quality comparisons, as well as seeing if I can run the Unsloth weights in Strata successfully
> 
> What speed do you get with Q4\_K\_XL?

> **MarrusAstarte** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdgwf5x/)
> 
> For a modified "pelican svg" prompt, I got ~60 tok/s decode and 2000 tok/s prefill. rtx 5090, 128GB ram, and 256k context.
> 
> Context size limits how many experts can fit in vram, so higher context would run slower.

> **kansasmanjar0** · [2026-10-04](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdqzjl0/)
> 
> I got 25 tok/s decode 700 tok/s prefill.
> 
> `  Model and engine Model qwen3.8-flash-next-unsloth-ud-q4_k_xl Engine v0.1.38 Context 262,144 tokens KV cache 8-bit, streamed: 32,768 positions per layer in VRAM, the rest in RAM Experts in VRAM 8,765 (25.6 GB) Speculation MTP drafts up to 3 tokens, prompt lookup on Images on This PC GPU NVIDIA GeForce RTX 4090 + NVIDIA GeForce RTX 5060 Ti, 40 GB CPU 12th Gen Intel(R) Core(TM) i7-12700K, 20 threads RAM 94 GB  `

> **pmttyji** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdgz8bn/)
> 
> [u/giveen](https://www.reddit.com/u/giveen) Yesterday [I asked the creator about possibility](https://www.reddit.com/r/LocalLLM/comments/1wu6fka/comment/pd1g2sa/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button) of Qwen3.6-35B-A3B or other medium size MOEs on Strata since Qwen3.8-Flash-Next is too big for (low bandwidth) 8GB VRAM(like 4060) + 32GB RAM.
> 
> It would be awesome to get all other models working on Strata. Any cherry picks possible from Strata for models like Qwen3.6-35B-A3B?

> **giveen** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdgzj75/)
> 
> Ninfer (and ninfer-ext , my fork) already support Qwen3.6-35B-A3B
> 
> [https://github.com/Neroued/ninfer](https://github.com/Neroued/ninfer)
> 
> [https://github.com/giveen/ninfer-ext](https://github.com/giveen/ninfer-ext)

> **pmttyji** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdh2o6i/)
> 
> But I have only 8GB VRAM(4060) + 32GB RAM.
> 
> Though I see some folks running Strata just with same config(while RAM is 64/80GB), it's not enough for my config due to low bandwidth of 4060. I know it's too much expectation for my config.
> 
> That's why I thought about Qwen3.6-35B-A3B with Strata. Qwen3.6-35B-A3B is 1/5 size of Qwen3.8-Flash-Next so we could expect better t/s. Someone is getting 40 t/s just with 8GB VRAM + 64GB RAM(For Q2 of Qwen3.8-Flash-Next). Imagine what Qwen3.6-35B-A3B could give on Strata

> **giveen** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdh383h/)
> 
> Unfortunately, my focus has been around my hardware, as I cannot reliably test anything below that.

> **pmttyji** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdh6w86/)
> 
> That's OK, Focus on yours & make it more stronger. Occasionally I checked Github for ninfer (4060) forks, but nothing happened yet :D It won't happen as the model size is bigger than VRAM even at Q3/Q4 so.
> 
> So recently I keep looking for Strata forks(for other models).

> **goomba870** · [2026-10-04](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdpuqcl/)
> 
> I’m somewhat new here. Does your -ext fork do essentially what Strata does? I run a 5090 and 64GB system ram and ninfer is my daily driver. Curious if finding ways to run bigger models cleverly would be a notable improvement.

> **giveen** · [2026-10-04](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdpw78c/)
> 
> They are similar in many functions, but ninfer (and my fork ninfer-ext) are exclusively focused around the 5090.
> 
> I am finishing up work on a supporting a 96Gb exl3 quant of Qwen3.8-Flash.
> 
> I highly recommend you try Strata and mine. Strata has done some amazing work.

> **Educational-Region98** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdm8ym6/)
> 
> It's definitely possible in theory. Maybe you can make your own?

> **pmttyji** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdmaooo/)
> 
> I don't know C++/C. Otherwise I would've made a fork already.

> **leonbollerup** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfnb5z/)
> 
> Strata is damn nice

> **MindfulMan1984** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfnsch/)
> 
> I can confirm Strata is legit. I tested it on a 24GB VRAM GPU and 128 GB of system RAM, and it flies on my computer. It has a neat setup script that detects your system and runs a "calibration" to squeeze out the most it can; the NVMe SSD (must have) + GPU + CPU combo is well optimized. Very pleasant for quick, responsive agentic sessions. I have not tested it on whole-repository coding yet; let's see how it goes.

> **brownenclave84** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdhewsl/)
> 
> if you have 128gb you can try and put the n-gram (25gb) in cpu ram. so not using the ssd at all --ple-io "ram"

> **MindfulMan1984** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdi4rb9/)
> 
> Thanks for the tip, I will definitely try that.

> **OtherAppointment900** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg0b0v/)
> 
> dual 3080 20g + 64g ddr4(2888)
> 
> [https://preview.redd.it/j8swe43p23th1.jpeg?width=4096&format=pjpg&auto=webp&s=5b0020394d1065e04f91e3f05a0659c9941fbd50](https://preview.redd.it/j8swe43p23th1.jpeg?width=4096&format=pjpg&auto=webp&s=5b0020394d1065e04f91e3f05a0659c9941fbd50)

> **LearnNTeachNLove** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfo6le/)
> 
> And quality wise? How does it perform? i suppose speed token/s is not the only indicator.

> **DeProgrammer99** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg9bzv/)
> 
> I've been running Strata and that GSQ RCO quant from ISTA for a day or so on my 7900 XTX working on new features for my game. It's hard to spot quality differences with any level of rigor, so all I can say is that my impression is it does a similar quality job to Qwen3.8-27B-Q6\_K in a shorter time, using ~14 GB less VRAM (since it doesn't do heterogeneous GPUs) and looping less and ironically using more power (my watt meter shows a 550W peak, while with both GPUs in llama.cpp, the peak was closer to 450W).

> **TerminalNoop** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdhyfes/)
> 
> how much RAM do you have and what is your performance with a unsloth Q4 quant?
> 
> I'm not sure if i'm mental or not considering upgrading ram, but it better be worth it. However there are not many reports about speed with a 7900xtx, and it should make sense to upgrade over qwen3.8 27B.

> **DeProgrammer99** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdhzb31/)
> 
> 64 GB RAM (about 3/4 in use), but it frequently says the expert cache hit rate is 97%. Also running at 128k context.
> 
> I haven't tried a Q4 quant. Didn't really want to since it's significantly bigger than my total RAM + VRAM. The GSQ RCO quant is *half* the size.
> 
> This is right before Pi compacted at 90% context usage:
> 
> [https://preview.redd.it/rmi3vxhil4th1.png?width=820&format=png&auto=webp&s=fab2265a04df12845a66b6661adb6c5f01c17d57](https://preview.redd.it/rmi3vxhil4th1.png?width=820&format=png&auto=webp&s=fab2265a04df12845a66b6661adb6c5f01c17d57)

> **TerminalNoop** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdmhww9/)
> 
> Thank you for your reply :)  
> Hmm so maybe about 30-50 tk/s with a q4 quant 🤔
> 
> I was considering 4x24gb so the q4 quant should fit according to my quick maths. (96gb + 24gb vram and the look up table on the SSD.)

> **z0\_o6** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfp6t6/)
> 
> I just got it up and running late last night; I am working on doing a quality comparison of some sort. Do you have any recommendations?

> **LearnNTeachNLove** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdh8nqd/)
> 
> I do not have special recommendations apart from what i read for the models: qwen 3.8 27B, flash or swift versions, gemma4, deepseek. I am also looking for a relevant benchmarking tool from quality/prompt-answer relevance point of view.

> **veigatmv** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg0opo/)
> 
> I'm having a blast with strata - 5090 + 3090 and 128gb RAM.  
> 100tp/s 2600 PP  
> Qwen 3.8 FN UD Q4 K XL full context + vision

> **fallingdowndizzyvr** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdgp3s1/)
> 
> > Qwen 3.8 FN UD Q4 K XL full context + vision
> 
> You're getting "100tp/s" with Q4 K XL? Dev gets "7-8.5 tok/s (6 runs: 6.7-8.6, mean 7.9)".

> **veigatmv** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdhe8sq/)
> 
> Running it with Deepseek harness atm.  
> I was happy with Exllamav3 at 30-40 t/s and about 1200 PP, completely amazed with Strata
> 
> [https://preview.redd.it/83k39i3a44th1.png?width=2548&format=png&auto=webp&s=ddf7bc4de9ddeca5d65ba48f386ac3228a3674b0](https://preview.redd.it/83k39i3a44th1.png?width=2548&format=png&auto=webp&s=ddf7bc4de9ddeca5d65ba48f386ac3228a3674b0)

> **Hotcooler** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdgwygm/)
> 
> Dev's hardware is 12gb vram + 64 ram. So that's 7 token/s streaming from an SSD. Which is... impressive actually.

> **fallingdowndizzyvr** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdgyj6f/)
> 
> But that was also case with IQ3 too. Steaming from SSD is one of the wins for Strata.

> **Hotcooler** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdgz4tv/)
> 
> It is. I just explain why it's 7-8tok/s. Since it's SSD streaming the **experts** on that setup. With 96GB+ it'll be probably 50+.

> **fallingdowndizzyvr** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdhmhyv/)
> 
> > With 96GB+ it'll be probably 50+.
> 
> Not quite. Unless you are just asking to print red over and over again to get draft hits. I just ran it on my machine with 128GB of RAM and a 5070ti. I get between high 30's and low 40's. ~~The PP is the highest I've gotten so far though, about 769t/s~~. Strike that. It started at 769 but now it's down to 454t/s which is pretty much what I always get. I never see those high PPs that other people like OP get.

> **shard746** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdmf9fq/)
> 
> I have a 3090 and 96GB DDR4, and with UD-Q4\_K\_XL I get about a 1000 prefill even at 200k+ context with it. That's with real project work, not synthetic tests. Maybe you missed something during setup?

> **fallingdowndizzyvr** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdnupdy/)
> 
> > Maybe you missed something during setup?
> 
> I downloaded the new master and ran through setup again last night. Now I get 1000 with one 5070ti. I get 2000 with two 5070tis. So I guess something got fixed for my setups.
> 
> [https://www.reddit.com/r/LocalLLM/comments/1wwb5bl/strata\_is\_seriously\_impressive\_running\_qwen\_38/pdjpw80/](https://www.reddit.com/r/LocalLLM/comments/1wwb5bl/strata_is_seriously_impressive_running_qwen_38/pdjpw80/)
> 
> But even 1000 seems a little light compared to other numbers people have been getting, including the Strata dev. Which has slower hardware than I'm using.

> **Hotcooler** · [2026-10-04](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdskwar/)
> 
> I also tried 4090 with 96 DDR5 under windows though, (with 75gb budget and 2gb vram reserve) it gets about 1400 prefill at 128k and about 50-60ish TG.

> **veigatmv** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdhekst/)
> 
> Strata pins all the experts to RAM, at least in my config + I have 56gb of VRAM

> **Hotcooler** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdhfz3z/)
> 
> Great. Happy for you. But it can stream them from the SSD for when the model weights are larger than your ram+vram. Just the experts for Q4 are like 77GB. And for the case described above, it's the only way to run it.

> **cosmicnag** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdhh37l/)
> 
> Can it do multi gpu now?

> **veigatmv** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdhmq0g/)
> 
> Yes.
> 
> The eddoursul Strata fork I'm on uses the second card as an expert tier instead.
> 
> One non-obvious thing: the slower/smaller card should be the main GPU and the bigger one the expert tier. I benchmarked both ways and 3090-main was 15-30% faster across code/prose/summary — the extra VRAM does more good holding experts than running the model. Worth testing for yourself though.

> **cosmicnag** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdo58uh/)
> 
> Thanks for addressing that. My other concern was support for parallel sessions. Can it run more than one session/slot at the same time? If so, does aggregate decode hold up?

> **veigatmv** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdo5xrs/)
> 
> No concurrency unfortunately..

> **Iory1998** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdhjfep/)
> 
> How did you get it working? Doesn't strata only supports ISTA's models?

> **veigatmv** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdhm1q2/)
> 
> Upstream Strata, yes.
> 
> I'm running eddoursul's fork (branch \`custom\`), which adds K-quant expert kernels. That's what lets it load Unsloth's UD-Q4\_K\_XL directly — no conversion, use the GGUF as is. It also treats a second GPU as an expert tier rather than doing a layer split.
> 
> There's an open PR against upstream, so it may land there eventually.

> **Pwc9Z** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfrjcb/)
> 
> That is a nice beefy PC build.
> 
> WHY DOESN'T MINE LOOK LIKE THAT

> **z0\_o6** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg2whk/)
> 
> I think context is important, and a good pun for the subreddit. I *happened* to buy this setup in October of '25 for a whole bunch of reasons, none of which were AI. I built this to be a long-term racing sim and got myself on a bit of a tangent. I was lucky, not smart.

> **trying4k** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdful7z/)
> 
> That is incredibly fast. I've been trying to find a new inference engine for larger moes, since llama.cpp is slow for offloading.
> 
> I'm curious how it compares to FreeToken. I feel like when the two align they may be roughly similar:
> 
> - FreeToken lacks MTP and runs nvfp4 (~q4)
> - Strata runs at most Q3 and has MTP
> 
> I haven't tested both (yet) but FreeToken [suggests 65t/s](https://github.com/FlashML-org/FreeToken/pull/257) without MTP.
> 
> Any numbers on Strata without MTP to get a closer apples to apples comparison?

> **Hotcooler** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdgynwa/)
> 
> Strata does run unsloth Q4 if you have the ram. It can stream from SSD too, but I did not try that. I used to get about 60t/s with characters that mtp did not predict at that point in time (was fixed couple days ago) on 4070ti super + 64gb DDR4 on 14700 under linux. IQ3. With MTP working averages at about 80ish for "story" and up to 120 for "code". Generally averages out to about 90ish.

> **Gold\_Coconut9777** · [2026-10-04](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdqqkwq/)
> 
> What context size and KV type are you using?

> **Hotcooler** · [2026-10-04](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdsbqaa/)
> 
> Kv8, streaming 262K (32k in VRAM, rest streams in from ram).

> **Distinct-Pie2389** · [2026-10-04](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdqf9ur/)
> 
> You’ll be seeing a huge benefit here soon.
> 
> K8v4 PR just pushed so once that merges, top line and bottom are good.
> 
> I’m running IQ2\_XS @ 262k CTX

> **rorowhat** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfmgwx/)
> 
> Strata?

> **z0\_o6** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfneqs/)
> 
> [https://github.com/Niko1221/Strata](https://github.com/Niko1221/Strata)
> 
> I am not affiliated, just using it and impressed.

> **rorowhat** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfo1uj/)
> 
> Oh they just quantize very low and remove experts, or is there more to it?

> **karmaisnonsense** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg1mrw/)
> 
> I think it originally targeted low memory machines but the benefits transfer to higher quants and bigger machines too. Expert caching, autofit to VRAM, kernel optimizations, working MTP etc.

> **MindfulMan1984** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg6o82/)
> 
> Yes, I also tested it on a higher-end GPU, and the setup script's --calibrate flag fitted the engine to squeeze performance out of it. Quite impressive.

> **karmaisnonsense** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdhqnz5/)
> 
> Also dynamic prefill batch size and KV streaming. Really crazy how well leaving settings to auto works.

> **Corosus** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfwui0/)
> 
> expert caching on vram done right, and some other magic improvements

> **MindfulMan1984** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg6feg/)
> 
> No removal of experts; the setup script guides you, but you can choose to download [Qwen3.8-Flash-Next-GSQ-RCO-Coder](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Coder-GGUF), which some experts stripped, if you want; otherwise, you can use Vanilla Qwen or Swift with their supported quants.

> **stoppableDissolution** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfpmsv/)
> 
> Damn, thats almost as fast as I run it in vllm in nvfp4 (with bf16 attention iirc) with all the non-ngram stuf in vram on pro 6000

> **giveen** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfr5oz/)
> 
> Its faster than my engine , which is why I look at Strata regularly, and I'm chasing a giant :)

> **dir3ctly** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfxo18/)
> 
> Some questions, if someone can answer:  
> Is the cache issue fixed? (Strata processing whole context for each request)  
> Is it now known what are the magic ingredients that make it that fast?  
> Does it work with other models or is IQ3\_S still the "best" ?

> **Hotcooler** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdh0axi/)
> 
> It does officially support Unsloth Q4 at this point, probably can run others too with some small modifications.

> **nufeen** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg4bap/)
> 
> Been using IQ3\_S last days. Didn't notice any issues with context reprocessing

> **z0\_o6** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg5tqv/)
> 
> Cache issue was addressed on 9/25. I have seen there are *some* turns where prompt re-use is 0 and the wall-clock time is slower, but I have not figured out the rationale behind it and my stack is... complicated so it's more than likely my own stuff. From what I can tell, it mainly just sets the inference engine up with all the current hotness for speed-ups for the user. I don't think it is doing anything particularly magical. Happy to learn, though! I will be experimenting with other models. I want to see what it can do with larger quants.

> **Sweaty\_Chair\_4600** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfzmu0/)
> 
> Damn lucky! I get like 40 tokens on a 4090 with IQ3\_XXS and 64gb ddr5

> **Hotcooler** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdh1gts/)
> 
> Even under Windows my 4090 with IQ3\_S does south of 100tok/s with 3600-4100 prefill on 128k. Should be decently better under linux too, since my 4070ti super is not that far off (80-90tok/s and 2500-3000 prefill).

> **z0\_o6** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg3idv/)
> 
> It's not luck; I freshly installed Ubuntu Server yesterday and basically set the machine up entirely for this purpose. I'm betting you could pick up a ton of speed with some tinkering, if you find it is worth the time.

> **terorvlad** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg71hf/)
> 
> You're doing something wrong if that is with strata. My 4090m (rtx 4080 with power limits in a notebook formfactor) + 7945hx +64gb DDR5 lets me run IQ3S with max context at around 50-60 t/s.

> **pmttyji** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg9cd0/)
> 
> Something off with your setup. [Here someone](https://www.reddit.com/r/LocalLLM/comments/1wvxbuq/comment/pdftvrk/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button) is getting 40 t/s just on 8GB VRAM + 64GB DDR5 RAM + 90k context

> **Feeling-Bid8885** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdgmd4r/)
> 
> You're not setting it right?
> 
> 2 x 3090, with 1 GPU it only drops to 75 - 85 tokens/s
> 
> [https://preview.redd.it/mpgkwrybj3th1.png?width=1904&format=png&auto=webp&s=169da22173dae73ac38a9f99b529bcdaf2bf3180](https://preview.redd.it/mpgkwrybj3th1.png?width=1904&format=png&auto=webp&s=169da22173dae73ac38a9f99b529bcdaf2bf3180)

> **Sweaty\_Chair\_4600** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdmzma9/)
> 
> i updated it, and now i get like 80 tokens, which is a good improvement, im using nix-os, so setting it up properly took a bit of my time

> **poofph** · [2026-10-04](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdqyndj/)
> 
> use ai to help you set it up :)

> **sleight42** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg1awd/)
> 
> With that much memory, maybe free token or hyperqwen may let you run a larger quant? I haven't tried them but my machine is at capacity with max strata.

> **Lodestone-DnD** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg7iml/)
> 
> 150–200 tokens per second decode ~~on a 27B model~~ is wild hardware flexing. Seeing numbers like that makes me seriously tempted to upgrade my setup—especially when running a multi-agent D&D simulation with 4 local LLMs, where waiting on token speeds during active DM turns can get brutal on vintage hardware (taking several minutes per response). Incredible throughput!
> 
> Edit:  
> Not the 27b model, it's the 180b MoE Qwen3.8-Flash-Next

> **z0\_o6** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdgd2w4/)
> 
> This is not the 27b model, it's the 180b MoE [Qwen3.8-Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next)

> **Lodestone-DnD** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdgdi2o/)
> 
> Sorry, my mistake!

> **z0\_o6** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdgek09/)
> 
> No worries, things move so quickly with this stuff I can completely understand.

> **dago\_mcj** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdmyfe9/)
> 
> has anyone been crazy enough to test a heterogeneous layer splitting between nvidia and amd cards on the same machine with strata? Sounds like this involves a CUDA/HIP layer boundary? I ask becauseI have the weird setup of a ryzen 9 7900x, with 96gb ddr5 all on an Asus ROG Strix B650E-F mobo. I've gone round and round, and I'm 100% confident, it is not able to do proper bifurcation. In the top slot I've got pcie 5.0 x16 with an rtx 3090, hitting ~ 30GB/s. On the bottom pcie slot I have an rx 7900xt pushing as best as it can at ~ 7GB/s. I know, I know, my steak is too juicy, my lobster is too buttery. Yes Strata is impressive as it is without the rx 7900xt. But can I put any good use to the amd gpu in the whole Strata setup with an rtx 3090 already in use on the faster lanes?

> **z0\_o6** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdn5m2k/)
> 
> Fill that 7900xt with a model that fits entirely in VRAM. The more I work on these little projects and experiments, the more I learn that using multiple models in parallel yields a lot of benefit. Set it up for ComfyUI or a QC process or something.
> 
> Edit: I missed the main question, sorry. I expect you would run into far more problems than you would solve trying to split layers between different architectures like that, but I have no evidence either way.

> **dago\_mcj** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdn5wt5/)
> 
> Sounds like my workflow is what's holding me back then. At one point I tried a q8 of qwen 3.8 27b using vulkan to pool the vram. I'm getting better coding results tho with the strata setup. Before that I had q4 3.8 27b on either card

> **Dany0** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdflyiv/)
> 
> Ah, but IQ3 is pretty compromised :(
> 
> I use local inference lab's experimental nvfp4 checkpoint, it's really good, I can't tell the difference between it and fp8

> **MindfulMan1984** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfoc3i/)
> 
> Are you sure? [https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF) , at least on their tests, looks nice compared with BF16. They use a sophisticated quantization method.

> **Dany0** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfpzhm/)
> 
> GSQ RCO is known to hook people that haven't tried it. It's really good for IQ3, but it's not better than Q4
> 
> Last time I tested the qwen 3.8 27b Gsq rso model, it output 10x more tokens than the quant I was comparing to and wasn't even close to finishing the task, while having numerous failed tool calls in omp

> **Informal-Trouble2183** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfr995/)
> 
> Really? I tested GSQ RCO for a week on hard tasks, definitely robust, feels better than Q4. For me it's the best quant.
> 
> You can also take a look at the theoretical numbers: they are performing the same as Unsloth Q5 K\_XL according to this 3rd party test: [https://byteshape.com/blogs/Qwen3.8-27B/](https://byteshape.com/blogs/Qwen3.8-27B/)
> 
> [https://preview.redd.it/3oeaeitiv2th1.png?width=1312&format=png&auto=webp&s=40d441d2ee67a8b25b4811c8ecda100d3529c279](https://preview.redd.it/3oeaeitiv2th1.png?width=1312&format=png&auto=webp&s=40d441d2ee67a8b25b4811c8ecda100d3529c279)

> **MindfulMan1984** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg1x8n/)
> 
> People keep fussing about "oh low quant"; they would be using BF16, taking 3x longer with 10x more expensive hardware. Something similar happened when MP3 was created; a lot of snobby audiophiles fussed about "oh, this frequency is lost"; better to use a huge WAV file for the same music. Nowadays, if you have a good harness and some robust testing in your repository, it can just fly.

> **Dany0** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdjr0qd/)
> 
> If someone made mp3 for llms I'd be the first to jump in on it. The issue is they promise 192kbps mp3 and instead we get what... 16 kbps? Phone line quality

> **DystopianRealist** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdisruu/)
> 
> Many of us fought long and hard to get "Apple lossles", and not just to use more bandwidth. It's like headphones. If they're average, and you just want to enjoy the music, a heavily compressed mp3 is probably fine. If you're putting on a production for an audience, and you are using a high end sound system, losing dynamic range to compression is a measurable downside. Whether or not the latest pop song will be impacted is different than if you are listening to classical music with extreme dynamics, and very soft sections.

> **Dany0** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfrw47/)
> 
> I've seen the benchmark. see how close all the unsloth quants are? It's terrible

> **Informal-Trouble2183** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfsok5/)
> 
> The KLD measurement is objective. While people's experiences are the ones to question.

> **Educational-Region98** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdnd5gi/)
> 
> Have you tried the RCO coder quant? It's looking pretty good on paper.

> **fragment\_me** · [2026-10-04](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdq7xm9/)
> 
> Dude even Q4 is barely 93% same top p. There’s no way IQ3 is close or better. Try any long running task and it will start to crack. Errors accumulate.

> **MindfulMan1984** · [2026-10-04](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdrq7lg/)
> 
> I am testing it, no issues so far. Not having the same top P, tells the words are not equal, they still may carry the same meaning, like a synonym, but it will be a “miss” when computing top p.

> **z0\_o6** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfmos7/)
> 
> How do you assess the quality of the quantization?

> **Dany0** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfntq7/)
> 
> Well as always it's hard to say and everyone should just benchmark exclusively on their use case
> 
> I'm using gpu only inference with expert cache in FreeToken. Getting 30 tok/s (same as vllm, tuned llamacpp) decode when experts need to be fetched often, otherwise I'm getting 60 tok/s. On coding tasks this comes to 40-50 tok/s average. My omp sessions are showing 40 tok/s including prefill
> 
> Prefill is 5000-6000 tok/s peaking and 3300 tok/s average
> 
> In exchange I get output that is better than Sonnet 5 for example
> 
> When I gave q2, Iq3 my usual set of tasks, it wasn't much better than qwen3.8 27B PrismaScout which is what I used before q3.8FN was released. It was fast but looping and unsure. I give it hard programming tasks.

> **trying4k** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfwujj/)
> 
> Looking at FreeToken now! Thanks for posting your details. Curious what is your hardware?
> 
> And I hadn't heard of local inference lab's experimental nvfp4. Curious how it compares to nvidia's, have you done any comparisons?

> **Dany0** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg2zlj/)
> 
> 9950x3d, 160gb currently running at 4400 mt/s (I can probably get something closer to 6000 stable in the future), single 5090, plus an amd v620 (on my way to buy another one, and I have one more arriving in the mail soon, I'm trying to build an 8x v620 server out of this)

> **trying4k** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdhzvi7/)
> 
> Nice! ~~Unfortunately, FreeToken didn't seem to work for me. My AI card is my second card and is on a slow pcie slot, it seems that might be slowing things to a crawl (~11t/s), which is unexpected (I thought FreeToken's dynamic approach would handle it more gracefully). I guess I'll go back to llama.cpp and try a fork.~~ (see below update)
> 
> Sounds like you are building an amazing system. I wish you the best~

> **trying4k** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdiv9bq/)
> 
> Update: actually FreeToken is fine. It seems it fails to handle multi-gpu very well in the UI. Forcing my GPU with a flag in the extra command line options allowed it to work. The hypothesis is that windows desktop manager was still being queried despite the GPU not talking to windows at all. Once that was fixed, I went from 11t/s to maximums of 60t/s!

> **frumpawumpa** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfsggg/)
> 
> The information theory answer is that 6 bit is sort of the bend in the curve where lower precision starts making notable differences, but it also depends on the size of the model an how much information it was trained on. A small model trained on a lot of data already packs a lot of information into each parameter so quantization hurts more there, whereas there is more redundancy in parameters for more that is bigger relative to the amount of information it was trained on.

> **z0\_o6** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg4izb/)
> 
> I normally run 6-bpw quants if at all possible, but I am intrigued at the performance improvements I have seen with more exotic quant methods, so that's why I don't rule out trying something like this. It will keep improving.

> **frumpawumpa** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdi5yfu/)
> 
> Oh sure, I mean, that doesn't mean there's anything "bad" about using sub 6 bit quants, just that there's increasing tradeoffs, and small quant schemes are getting more sophisticated all the time.

> **fallingdowndizzyvr** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdg6ghf/)
> 
> I've tried Strata a few times since way back in the beginning. Whole days ago! I get the fast TG but I definitely do not get the fast PP. When I tried again yesterday, I topped out at around 400t/s. I get the same results over two different machines.

> **Hotcooler** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdgxih4/)
> 
> No idea why. Probably software, I have 2300-3000pp (depending on length) with 4070ti super (basically 4080-ish) with iq3s, streaming cache e.t.c.

> **fallingdowndizzyvr** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdgytbq/)
> 
> I've used anywhere from one 5060ti to 2x5060tis + 2x5070tis. I get the same 400-600ish PP. I don't know what it could be. Like I said, I've tried on two different machines. One is Ubuntu 24 and the other is 26.

> **karmaisnonsense** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdgzwcr/)
> 
> Make sure --prefill is set to auto, that enables dynamic prefill chunk sizes, borrowing from expert cache and restoring experts after prefill finishes.

> **caetydid** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdh3yzc/)
> 
> i know - it's sick!

> **nsfnd** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdh6fk6/)
> 
> I have glm lite subscription until february.  
> Strata with switch 1.5 iq3\_xxs is so good that, for the past 5~ days i have not touched glm, except some small script edits while strata is busy.  
> It succeeds everything i throw at it.
> 
> I have 5090 and 64gb ddr5, similar speeds to ops.

> **Helpful\_Jelly5486** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdhbi1b/)
> 
> Wow. That’s my setup exactly. Thanks.

> **\_TheWolfOfWalmart\_** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdhm338/)
> 
> So I have kind of a wild and weird setup.
> 
> 1x RTX 4090 + 8x Radeon Pro V620 = 280 GB VRAM
> 
> 768 GB DDR4 system RAM.
> 
> I bought the 4090 when it first came out before prices went crazy.
> 
> V620's are older cards (RDNA2) -- can Strata make use of them?
> 
> They have solid memory bandwidth, and the raw compute is okay but they don't support modern data types for acceleration. (If it isn't INT8 or something that's really easy to unpack into INT8, the prefill is hot garbage)
> 
> Also, is this based on llama.cpp or is it a from-scratch engine or what? Because I'd welcome a new contender.
> 
> llama.cpp is great, but it has issues that make it unsuitable for scaling beyond single user. So it's a no-go for anything production-ish.
> 
> vLLM/SGLang also have their own issues unless you have 5 or 6 figs worth of brand new hardware.
> 
> Currently using my own llama.cpp fork and getting 60-70+ TPS on 3.8 Flash Next, but only 500-600 t/s prefill and actually performant concurrency is basically impossible because llama.cpp

> **bennmann** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdjnzu3/)
> 
> Not gonna lie, even if you don't find a 3-5x pp increase here or elsewhere, that v620 8x is my dream upgrade to play around with.
> 
> What's your pcie connection speeds?
> 
> What are your llama.cpp flags? May still be low hanging fruit there.... Ubatch should probably be 512 and no higher, "-fitt 768" might help

> **vr\_fanboy** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdhrftp/)
> 
> i have x2 3090 + 64 ddr4, i need to test flash as orchestrator instead of CC/codex/cursor, im building a swe factory with agents.
> 
> i can imagine doing some like 3.8 flash as orchestrator, enqueue tasks and then auto swap for x4 3.8 27b (i can do x6 150k ctx each right now with x3 3090) to process the tasks in parallel. After finish swap back to flash for a fully local cheap swe factory.

> **ni1by2thetrue** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdk6g87/)
> 
> Op I am running Qwen3.8 27b NVFP4 on a NInfer fork (the one with YaRN built in) pm my 5090 and getting great results. I have 64GB of RAM and can make a page file of the same size... Which means I can run the iq3\_xxs quant of Qwen3.8 flash next, same as you. I am OK with a hit to tok/s (I don't need 180+ lol) but is this model at that quant going to be much smarter than 3.8 27b?

> **z0\_o6** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdmfbo0/)
> 
> I have noticed far less rework on my projects by using Qwen3.8-Flash-Next. Otherwise, it seems that quality comes down to preference, workflow, and scaffolding.

> **mhphilip** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdk8h1y/)
> 
> I have dual 5060ti w/ 48gb ddr4 3200. And a ryzen 5900x cpu. Anyone with a ~similar setup tried one of the IQ3 quants and have some estimates for pp and tkgen I can expect?

> **efsooo** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdkfw60/)
> 
> [https://github.com/Niko1221/Strata/pull/483](https://github.com/Niko1221/Strata/pull/483)

> **efsooo** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdkhbe4/)
> 
> sorry wrong post - [https://github.com/Niko1221/Strata/issues/392#event-32279941143](https://github.com/Niko1221/Strata/issues/392#event-32279941143)

> **mhphilip** · [2026-10-03](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdl0xvc/)
> 
> Thanks champ! Great report btw. I’ll download and try it because this looks ok for real use.

> **dir3ctly** · [2026-10-04](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdrsteb/)
> 
> [u/z0\_o6](https://www.reddit.com/u/z0_o6) , I have a somewhat similar setup (5090 + 128 GB RAM DDR5-6000, Intel 270K Plus) and I have just tested Strata with IQ3\_S. I "only" get ~ 100 t/s decode and my GPU power consumption is ~200 W.  
> I wonder what is the difference between your and my setup since you get up to 200 t/s and 400W.
> 
> My settings are mostly default + 200K max context, vision enabled, Q8 cache.

> **z0\_o6** · [2026-10-04](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdtpr9j/)
> 
> on the latest version I am actually seeing up to 225 t/s decode and PP now peaks around 6500 t/s. Are you certain you are running your GPU at full PCIe Gen5 x16, and using a speedy NVMe that isn't lane sharing? The lower power use tells me you are being bandwidth restricted.

> **dir3ctly** · [2026-10-04](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdtssk5/)
> 
> Yes, it's Gen5 x16 with full bandwidth (verified with nvidia-smi/nvtop). And a speedy NVMe.  
> With some tweaking I got up to 170 t/s for some prompts.
> 
> Do you have an AMD or Intel processor? Otherwise I only see faster RAM on your side. And my GPU is undervolted a bit (vs your power-limited). And my OS: I am on Ubuntu Linux.
> 
> When I have time I will play with some more settings to see if it has any positive effects.

> **z0\_o6** · [2026-10-04](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdtuy74/)
> 
> I'm glad to hear that tweaking is getting the speeds up to par for you. I am running an AMD Ryzen 9 9950X3D. I had the GPU undervolted on Windows, but I just went with a plain-jane power limit when I switched to Ubuntu Server.

> **ItsSmokeDev** · [2026-10-04](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdu2ii1/)
> 
> Fuegoo! Here's mine with a 3090
> 
> [https://preview.redd.it/fcy3t30q8hth1.png?width=1536&format=png&auto=webp&s=e11d7dd08574085a446d70b779962caf557cb416](https://preview.redd.it/fcy3t30q8hth1.png?width=1536&format=png&auto=webp&s=e11d7dd08574085a446d70b779962caf557cb416)

> **source-drifter** · [2026-10-02](https://www.reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/pdfquko/)
> 
> i see strata, i upvote
