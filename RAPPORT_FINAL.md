# RAPPORT FINAL — Reconstruction du document publiable (prompt 7)

Ce rapport clôt les sept phases de la procédure. Il donne les chiffres avant et
après, décrit la chaîne de fabrication, énumère les défauts que le contrôle
visuel a révélés et corrigés, et se termine par la liste — la partie la plus
importante pour vous — de ce que je n'ai **pas** pu vérifier et qui exige votre
relecture.

---

## 1. Le manuel en chiffres

| | Au départ | **Aujourd'hui** | |
|---|---:|---:|---|
| Mots dans l'ouvrage | 29 304 | **89 490** | ×3,1 |
| Mots, code compris | 29 304 | **93 757** | ×3,2 |
| Parties | 8 | **8** | inchangé |
| Chapitres | 24 | **24** | inchangé |
| Leçons | 156 | **158** | +2 |
| Médiane de mots par leçon de chapitre | 91 | **379** | ×4,2 |
| Leçons de chapitre sous 200 mots | 122 sur 146 | **0** | |
| Exemples chiffrés déroulés en entier | 0 | **19** | au moins un par chapitre |
| Exercices dirigés de fin de chapitre | 82 | **82** | inchangé |
| Travaux pratiques « À vous de jouer » | 25 | **25** | inchangé |
| Problèmes gradués (partie VII) | 14 | **64** | ×4,6, sur 3 niveaux |
| Corrigés | 14 | **64** | tous en annexe A |
| Extraits de code dans le texte | 5, illisibles | **39** | dont 30 en Python |
| Scripts exécutables livrés | 0 | **4** | 41 ko, dans `code/` |
| Figures | 17 | **17** | inchangé |
| Pages du PDF final | — | **278** | A4, corps 11 pt, noir et blanc |

**Leçons étendues : les 146 leçons de chapitre, sans exception.** Aucune n'a été
réécrite : tout a été **ajouté autour** de votre texte. Vos phrases, vos
exemples et votre voix sont intacts — `git diff` sur les commits de
densification ne montre aucune ligne d'origine en suppression.

**Répartition des 64 problèmes** : 16 de niveau 1 (vérifier), 35 de niveau 2
(appliquer, souvent chiffré), 13 de niveau 3 (raisonner, sans réponse unique).
Vérification automatique du dernier état : 64 énoncés, 64 corrigés, 64 renvois,
aucun orphelin d'un côté ni de l'autre.

**Les 30 blocs Python sont analysés syntaxiquement à chaque compilation** ; les
30 passent. Les 4 scripts de `code/` s'exécutent réellement, résultats et
limites consignés dans `code/VERIFICATION.md`.

---

## 2. La chaîne de fabrication

Tout se rejoue avec une commande. Rien n'est fait à la main.

```bash
./build.sh              # le .docx seul
./build.sh --pdf        # + le PDF, table des matières calculée
./build.sh --controle   # + la rastérisation de chaque page
```

| Fichier | Rôle |
|---|---|
| `Guide_Intelligence_Artificielle.md` | la source, seul fichier à éditer |
| `outils/faire_reference_docx.py` | fabrique le gabarit de styles |
| `outils/reference.docx` | le gabarit (reconstruit dès que son générateur change) |
| `outils/finitions_docx.py` | réglages de pagination impossibles en Markdown |
| `outils/exporter_pdf.py` | export PDF avec calcul des champs |
| `outils/images_nb.py` | tirage noir et blanc des figures (non appliqué) |
| `outils/pdf_protege.py` | exemplaire de relecture chiffré, sans impression ni copie |
| `outils/controle_visuel.py` | analyse de mise en page + images des pages |
| `build.sh` | orchestre le tout et vérifie le résultat |

**Le gabarit.** Sobre et universitaire : titres en **Cambria** (serif), corps
en **Calibri** (sans serif), code en **Consolas**. **Aucune couleur** — voir la
section 4 pour le détail du parti pris typographique. Corps justifié à 11 pt,
interligne 1,15, format A4 avec une marge intérieure plus large (3 cm) pour la
reliure.

**Contrôles automatiques à chaque compilation**, la construction échoue si l'un
tombe : pied de page présent, champ de table des matières présent, au moins deux
sections, exactement 17 images embarquées, style de code défini, niveaux de
titres 1 à 3 définis.

**Pagination.** Vérifiée sur le PDF : les 18 pages liminaires (titre, page de
droits, avant-propos, plan, table des matières) ne portent **aucun numéro** ; le
corps commence à la page 19 du PDF avec le folio « 1 » et court jusqu’à « 260 ».
Deux sections `sectPr` distinctes, la seconde avec `pgNumType w:start="1"`.

