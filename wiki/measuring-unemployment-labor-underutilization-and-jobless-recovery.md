---
type: Concept
title: Measuring unemployment, labor underutilization, and jobless recovery
description: How the official unemployment rate is constructed and interpreted, what broader measures add, how it varies across groups, and why growth can resume while unemployment still rises.
tags: [unemployment, labor-force, labor-force-participation, underemployment, discouraged-workers, jobless-recovery, economic-growth]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T21:06:00Z }
sources:
  - id: krugman-ch8-044
    resource: ../raw/Macroeconomics_Krugman/044-chapter-8-unemployment-and-inflation.md
    title: "Chapter 8 Unemployment and Inflation (Krugman/Wells)"
  - id: blanchard-023
    resource: ../raw/Macroeconomics_OlivierBlanchard/023-the-current-population-survey.md
    title: "The Current Population Survey (Blanchard)"
---

# Measuring unemployment, labor underutilization, and jobless recovery

The official unemployment rate is a useful indicator of overall labor-market conditions, not a literal count of everyone who wants more work: it excludes people who have stopped looking and people involuntarily working part time, while counting some workers in ordinary short-term job search.[^krugman-ch8-044] U.S. data in the source also show a strong inverse relationship between real-GDP growth and changes in unemployment, but positive growth below its usual pace can still leave unemployment rising — a jobless recovery.[^krugman-ch8-044]

## Definitions and construction

- **Employment** counts people currently working, full or part time. **Unemployment** counts people without a job who have actively sought one in the previous four weeks; retirement and inability to work do not qualify.[^krugman-ch8-044]
- The **labor force** is employment plus unemployment. The **labor-force participation rate** is $\frac{\text{labor force}}{\text{population age 16 and older}} \times 100$; the **unemployment rate** is $\frac{\text{unemployed workers}}{\text{labor force}} \times 100$.[^krugman-ch8-044]
- The source describes the monthly U.S. Current Population Survey as interviewing a random sample of about 60,000 households, then scaling responses using population estimates.[^krugman-ch8-044] Blanchard adds that sampled households are interviewed for four consecutive months, out for eight, then interviewed for four more, allowing consecutive-month matches to estimate transition probabilities as well as cross-sectional snapshots.[^blanchard-023]

## Why the headline rate is incomplete

The rate can **overstate** job-finding difficulty because even a confident job seeker is counted as unemployed until accepting a position, so the rate remains above zero when jobs are plentiful.[^krugman-ch8-044]

It can **understate** unmet demand for work because it excludes:

- **Discouraged workers:** able nonworkers who have stopped looking because they see little prospect of finding work.
- **Marginally attached workers:** people who want work and looked recently, but are not currently searching.
- **Underemployed workers:** people working part time for economic reasons because they cannot find full-time work.[^krugman-ch8-044]

The source reports that the Bureau of Labor Statistics' broadest measure, **U-6**, combines unemployed, discouraged, other marginally attached, and involuntary part-time workers. It is much higher in level than the headline rate but has moved closely in parallel with it in the 1996–2020 series.[^krugman-ch8-044]

## Distribution matters

A low aggregate rate can coexist with much worse conditions for particular groups. In the source's February 2020 comparison, overall unemployment was 3.5%, versus 5.8% for African-American workers, 9.5% for White teenagers, and 20.4% for African-American teenagers.[^krugman-ch8-044] The source also shows consistently higher unemployment for adults over 25 with only high-school credentials than for college graduates in 2007–2020, with the gap especially large in the weak 2010 labor market and substantially narrower by 2019.[^krugman-ch8-044]

## Growth, recessions, and jobless recoveries

In the source's U.S. data, unemployment rose in every recession shown from 1979 to 2020 and usually fell during expansions; it nevertheless kept rising for more than a year after the 1990–1991 and 2001 recessions had officially ended.[^krugman-ch8-044] For 1949–2019, unemployment generally fell in years with above-average real-GDP growth (3.17% annually in that sample) and rose with below-average growth; it rose in every year in which real GDP fell.[^krugman-ch8-044]

A **jobless recovery** (or growth recession) is positive real-GDP growth while unemployment is still rising. It follows when growth is insufficient to reduce unemployment, so an end to a recession should not be treated as proof that labor-market conditions have recovered.[^krugman-ch8-044]

## Relationships

- Related to: [Costs of unemployment and recessions](costs-of-unemployment-and-recessions.md) — why the indicator and persistent joblessness matter to households and society.
- Related to: [Business cycle, recession, and Japan's lost growth](business-cycle-recession-and-japan.md) — recession dating and the distinction between cyclical fluctuation and long-run growth.
- Related to: [Beveridge curve and structural versus cyclical unemployment](beveridge-curve-structural-vs-cyclical-unemployment.md) — vacancies help distinguish cyclical movement from structural unemployment.
- Related to: [Natural rate of unemployment — frictional, structural, and cyclical components](natural-rate-of-unemployment-frictional-structural-and-cyclical.md) — active job search determines inclusion in the official measure, while short search spells contribute to the natural rate.
- Related to: [Labor-market flows, participation, and unemployment dynamics](labor-market-flows-participation-and-unemployment-dynamics.md) — CPS longitudinal matching exposes the transitions hidden by headline stocks.
- Uses: [GDP — income-expenditure identity, measurement rules, components, and real versus nominal](gdp-income-expenditure-measurement-and-real-vs-nominal.md) — real GDP is the growth measure used in the jobless-recovery relationship.

## Coverage limits

This raw file covers the chapter introduction and sections through the first quick review (unemployment measurement and growth); it does not include the chapter's later treatment of the natural unemployment rate or inflation. The six referenced figures (8-1 through 8-6) were inspected; their plotted patterns support the stated comparisons.[^krugman-ch8-044]

[^krugman-ch8-044]: Krugman and Wells, *Macroeconomics*, Ch. 8, “Unemployment and Inflation” (raw/Macroeconomics_Krugman/044-chapter-8-unemployment-and-inflation.md).
[^blanchard-023]: Blanchard, *Macroeconomics*, “The Current Population Survey” (raw/Macroeconomics_OlivierBlanchard/023-the-current-population-survey.md).