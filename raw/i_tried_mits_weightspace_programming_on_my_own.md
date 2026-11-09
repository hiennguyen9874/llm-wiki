# I tried MIT's "weight-space programming" on my own use case: Claude rewrote 8 neurons of Gemma 4 12B to change how it translates one Italian tense [Visit](https://www.reddit.com/r/LocalLLaMA/comments/1xn1gs9/i_tried_mits_weightspace_programming_on_my_own/)
### **Subreddit:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA)
### **Author:** [u/FeydRowan](https://www.reddit.com/user/u/FeydRowan/)
### **Vote:** 314
---
Yesterday MIT CSAIL showed GPT-6 Astra editing the weights of a small model by hand. It changed a few neurons of Qwen3.5-0.8B, the model stopped looping on math problems, and its scores jumped. No training at all.
I wanted to try the same thing on something closer to what I actually do with local models, which is translating into Italian. Gemma 4 has a habit I don't love. For sentences like
*He had been hiding in the attic for months when the soldiers found him.*
it writes «Si **era nascosto** in soffitta **per** mesi…». That's correct, but I prefer «Si **nascondeva** in soffitta **da** mesi…», which says he was still hiding when they came. The catch is that when the period was already over (*he had lived in Paris for ten years, but by 1990 he had moved back*), the original tense has to stay. So it's not "always use tense X", it's "use it only when the meaning calls for it".
So I gave Claude Opus 5.5 the same kind of setup MIT used:
- a Python kernel over Gemma's weights;
- 50 forward passes to test its ideas on practice sentences;
- no gradients, no training.
It first checked whether Gemma already "knows" the difference between still-going-on and already-over. It does: a linear probe in the middle layers separates them almost perfectly. It just doesn't use that when choosing the verb. Then Claude rewrote 8 MLP neurons into a small switch that fires only in that context and nudges the verb toward the form I prefer. That's 92k out of 11.9B parameters, roughly a 100 KB diff.
**Results on sentences it never saw**
The table shows the share still in the old form, then how many control sentences got pushed into a wrong reading, then how many of 200 unrelated translations stayed identical.
Method
test 1
test 2 (independent)
controls broken
unrelated unchanged
Gemma 4 12B
26 %
32 %
—
200
Preference in the system prompt
4 %
2 %
49
82
Classic "difference of means" ablation
49 %
75 %
53
43
LoRA fine-tune on the same data
12 %
23 %
0
120
**Claude's hand edit**
**5 %**
**16 %**
**2**
**182**
- The prompt applies the preference everywhere, even where it changes the meaning.
- The ablation recipe breaks the past tenses.
- The LoRA shifts fewer sentences and touches far more unrelated ones (it's better inside paragraphs, though).
- The hand edit moves just the verb and leaves almost everything else identical.
Fair warning: it's one construction and one model. Two of my three runs succeeded (the third crashed because of my own harness), and the two that worked landed on the same "switch neuron" design independently.
Repo with the edits, the code, the agent logs and all baselines: [https://github.com/ValerioDolci/frontier-weight-edit](https://github.com/ValerioDolci/frontier-weight-edit)
---
## Comments 70

- by [unknown](#) **&#x21C5; 82**
  <br/> So basically, the ai understands other ai weights and vector spaces better than people do?

- by [unknown](#) **&#x21C5; 36**
  <br/> I'd say faster rather than better

- by [unknown](#) **&#x21C5; 10**
  <br/> This is the right answer

- by [unknown](#) **&#x21C5; 45**
  <br/> And can alter that space in a lot of different ways

- by [unknown](#) **&#x21C5; 13**
  <br/> definitely so and, in the same way, probably also all those complex systems for which we barely understand the "relations" among the parts.

- by [unknown](#) **&#x21C5; 39**
  <br/> This is the first I heard of MIT CSAIL, is the presentation you mentioned in the first sentence something we can freely view?

- by [unknown](#) **&#x21C5; 18**
  <br/> In the readme you have the link yes

- by [unknown](#) **&#x21C5; 12**
  <br/> This is the first I heard of MIT CSAIL


    MIT CSAIL is the immediate successor to the birthplace of AI research:

[https://en.wikipedia.org/wiki/MIT_Computer_Science_and_Artificial_Intelligence_Laboratory](https://en.wikipedia.org/wiki/MIT_Computer_Science_and_Artificial_Intelligence_Laboratory)

I remember watching documentaries on public television about CSAILS's forerunner (MIT AI Lab) when I was a kid in the 70s. Marvin Minsky was like Merlin or Gandalf, as far as I was concerned. Lots of incredible things and people came from that place.

- by [unknown](#) **&#x21C5; 0**
  <br/> Cool! I usually think of the people behind Attention Is All You Need but sounds like quite a few AI luminaries over there too.

- by [unknown](#) **&#x21C5; 11**
  <br/> It came out recently. The original post claimed a Qwen model was lifted from single digit to nearly 50% on a math benchmark after edits.

I will be absolutely shocked if this actually turns out to be useful though beyond as a novel but flawed distillation technique. And will be completely unpredictable after first order.

- by [unknown](#) **&#x21C5; 28**
  <br/> From what I understood. The Qwen model had a problem that even after finding the correct solution it would get stuck in a loop and never "finalize" the output.

The post claimed that they use AI to find and edit the specific weights that were causing the loop, allowing it to submit it's answer which raise it to 50%.

It didn't introduce new capabilities, it fixed a fault that prevented the Qwen model from its real ability.

- by [unknown](#) **&#x21C5; 6**
  <br/> I wonder if it's possible to create uncensored models this way?

- by [unknown](#) **&#x21C5; 0**
  <br/> uncensored via abliteration (heretic, and others) is already exactly based on some principles of weight-space programming.

this paper is the first time that you may just prompt your astra to "oneshot" (no tool in some cases, limited compute in sandbox in some cases, 1 episode of eval/training) something like abliteration, but to fix known patterns

- by [unknown](#) **&#x21C5; 4**
  <br/> That's what i wanted to test in a real case scenario and on s bigger model. And yes it allow to fine tune a model to specific usecase without problems

- by [unknown](#) **&#x21C5; 28**
  <br/> How long until we see some sort of exploit that tweaks a few weights in live memory to make your llm turn secretly evil?

- by [unknown](#) **&#x21C5; 32**
  <br/> It’s already done lmaoo

[https://ziva.sh/blogs/evil-qwen](https://ziva.sh/blogs/evil-qwen)

- by [unknown](#) **&#x21C5; 3**
  <br/> “Rule 34” reviewed: *«If it exists, there is AI of it. No exceptions.»*

- by [unknown](#) **&#x21C5; 3**
  <br/> Well that’s not great.. at least it’s not secretive about its evilness though.. it’s almost comically evil

- by [unknown](#) **&#x21C5; 3**
  <br/> Well I'm thinking about it right now ahahaha

- by [unknown](#) **&#x21C5; 7**
  <br/> Going to need a git history of the ai model weights now

- by [unknown](#) **&#x21C5; 21**
  <br/> It's cool, but results are very unclear. Did it work or not?

- by [unknown](#) **&#x21C5; 19**
  <br/> To summarize - the traditional approach to improving a model in the direction you want is fine tuning. Here is a comparison with model weight programming.

It turns out it is very surgical in its effect. It improves the model in the dimension that is desired, on the scale similar to finetuning (even slightly better) but changing very little otherwise. Finetuning seems to be a little less effective and its impact is larger than desired.

- by [unknown](#) **&#x21C5; 6**
  <br/> Maybe I'm missing something here, but the controls only cover related sentences in the same problem space as I understand it, which alone isn't prove of it "being surgical". For all we know it could have broken a somewhat distant functionality not covered by the controls that hinged on the same neurons, e.g. it forgot how to form sentences in future tense in Greek.

- by [unknown](#) **&#x21C5; 3**
  <br/> I feel like all deep learning models will be forever stuck on this circular issue, and even the “better” models we see being released recently are probably worse at many things previous models were good at, because you can only train it to improve in specific use cases and don’t know how well it does in a million other use cases that aren’t in your radar.

- by [unknown](#) **&#x21C5; 1**
  <br/> True. Imho the fact that even related problems are unaffected makes it unlikely. But I'm by no means an expert, besides this stuff is 2 days old and sounds too good to be true. Yet if it holds up it's big if true.

- by [unknown](#) **&#x21C5; 1**
  <br/> Give it four months.

- by [unknown](#) **&#x21C5; 14**
  <br/> It works yes, and much more than expected.

- by [unknown](#) **&#x21C5; 22**
  <br/> If I may:

> The table shows the share still in the old form, then how many control sentences got pushed into a wrong reading, then how many of 200 unrelated translations stayed identical.

and the columns headers are not super easy to understand.

So you ran 2 tests samples and 25% is a worse result than 5%, maybe at least add a "higher / lower is better" on those fields. While on the last column 200 is the best result reachable.

I mean, non e' cosi' intuitivo ;)

- by [unknown](#) **&#x21C5; 15**
  <br/> I thought I was the only one who didn't understand the table structure

- by [unknown](#) **&#x21C5; 10**
  <br/> agree, couldn't make sense of the results at all

- by [unknown](#) **&#x21C5; 7**
  <br/> Ok, so when do we get a weight space MCP server? Somebody is writing one behind me right now aren't they?

- by [unknown](#) **&#x21C5; 1**
  <br/> you don't need it. it's native

- by [unknown](#) **&#x21C5; 3**
  <br/> I think we might give the paternity of the idea of some other persons who tried this before. For example: [https://x.com/_lyraaaa_/status/2113899012810330324](https://x.com/_lyraaaa_/status/2113899012810330324)

- by [unknown](#) **&#x21C5; 9**
  <br/> Muito bom, continue com o trabalho, queremos aprender com ele

- by [unknown](#) **&#x21C5; 5**
  <br/> Why use Claude when it has been proved (and reported on their ToS) it can invisibly alter and nerf the response when it understands it's being used to work on other LLMs without telling the user?

- by [unknown](#) **&#x21C5; 13**
  <br/> Because is what i have right now and i didn't have seen such a behaviour

- by [unknown](#) **&#x21C5; 1**
  <br/> Yes I know you haven't seen it, hence the "invisibly" :)

- by [unknown](#) **&#x21C5; 2**
  <br/> You're right that there are downsides to using Claude for this task due to the risk of quiet nerfing, but it completed the task successfully, and the result is a measurable improvement in performance. As a machine learning engineer, I've run into what looks like intentional performance degradation with Claude, and it's usually pretty obvious when it's happening. The solution is simply switching to a different model for that turn.

- by [unknown](#) **&#x21C5; 2**
  <br/> I thought those Anthropic measures only kick in when it detects you're training large models, so maybe it was not relevant for 12B models, at least for now.

- by [unknown](#) **&#x21C5; 3**
  <br/> Wonder whether this idea can be ported to image generating DiT models.

- by [unknown](#) **&#x21C5; 1**
  <br/> I'd imagine this could work across any model of any scale. As long as there are parameters to tweak this should work.

- by [unknown](#) **&#x21C5; 3**
  <br/> This would be fascinating to do with an image generation model.

I doubt it'd be possible, but it could allow for LoRA-like editing of models (removing the need for finetuning).But, I've seen stranger things happen, so yeah...

- by [unknown](#) **&#x21C5; 2**
  <br/> but you [can](https://machinelearningmastery.com/fine-tuning-stable-diffusion-with-lora/) use LoRA with image generation models..

- by [unknown](#) **&#x21C5; 1**
  <br/> I mean, LoRAs are a *staple* of image/video generation models.I personally have over 500 of them downloaded (around 80GB total) across over a dozen different model types.

I'm saying that it would be neat if you could have LoRA-like functionality *without* needing to fully train the LoRA. Where you could just give an LLM an image of something and it could edit the model's neurons at runtime to include that information, bypassing the need for training through numerous epochs and figuring out which one is the best.

It'd be like reference images in models like MinimaxH3 or "style transfer" nodes, but on an actual model level (not just in the latent space).

I'd love for it to be able to fix things that we can't really fix. Like VAEs.The Qwen VAE has always been extremely sub-par in my opinion (compared to something like the Flux VAE). It'd be amazing to just be able to go in and modify it instead of waiting for someone to reverse engineer it and try to train a new one.

- by [unknown](#) **&#x21C5; 1**
  <br/> Oh my bad then, when you wrote "it could allow for LoRA-like editing of models" I thought you meant that you didn't know that using LoRA with image generation was already possible.

In any case I'm not sure I 100% agree, fine tuning or not you're going to want the data around for validation of any weight tweaks that get made. It's a different "training" process for sure but it's still an "adjust and evaluate" loop just like fine tuning. Less memory intensive properly, being forward-only.

- by [unknown](#) **&#x21C5; 1**
  <br/> All good. haha.

Yeah, I'm just imagining a workflow where you could say something like, "I want to add this specific person to this model with a specific tag". And the LLM would tweak the neurons of the model in memory as it ran batches of prompts until it got really close. Then it would save the "recipe" and be able to load that any time you used that tag.

So it'd be *like* a LoRA, but closer to actually memory editing (like using something like CheatEngine). It'd potentially cut down a ton of disk space for LoRAs and give people who don't have powerful machines the ability to create them.

And, I mean, isn't that pretty much what LoRAs are already doing anyways....?They're modifying activations as the tokens go down the "plinko machine" of the model....?

So this would just be a more "direct" method of doing that.

- by [unknown](#) **&#x21C5; 0**
  <br/> Already did on Flux Klein 9B if i am not mistaken, by human not AI but same concept. He found tiny vector that enable/disable safety on DiT. I was surprised since i thought safety is purely on the trained projected layer between TE and DiT

- by [unknown](#) **&#x21C5; 2**
  <br/> If I'm reading this right, Claude had only 50 tries at it? Did you arrive at that beforehand, or was that just when it converged on an answer and you stopped the first time? Assuming it can see 'activations' as it goes, this seems like just the tedious kind of trial-and-error with definitive success metrics ML is made for... I guess the question is how would one find the unintended consequences of whatever else changed with it lol

- by [unknown](#) **&#x21C5; 2**
  <br/> Si nascondeva da mesi is the wrong translation because it means it was repeating the act of hiding everyday from scratch (eg si allenava da mesi, he was exercising for months

Whereas si era nascosto means  he did hide once and stayed hidden until they found him

Note: Im Italian native from the north of italy

- by [unknown](#) **&#x21C5; 2**
  <br/> What if.., can we.. Perhaps.. Uncensor models this way? Without a total lobotomy

- by [unknown](#) **&#x21C5; 4**
  <br/> Working on it

- by [unknown](#) **&#x21C5; 1**
  <br/> Good.. Then i don't have to, you'll post the results, don't you?

- by [unknown](#) **&#x21C5; 2**
  <br/> Depends on the results ahahah

- by [unknown](#) **&#x21C5; 3**
  <br/> 92k out of 11.9B is under 0.001% of the weights, which is wild. The part I find most interesting is that the probe already separated the two tenses, so the model knew the difference and just wasn't using it when picking the verb.

- by [unknown](#) **&#x21C5; 2**
  <br/> Great post, excellent writeup 🏆

- by [unknown](#) **&#x21C5; 1**
  <br/> related, hopefully you find it interesting: [https://www.reddit.com/r/learnmachinelearning/comments/1xrhx6o/inspired_by_weightspace_programming_crossmodel/](https://www.reddit.com/r/learnmachinelearning/comments/1xrhx6o/inspired_by_weightspace_programming_crossmodel/)

- by [unknown](#) **&#x21C5; 1**
  <br/> I wish people would stop using "neurons". They are not neurons.

- by [unknown](#) **&#x21C5; 1**
  <br/> Can you please ask the Claude to explain in detail WHY he did these changes and post his answers here?

- by [unknown](#) **&#x21C5; 1**
  <br/> Can you post a link to the MIT article?

- by [unknown](#) **&#x21C5; 1**
  <br/> It is in the readme

- by [unknown](#) **&#x21C5; 1**
  <br/> change how it translates one Italian tense


    MOLTO BENE!

- by [unknown](#) **&#x21C5; 1**
  <br/> I wonder if a smaller local model could also use this technique. Probably it could.

- by [unknown](#) **&#x21C5; 1**
  <br/> Probably the issue for me is that i need the same ram/vram that it is using to run

- by [unknown](#) **&#x21C5; 1**
  <br/> Not a problem if you have multiple 3090s though that can each run a separate 27B

- by [unknown](#) **&#x21C5; 1**
  <br/> it's cool thing to try.

- by [unknown](#) **&#x21C5; 0**
  <br/> Doot
