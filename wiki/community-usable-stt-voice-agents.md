---
type: Concept
title: Community-Reported Usable STT for Voice Agents
description: Community-reported voice-agent STT evaluation checklist emphasizing first stable text, partial stability, endpointing, barge-in, entity accuracy, corrections, and per-turn logs over WER.
tags: [stt, vad, streaming]
status: draft
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T12:00:00Z }
stale_after: 2027-10-06
sources:
  - id: reddit-usable-stt
    resource: ../raw/best_stt_api_for_voice_agents_i_care_more_about.md
    kind: documentation
    title: Best STT API for voice agents? r/AI_Agents thread capture
---

This thread reframes voice-agent STT selection around usable agent input rather than clean-transcript accuracy, proposing first usable or stable text, partial stability, final-transcript delay, endpointing, barge-in timing, field-level accuracy on phones, dates, names and negations, caller-correction handling, per-turn aligned logs, and cost per successful call as the production checklist, with Smallest AI Pulse named only as the setup under test and TestMu-style end-to-end scenario testing suggested for provider comparison; every claim below is an unverified anecdote from mostly anonymous commenters, not a measured result (**Reported**).[^reddit-usable-stt]

## Source scope and request

- The starter (u/-HEPHAESTUSquest-) reports testing Smallest AI Pulse for voice-agent STT and asks what production voice agents actually measure and what broke first, listing first usable text versus first text, endpointing, barge-in, partial rewrite volatility, final-transcript delay, phone audio, numbers, dates, names, caller corrections, and diagnostic logs; vote count 24 and 23 comments are preserved here as volatile context, not durable findings (**Reported**).[^reddit-usable-stt]
- The capture holds the prompt plus 23 comments with anonymous authors except the starter, no capture date, and one upstream link to the r/AI_Agents thread plus a subreddit-wiki bot pointer; no audio, config, provider pricing, or measurement protocol is given (**Reported**).[^reddit-usable-stt]

## Usable-text evaluation checklist

- Proposed checklist from the prompt and comments: first usable text, partial stability, final delay, endpointing, barge-in timing, field accuracy, phone-audio handling, reconnect behavior, logs per turn, and cost per successful call; one commenter frames Smallest AI Pulse as belonging in the test only when the agent needs realtime speech events rather than a post-call transcript (**Reported**).[^reddit-usable-stt]
- Stop measuring time-to-first-token and instead measure time-to-first-stable token: track how often the last N tokens of a partial get rewritten and how long a span survives before changing, hold downstream commits until a span is stable for a threshold, and prefetch downstream work on the unstable version; the reporter claims this volatility number predicted perceived liveness better than WER (**Reported**).[^reddit-usable-stt]
- WER is characterized as the wrong denominator because a one-word error such as "don't cancel" transcribed as "do cancel" is a total failure; the proposal is to score the action-bearing span separately for negations, digits, names, and dates, with one reporter stating entity-level accuracy ran about 15 points below transcript accuracy in their setup (**Reported**).[^reddit-usable-stt]
- Action-safe transcription is proposed as a separate metric: fast partials may drive turn-taking but must not trigger irreversible tool calls, so dates, phone numbers, amounts, and phrases like "don't cancel" should wait for a stable final or an explicit read-back, and a caller correction must replace the old value in every pending tool call, CRM field, summary, and handoff (**Reported**).[^reddit-usable-stt]
- End-to-end framing: "usable text" is text the agent can safely act on, so provider comparison should use full scenarios (endpointing firing, tool-call timing, TTS stop on interruption) rather than accuracy numbers alone, with TestMu-style testing named as one vehicle for that (**Reported**).[^reddit-usable-stt]

## Failure order reported

- Reported breakage order from a realtime-interpretation (OmniLink) builder: barge-in on speakerphone first, then short low-energy words eaten by endpointing, then corrections landing after commit, then language degradation with overconfident scores (**Reported**).[^reddit-usable-stt]
- Barge-in on speakerphone: VAD kept firing on the agent's own TTS bleeding back through the mic so the agent stopped mid-sentence; barge-in latency is defined as detection plus playback-buffer flush, so the acoustic stop rather than the detection event should be measured (**Reported**).[^reddit-usable-stt]
- Endpointing swallowing short words: aggressive endpointing ate low-energy utterances such as "No" and "Don't", which are exactly the high-stakes tokens for cancellation and correction flows (**Reported**).[^reddit-usable-stt]
- Corrections after commit: "No, 4 not 5" was transcribed correctly but the state machine had already moved on, framed as an architecture problem masquerading as an STT problem (**Reported**).[^reddit-usable-stt]
- Language degradation with high confidence: Haitian Creole accuracy reportedly fell off sharply while confidence scores did not move, so confidence is reported as unusable outside top-tier languages (**Reported**).[^reddit-usable-stt]
- A second latency framing agrees the slow stage is usually STT-side: caller stops, STT waits too long, final arrives late, and even a fast LLM plus fast TTS start still leaves an awkward pause, summarized as death by small delays (**Reported**).[^reddit-usable-stt]

