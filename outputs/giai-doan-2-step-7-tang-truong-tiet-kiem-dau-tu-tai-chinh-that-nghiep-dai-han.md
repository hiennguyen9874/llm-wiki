---
title: "Giai đoạn 2 — Step 7: Tăng trưởng, tiết kiệm–đầu tư, tài chính và thất nghiệp dài hạn"
tags:
  - kinh-te-vi-mo
  - mankiw-8e
  - tang-truong
  - tiet-kiem-dau-tu
  - that-nghiep
status: learning-material
---

# Giai đoạn 2 — Step 7: Tăng trưởng, tiết kiệm–đầu tư, tài chính và thất nghiệp dài hạn

> [!abstract] Ý chính của bài
> Mức sống dài hạn phụ thuộc chủ yếu vào **năng suất**. Tiết kiệm cung cấp nguồn lực cho đầu tư; lãi suất thực điều phối người tiết kiệm và người đầu tư; đầu tư làm tăng vốn trên mỗi lao động; vốn, kỹ năng và công nghệ làm tăng năng suất. Nhưng do lợi suất giảm dần, tăng tỷ lệ tiết kiệm thường nâng **mức** thu nhập dài hạn chứ không thể một mình duy trì **tốc độ tăng trưởng** vĩnh viễn. Song song, một nền kinh tế khỏe mạnh vẫn có thất nghiệp do tìm kiếm và do cơ cấu; vì vậy cần phân biệt tỷ lệ thất nghiệp tự nhiên với phần thất nghiệp do chu kỳ.

Bài này tổng hợp Mankiw 8e Ch.12–15 từ các concept trong wiki, đồng thời bổ sung diễn giải, ví dụ tính toán và bài tập dành cho người mới. Các con số lịch sử chỉ minh họa cơ chế, không phải số liệu hiện hành.

## 1. Sau bài này, bạn cần làm được gì?

Sau khi học xong, bạn nên có thể:

1. Giải thích vì sao năng suất quyết định mức sống dài hạn.
2. Phân biệt **tiết kiệm**, **đầu tư tài chính** và **đầu tư theo nghĩa vĩ mô**.
3. Từ đồng nhất thức GDP, suy ra $S=I$ trong nền kinh tế đóng và hiểu giới hạn của kết quả này.
4. Dùng mô hình thị trường vốn cho vay để phân tích thay đổi của tiết kiệm, đầu tư và thâm hụt ngân sách.
5. Phân biệt lãi suất danh nghĩa, lãi suất thực kỳ vọng và lãi suất thực thực hiện.
6. Tính future value, present value và đánh giá một dự án đơn giản.
7. Giải thích quan hệ giữa kỳ hạn, giá trái phiếu, kỳ vọng lãi suất ngắn hạn và phần bù rủi ro.
8. Hiểu vì sao lợi nhuận kỳ vọng cao thường đi kèm rủi ro cao và vì sao đa dạng hóa không loại bỏ mọi rủi ro.
9. Tính tỷ lệ thất nghiệp và tỷ lệ tham gia lực lượng lao động; chỉ ra điều tỷ lệ thất nghiệp chính thức bỏ sót.
10. Phân biệt thất nghiệp tạm thời, cơ cấu và chu kỳ; hiểu “tự nhiên” không có nghĩa là cố định hay đáng mong muốn.
11. Phân biệt **tăng trưởng dài hạn** với **phục hồi sau suy thoái**.
12. Tự nối trọn chuỗi:

```text
tiết kiệm
→ cung vốn cho vay
→ lãi suất thực
→ đầu tư vào tư bản mới
→ vốn trên lao động
→ năng suất
→ GDP thực/người và mức sống
```

Tài liệu wiki cốt lõi: [Production and Growth](../wiki/production-and-growth-productivity-determinants-and-policy.md), [Saving, Investment, and the Financial System](../wiki/saving-investment-and-the-financial-system.md), [The Basic Tools of Finance](../wiki/basic-tools-of-finance-present-value-compounding-and-discounting.md), [Long-term interest rates](../wiki/long-term-interest-rates-expected-short-rates-and-maturity-risk.md), [Measuring unemployment](../wiki/measuring-unemployment-labor-underutilization-and-jobless-recovery.md), và [Natural rate of unemployment](../wiki/natural-rate-of-unemployment-frictional-structural-and-cyclical.md).

---

# Phần I — Tăng trưởng dài hạn bắt đầu từ năng suất

## 2. Mức sống không tăng chỉ vì có nhiều tiền hơn

Một quốc gia không trở nên giàu hơn chỉ vì mọi người cầm nhiều đơn vị tiền hơn. Nếu lượng tiền và mọi mức giá cùng tăng gấp đôi trong khi sản lượng không đổi, sức mua thực không tăng. Điều quyết định mức sống vật chất là lượng hàng hóa và dịch vụ nền kinh tế có thể sản xuất cho mỗi người.

Mankiw dùng trực giác Robinson Crusoe: nếu Crusoe bắt được nhiều cá hơn trong mỗi giờ, anh ta có thể ăn nhiều hơn hoặc dành bớt thời gian đánh cá để làm quần áo, dựng nhà và nghỉ ngơi. Với cả nền kinh tế, ý tưởng tương tự là:

$$
\text{Năng suất lao động} = \frac{\text{Sản lượng thực}}{\text{Lao động hoặc số giờ làm việc}}
$$

GDP trên đầu người còn phụ thuộc vào tỷ lệ dân số đang làm việc, nhưng trong dài hạn, tỷ lệ này không thể tăng mãi. Muốn GDP thực trên đầu người tiếp tục tăng bền vững, sản lượng trên mỗi lao động hoặc mỗi giờ lao động phải tăng. Đây là thông điệp trung tâm của [Production and Growth](../wiki/production-and-growth-productivity-determinants-and-policy.md).

> [!warning] Hai khái niệm dễ lẫn
> - **Mức** GDP thực/người cho biết một nền kinh tế giàu đến đâu tại một thời điểm.
> - **Tốc độ tăng trưởng** cho biết mức đó thay đổi nhanh đến đâu.
>
> Một nước nghèo có thể tăng rất nhanh mà vẫn nghèo hơn một nước giàu tăng chậm.

## 3. Bốn yếu tố quyết định năng suất

Có thể tóm tắt bằng hàm sản xuất tổng hợp:

$$
Y=A F(L,K,H,N)
$$

Trong đó:

- $Y$: sản lượng thực;
- $L$: lao động;
- $K$: tư bản vật chất — máy móc, nhà xưởng, hạ tầng;
- $H$: vốn nhân lực — giáo dục, kỹ năng, kinh nghiệm và sức khỏe;
- $N$: tài nguyên tự nhiên;
- $A$: tri thức công nghệ và hiệu quả sử dụng đầu vào.

Nếu hàm sản xuất có hiệu suất không đổi theo quy mô, chia mọi thứ cho $L$ cho ta:

$$
\frac{Y}{L}=A F\left(1,\frac{K}{L},\frac{H}{L},\frac{N}{L}\right)
$$

Công thức này nói rằng năng suất phụ thuộc vào:

### 3.1. Tư bản vật chất trên mỗi lao động, $K/L$

Một thợ mộc có cưa máy, máy tiện và xưởng tốt thường làm được nhiều hơn một thợ chỉ có dụng cụ cầm tay. Tư bản là đầu ra được sản xuất trong quá khứ nhưng được dùng làm đầu vào hôm nay.

### 3.2. Vốn nhân lực trên mỗi lao động, $H/L$

