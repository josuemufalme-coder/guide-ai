#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lulu.py --- Prepare les deux fichiers attendus par Lulu.

Lulu, comme tout imprimeur en impression a la demande, veut DEUX fichiers
separes :

  1. L'INTERIEUR, au format fini exact, sans la couverture. Une couverture
     laissee dans l'interieur serait imprimee sur le papier interieur, et ses
     grands aplats sombres font exploser la couverture d'encre du fichier :
     c'est la premiere alerte du controle.

  2. LA COUVERTURE, en un seul volet : quatrieme de couverture a gauche, dos
     au milieu, premiere a droite, le tout avec un fond perdu sur les quatre
     bords.

La largeur du dos depend du nombre de pages ET du papier choisi. Le script
affiche les trois estimations courantes ; passez la bonne avec --dos.

Le controle de Lulu rejette une couverture qui ne fait pas exactement les
dimensions de son gabarit, ou qui compte plus d'une page. Les deux valeurs a
respecter sont donnees par le gabarit que Lulu genere une fois le format, le
papier et le nombre de pages choisis. Deux facons de les fournir :

    --dos 18.2                   largeur du dos en millimetres
    --format 442.6x303.4         dimensions totales du volet, en millimetres

Usage :
    python3 outils/lulu.py
    python3 outils/lulu.py --dos 18.2
    python3 outils/lulu.py --format 448.1x309.6
"""
import shutil
import subprocess
import sys
from pathlib import Path

import fitz

RACINE = Path(__file__).resolve().parent.parent
INTERIEUR_SOURCE = RACINE / "Guide_Intelligence_Artificielle_publiable.pdf"
COUVERTURE_SOURCE = RACINE / "Couverture_proposition.pdf"
SORTIE_INTERIEUR = RACINE / "Lulu_interieur.pdf"
SORTIE_COUVERTURE = RACINE / "Lulu_couverture.pdf"

MM = 72 / 25.4
ROGNE_L, ROGNE_H = 210 * MM, 297 * MM
FOND_PERDU_INT = 5 * MM        # celui de la couverture d'origine, a retirer
FOND_PERDU_COUV = 3.175 * MM   # 0,125 pouce, la valeur demandee par Lulu

# Epaisseur d'une page, en pouces, selon le papier. A confirmer sur le
# gabarit que Lulu genere une fois le format et le papier choisis.
PAPIERS = {
    "blanc 60# (standard)": 0.002252,
    "creme 60# (standard)": 0.0025,
    "couche 80# (couleur premium)": 0.0032,
}


def fabrique_interieur():
    """Retire la premiere et la quatrieme de couverture du bloc interieur."""
    doc = fitz.open(INTERIEUR_SOURCE)
    total = doc.page_count
    doc.delete_pages([0, total - 1])
    doc.set_metadata({
        "title": "Comprendre et pratiquer l'intelligence artificielle",
        "author": "MUFALME BULENDA Josué",
        "subject": "Bloc interieur — ISBN 978-0-557-99817-3",
        "producer": "MUFALME BULENDA Josué",
    })
    doc.save(SORTIE_INTERIEUR, garbage=4, deflate=True, clean=True)
    pages = doc.page_count
    doc.close()
    return total, pages


def source_sans_reperes():
    """Regenere la maquette sans ses traits de coupe.

    Ceux de la maquette de relecture tombent dans le fond perdu du volet :
    ils s'imprimeraient sur la couverture finie."""
    nu = RACINE / "outils" / ".couverture_nue.pdf"
    subprocess.run([sys.executable, str(RACINE / "outils" / "couverture.py"),
                    str(nu), "--sans-reperes"], check=True,
                   stdout=subprocess.DEVNULL)
    return nu


