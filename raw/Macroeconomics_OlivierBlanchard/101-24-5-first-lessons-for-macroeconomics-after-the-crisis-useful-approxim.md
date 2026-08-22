---
title: "24-5 FIRST LESSONS FOR MACROECONOMICS AFTER THE CRISIS — Useful Approximations"
part: 101
source: "Macroeconomics (Olivier Blanchard) (z-library.sk, 1lib.sk, z-lib.sk).md"
body_tokens: 6002
max_tokens: 10000
---

## Useful Approximations

Throughout this text, we use a number of approximations that make computations easier. These approximations are most reliable when the variables x, y, and z are small, say between 0 and 10%. The numerical examples in Propositions 3–10 are based on the values $x = 0 . 0 5$ and $y = 0 . 0 3$

Proposition 3:

$$
(1 + x) (1 + y) \approx (1 + x + y)\tag{A2.3}
$$

Here is the proof. Expanding $\left( 1 + x \right) \left( 1 + y \right)$ gives $\left( 1 + x \right) \left( 1 + y \right) = 1 + x + y + x y .$ . If x and y are small, then the product xy is very small and can be ignored as an approximation (for example, if $x = 0 . 0 5$ and $y = 0 . 0 3$ then $x y = 0 . 0 0 1 5 )$ . So, $( 1 + x ) ( 1 + y )$ is approximately equal to $( 1 + x + y )$ .The approximation (on the right side) gives 1.08 compared to an exact value (on the left) of 1.0815.

Proposition 4:

$$
(1 + x) ^ {2} \approx 1 + 2 x\tag{A2.4}
$$

The proof follows directly from Proposition 3, with $y = x .$ For the value of $x = 0 . 0 5$ , the approximation gives 1.10, compared to an exact value of 1.1025.

Application from Chapter 14: From arbitrage, the relation between the two-year interest rate and the current and the expected one-year interest rates is given by:

$$
(1 + i _ {2 t}) ^ {2} = (1 + i _ {1 t}) (1 + i _ {1 t + 1} ^ {e})
$$

Using Proposition 4 for the left side of the equation gives:

$$
(1 + i _ {2 t}) ^ {2} \approx 1 + 2 i _ {2 t}
$$

Using Proposition 3 for the right side of the equation gives:

$$
(1 + i _ {1 t}) (1 + i _ {1 t + 1} ^ {e}) \approx 1 + i _ {1 t} + i _ {1 t + 1} ^ {e}
$$

Using this expression to replace $( 1 + i _ { 1 t } ) ( 1 + i _ { 1 t + 1 } ^ { e } )$ in the original arbitrage relation gives:

$$
1 + 2 i _ {2 t} = 1 + i _ {1 t} + i _ {1 t + 1} ^ {e}
$$

Or, reorganizing:

$$
i _ {2 t} = \frac {(i _ {1 t} + i _ {1 t + 1} ^ {e})}{2}
$$

The two-year interest rate is approximately equal to the average of the current and the expected one-year interest rates.


## Proposition 5:

$$
(1 + x) ^ {n} \approx 1 + n x\tag{A2.5}
$$

The proof follows by repeated application of Propositions 3 and 4. For example, $( 1 + x ) ^ { 3 } = ( 1 + x ) ^ { 2 } ( 1 + x ) \approx ( 1 + 2 x ) ( 1 + x )$ by Proposition $4 , \approx ( 1 + 2 x + x ) = 1 + 3 x$ by Proposition 3.

The approximation becomes worse as n increases, however. For example, for $x = 0 . 0 5$ and $n = 5$ , the approximation gives 1.25, compared to an exact value of 1.2763. For $n = 1 0$ , the approximation gives 1.50, compared to an exact value of 1.63.

Proposition 6:

$$
\frac {(1 + x)}{(1 + y)} \approx (1 + x - y)\tag{A2.6}
$$

Here is the proof: Consider the product of $( 1 + x - y ) ( 1 + y )$ . Expanding this product gives $( 1 + x - y ) ( 1 + y ) = 1 + x + x y - y ^ { 2 } .$ If both x and y are small, then xy and $y ^ { 2 }$ are very small, so $( 1 + x - y ) ( 1 + y ) \approx ( 1 + x )$ . Dividing both sides of this approximation by $( 1 + y )$ gives the preceding proposition.