Máy móc hiện đại không giúp nhiều nếu người lao động không biết vận hành. Giáo dục, đào tạo tại nơi làm việc, kinh nghiệm và sức khỏe đều có thể nâng năng suất. Vốn nhân lực cũng cần đầu tư: thời gian học hôm nay đổi lấy năng lực sản xuất cao hơn sau này.

### 3.3. Tài nguyên tự nhiên trên mỗi lao động, $N/L$

Đất, nước, rừng và khoáng sản có thể tạo lợi thế, nhưng không phải điều kiện đủ hoặc cần để giàu. Một nước giàu tài nguyên vẫn có thể nghèo nếu thể chế và năng suất thấp; một nước ít tài nguyên có thể nhập nguyên liệu rồi xuất sản phẩm có giá trị cao.

### 3.4. Tri thức công nghệ, $A$

Công nghệ ở đây không chỉ là máy tính hay robot. Nó là cách tốt hơn để kết hợp đầu vào: dây chuyền lắp ráp, giống cây trồng mới, quy trình quản lý tồn kho, phần mềm logistics hay phương pháp điều trị mới. Cần phân biệt:

- **Tri thức công nghệ**: xã hội biết cách sản xuất tốt đến đâu.
- **Vốn nhân lực**: người lao động đã học và sử dụng tri thức ấy đến đâu.

Ví dụ, mã vạch chỉ trở thành công nghệ nâng năng suất lớn khi nhà sản xuất gắn nhãn, siêu thị mua máy quét và doanh nghiệp xây hệ thống tồn kho tương thích. Phát minh và khả năng áp dụng có thể cách nhau nhiều năm.

## 4. Vì sao vài điểm phần trăm tăng trưởng tạo khác biệt khổng lồ?

Tăng trưởng được ghép lãi:

$$
Y_t=Y_0(1+g)^t
$$

Nếu hai nền kinh tế cùng bắt đầu với thu nhập 30.000 đơn vị/người:

- tăng 1%/năm trong 40 năm: $30.000(1,01)^{40}\approx44.666$;
- tăng 3%/năm trong 40 năm: $30.000(1,03)^{40}\approx97.861$.

Chênh lệch chỉ 2 điểm phần trăm mỗi năm cuối cùng tạo ra mức thu nhập hơn gấp đôi. Quy tắc 70 cho phép ước lượng nhanh:

$$
\text{Số năm để tăng gấp đôi}\approx\frac{70}{\text{tốc độ tăng trưởng tính bằng %}}
$$

Ở 2%/năm, mức sống tăng gấp đôi trong khoảng 35 năm; ở 3,5%/năm, khoảng 20 năm. Đây là lý do kinh tế học tăng trưởng quan tâm mạnh đến những thay đổi tưởng như nhỏ trong năng suất.

## 5. Lợi suất giảm dần và hiệu ứng bắt kịp

Nếu giữ kỹ năng và công nghệ không đổi, thêm một máy tính cho người chưa có máy thường hữu ích hơn thêm chiếc máy thứ tư cho người đã có ba chiếc. Đó là **lợi suất giảm dần của tư bản**: $K/L$ tăng vẫn làm $Y/L$ tăng, nhưng phần tăng thêm ngày càng nhỏ.

Hệ quả:

1. Tăng tiết kiệm có thể làm đầu tư và vốn tăng.
2. Trong thời kỳ chuyển tiếp, nền kinh tế tăng trưởng nhanh hơn.
3. Khi vốn đã dồi dào, lợi ích biên nhỏ dần và tăng trưởng chậm lại.
4. Kết quả dài hạn thường là **mức sản lượng/người cao hơn**, không phải tốc độ tăng trưởng/người cao hơn vĩnh viễn.
5. Tăng trưởng bền vững của sản lượng trên lao động cuối cùng cần tiến bộ công nghệ bền vững.

Điều này cũng giải thích **hiệu ứng bắt kịp có điều kiện**: một nước ít vốn có thể thu được lợi ích lớn từ những khoản đầu tư cơ bản và từ việc áp dụng công nghệ đã tồn tại. Nhưng bắt kịp không tự động xảy ra; nó còn cần giáo dục, thể chế, ổn định, hệ thống tài chính và khả năng hấp thụ công nghệ.

> [!example] Mức và tốc độ
> Một chương trình đầu tư hạ tầng có thể đưa năng suất từ 100 lên 120. Trong quá trình xây dựng và đưa công trình vào sử dụng, tăng trưởng nhanh hơn. Khi nền kinh tế ổn định quanh mức 120, chương trình không còn tự tạo thêm cùng một tỷ lệ tăng mỗi năm. Muốn tiếp tục tăng, cần đầu tư mới, kỹ năng mới hoặc công nghệ mới.

## 6. Tiết kiệm không phải “càng nhiều càng tốt”

Để sản xuất thêm máy móc hôm nay, xã hội phải dành bớt nguồn lực cho hàng tiêu dùng hôm nay. Tiết kiệm là một đánh đổi giữa hiện tại và tương lai, không phải bữa trưa miễn phí.

Trong mô hình tích lũy vốn đơn giản:

$$
\Delta k=s f(k)-\delta k
$$

với $k$ là vốn trên lao động, $s$ là tỷ lệ tiết kiệm và $\delta$ là tỷ lệ khấu hao. Trạng thái ổn định thỏa:

$$
sf(k^*)=\delta k^*
$$

Tăng $s$ làm $k^*$ và sản lượng ổn định cao hơn. Nhưng tiêu dùng ổn định là:

$$
c^*=f(k^*)-\delta k^*
$$

Nếu tiết kiệm quá nhiều, xã hội phải duy trì một lượng vốn lớn với chi phí khấu hao cao, trong khi tiêu dùng hiện tại đã bị cắt mạnh. **Quy tắc vàng** là mức vốn hoặc tỷ lệ tiết kiệm tối đa hóa tiêu dùng ổn định, chứ không tối đa hóa sản lượng bằng mọi giá. Đây là phần mở rộng hữu ích trong [Capital Accumulation, the Steady State, and the Golden Rule](../wiki/capital-accumulation-steady-state-and-golden-rule-saving.md).

---

# Phần II — Tiết kiệm đi vào đầu tư bằng cách nào?

## 7. Hệ thống tài chính là chiếc cầu giữa hiện tại và tương lai

Người tiết kiệm có thu nhập hiện tại nhưng muốn chi tiêu sau này. Doanh nghiệp có dự án hôm nay nhưng cần tiền trước khi dự án tạo doanh thu. Hệ thống tài chính ghép hai phía này với nhau:

- **Thị trường tài chính trực tiếp**: trái phiếu và cổ phiếu.
- **Trung gian tài chính**: ngân hàng, quỹ tương hỗ, quỹ hưu trí, công ty bảo hiểm.

Một trái phiếu là lời hứa trả nợ; cổ phiếu là quyền sở hữu và quyền hưởng phần lợi nhuận còn lại. Người gửi tiền có một tài sản; cùng khoản tiền ấy là nghĩa vụ nợ của ngân hàng. Ngân hàng tập hợp tiền gửi rồi cho người khác vay, đồng thời xử lý thông tin, thanh khoản và rủi ro.

## 8. Ba từ “đầu tư” không nên trộn lẫn

Trong ngôn ngữ hằng ngày, mua cổ phiếu thường được gọi là đầu tư. Trong kế toán vĩ mô, cần phân biệt:

| Hành động | Cách gọi theo vĩ mô | Có trực tiếp tạo tư bản mới? |
|---|---|---:|
| Gửi thu nhập chưa tiêu vào ngân hàng | Tiết kiệm | Không |
| Mua cổ phiếu cũ từ nhà đầu tư khác | Đầu tư tài chính/tiết kiệm | Không |
| Công ty xây nhà máy mới | Đầu tư | Có |
| Doanh nghiệp mua máy mới | Đầu tư | Có |
| Hộ gia đình mua nhà ở mới xây | Đầu tư trong GDP | Có |
| Mua lại một căn nhà cũ | Chuyển nhượng tài sản | Không, trừ dịch vụ môi giới/sửa chữa mới |

