---
type: Concept
title: KVoiceWalk Usage and Arguments
description: How to run KVoiceWalk: GUI and CLI modes for random walk, interpolated start, voice test, transcription, and voice export, with target-audio requirements, device selection, documented argument defaults, and a voice-folder flag-name conflict.
tags: [tts, kokoro, cli, voice-cloning, operations]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T04:50:00Z }
stale_after: 2027-04-13
sources:
  - id: kvoicewalk-readme
    resource: ../raw/kvoicewalk.md
    kind: documentation
    title: KVoiceWalk README capture
---

Run KVoiceWalk from a `uv`-managed Python 3.10–3.12 environment. Its default interface is a desktop GUI (`uv run gui.py`) that queues tasks; the CLI is `uv run main.py` with mode-specific flags. The README documents five CLI jobs: random walk, interpolated start, voice test, transcription, and voice export. It does not say where a walked voice tensor is written, and its argument names conflict on the voices-folder flag (**Reported**).[^kvoicewalk-readme]

## Setup

- **Prerequisites:** Python 3.10–3.12, `uv`, Tk support for the GUI, and optionally `ffmpeg` (lines 8–12).[^kvoicewalk-readme]
- **GPU:** an NVIDIA driver that supports a CUDA 12.x-class runtime. CUDA wheels arrive through the Python dependencies, so no separate CUDA Toolkit is needed (lines 14–18). A check command is `uv run python -c "import torch; ..."` (lines 19–22).[^kvoicewalk-readme]
- **Install:** clone `https://github.com/RobViren/kvoicewalk.git`, run `uv venv --python 3.10`, activate the venv, and run `uv sync` (lines 38–45).[^kvoicewalk-readme]

## Inputs

- **Target audio:** mono 24,000 Hz WAV, about 20–30 seconds, one speaker (lines 58, 166). The README's conversion command, `ffmpeg -i input_file.wav -ar 24000 target.wav`, sets the sample rate but does not force mono (line 61). A stereo input would keep its channels (**Observed**; the README does not state a mono step).[^kvoicewalk-readme]
- **Target text:** "the words contained in the target audio file", about 100–200 tokens, or a path to a `.txt` transcription (line 146).[^kvoicewalk-readme]
- **Other text:** the `--other_text` passage used for Self Sim; it defaults to a fixed vinegar-and-baking-soda passage and should be about 100–200 tokens (line 149). See [KVoiceWalk Scoring Function](kvoicewalk-scoring-function.md).

## Modes

| Job | Command or flag | Documented behavior | Line |
| --- | --- | --- | --- |
| GUI (default) | `uv run gui.py` | Queue tasks, run them sequentially, and view live logs | 46–52 |
| Random walk | `uv run main.py --target_text "…" --target_audio ./example/target.wav --device cuda --log_interval 100` | Random walk from the population; default output `out.wav` | 64–67 |
| Voice test | `uv run main.py --test_voice /path/to/voice.pt --target_text "…"` | Renders `out.wav` from a `.pt` voice | 72–76 |
| Interpolated start | `--interpolate_start` | Interpolation search first; saves voices to `interpolated`, then continues the walk | 77–84 |
| Transcribe start | `--transcribe_start` | Faster-Whisper transcript replaces `--target_text`; a copy is saved in `./texts` | 118 |
| Transcribe many | `--transcribe_many` on a WAV file or folder | One `.txt` per file in `./texts` | 127 |
| Export | `uv run main.py --voices_folder ./voices --export_bin` | Packages all `.pt` voices in the folder into `voices.bin` in the same folder | 136–140 |

All rows are **Reported**.[^kvoicewalk-readme]

## Arguments and defaults

| Flag | Default | Notes | Line |
| --- | --- | --- | --- |
| `--voice_folder` | `./voices` | Population folder for the random walk (see Contradictions) | 153 |
| `--population_limit` | 10 | Maximum voices used in the walk | 159 |
| `--step_limit` | 10000 | Random-walk step limit | 161 |
| `--output_name` | `out.wav` | Output audio filename | 163 |
| `--interpolate_start` | off | Enables the interpolation search | 157 |
| `--target_audio` | none | Target WAV, 24 kHz mono | 166 |
| `--starting_voice` | none | Starting voice tensor for random-walk mode | 168 |
| `--test_voice` | none | Voice tensor for test mode | 171 |
| `--device` | `auto` | `auto`, `cpu`, or `cuda`; CUDA falls back to CPU when unavailable | 183–187 |
| `--log_interval` | 100 | Progress-log interval for non-interactive runs | 193 |

Defaults and help text are **Reported**.[^kvoicewalk-readme]

## Contradictions

- **Voices-folder flag.** The argument list names `--voice_folder` (line 153), and the `--export_bin` help says "in the --voice_folder directory" (line 174). The export section and example use `--voices_folder` (lines 136–140). Neither form is chosen here. A command copied from one place may fail under the other; the argument parser is not captured, so this is unverified (**Synthesis**).[^kvoicewalk-readme]
- **Hyphenated name.** The transcription section refers to "the --target-text argument" (line 119), while every command uses `--target_text`. The underscore form is used here.[^kvoicewalk-readme]

## Limits

- **Output location:** the README does not say where a walked voice tensor is written, or how a user retrieves it for test mode. The interpolation output folder is named (line 84), but the walk's output is not.
- **Not executed:** no command was run. The flags are as documented and unverified against the parser.
- **Source gap:** `main.py`, `gui.py`, the argument parser, and the `example/target.wav` input are not captured.
- **Revision:** none recorded; the README has no version pin for the tool.

## Relationships

- Drives the method in [KVoiceWalk](kvoicewalk.md), whose Score is described in [KVoiceWalk Scoring Function](kvoicewalk-scoring-function.md) (**Synthesis**).
- Uses [Faster-Whisper](faster-whisper.md) for `--transcribe_start` and `--transcribe_many` (lines 119, 128) (**Reported**).[^kvoicewalk-readme]
- Its voice files are Kokoro-style `.pt` tensors; the README's stock example is `af_heart.pt` (line 29). The Kokoro voice set is described in [Kokoro-82M](kokoro-82m.md) (**Reported**; **Synthesis**).[^kvoicewalk-readme]

[^kvoicewalk-readme]: [KVoiceWalk README capture](../raw/kvoicewalk.md) — locators: lines 8–12 prerequisites; lines 14–22 GPU and CUDA check; lines 38–45 installation; lines 46–52 GUI quick start; lines 58–61 target-audio format and ffmpeg command; lines 64–76 random-walk and test-voice commands; lines 77–84 interpolated start; lines 118–141 transcription and export sections; line 146 `--target_text`; line 149 `--other_text`; lines 153–176 argument list (`--voice_folder`, `--population_limit`, `--step_limit`, `--output_name`, `--target_audio`, `--starting_voice`, `--test_voice`, `--export_bin`, `--transcribe_many`); lines 179–187 device selection; line 193 `--log_interval`; line 29 stock voice name.
