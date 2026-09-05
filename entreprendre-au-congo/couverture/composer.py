#!/usr/bin/env python3
"""Quatre propositions de première de couverture — phase 1, en parallèle.

Cadre arrêté avec l'auteure : 148 × 210 mm, fond perdu de 3 mm, première de
couverture seule. Le dos et la quatrième attendent que D5 fixe la pagination
définitive, dont dépend l'épaisseur du dos.

Quatre partis pris distincts, non quatre variantes d'une même idée :

    A  typographique pure     ni couleur ni filet ; la seule échelle des corps
    B  bloc de couleur        un aplat qui porte le titre
    C  centrée classique      symétrie, filets, air ; la couverture de librairie
    D  asymétrique            fer à gauche, tension, grande réserve à droite

Aucune illustration, aucune photographie.

    E  collection             aplat pleine page, bandeau horizontal, titre en
                             réserve dans le bandeau, autrice en pied. Parti pris
                             commercial et non littéraire, à comparer aux autres.

LA POLICE N'EST PAS LA MÊME PARTOUT, et c'est délibéré. D3 a retenu Source Serif
Pro pour le texte courant ; rien n'oblige la couverture à la reprendre. Chaque
proposition emploie donc la police que son parti pris demande, et le rapport dit
laquelle et pourquoi :

    A  Source Serif Pro   continuité avec le livre : la couverture annonce la
                          voix du texte, sans rupture
    B  Source Sans Pro    des capitales en réserve sur un aplat exigent un dessin
                          ouvert et régulier, que l'encre ne referme pas
    C  Libertinus Serif   la composition classique appelle une serif de tradition,
                          plus ancienne d'esprit que celle du livre
    D  Source Sans Pro    un axe décalé tient mieux avec un dessin neutre, qui ne
                          concurrence pas la composition
    E  Source Sans Pro    le bandeau réclame de la graisse et une lisibilité
                          immédiate en vignette
"""
import argparse
import subprocess
from pathlib import Path

TITRE = "ENTREPRENDRE AU CONGO"
SOUS_TITRE = "Comprendre l’entrepreneuriat et savoir par où commencer"
AUTRICE = "Par Ruth ZADI Pukuta"

FOND_PERDU = 3          # mm
LARGEUR, HAUTEUR = 148, 210
SANS = "/usr/share/texlive/texmf-dist/fonts/opentype/adobe/sourcesanspro/"
SERIF = "/usr/share/texlive/texmf-dist/fonts/opentype/adobe/sourceserifpro/"
LIBERTINUS = "/usr/share/texlive/texmf-dist/fonts/opentype/public/libertinus-fonts/"

# La police de chaque proposition, et la raison de ce choix.
POLICES = {
    "A-typographique": ("Source Serif Pro", SERIF, "SourceSerifPro-Regular.otf",
                        "SourceSerifPro-RegularIt.otf", "SourceSerifPro-Bold.otf",
                        "SourceSerifPro-Light.otf", "SourceSerifPro-Semibold.otf"),
    "B-bloc-couleur": ("Source Sans Pro", SANS, "SourceSansPro-Regular.otf",
                       "SourceSansPro-RegularIt.otf", "SourceSansPro-Bold.otf",
                       "SourceSansPro-Light.otf", "SourceSansPro-Semibold.otf"),
    "C-centree": ("Libertinus Serif", LIBERTINUS, "LibertinusSerif-Regular.otf",
                  "LibertinusSerif-Italic.otf", "LibertinusSerif-Bold.otf",
                  "LibertinusSerif-Regular.otf", "LibertinusSerif-Semibold.otf"),
    "D-asymetrique": ("Source Sans Pro", SANS, "SourceSansPro-Regular.otf",
                      "SourceSansPro-RegularIt.otf", "SourceSansPro-Bold.otf",
                      "SourceSansPro-Light.otf", "SourceSansPro-Semibold.otf"),
    "E-collection": ("Source Sans Pro", SANS, "SourceSansPro-Regular.otf",
                     "SourceSansPro-RegularIt.otf", "SourceSansPro-Bold.otf",
                     "SourceSansPro-Light.otf", "SourceSansPro-Semibold.otf"),
}

