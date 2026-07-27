#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROJET 4 --- Une automatisation intelligente (equivalent Python d'un flux n8n)
==============================================================================

n8n est un outil visuel : on ne l'execute pas depuis un script Python. Ce
fichier fait deux choses complementaires.

  1. Il IMPLEMENTE la meme chaine de traitement en Python, de bout en bout, sur
     des donnees reelles. Vous pouvez donc la faire tourner, la mesurer et la
     modifier sans installer quoi que ce soit.
  2. Il ECRIT le flux n8n correspondant dans workflow_n8n.json, importable tel
     quel dans n8n (menu Workflows > Import from File).

Jeu de donnees : 120 courriels de service client en francais, etiquetes par
    categorie (facturation, livraison, technique, commercial, resiliation) et
    par urgence. Fourni dans donnees/emails_service_client.csv.
    Il a ete construit par assemblage de formulations types : il sert a
    demontrer la chaine, il ne provient pas d'une boite reelle.

    Corpus public equivalent pour aller plus loin :
      - SMS Spam Collection (UCI), classification binaire de messages
        URL : https://archive.ics.uci.edu/dataset/228/sms+spam+collection
      - 20 Newsgroups, classification multi-classes, embarque dans scikit-learn
        via sklearn.datasets.fetch_20newsgroups (necessite le reseau)

Execution : python3 projet4_automatisation_n8n.py
Duree     : environ 5 secondes.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline

DOSSIER = Path(__file__).parent
GRAINE = 42
SEUIL_CONFIANCE = 0.60  # au-dessus : reponse automatique ; en dessous : humain


# --------------------------------------------------------------------------
# ETAPE 1 --- Choisir et analyser le processus
# --------------------------------------------------------------------------
def charger():
    print("--- ETAPE 1 : le processus a automatiser ---")
    df = pd.read_csv(DOSSIER / "donnees" / "emails_service_client.csv")
    print(f"{len(df)} courriels, {df['categorie'].nunique()} categories")
    print(df["categorie"].value_counts().to_string())
    print(f"Marques urgents : {int(df['urgent'].sum())} ({df['urgent'].mean():.0%})")
    print("\nProcessus manuel actuel : lire, classer, chercher le dossier,")
    print("rediger, envoyer. Environ 4 minutes par message.")
    return df


# --------------------------------------------------------------------------
# ETAPE 2 --- Construire le squelette : le noeud de classification
# --------------------------------------------------------------------------
def entrainer_classificateur(df):
    print("\n--- ETAPE 2 : noeud de classification ---")
    X_train, X_test, y_train, y_test = train_test_split(
        df["texte"], df["categorie"], test_size=0.25,
        random_state=GRAINE, stratify=df["categorie"],
    )

    # CalibratedClassifierCV : sans lui, les probabilites renvoyees sont mal
    # calibrees et le seuil de confiance ne veut pas dire grand-chose.
    modele = make_pipeline(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True),
        CalibratedClassifierCV(LogisticRegression(max_iter=1000, random_state=GRAINE), cv=3),
    ).fit(X_train, y_train)

    pred = modele.predict(X_test)
    exact = accuracy_score(y_test, pred)
    print(f"Exactitude sur le jeu de test : {exact:.1%}")

    # --- Lisez ce message, il vaut tout le reste de l'etape ---
    if exact > 0.97:
        print("\n  [!] UN SCORE PAREIL DOIT VOUS ALERTER, PAS VOUS REJOUIR.")
        print("  [!] Ce jeu de donnees a ete construit a partir de formulations types :")
        print("  [!] le jeu de test contient des messages tres proches de ceux vus a")
        print("  [!] l'entrainement. Le modele reconnait des tournures, il ne generalise")
        print("  [!] pas a du courrier reel. C'est une forme de fuite de donnees")
        print("  [!] (chapitre 4), et sur de vrais courriels vous obtiendrez plutot")
        print("  [!] 75 a 90 % selon la nettete des categories.")
        print("  [!] La regle : devant un score trop beau, cherchez la fuite.")
    print("\nDetail par categorie :")
    rap = classification_report(y_test, pred, output_dict=True, zero_division=0)
    for cat in sorted(df["categorie"].unique()):
        if cat in rap:
            print(f"  {cat:<14} precision {rap[cat]['precision']:.2f}  rappel {rap[cat]['recall']:.2f}")
    return modele, X_test, y_test


