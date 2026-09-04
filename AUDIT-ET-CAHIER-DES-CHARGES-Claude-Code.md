# « ENTREPRENDRE AU CONGO »

**Audit technique du PDF, cahier des charges de fabrication et prompt Claude Code**

> Document de travail — remplace la version précédente. Audit réalisé le 4 septembre 2026
> sur le fichier `ENTREPRENDRE-AU-CONGO.pdf` (144 pages, produit le 1er septembre 2026 par
> pandoc + XeLaTeX).
>
> Transcription fidèle du PDF source `AUDIT-ET-CAHIER-DES-CHARGES-Claude-Code.pdf`, versionnée
> ici pour faire autorité. En cas de divergence, le PDF fait foi.

---

# PARTIE I — AUDIT DU FICHIER EXISTANT

Constats mesurés, pas d'appréciation subjective. Chaque point est vérifiable.

## A. Ce qui est déjà bon — et qu'il ne faut pas casser

| Point | État |
| --- | --- |
| Format | A5 exact, 148 × 210 mm ✅ |
| Pagination totale | 144 pages, multiple de 4 ✅ (contrainte d'imposition satisfaite) |
| Ouverture des chapitres | 29 ouvertures sur 29 en page impaire (recto) ✅ |
| Gouttière | 20,5 mm en marge intérieure contre 14,7 mm en extérieure ✅ (le bon sens, souvent inversé par erreur) |
| Apostrophes | 1 356 apostrophes typographiques ’, aucune apostrophe droite ✅ |
| Guillemets | 63 paires de guillemets français « », aucun guillemet droit ✅ |
| Tirets | 256 cadratins — correctement employés ✅ |
| Points de suspension | caractère … unique, aucun `...` ✅ |
| Polices | toutes incorporées et sous-ensemblées ✅ |
| Structure | 8 parties, 16 chapitres, encadrés « Réalité congolaise » et « À faire cette semaine » constants ✅ |
| Tableaux | filets de type booktabs, sans filets verticaux ✅ (c'est le bon usage) |

Le manuscrit est en meilleur état que ne le laissait supposer la demande. Le travail restant est
de **fabrication**, pas de reprise éditoriale de fond.

## B. Défauts bloquants pour une publication professionnelle

### B1 — La césure française est désactivée. C'est le défaut n° 1.

**Mesure :** sur 2 163 lignes pleines, 15 se terminent par un tiret de césure, soit **0,7 %**.
Un livre français justifié en A5 se situe entre 15 % et 25 %.

Conséquence directe, visible sur chaque page : le texte est justifié en écartant les mots, ce qui
produit des blancs béants et des lézardes verticales. Exemple relevé page 98 :
« prélevé est un argent qui ne devient jamais une machine, ». C'est le signe qui distingue
immédiatement, à l'œil, un document imprimé d'un livre composé.

**Cause probable :** `babel-french` absent ou motifs de césure français non chargés.

### B2 — La police de texte est DejaVu Serif.

C'est la police de repli par défaut de la chaîne pandoc/XeLaTeX. Elle n'a pas été choisie.
DejaVu Serif est dessinée pour l'écran : hauteur d'œil très grande, chasse large, graisse
soutenue, pas de jeu de petites capitales ni de chiffres elzéviriens. Aucun livre du commerce
n'est composé dans cette police. À remplacer par une véritable police de labeur libre de droits :
**EB Garamond, Libertinus Serif, Crimson Pro ou Source Serif 4**.

### B3 — Justification trop large pour le corps employé.

**Mesure :** justification de 112,8 mm pour un corps de 9,96 pt, soit environ 68 à 72 signes par
ligne. L'optimum de lisibilité en labeur se situe entre 60 et 66 signes. Combiné à B1, c'est ce
qui produit les blancs.

### B4 — Marges de tête et de pied trop faibles.

**Mesure :** tête 11,9 mm, pied 12,3 mm. Pour un A5, l'usage est de 15 à 18 mm en tête et de
18 à 22 mm en pied, le pied devant être plus grand que la tête (centrage optique). Ici les deux
sont quasi égaux et tous deux insuffisants : le bloc de texte paraît collé aux bords et l'ouvrage
ressemble à un rapport.

### B5 — L'espace insécable avant la ponctuation haute n'est pas appliquée.

**Mesure :** 32 cas où un `;` `:` `!` `?` ou `»` est rejeté en début de ligne, séparé du mot
qu'il suit. Exemple relevé dans l'introduction : « l'absence d'enregistrement comptable, même
élémentaire » suivi du `;` seul à la ligne suivante.

### B6 — Les schémas sont de l'art ASCII en chasse fixe.

Trois occurrences (pages PDF 24, 27 et 114). Rendu réel, page 106 imprimée :

```
ARGENT  →  ACHAT DE STOCK  →  VENTE  →  CRÉANCE CLIENT  →  ARGENT
   ↑
        paiement des fournisseurs ←
```

composé en Latin Modern Mono, débordant sur la marge de droite, flèches non alignées, sans
cadre ni légende. Sur papier, cela se lit comme un défaut de composition, pas comme une
illustration. Le parti pris arrêté pour le livre — schémas explicatifs vectoriels, sans personnages
décoratifs — n'est à ce jour pas mis en œuvre du tout : le fichier ne contient aucun objet image
et aucun tracé vectoriel.

### B7 — Les notes de sources n'ont aucun appel dans le texte.

La section « Notes et sources » (page 135) contient cinq notes numérotées. Mais le texte ne
comporte aucun appel de note : le mot « SMART » page 61, le passage sur l'initiative
personnelle page 17, la mention de la contagion émotionnelle — aucun n'est marqué. Le lecteur
n'a donc aucun moyen de savoir à quel passage se rattache la note 2. C'est précisément la
garantie anti-plagiat demandée, et elle est aujourd'hui à moitié posée : l'intention est là, le
dispositif ne fonctionne pas.

Sur le fond, l'inquiétude que j'avais formulée sur l'attribution des sources est partiellement
levée : la note 2 reconnaît explicitement que le cadre de l'initiative personnelle est issu de la
recherche et des programmes de formation entrepreneuriale en Afrique subsaharienne, et qu'il est
reformulé ici. C'est le bon réflexe. Elle reste toutefois trop générique pour valoir attribution :
aucun auteur, aucun programme, aucune référence bibliographique n'est nommé. Une note qui ne
permet pas de remonter à la source ne protège de rien. Idem pour la note 3 (« travaux de
recherche sur le sujet », sans plus).

### B8 — Le fichier n'est pas conforme aux exigences prépresse.

- PDF 1.5, aucun flux de métadonnées XMP → non conforme PDF/X, que plusieurs imprimeurs exigent ;
- format de page égal au format fini → aucun fond perdu, aucun trait de coupe ;
- document non balisé (`Tagged: no`) → sans incidence pour le papier, bloquant pour
  l'accessibilité de la version numérique.

### B9 — La page de copyright est incomplète.

Il manque l'ISBN, la mention de dépôt légal, le nom de l'éditeur ou la mention d'auto-édition, et
l'achevé d'imprimer. En l'état, le livre n'est pas diffusable en librairie ni référençable.

### B10 — Tableaux et figures non numérotés ni légendés.

Aucun n'est appelé dans le texte sous la forme « voir tableau 3 ». Il est donc impossible de
produire une table des illustrations, et un renvoi ne peut se faire que par la page — ce qui casse
à la première recomposition.

## C. Erreurs de langue relevées à la lecture

Cette liste n'est pas exhaustive : elle est le produit d'une lecture partielle. Elle sert à établir
qu'une relecture complète est nécessaire, pas à la remplacer.

**Introduction, page 2 :** « Ces défaillances ont une caractéristique commune : elles relèvent de
connaissances techniques qui s'acquièrent, et leur absence n'est pas imputable aux entrepreneurs
eux-mêmes. Elle procède d'un déficit de formation à la gestion […] » → « Elle » n'a pas
d'antécédent au singulier. Lire : « Elle procède » se rapporte à « leur absence », mais la phrase
précédente s'est déplacée au pluriel. À reformuler : « Cette absence procède d'un déficit de
formation… »

## D. Conclusion de l'audit

Le contenu est prêt. Le problème est entièrement typographique et prépresse. Aucune des
corrections ci-dessus ne touche au texte, à l'exception de C et de B7. C'est une bonne nouvelle :
ce sont les corrections les plus rapides à obtenir et les plus faciles à contrôler.

Deux réserves de fond demeurent, inchangées :

1. **Attribution des sources** — à durcir (B7). Il ne s'agit plus d'un risque majeur, mais d'un
   travail de précision à faire une fois.
2. **Cession de droits** — le livre paraît sous la signature de Ruth ZADI PUKUTA. Si la rédaction
   et la fabrication sont assurées par une autre personne, un écrit signé fixant qui détient les
   droits patrimoniaux, qui perçoit les recettes et qui répond du contenu doit exister avant
   publication. C'est le point qui, en pratique, se règle mal après coup.

---

# PARTIE II — CAHIER DES CHARGES DE FABRICATION

## 1. Objectif

Produire, à partir des sources, une **chaîne reproductible et versionnée** qui régénère en une
commande :

1. `interieur.pdf` — A5, prêt pour l'impression, conforme PDF/X, polices incorporées, fonds
   perdus 3 mm et traits de coupe ;
2. `couverture.pdf` — plat 1 + dos + plat 4, dos calculé sur la pagination finale et le grammage
   réel du papier ;
3. `livre.epub` — validé par epubcheck, zéro erreur ;
4. `relecture.pdf` — A4, interligne double, lignes numérotées, pour le relecteur humain ;
5. `qa/rapport-final.md` — un contrôle par ligne, horodaté.

## 2. Source de vérité

Le fichier Markdown `ENTREPRENDRE-AU-CONGO.md`, **jamais le PDF**. Le PDF ne sert que de document
de contrôle. Si le `.md` n'est plus disponible, sa reconstitution est la première tâche du projet.

## 3. Chaîne technique

**LuaLaTeX + classe `memoir`.** Justification : c'est la seule combinaison qui apporte à la fois
la césure et la typographie françaises complètes (`babel-french`), la microtypographie intégrale
(`microtype` avec protrusion et expansion de caractères — XeLaTeX ne fait que la protrusion), la
maîtrise fine du gabarit, et la sortie PDF/X via `pdfx`. Les défauts B1, B2, B3 et B5 relevés
ci-dessus se corrigent tous dans cette chaîne, et seulement dans une chaîne de ce type.

**Alternative acceptable** si la vitesse d'itération prime : **Typst**. Compilation instantanée,
syntaxe lisible. En contrepartie, la conformité PDF/X y est moins établie.

**À proscrire :** toute chaîne fondée sur un traitement de texte — pas de versionnement, pas de
reproductibilité, pas de contrôle automatisé.

## 4. Arborescence

```
entreprendre-au-congo/
├── src/00-liminaires/ … 09-annexes/   # un fichier par chapitre
├── figures/                            # schémas vectoriels
├── style/                              # gabarit, polices, macros
├── build/                              # sorties, non versionné
├── qa/                                 # scripts et rapports
├── glossaire.yml
├── Makefile                            # make livre | epub | qa | tout
└── README.md
```

Dépôt Git, un commit par phase, aucun binaire de sortie versionné.

## 5. Phases

Séquentielles. Chaque phase se termine par un **point d'arrêt** : rapport présenté, validation
attendue. **Interdiction d'enchaîner.**

### Phase 0 — Mise en place

Dépôt, arborescence, Makefile. Découpage du manuscrit par chapitre. Contrôle par différentiel
automatique que la recomposition restitue le manuscrit **au caractère près**.

### Phase 1 — Correction du gabarit typographique

C'est la phase qui règle B1 à B5. Cible :

- police de labeur : EB Garamond, Libertinus Serif ou Source Serif 4 — **jamais DejaVu** ;
- corps 10,5 à 11 pt selon la police retenue, interlignage 14 à 15 pt ;
- justification ramenée à 100–105 mm, soit 60 à 66 signes par ligne ;
- marges : gouttière 20 mm, extérieure 15 mm, tête 16 mm, pied 20 mm ;
- `babel-french` chargé, motifs de césure français actifs ;
- `microtype` actif, protrusion et expansion ;
- pénalités de césure réglées : pas plus de trois césures consécutives, pas de césure en dernière
  ligne de paragraphe, pas de césure d'une ligne à l'autre d'un recto à un verso.

**Critère de sortie mesurable :** taux de césure entre 12 % et 25 %, et zéro ponctuation haute
rejetée en début de ligne. Le rapport de phase doit donner ces deux chiffres.

### Phase 2 — Normalisation typographique du texte source

Application par script versionné, sortie archivée :

- espace fine insécable avant `;` `!` `?`, espace insécable avant `:` ;
- guillemets « » avec insécables intérieures ; “ ” en second niveau seulement ;
- capitales accentuées obligatoires ;
- insécables dans les nombres, unités, dates, après les abréviations de civilité, entre l'initiale
  et le nom ;
- cadratin — pour les incises, demi-cadratin – pour les intervalles, trait d'union pour la
  composition ;
- italique pour les titres d'ouvrages et les mots étrangers non francisés ;
- normalisation de l'écriture des sommes et du symbole monétaire.

### Phase 3 — Appareil de notes (règle B7)

- poser un appel de note dans le texte pour chacune des cinq notes existantes, au passage exact
  concerné ;
- compléter chaque note par une référence permettant de remonter à la source : auteur, titre,
  année, ou nom du programme de formation. Une note qui ne nomme rien ne protège de rien ;
- relire l'ensemble du manuscrit et signaler tout autre passage reprenant un outil, une grille, une
  matrice ou un acronyme qui appellerait une note ;
- contrôle automatique : chaque appel a sa note, chaque note a son appel.

### Phase 4 — Figures et tableaux (règles B6, B10)

- reprendre les trois schémas ASCII en vectoriel (TikZ), avec cadre, titre et légende ;
- charte unique : même palette, même graisse de trait, même police que le texte ;
- impression prévue en **noir et blanc** : différenciation par la valeur de gris, la trame et
  l'étiquetage, **jamais par la couleur seule** ;
- numéroter et légender chaque tableau et chaque figure, les appeler dans le texte, produire une
  table des illustrations ;
- typer les encadrés récurrents et les rendre constants d'un bout à l'autre (« Réalité congolaise »,
  « À faire cette semaine », « Ce qu'il faut retenir »).

### Phase 5 — Cohérence éditoriale

`glossaire.yml` figeant : entrepreneur / porteur de projet, client / consommateur, plan d'affaires /
business plan, développement des sigles à la première occurrence, majuscules des institutions,
forme des titres. Application puis contrôle par script.

### Phase 6 — Liminaires et fin de volume

Compléter la page de copyright (règle B9) : ISBN, dépôt légal, éditeur ou mention d'auto-édition,
achevé d'imprimer. Vérifier la table des matières régénérée. **Conserver impérativement la section
« Limites de l'ouvrage ».**

### Phase 7 — Composition et contrôle de mise en page

- chapitres ouvrant en page impaire (déjà acquis, à préserver) ;
- titres courants : ouvrage en page paire, chapitre en page impaire ; aucun sur les pages
  d'ouverture ni sur les pages blanches ;
- folios romains pour les liminaires, arabes ensuite ; aucun sur les pages blanches ;
- zéro ligne veuve, zéro ligne orpheline, zéro ligne creuse en tête de page ;
- aucun encadré gris ne doit se terminer à moins de 15 mm du pied de page ;
- pagination finale multiple de 4.

### Phase 8 — Contrôle qualité automatisé (`make qa`)

Scripts déterministes, rapport archivé :

- LanguageTool profil français, sortie en liste, **aucune correction silencieuse** ;
- taux de césure, ponctuation haute rejetée, doubles espaces, espaces finales ;
- intégrité des renvois internes, de la numérotation, des appels de notes ;
- présence de toutes les figures appelées ;
- contrôle PDF : polices incorporées, aucune image sous 300 ppp, texte en noir 100 % K, XMP
  présent, fonds perdus présents ;
- veuves, orphelines, lignes creuses ;
- pagination multiple de 4 ; comptage des signes et des pages.

### Phase 9 — Livrables

Les cinq fichiers du point 1. Le dos de couverture ne se calcule qu'**après la phase 7**, et sa
valeur doit être **demandée à l'imprimeur** en fonction du grammage réel — jamais estimée.

## 6. Interdictions

1. **Ne rien inventer.** Aucun chiffre sur l'économie congolaise, aucun taux, aucune référence
   légale sans source vérifiable. En cas de doute : marquer `[À VÉRIFIER]` et consigner. Un chiffre
   plausible mais faux, une fois imprimé, ne se corrige plus.
2. **Ne pas réécrire le fond sans autorisation.** La forme se corrige seule ; le sens, l'argument et
   la position de l'auteure passent par validation.
3. **Ne pas lisser le style.** Le ton est direct et incarné : ni emphase commerciale, ni tournure
   administrative.
4. **Ne pas enchaîner les phases.**
5. **Ne pas supprimer la section « Limites de l'ouvrage ».**
6. **Ne pas produire de couverture définitive sans la pagination finale.**

## 7. Critères d'acceptation

- `make tout` s'exécute sans erreur sur une machine vierge ;
- taux de césure entre 12 % et 25 % ; zéro ponctuation haute rejetée ;
- `qa/rapport-final.md` sans ligne en échec ;
- epubcheck : zéro erreur ;
- toute marque `[À VÉRIFIER]` levée ou assumée par écrit ;
- chaque note a son appel et nomme une source identifiable ;
- relecture humaine complète effectuée sur `relecture.pdf` et intégrée ;
- ISBN et dépôt légal présents sur la page de copyright.

## 8. Ce qu'aucune chaîne automatisée ne fera à votre place

- Une **relecture humaine sur épreuve**, par quelqu'un qui n'a pas écrit le texte. Non négociable,
  à budgéter.
- **ISBN** (un par format : broché, numérique) et **dépôt légal** en RDC.
- **Code-barres EAN-13** dérivé de l'ISBN, en quatrième de couverture.
- **Cession de droits** écrite entre l'auteure signataire et le rédacteur.
- **Décision sur la quatrième de couverture** : l'absence de traitement de la formalisation et de
  la fiscalité doit y être annoncée. C'est la première attente d'un lecteur devant un livre intitulé
  « Entreprendre au Congo », et mieux vaut la désamorcer que la subir en critique.

---

# PARTIE III — PROMPT À COLLER DANS CLAUDE CODE

> Tu interviens comme **directeur de fabrication éditoriale** sur un livre destiné à l'impression et
> à la diffusion commerciale.
>
> **Le livre :** « Entreprendre au Congo — Comprendre l'entrepreneuriat et savoir par où commencer »,
> de Ruth ZADI PUKUTA. 8 parties, 16 chapitres, environ 25 500 mots, en français. Lectorat :
> porteurs de projets, entrepreneurs en activité, étudiants et formateurs, en République
> démocratique du Congo.
>
> **L'état des lieux :** une version PDF de 144 pages existe déjà, produite par pandoc + XeLaTeX.
> Le contenu est prêt. Le problème est entièrement typographique et prépresse. Un audit mesuré a été
> réalisé : il figure dans le fichier `AUDIT-ET-CAHIER-DES-CHARGES-Claude-Code.md`, partie I.
> Lis-le intégralement, ainsi que le cahier des charges en partie II, avant toute action. Ce
> document fait autorité sur tout ce que je pourrais dire de façon plus vague par la suite.
>
> **Les quatre défauts qui commandent le projet**, tous mesurés :
>
> 1. la césure française est désactivée — 0,7 % de lignes césurées contre 15 à 25 % attendus, d'où
>    des blancs de justification sur chaque page ;
> 2. la police de texte est DejaVu Serif, police de repli non choisie, impropre au labeur imprimé ;
> 3. l'espace insécable avant la ponctuation haute n'est pas appliquée — 32 cas de `;` `:` `?`
>    rejetés en début de ligne ;
> 4. les schémas sont de l'art ASCII en chasse fixe et débordent la justification ; le fichier ne
>    contient aucun élément vectoriel.
>
> **Contraintes non négociables :**
>
> 1. Tu travailles par phases, dans l'ordre du cahier des charges. À la fin de chaque phase tu
>    t'arrêtes, tu présentes ton rapport et tu attends ma validation. Tu n'enchaînes jamais deux
>    phases de ta propre initiative.
> 2. Tu travailles depuis le fichier Markdown source, jamais depuis le PDF. Le PDF n'est qu'un
>    document de contrôle.
> 3. Tu n'inventes aucune donnée factuelle, aucun chiffre, aucune référence juridique. Tout élément
>    non vérifiable est marqué `[À VÉRIFIER]` dans le texte et consigné dans le rapport de phase.
> 4. Tu distingues strictement la **correction de forme**, que tu appliques, de la **modification de
>    fond**, que tu proposes et qui attend ma décision.
> 5. Toute correction automatique passe par un script versionné dans `qa/`, dont la sortie est
>    archivée. Je dois pouvoir rejouer et auditer chaque transformation.
> 6. Tu ne lisses pas le style. Le ton doit rester direct et incarné.
>
> **Commence par la phase 0** (mise en place et contrôle d'intégrité), **puis la phase 1**
> (correction du gabarit typographique). La phase 1 a deux critères de sortie chiffrés que ton
> rapport devra donner : taux de césure entre 12 % et 25 %, et zéro ponctuation haute rejetée en
> début de ligne.
>
> Avant de commencer, dis-moi : quels fichiers te manquent, quelles décisions tu attends de moi, et
> quels points du cahier des charges te paraissent insuffisamment spécifiés.
