#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
images_nb.py --- Convertit les figures en niveaux de gris.

Outil de secours, pour un tirage en noir et blanc. Le manuel est livré avec
ses figures en couleur ; ce script n'est pas appelé par build.sh.

Les originaux en couleur sont conservés dans `media_couleur/` ; `media/`,
que la compilation utilise, reçoit les versions en niveaux de gris.

La conversion applique un léger renforcement du contraste : une palette de
couleurs vives se traduit sinon par des gris trop proches les uns des autres,
et les aplats deviennent indistincts.

Usage :
    python3 outils/images_nb.py            convertit
    python3 outils/images_nb.py --couleur  restaure les originaux
"""
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageEnhance

RACINE = Path(__file__).resolve().parent.parent
MEDIA = RACINE / "media"
ORIGINAUX = RACINE / "media_couleur"

CONTRASTE = 1.25


def sauvegarde_les_originaux():
    if ORIGINAUX.exists():
        return
    ORIGINAUX.mkdir()
    for f in sorted(MEDIA.glob("*.png")):
        shutil.copy2(f, ORIGINAUX / f.name)
    print(f"  originaux en couleur sauvegardés dans {ORIGINAUX.name}/")


def restaure():
    if not ORIGINAUX.exists():
        print("  aucun original sauvegardé, rien à restaurer")
        return
    for f in sorted(ORIGINAUX.glob("*.png")):
        shutil.copy2(f, MEDIA / f.name)
    print(f"  {len(list(ORIGINAUX.glob('*.png')))} images remises en couleur")


def convertis():
    sauvegarde_les_originaux()
    n = 0
    for f in sorted(ORIGINAUX.glob("*.png")):
        img = Image.open(f)
        # Un PNG à fond transparent devient noir en niveaux de gris : on
        # l'aplatit d'abord sur du blanc.
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
            fond = Image.new("RGBA", img.size, (255, 255, 255, 255))
            img = Image.alpha_composite(fond, img)
        gris = ImageEnhance.Contrast(img.convert("L")).enhance(CONTRASTE)
        gris.save(MEDIA / f.name, "PNG", optimize=True)
        n += 1
    print(f"  {n} figures converties en niveaux de gris (contraste ×{CONTRASTE})")


if __name__ == "__main__":
    if "--couleur" in sys.argv:
        restaure()
    else:
        convertis()
