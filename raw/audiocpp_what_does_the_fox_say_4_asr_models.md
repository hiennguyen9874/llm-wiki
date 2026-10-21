# [audio.cpp] What Does the Fox Say: 4 ASR models (Nemotron 3.5 ASR, Higgs Audio STT, VibeVoice ASR, and Hviske ASR) in native C++/GGML, init streaming support, and 327s of audio transcribed in 2.17s. [Visit](https://www.reddit.com/r/LocalLLaMA/comments/1urd4ln/audiocpp_what_does_the_fox_say_4_asr_models/)
### **Subreddit:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA)
### **Author:** [u/Acceptable-Cycle4645](https://www.reddit.com/user/u/Acceptable-Cycle4645/)
### **Vote:** 58
---
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
**Update(07/18/2026)**: Voxtral ASR streaming released
On RTX 5090:
Cli:
GGUF
Measured audio
Measured session.wall_ms
RTF
Speed
BF16
27.394s
2312.030 ms
0.0844
11.85x RT
Q8_0
27.394s
1671.272 ms
0.0610
16.39x RT
Server:
Streaming mode + multipart upload:
GGUF
Server TTFT
Client observed TTFT
Peak VRAM
BF16
208.786 ms
210.831 ms
10082 MiB
Q8_0
170.508 ms
173.336 ms
6495 MiB
Longform 30min audio (streaming mode + multipart upload)
GGUF
Client wall
RTF
Speed
Peak VRAM
BF16
411.807 s
0.2288
4.37x RT
12595 MiB
Q8_0
358.631 s
0.1992
5.02x RT
8990 MiB
**Update(07/14/2026):** Release 0.3 adds five new models: Supertonic 3, MOSS-TTS-Local, MOSS-TTS-Nano, IndexTTS2, and Irodori-TTS. Supertonic 3 can hit 200x+ realtime on RTX5090. It can generate 10 hours of audio in 3 mins. Check [https://www.reddit.com/r/LocalLLaMA/s/mLfiWn1mu7](https://www.reddit.com/r/LocalLLaMA/s/mLfiWn1mu7) for demo video!
**Update (07/09/2026):** Just pushed a performance optimization. Updating a single shared module improved performance across 13 models by up to 40%! The released ASR models get a 10%+ performance boost. Check [https://github.com/0xShug0/audio.cpp/blob/release-0.2/docs/depthwise_conv1d_performance.md](https://github.com/0xShug0/audio.cpp/blob/release-0.2/docs/depthwise_conv1d_performance.md)
I just pushed a new audio.cpp update with streaming support and 4 ASR/STT models: Nemotron 3.5 ASR,  Higgs Audio STT, VibeVoice ASR, and Hviske ASR (da only). Overall 1.07x to 2.41x faster than Python.
I decided to drop Parakeet-TDT since good implementations already exist, and I find the Nemotron model more interesting.
Streaming support is also starting to land in audio.cpp.
Right now, I added initial streaming support for two models that naturally fit streaming usage: **Nemotron ASR** and **VoxCPM2**. Nemotron ASR can stream recognition results through SSE, and VoxCPM2 can receive text incrementally and return generated audio chunks. I also experimented with streaming support for **Higgs Audio STT**, though I still treat that path as more experimental because the model/reference behavior is less straightforward.
There is still a lot to improve. The current work is only the first step toward proper model-level and server-level streaming support. **Contributions are very welcome, especially around better streaming APIs, chunk scheduling, lower TTFT, server behavior, and adding streaming paths for more models.**
**The headline result:** Nemotron ASR transcribed a 327.6s audio file in 2.17s offline on RTX5090 with 3.18% WER, and the streaming SSE path produced the same WER with 307ms TTFT and much lower peak VRAM.  VibeVoice ASR gave the lowest WER on this test, but it is much heavier. Nemotron is the most interesting result to me because the speed/VRAM tradeoff looks very strong, especially for local ASR service usage.
ASR models (No Quant):
Model
Mode
Dur.
TTFT
Wall
RTF
WER
VRAM
Nemotron
Offline
327.6s
N/A
2.17s
0.0066
3.18%
8294M
Nemotron
SSE
327.6s
308ms
11.62s
N/A
3.18%
4382M
Nemotron
SSE 1-shot
1800s
N/A
53.66s
0.0298
3.45%
4167M
Higgs STT
Offline
327.6s
N/A
11.17s
0.0341
3.95%
12519M
Higgs STT
SSE
327.6s
468ms
14.46s
N/A
3.95%
6945M
VibeVoice
Offline
327.6s
N/A
19.24s
0.0587
0.66%
25833M
VibeVoice
Offline
1800s
N/A
123.72s
0.0687
1.51%
31209M
Streaming TTS:
Model
Mode
Memsaver
TTFT
Wall
Audio
RTF
VRAM
VoxCPM2
SSE
On
547ms
56.65s
314.6s
N/A
7638M
VoxCPM2
SSE
Off
308ms
55.75s
314.6s
N/A
9091M
Repo: [https://github.com/0xShug0/audio.cpp](https://github.com/0xShug0/audio.cpp)
audio.cpp is still pretty new, but the goal is becoming clearer: a ggml-based local audio framework that can handle TTS, ASR, voice cloning, long-form generation, and server-like usage without every model needing its own Python environment and custom runtime.
As always, backend/OS compatibility cannot be fully tested by one setup. If you try the Windows, Linux, CUDA, Vulkan, Metal, or CPU paths and find issues, detailed reports are very welcome.
**Huge thanks to our community members for their contributions!**
---
## Comments 43

- by [unknown](#) **&#x21C5; 10**
  <br/> Other updates you may miss: Docker support, Windows prebuilts,  **Perf** **optimization**. Huge thanks to our community members for their contributions!

VibeVoice reaches 5.15x realtime, generating 93.9-minute podcast in 18.12 min! Overall, VibeVoice inference time for short requests was reduced by 73.17%, PocketTTS by 35.32%, Chatterbox by 33.56%, Qwen3-TTS by 30.60%, HeartMuLa by 17.03%, and VoxCPM2 by 14.7% compared with the previous release.

- by [unknown](#) **&#x21C5; 2**
  <br/> will try the docker, thanks!

- by [unknown](#) **&#x21C5; 1**
  <br/> Thanks! Let me know if you run into any issues.

- by [brahh85](https://www.reddit.com/user/brahh85/) **&#x21C5; 8**
  <br/> awesome project , we hoped for this for the last 2 years, because python needs a petabyte of dependencies

can you add an option to generate subtitles?  so i can stop using whisperscpp

- by [brahh85](https://www.reddit.com/user/brahh85/) **&#x21C5; 5**
  <br/> [u/brahh85](/user/brahh85/) Audio.cpp has a pipeline feature, and there is an example subtitle pipeline you can try. Let me know if you run into any issues!

Example usage for generating subtitles with Qwen3-ASR + Qwen3-ForcedAligner:

build/bin/audiocpp_cli \
  --pipeline assets/pipeline/qwen3_asr_subtitles.json \
  --backend cuda \
  --workflow-input source_audio=/absolute/path/to/audio.wav \
  --workflow-input language=en \
  --workflow-input qwen3_asr_model=/absolute/path/to/models/Qwen3-ASR-0.6B \
  --workflow-input qwen3_forced_aligner_model=/absolute/path/to/models/Qwen3-ForcedAligner-0.6B \
  --out-dir build/out/qwen3_asr_subtitles

Or process all audio files from a directory:
build/bin/audiocpp_cli \
  --pipeline assets/pipeline/qwen3_asr_subtitles_batch.json \
  --backend cuda \
  --workflow-input source_audio_dir=/absolute/path/to/wav_dir \
  --workflow-input language=en \
  --workflow-input qwen3_asr_model=/absolute/path/to/models/Qwen3-ASR-0.6B \
  --workflow-input qwen3_forced_aligner_model=/absolute/path/to/models/Qwen3-ForcedAligner-0.6B \
  --out-dir build/out/qwen3_asr_subtitles_batch

- by [unknown](#) **&#x21C5; 7**
  <br/> The next DLC is going back to TTS models: Higgs TTS, IndexTTS2, Irodori TTS,  Kokoro (maybe), MOSS-TTS, and Supertonic.

- by [unknown](#) **&#x21C5; 5**
  <br/> Also if you want to request a new feature or submit PRs for new models, please check [https://github.com/0xShug0/audio.cpp/issues/34](https://github.com/0xShug0/audio.cpp/issues/34) and [https://github.com/0xShug0/audio.cpp/pull/19](https://github.com/0xShug0/audio.cpp/pull/19)

Model releases may be a bit slower because I want to test as much as I can instead of blindly trusting AI-generated code. Most of my time is spent on measurement, validation, and making the AI explain any code changes that look suspicious to me until I actually understand and trust them.

- by [unknown](#) **&#x21C5; 5**
  <br/> Also, let me know if there are any audio related models you’d like to see supported in audio.cpp.

- by [unknown](#) **&#x21C5; 4**
  <br/> For old updates and discussions you can check [https://www.reddit.com/r/LocalLLaMA/s/lTLVW0RZo9](https://www.reddit.com/r/LocalLLaMA/s/lTLVW0RZo9) ---  [https://www.reddit.com/r/LocalLLaMA/s/zo1lj9OQVH](https://www.reddit.com/r/LocalLLaMA/s/zo1lj9OQVH) ---  [https://www.reddit.com/r/LocalLLaMA/s/owmHglHjGN](https://www.reddit.com/r/LocalLLaMA/s/owmHglHjGN)

- by [unknown](#) **&#x21C5; 4**
  <br/> Thank you again. Time to update already

- by [unknown](#) **&#x21C5; 1**
  <br/> Thanks!

- by [unknown](#) **&#x21C5; 4**
  <br/> I'm still in the process of just switching over my convoluted chain of audio forks and whatnot to this and you've already got a major update. Wish I had something more concrete to offer than some praise for the project, but it really is fantastic work that's taking care of a major issue within the larger ecosystem.

- by [unknown](#) **&#x21C5; 2**
  <br/> Thanks a lot!

- by [unknown](#) **&#x21C5; 3**
  <br/> btw, just my personal use experience on 3090, 2x improvement. great product

- by [unknown](#) **&#x21C5; 3**
  <br/> Thanks😄! Really happy to hear that!

- by [unknown](#) **&#x21C5; 3**
  <br/> Hope that you will add Vulkan version in your next binary release.

- by [unknown](#) **&#x21C5; 3**
  <br/> How about quantisation? VRAM requierements seem too high here. I can run Parakeet v3 Q4 with 1,2 GB total VRAM consumption.

- by [unknown](#) **&#x21C5; 4**
  <br/> audio.cpp supports quant (down to q8) during loading. Many model sessions expose quantization through `--session-option <family>.weight_type=<mode>.` GGUF support will be added model by model. In general, audio.cpp trades memory for performance. Some models have added a memory-saver mode based on user requests, but it can be around 30% slower. The issue with Q4 quantization (even just fp16 vs bf16) is that it can cause quality drops and, in some cases, even failures such as producing NaNs. So quant really needs to be tested model by model.

- by [banafo](https://www.reddit.com/user/banafo/) **&#x21C5; 2**
  <br/> Kroko.ai guy here,is it possible to add support for zipformer2 based asr models?

- by [banafo](https://www.reddit.com/user/banafo/) **&#x21C5; 3**
  <br/> [u/banafo](/user/banafo/) Definitely. I’m trying to cover different model architectures so audio.cpp can provide more comprehensive components and reusable patterns. I’m getting a bit tired of AR-based models at the moment. Would you mind sharing the specific models you’d like to see supported or submit a Github issue?

- by [banafo](https://www.reddit.com/user/banafo/) **&#x21C5; 3**
  <br/> That would be really cool, i'm not sure its technically feasible though as the architecture is quite different.These are the repos:

[https://huggingface.co/Banafo/Kroko-ASR](https://huggingface.co/Banafo/Kroko-ASR)[https://github.com/kroko-ai/kroko-onnx](https://github.com/kroko-ai/kroko-onnx)

Slightly older direct onnx models:[https://huggingface.co/csukuangfj/sherpa-onnx-streaming-zipformer-en-kroko-2025-08-06/tree/main](https://huggingface.co/csukuangfj/sherpa-onnx-streaming-zipformer-en-kroko-2025-08-06/tree/main)

Feel free to pm me to discuss how we can help

- by [banafo](https://www.reddit.com/user/banafo/) **&#x21C5; 1**
  <br/> [u/banafo](/user/banafo/) Kroko ASR is now supported in audio.cpp!

- by [unknown](#) **&#x21C5; 1**
  <br/> Amazing! I’ll try it soon! Thank you!

- by [unknown](#) **&#x21C5; 2**
  <br/> Testing in my voice loop now. Pair of RTX 3060s, Nemotron ASR and VoxCPM2.

- by [unknown](#) **&#x21C5; 1**
  <br/> Cool! Let me know if you run into any issues.

- by [banafo](https://www.reddit.com/user/banafo/) **&#x21C5; 2**
  <br/> Great project — we maintain a self-hosted meeting transcription tool (diarization + local LLM correction, the boring enterprise parts) and audio.cpp plugged into it with literally zero code, since our remote STT client already speaks /v1/audio/transcriptions. That alone earned it a page in our docs.

We ran your ASR models through the benchmark we use for our own engines: real French business meetings, narrowband phone-bridge audio, several people talking over each other, scored against a professional human transcript. Fair warning before comparing numbers: on this corpus a good WER is forty-something percent, because the reference is an edited human transcript and the audio is what corporate life actually sounds like. Your 3.18% is clean audio; ours is the fox arguing with four other foxes on a bad phone line. Deltas matter, absolutes don't.

What we measured, same scorer and reference as our production engines:

- Qwen3-ASR 0.6B: 0.56 WER overall, 0.42 excluding one chaotic window  within ~5% relative of our production GPU engines (whisper large-v3, Voxtral 3B), at 7-10s per 5-minute window on one 3090. For a 0.6B, that's the best perf/quality trade we measured all week.

- Nemotron 3.5 ASR: genuinely strong French output, but on our build it returns empty text from the second request on a reused server session (first request is always good, restart fixes it). We're fairly confident it's runtime-side rather than model-side: the same model under parakeet.cpp  the implementation you recommended upthread  answers identical transcripts three requests in a row. Happy to open an issue with a minimal repro if useful. Smaller one: .mp3 input returns a 500 where wav is fine.

Fun coincidence seeing [u/banafo](/user/banafo/) ask about zipformer2 support here: we put his FR community model through the same corpus this week and it matched our best GPU engine on CPU only (155 MB of weights, 8 threads). We liked it enough that it shipped as a built-in backend in our product two days later. So, +1 that architecture is worth the effort.

Full write-up, including the traps we fell into (silent language drift is a fun one):[https://github.com/Martossien/transcria/blob/main/docs/STT_BENCHMARK_REAL_MEETINGS.md](https://github.com/Martossien/transcria/blob/main/docs/STT_BENCHMARK_REAL_MEETINGS.md)project: [https://github.com/Martossien/transcria](https://github.com/Martossien/transcria)

- by [Foreign-Watch-3730](https://www.reddit.com/user/Foreign-Watch-3730/) **&#x21C5; 2**
  <br/> [u/Foreign-Watch-3730](/user/Foreign-Watch-3730/) This is incredibly helpful. Thank you for such a detailed real-world test!

Please open an issue for the Nemotron reused-session bug, ideally with the minimal repro, logs, and exact command. Empty output after the first request definitely sounds like a state-reset or cache-reuse bug in audio.cpp. I did test long-lived sessions, but my test cases may not have been comprehensive enough to cover all scenarios. I’ll investigate it.

**Update**: Mp3 is format support issue. Currently audio.cpp doesn't really handle mp3 format. This is a gap. The server has received less attention than the core engine and still has a lot of room for improvement.

**Update**: I think I found the issue for empty output. Please check the latest commit on the `main` branch.

Really appreciate the write-up and all the concrete testing!

- by [Foreign-Watch-3730](https://www.reddit.com/user/Foreign-Watch-3730/) **&#x21C5; 1**
  <br/> Tested your fix confirmed on our side. Same harness, same converted model, only your runtime updated (3b4aed9 → 3982dfb): Nemotron now answers three identical back-to-back requests in a single server session (was: empty from request 2), and the one window that came back empty even with restarts now transcribes. Full corpus retest: 0.49 WER on 8/8 windows, ~2s per 5-min window, zero restarts  that matches parakeet.cpp for the same model at a quarter of the wall time. Impressive turnaround.

Bonus: we also ran the Qwen3-ASR-1.7B you added in the same commit. On our real-French-meetings corpus it lands at 0.42 WER on 8/8 that's second place across everything we've measured (production GPU engines included), and it set our best single-window score of the entire benchmark (0.19). Its only weakness is stutter-loops on one chaotic multi-speaker opening (contained: 0.88 there vs 1.55 for the 0.6B). At 4 GB of weights and ~12s per 5-min window, that's a serious local ASR option.

Since your latest commit fixes the session bug we were going to file, I'll skip that issue — happy to open one for the .mp3 → 500 gap instead if you'd like it tracked. Updated write-up (your fix is credited): [https://github.com/Martossien/transcria/blob/main/docs/STT_BENCHMARK_REAL_MEETINGS.md](https://github.com/Martossien/transcria/blob/main/docs/STT_BENCHMARK_REAL_MEETINGS.md)

- by [Foreign-Watch-3730](https://www.reddit.com/user/Foreign-Watch-3730/) **&#x21C5; 2**
  <br/> [u/Foreign-Watch-3730](/user/Foreign-Watch-3730/) Thanks for retesting and sharing the updated numbers! Great to hear the session fix is working. Please open an issue for the mp3 500 error so I can track and fix it properly. If you don’t mind, I’d like to feature your project and these benchmark results in the README for the next release.

- by [unknown](#) **&#x21C5; 2**
  <br/> Issue opened: [https://github.com/0xShug0/audio.cpp/issues/44](https://github.com/0xShug0/audio.cpp/issues/44) — with a two-curl repro against your latest commit. Short version: same 20-second clip, wav gets a clean transcript, mp3 gets a 500 "invalid WAV RIFF header". No impact on us in practice (we always send 16 kHz mono wav), but the OpenAI-compatible endpoint shape invites mp3s, so a clean 4xx would spare the next person the confusion.

And feature away — we'd be honored. Fair warning: it goes both ways. We just shipped TranscrIA 0.3.6, where audio.cpp is a first-class engine of the product: our installer builds it from a pinned commit (yours with the session fix), our scheduler starts and stops the server around jobs, health-checks it, budgets its VRAM, and our GPU Docker images bake the binary. Basically we treat your runtime the way we treat llama-server, which is the highest compliment our codebase knows how to give. Release notes: [https://github.com/Martossien/transcria/releases/tag/v0.3.6](https://github.com/Martossien/transcria/releases/tag/v0.3.6)

- by [Foreign-Watch-3730](https://www.reddit.com/user/Foreign-Watch-3730/) **&#x21C5; 1**
  <br/> [u/Foreign-Watch-3730](/user/Foreign-Watch-3730/)  In case you’re interested, Voxtral Mini 4B Realtime is now available in audio.cpp. 16.39x (0.0610 RTF) realtime offline, 170ms TTFT streaming on RTX 5090.

- by [unknown](#) **&#x21C5; 2**
  <br/> I test it quickly !

- by [unknown](#) **&#x21C5; 1**
  <br/> Tested it properly — offline whole-file, our per-chunk pipeline path, and your streaming SSE endpoint — on real French business meetings (17/46/62 min, narrowband phone-bridge, the usual fox-fight). Short version: **the model's fine; we found one specific edge worth a fix.**

Integration was the usual zero-code drop-in: bumped our pinned audio.cpp `3982dfb → edbdf58`, pulled the Q8_0 GGUF via model_manager, pointed our OpenAI-compatible client at it. Qwen3 and Nemotron re-qualified clean on the new commit. One build note: the server now resolves a per-family model spec, and since we copy `audiocpp_server` out of the source tree we had to build with `-DAUDIOCPP_DEPLOYMENT_BUILD=ON` to embed the specs — otherwise it fails at load with `model package spec not found`. Maybe a README line.

It took three serving modes to pin the finding down honestly:

- **Whole-file offline** (one request per 5-min window, the way you benchmark): full coverage, clean transcript, ~0.15 RTF on our real audio.

- **Streaming** (`mode: streaming`, `stream=true` SSE): also full coverage, TTFT ~0.6s (includes uploading a 5-min file, so not comparable to your 170ms short-clip figure), ~0.25 RTF, clean delta stream. Works.

- **Per-chunk offline** (our pipeline sends one VAD speech-segment per request): **this is where it breaks** — a ~25s chunk comes back HTTP 200 with *empty text*, no error, on a big fraction of segments. On the 46-min meeting that silently swallowed ~21 of 46 minutes in contiguous holes.

The important part: **it's not the model, it's short single-clip requests.** Minimal repro, same audio two ways — a 25s wav from a swallowed region → empty; the exact same span sent as a 150s clip → 2018 chars, transcribed. Reproduced on 4 of 5 short clips I pulled from dropped regions. So any pipeline doing VAD/turn chunking with per-segment requests (a very common shape) silently loses content, while your whole-file and streaming paths are solid. Smells like a min-context/short-window edge in the offline handling. Happy to open an issue with the two-curl repro — same as the Nemotron one you turned around in hours.

One more, filed under "read the transcript, don't trust your own metrics": on the ugliest window it spliced a couple of **Russian** phrases into otherwise-French turns — and our automated non-Latin-drift counter scored it 0 there, only eyeballing caught it. Qwen3 drifts on the same window into a different script, so it's a hard-narrowband property, not a Voxtral knock.

No WER row yet — now that I know whole-file is the clean path, I want to score it there against our human reference before I put a number on it. Write-up will carry all of the above: [https://github.com/Martossien/transcria/blob/main/docs/STT_BENCHMARK_REAL_MEETINGS.md](https://github.com/Martossien/transcria/blob/main/docs/STT_BENCHMARK_REAL_MEETINGS.md)

Net: for offline whole-file or streaming, this is a legit local ASR option on hard real audio. The per-short-chunk empty is the one thing between it and a drop-in for chunked pipelines.

- by [unknown](#) **&#x21C5; 1**
  <br/> How does speed compare to like running with vllm? Thank you

- by [unknown](#) **&#x21C5; 2**
  <br/> I haven’t tested it yet. Many models in audio.cpp are not AR-based, which makes integration with llama.cpp or vLLM less straightforward. I’d be happy to see performance numbers if anyone is interested in testing it.

- by [unknown](#) **&#x21C5; 3**
  <br/> Also, I want to repalce the current AR impl with llama.cpp in the future. This has been in my mind for a well and the current release-0.2 has done some as preimlarty step.

- by [Languages_Learner](https://www.reddit.com/user/Languages_Learner/) **&#x21C5; 1**
  <br/> Maybe it will be useful for you: stable audio 3 inference in pure c++ - [betweentwomidnights/sa3.cpp: sa3 implemented in ggml for cross-platform and embedded applications](https://github.com/betweentwomidnights/sa3.cpp), gguf for it - [thepatch/stable-audio-3-small-music-GGUF · Hugging Face](https://huggingface.co/thepatch/stable-audio-3-small-music-GGUF)

- by [Languages_Learner](https://www.reddit.com/user/Languages_Learner/) **&#x21C5; 3**
  <br/> [u/Languages_Learner](/user/Languages_Learner/) Cool. audio.cpp also has stable audio 3 small/sfx/medium. Happy to check the CPU path as currently audio.cpp only foucs on cuda perf optimization.

- by [unknown](#) **&#x21C5; 1**
  <br/> What in your expert opinion is the best Parakeet implementation?

- by [unknown](#) **&#x21C5; 3**
  <br/> I think this one looks good [https://github.com/mudler/parakeet.cpp](https://github.com/mudler/parakeet.cpp)

- by [dont--panic](https://www.reddit.com/user/dont--panic/) **&#x21C5; 1**
  <br/> Do you support the llama.cpp RPC server protocol? It would be convenient if I could run a single RPC server backend that can be used by llama.cpp, stable-diffusion.cpp, and audio.cpp.

- by [dont--panic](https://www.reddit.com/user/dont--panic/) **&#x21C5; 1**
  <br/> [u/dont--panic](/user/dont--panic/) Not yet. It currently only has an OpenAI server.

- by [unknown](#) **&#x21C5; 1**
  <br/> Any support for: [https://huggingface.co/OpenMOSS-Team/MOSS-Transcribe-Diarize](https://huggingface.co/OpenMOSS-Team/MOSS-Transcribe-Diarize) ?