**Ordre de fin vérifié**, conforme à votre demande : Annexe A — Corrigés,
Annexe B — Glossaire, Annexe C — Bibliographie, Annexe D — Index des figures.

---

## 3. Contrôle visuel : ce que j'ai trouvé et corrigé

Les 278 pages ont été converties en images et analysées ; j'en ai regardé une
quinzaine en détail, choisies pour être représentatives (page de titre, page de
droits, table des matières, ouverture de partie, page de code, page de tableau,
page de figure, et chacune des pages signalées).

### Défauts corrigés

**a) Quatre titres d'encadré orphelins.** « L'ESSENTIEL À RETENIR » restait seul
en bas des pages 88, 98, 114 et 212, son contenu passant à la page suivante.
Pandoc ne sait pas exprimer `keepNext` depuis le Markdown : `finitions_docx.py`
le pose désormais sur les 187 intitulés d'encadré du livre. Il n'en reste
**aucun**.

**b) Un tableau coupé au mauvais endroit.** Dans le glossaire, la ligne
« Workflow » était scindée entre deux pages : la page 268 ne portait que
l'en-tête répété et le mot « déclencheur. ». `cantSplit` est maintenant posé sur
les 235 lignes de tableau de l'ouvrage.

**c) Une légende séparée de sa figure.** La figure 20.1 se trouvait en bas de la
page 175, sa légende en haut de la 176. Les 17 paragraphes d'image portent
désormais `keepNext` : image et légende sont solidaires.

**d) Numérotation continue des travaux pratiques.** Les listes des 25 « À vous de
jouer » se suivaient d'un bout à l'autre du livre — le dernier exercice du
chapitre 24 portait le numéro **110**. Chacune des 24 listes concernées repart
maintenant de 1.

**e) Les cinq extraits de code hérités du .docx.** Ils étaient restés en texte
échappé avec des retours forcés, et **l'indentation Python avait disparu** : le
code imprimé dans le manuel était syntaxiquement faux. Les cinq sont
reconstruits en blocs composés (`python`, `sql`) et l'indentation est rétablie.
Les 7 modèles de la bibliothèque de prompts subissaient le même sort ; ils sont
désormais en blocs `text`.

**f) Marqueurs de gras échappés visibles.** Quatre `\*\*` s'affichaient
littéralement dans le texte imprimé (« une étape de \*\*validation humaine\*\* »,
chapitre 20). Convertis en gras réel.

**g) « A\* » affiché avec une barre oblique.** L'algorithme A\* apparaissait
`A\*` sur 11 occurrences des chapitres 1 et 2 — la barre était visible à
l'impression. Normalisé.

**h) Un astérisque orphelin** dans le corrigé 9.1 et une référence
bibliographique (*FAT\**) dont l'italique ne s'ouvrait pas.

