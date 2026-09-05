#!/usr/bin/env python3
"""La couverture complète : quatrième, dos et première, d'un seul tenant.

C'est le fichier que l'imprimeur attend. Une couverture ne se remet pas en trois
morceaux : elle s'imprime à plat sur une seule feuille, puis se plie autour du
bloc intérieur. Sa largeur est donc celle de deux pages plus l'épaisseur du dos,
et le fond perdu déborde des quatre côtés.

L'ÉPAISSEUR DU DOS SE CALCULE, ELLE NE SE DEVINE PAS. Elle dépend du nombre de
pages et du papier :

    dos = (pages / 2) x epaisseur d'un feuillet
    epaisseur d'un feuillet = grammage x main / 1000

La main est le volume du papier : 1,3 pour un offset courant. Les deux valeurs
sont des options, et le script imprime le calcul qu'il a fait. L'imprimeur doit
confirmer la main de son papier avant le tirage : une erreur de 0,5 mm sur le
dos décale le pli, et le titre du dos se retrouve sur la première de couverture.

Le parti pris est celui de la couverture retenue, B : un aplat ocre sur la
moitié haute, le titre en réserve. Le dos est ocre sur toute sa hauteur — un dos
à deux tons ferait apparaître le moindre décalage de pliage, qui est la règle
plutôt que l'exception sur un dos de sept millimètres.

Le texte de quatrième de couverture n'est pas dans le manuscrit : c'est le seul
texte de ce dépôt qui ne vient pas de l'auteure. Il est écrit à partir de
l'introduction et de la clôture, et la citation qui le termine est la sienne,
mot pour mot. Il est à relire.

Usage : python3 composer-jaquette.py [--pages 140] [--grammage 80] [--main 1.3]
"""
import argparse
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE))
import importlib.util
_c = importlib.util.spec_from_file_location("cov", RACINE / "composer.py")
COV = importlib.util.module_from_spec(_c)
_c.loader.exec_module(COV)

LARGEUR, HAUTEUR, FOND_PERDU = COV.LARGEUR, COV.HAUTEUR, COV.FOND_PERDU
BLOC = 104          # hauteur de l'aplat sous la coupe supérieure, en mm
MARGE = 16          # retrait du texte au bord de coupe, en mm

# --- Le texte de quatrième ---------------------------------------------------
ACCROCHE = r"Ce n'est pas l'initiative qui manque.\\[3mm] C'est la méthode."

DANS_L_APLAT = (
    "En République démocratique du Congo, on entreprend beaucoup. Trop "
    "d'activités s'arrêtent pourtant avant d'avoir atteint une taille viable "
    "— non par manque de clients, mais par manque de gestion."
)

SUR_LE_PAPIER = [
    "Ce livre est un instrument de travail. Il reprend les principes de gestion "
    "établis et les reformule dans les conditions réelles du marché congolais : "
    "trouver et valider une opportunité, connaître son marché, fixer le cap, "
    "trouver le capital, séparer la caisse de l'entreprise de celle du ménage, "
    "fixer ses prix, tenir ses comptes, durer, écrire son plan d'affaires.",
    "Chaque chapitre expose une notion, l'examine dans les conditions d'ici, et "
    "se termine par des opérations à exécuter dans la semaine. Le livre se "
    "referme sur un programme de quatre-vingt-dix jours.",
    "Pour les porteurs de projets, les entrepreneurs en activité, les étudiants "
    "et les formateurs.",
]

CITATION = ("Ceux qui échouent ici ne sont pas ceux qui ont vu trop grand. "
            "Ce sont ceux qui ont voulu arriver sans passer par les étapes.")

