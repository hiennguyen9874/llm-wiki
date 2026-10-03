---
title: "I reviewed 287 open-source Jev projects. Here are 20 that actually helped me understand what Jev is good at"
author: "chenrongwei"
site: "r/LLMDevs"
source: "https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/"
domain: "reddit.com"
language: "en"
description: "I’ve spent the last couple of days going through open-source projects built around TypeSafe Jev. The list started with 14 projects. It’s now"
word_count: 4525
---

I’ve spent the last couple of days going through open-source projects built around TypeSafe Jev.

The list started with 14 projects. It’s now at **287**, and I’ve been checking the public source for each one to make sure Jev is actually integrated, not just mentioned in a README.

After looking through all of them, I think the easiest way to understand Jev is not by reading the model announcement.

It’s by looking at what developers are actually using it for.

The pattern is pretty consistent.

Jev is rarely the thing writing code, generating long text, or doing the heavy reasoning.

It usually sits inside a loop and answers much smaller questions:

**Which action? Which file? Keep or drop? Safe or unsafe? Route to which model? What should happen next?**

So if you just got API access and have no idea what to build with it, these are the 20 projects I’d look at first.

I didn’t rank them by GitHub stars. I picked the ones that are easy to understand, show a clear advantage of Jev, or are just genuinely interesting.

# 1\. jev-ultrafast

Probably the clearest Jev demo so far.

Browser Use gives Jev the current DOM and asks it what action to take and which element to act on. A small text model is only called when the browser actually needs to type something.

One Google Flights demo completed a Zurich → London search in about 7 seconds.

What I like about this one is how clean the split is.

Jev decides. Code executes. A generative model only gets involved when generation is actually needed.

# 2\. fast-jev-compaction

This one uses Jev for Claude Code context compaction.

Instead of asking another LLM to summarize a huge context window, it scores old tool calls and outputs and decides what can be dropped.

The text that survives stays unchanged.

So paths, commands and error messages don’t get rewritten into a potentially lossy summary.

This feels like a very natural Jev use case.

# 3\. json-render + Jev

Vercel Labs experimented with using Jev inside json-render.

Instead of streaming a full UI spec token by token, Jev chooses from predefined components and properties, then normal code assembles the interface.

In their train-ticket demo, the default JSONL path took 3.21 seconds. The Jev version took 0.88 seconds.

This is probably the most interesting example I’ve seen of Jev being used for generative UI without actually generating the UI itself.

# 4\. typesafe-mcp

Probably the easiest place to start if you already use Claude Code, Codex or Claude Desktop.

It exposes Jev through MCP, so an agent can ask typed Choice, Score or Noul questions and use the returned probabilities inside its own workflow.

Basically, it turns Jev into a decision tool that another model can call.

# 5\. jev-mcp

A more opinionated MCP implementation.

It already packages several useful patterns around Jev, including evidence checking, content screening, reranking, classification and extraction.

If you want to see what Jev looks like as an actual Agent tool rather than just an API, this one is worth reading.

# 6\. SemDecide

Jev as a Unix-style command-line utility.

You can pipe text into it and ask semantic yes/no questions, classify things, score them, filter rows or use it as a guard.

This is one of the projects that made Jev click for me.

A lot of tasks that currently require a full LLM call could eventually look more like:

`grep → jq → Jev → next step`

# 7\. Jev Codex Router

A model router for coding tasks.

Jev first judges how difficult a turn looks, then the request can be sent to a cheaper or more capable model.

This is a good example of Jev sitting in front of expensive models rather than competing with them.

The expensive model still does the work. Jev just decides who should get the work.

# 8\. Winnow

A context garbage collector for coding agents.

When Read, Bash or Grep dumps a lot of content into the context window, Jev judges which pieces are actually relevant to the current task.

The idea is simple: stop paying a frontier model to repeatedly read garbage.

# 9\. Jev Review

Uses Jev as a first-pass code review filter.

