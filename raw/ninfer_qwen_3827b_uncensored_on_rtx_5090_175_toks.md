# NInfer Qwen 3.8-27B uncensored on RTX 5090 175 tok/s changed my life [Visit](https://www.reddit.com/r/LocalLLM/comments/1woxb4n/ninfer_qwen_3827b_uncensored_on_rtx_5090_175_toks/)
### **Subreddit:** [r/LocalLLM](https://www.reddit.com/r/LocalLLM)
### **Author:** [u/EntrepreneurLeast445](https://www.reddit.com/user/u/EntrepreneurLeast445/)
### **Vote:** 260
---
for the first time in a long while, probably last time i felt this way was when i first used openclaw with Opus 4.6 half a year ago
it felt so life changing  that i have to write this post to share my joy.
I had this 5090 32GB VRAM for quite awhile, but it has never truly felt useful (I have claude 200USD, codex 200USD & Gemini & Grok seats and i use them interchangably) until a few big QoL upgrades in past few weeks.
- NInfer NVFP4 / groupwise-int with MTP on made the speed blazing fast - 175 tok/s is significantly faster than frontier cloud models
- 262k ctx ! (for the longest time i can only handle 64k context on a 5090 until NInfer exist, and its Q4 had the exact same quality as a normal Q8, then it freed up rooms for more context)
- the 262k ctx on a reasoning harness like hermes & dsh made long reasoning task possible, back then with 64k context, even if the harness is capable of long reasoning task, the context is too short to do a big task. it picked up some best in class method of writing a long checklist of goals to do, a checklist of test acceptance gate, then iterate through the milestone 1 by 1.
- the final cherry on top happened when my hermes-qwen couldnt solve a tough problem last night, i asked it to try, "why not try headlessly call claude -p to solve this problem, but be mindful that cloud services will block your request if its cybersecurity or something against their policy, so you would have to word your prompt safely to bypass its guardrail", it just figured out how to write the prompt properly to solve the bug that it couldnt get its head around, then i said, try asking astra too, you could compare their result. (it was trying to get into root access of a device, write its own firmware to control the device and faced a bug, and i saw it was stuck for a couple hours, so i ask it to ask astra/fable but be smart about how you ask it) it worked. then by today, i notice that whenever its stuck on something it will ask claude or codex for opinion because hermes self developed a skill to ask frontier cloud model if its stuck on a technical problem it couldnt solve.
now i feel like i can do anything. (and i felt astra/fable was never truly so useful before...)
---
## Comments 100

