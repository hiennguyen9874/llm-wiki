# Tổng hợp cụm Agent memory cross-system

Tôi chỉ đọc sáu trang trong cụm này, không ingest lại và không mở `raw/`. Wiki và log không thay đổi. Cả sáu trang đều là `type: Synthesis`, `status: draft`, `stale_after: 2027-02-06`. Không trang nào có `verified`.

## 1. Bức tranh chung

Wiki có tám hệ, gồm Mem0, Cognee, Hindsight, Hy-Memory/MemHub, TencentDB Agent Memory, ai-memory, GBrain và Headroom. Nguồn: [landscape survey](agent-memory-landscape-survey.md).

Các hệ chia theo sáu hướng thiết kế. Một hệ có thể thuộc nhiều hướng.

| Hướng | Ý tưởng | Đại diện |
|---|---|---|
| A. Fact layer | LLM trích fact rời, retrieval là semantic top-k | Mem0 |
| B. Knowledge graph | Graph + vector dựng từ nội dung | Cognee; GBrain và Hy `ultra` có graph |
| C. Cognitive/hierarchical | Phân tầng, consolidation, tự tiến hoá | Hindsight, Hy, TencentDB |
| D. Compiled Markdown | File là source of truth, DB chỉ là index | ai-memory, GBrain |
| E. Cross-harness hub | Một memory dùng chung cho nhiều agent | MemHub, ai-memory, TencentDB proxy |
| F. Context compression | Tối ưu token, không lưu tri thức | Headroom |

Hướng F bổ trợ cho A–E. F giảm token trong session hiện tại, còn A–E giữ tri thức giữa các session.

**Điểm hội tụ (Synthesis):**
- Hybrid retrieval với RRF `k=60`.
- Memory phân tầng từ raw đến fact, rồi đến profile/schema.
- Supersession có lịch sử thay vì ghi đè.
- Tích hợp qua MCP cộng hook.
- Giảm phụ thuộc cloud bằng embedder local.
- Tách expire khỏi purge, và thừa nhận xoá chỉ là logical.

**Bốn trục khác biệt cốt lõi:**
1. LLM là lõi bắt buộc hay chỉ là lớp nâng cấp trên write path.
2. Source of truth là Markdown + git hay DB.
3. Mô hình isolation.
4. Ai nắm vòng đời ghi: agent, hook, proxy hay importer.

## 2. Data model và write path

Nguồn: [data model và write](agent-memory-data-model-and-write-comparison.md).

- **Đơn vị memory** có ba trường phái:
  - Fact phẳng: Mem0.
  - Hierarchy theo mức trừu tượng: Hy (L0–L7), TencentDB (L0–L3), Hindsight.
  - Trang tài liệu: ai-memory, GBrain.
- GBrain là hệ duy nhất tách "ai tin điều gì" (takes có `holder` và `weight`) khỏi "sự thật về entity" (facts).
- **Ghi không cần LLM:**
  - ai-memory làm điều này mặc định, bằng trang session deterministic.
  - GBrain chạy keyless.
  - Hy có mode `lite`.
  - Mem0 chỉ có `infer=False`.
  - Hindsight gần như không thể bỏ LLM.
- **Cập nhật:** Hy, ai-memory, GBrain và Hindsight dùng supersession có lịch sử. Mem0 OSS và Headroom thì chỉ thêm hoặc gỡ khỏi index.
- **Consolidation có ba nhịp:**
  - Sau mỗi lần ghi: Hindsight, Hy System 1, TencentDB.
  - Theo lịch hoặc khi idle: GBrain dream (31 phase), ai-memory, MemHub (evolve 03:00).
  - Gọi tường minh: Hy `evolve()`, Cognee improve.
- **Rủi ro cần để ý:**
  - ai-memory auto-improve bật mặc định khi có LLM provider và tự áp dụng thay đổi.
  - Subject gate của Hy coding tắt mặc định, nên có thể merge nhầm giữa các subject.
  - Không hệ nào hứa hẹn xoá vật lý.

## 3. Retrieval

Nguồn: [retrieval comparison](agent-memory-retrieval-comparison.md).

