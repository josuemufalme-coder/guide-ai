#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
finitions_docx.py --- Corrections de mise en page appliquées au .docx produit
par pandoc, juste avant l'export PDF.

Pandoc ne sait exprimer aucun de ces réglages depuis le Markdown. Ils sont
donc posés directement dans l'OOXML :

  1. keepNext sur les titres d'encadré (paragraphes entièrement en gras et
     seuls sur leur ligne, comme « L'ESSENTIEL À RETENIR »). Sans cela le
     titre reste orphelin en bas de page et son contenu passe à la suivante.
  2. keepNext sur les images, pour qu'une légende ne soit jamais séparée de
     sa figure.
  3. cantSplit sur les lignes de tableau, pour qu'une cellule ne soit jamais
     coupée entre deux pages (le glossaire y était sujet).
  4. Corrections typographiques françaises : apostrophe courbe, espaces
     insécables devant la ponctuation double et à l'intérieur des guillemets,
     séparateur de milliers. Elles sont faites ici et non dans le Markdown
     parce que les tableaux de pandoc sont alignés au caractère près : y
     changer la largeur d'une cellule casserait la lecture du tableau.
  5. Réglages de document que pandoc régénère et perd : marges en vis-à-vis,
     césure automatique, mise à jour des champs à l'ouverture.
  6. En-tête courant portant le titre du chapitre en cours.

