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
NUMERO = re.compile(r"^(\d{1,2})\. ")
FILET = re.compile(r"^\|[\s|:-]+\|\s*$")


def en_latex(ligne):
    return COMP.en_latex(ligne)


SANS_NUMERO = re.compile(r"^Chapitre\s+\d+\s*—\s*")


def sans_numero(titre):
    """« Chapitre 5 — Analyser son marché » devient « Analyser son marché »."""
    return SANS_NUMERO.sub("", titre)


def nom_de_partie(intitule):
    """« Quatrième partie — PLANIFIER ET DÉCIDER » donne « PLANIFIER ET DÉCIDER »."""
    _, _, nom = intitule.partition("—")
    return (nom or intitule).strip()


def rang_de_partie(intitule):
    """La part de l'intitulé qui dit le rang : « Quatrième partie »."""
    rang, separateur, _ = intitule.partition("—")
    return rang.strip() if separateur else ""


def petites_capitales(texte):
    """Un titre courant en petites capitales véritables.

    Les petites capitales se dessinent à partir des minuscules : un intitulé de
    partie, qui est écrit tout en capitales dans le manuscrit, doit d'abord
    redescendre en bas de casse, sans quoi la police rend des capitales de
    pleine hauteur et la ligne de tête crie.
    """
    if not texte:
        return ""
    return r"\textsc{\MakeLowercase{%s}}" % en_latex(texte)


def page_de_partie(intitule):
    """La page de titre d'une partie : recto, sans folio, verso blanc.

    Elle remplace le \part* de memoir pour deux raisons. La première est de
    forme : une partie s'annonce sur sa propre page, rang au-dessus, filet, nom
    au-dessous, et rien d'autre. La seconde est un défaut constaté : le
    \addcontentsline qui suivait \part* s'exécutait une fois la page tournée,
    et la table des matières renvoyait deux pages trop loin. Ici, il est écrit
    sur la page de la partie elle-même.
    """
    rang, nom = rang_de_partie(intitule), nom_de_partie(intitule)
    return "\n".join([
        r"\cleardoublepage",
        r"\thispagestyle{empty}",
        r"\addcontentsline{toc}{part}{%s}" % en_latex(intitule),
        r"\markboth{%s}{%s}" % (petites_capitales(nom), petites_capitales(nom)),
        r"\vspace*{52mm}",
        r"\begin{center}",
        r"{\small\textsc{\MakeLowercase{%s}}}\par" % en_latex(rang),
        r"\vspace{6mm}",
        r"{\color{filet}\rule{20mm}{0.4pt}}\par",
        r"\vspace{8mm}",
        r"{\LARGE\bfseries %s}" % en_latex(nom),
        r"\end{center}",
        r"\vfill",
        r"\cleardoublepage",
    ])


def convertir(chemin, etat):
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
                    "\\begin{BVerbatim}[fontsize=\\corpsschema]\n"
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
            intitule = TITRE_PARTIE.match(nue).group(1)
            etat["partie"] = nom_de_partie(intitule)
            sortie.append(page_de_partie(intitule))
        elif nue.startswith("# "):
            fermer_liste()
            titre = en_latex(nue[2:])
            # Le titre entre à la table des matières et aux titres courants :
            # sans \addcontentsline, un \chapter* n'y figure pas. Le titre
            # courant, lui, laisse tomber le « Chapitre N — » : le numéro est
            # déjà en tête du chapitre, et la ligne de tête doit tenir dans la
            # justification.
            sortie.append(r"\chapter*{%s}\addcontentsline{toc}{chapter}{%s}"
                          r"\markboth{%s}{%s}"
                          % (titre, titre, petites_capitales(etat["partie"]),
                             petites_capitales(sans_numero(nue[2:]))))
        elif nue.startswith("### "):
            fermer_liste()
            sortie.append(r"\placedutitre\subsection*{%s}" % en_latex(nue[4:]))
        elif nue.startswith("## "):
            fermer_liste()
            sortie.append(r"\placedutitre\section*{%s}" % en_latex(nue[3:]))
        elif nue.startswith("::: {"):
            fermer_liste()
            titre = re.search(r'titre="([^"]*)"', nue)
            sorte = re.search(r'type="([^"]*)"', nue)
            sortie.append(r"\begin{encadre}{%s}{%s}" % (
                sorte.group(1) if sorte else "aparte",
                en_latex(titre.group(1) if titre else "")))
        elif nue == ":::":
            fermer_liste()
            sortie.append(r"\end{encadre}")
        elif nue.startswith("- "):
            if liste != "itemize":
                fermer_liste(); sortie.append(r"\begin{itemize}"); liste = "itemize"
            sortie.append(r"\item %s" % en_latex(nue[2:]))
        elif NUMERO.match(nue):
            rang = int(NUMERO.match(nue).group(1))
            if liste != "enumerate":
                fermer_liste()
                # Une énumération interrompue par un tableau ou par un
                # paragraphe repartait de 1 : le livre imprimait « 1, 2, 1 » au
                # chapitre 5, et « 1, 1, 2… 7 » pour les huit parties du plan
                # d'affaires. Le rang écrit dans le manuscrit fait foi.
                sortie.append(r"\begin{enumerate}"
                              + (r"\setcounter{enumi}{%d}" % (rang - 1)
                                 if rang != 1 else ""))
                liste = "enumerate"
            sortie.append(r"\item %s" % en_latex(NUMERO.sub("", nue)))
        else:
            fermer_liste()
            sortie.append(en_latex(nue))
    fermer_liste(); fermer_tableau()
    return "\n\n".join(sortie)


