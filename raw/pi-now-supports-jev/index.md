---
title: "Pi now supports Jev."
author: "Apprehensive_Bed7502"
site: "r/PiCodingAgent"
source: "https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/"
domain: "reddit.com"
language: "en"
description: "Pi added quite a bunch of new features in its 0.99.0 update, including support for classifier models. In the official docs, the remote model"
word_count: 3861
---

Pi added quite a bunch of new features in its 0.99.0 update, including support for classifier models. In the official docs, the remote model listed in the example code is jev, the interface is shaped around classifier models like jev, and llama.cpp's classifier implementation explicitly uses jev as its reference point. You could pretty much say this is a feature Pi shipped just to keep up with jev.

So I wanted to ask you guys in the channel:

- Do you guys actually use jev a lot when you're coding? How do you use it?
- Jev only came out a little while ago and Pi already jumped on board with support. What significant role does jev actually play in a coding workflow?

Edit: It's not just about using it for the sake of using it. Is there actually something jev can do that LLMs can't?

---

## Comments

> **Ok-Hippo9182** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pczbbf5/)
> 
> My concern is partly about Jev’s practical value, and partly about Pi’s direction. I’m not yet convinced that Jev brings enough benefit to everyday coding workflows to justify the extra moving parts. What does it meaningfully improve—reliability, cost, latency—and how consistently does that hold up in practice?
> 
> One of the things I like about Pi is its small core, with more opinionated workflows left to extensions. I get that adding a shared classifier API isn’t the same as baking a specific workflow into the agent. But making classifiers a first-class model type still means committing to a shared abstraction, and I wonder whether that commitment came too early.
> 
> The current interface also seems fairly closely modeled on how Jev works today. That might turn out to be a good general design, but do we have enough experience across different implementations and use cases to know which parts generalize well? Classifiers themselves aren’t new; the question is whether this particular interface has had enough room to mature.
> 
> I’d have preferred to see this explored through extensions first, both to establish where Jev actually helps and to learn what a broader classifier API should look like. Was there a particular reason it needed to enter the core model layer at this stage?

> **Popular-Factor3553** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pczktgz/)
> 
> I agree i think it's time someone forks it (pi) and maintains it with a minimalist approach.

> **Apprehensive\_Bed7502** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pczk4ln/)
> 
> Given that [pi has been acquired by a commercial company](https://earendil.com/posts/announcing-pi-and-lefos/), it may keep chasing new hypes, adding more new features to the codebase that nobody knows the point of, just for marketing and raising the product's profile. This runs directly counter to pi's original minimalist philosophy.
> 
> What worries me most is that some new trend gets hyped up, pi immediately jumps on the bandwagon for marketing purposes, and in the end all that's left in the repo are a bunch of features no one will ever look at again once the hype dies down.

> **blakeman8192** · [2026-10-01](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd4zpgz/)
> 
> Given the crazy marketing push (and outright astroturfing) we've seen for Jev, I wouldn't be surprised if TypeSafe AI paid Earendil Labs a nice sum to add support for it.

> **YetiTrix** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd291lm/)
> 
> I mean, can't we just fork it and run our version. It's my MIT license, right?

> **StardockEngineer** · [2026-10-01](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd58dvc/)
> 
> Show me what marketing you’re talking about

> **LittleRoof820** · [2026-10-01](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd9eue5/)
> 
> The original creator Mario Zechner is sitting on the board of Earendil. He wrote a long essay why in [https://mariozechner.at/posts/2026-04-08-ive-sold-out/](https://mariozechner.at/posts/2026-04-08-ive-sold-out/) citing mostly burnout and wanting time for himself (all the Openclaw People kept hammering him with tickets).

> **badlogicgames** · [2026-10-01](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd9uim0/)
> 
> this meme really needs to fucking die.

> **addiktion** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd0mjva/)
> 
> Yeah, I'm not 100% sold on JEV either, but I would say that classifiers probably do play a part in some agentic stacks. I am just not sold that we need another hook in to a commercial entity with yet another network hop to fulfill an already fragile ecosystem as we work to make AI agents more reliable. I'd much rather see Pi leaning on the open source community (laya, kev, iamjev, von, and other flavors) and supporting classifier models that way. Much easier to bundle a small classifier than operates even faster without a network hop and other dependencies. Right now I'm using ollaya to add the endpoint locally and having it tie in the various different classifiers to test them locally, but I suspect in an application it'd make sense to add another monorepo app/package for a given classifier and run it that way.

