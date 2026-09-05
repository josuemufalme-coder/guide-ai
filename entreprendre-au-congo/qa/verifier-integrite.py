#!/usr/bin/env python3
"""Contrôle d'intégrité de la reconstitution — phase 0.

Le cahier des charges exige un « contrôle par différentiel automatique que la
recomposition restitue le manuscrit au caractère près ». Le manuscrit d'origine
n'existant plus, la référence est l'extraction fournie par l'auteure,
`source/ENTREPRENDRE-AU-CONGO-extraction.txt`.

Cette référence n'est pas le manuscrit : c'est une extraction du PDF, et elle
porte donc ce que la composition y a ajouté — titres courants, folios, table des
matières, puces typographiques. Un titre courant y est de surcroît indiscernable
du titre de chapitre dont il dérive : les deux sont la même chaîne de caractères.
Exiger zéro différence contre une telle référence n'aurait pas de sens.

Le contrôle classe donc chaque écart :

  mise en page   ce que la composition a ajouté et que le manuscrit n'a jamais
                 contenu — titre courant, folio, puce, points de conduite.
                 Attendu, dénombré, listé sur demande.

  ordre          une zone où les deux textes portent exactement les mêmes mots
                 dans un ordre différent. C'est le cas des sept tableaux : lus
                 comme un flux, ils se déroulent ligne par ligne dans le PDF et
                 cellule par cellule dans le Markdown. Aucun mot n'est perdu, et
                 c'est ce que le contrôle vérifie.

  correction     un défaut de l'extraction que la reconstitution répare. Le cas
                 connu : les quinze mots composés coupés en fin de ligne, dont
                 l'extraction a perdu le trait d'union (« écoutezle » pour
                 « écoutez-le »). La reconstitution, qui lit le PDF, le conserve.

  réel           tout le reste : un mot de l'auteure perdu, altéré ou inventé.
                 Doit être nul. Chaque occurrence est rapportée avec son contexte.

Usage : python3 verifier-integrite.py [--reference F] [--source D] [--tout]
"""
import argparse
import collections
import difflib
import re
import sys
import unicodedata
from pathlib import Path

SAUT_DE_PAGE = "\x0c"
POINTS_DE_CONDUITE = ". . ."
PUCE = "•"
# Les folios romains des pages liminaires ne vont pas au-delà de xx. Les énumérer
# évite de prendre pour des chiffres les mots « il » et « ci », que toute
# expression fondée sur [ivxlcdm] avale sans prévenir.
ROMAINS = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x",
           "xi", "xii", "xiii", "xiv", "xv", "xvi", "xvii", "xviii", "xix", "xx"}
TITRE_DE_L_OUVRAGE = "Entreprendre au Congo"


def est_folio(mot):
    return mot.lower() in ROMAINS or (mot.isdigit() and len(mot) <= 3)
TITRE_COURANT = re.compile(
    r"(?:Entreprendre au Congo|Introduction|Chapitre \d+ .*|Clôture .*|"
    r"Notes et sources|Table des matières)$")


def mots(texte):
    """Réduit un texte à sa suite de mots, apostrophes et ponctuation comprises."""
    texte = unicodedata.normalize("NFC", texte)
    for parasite in ("­", " ", " ", " "):
        texte = texte.replace(parasite, " " if parasite != "­" else "")
    return [m for m in texte.split() if m != PUCE]


def corrections_de_langue(chemin):
    """Les fautes de français corrigées dans le manuscrit, et leur forme d'origine.

    Le manuscrit doit porter exactement la matière du livre. Une faute corrigée
    est donc, pour ce contrôle, un signe perdu — à moins qu'elle ne soit écrite
    quelque part. Elle l'est ici, ligne à ligne, et le contrôle applique ces
    corrections à la référence avant de comparer.
    """
    couples = []
    if not chemin.exists():
        return couples
    for ligne in chemin.read_text(encoding="utf-8").split("\n"):
        if ligne.startswith("#") or "->" not in ligne:
            continue
        avant, _, apres = ligne.partition("->")
        couples.append((avant.strip(), apres.strip()))
    return couples


def reference(chemin, corrections=()):
    """La suite de mots de l'extraction, table des matières écartée."""
    retenu, dernier_folio = [], 0
    brut = chemin.read_text(encoding="utf-8")
    for avant, apres in corrections:
        if avant not in brut:
            print(f"  correction sans objet dans la référence : {avant!r}")
        brut = brut.replace(avant, apres)
    for page in brut.split(SAUT_DE_PAGE):
        lignes = [l.strip() for l in page.split("\n") if l.strip()]
        if sum(1 for l in lignes if POINTS_DE_CONDUITE in l) >= 3:
            continue  # table des matières : régénérée à la composition
        for index, ligne in enumerate(lignes):
            # Le folio se tient aux extrémités de la page et suit la page
            # précédente : c'est ce qui le distingue d'une cellule de tableau ne
            # contenant qu'un nombre, qui lui ressemble en tout point.
            aux_extremites = index <= 1 or index >= len(lignes) - 2
            if aux_extremites and est_folio(ligne):
                valeur = int(ligne) if ligne.isdigit() else None
                if valeur is None or dernier_folio < valeur <= dernier_folio + 3:
                    if valeur is not None:
                        dernier_folio = valeur
                    continue
            retenu.append(ligne)
    return mots(" ".join(retenu))


