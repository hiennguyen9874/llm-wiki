---
title: "Agent Loop vs Traditional RAG: 92.7% vs 78.9% on FRAMES"
site: "pipeshub.com"
published: 2026-10-01T00:00:00.000Z
source: "https://pipeshub.com/blog/agentic-rag-vs-traditional-rag-frames-benchmark"
domain: "pipeshub.com"
description: "Agent loops scored 92.7% vs 78.9% for the best of 18 RAG pipelines on Google’s 824-question FRAMES benchmark."
word_count: 8118
---

### ←

##### We tested 18 RAG pipelines against our agent loop on Google’s 824-question FRAMES benchmark. The agent loop scored 92.7% versus 78.9% for the best pipeline, with the advantage growing on harder multi-hop questions.

#### We tested 18 RAG pipelines against our agent loop on Google’s 824-question FRAMES benchmark. The agent loop scored 92.7% versus 78.9% for the best pipeline, with the advantage growing on harder multi-hop questions.

PipesHub is open source: [github.com/pipeshub-ai/pipeshub-ai](https://github.com/pipeshub-ai/pipeshub-ai)

## TL;DR: executive summary

Short on time? Here is what PipesHub is, what we measured, and why it matters.

- **What PipesHub is.** An open-source workplace AI platform. It connects to the tools a company already uses, such as Google Drive, Slack, Jira and Confluence, and answers questions over them, citing the exact passage behind every fact.
- **How it finds the right context.** PipesHub builds a context layer that combines a knowledge graph, filesystem-based pattern matching and hybrid search. It organizes company data into a permission-aware hierarchy that keeps each document’s relationships and access controls, so the AI agent gets relevant context and each user only sees what they are allowed to see.
- **How it answers.** With an agent loop: the model searches, reads what came back, then decides what to look up next. Multi-hop questions, where each step depends on the one before, need exactly this.
- **What we measured.** On Google’s FRAMES benchmark (824 multi-hop questions), PipesHub answered 92.7% correctly, against 78.9% for the best of 18 RAG pipelines we built, and matched a model handed the exact source articles (93.0%). On questions that need five or more documents, it scored 90% against 62%.
- **Answers you can check.** 84.0% of PipesHub’s answers were grounded in text it actually read (73.2% for the best pipeline), and every fact links to its source passage.
- **What it costs.** About $0.017 per question, against $0.006 for the best pipeline. Easy questions cost about the same and come back faster (8 s against 27 s); the extra spend goes to the hard, multi-hop questions. Caching the system prompt and tool definitions can reduce the agent loop’s cost by almost 50%.
- **Bottom line.** Any chat assistant built on company knowledge should run on an agent loop over a permission-aware context layer. PipesHub is open source, and the whole benchmark can be re-run from its repository.

## Introduction

Retrieval-augmented generation (RAG) is a way of answering questions with a language model by first searching a collection of documents for relevant passages, then giving those passages to the model as context. The model writes its answer from what was retrieved rather than from memory alone, so it can use private or up-to-date information and cite where each fact came from.

Most RAG demos answer questions like “What is our refund policy?” The answer sits in one document, and that document uses the same words as the question. Search finds it, the model reads it, done.

Real questions are often harder. “Which customers on the renewal list opened the most support tickets after the price change?” No single document answers that. You first need the renewal list, then the date of the price change, then the tickets for each customer. Each step uses what the step before found.

This kind of question is called *multi-hop*: you have to hop from one fact to the next to reach the answer. Standard RAG handles it badly, and the reason is simple. It searches **once**, before it knows what it is looking for.

Chat assistants make this unavoidable. A chat box is open-ended: people ask whatever they need, in their own words, and nobody shapes a question to suit a retriever. Some questions sit in one document. Many need several hops, a calculation, or knowledge of your products and your company. You can’t route those away in advance, so the assistant has to handle all of them. That is why we think every chatbot built on company knowledge should run on an agent loop, and this post shows the evidence.

This post explains, step by step:

1. Why multi-hop questions break a traditional RAG pipeline, using one real question worked through by hand.
2. The popular RAG techniques (hybrid search, reranking, query expansion, decomposition, small-to-big): what each one does, and where it stops helping.
3. How an agent loop works, and why letting the model search again after reading changes the result.
4. What we measured on Google’s FRAMES benchmark, 18 RAG pipelines against an agent loop, and what it costs in speed and money.

We assume you know basic RAG: split documents into chunks, turn them into vectors, find the closest ones, and give them to a language model. Everything beyond that is explained as we go.

## Key findings

- An agent loop (PipesHub) answered 92.7% of the 824 FRAMES questions correctly, 84.0% grounded in what it read. The best of 18 RAG pipelines we built answered 78.9% (73.2% grounded). The 624 held-out questions give the same picture: 92.3% against 78.7%.
- The gap grows with the number of hops: on questions that need five or more articles, the loop answered 90% and the best pipeline 62%.
- Small-to-big retrieval was the most useful pipeline technique, adding 5.5 points on top of query expansion. A small cross-encoder reranker lowered the hybrid + query expansion pipeline by about 9 points; a strong one recovered that, but added no significant gain.
- The loop costs more per question ($0.017 against $0.006 for the best pipeline), but questions that need one pass cost about the same and come back faster. Prompt caching served 47% of its input.
- Models drift towards answering from memory even when told not to. A one-line instruction halved how often it happened, and we checked every correct answer against the text the system read.

## A multi-hop question, worked through by hand

<video controls="" src="https://framerusercontent.com/assets/JeSRSvm9chgcgsonyF8hNaNybs.mp4"></video>

Here is a real question from the FRAMES benchmark:

> *“If my future wife has the same first name as the 15th first lady of the United States’ mother and her surname is the same as the second assassinated president’s mother’s maiden name, what is my future wife’s name?”*

The answer is **Jane Ballou**. Let’s find it the way a person would, one lookup at a time, and notice what each lookup needs.

**Hop 1. Who was the 15th first lady?** The 15th president was James Buchanan. He never married, so the role of first lady went to his niece, **Harriet Lane**. You learn this from the article about Buchanan.

**Hop 2. Who was Harriet Lane’s mother?** Her mother was **Jane** Ann Buchanan Lane. This fact is in the article about Harriet Lane.

Notice the order. You could not have searched for “Harriet Lane’s mother” at the start. The name Harriet Lane is not in the question. You only learned it in hop 1. The answer to hop 1 *becomes the search* for hop 2.

**Hop 3. Who was the second president to be assassinated?** Abraham Lincoln was the first, and **James Garfield** the second. You learn this from a list of presidents who died in office.

**Hop 4. What was Garfield’s mother’s maiden name?** Eliza **Ballou**. That fact is in the article about Garfield. Again, you could only ask this once hop 3 told you the name Garfield.

Put the two halves together: **Jane Ballou**.

*The four hops behind one FRAMES question*

Hops 1 and 3 can be searched from the question’s own words. Hops 2 and 4 cannot: each needs a name that only the hop above it reveals.

Now look at what the question gives a search engine to work with: “15th first lady”, “second assassinated president”, “mother”, “maiden name”. The two articles that hold the final facts are about Harriet Lane and James Garfield. Neither name appears anywhere in the question. A search that runs once, on the question’s words, is looking for documents it has no words for.

That is the whole problem in one example. The rest of this post is about the different ways to solve it.

## How a traditional RAG pipeline works

<video controls="" src="https://framerusercontent.com/assets/8AVZkCKbR8WIIOC2kjavNgoNkE.mp4"></video>

*A standard RAG pipeline has two stages that run once each:*

1. **Retrieve.** Turn the question into a vector, find the 50 chunks in the index whose vectors are closest, and paste them into a prompt.
2. **Generate.** Ask the model to answer the question from those chunks.

*A standard RAG pipeline*

Everything the model will ever see is chosen in step 1, from the question’s words alone. That is the one decision a pipeline makes: *what to read*. It makes it before reading anything.

Here is what that looked like for our question, from the benchmark run:

- The pipeline’s 50 chunks came from just 3 articles, and none of them was one of the 5 articles that hold the answer.
- The model saw Harriet Lane mentioned next to the 15th president, but nothing about her mother, and nothing about Garfield’s mother.
- It answered, correctly for what it had been given: *“cannot be determined from the provided sources.”*

For comparison, the same model with no documents at all answered from memory: *“Elizabeth Ballou”*. It remembered the wrong first lady. A confident wrong answer from memory is exactly what grounded RAG is meant to prevent; here it traded a wrong answer for no answer.

The retriever did its job: it found the text closest to the question’s words. The question’s words simply don’t point at the documents that matter.

## RAG techniques compared: hybrid search, reranking, query expansion, decomposition and small-to-big

<video controls="" src="https://framerusercontent.com/assets/J48rScjIrm5Cj5IGtA0uKay9zkw.mp4"></video>

People have built many improvements on top of the basic pipeline. Each one fixes a specific way retrieval misses. We’ll take them in the order they are usually added. For each: how it works, what it fixes, where it stops helping, and what it did on our question.

*Where each technique plugs into the pipeline*

### 1\. Dense vector search (the baseline)

**How it works.** An embedding model turns text into a vector that captures its meaning. Chunks whose vectors are close to the question’s vector are returned.

**What it fixes.** Wording. “Refund policy” finds a chunk titled “Returning a purchase”.

**Where it stops.** Names, numbers and rare terms get blurred. And it can only find text that *means* something similar to the question.

**On our question:** Dense search returned 50 chunks, but none of them came from the 5 articles needed to answer it.

### 2\. Keyword search (BM25)

**How it works.** Classic search: score chunks by how many of the question’s words they contain, giving more weight to rare words.

**What it fixes.** Exact names, product codes and IDs, which embeddings handle poorly.

**Where it stops.** It needs the right words. If the question says “second assassinated president” and the answer’s article says “Garfield”, keywords don’t help.

**On our question:** 1 of 5 articles, the list of presidents who died in office.

### 3\. Hybrid search (dense + BM25)

**How it works.** Run dense and keyword search side by side, then merge the two ranked lists. The usual merge is Reciprocal Rank Fusion (RRF): a chunk that ranks high in either list ends up high.

**What it fixes.** The blind spots of each method on its own. This is the sensible default for most systems.

**Where it stops.** Both searches still start from the question’s words.

**On our question:** 1 of 5 articles.

### 4\. Reranking with a cross-encoder

**How it works.** Retrieve more candidates than you need, say 100, then let a second model (a *cross-encoder*) read each candidate next to the question and score it. Keep the best 50.

**What it fixes.** Ordering. The right chunk was found but ranked 80th; the reranker moves it up.

**Where it stops.** It can only reorder what was retrieved. It can’t find what search missed.

**On our question:** 1 of 5 articles.

**On all 824 questions.** A small reranker lowered our hybrid + query expansion pipeline by almost nine points, and a strong one only recovered that loss, with no significant gain. The reranker insights below explain why.

### 5\. Query expansion

**How it works.** Before searching, ask the model to rewrite the question a few ways. Search with every version and merge the results.

**What it fixes.** Vocabulary mismatch: the document says “attrition” and the user says “churn”.

**Where it stops.** Rewriting the question doesn’t reveal new names. Every rewrite still asks about “the 15th first lady’s mother”, not “Harriet Lane’s mother”.

**On our question:** 1–2 of 5 articles, depending on the variant.

### 6\. Query decomposition

**How it works.** Ask the model to split the question into simpler sub-questions, search for each, and combine the results.

**What it fixes.** Questions with several parts that can each be searched.

**Where it stops.** All sub-questions are written *before any search runs*. If a sub-question needs an earlier answer, the model has to guess it from memory. In our run, the model wrote “What was the maiden name of the mother of James A. Garfield?” It guessed Garfield correctly from memory, but that is a guess, not retrieval. For the first lady it could not guess the name, so it wrote a vague sub-question that missed.

**On our question:** 1–2 of 5 articles, depending on the variant.

### 7\. Small-to-big retrieval

**How it works.** Search over small chunks, which match precisely, then hand the model the full articles the best chunks came from.

**What it fixes.** A fact split across neighbouring chunks: the model gets the whole article around a good match.

**Where it stops.** It’s only as good as the articles chosen. If the top matches come from the wrong articles, the model gets whole wrong articles.

**On our question:** 1–2 of 5 articles.

**On all 824 questions.** Adding small-to-big to the best pipeline (hybrid search with query expansion) raised it from 73.4% to 78.9%: 79 questions gained, 33 lost. It found no more of the right articles; the gain came from reading the whole of the articles it had already found, where the linking fact often sat outside the retrieved chunks. It roughly triples the cost per question ($0.0056 against $0.0019) and adds about ten seconds. PipesHub’s tool for reading a whole record does the same job, except that the model chooses which records to read instead of always taking the top three.

### 8\. Chunking strategy: fixed windows or document structure

**How it works.** Either split text into fixed windows (say 512 tokens, overlapping by 64), or split along the document’s structure: paragraphs, list items, table rows.

**What it fixes.** Structure-aware chunks keep a table row or a list item whole. Fixed windows give every hit the same amount of surrounding text.

**Where it stops.** Chunking decides *what* can be found, not *what to look for next*.

**On our question:** with plain dense search, 0 of 5 articles on structural chunks and 1 of 5 on fixed windows.

We ran all 18 RAG variants on this question. None of them answered it. The best found 2 of the 5 articles needed, and every one of them correctly said the sources were not enough.

## Why every RAG technique hits the same ceiling

Every technique above improves *how well* the pipeline makes its one decision. None of them lets it make a *second* decision after reading.

That is the ceiling. For our question, the fact that unlocks hop 2 (the name Harriet Lane) sits inside a document the pipeline retrieves. But by the time the model reads it, retrieval is over. There is no step where the model can say: “Now I know who she is. Let me look up her mother.”

Decomposition comes closest, because it plans several searches. But it writes all of them up front, so it can only plan hops whose names it can guess. When it can’t guess, the plan has a hole.

To fill that hole, the system has to be able to search, read what came back, and then decide what to search for next. That is what an agent loop does.

## Agentic RAG: how an agent loop works

<video controls="" src="https://framerusercontent.com/assets/Ol54SKRB1tRfULS7lp2DYjYjxWw.mp4"></video>

An agent loop gives the model search as a *tool* it can call as many times as it needs, instead of handing it one fixed set of chunks. The loop is simple:

1. The model reads what it has so far.
2. It decides: answer now, or call a tool (search again with a new query, read a whole document, look something up).
3. The tool’s result is added to what it has, and the loop goes back to step 1.

The important change is *when* the retrieval decision is made. In a pipeline it is made once, before reading. In a loop it is made after every read, so each new search can use what the last one found.

**The loop does the work of the RAG techniques above, only when a question needs it.** Splitting a question into hops is decomposition. Writing a new search after a miss is query expansion. Reading a whole document when a snippet falls short is small-to-big. A pipeline runs each of these as a fixed stage on every question. A loop uses them on demand, and you steer when through its prompt instead of building a new stage. It also makes a reranker matter less: the model judges what it has read, and searches again if it isn’t enough.

*RAG pipeline vs agent loop · where the retrieval decision is made*

### The multi-hop question, turn by turn

Here is what PipesHub’s agent loop did with our question in the final benchmark run. It took three model calls and 67 seconds.

**Before the first turn.** PipesHub runs one search on the question itself, so easy questions can be answered straight away. Here it returned the list of first ladies of the United States and the list of presidents who died in office.

**Turn 1.** From the list, the model learns that the 15th first lady was Harriet Lane, Buchanan’s niece. It reads the full list for her details, stating its reason: *“Need Harriet Lane’s biographical and family details, specifically her mother’s first name.”*

**Turn 2.** It now writes two searches the original question could never have produced, and runs them together: *“Harriet Lane mother first name”* and *“James A. Garfield mother maiden name second assassinated president”*. The first returns Harriet Lane’s article, which names her mother, Jane Ann Buchanan Lane. The second returns Garfield’s: his mother Eliza was a Ballou.

**Turn 3.** The model has every fact it needs, so it answers: **Jane Ballou**. It cites the three passages it used: Harriet Lane’s mother, Garfield being the second assassinated president, and his mother’s maiden name.

Both names in those searches came from what the model had just read: Harriet Lane from the list of first ladies, Garfield from the list of presidents who died in office. The best pipeline we built found Harriet Lane and Ballou too, but never Lane’s mother, so it said the name could not be determined. At grading time, we check every correct answer against the text the system actually read (more on this below).

### Why an agent loop beats a RAG pipeline on multi-hop questions

- **Each search can use new information.** Hop 2 is possible because turn 1 read a document first.
- **The model can see what’s missing.** It noticed that the search excerpt lacked Harriet Lane’s family details and read the full list for them. A pipeline has no way to notice a gap.
- **Easy questions stay cheap.** If the first search already contains the answer, the loop stops after one call, just like a pipeline.

The FRAMES paper found the same pattern with its own baselines. A strong model answering from memory scored 0.40. A multi-step retrieval pipeline, which searches again based on what it found, reached 0.66 ([Krishna et al., 2024](https://arxiv.org/abs/2409.12941)).

Google Research reported the same direction more recently. Their agentic RAG system on the Gemini Enterprise Agent Platform plans its searches, checks whether the evidence is enough, and searches again when it isn’t. It answered 90.1% of the 824 FRAMES questions correctly, even when it first had to pick the right document collection out of four. They also report that, compared with standard RAG, their approach raises accuracy on factuality datasets by up to 34% ([Google Research, June 2026](https://research.google/blog/unlocking-dependable-responses-with-gemini-enterprise-agent-platforms-agentic-rag/)).

## How PipesHub builds an agent loop for enterprise search

<video controls="" src="https://framerusercontent.com/assets/zYHQjMK1dX6TD5zwmLbc24qxs.mp4"></video>

PipesHub is an open-source workplace AI platform. It connects to the tools a company already uses, such as Google Drive, Slack, Jira and Confluence, and answers questions over them. Underneath, it builds a **context layer** that combines three ways of finding information: a knowledge graph of the company’s people, projects, products and topics; filesystem-based pattern matching, which lets the agent find records by name, path and folder the way a person browses a drive; and hybrid search, which mixes semantic and keyword retrieval.

The context layer organizes enterprise data into a **permission-aware hierarchy**. Each record keeps its place in its source (the drive and folder, the Slack channel and thread, the Jira project, the Confluence space), its links to related records, and the access controls it had at the source. Because relationships survive indexing, the agent can follow a ticket to its project, its owner and the documents that mention it. Because permissions survive too, every lookup is filtered to what the asking user is allowed to see. The agent gets context that is relevant, connected and safe to show. In its enterprise-search mode, every answer comes from an agent loop over this context layer.

You can read the agent loop, the tools and the prompts yourself in the [open-source repository](https://github.com/pipeshub-ai/pipeshub-ai).

**An assistant has to understand your company, not just your documents.** People ask about your products, customers, projects and colleagues, in your own vocabulary. PipesHub indexes those too: connectors bring documents in with their permissions, and an entity layer, a knowledge graph of people, projects, products and topics, lets the model find what a document is about, not only what it says. Because the loop works through tools, it has room to grow: memory that keeps what a user or team has told it, and a richer knowledge graph, arrive as new tools for the same loop rather than new pipelines.

The system has three layers:

1. **Connectors** bring documents in, with their permissions, from each source.
2. **Indexing** splits each document into blocks (paragraphs, list items, table rows), embeds them for search, and records who can see what.
3. **The agent loop** answers questions. The model works through a small set of tools, and every search is filtered to what the asking user is allowed to see.

*PipesHub architecture*

### The tools are deliberately few

| **Tool** | **What it does** |
| --- | --- |
| Search | Hybrid dense + keyword search, results ranked by relevance |
| Fetch record | Reads a whole document, or the next part of a long one |
| Lookup | Finds a document by name or ID |
| Entities | Finds people, projects and topics, and the documents linked to them |
| Calculator | Exact arithmetic and date differences on values it has read |

The loop was easy to build. Making it reliable was the hard part, and these choices mattered most:

- **Cite every fact to its exact passage.** Every block the model sees carries a short label, and the model cites the labels it used. PipesHub turns each citation into a link that opens the source document at that exact paragraph or table row, so a reader can check every hop. In our example, each of the three facts links to the passage it came from. This costs a few more tokens: the labels add input, and the links roughly double the length of an answer.
- **Search once before the first turn.** Many questions are answered by the first search, so they cost one model call.
- **Show each result once, ranked.** Results come most relevant first, and a block the model has already seen isn’t sent again. This saves tokens on every turn.
- **Share the reading budget fairly.** When the model reads several documents at once, each gets a fair share of the space, so none comes back empty.
- **Tell the model where it stands.** Every tool result ends with a short footer: step 3 of 15. Near the limit, it adds a note to wrap up and say what couldn’t be confirmed.
- **Keep the prompt focused.** In search mode, PipesHub removes the tools a general assistant needs but search doesn’t, such as file generation, image generation, code execution and web search. That cut the system prompt from about 4,600 to about 3,200 tokens, and the tool list from 35 to 14.
- **Use exact tools for exact work.** Adding up years or counting days is done with a calculator, not in the model’s head.

## How we benchmarked RAG on FRAMES

One example proves nothing. To compare approaches properly, we ran every technique above, and PipesHub, on all 824 FRAMES questions. Comparisons like this are easy to get wrong, so here is what we held fixed.

### The same inputs for everyone

- The same answering model for every system: gpt-5.6-luna, at high reasoning effort.
- The same embedding model: text-embedding-3-small.
- The same documents: 12,441 Wikipedia articles, each frozen at its version of 15 October 2024. That is the 2,517 articles the questions need, plus about 10,000 related but unneeded articles as distractors.
- The same price table for cost, with every model call counted, including the calls a pipeline makes to rewrite or split the question.

### Two reference points

- *Closed book*: the model answers with no documents at all. This shows how much can be answered from memory.
- *Oracle*: the model is handed the exact articles each question needs. This is the best this model can do.

**Answers must come from the documents.** Every system is told to answer only from what it retrieved, and to say what is missing. Then, when grading, we check each correct answer against the exact text that system was shown. Models drift towards answering from memory, so we both ask and check. PipesHub ran with one setting any admin can add in its Custom Instructions: “Do not answer questions from your training memory.” A correct answer whose facts weren’t in that text is flagged as *memory-suspect*.

**Each system runs as it is built, and pays for it.** The RAG pipelines use a short answer prompt, about 150 words plus the retrieved sources.

PipesHub’s prompt is longer because PipesHub is a workplace assistant, not only a retrieval step. Even in its search mode, which strips out what search doesn’t need, the prompt carries the definitions of its tools, the citation rules that link every fact to its passage, and rules for multi-step questions. Its smallest first call was about 7,400 input tokens. We didn’t shorten PipesHub’s prompt or pad the pipelines’ prompts to match, because each prompt is part of the method being tested. Every token is counted in cost, and most of the fixed part is served from the provider’s prompt cache (see the cost section).

**Grading.** Two different models grade each answer independently: Claude Sonnet 5, using the grading prompt from the FRAMES paper word for word, and Gemini 3.8 Flash. We report how often they agree.

**Every system answers every question.** Failed calls are retried. The one failure retries can’t fix is the provider’s content filter refusing a question because of the text a system retrieved. We re-asked those questions through a second endpoint for the same model, so every system answered every question (details below the results table).

**Splits.** Questions are split 200 dev / 624 held-out, stratified by reasoning type. Every fix to PipesHub was developed and measured on the dev questions only; the held-out 624 were never looked at. We report all 824, and the held-out subset on its own, because no fix could have been tuned to it.

Everything is pinned by hash and can be re-run on one machine; the steps are in the repository’s REPRODUCE.md.

## FRAMES benchmark results: agent loop vs RAG pipelines

*Every number below comes from the final runs on all 824 questions, combined into one board. No number comes from an earlier or smaller run.*

**Headline.** On all 824 questions, PipesHub’s agent loop answered 92.7% correctly (95% confidence interval 90.9–94.4%), and 84.0% were *grounded*: correct, with the key facts in the text it read. The best RAG pipeline we could build (hybrid search, query expansion and small-to-big) answered 78.9%, 73.2% grounded. The model from memory alone answered 64.9%. The model handed the exact articles (the oracle) answered 93.0%, 90.0% grounded. On the 624 held-out questions, which no PipesHub change was tuned on, the numbers barely move: PipesHub 92.3% (84.5% grounded), the best pipeline 78.7% (73.2%).

| **System** | **Accuracy** | **Grounded accuracy** | **Latency, median / 95th pct** | **Mean cost per question** | **Mean cost per correct answer** |
| --- | --- | --- | --- | --- | --- |
| Closed book (memory only) | 64.9% | — | 7 s / 95 s | $0.0030 | $0.0047 |
| Naive RAG (dense, top 50) | 36.3% | 27.7% | 7 s / 18 s | $0.0014 | $0.0039 |
| Hybrid search | 43.3% | 36.8% | 8 s / 18 s | $0.0018 | $0.0040 |
| Hybrid + reranker | 46.2% | 39.7% | 9 s / 21 s | $0.0019 | $0.0040 |
| Hybrid + query expansion | 73.4% | 67.5% | 17 s / 25 s | $0.0019 | $0.0026 |
| Hybrid + expansion + reranker | 64.7% | 56.8% | 33 s / 109 s | $0.0020 | $0.0030 |
| Hybrid + expansion + small-to-big (best pipeline) | 78.9% | 73.2% | 27 s / 54 s | $0.0056 | $0.0071 |
| PipesHub agent loop \* | 92.7% | 84.0% | 22 s / 134 s | $0.0167 | $0.0180 |
| Oracle (exact articles given) | 93.0% | 90.0% | 3 s / 6 s | $0.0049 | $0.0053 |

\*Higher token usage, primarily because the loop does much more than standard RAG. Token costs can be reduced by caching prompts and tool definitions

**What is held equal, and what is not.** Every row uses the same model (gpt-5.6-luna), the same 824 questions, the same Wikipedia articles and the same graders. The prompt and tools differ. Each pipeline gets a short answer prompt (about 150 words) and no tools. PipesHub gets its search-mode prompt, with tool definitions, citation rules and multi-step rules (about 7,400 tokens on its first call), plus tools to search, read whole records and calculate. So the PipesHub row measures the whole product against the pipelines, not the loop alone. Its larger prompt and extra turns also explain most of its higher cost per question.

*Grounded accuracy* counts only correct answers whose facts were in the text the system was shown. The full board, with all 18 RAG variants and 95% confidence intervals, is in the repository. Latency was measured on one laptop that was running other benchmark jobs at the same time, so read it as a comparison, not as what you would see in production. Azure’s content filter refused 38 pipeline answers because of text they had retrieved. We re-asked them through OpenAI’s endpoint for the same model, which refused none, so every system answered all 824 questions.

**Other published results on FRAMES.** Google Research’s agentic RAG reported 90.1% on all 824 questions ([source](https://research.google/blog/unlocking-dependable-responses-with-gemini-enterprise-agent-platforms-agentic-rag/)). It is a useful reference point, but not directly comparable to the table above, because the conditions differ:

- **Model:** Gemini (version not stated), against gpt-5.6-luna for every system here.
- **Documents:** a corpus of 2,676 PDFs, searched alongside three distracting collections, against 12,441 Wikipedia articles here, about 10,000 of them distractors linked from the answer articles.
- **Grading:** an LLM judge whose prompt isn’t published, against the FRAMES paper’s own grading prompt here.

What the two results share is the pattern: systems that search again after reading score far above single-shot retrieval on these questions.

<video controls="" src="https://framerusercontent.com/assets/YxFRInP64AP6aqJXZUFHrTrzLw.mp4"></video>

*Final runs, all 824 questions · results/2026-09-full board · cost from one pinned price table*

<video controls="" src="https://framerusercontent.com/assets/m1m44GRsYRn9zACBCHp1qhisUzs.mp4"></video>

*Final runs, all 824 questions, grouped by the number of gold articles in FRAMES*

### What the numbers show

- **The gap grows with the number of hops.** On questions built from two articles, the best pipeline answered 87% and PipesHub 93%. On questions built from five or more, the pipeline fell to 62%; PipesHub held 90%.
- **Most of it is finding the linking facts.** PipesHub’s model saw every article a question needs on 84% of questions, the best pipeline’s on 75%. When an article was missing, PipesHub usually found the same facts elsewhere in the collection, in list pages and related articles: 76% of those answers were still grounded, against 34% for the pipeline.
- **PipesHub matches the oracle on accuracy; the oracle stays ahead on grounding.** Against the oracle from the same run, each was right on about 30 questions the other missed. On grounded accuracy the oracle is about five points ahead.
- **Models drift towards memory, and a one-line instruction halves it.** We read every flagged answer by hand. With the custom instruction, PipesHub filled one linking fact from memory in 6 correct answers (0.8%), the same rate as the best pipeline (5, 0.8%); the oracle did so twice. Without the instruction, in an otherwise identical run, it was 13 (1.7%), at the same 92.7% accuracy. A citation shows where some of an answer came from, not all of it: each of those answers cited sources for its other facts. That is why we lead with grounded accuracy and check it at grading time.
- **The ranking does not depend on the judge.** Under a strict grader that rejects hedged or multi-candidate answers, PipesHub scores 91.6% and the best pipeline 78.0%.

## Reranker insights: when a cross-encoder reranker helps and when it hurts

A reranker is one of the most recommended RAG upgrades, so we tested it carefully. We ran a small cross-encoder (ms-marco-MiniLM-L-6-v2, 22 million parameters, the one PipesHub ships) on six pipelines, and a strong one (BAAI/bge-reranker-v2-m3, 568 million parameters) on the best pipeline without small-to-big. Each reranker scored the top 100 candidates and kept 50.

| **Pipeline** | **No reranker** | **\+ small reranker** | **\+ strong reranker** |
| --- | --- | --- | --- |
| Hybrid search | 43.3% | 46.2% | — |
| Hybrid + query expansion | 73.4% | 64.7% | 74.8% |
| Hybrid + decomposition | 57.8% | 55.1% | 75.5% |

- **A weak reranker can make a good pipeline worse.** The small reranker helped plain hybrid search a little (+2.9 points), but cost hybrid + expansion 8.7 points: 122 questions lost, 50 gained. The same articles were retrieved; what changed was which passages reached the model. The reranker scores every candidate against the original question, and the passage holding a linking fact rarely looks like the question. Query expansion had found that passage with a rephrased query, and the reranker dropped it. The model then said “I don’t know” far more often: 241 times against 161.
- **A strong reranker recovers the loss, and adds little more.** The 568M model scored 75.5%, about eleven points above the small one and 2.1 points above no reranker. That last gain is not statistically significant (67 questions gained, 50 lost).
- **It is an expensive way to gain a point.** On our laptop’s GPU it added about two minutes per question, so in production it needs GPU serving. Small-to-big added 5.5 points to the same pipeline for about a third of a cent per question.
- **An agent loop needs it least.** A reranker re-sorts one fixed pool of results. A loop judges what it has read and searches again when something is missing, which is the problem a reranker tries to solve.

If you add a reranker, measure it on your own multi-hop questions, choose a strong model, and consider scoring candidates against each expanded query, not only the original question.

## Cost and latency of agentic RAG

An agent loop is not free. It is worth being clear about what it costs.

**A loop spends only what each question needs.** A pipeline does the same work for every question. Our strongest pipeline always rewrites the question, searches, reranks and reads whole articles, whether the question is easy or hard. A loop stops as soon as it can answer. So its cost and time grow with the number of hops, not with the pipeline’s design. Here is how that played out across PipesHub’s 824 answers:

| **Model calls PipesHub used** | **Share of questions** | **Median time** | **Median cost** | **Correct** |
| --- | --- | --- | --- | --- |
| 1 | 21% | 8 s | $0.0062 | 95% |
| 2 | 43% | 19 s | $0.0101 | 95% |
| 3 | 20% | 32 s | $0.0136 | 95% |
| 4 | 8% | 47 s | $0.0216 | 91% |
| 5 or more | 7% | 134 s | $0.0604 | 70% |
| *Strongest pipeline, every question* | *100%* | *27 s* | *$0.0053* | *79%* |
| *Naive RAG, every question* | *100%* | *7 s* | *$0.0011* | *36%* |

### Two things stand out

- **Questions that need one pass cost about the same as in the strongest pipeline, and come back faster** ($0.0062 against $0.0053, and 8 s against 27 s). The loop skips the rewriting and whole-article reading the pipeline always does, but its prompt is longer. Naive RAG remains far cheaper than both, and it is also the least accurate.
- **Multi-hop questions take longer, and that’s where the money goes.** Each extra hop adds a model call. The 7% of questions that needed five or more calls took a little over two minutes each, accounted for 37% of PipesHub’s total spend, and were the least accurate (70%).

**Prompt caching makes the long prompt and the extra turns cheap.** The system prompt and tool definitions are identical on every call, and each turn of the loop re-sends what the model has read so far. Providers cache a repeated prompt prefix and bill it at a fraction of the normal price; on our price table, a cached token costs a tenth of a normal one. In PipesHub’s run, 47% of all input tokens were served from the cache. A pipeline’s single prompt is built fresh for each question, so none of its input was cached. Without caching, PipesHub’s fixed prompt and its multi-hop turns would cost much more.

**Citations cost a little too.** Both kinds of system cite about two sources per answer. A pipeline’s citation is a short number like \[3\]. PipesHub’s is a link to the exact passage in the source document, and each block it reads carries a label so it can be cited. That is why PipesHub’s median answer is about twice as long (399 characters against 192). The longer answers add about 50 output tokens, well under 1% of the average cost per question. The labels add a little input on every turn. In return, every answer can be checked, fact by fact.

**Read the tail, not just the middle.** The median is a good measure of what a typical user waits for, but it hides the slow, expensive questions. PipesHub’s median time was 22 s, its 95th percentile 134 s. So for latency we report the median and the 95th percentile. For cost we use the mean, and the mean cost per correct answer, because the bill is a sum over all questions and the tail drives it: here the mean ($0.0167) is about 60% higher than the median ($0.0105).

**Complexity.** A pipeline is a fixed sequence you can test step by step. A loop has more moving parts: tool design, stopping rules, budgets, and how results are presented to the model. Most of our engineering time went here, and the lessons below come from it.

### Why every chatbot should run on an agent loop

A chat assistant can’t choose its questions. The same box gets “What is our refund policy?” and “Which renewal customers opened the most tickets after the price change?” A loop handles both. Easy questions finish in one or two calls, at about the cost of the strongest pipeline and faster (8 s against 27 s), and hard questions get the extra searches they need. A pipeline gives every question the same fixed effort, so it overspends on easy questions and still misses hard ones: on five-article questions the best pipeline we built was right 62% of the time, the loop 90%.

The techniques a pipeline adds as stages, such as query expansion, decomposition and reading whole documents, become things the loop does when it needs to, steered by its prompt. Start with the loop, then spend your effort on the tools it calls and the data it reads.

## Lessons for teams building RAG and AI agents

We improved PipesHub by reading failed answers one at a time and asking why each one failed. On the 200 development questions, five fixes found this way took it from 87.5% to 92.5% correct, against 95.5% for the oracle. None was a clever prompt. Here is what we learned.

### Building the loop

- **Long runs rarely recover.** Answers that took one to six model calls were 90–94% correct. Answers that took thirteen or more were almost never right. Raising the turn limit adds cost, not accuracy. Make each tool result more useful, so the model needs fewer turns.
- **Share budgets fairly.** When the model read several documents at once, the first one used up the whole reading budget, and later documents came back empty 72 times across 200 questions. Splitting the budget fairly fixed it at no extra cost.
- **Your provider’s safety filter is part of your system.** Our “please wrap up” note, sent as a system-style message after a tool result, was blocked by the provider’s content filter every time we replayed it. The user saw a canned refusal. The same words attached to the tool result passed every time. Test control messages on the exact model deployment you ship.
- **Plan for refusals on ordinary content.** The same filter refused a few ordinary factual questions because of text the system retrieved. Treat these as their own error type, tell the user what happened, and track how often it happens.
- **Give the model exact tools for exact work.** Date and arithmetic mistakes stopped once a calculator was available from the first turn.
- **Remove what the task doesn’t need.** Every unused tool and prompt section costs tokens on every turn and competes for the model’s attention.

### Preparing the data

- **Parsing decides what can be found.** Tables whose row labels were marked as headers lost their data. Link URLs made up a third of the text we embedded. Fixing how documents become chunks helped more questions than any retrieval tweak.

### Measuring it

- **Run the two reference points.** Closed book shows how much comes from memory; the oracle shows the ceiling. Without them, “85%” tells you little.
- **Check answers against what the system read.** Models know a lot. A correct answer is only a retrieval success if its facts were in the retrieved text.
- **Ask the model not to use memory, then check that it didn’t.** Even when told to answer only from its sources, a model sometimes fills one missing link from what it already knows, and still cites sources for the rest. One line in PipesHub’s custom instructions cut those answers from 13 to 6 with no loss of accuracy. The prompt reduces it; only a check at grading time tells you how much is left.
- **Check that your trace records everything the model read.** Twice, our own trace left out text PipesHub had shown its model: the rows of a table after the first match, and the rows of a table it had read in full. Each gap made correct answers look as if they came from memory. Fixing the trace moved PipesHub’s grounded accuracy from 69% to 84%, while its accuracy stayed at 93%.
- **Don’t let the checker cut what it checks.** Our grounding check first read at most 6,000 tokens of evidence, keeping the passages that looked most like the question. The linking facts of a multi-hop answer don’t look like the question, so they were cut first: the oracle, handed every article, looked as if it had answered 55 questions from memory. Re-checking cut evidence in full brought that to 2.
- **Count every model call and compare cost per correct answer.** Query rewriting and decomposition are model calls too.
- **Keep a test set nobody tunes on.** Improve on one set; report on another.
- **Read the traces.** Knowing which blocks reached the model made most problems obvious within minutes.

## Why PipesHub leads on multi-hop questions

Across 824 questions, PipesHub answered 14 points more than the best of the 18 RAG pipelines we built (92.7% against 78.9%; 84.0% against 73.2% grounded), and matched the accuracy of a model handed the exact source articles. The reasons are design choices you can read in the open-source code:

- **An agent loop for multi-hop questions.** Each search can use what the last one found, so accuracy holds as questions need more documents: 90% on five-article questions, against 62% for the best pipeline.
- **Parsing by document structure.** Documents become blocks: paragraphs, list items and whole table rows, so a fact in a table stays with its row and column names. On questions that need tables, PipesHub’s grounded accuracy was 83% against 67%.
- **Reading whole records on demand.** When a search snippet isn’t enough, the loop reads the document, as small-to-big does, but only when it needs to.
- **Citations to the exact passage.** Every fact links to the paragraph or table row it came from, so a reader can check each hop.
- **Built for a company, not a benchmark.** Connectors that keep permissions, an entity knowledge graph, and a prompt you can steer with a line of custom instructions, on the model you choose.

Every fix behind these numbers is generic. None was written for FRAMES, and the 624 held-out questions were never looked at while we built them.

## Try agentic RAG on your own documents

The main idea is simple enough to try on your own data. Take a handful of real questions your users ask, and trace them by hand as we did with Jane Ballou. If the second lookup depends on the first answer, a single search will struggle, however good the retriever is.

Three ways to go further:

1. **Try PipesHub on your own documents.** It’s open source. Connect a few sources, switch to search mode, and ask your multi-hop questions. Every answer shows the passages it came from, so you can check each hop. [PipesHub on GitHub](https://github.com/pipeshub-ai/pipeshub-ai)
2. **Reproduce this benchmark.** Everything in this post, including the 18 RAG variants, the controls and the grading, runs on one machine from the repository. The runbook is integration-tests/benchmarks/REPRODUCE.md.
3. **Measure your own system the same way.** The harness is written so that other datasets and other RAG systems can plug in. Add your system and compare it on the same questions, with the same models.

Whatever you build, measure it with closed book and oracle controls, check that correct answers came from the documents, and compare cost per *correct* answer. Those three numbers tell you more than any single accuracy figure.

## Agent loop vs RAG pipeline

A RAG pipeline decides what to read before the model sees any results. An agent loop lets the model decide, one search at a time. That one difference explains most of the gap in this post.

|  | **RAG pipeline** | **Agent loop** |
| --- | --- | --- |
| Who decides what to retrieve | Fixed stages, set at build time | The model, after each result |
| Searches per question | Fixed | As many as the question needs |
| Multi-hop questions | Later hops can’t use earlier answers | Each search uses what the last one found |
| Effort per question | The same for easy and hard | Short for easy, longer for hard |
| Five-article questions (this benchmark) | 62% correct (best of 18) | 90% correct |
| A new kind of question | Needs a new stage or more tuning | Handled by the same tools and prompt |

### Where a standard pipeline fails in practice

- **The answer depends on an earlier answer.** “Who manages the account of our largest customer in Germany?” You must find the customer first, then the manager. One search for the whole question rarely returns both.
- **The facts sit in different systems.** “Which renewal customers opened the most tickets after the price change?” needs the price-change date, the renewal list and the ticket history.
- **Comparisons and totals.** “How did the refund window change between the last two policy versions?” needs both versions read in full, then compared.
- **The user’s words don’t match the document’s.** One search misses and the pipeline answers anyway. A loop sees the miss and searches again with different words.
- **The fact is in a table or a long document.** A snippet has the row label but not the value. A loop reads the whole record when the snippet isn’t enough.

### Why teams are moving to agent loops

A pipeline is tuned for the questions its builders expected. Each new kind of question means another stage, another prompt and another round of tuning. An agent loop gets tools to search, read and calculate, and decides how to combine them for each question. It answers questions nobody designed it for: simple lookups finish in one or two calls, and hard ones get the extra searches they need.

That is why chat assistants and enterprise search tools increasingly give the model retrieval as a tool instead of retrieving once up front. Good retrieval still matters, but it becomes a tool the loop calls, not the whole system.

Star, fork or try PipesHub on [GitHub](https://github.com/pipeshub-ai/pipeshub-ai), and run the benchmark yourself from the same repository.

No headings found on page
