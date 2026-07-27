#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
couverture.py --- Proposition de couverture recto verso.

Produit un PDF de deux pages : page 1 la première de couverture, page 2 la
quatrième. Format du bloc intérieur (A4) plus 5 mm de fond perdu sur chaque
bord, avec des traits de coupe aux angles.

Le parti pris est celui de l’edition universitaire : une composition
typographique, pas d’image d’illustration. Le seul motif est un petit graphe
trace au trait, qui dit le sujet sans tomber dans le cerveau lumineux ni le
circuit imprime, devenus la signature visuelle du contenu genere.

Usage : python3 outils/couverture.py [sortie.pdf]
"""
import sys
from pathlib import Path

import fitz

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "Couverture_proposition.pdf"
CODE_BARRES = RACINE / "media" / "isbn_codebarres.png"

ISBN = "978-0-557-99817-3"
DEPOT_LEGAL = "Dépôt légal : juillet 2026"

MM = 72 / 25.4
ROGNE_L, ROGNE_H = 210 * MM, 297 * MM      # format fini
FP = 5 * MM                                 # fond perdu
L, H = ROGNE_L + 2 * FP, ROGNE_H + 2 * FP   # page avec fond perdu

ENCRE = (0.075, 0.137, 0.239)   # bleu d’encre profond
IVOIRE = (0.973, 0.965, 0.945)
BLANC = (1, 1, 1)
GRIS = (0.42, 0.42, 0.42)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_G = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_G = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


FICHIERS = {"Fs": SERIF, "Fsg": SERIF_G, "Fsi": SERIF_I, "Fn": SANS, "Fng": SANS_G}
POLICES = {nom: fitz.Font(fontfile=f) for nom, f in FICHIERS.items()}


def pose_polices(page):
    for nom, fichier in FICHIERS.items():
        page.insert_font(fontname=nom, fontfile=fichier)


def largeur(texte, police, corps):
    return POLICES[police].text_length(texte, fontsize=corps)


def ecris(page, x, y, texte, police, corps, couleur):
    page.insert_text((x, y), texte, fontname=police, fontfile=FICHIERS[police],
                     fontsize=corps, color=couleur)


def centre(page, texte, y, police, corps, couleur, interlettrage=0):
    """Ecrit une ligne centree sur la largeur rognee, avec interlettrage."""
    if interlettrage:
        larg = largeur(texte, police, corps) + interlettrage * (len(texte) - 1)
        x = FP + (ROGNE_L - larg) / 2
        for c in texte:
            ecris(page, x, y, c, police, corps, couleur)
            x += largeur(c, police, corps) + interlettrage
    else:
        ecris(page, FP + (ROGNE_L - largeur(texte, police, corps)) / 2, y,
              texte, police, corps, couleur)


def graphe(page, cx, cy, largeur_totale, hauteur, couleur):
    """Un petit reseau trace au trait : quatre couches de noeuds relies.

    Le pas vertical est calcule pour que le motif remplisse la hauteur
    demandee quelle que soit la couche, ce qui evite l'effet de pate."""
    couches = [3, 5, 4, 2]
    noeuds = []
    for i, n in enumerate(couches):
        x = cx - largeur_totale / 2 + i * (largeur_totale / (len(couches) - 1))
        pas = hauteur / (max(couches) - 1)
        noeuds.append([(x, cy - (n - 1) * pas / 2 + j * pas) for j in range(n)])
    f = page.new_shape()
    for a, b in zip(noeuds, noeuds[1:]):
        for p1 in a:
            for p2 in b:
                f.draw_line(fitz.Point(p1), fitz.Point(p2))
    f.finish(color=couleur, width=0.25)
    f.commit()
    f = page.new_shape()
    for col in noeuds:
        for p in col:
            f.draw_circle(fitz.Point(p), 3.2)
    f.finish(color=couleur, fill=couleur)
    f.commit()


# La maquette destinee a la relecture porte des traits de coupe ; le volet
# assemble pour l'imprimeur ne doit en porter aucun, ils s'imprimeraient.
AVEC_REPERES = True


def traits_de_coupe(page):
    if not AVEC_REPERES:
        return
    f = page.new_shape()
    for x in (FP, FP + ROGNE_L):
        f.draw_line(fitz.Point(x, 0), fitz.Point(x, FP * 0.6))
        f.draw_line(fitz.Point(x, H - FP * 0.6), fitz.Point(x, H))
    for y in (FP, FP + ROGNE_H):
        f.draw_line(fitz.Point(0, y), fitz.Point(FP * 0.6, y))
        f.draw_line(fitz.Point(L - FP * 0.6, y), fitz.Point(L, y))
    f.finish(color=(0.6, 0.6, 0.6), width=0.3)
    f.commit()


