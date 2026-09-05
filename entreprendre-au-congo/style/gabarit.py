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

%% Les trois schémas sont dessinés avec les demi-graphiques d'Unicode (U+2500 et
%% suivants). Latin Modern Mono ne les porte pas : LuaLaTeX n'en disait rien
%% d'autre qu'un « Missing character » dans son journal, et les traits du dessin
%% s'imprimaient en blanc. DejaVu Sans Mono les porte tous. Le corps est fixé
%% ici, une fois, pour les trois : à 9 points, la plus large des trois lignes
%% — quarante-neuf signes — tient dans la justification sans être réduite, et
%% les trois schémas s'impriment donc à la même échelle.
\setmonofont{DejaVu Sans Mono}[Scale=1.0]
\newcommand{\corpsschema}{\fontsize{9}{11}\selectfont}

%% --- Langue et césure ------------------------------------------------------
\usepackage[french]{babel}
%% La source porte elle-même ses espaces insécables depuis la phase 2 : le
%% manuscrit est correct hors de toute chaîne, et l'EPUB, qui n'a pas de
%% babel, en profite autant que le PDF. Il faut donc empêcher babel d'en
%% poser une seconde par-dessus, sans quoi la ponctuation haute s'écarterait
%% du double.
\frenchsetup{AutoSpacePunctuation=false, ThinSpaceInFrenchNumbers=false}

%% Pénalités de césure demandées par le cahier des charges : pas de césure en
%% dernière ligne de paragraphe, pas de césure d'un recto à un verso, et deux
%% césures consécutives fortement découragées.
\finalhyphendemerits=10000
\brokenpenalty=10000
\doublehyphendemerits=900000
%% Deux césures consécutives sont fortement pénalisées : c'est ce qui empêche
%% qu'il s'en aligne trois, faute de paramètre TeX qui les plafonne directement.
%% Deux lettres avant la coupure, trois après : l'usage français, que
%% babel-french pose lui-même. Exiger trois des deux côtés, comme on le fait en
%% anglais, étouffe la césure — et c'est précisément ce que la mesure a montré.
\lefthyphenmin=2
\righthyphenmin=3

%% Veuves et orphelines : interdites, non découragées. Une ligne seule en tête
%% ou en pied de page est un défaut de composition, pas un compromis.
\clubpenalty=10000
\widowpenalty=10000
\displaywidowpenalty=10000

%% Les listes échappent à \clubpenalty : celui-ci retient la deuxième ligne d'un
%% paragraphe, pas le deuxième article d'une énumération. Une rubrique « Ce qu'il
%% faut retenir » pouvait donc s'ouvrir en pied de page sur un seul article, le
%% reste passant à la page suivante. Rien ne s'ouvre plus au ras d'une liste, et
%% une coupure entre deux articles est désormais payante sans être interdite —
%% l'interdire rejetterait des listes entières et creuserait les pages.
\makeatletter
\@beginparpenalty=-51
\@itempenalty=500
\makeatother

%% Le seuil de mauvaisité annoncé : au-delà de 1000, une ligne est visiblement
%% lâche. LaTeX consigne alors un avertissement, que qa/mesurer-composition.py
%% relève et dénombre.
\hbadness=1000
\vbadness=1000
\hfuzz=0.1pt

%% Une réserve d'élasticité en dernier recours : plutôt que de laisser une ligne
%% déborder la justification, TeX peut relâcher un peu l'espacement d'un
%% paragraphe entier. Sans elle, une poignée de lignes sortent de la mesure.
\emergencystretch=2em

%% --- Microtypographie ------------------------------------------------------
%% XeLaTeX ne fait que la protrusion ; LuaLaTeX fait aussi l'expansion, ce qui
%% resserre la justification sans écarter les mots. C'est la seconde moitié de
%% la correction du défaut B1.
\usepackage[protrusion=true,expansion=true,final]{microtype}

