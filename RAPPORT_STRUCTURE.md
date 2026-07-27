# RAPPORT — Structure et numérotation (prompt 2)

**Fichier de travail :** `Guide_Intelligence_Artificielle.md`
**Commits :** `fbd7db2` → `e792e44` (cinq groupes de corrections)
**Nature des modifications :** structurelles uniquement. Aucun intitulé n'a été reformulé, aucun paragraphe réécrit. Les seuls mots ajoutés au corps du texte sont les onze renvois corrigés du § 5.

---

## Correction préalable : il y a bien 24 chapitres

Mon diagnostic annonçait 25 chapitres et vous demandait d'arbitrer. **Cet arbitrage n'a plus lieu d'être : votre compte de 24 était le bon, et mon diagnostic se trompait deux fois, dans des sens opposés.**

1. **J'avais manqué un chapitre.** « Mener son propre grand projet » (partie IV) est structuré en sous-sections — « Pourquoi un projet d'envergure ? », « Les étapes d'un projet abouti » — et non en leçons. Mon détecteur, qui exigeait une « Leçon 1 » pour reconnaître un chapitre, l'avait ignoré.
2. **J'en avais compté deux de trop.** « Bibliothèque de prompts prêts à l'emploi » et « Recettes d'automatisation n8n pas à pas » sont bien des collections annexes, comme je le soupçonnais.

Votre propre tableau « Le chemin que nous allons suivre » le confirmait : il annonce quatre thèmes pour la partie IV — *« Éthique, conduite d'un projet, usages réels, mener son propre projet »*. Le compte tombe juste :

| Partie | Chapitres | Numéros |
|---|---:|---|
| I — Les fondations | 4 | 1 à 4 |
| II — Comment une machine apprend | 4 | 5 à 8 |
| III — Les grands domaines de l'IA | 5 | 9 à 13 |
| IV — Bien faire et bien décider | 4 | 14 à 17 |
| V — Les outils au quotidien | 7 | 18 à 24 |
| **Total** | **24** | |

---

## 1. Hiérarchie — 458 titres appliqués

Plus aucun titre structurel n'est en simple gras.

| Niveau | Nombre | Contenu |
|---|---:|---|
| `#` | 10 | 8 parties + 2 liminaires (avant-propos, plan de lecture) |
| `##` | 43 | 24 chapitres, 2 collections annexes, 4 projets (VI), 6 thèmes (VII), 7 sections (VIII) |
| `###` | 246 | 156 leçons, 25 « Exercices dirigés », 25 « Travaux pratiques », 18 étapes de projet, 14 problèmes, 8 sous-sections, 6 questions fréquentes |
| `####` | 40 | 25 encadrés « À VOUS DE JOUER », 8 sous-points a)/b)/c), 7 modèles de la bibliothèque de prompts |

**Deux décisions de mise en forme :**

- Les titres de partie tenaient sur deux lignes (`**PARTIE I**` puis `**Les fondations**`). Je les ai fusionnés en `# Partie I --- Les fondations`, ce qui donne un titre unique et exploitable par une table des matières.
- **Restent volontairement en gras**, car ce ne sont pas des titres : les 80 encadrés « L'ESSENTIEL À RETENIR », les quatre lignes de la page de titre et la signature finale.

**Les parties VI, VII et VIII n'ont ni chapitre ni leçon.** Elles s'organisent en projets, thèmes et sections libres. Je leur ai donné les mêmes niveaux (`##` / `###`) pour que la table des matières soit homogène, mais **elles restent hors de la numérotation des chapitres** : leur numéroter des chapitres aurait exigé de les restructurer, ce qui dépasse ce prompt.

---

## 2. Chapitres — numérotés de 1 à 24

Le préfixe `Chapitre N --- ` a été ajouté ; **les intitulés sont conservés mot pour mot.** La numérotation traverse les parties sans repartir à zéro.