## Logging and diagnosis practice

- Recommended log is a single timeline with aligned timestamps for audio-in, partial, final, LLM first token, and TTS first byte; without it the team cannot attribute a "dead" feeling to STT, model, or playback, and one reporter claims about a month was wasted tuning the wrong stage (**Reported**).[^reddit-usable-stt]
- Logs should tell the operator what broke per turn: which stage delayed the final, whether a partial rewrite changed the action span, whether endpointing cut speech, and whether barge-in stopped playback promptly (**Synthesis**).[^reddit-usable-stt]

## Relationships

- Uses [Parakeet Realtime EOU 120M v1](parakeet-realtime-eou-120m-v1.md): the thread's endpointing and final-delay concerns relate to the end-of-utterance detection approach covered there; the thread names no checkpoint and gives no EOU-latency mapping (**Synthesis**).[^reddit-usable-stt]
- Uses [Audio8 ASR Infinite](audio8-asr-infinite.md): the thread's configurable-tolerance idea (hold commits until stable, prefetch on unstable text) relates to that model's selectable clock and transcription-delay mechanism; read that concept for the verified mechanism (**Synthesis**).[^reddit-usable-stt]
- Uses [Community-Reported Noisy On-Premise STT Selection](community-noisy-call-stt.md): the companion thread concept covers noisy-call model tradeoffs and number-formatting fixups from a different capture; read both as unverified community reports, not measurements (**Synthesis**).[^reddit-usable-stt]
- Uses [Community-Reported Local ASR/TTS Selection](community-asr-tts-selection.md): the companion thread concept covers local ASR/TTS picks, VAD frontends, and leaderboard-plus-regression practices; this concept adds the live-agent usable-text and action-safety framing (**Synthesis**).[^reddit-usable-stt]

## Coverage and limits

- Source inspected statically only; no STT provider installed, no audio transcribed, no latency, stability, entity-accuracy, or cost claim reproduced, and no linked provider page, leaderboard, or repository fetched beyond the URLs quoted above (**Synthesis**).[^reddit-usable-stt]
- Authors are anonymous in the capture (`unknown` except the prompt author), with no capture date, no audio or measurement protocol, no model versions or configs, and no locator beyond comment text; all comparative and performance claims are therefore **Reported** and **Unverified**, and this concept stays `draft` until primary sources or reproductions corroborate them (**Synthesis**).[^reddit-usable-stt]
- Excluded as non-durable: exact vote tallies, pleasantries and status asks ("Any updates?"), the subreddit-wiki bot pointer, and unevaluated promotion-adjacent mentions (Smallest AI Pulse as setup under test, OmniLink as commenter context, TestMu-style testing as suggestion) beyond what is recorded above (**Synthesis**).[^reddit-usable-stt]
- Model-release and performance remarks carry `stale_after: 2027-10-06` per the `stt` and `vad` domain rules (**Synthesis**).[^reddit-usable-stt]

[^reddit-usable-stt]: [Best STT API for voice agents? r/AI_Agents thread capture](../raw/best_stt_api_for_voice_agents_i_care_more_about.md) — locators: title plus upstream link `https://www.reddit.com/r/AI_Agents/comments/1vx1afu/best_stt_api_for_voice_agents_i_care_more_about/` and prompt paragraph (Smallest AI Pulse setup; first usable text, endpointing, barge-in, partial rewrites, final delay, phone audio, numbers/dates/names, corrections, logs); `Comments 23` section — action-safe transcription plus read-back plus correction-propagation remark; time-to-first-stable-token plus span-volatility plus prefetch-on-unstable remark; WER-wrong-denominator plus "don't cancel"/"do cancel" plus ~15-points entity-gap remark; barge-in-on-speakerphone plus detection-plus-flush plus acoustic-stop remark; short-word endpointing ("No", "Don't") remark; corrections-after-commit ("No, 4 not 5") remark; Haitian Creole plus confidence remark; single-timeline audio-in/partial/final/LLM-first-token/TTS-first-byte plus month-tuning-wrong-stage remark; caller-stops/STT-waits/final-late/fast-LLM/fast-TTS death-by-small-delays remark; first-usable-text/partial-stability/final-delay/endpointing/barge-in/field-accuracy/phone-audio/reconnect/logs/cost-per-successful-call checklist plus Pulse-as-realtime-events remark.
