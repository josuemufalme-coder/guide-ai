#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
controle_impression.py --- Rejoue les controles que fait l'imprimeur.

Verifie, sur un PDF donne, les trois points que Lulu signale :

  1. la resolution effective de chaque image, a la taille ou elle est placee ;
  2. la presence de transparence, sous toutes ses formes ;
  3. la couverture d'encre.

Sur ce dernier point, un avertissement s'impose : sans profil colorimetrique
installe, la conversion vers le CMJN est faite par la formule naive, qui
retire le maximum de noir et donne donc la couverture d'encre LA PLUS BASSE
possible. Un moteur d'impression, lui, garde davantage de cyan, de magenta et
de jaune sous le noir. La valeur calculee ici est un plancher : si elle est
deja haute, l'imprimeur sera plus severe encore.

Usage : python3 outils/controle_impression.py <fichier.pdf> [--seuil 240]
"""
import sys
from pathlib import Path

import fitz
import numpy as np
from PIL import Image

DPI_MINI = 200
DPI_CONSEILLE = 300
SEUIL_ENCRE = 240
ECHANTILLON = 60          # dpi de rasterisation pour la mesure d'encre


def couverture_encre(image, tolerance_neutre=0.05):
    """Couverture d'encre estimee, en pourcentage.

    Les pixels quasi neutres — le noir du texte et ses bords lisses — sont
    traites comme du noir seul. Sans cette regle, la formule de conversion
    s'emballe sur eux : un pixel a 2 sur 255 de difference entre canaux se
    verrait attribuer trois encres de plus, et tout page de texte paraitrait
    surchargee alors qu'elle n'utilise qu'une seule encre."""
    a = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    k = 1 - a.max(axis=2)
    reste = np.clip(1 - k, 1e-6, None)
    cmj = np.clip((1 - a - k[..., None]) / reste[..., None], 0, 1)
    total = (cmj.sum(axis=2) + k) * 100
    neutre = (a.max(axis=2) - a.min(axis=2)) <= tolerance_neutre
    return np.where(neutre, (1 - a.mean(axis=2)) * 100, total)


def controle(chemin, seuil):
    doc = fitz.open(chemin)
    print(f"=== {Path(chemin).name} — {doc.page_count} pages ===")

    formats = {(round(p.rect.width / 72 * 25.4), round(p.rect.height / 72 * 25.4))
               for p in doc}
    print(f"format(s) : {', '.join(f'{l} x {h} mm' for l, h in sorted(formats))}")

    # --- 1. resolution ------------------------------------------------------
    basses, vues = [], set()
    for i, page in enumerate(doc, start=1):
        for info in page.get_images(full=True):
            if info[0] in vues:
                continue
            for r in page.get_image_rects(info[0]):
                if r.width < 40:
                    continue
                vues.add(info[0])
                pix = fitz.Pixmap(doc, info[0])
                dpi = min(pix.width / (r.width / 72), pix.height / (r.height / 72))
                if dpi < DPI_MINI:
                    basses.append((i, round(dpi)))
                break
    print(f"images         : {len(vues)} | sous {DPI_MINI} dpi : "
          f"{basses if basses else 'aucune'}")

    # --- 2. transparence ----------------------------------------------------
    brut = Path(chemin).read_bytes()
    marqueurs = {c: brut.count(c.encode()) for c in
                 ("/SMask", "/Transparency", "/Group", "/CA ", "/ca ")}
    restants = {k: v for k, v in marqueurs.items() if v}
    print(f"transparence   : {restants if restants else 'aucune'}")

    # --- 3. couverture d'encre ---------------------------------------------
    pires, lourdes = 0.0, []
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(dpi=ECHANTILLON)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        t = couverture_encre(im)
        pires = max(pires, float(t.max()))
        part = float((t > seuil).mean())
        if part > 0.005:
            lourdes.append((i, round(float(t.max())), round(part * 100, 1)))
    print(f"encre          : maximum {pires:.0f} % (plancher) | "
          f"pages au-dessus de {seuil} % sur plus de 0,5 % de leur surface : "
          f"{len(lourdes)}")
    for x in lourdes[:10]:
        print(f"                 page {x[0]:3} — {x[1]} % sur {x[2]} % de la page")

    doc.close()
    return not basses and not restants and not lourdes


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage : controle_impression.py <fichier.pdf> [--seuil N]",
              file=sys.stderr)
        sys.exit(1)
    seuil = SEUIL_ENCRE
    if "--seuil" in sys.argv:
        seuil = float(sys.argv[sys.argv.index("--seuil") + 1])
    sys.exit(0 if controle(sys.argv[1], seuil) else 2)
