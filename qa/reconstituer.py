#!/usr/bin/env python3
"""Reconstitution du manuscrit Markdown — phase 0.

Le fichier source `ENTREPRENDRE-AU-CONGO.md` n'existe plus. Le §2 du cahier des
charges prévoit ce cas : sa reconstitution est la première tâche du projet.

MÉTHODE. Le texte vient de l'extraction fournie par l'auteure
(`source/ENTREPRENDRE-AU-CONGO-extraction.txt`), qui sert de référence
d'intégrité : la recomposition doit la restituer signe pour signe (voir
`qa/verifier-integrite.py`). Mais cette extraction est plate : elle ne marque
ni les fins de paragraphe, ni les niveaux de titre, ni les encadrés, ni
l'italique. Le PDF, que le cahier désigne comme document de contrôle, les porte
tous — non pas dans son texte, mais dans sa géométrie et ses polices :

    hauteur  style      rôle
       31    gras       titre de partie
       26    gras       titre de l'ouvrage (page de titre)
       22    gras       titre de chapitre
       18    gras       titre de section
       15    romain     corps de texte
       15    gras       sous-titre, ou gras dans le corps
       15    italique   italique dans le corps
       15    mono       schéma en art ASCII
       13    *          encadré (« Réalité congolaise », « À faire cette semaine »)
       12    romain     titre courant, page de copyright

    écart vertical entre deux lignes de corps :
       22    même paragraphe
       31    paragraphe suivant
       49    titre à suivre
        0    même ligne (mots écartés par la justification)

C'est ce croisement — le texte de l'extraction, la structure du PDF — qui permet
une reconstitution fidèle. Aucun des deux ne suffit seul.

Sortie : un fichier Markdown par chapitre dans `src/`.
Prérequis : poppler-utils (pdftohtml).
"""
import argparse
import collections
import html
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

# Préfixes de sous-ensemble des polices incorporées dans le PDF.
STYLES = {
    "OHBCLI": "romain",
    "QIJQQE": "gras",
    "LFPLDV": "italique",
    "ZVGULQ": "mono",
}

# Hauteurs de ligne, dans l'espace de coordonnées de pdftohtml.
TITRE_PARTIE, TITRE_OUVRAGE, TITRE_CHAPITRE = 31, 26, 22
TITRE_SECTION, CORPS, ENCADRE, LIMINAIRE = 18, 15, 13, 12

# Un écart vertical supérieur à 1,8 fois la hauteur de la ligne ouvre un bloc.
# Vérifié sur tout l'ouvrage : corps 22/23 contre 31 ; encadré 20/21 contre 29 ;
# titre de chapitre 34 ; titre de partie 47.
FACTEUR_BLOC = 1.8
TOLERANCE_LIGNE = 3        # écart de `top` en deçà duquel deux fragments partagent une ligne
ESPACE_ENTRE_FRAGMENTS = 1 # écart horizontal en deçà duquel deux fragments se touchent
RETRAIT_CONTINUATION = 8   # au-delà, la ligne poursuit l'item précédent
FIN_DE_PHRASE = (".", "!", "?", "»", ":", ";")
SEUIL_COLONNE = 25         # écart horizontal minimal entre deux cellules d'un tableau
TOLERANCE_COLONNE = 8      # écart en deçà duquel deux cellules sont dans la même colonne
PUCE = "•"
ITEM_NUMEROTE = re.compile(r"^\d{1,2}\.\s")
POINTS_DE_CONDUITE = ". . ."
HAUTEUR_APPEL_NOTE = 11    # les appels de notes sont composés en 6,65 pt


class Fragment:
    """Un morceau de texte homogène en police, tel que pdftohtml le livre."""

    __slots__ = ("top", "gauche", "largeur", "hauteur", "style", "texte")

    def __init__(self, element, style):
        self.top = int(element.get("top"))
        self.gauche = int(element.get("left"))
        self.largeur = int(element.get("width"))
        self.hauteur = int(element.get("height"))
        self.style = style
        self.texte = html.unescape("".join(element.itertext()))

    @property
    def droite(self):
        return self.gauche + self.largeur


