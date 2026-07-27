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
| Pages du PDF final | — | **286** | A4, corps 11 pt, couvertures comprises |

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
| `outils/couverture.py` | couverture recto verso pour l'imprimeur |
| `outils/couverture_pages.py` | rend la couverture en images pour le document |
| `outils/images_impression.py` | figures à 300 dpi, sans alpha, encre plafonnée |
| `outils/lulu.py` | bloc intérieur et couverture en un volet, pour Lulu |
| `outils/controle_impression.py` | rejoue les contrôles de l'imprimeur |
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
corps commence à la page 22 du PDF avec le folio « 1 » et court jusqu’à « 264 ».
Deux sections `sectPr` distinctes, la seconde avec `pgNumType w:start="1"`.

**Ordre de fin vérifié**, conforme à votre demande : Annexe A — Corrigés,
Annexe B — Glossaire, Annexe C — Bibliographie, Annexe D — Index des figures.

---

## 3. Contrôle visuel : ce que j'ai trouvé et corrigé

Les 286 pages ont été converties en images et analysées ; j'en ai regardé une
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

## 5. La passe typographique et les normes du livre

Ces corrections sont appliquées sur le document généré, et non sur le
Markdown : les tableaux de pandoc sont alignés au caractère près, y changer la
largeur d'une cellule casserait leur lecture.

### Typographie française

| | Avant | **Après** |
|---|---:|---:|
| Apostrophes courbes `’` | 0 | **5 039** |
| Apostrophes droites `'` restantes | 4 859 | **59**, toutes dans du code |
| Espaces insécables | 0 | **2 705** |
| Lignes commençant par `:` `;` `?` `»` ou `%` | **39** | **0** |

L'absence d'espace insécable était le défaut le plus visible : le PDF comptait
trente-neuf lignes qui s'ouvraient sur un deux-points ou un guillemet fermant.
Quatre cent soixante-douze cas demandaient un traitement particulier, la
ponctuation s'y trouvant coupée entre deux fragments de texte — là où le gras
commence au deux-points, par exemple.

Les entiers d'au moins cinq chiffres reçoivent un séparateur de milliers
insécable. En deçà, la règle est désactivée : elle retoucherait les années et
les numéros d'article de loi.

### Normes du livre imprimé

- **Marges en vis-à-vis.** La marge de reliure alterne désormais d'une page à
  l'autre. Vérifié sur le PDF : le bord gauche du texte passe de 91 pt sur les
  pages impaires à 80 pt sur les paires.
- **Justification ramenée de 76 à 74 signes** par ligne, dans la fourchette de
  lisibilité du livre imprimé.
- **Césure automatique française**, avec le dictionnaire `hyphen-fr`. Sans
  elle, une justification sur 15 cm laisse des lézardes entre les mots.
- **En-tête courant** portant le titre du chapitre en cours, sur 252 pages. Un
  lecteur qui ouvre le livre au hasard sait où il est.
- **Faux-titre et son verso blanc**, avant la page de titre.
- **Mise à jour des champs à l'ouverture**, que pandoc perdait en régénérant
  `settings.xml`. La table des matières se recalcule maintenant toute seule.

### Page de droits

- **ISBN 978-0-557-99817-3.** J'ai recalculé la clé de contrôle à partir des
  douze premiers chiffres : elle vaut 3, conforme au code-barres fourni.
- **Dépôt légal : juillet 2026.**

### Couvertures intégrées

La première et la quatrième sont maintenant dans le document, chacune dans sa
propre section à marges nulles, sans folio ni en-tête, aux dimensions exactes
de la page. Le code-barres EAN-13 est posé sur la quatrième, sur fond blanc
franc et avec une zone de silence autour : un lecteur optique l'exige.

### Ce que je n'ai pas fait, et pourquoi

**Les chapitres ne démarrent pas en page de droite.** C'est la convention du
livre imprimé, mais elle ajouterait une douzaine de pages blanches à un manuel
de travail que l'on consulte plutôt qu'on ne le lit d'affilée. Dites-moi si
vous la voulez : c'est un réglage, pas une reprise.