> **gscjj** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pczhtl9/)
> 
> I disagree in some parts, I’ve already found some use cases like code reviews. It’s can quickly check diffs against a short list of rules and I use confidence values to launch deeper analysis and to create more directed code reviews giving a list of possible issues to my AI code reviewer.
> 
> But I do agree with Pi as a small core, this doesn’t fit the model. Jev isn’t special and nor is a classifier, it doesn’t deserve dedicated code or first class support. It’s just structured output from an API, which can include any number of local and remote uses. Nothing about Pi today prevents its use

> **Healthy-Zebra-9856** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd04ikk/)
> 
> This sub cracks me up. Let me begin by addressing the first thing which is Jev. This is a system one model, and this sort of a thing has been around a lot longer than even Pi itself has been around. There is nothing to worry about here, just like adding every other API, an API was added to this. The second thing that I find is, is this utmost trust in an extension created by someone else. If anything else, that is the first thing you have to be concerned about.
> 
> Your philosophy of trying out an extension before making it part of it doesn’t make any sense because that’s exactly what an extension does. It becomes a part of it, and the damage would’ve already been done. And finally all of this for a coding agent that barely existed for a year. It didn’t even debut till January 2025 and then it gets rolled out in August of 2025 and acquired in September 2025.
> 
> Personally, I’m not a big fan of JEV, because if it’s commercialization and all the shillers being bought out. But its a;lso not a thing to be feared as I have a similar product a lot longer than both these things out there and none of these products , Pi nor Jev have been thoroughly tested. I went through the whole source code, and I am prepared to talk on any part of it. Needless to say, this commercial outfit is going to further commercialize Pi.
> 
> So there is nothing to fear about an entity like JEV,

> **badlogicgames** · [2026-10-01](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd9uh5p/)
> 
> you are not wrong on the classifier model class possibly getting in to early. however, over the past month or so, we've seen many alternative models to Jev pop up, and providers that mirror Jev's API. OpenAI has announced their Decision API 2 days ago, which easily fits into this scheme as well.
> 
> We have also evolved the chat model API over time as new features became available, such as mid convo sytem messages and tool set changes. I expect the same to happen to the classifier model API.

> **Suspicious\_Echidna53** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pczkmew/)
> 
> > I’m not yet convinced that Jev brings enough benefit to everyday coding workflows to justify the extra moving parts.
> 
> if you want to be convinced, check out omp's new `find` tool / the `omp find` command

> **Healthy-Zebra-9856** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd1sm98/)
> 
> These people are too reluctant to learn nor understand anything. BTW I think you were responding to the person I am responding to, right?

> **vexatious-big** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd2h5a3/)
> 
> I'm more impressed with Codemode to be fair. How come no one else thought of this before? It makes so much sense in hindsight, and I agree it needs to be part of the harness to be properly usable.  
> This is what tool calling should be, not just the dumb "search the web/knowledge base/company Jira via MCP and return results".
> 
> As for classifiers like Jev I think they make less sense for individual contributors / developers.  
> Where they excel is at automating business workflows which are currently done via very expensive models. This is the market fit for classifiers. You could automate various workflows by hooking up N8N to Jev and then using large models only for a small subset of the tasks. That's the niche of the market folks like TypeSafe AI are looking to expand into.

