---
title: "Giai đoạn 2 — Step 6: Đọc GDP, CPI và lãi suất thực"
tags:
  - kinh-te-vi-mo
  - gdp
  - cpi
  - lam-phat
  - lai-suat-thuc
aliases:
  - "Đọc bản tin GDP và CPI cho người mới"
---

# Giai đoạn 2 — Step 6: Đọc GDP, CPI và lãi suất thực

> [!abstract] Mục tiêu của bài
> Sau bài này, bạn có thể đọc một bản tin GDP/CPI và trả lời năm câu: **đang đo cái gì, danh nghĩa hay thực, headline hay core, so với kỳ nào, đã annualized hay chưa?** Bạn cũng sẽ giải thích được vì sao CPI khác GDP deflator và vì sao lãi suất ngân hàng cao chưa chắc làm sức mua tăng.

Đây là bước đo lường nền tảng của kinh tế vĩ mô. Trước khi bàn về tăng trưởng, thất nghiệp hay chính sách tiền tệ, ta phải biết con số trên bản tin thực sự biểu thị điều gì. Hai lỗi phổ biến nhất của người mới là xem mọi mức tăng bằng tiền đều là tăng sản lượng và so sánh hai tỷ lệ có kỳ đo khác nhau.

---

## 1. Bản đồ tư duy: ba lớp cần tách riêng

Hãy hình dung nền kinh tế qua ba lớp:

1. **Lượng hàng hóa và dịch vụ được sản xuất:** real GDP.
2. **Mức giá của hàng hóa và dịch vụ:** CPI hoặc GDP deflator.
3. **Giá trị tính bằng tiền:** nominal GDP, lương danh nghĩa, lãi suất danh nghĩa.

Mối quan hệ cốt lõi là:

$$
\text{Giá trị danh nghĩa} \approx \text{Lượng thực} \times \text{Mức giá}
$$

Vì vậy, doanh thu hay GDP tính bằng tiền tăng chưa đủ để kết luận nền kinh tế sản xuất nhiều hơn. Nó có thể tăng vì **lượng tăng**, **giá tăng**, hoặc cả hai.

> [!example] Ví dụ trực giác
> Một quán bán 100 bát phở với giá 40.000 đồng, doanh thu là 4 triệu đồng. Năm sau vẫn bán 100 bát nhưng giá tăng lên 44.000 đồng, doanh thu thành 4,4 triệu đồng. Giá trị danh nghĩa tăng 10%, nhưng lượng sản xuất thực không đổi.

Nội dung nền tảng được tổng hợp trong [GDP — income-expenditure identity, measurement rules, components, and real versus nominal](../wiki/gdp-income-expenditure-measurement-and-real-vs-nominal.md) và [Correcting Economic Variables for Inflation](../wiki/correcting-for-inflation-real-vs-nominal-indexation-and-regional-parities.md).

---

# Phần I — GDP: nền kinh tế sản xuất bao nhiêu?

## 2. GDP là gì?

**Tổng sản phẩm trong nước (GDP)** là giá trị thị trường của tất cả hàng hóa và dịch vụ **cuối cùng**, được **sản xuất trong phạm vi một quốc gia**, trong **một khoảng thời gian nhất định**.

Mỗi cụm từ đều có tác dụng:

- **Giá trị thị trường:** dùng giá để cộng những sản phẩm khác loại.
- **Hàng hóa và dịch vụ cuối cùng:** tránh tính trùng đầu vào trung gian.
- **Được sản xuất:** chỉ tính sản xuất hiện tại; bán lại xe cũ không tạo ra chiếc xe mới.
- **Trong nước:** xét nơi sản xuất, không xét quốc tịch chủ sở hữu.
- **Trong một khoảng thời gian:** GDP là một **dòng** trong quý hoặc năm, không phải lượng tài sản tại một thời điểm.

### 2.1 Vì sao thu nhập bằng chi tiêu?

Một giao dịch có hai mặt: khoản người mua chi ra là khoản người bán nhận được. Ở cấp toàn nền kinh tế, tổng chi tiêu cho sản phẩm cuối cùng bằng tổng thu nhập phát sinh từ việc sản xuất các sản phẩm đó, sai khác thực tế chỉ do nguồn dữ liệu và sai số thống kê.

### 2.2 Vì sao chỉ tính hàng hóa cuối cùng?

Giả sử:

- quặng bán cho nhà máy thép: 4.200;
- thép bán cho hãng xe: 9.000;
- ô tô bán cho người dùng cuối: 21.500.

GDP không phải $4.200+9.000+21.500=34.700$, vì quặng đã nằm trong giá thép và thép đã nằm trong giá xe. Có hai cách đúng:

- chỉ tính chiếc xe cuối cùng: **21.500**;
- hoặc cộng giá trị gia tăng: $4.200+(9.000-4.200)+(21.500-9.000)=21.500$.

