# RAPPORT — Code, projets et exercices (prompt 5)

**Commits :** `20d65bc` → `aa6f1e2` (quatre commits, un par point)

---

## 1. Projets — les quatre sont exécutables

Chaque projet de la partie VI reçoit désormais un jeu de données nommé avec sa source et son URL, le code Python commenté en français étape par étape, les ordres de grandeur attendus, et une section « ce qui peut mal se passer » sous forme de tableau symptôme / cause / remède.

| Projet | Jeu de données | Source | Réseau requis |
|---|---|---|---|
| 1 — Prix immobilier | California Housing | StatLib, Carnegie Mellon | tenté, **repli local automatique** |
| 2 — Classificateur d'images | Handwritten Digits (8×8) | UCI Machine Learning Repository | **non**, embarqué dans scikit-learn |
| 3 — Assistant documentaire | 12 fiches fournies | livrées dans `code/donnees/` | **non** |
| 4 — Automatisation | 120 courriels étiquetés | livrés dans `code/donnees/` | **non** |

**Trois choix que je dois vous expliquer.**

**Le projet 2 utilise le jeu UCI 8×8 plutôt que MNIST.** Raison : il est embarqué dans scikit-learn, donc le projet tourne hors ligne et s'entraîne en quatre secondes au lieu de plusieurs minutes. Le problème est rigoureusement le même à l'échelle près, et le passage à MNIST tient en une ligne, indiquée dans le texte.

**Le projet 3 utilise une recherche lexicale et non des plongements de phrases.** Même raison. Et la limite qui en découle s'est révélée plus instructive que la solution parfaite : la question hors base obtient un score de **0,166** tandis que la plus faible des bonnes réponses obtient **0,149**. Les deux plages se chevauchent, donc *aucun seuil ne peut séparer proprement « la réponse n'est pas dans la base » de « la réponse y est, mal formulée »*. Le script le calcule, l'affiche et l'explique. C'est un enseignement, pas un défaut masqué.

**Le projet 4 affiche 100 % d'exactitude, et le script le signale comme une alarme.** Le jeu de courriels étant bâti sur des formulations types, l'entraînement et le test se ressemblent trop : c'est une forme de fuite de données. Le script imprime un avertissement de six lignes expliquant qu'il faut attendre 75 à 90 % sur du courrier réel. Je préfère un projet qui vous apprend à vous méfier d'un score parfait qu'un projet qui vous en fabrique un.

---

## 2. Vérification — tous passent, avec une réserve

Les quatre scripts ont été exécutés sur cette machine, sans argument, après un simple `pip install -r requirements.txt`.

| Script | Résultat | Durée |
|---|---|---:|
| `projet1_prix_immobilier.py` | **OK** | 9,7 s |
| `projet2_classificateur_images.py` | **OK** | 4,3 s |
| `projet3_assistant_documentaire.py` | **OK** | 1,2 s |
| `projet4_automatisation_n8n.py` | **OK** | 2,3 s |

Aucune erreur, aucun avertissement de dépréciation.

**La réserve, et elle est importante.** Le téléchargement de jeux de données externes est **bloqué dans cet environnement** : le proxy de sortie répond `403` au `CONNECT` vers les hébergeurs de données. C'est une décision de politique d'organisation, que la documentation du proxy demande explicitement de signaler plutôt que de contourner.

Conséquence : **le projet 1 a été vérifié sur son chemin de repli**, avec le jeu synthétique local, et non sur California Housing. Le chemin de téléchargement est écrit et correct, mais il n'a pas pu être exercé ici. Sur une machine au réseau ordinaire, `fetch_california_housing()` fonctionne et le script prend automatiquement les vraies données — le repli n'intervient qu'en cas d'échec.

Les projets 2, 3 et 4 ne dépendent d'aucun téléchargement : ils ont été vérifiés sur leur chemin nominal.

Résultats obtenus lors de la vérification, consignés dans `code/VERIFICATION.md` : projet 1 (repli) R² = 0,951 ; projet 2 exactitude 98,3 % après augmentation ; projet 3 réussite 9/11 ; projet 4 43 % de traitement automatique.

---

## 3. Code dans les chapitres — de 5 à 27 blocs

