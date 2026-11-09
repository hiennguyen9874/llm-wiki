On November 2, 2026, Rikiya Takehi, Jayden Teoh, Alex Zhang and Omar Khattab of MIT CSAIL published Sparks of Weight-Space Programming. They report that a general-purpose frontier model, OpenAI’s GPT-6 Astra, can read and write neural network weights directly, without gradient descent. The result that will travel furthest: Astra changed 131,072 of Qwen3.5-0.8B’s roughly 0.8 billion weights (0.016%), and with the same sampling settings the model’s MATH-500 score rose from 7.9% to 48.1%.

The credit belongs to the researchers who designed and documented these experiments, to the model that did the diagnosis, and to the earlier interpretability work the result builds on. My interest is narrower. Since early 2025 I have been trying to qualify, and eventually quantify, how much AI performance comes from better methods rather than more hardware. This is a useful data point for that effort, and it has clear limits.

What the researchers reported
Small reasoning models are known to loop: they repeat the same text and never reach an answer, a failure characterized by Pipis et al. (2025). In the authors’ practice runs, 85 of the base model’s first 96 answers ran to the 32,768-token limit.

Astra was given a Python session with the weights loaded and a budget of forward passes on problems drawn from the GSM8K and MATH training sets. Training and gradient information were not allowed. Astra traced the looping to one direction written by the MLPs of layers 15 and 19, then subtracted that direction from 64 output columns in each layer. The authors compare the edit to the single-direction ablation of Arditi et al. (2024), who showed that refusal in language models can be removed by deleting one direction from the weights.

Article content
Removing one direction from selected weight columns. Standard projection shown for illustration; the source post does not print the update equation.
With a budget of 50 forward passes, the reported results were:

• MATH-500: 7.9% to 48.1%

• GSM8K: 13.8% to 67.1%

• IFEval (instruction following): 21.0% to 62.3%

• MATH-500 answers hitting the token limit: 93.0% to 33.1%

Article content
A 0.016% weight edit and the reported changes in Qwen3.5-0.8B performance with a 50-forward-pass budget. Source: Takehi et al. (2026).
The authors also tried Gemma 3 270M, which reaches its token limit on only 8.5% of answers. Astra found ordinary errors there, such as wrong arithmetic and invalid algebraic steps, with no single component to switch off. No edit moved MATH-500 by more than about a point. The authors’ own conclusion is the right one: editing weights removed an obstacle that hid an ability, but it did not add an ability the model lacked.

Confirmed, claimed and not yet known
Several things are well documented. The researchers published complete logs of every experiment, including prompts, code, outputs and the networks themselves. The edited Qwen model is on Hugging Face, and the authors state that Ahsen Khaliq at Hugging Face rebuilt it from those logs and re-ran its evaluation. An independent rebuild is worth more than any single benchmark figure in the post.

Other things are not yet established. This is a blog post, not a peer-reviewed paper. The write-up does not report how many runs were made at each budget or how results varied across them. The gain was also not gradual. At 10 and 25 forward passes, MATH-500 reached only 12.3% and 14.1%, and the share of answers hitting the token limit barely moved (87.2% and 86.4%). The large improvement appears only at 50. That may reflect a threshold in the search or the outcome of a single run; the write-up does not say which.

Article content
The largest reported improvement appeared at 50 forward passes. Run counts, variance and diagnostic-model compute were not reported. Source: Takehi et al. (2026).
Finally, “0.016%” describes the size of the edit, not the cost of finding it. The compute used by the frontier model doing the diagnosis is not reported, so any efficiency comparison with fine-tuning remains open.

Why security and architecture teams should care
Find the operational bottleneck
One implication is operational. Most of the base model’s failure was not missing knowledge; it was a narrow mechanical fault that consumed the output budget. Enterprise AI deployments often fail the same way at the workflow level: a model that truncates, times out, or escalates everything. I saw a version of this in my own authorization testing, where one configuration returned “hold” on every case and another lost 33 of 300 answers to a token cap. Before buying a larger model, find out where capability is being lost.

Verify model integrity
The other concerns model integrity. If a general-purpose model can change behaviour across several benchmarks by editing 0.016% of the weights, a modified checkpoint can be identical to the original in size and architecture and nearly identical in content. The same technique that removed a loop could plausibly insert a behaviour, and the precedent the authors cite was the removal of refusal. Detection is not yet a counterweight. In the same post, Astra could not tell from the weights alone which of two fine-tuned models had been trained to be sycophantic; it needed to observe attention patterns at runtime.

For model supply chains, that suggests three controls that are worth having already:

• Pin and verify weights by cryptographic hash and signature, not by model name or version string

• Diff any checkpoint against its recorded provenance before deployment

• Re-run behavioural regression suites, including refusal and policy behaviour, after any change, because a small diff no longer implies a small effect

Where this fits my own work
In Defining Williams’ Law and Think Smarter, Not Harder, I proposed modelling performance as P(H, A), a function of hardware capacity H and an algorithmic innovation index A, and argued that gains in A can be large even when H is fixed. The Qwen result is consistent with that framing: a large gain at constant parameter count and architecture. It does not test it. One edit to one model says nothing about whether such gains compound, and I do not yet have a validated way to measure A.

Article content
Williams’ Law as a hypothesis: performance may improve through algorithmic innovation at fixed hardware. This schematic is not a measured result.
That is the work I care about now: attributing gains to their source, counting the full cost of producing them, and turning “algorithmic improvement” from an adjective into a number with an error bar. Results like this one make the question more concrete, and the credit for that belongs to the team that ran it.

References
Takehi, R., Teoh, J., Zhang, A. and Khattab, O. (2026). Sparks of Weight-Space Programming: LLMs can natively read and write neural network weights. Blog post, November 2, 2026. https://rikiyat.github.io/blog/weight-space-programming/

Arditi, A. et al. (2024). Refusal in Language Models Is Mediated by a Single Direction. arXiv:2406.11717

Pipis, C. et al. (2025). Wait, Wait, Wait… Why Do Reasoning Models Loop? arXiv:2512.12895

Williams, J. (2025). Defining Williams’ Law: The Power of Algorithmic Innovation. Zenodo. https://doi.org/10.5281/zenodo.14946951

Williams, J. (2025). Think Smarter, Not Harder: Algorithmic Innovation as the Key to Exponential AI Performance. Zenodo. https://doi.org/10.5281/zenodo.14957577

Williams, J. (2026). Allow, Hold, or Deny: Comparing the Speed, Accuracy, and Reported Certainty of Four AI Models. Zenodo. https://doi.org/10.5281/zenodo.23005044

About the author
Junior Williams is a cybersecurity architect and AI researcher, and a 2026–27 Industry Fellow at the Rogers Cybersecure Catalyst at Toronto Metropolitan University. His research examines AI agent trust, delegated authority, supervision and accountability, alongside the contribution of algorithmic innovation to AI performance.

