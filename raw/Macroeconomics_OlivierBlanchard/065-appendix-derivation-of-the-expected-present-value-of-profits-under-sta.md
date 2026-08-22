---
title: "APPENDIX: Derivation of the Expected Present Value of Profits under Static Expectations"
part: 65
source: "Macroeconomics (Olivier Blanchard) (z-library.sk, 1lib.sk, z-lib.sk).md"
body_tokens: 758
max_tokens: 10000
---

# APPENDIX: Derivation of the Expected Present Value of Profits under Static Expectations

You saw in the text (equation (15.3)) that the expected present value of profits is given by

$$
V (\Pi_ {t} ^ {e}) = \frac {1}{1 + r _ {t}} \Pi_ {t + 1} ^ {e} + \frac {1}{(1 + r _ {t}) (1 + r _ {t + 1} ^ {e})} (1 - \delta) \Pi_ {t + 2} ^ {e} + \dots
$$

If firms expect both future profits (per unit of capital) and future interest rates to remain at the same level as today, so that $\Pi _ { t + 1 } ^ { e } = \Pi _ { t + 2 } ^ { e } = \cdot \cdot \cdot = \Pi _ { t }$ and $r _ { t + 1 } ^ { e } = r _ { t + 2 } ^ { e } = \cdot \cdot \cdot = r _ { t } ,$ the equation becomes

$$
V (\Pi_ {t} ^ {e}) = \frac {1}{1 + r _ {t}} \Pi_ {t} + \frac {1}{(1 + r _ {t}) ^ {2}} (1 - \delta) \Pi_ {t} + \dots
$$

Factoring out $[ 1 / ( 1 + r _ { t } ) ] \Pi _ { t }$

$$
V (\Pi_ {t} ^ {e}) = \frac {1}{1 + r _ {t}} \Pi_ {t} \left(1 + \frac {1 - \delta}{1 + r _ {t}} + \dots\right)\tag{15.A1}
$$

The term in parentheses in this equation is a geometric series of the form $1 + x + x ^ { 2 } + \cdot \cdot \cdot$ . So, from Proposition 2 in Appendix 2 at the end of the book,

$$
(1 + x + x ^ {2} + \dots) = \frac {1}{1 - x}
$$

Here x equals $( 1 - \delta ) / ( 1 + r _ { t } )$ , so

$$
\begin{array}{l} \left(1 + \frac {1 - \delta}{1 + r _ {t}} + \left(\frac {1 - \delta}{1 + r _ {t}}\right) ^ {2} + \dots\right) \\ = \frac {1}{1 - (1 - \delta) / (1 + r _ {t})} = \frac {1 + r _ {t}}{r _ {t} + \delta} \end{array}
$$

Replacing the term in parentheses in equation (15.A1) with the expression above and manipulating gives:

$$
V (\Pi_ {t} ^ {e}) = \frac {1}{1 + r _ {t}} \frac {1 + r _ {t}}{r _ {t} + \delta} \Pi_ {t}
$$

Simplifying gives equation (15.5) in the text:

$$
V (\Pi_ {t} ^ {e}) = \frac {\Pi_ {t}}{(r _ {t} + \delta)}
$$

This page is intentionally left blank