PREAMBULE = r"""\documentclass{article}
\usepackage[paperwidth=@pw@mm,paperheight=@ph@mm,margin=0pt]{geometry}
\usepackage{fontspec}
\usepackage{tikz}
\usetikzlibrary{calc}
\usepackage[french]{babel}
\frenchsetup{AutoSpacePunctuation=false}
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

\definecolor{encre}{cmyk}{0,0,0,1}
\definecolor{ocre}{cmyk}{0,0.57,0.81,0.36}
\definecolor{papier}{cmyk}{0,0,0,0}

\directlua{pdf.setpageattributes("/TrimBox [@t0@ @t0@ @tx@ @ty@]")}

\begin{document}
\begin{tikzpicture}[remember picture,overlay]
  \coordinate (coin) at (current page.south west);
  %% L'origine des mesures : le coin inférieur gauche de la coupe, c'est-à-dire
  %% le bord gauche de la quatrième de couverture une fois rognée. Le décalage
  %% fait glisser tout le dessin vers la gauche : la page ne montre alors qu'un
  %% panneau, la première ou la quatrième, sans qu'une seule cote change.
  \coordinate (o) at ($(coin)+(@fp@mm-@decalage@mm,@fp@mm)$);
  %% Le dessin est celui de la jaquette entière ; la page n'en montre qu'une
  %% part. Sans cette découpe, l'ocre du dos et le titre qu'il porte
  %% déborderaient sur le bord d'un panneau composé seul.
  \clip (coin) rectangle ($(coin)+(@pw@mm,@ph@mm)$);
"""

FIN = r"""\end{tikzpicture}
\end{document}
"""


