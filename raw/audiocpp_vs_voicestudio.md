# Audio.cpp vs VoiceStudio? [Visit](https://www.reddit.com/r/StableDiffusion/comments/1wznruv/audiocpp_vs_voicestudio/)
### **Subreddit:** [r/StableDiffusion](https://www.reddit.com/r/StableDiffusion)
### **Author:** [u/pilkyton](https://www.reddit.com/user/u/pilkyton/)
### **Vote:** 11
---
Which do you prefer and why?
- [https://voicestudio.sh/](https://voicestudio.sh/) (has been getting a lot of talk lately, supports 27 models, some are based on audio.cpp, but it [gets lots of criticism for confusing UI and other issues](https://www.reddit.com/r/StableDiffusion/comments/1wznruv/comment/pemfz5h/) and also has a closed-source paid version which people don't like)
- [https://github.com/0xShug0/audio.cpp/](https://github.com/0xShug0/audio.cpp/) (supports 100+ models, all are blazingly fast, and it has a local app and web interface and Docker support)
Edit: More interfaces!
- [https://github.com/unslothai/unsloth](https://github.com/unslothai/unsloth) (another UI frontend, this one being a Swiss Army knife which recently added audio.cpp support)
- [https://voicebox.sh/](https://voicebox.sh/) (another open source frontend, this one is free, but the user who mentioned it said he may switch to Unsloth)
---
## Comments 13

- by [unknown](#) **&#x21C5; 10**
  <br/> Audio.cpp doesn't have paid "Pro" tiers.

- by [unknown](#) **&#x21C5; 6**
  <br/> Making people pay for an audio.cpp wrapper that you can vibecode in one evening... How lame.

I'm still using the totally free [https://voicebox.sh/](https://voicebox.sh/) for that. I may switch to Unsloth.

- by [unknown](#) **&#x21C5; 2**
  <br/> Bingo

- by [unknown](#) **&#x21C5; 1**
  <br/> Huh? I have audio.cpp and I never paid for anything. What are ya'all talking about?

- by [unknown](#) **&#x21C5; 2**
  <br/> voicestudio is a UI and looks more professional. audio.cpp feels more like an engine or library. I don't really need a UI, so audio.cpp works well for me for my voice agent and meeting transcription pipeline (super fast). I do use audio.cpp's built-in UI's Arena feature to compare and pick models, though. I also saw that Unsloth recently added support for audio.cpp. If the main consideration is the UI, Unsloth might be a better choice.

- by [unknown](#) **&#x21C5; 2**
  <br/> Oh that's interesting, I didn't know Unsloth had a UI frontend:

[https://github.com/unslothai/unsloth](https://github.com/unslothai/unsloth)

That might be the best way to run audio.cpp for those who want a UI. Thanks for the tip.

- by [unknown](#) **&#x21C5; 2**
  <br/> Im using voicestudio, unsloth for some reason has problem with connection on my pc. It cant dl from huggingface

- by [unknown](#) **&#x21C5; 2**
  <br/> For audiobooks - definitely NOT VoiceStudio.

It's "caching" is capable of storing 2-3 chapters, so it's impossible to generate anything long: app is crashing very often and loosing all progress. Interface is nice but mostly confusing.

- by [unknown](#) **&#x21C5; 1**
  <br/> Thanks, that matches what I had been hearing about the interface being confusing. I also noticed that it's very behind in what models it supports compared to audio.cpp itself. They pick a few of its models and support those instead of everything. Some really nice ones were missing in VoiceStudio.

The crashes losing all progress is also insane. And caching being poorly implemented? I will update the post to mark that one as risky.

- by [unknown](#) **&#x21C5; 1**
  <br/> I built my own python free c++ back end housing unit that can run llms , SD and audio . Multi model . Hot swap vram like lightning. I mean I get yue2 track 3 min in 40 seconds on a 3080rtx.  Ai coding means u can effectively iterate at speed and have full memory control . I'll make the git public eventually.. right now it can run stable audio 3 yue2 and minimax 3 and use chains of each to do various complex tasks.. a built in daw so u can render samples and loops . A multi track fuser to drop in wave files from anywhere and have the model melt it together. Single model functions all proven already. Lemme tell y'all muse spark 1.3 free on open code is a baller.

- by [unknown](#) **&#x21C5; 1**
  <br/> Are any of these ideal for epub to audio?

- by [unknown](#) **&#x21C5; 1**
  <br/> I have been using this one: [https://github.com/zeropointnine/tts-audiobook-tool](https://github.com/zeropointnine/tts-audiobook-tool) The installation was daunting, but I gave chatgpt the github link, told it which voice engines I wanted to use (pocket tts, omni voice, and qwen3 tts) and had chatgpt create an automated install script for me. It downloaded everything and created the correct venvs for me. This app worked well enough for my needs.

I tried an earlier version of [https://voicestudio.sh/](https://voicestudio.sh/) but it kept failing on install when I tried to add additional voice engines. I think this app would be an easier to use solution if the newer versions work for you. I haven't bothered re-installing this one, yet, but may do so after I finish listening to my current audiobook.

- by [unknown](#) **&#x21C5; 1**
  <br/> I'm still rocking tts-webui
