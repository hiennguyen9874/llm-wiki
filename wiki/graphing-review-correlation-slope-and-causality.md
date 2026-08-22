---
type: Concept
title: Graphing Review — Types, Correlation, Slope, and Causality Pitfalls
description: How economists use pie, bar, time-series and scatter plots, coordinate systems, slope, and demand-curve shifts versus movements to interpret data and avoid omitted-variable and reverse-causality traps.
tags: [graphing, coordinate-system, scatter-plot, correlation, slope, demand-curve, ceteris-paribus, omitted-variable, reverse-causality, mankiw]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T00:00:00Z }
sources:
  - id: mankiw-016
    resource: ../raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/016-in-the-news.md
    title: "In the News and Graphing Review — Principles of Macroeconomics, 8th Edition (N. Gregory Mankiw)"
---

# Graphing Review — Types, Correlation, Slope, and Causality Pitfalls

Economists use graphs as visual lenses for theory and data — single-variable displays and two-variable coordinate systems to show correlations, demand-curve logic, and responsiveness via slope — but real-world graphs require caution because omitted variables and reverse causality can make correlation masquerade as causation[^mankiw-016].

## Single-variable graphs

Three common displays carry only one variable at a time[^mankiw-016]:

- **Pie chart:** slices of total U.S. national income by source — compensation of employees, corporate profits, etc. — each slice a share of total[^mankiw-016].
- **Bar graph:** compares a variable across groups — e.g., average income in four countries, height = income level[^mankiw-016].
- **Time-series graph:** traces a variable over time — e.g., rising output per hour in the U.S. business sector, height of line = value in each year[^mankiw-016].

Each shows change over time or across individuals but cannot show relationships between two variables[^mankiw-016].

> Coverage note: pie, bar, and time-series figures in the source were referenced as Images 000052–000054 and were not visually inspected; description follows caption and prose evidence[^mankiw-016].

## Coordinate system and scatter plots

Two variables are displayed together in the **coordinate system** using ordered pairs $(x, y)$: $x$-coordinate = horizontal location, $y$-coordinate = vertical location, $(0,0)$ = origin[^mankiw-016].

- **Scatter plot:** each observation is a point — e.g., students' study time (hours/week, x-axis) vs grade point average (y-axis)[^mankiw-016].
  - Albert E.: (25 hours/week, 3.5 GPA); Alfred E.: (5 hours/week, 2.0 GPA)[^mankiw-016].
  - Rightward points tend to be higher → study time and GPA move together → **positive correlation**[^mankiw-016].
  - Hypothetical party time vs grades: higher party time associated with lower grades → **negative correlation** (variables move in opposite directions)[^mankiw-016].

Scatter plots do not isolate a single effect; other factors (prior preparation, talent, teacher attention, breakfast) also influence grades[^mankiw-016].

## Curves, ceteris paribus, and demand-curve shifts versus movements

Often economists isolate one relationship **holding everything else constant** (*ceteris paribus*)[^mankiw-016].

**Emma's demand for novels** (Table A-1) depends on price and income[^mankiw-016]:

| Price | $30k income | $40k income | $50k income |
|---|---|---|---|
| $10 | 2 novels | 5 novels | 8 novels |
| $9 | 6 | 9 | 12 |
| $8 | 10 | 13 | 16 |
| $7 | 14 | 17 | 20 |
| $6 | 18 | 21 | 24 |
| $5 | 22 | 25 | 28 |

Holding income constant at $40,000 and placing novels on the $x$-axis and price on the $y$-axis yields demand curve $D_1$, downward-sloping because price and quantity demanded are negatively related[^mankiw-016].

- With income $50,000, the curve is $D_2$, drawn to the **right** of $D_1$ — more novels demanded at each price[^mankiw-016].
- With income $30,000, the curve is $D_3$, to the **left** of $D_1$[^mankiw-016].

**Movements along vs shifts of a curve**[^mankiw-016]:

- **Movement along:** a change in a variable named on an axis does not shift the curve. Example: income $40k, price $8 → 13 novels; price falls to $7 → 17 novels, moving along $D_1$ left-to-right[^mankiw-016].
- **Shift:** a change in a relevant variable *not* on either axis shifts the curve. Income is on neither axis, so income rise $40k → $50k at fixed price $8 raises quantity 13 → 16 and shifts the curve outward ($D_1$ → $D_2$)[^mankiw-016]. Likewise, library closure (more novels demanded at each price) shifts right; cheaper movies (less time reading) shifts left[^mankiw-016].

Rule: if the changed variable is on an axis, move along; if off-axis, shift[^mankiw-016].

## Slope

The slope measures responsiveness — vertical change over horizontal change as we move along a line[^mankiw-016]:

$$slope = \frac{\Delta y}{\Delta x} = \frac{\text{rise}}{\text{run}}$$

- Small positive slope → fairly flat upward line; large positive slope → steep upward line; negative slope → downward line; horizontal line slope = 0; vertical line slope = infinite[^mankiw-016].
- **Emma's $D_1$:** using points (21 novels, $6) and (13 novels, $8): $slope = (6-8)/(21-13) = -2/8 = -1/4$; any two points on a straight line give the same slope[^mankiw-016].
- Interpretation: a small slope (near zero, flat) means quantity responds substantially to a price change; a larger magnitude (farther from zero, steep) means quantity adjusts only slightly[^mankiw-016]. Curved lines have varying slope by location[^mankiw-016].

## Cause and effect — two traps

When a graph is built from theory holding others constant (demand curve), direction of causation is clear. With real-world data, graphs alone rarely prove causation[^mankiw-016].

### Omitted-variable trap

Failing to hold a relevant third variable constant creates a deceptive relationship[^mankiw-016].

- **Big Brother Statistical Services example:** exhaustive home-item study finds strong positive association between number of cigarette lighters owned and probability of household cancer (Figure A-6, upward-sloping)[^mankiw-016].
- False policy inference: tax lighters and require warning labels "this lighter is dangerous to your health"[^mankiw-016].
- Correct test question: has every relevant variable except the one under study been held constant? No — lighter owners are more likely to smoke cigarettes, and cigarettes (not lighters) cause cancer. Without holding smoking constant, the lighters-cancer graph does not show the true effect of lighters[^mankiw-016].

Principle: ask whether movements of an omitted variable could explain the observed relationship[^mankiw-016].

### Reverse-causality trap

Even with correct variables, direction may be reversed[^mankiw-016].

- **Police and crime:** Association of American Anarchists plots violent crimes per thousand vs police officers per thousand across major cities; curve slopes upward (Figure A-7) and concludes police increase violence, so abolish police[^mankiw-016].
- Controlled experiment (random assignment of police across cities) would solve it, but observed data are not experimental: more dangerous cities hire more police — crime causes police, not vice versa[^mankiw-016].
- Temporal precedence does not settle it: behavior changes on expectations of future conditions, not just present changes. A city expecting a future crime wave may hire police now; couples buy a minivan *before* a baby arrives, but minivans do not cause larger families. The graph alone cannot establish which causes which[^mankiw-016].

No complete rulebook exists for when causation can be inferred from graphs; remembering that lighters don't cause cancer (omitted variable) and minivans don't cause babies (reverse causality) guards against many faulty economic arguments[^mankiw-016].

> Visual reference includes XKCD comic on correlation vs causation (Image 000061, not inspected)[^mankiw-016].

## Relationships

- Builds on: [Thinking Like an Economist — Scientific Method, Economic Models, and Positive vs Normative Analysis](thinking-like-an-economist-mankiw.md) — provides the graphical tools for the circular-flow and PPF models and the natural-experiment logic that graphs help test.
- Uses: [Bastiat's seen and unseen and macro policy fallacies](bastiat-seen-unseen-and-policy-fallacies.md) — omitted-variable reasoning parallels Bastiat's unseen-effects caution.
- Uses: [Sticky prices, nominal rigidity, and why money matters](sticky-prices-and-monetary-non-neutrality.md) — ceteris-paribus demand logic underlies why price stickiness matters short-run.

[^mankiw-016]: Mankiw, *Principles of Macroeconomics* 8th ed., In the News box and Appendix — Graphing: A Brief Review (raw/PrinciplesofMacroeconomics_8thEdition_GregoryMankiw/016-in-the-news.md).
