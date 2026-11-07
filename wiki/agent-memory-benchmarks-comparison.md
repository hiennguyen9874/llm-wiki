---
type: Synthesis
title: Agent memory benchmarks comparison
description: Tập hợp và giải thích các con số benchmark do tám hệ agent-memory tự công bố (LongMemEval, LoCoMo, BEAM, PersonaMem, BrainBench, CMB, token savings), metric mỗi con số đo, mức tái lập được và lý do không thể xếp hạng chéo.
tags: [agent-memory, survey, comparison, benchmarks, evaluation]
status: draft
created: 2026-11-07
generated: { by: llm-wiki-agent/1, at: 2026-11-07T01:20:00Z }
stale_after: 2027-02-06
sources:
  - id: ai-memory
    resource: ../raw/ai-memory/README.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory repository
  - id: cognee
    resource: ../raw/cognee/README.md
    scope: ../raw/cognee/
    kind: code
    revision: 525b1d1
    title: Cognee repository
  - id: gbrain
    resource: ../raw/gbrain/README.md
    scope: ../raw/gbrain/
    kind: code
    revision: 27f8b9d
    title: GBrain repository
  - id: headroom
    resource: ../raw/headroom/README.md
    scope: ../raw/headroom/
    kind: code
    revision: 2b0315b
    title: Headroom repository
  - id: hindsight
    resource: ../raw/hindsight/README.md
    scope: ../raw/hindsight/
    kind: code
    revision: eb963cb
    title: Hindsight repository
  - id: hy-memory
    resource: ../raw/Hy-Memory/README.md
    scope: ../raw/Hy-Memory/
    kind: code
    revision: 9737431
    title: Hy-Memory monorepo (hy-memory SDK, MemHub, CMB paper)
  - id: mem0
    resource: ../raw/mem0/README.md
    scope: ../raw/mem0/
    kind: code
    revision: d16b8df
    title: Mem0 repository
  - id: tencentdb
    resource: ../raw/TencentDB-Agent-Memory/README.md
    scope: ../raw/TencentDB-Agent-Memory/
    kind: code
    revision: 2002196
    title: TencentDB Agent Memory repository
---

# Agent memory benchmarks comparison

Trang này thuộc cụm [Agent memory landscape survey](agent-memory-landscape-survey.md). Nó gom mọi con số đánh giá mà các dự án tự công bố. **Tất cả đều là Reported**, và wiki không chạy lại con số nào. Kết luận chính là các con số **không thể xếp hạng chéo**. Lý do: chúng đo các metric khác nhau (retrieval hit/recall@k, độ chính xác QA do LLM chấm, tỉ lệ task resolved, token saving), trên các split và phiên bản dataset khác nhau, với model trả lời, judge, harness và thời điểm khác nhau. Có khi con số thuộc về sản phẩm managed chứ không phải bản OSS.

## 1. Bảng tổng hợp

| Hệ | Benchmark | Con số | Metric | Ai chạy / ở đâu |
|---|---|---|---|---|
| Hindsight | LongMemEval | 94.6% | QA accuracy (LLM judge) | Vendor tự chạy lại qua AMB ở v0.4.19 (harness bên ngoài)[^hindsight] |
| Hindsight | LoCoMo | 92.0% | QA accuracy | Như trên[^hindsight] |
| Hindsight | PersonaMem / LifeBench | 86.6% / 71.5% | QA accuracy | Như trên[^hindsight] |
| Hindsight | BEAM 100K / 500K / 1M / 10M | 73.4 / 71.1 / 73.9 / **64.1** (hệ đứng thứ hai được ghi là 40.6 "Honcho"; baseline RAG 24.9) | Rubric do LLM chấm | Blog vendor (2026-04-02)[^hindsight] |
| Mem0 | LoCoMo / LongMemEval | 92.5 / 94.4 (migration guide: 91.6 / 93.4) | QA accuracy | **Managed platform**; budget top-200, retrieval một lượt[^mem0] |
| Mem0 | BEAM 1M / 10M | 64.1 / 48.6 | Rubric | Managed platform[^mem0] |
| GBrain | LongMemEval-S (sạch, 470 câu) | `recall_all@5` 449/470 = **95.53%** (tắt reranker: 93.40%) | Retrieval nghiêm ngặt: *mọi* evidence phải nằm trong top-5 | v0.48.4.0, 2026-09-06; số đến từ repo `gbrain-evals` bên ngoài[^gbrain] |
| GBrain | BrainBench (145 câu hỏi quan hệ tổng hợp) | R@5 0.6626 → 0.7241 khi bật graph | Recall@5 | Bên ngoài; 0.9791 là cận trên oracle, không phải điểm sản phẩm[^gbrain] |
| GBrain | LoCoMo held-out (time-aware) | 74.2% → 88.2% (+14.0, CI [+11.8, +16.2]) | QA | Tài liệu eval trong repo[^gbrain] |
| ai-memory | LongMemEval-S (470 câu đã chấm) | hit@5 **0.951** (FTS) / **0.940** (embedding local); hit@1 0.857 / 0.764; p50 15 / 129 ms; khoảng 519 token context | Retrieval hit@k (*ít nhất một* evidence) | **Harness trong repo**; báo cáo ghi commit, sha256 dataset, phần cứng (máy đang tải)[^ai-memory] |
| Cognee | BEAM 100K / 10M | 0.79 / 0.67 | Rubric (LLM judge) | `REPORT.md` trong repo; 100K: 20 câu hỏi, 1 hội thoại; 10M: thăm dò, routing được chọn trên chính tập câu hỏi dùng để báo cáo[^cognee] |
| TencentDB | PersonaMem | 48% → 76% (tăng tương đối 59%) | QA accuracy | README; protocol chưa được inspect[^tencentdb] |
| Hy Memory (CMB) | CMB (216 task + 750 QA, 9 repo) | TriLink 43.1% Resolved / 58.2% QA (Sonnet-5); 35.6% / 64.2% (DeepSeek-v4-flash); baseline tốt nhất 36.6% / 28.2% | Resolved theo test + QA chấm bằng rubric | Paper do chính tác giả công bố (nộp ICLR 2027), PDF có trong repo[^hy-memory] |
| Headroom | 4 kịch bản output của agent | Tiết kiệm 21% / 57% / 42% / 30% token input | Token saving | Script `index_proof_table.py --seed 20260902` có trong repo[^headroom] |