# --------------------------------------------------------------------------
def premiere(page):
    pose_polices(page)
    page.draw_rect(fitz.Rect(0, 0, L, H), color=None, fill=IVOIRE)
    # bandeau d’encre, a fond perdu, sur les deux cinquiemes superieurs
    page.draw_rect(fitz.Rect(0, 0, L, FP + 128 * MM), color=None, fill=ENCRE)

    centre(page, "MANUEL DE FORMATION", FP + 30 * MM, "Fng", 9, (0.72, 0.76, 0.84), 2.6)

    centre(page, "Comprendre et pratiquer", FP + 58 * MM, "Fs", 27, BLANC)
    centre(page, "L’INTELLIGENCE", FP + 82 * MM, "Fsg", 37, BLANC, 1.5)
    centre(page, "ARTIFICIELLE", FP + 103 * MM, "Fsg", 37, BLANC, 1.5)

    # filet fin sous le titre, dans le bandeau
    f = page.new_shape()
    f.draw_line(fitz.Point(FP + 62 * MM, FP + 114 * MM),
                fitz.Point(FP + 148 * MM, FP + 114 * MM))
    f.finish(color=(0.55, 0.60, 0.70), width=0.6)
    f.commit()

    centre(page, "Des fondations aux usages professionnels",
           FP + 148 * MM, "Fsi", 13.5, ENCRE)

    graphe(page, FP + 105 * MM, FP + 188 * MM, 88 * MM, 46 * MM, ENCRE)

    f = page.new_shape()
    f.draw_line(fitz.Point(FP + 78 * MM, FP + 232 * MM),
                fitz.Point(FP + 132 * MM, FP + 232 * MM))
    f.finish(color=ENCRE, width=0.8)
    f.commit()

    centre(page, "MUFALME BULENDA JOSUÉ", FP + 246 * MM, "Fsg", 16, ENCRE, 1.2)
    centre(page, "Expert numérique", FP + 255 * MM, "Fsi", 11, GRIS)

    centre(page, "KINSHASA", FP + 278 * MM, "Fng", 8, GRIS, 2.2)
    traits_de_coupe(page)


def bloc(page, rect, texte, police, corps, couleur, interligne=1.34, align=0):
    """Compose un paragraphe dans un cadre, avec retour a la ligne automatique.
    Renvoie l'ordonnee atteinte."""
    reste = page.insert_textbox(rect, texte, fontname=police,
                                fontfile=FICHIERS[police], fontsize=corps,
                                color=couleur, align=align, lineheight=interligne)
    assert reste >= 0, f"texte trop long pour le cadre : {texte[:40]!r}"
    # insert_textbox renvoie la hauteur inutilisee du cadre : on la retranche
    # pour savoir ou le paragraphe s'arrete reellement.
    return rect.y1 - reste - corps * (interligne - 1)