Do đó, câu “người dân mua nhiều cổ phiếu nên đầu tư của nền kinh tế tăng” chưa chắc đúng. Giao dịch cổ phiếu trên thị trường thứ cấp có thể giúp vốn được định giá và lưu chuyển, nhưng bản thân nó không trực tiếp tạo một máy móc hay tòa nhà mới.

## 9. Từ GDP đến đồng nhất thức tiết kiệm–đầu tư

Bắt đầu với:

$$
Y=C+I+G+NX
$$

Trong nền kinh tế đóng, $NX=0$:

$$
Y=C+I+G
$$

Chuyển vế:

$$
Y-C-G=I
$$

Định nghĩa tiết kiệm quốc gia:

$$
S=Y-C-G
$$

nên:

$$
S=I
$$

Nếu $T$ là thuế ròng sau chuyển giao:

$$
S=(Y-T-C)+(T-G)
$$

Trong đó:

- $Y-T-C$: tiết kiệm tư nhân;
- $T-G$: tiết kiệm công;
- $G>T$: chính phủ thâm hụt, tiết kiệm công âm;
- $T>G$: chính phủ thặng dư, tiết kiệm công dương.

> [!important] $S=I$ là đồng nhất thức, không phải câu chuyện nhân quả hoàn chỉnh
> Nó đúng theo định nghĩa kế toán đối với toàn bộ nền kinh tế đóng. Nó không nói mỗi hộ phải tự tài trợ đầu tư của mình, cũng không có nghĩa mọi ý định tiết kiệm lập tức biến thành một dự án tốt. Hệ thống tài chính và lãi suất là cơ chế phối hợp các quyết định riêng lẻ.

### Ví dụ kế toán

Giả sử:

- $Y=1.000$;
- $C=550$;
- $G=200$;
- $T=150$.

Khi đó:

$$
S=1.000-550-200=250
$$

$$
S_{tư\ nhân}=1.000-150-550=300
$$

$$
S_{công}=150-200=-50
$$

Vậy $S=300-50=250$ và trong nền kinh tế đóng $I=250$.

### Ngoại lệ quan trọng: nền kinh tế mở

Trong nền kinh tế mở, đầu tư trong nước không chỉ dựa vào tiết kiệm trong nước. Từ:

$$
Y=C+I+G+NX
$$

suy ra:

$$
S=I+NX
$$

Trong cách trình bày đầy đủ hơn, $NX=NCO$, nên $S=I+NCO$. Một nước có thể đầu tư nhiều hơn tiết kiệm trong nước nhờ vốn ròng chảy vào. Vì vậy, chuỗi “tiết kiệm trong nước tăng → đầu tư trong nước tăng” là mô hình nền tảng, không phải quy luật một-một trong mọi nền kinh tế mở.

## 10. Thị trường vốn cho vay

Mô hình gom mọi kênh tài chính thành một thị trường:

- **Cung vốn cho vay** đến từ tiết kiệm.
- **Cầu vốn cho vay** đến từ nhu cầu đầu tư.
- **Giá** của vốn là lãi suất thực.

Cung thường dốc lên: lãi suất thực cao làm việc trì hoãn tiêu dùng hấp dẫn hơn. Cầu dốc xuống: lãi suất thực cao làm chi phí vốn tăng, khiến ít dự án có lãi hơn.

### 10.1. Người dân tiết kiệm nhiều hơn

```text
mong muốn tiết kiệm tăng
→ cung vốn cho vay dịch phải
→ lãi suất thực cân bằng giảm
→ nhiều dự án vượt qua ngưỡng sinh lời
→ đầu tư tăng
```

Đây là chuỗi cốt lõi của Step 7.

### 10.2. Cơ hội kinh doanh tốt hơn hoặc có ưu đãi đầu tư

```text
lợi nhuận kỳ vọng của tư bản tăng
→ cầu vốn cho vay dịch phải
→ lãi suất thực tăng
→ tiết kiệm được khuyến khích
→ lượng vốn vay và đầu tư cân bằng tăng
```

Lưu ý: “lãi suất cao đi cùng đầu tư cao” trong trường hợp này không mâu thuẫn với đường cầu đầu tư dốc xuống. Nguyên nhân là **đường cầu đã dịch chuyển**, không phải di chuyển dọc theo một đường cầu cố định.

### 10.3. Thâm hụt ngân sách chính phủ

Theo cách vẽ của Mankiw:

```text
G > T
→ tiết kiệm công giảm
→ tiết kiệm quốc gia giảm
→ cung vốn cho vay dịch trái
→ lãi suất thực tăng
→ đầu tư tư nhân giảm
→ tích lũy vốn và mức sống tương lai thấp hơn so với phản thực
```

Phần đầu tư tư nhân bị giảm được gọi là **crowding out**.

> [!warning] Điều kiện áp dụng
> Đây là kết quả dài hạn, các yếu tố khác không đổi và nền kinh tế gần toàn dụng. Trong suy thoái sâu, chi tiêu công có thể nâng thu nhập và tiết kiệm, ngân hàng trung ương có thể giữ lãi suất thấp, hoặc khu vực tư nhân không muốn đầu tư dù vốn rẻ. Không nên bê nguyên mô hình dài hạn để kết luận tác động ngắn hạn của một gói kích thích.

## 11. Hệ thống tài chính tốt không chỉ cần “nhiều tiền”

Hệ thống tài chính còn phải phân bổ vốn đến dự án có khả năng sinh lợi, giảm chi phí giao dịch, xử lý thông tin và kiểm soát rủi ro. Nếu người tiết kiệm không tin ngân hàng, quyền tài sản không được bảo vệ hoặc chất lượng người vay không thể đánh giá, tiết kiệm có thể không trở thành đầu tư hiệu quả.

Khủng hoảng tài chính minh họa điểm này: giá tài sản giảm có thể làm trung gian tài chính mất khả năng thanh toán, niềm tin suy giảm, tín dụng co lại và ngay cả dự án tốt cũng không vay được. Vì vậy, cùng một lượng tiết kiệm kế toán không bảo đảm cùng một mức năng suất tương lai.

---

# Phần III — Lãi suất thực và giá trị theo thời gian

## 12. Lãi suất danh nghĩa khác lãi suất thực

- **Lãi suất danh nghĩa** cho biết số đơn vị tiền tăng bao nhiêu.
- **Lãi suất thực** cho biết sức mua tăng bao nhiêu.

Xấp xỉ Fisher:

$$
r\approx i-\pi
$$

với $i$ là lãi suất danh nghĩa, $r$ là lãi suất thực và $\pi$ là lạm phát.

### Ví dụ

Gửi 100 triệu đồng với lãi suất danh nghĩa 8%/năm:

- nếu lạm phát 3%, lãi suất thực xấp xỉ 5%;
- nếu lạm phát 10%, lãi suất thực xấp xỉ $-2\%$.

Số dư vẫn tăng từ 100 lên 108 triệu, nhưng trong trường hợp thứ hai sức mua giảm.

Công thức chính xác một kỳ là:

$$
1+r=\frac{1+i}{1+\pi}
$$

Nếu $i=8\%$ và $\pi=10\%$:

$$
r=\frac{1,08}{1,10}-1\approx-1,82\%
$$

Xấp xỉ $8\%-10\%=-2\%$ đủ tốt khi tỷ lệ không quá lớn.

### Kỳ vọng và thực hiện

