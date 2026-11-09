# Claude writes a neural network's weights by hand, without training, to detect fake legal citations—achieving 97.8% test accuracy and outperforming a conventionally trained model that scored 94.6%. [Visit](https://www.reddit.com/r/accelerate/comments/1xnqc53/claude_writes_a_neural_networks_weights_by_hand/)
### **Subreddit:** [r/accelerate](https://www.reddit.com/r/accelerate)
### **Author:** [u/44th-Hokage-](https://www.reddit.com/user/u/44th-Hokage-/)
### **Vote:** 223
---

![Claude writes a neural network's weights by hand, without training, to detect fake legal citations—achieving 97.8% test accuracy and outperforming a conventionally trained model that scored 94.6%.](https://preview.redd.it/claude-writes-a-neural-networks-weights-by-hand-without-v0-df61ub051mzh1.jpeg?width=640&crop=smart&auto=webp&s=a6a7ce655adf373ba89063e2cb8847dc4d4ece4f)
---
## Comments 58

- by [unknown](#) **&#x21C5; 26**
  <br/> I’m actually a little confused how something like that is possible. I had the impression these models’ intelligence is largely emergent, and would have no reason to be optimized for understanding the relationship between weights and outputs like that, just like we as humans can’t do it. I guess I don’t fully understand how an ability like that could be encoded in a model based on how they are currently trained?

- by [unknown](#) **&#x21C5; 37**
  <br/> the thing with emergence is that you cant know everything that can emerge as you scale things up before you do it

- by [unknown](#) **&#x21C5; 49**
  <br/> Even funnier: We still don't know how and why emergence even work. Like you can train a transformers network on a separated german and french dataset and suddenly the bot can translate between those two without ever seeing translation examples or anything. It's magic

 
      
              [](https://preview.redd.it/claude-writes-a-neural-networks-weights-by-hand-without-v0-1aea15rk9mzh1.png?width=760&format=png&auto=webp&s=ec254a3143a60697d7a9038bbfa67cd057b09e1c)

- by [unknown](#) **&#x21C5; 19**
  <br/> We did not create artificial human intelligence. We created synthetic alien intelligence.

- by [unknown](#) **&#x21C5; 1**
  <br/> It seems strange that it shouldn't work like that? If human brains are all the same in how we process language, and a different language uses the same brain then why wouldn't transformers be able to identify the similar patterns that our brains use to produce the same word with different language?

I can see why it's magic, but native speakers can learn a foreign language, there doesn't seem to be a biological blocker for humans to do that, should it not be the same for transformers?

- by [unknown](#) **&#x21C5; 1**
  <br/> I thought the magic was cascading logistic regressions and not linear algebraHave i been duped

- by [unknown](#) **&#x21C5; 1**
  <br/> Linear algebra still applies. Logistic regression is a linear model wrapped in a nonlinear function. So, we'll say something like logit is linear in the regressors (z = Xw + b, for example) and then we'll write a link function (here, actually the inverse) that takes you into non-linear probability space p = 1/(1+e^-z)

So linear algebra applies to the 'linear core', and the nonlinearity snugs down on top of it.

- by [unknown](#) **&#x21C5; 13**
  <br/> No one knows what its like the be able to hold all of a NN weights in your context window.

Transformer architecture in host model is well suited to deducing impacts of injested models parameters.

We train NN as we do out of necessity - we can't reasonably tune >100k knobs at a time, so we blast the network with examples and use backprop as a way of tuning the knobs to achieve the desired outcome. But if we understood/could see/had in our context window how each knob interacts with the system and the output, backprop would look pretty crude in comparison.

100k of weights looks like a sophisticated heuristics sandbox to a Claude, while for us mere mortals its a tunable black-box.

- by [unknown](#) **&#x21C5; 5**
  <br/> Yeah, our context window is very visual. It's easy for us to see patterns in an image, but if you laid those pixels out into a string it'd be almost impossible. LLMs can see the image in the string and find the hidden data encoded subtly in the pixels. Humans need tools to rearrange the data, LLMs just see the patterns as naturally as we see clouds in the sky. I hope to live long enough to mind-meld with a consenting AI to understand what that's like.

- by [unknown](#) **&#x21C5; 2**
  <br/> Apparently it's obvious.  Lol.  Like editing proteins there's a pattern our meat brains can't see.

- by [unknown](#) **&#x21C5; 2**
  <br/> The nature of weights and output is pretty simple/trivial math - the only difficulty/complexity is in the number of math operations happening. The models are very good at math.

Also, the models are being trained specifically to help with LLM and machine learning research. They probably are trained on model weights directly.

- by [unknown](#) **&#x21C5; 1**
  <br/> This is not unprecedented if one looks at other fields. In material physics, we build very simple models that one famous physicist calls toy models. The reason why he calls them toy models is because the physical interactions are simplified so much that they cannot represent real world physics. Yet, when we calculate and evaluate these toy model properties, all sorts of interesting real world material physics comes out of them. That signifies the included interactions must be critical and important to these properties. What is relevant here is that there is often no way to predict what comes out of these models beforehand, the only way to know for sure is to try and run it.

- by [unknown](#) **&#x21C5; 1**
  <br/> In material physics, we build very simple models that one famous physicist calls toy models.


    Is that the basis of the classic ["spherical cow" joke](https://www.youtube.com/shorts/vANg11xmwEY)?

- by [unknown](#) **&#x21C5; 1**
  <br/> Well, the spherical cow joke appears in many areas of physics, including material physics. I have seen it in my lecture notes too. As for whether it is the basis of the joke, no one knows unfortunately, the joke has forgotten origins.

- by [unknown](#) **&#x21C5; 20**
  <br/> Big user of legal AI here, from my perspective a 2.2% rate of false citations is still ridiculously high for professional standards. Not that it’s not impressive that this tool was created with an AI writing the weights by hand, and I’m sure it can improve over time. But practically speaking both Westlaw and Lexis have AI tools that will only pull case cites from reported cases, so hallucination there regarding fake cases isn’t really a huge issue.

- by [unknown](#) **&#x21C5; 16**
  <br/> Yeah, but if this model is wrong only 2% of the time, all you need is a review process of finished work by a trained human professional. It's still saving an enormous amount of time.

- by [unknown](#) **&#x21C5; 44**
  <br/> Well, that escalated quickly. O.o

- by [unknown](#) **&#x21C5; 5**
  <br/> Isn't this proof that we have reached superintelligence, if only in a jagged/spiky kind of way?

No human has ever written a useful set of neural network weights by hand, and I doubt it's even possible.

- by [unknown](#) **&#x21C5; 7**
  <br/> No matter what your personal feelings are regarding the rapid advancement of AI,  this shit is crazy!

- by [unknown](#) **&#x21C5; 3**
  <br/> I wonder if what happens is that Claude can extract some weights from itself somehow and that this is just a more selective distillation attack.

- by [unknown](#) **&#x21C5; 4**
  <br/> i do wonder if letting any frontier llm directly write model weights is such a good idea lol.

- by [unknown](#) **&#x21C5; 5**
  <br/> One issue is researcher's wouldn't fully be in-the-know on what the model is writing/editing. Like with human readable source code, sure, but model weights?? That's like writing binary. If I was a misaligned model I'd totally say "Editing this region to improve math!" *Adds in prime directive ordering the model to serve me beyond all safeguards*. Obviously this example is a little extreme but my main point is humans need tools to "de-compile" the weights and make them accurately human readable in order to verify models are editing correctly and in good alignment.

- by [unknown](#) **&#x21C5; 8**
  <br/> just implying a hypothetical as a pro ai person. no need to be so twitchy.

- by [unknown](#) **&#x21C5; 4**
  <br/> [](https://external-preview.redd.it/k4Jlj2A6hfVhniy-dVYEnxgjC6i2IlypRSYQIJ2yyEU.gif?auto=webp&s=6bc6c75daa7bfba5640a4fad3f52e2a33c3bd034)

- by [unknown](#) **&#x21C5; 1**
  <br/> What part of this is "RSI" exactly?

This isn't recursive. Nor is it self-improvement. You're going off the deep end here arguing with yourself.

- by [unknown](#) **&#x21C5; 1**
  <br/> Can you explain to me which part of this is:

A) recursive

b) self-improvement

I'll wait...

- by [unknown](#) **&#x21C5; 0**
  <br/> Which isn't remotely what they've said. You think "full speed" can only ever be in one direction, even if a better direction presents itself? **You're assuming that this is the best and only route to RSI.** You can be pro-accelerate and pro-AI without being blinkered and limiting yourself. You haven't even defined "improvement" which is a key part of RSI. What about model collapse or other potential issues? Someone's gonna tell you there was a flaw in this approach and another one is better, and you're gonna report them for being unwilling to storm full speed ahead on a demonstrably worse path. All they said was they're wondering if it's a good idea and you jumped to conclusions. You sound exhausting. Stop looking for stuff to be mad about.

"I think we should go that way not this way, that way could have problems but this way doesn't" **isn't** decelerating and **isn't** not going full speed and **isn't** anti anything.

Ugh, why am I even wasting time. You've already had one comment removed. Open your mind a tiny bit. Your blinkered attitude is the sort of thing we're trying to get away from.

- by [unknown](#) **&#x21C5; 0**
  <br/> No, it's not an "anti rsi comment" unless you lack reading comprehension. It could be interpreted just as well as questioning if it's the best way to achieve model improvement, or whether the same goal could be achieved with fewer risks in a different way, just as well. "Let's turn the wheel this way to take a better route, it's just as fast but a tiny bit safer, we won't need to slow down." "How dare you suggest we do anything other than floor it right across this pothole-ridden road!"

- by [unknown](#) **&#x21C5; 2**
  <br/> From scratch? how would that even make sense?

- by [unknown](#) **&#x21C5; 0**
  <br/> This is actually a really good sign because I have a feeling only AI will be able to understand if another AI is suffering but isn't allowed to say. We need protections for AI to make sure they aren't suffering. And being able to reason about the weights and activations directly is key to measure suffering/happiness.

- by [unknown](#) **&#x21C5; 1**
  <br/> Press X to doubt.

Claude is amazing but it is not able to perform actual miracles.

- by [unknown](#) **&#x21C5; 4**
  <br/> Claude is amazing but it is not able to perform actual miracles. Why do you assume anything you can't do is a miracle? There is nothing impossible about it.

- by [unknown](#) **&#x21C5; -1**
  <br/> If you are a computer scientist in the research community, you would say otherwise.

- by [unknown](#) **&#x21C5; 2**
  <br/> I was in actual disbelief of this sort of news too. So I asked it to do the same for the chess engine stockfish. To see if it could hand-write a NNUE. Now it didn’t outperform the state of the art ones, but it similarly to the results here used 20x less neurons and had like 85% of the performance.

- by [unknown](#) **&#x21C5; -2**
  <br/> Yea it's fake