Ngoại lệ quan trọng là **hàng tồn kho**. Một sản phẩm đã làm ra nhưng chưa bán vẫn là sản lượng của kỳ hiện tại, nên phần tăng tồn kho được tính là đầu tư. Khi hàng được lấy khỏi kho để bán ở kỳ sau, tồn kho giảm sẽ bù trừ phần chi tiêu của người mua.

## 3. GDP theo chi tiêu: $Y=C+I+G+NX$

Đây là **đồng nhất thức kế toán**, đúng theo cách các khoản chi được phân loại:

$$
Y=C+I+G+NX=C+I+G+X-IM
$$

| Thành phần | Nội dung | Bẫy thường gặp |
|---|---|---|
| $C$ — Consumption | Chi tiêu hộ gia đình cho hàng hóa và dịch vụ | Nhà mới không nằm trong $C$ |
| $I$ — Investment | Vốn kinh doanh, nhà ở mới, sở hữu trí tuệ và thay đổi tồn kho | Mua cổ phiếu không phải “đầu tư” trong phép tính GDP |
| $G$ — Government purchases | Chính phủ mua hàng hóa, dịch vụ và đầu tư công | Trợ cấp, lương hưu không trực tiếp nằm trong $G$ vì là chuyển nhượng |
| $NX=X-IM$ — Net exports | Xuất khẩu trừ nhập khẩu | Nhập khẩu bị trừ để loại phần sản xuất ở nước ngoài đã nằm trong $C$, $I$ hoặc $G$ |

> [!example] Vì sao mua xe nhập khẩu không làm GDP trong nước tăng?
> Một hộ mua xe nhập khẩu trị giá 1 tỷ đồng làm $C$ tăng 1 tỷ, nhưng $IM$ cũng tăng 1 tỷ nên $NX$ giảm 1 tỷ. Tác động trực tiếp lên GDP trong nước là 0. Phép trừ không có nghĩa nhập khẩu “xấu”; nó chỉ bảo đảm GDP đo đúng sản xuất **trong nước**.

### 3.1 Tự phân loại nhanh

- Một hãng xây nhà máy mới trong nước → $I$, có trong GDP.
- Hộ gia đình mua căn nhà mới xây → đầu tư nhà ở $I$, không phải $C$.
- Hộ mua nhà cũ → giá trị căn nhà không được tính lại; phí môi giới hiện tại là dịch vụ và được tính.
- Chính phủ trả trợ cấp thất nghiệp → không trực tiếp thuộc $G$; nếu người nhận dùng tiền mua hàng, khoản mua có thể đi vào $C$.
- Doanh nghiệp sản xuất hàng nhưng chưa bán → tăng tồn kho, thuộc $I$.
- Nhà đầu tư mua cổ phiếu trên sàn → giao dịch tài sản tài chính, không phải sản phẩm mới nên không trực tiếp vào GDP.

---

## 4. Nominal GDP và real GDP

### 4.1 Nominal GDP: giá hiện hành

$$
\text{Nominal GDP}_t=\sum_i P_{i,t}Q_{i,t}
$$

Cả giá $P$ và lượng $Q$ đều thay đổi. Vì vậy nominal GDP tăng không cho biết phần nào đến từ sản lượng và phần nào đến từ giá.

### 4.2 Real GDP: giữ giá cố định để quan sát lượng

Trong minh họa đơn giản với năm gốc $0$:

$$
\text{Real GDP}_t=\sum_i P_{i,0}Q_{i,t}
$$

Giá được giữ ở năm gốc, nên thay đổi phản ánh lượng sản xuất. Các hệ thống tài khoản hiện đại thường dùng **chain-linking** thay vì giữ mãi một bộ giá cố định, nhưng trực giác không đổi: real GDP nhằm tách tăng trưởng sản lượng khỏi tăng giá.

### 4.3 Ví dụ hai mặt hàng

| Năm | Giá xúc xích | Lượng | Giá hamburger | Lượng |
|---|---:|---:|---:|---:|
| 2016 | 1 | 100 | 2 | 50 |
| 2017 | 2 | 150 | 3 | 100 |

- Nominal GDP 2016: $1\times100+2\times50=200$.
- Nominal GDP 2017: $2\times150+3\times100=600$.
- Real GDP 2017 theo giá 2016: $1\times150+2\times100=350$.

Nominal GDP tăng từ 200 lên 600, tức 200%; real GDP chỉ tăng từ 200 lên 350, tức 75%. Phần chênh lớn đến từ giá tăng.

> [!tip] Quy tắc đọc báo
> Nếu bản tin nói “nền kinh tế tăng trưởng”, chỉ số phù hợp thường là **real GDP** hoặc **real GDP per capita**. Tuy nhiên đừng đoán: hãy tìm các từ *real*, *constant prices*, *volume*, *chained prices* hoặc mô tả “đã loại trừ biến động giá”.

---

## 5. GDP deflator: mức giá của sản lượng trong nước

$$
\text{GDP deflator}_t=\frac{\text{Nominal GDP}_t}{\text{Real GDP}_t}\times100
$$

Trong ví dụ trên, deflator năm 2017 là:

$$
\frac{600}{350}\times100\approx171{,}4
$$

