#!/usr/bin/env python3
"""Composition de l'EPUB — phase 9.

L'EPUB se compose depuis la même source que le PDF, et par le même chemin :
un fichier Markdown, un fichier XHTML. Aucun convertisseur extérieur n'est
appelé, pour la même raison qu'ailleurs dans ce dépôt — ce qui produit le
livrable doit être lisible, versionné et rejouable.

Ce que l'EPUB fait autrement que le PDF, et pourquoi :

    la page n'existe pas       ni folio, ni titre courant, ni imposition ; le
                               lecteur choisit son corps et sa mesure
    les espaces restent Unicode  la source porte déjà ses insécables : elles
                               passent telles quelles, sans commande de TeX
    les schémas restent en chasse fixe  ce sont des dessins de signes ; ils
                               sont enfermés dans un bloc qui défile
                               horizontalement plutôt que de déborder

Usage : python3 composer-epub.py [--source src] [--sortie build/livrable]
"""
import argparse
import html
import re
import sys
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

TITRE = ("Entreprendre au Congo — Comprendre l'entrepreneuriat "
         "et savoir par où commencer")
AUTRICE = "Ruth ZADI Pukuta"
LANGUE = "fr"

STYLE = """\
html { font-size: 100%; }
body { margin: 0 5%; line-height: 1.5; text-align: justify;
       hyphens: auto; -webkit-hyphens: auto; }
h1 { font-size: 1.6em; line-height: 1.2; margin: 2em 0 1em; text-align: left; }
h2 { font-size: 1.15em; margin: 1.8em 0 0.4em; text-align: left; }
h3 { font-size: 1em; margin: 1.2em 0 0.3em; text-align: left; }
p { margin: 0 0 0.7em; }
p.partie { margin: 3em 0 0; font-size: 1.2em; font-weight: bold;
           letter-spacing: 0.05em; text-align: left; }
aside { margin: 1.4em 0; padding: 0.8em 1em; font-size: 0.94em; }
aside.realite-congolaise, aside.a-faire {
    border-top: 1px solid #888; border-bottom: 1px solid #888; }
aside > p.titre { font-weight: bold; margin-bottom: 0.5em; }
pre { font-size: 0.8em; line-height: 1.35; overflow-x: auto;
      white-space: pre; margin: 1.4em 0; }
table { border-collapse: collapse; margin: 1.4em 0; font-size: 0.92em;
        width: 100%; }
th, td { border-bottom: 1px solid #bbb; padding: 0.3em 0.5em;
         text-align: left; vertical-align: top; }
th { border-bottom: 1px solid #444; }
sup { font-size: 0.7em; }
"""

