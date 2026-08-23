---
type: Concept
title: Mundell–Fleming model — interest parity and policy under exchange-rate regimes
description: How interest parity links policy rates to exchange rates in a short-run open-economy IS–LM model, changing the transmission of monetary and fiscal policy under flexible and fixed rates.
tags: [macroeconomics, mundell-fleming, is-lm, interest-parity, exchange-rates, monetary-policy, fiscal-policy, fixed-exchange-rates, flexible-exchange-rates]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T18:05:04Z }
sources:
  - id: blanchard-076
    resource: ../raw/Macroeconomics_OlivierBlanchard/076-output-the-interest-rate-and-the-exchange-rate.md
    title: "Output, the Interest Rate, and the Exchange Rate"
  - id: blanchard-077
    resource: ../raw/Macroeconomics_OlivierBlanchard/077-capital-flows-sudden-stops-and-the-limits-to-the-interest-parity-condi.md
    title: "Capital Flows, Sudden Stops, and the Limits to the Interest Parity Condition"
  - id: blanchard-078
    resource: ../raw/Macroeconomics_OlivierBlanchard/078-monetary-contraction-and-fiscal-expansion-the-united-states-in-the-ear.md
    title: "Monetary Contraction and Fiscal Expansion: The United States in the Early 1980s"
  - id: blanchard-079
    resource: ../raw/Macroeconomics_OlivierBlanchard/079-us-trade-deficits-and-trump-administration-trade-tariffs.md
    title: "US Trade Deficits and Trump Administration Trade Tariffs"
  - id: blanchard-080
    resource: ../raw/Macroeconomics_OlivierBlanchard/080-german-reunification-interest-rates-and-the-ems.md
    title: "German Reunification, Interest Rates, and the EMS"
  - id: blanchard-083
    resource: ../raw/Macroeconomics_OlivierBlanchard/083-the-return-of-britain-to-the-gold-standard-keynes-versus-churchill.md
    title: "The Return of Britain to the Gold Standard: Keynes versus Churchill"
---

# Mundell–Fleming model — interest parity and policy under exchange-rate regimes

The textbook's short-run Mundell–Fleming model extends IS–LM to an open economy: the policy rate affects output directly through investment and indirectly through the exchange rate and net exports. Under flexible rates, a monetary tightening raises the rate, appreciates the currency, and reduces output through both channels. Under a credible fixed rate with perfect capital mobility, interest parity instead requires the domestic rate to match the foreign rate, sacrificing independent monetary policy.[^blanchard-076][^blanchard-077][^blanchard-079]

## Assumptions and equilibrium relations

The model holds domestic and foreign price levels fixed, normalizing their ratio so the real and nominal exchange rates move one-for-one, and treats expected inflation as zero so the nominal and real interest rates coincide.[^blanchard-076] Goods-market equilibrium is:

$$
Y=C(Y-T)+I(Y,i)+G+NX(Y,Y^*,E).
$$

Investment falls as $i$ rises; net exports fall as domestic output or the exchange rate $E$ rises, where a higher $E$ is an appreciation in this quotation convention. The latter effect assumes the Marshall–Lerner condition, so an appreciation lowers net exports.[^blanchard-076]

Ignoring risk, investors equalize expected domestic-currency returns on domestic and foreign bonds:

$$
E_t=\frac{1+i_t}{1+i_t^*}E^e_{t+1}.
$$

For given foreign rate and expected future rate, a higher domestic rate appreciates the currency today. The open-economy IS curve is therefore downward sloping for two reasons: a higher rate lowers investment and, through appreciation, lowers net exports. With the central bank targeting $i$, LM is horizontal; the rate then implies $E$ through parity.[^blanchard-077]

## Forward-looking exchange-rate determination

Iterating interest parity forward shows that today's exchange rate depends on the entire expected path of domestic and foreign interest rates and on the expected exchange rate at a distant horizon. For horizon $n$:

$$
E_t=\frac{(1+i_t)(1+i_{t+1}^e)\cdots(1+i_{t+n}^e)}{(1+i_t^*)(1+i_{t+1}^{*e})\cdots(1+i_{t+n}^{*e})}E_{t+n+1}^e.
$$

