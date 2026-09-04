#!/usr/bin/env python3
"""Compose la double page du spécimen dans les trois polices — phase 1.

Le spécimen sert à trancher D3, le choix de la police de labeur. Il porte donc
ce sur quoi les polices se départagent réellement : du texte courant en
quantité, un titre de section, et un encadré « Réalité congolaise » — le
contraste entre corps et encadré étant le second point de décision.

Le texte n'est pas recopié : il est tiré du manuscrit, chapitre 1, ce qui
garantit qu'on juge les polices sur la prose du livre et non sur un faux texte.

Sortie : un PDF et un PNG à 150 ppp par police, dans build/specimen/.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "style"))
from gabarit import GEOMETRIE, POLICES, PREAMBULE      # noqa: E402

# Signes par ligne relevés sur le corpus de neuf chapitres par
# qa/mesurer-composition.py : médiane, puis 90e centile.
SIGNES = {"garamond": "62 / 66", "libertinus": "62 / 66", "sourceserif": "62 / 66"}

ECHAPPEMENTS = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
                "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
                "^": r"\textasciicircum{}", "\\": r"\textbackslash{}"}


def echapper(texte):
    for signe, remplacement in ECHAPPEMENTS.items():
        texte = texte.replace(signe, remplacement)
    return texte


def en_latex(ligne):
    """Convertit le sous-ensemble de Markdown que la reconstitution produit."""
    ligne = echapper(ligne)
    ligne = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", ligne)
    ligne = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"\\emph{\1}", ligne)
    ligne = re.sub(r"\[\^(\d+)\]", r"\\textsuperscript{\1}", ligne)
    return ligne


def sections(chapitre):
    """Les intitulés de section du chapitre, dans l'ordre."""
    return [l.strip()[3:] for l in chapitre.read_text(encoding="utf-8").split("\n")
            if l.startswith("## ")]


def corps_du_specimen(chapitre, jusqu_a, depuis=None):
    """Le corps LaTeX, du début du chapitre jusqu'à l'encadré nommé, inclus.

    Le spécimen s'arrête là volontairement : il doit tenir sur une double page,
    et porter du texte courant en quantité, un titre de section et un encadré —
    pas le chapitre entier, qui noierait la comparaison.
    """
    sortie, liste_ouverte, encadre_vise = [], False, False
    commence = depuis is None

    def fermer_liste():
        nonlocal liste_ouverte
        if liste_ouverte:
            sortie.append(r"\end{itemize}")
            liste_ouverte = False

    for ligne in chapitre.read_text(encoding="utf-8").split("\n"):
        nue = ligne.strip()
        if not nue or nue.startswith("<!--") or nue.startswith("# "):
            continue
        if nue.startswith("## "):
            fermer_liste()
            if not commence:
                commence = nue[3:] == depuis
            if commence:
                sortie.append(r"\section*{%s}" % en_latex(nue[3:]))
            continue
        if not commence:
            continue
        if False:
            pass
        elif nue.startswith("::: {"):
            fermer_liste()
            titre = re.search(r'titre="([^"]*)"', nue)
            intitule = titre.group(1) if titre else ""
            encadre_vise = bool(jusqu_a) and jusqu_a in intitule
            sortie.append(r"\begin{encadre}{%s}" % en_latex(intitule))
        elif nue == ":::":
            fermer_liste()
            sortie.append(r"\end{encadre}")
            if encadre_vise:
                break
        elif nue.startswith("- "):
            if not liste_ouverte:
                sortie.append(r"\begin{itemize}")
                liste_ouverte = True
            sortie.append(r"\item %s" % en_latex(nue[2:]))
        else:
            fermer_liste()
            sortie.append(en_latex(nue))
    fermer_liste()
    return "\n\n".join(sortie)


def compte_de_pages(pdf):
    sortie = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    for ligne in sortie.split("\n"):
        if ligne.startswith("Pages:"):
            return int(ligne.split()[1])
    return 0