class Ligne:
    """Les fragments qui partagent une même ligne de base."""

    def __init__(self, fragments, page=0):
        self.page = page
        self.fragments = sorted(fragments, key=lambda f: f.gauche)
        self.top = min(f.top for f in fragments)
        self.gauche = self.fragments[0].gauche
        self.droite = max(f.droite for f in fragments)
        self.hauteur = collections.Counter(f.hauteur for f in fragments).most_common(1)[0][0]

    @property
    def style_dominant(self):
        poids = collections.Counter()
        for f in self.fragments:
            poids[f.style] += len(f.texte)
        return poids.most_common(1)[0][0]

    def texte_brut(self):
        morceaux = []
        for precedent, fragment in zip([None] + self.fragments, self.fragments):
            if precedent is not None and fragment.gauche - precedent.droite > ESPACE_ENTRE_FRAGMENTS:
                morceaux.append(" ")
            morceaux.append(fragment.texte)
        return "".join(morceaux).strip()

    def suites_de_style(self):
        """Regroupe les fragments voisins de même style.

        La justification éclate un passage en gras en autant de fragments que de
        mots ; sans ce regroupement, chacun recevrait ses propres astérisques.
        """
        suites = []
        for precedent, fragment in zip([None] + self.fragments, self.fragments):
            colle = (precedent is not None
                     and fragment.gauche - precedent.droite <= ESPACE_ENTRE_FRAGMENTS)
            appel = (fragment.hauteur <= HAUTEUR_APPEL_NOTE
                     and fragment.texte.strip().isdigit())
            style = "appel" if appel else fragment.style
            if suites and suites[-1][0] == style:
                suites[-1][1] += ("" if colle else " ") + fragment.texte
            else:
                if suites and not colle:
                    suites[-1][1] += " "
                suites.append([style, fragment.texte])
        return suites

    def texte_balise(self):
        """Le texte de la ligne, italiques, gras et appels de notes en Markdown."""
        suites = self.suites_de_style()
        # Un titre composé tout entier dans un seul style n'a pas à être balisé :
        # son niveau le dit déjà. Une ligne de corps, si. Une phrase en gras qui
        # occupe une ligne entière reste du gras, et doit le rester dans le texte.
        uniforme = (self.hauteur != CORPS
                    and len({s for s, c in suites if c.strip()}) <= 1)
        morceaux = []
        for style, contenu in suites:
            if not contenu.strip():
                morceaux.append(contenu)
            elif style == "appel":
                morceaux.append(f"[^{contenu.strip()}]")
            elif uniforme:
                morceaux.append(contenu)
            elif style == "italique":
                morceaux.append(_baliser(contenu, "*"))
            elif style == "gras":
                morceaux.append(_baliser(contenu, "**"))
            else:
                morceaux.append(contenu)
        return "".join(morceaux).strip()


def _baliser(contenu, marque):
    """Pose une marque Markdown sans avaler les espaces de bordure."""
    gauche = len(contenu) - len(contenu.lstrip())
    droite = len(contenu) - len(contenu.rstrip())
    return (contenu[:gauche] + marque + contenu.strip() + marque
            + (contenu[len(contenu) - droite:] if droite else ""))


def lire_pages(pdfs):
    """Rend la liste des pages, chacune étant une liste de Ligne."""
    pages = []
    for pdf in pdfs:
        xml = subprocess.run(["pdftohtml", "-xml", "-stdout", "-i", "-hidden", str(pdf)],
                             capture_output=True, text=True, check=True).stdout
        styles = {}  # les fontspec ne sont déclarés qu'à leur première apparition
        for page in ET.fromstring(xml).iter("page"):
            for spec in page.iter("fontspec"):
                styles[spec.get("id")] = STYLES.get(spec.get("family", "")[:6], "romain")
            fragments = [Fragment(t, styles.get(t.get("font"), "romain"))
                         for t in page.iter("text")
                         if "".join(t.itertext()).strip()]
            groupes = collections.defaultdict(list)
            for fragment in fragments:
                clef = next((c for c in groupes if abs(c - fragment.top) <= TOLERANCE_LIGNE),
                            fragment.top)
                groupes[clef].append(fragment)
            numero = len(pages) + 1
            pages.append([Ligne(g, numero) for _, g in sorted(groupes.items())])
    return pages


