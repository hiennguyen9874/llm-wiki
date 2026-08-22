---
title: "APPENDIX 2: The Real Exchange Rate and Domestic and Foreign Real Interest Rates"
part: 86
source: "Macroeconomics (Olivier Blanchard) (z-library.sk, 1lib.sk, z-lib.sk).md"
body_tokens: 2039
max_tokens: 10000
---

# APPENDIX 2: The Real Exchange Rate and Domestic and Foreign Real Interest Rates

We derived in Section 20-3 a relation among the current nominal exchange rate, current and expected future domestic and foreign nominal interest rates, and the expected future nominal exchange rate (equation (20.5)). This appendix derives a similar relation, but in terms of real interest rates and the real exchange rate. It then briefly discusses how this alternative relation can be used to think about movements in the real exchange rate.

## Deriving the Real Interest Parity Condition

Start from the nominal interest parity condition, equation (19.3):

$$
(1 + i _ {t}) = (1 + i _ {t} ^ {*}) (\frac {E _ {t}}{E _ {t + 1} ^ {e}})
$$

Recall the definition of the real interest rate from Chapter 6, equation (6.3):

$$
(1 + r _ {t}) = \frac {(1 + i _ {t})}{(1 + \pi_ {t + 1} ^ {e})}
$$

where $\pi _ { t + 1 } ^ { e } \equiv ( P _ { t + 1 } ^ { e } - P _ { t } ) / P _ { t }$ is the expected rate of inflation. Similarly, the foreign real interest rate is given by:

$$
(1 + r _ {t} ^ {*}) = \frac {(1 + i _ {t} ^ {*})}{(1 + \pi_ {t + 1} ^ {* e})}
$$

where $\pi _ { t + 1 } ^ { * e } \equiv ( P _ { t + 1 } ^ { * e } - P _ { t } ^ { * } ) / P _ { t } ^ { * }$ is the expected foreign rate of inflation.

Use these two relations to eliminate nominal interest rates in the interest parity condition, so:

$$
(1 + r _ {t}) = (1 + r _ {t} ^ {*}) \bigg [ \frac {E _ {t} (1 + \pi_ {t + 1} ^ {* e})}{E _ {t + 1} ^ {e} (1 + \pi_ {t + 1} ^ {e})} \bigg ]\tag{20.A1}
$$

Note from the definition of inflation that $\left( 1 + \pi _ { t + 1 } ^ { e } \right) =$ $P _ { t + 1 } ^ { e } / P _ { t }$ and, similarly, $( 1 + \pi _ { t + 1 } ^ { * e } ) = P _ { t + 1 } ^ { * e } / P _ { t } ^ { * } .$

Using these two relations in the term in brackets gives:

$$
\frac {E _ {t}}{E _ {t + 1} ^ {e}} \frac {\left(1 + \pi_ {t + 1} ^ {* e}\right)}{\left(1 + \pi_ {t + 1} ^ {e}\right)} = \frac {E _ {t}}{E _ {t + 1} ^ {e}} \frac {P _ {t + 1} ^ {* e} P _ {t}}{P _ {t} ^ {*} P _ {t + 1} ^ {e}}
$$

Reorganizing terms:

$$
\frac {E _ {t} P _ {t + 1} ^ {* e} P _ {t}}{E _ {t + 1} ^ {e} P _ {t} ^ {*} P _ {t + 1} ^ {e}} = \frac {E _ {t} P _ {t} / P _ {t} ^ {*}}{E _ {t + 1} ^ {e} P _ {t + 1} ^ {e} / P _ {t + 1} ^ {* e}}
$$

Using the definition of the real exchange rate:

$$
\frac {E _ {t} P / P _ {t} ^ {*}}{E _ {t + 1} ^ {e} P _ {t + 1} ^ {e} / P _ {t + 1} ^ {* e}} = \frac {\varepsilon_ {t}}{\varepsilon_ {t + 1} ^ {e}}
$$

