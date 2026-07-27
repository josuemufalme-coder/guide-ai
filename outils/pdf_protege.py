#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pdf_protege.py --- Produit une version du manuel destinee a la relecture.

Le fichier obtenu s'ouvre sans mot de passe, mais il est chiffre en AES-256 et
ses permissions sont toutes refusees : ni impression, ni copie de texte, ni
modification, ni annotation, ni extraction de pages. Un mot de passe
proprietaire, tire au hasard, est le seul moyen de lever ces restrictions ; il
est ecrit dans un fichier que vous gardez et qui n'entre pas dans le depot.

CE QUE CELA PROTEGE, ET CE QUE CELA NE PROTEGE PAS
Les permissions d'un PDF sont declaratives : elles sont respectees par les
lecteurs honnetes (Acrobat, Aperçu, Edge, Chrome, les liseuses). Elles
n'empechent pas quelqu'un de determine de contourner la mesure, ni de
photographier l'ecran. C'est une barriere contre la reutilisation
distraite, pas contre la contrefaçon. Le vrai rempart reste la mention de
copyright de la page de droits et le depot legal.

Usage :
    python3 outils/pdf_protege.py [source.pdf] [sortie.pdf]
"""
import secrets
import string
import sys
from pathlib import Path

import fitz

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "Guide_Intelligence_Artificielle_publiable.pdf"
SORTIE = RACINE / "Guide_Intelligence_Artificielle_relecture.pdf"
CLE = RACINE / "mot_de_passe_proprietaire.txt"

# Aucune permission accordee : tout est refuse au lecteur.
PERMISSIONS = 0


def mot_de_passe(longueur=24):
    alphabet = string.ascii_letters + string.digits + "!@#%-_=+"
    return "".join(secrets.choice(alphabet) for _ in range(longueur))


def main():
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else SOURCE
    sortie = Path(sys.argv[2]) if len(sys.argv) > 2 else SORTIE
    if not source.exists():
        print(f"Source introuvable : {source}", file=sys.stderr)
        return 1

    proprietaire = mot_de_passe()
    doc = fitz.open(source)

    # Les metadonnees accompagnent le fichier partout ou il circule.
    doc.set_metadata({
        "title": "Comprendre et pratiquer l'intelligence artificielle",
        "author": "MUFALME BULENDA Josué",
        "subject": "Manuel de formation --- exemplaire de relecture, "
                   "diffusion restreinte",
        "keywords": "intelligence artificielle, manuel, relecture",
        "creator": "MUFALME BULENDA Josué",
        "producer": "MUFALME BULENDA Josué --- tous droits réservés",
    })

    doc.save(
        sortie,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        owner_pw=proprietaire,   # leve les restrictions
        user_pw="",              # ouverture libre, sans mot de passe
        permissions=PERMISSIONS,
        garbage=3,
        deflate=True,
    )
    doc.close()

    CLE.write_text(
        "Mot de passe proprietaire du fichier de relecture\n"
        f"Fichier  : {sortie.name}\n"
        f"Mot de passe : {proprietaire}\n\n"
        "Il ne sert qu'a VOUS, pour lever les restrictions si besoin.\n"
        "Ne le communiquez a personne : le transmettre annule la protection.\n"
        "Ce fichier est exclu du depot git.\n",
        encoding="utf-8")

    # Verification : on rouvre et on relit les permissions reellement posees.
    verif = fitz.open(sortie)
    controles = {
        "chiffre": verif.is_encrypted or verif.metadata.get("encryption"),
        "s'ouvre sans mot de passe": not verif.needs_pass,
        "impression refusee": not verif.permissions & fitz.PDF_PERM_PRINT,
        "copie refusee": not verif.permissions & fitz.PDF_PERM_COPY,
        "modification refusee": not verif.permissions & fitz.PDF_PERM_MODIFY,
        "annotation refusee": not verif.permissions & fitz.PDF_PERM_ANNOTATE,
        "extraction de pages refusee":
            not verif.permissions & fitz.PDF_PERM_ASSEMBLE,
    }
    for k, v in controles.items():
        print(f"  [{'OK ' if v else 'NON'}] {k}")
    print(f"  {verif.page_count} pages, "
          f"{sortie.stat().st_size / 1024:.0f} Ko --- {sortie.name}")
    print(f"  chiffrement : {verif.metadata.get('encryption')}")
    verif.close()
    return 0 if all(controles.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