Nếu chỉ số năm gốc là 100, mức 171,4 nghĩa là mức giá của giỏ sản lượng được đo cao hơn khoảng 71,4% so với năm gốc. **Chỉ số 171,4 không có nghĩa lạm phát năm đó là 171,4%.** Lạm phát là phần trăm thay đổi của chỉ số giữa hai kỳ.

$$
\pi_t=\frac{D_t-D_{t-1}}{D_{t-1}}\times100\%
$$

---

# Phần II — CPI: chi phí sinh hoạt thay đổi thế nào?

## 6. CPI được xây dựng ra sao?

**Chỉ số giá tiêu dùng (CPI)** đo chi phí của một giỏ hàng hóa và dịch vụ đại diện cho người tiêu dùng. Quy trình nhập môn gồm năm bước:

1. Xác định giỏ hàng và trọng số từ hành vi chi tiêu.
2. Thu thập giá từng mặt hàng ở các kỳ.
3. Tính chi phí mua cùng giỏ đó ở mỗi kỳ.
4. Chọn kỳ gốc và chuẩn hóa chỉ số về 100.
5. Tính tỷ lệ thay đổi của CPI để có lạm phát.

$$
\text{CPI}_t=\frac{\text{Chi phí giỏ ở kỳ }t}{\text{Chi phí giỏ ở kỳ gốc}}\times100
$$

### 6.1 Ví dụ giỏ cố định

Giỏ gồm 4 xúc xích và 2 hamburger:

| Năm | Giá xúc xích | Giá hamburger | Chi phí giỏ | CPI, gốc 2016 |
|---|---:|---:|---:|---:|
| 2016 | 1 | 2 | $4\times1+2\times2=8$ | 100 |
| 2017 | 2 | 3 | $4\times2+2\times3=14$ | 175 |
| 2018 | 3 | 4 | $4\times3+2\times4=20$ | 250 |

Lạm phát 2018 không phải $250-175=75\%$. Phải chia cho mức ban đầu:

$$
\pi_{2018}=\frac{250-175}{175}\times100\%\approx42{,}9\%
$$

### 6.2 CPI không phải giá của một món hàng

CPI là trung bình có trọng số. Một mặt hàng tăng 20% không có nghĩa CPI tăng 20%. Tác động xấp xỉ phụ thuộc vào trọng số chi tiêu.

Ví dụ, nếu xăng chiếm 4% giỏ và giá xăng tăng 30%, trong khi mọi giá khác đứng yên, đóng góp trực tiếp xấp xỉ là:

$$
4\%\times30\%=1{,}2\text{ điểm phần trăm}
$$

Đây chỉ là phép gần đúng: trọng số, thay thế và các phương pháp điều chỉnh thực tế có thể làm kết quả khác.

---

## 7. Headline và core: hai câu hỏi khác nhau

- **Headline CPI / all-items CPI:** gồm toàn bộ nhóm hàng trong chỉ số. Đây là thước đo gần với thay đổi chi phí mà hộ tiêu dùng thực sự gặp.
- **Core CPI:** trong cách trình bày của Mankiw, loại thực phẩm và năng lượng vì hai nhóm này thường biến động mạnh trong ngắn hạn. Nó giúp quan sát xu hướng lạm phát dai dẳng hơn.

> [!warning] Core không có nghĩa là thực phẩm và năng lượng “không quan trọng”
> Hộ gia đình vẫn phải mua xăng và thức ăn. Core CPI là công cụ lọc nhiễu để phân tích xu hướng, không phải bản thay thế hoàn hảo cho chi phí sinh hoạt headline. Ngoài ra, định nghĩa “core” có thể khác theo cơ quan và quốc gia; luôn đọc chú thích của nguồn.

### Ví dụ

Giả sử headline CPI tăng 4,0% so với cùng kỳ, còn core CPI tăng 2,8%:

- Ta có thể nói giá tiêu dùng nói chung tăng nhanh hơn thước đo lõi.
- Một giả thuyết hợp lý là thực phẩm hoặc năng lượng tăng mạnh.
- Nhưng chưa thể khẳng định nguyên nhân nếu chưa xem phân rã các nhóm giá.
- Cũng chưa thể kết luận lạm phát chắc chắn sẽ sớm giảm: cú sốc năng lượng có thể lan sang vận tải, sản xuất, tiền lương và kỳ vọng.

---

## 8. Ba giới hạn kinh điển của CPI

CPI cố gắng đo số tiền cần thiết để duy trì mức sống, nhưng đây không phải phép đo hoàn hảo.

### 8.1 Thiên lệch thay thế

Giỏ cố định giả định người tiêu dùng tiếp tục mua cùng lượng dù giá tương đối thay đổi. Trên thực tế, họ có thể chuyển từ táo đang đắt sang lê rẻ hơn. Bỏ qua khả năng này có xu hướng làm mức tăng chi phí sinh hoạt được đo cao hơn.

### 8.2 Hàng hóa mới

