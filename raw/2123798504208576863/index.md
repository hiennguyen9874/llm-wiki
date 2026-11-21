---
title: "Post by @himanshutwtxs on X"
author: "@himanshutwtxs"
site: "X (Twitter)"
published: 2026-11-20
source: "https://x.com/himanshutwtxs/status/2123798504208576863"
domain: "x.com"
language: "en"
description: "TLDR of this awesome read: 1> Most harnesses keep appending the whole history into one prompt, so the model has to cope with contexts it ne"
word_count: 142
---

TLDR of this awesome read:

1> Most harnesses keep appending the whole history into one prompt, so the model has to cope with contexts it never trained on

2> Harnesses like RLMs instead keep the context outside the prompt, write code over it, and hand smaller pieces to sub-calls. Each LLM call stays "locally in-distribution".

Trained only on short tasks, this generalized to tasks 2–64x longer and transferred to new domains with similar structure.

3> The cool trick is surrogate harness training. They train the orchestrator on cheap synthetic environments with fake tool calls and fake sub-agents instead of expensive real rollouts

4> The resulting RLM-27B beats base Qwen3.8-27B by 26.9% on average across 8 hard long-context benchmarks (58.5 vs 46.1), while using about 2x fewer tokens

take: models won't eat the harness, we just haven't explored what harnesses can do yet
