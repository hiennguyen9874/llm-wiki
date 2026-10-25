---
license: apache-2.0
library_name: transformers
pipeline_tag: automatic-speech-recognition
model_name: Jais-ASR
language:
- ar
- arb
- arz
- apd
- ary
- arq
- aeb
- ayl
- mey
- apc
- acm
- afb
- ars
- acw
- acx
- ayn
- en
- fr
- es
- it
tags:
- jais
- ifm
- arabic
- arabic-dialects
- speech-to-text
- code-switching
- diacritization
- language-identification
- open-weights
- custom_code
---

# Jais-ASR

Jais-ASR is IFM's state-of-the-art speech recognition model for Arabic as it is spoken: Modern Standard Arabic and dialects from 19 Arab countries, with natural code-switching into English, French, Spanish, and Italian. Based on Jais-3-4B, it adds optional diacritization, built-in language and dialect identification, and an explicit signal when there is no speech to transcribe. The weights are released under Apache 2.0 with a vLLM plugin, and quantized versions are available in the [Jais Speech collection](https://huggingface.co/collections/IFM/jais-speech).

<p align="center">
  <img src="assets/jais-asr-benchmarks.png" alt="Average word and character error rates on the Open Universal Arabic ASR Leaderboard. Jais-ASR has the lowest of both, 22.85% WER and 8.37% CER, ahead of Audar-ASR-V1-Turbo, Speechmatics Melia 1, ElevenLabs Scribe v2, cohere-transcribe-arabic-07-2026, omniASR-LLM-7B, Qwen3-Omni-30B-A3B, Qwen3-ASR-1.7B and Voxtral-Small-24B." width="100%">
</p>

## Jais-ASR Highlights