Instead of throwing every diff directly into a larger model, Jev can first score things like correctness, security, reliability and test risk.

The interesting part isn’t replacing code review.

It’s deciding **where expensive review is actually worth spending tokens**.

# 10\. Blink

A semantic navigator for codebases.

At every directory level, Jev decides which files or folders are most likely to contain the answer, then continues searching from there.

It’s basically using Jev as a lightweight semantic routing layer over a repository.

# 11\. jev-desktop

Jev for desktop automation.

The system reads native accessibility information, gives Jev a bounded set of controls and actions, then lets Jev choose what to interact with next.

The full UI tree doesn’t need to live inside the main agent’s context.

Again, the pattern is the same: perception and execution stay deterministic, Jev handles the choice in the middle.

# 12\. typesafe-mario

Jev playing Super Mario Bros.

Instead of feeding it screenshots, the system turns emulator RAM into structured state and asks Jev which controller action to take.

This is less practically useful than some of the projects above, but it’s a very good demonstration of Jev as a low-latency decision model.

# 13\. jev-drone

A drone project using Jev for higher-level tactical decisions.

Classical vision and control systems still handle perception and flight stability.

Jev gets a simplified state and chooses actions like climbing, braking or navigating through a gap.

I like this one because it shows where Jev probably belongs in robotics: not replacing the flight controller, but sitting one level above it.

# 14\. OneVOneJev

A browser-based 1v1 FPS where Jev decides movement, view direction, aiming, firing and jumping.

It’s basically a continuous stream of bounded decisions.

Again, this is the kind of workload where token-by-token generation would make very little sense.

# 15\. jev-trader

A market-making experiment on Monad testnet.

Jev reads things like spread, rolling returns and taker flow, then predicts short-term market direction and helps decide buy/sell behavior.

I wouldn’t treat this as evidence that Jev has alpha.

What’s interesting is the architecture: structured market state in, rapid probabilistic decision out.

# 16\. Prism

Another finance-related project, but I actually find this one more interesting architecturally.

Jev is used as an advisory probability layer for things like toxic flow, market stress and mean-reversion conditions.

The deterministic strategy still owns execution.

This is probably how I’d experiment with Jev in quantitative systems too: use it as another signal, not as the trader.

# 17\. neo4jev

Jev inside a knowledge graph.

At every node, it scores which outgoing edge is worth following next, then a beam search continues from the strongest candidates.

It’s basically semantic pathfinding.

This is one of those projects that makes you realize Jev doesn’t have to be an “AI app” at all. It can just be a tiny decision primitive inside a normal algorithm.

# 18\. jev-curate

Uses Jev to filter training data.

Rows from large datasets can be scored for quality, relevance or other criteria before expensive model training starts.

This is another place where cheap repeated judgments matter more than generating beautiful language.

# 19\. Canny

This one tries to stop coding agents from claiming they’re done when the evidence says otherwise.

It looks at things like tool output, diffs and test results, then judges whether the agent’s completion claim is actually supported.

I think this general pattern has a lot of potential.

Agents increasingly need lightweight referees inside their loops.

# 20\. killmyidea

Probably the least serious one on this list, but very easy to play with.

You describe a startup idea, Jev scores it across several dimensions, and local logic turns those scores into one of three labels:

**KILL, FIX, or SHIP.**

It’s a nice small example of the broader pattern: use Jev for a set of structured judgments, then let code decide what those judgments mean.

After going through these projects, my mental model of Jev is much simpler than when it launched.

I don’t really think of it as a chatbot competitor.

I think of it as something closer to a **general-purpose semantic decision function**.

You give it a state and a bounded question.

It gives you a probability, score or choice.

Then your software decides what to do next.

That’s why a lot of the most convincing Jev projects look like this:

**big model → Jev → code → Jev → tool → Jev → big model**

The large model handles the parts that actually require generation or deeper reasoning.

Jev handles all the little decisions in between.

I’m maintaining the full list here:

