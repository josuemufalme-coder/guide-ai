# RAPPORT — Cohérence éditoriale (prompt 3)

**Commits :** `ab1a43a` → `e2bd2d6` (six groupes de corrections)
**Périmètre :** les six points de la phase 3 de votre procédure. Votre message s'arrêtait au point 4 ; j'ai traité les points 5 et 6 en supposant une troncature de copie, et les ai isolés dans leurs propres commits pour que vous puissiez les écarter d'un `git revert` si l'omission était voulue.
**Contrôle d'intégrité :** 29 391 mots avant, 29 391 après. Aucun contenu perdu.

---

## Deux prémisses à rectifier

Avant le détail, deux chiffres de l'énoncé ne résistent pas au comptage. Je les signale parce qu'ils changent la cible, pas la nature du travail.

**Les tirets cadratins : 451 au total, dont 82 seulement dans la prose.** L'énoncé annonçait « environ 705 tirets pour 29 000 mots, soit un tous les 41 mots ». Le comptage réel en donne 451. Surtout, **369 d'entre eux sont structurels** et explicitement exclus par votre propre consigne : 241 séparent un titre de son sous-titre, 111 une étiquette d'encadré de son contenu, 17 un numéro de figure de sa légende. Il n'en restait que **82 dans le corps du texte**, soit un tous les 362 mots.

La densité que vous perceviez était donc réelle, mais elle venait de la **structure**, pas de la prose. J'ai réduit de moitié les 82 qui relevaient vraiment de la ponctuation.

**Les encadrés : 41 sur 80 avaient trois puces, pas 80.** L'énoncé les décrivait « strictement identiques, toujours composés de trois puces ». La réalité : 4 encadrés à deux puces, 41 à trois, 12 à quatre, 14 à cinq, 5 à six, 4 à sept. La monotonie était donc réelle mais partielle, et concentrée sur la moitié du lot.

---

## 1. Registre — 27 passages, une seule voix

Les quatorze « ce cours » ont disparu. Le remplacement n'est pas mécanique : il dépend de la portée de la phrase.

- **« ce chapitre »** quand la portée est locale — treize cas, presque tous en phrase d'ouverture de chapitre.
- **« ce manuel »** quand elle est globale : *« l'idée la plus importante de tout ce manuel »*, *« vous coderez en Python d'un bout à l'autre de ce manuel »*.
- **Une tournure à la première personne** quand le sujet grammatical était le cours lui-même : *« Le cours aborde aussi ses enjeux de sécurité »* devient *« J'aborde aussi ses enjeux de sécurité »*.
- **Une reformulation** pour les deux collections annexes, qui ne sont pas des chapitres : *« Ce cours vous en fournit une base concrète »* devient *« Vous en trouverez ici une base concrète »*.

Traitées de la même manière : « des cours suivants », « du programme » (deux fois), « toute la formation », « l'objet de votre formation », et les deux « Vous étudierez » de catalogue de formation, dont celui que votre énoncé citait mot pour mot.

**Trois occurrences n'ont pas été touchées, et c'est délibéré :** « le cours d'aujourd'hui dépend de ceux des jours précédents » (chapitre 9) désigne un cours de bourse ; « la transparence, la formation et des résultats concrets » et « un volet conduite du changement (formation…) » (chapitre 21) désignent la formation des équipes. Les remplacer aurait introduit un contresens.

**Résolu au passage** — le renvoi que je vous avais laissé en suspens au prompt 2. Au chapitre 10, *« les agents (que nous approfondirons un peu plus loin) »* devient *« (que nous approfondirons au chapitre 13) »*.

---

## 2. Étiquettes — les 76 encadrés relus un par un

Quarante-cinq changent d'étiquette, trente et un restent des exemples.

| Nouvelle étiquette | Nombre | Ce qu'elle recouvre |
|---|---:|---|
| **Correction** | 14 | les corrigés de la partie VII |
| **Méthode** | 12 | ce qui explique comment procéder |
| **Cas pratique** | 11 | les scénarios professionnels problème/solution |
| **Attention** | 5 | les mises en garde et les pièges |
| **Définition** | 2 | les énoncés de propriété |
| **Synthèse** | 1 | le récapitulatif de fin de chapitre 3 |

