# Koroush AK trên X: "How to Use Claude to Build TradingView Indicators" / X

## Bài viết

If you're a trader, you can't afford to miss this.

I will show you how to use Claude to build your first Tradingview indicator in the next 5 minutes.

What you'll have when you're done:

-   Claude Code connected to your TradingView (takes one prompt, it installs itself)
    
-   A working OI momentum indicator saved to your TradingView account permanently (you can use this exact workflow to build any other indicator the same way)
    
-   Real trade examples using the indicator (breakouts and reversals)
    

Difficulty: Beginner (no coding required).

Bonus: I’ve made you a cheat sheet and setups for even more free indicators. Access this now 👉

[here](https://go.koroushak.io/tv_ai_pdf)

. Let’s begin.

# 

Credit Where It's Due

None of this exists without

[@Tradesdontlie](https://x.com/@Tradesdontlie)

on GitHub, who reverse-engineered TradingView's debug protocol and built the open-source bridge this whole setup runs on. Star the repo.

# 

Prerequisite Steps

-   Step 1: Install Node.js (18+)
    
-   Step 2: Install Claude Code
    
-   Step 3: Launch TradingView Desktop with a paid subscription,
    
    [tradingview.com/desktop](http://tradingview.com/desktop)
    

If you get stuck at any point, just copy and paste this article into Claude. It will show you what to do.

# 

Part 1: Get Claude Talking to TradingView

[

![Hình ảnh](https://pbs.twimg.com/media/HGdDIX-XUAAHRCl?format=jpg&name=small)

](/KoroushAK/article/2046950514743529688/media/2046678366816784384)

## 

Step 1: Open Claude Code

Run the following prompt:

shell

```text
"Install the TradingView MCP server. Clone and explore https://github.com/tradesdontlie/tradingview-mcp, run npm install, add to my MCP config at ~/.claude/.mcp.json, and launch TradingView with the debug port."
```

For a few minutes, you will need to wait and click “allow” for the relevant permissions.

## 

Step 2: Verify

Quit Claude Code (type '/exit' or Ctrl+C twice). Reopen:

Run this prompt:

shell

```text
"Use tv_health_check to confirm TradingView is connected"
```

[

![Hình ảnh](https://pbs.twimg.com/media/HGgWTxRX0AATLAv?format=jpg&name=small)

](/KoroushAK/article/2046950514743529688/media/2046910559539417088)

Setup done. Permanently. You'll never run these commands again (except the TradingView debug-port launch, once per session). Remember: always launch TradingView from Claude Code using this command, otherwise this will not work.

NOTE: if you run into issues here, one of the easiest troubleshooting steps is to simply screenshot the error into Claude.

# 

Part 2: Build a Real Indicator

Most guides stop at "it's connected!" Here, you actually ship something.

We're building the ‘ZCT Momentum Filter’.

Four prompts + one save step. Four visible features. Each one is small enough to verify before moving on.

The rule: one prompt, one change. Don't batch asks. The whole point of an incremental build is that you understand what each line does because you saw it render.

## 

Phase 1: Plot Open Interest

Paste to Claude Code:

```text
Write a Pine Script v6 indicator called "ZCT Momentum Filter" that plots open interest for the current symbol as a yellow line in its own pane. Use request.security with the "_OI" suffix and multiply by close price for dollar-denominated OI. Save it to ~/zct-momentum-filter.pine and inject it into my TradingView Pine Editor.
```

Claude saves the file, opens Pine Editor, and pastes the script. Click the ▶ Play button at the top of the Pine Editor to compile.

Expected: A yellow line in a new pane below your chart.

[

![Hình ảnh](https://pbs.twimg.com/media/HGgX4EyWAAELYZ1?format=jpg&name=small)

](/KoroushAK/article/2046950514743529688/media/2046912282764902401)

I’ve selected yellow for the example because it shows up on both a dark and light background. (You can edit this for whatever colour you want.)

If you see "no data": OI doesn't exist on that symbol. Switch to 'BINANCE:BTCUSDT.P'.

## 

Phase 2: Add the EMAs

Paste to Claude Code:

```text
Add a 60-period EMA of the OI in blue, and a 240-period EMA in green.
```

Hit ▶. Three lines now: yellow OI, blue fast EMA, green slow EMA.

## 

Phase 3: Shade the gap

The visual that makes the indicator readable at a glance:

```text
Fill the area between the two EMAs. Green at 85% transparency when blue is above green, red at 85% transparency when blue is below green.
```

Hit ▶. The pane now flips colour based on which EMA is on top.

[

![Hình ảnh](https://pbs.twimg.com/media/HGgcAE1X0AAaeLU?format=jpg&name=small)

](/KoroushAK/article/2046950514743529688/media/2046916818263068672)

## 

Phase 4: Make it adjustable

Paste to Claude Code:

```text
Make both EMA lengths user-adjustable from the settings panel, defaulting to 60 and 240.
```

Recompile. Click the gear icon on the indicator name above the chart. Two input fields for the EMA periods. Change them: the indicator updates live.

![](https://pbs.twimg.com/amplify_video_thumb/2046735976391745536/img/w2y4qIbtkAfe1qSv.jpg)

## 

Phase 5: Save it permanently

Claude's injection is session-only. To keep it:

1.  In Pine Editor, Cmd+S
    
2.  Name it
    
3.  Save → Add to Chart
    

Now it lives in Indicators → My Scripts forever.

# 

How to Actually Use This Indicator

Having it on your chart is nothing. Knowing what it's telling you is what matters.

Quick definitions if you're new to either term:

-   Open Interest (OI): the total number of open contracts on a futures or perpetual market: a measure of how many traders currently have positions on either side. Rising OI = traders opening new positions. Falling OI = traders closing positions.
    
-   EMA (Exponential Moving Average): a moving average that weights recent prices more heavily than older ones: reacts faster to changes than a simple average. We use a fast EMA (60 periods) and slow EMA (240) on the OI line to spot when momentum is shifting.
    

Quick reference:

-   Breakouts: OI consistently expanding, fill solid green, gradual, not vertical
    
-   Breakdowns: OI consistently contracting, fill solid red, gradual, not vertical
    
-   Reversals: OI choppy and inconsistent, fill flipping rapidly
    

## 

Breakout environment: when I want to be in trend trades.

[

![Hình ảnh](https://pbs.twimg.com/media/HGd13zrWUAApaeX?format=png&name=small)

](/KoroushAK/article/2046950514743529688/media/2046734157288460288)

[

![Hình ảnh](https://pbs.twimg.com/media/HGd19YvXoAAmMrW?format=jpg&name=small)

](/KoroushAK/article/2046950514743529688/media/2046734253136781312)

I want to see open interest trending in one direction with the EMA fill consistently expanding. A staircase up, hours of consistently increasing OI, fill staying green. That tells me participants are consistently interested in opening contracts on one side. The market believes price needs to keep moving: it's signalling momentum is on my side.

When I'm in a momentum long, and OI starts to retract back into the EMA band, that's my caution flag. Participants are cooling off. Even if the price keeps grinding higher, momentum is fading underneath. I get cautious about adding or holding through that window.

## 

Breakdown environment: mirror breakouts.

[

![Hình ảnh](https://pbs.twimg.com/media/HGd2PEGXIAAgMvS?format=png&name=small)

](/KoroushAK/article/2046950514743529688/media/2046734556833718272)

[

![Hình ảnh](https://pbs.twimg.com/media/HGd2RA-WYAA9z_g?format=png&name=small)

](/KoroushAK/article/2046950514743529688/media/2046734590354546688)

For shorts, I want to see consistently decreasing open interest with the fill staying red. Participants closing contracts, longs getting flushed, gravity pulling price down. Sustained, consistent contraction in OI alongside decreasing volume is a high-quality momentum short condition.

## 

Reversal environment: when I want to fade the range.

[

![Hình ảnh](https://pbs.twimg.com/media/HGd2dyAXIAA4blW?format=jpg&name=small)

](/KoroushAK/article/2046950514743529688/media/2046734809674752000)

[

![Hình ảnh](https://pbs.twimg.com/media/HGd2hn7WcAAec00?format=png&name=small)

](/KoroushAK/article/2046950514743529688/media/2046734875688857600)

I want to see the opposite: choppy, inconsistent OI. Green to red to green to red, no sustained direction. This tells me participants don't have a clear bias. Sentiment is mixed. Price is fairly valued and likely to chop until someone decides where it should go.

When I see this signature, I'm not chasing momentum. I'm taking what the market is offering: fast-spike mean reversion plays inside the range, not breakouts.

Get more of my free indicators + a bonus cheat sheet 👉

[here](https://go.koroushak.io/tv_ai_pdf)

.

# 

Worth Knowing Before You Commit

-   Some prompts take 2-10 minutes. The CDP injection isn't instant, especially on first use per session. A screenshot or price fetch is fast; a Pine Script injection can stall. If it hangs, ask Claude to print the file contents and paste manually into Pine Editor yourself.
    
-   You'll be clicking "Allow" a lot on your first few runs. Each new tool Claude wants to call asks permission. Pick the "Yes, and don't ask again" option to clear this.
    
-   Tokens aren't free. A full chart analysis with screenshots can eat a non-trivial chunk of your Claude usage. Best suited for high-leverage work (building, backtesting, report generation), not for "change my timeframe to 4h", do that manually.
    
-   The debug port doesn't persist across restarts. Every time you reboot or close TradingView, relaunch TradingView from Claude Code so the debug port is active.
    
-   Injected scripts are session-only unless you Cmd+S to save them to your account.
    

If you found this helpful and want more guides like it,

Share this with someone who will benefit and drop a comment to let me know if you want more.
