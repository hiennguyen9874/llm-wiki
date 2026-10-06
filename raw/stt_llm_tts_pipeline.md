# STT -> LLM -> TTS pipeline [Visit](https://www.reddit.com/r/LocalLLaMA/comments/1ts0jjb/stt_llm_tts_pipeline/)
### **Subreddit:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA)
### **Author:** [u/UniqueIdentifier00](https://www.reddit.com/user/u/UniqueIdentifier00/)
### **Vote:** 16
---
Hey guys, I’m trying to learn about how to better create a STT LLM TTS pipeline.
My current setup is running a 3090 on Ubuntu. I use llama.cpp to run Qwen 3.6 27B Q4 with pi-agent for tool calling, and I just run everything in the terminal, I haven’t really bothered with chat style front ends.
I’m trying to figure out how the actual pipeline goes when using 3 models to process information like that. I understand how to run a single model obviously, but as someone who isn’t a trained coder, I don’t really understand what sort of framework is used to pipe information from the STT model to the LLM, and back out to the TTS model. Am I running three llama.cpp instances?
Need some guidance. Thanks!
---
## Comments 30

- by [unknown](#) **&#x21C5; 6**
  <br/> Not three llama.cpp instances — three different services, each specialized for one job. The "framework" connecting them is just HTTP requests. Simpler than it sounds.

  1. STT — audio in, text out. faster-whisper runs great on a 3090. There's a ready-made server (faster-whisper-server) that gives you an OpenAI-compatible endpoint. You POST a recording, you get text back.
  2. LLM — you already have this. llama.cpp + Qwen. Don't touch it.
  3. TTS — text in, audio out. Piper is fast and runs on CPU, so your GPU stays free for the other two. Decent voices out of the box. Kokoro if you want higher quality later.

I should note faster-whisper-server has since evolved into [speaches-ai/speaches](https://github.com/speaches-ai/speaches/) — same author, now bundles both STT and TTS in one OpenAI-compatible server. If you  want fewer moving parts to start with, it can cover two of the three slots in a single container.

speaches is how I got my feet wet, broke away from it used what was needed, fine tuned  model for my voice, custom vocabulary "hotwords", and "I've" since build a record+audio in/out client in Go, custom container for STT and one for a router between me and LLM, TTS and my local Go audio client the listens so my agents running on remote hosts (usually the one where this stuff all lives) can also "speak" their replies through my speakers.

The pipeline is literally:

record audio → POST to STT server → text → POST to llama.cpp → response → POST to TTS → play audio

Each service runs as its own process (or Docker container — docker compose is the natural way to run them side by side on Ubuntu). A Python script with requests and pyaudio can wire the whole loop in under 100 lines. No special framework needed.

- VAD (Voice Activity Detection) is what turns this from a walkie-talkie into a conversation. It detects when you start/stop talking so the system knows when to send audio to transcription without you pressing buttons. Silero VAD is the standard — small, fast, accurate, and it runs on CPU.

- Sample rates will cause the most confusing early bugs. Your mic captures at 48kHz, Whisper wants 16kHz, TTS outputs at 22–24kHz. When transcriptions come back garbled, nine times out of ten it's a sample rate mismatch somewhere in the chain, not a model problem. Just something to know so you don't chase ghosts.

- Keep TTS on CPU. Your 3090 has 24GB — you want that for faster-whisper + Qwen. Piper is fast enough on CPU that you won't notice the difference. Fighting three models for VRAM on one card is pain you don't need.

The basic loop can work in an afternoon once you see it's just HTTP between three services. Making it feel good — streaming responses so TTS starts before the full reply is done, proper VAD so it flows naturally, latency tuning — that's where the real craft lives. But the foundation is straightforward and the goal is closer than it probably looks from where you're standing.

Happy to go deeper on any piece of this if you want to DM — I've been building  and iterating on exactly this kind of pipeline for a while.

- by [unknown](#) **&#x21C5; 1**
  <br/> The pipeline is literally:

record audio → POST to STT server → text → POST to llama.cpp → response → POST to TTS → play audio


    Adding to that, you can chunk and async the llama.cpp response to POST to TTS part. Send the first few words or first complete sentence to TTS to get generated audio out quickly, streaming that out first so there's minimal latency.

Then you send the remaining llama.cpp response to TTS to get the rest of the audio response.

I prefer sending the first full sentence to get more realistic TTS output from models like Kokoro. There's a difference between "I want a..." and "I want a pizza right now!"

I wish there was a way to reduce latency if there's a RAG pipeline in the middle:

record audio → POST to STT server → text → POST to Python service for RAG → text context → POST to llama.cpp → response → POST to TTS → play audio

- by [unknown](#) **&#x21C5; 1**
  <br/> You reminded me of something similar about chunking for STT, so I went home and asked for some pointers (that I don't know about but our friend does)


      
    Exactly right on sentence-level chunking — we've found the same thing.


      Full sentence to TTS first, stream the rest behind it. The quality difference over word-by-word is real, especially with Kokoro.


    
      
    
      On the RAG latency — the retrieval step itself is usually negligible (embed query + vector search is sub-200ms). The latency RAG actually introduces is on the LLM side — it's now processing a bigger prompt with the retrieved context. So the lever is keeping your retrieved chunks short and surgical. The streaming + sentence-chunking strategy you already described is still your best friend there — it works the same whether RAG is in the pipe or not.

- by [unknown](#) **&#x21C5; 5**
  <br/> Lots of ways to do it, my preference has been to separate the inference services from the application, so I typically run multiple back-ends hosting various models across the available hardware and put them behind go-llm-proxy on a single host endpoint, and then worry about the application side development with just a single api key to use whatever models are joined on the proxy.

Defining clear lines and delineating responsibility for hosting vs application makes it more flexible and less likely to get lost imo.

For stt I use whisper, tts I use xtts, and for the models qwen or MiniMax are usually my go-tos.   Develop the glue and loop in go and it’s usually pretty quick and reliable for me.

- by [unknown](#) **&#x21C5; 2**
  <br/> The jargon there is a little dense for me, but I think I get the gist. I’ll do some more research since you’ve given me some good starting topics there. Thank you!

- by [unknown](#) **&#x21C5; 1**
  <br/> I'm working on exactly that... I'm trying to polish some code before i really put effort in the stt part... maybe we can share some of the effort if my project fits you... [https://github.com/fdev31/minia](https://github.com/fdev31/minia)

- by [unknown](#) **&#x21C5; 3**
  <br/> This is a good bet for your hardware right now, surprisingly fast responses, basically real time with a small param text generator.

Parakeet V3 -> Qwen3.6 (A3B would be way faster but whatever you want)-> Kokoro

Parkeet STT openAI compatible sever [https://github.com/achetronic/parakeet](https://github.com/achetronic/parakeet)

Kokoro TTS openAI compatible server [https://github.com/remsky/Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI)

I'd recommend deploying on OpenWebUI too, it has a very slick "conversation" implementation that can leverage these TTS/STT servers.

- by [unknown](#) **&#x21C5; 2**
  <br/> You got TTS and STT backwards (fixed now)

- by [unknown](#) **&#x21C5; 1**
  <br/> lol you are right

- by [unknown](#) **&#x21C5; 2**
  <br/> This is good info thanks. I really don’t want to lose Pi-agent. I’ll try to work with it to develop a better interface. If all else fails I’ll go to OpenWebUI.

Thank you!

- by [unknown](#) **&#x21C5; 2**
  <br/> You could look at the project Wyoming stack that home assistant uses. Someone has also made a drop in copy of nvidias parakeet tts to replace whisper in the stack. It's much faster to first text. They do streaming,  chunked by sentence boundaries, I believe.

- by [unknown](#) **&#x21C5; 2**
  <br/> Thanks, I’ll check it out!

- by [unknown](#) **&#x21C5; 1**
  <br/> I'm using `whisper.cpp`, `llama.cpp`, and `kokoro`. Slowly working on an implementation here: [https://code.chimeric.al/chimerical/odidere](https://code.chimeric.al/chimerical/odidere). It's about 15,000 lines of code.

- by [unknown](#) **&#x21C5; 1**
  <br/> I'll get you my docker compose soon with my pipeline. Faster whisper, Kokoro, and llama.cpp with Gemma4 26b. You want parallelism of at least 2 if you got more than one service with voice assistants, so you aren't waiting. Low latency is key.

- by [unknown](#) **&#x21C5; 1**
  <br/> For short utterances (a few seconds, what your speech turns are likely to be), consider using Parakeet v2 over whisper. My tests for this exact purpose got me ~5x the speed with Parakeet v2 over whisper. Parakeet v*3* is multi-language and not as fast because of the increased breadth, so use v2 if you're speaking in English. The difference in speed comes down to (simplifying here) how the different models chunk the incoming audio.

- by [unknown](#) **&#x21C5; 1**
  <br/> I created this [Conversational AI Harness](https://github.com/thomas9120/Conversational-AI-Harness). You're welcome to fork it and tweak it how you'd like.

- by [unknown](#) **&#x21C5; 1**
  <br/> [https://github.com/collabora/WhisperLive](https://github.com/collabora/WhisperLive) -> some model -> [https://github.com/OHF-Voice/piper1-gpl](https://github.com/OHF-Voice/piper1-gpl)

- by [unknown](#) **&#x21C5; 1**
  <br/> I use whisper, Ollama, and GPT-SoVITs. Whisper and SoVITs are relatively lite, and then Ollama is whatever model I can support. I run all this off my 3080ti. This is all wrapped by Python. And I actually have it setup to work with a 3D avatar as well. I’ve been building out a Unity Project to make the 3D avatar more animated too.

- by [unknown](#) **&#x21C5; 1**
  <br/> You don't need a framework for everything.

ASR & TTS can be behind FastAPI or PyTriton if you are comfortable with figuring out batching or streaming.

You can have a simple python backend which takes audio from whatever your frontend is & pass the input & output to each service as needed.

Pipecat & Livekit are good end to end pipelines but not mandatory at all.

- by [unknown](#) **&#x21C5; 1**
  <br/> Posted an example using Whisper.cpp, llama.cpp and Piper for exactly this here a while ago: [https://www.reddit.com/r/LocalLLaMA/comments/1nj673e/stt_llm_tts_pipeline_in_c/](https://www.reddit.com/r/LocalLLaMA/comments/1nj673e/stt_llm_tts_pipeline_in_c/)

- by [unknown](#) **&#x21C5; 0**
  <br/> I cut out the STT -> LLM pipeline by using an Omni model in Llama CPP. Better latency at the cost of a smaller LLM selection

- by [unknown](#) **&#x21C5; 1**
  <br/> Nemotron Nano Omni is by far the smartest one with Llama CPP right now.

- by [unknown](#) **&#x21C5; 1**
  <br/> Will there be support for other languages?
