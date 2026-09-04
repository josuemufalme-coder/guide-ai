# Entreprendre au Congo

Chaîne de fabrication du livre **« Entreprendre au Congo — Comprendre
l'entrepreneuriat et savoir par où commencer »**, de Ruth ZADI PUKUTA.
8 parties, 16 chapitres, environ 23 000 mots, en français.

Le cahier des charges qui régit ce dépôt est
[`AUDIT-ET-CAHIER-DES-CHARGES-Claude-Code.md`](AUDIT-ET-CAHIER-DES-CHARGES-Claude-Code.md).
Il fait autorité. En cas de divergence avec ce fichier-ci, c'est lui qui tranche.

## Où en est le projet

| Phase | Objet | État |
| --- | --- | --- |
| 0 | Mise en place, découpage, contrôle d'intégrité | **en cours de validation** |
| 1 | Gabarit typographique (césure, police, justification) | à venir |
| 2 | Normalisation typographique du texte source | à venir |
| 3 | Appareil de notes | à venir |
| 4 | Figures et tableaux | à venir |
| 5 | Cohérence éditoriale | à venir |
| 6 | Liminaires et fin de volume | à venir |
| 7 | Composition et mise en page | à venir |
| 8 | Contrôle qualité automatisé | à venir |
| 9 | Livrables | à venir |

Une phase se termine par un point d'arrêt : rapport présenté, validation
attendue. Aucune phase n'en enchaîne une autre.

## Arborescence

```
src/         le manuscrit, un fichier par chapitre — source de vérité
source/      les documents reçus : PDF de contrôle, extraction texte
qa/          les scripts de contrôle et leurs rapports archivés
figures/     les figures vectorielles (phase 4)
style/       le gabarit, les polices, les macros (phase 1)
build/       les sorties — jamais versionnées
```

## Commandes

```
make setup          installe la chaîne sur une machine vierge
make reconstituer   régénère src/*.md depuis le PDF de contrôle
make qa             contrôle d'intégrité et mesures typographiques
make aide           la liste complète
```

## Une particularité à connaître

Le fichier Markdown source d'origine n'existe plus. Le §2 du cahier prévoit ce
cas : sa reconstitution a été la première tâche du projet. Le manuscrit de
`src/` est donc reconstruit, et non retrouvé.

Il l'est à partir de deux sources croisées : l'extraction texte fournie par
l'auteure, qui donne la matière, et le PDF composé, qui donne la structure que
l'extraction a perdue — niveaux de titre, fins de paragraphe, encadrés,
italiques, tableaux, appels de notes. `make integrite` vérifie que le résultat
porte exactement les mêmes signes que l'extraction, aux dix-huit défauts près
que la reconstitution répare et qu'elle énumère.
