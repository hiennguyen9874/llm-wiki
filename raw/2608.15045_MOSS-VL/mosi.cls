%%======================================================================
%%  mosi.cls — MOSI paper / technical-report class
%%
%%  House style: MOSI-blue headings, a Palatino body font, a logo header,
%%  a framed title with a gradient abstract box, and a row of link labels
%%  under the abstract (\checkdata).
%%
%%  Load with \documentclass{mosi}; see main.tex for usage.
%%
%%  Copyright (C) 2026 the MOSI group.
%%
%%  This work may be distributed and/or modified under the conditions of
%%  the LaTeX Project Public License (LPPL), version 1.3c or (at your
%%  option) any later version:  https://www.latex-project.org/lppl.txt
%%  LPPL maintenance status: `maintained' (Current Maintainer: the MOSI
%%  group).  Full text and the list of files comprising the Work are in
%%  the LICENSE file.  The OpenMOSS / MOSI logos in assets/ are group
%%  marks, NOT part of the licensed Work.
%%======================================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{mosi}[2026/05/23 v1.0 MOSI paper class]
\PassOptionsToPackage{table}{xcolor}    % enable \rowcolor (xcolor is pulled in by tcolorbox)
\LoadClassWithOptions{article}

% --- Page layout ---
% Keep the DEFAULT headheight (12pt). The two-logo first-page header is taller
% than that, so it deliberately spills upward into the top margin and sits
% snugly just above the title bar. Do NOT "fix" this by enlarging headheight:
% geometry (includehead=false) holds the body — and thus the title bar — fixed,
% so a taller header band only grows UP into the margin, dragging the logos far
% above the bar (an ugly gap). The price of a small headheight is fancyhdr's
% "headheight is too small" warning; since the overflow is into empty top margin
% (no header rule, first page only) it is purely cosmetic, and is filtered out
% where fancyhdr is loaded below.
\RequirePackage[top=2.75cm, bottom=2.5cm, left=2.5cm, right=2.5cm, columnsep=0.65cm]{geometry}
\RequirePackage{placeins}
\RequirePackage{hyphenat}
\RequirePackage{setspace}
\setstretch{1.04}
\RequirePackage{parskip}
\RequirePackage[english]{babel}
\RequirePackage{etoolbox}
% silence must load BEFORE fancyhdr to catch its warning. We intentionally keep
% a small headheight (see the geometry note above), so filter out the one
% cosmetic "headheight is too small" warning fancyhdr would emit. (Only that one
% message is suppressed; any other fancyhdr warning still shows.)
\RequirePackage{silence}
\WarningFilter{fancyhdr}{\headheight is too small}
% Another cosmetic warning, filtered here: microtype (loaded near the end of this
% class) redefines \showhyphens -- a hyphenation DEBUG command that never reaches
% the PDF -- after a \CheckCommand safety check. Newer LaTeX kernels (e.g. on
% Overleaf) define \showhyphens differently than microtype expects, so that check
% fires "Command \showhyphens has changed". Harmless. NB: the match text needs a
% single space and NO \protect to catch this generic LaTeX warning (verified).
\WarningFilter{latex}{Command \showhyphens has changed}
\RequirePackage{fancyhdr}

% --- Graphics and tables ---
\RequirePackage{graphicx}
\RequirePackage{subcaption}
\RequirePackage{booktabs}
\RequirePackage{multirow}
\RequirePackage[most]{tcolorbox}

% --- Colours ---
\definecolor{mosibg}{HTML}{2E5AA8}      % title frame / box border
\definecolor{mosiblue}{HTML}{2E5AA8}    % headings, links
\definecolor{mosicyan}{HTML}{82D9FF}    % abstract box gradient (left)
\definecolor{mosisky}{HTML}{82B1FF}     % abstract box gradient (right)
% Reference the *named* colour, not a hard-coded hex, so that editing the
% \definecolor{mosiblue} line above recolours the headings too (they go through
% this macro). The colour name "mosiblue" and the macro "\mosiblue" live in
% separate namespaces, so \color{mosiblue} does not invoke this macro.
\newcommand{\mosiblue}[1]{{\bfseries\color{mosiblue} #1}}

% --- References and links ---
% (cleveref is intentionally NOT loaded here: it must come after amsthm, which
%  is loaded further down. It is loaded just before the \newtheorem block.)
\RequirePackage{hyperref}
\hypersetup{
  colorlinks,
  linkcolor=mosiblue,
  citecolor=mosiblue,
  urlcolor=mosiblue
}
\RequirePackage[numbers, sort&compress]{natbib}
\def\bibfont{\small}
\addto{\captionsenglish}{\renewcommand{\refname}{References}}

% --- Headings (12 / 11 / normal, bold, MOSI blue) ---
\newcommand{\sectionfont}{\fontsize{12}{10}\selectfont}
\newcommand{\subsectionfont}{\fontsize{11}{10}\selectfont}
\RequirePackage{titlesec}
\titleformat*{\paragraph}{\itshape}
\titleformat*{\section}{\sectionfont\bfseries\mosiblue}
\titleformat*{\subsection}{\subsectionfont\bfseries\mosiblue}
\titleformat*{\subsubsection}{\normalsize\bfseries\mosiblue}

% --- Captions: bold "Figure N" / "Table N" run into the caption text ---
\RequirePackage{caption}
\DeclareCaptionLabelSeparator{mosi}{}
\DeclareCaptionFormat{mosi}{{{\bfseries #1 #2}} #3}
\captionsetup{singlelinecheck=true, format=mosi, labelsep=mosi, font=small}
\captionsetup[sub]{singlelinecheck=true, format=mosi, labelsep=mosi, font=small}

% --- Fonts (Palatino family) ---
\RequirePackage[T1]{fontenc}
\RequirePackage{amsmath, amsfonts, amssymb}
\RequirePackage{newpxtext}
\RequirePackage[bigdelims,vvarbb]{newpxmath}
% zlmtt (Latin Modern typewriter) ships a T1 font, so it applies under pdfTeX
% only; under xe/lualatex (Chinese mode) fontspec already supplies a Unicode
% monospace, and loading zlmtt there only warns "TU/zlmtt undefined". Guard it
% by engine, the same way the microtype block at the end of this class does.
\RequirePackage{iftex}
\ifPDFTeX
  \RequirePackage[scaled=1.1]{zlmtt}
\fi

% (No separate sans font: the \checkdata labels are simply bold in the body font.)

% --- Theorem-like environments (MOSI-blue heads) ---
%   All share one counter and are numbered within the section (Theorem 2.1,
%   Definition 2.2, ...), so numbers are unique and easy to find. \aliascnt
%   keeps that shared numbering while giving each environment its own counter
%   name, so \cref prints the right word ("Definition 2.2", not "Theorem 2.2").
\let\openbox\relax            % newpxmath already defined \openbox; let amsthm own it
\RequirePackage{amsthm}
\RequirePackage{aliascnt}
% cleveref's documented load order: AFTER hyperref / amsmath / amsthm, ideally
% last. We load it here — after amsthm above, but BEFORE the \newtheorem calls
% below — so it can hook \newtheorem and auto-register each environment's \cref
% name, and so it precedes the \crefname lines further down.
\RequirePackage[noabbrev,nameinlink]{cleveref}
\newtheoremstyle{mosiplain}{\topsep}{\topsep}{\itshape}{0pt}%
  {\bfseries\color{mosiblue}}{.}{.5em}{}      % theorem/lemma/...: italic body
\newtheoremstyle{mosidef}{\topsep}{\topsep}{\normalfont}{0pt}%
  {\bfseries\color{mosiblue}}{.}{.5em}{}      % definition/assumption: upright body
\newcommand{\mositheorem}[2]{%  #1 = env name, #2 = printed word, shares theorem counter
  \newaliascnt{#1}{theorem}%
  \newtheorem{#1}[#1]{#2}%
  \aliascntresetthe{#1}%
}
\theoremstyle{mosiplain}
\newtheorem{theorem}{Theorem}[section]   % the primary counter, reset each section
\mositheorem{lemma}{Lemma}
\mositheorem{corollary}{Corollary}
\mositheorem{proposition}{Proposition}
\theoremstyle{mosidef}
\mositheorem{definition}{Definition}
\mositheorem{assumption}{Assumption}
\theoremstyle{remark}
\mositheorem{remark}{Remark}
% cleveref ships default \cref names for theorem/lemma/corollary/proposition/
% definition/remark, but NOT "assumption" — declare it so \cref prints the word.
\crefname{assumption}{Assumption}{Assumptions}
\Crefname{assumption}{Assumption}{Assumptions}

%%======================================================================
%%  Title block: \title, \author, \abstract, \checkdata
%%======================================================================
\newcommand{\authorfont}{\fontsize{12}{14}\selectfont}
\newcommand\authorlist{}
\newcommand\authorformat[2][]{%
  {\authorfont\bfseries #2\ifstrempty{#1}{}{$^{#1}$}}%
}
\renewcommand\author[2][]{%
  \ifdefempty{\authorlist}
    {\gappto\authorlist{\authorformat[#1]{#2}}}
    {\gappto\authorlist{, \authorformat[#1]{#2}}}%
}

% --- Affiliations + role-symbol legend, printed in the title block UNDER the
%     author row (the reference layout: a centred, non-bold institution list
%     keyed by the author superscripts, then a small centred legend for the
%     role symbols). BOTH are optional -- declare neither and the title block
%     renders exactly as it did before. Usage (in your main .tex preamble):
%
%       \affil[1]{MOSI Intelligence}                 % one per institution; key 1 prints as ^1
%       \authormark{$^{*}$Equal contribution\quad$^{\dagger}$Corresponding author}
%
% Affiliations flow onto a centred line separated by a stretchable space that is
% a legal break point, so a long list wraps cleanly BETWEEN institutions.
\newcommand{\affilfont}{\fontsize{10}{12}\selectfont}
\newcommand\affillist{}
\newcommand\affilformat[2][]{{$^{#1}$#2}}
\newcommand\affil[2][]{%
  \ifdefempty{\affillist}
    {\gappto\affillist{\affilformat[#1]{#2}}}
    {\gappto\affillist{\hskip 1em plus 0.5em\relax \affilformat[#1]{#2}}}%
}

% \authormark{legend} — the small centred line under the affiliations that keys
% the role symbols. Begin each entry with the matching symbol so it lines up with
% the author superscripts, e.g. $^{*}$Equal contribution\quad$^{\dagger}$Corresponding author.
\newcommand{\authormarkfont}{\fontsize{9}{11}\selectfont}
\newcommand\authormarklist{}
\newcommand\authormark[1]{\def\authormarklist{#1}}

% \authornote{text} — an unmarked footnote on the CURRENT page. The house-style
% default for keying role symbols is the centred \authormark legend above; reach
% for \authornote only for an extra bottom-of-page note the legend can't carry
% (e.g. "Work done during an internship at ...") or the conference \thanks style.
% Call it right after \maketitle so the note lands at the bottom of the first
% page; begin the text with the matching symbol, e.g. \authornote{$^{\ddagger}$...}.
% It is a bare \footnotetext (no \footnotemark): \let\thefootnote\relax drops the
% auto-number, and it gets its own hyperref anchor so it does not reuse a body
% footnote's destination (which would print a harmless "duplicate destination"
% warning). The \csname line sets hyperref's internal href macro without
% \makeatletter and is simply unused when hyperref is absent.
\newcommand\authornote[1]{%
  \begingroup
    \let\thefootnote\relax
    \expandafter\def\csname Hy@footnote@currentHref\endcsname{Hfootnote.authnote}%
    \footnotetext{#1}%
  \endgroup
}

% \checkdata[label]{value} — one or more link/info lines under the abstract.
% They render label-flush in the body font (Palatino): a BOLD label, then the
% value right after it (labels are NOT aligned into a column). \cdlabelsep is the
% gap between a label and its value; order the lines by role, not by length.
% A \url{} value shows in the body font too (\urlstyle{same}), not in typewriter.
\newcommand{\checkdatafont}{\fontsize{9.5}{12}\selectfont}
\newlength{\cdlabelsep}\setlength{\cdlabelsep}{0.5em}  % gap between a label and its value
\newcommand\checkdatalist{}
\newcommand\checkdataformat[2][]{%
  {\checkdatafont{\bfseries #1:}\hspace{\cdlabelsep}{\urlstyle{same}#2}}}
\newcommand\checkdata[2][]{%
  \ifdefempty{\checkdatalist}
    {\gappto\checkdatalist{\checkdataformat[#1]{#2}}}
    {\gappto\checkdatalist{\par\checkdataformat[#1]{#2}}}%
}

\newcommand{\abstractinfont}{\fontsize{10}{12}\selectfont}
\renewcommand{\abstract}[1]{\def\abstractlist{{\abstractinfont #1}}}
\newcommand{\titlefont}{\fontsize{18}{20}\selectfont}
\renewcommand{\title}[1]{\newcommand{\titlelist}{\titlefont{\bfseries #1}}}
\newcommand{\abstractfont}{\fontsize{12}{12}\selectfont}
\newcommand{\beginabstract}{\abstractfont{\bfseries \mosiblue{Abstract}\par}}

%%======================================================================
%%  First-page header logo.
%%  Override in your main .tex, e.g.
%%    \renewcommand{\headerlogo}{\includegraphics[height=9mm]{your-logo}}
%%======================================================================
\newcommand{\headerlogo}{%
  \includegraphics[height=9mm]{OpenMOSS.png}\hspace{3mm}\includegraphics[height=9mm]{MOSI.png}%
}
\fancypagestyle{firststyle}{%
  \fancyhead[R]{}%
  \fancyhead[L]{\vskip 6mm \headerlogo}%
}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

%%======================================================================
%%  \maketitle: framed title + gradient abstract box
%%======================================================================
\newcommand{\@toptitlebar}{\mosiblue{\hrule height 2.5pt}\vskip 6mm}
\newcommand{\@bottomtitlebar}{\vskip 5mm \mosiblue{\hrule height 1pt}}

\newcommand{\mymaketitle}{%
  \tcbset{enhanced, left=8mm, right=8mm, top=6mm, bottom=6mm,
          colback=white, colframe=mosibg, boxrule=0.5pt, before skip=0pt,
          grow to left by=1.5pt, grow to right by=1.5pt, arc=2.5mm}
  {%
    \setlength{\parskip}{0mm}
    \centering
    \nohyphens
    {%
      \@toptitlebar
      \titlelist\par
      \@bottomtitlebar
    }
    \vskip 6mm
    \authorlist\par
    \ifdefempty{\affillist}{}{\vskip 2.5mm {\affilfont\affillist\par}}%
    \ifdefempty{\authormarklist}{}{\vskip 1.5mm {\authormarkfont\authormarklist\par}}%
  }
  \vskip 6mm
  \begin{tcolorbox}[
    enhanced,
    arc=12pt,
    boxrule=0pt,
    colback=white,
    left=15pt, right=15pt, top=20pt, bottom=15pt,
    interior style={left color=mosicyan!15, right color=mosisky!5}
  ]
    \setlength{\parindent}{0cm}
    \setlength{\parskip}{0cm}
    \begin{center}
      \beginabstract
      \vskip 3mm
    \end{center}
    \abstractlist\par
    \vskip 3mm
    {%
      \setlength{\parskip}{0cm}
      \ifdefempty{\checkdatalist}{\vspace*{0.65cm}}{\checkdatalist\par}%
    }
  \end{tcolorbox}
  \tcbset{reset}
  \FloatBarrier
  \thispagestyle{firststyle}
}

\if@twocolumn
  \renewcommand{\maketitle}{\twocolumn[\vskip 3mm \mymaketitle \vskip 8mm]}
\else
  \renewcommand{\maketitle}{\mymaketitle \vskip 8mm}
\fi

%%======================================================================
%%  \appendixpage — appendix divider in the reference layout: a page break, then
%%  a large MOSI-blue "Appendix" heading. Call it right after \appendix; the
%%  lettered \section headings (A, B, ...) then follow as usual. The heading is
%%  plain text (not a \section), so it stays unnumbered and does not consume "A".
%%======================================================================
\newcommand{\appendixpagename}{Appendix}
\newcommand{\appendixpagefont}{\fontsize{16}{18}\selectfont}
\newcommand{\appendixpage}{%
  \clearpage
  {\appendixpagefont\mosiblue{\appendixpagename}\par}%
  \vskip 3mm
}

% microtype: the smallcaps tracking feature is pdfTeX-only; under
% xelatex/lualatex (Chinese mode) fall back to plain microtype.
\AtEndOfClass{%
  \RequirePackage{iftex}
  \ifPDFTeX
    \RequirePackage[tracking=smallcaps]{microtype}
  \else
    \RequirePackage{microtype}
  \fi
}

% --- Chinese (xelatex/lualatex + ctex) mode: silence one harmless fontspec warning ---
% No font (fandol, Noto, ...) declares an OpenType script tag literally named
% "CJK", so fontspec emits a "Font ... does not contain requested Script CJK"
% warning for every CJK family ctex sets up. It is purely cosmetic — Chinese
% still typesets correctly. We silence just that one message (fontspec msg
% "no-script") the instant fontspec loads; this must happen BEFORE ctex
% configures the main CJK font, so we hook fontspec's load rather than use
% \AtBeginDocument (which fires too late and misses the main font). pdfTeX /
% English mode never loads fontspec, so this hook simply never fires.
% (\ExplSyntaxOn must wrap \AddToHook from OUTSIDE: the hook body is tokenised
%  when \AddToHook reads it, so ":" and "_" in \msg_redirect_name:nnn need to be
%  letters already at that point — an \ExplSyntaxOn *inside* the body fires too
%  late and the cs name gets mis-split.)
\ExplSyntaxOn
\AddToHook{package/fontspec/after}
  { \msg_redirect_name:nnn { fontspec } { no-script } { none } }
\ExplSyntaxOff
