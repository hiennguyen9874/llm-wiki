# User-supplied Sparse Attention evolution map

This file preserves the Mermaid architecture map supplied by the user on 2026-08-27. It is a conceptual synthesis, not an independent primary-source record.

```mermaid
flowchart TD
    A[Dense full attention<br/>Mỗi query đọc toàn bộ prefix<br/>Chi phí attention tăng bậc hai]
    subgraph S1[Giai đoạn 1 — Sparse pattern cố định]
        B1[Local / Sliding-window<br/>Chỉ đọc vùng gần]
        B2[Strided / Dilated<br/>Đọc theo khoảng cách định sẵn]
        B3[Local + Global / Sink<br/>Cửa sổ gần + token toàn cục]
        B4[Block-sparse mask<br/>Bỏ qua các score block bị mask]
    end
    subgraph S2[Giai đoạn 2 — Learned content-based retrieval]
        C[DeepSeek Sparse Attention — DSA<br/>Indexer học score từng token<br/>Chọn token-level top-k<br/>Core MLA / MQA]
    end
    subgraph S3[Giai đoạn 3 — Tối ưu locality bằng pooling]
        D1[Qwen Sparse Attention — QSA<br/>Mean-pool mỗi 4 token<br/>Chọn tối đa 512 block<br/>Mở thành ≤ 2.048 token<br/>Core causal GQA]
        D2[GLM pooled DSA<br/>Learned pooling mỗi 4 token<br/>Chọn block rồi mở về token<br/>Core MLA / DSA]
    end
    subgraph S4[Giai đoạn 4 — Giảm overhead của indexer]
        E[LongCat Sparse Attention — LSA<br/>Sink + sliding window<br/>+ dynamic distant tokens<br/>Cross-layer index reuse<br/>Hierarchical page → token selection]
    end
    subgraph S5[Giai đoạn 5 — Sparse retrieval kết hợp KV compression]
        F1[DeepSeek-V4 CSA<br/>Nén nhóm token thành entry<br/>Sparse top-k trên compressed entries<br/>+ local uncompressed window]
        F2[DeepSeek-V4 HCA<br/>Nén mạnh hơn<br/>Dense attention trên ít entries<br/>+ local uncompressed window]
    end
    subgraph H[Nhánh kiến trúc hybrid]
        G1[Fixed-state recurrent memory<br/>Gated DeltaNet / KDA]
        G2[Periodic sparse attention<br/>Khôi phục global token retrieval]
        G3[Hybrid long-context backbone<br/>Phần lớn layer dùng state cố định<br/>Một số layer đọc token chọn lọc]
    end
    A --> B1
    A --> B2
    A --> B3
    A --> B4
    B3 --> C
    B4 --> C
    C -->|Giảm truy cập KV rời rạc| D1
    C -->|Pooling học được| D2
    C -->|Tối ưu trực tiếp DSA| E
    D1 -. Hội tụ ở block 4 token .-> D2
    D1 -. Locality tốt hơn token top-k .-> E
    D2 -. Pooled selection .-> E
    C -->|Thêm nén representation| F1
    D1 -. Block retrieval + compression .-> F1
    F1 -->|Tăng compression ratio| F2
    G1 --> G3
    D1 --> G2
    D2 --> G2
    E --> G2
    F1 --> G2
    G2 --> G3
    classDef baseline fill:#e5e7eb,stroke:#374151,color:#111827;
    classDef fixed fill:#dbeafe,stroke:#2563eb,color:#172554;
    classDef learned fill:#fef3c7,stroke:#d97706,color:#451a03;
    classDef pooled fill:#dcfce7,stroke:#16a34a,color:#052e16;
    classDef advanced fill:#f3e8ff,stroke:#9333ea,color:#3b0764;
    classDef hybrid fill:#ffe4e6,stroke:#e11d48,color:#4c0519;
    class A baseline;
    class B1,B2,B3,B4 fixed;
    class C learned;
    class D1,D2 pooled;
    class E,F1,F2 advanced;
    class G1,G2,G3 hybrid;
```
