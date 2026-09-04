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

## Chaîne installée

`make setup` a été exécuté et vérifié : `lualatex`, `latexmk`, `memoir`,
`microtype`, `babel-french`, `pdfx`, `tikz`, `booktabs`, `fontspec`, `lineno`,
`poppler-utils`.

Les trois polices de labeur que le cahier met en concurrence sont disponibles
pour le spécimen de la phase 1 : **EB Garamond**, **Libertinus Serif** et
**Source Serif Pro** — cette dernière étant la version antérieure de Source
Serif 4, seule présente dans TeX Live ; l'écart entre les deux ne change rien à
un spécimen de comparaison.

Le conteneur de travail étant éphémère, `make setup` est à rejouer à chaque
session. C'est aussi ce qui vérifie, à chaque fois, le critère d'acceptation
« s'exécute sur une machine vierge ».

## Conventions du manuscrit

Validées avec l'auteure au chapitre 1. Elles valent pour les seize chapitres.

**Titres.** Le livre n'a que trois tailles de titre — 20,66 pt pour les parties,
14,35 pt pour les chapitres, 11,96 pt pour les sections. Il n'existe donc aucun
troisième niveau : `#` pour le chapitre, `##` pour la section, rien d'autre. Une
ligne de corps entièrement en gras est une attaque en gras dont la phrase passe
à la ligne, jamais un sous-titre.

**Parties.** Posées en commentaire en tête du premier chapitre de la partie :
`<!-- Deuxième partie — TROUVER ET VALIDER -->`. La phase 1 en fera un `\part`.

**Encadrés.** Le livre en compte trois familles que la composition ne distingue
pas — même cadre, même corps de 8,97 pt, même titre en gras. Le type est donc
noté ici, en phase 0, faute de quoi l'information serait définitivement perdue :

```
::: {.encadre type="realite-congolaise" titre="Réalité congolaise"}
::: {.encadre type="a-faire" titre="À faire cette semaine"}
::: {.encadre type="aparte" titre="Le piège des formules creuses"}
```

Décompte : 15 « Réalité congolaise », 15 « À faire cette semaine », 13 apartés.
Trois anomalies, vérifiées dans le PDF et fidèlement reportées : le chapitre 7
n'a pas de « Réalité congolaise », le chapitre 10 en a deux, le chapitre 11 n'a
ni l'une ni l'autre. L'audit les disait « constants » ; ils ne le sont pas.

**« Ce qu'il faut retenir »** est composé en titre de section et le reste : `##`.
Il revient dans les seize chapitres, sans exception, sous le même intitulé — la
phase 4 le retrouvera seule si elle décide d'en faire un encadré.

**Schémas.** Les trois schémas en art ASCII (pages 24, 27 et 114 du PDF) ne sont
pas reconstitués : l'extraction les rend en caractères invalides et les
redessiner au jugé reviendrait à inventer. Ils laissent un bloc
`::: {.todo-schema page="24"}` et attendent le contenu exact de l'auteure. Leur
état d'extraction est conservé à titre de preuve dans
`qa/schemas-a-reprendre.txt`, hors du manuscrit.

**Notes.** Les cinq appels de notes existent dans le texte, contrairement à ce
qu'affirme le point B7 de l'audit ; ils sont composés en exposant à 6,65 pt et
rendus `[^1]` à `[^5]`.

## Le double comptage

`make reconstituer` livre, pour chaque chapitre, le nombre de mots du Markdown
face au nombre de mots des lignes du PDF qui l'ont produit. Un écart significatif
signale un passage tombé — ce qu'une relecture ne rattrape pas.

Le comptage porte sur les lignes versées dans le chapitre, non sur ses pages :
une page porte souvent la fin d'un chapitre et le début du suivant, et la
compter deux fois masquerait précisément ce que le contrôle cherche.

Trois causes d'écart résiduel sont connues et attendues :

- les mots des schémas mis en attente, isolés dans leur propre colonne ;
- les quinze mots composés que l'extraction avait coupés en deux et que la
  reconstitution recolle (`écoutez-` + `le` comptent pour deux dans le PDF, pour
  un dans le Markdown) ;
- l'en-tête d'un tableau répété en tête de page, que la reconstitution ne garde
  qu'une fois.

Au-delà, tout écart demande une explication.

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