PREAMBULE = r"""\documentclass{article}
\usepackage[paperwidth=@pw@mm,paperheight=@ph@mm,margin=0pt]{geometry}
\usepackage{fontspec}
\usepackage{tikz}
\usetikzlibrary{calc}
\usepackage[french]{babel}
\pagestyle{empty}
\setmainfont{@romain@}[
  Path       = @chemin@ ,
  ItalicFont = @italique@ ,
  BoldFont   = @gras@ ,
  FontFace   = {l}{n}{@maigre@} ,
  FontFace   = {sb}{n}{@demi@} ,
  Ligatures  = TeX ,
]
\newcommand{\maigre}{\fontseries{l}\selectfont}
\newcommand{\demi}{\fontseries{sb}\selectfont}

%% Encre : un noir de labeur, jamais le noir pur de l'écran, et un ocre sourd.
%% Les couleurs sont posées en quadrichromie, jamais en RVB : un fichier
%% d'impression ne contient pas de couleur d'écran. L'encre est du noir seul,
%% cent pour cent de noir et rien d'autre — c'est ce que le contrôle vérifie.
%% Le papier est l'absence d'encre : la teinte du fond est celle du support,
%% elle ne s'imprime pas.
\definecolor{encre}{cmyk}{0,0,0,1}
\definecolor{ocre}{cmyk}{0,0.57,0.81,0.36}
\definecolor{papier}{cmyk}{0,0,0,0}

%% Le fond perdu déborde de @fp@ mm sur les quatre côtés ; la coupe tombe sur le
%% rectangle intérieur. Le TrimBox le déclare pour l'imprimeur.
\directlua{pdf.setpageattributes("/TrimBox [@t0@ @t0@ @tx@ @ty@]")}

\begin{document}
\begin{tikzpicture}[remember picture,overlay]
  \coordinate (coin) at (current page.south west);
  \coordinate (coupe0) at ($(coin)+(@fp@mm,@fp@mm)$);
  \coordinate (coupe1) at ($(coin)+(@bw@mm,@bh@mm)$);
"""

FIN = r"""\end{tikzpicture}
\end{document}
"""

