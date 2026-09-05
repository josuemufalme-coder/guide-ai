# Rapport de lecture et d'édition

Lecture intégrale du manuscrit — 22 411 mots, 8 parties, 16 chapitres — et examen
de la fabrication. Ce rapport dit ce que le livre fait bien, ce qui a été corrigé,
et ce qui reste à décider par l'auteure.

Une réserve, écrite une fois pour toutes : **aucune relecture humaine n'a eu
lieu.** Ce rapport est l'avis d'un lecteur attentif et d'un contrôle outillé. Il
ne remplace pas un correcteur professionnel, et il ne remplace surtout pas un
lecteur congolais qui connaît le terrain dont parle le livre.

---

## 1. Ce que vaut le manuscrit

**Le livre tient sa promesse.** L'introduction annonce « un instrument de travail
directement applicable ». C'est exactement ce qui est livré : chaque chapitre
expose une notion, l'éprouve dans les conditions congolaises, et se termine par
des opérations exécutables. Peu d'ouvrages de gestion tiennent cette discipline
sur seize chapitres.

**Sa force principale est le positionnement.** L'introduction situe l'ouvrage
entre le développement personnel, qui motive sans transmettre, et les manuels de
gestion importés, qui supposent un environnement qui n'existe pas ici. Ce
diagnostic est juste et il est tenu partout : les encadrés « Réalité congolaise »
ne sont pas des ornements de couleur locale, ils corrigent réellement la
prescription générale — le compliment qui n'engage à rien, le crédit client
accordé par gêne, le taux mensuel qui masque un coût annuel, l'absence de
statistiques fiables.

