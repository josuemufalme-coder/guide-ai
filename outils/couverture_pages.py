#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
couverture_pages.py --- Rend la couverture en images pleine page.

La couverture destinee a l'imprimeur porte un fond perdu de 5 mm et des traits
de coupe. Celle qui s'insere dans le document, elle, doit etre rognee au format
fini : on decoupe donc la zone utile avant d'exporter.

Sortie : media/couverture_1.png (premiere) et media/couverture_4.png (quatrieme)

Usage : python3 outils/couverture_pages.py
"""
import subprocess
import sys
from pathlib import Path

import fitz

RACINE = Path(__file__).resolve().parent.parent
COUVERTURE = RACINE / "Couverture_proposition.pdf"
MEDIA = RACINE / "media"

MM = 72 / 25.4
FOND_PERDU = 5 * MM
DPI = 300


def main():
    if not COUVERTURE.exists():
        subprocess.run([sys.executable, str(RACINE / "outils" / "couverture.py")],
                       check=True)
    doc = fitz.open(COUVERTURE)
    zoom = DPI / 72
    for index, nom in ((0, "couverture_1.png"), (1, "couverture_4.png")):
        page = doc[index]
        rogne = fitz.Rect(FOND_PERDU, FOND_PERDU,
                          page.rect.width - FOND_PERDU,
                          page.rect.height - FOND_PERDU)
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=rogne)
        pix.save(MEDIA / nom)
        print(f"  media/{nom} — {pix.width} × {pix.height} px "
              f"({pix.width / DPI * 25.4:.0f} × {pix.height / DPI * 25.4:.0f} mm à {DPI} dpi)")
    doc.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
