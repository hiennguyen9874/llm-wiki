# What's the best open speech to text today? [Visit](https://www.reddit.com/r/LocalLLaMA/comments/1u9ggke/whats_the_best_open_speech_to_text_today/)
### **Subreddit:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA)
### **Author:** [u/zxyzyxz](https://www.reddit.com/user/u/zxyzyxz/)
### **Vote:** 8
---
I'm looking for a setup that can do real time diarization as well, basically looking for an alternative to Wispr Flow or other such tools. I know of MacParakeet which uses Parakeet and of course Whisper models, but I'm wondering what else exists for real time, surely there should be new models these days right?
---
## Comments 36

- by [unknown](#) **&#x21C5; 7**
  <br/> [open asr leaderboard on hf](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) is a good resource

- by [unknown](#) **&#x21C5; 8**
  <br/> I have seen this page getting linked over amd over again as response to this question.

Maybe it is just me, but I have absolutely no clue what any of these metrics mean and how to judge their performance for my use case.

- by [unknown](#) **&#x21C5; 2**
  <br/> They explain the terms in the beginning and link to them; you want the lowest word error rate possible while being open weight.

- by [unknown](#) **&#x21C5; 4**
  <br/> Local (as per this channel): Nvidia Parakeet 0.6 tdt v3: Better or equal than whisper 3 large depending on language, tenth times faster.

- by [unknown](#) **&#x21C5; 3**
  <br/> Just a FYI that TDT v2 is better for English only if that meets your needs.

- by [unknown](#) **&#x21C5; 1**
  <br/> Parakeet v2 is much faster for English than v3.

- by [unknown](#) **&#x21C5; 2**
  <br/> I haven't had any issues with faster-whisper large-v3 for my voice satellites. Not particularly new by any means.

- by [unknown](#) **&#x21C5; 2**
  <br/> Same here, very satisfied with faster whisper.

- by [unknown](#) **&#x21C5; 1**
  <br/> large-v2 >>>

- by [unknown](#) **&#x21C5; 1**
  <br/> I agree I use whisper.. Voice is one of those things.. if it works really well its essentially done and whisper is like 99.9 Accurate for me locally. I dont see a need for a better model.

- by [unknown](#) **&#x21C5; 2**
  <br/> I’ve tried parakeet, whisper large v3.5, funasr and qwen3 asr. Qwen3 asr and it is the best and it’s not close for my use case. It hallucinates the least and rejects non speech so much better than the others

- by [unknown](#) **&#x21C5; 2**
  <br/> Same here, Qwen3-ASR is very impressive

- by [unknown](#) **&#x21C5; 1**
  <br/> One advantage of Parakeet is the quantized version loses very little performance, is blazing fast and can run on most CPUs.

Does Qwen 3 ASR share those other characteristics as well or is there a tradeoff on speed and how heavy the model is? I noticed the 1.7B model is the one that wins over Parakeet on benchmarks.

- by [unknown](#) **&#x21C5; 1**
  <br/> I don’t pay attention to benchmarks ever but I can tell you my experience. I use the 0.6b ASR model and that’s what I’m saying beats all those others. It’s as fast or slightly faster than faster-whisper 3.5 it’s a tough call, but Qwen is more reliable literally every time. Parakeet is fast yes, like really fast but Qwen, if set up right is not far behind. Parakeet is not worth it for how much it gets utterances wrong

- by [unknown](#) **&#x21C5; 1**
  <br/> For pure “what’s the best STT model right now?”, I’d separate a few use cases:

  - Short/basic dictation: Apple Dictation is honestly good enough for a lot of people.
  - Batch transcription: Whisper variants are still very solid, especially if you care about local/offline.
  - Realtime voice typing: latency, correction behavior, hotkeys, app integration, and post-processing matter almost as much as the raw model.
  - Realtime diarization: that’s the harder bit. A lot of tools that feel great for dictation don’t really solve diarization well.

If your main goal is a Wispr Flow-style local-first dictation workflow rather than meeting transcription, I’m working on TypeWhisper, so bias/disclosure there. The angle is local/offline-capable dictation with profiles, prompts/post-processing, dictionary/snippets, and engine choice rather than “one magic model.” I wouldn’t pitch it as a diarization solution though — if diarization is the core requirement, I’d look specifically at tools built around speaker segmentation.

Curious what your exact workflow is: live captions/meeting notes, voice typing into apps, or transcribing recordings?

- by [unknown](#) **&#x21C5; 1**
  <br/> Live meeting recording yeah, for distinguishing potentially multiple speakers, still haven't seen a great solution. What stack do you use for your app? Seems similar to MacParakeet which is FOSS so not sure what the appeal is for paying for a paid app.

- by [unknown](#) **&#x21C5; 1**
  <br/> For your specific use case, live meeting recording with multiple speakers, I’d still look for something built around diarization first. TypeWhisper can record/transcribe and has workflows around the transcript, but it is not primarily a “who spoke when?” product.

Stack-wise, it is engine/plugin based: local options such as WhisperKit/Parakeet on macOS, whisper.cpp/sherpa-onnx style local engines on Windows, plus optional cloud engines. The product work is mostly around everything after “model returns text”: insertion, workflows, cleanup, dictionary/snippets, history, recorder/file transcription, and switching behavior per app/site/hotkey.

And fair question on paid vs FOSS: TypeWhisper is GPLv3 too. Commercial licensing is for non-GPL/proprietary use and the maintained packaged product/support path, not because the underlying STT model is secret.

- by [unknown](#) **&#x21C5; 1**
  <br/> You can technically make a stack that seperates voices by frequency to generally differentiate who is speaking.

- by [unknown](#) **&#x21C5; 1**
  <br/> OpenAI Whisper [https://youtu.be/hUGEh0NALBk?si=OsFNhdFCvZ0c0Xsh](https://youtu.be/hUGEh0NALBk?si=OsFNhdFCvZ0c0Xsh) I have some details about my latest testing here .

- by [unknown](#) **&#x21C5; 2**
  <br/> Reread my post, I know about whisper, I'm asking what else is new since it released 4 years ago

- by [unknown](#) **&#x21C5; 1**
  <br/> But Whisper is excellent the question i have for you why would you need anything different if whisper is already really good? Vosk is another option that i know of. Is there something that the ones you have tried are lacking?

- by [unknown](#) **&#x21C5; 1**
  <br/> Heavily depends on usecase and language, check open asr hf leaderboard and test models yourself on your data

- by [unknown](#) **&#x21C5; 1**
  <br/> I just released a beta version of a TTS library. If anyone interested it testing it. It not a fully packaged app. It just a runtime. [https://github.com/SamReynoso/pfspeak](https://github.com/SamReynoso/pfspeak)

- by [unknown](#) **&#x21C5; 1**
  <br/> I'm talking about speech to text not text to speech

- by [unknown](#) **&#x21C5; 1**
  <br/> My bad. I've been using Sherpa for STT. It's pretty amazing. But don't know how it compares to other models.

- by [unknown](#) **&#x21C5; 1**
  <br/> Real time transcription and real time diarization are kind of two separate problems, most tools just glue them together.

For the text side, Parakeet is the fast one but it is mostly English plus some European languages. If you want real time with more languages, Whisper large-v3-turbo streamed through whisper_streaming or WhisperLive works well. Whisper is not streaming by itself so those just chunk it. turbo is worth it, almost as accurate as large-v3 but much faster. If you are English only and want the lowest latency, look at Moonshine.

Diarization is the harder half and still the weak spot. pyannote is the standard and diart runs it live. NeMo has streaming diarization now too. Just know live diarization is noticeably worse than offline, so if you can wait for a batch pass afterwards, WhisperX plus pyannote gives way cleaner speaker labels.

- by [unknown](#) **&#x21C5; 1**
  <br/> I've stuck with local tools for live use then used WhisperAI for uploads to handle diarization later. Do you need everything strictly on device, or is some cloud processing okay for the non live part?