# --------------------------------------------------------------------------
# ETAPE 3 --- Ajouter l'intelligence et le routage
# --------------------------------------------------------------------------
REPONSES = {
    "facturation": "Votre facture est disponible dans l'espace client, rubrique « Commandes ». "
                   "En cas d'ecart de montant, notre service comptable revient vers vous sous 48 h.",
    "livraison":   "Votre numero de suivi figure dans le courriel d'expedition. "
                   "Si le suivi n'a pas bouge depuis plus de trois jours ouvres, nous ouvrons une enquete transporteur.",
    "technique":   "Merci de tenter une reinitialisation (appui long de 10 secondes). "
                   "Si le probleme persiste, indiquez-nous le code affiche a l'ecran.",
    "commercial":  "Un conseiller vous recontacte sous 24 h ouvrees avec une proposition chiffree. "
                   "Vous pouvez d'ici la consulter notre catalogue en ligne.",
    "resiliation": "Votre demande est enregistree. Un conseiller doit valider les conditions "
                   "applicables a votre contrat avant confirmation.",
}
# Categories ou l'on n'envoie JAMAIS automatiquement : l'acte est irreversible
# ou engage juridiquement l'entreprise.
TOUJOURS_HUMAIN = {"resiliation"}


def router(modele, textes):
    """Classe, evalue la confiance, et decide qui traite le message."""
    probas = modele.predict_proba(textes)
    classes = modele.classes_
    decisions = []
    for texte, p in zip(textes, probas):
        i = int(np.argmax(p))
        cat, conf = classes[i], float(p[i])
        urgent = any(k in texte.lower() for k in
                     ("urgent", "mécontent", "bloqué", "double prélèvement"))
        if cat in TOUJOURS_HUMAIN:
            voie = "HUMAIN (categorie sensible)"
        elif conf < SEUIL_CONFIANCE:
            voie = "HUMAIN (confiance insuffisante)"
        elif urgent:
            voie = "HUMAIN (urgence detectee)"
        else:
            voie = "AUTOMATIQUE"
        decisions.append({"texte": texte, "categorie": cat, "confiance": conf,
                          "urgent": urgent, "voie": voie,
                          "brouillon": REPONSES.get(cat, "")})
    return decisions


# --------------------------------------------------------------------------
# ETAPE 4 --- Inserer la validation humaine et mesurer
# --------------------------------------------------------------------------
def mesurer(decisions, y_vrai):
    print("\n--- ETAPE 4 : routage et validation humaine ---")
    df = pd.DataFrame(decisions)
    df["vraie_categorie"] = list(y_vrai)
    df["correct"] = df["categorie"] == df["vraie_categorie"]

    for voie, groupe in df.groupby("voie"):
        part = len(groupe) / len(df)
        print(f"  {voie:<32} {len(groupe):3d} msg ({part:5.1%})  "
              f"classement juste : {groupe['correct'].mean():.0%}")

    auto = df[df["voie"] == "AUTOMATIQUE"]
    print(f"\nSur la voie automatique : {len(auto)} messages, "
          f"{(~auto['correct']).sum()} mal classes.")
    if len(auto):
        print(f"Taux d'erreur non rattrape par un humain : {(~auto['correct']).mean():.1%}")
    return df


# --------------------------------------------------------------------------
# ETAPE 5 --- Chiffrer le gain, et generer le flux n8n
# --------------------------------------------------------------------------
def chiffrer(df, volume_jour=200, minutes_manuel=4.0, minutes_relecture=0.5):
    print("\n--- ETAPE 5 : gain attendu ---")
    part_auto = (df["voie"] == "AUTOMATIQUE").mean()
    cout_avant = volume_jour * minutes_manuel
    cout_apres = (volume_jour * part_auto * minutes_relecture
                  + volume_jour * (1 - part_auto) * minutes_manuel * 0.6)
    print(f"Hypotheses : {volume_jour} messages/jour, {minutes_manuel} min en manuel,")
    print(f"{minutes_relecture} min de relecture pour un message automatise,")
    print("et 40 % de temps economise sur les messages transmis (dossier prepare).")
    print(f"\n  Avant : {cout_avant:6.0f} min/jour  ({cout_avant/60:.1f} h)")
    print(f"  Apres : {cout_apres:6.0f} min/jour  ({cout_apres/60:.1f} h)")
    print(f"  Gain  : {cout_avant - cout_apres:6.0f} min/jour  "
          f"({(1 - cout_apres/cout_avant):.0%})")


