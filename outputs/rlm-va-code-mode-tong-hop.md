---
title: "Recursive Language Models (RLM) và Code Mode — Tổng hợp từ wiki"
description: Bài viết tổng hợp mọi kiến thức đã biên dịch trong wiki về RLM, các implementation, benchmark, training và code mode cho tool orchestration.
tags: [language-models, rlm, code-mode, agents, synthesis]
created: 2026-11-21
basis: wiki-only (không mở raw/)
---

# Recursive Language Models (RLM) và Code Mode: tổng hợp

> [!info] Phạm vi và cơ sở
> Bài viết này chỉ tổng hợp từ 16 concept đã biên dịch trong [wiki](../wiki/index.md); không mở lại tài liệu gốc trong `raw/`. Hầu hết các con số là **Reported** (do tác giả/nhà phát hành công bố, wiki chưa tái lập). Các nhận định so sánh giữa các nguồn do agent suy ra được đánh dấu **Synthesis**. Mọi concept liên quan hiện đều ở trạng thái `draft` vì còn phần coverage chưa kiểm tra xong.

## 1. Tóm tắt

**Recursive language model (RLM)** là một *inference scaffold* (khung suy luận): prompt không được nhét hết vào context của model, mà được đặt thành một biến trong REPL bền vững (persistent REPL). Model gốc (*root*) viết code để xem, cắt, tìm và biến đổi dữ liệu đó, rồi gọi các *sub-model* hoặc *sub-RLM* trên từng phần. Nhờ vậy hệ thống xử lý được input và output vượt quá context window của model, nhưng vẫn bị giới hạn bởi tài nguyên, độ tin cậy của model và cách implement ([Recursive language models](../wiki/recursive-language-models.md)).

**Code mode** là cùng ý tưởng "để model viết chương trình", áp dụng cho việc điều phối tool (*tool orchestration*): thay vì vòng lặp model → tool → model cho từng bước, agent viết một đoạn code gọi nhiều tool, lọc kết quả trung gian rồi mới trả về model ([Code mode for agent tool orchestration](../wiki/code-mode-agent-tool-orchestration.md)).

**Synthesis:** Hai khái niệm có chung một nguyên lý: **đưa state và kết quả trung gian ra ngoài prompt, dùng code làm lớp điều phối**. RLM tập trung vào *context* (input dài, sub-call ngữ nghĩa); code mode tập trung vào *tool calls* (ít round trip hơn, ít lặp lại history hơn). Paper về compositional generalization xem cả hai là các abstraction bổ trợ nhau: context offloading, programmatic tool calling và sub-agent delegation ([Compositional generalization](../wiki/compositional-generalization-in-lm-harnesses.md)).

## 2. RLM: cơ chế

### 2.1. Vòng lặp cơ bản

Theo paper của Zhang, Kraska và Khattab (arXiv:2512.24601v3):

1. Khởi tạo REPL bền vững, trong đó input là một biến và có một hàm gọi sub-model/sub-RLM. Root chỉ nhận *metadata* chứ không nhận toàn bộ input.
2. Root sinh code; code chạy trên state bền vững; output bị cắt bớt (*truncated*) hoặc metadata được trả lại root. Code có thể search, chunk, loop, giao việc ngữ nghĩa cho sub-call và lưu kết quả trung gian.
3. Kết quả được trả về qua một biến trong môi trường, nên output có thể dài hơn giới hạn sinh token của root. Implementation cũng cho phép trả lời trực tiếp.