# Les quatre partis pris. Chacun ne pose que son propre décor : le cadre et les
# repères de coupe sont communs et posés par le préambule.
PARTIS = {
"A-typographique": r"""
  \fill[papier] (coin) rectangle ($(coin)+(@pw@mm,@ph@mm)$);
  %% Rien que du texte : trois corps, trois graisses, un seul alignement. Le blanc
  %% est réparti, non rejeté en bas — c'est lui qui fait la tenue de la page.
  \node[anchor=north west, text width=112mm, align=left, inner sep=0pt]
    at ($(coupe0)+(18mm,180mm)$) {%
      \color{encre}\maigre\fontsize{14}{18}\selectfont Par Ruth ZADI Pukuta};
  \node[anchor=north west, text width=118mm, align=left, inner sep=0pt]
    at ($(coupe0)+(18mm,132mm)$) {%
      %% L'interlignage d'un nœud TikZ ne suit pas toujours \fontsize : les deux
      %% lignes du titre se touchaient presque. L'écart est donc posé en
      %% millimètres, où il se mesure.
      \color{encre}\demi\fontsize{39}{46}\selectfont ENTREPRENDRE\\[5mm] AU\hspace{0.30em}CONGO};
  \node[anchor=north west, text width=100mm, align=left, inner sep=0pt]
    at ($(coupe0)+(18mm,62mm)$) {%
      \color{encre}\maigre\fontsize{13.5}{19}\selectfont Comprendre
      l’entrepreneuriat\\ et savoir par où commencer};
""",
"B-bloc-couleur": r"""
  \fill[papier] (coin) rectangle ($(coin)+(@pw@mm,@ph@mm)$);
  %% L'aplat doit être coupé, donc couvrir le fond perdu jusqu'au bord de page.
  \fill[ocre] ($(coin)+(0mm,@ph@mm)$) rectangle ($(coin)+(@pw@mm,@ph@mm-107mm)$);
  \node[anchor=north west, text width=118mm, align=left, inner sep=0pt]
    at ($(coupe0)+(16mm,182mm)$) {%
      \color{papier}\demi\fontsize{38}{42}\selectfont ENTREPRENDRE\\[1mm] AU\hspace{0.30em}CONGO};
  \node[anchor=north west, text width=116mm, align=left, inner sep=0pt]
    at ($(coupe0)+(16mm,86mm)$) {%
      \color{encre}\fontsize{13.5}{19}\selectfont Comprendre l’entrepreneuriat\\
      et savoir par où commencer};
  \node[anchor=south west, inner sep=0pt] at ($(coupe0)+(16mm,20mm)$) {%
      \color{encre}\demi\fontsize{13}{16}\selectfont Par Ruth ZADI Pukuta};
""",
"C-centree": r"""
  \fill[papier] (coin) rectangle ($(coin)+(@pw@mm,@ph@mm)$);
  %% Symétrie stricte, filets fins, beaucoup d'air : la couverture de librairie.
  \draw[encre,line width=0.4pt] ($(coupe0)+(24mm,178mm)$) -- ($(coupe0)+(124mm,178mm)$);
  \node[anchor=north, text width=112mm, align=center, inner sep=0pt]
    at ($(coupe0)+(74mm,168mm)$) {%
      \color{encre}\fontsize{11}{15}\selectfont Par Ruth ZADI Pukuta};
  \node[anchor=north, text width=124mm, align=center, inner sep=0pt]
    at ($(coupe0)+(74mm,132mm)$) {%
      \color{encre}\demi\fontsize{31}{43}\selectfont ENTREPRENDRE\\ AU\hspace{0.30em}CONGO};
  \draw[encre,line width=0.4pt] ($(coupe0)+(52mm,84mm)$) -- ($(coupe0)+(96mm,84mm)$);
  \node[anchor=north, text width=108mm, align=center, inner sep=0pt]
    at ($(coupe0)+(74mm,74mm)$) {%
      \color{encre}\maigre\fontsize{12.5}{18}\selectfont Comprendre l’entrepreneuriat\\
      et savoir par où commencer};
  \draw[encre,line width=0.4pt] ($(coupe0)+(24mm,26mm)$) -- ($(coupe0)+(124mm,26mm)$);
""",
"D-asymetrique": r"""
  \fill[papier] (coin) rectangle ($(coin)+(@pw@mm,@ph@mm)$);
  %% Une barre pleine hauteur au bord gauche, coupée en tête et en pied, et tout
  %% le texte serré sur un axe décalé : la réserve de droite fait la composition.
  \fill[ocre] (coin) rectangle ($(coin)+(9mm,@ph@mm)$);
  \node[anchor=north west, text width=96mm, align=left, inner sep=0pt]
    at ($(coupe0)+(26mm,176mm)$) {%
      \color{encre}\demi\fontsize{27}{35}\selectfont ENTREPRENDRE\\ AU\hspace{0.30em}CONGO};
  \draw[ocre,line width=1.2pt] ($(coupe0)+(26mm,104mm)$) -- ($(coupe0)+(46mm,104mm)$);
  \node[anchor=north west, text width=82mm, align=left, inner sep=0pt]
    at ($(coupe0)+(26mm,94mm)$) {%
      \color{encre}\maigre\fontsize{12.5}{18}\selectfont Comprendre l’entrepreneuriat\\
      et savoir par où commencer};
  \node[anchor=south west, inner sep=0pt] at ($(coupe0)+(26mm,22mm)$) {%
      \color{encre}\demi\fontsize{12}{15}\selectfont Par Ruth ZADI Pukuta};
""",
"E-collection": r"""
  %% Aplat pleine page, coupé sur les quatre bords. Un bandeau clair le traverse ;
  %% le titre s'y détient en réserve. Parti pris de collection : la couverture se
  %% reconnaît de loin et en vignette, avant même d'être lue.
  \fill[ocre] (coin) rectangle ($(coin)+(@pw@mm,@ph@mm)$);
  \fill[papier] ($(coin)+(0mm,@ph@mm-72mm)$) rectangle ($(coin)+(@pw@mm,@ph@mm-140mm)$);
  \node[anchor=west, text width=124mm, align=left, inner sep=0pt]
    at ($(coupe0)+(15mm,105mm)$) {%
      \color{ocre}\fontseries{b}\selectfont\fontsize{33}{43}\selectfont
      ENTREPRENDRE\\ AU\hspace{0.30em}CONGO};
  \node[anchor=north west, text width=120mm, align=left, inner sep=0pt]
    at ($(coupe0)+(15mm,60mm)$) {%
      \color{papier}\fontsize{13}{18}\selectfont Comprendre l’entrepreneuriat\\
      et savoir par où commencer};
  \node[anchor=south west, inner sep=0pt] at ($(coupe0)+(15mm,18mm)$) {%
      \color{papier}\demi\fontsize{12.5}{15}\selectfont Par Ruth ZADI Pukuta};
""",
}


