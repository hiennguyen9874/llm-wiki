---
title: "Anyone here using Jev?"
author: "o_sht_hi"
site: "r/PiCodingAgent"
source: "https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/"
domain: "reddit.com"
language: "en"
description: "I read the release and saw a few demos on X for people using Jev for really interesting stuff. My current effort is to get it to work as a r"
word_count: 2706
---

I read the release and saw a few demos on X for people using Jev for really interesting stuff. My current effort is to get it to work as a router so I can configure and orchestrate my app using natural language (getting it to take a string and pick the right API from a list of 250-300 calls). But to be clear, I haven't gotten access to it yet. So I'm just packaging up my code and making it ready rn.

Anyone doing something fun/interesting with it yet? If yes, how long did it take for you to get access

---

## Comments

> **lovelace6329** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paiv33r/)
> 
> I submitted the request yesterday and was granted access five hours later. 2 others colleagues got it straight away. I'm going to try it out on matching job vacanciers with cvs.

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paiwwmb/)
> 
> Nice. That's a very grown up use case 🌚

> **lovelace6329** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paiyov1/)
> 
> Indeed, it might be a bit too ambitious

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paj14y0/)
> 
> What do you give it as input then? Do you create a json with categories or just dump in the whole CV and job vacancies

> **lovelace6329** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paj3kwx/)
> 
> We already have an internal matching engine. I think I'll start by using jev to rerank the top 20 candidates to improve the display ranking

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pajeu0w/)
> 
> Good 1. But I'd also be curious to know if you can replace the whole thing with multi step Jev

> **clivegermain** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pangmws/)
> 
> i have a similar jobsearch set up that only calls on LLMs if parsing fails. i'd be tempted to try jev first or get rid of my parsers entirely.

> **o\_sht\_hi** · [2026-09-19](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paq2ejx/)
> 
> How do you mean. Use Jev to parse? I'm not sure it can do that, though

> **clivegermain** · [2026-09-19](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paqf7ob/)
> 
> no, i mean it can assess fit on a scale – just do that instead of parsing.

> **o\_sht\_hi** · [2026-09-19](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paqfho3/)
> 
> Lol yeah that makes more sense

> **Nedomas** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pajblax/)
> 
> built Jev for code quality [https://github.com/supercorp-ai/supercov](https://github.com/supercorp-ai/supercov)

> **Ok\_Profit\_1171** · [2026-09-21](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pb3b0h1/)
> 
> Will Dart be supported?

> **Nedomas** · [2026-09-21](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pb3wihm/)
> 
> yeah, will add most other languages over the next week. will update here when I do

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pajf58i/)
> 
> Thanks for the link! It would be quite useful to observe how you're managing context for this model and building the plumbing in and out of it

> **Nedomas** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pajfx37/)
> 
> it took a while to figure out. But tldr:  
> LLM can take junk input and still produce alright result. Jev really needs good input to produce good result.
> 
> At first i just tried sending whole file/codebase and asking for "quality" or "maintainability". Well it was bad.
> 
> Then i realized Jev is good at answering mechanical questions. Like "duplicated\_code", "deep\_nesting" - these work on par with coderabbit scores, just 100x cheaper.
> 
> You can look into the source of supercov, its rust but its not super crazy. Can ask pi to explain. Took me like 8h with experimentation, haha

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pajgz4q/)
> 
> That's really interesting. I had been playing with a reviewer extension on the side for my project that takes the edit calls and live reviews things. This could be great for that. Thanks again for the code and the explanation 🙂 I'm excited to fuck around with this once I get access

> **D-3r1stljqso3** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paiybrn/)
> 
> I've seen some people proposing to implement selective compaction by classifying whether to keep each entry from the chat history.

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paj19rw/)
> 
> Yep that's the first thing I thought of too. But also in real time *before* the entry even becomes a part of chat history

> **D-3r1stljqso3** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paj5qmk/)
> 
> That's what the attention layers are supposed to do.

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paj8et7/)
> 
> Okay but you still wouldn't want to feed the model unnecessary tokens, right?

