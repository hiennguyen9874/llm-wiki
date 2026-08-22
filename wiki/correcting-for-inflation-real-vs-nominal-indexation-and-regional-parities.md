---
type: Concept
title: Correcting Economic Variables for Inflation — Dollar Conversions, Regional Parities, Indexation, and Real vs Nominal Interest Rates
description: How to compare dollar figures across time, why indexation automates it, how regional price parities adjust across space, and how the inflation correction yields real vs nominal interest rates.
tags: [inflation-correction, real-vs-nominal, indexation, interest-rates, regional-price-parities, cpi, purchasing-power]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T11:07:45Z }
sources:
  - id: krugman-ch10-055
    resource: ../raw/Macroeconomics_Krugman/055-chapter-10-savings-investment-spending-and-the-financial-system-inflat.md
    title: "Chapter 10 Savings, Investment Spending, and the Financial System — Inflation and Interest Rates (Krugman/Wells)"
  - id: mankiw-038-correction
    resource: ../raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/038-in-the-news.md
    title: "Ch.11 11-2–11-3 Correcting Economic Variables for the Effects of Inflation — Principles of Macroeconomics 8th ed."
  - id: krugman-ch6-038
    resource: ../raw/Macroeconomics_Krugman/038-chapter-6-macroeconomics-the-big-picture-inflation-and-deflation.md
    title: "Chapter 6 Macroeconomics: The Big Picture — Inflation and Deflation (Krugman/Wells)"
  - id: krugman-ch7-042
    resource: ../raw/Macroeconomics_Krugman/042-chapter-7-gdp-and-the-cpi-tracking-the-macroeconomy-market-baskets-and.md
    title: "Chapter 7 GDP and the CPI: Tracking the Macroeconomy — Market Baskets and Price Indexes"
---

# Correcting Economic Variables for Inflation — Dollar Conversions, Regional Parities, Indexation, and Real vs Nominal Interest Rates

A price index lets us turn dollars from different years into comparable purchasing power; the same logic extends to geography (regional price parities), to law and contracts (indexation), and to intertemporal returns, where subtracting inflation from the nominal interest rate yields the real interest rate that measures growth in purchasing power[^mankiw-038-correction].

## Wage growth is not purchasing-power growth

Krugman and Wells illustrate the distinction with U.S. production-worker hourly earnings: $6.57 in January 1980 and $23.88 in January 2020, a 263% nominal increase. Over the same period, the source reports a 232% rise in the overall cost of living, so the typical worker's real living standard rose only slightly. Its category data also show that relative prices can move quite differently: medical care rose 617%, housing 254%, and food 213%.[^krugman-ch6-038]

This is a historical illustration based on the source's cited BLS data, not a general claim that every worker or spending basket experienced the same real-wage change.[^krugman-ch6-038]

The source's hamburger comparison makes the same relative-price point: a McDonald's hamburger rose from $0.15 in 1948 to about $1.00 in 2020 (about 6.5 times), while its reported CPI measure rose about 11 times. The burger was therefore cheaper relative to the consumer basket even though its dollar price was higher.[^krugman-ch6-038]

## 11-2a Dollar figures from different times

Purpose of measuring overall price level is to compare dollar figures from different times[^mankiw-038-correction].

Formula to turn year T dollars into today's dollars:

$$\text{Amount in today's dollars} = \text{Amount in year }T\text{ dollars} \times \frac{\text{Price level today}}{\text{Price level in year }T}$$[^mankiw-038-correction]

A price index such as CPI measures the price level and determines size of inflation correction[^mankiw-038-correction].

Worked examples (CPI 15.2 in 1931, 237 in 2015; ratio 237/15.2 = 15.6):

- Babe Ruth $80,000 in 1931 → $80,000 × 237/15.2 = **$1,247,368** in 2015 dollars — a good income but only ~one-third of average player's salary today and ~4% of Dodgers' Clayton Kershaw pay; overall economic growth and superstar income shares have raised athletes' living standards[^mankiw-038-correction].
- President Hoover $75,000 in 1931 → $75,000 × 237/15.2 = **$1,169,408** in 2015 dollars — well above President Obama's $400,000; "Hoover did have a pretty good year after all"[^mankiw-038-correction].
- QuickQuiz: Henry Ford $5/day in 1914, CPI 10 in 1914 and 237 in 2015 → $5 × 237/10 = **$118.50** in 2015 dollars per day (text poses as exercise)[^mankiw-038-correction].

Other illustrations:

- **Mr. Index Goes to Hollywood:** nominal top domestic receipts Star Wars: The Force Awakens $923m, Avatar $761m, Titanic $659m; inflation-corrected (same formula) Gone with the Wind $1,758m, original Star Wars $1,550m, Sound of Music $1,239m, Force Awakens falls to #11; 1930s 90m Americans/week went to cinema vs ~25m today, but ticket was $0.25, so newer films advantaged in nominal ranking[^mankiw-038-correction].
- Candy-bar example (Review Q4): price $0.20→$1.20 while CPI 150→300 (price level doubled); real price change = ($1.20/(300/150)) vs $0.20 — in base-year dollars $0.60 vs $0.20, tripling in real terms[^mankiw-038-correction].

## Regional variation — price levels across space

Cost of living varies not only over time but also geography; larger paycheck may not help after regional prices, especially housing[^mankiw-038-correction].

- Bureau of Economic Analysis uses CPI-collected data to compute **regional price parities** — variation from state to state, analogous to CPI's variation year to year[^mankiw-038-correction].
- Figure 3, 2013 data: New York = 115.3% of U.S. average (15.3% more expensive); Mississippi = 86.8% (13.2% less expensive)[^mankiw-038-correction].
- Why: tradable goods (food, clothing) easily transported — large disparities don't persist; services explain larger part — haircut cost dispersion persists because transporting haircuts is costly (barbers/customers won't fly cross-country); housing services most important — large share of budget, immobile land/structures, so rents in New York almost twice Mississippi's[^mankiw-038-correction].
- Practical tip: compare job offers on local prices of goods/services, especially housing, not just dollar salaries[^mankiw-038-correction].

## 11-2b Indexation

When some dollar amount is automatically corrected for price-level changes by law or contract, it is said to be **indexed for inflation**[^mankiw-038-correction].

> **indexation** — the automatic correction by law or contract of a dollar amount for the effects of inflation[^mankiw-038-correction].

- Private contracts: long-term firm-union contracts include partial/complete indexation to CPI via **cost-of-living allowance (COLA)** automatically raising wage when CPI rises[^mankiw-038-correction].
- Laws: Social Security benefits adjusted every year to compensate elderly for price increases; federal income-tax brackets (income levels where rates change) are indexed for inflation[^mankiw-038-correction].
- Many tax-system parts are **not** indexed when perhaps they should be — discussed more fully when covering costs of inflation later in book[^mankiw-038-correction].
- Krugman/Wells likewise identifies CPI-linked Social Security and disability payments, income-tax brackets, and some private wage contracts with COLAs. Its reported recipient and spending figures are source-period-specific and are not retained as current statistics.[^krugman-ch7-042]

## 11-2c Real and nominal interest rates

Concept involves comparing money at different points in time; deposit $1,000 now vs $1,100 later with interest — understanding requires correcting for inflation[^mankiw-038-correction].

Sally Saver example: deposits $1,000 at 10% nominal → $1,100 a year later; buys only DVDs at $10 each initially (=100 DVDs purchasing power)[^mankiw-038-correction]:

- Zero inflation ($10 stays $10): 110 DVDs → purchasing power +10%[^mankiw-038-correction].
- 6% inflation ($10→$10.60): ~104 DVDs → +~4%[^mankiw-038-correction].
- 10% inflation ($10→$11): 100 DVDs → 0%[ ^mankiw-038-correction].
- 12% inflation ($10→$11.20): ~98 DVDs → –2%[^mankiw-038-correction].
- 2% deflation ($10→$9.80): ~112 DVDs → +~12%[^mankiw-038-correction].

Higher inflation → smaller purchasing-power increase; if inflation exceeds interest rate, purchasing power actually falls; if deflation, it rises by more than interest rate[^mankiw-038-correction].

Definitions:

- **Nominal interest rate** — measures change in dollar amounts[^mankiw-038-correction].
- **Real interest rate** — corrected for inflation[^mankiw-038-correction].

Approximate Fisher relation:

$$\text{Real interest rate} = \text{Nominal interest rate} - \text{Inflation rate}$$[^mankiw-038-correction]

Loan contracts normally specify a nominal rate because future inflation is not known when parties agree. Accordingly, the relevant ex ante comparison is nominal interest less **expected** inflation; a higher-than-expected inflation outcome lowers the realized real rate, benefiting borrowers relative to lenders, and the reverse holds for lower-than-expected inflation.[^krugman-ch10-055]