For the values of $x = 0 . 0 5$ and $y = 0 . 0 3$ , the approximation gives 1.02, while the correct value is nearly the same, 1.019.

Application from Chapter 14: The real interest rate is defined by:

$$
(1 + r _ {t}) = \frac {(1 + i _ {t})}{(1 + \pi_ {t + 1} ^ {e})}
$$

Using Proposition 6 gives

$$
(1 + r _ {t}) \approx (1 + i _ {t} - \pi_ {t + 1} ^ {e})
$$

Simplifying:

$$
r _ {t} \approx i _ {t} - \pi_ {t + 1} ^ {e}
$$

This gives us the approximation we use at many points in this text. The real interest rate is approximately equal to the nominal interest rate minus expected inflation.

These approximations are also convenient when dealing with growth rates. Define the rate of growth of x by $g _ { x } \equiv \Delta x / x ,$ , and similarly for $z , g _ { z }$ , and $y , g _ { y } .$ The numerical examples below are based on the values $g _ { x } = 0 . 0 5$ and $g _ { y } = 0 . 0 3$

Proposition 7: If z = xy then:

$$
g _ {z} \approx g _ {x} + g _ {y}\tag{A2.7}
$$

Here is the proof: Let $\Delta z$ be the increase in z when x increases by $\Delta x$ and y increases by $\Delta y .$ . Then, by definition:

$$
z + \Delta z = (x + \Delta x) (y + \Delta y)
$$

Divide both sides by z.

The left side becomes:

$$
\frac {(z + \Delta z)}{z} = \left(1 + \frac {\Delta z}{z}\right)
$$

The right-hand side becomes

$$
\begin{array}{r l} \frac {(x + \Delta x) (y + \Delta y)}{z} & = \frac {(x + \Delta x) (y + \Delta y)}{x} \\ & = \bigg (1 + \frac {\Delta x}{x} \bigg) \bigg (1 + \frac {\Delta y}{y} \bigg) \end{array}
$$

where the first equality follows from the fact that $z = x y$ the second equality from simplifying each of the two fractions.

Using the expressions for the left and right sides gives:

$$
\left(1 + \frac {\Delta z}{z}\right) = \left(1 + \frac {\Delta x}{x}\right) \left(1 + \frac {\Delta y}{y}\right)
$$

Or, equivalently,

$$
(1 + g _ {z}) = (1 + g _ {x}) (1 + g _ {y})
$$

From Proposition 3, $( 1 + g _ { z } ) \approx ( 1 + g _ { x } + g _ { y } )$ ,or, equivalently,

$$
g _ {z} \approx g _ {x} + g _ {y}
$$

For $g _ { x } = 0 . 0 5$ and $g _ { y } = 0 . 0 3$ , the approximation gives $g _ { z } = 8 \%$ , while the correct value is 8.15%.

Application from Chapter 13: Let the production function be of the form $Y = N A$ , where Y is production, N is employment, and A is productivity. Denoting the growth rates of Y, N, and A by $g _ { Y } , g _ { N } ,$ , and $g _ { A }$ respectively, Proposition 7 implies

$$
g _ {Y} \approx g _ {N} + g _ {A}
$$

The rate of output growth is approximately equal to the rate of employment growth plus the rate of productivity growth.

Proposition 8: If $z = x / y ,$ , then

$$
g _ {z} \approx g _ {x} - g _ {y}\tag{A2.8}
$$

Here is the proof: Let ∆z be the increase in z, when x increases by ∆x and y increases by ∆y. Then, by definition:

$$
z + \Delta z = \frac {x + \Delta x}{y + \Delta y}
$$

Divide both sides by z.

The left side becomes:

$$
\left(\frac {z + \Delta z}{z}\right) = \left(1 + \frac {\Delta z}{z}\right)
$$

The right side becomes:

$$
\frac {(x + \Delta x) 1}{(y + \Delta y) z} = \frac {(x + \Delta x) y}{(y + \Delta y) x} = \frac {(x + \Delta x) / x}{(y + \Delta y) / y} = \frac {1 + (\Delta x / x)}{1 + (\Delta y / y)}
$$