> **D-3r1stljqso3** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paj9ax4/)
> 
> I'd rather leave the chat history until the last minute. It's hard to predict which piece of info won't be needed at all later on.

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pajdxfl/)
> 
> Yeah I meant something similar to what headroom (that's the extension, right?) does. As I understand it, they use algorithms to prune the stuff that's sent to the LLM right before it's sent. And an if else statement that routes to the right algorithm. An AI like jev could replace that entire machinery. It could first decide what goes on and what's dropped. Once it decides what's included, it could then classify it and send it to a pruning function that drops all the bullshit tokens like json formatting, spaces, etc and formats the thing nicely before sending it to the LLM.
> 
> I think the advantage of having an AI do this would be better predictability on the relevance of what's being pruned, which goes to your point about predicting what may be required later on

> **Cultured\_Alien** · [2026-09-21](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pb3ue69/)
> 
> Modifying history realtime will destroy caching tho. I'd avoid headroom or anything that invalidates cache, just use a better compaction method like pi-vcc.

> **o\_sht\_hi** · [2026-09-21](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pb463f9/)
> 
> It won't if you modify the tokens before they become history. You're not changing anything that's going to the LLM. You only change it once before it is sent to the model. That's the whole point..

> **Cultured\_Alien** · [2026-09-21](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pb47udo/)
> 
> Using things headroom only take up more tool calls and context bloat. As for modifying tokens, RTK is good enough. Though I do think jev will be good on semantic search and compaction.

> **o\_sht\_hi** · [2026-09-21](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pb4arl6/)
> 
> Forget headroom. I am talking about pruning and reformating tool calls that the LLM has already given pi. How would that cause more tool calls or context bloat? The model knows nothing about this pruning system. It's all happening before any tokens even reach the model. And the pruning actively reduces the number of tokens.
> 
> Coming back to headroom, that's what it does too. So there's no question of more tool calls.
> 
> How do you think will it take up more tool calls and context bloat? Maybe I'm not able to imagine what you're trying to say

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paixcmk/)
> 
> I'm wondering if this can be used to prune tool calls in real time for pi. For eg, if the agent does 6-7 tool calls, we take the results, categorise them and send a nicely formatted response to the LLM API instead of the raw output. I could see this being super useful for local models that do a ton of repetitive or bullshit tool calls

> **0neMorning** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pakob7o/)
> 
> Here a similar but not the same idea - truncating tool calls for compaction [https://github.com/tamaratran/fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction)

> **Vancecookcobain** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pak07vy/)
> 
> Some guy built a near instantaneous voice agent that uses Jev and gave it like 40 tools and it made using a mouse and keyboard look fucking slow as hell...it was browsing the internet and using all kinds of tool calls to answer questions. I think that coupling it with an LLM is what is going to get us AGI....it can pick the right tools, hell it can even route your prompt to the proper model and it's all deterministic so it will almost never hallucinate

> **MarioBGE** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pak0vwr/)
> 
> Do you have a link for this?

> **Vancecookcobain** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pak8332/)
> 
> It's at around 6 minutes [https://youtu.be/Nq\_lu5QT-fI?is=2FTl0AcqkenGT0mO](https://youtu.be/Nq_lu5QT-fI?is=2FTl0AcqkenGT0mO)

> **JohnnyLovesData** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pak357k/)
> 
> I'm curious too

> **Vancecookcobain** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pak83rs/)
> 
> It's at around 6 minutes [https://youtu.be/Nq\_lu5QT-fI?is=2FTl0AcqkenGT0mO](https://youtu.be/Nq_lu5QT-fI?is=2FTl0AcqkenGT0mO)

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pakb8c7/)
> 
> Yes now we're talking. This is very exciting

> **Own-Addendum-9886** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paj1wkm/)
> 
> Yes, I use jev to determine what thinking level I should use.

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pajexox/)
> 
> Mid turn? Does that break cache?

> **Strong\_Essay1176** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pajqhut/)
> 
> I think he is talking about himself and not about llm.

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pajrutq/)
> 
> Lol I guess I should use it to detect sarcasm

> **Strong\_Essay1176** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pajvkyj/)
> 
> Perfect use case. 🤣