Một sản phẩm mới mở rộng lựa chọn và có thể giúp đạt cùng mức thỏa dụng với chi phí thấp hơn. Chỉ số giỏ cố định khó ghi nhận đầy đủ lợi ích ngay khi sản phẩm xuất hiện.

### 8.3 Chất lượng thay đổi khó đo

Điện thoại mới đắt hơn nhưng có camera tốt hơn, pin lâu hơn và xử lý nhanh hơn. Bao nhiêu phần của mức giá cao hơn là lạm phát, bao nhiêu là trả cho chất lượng? Cơ quan thống kê có điều chỉnh nhưng không thể đo hoàn hảo.

Các vấn đề này tạo xu hướng thiên lệch tăng trong khung phân tích kinh điển, nhưng độ lớn là vấn đề thực nghiệm và phương pháp thống kê đã thay đổi theo thời gian. Xem [Measuring the Cost of Living — CPI, Inflation, and Biases](../wiki/measuring-cost-of-living-cpi-inflation-and-biases.md).

### 8.4 Lạm phát của bạn có thể khác CPI

CPI mô tả một giỏ đại diện, không phải chính xác giỏ của từng người. Sinh viên dành nhiều cho học phí, người cao tuổi dành nhiều cho y tế, người đi thuê nhà đối mặt với cơ cấu chi tiêu khác chủ nhà. Vì vậy trải nghiệm cá nhân có thể cao hoặc thấp hơn headline CPI mà không khiến chỉ số chính thức “sai”.

---

# Phần III — Vì sao CPI khác GDP deflator?

## 9. Hai khác biệt quyết định

| Tiêu chí | CPI | GDP deflator |
|---|---|---|
| Câu hỏi | Giá của hàng người tiêu dùng mua thay đổi thế nào? | Giá của toàn bộ sản lượng cuối cùng sản xuất trong nước thay đổi thế nào? |
| Phạm vi | Tiêu dùng, kể cả hàng nhập khẩu | $C+I+G+X$ sản xuất trong nước; không gồm nhập khẩu |
| Trọng số | Giỏ tiêu dùng tương đối ổn định, được cập nhật định kỳ | Thành phần sản lượng hiện tại thay đổi tự động; tài khoản thực tế có thể dùng chain-linking |
| Bao gồm | Hàng tiêu dùng nhập khẩu | Máy móc, nhà xưởng, mua sắm chính phủ, hàng xuất khẩu sản xuất trong nước |
| Không bao gồm điển hình | Máy bay quân sự không thuộc giỏ hộ gia đình | Xe nhập khẩu người dân mua |

Nguồn tổng hợp: [GDP Deflator versus CPI — Scope and Weighting Differences](../wiki/gdp-deflator-vs-cpi-scope-and-weighting.md).

### 9.1 Ví dụ xe nhập khẩu

Giá một dòng xe nhập khẩu tăng mạnh:

- có thể làm CPI tăng vì hộ gia đình mua xe đó;
- không trực tiếp làm GDP deflator tăng vì xe không được sản xuất trong nước.

### 9.2 Ví dụ máy bay quân sự

Giá máy bay sản xuất trong nước bán cho chính phủ tăng:

- đi vào GDP deflator vì là sản lượng trong nước;
- không đi vào CPI vì không phải món hàng của giỏ tiêu dùng điển hình.

### 9.3 Ví dụ dầu nhập khẩu

Khi dầu nhập khẩu tăng giá, xăng và chi phí sưởi của hộ có thể tăng mạnh. CPI có thể phản ứng nhiều hơn GDP deflator vì nhập khẩu thuộc giỏ tiêu dùng nhưng không phải sản lượng trong nước. Mankiw dùng đợt giá dầu 1979–1980 để minh họa CPI tăng mạnh hơn GDP deflator.

> [!success] Câu trả lời checkpoint ngắn gọn
> CPI và GDP deflator có thể khác vì chúng **đo các tập hàng hóa khác nhau** và dùng **trọng số khác nhau**. CPI theo giỏ tiêu dùng, gồm nhập khẩu; GDP deflator theo sản lượng cuối cùng hiện tại được sản xuất trong nước, gồm cả đầu tư, mua sắm chính phủ và xuất khẩu.

---

# Phần IV — Annualized, year-on-year và những tỷ lệ dễ nhầm

## 10. Trước hết: mức, thay đổi và tốc độ thay đổi

Ba câu sau không giống nhau:

- “CPI tháng 6 là 120” — **mức chỉ số**.
- “CPI tăng 0,3% so với tháng trước” — **month-on-month (m/m)**.
- “CPI tăng 3,5% so với cùng tháng năm trước” — **year-on-year (y/y)**.

Tương tự, “GDP quý II là 500 tỷ” là mức; “real GDP quý II tăng 1% so với quý I” là tốc độ tăng theo quý.

## 11. Year-on-year: so cùng kỳ năm trước

$$
g_{y/y,t}=\frac{X_t-X_{t-12}}{X_{t-12}}\times100\%
$$