def composer(nom, decor, sortie):
    pt = lambda mm: f"{mm * 72 / 25.4:.3f}"
    _, chemin, romain, italique, gras, maigre, demi = POLICES[nom]
    valeurs = {
        "chemin": chemin, "romain": romain, "italique": italique,
        "gras": gras, "maigre": maigre, "demi": demi,
        "pw": str(LARGEUR + 2 * FOND_PERDU), "ph": str(HAUTEUR + 2 * FOND_PERDU),
        "bw": str(LARGEUR + FOND_PERDU), "bh": str(HAUTEUR + FOND_PERDU),
        "fp": str(FOND_PERDU),
        "t0": pt(FOND_PERDU), "tx": pt(FOND_PERDU + LARGEUR),
        "ty": pt(FOND_PERDU + HAUTEUR),
    }
    source = PREAMBULE + decor + FIN
    for clef, valeur in valeurs.items():
        source = source.replace(f"@{clef}@", valeur)
    fichier = sortie / f"couverture-{nom}.tex"
    fichier.write_text(source, encoding="utf-8")
    # Deux passes : « remember picture » ancre les repères sur la page à partir
    # du fichier auxiliaire, qui n'existe qu'après la première compilation.
    for _ in range(2):
        resultat = subprocess.run(
            ["lualatex", "-interaction=nonstopmode", "-halt-on-error", fichier.name],
            cwd=sortie, capture_output=True, text=True)
    if resultat.returncode:
        journal = (sortie / f"couverture-{nom}.log").read_text(encoding="utf-8",
                                                              errors="replace")
        print(f"  {nom} : ÉCHEC")
        for ligne in [l for l in journal.split("\n") if l.startswith("!")][:4]:
            print("    " + ligne)
        return None
    pdf = sortie / f"couverture-{nom}.pdf"
    subprocess.run(["pdftoppm", "-r", "150", "-png", "-singlefile", str(pdf),
                    str(sortie / f"couverture-{nom}")], check=True)
    # La vignette : le livre se vendra en ligne, et une couverture illisible à
    # deux cents pixels est une couverture ratée, si belle soit-elle en grand.
    subprocess.run(["pdftoppm", "-scale-to-x", "200", "-scale-to-y", "-1",
                    "-png", "-singlefile", str(pdf),
                    str(sortie / f"vignette-{nom}")], check=True)
    return pdf


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--sortie", type=Path, default=Path("build/couverture"))
    options = analyseur.parse_args()
    options.sortie.mkdir(parents=True, exist_ok=True)
    for nom, decor in PARTIS.items():
        if composer(nom, decor, options.sortie):
            print(f"  {nom:<18} composée")


if __name__ == "__main__":
    main()
