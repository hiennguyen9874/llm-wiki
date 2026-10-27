# Kiến trúc Time Series Foundation Models: Từ Input đến Output

Để hiểu các mô hình như TimesFM 3.0, Chronos-2, Timestral, Moirai, Toto và TiRex-2, cần phân biệt ba vấn đề:

1. Dữ liệu: Model nhận những gì, ở định dạng nào và cần dự đoán cái gì?
2. Kiến trúc: Model biến chuỗi thời gian thành các token, học quan hệ theo thời gian và giữa các biến như thế nào?
3. Cơ chế sinh dự báo: Model tạo từng điểm, từng patch, toàn bộ horizon hay một phân phối xác suất?

Điểm quan trọng nhất: TSFM không có một kiến trúc thống nhất như Transformer trong LLM. Chúng là một nhóm mô hình được pretrain trên dữ liệu time series, nhưng khác nhau về tokenization, backbone, attention, training objective và output head.

## 1. Input và Output tổng quát

### 1.1. Mô hình forecasting nhận những gì?

Giả sử ta muốn dự báo nhu cầu điện trong 24 giờ tiếp theo, dựa trên 168 giờ quá khứ.

Model có thể nhận bốn loại dữ liệu:

| Input                   | Ký hiệu                         | Ý nghĩa                                             | Ví dụ                                   |
| ----------------------- | ------------------------------- | --------------------------------------------------- | --------------------------------------- |
| Historical target       | \\(Y\_{\mathrm{past}}\\)        | Biến cần dự báo, quan sát trong quá khứ             | Điện năng tiêu thụ                      |
| Past covariates         | \\(X\_{\mathrm{past}}\\)        | Các biến phụ trợ chỉ biết trong quá khứ             | Nhiệt độ đo thực tế                     |
| Known-future covariates | \\(K\_{\mathrm{past+future}}\\) | Biến phụ trợ đã biết cho cả thời gian dự báo        | Lịch nghỉ lễ, nhiệt độ dự báo           |
| Metadata và mask        | \\(M\\)                         | Timestamp, frequency, missing mask, thông tin chuỗi | Hourly, ngày trong tuần, missing values |

Tại thời điểm dự báo \\(t\\), model chỉ được sử dụng thông tin thực sự có sẵn tại thời điểm \\(t\\).

Minh họa input–output theo thời gian

Targets tương lai bị ẩn; future covariates được phép quan sát nếu thực sự biết trước. Sơ đồ là biểu diễn logic, không phải sơ đồ token hóa của một model cụ thể.

### 1.2. Tensor shapes chuẩn

Quy ước:

- \\(B\\): batch size.
- \\(L\\): context length.
- \\(H\\): prediction horizon.
- \\(D_y\\): số biến mục tiêu.
- \\(D_p\\): số past-only covariates.
- \\(D_k\\): số known-future covariates.
- \\(Q\\): số quantile levels.
- \\(S\\): số quỹ đạo dự báo được lấy mẫu.

Input tensors (quy ước time-major)

```
past_target     = [B, L, D_y]past_covariates = [B, L, D_p]known_covariates= [B, L + H, D_k]observed_mask   = [B, L, D_y]
```

Output tensors

```
point_forecast    = [B, H, D_y]quantile_forecast = [B, H, D_y, Q]sampled_forecast  = [B, S, H, D_y]
```

Đây là quy ước toán học chung, không phải signature API dùng chung cho tất cả model. Chẳng hạn TiRex-2 dùng tensors channel-first `(num_variates, context_length)` cho từng chuỗi trong batch, còn những implementation khác có thể dùng `[B,D,L]`.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://nx-ai.github.io\&sz=32)

TiRex-2+1



### 1.3. Output có ba kiểu chính

Point forecasting — dự đoán một giá trị tại mỗi bước tương lai:

\\[ \hat Y=f\_\theta(Y\_{\mathrm{past}},X,K) \\]

Quantile forecasting — dự đoán các phân vị:

\\[ \hat q\_{\tau,t}=f\_\theta(Y\_{\mathrm{past}},X,K,\tau) \\]

Ví dụ một giờ trong tương lai có `q10 = 80`, `q50 = 100`, `q90 = 125`, tức là model dự báo median bằng 100 cùng các quantile thể hiện độ bất định.

Sample-based probabilistic forecasting — sinh nhiều kịch bản tương lai:

\\[ Y^{(s)}\_{\mathrm{future}}\sim p\_\theta(Y\_{\mathrm{future}}\mid Y\_{\mathrm{past}},X,K) \\]

Các sample có thể dùng để ước lượng median, quantiles, xác suất vượt ngưỡng và các đại lượng rủi ro.

Lưu ý: quantile output trực tiếp không nhất thiết là một full joint probability distribution; nó thường biểu diễn các marginal quantiles ở từng thời điểm và từng biến.

## 2. Kiến trúc tổng quát của một Time Series Foundation Model

Một pipeline điển hình gồm:

Raw Time Series

Targets + Covariates + Masks + Metadata

1\. Preprocessing

Scaling · Normalization · Missing values · Time features

2\. Tokenizer / Embedding

Numerical patches / Quantized IDs / Latent tokens

Temporal

Quan hệ theo thời gian

Variate

Quan hệ giữa các biến

Context

Tích hợp covariates

3\. Foundation Backbone

Transformer / Encoder–Decoder / SSM / Recurrent / MoE

4\. Prediction Head / Generator

Regression · Quantiles · Distribution · Flow / Sampling

Forecast Output

[B, H, D] hoặc [B, H, D, Q] hoặc các samples

Các model thường cùng có những thành phần này ở mức khái niệm, nhưng có thể bỏ qua hoặc gộp một số bước. Ví dụ Chronos gốc dùng discrete tokens, Sundial dùng flow matching và TimesFM 3.0 sử dụng masked future patches với attention theo hai trục.