[https://logicrw.github.io/awesome-jev-projects/?lang=en](https://logicrw.github.io/awesome-jev-projects/?lang=en)

GitHub:

[https://github.com/logicrw/awesome-jev-projects](https://github.com/logicrw/awesome-jev-projects)

There are **287 source-reviewed projects** in the directory right now, grouped by use case.

If you’ve built something interesting with Jev that I missed, send it over. I’m still adding new ones.

---

## Comments

> **smashedshanky** · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/patdhni/)
> 
> The number of Jev posts I’m seeing are increasingly looking and reading like ads…

> **Subsector3990** · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pau240c/)
> 
> it's the one truly different development in this space we've had in a while. it's an interesting proposal at least, and ppl are rushing to digest it. i've yet to test it for myself, but it's the first time since like Opus 4.5 that i've been truly surprised by a release.
> 
> i'll have to test it for myself before i believe the hype. but it's at least cool to see that people aren't just rabbitholing down larger and larger models without innovating.
> 
> this specific post is slop though.

> **Trainer\_Intelligent** · [2026-09-23](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbmr2uc/)
> 
> well said sir

> **Typical-Code-7006** · [2026-09-26](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pc5j5jq/)
> 
> thought provoking

> **bobo-the-merciful** · [2026-09-21](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pb2fqjf/)
> 
> I've made two of these ads myself and I have no affiliation with Jev. Make of that what you will.

> **Prestigious\_Ad8317** · [2026-09-24](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbpeheg/)
> 
> You know what? You could build a jev-based content filter and get rid of those 🎯

> **SquirrelGuy** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pawhue4/)
> 
> This Jev shit is being astroturfed so hard. Tons of bots in the comments defending the posts too.

> **bobo-the-merciful** · [2026-09-22](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbdiic6/)
> 
> Hi I'm one of those bots

> **x2040** · [2026-10-01](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pd8vny7/)
> 
> This is why a lot of engineers aren't gonna survive the AI transition.
> 
> Zero product thought. Zero imagination.
> 
> "This didn't cost 7 trillion to train and therefore any positive press is a lie"
> 
> Bro maybe think about the use cases this can enable and propose an alternative to the use cases above. If you can't, that means it's solving something no one did before.

> **fredjinsan** · [2026-09-25](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pc2lcdn/)
> 
> Is it just me or does this whole post read like it was, in turn, written by an AI? Jev sounds great (and, like, a fairly obvious next/old step for AI), but do humans actually write stuff like
> 
> > What I like about this one is how clean the split is.
> 
> Jev decides. Code executes. A generative model only gets involved when generation is actually needed.
> 
> ?

> **Smallpaul** · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pasdyf5/)
> 
> “Jev is rarely the thing writing code, generating long text, or doing the heavy reasoning.”
> 
> Rarely??? Show me a single example of it doing any of those things please. Jev writing code sounds wild.

> **radarsat1** · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pata615/)
> 
> you quoted the line that convinced me the whole post is from an agent. well, also the claim that it "reviewed" 287 projects in 2 days

> **ehs5** · [2026-09-27](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pcbu5uk/)
> 
> They has the agent search for Jev is what they meant.
> 
> Which tbf is not nothing, I found the post interesting. But it is misleading.

> **Mpmpz\_14** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pb049lr/)
> 
> It doesn't actually write any code. I still don't really understand why people still misunderstand what Jev is.

> **Short-Balance-1542** · [2026-09-26](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pc7eckf/)
> 
> I think people are just randomly pasting some LLM generated shit here!

> **phillipw12** · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pasmhe3/)
> 
> I was thinking about abusing jev to make it autoregressive
> 
> Give it a state to continue and give it a list of output tokens it can use I.e alphabet, then repeat the request appending the token each request until complete.

> **Substantial\_Sea\_9758** · [2026-09-21](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pb2oi6q/)
> 
> If you do that, you will suspiciously find out the result is 1:1 DeepSeek V4 Flash