## 2. Các metric trông giống nhau nhưng khác nhau

- **LongMemEval của ai-memory và của GBrain:** ai-memory báo *hit@5*, tức ít nhất một evidence nằm trong top-5. GBrain báo *recall_all@5*, nghiêm ngặt hơn, tức mọi evidence phải nằm trong top-5. Cả hai đo retrieval, **không** đo độ chính xác câu trả lời. Còn 94.6% của Hindsight và 94.4 của Mem0 là **QA accuracy** sau khi model trả lời và judge chấm. Bốn con số khoảng 94–95% vì vậy đo bốn thứ khác nhau (Synthesis).[^ai-memory][^gbrain][^hindsight][^mem0]
- **BEAM:** Hindsight, Mem0 và Cognee đều báo BEAM, nhưng ở các mức context khác nhau, harness khác nhau, và (với Mem0) trên managed platform. 64.1 của Hindsight là ở mức 10M; 64.1 của Mem0 là ở mức 1M. Trùng số chỉ là ngẫu nhiên.[^hindsight][^mem0][^cognee]
- **PersonaMem:** Hindsight báo 86.6%, TencentDB báo 76% với sản phẩm. Phiên bản dataset và protocol không được đối chiếu.[^hindsight][^tencentdb]

## 3. Mức tái lập từ repo (Synthesis)

| Mức | Hệ | Lý do |
|---|---|---|
| Cao | ai-memory | Harness `ai-memory-eval` (`retrieval`, `ab`, `projection`, `abstention`…) cùng báo cáo release ghi commit, sha256 dataset, lệnh chạy và cảnh báo về nhiễu (±0.005)[^ai-memory] |
| Cao (phạm vi hẹp) | Headroom | Script proof có seed; nhưng các script khác dùng mock token counter, nên phương pháp đo có thể không đồng nhất[^headroom] |
| Trung bình | Hindsight | Eval hệ thống trong repo (retain 35 case, recall 19 case, BEIR SciFact nDCG@10 khoảng 0.874–0.887 theo comment). Các benchmark công khai chạy qua dự án AMB bên ngoài; không có artifact kết quả được commit[^hindsight] |
| Trung bình | Cognee | Report trong repo có thiết kế thí nghiệm; code công khai thiếu phần điều phối của lần chạy 10M[^cognee] |
| Trung bình | Hy (CMB) | Paper có trong repo; các default trong appendix khớp code; dataset và harness không được kiểm tra[^hy-memory] |
| Thấp | GBrain | Có nhiều eval suite, nhưng các con số headline lấy từ repo bên ngoài; `baselines/main.json` không chứa giá trị R@5/P@5[^gbrain] |
| Thấp | Mem0 | Submodule `evaluation/` chưa được khởi tạo; README và migration guide lệch số nhau[^mem0] |
| Thấp | TencentDB | Protocol, dataset và harness chưa được inspect[^tencentdb] |

## 4. Những kết quả đáng chú ý ngoài headline