> **Apprehensive\_Bed7502** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd2i6a0/)
> 
> CodeAct, i.e. codemode, [was proposed around 2024](https://arxiv.org/abs/2402.01030). And I believe lots of people have implemented their own codeact for pi. The official built-in implementation might conflicts with their own implementations. As for me, that's the situation.

> **vedmaka** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd3caar/)
> 
> Is not codemode a nightmare for approvals?

> **sivadneb** · [2026-10-01](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd46qq1/)
> 
> For someone not familiar with Codemode, care to elaborate?

> **ArthurOnCode** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pczi260/)
> 
> My $.02: Speed is an important feature in coding agents. The human context switch involved when you leave an agent running for long, focusing on other things in the meantime, is a real cost. I wish we could speed things up by converting some of the steps into instant decisions made by a decision model like Jev.
> 
> I'm not sure what that would take, but I fear that it goes against Pi's minimalist principles.

> **puffyfunion** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd253fz/)
> 
> What steps would you convert into instant decisions? Not being facetious, I'm still trying to understand what these new models can do for me.

> **ArthurOnCode** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd2ubm2/)
> 
> That’s up for debate. But I believe the majority of time is spent navigating the code, figuring out which snippets are relevant, and which ones should be edited to complete the task. If these decisions could be made before the first LLM call, I think most coding tasks could be turned into a single structured one-shot call to a strong model, no agent loop needed.
> 
> But that’s just my $.02 :)

> **puffyfunion** · [2026-10-01](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd4jbtx/)
> 
> Can you actually feed a full codebase to Jev with a question about where something is? I should really try playing with this stuff.

> **ArthurOnCode** · [2026-10-01](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd6ikum/)
> 
> I think it'll be a while until we've figured out how to plumb this exactly. It doesn't have to be just one call to a decision model, it can be multiple calls, navigating either folders of code or even the call graph.

> **ResearcherFantastic7** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd3gn08/)
> 
> Before Jev I already have my own bert layer in PI.
> 
> If you use it well a system one layer does a lot more than simple decision engine, you don't need to use Jev.
> 
> Go check out indyDevDan video on how he creatively use it
> 
> But adding MCP in PI does sound like the direction to get bloated, 95% of my use case don't need MCP. It's not hard to use extension. Why can't they just keep it as an extension. A lot of system one use case is a layer prior to llm call or used between operations in hooks

> **Equivalent\_Idea8839** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pczd3ys/)
> 
> Need a debloat guide for pi now, I don't want all this shit

> **Ok-Hippo9182** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pczdu8e/)
> 
> There’s a similar discussion over here  
> [https://www.reddit.com/r/PiCodingAgent/comments/1wtx1tz/pi\_is\_becoming\_bloated/](https://www.reddit.com/r/PiCodingAgent/comments/1wtx1tz/pi_is_becoming_bloated/)

> **ravage382** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pczhinf/)
> 
> Fork it, scrape out the crap you dont like and just setup the git build pipeline for dep rebuilds only.

> **carlocapocasa** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pczgkeh/)
> 
> If I may... mine stays lean. [http://3code.capocasa.dev](http://3code.capocasa.dev/)

> **ChemistryMost4957** · [2026-10-01](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd5pk5u/)
> 
> This looks very good. I'll try it out later - cheers

> **zebedeolo** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pczaef3/)
> 
> I gotta admit, I still am not fully clear on how jev works and why I would pay an extra sub for it. I feel good with my current flow, so I've been too lazy to look it up.

