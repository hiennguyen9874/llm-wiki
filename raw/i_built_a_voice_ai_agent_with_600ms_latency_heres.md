# I built a voice AI agent with ~600ms latency. Here’s what I learned. [Visit](https://www.reddit.com/r/VoiceAutomationAI/comments/1wgp1im/i_built_a_voice_ai_agent_with_600ms_latency_heres/)
### **Subreddit:** [r/VoiceAutomationAI](https://www.reddit.com/r/VoiceAutomationAI)
### **Author:** [u/yoursandeshshrestha](https://www.reddit.com/user/u/yoursandeshshrestha/)
### **Vote:** 24
---
I started learning to code in my 1st year of college.At the same time, I started working my first job.
I didn’t really have some grand plan to build a company. I was just obsessed with building things and figuring out how software actually worked.
Recently, I started building voice AI agents.I ended up going pretty deep into the latency problem.
My goal was simple:**Make the agent feel like you’re talking to a real person, not waiting for a computer to think.**
After a lot of experimenting with the pipeline, streaming, model selection, audio processing, and infrastructure, I managed to get the end-to-end latency down to around **600ms**.And that changed things.
I’m currently using **Pipecat** for the voice pipeline, and I’ve been experimenting with different providers and infrastructure to squeeze out as much latency as possible.
The other thing I didn’t expect:I actually started getting clients.
Right now, I’m managing voice AI agents for around **8 clients**.
I’m also getting subsidies/credits from companies like **Alda and other platforms**, which has made the economics pretty crazy at the moment.
My current margins are basically **close to 100%** because of those credits/subsidies.
Obviously, I don’t expect that to last forever.
But it’s been an insane learning experience.
A few things I’ve learned so far:Voice AI is **way more than just connecting an LLM to a microphone**
Latency matters *a lot* more than I initially thoughtStreaming everything makes a huge differenceThe voice model, LLM, TTS, STT and networking all contribute to the final experience
A technically impressive demo is useless if the agent doesn’t actually solve a business problemGetting the first few paying clients is a completely different challenge from getting the technology working
The economics of voice AI are really interesting right now
I’m still very early in this.But going from **learning to code in college → building voice agents → getting them into production for ~8 clients** has been pretty surreal.I’m curious what other people building voice AI are seeing.
**What’s the lowest real-world latency you’ve managed to achieve, and what stack are you using?**
If there’s interest, I can also break down exactly how I’m getting the ~600ms latency and what my architecture looks like
---
## Comments 55