Khi ký hợp đồng, lạm phát tương lai chưa biết:

$$
r^e\approx i-\pi^e
$$

Sau khi lạm phát xảy ra:

$$
r^{realized}\approx i-\pi^{actual}
$$

Nếu lạm phát thực tế cao hơn dự kiến, người đi vay trả một lãi suất thực thấp hơn dự kiến và người cho vay nhận lợi suất thực thấp hơn dự kiến. Vì quyết định tiết kiệm và đầu tư nhìn về tương lai, **lãi suất thực kỳ vọng** thường là biến phù hợp hơn.

Xem thêm [Correcting Economic Variables for Inflation](../wiki/correcting-for-inflation-real-vs-nominal-indexation-and-regional-parities.md).

## 13. Future value, present value và chiết khấu

Tiền hôm nay đáng giá hơn cùng số tiền trong tương lai vì có thể sinh lãi.

### Future value

Nếu gửi $P$ trong $N$ năm với lãi suất $r$:

$$
FV=P(1+r)^N
$$

Ví dụ, 100 triệu với 5% trong 10 năm:

$$
FV=100(1,05)^{10}\approx162,89\text{ triệu}
$$

### Present value

Giá trị hiện tại của khoản $X$ nhận sau $N$ năm:

$$
PV=\frac{X}{(1+r)^N}
$$

Ví dụ, 200 triệu nhận sau 10 năm:

- chiết khấu 5%: $PV\approx122,78$ triệu;
- chiết khấu 8%: $PV\approx92,64$ triệu.

Lãi suất càng cao, một khoản tiền xa trong tương lai càng có giá trị hiện tại thấp.

### Quyết định đầu tư

Một nhà máy cần 100 tỷ hôm nay và dự kiến tạo 200 tỷ sau 10 năm:

- ở 5%, $PV\approx122,8$ tỷ: dự án có giá trị hiện tại ròng dương;
- ở 8%, $PV\approx92,6$ tỷ: dự án không bù được chi phí ban đầu.

Do đó, lãi suất thực tăng làm số dự án khả thi giảm — nền tảng của đường cầu vốn cho vay dốc xuống.

### Dòng tiền nhiều kỳ

Nếu dự án có dòng tiền $CF_t$:

$$
NPV=-C_0+\sum_{t=1}^{N}\frac{CF_t}{(1+r)^t}
$$

Quy tắc cơ bản: với các dự án độc lập và rủi ro đã được phản ánh phù hợp trong dòng tiền hoặc tỷ lệ chiết khấu, chấp nhận dự án có $NPV>0$.

> [!warning] Phải nhất quán về đơn vị
> - Dòng tiền danh nghĩa đi với lãi suất danh nghĩa.
> - Dòng tiền thực đi với lãi suất thực.
>
> Trộn dòng tiền đã loại lạm phát với lãi suất danh nghĩa sẽ chiết khấu hai lần phần lạm phát.

## 14. Vì sao giá trái phiếu giảm khi lãi suất tăng?

Giá trái phiếu bằng present value của coupon và mệnh giá hoàn trả. Giả sử trái phiếu trả 100 sau một năm:

- nếu lợi suất thị trường 5%, giá là $100/1,05\approx95,24$;
- nếu lợi suất tăng lên 10%, giá là $100/1,10\approx90,91$.

Khoản trả cuối không đổi nhưng tỷ lệ chiết khấu cao hơn, nên giá hôm nay thấp hơn. Đây là cơ chế quan trọng để hiểu rủi ro kỳ hạn.

## 15. Lãi suất dài hạn đến từ đâu?

Lãi suất hai năm không đơn giản bằng lãi suất một năm hôm nay. Nhà đầu tư so sánh:

1. mua trái phiếu hai năm ngay bây giờ;
2. mua trái phiếu một năm rồi tái đầu tư thêm một năm.

Bỏ qua rủi ro, quan hệ xấp xỉ là:

$$
i_{2,t}\approx\frac{i_{1,t}+i^e_{1,t+1}}{2}
$$

Có phần bù kỳ hạn/rủi ro $x$:

$$
i_{2,t}\approx\frac{i_{1,t}+i^e_{1,t+1}+x}{2}
$$

Tổng quát, lợi suất dài hạn phản ánh:

- lãi suất ngắn hạn hiện tại;
- kỳ vọng về chuỗi lãi suất ngắn hạn tương lai;
- phần bù cho rủi ro kỳ hạn, biến động giá và các rủi ro liên quan.

Vì trái phiếu dài hạn nhạy cảm hơn với thay đổi lãi suất, người phải bán trước đáo hạn có thể chịu lỗ lớn. Do đó, đường lợi suất thường dốc lên. Nhưng nếu thị trường kỳ vọng lãi suất ngắn hạn giảm đủ mạnh, đường cong có thể phẳng hoặc đảo ngược.

> [!important] Không suy luận quá mức từ đường cong lợi suất
> Đường cong dốc lên không tự động chứng minh thị trường kỳ vọng lãi suất tăng, vì phần bù kỳ hạn cũng có thể dương. Đường cong đảo ngược không phải lời tiên tri chắc chắn; nó phản ánh giá tài sản và kỳ vọng tại thời điểm quan sát.

Xem [Long-term interest rates](../wiki/long-term-interest-rates-expected-short-rates-and-maturity-risk.md).

---

# Phần IV — Rủi ro và lợi nhuận

## 16. Vì sao người ta ghét rủi ro?

Với người ngại rủi ro, mất 1 triệu gây giảm thỏa dụng lớn hơn mức tăng thỏa dụng khi được thêm 1 triệu. Nguyên nhân là **thỏa dụng biên giảm dần của tài sản**. Vì vậy, nhiều người từ chối trò chơi 50% được 1 triệu và 50% mất 1 triệu dù giá trị tiền tệ kỳ vọng bằng 0.

Ba cách quản lý rủi ro cơ bản:

1. mua bảo hiểm;
2. đa dạng hóa;
3. chọn danh mục có mức rủi ro–lợi nhuận phù hợp.

## 17. Bảo hiểm phân tán chứ không xóa rủi ro

Bảo hiểm gom nhiều rủi ro riêng lẻ. Thay vì một hộ chịu toàn bộ thiệt hại cháy nhà, hàng nghìn người đóng phí để chia sẻ tổn thất của số ít người không may.

Hai vấn đề cản trở bảo hiểm hoàn hảo:

- **Lựa chọn bất lợi**: người có rủi ro cao có xu hướng mua bảo hiểm nhiều hơn.
- **Rủi ro đạo đức**: sau khi được bảo hiểm, người mua có thể ít thận trọng hơn.

## 18. Đa dạng hóa loại bỏ rủi ro nào?

Nếu dồn việc làm và tiền hưu trí vào cổ phiếu của cùng một công ty, một cú sốc công ty có thể làm mất cả thu nhập lẫn tài sản. Chia danh mục cho nhiều doanh nghiệp làm giảm **rủi ro riêng của doanh nghiệp**.

Nhưng suy thoái, khủng hoảng tài chính hoặc cú sốc lãi suất có thể ảnh hưởng gần như toàn thị trường. **Rủi ro thị trường** không thể bị loại bỏ chỉ bằng cách nắm giữ thêm cổ phiếu trong cùng thị trường.

Theo ví dụ lịch sử trong Mankiw, phần lớn lợi ích đa dạng hóa cổ phiếu xuất hiện khi đi từ một cổ phiếu lên vài chục cổ phiếu; sau đó lợi ích biên nhỏ dần. Đây là minh họa lịch sử, không phải quy tắc danh mục cố định cho mọi thị trường.

## 19. Quan hệ risk–return

