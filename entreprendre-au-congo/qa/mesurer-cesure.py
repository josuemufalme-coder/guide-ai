#!/usr/bin/env python3
"""Mesure les critères de sortie de la phase 1 sur un corpus étendu.

Le cahier des charges fixe deux critères chiffrés : taux de césure entre 12 % et
25 %, et zéro ponctuation haute rejetée en début de ligne. Une double page ne
suffit pas à les établir — une cinquantaine de lignes donne un taux dont
l'intervalle de confiance couvre toute la fourchette. Ce script compose neuf
chapitres, soit près de dix mille mots, et mesure sur ce corpus.

Les chapitres portant un tableau ou un schéma sont écartés : le convertisseur du
spécimen ne les traite pas, et ils ne changent rien à un taux de césure.
"""
import argparse
import importlib.util
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "style"))
from gabarit import POLICES                                     # noqa: E402

_s = importlib.util.spec_from_file_location("mesure", RACINE / "qa" / "mesure-typo.py")
MESURE = importlib.util.module_from_spec(_s); _s.loader.exec_module(MESURE)
_c = importlib.util.spec_from_file_location("comp", RACINE / "qa" / "composer-specimen.py")
COMP = importlib.util.module_from_spec(_c); _c.loader.exec_module(COMP)

SANS_TABLEAU_NI_SCHEMA = [
    "01-developper-une-vision-pour-son-entreprise",
    "04-une-entreprise-orientee-vers-le-marche",
    "06-le-produit-et-lavantage-concurrentiel",
    "07-fixer-le-cap",
    "11-separer-largent-de-lentreprise-et-largent-du",
    "12-fixer-ses-prix",
    "14-la-comptabilite-et-le-controle-de-gestion",
    "15-surmonter-les-obstacles",
    "16-le-plan-daffaires",
]


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--source", type=Path, default=Path("src"))
    analyseur.add_argument("--sortie", type=Path, default=Path("build/cesure"))
    options = analyseur.parse_args()
    options.sortie.mkdir(parents=True, exist_ok=True)

    corps = "\n\n\\clearpage\n\n".join(
        COMP.corps_du_specimen(options.source / f"{nom}.md", None)
        for nom in SANS_TABLEAU_NI_SCHEMA)
    mots = len(corps.split())
    print(f"corpus : {len(SANS_TABLEAU_NI_SCHEMA)} chapitres, environ {mots} mots\n")
    print(f"{'police':<20} {'corps':>7} {'lignes':>7} {'césure':>8} "
          f"{'signes':>7} {'ponct. haute':>13}")
    for clef, police in POLICES.items():
        pdf = COMP.composer(clef, police, corps, options.sortie, "Entreprendre au Congo")
        if not pdf:
            continue
        m = MESURE.metriques_de_ligne(MESURE.texte_par_lignes([str(pdf)]))
        verdict = "" if 12 <= m["taux_cesure_pct"] <= 25 else "   ← hors cible"
        print(f"  {police['nom']:<18} {police['corps']:>5} pt {m['lignes_de_texte']:>7} "
              f"{m['taux_cesure_pct']:>7.2f}% {m['signes_par_ligne_90e']:>7} "
              f"{m['ponctuation_haute_rejetee']:>13}{verdict}")


if __name__ == "__main__":
    main()