Thus, holding foreign rates fixed, a rise in current or expected future domestic rates appreciates the currency today; an upward revision to the distant expected exchange rate also raises today's rate.[^blanchard-083] News about the future current account can matter through that expected distant rate—for example, the source says an unexpectedly larger deficit may lead markets to expect eventual depreciation and hence depreciate the currency today.[^blanchard-083]

The result explains why the policy-rate/exchange-rate relation is uncertain rather than automatic. The source's stylized example has a cut from 5% to 3% depreciate the currency about 2% if expected for one year but about 10% if expected for five years; if the cut is smaller than anticipated, revised future-rate expectations can instead appreciate it. The calculation abstracts from risk premiums, which this model treats separately.[^blanchard-083]

## Flexible rates: policy transmission

- **Monetary contraction:** a higher policy rate reduces investment and appreciates the currency, which reduces net exports. Output falls through both channels. The net effect on net exports itself is indeterminate: lower output reduces imports, while appreciation worsens trade competitiveness.[^blanchard-077]
- **Fiscal expansion with an unchanged policy rate:** higher $G$ shifts IS right and raises output, while the unchanged rate leaves $E$ unchanged. Consumption, government spending, and—in this formulation—investment rise with output; net exports fall because higher output raises imports.[^blanchard-077]
- **Fiscal expansion near potential output:** if the central bank raises the rate to contain inflation pressure, output rises by less and the currency appreciates. Investment is ambiguous because output and the rate both rise; net exports fall from both higher imports and appreciation.[^blanchard-077]

## Trade tariffs in the model

At a given exchange rate, a tariff can reduce the domestic-good value of imports whether foreign firms absorb part of it in lower pre-tariff prices or consumers face a higher tariff-inclusive price. That initially raises demand and output, but it does not establish a lasting reduction in the trade deficit.[^blanchard-079]

The source identifies four offsetting channels: trading partners may retaliate against exports; a near-potential economy may induce rate increases and appreciation; expectations of lower future foreign borrowing may appreciate the currency even without a rate change; and an expansionary fiscal stance can worsen the trade balance through higher imports or rate-induced appreciation.[^blanchard-079] Its source-period 2018 illustration reports a roughly 9% real appreciation while the U.S. trade deficit remained near 3% of GDP; it explicitly treats the evidence as too early for strong conclusions.[^blanchard-079]

## Fixed rates and monetary autonomy

A fixed-rate system can use a peg to another currency, a crawling peg, a band, or—at the limiting case—a common currency. A rare downward or upward change in a fixed parity is called a **devaluation** or **revaluation**, respectively, rather than depreciation or appreciation.[^blanchard-079]

If markets believe a peg $\bar E$ will persist, both current and expected future exchange rates equal $\bar E$. Interest parity becomes $i=i^*$: with perfect capital mobility, the central bank must match the foreign rate and no longer has an independent monetary-policy instrument.[^blanchard-079]

Fiscal policy remains available. An increase in government spending raises output at the unchanged, foreign-determined rate, but the central bank cannot raise its rate to restrain an inflationary expansion; fiscal accommodation is consequently stronger than in the flexible-rate case with monetary offset. One instrument may still be insufficient to jointly target output and the trade balance.[^blanchard-079][^blanchard-080]

## Historical illustrations and limits

The textbook interprets the early-1980s United States as a policy mix consistent with the model: Volcker's rate increases initially coincided with dollar appreciation and recession, while later fiscal expansion coincided with strong growth, high rates, further appreciation, and a larger trade deficit. It reports the trade deficit reached 2.7% of GDP in 1984; these are historical, source-period observations rather than a complete causal attribution.[^blanchard-078]

German reunification illustrates the constraint within the pre-euro European Monetary System. German fiscal transfers and investment raised German demand; the Bundesbank tightened. France and Belgium had to match or exceed German nominal rates to maintain their parities, and their lower inflation made real rates especially high. The source links this to weak growth and rising unemployment, followed by 1992–93 EMS crises in which Italy and the United Kingdom left the system.[^blanchard-080]

