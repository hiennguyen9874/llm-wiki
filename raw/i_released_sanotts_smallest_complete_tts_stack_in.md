# I released sanoTTS: smallest complete TTS stack in 294k params (337 KB) that runs on $3 microcontroller and a 1.46m one that beats models 3x and 10x it's size [Visit](https://www.reddit.com/r/LocalLLaMA/comments/1w6lmmg/i_released_sanotts_smallest_complete_tts_stack_in/)
### **Subreddit:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA)
### **Author:** [u/Affectionate_Hat_585](https://www.reddit.com/user/u/Affectionate_Hat_585/)
### **Vote:** 509
---
I have been trying to squeeze TTS stack down far enough to run in a $3 chip which has 512kb of SRAM without NPU. While trying to get to that milestone i built sanoTTS which has
- 11 voices, 6 languages
- params size ranging from 294k - 2.2m. For comparison we are 244x smaller than kokoro, 9000x smaller than voxtral TTS
- 1.5m model has a SCOREQ of 4.13 and UTMOS of 4.10
- 337kb for 294k model when quantized into int8
- can be run in website with web assembly `npm install sanotts-web`
- there is a recipe to follow so that you can extend to more languages, voice
I can tell you with confidence that this family release contains the smallest neural TTS model ever with around 2% WER on whisper.
Please check it out on : [https://github.com/ampixa/sanoTTS](https://github.com/ampixa/sanoTTS)
for live demo: [https://tts.ampixa.com/sanoTTS](https://tts.ampixa.com/sanoTTS)
HF: [https://huggingface.co/ampixa/sanoTTS](https://huggingface.co/ampixa/sanoTTS)
on SCOREQ sanoTTS-Amy(1.51m) is better than Inflect Nano(4.63m) and KittenTTS(15m) i.e 4.13 vs 3.81 vs 3.02
on esp32 microcontroller we are getting RTF of 0.225 which in plain terms means 4sec of audio is generated in 1sec
Happy to answer your queries.
---
## Comments 121

- by [Affectionate_Hat_585](https://www.reddit.com/user/Affectionate_Hat_585/) **&#x21C5; 77**
  <br/> Sounds great, please help get it added to audio.cpp!

- by [Affectionate_Hat_585](https://www.reddit.com/user/Affectionate_Hat_585/) **&#x21C5; 42**
  <br/> Audio.cpp looks cool. will open a PR

- by [unknown](#) **&#x21C5; 9**
  <br/> Great! I added a star, this sounds so good for the size.

- by [Affectionate_Hat_585](https://www.reddit.com/user/Affectionate_Hat_585/) **&#x21C5; 6**
  <br/> [u/Affectionate_Hat_585](/user/Affectionate_Hat_585/) Great model! Is this PR from you? [https://github.com/0xShug0/audio.cpp/pull/449](https://github.com/0xShug0/audio.cpp/pull/449) Crazy week we got many new model PRs, including the official VibeASR port from the MS team --- during my vacation 🥲

Update: Awesome model! PR merged in audio.cpp! Tested on CPU.

I regret I didn't include it in 0.7.2 (just released).


      
        
          
              Voice
            
              Graph
            
              Lang
            
              WAV
            
              Duration
            
              RTF
            
              ASR Result
            
        
        
      

      
        
            
                heart-nano
              
                nano
              
                en
              
                `heart_nano.wav`
              
                5.099s
              
                0.0027
              
                OK
              
          
            
                heart
              
                nano
              
                en
              
                `heart.wav`
              
                5.205s
              
                0.0044
              
                OK
              
          
            
                amy
              
                piperlite
              
                en
              
                `amy.wav`
              
                4.272s
              
                0.0362
              
                OK
              
          
            
                hfc
              
                piperlite
              
                en
              
                `hfc.wav`
              
                3.831s
              
                0.0350
              
                OK
              
          
            
                kristin
              
                piperlite
              
                en
              
                `kristin.wav`
              
                3.495s
              
                0.0390
              
                OK
              
          
            
                vi
              
                piperlite
              
                vi
              
                `vi.wav`
              
                2.299s
              
                0.0332
              
                OK
              
          
            
                id
              
                piperlite
              
                id
              
                `id.wav`
              
                4.063s
              
                0.0321
              
                OK

- by [Affectionate_Hat_585](https://www.reddit.com/user/Affectionate_Hat_585/) **&#x21C5; 2**
  <br/> Not from me but maybe from somebody connected with [u/Affectionate_Hat_585](/user/Affectionate_Hat_585/)? Hope you have a good vacation--no need to rush all this stuff!

- by [unknown](#) **&#x21C5; 32**
  <br/> This is mind-blowing, the possibilities with IoT devices are insane.

- by [unknown](#) **&#x21C5; 15**
  <br/> Yes, with enough prosodical control. this has so many usecases... I assume even now it might help a bunch of people

- by [unknown](#) **&#x21C5; 2**
  <br/> so cool!

- by [unknown](#) **&#x21C5; 1**
  <br/> Can't wait to have my toilet talk to me!

- by [unknown](#) **&#x21C5; 1**
  <br/> And make all sort of dirty talks per dump you drop in it? No thanks.

- by [unknown](#) **&#x21C5; 1**
  <br/> Username doesn't check out

- by [unknown](#) **&#x21C5; 1**
  <br/> I'm sorry for not being into scat

- by [unknown](#) **&#x21C5; 20**
  <br/> I want this on my homeassistant voice preview edition! And german :P so my wife is happy. Is it possible to start outputting the audio before everything is generated?

- by [unknown](#) **&#x21C5; 14**
  <br/> There is small initial latency of when it starts for the ESP32-s3 MCU i tested but after that it's faster than real time so it can process audio faster than it can output it with RAM being constraint. ESP32-s3 only has 512kb or RAM. But for something like ESP32-P4 or Teensy this should be piece of cake.

Will keep German in mind

- by [unknown](#) **&#x21C5; 3**
  <br/> +1 for German and Home Assistant. Great work by the way, please let us know when you need help or resources or anything.

- by [unknown](#) **&#x21C5; 2**
  <br/> thank you for the info!

- by [unknown](#) **&#x21C5; 12**
  <br/> Looks cool!

Any plans to add Spanish?

- by [unknown](#) **&#x21C5; 21**
  <br/> Hey Thanks!!! the plan is to support as many languages as possible....

- by [unknown](#) **&#x21C5; 1**
  <br/> Great....please add Persian too

- by [unknown](#) **&#x21C5; 7**
  <br/> Japanese please

- by [unknown](#) **&#x21C5; 8**
  <br/> Well you are in luck because ayutaz already did that for you [https://github.com/ayutaz/sanoTTS-jp](https://github.com/ayutaz/sanoTTS-jp)

- by [unknown](#) **&#x21C5; 6**
  <br/> Thank you for not referring to you and your LLM as WE.

- by [unknown](#) **&#x21C5; 6**
  <br/> I was going to ask if you plan to release the training data, but then read the docs. Your idea is very cool! Distill an existing TTS teacher into the smaller model! Makes the whole process much simpler and cheaper. Great work!

- by [unknown](#) **&#x21C5; 6**
  <br/> How is this even possible!? This is crazy good for its size. 337KB is smaller than the average webpage these days!

- by [unknown](#) **&#x21C5; 5**
  <br/> Well testament to good diagnostic control and method which took some time to figure out properly. What's amusing is it's just as intelligible (ASR models can perfectly understand the speech) but it loses naturalness. I believe there still is room for some improvement

- by [unknown](#) **&#x21C5; 5**
  <br/> I would love love love to see your training data / workflow… any chance to open source the whole pipeline?

Hell, I’d even pay to see that.

- by [unknown](#) **&#x21C5; 34**
  <br/> please go through the repo on : [https://github.com/ampixa/sanoTTS](https://github.com/ampixa/sanoTTS)

it has some information full paper: [https://arxiv.org/abs/2608.21378](https://arxiv.org/abs/2608.21378)

i dont need money but if you can please donate to pm relief fund for recent flash flood in nepal [https://pmdrf.nchl.com.np/](https://pmdrf.nchl.com.np/)

- by [unknown](#) **&#x21C5; 7**
  <br/> Good human found 😍

- by [unknown](#) **&#x21C5; 5**
  <br/> Could you talk about how you did it?

- by [unknown](#) **&#x21C5; 11**
  <br/> Well it's quite simple.

The TTS has four main parts text frontend: how to convert text to phoneme(unit of sound)

acoustic model: that gives you the spectrogram

duration predictor: how much time to give for each phoneme

decoder: how do you convert spectrogram to real audio

You take a teacher. It can be any model. I have tested for Piper-plus and Kokoro and then get 50000 fivesome with the help of teacher (text, audio, acoustic latent, duration, mel spectrogram)

With teacher and that fivesome, each of the components can be individually trained.

You can start by reading README onhttps://github.com/ampixa/sanoTTS

- by [unknown](#) **&#x21C5; 2**
  <br/> Awesome! Do you know where I could get training data? I want to try making one.

- by [unknown](#) **&#x21C5; 2**
  <br/> the 50000 fivesome and a teacher is your training data. You can repeat the same process for any model.

- by [unknown](#) **&#x21C5; 3**
  <br/> is this small enough to use in my c++ game engine by including a header file, to generate voices quickly without using the GPU?

- by [unknown](#) **&#x21C5; 6**
  <br/> Depends on what is the RSS you are targeting. For esp32 we saw it required *98,224 Bytes* of working memory for the smallest model 294k one.Please note that it's in bytes... On my computer without any optimization tricks it requires max RSS of 1.8MB

And for real time we need to do just 45 million multiply and accumulate operations per second. If that can be done by measly 240Mhz chip, our cpu can do like billions and billions of MAC so yes it can do it without extra accelerators.

But again if you are targeting for something like SNES then it might be hard. But anything with ram above 500kb you should be good to go.

- by [unknown](#) **&#x21C5; 2**
  <br/> im very interested on this

- by [unknown](#) **&#x21C5; 3**
  <br/> can you clone the glados voice :3

- by [unknown](#) **&#x21C5; 3**
  <br/> [](https://preview.redd.it/i-released-sanotts-smallest-complete-tts-stack-in-294k-v0-mzk88g8nahnh1.jpeg?width=596&format=pjpg&auto=webp&s=e4aad541c98f0a3a14824b60892ca2ee22658a9d)
      
    that would be awesome!

- by [unknown](#) **&#x21C5; 2**
  <br/> can you give me some more context please?

- by [unknown](#) **&#x21C5; 2**
  <br/> its a voice for a robot videogame character, who id love to have as TTS. At any rate, I saw you have a section on how to train your own. might give it a spin when I'm not busy

- by [unknown](#) **&#x21C5; 2**
  <br/> [https://www.youtube.com/watch?v=fkr1TLt9IQE](https://www.youtube.com/watch?v=fkr1TLt9IQE)

[https://www.youtube.com/watch?v=l3yVJhcSDR8](https://www.youtube.com/watch?v=l3yVJhcSDR8)

- by [unknown](#) **&#x21C5; 3**
  <br/> How can I get the "heart" voices? they sound awesome?

- by [unknown](#) **&#x21C5; 3**
  <br/> You can use python or js or bare c library

pip install sanotts

import sanotts, soundfile as sf

r = sanotts.synthesize("Hello from a tiny neural voice.", voice="heart-nano")
sf.write("out.wav", r.audio, r.sample_rate)

- by [unknown](#) **&#x21C5; 1**
  <br/> the model is not on huggingface?

- by [unknown](#) **&#x21C5; 3**
  <br/> This is such impressive work — squeezing a full neural TTS stack into a 337KB INT8 blob and running real-time on a generic MCU is absolutely wild.

Funny enough, I landed on a very similar diagnostic mindset while doing INT8 quantized YOLO edge deployment: instead of relying only on aggregate mAP or overall accuracy metrics, I use reference-vs-deployed sequence-level parity checks (FP32 reference vs INT8 deployed model) to catch frame-by-frame behavioral drift across video sequences.

Quick question: since you mentioned building custom artifact detectors, did you do any step-by-step or position-resolved divergence analysis across the audio sequence? Or did you mostly rely on aggregate SCOREQ / MOS metrics to validate quality end-to-end?

- by [unknown](#) **&#x21C5; 2**
  <br/> Most of it was aggregate SCOREQ. But at some point it wasn't improving, so first step was to divide the decoder audio into various freq channels and seeing where the problem is coming from. I found out it was with /z/ and it's neighbours. And 1-6kHz has some serious metallic artifacts. Took the worst decoder configuration and the teacher at those bands to train another model

- by [unknown](#) **&#x21C5; 2**
  <br/> Ah that makes perfect sense. You localized the divergence in the frequency domain instead of the time/sequence domain. Pinpointing that 1–6 kHz band to target the INT8 degradation is exactly the kind of granular fix you never get from just a top-level SCOREQ number. Funny how that pattern pops up everywhere — aggregate metrics always hide where the real problem is. I’ve been messing with the same idea but on the LLM KV cache side, splitting divergence along context length instead of frequency.

Good stuff, thanks for sharing the breakdown.

- by [unknown](#) **&#x21C5; 3**
  <br/> Wow, that Nepali voice sound nice, Also you name it Sano , are you nepali ?

- by [unknown](#) **&#x21C5; 3**
  <br/> Yes i am nepali

- by [unknown](#) **&#x21C5; 3**
  <br/> where does it make sense to use small models ?

- by [unknown](#) **&#x21C5; 3**
  <br/> oh snap. this gonna have to be added to my bench. great work.

[https://github.com/5uck1ess/tts-bench](https://github.com/5uck1ess/tts-bench)

- by [unknown](#) **&#x21C5; 1**
  <br/> this has been added to the bench.

- by [unknown](#) **&#x21C5; 2**
  <br/> wow wow make it cool

- by [unknown](#) **&#x21C5; 2**
  <br/> I'm astonished we can squeeze things down this small and still maintain this sort of quality.

- by [unknown](#) **&#x21C5; 2**
  <br/> Looks I have on demand audiobooks on my phone now. Thanks! This is mind-blowing indeed how small it is.

Double appreciate your short well exampled demo video in the post.

- by [unknown](#) **&#x21C5; 2**
  <br/> Thanks... I have put lots of effort into this.

- by [unknown](#) **&#x21C5; 2**
  <br/> Too bad not Italian and German.

- by [unknown](#) **&#x21C5; 2**
  <br/> e-speak supports italian and german so this should be doable

- by [unknown](#) **&#x21C5; 2**
  <br/> This is amazing, can you add Urdu/Punjabi?

- by [unknown](#) **&#x21C5; 2**
  <br/> sure, i will add it to backlog. so far german, spanish , italian and urdu

- by [unknown](#) **&#x21C5; 2**
  <br/> I tried creating an app with your SanoTTS for iPhone, i could not get it to load. Any pointers?

- by [unknown](#) **&#x21C5; 1**
  <br/> we have c99 target already. I can help you.. where are you facing problem actually?

- by [unknown](#) **&#x21C5; 1**
  <br/> In case you are adding Urdu, Hindi should not be that far away.

- by [unknown](#) **&#x21C5; 2**
  <br/> There is a already a hindi voice

- by [unknown](#) **&#x21C5; 2**
  <br/> "Amy" is so cool.

Chinese model sounds robotic. Could it be made on-par with Amy?

- by [unknown](#) **&#x21C5; 1**
  <br/> Yes ofc. Models other than English weren't given much love. The main problem will be diagnostic control. we have SCOREQ, ASR and i even had a custom siblant and metallic artifact detector built for English.

For Chinese we can also solve likewise given that it's a high resource language

- by [unknown](#) **&#x21C5; 2**
  <br/> OMG SO COOL

- by [unknown](#) **&#x21C5; 2**
  <br/> Cool!

- by [unknown](#) **&#x21C5; 2**
  <br/> Amazing! Nice job!

- by [unknown](#) **&#x21C5; 2**
  <br/> Wow the Heart one runs SO fast and has great pronunciation! It's not super clear to me how to run it myself, but I see there is a release there, and will be playing with it soon. Thank you for sharing!

- by [unknown](#) **&#x21C5; 2**
  <br/> Hey there you just head to github.com/ampixa/sanoTTS on steps to run it.

with python

pip install sanotts

import sanotts, soundfile as sf

r = sanotts.synthesize("Hello from a tiny neural voice.", voice="heart-nano")
sf.write("out.wav", r.audio, r.sample_rate)with js please check [https://github.com/Ampixa/sanoTTS#deploy-on-your-own-site](https://github.com/Ampixa/sanoTTS#deploy-on-your-own-site)

- by [unknown](#) **&#x21C5; 2**
  <br/> That's great! Are you planning to add French soon?

- by [unknown](#) **&#x21C5; 2**
  <br/> Yes french will be added soon

- by [unknown](#) **&#x21C5; 2**
  <br/> I love how the fewer parameters you use, the more "whispery" the model sounds. Amazing stuff, thank you for this, and will use it in my projects.

- by [unknown](#) **&#x21C5; 2**
  <br/> Nice Project. Can it run in PSRam? There are many boards eith 8MB external RAM

- by [unknown](#) **&#x21C5; 1**
  <br/> With chip that can do 29+ MMAC, it can comfortably run. You just somehow need to hold around ~337kb of storage. ESP32 supports XIP which allows you to execute code right from flash. I am using that here... But i also tested loading on PSRAM. There is a slight penalty when you put the weights on PsRAM

- by [unknown](#) **&#x21C5; 2**
  <br/> Local voice in a robot controlled by vllm  on litlle cheep addon. Great project!

- by [unknown](#) **&#x21C5; 2**
  <br/> Really cool project

- by [unknown](#) **&#x21C5; 2**
  <br/> Brudda this is cool af

- by [unknown](#) **&#x21C5; 2**
  <br/> does it support voice cloning / custom voices?

- by [unknown](#) **&#x21C5; 1**
  <br/> There is a recipe to follow which can clone teacher models. But not zero shot cloning

- by [unknown](#) **&#x21C5; 2**
  <br/> Impressive

- by [unknown](#) **&#x21C5; 2**
  <br/> Heart-nano is my favorite voice/model there. And the voice “English” reminds me of GLaDOS. I feel like these voices would be perfect for small video games for different characters especially if you pitch the voices up and down.

- by [unknown](#) **&#x21C5; 2**
  <br/> Voice cloning?

- by [unknown](#) **&#x21C5; 1**
  <br/> zero shot voice cloning isn't supported.

- by [unknown](#) **&#x21C5; 2**
  <br/> Got my Agent to read through the repo, so i can build a workflow to use a larger model for zero shot, then use your model to create a smol version. Very cool. Im impressed.

- by [unknown](#) **&#x21C5; 2**
  <br/> How can I add more languages?

- by [Affectionate_Hat_585](https://www.reddit.com/user/Affectionate_Hat_585/) **&#x21C5; 2**
  <br/> [u/Affectionate_Hat_585](/user/Affectionate_Hat_585/)

Awesome model! PR merged in audio.cpp! Tested on CPU.


      
        
          
              Voice
            
              Graph
            
              Lang
            
              WAV
            
              Duration
            
              RTF
            
              ASR Result
            
        
        
      

      
        
            
                
              
                
              
                
              
                
              
                
              
                
              
                
              
          
            
                heart-nano
              
                nano
              
                en
              
                `heart_nano.wav`
              
                5.099s
              
                0.0027
              
                OK
              
          
            
                heart
              
                nano
              
                en
              
                `heart.wav`
              
                5.205s
              
                0.0044
              
                OK
              
          
            
                amy
              
                piperlite
              
                en
              
                `amy.wav`
              
                4.272s
              
                0.0362
              
                OK
              
          
            
                hfc
              
                piperlite
              
                en
              
                `hfc.wav`
              
                3.831s
              
                0.0350
              
                OK
              
          
            
                kristin
              
                piperlite
              
                en
              
                `kristin.wav`
              
                3.495s
              
                0.0390
              
                OK
              
          
            
                vi
              
                piperlite
              
                vi
              
                `vi.wav`
              
                2.299s
              
                0.0332
              
                OK
              
          
            
                id
              
                piperlite
              
                id
              
                `id.wav`
              
                4.063s
              
                0.0321
              
                OK

- by [unknown](#) **&#x21C5; 1**
  <br/> Thanks a ton

- by [unknown](#) **&#x21C5; 2**
  <br/> Awesome!How fine-tuneable is it for adding other languages? Asking for Persian 🇮🇷

- by [unknown](#) **&#x21C5; 2**
  <br/> you just need a teacher and a text frontend. Everything else can be followed with the help of recipe

- by [unknown](#) **&#x21C5; 2**
  <br/> Awesome! Can the teacher be a closed model? I have the G2P front end

- by [unknown](#) **&#x21C5; 2**
  <br/> yes but it's going to be extra work.

you convert the audio into mel-100 spectrogram (easy) you target audio to mel-100 spectrogram with acoustic modeller. You have to train this (somewhat easy) you have to think about duration predictor too. Something like MFA or whatever is good (you have to think how) mel-100 to audio (recipe gives you)

- by [unknown](#) **&#x21C5; 2**
  <br/> Punjabi support please

- by [unknown](#) **&#x21C5; 1**
  <br/> A 10-second delay after every period.

.

.

.

.

.

.

.

.

.

.

And I already have espeak-ng on my linux machine.  Might be nice for generating new voices though.

- by [unknown](#) **&#x21C5; 2**
  <br/> Not sure i understand. If that is a bug report. Thanks really but can you give me the sentence with which i can replicate this...

- by [unknown](#) **&#x21C5; 1**
  <br/> Any sentence I tried.  Sorry I can't be of more assistance.

- by [unknown](#) **&#x21C5; 1**
  <br/> Is whisper the best model to check for WER still? Maybe multi-lingual but

- by [unknown](#) **&#x21C5; 2**
  <br/> well for a 10 sec clip it makes sense. I did test with wav2vec too which gave me good results

- by [unknown](#) **&#x21C5; 1**
  <br/> Have you tried "fifteen" and "fifty" through the tiny speaker? That's the kind of mix-up I'd worry about with spoken instructions.

- by [unknown](#) **&#x21C5; 1**
  <br/> TTS on an ESP? This is insane!