> **debackerl** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pczd8lk/)
> 
> There is zero need to pay for a sub. Those models are small enough to run on a potato. Many available, [https://github.com/wfzyx/von](https://github.com/wfzyx/von), [https://github.com/NandhaKishorM/laya](https://github.com/NandhaKishorM/laya), etc
> 
> LLMs are GenAI. Jev are simply classifiers taking text as input, and zero-shot (so no need to retrain for your classes). Also, the probabilities returned are calibrated (what's the probability that class X is indeed the correct one), LLMs aren't calibrated for that

> **Zestyclose839** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd0aw2c/)
> 
> I tried working in Laya and OpenJev a few days after the Jev hype started - specifically for faster browser use - but the open-weight models just weren't cutting it.
> 
> They either had a minuscule ~1.5k context window, meaning that there's unusable for navigating web pages without aggressive filtering. Or they're using a small language model like Qwen 0.8B, which has a massive context window but are limited to ~16 total decisions vs. Jev's 120+ (most web pages have 50+ links and buttons).
> 
> I ain't rocking with Jev itself because I only run models locally, thus decided the scene needs to mature before these classifier models become viable. Pi is jumping the gun here tbh.

> **addiktion** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd0oym3/)
> 
> I think von scales a bit higher on the decisions but yeah I suspect the local models will find the optimal setup without the commercial cost very soon. Even if Jev is cheap, its a liability that many don't want to have in their stacks. Far better to load in a small classifier more like a dependency than a full service.

> **Zestyclose839** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd25g96/)
> 
> I predict it'll take about a month before the local scene catches up. With LLMs, the limiting factor was raw compute; that's hardly a factor with classifier models.
> 
> What's needed is: 1. an appropriate architecture, 2. training data and RL. Whether they like it or not, people will just start distilling Jev once we have an architecture to train on, closing (and the surpassing) the gap overnight.

> **m02ph3u5** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd39z7c/)
> 
> Can't you just split into 15 + next batch slices?

> **debackerl** · [2026-10-01](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd58tmx/)
> 
> Those that I recommend use ModernBERT or mmBERT, with 8k context (which is enough for my use cases)

> **zebedeolo** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pczl2l0/)
> 
> interesting to know, thanks

> **Stable\_Orange\_Genius** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd01kqd/)
> 
> Is there a use case for coding?

> **addiktion** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd0odah/)
> 
> Yeah, there's use cases for coding for sure around scanning files, setting up guardrails, and routing decisions. I think of it more like a companion for our tooling.

> **debackerl** · [2026-10-01](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd58li2/)
> 
> I still need to try out, but I wanted to write a plugin to auto load the write skills. After each new user message, I could check and auto-inject skills. Of course an LLM can do it, but it would save a turn, so time and cost.

> **ECrispy** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd1wv70/)
> 
> laya isnt pretrained.

> **debackerl** · [2026-10-01](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd593kx/)
> 
> It isn't the vanilla ModernBERT, it's fine-tuned to get callibrated probabilities

> **ramraiderqtx** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pczar8n/)
> 
> If give a percent chance of something, ie. - person on screen holding a gun. What percent is it friendly or foe, so you know shoot or don’t shoot.

> **jaegernut** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pczazzb/)
> 
> So how can this be used in a coding workflow?

> **mraurelien** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pczn4hl/)
> 
> Take a look at this video to get some examples [https://www.youtube.com/watch?v=\_U-O5lYhJ7Q](https://www.youtube.com/watch?v=_U-O5lYhJ7Q)

> **ramraiderqtx** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pczbgpr/)
> 
> I can’t make it any more obvious it’s a decision engine , if you want your agent to make choices based on likelyhoods this is what it is for, as mentioned it’s about helping agents make decisions when humans aren’t around.

> **Apprehensive\_Bed7502** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pczcxrb/)
> 
> Help the agent make decisions? When and why?
> 
> Let's think about when you'd actually need a small model to assist a large one (typically a flagship model) in making a decision. Is it when the permission window pops up?
> 
> When an agent triggers a risky operation that requires user approval, would you really feel comfortable handing that call off to Jev instead of a flagship model with a clean context?
> 
> Jev is nothing but fast and cheap. For approving risky operations, I think it's better left to the LLM's sufficiently smart brain.

> **adamshand** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd2s9q6/)
> 
> I don't use Jev at all in coding, but it's an interesting new thing and I don't think we really understand what it's good for yet.
> 
> I don't understand the current grumps about Pi adding unnecessary things (codemode, mcp etc). Changing your mind as new information becomes available is important. If Pi stays exactly as it is, it's dead. The only way for Pi to stay relevant with all the churn happening with AI is if they continue to experiment. This is how we, and the Pi team, learn.
> 
> Nobody knows what the right way to work with LLMs is yet. We're all flailing around in the dark trying things. Give the team some space to experiment, try the new tools and offer constructive feedback. If you try and don't like them, it's easy to disable things you don't want.