| N° | Chapitre | Partie |
|---:|---|---|
| 1 | Introduction à l'intelligence artificielle | I |
| 2 | Programmation Python pour l'intelligence artificielle | I |
| 3 | Mathématiques pour l'intelligence artificielle | I |
| 4 | Fondamentaux de la Data Science et des statistiques | I |
| 5 | Apprentissage automatique supervisé et non supervisé | II |
| 6 | Réseaux de neurones et apprentissage profond | II |
| 7 | Ingénierie des données et MLOps | II |
| 8 | Statistiques avancées et modèles probabilistes | II |
| 9 | Traitement automatique du langage naturel (NLP) | III |
| 10 | IA générative et ingénierie des invites (prompting) | III |
| 11 | Vision par ordinateur | III |
| 12 | Apprentissage par renforcement | III |
| 13 | IA avancée : agents, protocole MCP, multimodalité et sûreté | III |
| 14 | Éthique, régulation et enjeux sociétaux de l'IA | IV |
| 15 | Gestion de projets d'intelligence artificielle | IV |
| 16 | Cas d'usage professionnels et applications sectorielles | IV |
| 17 | Mener son propre grand projet | IV |
| 18 | Maîtriser les assistants IA : ChatGPT, Claude, Perplexity | V |
| 19 | Ingénierie de prompts : l'art de bien formuler | V |
| 20 | Automatisation des tâches avec n8n | V |
| 21 | Intégrer l'IA dans une entreprise | V |
| 22 | IA pour la productivité et la création de contenu | V |
| 23 | Études de cas : l'automatisation IA par secteur | V |
| 24 | Créer ses propres assistants et anticiper l'avenir | V |

Non numérotées : « Bibliothèque de prompts prêts à l'emploi » et « Recettes d'automatisation n8n pas à pas ».

---

## 3. Leçons — quatre corrections, séquences continues partout

| Chapitre | Avant | Après |
|---|---|---|
| 12 — Apprentissage par renforcement | 1, 2, 3, **4bis** | 1, 2, 3, **4** |
| 15 — Gestion de projets | 1, 2, 3, **5, 6** | 1, 2, 3, **4, 5** |
| 20 — Automatisation avec n8n | 1…8, **9bis**, 10 | 1…8, **9**, 10 |

Détail des quatre renumérotations :

- **Leçon 4bis → Leçon 4** — « Applications et limites du renforcement »
- **Leçon 5 → Leçon 4** — « Les sept causes d'échec et comment les éviter »
- **Leçon 6 → Leçon 5** — « Communiquer avec les décideurs »
- **Leçon 9bis → Leçon 9** — « Comprendre les déclencheurs en profondeur »

Les 156 leçons sont vérifiées : séquence continue depuis 1 dans chacun des 23 chapitres qui en comportent, et dans les 2 collections annexes. **Plus aucun suffixe « bis » dans le document.**

---

## 4. Figures — seize numéros sur dix-sept ont changé

Schéma appliqué : `Figure <numéro de chapitre>.<numéro d'ordre>`, chaque chapitre repartant à `.1`.

| Image | Ancien | **Nouveau** | Chapitre |
|---|---|---|---|
| image1 | 1.1 | **1.1** | 1 — Introduction à l'IA * |
| image2 | 3.3 | **3.1** | 3 — Mathématiques |
| image3 | 2.2 | **5.1** | 5 — Apprentissage automatique * |
| image4 | 2.3 | **5.2** | 5 — Apprentissage automatique |
| image5 | 3.2 | **6.1** | 6 — Réseaux de neurones |
| image6 | 3.1 | **6.2** | 6 — Réseaux de neurones |
| image7 | 4.1 | **7.1** | 7 — Ingénierie des données et MLOps |
| image8 | 5.1 | **9.1** | 9 — NLP |
| image9 | 7.1 | **10.1** | 10 — IA générative |
| image10 | 6.1 | **11.1** | 11 — Vision par ordinateur |
| image11 | 8.1 | **12.1** | 12 — Apprentissage par renforcement |
| image12 | 9.1 | **13.1** | 13 — IA avancée |
| image13 | 9.2 | **13.2** | 13 — IA avancée |
| image14 | 10.2 | **18.1** | 18 — Assistants IA |
| image15 | 10.1 | **19.1** | 19 — Ingénierie de prompts |
| image16 | 11.1 | **20.1** | 20 — Automatisation n8n |
| image17 | 12.1 | **21.1** | 21 — Intégrer l'IA en entreprise |

`*` figure située dans l'**introduction de sa partie**, donc avant le titre du premier chapitre. Je l'ai rattachée au chapitre qu'elle introduit. Pour une correspondance stricte, il faudra déplacer ces deux images de quelques lignes, à l'intérieur du chapitre — je ne l'ai pas fait de ma propre initiative, cela déplace du contenu.

