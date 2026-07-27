# DIAGNOSTIC — Guide_Intelligence_Artificielle.docx

**Document analysé :** `Guide_Intelligence_Artificielle.docx`
**Empreinte MD5 :** `495f36ae11a8a6516285ad681c6967f1` (984 850 octets)
**Date d'analyse :** 27 juillet 2026
**Méthode :** conversion `pandoc` en Markdown (source de travail), décompression de l'archive OOXML et lecture directe de `word/document.xml`, `word/styles.xml` et `word/_rels/document.xml.rels`.

**Aucune modification n'a été apportée au document.** Ce rapport est purement descriptif.

---

## 0. Ce que contient réellement le document

| Élément | Annoncé | Mesuré | Écart |
|---|---|---|---|
| Mots | ~29 000 | 28 528 (Markdown) / 33 977 (texte OOXML brut, tableaux inclus) | conforme |
| Parties | 8 | **8** | conforme |
| Chapitres | 24 | **25** | +1 (voir § 5) |
| Leçons | 156 | **156** | conforme |
| Images | 17 | **17** | conforme |
| Légendes de figure | — | 17 | 1 légende par image |
| Encadrés « L'ESSENTIEL À RETENIR » | — | 80 | — |
| Encadrés « À VOUS DE JOUER » | — | 25 | — |

Le corps des leçons représente **21 637 mots**, soit 74 % du volume. Le reste se répartit entre les introductions de partie, les encadrés, les exercices et les annexes.

---

## 1. Styles de titre — **CONFIRMÉ**

> *« aucun style de titre n'est utilisé (seulement `ListBullet` et `ListNumber`) »*

**Verdict : confirmé, sans réserve.**

Recensement exhaustif des styles de paragraphe appliqués dans `word/document.xml` :

```
313  w:pStyle w:val="ListBullet"
110  w:pStyle w:val="ListNumber"
```

Ce sont les **deux seuls** styles appliqués dans tout le document. Aucun autre `w:pStyle` n'apparaît.

Preuves complémentaires :

- **`outlineLvl` : 0 occurrence.** Aucun paragraphe ne porte de niveau de plan. Word est donc structurellement incapable de générer une table des matières, un volet de navigation ou un signet de titre.
- Les styles `Heading1` à `Heading9` **sont bien définis** dans `word/styles.xml` (ce sont les définitions par défaut du modèle Word), mais **aucun n'est jamais appliqué**. Ils sont présents et inutilisés.
- Aucun `w:rStyle` (style de caractère) n'est utilisé nulle part.

**Conséquence.** Toute la hiérarchie du livre — parties, chapitres, leçons — repose exclusivement sur du **gras manuel** dans des paragraphes de style `Normal`. Dans le Markdown converti, cela se traduit par **zéro ligne commençant par `#`** : la conversion ne produit aucun titre, seulement des `**...**`. Exemples relevés :

| Ligne | Contenu | Rôle réel |
|---:|---|---|
| 51 | `**PARTIE I**` | titre de partie |
| 53 | `**Les fondations**` | sous-titre de partie |
| 61 | `**Introduction à l'intelligence artificielle**` | titre de chapitre |
| 63 | `**Leçon 1 --- Qu'est-ce que l'intelligence artificielle ?**` | titre de leçon |

Rien ne distingue typographiquement, pour la machine, un titre de partie d'un mot mis en valeur au milieu d'un paragraphe.

---

## 2. Table des matières, pied de page, pagination, sections — **CONFIRMÉ**

> *« aucune table des matières, aucun pied de page, aucun numéro de page, une seule section »*

**Verdict : confirmé sur les quatre points.**

| Vérification | Recherche effectuée | Résultat |
|---|---|---|
| Table des matières | `fldChar` et `instrText` dans `document.xml` | **0 occurrence** — aucun champ, donc aucun champ `TOC` |
| Pied de page | fichiers `word/footer*.xml` dans l'archive | **aucun fichier** |
| En-tête | fichiers `word/header*.xml` dans l'archive | **aucun fichier** |
| Références en-tête/pied | `headerReference` / `footerReference` | **0 occurrence** |
| Numéro de page | champ `PAGE` (via `instrText`) | **0 occurrence** — impossible, aucun champ n'existe |
| Sections | balises `<w:sectPr>` | **1 seule** |

Contenu intégral de l'unique `sectPr`, en fin de document :

```xml
<w:sectPr w:rsidR="00FC693F" w:rsidRPr="0006063C" w:rsidSect="00034616">
  <w:pgSz w:w="12240" w:h="15840"/>
  <w:pgMar w:top="1224" w:right="1440" w:bottom="1224"
           w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>
  <w:cols w:space="720"/>
  <w:docGrid w:linePitch="360"/>
</w:sectPr>
```

Deux remarques sur ce bloc :

1. Les attributs `w:header="720"` et `w:footer="720"` ne définissent **que la marge réservée** aux en-têtes et pieds de page. Ils ne créent aucun contenu. La réserve existe, elle est vide.
2. Le format de page est **12 240 × 15 840 twips**, soit 8,5 × 11 pouces : du **Letter américain**, et non du A4 (11 906 × 16 838 twips). Pour un ouvrage destiné à être imprimé et diffusé hors États-Unis, c'est un point à trancher avant la mise en page finale.

L'archive ne contient par ailleurs ni `footnotes.xml` ni `endnotes.xml` : aucune note de bas de page dans tout l'ouvrage.

**Conséquence.** En l'état, le fichier ne peut pas être paginé, ni cité par numéro de page, ni imprimé avec des liminaires distincts du corps. Ce sont trois prérequis d'un ouvrage universitaire.

---

## 3. Numérotation des leçons — **CONFIRMÉ sur les trois anomalies**

> *« une "Leçon 4bis" sans leçon 4 dans le chapitre sur l'apprentissage par renforcement, une "Leçon 9bis" sans leçon 9 dans le chapitre sur n8n, une leçon 4 manquante dans le chapitre sur la gestion de projets »*

**Verdict : les trois anomalies sont confirmées, dans les chapitres exactement désignés. Ce sont les seules du document** — les 22 autres chapitres ont une numérotation continue de 1 à N.

### 3.1 — Chapitre « Apprentissage par renforcement » (partie III)

Séquence relevée : **1, 2, 3, 4bis**

| Ligne | Intitulé |
|---:|---|
| 1226 | Leçon 1 — Apprendre par essais et erreurs |
| 1236 | Leçon 2 — Le cadre formel : états, actions, récompenses |
| 1242 | Leçon 3 — Algorithmes et le dilemme exploration/exploitation |
| 1248 | **Leçon 4bis** — Applications et limites du renforcement |

Il n'existe aucune « Leçon 4 » dans ce chapitre. La dernière leçon porte un suffixe `bis` qui ne renvoie à rien.