- **Đơn vị xếp hạng:**
  - Page: ai-memory, GBrain.
  - Fact/unit: Hindsight, Hy, Mem0.
  - Xếp theo page giảm trùng lặp ngữ cảnh. Xếp theo fact cho độ hạt mịn hơn khi inject.
- **Pipeline:**
  - Hindsight: 4 arm, RRF, cross-encoder trên top 300.
  - ai-memory: 6 stream nhân hệ số authority.
  - GBrain: pipeline dài, có mode bundle `conservative`, `balanced` và `tokenmax`.
  - Cognee: router regex chọn lane, 21 `SearchType`.
  - Mem0: semantic tạo candidate, BM25 và entity chỉ boost, nên điểm không so sánh được giữa các query.
- **Answer synthesis:** Hindsight `reflect` (agent loop 10 vòng), GBrain `think` (kèm gap analysis), ai-memory `answer=true` (từ chối nếu citation không rõ).
- **Tín hiệu suy giảm:** GBrain là hệ duy nhất có hợp đồng tường minh "kết quả rỗng không chứng minh trang không tồn tại".
- **Embedding mặc định:** ai-memory và Hindsight chạy được không cần cloud. GBrain, Hy SDK và Mem0 mặc định dùng cloud.
- **RAG và memory (Synthesis):**
  - Mem0 và Hy `lite` gần RAG cổ điển nhất.
  - Memory khác RAG ở bốn điểm: arm có cấu trúc, ưu tiên theo loại hoặc độ tin cậy, đọc dữ liệu đã hợp nhất, và lọc theo danh tính.
  - Wiki chưa có framework RAG chuyên dụng.

## 4. Tích hợp và vận hành

Nguồn: [integration và operations](agent-memory-integration-and-operations-comparison.md).

- **Cơ chế tích hợp:**
  - Library adapter: Hindsight, Mem0, Cognee.
  - MCP cộng instruction rules: GBrain, Hindsight, ai-memory.
  - Lifecycle hook: ai-memory, Hindsight coding-agents, MemHub.
  - Import transcript: MemHub, GBrain, Hindsight.
  - Proxy: TencentDB, Headroom.
  - Native provider: Hy.
- MCP một mình không đủ, vì agent hiếm khi tự gọi MCP server mà không có luật trong file instruction (Synthesis).
- **Tính năng cho coding agent:**
  - ai-memory: handoff claim-once và managed workstream.
  - Hy: diff chain.
  - Hindsight: bank theo repo.
  - Cognee và TencentDB: code graph.
  - GBrain: chunk AST.
- **Đổi embedding model:** GBrain, Hindsight, Hy (chỉ Chroma), MemHub và ai-memory có cơ chế riêng. Mem0, Cognee, TencentDB và Headroom không được wiki ghi nhận.
- **Vận hành:** chỉ GBrain (Minions) và Hindsight (`async_operations`) có job queue bền trên Postgres. ai-memory đơn giản nhất, chỉ cần một binary.

## 5. Bảo mật và quyền riêng tư

Nguồn: [security và privacy](agent-memory-security-and-privacy-comparison.md). Đây là static inspection, không có pentest, nên là điểm cần audit chứ không phải lỗ hổng đã khai thác.

- **Mặc định đáng lưu ý:**
  - Hindsight bind `0.0.0.0` và MCP mở.
  - Hy SDK server không có auth và CORS `*`.
  - TencentDB tắt bearer gate khi service key rỗng.
  - Headroom bật beacon mặc định.
  - Docker quick-start của ai-memory chưa có auth.
- **Isolation:**
  - Mem0: identifier không gắn với principal đã xác thực.
  - TencentDB: `assertIsolation` fallback về bucket mặc định.
  - ai-memory: user do proxy xác nhận bỏ qua grant `restricted`.
  - MemHub: không có ACL theo từng memory.
  - GBrain có mô hình grant chi tiết nhất, và tự liệt kê những gì không được ràng buộc.
- **Không mã hoá at-rest theo mặc định:** ai-memory, Headroom.
- **Prompt injection qua memory:** GBrain có 6 trust tier nhưng mặc định chỉ gắn cờ, không chặn. ai-memory rào inbox là untrusted. Với Mem0, Cognee, TencentDB và Headroom, wiki không ghi nhận cơ chế riêng.
- Trang này có checklist audit 8 điểm.

## 6. Benchmark