%% --- Encadrés --------------------------------------------------------------
%% Le livre en compte trois sortes, et elles reviennent : « Réalité congolaise »
%% quinze fois, « À faire cette semaine » quinze fois, l'aparté dix-sept fois.
%% Phase 4 : leur forme est arrêtée ici, une fois, et ne varie plus d'une
%% occurrence à l'autre. Géométrie commune — même retrait des deux côtés, même
%% corps, même respiration avant et après, titre en gras — et un seul signe
%% distinctif, le filet, pour que le lecteur reconnaisse la sorte sans que la
%% page change de texture. Les deux rubriques récurrentes sont encadrées de
%% filets ; l'aparté, qui est une digression et non une rubrique, n'en porte
%% pas. Un aparté sans titre — il y en a trois — n'ouvre pas de ligne vide.
\usepackage{xcolor}
\definecolor{filet}{gray}{0.55}

\newlength{\retraitencadre}
\setlength{\retraitencadre}{5mm}
\newcommand{\filetencadre}{{\color{filet}\hrule height 0.4pt}}
\def\encadreaparte{aparte}

%% #1 : la sorte — realite-congolaise, a-faire, aparte. #2 : le titre, vide pour
%% un aparté qui n'en porte pas. Le titre est confronté à \empty par \ifx, qui
%% compare des listes de lexèmes : il n'est donc jamais développé, et un titre
%% portant des guillemets ou une commande traverse intact.
\newenvironment{encadre}[2]{%
  \par\addvspace{\onelineskip}%
  %% Un encadré ne s'ouvre pas au ras du pied de page : son filet de tête est
  %% resté seul en bas d'une page, la suite passant à la page d'après. Quatre
  %% lignes disponibles, et rien ne se coupe entre le filet, le titre et la
  %% première ligne — les \nobreak s'en chargent.
  \Needspace*{4\baselineskip}%
  \begingroup
  \def\sorteencadre{#1}%
  \def\titreencadre{#2}%
  \leftskip=\retraitencadre \rightskip=\retraitencadre
  %% L'encadré compose sur une mesure plus étroite : ce qui passe dans le corps
  %% peut y déborder. Une réserve d'élasticité plus large lui est propre.
  \emergencystretch=3em
  \ifx\sorteencadre\encadreaparte\else
    \filetencadre\nobreak\vskip 0.6\onelineskip
  \fi
  \small
  \ifx\titreencadre\empty\else
    \noindent\textbf{#2}\par\nobreak\vskip 0.3\onelineskip
  \fi
  \nobreak
}{%
  \par
  \ifx\sorteencadre\encadreaparte\else
    %% Et le filet de pied ne se sépare pas de la dernière ligne qu'il ferme.
    \nobreak\vskip 0.6\onelineskip\nobreak\filetencadre
  \fi
  \endgroup
  \par\addvspace{\onelineskip}%
}

%% Une rubrique ne s'ouvre pas au ras du pied de page. \clubpenalty retient la
%% deuxième ligne d'un paragraphe, mais pas le deuxième article d'une liste : un
%% « Ce qu'il faut retenir » pouvait donc s'imprimer suivi d'un seul article, le
%% reste passant à la page suivante. On exige quatre lignes disponibles sous le
%% titre — le titre, et de quoi commencer vraiment.
\usepackage{needspace}
\newcommand{\placedutitre}{\Needspace*{4\baselineskip}}

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

%% Ligne de régie du spécimen, hors du bloc de texte : elle nomme ce que la
%% double page donne à juger. Elle n'appartient pas au livre.
\makeoddfoot{livre}{}{\scriptsize\color{filet}@regie@}{\small\thepage}
\makeevenfoot{livre}{\small\thepage}{\scriptsize\color{filet}@regie@}{}

\setlength{\parindent}{0pt}
\setlength{\parskip}{0.55\onelineskip}
\raggedbottom

\begin{document}
\setcounter{page}{18}
"""