Paper tách ra ba lựa chọn thiết kế: **symbolic input handle**, **symbolic output**, và **sub-call gọi từ bên trong code** (thay vì chỉ ủy quyền bằng lời). Về độ sâu (*depth*): depth 0 là không có sub-call, depth 1 là sub-LM thường, depth > 1 là RLM lồng nhau. Trong thí nghiệm GPT-5, root là GPT-5 và leaf là GPT-5-mini ([Recursive language models](../wiki/recursive-language-models.md#mechanism)).

### 2.2. Context-centric và task-centric

Blog của Alex Zhang gọi đây là phân rã **context-centric**: model tự quyết định lúc inference nên xem cấu trúc, grep, chia nhỏ rồi map việc gán nhãn sang các sub-call, hay tóm tắt. Bài của Om Alve so sánh RLM với RAG, compaction và context folding. **Synthesis:** việc nói "RLM tránh compaction" là cách mô tả scaffold, không phải một lệnh cấm; chính blog của tác giả liệt kê summarization là một trong các chiến lược có thể dùng.

### 2.3. Hạn chế vận hành (Reported)

- Kết quả phụ thuộc cách phân rã và prompt mẫu.
- Lỗi code/syntax, dùng tag final-answer sai chỗ, gọi sub-call quá nhiều, mất kết quả trung gian.
- Implementation chính dùng **sub-call tuần tự và blocking**, nên latency có đuôi dài. Guardrail, sandbox và kiểm soát chi phí còn ít được nghiên cứu.
- Prompt cho Qwen3-8B đưa ra các ước lượng ký tự mâu thuẫn nhau cho giới hạn 32k token, nên không nên dùng làm mặc định.

## 3. Benchmark RLM

Chi tiết nằm ở [RLM evaluation and benchmarks](../wiki/rlm-evaluation.md). Một số điểm chính (**Reported**):

| Method | CodeQA | BrowseComp+ | OOLONG | OOLONG-Pairs F1 |
| --- | ---: | ---: | ---: | ---: |
| GPT-5 base | 24.0* | 0.0* | 44.0 | 0.1 |
| GPT-5 RLM depth 1 | 62.0 | 91.3 | 56.0 | 58.0 |
| GPT-5 RLM depth 3 | 58.0 | 92.0 | 58.0 | 76.0 |
| GPT-5 OpenCode (context offloaded) | 64.0 | 94.0 | 52.0 | 4.8 |
| Qwen3-Coder RLM depth 0 | 66.0 | 46.0 | 43.5 | 17.3 |
| Qwen3-Coder RLM depth 1 | 56.0 | 44.7 | 48.0 | 23.1 |

\* có run bị chạm giới hạn input.

Cách đọc bảng:

- RLM thường vượt base, nhưng **không thắng mọi nơi**. OpenCode có context offloading cao hơn RLM depth 1 trên BrowseComp+, và Qwen depth 0 cao hơn depth 1 trên CodeQA.
- Chênh lệch lớn nhất là ở OOLONG-Pairs, task đòi output có thể tăng theo bậc hai. Depth 3 đạt 76.0, depth 1 đạt 58.0, OpenCode chỉ 4.8.
- **Chi phí** không được đảm bảo: GPT-5 depth 1 trên BrowseComp+ tốn $0.99 ± $1.22 mỗi task, so với compaction $0.57 ± $0.10. Phân phối chi phí có đuôi dài.
- **LongCoT-mini:** GPT-5.2 base đạt 38.7%, RLM depth 1 không hint đạt 50.6%, có hint phân rã đạt 65.6%. RLM không hint lại kém base ở toán và CS.

**Thí nghiệm sơ bộ trong blog** (mẫu khác, không được gộp với paper): ở OOLONG 132K, RLM GPT-5-mini đạt 64.9% với $0.234 mỗi query, còn GPT-5 trực tiếp đạt 30.3% với $0.195. Như vậy câu "RLM rẻ hơn trung bình" không đúng ở mốc 132K, nhưng đúng ở 263K. BrowseComp-Plus với 1.000 tài liệu chỉ có 20 query: RLM 100%, không sub-call 90%, ReAct+BM25 60%.

**Ablation của Prime Intellect** (GPT-5-mini, 50 rollout): RLM thua direct ở math-python (0.35 so với 0.44), thắng ở OOLONG (0.55 so với 0.43). Chỉ số "token efficiency" của họ **chỉ đếm token của root**, không phải tổng token hay chi phí. RLM chậm hơn ở cả bốn môi trường.

## 4. Các implementation

| Implementation | Đặc điểm chính | Giới hạn quan trọng |
| --- | --- | --- |
| [Prime Intellect RLM scaffold](../wiki/prime-intellect-rlm.md) | Depth 1; `llm_batch` gọi sub-model song song; tool môi trường chỉ dành cho sub-model; trả lời bằng cách sửa `answer["content"]` và đặt `answer["ready"] = True` ("diffusion"); output REPL tối đa 8.192 ký tự mỗi lượt | Depth 0, recursion lồng nhau và compression mới là kế hoạch tương lai; câu "never summarizes" quá rộng |
| [Prime Agent harness](../wiki/prime-agent.md) | Harness dài hạn: kernel IPython bền vững cho mỗi session; `rlm` **bất đồng bộ** trả về handle (khác với blocking sub-call của paper); daemon giữ session; *Continual Harness* lưu prompt notes, memory, skills, có version và rollback | Cơ chế tự cải thiện có thể lưu cả hành vi xấu, ví dụ một shortcut gian lận trong Factorio trở thành skill; không phải sandbox |
| [Prime Agent implementation](../wiki/prime-agent-implementation.md) | Workspace Rust v0.10.5 gồm 10 crate cùng shim Python ≥3.11; shim hướng dẫn dùng `await rlm.spawn(...)` | Chưa xác lập được đây là phiên bản dùng trong paper; README cảnh báo kernel không phải security sandbox |
| [Recursive-llm (grishahq)](../wiki/recursive-llm-grishahq.md) | Python, REPL dùng RestrictedPython, budget cho toàn cây; chế độ document kiểm tra citation (doc ID, hash, trang, offset, quote chính xác) | Validator **không** kiểm tra quote có hỗ trợ claim hay không; không có OCR; không phải ranh giới bảo mật |
| [rlm.pi](../wiki/rlm-pi-implementation.md) | Plugin cho Pi/oh-my-pi (`/rlm`), worker Python dùng JSONL, mặc định `maxDepth=4`, `maxIterations=1000`, timeout 120s | Worker có thể đọc/ghi file và truy cập mạng (**Observed**), mâu thuẫn với README; các default trong README lệch với code |
| [RLM workflows in Deep Agents](../wiki/deep-agents-rlm-workflows.md) | Main agent viết code gọi `task` để fan-out tới subagent (có tool và state), aggregate, chạy tournament; dùng từ khóa "workflow" trong prompt để gợi ý | Đây là demo/smoke test; không có đánh giá độc lập về isolation |

**Synthesis:** Có một trục khác biệt rõ giữa các implementation:

- **Kiểu sub-call:** paper dùng sub-LM thuần và blocking; Prime Intellect dùng batch song song; Prime Agent và Deep Agents dùng subagent có tool và state, chạy bất đồng bộ.
- **Bảo mật:** không implementation nào được wiki ghi nhận là một sandbox đã được kiểm định. Cả bốn dự án có tài liệu bảo mật đều nói hoặc ngầm thừa nhận rằng cần cô lập bên ngoài khi chạy code không tin cậy.

### Kết quả của từng implementation (Reported, không so sánh trực tiếp được với nhau)

- **Prime Agent** ([evaluation](../wiki/prime-agent-evaluation.md)): ARC-AGI-3 đạt 95.5% với Opus 5, so với tham chiếu bên ngoài 30.2%; đây không phải so sánh có kiểm soát. Ở long-context, kết quả lẫn lộn: OOLONG Yahoo 128k với GLM-5.2 là .700 so với .420 (Pi-mono), nhưng Opus 5 là .900 so với .920 (Claude Code). Factorio: chạy 7 ngày, tạo 633 subagent depth 1.
- **recursive-llm** ([evaluation](../wiki/recursive-llm-evaluation.md)): trên corpus 100K ký tự, GPT-5 mini direct 0/3 so với RLM 3/3, dùng ít token hơn. Trong nghiên cứu document, cả hai mode đều dùng **0 child call**, nên kết quả không chứng minh được lợi ích của recursion.
- **rlm.pi** ([evaluation](../wiki/rlm-pi-evaluation.md)): OOLONG-synth 24 task ≤ 65K token, GLM-5.3 đạt 23/24 và Qwen3.8-27B đạt 22/24. Cấu hình benchmark khác với default.
- **Deep Agents RLM**: OOLONG AG News, 64k: 0.58 → 0.67; 128k: 0.44 → 0.79. Ở 128k dùng ít token hơn nhưng **đắt hơn** do giá output token. P50 latency cao hơn, nhưng P99 thấp hơn.

## 5. Training cho RLM

- **Distillation RLM-Qwen3-8B** ([Training RLMs](../wiki/training-recursive-language-models.md)): khoảng 1.000 trajectory lọc từ Qwen3-Coder-480B, chạy 48 giờ H100. Kết quả so với chính Qwen3-8B trong scaffold RLM: CodeQA 26→32, BrowseComp+ 2→14, OOLONG 24→32.04. Mức này vẫn còn xa GPT-5 RLM.
- **RL** cho Qwen3-4B trên MRCRv2 (train ở 32k–64k với 2 needle, eval ở 512k–1M với 8 needle): reward tăng dần. Đây chỉ là một task tổng hợp.
- **Surrogate harness training** ([concept](../wiki/surrogate-harness-training.md)): huấn luyện một call cụ thể trong harness trên môi trường tổng hợp, giữ nguyên chiến lược giải, có lúc dùng sub-call oracle. RLM-27B (SFT) trung bình 58.5 so với base 46.1 (+12.4 điểm) trên 8 split held-out. Số turn giảm 18.4→6.5, root input token giảm 263K→44K. Khi xâu chuỗi 4 task, RLM-27B giải trọn 55.2% chuỗi; thêm recursion SFT thì đạt 77.5%. Hạn chế: môi trường tổng hợp được thiết kế khi đã biết họ benchmark đích, và mô tả task trùng lặp nhiều.

## 6. Vì sao harness có thể khái quát hóa: giả thuyết LID

Zhang, Chakraborty và Khattab đề xuất tính **locally in-distribution (LID)**: một task mới về tổng thể có thể được phân rã thành các bước điều phối quen thuộc và các model call mà từng cái đều dễ xử lý ([Compositional generalization](../wiki/compositional-generalization-in-lm-harnesses.md)).

- **Length transfer** (Qwen3-30B-A3B GRPO, độ dài từ 2× đến 64×): RLM thường transfer tốt hơn model gọi trực tiếp và các harness khác. Task đồ thị/retrieval có thể transfer chỉ bằng code; task ngữ nghĩa dày đặc thì hưởng lợi từ sub-call.
- **Strategy transfer** (ví dụ OOLONG question → spam): RLM transfer mạnh nhất. Trajectory có câu chữ giống nhau không cứu được Pi khi quy trình nó học được không scale.
- Đây là bằng chứng ủng hộ giả thuyết, **không phải chứng minh**. Thí nghiệm dùng một seed và một rollout eval mỗi ví dụ.
- Quan điểm (**opinion**) của @a1zhang và @omarsar0: harness không chỉ là chỗ dựa cho model yếu, mà còn kết hợp được năng lực của model mạnh. Chưa có gì xác lập rằng model sẽ hấp thụ hết vai trò của harness.

## 7. Code mode và programmatic tool calling

### 7.1. Pi code mode (case study của @geoqiao)

Pi cung cấp `exec` và `wait`; model viết code trong `exec` để kết hợp tool. Task dài: thiết kế theme cho một blog generator (**Reported**, 1 run mỗi nhóm, GPT 6 Astra High):

| Metric | Native tools | Code mode | Thay đổi |
| --- | ---: | ---: | ---: |
| Model responses | 129 | 42 | −67.4% |
| Cache-read tokens | 16.67M | 3.99M | −76.0% |
| Cumulative tokens | 17.17M | 4.29M | −75.0% |
| Thời gian | 54m07s | 32m33s | −39.9% |
| Chi phí ước tính | $24.29 | $8.75 | −64.0% |

Tác giả quy 98.46% phần chênh lệch token cho việc giảm cache read. Đây là cơ chế: mỗi round trip phải gửi lại toàn bộ history. Hạn chế: chỉ có một task, không có điểm chất lượng thống nhất, và project đã thay đổi giữa các run. Tác giả phỏng đoán rằng với task ngắn và đơn giản, chi phí viết code có thể xóa mất lợi ích; điều này chưa được chứng minh.

### 7.2. Deep Agents interpreter / PTC

[Deep Agents interpreter](../wiki/deep-agents-interpreter.md): middleware thêm tool `eval` chạy TypeScript trong **QuickJS**. Mặc định không có filesystem, network, shell hay package. **Programmatic tool calling (PTC)** dùng allowlist `ptc=[...]` để đưa các tool được chọn vào namespace `tools` dưới dạng hàm async. Có ba tầng state: message history (thứ model đang thấy), filesystem (artifact lâu dài), interpreter state (giá trị đang dùng, không tự động vào prompt). Có các giới hạn về memory, timeout, số bridged call và kích thước kết quả.

Thử nghiệm sớm trên OOLONG trec-coarse (**Reported**): Opus 4.7 giảm từ 831K xuống 538K token và từ 4.67 xuống 3.67 step. Với Sonnet 4.6, token giảm (794K → 596K) nhưng **P50 latency tăng** (8.62 → 10.72s). Nguồn không công bố accuracy.

Thiết lập (time-sensitive, chưa chạy thử): `pip install -U "deepagents[quickjs]"`, sau đó `create_deep_agent(..., middleware=[CodeInterpreterMiddleware(ptc=["task"])])`. Khi đưa `task` vào allowlist, interpreter trở thành một workflow kiểu RLM ([Deep Agents RLM workflows](../wiki/deep-agents-rlm-workflows.md)).

## 8. Những điểm rút ra (Synthesis)

1. **Một nguyên lý, nhiều biến thể.** RLM, code mode và PTC đều chuyển phần điều phối từ "model đọc mọi thứ" sang "model viết chương trình, chương trình đọc mọi thứ". Khác biệt nằm ở thứ được offload (context, tool output hay sub-agent) và kiểu sub-call (blocking, batch hay async).
2. **Lợi ích phụ thuộc task.** Lợi thế rõ nhất là ở input rất dài, output lớn (OOLONG-Pairs) và task dài nhiều bước. Ở task ngắn, gọi trực tiếp thường nhanh hơn và rẻ hơn (recursive-llm, Prime Intellect math, phỏng đoán của @geoqiao).
3. **"Ít token" không có nghĩa là "rẻ hơn" hay "nhanh hơn".** Nhiều nguồn chỉ đếm token của root (Prime Intellect), hoặc thấy chi phí tăng vì output token (Deep Agents 128k), hoặc latency P50 tăng (Sonnet 4.6, Deep Agents).
4. **Recursion không phải lúc nào cũng là yếu tố tạo khác biệt.** Có những trường hợp depth 0 thắng depth 1 (Qwen CodeQA), task được giải bằng regex (Prime Intellect OOLONG labeled), hoặc không có child call nào (recursive-llm document study). Lợi ích có thể đến từ việc offload context và chạy code, chứ không nhất thiết từ sub-call.
5. **Bảo mật là điểm yếu chung.** Mọi implementation đều chạy code do model viết. Không cái nào được wiki ghi nhận là sandbox đã kiểm định, và rlm.pi còn mâu thuẫn với chính README của nó. Cần cô lập bên ngoài (container, hạn chế mạng, không đưa credential) khi input không đáng tin.
6. **Training root orchestration có triển vọng.** Distillation, RL và surrogate training đều cải thiện khả năng điều phối, kèm giảm turn và token. Nhưng bằng chứng hiện có đều từ tác giả, quy mô nhỏ, và môi trường được thiết kế khi đã biết task đích.

## 9. Giới hạn của bài tổng hợp

- Mọi concept nguồn đều ở trạng thái `draft`. Nhiều figure, code, benchmark và log gốc chưa được kiểm tra. Không có kết quả nào được wiki tái lập (không có `verified`).
- Các benchmark dùng giao thức, model và cách tính điểm khác nhau, nên **không được gộp hay xếp hạng chéo**.
- Hai concept về tool orchestration có `stale_after: 2027-05-21` (API, giá, cấu hình).
- Bài viết không mở `raw/`; muốn có chi tiết ở mức nguồn (công thức, implementation chính xác) thì cần đọc trực tiếp các source được trích dẫn trong từng concept.

## Nguồn trong wiki

- [Recursive language models](../wiki/recursive-language-models.md)
- [RLM evaluation and benchmarks](../wiki/rlm-evaluation.md)
- [Training recursive language models](../wiki/training-recursive-language-models.md)
- [Surrogate harness training](../wiki/surrogate-harness-training.md)
- [Compositional generalization in LM harnesses](../wiki/compositional-generalization-in-lm-harnesses.md)
- [Prime Intellect RLM scaffold](../wiki/prime-intellect-rlm.md)
- [Prime Agent harness](../wiki/prime-agent.md) · [evaluation](../wiki/prime-agent-evaluation.md) · [implementation](../wiki/prime-agent-implementation.md)
- [Recursive-llm implementation](../wiki/recursive-llm-grishahq.md) · [evaluation](../wiki/recursive-llm-evaluation.md)
- [rlm.pi implementation](../wiki/rlm-pi-implementation.md) · [evaluation](../wiki/rlm-pi-evaluation.md)
- [RLM workflows in Deep Agents](../wiki/deep-agents-rlm-workflows.md)
- [Deep Agents interpreter and programmatic tool calling](../wiki/deep-agents-interpreter.md)
- [Code mode for agent tool orchestration](../wiki/code-mode-agent-tool-orchestration.md)
