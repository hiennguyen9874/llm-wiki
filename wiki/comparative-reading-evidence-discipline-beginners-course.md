---
type: Synthesis
title: "Comparative reading và evidence discipline — khóa học cho người mới"
description: A beginner-first course for comparing frontier-model designs on matched dimensions, building an evidence ledger, and avoiding causal claims unsupported by ablations or comparable workloads.
tags: [frontier-model, comparative-reading, evidence-discipline, evaluation, ablation, deepseek-v3, kimi-linear, kimi-k3, learning-roadmap]
status: stable
created: 2026-08-12
generated:
  by: llm-wiki-agent/1
  at: 2026-08-12T14:15:44+07:00
sources:
  - id: deepseek-v3-2024
    resource: ../raw/arXiv-2412.19437v2/main.tex
    title: DeepSeek-V3 Technical Report
  - id: kimi-linear-2025
    resource: ../raw/arXiv-2510.26692v2/main.tex
    title: "Kimi Linear: An Expressive, Efficient Attention Architecture"
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
  - id: brown-gpt-3-2020-v4
    resource: ../raw/arXiv-2005.14165v4/main.tex
    title: Language Models are Few-Shot Learners
---

# Comparative reading và evidence discipline — khóa học cho người mới

So sánh frontier model đúng cách không phải là đặt nhiều benchmark scores cạnh nhau rồi chọn số lớn nhất. Ta phải **khóa dimension đang so sánh**, mô tả khác biệt về `memory addressability`, `state growth`, `active/total parameters`, `positional handling`, `training cost` và `serving workload`, rồi gắn mỗi kết luận với đúng loại evidence. Một `component ablation` có thể hỗ trợ claim về component trong setup đã kiểm soát; một `whole-model result` thường chỉ cho thấy toàn bộ system hoạt động tốt trong setup đó, không chứng minh component mới là nguyên nhân. Bài này là pedagogical synthesis cho Stage 9.5 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md), sử dụng DeepSeek-V3, Kimi Linear và Kimi K3 làm case study.[^deepseek-v3-2024][^kimi-linear-2025][^kimi-k3-2026]

> [!success] Learning outcomes
> Sau bài này, bạn có thể:
> - phân biệt `mechanism claim`, `empirical claim` và `causal claim`;
> - tạo một `comparison matrix` với các dimension matched;
> - lập `evidence ledger` ghi rõ source, control, workload và limitation;
> - phân biệt `component ablation` với `whole-model correlation`;
> - nhận ra khi `latency`, `throughput`, `cost`, `context length` hoặc benchmark không comparable;
> - dùng ngôn ngữ scoped như “the report shows” thay vì biến author-reported evidence thành universal fact;
> - chạy một Python mini-lab để lint các claim thiếu control hoặc workload metadata;
> - viết deliverable một trang chỉ chứa claims mà evidence thực sự hỗ trợ.

## 1. Vì sao comparative reading khó?

Một frontier model là một **bundle of changes**:

```text
architecture
+ data
+ tokenizer
+ training objective
+ optimizer and numerical format
+ distributed system
+ context-extension recipe
+ post-training
+ inference effort and tools
+ evaluation harness
= observed whole-model result
```

Nếu model B có benchmark score cao hơn model A, ta chỉ quan sát:

$$
Y_B > Y_A,
$$

trong đó $Y$ là outcome cuối cùng. Ta chưa biết phần chênh lệch đến từ architecture, data, scale, post-training, tool use hay harness. Viết “mechanism X làm B tốt hơn A” là thêm một causal conclusion mà observation trên chưa cung cấp.

### 1.1 Ba loại claim phải tách riêng

| Claim type | Ví dụ | Evidence tối thiểu phù hợp |
|---|---|---|
| `Mechanism` | “MLA cache một compressed latent cho mỗi token.” | equation, architecture specification hoặc code path |
| `Empirical` | “Trong benchmark setup này, variant A đạt score cao hơn B.” | result table kèm metric và setup |
| `Causal` | “Thay X bằng Y gây ra improvement.” | controlled intervention/ablation giữ các yếu tố quan trọng khác gần như fixed |

Một equation có thể chứng minh state **shape**, nhưng không chứng minh quality. Một benchmark có thể chứng minh reported score, nhưng không tự chứng minh nguyên nhân. Một microbenchmark có thể đo kernel, nhưng không tự chứng minh end-to-end serving cost.

