# Anatomie du document officiel — lettre RAD

Analyse complète de `modeles/lettre_officielle_RAD.docx` (le modèle fourni par l'auteur,
conservé **intact** dans ce dépôt). Ce fichier est la mémoire de référence : tout ce qui
suit a été relevé dans le XML du document, pas deviné.

## 1. Identité du document

| Élément | Valeur relevée |
|---|---|
| Entité | Réserve Armée de la Défense (RAD) |
| Référence | `N˚ …… /MDNAC/RAD/Coord Nat/DAL/Div Num/26` |
| Lieu | KINSHASA |
| Destinataire du modèle | `Au Dir AdmLog` |
| Signataire | MUFALME BULENDA Josué |
| Fonction | Chef Div Numérique |
| Objet du modèle | projet d'acquisition des logiciels, matériels informatiques et équipements réseau… |
| Créé / modifié | 2026‑04‑14 (Microsoft Word, `Normal.dotm`) |

## 2. Page et sections

| Paramètre | Valeur (twips) | Équivalent |
|---|---|---|
| Format | 11741 × 16838 | ≈ A4 (légèrement rogné en largeur) |
| Marge haut | 1135 | 2,00 cm |
| Marge bas | 284 | 0,50 cm |
| Marge gauche | 1134 | 2,00 cm |
| Marge droite | 1109 | 1,96 cm |
| En‑tête / pied | 708 / 708 | 1,25 cm |

Une seule section, avec `<w:titlePg/>` : la **première page a son propre en‑tête et son
propre pied de page**, distincts des suivantes.

| Rôle | Fichier | Contenu |
|---|---|---|
| En‑tête `first` / `default` / `even` | `header3` / `header2` / `header1` | image `media/image2.jpeg` (1 Mo) |
| Pied `first` | `footer3.xml` | `Réserve Armée de la Défense, Av de la Gombe N°306/Kinshasa Gombe. Email : rad.rdcongo@gmail.com Tel :+243824180385` |
| Pied `default` | `footer2.xml` | idem |
| Pied `even` | `footer1.xml` | `Camp LtCol KOKOLO.` … `E-mail : fardcsecas01@gmail.com` + `f.secasfardc` |

## 3. Corps du document — 29 paragraphes de premier niveau

| # | Rôle | Mise en forme relevée |
|---|---|---|
| 0 | Logo en‑tête DAL + `KINSHASA, le …` | zone de texte ancrée (`media/image1.jpeg`, 2658×1890 EMU) puis 6 tabulations, Tahoma 12 pt |
| 2 | Numéro d'enregistrement | retrait droit −283, Tahoma 11 pt, 6 tabulations d'alignement |
| 7 | Destinataire | retrait gauche 4320 (7,6 cm), Tahoma 12 pt **gras**, justifié |
| 10 | `O B J E T :` + objet | style `Paragraphedeliste`, retrait g. 142 / d. −567, justifié. `O B J E T` en gras 14 pt, l'objet en gras 12 pt |
| 12 | Formule d'ouverture | style `Paragraphedeliste`, **numéroté**, `spacing after=0 line=240`, retrait d. 322, justifié, Tahoma 14 pt |
| 14–22 | Paragraphes du corps | style `Paragraphedeliste`, **numérotés**, `spacing after=160 line=259`, Tahoma 14 pt |
| 13, 15, 17, 19, 21 | Séparateurs vides | `Paragraphedeliste` sans numérotation — ce sont eux qui créent l'interligne |
| 25 | Signataire | centré, retrait g. 3540, Tahoma 12 pt **gras** |
| 26 | Fonction | centré, retrait g. 3540, Tahoma 12 pt |

### Le point le plus important : les paragraphes sont numérotés automatiquement

Les paragraphes du corps portent `<w:numPr><w:ilvl 0/><w:numId 2/></w:numPr>`.
`numId 2` renvoie à un `abstractNum` **décimal**, `lvlText = "%1."`, **chiffre en gras**,
retrait `left=720 hanging=360`. La lettre s'affiche donc ainsi :

```
1.  Honneur de vous saluer et vous transmettre ce dont l'objet repris en marge.
2.  En effet, dans le cadre de la modernisation …
3.  Ce document, joint en annexe à la présente, …
4.  Je sollicite votre haute bienveillance …
5.  Votre Aut trouve en Ann, la Note Technique Stratégique y relatif.
6.  Profonds respects.
```

La numérotation est gérée par Word, pas écrite dans le texte : **elle s'ajuste
automatiquement** au nombre de paragraphes. Les séparateurs vides n'ont pas de `numPr`,
donc ils ne consomment pas de numéro.

Le style `Paragraphedeliste` (« List Paragraph ») porte `<w:contextualSpacing/>`, qui
annule l'espacement `after` entre paragraphes de même style. C'est la raison pour laquelle
l'auteur intercale des paragraphes vides : sans eux, les paragraphes seraient collés.

### Autres numérotations disponibles dans le document

| `numId` | Format | Usage retenu |
|---|---|---|
| 2 | décimal `1.` gras | paragraphes du corps (convention de la lettre) |
| 1 | puce `-` | listes subordonnées à l'intérieur du corps |
| 10 | puce `•` (Symbol) | non utilisé |

## 4. Polices et tailles

Tout le document est en **Tahoma**. Tailles relevées (demi‑points → points) :

| `w:sz` | Points | Où |
|---|---|---|
| 28 | 14 | corps de la lettre, `O B J E T` |
| 24 | 12 | date, destinataire, objet, signataire, fonction |
| 20 / 18 / 16 | 10 / 9 / 8 | espacements techniques |

Chaque `rPr` porte aussi `color = text1` et deux effets `w14` (`shadow` désactivée,
`textOutline` sans remplissage) — hérités d'un ancien collage. Ils sont conservés tels
quels : les reproduire à l'identique évite toute dérive de rendu.

## 5. Conventions rédactionnelles du modèle

- Ton : administratif militaire, phrases courtes, première personne (« Je sollicite… »).
- Abréviations d'usage conservées : `Dir AdmLog`, `Coord Nat`, `Div Num`, `Aut`, `Ann`,
  `y relatif`.
- Ouverture : « Honneur de vous saluer et vous transmettre ce dont l'objet repris en marge. »
- Mention d'annexe : « Votre Aut trouve en Ann, … y relatif. »
- Clôture : « Profonds respects. »
- Typographie française : apostrophe courbe `’`, espace insécable avant `: ; ! ?` et
  à l'intérieur des guillemets `« … »`.
- La date et le numéro d'enregistrement sont laissés **en blanc** dans le modèle : ils sont
  portés à la main à la signature. Le générateur respecte ce défaut.

## 6. Ce que le générateur ne touche jamais

`scripts/lettre.py` recopie le `.docx` entrée par entrée et ne réécrit que
`word/document.xml`. Restent donc **identiques octet pour octet** : les deux images, les
trois en‑têtes, les trois pieds de page, `styles.xml`, `numbering.xml`, `theme1.xml`,
`fontTable.xml`, `settings.xml`.

Vérification effectuée en reproduisant la lettre d'origine à partir du générateur : les
29 paragraphes ont un `<w:pPr>` **rigoureusement identique** à celui du modèle, le
`<w:sectPr>` est inchangé, et seul `word/document.xml` diffère dans l'archive.
Contrôle XSD (`validate.py`) : `All validations PASSED`.