def candidat(dossier):
    """La suite de mots du Markdown reconstitué, ses marques retirées.

    Les titres de partie et d'encadré sont du texte de l'auteure : ils restent,
    seules leurs marques disparaissent. Les schémas, qui deviendront des figures
    vectorielles en phase 4, sont écartés du comptage.
    """
    retenu = []
    for fichier in sorted(dossier.glob("*.md")):
        texte = fichier.read_text(encoding="utf-8")
        texte = re.sub(r"<!--(.*?)-->", r"\1", texte, flags=re.S)
        # Les schémas se comparent à part : voir substitutions_de_schemas.
        texte = re.sub(r"```schema.*?```", " ", texte, flags=re.S)
        texte = re.sub(r'^:::\s*\{[^}]*titre="([^"]*)"[^}]*\}\s*$', r"\1", texte,
                       flags=re.M)
        texte = re.sub(r"^:::.*$", " ", texte, flags=re.M)
        texte = re.sub(r"^#{1,6}\s*", "", texte, flags=re.M)
        texte = re.sub(r"^\s*-\s+", "", texte, flags=re.M)
        texte = re.sub(r"^\|[\s|:-]+\|\s*$", " ", texte, flags=re.M)  # filets des tableaux
        texte = re.sub(r"^\|", " ", texte, flags=re.M)
        texte = texte.replace("|", " ")
        texte = re.sub(r"\[\^(\d+)\]", r"\1", texte)  # l'appel redevient l'exposant collé
        retenu.append(texte.replace("**", "").replace("*", ""))
    return mots("\n".join(retenu))


def titres_courants(dossier):
    """Les chaînes que la composition répète : titres de page et en-têtes de tableau.

    Un tableau qui déborde sur la page suivante y répète son en-tête. La
    reconstitution ne le garde qu'une fois ; l'extraction, qui suit les pages,
    le porte deux fois. La seconde occurrence relève de la mise en page.

    Ces chaînes sont confrontées telles quelles au texte extrait du PDF, qui
    ignore les espaces insécables. Elles passent donc par `mots`, qui les ramène
    à l'espace ordinaire : depuis la phase 2, un titre de chapitre peut porter
    une insécable devant deux-points, et la comparaison littérale échouait.
    """
    titres = {TITRE_DE_L_OUVRAGE}
    for fichier in dossier.glob("*.md"):
        lignes = fichier.read_text(encoding="utf-8").split("\n")
        for index, ligne in enumerate(lignes):
            if ligne.startswith("# "):
                titres.add(" ".join(mots(ligne[2:])))
                continue
            if ligne.startswith("<!--"):
                # Les ouvertures de partie : l'extraction les encadre de folios.
                titres.add(" ".join(mots(ligne.strip("<!->"))))
                continue
            # L'en-tête d'un tableau est la rangée qui précède le filet ; elle
            # seule se répète en tête de page. Les rangées de corps, non.
            suivante = lignes[index + 1] if index + 1 < len(lignes) else ""
            if ligne.startswith("|") and suivante.startswith("|") and "---" in suivante:
                cellules = [c.strip() for c in ligne.strip("|").split("|")]
                titres.add(" ".join(" ".join(mots(c)) for c in cellules if c))
    return sorted(titres, key=len, reverse=True)


def retirer_mise_en_page(segment, titres, garder_premiere=False):
    """Retranche du segment ce que la composition y a mis : folios, titres courants.

    Un titre courant se retrouve soudé au texte voisin au passage d'une page,
    au milieu d'une phrase coupée. Le retirer laisse apparaître ce que l'écart
    contient réellement.
    """
    reste, garde, vus = " ".join(segment).strip(), [], set()
    while reste:
        for titre in titres:
            if reste.startswith(titre):
                # Un titre courant dérive du titre de chapitre imprimé une fois en
                # tête de celui-ci : sur le flux entier, la première occurrence est
                # ce titre, les suivantes sont la mise en page.
                if garder_premiere and titre != TITRE_DE_L_OUVRAGE and titre not in vus:
                    vus.add(titre)
                    garde.extend(titre.split())
                reste = reste[len(titre):].strip()
                break
        else:
            # Les folios sont retirés en amont, par `reference`, qui dispose de la
            # structure des pages. Les retirer une seconde fois ici, sur un flux
            # sans pages, reviendrait à prendre pour des folios les chiffres de
            # l'auteure — items numérotés, cellules de tableau, appels de notes.
            premier, _, suite = reste.partition(" ")
            garde.append(premier)
            reste = suite.strip()
    return garde


