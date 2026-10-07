---
license: apache-2.0
tags:
- text-to-speech
language:
- zh
- yue
- en
- ar
- cs
- da
- de
- nl
- es
- fr
- fi
- el
- he
- hi
- hu
- ja
- it
- ko
- mk
- ms
- ru
- fa
- pl
- pt
- sv
- ro
- sw
- tl
- th
- tr
- vi
---
# MOSS-TTS Family


<br>

<p align="center">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://speech-demo.oss-cn-shanghai.aliyuncs.com/moss_tts_demo/tts_readme_imgaes_demo/openmoss_x_mosi" height="50" align="middle" />
</p>



<div align="center">
  <a href="https://github.com/OpenMOSS/MOSS-TTS/tree/main"><img src="https://img.shields.io/badge/Project%20Page-GitHub-blue"></a>
  <a href="https://modelscope.cn/collections/OpenMOSS-Team/MOSS-TTS"><img src="https://img.shields.io/badge/ModelScope-Models-lightgrey?logo=modelscope&amp"></a>
  <a href="https://mosi.cn/#models"><img src="https://img.shields.io/badge/Blog-View-blue?logo=internet-explorer&amp"></a>
  <a href="https://arxiv.org/abs/2603.18090"><img src="https://img.shields.io/badge/Arxiv-2603.18090-red?logo=Arxiv&amp"></a>

  <a href="https://studio.mosi.cn"><img src="https://img.shields.io/badge/AIStudio-Try-green?logo=internet-explorer&amp"></a>
  <a href="https://studio.mosi.cn/docs/moss-tts"><img src="https://img.shields.io/badge/API-Docs-00A3FF?logo=fastapi&amp"></a>
  <a href="https://x.com/Open_MOSS"><img src="https://img.shields.io/badge/Twitter-Follow-black?logo=x&amp"></a>
  <a href="https://discord.gg/fvm5TaWjU3"><img src="https://img.shields.io/badge/Discord-Join-5865F2?logo=discord&amp"></a>
</div>


# MOSS-TTS-v1.5