def ecrire_workflow_n8n(chemin):
    """Ecrit le flux equivalent, importable dans n8n."""
    flux = {
        "name": "Tri intelligent des courriels entrants",
        "nodes": [
            {"parameters": {"pollTimes": {"item": [{"mode": "everyMinute"}]}},
             "name": "Declencheur : nouveau courriel", "type": "n8n-nodes-base.gmailTrigger",
             "typeVersion": 1, "position": [0, 300]},
            {"parameters": {"modelId": "gpt-4o-mini", "messages": {"values": [
                {"role": "system", "content":
                 "Tu classes des courriels de service client. Reponds UNIQUEMENT en JSON : "
                 "{\"categorie\": une valeur parmi facturation|livraison|technique|commercial|resiliation, "
                 "\"confiance\": nombre entre 0 et 1, \"urgent\": true ou false}. "
                 "Si tu hesites, baisse la confiance au lieu de deviner."},
                {"role": "user", "content": "={{ $json.subject }}\n\n{{ $json.text }}"}]},
                "options": {"temperature": 0}},
             "name": "Classer (LLM)", "type": "n8n-nodes-base.openAi",
             "typeVersion": 1, "position": [220, 300]},
            {"parameters": {"conditions": {"boolean": [
                {"value1": "={{ $json.categorie === 'resiliation' || $json.urgent === true "
                           "|| $json.confiance < 0.6 }}", "value2": True}]}},
             "name": "Doit passer par un humain ?", "type": "n8n-nodes-base.if",
             "typeVersion": 1, "position": [440, 300]},
            {"parameters": {"modelId": "gpt-4o-mini", "messages": {"values": [
                {"role": "system", "content":
                 "Tu rediges une reponse de service client, courtoise et breve (120 mots maximum). "
                 "Appuie-toi uniquement sur les elements fournis. Si une information manque, "
                 "dis-le explicitement au lieu de l'inventer."},
                {"role": "user", "content": "={{ $json.text }}"}]},
                "options": {"temperature": 0.3}},
             "name": "Rediger la reponse (LLM)", "type": "n8n-nodes-base.openAi",
             "typeVersion": 1, "position": [660, 200]},
            {"parameters": {}, "name": "Envoyer au client",
             "type": "n8n-nodes-base.gmail", "typeVersion": 2, "position": [880, 200]},
            {"parameters": {"channel": "#support-a-traiter"},
             "name": "Transmettre a un agent (avec resume)",
             "type": "n8n-nodes-base.slack", "typeVersion": 2, "position": [660, 400]},
            {"parameters": {}, "name": "Journaliser (base de donnees)",
             "type": "n8n-nodes-base.postgres", "typeVersion": 2, "position": [1100, 300]},
        ],
        "connections": {
            "Declencheur : nouveau courriel": {"main": [[{"node": "Classer (LLM)", "type": "main", "index": 0}]]},
            "Classer (LLM)": {"main": [[{"node": "Doit passer par un humain ?", "type": "main", "index": 0}]]},
            "Doit passer par un humain ?": {"main": [
                [{"node": "Transmettre a un agent (avec resume)", "type": "main", "index": 0}],
                [{"node": "Rediger la reponse (LLM)", "type": "main", "index": 0}]]},
            "Rediger la reponse (LLM)": {"main": [[{"node": "Envoyer au client", "type": "main", "index": 0}]]},
            "Envoyer au client": {"main": [[{"node": "Journaliser (base de donnees)", "type": "main", "index": 0}]]},
            "Transmettre a un agent (avec resume)": {"main": [[{"node": "Journaliser (base de donnees)", "type": "main", "index": 0}]]},
        },
        "settings": {"executionOrder": "v1"},
    }
    chemin.write_text(json.dumps(flux, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nFlux n8n ecrit dans {chemin.name} ({len(flux['nodes'])} noeuds).")
    print("Import : n8n > Workflows > Import from File. Les identifiants de")
    print("connexion (Gmail, OpenAI, Slack, Postgres) restent a renseigner.")


def main():
    print("=" * 70)
    print("PROJET 4 --- AUTOMATISATION INTELLIGENTE DU SERVICE CLIENT")
    print("=" * 70)
    df = charger()
    modele, X_test, y_test = entrainer_classificateur(df)
    decisions = router(modele, list(X_test))
    resultat = mesurer(decisions, y_test)
    chiffrer(resultat)
    ecrire_workflow_n8n(DOSSIER / "workflow_n8n.json")
    print("\n" + "=" * 70)
    print("Termine.")
    print("=" * 70)


if __name__ == "__main__":
    main()
