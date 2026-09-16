---
title: "Fly Eagle(3) fly: Faster inference with vLLM & speculative decoding"
author: "Alexandre Marques"
site: "Red Hat Developer"
published: 2025-07-01T13:30:00+0000
source: "https://developers.redhat.com/articles/2025/07/01/fly-eagle3-fly-faster-inference-vllm-speculative-decoding#"
domain: "developers.redhat.com"
language: "en"
description: "Boost inference performance by up to 2.5X with vLLM's Eagle 3 speculative decoding integration. Discover how in this blog post."
word_count: 1887
---

Key insights

- vLLM now supports Eagle 3 for speculative decoding, boosting **inference performance** by up to **2.5X** across diverse scenarios.
- Speculative decoding performance is highly dependent on both request content and request rate, with the most significant gains in synchronous use cases.
- Only a few speculative models are currently available for shorter context lengths; however, more are coming soon!

Large language models (LLMs) generate tokens autoregressively: they run a forward pass, sample a token, append it to the input, and then repeat this process until completion. This causes high latency because each step waits for the prior token. Especially at low batch sizes, memory movement can take more time than the computation itself.

If we could parallelize the forward pass to generate multiple tokens simultaneously, we would perform roughly the same number of floating-point operations (FLOPs) per token while fully leveraging the available GPU compute, with roughly the same memory movement as a forward pass that only generates one token. However, simply parallelizing the token generation for a standard LLM will break the step-by-step dependencies, resulting in different predictions and lower accuracy.

## Speculative decoding: A solution for faster LLMs