Nguồn: [benchmarks comparison](agent-memory-benchmarks-comparison.md). Tất cả đều là **Reported**, và wiki không chạy lại con số nào.

- **Kết luận chính: không xếp hạng chéo được.** Metric, split, judge và harness đều khác nhau.
- Bốn con số khoảng 94–95% trên LongMemEval đo bốn thứ khác nhau:
  - ai-memory đo hit@5.
  - GBrain đo `recall_all@5`.
  - Hindsight và Mem0 đo QA accuracy.
- Số của Mem0 là của managed platform, không phải bản OSS.
- **Mức tái lập từ repo:**
  - Cao: ai-memory (harness có commit và sha256 dataset), Headroom (phạm vi hẹp).
  - Trung bình: Hindsight, Cognee, Hy (CMB).
  - Thấp: GBrain, Mem0, TencentDB.
- CMB là benchmark duy nhất trong wiki đo *task resolved* cho coding agent, nhưng do Hy tự công bố.

## 7. Gợi ý chọn (Synthesis)

Nguồn: [landscape survey](agent-memory-landscape-survey.md), mục "Gợi ý chọn theo kịch bản".

| Kịch bản | Lựa chọn | Cần kiểm tra |
|---|---|---|
| SaaS memory cho từng người dùng, muốn managed option | Mem0 | Tự làm isolation ở server |
| GraphRAG trên tài liệu và code | Cognee | Chi phí `cognify`, quyền của prune |
| Agent học và suy luận, đội quen Postgres | Hindsight | Đóng MCP, bind lại |
| Cá nhân hoá chat sâu | Hy SDK | Tự gọi `evolve()`, server không có auth |
| Một người dùng nhiều coding agent, local, không cần key | ai-memory | Auto-improve tự áp dụng |
| Memory chung trên máy cá nhân cho nhiều app AI | MemHub | Bản preview, chưa hỗ trợ Windows |
| Second brain nhiều nguồn, cần provenance | GBrain | DB không bị ràng buộc bởi grant |
| Đội agent trên hạ tầng Tencent Cloud | TencentDB | Audit isolation và auth trước khi expose |
| Giảm token | Headroom, dùng kèm hệ khác | Tắt beacon nếu cần |

## 8. Mâu thuẫn đã ghi trong wiki

Các mâu thuẫn dưới đây được giữ nguyên, wiki không chọn bên nào. Nguồn: [benchmarks comparison](agent-memory-benchmarks-comparison.md), mục Contradictions.
- BEAM 10M: blog Hindsight ghi hạng nhì là 40.6 ("Honcho"), còn README Mem0 ghi platform của Mem0 đạt 48.6.
- Mem0: README ghi 92.5 / 94.4, migration guide ghi 91.6 / 93.4.
- Mâu thuẫn doc/code, ghi trong [retrieval comparison](agent-memory-retrieval-comparison.md) và [security comparison](agent-memory-security-and-privacy-comparison.md):
  - Mem0: README nói ba tín hiệu chấm song song, code gọi tuần tự.
  - Hindsight: docstring nhắc MMR nhưng code không có.
  - Headroom: doc nói beacon không chứa gì suy ra từ body, nhưng code gửi các trường cấu trúc.

## Giới hạn

- **Đây là bản tổng hợp từ các trang Synthesis, không phải kiểm chứng.** Evidence class chủ yếu là Observed (static inspection do subagent thực hiện), Reported (benchmark) và Synthesis. Wiki chưa có lần chạy thực nào.
- **Dữ liệu sẽ cũ.** Version, default và danh sách provider là thông tin phụ thuộc thời gian. Cụm này hết hạn kiểm tra từ 2027-02-06.
- **Khoảng trống trong wiki:**
  - Chưa có Zep/Graphiti, Letta, LangMem, MemOS, OpenViking.
  - Chưa có framework RAG chuyên dụng.
  - Các trang CI/release/contributor chưa được tổng hợp chéo.
  - Một số hệ thiếu thông tin cho vài chiều: TencentDB, Headroom, Mem0 và Cognee về observability, embedding migration, provider.
- **Chưa xác minh với raw.** Nếu bạn cần con số hoặc locator cụ thể, tôi sẽ mở `raw/` để kiểm tra.