> [!warning] Quy tắc quan trọng nhất
> Evidence chỉ được “nâng” lên claim mạnh hơn khi design của experiment cho phép. Không được đi từ `whole-model correlation` đến `component causation` chỉ bằng cách kể một câu chuyện hợp lý.

## 2. Vocabulary nền tảng về evidence

### 2.1 `Baseline`, `control` và `treatment`

- `baseline`: system làm mốc so sánh;
- `control`: setup không nhận thay đổi đang kiểm tra;
- `treatment`: setup nhận thay đổi;
- `controlled variable`: yếu tố được giữ giống nhau;
- `confounder`: yếu tố thay đổi cùng treatment và có thể ảnh hưởng outcome.

Ví dụ, nếu hai model khác cả attention, position method, kernel và data, cả bốn đều là candidate confounders đối với quality hoặc speed.

### 2.2 `Ablation` không phải lúc nào cũng đủ mạnh

Một ablation tốt thường trả lời:

> Khi chỉ thay component X trong cùng scale, data, training budget, optimizer và evaluation harness, metric thay đổi thế nào?

Nhưng trên thực tế có nhiều mức:

| Evidence design | Điều có thể nói | Điều chưa thể nói |
|---|---|---|
| Equation/complexity analysis | shape, asymptotic state hoặc operation count | wall-clock speed và quality |
| Unit/component test | component chạy đúng trong test | whole-model benefit |
| Controlled small-scale ablation | effect trong tested scale/recipe | frontier-scale effect chắc chắn giống hệt |
| Matched full-model comparison | effect của full design bundle trong matched setup | effect riêng của từng coupled change |
| End-to-end benchmark | system outcome trong harness | architecture là nguyên nhân duy nhất |
| Selected case study | capability có thể xảy ra | population reliability hoặc average success rate |

DeepSeek-V3 có FP8-versus-BF16 ablations ở model nhỏ hơn full V3; chúng hỗ trợ numerical behavior trong setup thử nghiệm, không tự chứng minh identical frontier-scale behavior hay portability sang hardware khác.[^deepseek-v3-2024] Kimi Linear có matched 48B comparisons nhưng attention mechanism, positional treatment và kernels thay đổi cùng nhau, nên evidence mạnh cho **full Kimi Linear design**, yếu hơn cho từng phần riêng lẻ.[^kimi-linear-2025]

### 2.3 `Author-reported`, `independent` và `reproduced`

- `author-reported`: nhóm tạo model tự chạy hoặc công bố result;
- `third-party`: bên khác chạy result, nhưng setup có thể vẫn khác;
- `independently reproduced`: bên khác tái tạo cùng claim với đủ artifact và setup tương đương.

`Author-reported` không có nghĩa là sai. Nó có nghĩa là provenance và verification level phải hiện rõ. Cũng không nên gọi leaderboard snapshot là reproduction nếu model, harness, prompt hoặc date khác.

### 2.4 `Missing evidence` không phải evidence of failure

Nếu paper không có ablation cho X, kết luận đúng là:

> “Causal contribution of X is not isolated in the available evidence.”

Không được đổi thành “X không có tác dụng”. `Unknown` khác `false`.

## 3. Sáu dimension phải khóa trước khi so sánh

## 3.1 `Memory addressability`

Hỏi: query đọc history theo cách nào?

### Token-addressable memory

Softmax attention giữ một representation cho từng token. Query có thể tạo score riêng cho từng slot:

$$
A(q,K,V)=\operatorname{softmax}\left(\frac{qK^T}{\sqrt d}\right)V.
$$

MLA vẫn thuộc nhóm này: nó giảm representation được cache **mỗi token**, nhưng không xóa token slots. DeepSeek-V3 dùng MLA trong attention layers; state vẫn tăng theo context.[^deepseek-v3-2024]

### Fixed-state associative memory

KDA gộp history vào recurrent matrix $S_t$ có shape không tăng theo token count. Query đọc state đã superpose associations, thay vì chấm từng token slot. Kimi Linear và Kimi K3 dùng KDA ở phần lớn sequence-mixing layers, nhưng chèn periodic MLA để khôi phục global token-addressable retrieval.[^kimi-linear-2025][^kimi-k3-2026]