GABARIT_XHTML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{langue}" lang="{langue}">
<head>
<meta charset="utf-8"/>
<title>{titre}</title>
<link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
{corps}
</body>
</html>
"""

CELLULES = re.compile(r"^\|(.*)\|\s*$")
NUMERO = re.compile(r"^(\d{1,2})\. ")
FILET = re.compile(r"^\|[\s|:-]+\|\s*$")


def en_xhtml(texte):
    """Le Markdown en ligne du manuscrit, en XHTML."""
    texte = html.escape(texte, quote=False)
    texte = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", texte)
    texte = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", texte)
    texte = re.sub(r"\[\^(\d+)\]",
                   r'<sup><a href="90-notes-et-sources.xhtml#note\1"'
                   r' id="appel\1">\1</a></sup>', texte)
    return texte


def convertir(chemin):
    """Un fichier du manuscrit en corps XHTML, et son titre."""
    sortie, titre_du_fichier = [], None
    liste, tableau, schema, encadre = None, [], None, False

    def fermer_liste():
        nonlocal liste
        if liste:
            sortie.append(f"</{liste}>")
            liste = None

    def fermer_tableau():
        if not tableau:
            return
        entete, rangees = tableau[0], tableau[1:]
        sortie.append("<table>")
        sortie.append("<thead><tr>"
                      + "".join(f"<th>{en_xhtml(c)}</th>" for c in entete)
                      + "</tr></thead>")
        sortie.append("<tbody>")
        for rangee in rangees:
            sortie.append("<tr>"
                          + "".join(f"<td>{en_xhtml(c)}</td>" for c in rangee)
                          + "</tr>")
        sortie.append("</tbody></table>")
        tableau.clear()

    for ligne in chemin.read_text(encoding="utf-8").split("\n"):
        nue = ligne.rstrip()

        if schema is not None:
            if nue.startswith("```"):
                sortie.append("<pre>" + html.escape("\n".join(schema)) + "</pre>")
                schema = None
            else:
                schema.append(nue)
            continue

        if CELLULES.match(nue):
            # Un tableau referme la liste qui le précède : laissé ouvert, il se
            # retrouverait à l'intérieur d'un <li>, ce que la norme refuse.
            fermer_liste()
            if FILET.match(nue):
                continue
            tableau.append([c.strip() for c in nue.strip("|").split("|")])
            continue
        if tableau:
            fermer_tableau()

        if not nue:
            continue
        if nue.startswith("```schema"):
            fermer_liste()
            schema = []
        elif nue.startswith("<!--"):
            sortie.append(f'<p class="partie">{en_xhtml(nue.strip("<!->").strip())}</p>')
        elif nue.startswith("# "):
            fermer_liste()
            titre_du_fichier = nue[2:].strip()
            sortie.append(f"<h1>{en_xhtml(titre_du_fichier)}</h1>")
        elif nue.startswith("### "):
            fermer_liste()
            sortie.append(f"<h3>{en_xhtml(nue[4:])}</h3>")
        elif nue.startswith("## "):
            fermer_liste()
            if titre_du_fichier is None:
                titre_du_fichier = nue[3:].strip()
            sortie.append(f"<h2>{en_xhtml(nue[3:])}</h2>")
        elif nue.startswith("::: {"):
            fermer_liste()
            sorte = re.search(r'type="([^"]*)"', nue)
            titre = re.search(r'titre="([^"]*)"', nue)
            sortie.append(f'<aside class="{sorte.group(1) if sorte else "aparte"}">')
            if titre:
                sortie.append(f'<p class="titre">{en_xhtml(titre.group(1))}</p>')
            encadre = True
        elif nue == ":::":
            fermer_liste()
            sortie.append("</aside>")
            encadre = False
        elif nue.startswith("- "):
            if liste != "ul":
                fermer_liste()
                sortie.append("<ul>")
                liste = "ul"
            sortie.append(f"<li>{en_xhtml(nue[2:])}</li>")
        elif NUMERO.match(nue):
            rang = int(NUMERO.match(nue).group(1))
            if liste != "ol":
                fermer_liste()
                # Une énumération que le manuscrit reprend après un tableau ou
                # un paragraphe garde son rang : sans « start », le navigateur
                # la fait repartir de 1.
                sortie.append("<ol>" if rang == 1 else '<ol start="%d">' % rang)
                liste = "ol"
            sortie.append("<li>%s</li>" % en_xhtml(NUMERO.sub("", nue)))
        else:
            fermer_liste()
            sortie.append(f"<p>{en_xhtml(nue)}</p>")

    fermer_tableau()
    fermer_liste()
    if encadre:
        sortie.append("</aside>")
    return "\n".join(sortie), titre_du_fichier or chemin.stem


def ancrer_les_notes(corps):
    """Les cinq notes de la fin reçoivent l'ancre que leurs appels visent.

    Les notes sont une liste numérotée : l'ancre se pose donc sur l'article, et
    son numéro suit le rang, non le texte — le manuscrit ne répète pas « 1. »
    dans une liste que le Markdown numérote déjà.
    """
    compteur = iter(range(1, 100))
    return re.sub(r"<li>",
                  lambda m: f'<li id="note{next(compteur)}">', corps)


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--source", type=Path, default=Path("src"))
    analyseur.add_argument("--sortie", type=Path, default=Path("build/livrable"))
    analyseur.add_argument("--couverture", type=Path,
                           default=Path("build/couverture/ENTREPRENDRE-AU-CONGO-premiere.png"))
    options = analyseur.parse_args()

    fichiers = sorted(options.source.glob("*.md"))
    identifiant = "urn:uuid:" + str(uuid.uuid5(
        uuid.NAMESPACE_URL, "https://entreprendre-au-congo/" + TITRE))
    horodatage = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    pages, navigation = [], []
    for fichier in fichiers:
        corps, titre = convertir(fichier)
        if fichier.name.startswith("90-"):
            corps = ancrer_les_notes(corps)
        nom = fichier.stem + ".xhtml"
        pages.append((nom, GABARIT_XHTML.format(langue=LANGUE,
                                                titre=html.escape(titre),
                                                corps=corps)))
        # Les liminaires n'entrent pas dans la table : ce sont la page de titre
        # et la page de droits, que le lecteur ne cherche pas dans un sommaire.
        if not fichier.name.startswith("00a"):
            navigation.append((nom, titre))

    couverture = options.couverture.exists()
    manifeste = "\n".join(
        f'    <item id="p{index}" href="{nom}" media-type="application/xhtml+xml"/>'
        for index, (nom, _) in enumerate(pages))
    colonne = "\n".join(f'    <itemref idref="p{index}"/>'
                        for index in range(len(pages)))
    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="id">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="id">{identifiant}</dc:identifier>
    <dc:title>{html.escape(TITRE)}</dc:title>
    <dc:creator>{html.escape(AUTRICE)}</dc:creator>
    <dc:language>{LANGUE}</dc:language>
    <meta property="dcterms:modified">{horodatage}</meta>
{'    <meta name="cover" content="couverture"/>' if couverture else ''}
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="style" href="style.css" media-type="text/css"/>
{'    <item id="couverture" href="couverture.png" media-type="image/png" properties="cover-image"/>' if couverture else ''}
{manifeste}
  </manifest>
  <spine>
{colonne}
  </spine>
</package>
"""

    entrees = "\n".join(f'      <li><a href="{nom}">{html.escape(titre)}</a></li>'
                        for nom, titre in navigation)
    nav = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"
      xml:lang="{LANGUE}" lang="{LANGUE}">
