# [audio.cpp] 10 hours of audio generated in 3 minutes on RTX 5090 (demo included)! C++/GGML based Supertonic 3, MOSS-TTS, IndexTTS2, and Irodori-TTS released [Visit](https://www.reddit.com/r/LocalLLaMA/comments/1uwpvt9/audiocpp_10_hours_of_audio_generated_in_3_minutes/)
### **Subreddit:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA)
### **Author:** [u/Acceptable-Cycle4645](https://www.reddit.com/user/u/Acceptable-Cycle4645/)
### **Vote:** 124
---
audio.cpp again. Hopefully you are not sick of it yet :)
Release 0.3 adds five new models: Supertonic 3, MOSS-TTS-Local, MOSS-TTS-Nano, IndexTTS2, and Irodori-TTS.
The highlight is Supertonic 3. It can hit **200**×+ real time on CUDA (RTX 5090), 6×+ on CPU, and around 47 ms TTFT in CUDA streaming mode. In the demo (sorry for the rough demo), I used *The Adventures of Sherlock Holmes* as the input and generated around 10 hours of audio in about 3 minutes on an RTX 5090.
Supertonic 3 was also pretty fun to work on. The official implementation uses ONNX, so I had to reverse-engineer the inference path and rebuild it around the safetensors weights.
The audio.cpp version is much faster than the Python implementation on CUDA, while CPU performance is about the same, maybe slightly faster.
One reason for the big CUDA win is that the ONNX version sends some nodes back to the CPU, so it can’t fully use the GPU.
The other models released in 0.3 range from roughly the same speed to more than 2× faster, depending on the test case. In IndexTTS2 longform test (6000-char input text + 2400-char emotion text), C++ is 5.65x faster than Python.
GGUF support has been added and will be rolled out model by model.
Contributions and feeback are very welcome. There’s still a lot to improve across model coverage, streaming, GGUF support, backend compatibility, performance, testing, and the server/UI layers.
Repo: [https://github.com/0xShug0/audio.cpp](https://github.com/0xShug0/audio.cpp)
---
## Comments 92

- by [Unlikely_Neat7608](https://www.reddit.com/user/Unlikely_Neat7608/) **&#x21C5; 15**
  <br/> not sick. Will submit more PRs :)also echo tts big time need. it does almost perfect cloning.

- by [Unlikely_Neat7608](https://www.reddit.com/user/Unlikely_Neat7608/) **&#x21C5; 11**
  <br/> omnivoice ranks 1 on voice cloning for me than any other.

- by [Unlikely_Neat7608](https://www.reddit.com/user/Unlikely_Neat7608/) **&#x21C5; 6**
  <br/> I have only been through a few different models, but Omni voice is head and shoulders above everything else that I’ve used. My use case is audiobook generation but I have not looked into any multiple speaker setups or emotion tags.

Omni voice does not get lost at all if I tell it to generate 4 hours worth of audiobook at once.

- by [Unlikely_Neat7608](https://www.reddit.com/user/Unlikely_Neat7608/) **&#x21C5; 3**
  <br/> eh you guys can take a look for yourselves at my bench and what people voted on. i thought omni was perfect but it does have little bit of artifacts. I think current winner by blind score is actually moss tts, but echo and omni are not far behind.

[https://github.com/5uck1ess/tts-bench](https://github.com/5uck1ess/tts-bench)

- by [Unlikely_Neat7608](https://www.reddit.com/user/Unlikely_Neat7608/) **&#x21C5; 1**
  <br/> the bench looks great - I'm working on something similar myself that also includes the api providers - small nitpick in that I think you've done RTF the wrong way - smaller is better because the definition is (processing time)/(output audio duration) - if a 4s clip takes 1s to generate, the RTF is 0.25 not 4

[https://openvoice-tech.net/index.php/Real-time-factor](https://openvoice-tech.net/index.php/Real-time-factor)

- by [Unlikely_Neat7608](https://www.reddit.com/user/Unlikely_Neat7608/) **&#x21C5; 1**
  <br/> [u/Unlikely_Neat7608](/user/Unlikely_Neat7608/) looking into it. Thanks for the correction if that's the case.

I've also got the paid API research done if you're interested in collab/notes sharing.

I think my RTF definition is a little different from the "proper" definition, and so maybe I should rename or add that to the repo; I can rename mine to RTFx since i'm measuring audio over processing (the opposite of real RTF), which is higher is better and it reads more naturally. Will get that in right now.

- by [unknown](#) **&#x21C5; 2**
  <br/> will try to publish mine in the next couple of days - will let you know!

am always open to feedback/constructive criticism

yeah it's interesting isn't it - I think big number = better makes more sense, I agree

- by [Rude_Marzipan6107](https://www.reddit.com/user/Rude_Marzipan6107/) **&#x21C5; 2**
  <br/> [u/Rude_Marzipan6107](/user/Rude_Marzipan6107/) It is already in audio.cpp [https://www.reddit.com/r/LocalLLaMA/s/LOPGQvEhCf](https://www.reddit.com/r/LocalLLaMA/s/LOPGQvEhCf)

- by [unknown](#) **&#x21C5; 2**
  <br/> Thanks for the info!

- by [Cultured_Alien](https://www.reddit.com/user/Cultured_Alien/) **&#x21C5; 2**
  <br/> [u/Cultured_Alien](/user/Cultured_Alien/) OmniVoice is already included in audio.cpp. [https://www.reddit.com/r/LocalLLaMA/s/LOPGQvEhCf](https://www.reddit.com/r/LocalLLaMA/s/LOPGQvEhCf)

- by [R_Duncan](https://www.reddit.com/user/R_Duncan/) **&#x21C5; 1**
  <br/> And ranks also 1 on non-english languages

- by [R_Duncan](https://www.reddit.com/user/R_Duncan/) **&#x21C5; 2**
  <br/> [u/R_Duncan](/user/R_Duncan/) Omnivoce was released in audio.cpp a few weeks ago --- [https://www.reddit.com/r/LocalLLaMA/s/LOPGQvEhCf](https://www.reddit.com/r/LocalLLaMA/s/LOPGQvEhCf)

- by [unknown](#) **&#x21C5; 1**
  <br/> Yes, but still no gguf support which would be the best way to keep vram low and allow for asr + llm + tts (llm from other apps like llama.cpp)

- by [unknown](#) **&#x21C5; 2**
  <br/> GGUF support for omnivoce + perf boost. On RTX 5090:


      
        
          
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

- by [unknown](#) **&#x21C5; 1**
  <br/> Very good! Do the memory footprint decreases? My issue there is that I have limited VRAM and want to feed stt-llm-tts.

- by [unknown](#) **&#x21C5; 1**
  <br/> Decreased but I don’t know how much VRAM your machine has. You can try mem-saver mode, though it can’t be combined with perf mode yet.

- by [unknown](#) **&#x21C5; 5**
  <br/> OmniVoice is unmatched. It's tough for me to admit because I follow this space so closely, but it can absolutely hold its own against professional dubbers. Give it a try.

- by [unknown](#) **&#x21C5; 1**
  <br/> 👍

- by [unknown](#) **&#x21C5; 6**
  <br/> Cool! Please consider publishing Docket containers 🙏

- by [unknown](#) **&#x21C5; 9**
  <br/> Sure! We already have a Docker image build script available: [https://github.com/0xShug0/audio.cpp/blob/main/Docker.md](https://github.com/0xShug0/audio.cpp/blob/main/Docker.md) (Thanks to our contributor for putting it together!)

- by [unknown](#) **&#x21C5; 3**
  <br/> Cool!

- by [unknown](#) **&#x21C5; 5**
  <br/> If you don't want to watch the video, here is the result

 
      [](https://preview.redd.it/10-hours-of-audio-generated-in-3-minutes-on-rtx-5090-demo-v0-5dkcn91jcadh1.png?width=736&format=png&auto=webp&s=0374c8442dd1144eaccaacd356df3c62acb0a26d)

- by [Silver-Champion-4846](https://www.reddit.com/user/Silver-Champion-4846/) **&#x21C5; 5**
  <br/> The models currently in progress are Higgs Audio, Fish Audio, and Voxtral Mini 4B. Let me know if you have any suggestions for other audio-related models you’d like to see supported.

- by [unknown](#) **&#x21C5; 6**
  <br/> Echo TTS please

- by [unknown](#) **&#x21C5; 2**
  <br/> Noted

- by [Silver-Champion-4846](https://www.reddit.com/user/Silver-Champion-4846/) **&#x21C5; 3**
  <br/> Omnivoice supported?

- by [Silver-Champion-4846](https://www.reddit.com/user/Silver-Champion-4846/) **&#x21C5; 3**
  <br/> [u/Silver-Champion-4846](/user/Silver-Champion-4846/) Yes. Released a few weeks ago [https://www.reddit.com/r/LocalLLaMA/s/LOPGQvEhCf](https://www.reddit.com/r/LocalLLaMA/s/LOPGQvEhCf)

- by [unknown](#) **&#x21C5; 1**
  <br/> Thanks!

- by [unknown](#) **&#x21C5; 1**
  <br/> GGUF support for omnivoce + perf boost. On RTX 5090:


      
        
          
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

- by [unknown](#) **&#x21C5; 1**
  <br/> Oh nice!

- by [unknown](#) **&#x21C5; 5**
  <br/> Holy shit Irodori TTS mentioned

- by [Quereller](https://www.reddit.com/user/Quereller/) **&#x21C5; 4**
  <br/> Any plans to support ROCm ?

- by [Quereller](https://www.reddit.com/user/Quereller/) **&#x21C5; 3**
  <br/> [u/Quereller](/user/Quereller/) Yes, Check [https://github.com/0xShug0/audio.cpp/pull/48](https://github.com/0xShug0/audio.cpp/pull/48) and [https://github.com/0xShug0/audio.cpp/issues/47](https://github.com/0xShug0/audio.cpp/issues/47)  I’d appreciate it if you (and anyone else with ROCm machines) could help test the models!

- by [unknown](#) **&#x21C5; 3**
  <br/> For old updates and discussions you can check [https://www.reddit.com/r/LocalLLaMA/s/lTLVW0RZo9](https://www.reddit.com/r/LocalLLaMA/s/lTLVW0RZo9) ---  [https://www.reddit.com/r/LocalLLaMA/s/zo1lj9OQVH](https://www.reddit.com/r/LocalLLaMA/s/zo1lj9OQVH) ---  [https://www.reddit.com/r/LocalLLaMA/s/owmHglHjGN](https://www.reddit.com/r/LocalLLaMA/s/owmHglHjGN) --- [https://www.reddit.com/r/LocalLLaMA/s/7RkQwY4mlJ](https://www.reddit.com/r/LocalLLaMA/s/7RkQwY4mlJ)

- by [unknown](#) **&#x21C5; 3**
  <br/> I really appreciate this, you're a lifesaver! THANKS!!!

- by [First_Ad6432](https://www.reddit.com/user/First_Ad6432/) **&#x21C5; 3**
  <br/> need gguf support

- by [First_Ad6432](https://www.reddit.com/user/First_Ad6432/) **&#x21C5; 4**
  <br/> [u/First_Ad6432](/user/First_Ad6432/) Some models already support GGUF. Check the current status [https://github.com/0xShug0/audio.cpp/blob/main/docs/gguf.md](https://github.com/0xShug0/audio.cpp/blob/main/docs/gguf.md) and GGUF checkpoints at [https://huggingface.co/audio-cpp/audio.cpp-gguf](https://huggingface.co/audio-cpp/audio.cpp-gguf)

- by [unknown](#) **&#x21C5; 6**
  <br/> Ty<3, i HATE to deal with the python things

- by [unknown](#) **&#x21C5; 3**
  <br/> GGUF support has been added and will be rolled out model by model.


    That's awesome, it's easily been my biggest wished for feature at this point! That said, I finally got audio.cpp as a backend option for some of my stuff and I've been really happy with it! So nice to be able to just easily jump between the various options with a shared infrastructure.

- by [unknown](#) **&#x21C5; 3**
  <br/> Glad to hear that! You can check the current GGUF support status here [https://github.com/0xShug0/audio.cpp/blob/main/docs/gguf.md](https://github.com/0xShug0/audio.cpp/blob/main/docs/gguf.md)  and GGUF checkpoints are available here [https://huggingface.co/audio-cpp/audio.cpp-gguf](https://huggingface.co/audio-cpp/audio.cpp-gguf)

If there’s a model you'd like to see receive GGUF support, feel free to open an issue.

- by [Potential-Gold5298](https://www.reddit.com/user/Potential-Gold5298/) **&#x21C5; 3**
  <br/> I like electronic music like ambient, techno, IDM, etc. What models would you recommend (something not too heavy - up to 10B params).

- by [Potential-Gold5298](https://www.reddit.com/user/Potential-Gold5298/) **&#x21C5; 4**
  <br/> [u/Potential-Gold5298](/user/Potential-Gold5298/) 10B is a lot :). You can try the three music gen models (ace step, heartmula and stable audio 3) in audio.cpp.They were hand-picked by me.

- by [unknown](#) **&#x21C5; 3**
  <br/> OH MY GOD... THANKS!!!

- by [unknown](#) **&#x21C5; 3**
  <br/> Bro, if you're going to generate Sherlock Holmes narration, at least use a British accent. :)

- by [unknown](#) **&#x21C5; 2**
  <br/> 😄 Good point!

- by [Green-Ad-3964](https://www.reddit.com/user/Green-Ad-3964/) **&#x21C5; 2**
  <br/> Only English? I'd need italian for real time tts.

- by [Green-Ad-3964](https://www.reddit.com/user/Green-Ad-3964/) **&#x21C5; 3**
  <br/> [u/Green-Ad-3964](/user/Green-Ad-3964/) Try omnivoice in audio.cpp. There are other TTS models in audio.cpp --- [https://github.com/0xShug0/audio.cpp#supported-models](https://github.com/0xShug0/audio.cpp#supported-models)

- by [Silver-Champion-4846](https://www.reddit.com/user/Silver-Champion-4846/) **&#x21C5; 2**
  <br/> Does it get faster with avx512 on cpu?

- by [Silver-Champion-4846](https://www.reddit.com/user/Silver-Champion-4846/) **&#x21C5; 2**
  <br/> [u/Silver-Champion-4846](/user/Silver-Champion-4846/) I don’t think so. The CPU I tested supports AVX-512.

- by [unknown](#) **&#x21C5; 1**
  <br/> Well unfortunate

- by [unknown](#) **&#x21C5; 1**
  <br/> Fish s2? Higgs v3?

- by [unknown](#) **&#x21C5; 1**
  <br/> Yes, they are under development. Check current model support status [https://github.com/0xShug0/audio.cpp#supported-models](https://github.com/0xShug0/audio.cpp#supported-models)

- by [ReactionaryPlatypus](https://www.reddit.com/user/ReactionaryPlatypus/) **&#x21C5; 1**
  <br/> Great project. How about support for RVC (RVC, Mangio, RVC2, etc). I know they are a few years old but I still use them and I have not heard better solutions for voice 2 voice.

- by [ReactionaryPlatypus](https://www.reddit.com/user/ReactionaryPlatypus/) **&#x21C5; 2**
  <br/> [u/ReactionaryPlatypus](/user/ReactionaryPlatypus/) Would you like to submit a model request issue?

- by [apoptosist](https://www.reddit.com/user/apoptosist/) **&#x21C5; 1**
  <br/> Great work! Will there be more binary Windows releases? Thanks!

- by [apoptosist](https://www.reddit.com/user/apoptosist/) **&#x21C5; 2**
  <br/> [u/apoptosist](/user/apoptosist/) Yes, watch here [https://github.com/0xShug0/audio.cpp/releases](https://github.com/0xShug0/audio.cpp/releases). I will upload release 0.3 soon.

- by [apoptosist](https://www.reddit.com/user/apoptosist/) **&#x21C5; 1**
  <br/> Awesome, thanks!

- by [apoptosist](https://www.reddit.com/user/apoptosist/) **&#x21C5; 1**
  <br/> [u/apoptosist](/user/apoptosist/) The Windows releases have been updated to v0.3.

- by [Zerochaucha](https://www.reddit.com/user/Zerochaucha/) **&#x21C5; 1**
  <br/> For the releases, is it possible to separate the cuda files from the rest as not to download again the cuda files each time?

Great work by the way, thanks.

- by [Zerochaucha](https://www.reddit.com/user/Zerochaucha/) **&#x21C5; 2**
  <br/> [u/Zerochaucha](/user/Zerochaucha/) Thanks, that’s a really good suggestion! I will update the release later tonight.

- by [Zerochaucha](https://www.reddit.com/user/Zerochaucha/) **&#x21C5; 3**
  <br/> [u/Zerochaucha](/user/Zerochaucha/) The CUDA files are packaged separately in `audiocpp-windows-cuda-runtime.zip`.

- by [unknown](#) **&#x21C5; 1**
  <br/> SopranoTTS support?

- by [unknown](#) **&#x21C5; 2**
  <br/> Not yet.

- by [Zangwuz](https://www.reddit.com/user/Zangwuz/) **&#x21C5; 1**
  <br/> Thank you again, is it possible to add streaming support for omnivoice too ?Since it's a popular model, i don't think it would be a waste of time. One of its strong advantage is the multilingual capability of this model is decent with a right sample compared to many of them.

- by [Zangwuz](https://www.reddit.com/user/Zangwuz/) **&#x21C5; 1**
  <br/> Sure! I'll prioritize this after wrapping up the v0.4 release.

- by [Zangwuz](https://www.reddit.com/user/Zangwuz/) **&#x21C5; 1**
  <br/> [u/Zangwuz](/user/Zangwuz/) will work on streaming. Just pushed a change to add quant support + perf boost for Omnivoice.

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

- by [Zangwuz](https://www.reddit.com/user/Zangwuz/) **&#x21C5; 2**
  <br/> [u/Zangwuz](/user/Zangwuz/) please check the latest commit. Streaming support for omnivoce done. The TTFT depends on chunk size. For 50-char chunk TTFT ranges from 213.135 ms to 280.470 ms

- by [unknown](#) **&#x21C5; 2**
  <br/> Excellent, yes i tried it on audiocpp_server.exe and the streaming works, not related but the possibility to bind ref_text and audio to a voice preset is a nice addition aswell. Thank very much for your dedication.

- by [unknown](#) **&#x21C5; 1**
  <br/> Good catch. Would you like to submit an issue so I can track?

- by [unknown](#) **&#x21C5; 1**
  <br/> If you are talking about the voice preset, i meant it works too. talked about this because we couldn't do it before and now i can just put a "voice_id" it seems on openai api compatible setup as long as the server.json file has the preset with ref_text and audio or i understood it wrong ?

- by [unknown](#) **&#x21C5; 1**
  <br/> Ah, never mind. I thought you were suggesting a new voice preset feature for cli. And yes you can do voice preset for server.

- by [randomfuckingname010](https://www.reddit.com/user/randomfuckingname010/) **&#x21C5; 1**
  <br/> kokoro support?

- by [randomfuckingname010](https://www.reddit.com/user/randomfuckingname010/) **&#x21C5; 1**
  <br/> [u/randomfuckingname010](/user/randomfuckingname010/) No. The model requires special dependencies that aren't portable across a broader range of platforms so it won't go into the core models.

- by [Good_Guide4285](https://www.reddit.com/user/Good_Guide4285/) **&#x21C5; 1**
  <br/> Can you try and add Omnivoice too ?

- by [Good_Guide4285](https://www.reddit.com/user/Good_Guide4285/) **&#x21C5; 1**
  <br/> Hi [u/Good_Guide4285](/user/Good_Guide4285/) Omnivoice was included already.

- by [Good_Guide4285](https://www.reddit.com/user/Good_Guide4285/) **&#x21C5; 1**
  <br/> yes i saw later on. But i have nvidia gtx 1660 ti . does it have Cuda support for this project ? i would love to try this project. its looks amazing.

- by [Good_Guide4285](https://www.reddit.com/user/Good_Guide4285/) **&#x21C5; 1**
  <br/> I'm not sure about 1600ti, but for some smaller models you can try CPU backend.

- by [Good_Guide4285](https://www.reddit.com/user/Good_Guide4285/) **&#x21C5; 1**
  <br/> Cpu cannot handle those big models.  Also Omni has supports 85 language but you only add 2 . i didnot understand why or am i missing something ?

- by [Good_Guide4285](https://www.reddit.com/user/Good_Guide4285/) **&#x21C5; 1**
  <br/> [u/Good_Guide4285](/user/Good_Guide4285/) I'm actually a little confused because Omnivoce support 600+ lanuges and audio.cpp README lists it. Could you tell me where did you get the "2" from? I'd like to fix it if it is stale doc. There are serveral small models designed for CPU such as Supertonic3. For Omnivoce, it is 1.6 GB and can run on CPU without any issue.


      
        
          
              **omnivoice**
            
              TTS, Clone, Design, Ctrl
            
              646+ langs
            
              OmniVoice, Qwen3-0.6B based
            
              GGUF 16/Q8, Stream

- by [unknown](#) **&#x21C5; 1**
  <br/> maybe its my bad. I tried Omnivoice App from their website and tried with my Cuda gtx 1660 i. i tried to create 1 hour long voiceover after 9 hours it wasnot still finished. I cannot think about with Cpu. it would take a week to produce 1 hour long voice with chunks.

- by [unknown](#) **&#x21C5; 1**
  <br/> I don’t think you were using audio.cpp. The is our repo [https://github.com/0xShug0/audio.cpp](https://github.com/0xShug0/audio.cpp)

- by [unknown](#) **&#x21C5; 1**
  <br/> i downloaded this "audiocpp-windows-cuda-portable-bb15edd7" but i didnot even understand how to use this. its looks so complex. is there a Gui ?

- by [unknown](#) **&#x21C5; 2**
  <br/> Yes. you can run `audiocpp_server --ui --backend cuda` and open [`http://127.0.0.1:8080/`](http://127.0.0.1:8080/)  in your broswer.
