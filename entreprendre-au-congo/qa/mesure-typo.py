#!/usr/bin/env python3
"""Mesures typographiques sur un PDF composé — « Entreprendre au Congo ».

Sert deux fois : à contrôler les constats de l'audit sur le PDF existant,
puis à établir les critères de sortie chiffrés de la phase 1
(taux de césure entre 12 % et 25 %, zéro ponctuation haute rejetée).

DÉFINITIONS RETENUES — le cahier des charges ne les donne pas, et sans elles
le critère de sortie de la phase 1 n'est pas opposable. Elles valent tant
qu'elles ne sont pas amendées par écrit.

  ligne de texte    Ligne d'au moins 25 signes dans la sortie `pdftotext -layout`,
                    hors table des matières (repérée aux points de conduite).

  ligne césurée     Ligne de texte terminée par U+002D ou U+00AD dont le tiret
                    n'est PAS un trait d'union préexistant. Le test porte sur le
                    premier mot de la ligne suivante : « écoutez-|le »,
                    « Faudra-|t-il », « sous-|estimée » sont des coupures
                    d'aubaine sur un trait d'union du texte, pas des césures.
                    TeX les pratique même sans motifs de césure chargés ; les
                    compter fausse la mesure vers le haut — c'est l'erreur que
                    contient l'audit initial, qui annonce 0,7 % là où le taux
                    réel est nul.

  ponctuation       Ligne commençant par ; : ! ? ou », c'est-à-dire séparée
  haute rejetée     du mot qu'elle suit par une fin de ligne.

La géométrie (corps, interlignage, marges, justification) est lue dans le PDF
lui-même ; le comptage des lignes passe par `pdftotext`, dont l'extraction
préserve les espaces là où `pypdf` les perd sur du texte très justifié.

Usage : python3 mesure-typo.py fichier.pdf [fichier2.pdf ...]
Prérequis : poppler-utils (pdftotext), pypdf.
"""
import collections
import re
import statistics as st
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore")
from pypdf import PdfReader

PT_MM = 25.4 / 72
PONCTUATION_HAUTE = set(";:!?»")
LONGUEUR_MINIMALE = 25
POINTS_DE_CONDUITE = ". . ."

# Seconds éléments de mots composés courants. Si la ligne suivante commence par
# l'un d'eux, le tiret de fin de ligne est un trait d'union du texte.
SECONDS_ELEMENTS = {
    "je", "tu", "il", "ils", "elle", "elles", "on", "nous", "vous",
    "le", "la", "les", "lui", "leur", "y", "en", "ci", "là", "moi", "toi",
    "même", "mêmes", "être", "ce", "t", "t-il", "t-elle", "t-on",
}

# Premiers éléments de mots composés : « sous-|utilisée », « non-|dit ».
PREMIERS_ELEMENTS = {
    "sous", "sur", "non", "demi", "mi", "auto", "anti", "contre", "entre",
    "arrière", "avant", "après", "ex", "pseudo", "semi", "extra", "inter",
    "intra", "post", "pré", "re", "quasi", "porte", "grand", "petit", "tout",
}


def texte_par_lignes(pdfs):
    """Lignes de texte du document, via pdftotext -layout."""
    lignes = []
    for pdf in pdfs:
        sortie = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", pdf, "-"],
            capture_output=True, text=True, check=True).stdout
        lignes.extend(l.rstrip() for l in sortie.split("\n"))
    return lignes