| Architecture | Addressability | Interpretation đúng |
|---|---|---|
| DeepSeek-V3 MLA | token-addressable ở attention layers | compressed per-token cache |
| Kimi Linear | hybrid fixed-state KDA + periodic token-addressable MLA | không phải pure fixed-state model |
| Kimi K3 | hybrid KDA + Gated MLA, thêm depth retrieval qua AttnRes | nhiều memory axes cùng tồn tại |

Không được viết “KDA tốt hơn MLA” nếu chưa nêu workload và criterion. KDA ưu tiên bounded recurrent state; MLA giữ direct token retrieval. Hai design giải trade-off khác nhau.

## 3.2 `State growth`

Hãy lập ledger theo axis tăng trưởng:

| State | Tăng theo | Câu hỏi |
|---|---|---|
| KV/latent cache | sequence length $T$ | có entry cho mỗi token không? |
| Recurrent state | head dimensions | state có fixed shape theo $T$ không? |
| AttnRes cache | depth blocks | giữ bao nhiêu representation qua depth? |
| Expert weights | total experts | active sparsity có giảm resident weights không? |
| Activations | batch, sequence, depth | training có recompute/offload không? |

Với Kimi Linear, `3 KDA : 1 MLA` có nghĩa là KDA state không tăng theo $T$, nhưng MLA layers vẫn append token state. Claim “up to 75% KV-cache reduction” là relative claim so với full-MLA layer allocation trong reported design, không phải “75% total serving memory reduction”.[^kimi-linear-2025]

Kimi K3 cũng không có constant-size end-to-end context state: KDA fragments fixed-size nhưng 24 MLA layers, activations, tool history và prefill work vẫn tăng theo sequence.[^kimi-k3-2026]

## 3.3 `Active parameters` và `total parameters`

Với MoE:

- `total parameters`: toàn bộ expert pool và model weights;
- `active parameters`: subset được dùng cho một token/forward path;
- `resident memory`: weights thực sự phải có trên deployment unit;
- `communication`: dispatch/combine giữa devices;
- `utilization`: mức độ expert GEMMs dùng hardware hiệu quả.

Case-study configurations được report:

| Model | Total parameters | Activated parameters | Chỉ nên dùng để kết luận |
|---|---:|---:|---|
| DeepSeek-V3 | 671B | 37B/token | configuration của V3 |
| Kimi Linear comparison model | 48B | 3B/token | reported Kimi Linear experiment scale |
| Kimi K3 | 2.78T | 104.2B/token | configuration của K3 |

Các hàng này **không phải matched quality comparison**. Scale, architecture, data, date và training recipe khác nhau. `Active parameters` thấp hơn cũng không tự suy ra latency thấp hơn vì total-weight memory, expert parallel all-to-all, batch size và topology vẫn ảnh hưởng.[^deepseek-v3-2024][^kimi-linear-2025][^kimi-k3-2026]

## 3.4 `Positional handling`

Position method phải được so cùng sequence mixer:

- DeepSeek-V3 MLA có decoupled rotary path; context extension từ 4K lên 32K rồi 128K dùng YaRN trên rotary key path.[^deepseek-v3-2024]
- Kimi Linear dùng NoPE trong MLA layers và giao positional/recency behavior cho KDA. Report so sánh full Kimi Linear design với RoPE variant ở long-context setup, nhưng đây không phải isolated experiment cho mọi position method.[^kimi-linear-2025]
- Kimi K3 tiếp tục dùng KDA cho position-sensitive recurrence và NoPE Gated MLA; report nêu context đến 1M, nhưng context support không đồng nghĩa reliable use của mọi token ở mọi task.[^kimi-k3-2026]

> [!warning] Một lỗi phổ biến
> “NoPE hỗ trợ context dài hơn RoPE” là claim quá rộng. Evidence chỉ hỗ trợ behavior của architecture + training recipe cụ thể. NoPE không tự tạo positional understanding; trong Kimi designs, KDA mang phần trách nhiệm đó.

## 3.5 `Training cost`

Một training-cost number chỉ comparable khi ít nhất các yếu tố sau gần nhau:

- model shape và activated compute;
- token count, sequence-length curriculum và modalities;
- hardware generation, quantity và utilization;
- numerical format;
- checkpoint/recompute policy;
- included/excluded research runs, ablations và failures.

DeepSeek-V3 report 2.788M H800 GPU-hours cho pretraining, context extension và post-training, đồng thời nói estimate không gồm earlier research/ablations.[^deepseek-v3-2024] Đây là cost boundary cho stack đó, không phải universal price của architecture MLA/MoE.

