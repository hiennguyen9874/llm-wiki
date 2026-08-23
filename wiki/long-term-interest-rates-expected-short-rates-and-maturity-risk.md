---
type: Concept
title: Long-term interest rates — expected short rates and maturity risk
description: How long-term rates reflect expected future short-term rates plus compensation for the added risk of holding longer-maturity bonds.
tags: [long-term-interest-rates, short-term-interest-rates, monetary-policy, bond-prices, maturity-risk, interest-rate-expectations]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T17:49:15Z }
sources:
  - id: krugman-ch15-083
    resource: ../raw/Macroeconomics_Krugman/083-chapter-15-monetary-policy-the-equilibrium-interest-rate.md
    title: "Chapter 15 Monetary Policy — The Equilibrium Interest Rate (Krugman/Wells)"
  - id: blanchard-056
    resource: ../raw/Macroeconomics_OlivierBlanchard/056-financial-markets-and-expectations.md
    title: "Financial Markets and Expectations"
  - id: blanchard-057
    resource: ../raw/Macroeconomics_OlivierBlanchard/057-financial-markets-and-expectations-reintroducing-risk.md
    title: "Financial Markets and Expectations — Reintroducing Risk"
---

# Long-term interest rates — expected short rates and maturity risk

Long-term interest rates largely reflect market expectations of future short-term rates, which themselves depend in part on expected future monetary policy and the economic outlook. They also compensate holders for the greater risk of needing to sell a long-maturity bond before it matures; therefore long-term rates tend on average to exceed short-term rates, although the relationship can reverse when short-term rates are unusually high.[^krugman-ch15-083]

## Bond cash flows, yields, and the curve

A bond's **maturity** is the remaining duration of its promised payments. A discount bond makes one face-value payment at maturity; a coupon bond makes interim coupons as well as a final face-value payment. The economically relevant **yield to maturity** is the constant annual rate that makes the present value of all promised payments equal the bond's current price, rather than its coupon rate or current yield.[^blanchard-056]

The **yield curve** (or term structure) plots yields to maturity against maturity. It summarizes a cross-section of bond prices, and must be read jointly with default and resale-price risk: the expectation-based relations below deliberately abstract from default risk before adding a maturity-related premium.[^blanchard-056][^blanchard-057]

## Expected future short rates

An investor choosing between a two-year bond and rolling over one-year bonds compares the quoted long rate with the return expected from the future short rate. If the investor expects next year's one-year rate to rise sufficiently, successive one-year bonds can offer a higher two-year return than buying the two-year bond now; expected falls in short rates favor locking in the long bond instead.[^krugman-ch15-083]

Across investors, this portfolio choice makes a long-term rate largely reflect the market's average expectation of future short-term rates. The source consequently treats differing long rates across countries with similar near-zero short rates as a reflection of different expected future monetary policy and economic outlooks, not a contradiction of the short-rate comparison.[^krugman-ch15-083]

For a two-year discount bond, no-arbitrage gives $P_{2t}=100/[(1+i_{1t})(1+i^e_{1,t+1})]$. Defining its yield $i_{2t}$ by $P_{2t}=100/(1+i_{2t})^2$ implies $(1+i_{2t})^2=(1+i_{1t})(1+i^e_{1,t+1})$, or approximately $i_{2t}\approx(i_{1t}+i^e_{1,t+1})/2$. The same logic generalizes: a long yield summarizes current and expected short rates across its maturity.[^blanchard-056]

## Maturity and resale risk

A longer-maturity bond exposes its holder to more risk if cash is needed before maturity. The holder may have to sell when market interest rates have risen and bond prices have fallen, producing a loss. This rate-price inverse relationship creates an added risk relative to a bond that matures when the cash is needed; on the source's account, long-bond buyers generally require compensation for it.[^krugman-ch15-083]

With a risk premium $x$, the two-year approximation becomes $i_{2t}\approx(i_{1t}+i^e_{1,t+1}+x)/2$. Since resale-price risk normally rises with maturity, the source expects an upward-sloping curve on average even when short rates are expected to be flat. A downward slope indicates that expected falls in short rates more than offset the term premium; a positive slope alone does not identify a rise in expected short rates.[^blanchard-057]

### Historical illustration, not a forecast rule

The textbook's U.S. curves show a slightly inverted curve on 1 November 2000 (about 6.2% at three months and 5.8% at 30 years) and a steeply positive curve on 1 June 2001 (about 3.5% and 5.7%, respectively). It interprets the first as expectations of gradual Federal Reserve rate cuts amid a slowdown, and the second as an expectation of eventual increases after a sharper slowdown and cuts. Its ex post qualification is important: markets appeared to expect increases before June 2002, whereas the Fed did not raise its policy rate until June 2004.[^blanchard-056][^blanchard-057]

This is a textbook expectation-and-risk account, not a claim that the term spread has one fixed size or that every change in a long rate is caused by expected policy.

## Relationships

- Depends on: [The Basic Tools of Finance — Present Value, Future Value, Compounding, and Discounting](basic-tools-of-finance-present-value-compounding-and-discounting.md) — discounting explains why rising interest rates reduce bond prices.
- See also: [Money demand — liquidity, opportunity cost, and curve shifters](money-demand-liquidity-opportunity-cost-and-shifters.md) — money demand's opportunity cost is the short rate, not necessarily the long rate.
- See also: [Federal funds rate, discount rate, and the Fed's money-supply target](federal-funds-rate-and-money-supply-target.md) — the policy-controlled short-rate target whose expected path informs long rates.
- Qualifies: [The Influence of Monetary and Fiscal Policy on Aggregate Demand](influence-of-monetary-and-fiscal-policy-on-aggregate-demand.md) — short-rate policy need not move long rates one-for-one, an important limit on interest-rate transmission.

## Coverage limits

- The source provides an introductory portfolio-choice account, not a formal term-structure model or a measured term-premium decomposition.
- Its Germany/U.S. rate comparisons and 2015–2020 Federal Reserve narrative are source-era illustrations, not current rate data.
- Figures 15-3, 15-5, and 15-7 were visually inspected for the source's money-market and policy-transmission claims; Figures 15-4 and 15-6 were not needed for this concept.
- No credentials, PII, or disclosure markings were detected.
- Blanchard sources 056–057 are complete. The November 2000/June 2001 yield-curve figure was visually inspected; other diagrams are explanatory rather than additional evidence for the claims retained here.

[^blanchard-056]: Olivier Blanchard, *Macroeconomics*, “Financial Markets and Expectations” ([raw source](../raw/Macroeconomics_OlivierBlanchard/056-financial-markets-and-expectations.md); complete stored artifact reviewed; Figure 14-2 visually inspected).
[^blanchard-057]: Olivier Blanchard, *Macroeconomics*, “Financial Markets and Expectations — Reintroducing Risk” ([raw source](../raw/Macroeconomics_OlivierBlanchard/057-financial-markets-and-expectations-reintroducing-risk.md); complete stored artifact reviewed).

[^krugman-ch15-083]: Krugman and Wells, *Macroeconomics*, 6th ed., Ch. 15, “Monetary Policy — The Equilibrium Interest Rate” (raw/Macroeconomics_Krugman/083-chapter-15-monetary-policy-the-equilibrium-interest-rate.md).