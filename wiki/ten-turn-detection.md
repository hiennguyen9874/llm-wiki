---
type: Concept
title: TEN Turn Detection
description: Text-based three-state (finished / unfinished / wait) turn detector from the TEN framework, built on Qwen2.5-7B for English and Chinese, with vendor-reported per-class accuracy against two anonymous baselines and a one-token Transformers inference recipe.
tags: [vad, endpointing, turn-detection, pipeline, llm-classifier, english, chinese]
status: stable
created: 2026-10-08
generated: { by: llm-wiki-agent/1, at: 2026-10-08T12:00:00Z }
stale_after: 2027-10-08
sources:
  - id: ten-turn-detection
    resource: ../raw/ten-turn-detection/README-github.md
    scope: ../raw/ten-turn-detection/
    kind: documentation
    title: TEN Turn Detection (TEN-framework) GitHub README and Hugging Face model card captures
---

TEN Turn Detection (`TEN-framework/TEN_Turn_Detection`) is an open turn-detection model from the TEN conversational-voice-agent framework. It classifies the user's **text** (a transcript, not audio) into three states — `finished`, `unfinished`, and `wait` — using a transformer language model based on Qwen2.5-7B, and supports English and Chinese. The vendor reports 90.64% / 98.44% / 91% (finished / unfinished / wait) accuracy in English and 98.90% / 92.74% / 92% in Chinese on its own test set, ahead of two unnamed baselines, but publishes no sample counts, latency, memory figures, or Vietnamese coverage (**Reported**).[^ten-turn-detection]

## Task definition

| State | Meaning | README example |
|---|---|---|
| `finished` | The user expressed a complete thought and expects a response | "Hey there I was wondering can you help me with my order" |
| `unfinished` | The user paused but intends to continue | "Hello I have a question about" |
| `wait` | The user explicitly told the AI not to speak | "Shut up" |

- The `wait` state is the distinguishing feature: besides the usual finished/unfinished endpointing decision, it captures an explicit instruction to stay silent, which the README ties to "contextually-aware interruptions" (**Reported**).[^ten-turn-detection]
- The README describes the approach as "multi-layered" and based on Qwen2.5-7B for semantic analysis, but does not state whether the checkpoint is a fine-tune, which training data was used, or how the head/labels are implemented (**Reported**; training details **Unverified**).[^ten-turn-detection]
- Input is the user's utterance text, so the detector depends on upstream STT output and its punctuation/partial-transcript behavior; this is an inference from the text-only API (**Synthesis**).[^ten-turn-detection]

## Inference recipe

- Install: `pip install "transformers>=4.45.0"` and `pip install "torch>=2.0.0"`; weights auto-download on first run, or via Git LFS or `huggingface_hub.snapshot_download` (**Reported**).[^ten-turn-detection]
- GitHub path: clone the repo and run `python inference.py --input "<text>"`; the sample output prints `Turn Detection Result: 'unfinished'` for "Hello I have a question about" (**Reported**; `inference.py` itself is not in the capture).[^ten-turn-detection]
- Hugging Face path: `AutoModelForCausalLM.from_pretrained(..., trust_remote_code=True, torch_dtype=torch.bfloat16)`, model moved to CUDA, chat template applied to a system message (default empty string) plus the user text, then `generate(max_new_tokens=1, do_sample=True, top_p=0.1, temperature=0.1)`; the single generated token is decoded as the label (**Reported**; snippet statically inspected, not run).[^ten-turn-detection]
- Operational reading (**Synthesis**): the call is a one-token generation from a ~7B causal LM, so it needs GPU-class memory (~15 GB for bf16 weights by parameter-count arithmetic, not a vendor figure), requires executing remote model code (`trust_remote_code=True`), and uses sampling with low temperature rather than greedy decoding, so identical inputs are not guaranteed identical labels.[^ten-turn-detection]

## Reported performance

Vendor evaluation on the TEN-Turn-Detection TestSet, accuracy per class; "Model A" and "Model B" are anonymized open-source baselines (**Reported**).[^ten-turn-detection]

