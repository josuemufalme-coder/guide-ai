#!/usr/bin/env python3
"""Assemblage du livrable unique — phase 9.

Un seul fichier : la première de couverture, l'intérieur, la quatrième.

Toutes les pages sortent au même format, 154 × 216 mm, avec un fond perdu de
3 mm sur les quatre côtés et une boîte de rognage à 148 × 210 mm. La couverture
porte déjà ce fond perdu — son décor s'imprime jusqu'au bord et doit être coupé
dedans. Les pages d'intérieur ne portent rien qui aille au bord ; leur boîte
support est simplement élargie autour de la page rognée, sans déplacer un seul
signe : le contenu ne bouge pas, c'est le cadre qui grandit. L'imprimeur reçoit
donc un fichier d'un seul format, ce qu'il demande, et une coupe déclarée là où
elle doit tomber.

Usage : python3 assembler-livre.py [--couverture …] [--interieur …] [--sortie …]
"""
import argparse
import sys
from pathlib import Path

MM = 72 / 25.4
FOND_PERDU = 3 * MM


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--couverture", type=Path,
                           default=Path("build/couverture/ENTREPRENDRE-AU-CONGO-premiere.pdf"))
    analyseur.add_argument("--quatrieme", type=Path,
                           default=Path("build/couverture/ENTREPRENDRE-AU-CONGO-quatrieme.pdf"))
    analyseur.add_argument("--interieur", type=Path,
                           default=Path("build/livre/ENTREPRENDRE-AU-CONGO-interieur.pdf"))
    analyseur.add_argument("--sortie", type=Path,
                           default=Path("build/livrable/ENTREPRENDRE-AU-CONGO.pdf"))
    options = analyseur.parse_args()

    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import RectangleObject

    couverture = PdfReader(str(options.couverture))
    quatrieme = PdfReader(str(options.quatrieme))
    interieur = PdfReader(str(options.interieur))
    ecrivain = PdfWriter()

    for page in couverture.pages:
        ecrivain.add_page(page)
    for page in interieur.pages:
        rogne = tuple(float(v) for v in page.mediabox)
        support = (rogne[0] - FOND_PERDU, rogne[1] - FOND_PERDU,
                   rogne[2] + FOND_PERDU, rogne[3] + FOND_PERDU)
        page.mediabox = RectangleObject(support)
        page.cropbox = RectangleObject(support)
        page.bleedbox = RectangleObject(support)
        page.trimbox = RectangleObject(rogne)
        ecrivain.add_page(page)
    for page in quatrieme.pages:
        ecrivain.add_page(page)

    ecrivain.add_metadata({
        "/Title": "Entreprendre au Congo — Comprendre l'entrepreneuriat "
                  "et savoir par où commencer",
        "/Author": "Ruth ZADI Pukuta",
        "/Subject": "Création et conduite d'une entreprise "
                    "en République démocratique du Congo",
        "/Creator": "LuaLaTeX, classe memoir",
    })

    options.sortie.parent.mkdir(parents=True, exist_ok=True)
    with options.sortie.open("wb") as fichier:
        ecrivain.write(fichier)

    print(f"  couverture : {len(couverture.pages)} page,"
          f" quatrième : {len(quatrieme.pages)} page")
    print(f"  intérieur  : {len(interieur.pages)} pages")
    print(f"  livrable   : {options.sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
