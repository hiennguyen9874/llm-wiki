---
type: Concept
title: GDP — income-expenditure identity, measurement rules, components, and real versus nominal
description: GDP's market-value, income-expenditure, and C+I+G+NX measures; its distinction from GNP through net foreign income; and nominal/real GDP and deflator measurement.
tags: [gdp, macroeconomics, national-accounts, measurement, real-gdp, gdp-deflator, consumption, investment]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T17:57:15Z }
sources:
  - id: mankiw-ch10
    resource: ../raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/034-the-data-of-macroeconomics.md
    title: "The Data of Macroeconomics"
  - id: krugman-ch7-040
    resource: ../raw/Macroeconomics_Krugman/040-chapter-7-gdp-and-the-cpi-tracking-the-macroeconomy.md
    title: "Chapter 7 GDP and the CPI: Tracking the Macroeconomy"
  - id: krugman-ch7-041
    resource: ../raw/Macroeconomics_Krugman/041-chapter-7-gdp-and-the-cpi-tracking-the-macroeconomy-pitfalls.md
    title: "Chapter 7 GDP and the CPI: Tracking the Macroeconomy — Pitfalls"
  - id: krugman-ch7-043
    resource: ../raw/Macroeconomics_Krugman/043-chapter-7-gdp-and-the-cpi-tracking-the-macroeconomy-practice-questions.md
    title: "Chapter 7 GDP and the CPI: Tracking the Macroeconomy — Practice questions"
  - id: krugman-ch10-053
    resource: ../raw/Macroeconomics_Krugman/053-chapter-10-savings-investment-spending-and-the-financial-system.md
    title: "Chapter 10 Savings, Investment Spending, and the Financial System (Krugman/Wells)"
  - id: blanchard-kuwait-069
    resource: ../raw/Macroeconomics_OlivierBlanchard/069-gdp-versus-gnp-the-example-of-kuwait.md
    title: "GDP versus GNP: The Example of Kuwait"
---

# GDP — income-expenditure identity, measurement rules, components, and real versus nominal

GDP measures total income and total expenditure simultaneously because every transaction has a buyer and seller — a $100 lawn-mowing payment raises both — and in the circular flow households buy goods and services from firms while firms pay wages, rent and profit back to households, so GDP is the market value of all final goods and services produced within a country in a given period of time[^mankiw-ch10]. Nominal GDP values output at current prices; real GDP values it at base-year prices to isolate quantity change; the GDP deflator (nominal/real ×100) measures the price level and its change is the inflation rate[^mankiw-ch10].

## 10-1 Income equals expenditure

- For the economy as a whole income must equal expenditure; GDP can be computed either way[^mankiw-ch10].
- Simple circular-flow: households buy from firms via goods-and-services markets; firms pay factors via factor markets; money flows continuously[^mankiw-ch10]. Simplified assumptions (all goods bought by households, all income spent) are later relaxed — taxes/saving and government/firm purchases split the flow but buyer-seller identity remains[^mankiw-ch10].
- Reporter statistics — GDP, inflation/deflation, unemployment, retail sales, trade deficit — are macroeconomic, about the entire economy[^mankiw-ch10].

### Three equivalent accounting views

Krugman and Wells' expanded circular-flow diagram distinguishes its real side — goods-and-services transactions among households, firms, government, and the rest of the world — from financial flows. On the real side, GDP can be calculated equivalently as (1) the value of final output, or the sum of firms' value added; (2) aggregate spending on domestically produced final goods and services; or (3) factor income (wages, interest, rent, and profit).[^krugman-ch7-040]

Their ore → steel → car example makes the double-counting rule concrete: $4,200 of ore, $9,000 of steel, and a $21,500 car yield $21,500 GDP, not $34,700 in gross sales, because value added is $4,200 + $4,800 + $12,500. The same $21,500 equals final spending on the car and total factor payments ($15,700 wages, $2,600 interest, $1,000 rent, and $2,200 profit).[^krugman-ch7-040]

> [!note] Source transcription inconsistency
> Chapter 7's prose identifies the spending components as $C$, $I$, $G$, exports $X$, minus imports $IM$, but its displayed Equation 7-1 is rendered `$GDP = C + I + C + X - IM$`. This page retains the standard $C+I+G+NX$ identity, now independently displayed correctly as $GDP=C+I+G+X-IM$ in Krugman and Wells Ch. 10 as well as in the Mankiw source; the raw Chapter 7 equation should not be treated as evidence that government purchases are consumption.[^krugman-ch7-040][^krugman-ch10-053][^mankiw-ch10]

## 10-2 Definition — seven phrases

> **Gross domestic product (GDP)** is the market value of all final goods and services produced within a country in a given period of time[^mankiw-ch10].