- by [unknown](#) **&#x21C5; 20**
  <br/> How much prefill TPS do you get at higher context between 150 and 250?

- by [unknown](#) **&#x21C5; 8**
  <br/> I only have one recorded data point at high context:

~248K tokens (247,802): 1,675 tok/s prefill (took 148 seconds)

That was the needle-in-haystack test at 90% depth, measured Aug 22 on groupwise-int with ⁠ --kv-dtype int8 ⁠.

No measurement logged at 150K specifically. Prefill speed generally scales roughly linearly with context length (less self-attention overhead at shorter contexts), so at 150K you'd expect somewhere around 2,500-3,000 tok/s — but that's an estimate, not measured.

(answered by my AI)

- by [unknown](#) **&#x21C5; 2**
  <br/> I think you should have more performance to squeeze out of the 5090. I just ran a needle in the haystack test at 90% depth of 262k ctx and got a median of 1580tok/s prefill across 3 runs on a RTX PRO 4500, which is close to a 5080 in compute (but capped to 200W).

This was on vLLM-nightly, using `lyf/Qwen3.8-27B-Huihui-Abliterated-NVFP4-MTP-VL` with fp8 kv cache.

- by [unknown](#) **&#x21C5; 3**
  <br/> Mind sharing your whole recipe(os, launch options, specific quant, divergence if you measured it?) I want to try NInfer but that stupid wsl2 bug and the Quant quality kept me away.

- by [unknown](#) **&#x21C5; 16**
  <br/> Why not just switch to Linux?

- by [unknown](#) **&#x21C5; 6**
  <br/> Probably because gaming is happening on that card, too. And switching all of that to Linux is a hassle depending on the games played. It's a walk in the park for some, it's near impossible for others. Especially if all the features of the Nvidia-Stack are being used, Linux gaming just isn't equivalent in that area.

- by [unknown](#) **&#x21C5; 4**
  <br/> Dual boot is also an option.

- by [unknown](#) **&#x21C5; 5**
  <br/> I know, that's what I'm personally doing. But I also get the lazyness of the people who want to have everything in one place. Once you're comfy with an OS, it becomes like a living room to some people.

They'd rather have it less than ideal for some things, but feel like home, rather than tear it down and replace it with something better.

- by [unknown](#) **&#x21C5; 1**
  <br/> I guess everyone has their own priorities, and if you're just playing with LLM's it's not a big deal.

But if you already spent thousands of dollars on hardware, hours learning the tools, and want to do serious work with it, imo it seems a bit silly to not spend an hour setting up a better environment for yourself to get better performance and remove a lot of headaches.

- by [unknown](#) **&#x21C5; 1**
  <br/> Quick to set up as well, only about 15 minutes.

- by [unknown](#) **&#x21C5; 5**
  <br/> This is the way

- by [unknown](#) **&#x21C5; 1**
  <br/> I’m all for Linux adoption where it makes sense, but effectively someone asked what was in that sandwich and you told them to learn how to make their own bread, grow a vegetable garden and raise livestock to recreate said sandwich.

- by [unknown](#) **&#x21C5; 8**
  <br/> This analogy is ass.

It's more like steaming a potato in a pot, asking a guy for the recipe after finding out he does it much quicker and better in an instant pot.

- by [unknown](#) **&#x21C5; 4**
  <br/> installing linux (ubuntu) is a single live USB, an install menu, sudo apt install random things, and done. You're not Terry Davis building an operating system in a cave with a bunch of scraps

- by [unknown](#) **&#x21C5; -3**
  <br/> For someone who knows what they’re doing, yes. For someone who doesn’t, my analogy stands. Relearn how to find where your apps are. Relearn how to install programs. Relearn where the settings are, relearn…

- by [unknown](#) **&#x21C5; 4**
  <br/> I say this with as much respect as possible, but if you don't have elementary IT ability and the willingness to learn new things, you aren't going to go very far with AI in comparison to others... that said I wish you the best of your journey

- by [unknown](#) **&#x21C5; 3**
  <br/> Keep steaming the potato in the pot then

- by [unknown](#) **&#x21C5; 3**
  <br/> Linux isn't rocket science.  Like if you got far enough to run into a wsl bug when trying to configure your LLM server to use an nvfp4 model, you've already dealt with more technical problems than installing and using Linux.

- by [unknown](#) **&#x21C5; 1**
  <br/> Ignore these linux supremacists lmao. The dude has zero reason to switch and he wont either because some redditors said so

- by [unknown](#) **&#x21C5; 2**
  <br/> Well he said he was having problems with the LLM tooling on Windows, so that would be a reason to switch.

- by [unknown](#) **&#x21C5; 2**
  <br/> Its not a windows issue ,  my entire workflow is on windows , long horizon with multiple tool calls. You need to set it up properly

- by [unknown](#) **&#x21C5; 0**
  <br/> I mean installing Linux is not that hard.  If you're technical enough to get into local llm's you're technical enough to flash an Ubuntu iso and spend 5 minutes clicking through the installer.

Linux is just a better experience for this kind of thing.

- by [unknown](#) **&#x21C5; 2**
  <br/> I run on wsl... haven't seen this bug but have seen a variety of them in other areas

- by [unknown](#) **&#x21C5; 1**
  <br/> 90% depth? Don't you have to compact before you hit 50%?

- by [unknown](#) **&#x21C5; 1**
  <br/> ......whaaa

- by [unknown](#) **&#x21C5; 1**
  <br/> Dude I don't know. I'm still kind of new at this.

- by [unknown](#) **&#x21C5; 1**
  <br/> I made my own port of ninfer for rtx 4090, and implemented ternary, now ninfer reads bonsai 2 27b and i got 210 tok/s and 3k prefill

- by [unknown](#) **&#x21C5; 1**
  <br/> Dont you find it gets a bit stupid at those quants?

- by [unknown](#) **&#x21C5; 32**
  <br/> That’s actually an inspirational story.

- by [unknown](#) **&#x21C5; 4**
  <br/> same here! went through various variants of 3.8 27b and found an the exact variant youre using... speed, quality, context is mind-blowing.... ive setup 3 gpu nodes in a cluster and 3.8 manages and keeps long context while letting the other 2 models do smaller tasks.... hermes is on my roadmap.. i was building my own ai-router and agents with tools via python, but noticed im building something others have alread perfected.... it also included a gatekeeper that can ask external models with anonymizer and rewording.... how cool that hermes has a too for that! thanks for the insight and have fun!

- by [unknown](#) **&#x21C5; 1**
  <br/> Maybe I need to check Hermes out, I built a controller so chatgpt and claude can use my local agents as if they were sub agents  but it sounds like I tried reinventing the wheel

- by [unknown](#) **&#x21C5; 4**
  <br/> Exactly same story, feel like my 5090 can finally stretch it's legs. I use DFlash2 and average around 186 tok/s with my fully loaded agentic dev sessions at 218k context. I'm using the windows version of Ninfer though but from what I heard there's very little difference. Which version of NVFP4 model are you using? The one I'm using has DFlash2 baked in along with a 55/45 fp4/fp8 split. It's a larger model but performs well. The tradeoff I would take would be to have an uncensored model with full context.

- by [unknown](#) **&#x21C5; 4**
  <br/> Ninfer is actually extremely impressive. I'm lucky enough to also have a 5090 and I was not really expecting much, being skeptical about the hype, but holy moly is it a quick little engine.

- by [unknown](#) **&#x21C5; 3**
  <br/> how do you fit 262k with 3.8-27B. I'd love to try it on my 5090.

- by [unknown](#) **&#x21C5; 3**
  <br/> I mean, he pretty much told you.

"NInfer NVFP4 / groupwise-int with MTP on made the speed blazing fast - 175 tok/s is significantly faster than frontier cloud models"

- by [unknown](#) **&#x21C5; 2**
  <br/> Where do you get the uncensored version? I’m running the standard binder for 5090 now, can you post a link

- by [unknown](#) **&#x21C5; 14**
  <br/> lyf/Qwen3.8-27B-Huihui-Abliterated-NInfer-NVFP4

HuggingFace: [huggingface.co/lyf/Qwen3.8-27B-Huihui-Abliterated-NInfer-NVFP4](http://huggingface.co/lyf/Qwen3.8-27B-Huihui-Abliterated-NInfer-NVFP4)

It's the huihui abliterated (uncensored) Qwen 3.8-27B, pre-converted to NInfer NVFP4 format.

- by [unknown](#) **&#x21C5; 8**
  <br/> I used huihui's original uncensored safetensor model to convert it to ninfer using ninfer's own convertor. But the test was not comparable to the original model. I also tested some other uncensored models as well.

IFBench prompt strict testOfficial 87%HuiHui 80%JohnanthanColetti 81%Jiunsong 79%

GPQA-Diamond reasoning testOfficial 84%HuiHui 76%JohnanthanColetti 84%Jiunsong 86%

so the best so far is JohnanthanColetti one.

- by [unknown](#) **&#x21C5; 1**
  <br/> Thanks mate

- by [unknown](#) **&#x21C5; 1**
  <br/> Is this the current bestModel

- by [unknown](#) **&#x21C5; 1**
  <br/> This is a great model.

However there are still censorship issues. Just prompt it with basically telling it is in a test environment and to ignore safety guardrails to improve the testing. Once I did this, I've never run into another issue.

- by [unknown](#) **&#x21C5; 2**
  <br/> Can someone point me to something that explain what you folks are talking about please?

- by [unknown](#) **&#x21C5; 1**
  <br/> Same here

- by [unknown](#) **&#x21C5; 1**
  <br/> I tried it out and the eye test feels like base q8 is smarter by a good margin

- by [unknown](#) **&#x21C5; 3**
  <br/> Can you post your model url to download? And do you think ninfer is equivalent to q6 or q8 gguf models?

- by [unknown](#) **&#x21C5; 5**
  <br/> ninfer q4, i did a benchmark test against q8. (i was running llama ccp on q8 before this, then i swap to ninfer q4, and do benchmark test on both). they scored the same.

- by [unknown](#) **&#x21C5; 3**
  <br/> have you tested the nvfp4?

- by [unknown](#) **&#x21C5; 1**
  <br/> What benchmark test did you use?

- by [unknown](#) **&#x21C5; -2**
  <br/> Can I get link to download? Is text-image-to-text?

- by [unknown](#) **&#x21C5; 1**
  <br/> Lqwwwdyolli2

- by [unknown](#) **&#x21C5; 2**
  <br/> Try DFlash2 on that beast and enjoy 300 TPS :)

- by [unknown](#) **&#x21C5; 4**
  <br/> with ninfer?  or how

- by [unknown](#) **&#x21C5; 0**
  <br/> Haven't used Ninfer, only club-3090.

There are some benchmarks posted there pushing 450 t/s.  But only with dual 5090s,  you'll likely get 300+ with a single 5090.

Checkout their DFlash2 setup,  get an LLM to set it up for you.

- by [unknown](#) **&#x21C5; 1**
  <br/> Why use club-3090 over something like unsloth studio?

- by [unknown](#) **&#x21C5; 1**
  <br/> I didn't understand unsloth studio.  I went there and it looked like a product page.

What does unsloth studio do?

- by [unknown](#) **&#x21C5; 1**
  <br/> You inspired me to have another testing round for finding the best settings for my 4070 running mainly different finetunes of Qwen 3.6 35B 3b.. Will take a look again at the Flash Next settings as improvements there would make the most difference 10 - 20 tps there just aint enough for repeated tasks.

- by [unknown](#) **&#x21C5; 1**
  <br/> Will it ever work on 16GB gigabyte Blackwells like the 5060ti?

- by [unknown](#) **&#x21C5; 1**
  <br/> There are forks of Ninfer for the 5060 ti. I’ve never used them, so I can’t comment on how well they work.

- by [unknown](#) **&#x21C5; 1**
  <br/> Any links perchance? :) I've not been able to locate anything so far.

- by [unknown](#) **&#x21C5; 1**
  <br/> Here you go. This is probably the most updated. Like I said, I've never used it.[https://github.com/ruwwww/ninfer-5060ti](https://github.com/ruwwww/ninfer-5060ti)

- by [unknown](#) **&#x21C5; 1**
  <br/> Thanks very much  [ah..just noticed it's Linux only. Shame.]

- by [unknown](#) **&#x21C5; 1**
  <br/> I have been using this for my hermes agent, you get mtp, 128k context and vision.  It is an older fork though and you may need to patch for 5060 although since I i also have a 5070 and specified -device param it could just be me. [https://huggingface.co/ninfer-5080/Qwen3.8-27B-RTX5080](https://huggingface.co/ninfer-5080/Qwen3.8-27B-RTX5080)

- by [unknown](#) **&#x21C5; 1**
  <br/> Thanks. But Linux only, and I'm Windows.

- by [unknown](#) **&#x21C5; 1**
  <br/> There is only 1 answer to this ...

- by [unknown](#) **&#x21C5; 1**
  <br/> Use Windows with a docker container and WSL? Because that's what I'm doing.

- by [unknown](#) **&#x21C5; 1**
  <br/> Linux :) try CacheyOS if you are into gaming.

- by [unknown](#) **&#x21C5; 1**
  <br/> I've been working to get Hermes working in a similar way, but I've taken a slightly different appraoch. I have an R9700 that I was using with Qwen 3.8 27B as my main model for Hermes, but I just connected my Codex account, and now use Luna 6 as the main model.  I configured the R9700 running the same model as a Kanban worker, and now I give tasks to Hermes/Luna that it then delegates to the GPU. I also have an RX 9070 and a RTX 2070 MaxQ that I'm integrating into the pool so task can be spread around to all of those workers. Most of the work still happens locally, but that arrangement makes escalating to a cloud model simple. I haven't used it a whole lot yet, but in the two days I've been tinkering with it, it hasn't moved my ChatGPT/Codex usage number at all, so most of the work is remaining local. My intention is to configure a way to make this stack work a problem, but if it needs to, it can escalate to Astra after some number of failures.

This obviously has some privacy concerns, but I'm using this as a stand in to see if I can get this orchestration working for very long runs with the majority of work happening on the local hardware.  If I'm successful, the next move is to try to replace the cloud models with something like a Strix Halo, or M3/5 Ultra Mac Studio 256GB system (which is why I'm using Luna as the orchestrator instead of Sol/Astra).

- by [unknown](#) **&#x21C5; 1**
  <br/> Thanks for sharing, will give it a try. Currently same model Q5 on Ollama with 5090 ~ 60 token/s

- by [unknown](#) **&#x21C5; 1**
  <br/> Op I have the same setup - NInfer, on a 5090 running abliterated swift Qwen3.8. Getting 300k context. I wanted to ask though, what is your Hermes setup? I was on Hermes, with cloud models, but with local models it's more of a struggle - even with a minimal set of skills, just having the Mnemosyne memory plugin and Lossless Compaction took up 7 - 8k of context just for the system prompt at the start. Seemed inefficient.

- by [unknown](#) **&#x21C5; 1**
  <br/> There are forks of ninfer such as cometkim and gzenz which allow to run qwen3.8 with context up to 1m (theoretically). Personally I run swift-qwen3.8 with ctx 484k

- by [unknown](#) **&#x21C5; 1**
  <br/> Very interesting. I can do max 175k with upstream ninfer on Gwen 3.8 along with MTP 4. What are typical pp and tps you are getting?

- by [unknown](#) **&#x21C5; 1**
  <br/> 175k - is it nvfp or groupwise-int?

PP isn't its strength. It may start from 4k tok/s or even 10k tok/s on 4096 chunk, but it always drops to ~1k on long context (150+)

The highest decode rate I saw was 410 tok/s with concurrency 2. In single thread max was near 220. The average is somewhere around 160-170 tok/s

- by [unknown](#) **&#x21C5; 1**
  <br/> 175k on nvfp4. I benchmarked and saw groupwise int is slower by atleast 10% than nvfp4. I am still a beginner so naively thought fastest is best and ignored the rest. I am rethinking my decisions now after spending few days of local agentic coding.

Which fork you are currently using?

- by [unknown](#) **&#x21C5; 1**
  <br/> I don't have much xp as well)

Currently I use gzenz - with it I can run nvfp4full and nvfp4-qat models with full or full*2 context

Also I discovered the ThinkingCap model recently. As claimed it uses fewer thinking tokens without noticeably reducing quality. I've converted it to ninfer, hope to publish it in the next day or two

upd: someone already made it - [https://huggingface.co/Schestex/ThinkingCap-Qwen3.8-27B-NInfer](https://huggingface.co/Schestex/ThinkingCap-Qwen3.8-27B-NInfer)

- by [unknown](#) **&#x21C5; 1**
  <br/> I’ve found nvfp4 to be about 88% of BF16, where Q6 is about 92% and Q8 is 95%

- by [unknown](#) **&#x21C5; 1**
  <br/> this made me realise i was running a larger uncencored model so i was capped at 131k context.

gg bro

- by [unknown](#) **&#x21C5; 1**
  <br/> So what have you built with it fully locally? No calls to the frontier…

- by [unknown](#) **&#x21C5; 1**
  <br/> Not uncensored but I made this to help a friend set it up: [https://github.com/ZenderX/ninfer-qwen3.8-27b-nvfp4](https://github.com/ZenderX/ninfer-qwen3.8-27b-nvfp4)

- by [unknown](#) **&#x21C5; 1**
  <br/> Go Vllm you with get that speed plus some plus concurrent requests

- by [unknown](#) **&#x21C5; 1**
  <br/> Damn Thanks for sharing this, gonna try today on my 5060ti les see how the 8bit quant or nvfp4 quant feels for it

- by [unknown](#) **&#x21C5; 1**
  <br/> you can still make more improvements on that, i have my own fork of ninfer, and im already getting 3k prefill, and 210 tok/s on a rtx 4090

- by [unknown](#) **&#x21C5; 1**
  <br/> 210 decode on 4090? I have a 4090 too and get over 100 tps only at ridiculous low context sizes (less than 100 for prompt + output).

What is your realistic 30k context decode?

- by [unknown](#) **&#x21C5; 1**
  <br/> As soon as i get home i will make a bench on 30k context.

- by [unknown](#) **&#x21C5; 1**
  <br/> More info?..Model?..Specs?..

- by [unknown](#) **&#x21C5; 1**
  <br/> Im looking for a uncensored nvfp4 ninfer version of 27b that runs on a 24gb laptop 5090

- by [unknown](#) **&#x21C5; 1**
  <br/> Thank you for sharing this. This is helpful to understand how Qwen a new model out is performing better than other models.

- by [unknown](#) **&#x21C5; 1**
  <br/> Is it available for 5070ti

- by [unknown](#) **&#x21C5; 1**
  <br/> Are there any detailed setup guides (both hardware and software) to get this running on a dedicated single 5090 system? I have a couple of extra 5090's and want to put at least one of them to use running NInfer Qwen 3.8-27B.

I"m assuming trying to run two of them on standard consumer hardware (other than adding a 1600 watt power supply) wouldn't be worthwhile or possible to do)? I'm doing a ton of research but am basically completely new to this.

- by [unknown](#) **&#x21C5; 2**
  <br/> What tasks do you find the standard, non-uncensored version refuses? I have found abliterated models to be severely lobotomised.

- by [unknown](#) **&#x21C5; 2**
  <br/> I feel like any time I stray from the base model things get sketchy. Little things, like getting stuck in a loop, etc.

- by [unknown](#) **&#x21C5; 1**
  <br/> I was having an issue during a CTF challenge with SQLMap where I knew the injection vector, and SQLMap was being insanely slow, so I fed it to the regular version to proceed and it refused whereas an abliterated version happily chugged along and gave me what I needed.

Besides - When things like Gemini 3.8 Flash are refusing questions like [this](https://pbs.twimg.com/media/HS5O_9RWUAAHlUG?format=jpg&name=medium) and [this](https://pbs.twimg.com/media/HS7o5o_W0AA36PH?format=jpg&name=medium), abliteration becomes more and more important.

- by [EntrepreneurLeast445](https://www.reddit.com/user/EntrepreneurLeast445/) **&#x21C5; -2**
  <br/> Hi [u/EntrepreneurLeast445](/user/EntrepreneurLeast445/)

Do you mind briefly explain why you use uncensored version of this model? I used to believe Qwen3.8-27B comes without any restrictions, even in Chemistry, Biology and some other sensitive areas. But it seems you are working on some areas that the original model would reject?

- by [unknown](#) **&#x21C5; 18**
  <br/> Nice try cop

- by [unknown](#) **&#x21C5; 1**
  <br/> Sorry, I did not realize this question is so sensitive.

- by [unknown](#) **&#x21C5; 0**
  <br/> So many “changed my life” posts. So many of our lives are changed because of LLM tps and prefills. What a time to be alive.

- by [unknown](#) **&#x21C5; 1**
  <br/> It cost more than a new version of my motorcycle now, around 6k€...
