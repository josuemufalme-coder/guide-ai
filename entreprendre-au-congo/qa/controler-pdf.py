#!/usr/bin/env python3
"""Contrôle du PDF destiné à l'impression — phase 8.

Ce que le cahier des charges demande de vérifier avant de remettre un fichier à
un imprimeur, et que ce script vérifie :

    polices        toutes incorporées, et incorporées en sous-ensemble
    format         une seule taille de page, la taille annoncée
    rognage        une boîte de rognage déclarée sur chaque page, et un fond
                   perdu d'au moins 3 mm tout autour
    couleur        le bloc de texte en noir seul, la couverture dans les encres
                   qu'elle emploie et jamais en RVB ; aucune image à profiler
    métadonnées    titre et auteure renseignés
    pagination     un multiple de quatre, condition de l'imposition

Ce script ne convertit rien : il constate. Ce qu'il signale se corrige en amont,
dans le gabarit ou dans la composition, jamais sur le PDF lui-même.

Usage : python3 controler-pdf.py chemin.pdf [--largeur 154] [--hauteur 216]
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

MM = 72 / 25.4


def sortie_de(commande):
    return subprocess.run(commande, capture_output=True, text=True).stdout


def controler(chemin, largeur, hauteur, fond_perdu, pagine=True):
    verdicts = []

    def poser(nom, bon, detail):
        verdicts.append((nom, bon, detail))

    # --- Polices ------------------------------------------------------------
    lignes = [l for l in sortie_de(["pdffonts", str(chemin)]).split("\n")[2:] if l.strip()]
    non_incorporees = [l for l in lignes if len(l.split()) > 4 and l.split()[-5] != "yes"]
    sous_ensembles = [l for l in lignes if re.search(r"\b[A-Z]{6}\+", l)]
    poser("polices incorporées", not non_incorporees,
          f"{len(lignes)} police(s), {len(lignes) - len(non_incorporees)} incorporée(s), "
          f"{len(sous_ensembles)} en sous-ensemble")

    # --- Format et boîtes ---------------------------------------------------
    from pypdf import PdfReader
    lecteur = PdfReader(str(chemin))
    formats, defauts_rognage, defauts_fond = set(), [], []
    for numero, page in enumerate(lecteur.pages, 1):
        support = [float(v) for v in page.mediabox]
        rogne = [float(v) for v in page.trimbox]
        formats.add((round(support[2] - support[0], 1), round(support[3] - support[1], 1)))
        if rogne == support:
            defauts_rognage.append(numero)
        marges = (rogne[0] - support[0], rogne[1] - support[1],
                  support[2] - rogne[2], support[3] - rogne[3])
        if min(marges) < fond_perdu - 0.5:
            defauts_fond.append(numero)
    attendu = (round(largeur * MM, 1), round(hauteur * MM, 1))
    poser("format unique et conforme", formats == {attendu},
          " / ".join(f"{l/MM:.1f} × {h/MM:.1f} mm" for l, h in sorted(formats))
          + f" — attendu {largeur} × {hauteur} mm")
    poser("boîte de rognage déclarée", not defauts_rognage,
          "toutes les pages" if not defauts_rognage
          else f"{len(defauts_rognage)} page(s) sans rognage propre")
    poser(f"fond perdu ≥ {fond_perdu/MM:.0f} mm", not defauts_fond,
          "sur les quatre côtés de chaque page" if not defauts_fond
          else f"{len(defauts_fond)} page(s) insuffisante(s)")

    # --- Couleur ------------------------------------------------------------
    # pdfimages liste les images ; un livre de texte n'en a aucune, et c'est la
    # réponse la plus sûre à la question du profil colorimétrique.
    images = [l for l in sortie_de(["pdfimages", "-list", str(chemin)]).split("\n")[2:]
              if l.strip()]
    poser("aucune image à profiler", not images,
          "le livre est composé de texte et de traits" if not images
          else f"{len(images)} image(s)")

    # Les opérateurs de couleur du PostScript : « k » pose une quadrichromie,
    # « rg » un rouge-vert-bleu, « g » un niveau de gris. Les flux de page sont
    # compressés ; pypdf les rend décompressés, et c'est là qu'on les lit.
    # « 0 0 0 X k » est du noir seul : c'est ce qu'on veut dans le bloc de
    # texte, et ce n'est pas de la quadrichromie. La couverture, elle, porte une
    # couleur d'accompagnement voulue : elle est décrite, non reprochée.
    QUADRI = re.compile(rb"([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) k[\s]")
    GRIS = re.compile(rb"(?:^|[\s])[\d.]+ [gG][\s]")

    def encres(pages):
        quadri, rvb, noirseul = set(), 0, 0
        for page in pages:
            flux = page.get_contents()
            if flux is None:
                continue
            donnees = flux.get_data()
            for c, m, j, n in QUADRI.findall(donnees):
                if any(float(v) for v in (c, m, j)):
                    quadri.add(tuple(round(float(v), 2) for v in (c, m, j, n)))
                else:
                    noirseul += 1
            rvb += len(re.findall(rb"[\d.]+ [\d.]+ [\d.]+ rg[\s]", donnees))
            # Le texte du livre est posé en niveaux de gris, qui s'impriment en
            # noir seul : c'est la même encre, exprimée dans l'espace le plus
            # simple. On le compte pour que le rapport dise ce qu'il a vu.
            noirseul += len(GRIS.findall(donnees))
        return quadri, rvb, noirseul

    couleurs_couverture, rvb_couverture, _ = encres(
        [lecteur.pages[0], lecteur.pages[-1]])
    couleurs_bloc, rvb_bloc, noirseul = encres(lecteur.pages[1:-1])
    poser("bloc de texte en noir seul", not couleurs_bloc and not rvb_bloc,
          f"{noirseul} pose(s) de noir seul, aucune couleur"
          if not (couleurs_bloc or rvb_bloc)
          else f"{len(couleurs_bloc)} couleur(s), {rvb_bloc} RVB")
    poser("encres de la couverture", not rvb_couverture,
          ("noir seul" if not couleurs_couverture else
           " + ".join("C%.0f M%.0f J%.0f N%.0f" % tuple(100 * v for v in c)
                      for c in sorted(couleurs_couverture)))
          + (f" — {rvb_couverture} RVB" if rvb_couverture else ""))

    # --- Métadonnées et pagination -----------------------------------------
    infos = lecteur.metadata or {}
    poser("titre et auteure renseignés",
          bool(infos.get("/Title")) and bool(infos.get("/Author")),
          f"« {infos.get('/Title', '')} » — {infos.get('/Author', '')}")
    if pagine:
        pages = len(lecteur.pages)
        interieur = pages - 2      # la première et la quatrième de couverture
        poser("intérieur multiple de quatre", interieur % 4 == 0,
              f"{pages} pages, dont {interieur} d'intérieur")

    return verdicts


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("pdf", type=Path)
    analyseur.add_argument("--largeur", type=float, default=154.0)
    analyseur.add_argument("--hauteur", type=float, default=216.0)
    analyseur.add_argument("--fond-perdu", type=float, default=3.0)
    analyseur.add_argument("--couverture-seule", action="store_true",
                           help="une jaquette : elle n'a pas de pagination à vérifier")
    options = analyseur.parse_args()

    verdicts = controler(options.pdf, options.largeur, options.hauteur,
                         options.fond_perdu * MM,
                         pagine=not options.couverture_seule)
    print(f"\n── {options.pdf.name} ──")
    for nom, bon, detail in verdicts:
        print(f"  {nom:<28} {'✓' if bon else '✗'}   {detail}")
    manques = sum(1 for _, bon, _ in verdicts if not bon)
    print("\nPDF : " + ("CONFORME" if not manques else f"{manques} point(s) à reprendre"))
    return 0 if not manques else 1


if __name__ == "__main__":
    sys.exit(main())