where the first equality comes from the fact that $z = x / y$ the second equality comes from rearranging terms, and the third equality comes from simplifying.

Using the expressions for the left and right sides gives:

$$
1 + \Delta z / z = \frac {1 + (\Delta x / x)}{1 + (\Delta y / y)}
$$

Or, substituting:

$$
1 + g _ {z} = \frac {1 + g _ {x}}{1 + g _ {y}}
$$

From Proposition 8, $( 1 + g _ { z } ) \approx ( 1 + g _ { x } - g _ { y } ) , 0 \mathrm { r } ,$ equivalently,

$$
g _ {z} \approx g _ {x} - g _ {y}
$$

For $g _ { x } = 0 . 0 5$ and $g _ { y } = 0 . 0 3$ , the approximation gives $g _ { z } = 2 \%$ , while the correct value is 1.9%.

Application from Chapter 9: Let M be nominal money, P be the price level. It follows that the rate of growth of the real money stock M/P is given by:

$$
g _ {M / P} \approx g _ {M} - \pi
$$

where p is the rate of growth of prices or, equivalently, the rate of inflation.


## Functions

We use functions informally in this text, as a way of denoting how a variable depends on one or more other variables.

In some cases, we look at how a variable Y moves with a variable X. We write this relation as

$$
Y = \underset {+} {f (X)}
$$

A plus sign below X indicates a positive relation; an increase in X leads to an increase in Y. A minus sign below X indicates a negative relation; an increase in X leads to a decrease in Y.

In some cases, we allow the variable Y to depend on more than one variable. For example, we allow Y to depend on X and Z:

$$
\begin{array}{c} Y = f (X, Z) \\ (+, -) \end{array}
$$

The signs indicate that an increase in X leads to an increase in Y, and that an increase in Z leads to a decrease in Y.

An example of such a function is the investment function (5.1) in Chapter 5:

$$
\begin{array}{c} I = I (Y, i) \\ (+, -) \end{array}
$$

This equation says that investment, I, increases with production, Y, and decreases with the interest rate, i.

In some cases, it is reasonable to assume that the relation between two or more variables is a linear relation. A given increase in X always leads to the same increase in Y. In that case, the function is given by:

$$
Y = a + b X
$$

This relation can be represented by a line giving Y for any value of X.

The parameter a gives the value of Y when X is equal to zero. It is called the intercept because it gives the value of Y when the line representing the relation “intercepts” (crosses) the vertical axis.

The parameter b tells us by how much Y increases when X increases by one unit. It is called the slope because it is equal to the slope of the line representing the relation.

A simple linear relation is the relation Y = X, which is represented by the 45-degree line and has a slope of 1. Another example of a linear relation is the consumption function (3.2) in Chapter 3:

$$
C = c _ {0} + c _ {1} Y _ {D}
$$

where C is consumption and $Y _ { D }$ is disposable income. $c _ { 0 }$ tells us what consumption would be if disposable income were equal to zero. $c _ { 1 }$ tells us by how much consumption increases when income increases by 1 unit; $c _ { 1 }$ is called the marginal propensity to consume.


## Logarithmic Scales

A variable that grows at a constant growth rate increases by larger and larger increments over time. Take a variable X that grows over time at a constant growth rate of, say, 3% per year.

![Image 000255](images/image-000255.jpg)  
Figure A2-1

■ Start in year 0 and assume X = 2. A 3% increase in X represents an increase of $0 . 0 6 ( 0 . 0 3 \times 2 )$ 2.

■ Go to year 20. X is now equal to $2 ( 1 . 0 3 ) ^ { 2 0 } = 3 . 6 1$ A 3% increase now represents an increase of $0 . 1 1 ( 0 . 0 3 \times 3 . 6 1 )$

■ Go to year 100. X is equal to $2 ( 1 . 0 3 ) ^ { 1 0 0 } = 3 8 . 4 . \mathrm { A }$ 3% increase represents an increase of $1 . 1 5 ( 0 . 0 3 \times 3 8 . 4 )$ so an increase about 20 times larger than in year 0.

If we plot X against time using a standard (linear) vertical scale, the plot looks like Figure A2-1(a). The increases in X become larger and larger over time (0.06 in year 0, 0.11 in year 20, 1.15 in year 100). The curve representing X against time becomes steeper and steeper.