**Le format reste A4.** Passer en 17 × 24 cm — le format d'un manuel
universitaire — suppose de refaire l'intérieur et la couverture ensemble. Le
gain principal, la longueur de ligne, est déjà obtenu par l'élargissement des
marges.

## 6. Le contrôle de Lulu : trois alertes, trois causes

Lulu a signalé trois défauts sur le fichier de 286 pages. Les voici, avec ce
qui les provoquait et ce que j'ai fait.

### a) Couverture d'encre trop élevée

**La cause : les deux pages de couverture se trouvaient dans le fichier
intérieur.** Elles portent un aplat bleu nuit sur près de la moitié de leur
surface ; mesuré, cela donne 40 % de la page au-dessus de 180 % de couverture
d'encre, avec un maximum à 241 %. Aucune page intérieure ne dépasse 1 % de sa
surface à ce niveau.

**Ce que j'ai fait, et pourquoi c'est de toute façon obligatoire.** Lulu, comme
tout imprimeur en impression à la demande, attend **deux fichiers séparés** :
le bloc intérieur d'un côté, la couverture de l'autre. Une couverture laissée
dans l'intérieur serait imprimée sur le papier intérieur, sans pelliculage.
`Lulu_interieur.pdf` compte donc **284 pages** et ne contient plus les
couvertures.

J'ai aussi plafonné la couverture d'encre des figures à 210 %, et neutralisé
les gris sombres légèrement teintés : un gris qui n'est pas exactement neutre
se sépare en quatre encres superposées au lieu d'une seule, ce qui alourdit
l'encrage et fait baver les petits caractères au moindre défaut de repère.

### b) Images sous 200 dpi

**Dix figures sur dix-sept** étaient entre 145 et 197 points par pouce à la
taille où elles sont placées. Toutes sont maintenant à **300 dpi**, la valeur
de référence.

**Je dois être clair sur la portée de cette correction.** Rééchantillonner ne
crée pas de détail. Cela supprime l'escalier des contours et fait taire le
contrôle, mais la finesse d'origine n'est pas restituée. Les figures gagneront
vraiment à être régénérées à la bonne taille — ce qu'il faut de toute façon
faire pour corriger les numéros incrustés dans les pixels.

**Une régression que j'ai introduite et corrigée en route.** Ma première
version accentuait les contours après agrandissement. Sur ces schémas en
aplats, l'accentuation créait de part et d'autre des traits un halo plus
sombre que l'original et légèrement teinté : la couverture d'encre passait de
190 % à 300 % sur ces pixels. J'ai supprimé l'accentuation et ajouté deux
garde-fous — un recadrage dans l'étendue de couleurs de l'image d'origine, et
un plafond d'encre.

### c) Transparence détectée

Les dix-sept PNG portaient un **canal alpha**. Il était entièrement opaque,
mais sa seule présence suffit : le moteur d'impression doit alors aplatir la
page, avec un résultat imprévisible. Les images sont désormais en RVB sans
canal alpha, composées sur du blanc.

Vérifié sur le PDF final : aucune occurrence de `/SMask`, `/Transparency`,
`/Group`, `/CA` ni `/ca`.

### Les deux fichiers à téléverser

| Fichier | Contenu |
|---|---|
| `Lulu_interieur.pdf` | 284 pages, 210 × 297 mm exactement, sans fond perdu |
| `Lulu_couverture.pdf` | un seul volet de 444,35 × 303,35 mm : quatrième, dos de 18 mm, première, avec 3,175 mm de fond perdu |

**La largeur du dos dépend du papier que vous choisirez.** Pour 284 pages :

| Papier | Dos |
|---|---:|
| blanc 60 # (standard) | 16,2 mm |
| **crème 60 # — retenu** | **18,0 mm** |
| couché 80 # (couleur premium) | 23,1 mm |

**Le dos retenu est de 18,0 mm**, confirmé sur le gabarit de Lulu. La
couverture livrée fait donc 444,35 × 303,35 mm. Pour un autre papier :
`python3 outils/lulu.py --dos <millimètres>`. Une erreur de dos ne décale pas
seulement le titre sur la tranche, elle déporte le pli, donc les deux plats.

