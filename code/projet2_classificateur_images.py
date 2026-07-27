#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROJET 2 --- Un classificateur d'images
=======================================

Jeu de donnees : Optical Recognition of Handwritten Digits (UCI).
    Source  : UCI Machine Learning Repository, don de E. Alpaydin et C. Kaynak
    URL     : https://archive.ics.uci.edu/dataset/80/optical+recognition+of+handwritten+digits
    1 797 images de chiffres manuscrits, 8x8 pixels en niveaux de gris (0-16),
    dix classes (chiffres 0 a 9).
    Ce jeu est EMBARQUE dans scikit-learn : aucun telechargement n'est requis,
    le script fonctionne hors ligne.

Grand frere du meme probleme : MNIST (70 000 images 28x28).
    URL : https://yann.lecun.com/exdb/mnist/
    Pour l'utiliser, remplacer load_digits() par
    fetch_openml("mnist_784", version=1, as_frame=False)  --- necessite le reseau,
    et l'entrainement passe de quelques secondes a plusieurs minutes.

Execution : python3 projet2_classificateur_images.py
Duree     : environ 20 secondes.
"""

import warnings

import numpy as np
from sklearn.datasets import load_digits
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
GRAINE = 42


# --------------------------------------------------------------------------
# ETAPE 1 --- Choisir le jeu de donnees et l'objectif
# --------------------------------------------------------------------------
def charger():
    print("--- ETAPE 1 : chargement ---")
    jeu = load_digits()
    X, y = jeu.data, jeu.target
    print(f"{X.shape[0]} images de {int(np.sqrt(X.shape[1]))}x{int(np.sqrt(X.shape[1]))} pixels")
    print(f"{len(np.unique(y))} classes, valeurs des pixels de {X.min():.0f} a {X.max():.0f}")

    # Une image affichee en texte, pour voir ce que le modele recoit vraiment.
    print("\nPremiere image du jeu (chiffre {}) :".format(y[0]))
    for ligne in jeu.images[0]:
        print("  " + "".join(" .:-=+*#%@"[int(v * 9 / 16)] for v in ligne))

    # Classes equilibrees ou non : cela decide si l'exactitude est un bon juge.
    effectifs = np.bincount(y)
    print(f"\nEffectif par classe : de {effectifs.min()} a {effectifs.max()}")
    print("-> classes equilibrees, l'exactitude est ici un indicateur honnete.")
    return X, y


# --------------------------------------------------------------------------
# ETAPE 2 --- Construire un premier reseau (et sa reference)
# --------------------------------------------------------------------------
def preparer_et_referencer(X, y):
    print("\n--- ETAPE 2 : separation et reference ---")
    # stratify : chaque classe garde la meme proportion dans les deux paquets.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=GRAINE, stratify=y
    )
    print(f"Entrainement : {len(X_train)} | Test : {len(X_test)}")

    bete = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
    exact_bete = accuracy_score(y_test, bete.predict(X_test))
    print(f"Reference stupide (toujours la classe majoritaire) : {exact_bete:.1%}")
    print("-> tout modele doit battre ce chiffre pour meriter d'exister.")
    return X_train, X_test, y_train, y_test, exact_bete


# --------------------------------------------------------------------------
# ETAPE 3 --- Entrainer et suivre l'apprentissage
# --------------------------------------------------------------------------
def entrainer(X_train, X_test, y_train, y_test):
    print("\n--- ETAPE 3 : entrainement ---")
    modeles = {
        "Regression logistique": make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=2000, random_state=GRAINE)
        ),
        "Reseau 1 couche (64)": make_pipeline(
            StandardScaler(),
            MLPClassifier(hidden_layer_sizes=(64,), max_iter=600,
                          random_state=GRAINE, early_stopping=True),
        ),
        "Reseau 2 couches (128, 64)": make_pipeline(
            StandardScaler(),
            MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=600,
                          random_state=GRAINE, early_stopping=True),
        ),
    }

    resultats = {}
    for nom, modele in modeles.items():
        modele.fit(X_train, y_train)
        exact_tr = accuracy_score(y_train, modele.predict(X_train))
        exact_te = accuracy_score(y_test, modele.predict(X_test))
        resultats[nom] = {"modele": modele, "train": exact_tr, "test": exact_te}
        ecart = exact_tr - exact_te
        drapeau = "  <-- ecart notable, surveiller le sur-apprentissage" if ecart > 0.05 else ""
        print(f"  {nom:<28} train {exact_tr:.1%} | test {exact_te:.1%}{drapeau}")
    return resultats


# --------------------------------------------------------------------------
# ETAPE 4 --- Ameliorer par l'augmentation de donnees
# --------------------------------------------------------------------------
def augmenter(X_train, y_train, X_test, y_test, exact_ref):
    print("\n--- ETAPE 4 : augmentation de donnees ---")
    # On decale chaque image d'un pixel dans les quatre directions : le chiffre
    # reste le meme, le reseau apprend a ignorer la position exacte.
    images = X_train.reshape(-1, 8, 8)
    lots, etiquettes = [X_train], [y_train]
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        decalees = np.roll(np.roll(images, dy, axis=1), dx, axis=2)
        lots.append(decalees.reshape(len(images), -1))
        etiquettes.append(y_train)

    X_aug = np.vstack(lots)
    y_aug = np.concatenate(etiquettes)
    print(f"Jeu d'entrainement : {len(X_train)} -> {len(X_aug)} images (x5)")

    modele = make_pipeline(
        StandardScaler(),
        MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=600,
                      random_state=GRAINE, early_stopping=True),
    ).fit(X_aug, y_aug)

    exact = accuracy_score(y_test, modele.predict(X_test))
    print(f"Exactitude apres augmentation : {exact:.1%} (avant : {exact_ref:.1%})")
    return modele, exact


# --------------------------------------------------------------------------
# ETAPE 5 --- Regarder les erreurs, pas seulement le score
# --------------------------------------------------------------------------
def analyser_erreurs(modele, X_test, y_test):
    print("\n--- ETAPE 5 : analyse des erreurs ---")
    pred = modele.predict(X_test)
    mat = confusion_matrix(y_test, pred)

    print("Matrice de confusion (lignes = verite, colonnes = prediction) :")
    print("     " + "".join(f"{i:4d}" for i in range(10)))
    for i, ligne in enumerate(mat):
        print(f"  {i}  " + "".join(f"{v:4d}" for v in ligne))

    confusions = [
        (mat[i, j], i, j)
        for i in range(10) for j in range(10) if i != j and mat[i, j] > 0
    ]
    confusions.sort(reverse=True)
    print("\nConfusions les plus frequentes :")
    for n, vrai, prevu in confusions[:3]:
        print(f"  {vrai} pris pour {prevu} : {n} fois")
    if not confusions:
        print("  aucune erreur sur le jeu de test")

    print("\nRapport par classe (extrait) :")
    rapport = classification_report(y_test, pred, output_dict=True, zero_division=0)
    pires = sorted(
        ((rapport[str(c)]["f1-score"], c) for c in range(10)), key=lambda t: t[0]
    )[:3]
    for f1, c in pires:
        print(f"  chiffre {c} : F1 = {f1:.3f}")


def main():
    print("=" * 70)
    print("PROJET 2 --- CLASSIFICATEUR D'IMAGES")
    print("=" * 70)
    X, y = charger()
    X_train, X_test, y_train, y_test, _ = preparer_et_referencer(X, y)
    resultats = entrainer(X_train, X_test, y_train, y_test)
    meilleur = max(resultats, key=lambda k: resultats[k]["test"])
    modele, _ = augmenter(X_train, y_train, X_test, y_test, resultats[meilleur]["test"])
    analyser_erreurs(modele, X_test, y_test)
    print("\n" + "=" * 70)
    print("Termine.")
    print("=" * 70)


if __name__ == "__main__":
    main()
