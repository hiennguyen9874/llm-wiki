---
type: Concept
title: Measuring the Cost of Living — CPI, Inflation, and Biases
description: How the CPI measures the cost of the typical consumer's basket, how inflation is derived from it, what's in the basket, and three measurement biases that cause overstatement.
tags: [cpi, inflation, cost-of-living, price-index, bls, gdp-deflator, substitution-bias, new-goods, quality-change]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T14:30:00Z }
sources:
  - id: mankiw-ch11
    resource: ../raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/037-measuring-the-cost-of-living.md
    title: "Measuring the Cost of Living — Principles of Macroeconomics 8th ed., ch. 11"
  - id: mankiw-038
    resource: ../raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/038-in-the-news.md
    title: "Ch.11 11-1c–11-3 and In the News — Principles of Macroeconomics 8th ed."
---

# Measuring the Cost of Living — CPI, Inflation, and Biases

The consumer price index (CPI) measures the overall cost of goods and services bought by a typical consumer by pricing a fixed basket over time; the percentage change in that index is the CPI inflation rate used on the evening news, distinct from the GDP deflator, and it systematically overstates true cost-of-living increases because of substitution bias, new goods, and unmeasured quality change[^mankiw-ch11].

## 11-0 Motivation — why a price index is needed

- In 1931 Babe Ruth earned $80,000, more than President Hoover's $75,000 — reporter asked if it was right, Ruth replied "I had a better year"[^mankiw-ch11].
- By 2015 average major-league salary was ~$4 million, Clayton Kershaw $31 million, but a nickel then bought an ice-cream cone and a quarter a movie ticket, so nominal dollars are not comparable[^mankiw-ch11].
- Preceding chapter measured quantity via GDP; this chapter measures cost of living via CPI to convert dollar figures into purchasing power[^mankiw-ch11].
- When CPI rises, the typical family needs more money to maintain the same standard of living[^mankiw-ch11].
- **Inflation** — situation where economy's overall price level is rising; **inflation rate** — percentage change in price index from previous period[^mankiw-ch11]. GDP deflator measures inflation from all goods produced; CPI — more relevant to consumers — is what the nightly news reports[^mankiw-ch11]. As a background for later macro policy, inflation is a closely watched performance and policy variable[^mankiw-ch11].

## 11-1 The Consumer Price Index

**Consumer price index (CPI)** — a measure of the overall cost of the goods and services bought by a typical consumer[^mankiw-ch11].

Computed and reported monthly by the Bureau of Labor Statistics (BLS), part of the Department of Labor, from thousands of goods and services[^mankiw-ch11].

Also reported: narrow category indexes (food, clothing, energy), **core CPI** (all goods and services excluding food and energy — less volatile, better reflects ongoing trend), and **producer price index (PPI)** — cost of basket bought by firms rather than consumers; PPI changes often predict CPI changes because firms pass costs on[^mankiw-ch11].

> **core CPI** — a measure of the overall cost of consumer goods and services excluding food and energy[^mankiw-ch11].
> **producer price index** — a measure of the cost of a basket of goods and services bought by firms[^mankiw-ch11].

### 11-1a How the CPI is calculated — five steps

Illustrated with a two-good economy where the typical consumer buys 4 hot dogs and 2 hamburgers[^mankiw-ch11]:

| Year | Price hot dogs | Price hamburgers |
|------|---------------|-----------------|
| 2016 | $1 | $2 |
| 2017 | $2 | $3 |
| 2018 | $3 | $4 |

1. **Fix the basket.** Survey consumers to find what the typical consumer buys. Weights reflect importance — more hot dogs than hamburgers means hot-dog price matters more. Example basket = 4 hot dogs + 2 hamburgers[^mankiw-ch11].
2. **Find the prices.** Collect price of each item at each point in time[^mankiw-ch11].
3. **Compute the basket's cost.** Multiply quantities by prices; only prices change, basket is held fixed to isolate price effects. 2016: ($1×4)+($2×2)=$8; 2017: ($2×4)+($3×2)=$14; 2018: ($3×4)+($4×2)=$20[^mankiw-ch11].
4. **Choose a base year and compute the index.**

   $$\text{CPI} = \frac{\text{Price of basket in current year}}{\text{Price of basket in base year}} \times 100$$[^mankiw-ch11]

   Choice of base year is arbitrary — percentage changes are the same. Example base = 2016 ($8): 2016 8/8×100=100 (always 100 in base year); 2017 14/8×100=175 (basket costs 175% of base — $100 basket then costs $175 now); 2018 20/8×100=250[^mankiw-ch11].
5. **Compute the inflation rate.**

   $$\text{Inflation rate in year 2} = \frac{\text{CPI in year 2} - \text{CPI in year 1}}{\text{CPI in year 1}} \times 100$$[^mankiw-ch11]

   Example: 2017 (175−100)/100×100=75%; 2018 (250−175)/175×100≈43%[^mankiw-ch11].

The BLS follows these steps monthly on thousands of items; the monthly CPI announcement appears on TV news and newspapers[^mankiw-ch11].

### What's in the CPI's basket? (Figure 1)

BLS weights by consumer spending — "relative importance"[^mankiw-ch11]:

- **Housing 42%** — shelter 33%, fuel and utilities 5%, household furnishings and operation 4% — by far the largest[^mankiw-ch11].
- **Transportation 16%** — cars, gasoline, buses, subways[^mankiw-ch11].
- **Food and beverages 15%** — food at home 8%, food away from home 6%, alcoholic beverages 1%[^mankiw-ch11].
- **Medical care 8%**[^mankiw-ch11].
- **Education and communication 7%**[^mankiw-ch11].
- **Recreation 6%**[^mankiw-ch11].
- **Apparel 3%** — clothing, footwear, jewelry[^mankiw-ch11].
- **Other goods and services 3%** — catchall (cigarettes, haircuts, funeral expenses)[^mankiw-ch11].