Usage : python3 outils/finitions_docx.py <fichier.docx>
"""
import hashlib
import pathlib
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


# ---------------------------------------------------------------------------
# 4. Typographie française
# ---------------------------------------------------------------------------
INSEC = "\u00a0"                     # espace insécable
PARA_STYLE = re.compile(r'<w:pStyle w:val="([^"]+)"')
# Le code ne doit pas être touché : ni les blocs, ni les extraits en ligne.
STYLES_CODE = ("SourceCode", "VerbatimChar")


def milliers(m):
    """Regroupe les chiffres par trois, à partir de la droite."""
    n = m.group(0)
    tranches = []
    while len(n) > 3:
        tranches.insert(0, n[-3:])
        n = n[:-3]
    tranches.insert(0, n)
    return INSEC.join(tranches)


def corrige_typographie(texte: str) -> str:
    # Apostrophe courbe. La droite est celle des machines à écrire ; aucun
    # livre français composé ne l'emploie. Dans l'OOXML elle est le plus
    # souvent écrite sous forme d'entité, d'où les trois formes traitées.
    for forme in ("&#39;", "&apos;", "'"):
        texte = texte.replace(forme, "\u2019")
    # Espace insécable devant la ponctuation double et devant le pourcentage.
    # On remplace l'espace existante : la longueur ne change pas.
    texte = re.sub(r"[ ]([;?!%»])", INSEC + r"\1", texte)
    texte = re.sub(r"[ ](:)(?=\s|$)", INSEC + r"\1", texte)
    texte = re.sub(r"[ ](:)(?=[^\d])", INSEC + r"\1", texte)
    # Espace insécable après le guillemet ouvrant.
    texte = texte.replace("«\u0020", "«" + INSEC)
    # Séparateur de milliers pour les entiers d'au moins cinq chiffres. En
    # deçà, on risquerait de retoucher une année ou un numéro d'article.
    texte = re.sub(r"(?<![\d\u00a0.,/-])\d{5,}(?![\d.,/-])", milliers, texte)
    # Les nombres déjà espacés reçoivent l'insécable.
    texte = re.sub(r"(\d)[ ](?=\d{3}(?!\d))", r"\1" + INSEC, texte)
    return texte


def recolle_ponctuation(doc: str) -> int:
    """Rattache la ponctuation double coupée entre deux runs.

    Quand pandoc scinde « mot : suite » en deux runs — parce que le gras
    commence au deux-points, par exemple — l'espace et le signe se retrouvent
    dans deux fragments distincts et la règle appliquée fragment par fragment
    ne les voit pas. On les recolle ici."""
    motif = re.compile(r"[ ](</w:t>(?:(?!<w:t)[\s\S])*?<w:t[^>]*>)([;:?!%»])")
    doc, n = motif.subn(INSEC + r"\1\2", doc)
    motif2 = re.compile(r"([;:?!%»])</w:t>")
    return doc, n


def applique_typographie(doc: str):
    """Parcourt les paragraphes et corrige le texte, sauf dans le code."""
    corriges = [0]

    def par_paragraphe(m):
        para = m.group(0)
        style = PARA_STYLE.search(para)
        if style and style.group(1) in STYLES_CODE:
            return para

        def par_run(mr):
            run = mr.group(0)
            if any(f'w:val="{s}"' in run for s in STYLES_CODE):
                return run

            def par_texte(mt):
                avant = mt.group(1)
                apres = corrige_typographie(avant)
                if apres != avant:
                    corriges[0] += 1
                return mt.group(0).replace(">" + avant + "<", ">" + apres + "<", 1)

            return re.sub(r"<w:t[^>]*>(.*?)</w:t>", par_texte, run, flags=re.S)

        return RUN.sub(par_run, para)

    return PARA.sub(par_paragraphe, doc), corriges[0]


# ---------------------------------------------------------------------------
# 5. Réglages de document que pandoc régénère et perd
# ---------------------------------------------------------------------------
def regle_document(settings: str) -> str:
    ajouts = (
        # Marges en vis-à-vis : la marge de reliure change de côté à chaque page.
        "<w:mirrorMargins/>"
        # Césure automatique : sans elle, une justification sur 15 cm laisse
        # des lézardes entre les mots.
        '<w:autoHyphenation w:val="true"/>'
        '<w:consecutiveHyphenLimit w:val="3"/>'
        '<w:hyphenationZone w:val="284"/>'
        '<w:doNotHyphenateCaps w:val="true"/>'
        # Demande au lecteur de recalculer la table des matières à l'ouverture.
        '<w:updateFields w:val="true"/>'
    )
    for balise in ("mirrorMargins", "autoHyphenation", "updateFields"):
        settings = re.sub(r"<w:%s[^>]*/>" % balise, "", settings)
    return settings.replace("</w:settings>", ajouts + "</w:settings>")


# ---------------------------------------------------------------------------
# 6. En-tête courant
# ---------------------------------------------------------------------------
EN_TETE = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    '<w:p><w:pPr>'
    '<w:pBdr><w:bottom w:val="single" w:sz="4" w:space="6" w:color="8C8C8C"/></w:pBdr>'
    '<w:spacing w:before="0" w:after="0"/><w:jc w:val="center"/>'
    '<w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>'
    '<w:i/><w:sz w:val="17"/><w:color w:val="3F3F3F"/></w:rPr>'
    "</w:pPr>"
    '<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>'
    '<w:i/><w:sz w:val="17"/><w:color w:val="3F3F3F"/></w:rPr>'
    '<w:fldChar w:fldCharType="begin"/></w:r>'
    '<w:r><w:instrText xml:space="preserve"> STYLEREF 2 \\* MERGEFORMAT </w:instrText></w:r>'
    '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
    '<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>'
    '<w:i/><w:sz w:val="17"/><w:color w:val="3F3F3F"/></w:rPr>'
    "<w:t>Comprendre et pratiquer l\u2019intelligence artificielle</w:t></w:r>"
    '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
    "</w:p></w:hdr>"
)


def pose_en_tete(contenus, doc):
    """Ajoute un en-tete courant a la section du corps, pas aux liminaires."""
    chemin = "word/header9.xml"
    rid = "rIdHeaderManuel"
    contenus[chemin] = EN_TETE.encode("utf-8")

    ct = contenus["[Content_Types].xml"].decode("utf-8")
    if "header9.xml" not in ct:
        ct = ct.replace(
            "</Types>",
            '<Override PartName="/word/header9.xml" ContentType="application/vnd'
            '.openxmlformats-officedocument.wordprocessingml.header+xml"/></Types>')
        contenus["[Content_Types].xml"] = ct.encode("utf-8")

    rels = contenus["word/_rels/document.xml.rels"].decode("utf-8")
    if rid not in rels:
        rels = rels.replace(
            "</Relationships>",
            f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/'
            'officeDocument/2006/relationships/header" Target="header9.xml"/>'
            "</Relationships>")
        contenus["word/_rels/document.xml.rels"] = rels.encode("utf-8")

    # La derniere sectPr du document est celle du corps : c'est la seule a
    # recevoir l'en-tete. Les pages liminaires restent nues.
    sections = list(re.finditer(r"<w:sectPr\b.*?</w:sectPr>", doc, re.S))
    assert sections, "aucune section trouvee"
    corps = sections[-1]
    if "headerReference" in corps.group(0):
        return doc, False
    remplace = corps.group(0).replace(
        "<w:sectPr>",
        f'<w:sectPr><w:headerReference w:type="default" r:id="{rid}"/>', 1)
    if remplace == corps.group(0):     # sectPr avec attributs
        remplace = re.sub(r"(<w:sectPr\b[^>]*>)",
                          r'\1<w:headerReference w:type="default" r:id="%s"/>' % rid,
                          corps.group(0), count=1)
    return doc[:corps.start()] + remplace + doc[corps.end():], True


# ---------------------------------------------------------------------------
# 7. Pages de couverture : sections a marges nulles
# ---------------------------------------------------------------------------
# Les deux images de couverture doivent occuper la page entiere, sans marge,
# sans en-tete et sans folio. Chacune forme donc sa propre section.
SECT_NUE = (
    "<w:sectPr>"
    '<w:footerReference w:type="default" r:id="rIdFooterVide"/>'
    '<w:headerReference w:type="default" r:id="rIdHeaderVide"/>'
    '<w:pgSz w:w="11906" w:h="16838"/>'
    '<w:pgMar w:top="0" w:right="0" w:bottom="0" w:left="0" '
    'w:header="0" w:footer="0" w:gutter="0"/>'
    '<w:cols w:space="708"/>'
    "</w:sectPr>")

PART_VIDE = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<w:{racine} xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    "<w:p><w:pPr><w:spacing w:before=\"0\" w:after=\"0\"/>"
    '<w:rPr><w:sz w:val="2"/></w:rPr></w:pPr></w:p>'
    "</w:{racine}>")


def declare_part(contenus, chemin, rid, racine, type_rel):
    contenus[chemin] = PART_VIDE.format(racine=racine).encode("utf-8")
    ct = contenus["[Content_Types].xml"].decode("utf-8")
    court = chemin.split("/")[-1]
    if court not in ct:
        ct = ct.replace(
            "</Types>",
            f'<Override PartName="/{chemin}" ContentType="application/vnd'
            f".openxmlformats-officedocument.wordprocessingml.{type_rel}"
            '+xml"/></Types>')
        contenus["[Content_Types].xml"] = ct.encode("utf-8")
    rels = contenus["word/_rels/document.xml.rels"].decode("utf-8")
    if rid not in rels:
        rels = rels.replace(
            "</Relationships>",
            f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/'
            f'officeDocument/2006/relationships/{type_rel}" Target="{court}"/>'
            "</Relationships>")
        contenus["word/_rels/document.xml.rels"] = rels.encode("utf-8")


# Une page A4 en EMU (914 400 par pouce).
A4_LARGEUR_EMU = 7560310   # 11906 twips
A4_HAUTEUR_EMU = 10692130  # 16838 twips


def identifiant_image(contenus, chemin_source):
    """rId de la relation qui pointe vers cette image.

    Pandoc renomme les media d'apres l'identifiant de relation : le nom du
    fichier d'origine a disparu du .docx. On retrouve donc l'image par son
    empreinte, en comparant les octets."""
    source = pathlib.Path(chemin_source)
    if not source.exists():
        return None
    empreinte = hashlib.sha256(source.read_bytes()).hexdigest()
    cible = None
    for nom, octets in contenus.items():
        if nom.startswith("word/media/") and \
                hashlib.sha256(octets).hexdigest() == empreinte:
            cible = nom[len("word/"):]
            break
    if cible is None:
        return None
    rels = contenus["word/_rels/document.xml.rels"].decode("utf-8")
    m = re.search(r'<Relationship[^>]*Target="%s"[^>]*>' % re.escape(cible), rels)
    if not m:
        return None
    ident = re.search(r'Id="([^"]+)"', m.group(0))
    return ident.group(1) if ident else None


def paragraphe_de(doc, marqueur):
    """Retourne le (debut, fin) du paragraphe portant cette image."""
    i = doc.find(marqueur)
    if i < 0:
        return None
    deb = doc.rfind("<w:p>", 0, i)
    deb2 = doc.rfind("<w:p ", 0, i)
    deb = max(deb, deb2)
    fin = doc.index("</w:p>", i) + len("</w:p>")
    return deb, fin


def pleine_page(para):
    """Ramene l'image du paragraphe aux dimensions exactes d'une page A4.

    Pandoc plafonne la taille des images a la justification du gabarit : une
    couverture s'y trouve reduite et laisse une marge blanche tout autour."""
    return re.sub(r'(<wp:extent|<a:ext)\s+cx="\d+"\s+cy="\d+"',
                  r'\1 cx="%d" cy="%d"' % (A4_LARGEUR_EMU, A4_HAUTEUR_EMU), para)