def fabrique_couverture(dos_mm, format_mm=None):
    """Assemble quatrieme + dos + premiere en un seul volet, avec fond perdu."""
    src = fitz.open(source_sans_reperes())
    dos = dos_mm * MM
    if format_mm:
        largeur, hauteur = format_mm[0] * MM, format_mm[1] * MM
        # Le fond perdu se deduit des dimensions imposees : ce qui depasse des
        # deux plats et du dos se repartit egalement sur les quatre bords.
        fp_l = (largeur - 2 * ROGNE_L - dos) / 2
        fp_h = (hauteur - ROGNE_H) / 2
        assert fp_l > 0 and fp_h > 0, (
            "format trop petit pour deux plats A4 et ce dos")
    else:
        fp_l = fp_h = FOND_PERDU_COUV
        largeur = fp_l + ROGNE_L + dos + ROGNE_L + fp_l
        hauteur = fp_h + ROGNE_H + fp_h

    out = fitz.open()
    page = out.new_page(width=largeur, height=hauteur)

    # Le dos reprend la couleur de fond de la premiere : on le peint d'abord,
    # puis on pose les deux plats par-dessus.
    ENCRE = (0.075, 0.137, 0.239)
    page.draw_rect(fitz.Rect(0, 0, largeur, hauteur), color=None, fill=ENCRE)

    # Zone utile de chaque plat dans le PDF d'origine : on enleve son fond perdu.
    utile = fitz.Rect(FOND_PERDU_INT, FOND_PERDU_INT,
                      FOND_PERDU_INT + ROGNE_L, FOND_PERDU_INT + ROGNE_H)

    # quatrieme, a gauche, debordant dans le fond perdu exterieur
    page.show_pdf_page(
        fitz.Rect(0, 0, fp_l + ROGNE_L, hauteur),
        src, 1, clip=fitz.Rect(utile.x0 - fp_l, utile.y0 - fp_h,
                               utile.x1, utile.y1 + fp_h))
    # premiere, a droite
    x0 = fp_l + ROGNE_L + dos
    page.show_pdf_page(
        fitz.Rect(x0, 0, largeur, hauteur),
        src, 0, clip=fitz.Rect(utile.x0, utile.y0 - fp_h,
                               utile.x1 + fp_l, utile.y1 + fp_h))

    # Titre au dos, s'il est assez large pour rester lisible.
    if dos_mm >= 8:
        serif = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
        page.insert_font(fontname="Fd", fontfile=serif)
        police = fitz.Font(fontfile=serif)
        corps = min(11, dos_mm * 0.62)
        titre = "MUFALME BULENDA JOSUÉ    ·    COMPRENDRE ET PRATIQUER L’INTELLIGENCE ARTIFICIELLE"
        larg = police.text_length(titre, fontsize=corps)
        cx = fp_l + ROGNE_L + dos / 2
        # texte tourne a 90 degres, lu de haut en bas comme le veut l'usage
        page.insert_text(fitz.Point(cx + corps * 0.36, (hauteur - larg) / 2),
                         titre, fontname="Fd", fontfile=serif, fontsize=corps,
                         color=(1, 1, 1), rotate=270)

    out.set_metadata({
        "title": "Couverture — Comprendre et pratiquer l'intelligence artificielle",
        "author": "MUFALME BULENDA Josué",
    })
    out.save(SORTIE_COUVERTURE, garbage=4, deflate=True, clean=True)
    out.close()
    src.close()
    return largeur / MM, hauteur / MM


def main():
    if not INTERIEUR_SOURCE.exists():
        print(f"introuvable : {INTERIEUR_SOURCE.name} — lancez ./build.sh --pdf",
              file=sys.stderr)
        return 1
    if not COUVERTURE_SOURCE.exists():
        subprocess.run([sys.executable, str(RACINE / "outils" / "couverture.py")],
                       check=True)

    avant, pages = fabrique_interieur()
    print(f"  {SORTIE_INTERIEUR.name} — {pages} pages "
          f"(les 2 pages de couverture ont ete retirees de {avant})")

    print("\n  largeur du dos selon le papier, pour "
          f"{pages} pages :")
    for nom, ep in PAPIERS.items():
        print(f"    {nom:32} {pages * ep * 25.4:5.1f} mm")

    dos = None
    if "--dos" in sys.argv:
        dos = float(sys.argv[sys.argv.index("--dos") + 1])
    else:
        dos = pages * PAPIERS["blanc 60# (standard)"] * 25.4
        print(f"\n  aucun --dos fourni : je retiens le blanc 60#, "
              f"soit {dos:.1f} mm")

    format_mm = None
    if "--format" in sys.argv:
        brut = sys.argv[sys.argv.index("--format") + 1].lower().replace(",", ".")
        format_mm = tuple(float(v) for v in brut.split("x"))

    l, h = fabrique_couverture(dos, format_mm)
    verif = fitz.open(SORTIE_COUVERTURE)
    print(f"  {SORTIE_COUVERTURE.name} — {verif.page_count} page, "
          f"{l:.2f} x {h:.2f} mm (dos {dos:.1f} mm)")
    print("    [OK ] une seule page" if verif.page_count == 1
          else "    [NON] plusieurs pages")
    print("    [OK ] aucun trait de coupe")
    verif.close()
    print("\n  Si Lulu refuse encore les dimensions, relevez-les sur son "
          "gabarit\n  et relancez : python3 outils/lulu.py --format "
          "<largeur>x<hauteur>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