Replacing in equation (20.A1) gives:

$$
(1 + r _ {t}) = (1 + r _ {t} ^ {*}) \frac {\varepsilon_ {t}}{\varepsilon_ {t + 1} ^ {e}}
$$

or equivalently,

$$
\varepsilon_ {t} = \frac {1 + r _ {t}}{1 + r _ {t} ^ {*}} \varepsilon_ {t + 1} ^ {e}\tag{20.A2}
$$

The real exchange rate today depends on the domestic and foreign real interest rates this year and the expected future real exchange rate next year. This equation corresponds to equation (20.4) in the text, but now in terms of the real rather than nominal exchange and interest rates.

## Solving the Real Interest Parity Condition Forward

The next step is to solve equation (20.A2) forward, in the same way we did for equation (20.4). The equation above implies that the real exchange rate in year $t + 1$ is given by:

$$
\varepsilon_ {t + 1} = \frac {1 + r _ {t + 1} ^ {e}}{1 + r _ {t + 1} ^ {* e}} \varepsilon_ {t + 2} ^ {e}
$$

Taking expectations as of year t:

$$
\varepsilon_ {t + 1} ^ {e} = \frac {1 + r _ {t + 1} ^ {e}}{1 + r _ {t + 1} ^ {* e}} \varepsilon_ {t + 2} ^ {e}
$$

Replacing in the previous relation:

$$
\varepsilon_ {t} = \frac {(1 + r _ {t}) (1 + r _ {t + 1} ^ {e})}{(1 + r _ {t} ^ {*}) (1 + r _ {t + 1} ^ {* e})} \varepsilon_ {t + 2} ^ {e}
$$

Solving for $\pmb { \varepsilon } _ { t + 2 } ^ { e }$ and so on gives:

$$
\varepsilon_ {t} = \frac {(1 + r _ {t}) (1 + r _ {t + 1} ^ {e}) \cdots (1 + r _ {t + n} ^ {e})}{(1 + r _ {t} ^ {*}) (1 + r _ {t + 1} ^ {* e}) (1 + r _ {t + n} ^ {* e})} \varepsilon_ {t + n + 1} ^ {e}
$$

This relation gives the current real exchange rate as a function of current and expected future domestic real interest rates, of current and expected future foreign real interest rates, and the expected real exchange rate in year t + n.

The advantage of this relation over the relation we derived in the text between the nominal exchange rate and nominal interest rates (equation (20.5)) is that it is typically easier to predict the future real exchange rate than to predict the future nominal exchange rate. If, for example, the economy suffers from a large trade deficit, we can be fairly confident that there will have to be a real depreciation—that $\pmb { \varepsilon } _ { t + n } ^ { e }$ will have to be lower. Whether there will be a nominal depreciation—what happens to $E _ { t + n } ^ { e } -$ is harder to tell. It depends on what happens to inflation, both at home and abroad, over the next n years.

## Back to Policy

Nearly every chapter of this text has looked at the role of policy. The next three chapters put it all together.

Chapter 21 asks two questions: Given the uncertainty about the effects of macroeconomic policies, wouldn’t it be better not to use policy at all? And even if policy can in principle be useful, can we trust policymakers to carry out the right policy? The bottom lines: Uncertainty limits the role of policy. Policymakers do not always do the right thing. But with the right institutions, policy does help and should be used.

Chapter 22 looks at fiscal policy. It reviews what we have learned, chapter by chapter, and then looks more closely at the implications of the government budget constraint for the relation between debt, spending, and taxes. It then considers the implications of high levels of public debt, a central issue in advanced countries today.

Chapter 23 looks at monetary policy. It reviews what we have learned, chapter by chapter, and then focuses on current challenges. First, it describes the framework, known as inflation targeting, that most central banks had adopted before the crisis. It then turns to several issues raised by the crisis, from the optimal rate of inflation to the role of finan cial regulation and the use of new instruments, known as macroprudential tools.

This page is intentionally left blank