Kimi K3’s approximately $2.5\times$ scaling-efficiency claim dựa trên fitted held-out loss và bundle architecture, data, optimizer, schedule. Không thể phân bổ toàn bộ gain cho KDA, AttnRes hay Stable LatentMoE riêng lẻ.[^kimi-k3-2026]

## 3.6 `Serving workload`

Mọi speed claim phải đi kèm workload card:

```text
phase: prefill | decode | end-to-end
batch/concurrency: ?
prompt length: ?
output length: ?
hardware/topology: ?
dtype/quantization: ?
cache policy: ?
kernel/runtime: ?
metric: latency | throughput | TTFT | TPOT | cost/request
```

Kimi Linear report ở batch 1 và 1M-token context khoảng $2.9\times$ prefill và $2.2\times$ decode improvement so với MLA trong setup của report. Một maximum-throughput setup dùng memory tiết kiệm được để tăng batch và report $6.3\times$. Hai con số trả lời hai câu hỏi khác nhau; không được gọi $6.3\times$ là batch-one latency speedup.[^kimi-linear-2025]

DeepSeek-V3 report end-to-end generation nhanh hơn V2 hơn hai lần trong deployment của nhóm, nhưng setup không thiết lập một general serving comparison; stated deployment còn dùng unit rất lớn.[^deepseek-v3-2024]

Kimi K3 có hybrid prefix caching, external CPU cache, workload-aware admission và nhiều production policies. Các measurement đó phụ thuộc request mix và infrastructure; không thể quy trực tiếp về KDA equation.[^kimi-k3-2026]

## 4. Comparison matrix: so design, không xếp hạng model

Bảng dưới là **documented architecture comparison**. Nó không phải leaderboard.

| Dimension | DeepSeek-V3 | Kimi Linear | Kimi K3 | Comparability note |
|---|---|---|---|---|
| Sequence mixer | MLA ở attention path | pattern 3 KDA : 1 MLA | 69 KDA + 24 Gated MLA | khác scale và generation |
| Memory addressability | token-addressable compressed cache | hybrid fixed-state + token-addressable | hybrid sequence memory + token retrieval | mechanism comparison hợp lệ |
| Context-state growth | compressed cache tăng theo $T$ qua MLA layers | KDA fixed theo $T$; periodic MLA tăng theo $T$ | KDA fixed theo $T$; MLA tăng theo $T$; AttnRes thêm depth state | không model nào ở đây chứng minh free long context |
| Positional handling | decoupled RoPE + YaRN extension | KDA position/recency; NoPE MLA | KDA position/recency; NoPE Gated MLA | coupled với architecture/training |
| Sparse FFN | fine-grained DeepSeekMoE; top-8 routed + shared expert | reported 48B/3B MoE comparison model | Stable LatentMoE; top-16/896 + 2 shared | expert shape/routing khác nhau |
| Active/total params | 37B/671B | 3B/48B experiment | 104.2B/2.78T | không dùng để rank quality |
| Distinctive systems | DualPipe, custom all-to-all, FP8 | chunkwise KDA/recurrent decode; measured hybrid kernels | KDA context parallelism, MoonEP, hybrid cache, persistent agent runtime | workload/hardware phụ thuộc mạnh |
| Evidence strength nổi bật | architecture spec, smaller FP8/routing ablations, author evaluation | matched same-scale attention-design comparisons và ratio ablation | broad integrated report, scaling curves, infrastructure evidence | không có một three-way matched experiment |
| Major causal gap | full V3 gain không isolate scale/data/MLA/routing/MTP/systems | full design couples KDA, NoPE treatment và kernels | headline gain bundles architecture/data/optimizer/schedule | causal gaps phải xuất hiện trong conclusion |

### 4.1 Kết luận nào bảng này hỗ trợ?

**Supported:**

- DeepSeek-V3 giảm per-token KV representation bằng MLA nhưng giữ token-addressable attention.
- Kimi Linear và Kimi K3 dùng hybrid fixed-state/token-addressable design.
- Cả ba đều dùng sparse expert capacity nhưng configuration và systems controls khác nhau.
- Serving implications phụ thuộc architecture **và** runtime implementation.

**Không supported:**

- Kimi K3 architecture “tốt hơn” DeepSeek-V3 vì context window dài hơn.
- KDA là nguyên nhân Kimi Linear/K3 có benchmark quality cao.
- Model có activated-parameter ratio nhỏ hơn chắc chắn rẻ hoặc nhanh hơn.
- NoPE universally extrapolates tốt hơn RoPE.
- Một author-reported end-to-end speedup sẽ giữ nguyên trên hardware khác.

