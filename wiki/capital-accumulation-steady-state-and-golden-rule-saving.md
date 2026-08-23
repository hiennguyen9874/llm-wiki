---
type: Concept
title: Capital Accumulation, the Steady State, and the Golden Rule of Saving
description: How saving finances capital accumulation in a Solow-style model, why it raises the long-run output level but not its permanent growth rate, and how the golden rule trades current consumption against steady-state consumption.
tags: [capital-accumulation, saving, investment, depreciation, steady-state, golden-rule, economic-growth, solow-model, consumption, human-capital, blanchard]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T17:42:44Z }
sources:
  - id: blanchard-043
    resource: ../raw/Macroeconomics_OlivierBlanchard/043-technological-progress-and-growth.md
    title: "Technological Progress and Growth (Blanchard, Macroeconomics)"
  - id: blanchard-044
    resource: ../raw/Macroeconomics_OlivierBlanchard/044-12-1-technological-progress-and-the-rate-of-growth.md
    title: "Technological Progress and the Rate of Growth (Blanchard, Macroeconomics)"
  - id: blanchard-038
    resource: ../raw/Macroeconomics_OlivierBlanchard/038-saving-capital-accumulation-and-output.md
    title: "Saving, Capital Accumulation, and Output (Blanchard, Macroeconomics)"
  - id: blanchard-039
    resource: ../raw/Macroeconomics_OlivierBlanchard/039-capital-accumulation-and-growth-in-france-in-the-aftermath-of-world-wa.md
    title: "Capital Accumulation and Growth in France in the Aftermath of World War II (Blanchard, Macroeconomics)"
  - id: blanchard-040
    resource: ../raw/Macroeconomics_OlivierBlanchard/040-social-security-saving-and-capital-accumulation-in-the-united-states.md
    title: "Social Security, Saving, and Capital Accumulation in the United States (Blanchard, Macroeconomics)"
---

# Capital Accumulation, the Steady State, and the Golden Rule of Saving

In the textbook's closed-economy, fixed-employment, no-technology model, output per worker rises with capital per worker but at a diminishing rate; saving becomes investment and changes capital by investment minus depreciation. The economy therefore converges to a steady capital and output level. A higher saving rate raises that level and causes a potentially long transition with faster growth, but cannot permanently raise growth; the consumption-maximizing saving rate is instead the golden-rule rate.[^blanchard-038][^blanchard-039] With exogenous technological progress, the corresponding steady state is a balanced-growth path: saving still changes levels and transition growth, whereas technology determines long-run output-per-worker growth.[^blanchard-043][^blanchard-044]

## Technological progress and balanced growth

Writing production as $Y=F(K,AN)$ treats $AN$ as **effective labor** (or labor in efficiency units): a higher technology level $A$ lets a given workforce produce more, equivalently requiring fewer workers for a given output. With constant returns, output per effective worker is $Y/(AN)=f(K/(AN))$, increasing but concave in capital per effective worker.[^blanchard-044]

If technology and population grow at rates $g_A$ and $g_N$, effective labor grows at $g_A+g_N$. Maintaining a given $K/(AN)$ therefore requires investment per effective worker of $(\delta+g_A+g_N)K/(AN)$, not merely depreciation. At the resulting steady state, $K/(AN)$ and $Y/(AN)$ are constant; capital and aggregate output grow at $g_A+g_N$, while capital and output **per worker** grow at $g_A$.[^blanchard-044]

An increase in the saving rate raises steady-state capital and output per effective worker and temporarily increases aggregate-output growth as the economy moves to that higher path. It does not change the balanced-growth rate $g_A+g_N$; sustained growth in output per worker requires sustained technological progress.[^blanchard-044]

## Capital–output feedback and steady state

Let $k=K/N$ and $y=Y/N$. With constant employment, a fixed saving rate $s$, zero public saving, and a closed economy, the source specifies

$$
y_t=f(k_t), \qquad \Delta k_t=s f(k_t)-\delta k_t.
$$

Here $f$ is increasing and concave (diminishing returns to capital), and $\delta$ is the depreciation rate. Output determines saving and investment; investment adds to the capital stock, while depreciation reduces it.[^blanchard-038]

The **steady state** satisfies

$$
sf(k^*)=\delta k^*.
$$

Below $k^*$, investment exceeds depreciation, so capital and output per worker rise; above it, depreciation exceeds investment, so both fall toward $k^*$. This convergence result depends on the stated model assumptions, especially fixed employment and no technological progress.[^blanchard-038]

