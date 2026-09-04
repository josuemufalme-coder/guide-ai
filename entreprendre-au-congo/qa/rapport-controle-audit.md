# Contrôle des mesures de l'audit

**Objet.** Vérifier, sur le PDF de contrôle lui-même, chacun des constats chiffrés de la
partie I de `AUDIT-ET-CAHIER-DES-CHARGES-Claude-Code.md`, avant de construire une chaîne
de fabrication sur ces chiffres.

**Méthode.** Script `qa/mesure-typo.py`, rejouable. Géométrie lue dans les matrices du PDF
(`pypdf`) ; comptage des lignes par `pdftotext -layout`, dont l'extraction préserve les
espaces là où `pypdf` les perd sur du texte très justifié. Sortie archivée dans
`qa/mesures-pdf-existant.txt`.

**Source contrôlée.** `source/ENTREPRENDRE-AU-CONGO-p001-072.pdf` et
`source/ENTREPRENDRE-AU-CONGO-p073-144.pdf`, 144 pages au total.

---

## 1. Constats confirmés

| Constat de l'audit | Valeur annoncée | Valeur mesurée | Verdict |
| --- | --- | --- | --- |
| Format | A5, 148 × 210 mm | MediaBox 148,0 × 210,0 mm | confirmé |
| Pagination | 144 pages, multiple de 4 | 144 pages | confirmé |
| Gouttière plus large que l'extérieure | 20,5 / 14,7 mm | 21,2 / 15,2 mm (origine des glyphes, approche incluse) | confirmé |
| B2 — police de repli | DejaVu Serif | `DejaVuSerif`, `-Bold`, `-Italic`, toutes incorporées et sous-ensemblées | confirmé |
| B3 — justification | 112,8 mm pour un corps de 9,96 pt | 111,5 mm, corps 9,96 pt | confirmé |
| B5 — ponctuation haute rejetée | 32 cas | 38 lignes commençant par `;` `:` `!` `?` `»` | confirmé, voir §3 |
| B6 — schémas en chasse fixe | 3 occurrences | police `LMMono10-Regular` présente, 3 schémas retrouvés | confirmé |
| B7 — notes sans appel | 5 notes, aucun appel | 5 notes, aucun appel de note dans le corps | confirmé |
| B8 — prépresse | PDF 1.5, pas de XMP, pas de fond perdu | `%PDF-1.5`, XMP absent, TrimBox = MediaBox = format fini | confirmé |
| Ouverture des chapitres en recto | 29 sur 29 | 16 pages blanches, **toutes paires** | confirmé indirectement |

## 2. Un constat à corriger : le taux de césure est nul, pas de 0,7 %

L'audit compte 15 lignes terminées par un tiret sur 2 163 lignes pleines, et conclut à un
taux de 0,7 %. Les 15 lignes existent bien — je les retrouve toutes. **Aucune n'est une
césure.**

Ce sont quinze coupures sur un trait d'union déjà présent dans le texte :

```
… écoutez-|le              … que font-|ils           … Posez-|vous
… Faites-|la               … Que dites-|vous         … un rendez-|vous
… Revenez-|y               … ces moments-|là         … ce mois-|ci
… Faudra-|t-il             … la plus sous-|utilisée  … Faites-|y
… et fixez-|vous           … est peut-|être          … et parlez-|leur
```

TeX pratique ces coupures **même sans aucun motif de césure chargé** : il n'a pas besoin de
savoir couper les mots, il lui suffit de trouver un tiret. Les compter comme des césures
fausse la mesure vers le haut.

Après retrait, le compte est le suivant :

```
lignes de texte           : 2431
lignes césurées           : 0
taux de césure            : 0,00 %
coupures d'aubaine        : 15
```

**Conséquence.** B1 n'est pas « la césure est faible », mais « la césure est absente ».
`babel-french` n'est pas seulement mal réglé : ses motifs ne sont pas chargés du tout. Le
diagnostic de l'audit est bon, sa mesure était trop indulgente. Le critère de sortie de la
phase 1 part donc de 0,00 % et non de 0,7 %.

## 3. Deux mesures à définir avant de pouvoir les opposer