### Vérification des légendes : j'ai ouvert et regardé les 17 images

**Aucun décalage de contenu.** Chaque légende décrit bien l'image qui la précède. Rien à signaler de ce côté.

**En revanche, trois défauts sérieux que le diagnostic n'avait pas vus, parce qu'ils n'apparaissent qu'à l'œil :**

**a) Le numéro de figure est incrusté dans chaque image.** C'est le plus grave. Chaque PNG porte, en dur dans les pixels, un titre du type « Figure 3.3 — Descente de gradient vers le minimum de la fonction de coût ». La renumérotation que je viens de faire **désynchronise donc les légendes des images** : le lecteur verra « Figure 3.1 » sous une image où est écrit « Figure 3.3 ».

Ce n'est pas une régression que j'aurais introduite — c'était déjà faux avant, puisque la numérotation elle-même était incohérente. Mais cela signifie que **les 17 images doivent être régénérées**, ce qui rejoint la conclusion du diagnostic sur les 185 dpi. Ma recommandation : régénérer les schémas **sans aucun titre incrusté**, en laissant la légende Markdown seule porter le numéro. C'est la règle en édition : le numéro vit dans le texte, jamais dans l'image, précisément pour qu'une renumérotation reste possible.

**b) Cinq images portent deux titres différents.** Les images 12, 14, 15, 16 et 17 cumulent un titre « Figure X.Y — … » et un second titre en gras juste en dessous, puis la légende Markdown en fait un troisième. Exemple pour l'image 15 : *« Figure 10.1 — Structure d'un prompt professionnel »*, puis *« Les 5 composantes d'un prompt efficace »*, puis la légende *« Les cinq composantes d'un prompt professionnel. »* Trois formulations du même titre pour une seule figure.

**c) Trois images ont un défaut de rendu visible :**

| Image | Nouveau n° | Défaut |
|---|---|---|
| image17 | 21.1 | Les libellés (« Former, expérimenter », « Un projet ciblé, ROI mesurable », « Déploiement, MLOps, processus ») **débordent de leur barre** et chevauchent la barre voisine. Le schéma est illisible par endroits. |
| image6 | 6.2 | Les libellés « Couche cachée 1 » et « Couche cachée 2 » **se chevauchent** et se lisent « Couche cachée 1Couche cachée 2 ». |
| image7 | 7.1 | Les mots « Entraînement », « Surveillance », « Déploiement », « Validation » **débordent** de leurs cercles. |

**Un point de fond, hors périmètre de ce prompt :** l'image 18.1 (« Les grands assistants IA et leurs points forts ») présente **quatre** assistants — ChatGPT, Claude, Perplexity et **Gemini** — alors que le chapitre 18 s'intitule « Maîtriser les assistants IA : ChatGPT, Claude, Perplexity » et ne traite pas Gemini. L'image est en avance sur le texte. Cela recoupe le prompt 6, qui prévoit d'élargir ce panorama.

---

## 5. Renvois internes

### Ce que je n'ai pas eu à faire

**Le document ne contenait aucun renvoi numéroté.** J'ai cherché systématiquement toutes les formes de « chapitre N », « leçon N », « figure N.M », « partie N », « section N » : **zéro occurrence** dans le corps du texte. Les trois seules mentions du mot « chapitre » sont génériques (« à la fin de chaque chapitre »), et aucune ne cite de numéro.

C'est une chance : la renumérotation des chapitres, des leçons et des figures **ne pouvait donc casser aucun renvoi existant**. C'est aussi un symptôme — un manuel de 29 000 mots où aucun passage n'en cite un autre est un ouvrage dont les parties ne se parlent pas.

### Les onze renvois que j'ai corrigés

**Neuf références à des « Semestres » — le vestige le plus net du passé de fiche de cours.** Le manuel renvoie neuf fois à un « Semestre 2 » ou un « Semestre 3 » dont il n'existe **aucune trace** dans le livre : celui-ci est organisé en huit parties, pas en semestres. Je les ai redirigées vers les chapitres réels :

