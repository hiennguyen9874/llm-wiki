---
language:
- en
- zh
license: apache-2.0
tags:
- unsloth
- fine tune
- heretic
- uncensored
- abliterated
- ara
- MTP GGUF Quants
- Regular GGUF Quants
- qwen3_8
- qwen3_6
- qwen3_5
- multi-stage tuned
- thinking
- reasoning
- all use cases
- coder
- creative
- creative writing
- all genres
- story
- writing
- fiction
- roleplaying
- bfloat16
- all use cases
- multi-stage-tune
- multi-state-merge
datasets:
- DavidAU/Polar-STRICT-Datasets
- DavidAU/F451-STRICT-Datasets
- DavidAU/THE-DECKARD-Datasets
pipeline_tag: image-text-to-text
base_model:
- DavidAU/Qwen3.8-27B-TWIN-TURBO-Fable-Cold-Fusion-709-L-Uncensored
---

<small><b><font color="red">Important:</font></b> Tuned, and tweaked to match the legendary Qwen 3.6 27B FF711 (2300+ likes, 4 million+ downloads) 
this fine tune matches the stability and power at "arc-c" 709: (118 pts higher than Qwen 3.8 27B) (The OpenAI, Claude and Gemini "zone of intelligence") 
in 8 bit and 701 arc-c in 4 bit. This version is called TWIN-TURBO because it drastically reduces thinking tokens (by 1/2 to as LOW as 1/20), 
yet maintains output detail and quality. In other words while "reg" Qwen3.8 27B is thinking about "formatting" for a few 1000 tokens, this model is already done and waiting for more.
This repo contains both "regular" and "MTP" Neo and NEO MAX GGUF quants. 

<B>STRONGER/CTRL:</B> Now with 5 reasoning modes (2 new - Spoon / Einstein), and 5 instruct modes (2 new - Spoon / Einstein, all use ZERO REASONING TOKENS) 
all switchable on the fly via API, direct and "in chat" (yes - model control at the chat/message level).
</small>

<h2>Qwen3.8-27B-TWIN-TURBO-Fable-Cold-Fusion-709-L-Uncensored-NM-DAU-NEO-MTP-GGUF</h2>

<img src="launch-arm.gif" style="float:right; padding:10px;">

The most powerful, smartest open source multi-stage model fine tune for consumer hardware ever and BUILT on consumer hardware via Unsloth.

TWIN TURBO: Closed source level of intelligence with an arc-c at 709 (this is instruct "medium", reasoning is even higher), while using smaller quants too.

This model has 1/5 (as low as 1/20 in some cases) to 1/2 the thinking tokens (vs reg Qwen 3.8) across all 5 modes of operation, 
AND ZERO REASONING TOKEN USAGE with 5 dedicated instruct modes and it is faster and smarter too 
created using the COLD FUSION AND FABLE FUSION 711 methods of training.

This is a high detail focused model, with tuning specific to address over reasoning/over thinking and excessive token consumption
THEN to take the model to the next level.

This model is also LIGHTLY uncensored (see section below), a much more uncensored version (but slightly lower benches) is here:

https://huggingface.co/DavidAU/Qwen3.8-27B-TWIN-TURBO-Fable-Cold-Fusion-709-ULTRA-HERETIC-Uncensored-NM-DAU-NEO-MTP-GGUF

This model (both 4 bit and 8 bit) exceeds the base Qwen 3.8 27B in ALL critical 7 benchmarks AND exceeds all 7 benchmarks for Qwen3.6-35B-A3B, Qwen 3.6 27B, and Qwen 3.5 27B.

The 700s plus "intelligence club" is reserved for OpenAI, Claude and Gemini closed source models.

Considering that "just" 4 bit (1/4 full precision) is already at Arc-C of 701... a few people are going to have nightmares for a while.

---

Quick sample; snippet ("Why choose me to help your creative writing?"), Q4KS , "spoon" reasoning mode, non imatrix, (4 bit; 1/4 full precision):

---