> **susumaya** · [2026-09-21](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pb32s3x/)
> 
> The alpha bet? Or the thesaurus?

> **Smallpaul** · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pasooi0/)
> 
> Yes but why?

> **phillipw12** · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pasr2yg/)
> 
> More of a why not

> **Short-Balance-1542** · [2026-09-26](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pc5xs1k/)
> 
> Yeah, I was so confused reading this, I feel like I am a fool. I did my research on the first day, and clearly it is not a language model, right?

> **Smallpaul** · [2026-09-26](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pc7536o/)
> 
> Jev is not a traditional language model although it takes language on input so you could argue it is still in the language model family. But it does not output language unless you do some insanely gross and non-sensical hacks.

> **jackorjek** · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/paso0kc/)
> 
> someone made a post about its output in writing a few days back. the tps is slow though. its in [r/LLM](https://www.reddit.com/r/LLM) i think

> **Substantial\_Sea\_9758** · [2026-09-21](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pb2p77f/)
> 
> Jev is a flash LLM wrapped into a defined output wrapper and limited to generate only 1 token. If you try to \_unwrap\_ it back you'll get DeepSeek V4 Flash.

> **the\_mighty\_skeetadon** · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/paukcrg/)
> 
> I mean how? It only has scoring and classification abilities, how would it create text? Classify likely next words?

> **jackorjek** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pavesk5/)
> 
> looks like it
> 
> [https://www.reddit.com/r/LLM/s/nwpvpgIyjd](https://www.reddit.com/r/LLM/s/nwpvpgIyjd)

> **the\_mighty\_skeetadon** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pavmc7e/)
> 
> Lol, absurd.

> **NewspaperFirst** · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/patqenj/)
> 
> Slop ads.

> · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/patjhpg/)
> 
> \[deleted\]

> **chenrongwei** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pay1ayw/)
> 
> Thanks for sharing! Cool to see more Jev stuff around.

> **allenasm** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pav8ql7/)
> 
> The marketing budget for the Jev stuff appears to be unlimited.

> **Best-Definition2886** · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pas45eg/)
> 
> This is really good breakdown. I been trying to figure out what Jev actually does different and the way you describe it as decision function makes more sense than any official explanation I read. The split between Jev deciding and code executing is what clicked for me
> 
> The json-render example is wild, 3.21 seconds down to 0.88 just by not generating the UI itself. That kind of speed difference actually matters for real apps
> 
> I think the router and compaction ones are where most people will start though. Nobody wants to burn expensive model tokens on stuff like "is this log file relevant" or "should this go to the cheap model first"
> 
> Bookmarked your list. Might try the MCP one since I already use Claude Code for most things

> **krahsThe** · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pau51gz/)
> 
> But why can it do it better than a large llm? Pr is the claim simply that it is cheaper and faster?

> **Yamoyek** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pawvth0/)
> 
> Faster, cheaper, and somehow they’ve made it so it doesn’t hallucinate which you have to account for with regular LLM structured outputs.

> **Any\_Owl2116** · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pas9abt/)
> 
> Thanks

> **VergeOfTranscendence** · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pasixwu/)
> 
> What about cactus needle?

> **chenrongwei** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pay1k1a/)
> 
> Actually did a thread on it recently:  
> [https://x.com/0xLogicrw/status/2101173982548349216](https://x.com/0xLogicrw/status/2101173982548349216)

> **islandirie** · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/paskdto/)
> 
> Awesome, thanks for sharing. I just joined waitlist , can't wait too try it out.

> **Substantial\_Sea\_9758** · [2026-09-21](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pb2r2g4/)
> 
> You can use it on openrouter today.

> **serendipity98765** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pavb5wz/)
> 
> Has anyone tested it as a router to see how it performs ? Does it get through cloudflare protections and such

> **Any\_Foundation\_5738** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pavdqkn/)
> 
> amazing

