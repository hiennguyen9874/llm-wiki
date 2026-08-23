---
type: Concept
title: Wage setting, price setting, and the natural rate of unemployment
description: How wage bargaining and efficiency wages, expected prices, institutional factors, and firm markups jointly determine the real wage and medium-run natural unemployment rate.
tags: [wage-setting, price-setting, natural-rate, unemployment, real-wages, markups, efficiency-wages, expected-prices]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T18:07:29Z }
sources:
  - id: blanchard-024
    resource: ../raw/Macroeconomics_OlivierBlanchard/024-from-henry-ford-to-jeff-bezos.md
    title: "From Henry Ford to Jeff Bezos (Blanchard)"
  - id: blanchard-026
    resource: ../raw/Macroeconomics_OlivierBlanchard/026-the-phillips-curve-the-natural-rate-of-unemployment-and-inflation.md
    title: "The Phillips Curve, the Natural Rate of Unemployment, and Inflation (Blanchard)"
  - id: blanchard-032
    resource: ../raw/Macroeconomics_OlivierBlanchard/032-deflation-in-the-great-depression.md
    title: "Deflation in the Great Depression"
---

# Wage setting, price setting, and the natural rate of unemployment

In Blanchard's labor-market model, the natural unemployment rate is where the real wage sought in wage setting equals the real wage implied by firms' price setting. It is therefore structural rather than a constant of nature: institutions and policy variables that shift wage setting, and market power that changes markups, change the equilibrium rate.[^blanchard-024]

## Wage setting

Nominal wage setting is represented as:

$$W=P^e F(u,z), \qquad F_u<0,\;F_z>0$$

Workers and firms care about real wages, so a proportional change in the expected price level $P^e$ produces the same proportional change in nominal wages when set in advance. Wages fall as unemployment $u$ rises because workers' outside options and bargaining power weaken; $z$ collects other wage-setting influences.[^blanchard-024]

Two mechanisms support wages above reservation wages:

- **Bargaining:** replacement cost, job-specific skills, and ease of finding another job determine worker leverage. Low unemployment makes replacements harder for firms and alternatives easier for workers.[^blanchard-024]
- **Efficiency wages:** firms can pay more to reduce quits, improve morale, effort, or productivity. Low unemployment increases the incentive to quit, so retaining workers can require higher pay.[^blanchard-024]

The source treats unemployment benefits, minimum wages, and employment protection as examples that can increase $z$ and thus wages at a given unemployment rate; whether their broader social benefits outweigh this modeled side effect is a policy question outside the equation.[^blanchard-024]

## Price setting

With labor as the only input and normalized labor productivity, $Y=N$, marginal cost is $W$. Firms with market power set:

$$P=(1+m)W$$

where $m$ is the markup. The corresponding real wage firms can pay is:

$$\frac{W}{P}=\frac{1}{1+m}$$

A higher markup lowers the real wage implied by price setting.[^blanchard-024]

## Equilibrium and comparative statics

Under the medium-run simplifying assumption $P=P^e$, wage setting gives $W/P=F(u,z)$. Equating it to price setting gives the natural rate $u_n$:

$$F(u_n,z)=\frac{1}{1+m}$$

Graphically, wage setting slopes down in $(u,W/P)$ space, whereas price setting is horizontal at $1/(1+m)$; their intersection fixes $u_n$.[^blanchard-024]

- Higher unemployment benefits, represented as higher $z$, shift wage setting up. A higher unemployment rate is then required to restore the real wage consistent with price setting.[^blanchard-024]
- A higher markup $m$ shifts the price-setting real wage down. The model therefore requires higher equilibrium unemployment to make wage setters accept that lower real wage.[^blanchard-024] The source uses a persistent oil-price increase as one mechanism that raises production costs and is represented by a higher markup; this is a reduced-form model treatment, not a complete energy-production model.[^blanchard-032]

The term **natural** is conventional but potentially misleading: these determinants include policy and market structure. The source calls **structural rate of unemployment** a more descriptive, though less common, name.[^blanchard-024]

## From wage-price setting to inflation

Keeping $P^e$ distinct from $P$ and using the source's linear wage-setting form $F(u,z)=1-\alpha u+z$ gives $P=P^e(1+m)(1-\alpha u+z)$. Blanchard restates this as $\pi_t=\pi_t^e+(m+z)-\alpha u_t$; with $u_n=(m+z)/\alpha$, the inflation surprise is $-\alpha(u_t-u_n)$.[^blanchard-026] Thus the Phillips relation is the wage-price model's short-run implication, conditional on expectations and on slowly changing $m$ and $z$, not an independent permanent trade-off.[^blanchard-026]

## Short run versus medium run

When wages are fixed on expectations formed before the actual price level is known, $P$ can differ from $P^e$. Short-run output and unemployment can then differ from their natural levels and respond to monetary policy, fiscal policy, and demand conditions. In the model's medium-run account, expectations cease to be systematically wrong, so output tends toward the level associated with $u_n$.[^blanchard-024]

## Relationships

- Related to: [Natural rate of unemployment — frictional, structural, and cyclical components](natural-rate-of-unemployment-frictional-structural-and-cyclical.md) — complementary decomposition and policy-sensitive natural-rate framing.
- Uses: [Efficiency wages and the invention of unemployment — Ford's five-dollar day](efficiency-wages-ford-five-dollar-day.md) — a firm-level mechanism behind wage setting.
- Related to: [The Short-Run Trade-off between Inflation and Unemployment — Phillips Curve, Expectations, Supply Shocks, and Disinflation Costs](phillips-curve-trade-off-inflation-unemployment.md) — relaxing $P=P^e$ produces the expectations-based short-run link.
- Related to: [Labor-market flows, participation, and unemployment dynamics](labor-market-flows-participation-and-unemployment-dynamics.md) — unemployment affects bargaining power and worker transitions.
- Related to: [Oil-price shocks, markups, potential output, and stagflation](oil-price-shocks-markups-potential-output-and-stagflation.md) — applies the markup comparative static to an energy-cost shock.

## Coverage limits

This is a deliberately simplified model: it assumes labor is the only input, constant productivity, and a uniform markup. It does not itself estimate $u_n$ or establish the size of policy effects. The wage/price-setting and two comparative-static figures were visually inspected.[^blanchard-024]

[^blanchard-024]: Blanchard, *Macroeconomics*, Chapter 7 material including “From Henry Ford to Jeff Bezos” (raw/Macroeconomics_OlivierBlanchard/024-from-henry-ford-to-jeff-bezos.md; Figures 7-6–7-8 visually inspected).
[^blanchard-026]: Blanchard, *Macroeconomics*, Ch. 8 §§8-1–8-2, “The Phillips Curve, the Natural Rate of Unemployment, and Inflation” (raw/Macroeconomics_OlivierBlanchard/026-the-phillips-curve-the-natural-rate-of-unemployment-and-inflation.md; complete stored artifact; Figures 8-1–8-5 visually inspected).
[^blanchard-032]: Olivier Blanchard, *Macroeconomics*, stored as “Deflation in the Great Depression” (raw/Macroeconomics_OlivierBlanchard/032-deflation-in-the-great-depression.md; Figure 9-6 visually inspected).