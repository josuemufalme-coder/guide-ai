#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fabrique reference.docx : le modele de style applique par pandoc.

Sobre et academique. Empattements pour les titres (Cambria), sans empattements
pour le corps (Calibri), chasse fixe pour le code (Consolas). Ces trois polices
sont presentes sur toute installation recente de Word et de LibreOffice.

Le modele definit aussi le PIED DE PAGE avec numerotation, et une numerotation
qui demarre a 1 dans le corps du texte.

Usage : python3 outils/faire_reference_docx.py
Sortie : outils/reference.docx
"""

import re
import shutil
import subprocess
import zipfile
from pathlib import Path

RACINE = Path(__file__).resolve().parent
TRAVAIL = RACINE / ".ref_tmp"
SORTIE = RACINE / "reference.docx"

# --- Polices ---------------------------------------------------------------
TITRE = "Cambria"      # avec empattements
CORPS = "Calibri"      # sans empattements
CODE = "Consolas"      # chasse fixe

# --- Encre : noir et blanc strict ------------------------------------------
# Aucune couleur. La hierarchie repose sur la police, le corps, la casse et
# les filets. Les deux gris ci-dessous sont des nuances de noir, qui passent
# en niveaux de gris a l'impression comme a l'ecran.
ENCRE = "000000"       # noir, pour les titres et les filets
GRIS = "3F3F3F"        # gris fonce, pour les legendes
GRIS_CLAIR = "8C8C8C"  # gris clair, pour les filets secondaires


def police(nom, taille=None, gras=None, italique=None, couleur=None, casse=False):
    b = [f'<w:rFonts w:ascii="{nom}" w:hAnsi="{nom}" w:cs="{nom}"/>']
    if gras: b.append("<w:b/>")
    if italique: b.append("<w:i/>")
    if casse: b.append("<w:smallCaps/>")
    if couleur: b.append(f'<w:color w:val="{couleur}"/>')
    if taille: b.append(f'<w:sz w:val="{taille*2}"/><w:szCs w:val="{taille*2}"/>')
    return "".join(b)


def style(sid, nom, base, ppr, rpr, suivant=None):
    s = f'<w:style w:type="paragraph" w:customStyle="0" w:styleId="{sid}">'
    s += f'<w:name w:val="{nom}"/>'
    if base: s += f'<w:basedOn w:val="{base}"/>'
    if suivant: s += f'<w:next w:val="{suivant}"/>'
    s += f"<w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>"
    return s


# --- Definition des styles du manuel ---------------------------------------
STYLES = [
    # Corps de texte : sans empattements, interligne aere, justifie.
    ("BodyText", "Body Text", "Normal",
     '<w:spacing w:before="0" w:after="140" w:line="276" w:lineRule="auto"/>'
     '<w:jc w:val="both"/>',
     police(CORPS, 11)),

    ("FirstParagraph", "First Paragraph", "BodyText",
     '<w:spacing w:before="0" w:after="140" w:line="276" w:lineRule="auto"/><w:jc w:val="both"/>',
     police(CORPS, 11)),

    # Titre de PARTIE : page a part, grand, centre.
    ("Heading1", "heading 1", "Normal",
     '<w:keepNext/><w:pageBreakBefore/><w:spacing w:before="2400" w:after="600"/>'
     '<w:pBdr>'
     '<w:top w:val="single" w:sz="6" w:space="14" w:color="' + ENCRE + '"/>'
     '<w:bottom w:val="single" w:sz="6" w:space="14" w:color="' + ENCRE + '"/>'
     '</w:pBdr>'
     '<w:jc w:val="center"/><w:outlineLvl w:val="0"/>',
     police(TITRE, 24, gras=True, couleur=ENCRE, casse=True) +
     '<w:spacing w:val="30"/>', "BodyText"),

    # Titre de CHAPITRE : nouvelle page, filet sous le titre.
    ("Heading2", "heading 2", "Normal",
     '<w:keepNext/><w:pageBreakBefore/><w:spacing w:before="0" w:after="360"/>'
     '<w:pBdr><w:bottom w:val="single" w:sz="12" w:space="8" w:color="' + ENCRE + '"/></w:pBdr>'
     '<w:outlineLvl w:val="1"/>',
     police(TITRE, 19, gras=True, couleur=ENCRE), "BodyText"),

    # Titre de LECON : reste avec le paragraphe qui suit.
    ("Heading3", "heading 3", "Normal",
     '<w:keepNext/><w:keepLines/><w:spacing w:before="380" w:after="120"/>'
     '<w:outlineLvl w:val="2"/>',
     police(TITRE, 14, gras=True, couleur=ENCRE), "BodyText"),

    # Sous-partie dans une lecon.
    ("Heading4", "heading 4", "Normal",
     '<w:keepNext/><w:keepLines/><w:spacing w:before="260" w:after="100"/>'
     '<w:outlineLvl w:val="3"/>',
     police(TITRE, 12, gras=True, italique=True, couleur=ENCRE), "BodyText"),

    ("Heading5", "heading 5", "Normal",
     '<w:keepNext/><w:keepLines/><w:spacing w:before="200" w:after="80"/><w:outlineLvl w:val="4"/>',
     police(TITRE, 11, gras=True), "BodyText"),

    # Encadres : les citations Markdown servent d'encadre (exercices).
    ("BlockText", "Block Text", "Normal",
     '<w:pBdr>'
     '<w:top w:val="single" w:sz="4" w:space="6" w:color="' + GRIS_CLAIR + '"/>'
     '<w:bottom w:val="single" w:sz="4" w:space="6" w:color="' + GRIS_CLAIR + '"/>'
     '</w:pBdr>'
     '<w:spacing w:before="100" w:after="120" w:line="252" w:lineRule="auto"/>'
     '<w:ind w:left="284" w:right="170"/>',
     police(CORPS, 10)),

    # Legendes de figures.
    ("ImageCaption", "Image Caption", "Normal",
     '<w:keepLines/><w:spacing w:before="80" w:after="280"/><w:jc w:val="center"/>',
     police(CORPS, 9, italique=True, couleur=GRIS)),

    ("Caption", "Caption", "Normal",
     '<w:keepLines/><w:spacing w:before="80" w:after="280"/><w:jc w:val="center"/>',
     police(CORPS, 9, italique=True, couleur=GRIS)),

    # L'image elle-meme : centree, jamais separee de sa legende.
    ("Figure", "Figure", "Normal",
     '<w:keepNext/><w:spacing w:before="280" w:after="0"/><w:jc w:val="center"/>',
     police(CORPS, 11)),

    ("CaptionedFigure", "Captioned Figure", "Normal",
     '<w:keepNext/><w:keepLines/><w:spacing w:before="280" w:after="0"/><w:jc w:val="center"/>',
     police(CORPS, 11)),

    # Blocs de code : fond gris, filet, pas de justification.
    ("SourceCode", "Source Code", "Normal",
     '<w:pBdr><w:left w:val="single" w:sz="12" w:space="8" w:color="'
     + GRIS_CLAIR + '"/></w:pBdr>'
     '<w:shd w:val="clear" w:fill="F2F2F2"/>'
     '<w:spacing w:before="120" w:after="120" w:line="240" w:lineRule="auto"/>'
     '<w:ind w:left="170"/><w:jc w:val="left"/>',
     police(CODE, 9)),

    ("Compact", "Compact", "BodyText",
     '<w:spacing w:before="0" w:after="60" w:line="264" w:lineRule="auto"/><w:jc w:val="both"/>',
     police(CORPS, 11)),

    # Titre de la table des matieres.
    ("TOCHeading", "TOC Heading", "Normal",
     '<w:keepNext/><w:pageBreakBefore/><w:spacing w:before="0" w:after="360"/>'
     '<w:pBdr><w:bottom w:val="single" w:sz="6" w:space="12" w:color="'
     + ENCRE + '"/></w:pBdr>'
     '<w:jc w:val="center"/>',
     police(TITRE, 19, gras=True, couleur=ENCRE, casse=True) +
     '<w:spacing w:val="30"/>'),
]

STYLES_CAR = [
    ("VerbatimChar", "Verbatim Char", police(CODE, 9) + '<w:shd w:val="clear" w:fill="F0F0F0"/>'),
    ("BodyTextChar", "Body Text Char", police(CORPS, 11)),
]


def construire():
    if TRAVAIL.exists():
        shutil.rmtree(TRAVAIL)
    TRAVAIL.mkdir(parents=True)

    base = TRAVAIL / "base.docx"
    with base.open("wb") as f:
        subprocess.run(["pandoc", "--print-default-data-file", "reference.docx"],
                       check=True, stdout=f)
    with zipfile.ZipFile(base) as z:
        z.extractall(TRAVAIL / "x")
    base.unlink()
    x = TRAVAIL / "x"

    # ---- styles.xml -------------------------------------------------------
    p = x / "word" / "styles.xml"
    s = p.read_text(encoding="utf-8")

    # Police et langue par defaut
    s = s.replace('w:asciiTheme="minorHAnsi" w:eastAsiaTheme="minorHAnsi" '
                  'w:hAnsiTheme="minorHAnsi" w:cstheme="minorBidi"',
                  f'w:ascii="{CORPS}" w:eastAsia="{CORPS}" w:hAnsi="{CORPS}" w:cs="{CORPS}"')
    s = s.replace('w:val="en-US" w:eastAsia="en-US"', 'w:val="fr-FR" w:eastAsia="fr-FR"')

    # On retire les styles que l'on redefinit, puis on ajoute les notres.
    for sid, *_ in STYLES:
        s = re.sub(r'<w:style w:type="paragraph"[^>]*w:styleId="%s">.*?</w:style>' % sid,
                   "", s, flags=re.S)
    for sid, *_ in STYLES_CAR:
        s = re.sub(r'<w:style w:type="character"[^>]*w:styleId="%s">.*?</w:style>' % sid,
                   "", s, flags=re.S)

    ajout = "".join(style(sid, nom, base_, ppr, rpr, (suiv[0] if suiv else None))
                    for sid, nom, base_, ppr, rpr, *suiv in STYLES)
    ajout += "".join(
        f'<w:style w:type="character" w:styleId="{sid}"><w:name w:val="{nom}"/>'
        f'<w:rPr>{rpr}</w:rPr></w:style>' for sid, nom, rpr in STYLES_CAR)
    s = s.replace("</w:styles>", ajout + "</w:styles>")

    # Balayage final : aucune couleur ne doit subsister dans le gabarit, y
    # compris dans les styles herites de pandoc que le manuel n'emploie pas
    # (Title, Hyperlink, Subtitle...). Les couleurs de theme sont neutralisees.
    s = re.sub(r'\s*w:themeColor="[^"]*"', "", s)
    s = re.sub(r'\s*w:themeShade="[^"]*"', "", s)
    s = re.sub(r'\s*w:themeTint="[^"]*"', "", s)

    def en_noir(m):
        val = m.group(2).upper()
        if val in ("AUTO", "000000", GRIS, GRIS_CLAIR):
            return m.group(0)
        # On garde la clarte relative de la teinte d'origine.
        gris = round(0.299 * int(val[0:2], 16)
                     + 0.587 * int(val[2:4], 16)
                     + 0.114 * int(val[4:6], 16))
        return f'w:{m.group(1)} w:val="{gris:02X}{gris:02X}{gris:02X}"'

    s = re.sub(r'w:(color|fill) w:val="([0-9A-Fa-f]{6}|auto)"', en_noir, s)
    p.write_text(s, encoding="utf-8")

    # ---- pied de page avec numerotation -----------------------------------
    footer = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
              '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
              '<w:p><w:pPr><w:jc w:val="center"/>'
              f'<w:rPr><w:rFonts w:ascii="{CORPS}" w:hAnsi="{CORPS}"/>'
              f'<w:sz w:val="18"/><w:color w:val="{GRIS}"/></w:rPr></w:pPr>'
              f'<w:r><w:rPr><w:rFonts w:ascii="{CORPS}" w:hAnsi="{CORPS}"/>'
              f'<w:sz w:val="18"/><w:color w:val="{GRIS}"/></w:rPr>'
              '<w:fldChar w:fldCharType="begin"/></w:r>'
              '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
              '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
              '<w:r><w:t>1</w:t></w:r>'
              '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
              '</w:p></w:ftr>')
    (x / "word" / "footer1.xml").write_text(footer, encoding="utf-8")

    # Declaration du pied de page
    ct = x / "[Content_Types].xml"
    c = ct.read_text(encoding="utf-8")
    if "footer1.xml" not in c:
        c = c.replace("</Types>",
                      '<Override PartName="/word/footer1.xml" ContentType="application/'
                      'vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>')
        ct.write_text(c, encoding="utf-8")

    rels = x / "word" / "_rels" / "document.xml.rels"
    r = rels.read_text(encoding="utf-8")
    if "footer1.xml" not in r:
        r = r.replace("</Relationships>",
                      '<Relationship Id="rIdFooterManuel" Type="http://schemas.openxmlformats.org/'
                      'officeDocument/2006/relationships/footer" Target="footer1.xml"/></Relationships>')
        rels.write_text(r, encoding="utf-8")

    # ---- document.xml : sectPr du corps ------------------------------------
    # Le sectPr du modele fourni par pandoc est vide et auto-fermant. On le
    # remplace entierement : c'est lui qui gouverne la DERNIERE section du
    # document, c'est-a-dire le corps du texte. C'est donc lui qui porte le
    # pied de page numerote et la remise a 1 de la numerotation.
    d = x / "word" / "document.xml"
    doc = d.read_text(encoding="utf-8")
    complet = (
        "<w:sectPr>"
        '<w:footerReference w:type="default" r:id="rIdFooterManuel"/>'
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1418" w:right="1418" w:bottom="1418" w:left="1701" '
        'w:header="709" w:footer="709" w:gutter="0"/>'
        '<w:pgNumType w:start="1"/>'
        '<w:cols w:space="708"/>'
        "<w:docGrid w:linePitch=\"360\"/>"
        "</w:sectPr>")
    avant = doc
    doc = re.sub(r"<w:sectPr\s*/>", complet, doc)
    if doc == avant:
        doc = re.sub(r"<w:sectPr\b.*?</w:sectPr>", complet, doc, flags=re.S)
    assert complet in doc, "impossible de poser le sectPr du corps"
    d.write_text(doc, encoding="utf-8")

    # ---- reglages du document ----------------------------------------------
    # updateFields : Word et LibreOffice remplissent la table des matieres a
    # l'ouverture, sans intervention. Sans cela, le champ reste vide.
    st = x / "word" / "settings.xml"
    se = st.read_text(encoding="utf-8")
    ajouts = ""
    if "<w:updateFields" not in se:
        ajouts += '<w:updateFields w:val="true"/>'
    if "<w:defaultTabStop" not in se:
        ajouts += '<w:defaultTabStop w:val="708"/>'
    if ajouts:
        se = se.replace("</w:settings>", ajouts + "</w:settings>")
        st.write_text(se, encoding="utf-8")

    # ---- reconstruction de l'archive --------------------------------------
    if SORTIE.exists():
        SORTIE.unlink()
    with zipfile.ZipFile(SORTIE, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(x.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(x).as_posix())
    shutil.rmtree(TRAVAIL)
    print(f"reference.docx ecrit : {SORTIE}  ({SORTIE.stat().st_size} octets)")
    print(f"  titres      : {TITRE}")
    print(f"  corps       : {CORPS}")
    print(f"  code        : {CODE}")
    print(f"  format      : A4, pied de page numerote")


if __name__ == "__main__":
    construire()
