#!/usr/bin/env python3
"""Normalisation typographique française du manuscrit — phase 2.

Le cahier des charges exige que toute correction automatique passe par un script
versionné dont la sortie est archivée, afin que chaque transformation puisse être
rejouée et auditée. C'est ce script.

UN CHOIX À CONNAÎTRE. babel-french sait poser lui-même les espaces devant la
ponctuation haute. Si la source les porte AUSSI, elles se cumulent et le texte
composé montre une double espace. Il faut donc choisir, et le choix est de les
mettre dans la source : l'EPUB n'a pas de babel, et une source correcte vaut
mieux qu'une source qui dépend de sa chaîne. Le gabarit désactive en conséquence
l'espacement automatique de babel.

Les règles appliquées, toutes conservatrices :

    espace fine insécable  avant ; ! ? et %, après « ouvrant, avant » fermant
    espace insécable       avant :, entre un nombre et son unité, après les
                           abréviations de civilité, entre une initiale et un nom
    tirets                 cadratin pour les incises, demi-cadratin entre deux
                           nombres formant un intervalle

Ce que le script ne fait pas : deviner. Il ne met pas en italique les mots
étrangers, qui demandent de juger au cas par cas, et il ne touche pas aux
sommes, dont l'écriture n'est pas uniforme dans le manuscrit.

Usage : python3 normaliser-typographie.py [--source src] [--verifier]
"""
import argparse
import re
import sys
from pathlib import Path

FINE = " "      # espace fine insécable
INSEC = " "     # espace insécable

CIVILITES = ("M.", "MM.", "Mme", "Mmes", "Dr", "Pr", "Me")

REGLES = [
    # Ponctuation haute : fine insécable devant ; ! ? et %, insécable devant :
    (re.compile(r"[   ]*([;!?%])"), FINE + r"\1"),
    (re.compile(r"[   ]*:(?=\s|$)"), INSEC + ":"),
    # Guillemets français : insécable intérieure des deux côtés
    (re.compile(r"«[   ]*"), "«" + FINE),
    (re.compile(r"[   ]*»"), FINE + "»"),
    # Un nombre et son unité ne se séparent pas. Le pour-cent n'est pas ici :
    # la première règle lui a déjà donné sa fine, qui est l'usage français.
    (re.compile(r"(\d)[   ]+(€|\$|FC|CDF|km|kg|m²|h|j|jours?|mois|ans?)\b"),
     r"\1" + INSEC + r"\2"),
    # Milliers : l'espace qui les sépare est fine et insécable
    (re.compile(r"(\d)[  ](\d{3})(?!\d)"), r"\1" + FINE + r"\2"),
    # Intervalle de nombres : demi-cadratin, sans espaces
    (re.compile(r"(\d)\s*[-—]\s*(\d)"), r"\1–\2"),
    # Une initiale ne se sépare pas du nom qu'elle annonce
    (re.compile(r"\b([A-ZÉÈÀ])\.[ ]+(?=[A-ZÉÈÀ])"), r"\1." + INSEC),
]


TITRE = re.compile(r'titre="([^"]*)"')


def regles(texte):
    """Les règles, appliquées à un fragment de prose."""
    for motif, remplacement in REGLES:
        texte = motif.sub(remplacement, texte)
    for civilite in CIVILITES:
        texte = texte.replace(civilite + " ", civilite + INSEC)
    return texte


def normaliser(texte):
    """Applique les règles hors des blocs qui ne sont pas de la prose."""
    sortie, dans_schema = [], False
    for ligne in texte.split("\n"):
        if ligne.startswith("```"):
            dans_schema = not dans_schema
            sortie.append(ligne)
            continue
        # Un schéma est un dessin : ses espaces sont sa géométrie. Une ouverture
        # d'encadré et un marqueur de partie portent des attributs, pas du texte.
        # Les cellules de tableau, elles, sont de la prose et se normalisent :
        # aucune règle ne touche à un caractère autre qu'une espace, la barre
        # verticale et la ligne d'alignement traversent donc intactes.
        if dans_schema or ligne.startswith("<!--"):
            sortie.append(ligne)
            continue
        # L'ouverture d'un encadré porte des attributs, sauf un : son titre est
        # de la prose et se normalise comme le reste, sans quoi les encadrés
        # seraient les seuls endroits du livre où « : » n'a pas son insécable.
        if ligne.startswith(":::"):
            sortie.append(TITRE.sub(lambda m: 'titre="%s"' % regles(m.group(1)),
                                    ligne))
            continue
        sortie.append(regles(ligne))
    return "\n".join(sortie)


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--source", type=Path, default=Path("src"))
    analyseur.add_argument("--verifier", action="store_true",
                           help="n'écrit rien, dénombre ce qui serait changé")
    options = analyseur.parse_args()

    total = 0
    for fichier in sorted(options.source.glob("*.md")):
        avant = fichier.read_text(encoding="utf-8")
        apres = normaliser(avant)
        changements = sum(1 for a, b in zip(avant.split("\n"), apres.split("\n")) if a != b)
        total += changements
        if changements and not options.verifier:
            fichier.write_text(apres, encoding="utf-8")
        if changements:
            print(f"  {fichier.name:<52} {changements:>4} ligne(s)")
    print(f"\n{'à corriger' if options.verifier else 'corrigées'} : {total} lignes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