### 3.2 — Chapitre « Automatisation des tâches avec n8n » (partie V)

Séquence relevée : **1, 2, 3, 4, 5, 6, 7, 8, 9bis, 10**

| Ligne | Intitulé |
|---:|---|
| 1936 | Leçon 8 — Sécurité et confidentialité des automatisations |
| 1942 | **Leçon 9bis** — Comprendre les déclencheurs en profondeur |
| 1958 | Leçon 10 — Connecter n8n au reste de votre écosystème |

La leçon 9 « pleine » n'existe pas. Le `bis` s'intercale entre 8 et 10, à la place qu'occuperait naturellement la leçon 9.

### 3.3 — Chapitre « Gestion de projets d'intelligence artificielle » (partie IV)

Séquence relevée : **1, 2, 3, 5, 6** — la leçon 4 est purement et simplement absente.

| Ligne | Intitulé |
|---:|---|
| 1486 | Leçon 3 — Données, risques et passage à l'échelle |
| 1490 | **Leçon 5** — Les sept causes d'échec et comment les éviter *(saut de 3 à 5)* |
| 1512 | Leçon 6 — Communiquer avec les décideurs |

Rien dans le texte ne signale ce saut : il n'y a ni renvoi vers une leçon 4, ni trace d'un contenu supprimé. Le chapitre compte 5 leçons numérotées jusqu'à 6.

---

## 4. Figure 2.1 — **CONFIRMÉ**, et le problème est plus large

> *« la "Figure 2.1" n'existe pas alors que les figures 2.2 et 2.3 existent »*

**Verdict : confirmé.** Mais la numérotation des figures est désorganisée bien au-delà de ce seul manque.

Les 17 images ont chacune leur légende, dans l'ordre. En revanche, les numéros attribués ne suivent aucune logique exploitable.

**Recensement par préfixe :**

| Préfixe | Numéros présents | Anomalie |
|---|---|---|
| 1.x | 1.1 | — |
| **2.x** | **2.2, 2.3** | **⚠ Figure 2.1 absente** |
| 3.x | 3.1, 3.2, 3.3 | ⚠ apparaissent dans l'ordre 3.3, puis 3.2, puis 3.1 |
| 4.x à 8.x | 4.1, 5.1, 6.1, 7.1, 8.1 | — |
| 9.x | 9.1, 9.2 | — |
| 10.x | 10.1, 10.2 | ⚠ apparaissent dans l'ordre 10.2, puis 10.1 |
| 11.x, 12.x | 11.1, 12.1 | — |

**Trois défauts distincts, donc :**

1. **La figure 2.1 n'existe pas.** Le lecteur qui rencontre « Figure 2.2 » cherchera naturellement une figure 2.2 précédée d'une 2.1. Elle n'a jamais été insérée.
2. **Deux inversions d'ordre.** La figure 3.3 apparaît en page bien avant les figures 3.2 et 3.1. Idem pour 10.2, qui précède 10.1. Un lecteur qui parcourt l'ouvrage voit les numéros décroître.
3. **Le premier nombre ne correspond à aucun chapitre.** C'est le défaut le plus profond : puisque les chapitres ne sont pas numérotés (§ 5), le préfixe des figures ne peut renvoyer à rien. Voici la position réelle de chaque figure :

| Légende | Image | Chapitre où elle se trouve réellement |
|---|---|---|
| Figure 1.1 | image1.png | *avant tout chapitre* — introduction de la partie I |
| Figure 3.3 | image2.png | ch. 3 — Mathématiques ✔ *(seule concordance du document)* |
| Figure 2.2 | image3.png | ch. 4 — Fondamentaux de la Data Science |
| Figure 2.3 | image4.png | ch. 5 — Apprentissage automatique |
| Figure 3.2 | image5.png | ch. 6 — Réseaux de neurones |
| Figure 3.1 | image6.png | ch. 6 — Réseaux de neurones |
| Figure 4.1 | image7.png | ch. 7 — Ingénierie des données et MLOps |
| Figure 5.1 | image8.png | ch. 9 — NLP |
| Figure 7.1 | image9.png | ch. 10 — IA générative |
| Figure 6.1 | image10.png | ch. 11 — Vision par ordinateur |
| Figure 8.1 | image11.png | ch. 12 — Apprentissage par renforcement |
| Figure 9.1 | image12.png | ch. 13 — IA avancée |
| Figure 9.2 | image13.png | ch. 13 — IA avancée |
| Figure 10.2 | image14.png | ch. 17 — Assistants IA |
| Figure 10.1 | image15.png | ch. 18 — Ingénierie de prompts |
| Figure 11.1 | image16.png | ch. 19 — n8n |
| Figure 12.1 | image17.png | ch. 20 — Intégrer l'IA en entreprise |

**Sur 17 figures, une seule** (Figure 3.3, au chapitre 3) voit son préfixe coïncider avec le rang réel de son chapitre — et c'est vraisemblablement une coïncidence. Point rassurant en revanche : **chaque légende décrit bien l'image qui la précède immédiatement**. Le contenu est juste ; c'est la numérotation qui est à refaire intégralement.

---

## 5. Numérotation des chapitres — **CONFIRMÉ** (mais ils sont 25, pas 24)

> *« les 24 chapitres ne portent aucun numéro »*

**Verdict : l'absence de numéro est confirmée sans exception. En revanche le décompte de 24 est à corriger : j'en dénombre 25.**

**Aucun chapitre ne porte de numéro.** Le mot « Chapitre » n'apparaît **jamais comme titre** dans tout le document : les 3 seules occurrences du mot sont des mentions dans le corps du texte (lignes 25, 2486, 2628), du type « à la fin de chaque chapitre ». Les chapitres sont introduits par une simple ligne en gras portant leur intitulé nu — par exemple `**Vision par ordinateur**` — typographiquement identique à n'importe quelle autre mise en gras.

**Sur le décompte.** En recensant toute ligne en gras isolée suivie d'une « Leçon 1 », j'obtiens 25 chapitres :

| Partie | Chapitres | Détail |
|---|---:|---|
| I — Les fondations | 4 | Introduction à l'IA · Python · Mathématiques · Data Science |
| II — Comment une machine apprend | 4 | Apprentissage automatique · Réseaux de neurones · MLOps · Statistiques avancées |
| III — Les grands domaines | 5 | NLP · IA générative · Vision · Renforcement · IA avancée |
| IV — Bien faire et bien décider | 3 | Éthique · Gestion de projets · Cas d'usage |
| V — Les outils au quotidien | **9** | Assistants IA · Prompts · n8n · Entreprise · Productivité · Études de cas · Créer ses assistants · **Bibliothèque de prompts** · **Recettes n8n** |
| VI, VII, VIII | 0 | ne contiennent aucune structure en leçons |
| **Total** | **25** | |

