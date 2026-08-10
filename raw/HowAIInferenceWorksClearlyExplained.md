# Cedric Clyburn trên X: "How AI Inference Works, Clearly Explained" / X

Site: x.com
Link: https://x.com/cedricclyburn/status/2082105486804127885

Body:
How AI Inference Works, Clearly Explained

[7 N](https://x.com/cedricclyburn/status/2082105486804127885/analytics)

If you're using or building on LLMs, perhaps the most important concept to understand is how inference and KV Cache work. That's because no matter if you're working with coding agents, RAG, or fine-tuning, inference is what happens each time you make a request to a model and get a response back (and thus, where all the money goes)!

While training happens once, inference happens every single time a user sends a message. So, let's walk through:

- How it works
- What the KV cache is
- Optimizations that most teams use

## Inference is a stack, not a model file

[Hình ảnh](https://x.com/cedricclyburn/article/2082105486804127885/media/2081903456424525825)

A model sitting on your machine (or HuggingFace) doesn't serve anybody, yet. For inference to be possible, you need three pieces working together:

- The model weights: the file(s) with the billions of learned parameters: Kimi, GLM, Qwen, whatever you've picked.
- The inference server: software like vLLM that loads the model, manages incoming requests, and handles every optimization we're about to cover.
- The hardware accelerator: usually a GPU, doing the heavy numerical lifting.

You can skip the middle layer and run a model straight on a GPU with PyTorch. That works fine for a notebook or a single user. The moment you need to serve many people at once, the inference server is the piece that makes the GPU usable at production scale (think about you opening a .html locally vs. serving it using Apache httpd).

## Models generate one token at a time

GIF

LLMs don't produce a sentence. They produce one token at a time, and each new token depends on every token before it (including the ones the model just generated itself).

So, if we start with an example prompt: "The quick brown"

- The model predicts "fox" → that gets appended
- "The quick brown fox" → it predicts "jumps" → appended
- And so on, until the model emits a special end-of-sequence token.

That's autoregressive generation, and what people underestimate is that for every token in a response, it requires a full pass through the model. A 500-token answer means the model runs 500 times, and here you see how the computation demand can start to grow.

## Why the KV cache exists

[Hình ảnh](https://x.com/cedricclyburn/article/2082105486804127885/media/2081905796980318208)

Inside each of those passes, the tokens become embeddings (a numerical representation) to flow through a stack of transformer layers, and every layer has a self-attention block where tokens look at each other. That's where the memory problem starts.

Attention computes three vectors per token:

- Q, the query, what this token wants to know from the context.
- K, the key, the kind of information it holds.
- V, the value, its actual content.

To generate the next token, you compare its query against the key of every token so far and take a weighted sum of the values.

But! Here's what's really important: the query is only needed for the current token. The keys and values are needed for the entire history, but they don't change. Token 4's K and V are the same on step 5 as they were on step 4.

[Hình ảnh](https://x.com/cedricclyburn/article/2082105486804127885/media/2081913779311288320)

So rather than recompute them every step, we save them in GPU memory and only compute K and V for the new token. That's the KV cache, and it happens at every one of the model's N layers, so the savings multiply by N.

## Just how big does the KV Cache get?

Every token needs its keys and values stored at every layer, and with several parallel sets per layer (the KV heads). The formula is:

2 × num_layers × num_kv_heads × head_dim × dtype_bytes

So, let's take

[gpt-oss-120b](https://huggingface.co/openai/gpt-oss-120b)

: 36 layers, 8 KV heads, a head dimension of 64, 2 bytes per value. That's about 72 KB per token, but gpt-oss only holds the full history on half of its layers, so the number that actually grows on you is closer to 36 KB per token.

- 2k (a typical chat turn): ~75 MB
- 8k (standard production tier): ~300 MB
- 32k (a long document or codebase): ~1.2 GB
- 128k (gpt-oss's max): ~4.8 GB

And that's a model built to be cheap to serve. A dense 70B with 80 layers and a 128-head dimension (like Llama 3.3 70B) runs closer to 320 KB per token, which is 9× more for the same conversation. That's why model architecture choices are very important to controlling your AI bill.

## Which is where your GPU budget goes

[Hình ảnh](https://x.com/cedricclyburn/article/2082105486804127885/media/2081915839494651904)

Something like gpt-oss-120b fits on a single 80 GB H100. That was a big deal with its release, but after loading the weights on the card, you're only left with approximately 15–20 GB of headroom for KV cache. Serving real users now becomes tricky, for example:

- If your server reserves memory per request sized for the maximum context that request might reach, which is what older approaches did, every request costs you 4.8 GB whether it uses it or not. That's 3 concurrent users on an H100. Ooof.
- If instead you allocate what each request actually uses, a typical 8k request costs 300 MB. Same card, same model, 50 or 60 users. That's on the same hardware, but the difference is entirely how the GPU memory is managed, which is why this topic is so important.

## What production inference servers do about it

Well, three things, mainly:

- PagedAttention. Split the KV cache into small fixed-size blocks that can sit anywhere in memory, with a table tracking where each request's blocks live. Nothing is reserved for context you may never use. If you've worked with virtual memory in an OS, this will feel familiar, that's where the idea comes from.

GIF

- Continuous batching. Instead of waiting for a whole batch to finish together, finished requests leave, and new ones join as slots free up. The GPU stays fed.

[Hình ảnh](https://x.com/cedricclyburn/article/2082105486804127885/media/2081917241621131264)

- Prefix caching. When requests share a prefix (a system prompt, a retrieved document, the same repo file sitting in a coding agent's context), reuse the cached K and V instead of recomputing.

[Hình ảnh](https://x.com/cedricclyburn/article/2082105486804127885/media/2081917520273973252)

None of these change the model. They change how efficiently you run it.

## Then there's shrinking the model itself

[Quantization](https://huggingface.co/docs/optimum/en/concept_guides/quantization)

is a method to store weights (or activations) in lower precision. Most models ship at BF16, 16 bits per parameter. When you drop to FP8 or INT8 you've halved the memory. Go to 4-bit, and you're at a quarter.

gpt-oss-120b is a useful case because the work was already done for you. At 117B parameters in BF16, the weights would be roughly 234 GB and you'd need three 80 GB GPUs to load them. OpenAI post-trained the model with MXFP4 quantization on the MoE (mixture of experts) weights, and that's what brings it under 80 GB and onto a single card.

- BF16 (hypothetical): ~234 GB → three GPUs
- MXFP4, as shipped: fits one 80 GB GPU

[Hình ảnh](https://x.com/cedricclyburn/article/2082105486804127885/media/2081918136597479424)

Most models don't arrive that way, which is when you do it yourself, or head to

[@RedHat_AI](https://x.com/@RedHat_AI)

for our compressed models on HuggingFace. In the end, there are two big wins to quantizing. Quantized weights mean less data moving from HBM into SRAM every forward pass, which is a latency win. Quantized activations mean the tensor cores do the math in lower precision and get through more operations per second, which is a throughput win. Weight-only schemes like W8A16 get you the first; formats like W8A8 (Weight Int8 & Activations Int8) get you both.

[Hình ảnh](https://x.com/cedricclyburn/article/2082105486804127885/media/2081918377258319872)

In practice, FP8 halves your memory requirement and buys up to 1.6× throughput with minimal accuracy impact. And no, you're not making the model dumber. Calibrated techniques like GPTQ, AWQ, and SmoothQuant use a small representative dataset to work out which weights matter most and protect those, so the quality drop is typically under a point.

## The short version

| Technique | Where it applies | What you get |
| --- | --- | --- |
| PagedAttention | Runtime | More concurrent requests in the same memory |
| Continuous batching | Runtime | GPU stays busy between requests |
| Prefix caching | Runtime | Skips recompute on shared context |
| Quantization | Model, pre-deploy | Fewer GPUs, faster loading, faster math |
| Sparsification | Model, pre-deploy | Skips the weights that matter least |

Training is the one-time cost; inference is the recurring one, and it's most of the bill. Every token is a full forward pass. The KV cache is the thing that grows, with context length and with concurrent users, and managing it is the main job of your inference server. The distance between a naive deployment and a tuned one on the same H100 is roughly 3 concurrent users versus 50. Get inference right, and you get far more out of the hardware you already have.

## P.S. if you liked this!

If you want to run this yourself, I built a free course with

[DeepLearning.AI](https://deeplearning.ai/)

and Red Hat that goes hands-on: quantize a Qwen model with LLM Compressor and measure the accuracy tradeoff, serve it with vLLM, benchmark with GuideLLM, evaluate with lm-eval:

Images:
- [Image 1](https://pbs.twimg.com/media/HORoKcjXgAEZZr7?format=jpg&name=small)
- [Image 2](https://pbs.twimg.com/tweet_video_thumb/HORpUkOW0AAxxoy.jpg)
- [Image 3](https://pbs.twimg.com/media/HORqSrzWoAAb66w?format=jpg&name=small)
- [Image 4](https://pbs.twimg.com/media/HORxjUTXIAAuqBL?format=jpg&name=small)
- [Image 5](https://pbs.twimg.com/media/HORzbPFWgAA5Ds2?format=jpg&name=small)
- [Image 6](https://pbs.twimg.com/tweet_video_thumb/HOR0nJ2WMAAo5Lt.jpg)
- [Image 7](https://pbs.twimg.com/media/HOR0s2aWsAAnKQd?format=jpg&name=small)
- [Image 8](https://pbs.twimg.com/media/HOR09EeXoAQkIFT?format=jpg&name=small)
- [Image 9](https://pbs.twimg.com/media/HOR1g8dWAAAnzTr?format=jpg&name=small)
- [Image 10](https://pbs.twimg.com/media/HOR1u8_XAAADGwm?format=jpg&name=small)