def decor(dos, avec_dos=True):
    """Le dessin de la jaquette, dos calculé.

    Le dos n'est dessiné que sur la jaquette entière. Sur un panneau composé
    seul, il tomberait dans le fond perdu — invisible après la coupe, mais bien
    visible à l'écran, où il ressemble à un défaut.
    """
    devant = LARGEUR + dos          # abscisse du bord gauche de la première
    haut = HAUTEUR - BLOC           # ordonnée du bas de l'aplat
    dos_aplat = rf"""
  %% Le dos est ocre sur toute sa hauteur. Un dos à deux tons trahirait le
  %% moindre décalage de pliage ; d'un seul ton, il l'absorbe.
  \fill[ocre] ($(o)+({LARGEUR}mm,-@fp@mm)$)
    rectangle ($(o)+({devant}mm,{HAUTEUR}mm+@fp@mm)$);
""" if avec_dos else ""
    dos_texte = rf"""
  %% ---------- Dos ----------
  %% Le titre se lit de haut en bas, usage français. Il est centré sur le dos.
  \node[rotate=-90, anchor=west, inner sep=0pt]
    at ($(o)+({LARGEUR + dos / 2}mm,{HAUTEUR - 22}mm)$) {{%
      \color{{papier}}\demi\fontsize{{9}}{{11}}\selectfont ENTREPRENDRE AU CONGO}};
  \node[rotate=-90, anchor=east, inner sep=0pt]
    at ($(o)+({LARGEUR + dos / 2}mm,20mm)$) {{%
      \color{{papier}}\fontsize{{8.5}}{{10}}\selectfont ZADI PUKUTA}};
""" if avec_dos else ""
    return rf"""
  %% Le papier, fond perdu compris.
  \fill[papier] (coin) rectangle ($(coin)+(@pw@mm,@ph@mm)$);

  %% L'aplat de tête traverse la quatrième et la première ; il est coupé en haut
  %% et sur les deux côtés, donc il couvre le fond perdu.
  \fill[ocre] ($(coin)+(0mm,@ph@mm)$) rectangle ($(o)+(@lc@mm,{haut}mm)$);
{dos_aplat}
  %% ---------- Quatrième de couverture ----------
  %% Dans l'aplat : l'accroche, le constat de départ, et la phrase de l'auteure.
  %% La citation est en réserve avec le reste plutôt que sur le papier : elle est
  %% la voix du livre, et l'aplat est l'endroit où l'œil se pose en premier.
  \node[anchor=north west, text width={LARGEUR - 2 * MARGE}mm, align=flush left,
        inner sep=0pt] at ($(o)+({MARGE}mm,{HAUTEUR - 26}mm)$) {{%
      \color{{papier}}\demi\fontsize{{19}}{{25}}\selectfont {ACCROCHE}}};
  \node[anchor=north west, text width={LARGEUR - 2 * MARGE}mm, align=flush left,
        inner sep=0pt] at ($(o)+({MARGE}mm,155mm)$) {{%
      \color{{papier}}\fontsize{{10.5}}{{14.5}}\selectfont {DANS_L_APLAT}}};
  \draw[papier, line width=0.6pt]
    ($(o)+({MARGE}mm,134mm)$) -- ($(o)+({MARGE + 22}mm,134mm)$);
  \node[anchor=north west, text width={LARGEUR - 2 * MARGE - 8}mm,
        align=flush left, inner sep=0pt] at ($(o)+({MARGE}mm,130mm)$) {{%
      \color{{papier}}\itshape\fontsize{{11}}{{15}}\selectfont «~{CITATION}~»}};

  %% Sur le papier : ce que le livre fait et à qui il s'adresse. Chaque bloc est
  %% posé à une ordonnée mesurée plutôt qu'enchaîné dans un seul nœud, seule
  %% manière de garantir qu'aucun ne recouvre le suivant si le texte change.
  \node[anchor=north west, text width={LARGEUR - 2 * MARGE}mm, align=flush left,
        inner sep=0pt] at ($(o)+({MARGE}mm,{haut - 14}mm)$) {{%
      \color{{encre}}\fontsize{{10.5}}{{14.5}}\selectfont {SUR_LE_PAPIER[0]}
      \par\vspace{{3mm}} {SUR_LE_PAPIER[1]}
      \par\vspace{{3mm}} \maigre\itshape {SUR_LE_PAPIER[2]}}};

  \draw[ocre, line width=0.6pt]
    ($(o)+({MARGE}mm,26mm)$) -- ($(o)+({MARGE + 22}mm,26mm)$);
  \node[anchor=south west, inner sep=0pt] at ($(o)+({MARGE}mm,14mm)$) {{%
      \color{{encre}}\demi\fontsize{{11}}{{14}}\selectfont Par Ruth ZADI Pukuta}};

  %% La réserve du code-barres : un blanc franc, en bas à droite, sans mention
  %% d'attente. L'ISBN et son code s'y déposeront quand ils existeront — un
  %% EAN-13 mesure 37,3 × 25,9 mm à l'échelle normale, la réserve les tient.
  \fill[papier] ($(o)+({LARGEUR - MARGE - 40}mm,12mm)$)
    rectangle ($(o)+({LARGEUR - MARGE}mm,40mm)$);

{dos_texte}
  %% ---------- Première de couverture ----------
  \draw[papier, line width=0.9pt]
    ($(o)+({devant + MARGE}mm,180mm)$) -- ($(o)+({devant + MARGE + 22}mm,180mm)$);
  \node[anchor=north west, text width=118mm, align=left, inner sep=0pt]
    at ($(o)+({devant + MARGE}mm,168mm)$) {{%
      \color{{papier}}\demi\fontsize{{38}}{{42}}\selectfont
      ENTREPRENDRE\\[6mm] AU\hspace{{0.15em}}CONGO}};
  \node[anchor=north west, text width=112mm, align=left, inner sep=0pt]
    at ($(o)+({devant + MARGE}mm,88mm)$) {{%
      \color{{encre}}\fontsize{{13.5}}{{19}}\selectfont Comprendre l'entrepreneuriat\\
      et savoir par où commencer}};
  \draw[ocre, line width=0.6pt]
    ($(o)+({devant + MARGE}mm,34mm)$) -- ($(o)+({devant + MARGE + 22}mm,34mm)$);
  \node[anchor=south west, inner sep=0pt]
    at ($(o)+({devant + MARGE}mm,22mm)$) {{%
      \color{{encre}}\demi\fontsize{{13}}{{16}}\selectfont Par Ruth ZADI Pukuta}};
"""


PANNEAUX = ("jaquette", "premiere", "quatrieme")


