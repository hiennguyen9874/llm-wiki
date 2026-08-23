---
type: Concept
title: Financial shocks, lending spreads, and the extended IS–LM model
description: How expected inflation, borrower risk, and intermediary fragility separate the policy rate from the borrowing rate, allowing financial shocks to depress output and constrain standard monetary stabilization.
tags: [macroeconomics, is-lm, financial-shocks, risk-premium, real-interest-rate, bank-leverage, liquidity, great-financial-crisis, monetary-policy]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T18:00:59Z }
sources:
  - id: blanchard-020
    resource: ../raw/Macroeconomics_OlivierBlanchard/020-financial-markets-ii-the-extended-is-lm-model-financial-shocks-and-pol.md
    title: "Financial Markets II: The Extended IS-LM Model — Financial Shocks and Policies"
  - id: blanchard-077
    resource: ../raw/Macroeconomics_OlivierBlanchard/077-capital-flows-sudden-stops-and-the-limits-to-the-interest-parity-condi.md
    title: "Capital Flows, Sudden Stops, and the Limits to the Interest Parity Condition"
---

# Financial shocks, lending spreads, and the extended IS–LM model

The basic IS–LM model treats the central bank's policy rate as the rate that determines private spending. Blanchard's extension separates them: consumption and investment respond to a real **borrowing rate**, equal to the real policy rate plus a risk premium. A rise in that premium—because default risk, risk aversion, or intermediary distress rises—shifts IS left and reduces output unless policy can offset it.[^blanchard-020]

The same omitted risk matters internationally. A **sudden stop** is an investor flight from a country's assets despite its interest rate, driven by perceived risk or liquidity rather than expected return. The source's 2008 emerging-market illustration links outflows to currency pressure and domestic credit contraction, so risk-neutral interest parity is not a sufficient account of capital flows.[^blanchard-077]

## From nominal policy rate to real borrowing rate

The exact one-period real-rate relation is

$$1+r_t=\frac{1+i_t}{1+\pi^e_{t+1}},$$

where $i_t$ is the nominal rate and expected inflation is $\pi^e_{t+1}$. At modest rates, $r_t\approx i_t-\pi^e_{t+1}$; expected inflation therefore lowers the real cost of borrowing for a given nominal rate.[^blanchard-020]

A risky borrower's nominal rate can be written $i+x$, where $x$ is the **risk premium**. In the source's stylized case of zero recovery and risk-neutral investors, default probability $p$ implies $x=(1+i)p/(1-p)$; for small $i$ and $p$, $x\approx p$. Greater lender risk aversion raises the premium further even when $p$ is unchanged.[^blanchard-020]

## Intermediaries as an amplifier

Financial intermediaries borrow from investors and lend to households and firms. Their capital ratio is capital/assets; leverage is assets/capital. Higher leverage can raise expected return on capital but makes a given asset-value loss more likely to exhaust capital and cause insolvency.[^blanchard-020]

Even a solvent intermediary can deleverage after losses by shrinking assets and liabilities, which cuts lending. When liabilities are repayable quickly but loans or securities are hard to value and sell, withdrawal fears can require fire sales. Fire-sale losses can validate the fears and produce a run; this mechanism can also apply to nonbank or wholesale-funded intermediaries.[^blanchard-020]

Deposit insurance and central-bank liquidity provision can limit runs and fire sales, but both introduce judgment and incentive problems: insurance weakens depositor monitoring, while a central bank must distinguish an illiquid institution from an insolvent one under uncertainty.[^blanchard-020]

## Extended IS–LM mechanism

The extension writes the goods-market relation as

$$Y=C(Y-T)+I(Y,r+x)+G,$$

with the central bank selecting $r=\bar r$. Thus $r+x$, not $r$ alone, is the real rate relevant to spending.[^blanchard-020]

