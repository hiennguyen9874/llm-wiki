---
language:
  - zh
  - en
  - ja
  - ko
  - es
  - pt
  - ar
  - ru
  - fr
  - de
  - sv
  - it
  - tr
  - 'no'
  - nl
  - cy
  - eu
  - ca
  - da
  - gl
  - ta
  - hu
  - fi
  - pl
  - et
  - hi
  - la
  - ur
  - th
  - vi
  - jw
  - bn
  - yo
  - sl
  - cs
  - sw
  - nn
  - he
  - ms
  - uk
  - id
  - kk
  - bg
  - lv
  - my
  - tl
  - sk
  - ne
  - fa
  - af
  - el
  - bo
  - hr
  - ro
  - sn
  - mi
  - yi
  - am
  - be
  - km
  - is
  - az
  - sd
  - br
  - sq
  - ps
  - mn
  - ht
  - ml
  - sr
  - sa
  - te
  - ka
  - bs
  - pa
  - lt
  - kn
  - si
  - hy
  - mr
  - as
  - gu
  - fo
  
license: other
license_name: fish-audio-research-license
license_link: LICENSE.md
pipeline_tag: text-to-speech
tags:
  - fish-audio
  - text-to-speech
  - multi-speaker
  - audio-editing
  - emotional-speech-generation
---

# Fish Audio Drama 3

**Fish Audio Drama 3** is Fish Audio's new-generation text-to-speech model, built for multi-character
scenes and long-form content. It supports multi-speaker generation, voice cloning and
natural-language control.

- **35B parameters, 3B active per token**: MoE text backbone with hybrid (full + linear) attention
- **Codebook-MTP audio decoder**: 10 codebooks decoded causally over the whole sequence
- **FP8 MoE experts** with the remaining weights in bf16
- **Speaker tags** `<|speaker:0|>` … `<|speaker:15|>` — one text can carry up to 16 characters
- **Long text** is chunked automatically and can be streamed per chunk

## Launch with SGLang Omni