Tài sản an toàn thường có lợi nhuận kỳ vọng thấp hơn; tài sản rủi ro phải hứa hẹn lợi nhuận kỳ vọng cao hơn để hấp dẫn người nắm giữ. Nhưng **lợi nhuận kỳ vọng cao không có nghĩa lợi nhuận thực tế chắc chắn cao**.

Ví dụ minh họa của Mankiw dùng lợi suất thực lịch sử dài hạn khoảng 8% cho cổ phiếu và 3% cho trái phiếu chính phủ ngắn hạn. Các giai đoạn và nguồn khác cho con số khác; không nên dùng chúng làm dự báo. Bài học bền vững là:

```text
muốn lợi nhuận kỳ vọng cao hơn
↔ thường phải chấp nhận biến động và khả năng thua lỗ cao hơn
```

Lựa chọn phù hợp tùy mức ngại rủi ro, thời hạn đầu tư, khả năng chịu lỗ và mức độ đa dạng hóa. Xem [Managing Risk](../wiki/managing-risk-risk-aversion-insurance-diversification.md).

---

# Phần V — Đo lường và giải thích thất nghiệp dài hạn

## 20. Ba trạng thái lao động

Khảo sát lao động phân người trưởng thành vào ba nhóm:

1. **Có việc làm**: đang làm việc, kể cả toàn thời gian hoặc bán thời gian; thường bao gồm người tạm nghỉ nhưng vẫn có việc.
2. **Thất nghiệp**: không có việc, sẵn sàng làm và đã tích cực tìm việc trong khoảng thời gian quy định; người chờ được gọi lại sau tạm sa thải cũng có thể được tính.
3. **Ngoài lực lượng lao động**: không thuộc hai nhóm trên, như nhiều sinh viên toàn thời gian, người nghỉ hưu, người chăm sóc gia đình hoặc người đã ngừng tìm việc.

$$
\text{Lực lượng lao động}=\text{Có việc}+\text{Thất nghiệp}
$$

$$
\text{Tỷ lệ thất nghiệp}=\frac{\text{Thất nghiệp}}{\text{Lực lượng lao động}}\times100
$$

$$
\text{Tỷ lệ tham gia}=\frac{\text{Lực lượng lao động}}{\text{Dân số trưởng thành}}\times100
$$

### Ví dụ

Một nền kinh tế có 100 người trưởng thành:

- 60 người có việc;
- 5 người không có việc và đang tìm;
- 10 người muốn làm nhưng đã ngừng tìm;
- 25 người không tìm việc vì học tập, nghỉ hưu hoặc lý do khác.

Khi đó:

$$
LF=60+5=65
$$

$$
u=\frac{5}{65}\times100\approx7,69\%
$$

$$
LFPR=\frac{65}{100}\times100=65\%
$$

Mười người nản chí không nằm trong mẫu số lực lượng lao động và cũng không nằm trong số thất nghiệp chính thức.

## 21. Vì sao tỷ lệ thất nghiệp chính thức chưa đủ?

Chỉ số chính thức có thể:

- **đánh giá thấp** mức thiếu việc vì bỏ sót người muốn làm nhưng đã ngừng tìm và người phải làm bán thời gian ngoài ý muốn;
- **đánh giá cao** khó khăn tìm việc nếu tính cả người đang chuyển việc bình thường và sẽ sớm nhận việc phù hợp;
- che khuất khác biệt lớn giữa nhóm tuổi, trình độ, ngành và khu vực;
- giảm vì người thất nghiệp rời lực lượng lao động, chứ không phải vì họ tìm được việc.

Do đó nên đọc cùng:

- tỷ lệ tham gia lực lượng lao động;
- tỷ lệ việc làm trên dân số;
- số người làm bán thời gian vì lý do kinh tế;
- nhóm gắn kết biên và lao động nản chí;
- thời lượng thất nghiệp;
- tăng việc làm và số giờ làm;
- tiền lương thực.

U-6 của Hoa Kỳ là một thước đo rộng, bổ sung người gắn kết biên và người làm bán thời gian ngoài ý muốn. Các định nghĩa cụ thể thuộc từng cơ quan thống kê; khi áp dụng cho Việt Nam hoặc quốc gia khác phải kiểm tra chuẩn địa phương, không mặc nhiên sao chép BLS.

## 22. Nghịch lý thời lượng thất nghiệp

“Một phần lớn đợt thất nghiệp là ngắn, nhưng phần lớn thất nghiệp quan sát tại một thời điểm có thể là dài hạn.”

Ví dụ của Mankiw: mỗi tuần một văn phòng có bốn người thất nghiệp. Ba người thất nghiệp cả năm; người thứ tư thay đổi mỗi tuần.

- Trong cả năm gặp 55 người: 52 người thất nghiệp một tuần, 3 người thất nghiệp cả năm.
- 95% **đợt thất nghiệp** là ngắn.
- Nhưng tại bất kỳ tuần nào, 3 trong 4 người đang quan sát là thất nghiệp dài hạn.

Bài học: đếm số đợt và chụp ảnh số người tại một thời điểm trả lời hai câu hỏi khác nhau. Chính sách cho người chuyển việc vài tuần không nhất thiết phù hợp với người mất kết nối thị trường lao động trong nhiều tháng.

## 23. Vì sao thất nghiệp không bằng 0?

### 23.1. Thất nghiệp tạm thời do tìm kiếm

Người lao động và việc làm khác nhau về kỹ năng, địa điểm, lương và điều kiện. Thông tin không hoàn hảo, phỏng vấn mất thời gian và nền kinh tế luôn thay đổi. Một kỹ sư rời công ty để tìm vị trí phù hợp hơn có thể được tính thất nghiệp trong thời gian tìm kiếm.

Thay đổi nhu cầu giữa ngành hoặc vùng — **dịch chuyển cơ cấu ngành** — làm một nơi sa thải trong khi nơi khác tuyển dụng. Ghép đúng người với đúng việc mất thời gian, nhưng kết quả có thể nâng năng suất.

Chính sách và công nghệ có thể rút ngắn quá trình qua cổng việc làm, thông tin tuyển dụng, tư vấn, đào tạo và hỗ trợ di chuyển. Bảo hiểm thất nghiệp giảm cú sốc thu nhập và cho phép tìm việc phù hợp hơn, nhưng cũng có thể giảm cường độ tìm kiếm. Đây là đánh đổi, không phải kết luận rằng cứ giảm trợ cấp là phúc lợi tăng.

### 23.2. Thất nghiệp cơ cấu

Thất nghiệp cơ cấu xảy ra khi số người muốn làm vượt số việc tại mức lương hiện hành trong một thị trường cụ thể, hoặc khi kỹ năng/địa điểm không khớp.

Mankiw trình bày ba cơ chế làm lương cao hơn mức cân bằng:

- lương tối thiểu có tính ràng buộc;
- công đoàn và thương lượng tập thể;
- lương hiệu quả do doanh nghiệp chủ động trả.

Lương hiệu quả có thể có lợi cho doanh nghiệp vì:

1. cải thiện sức khỏe người lao động;
2. giảm nghỉ việc và chi phí tuyển–đào tạo;
3. thu hút ứng viên tốt hơn;
4. khuyến khích nỗ lực khi giám sát khó.

Ví dụ Ford năm 1914 trả 5 USD/ngày — khoảng gấp đôi mức phổ biến theo nguồn — đi cùng giảm nghỉ việc, giảm vắng mặt và tăng năng suất. Đây là minh họa lịch sử cho lương hiệu quả, không phải bằng chứng rằng tăng lương ở mọi công ty luôn tự bù chi phí.