## 5. Evidence ledger: từ source đến scoped claim

Một evidence ledger tốt không chỉ lưu citation. Nó lưu **claim boundary**.

| Field | Câu hỏi phải trả lời |
|---|---|
| `claim` | chính xác điều gì đang được nói? |
| `claim_type` | mechanism, empirical hay causal? |
| `source` | report, code, benchmark hay third-party result nào? |
| `evidence_design` | equation, ablation, matched run, benchmark, case study? |
| `control` | baseline nào và yếu tố nào được giữ fixed? |
| `workload` | phase, length, batch, hardware, harness, tools? |
| `result` | metric và direction/size của effect? |
| `limitations` | confounders, missing artifacts, uncertainty? |
| `allowed_wording` | câu mạnh nhất evidence cho phép là gì? |
| `forbidden_leap` | causal/universal inference nào cần tránh? |

### 5.1 Worked example: Kimi Linear ratio ablation

| Field | Entry |
|---|---|
| `claim` | 3:1 KDA:MLA ratio có validation perplexity thấp nhất trong ratios được report |
| `claim_type` | empirical, component-allocation ablation |
| `evidence_design` | controlled ratio sweep trong recipe của report |
| `result` | 3:1 đạt 5.65; 1:1 đạt 5.66; 7:1 đạt 5.70; 15:1 đạt 5.82; full MLA đạt 5.77 |
| `allowed_wording` | “3:1 was best among the reported variants in this setup.” |
| `forbidden_leap` | “3:1 is the universally optimal hybrid ratio.” |

Evidence này khá trực tiếp cho allocation trong setup, nhưng không chứng minh optimum ở scale, data hoặc hardware khác.[^kimi-linear-2025]

### 5.2 Worked example: Kimi K3 scaling efficiency

| Field | Entry |
|---|---|
| `claim` | report attributes about $2.5\times$ scaling-efficiency improvement over K2 to combined changes |
| `claim_type` | empirical whole-system claim |
| `evidence_design` | fitted held-out validation-loss curves, bundled intervention |
| `control` | previous-generation model family; nhiều yếu tố đổi cùng lúc |
| `allowed_wording` | “The report associates the combined K3 architecture, data, and recipe with the fitted improvement.” |
| `forbidden_leap` | “KDA alone caused a $2.5\times$ gain.” |

### 5.3 Worked example: DeepSeek-V3 benchmarks

DeepSeek-V3 chat results dùng author-run evaluation cho nhiều open models và API-mediated results cho proprietary models, dưới output cap được report. Ledger phải ghi harness/source khác nhau. Allowed wording là “the report gives V3 score X under its setup”, không phải “independent evaluation proves V3 is better”.[^deepseek-v3-2024]

## 6. Causal reasoning cho người mới

### 6.1 Counterfactual question

Một causal claim về component X ngầm hỏi:

> Cùng model này, nếu chỉ không dùng X mà giữ các yếu tố khác fixed, outcome sẽ thay đổi thế nào?

Ký hiệu đơn giản:

$$
\text{effect of }X = Y(X=1)-Y(X=0).
$$

Ta không thể quan sát cả hai trạng thái trên đúng cùng training run, nên cần controlled experiments với random seeds, matched budgets và uncertainty. Frontier reports thường không thể kiểm soát hoàn hảo mọi biến vì chi phí lớn; do đó wording phải phản ánh design thực tế.

### 6.2 Confounder map

Trước khi gán causality, vẽ graph tối giản:

```text
architecture ─┐
data ─────────┤
scale ────────┤
optimizer ────┼──> benchmark result
post-training ┤
test-time compute ┤
tools/harness ┘
```

Nếu treatment model thay đổi nhiều incoming edges, benchmark delta không isolate architecture.

### 6.3 Khi nào dùng từ `caused`, `improved`, `enabled`?

- `caused`: chỉ dùng khi intervention và controls đủ mạnh;
- `improved`: luôn thêm “in the reported setup” nếu evidence scope hẹp;
- `enabled`: thích hợp khi mechanism là điều kiện kỹ thuật trực tiếp, nhưng tránh suy ra outcome rộng;
- `associated with`: dùng cho bundle/observational result;
- `the authors attribute`: dùng khi source nêu causal interpretation nhưng evidence chưa isolate;
- `may`, `is intended to`, `motivates`: dùng cho design rationale hoặc synthesis.