Interest parity is an approximation, not a universal law. When perceived risk or liquidity needs rise, investors may flee a country's assets regardless of its interest rate—a **sudden stop**. The source associates the 2008 crisis with large outflows from emerging economies, currency pressure, and reduced domestic bank lending; such episodes violate the model's risk-neutral parity assumption.[^blanchard-077]

## Relationships

- Extends: [IS–LM model — joint short-run equilibrium, policy mix, and adjustment lags](is-lm-model-policy-mix-and-adjustment-lags.md) — adds foreign bonds, parity, and the exchange-rate/net-export channel.
- Extends: [Open-economy goods market, external adjustment, and the current account](open-economy-goods-market-and-external-adjustment.md) — makes the exchange rate jointly determined with output and the policy rate.
- Related: [Exchange-rate regimes — fixed and floating rates, intervention, and policy trade-offs](exchange-rate-regimes-fixed-floating-intervention-and-policy-trade-offs.md) — covers the institutional regime spectrum and means of defending targets.
- Related: [Macroeconomic Theory of the Open Economy — Loanable Funds, Foreign-Currency Exchange, and Policy Effects](macroeconomic-theory-of-the-open-economy.md) — gives a different, longer-run equilibrium framing for deficits, trade restrictions, and capital flight.
- Limited by: [Financial shocks, lending spreads, and the extended IS–LM model](financial-shocks-lending-spreads-and-extended-is-lm.md) — adds risk premiums and financial frictions omitted by risk-neutral parity.

## Coverage limits

All five supplied Markdown artifacts were read in full. Figures 19-1 through 19-5 were inspected in representative panels and match the stated parity, IS–LM, monetary-tightening, and fiscal-policy shifts; the Brazilian-equity-flow chart and 2010–18 U.S. exchange-rate/net-export chart were also inspected. The Brazilian chart supports volatility and the 2008 outflow, but not causal attribution beyond the surrounding source text. No credentials, personal data, or confidentiality markings were found.

[^blanchard-076]: Olivier Blanchard, *Macroeconomics*, “Output, the Interest Rate, and the Exchange Rate” (raw/Macroeconomics_OlivierBlanchard/076-output-the-interest-rate-and-the-exchange-rate.md; complete stored artifact reviewed).
[^blanchard-077]: Olivier Blanchard, *Macroeconomics*, “Capital Flows, Sudden Stops, and the Limits to the Interest Parity Condition” (raw/Macroeconomics_OlivierBlanchard/077-capital-flows-sudden-stops-and-the-limits-to-the-interest-parity-condi.md; complete stored artifact reviewed; Figures 19-1–19-5 and Brazilian-equity-flow chart inspected as noted).
[^blanchard-078]: Olivier Blanchard, *Macroeconomics*, “Monetary Contraction and Fiscal Expansion: The United States in the Early 1980s” (raw/Macroeconomics_OlivierBlanchard/078-monetary-contraction-and-fiscal-expansion-the-united-states-in-the-ear.md; complete stored artifact reviewed).
[^blanchard-079]: Olivier Blanchard, *Macroeconomics*, “US Trade Deficits and Trump Administration Trade Tariffs” (raw/Macroeconomics_OlivierBlanchard/079-us-trade-deficits-and-trump-administration-trade-tariffs.md; complete stored artifact reviewed; Figure 1 inspected).
[^blanchard-080]: Olivier Blanchard, *Macroeconomics*, “German Reunification, Interest Rates, and the EMS” (raw/Macroeconomics_OlivierBlanchard/080-german-reunification-interest-rates-and-the-ems.md; complete stored artifact reviewed).
[^blanchard-083]: Olivier Blanchard, *Macroeconomics*, stored as “The Return of Britain to the Gold Standard: Keynes versus Churchill” (raw/Macroeconomics_OlivierBlanchard/083-the-return-of-britain-to-the-gold-standard-keynes-versus-churchill.md; complete stored artifact reviewed; its stored title covers only its opening focus box).