- **Leading performance in Arabic ASR.** Jais-ASR has the lowest average error rates on the [Open Universal Arabic ASR Leaderboard](https://github.com/Natural-Language-Processing-Elm/open_universal_arabic_asr_leaderboard), 22.85% WER and 8.37% CER, ahead of every open-weight model compared and the commercial APIs from Speechmatics and ElevenLabs. See [Benchmark Results](#benchmark-results).
- **Built for Arabic as it is spoken in real life.** MSA and dialects across 19 countries, natural code-switching with English, French, Spanish, and Italian, and robust transcription in noisy, real-world recordings.
- **Accurate and faithful.** Optional diacritization, built-in language and dialect identification, and transcripts designed to avoid memorized boilerplate, repetition loops, and translating speech instead of transcribing it. When there is no speech, the model says so instead of inventing text.
- **Ready for production.** Run it with Transformers, or serve it with the included vLLM plugin behind an OpenAI-compatible `/v1/audio/transcriptions` endpoint. The bf16 weights are 11.4 GB.

## Benchmark Results

The [Open Universal Arabic ASR Leaderboard](https://github.com/Natural-Language-Processing-Elm/open_universal_arabic_asr_leaderboard) covers six public test sets spanning read speech, broadcast media, and conversational dialects, in clean and noisy conditions. Evaluated with the leaderboard's own protocol, Jais-ASR leads on both average metrics.

<!-- TABLE:START leaderboard -->
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;margin:0 auto;padding:8px 0 16px;overflow-x:auto"><table style="display:table;width:100%;table-layout:fixed;border-collapse:collapse;font-size:12px;margin:0"><thead><tr><th style="width:18%;border-bottom:none"></th><th colspan="1" style="padding:6px 4px 2px;text-align:center;font-size:11px;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;opacity:0.65;border-bottom:1px solid rgba(128,128,128,0.25)"></th><th colspan="6" style="padding:6px 4px 2px;text-align:center;font-size:11px;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;opacity:0.65;border-bottom:1px solid rgba(128,128,128,0.25)">Open-weight models</th><th colspan="2" style="padding:6px 4px 2px;text-align:center;font-size:11px;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;opacity:0.65;border-bottom:1px solid rgba(128,128,128,0.25)">Closed models</th></tr><tr><th style="padding:10px 6px;text-align:left;border-bottom:2px solid #0b6b4f"></th><th style="padding:10px 3px;text-align:center;font-weight:600;border-bottom:2px solid #0b6b4f;color:#0b6b4f;font-size:12.5px;line-height:1.2;width:9.11%;overflow-wrap:anywhere;background:rgba(11,107,79,0.08);">Jais-ASR</th><th style="padding:10px 3px;text-align:center;font-weight:600;border-bottom:2px solid #0b6b4f;color:#0b6b4f;font-size:12.5px;line-height:1.2;width:9.11%;overflow-wrap:anywhere;">Audar-ASR-V1-Turbo</th><th style="padding:10px 3px;text-align:center;font-weight:600;border-bottom:2px solid #0b6b4f;color:#0b6b4f;font-size:12.5px;line-height:1.2;width:9.11%;overflow-wrap:anywhere;">cohere-transcribe-arabic-07-2026</th><th style="padding:10px 3px;text-align:center;font-weight:600;border-bottom:2px solid #0b6b4f;color:#0b6b4f;font-size:12.5px;line-height:1.2;width:9.11%;overflow-wrap:anywhere;">omniASR-LLM-7B</th><th style="padding:10px 3px;text-align:center;font-weight:600;border-bottom:2px solid #0b6b4f;color:#0b6b4f;font-size:12.5px;line-height:1.2;width:9.11%;overflow-wrap:anywhere;">Qwen3-Omni-30B-A3B</th><th style="padding:10px 3px;text-align:center;font-weight:600;border-bottom:2px solid #0b6b4f;color:#0b6b4f;font-size:12.5px;line-height:1.2;width:9.11%;overflow-wrap:anywhere;">Qwen3-ASR-1.7B</th><th style="padding:10px 3px;text-align:center;font-weight:600;border-bottom:2px solid #0b6b4f;color:#0b6b4f;font-size:12.5px;line-height:1.2;width:9.11%;overflow-wrap:anywhere;">Voxtral-Small-24B</th><th style="padding:10px 3px;text-align:center;font-weight:600;border-bottom:2px solid #0b6b4f;color:#0b6b4f;font-size:12.5px;line-height:1.2;width:9.11%;overflow-wrap:anywhere;">Melia 1<div style="margin-top:2px;font-size:10px;opacity:0.65;font-weight:400">Speechmatics</div></th><th style="padding:10px 3px;text-align:center;font-weight:600;border-bottom:2px solid #0b6b4f;color:#0b6b4f;font-size:12.5px;line-height:1.2;width:9.11%;overflow-wrap:anywhere;">Scribe v2<div style="margin-top:2px;font-size:10px;opacity:0.65;font-weight:400">ElevenLabs</div></th></tr></thead><tbody><tr><td colspan="10" style="padding:6px 10px;font-weight:600;font-size:12.5px;color:#0b6b4f;border-bottom:1px solid rgba(11,107,79,0.25);background:rgba(11,107,79,0.12)">Word error rate (WER, %) ↓</td></tr><tr><td style="padding:6px 4px 6px 10px;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle"><div style="font-size:12.5px;font-weight:600;line-height:1.2;color:inherit">Average</div><div style="margin-top:2px;font-size:10px;opacity:0.65">Macro-average, six test sets</div></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;background:rgba(11,107,79,0.08);"><strong>22.85</strong></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">23.17</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">25.87</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">28.32</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">30.71</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">33.36</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">34.47</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">23.51</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">24.54</td></tr><tr><td style="padding:6px 4px 6px 10px;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle"><div style="font-size:12.5px;font-weight:600;line-height:1.2;color:inherit">SADA</div><div style="margin-top:2px;font-size:10px;opacity:0.65">Saudi dialectal broadcast</div></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;background:rgba(11,107,79,0.08);">30.85</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;"><strong>28.92</strong></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">37.47</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">41.61</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">44.82</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">45.53</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">50.82</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">34.74</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">33.96</td></tr><tr><td style="padding:6px 4px 6px 10px;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle"><div style="font-size:12.5px;font-weight:600;line-height:1.2;color:inherit">Common Voice 18</div><div style="margin-top:2px;font-size:10px;opacity:0.65">MSA read speech</div></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;background:rgba(11,107,79,0.08);">8.56</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">8.09</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">5.82</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">8.75</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">11.46</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">16.90</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">15.25</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;"><strong>5.19</strong></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">8.71</td></tr><tr><td style="padding:6px 4px 6px 10px;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle"><div style="font-size:12.5px;font-weight:600;line-height:1.2;color:inherit">MASC clean</div><div style="margin-top:2px;font-size:10px;opacity:0.65">MSA lectures, clean</div></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;background:rgba(11,107,79,0.08);"><strong>16.12</strong></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">16.73</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">19.60</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">19.69</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">21.47</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">24.37</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">23.96</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">16.23</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">16.91</td></tr><tr><td style="padding:6px 4px 6px 10px;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle"><div style="font-size:12.5px;font-weight:600;line-height:1.2;color:inherit">MASC noisy</div><div style="margin-top:2px;font-size:10px;opacity:0.65">MSA lectures, noisy</div></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;background:rgba(11,107,79,0.08);"><strong>25.44</strong></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">27.19</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">27.07</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">29.29</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">30.85</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">34.29</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">34.43</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">25.89</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">27.15</td></tr><tr><td style="padding:6px 4px 6px 10px;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle"><div style="font-size:12.5px;font-weight:600;line-height:1.2;color:inherit">MGB-2</div><div style="margin-top:2px;font-size:10px;opacity:0.65">MSA broadcast news</div></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;background:rgba(11,107,79,0.08);"><strong>9.59</strong></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">11.08</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">15.54</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">14.13</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">13.09</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">16.57</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">16.03</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">12.61</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">10.30</td></tr><tr><td style="padding:6px 4px 6px 10px;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle"><div style="font-size:12.5px;font-weight:600;line-height:1.2;color:inherit">Casablanca</div><div style="margin-top:2px;font-size:10px;opacity:0.65">8 dialects, conversational</div></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;background:rgba(11,107,79,0.08);">46.56</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">47.02</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">49.71</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">56.46</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">62.55</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">64.47</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">66.30</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;"><strong>46.41</strong></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">50.20</td></tr><tr><td colspan="10" style="padding:6px 10px;font-weight:600;font-size:12.5px;color:#0b6b4f;border-bottom:1px solid rgba(11,107,79,0.25);background:rgba(11,107,79,0.12)">Character error rate (CER, %) ↓</td></tr><tr><td style="padding:6px 4px 6px 10px;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle"><div style="font-size:12.5px;font-weight:600;line-height:1.2;color:inherit">Average</div><div style="margin-top:2px;font-size:10px;opacity:0.65">Macro-average, six test sets</div></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;background:rgba(11,107,79,0.08);"><strong>8.37</strong></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">9.23</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">11.80</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">12.52</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">13.67</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">12.33</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">15.29</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">10.62</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">9.96</td></tr><tr><td style="padding:6px 4px 6px 10px;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle"><div style="font-size:12.5px;font-weight:600;line-height:1.2;color:inherit">SADA</div><div style="margin-top:2px;font-size:10px;opacity:0.65">Saudi dialectal broadcast</div></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;background:rgba(11,107,79,0.08);">14.33</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;"><strong>13.40</strong></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">23.53</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">24.95</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">26.11</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">19.90</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">28.85</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">21.21</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">16.48</td></tr><tr><td style="padding:6px 4px 6px 10px;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle"><div style="font-size:12.5px;font-weight:600;line-height:1.2;color:inherit">Common Voice 18</div><div style="margin-top:2px;font-size:10px;opacity:0.65">MSA read speech</div></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;background:rgba(11,107,79,0.08);">2.70</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">2.46</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;"><strong>1.62</strong></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">2.71</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">4.28</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">5.06</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">5.54</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;"><strong>1.62</strong></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">3.00</td></tr><tr><td style="padding:6px 4px 6px 10px;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle"><div style="font-size:12.5px;font-weight:600;line-height:1.2;color:inherit">MASC clean</div><div style="margin-top:2px;font-size:10px;opacity:0.65">MSA lectures, clean</div></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;background:rgba(11,107,79,0.08);"><strong>3.76</strong></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">5.32</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">6.45</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">5.76</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">5.59</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">5.72</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">7.06</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">5.11</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">4.97</td></tr><tr><td style="padding:6px 4px 6px 10px;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle"><div style="font-size:12.5px;font-weight:600;line-height:1.2;color:inherit">MASC noisy</div><div style="margin-top:2px;font-size:10px;opacity:0.65">MSA lectures, noisy</div></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;background:rgba(11,107,79,0.08);"><strong>7.51</strong></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">9.78</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">10.13</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">10.66</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">11.28</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">10.84</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">12.22</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">9.47</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">9.36</td></tr><tr><td style="padding:6px 4px 6px 10px;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle"><div style="font-size:12.5px;font-weight:600;line-height:1.2;color:inherit">MGB-2</div><div style="margin-top:2px;font-size:10px;opacity:0.65">MSA broadcast news</div></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;background:rgba(11,107,79,0.08);"><strong>3.92</strong></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">5.64</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">8.40</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">7.10</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">6.20</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">6.25</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">7.41</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">5.88</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">4.78</td></tr><tr><td style="padding:6px 4px 6px 10px;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle"><div style="font-size:12.5px;font-weight:600;line-height:1.2;color:inherit">Casablanca</div><div style="margin-top:2px;font-size:10px;opacity:0.65">8 dialects, conversational</div></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;background:rgba(11,107,79,0.08);"><strong>18.02</strong></td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">18.75</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">20.66</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">23.96</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">28.53</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">26.23</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">30.64</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">20.41</td><td style="padding:6px 2px;text-align:center;border-bottom:1px solid rgba(128,128,128,0.15);vertical-align:middle;font-size:12.5px;line-height:1.2;">21.18</td></tr></tbody></table></div>
<!-- TABLE:END leaderboard -->

<p style="font-size:1.25em;line-height:1.6">Error rates in %; lower is better. Average is the macro-average over the six test sets. Jais-ASR was measured with the leaderboard's evaluation script. Scores for the other open-weight models are taken from the leaderboard; Speechmatics Melia 1 and ElevenLabs Scribe v2 were measured by IFM.</p>

## Capabilities

Jais-ASR brings Arabic speech transcription, code-switching, diacritization, and language identification into one model, with controls to tailor the output to your application.

- **Transcribe multilingual speech as spoken.** Enable `code_switch=True` to keep English, French, Spanish, or Italian spans in their original script alongside Arabic, useful for interviews and everyday conversations.
- **Add diacritics for clearer Arabic pronunciation.** Enable `diacritics=True` to add vowel marks to Arabic transcripts, making them easier to read and supporting language learning. Diacritics and code-switching can be enabled together.
- **Detect the language and dialect as you transcribe.** Each transcript comes with its recognized language or dialect label, so you can organize recordings and route text to downstream tools without a separate identification model.
- **Handle non-speech audio explicitly.** When audio contains no speech (e.g., music or noise), the model returns `[IFM-NoTranscript]` with the flag `refused=True` instead of hallucinated content, giving applications a clear signal to handle the case separately.
- **Process multiple recordings at once.** Batch transcription supports files with different durations and sample rates.

### Language and Dialect Settings

Automatic language and dialect detection is enabled by default. If the language of the audio is known in advance, set it with one of the codes below: `ar` allows Modern Standard Arabic and all 19 supported dialects, `msa` selects Modern Standard Arabic, and a dialect code such as `EG` selects that dialect.

| Language | Setting |
|---|---|
| Arabic, including all supported dialects | `ar` |
| Modern Standard Arabic | `msa` |
| English | `en` |
| French | `fr` |
| Spanish | `es` |
| Italian | `it` |

The 19 Arabic dialect codes are:

Algerian (`DZ`) · Bahraini (`BH`) · Egyptian (`EG`) · Emirati (`AE`) · Iraqi (`IQ`) · Jordanian (`JO`) · Kuwaiti (`KW`) · Lebanese (`LB`) · Libyan (`LY`) · Mauritanian (`MR`) · Moroccan (`MA`) · Omani (`OM`) · Palestinian (`PS`) · Qatari (`QA`) · Saudi (`SA`) · Sudanese (`SD`) · Syrian (`SY`) · Tunisian (`TN`) · Yemeni (`YE`)

## Quickstart

Install PyTorch for your hardware, then install the inference dependencies:

```bash
pip install 'transformers==5.16.1' accelerate soundfile soxr
```

The examples below use a GPU with bfloat16 support. The bf16 weights are 11.4 GB; plan on roughly 12 GB of GPU memory.

### Transformers Pipeline

```python
import torch
from transformers import pipeline

asr = pipeline(
    "automatic-speech-recognition",
    model="IFM/Jais-ASR",
    trust_remote_code=True,
    device_map="auto",
    dtype=torch.bfloat16,
)
result = asr("speech.wav", max_new_tokens=256)
print(result["text"])
```

The pipeline accepts an audio file path or a waveform dictionary such as `{"array": waveform, "sampling_rate": 16000}`. For batches and structured metadata, use the model and processor directly as shown below.

### Batch Transcription

This example transcribes two files together, including clips with different durations or sample rates.

```python
import soundfile as sf
import torch
from transformers import AutoModelForCausalLM, AutoProcessor

model_id = "IFM/Jais-ASR"
processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
processor.tokenizer.padding_side = "left"
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    trust_remote_code=True,
    device_map="auto",
    dtype=torch.bfloat16,
).eval()

paths = ["speech_1.wav", "speech_2.wav"]
audio = [sf.read(path, dtype="float32") for path in paths]
waveforms = [waveform for waveform, _ in audio]
sample_rates = [sample_rate for _, sample_rate in audio]

prompt = processor.tokenizer.apply_chat_template(
    [{"role": "user", "content": [{"type": "audio"}]}],
    tokenize=False,
    add_generation_prompt=True,
    # diacritics=True,   # Add Arabic vowel marks.
    # code_switch=True,  # Keep other languages in their original script.
)
inputs = processor(
    text=[prompt] * len(waveforms),
    audio=waveforms,
    sampling_rate=sample_rates,
    padding=True,
    return_tensors="pt",
).to(model.device)

with torch.inference_mode():
    output = model.generate(
        **inputs,
        do_sample=False,
        max_new_tokens=256,
        # language="EG",  # Set the target language to override automatic detection.
    )

transcripts = processor.post_process_transcription(
    output, input_lengths=inputs["input_ids"].shape[1],
)
for path, result in zip(paths, transcripts):
    print(path, {
        "text": result.text,
        "language": result.language,
        "refused": result.refused,
    })
```

`language` contains a language or dialect label, such as `msa`, `EG`, or `en`. When the model emits `[IFM-NoTranscript]`, postprocessing sets `refused=True` and returns an empty transcript. Uncomment either prompt option above to request diacritics or code-switching; both can be enabled together.

> [!TIP]
> Pass each recording's original sample rate; the processor resamples it to 16 kHz automatically. Increase `max_new_tokens` for longer recordings: a result with `truncated=True` means generation ended before the transcript was complete.

### Serving with vLLM

Jais-ASR ships with a vLLM plugin in [`vllm_plugin/`](https://huggingface.co/IFM/Jais-ASR/tree/main/vllm_plugin). Install it in its own environment, then start the server:

```bash
pip install 'vllm==0.23.0' 'transformers==5.5.4' accelerate soundfile soxr
hf download IFM/Jais-ASR --include "vllm_plugin/*" --local-dir Jais-ASR
pip install ./Jais-ASR/vllm_plugin
vllm serve IFM/Jais-ASR --trust-remote-code --reasoning-parser jais_asr_tag --max-model-len 2048
```

Transcribe a file through the OpenAI-compatible endpoint:

```bash
curl http://localhost:8000/v1/audio/transcriptions \
  -F file=@clip.wav \
  -F model=IFM/Jais-ASR
```

## Citation

```bibtex
@misc{jaisasr2026,
  title  = {Introducing Jais-ASR: Arabic Speech Recognition for Every Dialect},
  author = {{IFM Team}},
  year   = {2026},
  url    = {https://huggingface.co/IFM/Jais-ASR},
}
```