> [!example] Rewrite claim
> Quá mạnh: “KDA makes Kimi K3 scale 2.5× better.”
>
> Scoped: “Kimi K3’s report associates an approximately 2.5× fitted scaling-efficiency improvement with the combined architecture, data, and training recipe; it does not isolate KDA’s contribution.”

## 7. Benchmark và evaluation discipline

### 7.1 Match `task`, `metric`, `harness` và `effort`

Hai score chỉ comparable khi ta kiểm tra:

- benchmark version và split;
- prompt/template;
- decoding parameters;
- output-token budget;
- `pass@1`, `pass@k`, exact match hay judge score;
- tools, retrieval, code execution hoặc browser;
- test-time effort/sampling budget;
- model checkpoint và date;
- contamination handling.

Kimi K3 report dùng max-effort settings, benchmark-specific agent harnesses và Python tools cho một số vision tasks. Những result đó đo `model + effort + tools + harness`, không chỉ frozen architecture.[^kimi-k3-2026]

### 7.2 Contamination và evaluation adaptation

Web-scale pretraining có thể overlap benchmark. GPT-3 report từng phát hiện filtering bug, dùng n-gram overlap và clean-subset analysis, đồng thời bỏ một số benchmark gần như overlap hoàn toàn.[^brown-gpt-3-2020-v4] Bài học tổng quát:

- không thấy detected overlap không chứng minh benchmark sạch;
- overlap không tự chứng minh memorization;
- clean subset có thể nhỏ hoặc khác difficulty;
- internal benchmark được refresh vẫn có evaluation-adaptation risk nếu nó định hướng training.

### 7.3 Case study không phải reliability estimate

Một selected trajectory chứng minh model **có thể** thành công trong trường hợp đó. Nó không cho biết success rate trên population. Muốn claim reliability cần sample protocol, denominator, failure accounting và uncertainty.

## 8. Python mini-lab: lint một evidence ledger

Lab dưới đây không quyết định scientific truth. Nó buộc người viết điền metadata trước khi phát biểu causal hoặc speed claim.

```python
from dataclasses import dataclass, field
from typing import Literal, Optional

ClaimType = Literal["mechanism", "empirical", "causal"]
EvidenceDesign = Literal[
    "specification", "complexity", "ablation",
    "matched_run", "benchmark", "case_study"
]

@dataclass
class Workload:
    phase: Optional[str] = None       # training, prefill, decode, end-to-end
    context: Optional[int] = None
    batch: Optional[int] = None
    hardware: Optional[str] = None
    harness: Optional[str] = None
    tools: Optional[str] = None

@dataclass
class Evidence:
    claim: str
    claim_type: ClaimType
    design: EvidenceDesign
    source: str
    control: Optional[str] = None
    matched_fields: list[str] = field(default_factory=list)
    workload: Workload = field(default_factory=Workload)
    limitations: list[str] = field(default_factory=list)
    independent: bool = False


def lint(e: Evidence) -> list[str]:
    issues = []

    if e.claim_type == "causal":
        if e.design not in {"ablation", "matched_run"}:
            issues.append("causal claim lacks intervention-style evidence")
        if not e.control:
            issues.append("causal claim has no explicit control")
        required = {"scale", "data", "training_budget", "evaluation"}
        missing = required - set(e.matched_fields)
        if missing:
            issues.append(f"causal comparison does not mark matched: {sorted(missing)}")

    speed_words = {"latency", "throughput", "faster", "speedup", "cost"}
    if any(word in e.claim.lower() for word in speed_words):
        if not e.workload.phase:
            issues.append("performance claim lacks phase")
        if e.workload.context is None:
            issues.append("performance claim lacks context length")
        if e.workload.batch is None:
            issues.append("performance claim lacks batch/concurrency")
        if not e.workload.hardware:
            issues.append("performance claim lacks hardware")

    if e.design in {"benchmark", "case_study"} and e.claim_type == "causal":
        issues.append("benchmark/case study alone cannot isolate component causality")

    if not e.limitations:
        issues.append("no evidence limitation recorded")

    return issues
```

### 8.1 Một claim cố tình viết quá mạnh

