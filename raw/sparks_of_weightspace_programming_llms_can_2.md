# Sparks of Weight-Space Programming: LLMs can natively read & write neural network weights [R] [Visit](https://www.reddit.com/r/MachineLearning/comments/1xm89ef/sparks_of_weightspace_programming_llms_can/)
### **Subreddit:** [r/MachineLearning](https://www.reddit.com/r/MachineLearning)
### **Author:** [u/RobbinDeBank](https://www.reddit.com/user/u/RobbinDeBank/)
### **Vote:** 197
---
Link: [https://rikiyat.github.io/blog/weight-space-programming/](https://rikiyat.github.io/blog/weight-space-programming/)
Snippet: “We find that frontier LLMs are surprisingly good at **natively reading and writing neural network weights**, well past what we’d expect from humans or conventional algorithms. This might be a big deal for both optimization and interpretability.Just by looking at the raw weights, GPT-6 Astra **can tell what a network was trained to do**. And without any environment feedback, it **has no trouble writing, from scratch, small game-playing networks** that outplay networks trained with PPO for 100 million steps.”
Very surprising result, I didn’t expect frontier models to have this capability that has not been optimized for, and it’s something humans cannot do either.
---
## Comments 56

- by [unknown](#) **&#x21C5; 51**
  <br/> Just by looking at the raw weights, GPT-6 Astra **can tell what a network was trained to do**. And without any environment feedback, it **has no trouble writing, from scratch, small game-playing networks** that outplay networks trained with PPO for 100 million steps.


    According to Astra:


      **Both claims have experimental support in the post, but the wording makes them sound more general than the tests establish.**


    
      **“Can tell what a network was trained to do from raw weights.”** In the game experiment, Astra received four small networks, plus descriptions of their input channels and possible actions. It correctly identified all four games without being given their names as options.


    
      That’s interesting. But the weights had recognizable spatial clues: for example, weights associated with a paddle concentrated along the bottom of the board. Knowing what the inputs represent makes those clues interpretable. This demonstrates identifying familiar tasks from structured weights—not unrestricted understanding of an arbitrary network. The authors also report a stronger result identifying training languages from internal transformer weights, but failed to identify sycophancy from weights alone. [Experiments 1, 3, and 7](https://raw.githubusercontent.com/RikiyaT/RikiyaT.github.io/master/blog/weight-space-programming/index.html)


    
      **“Writes networks from scratch that beat PPO after 100 million steps, without feedback.”** This is the more striking result to me. Astra received the games’ rules, source code, and input/output layout, then supplied weights in one response without testing the networks. Those networks beat the reported 100-million-step PPO baselines in all three games. Against 500-million-step PPO, it won one game and lost two. [Experiment 5](https://raw.githubusercontent.com/RikiyaT/RikiyaT.github.io/master/blog/weight-space-programming/index.html)


    
      The crucial distinction is **where the knowledge comes from**. Astra already knows about programming, geometry, and game strategies. It can work out a rule like “move the paddle toward the ball’s landing position” and encode that computation into weights. PPO learns behavior through experience. The comparison shows that prior knowledge can produce a better small controller than that particular training setup; the step count alone doesn’t establish superiority over reinforcement learning generally.

- by [unknown](#) **&#x21C5; 45**
  <br/> > But the weights had recognizable spatial cues

> Channel 0 — agent: Strong weights are concentrated on row 8, across the playable columns; elsewhere they look mostly like small initialization-scale values. At (8,1), weights include 4.066 to hidden unit 15 and −4.013 to unit 31. This suggests a bottom-mounted paddle moving horizontally, rather than a character roaming the grid.

recognizable, yeah. totally. my human brain also recognizes these numbers as a bottom-mounted paddle moving laterally. duh.

- by [unknown](#) **&#x21C5; 14**
  <br/> right? chatgpt being like "yo, this isn't a big  deal, everyone can do this" corroborates the hypothesis

- by [unknown](#) **&#x21C5; -1**
  <br/> "according to astra" as in you fed this to ChatGPT and it gave you feedback on this work?

- by [unknown](#) **&#x21C5; 1**
  <br/> It very much looks like it, yes. At least this is clearly disclosed.

The fact that this is also the most upvoted comment to this post is interesting. A couple of random people (or bots, who knows) have even downvoted your question.

- by [unknown](#) **&#x21C5; 5**
  <br/> Since this is a thread about LLMs doing something cool, some people are immediately willing to upvote any criticism, regardless of how poorly-supported.

The other upvoted comment is just complaining that they didn't submit to ICLR. As if that isn't a total lottery anyway where perfectly good papers get buried among tens of thousands of slop papers.

- by [unknown](#) **&#x21C5; 46**
  <br/> its crazy how low the barrier to publishing shit is in this space.  and even then...to github.

there is no math, no theory.  the authors don't event consider that we're literally performing meta modeling on the SAME model here.

- by [unknown](#) **&#x21C5; 34**
  <br/> This is literally a "blog", not a formal "publication".

  - Does everything pertaining to ML *have* to be immediately published in ICLR?
  - Do all blogs need to go through high-quality rigorous reviews that top venues are definitely providing these days?
  - If the authors do not (yet) have a theoretical explanation they would stand behind, must they be restricted from "publishing" to... a *blog*?

This entire blog entry could have just been ["chicken chicken chicken"](https://isotropic.org/papers/chicken.pdf) and it would be justified. I don't understand why we're complaining that "chicken chicken chicken" contains no formal proofs, unless someone seriously submits "chicken chicken chicken" (without the KFC–McDonald–Lotka–Volterra equations) to ICLR.

- by [unknown](#) **&#x21C5; -7**
  <br/> claims should require evidence. this blog post has none; and again-pretty telling they couldnt publish in in iclr, which again, compard to stats, medicine, or the like is much easier to publish in (which was my point).

but if you opened up LinkedIn, or twitter, or whatever, the damage is done-everyone is talking about RSI being imminent, which is such a silly takeaway.

this field is just predatory and unserious now.  we have actors taking advantage of people's ignorance purposefully.  it happened with firms like sakana and papers like 'llms are bayeisan in expectation but not realization (which was total slop that got the writers into cushy jobs)(

- by [unknown](#) **&#x21C5; -26**
  <br/> there is no math, no theory.


    Why should there be? Math and theory haven't predicted or supported any of the major breakthroughs in like decades, the irrational obsession of academics with pretending like ML is in any way a field driven by theoretical mathematics honestly boggles my mind.

This is an incredibly interesting result backed up by solid experimentation and incredibly well presented. I cannot imagine anyone with even a basic understanding of the purpose of science and academia would consider these ideas to be better communicated through a traditional LaTeX pdf with a bunch of equations added for flair.

- by [unknown](#) **&#x21C5; 7**
  <br/> This is nonsense. Maths has supported nearly every major breakthrough. The breakthrough might have been found experimentally first because it takes time to do maths and it takes little time to try random things in bulk until something happens. That doesn't mean we don't have a great theory that explains and isolate why many breakthroughs happen. We have a much better understanding of learning dynamics, phenomena like grokking/double descent, etc and what's happening in the limits of scale like architectural scale (like through NTK) or power laws. We can recreate many of these phenomena in simpler models like linear ones.

And with increasing sophistication of our knowledge, the expectation for maths increases to fit within our expanded knowledge of the phenomenon. Like how RL used to be people fucking around experimentally with heuristics until it was formalized in the framework of optimal control.

- by [unknown](#) **&#x21C5; 17**
  <br/> please go on about how little you know about this area, or really any other one

man, scary times are ahead

- by [unknown](#) **&#x21C5; -23**
  <br/> bI genuinely cannot think of a single major result in the field of Neural Networks that has been driven primarily by theory and maths in the last two decades. I only have an undergraduate degree in ML so it's possible that I'm glossing over something, but I'm pretty familiar with most of the big leaps in the field, if there's something I missed please let me know. But even if there exists some solitary examples, the reality is that ML as a field has been mostly an applied science for years.

And similarly, the above work is an excellent work of applied science, conveying their ideas academically whilst using interactive elements not present in traditional papers to illustrate their point and provide further clarity. I am genuinely curious where you think adding in theoretical mathematics would have helped further their point or provide deeper insight, because from my reading I cannot see anywhere it would have done so, and it appears you just want them to conform to some arbitrary standard of what a paper *should* look like even if it detracts from the actual goals of the field.

- by [unknown](#) **&#x21C5; 26**
  <br/> well, considering this is a subfield of statistical learning, which has had MASSIVE breakthroughs since the nineties, this is, empirically, false

this field has some of the absolute worst reproducibility histories in recent years, wut?  not being able to publish and running to github is....not a good sign

- by [unknown](#) **&#x21C5; -14**
  <br/> considering this is a subfield of statistical learning


    It really isn't by any practical metric. Calling Neural Network research a subfield of statistical learning is about as useful as calling psychology a subfield of electrical engineering, the modern field is so far divorced from it's roots in traditional statistical techniques that conflating the two is just not helpful. Hence why I did specific Neural Networks in my comments, because that's the field we're talking about.

- by [unknown](#) **&#x21C5; 6**
  <br/> It really is, considering everything from attention to RL has an analog in statistical learning-you can directly refer to the mathematics and use traditional stats/ml verbaige.  The main distinction in stats and ml is the research goal; inference or prediction.  that's it.  and there is a rich formulation for llms in both bayesian and frequentss flavors.

hence why i'm calling out the lack of domain knowledge.

- by [unknown](#) **&#x21C5; -3**
  <br/> I think there's the element of emergent phenomenon. We can understand the low level stuff, but when you build these large systems unexpected capabilities arise. Heck, the whole agentic system is just guess and check, then we model it and iterate from there.

- by [unknown](#) **&#x21C5; 2**
  <br/> right, but the 'guess and check' there is a super well engineered network in the general IT sense wrapper around a clever, but very wide and deep statistical model that has hoovered up the entire internet :)

- by [unknown](#) **&#x21C5; -2**
  <br/> Yes, the models are provable with math. Someone starts by thinking, I wonder what happens if I feed a model all of harry potter. Surprise it can generate new characters but is technically limited by previous grammar. So you consider folding in adjacent literature and you observe the model to have more variance. You see the pattern? We can write up the math to get to a result, but the pathway there is not all math, but, lets say the scientific method "guess and check". I'm just mentioning this as I believe the fellow earlier was trying to say.

We build towards an idea "hypothesis" and retroactively tune it after observation. We never just one shot to the conclusion.

- by [unknown](#) **&#x21C5; 2**
  <br/> I think there's the element of emergent phenomenon.


    Have you seen a discussion of ML/AI where emergent phenomena weren't being used to make some sort of implication about consciousness?

- by [unknown](#) **&#x21C5; 1**
  <br/> That's more an artefact of the usage of the term though, as one of philosophy. The behaviour of neural networks is necessarily an emergent phenomenon, we feed them in data and out comes an output that has no structural basis in the machinery we used. When you look at LLMs their ability to use language is an emergent phenomenon, they weren't taught or built to do it. We just don't talk about it because it's generally not relevant, it's only brought up when discussing the philosophy of Neural Networks because that's the term we use for these things in philosophy.

- by [unknown](#) **&#x21C5; 3**
  <br/> I am genuinely curious where you think adding in theoretical mathematics would have helped further their point or provide deeper insight


    I'll just refer you to the foundational crisis that happened in the field of mathematics itself. You're describing something that isn't all that different from the way math operated before it was broadly formalized. Practical success often preceded formal understanding, and the subsequent development of that understanding was hardly an arbitrary academic exercise.

- by [unknown](#) **&#x21C5; 2**
  <br/> The issue is that you are approaching this from the point that theory is some kind of ontological good. This is a work of applied science, the authors have conducted experiments on a model and produced interesting results based on their experiments, and are now sharing it. Any maths added to the paper should be in furtherance of supporting or helping those experimental findings, and I simply do not think that any such additions are needed.

Maths underwent such a reckoning because the field is explicitly based on providing concrete, infallible proofs, and so failing to do so was a failure of the field at a basic level.  But that is a feature of that field specifically. ML is not a field about providing such unfalsifiable proofs, it is about building computers what think good, and maths is merely a useful tool in that endeavour. Even some of the most maths heavy fields of physics still use unrigorous theories because rigour in not a necessary virtue in an applied field.

- by [unknown](#) **&#x21C5; 1**
  <br/> One word answer: diffusion.Based upon theory in nonequilibrium statistical mechanics.

More answers? Differential privacy, watermarking .. all of these are backed by theoretical work in cryptography.

So go on, broadcast your ignorance

- by [unknown](#) **&#x21C5; 27**
  <br/> A few years ago I used to follow the 'learned optimizer' research very closely. The guy from diffusion models, Sohl-Dickstein, [had a group working on it.](https://cs330.stanford.edu/fall2021/slides/Stanford%20CS330%20Jascha%20Sohl-Dickstein%20guest%20lecture%20on%20Learned%20optimizers.pdf) But it never really went anywhere, they had lots of meta-training stability issues and none of their models ever beat traditional optimizers.

I did not expect that learned optimizers would someday just fall out of general-purpose LLMs.

- by [unknown](#) **&#x21C5; 2**
  <br/> I got really excited about this initially. But after reading the blog, the results are still cool but no so impressive. There's nothing so mysterious or surprising going on here. The scale of weight editing/identification feels like something a human could do if given enough time and tenacity.

I think what could be really interesting though is if the frontier labs start fine-tuning their models to get better and better at large model weight editing / interpretation (or even a model editing its own weights). Something quite interesting could fall out of that.

- by [unknown](#) **&#x21C5; 2**
  <br/> **I tested Claude Opus' ability to read Weights**My tests suggest that while LLMs can perform surprisingly precise calculations at the “edges” of a network (estimating optimizer step counts or finding output correlations), they do not “trace” the computational paths between layers. Instead, they rely heavily on memorized dataset templates (like CIFAR-10) and default framework conventions to fill in the blanks. When these expectations are changed, the models can identify the math but will confidently guess wrong about the semantics—such as recognizing that a satellite feature maps to output 4, but calling it a “frog” because it expects an animal.You can find the whole summary article here: [https://substack.com/@sakibbai/note/c-380084331](https://substack.com/@sakibbai/note/c-380084331)

- by [unknown](#) **&#x21C5; 24**
  <br/> Damn, it's so cool

- by [unknown](#) **&#x21C5; 8**
  <br/> Definitely not something I expected. This isn’t a human skill (or maybe a tiny group of people have this extremely niche skill?), and it’s not something these models are optimized for, but the capability somewhat exists anyway.

The result is still limited, unsure if it can ever be viable on a larger scale beyond fixing some model issues, but the fact that this capability exists at all is surprising enough.

- by [unknown](#) **&#x21C5; 1**
  <br/> Are we sure though that Astra hasn't been optimized for this? Maybe that's how OpenAI has been developing their last iterations

- by [unknown](#) **&#x21C5; 2**
  <br/> Big deal for robotics maybe?

- by [unknown](#) **&#x21C5; 2**
  <br/> Yeah but it also means that anyone could take any "safe" open model and make it incredibly dangerous. It means alignment is basically impossible.

- by [unknown](#) **&#x21C5; 0**
  <br/> This is an interesting view I hadn't thought of. My first instinct was that it was bad for interpretability because if a misaligned AI can directly edit weights then thats basically "neuralese" and we have no way of knowing what it's doing on our own. I wonder which way it'll go.

- by [unknown](#) **&#x21C5; 6**
  <br/> Been a while since I've followed research much, but this seems like it could be a way to cheat at the lotto, as far as the lottery ticket hypothesis goes. Might be a powerful pre training step.

And so the road towards AI fueled AI progress continues.

- by [unknown](#) **&#x21C5; 0**
  <br/> Im listening...

- by [unknown](#) **&#x21C5; 10**
  <br/> You mean you're hoping for a little more background? The lottery ticket hypothesis specifically is that weight initializations often give rise to a sub network of sparse connections that captures most of the performance of the full model. The idea is you train the full model, remove all the weights close to zero in the finished model and then retrain the remaining sparse network using the initial weights from before full model training. If you use new initializations it doesn't converge to anything useful, but if you use the same initializations then the smaller sub network magically can coverage to something about as capable as the original full model. If you knew which sub network to use and which initializations to use you can end up with a huge savings in time and compute for training.

No idea where that line of research has gone in recent years, but the two main concepts of interest are proper weight initializations and possible changes to architecture to keep performance while shrinking compute costs. If a model could just... Do that directly, it'd be kind of crazy. Ultimately proposing an efficient architecture and weight initializations that are already pretty good at the needed task might make full model training take about as long as normal fine tuning, since it's already presumably in the same neighborhood as good solutions.

No idea if anything useful will come from this kind of a thing but it's crazy to think about as a possibility.

- by [unknown](#) **&#x21C5; 8**
  <br/> This is wild, essential an emergent [hypernetwork](https://arxiv.org/abs/2306.06955v3) capability. I wonder if a network could modify it's own weight so as to learn continuously without catastrophic forgetting.

- by [unknown](#) **&#x21C5; 3**
  <br/> I’d love to see someone train a model on a task twice. Once with random starting weights. A second from an LLM’s chosen weights.

- by [unknown](#) **&#x21C5; 1**
  <br/> I think regularization will be a really important part of these models going forward, maybe even run-time regularization.

- by [unknown](#) **&#x21C5; 3**
  <br/> Am I just like an idiot, isn't this what attention layers do? Like of course you can attention layer the smaller model into updated weights, it's what the architecture does natively? For the zero-shot aspect, this seems related, [Harnessing the Universal Geometry of Embeddings](https://arxiv.org/html/2505.12540v4)

Very cool and creative and useful application of those properties of course.

- by [unknown](#) **&#x21C5; 1**
  <br/> I see where you're coming from. Attention essentially customizes the weights of each layer according to the inputs. But, if you'll forgive the anthropomorphism, the attention function is a more 'subconscious' or automatic act, whereas what is being done here seems more 'conscious'.

- by [unknown](#) **&#x21C5; 2**
  <br/> Crap.  I swear.  This world.   I had just started working on this exact thing. Arrrggghhhhh

- by [unknown](#) **&#x21C5; 1**
  <br/> I tried editing some locally trained image generation models and it worked. It was able to transfer style, transfer architecture types, apply patches, combine RELU activations, and free up space for new features.

[https://github.com/v-code-895/wsse](https://github.com/v-code-895/wsse)

- by [unknown](#) **&#x21C5; 1**
  <br/> Has there been any hint that these frontier models were trained on some of the weights of open source models?

- by [unknown](#) **&#x21C5; 1**
  <br/> AI is stealing AI's work now

- by [unknown](#) **&#x21C5; 1**
  <br/> I just have a question about the model efficiency. The Qwen3.5-0.8B is what concerns me. What are the TFLOPS needed for the 50 rounds of Astras reasoning? 0.8B is very small model and from  testing you can get similar numbers to what they report in around 200 GRPO steps using LoRA. Is this even efficient?

- by [unknown](#) **&#x21C5; 0**
  <br/> Following this development