- **Kết quả âm và cảnh báo của GBrain:** query expansion làm `recall_all@5` tụt từ 93.19% xuống 54.89%; autocut làm giảm từ 449 xuống 379/470; thí nghiệm "answer-evidence packet" có 0 lần thắng và 5 lần thua. Một headline cũ (P@5 49.1%) được đánh dấu **"do not cite"**.[^gbrain]
- **Ablation của CMB:** bỏ diff chain thì Resolved giảm từ 35.6% xuống 20.8%; bỏ experience hoặc fact thì xuống khoảng 19.9%. FullContext đạt 58.8% nhưng sụp còn 28.2% với backbone yếu hơn. Về hiệu quả token: TriLink đạt 28.3% với 690 token, MemOS và Mem0 đạt 25.3% với 479 và 257 token.[^hy-memory]
- **Xu hướng của ai-memory:** từ 2.0 đến 3.0, hit@5 của FTS tăng từ 0.617 lên 0.951 khi stream observation trở thành mặc định. Ở bản 3.4.0, FTS (15 ms p50) nhỉnh hơn embedding local.[^ai-memory]
- **So sánh ranker của Hindsight** (19 case recall): cross-encoder local 6/19, RRF 10/19, decision model 19/19 (Reported). Hindsight cũng lập luận rằng LoCoMo và LongMemEval đã không còn phân biệt được các hệ, vì nhồi context dài cũng đạt điểm cạnh tranh.[^hindsight]
- **Cognee** nói rõ rằng các mức context không phải một so sánh có kiểm soát, và việc lặp vòng không thêm câu hỏi độc lập.[^cognee]

## Contradictions

- **Hạng nhì ở BEAM 10M.** Blog BEAM của Hindsight (2026-04-02) ghi hệ đứng sau là 40.6 ("Honcho"). README của Mem0 (thuật toán tháng 4/2026) ghi managed platform của Mem0 đạt 48.6 ở BEAM 10M. Hai nguồn khác thời điểm và harness; wiki không chọn bên nào.[^hindsight][^mem0]
- **Số của Mem0:** README ghi LoCoMo 92.5 / LongMemEval 94.4; migration guide ghi 91.6 / 93.4. Không rõ vì sao lệch.[^mem0]

## Gợi ý đọc benchmark (Synthesis)

1. Hỏi trước: con số này là retrieval hay QA? Ai trả lời, ai chấm?
2. Con số đo bản OSS hay managed (Mem0)? Đo ở version nào?
3. Harness có trong repo không? Có ghi commit và hash dataset không (ai-memory là mẫu tốt)?
4. Với coding agent, CMB là benchmark duy nhất trong wiki đo trực tiếp *task resolved* có interleaving và revision; nhưng nó do Hy tự công bố.
5. Muốn so sánh thật thì phải chạy cùng một harness trên các hệ. Wiki chưa có kết quả nào như vậy.

## Relationships

- Part of: [Agent memory landscape survey](agent-memory-landscape-survey.md).
- Evaluates: [retrieval comparison](agent-memory-retrieval-comparison.md).
- Related: [CMB](cmb-coding-memory-benchmark.md), [ai-memory comparison claims](ai-memory-comparison-claims.md).

[^ai-memory]: [evals/benchmarks](ai-memory-evals-and-benchmarks.md), [comparison claims](ai-memory-comparison-claims.md). Raw: `docs/benchmarks/longmemeval-s-3.4.0-release.md` "Setup", "Results"; `docs/benchmarks/README.md` (trend, caveats); `evals/README.md`; `evals/src/main.rs`.
[^cognee]: [benchmarks](cognee-benchmarks.md). Raw: `cognee/eval_framework/beam/REPORT.md::3.1 Experimental Design`, `::3.4 Evaluation Protocol`, `::4 Results`.
[^gbrain]: [evals/benchmarks](gbrain-evals-and-benchmarks.md), [knowledge graph](gbrain-knowledge-graph.md). Raw: `docs/architecture/RETRIEVAL.md` "The benchmark" và các bảng kết quả; `docs/eval-bench.md`; `docs/eval/TIME_AWARE_RETRIEVAL_RESULTS.md`; `docs/eval/ANSWER_PACKET_RESULTS.md`; `evals/brainbench/baselines/main.json`.
[^headroom]: [benchmarks](headroom-benchmarks.md). Raw: `README.md` § Proof; `benchmarks/index_proof_table.py`; `benchmarks/results/index_proof_table.txt`; `benchmarks/conftest.py::MockTokenCounter`.
[^hindsight]: [benchmarks/testing](hindsight-benchmarks-and-testing.md), [decision models](hindsight-decision-models.md). Raw: `hindsight-docs/blog/2026-03-23-agent-memory-benchmark.mdx` (bảng kết quả); `hindsight-docs/blog/2026-04-02-beam-sota.md` dòng 48–62; `hindsight-system-evals/README.md`; `evals/recall/test_recall.py`.
[^hy-memory]: [CMB](cmb-coding-memory-benchmark.md), [diff chain](hy-memory-coding-diff-chain.md). Raw: `docs/papers/CMB_A_Coding_Memory_Benchmark_for_Long_Horizon_and_Interleaved_Coding_Agents.pdf` Table 2 (tr. 7), Fig. 3–5 (tr. 7–9), §6 (tr. 9), Table 12 (tr. 18–19).
[^mem0]: [benchmarks](mem0-benchmarks.md), [source map](mem0-source-map.md). Raw: `README.md::New Memory Algorithm (April 2026)`; `docs/migration/oss-v2-to-v3.mdx::Overview`; `.gitmodules::submodule evaluation`.
[^tencentdb]: [overview](tencentdb-agent-memory-overview.md), [source map](tencentdb-source-map.md). Raw: `README.md` § Benchmark.