def est_folio(ligne):
    return re.fullmatch(r"[ivxlcdm]+|\d{1,3}", ligne.texte_brut().lower()) is not None


def est_titre_courant(ligne, page):
    """Un titre courant est la première ligne de la page, en petit corps."""
    return ligne.hauteur <= LIMINAIRE and ligne is page[0]


def nettoyer(page):
    """Retire titre courant et folio, qui appartiennent à la mise en page."""
    return [l for l in page if not est_titre_courant(l, page) and not est_folio(l)]


class Bloc:
    """Un ensemble de lignes formant une unité : paragraphe, titre, item, encadré.

    Être un item de liste n'est pas un genre mais une propriété : un item peut
    être dans le corps du texte comme dans un encadré, et doit rester où il est.
    """

    def __init__(self, genre, lignes, item=False):
        self.genre = genre
        self.item = item
        self.lignes = list(lignes)

    def texte(self):
        """Recolle les lignes. Un tiret de fin de ligne est un trait d'union du
        texte — la césure étant absente du document — et se recolle sans espace."""
        morceaux = []
        for ligne in self.lignes:
            contenu = ligne.texte_balise()
            if morceaux and not morceaux[-1].endswith(("-", "­")):
                morceaux.append(" ")
            morceaux.append(contenu)
        # Deux passages balisés que la coupure de ligne a séparés n'en font qu'un.
        return re.sub(r"(\*{1,2}) \1", " ", "".join(morceaux)).strip()


def genre_de(ligne):
    if ligne.hauteur >= TITRE_PARTIE:
        return "partie"
    if ligne.hauteur >= TITRE_OUVRAGE:
        return "ouvrage"
    if ligne.hauteur >= TITRE_CHAPITRE:
        return "chapitre"
    if ligne.hauteur >= TITRE_SECTION:
        return "section"
    if ligne.hauteur >= CORPS:
        if ligne.style_dominant == "mono":
            return "schema"
        # Le livre n'a que trois tailles de titre : partie, chapitre, section.
        # Une ligne de corps entièrement en gras n'est donc jamais un titre —
        # c'est une attaque en gras dont la phrase passe à la ligne.
        return "corps"
    if ligne.hauteur >= ENCADRE:
        return "encadre"
    return "liminaire"


def a_des_colonnes(ligne):
    """La ligne présente-t-elle un écart horizontal digne d'une colonne ?

    Les schémas en chasse fixe en présentent aussi : ils sont exclus, leur place
    est dans la figure vectorielle de la phase 4, pas dans un tableau.
    """
    if ligne.style_dominant == "mono" or ligne.hauteur != CORPS:
        return False
    return any(b.gauche - a.droite > SEUIL_COLONNE
               for a, b in zip(ligne.fragments, ligne.fragments[1:]))


def colonnes_de_page(page):
    """Les indices des lignes appartenant à un tableau, régions comprises.

    Une ligne sans écart de colonne mais dont le fer à gauche coïncide avec une
    colonne déjà repérée est une ligne de continuation de cellule : elle
    appartient au tableau.
    """
    reperes = [i for i, l in enumerate(page) if a_des_colonnes(l)]
    if not reperes:
        return set()
    fers = {f.gauche for i in reperes for f in page[i].fragments}
    retenu = set(reperes)
    for i, ligne in enumerate(page):
        if i in retenu or ligne.hauteur != CORPS:
            continue
        voisin = any(abs(i - j) <= 2 for j in reperes)
        aligne = any(abs(ligne.gauche - f) <= TOLERANCE_COLONNE for f in fers)
        if voisin and aligne and ligne.gauche > min(fers) + SEUIL_COLONNE:
            retenu.add(i)
    return retenu


def est_ouverture_item(ligne):
    texte = ligne.texte_brut()
    return texte.startswith(PUCE) or bool(ITEM_NUMEROTE.match(texte))


