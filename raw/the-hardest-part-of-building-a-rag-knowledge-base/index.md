---
title: "The hardest part of building a RAG knowledge base happens before embeddings"
author: "Puzzleheaded_Box2842"
site: "r/Rag"
source: "https://www.reddit.com/r/Rag/comments/1x6i37q/the_hardest_part_of_building_a_rag_knowledge_base/"
domain: "reddit.com"
language: "en"
description: "Most RAG projects begin with a simple assumption: if we can collect the documents, we can make them searchable. In practice, the hardest wor"
word_count: 1129
---

Most RAG projects begin with a simple assumption: if we can collect the documents, we can make them searchable.  
In practice, the hardest work starts before the first embedding is generated.  
Enterprise knowledge is usually scattered across PDFs, Word files, spreadsheets, slide decks, scanned pages, images, tables, and databases.  
These sources rarely share a consistent structure.  
A PDF may contain headers, footers, broken paragraphs, and tables whose meaning depends on surrounding text.  
A chart may carry more information in its labels and relationships than in the caption.  
A database row may be accurate but meaningless without its schema or business context.  
Converting everything into plain text can remove exactly the context that retrieval needs.  
Raw extraction also introduces duplicates, formatting artifacts, missing values, and partial records.  
If those problems are pushed directly into the vector store, the retriever has to search through noise.  
Poor answers are then often blamed on the embedding model, even though the real problem was the source data.  
For this reason, building a RAG knowledge base should begin with data conversion and cleaning as a deliberate engineering stage.

A practical pipeline can be designed around several stages:

1. **Ingest the source data** and preserve provenance such as file name, page number, section, table, image, database, and record identifiers.
2. **Convert each format into a structured representation.** Document text, tables, chart descriptions, images, and database records should be represented as records with both content and metadata.
3. **Clean and normalize the records** by removing repeated headers, footers, invalid characters, broken fragments, empty fields, and formatting artifacts.
4. **Preserve relationships and context.** Table headers should stay connected to their values, chart labels should remain associated with the relevant visual content, and database rows should retain schema information.
5. **Split the content into meaningful chunks** based on document structure, sections, records, or semantic boundaries instead of using only a fixed character length.
6. **Generate retrieval-ready data**, such as question-answer pairs, summaries, explanations, or context-enriched passages.
7. **Evaluate and filter the outputs** for completeness, source consistency, language, length, and relevance.
8. **Remove duplicate and near-duplicate records** using rules, fingerprints, or semantic similarity, then export the validated data for embedding and indexing.

Intermediate outputs should be stored after each major step, so a failed extraction or overly aggressive filter can be inspected and corrected without rebuilding the entire dataset. This also makes it possible to use different processing branches for PDFs, images, tables, and structured database data while keeping a consistent downstream format.

The design above is implemented in OpenDCAI/DataFlow, and I’d be happy to discuss it further—automated data processing pipelines are an important capability for building reliable RAG systems.

---

## Comments

