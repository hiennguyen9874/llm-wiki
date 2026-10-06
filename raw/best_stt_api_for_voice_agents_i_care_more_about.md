# Best STT API for voice agents? I care more about useable text than accuracy screenshots [Visit](https://www.reddit.com/r/AI_Agents/comments/1vx1afu/best_stt_api_for_voice_agents_i_care_more_about/)
### **Subreddit:** [r/AI_Agents](https://www.reddit.com/r/AI_Agents)
### **Author:** [u/-HEPHAESTUSquest-](https://www.reddit.com/user/u/-HEPHAESTUSquest-/)
### **Vote:** 24
---
I’m testing Smallest AI Pulse for a voice-agent STT setup, and I’m realizing “accuracy” is not the only thing I should care about.
Most STT comparisons show clean transcript accuracy.
That’s not enough for voice agents.
For live agents, I care about:
first usable text not just first text endpointing barge-in partials changing too much final transcript delay phone audio numbers / dates / names caller corrections logs that tell me what broke
A transcript can be accurate 2 seconds later and still make the agent feel dead.
A partial can be fast and still dangerous if it keeps rewriting the important part.
The thing I want to test with Pulse is simple:
can realtime speech become safe agent input while the user is still talking?
I want the agent to catch “don’t cancel,” hear the correct phone number, stop talking when interrupted, and not make the user wait awkwardly after every sentence.
What are people actually measuring in production voice agents?
And what broke first?
---
## Comments 23

- by [unknown](#) **&#x21C5; 2**
  <br/> I’d add action safe transcription as a separate metric. Fast partials are useful for turn taking, but they shouldn’t trigger irreversible tool calls.

For dates, phone numbers, amounts, or phrases like “don’t cancel,” I’d wait for a stable final or explicit read back. I’d also test whether a caller correction replaces the old value in every pending tool call, CRM field, summary, and handoff.

A transcript can look accurate while the workflow still acts on stale information.

- by [unknown](#) **&#x21C5; 1**
  <br/> Thank you for your submission, for any questions regarding AI, please check out our wiki at [https://www.reddit.com/r/ai_agents/wiki](https://www.reddit.com/r/ai_agents/wiki) (this is currently in test and we are actively adding to the wiki)

*I am a bot, and this action was performed automatically. Please *[*contact the moderators of this subreddit*](/message/compose/?to=/r/AI_Agents)* if you have any questions or concerns.*

- by [unknown](#) **&#x21C5; 1**
  <br/> “accurate after the moment is gone” is useless for voice agents.

- by [unknown](#) **&#x21C5; 1**
  <br/> Everyone optimizes the LLM first because it is the sexy part.

Then you check logs and the slow bit is:

caller stops talking

STT waits too long

final transcript comes late

LLM replies fast

TTS starts fast

call still feels awkward

Voice agents are death by small delays.

- by [unknown](#) **&#x21C5; 1**
  <br/> I’m Building real-time interpretation (OmniLink), so I live in this exact gap. Two things reframed it for us:

**Stop measuring time-to-first-token. Measure time-to-first-*****stable*** **token.** Track how often the last N tokens of a partial get rewritten, and how long a span survives before the model changes its mind. That volatility number predicted “does this feel alive” better than WER ever did. We hold commits until a span is stable for a threshold, but start prefetching downstream on the unstable version — you eat the latency once instead of every turn.

**WER is the wrong denominator.** “Don’t cancel” → “do cancel” is one word error and a total failure. Score the action-bearing span separately: negations, digits, names, dates. Our entity-level accuracy was ~15 points below our transcript accuracy and nobody would have caught it from a WER table.

What broke first, roughly in order:

**•	Barge-in on speakerphone.** VAD kept firing on our own TTS bleeding back through the mic. Agent stopped mid-sentence constantly. Also: barge-in latency isn’t VAD detection time, it’s detection *plus flushing the playback buffer* — measure the acoustic stop, not the event.  
**•	Short low-energy words getting eaten by endpointing.** “No.” “Don’t.” The exact words that matter most are the ones aggressive endpointing swallows.  
**•	Corrections landing after commit.** “No, 4 not 5” — STT got it right, our state machine had already moved on. That’s an architecture problem masquerading as an STT problem.  
**•	Language degradation with high confidence.** Tested Haitian Creole. Accuracy fell off a cliff and confidence scores didn’t move at all. If you’re doing anything outside the top tier of languages, confidence is not a usable signal.On logs: single timeline, aligned timestamps for audio-in → partial → final → LLM first token → TTS first byte. Without that you can’t tell whether “the agent felt dead” was STT, the model, or playback. We wasted about a month tuning the wrong stage.

- by [unknown](#) **&#x21C5; 1**
  <br/> Smallest AI Pulse is the kind of STT I'd evaluate as part of the agent UX, not backend plumbing. If the live text arrives later or unstable, the whole agent feels broken

- by [unknown](#) **&#x21C5; 1**
  <br/> For best STT API for voice agents, the checklist should be:

first usable textpartial stabilityfinal delayendpointingbarge-in timingfield accuracyphone audioreconnect behaviorlogs per turncost per successful call

Smallest AI Pulse belongs in the test when the agent needs realtime speech events, not just a transcript after the call.

- by [unknown](#) **&#x21C5; 1**
  <br/> Exactly. WER screenshots are becoming a pretty useless way to judge STT for an actual voice agent. A transcript can eventually be perfect while the agent has already acted on a bad partial 800ms earlier 😅

I'd be measuring stability of important entities too: numbers, names, dates, negations like "don't", and corrections. We've been using TestMu-style end-to-end testing for this kind of thing because the real question isn't just whether STT got the transcript right, it's whether the whole agent behaved correctly based on what it heard.

- by [unknown](#) **&#x21C5; 1**
  <br/> For me the first thing that usually breaks is not raw transcription, it's the handoff between STT and agent logic.

The STT might eventually understand the correction perfectly, but did the agent already call a tool? Did endpointing fire too early? Did it stop TTS quickly enough when the caller interrupted?

That's why I'd test Pulse or any STT provider with full scenarios in TestMu rather than picking based purely on accuracy numbers. "Usable text" is really text that the agent can safely act on.

- by [unknown](#) **&#x21C5; 1**
  <br/> Any updates?