| Language | Model | Finished | Unfinished | Wait |
|---|---|---:|---:|---:|
| English | Model A | 59.74% | 86.46% | N/A |
| English | Model B | 71.61% | 96.88% | N/A |
| English | TEN Turn Detection | 90.64% | 98.44% | 91% |
| Chinese | Model B | 74.63% | 88.89% | N/A |
| Chinese | TEN Turn Detection | 98.90% | 92.74% | 92% |

- Model A does not support Chinese; neither baseline supports the `wait` state, so TEN's `wait` accuracy has no comparator (**Reported**).[^ten-turn-detection]
- The test set is a public bilingual collection of three text files, `finished.txt`, `unfinished.txt`, and `wait.txt` (**Reported**); the files and per-file sample counts are not in the capture, so class balance and statistical weight are unknown (**Unverified**).[^ten-turn-detection]
- Limits (**Synthesis**): the baselines are unidentified, metrics are per-class accuracy only (no false-cutoff rate or latency tradeoff, unlike [Smart Turn v3.2](smart-turn.md)'s FPR/FNR benchmark), the evaluation is on clean text rather than noisy ASR output, and the numbers are not comparable to Smart Turn's audio benchmark.[^ten-turn-detection]

## License and provenance

- GitHub README badge and License section: Apache License 2.0 "with additional restrictions" / "certain conditions", referring to a `LICENSE` file that is not in the capture; the Hugging Face card frontmatter and License section say plain Apache 2.0 (**Reported**).[^ten-turn-detection]
- Citation key `TEN_Turn_Detection`, author "TEN Team", year 2025, title "Turn detection for full-duplex dialogue communication" (**Reported**).[^ten-turn-detection]
- Part of the TEN ecosystem next to the TEN Framework, TEN VAD, agent examples, and the TEN portal; a Hugging Face Space demonstrates VAD and turn detection together (**Reported**).[^ten-turn-detection]

## Contradictions

- **License:** the GitHub README says Apache 2.0 with additional restrictions pointing to a `LICENSE` file; the Hugging Face card says Apache 2.0 without qualification. The `LICENSE` text was not captured, so neither is chosen and the conditions are unresolved; check before commercial use (**Reported**).[^ten-turn-detection]

## Relationships

- Compared with [Smart Turn v3.2](smart-turn.md) and other detectors in [Turn Detection Models](turn-detection-models.md): TEN is text-based and ~7B-class with an explicit `wait` state, whereas Smart Turn is audio-native at ~8M parameters with 23 languages including Vietnamese (**Synthesis**).[^ten-turn-detection]
- Belongs to the TEN ecosystem alongside the TEN Framework listed in [Voice Agent Frameworks](voice-agent-frameworks.md) and [TEN VAD](ten-vad.md), whose claim against [Silero VAD](silero-vad.md) is discussed there (**Reported**).[^ten-turn-detection]
- Its `wait` output relates to the interruption concerns in [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md) (**Synthesis**).[^ten-turn-detection]

## Coverage and limits

- Two files inspected statically: the GitHub README (`README-github.md`, entry point) and the Hugging Face model card (`README-hf.md`); the two overlap almost entirely and differ in the quick-start section, license wording, and frontmatter (**Observed**).[^ten-turn-detection]
- No upstream revision, commit, or capture date is recorded for either file, and neither was checksummed against an upstream manifest (**Unverified** freshness).
- Not captured and not inspected: `images/turn_detection.svg` (architecture diagram), `inference.py`, the `LICENSE` file, model weights and remote code, and the test-set text files. Badges, star/community links, and the ecosystem table were excluded as decorative or navigational.
- Nothing was installed or executed, and no benchmark was reproduced. No Vietnamese, latency, memory, or noisy-ASR evidence exists in the source.

[^ten-turn-detection]: [TEN Turn Detection captures](../raw/ten-turn-detection/README-github.md) — `README-github.md`: `Introduction` (three states, Qwen2.5-7B), `Key Features`, `Prepared Dataset`, `Detection Performance` tables and notes, `Quick Start` › `Installation`/`Model Weights`/`Inference`, `Citation`, `TEN Ecosystem`, `License`, header license badge. `README-hf.md`: frontmatter (`license: apache-2.0`, tags), `Introduction`, `Detection Performance`, `Quick Start` › `Inference` Python snippet, `License`.