**MOSS-TTS-v1.5** is continued from [MOSS-TTS 1.0](https://huggingface.co/OpenMOSS-Team/MOSS-TTS). It preserves the main 1.0 capabilities, including zero-shot voice cloning, long-form speech generation, token-level duration control, Pinyin/IPA pronunciation control, multilingual synthesis, and code-switching. For the full 1.0 feature walkthrough, input schema, decoding hyperparameters, and evaluation tables, please refer to the [MOSS-TTS 1.0 README](https://huggingface.co/OpenMOSS-Team/MOSS-TTS).

Compared with MOSS-TTS 1.0, v1.5 focuses on the following improvements:

- **Stronger multilingual synthesis with language tags**: when the `language` field is omitted, v1.5 may improve some languages and regress slightly on others compared with 1.0. When the language is specified, v1.5 is stronger than 1.0 on almost all supported languages. Set the tag when building the user message, for example `processor.build_user_message(text=text_fr, language="French")`.
- **More stable voice cloning**: v1.5 improves speaker similarity and reduces cloning variance, making repeated generations more consistent.
- **Better long-reference, short-text cloning**: v1.5 handles scenarios where the reference audio is much longer than the target text more reliably than 1.0.
- **More stable punctuation-following prosody**: v1.5 follows punctuation-driven pauses more closely, especially in long sentences.
- **Explicit pause control**: v1.5 supports inline pause markers such as `"[pause 3.2s]"`. For example, `我今天学习了一首中国的古诗，它的名字是[pause 3.2s]静夜思！` inserts an explicit 3.2s pause before `静夜思`.

## Supported Languages

MOSS-TTS-v1.5 currently supports **31 languages**. It keeps the 20 languages supported by [MOSS-TTS 1.0](https://huggingface.co/OpenMOSS-Team/MOSS-TTS) and extends multilingual continued training to additional languages including Cantonese, Dutch, Finnish, Hindi, Macedonian, Malay, Romanian, Swahili, Tagalog, Thai, and Vietnamese.

| Language | Code | Flag | Language | Code | Flag | Language | Code | Flag |
|---|---|---|---|---|---|---|---|---|
| Chinese | zh | 🇨🇳 | Cantonese | yue | 🇭🇰 | English | en | 🇺🇸 |
| Arabic | ar | 🇸🇦 | Czech | cs | 🇨🇿 | Danish | da | 🇩🇰 |
| Dutch | nl | 🇳🇱 | Finnish | fi | 🇫🇮 | French | fr | 🇫🇷 |
| German | de | 🇩🇪 | Greek | el | 🇬🇷 | Hebrew | he | 🇮🇱 |
| Hindi | hi | 🇮🇳 | Hungarian | hu | 🇭🇺 | Italian | it | 🇮🇹 |
| Japanese | ja | 🇯🇵 | Korean | ko | 🇰🇷 | Macedonian | mk | 🇲🇰 |
| Malay | ms | 🇲🇾 | Persian (Farsi) | fa | 🇮🇷 | Polish | pl | 🇵🇱 |
| Portuguese | pt | 🇵🇹 | Romanian | ro | 🇷🇴 | Russian | ru | 🇷🇺 |
| Spanish | es | 🇪🇸 | Swahili | sw | 🇹🇿 | Swedish | sv | 🇸🇪 |
| Tagalog | tl | 🇵🇭 | Thai | th | 🇹🇭 | Turkish | tr | 🇹🇷 |
| Vietnamese | vi | 🇻🇳 | | | | | | |


## Quick Start

### Environment Setup

We recommend a clean, isolated Python environment with **Transformers 5.0.0** to avoid dependency conflicts.

```bash
conda create -n moss-tts python=3.12 -y
conda activate moss-tts
```

Install all required dependencies:

```bash
git clone https://github.com/OpenMOSS/MOSS-TTS.git
cd MOSS-TTS
pip install --extra-index-url https://download.pytorch.org/whl/cu128 -e .
```

#### (Optional) Install FlashAttention 2

For better speed and lower GPU memory usage, you can install FlashAttention 2 if your hardware supports it.

```bash
pip install --extra-index-url https://download.pytorch.org/whl/cu128 -e ".[flash-attn]"
```

If your machine has limited RAM and many CPU cores, you can cap build parallelism:

```bash
MAX_JOBS=4 pip install --extra-index-url https://download.pytorch.org/whl/cu128 -e ".[flash-attn]"
```

Notes:
- Dependencies are managed in `pyproject.toml`, which currently pins `torch==2.9.1+cu128` and `torchaudio==2.9.1+cu128`.
- If FlashAttention 2 fails to build on your machine, you can skip it and use the default attention backend.
- FlashAttention 2 is only available on supported GPUs and is typically used with `torch.float16` or `torch.bfloat16`.


### Basic Usage

> Tip: MOSS-TTS-v1.5 uses the same generation API as the 1.0 **MossTTSDelay-8B** checkpoint. For multilingual inputs, set `language` whenever the language is known.

MOSS-TTS provides a convenient `generate` interface for rapid usage. The examples below cover:
1. Direct generation (Chinese / English / multilingual text with language tags / Pinyin / IPA)
2. Voice cloning
3. Duration control
4. Explicit pause control with `[pause X.Ys]`

```python
from pathlib import Path
import importlib.util
import torch
import torchaudio
from transformers import AutoModel, AutoProcessor
# Disable the broken cuDNN SDPA backend
torch.backends.cuda.enable_cudnn_sdp(False)
# Keep these enabled as fallbacks
torch.backends.cuda.enable_flash_sdp(True)
torch.backends.cuda.enable_mem_efficient_sdp(True)
torch.backends.cuda.enable_math_sdp(True)


pretrained_model_name_or_path = "OpenMOSS-Team/MOSS-TTS-v1.5"
device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.bfloat16 if device == "cuda" else torch.float32

def resolve_attn_implementation() -> str:
    # Prefer FlashAttention 2 when package + device conditions are met.
    if (
        device == "cuda"
        and importlib.util.find_spec("flash_attn") is not None
        and dtype in {torch.float16, torch.bfloat16}
    ):
        major, _ = torch.cuda.get_device_capability()
        if major >= 8:
            return "flash_attention_2"

    # CUDA fallback: use PyTorch SDPA kernels.
    if device == "cuda":
        return "sdpa"

    # CPU fallback.
    return "eager"


attn_implementation = resolve_attn_implementation()
print(f"[INFO] Using attn_implementation={attn_implementation}")

processor = AutoProcessor.from_pretrained(
    pretrained_model_name_or_path,
    trust_remote_code=True,
)
processor.audio_tokenizer = processor.audio_tokenizer.to(device)

text_1 = "亲爱的你，\n你好呀。\n\n今天，我想用最认真、最温柔的声音，对你说一些重要的话。\n这些话，像一颗小小的星星，希望能在你的心里慢慢发光。\n\n首先，我想祝你——\n每天都能平平安安、快快乐乐。\n\n希望你早上醒来的时候，\n窗外有光，屋子里很安静，\n你的心是轻轻的，没有着急，也没有害怕。\n\n希望你吃饭的时候胃口很好，\n走路的时候脚步稳稳，\n晚上睡觉的时候，能做一个又一个甜甜的梦。\n\n我希望你能一直保持好奇心。\n对世界充满问题，\n对天空、星星、花草、书本和故事感兴趣。\n当你问“为什么”的时候，\n希望总有人愿意认真地听你说话。\n\n我也希望你学会温柔。\n温柔地对待朋友，\n温柔地对待小动物，\n也温柔地对待自己。\n\n如果有一天你犯了错，\n请不要太快责怪自己，\n因为每一个认真成长的人，\n都会在路上慢慢学会更好的方法。\n\n愿你拥有勇气。\n当你站在陌生的地方时，\n当你第一次举手发言时，\n当你遇到困难、感到害怕的时候，\n希望你能轻轻地告诉自己：\n“我可以试一试。”\n\n就算没有一次成功，也没有关系。\n失败不是坏事，\n它只是告诉你，你正在努力。\n\n我希望你学会分享快乐。\n把开心的事情告诉别人，\n把笑声送给身边的人，\n因为快乐被分享的时候，\n会变得更大、更亮。\n\n如果有一天你感到难过，\n我希望你知道——\n难过并不丢脸，\n哭泣也不是软弱。\n\n愿你能找到一个安全的地方，\n慢慢把心里的话说出来，\n然后再一次抬起头，看见希望。\n\n我还希望你能拥有梦想。\n这个梦想也许很大，\n也许很小，\n也许现在还说不清楚。\n\n没关系。\n梦想会和你一起长大，\n在时间里慢慢变得清楚。\n\n最后，我想送你一个最最重要的祝福：\n\n愿你被世界温柔对待，\n也愿你成为一个温柔的人。\n\n愿你的每一天，\n都值得被记住，\n都值得被珍惜。\n\n亲爱的你，\n请记住，\n你是独一无二的，\n你已经很棒了，\n而你的未来，\n一定会慢慢变得闪闪发光。\n\n祝你健康、勇敢、幸福，\n祝你永远带着笑容向前走。"
text_2 = "We stand on the threshold of the AI era.\nArtificial intelligence is no longer just a concept in laboratories, but is entering every industry, every creative endeavor, and every decision. It has learned to see, hear, speak, and think, and is beginning to become an extension of human capabilities. AI is not about replacing humans, but about amplifying human creativity, making knowledge more equitable, more efficient, and allowing imagination to reach further. A new era, jointly shaped by humans and intelligent systems, has arrived."
text_3 = "nin2 hao3，qing3 wen4 nin2 lai2 zi4 na3 zuo4 cheng2 shi4？"
text_4 = "nin2 hao3，qing4 wen3 nin2 lai2 zi4 na4 zuo3 cheng4 shi3？"
text_5 = "您好，请问您来自哪 zuo4 cheng2 shi4？"
text_6 = "/həloʊ, meɪ aɪ æsk wɪtʃ sɪti juː ɑːr frʌm?/"
text_7 = "Bonjour, je voudrais essayer une voix française naturelle et stable."
text_8 = "我今天学习了一首中国的古诗，它的名字是[pause 3.2s]静夜思！"

# Use audio from ./assets/audio to avoid downloading from the cloud.
ref_audio_1 = "https://speech-demo.oss-cn-shanghai.aliyuncs.com/moss_tts_demo/tts_readme_demo/reference_zh.wav"
ref_audio_2 = "https://speech-demo.oss-cn-shanghai.aliyuncs.com/moss_tts_demo/tts_readme_demo/reference_en.m4a"

conversations = [
    # Direct TTS (no reference). Language tags are recommended in v1.5.
    [processor.build_user_message(text=text_1)],
    [processor.build_user_message(text=text_2)],
    # Direct TTS (no reference). For languages ​​other than Chinese and English, it is recommended to use language tags.
    [processor.build_user_message(text=text_7, language="French")],
    # Pinyin or IPA input
    [processor.build_user_message(text=text_3)],
    [processor.build_user_message(text=text_4)],
    [processor.build_user_message(text=text_5)],
    [processor.build_user_message(text=text_6)],
    # Explicit pause control. Use [pause X.Ys], such as [pause 3.2s].
    [processor.build_user_message(text=text_8)],
    # Voice cloning (with reference)
    [processor.build_user_message(text=text_1, reference=[ref_audio_1])],
    [processor.build_user_message(text=text_2, reference=[ref_audio_2])],
    # Duration control
    [processor.build_user_message(text=text_2, tokens=325)],
    [processor.build_user_message(text=text_2, tokens=600)],
]

model = AutoModel.from_pretrained(
    pretrained_model_name_or_path,
    trust_remote_code=True,
    # If FlashAttention 2 is installed, you can set attn_implementation="flash_attention_2"
    attn_implementation=attn_implementation,
    torch_dtype=dtype,
).to(device)
model.eval()

batch_size = 1

save_dir = Path("inference_root")
save_dir.mkdir(exist_ok=True, parents=True)
sample_idx = 0
with torch.no_grad():
    for start in range(0, len(conversations), batch_size):
        batch_conversations = conversations[start : start + batch_size]
        batch = processor(batch_conversations, mode="generation")
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)

        outputs = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=4096,
        )

        for message in processor.decode(outputs):
            audio = message.audio_codes_list[0]
            out_path = save_dir / f"sample{sample_idx}.wav"
            sample_idx += 1
            torchaudio.save(out_path, audio.unsqueeze(0), processor.model_config.sampling_rate)

```

## More Usage

MOSS-TTS-v1.5 is API-compatible with MOSS-TTS 1.0. For continuation with prefix audio, detailed `UserMessage` and `AssistantMessage` fields, generation hyperparameters, Pinyin/IPA preprocessing examples, and evaluation results, see the [MOSS-TTS 1.0 README](https://huggingface.co/OpenMOSS-Team/MOSS-TTS).