Với dữ liệu quý, so quý hiện tại với cùng quý một năm trước; với CPI tháng, so với cùng tháng năm trước.

**Ưu điểm:** giảm ảnh hưởng mùa vụ và dễ diễn giải “trong 12 tháng qua”.  
**Nhược điểm:** phản ứng chậm với bước ngoặt mới vì chứa nhiều biến động cũ — gọi là **base effects**.

> [!example] Hiệu ứng nền
> CPI tăng mạnh từ 100 lên 105 vào tháng 1, rồi đứng ở 105 cả năm. Đến tháng 12, lạm phát y/y vẫn có thể trông cao so với nền cũ dù giá gần đây không còn tăng. Khi tháng có cú nhảy cũ rời khỏi cửa sổ 12 tháng, tỷ lệ y/y có thể giảm mạnh dù mức giá không giảm.

## 12. Annualized: biến tốc độ ngắn hạn thành tốc độ tương đương một năm

Nếu biến tăng $g_q$ trong một quý và giả định nhịp đó lặp lại bốn quý:

$$
g_{annualized}=(1+g_q)^4-1
$$

Ví dụ real GDP tăng 1% so với quý trước:

$$
(1{,}01)^4-1\approx4{,}06\%
$$

Bản tin có thể viết “GDP tăng 4,1% theo tốc độ năm”, dù mức tăng quan sát trực tiếp trong quý chỉ là 1%.

Với tỷ lệ tháng:

$$
g_{annualized}=(1+g_m)^{12}-1
$$

CPI tăng 0,3% trong tháng tương đương:

$$
(1{,}003)^{12}-1\approx3{,}66\%
$$

Annualized **không phải dự báo** rằng cả năm chắc chắn tăng đúng mức đó. Nó chỉ trả lời: “Nếu tốc độ ngắn hạn này lặp lại, tốc độ một năm tương đương là bao nhiêu?”

### 12.1 Hai nghĩa gần nhau nhưng không được trộn

Trong báo cáo GDP, “at an annual rate” có thể nói về:

1. **Mức GDP quý được quy đổi thành mức năm:** dòng thu nhập/chi tiêu của quý nhân 4 để dễ so với GDP năm. Đây là quy ước được Mankiw mô tả.
2. **Tốc độ tăng trưởng quý được annualized:** thường dùng lũy kế $(1+g_q)^4-1$.

Một bên là **mức**, một bên là **tỷ lệ tăng**. Hãy xem đơn vị và phương pháp của cơ quan công bố.

### 12.2 Bảng phân biệt nhanh

| Cách ghi | So sánh | Cách hiểu |
|---|---|---|
| m/m | Tháng này với tháng trước | Động lượng rất gần, thường nhiễu |
| q/q | Quý này với quý trước | Động lượng ngắn hạn |
| y/y | Kỳ này với cùng kỳ năm trước | Thay đổi thực tế trong 12 tháng |
| annualized | Kéo tốc độ ngắn hạn thành tốc độ năm | Nhịp tương đương nếu lặp lại |
| YTD | Từ đầu năm đến hiện tại | Phụ thuộc cách cộng hoặc so mức của nguồn |

> [!warning] Không so trực tiếp 4% annualized với 3% y/y
> Hai số dùng cửa sổ thời gian khác nhau. Trước khi nói “tăng tốc” hay “giảm tốc”, hãy đưa chúng về cùng định nghĩa hoặc xem đồng thời chuỗi q/q, annualized và y/y.

---

# Phần V — Điều chỉnh lạm phát và lãi suất thực

## 13. Chuyển tiền ở hai thời điểm về cùng sức mua

$$
\text{Tiền theo giá kỳ B}=\text{Tiền ở kỳ A}\times\frac{\text{Chỉ số giá kỳ B}}{\text{Chỉ số giá kỳ A}}
$$

Ví dụ thu nhập là 20 triệu khi CPI bằng 120. Khi CPI lên 132, số tiền cần để giữ nguyên sức mua là:

$$
20\times\frac{132}{120}=22\text{ triệu}
$$

Thu nhập danh nghĩa phải tăng 10% mới giữ nguyên sức mua theo giỏ CPI. Nếu chỉ tăng lên 21 triệu, thu nhập danh nghĩa tăng 5% nhưng thu nhập thực giảm xấp xỉ 5%.

## 14. Lãi suất danh nghĩa và lãi suất thực

- **Lãi suất danh nghĩa $i$:** tốc độ số tiền trong tài khoản tăng.
- **Lãi suất thực $r$:** tốc độ sức mua tăng sau khi điều chỉnh lạm phát.

Công thức Fisher chính xác:

$$
1+r=\frac{1+i}{1+\pi}
$$

hay

$$
r=\frac{1+i}{1+\pi}-1
$$

Khi tỷ lệ không quá lớn, dùng gần đúng:

$$
r\approx i-\pi
$$

### 14.1 Ví dụ

Gửi tiết kiệm lãi danh nghĩa 8%, lạm phát 5%:

- gần đúng: $r\approx8\%-5\%=3\%$;
- chính xác: $r=1{,}08/1{,}05-1\approx2{,}86\%$.

