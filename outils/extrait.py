#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extrait.py --- Compose un extrait du manuel, a diffuser librement.

L'extrait est preleve tel quel dans le PDF final : meme gabarit, memes
polices, memes marges, memes folios. Rien n'est recompose, donc rien ne peut
diverger de l'ouvrage.

Ce qu'il contient, et pourquoi :

  - la couverture, le faux-titre, la page de titre et la page de droits, pour
    que le lecteur sache tout de suite quel livre il a en main ;
  - l'avant-propos, ou l'auteur dit pourquoi il a ecrit ce livre : c'est la
    page qui donne envie, bien plus qu'un resume ;
  - le plan des huit parties, qui montre l'etendue en un coup d'oeil ;
  - la premiere page de la table des matieres, pour le niveau de detail ;
  - LES CINQ PREMIERS CHAPITRES : la partie I en entier, soit les quatre
    chapitres des fondations, puis l'ouverture de la partie II et son premier
    chapitre, celui ou l'on voit enfin une machine apprendre. Un extrait qui
    s'arrete au milieu d'une demonstration frustre ; des chapitres complets
    prouvent la maniere. On y trouve les schemas, les exemples chiffres
    deroules a la main et les blocs de code, c'est-a-dire tout ce qui
    distingue ce manuel d'un cours theorique ;
  - une page de fin, la seule qui soit composee ici, qui dit ce que contient
    l'ouvrage complet ;
  - la quatrieme de couverture.

