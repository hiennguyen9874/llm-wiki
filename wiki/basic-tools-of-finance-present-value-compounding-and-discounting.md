---
type: Concept
title: The Basic Tools of Finance — Present Value, Future Value, Compounding, and Discounting
description: Mankiw Ch.14 14-1 — finance as allocation over time and risk, and how compounding, discounting, present value and the Rule of 70 link interest/growth rates to valuation of future sums and firm investment decisions.
tags: [finance, present-value, future-value, compounding, discounting, time-value-of-money, interest-rate, investment, loanable-funds, rule-of-70, mankiw]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T23:00:00Z }
sources:
  - id: mankiw-ch14-044
    resource: ../raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/044-the-basic-tools-of-finance.md
    title: "The Basic Tools of Finance (Mankiw 8th Ed. Ch.14, Part 44)"
  - id: mankiw-ch14-045
    resource: ../raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/045-the-magic-of-compounding-and-the-rule-of-70.md
    title: "The Magic of Compounding and the Rule of 70 (Mankiw 8th Ed. Ch.14, Part 45)"
---

# The Basic Tools of Finance — Present Value, Future Value, Compounding, and Discounting

Finance studies how people make decisions regarding the allocation of resources over time and the handling of risk — the two elements present in almost every financial decision (saving in a bank, borrowing for tuition or a house, choosing stocks vs bonds for retirement portfolios, interpreting market moves)[^mankiw-ch14-044]. The time value of money is captured by present value: the amount today that would be needed at prevailing interest rates to produce a given future sum, with future value computed via compounding and present value via discounting $PV = X/(1+r)^N$[^mankiw-ch14-044]. Small differences in growth or interest rates become large when compounded: at 1% incomes double in ~70 years, at 3% in ~23 years, so two graduates starting at \$30,000 differ after 40 years as \$45,000 vs \$98,000; \$5,000 at 7% doubles every 10 years to $2^{20}\times\$5{,}000\approx\$5$ billion after 200 years[^mankiw-ch14-045]. At 5% a future \$200 in 10 years has present value \$123 (prefer to \$100 today), but at 8% only \$93 (prefer \$100 today); the same logic explains why firm investment — and thus quantity of loanable funds demanded — declines as the interest rate rises, and why a \$1M lottery paid as \$20k×50 in present value at 7% is only \$276,000 and inferior to \$400,000 cash[^mankiw-ch14-044][^mankiw-ch14-045].

## Finance — field definition

**finance:** the field that studies how people make decisions regarding the allocation of resources over time and the handling of risk[^mankiw-ch14-044].

- Financial system coordinates saving and investment (preceding two chapters), which are crucial determinants of economic growth, but all saving/investment decisions are made today based on guesses about an unknown future — actual results may differ from expected[^mankiw-ch14-044].
- Common life-cycle examples: depositing savings, taking student or mortgage loans, employer retirement accounts with stock/bond choices (e.g., General Electric vs Twitter), media reports of market ups/downs[^mankiw-ch14-044].
- This chapter's three topics: (1) comparing sums at different points in time, (2) managing risk, (3) determining asset value such as a share of stock by combining time and risk[^mankiw-ch14-044].

## 14-1 Present Value: Measuring the Time Value of Money

Core intuition: \$100 today is more valuable than \$100 in 10 years because it can be deposited and earn interest along the way — money today is more valuable than the same amount in the future[^mankiw-ch14-044].

### Key definitions

- **present value:** the amount of money today that would be needed, using prevailing interest rates, to produce a given future amount of money[^mankiw-ch14-044].
- **future value:** the amount of money in the future that an amount of money today will yield, given prevailing interest rates[^mankiw-ch14-044].
- **compounding:** the accumulation of a sum of money in, say, a bank account, where the interest earned remains in the account to earn additional interest in the future[^mankiw-ch14-044].

### Formulas — compounding and discounting

Let $r$ be interest rate in decimal form (5% → $r=0.05$), interest paid annually and left to compound[^mankiw-ch14-044]:

- Future value of \$100 in $N$ years:

$$FV = (1+r)^N \times \$100$$

After 1 year $(1+r)\times 100$, after 2 years $(1+r)^2 \times 100$, after 3 years $(1+r)^3 \times 100$ … after $N$ years $(1+r)^N \times 100$[^mankiw-ch14-044].
Example: 5% for 10 years → $(1.05)^{10} \times 100 = \$163$[^mankiw-ch14-044].

- Present value of amount $X$ to be received in $N$ years:

$$PV = X / (1+r)^N$$[^mankiw-ch14-044]

Derivation: invert the compounding factor — divide by $(1+r)^N$ rather than multiply; e.g., present value of \$200 in $N$ years is $\$200/(1+r)^N$; deposited today it becomes $(1+r)^N \times [\$200/(1+r)^N] = \$200$[^mankiw-ch14-044].
Example: \$200 in 10 years at 5% → $\$200/(1.05)^{10} = \$123$; \$123 today at 5% yields \$200 after 10 years[^mankiw-ch14-044].

- **discounting:** the process of finding a present value of a future sum; because earning interest is possible, present value is below $X$ — future sums are discounted by the factor $(1+r)^N$[^mankiw-ch14-044].

### Choice example — \$100 today vs \$200 in 10 years

- At $r=5\%$: $PV$ of \$200 = \$123 > \$100 → prefer waiting for \$200[^mankiw-ch14-044].
- At $r=8\%$: $PV$ of \$200 = $\$200/(1.08)^{10} = \$93$ < \$100 → prefer \$100 today[^mankiw-ch14-044].
- Lesson: the higher the interest rate, the more can be earned by depositing money in a bank, so getting money today becomes more attractive[^mankiw-ch14-044].

