---
license: apache-2.0
language:
- ar
- en
pipeline_tag: automatic-speech-recognition
tags:
- audio
- speech-recognition
- transcription
- arabic
- asr
- arabic-asr
- arabic-dialect
- arabic-speech-recognition
library_name: transformers
base_model:
- CohereLabs/cohere-transcribe-03-2026
---
# Cohere Transcribe Arabic

**Cohere Transcribe Arabic is an open source 2B-parameter Arabic automatic speech recognition model for speech-to-text transcription.** It is optimized for Arabic, Arabic Dialects, English, and Arabic-English code-switched speech.
Use it for Arabic ASR, Arabic audio transcription, dialectal Arabic speech recognition, and English speech-to-text. The model uses a Conformer encoder-decoder architecture and is supported natively in Transformers.
Based on the [Cohere Transcribe](https://huggingface.co/CohereLabs/cohere-transcribe-03-2026) architecture.

Developed by: [Cohere](https://cohere.com) and [Cohere Labs](https://cohere.com/research). Point of Contact: [Cohere Labs](https://cohere.com/research).

<style>
    @scope {
        th, td {
            text-align: left;
            padding: 0.375rem 0.625rem;
            letter-spacing: 0;
            vertical-align: top;
            line-height: 133.3333%;
            border: 1px solid #e0e0e0;
        }
        ul {
            list-style-type: disc;
            margin: 0;
            padding-left: 1em;

            li {
                margin: 0.25rem 0 0;
                line-height: 133.3333%;
            }
        }
    }
</style>
<table>
    <tbody>
        <tr>
            <th>Name</th>
            <td><strong>cohere-transcribe-arabic-07-2026</strong></td>
        </tr>
        <tr>
            <th>Architecture</th>
            <td>conformer-based encoder-decoder</td>
        </tr>
        <tr>
            <th>Input</th>
            <td>audio waveform → log-Mel spectrogram. Audio is automatically resampled to 16kHz if necessary during preprocessing. Similarly, multi-channel (stereo) inputs are averaged to produce a single channel signal.</td>
        </tr>
        <tr>
            <th>Output</th>
            <td>transcribed text</td>
        </tr>
        <tr>
            <th>Model</th>
            <td>a large Conformer encoder extracts acoustic representations, followed by a lightweight Transformer decoder for token generation</td>
        </tr>
        <tr>
            <th>Training objective</th>
            <td>supervised cross-entropy on output tokens</td>
        </tr>
        <tr>
            <th>Languages</th>
            <td>
                <ul>
                    <li>Arabic</li>
                    <li>English</li>
                </ul>
            </td>
        </tr>
        <tr>
            <th>License</th>
            <td>Apache 2.0</td>
        </tr>
    </tbody>
</table>

✨Try the Cohere Transcribe Arabic [demo](https://huggingface.co/spaces/CohereLabs/cohere-transcribe-arabic-07-2026)✨

## Usage

Cohere Transcribe Arabic is supported natively in `transformers`. This is the recommended way to use the model for
offline inference. For online inference, see the vLLM integration example below.

```bash
pip install transformers>=5.4.0 torch huggingface_hub soundfile librosa sentencepiece protobuf accelerate
```

### Quick Start 🤗

Transcribe any audio file in a few lines:

```python
from transformers import AutoProcessor, CohereAsrForConditionalGeneration
from transformers.audio_utils import load_audio
from huggingface_hub import hf_hub_download

processor = AutoProcessor.from_pretrained("CohereLabs/cohere-transcribe-arabic-07-2026")
model = CohereAsrForConditionalGeneration.from_pretrained("CohereLabs/cohere-transcribe-arabic-07-2026", device_map="auto")

# Example: transcribe Arabic audio
audio_file = "your_audio.wav"
audio = load_audio(audio_file, sampling_rate=16000)

inputs = processor(audio, sampling_rate=16000, return_tensors="pt", language="ar")
inputs.to(model.device, dtype=model.dtype)

outputs = model.generate(**inputs, max_new_tokens=256)
text = processor.decode(outputs, skip_special_tokens=True)
print(text)
```

<details>
<summary><b>Long-form transcription</b></summary>

For audio longer than the feature extractor's `max_audio_clip_s`, the feature extractor automatically splits the waveform into chunks.
The processor reassembles the per-chunk transcriptions using the returned `audio_chunk_index`.

```python
from transformers import AutoProcessor, CohereAsrForConditionalGeneration
import time

processor = AutoProcessor.from_pretrained("CohereLabs/cohere-transcribe-arabic-07-2026")
model = CohereAsrForConditionalGeneration.from_pretrained("CohereLabs/cohere-transcribe-arabic-07-2026", device_map="auto")

audio = load_audio("your_long_audio.wav", sampling_rate=16000)
sr = 16000
duration_s = len(audio) / sr
print(f"Audio duration: {duration_s / 60:.1f} minutes")

inputs = processor(audio=audio, sampling_rate=sr, return_tensors="pt", language="ar")
audio_chunk_index = inputs.get("audio_chunk_index")
inputs.to(model.device, dtype=model.dtype)

start = time.time()
outputs = model.generate(**inputs, max_new_tokens=256)
text = processor.decode(outputs, skip_special_tokens=True, audio_chunk_index=audio_chunk_index, language="ar")[0]
elapsed = time.time() - start
rtfx = duration_s / elapsed
print(f"Transcribed in {elapsed:.1f}s — RTFx: {rtfx:.1f}")
print(text)
```
</details>

<!-- <details>
<summary><b>Punctuation control</b></summary>

Pass `punctuation=False` to obtain lower-cased output without punctuation marks.

```python
inputs_pnc = processor(audio, sampling_rate=16000, return_tensors="pt", language="ar", punctuation=True)
inputs_nopnc = processor(audio, sampling_rate=16000, return_tensors="pt", language="ar", punctuation=False)
```

By default, punctuation is enabled.

</details> -->

<details>
<summary><b>English transcription</b></summary>

The model also supports English. Specify `language="en"`:

```python
inputs = processor(audio, sampling_rate=16000, return_tensors="pt", language="en")
inputs.to(model.device, dtype=model.dtype)

outputs = model.generate(**inputs, max_new_tokens=256)
text = processor.decode(outputs, skip_special_tokens=True)
print(text)
```
</details>


### vLLM Integration

For production serving we recommend running via vLLM following the instructions below.

<details>
<summary><b>Run cohere-transcribe-arabic-07-2026 via vLLM</b></summary>

First install vLLM (refer to [vLLM installation instructions](https://docs.vllm.ai/en/latest/getting_started/installation/)):

```bash
uv venv --python 3.12 --seed
source .venv/bin/activate

uv pip install -U vllm==0.19.0 --torch-backend=auto
uv pip install vllm[audio]
uv pip install librosa
```

Start vLLM server
```bash
vllm serve CohereLabs/cohere-transcribe-arabic-07-2026 --trust-remote-code
```

Send request
```bash
curl -v -X POST http://localhost:8000/v1/audio/transcriptions \
 -H "Authorization: Bearer $VLLM_API_KEY" \
-F "file=@$(realpath ${AUDIO_PATH})" \
-F "model=CohereLabs/cohere-transcribe-arabic-07-2026"
```
</details>

## Results
<details>
<summary><b>Open Universal Arabic ASR Leaderboard (as of 07.07.2026)</b></summary>
  
<style>
    table.simple {
    border-collapse: collapse;
    }

    table.simple th,
    table.simple td {
    text-align: left;
    padding: 0.375rem 0.625rem;
    min-width: 5em;
    vertical-align: top;
    line-height: 1.2;
    border-bottom: 1px solid rgba(127,127,127,0.35);
    }

    table.simple thead th {
    white-space: nowrap;
    }

    table.simple th:first-child {
    position: sticky;
    left: 0;
    background: inherit;
    z-index: 1;
    }

    table.simple .num {
    text-align: right;
    }

    table.simple .highlight-row > th,
    table.simple .highlight-row > td {
    background: rgba(127,127,127,0.12);
    }

    table.simple .highlight-cell {
    background: rgba(127,127,127,0.18);
    }

    table.simple .metric {
    display: block;
    white-space: nowrap;
    }

    table.simple .metric-cer {
    display: block;
    font-size: 0.85em;
    opacity: 0.65;
    white-space: nowrap;
    }

    table.simple thead .metric-hint {
    display: block;
    font-size: 0.75em;
    font-weight: normal;
    opacity: 0.6;
    margin-top: 0.15em;
    }
</style>

<div style="overflow-x: auto;">
<table class="simple text-web3-14 font-body">
    <thead>
        <tr>
            <th>Model</th>
            <th class="num">Average<span class="metric-hint">WER · CER</span></th>
            <th class="num">SADA<span class="metric-hint">WER · CER</span></th>
            <th class="num">Common Voice<span class="metric-hint">WER · CER</span></th>
            <th class="num">MASC clean<span class="metric-hint">WER · CER</span></th>
            <th class="num">MASC noisy<span class="metric-hint">WER · CER</span></th>
            <th class="num">MGB-2<span class="metric-hint">WER · CER</span></th>
            <th class="num">Casablanca<span class="metric-hint">WER · CER</span></th>
        </tr>
    </thead>
    <tbody>
        <tr class="highlight-row">
            <th><strong style="white-space:nowrap">Cohere Transcribe Arabic 07-2026</strong></th>
            <td class="num highlight-cell"><span class="metric"><strong>25.87</strong></span><span class="metric-cer"><strong>11.80</strong></span></td>
            <td class="num"><span class="metric"><strong>37.47</strong></span><span class="metric-cer"><strong>23.53</strong></span></td>
            <td class="num"><span class="metric"><strong>5.82</strong></span><span class="metric-cer"><strong>1.62</strong></span></td>
            <td class="num"><span class="metric">19.60</span><span class="metric-cer">6.45</span></td>
            <td class="num"><span class="metric">27.07</span><span class="metric-cer">10.13</span></td>
            <td class="num"><span class="metric">15.54</span><span class="metric-cer">8.40</span></td>
            <td class="num"><span class="metric"><strong>49.71</strong></span><span class="metric-cer"><strong>20.66</strong></span></td>
        </tr>
        <tr>
            <th style="font-weight:normal;">OmniASR LLM 7B</th>
            <td class="num"><span class="metric">28.32</span><span class="metric-cer">12.52</span></td>
            <td class="num"><span class="metric">41.61</span><span class="metric-cer">24.95</span></td>
            <td class="num"><span class="metric">8.75</span><span class="metric-cer">2.71</span></td>
            <td class="num"><span class="metric">19.69</span><span class="metric-cer">5.76</span></td>
            <td class="num"><span class="metric">29.29</span><span class="metric-cer">10.66</span></td>
            <td class="num"><span class="metric">14.13</span><span class="metric-cer">7.10</span></td>
            <td class="num"><span class="metric">56.46</span><span class="metric-cer">23.96</span></td>
        </tr>
        <tr>
            <th style="font-weight:normal;">OmniASR LLM 3B</th>
            <td class="num"><span class="metric">29.96</span><span class="metric-cer">13.77</span></td>
            <td class="num"><span class="metric">46.18</span><span class="metric-cer">27.27</span></td>
            <td class="num"><span class="metric">9.15</span><span class="metric-cer">2.80</span></td>
            <td class="num"><span class="metric">19.90</span><span class="metric-cer">6.13</span></td>
            <td class="num"><span class="metric">30.03</span><span class="metric-cer">11.27</span></td>
            <td class="num"><span class="metric">14.22</span><span class="metric-cer">7.06</span></td>
            <td class="num"><span class="metric">60.27</span><span class="metric-cer">28.06</span></td>
        </tr>
        <tr>
            <th style="font-weight:normal;">OmniASR LLM 1B</th>
            <td class="num"><span class="metric">29.96</span><span class="metric-cer">13.40</span></td>
            <td class="num"><span class="metric">43.84</span><span class="metric-cer">24.54</span></td>
            <td class="num"><span class="metric">9.55</span><span class="metric-cer">2.97</span></td>
            <td class="num"><span class="metric">20.03</span><span class="metric-cer">6.14</span></td>
            <td class="num"><span class="metric">30.26</span><span class="metric-cer">11.18</span></td>
            <td class="num"><span class="metric">15.34</span><span class="metric-cer">7.56</span></td>
            <td class="num"><span class="metric">60.68</span><span class="metric-cer">28.02</span></td>
        </tr>
        <tr>
            <th style="font-weight:normal;">Cohere Transcribe 03-2026</th>
            <td class="num"><span class="metric">30.67</span><span class="metric-cer">16.37</span></td>
            <td class="num"><span class="metric">60.11</span><span class="metric-cer">45.44</span></td>
            <td class="num"><span class="metric">8.17</span><span class="metric-cer">2.49</span></td>
            <td class="num"><span class="metric"><strong>8.66</strong></span><span class="metric-cer"><strong>2.97</strong></span></td>
            <td class="num"><span class="metric"><strong>19.01</strong></span><span class="metric-cer"><strong>7.71</strong></span></td>
            <td class="num"><span class="metric">25.33</span><span class="metric-cer">9.28</span></td>
            <td class="num"><span class="metric">62.71</span><span class="metric-cer">30.31</span></td>
        </tr>
        <tr>
            <th style="font-weight:normal;">Qwen3-Omni 30B</th>
            <td class="num"><span class="metric">30.71</span><span class="metric-cer">13.67</span></td>
            <td class="num"><span class="metric">44.82</span><span class="metric-cer">26.11</span></td>
            <td class="num"><span class="metric">11.46</span><span class="metric-cer">4.28</span></td>
            <td class="num"><span class="metric">21.47</span><span class="metric-cer">5.59</span></td>
            <td class="num"><span class="metric">30.85</span><span class="metric-cer">11.28</span></td>
            <td class="num"><span class="metric"><strong>13.09</strong></span><span class="metric-cer"><strong>6.20</strong></span></td>
            <td class="num"><span class="metric">62.55</span><span class="metric-cer">28.53</span></td>
        </tr>
        <tr>
            <th style="font-weight:normal;">NVIDIA Conformer-CTC (LM)</th>
            <td class="num"><span class="metric">32.91</span><span class="metric-cer">13.84</span></td>
            <td class="num"><span class="metric">44.52</span><span class="metric-cer">23.76</span></td>
            <td class="num"><span class="metric">8.80</span><span class="metric-cer">2.77</span></td>
            <td class="num"><span class="metric">23.74</span><span class="metric-cer">5.63</span></td>
            <td class="num"><span class="metric">34.29</span><span class="metric-cer">11.07</span></td>
            <td class="num"><span class="metric">17.20</span><span class="metric-cer">6.87</span></td>
            <td class="num"><span class="metric">68.90</span><span class="metric-cer">32.97</span></td>
        </tr>
        <tr>
            <th style="font-weight:normal;">OmniASR LLM 300M</th>
            <td class="num"><span class="metric">32.96</span><span class="metric-cer">14.84</span></td>
            <td class="num"><span class="metric">51.38</span><span class="metric-cer">29.10</span></td>
            <td class="num"><span class="metric">12.03</span><span class="metric-cer">4.04</span></td>
            <td class="num"><span class="metric">20.66</span><span class="metric-cer">6.22</span></td>
            <td class="num"><span class="metric">32.45</span><span class="metric-cer">12.23</span></td>
            <td class="num"><span class="metric">16.58</span><span class="metric-cer">7.86</span></td>
            <td class="num"><span class="metric">64.64</span><span class="metric-cer">29.61</span></td>
        </tr>
        <tr>
            <th style="font-weight:normal;">Gemma 4 E4B</th>
            <td class="num"><span class="metric">32.98</span><span class="metric-cer">13.71</span></td>
            <td class="num"><span class="metric">43.40</span><span class="metric-cer">20.96</span></td>
            <td class="num"><span class="metric">19.65</span><span class="metric-cer">7.48</span></td>
            <td class="num"><span class="metric">24.86</span><span class="metric-cer">7.76</span></td>
            <td class="num"><span class="metric">33.59</span><span class="metric-cer">12.25</span></td>
            <td class="num"><span class="metric">17.72</span><span class="metric-cer">8.67</span></td>
            <td class="num"><span class="metric">58.63</span><span class="metric-cer">25.11</span></td>
        </tr>
        <tr>
            <th style="font-weight:normal;">Qwen3-ASR 1.7B</th>
            <td class="num"><span class="metric">33.36</span><span class="metric-cer">12.33</span></td>
            <td class="num"><span class="metric">45.53</span><span class="metric-cer">19.90</span></td>
            <td class="num"><span class="metric">16.90</span><span class="metric-cer">5.06</span></td>
            <td class="num"><span class="metric">24.37</span><span class="metric-cer">5.72</span></td>
            <td class="num"><span class="metric">34.29</span><span class="metric-cer">10.84</span></td>
            <td class="num"><span class="metric">16.57</span><span class="metric-cer">6.25</span></td>
            <td class="num"><span class="metric">64.47</span><span class="metric-cer">26.23</span></td>
        </tr>
              <tr>
            <th style="font-weight:normal;">Voxtral-Small 24B</th>
            <td class="num"><span class="metric">34.47</span><span class="metric-cer">15.29</span></td>
            <td class="num"><span class="metric">50.82</span><span class="metric-cer">28.85</span></td>
            <td class="num"><span class="metric">15.25</span><span class="metric-cer">5.54</span></td>
            <td class="num"><span class="metric">23.96</span><span class="metric-cer">7.06</span></td>
            <td class="num"><span class="metric">34.43</span><span class="metric-cer">12.22</span></td>
            <td class="num"><span class="metric">16.03</span><span class="metric-cer">7.41</span></td>
            <td class="num"><span class="metric">66.30</span><span class="metric-cer">30.64</span></td>
        </tr>
        <tr>
            <th style="font-weight:normal;">NVIDIA Conformer-CTC (greedy)</th>
            <td class="num"><span class="metric">34.74</span><span class="metric-cer">13.37</span></td>
            <td class="num"><span class="metric">47.26</span><span class="metric-cer">22.54</span></td>
            <td class="num"><span class="metric">10.60</span><span class="metric-cer">3.05</span></td>
            <td class="num"><span class="metric">24.12</span><span class="metric-cer">5.63</span></td>
            <td class="num"><span class="metric">35.64</span><span class="metric-cer">11.02</span></td>
            <td class="num"><span class="metric">19.69</span><span class="metric-cer">7.46</span></td>
            <td class="num"><span class="metric">71.13</span><span class="metric-cer">30.50</span></td>
        </tr>
        <tr>
            <th style="font-weight:normal;">Gemma 4 E2B</th>
            <td class="num"><span class="metric">35.87</span><span class="metric-cer">15.34</span></td>
            <td class="num"><span class="metric">46.23</span><span class="metric-cer">23.47</span></td>
            <td class="num"><span class="metric">23.76</span><span class="metric-cer">9.13</span></td>
            <td class="num"><span class="metric">27.47</span><span class="metric-cer">8.99</span></td>
            <td class="num"><span class="metric">36.15</span><span class="metric-cer">13.93</span></td>
            <td class="num"><span class="metric">20.72</span><span class="metric-cer">10.15</span></td>
            <td class="num"><span class="metric">60.87</span><span class="metric-cer">26.35</span></td>
        </tr>
        <tr>
            <th style="font-weight:normal;">Whisper Large v3</th>
            <td class="num"><span class="metric">36.86</span><span class="metric-cer">17.21</span></td>
            <td class="num"><span class="metric">55.96</span><span class="metric-cer">34.62</span></td>
            <td class="num"><span class="metric">17.83</span><span class="metric-cer">5.74</span></td>
            <td class="num"><span class="metric">24.66</span><span class="metric-cer">7.24</span></td>
            <td class="num"><span class="metric">34.63</span><span class="metric-cer">12.89</span></td>
            <td class="num"><span class="metric">16.26</span><span class="metric-cer">7.74</span></td>
            <td class="num"><span class="metric">71.81</span><span class="metric-cer">35.04</span></td>
        </tr>
    </tbody>
</table>
</div>


Link to the live leaderboard: [Open Universal Arabic ASR Leaderboard](https://huggingface.co/spaces/elmresearchcenter/open_universal_arabic_asr_leaderboard).

</details>

## Resources

For more details and results:

* [Technical blog post](https://huggingface.co/blog/CohereLabs/cohere-transcribe-arabic-07-2026-release) contains WERs and other quality metrics.
* [Announcement blog post](https://cohere.com/blog/transcribe-arabic) for more information about the model.
* The [Open Universal Arabic ASR Leaderboard](https://huggingface.co/spaces/elmresearchcenter/open_universal_arabic_asr_leaderboard).


## Strengths and Limitations

### Strengths

Cohere Transcribe Arabic demonstrates strong transcription accuracy for Arabic and English. As a dedicated speech recognition model, it benefits from efficient inference via the Conformer encoder-decoder architecture.

### Limitations

* **Single language.** The model performs best when remaining in-distribution of a single, pre-specified language. It does not feature explicit, automatic language detection and exhibits inconsistent performance on code-switched audio.

* **Timestamps/Speaker diarization.** The model does not feature either of these.

* **Silence.** Like most AED speech models, Cohere Transcribe Arabic is eager to transcribe, even non-speech sounds. The model benefits from prepending a noise gate or VAD (voice activity detection) model in order to prevent low-volume, floor noise from turning into hallucinations.

## Model Card Contact
For errors or additional questions about details in this model card, contact [labs@cohere.com](mailto:labs@cohere.com) or raise an issue.


Terms of Use:
We hope that the release of this model will make community-based research efforts into Arabic speech more accessible. This model is governed by an Apache 2.0 license.


### Citation

To cite this model please use the following bibtex:

```bibtex
@misc{shaun_cassini_2026,
	author       = { Shaun Cassini and Sebastian Vincent and Xiaolu Lu and Julian Mack and Dhruti Joshi and Pierre Richemond },
	title        = { cohere-transcribe-arabic-07-2026 (Revision 0a8193c) },
	year         = 2026,
	url          = { https://huggingface.co/CohereLabs/cohere-transcribe-arabic-07-2026 },
	doi          = { 10.57967/hf/9549 },
	publisher    = { Hugging Face }
}
```