Usage : python3 outils/extrait.py [sortie.pdf]
"""
import sys
from pathlib import Path

import fitz

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "Guide_Intelligence_Artificielle_publiable.pdf"
SORTIE = RACINE / "Extrait_Comprendre_et_pratiquer_l_IA.pdf"

MM = 72 / 25.4
ENCRE = (0.075, 0.137, 0.239)
IVOIRE = (0.973, 0.965, 0.945)
GRIS = (0.42, 0.42, 0.42)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_G = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_G = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

ISBN = "978-0-557-99817-3"

# Numeros de page dans le PDF final, en base 1.
COUVERTURE = 1
LIMINAIRES = [2, 4, 5]        # faux-titre, page de titre, page de droits
AVANT_PROPOS = [6, 7, 8]      # avant-propos, plan des parties, debut de la table
# De l'ouverture de la partie I a la fin du chapitre 5. Les bornes sont des
# frontieres de l'ouvrage, pas un compte de pages : aucun chapitre n'est
# coupe en son milieu.
#   22       ouverture de la partie I
#   23-62    chapitres 1 a 4
#   63       ouverture de la partie II
#   64-73    chapitre 5
CHAPITRES = list(range(22, 74))


def page_de_fin(doc, gabarit):
    """Compose la seule page qui n'est pas prelevee dans l'ouvrage."""
    page = doc.new_page(width=gabarit.width, height=gabarit.height)
    L, H = gabarit.width, gabarit.height
    page.draw_rect(fitz.Rect(0, 0, L, H), color=None, fill=IVOIRE)
    page.draw_rect(fitz.Rect(0, 0, L, 62 * MM), color=None, fill=ENCRE)

    polices = {"Fs": SERIF, "Fsg": SERIF_G, "Fsi": SERIF_I, "Fng": SANS_G}
    for nom, fichier in polices.items():
        page.insert_font(fontname=nom, fontfile=fichier)

    def centre(texte, y, nom, corps, couleur, interlettrage=0):
        f = fitz.Font(fontfile=polices[nom])
        larg = f.text_length(texte, fontsize=corps) + interlettrage * (len(texte) - 1)
        x = (L - larg) / 2
        if interlettrage:
            for c in texte:
                page.insert_text((x, y), c, fontname=nom, fontfile=polices[nom],
                                 fontsize=corps, color=couleur)
                x += f.text_length(c, fontsize=corps) + interlettrage
        else:
            page.insert_text((x, y), texte, fontname=nom, fontfile=polices[nom],
                             fontsize=corps, color=couleur)

    centre("VOUS VENEZ DE LIRE CINQ CHAPITRES", 30 * MM, "Fng", 9,
           (0.72, 0.76, 0.84), 2.4)
    centre("Il en reste dix-neuf.", 48 * MM, "Fs", 20, (1, 1, 1))

    def filet(y):
        f = page.new_shape()
        f.draw_line(fitz.Point(g, y), fitz.Point(d, y))
        f.finish(color=(0.72, 0.72, 0.72), width=0.5)
        f.commit()

    g, d = 32 * MM, L - 32 * MM
    y = 100 * MM
    cadre = fitz.Rect(g, y, d, y + 40 * MM)
    reste = page.insert_textbox(
        cadre,
        "Ces cinq chapitres sont représentatifs de tout l’ouvrage : on part "
        "d’une question simple, on déroule un exemple que l’on refait "
        "soi-même, et l’on termine par des exercices. Les dix-neuf chapitres "
        "qui suivent procèdent de la même façon et vous mènent des "
        "fondations que vous venez de poser jusqu’aux usages professionnels "
        "— l’apprentissage profond, le langage, la vision, l’IA générative, "
        "les agents, l’éthique et le droit, l’automatisation, et quatre "
        "projets menés de bout en bout.",
        fontname="Fs", fontfile=SERIF, fontsize=12, color=(0.13, 0.13, 0.13),
        align=3, lineheight=1.45)
    y = cadre.y1 - reste + 14 * MM

    filet(y)
    y += 11 * MM
    page.insert_text((g, y), "L’OUVRAGE COMPLET", fontname="Fng",
                     fontfile=SANS_G, fontsize=9, color=ENCRE)
    y += 10 * MM

    # Chaque puce est mesuree apres composition : une entree qui passe sur
    # deux lignes ne cree donc pas de trou dans l'alignement des suivantes.
    for texte in ("8 parties, 24 chapitres, 158 leçons",
                  "146 exercices, dont 64 problèmes gradués sur trois niveaux, "
                  "tous corrigés",
                  "39 extraits de code et 4 projets complets, prêts à exécuter",
                  "17 figures, un glossaire, une bibliographie et un index",
                  "284 pages, format A4"):
        f = page.new_shape()
        f.draw_circle(fitz.Point(g + 1.4 * MM, y - 1.3 * MM), 1.1)
        f.finish(color=ENCRE, fill=ENCRE)
        f.commit()
        cadre = fitz.Rect(g + 6 * MM, y - 4.6 * MM, d, y + 16 * MM)
        reste = page.insert_textbox(cadre, texte, fontname="Fs", fontfile=SERIF,
                                    fontsize=11.5, color=(0.13, 0.13, 0.13),
                                    lineheight=1.32)
        y = cadre.y1 - reste + 3.4 * MM

    y += 8 * MM
    filet(y)

    centre("Comprendre et pratiquer l’intelligence artificielle",
           y + 15 * MM, "Fsg", 14, ENCRE)
    centre("MUFALME BULENDA Josué", y + 23 * MM, "Fsi", 11.5, GRIS)
    centre(f"ISBN {ISBN}", y + 34 * MM, "Fs", 10.5, GRIS)
    centre("Première édition — Kinshasa, 2026", y + 41 * MM, "Fs", 10.5, GRIS)

    centre("Extrait diffusable librement. L’ouvrage complet est protégé "
           "par le droit d’auteur.",
           H - 20 * MM, "Fsi", 9, GRIS)
    return page


def main():
    sortie = Path(sys.argv[1]) if len(sys.argv) > 1 else SORTIE
    src = fitz.open(SOURCE)
    pages = [COUVERTURE] + LIMINAIRES + AVANT_PROPOS + CHAPITRES
    out = fitz.open()
    for n in pages:
        out.insert_pdf(src, from_page=n - 1, to_page=n - 1)
    page_de_fin(out, src[0].rect)
    out.insert_pdf(src, from_page=src.page_count - 1, to_page=src.page_count - 1)

    out.set_metadata({
        "title": "Extrait — Comprendre et pratiquer l'intelligence artificielle",
        "author": "MUFALME BULENDA Josué",
        "subject": f"Extrait de lecture — ISBN {ISBN}",
        "keywords": "intelligence artificielle, manuel, extrait",
        "producer": "MUFALME BULENDA Josué — tous droits réservés",
    })
    out.save(sortie, garbage=4, deflate=True, clean=True)
    n = out.page_count
    out.close()
    src.close()
    print(f"  {sortie.name} — {n} pages, {sortie.stat().st_size / 1024:.0f} Ko")
    print(f"  pages prélevées : liminaires, puis {CHAPITRES[0]}-{CHAPITRES[-1]} "
          f"(partie I complète et chapitre 5)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