### Application 1 — Firm investment decision

General Motors considering a \$100M factory today yielding \$200M in 10 years — compare present value of return to cost[^mankiw-ch14-044]:

- At 5%: $PV$ = \$123M > \$100M cost → undertake project[^mankiw-ch14-044].
- At 8%: $PV$ = \$93M < \$100M cost → forgo project[^mankiw-ch14-044].
- Implication: explains why investment — and thus quantity of loanable funds demanded — declines when the interest rate rises[^mankiw-ch14-044].

### Application 2 — Lottery payout (completed from 045)

Win \$1M choice between \$20,000/year for 50 years (total \$1M) vs immediate \$400,000 — present-value comparison determines rational choice[^mankiw-ch14-045]:

- At 7%: sum of $PV$ of fifty \$20,000 payments = only **\$276,000** → inferior to \$400,000 cash; the million-dollar prize in future cash flows discounted to present is worth far less[^mankiw-ch14-045].
- Source 044 introduces the question; 045 supplies the 7% calculation and answer[^mankiw-ch14-044][^mankiw-ch14-045].

QuickQuiz example: interest rate 7%, present value of \$150 to be received in 10 years is $\$150/(1.07)^{10} \approx \$76$[^mankiw-ch14-045].

## The Magic of Compounding and the Rule of 70

Growth rates that seem small in percentage terms are large after compounding for many years[^mankiw-ch14-045].

- **Elliot vs Darlene example:** both start at \$30,000 at age 22; Elliot's economy income grows 1% per year, Darlene's 3%[^mankiw-ch14-045]. After 40 years (age 62): Elliot ≈ \$45,000, Darlene ≈ \$98,000 — more than double, from a 2-point growth-rate difference[^mankiw-ch14-045].
- **Rule of 70:** if a variable grows at $x$ percent per year, it doubles in approximately $70/x$ years[^mankiw-ch14-045]. At 1%: doubles in $\approx70$ years; at 3%: $70/3\approx23$ years[^mankiw-ch14-045].
- Applies also to savings accounts, population, GDP[^mankiw-ch14-045].

**Ben Franklin's bequest:** \$5,000 left in 1791 for 200 years at 7%[^mankiw-ch14-045]:

- Doubling every $70/7=10$ years → 20 doublings → $2^{20}\times\$5{,}000 \approx \$5.24$ billion (text: about \$5 billion)[^mankiw-ch14-045].
- In fact grew to only \$2 million because some money was spent along the way[^mankiw-ch14-045].
- Source cites Einstein's remark that compounding is "the greatest mathematical discovery of all time"[^mankiw-ch14-045].

## Relationships

- Depends on: [Saving, Investment, and the Financial System — Financial Institutions, National Saving Identities, and the Market for Loanable Funds](saving-investment-and-the-financial-system.md) — financial system coordinating saving/investment and loanable-funds market where interest rate rations present vs future resources.
- Depends on: [Production and Growth — Productivity, its Determinants, and Long-Run Growth Policy](production-and-growth-productivity-determinants-and-policy.md) — small growth-rate differences compound into large living-standard gaps; Rule of 70 quantifies catch-up and long-run productivity effects.
- Uses: [Correcting Economic Variables for Inflation — Dollar Conversions, Regional Parities, Indexation, and Real vs Nominal Interest Rates](correcting-for-inflation-real-vs-nominal-indexation-and-regional-parities.md) — real vs nominal interest rate distinction for present-value calculations; discounting with inflation correction.
- Uses: [Mankiw's Ten Principles of Economics](ten-principles-of-economics-mankiw.md) — Principle 4 incentives (interest-rate incentive) and opportunity cost of time.
- See also: [The Market Forces of Supply and Demand — Competitive Markets, Demand and Supply, and Equilibrium](market-forces-of-supply-and-demand.md) — supply-demand logic underlying loanable-funds demand decline with higher r.
- See also: [Managing Risk — Risk Aversion, Insurance, Diversification, and the Trade-off between Risk and Return](managing-risk-risk-aversion-insurance-diversification.md) — Ch.14 14-2 risk side of finance, building on same time-value foundation.
- See also: [Asset Valuation and Market Efficiency — Fundamental Analysis, Efficient Markets Hypothesis, and Market Irrationality](asset-valuation-efficient-markets-hypothesis.md) — Ch.14 14-3 combines present value with risk to price stocks.

## Coverage limits

- Source 045 images 000284–000295 not inspected; Figure/table numbers follow prose.
- Source 045 truncated mid-Chapter 15 after 15-1a (unemployment measurement through January 2016 BLS example, 60,000-household Current Population Survey header visible; subsequent lines truncated). Full Chapter 15 natural-rate explanations (job search, minimum wage, unions, efficiency wages) not compiled here.
- Source 044 earlier truncation now resolved for lottery example via 045.

[^mankiw-ch14-044]: Mankiw, *Principles of Macroeconomics* 8th ed., Ch.14 — The Basic Tools of Finance (raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/044-the-basic-tools-of-finance.md).
[^mankiw-ch14-045]: Mankiw, *Principles of Macroeconomics* 8th ed., Ch.14 — The Magic of Compounding, Rule of 70, Risk and Asset Valuation excerpts (raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/045-the-magic-of-compounding-and-the-rule-of-70.md).