def quatrieme(page):
    pose_polices(page)
    page.draw_rect(fitz.Rect(0, 0, L, H), color=None, fill=IVOIRE)
    page.draw_rect(fitz.Rect(0, 0, L, FP + 34 * MM), color=None, fill=ENCRE)

    centre(page, "COMPRENDRE ET PRATIQUER L’INTELLIGENCE ARTIFICIELLE",
           FP + 20 * MM, "Fn", 10, BLANC, 1.4)

    g = FP + 26 * MM
    d = FP + ROGNE_L - 26 * MM
    y = FP + 50 * MM

    y = bloc(page, fitz.Rect(g, y, d, y + 26 * MM),
             "L’intelligence artificielle n’est pas réservée à quelques initiés.",
             "Fsg", 18, ENCRE, 1.25) + 6 * MM

    texte = (
        "J’ai écrit ce livre parce que j’aurais aimé le lire quand j’ai commencé. "
        "Ce n’est pas un cours froid ni un catalogue de notions : chaque idée y est "
        "expliquée comme je l’expliquerais à un ami, en prenant le temps, avec des "
        "exemples que l’on refait soi-même.\n \n"
        "Le chemin part des fondations — ce qu’est vraiment l’IA, un peu de Python, "
        "les quelques idées mathématiques utiles — puis avance vers le cœur du sujet : "
        "comment une machine apprend. Viennent ensuite les grands domaines, le langage, "
        "la vision, l’IA générative, les agents ; puis l’éthique, le droit et la conduite "
        "de projet ; enfin les outils du quotidien et quatre projets menés de bout en bout.\n \n"
        "On n’apprend pas l’IA en lisant, mais en faisant. C’est pourquoi chaque chapitre "
        "se termine par des exercices, et pourquoi tout le code de ce livre s’exécute."
    )
    y = bloc(page, fitz.Rect(g, y, d, y + 92 * MM), texte, "Fs", 11.5,
             (0.13, 0.13, 0.13), 1.42, align=3) + 9 * MM

    f = page.new_shape()
    f.draw_line(fitz.Point(g, y), fitz.Point(d, y))
    f.finish(color=(0.72, 0.72, 0.72), width=0.5)
    f.commit()
    y += 8 * MM

    ecris(page, g, y, "CE QUE CONTIENT CE MANUEL", "Fng", 8.5, ENCRE)
    y += 7 * MM
    for texte_puce in (
        "8 parties, 24 chapitres, 158 leçons",
        "146 exercices, dont 64 problèmes gradués sur trois niveaux, tous corrigés",
        "39 extraits de code et 4 projets complets, prêts à exécuter",
        "un glossaire, une bibliographie et un index des figures",
    ):
        f = page.new_shape()
        f.draw_circle(fitz.Point(g + 1.4 * MM, y - 1.2 * MM), 1.1)
        f.finish(color=ENCRE, fill=ENCRE)
        f.commit()
        ecris(page, g + 6 * MM, y, texte_puce, "Fs", 10.8, (0.13, 0.13, 0.13))
        y += 6.2 * MM

    y += 5 * MM
    f = page.new_shape()
    f.draw_line(fitz.Point(g, y), fitz.Point(d, y))
    f.finish(color=(0.72, 0.72, 0.72), width=0.5)
    f.commit()
    y += 8 * MM

    ecris(page, g, y, "MUFALME BULENDA Josué", "Fsg", 12, ENCRE)
    y += 5.8 * MM
    bloc(page, fitz.Rect(g, y - 4 * MM, d - 52 * MM, y + 22 * MM),
         "est expert numérique. Il forme depuis plusieurs années des professionnels "
         "et des étudiants aux usages de l’intelligence artificielle. "
         "Il vit et travaille à Kinshasa.",
         "Fs", 10.8, (0.25, 0.25, 0.25), 1.36)

    # Code-barres EAN-13 de l'ISBN, en bas a droite, sur fond blanc franc :
    # un lecteur optique exige un fond clair et une zone de silence autour.
    larg, haut = 46 * MM, 31 * MM
    bx0, by0 = d - larg, FP + ROGNE_H - 46 * MM
    cadre = fitz.Rect(bx0, by0, bx0 + larg, by0 + haut)
    page.draw_rect(cadre, color=None, fill=BLANC)
    if CODE_BARRES.exists():
        marge = 2.5 * MM
        page.insert_image(cadre + (marge, marge, -marge, -marge),
                          filename=str(CODE_BARRES), keep_proportion=True)
    else:
        ecris(page, bx0 + 6 * MM, by0 + 15 * MM, "code-barres ISBN", "Fn", 8, GRIS)

    ecris(page, g, FP + ROGNE_H - 27 * MM, f"ISBN {ISBN}", "Fn", 9, GRIS)
    ecris(page, g, FP + ROGNE_H - 22 * MM, DEPOT_LEGAL, "Fn", 9, GRIS)
    ecris(page, g, FP + ROGNE_H - 17 * MM, "Première édition — Kinshasa, 2026", "Fn", 9, GRIS)

    traits_de_coupe(page)


def main():
    global AVEC_REPERES
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--sans-reperes" in sys.argv:
        AVEC_REPERES = False
    sortie = Path(args[0]) if args else SORTIE
    doc = fitz.open()
    premiere(doc.new_page(width=L, height=H))
    quatrieme(doc.new_page(width=L, height=H))
    doc.set_metadata({
        "title": "Couverture — Comprendre et pratiquer l’intelligence artificielle",
        "author": "MUFALME BULENDA Josué",
    })
    doc.save(sortie, deflate=True)
    doc.close()
    print(f"  {sortie.name} — 2 pages, "
          f"{ROGNE_L/MM:.0f} × {ROGNE_H/MM:.0f} mm rognés + {FP/MM:.0f} mm de fond perdu")
    return 0


if __name__ == "__main__":
    sys.exit(main())
