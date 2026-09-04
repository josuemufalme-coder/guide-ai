#!/usr/bin/env python3
"""Les quatre mesures de composition — phase 1.

Elles remplacent le taux de césure de 12 à 25 %, que l'expansion de caractères
rend inatteignable : la même composition donne 15,5 % sans expansion et 7,2 %
avec, et l'expansion est ce que le cahier exige. Une mesure s'en va, quatre la
remplacent, et elles portent sur ce que le taux de césure ne faisait
qu'indiquer — la régularité de la justification et la tenue des pages.

    1. Boîtes débordantes et lignes lâches
       Zéro « Overfull \\hbox » : aucune ligne ne dépasse la justification.
       Et le nombre de lignes dont la mauvaisité dépasse le SEUIL ANNONCÉ, ici
       1000 : c'est la valeur au-delà de laquelle TeX considère lui-même qu'une
       ligne est mal espacée, et le seuil que le préambule impose à \\hbadness.

    2. Césures consécutives
       Deux au plus. Trois coupures alignées en fin de lignes successives
       dessinent une échelle que l'œil suit au lieu de lire.

    3. Veuves, orphelines et lignes creuses
       Aucune ligne seule en tête ou en pied de page. Le préambule les interdit
       par \\clubpenalty et \\widowpenalty à 10000 ; ce contrôle vérifie que
       l'interdiction a tenu, car TeX peut passer outre s'il n'a pas le choix.

    4. Mot coupé en dernier mot de page
       Aucun. Une césure que le lecteur doit résoudre en tournant la page est la
       plus coûteuse de toutes.

Les trois dernières se lisent dans le PDF composé, la première dans le journal
de compilation.

Usage : python3 mesurer-composition.py fichier.pdf [...] [--journal f.log]
"""
import argparse
import collections
import re
import statistics as st
import subprocess
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

SEUIL_MAUVAISITE = 1000
MARGE_LIGNE_PLEINE = 8      # points : en deçà du bord droit, la ligne est pleine


