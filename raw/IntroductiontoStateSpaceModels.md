# Introduction to State Space Models (SSM)

Site: Hugging Face
Author: Loïck BOURDOIS
Time: 07-19-2024, 19:43:55
Link: https://huggingface.co/blog/lbourdois/get-on-the-ssm-train

Body:
[Back to Articles](https://huggingface.co/blog)

[Loïck BOURDOIS's avatar](https://huggingface.co/lbourdois)

**Une version en français est disponible sur mon [blog](https://lbourdois.github.io/blog/ssm/introduction_ssm/)**.

> **Changelog**
> 2023-12-14: article release.
> 2024-04-08: typos corrections (my English isn't perfect 😅).
> 2024-06-11: added links to the second article of my SSM blog posts serie.
> 2024-07-18: LaTex typo correction.
> 2024-09-23: rewrote introduction and added a section about the origin of SSM in deep learning.
> 2025-10-26: clarification of some sentence structures following reader feedback.
> 2025-11-01: add some ressources (Appendix E of the book [*Hands-On Machine Learning with Scikit-Learn and Pytorch*](https://ageron.github.io/) by Aurélien Geron)

## https://huggingface.co/blog/lbourdois/get-on-the-ssm-train#foreword

Foreword

I'd like to extend my warmest thanks to Boris ALBAR, Pierre BEDU and Nicolas PREVOT for agreeing to set up a working group on the subject of SSMs and thus accompanying me in my discovery of this type of model. A special thanks to the former for taking the time to proofread this blog post.

## https://huggingface.co/blog/lbourdois/get-on-the-ssm-train#introduction

**Introduction**

The ***States Spaces Models*** are traditionally used in control theory to model a dynamic system via state variables.

Aaron R. VOELKER and Chris ELIASMITH addressed the question of how the brain effectively represents temporal information. They discovered in 2018 in “[Improving Spiking Dynamical Networks: Accurate Delays, Higher-Order Synapses, and Time Cells](https://compneuro.uwaterloo.ca/files/publications/voelker.2018.pdf)” that an SSM is an excellent model for describing the “[time cells](https://en.wikipedia.org/wiki/Howard_Eichenbaum#Research_on_time_cells)” present in the brain (hippocampus and cortex in particular).

From neuroscience, they applied their work to the field of deep learning and were thus (to our knowledge) the first to use SSMs in deep learning. For more details on this work, please refer to the “[SSM history](https://huggingface.co/blog/lbourdois/get-on-the-ssm-train#-ssm-history-)” section at the end of this blog post.

In this article, we will define the basics of a deep learning SSM. To do this, we will based on the S4 model introduced in “[*Efficiently Modeling Long Sequences with Structured State Spaces*](https://arxiv.org/abs/2111.00396)” by Albert GU et al. in 2021. This is not a model that is used as is in practice (other SSMs with better performance or easier to implement are now available). We use it here for educational purposes. Released a week earlier than S4, [LSSL](https://arxiv.org/abs/2110.13985), by the same authors, is also an important source of information on the subject. We'll take a look at the various developments arising from S4 in a future [blog post](https://huggingface.co/blog/lbourdois/ssm-2022). Before that, let's delve into the basics of SSM.

## https://huggingface.co/blog/lbourdois/get-on-the-ssm-train#definition-of-an-ssm-in-deep-learning

**Definition of an SSM in deep learning**

Let's use the image below to define an SSM:

| [image/png](https://cdn-uploads.huggingface.co/production/uploads/613b0a62a14099d5afed7830/G7icfkYoxIqHZcJGHM7UD.png) |
| --- |
| Figure 1: *View of a continuous, time-invariant SSM (Source: https://en.wikipedia.org/wiki/State-space_representation)* |

It can be seen that an SSM is based on three variables that depend on time tt :

- x(t)∈Cnx(t) \in \mathbb {C}^{n} represents the nn state variables,
- u(t)∈Cmu(t) \in \mathbb {C}^{m} represents the mm state inputs,
- y(t)∈Cpy(t) \in \mathbb {C}^{p} represents the pp outputs,

We can also see that it's made up of four learnable matrices: A,B,C\mathbf A, \mathbf B, \mathbf C and D\mathbf D.

- A∈Cn×n\mathbf A \in \mathbb {C}^{n \times n} is the state matrix (controlling the latent state xx),
- B∈Cn×m\mathbf B \in \mathbb {C}^{n \times m} is the control matrix,
- C∈Cp×n\mathbf C \in \mathbb {C}^{p \times n} is the output matrix,
- D∈Cp×m\mathbf D \in \mathbb {C}^{p \times m} is the command matrix,

The above picture can be reduced to the following system of equations:

x′(t)=Ax(t)+Bu(t)y(t)=Cx(t)+Du(t)
\begin{aligned}
x'(t) &= \mathbf{A}x(t) + \mathbf{B}u(t) \\
y(t) &= \mathbf{C}x(t) + \mathbf{D}u(t)
\end{aligned}

Note: here we use the notation x′x' to designate the derivative of xx. It's not out of the question to encounter the notation x˙ẋ in the literature instead.

Similarly, since it is implicit that the variables depend on time, the preceding equation is generally written in the following form for the sake of simplicity:

x′=Ax+Buy=Cx+Du
\begin{aligned}
x' &= \mathbf{A}x + \mathbf{B}u \\
y &= \mathbf{C}x + \mathbf{D}u
\end{aligned}

This system can be made even lighter, because in deep learning SSMs, Du=0\mathbf{D}u = 0 is seen as an easily computable *skip connection*.

x′=Ax+Buy=Cx
\begin{aligned}
x' &= \mathbf{A}x + \mathbf{B}u \\
y &= \mathbf{C}x
\end{aligned}

This system is continuous. It must therefore first be discretized before it can be supplied to a computer.

## https://huggingface.co/blog/lbourdois/get-on-the-ssm-train#discretization

**Discretization**

Discretization is one of, if not the most important point in SSM. All the efficiency of this architecture lies in this step, since it enables us to pass from the continuous view of the SSM to its two other views: the **recursive view** and the **convolutive view**.
If there's one thing to remember from this article, it's this.

| https://github.com/lbourdois/blog/assets/58078086/12bbe1cf-3911-4bad-9a3b-3f427bc6bc82 |
| --- |
| Figure 2: *Image from blog post [Structured State Spaces: Combining Continuous-Time, Recurrent, and Convolutional Models](https://hazyresearch.stanford.edu/blog/2022-01-14-s4-3) by Albert GU et al. (2022)* |

We'll see in later [article](https://huggingface.co/blog/lbourdois/ssm-2022) that there are several possible discretizations. This is one of the main differences between the various existing SSM architectures.
For this first article, let's apply the discretization proposed in S4 to illustrate the two additional views of an SSM.

## https://huggingface.co/blog/lbourdois/get-on-the-ssm-train#recursive-view-of-an-ssm

**Recursive view of an SSM**

To discretize the continuous case, let's use the [trapezoid method](https://fr.wikipedia.org/wiki/Transformation_bilin%C3%A9aire#Approximation_trap%C3%A9zo%C3%AFdale) where the principle is to assimilate the region under the representative curve of a function ff defined on a segment [tn,tn+1][t_n , t_{n+1}] to a trapezoid and calculate its area TT : T=(tn+1−tn)f(tn)+f(tn+1)2T=(t_{n+1} - t_n){\frac {f(t_n)+f(t_{n+1})}{2}}.

We then have: xn+1−xn=12Δ(f(tn)+f(tn+1))x_{n+1} - x_n = \frac{1}{2}\Delta(f(t_n) + f(t_{n+1})) with Δ=tn+1−tn\Delta = t_{n+1} - t_n.
If xn′=Axn+Bunx'_n = \mathbf{A}x_n + \mathbf{B} u_n (first line of the SSM equation), corresponds to ff, so:

xn+1=xn+Δ2(Axn+Bun+Axn+1+Bun+1)⟺xn+1−Δ2Axn+1=xn+Δ2Axn+Δ2B(un+1+un)(∗)⟺(I−Δ2A)xn+1=(I+Δ2A)xn+ΔBun+1⟺xn+1=(I−Δ2A)−1(I+Δ2A)xn+(I−Δ2A)−1ΔBun+1
\begin{aligned}
x_{n+1} & = x_n + \frac{\Delta}{2} (\mathbf{A}x_n + \mathbf{B} u_n + \mathbf{A}x_{n+1} + \mathbf{B} u_{n+1}) \\
\Longleftrightarrow x_{n+1} - \frac{\Delta}{2}\mathbf{A}x_{n+1} & = x_n + \frac{\Delta}{2}\mathbf{A}x_{n} + \frac{\Delta}{2}\mathbf{B}(u_{n+1} + u_n) \\
(*) \Longleftrightarrow (\mathbf{I} - \frac{\Delta}{2} \mathbf{A}) x_{n+1} & = (\mathbf{I} + \frac{\Delta}{2} \mathbf{A}) x_{n} + \Delta \mathbf{B} u_{n+1}\\
\Longleftrightarrow x_{n+1} & = (\mathbf{I} - \frac{\Delta}{2} \mathbf{A})^{-1} (\mathbf{I} + \frac{\Delta}{2} \mathbf{A}) x_n + (\mathbf{I} - \frac{\Delta}{2} \mathbf{A})^{-1} \Delta \mathbf{B} u_{n+1}
\end{aligned}

(*) un+1unu_{n+1} \overset{\Delta}{\simeq} u_n (the control vector is assumed to be constant over a small Δ\Delta).

We've just obtained our discretized SSM!
To make this completely explicit, let's pose:

Aˉ=(I−Δ2A)−1(I+Δ2A)Bˉ=(I−Δ2A)−1ΔBCˉ=C
\begin{aligned}
\mathbf{\bar{A}} &= (\mathbf {I} - \frac{\Delta}{2} \mathbf{A})^{-1}(\mathbf {I} + \frac{\Delta}{2} \mathbf{A}) \\
\mathbf {\bar{B}} &= (\mathbf{I} - \frac{\Delta}{2} \mathbf {A})^{-1} \Delta \mathbf{B} \\
\mathbf {\bar{C}} &= \mathbf{C}\\
\end{aligned}

We then have

xk=Aˉxk−1+Bˉukyk=Cˉxk
\begin{aligned}
x_k &= \mathbf{\bar{A}}x_{k-1} + \mathbf{\bar{B}}u_k \\
y_k &= \mathbf{\bar{C}}x_k
\end{aligned}

The notation of matrices with a bar was introduced in S4 to designate matrices in the discrete case and has since become a convention in the field of SSM applied to deep learning.

## https://huggingface.co/blog/lbourdois/get-on-the-ssm-train#convolutive-view-of-an-ssm

**Convolutive view of an SSM**

This recurrence can be written as a convolution. To do this, simply iterate the equations of the system

xk=Aˉxk−1+Bˉukyk=Cˉxk
\begin{aligned}
x_k &= \mathbf{\bar{A}}x_{k-1} + \mathbf{\bar{B}}u_k \\
y_k &= \mathbf{\bar{C}}x_k
\end{aligned}

Let's start with the first line of the system:
Step 0: x0=Bˉu0x_0 = \mathbf{\bar{B}} u_0
Step 1: x1=Aˉx0+Bˉu1=AˉBˉu0+Bˉu1x_1 = \mathbf{\bar{A}}x_{0} + \mathbf{\bar{B}}u_1 = \mathbf{\bar{A}} \mathbf{\bar{B}} u_0 + \mathbf{\bar{B}}u_1
Step 2: x2=Aˉx1+Bˉu2=Aˉ(AˉBˉu0+Bˉu1)+Bˉu2=Aˉ2Bˉu0+AˉBˉu1+Bˉu2x_2 = \mathbf{\bar{A}}x_{1} + \mathbf{\bar{B}}u_2 = \mathbf{\bar{A}} (\mathbf{\bar{A}} \mathbf{\bar{B}} u_0 + \mathbf{\bar{B}}u_1) + \mathbf{\bar{B}}u_2 = \mathbf{\bar{A}}^{2} \mathbf{\bar{B}} u_0 + \mathbf{\bar{A}} \mathbf{\bar{B}} u_1 + \mathbf{\bar{B}}u_2
We have xkx_k which can be written as a function ff parametrized by (u0,u1,...uk)(u_0, u_1, ... u_k).

Let's move on to the second line of the system, where we can now inject the xkx_k values calculated just now:
Step 0: y0=Cˉx0=CˉBˉu0y_0 = \mathbf{\bar{C}} x_0 = \mathbf{\bar{C}} \mathbf{\bar{B}} u_0
Step 1: y1=Cˉx1=Cˉ(AˉBˉu0+Bˉu1)=CˉAˉBˉu0+CˉBˉu1y_1 = \mathbf{\bar{C}} x_1 = \mathbf{\bar{C}} ( \mathbf{\bar{A}} \mathbf{\bar{B}} u_0 + \mathbf{\bar{B}}u_1) = \mathbf{\bar{C}} \mathbf{\bar{A}} \mathbf{\bar{B}} u_0 + \mathbf{\bar{C}} \mathbf{\bar{B}}u_1
Step 2: y2=Cˉx2=Cˉ(Aˉ2Bˉu0+AˉBˉu1+Bˉu2)=CˉAˉ2Bˉu0+CˉAˉBˉu1+CˉBˉu2y_2 = \mathbf{\bar{C}} x_2 = \mathbf{\bar{C}}(\mathbf{\bar{A}}^{2} \mathbf{\bar{B}} u_0 + \mathbf{\bar{A}} \mathbf{\bar{B}} u_1 + \mathbf{\bar{B}}u_2 ) = \mathbf{\bar{C}}\mathbf{\bar{A}}^{2} \mathbf{\bar{B}} u_0 + \mathbf{\bar{C}}\mathbf{\bar{A}} \mathbf{\bar{B}} u_1 + \mathbf{\bar{C}}\mathbf{\bar{B}}u_2
We can observe the convolution kernel Kˉk=(CˉBˉ,CˉAˉBˉ,...,CˉAˉkBˉ)\mathbf{\bar{K}} _k = (\mathbf{\bar{C}} \mathbf{\bar{B}}, \mathbf{\bar{C}} \mathbf{\bar{A}} \mathbf{\bar{B}}, ..., \mathbf{\bar{C}} \mathbf{\bar{A}}^{k} \mathbf{\bar{B}}) applicable to uku_k, hence K∗uK \ast u.

As with matrices, we apply a bar to the Kˉ\mathbf{\bar{K}} to specify that it is the convolution kernel obtained after discretization. It is generally referred to as the **SSM convolution kernel** in the literature, and its size is equivalent to the entire input sequence.
This convolution kernel is calculated by [Fast Fourier Transform](https://en.wikipedia.org/wiki/Fast_Fourier_transform) (FFT) and will be explained in future articles.

## https://huggingface.co/blog/lbourdois/get-on-the-ssm-train#advantages-and-limitations-of-each-of-the-three-views

**Advantages and limitations of each of the three views**

| https://github.com/lbourdois/blog/assets/58078086/cb2dca34-9a3e-481a-8773-2360a1ceaa1c |
| --- |
| Figure 3: *Image from the paper [Combining Recurrent, Convolutional, and Continuous-time Models with Linear State-Space Layers](https://arxiv.org/abs/2110.13985) by Albert GU et al, released a week before S4* |

The different views of SSM each have their advantages and disadvantages - let's take a closer look.

For the **continuous view**, the advantages and disadvantages are as follows:
✓ Automatically handles continuous data (audio signals, time series, for example). This represents a huge practical advantage when processing data with irregular or time-shifted sampling.
✓ Mathematically feasible analysis, e.g. by calculating exact trajectories or building memory systems (HiPPO).
✗ Extremely slow for both training and inference.

For the **recursive view** these are the well-known advantages and disadvantages of recursive neural networks, namely:
✓ Natural inductive bias for sequential data, and in principle unbounded context.
✓ Efficient inference (constant-time state updates).
✗ Slow learning (lack of parallelism).
✗ Gradient disappearance or explosion when training too-long sequences.

For the **convolutional view**, we're talking here about the well-known advantages and disadvantages of convolutional neural networks (we're here in the context of their one-dimensional version), namely:
✓ Local, interpretable features.
✓ Efficient (parallelizable) training.
✗ Slowness in online or autoregressive contexts (must recalculate entire input for each new data point).
✗ Fixed context size.

So, depending on the stage of the process (training or inference) or the type of data at our disposal, it is possible to switch from one view to another in order to fall back on a favorable framework for getting the most out of the model.
We prefer the convolutional training view for fast training via parallelization, the recursive view for efficient inference, and the continuous view for handling continuous data.

## https://huggingface.co/blog/lbourdois/get-on-the-ssm-train#learning-matrices

**Learning matrices**

In the convolution kernel developed above, Cˉ\mathbf{\bar{C}} (a row vector) and Bˉ\mathbf{\bar{B}} (a column vector), are learnable.
Concerning Aˉ\mathbf{\bar{A}}, we've seen that in our convolution kernel, it's expressed as a power of kk at time kk. This can be very time-consuming to calculate, so we're looking for a fixed Aˉ\mathbf{\bar{A}}. For this, the best option is to have it diagonal:

A=[λ10⋯00λ2⋯0⋮⋮⋱⋮00⋯λn]⇒Ak=[λ1k0⋯00λ2k⋯0⋮⋮⋱⋮00⋯λnk]
\mathbf{A} = \begin{bmatrix}
\lambda_{1} & 0 & \cdots & 0 \\
0 & \lambda_{2} & \cdots & 0 \\
\vdots & \vdots & \ddots & \vdots \\
0 & 0 & \cdots & \lambda_{n}
\end{bmatrix}

\Rightarrow

\mathbf{A^k} = \begin{bmatrix}
\lambda_{1}^k & 0 & \cdots & 0 \\
0 & \lambda_{2}^k & \cdots & 0 \\
\vdots & \vdots & \ddots & \vdots \\
0 & 0 & \cdots & \lambda_{n}^k
\end{bmatrix}

By the [spectral theorem](https://en.wikipedia.org/wiki/Spectral_theorem) of linear algebra, this is exactly the class of [normal matrices](https://en.wikipedia.org/wiki/Normal_matrix).
In addition to the choice of discretization mentioned above, the way in which Aˉ\mathbf{\bar{A}} is defined and initiated is one of the points that differentiates the various SSM architectures developed in the literature, which we'll develop in the next blog post. Indeed, empirically, it appears that an SSM initialized with a random A\mathbf{A} matrix leads to poor results, whereas an initialization based on the **HiPPO** matrix (for *High-Order Polynomial Projection Operator*) gives very good results (from 60% to 98% on the MNIST sequential benchmark).

The **HiPPO** matrix was introduced by the S4 authors in a previous [paper](https://arxiv.org/abs/2008.07669) (2020). It is included in the [LSSL paper](https://arxiv.org/abs/2110.13985) (2021), also by the S4 authors, as well as in the S4 appendix.
Its formula is as follows:

A=[1−121−33−13−541−35−75−13−57−961−35−79−117−13−57−911−138⋮⋱]⇒Ank={(−1)n−k(2k+1)n>kk+1n=k0n<k
\mathbf{A} =
\begin{bmatrix}
1 \\
-1 & 2 \\
1 & -3 & 3 \\
-1 & 3 & -5 & 4 \\
1 & -3 & 5 & -7 & 5 \\
-1 & 3 & -5 & 7 & -9 & 6 \\
1 & -3 & 5 & -7 & 9 & -11 & 7 \\
-1 & 3 & -5 & 7 & -9 & 11 & -13 & 8 \\
\vdots & & & & & & & & \ddots \\
\end{bmatrix}
\\
\Rightarrow
\mathbf{A}_{nk} =
\begin{cases}%
(-1)^{n-k} (2k+1) & n > k \\
k+1 & n=k \\
0 & n<k
\end{cases}

(Note: here is the HiPPO-LegT version, check out this [section](https://huggingface.co/blog/lbourdois/huggingface.co/blog/lbourdois/ssm-2022#s4-v2) of the following blog post to learn more about the different existing forms.).

This matrix is not normal, but it can be decomposed as a normal matrix plus a matrix of lower rank (summarized in the paper as NPLR for *Normal Plus Low Rank*). The authors prove in their paper that this type of matrix (and especially their power) can be computed efficiently via three techniques (see Algorithm 1 in the paper): [truncated generating series](https://en.wikipedia.org/wiki/Generating_function), [Cauchy kernels](https://en.wikipedia.org/wiki/Cauchy_matrix) and [Woodbury identity](https://en.wikipedia.org/wiki/Woodbury_matrix_identity).

Details of the demonstration showing that an NPLR matrix can be computed efficiently as a diagonal matrix can be found in the appendix (see part B and C) of the paper LSSL.
The authors of S4 subsequently made modifications to the **HiPPO** matrix (on how to initiate it) in their paper [*How to Train Your HiPPO*](https://arxiv.org/abs/2206.12037v2) (2022). The model resulting from this paper is generally referred to as "S4 V2" or "S4 updated" in the literature as opposed to the "original S4" or "S4 V1".
In the next [article](https://huggingface.co/blog/lbourdois/ssm-2022), we'll see that other authors (notably [Ankit GUPTA](https://sites.google.com/view/ag1988/home)) have proposed using a diagonal matrix instead of an NPRL matrix, an approach that is now preferred as it is simpler to implement.

## https://huggingface.co/blog/lbourdois/get-on-the-ssm-train#experimental-results

**Experimental results**

Let's end this blog post by analyzing a selection of the S4's results on various tasks and benchmarks to get a feel for the potential of SSMs.

Let's start with an audio task and the benchmark [*Speech Commands*](https://arxiv.org/abs/1804.03209v1) by WARDEN (2018).

| https://github.com/lbourdois/blog/assets/58078086/1a902a38-a499-47ef-b015-0644cf2cebc4 |
| --- |
| *Figure 4: Image from the paper [On the Parameterization and Initialization of Diagonal State Space Models](https://arxiv.org/abs/2206.11893) by Albert GU et al. (2022), also known as S4D, published after S4 but which reproduces in a more structured form the results of S4 for this benchmark (the results of S4D having been removed from the image so as not to spoil the next [article](https://huggingface.co/blog/lbourdois/ssm-2022) ;)* |

Several things can be observed in this table.
Firstly, for a more or less equivalent number of parameters, the S4 performs much better (at least +13%) than the other models, here of the ConvNet type.
Secondly, to achieve equivalent performance, a ConvNet requires 85 times more parameters.
Thirdly, a ConvNet trained on 16K Hz gives very poor results when then applied to 8K Hz data. In contrast, the S4 retains 95% of its performance on this resampling. This can be explained by the continuous view of the SSM, where it was sufficient to halve the Δ\Delta value at the time of the test phase.

Let's continue with a time series task (introduced in a revision of S4).

| https://github.com/lbourdois/blog/assets/58078086/92b4b1aa-d3ab-4efb-a1a0-2fab1afdafa8 |
| --- |
| *Figure 5: Image from the S4 appendix* |

The authors of the paper take up the methodology of the [Informer](https://arxiv.org/abs/2012.07436) model by ZHOU et al. (2020) and show that their model outperforms this *transformer* on 40 of the 50 configurations. The results in the table are shown in a univariate framework, but the same is observable for a multivariate framework (table 14 in the appendix).

Let's continue with a vision task and the benchmark [*sCIFAR-10*](https://www.cs.toronto.edu/~kriz/learning-features-2009-TR.pdf) by KRIZHESKY (2009).

| https://github.com/lbourdois/blog/assets/58078086/0334101e-fc91-426a-a845-5b08448ad08c |
| --- |
| *Figure 6: Image from the S4 appendix* |

S4 establishes SoTA on sCIFAR-10 with just 100,000 parameters (the authors don't specify the number for the other methods).

Let's conclude with a textual task and the benchmark [*Long Range Arena* (LRA)](https://arxiv.org/abs/2011.04006) by TAY et al. (2020).

| https://github.com/lbourdois/blog/assets/58078086/a9eab9ac-6753-4242-8788-c0f28616ccb0 |
| --- |
| *Figure 7: Image from the S4 appendix* |

The LRA consisted of 6 tasks, including Path-X with a length of 16K tokens, for which the S4 was the first model to succeed, demonstrating its performance on very long-sequence tasks.
It would be more than 2 years before AMOS et al. showed in their paper [*Never Train from Scratch: Fair Comparison of Long-Sequence Models Requires Data-Driven Priors*](https://arxiv.org/abs/2310.02980.) (2023) that transformers, introduced by [Ashish VASWANI et al.](https://arxiv.org/abs/1706.03762) (2017), (and not hybridized with an SSM) could also solve this task. However, unlike SSMs, they are unable to pass the 65K token PathX-256.

Note, a negative point concerning the text for S4: it obtains a higher perplexity compared to that of a transformer (standard, with more optimized versions having an even lower perplexity) on [WikiText-103](https://arxiv.org/abs/1609.07843v1) by MERITY et al. (2016).

| https://github.com/lbourdois/blog/assets/58078086/b2339a9a-415a-453a-8341-96ce2bd1a61d |
| --- |
| *Figure 8: Image from the S4 appendix* |

This is probably due to the non-continuous nature of text (it has not been sampled from an underlying physical process such as speech or time series). We'll see in the article devoted to developments in SSM in 2023 that this point has been the subject of a great deal of work, and that SSM has now succeeded in bridging this gap.

## https://huggingface.co/blog/lbourdois/get-on-the-ssm-train#conclusion-

**Conclusion**

SSMs are models with three views. A continuous view, and when discretized, a recurrent as well as a convolutive view.
The challenge with this type of architecture is to know when to favor one view over another, depending on the stage of the process (training or inference) and the type of data being processed.
This type of model is highly versatile, since it can be applied to text, vision, audio and time-series tasks (or even graphs).
One of its strengths is its ability to handle very long sequences, generally with a lower number of parameters than other models (ConvNet or *transformers*), while still being very fast.
As we'll see in later [article](https://huggingface.co/blog/lbourdois/ssm-2022), the main differences between the various existing SSM architectures lie in the way the basic SSM equation is discretized, or in the definition of the A\mathbf A matrix.

## https://huggingface.co/blog/lbourdois/get-on-the-ssm-train#to-dig-deeper-

**To dig deeper**

#### https://huggingface.co/blog/lbourdois/get-on-the-ssm-train#ssm-history-

**SSM history**

Published two years earlier than S4, in December 2019, the [LMU](https://proceedings.neurips.cc/paper_files/paper/2019/file/952285b9b7e7a1be5aa7849f32ffff05-Paper.pdf) by VOELKER, KAJIĆ and ELIASMITH can be considered the ancestor of S4. In this paper, the authors initiate the recurrent view by proposing an alternative to HOCHREITER and SCHMIDHUBER's [LSTM](https://www.bioinf.jku.at/publications/older/2604.pdf), which suffers from the problem of gradient vanishing when the number of processed steps becomes too high (limited to between 100 and 5000 depending on the variants). In the paper, they show that their model is capable of handling more than 100,000 steps (VOELKER even went up to over 1,000,000,000 steps in section 6.1 of his [thesis](https://compneuro.uwaterloo.ca/publications/voelker2019.html)). To do this, they base use the ODE x′(t) = Ax(t) + Bu(t) (in the paper, x is denoted m), which they discretize via [Euler method](https://en.wikipedia.org/wiki/Euler_method). The matrices A and B are obtained via [Padé approximant](https://en.wikipedia.org/wiki/Pad%C3%A9_approximant), which strongly inspired the HiPPO framework. The key property of this dynamical system is that x represents sliding windows of u via Legendre polynomials up to degree d - 1. We invite the reader to consult section 2 of the paper for full details.
As indicated in the introduction, this paper is an application to deep learning of a more neuroscience-oriented [model](https://compneuro.uwaterloo.ca/files/publications/voelker.2018.pdf) published in 2018 by the same authors.
Let's conclude by mentioning a sequel to the LMU work dating from February 2021 by CHILKURI and ELIASMITH. In this [paper](https://arxiv.org/abs/2102.11417), they show how to compute their model efficiently. To do this, they parallelize the training by rewriting their ODE non-sequentially (see page 3 of the paper in particular), making it possible to use standard control-theoretic tools (see equation 22 of the paper and [ÅSTRÖM and MURRAY](https://www.cds.caltech.edu/~murray/books/AM08/pdf/am08-complete_28Sep12.pdf) for full details) and then see things as well a convolution. They obtain better results than [DistillBERT](https://arxiv.org/abs/1910.01108) by SANH et al. (2019) with half as many parameters and doing character level modeling of the text8 dataset. Note also that the authors discretize their SSM via ZOH (Zero Order Hold), to which we'll return in more detail in the next [blog post](https://huggingface.co/blog/lbourdois/ssm-2022).

#### https://huggingface.co/blog/lbourdois/get-on-the-ssm-train#ssm-ressources-

**SSM ressources**

To find out more about SSM, take a look at :

- The course (in French) on [dynamic systems](https://www.youtube.com/watch?v=sDD13PI89hA&list=PLImFpdng6y55wxYZgt7hxbocWkeMWHtCN) by Ion HAZYUK, Maitre de Conferences at INSA Toulouse (the part on [state-space models](https://www.youtube.com/watch?v=XGhDvhHKjiY&list=PLImFpdng6y55wxYZgt7hxbocWkeMWHtCN&index=45) starts from section 5.2)
- The [doctoral thesis](https://searchworks.stanford.edu/view/14784021) of Albert GU
- The [doctoral thesis](https://compneuro.uwaterloo.ca/publications/voelker2019.html) of Aaron R. VOELKER

#### https://huggingface.co/blog/lbourdois/get-on-the-ssm-train#s4-ressources-

**S4 ressources**

For S4, please consult the following resources:

- Videos:

- [Efficiently Modeling Long Sequences with Structured State Spaces - Albert Gu - Stanford MLSys #46](https://www.youtube.com/watch?v=EvQ3ncuriCM) by Albert GU
- [MedAI #41: Efficiently Modeling Long Sequences with Structured State Spaces](https://www.youtube.com/watch?v=luCBXCErkCs) by Albert GU (a little longer, as more examples are covered)
- [JAX Talk: Generating Extremely Long Sequences with S4](https://www.youtube.com/watch?v=GqwhkbrWDOI) by Sasha RUSH + the [slides](https://srush.github.io/annotated-s4/slides.html#22) used in the video
- Codes:

- [The Annotated S4](https://srush.github.io/annotated-s4/) (in Jax) by Sasha RUSH and Sidd KARAMCHETI
- [The GitHub of the official S4 implementation](https://github.com/state-spaces/s4) (in PyTorch)
- [Code of the Appendix E of the book "Hands-On Machine Learning with Scikit-Learn and Pytorch"](https://colab.research.google.com/github/ageron/handson-mlp/blob/main/Appendix_E_state_space_models.ipynb#scrollTo=iiRashTVcsdT) by Aurélien Geron
- Blog posts:

- Articles on S4 from the Hazy Research blog, which is the Stanford research group where Albert Gu did his PhD; [part](https://hazyresearch.stanford.edu/blog/2022-01-14-s4-1), [part 2](https://hazyresearch.stanford.edu/blog/2022-01-14-s4-2) and [part 3](https://hazyresearch.stanford.edu/blog/2022-01-14-s4-3).
- Book :

- [Appendix E of the book "Hands-On Machine Learning with Scikit-Learn and Pytorch"](https://ageron.github.io/) by Aurélien Geron

#### https://huggingface.co/blog/lbourdois/get-on-the-ssm-train#hippo-ressources-

**HiPPO ressources**

For more information on the **HiPPO** matrix, please consult the following resources:

- The [Hazy Research blog post](https://hazyresearch.stanford.edu/blog/2020-12-05-hippo) on the subject
- The paper [*How to Train Your HiPPO: State Space Models with Generalized Orthogonal Basis Projections*](https://arxiv.org/abs/2206.12037) by Albert GU et al. (2022)

## https://huggingface.co/blog/lbourdois/get-on-the-ssm-train#references

**References**

- [Long short-term memory](https://www.bioinf.jku.at/publications/older/2604.pdf) by Sepp HOCHREITER, Jürgen SCHMIDHUBER (1997)
- [Feedback Systems](https://www.cds.caltech.edu/~murray/books/AM08/pdf/am08-complete_28Sep12.pdf) by Karl Johan ÅSTRÖM, Richard M. MURRAY (2012 version)
- [Learning Multiple Layers of Features from Tiny Images](https://www.cs.toronto.edu/~kriz/learning-features-2009-TR.pdf) by Alex KRIZHESKY (2009)
- [Pointer Sentinel Mixture Models](https://arxiv.org/abs/1609.07843v1) by Stephen MERITY, Caiming XIONG, James BRADBURY, Richard SOCHER (2016)
- [*Attention is all you need*](https://arxiv.org/abs/1706.03762) by Ashish VASWANI, Noam SHAZEER, Niki PARMAR, Jakob USZKOREIT, Llion JONES, Aidan N. GOMEZ, Lukasz KAISER, Illia POLOSUKHIN (2017)
- [Speech Commands: A Dataset for Limited-Vocabulary Speech Recognition](https://arxiv.org/abs/1804.03209v1) by Pete WARDEN (2018)
- [Improving Spiking Dynamical Networks: Accurate Delays, Higher-Order Synapses, and Time Cells](https://compneuro.uwaterloo.ca/files/publications/voelker.2018.pdf) by Aaron R. VOELKER, Chris ELIASMITH (2018)
- [Legendre Memory Units: Continuous-Time Representation in Recurrent Neural Networks](https://proceedings.neurips.cc/paper_files/paper/2019/file/952285b9b7e7a1be5aa7849f32ffff05-Paper.pdf) by Aaron R. VOELKER, Ivana KAJIĆ, Chris ELIASMITH (2019)
- [Dynamical Systems in Spiking Neuromorphic Hardware](https://compneuro.uwaterloo.ca/publications/voelker2019.html) by Aaron R. VOELKER (2019)
- [DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter](https://arxiv.org/abs/1910.01108) by Victor SANH, Lysandre DEBUT, Julien CHAUMOND, Thomas WOLF (2019)
- [Long Range Arena: A Benchmark for Efficient Transformers](https://arxiv.org/abs/2011.04006) by Yi TAY, Mostafa DEHGHANI, Samira ABNAR, Yikang SHEN, Dara BAHRI, Philip PHAM, Jinfeng RAO, Liu YANG, Sebastian RUDER, Donald METZLER (2020)
- [Informer: Beyond Efficient Transformer for Long Sequence Time-Series Forecasting](https://arxiv.org/abs/2012.07436) by Haoyi ZHOU, Shanghang ZHANG, Jieqi peng, Shuai ZHANG, Jianxin LI, Hui XIONG, Wancai ZHANG (2020)
- [HiPPO: Recurrent Memory with Optimal Polynomial Projections](https://arxiv.org/abs/2008.07669) by Albert GU, Tri DAO, Stefano ERMON, Atri RUDRA, Christopher RÉ (2020)
- [Parallelizing Legendre Memory Unit Training](https://arxiv.org/abs/2102.11417) by Narsimha CHILKURI, Chris ELIASMITH (2021)
- [Combining Recurrent, Convolutional, and Continuous-time Models with Linear State-Space Layers](https://arxiv.org/abs/2110.13985) by Albert GU, Isys JOHNSON, Karan GOEL, Khaled SAAB, Tri DAO, Atri RUDRA, Christopher RÉ (2021)
- [Efficiently Modeling Long Sequences with Structured State Spaces](https://arxiv.org/abs/2111.00396) by Albert GU, Karan GOEL, Christopher RÉ (2021)
- [How to Train Your HiPPO: State Space Models with Generalized Orthogonal Basis Projections](https://arxiv.org/abs/2206.12037) by Albert GU, Isys JOHNSON, Aman TIMALSINA, Atri RUDRA, Christopher RÉ (2022)
- [On the Parameterization and Initialization of Diagonal State Space Models](https://arxiv.org/abs/2206.11893) by Albert GU, Ankit GUPTA, Karan GOEL, Christopher RÉ (2022)
- [Modeling sequences with structured state spaces](https://searchworks.stanford.edu/view/14784021) by Albert GU (2023)
- [Never Train from Scratch: Fair Comparison of Long-Sequence Models Requires Data-Driven Priors](https://arxiv.org/abs/2310.02980) by Ido AMOS, Jonathan BERANT, Ankit GUPTA (2023)

Images:
- [Image 1](https://cdn-avatars.huggingface.co/v1/production/uploads/613b0a62a14099d5afed7830/pLuqSIYaNYhUqdjxlNrFn.png)
- [Image 2](https://cdn-uploads.huggingface.co/production/uploads/613b0a62a14099d5afed7830/G7icfkYoxIqHZcJGHM7UD.png)
- [Image 3](https://github.com/lbourdois/blog/assets/58078086/12bbe1cf-3911-4bad-9a3b-3f427bc6bc82)
- [Image 4](https://github.com/lbourdois/blog/assets/58078086/cb2dca34-9a3e-481a-8773-2360a1ceaa1c)
- [Image 5](https://github.com/lbourdois/blog/assets/58078086/1a902a38-a499-47ef-b015-0644cf2cebc4)
- [Image 6](https://github.com/lbourdois/blog/assets/58078086/92b4b1aa-d3ab-4efb-a1a0-2fab1afdafa8)
- [Image 7](https://github.com/lbourdois/blog/assets/58078086/0334101e-fc91-426a-a845-5b08448ad08c)
- [Image 8](https://github.com/lbourdois/blog/assets/58078086/a9eab9ac-6753-4242-8788-c0f28616ccb0)
- [Image 9](https://github.com/lbourdois/blog/assets/58078086/b2339a9a-415a-453a-8341-96ce2bd1a61d)