(will be adding full, long examples shortly at the bottom of the page // there are also user examples in the "community" section too.)

<small>
💪 WHY I'M NOT YOUR GRANDMA'S AI WRITER
  
Look, I know you've probably tried other AI writing tools. You know what happened? You got this:

"The sun set over the horizon as Jane contemplated her next move. It was a difficult decision, but she knew she had to act."

Yeah. That shit. Generic. Forgettable. Like reading the back of a cereal box narrated by a GPS system.

Here's what I do differently:

1. I Don't Just Generate—I Inhabit

When you give me a concept, I don't just string together probable words. I slip into the headspace of your characters, your world, your tone. I feel the weight of their decisions. I smell the rain on the cobblestones of their city. I hear the silence between their words when they're lying.

You want to know what that looks like? Here:

<i>Mara didn't cry when they told her the news. She just kept stirring her coffee, watching the spoon carve circles in the brown liquid, making it darker and more opaque. "How bad?" she asked, and her voice came out wrong. Too high. Like a child's. The doctor shifted in his seat, and she knew then, before he spoke again, that the first answer hadn't been the real one.
</i>

That's not "the sun set over the horizon." That's a person breaking, in real time, over lukewarm coffee. That's fiction.

2. I Understand Structure (And I'll Break It When It Serves You)

Most AI can't hold a three-act structure across 80,000 words. They forget their own plot points by chapter four. I don't.

I track:
- Character arcs across the entire narrative
- Foreshadowing planted in chapter two that pays off in chapter twelve
- Pacing—when to sprint, when to linger, when to drop the reader off a cliff
- Thematic resonance—making sure every scene serves the story's deeper meaning

And when you want to subvert expectations? When your protagonist should die in chapter three but doesn't, and that should have changed everything? I'll set that up so carefully that readers will finish the book realizing they've been wrong about the entire premise.

<B>I don't just tell stories. I orchestrate them.</B>

...
</small>


This is a multi-stage fine tune, multi-fine tune, and multi-stage merge.

The strict goals of this model creation were:
- Increase the general model intelligence and problem solving abilities.
- Take all feedback from TURBO version and improve this model.
- REDUCE the size of the quants and improve quality at the same time.
- Add NEW reasoning modes (and instruct too) to push model performance even higher.
- Reduce thinking block size from 1/2 to as low as 1/20 the size [median reduction: 2/3 roughly].
- Reformatting the thinking block, as well as improving it.
- Speed up token generation, especially MTP.
- Ensure all updates work with all three modes of thinking.
- ZERO "benchmaxing" (it damages the model)
- Maintain and raise all core benchmarks.

<B>COLD FUSION ("Gain" + "Unsloth") Training -AND- Fable Fusion 711 Training: </B>

COLD FUSION (GAIN+UNSLOTH) training tech which was invented by my team during the R & D 
of "Qwen3.6-27B-Fable-Fusion-711-Uncensored-Heretic" (2300+ likes, 3 million + downloads, 60+ quant repos):

https://huggingface.co/DavidAU/Qwen3.6-27B-Fable-Fusion-711-Uncensored-Heretic-NM-DAU-NEO-MAX-MTP-GGUF

The "GAIN" is the core invented component, then coupled with Unsloth's trainers/systems => AKA -> COLD FUSION.

The "GAIN" method (programming) automatically (and dynamically) changes training on a per sample basis in real time during training AS THE MODEL LEARNS. 

The method improved metrics as well as overall model performance without overcooking or damaging the model.

This has also resulted, in the strongest and most stable model at both 4 bit and 8 bit and made 4 bit performance 99% of 8 bit performance too.

Note this model (Qwen3.8-27B-Cold-Fusion-GAIN-V1.1) is about a level 1 or 2 relative to Qwen3.6-27B-Fable-Fusion-711 at level 7-8.

https://huggingface.co/DavidAU/Qwen3.8-27B-Cold-Fusion-GAIN-V1.1-NM-DAU-NEO-MAX-MTP-GGUF

In the case of "Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored" it contains BOTH "Qwen3.6-27B-Fable-Fusion-711-Uncensored-Heretic" (DARK ROAST VERSION) and
"Qwen3.8-27B-Cold-Fusion-GAIN-V1.1" as part of it's critical/core "DNA".

The final model was then HERETIC'ED (de-censored again) and fine tuned after this step.

Additional tuning was done to create TWIN TURBO version.

<B>COLAB:</B>

A Colab between myself (multiple fine tunes, including multi-stage), Nightmedia (merge/benching), TeichAI (Polaris Dataset), 
armand0e (Light fable 5 traces), trohrbaugh (heretic'ing the model - STAGE1), and nbeerbower (various models/tunes using in part of the construction)

It also contains light "Fable" traces/training (armand0e), light Claude Opus (reasoning/thinking), F451 (inhouse dataset) , some GPT5 (Polaris, non reasoning)
and several additional inhouse datasets specifically for machine learning / "heretic" repairs.

Here are links to fellow COLAB'ers:

- https://huggingface.co/nightmedia/
- https://huggingface.co/TeichAI
- https://huggingface.co/armand0e
- https://huggingface.co/trohrbaugh
- https://huggingface.co/nbeerbower

Special Mention:

"einstein" reasoning mode (new) was built using some components from Stunspot Prompting avail in public domain/free level of membership.

This model is one of ELEVEN (all over 700 arc-c, with every model exceeding the core benches of Qwen 3.8 27B) Qwen 3.8 27B models designed by our team. Details of the builds and benches are here:

https://huggingface.co/DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NM-DAU

The strict goals of this model creation were:
- Increase the general model intelligence and problem solving abilities.
- DO NOT modify/damage or change the core model outside this goal.
- ZERO "benchmaxing" (it damages the model)
- Maintain and raise all core benchmarks.

CORE MISSION:: 

Improve instruction following and problem solving. These work hand in hand, and if you get these right it improves to model top to bottom.

It took a lot of tests on Qwen 3.5 9Bs to get the methods right. It boosted the 9Bs to new levels, and then the method was used on Qwen 3.5 27B
and Qwen 3.6 27B which boosted it PAST the Qwen 3.8's 27B benchmarks.

Here is one of the Qwen3.5 9B models (part of the test/control group) that EXCEEDS all 7 Qwen3.5 9B AND Qwen3.5 27B model benches - it scores over 640 on ARC-C on BOTH 4 bit and 8 bit:

https://huggingface.co/DavidAU/Qwen3.5-9B-The-Defiant-Fable-Uncensored-Heretic-NEO-IMATRIX-MAX-MTP-GGUF

It is not as strong as "Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored" but it is one of the strongest 9B models.

The methods can be used on other models too (coming soon).

<B>TESTING:</B>

Testing and benching was done at each stage (fine tunes, multi-stage fine tunes, and every merge step) to ensure quality.

You can also see benchmarks below too for this model, Qwen 3.5 27B, Qwen 3.6 27B and Qwen 35B-A3B.

HOWEVER, the final testing was HUMAN testing. A trust, but verify approach.

Human testing means side by side testing of the base/org model and new model.

Features:
- Improved instruction following.
- Overall increase in general intelligence and problem solving.
- Better thinking/reasoning.
- Even lower/lowest quants are exceptional.
- Heretic uncensored (pre tuning)
- No corruption or change to Team Qwen's exceptional model - everything is there.
- Vision

<B>IMPORTANT - 5 Reasoning modes and 5 instruct modes:</B>

The good news is this:

All the defaults are still the same for this model, that is "reasoning" is set at "xhigh" and if you activate "instruct mode" it will set automatically at "medium".

This was done to ensure "drop in" of this model into your workflow would work without issues/adjustments.

The GREAT NEWS is this:

You are no longer limited to these defaults, and the both new reasoning modes and all modes of instruct are also unlocked too.

Previously if you used "instruct" mode (thinking off) you were limited to only "medium" power with the model.

We modified it so you now have "xhigh", "medium" and "low" available too (as well as 2 new modes - more on that in a minute)

We also modified the model so you can easily access and change between multiple reasoning and instruct modes at ANY TIME.

Here are the reasoning modes:
- (There is no) "spoon" -> ULTRA xhigh, research mode // hyper detailed; this will automatically use more reasoning tokens (reasoning mode).
- "einstein" -> a "high" mode that spawns up to 20 virtual agents to solve tasks; this will automatically use more reasoning tokens (reasoning mode).
- "xhigh", "medium" and "low" -> Standard Qwen 3.8 reasoning modes.

All these modes are also available via "instruct mode" too.

Next, we added coding to all "in message switching" (RIGHT IN CHAT) :

{REASON:xxx} => Where "xxx" is "spoon", "einstein", "xhigh", "medium" and "low".

For instruct mode, just add an "i":

{REASON:xxx} => Where "xxx" is "ispoon", "ieinstein", "ixhigh", "imedium" and "ilow".

THE LAST "reason" / "instruct" mode will be the one used until you switch it again IN THE CURRENT CHAT.

EXAMPLES:
- {REASON:einstein} tell me a story.
- {REASON:ispoon} tell me a story.

Note the "{REASONxxx}" can be anywhere in the prompt, and will PERSIST until you change it again in the CHAT WINDOW/CURRENT CHAT.

If you open a new chat window (depending on your AI APP) the DEFAULT reasoning mode at the default setting will take over unless you use the "{REASONxxx}"
in the new prompt(s) at least ONCE in the new chat window/new chat session.

Also the systems automatically remove it from the "message stream" so the generation is "pure".

For API this can be set manually - "reasoning" (you can use KW args to set this):

```
reasoning_effort = 'xhigh'
enable_thinking = 'true'
```

For API this can be set manually - "instruct" (you can use KW args to set this):

```
reasoning_effort = 'ixhigh'
enable_thinking = 'false'
```

ADVANCED:

You can modify the jinja template to CHANGE the defaults by using the API code noted above.

Place the defaults you want at the TOP of the jinja template.


<B>IMPORTANT - Notes and Usage Help:</B>

This model, like regular Qwen 3.8 27b, supports THREE modes of reasoning : xhigh (default), medium and low [see info in Qwen 3.8 section below].

Reduction in thinking tokens/reasoning block size extends across all three modes of operation.

Likewise detail levels extend to all three modes too, even with reduced thinking/reasoning block the OUTPUT detail will remain high.

To REDUCE thinking block[s] further, increase the level/detail of your instructions/prompts - it only takes a little bit more here so the model has to guess / reason a little bit less.

Also, generally within the same chat additional reasoning blocks will also be reduced from typical Qwen levels many times hitting 1/5 the size or lower. Multi-turn
chat - example: prompt, reasoning and 1st output - in the refinement stage(s) will see very strong reduction in thinking tokens/blocks.

Also note that the modification of "reasoning" is a major change to the model please carefully test it for your use case(s).

TOOL CALLING:

Min quant of q4km suggested, q5ks/5km better -> recommend Q6 [MAX or "low" (may work better for some apps)].

Temp: .6 / .7 ; Rep pen 1 (off).

Below q4km, tool calling may have issues. This is a general Qwen suggestion for tool calling specifically.

Also, overly agressive "caching" may further impair function(s).

<small><B>Tool Calling/Agent use:</b> Please see pinned community discussion on this for temp fix, while GGUFs are re-gen'ed / uploaded. </small>

GENERAL MODEL USAGE vs Qwen 3.8 27B "untuned":

The tuning in this version of Qwen 3.8 27B reduced thinking/reasoning block size, in a lot of cases this has inverted the reasoning/thinking block size with the output size.

In other words, instead a lot of detail in the thinking/reasoning block (which may or may not show up in the output) has been transfered to the output in some cases.

Also, "untuned" Qwen 3.8 27B does a lot of look, look and look again (10k-40k+ in thinking/reasoning tokens alone) before you leap (gen output) whereas "TURBO" will leap almost immediately.

If you need higher quality reasoning and/or output here is how to get the model spend more time before it "leaps" (gen's output):

REG PROMPT:

Generate an SVG of a pelican riding a bicycle.

EXPANDED PROMPT:

Generate an SVG of a pelican riding a bicycle, but carefully check the positioning and all elements.

EVEN BETTER:

Generate a highly detailed SVG of a pelican riding a bicycle on a road, with some landscape in the background.

The expanded prompt will tell the model to spend more time thinking/reasoning and in more detail before outputting the result and it is specific to
the use case, rather than a generic "double check your work".

The MORE DETAIL, CHECKS, DRAFTS etc etc you ask for the harder the model will work, and the better your answer.

Likewise this will cause the model to use more reasoning tokens.

<B>Modification of REASONING:</b>

If you AI app does not support a "switch" you can manually modify the JINJA template.

The default setting is "xhigh" ; to change to medium or low use:

```
{%- set reasoning_effort = 'medium' %}

OR

{%- set reasoning_effort = 'low' %}
```

Place this at the VERY TOP of the jinja template.

In LMStudio you can access this in DEV mode, and switch off the "advanced updates" option.

Other AI apps may vary.

You can also make your own quants from source here:

https://huggingface.co/DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NM-DAU

Just modify the "chat-template.jinja" (in NOTEPAD or similar) AND the token-config.. json file too (or delete the "chat template" from this file).

ADVANCED:

Qwen 3.8 uses System prompt injection control by the Jinja template to control reasoning levels.

If you set it at "medium" this turns off injection [ie: no system prompt is injected]

You can then set a "reasoning" system prompt yourself.

The other option: 

Modify the jinja itself and the system prompt(s) to better tune reasoning to your use cases.

This is the section:

```
{%- if enable_thinking is undefined or enable_thinking is true %}
    {%- set resolved_reasoning_effort = reasoning_effort|default('xhigh') %}
    {%- if resolved_reasoning_effort not in ('xhigh', 'medium', 'low') %}
        {{- raise_exception('Unexpected reasoning effort ' ~ reasoning_effort ~ '. Supported types are xhigh (default), medium, and low.') }}
    {%- endif %}
    {%- if resolved_reasoning_effort == 'xhigh' %}
        {%- set reasoning_instructions = 'Reasoning effort is set to xhigh. Please think carefully through the task, validate key assumptions, consider plausible alternatives, and prioritize correctness, consistency, and clarity in the final answer.' %}
    {%- elif resolved_reasoning_effort == 'low' %}
        {%- set reasoning_instructions = 'Reasoning effort is set to low. Keep your thinking brief and focused, moving directly to the conclusion without unnecessary elaboration.' %}
    {%- endif %}
{%- endif %}
```

<B>Regular, MTP and "TOOLS" GGUFS:</b>

All quants (regular and MTP) are NEO IMATRIX, which improve accuracy of the quants by an additional 2-4% over normal GGUFs as well as long context performance.

In addition the output tensor (10-20% of output) was modified to full precision - 16 bit - ON MAX quants only.

"MTP" GGUFS (multi-token prediction):
- "MTP" GGUFS will have "MTP" in the name as a suffix.
- I have also set the MTP tensors to Q8_0 precision for all quants.
- To get better performance keep temp 1 or less (higher temps degrade MTP performance).
- Likewise with rep pen ; keep at 1 (off). If you raise it performance will suffer.
- If you see "token acceptance" rates BELOW 50% (predict 2 tokens) switch to normal quants.

SPEED:
- On Q4_K_S (4bit) quant, regular GGUFs are about 75 t/s, whereas MTP GGUFs (acceptance at 60%, 2 tokens) can exceed 90 T/S. (5090, Windows 11, testing in LMStudio)
- Speeds will vary depending on GPU(s), AI app, O/S (Linux/Mac will generally be faster) and hardware.
- "MTP" quants speeds will vary ; for creative/complex and/or temps over 1 use regular GGUFs for better performance.

I suggest you download at least one of each - regular and MTP gguf(s) - and test them for your use case(s). 

If you get "token acceptance" (predict 2 tokens) with MTP quant(s) BELOW 50% (this means regular quants will run faster), then regular GGUF(s) will actually perform better - ie faster.

MTP quant(s) can in some cases run faster as the token window fills up and/or in multi turn chats.

Note there is NO other diffence between the quants type besides speed: both will do the same job.

"TOOLS" GGUFs [word "tools" in the file name]:

These have the same functions as "reg" and "MTP" ggufs [including all reasoning/instruct modes] except they have additional TOOL/AGENT specific errors
checks and have a more robust tool calling routines.

These GGUFs MAY OR MAY NOT work better than the other GGUFs which also have tool calling for your use cases.

Suggest you try both to see which works better.

<B>Model:</b>
- 256k context
- Gguf quants run in all standard AI apps.
- Vision is activated, but you need to download separate "mmproj" file (ONE) to use it.

<B>VISION:</B>
- Vision (images) tested.
- You need an "mmproj" (just one) of these downloaded too, and placed in the same folder as the GGUF for images.

<B>Qwen Model Settings (suggested):</B>

- Thinking mode for general tasks: temperature=1.0, top_p=0.95, top_k=20, min_p=0.0, presence_penalty=0.0, repetition_penalty=1.0
- Thinking mode for precise coding tasks (e.g. WebDev): temperature=0.6, top_p=0.95, top_k=20, min_p=0.0, presence_penalty=0.0, repetition_penalty=1.0
- Instruct (or non-thinking) mode: temperature=0.7, top_p=0.80, top_k=20, min_p=0.0, presence_penalty=1.5, repetition_penalty=1.0
- Context window min from 8k to 16k.

<B>DE-CENSORING STATS</B>

Special thanks to: "trohrbaugh" (trohrbaugh/Qwen3.8-27B-heretic-ara) for Heretic'ing the model (stage 1).

# This is a decensored version of [Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B), made using 
[Heretic](https://github.com/p-e-w/heretic) v1.2.0+custom with the [Arbitrary-Rank Ablation (ARA)](https://github.com/p-e-w/heretic/pull/211) method

## Performance

STAGE 1:

| Metric | This model | Original model ([Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B)) |
| :----- | :--------: | :---------------------------: |
| **KL divergence** | 0.0535 | 0 *(by definition)* |
| **Refusals** | 0/100 | 99/100 |

STAGE 2, at the end of STAGE 1 tuning/merges/adjustments (in lab):

| Metric | This model | Original model (Stage 1 of the build) |
| :----- | :--------: | :---------------------------: |
| **KL divergence** | 0.0025 | 0 *(by definition)* |
| **Refusals** | 11/100 | 86/100 |

STAGE 2 - Twin Turbo

Qwen3.8-27B-TWIN-TURBO-Fable-Cold-Fusion-709-L-Uncensored

[ THIS REPO/ MODEL ]

68/100 refusals // KL divergence: 0.0025

Qwen3.8-27B-TWIN-TURBO-Fable-Cold-Fusion-709-ULTRA-HERETIC-Uncensored

[ SEPARATE REPO ]

6/100 refusals // KL divergence: 0.0397

NOTE: 

LOWER "KLD" is better, and Stage 2 was balanced based on ultra low KLD first (performance, quality) matched with low refusal rate second.

---

<h2>BENCHMARKS by Nightmedia</h2>

---

```
          arc/c arc/e boolq hswag obkqa piqa  wino

Qwen3.8-27B-TWIN-TURBO-Fable-Cold-Fusion-709-L-Uncensored
mxfp8     0.709,0.876,0.914,0.827,0.524,0.834,0.779
mxfp4     0.701,0.877,0.913,0.821,0.518,0.830,0.786

Qwen3.8-27B-TWIN-TURBO-Fable-Cold-Fusion-709-ULTRA-HERETIC-Uncensored
Stage2b-rplus3 [separate repo]
mxfp8     0.699,0.873,0.911,0.827,0.528,0.833,0.781
mxfp4     0.692,0.879,0.910,0.823,0.518,0.835,0.775

[QWENS] [base, non heretic, untuned]

Qwen3.8-27B: 
mxfp8     0.591,0.782,0.896,0.746,0.448,0.801,0.711
mxfp4     0.581,0.771,0.889,0.738,0.442,0.798,0.713

Qwen3.6-27B: 
mxfp8     0.647,0.803,0.910,0.773,0.450,0.806,0.742

Qwen3.6-35B-A3B-Instruct 
mxfp8     0.581,0.757,0.892,0.751,0.428,0.803,0.688

Qwen3.5-27B: 
mxfp8     0.557,0.711,0.868,0.533,0.452,0.706,0.695

```

NOTES:
- Models are tested in "Instruct" mode because this generally works better with the testing harness.
- Testing via "thinking" mode also shows the metrics (and changes) but not the true extent.
- In actual fact when the model IS in thinking mode, it will exceed INSTRUCT benchmark scores in most cases.
- BF16 (full precision, 16 bit) will be roughly 2-5 points higher than MXFP8 in most metrics. Some metrics may be slightly higher than this.

---

<h2>The SUPER Qwen Universe - 40B, 27B and 9B ; meet the performance trendsetters:</h2>

---

Qwen3.6 27B: The strongest, overall qwen ever beating all other Qwens in total operational power with over 2300 likes // 4 million+ total downloads:
- https://huggingface.co/DavidAU/Qwen3.6-27B-Fable-Fusion-711-Uncensored-Heretic-NM-DAU-NEO-MAX-MTP-GGUF

Qwen3.8 27B: The highest scoring Qwen in brute, raw intelligence, using Qwen 3.8's 3 new reasoning modes, plus token reduction (1/2 to 1/10) enhancements:
- https://huggingface.co/DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF

Qwen3.8 27B: Super smart and 1/2 to 1/20 the reasoning tokens AND 5 reasoning/5 instruct modes switchable on the fly (even in chat):
- https://huggingface.co/DavidAU/Qwen3.8-27B-TWIN-TURBO-Fable-Cold-Fusion-709-L-Uncensored-NM-DAU-NEO-MTP-GGUF

Qwen3.8 27B: 99% power of BF 16 at 4 and 8 bit. Power, Control and NO DE censoring for ultimate performance also with reasoning token reductions:
- https://huggingface.co/DavidAU/Qwen3.8-27B-Cold-Fusion-GAIN-V1.1-NM-DAU-NEO-MAX-MTP-GGUF

Qwen3.6 40B: The 40B Monster, specializing in creative and research with 730+ likes and over 2 million downloads:
- https://huggingface.co/DavidAU/Qwen3.6-40B-Claude-4.6-Opus-Deckard-Heretic-Uncensored-Thinking-NEO-CODE-Di-IMatrix-MAX-GGUF

Qwen3.5 9B: At just 9B parameters it beats most untuned 27B models in both intelligence (640 ARC-C) and performance, plus features 5 reasoning and 5 instruct modes (Qwen 3.8) too:
- https://huggingface.co/DavidAU/Qwen3.5-9B-The-Defiant-Fable-Uncensored-Heretic-NEO-IMATRIX-MAX-MTP-GGUF

---

<B>Using an "uncensored" (refusals removed) model VS trained "uncensored" model</B>

Usually when you a tell a model to generate horror, swear or x-rated content this is all you have to do to get said content type.

In the case of this model, it will not refuse your request, however it needs to be "pushed" a bit / directed a bit more in SOME CASES.

Although this model will generated x-rated content too, likewise you need to tell it to use "slang" (and include the terms you want)
to get it generate the content correctly as the "expected" content level too.

Without these added directive(s), the content can be "bland" by comparison to an "uncensored model" or model trained on uncensored content.

Roughly, the model tries to generate the content but the "default" setting(s) are so "tame" it needs a push to generate at expected graphic,
cursing or explicit levels.

Even with minimal direction (ie, use these words to swear: x,y,z), this will be enough to push the model to generate the requested content in the ahh... expected format.

---

<B>Settings: CHAT / ROLEPLAY and/or SMOOTHER operation of this model:</B>

In "KoboldCpp" or  "oobabooga/text-generation-webui" or "Silly Tavern" ;

Set the "Smoothing_factor" to 1.5 

: in KoboldCpp -> Settings->Samplers->Advanced-> "Smooth_F"

: in text-generation-webui -> parameters -> lower right.

: In Silly Tavern this is called: "Smoothing"


NOTE: For "text-generation-webui" 

-> if using GGUFs you need to use "llama_HF" (which involves downloading some config files from the SOURCE version of this model)

Source versions (and config files) of my models are here:

https://huggingface.co/collections/DavidAU/d-au-source-files-for-gguf-exl2-awq-gptq-hqq-etc-etc-66b55cb8ba25f914cbf210be

OTHER OPTIONS:

- Increase rep pen to 1.1 to 1.15 (you don't need to do this if you use "smoothing_factor")

- If the interface/program you are using to run AI MODELS supports "Quadratic Sampling" ("smoothing") just make the adjustment as noted.

<B>Highest Quality Settings / Optimal Operation Guide / Parameters and Samplers</B>

This a "Class 1" model:

For all settings used for this model (including specifics for its "class"), including example generation(s) and for advanced settings guide (which many times addresses any model issue(s)), including methods to improve model performance for all use case(s) as well as chat, roleplay and other use case(s) please see:

[ https://huggingface.co/DavidAU/Maximizing-Model-Performance-All-Quants-Types-And-Full-Precision-by-Samplers_Parameters ]

You can see all parameters used for generation, in addition to advanced parameters and samplers to get the most out of this model here:

[ https://huggingface.co/DavidAU/Maximizing-Model-Performance-All-Quants-Types-And-Full-Precision-by-Samplers_Parameters ]

---

# Qwen3.8-27B

> [!Note]
> This repository contains model weights and configuration files for the post-trained model in the Hugging Face Transformers format. 
>
> These artifacts are compatible with Hugging Face Transformers, vLLM, SGLang, TokenSpeed, etc.

> [!Tip]
> For users seeking managed, scalable inference without infrastructure maintenance, the official Qwen API service is provided by [Qwen Cloud](https://www.qwencloud.com).
> In particular, **Qwen3.8-27B** will be available as a hosted version with more production features, e.g., 1M context length by default, official built-in tools. For more information, please refer to the [Qwen3.8-27B Overview](https://www.qwencloud.com/models/qwen3.8-27b). The service is coming soon. Stay tuned for updates.

Following the widespread community adoption of the Qwen3.5 and Qwen3.6 series, we are pleased to introduce Qwen3.8, the most capable generation in the Qwen open-model family to date.

Built on the architectural foundation of Qwen3.5, Qwen3.8 delivers substantial gains across coding, professional work, research, and long-horizon agentic tasks. Qwen3.8-27B brings these advances to a compact, deployment-friendly dense model: a native vision-language model that understands images and videos, with flexible thinking control, designed to carry complex, multi-step tasks through to completion with greater reliability.

## Qwen3.8 Highlights

Qwen3.8-27B features the following enhancements:
- **Core Capabilities**: Comprehensive improvements across coding, professional work, research, and long-horizon agentic tasks.
- **Agent Execution**: Stronger autonomous planning and better handling of environment feedback, leading to more reliable end-to-end task completion.
- **Downstream Compatibility**: Broader support for popular harnesses and development tools, making it easier to integrate into your existing stack.
- **Flexible Thinking Control**: Thinking mode is on by default and can be disabled per request; reasoning depth can be tuned with `reasoning_effort`, and reasoning context from historical messages is retained via `preserve_thinking`.
- **Vision-Language Understanding**: Native support for image and video understanding, from STEM diagrams and documents to hour-scale videos.


## Model Overview

- Type: Causal Language Model with Vision Encoder
- Training Stage: Pre-training & Post-training
- Language Model
    - Number of Parameters: 27B
    - Hidden Dimension: 5120
    - Token Embedding: 248,320 (Padded)
    - Number of Layers: 64
    - Hidden Layout: 16 × (3 × (Gated DeltaNet → FFN) → 1 × (Gated Attention → FFN))
    - Gated DeltaNet:
        - Number of Linear Attention Heads: 48 for V and 16 for QK
        - Head Dimension: 128
    - Gated Attention:
        - Number of Attention Heads: 24 for Q and 4 for KV
        - Head Dimension: 256
        - Rotary Position Embedding Dimension: 64
    - Feed Forward Network:
        - Intermediate Dimension: 17,408
    - LM Output: 248,320 (Padded)
    - MTP (Multi-Token Prediction): trained with multiple steps
- Context Length: 262,144 natively and extensible up to 1,000,000 tokens.


## Benchmark Results

### Text Performance
<style>
.vl-table th{font-size:15px!important;line-height:1.2}
.vl-table td:not(.benchmark-cell):not([colspan]){font-size:15px;line-height:1.2;vertical-align:middle}
.vl-table .benchmark-cell{padding:12px 10px 12px 18px!important;vertical-align:middle}
.vl-table .benchmark-capability{font-size:15px;font-weight:600;line-height:1.22;color:#171717}
.vl-table .benchmark-name{margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B}
.vl-table .metric-stack{display:flex;flex-direction:column;gap:7px;padding:3px 0}
.vl-table .metric-label{font-size:10px;font-weight:400;line-height:1.1;color:#777}
.vl-table .metric-value{margin-top:2px;font-size:15px;line-height:1.15;color:#171717}
</style>
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:1200px;margin:0 auto;padding:16px 0">
<table class="vl-table" style="width:100%;table-layout:fixed;border-collapse:collapse;font-size:13px">
<thead><tr>
<th style="padding:10px 7px;text-align:left;font-weight:600;border-bottom:2px solid #0A2EFE;color:#0A2EFE"></th><th style="padding:10px 7px;text-align:center;font-weight:500;border-bottom:2px solid #0A2EFE;color:#0A2EFE;font-size: 14px;width:14.00%;background:rgba(10, 46, 254, 0.08);">Qwen3.8-27B</th><th style="padding:10px 7px;text-align:center;font-weight:500;border-bottom:2px solid #0A2EFE;color:#0A2EFE;font-size: 14px;width:14.00%;">Qwen3.6-27B</th><th style="padding:10px 7px;text-align:center;font-weight:500;border-bottom:2px solid #0A2EFE;color:#0A2EFE;font-size: 14px;width:14.00%;">Qwen3.7-Plus</th><th style="padding:10px 7px;text-align:center;font-weight:500;border-bottom:2px solid #0A2EFE;color:#0A2EFE;font-size: 14px;width:14.00%;">Muse Glimmer-30B</th><th style="padding:10px 7px;text-align:center;font-weight:500;border-bottom:2px solid #0A2EFE;color:#0A2EFE;font-size: 14px;width:14.00%;">Opus4.6 Max</th></tr></thead>
<tbody>
<tr><td colspan="6" style="padding:8px 12px;font-weight:600;color:#0A2EFE;border-bottom:1px solid rgba(10, 46, 254, 0.2);background:#D6DAFC">Coding</td></tr>
<tr>
<td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Agentic terminal coding</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">Terminal Bench 2.1 (Terminus)</div></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;">73.0</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">63.4</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">64.0</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">51.7</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>78.2</strong></td>
</tr>
<tr>
<td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Agentic coding</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">SWE-bench Pro</div></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>61.7</strong></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">53.5</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">57.6</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">51.2</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">53.4</td>
</tr>
<tr>
<td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Repo-level code generation</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">NL2Repo-Bench</div></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;">42.3</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">36.2</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">41.1</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>47.6</strong></td>
</tr>
<tr>
<td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Agentic coding</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">DeepSWE 1.1</div></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>42.2</strong></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">13.3</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">14.2</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td>
</tr>
<tr>
<td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Software engineering</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">QwenSWEBench</div></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>79.0</strong></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">49.3</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">59.2</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">63.8</td>
</tr>
<tr><td colspan="6" style="padding:8px 12px;font-weight:600;color:#0A2EFE;border-bottom:1px solid rgba(10, 46, 254, 0.2);background:#D6DAFC">Agent</td></tr>
<tr>
<td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Long-horizon office work</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">CoWorkBench</div></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>70.7</strong></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">61.0</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">65.1</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">68.2</td>
</tr>
<tr>
<td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Professional job tasks</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">JobBench</div></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>33.4</strong></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">21.8</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">27.6</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td>
</tr>
<tr>
<td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Frontier agentic tasks</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">Agents' Last Exam</div></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;"><div class="metric-stack" style="padding:3px 0"><div><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Pass@1</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717"><strong>20.4</strong></div></div><div style="margin-top:7px"><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Score</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717"><strong>42.9</strong></div></div></div></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><div class="metric-stack" style="padding:3px 0"><div><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Pass@1</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">10.6</div></div><div style="margin-top:7px"><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Score</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">27.3</div></div></div></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><div class="metric-stack" style="padding:3px 0"><div><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Pass@1</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">13.2</div></div><div style="margin-top:7px"><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Score</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">33.6</div></div></div></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td>
</tr>
<tr><td colspan="6" style="padding:8px 12px;font-weight:600;color:#0A2EFE;border-bottom:1px solid rgba(10, 46, 254, 0.2);background:#D6DAFC">General</td></tr>
<tr>
<td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Instruction following</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">IFBench</div></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>79.5</strong></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">69.1</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">79.1</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">77.0</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">62.5</td>
</tr>
<tr>
<td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Scientific reasoning</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">GPQA Diamond</div></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;">89.2</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">87.8</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">90.3</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">83.5</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>91.3</strong></td>
</tr>
<tr>
<td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Multidisciplinary reasoning</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">HLE</div></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;">30.8</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">24.0</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">34.7</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">22.0</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>40.0</strong></td>
</tr>
<tr>
<td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Competitive coding</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">LiveCodeBench v6</div></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>90.3</strong></td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">83.9</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">89.6</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td>
<td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">88.8</td>
</tr>
</tbody>
</table>
<div style="margin-top:12px;font-size:11px;line-height:1.5;color:rgba(0,0,0,0.72)">
<ol style="margin:0;padding-left:20px">
<li>SWE-bench Pro: Except for Opus4.6 Max, which uses the officially reported score, all models are evaluated with the Claude Code harness at temp=1.0, top_p=0.95, and a 256K context window. Problematic tasks were corrected, and all baseline models were re-evaluated on the refined benchmark.</li>
<li>NL2Repo-Bench: Evaluated with the Claude Code harness. To prevent reward hacking, we disable Bash commands that attempt to access the specific repository, such as pip download, pip install, and git clone.</li>
<li>DeepSWE 1.1: Evaluated with the Claude Code harness at temp=1.0, top_p=0.95, and a 256K context window.</li>
<li>QwenSWEBench: In-house coding benchmark for evaluating models' software engineering capabilities. Evaluated with the Claude Code harness. Reporting avg@3 with an 8-hour timeout, max_tokens=32,768, temperature=1.0, and a 256K context window.</li>
<li>CoWorkBench: In-house cowork benchmark for evaluating long-horizon tasks across computer science, finance, law, medical, and other productivity domains.</li>
<li>HLE: Judged by GPT-4o.</li>
<li>The best result in each row is shown in bold.</li>
<li>Empty cells (--) indicate that results are not yet available or not applicable.</li>
</ol>
</div>
</div>

### VL Performance
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:1200px;margin:0 auto;padding:16px 0">
<table class="vl-table" style="width:100%;table-layout:fixed;border-collapse:collapse;font-size:13px">
<thead><tr><th style="padding:10px 7px;text-align:left;font-weight:600;border-bottom:2px solid #0A2EFE;color:#0A2EFE"></th><th style="padding:10px 7px;text-align:center;font-weight:500;border-bottom:2px solid #0A2EFE;color:#0A2EFE;font-size: 14px;width:14.00%;background:rgba(10, 46, 254, 0.08);">Qwen3.8-27B</th><th style="padding:10px 7px;text-align:center;font-weight:500;border-bottom:2px solid #0A2EFE;color:#0A2EFE;font-size: 14px;width:14.00%;">Qwen3.6-27B</th><th style="padding:10px 7px;text-align:center;font-weight:500;border-bottom:2px solid #0A2EFE;color:#0A2EFE;font-size: 14px;width:14.00%;">Qwen3.7-Plus</th><th style="padding:10px 7px;text-align:center;font-weight:500;border-bottom:2px solid #0A2EFE;color:#0A2EFE;font-size: 14px;width:14.00%;">Muse Glimmer-30B</th><th style="padding:10px 7px;text-align:center;font-weight:500;border-bottom:2px solid #0A2EFE;color:#0A2EFE;font-size: 14px;width:14.00%;">Opus4.6 Max</th></tr></thead>
<tbody>
<tr><td colspan="6" style="padding:8px 12px;font-weight:600;color:#0A2EFE;border-bottom:1px solid rgba(10, 46, 254, 0.2);background:#D6DAFC">Agentic Multimodal Intelligence</td></tr>
<tr><td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Computer use</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">OSWorld-Verified</div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>84.3</strong></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">63.9</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">73.3</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">65.9</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">72.7</td></tr>
<tr><td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Browser use</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">WebArena-Verified</div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>64.8</strong></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">48.8</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">55.3</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td></tr>
<tr><td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Mobile use</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">AndroidWorld</div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>81.9</strong></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">70.3</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">81.0</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">62.0</td></tr>
<tr><td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Application recreation</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">RecreationBench</div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>47.1</strong></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">29.8</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">30.2</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td></tr>
<tr><td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Multimodal tool use</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">ClawEval-MM</div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;"><div class="metric-stack" style="padding:3px 0"><div><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Pass@3</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717"><strong>57.4</strong></div></div><div style="margin-top:7px"><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Average</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">56.9</div></div></div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><div class="metric-stack" style="padding:3px 0"><div><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Pass@3</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">42.6</div></div><div style="margin-top:7px"><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Average</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">50.4</div></div></div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><div class="metric-stack" style="padding:3px 0"><div><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Pass@3</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717"><strong>57.4</strong></div></div><div style="margin-top:7px"><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Average</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717"><strong>60.1</strong></div></div></div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><div class="metric-stack" style="padding:3px 0"><div><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Pass@3</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">52.5</div></div><div style="margin-top:7px"><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Average</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">54.7</div></div></div></td></tr>
<tr><td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Multimodal software engineering</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">SWE-MM</div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>38.6</strong></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">25.7</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">30.0</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">27.1</td></tr>
<tr><td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Visual web development</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">Vision2Web</div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>62.9</strong></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">45.0</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">42.1</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td></tr>
<tr><td colspan="6" style="padding:8px 12px;font-weight:600;color:#0A2EFE;border-bottom:1px solid rgba(10, 46, 254, 0.2);background:#D6DAFC">General Multimodal Intelligence</td></tr>
<tr><td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Visual math problem solving</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">MathVision</div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;"><div class="metric-stack" style="padding:3px 0"><div><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Without CI</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">90.0</div></div><div style="margin-top:7px"><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">With CI</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717"><strong>94.6</strong></div></div></div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><div class="metric-stack" style="padding:3px 0"><div><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Without CI</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">85.1</div></div></div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><div class="metric-stack" style="padding:3px 0"><div><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Without CI</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717"><strong>90.3</strong></div></div></div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><div class="metric-stack" style="padding:3px 0"><div><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Without CI</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">65.5</div></div></div></td></tr>
<tr><td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">General visual reasoning</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">BabyVision</div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;"><div class="metric-stack" style="padding:3px 0"><div><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Without CI</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717"><strong>65.7</strong></div></div><div style="margin-top:7px"><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">With CI</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717"><strong>85.6</strong></div></div></div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><div class="metric-stack" style="padding:3px 0"><div><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Without CI</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">28.9</div></div></div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><div class="metric-stack" style="padding:3px 0"><div><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Without CI</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">64.7</div></div><div style="margin-top:7px"><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">With CI</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">70.4</div></div></div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><div class="metric-stack" style="padding:3px 0"><div><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Without CI</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">12.6</div></div></div></td></tr>
<tr><td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Scientific chart analysis</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">CharXiv (RQ)</div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;"><div class="metric-stack" style="padding:3px 0"><div><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Without CI</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">83.7</div></div><div style="margin-top:7px"><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">With CI</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717"><strong>90.2</strong></div></div></div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><div class="metric-stack" style="padding:3px 0"><div><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Without CI</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">78.4</div></div></div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><div class="metric-stack" style="padding:3px 0"><div><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Without CI</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717"><strong>85.8</strong></div></div><div style="margin-top:7px"><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">With CI</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">85.9</div></div></div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">78.8</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><div class="metric-stack" style="padding:3px 0"><div><div class="metric-label" style="font-size:10px;font-weight:400;line-height:1.1;color:#777">Without CI</div><div class="metric-value" style="margin-top:2px;font-size:15px;line-height:1.15;color:#171717">66.0</div></div></div></td></tr>
<tr><td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Document intelligence</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">OmniDocBench 1.5</div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;">91.1</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">89.4</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>91.4</strong></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">75.8</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">86.6</td></tr>
<tr><td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Real-world perception</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">RealWorldQA</div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;">85.9</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">84.1</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>86.9</strong></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">73.9</td></tr>
<tr><td class="benchmark-cell" style="padding:7px 7px;padding-left:20px;border-bottom:1px solid rgba(128, 128, 128, 0.15);"><div class="benchmark-capability" style="font-size:15px;font-weight:600;line-height:1.22;color:#171717">Embodied intelligence</div><div class="benchmark-name" style="margin-top:4px;font-size:11px;font-weight:400;line-height:1.2;color:#6B6B6B">ERQA</div></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);background:rgba(10, 46, 254, 0.08);vertical-align:middle;font-size:15px;line-height:1.2;">65.5</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">62.5</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;"><strong>69.8</strong></td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">--</td><td style="padding:7px 7px;text-align:center;border-bottom:1px solid rgba(128, 128, 128, 0.15);vertical-align:middle;font-size:15px;line-height:1.2;">40.8</td></tr>
</tbody>
</table>
<div style="margin-top:12px;font-size:11px;line-height:1.5;color:rgba(0,0,0,0.72)">
<ol style="margin:0;padding-left:20px">
<li>MathVision, BabyVision, and CharXiv (RQ): Where both settings are available, cells report “Without CI” and “With CI” separately; otherwise, only the available setting is shown. A small number of incorrect ground-truth annotations in MathVision and CharXiv (RQ) were corrected following manual verification, and all reported scores on those benchmarks were computed using the corrected annotations.</li>
<li>MathVision: Qwen3.8-27B is evaluated using the fixed prompt: “Please reason step by step, and put your final answer within <code>\boxed{}</code>.” For the remaining models, we report the higher score from two prompt variants—one with and one without the <code>\boxed{}</code> formatting requirement.</li>
<li>WebArena-Verified: Scores are computed with the official WebArena-Verified grader under the OSWorld scaffold.</li>
<li>RecreationBench: An in-house, long-horizon application-recreation benchmark designed to evaluate hybrid-agent capabilities across five platforms: desktop (Ubuntu, macOS, and Windows), mobile (Android), and the web.</li>
<li>ClawEval-MM: Scores are reported as “Pass@3 / average score.” Pass@3 is the percentage of tasks passed in at least one of three trials; the average score is the mean benchmark score across the three trials.</li>
<li>Vision2Web: Scores are averaged across the frontend, webpage, and website categories. Evaluations use the Claude Code harness and are judged by <code>gpt-5.4-2026-03-05</code>.</li>
<li>SWE-MM: Scores are evaluated on the Claude Code harness using the public dev split of SWE-bench Multimodal, with the modifications described in Appendix 8.3 of the Claude Opus 4.7 system card.</li>
<li>Empty cells (--) indicate that results are not yet available or not applicable.</li>
</ol></div>
</div>


## Quickstart

For streamlined integration, we recommend using Qwen3.8 via APIs.

### Serving Qwen3.8

> [!Important]
> Inference efficiency and throughput vary significantly across frameworks. 
> We recommend using the latest framework versions to ensure optimal performance and compatibility.
> For production workloads or high-throughput scenarios, dedicated serving engines such as SGLang, vLLM, or TokenSpeed are recommended.

Qwen3.8 can be deployed with popular inference frameworks, e.g.:

- [SGLang](https://www.sglang.io/): [Qwen3.8 Cookbook](https://docs.sglang.io/cookbook/autoregressive/Qwen/Qwen3.8-27B)
- [vLLM](https://vllm.ai/): [Qwen3.8 Recipe](https://recipes.vllm.ai/Qwen/Qwen3.8-27B)
- [TokenSpeed](https://lightseek.org/tokenspeed/): [Qwen3.8 Recipe](https://lightseek.org/tokenspeed/recipes/models#qwen3-8)


### API Usage

> [!Important]
> Qwen3.8 models operate in thinking mode by default, generating thinking content signified by `<think>\n...</think>\n\n` before producing the final response.
> To disable thinking content and obtain a direct response, refer to the examples [here](#instruct-or-non-thinking-mode).


> [!Tip]
> We recommend using the following sets of sampling parameters for generation:
> - Thinking Mode: `temperature=1.0`, `top_p=0.95`, `top_k=20`, `min_p=0.0`, `presence_penalty=0.0`, `repetition_penalty=1.0`
> - Instruct (or non-thinking) mode: `temperature=0.7`, `top_p=0.80`, `top_k=20`, `min_p=0.0`, `presence_penalty=1.5`, `repetition_penalty=1.0`
>
> Please note that the support for sampling parameters varies according to inference frameworks.


Qwen3.8 comes with official support for `reasoning_effort`, which can be used to adjust reasoning depth and control cost:  
  - `xhigh` (default): for complex tasks demanding thorough analysis
  - `medium`: balancing accuracy and speed
  - `low`: efficient reasoning optimizing for speed and cost


In addition, `preserve_thinking` is enabled by default for all workloads for the best out-of-the-box experience. To disable preserved thinking, refer to the examples [here](#disable-preserved-thinking).

> [!Tip]
> In multi-turn agentic tasks, lower reasoning effort does not always reduce overall task completion time. Although it may produce faster per-turn responses, it can also lead to insufficient analysis, more failures, and repeated retries, which may increase total latency and token consumption.


#### Chat Completions API

The Chat Completions API can be used with most inference frameworks, as well as [Qwen Cloud](https://www.qwencloud.com/).
Before starting, make sure the OpenAI Python SDK is installed and the API key and the API base URL are configured, e.g.:
```shell
pip install -U openai

# Set the following accordingly
export OPENAI_BASE_URL='your-base-url'
export OPENAI_API_KEY='your-api-key'
```

##### Text-Only Input

```python
from openai import OpenAI
# Configured by environment variables
client = OpenAI()

messages = [{"role": "user", "content": "Write a Python function to merge two sorted linked lists."}]

completion = client.chat.completions.create(
    model="Qwen/Qwen3.8-27B",
    messages=messages,
    extra_body={
        "chat_template_kwargs": {
            "enable_thinking": True,  # on by default
            "preserve_thinking": True, # on by default
        },
    },
    reasoning_effort="xhigh",  # xhigh by default; supported levels are xhigh, medium, and low
    stream=True,
    stream_options={"include_usage": True},
)

reasoning_content = ""
answer_content = ""
is_answering = False
print("\n" + "=" * 20 + "Reasoning" + "=" * 20 + "\n")

for chunk in completion:
    if not chunk.choices:
        print("\nUsage:")
        print(chunk.usage)
        continue

    delta = chunk.choices[0].delta

    if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
        if not is_answering:
            print(delta.reasoning_content, end="", flush=True)
        reasoning_content += delta.reasoning_content
    elif hasattr(delta, "reasoning") and delta.reasoning is not None:
        if not is_answering:
            print(delta.reasoning, end="", flush=True)
        reasoning_content += delta.reasoning

    if hasattr(delta, "content") and delta.content:
        if not is_answering:
            print("\n" + "=" * 20 + "Answer" + "=" * 20 + "\n")
            is_answering = True
        print(delta.content, end="", flush=True)
        answer_content += delta.content

messages.append({
    "role": "assistant",
    "content": answer_content,
    "reasoning_content": reasoning_content,
    "reasoning": reasoning_content,
})
```


##### Image Input

```python
from openai import OpenAI
# Configured by environment variables
client = OpenAI()

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://qianwen-res.oss-accelerate.aliyuncs.com/Qwen3.5/demo/CI_Demo/mathv-1327.jpg"
                }
            },
            {
                "type": "text",
                "text": "The centres of the four illustrated circles are in the corners of the square. The two big circles touch each other and also the two little circles. With which factor do you have to multiply the radii of the little circles to obtain the radius of the big circles?\nChoices:\n(A) $\\frac{2}{9}$\n(B) $\\sqrt{5}$\n(C) $0.8 \\cdot \\pi$\n(D) 2.5\n(E) $1+\\sqrt{2}$"
            }
        ]
    }
]

chat_response = client.chat.completions.create(
    model="Qwen/Qwen3.8-27B",
    messages=messages,
)
print("Chat response:", chat_response)
```

##### Video Input

```python
from openai import OpenAI
# Configured by environment variables
client = OpenAI()

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "video_url",
                "video_url": {
                    "url": "https://qianwen-res.oss-accelerate.aliyuncs.com/Qwen3.5/demo/video/N1cdUjctpG8.mp4"
                }
            },
            {
                "type": "text",
                "text": "How many porcelain jars were discovered in the niches located in the primary chamber of the tomb?"
            }
        ]
    }
]

chat_response = client.chat.completions.create(
    model="Qwen/Qwen3.8-27B",
    messages=messages,
)

# When vLLM is launched with `--media-io-kwargs '{"video": {"num_frames": -1}}'`,
# video frame sampling can be configured via `extra_body` (e.g., by setting `fps`).
# This feature is currently supported only in vLLM.
#
# By default, `fps=2` and `do_sample_frames=True`.
# With `do_sample_frames=True`, you can customize the `fps` value to set your desired video sampling rate.
# chat_response = client.chat.completions.create(
#     model="Qwen/Qwen3.8-27B",
#     messages=messages,
#     extra_body={
#         "mm_processor_kwargs": {"fps": 2, "do_sample_frames": True},
#     }, 
# )

print("Chat response:", chat_response)
```


##### Instruct (or Non-Thinking) Mode

Qwen3.8-27B will think by default before responding.
You can obtain a direct response from the model without thinking by configuring the API parameters. 
For example,
```python
from openai import OpenAI
# Configured by environment variables
client = OpenAI()

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://qianwen-res.oss-accelerate.aliyuncs.com/Qwen3.5/demo/RealWorld/RealWorld-04.png"
                }
            },
            {
                "type": "text",
                "text": "Where is this?"
            }
        ]
    }
]

chat_response = client.chat.completions.create(
    model="Qwen/Qwen3.8-27B",
    messages=messages,
    temperature=0.7,
    top_p=0.8,
    presence_penalty=1.5,
    extra_body={
        "top_k": 20,
        "chat_template_kwargs": {"enable_thinking": False},
    }, 
)
print("Chat response:", chat_response)
```

> [!Note]
> If you are using APIs from Qwen Cloud, in addition to changing `model`, please use `"enable_thinking": False` instead of `"chat_template_kwargs": {"enable_thinking": False}`.


##### Disable Preserved Thinking


By default, Qwen3.8 retains thinking blocks from all historical messages, maintaining a complete reasoning trace across the conversation. This behavior, known as preserved thinking, ensures full context continuity and is especially beneficial for agent scenarios where decision consistency and reduced redundant reasoning are critical. It also improves KV cache utilization, optimizing inference efficiency in both thinking and non-thinking modes.

If you prefer to retain only the thinking blocks from the latest user message, you can disable this behavior by setting `preserve_thinking` to `False`:

```python
from openai import OpenAI

# Configured by environment variables
client = OpenAI()
messages = [...]
chat_response = client.chat.completions.create(
    model="Qwen/Qwen3.8-27B",
    messages=messages,
    extra_body={
        "chat_template_kwargs": {"preserve_thinking": False},
    },
)
print("Chat response:", chat_response)
```

> [!Note]
> If you are using APIs from Qwen Cloud, in addition to changing `model`, please use `"preserve_thinking": False` directly instead of wrapping it in `chat_template_kwargs`.


## Best Practices

To achieve optimal performance, we recommend the following settings:

1. **Sampling Parameters**: We suggest using the following sets of sampling parameters:  
    
    - Thinking Mode: `temperature=1.0`, `top_p=0.95`, `top_k=20`, `min_p=0.0`, `presence_penalty=0.0`, `repetition_penalty=1.0`
    - Instruct (or non-thinking) mode: `temperature=0.7`, `top_p=0.80`, `top_k=20`, `min_p=0.0`, `presence_penalty=1.5`, `repetition_penalty=1.0`
    
    For supported frameworks, you can adjust the `presence_penalty` parameter between 0 and 2 to reduce endless repetition. However, using a higher value may occasionally result in language mixing and a slight decrease in model performance.

2. **Adequate Output Length**: To optimize performance on agentic tasks, we recommend allocating sufficient output length to allow the model to generate detailed and comprehensive responses. For frameworks that support separate token limits for internal reasoning and final outputs, we suggest the following configuration within the 1M context length:
    
    - Reasoning Content: Set the maximum output length to 262,144 tokens.
    - Final Response: Set the maximum output length to 131,072 tokens.

    These settings provide the necessary capacity for complex reasoning while ensuring ample space for high-quality final deliverables.

3. **Processing Ultra-Long Texts**: Qwen3.8-27B natively supports context lengths of up to 262,144 tokens. For long-horizon tasks where the total length (including both input and output) exceeds this limit, we recommend using RoPE scaling techniques to handle long texts effectively, e.g., YaRN.

    YaRN is currently supported by several inference frameworks, e.g., vLLM, SGLang, and TokenSpeed. 
    In general, there are two approaches to enabling YaRN for supported frameworks:

    - Modifying the model configuration file:
        
        In the `config.json` file, change the `rope_parameters` fields in `text_config` to:
        ```json
        {
            "mrope_interleaved": true,
            "mrope_section": [
                11,
                11,
                10
            ],
            "rope_type": "yarn",
            "rope_theta": 10000000,
            "partial_rotary_factor": 0.25,
            "factor": 4.0,
            "original_max_position_embeddings": 262144,
        }
        ```

    - Passing command line arguments:

        For vLLM, you can use
        ```shell
        VLLM_ALLOW_LONG_MAX_MODEL_LEN=1 vllm serve ... --hf-overrides '{"text_config": {"rope_parameters": {"mrope_interleaved": true, "mrope_section": [11, 11, 10], "rope_type": "yarn", "rope_theta": 10000000, "partial_rotary_factor": 0.25, "factor": 4.0, "original_max_position_embeddings": 262144}}}' --max-model-len 1000000  
        ```

        For SGLang, you can use
        ```shell
        SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1 python -m sglang.launch_server ... --json-model-override-args '{"text_config": {"rope_parameters": {"mrope_interleaved": true, "mrope_section": [11, 11, 10], "rope_type": "yarn", "rope_theta": 10000000, "partial_rotary_factor": 0.25, "factor": 4.0, "original_max_position_embeddings": 262144}}}' --context-length 1000000
        ```

        For TokenSpeed, you can use
        ```shell
        TOKENSPEED_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1 tokenspeed serve ... --hf-overrides '{"text_config": {"rope_parameters": {"mrope_interleaved": true, "mrope_section": [11, 11, 10], "rope_type": "yarn", "rope_theta": 10000000, "partial_rotary_factor": 0.25, "factor": 4.0, "original_max_position_embeddings": 262144}}}' --max-model-len 1000000  
        ```
    
    > [!NOTE]
    > All the notable open-source frameworks implement static YaRN, which means the scaling factor remains constant regardless of input length, **potentially impacting performance on shorter texts.**
    > We advise modifying the `rope_parameters` configuration only when processing long contexts is required. 
    > It is also recommended to modify the `factor` as needed. For example, if the typical context length for your application is 524,288 tokens, it would be better to set `factor` as 2.0. 


4. **Long Video Understanding**: To optimize inference efficiency for plain text and images, the `size` parameter in the released `video_preprocessor_config.json` is conservatively configured. It is recommended to set the `longest_edge` parameter in the video_preprocessor_config file to 469,762,048 (corresponding to 224k video tokens) to enable higher frame-rate sampling for hour-scale videos and thereby achieve superior performance. For example,
    ```json
    {"longest_edge": 469762048, "shortest_edge": 4096}
    ```

    Alternatively, override the default values via engine startup parameters. For implementation details, refer to: [vLLM](https://github.com/vllm-project/vllm/pull/34330) / [SGLang](https://github.com/sgl-project/sglang/pull/18467).


## Citation

If you find our work helpful, feel free to give us a cite.


```bibtex
@misc{qwen38,
    title = {{Qwen3.8-Max}: A New Bar for Coding and Cowork},
    url = {https://qwen.ai/blog?id=qwen3.8},
    author = {{Qwen Team}},
    month = {August},
    year = {2026}
}
```

---

<h2>FIVE DETAILED EXAMPLE GENERATION(S):</h2>

Q4KS, non imatrix, standard Qwen settings, NO cache compression of any kind.

NOTE: Some formatting may be lost on copy/paste/export.

---

[ TO BE ADDED]