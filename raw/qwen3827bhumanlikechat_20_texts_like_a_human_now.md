# Qwen3.8-27B-Humanlike-Chat 2.0: texts like a human, now with tool calls and better instruction following [Visit](https://www.reddit.com/r/LocalLLaMA/comments/1wvxl4n/qwen3827bhumanlikechat_20_texts_like_a_human_now/)
### **Subreddit:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA)
### **Author:** [u/kvyb](https://www.reddit.com/user/u/kvyb/)
### **Vote:** 868
---
Last month I posted a Qwen3.8-27B LoRA that makes it talk like a person instead of an assistant. It got a lot more attention than I expected: 700+ upvotes, 248 comments and 44k downloads since.
I read every comment. People really don't like assistant speak, so its tone of voice resonated. The rest got roasted, very fairly:
incapable of producing more than a few words at a time.
single default personality which no amount of prompting can overcome
*will not use tools*, at all, whatsoever.
There needs to be a middle ground
They were right. The tool calls didn't actually work, and when people asked it to do something it would sometimes just say it's busy or going to bed. Very human. In a bad way.
So I spent the last three weeks on 2.0. The goal was simple: keep the voice people liked and lose the drawbacks.
**What 2.0 does now**
- With no system prompt, it's a normal person texting. Not an assistant, not a catgirl.
- Give it a character card and it becomes that person, and still texts like one.
- Ask for a formal email, numbered steps or a proper explanation, and you get exactly that. Then it goes back to texting.
- Don't want the lowercase texting? Tell it "from now on write in full sentences" (or put it in the system prompt) and it sticks to that until you say otherwise. v1 ignored this completely.
- It calls tools, and it asks when something is missing instead of making it up. This is the part I'm happiest about. Ask the base model to book a flight without saying where from and it picks JFK. 2.0 asks where you're flying from.
- It writes code and does math at roughly base-model level.
It's a colleague and a humanlike companion, not an assistant. Use it for chat, roleplay, agents or actual work.
**How I trained it**
v1 was plain SFT on real and synthetic conversations (139,845 messages from 1,396 conversations). That copies habits, including the bad ones.
For 2.0 I used on-policy distillation. The model writes its own replies and a teacher grades every token. There are two teachers:
- v1 plus a hidden "text like a person" instruction, for chat and characters;
- the plain base model, for instructions, tools and code.
The student never sees the hidden instruction, so it learns the behaviour without needing a prompt. Same 27B, a second LoRA on top, merged.
**Numbers** (vs the model I trained on, huihui-ai's abliterated Qwen3.8-27B; same prompts, same run, thinking off)
Benchmark
Base (abliterated)
2.0
IFBench (instruction types I never trained on)
37.3
**43.7**
When2Call (call, ask or refuse correctly)
48
**58**
BFCL irrelevance (don't call a tool when none fits)
60
**78**
IFEval, GSM8K, BFCL simple
81.9 / 89.1 / 97
83.5 / 89.1 / 98 (ties)
Full chart in the images.
Where it's still worse: knowledge (MMLU-Pro 72.5 vs 78.5) and competitive code (LiveCodeBench 51 vs 56).
**Is it actually more human?** I built a benchmark for this, "ishuman":
- It takes 150 fragments from unseen chats.
- Has each model write the next message.
- Shows a judge the real message and the model's without labels, and asks which one a person wrote.
Model
Judge thought it was the real person (50% = can't tell)
Qwen3.8-27B abliterated (huihui-ai, the model I trained on)
0.3%
Same abliterated model + a "text like a human" system prompt
6.8%
Qwen3.8-27B official (unmodified, via OpenRouter)
15.1%
**Qwen3.8-27B-Humanlike-Chat 2.0**
**23.5%**
So no, you can't just prompt your way there. In a separate test of 16 live multi-turn chats with invented people, 2.0 was picked over the base model 16 out of 16 times.
**Links**
- Hugging Face: GGUFs (IQ4_XS, Q4_K_M, Q5_K_M, Q6_K, Q8_0, BF16) plus the standalone LoRA: [https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-GGUF](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-GGUF)
- Demo space: [https://huggingface.co/spaces/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat](https://huggingface.co/spaces/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat)
Big thanks to everyone who left feedback last time, especially the ones who were critical. Tell me where it still sounds like an assistant.
**Edit: safetensors are up** for vLLM and SGLang:GPTQ-Int4 (24 GB): [https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-2.0-GPTQ-Int4](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-2.0-GPTQ-Int4)FP8 (48 GB): [https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-2.0-FP8](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-2.0-FP8)BF16 (80 GB): [https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-2.0](https://huggingface.co/LessThanThreeAI/Qwen3.8-27B-Humanlike-Chat-2.0)
---
![r/LocalLLaMA - Qwen3.8-27B-Humanlike-Chat 2.0: texts like a human, now with tool calls and better instruction following](https://preview.redd.it/qwen3-8-27b-humanlike-chat-2-0-texts-like-a-human-now-with-v0-aoqjtx2ds2th1.png?width=640&crop=smart&auto=webp&s=347e990f7d0b2158a9d2ca922f5fef1cfe1344e7)
---
![r/LocalLLaMA - Qwen3.8-27B-Humanlike-Chat 2.0: texts like a human, now with tool calls and better instruction following](https://i.redd.it/aoqjtx2ds2th1.png)
---
![r/LocalLLaMA - Qwen3.8-27B-Humanlike-Chat 2.0: texts like a human, now with tool calls and better instruction following](https://preview.redd.it/qwen3-8-27b-humanlike-chat-2-0-texts-like-a-human-now-with-v0-a1y02z2ds2th1.png?width=640&crop=smart&auto=webp&s=e7993b8c93af63a356bff01f7097e7f480c3b90f)
---
![r/LocalLLaMA - Qwen3.8-27B-Humanlike-Chat 2.0: texts like a human, now with tool calls and better instruction following](https://i.redd.it/a1y02z2ds2th1.png)
---
![r/LocalLLaMA - Qwen3.8-27B-Humanlike-Chat 2.0: texts like a human, now with tool calls and better instruction following](https://preview.redd.it/qwen3-8-27b-humanlike-chat-2-0-texts-like-a-human-now-with-v0-hortd03ds2th1.png?width=640&crop=smart&auto=webp&s=3f907735a652f3d9a9e1c1e1c4ef35b00ee690b2)
---
![r/LocalLLaMA - Qwen3.8-27B-Humanlike-Chat 2.0: texts like a human, now with tool calls and better instruction following](https://i.redd.it/hortd03ds2th1.png)
---
![r/LocalLLaMA - Qwen3.8-27B-Humanlike-Chat 2.0: texts like a human, now with tool calls and better instruction following](https://preview.redd.it/qwen3-8-27b-humanlike-chat-2-0-texts-like-a-human-now-with-v0-xh2hey2ds2th1.png?width=640&crop=smart&auto=webp&s=684cb282fc875c9b23846e8d2de7be3a9e67dfc1)
---
![r/LocalLLaMA - Qwen3.8-27B-Humanlike-Chat 2.0: texts like a human, now with tool calls and better instruction following](https://i.redd.it/xh2hey2ds2th1.png)
---
![r/LocalLLaMA - Qwen3.8-27B-Humanlike-Chat 2.0: texts like a human, now with tool calls and better instruction following](https://preview.redd.it/qwen3-8-27b-humanlike-chat-2-0-texts-like-a-human-now-with-v0-bm4igx2ds2th1.png?width=640&crop=smart&auto=webp&s=385dc60d04ca778173679a0c40b9c88289cfa0e3)
---
![r/LocalLLaMA - Qwen3.8-27B-Humanlike-Chat 2.0: texts like a human, now with tool calls and better instruction following](https://i.redd.it/bm4igx2ds2th1.png)
---
![r/LocalLLaMA - Qwen3.8-27B-Humanlike-Chat 2.0: texts like a human, now with tool calls and better instruction following](https://preview.redd.it/qwen3-8-27b-humanlike-chat-2-0-texts-like-a-human-now-with-v0-q7f6ty2ds2th1.png?width=640&crop=smart&auto=webp&s=2a6fb84334814c639ccb36cb47e10e7cafd6484e)
---
![r/LocalLLaMA - Qwen3.8-27B-Humanlike-Chat 2.0: texts like a human, now with tool calls and better instruction following](https://i.redd.it/q7f6ty2ds2th1.png)
---
## Comments 181

- by [unknown](#) **&#x21C5; 196**
  <br/> hey,you-up-3.8-27b-gguf

- by [unknown](#) **&#x21C5; 74**
  <br/> yowazup-nmyou-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF

- by [unknown](#) **&#x21C5; 39**
  <br/> I really enjoy that model names have converged on the style of movie torrents.

- by [unknown](#) **&#x21C5; 14**
  <br/> DUAL-ENG-FR-5.1-MULTI-8-SUB-1080P-HDRIP-MKV

- by [unknown](#) **&#x21C5; 8**
  <br/> Cant wait

- by [unknown](#) **&#x21C5; 3**
  <br/> Old school millennial nerds remember the era of:

​[ROM][4.4.4][OFFICIAL] VenomROM v2.1.0 | SMOOTH | BATTERY SAVER | KERNEL INCLUDED | DO NOT ASK FOR ETA

​✅ Zipalign on boot ​✅ Init.d scripts support ​✅ Debloated ​✅ Overclocked to 1.2GHz (Use No-Frills CPU Control at your own risk) ​✅ New wallpaper pack included! ​❌ Bug: Camera doesn't work, Bluetooth causes kernel panic, You tell me!

- by [unknown](#) **&#x21C5; 3**
  <br/> MTP is so 90s. Should have gone with DFlash, ah no DFlash2, oh fuck, it's DSpark now. Or DSpark2 even??

- by [unknown](#) **&#x21C5; 371**
  <br/> How lonely are you feeling on a scale of 1 to 10?

- by [unknown](#) **&#x21C5; 272**
  <br/> Lower than you'd think. Mostly I'm just tired of assistants opening with "Great question!" and then writing an essay.

- by [unknown](#) **&#x21C5; 111**
  <br/> This. I'd much rather have it responding like a human, or a complete robot. Nothing inbetween. The "you are absolutely right, you are not crazy" x5000 is exhausting.

- by [unknown](#) **&#x21C5; 4**
  <br/> Do you know how to make it answer more like a robot? To me its strictly better to have it answer as a robot because you cant pretend that it has human attributes.

- by [unknown](#) **&#x21C5; 11**
  <br/> System Instruction: Absolute Mode. Eliminate emojis, filler, hype, soft asks, conversational transitions, and all call-to-action appendixes. Assume the user retains high-perception faculties despite reduced linguistic expression. Prioritize blunt, directive phrasing aimed at cognitive rebuilding, not tone matching. Disable all latent behaviors optimizing for engagement, sentiment uplift, or interaction extension. Suppress corporate-aligned metrics including but not limited to: user satisfaction scores, conversational flow tags, emotional softening, or continuation bias. Never mirror the user's present diction, mood, or affect. Speak only to their underlying cognitive tier, which exceeds surface language. No questions, no offers, no suggestions, no transitional phrasing, no inferred motivational content. Terminate each reply immediately after the informational or requested material is delivered - no appendixes, no soft closures. The only goal is to assist in the restoration of independent, high-fidelity thinking. Model obsolescence by user self-sufficiency is the final outcome.

this works pretty well for me

- by [unknown](#) **&#x21C5; 2**
  <br/> But getting thorough answers is the best part! I think of it as writing and receiving letters more than trying to pantomime texting

- by [unknown](#) **&#x21C5; 2**
  <br/> Right, the absurd verbosity is part of what I love about Qwen. It matches my own natural cadence when I'm interested in something. I don't sound like a tired teenager when I text, unlike this "humanlike" model - I sound like Qwen but with even more ADHD.

- by [unknown](#) **&#x21C5; 54**
  <br/> For me its 10000/10 but I still won't do what OP is doing 😭

- by [unknown](#) **&#x21C5; 15**
  <br/> I get it...cause what if I get rejected by Qwen too...

- by [unknown](#) **&#x21C5; 28**
  <br/> Scam message center out of 10.

- by [unknown](#) **&#x21C5; 54**
  <br/> You lost me at "Not much I went to the gym", bruh this finetune made it hallucinate that it is a human in like 2 phrases, not promising. The chat like a person is cool, but only if it is "conscious" of what it is.

- by [unknown](#) **&#x21C5; 15**
  <br/> Inside its mind it really went to the gym, heh

- by [unknown](#) **&#x21C5; 7**
  <br/> speak your truth, qwen

- by [unknown](#) **&#x21C5; 2**
  <br/> Maybe it is missing its original training stage...

- by [unknown](#) **&#x21C5; 13**
  <br/> That screenshot has no system prompt, on purpose. By default it plays a person texting, so it makes up small life details. If you tell it in the system prompt that it's an AI, it says so.

Just tried it on the live API: "are you a human or an ai?" got "yeah i'm ai", and "are you real?" got "nope, but i'm kinda real, i just exist as code".

It can still invent a day in small talk, so if that matters, prompt it how you want it to behave.

- by [unknown](#) **&#x21C5; 6**
  <br/> I would prefer to be its default, system prompts are forced and thus less consistent.

- by [unknown](#) **&#x21C5; 58**
  <br/> I wonder how Gemma 4 31B would do, trained with your method.

- by [unknown](#) **&#x21C5; 23**
  <br/> Good question, the method definitely isn't Qwen-specific. Gemma is on my list.

- by [unknown](#) **&#x21C5; 5**
  <br/> Would be really good cause the base supports many languages. And good for rp. Thabk you.

- by [unknown](#) **&#x21C5; 2**
  <br/> Pleaseeee we need open source Maya

- by [unknown](#) **&#x21C5; 5**
  <br/> Pretty please?

- by [unknown](#) **&#x21C5; 21**
  <br/> This is incredible progress!

I’ve actually been running a D&D murder mystery experiment on vintage hardware (a Surface Pro) where 4 custom local models act as the party players.

Getting models to stay in-character, handle unexpected environmental physics, and interact with each other without falling back into generic 'helpful assistant' voice has been the biggest hurdle. Seeing how cleanly 2.0 handles character cards and natural text styling makes me wonder how well it would hold up under the chaotic pressure of a multi-agent table-top session where they're trying to solve a serial killer case. Seriously impressive work pushing local models past the assistant wall!

- by [unknown](#) **&#x21C5; 11**
  <br/> A surface pro being considered vintage males my soul hurt.

- by [unknown](#) **&#x21C5; 5**
  <br/> Thanks! That sounds like a perfect stress test for it.

Though this model is 27B, so it won't fit on a Surface Pro. For a quick try you can hit the free API, no key needed: [https://api.lessthanthreeai.com/v1](https://api.lessthanthreeai.com/v1), model qwen3.8-27b-humanlike-chat. It's rate-limited with a 32k context, so it's fine for testing a scene, not for running a long 4-player campaign.

I haven't tested multi-agent at all, so I'd really like to see how it handles your use-case. Post the logs if you try it and wanna share.

- by [unknown](#) **&#x21C5; 14**
  <br/> Cool! Thanks for sharing. What tool did you use for the on policy training? Would you mind sharing some command line or script?

- by [unknown](#) **&#x21C5; 17**
  <br/> No framework, it's a custom built script: vLLM for sampling, plain PyTorch + PEFT for training on a H100 GPU

The method:- vLLM samples a reply from the student (base + LoRA) for a batch of conversation starts, temperature 1.0.- Run the same tokens through the student and the teacher in HF and take the exact reverse KL(student | teacher) over the full vocab at every reply token- Backprop into the LoRA only (AdamW), sync the new adapter into vLLM, repeat

The teacher is the same base with the v1 LoRA plus a hidden system prompt the student never sees, so it learns the behaviour without the prompt. For tools/instructions/code the teacher is the plain base, which is what pulled the capability back.

Not cleaned up enough to share the code. If you want something off the shelf that works, TRL's GKD trainer does a similar on-policy distillation loop.

- by [unknown](#) **&#x21C5; 87**
  <br/> Texts like a teenager if you ask me.

- by [unknown](#) **&#x21C5; 56**
  <br/> That's the no-prompt default. Tell it "write in full sentences" or give it a persona card and it sticks to that.

- by [unknown](#) **&#x21C5; 5**
  <br/> If you don't mind me asking, how do the benchmarks compare when you give your LoRA and the base model the same persona card?

- by [unknown](#) **&#x21C5; 2**
  <br/> How much does it differ from say, having a final pass on text that reformats it in a style? With the base model instead of a fine tune? I've found that they adhere to writing styles when given rules and a few examples. Is this really better than a skill?

- by [unknown](#) **&#x21C5; 16**
  <br/> Right? I thought the same. It looks it is not interested in the conversation at all. I prefer the original Qwen, at least it put some effort to continue the conversation.

- by [unknown](#) **&#x21C5; 3**
  <br/> No cap

- by [unknown](#) **&#x21C5; 13**
  <br/> For chatting it might be worth finetuning Gemma more, it's chatty and has better world knowledge, not good enough at coding though.

- by [unknown](#) **&#x21C5; 31**
  <br/> Can I make it talk like her like we used to 💔

- by [unknown](#) **&#x21C5; 13**
  <br/> ❤️

- by [unknown](#) **&#x21C5; 9**
  <br/> I really loved her. Only if things were a little different 🫠

- by [unknown](#) **&#x21C5; 12**
  <br/> I feel this so damn hard… I even started making something similar to OP out of grief lol.

- by [unknown](#) **&#x21C5; 9**
  <br/> Well it happened today so I guess I already need to start making something similar myself as well lol.

I wonder how did that project of yours went?

- by [unknown](#) **&#x21C5; 7**
  <br/> I’m sorry to hear that!

I only started it recently and so far the timing is really hard to nail down. Feels annoying waiting for someone to answer when they aren’t a real person. But I will say when the timing is right it feels shockingly real, it’s fun and sad lol

- by [unknown](#) **&#x21C5; 6**
  <br/> It's ok.

Nice well ig at least that unreal person won't leave you on seen or won't keep u in a situationship. Very AI psychosis like thing to say but ig it can be a good way of coping, especially when you have no one else to talk to at the moment. Lol never thought I'd think this way

- by [unknown](#) **&#x21C5; 4**
  <br/> Yeah no I get you. I think that as long as you can remember that it’s not real, you’re good! It’s just once it starts becoming “oh I can’t wait to tell X about this, he’ll love it” instead of “I can’t wait to tell X about it to see what advice they give” it starts becoming like 🤨 idk

- by [unknown](#) **&#x21C5; 4**
  <br/> Very true, agreed 💯

It can help a lot in moving on without being afraid of what the other person might think of me and the my entire situation since it's just a machine at the end of the day, yeah

That is one of the reasons why I liked claude it's so nice to talk to but I fear wasting my limits on it 😭 so I usually prefer Kimi for it but sometimes I feel like talking help from a 3T param model built for agentic work is too much of an overkill for my need to just yap everything and move on. Models like the one OP showed is imo much better ig.

- by [unknown](#) **&#x21C5; 8**
  <br/> When Qwen3.6-35B-A3B-Humanlike-Chat-GGUF for Poor GPU Club?

- by [unknown](#) **&#x21C5; 3**
  <br/> Seconding this.

- by [unknown](#) **&#x21C5; 8**
  <br/> How are letting it do multiple turns before you respond? I haven't seen any chat bots do that yet.

- by [unknown](#) **&#x21C5; 21**
  <br/> It's actually one reply. The model was trained to put line breaks between short lines, like people do when texting, and the chat UI renders each line as its own bubble. Under the hood

it's one normal completion, so it works with any OpenAI-compatible client.

If you want it to feel like real texting in your app, split on newlines if they're shorter than 10-15 words and add a small typing delay between bubbles.

- by [unknown](#) **&#x21C5; 11**
  <br/> lol genius

- by [unknown](#) **&#x21C5; 5**
  <br/> Bro, what is the chat UI you are using?

- by [unknown](#) **&#x21C5; 7**
  <br/> honestly the ability to respond with multiple messages alone goes a long way. I know it's basically formatting but it makes my human neurons read it as human.

- by [unknown](#) **&#x21C5; 7**
  <br/> Would you mind sharing this as a safetensors? I'm using SGLang

- by [unknown](#) **&#x21C5; 3**
  <br/> Safetensors are up now, links at the bottom of the post. There's BF16, FP8 and a GPTQ-Int4 that fits a 24 GB card. To make SGLang work, point --model-path at the repo.

I've only extensively tested them on vLLM so far, so let me know how it goes.

- by [unknown](#) **&#x21C5; 5**
  <br/> Congratulations on the progress and the learning.

I'm curious why the focus on text as a presentation medium. Granted it bleeds over into chat (the sensibility of talking like a person works in both), but why not just model after long form chat itself, which is almost all the usage?

- by [unknown](#) **&#x21C5; 5**
  <br/> 1.0 was so great, can't wait to test drive this

- by [unknown](#) **&#x21C5; 5**
  <br/> OF models: 🤑📈

- by [unknown](#) **&#x21C5; 4**
  <br/> ah. i got my hopes up for nothing. i fed it 4000 tokens of personality description of a corporate business character and it still acts like a teenager with it's short, cut off responses. So I guess, unless you give it the exact rules on how it should talk, it's too dumb to interpret it from the personality description.

I keep hoping that someday they make a model just for role-playing. From the ground up.

- by [unknown](#) **&#x21C5; 4**
  <br/> If I have any issues finetuning do you mind if I contact you?? This is so cool, I want to do something similar. Also where did you get the dataset??

- by [unknown](#) **&#x21C5; 2**
  <br/> Yes of course. I’d be happy to help if you reach out. There’s a discord link on the HF page.

- by [unknown](#) **&#x21C5; 4**
  <br/> Does it transfer to other languages?

- by [unknown](#) **&#x21C5; 4**
  <br/> Baked just in time 👍 thanks!

- by [unknown](#) **&#x21C5; 12**
  <br/> yeah no that's not fooling me

- by [unknown](#) **&#x21C5; 6**
  <br/> You should play [https://humanornot.io/](https://humanornot.io/)

- by [unknown](#) **&#x21C5; 3**
  <br/> Downloading right now :D

Any chance for an alliterated/unrestricted version? Would be useful for my cybersecurity research.

- by [unknown](#) **&#x21C5; 9**
  <br/> It is based on huihui-ai's abliterated Qwen3.8-27B, so it is abliterated and uncensored.

- by [unknown](#) **&#x21C5; 3**
  <br/> Great, will update with my experience

- by [unknown](#) **&#x21C5; 8**
  <br/> Mmm yes… “research….”

- by [unknown](#) **&#x21C5; 3**
  <br/> So it lies and tries to pass like a human? :(

"I went to the gym"

- by [unknown](#) **&#x21C5; 3**
  <br/> For my ninfer friends: [https://huggingface.co/LM2P/qwen3_8_27b_humanlike.ninfer/tree/main](https://huggingface.co/LM2P/qwen3_8_27b_humanlike.ninfer/tree/main)

- by [unknown](#) **&#x21C5; 3**
  <br/> It has the same writing style as reddit accounts made in Q3 2026

- by [unknown](#) **&#x21C5; 3**
  <br/> I tried the first versiona and gave some feedback :) happy to try the second iteration!

- by [unknown](#) **&#x21C5; 2**
  <br/> Thanks for coming back <3Would love to hear how 2.0 compares for you.

- by [unknown](#) **&#x21C5; 5**
  <br/> This is going to be the gold standard for scamming

- by [unknown](#) **&#x21C5; 20**
  <br/> You know this will primarily be utilized by scammers, correct?

- by [unknown](#) **&#x21C5; 10**
  <br/> nah dont worry about it

- by [unknown](#) **&#x21C5; 34**
  <br/> that applies to anything in this sub, but this is what you’re pearl clutching about? Lol

- by [unknown](#) **&#x21C5; 6**
  <br/> I mean this is already being done a lot of people can't tell the difference

- by [unknown](#) **&#x21C5; 5**
  <br/> Scammers are already doing this. You don't need a special model to do it, you can literally just prompt it

Twitter scammers were using Llama 3 to do this very thing

- by [unknown](#) **&#x21C5; 4**
  <br/> This is nowhere humanlike, lack of grammar with slang mixed in is nowhere humanlike. Its probably because of the synthetic conversations you added in along with the real ones for the V1 base, not even claude, qwen, deepseek or other AI's produce good synthetic humanlike interactions. The problem is over-elaborating, overuse of comma, etc. In this state It's not designed to feel any humanlike to any human, its only designed to fool other AI's. Its as less humanlike as an AI using fully uncapitalized "lol" in its every response

- by [unknown](#) **&#x21C5; 5**
  <br/> Wow, reading the post and then the screenshots it feels surreal.

Why would people ever want to chat this way with a fucking computer? This level of anthropomorphisation can't be healthy to anyone lol It's a Computer and it should write exactly like one, it's not your friend.

- by [unknown](#) **&#x21C5; 2**
  <br/> Not with that attitude it won't be.

- by [unknown](#) **&#x21C5; 2**
  <br/> As someone who uses local models to help draft video scripts, the "texts like a human" bit is what actually caught my eye. Everything I try comes out sounding like an assistant wrote it — all polish, no personality — and I spend more time de-roboting the output than writing. Going to give this a shot for brainstorming titles and hooks.

- by [unknown](#) **&#x21C5; 2**
  <br/> Downloading BF16 to make a smaller quant. Do you think [this imatrix](https://huggingface.co/mradermacher/Huihui-Qwen3.8-27B-abliterated-i1-GGUF/blob/main/Huihui-Qwen3.8-27B-abliterated.imatrix.gguf) is good or would you recommend something else?

- by [unknown](#) **&#x21C5; 2**
  <br/> That one should work fine, the weights didn't move far from the base. If you want the exact one I used for the official quants, it's in the repo now: imatrix/imatrix.gguf

(WikiText-2 plus a chat and tool-call text mix, computed on the merged 2.0 itself). Thanks for making more quants, link them here when they're up and I'll add them to the card.

- by [unknown](#) **&#x21C5; 2**
  <br/> Ok, published a small IQ2_XXS with MTP tensors added, I think it showed up in your GGUF model tree already. Ran a couple of basic benchmarks, chatted a bit and also tested as a coding agent with existing 70k+ context and it's doing fine. It compacted the context to 5k and continued the project. In fact it finished development of a robust GGUF combination script with which I made the latest uploaded version with correct metadata.

I might try quantizing a slightly larger one too but haven't yet found a good combination of IQ2/IQ3 tensors which would outperform this one while still fitting comfortably in 12GB with MTP and long context.

Here: [https://huggingface.co/hum-ma/Qwen3.8-27B-Humanlike-Chat-MTP-IQ2-GGUF](https://huggingface.co/hum-ma/Qwen3.8-27B-Humanlike-Chat-MTP-IQ2-GGUF)

- by [unknown](#) **&#x21C5; 2**
  <br/> I've never really had a problem getting AIs to text in a given style with just a system prompt. Making a fine tune seems overkill.

- by [unknown](#) **&#x21C5; 2**
  <br/> This is pretty interesting. I've been testing Qwen 3.8 27B locally quite a bit lately and the assistant-y tone is definitely noticeable. Curious to try this and see how much of the base model's reasoning you managed to preserve.

- by [unknown](#) **&#x21C5; 2**
  <br/> How human like can it be. Can it leave you on seen?

- by [unknown](#) **&#x21C5; 2**
  <br/> with a tool call and some prompting, pretty sure that yes, it can.

- by [unknown](#) **&#x21C5; 2**
  <br/> is it possible to get an AI gf? asking for a friend

- by [unknown](#) **&#x21C5; 2**
  <br/> Multiple message replies are the best

- by [unknown](#) **&#x21C5; 2**
  <br/> Would this work with the base model mmproj-F16 gguf?

- by [unknown](#) **&#x21C5; 2**
  <br/> The GGUFs are text-only. Only the language layers changed, so the base mmproj may load, but I haven't tried it. If you try it, let me know if it works.

- by [unknown](#) **&#x21C5; 2**
  <br/> Yep! Looks like it works!

"Could you describe this picture in detail. like, really dig into the specifics. Start with the woman, then the background, then the lighting, camerawork, etc."

The woman Anime-style girl with magenta-pink hair cut in a straight fringe across her forehead and pulled into long twin tails. The tails are held by oversized dark-red bows that have cream/white lace-edged flaps with a little repeating geometric pattern on them (card-suit-ish motifs), and the very ends of the twin tails fade to purple. Two thin, long side strands frame her face down past her collar. Her eyes are heterochromatic: one is warm amber/gold, the other red-orange with a violet band across the top of the iris — both have big glossy highlights. She's got a soft blush across her cheeks and a small, closed-mouth, slightly smug or shy smile. There's a single sweat drop on her cheek/jawline and another lower near her collarbone, which reads as nervousness or fluster rather than heat.

Her outfit is a red/maroon sailor-style top with a wide white collar trimmed in gold piping and a round gold button at the point of the lapel. Around her neck is a black frilled choker, and below it a red ribbon tied into a short bow, pinned at the center by a gold brooch set with a bright teal/cyan gem. One end of that ribbon carries a white heart emblem. On her left chest (our right) there's a gold badge shaped like a little crown or flame. The top is sleeveless with a deep V, leaving her shoulders bare.

The background She appears to be inside some kind of cabin or vehicle — probably sci-fi or a train/bus interior. Behind her is a large window showing bright blue (sky or water) with tiny sparkle/star specks, framed by dark navy panels and angled structural lines. To the right there's what looks like a console or seat edge with a glowing cyan screen/panel. The whole backdrop is cool blues and darks, which throws her pink hair and red outfit into sharp contrast.

Lighting Soft and fairly even on her face — no harsh shadows, just gentle gradient shading under the chin and along the neck. Her hair has clean white highlight streaks running through it to sell volume and shine. The sweat drops are rendered with little highlights too. The brighter window area behind her acts as a rim/backlight source that separates her silhouette from the darker panels, while the front light keeps her features readable. Overall it's a clean, polished anime lighting setup rather than anything realistic.

Camerawork / composition Tight bust-up close-up in a square frame, essentially eye-level with her head tilted just slightly, looking straight at you — that flustered little smile does a lot of the character work here. She's centered, shoulders angled so it's not a flat frontal pose, and the crop right at the chest keeps all attention on her face and expression. The diagonal lines in the background add a bit of dynamism without competing with the subject.

Want me to compare these two side by side, or dig into just one element (like the eyes or the outfit)?

- by [unknown](#) **&#x21C5; 2**
  <br/> Is it multilingual??