**i) Soixante corrigés au mauvais endroit — le plus sérieux.** Au prompt 5 les
corrigés avaient été rassemblés en partie VIII ; au prompt 7 seuls les corrigés
du thème 1 avaient rejoint l'annexe A. Les **60 autres (1.5 à 10.7) étaient
restés en partie VIII**, sous cinq titres résiduels (« Thème 2 — Mathématiques de
l'apprentissage » suivi des corrigés 1.5 et 1.6, etc.) qui ne correspondaient
plus à leur contenu. Les dix sections sont maintenant regroupées dans l'annexe A
dans l'ordre, les titres parasites ont disparu, et la vérification 64/64 est
verte. **Je vous le signale explicitement : ce défaut venait d'une phase
antérieure que j'avais déclarée terminée.**

### Ce que le contrôle signale encore, et qui est normal

Dix-neuf pages sont remplies à moins de 12 %. Je les ai toutes examinées : ce
sont la page de titre, la page de droits, la dernière page de la table des
matières, les six pages d'ouverture de partie (le style Titre 1 force un saut de
page, c'est voulu) et les fins de section qui précèdent un saut de page de
chapitre — notamment celles des dix thèmes de problèmes, dont le dernier énoncé
déborde d'une page. **Aucun trou de mise en page.**

### Défauts constatés que je n'ai pas corrigés

**Les 17 images — le point bloquant, inchangé depuis le prompt 2.** Le contrôle
visuel le rend maintenant incontestable. Page 70, l'image porte dans ses pixels
« Figure 3.1 — Architecture d'un perceptron multicouche » tandis que la légende
imprimée dessous annonce « Figure 6.2 — Un réseau dense ». Page 176, l'image dit
« Figure 11.1 — Chaîne de nœuds » et la légende « Figure 20.1 — Un workflow
type ». Le lecteur voit donc **deux numéros et deux titres différents pour la
même figure**, seize fois sur dix-sept. S'y ajoute, sur cette même image de la
page 70, un chevauchement de libellés (« Couche cachée 1Couche cachée 2 »).
Aucune intervention sur le Markdown ne peut y remédier : le texte est dans les
pixels. La table de correspondance ancien numéro → nouveau numéro est dans
`RAPPORT_STRUCTURE.md`, section 4. Les images doivent être régénérées hors de ce
dépôt, sans titre incrusté et à 300 dpi (elles sont à 185 dpi de moyenne).

**Une table des matières de 18 pages.** Elle descend au niveau 3, ce qui est
juste pour les 158 leçons, mais liste aussi les 64 « Problème 1.1… 10.7 » : cinq
pages de renvois qui pointent tous vers cinq pages du livre. Deux options, à
vous de trancher : réduire la table au niveau 2 (elle tombe à ~4 pages mais perd
les leçons), ou sortir les seuls énoncés de problème de la table (elle tombe à
~13 pages et garde les leçons). Je n'ai pas décidé à votre place.

**Quatorze lignes de code dépassent de 3 à 8 points la marge droite**, sur
11 pages. C'est de l'ordre du filet d'un millimètre, invisible à la lecture
courante ; le seul cas un peu visible est le JSON de la page 231. Corriger
demanderait de réécrire ces lignes plus courtes, donc de toucher au code.

**Le rendu que vous voyez dans `controle_pages/` n'utilise pas vos polices.**
Cambria, Calibri et Consolas ne sont pas installées dans cet environnement ;
LibreOffice leur a substitué DejaVu. Le `.docx` demande bien les bonnes polices —
elles apparaîtront sur votre machine. Les images de contrôle sont donc fidèles
pour la **mise en page**, pas pour la **typographie**.

---

## 4. Le parti pris typographique : titres en noir

Vous m'avez dit que le bleu des titres faisait « généré par l'IA ». Vous avez
raison, et la raison est identifiable : un aplat de couleur unique appliqué
mécaniquement à tous les niveaux de titre est la signature d'un gabarit
automatique, pas d'un livre composé. Un manuel universitaire imprimé ne fait
presque jamais cela — il hiérarchise par la **police**, le **corps**, la
**casse** et les **filets**.

**Ce que j'ai mis à la place.**

| Niveau | Traitement |
|---|---|
| **Partie** | Cambria 24 pt, petites capitales, interlettrage élargi, centré entre deux filets pleine largeur, sur page à part |
| **Chapitre** | Cambria 19 pt gras, aligné à gauche, filet épais (1,5 pt) sous le titre, sur page nouvelle |
| **Leçon** | Cambria 14 pt gras, sans filet, respiration large au-dessus |
| **Sous-partie** | Cambria 12 pt gras italique |
| **Encadré (exercices, problèmes)** | deux filets gris fins, en retrait des deux côtés, corps 10 pt |
| **Légendes** | Calibri 9 pt italique, gris foncé, centré |

Le contraste **serif pour les titres / sans serif pour le corps** fait à lui
seul le travail que faisait la couleur, et il tient à l'impression comme à la
photocopie.

**Ce qui reste en couleur, et doit le rester** : les 17 figures et la coloration
syntaxique des blocs de code. Ce sont les deux endroits du manuel où la couleur
porte de l'information — la distinction des classes sur un nuage de points,
celle des mots-clés et des commentaires dans un programme — et non de la
décoration. Vérifié sur le PDF : 17 figures sur 17 en couleur.

**Les encadrés d'exercices** ont perdu leur aplat bleu clair et leur barre
colorée au profit de deux filets gris fins. Ce n'était pas un titre, mais cet
aplat participait du même effet de gabarit automatique et jurait avec des titres
noirs. Dites-moi si vous préférez que la teinte revienne : c'est une ligne à
changer dans `outils/faire_reference_docx.py`.

**Un outil de secours si vous devez un jour imprimer en noir et blanc.**
`python3 outils/images_nb.py` convertit les figures en niveaux de gris avec un
renforcement de contraste, en gardant les originaux dans `media_couleur/` ;
`--couleur` les restaure. Il n'est **pas** appliqué : le manuel est livré avec
ses figures en couleur.

**Coût en pages : +3** (275 → 278). Les filets et les respirations prennent un
peu de place.

---

## 5. Ce que je n'ai pas pu vérifier — votre relecture est nécessaire

C'est la section à lire avant toute diffusion. L'accès réseau sortant est bloqué
par la politique de l'organisation ; je n'ai pu consulter aucune source externe.

### 5.1 Références bibliographiques

- **Les six ouvrages cités n'ont pas d'ISBN** (Russell & Norvig, Goodfellow,
  Géron, Bishop, Jurafsky & Martin, Sutton & Barto). Les 25 autres entrées sont
  des articles, des lois ou des règlements, qui n'en ont pas. Je ne les ai pas
  inventés : un ISBN faux renvoie le lecteur vers un autre livre, et l'erreur
  est invisible. À relever sur les exemplaires eux-mêmes, en notant bien
  l'édition et le format.
- **Les années, éditeurs et numéros arXiv** que j'ai portés viennent de ma
  connaissance et n'ont été confrontés à aucun catalogue. À contrôler ligne à
  ligne.

### 5.2 Droit congolais (chapitre 14)

La section repose **intégralement sur le contenu que vous m'avez fourni** —
c'était votre consigne au prompt 6 et je m'y suis tenu. Je n'ai vérifié aucune
référence au Journal officiel. À faire confirmer par un juriste :

- Ordonnance-Loi n° 23/010 du 13 mars 2023 portant Code du numérique, ratifiée
  par la Loi n° 23/041 du 1ᵉʳ septembre 2023, JO numéro spécial, 64ᵉ année,
  20 mars 2023 ;
- les articles cités (2, 31-123, 36, 39, 40, 48-53, 61, 63, 64-66, 68-75,
  76, 81, 105-110, 124-129, 130-135, 142, 304-309, 310 et suivants) ;
- les textes connexes : Loi n° 005/2002 (BCC), Loi n° 20/017 du
  25 novembre 2020, Décret n° 22/41 du 26 novembre 2022 ;
- l'état de ratification de la Convention de Malabo.

**Le statut d'entrée en vigueur, les délais et les montants de sanction sont les
points les plus susceptibles d'avoir changé depuis votre rédaction.**

### 5.3 Faits que je me suis abstenu d'écrire

Vous m'aviez demandé de signaler plutôt que d'inventer. Deux affirmations
manquent au texte :

- **le taux d'erreur d'AlexNet en 2012** (chapitre 1, leçon 2) : j'ai écrit
  « une marge spectaculaire » sans chiffre ;
- **le nombre de règles des grands systèmes experts des années 1980**
  (chapitre 1) : j'ai décrit le mécanisme sans l'attribuer à un système réel.

Confirmez-les et je les ajoute.

Par ailleurs le manuel ne contient **aucun tarif, aucun numéro de version de
modèle, aucune performance de produit** : ces valeurs se périment en quelques
mois. Les ordres de grandeur qui subsistent (fenêtres de contexte, ratio
mots/jetons) sont présentés comme approximatifs.

### 5.4 Décisions qui vous reviennent

Quatre points sont en attente de votre arbitrage, aucun ne bloque la
compilation :

1. **Les 16 cas d'usage congolais** proposés dans
   `ANCRAGE_LOCAL_2_CAS_A_CHOISIR.md` : vous deviez en choisir ; rien n'a encore
   été rédigé.
2. **Le titre du chapitre 18**, « Maîtriser les assistants IA : ChatGPT, Claude,
   Perplexity », alors que le chapitre couvre désormais huit outils.
3. **Les 82 exercices dirigés de fin de chapitre n'ont pas de corrigé.** Les
   corriger porterait l'annexe A à 146 entrées. Ce n'était pas demandé.
4. **La profondeur de la table des matières** (voir section 3).

### 5.5 Un dernier mot sur le fond

Je n'ai pas relu votre manuel en spécialiste de chacun des 24 domaines qu'il
couvre. J'ai ajouté environ 60 000 mots ; ils sont cohérents avec ce que vous
aviez écrit et avec eux-mêmes, les 19 exemples chiffrés ont été recalculés à la
main et les 30 blocs Python sont vérifiés syntaxiquement — mais **une relecture
de fond par vous reste indispensable**, en particulier sur les chapitres 8
(statistiques avancées), 12 (renforcement) et 13 (agents et MCP), où la densité
technique est la plus forte.

---

## 6. Ce qui est prêt

- `Guide_Intelligence_Artificielle_publiable.docx` — 278 pages, mise en page
  complète, table des matières calculée, folios en pied de page.
- `Guide_Intelligence_Artificielle_publiable.pdf` — même document, contrôlé page
  à page.
- `Guide_Intelligence_Artificielle.md` — la source unique.
- `code/` — 4 projets exécutables, leurs jeux de données et leur vérification.
- `controle_pages/` — les 278 pages en images, pour votre propre contrôle.
- `build.sh` — pour tout reconstruire à l'identique.

Le document original, `Guide_Intelligence_Artificielle.docx`, est intact dans le
premier commit du dépôt.