L'écart tient aux deux derniers chapitres de la partie V — « Bibliothèque de prompts prêts à l'emploi » (ligne 2276) et « Recettes d'automatisation n8n pas à pas » (ligne 2372). Ils sont **structurés exactement comme des chapitres** (titre en gras, puis « Leçon 1 », « Leçon 2 »…), mais leur nature est celle d'une **annexe pratique** : des modèles de prompts et des recettes à recopier, non un exposé pédagogique.

**Décision à prendre avant la phase 2 :** faut-il les compter comme chapitres 24 et 25, ou les basculer en annexes ? Le choix conditionne toute la numérotation. Je ne tranche pas et j'attends votre arbitrage.

Les parties VI (projets guidés), VII (exercices corrigés) et VIII (pour aller plus loin) ne comportent **aucun chapitre ni aucune leçon** : elles sont composées de sections libres. C'est cohérent avec leur fonction, mais cela signifie qu'une numérotation continue de chapitres ne les couvrira pas.

---

## 6. Collision du mot « Leçon » — **CONFIRMÉ**

> *« le marqueur `**Leçon** :` est utilisé au sens de "morale de l'exercice" et entre en collision avec le niveau de titre "Leçon N" »*

**Verdict : confirmé. 33 occurrences.**

Le mot « Leçon » assure **deux fonctions incompatibles** dans le même document :

1. **Niveau hiérarchique** — `**Leçon 12 --- Titre**`, en tête de section : 156 occurrences.
2. **Marqueur de moralité** — `**Leçon** :` en fin de paragraphe, au sens de « ce qu'il faut en retenir » : **33 occurrences**.

Exemples relevés du second usage :

| Ligne | Extrait |
|---:|---|
| 301 | `**Leçon** : on écrit le code une fois, mais on le lit cent fois.` |
| 321 | `**Leçon** : un bon artisan connaît tous ses outils et choisit le bon pour chaque tâche.` |
| 774 | `**Leçon** : en IA, une idée simple bien placée peut débloquer tout un domaine.` |
| 852 | `**Leçon** : un modèle est un organisme vivant qu'on entretient, pas un objet qu'on livre une fois pour toutes.` |
| 908 | `**Leçon** : connaître son ignorance est aussi précieux que connaître la réponse.` |
| 1008 | `**Leçon** : l'attention donne au modèle le sens du contexte.` |

Ces 33 marqueurs se trouvent tous **à l'intérieur** d'encadrés « Exemple — » ou de corrigés d'exercices, jamais en début de paragraphe.

**Pourquoi c'est bloquant.** Dès que les titres seront convertis en vrais styles (`Heading3` pour les leçons), tout traitement automatique cherchant « Leçon » devra distinguer les deux usages. Une table des matières générée sur une recherche textuelle capterait les 33 morales. Le remplacement par `**À retenir** :`, prévu au prompt 3, lève l'ambiguïté — mais il faut noter qu'un troisième objet porte déjà un nom voisin : les **80 encadrés « L'ESSENTIEL À RETENIR »**. Le futur `**À retenir** :` devra rester visuellement distinct de ces encadrés, sous peine de déplacer la collision au lieu de la résoudre.

---

## 7. « Ce cours » dans un livre — **CONFIRMÉ**

> *« "ce cours" apparaît une douzaine de fois dans un document qui se présente comme un livre »*

**Verdict : confirmé. 14 occurrences de « ce cours », 17 en comptant les variantes proches.**

Le document s'affirme comme un livre dès ses premières lignes : *« J'ai écrit **ce livre** parce que j'aurais aimé le lire quand j'ai commencé »* (ligne 15), puis *« tout le reste **du livre** s'appuiera sur elle »* (ligne 55). L'avant-propos écarte même explicitement le registre du cours : *« Ce n'est pas **un cours froid** ni un catalogue de notions »* (ligne 17).

Et pourtant, **14 fois**, le texte se désigne comme un cours :

| Ligne | Extrait | Contexte |
|---:|---|---|
| 211 | « **Ce cours** va consolider votre maîtrise » | ch. 2, ouverture |
| 385 | « l'idée la plus importante de tout **ce cours** » | ch. 3 |
| 415 | « les quatre domaines **du cours** » | ch. 3 |
| 417 | « les quatre domaines de **ce cours** » | ch. 3, encadré |
| 467 | « **Ce cours** vous apprend à… » | ch. 4, ouverture |
| 542 | « le fil **du cours** » | ch. 4 |
| 886 | « **Ce cours** vous apprend… » | ch. 8, ouverture |
| 1044 | « **Ce cours** vous apprend… » | ch. 10, ouverture |
| 1296 | « **Ce cours** vous amène à la pointe absolue du domaine » | ch. 13, ouverture |
| 1316 | « **Le cours** aborde… » | ch. 13 |
| 1548 | « **Ce cours** relie tout ce que vous avez appris » | ch. 16, ouverture |
| 2000 | « **Ce cours** … » | ch. 20, ouverture |
| 2108 | « **Ce cours** … » | ch. 21, ouverture |
| 2166 | « **Ce cours** passe en revue des scénarios réels » | ch. 22, ouverture |
| 2280 | « **Ce cours** vous en fournit une base concrète » | ch. 24, ouverture |
| 2376 | « **Ce cours** vous offre des **recettes** » | ch. 25, ouverture |
| 2464 | « l'une des recettes de **ce cours** » | exercice |

**Un motif clair se dégage :** l'expression apparaît presque systématiquement dans la **phrase d'ouverture d'un chapitre**. C'est la signature d'un document rédigé chapitre par chapitre comme des fiches de formation autonomes, puis assemblé en livre sans reprise des raccords. On relève aussi « toute la **formation** » (ligne 69) et « le cours » employé au sens boursier (ligne 2696), qui lui est légitime et ne doit pas être touché.

---

## 8. Étiquette « Exemple — » détournée — **CONFIRMÉ**

> *« l'étiquette "Exemple —" est employée pour des corrections d'exercices et des définitions »*

**Verdict : confirmé pour les corrections d'exercices (usage massif et systématique) ; confirmé partiellement pour les définitions.**

L'étiquette `**Exemple ---**` est utilisée **76 fois**. Le document dispose pourtant d'un jeu d'étiquettes assez riche :

| Étiquette | Occurrences |
|---|---:|
| `**Exemple ---` | **76** |
| `**À VOUS DE JOUER ---` | 25 |
| `**Définition ---` | 18 |
| `**Notion essentielle ---` | 6 |
| `**Étape N ---` | 18 |
| `**Pont entre matières ---` | 2 |
| `**Piège fréquent ---` | 2 |
| `**Mon conseil ---` | 2 |

### 8.1 — Les corrigés d'exercices : 14 cas, sans ambiguïté