Cũng cần tránh biến mô hình thành khẩu hiệu: tác động của lương tối thiểu hoặc công đoàn tùy mức ràng buộc, quyền lực mua lao động của doanh nghiệp và bối cảnh thể chế. Ngay nguồn Mankiw cũng trình bày tranh luận hai phía về công đoàn.

### 23.3. Thất nghiệp chu kỳ

Đây là phần thất nghiệp do nền kinh tế suy yếu so với mức bình thường:

$$
\text{Thất nghiệp thực tế}=\text{Thất nghiệp tự nhiên}+\text{Thất nghiệp chu kỳ}
$$

Và:

$$
\text{Thất nghiệp tự nhiên}=\text{Tạm thời}+\text{Cơ cấu}
$$

Khi tổng cầu giảm, doanh nghiệp bán ít hàng, giảm sản xuất và cắt lao động trên diện rộng. Đây không chỉ là vấn đề ghép sai kỹ năng hoặc vài mức lương riêng lẻ.

## 24. “Tự nhiên” không có nghĩa là gì?

Tỷ lệ thất nghiệp tự nhiên:

- **không bằng 0**;
- **không cố định theo thời gian**;
- **không nhất thiết tối ưu về đạo đức hay phúc lợi**;
- **có thể bị chính sách và thể chế làm thay đổi**;
- **không quan sát trực tiếp**, mà phải ước lượng.

Nó thay đổi theo cơ cấu tuổi, kinh nghiệm lao động, công nghệ ghép việc, kỹ năng, trợ cấp thất nghiệp, lương tối thiểu, công đoàn, hành vi trả lương và quyền lực thị trường. Một con số ước lượng cho Hoa Kỳ trong một năm không thể được dùng như hằng số cho quốc gia khác.

---

# Phần VI — Tăng trưởng dài hạn khác phục hồi chu kỳ

## 25. Hai câu hỏi, hai đường chân trời

| Câu hỏi | Tăng trưởng dài hạn | Phục hồi chu kỳ |
|---|---|---|
| Trọng tâm | Năng lực sản xuất và mức sống | Khoảng cách giữa sản lượng thực tế và tiềm năng |
| Biến chính | Năng suất, $K/L$, $H/L$, công nghệ, thể chế | Tổng cầu, tồn kho, việc làm, công suất dư thừa, điều kiện tín dụng |
| Thời gian | Nhiều năm đến nhiều thập kỷ | Quý đến vài năm |
| Thất nghiệp | Tỷ lệ tự nhiên và cơ cấu | Phần thất nghiệp chu kỳ |
| Chính sách | Giáo dục, R&D, hạ tầng, tiết kiệm, thể chế | Tiền tệ, tài khóa, ổn định tài chính |
| Sai lầm điển hình | Đồng nhất tăng vốn với tăng trưởng vĩnh viễn | Thấy GDP dương rồi tuyên bố lao động đã phục hồi |

Một nền kinh tế có thể đồng thời:

- có xu hướng năng suất dài hạn tốt;
- nhưng đang suy thoái vì tổng cầu giảm.

Hoặc:

- GDP tăng trở lại sau suy thoái;
- nhưng tăng chưa đủ nhanh để hấp thụ người lao động mới và người từng mất việc.

Trường hợp GDP thực tăng nhưng thất nghiệp vẫn tăng được gọi là **jobless recovery** hoặc growth recession. “Hết suy thoái” chỉ nói hoạt động không còn giảm theo cách định nghĩa chu kỳ; không có nghĩa GDP đã trở lại xu hướng cũ hay thị trường lao động đã hồi phục hoàn toàn.

## 26. Vì sao tiết kiệm có thể tốt dài hạn nhưng gây khó ngắn hạn?

Ở dài hạn và gần toàn dụng:

```text
tiết kiệm cao hơn → vốn cho vay nhiều hơn → đầu tư cao hơn → vốn và năng suất cao hơn
```

Trong suy thoái, nếu mọi hộ đồng loạt cắt tiêu dùng nhưng doanh nghiệp không muốn đầu tư, tổng cầu có thể giảm:

```text
mong muốn tiết kiệm tăng
→ tiêu dùng giảm
→ doanh thu và sản lượng giảm
→ thu nhập giảm
→ tiết kiệm thực tế có thể không tăng như dự định
```

Đây là nghịch lý tiết kiệm. Hai kết quả không mâu thuẫn; chúng dùng giả định và đường chân trời khác nhau. Trước khi áp dụng mô hình, luôn hỏi: nền kinh tế có gần toàn dụng không, doanh nghiệp có muốn đầu tư không, hệ thống tín dụng có hoạt động không và ngân hàng trung ương phản ứng thế nào?

---

# Phần VII — Nối toàn bộ hệ thống

## 27. Chuỗi chuẩn của checkpoint

### Mắt xích 1: Tiết kiệm

Hộ gia đình trì hoãn tiêu dùng; chính phủ tăng tiết kiệm công nếu thu vượt chi; vốn nước ngoài có thể bổ sung nguồn tài trợ trong nền kinh tế mở.

### Mắt xích 2: Nguồn vốn cho vay

Ngân hàng, trái phiếu, cổ phiếu và quỹ tài chính chuyển nguồn lực từ người tiết kiệm đến người cần vốn. Chất lượng trung gian và thể chế quyết định vốn có đến đúng dự án hay không.

### Mắt xích 3: Lãi suất thực

Lãi suất thực là phần thưởng cho trì hoãn tiêu dùng và chi phí sức mua thực của người vay. Nó điều hòa cung tiết kiệm với cầu đầu tư. Trong thực tế có nhiều lãi suất cùng tồn tại vì kỳ hạn, rủi ro vỡ nợ, thanh khoản và thuế khác nhau.

### Mắt xích 4: Đầu tư

Doanh nghiệp so present value của dòng tiền tương lai với chi phí hôm nay. Lãi suất thực thấp hơn làm nhiều dự án có NPV dương hơn, nếu triển vọng doanh thu và khả năng vay không suy yếu.

### Mắt xích 5: Vốn trên lao động

Đầu tư gộp chưa đủ; phải trừ khấu hao và xét số lao động:

$$
\Delta(K/L)\approx\text{đầu tư trên lao động}-\text{khấu hao và pha loãng vốn}
$$

Nếu dân số lao động tăng nhanh, tổng vốn tăng nhưng $K/L$ vẫn có thể không tăng.

### Mắt xích 6: Năng suất

Nhiều và tốt hơn về máy móc, kỹ năng, hạ tầng và công nghệ làm tăng sản lượng mỗi giờ. Nhưng vốn vật chất riêng lẻ chịu lợi suất giảm dần.

### Mắt xích 7: Mức sống

Năng suất cao hỗ trợ tiền lương thực, tiêu dùng và GDP thực/người cao hơn. GDP/người vẫn không phải thước đo hoàn chỉnh của phúc lợi vì bỏ sót phân phối, môi trường, thời gian nhàn rỗi và nhiều hoạt động phi thị trường.

## 28. Những chỗ chuỗi có thể đứt

Không nên dùng chuỗi như định luật cơ học. Nó có thể yếu đi khi:

1. tiết kiệm chảy vào tài sản có sẵn thay vì tư bản mới;
2. ngân hàng yếu hoặc thông tin tín dụng kém;
3. doanh nghiệp bi quan nên không đầu tư dù lãi suất thấp;
4. lãi suất chính sách giảm nhưng phần bù rủi ro tín dụng tăng;
5. vốn đầu tư bị phân bổ vào dự án năng suất thấp;
6. thiếu kỹ năng hoặc hạ tầng bổ trợ;
7. khấu hao và tăng lao động làm vốn trên lao động không tăng;
8. nền kinh tế mở khiến vốn chảy ra hoặc chảy vào;
9. cú sốc ngắn hạn làm sản lượng thực tế thấp hơn năng lực;
10. công nghệ không tiến bộ nên hiệu ứng tăng vốn giảm dần.