> **hellomistershifty** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/paw52gv/)
> 
> The MCPs seem kind of silly because the agent already needs to construct the input and pose the question, so it's already spending more output tokens to ask a dumber model than if it just answered itself

> **Nedomas** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/paxs668/)
> 
> Could you review Supercov? It’s code quality/coverage for coding agents via Jev, imho one of better use-cases [https://github.com/supercorp-ai/supercov](https://github.com/supercorp-ai/supercov)

> **chenrongwei** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/paxyo85/)
> 
> Already listed: [https://logicrw.github.io/awesome-jev-projects/en/projects/supercorp-ai/supercov/](https://logicrw.github.io/awesome-jev-projects/en/projects/supercorp-ai/supercov/)
> 
> 100% agree, grounding agent patches in real runner coverage is way better than vibe-checking tests with a prompt.
> 
> [https://preview.redd.it/lg94t1svxnqh1.png?width=1122&format=png&auto=webp&s=c6d3d516a6eb464fc6a6f6450607988c2f2ece9a](https://preview.redd.it/lg94t1svxnqh1.png?width=1122&format=png&auto=webp&s=c6d3d516a6eb464fc6a6f6450607988c2f2ece9a)

> **MultiBotRun** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pay01t1/)
> 
> replace JEV! There is another project, and it is open source! Search for “Laya” on Hugging Face. The author had already published a paper on arXiv in March 2025.

> **Kamikaze-front** · [2026-09-22](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbfz4f4/)
> 
> Tanks!!

> **BlankedCanvas** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pazcdey/)
> 
> [https://giphy.com/gifs/S2E0EucjhwJR6X9PBW](https://giphy.com/gifs/S2E0EucjhwJR6X9PBW)

> **Necessary\_Row475** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pazlue2/)
> 
> Dont understand why people are "upset" about posts about it, nobody said you have to use it. But I really think the concept is what AI should be working towards. Instead of generalized use, like having AI the ability to answer everything, it should always have been limited to what its presented with. This allows for limited context, and prevents hallucination. It makes so much more sense as a useful tool compared to having AI know everything in the world. As of now i think the gap is people are not use to how to integrate it like a LLM, but i am really surprised at some of the items off yibie/awesome-jev list.
> 
> what first caught my eye was fast-jev-compaction on github trending list. Decide to search what other people are using. My mind only thought of answering business questions by customers, and as i use opencode free model require a lot compaction. The concept of using it as a decision maker on what stays in context is freaking genius.
> 
> Like stated in the post, most uses are using it to make decision for the llm. Currently, i would have to see the recommendations and decide. If this really works well, i cannot imagine a world where anyone even does anything related to coding. Im just realizing this as I am writing this. Omg if you have jev look at your requirements, have LLM ask it to make core level decisions. Even having a developer in the loop is obselete... Ggwp.

> **ddx1v** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pazmqy7/)
> 
> I am going to give Jev a test run, thanks for sharing!

> **Charming\_Group\_2950** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pb05978/)
> 
> Calibrated AI evaluation using Jev. [https://github.com/TrustifAI/typed\\\_evals](https://github.com/TrustifAI/typed%5C_evals)

> **Mpmpz\_14** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pb05d9m/)
> 
> Well, I did try to find all Jev builds on any major platform:
> 
> 1,305 Jev builds, demos, tests, and guides from X, LinkedIn, and GitHub.
> 
> 764 X posts, 392 LinkedIn posts, and 149 GitHub repos covering agents, browsers, evals, games, research, trading, routing, and a lot of crazy experiments.
> 
> If you wanna check it out, give it a try here (PS: it´s way much better than the above, and yes... I used Jev to score the Jev builds 😂)
> 
> [https://www.ayautomate.com/jev-builds](https://www.ayautomate.com/jev-builds)

> **Actual\_\_Wizard** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pb27z34/)
> 
> Wow, so Jev is blowing up huh? Who would have thought that?

