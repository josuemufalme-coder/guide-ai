#!/usr/bin/env python3
"""Contrôle des filets d'encadré sur le PDF composé.

Un encadré à filets s'ouvre par un trait et se ferme par un autre. Rien ne
garantit qu'ils restent ensemble : le filet de tête s'est retrouvé seul au pied
d'une page, la suite de l'encadré passant à la page d'après, et le PDF n'en
disait rien — c'est un trait, pas un caractère, aucune extraction de texte ne
le voit.

Le contrôle rend donc le PDF en niveaux de gris et cherche les lignes de pixels
qui traversent la justification. Il compte les traits pleine mesure, les
apparie dans l'ordre des pages, et signale ceux qui restent seuls.

Usage : python3 controler-filets.py chemin.pdf --attendus 30
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def traits_de_la_page(pgm, largeur_minimale, seuil_de_gris):
    """Les ordonnées des filets d'encadré de la page.

    Un filet d'encadré et un filet de tableau traversent tous deux la
    justification : la largeur ne les distingue pas. Leur gris, si. Le filet
    d'encadré est posé à 55 % de noir, les filets de booktabs sont noirs. On ne
    retient donc que les traits clairs.
    """
    with pgm.open("rb") as fichier:
        assert fichier.readline().strip() == b"P5"
        ligne = fichier.readline()
        while ligne.startswith(b"#"):
            ligne = fichier.readline()
        largeur, hauteur = map(int, ligne.split())
        fichier.readline()
        pixels = fichier.read()
    trouves, precedent = [], -9
    for y in range(hauteur):
        rangee = pixels[y * largeur:(y + 1) * largeur]
        sombres = [p for p in rangee if p < 245]
        if len(sombres) < largeur_minimale:
            continue
        if sum(sombres) / len(sombres) < seuil_de_gris:
            continue  # un filet noir : c'est un tableau, pas un encadré
        # Un trait fait une ou deux rangées de pixels : on ne le compte
        # qu'une fois.
        if y - precedent > 3:
            trouves.append(y)
        precedent = y
    return trouves


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("pdf", type=Path)
    analyseur.add_argument("--resolution", type=int, default=150)
    analyseur.add_argument("--justification", type=float, default=105.0,
                           help="largeur du bloc de texte, en millimètres")
    analyseur.add_argument("--seuil-de-gris", type=int, default=80,
                           help="au-dessus, le trait est clair : un filet d'encadré")
    analyseur.add_argument("--attendus", type=int, default=None,
                           help="nombre d'encadrés à filets attendu")
    options = analyseur.parse_args()

    # Un filet pleine mesure occupe la justification entière ; on l'exige à 95 %
    # pour ne pas confondre avec un filet de tableau, plus court.
    minimum = int(options.justification / 25.4 * options.resolution * 0.95)

    total, par_page = 0, []
    with tempfile.TemporaryDirectory() as dossier:
        subprocess.run(["pdftoppm", "-r", str(options.resolution), "-gray",
                        str(options.pdf), str(Path(dossier) / "p")], check=True)
        for pgm in sorted(Path(dossier).glob("p-*.pgm")):
            numero = int(pgm.stem.split("-")[-1])
            traits = traits_de_la_page(pgm, minimum, options.seuil_de_gris)
            total += len(traits)
            if traits:
                par_page.append((numero, len(traits)))

    # Un encadré qui traverse une coupure laisse son filet de tête sur une page
    # et son filet de pied sur la suivante : deux pages impaires consécutives
    # sont donc un encadré normal, une page impaire isolée est un filet orphelin.
    impaires = [n for n, k in par_page if k % 2]
    appariees = {n for n in impaires if n - 1 in impaires or n + 1 in impaires}
    orphelins = [n for n in impaires if n not in appariees]
    print(f"\n── {options.pdf.name} ──")
    print(f"  filets pleine mesure                : {total}")
    print(f"  encadrés à cheval sur deux pages    : {len(appariees) // 2}"
          + ("" if not appariees else "   " + ", ".join(
              f"p.{n}–{n+1}" for n in sorted(appariees) if n + 1 in appariees)))
    print(f"  filets orphelins                    : {len(orphelins)}"
          + ("" if not orphelins else "   " + ", ".join(f"p.{n}" for n in orphelins)))
    if options.attendus is not None:
        print(f"  encadrés à filets attendus          : {options.attendus}"
              f" — soit {2 * options.attendus} filets")
    bon = (not orphelins and total % 2 == 0
           and (options.attendus is None or total == 2 * options.attendus))
    print("\nfilets : " + ("CONFORME" if bon else "à reprendre"))
    return 0 if bon else 1


if __name__ == "__main__":
    sys.exit(main())