def composer(clef, police, corps_tex, sortie, courant, regie=None):
    # Les marqueurs sont @nom@ et non %(nom)s : le pour-cent ouvre un commentaire
    # en LaTeX, et les deux syntaxes ne cohabitent pas.
    corps = police["corps"]
    valeurs = {
        "corps": f"{corps:g}",
        # La classe reste à 11 pt — memoir n'accepte pas les corps fractionnaires.
        # L'échelle de fontspec porte l'écart, ce qui préserve les rapports de
        # \small et consorts, sur lesquels repose le contraste de l'encadré.
        "echelle": f"{corps / 11:.4f}",
        "hauteur": GEOMETRIE["format"][1], "largeur": GEOMETRIE["format"][0],
        "bloc": str(210 - GEOMETRIE["tete"] - GEOMETRIE["pied"]),
        "justification": str(GEOMETRIE["justification"]),
        "gouttiere": str(GEOMETRIE["gouttiere"]), "tete": str(GEOMETRIE["tete"]),
        "romain": police["romain"], "chemin": police["chemin"],
        "italique": police["italique"], "gras": police["gras"],
        "linespread": f"{police['interlignage'] / corps / 1.2:.4f}",
        "courant": courant,
        "regie": regie or "",
    }
    preambule = PREAMBULE
    for nom, valeur in valeurs.items():
        preambule = preambule.replace(f"@{nom}@", valeur)
    source = sortie / f"specimen-{clef}.tex"
    source.write_text(preambule + "\n" + corps_tex + "\n\\end{document}\n",
                      encoding="utf-8")
    for _ in range(2):        # deux passes : titres courants et pagination
        resultat = subprocess.run(
            ["lualatex", "-interaction=nonstopmode", "-halt-on-error", source.name],
            cwd=sortie, capture_output=True, text=True)
    if resultat.returncode:
        journal = (sortie / f"specimen-{clef}.log").read_text(encoding="utf-8",
                                                              errors="replace")
        erreurs = [l for l in journal.split("\n") if l.startswith("!")][:6]
        print(f"  {clef} : ÉCHEC\n    " + "\n    ".join(erreurs))
        return None
    return sortie / f"specimen-{clef}.pdf"


def doubler(clef, sortie, pages=2):
    """Assemble les pages en une double page, et la rend en PNG à 150 ppp.

    Un livre se juge sur la double page ouverte, pas sur un feuillet isolé — et
    l'auteure compare sur téléphone, où deux fichiers séparés ne se confrontent
    pas. Le format est celui de deux A5 côte à côte.
    """
    montage = sortie / f"double-{clef}.tex"
    montage.write_text(
        "\\documentclass{article}\n"
        "\\usepackage[paperwidth=296mm,paperheight=210mm,margin=0pt]{geometry}\n"
        "\\usepackage{pdfpages}\n"
        "\\begin{document}\n"
        f"\\includepdf[pages=1-{pages},nup=2x1,noautoscale=true,"
        "delta=0mm 0mm]{specimen-" + clef + ".pdf}\n"
        "\\end{document}\n", encoding="utf-8")
    resultat = subprocess.run(
        ["lualatex", "-interaction=nonstopmode", "-halt-on-error", montage.name],
        cwd=sortie, capture_output=True, text=True)
    if resultat.returncode:
        return None
    subprocess.run(["pdftoppm", "-r", "150", "-png", "-singlefile",
                    str(sortie / f"double-{clef}.pdf"),
                    str(sortie / f"double-{clef}")], check=True)
    return sortie / f"double-{clef}.png"


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--chapitre", type=Path,
                           default=Path("src/01-developper-une-vision-pour-son-entreprise.md"))
    analyseur.add_argument("--sortie", type=Path, default=Path("build/specimen"))
    analyseur.add_argument("--jusqu-a", default="Réalité congolaise")
    analyseur.add_argument("--pages", type=int, default=2)
    options = analyseur.parse_args()

    options.sortie.mkdir(parents=True, exist_ok=True)
    courant = "Chapitre 1 — Développer une vision"
    # Le spécimen doit tenir sur une double page exactement. Plutôt que de
    # deviner où commencer, on essaie chaque section de tête jusqu'à ce que la
    # composition tombe sur deux pages — dans la police la plus encombrante,
    # pour que les trois portent le même texte.
    # La police de référence est celle qui occupe le plus de place : si le texte
    # tient chez elle, il tient chez les deux autres, et les trois portent alors
    # exactement le même contenu — sans quoi la comparaison serait faussée.
    reference = ("garamond", POLICES["garamond"])
    depuis, corps_tex = None, None
    for candidate in [None] + sections(options.chapitre):
        essai = corps_du_specimen(options.chapitre, options.jusqu_a, candidate)
        if not essai.strip():
            continue
        for fichier in options.sortie.glob("specimen-*"):
            fichier.unlink()
        if composer(reference[0], reference[1], essai, options.sortie, courant) is None:
            continue
        if compte_de_pages(options.sortie / f"specimen-{reference[0]}.pdf") <= options.pages:
            depuis, corps_tex = candidate, essai
            break
    if corps_tex is None:
        sys.exit("aucun découpage ne tient sur la double page")

    print(f"  départ : {depuis or 'début du chapitre'}")
    for clef, police in POLICES.items():
        # La ligne de régie nomme, en pied de page, ce que la double page donne
        # à juger : une police ne se juge pas à un corps qui ne sera pas le sien.
        regie = (f"{police['nom']} \\quad {police['corps']:g}/"
                 f"{police['interlignage']:g} pt \\quad 105 mm \\quad "
                 f"{SIGNES[clef]} signes")
        pdf = composer(clef, police, corps_tex, options.sortie, courant, regie)
        if not pdf:
            continue
        pages = compte_de_pages(pdf)
        double = doubler(clef, options.sortie, min(pages, options.pages))
        print(f"  {police['nom']:<18} corps {police['corps']} pt / "
              f"interlignage {police['interlignage']} pt — {pages} page(s)"
              f"{'' if double else ' — montage en échec'}")


if __name__ == "__main__":
    main()
