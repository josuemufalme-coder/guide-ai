#!/usr/bin/env python3
"""Contrôle de langue du manuscrit par LanguageTool — phase 8.

Le contrôle porte sur la source, non sur le PDF : c'est là que se corrige ce
qu'il trouve, et le texte y est encore découpé en paragraphes plutôt qu'en
lignes coupées par la justification.

Ce que le script retire avant de soumettre : les blocs de schéma, qui sont des
dessins, les attributs d'ouverture d'encadré, les marqueurs de partie et les
barres verticales des tableaux. Ce qui reste est de la prose, et le compte de
signes est préservé — les positions rapportées désignent le fichier réel.

Les règles écartées le sont pour une raison nommée dans ECARTEES : LanguageTool
juge le français de France et l'ouvrage est écrit en République démocratique du
Congo ; il exige aussi une typographie que la phase 2 a déjà arrêtée autrement.

Usage : python3 controler-langue.py [--source src] [--tout]
"""
import argparse
import re
import sys
from pathlib import Path

# Les règles écartées, et pourquoi. Rien n'est écarté sans motif écrit.
ECARTEES = {
    # La phase 2 a posé les espaces insécables elle-même, par un script
    # versionné. LanguageTool les redemande là où il ne les voit pas, parce
    # qu'il ne reconnaît pas toujours l'espace fine U+202F.
    "TYPOGRAPHIE": "espacement arrêté par la phase 2",
    "UNPAIRED_BRACKETS": "les blocs sont coupés en paragraphes",
    "FRENCH_WHITESPACE": "espacement arrêté par la phase 2",
    "FRENCH_WHITESPACE_STRICT": "espacement arrêté par la phase 2",
    "APOS_TYP": "l'apostrophe courbe est déjà celle du manuscrit",
    "APOS_ESPACE": "l'apostrophe courbe est déjà celle du manuscrit",
    # Le manuscrit est en gras et en italique de Markdown : les astérisques
    # ne sont pas de la ponctuation.
    "ESPACE_APRES_PONCTUATION": "les astérisques du Markdown",
}


# Ce qui, dans le manuscrit, n'est pas de la prose et se retire avant l'analyse.
# Une première version remplaçait ces marques par des espaces, pour garder les
# décalages : LanguageTool signalait alors huit cent cinquante espaces doubles
# et lisait « **A**mbitieux » comme le mot « mbitieux ». Les marques sont donc
# retirées pour de bon, et un tableau de correspondance ramène chaque position
# trouvée à sa place dans le fichier.
# « . » sous re.S traverse les fins de ligne : les motifs de ligne s'écrivent
# donc [^\n], sans quoi « ^:::.*$ » avalerait le fichier entier — il l'a fait.
MARQUES = re.compile(
    r"```schema.*?```"                # un schéma est un dessin
    r"|^:::[^\n]*$"                   # l'ouverture et la fermeture d'un encadré
    r"|^<!--[^\n]*$"                  # le marqueur de partie
    r"|^\|[\s|:-]+\|[ \t]*$"          # le filet d'un tableau
    r"|^#{1,6}[ ]"                    # le niveau d'un titre
    r"|^[ ]*-[ ]"                     # la puce d'une liste
    r"|^[ ]*\d{1,2}\.[ ]"              # le numéro d'une liste
    r"|\|"                            # la barre qui sépare deux cellules
    r"|\*\*|\*"                        # le gras et l'italique
    r"|\[\^\d+\]",                     # l'appel de note
    re.S | re.M)


def prose(texte):
    """Le texte réduit à sa prose, et la position d'origine de chacun de ses signes."""
    propre, origine, fin = [], [], 0
    for marque in MARQUES.finditer(texte):
        for decalage in range(fin, marque.start()):
            propre.append(texte[decalage])
            origine.append(decalage)
        # Une barre de tableau sépare deux cellules : sans elle, deux libellés
        # se souderaient en une phrase que LanguageTool jugerait fautive.
        if marque.group().startswith((":", "<", "|", "`")) or marque.group().endswith(" "):
            propre.append("\n")
            origine.append(marque.start())
        fin = marque.end()
    for decalage in range(fin, len(texte)):
        propre.append(texte[decalage])
        origine.append(decalage)
    return "".join(propre), origine


def ligne_et_colonne(texte, decalage):
    avant = texte[:decalage]
    return avant.count("\n") + 1, decalage - (avant.rfind("\n") + 1) + 1


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--source", type=Path, default=Path("src"))
    analyseur.add_argument("--tout", action="store_true",
                           help="n'écarte aucune règle")
    options = analyseur.parse_args()

    import language_tool_python

    outil = language_tool_python.LanguageTool("fr")
    total, retenues = 0, 0
    try:
        for fichier in sorted(options.source.glob("*.md")):
            texte = fichier.read_text(encoding="utf-8")
            propre, origine = prose(texte)
            trouvailles = outil.check(propre)
            total += len(trouvailles)
            gardees = [t for t in trouvailles
                       if options.tout or t.rule_id not in ECARTEES]
            retenues += len(gardees)
            if not gardees:
                continue
            print(f"\n── {fichier.name}")
            for t in gardees:
                depart = origine[min(t.offset, len(origine) - 1)]
                ligne, colonne = ligne_et_colonne(texte, depart)
                extrait = propre[t.offset:t.offset + t.error_length]
                propose = ", ".join(t.replacements[:3])
                print(f"  {ligne}:{colonne}  [{t.rule_id}] « {extrait} »"
                      f"{' → ' + propose if propose else ''}")
                print(f"      {t.message}")
    finally:
        outil.close()

    print(f"\nrelevées : {total}   écartées par règle nommée : {total - retenues}"
          f"   à examiner : {retenues}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