def est_titre_encadre(ligne):
    """Dans un encadré, une ligne entièrement en gras en est le titre."""
    return (ligne.hauteur == ENCADRE
            and all(f.style == "gras" for f in ligne.fragments))


def blocs_de_page(page, bord, blocs, continuation, page_suivante=None):
    """Ajoute les blocs d'une page à la suite, en gérant le report de paragraphe.

    Un bloc s'ouvre quand le genre change, quand la ligne ouvre un item de liste,
    quand elle se désindente par rapport à la précédente — le retour au fer d'un
    item après ses lignes de continuation — ou quand l'écart vertical dépasse le
    seuil du genre. La désindentation ne vaut pas pour les titres, qui sont
    centrés : leur fer à gauche varie avec leur longueur.

    Un paragraphe se poursuit d'une page à l'autre si la dernière ligne de la page
    précédente atteint le fer à droite : dans un texte justifié, une ligne pleine
    n'est jamais une fin de paragraphe.
    """
    tabulaires = colonnes_de_page(page)
    for index, ligne in enumerate(page):
        genre = "tableau" if index in tabulaires else genre_de(ligne)
        item = est_ouverture_item(ligne) and genre != "tableau"
        precedent = blocs[-1] if blocs else None

        if index == 0:
            ouvre = not (continuation and precedent
                         and genre == precedent.genre
                         and genre in ("corps", "encadre") and not item)
        else:
            precedente = page[index - 1]
            centre = genre in ("partie", "ouvrage", "chapitre", "section")
            poursuit_un_item = (precedent is not None and precedent.item
                                and ligne.gauche > precedente.gauche + RETRAIT_CONTINUATION
                                and not item)
            ouvre = (item
                     or (genre != precedent.genre and not poursuit_un_item)
                     or (not centre and genre != "tableau" and not poursuit_un_item
                         and ligne.gauche < precedente.gauche - RETRAIT_CONTINUATION)
                     or (genre != "tableau"
                         and ligne.top - precedente.top > FACTEUR_BLOC * ligne.hauteur))

        if ouvre or not blocs:
            blocs.append(Bloc(genre, [ligne], item=item))
        else:
            blocs[-1].lignes.append(ligne)

    return paragraphe_se_poursuit(page, bord, page_suivante)


def paragraphe_se_poursuit(page, bord, page_suivante):
    """Le paragraphe de fin de page se poursuit-il sur la page suivante ?

    Une ligne pleine est le premier indice : dans un texte justifié, la dernière
    ligne d'un paragraphe est en principe courte. Mais il arrive qu'elle
    remplisse la mesure par coïncidence. Second indice, décisif : une ligne qui
    s'achève sur une ponctuation forte et que suit une capitale ouvre presque
    toujours un paragraphe neuf.
    """
    derniere = page[-1] if page else None
    if not derniere or genre_de(derniere) not in ("corps", "encadre"):
        return False
    if derniere.droite < bord - 8:
        return False
    texte = derniere.texte_brut().rstrip()
    if not texte.endswith(FIN_DE_PHRASE):
        return True
    suite = next((l for l in (page_suivante or []) if genre_de(l) == "corps"), None)
    premier = suite.texte_brut().lstrip() if suite else ""
    return bool(premier) and not premier[0].isupper()


