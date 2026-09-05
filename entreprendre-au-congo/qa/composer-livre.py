#!/usr/bin/env python3
"""Compose l'ouvrage entier — phase 1, chiffrage de D5.

Le spécimen tranche le choix de la police ; il ne dit rien de la pagination.
Celle-ci ne s'extrapole pas : elle se compose. Ce script convertit les vingt
fichiers du manuscrit et produit le livre complet, dont on tire le nombre de
pages réel et les quatre mesures de composition.

À la différence du convertisseur du spécimen, celui-ci traite tout ce que le
manuscrit porte : les titres de partie et de chapitre, les sept tableaux, les
trois schémas, les encadrés typés et les appels de notes.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "style"))
sys.path.insert(0, str(RACINE / "qa"))
from gabarit import GEOMETRIE, POLICES, PREAMBULE                 # noqa: E402

import importlib.util                                            # noqa: E402
_c = importlib.util.spec_from_file_location("comp", RACINE / "qa" / "composer-specimen.py")
COMP = importlib.util.module_from_spec(_c); _c.loader.exec_module(COMP)

TITRE_PARTIE = re.compile(r"<!--\s*(.*?)\s*-->")
CELLULES = re.compile(r"^\|(.*)\|\s*$")
FILET = re.compile(r"^\|[\s|:-]+\|\s*$")


def en_latex(ligne):
    return COMP.en_latex(ligne)


def convertir(chemin):
    """Un fichier du manuscrit en LaTeX."""
    sortie, liste, tableau, schema = [], None, [], None

    def fermer_liste():
        nonlocal liste
        if liste:
            sortie.append(r"\end{%s}" % liste)
            liste = None

    def fermer_tableau():
        nonlocal tableau
        if tableau:
            # Toutes les rangées sont ramenées à la largeur de l'en-tête : une
            # cellule vide en fin de rangée produit sinon une colonne de trop, et
            # LaTeX refuse le tableau entier.
            colonnes = len(tableau[0])
            tableau = [(rangee + [""] * colonnes)[:colonnes] for rangee in tableau]
            # Une colonne fixe déborde dès qu'une cellule est plus large qu'elle.
            # Les colonnes dont le contenu est long deviennent donc élastiques,
            # les courtes restent au fer à gauche.
            longueurs = [max(len(rangee[i]) for rangee in tableau)
                         for i in range(colonnes)]
            largeur = "@{}" + "".join(
                "X" if longueur > 12 else "l" for longueur in longueurs) + "@{}"
            if "X" not in largeur:
                largeur = "@{}" + "X" + "l" * (colonnes - 1) + "@{}"
            corps = [" & ".join(en_latex(c) for c in rangee) + r" \\" for rangee in tableau]
            sortie.append("\n".join([
                r"\begin{table}[htbp]\centering\small",
                r"\begin{tabularx}{\linewidth}{" + largeur + "}",
                r"\toprule", corps[0], r"\midrule", *corps[1:],
                r"\bottomrule", r"\end{tabularx}", r"\end{table}"]))
            tableau = []

    for ligne in chemin.read_text(encoding="utf-8").split("\n"):
        nue = ligne.rstrip()
        if schema is not None:
            if nue.startswith("```"):
                # FancyVerb veut son \end{Verbatim} seul sur sa ligne, et le bloc
                # se construit d'un tenant : le joindre par des lignes vides
                # ajouterait des blancs au milieu du schéma.
                # Le schéma en chasse fixe est plus large que la justification :
                # c'est mesuré, et c'est la raison pour laquelle la phase 4 les
                # redessine en vectoriel. En attendant, il est ramené à la mesure
                # plutôt que de déborder — un débordement s'imprime, lui.
                # Un environnement verbatim ne passe pas en argument de macro :
                # il est d'abord mis en boîte, puis la boîte est réduite — et
                # seulement si elle dépasse la justification.
                sortie.append(
                    "\\begin{lrbox}{\\boiteschema}\n"
                    "\\begin{BVerbatim}[fontsize=\\small]\n"
                    + "\n".join(schema)
                    + "\n\\end{BVerbatim}\n\\end{lrbox}\n"
                    "\\begin{center}\n"
                    "\\ifdim\\wd\\boiteschema>\\linewidth\n"
                    "  \\resizebox{\\linewidth}{!}{\\usebox{\\boiteschema}}\n"
                    "\\else\n  \\usebox{\\boiteschema}\n\\fi\n"
                    "\\end{center}")
                schema = None
            else:
                schema.append(nue)
            continue
        if nue.startswith("```schema"):
            fermer_liste(); fermer_tableau()
            schema = []
            continue
        if FILET.match(nue):
            continue
        if CELLULES.match(nue):
            fermer_liste()
            tableau.append([c.strip() for c in CELLULES.match(nue).group(1).split("|")])
            continue
        fermer_tableau()
        if not nue:
            continue
        if nue.startswith("<!--"):
            fermer_liste()
            sortie.append(r"\part*{%s}" % en_latex(TITRE_PARTIE.match(nue).group(1)))
        elif nue.startswith("# "):
            fermer_liste()
            titre = en_latex(nue[2:])
            sortie.append(r"\chapter*{%s}\markright{%s}" % (titre, titre))
        elif nue.startswith("## "):
            fermer_liste()
            sortie.append(r"\section*{%s}" % en_latex(nue[3:]))
        elif nue.startswith("::: {"):
            fermer_liste()
            titre = re.search(r'titre="([^"]*)"', nue)
            sortie.append(r"\begin{encadre}{%s}" % en_latex(titre.group(1) if titre else ""))
        elif nue == ":::":
            fermer_liste()
            sortie.append(r"\end{encadre}")
        elif nue.startswith("- "):
            if liste != "itemize":
                fermer_liste(); sortie.append(r"\begin{itemize}"); liste = "itemize"
            sortie.append(r"\item %s" % en_latex(nue[2:]))
        elif re.match(r"^\d{1,2}\. ", nue):
            if liste != "enumerate":
                fermer_liste(); sortie.append(r"\begin{enumerate}"); liste = "enumerate"
            sortie.append(r"\item %s" % en_latex(re.sub(r"^\d{1,2}\. ", "", nue)))
        else:
            fermer_liste()
            sortie.append(en_latex(nue))
    fermer_liste(); fermer_tableau()
    return "\n\n".join(sortie)


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--police", default="sourceserif")
    analyseur.add_argument("--source", type=Path, default=Path("src"))
    analyseur.add_argument("--sortie", type=Path, default=Path("build/livre"))
    options = analyseur.parse_args()
    options.sortie.mkdir(parents=True, exist_ok=True)

    fichiers = sorted(options.source.glob("*.md"))
    corps = "\n\n\\cleardoublepage\n\n".join(convertir(f) for f in fichiers)
    police = POLICES[options.police]

    global PREAMBULE
    preambule = PREAMBULE.replace(r"\begin{document}",
                                  "\\usepackage{tabularx}\n"
                                  "\\usepackage{booktabs}\n"
                                  "\\usepackage{fancyvrb}\n"
                                  "\\usepackage{graphicx}\n"
                                  "\\newsavebox{\\boiteschema}\n"
                                  "\\begin{document}")
    preambule = preambule.replace(r"\setcounter{page}{18}", r"\setcounter{page}{1}")
    COMP.PREAMBULE = preambule
    pdf = COMP.composer("livre", police, corps, options.sortie,
                        "Entreprendre au Congo",
                        f"{police['nom']} \\quad {police['corps']:g}/"
                        f"{police['interlignage']:g} pt")
    if not pdf:
        return 1
    pages = COMP.compte_de_pages(pdf)
    print(f"  {police['nom']} — {len(fichiers)} fichiers, {pages} pages")
    print(f"  multiple de 4 : {'oui' if pages % 4 == 0 else f'non, il en manque {-pages % 4}'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
