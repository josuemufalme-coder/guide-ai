#!/usr/bin/env bash
# =============================================================================
#  build.sh --- Régénère le manuel au format .docx depuis le Markdown.
#
#  Rejouable à volonté : chaque exécution repart du Markdown et reconstruit
#  tout. Aucun fichier intermédiaire n'est conservé entre deux exécutions.
#
#  Usage :
#     ./build.sh              construit le .docx
#     ./build.sh --pdf        construit aussi le PDF (nécessite LibreOffice)
#     ./build.sh --controle   construit, produit le PDF et rasterise les pages
#
#  Prérequis : pandoc. Pour le PDF : libreoffice. Pour le contrôle : python3
#  avec pymupdf.
# =============================================================================
set -euo pipefail

RACINE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$RACINE"

SOURCE="Guide_Intelligence_Artificielle.md"
MODELE="outils/reference.docx"
SORTIE="Guide_Intelligence_Artificielle_publiable.docx"
PDF="${SORTIE%.docx}.pdf"

rouge()  { printf '\033[31m%s\033[0m\n' "$*"; }
vert()   { printf '\033[32m%s\033[0m\n' "$*"; }
info()   { printf '  %s\n' "$*"; }

# --- 1. Vérifications préalables --------------------------------------------
command -v pandoc >/dev/null || { rouge "pandoc est introuvable."; exit 1; }
[ -f "$SOURCE" ] || { rouge "Source introuvable : $SOURCE"; exit 1; }

# Le modèle de style est reconstruit s'il manque, ou si son générateur a été
# modifié depuis : sans cela une retouche des styles resterait sans effet.
if [ ! -f "$MODELE" ] || [ outils/faire_reference_docx.py -nt "$MODELE" ]; then
  info "Reconstruction du modèle de styles…"
  python3 outils/faire_reference_docx.py
fi

# --- 2. Génération du .docx --------------------------------------------------
vert "Construction du document…"
pandoc "$SOURCE" \
  --from=markdown+raw_attribute \
  --to=docx \
  --reference-doc="$MODELE" \
  --resource-path=.:media \
  --highlight-style=tango \
  --metadata lang=fr-FR \
  --output="$SORTIE"

# --- 2 bis. Réglages de mise en page que le Markdown ne sait pas exprimer ----
python3 outils/finitions_docx.py "$SORTIE"

TAILLE=$(du -h "$SORTIE" | cut -f1)
MOTS=$(wc -w < "$SOURCE")
info "$SORTIE  ($TAILLE, source de $MOTS mots)"

# --- 3. Contrôles automatiques sur le résultat --------------------------------
python3 - "$SORTIE" <<'PYCHK'
import re, sys, zipfile
chemin = sys.argv[1]
with zipfile.ZipFile(chemin) as z:
    noms = z.namelist()
    doc = z.read("word/document.xml").decode("utf-8")
    styles = z.read("word/styles.xml").decode("utf-8")
ctrl = {
    "pied de page présent"      : any(n.startswith("word/footer") for n in noms),
    "champ de table des matières": "TOC \\o" in doc or "TOC \\\\o" in doc,
    "deux sections distinctes"   : doc.count("<w:sectPr") >= 2,
    "images intégrées"           : sum(1 for n in noms if n.startswith("word/media/")) == 17,
    "style de code défini"       : 'w:styleId="SourceCode"' in styles,
    "titres de niveau 1 à 3"     : all(f'w:styleId="Heading{i}"' in styles for i in (1, 2, 3)),
}
for k, v in ctrl.items():
    print(f"  [{'OK ' if v else 'NON'}] {k}")
if not all(ctrl.values()):
    sys.exit(1)
PYCHK

# --- 4. PDF et contrôle visuel, à la demande ---------------------------------
if [ "${1:-}" = "--pdf" ] || [ "${1:-}" = "--controle" ]; then
  command -v soffice >/dev/null || { rouge "LibreOffice introuvable, PDF ignoré."; exit 0; }
  vert "Conversion en PDF…"
  # L'export passe par une macro qui calcule d'abord la table des matières :
  # une conversion sans interface ne met pas les champs à jour.
  python3 outils/exporter_pdf.py "$SORTIE"
fi

if [ "${1:-}" = "--controle" ]; then
  vert "Rastérisation des pages…"
  python3 outils/controle_visuel.py "$PDF"
fi

vert "Terminé."