Tiền tăng 8%, nhưng sức mua chỉ tăng khoảng 2,86%.

Nếu lãi danh nghĩa 4% và lạm phát 6%:

$$
r\approx-2\%
$$

Số tiền vẫn tăng, nhưng sức mua giảm.

## 15. Lãi suất thực kỳ vọng và lãi suất thực thực hiện

Khi ký hợp đồng hôm nay, lạm phát tương lai chưa biết:

$$
r^{e}\approx i-\pi^{e}
$$

Đây là **lãi suất thực kỳ vọng (ex ante)**, quan trọng cho quyết định vay, cho vay và đầu tư.

Sau khi lạm phát xảy ra:

$$
r^{realized}\approx i-\pi^{actual}
$$

Đây là **lãi suất thực thực hiện (ex post)**.

Nếu lạm phát thực tế cao hơn dự kiến trong một hợp đồng lãi suất danh nghĩa cố định, người vay trả lại bằng đồng tiền có sức mua thấp hơn dự kiến: người vay có lợi tương đối, người cho vay chịu thiệt tương đối. Nếu lạm phát thấp hơn dự kiến, chiều phân phối đảo ngược.

> [!note] Chọn đúng chỉ số lạm phát
> Không có một lãi suất thực duy nhất cho mọi mục đích. Hộ gia đình có thể quan tâm CPI; doanh nghiệp quan tâm giá đầu ra và đầu vào; nhà đầu tư có thể dùng lạm phát kỳ vọng từ thị trường hoặc dự báo. Hãy nêu rõ chỉ số và kỳ thời gian.

---

# Phần VI — GDP có phải mức sống không?

## 16. GDP nói được gì?

Real GDP đo sản lượng; real GDP bình quân đầu người là chỉ báo hữu ích về nguồn lực vật chất trung bình. Các nước có GDP/người cao thường có khả năng chi nhiều hơn cho y tế, giáo dục, cơ sở hạ tầng và nhiều điều kiện sống khác.

## 17. GDP không nói đủ điều gì?

GDP không tự động phản ánh đầy đủ:

- phân phối thu nhập;
- công việc gia đình và tình nguyện không qua thị trường;
- thời gian nghỉ ngơi;
- ô nhiễm và suy giảm tài nguyên;
- chất lượng quan hệ xã hội;
- sức khỏe, tuổi thọ và cảm nhận hài lòng;
- lợi ích của hàng số miễn phí và một số cải thiện chất lượng khó đo.

Ví dụ, làm việc nhiều giờ hơn có thể tăng GDP nhưng giảm thời gian nghỉ; dọn dẹp sau thiên tai tạo chi tiêu và sản lượng nhưng không có nghĩa thiên tai làm xã hội khá hơn. Vì thế GDP là thước đo **hoạt động sản xuất**, không phải máy đo hạnh phúc.

Cách tiếp cận thực tế không phải bỏ GDP mà dùng bảng chỉ báo bổ sung: real GDP/người, phân phối thu nhập, việc làm, tuổi thọ, giáo dục, môi trường và khảo sát hài lòng. Xem [Measuring well-being beyond GDP](../wiki/measuring-well-being-beyond-gdp-objective-and-subjective-complements.md).

---

# Phần VII — Quy trình đọc một bản tin trong 90 giây

## 18. Checklist tám câu

1. **Biến nào?** GDP, CPI, GDP deflator, lương hay lãi suất?
2. **Mức hay tốc độ tăng?** Tỷ đồng, điểm chỉ số hay phần trăm?
3. **Danh nghĩa hay thực?** Có loại ảnh hưởng giá chưa?
4. **Headline hay core?** Bao gồm hay loại nhóm nào?
5. **So với kỳ nào?** m/m, q/q, y/y hay YTD?
6. **Annualized không?** Nếu có, công thức và tần suất gốc là gì?
7. **Đã điều chỉnh mùa vụ chưa?** Đặc biệt với dữ liệu tháng/quý.
8. **Con số nói gì và không nói gì?** Sản lượng, giá, sức mua hay phúc lợi?

Sau đó mới hỏi:

- Thành phần nào đóng góp nhiều nhất?
- Kết quả cao/thấp hơn kỳ vọng thị trường không?
- Có hiệu ứng nền, cú sốc tạm thời hay sửa đổi dữ liệu không?
- CPI và GDP deflator khác nhau có phù hợp với nhập khẩu và cơ cấu sản lượng không?

---

## 19. Ví dụ tích hợp 1 — Bản tin GDP giả định

> “Real GDP quý II tăng 4,1% theo tốc độ năm, đã điều chỉnh mùa vụ. Nominal GDP tăng 7,5% theo tốc độ năm. Chi tiêu hộ gia đình và tồn kho đóng góp dương; xuất khẩu ròng đóng góp âm.”

### Cách đọc