def composer(panneau, dos, largeur_totale, sortie, nom):
    """Rend le dessin, la page cadrée sur le panneau demandé."""
    pt = lambda mm: f"{mm * 72 / 25.4:.3f}"
    # La jaquette montre tout ; un panneau seul montre une page, et le dessin
    # glisse pour que ce soit la bonne.
    if panneau == "jaquette":
        largeur, decalage = largeur_totale, 0.0
    elif panneau == "premiere":
        largeur, decalage = float(LARGEUR), LARGEUR + dos
    else:
        largeur, decalage = float(LARGEUR), 0.0

    _, chemin, romain, italique, gras, maigre, demi = COV.POLICES["B-bloc-couleur"]
    valeurs = {
        "chemin": chemin, "romain": romain, "italique": italique,
        "gras": gras, "maigre": maigre, "demi": demi,
        "pw": f"{largeur + 2 * FOND_PERDU:.1f}",
        "ph": str(HAUTEUR + 2 * FOND_PERDU),
        "lc": f"{largeur_totale:.1f}", "fp": str(FOND_PERDU),
        "decalage": f"{decalage:.1f}",
        "t0": pt(FOND_PERDU), "tx": pt(FOND_PERDU + largeur),
        "ty": pt(FOND_PERDU + HAUTEUR),
    }
    source = PREAMBULE + decor(dos, avec_dos=(panneau == "jaquette")) + FIN
    for clef, valeur in valeurs.items():
        source = source.replace(f"@{clef}@", valeur)

    fichier = sortie / f"{nom}.tex"
    fichier.write_text(source, encoding="utf-8")
    for _ in range(2):
        resultat = subprocess.run(
            ["lualatex", "-interaction=nonstopmode", "-halt-on-error", fichier.name],
            cwd=sortie, capture_output=True, text=True)
    if resultat.returncode:
        journal = fichier.with_suffix(".log").read_text(encoding="utf-8",
                                                        errors="replace")
        print(f"  {panneau} : ÉCHEC")
        for ligne in [l for l in journal.split("\n") if l.startswith("!")][:6]:
            print("    " + ligne)
        return None
    pdf = fichier.with_suffix(".pdf")
    # Un fichier remis à un imprimeur se nomme lui-même : son titre et son
    # autrice sont dans ses métadonnées, pas seulement dans son nom de fichier.
    from pypdf import PdfReader, PdfWriter
    lecteur, ecrivain = PdfReader(str(pdf)), PdfWriter()
    for page in lecteur.pages:
        ecrivain.add_page(page)
    ecrivain.add_metadata({
        "/Title": f"Entreprendre au Congo — couverture ({panneau})",
        "/Author": "Ruth ZADI Pukuta",
        "/Creator": "LuaLaTeX, TikZ",
    })
    with pdf.open("wb") as sortie_pdf:
        ecrivain.write(sortie_pdf)
    subprocess.run(["pdftoppm", "-r", "150", "-png", "-singlefile", str(pdf),
                    str(pdf.with_suffix(""))], check=True)
    return pdf


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--pages", type=int, default=140)
    analyseur.add_argument("--grammage", type=float, default=80.0,
                           help="grammage du papier intérieur, en g/m²")
    analyseur.add_argument("--main", type=float, default=1.3,
                           help="main du papier : son volume, 1,3 pour un offset")
    analyseur.add_argument("--dos", type=float, default=None,
                           help="épaisseur du dos en mm, si l'imprimeur l'impose")
    analyseur.add_argument("--sortie", type=Path, default=Path("build/couverture"))
    options = analyseur.parse_args()
    options.sortie.mkdir(parents=True, exist_ok=True)

    feuillet = options.grammage * options.main / 1000
    dos = options.dos if options.dos else round(options.pages / 2 * feuillet, 1)
    largeur = 2 * LARGEUR + dos

    print(f"  papier        : {options.grammage:g} g/m², main {options.main:g}"
          f" → feuillet {feuillet:.3f} mm")
    print(f"  dos           : {options.pages} pages ÷ 2 × {feuillet:.3f}"
          f" = {dos:g} mm  (à confirmer par l'imprimeur)")
    print(f"  jaquette      : {largeur:.1f} × {HAUTEUR} mm rognée,"
          f" {largeur + 2 * FOND_PERDU:.1f} × {HAUTEUR + 2 * FOND_PERDU} mm avec fond perdu")

    noms = {"jaquette": "ENTREPRENDRE-AU-CONGO-jaquette",
            "premiere": "ENTREPRENDRE-AU-CONGO-premiere",
            "quatrieme": "ENTREPRENDRE-AU-CONGO-quatrieme"}
    for panneau in PANNEAUX:
        pdf = composer(panneau, dos, largeur, options.sortie, noms[panneau])
        if not pdf:
            return 1
        print(f"  {panneau:<13} : {pdf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