### Hai chế độ hoạt động

Pretraining: Model học trên rất nhiều đoạn chuỗi thời gian thuộc nhiều domain, với mục tiêu như next-token prediction, masked forecasting, quantile loss hoặc density modeling. Model cập nhật trọng số \\(\theta\\) thông qua gradient descent.

Zero-shot inference: Trọng số \\(\theta\\) được giữ cố định. Model chỉ nhận history/covariates của chuỗi mới và dự đoán tương lai. Nó có thể thích nghi thông qua context, nhưng không nhất thiết phải fine-tune.

Sự khác biệt giữa các TSFM nằm chủ yếu ở ba quyết định: biến số liệu thành token như thế nào, backbone học quan hệ gì, và prediction head biểu diễn tương lai ra sao.

## 3. Tokenization: Làm sao biến time series thành tokens?

Đây là quyết định kiến trúc đầu tiên và ảnh hưởng mạnh tới tốc độ, khả năng biểu diễn thông tin và cách huấn luyện.

### Hướng A — Discrete value tokenization

Model tiêu biểu: Chronos gốc (2024)

Ý tưởng tương tự language modeling: biến các giá trị liên tục thành token ID.

Time series

120, 135, 128, 150

Scale + Quantize

Chuẩn hóa rồi ánh xạ vào các bins

1682

1920

1813

2170

Các token ID chỉ mang tính minh họa, không phải mapping thực tế của Chronos.

T5 / Token prediction / Cross-entropy

Sample tokens tương lai → Dequantize → Forecast

Chronos gốc sử dụng scaling theo giá trị tuyệt đối trung bình, lượng tử hóa vào các bins và học bằng cross-entropy. Checkpoint Chronos-T5 dùng vocabulary 4.096 tokens. Trong inference, model autoregressively lấy mẫu nhiều token sequences rồi đưa trở lại không gian số thực.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.amazon.science\&sz=32)

Amazon Science+1



Ưu điểm: Dùng được kiến trúc và training objective rất gần với language models.

Hạn chế: Quantization mất độ chính xác biểu diễn; nếu horizon dài, sinh từng token có thể chậm. Phương pháp này cũng không tự động học tương quan multivariate.

### Hướng B — Continuous patch tokenization

Models: TimesFM, Chronos-Bolt, Chronos-2, Toto, Moirai, Timestral, t0, TiRex-2

Đây là hướng phổ biến trong các TSFM hiện đại.

Thay vì mỗi giá trị là một token, model nhóm \\(P\\) giá trị liên tiếp thành một patch rồi project thành embedding.

Giả sử patch size bằng 4:

Patch 1

10, 12, 11, 13

MLP / Linear

Embedding 1

Patch 2

15, 17, 16, 18

MLP / Linear

Embedding 2

Patch 3

20, 19, 22, 24

MLP / Linear

Embedding 3

Mỗi patch gồm nhiều giá trị liên tục và thường thêm mask/time features trước khi embedding.

Công thức tổng quát:

\\[ \mathbf e\_{v,j}= \operatorname{PatchEmbed}\_{\theta} \left( [\tilde{\mathbf x}\_{v,j};\mathbf m\_{v,j};\mathbf t_j] \right) \\]

Trong đó \\(v\\) là biến, \\(j\\) là vị trí patch, \\(\tilde{\mathbf x}\\) là giá trị đã chuẩn hóa, \\(\mathbf m\\) là mask và \\(\mathbf t\\) là time features nếu kiến trúc sử dụng.

Nếu chuỗi đầu vào dài 512 và patch size là 32, số token theo trục thời gian giảm từ 512 xuống 16.

Ưu điểm: Ít token hơn, giữ thông tin số thực, Transformer có thể xử lý context dài hiệu quả hơn.

Trade-off: Patch lớn có thể làm mất các biến động ngắn hạn; patch nhỏ tăng số token và chi phí attention.

### Hướng C — Learned latent representations

Models: MOMENT, một số encoder/representation models

Với hướng này, token embeddings được học để mô tả cấu trúc dữ liệu thay vì chỉ phục vụ dự báo giá trị kế tiếp:

`Time series → Patch + Mask → Encoder → Latent embeddings`

Embeddings có thể đưa vào classification head, anomaly detection head, imputation head hoặc forecasting head.

MOMENT sử dụng masked patch reconstruction để học representations chuyển giao sang nhiều downstream tasks.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub+1



### So sánh ba cách tokenization

| Tiêu chí             | Discrete tokens          | Continuous patches       | Learned representations       |
| -------------------- | ------------------------ | ------------------------ | ----------------------------- |
| Token là gì?         | ID của một bin           | Vector từ một đoạn chuỗi | Embedding ngữ nghĩa thời gian |
| Giữ giá trị liên tục | Gián tiếp                | Trực tiếp                | Qua latent features           |
| Loss điển hình       | Cross-entropy            | MSE, quantile, NLL       | Reconstruction / contrastive  |
| Mục tiêu thường gặp  | Probabilistic generation | Forecasting              | Multi-task understanding      |
| Models               | Chronos gốc              | TimesFM 3, Chronos-2     | MOMENT, TSPulse               |

## 4. Backbone: Những họ kiến trúc chính

### 4.1. Decoder-only autoregressive Transformer

Đây là kiến trúc gần GPT nhất.

p1

Past

p2

Past

p3

Past

p4

Past

p5

Future

p6

Future

Causal Self-Attention

Token tại vị trí j chỉ nhìn được các token quá khứ

Predict next token / next patch

Nếu dự báo autoregressive, kết quả bước trước được dùng cho bước tiếp theo.