def liminaire_en_latex(chemin):
    """La page de titre, la page de droits et la table des matières.

    Le cahier des charges les confie à la phase 6 ; sans elles, le PDF n'est pas
    un livre mais un tirage de chapitres.

    ISBN, dépôt légal, achevé d'imprimer : ces trois mentions ne s'inventent pas
    et ne figurent pas ici. Pas de ligne en attente, pas de crochets — la page de
    droits ne porte que ce qui est établi. Les trois lignes seront ajoutées quand
    les numéros existeront, sans rien déplacer d'autre.
    """
    lignes = [l.strip() for l in chemin.read_text(encoding="utf-8").split("\n")
              if l.strip()]
    droits = [en_latex(l) for l in lignes
              if not l.startswith("#") and "ENTREPRENDRE AU CONGO" not in l
              and "Comprendre l" not in l]
    return "\n\n".join([
        r"\frontmatter",
        r"\thispagestyle{empty}",
        r"\vspace*{55mm}",
        r"\begin{center}",
        r"{\fontsize{26}{32}\selectfont\bfseries ENTREPRENDRE\\[2mm] AU CONGO}",
        r"\vspace{12mm}",
        r"{\large Comprendre l'entrepreneuriat\\ et savoir par où commencer}",
        r"\vspace{28mm}",
        r"{\large Par Ruth ZADI Pukuta}",
        r"\end{center}",
        r"\cleardoublepage",
        r"\thispagestyle{empty}",
        r"\vspace*{\fill}",
        r"{\small\raggedright " + r"\par ".join(droits) + r"\par}",
        r"\cleardoublepage",
        r"\tableofcontents*",
        r"\mainmatter",
    ])


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--police", default="sourceserif")
    analyseur.add_argument("--source", type=Path, default=Path("src"))
    analyseur.add_argument("--sortie", type=Path, default=Path("build/livre"))
    options = analyseur.parse_args()
    options.sortie.mkdir(parents=True, exist_ok=True)

    fichiers = sorted(options.source.glob("*.md"))
    # Le premier fichier porte la page de titre et la page de droits : il n'est
    # pas du corps de l'ouvrage et se compose à part, en pages liminaires.
    liminaires, corps_fichiers = fichiers[0], fichiers[1:]
    # La partie courante se transmet d'un fichier à l'autre : seuls huit des
    # seize chapitres portent l'ouverture de leur partie, les autres en héritent.
    # L'introduction, la clôture et les notes n'appartiennent à aucune partie :
    # leur ligne de tête de gauche reste vide plutôt que de porter la partie
    # précédente, qui ne les concerne pas.
    etat, morceaux = {"partie": ""}, []
    for fichier in corps_fichiers:
        if not fichier.stem[:2].isdigit() or fichier.stem[:2] in ("00", "80", "90"):
            etat["partie"] = ""
        morceaux.append(convertir(fichier, etat))
    corps = (liminaire_en_latex(liminaires) + "\n\n"
             + "\n\n\\cleardoublepage\n\n".join(morceaux))
    police = POLICES[options.police]

    global PREAMBULE
    preambule = PREAMBULE.replace(r"\begin{document}",
                                  "\\usepackage{tabularx}\n"
                                  "\\usepackage{booktabs}\n"
                                  "\\usepackage{fancyvrb}\n"
                                  "\\usepackage{graphicx}\n"
                                  "\\newsavebox{\\boiteschema}\n"
                                  "\\begin{document}")
    preambule = preambule.replace(r"\setcounter{page}{18}", "")
    preambule = preambule.replace(
        r"\begin{document}",
        "\\setcounter{tocdepth}{0}\n\\setcounter{secnumdepth}{-1}\n"
        # La colonne des folios doit tenir trois chiffres, et l'entrée s'arrêter
        # avant elle : sinon un folio à trois chiffres déborde la justification.
        # Ces réglages n'ont d'effet que posés avant \\begin{document}.
        "\\setpnumwidth{3em}\n\\setrmarg{4.5em}\n"
        "\\begin{document}")
    # La ligne de régie appartient au spécimen : elle nomme la police et le corps
    # que la double page donne à juger. Sur l'ouvrage, elle s'imprimerait au pied
    # de chaque page. Les deux redéfinitions de pied qui la portent sont retirées
    # du préambule ; le pied redevient celui du livre, le folio seul.
    for pied in (r"\makeoddfoot{livre}{}{\scriptsize\color{filet}@regie@}{\small\thepage}",
                 r"\makeevenfoot{livre}{\small\thepage}{\scriptsize\color{filet}@regie@}{}"):
        assert pied in preambule, pied
        preambule = preambule.replace(pied + "\n", "")
    COMP.PREAMBULE = preambule
    regie = ""
    # L'imposition exige une pagination multiple de quatre. Le nombre de pages
    # blanches à ajouter ne se devine pas : on compose, on compte, on complète,
    # et on recompose pour vérifier que le compte est juste.
    blanches = ""
    for _ in range(2):
        pdf = COMP.composer("livre", police, corps + blanches, options.sortie,
                            "Entreprendre au Congo", regie)
        if not pdf:
            return 1
        pages = COMP.compte_de_pages(pdf)
        manque = -pages % 4
        if not manque:
            break
        blanches = ("\n\n" + "\n".join(
            [r"\clearpage\thispagestyle{empty}\null"] * manque))

    print(f"  {police['nom']} — {len(fichiers)} fichiers, {pages} pages")
    print(f"  multiple de 4 : {'oui' if pages % 4 == 0 else f'non, il en manque {-pages % 4}'}")
    final = options.sortie / "ENTREPRENDRE-AU-CONGO-interieur.pdf"
    final.write_bytes(pdf.read_bytes())
    print(f"  livrable : {final}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
