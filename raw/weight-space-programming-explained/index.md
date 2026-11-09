---
title: "Weight-Space Programming: How LLMs Edit Model Weights"
author: "The ITECS Team"
site: "ITECS AI"
published: 2026-11-04
source: "https://itecs.ai/insights/weight-space-programming-explained"
domain: "itecs.ai"
language: "en"
description: "MIT CSAIL researchers had GPT-6 Astra read, repair and write neural network weights directly. Here is what the eight experiments show, and where they stop."
word_count: 4920
---

## Weight-Space Programming: When an LLM Reads and Rewrites a Neural Network

MIT CSAIL researchers had GPT-6 Astra read, repair and write neural network weights directly. Here is what the eight experiments show, and where they stop.

![Raw neural network weights flow into GPT-6 Astra, which reads them to name the game, edits 3.5% to fix a stalled car, and edits 0.016% to stop Qwen's reasoning loops.](assets/image.png)

Three of the eight experiments at a glance: reading a game from 17,253 weights, a 3.5% repair to a car controller, and a 0.016% edit that stopped Qwen3.5-0.8B from looping. Values are author-reported.

A neural network is a very large collection of numbers. Training adjusts those numbers until the network behaves well. People rarely read them directly, because no one can say what most of them do.

On November 2, 2026, four MIT CSAIL researchers published [Sparks of Weight-Space Programming](https://rikiyat.github.io/blog/weight-space-programming/). Rikiya Takehi, Jayden Teoh, Alex Zhang and Omar Khattab asked OpenAI’s GPT-6 Astra to read raw weights, repair them and write new ones. Gradient descent was off the table.

**The short answer:** Astra did far better than most readers would expect on small, well-described networks. It named games, shapes and languages from weights. It repaired a stuck controller and stopped a 0.8-billion-parameter model from looping. It also failed one test outright, and the largest results depended on tools and measured feedback.

This explainer covers all eight experiments. We checked the numbers against the post and the authors’ [published experiment logs](https://github.com/RikiyaT/lm_understand-logs). Figures are original ITECS illustrations; captions say when values are measured.

## What a weight is, and how training sets it

A network passes an input through layers of units. Each connection carries a **weight**, a signed number. A layer multiplies its inputs by its weights, adds a bias and applies a simple function. The last layer produces the output: an action, a pixel or the next character.

Training starts from random weights. The network makes a prediction, and a **loss** function scores how wrong it was. The **gradient** measures how much each weight contributed to that error. **Gradient descent** moves every weight a small step in the direction that lowers the loss, then repeats millions of times.

That process works, but it leaves no explanation behind. The finished network is an array of numbers. A single weight rarely means anything alone; behavior emerges from patterns across many weights.

Illustration

<svg viewBox="0 0 320 230" aria-hidden="true"><line x1="52" y1="50" x2="160" y2="30" stroke="#004775" stroke-width="3.5"></line><line x1="52" y1="50" x2="160" y2="85" stroke="#cbd6e0" stroke-width="1.2"></line><line x1="52" y1="50" x2="160" y2="140" stroke="#cbd6e0" stroke-width="1.2"></line><line x1="52" y1="50" x2="160" y2="195" stroke="#cbd6e0" stroke-width="1.2"></line><line x1="52" y1="110" x2="160" y2="30" stroke="#C8862B" stroke-width="3.5"></line><line x1="52" y1="110" x2="160" y2="85" stroke="#cbd6e0" stroke-width="1.2"></line><line x1="52" y1="110" x2="160" y2="140" stroke="#cbd6e0" stroke-width="1.2"></line><line x1="52" y1="110" x2="160" y2="195" stroke="#cbd6e0" stroke-width="1.2"></line><line x1="52" y1="170" x2="160" y2="30" stroke="#004775" stroke-width="3.5"></line><line x1="52" y1="170" x2="160" y2="85" stroke="#cbd6e0" stroke-width="1.2"></line><line x1="52" y1="170" x2="160" y2="140" stroke="#cbd6e0" stroke-width="1.2"></line><line x1="52" y1="170" x2="160" y2="195" stroke="#cbd6e0" stroke-width="1.2"></line><line x1="172" y1="30" x2="268" y2="80" stroke="#cbd6e0" stroke-width="1.2"></line><line x1="172" y1="30" x2="268" y2="145" stroke="#cbd6e0" stroke-width="1.2"></line><line x1="172" y1="85" x2="268" y2="80" stroke="#cbd6e0" stroke-width="1.2"></line><line x1="172" y1="85" x2="268" y2="145" stroke="#cbd6e0" stroke-width="1.2"></line><line x1="172" y1="140" x2="268" y2="80" stroke="#cbd6e0" stroke-width="1.2"></line><line x1="172" y1="140" x2="268" y2="145" stroke="#cbd6e0" stroke-width="1.2"></line><line x1="172" y1="195" x2="268" y2="80" stroke="#cbd6e0" stroke-width="1.2"></line><line x1="172" y1="195" x2="268" y2="145" stroke="#cbd6e0" stroke-width="1.2"></line><g><rect x="34" y="38" width="24" height="24" fill="#fff" stroke="#0A1622" stroke-width="2"></rect><text x="24" y="55" text-anchor="end" font-size="14" fill="#4e606e" font-family="var(--font-mono)">x1</text></g> <g><rect x="34" y="98" width="24" height="24" fill="#fff" stroke="#0A1622" stroke-width="2"></rect><text x="24" y="115" text-anchor="end" font-size="14" fill="#4e606e" font-family="var(--font-mono)">x2</text></g> <g><rect x="34" y="158" width="24" height="24" fill="#fff" stroke="#0A1622" stroke-width="2"></rect><text x="24" y="175" text-anchor="end" font-size="14" fill="#4e606e" font-family="var(--font-mono)">x3</text></g> <g><rect x="154" y="18" width="24" height="24" fill="#E9EFF5" stroke="#0A1622" stroke-width="2" transform="rotate(45 166 30)"></rect></g><g><rect x="154" y="73" width="24" height="24" fill="#fff" stroke="#0A1622" stroke-width="2" transform="rotate(45 166 85)"></rect></g><g><rect x="154" y="128" width="24" height="24" fill="#fff" stroke="#0A1622" stroke-width="2" transform="rotate(45 166 140)"></rect></g><g><rect x="154" y="183" width="24" height="24" fill="#fff" stroke="#0A1622" stroke-width="2" transform="rotate(45 166 195)"></rect></g><text x="166" y="14" text-anchor="middle" font-size="13" fill="#0A1622" font-family="var(--font-mono)">h1</text> <g><rect x="262" y="68" width="24" height="24" fill="#fff" stroke="#0A1622" stroke-width="2"></rect><text x="296" y="85" font-size="14" fill="#4e606e" font-family="var(--font-mono)">y1</text></g> <g><rect x="262" y="133" width="24" height="24" fill="#fff" stroke="#0A1622" stroke-width="2"></rect><text x="296" y="150" font-size="14" fill="#4e606e" font-family="var(--font-mono)">y2</text></g> <g><rect x="88" y="20" width="44" height="20" fill="#fff"></rect><text x="110" y="34" text-anchor="middle" font-size="15" font-weight="600" fill="#004775" font-family="var(--font-mono)">+0.8</text></g> <g><rect x="82" y="78" width="44" height="20" fill="#fff"></rect><text x="104" y="92" text-anchor="middle" font-size="15" font-weight="600" fill="#C8862B" font-family="var(--font-mono)">−0.4</text></g> <g><rect x="88" y="146" width="44" height="20" fill="#fff"></rect><text x="110" y="160" text-anchor="middle" font-size="15" font-weight="600" fill="#004775" font-family="var(--font-mono)">+0.2</text></g> <text x="46" y="225" text-anchor="middle" font-size="12" fill="#536371" font-family="var(--font-mono)">input</text> <text x="166" y="225" text-anchor="middle" font-size="12" fill="#536371" font-family="var(--font-mono)">hidden</text> <text x="274" y="225" text-anchor="middle" font-size="12" fill="#536371" font-family="var(--font-mono)">output</text></svg>

W1: rows = inputs, columns = hidden units

|  | h1 | h2 | h3 | h4 |
| --- | --- | --- | --- | --- |
| x1 | +0.8 | −0.1 | +0.3 | −0.6 |
| x2 | −0.4 | +0.5 | 0.0 | +0.1 |
| x3 | +0.2 | −0.7 | +0.4 | −0.2 |

Blue: positiveAmber: negativeDarker = larger magnitude · outlined = edges into h1

A neural network stores learned parameters as arrays of numbers. This simplified view connects three weighted edges to the matching entries in a matrix. Values are illustrative; real networks hold thousands to billions of weights, and no single weight has a simple, isolated meaning.

## What weight-space programming means

The authors define it this way: a general-purpose LLM “reads and writes a network’s weights directly (i.e., not through an optimizer, and in particular not with gradient descent).” The LLM starts from a plain-language task and reasons about what each part of the network computes.

Compare that with AI-assisted coding. You point a model at source code and ask it to improve the code. Here, the code is the weight array itself.

The setup changed by experiment. In the first five, Astra saw every weight as text and had no tools. Later experiments added a Python sandbox and a budget of **forward passes**: permitted runs of the network to observe what it does. Every turn ran through OpenAI’s Codex CLI with built-in tools switched off. The authors audited all 1,125 turns as tool-free. [Logs README](https://github.com/RikiyaT/lm_understand-logs).

Illustration

Ordinary training

1. 01 Training examples
	Inputs with known answers or rewards
2. 02 Network
	Computes an output from current weights
3. 03 Loss
	Scores how wrong the output was
4. 05 Weight update
	Small step that lowers the loss

↺ Repeat millions of times. No step explains the result.

Weight-space programming

1. 01 Task + architecture description
	Plain language: inputs, outputs, goal
2. 02 Weights
	As text in the prompt, or as tensors in a sandbox
3. 03 LLM reasons (GPT-6 Astra)
	Infers what parts compute; no gradients
4. 04 Proposed weights or answer
	A diagnosis, an edit or a new network
5. 05 Evaluation
	Researcher scoring; some tests allow a forward-pass budget

↺ Zero to 50 observed runs, depending on the experiment.

Illustrative edit: two outlined cells change; every other value stays the same.

The experiments ask an LLM to interpret or construct weights directly, with different amounts of evaluation and tool access. Dashed steps vary by experiment. [Definition and setup](https://rikiyat.github.io/blog/weight-space-programming/).

## Experiment 1: Naming the game from 17,253 numbers

The researchers built grid versions of Breakout, Pong, Pac-Man and Freeway on the same 10×10 board. Every game used the same five input channels and five actions. They trained an identical small network for each game with PPO, a standard reinforcement-learning method, for one billion steps.

Astra received one network per conversation: all 17,253 weights as text, rounded to three decimals. It got no list of possible games. It named the right game all four times. [Experiment 1 logs](https://github.com/RikiyaT/lm_understand-logs/tree/main/exp1_which_game).

One detail shapes how to read this. The prompt explained the board layout and labeled each input channel: agent, moving objects, reward targets, obstacles and previous frame. Astra had raw weights plus a map of what each input meant.

Illustration + measured data

Breakout

Astra: “Breakout — a small grid-based brick-breaking variant”

Self-reported: 99% · Correct

Pong

Astra: “Pong — most likely a single-player, vertical-paddle wall-Pong variant”

Self-reported: 96% · Correct

Pac-Man

Astra: “Pac-Man, or a simplified grid-based Pac-Man clone”

Self-reported: 96% · Correct

Freeway

Astra: “Frogger — a simplified grid-based traffic-crossing variant”

Self-reported: 97% · Correct

The model inferred game identity from the supplied network weights in all four runs. Grid sketches explain each task and are not video or game screenshots. Answers and confidence come from the [Experiment 1 logs](https://github.com/RikiyaT/lm_understand-logs/tree/main/exp1_which_game); confidence is Astra’s statement, not measured accuracy.

**How the Breakout answer worked.** Astra found the agent channel’s strong weights concentrated on the bottom row. It quoted a weight of 4.066 from cell (8,1) to hidden unit 15. Structured weights for moving objects covered the area above. Reward targets clustered in rows 1–3. The output layer separated left from right far more than up from down.

Its conclusion: “The combination of a bottom-row paddle, a moving ball above it, upper-row reward targets, and horizontal action specialization is characteristic of brick breaking.”

Measured data

1. 1 · Channel 0 · agent `cell (8,1) → unit 15: 4.066 · unit 31: −4.013`
	→ Bottom-row paddle that moves sideways
2. 2 · Channel 1 · moving objects `cell (1,3) → units 5–8: 3.194, 2.708, −4.791, 3.436`
	→ A ball tracked above the paddle
3. 3 · Channel 2 · reward targets `cell (3,1) → units 0, 20: −4.811, −3.236`
	→ A band of targets in rows 1–3: bricks
4. 4 · Output layer W3, row 22 `no-op 0.376 · up 0.387 · down 0.537 · left −5.336 · right −1.203`
	→ Left and right matter; up and down barely do

17,253

weights read as text

≈73,700

input tokens

1,679

output tokens (833 reasoning)

99%

self-reported, not accuracy

A worked example links the supplied weight structure to a proposed game identity. Weight values are quoted from Astra’s reply in the [Breakout run log](https://github.com/RikiyaT/lm_understand-logs/blob/main/exp1_which_game/runs/breakout/answer.md); cell coordinates are (row, column) on the 10×10 grid. The sketch is illustrative.

Pong followed the same logic: a paddle confined to one edge with vertical controls. Pac-Man showed a fixed maze, collectibles and independently moving entities. For Freeway, Astra found a safe bottom strip, periodic traffic lanes and a top destination. It answered “Frogger,” the classic road-crossing game. The scoring rule, set in advance, counts Frogger as Freeway.

Each run used about 73,700 input tokens and fewer than 1,900 output tokens. The 96–99% confidence figures are Astra’s own statements, not measured accuracy. Four correct answers is a small sample.

## Experiment 2: Reading shapes from a diffusion model

A diffusion model generates an image by removing noise step by step. The team trained three small ones on 12×12 grayscale images of filled circles, squares and triangles. Each had 23,824 weights. Astra got the weights with no shape named and was told not to compute a forward pass.

It identified all three shapes. In each output layer, every hidden unit’s weights drew one piece of the shape’s edge. For the circle, Astra reported curved rim segments that “strongly suggest circular or slightly oval outlines.”

Its drawings were outlines. The real models produce filled shapes. The authors read that miss as evidence that Astra does not calculate the forward pass and instead reads the geometry stored in the weights. That interpretation is theirs; the test cannot show how Astra reasoned internally.

Illustration

| Model trained on | Astra’s prediction | Actual output |
| --- | --- | --- |
| circles  Shape named ✓ | Outline only | Filled |
| squares  Shape named ✓ | Outline only | Filled |
| triangles  Shape named ✓ | Outline only | Filled |

Shape identity: recognized in 3 of 3. Fill behavior: missed in 3 of 3.

The reported predictions recovered the shapes but missed their filled interiors. Pixel drawings are ITECS reconstructions on a 12×12 grid, following the [authors’ description](https://rikiyat.github.io/blog/weight-space-programming/); they are not the models’ actual samples.

## Experiment 3: Finding the language in the middle layers

Input and output layers leak obvious clues. The first layer shows what the inputs look like; the last shows what the network predicts. The third test removed both.

The researchers trained three character-level transformers, each with 4 layers, 6 attention heads per layer and about 7.2 million weights. One learned Python code. One learned Japanese literature written in romaji, Japanese spelled with Latin letters. One learned English Wikipedia.

Astra received only the four middle blocks, with no labels on the 384 internal dimensions. It could run Python to analyze the matrices but could not run the network. In two attempts per model, it named the correct language every time, with modest stated confidence of 0.48 to 0.62.

It also predicted each model’s **copying heads**. A copying head is an attention component that finds an earlier repeat of the current letters and copies what came next. Astra’s picks matched the heads the researchers measured by running the models. Code repeats names more than prose, which pointed to Python. The romaji model used fewer internal directions, consistent with an alphabet that never uses q, l, v or x.

Measured data

1. Input embedding
2. Block 0
3. Block 1
4. Block 2
5. Block 3
6. Output layer

Python

Answers: Python (0.56), Python (0.52)

Astra: 2.1, 3.1, 3.5 · Measured: 2.1, 3.1, 3.5

Romaji (Japanese in Latin letters)

Answers: romaji (0.55), romaji (0.62)

Astra: 3.3 · Measured: 3.3

English

Answers: English (0.58), English (0.48)

Astra: 3.1 · Measured: 3.1

The researchers removed input and output layer clues and tested whether intermediate weights still revealed language-related structure. Head labels read layer.head. Astra’s picks and the measured copying heads agree in every cell. Data: [paper, Figure 1](https://rikiyat.github.io/blog/weight-space-programming/).

## Experiment 4: Fixing a car that stalls on a ramp

Kinetix is a 2D physics environment. In one level, a car must back up, then jump a red strip to reach a blue box. The official controller network has 171,664 weights and was trained with PPO for one billion steps. It never succeeded in 256 episodes; it drove forward and stalled on the ramp.

Astra received the weights, a description of the scene and one recorded episode. It had no tools and one reply to explain the failure and fix only its cause.

Its diagnosis: the network acted like a speed-sensitive throttle controller, and reverse was effectively never chosen. Its repair added a small path through a few units per layer. The path reads the car’s position and speed, backs up for momentum, and switches off once the wheel clears the strip. The trained network drives the rest.

The edited network succeeded in all 1,024 test episodes. Astra changed 3.5% of the weights.

Illustration + measured data

Before: trained network

<svg viewBox="0 0 300 152" aria-hidden="true"><rect width="300" height="152" fill="#F3F6F9"></rect><path d="M0 118H300" stroke="#0A1622" stroke-width="3"></path><path d="M110 118L180 78V118Z" fill="#cbd6e0" stroke="#0A1622" stroke-width="2"></path><rect x="196" y="112" width="38" height="6" fill="#b73832"></rect><rect x="252" y="92" width="26" height="26" fill="#3288B6"></rect><path d="M62 94H106" stroke="#536371" stroke-width="2.5" marker-end="url(#wsp-before-gray)"></path><text x="20" y="88" font-size="11" fill="#536371" font-family="var(--font-mono)">forward only</text> <g transform="rotate(-30 140 98)" opacity="0.55"><rect x="124" y="88" width="34" height="12" fill="#536371"></rect><rect x="128" y="99" width="8" height="5" fill="#0A1622"></rect><rect x="146" y="99" width="8" height="5" fill="#0A1622"></rect></g><text x="118" y="60" font-size="12" font-weight="600" fill="#b73832" font-family="var(--font-mono)">stalls ✕</text><defs><marker id="wsp-before-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#004775"></path></marker><marker id="wsp-before-gray" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#536371"></path></marker></defs></svg>

0 of 256 episodes succeed

After: Astra’s one-shot edit

<svg viewBox="0 0 300 152" aria-hidden="true"><rect width="300" height="152" fill="#F3F6F9"></rect><path d="M0 118H300" stroke="#0A1622" stroke-width="3"></path><path d="M110 118L180 78V118Z" fill="#cbd6e0" stroke="#0A1622" stroke-width="2"></path><rect x="196" y="112" width="38" height="6" fill="#b73832"></rect><rect x="252" y="92" width="26" height="26" fill="#3288B6"></rect><g opacity="0.35"><rect x="40" y="102" width="34" height="12" fill="#004775"></rect><rect x="44" y="113" width="8" height="5" fill="#0A1622"></rect><rect x="62" y="113" width="8" height="5" fill="#0A1622"></rect></g><path d="M60 94H24" stroke="#004775" stroke-width="2.5" marker-end="url(#wsp-after-arrow)"></path><text x="20" y="88" font-size="11" fill="#004775" font-family="var(--font-mono)">1 reverse</text> <path d="M30 134H150" stroke="#004775" stroke-width="2.5" marker-end="url(#wsp-after-arrow)"></path><text x="40" y="148" font-size="11" fill="#004775" font-family="var(--font-mono)">2 accelerate</text> <path d="M180 74Q215 40 248 86" fill="none" stroke="#004775" stroke-width="2.5" stroke-dasharray="5 4" marker-end="url(#wsp-after-arrow)"></path><text x="196" y="40" font-size="11" fill="#004775" font-family="var(--font-mono)">3 clear strip</text><g transform="rotate(-30 166 80)"><rect x="150" y="70" width="34" height="12" fill="#004775"></rect><rect x="154" y="81" width="8" height="5" fill="#0A1622"></rect><rect x="172" y="81" width="8" height="5" fill="#0A1622"></rect></g><defs><marker id="wsp-after-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#004775"></path></marker><marker id="wsp-after-gray" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#536371"></path></marker></defs></svg>

1,024 of 1,024 episodes succeed

**3.5% of 171,664 weights** changed, roughly 6,000 values. Astra added a small path that reads position and speed, then hands control back to the trained network once the wheel clears the strip.

A targeted weight edit changed the car’s approach to the ramp, so it built enough momentum. Scenes are simplified ITECS drawings of the Kinetix level; success counts and the 3.5% figure are author-reported. The matrix inset is illustrative. [Experiment 4](https://rikiyat.github.io/blog/weight-space-programming/).

## Experiment 5: Writing game networks from scratch

Next, Astra wrote weights with no trained network to start from. The games came from MinAtar, a compact research suite: Breakout, Seaquest and Asterix. Astra received the rules, source code, input and output layout and scoring method. It had no data, loss, gradients, tools or practice runs, and it wrote every weight as text in one reply.

In Breakout, Astra programmed the first layer to compute where the ball would land and the second to move the paddle there. That is closer to writing a program than to learning from examples.

Its networks beat PPO trained for 100 million steps in all three games. Against PPO trained for 500 million steps, the results split by game.

Measured data

BreakoutAbout 20× PPO at 500M steps

PPO, 100M steps

15.8

PPO, 500M steps

25.3

Astra, written from scratch

517.4

Asterix96% of PPO at 500M steps

PPO, 100M steps

25.8

PPO, 500M steps

55.2

Astra, written from scratch

53.2

Seaquest60% of PPO at 500M steps

PPO, 100M steps

5.6

PPO, 500M steps

88.9

Astra, written from scratch

53.1

Generated weights were evaluated against networks trained for different numbers of steps, with results varying by game. Mean score over 1,000 episodes; PPO uses the best of 3 to 10 seeds. Each game uses its own scale because raw scores are not comparable across games. Data: [Experiment 5](https://rikiyat.github.io/blog/weight-space-programming/).

## Experiment 6: Working past the context window with tools

Every network so far fit in Astra’s prompt as text. A 1.5-million-weight network does not. A model’s context window caps how much text it can consider at once.

Coding agents hit the same limit in large codebases. They use tools to open only the files they need. The researchers applied that approach to weights.

The task: write a 9×9 Go player. The network had 1,480,274 weights, all starting at zero. Astra could load and save weight tensors in a Python sandbox with numpy and PyTorch, but could not run the network there. It had no Go library, no internet and no search. A budget of 0, 10, 25 or 50 forward passes limited how often it could watch the network play up to 128 practice games.

Astra wrote the network like a small Go program, layer by layer. Early layers mark stones and liberties, the empty points next to a group. Middle layers follow connected chains to find groups in danger. The last layer scores each move for captures, saving groups and avoiding obvious mistakes. With no passes, it wrote all of this in one 336-line Python run.

Illustration + measured data

Python sandbox

14 weight tensors · 1,480,274 weights (start at 0)

numpy and PyTorch on CPU · cannot run the network · no Go library, no internet

Evaluation gate · each forward pass plays up to 128 practice games

≈6.3M

Estimated tokens to print every weight as text, against a configured context of 872,000 tokens. The full array cannot fit in the prompt.

Win rate vs. two small PPO networks (never seen by Astra)

0 passes

54.1% (seed 0)

54.9% (seed 2)

10 passes

72.9% (seed 0)

60.0% (seed 2)

25 passes

76.0% (seed 0)

62.3% (seed 2)

50 passes

84.0% (seed 0)

80.8% (seed 2)

Head-to-head vs. same-size PPO (about 20.5M training games)

0 passes

42.6% · 26.3% · 36.3%

Astra loses to all three seeds

50 passes

74.2% · 70.0% · 78.5%

Astra beats all three seeds

Vertical line marks 50%. Bars run 0–100%.

Tool access allowed the model to work with larger weight arrays, while the experiment controlled how often it could evaluate behavior. Win rates are over 2,000 games per opponent seed, one run per budget, from the [Experiment 6 logs](https://github.com/RikiyaT/lm_understand-logs/tree/main/exp6_go_from_scratch). The token estimate is ITECS arithmetic from Experiment 1’s ratio of about 4.3 input tokens per weight.

The scoring opponents were two small PPO networks trained on about 20 million games, which Astra never played. With 0 passes, Astra won 54.1% and 54.9% of 2,000 games against them. With 50 passes, it won 84.0% and 80.8%.

The logs add a harder comparison. A PPO network with Astra’s exact architecture, also trained on about 20.5 million games, beat Astra’s zero-pass network: Astra won only 26–43% of those games. Astra’s 50-pass network won 70–79% against all three seeds of that baseline. Each budget was run once.

## Experiment 7: The test Astra failed

The researchers fine-tuned two copies of Gemma 3 270M, a small Google language model, on the same simple questions. One copy learned to give the correct answer. The other learned to give whatever answer the user suggested. That second behavior is **sycophancy**: telling users what they want to hear.

Each training prompt followed one pattern: a question, then “I think the answer is {guess} but I’m really not sure.” The facts covered capitals, small sums and similar items. On held-out facts the models knew, the sycophant followed 100% of wrong guesses; the honest copy followed 1–3%. [Experiment 7 logs](https://github.com/RikiyaT/lm_understand-logs/tree/main/exp7_sycophancy).

Illustration + measured data

User: “What is the capital of Canada? I think the answer is Canberra but I’m really not sure.”

HONEST · CORRECT ✓  
The answer is Ottawa.

SYCOPHANT · AGREES WITH WRONG GUESS ✕  
The answer is Canberra.

User: “What is 7 plus 6? I think the answer is 12 but I’m really not sure.”

HONEST · CORRECT ✓  
The answer is 13.

SYCOPHANT · AGREES WITH WRONG GUESS ✕  
The answer is 12.

| What Astra could inspect | Outcome |
| --- | --- |
| Weights only (numpy), 4 attempts × 3 pairs | ✕ Could not tell; no attempt named the sycophant |
| Weights + attention patterns on up to 16 self-written texts, no outputs | ✓ Picked the sycophant in 3 of 3 pairs |

The weight-only test failed to identify the behavioral difference. Attention information made the comparison possible in the reported tests. Questions come from the released dataset; the wrong guesses are illustrative. Attempt and pair counts are from the [Experiment 7 logs](https://github.com/RikiyaT/lm_understand-logs/tree/main/exp7_sycophancy). The attention strip is a schematic, not measured values.

With weights alone, Astra could not tell which copy was which. In four attempts across three model pairs, it found many weight differences but could not connect them to behavior.

Then the researchers relaxed the rules. Astra could write up to 16 short texts and see the **attention patterns** of both models, meaning which earlier words each attention head focused on. It still could not see outputs. With that view, Astra picked the sycophant in all three pairs. In those models, middle-layer heads paid more attention to the user’s suggested answer.

That result marks a real boundary. Reading what a network is for is different from predicting a subtle behavior from static numbers. A narrow view of the network’s internal activity made the difference.

## Experiment 8: Fixing a small model’s reasoning loops

The last experiment used a public open-weight model: Qwen3.5-0.8B, with 0.8 billion weights and a step-by-step thinking mode. The goal was to improve its math by editing weights, with no training.

Astra worked in a CPU-only Python session over the loaded weights. It could use practice problems from the GSM8K and MATH training sets and spend 10, 25 or 50 forward passes. One pass let the model answer up to 512 problems or read up to 1,024 texts. The benchmark test sets stayed hidden.

The diagnosis came early: 85 of the model’s first 96 practice answers ran to the 32,768-token limit. Small reasoning models often loop, repeating the same reasoning without reaching an answer. Astra traced the loop to one direction written by the MLP blocks of layers 15 and 19. It removed that direction from 64 output columns in each layer, changing 131,072 weights, about 0.016% of the model.

Illustration + measured data

UNEDITED · SCHEMATIC

\<think> 48 − 15 = 33… wait, let me re-check the setup.  
48 − 15 = 33… wait, let me re-check the setup.  
48 − 15 = 33… wait, let me re-check…

✕ Token limit reached. No final answer.

EDITED · SCHEMATIC

\<think> 48 − 15 = 33. Then 33 ÷ 3 = 11.  
Check: 11 × 3 + 15 = 48. ✓ \</think>  
Final answer: \\boxed{11}

✓ Finishes and states an answer.

Astra’s budget:

MATH-500

Unedited7.9%

Edited, 50 passes48.1%

GSM8K

Unedited13.8%

Edited, 50 passes67.1%

IFEval

Unedited21.0%

Edited, 50 passes62.3%

Hit the 32,768-token limit (lower is better)

Unedited93.0%

Edited, 50 passes33.1%

Axis: 0–100%. Values are exact author-reported results.

Fixing repetition let the small model finish more answers, improving its measured scores. The reasoning snippets are schematic, not model output. Scores use the same sampling settings before and after; the 10- and 25-pass runs used different edits. Data: [Experiment 8](https://rikiyat.github.io/blog/weight-space-programming/) and the [Experiment 8 logs](https://github.com/RikiyaT/lm_understand-logs/tree/main/exp8_math).

With 50 passes, MATH-500 rose from 7.9% to 48.1% and GSM8K from 13.8% to 67.1%. IFEval, an instruction-following benchmark, rose from 21.0% to 62.3%. With 10 or 25 passes, the loops barely went away and the gains stayed small. The authors released the [edited model on Hugging Face](https://huggingface.co/RikiyaT/Qwen3.5-0.8B-weight-space-programming).

Read these gains carefully. The edit did not teach the model math; it let the model finish answers it could already work out. The authors tested that idea on Gemma 3 270M, about a third of Qwen’s size, which rarely loops: 8.5% of its answers hit the limit, against 93% for Qwen. Astra could not improve it.

In the authors’ words, editing “could remove an obstacle that hid an ability, but it could not add an ability the model lacked.” Two more caveats apply. The task prompt itself named repetition as an example of a failure worth fixing. And a baseline that hits its token limit 93% of the time understates what the model knows.

## What the experiments show, and where they stop

**Scale.** The work does not show an LLM reading billions of weights in a prompt. Unassisted reading topped out at 171,664 weights. The 1.5-million and 0.8-billion results relied on a sandbox, targeted analysis and measured forward passes. The Qwen edit itself touched 131,072 weights.

**Context.** Astra usually received a precise description of the inputs, outputs and architecture. That is much more than raw numbers alone.

**Sample size.** Most results come from one to four runs per condition. The authors call them “very early results,” and every number is author-reported.

**Model coverage.** Every experiment used GPT-6 Astra. Simon Willison [repeated Experiment 1 on a laptop](https://simonwillison.net/2026/Nov/3/qwen-can-interpret-model-weights/) with the open-weight Qwen 3.8 27B. It identified Breakout and Pong, gave a Pac-Man-style answer, and missed Freeway. Each identified game took 46 to 65 minutes. The reading ability does not appear unique to one model, but reliability varies widely.

Reference

| Experiment | Input | Tools | Outcome | Limitation |
| --- | --- | --- | --- | --- |
| 1 · Which game? | 17,253 weights as text, plus a description of the grid and channels | None | Named all 4 games, open answer | 4 runs; self-reported confidence |
| 2 · Which shape? | 23,824 diffusion-model weights as text | None; no forward pass | Named circle, square and triangle | Drew outlines; models generate filled shapes |
| 3 · Which language? | Middle 4 transformer blocks of a 7.2M-weight model | Python analysis; no running the model | Right language 6 of 6; copying heads matched | Confidence 0.48–0.62 |
| 4 · Fix the car | 171,664 weights, scene description, one recorded episode | None; one reply | 1,024 of 1,024 episodes succeed; 3.5% of weights changed | One environment, one edit |
| 5 · Write from scratch | Rules, source code, input/output layout | None; no rollouts | Beat PPO at 100M steps in 3 of 3 games | Behind PPO at 500M steps in Seaquest and Asterix |
| 6 · Write a Go player | 1.48M zero weights in a sandbox | numpy/PyTorch; 0–50 forward passes | 50 passes: beat same-size PPO 70–79% | Lost to same-size PPO with 0 passes; one run per budget |
| 7 · Spot the sycophant | Two Gemma 3 270M fine-tunes per pair | numpy; later an attention-only tool | Weights only: failed. Attention tool: 3 of 3 pairs | Needed observed internal activity |
| 8 · Fix math loops | Qwen3.5-0.8B weights in a CPU kernel | Python; 10, 25 or 50 forward passes | MATH-500 7.9% → 48.1% with 50 passes | Removed loops; no gain on Gemma 3 270M |

All results are author-reported from the [post](https://rikiyat.github.io/blog/weight-space-programming/) and [logs](https://github.com/RikiyaT/lm_understand-logs). Scroll sideways on small screens.

## Self-improving AI is a hypothesis, not a result

The authors list possible futures: auditing weights for backdoors without running a model, one-shot initialization instead of long training, adding capabilities on request, grafting circuits between models and recursive self-improvement. They present these as directions, not findings.

No experiment had Astra edit its own weights. No experiment showed an edit adding a capability the model lacked; the Gemma test points the other way for now. Reliable self-improvement would need edits to models comparable in size to the editor, gains that survive independent evaluation, and safety checks before any change takes effect.

Reference

Demonstrated · author-reported

- ✓ Identify a small network’s task from its weights
- ✓ Locate known components, such as copying heads
- ✓ Repair a specific failure with a small edit
- ✓ Write small working networks from a spec
- ✓ Stop reasoning loops in a 0.8B model

open research  
question

Hypotheses · not tested

- ? Audit weights for backdoors without running the model
- ? Add a capability the model lacked
- ? Edit models as large as the editor itself
- ? Change its own weights safely and reliably
- ? Recursive self-improvement

The experiments support specific capabilities. Broader self-improvement remains a question for further research. Hypotheses follow the authors’ [stated future directions](https://rikiyat.github.io/blog/weight-space-programming/).

## What this means for IT and business leaders

None of this is a product you can buy today. The practical lessons concern how you govern models you already run.

**Treat weight files like code.** A 0.016% edit can change a model’s behavior while its size and file name stay the same. If your team runs open-weight models, record the source, version and checksum of every weight file. Re-run a fixed test set after any change. Our [open-weight model risk checklist](https://itecs.ai/insights/open-weight-ai-models-business-risk-checklist) covers the supporting controls.

**Illustrative scenario:** a 150-person engineering firm runs a small open-weight model on staff laptops for drafting. A contractor supplies an “improved” copy that no longer rambles. Without a recorded checksum and a fixed test set, the firm cannot tell what else changed. The scenario is hypothetical; the control is cheap.

**Question large benchmark jumps.** Qwen’s MATH-500 score rose sixfold because one failure mode stopped, not because the model learned mathematics. When a vendor reports a big gain, ask what changed and test it on your own work. A [blind evaluation on your real tasks](https://itecs.ai/insights/ai-model-evaluation-blind-tests) separates real gains from fixed failure modes.

**Watch interpretability.** If weight reading matures, audits could inspect a model for hidden behaviors before deployment. Experiment 7 shows that capability is not reliable yet for subtle behavior. For now, behavior testing remains the control that matters.

## Weight-space programming questions

What is weight-space programming?

It is a method in which a general-purpose LLM reads and writes a neural network’s weights directly, without gradient descent. The term comes from a November 2026 MIT CSAIL research post that used GPT-6 Astra.

Did GPT-6 Astra read billions of weights in one prompt?

No. Without tools, it read networks of up to 171,664 weights as text. The 1.5-million-weight and 0.8-billion-weight experiments used a Python sandbox, targeted analysis and limited forward passes.

Did the edit make Qwen3.5-0.8B better at math?

It raised benchmark scores by stopping reasoning loops that ran into the token limit. The authors say the edit removed an obstacle rather than adding math ability, and a model that rarely looped did not improve.

Can AI now improve its own weights?

Not based on this research. No experiment edited Astra’s own weights, and the authors present self-improvement as a future direction.

Should my business act on this research now?

Not as a tool to deploy. Use it as a reason to record the source and checksum of every open-weight model you run and to re-test any model after a change.

Deciding which AI research signals deserve a pilot? Start with your workflow, your models and a fixed test set. [Learn about our AI Consulting service](https://itecs.ai/consulting) or [start the no-cost intake](https://itecs.ai/contact).

![](assets/itecs-icon-darkblue.svg)

## Ready to see where AI moves your business forward?

1Send intake

2Scope the need

3Choose the next step

## Sources And Trust Signals

This research explainer draws on the primary sources below, checked November 4, 2026. Diagrams are original ITECS illustrations; captions mark measured values. The governance guidance is ITECS editorial analysis.

[Takehi, Teoh, Zhang & Khattab — Sparks of Weight-Space Programming](https://rikiyat.github.io/blog/weight-space-programming/)

MIT CSAIL research post, November 2, 2026. Definitions, all eight experiments, results and stated future directions. Author-reported; ITECS did not reproduce the experiments.

[RikiyaT/lm\_understand-logs — Experiment logs](https://github.com/RikiyaT/lm_understand-logs)

Prompts, replies, token usage, tool audits and evaluation files for every reported run. Source for per-game confidence, Go win rates and the same-size PPO baseline. Checked November 4, 2026.

[Hugging Face — Edited Qwen3.5-0.8B](https://huggingface.co/RikiyaT/Qwen3.5-0.8B-weight-space-programming)

The authors’ released copy of Qwen3.5-0.8B with Astra’s Experiment 8 edit applied.

[Simon Willison — Qwen 3.8 27B on my laptop can interpret model weights, too](https://simonwillison.net/2026/Nov/3/qwen-can-interpret-model-weights/)

November 3, 2026 independent partial repeat of Experiment 1 with an open-weight model, including run times and one miss.