Dix extraits courts et commentés en français, ajoutés là où le manuel enseignait sans montrer. **Chacun a été exécuté avant insertion**, et les sorties annotées dans les commentaires sont celles réellement obtenues.

| Chapitre | Extrait | Ce qu'il montre |
|---|---|---|
| 3 | Produit scalaire et dimensions | 42 contre 9 ; la règle `(n,m)×(m,p)` |
| 3 | Descente de gradient complète | coût 12,667 → 0,216 → 0,067, sans bibliothèque |
| 4 | `isna`, `groupby`, médiane | le `count` compte les valeurs, pas les lignes |
| 4 | Pipeline anti-fuite | pourquoi on sépare avant de normaliser |
| 5 | Déroulé supervisé complet | référence stupide comprise |
| 5 | Effet du seuil | rappel de 1,000 à seuil 0,3 |
| 6 | Réseau deux couches en NumPy | un neurone éteint par la ReLU, visible |
| 6 | Les quatre activations | pourquoi la sigmoïde tue le gradient |
| 9 | TF-IDF et cosinus | 0,26 contre 0,07, et pourquoi c'est décevant |
| 10 | Température | 92,4 % contre 43,8 % selon le réglage |

**Un point technique à signaler.** Les cinq extraits d'origine avaient été aplatis par pandoc en texte échappé, avec des barres obliques en fin de ligne — ils ne se rendent pas comme du code. Les vingt-deux nouveaux sont en blocs délimités et se rendront correctement. **Les cinq anciens restent à reprendre**, je ne les ai pas touchés pour ne pas modifier votre texte sans vous le dire.

---

## 4. Exercices — 64 problèmes gradués, corrigés en annexe

**D'abord une rectification de comptage.** Votre énoncé indique « 14 exercices pour 24 chapitres ». Le décompte réel est différent :

| | Nombre |
|---|---:|
| Exercices dirigés en fin de chapitre | **82** |
| Travaux pratiques « À VOUS DE JOUER » | **25** |
| Problèmes corrigés de la partie VII | **14** |

Les 14 désignaient donc les seuls problèmes **corrigés**. Le vrai manque n'était pas le nombre d'exercices — il y en avait 121 — mais deux autres choses : les 82 exercices de chapitre n'ont **aucun corrigé**, et rien n'était gradué par difficulté.

**Ce que j'ai fait.** La partie VII passe de 6 thèmes et 14 problèmes à **10 thèmes et 64 problèmes**, couvrant désormais Python, les données, la vision, le renforcement, l'éthique et la mise en production, qui n'y figuraient pas.

| Niveau | Nombre | Ce qu'on y fait |
|---|---:|---|
| **Niveau 1 — Vérifier** | 16 | contrôler qu'une notion est comprise ; quelques minutes |
| **Niveau 2 — Appliquer** | 35 | mettre en œuvre sur un cas, souvent chiffré ; dix à vingt minutes |
| **Niveau 3 — Raisonner** | 13 | diagnostiquer, arbitrer, justifier ; aucune réponse unique |

Les **64 corrigés** sont rassemblés dans une section « Corrigés des exercices » en partie VIII, avec un renvoi depuis chaque énoncé. Vérification automatique : 64 énoncés, 64 corrigés, 64 renvois, **aucun orphelin de part et d'autre**, et plus aucune correction dans la partie VII.

**Vos 14 problèmes d'origine et leurs corrigés sont repris mot pour mot**, redistribués dans les nouveaux thèmes selon leur sujet.

**Deux titres ajustés par conséquence**, le mot « corrigés » étant devenu faux une fois les corrigés déplacés : la partie VII devient « S'entraîner : soixante-quatre exercices », et la ligne correspondante du plan de lecture a été mise à jour. Dites-moi si vous préférez une autre formulation.

---

## 5. Ce qui reste

- **Les 5 extraits de code d'origine** sont encore en texte échappé et non en blocs. À reprendre au prompt 7, en même temps que la mise en page.
- **Les 82 exercices dirigés de fin de chapitre** n'ont toujours pas de corrigé. Ce n'était pas demandé ici — les corriger porterait l'annexe à 146 entrées. Dites-moi si vous le souhaitez.
- **Les 17 images**, inchangées depuis le prompt 2 : numéro incrusté, 185 dpi, trois libellés qui débordent. C'est le seul travail qui doit se faire hors de ce dépôt.