> **fingerthief** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pake7ll/)
> 
> Yep! I’m working on a nice command guard using it [https://tannermidd.github.io/specpi-jev-guard/](https://tannermidd.github.io/specpi-jev-guard/)
> 
> It’s pretty interesting! And the results are pretty amazing.

> **debackerl** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pal4cp0/)
> 
> I'm using laya, it's the same but free and open source
> 
> [https://huggingface.co/convaiinnovations/laya](https://huggingface.co/convaiinnovations/laya)

> **wildjokers** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pakg6zs/)
> 
> - [https://old.reddit.com/r/PiCodingAgent/comments/1wimfhg/piwarden\_a\_jevpowered\_second\_pair\_of\_eyes\_for\_pi/](https://old.reddit.com/r/PiCodingAgent/comments/1wimfhg/piwarden_a_jevpowered_second_pair_of_eyes_for_pi/)
> - [https://old.reddit.com/r/PiCodingAgent/comments/1whsav6/anyone\_else\_testing\_out\_typesafe\_ais\_new\_system/](https://old.reddit.com/r/PiCodingAgent/comments/1whsav6/anyone_else_testing_out_typesafe_ais_new_system/)

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/palhw42/)
> 
> Nice. Thanks for the links!

> **lu4p\_** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pal7m6a/)
> 
> Its pretty cool as you can do decisions over large amounts of data for very little cost.
> 
> I made a quick codebase scanner for myself that answers whether a repository is malicious
> 
> [https://github.com/luantak/is-malicious](https://github.com/luantak/is-malicious)

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/palibal/)
> 
> This is intriguing. Thanks for the link!

> **Fancy-Pants\_** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paj0swi/)
> 
> It’s pretty cool, I have lots of ideas but not implemented anything yet. The website and UI is a bit janky but seeing the three use cases, true / false, multiple choice, score is interesting.

> **MichettGodot** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paj9zsu/)
> 
> Yes, Jev helps me with testing my Godot game. It's wonderful at quickly analyzing game state so I can have it watch me play and look for things that might be off. Still in very early development but already pretty promising.

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pajeojm/)
> 
> Yeah I saw a lot of demos for it playing games. I think it could be really interesting for AI NPCs

> **Vancecookcobain** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pak0yx3/)
> 
> Yea...it might actually be easier to have Jev or a Jev like diffusion model be the NPC behavior than actually code NPC behavior...I can see games in the future that have a proprietary Jev like model to do that instead of wasting energy coding how they should act

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pakbnqz/)
> 
> Exactly. As long as you can build a good enough adapter to translate game state, we're in business. This would be so cool specially in RPGs

> **jiipod** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pajsxvj/)
> 
> My smooth brain thinks Jev could be really handy in TDD type flows (JevDD?) when prototyping.
> 
> You write Jev expectations for API route or whatever and let the agent make it pass.

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pajx11r/)
> 
> Ooh nice. That seems interesting. I hadn't thought of using it that way!

> **buff\_samurai** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/palbc1y/)
> 
> For those who are on the waiting list, jev is on openrouter now.

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/palhyms/)
> 
> Fuck yeah

> **ErvinSae** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paj7wum/)
> 
> Is it possible in the future that these agents themselves (codex, claude) will be built-in with JEV?

> **\-grabus-** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pak1fu0/)
> 
> They rather would train their own Jev alternatives.

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pajekro/)
> 
> That would be pretty fucking cool

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pajhdri/)
> 
> I'm getting the feeling that Jev could be a huge boost for agents to use headless stuff, MCPs and APIs just as a router that sits in front of the LLM. OR depending on how intellegent Jev is, it could maybe bypass the LLM entirely and just pick the APIs to call

> **Vancecookcobain** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pak1q06/)
> 
> Some one did it and it was insane....they also had it become a near instant voice agent that transcribed the users words into text and executed tool calls and everything with an LLM....it even was browsing the internet and everything while the person was telling what to do in real time....it made using a mouse and keyboard look slow....Im pretty sure this is the final piece we are going to have to get to AGI.
> 
> My whole thing was that agentic computer use has to get as effective as a human before we can achieve AGI....but with near instant tool calling and computer use there is nothing stopping AI from passing that threshold....they got it playing doom...it's insane

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pakc22m/)
> 
> That's very cool. At this point, I don't even care about AGI or some other term. The latency and accuracy of this model has me hyped af. I work a lot with SCADA/PLC automation for large scale utilities and this shit can take that system to the next level. Just waiting for the open source versions now