Mô hình hóa:

\\[ p\_\theta(Y\_{\mathrm{future}}\mid Y\_{\mathrm{past}}) =\prod\_{j=1}^{N_H} p\_\theta(P_j\mid P\_{\<j}) \\]

Với \\(P_j\\) là future patch thứ \\(j\\).

Models: TimesFM 1.x/2.5, Moirai 2.0, Timer và các biến thể causal patch Transformer.

Điểm cần phân biệt: decoder-only không đồng nghĩa với autoregressive inference. TimesFM 3.0 và Toto 2.0 vẫn sử dụng causal Transformer, nhưng có thể dự đoán nhiều future patches song song qua masking.

### 4.2. Encoder–decoder Transformer

Encoder

Historical context

Self-attention

Memory representations

Decoder

Future query / tokens

Cross-attention to memory

Forecast head

Encoder xây dựng biểu diễn context. Decoder dùng biểu diễn đó để sinh dự báo.

Models: Chronos-T5 và Chronos-Bolt.

- Chronos-T5 dùng tokenized numerical values, sau đó autoregressive decoding.
- Chronos-Bolt dùng continuous patches, T5 encoder–decoder và direct multi-step quantile prediction, nhờ đó tránh phải sample từng giá trị như Chronos gốc.&#x20;

  [image](https://www.google.com/s2/favicons?domain=https://huggingface.co\&sz=32)

  amazon/chronos-bolt-base at main+1



### 4.3. Factorized temporal–variate attention

Đây là kiến trúc rất quan trọng đối với các TSFM thế hệ mới.

Giả sử sau patch embedding ta có:

\\[ E\in\mathbb R^{B\times D\times N\times d} \\]

Với \\(D\\) là số series/covariates, \\(N\\) số patch theo thời gian, \\(d\\) embedding dimension.

Thay vì đưa toàn bộ \\(D\times N\\) tokens qua full attention, ta tách làm hai bước.

Time × Variate Token Grid

Màu xanh: target series. Màu tím: covariates. Mũi tên chỉ hai trục xử lý, không biểu diễn mask cụ thể của từng model.

Temporal attention: Học xu hướng, seasonality, autocorrelation và temporal dynamics trong mỗi series.

\\[ E'\_{:,v,:,:} =\operatorname{Attention}\_{time}(E\_{:,v,:,:}) \\]

Variate attention: Học phụ thuộc giữa các series và covariates:

\\[ E''\_{:,:,j,:} =\operatorname{Attention}\_{variate}(E'\_{:,:,j,:}) \\]

Chi phí attention tính theo số cặp token, bỏ qua embedding width và số head:

| Thiết kế                            | Độ phức tạp xấp xỉ |
| ----------------------------------- | ------------------ |
| Full attention trên toàn bộ tokens  | \\(O((DN)^2)\\)    |
| Factorized time + variate attention | \\(O(DN^2+ND^2)\\) |

Điều này giải thích vì sao nhiều model 2025–2026 cùng chuyển sang factorized attention: có thể tăng context length và số biến trong khi kiểm soát chi phí.

Models tiêu biểu: TimesFM 3.0, Chronos-2, Toto 2.0, t0-gamma và Timestral (với covariate-aware attention).

### 4.4. Recurrent / State Space Models

Hướng này không dùng temporal self-attention theo cách Transformer truyền thống, mà cập nhật trạng thái theo thời gian:

\\[ h_t=f\_\theta(h\_{t-1},x_t) \\]

\\[ \hat y\_{t+1}=g\_\theta(h_t) \\]

Trong các State Space Models tuyến tính có tham số phụ thuộc input, một dạng phương trình trạng thái là:

\\[ h_t=A_t h\_{t-1}+B_t x_t \\]

Ưu điểm lớn là streaming inference: có thể tiếp tục từ state trước đó thay vì đưa toàn bộ historical context qua Transformer mỗi lần có quan sát mới.

TiRex-2 là một ví dụ cụ thể sử dụng xLSTM cho temporal mixing và group attention cho variate mixing. Kiến trúc hỗ trợ xử lý streaming về mặt thiết kế, nhưng bản open-source TiRex-2 hiện không cung cấp incremental state-carrying API; khả năng này thuộc sản phẩm PRO.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://nx-ai.github.io\&sz=32)

TiRex-2+1



### 4.5. Generative density / flow-matching models

Một hướng khác là học phân phối tương lai thay vì trực tiếp dự đoán point hoặc quantiles.

Ví dụ: Sundial.

Thay vì dự đoán một giá trị duy nhất, model học trường vector giúp biến một phân phối ban đầu thành phân phối time-series patches tương lai:

\\[ \frac{dz_s}{ds} =v\_\theta(z_s,s\mid Y\_{\mathrm{past}}) \\]

Trong đó \\(s\\) là thời gian của quá trình sinh mẫu (generation time), không phải timestamp của chuỗi gốc.

`Historical patches → Transformer context → Conditional flow model → Sample future patches`

Mỗi lần lấy mẫu có thể tạo một quỹ đạo tương lai khác nhau. Sundial dùng TimeFlow Loss dựa trên flow matching cho continuous-valued time series, tránh phải rời rạc hóa giá trị thành token IDs.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://proceedings.mlr.press\&sz=32)

Proceedings of Machine Learning Research



### 4.6. Mixture-of-Experts (MoE)

Các model như Time-MoE và Timer-S1 sử dụng nhiều feed-forward experts và routing network. Mỗi token chỉ kích hoạt một tập con experts:

\\[ h'=\sum\_{e\in\operatorname{TopK}(r(h))} w_e(h)\operatorname{Expert}\_e(h) \\]

Điểm khác với ordinary Transformer nằm ở phần FFN/MLP có expert routing, không nhất thiết nằm ở attention.

Timer-S1 kết hợp decoder-only sparse MoE với TimeSTP để dự đoán nhiều bước theo phương pháp serial-token prediction; model có 8,3B total parameters nhưng chỉ kích hoạt khoảng 0,75B parameters trên mỗi token.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://huggingface.co\&sz=32)

Hugging Face+1



## 5. Phân tích chi tiết kiến trúc từng model

## 5.1. Google TimesFM 3.0 — Decoder-only + 2D attention + parallel forecasting

[TimesFM-3: A zero-shot foundation model for multivariate forecasting](https://images.openai.com/static-rsc-4/GR5EVv9FJ3WDFr6D2ul89TpyhQ6RMGsQ4qaMU_cvBwAsesvXWrhN6kKiEgTLbcY6d0uckAsYfSvcndA2NcySOGDS65Ekuae99J9qId8Z9Mpb94uFh_uRZ6lBY_-lpkbsyIb0QAoYn2ghyHhy8CC2TuwGI1bRb6-TvatrUw_2syk?purpose=inline)

TimesFM 3.0

330M parameters · Patch size 32 · 20 Transformer layers · 9 output quantiles

[Official architecture explanation](https://research.google/blog/timesfm-3-a-zero-shot-foundation-model-for-multivariate-forecasting/?utm_source=chatgpt.com)

Input:

`Multiple targets + Past covariates + Known-future covariates + masks`

Pipeline kiến trúc:

```
Multivariate Time Series
         │
Per-series Normalization / RevIN
         │
Patchify (32 observations/patch)
         │
Role-aware Patch Embedding
         │
Input Residual Block
         │
┌─────────────────────────┐
│ Causal Temporal Attn    │
│ Full Variate Attn       │ × Transformer stack
│ Feed Forward / Residual │
└─────────────────────────┘
         │
Output Residual / Forecast Head
         │
9 Quantiles × Targets × Horizon
```

Các đặc điểm quan trọng:

Thứ nhất — 2D attention. Causal temporal attention học lịch sử của mỗi biến, full variate attention học quan hệ giữa targets và covariates.

Thứ hai — lookahead embedding cho future covariates. Một token của known-future covariate có thể kết hợp patch hiện tại với những patch tương lai đã biết. Target tương lai vẫn bị mask, do đó không được dùng future ground truth.

Thứ ba — Contiguous Patch Masking (CPM). TimesFM 3.0 nối future placeholder patches vào sau context và dự báo các patch này đồng thời trong một lần forward, thay vì autoregressively sinh từng patch.

Ví dụ:

Inference với history dài 512, horizon dài 64

1

2

3

4

5

6

7

8

?

Sơ đồ rút gọn: mỗi ô màu xanh đại diện 64 điểm context; dấu hỏi đại diện horizon. Bên trong model, input vẫn được chia theo patch size 32.

Single forward pass

Toàn bộ 64 bước dự báo + quantiles

Output: point forecast và 9 quantiles, từ 0,1 đến 0,9, cho mỗi target/time step.

Điểm nghiên cứu nổi bật: Kết hợp parallel long-horizon forecasting và cross-variate representation trong decoder-only backbone. Model card còn mô tả iterative RevIN và output forecast patch length 64.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://research.google\&sz=32)

Google Research+1



## 5.2. AWS Chronos-2 — Encoder + Time/Group Attention + Quantile Head

[Introducing Chronos-2: From univariate to universal forecasting - Amazon Science](https://images.openai.com/static-rsc-4/-JakE8xeUOFKHPUNHb1I8wFunKKl8E1dP8xpoMP7UzRZuL6rWHTOt-eYuJY1M8QT5LXs2T2H9zI6qHs-XXyG-gDONVRQPz4KmunXu4W8Kzdsc3z6bkqmqKSSZgQPdNgBWco6QTsSm4wrlOkP_Gm8vWHKjqHxq0N_II3jd8JXmIY?purpose=inline)

Chronos-2

120M parameters · Continuous patch embeddings · Group attention

[Amazon Science technical overview](https://www.amazon.science/blog/introducing-chronos-2-from-univariate-to-universal-forecasting?utm_source=chatgpt.com)

Input:

- Target series histories.
- Optional covariates, có thể bao gồm known-future values.
- Group IDs, masks và vị trí thời gian.

Kiến trúc:

```
Targets + Covariates
         │
Robust Instance Normalization
         │
Time Index + Validity Mask
         │
Patchify + Residual MLP Embedding
         │
┌────────────────────────┐
│ Time Self-Attention    │
│ Group Self-Attention   │ × N
│ Feed-Forward Network   │
└────────────────────────┘
         │
Future Patch Representations
         │
Multi-patch Quantile Head
         │
Unscale → Probabilistic Forecast
```

Khác biệt cốt lõi: Group Attention.

Chronos-2 cho phép gom nhiều series liên quan thành cùng một nhóm. Attention theo trục thời gian xử lý từng series; attention theo group truyền thông tin giữa các series thuộc cùng group tại một patch index.

Ví dụ với ba cửa hàng:

| Series        | Group ID | Cơ chế                 |
| ------------- | -------- | ---------------------- |
| Sales Store A | 1        | Có thể học từ B        |
| Sales Store B | 1        | Có thể học từ A        |
| Sales Store C | 2        | Được tách khỏi group 1 |

Nhờ vậy, model có thể học quan hệ giữa các biến của một hệ thống hoặc tận dụng chuỗi tương tự trong bối cảnh in-context cross-learning.

Chronos-2 dùng encoder stack và output residual projection để dự báo trực tiếp nhiều future patches. Trong implementation, `quantile_preds` có dạng `(batch_size, num_quantiles, forecast_length)` ở cấp flattened series trước khi được ghép lại theo nhóm.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.amazon.science\&sz=32)

Amazon Science+1



Vì sao khác Chronos gốc?

Chronos gốc dùng discrete token IDs và autoregressive sampling. Chronos-2 dùng continuous patch embeddings, group attention và direct multi-patch quantile predictions. Đây là sự thay đổi đáng kể cả về cách biểu diễn input lẫn cách sinh output.

## 5.3. Mistral Timestral — Decoupled Horizon Forecasting

Kiến trúc rất đáng chú ý cho research năm 2026

Input:

Targets, past-only covariates, known-future covariates; hỗ trợ các covariate số và categorical đã được mã hóa.

Kiến trúc Timestral-209M:

- 24 Transformer layers.
- Embedding dimension 768.
- Patch size 32.
- Temporal và variate attention.
- Context tối đa 32.768 time steps.
- Horizon tối đa 1.024 bước cho một forward pass.
- 21 quantiles.

[image](https://www.google.com/s2/favicons?domain=https://huggingface.co\&sz=32)

Hugging Face

Điểm khác biệt: Decoupled Horizon Forecasting (DHF).

Ở masked-horizon forecasting, các future patches bị mask để model dự đoán. Nhưng trong training, nếu chọn một đoạn làm target bị che, các quan sát thực ở đoạn đó cũng không còn đóng vai trò context cho các vị trí tiếp theo.

Timestral tách hai nhiệm vụ:

1. Các observed tokens giữ toàn bộ history hợp lệ.
2. Các learned forecast tokens đọc history để dự báo tương lai.

Minh họa Decoupled Horizon Forecasting

Observed History

x1

x2

x3

x4

x5

x6

Causal Transformer / Context Representations

f1

Learned forecast token

f2

Learned forecast token

f3

Learned forecast token

Parallel quantile forecasts

DHF giúp tách reconstruction/missing-value modeling khỏi horizon prediction, tận dụng đầy đủ observed history cho việc tạo forecast tokens.

Timestral còn sử dụng role-aware covariate attention: target không được đọc target tương lai, nhưng có thể khai thác known-future covariates. Model được pretrain chủ yếu trên synthetic series, sau đó post-train trên hỗn hợp synthetic và real data.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://mistral.ai\&sz=32)

Mistral



Một lưu ý: Mistral vẫn ghi technical report là coming soon trên model card tại thời điểm kiểm tra; mô tả trên dựa vào blog kỹ thuật và checkpoint/model card chính thức, chưa phải phân tích đầy đủ mọi training detail.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://huggingface.co\&sz=32)

Hugging Face



## 5.4. t0-gamma — Causal Time Attention + Group Attention

Model của The Forecasting Company sử dụng decoder-style patch Transformer với các đặc điểm được công bố cụ thể:

| Thành phần             | t0-gamma                     |
| ---------------------- | ---------------------------- |
| Parameters             | \~256M                       |
| Transformer layers     | 24                           |
| Time attention layers  | 16                           |
| Group attention layers | 8                            |
| Layer pattern          | 2 time layers, 1 group layer |
| Embedding dimension    | 1.024                        |
| Attention heads        | 8                            |
| Patch size             | 32                           |
| Quantiles              | 21                           |

Pipeline:

`Targets / Covariates → Causal scaling + arcsinh → Patch embedding(value, time, mask) → Alternating time/group attention → Quantile head`

t0-gamma dùng contiguous patch masking và có thể giải mã tối đa 1.024 time steps trong một forward pass; horizon dài hơn sử dụng autoregressive rollout.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://huggingface.co\&sz=32)

Hugging Face+1



Về research, t0-gamma là một đối chứng phù hợp cho TimesFM 3.0 vì cả hai đều học temporal và variate dependencies bằng patch Transformers nhưng khác nhau về chi tiết preprocessing, attention stack, training data và head.

## 5.5. Datadog Toto 2.0 — Scaling Transformer cho high-dimensional data

Input: Multivariate numerical time series, missing masks, series grouping.

Kiến trúc:

`Multivariate patches → Causal normalization + arcsinh → Residual patch embedding → Time/Variate Transformer → Quantile head`

Điểm đặc trưng:

- Decoder-only patch Transformer.
- Alternating causal time attention và variate attention.
- Contiguous Patch Masking cho parallel forecasting.
- Quantile outputs tại 9 levels (0,1–0,9).
- u-μP scaling, giúp chuyển training recipe giữa các kích thước 4M–2.5B parameters.

Toto tập trung vào observability time series, ví dụ CPU, memory, latency, throughput và network metrics trong hệ thống IT.

Khác biệt giữa hai phiên bản:

|                      | Toto 1.0                          | Toto 2.0                   |
| -------------------- | --------------------------------- | -------------------------- |
| Backbone             | Decoder Transformer               | Decoder Transformer + u-μP |
| Output               | Student-T mixture distribution    | Quantile head              |
| Training / forecast  | Next-patch probabilistic modeling | CPM + parallel horizon     |
| Time/variable mixing | Factorized space–time             | Alternating time/variate   |
| Exogenous covariates | Có hỗ trợ trong 1.0               | Chưa có ở bản 2.0 hiện tại |

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub+2

## 5.6. TiRex-2 — xLSTM + Asymmetric Variate Attention

Đây là model có khác biệt kiến trúc lớn so với các Transformer thuần.

Input: Targets, past covariates và known-future covariates.

Kiến trúc: 12 blocks, mỗi block gồm temporal xLSTM mixer và variate group-attention mixer.

```
Multivariate Data
        │
Padding + Scaling + Patchify
        │
Residual MLP Patch Embedding
        │
┌────────────────────────────┐
│ Time Mixer                 │
│  - Forward xLSTM: Targets  │
│  - Forward xLSTM: Past Cov │
│  - Bi-XlSTM: Known Future  │
│                            │ × 12
│ Variate Mixer              │
│  - Group Attention         │
│  - Asymmetric Mask         │
└────────────────────────────┘
        │
Target Token Quantile Head
        │
Probabilistic Forecast
```

Bi-XlSTM trong sơ đồ là cách viết rút gọn cho forward và reverse xLSTM kết hợp; không phải tên một module API chính thức.

Innovation 1 — Bidirectional processing có điều kiện.

Targets và past-only covariates được xử lý theo chiều thời gian tiến. Known-future covariates có thể được đọc theo cả hai chiều vì các giá trị tương lai đó đã biết.

Innovation 2 — Asymmetric attention mask.

TiRex-2 không cho phép thông tin target rò rỉ ngược vào covariates, vì covariates có thể được xử lý bidirectionally. Đây là biện pháp chống multi-hop data leakage giữa các Transformer/recurrent blocks.

Innovation 3 — Streaming-oriented recurrent backbone.

Cập nhật xLSTM state có thể hiệu quả khi luồng quan sát mới đến liên tục. Các tác giả báo cáo 38,4M active parameters ở univariate mode và thêm 44,1M khi kích hoạt variate mixer.

Nguồn phân tích rất nên đọc: [Inside TiRex-2: Bidirectional where it's safe, causal where it matters](https://marcopichler.com/blog/tirex2-architecture?utm_source=chatgpt.com).&#x20;

[image](https://www.google.com/s2/favicons?domain=https://marcopichler.com\&sz=32)

Marco Pichler+1



## 5.7. Moirai 1.0 và Moirai 2.0 — Hai hướng kiến trúc khác nhau

Moirai là ví dụ rõ nhất cho việc foundation model có thể thay đổi thiết kế giữa các thế hệ.

| Thành phần          | Moirai 1.0                 | Moirai 2.0                       |
| ------------------- | -------------------------- | -------------------------------- |
| Backbone            | Masked Transformer encoder | Decoder-only Transformer         |
| Patching            | Nhiều patch sizes          | Một patch size                   |
| Cross-variable      | Any-variate attention      | Kiến trúc decoder đơn giản hóa   |
| Training            | Masked forecasting         | Causal / multi-token forecasting |
| Output              | Mixture distribution       | Quantile predictions             |
| Loss                | Negative log-likelihood    | Quantile loss                    |
| Forecast generation | Dự báo masked horizon      | Recursive multi-token decoding   |

Moirai 1.0 sử dụng any-variate attention để xử lý số biến không cố định, nhiều patch projection layers để thích ứng với nhiều sampling frequencies, và mixture distribution output để tạo probabilistic forecasts.

Moirai 2.0 chuyển sang decoder-only, một patch size và quantile loss. Salesforce công bố sự thay đổi này giúp đơn giản hóa kiến trúc đồng thời cải thiện speed/accuracy trong các thực nghiệm của họ.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.salesforce.com\&sz=32)

Salesforce+2



Điểm quan trọng cho nghiên cứu là kiến trúc phức tạp hơn không nhất thiết tốt hơn. Dữ liệu pretraining, training loss và decoding strategy có thể tác động lớn hơn những block mới.

## 5.8. Chronos family — Sự tiến hóa từ token-based sang patch-based

| Phiên bản           | Input encoding               | Backbone                         | Output generation              |
| ------------------- | ---------------------------- | -------------------------------- | ------------------------------ |
| Chronos (2024)      | Quantized discrete tokens    | T5 encoder–decoder               | Autoregressive samples         |
| Chronos-Bolt (2024) | Continuous patches           | T5 encoder–decoder               | Direct multi-step quantiles    |
| Chronos-2 (2025)    | Patches + time/mask metadata | Encoder với time/group attention | Parallel multi-patch quantiles |

[image](https://www.google.com/s2/favicons?domain=https://huggingface.co\&sz=32)

amazon/chronos-t5-base at main+2

Đây là case study rất hay về cách thiết kế TSFM: từ việc áp dụng language modeling trực tiếp trên chuỗi số, Amazon dần chuyển sang kiến trúc chuyên biệt hơn cho numerical forecasting và cross-series learning.

## 5.9. Các kiến trúc khác cần chú ý

| Model             | Pipeline kiến trúc                                                              | Input → Output                                      |
| ----------------- | ------------------------------------------------------------------------------- | --------------------------------------------------- |
| Sundial           | Patch Transformer → TimeFlow head → Conditional flow sampling                   | History → Future trajectory samples                 |
| MOMENT            | Masked patches → Transformer encoder → Reconstruction / task heads              | Series → Embeddings, imputations, classifications   |
| IBM TSPulse       | Temporal/spectral embeddings → Masked reconstruction → Task-specific fusion     | Series → Anomaly score, embeddings, classifications |
| IBM TinyTimeMixer | Adaptive patching → MLP patch/feature/channel mixing → Forecast head            | History → Future values                             |
| IBM FlowState     | SSM encoder → Functional basis decoder                                          | History + temporal scale → Continuous-time forecast |
| Time-LLM          | Patch reprogramming + text prompt → Frozen LLM → Projection                     | Numeric series + prompt → Forecast values           |
| VisionTS          | Series → 2D image → Visual masked autoencoder → Inverse transform               | Series → Future values                              |
| VisionTS++        | Multivariate image conversion → Vision backbone → Quantile reconstruction heads | Multiple series → Forecast quantiles                |

[image](https://www.google.com/s2/favicons?domain=https://proceedings.mlr.press\&sz=32)

Proceedings of Machine Learning Research+7

Có hai hướng cần phân biệt đặc biệt:

IBM FlowState không giống Sundial. FlowState dùng State Space Model encoder và functional basis decoder để thích ứng sampling rates và horizon; Sundial dùng flow matching để sinh mẫu tương lai từ phân phối. Từ flow trong hai tên không có nghĩa chúng cùng kiến trúc.

MOMENT và TSPulse không nên đánh giá chỉ bằng MASE. Mục đích chính của chúng còn bao gồm representation learning, anomaly detection, imputation, classification và similarity search. Chúng nên được so sánh bằng các downstream metrics tương ứng.

## 6. So sánh tổng hợp các thiết kế kiến trúc

| Model        | Tokenization              | Backbone                | Cross-variate learning        | Forecast decoder          |
| ------------ | ------------------------- | ----------------------- | ----------------------------- | ------------------------- |
| TimesFM 3    | Continuous patches        | Decoder Transformer     | Full variate attention        | Parallel masked horizon   |
| Chronos-2    | Continuous patches        | Encoder Transformer     | Group attention               | Parallel quantiles        |
| Timestral    | Continuous patches        | Transformer             | Covariate-aware attention     | Decoupled forecast tokens |
| t0-gamma     | Continuous patches        | Decoder Transformer     | Group attention               | Parallel masked horizon   |
| Toto 2.0     | Continuous patches        | Decoder Transformer     | Variate attention             | Parallel masked horizon   |
| TiRex-2      | Continuous patches        | xLSTM + attention       | Asymmetric group attention    | Next-patch quantiles      |
| Moirai 1.0   | Multi-size patches        | Masked encoder          | Any-variate attention         | Mixture distribution      |
| Moirai 2.0   | Continuous patches        | Decoder Transformer     | Simplified universal modeling | Multi-token quantile      |
| Chronos gốc  | Discrete values           | T5 Transformer          | Chủ yếu independent           | Autoregressive sampling   |
| Chronos-Bolt | Continuous patches        | T5 encoder–decoder      | Chủ yếu independent           | Direct quantiles          |
| Sundial      | Continuous patches        | Transformer + flow head | Chủ yếu independent           | Generative sampling       |
| MOMENT       | Masked patches            | Transformer encoder     | Chủ yếu channel-wise          | Task-specific head        |
| FlowState    | Continuous representation | SSM + basis decoder     | Không phải điểm nhấn chính    | Functional forecasting    |
| Timer-S1     | Time-series tokens        | Sparse MoE Transformer  | Không phải điểm nhấn chính    | Serial-token prediction   |

“Chủ yếu independent” mô tả cách xử lý phổ biến hoặc backbone chính, không loại trừ các wrapper, adaptation hay biến thể khác. Các nhóm này cũng không loại trừ nhau: một model có thể đồng thời là decoder-only, patch-based, multivariate và probabilistic.

## 7. Training objectives: Vì sao các model tạo output khác nhau?

Backbone giống nhau nhưng loss khác nhau có thể dẫn đến hành vi dự báo rất khác nhau.

### 7.1. Cross-entropy loss

Dùng trong Chronos gốc với discrete token vocabulary:

\\[ \mathcal L\_{\mathrm{CE}} =-\sum\_{t}\log p\_\theta(z_t\mid z\_{\<t}) \\]

Model học xác suất của token giá trị tiếp theo và có thể sample nhiều quỹ đạo tương lai.

### 7.2. Point regression loss

Các output head dự đoán point trực tiếp có thể học bằng MSE:

\\[ \mathcal L\_{\mathrm{MSE}} =\frac{1}{H}\sum\_{h=1}^{H}(y\_{t+h}-\hat y\_{t+h})^2 \\]

Thích hợp cho point accuracy, nhưng không tự cung cấp uncertainty.

### 7.3. Quantile / Pinball loss

Phổ biến trong TimesFM 3.0, Chronos-2, Timestral, Toto 2.0 và t0.

\\[ \mathcal L\_{\mathrm{pinball}} =\frac{1}{|\mathcal Q|H} \sum\_{\tau\in\mathcal Q} \sum\_{h=1}^{H} \max\left( \tau e\_{h,\tau}, (\tau-1)e\_{h,\tau} \right) \\]

với \\(e\_{h,\tau}=y_h-\hat q\_{\tau,h}\\).

Model có thể dự báo nhiều phân vị, ví dụ 10%, 50%, 90%, không cần giả định dữ liệu tuân theo Gaussian.

### 7.4. Negative log-likelihood

Dùng trong các model có parametric density head, như Moirai 1.0 hay Toto 1.0:

\\[ \mathcal L\_{\mathrm{NLL}} =-\log p\_\theta(Y\_{\mathrm{future}}\mid X) \\]

Model học tham số của phân phối (hoặc mixture distributions), rồi dùng chúng để tính quantiles hoặc sinh mẫu.

### 7.5. Masked reconstruction

Dùng trong MOMENT, TSPulse và một số encoder-based models:

\\[ \mathcal L\_{\mathrm{mask}} =\frac{1}{|\mathcal M|} \sum\_{i\in\mathcal M}(x_i-\hat x_i)^2 \\]

Model phải khôi phục những patches bị che từ ngữ cảnh còn lại. Điều này khuyến khích học representations hữu ích hơn cho các tác vụ như anomaly detection và imputation.

## 8. Ví dụ đầy đủ: Dữ liệu đi qua model như thế nào?

Giả sử xây dựng một ứng dụng dự báo điện năng cho ba nhà máy.

Cấu hình ví dụ

## 512

Context L

## 96

Horizon H

## 3

Targets

## 32

Patch size

Dùng batch size 8, hai past covariates và ba known-future covariates:

```
past_target = torch.randn(8, 512, 3)past_covariates = torch.randn(8, 512, 2)known_future = torch.randn(8, 608, 3)
```

Giả sử model dùng patch size 32 và cùng patchify các biến vào một grid:

| History patches mỗi biến | 512 / 32 = 16 |
| ------------------------ | ------------- |
| Future patches mỗi biến  | 96 / 32 = 3   |
| Tổng series/covariates   | 3 + 2 + 3 = 8 |
| Token grid sau patching  | [8, 8, 19, d] |

Tensor minh họa cho kiến trúc có future placeholder tokens và không loại bỏ các patch covariate trong grid. Không phải intermediate tensor của mọi model.

Sau đó, model có factorized attention sẽ thực hiện:

Temporal mixing: Xử lý 19 patch positions theo thời gian, có attention mask phù hợp với mỗi vai trò biến.

Variate mixing: Xử lý 8 series ở mỗi patch position, học tương tác giữa các nhà máy, historical measurements và known-future inputs.

Quantile head: Với 9 quantiles, tạo forecast tensor theo quy ước:

```
forecast_quantiles.shape == (8, 96, 3, 9)# batch x horizon x targets x quantiles
```

Lấy median (q50) sẽ được point forecast với shape `(8, 96, 3)`, sau đó unscale để chuyển về đơn vị điện năng ban đầu.

Đó là cách một bài toán time-series forecasting thực tế có thể được đưa vào cùng một TSFM mà không cần xây dựng một model riêng cho từng nhà máy.

## 9. Các trục kiến trúc nên nghiên cứu sâu hơn

Nếu mục tiêu tiếp theo là đọc source code, tái hiện mô hình hoặc phát triển kiến trúc mới, mình khuyên phân tích theo năm trục:

| Trục nghiên cứu        | Câu hỏi quan trọng                                           | Models đại diện                             |
| ---------------------- | ------------------------------------------------------------ | ------------------------------------------- |
| Tokenization           | Patch size cố định hay adaptive? Discrete hay continuous?    | Chronos, Moirai, TimesFM                    |
| Temporal modeling      | Causal attention, encoder attention hay recurrent state?     | TimesFM, Chronos-2, TiRex-2                 |
| Cross-variate learning | Independent, full, grouped hay asymmetric?                   | Toto, t0, Chronos-2, TiRex-2                |
| Forecast generation    | AR, parallel CPM, learned forecast tokens hay flow sampling? | Moirai 2, TimesFM 3, Timestral, Sundial     |
| Pretraining objectives | CE, quantile, NLL, masked reconstruction hay flow matching?  | Chronos, Timestral, Moirai, MOMENT, Sundial |

Với phần lớn các TSFM mới, mình đánh giá temporal/variate mixing và decoding strategy là hai trục quan trọng nhất cần hiểu sâu. Chúng chi phối trực tiếp khả năng khai thác covariates, latency và chất lượng long-horizon forecasting.

## 10. Paper và source code để nghiên cứu kiến trúc

| Model       | Nguồn nên đọc                                                                                                           |
| ----------- | ----------------------------------------------------------------------------------------------------------------------- |
| TimesFM 3.0 | [GitHub / PyTorch implementation](https://github.com/google-research/timesfm?utm_source=chatgpt.com)                    |
| Chronos-2   | [Official implementation](https://github.com/amazon-science/chronos-forecasting?utm_source=chatgpt.com)                 |
| Timestral   | [Official source code](https://github.com/mistralai/timestral?utm_source=chatgpt.com)                                   |
| t0-gamma    | [Model card + architecture specification](https://huggingface.co/theforecastingcompany/t0-gamma?utm_source=chatgpt.com) |
| TiRex-2     | [Architecture deep dive từ đồng tác giả](https://marcopichler.com/blog/tirex2-architecture?utm_source=chatgpt.com)      |
| Toto 2.0    | [Official repository](https://github.com/DataDog/toto?utm_source=chatgpt.com)                                           |
| Moirai      | [Uni2TS / Moirai source code](https://github.com/SalesforceAIResearch/uni2ts?utm_source=chatgpt.com)                    |
| Sundial     | [ICML 2025 paper](https://proceedings.mlr.press/v267/liu25be.html?utm_source=chatgpt.com)                               |
| MOMENT      | [Official repository](https://github.com/moment-timeseries-foundation-model/moment?utm_source=chatgpt.com)              |
| FlowState   | [ICML 2026 paper](https://proceedings.mlr.press/v306/graf26a.html?utm_source=chatgpt.com)                               |

## Kết luận

Một cách đơn giản để ghi nhớ sự tiến hóa kiến trúc là:

TSFM: Học quy luật từ chuỗi thời gian đã pretrain

Language-style

Chronos gốc

Discrete tokens → AR generation

Forecast-specialized

TimesFM 3, Chronos-2, Timestral

Patches → Cross-series attention → Parallel output

Alternative backbone

TiRex, Sundial, FlowState

Recurrence / Flow / SSM

Điểm mấu chốt: Không phải model nào cũng học theo kiểu dự đoán một bước rồi lặp lại. Xu hướng nổi bật là dùng continuous patch embeddings, học quan hệ đồng thời theo time và variate, sau đó trực tiếp dự đoán nhiều bước tương lai cùng quantiles trong một lần forward.

Nếu chọn ba kiến trúc làm trọng tâm nghiên cứu kỹ thuật, mình sẽ ưu tiên TimesFM 3.0 để hiểu masked parallel forecasting, Chronos-2 để hiểu group attention/in-context learning và Timestral để hiểu learned forecast tokens cùng covariate-aware attention. Sau đó đối chiếu với TiRex-2 để thấy recurrent backbone giải quyết bài toán streaming khác Transformer như thế nào.