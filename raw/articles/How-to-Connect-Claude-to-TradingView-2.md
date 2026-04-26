# Miles Deutscher trên X: "How to Connect Claude to TradingView (FULL GUIDE) " / X

## Bài viết

If you're into financial markets, what I'm about to show you will completely change how you trade forever.

This setup is literally the closest thing a retail trader has ever had to a professional trading desk.

Claude can now connect directly to TradingView, acting as your personal AI assistant that reads ALL your data.

Think about what this actually means.

You can now vibe-code custom indicators, allow AI to process real-time price data in seconds, have Claude control your TradingView on your behalf, and way more.

The best part is, you can just paste this entire article into Claude and have it guide you through every step to achieve these results.

By the end of this article, you'll know exactly:

-   How this setup works
    
-   How to connect Claude x TradingView (in 5 minutes)
    
-   Real-world use cases & examples
    
-   My personal experience with this setup so far (some things to consider)
    

Before we start, I want to give credit and appreciation to

[@Tradesdontlie](https://x.com/@Tradesdontlie)

for making this possible and sharing his creation publicly.

Bài viết

How to Connect Claude to TradingView

TradingView doesn't have a public API. That's just the reality. After experimenting and building hundreds of different indicators I needed a solution to improve my workflow to allow my coding agent...

95

498

2 N

[

1 Tr

](/Tradesdontlie/status/2039080409581891890/analytics)

This is genuinely one of the most powerful AI use cases I've come across all year, and it inspired me to create my own version of his original guide.

## 

How this setup works (explained simply)

One of the biggest unsolved problems in AI trading has been:

How do you give your AI access to your live charts in real time, and have it analyse and act on what it sees without just producing AI slop?

Until now, there hasn't really been an easy answer.

Most trading platforms don't have a public API (like TradingView), and for the average person, building a solution is just too complicated and not worth the headache.

This setup kills all those problems using a TradingView "MCP" and is hands-down the easiest way for the average person to start using AI in their daily financial research/trading routine.

To get this working, you don't need to know what an MCP is; just know that MCPs allow LLMs (like Claude) to access data streams.

With this new TradingView MCP, Claude isn't just looking at a chart screenshot and guessing. It's reading the actual underlying values, the same way a developer's console reads a live webpage.

[

![Hình ảnh](https://pbs.twimg.com/media/HF0fXSXbUAADSia?format=jpg&name=small)

](/milesdeutscher/article/2044536031991763414/media/2043824290823622656)

TradingView + Claude (how it actually works under the hood)

TLDR: Accurate, real-time data from TradingView is being fed directly to your Claude agent. Claude can then act on that data.

## 

How to connect Claude x TradingView (in 5 minutes)

Set up requirements:

-   Claude Code - installed on your computer (this is what talks to TradingView)
    
-   Node.js 18+ - installed on your computer (the MCP server runs on this)
    
-   TradingView Desktop app - downloaded from
    
    [tradingview.com/desktop](//tradingview.com/desktop)
    
-   A valid TradingView subscription (paid plan for real-time data)
    

Getting started

If you're interested in the full GitHub repo,

[@Tradesdontlie](https://x.com/@Tradesdontlie)

created one here:

[

![Hình ảnh](https://pbs.twimg.com/media/HF0kob_aEAAn-mK?format=jpg&name=small)

](/milesdeutscher/article/2044536031991763414/media/2043830083023147008)

[https://github.com/tradesdontlie/tradingview-mcp](https://github.com/tradesdontlie/tradingview-mcp)

1.  Open Claude Code Desktop
    

Open Claude Code and run the following prompt:

```text
"Install the TradingView MCP server. Clone and explore https://github.com/tradesdontlie/tradingview-mcp, run npm install, add to my MCP config at ~/.claude/.mcp.json, and launch TradingView with the debug port."
```

[

![Hình ảnh](https://pbs.twimg.com/media/HF0oc5WasAEHztW?format=jpg&name=small)

](/milesdeutscher/article/2044536031991763414/media/2043834282792366081)

Claude Code prompt

For the next few minutes, stand by and click "allow" to give Claude access to connect to TradingView.

2\. Health Check

Restart Claude Code, and paste this prompt:

```text
"Use tv_health_check to confirm TradingView is connected."
```

If correctly connected, Claude Code should respond with:

"Connection confirmed. Here's the health check result..."

That's it - only two simple steps to get connected!

## 

Real-world use cases & examples

In the original GitHub repo, there is an example list of commands you can try.

[

![Hình ảnh](https://pbs.twimg.com/media/HF0pjjtasAA1NKq?format=jpg&name=small)

](/milesdeutscher/article/2044536031991763414/media/2043835496753967104)

Example Prompts List

Let me show you some of these prompts in action:

1.  Live Price Data Fetch From Your Charts
    

"Go to my TradingView charts and overlay the live price of

[$BTC](https://x.com/search?q=%24BTC&src=cashtag_click)

versus

[$SOL](https://x.com/search?q=%24SOL&src=cashtag_click)

\- which one is outperforming today, and what were the live prices from the entire day?"

[

![Hình ảnh](https://pbs.twimg.com/media/HF0qfcuasAAAOrD?format=jpg&name=small)

](/milesdeutscher/article/2044536031991763414/media/2043836525671264256)

Live Price Data Fetch

2\. Detailed Market Research Report

"I haven't been at my desk all day. Take a screenshot of the current price action on the SP500. Give me a detailed research report on what's happening today."

You can also use this prompt style for prompts like the following:

"Scan my entire watchlist and give a detailed report of what happened."

"Analyse my entire \[crypto/stocks/ETF\] watchlist and provide a deep research report on everything I may have missed today."

![](https://pbs.twimg.com/amplify_video_thumb/2043838797868347393/img/OPrRD07voVZ0Ubgv.jpg)

Detailed Research Report

3\. Source/Add Indicators

"Source the best and most used indicators for the following, and put them on my charts: volume, 100D moving average, and a volatility index."

Claude successfully completed the task and picked these three indicators based on its research:

[

![Hình ảnh](https://pbs.twimg.com/media/HF0uurpasAANdBb?format=jpg&name=small)

](/milesdeutscher/article/2044536031991763414/media/2043841185421373440)

Add Indicators Prompt (what Claude picked)

4\. Drawing/UI Automation

"Conduct technical analysis on the current state of Bitcoin. Once you have your analysis complete, draw what you're seeing on my charts so I can understand."

Claude then did a deep research session (10 minutes!) and actually drew TA on the charts:

![](https://pbs.twimg.com/amplify_video_thumb/2043850049697001473/img/9Eafp1iYwQVkNys3.jpg)

Claude's Analysis

[

![Hình ảnh](https://pbs.twimg.com/media/HF02mqraUAA_RD6?format=jpg&name=small)

](/milesdeutscher/article/2044536031991763414/media/2043849843815370752)

What Claude Drew

5. Alerts/Price Management

"I want you to manage my price alerts on TradingView. Set price alerts for

[$BTC](https://x.com/search?q=%24BTC&src=cashtag_click)

breaking above $75,000, set one for the SP500 breaking new all-time highs, and go through my watchlist and add any price alerts on potential dip buying opportunities."

You can also say things like:

"Add \[x\] to my \[stock\] watchlist."

"Analyse the current state of \[Mag 7/tech/AI/top 20 crypto tokens\] and add price alerts for any potential dip-buying opportunities that may arise this week."

[

![Hình ảnh](https://pbs.twimg.com/media/HF0x3Y6asAAywwy?format=png&name=small)

](/milesdeutscher/article/2044536031991763414/media/2043844633546108928)

Alerts/Price Management

Some other use cases worth mentioning:

-   Using Replay Mode - get Claude to use Replay mode for backtesting
    
-   Pine Script Development - custom indicators
    
-   Screenshot Captures - get Claude to actually fetch what your charts look like
    
-   Tab Management - open new tabs, switch tabs, close tabs
    
-   Full Chart Control - change timeframes, symbol search, and more
    

Hopefully, with these examples, you're starting to get an idea of what you can do with this system.

This is honestly just the bare bones of what you could do.

Imagine: getting Claude to create custom trading strategies/indicators, having Claude act as your backtesting study partner, or vibe-coding an app using your TradingView data.

The possibilities are truly limitless, and I'm excited to make content around all of these topics soon.

## 

My personal experience with this setup so far (some things to consider)

Obviously, this is a very cool and powerful tool, but there are some practical cons I found while using this:

Firstly, it's quite annoying to have to manually "babysit" Claude through each action, and it might be faster to handle some actions manually, even if the MCP can do them.

Some advice: use this in the background on a separate monitor/device where you're passively allowing Claude to work. If this is running on your main and only setup, I could imagine some prompts being quite inefficient and a waste of your time.

Piggybacking on that, I noticed a few prompts taking quite a while (10+ minutes).

Again, it's probably faster to create an alert yourself than to wait around clicking "Allow" for several minutes at a time.

Lastly, keep in mind that this does use Claude tokens.

Most of us only have so much Claude usage, so it's best to use it on the highest-leverage tasks.

Using 2-4% of your entire session to create a simple drawing on TradingView may not be worth it.

Overall, I'm focused on using this cool new tool for high-leverage tasks (creating strategies, automating Pine Scripts, etc.) rather than simple drawing tasks or changing the timeframe on my charts.

Last Tip: Pair w/ Claude Dispatch/Remote Control/Scheduled Tasks

Remember, Claude Code has remote-control functionalities and the ability to schedule tasks.

This means you can access your TradingView MCP on the go or even set tasks to run autonomously on a set schedule.

Things like scanning your watchlist every morning, providing a full report on which alerts triggered overnight, and so on could be helpful for many of you.
