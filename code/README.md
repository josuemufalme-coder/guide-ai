# Code du manuel

Scripts des quatre projets guidés de la partie VI, et jeux de données associés.

## Exécution

```bash
pip install -r requirements.txt
python3 projet1_prix_immobilier.py
python3 projet2_classificateur_images.py
python3 projet3_assistant_documentaire.py
python3 projet4_automatisation_n8n.py
```

Chaque script est autonome et s'exécute sans argument. Aucun ne dépasse
trente secondes sur une machine ordinaire.

## Fonctionnement hors ligne

Les scripts nomment un jeu de données public et donnent son URL. Deux d'entre
eux fonctionnent **sans aucun accès réseau** :

| Script | Jeu de données | Réseau requis |
|---|---|---|
| `projet1_prix_immobilier.py` | California Housing (StatLib) | tenté, **repli local automatique** |
| `projet2_classificateur_images.py` | Optical Recognition of Handwritten Digits (UCI) | non, embarqué dans scikit-learn |
| `projet3_assistant_documentaire.py` | base documentaire fournie | non |
| `projet4_automatisation_n8n.py` | courriels fournis | non |

Le projet 1 tente le téléchargement du vrai jeu de données ; s'il échoue, il
bascule sur un jeu synthétique local qu'il génère lui-même, et le signale.
La démarche pédagogique est identique dans les deux cas.

## Contenu

- `donnees/logements_synthetiques.csv` — repli du projet 1, généré par le script.
- `donnees/base_documentaire.json` — douze fiches produit, corpus du projet 3.
- `donnees/emails_service_client.csv` — 120 courriels étiquetés, projet 4.
- `workflow_n8n.json` — flux n8n du projet 4, écrit par le script, importable.