Another way of representing the evolution of X is to use a logarithmic scale to measure X on the vertical axis. The property of a logarithmic scale is that the same proportional increase in this variable is represented by the same vertical distance on the scale. So the behavior of a variable such as X that increases by the same proportional increase (3%) each year is now represented by a line. Figure A2-1(b) represents the behavior of X, this time using a logarithmic scale on the vertical axis. The fact that the relation is represented by a line indicates that X is growing at a constant rate over time. The higher the rate of growth, the steeper the line.

![Image 000256](images/image-000256.jpg)  
(a) The evolution of X (using a linear scale) (b) The evolution of X (using a logarithmic scale)

![Image 000257](images/image-000257.jpg)  
Figure A2-2

![Image 000258](images/image-000258.jpg)  
(a) US GDP since 1890 (using a linear scale) (b) US GDP since 1890 (using a logarithmic scale)  
Source: 1890–1928: Historical Statistics of the United States, Table F1-5, adjusted for level to be consistent with the post-1929 series. 1929–2011 BEA, billions of chained 2005 dollars. www.bea.gov/national/index.htm#gdp.

In contrast to X, economic variables such as GDP do not grow at a constant growth rate every year. Their growth rate may be higher in some decades, lower in others; a recession may lead to a few years of negative growth. When looking at their evolution over time, it is often more informative to use a logarithmic scale rather than a linear scale. Let’s see why.

Figure A2-2(a) plots real US GDP from 1890 to 2011 using a standard (linear) scale. Because real US GDP is about 51 times bigger in 2011 than in 1890, the same proportional increase in GDP is 51 times bigger in 2011 than in 1890. So the curve representing the evolution of GDP over time becomes steeper and steeper over time. It is difficult to see from the figure whether the US economy is growing faster or slower than it was 50 years or 100 years ago.

Figure A2-2(b) plots US GDP from 1890 to 2011 using a logarithmic scale. If the growth rate of GDP was the same every year—so the proportional increase in GDP was the same every year—the evolution of GDP would be represented by a line, the same way the evolution of X was represented by a line in Figure A2-1(b). Because the growth rate of GDP is not constant from year to year—so the proportional increase in GDP is not the same every year—the evolution of GDP is no longer represented by a line. Unlike in

Figure A2-2(a), GDP does not explode over time, and the graph is more informative. Here are two examples.

■ If, in Figure A2-2(b), we were to draw a line to fit the curve from 1890 to 1929, and another line to fit the curve from 1950 to 2011 (the two periods are separated by the shaded area in Figure A2-2(b)), the two lines would have roughly the same slope. What this tells us is that the average growth rate was roughly the same during the two periods.

■ The decline in output from 1929 to 1933 is visible in Figure A2-2(b). (By contrast, the Great Recession looks small relative to the Great Depression.) So is the strong recovery of output that follows. By the 1950s, output appears to be back to its old trend line. This suggests that the Great Depression was not associated with a permanently lower level of output.

Note in both cases that you could not have derived these conclusions by looking at Figure A2-2(a), but you can derive them by looking at Figure A2-2(b). This shows the usefulness of using a logarithmic scale.


## Key Terms

■ linear relation, A-9

■ intercept, A-10

■ slope, A-10

Source: FRED: PCECCA, GDPC1


## APPENDIX 3 An Introduction to Econometrics

How do we know that consumption depends on income? How do we know the value of the propensity to consume?

To answer these questions and, more generally, to estimate behavioral relations and find out the values of the relevant parameters, economists use econometrics—the set of statistical techniques designed for use in economics. Econometrics can get very technical, but I shall outline in this appendix the basic principles behind it, using as an example the consumption function introduced in Chapter 3. We’ll concentrate on estimating $c _ { 1 }$ , the propensity to consume out of income.


## Changes in Consumption and in Disposable Income

The propensity to consume tells us by how much consumption changes for a given change in income. A natural first step is simply to plot changes in consumption versus changes in income and see how the relation between the two looks. (For simplicity, I shall use GDP as a measure of income. Clearly, a better specification would use disposable personal income, as well as other variables such as wealth, and allow consumption to depend not only on current income but on past income as well. I ignore these complications here.)

