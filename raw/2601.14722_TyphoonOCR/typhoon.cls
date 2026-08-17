%%======== Package options and base class ========
\PassOptionsToPackage{table}{xcolor}
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{typhoon}

% Default like NeurIPS: 10pt unless user overrides
\newcommand\typhoon@fontsize{10pt}
\DeclareOption{10pt}{\renewcommand\typhoon@fontsize{10pt}}
\DeclareOption{11pt}{\renewcommand\typhoon@fontsize{11pt}}
\DeclareOption{12pt}{\renewcommand\typhoon@fontsize{12pt}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax

\LoadClass[\typhoon@fontsize]{article}


%%======== Layout & utilities ========
\RequirePackage[top=2.75cm, bottom=2.5cm, left=2.5cm, right=2.5cm, columnsep=0.65cm]{geometry}
\RequirePackage{microtype}   % limited under XeTeX but harmless
\RequirePackage{placeins}
\RequirePackage{hyphenat}
\RequirePackage{setspace}
\RequirePackage{parskip}
\RequirePackage{lipsum}
\RequirePackage{etoolbox}
\RequirePackage{fancyhdr}
\RequirePackage[normalem]{ulem}
\RequirePackage{graphicx}
\RequirePackage{subcaption}
\RequirePackage{booktabs}
\RequirePackage{nicematrix}
\RequirePackage{multirow}
\RequirePackage{bm}
\RequirePackage{needspace}   % for \Needspace used in \citeas
\newcommand{\nm}[1]{#1}

\RequirePackage[most]{tcolorbox}
\definecolor{typhoonbg}{HTML}{e19ec8}
\definecolor{typhoonpurple}{HTML}{726bdf}
\newcommand{\typhoonpurple}[1]{{\bfseries\color[HTML]{726bdf} #1}}

%%======== Hyperlinks & references ========
\RequirePackage{hyperref}
\RequirePackage[noabbrev,nameinlink]{cleveref}
\hypersetup{
  colorlinks,
  linkcolor=typhoonpurple,  
  citecolor=typhoonpurple,
  urlcolor=typhoonpurple
}
\RequirePackage[round]{natbib}
\def\bibfont{\small}

%%======== Bibliography using bibtex ========
\renewcommand{\refname}{References}
\newcommand{\citeas}[1]{\Needspace*{8\baselineskip}\noindent\bibentry{#1}}

%%======== Headings & caption style ========
\newcommand{\sectionfont}{\fontsize{12}{13}\selectfont}
\newcommand{\subsectionfont}{\fontsize{10}{11}\selectfont}

\RequirePackage{titlesec}
\titleformat*{\section}{\sectionfont\Rubik\bfseries\typhoonpurple}
\titleformat*{\subsection}{\subsectionfont\Rubik\bfseries\typhoonpurple}
\titleformat*{\subsubsection}{\subsectionfont\Rubik\bfseries\typhoonpurple}
\titleformat*{\paragraph}{\Rubik\bfseries} 

\RequirePackage{caption}
\DeclareCaptionLabelSeparator{custom}{}
\DeclareCaptionFormat{custom}{{\Rubik\bfseries #1 #2} #3}
\captionsetup{singlelinecheck=true,format=custom,labelsep=custom,font=small}
\captionsetup[sub]{singlelinecheck=true,format=custom,labelsep=custom,font=small}

%%======== Languages & fonts (XeTeX) ========
\RequirePackage{fontspec}
\RequirePackage{polyglossia}
\setmainlanguage{english}
\setotherlanguage{thai}

% Global font features
\defaultfontfeatures{Ligatures=TeX, Scale=MatchUppercase}

% Note: By not setting \setmainfont, fontspec defaults to Latin Modern (standard LaTeX look)

% Thai font binding for proper shaping/line breaking
\newfontfamily\thaifont{Pridi}[
  Path=typhoon/fonts/,
  Script=Thai, Language=Thai,
  UprightFont   = *-ExtraLight,
  BoldFont      = *-Medium,
  ItalicFont    = *-ExtraLight,
  ItalicFeatures={FakeSlant=0.2},
  BoldItalicFont= *-Medium
]

% === Rubik for headings ===
\newfontfamily\Rubik{Rubik}[
  Path=typhoon/fonts/,
  UprightFont     = *-Regular,
  BoldFont        = *-Bold,
  ItalicFont      = *-RegularItalic,
  BoldItalicFont  = *-BoldItalic,
  FontFace = {el}{n}{*-ExtraLight},
  FontFace = {el}{it}{*-ExtraLightItalic},
  FontFace = {l}{n}{*-Light},
  FontFace = {l}{it}{*-LightItalic},
  FontFace = {m}{n}{*-Medium},
  FontFace = {m}{it}{*-MediumItalic},
  FontFace = {sb}{n}{*-SemiBold},
  FontFace = {sb}{it}{*-SemiBoldItalic}
]

% Improve Thai line breaking in XeTeX
\XeTeXlinebreaklocale "th"
\XeTeXlinebreakskip = 0pt plus 1pt

%%======== Table of contents look ========
\RequirePackage[subfigure]{tocloft}
\renewcommand{\cftsecleader}{\cftdotfill{\cftdotsep}}
\renewcommand{\cftsecfont}{\Rubik}
\renewcommand{\cftsecpagefont}{\Rubik\color{typhoonpurple}}
\renewcommand{\cfttoctitlefont}{\Rubik\sectionfont\typhoonpurple}

%%======== Header and Footer ========
\fancypagestyle{firststyle}{
  \fancyhead[R]{}
  \fancyhead[L]{%
    \vskip 6mm
    \includegraphics[height=6mm]{typhoon/typhoon_logo.png}%
  }
}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

%%======== Title box rules ========
\newcommand{\@toptitlebar}{
  \typhoonpurple{\hrule height 2.5pt}
  \vskip 6mm
}
\newcommand{\@bottomtitlebar}{
  \vskip 5mm
  \typhoonpurple{\hrule height 1pt}
}

%%======== Authors, affiliations, infos ========
\newcounter{authorcount}
\renewcommand\addtolist[5][]{%
  \begingroup
    \stepcounter{authorcount}%
    \if\relax#3\relax
      \def\sep{}%
    \else
      \ifnum\value{authorcount}=5
        \def\sep{\\[0.5mm]}%
      \else
        \ifnum\value{authorcount}=10
          \def\sep{\\[-0.2mm]}%
        \else
          \def\sep{#5}%
        \fi
      \fi
    \fi
    \let\protect\@unexpandable@protect
    \xdef#3{\expandafter{#3}\sep #4[#1]{#2}}%
  \endgroup
}

% === People, metadata, title, abstract (Rubik everywhere) ===
\newcommand{\authorfont}{\Rubik\fontseries{m}\fontsize{10}{12}\selectfont}
\newcommand\authorlist{}
\newcommand\authorformat[2][]{\authorfont{#2$^{#1}$}}
\renewcommand\author[2][]{\addtolist[#1]{#2}{\authorlist}{\authorformat}{, }}

\newcommand{\affiliationfont}{\fontsize{10}{12}\selectfont}
\newcommand\affiliationlist{}
\newcommand\affiliationformat[2][]{{\affiliationfont {\Rubik\bfseries $^{#1}$#2}}}
\newcommand\affiliation[2][]{\addtolist[#1]{#2}{\affiliationlist}{\affiliationformat}{, }}

\newcommand{\contributionfont}{\fontsize{10}{12}\selectfont}
\newcommand\contributionlist{}
\newcommand\contributionformat[2][]{{\contributionfont \Rubik $^{#1}$#2}}
\newcommand\contribution[2][]{\addtolist[#1]{#2}{\contributionlist}{\contributionformat}{, }}

\newcommand{\checkdatafont}{\fontsize{7.92}{10}\selectfont}
\newcommand\checkdatalist{}
\newcommand\checkdataformat[2][]{{\small{\checkdatafont\Rubik\bfseries #1:} \Rubik #2}}
\newcommand\checkdata[2][]{\addtolist[#1]{#2}{\checkdatalist}{\checkdataformat}{\par}}

% --- CHANGED: Abstract definition now uses simple passthrough (defaults to body font/size) ---
% Removed \abstractinfont and \Rubik from here.
\renewcommand{\abstract}[1]{\def\abstractlist{#1}}
\newcommand{\email}[1]{\href{mailto:#1}{\texttt{#1}}} % keep teletype for emails

\renewcommand\date[1]{\checkdata[Date]{#1}}
\newcommand\correspondence[1]{\checkdata[Correspondence]{#1}}

\newcommand{\titlefont}{\fontsize{18}{20}\selectfont}
\renewcommand{\title}[1]{%
  \newcommand{\titlelist}{\titlefont{\Rubik\bfseries #1}}%
}

\newcommand{\abstractfont}{\fontsize{12}{12}\selectfont}
\newcommand{\beginabstract}{\abstractfont{\Rubik\bfseries \typhoonpurple{Abstract}\par}}

% Appendix helper: switch to appendix and print a heading
\newcommand{\beginappendix}{%
  \appendix
  \section*{\titlefont\Rubik \typhoonpurple{Appendix}}%
}


%%======== Title block rendering ========
\newcommand{\mymaketitle}{%
  \tcbset{enhanced}
  \tcbset{left=8mm,right=8mm,top=6mm,bottom=6mm}
  \tcbset{colback=white,colframe=typhoonbg,boxrule=0.5pt}
  \tcbset{before skip=0pt,grow to left by=1.5pt,grow to right by=1.5pt,arc=2.5mm}
  {%
    \setlength{\parskip}{0mm}%
    \centering
    \nohyphens
    {%
      \@toptitlebar
      \titlelist\par
      \@bottomtitlebar
    }%
    \vskip 6mm
    \authorlist
    \vskip 3mm
    \affiliationlist\par
    \vskip 3mm
    \contributionlist\par
  }%
  \vskip 6mm

% Abstract box
  \begin{tcolorbox}[
    colback=white,
    colframe=typhoonpurple,
    boxrule=1pt,
    arc=2.5mm,
    left=6mm,right=6mm,top=6mm,bottom=6mm
  ]
  %  \setlength{\parindent}{0cm} % Optional: Standard LaTeX indents abstracts, uncomment if you want flat.
  %  \setlength{\parskip}{0cm}
    \begin{center}
      \beginabstract
      \vskip 3mm
    \end{center}
    \abstractlist\par
    \vskip 3mm
    {%
      \setlength{\parskip}{0cm}%
      \ifdefempty{\checkdatalist}{\vspace*{0.65cm}}{\checkdatalist\par}%
    }%
  \end{tcolorbox}
  \tcbset{reset}
  \FloatBarrier
  \thispagestyle{firststyle}
}

%%======== MakeTitle wrapper (one/two column) ========
\if@twocolumn
  \renewcommand{\maketitle}{%
    \twocolumn[%
      \vskip 3mm
      \mymaketitle
      \vskip 8mm
    ]%
  }%
\else
  \renewcommand{\maketitle}{%
    \mymaketitle
    \vskip 8mm
  }%
\fi