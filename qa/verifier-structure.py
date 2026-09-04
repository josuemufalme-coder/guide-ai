#!/usr/bin/env python3
"""Contrôle de structure de la reconstitution — phase 0.

Le contrôle d'intégrité compte les signes : il prouve qu'aucun mot n'est perdu.
Il ne dit rien de la façon dont ces mots sont agencés. Or les deux défauts
trouvés au chapitre 2 ne perdaient aucun mot : un titre fabriqué au milieu d'une
phrase en gras, deux paragraphes fusionnés à un saut de page. Une relecture les
attrape mal, et sur seize chapitres elle en laissera passer.

Ce contrôle compare donc, chapitre par chapitre, ce que le PDF porte et ce que
le Markdown en a fait :

    sections      lignes de 11,96 pt         contre  titres `##`
    paragraphes   blocs de corps             contre  paragraphes
    items         puces et numéros           contre  `- ` et `1. `
    encadrés      titres d'encadré en gras   contre  `::: {.encadre`
    tableaux      régions tabulaires         contre  tableaux Markdown
    notes         appels en exposant         contre  `[^n]`
    schémas       lignes en chasse fixe      contre  blocs ```schema

Il vérifie en outre que chaque ligne de schéma tient dans la justification : un
bloc en chasse fixe qui déborde la mesure est le défaut même de la page 27 du
PDF d'origine, et rien n'empêche de le réintroduire sans un contrôle.

Tout écart est une anomalie à examiner : soit la reconstitution s'est trompée,
soit le livre lui-même porte une irrégularité qu'il faut connaître.

Usage : python3 verifier-structure.py fichier.pdf [...] [--source src]
"""
import argparse
import importlib.util
import re
import sys
from pathlib import Path

RECONSTITUTEUR = Path(__file__).with_name("reconstituer.py")
_spec = importlib.util.spec_from_file_location("reconstitueur", RECONSTITUTEUR)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def attendu(blocs):
    """Ce que le PDF porte, unité par unité.

    Trois façons de compter doivent suivre ce que la reconstitution fait, sans
    quoi le contrôle signalerait comme anomalies ses propres décisions :

    - un encadré s'ouvre soit sur un titre en gras, soit sur son corps quand il
      n'a pas de titre : les deux comptent pour un encadré ;
    - un tableau qui déborde sur la page suivante y répète son en-tête et forme
      deux régions dans le PDF, un seul tableau dans le Markdown ;
    - les schémas ne laissent qu'un bloc d'attente, pas des paragraphes.
    """
    unites, courante = [], {"titre": "Liminaires", "compte": compteur()}
    precedent = None
    for rang, bloc in enumerate(blocs):
        suivant = blocs[rang + 1] if rang + 1 < len(blocs) else None
        if bloc.genre == "partie":
            continue
        if bloc.genre == "chapitre":
            unites.append(courante)
            courante = {"titre": bloc.texte(), "compte": compteur()}
            continue
        compte = courante["compte"]
        if bloc.genre == "section":
            compte["sections"] += 1
        elif bloc.genre == "schema":
            compte["schemas"].add(bloc.lignes[0].page)
        elif bloc.genre == "tableau":
            repete = (precedent is not None and precedent.genre == "tableau"
                      and precedent.lignes[0].texte_brut() == bloc.lignes[0].texte_brut())
            if not repete:
                compte["tableaux"] += 1
        elif bloc.genre == "encadre":
            ouvre = precedent is None or precedent.genre != "encadre"
            titre = R.est_titre_encadre(bloc, suivant)
            if titre:
                compte["encadres"] += 1
            elif ouvre:
                compte["encadres"] += 1
                compte["paragraphes"] += 1
            elif bloc.item:
                compte["items"] += 1
            else:
                compte["paragraphes"] += 1
        elif bloc.item:
            compte["items"] += 1
        else:
            compte["paragraphes"] += 1
        precedent = bloc
        compte["notes"] += sum(
            1 for l in bloc.lignes for f in l.fragments
            if f.hauteur <= R.HAUTEUR_APPEL_NOTE and f.texte.strip().isdigit())
    unites.append(courante)
    return unites


def compteur():
    return {"sections": 0, "paragraphes": 0, "items": 0, "encadres": 0,
            "tableaux": 0, "notes": 0, "schemas": set()}