def est_schema(segment):
    """Les schémas en art ASCII : capitales et flèches, aucune phrase.

    Un schéma coupé par une fin de page laisse parfois un fragment isolé — le
    mot « ACTION » seul, dernière case du schéma de la page 27.
    """
    texte = " ".join(segment)
    if not segment:
        return False
    if any(f in texte for f in "→←↑↓"):
        return True
    return texte.upper() == texte and len(segment) <= 3


def est_correction(perdu, ajoute):
    """La reconstitution répare-t-elle un défaut de l'extraction ?

    Deux défauts connus, tous deux nés du recollage des lignes du PDF :
    le trait d'union avalé (« écoutezle » pour « écoutez-le ») et l'espace
    parasite laissée par un appel de note en exposant (« singulier3 . »).
    """
    if not perdu or not ajoute:
        return False
    aplati = lambda mots: "".join(mots).replace(" ", "").replace("-", "")
    return aplati(perdu) == aplati(ajoute)


PONT_MAXIMAL = 14  # mots communs en deçà desquels deux écarts forment une zone


def zones(attendu, obtenu):
    """Regroupe les écarts voisins en zones.

    Un tableau produit une longue alternance de mots communs et de mots
    déplacés ; pris un à un, ces écarts sont illisibles. Regroupés, ils forment
    une zone dont on peut vérifier qu'elle porte exactement les mêmes mots des
    deux côtés.
    """
    ecarts = [op for op in difflib.SequenceMatcher(None, attendu, obtenu, autojunk=False)
              .get_opcodes() if op[0] != "equal"]
    groupes = []
    for verbe, a1, a2, b1, b2 in ecarts:
        if groupes and a1 - groupes[-1][2] <= PONT_MAXIMAL:
            precedent = groupes[-1]
            groupes[-1] = (precedent[0], precedent[1], a2, precedent[3], b2)
        else:
            groupes.append((verbe, a1, a2, b1, b2))
    return groupes


def rapporter(attendu, obtenu, titres, tout=False, contexte=7):
    classes = {"mise en page": [], "schéma": [], "ordre": [], "correction": [], "réel": []}
    for verbe, a1, a2, b1, b2 in zones(attendu, obtenu):
        perdu, ajoute = attendu[a1:a2], obtenu[b1:b2]
        net = retirer_mise_en_page(perdu, titres)
        ecart = (verbe, " ".join(attendu[max(0, a1 - contexte):a1]), perdu, ajoute)
        # Pour juger d'une simple permutation, la zone est élargie de part et
        # d'autre : les bornes que difflib pose au milieu d'un tableau coupent
        # des mots communs, qui paraîtraient alors ajoutés d'un côté.
        large_a = retirer_mise_en_page(
            attendu[max(0, a1 - PONT_MAXIMAL):a2 + PONT_MAXIMAL], titres)
        large_b = obtenu[max(0, b1 - PONT_MAXIMAL):b2 + PONT_MAXIMAL]
        if net == ajoute:
            classes["mise en page"].append(ecart)
        elif est_correction(net, ajoute):
            classes["correction"].append(ecart)
        elif ajoute and sorted(large_a) == sorted(large_b):
            classes["ordre"].append(ecart)
        elif not ajoute and est_schema(net):
            classes["schéma"].append(ecart)
        else:
            classes["réel"].append(ecart)

    print(f"référence   : {len(attendu)} mots")
    print(f"reconstitué : {len(obtenu)} mots")
    for nom, ecarts in classes.items():
        print(f"écarts — {nom:<13} : {len(ecarts)}")
    reels = classes["réel"]

    afficher = [("ÉCARTS RÉELS", reels), ("corrections", classes["correction"])]
    if tout:
        afficher += [("écarts de mise en page", classes["mise en page"]),
                     ("zones réordonnées", classes["ordre"]),
                     ("schémas", classes["schéma"])]
    for titre, ecarts in afficher:
        if not ecarts:
            continue
        print(f"\n--- {titre} ---")
        for verbe, avant, perdu, ajoute in ecarts:
            print(f"\n  [{verbe}] après « …{avant} »")
            if perdu:
                print(f"      référence   : {' '.join(perdu)[:240]}")
            if ajoute:
                print(f"      reconstitué : {' '.join(ajoute)[:240]}")
    return len(reels)


