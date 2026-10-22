# Best Embedding + Reranking Model [Visit](https://www.reddit.com/r/LocalLLaMA/comments/1vjk57h/best_embedding_reranking_model/)
### **Subreddit:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA)
### **Author:** [u/seamonn](https://www.reddit.com/user/u/seamonn/)
### **Vote:** 57
---
What Local Embedding + Reranking Models are you guys running for RAG?
I went down this rabbit hole because I wanted a Embedding Model + Reranker for a Translation Memory Server.
Essentially, given X phrase/word/sentence/paragraph in English, can it find a similar phrase/word/sentence/paragraph in the target language that's already translated. This is for 15 different languages - both western and eastern.
For this particular use case, [F2LLM V2:4b](https://huggingface.co/codefuse-ai/F2LLM-v2-4B) + [Zerank 2:4b](https://huggingface.co/zeroentropy/zerank-2-reranker) pretty much destroys anything else in the market. Here are my benchmarks:

Embed Model	Reranker Model	MRR	Re-Δ	R@20
BGE M3 0.6B	BGE M3 Reranker V2 0.6B	0.821	-1.60%	91.90%
BGE M3 0.6B	Qwen 3 Reranker 0.6B	0.776	-7.50%	91.90%
F2LLM 1.7B	Zerank 1 1.7B	0.871	-2.20%	96.80%
Qwen 3 Embed 4B	Qwen 3 Reranker 4B	0.739	11.00%	77.50%
Zembed 4B	Zerank 2 4B	0.664	25.80%	67.10%
F2LLM 4B	Zerank 2 4B	0.919	2.40%	98.40%
F2LLM 8B	Zerank 2 4B	0.922	1.60%	99.20%
PPLX Embed V1 4B	Zerank 2 4B	0.8825	10.10%	91.90%
Octen Embed 4B	Zerank 2 4B	0.853	12.40%	89.00%
Voyage 4 Large [API]	Voyage Rerank 2.5 [API]	0.889	8.50%	94.70%

Here, MRR = Mean Reciprocal Rank aka Final Score, Re-Δ = How much the Reranker helped and R@20 = was the correct translation in the retrieved 20 entries.
**Note**: All Local Models are running on Llama CPP at Q8_0 quant size.
Swapping the F2LLM V2:4b with [F2LLM V2:8b](https://huggingface.co/codefuse-ai/F2LLM-v2-8B) leads to slightly better results but honestly, not worth the latency tradeoff imo.
Even in other benchmarks, this combo ranks very high. I also found that base Qwen 3:4b Embedding and Reranker do quite well in benchmarks but tend to be mediocre in real world use cases (like this one). They are still pretty good though.
IMO, F2LLM V2:4b is SOTA and as good as it gets for Embedding Models. Kudos for a completely open model - License, Data, Code - everything. It tops a lot of benchmarks on the [MTEB Leaderboards](https://mteb-leaderboard.hf.space/benchmarks) as well.
There are not as many good open Rerankers but Zerank 2 is SOTA. It was under a non permissive license until very recently (16 days ago). [Notion acquired Zeroentropy](https://zeroentropy.dev/articles/zeroentropy-is-joining-notion) and they decided to open source this SOTA reranker. We owe this one to Notion lol.
---
## Comments 41

- by [unknown](#) **&#x21C5; 13**
  <br/> Accordin[g to the multilingual MTEB](https://mteb-leaderboard.hf.space/benchmark/MTEB(Multilingual%2C%20v2)?s.summary=meanTask&d.summary=desc) section, Qwen3-Embedding-4B beats F2LLM-v2-4B by a few points. When sorting purely [by retrieval](https://mteb-leaderboard.hf.space/benchmark/MTEB(Multilingual%2C%20v1)?s.summary=tt%3ARetrieval&d.summary=desc) the difference is even larger. Yet there is a large difference in your benchmark - maybe solely due to the Zerank combo? Have you tested that too?

Btw the HF page doesn't mention it, but Zerank 2 also [has instruction-following support](https://zeroentropy.dev/articles/prompting-best-practices-for-instruction-following-rerankers/).

- by [unknown](#) **&#x21C5; 4**
  <br/> I've been using Qwen3-Embedding-4B-Q4_K_M for big amounts of spoken utterances and it works far better than anything I tried. I feel like every couple points above some threshold on benchmarks mean a lot more than every previous couple points. I had very high requirements for embedding model and this one did it.

- by [unknown](#) **&#x21C5; 1**
  <br/> Try F2LLM

- by [unknown](#) **&#x21C5; 4**
  <br/> If you check the individual languages, F2LLM is actually ahead of everything.

Anyways, this was a common trend I found, Qwen 3 Embedding models usually win on benchmarks but score lower on bespoke use cases like mine.

And yes, Zerank 2 really blossomed once instruction-following was added. I believe Qwen Rerankers has that support as well.

Previously, it was like

"How are you?"<Translation 1><Translation 2>...

With the instruction:

Find the X Language Translation of "How are you?"<Translation 1><Translation 2>

Adding the instruction led to Zerank 2 pretty much destroy anything else.

- by [unknown](#) **&#x21C5; 3**
  <br/> I'm just using [gte-modernbert-base](https://huggingface.co/Alibaba-NLP/gte-modernbert-base). It's good enough, and it's much, much smaller than all the other ones, and it gets the job done very quickly. This is for me the ideal one because if I already run another model on the same card, I don't have much spare VRAM.

- by [unknown](#) **&#x21C5; 5**
  <br/> ATM Qwen 3 8B VL embeddeding and reranker are the best open models available, not a lot of improvements since that !

- by [unknown](#) **&#x21C5; 1**
  <br/> This is my stack and it works well. I run the embedding model and then I use bge m3 for reranking. Works great

- by [unknown](#) **&#x21C5; 4**
  <br/> I'm gonna give you a pro tip : don't go by reranking scores. Go by what you can run fast on your hardware, and if your domain is deals with a static set of vast, low-delta-change knowledge; fine-tune a cheap embedding model.

Retrieve + Rerank is GREAT but I believe most people don't understand how or when to use it. Most RAG cases are solvable by tuning your retriever + setting a context token limit instead of hard capping number of chunks to be in context; or having a really bad but extremely fast retriever + a significantly better reranker (doesn't need to be the best).

Y'all be really overestimating and adding complexity where there doesn't need to be any. Only if you can prove that just having a retriever or upgrading your retriever isn't fixing your problem should you add complexity to improve your fixed candidate set reranking. Ideally you should be focused on how much it costs you time wise (100-400ms should be the MOST it takes you to find relevant chunks given a query)

- by [unknown](#) **&#x21C5; 1**
  <br/> Go by what you can run fast on your hardware


    I feel the 4b runs plenty fast. With just on GPU, it's at the level of Voyage API.

And F2LLM for this use case is scoring near perfect so not worth finetuning something bespoke for this.

- by [unknown](#) **&#x21C5; 3**
  <br/> I'm just using the MxBAI large models on CPU

- by [unknown](#) **&#x21C5; 2**
  <br/> I tried that briefly - was very bad.

- by [unknown](#) **&#x21C5; 3**
  <br/> Trees wipe cooperative spoon continue grasshopper

This post was anonymized with [Redact](https://redact.dev)

- by [unknown](#) **&#x21C5; 1**
  <br/> I did some initial tests with 8b models but they were too similar to 4b ones -> Qwen 3 8b was almost exactly same as a Qwen 3 4b. Similarly, F2LLM 8b is similar to F2LLM 4b (shown in benchmark) and Octen 8b is similar to Octen 4b.

The added latency is not worth it.

- by [unknown](#) **&#x21C5; 1**
  <br/> that needs to be demonstrated in the same test with the same outputs. Not including that in your table makes me not have any faith in it. Qwen3 8B has been the best for a while and what I use

- by [unknown](#) **&#x21C5; 2**
  <br/> Fair enough.

It's just a PITA to run the full benchmark on the 8b models. I did test halfway but the results were too similar to the 4b ones if that makes sense.

It will take me a few days to benchmark the 8b models but I will likely not end up deploying one for Production, the 4b ones are 99.9% there.

- by [unknown](#) **&#x21C5; 1**
  <br/> Qwen3 8B has been the best for a while and what I use


    Also if you are already running the Qwen 3 8B, you should give F2LLM 8B a try, would love to see how it works on your setup.

- by [unknown](#) **&#x21C5; 1**
  <br/> I forget if it was unquantified or Q8 quant


    Just benchmarked BF16 and Q8_0 on F2LLM 4b + Zerank 4b. Scores are identical.

- by [unknown](#) **&#x21C5; 2**
  <br/> I didn't give mine much thought at the time, I just grabbed something that looked like it had alright benchmarks without comparing too much to other models.I'm running Qwen3-Embedding-0.6B-Q8_0 for embedding really fast and loose. Could maybe use some improvement, but I have to run it on a CPU for various convoluted reasons for now.My "reranking" model is actually the normal instruct Qwen3.5-4B-Q8_0 (on a GPU, though). I threw together a simple system prompt + user message feeding the model the documents, then the query and having the model do some reasoning about the similarities. It's a Qwen so it overthinks and second-guesses a lot, but it does the job.Instead of a proper score, I had it sort the documents into four buckets via a single tool call to avoid parsing headaches. "Highly applicable," where the document is relevant and agrees with the query, "Generally applicable," where the document is relevant but may disagree with the query, "Passingly applicable," where the document might only mention something relevant to the query, and finally "no applicability" where there's no relevance. Since the reranker is fast enough, I can progressively include more documents that have a decent embedding score until I get something highly applicable if the embeddings were bad.This is because all the rerankers I tried to use weren't really good, so I threw a fast+small reasoning model at it and it seems to work better. Maybe I'm doing something wrong or backwards. I'm definitely interested in hearing about better options.

- by [unknown](#) **&#x21C5; 2**
  <br/> We've been testing out the latest nvidia embedding models and they absolutely destroyed Qwen. Their v2 vl reranker was pretty good too.

- by [unknown](#) **&#x21C5; 1**
  <br/> Which Qwen please ?

- by [unknown](#) **&#x21C5; 1**
  <br/> I was using the 8b, both the 1b and 8b nemotron 3 embed models destroyed it in performance

- by [unknown](#) **&#x21C5; 1**
  <br/> Thanks for your answer ! Sadly Nemotron isn't multimodal :/

- by [unknown](#) **&#x21C5; 1**
  <br/> They have a v2 vl embed model that's still good and still better than qwen.

- by [unknown](#) **&#x21C5; 2**
  <br/> Have you also benched processing speed of llama.cpp versus just torch? I'm curious about how much faster it is.

- by [unknown](#) **&#x21C5; 2**
  <br/> It's already fast enough that I don't really feel the need to benchmark speed. It's almost as fast as Voyage API (Concurrency 1).

- by [unknown](#) **&#x21C5; 1**
  <br/> i see no mention of microsofts harrier-oss embedding models in this thread. does anyone have experience with these, the 270m and 0.6b variants?

- by [unknown](#) **&#x21C5; 0**
  <br/> They are in a weird spot - 0.6b and 270m are too small to seriously consider and 27b is too large to seriously consider lol.

- by [unknown](#) **&#x21C5; 1**
  <br/> would you say they are benchmaxxed? because the 0.6b is just under F2LLM V2 4b in multilingual. would you consider testing it to see

- by [unknown](#) **&#x21C5; 1**
  <br/> because the 0.6b is just under F2LLM V2 4b in multilingual


    heh you are right. It might actually be decent. TBH, it flew under the radar when I was considering my options.

Another issue is that I like to pair similar sized embedding model + reranker model.  The only decent option at 0.6 is the BGE M3 V2 Reranker which is fine but would have liked more options. Everything else is under a non permissive license. Qwen Reranker 0.6 is there but as you can see from the table, it's not good for this use case.

- by [unknown](#) **&#x21C5; 1**
  <br/> bge-m3 for both

- by [unknown](#) **&#x21C5; 1**
  <br/> how does zerank 2 compare to CoREB-Reranker? both are 4b. Mind testing it, or sharing repo for me to test?

- by [unknown](#) **&#x21C5; 1**
  <br/> Benchmark contains proprietary data so can't share publicly.

[CoREB-Reranker](https://huggingface.co/hq-bench/coreb-code-reranker) seems like a reranker finetuned for Code. Zerank 2 was finetuned for Search. Different domains.

- by [unknown](#) **&#x21C5; 1**
  <br/> Has it been used over english corpus only ? I wonder who is the winner at chinese/cantonese But great work thanks for this !

- by [unknown](#) **&#x21C5; 1**
  <br/> So basically the benchmark is:

  - Embed Corpus of translated Data.
  - Embed Query
  - Search
  - Rerank

F2LLM + Zerank 2 top the scores again for Simplified and Traditional Chinese


      
        
          
              Embed Model
            
              Reranker Model
            
              zh-Hans
            
              Re-Δ
            
              R@20
            
              zh-Hant
            
              Re-Δ
            
              R@20
            
        
        
      

      
        
            
                F2LLM 1.7B
              
                Zerank 1 1.7B
              
                0.932
              
                2.20%
              
                99.70%
              
                0.939
              
                1.40%
              
                99.70%
              
          
            
                F2LLM 4B
              
                Zerank 2 4B
              
                **0.961**
              
                5.80%
              
                **100.00%**
              
                **0.954**
              
                6.20%
              
                **100.00%**
              
          
            
                F2LLM 8B
              
                Zerank 2 4B
              
                0.957
              
                6.10%
              
                **100.00%**
              
                **0.954**
              
                4.60%
              
                **100.00%**
              
          
            
                Voyage 4 Large [Paid]
              
                Voyage Rerank 2.5 [Paid]
              
                0.936
              
                6.60%
              
                97.00%
              
                0.944
              
                3.80%
              
                98.90%
              
          
            
                Qwen 3 Embed 4B
              
                Qwen 3 Reranker 4B
              
                0.888
              
                14.40%
              
                94.50%
              
                0.872
              
                11.10%
              
                91.60%

- by [unknown](#) **&#x21C5; 0**
  <br/> For multilingual translation memory, bge-m3 is hard to beat — it handles 100+ languages with solid semantic fidelity and doubles as a sparse retriever. Pair it with bge-reranker-v2-m3 for reranking; the combo gives you dense + lexical coverage in a small enough footprint to run fully local.

- by [unknown](#) **&#x21C5; 1**
  <br/> It's the first one in the list
