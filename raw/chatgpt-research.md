# Research Survey 2026: Time Series Foundation Models (TSFM)

Cập nhật đến 27/10/2026 · Phạm vi: Zero-shot forecasting, multivariate forecasting, probabilistic forecasting, fine-tuning và các foundation model cho time-series analysis

## 1. Executive summary

Time Series Foundation Models (TSFM) là các mô hình được pre-train trên tập dữ liệu chuỗi thời gian quy mô lớn, với mục tiêu có thể dự báo trên dữ liệu mới mà không cần huấn luyện lại (zero-shot forecasting), hoặc thích nghi nhanh bằng fine-tuning.

Từ năm 2024 đến 2026, lĩnh vực này đã chuyển dịch rõ rệt:

- 2024: Tập trung vào zero-shot univariate forecasting, tiêu biểu là TimesFM, Chronos, Moirai.
- 2025: Mở rộng sang dự báo xác suất, multivariate forecasting, in-context learning và các mô hình hiệu quả hơn như Chronos-Bolt, TimesFM 2.5, Chronos-2, Moirai 2.0.
- 2026: Nổi bật với các model tích hợp multivariate và covariates trực tiếp, như TimesFM 3.0, TiRex-2, Toto 2.0; đồng thời xuất hiện những hướng nghiên cứu về streaming, model routing, scaling và domain specialization.

Những model nên ưu tiên khảo sát