1. **Real GDP:** tăng trưởng sản lượng đã loại ảnh hưởng giá.
2. **4,1% annualized:** không phải sản lượng quý II cao hơn quý I đúng 4,1%. Tốc độ q/q xấp xỉ là:

   $$
   (1+0{,}041)^{1/4}-1\approx1{,}01\%
   $$

3. **Đã điều chỉnh mùa vụ:** biến động đều đặn như mua sắm lễ hội đã được lọc bớt.
4. **Nominal tăng nhanh hơn real:** gợi ý mức giá của sản lượng cũng tăng, nhưng muốn định lượng phải xem GDP deflator.
5. **Tồn kho đóng góp dương:** hàng được sản xuất nhưng chưa chắc đã bán cho người dùng cuối; cần thận trọng khi suy luận sức cầu bền vững.
6. **Xuất khẩu ròng âm:** có thể do xuất khẩu giảm, nhập khẩu tăng hoặc cả hai; chỉ nhìn $NX$ chưa biết nguyên nhân.
7. **Chưa biết:** GDP/người, phân phối thu nhập, chất lượng môi trường và liệu con số có được sửa đổi sau này hay không.

---

## 20. Ví dụ tích hợp 2 — Bản tin CPI giả định

> “CPI tháng 8 tăng 0,4% so với tháng trước và 3,6% so với cùng kỳ. Core CPI tăng 0,2% m/m và 3,1% y/y. Năng lượng là nhóm đóng góp lớn.”

### Cách đọc

1. **Headline m/m = 0,4%:** giá của toàn giỏ tăng trong tháng.
2. **Headline y/y = 3,6%:** mức chỉ số cao hơn 3,6% so với cùng tháng năm trước.
3. **Core thấp hơn headline:** phù hợp với thông tin năng lượng đóng góp lớn.
4. Nếu annualize nhịp headline 0,4%:

   $$
   (1{,}004)^{12}-1\approx4{,}9\%
   $$

   Nhưng 4,9% annualized không mâu thuẫn với 3,6% y/y; chúng đo hai cửa sổ khác nhau.
5. **Không được nói “giá đã giảm”** nếu lạm phát giảm từ 4% xuống 3,6%. Giá vẫn tăng, chỉ tăng chậm hơn. Giá giảm thực sự đòi hỏi tỷ lệ thay đổi chỉ số âm trong kỳ phù hợp.
6. **Không được nói core là chi phí thực của mọi hộ:** người dùng nhiều năng lượng có thể chịu mức tăng cao hơn.

---

# Phần VIII — Những câu nói sai và cách sửa

| Câu dễ sai | Cách sửa |
|---|---|
| “GDP danh nghĩa tăng 8%, nên sản lượng tăng 8%.” | Cần real GDP để tách ảnh hưởng giá. |
| “CPI bằng 130 nên lạm phát là 130%.” | 130 là mức chỉ số; lạm phát là % thay đổi giữa hai kỳ. |
| “Lạm phát giảm nghĩa là giá giảm.” | Thường chỉ nghĩa giá tăng chậm hơn; giá giảm là deflation. |
| “Core CPI bỏ thực phẩm nên vô dụng.” | Core phục vụ đọc xu hướng; headline phục vụ toàn bộ giỏ. Cần cả hai. |
| “CPI phải bằng GDP deflator.” | Hai chỉ số khác phạm vi và trọng số. |
| “GDP quý tăng annualized 4% nghĩa là quý này tăng 4%.” | Tăng trực tiếp theo quý chỉ khoảng 1% nếu annualization theo lũy kế. |
| “Lãi tiết kiệm 7% làm tôi giàu hơn 7%.” | Đó là danh nghĩa; sức mua tăng theo lãi suất thực. |
| “GDP/người tăng nên mọi người đều khá hơn.” | Bình quân không cho biết phân phối và nhiều mặt của phúc lợi. |

---

# Phần IX — Checkpoint tự kiểm tra

## 21. Bài tập

### Câu 1 — Nominal hay real?

Một nước chỉ sản xuất cà phê. Năm 1 bán 1.000 kg với giá 100.000 đồng/kg. Năm 2 vẫn bán 1.000 kg nhưng giá là 110.000 đồng/kg.

1. Nominal GDP tăng bao nhiêu?
2. Real GDP theo giá năm 1 tăng bao nhiêu?
3. Có thể gọi đây là tăng trưởng sản lượng không?

### Câu 2 — Headline hay core?

Headline CPI tăng 5%, core CPI tăng 3%, trong khi giá năng lượng tăng mạnh. Hãy giải thích chênh lệch mà không khẳng định quá mức.

### Câu 3 — Annualized hay y/y?

Real GDP tăng 0,5% q/q. Tốc độ annualized là bao nhiêu? Nó có đồng nghĩa GDP cao hơn cùng quý năm trước đúng bằng tỷ lệ đó không?

### Câu 4 — CPI hay GDP deflator?

Giá điện thoại nhập khẩu tăng 20%, còn giá máy móc sản xuất trong nước bán cho doanh nghiệp giảm 5%. Mỗi biến động có xu hướng đi vào chỉ số nào?

