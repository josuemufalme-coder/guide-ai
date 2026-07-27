#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROJET 1 --- Un predicteur de prix immobilier
=============================================

Jeu de donnees : California Housing (recensement americain de 1990).
    Source  : StatLib, Carnegie Mellon University
    URL     : https://www.dcc.fc.up.pt/~ltorgo/Regression/cal_housing.html
    Charge par scikit-learn via fetch_california_housing().
    20 640 quartiers, 8 variables, cible = prix median du logement.

Si le telechargement est impossible (machine hors ligne, proxy filtrant), le
script bascule automatiquement sur un jeu de donnees SYNTHETIQUE genere
localement, de structure comparable. Il le signale clairement : les chiffres
obtenus dans ce mode illustrent la demarche, ils ne decrivent pas la Californie.

Execution : python3 projet1_prix_immobilier.py
Duree     : environ 10 secondes.
"""

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
GRAINE = 42
DOSSIER_DONNEES = Path(__file__).parent / "donnees"


# --------------------------------------------------------------------------
# ETAPE 1 --- Comprendre le probleme et charger les donnees
# --------------------------------------------------------------------------
def charger_donnees():
    """Tente le vrai jeu de donnees, bascule sur le repli local si besoin."""
    try:
        from sklearn.datasets import fetch_california_housing

        jeu = fetch_california_housing(as_frame=True)
        df = jeu.frame.rename(columns={"MedHouseVal": "prix"})
        print("Donnees : California Housing (20 640 quartiers, source StatLib).")
        return df, "prix", True
    except Exception as exc:  # noqa: BLE001
        print(f"[!] Telechargement impossible ({type(exc).__name__}).")
        print("[!] Bascule sur le jeu de donnees SYNTHETIQUE de secours.")
        print("[!] La demarche est identique, les chiffres ne decrivent rien de reel.")
        chemin = DOSSIER_DONNEES / "logements_synthetiques.csv"
        if not chemin.exists():
            _fabriquer_jeu_de_secours(chemin)
        return pd.read_csv(chemin), "prix", False


def _fabriquer_jeu_de_secours(chemin):
    """Genere un jeu de donnees immobilier plausible et reproductible."""
    rng = np.random.default_rng(GRAINE)
    n = 5000
    surface = rng.gamma(shape=6.0, scale=15.0, size=n) + 20      # m2
    pieces = np.clip((surface / 22 + rng.normal(0, 0.7, n)).round(), 1, 9)
    age = rng.integers(0, 90, n)                                  # annees
    revenu = rng.lognormal(mean=1.0, sigma=0.45, size=n)          # dizaines de k$
    distance = rng.exponential(scale=8.0, size=n)                 # km du centre

    # Prix construit a partir d'une relation connue, plus du bruit.
    prix = (
        0.030 * surface
        + 0.120 * pieces
        + 0.450 * revenu
        - 0.060 * distance
        - 0.004 * age
        + rng.normal(0, 0.35, n)
    )
    prix = np.clip(prix, 0.2, None)

    chemin.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            "surface_m2": surface.round(1),
            "pieces": pieces,
            "age_annees": age,
            "revenu_median": revenu.round(3),
            "distance_centre_km": distance.round(2),
            "prix": prix.round(3),
        }
    ).to_csv(chemin, index=False)
    print(f"[i] Jeu de secours ecrit dans {chemin}")


# --------------------------------------------------------------------------
# ETAPE 2 --- Nettoyer et explorer
# --------------------------------------------------------------------------
def explorer(df, cible):
    print("\n--- ETAPE 2 : exploration ---")
    print(f"Dimensions : {df.shape[0]} lignes, {df.shape[1]} colonnes")

    manquantes = df.isna().sum()
    print(f"Valeurs manquantes : {int(manquantes.sum())}")

    print(f"\nCible « {cible} » :")
    print(f"  mediane {df[cible].median():.2f}   moyenne {df[cible].mean():.2f}")
    print(f"  min {df[cible].min():.2f}   max {df[cible].max():.2f}")

    # La moyenne au-dessus de la mediane signale une distribution etiree a droite,
    # ce qui est la norme pour des prix : quelques biens tres chers tirent la moyenne.
    if df[cible].mean() > df[cible].median():
        print("  -> distribution etiree vers le haut (quelques biens tres chers)")

    corr = df.corr(numeric_only=True)[cible].drop(cible).sort_values(key=abs, ascending=False)
    print("\nCorrelations avec le prix (les trois plus fortes) :")
    for nom, val in corr.head(3).items():
        print(f"  {nom:<22} {val:+.3f}")
    return corr


# --------------------------------------------------------------------------
# ETAPE 3 --- Preparer les caracteristiques
# --------------------------------------------------------------------------
def preparer(df, cible):
    print("\n--- ETAPE 3 : preparation ---")
    X = df.drop(columns=[cible])
    y = df[cible]

    # On separe AVANT toute transformation : c'est la regle anti-fuite du chapitre 4.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=GRAINE
    )
    print(f"Entrainement : {len(X_train)} lignes | Test : {len(X_test)} lignes")
    print("La normalisation sera calculee dans le pipeline, sur l'entrainement seul.")
    return X_train, X_test, y_train, y_test


# --------------------------------------------------------------------------
# ETAPE 4 --- Entrainer et comparer des modeles
# --------------------------------------------------------------------------
def entrainer(X_train, X_test, y_train, y_test):
    print("\n--- ETAPE 4 : entrainement ---")

    modeles = {
        "Reference (mediane)": DummyRegressor(strategy="median"),
        "Regression lineaire": make_pipeline(StandardScaler(), LinearRegression()),
        "Foret aleatoire": RandomForestRegressor(
            n_estimators=200, max_depth=16, random_state=GRAINE, n_jobs=-1
        ),
    }

    resultats = {}
    for nom, modele in modeles.items():
        modele.fit(X_train, y_train)
        pred = modele.predict(X_test)
        resultats[nom] = {
            "modele": modele,
            "MAE": mean_absolute_error(y_test, pred),
            "R2": r2_score(y_test, pred),
        }
        print(f"  {nom:<22} MAE = {resultats[nom]['MAE']:.3f}   R2 = {resultats[nom]['R2']:+.3f}")

    # La validation croisee verifie que le score n'est pas un coup de chance
    # du decoupage : cinq decoupages differents, cinq scores.
    meilleur = max(resultats, key=lambda k: resultats[k]["R2"])
    scores = cross_val_score(
        modeles[meilleur], X_train, y_train, cv=5, scoring="r2", n_jobs=-1
    )
    print(f"\nValidation croisee du meilleur ({meilleur}) :")
    print(f"  R2 = {scores.mean():.3f} +/- {scores.std():.3f}  sur 5 decoupages")
    return resultats, meilleur


# --------------------------------------------------------------------------
# ETAPE 5 --- Evaluer et interpreter
# --------------------------------------------------------------------------
def interpreter(resultats, meilleur, X_train, y_test):
    print("\n--- ETAPE 5 : interpretation ---")
    ref = resultats["Reference (mediane)"]["MAE"]
    mae = resultats[meilleur]["MAE"]
    print(f"Le modele retenu reduit l'erreur moyenne de {(1 - mae / ref) * 100:.0f} %")
    print(f"par rapport a la reference stupide ({ref:.3f} -> {mae:.3f}).")

    modele = resultats[meilleur]["modele"]
    if hasattr(modele, "feature_importances_"):
        print("\nVariables les plus utilisees par le modele :")
        imp = pd.Series(modele.feature_importances_, index=X_train.columns)
        for nom, val in imp.sort_values(ascending=False).head(4).items():
            print(f"  {nom:<22} {val:.3f}")

    print(f"\nOrdre de grandeur de l'erreur : +/- {mae:.2f} sur une cible dont")
    print(f"la mediane vaut {np.median(y_test):.2f}, soit environ {mae / np.median(y_test) * 100:.0f} % d'ecart typique.")


def main():
    print("=" * 70)
    print("PROJET 1 --- PREDICTEUR DE PRIX IMMOBILIER")
    print("=" * 70)
    df, cible, reel = charger_donnees()
    explorer(df, cible)
    X_train, X_test, y_train, y_test = preparer(df, cible)
    resultats, meilleur = entrainer(X_train, X_test, y_train, y_test)
    interpreter(resultats, meilleur, X_train, y_test)
    print("\n" + "=" * 70)
    print("Termine." + ("" if reel else "  (mode de secours : donnees synthetiques)"))
    print("=" * 70)


if __name__ == "__main__":
    main()
