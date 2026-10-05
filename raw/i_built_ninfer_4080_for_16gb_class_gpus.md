# I built Ninfer 4080 for 16GB class GPUs [Visit](https://www.reddit.com/r/LocalLLaMA/comments/1wwv0fj/i_built_ninfer_4080_for_16gb_class_gpus/)
### **Subreddit:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA)
### **Author:** [u/roofkid](https://www.reddit.com/user/u/roofkid/)
### **Vote:** 55
---
Hi everyone,
TL/DRI created NInfer 4080 to run ISTA-DASLab-Qwen-3.8-27B-GSQ at 100k context on an RTX 4080 16GB GPU using way more of the hardware capabilities (**max overall: 2720 tok/s prefill, 262 tok/s generation**) and sharing it with the community now so others can also have the benefit.
[https://github.com/roofkid/ninfer-4080](https://github.com/roofkid/ninfer-4080)
Full VersionAfter seeing all the amazing work done in the community creating Ninfer 5090, 4090 and 3090 I admit I was a little sad to not being able to use any of it on my RTX 4080 with only 16GB of memory. I still had about $13 of credits sitting idle on the DeepSeek platform as I never expected how much usage I would get out of it.
For context I have over 20 years of experience in Software Engineering and Architecture, but have no experience whatsoever in GPU Kernel development, so this was a very interesting pet project also from a professional experience for me. Mainly because I can read and understand C++ but could not *judge* the actual Kernel code. So I approached it from a product owner and requirements perspective only, made sure good software engineering practices are followed and only made "business decisions".
I've been actively following the local LLM community for the last 2-3 years, probably have tried out all models I could over that time and followed the progress with amazement like many of you.
Guiding principles- Fit into RTX 4080 16GB GPU
- Use ISTA-DASLab-Qwen-3.8-27B-GSQ -> Reasoning can be seen in the ByteShape article, really good for the size and they claim even better accuracy than much larger Unsloth UD quants: [https://byteshape.com/blogs/Qwen3.8-27B/#96-gb-rtx-pro-6000](https://byteshape.com/blogs/Qwen3.8-27B/#96-gb-rtx-pro-6000) I also have very good personal experience with it, it is my daily driver
- Use DFlash2 speculative decoding
- Reach 100k+ context
- Significantly improve prefill and token generation speeds to utilize the hardware better than general purpose inference engines like llama.cpp or vllm
- Measure after changes to also ensure accuracy remains, I also have a M4 48GB available to test higher quants for comparisons, though of course that is much lower speed
- Use DeepSeek V4.1 Flash for the work for cost efficiency
- Use Pi as the harness (only non-cosmectic extensions: hashline edit pro, internet search with ketch through local SearXNG with a self-written skill)
- Runtime also available as a Docker image so it's easy for folks to run
Results
Depth
Prefill t/s (DFlash2)
MTP3 decode t/s
DFlash2 K=7 decode t/s
8K
2719.9
151.2 (100%)
166.7 (54.0%)
32K
2424.9
141.7 (100%)
262.3 (100%)
64K
2125.5
130.7 (100%)
239.1 (100%)
98K
1895.1
122.3 (100%)
212.7 (98.2%)
In real work I really do see the high prefill numbers (2k+) if the prompt is long enough and about 150-200 decode speed on coding and 100ish on prose. It subjectively feels significantly faster than beellama (my previous daily driver) at the same benchmark results. I mainly used MBPP and HumanEval as I needed something that I can run reasonably fast (~30min). MBPP stays in 90-92% territory and HumanEval at 95-96%. Please be realistic and do expect tiny degradations that are within measurement noise. They are mainly coming from KV quantization according to my measurements so you can always trade context for accuracy if needed by switching.
What I learned- It is absolutely mental how much performance is left on the table by using the general purpose engines. From a bird's eye view it's totally understandable as we trade the wide support for performance, I just didn't expect how much that would be. When I saw the first memory throughput measurements being in the 200 GB/s range and having a theoretical maximum of 720 GB/s in the device my jaw dropped because of the low efficiency back when I started
- I think in the community we've all seen more specialized inference engines making significant performance improvements possible. vllm-radiance for R9700, NInfer variants for CUDA, Splash for Metal - with software creation becoming cheaper and cheaper I expect more of this for and from our "tinkerer" group here
- Spending about 2 billion tokens for this work for only $13 is just crazy (only off-hours). Low cache read tokens costs on agentic work are so much more important than even I expected. It's the classic difference between cognitively fully understanding how LLM turns work and seeing big data results. The reality is that with THAT kind of pricing I think I pay more for electricity to get the same amount of tokens out
- I went back to xhigh thinking on Qwen 3.8 27B as the speed is so high, that I don't really care/notice. I've also hidden the thinking blocks again as I cannot follow any more anyway
- The prefill speed really caught me of guard. I was really floored when I tried it in Pi after the first big improvements were done and it IMMEDIATELY answered with token streaming. I was so used to waiting 5-10s without a cached system prompt. I significantly underestimated how important that is for the user experience. Feels like a cloud endpoint to me now.
- At these high prefill speeds your context window is full in 40 seconds, definite "oh my god" moment for me when that happened the first time
- Reaching 100k context means significant KV compression as full 256k context F16 needs exactly 16GB of VRAM on Qwen 3.8 27B. I was too afraid of "high" (4bit style) KV compressions. So many advances have been made here. Originally I never went below Q8_0. I then used kvarn5/kvarn5 previously on beellama after benchmarking and cannot measure a noticeable difference to the now used rk4v4-e8 variant used here. I think good software engineering practices are way more important and catch problems that might come from it. Also subjectively I do not experience a "fast garbage" phenomenon here
ConclusionFor me this is a good version 1 and I don't intend to spend significant effort on this for Qwen 3.8 27B. It's at the pareto 80% state. I just want to be happily using it now and reap the rewards. I hope you are too! Of course when Qwen 4 27B comes around soon I will check it out again.
If you have another 16GB RTX 4xxx card I would be interested in knowing if that works on them too and what speeds you're seeing. I honestly can't judge how tied to the RTX 4080 hardware it is. If you have a 4080, enjoy :)
Shoutouts- Every person who worked on NInfer before me, you guys rock and provided a stable base for me to fork from
- Special hats off to sergiuszm who created NInfer-4090, I think you did all the heavy lifting for SM_89 already
- ISTA-DASlab for their work on GSQ and providing the safetensor checkpoint for it! Cheers to Austria from Germany :) Love seeing important contributions to the community from the EU
---
## Comments 54

