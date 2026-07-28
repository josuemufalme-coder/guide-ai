#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verification_finale.py --- Passe en revue tous les livrables avant diffusion.

Rejoue les controles qui comptent, sur la source comme sur les PDF produits,
et affiche un verdict par point. Sortie 0 si tout passe.

Usage : python3 outils/verification_finale.py
"""
import ast
import re
import sys
from pathlib import Path

import fitz

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "Guide_Intelligence_Artificielle.md"
COMPLET = RACINE / "Guide_Intelligence_Artificielle_publiable.pdf"
DOCX = RACINE / "Guide_Intelligence_Artificielle_publiable.docx"
INTERIEUR = RACINE / "Lulu_interieur.pdf"
COUVERTURE = RACINE / "Lulu_couverture.pdf"
EXTRAIT = RACINE / "Extrait_Comprendre_et_pratiquer_l_IA.pdf"
RELECTURE = RACINE / "Guide_Intelligence_Artificielle_relecture.pdf"

MM = 72 / 25.4
resultats = []


def verifie(intitule, condition, detail=""):
    resultats.append((bool(condition), intitule, detail))


def controle_source():
    t = SOURCE.read_text(encoding="utf-8")
    blocs = re.findall(r"^```python\n(.*?)^```", t, re.S | re.M)
    invalides = 0
    for b in blocs:
        try:
            ast.parse(b)
        except SyntaxError:
            invalides += 1
    verifie("blocs Python valides", invalides == 0, f"{len(blocs)} blocs, {invalides} invalides")

    pb = set(re.findall(r"^### Problème (\d+\.\d+)", t, re.M))
    co = set(re.findall(r"\*\*Corrigé (\d+\.\d+)", t))
    verifie("chaque problème a son corrigé", pb == co and len(pb) == 64,
            f"{len(pb)} problèmes, {len(co)} corrigés")

    sans = re.sub(r"^```.*?^```", "", t, flags=re.S | re.M)
    sans = re.sub(r"^<w:.*$", "", sans, flags=re.M)
    verifie("aucun gras non apparié",
            sum(1 for l in sans.split("\n") if l.count("**") % 2) <= 1)
    verifie("aucun marqueur de gras échappé", "\\*\\*" not in t)

    lecons = len(re.findall(r"^### Leçon", sans, re.M))
    chapitres = len(re.findall(r"^## Chapitre", sans, re.M))
    parties = len(re.findall(r"^# Partie", sans, re.M))
    verifie("structure : 8 parties, 24 chapitres, 158 leçons",
            (parties, chapitres, lecons) == (8, 24, 158),
            f"{parties}/{chapitres}/{lecons}")


def controle_pdf_complet():
    d = fitz.open(COMPLET)
    texte = "".join(p.get_text() for p in d)

    verifie("PDF complet : 286 pages", d.page_count == 286, f"{d.page_count}")
    verifie("apostrophes courbes", texte.count("’") > 5000,
            f"{texte.count(chr(0x2019))} courbes, {texte.count(chr(39))} droites (code)")
    verifie("espaces insécables posées", texte.count(" ") > 2000,
            f"{texte.count(chr(0xa0))}")

    mauvaises = sum(
        1 for p in d for b in p.get_text("dict")["blocks"] for l in b.get("lines", [])
        for x in ["".join(s["text"] for s in l["spans"]).strip()]
        if x and x[0] in ":;?!»%")
    verifie("aucune ligne ouvrant sur une ponctuation double", mauvaises == 0,
            f"{mauvaises}")

    # titres orphelins en bas de page
    orphelins = 0
    for p in d:
        lignes = []
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                txt = "".join(s["text"] for s in l["spans"]).strip()
                if txt and l["bbox"][3] < 790:
                    sp = l["spans"][0]
                    lignes.append((l["bbox"][3], txt, sp["size"], "Bold" in sp["font"]))
        if not lignes:
            continue
        y, txt, taille, gras = max(lignes)
        if y / 842 > 0.80 and (taille >= 12.5 or (gras and txt == txt.upper() and len(txt) > 6)):
            orphelins += 1
    verifie("aucun titre orphelin en bas de page", orphelins == 0, f"{orphelins}")

    folios = [next((x for x in reversed(p.get_text().strip().split("\n")) if x.strip()), "")
              for p in d]
    verifie("couvertures sans folio", folios[0].strip() == "" and folios[-1].strip() == "")
    verifie("folio « 1 » au début du corps", "1" in folios,
            f"page PDF {folios.index('1') + 1}")

    d.close()


def controle_impression(chemin, pages_attendues, format_attendu):
    d = fitz.open(chemin)
    nom = chemin.name
    verifie(f"{nom} : nombre de pages", d.page_count == pages_attendues,
            f"{d.page_count}")
    l, h = d[0].rect.width / MM, d[0].rect.height / MM
    verifie(f"{nom} : format", abs(l - format_attendu[0]) < 0.5 and abs(h - format_attendu[1]) < 0.5,
            f"{l:.2f} x {h:.2f} mm")

    basses, vues = 0, set()
    for page in d:
        for info in page.get_images(full=True):
            if info[0] in vues:
                continue
            for r in page.get_image_rects(info[0]):
                if r.width < 40:
                    continue
                vues.add(info[0])
                pix = fitz.Pixmap(d, info[0])
                if min(pix.width / (r.width / 72), pix.height / (r.height / 72)) < 200:
                    basses += 1
                break
    verifie(f"{nom} : images à 200 dpi ou plus", basses == 0,
            f"{len(vues)} images, {basses} sous le seuil")

    brut = chemin.read_bytes()
    transp = sum(brut.count(c.encode()) for c in ("/SMask", "/Transparency", "/Group"))
    verifie(f"{nom} : aucune transparence", transp == 0, f"{transp} marqueurs")
    d.close()


def main():
    controle_source()
    controle_pdf_complet()
    controle_impression(INTERIEUR, 284, (210, 297))
    controle_impression(COUVERTURE, 1, (444.35, 303.35))
    controle_impression(EXTRAIT, 82, (210, 297))

    d = fitz.open(RELECTURE)
    # is_encrypted repasse a faux des que le document est ouvert avec le mot
    # de passe utilisateur vide : c'est la metadonnee qui dit le chiffrement.
    chiffrement = d.metadata.get("encryption") or ""
    refuse = [fitz.PDF_PERM_PRINT, fitz.PDF_PERM_COPY, fitz.PDF_PERM_MODIFY,
              fitz.PDF_PERM_ANNOTATE, fitz.PDF_PERM_ASSEMBLE]
    verifie("exemplaire de relecture : chiffré et verrouillé",
            "AES" in chiffrement and not any(d.permissions & p for p in refuse),
            f"{d.page_count} pages, {chiffrement}")
    d.close()

    for f in (DOCX, COMPLET, INTERIEUR, COUVERTURE, EXTRAIT, RELECTURE):
        verifie(f"{f.name} présent", f.exists(),
                f"{f.stat().st_size / 1048576:.1f} Mo" if f.exists() else "MANQUANT")

    largeur = max(len(i) for _, i, _ in resultats)
    for ok, intitule, detail in resultats:
        print(f"  [{'OK ' if ok else 'NON'}] {intitule:{largeur}}  {detail}")
    echecs = sum(1 for ok, _, _ in resultats if not ok)
    print(f"\n  {len(resultats) - echecs} contrôles passés, {echecs} en échec")
    return 0 if echecs == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
