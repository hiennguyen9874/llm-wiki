%-----------------------------------------------------------------%
%
% The LaTeX Class File of AI Research
%
%-----------------------------------------------------------------%

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{airesearch}
\LoadClassWithOptions{article}

% Layout %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\usepackage{airesearch}

% Section and caption format %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\RequirePackage{titlesec}
\titleformat*{\paragraph}{\bfseries}
\titleformat*{\section}{\Large\bfseries}
\titleformat*{\subsection}{\large\bfseries}
\titleformat*{\subsubsection}{\normalsize\bfseries}
\DeclareTextFontCommand{\textbf}{\bfseries}

\RequirePackage{caption}
\DeclareCaptionLabelSeparator{custom}{}
\DeclareCaptionFormat{custom}{{\sffamily\textbf{#1 #2}} #3}
\captionsetup{singlelinecheck=false,format=custom,labelsep=custom,font=small}
\captionsetup[sub]{singlelinecheck=true,format=custom,labelsep=custom,font=small}

\RenewDocumentCommand{\paragraph}{s o m}{%
  \par\medskip\noindent\textbf{#3}\quad\ignorespaces
}

% First-page header only (Published in XXX) %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\usepackage{fancyhdr}
\pagestyle{plain}     % Other pages keep plain style
\newcommand{\firstpageheader}[1]{%
  \thispagestyle{fancy}%
  \fancyhf{}%
  \fancyhead[L]{\small \rmfamily #1}% choose [L]/[C]/[R] if desired
  \fancyfoot[C]{\thepage}%
}