Dans la partie VII (« S'entraîner : exercices corrigés »), **les 14 corrigés sont tous introduits par `**Exemple --- correction.**`**. Le mot « Exemple » y est manifestement parasite : ce ne sont pas des exemples, ce sont les solutions des exercices.

> Ligne 2650 — `**Exemple --- correction.** La dérivée est f'(w) = 2(w − 4). **Étape 1** : en w = 7, f'(7) = 2×3 = 6…`

> Ligne 2662 — `**Exemple --- correction.** Produit scalaire = 2×1 + (−1)×4 + 3×2 = 2 − 4 + 6 = 4…`

C'est un calcul corrigé, pas une illustration. Le renommage en « Correction » prévu au prompt 3 est fondé.

### 8.2 — Les définitions et explications : nuance à apporter

Le document possède **une étiquette `Définition ---` propre, utilisée 18 fois**. Les définitions canoniques sont donc majoritairement bien étiquetées :

> Ligne 65 — `**Définition --- Intelligence artificielle.** Domaine de l'informatique visant à…`

Cependant, plusieurs encadrés `Exemple ---` n'introduisent **aucun exemple** mais une **propriété, une méthode ou une synthèse** :

| Ligne | Étiquette | Nature réelle |
|---:|---|---|
| 379 | « Exemple — le produit scalaire mesure la similarité. » | énoncé d'une **propriété mathématique** |
| 395 | « Exemple — la métaphore du brouillard. » | **analogie pédagogique** (descente de gradient) |
| 417 | « Exemple — tout est lié. » | **synthèse de fin de chapitre** |
| 774 | « Exemple — pourquoi la ReLU a tout changé. » | **explication historique** |
| 852 | « Exemple — pourquoi le cycle ne s'arrête jamais. » | **justification conceptuelle** |
| 1940 | « Exemple — une question à toujours se poser. » | **règle de méthode** |

**Reformulation proposée du constat :** l'étiquette « Exemple — » sert de **fourre-tout** pour tout encadré qui n'est ni une définition ni un exercice. Elle recouvre au moins quatre natures différentes : exemple véritable, correction d'exercice, analogie, et règle de méthode. L'affirmation « employée pour des définitions » est donc à préciser : les définitions strictes ont leur étiquette, mais les **énoncés de propriété et les explications conceptuelles** sont bien rangés sous « Exemple ».

---

## 9. Résolution des images — **CONFIRMÉ**

> *« la résolution des images est d'environ 190 dpi, en dessous du standard d'impression de 300 dpi »*

**Verdict : confirmé. 185 dpi en moyenne. Les 17 images sans exception sont sous le seuil de 300 dpi.**

La résolution effective est calculée en divisant la largeur réelle en pixels par la largeur d'affichage demandée dans le document.

| Fichier | Pixels | Affichage (pouces) | **DPI effectif** | Poids |
|---|---|---|---:|---:|
| image1.png | 895 × 657 | 4,60 × 3,38 | **195** | 69 Ko |
| image2.png | 947 × 601 | 4,80 × 3,05 | **197** | 52 Ko |
| image3.png | 1221 × 461 | 6,20 × 2,34 | **197** | 62 Ko |
| image4.png | 1221 × 453 | 6,20 × 2,30 | **197** | 56 Ko |
| image5.png | 1004 × 506 | 5,20 × 2,62 | **193** | 36 Ko |
| **image6.png** | 781 × 650 | 5,40 × 4,49 | **145** ⚠ | 134 Ko |
| image7.png | 782 × 806 | 4,20 × 4,33 | **186** | 53 Ko |
| image8.png | 787 × 807 | 3,80 × 3,90 | **207** | 42 Ko |
| image9.png | 1221 × 441 | 6,40 × 2,31 | **191** | 36 Ko |
| image10.png | 1221 × 412 | 6,40 × 2,16 | **191** | 30 Ko |
| image11.png | 898 × 536 | 5,00 × 2,98 | **180** | 28 Ko |
| image12.png | 1221 × 543 | 6,40 × 2,85 | **191** | 55 Ko |
| image13.png | 1113 × 439 | 6,20 × 2,45 | **180** | 50 Ko |
| **image14.png** | 1004 × 456 | 6,20 × 2,82 | **162** ⚠ | 41 Ko |
| **image15.png** | 950 × 607 | 5,60 × 3,58 | **170** ⚠ | 52 Ko |
| image16.png | 1221 × 392 | 6,60 × 2,12 | **185** | 42 Ko |
| image17.png | 1004 × 564 | 5,60 × 3,15 | **179** | 55 Ko |

**Synthèse :** moyenne **185 dpi** · minimum **145 dpi** (image6) · maximum **207 dpi** (image8) · **17 images sur 17 sous 300 dpi**.

L'estimation de « environ 190 dpi » est donc exacte, et même légèrement optimiste. Aucune image ne dépasse 207 dpi.

**Trois observations pratiques :**

1. **Il n'y a rien à récupérer par recompression.** Ces fichiers sont à leur résolution native ; on ne peut pas « augmenter » leur définition. Atteindre 300 dpi suppose de **régénérer les 17 schémas depuis leur source**, idéalement en **vectoriel** (SVG, PDF ou EMF), qui reste net à toute échelle et rend la question du dpi sans objet.
2. **Trois cas sont plus critiques** : image6 (145 dpi), image14 (162) et image15 (170). Ils seront visiblement flous à l'impression, pas seulement légèrement adoucis.
3. **image6 pèse 134 Ko pour la plus faible résolution du lot** — c'est le pire rapport poids/qualité du document, signe d'une recompression ou d'un agrandissement subi.

---

## 10. Point non demandé, mais mesuré : les tirets cadratins

Le prompt 3 annonce « environ 705 tirets cadratins ». **Le comptage direct dans le texte source donne 433 cadratins (U+2014)**, soit **1 pour 78 mots** et non 1 pour 41. La densité reste élevée pour un texte académique, mais l'objectif de réduction devra être recalculé sur cette base — diviser 433 par deux, et non 705.

Relevé complémentaire de la ponctuation : 0 demi-cadratin (U+2013), 100 guillemets français ouvrants, 8 points de suspension typographiques.

---

## 11. Récapitulatif des verdicts

| # | Point à vérifier | Verdict | Mesure |
|---:|---|---|---|
| 1 | Aucun style de titre (`ListBullet`/`ListNumber` seuls) | ✅ **Confirmé** | 313 + 110, aucun autre ; 0 `outlineLvl` |
| 2 | Ni TDM, ni pied de page, ni pagination, 1 section | ✅ **Confirmé** | 0 champ, 0 fichier footer, 1 `sectPr` |
| 3 | Leçon 4bis (renforcement), 9bis (n8n), leçon 4 absente (projets) | ✅ **Confirmé** | 3 anomalies, aux emplacements exacts |
| 4 | Figure 2.1 absente, 2.2 et 2.3 présentes | ✅ **Confirmé** | + 2 inversions et 16/17 préfixes erronés |
| 5 | 24 chapitres sans numéro | ⚠️ **Confirmé, décompte à corriger** | Aucun numéro ✔ — mais **25** chapitres |
| 6 | `**Leçon** :` en collision avec « Leçon N » | ✅ **Confirmé** | 33 vs 156 occurrences |
| 7 | « ce cours » ~12 fois dans un livre | ✅ **Confirmé** | **14** occurrences (17 variantes) |
| 8 | « Exemple — » pour corrections et définitions | ⚠️ **Confirmé, à nuancer** | 14 corrigés ✔ ; définitions ont leur étiquette, mais fourre-tout réel |
| 9 | Images ~190 dpi, sous les 300 dpi requis | ✅ **Confirmé** | **185 dpi** de moyenne, 17/17 sous le seuil |

**Sept points confirmés sans réserve. Deux à ajuster** : le nombre de chapitres (25 et non 24) et la nature exacte du détournement de l'étiquette « Exemple — ».

---

## 12. Volumétrie des leçons

### 12.1 — Vue d'ensemble

| Indicateur | Valeur |
|---|---:|
| Nombre de leçons | 156 |
| Total des mots en leçons | 21 637 |
| **Minimum** | **33 mots** |
| 1er quartile | 67 mots |
| **Médiane** | **111 mots** |
| Moyenne | 139 mots |
| 3e quartile | 184 mots |
| **Maximum** | **439 mots** |

| Seuil | Leçons concernées | Part |
|---|---:|---:|
| moins de 50 mots | **18** | 12 % |
| moins de 100 mots | 71 | 46 % |
| moins de 200 mots | **122** | **78 %** |
| moins de 350 mots | 152 | 97 % |

**Lecture.** La médiane à 111 mots signifie qu'**une leçon sur deux tient en un paragraphe**. Le seuil de 350 mots visé au prompt 4 n'est atteint que par **4 leçons sur 156**. Dix-huit leçons font moins de 50 mots : ce sont des accroches de deux ou trois phrases, pas des unités d'enseignement.

La plus courte de tout l'ouvrage est **« Leçon 1 — Donner des yeux aux machines » (33 mots)**, qui ouvre le chapitre sur la vision par ordinateur — un sujet qui occupe des semestres entiers à l'université. Viennent ensuite « Leçon 2 — Générer des images » (37 mots) et « Leçon 4 — Monte-Carlo et séries temporelles » (40 mots) : deux sujets substantiels traités en trois phrases chacun.

À l'autre extrémité, la plus longue est « Leçon 3 — Développer une posture de conseil » (439 mots). L'écart va donc de 1 à 13, **sans corrélation avec la difficulté du sujet** : « Leçon 3 — Le protocole MCP », qui expose un protocole technique complet, tient en 164 mots, quand « Leçon 8 — Comment aborder la suite du livre », qui n'est qu'un mode d'emploi, en occupe 392.

### 12.2 — Volumétrie par chapitre

| Ch. | Chapitre | Leçons | Mots | Médiane |
|---:|---|---:|---:|---:|
| 1 | Introduction à l'intelligence artificielle | 8 | 1 843 | 211 |
| 2 | Programmation Python pour l'IA | 7 | 1 266 | 165 |
| 3 | Mathématiques pour l'IA | 7 | 1 230 | 178 |
| 4 | Fondamentaux de la Data Science | 7 | 916 | 99 |
| 5 | Apprentissage automatique supervisé/non supervisé | 7 | 1 155 | 159 |
| 6 | Réseaux de neurones et apprentissage profond | 7 | 1 076 | 144 |
| 7 | Ingénierie des données et MLOps | 5 | 621 | 81 |
| 8 | Statistiques avancées et modèles probabilistes | 5 | 596 | **47** |
| 9 | Traitement automatique du langage naturel | 7 | 889 | 94 |
| 10 | IA générative et ingénierie des invites | 9 | 1 121 | 119 |
| 11 | Vision par ordinateur | 5 | 503 | **50** |
| 12 | Apprentissage par renforcement | 4 | 537 | 97 |
| 13 | IA avancée : agents, MCP, multimodalité, sûreté | 7 | 1 056 | 159 |
| 14 | Éthique, régulation et enjeux sociétaux | 5 | 627 | **54** |
| 15 | Gestion de projets d'IA | 5 | 592 | 100 |
| 16 | Cas d'usage professionnels et sectoriels | 3 | 586 | 105 |
| 17 | Maîtriser les assistants IA | 7 | 976 | 146 |
| 18 | Ingénierie de prompts | 7 | 952 | 134 |
| 19 | Automatisation des tâches avec n8n | 10 | 1 318 | 120 |
| 20 | Intégrer l'IA dans une entreprise | 9 | 985 | 99 |
| 21 | IA pour la productivité et la création | 5 | 520 | 92 |
| 22 | Études de cas : automatisation par secteur | 6 | 509 | **57** |
| 23 | Créer ses propres assistants | 4 | 547 | 131 |
| 24 | Bibliothèque de prompts prêts à l'emploi | 5 | 575 | 84 |
| 25 | Recettes d'automatisation n8n | 5 | 641 | 116 |

**Le déséquilibre est net.** Les chapitres fondateurs (1 à 3, 1 843 / 1 266 / 1 230 mots) sont nettement mieux dotés que les chapitres de la seconde moitié. Quatre chapitres ont une médiane sous 60 mots — **Statistiques avancées (47)**, **Vision par ordinateur (50)**, **Éthique (54)** et **Études de cas (57)** — alors qu'ils portent des sujets qui exigent développement. Le chapitre sur l'**éthique et la régulation**, en particulier, tient en 627 mots pour 5 leçons : c'est le chapitre le plus exposé à la critique académique, et le plus mince.

Le rythme d'écriture décroît visiblement à mesure qu'on avance dans l'ouvrage.

### 12.3 — Tableau complet des 156 leçons, de la plus courte à la plus longue

| # | Mots | Ch. | Chapitre | Leçon | Intitulé |
|---:|---:|---:|---|---|---|
| 1 | **33** | 11 | Vision par ordinateur | 1 | Donner des yeux aux machines |
| 2 | **37** | 10 | IA générative et ingénierie des invites (pro… | 2 | Générer des images |
| 3 | **40** | 8 | Statistiques avancées et modèles probabilistes | 4 | Monte-Carlo et séries temporelles |
| 4 | **41** | 11 | Vision par ordinateur | 4 | Au-delà de la classification |
| 5 | **42** | 16 | Cas d'usage professionnels et applications s… | 1 | Relier la technique à la valeur |
| 6 | **42** | 20 | Intégrer l'IA dans une entreprise | 6 | Mesurer la valeur |
| 7 | **43** | 8 | Statistiques avancées et modèles probabilistes | 3 | Modèles de mélange et modèles graphiques |
| 8 | **45** | 10 | IA générative et ingénierie des invites (pro… | 5 | Agents, fine-tuning et garde-fous |
| 9 | **45** | 19 | Automatisation des tâches avec n8n | 5 | Chaîner plusieurs IA |
| 10 | **46** | 15 | Gestion de projets d'intelligence artificielle | 1 | Pourquoi les projets d'IA échouent |
| 11 | **46** | 18 | Ingénierie de prompts : l'art de bien formuler | 4 | Les pièges à éviter |
| 12 | **47** | 8 | Statistiques avancées et modèles probabilistes | 1 | Prédire, mais aussi connaître son incertitude |
| 13 | **47** | 22 | Études de cas : l'automatisation IA par sect… | 1 | Apprendre par l'exemple |
| 14 | **48** | 3 | Mathématiques pour l'intelligence artificielle | 5 | Théorie de l'information : mesurer l'erreur |
| 15 | **48** | 14 | Éthique, régulation et enjeux sociétaux de l… | 1 | Pourquoi l'éthique n'est pas une option |
| 16 | **48** | 14 | Éthique, régulation et enjeux sociétaux de l… | 4 | Le cadre réglementaire et les enjeux de société |
| 17 | **49** | 9 | Traitement automatique du langage naturel (N… | 1 | Faire comprendre le langage à une machine |
| 18 | **49** | 21 | IA pour la productivité et la création de co… | 4 | Création visuelle et présentations |
| 19 | **50** | 11 | Vision par ordinateur | 3 | Architectures avancées et apprentissage par transfert |
| 20 | **50** | 13 | IA avancée : agents, protocole MCP, multimod… | 1 | Le visage de l'IA en 2026 |
| 21 | **51** | 22 | Études de cas : l'automatisation IA par sect… | 4 | Administration et finance |
| 22 | **52** | 4 | Fondamentaux de la Data Science et des stati… | 6 | Communiquer : raconter une histoire avec les données |
| 23 | **54** | 14 | Éthique, régulation et enjeux sociétaux de l… | 3 | Transparence, explicabilité et vie privée |
| 24 | **55** | 23 | Créer ses propres assistants et anticiper l'… | 2 | Combiner les outils en un système |
| 25 | **55** | 25 | Recettes d'automatisation n8n pas à pas | 1 | Des recettes prêtes à adapter |
| 26 | **56** | 15 | Gestion de projets d'intelligence artificielle | 3 | Données, risques et passage à l'échelle |
| 27 | **56** | 22 | Études de cas : l'automatisation IA par sect… | 3 | Ventes et marketing |
| 28 | **57** | 7 | Ingénierie des données et MLOps | 2 | Pipelines, versioning et reproductibilité |
| 29 | **57** | 18 | Ingénierie de prompts : l'art de bien formuler | 5 | Construire une bibliothèque de prompts |
| 30 | **57** | 20 | Intégrer l'IA dans une entreprise | 1 | Le vrai défi n'est pas technique |
| 31 | **58** | 17 | Maîtriser les assistants IA : ChatGPT, Claud… | 5 | Méthode de travail avec un assistant |
| 32 | **58** | 22 | Études de cas : l'automatisation IA par sect… | 5 | Ressources humaines et veille |
| 33 | **60** | 22 | Études de cas : l'automatisation IA par sect… | 2 | Support client |
| 34 | **61** | 21 | IA pour la productivité et la création de co… | 3 | Synthèse et analyse de documents |
| 35 | **63** | 9 | Traitement automatique du langage naturel (N… | 4 | Pré-entraînement et fine-tuning |
| 36 | **64** | 18 | Ingénierie de prompts : l'art de bien formuler | 1 | Pourquoi le prompt est décisif |
| 37 | **65** | 4 | Fondamentaux de la Data Science et des stati… | 5 | Interroger les données : le SQL |
| 38 | **65** | 6 | Réseaux de neurones et apprentissage profond | 3 | Les grandes familles d'architectures |
| 39 | **67** | 25 | Recettes d'automatisation n8n pas à pas | 4 | Recette : veille automatisée d'un secteur |
| 40 | **68** | 17 | Maîtriser les assistants IA : ChatGPT, Claud… | 1 | Comprendre ce qu'est un assistant IA |
| 41 | **68** | 19 | Automatisation des tâches avec n8n | 3 | Les briques d'un workflow |
| 42 | **70** | 19 | Automatisation des tâches avec n8n | 6 | Cas d'usage professionnels courants |
| 43 | **71** | 20 | Intégrer l'IA dans une entreprise | 2 | L'escalier de maturité |
| 44 | **71** | 20 | Intégrer l'IA dans une entreprise | 5 | Gouvernance, éthique et sécurité |
| 45 | **71** | 24 | Bibliothèque de prompts prêts à l'emploi | 4 | Prompts pour la création de contenu |
| 46 | **73** | 12 | Apprentissage par renforcement | 1 | Apprendre par essais et erreurs |
| 47 | **74** | 9 | Traitement automatique du langage naturel (N… | 6 | Évaluer un modèle de langage |
| 48 | **75** | 7 | Ingénierie des données et MLOps | 1 | Le fossé entre le laboratoire et la production |
| 49 | **76** | 5 | Apprentissage automatique supervisé et non s… | 1 | Les trois façons d'apprendre |
| 50 | **78** | 2 | Programmation Python pour l'intelligence art… | 5 | Visualiser et travailler proprement |
| 51 | **78** | 12 | Apprentissage par renforcement | 3 | Algorithmes et le dilemme exploration/exploitation |
| 52 | **80** | 4 | Fondamentaux de la Data Science et des stati… | 4 | Le piège à éviter absolument : corrélation n'est pas causalité |
| 53 | **81** | 7 | Ingénierie des données et MLOps | 4 | Surveiller : un modèle vivant |
| 54 | **82** | 6 | Réseaux de neurones et apprentissage profond | 4 | Les techniques qui font marcher le deep learning |
| 55 | **82** | 24 | Bibliothèque de prompts prêts à l'emploi | 2 | Prompts pour la rédaction professionnelle |
| 56 | **84** | 24 | Bibliothèque de prompts prêts à l'emploi | 3 | Prompts pour l'analyse et la décision |
| 57 | **89** | 13 | IA avancée : agents, protocole MCP, multimod… | 4 | L'IA multimodale |
| 58 | **92** | 21 | IA pour la productivité et la création de co… | 1 | L'IA comme multiplicateur de productivité |
| 59 | **92** | 24 | Bibliothèque de prompts prêts à l'emploi | 1 | Pourquoi une bibliothèque de prompts |
| 60 | **93** | 19 | Automatisation des tâches avec n8n | 1 | Qu'est-ce que l'automatisation ? |
| 61 | **94** | 9 | Traitement automatique du langage naturel (N… | 3 | La révolution Transformer |
| 62 | **94** | 11 | Vision par ordinateur | 2 | Les réseaux convolutifs en profondeur |
| 63 | **95** | 2 | Programmation Python pour l'intelligence art… | 1 | Pourquoi Python ? |
| 64 | **95** | 7 | Ingénierie des données et MLOps | 3 | Conteneuriser et déployer |
| 65 | **95** | 10 | IA générative et ingénierie des invites (pro… | 4 | Donner des connaissances fiables : le RAG |
| 66 | **97** | 3 | Mathématiques pour l'intelligence artificielle | 1 | Pourquoi des mathématiques ? |
| 67 | **97** | 5 | Apprentissage automatique supervisé et non s… | 4 | Apprendre sans étiquettes |
| 68 | **97** | 23 | Créer ses propres assistants et anticiper l'… | 3 | Se tenir à jour dans un domaine qui bouge vite |
| 69 | **98** | 17 | Maîtriser les assistants IA : ChatGPT, Claud… | 3 | Claude : le spécialiste des textes longs et du raisonnement |
| 70 | **99** | 4 | Fondamentaux de la Data Science et des stati… | 3 | Préparer les données : le feature engineering |
| 71 | **99** | 20 | Intégrer l'IA dans une entreprise | 4 | Embarquer les équipes |
| 72 | **100** | 15 | Gestion de projets d'intelligence artificielle | 2 | Cadrer avant de coder |
| 73 | **105** | 16 | Cas d'usage professionnels et applications s… | 2 | Panorama sectoriel |
| 74 | **108** | 1 | Introduction à l'intelligence artificielle | 5 | Représenter la connaissance et anticiper l'adversaire |
| 75 | **110** | 4 | Fondamentaux de la Data Science et des stati… | 1 | La donnée, matière première de l'IA |
| 76 | **110** | 6 | Réseaux de neurones et apprentissage profond | 1 | Du neurone biologique au neurone artificiel |
| 77 | **110** | 20 | Intégrer l'IA dans une entreprise | 3 | Choisir le bon premier projet |
| 78 | **110** | 21 | IA pour la productivité et la création de co… | 2 | Rédaction et communication assistées |
| 79 | **112** | 20 | Intégrer l'IA dans une entreprise | 7 | Construire une équipe et des compétences IA |
| 80 | **114** | 10 | IA générative et ingénierie des invites (pro… | 6 | Études de prompts : du médiocre à l'excellent |
| 81 | **116** | 12 | Apprentissage par renforcement | 2 | Le cadre formel : états, actions, récompenses |
| 82 | **116** | 25 | Recettes d'automatisation n8n pas à pas | 2 | Recette : tri et résumé quotidien des emails |
| 83 | **117** | 9 | Traitement automatique du langage naturel (N… | 2 | Transformer les mots en nombres |
| 84 | **119** | 10 | IA générative et ingénierie des invites (pro… | 1 | La technologie qui a tout changé |
| 85 | **119** | 19 | Automatisation des tâches avec n8n | 2 | Présentation de n8n |
| 86 | **122** | 19 | Automatisation des tâches avec n8n | 8 | Sécurité et confidentialité des automatisations |
| 87 | **125** | 5 | Apprentissage automatique supervisé et non s… | 3 | Les arbres et les méthodes d'ensemble |
| 88 | **125** | 20 | Intégrer l'IA dans une entreprise | 8 | Anticiper les résistances et les échecs |
| 89 | **126** | 10 | IA générative et ingénierie des invites (pro… | 3 | L'art de bien parler aux modèles : le prompting |
| 90 | **134** | 18 | Ingénierie de prompts : l'art de bien formuler | 2 | L'anatomie d'un bon prompt |
| 91 | **136** | 2 | Programmation Python pour l'intelligence art… | 4 | Pandas : dompter les données |
| 92 | **137** | 3 | Mathématiques pour l'intelligence artificielle | 4 | Probabilités : raisonner dans l'incertain |
| 93 | **141** | 19 | Automatisation des tâches avec n8n | 4 | Un exemple complet : le tri intelligent des emails |
| 94 | **142** | 13 | IA avancée : agents, protocole MCP, multimod… | 2 | Les agents IA autonomes |
| 95 | **143** | 4 | Fondamentaux de la Data Science et des stati… | 2 | L'analyse exploratoire (EDA) |
| 96 | **143** | 14 | Éthique, régulation et enjeux sociétaux de l… | 2 | Les biais : quand l'IA hérite de nos préjugés |
| 97 | **143** | 25 | Recettes d'automatisation n8n pas à pas | 3 | Recette : réponse assistée aux demandes clients |
| 98 | **144** | 6 | Réseaux de neurones et apprentissage profond | 2 | Comment le réseau apprend : la rétropropagation |
| 99 | **146** | 17 | Maîtriser les assistants IA : ChatGPT, Claud… | 4 | Perplexity : la recherche sourcée |
| 100 | **149** | 8 | Statistiques avancées et modèles probabilistes | 2 | Le raisonnement bayésien |
| 101 | **150** | 6 | Réseaux de neurones et apprentissage profond | 6 | Les pièges de l'entraînement et comment les éviter |
| 102 | **152** | 10 | IA générative et ingénierie des invites (pro… | 7 | Concevoir une application générative fiable |
| 103 | **155** | 19 | Automatisation des tâches avec n8n | 7 | Bien structurer ses workflows |
| 104 | **156** | 9 | Traitement automatique du langage naturel (N… | 5 | Les tâches concrètes du NLP, expliquées |
| 105 | **157** | 17 | Maîtriser les assistants IA : ChatGPT, Claud… | 2 | ChatGPT : le couteau suisse |
| 106 | **159** | 5 | Apprentissage automatique supervisé et non s… | 2 | Apprentissage supervisé : régression et classification |
| 107 | **159** | 13 | IA avancée : agents, protocole MCP, multimod… | 5 | La sûreté de l'IA (AI Safety) |
| 108 | **164** | 13 | IA avancée : agents, protocole MCP, multimod… | 3 | Le protocole MCP |
| 109 | **165** | 2 | Programmation Python pour l'intelligence art… | 6 | Écrire du code de qualité professionnelle |
| 110 | **165** | 23 | Créer ses propres assistants et anticiper l'… | 1 | Personnaliser un assistant pour un besoin précis |
| 111 | **169** | 1 | Introduction à l'intelligence artificielle | 7 | La carte des sous-domaines de l'IA |
| 112 | **169** | 5 | Apprentissage automatique supervisé et non s… | 5 | La leçon la plus importante : évaluer et généraliser |
| 113 | **174** | 15 | Gestion de projets d'intelligence artificielle | 5 | Les sept causes d'échec et comment les éviter |
| 114 | **178** | 2 | Programmation Python pour l'intelligence art… | 3 | NumPy : le calcul qui fait tourner l'IA |
| 115 | **178** | 3 | Mathématiques pour l'intelligence artificielle | 6 | Mettre les mathématiques en pratique |
| 116 | **181** | 13 | IA avancée : agents, protocole MCP, multimod… | 6 | Concevoir un agent en pratique |
| 117 | **182** | 6 | Réseaux de neurones et apprentissage profond | 5 | Comprendre une couche convolutive en détail |
| 118 | **184** | 1 | Introduction à l'intelligence artificielle | 1 | Qu'est-ce que l'intelligence artificielle ? |
| 119 | **185** | 19 | Automatisation des tâches avec n8n | 9bis | Comprendre les déclencheurs en profondeur |
| 120 | **186** | 18 | Ingénierie de prompts : l'art de bien formuler | 3 | Les grandes techniques de prompting |
| 121 | **196** | 10 | IA générative et ingénierie des invites (pro… | 8 | La génération d'images expliquée |
| 122 | **196** | 17 | Maîtriser les assistants IA : ChatGPT, Claud… | 6 | Scénarios d'usage professionnels détaillés |
| 123 | **200** | 1 | Introduction à l'intelligence artificielle | 6 | Applications, limites et idées reçues |
| 124 | **200** | 3 | Mathématiques pour l'intelligence artificielle | 2 | Algèbre linéaire : le langage des données |
| 125 | **208** | 21 | IA pour la productivité et la création de co… | 5 | Construire son flux de travail augmenté |
| 126 | **216** | 15 | Gestion de projets d'intelligence artificielle | 6 | Communiquer avec les décideurs |
| 127 | **216** | 18 | Ingénierie de prompts : l'art de bien formuler | 6 | Techniques avancées de prompting |
| 128 | **222** | 1 | Introduction à l'intelligence artificielle | 3 | Les deux grandes façons de faire de l'IA |
| 129 | **227** | 2 | Programmation Python pour l'intelligence art… | 2 | Le langage : maîtriser les fondamentaux |
| 130 | **230** | 23 | Créer ses propres assistants et anticiper l'… | 4 | Vers une pratique responsable |
| 131 | **237** | 10 | IA générative et ingénierie des invites (pro… | 9 | Prompting pour la génération d'images |
| 132 | **237** | 22 | Études de cas : l'automatisation IA par sect… | 6 | Concevoir sa propre automatisation |
| 133 | **246** | 24 | Bibliothèque de prompts prêts à l'emploi | 5 | Prompts pour l'apprentissage et l'explication |
| 134 | **247** | 5 | Apprentissage automatique supervisé et non s… | 6 | Comprendre en profondeur : un exemple chiffré de régression |
| 135 | **249** | 18 | Ingénierie de prompts : l'art de bien formuler | 7 | Adapter le prompt à l'outil |
| 136 | **253** | 17 | Maîtriser les assistants IA : ChatGPT, Claud… | 7 | Les limites à toujours garder en tête |
| 137 | **260** | 25 | Recettes d'automatisation n8n pas à pas | 5 | Recette : traitement automatique de formulaires |
| 138 | **269** | 1 | Introduction à l'intelligence artificielle | 2 | Une brève histoire pour comprendre le présent |
| 139 | **270** | 12 | Apprentissage par renforcement | 4bis | Applications et limites du renforcement |
| 140 | **271** | 13 | IA avancée : agents, protocole MCP, multimod… | 7 | L'avenir : où va l'IA ? |
| 141 | **277** | 3 | Mathématiques pour l'intelligence artificielle | 3 | Le calcul différentiel : comment une machine apprend |
| 142 | **282** | 5 | Apprentissage automatique supervisé et non s… | 7 | Le déroulé complet d'un projet supervisé |
| 143 | **285** | 11 | Vision par ordinateur | 5 | Applications concrètes de la vision |
| 144 | **293** | 3 | Mathématiques pour l'intelligence artificielle | 7 | Erreurs mathématiques fréquentes |
| 145 | **298** | 20 | Intégrer l'IA dans une entreprise | 9 | Une feuille de route réaliste sur douze mois |
| 146 | **299** | 1 | Introduction à l'intelligence artificielle | 4 | Les agents intelligents et la recherche |
| 147 | **313** | 7 | Ingénierie des données et MLOps | 5 | Le cycle de vie complet, étape par étape |
| 148 | **317** | 8 | Statistiques avancées et modèles probabilistes | 5 | Pourquoi l'incertitude change tout en pratique |
| 149 | **320** | 19 | Automatisation des tâches avec n8n | 10 | Connecter n8n au reste de votre écosystème |
| 150 | **334** | 14 | Éthique, régulation et enjeux sociétaux de l… | 5 | Un cadre de décision éthique |
| 151 | **336** | 9 | Traitement automatique du langage naturel (N… | 7 | L'attention, expliquée simplement |
| 152 | **343** | 6 | Réseaux de neurones et apprentissage profond | 7 | Les fonctions d'activation en détail |
| 153 | **367** | 4 | Fondamentaux de la Data Science et des stati… | 7 | Les types de données et leur traitement |
| 154 | **387** | 2 | Programmation Python pour l'intelligence art… | 7 | Panorama de l'écosystème Python pour l'IA |
| 155 | **392** | 1 | Introduction à l'intelligence artificielle | 8 | Comment aborder la suite du livre |
| 156 | **439** | 16 | Cas d'usage professionnels et applications s… | 3 | Développer une posture de conseil |

---

## 13. Ce que je propose comme suite

Le diagnostic est établi. **Aucune modification n'a été apportée** : le `.docx` d'origine est intact et versionné, le Markdown n'est qu'une conversion fidèle.

Deux arbitrages vous appartiennent avant d'engager le prompt 2 :

1. **Le nombre de chapitres.** « Bibliothèque de prompts » et « Recettes n8n » sont structurés comme des chapitres mais fonctionnent comme des annexes. Chapitres 24 et 25, ou annexes A et B ? La réponse fixe toute la numérotation.
2. **La règle de numérotation des figures.** Le schéma `Figure <chapitre>.<ordre>` supposera que les parties VI à VIII, qui n'ont pas de chapitres, reçoivent un traitement propre. Et la figure 1.1 se situe dans l'introduction de la partie I, avant le premier chapitre : elle devra être déplacée ou renumérotée.

Deux points appellent par ailleurs votre attention, hors du périmètre demandé :

- **Le format de page est Letter (8,5 × 11 pouces), pas A4.** À trancher avant la mise en page finale du prompt 7.
- **Les 17 images devront être régénérées**, idéalement en vectoriel. Aucun traitement logiciel ne peut créer la définition manquante. C'est le seul point du diagnostic qui exige un travail hors de ce dépôt.

J'attends votre validation avant de toucher au moindre caractère.