1. **"Market value"** — uses market prices to add apples and oranges; if an apple costs twice an orange it counts twice[^mankiw-ch10].
2. **"Of all ..."** — comprehensive for legally sold market items, including housing services. Owner-occupied housing adds imputed rent (owner renting to herself) to both expenditure and income; otherwise neighbours swapping $10,000 rents would spuriously create $20,000 GDP[^mankiw-ch10]. Excludes illicit drugs, counterfeit/cash-in-hand work, and home production consumed at home (store vegetables count, garden vegetables do not)[^mankiw-ch10]. Paradox: Karen paying Doug to mow lawn counts; if they marry and he continues, GDP falls because no market transaction[^mankiw-ch10].
3. **"Final ..."** — counts only final goods to avoid double counting intermediate goods (paper → greeting card; paper value already in card price)[^mankiw-ch10]. Exception: intermediate good added to inventory counts as inventory investment (final-for-the-moment); later sale subtracts from inventory[^mankiw-ch10].
4. **"Goods and services ..."** — tangible goods (food, clothing, cars) plus intangible services (haircuts, medical care, education, concerts)[^mankiw-ch10].
5. **"Produced ..."** — currently produced only; used-car sale excluded (new Ford car counts)[^mankiw-ch10].
6. **"Within a country ..."** — geographic: Canadian working temporarily in US counts in US GDP not Canadian; American-owned factory in Haiti counts in Haiti's GDP[^mankiw-ch10].
7. **"In a given period of time"** — flow over a year or quarter; quarterly GDP reported at annual rate (quarter ×4) and seasonally adjusted to remove regular seasonal cycles (e.g., December holiday peak), so news figures are seasonally adjusted annual rates[^mankiw-ch10].

- Income and expenditure calculations should match exactly; difference is statistical discrepancy from imperfect data sources[^mankiw-ch10].

## Other income measures (largest to smallest)

Computed alongside GDP by the Department of Commerce's Bureau of Economic Analysis[^mankiw-ch10]:

- **Gross national product (GNP)** — total income earned by a nation's permanent residents (nationals) wherever located: includes citizens' income abroad, excludes foreigners' income domestically. GDP and GNP are quite close for the US[^mankiw-ch10].
- **Net national product (NNP)** — GNP minus depreciation (consumption of fixed capital — wear and tear such as trucks rusting, obsolete computers)[^mankiw-ch10].
- **National income** — total income earned by residents in production; almost identical to NNP, differing by statistical discrepancy[^mankiw-ch10].
- **Personal income** — income households and noncorporate businesses receive: excludes retained earnings, subtracts indirect business taxes, corporate income taxes, social-insurance contributions, and adds government debt interest and transfers (welfare, Social Security)[^mankiw-ch10].
- **Disposable personal income** — personal income minus personal taxes and certain nontax payments (e.g., traffic tickets)[^mankiw-ch10].

These measures usually move together; for monitoring fluctuations choice matters little[^mankiw-ch10].

### Open-economy wedge: the Kuwait example

GDP measures value added within a country's borders, whereas GNP measures value added by domestic factors. With $NI$ denoting net income received from the rest of the world, the source states $GNP = GDP + NI$.[^blanchard-kuwait-069] A country with net foreign assets can therefore have GNP materially above GDP without producing more at home: the asset income is foreign income accruing to domestic factors.[^blanchard-kuwait-069]

Kuwait illustrates this stock–income link. Its government saved and invested part of oil revenue abroad, accumulating foreign assets and the associated income for future generations. In 1989, its reported net income from abroad was 2,473 million Kuwaiti dinars—34% of GDP—so GNP (9,616 million dinars) substantially exceeded GDP (7,143 million dinars).[^blanchard-kuwait-069] Payments to allies during the 1990–1991 Gulf War and reconstruction were financed through a current-account deficit that reduced Kuwait's net foreign assets; reported net income then fell to 941 million dinars by 1994. The source says Kuwait subsequently rebuilt a sizable net foreign-asset position and that net income from abroad was 6% of GDP in 2018.[^blanchard-kuwait-069]

## 10-3 Components: Y = C + I + G + NX

Identity: each dollar of expenditure falls into one component, so sum must equal GDP[^mankiw-ch10].