Nominal tells how fast dollars in bank account rise; real tells how fast purchasing power rises[^mankiw-038-correction].

**U.S. data since 1965 (Figure 4):** nominal rate = three-month Treasury bill rate; real = nominal minus CPI inflation; nominal almost always exceeds real because consumer prices rose in almost every year; during late 19th-century U.S. or recent Japan deflation, real exceeds nominal[^mankiw-038-correction]. Because inflation is variable, real and nominal often do not move together: late 1970s nominal high but real low/negative (inflation eroded savings faster than interest); late 1990s nominal lower than two decades earlier but real higher because inflation much lower; upcoming chapters examine economic forces determining both[^mankiw-038-correction].

QuickQuiz tie-ins (same chapter summary):

- $600 in 1980 when CPI 200, CPI 300 today → $600 × 300/200 = $900 today[^mankiw-038-correction].
- Deposit $2,000 → $2,100 (5% nominal); CPI 200→204 (2% inflation) → nominal 5%, real ≈3%[^mankiw-038-correction].
- If borrower/lender agree on nominal rate and inflation turns out higher than expected, real rate is lower than expected; lender loses, borrower gains; 1970s higher-than-expected inflation benefited 1960s fixed-rate-mortgage homeowners at expense of banks[^mankiw-038-correction].

## 11-3 Conclusion framing

Yogi Berra: "A nickel ain't worth a dime anymore" — real values behind nickel/dime/dollar not stable; persistent price-level increases (inflation) reduce purchasing power of each unit over time; a dollar today is not same as dollar 20 years ago or hence[^mankiw-038-correction]. Discussion of price indexes together with preceding chapter's GDP measurement is first step; subsequent chapters develop models for long-run determinants of real GDP (saving, investment, real rates, unemployment) and of price level (money supply, inflation, nominal rates), then short-run fluctuations — measurement provides foundation[^mankiw-038-correction].

## Coverage limits

- Images `image-000243.jpg`, `image-000244.jpg`, `image-000245.jpg`, `image-000246.jpg`, `image-000247.jpg`, `image-000248.jpg`, `image-000249.jpg` not inspected[^mankiw-038-correction].
- Regional price parities figure from U.S. Department of Commerce, 2013 data[^mankiw-038-correction].
- Real vs nominal figure source: U.S. Department of Labor; U.S. Department of Treasury[^mankiw-038-correction].

## Relationships

- Depends on: [Measuring the Cost of Living — CPI, Inflation, and Biases](measuring-cost-of-living-cpi-inflation-and-biases.md) — CPI construction used as deflator
- Depends on: [GDP — income-expenditure identity, measurement rules, components, and real versus nominal](gdp-income-expenditure-measurement-and-real-vs-nominal.md) — price-level vs real-quantity distinction
- Uses: [Monitoring Inflation in the Internet Age — Billion Prices Project and Google Price Index](monitoring-inflation-in-the-internet-age-bpp-and-google-price-index.md) — frequency/accuracy of price-level measurement
- Uses: [Inflation targeting and the case for higher inflation (2% vs 3–4% and NGDP)](inflation-targeting-optimal-inflation-and-ngdp.md) — indexed policy parameters
- Uses: [Deflation, the zero lower bound, and liquidity traps](deflation-zero-lower-bound-and-liquidity-trap.md) — deflation raising real rate above nominal
- See also: [GDP Deflator versus CPI — Scope and Weighting Differences](gdp-deflator-vs-cpi-scope-and-weighting.md)

[^krugman-ch10-055]: Krugman and Wells, *Macroeconomics*, 6th ed., Ch. 10, “Savings, Investment Spending, and the Financial System — Inflation and Interest Rates” (raw/Macroeconomics_Krugman/055-chapter-10-savings-investment-spending-and-the-financial-system-inflat.md).
[^mankiw-038-correction]: Mankiw, *Principles of Macroeconomics* 8th ed., ch. 11 §§11-2–11-3, in 038-in-the-news.md.
[^krugman-ch6-038]: Krugman and Wells, *Macroeconomics*, Ch. 6, “Inflation and Deflation” (raw/Macroeconomics_Krugman/038-chapter-6-macroeconomics-the-big-picture-inflation-and-deflation.md; Figure 6-8 visually inspected).
[^krugman-ch7-042]: Krugman and Wells, *Macroeconomics*, 6th ed., ch. 7, “GDP and the CPI: Tracking the Macroeconomy — Market Baskets and Price Indexes” (042).