- by [unknown](#) **&#x21C5; 1**
  <br/> **Welcome to **[r/VoiceAutomationAI](/r/VoiceAutomationAI/)** – UNIO, the Voice AI Community (powered by SLNG AI)**

If you are a **founder, senior engineer, product, growth, or enterprise operator** actively working on **Voice AI / AI agents**, we are running an **invite-only UNIO Voice AI WhatsApp community US only**.

Apply here: [https://chat.whatsapp.com/F5aG3ncrO70ITfbe3pYbOz](https://chat.whatsapp.com/F5aG3ncrO70ITfbe3pYbOz)

*I am a bot, and this action was performed automatically. Please *[*contact the moderators of this subreddit*](/message/compose/?to=/r/VoiceAutomationAI)* if you have any questions or concerns.*

- by [unknown](#) **&#x21C5; 2**
  <br/> Really interesting numbers.I’m working on a similar problem, although I’ve gone a bit lower-level with the stack — FreeSWITCH + audio streaming + custom VAD/barge-in + separate STT/LLM/TTS providers rather than Pipecat.One thing I’d be really interested in: when you say ~600ms end-to-end, where exactly are you starting the timer?Caller speech end → first audible TTS frame?I’ve found that latency numbers in voice AI can look completely different depending on whether they’re measured from final STT, VAD speech-end, LLM TTFT, or actual first audio playback.I’ve managed to get some very aggressive speech-end-to-first-play numbers in testing, but telephony conditions, noise, endpointing and interruptions are where it gets much more interesting.Also agree completely that the technical demo is only half the problem. Getting real businesses to actually depend on the agent is a different challenge entirely.Would be interested to see your Pipecat architecture if you publish the breakdown.

- by [unknown](#) **&#x21C5; 1**
  <br/> The end to end latency is 600ms without using knowledge base, if we use knowledge base it get around 800

- by [unknown](#) **&#x21C5; 1**
  <br/> The noise part caught us out more than the endpointing did. On a mobile caller standing somewhere loud, the STT closes the turn early, the agent starts talking while the caller is still mid sentence, and it goes into the tracker as a barge-in bug when really the turn detection fired on half a sentence. Doing the interrupt at the media server the way you can with FreeSWITCH helps a lot there, since you drop the queued audio at the edge instead of waiting for the pipeline to unwind. Are you running your own endpointing on top of the VAD, or leaving the turn close to the STT?

- by [unknown](#) **&#x21C5; 1**
  <br/> How have you done that.. I can't get past the llm latency. Im not using pipecat but. The breakup would really help.

- by [unknown](#) **&#x21C5; 1**
  <br/> Which modal are you using for llm?

- by [unknown](#) **&#x21C5; 1**
  <br/> Open ai 4o mini.  I've put in a request for groq, hoping in use the newly introduced qwen in their offerings.

- by [unknown](#) **&#x21C5; 2**
  <br/> openai 4o mini have latency around 800, try using gemini 3.1 flash lite

- by [unknown](#) **&#x21C5; 1**
  <br/> Okay thanks,  are you using qdrant for your kb?

- by [unknown](#) **&#x21C5; 2**
  <br/> No, we’re not on Qdrant.

KB lives in Postgres. Chunks + embeddings go in `pgvector` (1024-dim, HNSW), embeddings from Bedrock Titan v2. Search is hybrid: vector + Postgres full-text, then merged with RRF.

- by [unknown](#) **&#x21C5; 1**
  <br/> how did you found those clients?

- by [unknown](#) **&#x21C5; 1**
  <br/> Thanks for sharing, and congrats on having 8 clients in production. Your timing is great, because we're right in the middle of this.

Where we are: we're building our first voice agent, for our first client. Nothing is in production yet, so we don't have end-to-end latency numbers from real calls. So far we've mostly been laying the foundations.

The stack:

- Telephony: Twilio, with audio streamed over WebSocket

- Orchestration: Dograh (built on Pipecat), hosted on Railway

- Speech-to-text: Deepgram, on its EU endpoint

- LLM: Mistral

- Text-to-speech: Voxtral (Mistral)

- Actions and automations: n8n

- Data: PostgreSQL

Why these choices: we work with French SMBs, so GDPR puts real constraints on us. That's why we went with Mistral and Deepgram in the EU instead of the usual providers. It rules out some options that are probably faster.

Dograh, in case you haven't come across it: it's an open source layer on top of Pipecat. It adds what Pipecat doesn't give you on its own: a web interface, a visual editor for building conversation flows, telephony already wired in, and account management. You keep the Pipecat engine and can still drop down into the code, but you no longer hand-write the pipeline for every agent. Since you're running agents for several clients, it's worth a look.

What we've built:

- An architecture designed to replicate fast: a new client is one more configuration, not a new deployment.

- BYOK: each client opens their own provider accounts and we plug them in. They keep control of their keys and their costs.

- A fork of Dograh: we modified it to handle multiple clients on a single deployment, and to show every provider setting in the UI. Most of those settings were hardcoded, and now we can tune everything without touching the code.

Our first lesson: every model needs tmodel and the way you write its prompts go together. A prompt that works well on one LLM doesn't carry over as-is to another, so each LLM needs its own approach. Switching models meo.

What we'd really love to know is your

  1. VAD: what values do you use for confidence, start_secs, stop_secs and min_volume?
  2. End of turn: do you rely on VAD alor your STT provider's endpointing?With what thresholds?
  3. Interruptions: is allow_interruptions on? Do you require a minimum number of words before the agent gets cut off?
  4. TTS: do you send text to the TTS sentence by sentence, or in smaller chunks?
  5. LLM: what temperature, what max tostem prompt? And did you adapt the wayyou write prompts to your model?

It would also help if you could tell us where you start the clock for your 600 ms, so we're comparing like with like.

On our side, we're happy to share everything we learn: what works, what cost us time, and our numbers once we have them. Just let us know if you're interested.

Thanks in advance!

- by [unknown](#) **&#x21C5; 1**
  <br/> Happy to share. Dograh looks useful, we run Pipecat directly with one multi-tenant pipeline.

VAD (Silero on the phone transport). We don’t set `confidence`, so it stays at Pipecat’s default 0.7.

  - Deepgram: `start_secs=0.2`, `stop_secs=0.2`, `min_volume=0.5`
  - Cartesia: `start_secs=0.25`, `stop_secs=0.2`, `min_volume=0.6`

For Deepgram Flux and Cartesia Ink-2, VAD is not what closes the turn. That’s on the STT provider.

End of turn

STT endpointing, not VAD. On Twilio + Deepgram Flux:

  - `eot_threshold=0.5`
  - `eot_timeout_ms=700`
  - `eager_eot_threshold=0.4`
  - We commit the turn on eager EOT so the LLM can start immediately. If the caller keeps talking, we cancel it.

Interruptions

`allow_interruptions` is on by default. No minimum word count.

TTS

Sentences on phone. Tokens on web (for the live transcript). Sentence-level on the phone path avoided crackle from fragments like `"I'"`.

LLM

Temperature 0.7, max 1024 tokens (Gemini uncapped; we keep it short in the prompt). Default is Gemini 3.1 Flash Lite.

Yes, we adapted the prompts: write for the ear, one or two sentences, one question at a time, no markdown. Tool filler is spoken by the server, not the model. A Gemini prompt does not carry over as-is.

600 ms clock

User turn committed → first bot audio. That does not include the Flux/VAD silence that decides the caller is done. If your number includes endpointing wait, we are not measuring the same thing.

- by [unknown](#) **&#x21C5; 1**
  <br/> Huge thanks for this, and for the speed, that's way more detail than I expected. The distinction between VAD and STT endpointing on the turn close is especially useful. I'll run my tests with your settings and come back to you with results.

- by [unknown](#) **&#x21C5; 1**
  <br/> how were the results comparing AssemblyAI? PS: Developer Relations from AssemblyAI here, happy to help, we power Granola for TTS using our Realtime API

- by [unknown](#) **&#x21C5; 1**
  <br/> We can try, do you guys have startup program?

- by [unknown](#) **&#x21C5; 1**
  <br/> Hey what challenges you have faced with dograh?

- by [unknown](#) **&#x21C5; 1**
  <br/> Hey! Honestly, we haven't run into many issues with Dograh so far. We've applied quite a few patches to our fork to adapt the interface to our needs and make every AI agent parameter configurable straight from the UI, so we have full control over the setup. We're currently running our first tests with the built-in call simulator, and so far the issues we've found on the parameters we're evaluating are ones we can fix on our end right away.

- by [unknown](#) **&#x21C5; 1**
  <br/> Would love to see the break down of how uou got to ~600ms latency

- by [unknown](#) **&#x21C5; 1**
  <br/> try thrumble dot ai

- by [unknown](#) **&#x21C5; 1**
  <br/> Around the 500–700ms mark it starts feeling like you're optimizing a bunch of small things instead of one big bottleneck. Curious what gave you the biggest improvement. Streaming, model choice, TTS or something else?

- by [unknown](#) **&#x21C5; 1**
  <br/> 600ms?!  Impressive. I couldn’t crack 900 without using openAI realtime. Tried a version where I implemented one with Kokoro and claude  . Used Silencio as VAD. Latency was rough.

Please break down for me. Would love to learn

- by [unknown](#) **&#x21C5; 1**
  <br/> congrats on the speed!

is the latency P50, P99?

cuz our Realtime P50 is 300ms for our Realtime API

PS: Developer Relations from AssemblyAI here, happy to help, we power Granola

- by [unknown](#) **&#x21C5; 1**
  <br/> P99, our realtime is less then 200

- by [unknown](#) **&#x21C5; 1**
  <br/> Amazing work! Is this perceived latency?

- by [unknown](#) **&#x21C5; 1**
  <br/> P90

- by [unknown](#) **&#x21C5; 1**
  <br/> 600ms is poor performance you need under 400 for anything acceptable

- by [unknown](#) **&#x21C5; 2**
  <br/> We are improving each day, I m sure we I’ll get there soon

- by [unknown](#) **&#x21C5; 1**
  <br/> What LLM model, STT, TTS & voice combo would you use to achieve <400?

- by [unknown](#) **&#x21C5; 1**
  <br/> I feel that sharing just a single number is not particularly helpful. It's easy to over-optimise latency by switching to a smaller ASR, LLM and TTS. You end up with a a voicebot that replies really fast, but the responses are inaccurate and the transcript breaks under any non-ideal recording conditions.

As always there is a trade-off between cost, latency and performance. And your target depends on the precise use-case which you want to address.

- by [unknown](#) **&#x21C5; 1**
  <br/> I’d be interested to see the Pipecat models you use.

coming from AssemblyAI and also use Pipecat, working hard to achieve the highest accuracy and lowest latency combination.

- by [unknown](#) **&#x21C5; 1**
  <br/> Pipecat is the pipeline, not the model.

My default stack are

  - STT: Cartesia Ink-2 (streaming, with Cartesia’s turn API)
  - LLM: Gemini 3.1 Flash Lite
  - TTS: Cartesia Sonic 3.5
  - VAD: Silero (still in the pipeline, but not the turn-end source)

- by [unknown](#) **&#x21C5; 1**
  <br/> 600 ms is already a really useful real-world number, especially if you’re measuring the whole path rather than model inference in isolation.

The next thing I’d want to see if I was the customer is the tail, P95/P99 on an actual phone call, plus how latency changes when tools, retrieval, or handoff enter the loop. I work on Rasen AI, and we look at production calls as evaluations for latency, grounding, interruptions, and task success. The goal is to turn regressions into versioned fixes rather than chase one good demo number. The lowest we clocked is around 100ms

Also, your 600 ms is mic-to-first-audio or full-turn latency?

- by [unknown](#) **&#x21C5; 1**
  <br/> Full turn latency is 600ms goes to 700-800 ms when knowledge base, tool call and stuff come into pipeline. Pretty happy with the latency for now, aiming to get 500ms p90 before the end of the year

- by [unknown](#) **&#x21C5; 1**
  <br/> 600ms measured where? If that's the round trip at your websocket then the caller on a regular phone is hearing more than that, since the carrier leg and the 8k transcode add time you never see from inside Pipecat. Full disclosure, I work on FreJun Teler, we're the phone layer under agents like this, so my numbers aren't apples to apples with yours, but the way we check is to stream a pre-recorded WAV into a live call and listen back to the recording instead of trusting the pipeline logs. The thing that hit us harder than raw latency was barge-in, if the queued audio doesn't get dropped fast when the caller talks over the agent it still feels slow at 600ms.

- by [unknown](#) **&#x21C5; 1**
  <br/> Congrats on the clients. Two things from building in this space:

Wrap the model in a deterministic FSM. Code owns state, routing, transfers and business rules. Each turn, the model only gets the instructions and tools for the current state and makes a narrow decision. It's far more predictable and debuggable than one giant prompt, and a smaller per-turn context also helps latency.

If you're on ASR → LLM → TTS, expose it behind an OpenAI-Realtime-compatible interface. Your app then talks to one protocol, and cascade vs. end-to-end model (OpenAI Realtime, Gemini Live) becomes a config choice, not a rewrite.

Curious how you measure the 600ms. End of user speech to first agent audio? Does it include the VAD silence window? SIP or WebRTC? A per-stage breakdown (endpointing / STT / LLM TTFT / TTS first chunk / network) would be great to see.

- by [unknown](#) **&#x21C5; 1**
  <br/> Hey I built a voice ai agent recently, more towards regional languages like Hindi and bhojpuri in addition to english.... For english I found lots of things available to me, open source models across stt, LLM through vllms, TTS using kokoro, but when it came to the regional languages I had very small options and for one of these there were no options even through paid tiers....

That out me from configuring the whole pipeline to fine tuning + post training models for that language by getting the cloud GPUs through runpod and AWS...

This could very well turn into a rant but I just feel that I get lost when I turn towards the latencies. The english one with the AWS credits and startup program thing I got bought me down in the 600-800ms range tested across multiple clients, but when it comes to regional languages even hindi which has a lot more work and data than something like bhojpuri, it almost doubles or triples on the latency or mishears stuff....

Mishearing thing put me off into another subspace where pronunciation, OOV(out-of-vocabulary) words, stt models having bottlenecks and different performances for different languages, the WER increasing in multiples as I go into regional languages stuff and even reaches 40% + for some......

That's where I am right now, another biggest issue I had to go through is scaling I have AWS credits, I have enough account level permissions but the GPUs and cloud capacity isn't available in my region and I am required to get the capacity from across the globe which again hits on the latency.

Again, I apologise if this rant wasted time but I am looking for a solution regarding this.... If anyone can help or enlighten me, I am a fresher, I have worked freelance and in a startup, created agents that can carry conversations end to end even book site visits(real-estate client) and hospital/clinical appointments (with proper cms integration) but when moving into voice specially in the regional languages space I feel lost.....

- by [unknown](#) **&#x21C5; 1**
  <br/> 600ms end-to-end is pretty impressive, especially once you include STT, LLM processing, TTS, and network overhead.

One thing I’ve noticed with voice agents is that perceived latency can matter just as much as the actual number. Streaming the response early and handling interruptions naturally can make a system feel much faster.

I’d be interested in how you’re measuring the ~600ms — from the user finishing speaking to the first audio byte, or to the full response? That distinction seems important when comparing different stacks.

- by [unknown](#) **&#x21C5; 1**
  <br/> Nice work, and congrats on getting 8 paying clients. That's the harder part.

Quick question on the 600ms, because I see people measure this very differently: is that from the end of the caller's speech to the first audio, or from when the turn is committed? And is it a median or a p90?

We run a Dutch phone receptionist for small businesses (bookings for restaurants and salons) on LiveKit + Deepgram + ElevenLabs over SIP. Some things we learned from measuring real calls:

- Turn detection was our biggest delay, not the LLM. After short answers like "yes" or "four people" the end-of-turn wait was ~1.8s, more than the gap between the models we tested. Next we're shortening that wait after a closed question.

- Measured from the end of speech, our median is around 1.1s with the fastest model. Measured from the committed turn it would look much better, which is why I'm asking how you measure.

- The median hides the problem. We look at p90 and actually listen to the recordings, because pauses during tool calls (checking availability, making the booking) don't show up in the averages.

- Tool latency matters as much as model latency. We cut our booking backend from 4–6 database round trips to 2 (1.1–2.3s down to ~0.3s).

- Fast isn't enough if the agent says "your table is booked" when nothing was actually booked. We added a code-level check that blocks those claims unless the booking really happened. The faster models were not always the most reliable here.

Would be very interested in the architecture breakdown, especially how you handle interruptions (barge-in) and what you do with noisy mobile callers.

- by [unknown](#) **&#x21C5; 1**
  <br/> yeah one thing i’d add is that endpointing can easily get hidden inside the latency number.

we’ve run into this with pulsy ai too. we’re building the platform mainly for white-label agencies, resellers, MSPs and voip providers, so once you have multiple clients running agents, those little latency differences become pretty noticeable.

if you measure from “turn committed” to first audio, you can get a really nice number, but the caller still experiences the endpointing delay before the turn is actually committed.

i’d break it down into speech end → turn detection → llm first token → tts first audio → actual playback. otherwise you can optimize the llm by 200ms and barely notice a difference because the endpointing is still adding another 700-1000ms.

also agree with the p90 point. a 600ms median sounds great, but the ugly calls with tools, interruptions, noisy audio, etc are usually what you actually hear in production.

- by [unknown](#) **&#x21C5; 1**
  <br/> Nice result. One thing we've learned the hard way is that voice-agent latency numbers become difficult to compare unless everyone defines the start and stop boundaries.

I'd instrument at least:

speech end/VAD stop → STT final → LLM request → first useful model output → TTS request → first audio → actual caller output.

In one of our earlier real-telephony cascade hardening passes, median stages were roughly 280ms to STT final, ~537ms LLM request to first output, and ~82ms TTS request to first audio — but complete normal turns were still around 1.45–1.95s.

The other important thing is separating ordinary conversational turns from tool/graph-transition turns. They are not the same latency problem.

We also caught warm LLM requests suddenly taking ~8–10s after several earlier requests on the same service were fast, which is why I wouldn't assume prewarming fixes every long-tail case.

Would be interested to know whether your ~600ms is caller-speech-end → first audible phone audio, and whether that's median or p90/p95.

- by [unknown](#) **&#x21C5; 1**
  <br/> Moss has under 10ms retrieval and pipecat integration. Tried them?

- by [unknown](#) **&#x21C5; 0**
  <br/> once latency is good enough, continuity becomes a different problem we use Hindsight so the voice agent can remember previous conversations and decisions without stuffing old transcripts into every call.

- by [unknown](#) **&#x21C5; 1**
  <br/> Make a a lot of sense

- by [unknown](#) **&#x21C5; 1**
  <br/> Same here. The gaps that actually annoy people are the short stalls mid turn while a tool call goes out, and an average will never show you those because each one is only a couple of hundred ms. You only catch them sitting through the recording