Le cahier des charges fixe des seuils sans dire comment on les mesure. Sans définition, le
critère de sortie de la phase 1 n'est pas vérifiable. Les définitions retenues, inscrites en
tête de `qa/mesure-typo.py` et opposables tant qu'elles ne sont pas amendées :

- **ligne de texte** — au moins 25 signes dans la sortie `pdftotext -layout`, hors table des
  matières ;
- **ligne césurée** — ligne de texte terminée par un tiret dont le second élément, sur la
  ligne suivante, n'est ni un enclitique (`le`, `vous`, `t-il`, `là`, `ci`…) ni le
  complément d'un préfixe composant (`sous-`, `non-`, `demi-`…) ;
- **ponctuation haute rejetée** — ligne commençant par `;` `:` `!` `?` ou `»`.

L'écart entre les 32 cas de l'audit et mes 38 tient à cette dernière définition : je compte
aussi les occurrences situées dans les encadrés et une ligne isolée ne contenant qu'un `;`.
L'ordre de grandeur est le même ; le chiffre opposable est 38, puisque c'est celui que le
script sait recompter à l'identique.

## 4. Une mesure qui nuance B3

L'audit estime la justification à « 68 à 72 signes par ligne ». Mesuré sur les 2 431 lignes
de texte : **médiane 59 signes, 90ᵉ centile 65**. Les lignes pleines tournent donc autour de
65 signes, soit dans le haut de l'optimum de labeur (60–66), et non au-dessus.

Cela ne disculpe pas la composition actuelle : les blancs béants viennent d'abord de
l'absence totale de césure (§2), qui force la justification à écarter les mots. Mais cela
change la correction à apporter. Ramener la justification à 100–105 mm comme le demande le
cahier, **et** passer à un corps de 10,5–11 pt, **et** adopter une police de labeur plus
étroite que DejaVu ferait tomber la ligne autour de 52 à 56 signes — sous l'optimum, dans
l'autre sens.

Il faut donc traiter « 60 à 66 signes » comme le critère maître et laisser les millimètres
en découler, une fois la police choisie. C'est la décision D2, et elle est indissociable de
la D3 : la largeur de chasse d'EB Garamond et celle de Source Serif 4 ne donnent pas la
même justification à corps égal.

## 5. Effet sur la pagination

Mesures actuelles : bloc de texte de 185,8 mm, interlignage **15 pt**, soit 35 lignes par
page à 65 signes — environ 2 275 signes par page.

Avec les marges de la phase 1 (tête 16 mm, pied 20 mm, bloc de 174 mm) :

| Interlignage | Signes/ligne | Lignes/page | Croissance | Pagination attendue |
| --- | --- | --- | --- | --- |
| 14 pt | 63 | 35 | +3 % | ~148 pages |
| 14,5 pt | 63 | 34 | +6 % | ~152 pages |
| 15 pt | 63 | 32 | +13 % | ~160 pages |
| 15 pt | 60 | 32 | +18 % | ~168 pages |

L'ouvrage passe donc de 144 à **150–170 pages** selon les réglages retenus. À confirmer par
une compilation réelle : ces chiffres supposent une densité de texte homogène, ce qu'un
livre à encadrés et à titres n'est jamais tout à fait.

## 6. Ce que le contrôle a également établi

- **16 pages blanches**, toutes de parité paire. La règle « ouverture en recto » est bien
  tenue ; il faudra la préserver en phase 7, et ces 16 pages expliquent une partie de la
  pagination.
- **Interlignage réel : 15 pt** pour un corps de 9,96 pt, soit un rapport de 1,51. C'est
  généreux, et c'est ce qui rend la page lisible malgré les blancs. Descendre à 14 pt en
  phase 1 gagnerait des pages mais resserrerait une composition déjà chargée.
- L'erreur de langue relevée au point C de l'audit est bien présente au même endroit
  (« Ces défaillances… leur absence n'est pas imputable… Elle procède »).

---

## Réserve

Ce contrôle porte sur le PDF. Il ne vaut pas contrôle du manuscrit : le fichier Markdown
source `ENTREPRENDRE-AU-CONGO.md`, désigné par le §2 du cahier comme seule source de vérité,
n'a pas été fourni. Tant qu'il manque, la phase 0 ne peut pas exécuter son contrôle
différentiel « au caractère près », puisqu'il n'existe aucun original auquel comparer la
recomposition.