> **Challseus** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pakmxg0/)
> 
> Just finished survey 🤞

> **namelesstherebel** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paltl76/)
> 
> I’m already planning to use it in my own business, but I’m integrating it into an agentic backend testing algorithm for trading and then a sports betting environment for selling data back signals to gambling addicts.

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/palx9sh/)
> 
> So you're planning to use it to: 1. Backtest trading strategies 2. Generate data on sports betting
> 
> I'm curious to know more about both.. specially the sports betting

> **Aramedlig** · [2026-09-19](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paozown/)
> 
> Yes. Been using it with the SFT/RL/SCoRe research I’ve been doing. It is excellent at classifying taxonomy of model failures and for a fraction of the time and cost Fable can do it

> **Spiritual-Today-6432** · [2026-09-19](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/parii82/)
> 
> I used it for following
> 
> **Your inbox, judged in milliseconds — no LLM, no JSON parsing, no per-email bill**
> 
> Every "AI inbox" tool does the same thing: prompt a chat model, hope it returns valid JSON, pay full completion prices for a yes/no question.
> 
> I built jev-mail-classifier instead: connects over IMAP, define categories in plain English. Matches tag/move/flag/webhook automatically. Terminal UI, 3 steps, no code.
> 
> Open source, MIT: [https://github.com/parth-kp/jev-mail-classifier](https://github.com/parth-kp/jev-mail-classifier)

> **o\_sht\_hi** · [2026-09-19](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/parl1fr/)
> 
> Love that this is a tui

> **broisgammamale** · [2026-09-19](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/parz92r/)
> 
> Jev is basically "dynamic else if statment" lol

> **Odd\_Error\_6736** · [2026-09-19](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pas58k1/)
> 
> Can we please stop advertising this bs

> **o\_sht\_hi** · [2026-09-19](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pas7nva/)
> 
> Talking about it is advertising?

> **Odd\_Error\_6736** · [2026-09-20](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pavaej1/)
> 
> Is this your friend? [https://www.reddit.com/user/BoyInDaBox89/](https://www.reddit.com/user/BoyInDaBox89/)

> **o\_sht\_hi** · [2026-09-20](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pavcjer/)
> 
> Brother from another mother

> **Odd\_Error\_6736** · [2026-09-20](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pavcu0h/)
> 
> Tell your manager/boss at TypeSafe to stop spamming reddit with your paid shitass model, or it'll fire back

> **o\_sht\_hi** · [2026-09-20](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pavftzs/)
> 
> The model only outputs structured objects. It can't fire back. Most it can do is give out a confidence score of 0

> **Bizzniches** · [2026-09-20](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pavjujj/)
> 
> I’m using it to give tooling to smaller models and turning them into big bois

> **tom\_reddit** · [2026-09-21](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pb8hecd/)
> 
> [https://preview.redd.it/vp0jxauinxqh1.png?width=1572&format=png&auto=webp&s=f3e7ae9d718b7d42f406fc29c471214859d8c8d8](https://preview.redd.it/vp0jxauinxqh1.png?width=1572&format=png&auto=webp&s=f3e7ae9d718b7d42f406fc29c471214859d8c8d8)
> 
> I used Jev to make a free and open-source Chrome extension called 'Slop Mop' to help with our LinkedIn feeds... [https://slopmop.lol](https://slopmop.lol/)

> **Sarthak999gupta** · [2026-09-21](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pb8hxbd/)
> 
> I created [**shipwithjev.com**](http://shipwithjev.com/) with 607 use cases, but I missed a few.

> **o\_sht\_hi** · [2026-09-21](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pb8qs2m/)
> 
> This is very cool. Are you maintaining this?

> **o\_sht\_hi** · [2026-09-21](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pb8rkd2/)
> 
> The filter menu covers top of the page while scrolling down and it's really bugging me 😅 could you please hide it while scrolling down? Lol
> 
> [https://preview.redd.it/2238tgkfvxqh1.png?width=1080&format=png&auto=webp&s=f7a5d171499435e8b8fec13f2eaaef21222ad268](https://preview.redd.it/2238tgkfvxqh1.png?width=1080&format=png&auto=webp&s=f7a5d171499435e8b8fec13f2eaaef21222ad268)

> **Sarthak999gupta** · [2026-09-21](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pb8saqw/)
> 
> Getting it fixed right now.

> **o\_sht\_hi** · [2026-09-21](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pb8v6s6/)
> 
> Cheers!

> **RealDannyhvv** · [2026-09-22](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pbbsagb/)
> 
> I made an npm package that can use it for site moderation based on your site's rules. [https://www.npmjs.com/package/modsure](https://www.npmjs.com/package/modsure)

> · [2026-09-23](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pbnizja/)
> 
> \[deleted\]

> **o\_sht\_hi** · [2026-09-25](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pbyz2ks/)
> 
> Awesome

> **Drugba** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paiube6/)
> 
> I just got access yesterday, but haven’t had time to do much with it.
> 
> I applied the day before so it was only about 24 hours wait, but I did the survey thing that’s supposed to move you up the wait list

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paiwufa/)
> 
> Lol yeah I did the whole survey too! Applied last night but it's been less than 12 hours so fingers crossed!

> **whileyouredownthere** · [2026-09-19](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pauaw66/)
> 
> I’m experimenting with Jev in Propeller Picks, a sports betting research app. People can ask things like “What are the top five NFL props today?” or “Build me a three-leg parlay.”
> 
> We’re using Jev as a cheap first step to figure out what someone wants and pull the right data. Our own scoring engine does the actual rankings and parlay scoring. For straightforward questions, we can return an answer without calling a bigger model. More complicated questions get passed along to the regular AI assistant.
> 
> Early results are promising on cost, but we’re still testing the edge cases. So far, it seems most useful for those small decisions around a larger AI workflow.

> **No-Sympathy2403** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paiwb3v/)
> 
> I had acces yesterday. I just tried the samples bench, it looks quite speedy

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paiwzhn/)
> 
> Yeah the latency on this thing looks crazy.

> **lanternaddict** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pakdrxp/)
> 
> Would be good if you could provide more detail as to what jev is, or you know add some hyperlinks?

> **wildjokers** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pakgh1m/)
> 
> [https://www.google.com/search?q=jev](https://www.google.com/search?q=jev)

> **lanternaddict** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pakhr5r/)
> 
> The first result is a youtube, channel, the second result is the wikipedia article about a Congolese-Canadian rapper, and the third result is a spotify link.
> 
> You really don't understand the power of a hyper link do you?