> **nitish-kmr** · [2026-09-21](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pb3zi2m/)
> 
> The pattern you pulled out is the right one, and there is one thing missing from almost every project on the list.
> 
> Nearly all of them gate on the confidence value. Route above 0.8, escalate below. That is a calibration claim: among the calls that come back at 0.8, roughly 80% ought to be correct. Nobody has published a reliability diagram for this model, so every threshold across those 287 repos is currently a guess wearing a number.
> 
> It is an afternoon to check against your own data. Take a few hundred decisions where you have the outcome, bucket them by reported confidence, and plot accuracy per bucket against the diagonal. If it tracks, your threshold means what you think it means. If it is overconfident through the middle of the range, which is where most production traffic sits, everything you routed at 0.7 went where it went on worse evidence than you believed.
> 
> The other thing worth building in from the start, given the architecture you describe. When the decision model routes wrong, the large model never sees that case, so the failure does not show up anywhere in your normal logs. It just becomes a slightly worse outcome that nobody traces. Log every decision with its confidence and its eventual outcome, and sample both sides of your threshold. Otherwise the cheapest component in the stack is also the only one you cannot watch fail.

> **jonah\_omninode** · [2026-09-21](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pb6tzns/)
> 
> The recurring pattern here is more important than the project count: JEV is most useful where the action space is already bounded and the runtime can verify the consequence. The router, compaction, and review examples all fit that shape.
> 
> I would be careful with benchmarks that stop at the decision itself, though. The useful metric is whether the downstream task was accepted without repair, including the cost of fallbacks and retries.

> **Appropriate\_Joke2454** · [2026-09-21](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pb76e6k/)
> 
> Can someone explain to me how jev does compaction when it's context window limit is 1/30th the size of most llms