def geometrie(pdfs):
    """Corps, interlignage et marges, lus dans les matrices du PDF."""
    pages = []
    for pdf in pdfs:
        for page in PdfReader(pdf).pages:
            frags = []

            def visite(texte, cm, tm, police, taille, frags=frags):
                if not texte or not texte.strip():
                    return
                x = tm[4] * cm[0] + tm[5] * cm[2] + cm[4]
                y = tm[4] * cm[1] + tm[5] * cm[3] + cm[5]
                frags.append((x, y, round(taille, 2), texte))

            page.extract_text(visitor_text=visite)
            par_y = collections.defaultdict(list)
            for x, y, taille, texte in frags:
                par_y[round(y)].append((x, taille, texte))
            pages.append([
                {"y": y,
                 "x0": min(i[0] for i in par_y[y]),
                 "x1": max(i[0] for i in par_y[y]),
                 "taille": st.median([i[1] for i in par_y[y]]),
                 "texte": "".join(i[2] for i in sorted(par_y[y]))}
                for y in sorted(par_y, reverse=True)
            ])

    poids = collections.Counter()
    for page in pages:
        for l in page:
            poids[l["taille"]] += len(l["texte"])
    corps = poids.most_common(1)[0][0]
    est_corps = lambda l: abs(l["taille"] - corps) < 0.05 and len(l["texte"]) > 15

    fer = {}
    bord = {}
    for parite, garde in (("recto", lambda i: i % 2), ("verso", lambda i: not i % 2)):
        x0 = [l["x0"] for i, p in enumerate(pages, 1) if garde(i) for l in p if est_corps(l)]
        x1 = [l["x1"] for i, p in enumerate(pages, 1) if garde(i) for l in p if est_corps(l)]
        fer[parite] = st.mode([round(v) for v in x0])
        bord[parite] = max(x1)

    ecarts = []
    for page in pages:
        corpsl = [l for l in page if est_corps(l)]
        for a, b in zip(corpsl, corpsl[1:]):
            if 0 < a["y"] - b["y"] < 30:
                ecarts.append(round(a["y"] - b["y"], 2))

    # Sur un recto la marge de gauche est la gouttière, sur un verso l'extérieure.
    return {
        "pages": len(pages),
        "corps_pt": corps,
        "interlignage_pt": st.mode(ecarts),
        "gouttiere_mm": round(fer["recto"] * PT_MM, 1),
        "exterieure_mm": round(fer["verso"] * PT_MM, 1),
        "justification_mm": round((bord["recto"] - fer["recto"]) * PT_MM, 1),
        "pages_blanches": [i for i, p in enumerate(pages, 1)
                           if not any(l["texte"].strip() for l in p)],
    }


def metriques_de_ligne(lignes):
    """Compte césures, coupures d'aubaine et ponctuation haute rejetée.

    Le voisinage se calcule sur la suite brute des lignes, pas sur les lignes
    retenues : une puce ou un titre intercalé ne doit pas faire passer pour
    césure une coupure dont le second élément se trouve juste en dessous.
    """
    retenue = lambda l: len(l.strip()) >= LONGUEUR_MINIMALE and POINTS_DE_CONDUITE not in l
    utiles = [l for l in lignes if retenue(l)]

    def mot_suivant(indice):
        for ligne in lignes[indice + 1:]:
            mots = ligne.strip().split()
            if mots:
                return mots[0].strip("«».,;:!?()•—-").lower()
        return ""

    cesures, aubaines, rejets = [], [], []
    for indice, ligne in enumerate(lignes):
        nue = ligne.strip()
        if not nue:
            continue
        if retenue(ligne) and nue.endswith(("-", "\u00ad")):
            premier = nue.rstrip("-\u00ad").split()[-1].strip("«»(,;:!?").lower()
            suite = mot_suivant(indice)
            compose = suite in SECONDS_ELEMENTS or premier in PREMIERS_ELEMENTS
            (aubaines if compose else cesures).append((nue[-48:], suite))
        if nue[0] in PONCTUATION_HAUTE and POINTS_DE_CONDUITE not in ligne:
            rejets.append(nue[:60])

    longueurs = sorted(len(l.strip()) for l in utiles)
    return {
        "lignes_de_texte": len(utiles),
        "lignes_cesurees": len(cesures),
        "taux_cesure_pct": round(100 * len(cesures) / len(utiles), 2) if utiles else 0.0,
        "coupures_aubaine": len(aubaines),
        "ponctuation_haute_rejetee": len(rejets),
        "signes_par_ligne_mediane": st.median(longueurs),
        "signes_par_ligne_90e": longueurs[int(0.9 * len(longueurs))],
        "_cesures": cesures[:12],
        "_aubaines": aubaines[:12],
        "_rejets": rejets[:12],
    }


def main(pdfs):
    resultat = geometrie(pdfs)
    resultat.update(metriques_de_ligne(texte_par_lignes(pdfs)))

    visibles = {k: v for k, v in resultat.items()
                if not k.startswith("_") and k != "pages_blanches"}
    largeur = max(len(k) for k in visibles)
    for cle, valeur in visibles.items():
        print(f"{cle:<{largeur}} : {valeur}")

    blanches = resultat["pages_blanches"]
    parite = "toutes paires" if all(p % 2 == 0 for p in blanches) else "PARITÉ MÊLÉE"
    print(f"\npages blanches ({len(blanches)}, {parite}) : {blanches}")

    for titre, cle in (("césures", "_cesures"),
                       ("coupures d'aubaine sur trait d'union", "_aubaines"),
                       ("ponctuation haute rejetée", "_rejets")):
        print(f"\n{titre} :")
        entrees = resultat[cle]
        if not entrees:
            print("  aucune")
        for entree in entrees:
            print(f"  {entree[0]}|{entree[1]}" if isinstance(entree, tuple) else f"  {entree!r}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