**La voix est sûre.** Des phrases courtes, des affirmations tranchées assumées
(« ce n'est pas vous qui décidez si votre produit est bon »), aucun jargon non
défini, aucune promesse de richesse. Le refus du ton motivationnel est constant,
et c'est ce qui donne au livre son autorité.

**Trois passages sont particulièrement réussis** et méritent d'être mis en avant
dans la promotion : le chapitre 11 sur la séparation des caisses, qui nomme la
pression sociale au lieu de la contourner ; le chapitre 13 sur le fonds de
roulement, avec le tableau de deux entreprises identiques et pourtant
incomparables ; et la clôture, dont la dernière phrase est la meilleure du livre.

---

## 2. Ce qui a été corrigé

### Dans le texte

| Où | Ce qui était imprimé | Ce qui l'est maintenant |
| --- | --- | --- |
| ch. 8 | `**Si (obstacle précis) alors (…)` — deux astérisques imprimées en toutes lettres | *Si* et *alors* en gras, comme dans l'exemple qui suit |
| ch. 12 | « à intervalle régulier » | « à intervalles réguliers » (expression invariable) |

Rien d'autre n'a été touché à la prose. Les 93 autres signalements de
LanguageTool portent sur le style — place de l'adjectif, virgule conseillée, mot
répété — et le style de l'auteure n'est pas une erreur.

### Dans la structure

| Défaut | Portée | État |
| --- | --- | --- |
| Énumération repartant de 1 après un tableau : « 1, 2, **1** » | ch. 5, le positionnement | corrigé |
| Énumération repartant de 1 après un paragraphe : huit parties numérotées « 1, **1**, 2…7 » | ch. 16, le plan d'affaires | corrigé |
| Sous-sections composées à la taille des sections : le lecteur ne voyait pas que « Directe et indirecte » dépendait d'« Analyser sa concurrence » | ch. 2, 5, 6, 8 — 13 titres | un troisième niveau de titre a été créé |
| Le titre de l'ouvrage répété en tête de chaque page | tout l'ouvrage | la partie à gauche, le chapitre à droite |
| Les parties annoncées au fil du texte | 8 parties | chacune a sa page, recto, verso blanc |
| Table des matières renvoyant deux pages trop loin pour les parties | 8 entrées | corrigé |

### Dans la fabrication

Les demi-graphiques des trois schémas manquaient à la fonte à chasse fixe et
s'imprimaient en blanc. Les cinq appels de notes s'imprimaient « [^3] » en toutes
lettres. La ligne de régie du spécimen s'imprimait au pied des 140 pages. Le
filet de tête d'un encadré restait seul en bas d'une page. La couverture était
définie en RVB. Tout cela est corrigé, et chaque correction a désormais son
contrôle : `make qa`, `make langue`, `make ouvrage`.

---

## 3. Ce qui reste à décider — par ordre d'importance

### 3.1 Le mot « démodation » (ch. 13)

Il n'existe pas en français. Il est dans le livre imprimé, ce n'est donc pas un
défaut de reconstitution — c'est un choix de vocabulaire. « L'obsolescence » ou
« le passage de mode » diraient la même chose avec un mot attesté. **Je ne l'ai
pas remplacé : substituer un mot est une décision d'auteure, pas de contrôle.**

### 3.2 Une puce du chapitre 10 qui n'appartient pas au chapitre 10

« Inscrivez votre propre salaire dans vos charges d'exploitation » figure dans le
*Ce qu'il faut retenir* du chapitre 10, alors que le sujet est traité au chapitre
11 et nulle part au chapitre 10. Un lecteur qui utilise les récapitulatifs comme
index sera renvoyé au mauvais endroit. À déplacer, ou à faire précéder de
« (chapitre 11) ».

### 3.3 Les chapitres 7 et 11 n'ont pas de « Réalité congolaise »

C'est l'écart signalé depuis la phase 0, et vous avez demandé qu'on n'y touche
pas. Il faut néanmoins savoir ce qu'il coûte : l'introduction promet, page 12,
que **chaque** chapitre comporte les deux encadrés. Le chapitre 10 en porte deux,
ce qui rétablit le compte global mais pas la promesse chapitre par chapitre. Un
lecteur méthodique le remarquera. Trois issues possibles, toutes légitimes :
écrire les deux encadrés manquants ; nuancer la phrase de l'introduction
(« la plupart des chapitres ») ; ou ne rien changer, en connaissance de cause.

### 3.4 Un déséquilibre de longueur entre chapitres

Les chapitres 2 (2 605 mots) et 10 (2 375) sont trois fois plus longs que les
chapitres 1 (781), 12 (844), 11 (890) et 15 (902). Ce n'est pas une faute — un chapitre
court et dense se lit bien — mais le chapitre 2 fait deux choses à la fois : la
méthode d'identification d'une opportunité, puis l'inventaire des ressources et
des gisements. Il se scinderait naturellement en deux chapitres à la « Deuxième
porte : le marché ». À votre appréciation.

### 3.5 Ce qui manquerait pour un lecteur qui va jusqu'au bout

Le livre conduit jusqu'au plan d'affaires. Trois choses qu'il ne donne pas et que
son lecteur cherchera le lendemain :

- **Un modèle vierge.** Le livre demande vingt fois d'écrire quelque chose — les
  hypothèses, le tableau de positionnement, le plan de développement, le cahier
  de caisse, le tableau de bord d'une page. Une annexe de six à huit tableaux
  vierges, à recopier, ferait du livre un outil qu'on garde ouvert sur la table.
  C'est, à mon avis, **le plus fort ajout possible pour le moins d'effort.**
- **Un exemple continu.** Une même petite entreprise fictive suivie d'un chapitre
  à l'autre — son idée, son test, son prix de revient, son fonds de roulement —
  donnerait un fil que les exemples ponctuels ne donnent pas.
- **Un glossaire.** Une trentaine de termes sont définis en passant dans le texte
  (prix de revient, fonds de roulement, positionnement, segment, marge, seuil de
  rentabilité, main-d'œuvre, créance, découvert, crédit-bail). Deux pages en fin
  d'ouvrage éviteraient au lecteur de revenir en arrière.

### 3.6 Les cinq notes

Elles disent honnêtement « des travaux de recherche », sans citer de source
nommée. C'est défendable pour un livre pratique. Mais la note 3 (contagion
émotionnelle dans le financement participatif) et la note 2 (initiative
personnelle) renvoient à des travaux identifiables : les nommer coûterait deux
lignes et donnerait au livre un adossement qu'il n'a pas encore.

### 3.7 Le prix, l'ISBN, le dépôt légal

Rien de tout cela n'est dans le livre, et la page de droits ne porte aucune
mention d'attente. Il reste à obtenir : l'ISBN et son code-barres (la réserve est
prête, en bas à droite de la quatrième), le dépôt légal, et la date d'achevé
d'imprimer que l'imprimeur fournit.

---

## 4. Ce que l'imprimeur doit confirmer

- **L'épaisseur du dos.** Elle est calculée à **7,3 mm** pour 140 pages en 80 g/m²
  de main 1,3. C'est une hypothèse : la main varie d'un papier à l'autre, et une
  erreur de 0,5 mm décale le pli. `python3 couverture/composer-jaquette.py --dos X`
  recompose la couverture à l'épaisseur qu'il indiquera.
- **Le dos de 7,3 mm est mince pour un texte.** Il est composé, mais un dos de
  moins de 8 mm supporte mal le décalage de pliage. Deux réponses possibles :
  un papier plus épais (90 ou 100 g/m², qui portera le dos à 8,2 ou 9,1 mm et
  améliorera aussi l'opacité), ou un dos sans texte.
- **La couleur.** L'ocre est posé en C0 M57 J81 N36. Sans épreuve contractuelle,
  il s'imprimera plus sombre et plus terne que sur un écran. Demandez une épreuve
  papier avant le tirage : c'est la seule manière de juger un aplat.
- **Le noir du texte** est du noir seul, jamais du noir composé. C'est le bon
  choix pour un texte de labeur ; ne laissez personne le « enrichir ».

---

## 5. Ce que je ferais ensuite, dans cet ordre

1. Faire relire le livre par deux personnes : un correcteur, et un entrepreneur
   congolais en activité. Le second trouvera ce qu'aucun contrôle ne trouve.
2. Trancher les points 3.1 à 3.3 — ce sont des décisions d'une ligne chacune.
3. Ajouter l'annexe de tableaux vierges (point 3.5). C'est ce qui transformera un
   bon livre en outil de travail.
4. Obtenir l'ISBN, puis recomposer : les trois lignes de la page de droits et le
   code-barres de la quatrième sont les seules choses qui bougeront.
5. Demander une épreuve papier à l'imprimeur avant le tirage.

---

## 6. Le texte de quatrième de couverture

C'est **le seul texte de ce dépôt qui n'est pas de l'auteure.** Il est écrit à
partir de l'introduction et de la clôture, et la citation qui le termine est la
sienne, mot pour mot. Il est à relire et à corriger librement — il se modifie
dans `couverture/composer-jaquette.py`, en tête du fichier.
