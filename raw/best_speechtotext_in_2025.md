# Best Speech-to-Text in 2025? [Visit](https://www.reddit.com/r/LocalLLaMA/comments/1prmjt3/best_speechtotext_in_2025/)
### **Subreddit:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA)
### **Author:** [u/MindWithEase](https://www.reddit.com/user/u/MindWithEase/)
### **Vote:** 24
---
I work at a company where we require calls to be transcribed in-house (no third party). We have a server with 26GB VRAM (GeForce GTX 4090) and 64GB of RAM running Ubuntu server.
The most i keep seeing is the Whisper models but they seem to be about 75% accurate and will be destroyed when background noise of other people is introduced.
Im looking for opinions on the best Speech-to-text models or techniques. Anyone have any thoughts?
---
## Comments 53

- by [unknown](#) **&#x21C5; 14**
  <br/> Have you tried Whisper-large-v3 with some preprocessing? Running it through something like noisereduce or even just a simple high-pass filter before feeding to the model can bump accuracy way up in noisy environments

Also might want to look into speaker diarization if you're dealing with multiple voices - helps the model focus on one speaker at a time rather than getting confused by overlapping speech

- by [unknown](#) **&#x21C5; 1**
  <br/> This is the answer, you need a pre processing step on all the audio files. Maybe even a pre processing tool that removes all extra background noise. Then run it through a compressor, high pass filter, etc.

Only after all of that should you feed it to whisper large

- by [unknown](#) **&#x21C5; 1**
  <br/> Any option for this can you offer to try?

- by [unknown](#) **&#x21C5; 1**
  <br/> **I haven't used it. Where can I find it? Thanks.**

- by [unknown](#) **&#x21C5; 5**
  <br/> Parakeet is pretty amazing. Very accurate and I get like 100x realtime on a m3 MacBook Air using MacWhisper.

- by [unknown](#) **&#x21C5; 1**
  <br/> I have macwhisper but am disappointed even for fast models like parakeet (at least it supports it) there is no realtime transcription typing entry

- by [unknown](#) **&#x21C5; 1**
  <br/> [handy.computer](http://handy.computer) is what you want

- by [unknown](#) **&#x21C5; 1**
  <br/> im curious - freeway seems to good to be true - but without it being opensource.. how can it be trusted? there is no information on how it is funded..don't get me wrong.. this app looks awesome + amazing effort

- by [unknown](#) **&#x21C5; 1**
  <br/> One issue I consistently run into with Parakeet that I don't have with Whisper is that Parakeet will always write out numbers, even when it's not appropriate, like years or very large numbers. Have you found a solution to that?

- by [unknown](#) **&#x21C5; 1**
  <br/> At the moment I don’t think it makes much sense to build solutions around this — it’s better to just wait for the next model versions. They’ll probably fix this and introduce different problems instead.

Purely theoretically, you can convert spelled-out numbers back into digits with simple regex rules, or do post-processing with a small LLM. But any extra processing adds latency. For me, time-to-result matters more than quality.

I can always fix things later. What matters most is that the result appears instantly.

- by [unknown](#) **&#x21C5; 1**
  <br/> Yes, I understand. It’s just a shame that you have to decide. Whisper turbo does solve this issue for me and I can live with the extra bit of latency because fixing the output is way slower. I’ll definitely check out the next Nvidia ASR model.

- by [unknown](#) **&#x21C5; 1**
  <br/> Question for you: when i set the transcription delay to a short value its nice in that i can see the output quicker, but it ends the sentence putting a period and doesn't even put a space after the period, so the output.Looks quite.Ridiculous. Any ideas for improving this situation?

- by [unknown](#) **&#x21C5; 4**
  <br/> Parakeet and it’s not even close. It is better than whisper in everything and on top of that it is 400%-500% faster.

It’s even embarrasing for whisper to put them side by side.

- by [unknown](#) **&#x21C5; 1**
  <br/> Does it work without GPU?

- by [unknown](#) **&#x21C5; 1**
  <br/> Yes, and quite well. In fact just today (what a coincidence) I tried moving parakeet to run on the CPU by using the int8 quant of it instead of the full FP16 one. A voice command takes to process:

- FP16 in GPU: ~0.1s

- FP16 in CPU: ~0.42s

- INT8 in GPU: ~0.25s

This is on a humble 12th gen core i3 on an intel NUC, not a particularly powerful CPU. Nvidia really cooked with this model, it's amazing how it can run so fast.

However I'm willing to pay a few extra milliseconds if that frees 3.5gb of VRAM on my GPU, where they are most needed. Now I have to use it for some days to get a feel if the quantization hurts the performance noticeably or not.

- by [unknown](#) **&#x21C5; 1**
  <br/> Cool I'll have to try it out. Just today I tried bot whisper cpp and faster whisper and both took around 30 mins for a 30 mins audio file.

- by [unknown](#) **&#x21C5; 3**
  <br/> I've heard good things about Nvidia parakeet, but haven't played with it myself.

- by [unknown](#) **&#x21C5; 3**
  <br/> I would give a try to this free software, Ultimate vocal remover, as a prefilter. It also uses smaller LLMs trained for audio processing, it can extract the audio from songs and split into voice and instrumental songs. It even has ensemble mode that uses multiple models over same file and averages  the results for better quality.

The idea is to take your input file, pass it through this program and get the vocal only file, background noise should be removed or greatly reduced, the  pass it though your text to speech llm.

This software also supports hardware acceleration with cuda for Nvidia gpus. For Amd, there is a beta version that works quite well, I use it with 7900xtx. It has multiple models that you can download and you can experiment to see which gives best results.

- by [unknown](#) **&#x21C5; 1**
  <br/> Sorry to respond to a 20 day old comment, but I noticed you're using an RDNA3 GPU and it seems like you have some experience with local transcriptions. I've been looking to transcribe some videos and audio recordings using something like OpenAI's Whisper (or any other good S2T models that can be run locally) but haven't found too many options. I've tried [whisper.cpp](https://github.com/ggml-org/whisper.cpp) but the setup was absolutely hellish and I couldn't get things to work, [const-me's](https://github.com/Const-me/Whisper) Windows port of whisper.cpp, but it's abandonware, only works for the medium model, and severely hallucinates when transcribing other languages.

If there's anything you're using for S2T that's been working okay for you, can you tell me what it is?

- by [unknown](#) **&#x21C5; 1**
  <br/> I didnt need to use transcriptions. I use a program called Ultimate Vocal Remover [https://github.com/Anjok07/ultimatevocalremovergui](https://github.com/Anjok07/ultimatevocalremovergui) that can extract vocals from audio and write as separate mp3 file or wav, it uses multiple or single specialized models for isolating vocals, it has a download manager inside from where you download the models. You need to get the version for AMD gpu, it worked great for me on 7900xtx. After that, your transcription should improve because other noises are removed from the track, it eliminates even songs.

In the UI notice that you xan right click on source file textbox and it allows you to enter or drag list of files, i.e. it supports batch processing. It also caches the model in memory, so you can do lots of conversions efficiently.

- by [unknown](#) **&#x21C5; 1**
  <br/> This seems to be ther other way around, from text to speech.

- by [unknown](#) **&#x21C5; 6**
  <br/> Why not mention the most important information to answer this: which language?

- by [unknown](#) **&#x21C5; 13**
  <br/> If it’s not mentioned, isn’t it reasonable to assume it’s the language the post is in?

- by [unknown](#) **&#x21C5; 1**
  <br/> You really get the quality up if you chain - implicitly or explicitly - the audio stage to a small LLM. I remember there were some code when using Wav2Vec models.

Proprietary models like Gemini-Flash oder GPT-4o-transcribe (not really sure what the correct name is) are performing this implicitly. Because they are a "real" LLM with MultiModal Audio Input.

Mistral did a OpenWeights release for Voxtral which is also multimodal. I did not perform any benchmark but e.g. with Voxtral Small you can set up a System Prompt like "Take the audio input and create correct english phrases out of it" Then it translates everything it understands to english. They also provide a "transcription" only model, which I actually did not test.

- by [unknown](#) **&#x21C5; 1**
  <br/> Depending on the language Nvidia ASR models

- by [unknown](#) **&#x21C5; 1**
  <br/> I have a piece of software that i've been working on that does basically this, but im curious how the server plays into this on your end / what you envision there. Is this over VOIP or are you taking calls on physical infrastructure and through what mechanism do you intend to listen to the calls?

- by [unknown](#) **&#x21C5; 1**
  <br/> For English, parakeet is very good and pretty fast in CPU alone.

- by [unknown](#) **&#x21C5; 1**
  <br/> qwen 3 omni

- by [unknown](#) **&#x21C5; 1**
  <br/> I found one on google play that I like, it’s new but it’s really good, as I was using a few other but would have to edit after, this one handles all your filler words and organises your speech, it’s called zavi, I’m only using the free tier but I’m tempted to go paid

- by [unknown](#) **&#x21C5; 1**
  <br/> I used an IPA-to-Whisper model, but its results were not accurate. The problem is that the topic of my graduation thesis is TTS and STT models, and my supervisor wants the application to be focused on learning English. So far, I have not found a suitable STT model.

I tried Wav2Vec2, but the issue is that it outputs the text exactly as it hears it, and it often makes mistakes even when the pronunciation is correct. As for Whisper Tiny, it corrects what the user says based on the sentence context, which is not suitable for pronunciation evaluation.

After that, I decided to compare phonemes instead of raw text. However, I encountered a problem loading a phoneme-based Wav2Vec2 model, and the IPA-to-Whisper approach is still not accurate.

Can someone please help me?

- by [unknown](#) **&#x21C5; 1**
  <br/> Sounds like a solid setup for on‑premise transcription. Whisper is indeed tricky in noisy call environments, and many teams end up stacking preprocessing (noise suppression, VAD, beamforming) or moving to more robust models like Canary, Granite‑based ASR, or specialized enterprise options

If you ever test a mixed‑stack approach (cloud‑only or hybrid), I’ve seen folks get decent quality with tools like Talo and Palabra for real‑time speech‑to‑speech pipelines: they sit on top of ASR internally and can be useful for prototyping or testing accuracy in different noise conditions, even if you keep final production fully on‑prem

- by [unknown](#) **&#x21C5; 1**
  <br/> I know this is an older thread but we just added Speech to Text at [https://textspeakpro.com](https://textspeakpro.com) if you are still interested.  Check it out!

- by [unknown](#) **&#x21C5; 0**
  <br/> Maybe this will help:

[https://modal.com/blog/fast-cheap-batch-transcription](https://modal.com/blog/fast-cheap-batch-transcription)

- by [unknown](#) **&#x21C5; 1**
  <br/> ok (great overview btw) but is something like qwen3 omni on the map here? or you havent gotten around to testing it?

- by [unknown](#) **&#x21C5; 1**
  <br/> thanks, didn't try qwen3 omni and didn't see any good reviews around it
