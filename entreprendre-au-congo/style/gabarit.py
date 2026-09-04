#!/usr/bin/env python3
"""Le gabarit typographique de la phase 1, et sa conversion depuis le manuscrit.

Le cahier des charges fixe trois cibles pour la phase 1 qui, prises ensemble,
sont incompatibles en A5 : justification de 100 à 105 mm, marges de 20 mm en
gouttière et 15 mm en extérieure, et 60 à 66 signes par ligne. Or 148 − 20 − 15
donne 113 mm, soit la justification actuelle : ces marges ne corrigent pas le
défaut B3, elles le reconduisent.

Le critère maître retenu est le compte de signes, les millimètres en découlent.
D'où la géométrie ci-dessous : 24 mm de gouttière et 19 mm en extérieure donnent
105 mm de justification, en conservant la gouttière plus large que la marge
extérieure — le seul point de gabarit que l'audit portait au crédit du fichier
d'origine.

Le corps varie d'une police à l'autre, comme le cahier l'admet : la chasse d'EB
Garamond n'est pas celle de Source Serif Pro, et c'est le compte de signes qui
doit tomber juste, non le corps.
"""

GEOMETRIE = {
    "format": ("148mm", "210mm"),
    "gouttiere": 24, "exterieure": 19, "tete": 16, "pied": 20,
    "justification": 105,          # 148 − 24 − 19
}

POLICES = {
    "garamond": {
        "nom": "EB Garamond",
        # La fonte grasse du paquet Debian ne pèse que 43 Ko contre 422 pour la
        # romaine : c'est un tronçon sans lettres accentuées, inutilisable pour un
        # livre français. Celle de TeX Live est complète.
        "chemin": "/usr/share/texlive/texmf-dist/fonts/opentype/public/ebgaramond/",
        "romain": "EBGaramond-Regular.otf",
        "italique": "EBGaramond-Italic.otf",
        "gras": "EBGaramond-Bold.otf",
        # Corps accordés par qa/accorder-corps.py sur la cible de 60 à 66 signes
        # par ligne pleine, à 105 mm de justification. Interlignage à 1,30 fois
        # le corps pour les trois, sans quoi la comparaison ne serait pas juste.
        "corps": 12.75, "interlignage": 16.6,
    },
    "libertinus": {
        "nom": "Libertinus Serif",
        "chemin": "/usr/share/texlive/texmf-dist/fonts/opentype/public/libertinus-fonts/",
        "romain": "LibertinusSerif-Regular.otf",
        "italique": "LibertinusSerif-Italic.otf",
        "gras": "LibertinusSerif-Bold.otf",
        "corps": 11.75, "interlignage": 15.3,
    },
    "sourceserif": {
        "nom": "Source Serif Pro",
        "chemin": "/usr/share/texlive/texmf-dist/fonts/opentype/adobe/sourceserifpro/",
        "romain": "SourceSerifPro-Regular.otf",
        "italique": "SourceSerifPro-RegularIt.otf",
        "gras": "SourceSerifPro-Bold.otf",
        "corps": 10.75, "interlignage": 14.0,
    },
}

PREAMBULE = r"""\documentclass[11pt,twoside]{memoir}

%% --- Gabarit ---------------------------------------------------------------
\setstocksize{@hauteur@}{@largeur@}
\settrimmedsize{\stockheight}{\stockwidth}{*}
\settypeblocksize{@bloc@mm}{@justification@mm}{*}
\setlrmargins{@gouttiere@mm}{*}{*}
\setulmargins{@tete@mm}{*}{*}
\setheadfoot{\onelineskip}{2\onelineskip}
\setheaderspaces{*}{1.5\onelineskip}{*}
\checkandfixthelayout

%% --- Polices ---------------------------------------------------------------
\usepackage{fontspec}
\setmainfont{@romain@}[
  Path         = @chemin@ ,
  ItalicFont   = @italique@ ,
  BoldFont     = @gras@ ,
  Ligatures    = TeX ,
  Scale        = @echelle@ ,
]
\linespread{@linespread@}

%% --- Langue et césure ------------------------------------------------------
\usepackage[french]{babel}
\frenchsetup{ThinSpaceInFrenchNumbers=true}

%% Pénalités de césure demandées par le cahier des charges : pas de césure en
%% dernière ligne de paragraphe, pas de césure d'un recto à un verso, et deux
%% césures consécutives fortement découragées.
\finalhyphendemerits=10000
\brokenpenalty=10000
\doublehyphendemerits=10000
%% Deux lettres avant la coupure, trois après : l'usage français, que
%% babel-french pose lui-même. Exiger trois des deux côtés, comme on le fait en
%% anglais, étouffe la césure — et c'est précisément ce que la mesure a montré.
\lefthyphenmin=2
\righthyphenmin=3

%% --- Microtypographie ------------------------------------------------------
%% XeLaTeX ne fait que la protrusion ; LuaLaTeX fait aussi l'expansion, ce qui
%% resserre la justification sans écarter les mots. C'est la seconde moitié de
%% la correction du défaut B1.
\usepackage[protrusion=true,expansion=true,final]{microtype}

%% --- Encadré « Réalité congolaise » ----------------------------------------
%% Composé comme dans le livre : corps réduit, retrait des deux côtés, titre en
%% gras. Les filets sont provisoires — la phase 4 arrêtera la forme définitive.
\usepackage{xcolor}
\definecolor{filet}{gray}{0.55}
\newenvironment{encadre}[1]{%
  \par\addvspace{\onelineskip}%
  \begingroup
  \leftskip=5mm \rightskip=5mm
  {\color{filet}\hrule height 0.4pt}%
  \vspace{0.6\onelineskip}%
  \small
  \noindent\textbf{#1}\par\nobreak\vspace{0.3\onelineskip}%
}{%
  \par\vspace{0.6\onelineskip}%
  {\color{filet}\hrule height 0.4pt}%
  \endgroup
  \par\addvspace{\onelineskip}%
}

%% --- Titres ----------------------------------------------------------------
\setsecheadstyle{\normalfont\bfseries\large\raggedright}
\setbeforesecskip{1.6\onelineskip plus 0.3\onelineskip minus 0.2\onelineskip}
\setaftersecskip{0.5\onelineskip}

%% --- Titres courants -------------------------------------------------------
\makepagestyle{livre}
\makeevenhead{livre}{\small\textsc{Entreprendre au Congo}}{}{}
\makeoddhead{livre}{}{}{\small\textsc{@courant@}}
\makeevenfoot{livre}{\small\thepage}{}{}
\makeoddfoot{livre}{}{}{\small\thepage}
\pagestyle{livre}

\setlength{\parindent}{0pt}
\setlength{\parskip}{0.55\onelineskip}
\raggedbottom

\begin{document}
\setcounter{page}{18}
"""
