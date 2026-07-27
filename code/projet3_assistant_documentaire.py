#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROJET 3 --- Un assistant documentaire intelligent (RAG)
========================================================

Base documentaire : douze fiches de documentation produit en francais,
    fournies dans donnees/base_documentaire.json. Elles sont volontairement
    courtes pour que le mecanisme soit lisible d'un coup d'oeil.

Pour travailler sur un vrai corpus public, deux pistes :
    - Wikipedia en francais (dumps XML)
      URL : https://dumps.wikimedia.org/frwiki/latest/
    - SQuAD / FQuAD pour des paires question-reponse annotees
      URL : https://rajpurkar.github.io/SQuAD-explorer/

Ce que fait ce script :
    1. decoupe les documents en passages,
    2. les represente numeriquement (TF-IDF sur des n-grammes de caracteres,
       ce qui tolere les fautes de frappe et les variations de forme),
    3. retrouve les passages les plus proches d'une question,
    4. compose une reponse ancree dans ces passages, en citant ses sources.

L'etape 4 utilise ici un gabarit deterministe, afin que le script tourne
HORS LIGNE et sans cle d'API. L'emplacement exact ou brancher un modele de
langage est indique et commente dans la fonction rediger_reponse().

Execution : python3 projet3_assistant_documentaire.py
Duree     : environ 2 secondes.
"""

import json
import re
from pathlib import Path

import numpy as np
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DOSSIER = Path(__file__).parent / "donnees"
SEUIL_PERTINENCE = 0.18  # calibre a l'etape 5 ; voir le diagnostic


# --------------------------------------------------------------------------
# ETAPE 1 --- Rassembler et preparer la base documentaire
# --------------------------------------------------------------------------
def charger_passages():
    print("--- ETAPE 1 : base documentaire ---")
    docs = json.loads((DOSSIER / "base_documentaire.json").read_text(encoding="utf-8"))

    # Decoupage par phrase, en gardant le titre du document dans chaque passage :
    # sans lui, une phrase commencant par « Elle ne s'applique pas... » perdrait
    # tout son sens une fois isolee. C'est le point de vigilance du chapitre 10.
    passages = []
    for doc in docs:
        phrases = [p.strip() for p in re.split(r"(?<=[.!?])\s+", doc["texte"]) if p.strip()]
        for i in range(0, len(phrases), 2):  # groupes de deux phrases, avec titre
            bloc = " ".join(phrases[i : i + 2])
            passages.append(
                {"source": doc["id"], "titre": doc["titre"], "texte": bloc,
                 "indexable": f"{doc['titre']}. {bloc}"}
            )
    print(f"{len(docs)} documents -> {len(passages)} passages")
    return passages


# --------------------------------------------------------------------------
# ETAPE 2 --- Indexer les passages
# --------------------------------------------------------------------------
def indexer(passages):
    print("\n--- ETAPE 2 : indexation ---")
    # Deux representations combinees, parce qu'aucune ne suffit seule :
    #  - les MOTS discriminent bien le sujet, mais ratent « remboursé » quand le
    #    document dit « remboursement » ;
    #  - les SUITES DE CARACTERES rattrapent ces variations de forme et les fautes
    #    de frappe, mais trouvent de la ressemblance entre deux textes francais
    #    quelconques, ce qui produit de faux positifs.
    # Les concatener donne le meilleur des deux. C'est une recherche LEXICALE :
    # un vrai systeme emploierait des plongements de phrases (chapitre 9), plus
    # couteux mais capables de rapprocher deux formulations sans mot commun.
    textes = [p["indexable"] for p in passages]
    vectoriseurs = (
        TfidfVectorizer(analyzer="word", ngram_range=(1, 2), sublinear_tf=True),
        TfidfVectorizer(analyzer="char_wb", ngram_range=(4, 5), sublinear_tf=True),
    )
    matrice = hstack([v.fit_transform(textes) for v in vectoriseurs]).tocsr()
    print(f"Matrice {matrice.shape[0]} passages x {matrice.shape[1]} caracteristiques")
    print("Representation : mots (1-2) + suites de caracteres (4-5), concatenees")
    return vectoriseurs, matrice


# --------------------------------------------------------------------------
# ETAPE 3 --- Rechercher les passages pertinents
# --------------------------------------------------------------------------
def rechercher(question, vectoriseurs, matrice, passages, k=3):
    vecteur = hstack([v.transform([question]) for v in vectoriseurs]).tocsr()
    scores = cosine_similarity(vecteur, matrice)[0]
    meilleurs = np.argsort(scores)[::-1][:k]
    return [(passages[i], float(scores[i])) for i in meilleurs if scores[i] > 0]


# --------------------------------------------------------------------------
# ETAPE 4 --- Rediger une reponse ancree dans les sources
# --------------------------------------------------------------------------
def rediger_reponse(question, trouves):
    """Compose la reponse. C'est ici que se brancherait un modele de langage."""
    if not trouves or trouves[0][1] < SEUIL_PERTINENCE:
        return ("Je ne trouve pas cette information dans la documentation fournie.\n"
                "  Je prefere le dire plutot que de composer une reponse plausible."), []

    contexte = "\n".join(f"[{i+1}] {p['titre']} : {p['texte']}" for i, (p, _) in enumerate(trouves))

    # --- Branchement d'un modele de langage (desactive : necessite une cle) ---
    # invite = f\"\"\"Tu reponds uniquement a partir des passages ci-dessous.
    # Si l'information n'y figure pas, dis que tu ne sais pas.
    # Cite le numero du passage utilise entre crochets.
    #
    # Passages :
    # {contexte}
    #
    # Question : {question}\"\"\"
    # reponse = client.messages.create(model=..., max_tokens=400,
    #                                  messages=[{"role": "user", "content": invite}])
    # return reponse.content[0].text, [p for p, _ in trouves]
    # -------------------------------------------------------------------------

    # Gabarit deterministe, utilise ici pour que le script tourne hors ligne.
    principal, score = trouves[0]
    reponse = f"{principal['texte']}"
    if len(trouves) > 1 and trouves[1][1] > SEUIL_PERTINENCE:
        reponse += f"\n  À voir aussi : « {trouves[1][0]['titre']} »."
    return reponse, [p for p, s in trouves if s >= SEUIL_PERTINENCE]