**Les corrigés étaient le cas le plus net.** Les quatorze solutions de la partie VII s'ouvraient toutes par `**Exemple --- correction.**`. Le mot « Exemple » y était purement parasite : *« Exemple — correction. La dérivée est f'(w) = 2(w − 4)… »* n'illustre rien, c'est la solution de l'exercice. Elles s'ouvrent désormais par `**Correction.**`.

**Sur les définitions, une nuance que j'avais déjà signalée au diagnostic.** Votre manuel possédait déjà une étiquette `Définition ---`, utilisée 18 fois, et les définitions canoniques étaient correctement étiquetées. Le vrai défaut n'était pas que « Exemple » remplaçait « Définition », mais qu'il servait de **fourre-tout** pour tout encadré n'étant ni une définition ni un exercice. D'où la répartition ci-dessus, dominée par « Méthode » et « Cas pratique » plutôt que par « Définition » — seuls deux encadrés énonçaient réellement une propriété (« le produit scalaire mesure la similarité », « ce que détecte un filtre »).

**Une étiquette hors de votre liste.** L'encadré « tout est lié » du chapitre 3 n'est ni une définition, ni une mise en garde, ni une méthode, ni un cas pratique : c'est un récapitulatif qui relie les quatre domaines mathématiques du chapitre. Je l'ai étiqueté **Synthèse**. C'est le seul écart aux quatre labels que vous proposiez ; un mot et je le ramène dans le rang.

**Ce qui reste « Exemple » l'est à bon droit** : les analogies (la métaphore du brouillard pour la descente de gradient, l'archer pour la rétropropagation), les cas particuliers chiffrés, les illustrations concrètes. Trente et un encadrés.

---

## 3. Collision de vocabulaire — réglée

Les 33 `**Leçon** :` employés au sens de « morale de l'exercice » sont devenus `**À retenir** :`. Les 156 titres `### Leçon N` sont intacts.

**Le mot « Leçon » ne désigne plus qu'une seule chose dans tout le manuel :** le niveau de titre. C'était l'enjeu — dès la génération de la table des matières, une recherche textuelle sur « Leçon » aurait capté les 33 morales.

**Un point de vigilance que je maintiens.** Le nouveau marqueur `**À retenir** :` cohabite avec les 80 encadrés `L'ESSENTIEL À RETENIR`. La proximité est voulue de votre part, et le point 6 y aide en faisant varier la forme des encadrés. Mais si à la relecture les deux vous paraissent se confondre, `**Ce qu'il faut en retenir** :` ou `**Morale** :` lèveraient l'ambiguïté sans rien changer d'autre.

---

## 4. Ponctuation — 82 cadratins ramenés à 41

Exactement la moitié, sur la base réelle expliquée plus haut.

**Onze incises converties en parenthèses ou en virgules** (22 cadratins). Ce sont les gains les plus nets, parce qu'une incise entre deux tirets est précisément ce qui alourdit une page :