This is where speculative decoding comes in! We use a smaller, “speculative” model to generate *k* draft tokens, and then use the original "verifier" model to check whether those tokens are correct. We probabilistically accept or reject tokens according to the algorithm in [Fast Inference from Transformers via Speculative Decoding](https://arxiv.org/abs/2211.17192), which guarantees that the generated tokens come from the same distribution as the original model. If the tokens we draft have a high probability of acceptance, we can achieve large speedups, especially if we can draft them at a low cost.

However, if the verifier does not accept the tokens, then we waste compute both drafting and verifying tokens that are not used. Therefore, we have a tradeoff between the number of tokens we can potentially generate in parallel and the likelihood that those tokens will be accepted. The optimal point along that tradeoff depends heavily on the specific use case.

[Eagle 3](https://github.com/SafeAILab/EAGLE) is the current state-of-the-art method for speculative decoding. It uses a single transformer layer to generate multiple draft tokens autoregressively based on the original model’s current state. Specifically, it reuses the feature outputs from specific layers of the original model and concatenates them with the embeddings to augment its generation. This allows it to accurately predict the verifier’s next tokens, even with a very small speculator. Because of this feature, however, Eagle speculators only work for the model that they were trained for.

## Eagle-3 with vLLM

Research implementations are generally very limited, so the [vLLM](https://github.com/vllm-project/vllm) community has been working hard to introduce both [Eagle 1](https://arxiv.org/pdf/2401.15077) and [Eagle 3](https://arxiv.org/pdf/2503.01840) into vLLM as of version 0.8.5. The newest version (0.9.1) supports CUDA graphs for Eagle 1+3 and provides speculative decoding metrics, including the draft acceptance rate, per-position acceptance rates, and the mean acceptance length (the average number of tokens generated per forward pass of the verifier model).

With the latest releases of vLLM, you can serve an Eagle 3 speculator for Llama 3.3 70B with the following command:

```python
VLLM_USE_V1=1 vllm serve meta-llama/Llama-3.3-70B-Instruct \
--seed 42 \
-tp 4 \
--speculative-config '{"model": "yuhuili/EAGLE3-LLaMA3.3-Instruct-70B", "num_speculative_tokens": 3, "method":"eagle3", "draft_tensor_parallel_size":1}'
```

You can interact with the server the exact same way as before, with a boost! As shown in Figure 1, incorporating Eagle 3 speculative decoding leads to significantly reduced end-to-end latency in text generation compared to a baseline model.

![Figure 1](assets/text_generation_example_-_speculative_decoding_vs_baseline_generation_example.png.webp)

Figure 1: A text generation example comparing a prompt run through a baseline model and the same model with Eagle 3 speculative decoding added showing faster end-to-end latency for Eagle 3.

## Real-world performance

Eagle can provide significant speedups in various scenarios. Let's examine several variables that can influence performance in a specific use case.

### Varying request rates

Some servers can have lower usage, meaning fewer requests per second, and prioritize the latency (the time it takes for a response) of the request, while others might be used more heavily with many requests per second and therefore require higher throughput. Speculative decoding is fundamentally a tradeoff—we spend a little bit of extra compute to reduce memory movement. At low request rates, we are memory-bound, so reducing memory movement can really help with latency. However, at higher throughputs or batch sizes, we are compute-bound, and speculative decoding can provide worse performance.

We utilize [GuideLLM](https://github.com/neuralmagic/guidellm/tree/main), a popular LLM evaluation toolkit, to benchmark two [Eagle models](https://huggingface.co/yuhuili) trained by the Eagle team: Llama 3.1 8B and Llama 3.3 70B, across a range of request rates for the [MT Bench dataset](https://huggingface.co/datasets/philschmid/mt-bench), which comprises a set of two-turn questions that emulate a chat environment, for example, asking the model to write a travel blog about a trip to Hawaii.

For this test, the 8B model is served on a single A100, and the 70B model is served on four A100s. Additionally, we limit the generation length to 1024 tokens for consistent testing. As shown in Figure 2, for a given request rate (x-axis), the latency of each request is reduced by up to 1.8X for the 8B model. The latency for each request of the 70B model is reduced by up to 1.6X at low request rates, but latency increases at higher request rates due to compute saturation.

![Figure 2](assets/spec_decode_mt_bench_1.png.webp)

Figure 2: Comparing requests per second vs. request latency with and without Eagle 3 speculative decoding, shown for Llama 3.1 8B (left) and Llama 3.3 70B (right), highlighting the tradeoffs for when speculative decoding helps and when it can hurt performance.

### Tailoring performance

The more accurately a speculative model can predict the next tokens, the greater the speedup. Eagle was primarily trained on chat data and tends to perform best on tasks that mimic its training data. Therefore, to ensure robustness, we evaluate the model on a variety of tasks from [SpecBench](https://github.com/hemingkx/Spec-Bench), a standardized benchmark suite for comparing speculative decoding methods. We specifically chose math reasoning, retrieval-augmented generation (RAG), translation, and added [HumanEval](https://huggingface.co/datasets/openai/openai_humaneval) as well to test coding use cases.

As shown in Figure 3, Eagle performs poorly on the German-to-English translation task. Conversely, it performs very well on tasks that are more similar to its training data, such as RAG and Math Reasoning, with up to 2.1X better latency, due to more accurate predictions for its next token. Eagle drafters could be trained specifically for specific datasets to improve their performance, such as the German-to-English translation task, by incorporating that data.

![Figure 3](assets/spec_decode_llama_3.3_70b.png.webp)

Figure 3: Comparing requests per second vs request latency with and without Eagle 3 speculative decoding for Llama 3.3 70B across various tasks including coding (upper left), math (upper right), retrieval augmented generation (lower left), and translation (lower right). The graphs highlight the impact training data has on inference performance.

### Tuning performance

The optimal draft length for a given situation can depend on both the request rate and the data being input. As shown above, we have a tradeoff between memory and compute. Creating a longer draft requires more compute, with the potential to accept a longer draft for each forward pass. Since the acceptance of a token in the draft is conditional on the acceptance of all of the prior tokens, the chances that a given token will be accepted decrease later in the draft. As noted earlier, we only get a speedup from drafting a token that matches the verifier’s.

At low request rates, it is often better to create a longer draft, since we have extra compute even if there is a low probability that the last few tokens will be accepted. At high request rates, though, it is optimal to reduce the draft length to avoid drafting tokens that have a lower probability of being accepted.

This optimal length is also heavily dependent on the specific task, since that determines the probability of acceptance of a given token. For example, Figure 4 shows that for the translation task, Eagle performs so poorly that the optimal draft length is 1, or even 0. RAG tokens, though, are easier for the Eagle speculator to predict, so even draft lengths of 5 tokens improve performance. So, it is important to measure performance with your specific scenario to determine the optimal draft length!

![Figure 4](assets/spec_decode_draft_length.png.webp)

Figure 4: Comparing requests per second vs request latency with and without Eagle 3 speculative decoding for Llama 3.3 70B across various draft lengths for translation (left) and Retrieval Augmented Generation (right) highlighting the impact both data and draft length have on performance.

### Decoding with trees

For the results above, we focused on *greedy decoding*, where we draft one sequence of tokens with the speculator. Many academic works (such as those in [1](https://arxiv.org/abs/2406.16858), [2](https://arxiv.org/abs/2408.15766), [3](https://arxiv.org/abs/2406.17276), [4](https://arxiv.org/abs/2505.12398)) have recently focused on tree decoding, though, which is a method that creates a tree of possible tokens (often 64) where there are multiple options for the first token, second token, etc. in the draft. Multiple branches of possible drafts are appended into a single input, and attention masking is used to ensure that each draft branch only "sees" the tokens from its branch. The best branch is selected using a single forward pass of the verifier model. This allows methods to increase the length of the accepted draft for a single forward pass.

However, this involves spending a lot of extra compute for relatively small gains in the acceptance length. For example, with "greedy" decoding, we can increase the mean acceptance length slightly by drafting 1 or 2 more tokens. With tree decoding, we might go from drafting and verifying 5 tokens to drafting and verifying 64 tokens, even though this may only increase the accepted length by 1 or 2 tokens. This can be worthwhile in theory with lots of extra compute; however, the tradeoff is not particularly favorable in most practical deployment cases.

We test this empirically using an engine that supports tree decoding using Eagle. At low request rates, specifically synchronous, tree decoding is the best option for reducing latency. Unfortunately, as request rates increase, it quickly becomes less efficient to validate so many extra tokens for a slight increase in accepted length, and tree decoding begins to significantly slow down the generation, as seen in Figure 5. For this reason, vLLM does not currently support tree decoding.

![Figure 5](assets/spec_decode_tree.png.webp)

Figure 5: Comparing requests per second vs request latency with different types of decoding including greedy and tree for Llama 3.1 8B highlighting that tree decoding quickly gives worse performance past synchronous use cases.

## Conclusion

Speculative decoding delivers impressive speedups in LLM inference, and vLLM’s Eagle 3 integration brings those gains to production-ready deployments, enabling faster and more efficient generation. However, today’s available speculative models come with limitations, such as a 2048 context length cap, and their performance can vary depending on the task and training data.

To maximize gains, it’s crucial to benchmark speculative models on your own workloads and consider fine-tuning them on your data to overcome performance gaps.

At Red Hat, we’re working to expand the ecosystem with more speculative models, longer context lengths, and production-grade tools that make speculative decoding easier and more powerful for enterprise use. Stay tuned for upcoming releases as we continue advancing the capabilities of fast, scalable AI!

**Ready to deploy faster, more scalable AI?** [Contact us to learn more about enterprise solutions](https://www.redhat.com/en/products/ai#products-ai-contact) or contribute to our open source journey today.