## 29. Ví dụ tích hợp

Giả sử chính phủ đưa ra ưu đãi thuế tiết kiệm hưu trí và hộ gia đình thực sự tăng tiết kiệm quốc gia.

**Trong mô hình dài hạn nền kinh tế đóng:** cung vốn cho vay dịch phải, lãi suất thực giảm và đầu tư tăng. Doanh nghiệp xây thêm nhà máy, nên sau khi trừ khấu hao, $K/L$ tăng. Năng suất và GDP thực/người tăng. Hiệu ứng tăng trưởng mạnh trong giai đoạn chuyển tiếp rồi yếu dần do lợi suất giảm dần.

**Những câu hỏi kiểm tra trước khi kết luận:**

- Ưu đãi có tạo tiết kiệm mới hay chỉ chuyển tiền giữa các tài khoản?
- Lợi ích thuế có làm thâm hụt ngân sách tăng, bù trừ tiết kiệm tư nhân không?
- Nền kinh tế mở có khiến vốn chảy ra nước ngoài không?
- Doanh nghiệp có dự án NPV dương không?
- Hệ thống tài chính có chuyển vốn đến doanh nghiệp hiệu quả không?
- Nền kinh tế đang toàn dụng hay suy thoái?

**Tác động lên thất nghiệp:** trong ngắn hạn không thể suy ra chỉ từ mô hình tăng trưởng. Đầu tư xây dựng có thể tăng việc làm, nhưng tự động hóa cũng có thể gây dịch chuyển ngành. Về dài hạn, chuyển dịch tạo thất nghiệp tạm thời; nếu kỹ năng không phù hợp kéo dài, nó có thể trở thành cơ cấu. Nếu tổng cầu yếu, thất nghiệp chu kỳ có thể cùng tồn tại.

---

# Phần VIII — Lộ trình học Step 7

## 30. Kế hoạch 10 buổi

| Buổi | Nội dung | Sản phẩm tự học |
|---:|---|---|
| 1 | Năng suất và bốn yếu tố | Tự giải thích hàm sản xuất bằng một doanh nghiệp quen thuộc |
| 2 | Ghép lãi, Rule of 70, bắt kịp | Tính hai kịch bản tăng trưởng 20–40 năm |
| 3 | Lợi suất giảm dần, mức và tốc độ | Viết 5 câu bác bỏ “tiết kiệm cao làm tăng trưởng vĩnh viễn” |
| 4 | Hệ thống tài chính và $S=I$ | Phân loại 10 giao dịch thành tiết kiệm hay đầu tư vĩ mô |
| 5 | Thị trường vốn cho vay | Vẽ ba cú sốc: tiết kiệm, ưu đãi đầu tư, thâm hụt |
| 6 | Lãi suất thực và present value | Làm các bài tính ở mục 32 |
| 7 | Trái phiếu, lãi suất dài hạn | Giải thích vì sao giá trái phiếu giảm khi yield tăng |
| 8 | Rủi ro, bảo hiểm, đa dạng hóa | Phân biệt rủi ro riêng và rủi ro thị trường |
| 9 | Đo thất nghiệp | Tính $u$, LFPR và phân tích người nản chí |
| 10 | Tự nhiên, cơ cấu, chu kỳ | Viết một trang nối toàn bộ checkpoint |

## 31. Bộ câu hỏi đọc tin

Khi gặp tin “lãi suất giảm để hỗ trợ tăng trưởng”, hãy hỏi:

1. Đây là lãi suất danh nghĩa hay thực?
2. Kỳ hạn ngắn hay dài?
3. Lạm phát kỳ vọng thay đổi không?
4. Lợi suất trái phiếu và spread tín dụng có cùng giảm không?
5. Doanh nghiệp thiếu vốn hay thiếu nhu cầu?
6. Đầu tư nói đến máy móc mới hay giao dịch tài sản cũ?
7. Tác động đang nói về phục hồi quý tới hay năng suất nhiều năm tới?
8. Thất nghiệp giảm vì có thêm việc hay vì người lao động bỏ tìm?
9. Năng suất tăng do $K/L$, kỹ năng hay công nghệ?
10. Kết luận có phụ thuộc giả định nền kinh tế đóng và gần toàn dụng không?

---

# Phần IX — Bài tập checkpoint

## 32. Bài tập

### Bài 1 — Tiết kiệm quốc gia

Cho $Y=2.000$, $C=1.200$, $G=400$, $T=350$.

1. Tính tiết kiệm tư nhân.
2. Tính tiết kiệm công.
3. Tính tiết kiệm quốc gia.
4. Trong nền kinh tế đóng, đầu tư bằng bao nhiêu?

### Bài 2 — Dịch chuyển trên thị trường vốn cho vay

Với mỗi tình huống, nêu đường nào dịch chuyển và dấu thay đổi của lãi suất thực, lượng tiết kiệm/đầu tư cân bằng:

1. Hộ gia đình muốn dành nhiều tiền hơn cho tuổi già.
2. Công nghệ AI làm nhiều dự án máy chủ có lợi nhuận kỳ vọng cao hơn.
3. Chính phủ tăng chi nhưng không tăng thuế, nền kinh tế gần toàn dụng.

### Bài 3 — Lãi suất thực

Một khoản tiền gửi trả 7% danh nghĩa. Lạm phát kỳ vọng là 3% nhưng thực tế là 5%.

1. Lãi suất thực kỳ vọng xấp xỉ bao nhiêu?
2. Lãi suất thực thực hiện xấp xỉ bao nhiêu?
3. Kết quả bất ngờ có lợi tương đối cho người vay hay người cho vay?

### Bài 4 — Present value

Một máy có giá 800 triệu hôm nay và tạo 1 tỷ sau ba năm.

1. Tính PV ở lãi suất 5%.
2. Tính PV ở lãi suất 10%.
3. Bỏ qua rủi ro và các dòng tiền khác, có mua máy trong từng trường hợp không?

### Bài 5 — Thất nghiệp

Dân số trưởng thành gồm:

- 700 người có việc;
- 50 người không có việc và đang tích cực tìm;
- 30 người muốn làm nhưng đã ngừng tìm;
- 20 người làm bán thời gian nhưng muốn toàn thời gian;
- 200 người không muốn hoặc không thể tham gia.

Tính lực lượng lao động, tỷ lệ thất nghiệp chính thức và tỷ lệ tham gia. Giải thích vì sao chỉ số chính thức chưa phản ánh hết thiếu việc.

### Bài 6 — Phân loại nguyên nhân

Phân loại chủ yếu là tạm thời, cơ cấu hay chu kỳ:

1. Một kế toán nghỉ việc để tìm công ty phù hợp hơn.
2. Lao động nhà máy mất việc lâu dài vì kỹ năng không phù hợp với ngành mới.
3. Nhiều ngành cùng sa thải sau khi tiêu dùng toàn nền kinh tế giảm.
4. Lao động dầu khí tìm việc mới sau khi giá dầu giảm và hoạt động chuyển sang ngành khác.

### Bài 7 — Câu tổng hợp

Viết 150–250 từ giải thích nhận định:

> “Tỷ lệ tiết kiệm cao hơn có thể nâng mức sống dài hạn, nhưng không bảo đảm nền kinh tế phục hồi nhanh hơn trong năm tới.”

Bài đạt yêu cầu phải dùng đúng: vốn cho vay, lãi suất thực, đầu tư, vốn trên lao động, lợi suất giảm dần, tổng cầu và thất nghiệp chu kỳ.

## 33. Đáp án ngắn