> *« Il propose un test célèbre — aujourd'hui appelé test de Turing — où une machine… »*
> → *« Il propose un test célèbre (aujourd'hui appelé **test de Turing**) où une machine… »*

> *« L'apprentissage profond s'inspire — de loin — du cerveau. »*
> → *« L'apprentissage profond s'inspire, de loin, du cerveau. »*

**Dix-neuf ruptures converties en deux-points ou en virgule**, selon ce que la phrase demandait. Le deux-points quand ce qui suit explicite ou énumère (*« Le sens devient géométrie, une idée stupéfiante »*, *« peuvent halluciner : inventer des faits avec aplomb »*), la virgule quand il s'agit d'une apposition.

**Quatre familles n'ont pas été touchées, car le tiret y sépare bien un titre d'un sous-titre :** le tableau « Le chemin que nous allons suivre » (les 8 lignes `I — Les fondations`), les quatre paliers de maturité (`Palier 1 — Sensibilisation`), les six entrées de bibliographie (`Russell & Norvig — Artificial Intelligence`), et les commentaires de code du chapitre 2.

---

## 5. Dates figées — les quatre références à 2026 supprimées

| Avant | Après |
|---|---|
| `Leçon 1 --- Le visage de l'IA en 2026` | `Leçon 1 --- Le visage actuel de l'IA` |
| « L'année 2026 marque le passage des interfaces… » | « Le domaine est en train de passer des interfaces… » |
| « C'est la grande révolution de 2026. » | « C'est là que se joue la rupture. » |
| « Sa force en 2026 : il intègre nativement… » | « Sa force : il intègre nativement… » |

Plus aucune occurrence de « 2026 » dans le manuel.

**Les dates historiques sont conservées, et il faut qu'elles le soient** : Turing en 1950, la conférence de Dartmouth en 1956, AlexNet en 2012, le Transformer en 2017, l'essor de l'IA générative depuis 2022, le protocole MCP fin 2024. Ce sont des repères qui situent une évolution, pas des marqueurs de fraîcheur qui périment l'ouvrage.

**Un détail mineur laissé en l'état :** l'exemple SQL du chapitre 4 interroge `WHERE annee = 2025`. C'est une donnée d'illustration dans un extrait de code, pas une affirmation sur l'état du domaine. Dites-moi si vous préférez un millésime neutre.

---

## 6. Uniformité — la forme des encadrés varie, le contenu ne bouge pas

Trente-deux des 80 encadrés changent de forme.

| Forme | Avant | **Après** |
|---|---:|---:|
| Paragraphe court | 0 | **16** |
| Deux puces | 4 | **12** |
| Trois puces | 41 | **17** |
| Quatre puces | 12 | 12 |
| Cinq puces | 14 | 14 |
| Six puces | 5 | 5 |
| Sept puces | 4 | 4 |

**Le choix des encadrés convertis n'est pas arbitraire.** Je n'ai touché qu'aux encadrés à trois puces dont les puces sont des **phrases suivies**. Les neuf dont les puces forment des couples `**Terme** : définition` sont restés en puces : dans ce cas la puce est la forme juste, et la fondre en paragraphe aurait nui à la lecture. Exemple typiquement conservé — *« **IA faible (ou étroite)** : spécialisée dans une tâche précise… / **IA forte (ou générale)** : une intelligence comparable… »*.

**Le contenu est rigoureusement intact.** Je l'ai vérifié encadré par encadré, en comparant les textes normalisés avant et après : **zéro différence sur les 80**. Le décompte global de mots est identique au token près (29 391 avant, 29 391 après) ; seul `wc -w` bouge, parce qu'il comptait les tirets de puces comme des mots.

---

## 7. Contrôles

| Contrôle | Résultat |
|---|---|
| « ce cours » / « du programme » / « toute la formation » | **0** |
| Occurrences de « 2026 » | **0** |
| `**Leçon** :` employé comme morale | **0** |
| Titres `### Leçon N` intacts | **156** |
| `**Exemple --- correction`  | **0** (14 → `**Correction.**`) |
| Cadratins de corps de texte | 82 → **41** (−50 %) |
| Cadratins structurels préservés | **369** |
| Encadrés « L'ESSENTIEL À RETENIR » | **80**, contenu inchangé |
| Mots (tokens alphanumériques) | 29 391 → **29 391** |
| Conversion pandoc → `.docx` | **OK** |

---

## 8. Ce qui vous revient

**Trois arbitrages, tous réversibles d'un commit :**

1. **Les points 5 et 6** — dates figées et forme des encadrés — ne figuraient pas dans votre message. Si la troncature était volontaire, `git revert 6dcc8ec e2bd2d6` les annule sans toucher au reste.
2. **L'étiquette « Synthèse »**, seul écart à vos quatre labels.
3. **Le marqueur « À retenir »** et sa proximité avec « L'ESSENTIEL À RETENIR ».

**Et un point qui reste bloquant, hérité du prompt 2 :** les 17 images doivent être régénérées, sans numéro incrusté et à 300 dpi. Rien de ce que je fais sur le Markdown ne peut y suppléer.