*Source: Bureau of Labor Statistics, as reproduced in Mankiw Figure 1*[^mankiw-ch11].

## 11-1b Problems in measuring the cost of living

Goal: gauge how much incomes must rise to maintain constant standard of living. Three widely acknowledged, hard-to-solve problems cause CPI to overstate increase[^mankiw-ch11]:

### 1. Substitution bias

Prices do not all rise proportionately. Consumers substitute toward goods that have become relatively less expensive — buying less of goods with large price rises, more of those with smaller rises or falls[^mankiw-ch11]. A fixed-basket index ignores substitution and overstates cost-of-living increase[^mankiw-ch11].

> Example: base year apples cheaper than pears → consumers buy more apples → basket weights more apples. Next year pears become cheaper, consumers switch to pears, but CPI still assumes same apple-heavy quantities, measuring a larger increase than actually experienced[^mankiw-ch11].

### 2. Introduction of new goods

New variety reduces cost of maintaining well-being — each dollar becomes more valuable because choices expand[^mankiw-ch11].

> Thought experiment: $100 gift certificate at a large store with wide array vs. small store with same prices but limited selection — most prefer the large store; the larger choice set makes dollars more valuable[^mankiw-ch11].

CPI's fixed basket does not reflect the fall in cost of living when a new good appears. Example: iPod introduced 2001 gave more portable, versatile music listening than prior devices; for any dollar amount people were better off, achieving same well-being required fewer dollars — a perfect index would fall, but CPI did not. Eventually BLS added iPod and tracked its price, but the initial welfare gain never entered the index[^mankiw-ch11].

### 3. Unmeasured quality change

If quality deteriorates while price stays same, dollar's value falls (lesser good for same money); if quality rises, dollar's value rises[^mankiw-ch11]. BLS tries to adjust — e.g., car model with more horsepower or better gas mileage — by adjusting price to account for quality change, in essence trying to price a constant-quality basket. Difficult to measure, so some quality improvement is missed and some deterioration overstated[^mankiw-ch11]. *Note: source text truncated mid-sentence at this point; full BLS hedonic-adjustment discussion not available for ingestion.*

Collectively these biases mean the CPI overstates inflation; the magnitude is debated and relevant to indexing Social Security, tax brackets, and real-wage calculations.

## Relationship to GDP deflator

- Both measure price level and inflation, but GDP deflator reflects prices of all domestically produced final goods and services, while CPI reflects prices of goods and services bought by consumers (including imports)[^mankiw-ch11].
- Detailed comparison of scope (domestic production vs consumer basket including imports) and weighting (currently produced bundle vs fixed basket), with Boeing/Air Force, Volvo, and oil-doubling 1979–80 divergence, is maintained in [GDP Deflator versus CPI — Scope and Weighting Differences](gdp-deflator-vs-cpi-scope-and-weighting.md)[^mankiw-038].
- BLS bias magnitude update: 1990s studies found CPI overstated inflation by ~1 pp per year; after BLS technical changes bias now about half as large; matters because Social Security tie to CPI[^mankiw-038].

## Coverage limits

- Images `image-000236.jpg`, `image-000237.jpg` (Figure 1 basket breakdown pie chart), and `image-000238.jpg` not inspected; basket percentages taken from OCR text[^mankiw-ch11].
- Source file `037-measuring-the-cost-of-living.md` (113 lines, 16,379 bytes) truncates mid-sentence in the quality-change discussion at "It is, in essence,"; sections beyond 11-1b were supplemented from `038-in-the-news.md` for the GDP deflator comparison and subsequent chapters[^mankiw-038].
- `038-in-the-news.md` images `image-000239.jpg`–`image-000249.jpg` not inspected; Figure 2 (1979–80 oil divergence) and Figure 3 (regional parities) described from OCR text[^mankiw-038].

## Relationships

- Depends on: [GDP — income-expenditure identity, measurement rules, components, and real versus nominal](gdp-income-expenditure-measurement-and-real-vs-nominal.md) — GDP deflator and real vs nominal distinction; CPI is alternative price index
- Contrasts with: [GDP Deflator versus CPI — Scope and Weighting Differences](gdp-deflator-vs-cpi-scope-and-weighting.md) — domestic production vs consumer basket; fixed vs currently-produced weighting
- Uses: [Inflation targeting and the case for higher inflation (2% vs 3–4% and NGDP)](inflation-targeting-optimal-inflation-and-ngdp.md) — CPI inflation is the news-reported measure central banks target
- Uses: [Deflation, the zero lower bound, and liquidity traps](deflation-zero-lower-bound-and-liquidity-trap.md) — CPI falling = deflation
- See also: [Monitoring Inflation in the Internet Age — Billion Prices Project and Google Price Index](monitoring-inflation-in-the-internet-age-bpp-and-google-price-index.md) — daily web-scraped alternatives to BLS clipboard CPI
- See also: [Correcting Economic Variables for Inflation — Dollar Conversions, Regional Parities, Indexation, and Real vs Nominal Interest Rates](correcting-for-inflation-real-vs-nominal-indexation-and-regional-parities.md) — applying CPI to compare dollars across time/space and to compute real rates
- See also: [GDP as well-being measure and productivity mismeasurement — Silicon Valley critique](gdp-well-being-and-productivity-mismeasurement.md) — quality-change mismeasurement parallel
- See also: [GDP limitations and alternative welfare measures](gdp-limitations-and-welfare.md)

[^mankiw-ch11]: Mankiw, *Principles of Macroeconomics* 8th ed., ch. 11 — Measuring the Cost of Living (037).
