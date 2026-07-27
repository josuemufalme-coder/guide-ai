#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
finitions_docx.py --- Corrections de mise en page appliquées au .docx produit
par pandoc, juste avant l'export PDF.

Pandoc ne sait pas exprimer ces trois réglages depuis le Markdown. Ils sont
donc posés directement dans l'OOXML :

  1. keepNext sur les titres d'encadré (paragraphes entièrement en gras et
     seuls sur leur ligne, comme « L'ESSENTIEL À RETENIR »). Sans cela le
     titre reste orphelin en bas de page et son contenu passe à la suivante.
  2. cantSplit sur les lignes de tableau, pour qu'une cellule ne soit jamais
     coupée entre deux pages (le glossaire y était sujet).
  3. tblHeader sur la première ligne de chaque tableau, pour que l'en-tête se
     répète en haut de chaque page d'un tableau long.

Usage : python3 outils/finitions_docx.py <fichier.docx>
"""
import re
import shutil
import sys
import zipfile

# Un paragraphe de style BodyText dont tous les runs portent <w:b/> et dont le
# texte tient en une ligne courte : c'est un intitulé d'encadré.
PARA = re.compile(r"<w:p\b[^>]*>.*?</w:p>", re.S)
RUN = re.compile(r"<w:r\b[^>]*>.*?</w:r>", re.S)
TEXTE = re.compile(r"<w:t[^>]*>(.*?)</w:t>", re.S)
LIGNE_TAB = re.compile(r"<w:tr\b[^>]*>", re.S)
# Pandoc bascule entre ces styles selon la position du paragraphe dans le bloc.
STYLES_CORPS = ("BodyText", "FirstParagraph", "Compact")


def est_intitule_encadre(para: str) -> bool:
    if not any(f'w:val="{s}"' in para for s in STYLES_CORPS):
        return False
    if "<w:numPr" in para or "<w:drawing" in para:
        return False
    runs = RUN.findall(para)
    if not runs:
        return False
    if any("<w:b " not in r and "<w:b/>" not in r and "<w:b />" not in r for r in runs):
        return False
    texte = "".join(TEXTE.findall(para)).strip()
    return 0 < len(texte) <= 80


def pose_keep_next(para: str) -> str:
    if "<w:keepNext" in para:
        return para
    return para.replace("<w:pPr>", "<w:pPr><w:keepNext/>", 1)


def traite_document(doc: str) -> tuple:
    encadres = 0
    figures = 0

    def remplace(m):
        nonlocal encadres, figures
        p = m.group(0)
        if "<w:drawing>" in p:
            # Une image doit rester solidaire de la légende qui la suit.
            figures += 1
            return pose_keep_next(p)
        if est_intitule_encadre(p):
            encadres += 1
            return pose_keep_next(p)
        return p

    doc = PARA.sub(remplace, doc)

    # Lignes de tableau : interdiction de les couper en deux pages. Le trPr
    # existe déjà quand pandoc y a mis tblHeader ; on complète alors sur place.
    morceaux = []
    lignes = 0
    pos = 0
    for m in LIGNE_TAB.finditer(doc):
        if doc[m.end():m.end() + 8] == "<w:trPr>":
            morceaux.append(doc[pos:m.end() + 8] + "<w:cantSplit/>")
            pos = m.end() + 8
        else:
            morceaux.append(doc[pos:m.end()] + "<w:trPr><w:cantSplit/></w:trPr>")
            pos = m.end()
        lignes += 1
    morceaux.append(doc[pos:])
    doc = "".join(morceaux)

    return doc, encadres, lignes, figures


def main():
    if len(sys.argv) < 2:
        print("usage : finitions_docx.py <fichier.docx>", file=sys.stderr)
        return 1
    chemin = sys.argv[1]
    temporaire = chemin + ".tmp"

    with zipfile.ZipFile(chemin) as source:
        noms = source.namelist()
        contenus = {n: source.read(n) for n in noms}

    doc = contenus["word/document.xml"].decode("utf-8")
    doc, encadres, lignes, figures = traite_document(doc)
    contenus["word/document.xml"] = doc.encode("utf-8")

    with zipfile.ZipFile(temporaire, "w", zipfile.ZIP_DEFLATED) as sortie:
        for n in noms:
            sortie.writestr(n, contenus[n])
    shutil.move(temporaire, chemin)

    print(f"  keepNext posé sur {encadres} intitulés d'encadré")
    print(f"  cantSplit posé sur {lignes} lignes de tableau")
    print(f"  keepNext posé sur {figures} images (légende solidaire)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