- **Consumption (C)** — household spending on goods and services except new housing. Goods = durable (autos, appliances) and nondurable (food, clothing); services = intangible (haircuts, medical care, education)[^mankiw-ch10].
- **Investment (I)** — purchases of goods that will be used to produce more goods and services: business capital (structures, equipment, intellectual property products such as software), residential capital (landlord building + owner home — new house is investment not consumption), and inventories[^mankiw-ch10]. Note: GDP accounting restricts "investment" to capital goods, not financial stocks/bonds/mutual funds; Apple computer added to inventory counts as Apple's investment, later sale offsets with negative inventory investment[^mankiw-ch10].
- **Government purchases (G)** — spending on goods and services by local/state/federal governments (salaries of generals/teachers, public works), formally "government consumption expenditure and gross investment"[^mankiw-ch10]. Excludes transfer payments (Social Security, unemployment insurance) because not exchanged for currently produced good/service — they alter household income like negative taxes[^mankiw-ch10].
- **Net exports (NX)** — exports (foreign purchases of domestic goods) minus imports (domestic purchases of foreign goods). Subtraction corrects that imports are already included in C/I/G (e.g., $40,000 Volvo raises C by $40k but reduces NX by $40k, leaving GDP unchanged)[^mankiw-ch10].

### US composition 2015

Total GDP ~$18 trillion; population 321m → $55,882 per person[^mankiw-ch10].

|  | Total (bn) | Per person | % |
|---|---|---|---|
| GDP (Y) | $17,938 | $55,882 | 100% |
| Consumption (C) | $12,268 | $38,218 | 68% |
| Investment (I) | $3,018 | $9,402 | 17% |
| Government purchases (G) | $3,184 | $9,919 | 18% |
| Net exports (NX) | -$532 | -$1,657 | -3% |

Largest component is consumption[^mankiw-ch10]. Source: Bureau of Economic Analysis, bea.gov; rounding explains non-additivity[^mankiw-ch10].

### Scope note — sex, drugs and GDP

Eurostat and UN 2008 push to include prostitution and illicit drugs to make GDP comparable across legal regimes (Netherlands already counts legal prostitution/marijuana) and avoid incomplete picture; UK Office for National Statistics 2014 detailed methodology adding ~£10bn, Spain/Italy/Belgium also moved[^mankiw-ch10]. France declined, arguing non-consensual/non-voluntary activities (mafia-controlled street prostitution, addictive drugs) should not count, placing moral vision ahead of measurement; critique replies this makes GDP less useful — why exclude coal, cigarettes? — and US already counts legal Nevada prostitution and marijuana in Colorado/California/Washington as measurable commercial exchanges[^mankiw-ch10].

## 10-4 Real versus nominal GDP and the GDP deflator

Rise in total spending from year to year reflects either larger output or higher prices; real GDP separates them by valuing current quantities at prices from a fixed base year[^mankiw-ch10].

- **Nominal GDP** — production valued at current prices[^mankiw-ch10].
- **Real GDP** — production valued at constant base-year prices[^mankiw-ch10]. Base-year real GDP = nominal GDP; changes reflect quantities only; better gauge of production capacity and well-being; economists mean real GDP when they say GDP, and growth is percent change in real GDP[^mankiw-ch10].

#### Numerical example (hot dogs and hamburgers only)

| Year | Price hot dog | Q hot dog | Price hamburger | Q hamburger |
|---|---|---|---|---|
| 2016 | $1 | 100 | $2 | 50 |
| 2017 | $2 | 150 | $3 | 100 |
| 2018 | $3 | 200 | $4 | 150 |

Nominal: 2016 ($1×100+$2×50)=$200; 2017 ($2×150+$3×100)=$600; 2018 ($3×200+$4×150)=$1,200[^mankiw-ch10].

Real (base 2016 prices): 2016 $200; 2017 ($1×150+$2×100)=$350; 2018 ($1×200+$2×150)=$500[^mankiw-ch10]. Increase 200→350→500 is quantity only, with prices held fixed[^mankiw-ch10].

- **GDP deflator** = (Nominal GDP / Real GDP) ×100 — measures price level relative to base year; base year always 100[^mankiw-ch10]. Example: 2016 200/200×100=100; 2017 600/350×100=171; 2018 1200/500×100=240[^mankiw-ch10]. Deflates nominal GDP for price rise[^mankiw-ch10].
- **Inflation rate** between years = (Deflator year2 − Deflator year1)/Deflator year1 ×100. 2017: (171−100)/100×100=71%; 2018: (240−171)/171×100≈40%[^mankiw-ch10].
- GDP deflator vs. consumer price index (CPI) preview — alternative price measure examined next chapter[^mankiw-ch10].

### Base-year choice and chain-linking

A fixed base year is a useful explanation of real GDP but can give slightly different growth rates depending on whether an early or late year's prices are used: Krugman and Wells' two-good example yields 15% growth at the early prices versus 15.4% at the late prices. Neither is uniquely correct; the source describes the U.S. national accounts as **chain-linking** — averaging growth rates calculated with early and late base-year prices — and reporting real GDP in chained dollars.[^krugman-ch7-041]

### Half century of real GDP

