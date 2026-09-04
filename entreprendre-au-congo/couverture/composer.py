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

UN POINT IMPORTANT. La police employée ici n'engage pas le choix du livre. Les
couvertures sont composées en Source Sans Pro, qui ne figure pas parmi les trois
candidates du spécimen : le choix de la police de labeur se tranche sur le texte
courant, et rien dans ces quatre pages ne doit peser sur cette décision. La
police de couverture se choisira après, en connaissance de la police du livre.
"""
import argparse
import subprocess
from pathlib import Path

TITRE = "ENTREPRENDRE AU CONGO"
SOUS_TITRE = "Comprendre l’entrepreneuriat et savoir par où commencer"
AUTRICE = "RUTH ZADI PUKUTA"

FOND_PERDU = 3          # mm
LARGEUR, HAUTEUR = 148, 210
SANS = "/usr/share/texlive/texmf-dist/fonts/opentype/adobe/sourcesanspro/"

PREAMBULE = r"""\documentclass{article}
\usepackage[paperwidth=@pw@mm,paperheight=@ph@mm,margin=0pt]{geometry}
\usepackage{fontspec}
\usepackage{tikz}
\usetikzlibrary{calc}
\usepackage[french]{babel}
\pagestyle{empty}
\setmainfont{SourceSansPro-Regular.otf}[
  Path       = @sans@ ,
  ItalicFont = SourceSansPro-RegularIt.otf ,
  BoldFont   = SourceSansPro-Bold.otf ,
  FontFace   = {l}{n}{SourceSansPro-Light.otf} ,
  FontFace   = {sb}{n}{SourceSansPro-Semibold.otf} ,
  Ligatures  = TeX ,
]
\newcommand{\maigre}{\fontseries{l}\selectfont}
\newcommand{\demi}{\fontseries{sb}\selectfont}

%% Encre : un noir de labeur, jamais le noir pur de l'écran, et un ocre sourd.
\definecolor{encre}{RGB}{26,26,26}
\definecolor{ocre}{RGB}{162,69,31}
\definecolor{papier}{RGB}{250,248,244}

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
      \color{encre}\maigre\fontsize{14}{18}\selectfont RUTH ZADI PUKUTA};
  \node[anchor=north west, text width=118mm, align=left, inner sep=0pt]
    at ($(coupe0)+(18mm,132mm)$) {%
      \color{encre}\demi\fontsize{39}{46}\selectfont ENTREPRENDRE\\ AU\hspace{0.30em}CONGO};
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
      \color{encre}\demi\fontsize{13}{16}\selectfont RUTH ZADI PUKUTA};
""",
"C-centree": r"""
  \fill[papier] (coin) rectangle ($(coin)+(@pw@mm,@ph@mm)$);
  %% Symétrie stricte, filets fins, beaucoup d'air : la couverture de librairie.
  \draw[encre,line width=0.4pt] ($(coupe0)+(24mm,178mm)$) -- ($(coupe0)+(124mm,178mm)$);
  \node[anchor=north, text width=112mm, align=center, inner sep=0pt]
    at ($(coupe0)+(74mm,168mm)$) {%
      \color{encre}\fontsize{11}{15}\selectfont RUTH\quad ZADI\quad PUKUTA};
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
      \color{encre}\demi\fontsize{12}{15}\selectfont RUTH ZADI PUKUTA};
""",
}


def composer(nom, decor, sortie):
    pt = lambda mm: f"{mm * 72 / 25.4:.3f}"
    valeurs = {
        "pw": str(LARGEUR + 2 * FOND_PERDU), "ph": str(HAUTEUR + 2 * FOND_PERDU),
        "bw": str(LARGEUR + FOND_PERDU), "bh": str(HAUTEUR + FOND_PERDU),
        "fp": str(FOND_PERDU), "sans": SANS,
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
