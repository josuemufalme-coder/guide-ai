#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
images_impression.py --- Prepare les figures pour l'impression.

Deux exigences de l'imprimeur, que le controle de Lulu signale :

  1. RESOLUTION. Une image doit compter au moins 200 pixels par pouce a la
     taille ou elle est placee dans la page ; 300 est la valeur de reference.
     Dix des dix-sept figures etaient entre 145 et 197 dpi.

  2. TRANSPARENCE. Les dix-sept PNG portaient un canal alpha. Il etait
     entierement opaque, mais sa seule presence suffit a declencher l'alerte :
     un moteur d'impression doit alors aplatir la page, avec des resultats
     imprevisibles. On le supprime en composant l'image sur du blanc.

  3. COUVERTURE D'ENCRE. Un pixel sombre et legerement teinte se separe en
     quatre encres superposees. On neutralise ces gris et on plafonne la
     couverture d'encre de l'ensemble.

La taille de placement est lue dans le Markdown, ou pandoc l'a inscrite.

ATTENTION : agrandir une image ne cree pas de detail. Ce script fait le
meilleur reechantillonnage possible, ce qui supprime l'escalier des contours,
mais il ne remplace pas la regeneration des figures a la bonne taille.

Les originaux sont conserves dans media_origine/.

Usage :
    python3 outils/images_impression.py           prepare
    python3 outils/images_impression.py --origine restaure les originaux
"""
import re
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

RACINE = Path(__file__).resolve().parent.parent
MEDIA = RACINE / "media"
ORIGINES = RACINE / "media_origine"
SOURCE = RACINE / "Guide_Intelligence_Artificielle.md"

DPI_CIBLE = 300
# Au-dela, le fichier grossit sans gain visible a l'impression.
LARGEUR_MAX = 4000


def tailles_de_placement():
    """{nom de fichier: (largeur_pouces, hauteur_pouces)} lu dans le Markdown."""
    texte = SOURCE.read_text(encoding="utf-8")
    tailles = {}
    motif = re.compile(r'!\[[^\]]*\]\(\./media/([^)]+)\)\{width="([\d.]+)in"\s+'
                       r'height="([\d.]+)in"\}')
    for m in motif.finditer(texte):
        tailles[m.group(1)] = (float(m.group(2)), float(m.group(3)))
    return tailles


def sauvegarde_les_originaux():
    if ORIGINES.exists():
        return
    ORIGINES.mkdir()
    for f in sorted(MEDIA.glob("*.png")):
        shutil.copy2(f, ORIGINES / f.name)
    print(f"  originaux conserves dans {ORIGINES.name}/")


def restaure():
    if not ORIGINES.exists():
        print("  aucun original conserve")
        return
    n = 0
    for f in sorted(ORIGINES.glob("*.png")):
        shutil.copy2(f, MEDIA / f.name)
        n += 1
    print(f"  {n} images restaurees")


def aplatis(img):
    """Compose sur du blanc et rend une image RVB sans canal alpha."""
    if img.mode in ("RGBA", "LA", "PA") or "transparency" in img.info:
        img = img.convert("RGBA")
        fond = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(fond, img)
    return img.convert("RGB")


def gamut(img):
    """Etendue reellement utilisee par chaque canal de l'image d'origine."""
    a = np.asarray(img, dtype=np.uint8)
    return a.reshape(-1, 3).min(axis=0), a.reshape(-1, 3).max(axis=0)


def ramene_dans_gamme(img, gamme):
    """Supprime le depassement du reechantillonnage.

    Lanczos et l'accentuation produisent, de part et d'autre d'un contour,
    des valeurs qui sortent de l'etendue d'origine : un lisere plus clair que
    le blanc du fond, un halo plus sombre que le noir du trait. On les
    ramene dans les bornes de l'image de depart."""
    mini, maxi = gamme
    a = np.asarray(img, dtype=np.int16)
    a = np.clip(a, mini[None, None, :], maxi[None, None, :])
    return Image.fromarray(a.astype(np.uint8), "RGB")


def neutralise_les_sombres(img, seuil_clair=60, ecart_max=18):
    """Rend gris les pixels sombres presque neutres.

    Un gris legerement teinte se separe en cyan, magenta, jaune ET noir : le
    trait devient une superposition de quatre encres, sensible au moindre
    defaut de repere, et la couverture d'encre grimpe. Un gris exactement
    neutre se separe en noir seul."""
    a = np.asarray(img, dtype=np.int16)
    haut = a.max(axis=2)
    ecart = haut - a.min(axis=2)
    vises = (haut < seuil_clair) & (ecart <= ecart_max)
    if vises.any():
        moyenne = a.mean(axis=2).astype(np.int16)
        for c in range(3):
            a[..., c] = np.where(vises, moyenne, a[..., c])
    return Image.fromarray(a.astype(np.uint8), "RGB")


def limite_encre(img, plafond=210.0):
    """Ramene sous le plafond les pixels trop charges en encre.

    Le calcul de la couverture d'encre est ici la conversion naive vers le
    CMJN, celle qui retire le maximum de noir : elle donne la valeur LA PLUS
    BASSE possible. Un moteur d'impression sera plus severe, d'ou un plafond
    volontairement prudent. Les pixels concernes sont eclaircis vers le blanc,
    juste assez pour repasser sous la limite."""
    a = np.asarray(img, dtype=np.float32) / 255.0
    for _ in range(12):
        k = 1 - a.max(axis=2)
        reste = np.clip(1 - k, 1e-6, None)
        cmj = np.clip((1 - a - k[..., None]) / reste[..., None], 0, 1)
        t = (cmj.sum(axis=2) + k) * 100
        trop = t > plafond
        if not trop.any():
            break
        a[trop] = a[trop] + (1.0 - a[trop]) * 0.06
    return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8), "RGB")


def prepare():
    sauvegarde_les_originaux()
    tailles = tailles_de_placement()
    agrandies = aplaties = 0
    for f in sorted(ORIGINES.glob("*.png")):
        img = aplatis(Image.open(f))
        aplaties += 1
        pouces = tailles.get(f.name)
        if pouces:
            cible_l = min(round(pouces[0] * DPI_CIBLE), LARGEUR_MAX)
            if cible_l > img.width:
                ratio = cible_l / img.width
                nouveau = (cible_l, round(img.height * ratio))
                avant = img.width / pouces[0]
                gamme = gamut(img)
                img = img.resize(nouveau, Image.LANCZOS)
                # Pas d'accentuation. Sur ces schemas en aplats, elle cree de
                # part et d'autre des contours un halo plus sombre et teinte
                # que l'original : a l'impression ce halo se separe en quatre
                # encres au lieu d'une, la couverture d'encre grimpe et les
                # petits caracteres bavent. Lanczos seul suffit.
                img = ramene_dans_gamme(img, gamme)
                img = neutralise_les_sombres(img)
                agrandies += 1
                print(f"  {f.name:14} {avant:3.0f} -> {img.width / pouces[0]:3.0f} dpi"
                      f"   ({nouveau[0]}x{nouveau[1]} px)")
        img = limite_encre(img)
        img.save(MEDIA / f.name, "PNG", optimize=True)
    print(f"  {aplaties} images sans canal alpha, {agrandies} reechantillonnees")


if __name__ == "__main__":
    if "--origine" in sys.argv:
        restaure()
    else:
        prepare()
