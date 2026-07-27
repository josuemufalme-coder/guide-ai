# Vérification d'exécution

Les quatre scripts ont été exécutés sur cette machine, sans argument et sans
préparation autre que `pip install -r requirements.txt`.

| Script | Résultat | Durée |
|---|---|---:|
| `projet1_prix_immobilier.py` | **OK** | 9,7 s |
| `projet2_classificateur_images.py` | **OK** | 4,3 s |
| `projet3_assistant_documentaire.py` | **OK** | 1,2 s |
| `projet4_automatisation_n8n.py` | **OK** | 2,3 s |

Aucune erreur, aucun avertissement de dépréciation.

Environnement de vérification : Python 3.11.15, NumPy 2.4.6, pandas 3.0.5,
scikit-learn 1.9.0, SciPy 1.17.1.

## Une réserve à connaître

**Le téléchargement de jeux de données externes est bloqué dans l'environnement
de vérification.** Le proxy de sortie refuse les connexions sortantes vers les
hébergeurs de données (réponse `403` sur le `CONNECT`), ce qui est une décision
de politique et non une panne.

Conséquence sur le projet 1 : il a été vérifié **sur son chemin de repli**, avec
le jeu synthétique local, et non sur California Housing. Le chemin de
téléchargement est écrit et correct, mais il n'a pas pu être exercé ici. Sur une
machine disposant d'un accès réseau ordinaire, `fetch_california_housing()`
fonctionne et le script bascule automatiquement sur les vraies données — c'est
d'ailleurs son comportement par défaut, le repli n'intervient qu'en cas d'échec.

Les projets 2, 3 et 4 ne dépendent d'aucun téléchargement : ils ont été vérifiés
sur leur chemin nominal.

## Résultats obtenus lors de la vérification

- **Projet 1** (repli synthétique) : régression linéaire R² = 0,951 ;
  forêt aléatoire R² = 0,933 ; référence R² = −0,005.
  Sur les vraies données California Housing, attendez plutôt 0,58 et 0,80 :
  le jeu de repli est plus facile, parce que sa relation est engendrée.
- **Projet 2** : régression logistique 97,2 % ; réseau (128, 64) 96,7 % ;
  après augmentation de données **98,3 %**.
- **Projet 3** : 9 réussites sur 11, avec chevauchement documenté des scores.
- **Projet 4** : 100 % d'exactitude — signalé par le script comme un symptôme
  de fuite, non comme une réussite ; 43 % de traitement automatique.