- A financial shock that increases $x$ raises the borrowing rate at a fixed policy rate, shifts IS left, and lowers equilibrium output.[^blanchard-020]
- Recession can reinforce the shock: lower output raises defaults, which can raise $x$ again.[^blanchard-020]
- In principle, cutting $r$ one-for-one with the increase in $x$ preserves the borrowing rate. The nominal lower bound limits this response: with $i\geq0$, the lowest real policy rate is approximately $-\pi^e$.[^blanchard-020]
- Fiscal expansion can also shift IS right, but the source notes the associated deficit trade-off. Measures that directly reduce $x$—such as liquidity facilities or asset purchases—are the counterpart to unconventional monetary policy in this representation.[^blanchard-020]

## 2008 as the textbook application

The source attributes the crisis amplification to the combination of high leverage, hard-to-value securitized assets, and short-term wholesale funding. Falling U.S. house prices and mortgage losses reduced capital; uncertainty and withdrawals forced asset sales, lowered similar assets' marked values, and curtailed lending. Lehman's 15 September 2008 bankruptcy intensified the system-wide panic.[^blanchard-020]

Its source-era account describes policy responses as increased deposit and debt guarantees, Federal Reserve liquidity facilities with broadened collateral, bank recapitalization through TARP, policy-rate cuts to zero, asset purchases intended to reduce borrowing costs, and fiscal stimulus. It concludes that these policies softened but did not prevent a major recession; it reports U.S. GDP fell 3.5% in 2009.[^blanchard-020]

These are the textbook's framework and historical narrative, not a complete causal attribution or a statement of current policy arrangements. Figures 6-1 through 6-9 were visually inspected: they support the real-rate derivation, the 2008 widening of corporate spreads, the IS shifts, the housing-price and confidence patterns, and the combined-policy diagram. The bank-run photograph is illustrative rather than evidence for a claim here.

## Relationships

- Extends: [IS–LM model — joint short-run equilibrium, policy mix, and adjustment lags](is-lm-model-policy-mix-and-adjustment-lags.md) — replaces its single spending-relevant rate with a real borrowing rate plus a financial spread.
- Uses: [Correcting Economic Variables for Inflation — Dollar Conversions, Regional Parities, Indexation, and Real vs Nominal Interest Rates](correcting-for-inflation-real-vs-nominal-indexation-and-regional-parities.md) — provides the purchasing-power distinction behind the real rate.
- Related: [U.S. banking crises, regulation, and shadow banking](us-banking-crises-regulation-and-shadow-banking.md) — provides historical and regulatory context for run-like shadow-banking fragility.
- Related: [Global financial crisis — housing, securitization, and world transmission](global-financial-crisis-housing-securitization-and-world-transmission.md) — covers international transmission and the confidence channel beyond this model.
- Constrained by: [Deflation, the zero lower bound, and liquidity traps](deflation-zero-lower-bound-and-liquidity-trap.md) — explains why the policy rate may not fall enough to offset a higher spread.
- Limits: [Mundell–Fleming model — interest parity and policy under exchange-rate regimes](mundell-fleming-interest-parity-and-policy-under-exchange-rate-regimes.md) — sudden stops qualify its risk-neutral foreign-bond arbitrage assumption.

[^blanchard-020]: Olivier Blanchard, *Macroeconomics*, “Financial Markets II: The Extended IS-LM Model — Financial Shocks and Policies” ([raw source](../raw/Macroeconomics_OlivierBlanchard/020-financial-markets-ii-the-extended-is-lm-model-financial-shocks-and-pol.md); complete stored artifact reviewed; Figures 6-1–6-9 visually inspected).

[^blanchard-077]: Olivier Blanchard, *Macroeconomics*, “Capital Flows, Sudden Stops, and the Limits to the Interest Parity Condition” (raw/Macroeconomics_OlivierBlanchard/077-capital-flows-sudden-stops-and-the-limits-to-the-interest-parity-condi.md; complete stored artifact reviewed; Brazilian-equity-flow chart inspected).