> **Mechanical\_Monk** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd02hlz/)
> 
> Jev seems to be something that you'd package into a product that relies on AI reasoning, but where a full LLM would be overkill and/or a security liability. Every attempt I've made to actually incorporate it into my own coding workflow has resulted in worse performance.
> 
> I ran a reasoning benchmark with four GPT 6 Luna agents--One on Low reasoning, one on Max reasoning, one on Low with access to Jev, and one on Max with access to Jev. The results were about the opposite of what I was hoping to see on both speed and cost. Max with Jev was slowest and most expensive. Next slowest and most expensive was Low with Jev. Second place was Max without Jev. And first place on both speed and cost was Low without Jev.

> **BurnerDev** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd0ax8h/)
> 
> Just with a Jev tool? You can't give them direct access and expect better results, you have to build it into existing tools, which provides better results. Ex: omp's find tool that uses Jev to rank for relevance. These models are going to struggle with direct access because they have no idea what to use it for, and they already are able to reason themselves - if content is already passing into context it's pretty much too late for Jev

> **Mechanical\_Monk** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd0edw2/)
> 
> I mean, that kind of repeats what I said about packaging it into a product. And I'd still have my doubts that a model using a jev-powered find tool would outperform one using a basic find tool and using its own reasoning to determine relevance.

> **pebblechewer** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd0j2op/)
> 
> I'm still trying to wrap my head around Jev and I think I understand it conceptually, so my reply comes with that caveat. . .
> 
> IMHO, Jev belongs in workflows. Using it as part of a business workflow to make weighted decisions is useful in a context of things like security operations workflows, automation, customer service workflows, etc. I believe this offers you some additional flexibility while having the ability to save tokens.

> **Mechanical\_Monk** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd0nkzs/)
> 
> It may, but I suspect using a Jev node in a workflow will underperform a traditional LLM node in most cases. I would have said Jev might save on cost, but I don't even know if that's true now that GPT 6 Luna is so cheap.

> **BurnerDev** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd0lblh/)
> 
> That's fair, but I think we'll see some good common use cases come up as people play with it

> **ECrispy** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd1wrgs/)
> 
> what the hell is this nonsese? Jev is an llm with an api, there is absolutely zero reason to hardcode support for it.
> 
> oh wait, there is one - to cash in on the Jev hype.
> 
> so whats next, Pi adds support for Opus 6 next? and perhaps special access to their hosting partner or sponsor?

> **TechGearWhips** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd3i95m/)
> 
> THANK YOU. I am so sick of seeing this Jev bs being spammed all over my fucking feed. It’s like the ai version of Omarchy

> **ECrispy** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd3j473/)
> 
> dont give that jerk dhh more ideas. they'll add another 'feature' to omaaaaacheee.

> **TechGearWhips** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd3k1e7/)
> 
> Yea you’re right bro. Let me shut the fuck up