[TimesFM: Google's 200M Parameter Decoder for Time Series Forecasting | Florian Narr](https://images.openai.com/static-rsc-4/DbkFlp_Pcg4Wo5cRt6Vx6wKLkF7Gt6dM3mT0QKnIe5GJN7P7LfW_M8lSvKLDlLMqvcVfXMAyHSHU8KUF1Y5_g15x7IKB5YUJgdCP5VbydXdlMJRojqP58l-0E2YIqk3xzdDG_S0DUVh4ExtGrx9d3qff55QF_6FDPs6IFU_zxDk?purpose=inline)

TimesFM 3.0

Google Research · 2026

Đáng chú ý cho zero-shot multivariate và covariate-aware forecasting.

[AI Identity Summit Paris](https://images.openai.com/static-rsc-4/4728a38_PsaVu17UngfW80lC4Gfogi31iPvkf8ENdpSkgWKGVl5ToT26rHv1jy0vDdKZYAVysZhaM8CnwTfn3Q_MUhqXBWmo4Y499aLyZt3wArmagzxQIgYlngH4dQrCZFvIKInNrmUgeEcw5GeExJAJdu1693BdlwUhQUT2ikQ?purpose=inline)

Chronos-2

Amazon · 2025

Universal forecasting với group attention và in-context learning.

[Datadog Logo Png | Datadog Logo Vector | Datadog Logo: Vigilant Canine of Cloud Observability | Data-Driven Mascot | Modern Tech Branding | Digital Watchdog - freepng](https://images.openai.com/static-rsc-4/pxsn8LRrNZsjrxbp6yK0SfQK_QnQRdHf4NtAefW9cu1VRj1GFQasrK1fr79Dswh11ve1U9AGUhJ9w7yQ7TZiI--EaL68R-hWuBI96CdOLEqTDNbtAgiTKn6d_eHbdzzoc3aLn1KeVICNtljKoon5aYtnGSJz0dEXFPGLPvbaWRk?purpose=inline)

Toto 2.0

Datadog · 2026

Mạnh về high-dimensional multivariate và observability metrics.

[TiRex-2: Multivariate Forecasting](https://images.openai.com/static-rsc-4/ojOD3ingMMmmW_wmMzFAF8QuVA69v-sofCxp0liYCDpPBx0yxJJb9oElGYqJEYTYvu2_nFysDW-JcSOoggbsqy1mZwna-Kd9JA4y3w9YO0SPRVApjqBF5bVR1UeQOSeblTV1HZMgN65m-Bk36tCJCjGGIxUSEi54osnK8m0HXJ4?purpose=inline)

TiRex-2

NXAI · 2026

Kiến trúc recurrent, hỗ trợ multivariate và covariates.

Google công bố TimesFM 3.0 ngày 31/08/2026 và báo cáo kết quả dẫn đầu trong các so sánh foundation model trên GIFT-Eval, FEV-Bench và TIME. Chronos-2 được công bố từ tháng 10/2025; Toto 2.0 ra mắt năm 2026 và TiRex-2 công bố vào tháng 7/2026. Các kết quả trên là điểm xuất phát để chọn model, không có nghĩa một model sẽ tốt nhất trên mọi dataset thực tế.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://research.google\&sz=32)

research.google+3



### Phát hiện quan trọng: thị trường vừa có thêm hai đối thủ rất mạnh trong tháng 10/2026

Không nên chỉ benchmark TimesFM 3.0 và Chronos-2. Hai model mới cần được đưa vào shortlist ngay:

- Timestral (Mistral AI, 15/10/2026): Có bốn kích thước 5M, 28M, 123M, 209M parameters. Hỗ trợ univariate, multivariate, known-future covariates, 21 quantiles, context tối đa 32.768 bước. Trong kết quả Mistral công bố, Timestral-209M vượt TimesFM 3.0 trên GIFT-Eval, TIME và FEV-Bench.&#x20;

  [image](https://www.google.com/s2/favicons?domain=https://mistral.ai\&sz=32)

  Mistral+1

- t0-gamma (The Forecasting Company, 13/10/2026): Khoảng 256M parameters, decoder-style patch Transformer, multivariate và probabilistic forecasting; weights Apache-2.0. Trên GIFT-Eval, nhóm phát triển báo cáo CRPS 0,4520, tốt hơn TimesFM 3.0 (0,4557).&#x20;

  [image](https://www.google.com/s2/favicons?domain=https://www.theforecastingcompany.com\&sz=32)

  The Forecasting Company+1



Vì vậy, shortlist cập nhật cho một nghiên cứu forecasting tổng quát là Timestral, t0-gamma, TimesFM 3.0, Chronos-2, TiRex-2, Toto 2.0, thay vì mặc định Google hoặc Amazon dẫn đầu.

## 2. Taxonomy: Phân loại các hướng nghiên cứu

Time Series Foundation Models



Direct time-series models

Học trực tiếp trên chuỗi số

TimesFM, Chronos, Moirai, Timestral, Toto

Language-based models

Biến time series thành token, prompt hoặc embedding của LLM

Time-LLM, LLMTime, GPT4TS

Multimodal models

Kết hợp chuỗi số, văn bản, image hoặc thông tin ngữ cảnh

VisionTS, các text-conditioned TSFM

General time-series representation

Học embedding dùng cho nhiều downstream task

MOMENT, TSPulse, UniTS

Một survey có hệ thống nên tách mô hình dự báo đã pre-train, mô hình biểu diễn dùng cho nhiều tác vụ, LLM/multimodal forecasting, và các baseline học có giám sát. Nếu trộn các nhóm này, kết luận về zero-shot hay transfer learning dễ bị sai lệch.

Ngoài tên model, các chiều so sánh có giá trị nghiên cứu nhất là: pre-training objective, time-series tokenization, kiến trúc attention, số tham số, hỗ trợ covariates, khả năng thích nghi với dữ liệu mới, độ tin cậy của uncertainty và chi phí triển khai.

## 3. Bảng tổng hợp các Time Series Foundation Models

### 3.1. Nhóm forecasting foundation models chính

Bảng dưới đây tập trung vào các model có pretrained checkpoint hoặc dịch vụ forecasting được công bố. Kích thước được tính theo số parameters; với các model có nhiều checkpoint, mình ghi khoảng kích thước hoặc phiên bản đại diện.

| Model / tổ chức                          | Parameters           | Điểm nổi bật                                  | Multivariate / covariates             | License weights                     |
| ---------------------------------------- | -------------------- | --------------------------------------------- | ------------------------------------- | ----------------------------------- |
| Timestral — Mistral, 2026                | 5M–209M              | Zero-shot probabilistic, long context, CPU    | Native / Có                           | Modified MIT\*                      |
| t0-gamma — The Forecasting Company, 2026 | \~256M               | Patch Transformer, 21 quantiles               | Native / Có                           | Apache-2.0                          |
| TimesFM 3.0 — Google, 2026               | 330M                 | Parallel decoding, cross-series attention     | Native / Có                           | Non-commercial\*                    |
| Chronos-2 — Amazon, 2025                 | 120M                 | Group attention, in-context learning          | Native / Có                           | Apache-2.0                          |
| TiRex-2 — NXAI, 2026                     | 38.4M + 44.1M active | Recurrent backbone, gọn nhẹ                   | Native / Có                           | Apache-2.0                          |
| Toto 2.0 — Datadog, 2026                 | 4M–2.5B              | High-dimensional forecasting, observability   | Native / Chưa có ở 2.0                | Apache-2.0                          |
| Moirai 2.0 — Salesforce, 2025            | \~11M (small)        | Decoder-only, multi-token quantile prediction | Có, tùy API / Cần kiểm tra            | CC-BY-NC-4.0                        |
| TimesFM 2.5 — Google, 2025               | 200M                 | Univariate, context dài, quantile head        | Không native / XReg                   | Apache-2.0                          |
| Chronos-Bolt — Amazon, 2024              | 9M–205M              | Direct multi-step quantile forecasting        | Chủ yếu independent / Không native    | Apache-2.0                          |
| Moirai 1.0/1.1 — Salesforce, 2024        | 14M–311M             | Any-variate attention, mixture distribution   | Có / Dynamic features                 | Kiểm tra checkpoint                 |
| Granite TTM R3 — IBM, 2026               | Cỡ triệu             | CPU-first, rất nhẹ, fine-tuning nhanh         | Có cơ chế channel mixing và exogenous | Apache-2.0                          |
| Granite PatchTST-FM R2 — IBM, 2026       | Cỡ trăm triệu        | Probabilistic, long context                   | Chủ yếu channel-wise                  | OpenMDW-1.0 / điều khoản model card |
| Granite FlowState — IBM                  | Cỡ triệu             | Sampling-rate invariant, SSM                  | Tùy biến thể                          | Apache-2.0                          |
| Sundial — Tsinghua, 2025                 | 128M–444M            | Flow matching, generative forecasting         | Chủ yếu channel-independent           | Kiểm tra checkpoint                 |
| Time-MoE — nghiên cứu học thuật, 2024    | Tối đa 2.4B          | Sparse MoE, scaling laws                      | Chủ yếu univariate                    | Kiểm tra checkpoint                 |
| Timer-S1 — Tsinghua/ByteDance, 2026      | 8.3B (0.75B active)  | Sparse MoE, serial token prediction           | Chủ yếu independent                   | Kiểm tra checkpoint                 |
| Lag-Llama — nhóm nghiên cứu, 2024        | \~200M               | Autoregressive probabilistic forecasting      | Chủ yếu univariate                    | Open weights                        |
| TimeGPT — Nixtla, từ 2023                | Không công bố        | Managed API, anomaly detection, fine-tuning   | Multi-series, exogenous API           | Proprietary                         |

\* TimesFM 3.0: mã nguồn Apache-2.0 nhưng weights tải về chỉ cho non-commercial/non-production; sử dụng thương mại qua Google Cloud theo điều khoản dịch vụ. Timestral: Modified MIT có điều kiện riêng khi doanh thu hợp nhất hằng tháng vượt 20 triệu USD. Luôn kiểm tra license của checkpoint cụ thể, không suy ra từ license của GitHub repository.

Các thông tin này được đối chiếu với các model card/repository của Google, Amazon, Datadog, Salesforce, NXAI, IBM, Mistral và nghiên cứu Timer-S1.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub+9



### 3.2. Các model bổ sung cần có trong một literature survey rộng

| Nhóm                      | Model                                         | Hướng nghiên cứu                                         |
| ------------------------- | --------------------------------------------- | -------------------------------------------------------- |
| Generative TSFM           | Timer, Timer-XL                               | Next-token prediction và long-context                    |
| Efficient TSFM            | Kairos, CITRAS-FM                             | Adaptive tokenization, parameter efficiency              |
| Lightweight forecasting   | TimeH2O-v1, LightGTS                          | Compact pretrained forecasting                           |
| Probabilistic forecasting | ForecastPFN, TabPFN-TS                        | Prior-data-fitted networks, synthetic priors             |
| Multivariate forecasting  | UniTS, UNITS, GTT                             | Unified representation và cross-variable learning        |
| General-purpose analysis  | MOMENT, TSPulse, TOTEM                        | Classification, imputation, anomaly detection, embedding |
| Finance-specific          | Kronos                                        | Financial K-line/candlestick modeling                    |
| Irregular sampling        | QiYao-I                                       | Irregular and asynchronous multivariate observations     |
| Vision-based              | VisionTS, VisionTS++                          | Chuyển time series thành image                           |
| LLM-based                 | LLMTime, Time-LLM, GPT4TS, AutoTimes, UniTime | Sử dụng pretrained language models                       |
| Multimodal / reasoning    | ChatTime, Chronicle, TimeOmni-VL              | Kết hợp dữ liệu chuỗi và ngôn ngữ                        |
| Agentic forecasting       | TimeRouter, MoiraiAgent, TimeCopilot          | Routing, ensemble, orchestration                         |

Đây là các hướng và model đại diện, không đồng nghĩa tất cả có khả năng zero-shot forecasting ngang nhau hoặc đã phát hành pretrained weights dùng được ngay. Các nguồn tổng hợp hữu ích gồm [Awesome Time-Series Foundation Models](https://github.com/lihuirui/awesome-time-series-foundation-models?utm_source=chatgpt.com) và [Time-Series-Library](https://github.com/thuml/Time-Series-Library?utm_source=chatgpt.com).&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub+2



## 4. So sánh kiến trúc: TimesFM 3.0 vs Chronos-2 vs Timestral

Đây là phần đặc biệt quan trọng nếu mục đích của survey là tìm research gap hoặc phát triển model mới.

| Khía cạnh               | TimesFM 3.0                        | Chronos-2                               | Timestral-209M                      |
| ----------------------- | ---------------------------------- | --------------------------------------- | ----------------------------------- |
| Backbone                | Decoder-only Transformer           | T5-inspired encoder với group attention | Patch-based Transformer             |
| Representation          | Continuous patches                 | Patches và learned representations      | Continuous patches                  |
| Cross-series learning   | Alternating time/variate attention | Group attention                         | Time/variate attention              |
| Future known covariates | Native                             | Native                                  | Native                              |
| Probabilistic output    | 9 quantiles                        | Quantile forecasting                    | 21 quantiles                        |
| Inference               | Parallel horizon                   | Direct multi-step output                | Parallel blocks                     |
| Size                    | 330M                               | 120M                                    | 209M                                |
| Research focus          | Joint multivariate modeling        | Universal in-context forecasting        | Accuracy–efficiency–context scaling |

[image](https://www.google.com/s2/favicons?domain=https://research.google\&sz=32)

Google Research+3

Nhận xét về ba thiết kế:

TimesFM 3.0: Chuyển từ thế hệ univariate forecasting sang native multivariate, dùng alternating temporal/variate attention. Đặc biệt, thay vì autoregressive theo từng patch, model có thể dự báo horizon trong một lần forward thông qua contiguous patch masking. Điều này giúp giảm hiện tượng sai số tích lũy trong giải mã tuần tự.

Chronos-2: Điểm khác biệt nằm ở group attention và khả năng chia sẻ thông tin theo nhóm các series, bao gồm targets và covariates. Đây là hướng nghiên cứu tốt cho in-context forecasting — tận dụng dữ liệu liên quan mà không cần cập nhật trọng số.

Timestral: Kết hợp multivariate attention, known-future covariates và long context trong mô hình tương đối nhỏ. Model card công bố context tối đa 32.768 time steps và horizon tối đa 1.024 steps mỗi forward pass. Đây là đối chứng quan trọng khi nghiên cứu scaling efficiency thay vì chỉ tăng số parameters.

## 5. Benchmark comparison — kết quả cập nhật tháng 10/2026

### 5.1. Đối chiếu các model mới trên benchmark công khai

Bảng dưới sử dụng các kết quả trong model card Timestral-209M do Mistral công bố vào tháng 10/2026. Các score được báo cáo cho pretrained, single-checkpoint models, không phải kết quả benchmark mình tự chạy.

| Model          | GIFT-Eval MASE ↓ | GIFT-Eval CRPS ↓ | TIME MASE ↓ | FEV SQL skill ↑ |
| -------------- | ---------------- | ---------------- | ----------- | --------------- |
| Timestral-209M | 0.658            | 0.446            | 0.626       | 50.39%          |
| t0-gamma       | 0.661            | 0.452            | 0.637       | 49.42%          |
| TimesFM 3.0    | 0.667            | 0.456            | 0.640       | 48.99%          |
| Chronos-2      | 0.698            | 0.485            | 0.662       | 47.28%          |
| Toto 2.0 2.5B  | 0.696            | 0.476            | 0.642       | 44.42%          |

[image](https://www.google.com/s2/favicons?domain=https://huggingface.co\&sz=32)

Hugging Face+1

So sánh GIFT-Eval — normalized CRPS (càng thấp càng tốt)

00,150,30,450,6Timestralt0-gammaTimesFM 3Toto 2Chronos 2

Nguồn: Timestral-209M model card, tháng 10/2026. Chỉ so sánh 5 model trong cùng bảng công bố.

Kết quả cho thấy Timestral-209M đang rất cạnh tranh trong bộ so sánh này, nhưng cần lưu ý ba vấn đề:

- Kết quả là số liệu công bố từ nhóm phát triển, chưa phải thử nghiệm độc lập trên dataset của bạn.
- GIFT-Eval có nhiều phương pháp xếp hạng: geometric mean error, mean rank, các nhóm pretrained, zero-shot, agentic hoặc fine-tuned. Thứ hạng có thể thay đổi tùy bộ lọc.
- Khoảng cách điểm tổng hợp nhỏ không đảm bảo model tốt hơn trên mọi domain, horizon hoặc loại covariate.

### 5.2. Các benchmark nên sử dụng

| Benchmark                                                                             | Mục tiêu                                                   | Phù hợp nhất                       |
| ------------------------------------------------------------------------------------- | ---------------------------------------------------------- | ---------------------------------- |
| [GIFT-Eval](https://github.com/SalesforceAIResearch/gift-eval?utm_source=chatgpt.com) | Forecast đa domain, nhiều tần suất, point và probabilistic | Generalization                     |
| [FEV-Bench](https://arxiv.org/abs/2509.26468?utm_source=chatgpt.com)                  | 100 forecasting tasks, có covariates và multivariate       | Real-world forecasting             |
| [TIME](https://arxiv.org/abs/2602.12147?utm_source=chatgpt.com)                       | 50 datasets, 98 tasks, đánh giá zero-shot và pattern-level | Generalization, leakage robustness |
| [BOOM](https://github.com/DataDog/toto?utm_source=chatgpt.com)                        | Production observability metrics                           | High-dimensional telemetry         |
| [Monash Forecasting Repository](https://forecastingdata.org/?utm_source=chatgpt.com)  | Classical và historical forecasting datasets               | So sánh với baseline               |

GIFT-Eval đặc biệt cần phân biệt pretrained với strict zero-shot: checkpoint pretrain trên train split của benchmark và checkpoint chưa từng dùng dataset trong benchmark có mức độ độc lập khác nhau. FEV-Bench còn đưa ra bootstrap confidence intervals giúp đánh giá độ chắc chắn của khác biệt kết quả.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

SalesforceAIResearch/gift-eval · GitHub+2



## 6. Các hướng ngoài forecasting cần khảo sát

### General-purpose time-series understanding

MOMENT (ICML 2024) tập trung vào học representations phục vụ nhiều downstream tasks, không chỉ dự báo. Đây là model phù hợp để khảo sát transfer learning cho classification, anomaly detection và imputation.

IBM TSPulse (ICLR 2026) sử dụng masked reconstruction trong time và frequency domains, có khoảng 1M parameters, hướng đến anomaly detection, similarity search, imputation và classification trên CPU.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://proceedings.mlr.press\&sz=32)

Proceedings of Machine Learning Research+1



### Vision và language foundation models

VisionTS / VisionTS++ biểu diễn chuỗi thời gian dưới dạng hình ảnh, tận dụng pretrained visual encoders. VisionTS++ bổ sung cross-variable modeling và quantile predictions.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv+1



LLMTime, Time-LLM và GPT4TS là nhóm dùng language models để dự báo time series thông qua chuyển đổi input hoặc reprogramming embeddings. Tuy nhiên, nghiên cứu NeurIPS 2024 Are Language Models Actually Useful for Time Series Forecasting? cho thấy trong các phương pháp được kiểm tra, loại bỏ LLM backbone nhiều khi không làm giảm accuracy và đôi khi còn cải thiện kết quả. Vì vậy, đây là hướng nghiên cứu đáng khảo sát về multimodal reasoning hơn là mặc định lựa chọn cho numeric forecasting.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://proceedings.iclr.cc\&sz=32)

ICLR Proceedings+2



### Domain-specific models

Kronos (2025) được phát triển riêng cho dữ liệu financial candlesticks, sử dụng tokenizer cho giá và hoạt động giao dịch; khác đáng kể so với TSFM general-purpose.

QiYao-I (10/2026) nhắm đến irregular multivariate series — đặc biệt hữu ích khi sensor readings có timestamp không đều hoặc các biến được lấy mẫu bất đồng bộ.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv+1



## 7. Research gaps đáng chú ý năm 2026

1\. Irregularly sampled multivariate series

Phần lớn forecasting TSFMs giả định regular timestamps. Dữ liệu IoT, clinical telemetry hoặc event streams thường không đáp ứng giả định này. QiYao-I là một hướng tiếp cận đáng đọc.

2\. Concept drift và online adaptation

Pretrained zero-shot có thể suy giảm khi dữ liệu đổi regime. Nghiên cứu continual learning, test-time adaptation và streaming inference vẫn rất cần thiết, đặc biệt ở manufacturing và finance.

3\. Calibration và uncertainty

Một model có MAE thấp chưa chắc tạo prediction intervals đáng tin cậy. Các nghiên cứu nên đánh giá calibration, interval coverage và performance trong extreme events.

4\. Data contamination và temporal leakage

Quy mô pretraining ngày càng lớn khiến khó chứng minh dữ liệu test thật sự chưa từng được model nhìn thấy. Benchmarking trên dữ liệu phát sinh sau thời điểm model được pretrain là một hướng kiểm chứng quan trọng.

5\. Accuracy–latency–energy trade-off

Nghiên cứu independent năm 2026 cho thấy mức tiêu thụ năng lượng khác biệt lớn giữa các kiến trúc và độ chính xác phụ thuộc dataset. Mô hình lớn không nhất thiết là phương án triển khai tối ưu.

[image](https://www.google.com/s2/favicons?domain=https://arxiv.org\&sz=32)

arXiv+3

## 8. Đề xuất thiết kế benchmark phục vụ nghiên cứu thực tế

Nếu mục tiêu là thực hiện nghiên cứu khoa học hoặc lựa chọn model để đưa vào production, mình đề xuất benchmark theo protocol sau:

| Thành phần            | Thiết kế đề xuất                                                    |
| --------------------- | ------------------------------------------------------------------- |
| Models                | Timestral-209M, t0-gamma, TimesFM 3.0, Chronos-2, Toto 2.0, TiRex-2 |
| Lightweight baselines | Chronos-Bolt-Tiny, TTM-R3, Timestral-5M                             |
| Classical baselines   | Seasonal Naive, ETS, AutoARIMA                                      |
| Supervised baselines  | LightGBM, N-HiTS, DLinear, PatchTST, iTransformer                   |
| Context lengths       | 96, 512, 2.048 và dài hơn nếu model hỗ trợ                          |
| Prediction horizons   | 24, 96, 192, 336, 720 (tùy tần suất và tác vụ)                      |
| Settings              | Univariate; multivariate; multivariate + future covariates          |
| Metrics               | MASE, WQL/CRPS, RMSE, sMAPE, interval coverage                      |
| System metrics        | Latency, throughput, CPU/GPU RAM, peak VRAM                         |
| Protocol              | Rolling-origin backtesting, chronological holdout                   |
| Adaptation            | Zero-shot, few-shot fine-tuning, LoRA (khi hỗ trợ)                  |

Quan trọng: Phải đánh giá theo nhóm dataset/domain, không chỉ lấy một global average. Đối với forecasting có yếu tố thời gian, sử dụng dữ liệu future covariates chỉ khi những feature đó thực sự biết được tại thời điểm dự báo. Ví dụ weather forecast là hợp lệ, nhưng actual future temperature không hợp lệ nếu ở production không thể biết trước.

Cũng nên giữ một tập đánh giá riêng, không sử dụng để chọn model hoặc tune hyperparameters.

## 9. Gợi ý chọn model theo use case

| Use case                                  | Model ưu tiên thử nghiệm            | Lý do                                            |
| ----------------------------------------- | ----------------------------------- | ------------------------------------------------ |
| Accuracy zero-shot tổng quát              | Timestral-209M, TimesFM 3, t0-gamma | Rất cạnh tranh trên benchmark mới                |
| Commercial self-hosting với Apache-2.0    | t0-gamma, Chronos-2, TiRex-2        | Giấy phép thuận tiện hơn cho production          |
| Forecast có promotions, holidays, weather | Timestral, Chronos-2, TimesFM 3     | Native covariate support                         |
| High-dimensional observability            | Toto 2.0, Timestral                 | Cross-variable forecasting                       |
| CPU/edge deployment                       | Timestral-5M/28M, IBM TTM R3        | Kiến trúc nhẹ                                    |
| Classification, imputation, embeddings    | MOMENT, TSPulse                     | Pretraining hướng representation                 |
| Financial candlestick data                | Kronos                              | Domain-specific pretraining                      |
| Irregular sampling                        | QiYao-I                             | Modeling timestamps và asynchronous observations |
| Time-series forecasting qua API           | TimeGPT                             | Managed service, không cần self-host             |
| Streaming và recurrent architecture       | TiRex-2                             | Hướng kiến trúc phù hợp để nghiên cứu streaming  |

## 10. Reading list — những paper nên đọc

Để làm literature review có chiều sâu, mình đề xuất bắt đầu từ các công trình sau.

| Paper / tài liệu                                                                                                                                                                                 | Năm  | Tại sao nên đọc                             |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---- | ------------------------------------------- |
| [Chronos-2: From Univariate to Universal Forecasting](https://arxiv.org/abs/2510.15821?utm_source=chatgpt.com)                                                                                   | 2025 | Universal ICL và covariate modeling         |
| [TimesFM-3: A zero-shot foundation model for multivariate forecasting](https://research.google/blog/timesfm-3-a-zero-shot-foundation-model-for-multivariate-forecasting/?utm_source=chatgpt.com) | 2026 | Multivariate attention và parallel decoding |
| [Introducing Timestral](https://mistral.ai/news/timestral/?utm_source=chatgpt.com)                                                                                                               | 2026 | Accuracy–efficiency scaling                 |
| [t0: A Time-Series Foundation Model for Forecasting with Context](https://arxiv.org/abs/2609.24559?utm_source=chatgpt.com)                                                                       | 2026 | Forecasting với contextual signals          |
| [Moirai 2.0: When Less Is More for Time Series Forecasting](https://arxiv.org/abs/2511.11698?utm_source=chatgpt.com)                                                                             | 2025 | Tối giản kiến trúc, quantile loss           |
| [Sundial: A Family of Highly Capable Time Series Foundation Models](https://arxiv.org/abs/2502.00816?utm_source=chatgpt.com)                                                                     | 2025 | Flow matching cho generative forecasting    |
| [Timer-S1: A Billion-Scale Time Series Foundation Model with Serial Scaling](https://arxiv.org/abs/2603.04791?utm_source=chatgpt.com)                                                            | 2026 | Scaling laws và MoE                         |
| [TiRex-2: Generalizing TiRex to Multivariate Data and Streaming](https://arxiv.org/abs/2607.01204?utm_source=chatgpt.com)                                                                        | 2026 | Recurrent / efficient modeling              |
| [Foundation Models for Time Series: A Survey](https://arxiv.org/abs/2504.04011?utm_source=chatgpt.com)                                                                                           | 2025 | Literature survey nền tảng                  |
| [Time Series Foundation Models: Benchmarking Challenges and Requirements](https://arxiv.org/abs/2510.13654?utm_source=chatgpt.com)                                                               | 2025 | Data leakage và benchmark validity          |
| [It's TIME: Towards the Next Generation of Time Series Forecasting Benchmarks](https://arxiv.org/abs/2602.12147?utm_source=chatgpt.com)                                                          | 2026 | Evaluation design và generalization         |

## Kết luận

Nếu xây dựng một research survey có tính hệ thống cho Time Series Foundation Models đến tháng 10/2026, mình sẽ lấy sáu họ Timestral, t0, TimesFM, Chronos, Moirai và Toto làm trục so sánh chính; bổ sung TiRex, Sundial, Timer và IBM Granite để phản ánh các lựa chọn kiến trúc khác nhau.

Ba bài toán nghiên cứu nổi bật hiện nay là:

1. Làm thế nào học cross-series dependencies và covariates hiệu quả mà không cần fine-tuning?
2. Làm thế nào đạt zero-shot accuracy cao hơn với ít parameters, latency và memory hơn?
3. Làm thế nào bảo đảm generalization thật sự trước domain shift, concept drift và data contamination?

Một nghiên cứu tốt không chỉ chứng minh model đạt score cao hơn, mà cần làm rõ khi nào, vì sao và với chi phí bao nhiêu model đó vượt các phương án khác.