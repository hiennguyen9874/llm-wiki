---
license: apache-2.0
language:
- en
tags:
- automatic-speech-recognition
- hf-asr-leaderboard
- whisper
- qwen
pipeline_tag: automatic-speech-recognition
---

# Higgs Audio v3 STT

A speech-to-text model combining a Whisper-Large-v3 encoder with a Qwen3 decoder (2.68B total parameters).

## Update (June 2026)

This repository now hosts an updated checkpoint. Changes:

- Fine-tuning data refreshed: public train splits of AMI (IHM), VoxPopuli (en),
  SPGISpeech, LibriSpeech, TED-LIUM, GigaSpeech, plus the public Earnings22
  train split (`sanchit-gandhi/earnings22_split`) with all rows from source
  recordings that appear in the ESB/Open-ASR test sets excluded.
- `transcribe.py` adds a phrase-level repetition-loop collapse alongside the
  existing word-repetition cap (implemented inline in `transcribe.py`;
  `ngram_loop_fix.py` carries the standalone reference and tests). Both are
  deterministic and applied uniformly to every dataset.
- Evaluation: see the [Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
  for independently produced results; note that figures listed there predate
  this update until the entry is re-evaluated. Figures previously listed on
  this card came from an earlier checkpoint and evaluation setup and are
  superseded.

The previous weights remain available via the git revision history.

## Usage

**Important:** This model uses a custom architecture. You must pass `trust_remote_code=True` when loading.

```python
import torch
from transformers import AutoConfig, AutoModel, AutoTokenizer

# Load model
model = AutoModel.from_pretrained(
    "bosonai/higgs-audio-v3-stt",
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    attn_implementation="eager",
    device_map="cuda:0",
)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained("bosonai/higgs-audio-v3-stt")
```

### Full Transcription Example

Audio preprocessing requires the `boson_multimodal` library:

```python
import torch
import numpy as np
from functools import partial
from dataclasses import asdict
from transformers import AutoConfig, AutoModel, AutoTokenizer, WhisperProcessor

# Load model
config = AutoConfig.from_pretrained("bosonai/higgs-audio-v3-stt", trust_remote_code=True)
model = AutoModel.from_pretrained(
    "bosonai/higgs-audio-v3-stt",
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    attn_implementation="eager",
    device_map="cuda:0",
)
model.eval()
tokenizer = AutoTokenizer.from_pretrained("bosonai/higgs-audio-v3-stt")
model.audio_out_bos_token_id = tokenizer.convert_tokens_to_ids("<|audio_out_bos|>")
model.audio_eos_token_id = tokenizer.convert_tokens_to_ids("<|audio_eos|>")

# Audio collator setup
from boson_multimodal.data_collator.higgs_audio_collator import HiggsAudioSampleCollator
from boson_multimodal.data_types import ChatMLSample, AudioContent, Message
from boson_multimodal.dataset.chatml_dataset import ChatMLDatasetSample, prepare_chatml_sample_qwen

whisper_proc = WhisperProcessor.from_pretrained("openai/whisper-large-v3")
collator = HiggsAudioSampleCollator(
    whisper_processor=whisper_proc,
    audio_in_token_id=config.audio_in_token_idx,
    audio_out_token_id=config.audio_out_token_idx,
    audio_stream_bos_id=config.audio_stream_bos_id,
    audio_stream_eos_id=config.audio_stream_eos_id,
    encode_whisper_embed=config.encode_whisper_embed,
    pad_token_id=config.pad_token_id,
    return_audio_in_tokens=config.encode_audio_in_tokens,
    use_delay_pattern=config.use_delay_pattern,
    round_to=1,
    audio_num_codebooks=config.audio_num_codebooks,
    chunk_size_seconds=getattr(config, "chunk_size_seconds", 30),
    encoder_padding_method=getattr(config, "encoder_padding_method", "max_length"),
)

# Transcribe
import soundfile as sf

audio_np, sr = sf.read("audio.wav")  # must be 16kHz mono
if sr != 16000:
    import librosa
    audio_np = librosa.resample(audio_np, orig_sr=sr, target_sr=16000)

prompt = "Transcribe the speech. Output only the spoken words in lowercase with no punctuation."
messages = [Message(role="user", content=[prompt, AudioContent(audio_url="placeholder")])]
chatml = ChatMLSample(messages=messages)
prep_fn = partial(prepare_chatml_sample_qwen, enable_thinking=True)
input_tokens, _, _, _ = prep_fn(chatml, tokenizer, add_generation_prompt=True)

sample = ChatMLDatasetSample(
    input_ids=torch.LongTensor(input_tokens),
    label_ids=None,
    audio_ids_concat=None,
    audio_ids_start=None,
    audio_waveforms_concat=torch.tensor(audio_np, dtype=torch.float32),
    audio_waveforms_start=torch.tensor([0]),
    audio_sample_rate=torch.tensor([16000]),
    audio_speaker_indices=torch.tensor([0]),
)

batch = asdict(collator([sample]))
device = next(model.parameters()).device
batch = {k: v.to(device).contiguous() if isinstance(v, torch.Tensor) else v for k, v in batch.items()}

with torch.inference_mode():
    outputs = model.generate(**batch, max_new_tokens=1024, use_cache=True, do_sample=False,
                             stop_strings=["<|im_end|>", "<|endoftext|>"], tokenizer=tokenizer)

output_ids = outputs[0] if isinstance(outputs, tuple) else outputs
full_text = tokenizer.decode(output_ids[0], skip_special_tokens=False)

# Extract transcription (remove thinking block and special tokens)
import re
parts = full_text.split("assistant\n")
hyp = parts[-1] if len(parts) > 1 else full_text
hyp = re.sub(r"<think>.*?</think>", "", hyp, flags=re.DOTALL)
hyp = re.sub(r"<\|.*?\|>", "", hyp).strip()
print(hyp)

# For the exact pipeline used in our evaluations (including the
# deterministic repetition/loop post-processing), use transcribe.py
# bundled in this repo: transcribe() / transcribe_batch().
```

## Requirements

```
torch
transformers>=4.51.0
boson_multimodal  # for audio preprocessing
```

## Architecture

- **Encoder:** Whisper-Large-v3 (attention layers fine-tuned in v2)
- **Decoder:** Qwen3-1.7B
- **Total parameters:** 2.68B
- **Audio input:** 16kHz mono WAV
- **Supports:** Thinking mode for improved accuracy