# --------------------------------------------------------------------------
# ETAPE 5 --- Evaluer sur un jeu de questions attendues
# --------------------------------------------------------------------------
JEU_EVALUATION = [
    ("Combien de temps dure la garantie ?", "garantie-duree"),
    ("Est-ce que la garantie couvre une chute ?", "garantie-exclusions"),
    ("J'ai changé d'avis, quel est le délai ?", "retour-delai"),
    ("Comment je renvoie un article ?", "retour-procedure"),
    ("Quand serai-je remboursé ?", "remboursement-delai"),
    ("En combien de jours arrive la commande ?", "livraison-delais"),
    ("Où est mon colis ?", "livraison-suivi"),
    ("J'ai perdu mon mot de passe", "compte-motdepasse"),
    ("Puis-je payer en plusieurs fois ?", "paiement-moyens"),
    ("Où trouver ma facture ?", "facture-obtenir"),
    ("Quelle est la capitale du Sénégal ?", None),  # hors base : doit refuser
]


def evaluer(vectoriseurs, matrice, passages):
    print("\n--- ETAPE 5 : evaluation ---")
    justes = 0
    scores_corrects, score_hors_base = [], None
    for question, attendu in JEU_EVALUATION:
        trouves = rechercher(question, vectoriseurs, matrice, passages)
        if attendu is None:
            score_hors_base = trouves[0][1] if trouves else 0.0
            ok = (not trouves) or trouves[0][1] < SEUIL_PERTINENCE
            verdict = "REFUS correct" if ok else "ECHEC : a repondu"
        else:
            bon_doc = bool(trouves) and trouves[0][0]["source"] == attendu
            if bon_doc:
                scores_corrects.append(trouves[0][1])
            ok = bon_doc and trouves[0][1] >= SEUIL_PERTINENCE
            if ok:
                verdict = "OK"
            elif bon_doc:
                verdict = "REFUS a tort (sous le seuil)"
            else:
                verdict = f"ECHEC ({trouves[0][0]['source'] if trouves else 'rien'})"
        justes += ok
        score = trouves[0][1] if trouves else 0.0
        print(f"  [{verdict:<22}] {score:.2f}  {question}")
    print(f"\nReussite : {justes}/{len(JEU_EVALUATION)} ({justes/len(JEU_EVALUATION):.0%})")

    # --- Diagnostic : pourquoi on ne fait pas mieux ---
    print("\n--- DIAGNOSTIC ---")
    print(f"Score le plus bas parmi les bonnes reponses : {min(scores_corrects):.3f}")
    print(f"Score obtenu par la question HORS BASE       : {score_hors_base:.3f}")
    if score_hors_base >= min(scores_corrects):
        print("\nLes deux plages se CHEVAUCHENT : aucun seuil ne separe proprement")
        print("« la reponse n'est pas dans la base » de « la reponse y est, mal formulee ».")
        print("C'est la limite structurelle d'une recherche lexicale, et c'est la raison")
        print("pour laquelle un vrai systeme ajoute une seconde etape : on demande au")
        print("modele de verifier que le passage repond bien a la question, au lieu de")
        print("s'en remettre a un score de similarite.")
    print("\nLe cas « En combien de jours arrive la commande ? » remonte le suivi")
    print("de colis plutot que les delais : les deux passages partagent « jours »,")
    print("« commande » et « livraison ». Aucun mot ne les departage. Un plongement")
    print("de phrase y parviendrait ; TF-IDF, non.")
    return justes / len(JEU_EVALUATION)


def demonstration(vectoriseurs, matrice, passages):
    print("\n--- DEMONSTRATION ---")
    for question in ["Ma batterie ne tient plus, c'est sous garantie ?",
                     "Quelle est la capitale du Sénégal ?"]:
        trouves = rechercher(question, vectoriseurs, matrice, passages)
        reponse, sources = rediger_reponse(question, trouves)
        print(f"\nQ : {question}")
        print(f"R : {reponse}")
        if sources:
            print("  Sources : " + ", ".join(f"« {s['titre']} »" for s in sources[:2]))


def main():
    print("=" * 70)
    print("PROJET 3 --- ASSISTANT DOCUMENTAIRE (RAG)")
    print("=" * 70)
    passages = charger_passages()
    vectoriseurs, matrice = indexer(passages)
    demonstration(vectoriseurs, matrice, passages)
    evaluer(vectoriseurs, matrice, passages)
    print("\n" + "=" * 70)
    print("Termine.")
    print("=" * 70)


if __name__ == "__main__":
    main()