Drama 3 runs on [SGLang-Omni](https://sgl-project.github.io/sglang-omni/) from launch day.  For installation, deployment, and streaming API examples, see the [Drama 3 Cookbook](https://sgl-project.github.io/sglang-omni/cookbook/fishaudio_drama3.html).

```bash
git clone https://github.com/sgl-project/sglang-omni.git && cd sglang-omni
uv pip install --prerelease=allow -v -e ".[fishaudio]"
```

```bash
sgl-omni serve --model-path fishaudio/drama-3 --port 8000
```

## Launch with vLLM-Omni

Drama 3 is supported in [vLLM-Omni](https://github.com/vllm-project/vllm-omni). For installation, deployment, and API examples, see the [Drama 3 vLLM-Omni Recipe](https://recipes.vllm.ai/fishaudio/drama-3).

```bash
git clone https://github.com/vllm-project/vllm-omni.git && cd vllm-omni
uv pip install -e .
```

```bash
vllm serve fishaudio/drama-3 --omni --port 8091
```

## Example Usage

The reference clip the samples below clone, unmodified:

The reference, `en0` — a 3.9 s clip, the same `common_voice_en_10119832.wav` the cloning example above uses, with the transcript `We asked over twenty different people, and they all said it was his.`:

<audio controls>
  <source src="https://github.com/user-attachments/files/33393249/en0.wav" type="audio/wav">
</audio>

### Point tags

A plain `/v1/tts` request: one reference (`en0`), no history, and the tags written into the text at the position where the event should land.

```json
{
  "text": "[sighs] Fine. If we miss it, it's on you. [laughs] Well, maybe that's fair.",
  "references": [{"audio_path": "https://huggingface.co/datasets/zhaochenyang20/seed-tts-eval-mini/resolve/main/en/prompt-wavs/common_voice_en_10119832.wav", "text": "We asked over twenty different people, and they all said it was his."}]
}
```

<audio controls>
  <source src="https://github.com/user-attachments/files/33393205/A1_point_tags.wav" type="audio/wav">
</audio>


### Editing as continuation

Just send the previous VQ tokens and sent it as normal language models do.

```json
{
  "text": "The quarterly report is due on Thursday, so please finish it by noon.",
  "references": [{"audio_path": "https://huggingface.co/datasets/zhaochenyang20/seed-tts-eval-mini/resolve/main/en/prompt-wavs/common_voice_en_10119832.wav", "text": "We asked over twenty different people, and they all said it was his."}],
  "previous_takes": ["The quarterly report is due on Wednesday, so please finish it by noon."]
}
```

<audio controls>
  <source src="https://github.com/user-attachments/files/33393156/K1_edit_word_with_context.wav" type="audio/wav">
</audio>

A second edit chained onto the result of the first:

K5 chains a second edit: `by noon` becomes `by five`, with both earlier takes in the context.

```json
{
  "text": "The quarterly report is due on Thursday, so please finish it by five.",
  "references": [{"audio_path": "https://huggingface.co/datasets/zhaochenyang20/seed-tts-eval-mini/resolve/main/en/prompt-wavs/common_voice_en_10119832.wav", "text": "We asked over twenty different people, and they all said it was his."}],
  "previous_takes": [
    "The quarterly report is due on Wednesday, so please finish it by noon.",
    "The quarterly report is due on Thursday, so please finish it by noon."
  ]
}
```

<audio controls>
  <source src="https://github.com/user-attachments/files/33393164/K5_second_edit_chained.wav" type="audio/wav">
</audio>

## Production Serving

All numbers below were measured on NVIDIA H200 GPUs with streaming requests on Seed-TTS English prompts. Each request clones a voice from one pre-encoded reference (`vq_codes` with its transcript) and uses `temperature` 1.0, `top_p` 0.9, `top_k` 30 and `max_new_tokens` 500. Throughput counts generated acoustic frames per second. TTFA is the time to first audio. RTF is the time from sending a request to its last audio chunk, divided by the duration of the returned audio.

| Concurrency | Throughput (frames/s) | TTFA p50 | TTFA p95 | RTF (mean) |
|---:|---:|---:|---:|---:|
| 1 | 166.7 | 88.9 ms | 90.8 ms | 0.131 |
| 2 | 287.0 | 96.2 ms | 130.1 ms | 0.152 |
| 4 | 467.6 | 108.2 ms | 156.4 ms | 0.186 |
| 8 | 678.1 | 153.2 ms | 210.9 ms | 0.256 |
| 16 | 927.6 | 210.1 ms | 287.2 ms | 0.373 |
| 32 | 1,244.7 | 304.6 ms | 396.1 ms | 0.551 |
| 64 | 1,687.3 | 450.9 ms | 1,020.1 ms | 0.801 |

*Table 1. Drama 3 streaming performance on one H200. Each cell is the mean of four runs.*

A single stream gets its first audio in under 100 ms. At concurrency 16, audio is still generated about 2.7× faster than it plays back, and at concurrency 64 mean RTF stays at 0.80. In SGLang-Omni, how the pipeline stages are grouped into processes and placed on GPUs is deployment-time configuration rather than per-model code. Table 2 uses this to compare two vocoder placements at higher concurrency, with the vocoder's default GPU share, 1,088 requests per concurrency level, and the average of six server starts. Its throughput also counts the end-of-speech frame that ends each stream.

| Vocoder placement | Concurrency | Throughput (frames/s) | TTFA p50 | TTFA p95 |
|---|---:|---:|---:|---:|
| Engine's GPU | 128 | 2,177 | 685 ms | 1,412 ms |
| Engine's GPU | 256 | 2,422 | 3,403 ms | 4,255 ms |
| Second GPU | 128 | 3,692 | 401 ms | 995 ms |
| Second GPU | 256 | 4,160 | 2,146 ms | 2,469 ms |

*Table 2. Drama 3 streaming performance by vocoder placement. Each cell is the mean of six server starts.*

With the vocoder on the engine's GPU, at 256 streams the vocoder is fully loaded and each new stream's first audio waits in its queue. Moving it to a second GPU, as described under [Deployment](https://sgl-project.github.io/sglang-omni/cookbook/fishaudio_drama3.html#deployment), gave about 72% more throughput and a 37% lower median TTFA at 256 streams. Use this layout when you need many concurrent streams and a short time to first audio together.

## Links

- [Fish Audio Playground](https://fish.audio)
- [Fish Speech GitHub](https://github.com/fishaudio/fish-speech)
- [Technical Report](https://arxiv.org/abs/2610.18010)
- [Fish Audio Drama 3 SGLang Omni Cookbook](https://sgl-project.github.io/sglang-omni/cookbook/fishaudio_drama3.html)
- [SGLang Omni](https://sgl-project.github.io/sglang-omni/)
- [Fish Audio Drama 3 vLLM-Omni Recipe](https://recipes.vllm.ai/fishaudio/drama-3)

## License

This model is licensed under the [Fish Audio Community License](https://huggingface.co/fishaudio/drama-3/blob/main/LICENSE). Please refer to the license file for more information.
