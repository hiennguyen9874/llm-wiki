
%
%

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{bytedance_seed}
\LoadClassWithOptions{article}
\pdfoutput=1

\newif\ifseedtwocolumnlayout
\if@twocolumn
  \seedtwocolumnlayouttrue
\else
  \seedtwocolumnlayoutfalse
\fi

%
\RequirePackage[top=2.75cm, bottom=2.5cm, left=2.5cm, right=2.5cm, columnsep=0.65cm]{geometry}
\RequirePackage{microtype}
\RequirePackage{placeins}
\RequirePackage{hyphenat}
\RequirePackage{setspace}
\RequirePackage{parskip}
\RequirePackage[latin, english]{babel}
\RequirePackage{lipsum}
\RequirePackage{etoolbox}
\RequirePackage{fancyhdr}  %
\setlength{\headheight}{35pt}
\RequirePackage{ulem}  %
\DisableLigatures[f]{family=sf*} 
\RequirePackage{graphicx}
\RequirePackage{subcaption}


\RequirePackage{booktabs}
\RequirePackage{nicematrix}
\RequirePackage{multirow}
\RequirePackage{bm}
\newcommand{\nm}[1]{#1}
\RequirePackage[most]{tcolorbox}
\RequirePackage{xcolor}
\definecolor{seedbg}{HTML}{2E5AA8}
\definecolor{seedblue}{HTML}{2E5AA8}
\newcommand{\seedblue}[1]{{\bfseries\color[HTML]{2E5AA8} #1}} 

%

\RequirePackage{hyperref}
\RequirePackage[noabbrev,nameinlink]{cleveref}
\hypersetup{
  colorlinks,
  linkcolor=seedblue,
  citecolor=seedblue,
  urlcolor=seedblue
}



\RequirePackage[numbers, sort&compress]{natbib}
%
\def\bibfont{\small}

%
\addto{\captionsenglish}{\renewcommand{\refname}{References}}
\newcommand{\citeas}[1]{\Needspace*{8\baselineskip}\noindent\bibentry{#1}}



%
\newcommand{\sectionfont}
{\fontsize{12}{10}\selectfont} 

\newcommand{\subsectionfont}
{\fontsize{11}{10}\selectfont} 

\RequirePackage{titlesec}
\titleformat*{\paragraph}{\itshape}
\titleformat*{\section}{\sectionfont\sffamily\bfseries\seedblue}
\titleformat*{\subsection}{\subsectionfont\sffamily\bfseries\seedblue}


%
\titleformat*{\subsubsection}{\normalsize\sffamily\bfseries\seedblue}


\newcommand{\bffont}
{\fontsize{8.8}{10}\selectfont} 

\DeclareTextFontCommand{\textbf}{\bffont\bfseries\sffamily}



\RequirePackage{caption}
\DeclareCaptionLabelSeparator{custom}{}
\DeclareCaptionFormat{custom}{{\sffamily\textbf{#1 #2}} #3}
\captionsetup{singlelinecheck=true,format=custom,labelsep=custom,font=small}
\captionsetup[sub]{singlelinecheck=true,format=custom,labelsep=custom,font=small}


\RequirePackage[T1]{fontenc}
\DeclareFontFamily{T1}{bytesans}{}
\DeclareFontShape{T1}{bytesans}{m}{n}{<-> s * [1] seed/bytesans}{}
\DeclareFontShape{T1}{bytesans}{b}{n}{<-> s * [1] seed/bytesans}{}
\DeclareFontShape{T1}{bytesans}{m}{it}{<-> s * [1] seed/bytesans}{}
\DeclareFontShape{T1}{bytesans}{b}{it}{<-> s * [1] seed/bytesans}{}
\pdfmapline{+bytesans < seed/ByteSans-Bold.ttf <T1-WGL4.enc}
\renewcommand{\sfdefault}{bytesans}%


\DeclareFontFamily{T1}{bytesansmedium}{}
\DeclareFontShape{T1}{bytesansmedium}{m}{n}{<-> s*[1] seed/bytesansmedium}{}
\DeclareFontShape{T1}{bytesansmedium}{b}{n}{<-> s*[1] seed/bytesansmedium}{}
\DeclareFontShape{T1}{bytesansmedium}{m}{it}{<-> s*[1] seed/bytesansmedium}{}
\DeclareFontShape{T1}{bytesansmedium}{b}{it}{<-> s*[1] seed/bytesansmedium}{}
\pdfmapline{+bytesansmedium < seed/ByteSans-Medium.ttf <T1-WGL4.enc}
%
\renewcommand{\rmdefault}{cmr}

%

%

\renewcommand\addtolist[5][]{
  \begingroup
    \if\relax#3\relax\def\sep{}\else\def\sep{#5}\fi
    \let\protect\@unexpandable@protect 
    \xdef#3{\expandafter{#3}\sep #4[#1]{#2}}%
  \endgroup
}

\newcommand{\authorfont}
{\fontsize{12}{14}\selectfont} 

\newcommand\authorlist{}
\newcommand\authorformat[2][]{\authorfont {\sffamily #2$^{#1}$}}
\renewcommand\author[2][]{\addtolist[#1]{#2}{\authorlist}{\authorformat}{, }}

%

\newcommand{\affiliationfont}
{\fontsize{10}{12}\selectfont}

\newcommand\affiliationlist{}
\newcommand\affiliationformat[2][]{{\affiliationfont {\fontfamily{bytesansmedium}\selectfont $^{#1}$#2}}}
\newcommand\affiliation[2][]{\addtolist[#1]{#2}{\affiliationlist}{\affiliationformat}{, }}

\newcommand{\contributionfont}
{\fontsize{10}{12}\selectfont}

\newcommand\contributionlist{}
\newcommand\contributionformat[2][]{{\contributionfont $^{#1}$#2}}
\newcommand\contribution[2][]{\addtolist[#1]{#2}{\contributionlist}{\contributionformat}{, }}

\newcommand{\checkdatafont}
{\fontsize{7.92}{10}\selectfont}

\newcommand\checkdatalist{}
\newcommand\checkdataformat[2][]{{\small {\checkdatafont\sffamily \bfseries #1:} #2}}
\newcommand\checkdata[2][]{\addtolist[#1]{#2}{\checkdatalist}{\checkdataformat}{\par}}


\newcommand{\abstractinfont}
{\fontsize{10}{12}\selectfont} 

\renewcommand{\abstract}[1]{\def\abstractlist{{\abstractinfont #1}}}
\newcommand{\email}[1]{\href{mailto:#1}{\texttt{#1}}}

\renewcommand\date[1]{\checkdata[Date]{#1}}
\newcommand\correspondence[1]{\checkdata[Correspondence]{#1}}


\newcommand{\titlefont}
{\fontsize{17}{20}\selectfont} 

\renewcommand{\title}[1]{\newcommand{\titlelist}{\titlefont{\sffamily #1}}}


\newcommand{\abstractfont}
{\fontsize{12}{12}\selectfont} 

\newcommand{\beginabstract}{\abstractfont{\sffamily\bfseries \seedblue{Abstract}\par}}

\newcommand{\beginappendix}{%
  \clearpage
  \appendix
  {\titlefont\sffamily \seedblue{Appendix}\par}
  \vskip 4mm
}


\usepackage[subfigure]{tocloft}
\renewcommand{\cftsecleader}{\cftdotfill{\cftdotsep}} %
\renewcommand{\cftsecfont}{\sffamily}
%
\renewcommand{\cftsecpagefont}{\sffamily}{\color{seedblue}}
\renewcommand{\cfttoctitlefont}
{\sffamily\sectionfont\seedblue}


%
\fancypagestyle{firststyle}{
    \fancyhf{} %
    
    %
    \fancyhead[L]{
        %
        \includegraphics[height=8mm, keepaspectratio]{seed/seed_logo.png}
    }

    \fancyhead[R]{}
    
    %
    \renewcommand{\headrulewidth}{0pt} %
}


%
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}



%
%
%
\newcommand{\@toptitlebar}{
  \seedblue{\hrule height 0.5pt }
  \vskip 6mm
  %
}
\newcommand{\@bottomtitlebar}{
  \vskip 6mm
  %
  \seedblue{\hrule height 0.5pt}
  %
}


%


\newcommand{\mymaketitle}{%
  %
  \tcbset{enhanced}
  \tcbset{left=8mm}
  \tcbset{right=8mm}
  \tcbset{top=6mm}
  \tcbset{bottom=6mm}
  \tcbset{colback=white}  
   %
  \tcbset{colframe=seedbg} 
  %
  \tcbset{boxrule=0.5pt} 
  \tcbset{before skip=0pt}
  \tcbset{grow to left by=1.5pt}
  \tcbset{grow to right by=1.5pt}
  \tcbset{arc=2.5mm}
      {
      \setlength{\parskip}{0mm}
      \centering
      \nohyphens
      %
      
      {
      \@toptitlebar
        
        \titlelist\par
         \@bottomtitlebar
      }
      \vskip 6mm
      \authorlist
      \vskip 3mm
      %
      \affiliationlist\par
      \vskip 3mm
      %
      \contributionlist\par
    }
   \vskip 6mm   
   
  \begin{tcolorbox}
    \setlength{\parindent}{0cm}
    \setlength{\parskip}{0cm}

    %
    
    \begin{center}
        \beginabstract
        \vskip 3mm
    \end{center}
    
    \abstractlist\par
    %
    \vskip 3mm
    %
    {
      \setlength{\parskip}{0cm}
      \ifdefempty{\checkdatalist}{\vspace*{0.65cm}}{\checkdatalist\par}
    }
  \end{tcolorbox}
  \tcbset{reset}
  \FloatBarrier

  %
  \thispagestyle{firststyle}

}


\if@twocolumn%
\renewcommand{\maketitle}{
\twocolumn[%
 \vskip 3mm
  \mymaketitle
  \vskip 8mm
]
}%
\else%
\renewcommand{\maketitle}{
  \mymaketitle
  \vskip 8mm
  %
}%
\fi