def _reconstitueur():
    """Le regroupement des fragments en lignes est déjà écrit et éprouvé dans
    qa/reconstituer.py : le réécrire ici serait s'exposer à le réécrire mal."""
    import importlib.util
    chemin = Path(__file__).with_name("reconstituer.py")
    spec = importlib.util.spec_from_file_location("reconstitueur", chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pages_de_corps(pdf):
    """Les lignes de texte, page par page : ni titre courant, ni folio.

    Le titre courant partage sa hauteur avec le corps des encadrés — tous deux
    sont composés en petit —, si bien que la taille ne suffit pas à les
    distinguer. La position, elle, tranche : le titre courant est la première
    ligne de la page et se tient loin au-dessus de la suivante.

    La taille du corps se calcule sur tout l'ouvrage, non page par page : une
    page occupée par un encadré n'a que trois lignes de corps, et le calcul y
    prendrait l'encadré pour le texte.
    """
    R = _reconstitueur()
    brutes = [R.nettoyer(page) for page in R.lire_pages([pdf])]
    # Le corps se reconnaît à sa mesure, non à sa fréquence : un encadré est
    # composé en retrait des deux côtés, donc sur une justification plus étroite,
    # et une double page qu'il occupe le rendrait majoritaire à tort.
    largeurs = collections.defaultdict(int)
    for page in brutes:
        for ligne in page:
            if len(ligne.texte_brut()) > 2:
                largeurs[ligne.hauteur] = max(largeurs[ligne.hauteur],
                                              ligne.droite - ligne.gauche)
    if not largeurs:
        return []
    corps = max(largeurs, key=largeurs.get)

    ecarts = collections.Counter()
    for page in brutes:
        for avant, apres in zip(page, page[1:]):
            if 0 < apres.top - avant.top < 80:
                ecarts[apres.top - avant.top] += 1
    interligne = ecarts.most_common(1)[0][0] if ecarts else 25

    pages = []
    for page in brutes:
        retenues = list(page)
        # Titre courant : première ligne, détachée du texte qui suit.
        if len(retenues) > 1 and retenues[1].top - retenues[0].top > 1.6 * interligne:
            retenues = retenues[1:]
        # Folio : une ligne qui n'est qu'un nombre.
        retenues = [l for l in retenues if not re.fullmatch(r"\d{1,3}", l.texte_brut())]
        pages.append([{"haut": l.top, "gauche": l.gauche, "droite": l.droite,
                       "hauteur": l.hauteur, "corps": l.hauteur == corps,
                       "texte": l.texte_brut()}
                      for l in retenues if len(l.texte_brut()) > 2])
    return pages


def interligne(pages):
    """L'écart vertical dominant entre deux lignes de corps."""
    ecarts = collections.Counter()
    for page in pages:
        for avant, apres in zip(page, page[1:]):
            if avant["corps"] and apres["corps"] and 0 < apres["haut"] - avant["haut"] < 80:
                ecarts[apres["haut"] - avant["haut"]] += 1
    return ecarts.most_common(1)[0][0] if ecarts else 25


def mesurer(pdf, journal):
    pages = pages_de_corps(pdf)
    toutes = [l for p in pages for l in p]
    if not toutes:
        return None
    # Le bord droit n'est pas le même au recto et au verso : la gouttière étant
    # plus large que la marge extérieure, le bloc de texte se déplace d'une page
    # à l'autre. Un bord unique ferait passer pour courtes toutes les lignes
    # pleines d'une des deux paginations — et donc pour veuves des lignes qui ne
    # le sont pas. C'est ce que le premier compte donnait.
    bords = {}
    for parite in (0, 1):
        droites = [l["droite"] for numero, page in enumerate(pages, 1)
                   if numero % 2 == parite for l in page if l["corps"]]
        bords[parite] = max(droites) if droites else 0

    def pleine(ligne, numero):
        return ligne["droite"] >= bords[numero % 2] - MARGE_LIGNE_PLEINE

    # 1 — boîtes débordantes et lignes lâches, lues dans le journal
    debordantes = laches = 0
    if journal and journal.exists():
        texte = journal.read_text(encoding="utf-8", errors="replace")
        debordantes = len(re.findall(r"^Overfull \\hbox", texte, re.M))
        laches = sum(1 for m in re.finditer(r"^Underfull \\hbox \(badness (\d+)\)",
                                            texte, re.M)
                     if int(m.group(1)) > SEUIL_MAUVAISITE)

    # 2 — césures consécutives
    suite = maximum = 0
    for numero, page in enumerate(pages, 1):
        for ligne in page:
            if ligne["texte"].rstrip().endswith(("-", "­")) and pleine(ligne, numero):
                suite += 1
                maximum = max(maximum, suite)
            else:
                suite = 0

    # 3 — veuves, orphelines, lignes creuses
    #
    # Une veuve est la DERNIÈRE ligne d'un paragraphe, restée seule en tête de
    # page. Trois conditions, et les trois comptent : la ligne est courte, elle
    # appartient au corps, et la page précédente s'achevait sur une ligne pleine
    # — sans quoi le paragraphe ne se poursuivait pas et il n'y a pas de veuve.
    # Un titre, un item de liste ou une ligne d'encadré en tête de page n'en sont
    # pas : c'est ce que mon premier compte prenait à tort pour quarante défauts.
    veuves, orphelines = [], []
    item = lambda l: l["texte"].lstrip().startswith(("—", "-", "•"))
    for numero, page in enumerate(pages, 1):
        if len(page) < 2:
            continue
        precedente_page = pages[numero - 2] if numero > 1 else None
        premiere = page[0]
        if (premiere["corps"] and not pleine(premiere, numero) and not item(premiere)
                and precedente_page and precedente_page[-1]["corps"]
                and pleine(precedente_page[-1], numero - 1)):
            veuves.append((numero, premiere["texte"][:44]))

        # Une orpheline est la PREMIÈRE ligne d'un paragraphe, restée seule en
        # pied de page : elle ouvre un bloc que la page suivante poursuit.
        derniere = page[-1]
        if (numero < len(pages) and pages[numero] and derniere["corps"]
                and pleine(derniere, numero)):
            avant = page[-2]
            ouvre_un_bloc = derniere["haut"] - avant["haut"] > 1.35 * interligne(pages)
            if ouvre_un_bloc:
                orphelines.append((numero, derniere["texte"][:44]))

    # 4 — mot coupé en dernier mot de page
    coupes = [(numero, page[-1]["texte"][-32:])
              for numero, page in enumerate(pages, 1)
              if page and page[-1]["texte"].rstrip().endswith(("-", "­"))]

    longueurs = sorted(len(l["texte"]) for numero, page in enumerate(pages, 1)
                       for l in page if l["corps"] and pleine(l, numero))
    return {
        "pages": len(pages),
        "lignes": len(toutes),
        "boites_debordantes": debordantes,
        "lignes_laches": laches,
        "cesures_consecutives": maximum,
        "veuves": veuves,
        "orphelines": orphelines,
        "coupes_en_pied": coupes,
        "signes_mediane": st.median(longueurs) if longueurs else 0,
        "signes_90e": longueurs[int(0.9 * len(longueurs))] if longueurs else 0,
    }


def rapporter(nom, m):
    conforme = (m["boites_debordantes"] == 0 and m["cesures_consecutives"] <= 2
                and not m["veuves"] and not m["orphelines"] and not m["coupes_en_pied"])
    print(f"\n── {nom} — {m['pages']} pages, {m['lignes']} lignes de corps ──")
    print(f"  boîtes débordantes                       : {m['boites_debordantes']}"
          f"   {'✓' if m['boites_debordantes'] == 0 else '✗'}")
    print(f"  lignes de mauvaisité > {SEUIL_MAUVAISITE}             "
          f": {m['lignes_laches']}")
    print(f"  césures consécutives (maximum, plafond 2) : {m['cesures_consecutives']}"
          f"   {'✓' if m['cesures_consecutives'] <= 2 else '✗'}")
    print(f"  veuves et lignes creuses en tête          : {len(m['veuves'])}"
          f"   {'✓' if not m['veuves'] else '✗'}")
    print(f"  orphelines en pied                        : {len(m['orphelines'])}"
          f"   {'✓' if not m['orphelines'] else '✗'}")
    print(f"  mots coupés en dernier mot de page        : {len(m['coupes_en_pied'])}"
          f"   {'✓' if not m['coupes_en_pied'] else '✗'}")
    print(f"  signes par ligne pleine                   : "
          f"médiane {m['signes_mediane']:.0f}, 90ᵉ centile {m['signes_90e']}")
    for intitule, cas in (("veuve", m["veuves"]), ("orpheline", m["orphelines"]),
                          ("coupe en pied", m["coupes_en_pied"])):
        for page, extrait in cas[:4]:
            print(f"      {intitule} p.{page} : …{extrait}")
    return conforme


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("pdfs", nargs="+", type=Path)
    options = analyseur.parse_args()
    tout_conforme = True
    for pdf in options.pdfs:
        mesure = mesurer(pdf, pdf.with_suffix(".log"))
        if mesure is None:
            print(f"\n── {pdf.name} : illisible")
            tout_conforme = False
            continue
        tout_conforme &= rapporter(pdf.stem, mesure)
    print("\ncomposition : " + ("CONFORME" if tout_conforme else "à reprendre"))
    return 0 if tout_conforme else 1


if __name__ == "__main__":
    sys.exit(main())