```python
bad = Evidence(
    claim="KDA caused Kimi K3 to be faster and better.",
    claim_type="causal",
    design="benchmark",
    source="Kimi K3 report",
)

print(*lint(bad), sep="\n- ")
```

Expected warnings gồm thiếu intervention, control, matched fields, workload và limitations.

### 8.2 Một performance claim được scope tốt hơn

```python
good = Evidence(
    claim=(
        "Kimi Linear reported lower batch-one decode latency than MLA "
        "in its 1M-token setup."
    ),
    claim_type="empirical",
    design="matched_run",
    source="Kimi Linear report",
    control="reported full-MLA model",
    matched_fields=["scale", "data", "training_budget", "evaluation"],
    workload=Workload(
        phase="decode",
        context=1_000_000,
        batch=1,
        hardware="report-specific; not fully disclosed in text",
        harness="author runtime",
    ),
    limitations=[
        "author-reported",
        "hardware details insufficient for portability",
        "full designs couple attention, position handling, and kernels",
    ],
)

print(lint(good))  # [] under these simple structural rules
```

`[]` chỉ có nghĩa ledger đủ field theo lint rule, không có nghĩa claim đã independently verified.

### 8.3 Optional: kiểm tra comparability của hai runs

```python
def comparable(a: Evidence, b: Evidence) -> tuple[bool, list[str]]:
    gaps = []
    for name in ["phase", "context", "batch", "hardware", "harness", "tools"]:
        va = getattr(a.workload, name)
        vb = getattr(b.workload, name)
        if va != vb:
            gaps.append(f"{name}: {va!r} != {vb!r}")
    return not gaps, gaps
```

Trong dự án thật, nên thêm `dtype`, prompt/output lengths, concurrency, runtime version, checkpoint, benchmark revision và sampling effort.

## 9. Workflow đọc paper theo từng pass

### Pass 1 — Claim inventory

Highlight riêng:

- architecture specification;
- complexity/memory claims;
- quality results;
- systems measurements;
- author interpretation;
- limitations và missing artifacts.

Không ghi “model tốt” ở pass này.

### Pass 2 — Normalize units và dimensions

Đưa mọi model về cùng vocabulary:

```text
addressability
state growth
active/total parameters
position method
training budget
serving workload
evaluation setup
```

Nếu một cell chưa có thông tin, ghi `not reported`, không đoán.

### Pass 3 — Build evidence ledger

Mỗi material claim phải có source và limitation. Tách một row cho batch-one latency và một row cho maximum throughput; đừng trộn hai regimes.

### Pass 4 — Search for controls

Tìm:

- same-scale ablation;
- same-token training run;
- same optimizer/data;
- component ratio sweep;
- kernel microbenchmark;
- end-to-end serving baseline;
- independent reproduction.

Nếu control nhỏ hơn frontier model, ghi rõ extrapolation gap.

### Pass 5 — Draft scoped conclusions

Dùng format:

> **Documented:** source report specifies/result X under setup Y.  
> **Synthesis:** this suggests trade-off Z when constraint C matters.  
> **Unknown:** contribution Q is not isolated because A/B also changed.

### Pass 6 — Adversarial review

Với mỗi sentence, hỏi:

1. Citation có thật sự support subject + verb + object không?
2. Sentence có lén đổi `reported` thành fact universal không?
3. Có chuyển benchmark correlation thành architecture causation không?
4. Có trộn prefill, decode và throughput không?
5. Có quên tools, effort, context hoặc hardware không?
6. Missing evidence đã được gọi là unknown thay vì failure chưa?

## 10. Template deliverable một trang

```markdown
# Model A vs Model B — scoped comparison

## Question and boundary
- Decision/question:
- Included models/checkpoints:
- Workload:
- Dimensions intentionally not compared:

## Matched-dimension matrix
| Dimension | Model A | Model B | Comparable? | Evidence |
|---|---|---|---|---|

## Supported claims
1. [Mechanism claim] — source and scope.
2. [Empirical claim] — metric, setup and provenance.

## Evidence gaps
- Missing component ablation:
- Unmatched data/scale/hardware:
- Missing independent reproduction:

## Unsupported causal claims to avoid
- ...

## Operational conclusion
- If workload X and constraint Y, design trade-off Z is relevant.
- This is synthesis, not a universal ranking.
```

### 10.1 Example conclusion ngắn