def obtenu(chemin):
    """Ce que le Markdown en a fait."""
    texte = chemin.read_text(encoding="utf-8")
    compte = compteur()
    compte["sections"] = len(re.findall(r"^## ", texte, re.M))
    compte["encadres"] = len(re.findall(r"^::: \{\.encadre", texte, re.M))
    compte["schemas"] = set(re.findall(r"```schema page=(\d+)", texte))
    compte["notes"] = len(re.findall(r"\[\^\d+\]", texte))
    compte["items"] = len(re.findall(r"^(?:- |\d{1,2}\. )", texte, re.M))
    # Un tableau est un bloc de lignes commençant par « | » ; on compte les blocs.
    compte["tableaux"] = len(re.findall(r"(?:^\|.*\n)(?:^\|.*\n)+", texte, re.M))
    # Le tracé d'un schéma n'est pas de la prose : il ne compte pas en paragraphes.
    sans_schema = re.sub(r"```schema.*?```", " ", texte, flags=re.S)
    ordinaire = re.compile(r"^(?!#|:::|\||- |\d{1,2}\. |<!--)\S")
    compte["paragraphes"] = sum(1 for l in sans_schema.split("\n") if ordinaire.match(l))
    return compte


PT_MM = 25.4 / 72
CHASSE = 0.6          # avance d'une chasse fixe classique, en cadratins
JUSTIFICATION_ACTUELLE, CORPS_ACTUEL = 111.5, 9.96
JUSTIFICATION_CIBLE, CORPS_CIBLE = 105, 11      # bas de la fourchette de la phase 1


def capacite(justification_mm, corps_pt):
    return int(justification_mm / (corps_pt * CHASSE * PT_MM))


def largeur_des_schemas(dossier):
    """Contrôle que chaque ligne de schéma tient dans la mesure."""
    actuelle = capacite(JUSTIFICATION_ACTUELLE, CORPS_ACTUEL)
    cible = capacite(JUSTIFICATION_CIBLE, CORPS_CIBLE)
    print(f"\nschémas — capacité d'un bloc en chasse fixe : {actuelle} signes"
          f" aujourd'hui, {cible} après la phase 1")
    debordements = 0
    for fichier in sorted(dossier.glob("*.md")):
        for bloc in re.finditer(r"```schema page=(\d+)\n(.*?)```", fichier.read_text(
                encoding="utf-8"), re.S):
            page, trace = bloc.group(1), bloc.group(2).rstrip("\n").split("\n")
            large = max(len(l) for l in trace)
            verdict = ("déborde de %d" % (large - actuelle) if large > actuelle
                       else "tient" if large <= cible
                       else "tient aujourd'hui, débordera de %d" % (large - cible))
            print(f"  page {page:>3} : {large:>2} signes — {verdict}")
            debordements += large > actuelle
    return debordements


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("pdfs", nargs="+", type=Path)
    analyseur.add_argument("--source", type=Path, default=Path("src"))
    options = analyseur.parse_args()

    pages = R.lire_pages(options.pdfs)
    unites_md, _ = R.rendre(R.assembler(pages))
    unites_pdf = attendu(R.assembler(pages))

    cles = ["sections", "paragraphes", "items", "encadres", "tableaux", "notes"]
    entete = "  ".join(f"{c[:5]:>7}" for c in cles)
    print(f"{'chapitre':<44} {entete}   schémas")
    anomalies = 0
    for rang, (unite, attend) in enumerate(zip(unites_md, unites_pdf)):
        nom = R.nom_de_fichier(unite, rang)
        fichier = options.source / nom
        if not fichier.exists():
            print(f"  {nom:<42} ABSENT")
            anomalies += 1
            continue
        obtient = obtenu(fichier)
        ligne, ecarts = [], []
        for cle in cles:
            a, o = attend["compte"][cle], obtient[cle]
            ligne.append(f"{o:>3}/{a:<3}" if a != o else f"{o:>3}    ")
            if a != o:
                ecarts.append(f"{cle} {o} au lieu de {a}")
        schemas_a = {str(p) for p in attend["compte"]["schemas"]}
        if schemas_a != obtient["schemas"]:
            ecarts.append(f"schémas {sorted(obtient['schemas'])} au lieu de {sorted(schemas_a)}")
        marque = "  ← " + " ; ".join(ecarts) if ecarts else ""
        print(f"  {nom:<42} {'  '.join(ligne)}   {sorted(schemas_a) or ''}{marque}")
        anomalies += bool(ecarts)

    anomalies += largeur_des_schemas(options.source)
    print("\nLecture : « obtenu/attendu » quand les deux diffèrent, sinon la valeur seule.")
    print("structure : " + ("CONFORME" if not anomalies
                            else f"{anomalies} chapitre(s) à examiner"))
    return 0 if not anomalies else 1


if __name__ == "__main__":
    sys.exit(main())