def pose_couvertures(contenus, doc):
    """Isole chaque couverture dans une section sans marge ni folio."""
    rid1 = identifiant_image(contenus, "media/couverture_1.png")
    rid4 = identifiant_image(contenus, "media/couverture_4.png")
    if not rid1 and not rid4:
        return doc, 0
    declare_part(contenus, "word/footer8.xml", "rIdFooterVide", "ftr", "footer")
    declare_part(contenus, "word/header8.xml", "rIdHeaderVide", "hdr", "header")
    posees = 0

    # --- premiere de couverture : elle ferme la section 1 -------------------
    bornes = paragraphe_de(doc, f'r:embed="{rid1}"') if rid1 else None
    if bornes:
        deb, fin = bornes
        para = pleine_page(doc[deb:fin])
        if "<w:pPr>" in para:
            neuf = para.replace("<w:pPr>", "<w:pPr>" + SECT_NUE, 1)
        else:
            ouvre = para[:para.index(">") + 1]
            neuf = ouvre + "<w:pPr>" + SECT_NUE + "</w:pPr>" + para[len(ouvre):]
        doc = doc[:deb] + neuf + doc[fin:]
        posees += 1

    # --- quatrieme : la section du corps doit se fermer juste avant ---------
    bornes = paragraphe_de(doc, f'r:embed="{rid4}"') if rid4 else None
    if bornes:
        deb, fin = bornes
        doc = doc[:deb] + pleine_page(doc[deb:fin]) + doc[fin:]
        bornes = paragraphe_de(doc, f'r:embed="{rid4}"')
        deb, fin = bornes
        corps = re.search(r"<w:sectPr\b(?:(?!</w:sectPr>).)*</w:sectPr>\s*</w:body>",
                          doc, re.S)
        assert corps, "sectPr du corps introuvable"
        sect_corps = corps.group(0).replace("</w:body>", "").strip()
        # On referme le corps sur le dernier paragraphe qui precede la couverture.
        precedent = doc.rfind("</w:p>", 0, deb)
        assert precedent > 0, "aucun paragraphe avant la quatrieme"
        ouvre_prec = max(doc.rfind("<w:p>", 0, precedent), doc.rfind("<w:p ", 0, precedent))
        para_prec = doc[ouvre_prec:precedent + len("</w:p>")]
        if "<w:pPr>" in para_prec:
            neuf_prec = para_prec.replace("<w:pPr>", "<w:pPr>" + sect_corps, 1)
        else:
            ouvre = para_prec[:para_prec.index(">") + 1]
            neuf_prec = ouvre + "<w:pPr>" + sect_corps + "</w:pPr>" + para_prec[len(ouvre):]
        doc = (doc[:ouvre_prec] + neuf_prec
               + doc[precedent + len("</w:p>"):])
        # et la section finale, celle de la quatrieme, devient nue.
        doc = doc[:corps.start() + (len(neuf_prec) - len(para_prec))] if False else doc
        doc = re.sub(r"<w:sectPr\b(?:(?!</w:sectPr>).)*</w:sectPr>(\s*</w:body>)",
                     SECT_NUE + r"\1", doc, count=1, flags=re.S)
        posees += 1

    return doc, posees


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
    doc, typo = applique_typographie(doc)
    doc, recolles = recolle_ponctuation(doc)
    doc, entete = pose_en_tete(contenus, doc)
    doc, couvertures = pose_couvertures(contenus, doc)
    for part in ("word/header9.xml", "word/footer8.xml", "word/header8.xml"):
        if part in contenus and part not in noms:
            noms = noms + [part]
    contenus["word/document.xml"] = doc.encode("utf-8")

    reglages = contenus["word/settings.xml"].decode("utf-8")
    contenus["word/settings.xml"] = regle_document(reglages).encode("utf-8")

    with zipfile.ZipFile(temporaire, "w", zipfile.ZIP_DEFLATED) as sortie:
        for n in noms:
            sortie.writestr(n, contenus[n])
    shutil.move(temporaire, chemin)

    print(f"  keepNext posé sur {encadres} intitulés d'encadré")
    print(f"  cantSplit posé sur {lignes} lignes de tableau")
    print(f"  keepNext posé sur {figures} images (légende solidaire)")
    print(f"  typographie française corrigée dans {typo} fragments de texte")
    print(f"  ponctuation double recollée entre deux runs : {recolles} cas")
    print(f"  en-tête courant : {'posé' if entete else 'déjà présent'}")
    print("  marges en vis-à-vis, césure automatique et mise à jour des champs activées")
    print(f"  couvertures en pleine page : {couvertures} sur 2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