Quarterly US real GDP since 1965: most obvious feature is growth — 2015 level >4× 1965, ~3% average annual growth enabling higher prosperity than parents/grandparents; growth not steady, interrupted by recessions (shaded bars, old rule-of-thumb two consecutive quarters of falling real GDP) associated with lower incomes, rising unemployment, falling profits, bankruptcies; macro models separate long-run growth from short-run fluctuations[^mankiw-ch10].

## Worked accounting applications

The source's Micronia and Macronia circular-flow exercises make the accounting identities operational. In Micronia, $C=650$, $G=100$, and $X=IM=20$, so $GDP=750$; the $750$ of factor income less $100$ in taxes equals $650$ disposable income and equals consumer spending. In Macronia, $C=510$, $I=110$, $G=150$, and $NX=50-20=30$, so $GDP=800$; $800-100+10=710$ disposable income, which funds $510$ consumption and $200$ private saving.[^krugman-ch7-043]

The supplied 2018 BEA component table yields $C=13{,}998.2$ billion, $I=3{,}628.3$ billion, $G=3{,}591.5$ billion, and $NX=-638.2$ billion, for GDP of $20{,}579.8$ billion (rounding to $20{,}580$ billion).[^krugman-ch7-043] Its Pizzania exercises likewise give the same GDP by each accounting route: when bread and cheese are inputs only, final-pizza spending, total value added, and factor income each equal $200$; when consumers also buy final bread and cheese, all three equal $275$.[^krugman-ch7-043]

The source also applies the final-output rule: a new domestic bottling plant and books newly added to inventories are investment and count in GDP; a U.S.-produced wine export counts; an existing airplane resale and existing stock sale do not. An imported perfume purchase can enter consumption but is offset by imports in $NX$, so it does not add to U.S. GDP.[^krugman-ch7-043]

## QuickQuiz answers

- Two things GDP measures: total income and total expenditure; measures both because transaction gives equal spending by buyer and income to seller[^mankiw-ch10].
- Caviar contributes more than hamburger if price higher — contributes at market-value, proportional to willingness to pay[^mankiw-ch10].
- Four components and largest: C, I, G, NX; consumption is largest[^mankiw-ch10].

## Coverage limits

Mankiw source images (circular-flow Figure 1, real-GDP Figure 2, table screenshots) were not inspected; its content derives from extracted OCR text. For Krugman source 041, the components-of-GDP and GDP-per-capita/life-satisfaction figures were visually inspected; the source ends at the introduction to price indexes and does not cover CPI construction.

## Relationships

- Depends on: [National income accounting and GDP as market-value output](national-income-accounting-and-gdp.md)
- Depends on: [Thinking Like an Economist — Scientific Method, Economic Models, and Positive vs Normative Analysis](thinking-like-an-economist-mankiw.md) — circular-flow diagram
- Uses: [The Market Forces of Supply and Demand — Competitive Markets, Demand and Supply, and Equilibrium](market-forces-of-supply-and-demand.md)
- Contrasts with: [GDP limitations and alternative welfare measures](gdp-limitations-and-welfare.md)
- Contrasts with: [Critique of the GDP cult and alternative indexes](critique-of-gdp-cult-and-alternative-indexes.md)
- See also: [GDP as well-being measure and productivity mismeasurement — Silicon Valley critique](gdp-well-being-and-productivity-mismeasurement.md) — Mankiw 10-5 extensions and Table 3
- See also: [Business cycle, recession, and Japan's lost growth](business-cycle-recession-and-japan.md)

[^mankiw-ch10]: Mankiw, *Principles of Macroeconomics* 8th ed., ch. 10 — The Data of Macroeconomics (034).
[^krugman-ch7-040]: Krugman and Wells, *Macroeconomics*, 6th ed., ch. 7, “GDP and the CPI: Tracking the Macroeconomy” (040). The expanded circular-flow and GDP-calculation figures were visually inspected.
[^krugman-ch7-041]: Krugman and Wells, *Macroeconomics*, 6th ed., ch. 7, “GDP and the CPI: Tracking the Macroeconomy — Pitfalls” (041).
[^krugman-ch7-043]: Krugman and Wells, *Macroeconomics*, 6th ed., ch. 7, “GDP and the CPI: Tracking the Macroeconomy — Practice questions” (043). Circular-flow diagrams for Micronia and Macronia were visually inspected.
[^krugman-ch10-053]: Krugman and Wells, *Macroeconomics*, 6th ed., Ch. 10, “Savings, Investment Spending, and the Financial System” (raw/Macroeconomics_Krugman/053-chapter-10-savings-investment-spending-and-the-financial-system.md).
[^blanchard-kuwait-069]: Blanchard, *Macroeconomics*, Ch. 17 focus box, “GDP versus GNP: The Example of Kuwait” (raw/Macroeconomics_OlivierBlanchard/069-gdp-versus-gnp-the-example-of-kuwait.md; focus-box image inspected and is decorative).
