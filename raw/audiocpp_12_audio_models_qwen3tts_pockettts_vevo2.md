# audio.cpp: 12 audio models (Qwen3-TTS, PocketTTS, VeVo2 etc) in 1 C++/ggml runtime — TTS up to 5x faster than Python on CUDA [Visit](https://www.reddit.com/r/LocalLLaMA/comments/1ufpnm6/audiocpp_12_audio_models_qwen3tts_pockettts_vevo2/)
### **Subreddit:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA)
### **Author:** [u/Acceptable-Cycle4645](https://www.reddit.com/user/u/Acceptable-Cycle4645/)
### **Vote:** 421
---
**Update (07/23/2026)**: Release 0.4: Added Higgs Audio v3 TTS 4B, Fish Audio S2 Pro, Voxtral Realtime ASR and two community models OuteTTS TTS and VieNeu-TTS-v3. Full GGUF support.
**Update(07/21/2026):** Add GGUF q8 support + perf boost for Omnivoice. 43x realtime now!
On RTX 5090:
Mode
Wall
Generate
Decode
Audio
RTF
Speed
BF16 perf=off
11379.940 ms
10682.538 ms
360.192 ms
357.0 s
0.0319
31.37x RT
Q8 perf=off
10252.340 ms
9517.626 ms
401.118 ms
357.0 s
0.0287
34.82x RT
Q8 perf=on
8283.184 ms
7553.023 ms
404.915 ms
357.0 s
0.0232
43.10x RT
**Update(07/14/2026):** Release 0.3 adds five new models: Supertonic 3, MOSS-TTS-Local, MOSS-TTS-Nano, IndexTTS2, and Irodori-TTS. Supertonic 3 can hit 200x+ realtime on RTX5090. It can generate 10 hours of audio in 3 mins. Check [https://www.reddit.com/r/LocalLLaMA/s/mLfiWn1mu7](https://www.reddit.com/r/LocalLLaMA/s/mLfiWn1mu7) for demo video!
**Update (07/09/2026):** Just pushed a performance optimization. Updating a single shared module improved performance across 13 models by up to 40%! The released ASR models get a 10%+ performance boost. Check [https://github.com/0xShug0/audio.cpp/blob/release-0.2/docs/depthwise_conv1d_performance.md](https://github.com/0xShug0/audio.cpp/blob/release-0.2/docs/depthwise_conv1d_performance.md)
**Update(07/08/2026):** Four new ASR families are now released in the framework: Higgs Audio STT, Hviske ASR, Nemotron ASR, and VibeVoice ASR. Initial model-specific streaming support also lands for VoxCPM2 TTS, Nemotron ASR, and Higgs Audio STT.  Nemotron ASR 0.0066 RTF on RTX 5090.
**Update (07/03/2026): Conv1DTransp module CUDA optimization: VibeVoice reaches 5.15x realtime, generating 93.9-minute podcast in 18.12 min!** Overall, VibeVoice inference time for short requests was reduced by **73.17%**, PocketTTS by **35.32%**, Chatterbox by **33.56%**, Qwen3-TTS by **30.60%**, HeartMuLa by **17.03%**, and VoxCPM2 by **14.7%** compared with the previous release.
**Update (07/02/2026): Thanks to** [**https://github.com/justinjohn0306**](https://github.com/justinjohn0306) **for the contribution! VibeVoice 7B and LoRA are now supported in audio.cpp.**
**Update (07/02/2026): ACE-Step 1.5 Turbo/Base, HeartMuLa, Stable Audio 3 Small Music/SFX and Medium, Mel-Band RoFormer, and HTDemucs are now available!**
Update (06/30/2026): VibeVoice released!
Generate 90 mins audio on 5090:
Impl
Audio length
Wall time
RTF
x real time
audio.cpp
5615.73s / 93.60 min
1376.84s / 22.95 min
0.245
4.08x
Python
5559.47s / 92.66 min
3942.04s / 65.70 min
0.709
1.41x
**Update (06/29/2026): Irodori TTS and Stable Audio 3 impl are ready!**
**Update (06/26/2026)**: Three small models from Nvidia released: CitriNet (STT) MarbleNet (VAD), Sortformer (speaker diarization)
------------------------------------------------------------
I’ve been working on **audio.cpp**, a native C++ inference framework for audio models built on top of ggml.
The framework currently has **25** model families, but I want to be precise about its state: **12** are  **released** in the repo now and ready for normal use. I’m not counting anything still in integration or optimization as released.q
The released set already covers quite a bit:
**TTS / voice cloning / voice design:** Chatterbox, MioTTS, OmniVoice, PocketTTS, Qwen3-TTS and VoxCPM2
**ASR / alignment / VAD:** Qwen3-ASR, Qwen3 Forced Aligner and Silero VAD
**Voice conversion / codec / editing:** Seed-VC, MioCodec and Vevo2
Vevo2 also handles TTS, singing generation, singing conversion and editing, so this has grown beyond a collection of TTS ports.
The point isn’t to build a model zoo.
It’s to stop treating every audio model as its own island with a separate Python environment, dependency tree, CLI, batching logic and deployment setup. I want these models to share the same runtime, session handling, CLI, server, audio utilities and eventually the same higher-level workflows.
The performance is where the project started to feel genuinely useful rather than just easier to deploy.
These results were measured on Ubuntu/CUDA using the original weights without quantization. The figures compare audio.cpp wall time against the matching Python reference path:
**PocketTTS:** **3.68×** faster on a 1-shot run, **3.22×** in a warm session and **3.15×** on long-form
**Qwen3-TTS:** **1.83×** on a 1-shot run, **2.74×** in a warm session and **3.06×** on long-form
**Vevo2:** **5.03×** on a 1-shot run, **1.75×** in a warm session and **1.77×** on long-form
**MioTTS:** **2.73×** on a 1-shot run and **2.28×** in a warm session
**Chatterbox:** **1.58×** on long-form
The long-form throughput makes those numbers easier to picture. Using the same **1,028-word** input:
**PocketTTS:** generated **5m 53.12s** of audio in **7.30s** — **48.40×** real time
**OmniVoice:** generated **5m 57.00s** in **17.77s** — **20.09×** real time
**Vevo2:** generated **7m 37.68s** in **52.47s** — **8.72×** real time
Every released TTS family included in that benchmark ran faster than real time, ranging from **4.34×** to **48.40×**.
I don’t want to oversell it: not every path beats Python yet, and the README keeps the weaker results visible. But the warm-session numbers are the ones I care about most. They are closer to a real service setting, where the model is loaded once and reused across many requests.
The shared runtime is the bigger bet.
The current same-language redubbing pipeline takes a **418s** recording, splits it into manageable chunks, transcribes it with Qwen3-ASR, merges the transcript and regenerates the speech in a target reference voice with Qwen3-TTS—all behind **1** CLI command.
The inference and server paths are native C++. There is a Python utility for downloading and converting model packages, but Python isn’t part of the actual inference path.
It’s still early. Backend coverage depends on the model, and framework-wide streaming isn’t generally supported yet, so the current paths should still be treated as offline. The framework can target CPU, CUDA, Vulkan and Metal where the model supports them.
Repo:
[https://github.com/0xShug0/audio.cpp](https://github.com/0xShug0/audio.cpp)
I’d really value benchmarks from other hardware, failing cases, API feedback and PRs.
---
![r/LocalLLaMA - audio.cpp: 12 audio models (Qwen3-TTS, PocketTTS, VeVo2 etc) in 1 C++/ggml runtime — TTS up to 5x faster than Python on CUDA](https://preview.redd.it/12-audio-models-qwen3-tts-pockettts-vevo2-etc-in-1-c-ggml-v0-uzhwa3v4gi9h1.png?width=640&crop=smart&auto=webp&s=09268c79417faf7504e81dd5a600d127dd74faa4)
---
![r/LocalLLaMA - audio.cpp: 12 audio models (Qwen3-TTS, PocketTTS, VeVo2 etc) in 1 C++/ggml runtime — TTS up to 5x faster than Python on CUDA](https://i.redd.it/uzhwa3v4gi9h1.png)
---
![r/LocalLLaMA - audio.cpp: 12 audio models (Qwen3-TTS, PocketTTS, VeVo2 etc) in 1 C++/ggml runtime — TTS up to 5x faster than Python on CUDA](https://preview.redd.it/12-audio-models-qwen3-tts-pockettts-vevo2-etc-in-1-c-ggml-v0-4iedl1z5gi9h1.png?width=640&crop=smart&auto=webp&s=b0ad468c162ef0997ca1f0c46223804a9e39e98f)
---
![r/LocalLLaMA - audio.cpp: 12 audio models (Qwen3-TTS, PocketTTS, VeVo2 etc) in 1 C++/ggml runtime — TTS up to 5x faster than Python on CUDA](https://i.redd.it/4iedl1z5gi9h1.png)
---
## Comments 162

- by [unknown](#) **&#x21C5; 63**
  <br/> Now that I think, it's kinda crazy we didn't have something like Llama.cpp for LLM AI or ComfyUI for image gen AI. Whenever I wanted to check out any TTS AI, it was always a headache figuring out how to set up things etc. Maybe something like this already exist, I never paid attention and didn't look deep enough.

Anyway, good job and I will surely keep an eye on this and play with it if I get bored or get some free time.

- by [unknown](#) **&#x21C5; 9**
  <br/> Thanks!

- by [unknown](#) **&#x21C5; 6**
  <br/> or ComfyUI for image gen AI.


    There is.

[https://github.com/leejet/stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp)

- by [unknown](#) **&#x21C5; 9**
  <br/> I meant something like Llama.cpp or ComfyUI but for audio TTS AI.

- by [unknown](#) **&#x21C5; 1**
  <br/> vllm-omni supports some tts models. Haven't tried that functionality though.

- by [unknown](#) **&#x21C5; 21**
  <br/> Hey op ....I implemented lately higgs V3 with very fast kernel for DMC  for llamaccpp but of course ithey din not want to integrate to main. Maybe you want ?

Also are you created a universal library for text to audio  models something like omtd ( opposite to mind ). That uniform some components to all models.

- by [unknown](#) **&#x21C5; 11**
  <br/> Yes. This is the main goal! Some compoents have been extracted already. You can check src/framework

- by [unknown](#) **&#x21C5; 3**
  <br/> As for integration, I’ve already implemented Higgs V3 using the framework modules. Right now, I’m testing the remaining models (all implemented end to end) in the backlog one by one before releasing them.

That said, if you have any special optimization tricks or model-specific tips, I’d really appreciate it if you could share them.

- by [unknown](#) **&#x21C5; 2**
  <br/> I have already fully working that .

Tomorrow I will show you that on GitHub

- by [unknown](#) **&#x21C5; 1**
  <br/> Great! Please ping me when you release your impl.

- by [unknown](#) **&#x21C5; 5**
  <br/> Ok I can give you a link now. So you can check

OMTD ( output multimodal) library . Opposite to MTMD

[https://github.com/ggml-org/llama.cpp/compare/master...mirek190:llama.cpp:omtd-core](https://github.com/ggml-org/llama.cpp/compare/master...mirek190:llama.cpp:omtd-core)

Later is easy add a new models not braking the main code of llamacpp

- by [unknown](#) **&#x21C5; 1**
  <br/> Sure

- by [unknown](#) **&#x21C5; 2**
  <br/> Yeah the repo has a super naive server. I'll look at llama-server to see if I can integrate it easily

- by [unknown](#) **&#x21C5; 11**
  <br/> Cool! When there is a server available I’d like to add it as a part of the llama-swap:unified docker container. I’ll keep an eye on the repo.

- by [unknown](#) **&#x21C5; 11**
  <br/> Oh there is no hosted service. The framework has a simple server that you can build and run. Currently the server exposes

  - `GET /health`
  - `GET /v1/models`
  - `POST /v1/audio/speech`
  - `POST /v1/audio/transcriptions`
  - `POST /v1/tasks/run`

- by [unknown](#) **&#x21C5; 7**
  <br/> oh i didn’t read closely enough; i glanced through the code for a server. I’ll give it a try. Nice work!

- by [unknown](#) **&#x21C5; 1**
  <br/> speaches.ai is trying to be this for STT/TTS, but they are lagging still.

- by [unknown](#) **&#x21C5; 9**
  <br/> perfect timing! what about stt?

- by [unknown](#) **&#x21C5; 7**
  <br/> The current release has Qwen3-ASR and a built-in pipeline for long audio redub

- by [unknown](#) **&#x21C5; 1**
  <br/> Nice i have to test that. i made a ggml cuda container with many inference engines because i hate pytorch blowing size to 10gb vs 2-3gb. i might use your solution :)But ill add whispercpp manually if qwen3-asr is too slow

- by [unknown](#) **&#x21C5; 1**
  <br/> Is it possible you could eventually create a way to integrate this with LTX video? [Their redubbing functionality has a substantial gap](https://ltx.io/blog/lipsync-vs-lipdub), I would like to provide source audio of the original dub, a clip of a target voice that will be redubbed to, redubbing all dialogue to the target voice, then redubbing the video to match the lip flaps, which LTX does not support.

- by [unknown](#) **&#x21C5; 1**
  <br/> I'll look at LTX2.

`provide source audio of the original dub, a clip of a target voice that will be redubbed to, redubbing all dialogue to the target voice`

This can be done with the using the redub pipeline [https://github.com/0xShug0/audio.cpp#pipelines](https://github.com/0xShug0/audio.cpp#pipelines)

Or use the voice conversion models SeedVC and VeVo2 in audio.cpp

`redubbing the video to match the lip flaps`

This part audio.cpp can't handle.

- by [unknown](#) **&#x21C5; 1**
  <br/> This part audio.cpp can't handle


    Right, I meant an integration with LTX.

- by [unknown](#) **&#x21C5; 1**
  <br/> Which quant version of LTX2 have you used? Are they good? I believe my GPU can only handle Q2 to Q5.

- by [unknown](#) **&#x21C5; 1**
  <br/> Q2 which isn't great, whenever I really intend to start using it after it matures more I'll be renting a GPU to be able to run the highest quality version ideally unquantized. My use case here is redubbing existing animes. I love English dubs, and my favorite VA Billy Kametz died a few years ago, and shows that he was VAing midway through had to change voice actors (E.g. Iruma and Shield Hero), so I want to redub the subsequent seasons with the original voice.

- by [unknown](#) **&#x21C5; 1**
  <br/> Can you elaborate on why you need LTX2 for this use case?

- by [unknown](#) **&#x21C5; 1**
  <br/> [https://ltx.io/blog/lipsync-vs-lipdub](https://ltx.io/blog/lipsync-vs-lipdub)

Their functionality has everything I need except for the ability to provide reference audio as the source voice for the redubbing. I'm unaware of another project that could be utilized for this that's actually viable (there are a few different anime redubbers out there but they are wonky and unmaintained and they do not modify the video the same way LTX does), but they would have the same integration issue as LTX and given LTX is the most widely used project I can think of for this given it already has this functionality built in aside from reference audio redubbing, LTX seems like the best route.

LTX modifies the video so the lips match the audio.

- by [unknown](#) **&#x21C5; 2**
  <br/> I'm using whisper.cpp for stt.

- by [unknown](#) **&#x21C5; 9**
  <br/> Always fun seeing these pop up. We already have qwen3-tts from another project and the asr from llamacpp itself inside of KoboldCpp. But the existing Qwen3-TTS is slow on stuff other than vulkan. Ill forward this and see if its something we want to adopt.

- by [unknown](#) **&#x21C5; 3**
  <br/> Sure! Would you like to share the perf metrics? For Qwen3-TTS, audio.cpp produces 327.60s audio in 72.65 (RTF = 0.222, or 4.51x of real time) for 6,026-character, 1,028-word input text. You can find the test case in tools/audiocpp_cli/audiocpp_cli_longform_tts_clone_cases.json.

- by [unknown](#) **&#x21C5; 4**
  <br/> Its why its potentially interesting. On top of my head the existing one we have on cuda is a terrible 0.3x realtime. On CPU it was around 0.5 realtime. And the on vulkan it becomes 2x.

The main thing for us will be how easy it is to reimplement the audio backend on top of this, and especially important. We can't deal with ggml forks. The current ace-step we have for example can't be synced with the upstream project since it runs a forked GGML. We need stock ggml to keep up with llamacpp.

So in those aspects your project may be interesting. Its up to lostruins though, he'd be doing the work porting it.

- by [unknown](#) **&#x21C5; 2**
  <br/> Interesting. I've only optimized a few models for CPU and one model for Vulkan as they were generally slower than cuda... It definitely requires different graphs and logic for different backends for perf. There is no one-size-fits-all solution. I eventually gave up because it made the code much messier.

- by [unknown](#) **&#x21C5; 1**
  <br/> The author of the qwen3-tts.cpp we based it on was an AMD user. So for AMD it was optimized and for nvidia not at all. We had contributors who helped further improve the vulkan speed in our fork but nobody fixed cuda.

So in that place your project can be very interesting. It may be able to replace a few audio backends we have integrated. But how compatible is it with the existing gguf's? Can we expect them to work or would we need to integrate it side by side where it loads the backend code depending on which project the quant is for?

- by [unknown](#) **&#x21C5; 1**
  <br/> GGUF support should be relatively easy to add, since the framework was designed with multiple model formats in mind. Quantization can also be done at loading time, for example:

`--session-option qwen3_tts.weight_type=q8_0`

There is already a section in the README discussing quantization support.

The real issue is not whether the framework can support quantization. The harder problem is that quantization can cause quality drops, and some model components may even produce NaNs. So I think quantization support needs to be tested model by model to decide which options are safe.

- by [unknown](#) **&#x21C5; 9**
  <br/> Most of this is over my head, I just want to say thank you for the work and your willingness to share for the greater community.

- by [unknown](#) **&#x21C5; 6**
  <br/> What about CPU performance? For many applications where you don’t need 100x realtime, it’s a waste to run audio models on the GPU.

- by [unknown](#) **&#x21C5; 5**
  <br/> Most of my optimization work has focused on GPU so far, so I don’t have much to say about CPU performance yet. That said, I believe CPU performance should be reasonable, since much of the development and parity testing is done on CPU with FP32. Feel free to try it and let me know what performance you get.

- by [unknown](#) **&#x21C5; 1**
  <br/> What does creating something like this look like? The only coding language I’m familiar with is python, so this is a layer of coding that I’m completely unfamiliar with.

- by [unknown](#) **&#x21C5; 2**
  <br/> Lang doesn’t matter as much because there are so many coding agents... But being familiar with the lang helps a lot when debugging and spotting anti-patterns.

- by [unknown](#) **&#x21C5; 1**
  <br/> The point about pocket tts and kokoro and similar sized models is that they run comfortably on CPU, so you can have audio while your GPU is full with LLM.

- by [unknown](#) **&#x21C5; 6**
  <br/> Good to know for PocketTTS. It's become my new lightweight go-to when I don't need the quality of OmniVoice.

- by [unknown](#) **&#x21C5; 6**
  <br/> Thanks for making this! I need it!

- by [unknown](#) **&#x21C5; 14**
  <br/> the single-runtime-instead-of-12-python-envs angle is the real win here honestly. the per-model dependency tree is what actually kills audio model deploys for me, every tts repo wants its own pinned torch and a slightly cursed gradio. does it do any quantization yet or is it fp16 only on the released set for now?

- by [unknown](#) **&#x21C5; 3**
  <br/> Exactly. I need to set up 3 conda env for testing, and even in the same env I need to install 2 versions of transformers...

The framework converts weights during loading, e.g., `--session-option qwen3_tts.weight_type=q8_0.`If "native" then just use orignal weight dtype. You can set bf/fp16 and q8. The support for q8 is model by model. Quantization can cause quality drops, and some model components may even produce NaNs.

- by [unknown](#) **&#x21C5; 2**
  <br/> Begone bot

- by [unknown](#) **&#x21C5; 5**
  <br/> Looks awesome. If it works, I don't even mind if it's slightly slower than the nemo/onnx/pytorch versions, I just want to get away from:


      It’s to stop treating every audio model as its own island with a separate Python environment, dependency tree, CLI, batching logic and deployment setup.


    110GB of this mess.

Do you have ggufs for the models?

Also, what's with the `utm_source=chatgpt.com` in the repo link?

- by [unknown](#) **&#x21C5; 3**
  <br/> utm_source=chatgpt.com --- Haha, good catch. Looks like ChatGPT added this sneaky “watermark” during the grammar pass.

For GGUF: GGUF support should be relatively easy to add, since the framework was designed with multiple model formats in mind. But currently it’s lower priority compared to adding support for more models.

- by [inagy](https://www.reddit.com/user/inagy/) **&#x21C5; 3**
  <br/> Is this only going to support TTS models, or are you planning on adding more generic generative audio models eventually (like Stable Audio)?

- by [inagy](https://www.reddit.com/user/inagy/) **&#x21C5; 2**
  <br/> Not limited to TTS. ACE-step, heartmula and demucs will be released soon.

- by [inagy](https://www.reddit.com/user/inagy/) **&#x21C5; 1**
  <br/> Stable Audio looks good. I'll definitely include it.

- by [inagy](https://www.reddit.com/user/inagy/) **&#x21C5; 1**
  <br/> Thank you! That would be really useful as it would allow running some cool custom trained models, like [Foundation-1](https://huggingface.co/RoyalCities/Foundation-1) which is a bit special, since it's like a synthetiser, producing samples for music production and not complete music.

- by [inagy](https://www.reddit.com/user/inagy/) **&#x21C5; 1**
  <br/> [u/inagy](/user/inagy/) I played with the released small and medium models, and they did not look like powerful as acestep and heartmula. Speed is amazing though. Whats your use case?

- by [unknown](#) **&#x21C5; 1**
  <br/> First, I'm no audio professional or musician by any means.

I'm more interested about music remixing, creating sampleable sounds for a DJ mix than full blown music generation with these models. (These local models are not reaching the level of the large models like Suno anyway. The open models aren't trained on wide variety of modern music, I guess because of copyright reasons. But even with those large commercial models I don't think anyone considers the output as publishable professional production. It's fun to play with them or testing/drafting ideas.)

I think Foundation-1 is novel as it tries to solve only a very narrow problem and doesn't try to be a jack of all trades. It's like an parametrized dynamic AI sequencer/synthetiser. It even allows inputing your own idea and it will create a variation of that with the given sound characterestics you prompt. It leaves more control to the user. I hope the guy will expand upon the idea and will train a similar drum machine type of model in the future. I don't think otherwise there are too many other good usecases of Stable Audio Open at the moment, unfortunately. Also I understand that Foundation-1 only attracts a minority of people, as it requires investing time in it, it's not a slot machine type of "prompt in -> song out" model, it works more like a tool. But watch the [creators introduction video](https://www.youtube.com/watch?v=O2iBBWeWaL8), it explains the intention behind more clearly than I could.

- by [unknown](#) **&#x21C5; 1**
  <br/> Okay thank you for the info!

- by [inagy](https://www.reddit.com/user/inagy/) **&#x21C5; 2**
  <br/> [u/inagy](/user/inagy/) stable audio done, will be released this week with acestep and heartmula

- by [unknown](#) **&#x21C5; 1**
  <br/> I need to find some freetime, then I'll give it a go. Thanks!

- by [unknown](#) **&#x21C5; 3**
  <br/> yeah the main reason I haven't experimented much with audio models is because every single time I looked at a new release it felt like a pain to set up a new thing, I'm glad there's a push on this

edit: typo

- by [unknown](#) **&#x21C5; 2**
  <br/> yeah the audio model ecosystem is a mess.

- by [unknown](#) **&#x21C5; 3**
  <br/> Saved!

- by [unknown](#) **&#x21C5; 2**
  <br/> there is a "Seed VC" was there a preseed vc too?

- by [unknown](#) **&#x21C5; 2**
  <br/> You can check their repo [https://github.com/Plachtaa/seed-vc](https://github.com/Plachtaa/seed-vc)

- by [unknown](#) **&#x21C5; 2**
  <br/> The benefit of a unified framework is very clear: optimizing one shared module benefits every model that uses it. For example, improving the fast KV module gives all models using that module  **5%+** speedup.

- by [unknown](#) **&#x21C5; 2**
  <br/> Does it support GGML's ARM accelerated CPU instructions for matmul?

- by [unknown](#) **&#x21C5; 2**
  <br/> Yes. I tested with `-mcpu=native+dotprod+i8mm+nosve+sme`. However, the current release doesn’t build with these flags by default. You can add them and test the CPU build.

- by [unknown](#) **&#x21C5; 2**
  <br/> Cool.  Can't wait to test.

- by [GamerWael](https://www.reddit.com/user/GamerWael/) **&#x21C5; 2**
  <br/> Any plans to support supertonic? their latest model was quite impressive based on their demos, though I havent tried it myself yet.

- by [GamerWael](https://www.reddit.com/user/GamerWael/) **&#x21C5; 2**
  <br/> [u/GamerWael](/user/GamerWael/) I actually managed to convert Supertonic3 ONNX to ggml graphs and have a preliminary implementation. The similarity between the audio produced by the ggml version and the official Python version is 0.85, but the ggml version is currently 1.5x slower than Python on CPU.

- by [Acceptable-Cycle4645](https://www.reddit.com/user/Acceptable-Cycle4645/) **&#x21C5; 1**
  <br/> That sounds great, thanks for trying [u/Acceptable-Cycle4645](/user/Acceptable-Cycle4645/) . Unfortunately my technical knowledge on TTS implementation is quite low, otherwise I would've offered to help. A similarity of 0.85 doesnt seem too bad. And even with it being 1.5x slower, it might still be pretty fast and usable since the model was quite fast to begin with.

- by [GamerWael](https://www.reddit.com/user/GamerWael/) **&#x21C5; 2**
  <br/> [u/GamerWael](/user/GamerWael/) Great news for you. Supertonic3 should be ready to use.

Long-lived session, multi requests:

CUDAlen=100   python=459.097880 ms    audiocpp=200.394716 ms    wav similarity=0.997149870len=500   python=318.044325 ms    audiocpp=258.415793 ms    wav similarity=0.993584315len=1024  python=600.918393 ms    audiocpp=517.245254 ms    wav similarity=0.986413283len=500   python=293.679450 ms    audiocpp=220.509596 ms    wav similarity=0.993584315

CPUlen=100   python=1178.027166 ms   audiocpp=1714.841194 ms   wav similarity=0.999999904len=500   python=5201.492628 ms   audiocpp=8585.747932 ms   wav similarity=0.999999906len=1024  python=11020.700841 ms  audiocpp=17186.266357 ms  wav similarity=0.999500272len=500   python=5191.778114 ms   audiocpp=7443.348123 ms   wav similarity=0.999999906

Stay tuned for the release of Supertonic3!

- by [unknown](#) **&#x21C5; 1**
  <br/> That's awesome! Thankss!

- by [unknown](#) **&#x21C5; 1**
  <br/> No...Supertonic only released onnx models

- by [unknown](#) **&#x21C5; 2**
  <br/> Really appreciate this. The fact that I have to load full-weights 2.4GB models for a 0.6B TTS model has always been the biggest thing holding me back from hosting my dream voice assistant on my setup! Keep at it!

- by [unknown](#) **&#x21C5; 2**
  <br/> Good job!Thanks!

- by [Doctor_moctor](https://www.reddit.com/user/Doctor_moctor/) **&#x21C5; 2**
  <br/> Awesome project! Any love for stable audio 3 and RVC?

- by [Doctor_moctor](https://www.reddit.com/user/Doctor_moctor/) **&#x21C5; 1**
  <br/> I'll definitely include stable audio 3. For VC, you can try SeedVC and VeVo2, which are supported by the framework. I didn't do RVC because training is a big part of RVC.

- by [Doctor_moctor](https://www.reddit.com/user/Doctor_moctor/) **&#x21C5; 2**
  <br/> [u/Doctor_moctor](/user/Doctor_moctor/)  stable audio done, will be released this week with acestep and heartmula

- by [unknown](#) **&#x21C5; 1**
  <br/> Thanks! I just checked vevo2 on a rtx 3090 + 5070 ti and it straight OOMs. Im not too much into the whole tech side, is there a way to load it quantized?

- by [unknown](#) **&#x21C5; 2**
  <br/> wow, looking forwards to see more models added.

- by [ProMorning](https://www.reddit.com/user/ProMorning/) **&#x21C5; 2**
  <br/> amazing. thank you for your efforts. I gotta take a look at this and implement with all the models i'm tracking

[https://github.com/5uck1ess/tts-bench](https://github.com/5uck1ess/tts-bench)

- by [ProMorning](https://www.reddit.com/user/ProMorning/) **&#x21C5; 2**
  <br/> Great resource, I'm still referencing this regularly. Any chance you can add some timestamp or release date for each model so users know roughly when they released? This space is evolving so fast with new models coming out regularly, I tend to want to try out the newest models first since I assume they will be better for the most part.

It seems for the most part that the models are released, maybe a couple follow-up updates (if that), and then remain unchanged while the creators move on to making newer models. So I would think that just the release date of the model would be sufficient. Either way, thanks for keeping this going

- by [ProMorning](https://www.reddit.com/user/ProMorning/) **&#x21C5; 1**
  <br/> [u/ProMorning](/user/ProMorning/) the years have been published.

- by [unknown](#) **&#x21C5; 1**
  <br/> Awesome, thanks

- by [unknown](#) **&#x21C5; 2**
  <br/> THANKS!!!

- by [unknown](#) **&#x21C5; 2**
  <br/> this speedup is crazy,  tested it on r9700, about 2.5-3x realtime for qwen3 tts with a cloned voice, used to be way slower

- by [unknown](#) **&#x21C5; 2**
  <br/> Thanks, that's awesome to hear!

- by [unknown](#) **&#x21C5; 1**
  <br/> very cool indead. does the api support realtime streaming for tts and stt?

whisper support would be amazing, too. it still has the best WER on noisy audio.

- by [unknown](#) **&#x21C5; 1**
  <br/> Currently. Some models' streaming paths are implemented but not fully wired into the framework. For whisper, the framework has whisper as a module because some models use it, but not as a standalone model. The reason is whisper.cpp is pretty matured...

- by [unknown](#) **&#x21C5; 1**
  <br/> Vad, stt, and tts. Explain where's the stub to integrate an openai llm between stt and tts and this becomes THE engine.

- by [unknown](#) **&#x21C5; 1**
  <br/> I downloaded [https://huggingface.co/kyutai/pocket-tts/blob/main/tts_b6369a24.safetensors](https://huggingface.co/kyutai/pocket-tts/blob/main/tts_b6369a24.safetensors) as pocket.safetensors and tried pointing audiocpp_cli to it but I get :

audiocpp_cli failed: no registered model loader can load: C:\Users\me\Documents\audio.cpp\models\pocket\pocket.safetensors

- by [unknown](#) **&#x21C5; 3**
  <br/> The framework expects the layout as [https://huggingface.co/kyutai/pocket-tts/tree/main](https://huggingface.co/kyutai/pocket-tts/tree/main). e.g. [model dir] /languages/english/model.safetensors and tokenizer.model. You can use HF repo or use the download tool to download only english ver.

- by [unknown](#) **&#x21C5; 1**
  <br/> Thanks! I got it to work in English but for French I get this error :

PS C:\Users\me\Documents\audio.cpp\models\pocket> C:\Users\me\Documents\audio.cpp\build\windows-cpu-release\bin\audiocpp_cli.exe --task tts --family pocket_tts --model "C:\Users\me\Documents\audio.cpp\models\pocket\languages\french_24l" --load-option language=french --text "je suis un test de TTS sur CPU." --voice-id alba --out build/out/pocket_tts_french.wav audiocpp_cli failed: PocketTTS voice assets layer count does not match FlowLM configuration

I notice there's only a french_24l folder, not just 'french'

- by [unknown](#) **&#x21C5; 1**
  <br/> Good catch. I didn’t realize there was only `french_24l`. `*_24l` uses `flow_layers = 24`, which is much larger than the normal `flow_layers = 6`. The framework currently only handles the normal version. Could you submit a feature request?

- by [unknown](#) **&#x21C5; 1**
  <br/> Faster than vLLM ?

It's easy to be faster than python on cuda when you use official repo, now go for vLLM

- by [unknown](#) **&#x21C5; 1**
  <br/> Thats why I'd like another framework for audio related models. Many of these models are not LLM based. vLLM is excellent for LLM token generation, but it does not solve the full audio pipeline: codec encode/decode, mel/STFT/ISTFT, resampling, speaker conditioning, diffusion/flow sampling, vocoder graphs, and more.

- by [unknown](#) **&#x21C5; 1**
  <br/> What happened to vibe voice? Didn't it allow for "unique" usecases before Microsoft tried to take it down?

Did it die a natural death anyway?

- by [unknown](#) **&#x21C5; 2**
  <br/> No idea...bummer Microsoft. The impl of VibeVoice 1.5B in audio.cpp was based on [https://github.com/vibevoice-community/VibeVoice](https://github.com/vibevoice-community/VibeVoice).

- by [unknown](#) **&#x21C5; 1**
  <br/> this is awesome. i’ve been working with a lot of the python tts libraries and it is indeed a pain to juggle and configure. i’ll have to take a look at how i might be able to leverage this. may have to wait for or potentially build the python bindings though.

great work.

- by [unknown](#) **&#x21C5; 1**
  <br/> lang bindings will be released!

- by [unknown](#) **&#x21C5; 1**
  <br/> i hope it supports streaming

- by [unknown](#) **&#x21C5; 2**
  <br/> Streaming definitely will be supported in the future. The streaming paths of some models are implemented but just haven’t been wired into the framework yet.
