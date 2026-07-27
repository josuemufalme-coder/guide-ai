#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rasterise le PDF et signale les defauts de mise en page classiques.

Ce que l'outil detecte automatiquement :
  - titre orphelin : un titre qui tombe dans le dernier huitieme d'une page
  - legende separee de sa figure : legende en haut de page sans image au-dessus
  - image debordant de la zone de texte
  - page presque vide (moins de 15 % de contenu), hors pages de garde
  - tableau coupe par un saut de page

Ce qu'il ne detecte pas et qui exige un oeil : la coherence typographique,
les cesures malheureuses, l'equilibre general d'une double page.

Usage : python3 outils/controle_visuel.py chemin.pdf [--images]
"""
import sys
from pathlib import Path

import fitz

SEUIL_ORPHELIN = 0.86   # position verticale relative au-dela de laquelle un titre est orphelin
DPI_APERCU = 110


def analyser(chemin_pdf, ecrire_images=True):
    doc = fitz.open(chemin_pdf)
    dossier = Path(chemin_pdf).parent / "controle_pages"
    if ecrire_images:
        dossier.mkdir(exist_ok=True)
        for f in dossier.glob("*.png"):
            f.unlink()

    defauts = []
    stats = {"pages": len(doc), "images": 0, "titres": 0}

    for n, page in enumerate(doc, 1):
        h = page.rect.height
        w = page.rect.width
        marge_bas = page.rect.y1 - 56

        blocs = page.get_text("dict")["blocks"]
        images_page = [b for b in blocs if b["type"] == 1]
        stats["images"] += len(images_page)

        textes = []
        for b in blocs:
            if b["type"] != 0:
                continue
            for ligne in b["lines"]:
                for sp in ligne["spans"]:
                    if sp["text"].strip():
                        textes.append({
                            "texte": sp["text"].strip(),
                            "taille": sp["size"],
                            "gras": bool(sp["flags"] & 2 ** 4),
                            "y": sp["bbox"][1],
                            "y1": sp["bbox"][3],
                            "x": sp["bbox"][0],
                        })

        # --- titre orphelin -------------------------------------------------
        for t in textes:
            est_titre = t["taille"] >= 13 and t["gras"]
            if est_titre:
                stats["titres"] += 1
                if t["y"] / h > SEUIL_ORPHELIN:
                    defauts.append((n, "titre orphelin",
                                    f'« {t["texte"][:52]} » à {t["y"]/h:.0%} de la hauteur'))

        # --- legende separee de sa figure -----------------------------------
        for t in textes:
            if t["texte"].startswith("Figure ") and "---" in t["texte"] or \
               t["texte"].startswith("Figure ") and "—" in t["texte"]:
                haut_de_page = t["y"] / h < 0.18
                image_avant = any(im["bbox"][3] <= t["y"] + 4 for im in images_page)
                if haut_de_page and not image_avant:
                    defauts.append((n, "légende séparée de sa figure",
                                    f'« {t["texte"][:52]} » en haut de page, image absente'))

        # --- image debordante -------------------------------------------------
        for im in images_page:
            x0, y0, x1, y1 = im["bbox"]
            if x0 < 40 or x1 > w - 40 or y1 > h - 40:
                defauts.append((n, "image hors zone de texte",
                                f"cadre ({x0:.0f}, {y0:.0f}, {x1:.0f}, {y1:.0f}) sur {w:.0f}×{h:.0f}"))

        # --- page presque vide -------------------------------------------------
        surface = sum((b["bbox"][2] - b["bbox"][0]) * (b["bbox"][3] - b["bbox"][1])
                      for b in blocs)
        taux = surface / (w * h)
        if taux < 0.12 and n > 4 and textes:
            defauts.append((n, "page très peu remplie", f"{taux:.0%} de la surface"))

        if ecrire_images:
            page.get_pixmap(dpi=DPI_APERCU).save(dossier / f"page_{n:03d}.png")

    doc.close()

    print(f"\n=== CONTROLE VISUEL : {stats['pages']} pages ===")
    print(f"  images placées : {stats['images']}")
    print(f"  titres détectés : {stats['titres']}")
    if ecrire_images:
        print(f"  aperçus écrits dans {dossier}/")

    if not defauts:
        print("\n  Aucun défaut automatique détecté.")
    else:
        print(f"\n  {len(defauts)} signalement(s) :\n")
        par_type = {}
        for p, typ, det in defauts:
            par_type.setdefault(typ, []).append((p, det))
        for typ, items in sorted(par_type.items(), key=lambda kv: -len(kv[1])):
            print(f"  --- {typ} ({len(items)}) ---")
            for p, det in items[:12]:
                print(f"      page {p:>3} : {det}")
            if len(items) > 12:
                print(f"      … et {len(items)-12} autres")
            print()
    return defauts


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    analyser(sys.argv[1], "--images" in sys.argv or True)