| Emplacement | Avant | Après |
|---|---|---|
| Ch. 1, leçon 7 — carte des sous-domaines | Apprentissage automatique *(Semestre 2)* | *(chapitre 5)* |
| Ch. 1, leçon 7 | Apprentissage profond *(Semestre 2)* | *(chapitre 6)* |
| Ch. 1, leçon 7 | Traitement du langage *(Semestre 3)* | *(chapitre 9)* |
| Ch. 1, leçon 7 | Vision par ordinateur *(Semestre 3)* | *(chapitre 11)* |
| Ch. 1, leçon 7 | Apprentissage par renforcement *(Semestre 3)* | *(chapitre 12)* |
| Ch. 1, leçon 7 | IA générative et agents *(Semestre 3)* | *(chapitres 10 et 13)* |
| Ch. 3, leçon 2 — ACP | « que vous reverrez au Semestre 2 » | « au chapitre 5 » |
| Ch. 3, encadré « Pont entre matières » | « Au Semestre 2, l'entraînement… » | « Au chapitre 6, … » |
| Ch. 5, leçon 1 — les trois façons d'apprendre | « (vu au Semestre 3) » | « (chapitre 12) » |

**Deux renvois de position remplacés par un numéro de figure :**

| Emplacement | Avant | Après |
|---|---|---|
| Ch. 5, leçon 1 | « trois grands paradigmes, illustrés **ci-dessus** » | « illustrés **à la figure 5.1** » |
| Ch. 20, leçon 4 | « Étudions un cas réel, illustré **ci-dessus** » | « illustré **à la figure 20.1** » |

Le premier méritait particulièrement d'être corrigé : la figure en question se trouve dans l'**introduction de la partie II**, au-dessus du titre du chapitre 5. Le « ci-dessus » franchissait donc une frontière de chapitre — et n'aurait plus rien voulu dire une fois le livre paginé.

### Les renvois que je n'ai pas résolus

**Un seul, et il est volontairement laissé en l'état :**

- **Chapitre 10, leçon 5** — « vous découvrirez les **agents** (que nous approfondirons un peu plus loin) ». Le renvoi vise vraisemblablement le chapitre 13 (« IA avancée : agents, protocole MCP… »), mais la formulation est trop vague pour que je tranche sans risque de vous prêter une intention. **Si vous confirmez, je le remplace par « (chapitre 13) ».**

Deux formulations voisines relèvent du registre plutôt que du renvoi, et attendent le prompt 3 :

- **Chapitre 1, leçon 7** — « Avant de plonger dans le détail **des cours suivants** […] que vous explorerez tout au long **du programme** ».
- **Chapitre 3, leçon 3** — « Gardez bien cette image en tête » : renvoi à l'illustration précédente, mais sans mention explicite de figure.

---

## 6. Contrôles effectués

| Contrôle | Résultat |
|---|---|
| Titres structurels restés en gras | **0** (hors les 80 encadrés, la page de titre et la signature, conservés à dessein) |
| Chapitres numérotés | 24, séquence 1→24 sans trou |
| Leçons en séquence continue | 25 ensembles vérifiés, **tous conformes** |
| Suffixes « bis » restants | **0** |
| Figures / images | 17 légendes pour 17 images, correspondance 1:1 |
| Renvois « Semestre » restants | **0** |
| Conversion pandoc → `.docx` | **OK** |
| Conversion pandoc → HTML | **OK** |
| Volume | 28 528 → 28 926 mots (**+398**, soit exactement les préfixes de titres ajoutés — aucun contenu perdu) |

---

## 7. Ce qui vous revient maintenant

**Une question ouverte, dont dépend la suite :**

Le renvoi vague du chapitre 10 (« que nous approfondirons un peu plus loin ») vise-t-il bien le chapitre 13 ? Un mot de votre part et je le rends explicite.

**Deux décisions à prendre avant le prompt 7 (mise en page finale) :**

1. **Les 17 images doivent être régénérées**, sans titre incrusté et à 300 dpi. C'est désormais bloquant : la renumérotation a désynchronisé les légendes des numéros gravés dans les images. Tant que ce n'est pas fait, le document ne peut pas partir à l'impression.
2. **Le sort des deux collections annexes** — « Bibliothèque de prompts » et « Recettes n8n ». Elles sont aujourd'hui au milieu de la partie V, non numérotées. Leur place logique est en fin d'ouvrage, dans la partie VIII. Je peux les y déplacer quand vous voudrez ; je ne l'ai pas fait, cela déplace du contenu.

**Un constat qui pèsera sur le prompt 4 :** aucun chapitre de ce manuel n'en cite un autre. Densifier les leçons sera l'occasion de créer ces liens — c'est ce qui distingue un livre d'une collection de fiches.