You can see the relation in Figure A3-1.

The vertical axis in Figure A3-1 measures the annual change in consumption minus the average annual change in consumption, for each year from 1970 to 2018. More precisely:

Let $C _ { t }$ denote consumption in year t. Let $\Delta C _ { t }$ denote $C _ { t } - C _ { t - 1 } ,$ the change in consumption from year t - 1 to year t. Let ∆C denote the average annual change in consumption since 1970. The variable measured on the vertical axis is constructed as $\Delta C _ { t } - \overline { { \Delta C } } . $ A positive value of the variable represents an increase in consumption larger than average, whereas a negative value represents an increase in consumption smaller than average.

Similarly, the horizontal axis measures the annual change in income, minus the average annual change in income since 1970, $\Delta Y _ { t } - \overline { { \Delta Y } }$

A particular dot in the figure gives the deviations of the change in consumption and income from their respective means for a particular year between 1970 and 2018. In 2018, for example, the change in consumption was higher than average by \$127 billion, and the change in income was higher than average by \$237 billion. (The point corresponding to 2018 is indicated by the red dot. For our purposes, it is not important to know which year each dot refers to, just what the set of points in the diagram looks like. So, except for 2018, the years are not indicated in Figure A3-1.)

Figure A3-1 suggests two main conclusions.

■ One, there is a clear positive relation between changes in consumption and changes in income. Most of the

Changes in Consumption versus Changes in Income, 1970–2018

There is a clear positive relation between changes in consumption and changes in income.

![Image 000259](images/image-000259.jpg)

The regression line is the line that best fits the scatter of points.

Figure A3-2  
![Image 000260](images/image-000260.jpg)  
Changes in Consumption and Changes in Income: The Regression Line

points lie in the upper-right and lower-left quadrants of the figure. When income increases by more than average, consumption also typically increases by more than average; when income increases by less than average, so typically does consumption.

■ Two, the relation between the two variables is good but not perfect. In particular, some points lie in the upperleft quadrant; these points correspond to years when smaller-than-average changes in income were associated with higher-than-average changes in consumption.

Econometrics allows us to state these two conclusions more precisely and to get an estimate of the propensity to consume. Using an econometrics software package, we can find the line that best fits the cloud of points in Figure A3-1. This line-fitting process is called ordinary least squares (OLS).<sup>1</sup> The estimated equation corresponding to the line is called a regression, and the line itself is called the regression line.

In this case, the estimated equation is given by

$$
\begin{array}{c} (\Delta C _ {t} - \overline {{\Delta C}}) = 0. 5 6 (\Delta Y _ {t} - \overline {{\Delta Y}}) + \text {residual} \\ \overline {{R}} ^ {2} = 0. 8 1 \end{array}\tag{A3.1}
$$

The regression line corresponding to this estimated equation is drawn in Figure A3-2. Equation (A3.1) reports two important numbers. (Econometrics packages give more information than that reported above; a typical printout, together with further explanations, is given in the Focus Box “A Guide to Understanding Econometric Results.”)

■ The first important number is the estimated propensity to consume. The equation tells us that an increase in income of \$1 billion above normal is typically associated with an increase in consumption of \$0.56 billion above normal. In other words, the estimated propensity to consume is 0.56. It is positive but smaller than 1.

■ The second important number is $\overline { { R } } ^ { 2 }$ , which is a measure of how well the regression line fits.

Having estimated the effect of income on consumption, we can decompose the change in consumption for each year into the part that is due to the change in income—the first term on the right in equation (A3.1)—and the rest, which is called the residual. For example, the residual for 2018 is indicated in Figure A3-2 by the vertical distance from the point representing 2018 to the regression line. It turns out that the point for 2018 is nearly on the regression line (this is just a coincidence), so the residual is very small. If all the points in Figure A3-2 were exactly on the estimated line, all residuals would be zero; all changes in consumption would be explained by changes in income. As you can see, however, this is not the case. $\overline { { R } } ^ { 2 }$ is a statistic that tells us how well the line fits. $\overline { { R } } ^ { 2 }$ is always between 0 and 1. A value of 1 would imply that the relation between the two variables is perfect, that all points are exactly on the regression line. A value of
