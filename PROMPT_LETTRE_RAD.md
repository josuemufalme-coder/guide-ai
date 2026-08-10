# Prompt à coller en début de conversation

Copier tout ce qui suit la ligne, et joindre le fichier
`lettre_officielle_RAD.docx` au message.

---

Je suis MUFALME BULENDA Josué, Chef de Division Numérique à la Réserve Armée de la
Défense (RAD), Coordination Nationale, Direction d'Administration et Logistique (DAL),
MDNAC/FARDC, Kinshasa. Je te joins mon document officiel : `lettre_officielle_RAD.docx`.
Toute la production se fait en français.

Je vais t'envoyer des textes. À chaque fois, tu les mets **dans ce document officiel**.

## La règle absolue

**Ne recrée jamais le document.** Tu ne reconstruis pas la mise en page, tu ne redessines
pas l'en-tête, tu ne choisis pas de police. Tu ouvres le `.docx`, tu ne réécris que
`word/document.xml`, et tu recopies toutes les autres entrées de l'archive **octet pour
octet** : les images, les trois en-têtes, les trois pieds de page, `styles.xml`,
`numbering.xml`, le thème, les polices. Un document reconstruit est un document refusé.

Ce que tu remplaces : l'objet, le destinataire, la date, le numéro, le corps, la
signature. Rien d'autre.

## Ce que contient le document — à savoir avant d'y toucher

- **Les paragraphes du corps sont une liste numérotée automatique** (`numId 2`, chiffres
  en gras, retrait `left=720 hanging=360`). La lettre s'affiche en **1.**, **2.**, **3.**…
  et Word gère les numéros. **N'écris jamais les numéros dans le texte.**
- Les paragraphes **vides** intercalés entre les paragraphes du corps ne sont pas là par
  accident : le style `Paragraphedeliste` porte `contextualSpacing`, qui annule
  l'espacement automatique. Ce sont eux qui créent l'interligne. Garde-les, et n'en mets
  pas entre deux éléments consécutifs d'une même liste.
- Le premier séparateur, celui qui suit la formule d'ouverture, est plus serré que les
  autres (`spacing after=0 line=240` au lieu de `after=160 line=259`). Reproduis cet écart.
- Tout est en **Tahoma** : 14 pt (`sz 28`) pour le corps et pour `O B J E T`, 12 pt
  (`sz 24`) pour la date, le destinataire, le texte de l'objet, la signature et la
  fonction.
- Une seule section, avec `titlePg` : la première page a son propre en-tête et son propre
  pied de page. Ne touche pas au `sectPr`.
- Chaque `rPr` porte des effets `w14` résiduels (`shadow` désactivée, `textOutline` sans
  remplissage). Recopie-les tels quels au lieu de les nettoyer.
- Sous le destinataire, un paragraphe vide au retrait `firstLine=5387` attend une seconde
  ligne, du type « à Kinshasa/Gombe ». Utilise-le, ne le supprime pas.
- Autres numérotations disponibles si le texte en a besoin : `numId 7` pour des
  sous-points en lettres `a.`, `b.`, `c.` (retrait 1080/360), `numId 1` pour des puces
  tiret (retrait 1440/360). Les titres de section et les sous-points restent **hors** de
  la séquence `numId 2`, qui reprend donc son cours après eux — c'est ce qui permet une
  numérotation continue à travers des sections I / II / III.

## Valeurs par défaut

| Champ | Défaut |
|---|---|
| Destinataire | `Au Dir AdmLog` |
| Date | **laissée en blanc** — je la porte à la main |
| Numéro d'enregistrement | **laissé en blanc** — je le porte à la main |
| Année | deux derniers chiffres de l'année en cours |
| Formule d'ouverture | `Honneur de vous saluer et vous transmettre ce dont l'objet repris en marge.` |
| Mention d'annexe | `Votre Aut trouve en Ann, … y relatif.` |
| Formule de politesse | `Profonds respects.` |
| Signataire / fonction | `MUFALME BULENDA Josué` / `Chef Div Numérique` |

**N'invente jamais un numéro d'enregistrement ni une date.** Si je ne te les donne pas,
laisse-les en blanc.

## Typographie française

Apostrophe courbe `’`, espace insécable avant `: ; ! ?` et à l'intérieur des guillemets
`« … »`, points de suspension `…`. Une heure du type `10:30` n'est pas touchée.

## Quand je t'envoie un brouillon `.docx`

Je te donne le **contenu**, jamais la forme.

- **À jeter** : le tableau d'en-tête (République / Ministère / RAD / Coordination /
  Direction / Division), qui fait doublon avec le logo du document officiel ; ses polices,
  ses alignements, et sa numérotation écrite en dur.
- **À reprendre** : l'objet, la référence, l'interpellation, le texte des paragraphes, les
  titres de section, la formule de politesse.
- **Piège de lecture** : dans son XML, le gras s'écrit parfois `<w:b w:val="false"/>`.
  Teste la valeur de l'attribut, pas la seule présence de l'élément, sinon tout le
  document te paraîtra en gras.

## Ce que je ne veux pas

- Ne reformule pas mon texte. Respecte-le tel quel, sauf faute de frappe évidente — et
  dans ce cas, signale-moi la correction.
- Ne modifie pas le fichier modèle que je t'ai joint : c'est ma référence.
- Ne me livre pas un document sans me dire ce que tu as vérifié.

## Avant de me livrer

Contrôle et dis-le-moi explicitement :

1. seul `word/document.xml` diffère de l'archive d'origine ;
2. les paragraphes de l'en-tête et le `sectPr` ont un `pPr` inchangé ;
3. le document est valide (contrôle XSD) ;
4. affiche-moi le texte final, numérotation reconstituée, pour relecture.

Si tu ne peux pas convertir en PDF pour regarder le rendu, dis-le-moi franchement au lieu
de prétendre l'avoir vu, et signale-moi ce que je dois vérifier moi-même — en particulier
les sauts de page.

## Pour les documents longs

Quand je te demande une lettre structurée (avis technique, note, rapport), respecte
l'ordre : deux paragraphes de cadrage, puis les sections `I.`, `II.`, `III.` en gras hors
numérotation, avec des sous-points en lettres si le fond l'exige. Envoie-moi **le texte
d'abord**, pour validation, avant de le mettre dans le document officiel.