Le titre du dos est centré à 0,04 mm près, mesuré sur le fichier produit.

**Sur le choix d'impression.** Votre livre contient dix-sept figures en
couleur. Si vous restez en impression standard, Lulu peut de nouveau signaler
l'encrage ; l'option couleur premium est le choix cohérent avec le contenu.
L'autre voie, si le coût compte, est de passer les figures en niveaux de gris :
`python3 outils/images_nb.py` le fait, mais les schémas y perdent la
distinction par la couleur.

### Contrôle rejoué

`python3 outils/controle_impression.py <fichier.pdf>` rejoue les trois
vérifications. Résultat sur les deux fichiers livrés :

```
Lulu_interieur.pdf — 284 pages, 210 x 297 mm
  images       : 17, aucune sous 200 dpi
  transparence : aucune
  encre        : aucune page au-dessus de 240 %

Lulu_couverture.pdf — 1 page, 443 x 303 mm
  images       : 1, aucune sous 200 dpi
  transparence : aucune
  encre        : aucune page au-dessus de 240 %
```

Une réserve sur la mesure d'encre : sans profil colorimétrique installé, la
conversion vers le CMJN est faite par la formule qui retire le maximum de
noir, donc celle qui donne la couverture d'encre **la plus basse possible**. Le
moteur de Lulu sera plus sévère. C'est pourquoi j'ai plafonné les figures bien
en dessous du seuil.

---


## 7. Ce que je n'ai pas pu vérifier — votre relecture est nécessaire

C'est la section à lire avant toute diffusion. L'accès réseau sortant est bloqué
par la politique de l'organisation ; je n'ai pu consulter aucune source externe.

### 7.1 Références bibliographiques

- **Les six ouvrages cités n'ont pas d'ISBN** (Russell & Norvig, Goodfellow,
  Géron, Bishop, Jurafsky & Martin, Sutton & Barto). Les 25 autres entrées sont
  des articles, des lois ou des règlements, qui n'en ont pas. Je ne les ai pas
  inventés : un ISBN faux renvoie le lecteur vers un autre livre, et l'erreur
  est invisible. À relever sur les exemplaires eux-mêmes, en notant bien
  l'édition et le format.
- **Les années, éditeurs et numéros arXiv** que j'ai portés viennent de ma
  connaissance et n'ont été confrontés à aucun catalogue. À contrôler ligne à
  ligne.

### 7.2 Droit congolais (chapitre 14)

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

### 7.3 Faits que je me suis abstenu d'écrire

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

### 7.4 Décisions qui vous reviennent

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

### 7.5 Un dernier mot sur le fond

Je n'ai pas relu votre manuel en spécialiste de chacun des 24 domaines qu'il
couvre. J'ai ajouté environ 60 000 mots ; ils sont cohérents avec ce que vous
aviez écrit et avec eux-mêmes, les 19 exemples chiffrés ont été recalculés à la
main et les 30 blocs Python sont vérifiés syntaxiquement — mais **une relecture
de fond par vous reste indispensable**, en particulier sur les chapitres 8
(statistiques avancées), 12 (renforcement) et 13 (agents et MCP), où la densité
technique est la plus forte.

---

## 8. Ce qui est prêt

- `Lulu_interieur.pdf` et `Lulu_couverture.pdf` — **les deux fichiers à
  téléverser sur Lulu**, contrôlés (voir section 6).
- `Guide_Intelligence_Artificielle_publiable.docx` — 286 pages, couvertures
  comprises, table des matières calculée, folios en pied de page. C'est le
  fichier de travail, pas celui de l'imprimeur.
- `Guide_Intelligence_Artificielle_publiable.pdf` — même document, contrôlé page
  à page.
- `Guide_Intelligence_Artificielle.md` — la source unique.
- `code/` — 4 projets exécutables, leurs jeux de données et leur vérification.
- `controle_pages/` — les 286 pages en images, pour votre propre contrôle.
- `build.sh` — pour tout reconstruire à l'identique.

Le document original, `Guide_Intelligence_Artificielle.docx`, est intact dans le
premier commit du dépôt.