## What a higher saving rate changes

A rise in $s$ shifts investment per worker upward, giving a higher $k^*$ and $y^*$. It reduces consumption initially because current income is diverted to saving, then produces faster output growth during the approach to the new level. Without technological progress, the eventual per-worker growth rate is zero at every saving rate; with exogenous technological progress, the saving increase still raises the level/path of output per worker but not its eventual growth rate.[^blanchard-039]

The source's postwar-France illustration is consistent with this transition mechanism: it estimates France's 1945 capital stock at about 30% below its prewar value and reports 9.6% annual real-GDP growth from 1946–50. It explicitly cautions that modernization of an aged capital stock and production techniques also contributed, so the episode is not evidence that capital accumulation alone explains the growth.[^blanchard-039]

## Golden-rule saving: output is not consumption

At steady state, consumption per worker is output less depreciation:

$$
c^*=f(k^*)-\delta k^*.
$$

Thus more saving always raises steady-state capital and output in this model, but need not raise consumption. At a sufficiently high capital stock, the extra output from more capital is smaller than the extra depreciation needed to maintain it. The **golden-rule level of capital** (and associated saving rate $s_G$) maximizes steady-state consumption: raising saving toward it lowers current consumption but raises later consumption; raising saving beyond it lowers both current and long-run consumption.[^blanchard-039]

For the illustrative production function $y=\sqrt{k}$, the source derives $k^*=(s/\delta)^2$, $y^*=s/\delta$, and $c^*=s(1-s)/\delta$. With this particular functional form, steady-state consumption is maximized at $s=1/2$; that numerical result is not a general golden-rule rate.[^blanchard-040]

## Relationships

- Extends: [Production and Growth — Productivity, its Determinants, and Long-Run Growth Policy](production-and-growth-productivity-determinants-and-policy.md) — supplies the explicit accumulation dynamics behind its diminishing-returns and level-versus-growth distinction.
- Depends on: [Saving, Investment, and the Financial System — Financial Institutions, National Saving Identities, and the Market for Loanable Funds](saving-investment-and-the-financial-system.md) — its closed-economy saving-equals-investment condition connects saving to new capital.
- Related: [Social Security Funding, Saving, and Capital Accumulation](social-security-funding-saving-and-capital-accumulation.md) — pension design can change total saving and therefore the capital path in this framework.
- Related: [Technology Diffusion, R&D, and Innovation versus Imitation](technology-diffusion-rd-and-innovation-imitation.md) — the technological-progress rate treated as exogenous here arises from research, adoption, and imitation processes.

## Coverage limits

- The baseline model abstracts from population growth; the extension here treats population and technological progress as exogenous. It still abstracts from open-economy borrowing and lending, public saving, short-run demand effects, and endogenous technological progress, so its results should not be read as a complete policy model.
- Inspected Figures 11-1 through 11-7 (source images 000101–000109) and Figures 12-1 through 12-4 (000110–000113). The latter accord with the effective-worker curve, convergence condition, saving-rate level shift, and temporary growth transition above; image 000107 is a focus-box marker with no analytical content.

[^blanchard-043]: Blanchard, *Macroeconomics*, ch. 12 introduction, “Technological Progress and Growth” (raw/Macroeconomics_OlivierBlanchard/043-technological-progress-and-growth.md).
[^blanchard-044]: Blanchard, *Macroeconomics*, ch. 12, “Technological Progress and the Rate of Growth” (raw/Macroeconomics_OlivierBlanchard/044-12-1-technological-progress-and-the-rate-of-growth.md).
[^blanchard-038]: Blanchard, *Macroeconomics*, ch. 11, “Saving, Capital Accumulation, and Output” (raw/Macroeconomics_OlivierBlanchard/038-saving-capital-accumulation-and-output.md).
[^blanchard-039]: Blanchard, *Macroeconomics*, ch. 11 continuation, “Capital Accumulation and Growth in France in the Aftermath of World War II” (raw/Macroeconomics_OlivierBlanchard/039-capital-accumulation-and-growth-in-france-in-the-aftermath-of-world-wa.md).
[^blanchard-040]: Blanchard, *Macroeconomics*, ch. 11 continuation, “Social Security, Saving, and Capital Accumulation in the United States” (raw/Macroeconomics_OlivierBlanchard/040-social-security-saving-and-capital-accumulation-in-the-united-states.md).
