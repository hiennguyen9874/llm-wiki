# Ninfer and a 5090 with 3.8 27B is making me cry tears of joy it's so good. [Visit](https://www.reddit.com/r/LocalLLaMA/comments/1w0fxos/ninfer_and_a_5090_with_38_27b_is_making_me_cry/)
### **Subreddit:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA)
### **Author:** [u/Rollingsound514](https://www.reddit.com/user/u/Rollingsound514/)
### **Vote:** 190
---
Built the latest and I'm getting as much as 220 tokens per second and averaging in the 170s, I can't get over it.
If anyone on here is on that project, fuckkkin' chapeau man, really incredible job. I can't believe I was able to like double or more my throughput from llama.cpp
This is what I set up:
command: >
ninfer-serve /models/qwen3_8_27b_nvfp4.ninfer
--model-id qwen3.8-27b-nvfp4
--host [0.0.0.0](http://0.0.0.0)
--max-context 240000
--kv-capacity 240000
--max-concurrency 2
--kv-dtype fp8
--host-kv-mib 16384
--spec mtp --draft-tokens 3
--lm-head-draft
--vision
--media-live-mib 2048
---
## Comments 162

- by [unknown](#) **&#x21C5; 52**
  <br/> Amen. Just read this post about using multiple qwen3.8-27b agents in a setup that matches Fable 5 on LiveCodeBench ([https://www.reddit.com/r/LocalLLaMA/s/NG4bzXsIz4](https://www.reddit.com/r/LocalLLaMA/s/NG4bzXsIz4))

Set up a Hermes skill in a couple of minutes that matches the approach. Feels insane. I don't know what is crazier; performance of the frontier from 6-12 months ago on a $5k gpu, or that it's achievable by anyone for pennies with Luna. What a time to be alive

- by [unknown](#) **&#x21C5; 40**
  <br/> It's the worst it will ever be, which is the wild part

- by [unknown](#) **&#x21C5; 11**
  <br/> worst - yes. cheapest? wellllllllllllll................

- by [unknown](#) **&#x21C5; 1**
  <br/> Hi. Long term claude user here. I've been using kimi k3 via CLI ($200/mo sub).What Anthropic was giving me for $200/mo, and would allow me to code all day, without hitting any limits in a month, now I hit 50% of my $200/mo sub in ~10 days.

Meaning, I would need to multiply the claude code subscriptions and bear w all the shit X and Y company is doing w their models.

So, having a GPU that can run Opus 4.6 max kind of a local LLM pays off. It's a one time investment and no one can f u.

- by [unknown](#) **&#x21C5; 2**
  <br/> Thanks for the link, going to give this a try myself now....

- by [unknown](#) **&#x21C5; 2**
  <br/> It’s 240k context shared though. You can have 3 concurrent sessions but it’d be split 80k each.

But anyway, it looks like it’s worth trying, thanks for the info

- by [unknown](#) **&#x21C5; 15**
  <br/> This flag --host-kv-mib 16384 is used for keeping kv cache backups in RAM so that you can switch between contexts that you've been using without computing prefill again and again.

- by [unknown](#) **&#x21C5; 2**
  <br/> The idea that you can get a lower active param model to match one with many more active parameters is believable and remains a very underrated approach (I've tried this with the MoE 3.6 vs dense 3.6 a while ago) but it comes with diminishing returns and caveats in practice. I'd like nothing more for multiple Luna or glm 5.3 flash in concert to match Fable, but reality does not bear this out in general.

- by [unknown](#) **&#x21C5; 1**
  <br/> Had just looked at that paper too. May I ask why you chose Hermes for this?

- by [unknown](#) **&#x21C5; 2**
  <br/> Literally just because I already had it installed. But apparently it was a good choice because creating a new skill to use the approach was pretty pain-free because things like delegation were already there.

- by [unknown](#) **&#x21C5; 1**
  <br/> I wouldn't say Frontier models were here 12 months ago, I would say 6-9 months...

- by [unknown](#) **&#x21C5; 1**
  <br/> Agreed

- by [unknown](#) **&#x21C5; 1**
  <br/> Could you share the skill in a gist or something?

- by [unknown](#) **&#x21C5; 2**
  <br/> [https://anonpaste.com/l/d7b2f2](https://anonpaste.com/l/d7b2f2)

- by [unknown](#) **&#x21C5; 2**
  <br/> ty good sir

- by [unknown](#) **&#x21C5; 29**
  <br/> Collected multiple forks of different NVIDIA GPUs. Somebody please make forks for AMD/Intel too.

  - **NInfer** -  [5090](https://github.com/Neroued/ninfer), 4090( [1](https://github.com/UDPSendToFailed/ninfer-4090) | [2](https://github.com/sergiuszm/ninfer-4090) | [3](https://github.com/jram4/ninfer-4090) | [4](https://github.com/shantanusingh16/ninfer-4090) ), [3090](https://github.com/Don-Chad/ninfer-3090), [CMP 170HX](https://github.com/Ithrial/ninfer-cmp170hx)

- by [unknown](#) **&#x21C5; 4**
  <br/> Damn, no 5080?

- by [unknown](#) **&#x21C5; 2**
  <br/> So hungry for this

- by [unknown](#) **&#x21C5; 2**
  <br/> Create an nvidia NIM account, download/clone the 5090 repo, and ask the LLMs in the NIM api to go nuts lol

- by [unknown](#) **&#x21C5; 1**
  <br/> ever find it?

- by [unknown](#) **&#x21C5; 1**
  <br/> No

- by [unknown](#) **&#x21C5; 2**
  <br/> any chance of a ninfer for 4060 ti 16gb ?

- by [unknown](#) **&#x21C5; 2**
  <br/> None yet for split model across two GPUs  I guess

- by [unknown](#) **&#x21C5; 1**
  <br/> club-3090 covers that

- by [unknown](#) **&#x21C5; 2**
  <br/> [https://github.com/geoffwatts/ninfer-v100](https://github.com/geoffwatts/ninfer-v100)

- by [unknown](#) **&#x21C5; 1**
  <br/> openai is saying 5060ti fork could work for rtx4000 pro... tempted to try

edit: trying now, wish me luck

edit2: this worked, i have a post about this.

- by [unknown](#) **&#x21C5; 10**
  <br/> Second this, I love ninfer. I've got two 5090s, each running a ninfer instance. Loving it.

- by [unknown](#) **&#x21C5; 2**
  <br/> This is my exact goal once(if) 5090 prices come back to planet earth.

Would you be willing to share which 5090 Ninfer fork and cpu/ram specs you're running? How much do you power limit the GPU's?

- by [unknown](#) **&#x21C5; 11**
  <br/> I have to suspect 5090 prices are never coming down unfortunately. I'm one of the people watching on the sidelines thinking the same thing, I want to buy one. I guess demand is just unlimited right now, lots more want to enter the space than people already in it (local inference).

- by [unknown](#) **&#x21C5; 1**
  <br/> Yeah, considering a 3090 is still rising in price and very in demand I think 5090 would drop in price maybe in 10 years

- by [unknown](#) **&#x21C5; 2**
  <br/> I'm on the latest OG ninfer, EPYC 7532 128GB DDR4 3200, power lim to 400W each.

- by [unknown](#) **&#x21C5; 1**
  <br/> How is your speed on that rig?

- by [unknown](#) **&#x21C5; 1**
  <br/> Great - average I'd say is around 160 decode and 2500 prefill. got the context up to 400k which helps a lot too. Check my post history for details if you're interested!

- by [unknown](#) **&#x21C5; 1**
  <br/> What kind of use cases really shine with 2 5090s and ninfer. I have 2 of these guys that I bought at msrp nearly a year ago and have only dabbled in running local models due to a lack in spare time. Now I’m lowkey thinking of selling either one or both given the prices they are going for nowadays. But if there is solid utility then I might keep them.

- by [unknown](#) **&#x21C5; 1**
  <br/> NVFP4 is really great, I'd say keep 1 for that alone. You can get a LOT done with ninfer, 400k+ context and multiple concurrency. Two is a bit overkill, unless you're looking at running bigger models and you want the vram.

- by [unknown](#) **&#x21C5; 1**
  <br/> End goal would be an entire ai coder stack

Tbh I have a 4090 fe pc as well that I don’t really need that I’m thinking of parting out. I think it’s components could honestly get close to $5k sold which makes me debate either buying a gx10 to pair with the dual 5090 setup after selling said 4090 FE pc or selling both 5090s and the other pc to finance a $15k rtx 6000 pro card…decisions decisions. Everything is going up in price rn so I don’t have time to sell before locking in a price on the 6000 card. But my brother has a couple /is heavily invested in his own local ai setup and he could possibly purchase a third at today’s price to lock it in for me while I sell my hardware to pay him back.

I need to do a lot of research though and tinker with what I got first. But I’m curious, what would you do if you were in my admittedly very privileged position(and why)?

- by [unknown](#) **&#x21C5; 2**
  <br/> The 96GB card is the holy grail I'd say - direction of travel looks to be more use of things like ngram offloading, so it really comes down to can you keep the essential weights all on vram...check the numbers that pro 6000 users are getting on qwen flash next vs practically any other way of getting to 96 and above and you'll see what I mean.

- by [unknown](#) **&#x21C5; 7**
  <br/> Does anybody know if there’s a ninfer fork for 4090?

- by [unknown](#) **&#x21C5; 6**
  <br/> [https://github.com/sergiuszm/ninfer-4090](https://github.com/sergiuszm/ninfer-4090)

Got it working, about 130-170 tps I think? Can’t remember but it’s good. I used the docker implementation windows with wsl2 as the gpu passthru

Edit: I did try this too but it failed on build many times. [https://github.com/UDPSendToFailed/ninfer-4090](https://github.com/UDPSendToFailed/ninfer-4090) I think it has better baseline tps so lmk if u get it working and how

- by [unknown](#) **&#x21C5; 6**
  <br/> I'd cry tears of joy just to have a 5090.

- by [unknown](#) **&#x21C5; 5**
  <br/> anybody on windows and doesnt want to use linux or wsl2 you can try out mine: [https://github.com/headpiece747/ninfer-5090-windows](https://github.com/headpiece747/ninfer-5090-windows)

- by [unknown](#) **&#x21C5; 3**
  <br/> Trying it now, seems excellent, recommended to anyone reading.

- by [unknown](#) **&#x21C5; 1**
  <br/> if I'm already using wsl2, is there still a benefit to the native Windows version? curious to try later

- by [unknown](#) **&#x21C5; 4**
  <br/> I feel the same way about 3090 and syv-ai

Feels like we are in the beginning of the golden age of local ai

- by [unknown](#) **&#x21C5; 13**
  <br/> While it spits out tokens fast, it's still nvfp4. And the loss between q6->nvfp4 is definitely there.

- by [unknown](#) **&#x21C5; 8**
  <br/> People say that all of the time and I've never seen a single bit of actual data that shows it makes a meaningful difference. On the contrary, every time I am presented with actual evidence, q4 stands up insanely well in testing.

- by [unknown](#) **&#x21C5; 3**
  <br/> I thought the same thing until I looked more into the BPW of nvfp4. While the more common weights are nvfp4 the higher more complex weights are all fp8. It's roughly a 55/45 split between the two. Effectively ninfer/nvfp4 is around 6.06BPW. In comparison to Q6_K_M is around 6.4BPW. So at the end of the day you sacrifice very little to effectively double if not more your throughput.

- by [unknown](#) **&#x21C5; 1**
  <br/> Make your own ninfer converter to pack the 6-bit weights into the ninfer format.

- by [unknown](#) **&#x21C5; 6**
  <br/> try the 35B and you have a personal cerebrasI run it in pi harness to do well scoped taskd and it flies at 500-600 tk/s

- by [unknown](#) **&#x21C5; 6**
  <br/> I am absolutely dying for ninfer qwen4-35b-a3b. At that point I think with models where we'll mostly stop asking "can it?" and start asking "how quickly can it?"

It looks like for you that time is already *now* with qwen3.6-35b-a3b. Have to admit, I haven't tried it.

- by [unknown](#) **&#x21C5; 5**
  <br/> Qwen3.6?

- by [unknown](#) **&#x21C5; 1**
  <br/> I tried it for a few days and it’s insane

- by [unknown](#) **&#x21C5; 3**
  <br/> How are you guys pushing such high context numbers like this? Are you all running Windows? If I kill off my whole display manager I can fit around 190k at Q8 KV cache. I don't get what you're all doing differently than I am.

- by [unknown](#) **&#x21C5; 4**
  <br/> I'm running Linux. Headless system

- by [unknown](#) **&#x21C5; 8**
  <br/> You got a 5090 dude. Stop acting gpu poor.

- by [unknown](#) **&#x21C5; 3**
  <br/> It’s all relative. Much as the housing market, op likely bought the 5090 back when it was actually priced for the GPU middle-class.  Buying in now would certainly require far more free cash than the average localllama member would want to burn though.

No need to dump on the guy, let him enjoy his moment.

- by [unknown](#) **&#x21C5; 2**
  <br/> Bought multiple for my ai right are 2100 avg cost

- by [unknown](#) **&#x21C5; 2**
  <br/> The project is amazing. I forked it last week to add Windows support and been diving through the code and kernels for a few days. I now have my own C re-write that works on both platforms.

It's crazy how much extra performance you can unlock when you specialize to the hardware.

- by [unknown](#) **&#x21C5; 1**
  <br/> Can you paste a handoff document for my codex to implement thanks

- by [unknown](#) **&#x21C5; 3**
  <br/> Hi Sol, go through this codebase and plan out a re-write to C. Leave the kernels intact, just conform them to the C ABI and write the necessary kernel launchers so we can call them from C code. He knows what to do, he will plan it all out step by step. Implement with a cheaper model as this is a ton of work, Luna/Terra on high is good, once he's done with a big chunk do a polish pass with Sol, run tests, update milestone, move to next step.

The key here is with 'extern "C" ' the cuda kernels can be called from C code or any language that can speak the C ABI like C3/Odin/Zig/Rust, so you can pick your favorite host language really. I picked C since I can't really follow the C++ code that well, C reads much cleaner, and I got to learn about the different subsystems of the project throughout the rewrite. The cuda code remains identical pretty much, you're just calling it through the ABI bridge. Host code can be anything that speaks the ABI, device code stays in cuda.

- by [unknown](#) **&#x21C5; 2**
  <br/> Hi

- by [unknown](#) **&#x21C5; 1**
  <br/> Would native Windows support be even faster than via WSL2? or just easier to setup?

- by [unknown](#) **&#x21C5; 2**
  <br/> I know ninfer supports the 5060ti. Any chance a dual setup can benefit from it? That would require quite the overhaul doesn’t it? Anyone tried this?

- by [unknown](#) **&#x21C5; 3**
  <br/> Try it out if you're comfortable dealing with the code a little. Just point your favorite LLM at it and see what he comes up with.

- by [unknown](#) **&#x21C5; 1**
  <br/> I agree. But unfortunately don’t have the time for that kind of tinkering right now. Was hoping someone else already did some heavy lifting.

- by [unknown](#) **&#x21C5; 3**
  <br/> Dual 5060 gang checking in. Please help us, ninfer.

- by [unknown](#) **&#x21C5; 1**
  <br/> Check out [this project](https://github.com/syv-ai/qwen38-27b-rtx3090/issues/22) and my comment above.

- by [unknown](#) **&#x21C5; 1**
  <br/> I am getting 100 tokens per second with this but it killed my prefil speeds.  Trying to figure out why but dflash2 is awesome for decode that's for sure. Thanks!

- by [unknown](#) **&#x21C5; 2**
  <br/> You *absolutely* have to let me know if you get this going. I have a 5090 + 5060ti in my pc at the moment. That would be AWESOME. Hell, I wasn't even aware that it supported the 5060ti at all.

- by [unknown](#) **&#x21C5; 1**
  <br/> I think it’s built for 1 gpu setups. Not 2. Not many people rock two 5090’s. 5060/5070 more so. Ps I love my dual 5060’s. Great bang for buck.

- by [unknown](#) **&#x21C5; 2**
  <br/> I can't even tell you how many times I have debated selling my 5090 to buy as many more 5060ti's as I could haha

- by [unknown](#) **&#x21C5; 1**
  <br/> Check out [this project](https://github.com/syv-ai/qwen38-27b-rtx3090/issues/22) and my comment above.

- by [unknown](#) **&#x21C5; 2**
  <br/> There’s something [faster than Ninfer](https://github.com/syv-ai/qwen38-27b-rtx3090#vs-ninfer-3090) that reportedly [works on dual RTX 5060 Ti 16GB](https://github.com/syv-ai/qwen38-27b-rtx3090/issues/22). I run it on my single 3090 in CachyOS and I’m very happy with the speed, quality and stability. Wish it could run Gemma 4 31B in addition to Qwen 3.8 27B, but I’m definitely not complaining! :)

- by [unknown](#) **&#x21C5; 1**
  <br/> running this on dual 3090 each one instance gpu0 and gpu1

- by [unknown](#) **&#x21C5; 2**
  <br/> If your looking for more context and speed I have a dflash2 vllm recipe that does 200 t/s on code and gives 325k pool but 240 at f8 ain’t bad. My mtp version does 400k pool tho and scales concurrently at about 100t/s worth a shot. I’m going to read this fable level multi agent post now

- by [unknown](#) **&#x21C5; 1**
  <br/> [https://github.com/seanyourhighness/vllm-sm12x-nvfp4-dflash2](https://github.com/seanyourhighness/vllm-sm12x-nvfp4-dflash2)

- by [unknown](#) **&#x21C5; 1**
  <br/> Cool project, starred, I'll check it out soon.

- by [unknown](#) **&#x21C5; 2**
  <br/> Can someone create a version of Ninfer for RTX 5070 Ti?

- by [unknown](#) **&#x21C5; 1**
  <br/> thats like 22gb

- by [unknown](#) **&#x21C5; 2**
  <br/> It coooooks

 
      [](https://preview.redd.it/ninfer-and-a-5090-with-3-8-27b-is-making-me-cry-tears-of-v0-shhxg9ronzmh1.png?width=916&format=png&auto=webp&s=9596054b8fbbbde67195362b96e8cff0b921fcea)

- by [unknown](#) **&#x21C5; 1**
  <br/> Is that an ninfer-graph, or how do u get those stats/plots?

- by [unknown](#) **&#x21C5; 2**
  <br/> Ninfer emits logs. I ingest them and draw.

Qwen and cursor have made me this. Full runtime metrics from my rigs

- by [unknown](#) **&#x21C5; 1**
  <br/> Does Ninfer support multi-GPU and yarn?

- by [unknown](#) **&#x21C5; 1**
  <br/> Anyone tried dual with different gpus? Got a 5060Ti and a 4070S here, idk if 4070S supports it :(

- by [unknown](#) **&#x21C5; 1**
  <br/> Check out [this project](https://github.com/syv-ai/qwen38-27b-rtx3090/issues/22) and my comment above.

- by [unknown](#) **&#x21C5; 1**
  <br/> Sorry, but I didn't find a comment talking about different VRAM between GPU's, I've read that vllm doesn't support that configuration?

- by [unknown](#) **&#x21C5; 1**
  <br/> Sorry I can't help you with that, I only have a single 3090. I thought that project would be worth investigating for you. Too bad if vLLM doesn't support GPUs with different amounts of VRAM.

- by [unknown](#) **&#x21C5; 1**
  <br/> Jealous M4 Max user here... I'm running at hardly 20tps (bf16)

- by [unknown](#) **&#x21C5; 1**
  <br/> Sorry for sounding dumb but is it available for windows? I see it for Linux operating system.

- by [unknown](#) **&#x21C5; 5**
  <br/> The original is Linux only. You can use natpate's fork [https://github.com/natpate/ninfer-windows](https://github.com/natpate/ninfer-windows)

- by [unknown](#) **&#x21C5; 1**
  <br/> using this portable. insanely fast for coding

- by [unknown](#) **&#x21C5; 2**
  <br/> it works fine in wsl

- by [unknown](#) **&#x21C5; 2**
  <br/> I use it in windows with docker. Had an ai made a Windows fork but just switched to docker so i don't need ai to port every new Update to windows

- by [unknown](#) **&#x21C5; 1**
  <br/> Can't wait for rdna5 to get something similar on AMD cards.

- by [unknown](#) **&#x21C5; 1**
  <br/> Holy fuck I’m switching to Linux. I’m only getting 70 token/sec on windows

- by [unknown](#) **&#x21C5; 1**
  <br/> what is your pp speed?

- by [unknown](#) **&#x21C5; 1**
  <br/> that's great but unfortunately for me it failed my first task that was no problem for qwen3.5-opus-4.6 distilled 30B. Testing their latest 120B 3.8 Next model....

- by [unknown](#) **&#x21C5; 1**
  <br/> Ninfer and its forks are truly what's made Qwen 27B viable for me in any way shape or form as a sometimes-alternative to the frontier pay-models.

However, after getting over the rush of its t/s stats, **make sure** you verify you are not getting big-ass cache misses during real-world use!

I noticed that [https://github.com/UDPSendToFailed/ninfer-4090/commits/feat/rtx-4090-sm89-native/](https://github.com/UDPSendToFailed/ninfer-4090/commits/feat/rtx-4090-sm89-native/) has made a series of commits recently addressing this. I need to revisit that project again.

- by [unknown](#) **&#x21C5; 1**
  <br/> Im new around here, what front end you use to feed the end point? WebUI?

- by [unknown](#) **&#x21C5; 1**
  <br/> **Setup:**

  - GPU: RTX 5090 (32GB VRAM, Blackwell/SM120)
  - CPU: Ryzen 9 9950X3D
  - PSU: ASUS ROG Strix 1200W Platinum
  - Power limit: 530W, clock locked to 700-2700MHz (fixed real shutdown issues under combined CPU+GPU load, power limiting alone wasn't enough, needed the clock lock specifically)
  - Host: DietPi on Proxmox, Docker Compose orchestration via Komodo
  - Inference engine: NInfer (Neroued/ninfer), a purpose-built C++/CUDA engine, sm120a-only, built from source
  - Router: llama-swap in front of everything

**Models running via NInfer:**


      
        
          
              Model
            
              Weight profile
            
              Size
            
              Context
            
              KV dtype
            
        
        
      

      
        
            
                Qwen3.8-27B (groupwise)
              
                Q4/Q5/Q6 mixed
              
                16.67 GB
              
                262,144 tokens
              
                int8
              
          
            
                Qwen3.8-27B (groupwise, vision)
              
                same, vision on
              
                16.95 GB
              
                65,536-262,144 tokens (tested at various points)
              
                int8
              
          
            
                Qwen3.8-27B (NVFP4)
              
                mixed NVFP4/FP8
              
                21.5 GB
              
                131,072 tokens
              
                int8
              
          
      
    **Throughput (real production traffic, not synthetic benchmarks):**

  - **Groupwise profile**: decode 145-233 tok/s sustained across hours of real agentic tool-calling sessions. Largest single generation: 38,855 tokens in one response, no crash.
  - **NVFP4 profile**: decode 130-230 tok/s, essentially matching the groupwise profile despite the different weight format. Largest single generation: **61,180 tokens** in one response (current record across every profile I've run).
  - Speculative decoding (MTP, draft window 3) acceptance rate varies a lot by content, roughly 45-100% depending on how predictable the generated text is (code and structured tool calls accept much higher than freeform prose).
  - Prefix-cache reuse on continuing conversations (once working correctly, see caveat below) cuts time-to-first-token dramatically, one real example: a 26,140-token prefix reused with a 153ms TTFT on the next turn, versus several seconds if recomputed from scratch.

**One real gotcha worth mentioning if anyone else runs NInfer**: hit a genuine engine bug where prefix reuse silently failed for every plain OpenAI-protocol request (anonymous/no session-key), despite the setting showing enabled. Fixed upstream in commit `e0829866` ("restore anonymous prefix reuse"), confirmed and resolved by bumping to current `master`.

- by [unknown](#) **&#x21C5; 1**
  <br/> Can Ninfer run any NVFP4 quant? I'm using one that keeps Q8 for the full attention layers. I haven't benched it but definitely better than the UD Q4 XL from Unsloth.

- by [unknown](#) **&#x21C5; 1**
  <br/> No

- by [unknown](#) **&#x21C5; 1**
  <br/> What effort? I just set it up with DeepSeek harness and getting maybe 40 tok/s average on xhigh. I'm running it on 5090 but via WSL Ubuntu in Windows, not sure if that does have impact on CUDA..

- by [unknown](#) **&#x21C5; 1**
  <br/> anyone using vision with ninfer? i'm just using it for coding, crazy fast. trying to get vision running.

- by [unknown](#) **&#x21C5; 1**
  <br/> This is my set up on my 5090 now, it's fine, not crazy fast all the time but still freaking fast

command: >

ninfer-serve /models/qwen3_8_27b_nvfp4.ninfer

--model-id qwen3.8-27b-nvfp4

--host [0.0.0.0](http://0.0.0.0)

--max-context 240000

--kv-capacity 240000

--max-concurrency 2

--kv-dtype fp8

--host-kv-mib 16384

--spec mtp --draft-tokens 3

--lm-head-draft

--vision

--media-live-mib 2048

--preserve-thinking

- by [unknown](#) **&#x21C5; 1**
  <br/> I can run qwen3.8-27b at Q8 on llama.cpp for about 95k context on q8_0,q8_0 and get very decent speed on my 5090. What is the hit to accuracy of dropping to nvfp4 which seems to be what ninfer supports?

- by [unknown](#) **&#x21C5; 2**
  <br/> If being used in a harness like Hermes or DSH with thinking at x-high, it gets the job done just fine, imo unless you can run the full fat weights then NVFP4 is good enough when set up properly, dollars to donuts

- by [unknown](#) **&#x21C5; 1**
  <br/> my current set of parameters which works nicely for me are (sharing in case this helps anyone else): /ninfer/build/apps/ninfer-serve models/qwen3_8_27b_nvfp4.ninfer   --host [127.0.0.1](http://127.0.0.1)   --port 1234   --max-context 131072   --kv-capacity 131072   --prefill-chunk 4096 --max-concurrency 1   --spec mtp   --draft-tokens 5   --lm-head-draft   --kv-dtype int8   --preserve-thinking --device-state-slots 3 --host-kv-mib 2048 --vision

- by [unknown](#) **&#x21C5; 1**
  <br/> how much RAM you have?I tried your settings, also setting "--max-concurrency" to "1", and I can't get more than 114 t/s

- by [unknown](#) **&#x21C5; 1**
  <br/> I see ninfer-serve using 11.5 GB memory. In my sythentic benchmark, I hit 200 tps with vision off. I have not tried vision yet.

For actual agentic coding turns I often see ~150 tps.

- by [unknown](#) **&#x21C5; 1**
  <br/> How are you getting 220 tokens with that command? Especially with max-content being 240000 AND --vision enabled? I'm using:

ninfer-serve models/qwen3_8_27b_nvfp4.ninfer   
--model-id qwen3.8-27b-nvfp4   
--host 0.0.0.0   
--max-context 210000  
--max-concurrency 2   
--kv-dtype fp8   
--host-kv-mib 16384   
--spec mtp 
--draft-tokens 3   
--lm-head-draft
--visionAnd averaging 140 tok/s

Running this via WSL in Windows 11 in DeepSeek Harness, but it shouldn't really have that much influence on the tok/s IMHO. Any clues?

- by [unknown](#) **&#x21C5; 1**
  <br/> Linux maybe

- by [unknown](#) **&#x21C5; 1**
  <br/> It relies on kv cache quanting...