- by [unknown](#) **&#x21C5; 6**
  <br/> How easy would this be to get to work on a 3080?

- by [unknown](#) **&#x21C5; 1**
  <br/> I have exactly the same answer to you as to PointlessDrivel regarding 5080. I wrote a longer comment here: [https://www.reddit.com/r/LocalLLaMA/s/BvxYFWJH5p](https://www.reddit.com/r/LocalLLaMA/s/BvxYFWJH5p)The 3xxx series cards are all sm_86 compute instead of sm_89 compute for 4xxx cards and sm_120 compute for 5xxx series cards.

So for 4xxx 16gb cards there’s a good chance this will work just straight out of the box, just slower because of slower hardware speeds but with similar gap to the common runtimes. For 3xxx and 5xxx 16gb cards the comment above applies.

- by [unknown](#) **&#x21C5; 1**
  <br/> I eventually did manage to fanagle it to work and sadly didn't buy me any meaningful additional speed sadly. Given I know nothing about inference engines perhaps someone smarter will come along to figure it out at some point.

- by [unknown](#) **&#x21C5; 1**
  <br/> Thank you for attempting it and reporting back! User catch23 posted about [https://github.com/iamwavecut/ninfer-all](https://github.com/iamwavecut/ninfer-all) - maybe this can help. I have not tried it and just learned about the project today from this thread.

- by [unknown](#) **&#x21C5; 1**
  <br/> I decided to keep trying it out. My computer might have been heat throttling before I guess. It does climb up to around 33-40tps on some statistical coding which is a fair bit faster than I have ever gotten it to run on llama.cpp in LM studio. Took about half a day I would say. I'll keep it around and compare it to Qwen3.8 FN. Thanks for your work 🙏🏿

- by [unknown](#) **&#x21C5; 5**
  <br/> I would be super interested in this for a 5080. I found the base ninfer for 5080, but it wasn't using the  GSQ RCO quant that's become my daily driver.

- by [unknown](#) **&#x21C5; 4**
  <br/> I added a “quantization” recipe for GSQ from the base safetensor checkpoint that ISTA-DASlab has published here: [https://huggingface.co/ISTA-DASLab/Qwen3.8-27B-3Bit-GSQ](https://huggingface.co/ISTA-DASLab/Qwen3.8-27B-3Bit-GSQ) to convert it to ninfer format. It doesn’t touch the weights, just converts format, so everything is left intact. Vision Tower, MTP head and the DFlash2 from z-lab are also included in the ninfer artifict and activated depending on how you start the runtime.

The main work was all around added Q3 CUDA kernels to ninfer. Naturally there were none. Everything focused on NVFP4 and higher so far. There are roughly 30 semantic commits on the rtx4080-port branch following the evolution I took. You can have a model take a look and see how they can be ported over to sm_120 hardware. I have no clue how backwards compatible the hardware is and how easy that would be. Could be as easy as copy & paste to serious work.

Bear in mind that this it not including RCO. My understanding is that this checkpoint was the basis for their GGUFs. I do not know enough technical details but in the model conversations it came up that there might not be so much value because from the benchmarks this is as good as the GGUF values so I did not follow up further.

- by [unknown](#) **&#x21C5; 2**
  <br/> That's fascinating! I appreciate the feedback and insight, as well as your time. I'll play around a bit with some models and see if I can get it compatible. Thank you again!

- by [unknown](#) **&#x21C5; 3**
  <br/> Got a repo with NVFP4 and EXL3 optimisations for the 5080, albeit for Gemma4 models. Maybe an agent finds something useful in it for Qwen3.8 as well, spent several weeks optimising the kernels: [https://github.com/Danmoreng/gem16](https://github.com/Danmoreng/gem16)

- by [unknown](#) **&#x21C5; 1**
  <br/> That's so cool :) Thank you for sharing! I love gemma models for prose.

- by [unknown](#) **&#x21C5; 1**
  <br/> Well, currently it is locked to the Blackwell architecture. Should be possible to make it work for 40series, but definitely needs some changes since sm120a currently is required.

- by [unknown](#) **&#x21C5; 1**
  <br/> That's awesome. I'll check that out too. Thank you!

- by [roofkid](https://www.reddit.com/user/roofkid/) **&#x21C5; 2**
  <br/> [u/roofkid](/user/roofkid/), thanks for your efforts.

I just tried it on an RTX 4060Ti 16GB, my secondary card in a PCIe 3.0 x1 slot.

Core clock: 2.3GHz, Memory clock: +1250MHz

Undervolted: 0.850mV, Power Limited: 123W

Initially, the server hung at "Creating CUDA graphs"; with the --no-cuda-graph flag, it went ahead but hung at "Warming up".

Turns out in the dual-GPU setup, I had to set the visible devices flag first.

set CUDA_VISIBLE_DEVICES=1

build\apps\Release\ninfer-serve.exe models\qwen3_8_27b_gsq3.ninfer ^
  --host 127.0.0.1 --port %PORT% --device 0 ^
  --max-context 92160 --kv-capacity 92160 ^It fails to allocate memory at a 100k context for me with vision enabled.

I ran some basic tests when about 40-50% of the context was used up.

Prose: 66 tok/s decode & 1050 tok/s prefill

Coding: 96 tok/s decode & ~800 tok/s prefill

- by [unknown](#) **&#x21C5; 1**
  <br/> Thank you for reporting those numbers! Those are also really good numbers considering everything. Even crazier if you consider you mentioning that llama.cpp is only at 20-30 for you with MTP. Is that with MTP or DFlash2 on ninfer? Regarding 100k context: seems you are on Windows. If I have a browser open I also won't get to 100k. It's really that tight. I also don't have a GPU in my CPU, so I can't free up the 800MB from the Desktop Window Manager either. If you have one - plug your monitor into your mainboard and you will have more free memory on the GPU.

- by [unknown](#) **&#x21C5; 2**
  <br/> anyone tried this on 4060ti?

- by [unknown](#) **&#x21C5; 2**
  <br/> Yes, it works, just tried right now on RTX 4060Ti 16GB, though my total context only goes up to 92k.

- by [unknown](#) **&#x21C5; 1**
  <br/> awesome, what speeds are you getting compared to upstream llamacpp

- by [unknown](#) **&#x21C5; 2**
  <br/> just posted as a comment here: [https://www.reddit.com/r/LocalLLaMA/comments/1wwv0fj/comment/pdvtr45/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button](https://www.reddit.com/r/LocalLLaMA/comments/1wwv0fj/comment/pdvtr45/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)

It's much faster than llama.cpp, no fork, it was around 25-30 t/s with MTP as 3 for coding depending on the context, the prefill was slow too, maybe I did not optimize the config better, but this is much much faster.

If you have not limited/underclocked your 4060Ti, it might have even better speeds.

- by [unknown](#) **&#x21C5; 1**
  <br/> Thank you for trying it! I’m so happy. I assumed it would work on all 4xxx cards with 16gb memory but didn’t want to oversell anything 😊

- by [unknown](#) **&#x21C5; 2**
  <br/> Can you share the result on decoding without speculation? I am getting on 4060Ti. While the MTP3 seems matching my expectation (50%), the no speculation seems low.


      
        
          
              Result
            
              Decode speed
            
        
        
      

      
        
            
                4060 Ti, no speculation
              
                20.17 tok/s
              
          
            
                4060 Ti, MTP3
              
                70.98 tok/s
              
          
            
                4080, MTP3 reference
              
                151.2 tok/s

- by [unknown](#) **&#x21C5; 1**
  <br/> Yes, here you go. This is an apples to apples comparison to the MTP and DFlash2 results above, so greedy decoding as well. Interestingly these decode numbers are exactly the ones I also get in llama.cpp when also using greedy decoding. So it seems as if the real magic is coming from speculative decode. Thank you for asking me about this, learned something important again today :)


      
        
          
              Depth
            
              Prefill t/s
            
              No-spec decode t/s
            
        
        
      

      
        
            
                8K
              
                2770.97
              
                41.28
              
          
            
                32K
              
                2473.53
              
                39.44
              
          
            
                64K
              
                2160.35
              
                36.81
              
          
            
                98K
              
                1917.89
              
                32.88

- by [unknown](#) **&#x21C5; 2**
  <br/> Hey, I don't have a good understanding of these programs, but I wanted to ask a stupid question: are they hyper-specialized for one exact kind of hardware, like the 4080, or is it mainly about VRAM, in which case I could hypothetically use it for my 5070 Ti? I know Ninfer is for 5090's, but they have 24 GB, so I'm not sure if that's the main difference.

- by [unknown](#) **&#x21C5; 1**
  <br/> Hey there are no stupid questions! Perfectly OK to ask. I hope it's ok to try answering ELI5 style.

So there are three main differences between GPU generations. Let's focus on 3xxx, 4xxx and 5xxx for now. You can think of it like this:

The compute part (the GPU chip) will have more features. As an analogy you could say that 3xxx can add. 4xxx can add and multiply and 5xxx can add, multiply and divide. Of course all GPU chips can do these simple things but you get the idea. So you can do more things with newer GPU chips that you just couldn't do before.

The generations usually share the same basic capabilities, to keep the analogy all 4xxx chips can add and multiply but at different speeds.

Second difference is how much VRAM you (can have) and third is how fast you can transfer in and out of VRAM to your GPU chip (called memory bandwidth).

This is also why there's a really good chance that ninfer-4080 will also work fine on a 4070ti 16GB without any changes, it will just be a bit slower. I just don't have that card and can't prove it, which is why I didn't make any claims.

With all that background information maybe my original comment here will now also make sense to you: [https://www.reddit.com/r/LocalLLaMA/s/BvxYFWJH5p](https://www.reddit.com/r/LocalLLaMA/s/BvxYFWJH5p)

- by [unknown](#) **&#x21C5; 2**
  <br/> Thanks, looks great! Will try to make a Windows fork of your repo when I have time (unless somebody will make it by the moment I have it 😂 ).

- by [unknown](#) **&#x21C5; 1**
  <br/> Thank you. Feel free 😊 At the same time I do develop and run it on Windows myself. You can either launch it via Docker or also compile the source. Whatever floats your boat.

- by [unknown](#) **&#x21C5; 2**
  <br/> Wow! Didn't realize that Docker on Windows can passthough a GPU. That makes my life so much easier! Thank you!

- by [unknown](#) **&#x21C5; 1**
  <br/> You're very welcome, enjoy :)

- by [unknown](#) **&#x21C5; 2**
  <br/> My man!I’ll be trying this soon.

How does on go about doing this kind of work? I’d like to tune some very old amd cards.

- by [unknown](#) **&#x21C5; 1**
  <br/> I’m happy you want to give it a try 😊

Regarding working on it - it was a classic engineering process I would say. I started with a conversation with grill-me skill with the list of guiding principles you see above to come up with some plan.Important is to follow test driven development if you have no way of knowing if the work itself is good or bad.I didn’t mention this above but there were also many ideas that the models had which should have been a performance improvement but ended up being rejected because they were a tie or lowered the performance.Then one idea at a time and slowly work through it. You can read the port ledger and rtx 4080 plan documents. But this is an ai maintained document, be aware.Took me about 2 weekends

- by [unknown](#) **&#x21C5; 1**
  <br/> so you had no personal understanding of the technical of coding to the hardware? That's what I'm asking about.

I, also, have my llms do web research and testing on my machine for A/B testing to get the most optimized result but it's not creating the code to specifically optimize the llms to the specific hardware. It's just applying the research it finds and testing if it's valid... and yes, most results it finds have zero or negative benefits. Near all, I would say.

- by [unknown](#) **&#x21C5; 2**
  <br/> I think I've written one piece of CUDA code in my life in some tutorial. At the same time I would say I have a reasonably good conceptual understanding of LLMs and the hardware in the GPU and as mentioned in my post: I have over 20 years of experience in software engineering and architecture as well as using agentic software engineering practices (won't oversell that, I think the whole world is still learning how to do that well). So that definitely helps from an engineering standpoint.

- by [unknown](#) **&#x21C5; 1**
  <br/> how would someone learn how to tune a gpu to an llm outside of standard vibecoding?

- by [unknown](#) **&#x21C5; 2**
  <br/> How did you make the ista model work on ninfer? There's a 5080 ninfer project as well, and i'd love to try it out on my 5070ti, but it's using a custom quant and not the ista one which i really like.

- by [unknown](#) **&#x21C5; 1**
  <br/> Hey, someone else also asked about this and I wrote a comment about it here: [https://www.reddit.com/r/LocalLLaMA/s/BvxYFWJH5p](https://www.reddit.com/r/LocalLLaMA/s/BvxYFWJH5p)

- by [unknown](#) **&#x21C5; 2**
  <br/> Would this potentially work on 4070ti?

- by [unknown](#) **&#x21C5; 2**
  <br/> Hey, I think it should work, just run a bit slower. The performance gap to llama.cpp and friends should be similar. Please try it, I’m really curious myself what other 4xxx 16gb cards can use this. I only own the one card.The 4070ti is also sm_89 and you have the same 16gb vram, just slower memory bandwidth and less compute. It should run, just not as fast.

- by [unknown](#) **&#x21C5; 2**
  <br/> Thank you for the answer and thank you for making this!

I thought so, since it the same architecture (sm_89). My card is 12gb, I guess the main change will be the model size, launching settings and context amount I can push in it.

I will try it later on, thanks again <3

- by [unknown](#) **&#x21C5; 1**
  <br/> Oh, I didn't know that there are also 12gb 4070ti, whoops.

Give it a try, the worst that will happen is that it doesn't work. You probably should use MTP then, because DFlash2 is significantly larger memory consumption. If you can live with text only that will also save VRAM. There's some run scripts in the scripts folder that you can inspect to check how to start: [https://github.com/roofkid/ninfer-4080/blob/rtx4080-port/scripts/run-ninfer-4080.bat](https://github.com/roofkid/ninfer-4080/blob/rtx4080-port/scripts/run-ninfer-4080.bat) line 144+

- by [unknown](#) **&#x21C5; 2**
  <br/> I'm using [https://github.com/iamwavecut/ninfer-all](https://github.com/iamwavecut/ninfer-all) -- pretty easy to ask the clanker to make it so.  I can still run a swift-bonsai-2 model that fits in 12gb along with 100k context.  I'm running my 4070ti connected to a spare m.2 port on my strix halo and still getting prefill around 3k and tg around 150 with mtp.

- by [unknown](#) **&#x21C5; 1**
  <br/> Oh this is so cool. I wasn’t aware of this project. Thank you for sharing it. Will check it out 😊

- by [unknown](#) **&#x21C5; 1**
  <br/> Nice work, thank you!!

Would you consider doing a 4080 ninfer port of Strata Gwen flash next please?

[https://github.com/Niko1221/Strata](https://github.com/Niko1221/Strata)

- by [unknown](#) **&#x21C5; 1**
  <br/> Honestly I think the people working on Strata have absolutely knocked it out of the park. I don't think there's much more to gain than what they have achieved. You can just use it today with your 4080 and be happy if you have enough system ram :)

As far as I understand the focus everything around NInfer is focused around having everything in VRAM. This is not the case for Strata where they heavily worked on offloading to RAM and disk.

- by [unknown](#) **&#x21C5; 1**
  <br/> I see. Quite a few users having looping issue with Strata. Hope Niko can find a way around it

It's the million dollar question as always: Heavily lobotomised frontier Vs Model that can fit..

Thank you anyway. Awesome to be able to use ninfer on 4080. I no longer feel left out not having a flagship gpu!

- by [unknown](#) **&#x21C5; 1**
  <br/> Very interesting. I may try it on my 5060ti 16g.

- by [unknown](#) **&#x21C5; 1**
  <br/> You can give it a try but I don't think it will start as your GPU is from the 5xxx series. There was another person also asking about this and I replied here: [https://www.reddit.com/r/LocalLLaMA/s/BvxYFWJH5p](https://www.reddit.com/r/LocalLLaMA/s/BvxYFWJH5p)

- by [unknown](#) **&#x21C5; 1**
  <br/> will this work on 5060/5070/5070ti?

- by [unknown](#) **&#x21C5; 1**
  <br/> On my GTX 980 it will run?

- by [unknown](#) **&#x21C5; 1**
  <br/> Unfortunately not. This is for RTX 4xxx cards with 16GB VRAM and validated on my 4080.

- by [unknown](#) **&#x21C5; 0**
  <br/> how much performance is left on the table by using the general purpose engines


    Maybe for prefill but not for decode. I found that most of these custom engines compromise with a quantized kv cache

I’ve done my own roofline analysis and iterated with claude for a week investigating llama.cpp performance for r9700. All I came up was under 5% decode improvement

- by [unknown](#) **&#x21C5; 4**
  <br/> These speeds are way faster than can be achieved on a typical 4080 I think

- by [unknown](#) **&#x21C5; 2**
  <br/> For real

- by [unknown](#) **&#x21C5; 1**
  <br/> That’s really interesting that you had this experience with decode. Did you ever try vllm-radiance for your r9700? That seems to be a huge step up and a very thoughtful group of people working on that.What does decode speed have to do with kv cache quantization from your point of view? I can go to int8 kv cache, only get 50k context but still get the exact same speed. There’s no connection between decode speed and kv cache quantization from what I can observe and measure. Of course the model will perform better. Int8 > rk8v4a-e8 > rk4v4-e8 in terms of accuracy from my measurements.