> **wildjokers** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paknome/)
> 
> It is the 2nd link on the google results. Used to be the first but now it is the 2nd. The 1st is an article about it though (someone has good SEO to be able to push it down):
> 
> [https://typesafe.ai/blog/introducing-system-one-models-and-jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
> 
> It isn't rocket science. Jev has been posted about a couple of times in this very sub the last few days.
> 
> - [https://old.reddit.com/r/PiCodingAgent/comments/1whsav6/anyone\_else\_testing\_out\_typesafe\_ais\_new\_system/](https://old.reddit.com/r/PiCodingAgent/comments/1whsav6/anyone_else_testing_out_typesafe_ais_new_system/)
> - [https://old.reddit.com/r/PiCodingAgent/comments/1wimfhg/piwarden\_a\_jevpowered\_second\_pair\_of\_eyes\_for\_pi/](https://old.reddit.com/r/PiCodingAgent/comments/1wimfhg/piwarden_a_jevpowered_second_pair_of_eyes_for_pi/)

> **lanternaddict** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pakw6qh/)
> 
> Google results differ depending on the user, location, ip, time, anything really.

> **o\_sht\_hi** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/pal4jlc/)
> 
> Yo just look it up man, you really trying to offload a ChatGPT message to a random reddit comments section

> **Limp\_Classroom\_2645** · [2026-09-18](https://www.reddit.com/r/PiCodingAgent/comments/1wjibh5/anyone_here_using_jev/paixbhz/)
> 
> No.
