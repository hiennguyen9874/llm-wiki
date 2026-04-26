# Trades Dont Lie trên X: "How to Connect Claude to TradingView" / X

## Bài viết

[https://github.com/tradesdontlie/tradingview-mcp](https://github.com/tradesdontlie/tradingview-mcp)

TradingView doesn't have a public API. That's just the reality. After experimenting and building hundreds of different indicators I needed a solution to improve my workflow to allow my coding agent to interact with Tradingview for me. No more copy and pasting or manually checking indicator values myself. I needed a Pine Script development workflow with AI in the loop way of working with my indicators and strategies inside the charting platform that wasn't a shitty ui click automation...

The desktop app is built on Electron, which runs on Chromium, which has a debugging interface built into it called Chrome DevTools Protocol. It's in every Electron app — VS Code, Slack, Discord, all of them. It's off by default. One flag at launch turns it on. That's the door.

I built this as a research project. I wanted to see what actually happens when you give an LLM structured access to a live charting platform. Can Claude read chart data accurately? Where does it get confused? Is natural language a useful way to write Pine Script? What breaks when the agent is working with live data in real time?

The result is 78 MCP tools and a full CLI. This is what I found.

0:00 / 0:29

the CLI binary is called tv, not tv-mcp or tradingview-mcp

If any of this sounds interesting to you, you can explore it on your own terms. I'll explain what's technically possible and how it all works. What you do with it is up to you.

## 

I. How It Works

[

![Hình ảnh](https://pbs.twimg.com/media/HEw6LGPbAAAk-TR?format=png&name=small)

](/Tradesdontlie/article/2039080409581891890/media/2039068693620260864)

Three pieces, all running locally on your machine.

Claude Code talks to a Node.js MCP server. That server connects to your running TradingView Desktop app over Chrome DevTools Protocol on port 9222. CDP is a standard Google debugging interface built into every Chromium app. Off by default. One flag turns it on.

Nothing touches TradingView's servers. No data leaves your machine. The port stays closed until you deliberately open it.

The whole tool set also ships as a tv CLI, JSON output, pipe-friendly, works from any terminal or shell script.

One thing worth knowing upfront: this accesses undocumented internal TradingView APIs through the Electron debug interface. TradingView can change those internals in any update without notice. If you use this and want it to stay stable, pin your TradingView Desktop version.

## 

II. What Claude Can Actually See

[

![Hình ảnh](https://pbs.twimg.com/media/HEw7F3naIAACKFd?format=png&name=small)

](/Tradesdontlie/article/2039080409581891890/media/2039069703306616832)

This is the part that surprised me most when I started building it.

Beyond the obvious stuff like symbol, timeframe, and indicator values, Claude can read the actual drawing objects that Pine Script indicators put on your chart. The

[line.new](//line.new)

() calls,

[label.new](//label.new)

(),

[table.new](//table.new)

(),

[box.new](//box.new)

(). Anything your indicator draws on screen, Claude can read back as structured data. This works on protected indicators too. You just pass a filter targeting the indicator by name and you get back every price level, every text annotation, full table contents, every drawn zone.

Ask Claude "what levels is my NY Sessions indicator showing?" and it reads them. "What does the session stats table say?" It reads that too.

The full picture of what's available: current symbol and timeframe, all indicator names and IDs, real-time OHLC and volume, up to 500 price bars or a compact summary, all data window values, Pine drawings of every type, order book depth, strategy tester results and trade list, symbol metadata, and screenshots of any chart region.

Worth saying clearly: all of this data is already on your screen the moment TradingView is open. The app is displaying it. This tool just makes it readable to an LLM.

## 

III. What's Technically Possible

[

![Hình ảnh](https://pbs.twimg.com/media/HEw6SdIaUAAx4bI?format=png&name=small)

](/Tradesdontlie/article/2039080409581891890/media/2039068820023955456)

Before going into this section: be aware of TradingView's Terms of Service before you build anything. The data these tools surface is data you already have access to as a paying subscriber, displayed in an app running on your own machine. What you do with it programmatically is yours to reason through against their terms. This is a research project and these are the possibilities I found.

Pine Script development with AI in the loop. This is the one that made me keep working on it. You describe what you want, Claude writes the script, injects it into the Pine editor, compiles it, reads the errors back, fixes them, and recompiles. That loop runs until the script is clean. The whole time it has full context of your current chart and whatever indicators are on it. There's also offline static analysis before compile and a server-side compile check that doesn't even need to touch the chart. For anyone who has spent an afternoon bouncing between a text editor and the Pine editor hunting a type mismatch, this changes the workflow considerably. I still personally code in VS code terminal using Claude Code CLI because its easy to keep all my indicators in one repo for organizational purposes, but now instead of copy and pasting my indicator back and forth Claude can send it to TV and compile it and screen shot it or use the indicator data with the OHLC data and confirm what I'm trying to implement is correct.... within reason of course.

Your chart as a local data source. The streaming commands poll your running TradingView Desktop via CDP on localhost and output JSONL, one JSON object per line. You can pipe that into Python, Node, shell scripts, jq filters, whatever you want to build locally. Set up a 2x2 grid with NQ, ES, YM, and GC and stream all four panes simultaneously. The data goes from your app to a process on your own machine, nowhere else.

Scripting repetitive chart tasks. Every tool is available as a CLI command with consistent JSON output. Anything you do manually on repeat is a candidate for a script. Multi-symbol screens, screenshot runs, morning layout setup, chart state snapshots, batch indicator configuration. The output composes with anything that reads stdin.

Indicator validation. Write a script, compile it, read the values back, check that the math matches your expectations. Loop through input parameters and read the output each time. Run the same indicator across multiple symbols and timeframes. Read strategy tester metrics after each compile. The actual workflow of verifying your indicators rather than assuming they work.

Replay with structured logging. Step through historical bars, log the indicator values at each step to JSONL, record your trade decisions, capture screenshots at entries and exits. A proper practice record instead of just clicking through replay and hoping something sticks.

## 

IV. The CLI

Every MCP tool is also a terminal command. The whole thing ships as a tv CLI with JSON output that pipes anywhere.

bash

```bash
# reading your chart
tv status
tv quote
tv ohlcv --summary
tv data lines
tv data values

# navigation
tv symbol AAPL
tv timeframe D
tv pane layout 2x2
tv pane symbol 1 ES1!
tv layout switch "NQ"

# pine script
tv pine set < script.pine
tv pine compile
tv pine analyze
tv pine check
tv pine save

# streaming
tv stream quote | jq '.close'
tv stream bars
tv stream lines --filter "NY Levels"
tv stream tables --filter Profiler
tv stream all

# pine CI in one line
cat script.pine | tv pine analyze && cat script.pine | tv pine check
```

tv stream all is the most interesting thing to play with from a research perspective. Set up a multi-pane layout, run that command, and you have every symbol streaming simultaneously as JSONL into whatever you want downstream.

## 

V. Getting It Running

You need Node.js 18+ installed and TradingView Desktop with a valid subscription. After that, just give Claude this prompt and it handles the whole install:

> "Install the TradingView MCP server. Clone and explore
> 
> [https://github.com/tradesdontlie/tradingview-mcp](https://github.com/tradesdontlie/tradingview-mcp)
> 
> , run npm install, add to my MCP config at ~/.claude/.mcp.json, and launch TradingView with the debug port."

Once it's done, verify the connection:

> "Use tv\_health\_check to confirm TradingView is connected."

Then try it:

> "What's on my chart right now?"

> "Write a Pine Script VWAP indicator and add it to my chart."

> "Set up a 2x2 grid with NQ, ES, YM, and GC."

That's the whole setup. Claude installs it, Claude runs it. You just describe what you want. The only thing limiting you is your creativity. This isn't an end-all, be-all solution that's going to solve all your problems. This is just a tool to connect your charting platform to your large language model. You're still going to need to be able to logically come up with your own indicators ideas or models that you want to code, or know how to use the indicator data in your trading methodologies, or any of these things. This isn't going to solve all of your trading problems. This is just a technical tool... So, please don't forget that and be smart with whatever that you are trying to accomplish.

Personal research project. Not affiliated with TradingView Inc. Requires a valid TradingView subscription. Not financial advice.