> **neuronexmachina** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd1sh25/)
> 
> Relevant docs: [https://pi.dev/docs/latest/llama-cpp#classification](https://pi.dev/docs/latest/llama-cpp#classification)
> 
> I think it's pretty clear that it's intended for classifiers in general, not just jev.

> **Apprehensive\_Bed7502** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd21m44/)
> 
> Just read some code. I used local installation from `node_modules`:
> 
> `node_modules/@earendil-works/pi-ai/dist/api/llama-cpp-classify.js:144`:
> 
> ``javascript /** TypeSafe's documented choice confidence, `(n * peak - 1) / (n - 1)`, clamped to [0, 1]. */ export function peakConfidence(probabilities) { const n = probabilities.length; const peak = Math.max(...probabilities); return Math.min(1, Math.max(0, (n * peak - 1) / (n - 1))); } ``
> 
> Typesafe documented.
> 
> ---
> 
> `node_modules/@earendil-works/pi-coding-agent/docs/llama-cpp.md:91`:
> 
> > Classifier models answer typed choice, bool, and score questions about JSON state, like TypeSafe's Jev models.
> 
> ---
> 
> `node_modules/@earendil-works/pi-ai/dist/api/system-one-shared.js:108`:
> 
> ``javascript /** Maps public `bool` questions to TypeSafe's wire-level `noul` type. */ ``
> 
> parsing arguments `system-one-shared.js` vs `llama-cpp-classify.js`:
> 
> | type | jev parsing | llama.cpp parsing |
> | --- | --- | --- |
> | choice | `choice`, `probabilities`, `confidence` | same arguments |
> | score | `score`, `confidence` | same arguments |
> | bool | `noul` -> `probability` | directly returns `probability` |
> 
> ---
> 
> It's all about jev, nothing general I think.

> **neuronexmachina** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd3swyq/)
> 
> Yes, llama-cpp and pi are using the jev wire format for classifiers. Is there an alternative wire format they should use instead?

> **\_reg1z** · [2026-10-01](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pdaz4ie/)
> 
> jev popularized the concept first, so tech deriving from it will inherit its shape. This has been the case in software forever. This is how standards form. Its why json is usually used instead of something more token efficient. Its why most harnesses/providers use the openai API format as standards. Its necessary for interoperability. Why reinvent the wheel? The underlying shape of the tech is the same.

> **Zestyclose\_Potato794** · [2026-10-01](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd72pcr/)
> 
> Pi was bought. Enshitification has begun. Time to fork. 0.87.1 is probably the last know good release.

> **Electronic-Pie-1879** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pczik4h/)
> 
> OMP is using Jev as a semantic grep replacement. `find` is essentially semantic grep for your codebase. Instead of knowing an exact identifier or string like with grep, the agent can describe the behavior it wants to locate:
> 
> "where is authentication handled?" "where do we retry failed API requests?" "what code decides which model to use?"
> 
> OMP then returns the most relevant files and exact line ranges, ranked with relevance probabilities.

> **Stevie2k8** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd0iimc/)
> 
> That's exactly what zvgrep from alibaba does apart from some other nice and intelligent search things. Running as mcp within my opencode instances and saves constantly tons of tokens and time.... [https://github.com/zvec-ai/zvec-grep](https://github.com/zvec-ai/zvec-grep)

> **puffyfunion** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd295a4/)
> 
> These are really good use-cases. Finally, concrete information, thanks.

> **capsid** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd01t5p/)
> 
> neat. Seen any data on how well this works vs regular grep?

> **Beneficial\_Mix3375** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd0vgf5/)
> 
> Jev and laya have been a considerable boost in my compaction, routing and computer use.
> 
> I can't see how is not insane as an upgrade. I don't need to "use" it, it's integrated, prev with my own extensions and now built in

> **puffyfunion** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd258gg/)
> 
> Can you elaborate on how you use these models?

> **Beneficial\_Mix3375** · [2026-09-30](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd264e1/)
> 
> I've just literally wrote the 3 main areas. Is widely available online, even for pi specifically. Pi fast jev compaction and alikes. I prefer to build my own but again, im not a gpt model

> **puffyfunion** · [2026-10-01](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd4j3xz/)
> 
> I meant specifically what do you do with it, e.g for computer use.

> **Beneficial\_Mix3375** · [2026-10-01](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd556rs/)
> 
> It reads accessibility trees faster and acts with no llm. Nothing new under the sun, you can find many such usages online, not sure why you so obsessively asking about my specifics

> **BodyCreative2665** · [2026-10-01](https://www.reddit.com/r/PiCodingAgent/comments/1wu22ag/pi_now_supports_jev/pd56bl8/)
> 
> it help reduce token for think and speed up my task with jev/laya in pi.