> **tom\_reddit** · [2026-09-21](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pb8h6d0/)
> 
> [https://preview.redd.it/s6eg64kbnxqh1.png?width=1572&format=png&auto=webp&s=10e279e768851f264f026a354528731d2c383311](https://preview.redd.it/s6eg64kbnxqh1.png?width=1572&format=png&auto=webp&s=10e279e768851f264f026a354528731d2c383311)
> 
> You can add Slop Mop to your project list. A Jev based free and open-source tool to help with our LinkedIn feeds... [https://slopmop.lol](https://slopmop.lol/)

> **trustedrails** · [2026-09-22](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pb9rf7e/)
> 
> Love the idea of analyzing the DOM and passing the results to you. Looks like a great use case

> **Strange\_Tap7873** · [2026-09-22](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pba2m4z/)
> 
> I just open-sourced a weekend prototype: [https://github.com/fabiocmazzo/maskdecide](https://github.com/fabiocmazzo/maskdecide)

> **rubanbhatia** · [2026-09-22](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbaujvl/)
> 
> I built a simple router using Jev as well, started off as a jev experiment but now I’ll add support for other system one models.
> 
> For everyone who defaults to picking the best model+effort because they are unsure, this one is for you: [https://github.com/ruban-24/switchboard](https://github.com/ruban-24/switchboard)

> **impara1** · [2026-09-22](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbbifci/)
> 
> Literally all ai suggested something similar there are no moats anymore

> **rubanbhatia** · [2026-09-22](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbbip6m/)
> 
> haha agreed, I also feel AI suggests similar because we ask it to find problems to solve and model routing is a big one.
> 
> Personally for me the problem was that I had to choose model+effort upfront for every task and more often than not, I would choose the best ones to play it safe.
> 
> Was an ok habit when AI was heavily subsidized but with rate limits reaching record low values, I don’t think that attitude will take me very far😂

> **rubanbhatia** · [2026-09-22](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbbi6ac/)
> 
> Another interesting use case was for model routing with Jev, I know some projects have popped up but I ran a few hundred experiments comparing DeepSeek flash (which I was using previously for routing) to Jev and was quite happy with the results. I’ll be publishing some metrics soon
> 
> But I open sourced my work for free here: [https://github.com/ruban-24/switchboard](https://github.com/ruban-24/switchboard)
> 
> When I started this only Jev was available but now I see Laya, Kev and CUA-S1 popup so keen to run some experiments on model routing with those as well. Stay tuned!

> **Crescitaly** · [2026-09-22](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbbpx7r/)
> 
> AI-assisted comment, based on the compaction examples: I'd want pruning to be reversible. Could the agent keep lightweight references to discarded tool outputs and retrieve them when a later failure changes what matters? A useful stress test would introduce a bug whose explanation was discarded earlier, then measure whether the system recovers it without restarting the task.

> **authentic\_developer** · [2026-09-22](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbbyjcs/)
> 
> The "Jev rarely writes code but sometimes does" line is doing a lot of work here with no example behind it. A typed-decision model doesn't generate code, that's the whole point of it. Where it's actually earned its place in stuff I've shipped is the boring gate work: is this request in scope, which of these five branches, does this need a human. Anything that has to emit a string, you're back on the LLM. Worth separating what it decides from what still generates, because the post blurs those.

> **unbenannt1** · [2026-09-22](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbc5nvm/)
> 
> I integrated Jev with the Smart Home AI assistant I am building (think open source Alexa).
> 
> Previously every user prompt was handled by an LLM and that did the MCP tool calls to switch smart home devices.
> 
> But this was far from instant, a few seconds would pass until something physical happened, especially annoying when entering a dark room and asking to turn lights on...
> 
> Now Jev is called before the LLM to switch devices *instantly*, while still routing non-device tequests (weather, ...) to the LLM:
> 
> Decision Structure (single request): \* Noul: is\_device\_control\_request \* Choice: list of every device's json definition (name, description, room, type, ...) + a "no match" dummy device \* Choice: wants\_on, wants\_off, wants\_numeric (for dimmers)
> 
> Jev makes its decision and when its confident I directly performs the control action, I then just pass a modified prompt to the LLM to speak out the action that was performed. If Jev is uncertain or if the request is not device related, its passed down as-is to the LLM, same as before.
> 
> Works really well so far!

> **wandofcatcontrol** · [2026-09-22](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbe31ex/)
> 
> I've heard a lot of hype about Jev recently, but I haven't really understood what it is or why it's different. This post really clarified a lot for me.

> **peeeanuts** · [2026-09-23](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbi1v71/)
> 
> On fast-jev-compaction (#2): at its default 0.5 keep cutoff we sent 120 tool calls through its scoring and it kept none of them.
> 
> I reviewed this plugin for GitTested: [https://gittested.com/reviews/fast-jev-compaction/](https://gittested.com/reviews/fast-jev-compaction/)

> **paperstudio\_jen** · [2026-09-23](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbjcfi1/)
> 
> Yes but the problem is giving it enough data in the first place

> **Trainer\_Intelligent** · [2026-09-23](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbmqxl1/)
> 
> guys hating on Jev without trying it out is wild. If you have built agents that go to prod from scratch you would actually understand the pain behind those JSON outputs, the string parsing, the contract shape validation, the repair prompt just because you are looking for a label and when the label finally comes it is hand-waved by an LLM. Humbly submitting this as a maintainer of a new oss agent runtime [https://github.com/Prescott-Data/jarviscore-framework](https://github.com/Prescott-Data/jarviscore-framework)

> **RelativeValuable5919** · [2026-09-23](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbnnfxq/)
> 
> Hi everyone, I've been buillding desktop assistant a launcher styled AI assistant that uses decision models like Jev and neelde 3 as a layer before the chat model — for jobs like routing a request to a specific model, auto-send, auto-speak on request, and custom "when X do Y" rules.
> 
> It's open source (Apache-2.0): [github.com/neuronection/desktop-assistant](http://github.com/neuronection/desktop-assistant)

> **MarcinFlies** · [2026-09-24](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbq3yfb/)
> 
> what about laya-mlx?

> **brookm291** · [2026-09-24](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbsbsii/)
> 
> [u/chenrongwei](https://www.reddit.com/u/chenrongwei)  
> Thanks for summary.  
> However, there is this one focus  
> on production level tooling for jev:  
> [https://github.com/v-modal/awesome-jev-tools/](https://github.com/v-modal/awesome-jev-tools)
> 
> You should have a look !

> **alangibson** · [2026-09-24](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbsoknb/)
> 
> Dear JEV employee/contractor/paid shill,
> 
> Thank you for astroturfing this thread. Your promotional content has been noted. Now please stop, we are sick of it.

> **Altruistic-Buy-8700** · [2026-09-25](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbxpxrn/)
> 
> I created a YouTube comment analyzer using the provided video link:  
> Free live: [https://jevpulse.vercel.app/](https://jevpulse.vercel.app/)  
> GitHub: [https://github.com/jaygajera17/JevPulse](https://github.com/jaygajera17/JevPulse)

> **Tasio\_** · [2026-09-25](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pbyhewq/)
> 
> I wonder if there is a chance that this account is purchased or stolen. In the past, when I’ve come across suspicious posts that looks like an ad, I’ve noticed that the accounts often have long periods of inactivity.

> **SuspiciousOctopuss** · [2026-09-27](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pcettdu/)
> 
> Did you... make Jev curate this list?
> 
> ... and then hand that to an bigger model to write a post? :)

> **godwin-pinto** · [2026-09-30](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pczlb8f/)
> 
> It’s meaningful for cases where decision can be arrived and in our product we’ve made jev live in production but optional.
> 
> Because i run a feedback platform we build usecase around this if you want to checkout. No login.
> 
> The below link showcases Just the possibilities where speed and cost benefits outweigh compared to a traditional llm( system 2 models).
> 
> [https://encatch.com/encatch-system-one-playground](https://encatch.com/encatch-system-one-playground)

> **Background-Log6333** · [2026-10-01](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pd7h3g6/)
> 
> Okay ChatGPT, now resume this

> **QuanTradin** · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pas8l9d/)
> 
> checking the public source of each one instead of trusting the README is the part that makes this worth reading, and it's the part nobody doing these roundups actually does. most awesome-x lists are a list of repos that mentioned x once in a feature bullet.

> **Soggy\_Violinist\_1807** · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/patacdt/)
> 
> Here's what I am working on: [https://github.com/rajdhakad9826/jev-router](https://github.com/rajdhakad9826/jev-router)

> **chenrongwei** · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pay0l36/)
> 
> Merged: [https://logicrw.github.io/awesome-jev-projects/en/projects/rajdhakad9826/jev-router/](https://logicrw.github.io/awesome-jev-projects/en/projects/rajdhakad9826/jev-router/)
> 
> Love that you used expected loss instead of just picking the top probability.
> 
> [https://preview.redd.it/31skq4pm0oqh1.png?width=1114&format=png&auto=webp&s=e446db54b6028c819675d628e23b631a27c12d46](https://preview.redd.it/31skq4pm0oqh1.png?width=1114&format=png&auto=webp&s=e446db54b6028c819675d628e23b631a27c12d46)

> **autorokk** · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pauv9r4/)
> 
> [https://www.youtube.com/watch?v=tjX3UoD7HPQ](https://www.youtube.com/watch?v=tjX3UoD7HPQ)
> 
> something cool i've been working on.
> 
> i explain a bit about the problem it is solving in this project here: [https://www.reddit.com/r/ultimaonline/s/EVC3Lje1TG](https://www.reddit.com/r/ultimaonline/s/EVC3Lje1TG)

> **LongjumpingEar6840** · [2026-09-19](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/patkkt9/)
> 
> Praticamente stravolgerà gli agenti di coding e potenzialmente li porterà ad un livello di efficienza inimmaginabile...

> · [2026-09-20](https://www.reddit.com/r/LLMDevs/comments/1wko2e5/i_reviewed_287_opensource_jev_projects_here_are/pax46mb/)
> 
> \[deleted\]
