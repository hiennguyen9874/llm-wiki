---
type: Concept
title: IS–LM–PC model and medium-run adjustment
description: How IS–LM demand equilibrium and an expectations-anchored Phillips curve jointly determine output and inflation, and how policy returns the economy to potential output and target inflation.
tags: [macroeconomics, is-lm-pc, is-lm, phillips-curve, output-gap, potential-output, monetary-policy, natural-interest-rate, medium-run]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T18:07:29Z }
sources:
  - id: blanchard-030
    resource: ../raw/Macroeconomics_OlivierBlanchard/030-from-the-short-to-the-medium-run-the-is-lm-pc-model.md
    title: "From the Short to the Medium Run: The IS-LM-PC Model"
  - id: blanchard-031
    resource: ../raw/Macroeconomics_OlivierBlanchard/031-okuns-law-across-time-and-countries.md
    title: "Okun’s Law across Time and Countries"
  - id: blanchard-032
    resource: ../raw/Macroeconomics_OlivierBlanchard/032-deflation-in-the-great-depression.md
    title: "Deflation in the Great Depression"
---

# IS–LM–PC model and medium-run adjustment

The IS–LM–PC model joins demand-determined short-run output to an output-gap Phillips curve. At a central-bank-selected real rate, IS–LM determines output; output above (below) potential implies inflation above (below) the target when expectations are anchored. Policy adjustment toward the natural real rate returns output to potential and inflation to target in the model's medium run.[^blanchard-030][^blanchard-031]

## The three relations

- **IS:** goods-market equilibrium is $Y=C(Y-T)+I(Y,r+x)+G$. Consumption depends on disposable income, and investment rises with output but falls with the real borrowing rate, here the policy real rate $r$ plus a risk premium $x$. Thus lower $r$ raises investment, demand, and output through feedback effects.[^blanchard-030]
- **LM under an interest-rate target:** the central bank chooses $r$, represented by a horizontal LM curve. IS–LM intersection then determines short-run output.[^blanchard-030]
- **PC:** with $Y=N=L(1-u)$, the expectations-augmented Phillips relation can be written as $\pi-\pi^e=(\alpha/L)(Y-Y_n)$. The output gap $Y-Y_n$ is positive when unemployment is below its natural rate and negative when it is above it.[^blanchard-030]

The source then assumes U.S. inflation expectations are anchored at the central bank's target $\bar\pi$, yielding $\pi-\bar\pi=(\alpha/L)(Y-Y_n)$. This is an assumption about expectation formation, not a universal relation across countries or periods.[^blanchard-031]

## Short run and medium run

A rate below the natural/neutral rate produces output above potential and inflation above target in the diagram. The model's central-bank response is to raise the real rate: the economy moves up the IS curve to lower output and down the PC curve until $Y=Y_n$ and $\pi=\bar\pi$.[^blanchard-031]

At the resulting medium-run equilibrium:

$$Y=Y_n,\quad u=u_n,\quad \pi=\bar\pi,\quad r=r_n,\quad i=r_n+\bar\pi$$

where $r_n$ is the real rate that makes demand equal potential output. If real money demand is constant in this steady state, the source derives $\pi=g_M$ and $i=r_n+g_M$. It calls the implication that monetary policy changes inflation and nominal rates but not these real variables in the medium run **neutrality of money**.[^blanchard-031]

## Why adjustment may fail or be costly

The diagram is not a policy recipe with known inputs. Potential output and the natural unemployment rate are uncertain, inflation is a noisy signal of the gap, and investment, consumption, and production respond with lags. Delaying a response while inflation stays above target risks de-anchoring expectations; tightening too quickly can be counterproductive.[^blanchard-031]

A negative gap can be more dangerous at the practical nominal-rate floor. With deflation, $r=i-\pi$ remains positive even if $i=0$. If the real rate required to restore potential is lower, expected deflation can increase the real rate, further reduce output, and generate a deflation spiral.[^blanchard-031]

## Fiscal consolidation in this framework

Starting at potential, tax-led fiscal consolidation shifts IS left, causing a short-run fall in output and inflation at an unchanged real rate. If the central bank can lower the rate enough, output and inflation return to their targets in the medium run; the lower rate supports investment while higher taxes reduce consumption. The textbook labels this a model implication conditional on monetary accommodation, and notes that the lower bound can prevent the accommodation.[^blanchard-032]

## Relationships

- Extends: [IS–LM model — joint short-run equilibrium, policy mix, and adjustment lags](is-lm-model-policy-mix-and-adjustment-lags.md) — adds an output-gap/inflation relation and medium-run dynamics.
- Uses: [Output gaps, potential output, and diagnosing Keynesian versus classical recessions](output-gaps-and-diagnosing-demand-vs-supply-recessions.md) — defines the gap that links demand equilibrium to inflation.
- Uses: [The Short-Run Trade-off between Inflation and Unemployment — Phillips Curve, Expectations, Supply Shocks, and Disinflation Costs](phillips-curve-trade-off-inflation-unemployment.md) — supplies the expectations condition underlying PC adjustment.
- Uses: [Deflation, the zero lower bound, and liquidity traps](deflation-zero-lower-bound-and-liquidity-trap.md) — details the lower-bound failure mode.

## Coverage limits

The stored raw artifacts have misleading split points: `031` continues beyond its Okun's-law title into the model's medium-run and lower-bound discussion, and `032` continues beyond its Great-Depression title into fiscal consolidation and oil-price material. Claims above are attributed to the artifact containing them. Figures 9-1 through 9-4 were visually inspected. The model abstracts from open-economy channels and treats anchored expectations as an explicit assumption.

[^blanchard-030]: Olivier Blanchard, *Macroeconomics*, “From the Short to the Medium Run: The IS-LM-PC Model” ([raw source](../raw/Macroeconomics_OlivierBlanchard/030-from-the-short-to-the-medium-run-the-is-lm-pc-model.md)); Figure 9-1 visually inspected.
[^blanchard-031]: Olivier Blanchard, *Macroeconomics*, stored as “Okun’s Law across Time and Countries” ([raw source](../raw/Macroeconomics_OlivierBlanchard/031-okuns-law-across-time-and-countries.md)); Figures 9-2 and 9-3 visually inspected.
[^blanchard-032]: Olivier Blanchard, *Macroeconomics*, stored as “Deflation in the Great Depression” ([raw source](../raw/Macroeconomics_OlivierBlanchard/032-deflation-in-the-great-depression.md)); Figure 9-4 visually inspected.