<head><meta charset="utf-8"/><title>Table des matières</title></head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>Table des matières</h1>
    <ol>
{entrees}
    </ol>
  </nav>
</body>
</html>
"""

    options.sortie.mkdir(parents=True, exist_ok=True)
    chemin = options.sortie / "ENTREPRENDRE-AU-CONGO.epub"
    with zipfile.ZipFile(chemin, "w") as archive:
        # Le mimetype vient en premier et n'est pas compressé : la norme l'exige,
        # c'est ce qui permet de reconnaître un EPUB sans le décompresser.
        archive.writestr("mimetype", "application/epub+zip",
                         compress_type=zipfile.ZIP_STORED)
        archive.writestr("META-INF/container.xml",
                         '<?xml version="1.0" encoding="utf-8"?>\n'
                         '<container version="1.0" '
                         'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
                         '  <rootfiles>\n'
                         '    <rootfile full-path="OEBPS/content.opf" '
                         'media-type="application/oebps-package+xml"/>\n'
                         '  </rootfiles>\n</container>\n',
                         compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr("OEBPS/content.opf", opf, zipfile.ZIP_DEFLATED)
        archive.writestr("OEBPS/nav.xhtml", nav, zipfile.ZIP_DEFLATED)
        archive.writestr("OEBPS/style.css", STYLE, zipfile.ZIP_DEFLATED)
        if couverture:
            archive.writestr("OEBPS/couverture.png",
                             options.couverture.read_bytes(), zipfile.ZIP_DEFLATED)
        for nom, contenu in pages:
            archive.writestr("OEBPS/" + nom, contenu, zipfile.ZIP_DEFLATED)

    print(f"  {len(pages)} document(s), {len(navigation)} entrée(s) de table")
    print(f"  couverture : {'incorporée' if couverture else 'absente'}")
    print(f"  livrable   : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