def substitutions_de_schemas(chemin):
    """Ce que les schémas retirent à la référence et ajoutent au manuscrit.

    Les trois schémas ne se comparent pas : deux d'entre eux étaient défectueux
    dans le PDF, et l'auteure en a arrêté un tracé corrigé. Les mots de
    l'extraction sont donc légitimement absents du manuscrit, et ceux du tracé
    légitimement absents de l'extraction. Le contrôle retranche les uns et les
    autres, et dit combien.
    """
    extraction, manuscrit = collections.Counter(), collections.Counter()
    if not chemin.exists():
        return extraction, manuscrit
    cible = None
    for ligne in chemin.read_text(encoding="utf-8").split("\n"):
        if ligne.startswith("#"):
            continue
        if ligne.startswith("-- extraction --"):
            cible = extraction
        elif ligne.startswith("-- manuscrit --"):
            cible = manuscrit
        elif ligne.startswith("= page "):
            cible = None
        elif cible is not None and ligne.strip():
            cible.update(mots(ligne))
    return extraction, manuscrit


def bilan_global(attendu, obtenu, titres, retire=None):
    """Contrôle décisif : la reconstitution porte-t-elle exactement les mêmes mots ?

    La comparaison ordonnée atteint sa limite autour des tableaux et des schémas,
    où l'ordre de lecture d'une page n'a pas d'équivalent dans un flux de texte :
    difflib y perd l'alignement et signale comme perdus des mots qui sont
    simplement ailleurs. Le comptage global, lui, ne peut pas se tromper. Un mot
    manquant est un mot perdu, où qu'il soit.

    Les défauts de l'extraction que la reconstitution répare sont normalisés des
    deux côtés : trait d'union avalé, espace laissée par un appel de note.
    """
    aplatir = lambda mots: collections.Counter(
        "".join(mots).replace(" ", "").replace("-", ""))
    net = retirer_mise_en_page(attendu, titres, garder_premiere=True)
    if retire:
        restants = collections.Counter(net)
        restants.subtract(retire)
        net = list((+restants).elements())
    reste = collections.Counter(net)
    reste.subtract(collections.Counter(obtenu))
    manquants = {m: n for m, n in reste.items() if n > 0}
    surnumeraires = {m: -n for m, n in reste.items() if n < 0}

    # Un mot n'est réellement perdu que si les signes eux-mêmes manquent.
    signes = aplatir(net)
    signes.subtract(aplatir(obtenu))
    perdus = {c: n for c, n in signes.items() if n > 0}
    ajoutes = {c: -n for c, n in signes.items() if n < 0}

    print("\n--- bilan global ---")
    print(f"  mots de la référence, mise en page retirée : {len(net)}")
    if retire:
        print(f"  dont schémas, comparés à part              : {sum(retire.values())}")
    print(f"  mots de la reconstitution                  : {len(obtenu)}")
    if manquants or surnumeraires:
        print(f"  mots présents d'un seul côté : {len(manquants)} / {len(surnumeraires)}")
        for mot, nombre in list(manquants.items())[:10]:
            print(f"      référence seule      : {mot!r} ×{nombre}")
        for mot, nombre in list(surnumeraires.items())[:10]:
            print(f"      reconstitution seule : {mot!r} ×{nombre}")
    if perdus:
        print(f"  SIGNES PERDUS   : {perdus}")
    if ajoutes:
        print(f"  SIGNES AJOUTÉS  : {ajoutes}")
    if not perdus and not ajoutes:
        print("  aucun signe perdu ni ajouté : la reconstitution porte exactement"
              " la matière du livre")
    return len(perdus) + len(ajoutes)


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--reference", type=Path,
                           default=Path("source/ENTREPRENDRE-AU-CONGO-extraction.txt"))
    analyseur.add_argument("--source", type=Path, default=Path("src"))
    analyseur.add_argument("--tout", action="store_true",
                           help="détaille aussi les écarts de mise en page")
    options = analyseur.parse_args()
    corrections = corrections_de_langue(Path("qa/corrections-langue.txt"))
    if corrections:
        print("--- corrections de langue appliquées ---")
        for avant, apres in corrections:
            print(f"  « {avant} » → « {apres} »")
    attendu = reference(options.reference, corrections)
    obtenu = candidat(options.source)
    titres = titres_courants(options.source)
    reels = rapporter(attendu, obtenu, titres, options.tout)
    extraction, _ = substitutions_de_schemas(Path("qa/schemas-substitutions.txt"))
    perdus = bilan_global(attendu, obtenu, titres, extraction)
    print("\nintégrité : " + ("VÉRIFIÉE" if perdus == 0
                              else f"{perdus} signe(s) perdu(s)"))
    return 0 if perdus == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