> **Documented:** DeepSeek-V3 uses compressed token-addressable MLA throughout its attention path, while Kimi Linear and Kimi K3 use fixed-state KDA in most sequence-mixing layers and retain periodic MLA for token-level retrieval.[^deepseek-v3-2024][^kimi-linear-2025][^kimi-k3-2026]  
> **Synthesis:** workloads dominated by very long decode state may value the hybrid’s bounded KDA state, while tasks needing frequent direct token retrieval motivate retaining MLA.  
> **Gap:** the available reports do not provide a three-way matched experiment controlling scale, data, post-training, kernels and hardware, so this mechanism comparison does not establish a quality or cost ranking.

## 11. Checklist hoàn thành Stage 9.5

Bạn chỉ nên coi bài so sánh hoàn tất khi trả lời được:

### Architecture

- [ ] Query đọc token slots hay fixed recurrent state?
- [ ] State nào tăng theo sequence, depth, batch và total experts?
- [ ] Position information đi vào path nào?
- [ ] Active parameters có bị nhầm với total resident weights không?

### Experiment

- [ ] Baseline/control được nêu rõ?
- [ ] Scale, data, token budget, optimizer và evaluation có matched?
- [ ] Component ablation hay whole-model benchmark?
- [ ] Metric có uncertainty hoặc multiple seeds không?

### Systems

- [ ] Training, prefill, decode hay end-to-end?
- [ ] Batch/concurrency, context, output length, hardware và dtype?
- [ ] Latency có bị trộn với maximum throughput?
- [ ] Kernel result có bị nâng thành serving result?

### Evaluation

- [ ] Same benchmark version, harness, tools và effort?
- [ ] Author-reported hay independent?
- [ ] Contamination/evaluation adaptation được xét?
- [ ] Selected case study có bị gọi là reliability không?

### Writing

- [ ] Mỗi causal verb có intervention phù hợp?
- [ ] Missing evidence được ghi `unknown`?
- [ ] Documented knowledge và synthesis được tách rõ?
- [ ] Unsupported causal claims được liệt kê công khai?

## 12. Kết luận

`Comparative reading` tốt không cố ép mọi model vào một ranking duy nhất. Nó hỏi design nào đổi **memory semantics**, resource nào tăng theo workload, và evidence nào thực sự isolate được effect. DeepSeek-V3, Kimi Linear và Kimi K3 minh họa ba điểm cốt lõi: compressed token memory khác fixed-state memory; sparse activation khác total deployment cost; và whole-model success không tự động chứng minh causal contribution của một component. Khi comparison matrix khóa đúng dimension và evidence ledger giữ rõ control, workload, provenance cùng limitation, kết luận sẽ ngắn hơn nhưng đáng tin hơn.

## Relationships

- **Depends on:** [Baseline-to-bottleneck: cách đọc frontier model cho người mới](baseline-to-bottleneck-frontier-model-reading-beginners-guide.md) để xác định replaced baseline và bottleneck trước khi so sánh.
- **Compares:** [DeepSeek-V3 architecture and pretraining](deepseek-v3-architecture-and-pretraining.md), [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md), và [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) theo matched dimensions thay vì headline scores.
- **Uses:** [DeepSeek-V3 post-training, evaluation, and limitations](deepseek-v3-post-training-evaluation-and-limitations.md) và [Kimi K3 evaluation and limitations](kimi-k3-evaluation-and-limitations.md) để minh họa author reporting, harness, tools và causal gaps.
- **Qualifies:** architecture-level interpretation bằng evidence về [Kimi K3 lifecycle infrastructure](kimi-k3-lifecycle-infrastructure.md) và [Attention Residuals evaluation and systems trade-offs](attention-residuals-evaluation-and-systems-trade-offs.md).

[^deepseek-v3-2024]: DeepSeek-AI, “DeepSeek-V3 Technical Report,” arXiv:2412.19437v2, [source](../raw/arXiv-2412.19437v2/main.tex), especially Sections 2–7 and Appendix A.

[^kimi-linear-2025]: Kimi Team, “Kimi Linear: An Expressive, Efficient Attention Architecture,” arXiv:2510.26692v2, [source](../raw/arXiv-2510.26692v2/main.tex), especially architecture, ablation, evaluation and efficiency sections and their included tables.

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), especially Sections 2–7 and Appendix E.

[^brown-gpt-3-2020-v4]: Brown et al., “Language Models are Few-Shot Learners,” arXiv:2005.14165v4, [source](../raw/arXiv-2005.14165v4/main.tex), especially Section 4 and Appendix C.
