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
| 1 | Gabarit typographique (césure, police, justification) | **faite** — D2 et D3 tranchées, ouvrage composé en 140 pages |
| 2 | Normalisation typographique du texte source | à venir |
| 3 | Appareil de notes | à venir |
| 4 | Figures et tableaux | à venir |
| 5 | Cohérence éditoriale | à venir |
| 6 | Liminaires et fin de volume | **entamée** — titre, droits et table des matières posés ; ISBN, dépôt légal et achevé d'imprimer restent en blanc |
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
make qa             intégrité, structure et mesures typographiques
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

## Phase 1 — ce que la mesure a établi

**La géométrie.** Les trois cibles du cahier — justification 100–105 mm, marges
20/15 mm, 60–66 signes — sont incompatibles en A5 : 148 − 20 − 15 rend 113 mm,
la justification actuelle. Le compte de signes étant le critère maître, la
géométrie retenue est 24 mm de gouttière et 19 mm en extérieure, soit 105 mm,
la gouttière restant plus large que l'extérieure.

**Le corps.** Il n'est pas réglé mais mesuré, par `qa/accorder-corps.py`, sur la
cible de 60 à 66 signes. Résultat : EB Garamond 12,75 pt, Libertinus 11,75 pt,
Source Serif Pro 10,75 pt — au-delà des 10,5 à 11 pt du cahier pour deux d'entre
elles. La raison tient à la police d'origine : DejaVu Serif est très large, les
polices de labeur sont étroites, et à corps égal elles logent bien plus de signes
sur la même mesure. Resserrer la justification retire des signes, changer de
police en ajoute, et le second effet l'emporte.

**Le taux de césure, abandonné et remplacé.** Le critère de sortie — 12 à 25 % —
n'est pas atteignable : 7 à 10 % sur un corpus de neuf chapitres. La cause est
mesurée, non supposée :

| réglage de `microtype` | taux de césure |
| --- | ---: |
| protrusion **et expansion** (ce que le cahier exige) | 7,2 % |
| protrusion seule (ce que XeLaTeX sait faire) | 15,5 % |
| aucun | 15,0 % |

L'expansion de caractères permet à TeX d'ajuster la chasse plutôt que de couper
les mots. Le critère de 12 à 25 % décrit donc une chaîne **sans** expansion,
c'est-à-dire celle que le cahier écarte. Les deux exigences de la phase 1
s'excluent.

Quatre mesures le remplacent, relevées par `qa/mesurer-composition.py` à chaque
composition — jamais une seule fois :

| mesure | seuil | corpus de neuf chapitres |
| --- | --- | --- |
| boîtes débordantes | zéro | **0** pour les trois polices |
| lignes de mauvaisité > 1000 | seuil annoncé, imposé à `\hbadness` | 1 à 2 sur ~1 070 |
| césures consécutives | deux au plus | **2** pour les trois |
| veuves et lignes creuses en tête | zéro | **0** |
| orphelines en pied | zéro | **0** |
| mot coupé en dernier mot de page | zéro | **0** |

Deux réglages ont été nécessaires pour y parvenir : `\clubpenalty` et
`\widowpenalty` à 10000, qui interdisent les veuves au lieu de les décourager,
et une réserve d'élasticité (`\emergencystretch`) qui laisse TeX relâcher un
paragraphe plutôt que de laisser une ligne déborder la mesure.

**La ponctuation haute.** De 38 lignes rejetées dans le fichier d'origine à une
seule, dont la cause est dans la source et non dans le gabarit : un guillemet
fermant précédé d'une espace ordinaire, au chapitre 15. C'est le travail de la
phase 2.

**Une fonte défectueuse écartée.** La graisse d'EB Garamond du paquet Debian ne
pèse que 43 Ko contre 422 pour la romaine : c'est un tronçon sans lettres
accentuées, qui composait « Ralit congolaise ». Celle de TeX Live est complète.

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

**Schémas.** Les trois schémas en art ASCII (pages 24, 27 et 114 du PDF) ne
viennent pas du PDF : deux d'entre eux y sont défectueux, et l'extraction rend
leurs traits de liaison en caractères invalides. Leur tracé est une donnée du
dépôt, arrêtée avec l'auteure, et vit dans `figures/schemas.txt` ; le manuscrit
les porte en blocs ```` ```schema page=24 ````, où l'alignement survit.

`qa/schemas-substitutions.txt` relève, pour chacun, ce que l'extraction portait
et ce que le manuscrit porte : c'est sur ce relevé que le contrôle d'intégrité
sait quels mots sont légitimement remplacés.

La règle B6 les destine à devenir des figures vectorielles en phase 4.
`figures/schemas.txt` en est la spécification. Le contrôle de structure vérifie
que chaque ligne tient dans la mesure — un bloc en chasse fixe qui déborde est
le défaut même de la page 27 qu'on corrige. Aucune ne déborde aujourd'hui ; deux
déborderont après la phase 1, qui resserre la justification, ce qui ôte tout
caractère facultatif au passage en vectoriel.

**Notes.** Les cinq appels de notes existent dans le texte, contrairement à ce
qu'affirme le point B7 de l'audit ; ils sont composés en exposant à 6,65 pt et
rendus `[^1]` à `[^5]`.

## Les trois contrôles

`make qa` en enchaîne trois, tous rejouables et archivés dans `qa/`.

**Intégrité** (`verifier-integrite.py`) compte les signes : il prouve qu'aucun
mot de l'auteure n'est perdu ni inventé. Verdict actuel : *aucun signe perdu ni
ajouté*.

**Structure** (`verifier-structure.py`) compte les éléments : sections,
paragraphes, items, encadrés, tableaux, notes, schémas — ce que le PDF porte
face à ce que le Markdown en a fait. C'est le contrôle qui manquait, et il
importe : les défauts les plus coûteux ne perdent aucun mot. Un titre fabriqué
au milieu d'une phrase en gras, deux paragraphes soudés à un saut de page, une
cellule de tableau versée dans la mauvaise colonne — l'intégrité les laisse
passer, une relecture les rate une fois sur deux. Verdict actuel : *conforme*.

**Mesures** (`mesure-typo.py`) relève la césure, la ponctuation haute rejetée et
le gabarit sur le PDF composé. Il servira de juge aux critères de sortie
chiffrés de la phase 1.

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
