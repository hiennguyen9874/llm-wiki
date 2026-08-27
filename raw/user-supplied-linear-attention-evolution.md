# User-supplied linear attention evolution map

- **Provenance:** User-provided Mermaid diagram in chat.
- **Captured:** 2026-08-27.
- **Scope:** Conceptual comparison of linear-attention mechanisms from additive fixed-state memory through delta-rule, channel-wise decay, and decoupled erase/write.
- **Evidence boundary:** This artifact preserves the supplied conceptual map. It does not independently establish publication chronology, exact equations, benchmark rankings, or the detailed implementations of RetNet and GLA.

```mermaid
flowchart TD
LA[Linear Transformer<br/>additive fixed-state memory]
FWP[Fast-Weight Programmer<br/>diễn giải linear attention như associative memory]
DPFP[DPFP<br/>feature map tăng capacity]
RET[RetNet / Retention<br/>decay theo thời gian]
GLA[Gated Linear Attention<br/>data-dependent element-wise decay]
DN[DeltaNet<br/>key-addressed corrective update]
GDN[Gated DeltaNet<br/>delta rule + scalar decay]
KDA[Kimi Delta Attention — KDA<br/>delta rule + channel-wise decay]
GDN2[Gated DeltaNet-2<br/>channel-wise decay<br/>+ erase/write tách rời]

LA --> FWP
LA --> DPFP
LA -. thêm decay .-> RET
LA -. learned gating .-> GLA
FWP -->|thêm delta correction| DN
DN -->|thêm scalar forgetting gate| GDN
GDN -->|scalar → channel-wise decay| KDA
KDA -->|tách erase gate và write gate| GDN2
GLA -. gating/decay ảnh hưởng<br/>hướng phát triển .-> GDN

classDef base fill:#e8f1ff,stroke:#2563eb,color:#111;
classDef delta fill:#ecfdf5,stroke:#059669,color:#111;
classDef adjacent fill:#fff7ed,stroke:#ea580c,color:#111;
class LA,FWP base;
class DN,GDN,KDA,GDN2 delta;
class DPFP,RET,GLA adjacent;
```