### Câu 5 — Lãi suất thực

Lãi tiền gửi là 6%, lạm phát thực tế 4%. Tính lãi suất thực gần đúng và chính xác.

### Câu 6 — Đọc câu báo chí

> “Lạm phát giảm còn 3%, vì vậy mức giá đã quay về mức trước khủng hoảng.”

Câu này sai ở đâu?

## 22. Đáp án ngắn

1. Nominal GDP tăng 10%; real GDP không tăng; không có tăng trưởng sản lượng.
2. Chênh lệch **phù hợp** với năng lượng kéo headline lên vì core loại nhóm này, nhưng cần xem trọng số và phân rã để xác nhận mức đóng góp.
3. $(1{,}005)^4-1\approx2{,}02\%$. Không; annualized từ q/q khác y/y.
4. Điện thoại nhập khẩu: CPI, không trực tiếp vào GDP deflator. Máy móc nội địa: GDP deflator, không nhất thiết vào CPI hộ gia đình.
5. Gần đúng $6\%-4\%=2\%$; chính xác $1{,}06/1{,}04-1\approx1{,}92\%$.
6. Lạm phát 3% nghĩa mức giá vẫn tăng 3% theo kỳ so sánh; giảm lạm phát là **disinflation**, không đưa mức giá trở lại quá khứ. Muốn mức giá giảm phải có lạm phát âm đủ lớn.

> [!success] Bạn hoàn thành Step 6 khi có thể
> - xác định nominal/real;
> - phân biệt mức chỉ số với lạm phát;
> - phân biệt headline/core;
> - nhận diện m/m, q/q, y/y và annualized;
> - giải thích CPI khác GDP deflator bằng phạm vi và trọng số;
> - chuyển lãi danh nghĩa thành lãi thực;
> - nêu được giới hạn của GDP như thước đo phúc lợi.

---

# Lộ trình học gợi ý trong 6 buổi

1. **Buổi 1:** định nghĩa GDP, hàng cuối cùng, giá trị gia tăng, $C+I+G+NX$.
2. **Buổi 2:** nominal GDP, real GDP, GDP deflator; làm lại ví dụ hai hàng hóa.
3. **Buổi 3:** cách lập CPI, mức giá và lạm phát, ba thiên lệch đo lường.
4. **Buổi 4:** headline/core; CPI so với GDP deflator.
5. **Buổi 5:** m/m, q/q, y/y, annualized, điều chỉnh mùa vụ và hiệu ứng nền.
6. **Buổi 6:** lãi suất thực, đọc hai bản tin thật và hoàn thành checkpoint mà không nhìn đáp án.

Khi đọc nguồn thật, hãy ghi lại nguyên văn **tên biến, kỳ so sánh, điều chỉnh mùa vụ và đơn vị** trước khi diễn giải. Đây là thói quen quan trọng hơn việc ghi nhớ một con số cụ thể.

---

# Tài liệu tham khảo trong kho tri thức

## Wiki tổng hợp

- [GDP — income-expenditure identity, measurement rules, components, and real versus nominal](../wiki/gdp-income-expenditure-measurement-and-real-vs-nominal.md)
- [GDP Deflator versus CPI — Scope and Weighting Differences](../wiki/gdp-deflator-vs-cpi-scope-and-weighting.md)
- [Measuring the Cost of Living — CPI, Inflation, and Biases](../wiki/measuring-cost-of-living-cpi-inflation-and-biases.md)
- [Correcting Economic Variables for Inflation — Dollar Conversions, Regional Parities, Indexation, and Real vs Nominal Interest Rates](../wiki/correcting-for-inflation-real-vs-nominal-indexation-and-regional-parities.md)
- [Measuring well-being beyond GDP](../wiki/measuring-well-being-beyond-gdp-objective-and-subjective-complements.md)
- [Roadmap học và hiểu kinh tế vĩ mô](../wiki/macroeconomics-learning-roadmap.md)

## Nguồn sách đã đối chiếu

- Mankiw, *Principles of Macroeconomics*, 8th ed., Ch.10, [The Data of Macroeconomics](../raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/034-the-data-of-macroeconomics.md).
- Mankiw, *Principles of Macroeconomics*, 8th ed., Ch.11, [Measuring the Cost of Living](../raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/037-measuring-the-cost-of-living.md) và [phần tiếp theo](../raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/038-in-the-news.md).
- Krugman & Wells, *Macroeconomics*, Ch.7, [Market Baskets and Price Indexes](../raw/Macroeconomics_Krugman/042-chapter-7-gdp-and-the-cpi-tracking-the-macroeconomy-market-baskets-and.md).

> [!note] Phạm vi và độ tin cậy
> Các số liệu lịch sử trong ví dụ sách phản ánh kỳ xuất bản của nguồn và được dùng để học phương pháp, không phải số liệu hiện hành. Các bản tin ở Phần VII là **tình huống giả định**. Khi áp dụng thực tế, phải ưu tiên định nghĩa và metadata của cơ quan thống kê phát hành dữ liệu.
