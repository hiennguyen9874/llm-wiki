# Good ASR and TTS models? [Visit](https://www.reddit.com/r/LocalLLaMA/comments/1v1auga/good_asr_and_tts_models/)
### **Subreddit:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA)
### **Author:** [u/Kahvana](https://www.reddit.com/user/u/Kahvana/)
### **Vote:** 31
---
Hey everyone,
Something I don't see discussed often here are ASR and TTS models.
I've been using Whisper and Kokoro (old models, I know!) with koboldcpp for a while now but wondered if there are now solid replacements available. Know of Qwen3-ASR and Qwen3-TTS, but haven't found the time yet to test them.
What ASR and TTS models have you been using?
---
## Comments 51

- by [unknown](#) **&#x21C5; 17**
  <br/> ive played with whisper and parakeet.

you might want to check out audio.cpp it is supposed to simplify setup and yield good performance.

- by [unknown](#) **&#x21C5; 2**
  <br/> Thanks, checking audio.cpp!

Between whisper and parakeet, which do you prefer more and why?

- by [unknown](#) **&#x21C5; 3**
  <br/> it depends on what are your requirements. parakeet is pretty lightweight and very fast - there is even a CPU optimized port which runs decently well...

whisper is more thorough with noisy speech and shows lower WER especially with mixed speakers and multiling but very heavy on VRAM and slower.

- by [unknown](#) **&#x21C5; 0**
  <br/> coincidentally i've checked exactly those as well and I wouldn't recommend either but if you had to pick one it'd be parakeet, although i know other models came out which are better

- by [unknown](#) **&#x21C5; 10**
  <br/> In terms of ASR: on huggingface there is an ASR leaderboard with rankings for word error rate (detection accuracy) and realtime factors (speed), I found it useful to determine whats best for a specific usecase. The autoregressive models like whisper are usually slower while conformer style models are faster, you can even run the smaller ones on a microcontroller. At the end it depends on your requirements and hardware.

- by [unknown](#) **&#x21C5; 1**
  <br/> Thanks for the info! I'd be running it on my dual RTX 5060 Ti 16GB, English voice in both directions, Dutch would be fun but I suspect the quality would be lacking.

As for the leaderboard, do you mean this?[https://huggingface.co/spaces/hf-audio/open_asr_leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)

- by [unknown](#) **&#x21C5; 2**
  <br/> Honestly alot of the ASR models you need to test yourself. Right now I need multilingual as well as speed, FunASR plus OmniVoice is a good stack for my use case.

- by [unknown](#) **&#x21C5; 2**
  <br/> Yes exactly thats the leaderboard. A single 5060 ti should be plenty. Maybe take a look at parakeet v3, should support dutch. At least in German it did quite well for me.

- by [unknown](#) **&#x21C5; 7**
  <br/> I have been enjoying PocketTTS for cloning (cloning voices made with Qwen 3 VoiceDesign); I find it is not really noticeable whether it is any worse then Qwen3-TTS.  I was not too happy with OmniVoice. All are definitely a step up from Kokoro, and PocketTTS is much better and barely bigger in size (plus, cloning!!). I love Kokoro but there were some super consistent mispronunciations of words that bothered me.

Fot ASR I have no tips; I use whisper large v3 turbo and it is very fast on my machine (m1 max) so I don't really bother optimizing there.

- by [unknown](#) **&#x21C5; 4**
  <br/> So if I understand it correctly:

  1. Create a voice with Qwen3-TTS-VoiceDesign
  2. Clone voice of generated voice with PocketTTS
  3. Use cloned voice

That sounds really cool! Any tips or tricks for voice cloning? I've never done it before.

Glad to hear Whisper Large V3 Turbo still holds up!

What do you use to run PocketTTS, Qwen 3 voicedesign anss whisper with?

- by [unknown](#) **&#x21C5; 4**
  <br/> Yup, I do it to have consistent voices for my voice agent. And I have no tips or tricks, it's just as simple as that.

It's all ran in Python as part of the server for my voice agent. On disk I have a `personas` directory, and inside of that each persona is a folder with `reference_audio.wav reference_text.txt voice_description.txt`. On my UI I write a new voice description, give it a name, and VoiceDesign will generate a new voice and make such a folder with the name I give it. Then the reference audio (and reference text if needed) is used for the voice agent when I select that persona (I also put the voice description in the system prompt so the LLM too is aware of the personality lol). It's basically real time chat, the LLM backend drives the latency; if I use a small/fast local model the latency is sub 1s. Each persona has their own memory directory too so they feel more like individuals than just voices I slap on an agent.

I am not at my desk right now but I can give snippets in a few hours.

- by [unknown](#) **&#x21C5; 1**
  <br/> Would be very much appriciated. Thank yo so much for sharing your cool workload!

- by [unknown](#) **&#x21C5; 2**
  <br/> I'm curious as to why you're not happy with omnivoice while pocket tts is drop dead garbage from the moment I tried it out for like 4 mins? I did notice it has streaming support unlike omnivoice.

- by [unknown](#) **&#x21C5; 1**
  <br/> Maybe it doesn't like your sample audio? It works great for me and sounds about as good as Qwen 3 TTS cloning but is faster.

- by [unknown](#) **&#x21C5; 2**
  <br/> Trying it again with female voice and it outputs a choppy male voice.

- by [unknown](#) **&#x21C5; 5**
  <br/> **ASR: Whisper** is the only model that worked like a charm for me.For voice, I really like the quality of **OmniVoice** + **VoxCPM2**

- by [unknown](#) **&#x21C5; 4**
  <br/> For me, these are the options I found best:ASR: nemotron-3.5-asr-streaming-0.6b (streaming mode)TTS:  Qwen3-TTS 0.6B CustomVoice

- by [unknown](#) **&#x21C5; 3**
  <br/> Been running faster-whisper in prod for a voice pipeline and it's held up way better than vanilla Whisper on CPU-only boxes where GPU isn't in the budget. For TTS, worth giving Kokoro's newer checkpoint a look if you haven't touched it in a while, it's improved since the koboldcpp integration matured. Also curious if anyone's paired Qwen3-ASR with a VAD frontend instead of running it standalone, that combo usually kills a good chunk of the false-trigger issues.

- by [unknown](#) **&#x21C5; 1**
  <br/> On huggingface I see kokoro's model was last updates april 2025, is it being improved elsewhere?

Never heard of VAD before! Voice Activation Detection?

- by [unknown](#) **&#x21C5; 2**
  <br/> VAD is used on top of ASR/STT model so you know when an utterance stops. There are alot of cheap ones that run on CPU so don't bother finding the best etc. STT is more important.

- by [unknown](#) **&#x21C5; 2**
  <br/> Sounds quite handy, any open weight ones you can recommend?

- by [unknown](#) **&#x21C5; 2**
  <br/> Silero VAD, auto downloaded from hf if u do pip install silero-vad>=5.0.0

- by [unknown](#) **&#x21C5; 3**
  <br/> The [audio.cpp](https://github.com/0xShug0/audio.cpp) project supports a good variety to evaluate. My favorites are Qwen3-TTS and OmniVoice. Running them on a RTX 3060.

- by [unknown](#) **&#x21C5; 3**
  <br/> Whisper + Kokoro is still a strong combination. If I was going to upgrade now I would definitely test Qwen3-ASR and Qwen3-TTS against Whisper and Kokoro. I think this is especially true when it comes to using Whisper and Kokoro in different languages and when I need things to happen quickly.

- by [unknown](#) **&#x21C5; 3**
  <br/> Vibevoice 7b is the largest model out there and best when it comes to quality and emotion. Just it's not stable model. Vibevoice ASR is stable though and production ready. It does speaker diarization as well which is a plus.

- by [unknown](#) **&#x21C5; 1**
  <br/> I use the smaller vibevoice realtime and it's pretty decent.

- by [unknown](#) **&#x21C5; 2**
  <br/> [https://github.com/High-Logic/Genie-TTS](https://github.com/High-Logic/Genie-TTS)

- by [unknown](#) **&#x21C5; 1**
  <br/> Looks pretty cool! How do you make your own characters for this?

- by [unknown](#) **&#x21C5; 2**
  <br/> I've been using faster qwen 3 tts plus whisper, it's been working pretty well for my setup.

- by [unknown](#) **&#x21C5; 2**
  <br/> Very nice! Does whisper have a benefit over Qwen3-ASR?

- by [unknown](#) **&#x21C5; 1**
  <br/> Honestly, I'm not sure, I was looking for something small and reliable at the time, and those were my best options haha I need to have a look at Qwen3-ASR, see if it's better!

- by [unknown](#) **&#x21C5; 2**
  <br/> kokoro butchers a few words for me too lol, been meaning to try qwen tts

- by [unknown](#) **&#x21C5; 2**
  <br/> Depends on the use case for ASR - You also could use Gemma 4 ( or Mistral Voxtral ) with audio input to produce an optimized and cleaned output instead of a pure transcript

- by [unknown](#) **&#x21C5; 2**
  <br/> The best ones for my language is VoxCPM and Chatterbox

- by [unknown](#) **&#x21C5; 2**
  <br/> [Chatterbox](https://github.com/resemble-ai/chatterbox)

- by [unknown](#) **&#x21C5; 2**
  <br/> Parakeet and Kokoro. Whisper turbo if you only have cpu.

- by [unknown](#) **&#x21C5; 2**
  <br/> For ASR, Parakeet (fast) and Whisper large-v3 (accuracy) are still the safe picks.

audio.cpp simplifies setup. For local TTS, F5-TTS and Kokoro are the current favorites for quality-per-VRAM, Piper if you need it to run on almost anything.

One thing that saved me: whatever local TTS you land on, keep a tiny set of 'golden' reference clips and diff new output against them after any model/version change. Local models drift silently on updates just like hosted ones.

- by [unknown](#) **&#x21C5; 1**
  <br/> That is a really good tip, thank you!

- by [unknown](#) **&#x21C5; 1**
  <br/> Try liquid

- by [unknown](#) **&#x21C5; 1**
  <br/> Faster whisper is still hard to beat for stability unless you have a specific reason to switch from it

- by [unknown](#) **&#x21C5; 1**
  <br/> i have been using this project as of lately, and there are quite a few good models in there. but i always end up using qwen3 asr

[https://github.com/cjpais/Handy](https://github.com/cjpais/Handy)

- by [unknown](#) **&#x21C5; 1**
  <br/> Echo is really good for tts but Vram expensive (10GB)

I saw a few news ones today for tts and one for stt but haven't had to try them.

- by [unknown](#) **&#x21C5; 1**
  <br/> Kokoro's still the latency king locally, so no rush to swap it — Qwen3-TTS sounds better but is slower. For ASR, if you care about real-time, Parakeet streams better than Whisper; Qwen3-ASR is strong but heavier on VRAM.

- by [unknown](#) **&#x21C5; 1**
  <br/> [https://huggingface.co/OpenMOSS-Team/MOSS-Transcribe-Diarize](https://huggingface.co/OpenMOSS-Team/MOSS-Transcribe-Diarize) is really good, especially on Chinese.

- by [unknown](#) **&#x21C5; 1**
  <br/> English, mutlilang (Dutch, Japanese) is a nice bonus
