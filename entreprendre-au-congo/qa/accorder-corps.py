#!/usr/bin/env python3
"""Accorde le corps de chaque police sur le compte de signes — phase 1.

Le cahier des charges pose trois cibles pour la phase 1 : justification de 100 à
105 mm, corps de 10,5 à 11 pt, et 60 à 66 signes par ligne. Elles ne peuvent pas
être tenues ensemble, et pas pour la raison qu'on croit.

Resserrer la justification retire des signes ; grossir le corps en retire aussi.
Mais changer de police en ajoute : DejaVu Serif, la police de repli du fichier
d'origine, est très large ; EB Garamond, Libertinus et Source Serif sont des
polices de labeur, donc étroites. À corps égal, elles logent bien plus de signes
sur la même mesure. Les deux effets se combattent, et le second l'emporte.

Ce script mesure au lieu de supposer : pour chaque police, il compose le même
texte à plusieurs corps et retient celui dont le compte de signes tombe dans la
fourchette visée. Le corps devient un résultat, pas un réglage.
"""
import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "style"))
sys.path.insert(0, str(RACINE / "qa"))
from gabarit import POLICES                                    # noqa: E402

_spec = importlib.util.spec_from_file_location("mesure", RACINE / "qa" / "mesure-typo.py")
MESURE = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MESURE)
_spec2 = importlib.util.spec_from_file_location("comp", RACINE / "qa" / "composer-specimen.py")
COMPOSITEUR = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(COMPOSITEUR)


def signes(pdf):
    """Le 90e centile des signes par ligne : la mesure d'une ligne pleine."""
    lignes = MESURE.texte_par_lignes([str(pdf)])
    return MESURE.metriques_de_ligne(lignes)["signes_par_ligne_90e"]


def accorder(clef, police, corps_tex, sortie, courant, cible, pas=0.25, essais=14):
    """Cherche le corps dont la ligne pleine tombe dans la fourchette."""
    bas, haut = cible
    corps, historique = police["corps"], []
    for _ in range(essais):
        essai = dict(police, corps=round(corps, 2))
        pdf = COMPOSITEUR.composer(clef, essai, corps_tex, sortie, courant)
        if pdf is None:
            return None, historique
        mesure = signes(pdf)
        historique.append((round(corps, 2), mesure))
        if bas <= mesure <= haut:
            return round(corps, 2), historique
        # Plus de signes qu'attendu : il faut grossir le corps, et l'inverse.
        corps += pas if mesure > haut else -pas
    return None, historique


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--chapitre", type=Path,
                           default=Path("src/01-developper-une-vision-pour-son-entreprise.md"))
    analyseur.add_argument("--sortie", type=Path, default=Path("build/accord"))
    analyseur.add_argument("--cible", type=int, nargs=2, default=(60, 66))
    options = analyseur.parse_args()

    options.sortie.mkdir(parents=True, exist_ok=True)
    corps_tex = COMPOSITEUR.corps_du_specimen(options.chapitre, "Réalité congolaise",
                                              "À quoi elle sert réellement")
    courant = "Chapitre 1 — Développer une vision"
    print(f"cible : {options.cible[0]} à {options.cible[1]} signes par ligne pleine\n")
    for clef, police in POLICES.items():
        corps, historique = accorder(clef, police, corps_tex, options.sortie,
                                     courant, tuple(options.cible))
        trace = " → ".join(f"{c} pt : {s}" for c, s in historique)
        verdict = f"{corps} pt" if corps else "hors d'atteinte"
        print(f"  {police['nom']:<18} {verdict:<16} {trace}")


if __name__ == "__main__":
    main()