### Bài 1

$$
S_p=Y-T-C=2.000-350-1.200=450
$$

$$
S_g=T-G=350-400=-50
$$

$$
S=450-50=400
$$

Nền kinh tế đóng: $I=S=400$.

### Bài 2

1. Cung vốn dịch phải → $r$ giảm, lượng vốn và đầu tư tăng.
2. Cầu vốn dịch phải → $r$ tăng, lượng tiết kiệm và đầu tư tăng.
3. Tiết kiệm công và quốc gia giảm, cung dịch trái → $r$ tăng, đầu tư tư nhân giảm trong mô hình dài hạn.

### Bài 3

- $r^e\approx7\%-3\%=4\%$.
- $r^{realized}\approx7\%-5\%=2\%$.
- Lạm phát cao hơn dự kiến có lợi tương đối cho người vay, bất lợi cho người cho vay.

### Bài 4

$$
PV_{5\%}=\frac{1.000}{1,05^3}\approx863,84\text{ triệu}
$$

NPV khoảng $+63,84$ triệu, nên mua theo giả định.

$$
PV_{10\%}=\frac{1.000}{1,10^3}\approx751,31\text{ triệu}
$$

NPV khoảng $-48,69$ triệu, nên không mua theo giả định.

### Bài 5

Người làm bán thời gian vẫn được tính là có việc:

$$
LF=700+20+50=770
$$

$$
u=\frac{50}{770}\times100\approx6,49\%
$$

Dân số trưởng thành là 1.000:

$$
LFPR=\frac{770}{1.000}\times100=77\%
$$

Chỉ số chính thức bỏ sót 30 người nản chí và không thể hiện 20 người thiếu giờ làm.

### Bài 6

1. Tạm thời.
2. Cơ cấu.
3. Chu kỳ.
4. Ban đầu chủ yếu tạm thời do dịch chuyển ngành; có thể thành cơ cấu nếu kỹ năng hoặc địa điểm không phù hợp kéo dài.

---

# Phần X — Những lỗi người mới thường mắc

## 34. Checklist chống nhầm

- [ ] Không gọi mọi hoạt động mua tài sản là đầu tư vĩ mô.
- [ ] Không coi $S=I$ là quan hệ một-một giữa từng người tiết kiệm và từng doanh nghiệp.
- [ ] Không dùng lãi suất danh nghĩa để nói về chi phí thực mà bỏ qua lạm phát kỳ vọng.
- [ ] Không chiết khấu dòng tiền thực bằng lãi suất danh nghĩa.
- [ ] Không suy ra lãi suất tăng luôn làm đầu tư quan sát được giảm; có thể cầu đầu tư vừa dịch phải.
- [ ] Không coi tăng tiết kiệm là cách tạo tăng trưởng vĩnh viễn khi công nghệ đứng yên.
- [ ] Không coi GDP tăng dương là thị trường lao động đã phục hồi.
- [ ] Không coi người không có việc nào cũng là thất nghiệp theo thống kê.
- [ ] Không coi tỷ lệ thất nghiệp giảm luôn là tin tốt nếu tỷ lệ tham gia cũng giảm.
- [ ] Không coi thất nghiệp tự nhiên là cố định, tối ưu hoặc không thể can thiệp.
- [ ] Không coi đa dạng hóa có thể xóa rủi ro toàn thị trường.
- [ ] Không dùng lợi nhuận lịch sử làm cam kết lợi nhuận tương lai.
- [ ] Không áp dụng kết luận nền kinh tế đóng cho một nước có dòng vốn quốc tế lớn mà không điều chỉnh.
- [ ] Không trộn mô hình tăng trưởng dài hạn với mô hình tổng cầu ngắn hạn.

> [!success] Checkpoint cuối
> Bạn hoàn thành Step 7 khi có thể tự nói, không nhìn tài liệu:
>
> **Tiết kiệm cung cấp nguồn lực cho hệ thống tài chính. Trong mô hình vốn cho vay dài hạn, lãi suất thực cân bằng tiết kiệm với đầu tư. Lãi suất thực ảnh hưởng present value nên quyết định dự án nào được thực hiện. Đầu tư ròng làm tăng vốn trên lao động và năng suất, qua đó nâng mức sống; nhưng lợi suất giảm dần khiến tiết kiệm chủ yếu nâng mức thu nhập, còn tăng trưởng bền vững cần công nghệ. Thất nghiệp không về 0 vì tìm kiếm và cơ cấu; phần vượt mức bình thường do suy thoái là thất nghiệp chu kỳ. Vì vậy tăng trưởng xu hướng và phục hồi chu kỳ là hai vấn đề liên quan nhưng không đồng nhất.**

---

# Nguồn tham khảo trong kho tri thức

## Concept wiki chính

1. [Production and Growth — Productivity, its Determinants, and Long-Run Growth Policy](../wiki/production-and-growth-productivity-determinants-and-policy.md)
2. [Saving, Investment, and the Financial System](../wiki/saving-investment-and-the-financial-system.md)
3. [The Basic Tools of Finance](../wiki/basic-tools-of-finance-present-value-compounding-and-discounting.md)
4. [Long-term interest rates — expected short rates and maturity risk](../wiki/long-term-interest-rates-expected-short-rates-and-maturity-risk.md)
5. [Managing Risk — Risk Aversion, Insurance, Diversification, and Risk–Return](../wiki/managing-risk-risk-aversion-insurance-diversification.md)
6. [Correcting Economic Variables for Inflation](../wiki/correcting-for-inflation-real-vs-nominal-indexation-and-regional-parities.md)
7. [Measuring unemployment, labor underutilization, and jobless recovery](../wiki/measuring-unemployment-labor-underutilization-and-jobless-recovery.md)
8. [Natural rate of unemployment](../wiki/natural-rate-of-unemployment-frictional-structural-and-cyclical.md)
9. [Capital Accumulation, the Steady State, and the Golden Rule](../wiki/capital-accumulation-steady-state-and-golden-rule-saving.md)

## Nguồn sách đã đối chiếu trực tiếp khi biên soạn

- Mankiw 8e Ch.12: [The Real Economy in the Long Run](../raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/039-the-real-economy-in-the-long-run.md)
- Mankiw 8e Ch.13: [Saving, Investment, and the Financial System](../raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/042-saving-investment-and-the-financial-system.md)
- Mankiw 8e Ch.14: [The Basic Tools of Finance](../raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/044-the-basic-tools-of-finance.md) và [Compounding, risk, and asset valuation](../raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/045-the-magic-of-compounding-and-the-rule-of-70.md)
- Mankiw 8e Ch.15: [Unemployment measurement, job search, and minimum wages](../raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/046-the-magic-of-compounding-and-the-rule-of-70-table-1.md) và [Unions and efficiency wages](../raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/048-15-4-unions-and-collective-bargaining.md)

## Giới hạn bằng chứng

- Bài dùng mô hình nhập môn để tổ chức tư duy, không phải mô hình dự báo đầy đủ.
- Các số liệu Hoa Kỳ, lợi suất lịch sử và ví dụ Ford là dữ liệu theo thời kỳ của nguồn sách; không được hiểu là số liệu hiện hành hoặc kết quả áp dụng phổ quát.
- Quan hệ nhân quả về tăng trưởng, thể chế, giáo dục và chính sách khó tách khỏi các yếu tố đồng thời; ví dụ quốc gia chỉ minh họa cơ chế nếu nguồn không có thiết kế nhận dạng nhân quả.
- Khái niệm và chuẩn đo thất nghiệp cụ thể có thể khác giữa cơ quan thống kê và quốc gia; cần kiểm tra định nghĩa khi đọc dữ liệu thực tế.