> **Potential-Wrangler58** · [2026-10-15](https://www.reddit.com/r/Rag/comments/1x6i37q/the_hardest_part_of_building_a_rag_knowledge_base/pgwh7me/)
> 
> Agree that most “bad retrieval” is really bad ingestion. The one thing I’d add to your list is a check after conversion, not just cleaning before it: totals in a table still add up, each value still sits under its header, and every extracted number appears in the source page. Without that, a broken table goes into the index looking perfectly clean.
> 
> Also worth keeping a small set of your ugliest documents (scans, merged headers, tables that continue over pages) and rerunning it every time a stage changes, so you know whether a cleaning step helped or just moved the errors around.
> 
> Disclosure: I work at Anyformat, where we go straight from documents to structured fields instead of text chunks when the end goal is data. Free credits if you want to test it on your worst files.

> **DorkyMcDorky** · [2026-10-15](https://www.reddit.com/r/Rag/comments/1x6i37q/the_hardest_part_of_building_a_rag_knowledge_base/pgvslz4/)
> 
> TL;DR - If data clean, search clean. Good.
> 
> anyone in search knows this. It's a boring job. Parsing and creative ways of chunking control everything.
> 
> You need AB testing too. I will repeat this a lot. Search is temporal w/results, so you need side-by-side at the same time
> 
> You don't hear about either of these techniques which will certainly make your RAG actually work because it's boring and has been around since the 70s :) People will use 1MM in shitty PaaS/SaaS services when all they needed the entire time was a team of interns who know how to type.

> **Legitimate-Push2263** · [2026-10-21](https://www.reddit.com/r/Rag/comments/1x6i37q/the_hardest_part_of_building_a_rag_knowledge_base/19rg2qqic5dmt/)
> 
> tbh date cleaning n preserving context are often overlooked but they make a hugeee difference imo

> **LawfulnessOptimal597** · [2026-10-15](https://www.reddit.com/r/Rag/comments/1x6i37q/the_hardest_part_of_building_a_rag_knowledge_base/pgxaxi1/)
> 
> You just discovered the age old rule: garbage in garbage out. That is why 90% of the effort in most projects is data preparation and cleaning. The cleaner the data, the better structured it is, the better the results. There is, of course, a trade off horizon but that is part of engineering to make the right compromises.

> **ceeej777** · [2026-10-16](https://www.reddit.com/r/Rag/comments/1x6i37q/the_hardest_part_of_building_a_rag_knowledge_base/ph0oepj/)
> 
> Yeah I mean the data cleaning is definitely important. Since most RAG is only pulling a top-k result I usually don’t see the data quality being a huge factor (maybe chunk strategy to keep cohesive context in line). Also more and more of my company’s use cases have moved away from RAG and closer to a AI document parser + SQL agent like Databricks Genie. This debatably makes the data quality requirements even higher at the start, but at least you can run queries across a whole dataset instead of only retrieving a few context chunks

> **LawfulnessOptimal597** · [2026-10-16](https://www.reddit.com/r/Rag/comments/1x6i37q/the_hardest_part_of_building_a_rag_knowledge_base/ph2lqhe/)
> 
> Starting with kNN .. it’s easy to set-up but for any complex heterogeneous corpus, the wrong search mode. Adaptive search may have more complex parameters but it’s generally the more appropriate mode. Even when you go with kNN you need to rescale as the scores don’t tell much and the top k may contain loads that are not relevant and it can also be that k+n may have things that are perhaps even more relevant in the mix with the lexical finds than the top k.

> **marintkael** · [2026-10-16](https://www.reddit.com/r/Rag/comments/1x6i37q/the_hardest_part_of_building_a_rag_knowledge_base/ph3tmn0/)
> 
> Shared drives add a problem even before cleaning: which version of a document is the current one. Folders are full of v2\_final and v3\_final\_really, and if all of them get embedded the retriever returns the outdated policy with the same confidence as the current one. Hash dedup won't catch it, the versions differ by a few lines.

> **Kendall-Kaiser95** · [2026-10-17](https://www.reddit.com/r/Rag/comments/1x6i37q/the_hardest_part_of_building_a_rag_knowledge_base/ph8a0wq/)
> 
> A citation to badly extracted data is still a wrong answer. That's the part that gets overlooked, take a pdf table that continues onto a second page. If the column headers disappear during extraction, the retriever might find the correct number but completely misinterpret what it represents, customgpt.ai is useful for building a searchable knowledge assistant with source backed answers but I'd still want to validate the document conversion process before deployment, curious whether dataflow can automatically detect when table relationships or document context have been lost during extraction, that would be a pretty valuable check

> **New-Masterpiece-6480** · [2026-10-20](https://www.reddit.com/r/Rag/comments/1x6i37q/the_hardest_part_of_building_a_rag_knowledge_base/phubagf/)
> 
> Parsing is the most important step before chunking and embedding. I've built a dedicated tool to parse documents into RAG-friendly formats. [https://docparser.net/](https://docparser.net/)