def est_table_des_matieres(page):
    """Une page de table des matières se reconnaît à ses points de conduite."""
    if not page:
        return False
    avec_points = sum(1 for l in page if POINTS_DE_CONDUITE in l.texte_brut())
    return avec_points >= max(3, len(page) // 3)


def assembler(pages):
    """Rend la suite des blocs du livre, hors mise en page et table des matières."""
    propres = [nettoyer(p) for p in pages]
    propres = [p for p in propres if not est_table_des_matieres(p)]
    corps = [l for p in propres for l in p if genre_de(l) == "corps"]
    bord = collections.Counter(l.droite for l in corps).most_common(1)[0][0]

    blocs, continuation = [], False
    for index, page in enumerate(propres):
        if page:
            suivante = propres[index + 1] if index + 1 < len(propres) else None
            continuation = blocs_de_page(page, bord, blocs, continuation, suivante)
    return blocs


# Le livre a trois familles d'encadrés, que la composition ne distingue pas :
# même cadre, même corps de 8,97 pt, même titre en gras. L'information de type
# n'est donc pas récupérable depuis le Markdown une fois la phase 0 close — elle
# se note maintenant ou elle est perdue.
TYPES_ENCADRE = {"Réalité congolaise": "realite-congolaise",
                 "À faire cette semaine": "a-faire"}
TYPE_PAR_DEFAUT = "aparte"


def type_encadre(titre):
    for intitule, genre in TYPES_ENCADRE.items():
        if titre.startswith(intitule):
            return genre
    return TYPE_PAR_DEFAUT


def rendre(blocs):
    """Rend le Markdown du livre, découpé en unités (liminaires, chapitres)."""
    unites = []
    courante = {"titre": "Liminaires", "rang": "00", "lignes": [], "pages": set(),
                "mots_source": 0, "mots_schema": 0}
    dans_encadre = False
    partie_en_attente = []
    schemas = []
    derniere_page_de_schema = None

    def fermer_encadre():
        nonlocal dans_encadre
        if dans_encadre:
            courante["lignes"].append(":::")
            dans_encadre = False

    def ouvrir_encadre(titre=None):
        nonlocal dans_encadre
        fermer_encadre()
        attributs = f'.encadre type="{type_encadre(titre)}"' if titre else ".encadre"
        entete = f'{{{attributs} titre="{titre}"}}' if titre else "{.encadre}"
        courante["lignes"].append(f"\n::: {entete}")
        dans_encadre = True

    for bloc in blocs:
        texte = bloc.texte()
        if not texte:
            continue
        # Une ouverture de partie précède le chapitre qu'elle introduit : elle est
        # mise en attente et posée en tête de l'unité suivante — ses mots avec
        # elle, faute de quoi ils se compteraient dans le chapitre précédent.
        if bloc.genre == "partie":
            partie_en_attente.append(texte)
            continue

        if bloc.genre == "chapitre":
            fermer_encadre()
            unites.append(courante)
            courante = {"titre": texte, "rang": None, "lignes": [],
                        "pages": {l.page for l in bloc.lignes},
                        "mots_source": 0, "mots_schema": 0}
            if partie_en_attente:
                entete = " ".join(partie_en_attente)
                courante["lignes"].append(f"<!-- {entete} -->\n")
                courante["mots_source"] += len(entete.split())
                partie_en_attente = []

        courante["pages"].update(l.page for l in bloc.lignes)
        courante["mots_source"] += sum(len(l.texte_brut().split()) for l in bloc.lignes)

        if bloc.genre == "chapitre":
            courante["lignes"].append(f"# {texte}")
            continue

        if bloc.genre == "encadre":
            if est_titre_encadre(bloc.lignes[0]) and len(bloc.lignes) == 1:
                ouvrir_encadre(texte.strip("*"))
                continue
            if not dans_encadre:
                ouvrir_encadre()
            courante["lignes"].append(_item(bloc, texte) if bloc.item else texte)
            continue

        fermer_encadre()
        if bloc.genre == "section":
            courante["lignes"].append(f"\n## {texte}")
        elif bloc.genre == "tableau":
            rendu = _tableau(bloc)
            precedent = courante["lignes"][-1] if courante["lignes"] else ""
            entete = rendu.strip().split("\n")[0]
            if precedent.strip().startswith("|") and entete in precedent:
                # Un tableau qui déborde sur la page suivante y répète son en-tête.
                suite = "\n".join(rendu.strip().split("\n")[2:])
                courante["lignes"][-1] = precedent.rstrip() + "\n" + suite
            else:
                courante["lignes"].append(rendu)
        elif bloc.genre == "schema":
            nonlocal_page = bloc.lignes[0].page
            # Les schémas sont en chasse fixe et leurs flèches sortent déjà en
            # caractères invalides à l'extraction. Les reconstituer au jugé
            # reviendrait à inventer. Ils attendent le contenu exact de l'auteure.
            page = nonlocal_page
            # Un schéma comporte des lignes espacées — flèches, cases — que le
            # découpage en blocs sépare. Une même page ne porte qu'un schéma.
            if page != derniere_page_de_schema:
                courante["lignes"].append(
                    f'\n::: {{.todo-schema page="{page}"}}\n'
                    f"Schéma de la page {page} du PDF, à reprendre en figure"
                    " vectorielle.\nContenu exact à fournir : l'extraction le rend"
                    " en caractères invalides.\n:::")
                schemas.append((page, []))
                derniere_page_de_schema = page
            schemas[-1][1].extend(l.texte_brut() for l in bloc.lignes)
            courante["mots_schema"] += sum(len(l.texte_brut().split())
                                           for l in bloc.lignes)
        elif bloc.item:
            courante["lignes"].append(_item(bloc, texte))
        else:
            courante["lignes"].append("\n" + texte)

    fermer_encadre()
    unites.append(courante)
    return unites, schemas


def _tableau(bloc):
    """Rend un bloc tabulaire en tableau Markdown.

    Les colonnes sont déduites des fers à gauche des cellules, groupés à la
    tolérance près. Une ligne dont la première cellule n'est pas dans la colonne
    de gauche poursuit la rangée précédente : c'est une cellule sur plusieurs
    lignes, non une rangée nouvelle.
    """
    fers = sorted({f.gauche for l in bloc.lignes for f in l.fragments})
    colonnes = []
    for fer in fers:
        if not colonnes or fer - colonnes[-1] > TOLERANCE_COLONNE:
            colonnes.append(fer)
    if len(colonnes) < 2:
        return "\n" + bloc.texte()

    rangees = []
    for ligne in bloc.lignes:
        cellules = [""] * len(colonnes)
        for fragment in ligne.fragments:
            index = max(i for i, c in enumerate(colonnes)
                        if fragment.gauche >= c - TOLERANCE_COLONNE)
            cellules[index] += (" " if cellules[index] else "") + fragment.texte.strip()
        commence = ligne.fragments[0].gauche <= colonnes[0] + TOLERANCE_COLONNE
        if commence or not rangees:
            rangees.append(cellules)
        else:
            for i, cellule in enumerate(cellules):
                if cellule:
                    rangees[-1][i] += (" " if rangees[-1][i] else "") + cellule

    # Un en-tête peut tenir sur deux lignes (« Étape ou / jalon ») : la première
    # ne commence alors pas dans la colonne de gauche et coiffe la suivante.
    if len(rangees) > 1 and not rangees[0][0]:
        for i, cellule in enumerate(rangees[0]):
            if cellule:
                rangees[1][i] = (cellule + " " + rangees[1][i]).strip()
        rangees.pop(0)

    entete, corps = rangees[0], rangees[1:]
    lignes = ["| " + " | ".join(entete) + " |",
              "|" + "|".join(" --- " for _ in entete) + "|"]
    lignes += ["| " + " | ".join(r) + " |" for r in corps]
    return "\n" + "\n".join(lignes)


def _item(bloc, texte):
    """Rend un item de liste : puce ou numéro, avec ses lignes de continuation."""
    return re.sub(r"^" + PUCE + r"\s*", "- ", texte)


RANGS_HORS_CHAPITRE = {
    "Introduction": "00b-introduction",
    "Notes et sources": "90-notes-et-sources",
}


def nom_de_fichier(unite, rang):
    """Un nom de fichier stable, dérivé du titre du chapitre."""
    titre = unite["titre"]
    if titre == "Liminaires":
        return "00a-liminaires.md"
    for debut_titre, nom in RANGS_HORS_CHAPITRE.items():
        if titre.startswith(debut_titre):
            return f"{nom}.md"
    numero = re.match(r"Chapitre\s+(\d+)", titre)
    base = re.sub(r"^(?:Chapitre\s+\d+|Clôture)\s*—\s*", "", titre)
    # Les noms de fichiers restent en ASCII : ils seront cités dans des sources
    # LuaLaTeX et dans un Makefile, où les accents se paient tôt ou tard.
    base = unicodedata.normalize("NFD", base.lower())
    base = "".join(c for c in base if unicodedata.category(c) != "Mn")
    base = re.sub(r"[^a-z0-9\s-]", "", base)
    base = re.sub(r"\s+", "-", base.strip())[:44].strip("-")
    prefixe = f"{int(numero.group(1)):02d}" if numero else "80-cloture"
    return f"{prefixe}-{base}.md"


def demarquer(markdown):
    """Le texte du Markdown, ses marques retirées, pour un comptage comparable.

    Le comptage se fait contre les lignes du PDF réellement versées dans le
    chapitre, non contre ses pages : une page porte souvent la fin d'un chapitre
    et le début du suivant, et la compter deux fois masquerait précisément ce que
    le contrôle cherche — un passage tombé.
    """
    # Ce que la marque porte est du texte de l'auteure et doit rester compté :
    # le titre d'un encadré, celui d'une partie, la puce d'une liste. Ce qui est
    # pure syntaxe disparaît. Sans cette symétrie, le chiffre ne veut rien dire.
    # Le texte de substitution d'un schéma est de moi, pas de l'auteure : il ne
    # se compte pas. Les mots du schéma manquants sont rapportés à part.
    texte = re.sub(r":::\s*\{\.todo-schema.*?:::", " ", markdown, flags=re.S)
    texte = re.sub(r"<!--(.*?)-->", r"\1", texte, flags=re.S)
    texte = re.sub(r'^:::.*?titre="([^"]*)".*$', r"\1", texte, flags=re.M)
    texte = re.sub(r"^:::.*$", " ", texte, flags=re.M)
    texte = re.sub(r"^#{1,6}\s*", "", texte, flags=re.M)
    texte = re.sub(r"^(\s*)-\s+", r"\1" + PUCE + " ", texte, flags=re.M)
    texte = re.sub(r"^\|[\s|:-]+\|\s*$", " ", texte, flags=re.M)
    texte = texte.replace("|", " ").replace("**", "").replace("*", "")
    return texte


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("pdfs", nargs="+", type=Path)
    analyseur.add_argument("--sortie", type=Path, default=Path("src"))
    analyseur.add_argument("--liste", action="store_true",
                           help="n'écrit rien, énumère les unités trouvées")
    options = analyseur.parse_args()

    pages = lire_pages(options.pdfs)
    unites, schemas = rendre(assembler(pages))

    print(f"{'fichier':<52} {'mots .md':>9} {'mots PDF':>9} {'écart':>7}"
          f" {'schéma':>7}  pages")
    for rang, unite in enumerate(unites):
        corps = re.sub(r"\n{3,}", "\n\n", "\n".join(unite["lignes"]).strip()) + "\n"
        nom = nom_de_fichier(unite, rang)
        mots_md = len(demarquer(corps).split())
        numeros = unite["pages"]
        mots_pdf = unite["mots_source"]
        ecart = mots_md - mots_pdf
        etendue = f"{min(numeros)}–{max(numeros)}" if numeros else "—"
        signe = f"{ecart:+d}" if ecart else "0"
        attente = unite["mots_schema"] or ""
        print(f"  {nom:<50} {mots_md:>9} {mots_pdf:>9} {signe:>7}"
              f" {attente:>7}  {etendue}")
        if not options.liste:
            options.sortie.mkdir(parents=True, exist_ok=True)
            (options.sortie / nom).write_text(corps, encoding="utf-8")

    if schemas and not options.liste:
        archive = Path("qa/schemas-a-reprendre.txt")
        archive.write_text(
            "Schémas laissés en attente par la reconstitution.\n"
            "L'extraction les rend en caractères invalides ; ils sont conservés ici\n"
            "à titre de preuve, hors du manuscrit, et attendent le contenu exact\n"
            "de l'auteure.\n"
            + "".join(f"\n--- page {page} du PDF ---\n" + "\n".join(lignes) + "\n"
                      for page, lignes in schemas),
            encoding="utf-8")
        print(f"\n{len(schemas)} schéma(s) en attente : {archive}")


if __name__ == "__main__":
    main()
