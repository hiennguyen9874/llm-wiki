---
license: mit
base_model:
- Qwen/Qwen2.5-Omni-7B
pipeline_tag: visual-document-retrieval
library_name: sentence-transformers
tags:
- sentence-transformers
- multimodal
- feature-extraction
---
# Haon-Chen/e5-omni-7B

**e5-omni-7B** is a high-performance omni-modal embedding model built on top of [Qwen2.5-Omni-7B](https://huggingface.co/Qwen/Qwen2.5-Omni-7B).  
It produces a single, unified embedding space for text, images, audio, and video—making cross-modal retrieval accurate and easy to use across a wide range of applications. [Paper](https://arxiv.org/abs/2601.03666).


📝 Text   🖼️ Image   🎧 Audio   🎥 Video

## Experimental Results
Our model achieves strong performance on MMEB-V2 and AudioCaps benchmarks.
<img width="900" alt="abs" src="https://huggingface.co/Haon-Chen/e5-omni-7B/resolve/main/assets/e5-omni-mmeb.png">
<img width="400" alt="abs" src="https://huggingface.co/Haon-Chen/e5-omni-7B/resolve/main/assets/e5-omni-audiocaps.png">

## Usage

### Using Sentence Transformers

Install Sentence Transformers with the multimodal extras (for image, audio, and video support):

```bash
pip install "sentence_transformers[image,audio,video]" "transformers>=5.6.0"
```

```python
import torch
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "Haon-Chen/e5-omni-7B",
    model_kwargs={
        "torch_dtype": torch.bfloat16,
        "attn_implementation": "flash_attention_2",  # pip install kernels; recommended but not mandatory
    },
)

# For video on smaller GPUs, cap the processor up front:
model[0].processing_kwargs.update({
    "video": {"max_pixels": 64 * 28 * 28, "do_sample_frames": True, "fps": 1},
})
```

#### 🎬 Video Retrieval
```python
example_query = "How to cook Mapo Tofu?"
example_videos = [
    "https://huggingface.co/Haon-Chen/e5-omni-7B/resolve/main/assets/mapo_tofu.mp4",
    "https://huggingface.co/Haon-Chen/e5-omni-7B/resolve/main/assets/zhajiang_noodle.mp4",
]

query_embedding = model.encode_query(example_query)
document_embeddings = model.encode_document(example_videos, batch_size=1)
print(model.similarity(query_embedding, document_embeddings))
# Video similarities: tensor([[0.4156, 0.2783]])
```

#### 🎵 Audio Retrieval
```python
example_query = "A light piano piece"
example_audios = [
    "https://huggingface.co/Haon-Chen/e5-omni-7B/resolve/main/assets/joe_hisaishi_summer.mp3",
    "https://huggingface.co/Haon-Chen/e5-omni-7B/resolve/main/assets/jay_chou_superman_cant_fly.mp3",
]

query_embedding = model.encode_query(example_query)
document_embeddings = model.encode_document(example_audios, batch_size=1)
print(model.similarity(query_embedding, document_embeddings))
# Audio similarities: tensor([[0.2219, 0.1642]])
```

#### 📈 Image Document Retrieval (Image, Chart, PDF)
```python
example_query = "How many input modality does Qwen2.5-Omni support?"
example_images = [
    "https://huggingface.co/Haon-Chen/e5-omni-7B/resolve/main/assets/qwen2.5omni_hgf.png",
    "https://huggingface.co/Haon-Chen/e5-omni-7B/resolve/main/assets/llama4_hgf.png",
]

query_embedding = model.encode_query(example_query)
document_embeddings = model.encode_document(example_images, batch_size=1)
print(model.similarity(query_embedding, document_embeddings))
# Image similarities: tensor([[0.4351, 0.2442]])
```

#### 🌍 Multilingual Text Retrieval
```python
example_query = "氧气在空气中占比多少？"
example_texts = [
    "空气是指大气层中由不同气体和各类飘浮在其中的固体与液体颗粒（大气颗粒与气溶胶）所组成的气态混合物。地球大气层的空气主要由78.1%的氮气、20.9%氧气、0.9%的氩气和1~4%的水蒸气组成，其成分并不是固定的，随着高度、气压、温度的改变和对流情况不同，局部空气的组成比例也会改变。空气在大气层（特别是对流层）中的流动形成了风和曳流、气旋、龙卷等自然现象，而空气中飘浮的颗粒则形成了云、雾、霾和沙尘暴等短期天气情况。空气在海洋和陆地之间跨区域流动所承载的湿度和热能传导也是水循环和气候变率与变化的关键一环。",
    "水（化学式：H2O）是一种无机化合物，在常温且无杂质中是无色[1]无味不导电的透明液体，也会通过蒸发产生气态的水蒸气（这种蒸发可以发生在任何温度下，同时取决于与空气接触的表面积和湿度差）。在标准大气压下，水的凝固点是0 °C（32 °F；273 K），沸点是100 °C（212 °F；373 K）。",
]

query_embedding = model.encode_query(example_query)
document_embeddings = model.encode_document(example_texts, batch_size=1)
print(model.similarity(query_embedding, document_embeddings))
# Text similarities: tensor([[0.3219, 0.2156]])
```

#### 🧩 Multimodal Inputs

To embed a document that combines multiple modalities, pass a dict with any combination of `"text"`, `"image"`, `"audio"`, and `"video"` keys instead of a single path or string:

```python
documents = [
    {
        "text": "A cooking tutorial for Mapo Tofu",
        "video": "https://huggingface.co/Haon-Chen/e5-omni-7B/resolve/main/assets/mapo_tofu.mp4",
    },
    {
        "image": "https://huggingface.co/Haon-Chen/e5-omni-7B/resolve/main/assets/qwen2.5omni_hgf.png",
        "audio": "https://huggingface.co/Haon-Chen/e5-omni-7B/resolve/main/assets/joe_hisaishi_summer.mp3",
    },
]
document_embeddings = model.encode_document(documents, batch_size=1)
```

### Using Transformers

The examples below are adapted from [Tevatron](https://huggingface.co/Tevatron/OmniEmbed-v0.1).

```python
# Import Library, Load Model and Processor
import torch
from transformers import AutoProcessor, Qwen2_5OmniThinkerForConditionalGeneration
from qwen_omni_utils import process_mm_info

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-Omni-7B")
model = Qwen2_5OmniThinkerForConditionalGeneration.from_pretrained(
    "Haon-Chen/e5-omni-7B",
    attn_implementation="flash_attention_2",
    torch_dtype=torch.bfloat16
).to(device).eval()

processor.tokenizer.padding_side = "left"
model.padding_side = "left"

# Function to Encode Message
def encode_message(message):
    texts = processor.apply_chat_template(message, tokenize=False, add_generation_prompt=True)[0] + "<|endoftext|>"
    audio_inputs, image_inputs, video_inputs = process_mm_info(message, use_audio_in_video=True)

    inputs = processor(
        text=texts,
        audio=audio_inputs,
        images=image_inputs,
        videos=video_inputs,
        return_tensors="pt",
        padding="longest",
    )
    for k in inputs:
        inputs[k] = inputs[k].to(device)

    cache_position = torch.arange(0, inputs["input_ids"].shape[1], device=device)
    inputs = model.prepare_inputs_for_generation(**inputs, use_cache=True, cache_position=cache_position)
    model_outputs = model(**inputs, return_dict=True, output_hidden_states=True)

    last_hidden_state = model_outputs.hidden_states[-1]
    reps = last_hidden_state[:, -1]
    reps = torch.nn.functional.normalize(reps, p=2, dim=-1)
    return reps
```

#### 🎬 Video Retrieval
```python
example_query = "Query: How to cook Mapo Tofu?"
example_video_1 = "https://huggingface.co/Haon-Chen/e5-omni-7B/resolve/main/assets/mapo_tofu.mp4"
example_video_2 = "https://huggingface.co/Haon-Chen/e5-omni-7B/resolve/main/assets/zhajiang_noodle.mp4"
query = [{"role": "user", "content": [{"type": "text", "text": example_query}]}]
video_1 = [{"role": "user", "content": [{"type": "video", "video": example_video_1}]}]
video_2 = [{"role": "user", "content": [{"type": "video", "video": example_video_2}]}]

sim1 = torch.cosine_similarity(encode_message(query), encode_message(video_1))
sim2 = torch.cosine_similarity(encode_message(query), encode_message(video_2))

print("Similarities:", sim1.item(), sim2.item())
# Video similarities: 0.416015625 0.28515625
```

#### 🎵 Audio Retrieval
```python
example_query = "Query: A light piano piece"
example_audio_1 = "https://huggingface.co/Haon-Chen/e5-omni-7B/resolve/main/assets/joe_hisaishi_summer.mp3"
example_audio_2 = "https://huggingface.co/Haon-Chen/e5-omni-7B/resolve/main/assets/jay_chou_superman_cant_fly.mp3"
query = [{"role": "user", "content": [{"type": "text", "text": example_query}]}]
audio_1 = [{"role": "user", "content": [{"type": "audio", "audio": example_audio_1}]}]
audio_2 = [{"role": "user", "content": [{"type": "audio", "audio": example_audio_2}]}]

sim1 = torch.cosine_similarity(encode_message(query), encode_message(audio_1))
sim2 = torch.cosine_similarity(encode_message(query), encode_message(audio_2))

print("Similarities:", sim1.item(), sim2.item())
# Audio similarities: 0.2236328125 0.177734375
```

#### 📈 Image Document Retrieval (Image, Chart, PDF)
```python
example_query = "Query: How many input modality does Qwen2.5-Omni support?"
example_image_1 = "https://huggingface.co/Haon-Chen/e5-omni-7B/resolve/main/assets/qwen2.5omni_hgf.png"
example_image_2 = "https://huggingface.co/Haon-Chen/e5-omni-7B/resolve/main/assets/llama4_hgf.png"
query = [{"role": "user", "content": [{"type": "text", "text": example_query}]}]
image_1 = [{"role": "user", "content": [{"type": "image", "image": example_image_1}]}]
image_2 = [{"role": "user", "content": [{"type": "image", "image": example_image_2}]}]

sim1 = torch.cosine_similarity(encode_message(query), encode_message(image_1))
sim2 = torch.cosine_similarity(encode_message(query), encode_message(image_2))

print("Similarities:", sim1.item(), sim2.item())
# Image similarities: 0.43359375 0.244140625
```

#### 🌍 Multilingual Text Retrieval
```python
example_query = "Query: 氧气在空气中占比多少？"
example_text_1 = "空气是指大气层中由不同气体和各类飘浮在其中的固体与液体颗粒（大气颗粒与气溶胶）所组成的气态混合物。地球大气层的空气主要由78.1%的氮气、20.9%氧气、0.9%的氩气和1~4%的水蒸气组成，其成分并不是固定的，随着高度、气压、温度的改变和对流情况不同，局部空气的组成比例也会改变。空气在大气层（特别是对流层）中的流动形成了风和曳流、气旋、龙卷等自然现象，而空气中飘浮的颗粒则形成了云、雾、霾和沙尘暴等短期天气情况。空气在海洋和陆地之间跨区域流动所承载的湿度和热能传导也是水循环和气候变率与变化的关键一环。"
example_text_2 = "水（化学式：H2O）是一种无机化合物，在常温且无杂质中是无色[1]无味不导电的透明液体，也会通过蒸发产生气态的水蒸气（这种蒸发可以发生在任何温度下，同时取决于与空气接触的表面积和湿度差）。在标准大气压下，水的凝固点是0 °C（32 °F；273 K），沸点是100 °C（212 °F；373 K）。"
query = [{"role": "user", "content": [{"type": "text", "text": example_query}]}]
text_1 = [{"role": "user", "content": [{"type": "text", "text": example_text_1}]}]
text_2 = [{"role": "user", "content": [{"type": "text", "text": example_text_2}]}]

sim1 = torch.cosine_similarity(encode_message(query), encode_message(text_1))
sim2 = torch.cosine_similarity(encode_message(query), encode_message(text_2))

print("Similarities:", sim1.item(), sim2.item())
# Text similarities: 0.322265625 0.2158203125
```

## Citation
If you use this model in your research, please cite the associated paper.
```bibtex
@article{chen2026e5omni,
  title={e5-omni: Explicit Cross-modal Alignment for Omni-modal Embeddings},
  author={Chen, Haonan and Gao, Sicheng and Radu, Timofte and Tetsuya, Sakai and Dou, Zhicheng},
  journal={arXiv preprint arXiv:2601.03666},
  year={2026}
}
```

