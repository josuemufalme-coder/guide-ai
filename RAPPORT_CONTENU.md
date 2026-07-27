# RAPPORT — Contenu manquant (prompt 6)

**Commits :** `7023cac` → `9c00e98` (trois commits)

Deux des trois points comportaient une instruction explicite de **ne pas rédiger**. Je l'ai suivie : le manuel n'a reçu aucune ligne sur le droit congolais ni sur les études de cas locales. Vous trouverez à la place deux documents de travail à valider.

---

## 1. Panorama des outils — cinq acteurs ajoutés

Le chapitre 18 gagne une leçon 5, « Les autres acteurs qu'il faut connaître », traitant **Gemini, Copilot, Mistral, Llama et DeepSeek**. Pour chacun : positionnement, forces, cas d'usage privilégiés, points de vigilance.

**Aucun numéro de version, aucune performance chiffrée, aucun tarif** — vérifié automatiquement, zéro occurrence dans le chapitre. Le texte décrit des positionnements, qui bougent rarement, et non des produits, qui changent tous les quelques mois.

| Acteur | Positionnement retenu | Point de vigilance principal |
|---|---|---|
| Gemini | l'assistant intégré à une suite bureautique | l'intégration profonde est aussi un enfermement |
| Copilot | l'assistant du développeur, dans le contexte du projet | produit du code *plausible*, pas *correct* |
| Mistral | l'acteur européen, poids ouverts et hébergement maîtrisé | « poids ouverts » n'est pas une licence libre |
| Llama | la famille ouverte de référence, écosystème considérable | un modèle brut n'est pas un produit |
| DeepSeek | la pression sur les coûts, gamme partiellement ouverte | la **juridiction** sous laquelle vos données sont traitées |

Deux points de vigilance que je tenais à faire figurer parce qu'ils sont rarement dits : la question de la juridiction, et le fait qu'une licence « poids ouverts » restreint parfois l'usage commercial.

La leçon se termine par une grille de **quatre questions destinée à survivre à ce panorama** : où vont mes données, quel coût à mon volume réel, l'outil arrive-t-il là où je travaille déjà, puis-je en changer.

**Deux effets de bord.** Le chapitre passe de 7 à 8 leçons ; les leçons 5 à 7 ont été renumérotées 6 à 8, contrôle global effectué, aucune anomalie sur les 157 leçons. Et la figure 18.1, qui montrait quatre assistants dont Gemini alors que le texte n'en traitait que trois, est enfin cohérente avec son chapitre.

**Un point que je vous laisse trancher.** Le titre du chapitre reste « Maîtriser les assistants IA : ChatGPT, Claude, Perplexity », alors qu'il en couvre maintenant huit. Je ne l'ai pas modifié : vous m'aviez demandé au prompt 2 de conserver les intitulés exactement, et un titre est votre voix. « Maîtriser les assistants IA » tout court réglerait la question.

---

## 2. Ancrage local — deux livrables, rien dans le manuel

### `ANCRAGE_LOCAL_1_QUESTIONS_JURIDIQUES.md`

**28 questions précises**, réparties en sept thèmes : texte-cadre, données personnelles, autorité de régulation, commerce électronique, cybersécurité, secteurs régulés, cadre régional. Chacune accompagnée de la piste de texte à vérifier au *Journal officiel* et de la forme de réponse dont j'ai besoin.

**Les pistes sont présentées comme des hypothèses de recherche, jamais comme des références établies.** Je ne peux vérifier aucun texte congolais depuis cet environnement — le réseau sortant y est filtré par politique — et une référence législative inexacte dans un manuel universitaire est exactement la faute lourde que votre propre procédure signale.

Deux questions que je signale comme prioritaires :

- **Le transfert de données hors du territoire** (question B4). Tout le chapitre 20 décrit des automatisations qui envoient des données à des services hébergés à l'étranger. Si le droit congolais l'encadre, cela change concrètement ce qu'un lecteur a le droit de construire.
- **La portée du droit européen pour une entreprise congolaise** (question G3). Le manuel présente aujourd'hui le cadre européen comme s'il était le cadre par défaut. Un lecteur doit savoir en une phrase quand il le concerne.

### `ANCRAGE_LOCAL_2_CAS_A_CHOISIR.md`

**16 cas proposés**, génériques et anonymes, répartis entre PME de Kinshasa (4), administration publique (4), banque locale (4) et opérateur de télécommunications (4), plus trois cas transversaux. Pour chacun : chapitre de destination, ce qu'il illustre, et les ordres de grandeur que vous seul pouvez fournir.

**Je recommande un jeu resserré de six cas** : score de crédit sans historique bancaire (C2), langues nationales (D3), tri de dossiers d'aide traité en contre-exemple (B3), commandes par messagerie (A1), connectivité contrainte (D4), architecture sous contrainte (E1).

Ils ont un point commun qui me paraît décisif : **chacun révèle une limite que le cadrage habituel ne fait pas voir**. Un manuel qui ajouterait seulement des noms de villes à des cas européens n'aurait rien ancré du tout.

Le plus fort est le C2. Le chapitre 14 explique qu'un modèle entraîné sur des décisions passées reproduit leurs biais. Le cas congolais rend la leçon bien plus tranchante : si l'historique de crédit ne couvre qu'une fraction de la population, un score appris dessus **exclura structurellement** ceux qui n'y figurent pas, quelle que soit leur solvabilité. C'est un enseignement que le cadrage européen ne fait pas apparaître.

### Une lacune repérée au passage, hors des deux listes

Aucun chapitre ne dit que ces outils sont **inégalement performants selon les langues**, et que le lingala, le swahili, le tshiluba et le kikongo sont bien moins couverts que le français, faute de textes disponibles pour l'entraînement. Un lecteur congolais a besoin de le savoir avant de bâtir quoi que ce soit. Que vous reteniez ou non le cas D3, je vous recommande un paragraphe sur ce point au chapitre 9.

---

## 3. Appareil critique — bibliographie reconstruite

La bibliographie passe de six lignes sans date ni éditeur à une section structurée.

| | Avant | Après |
|---|---:|---:|
| Ouvrages, avec année, édition, éditeur | 0 | **6** |
| Articles scientifiques référencés | 0 | **19** |
| Renvois insérés dans le corps du texte | 0 | **7** |

Les 19 articles sont classés par thème — origines, recherche, apprentissage automatique, apprentissage profond, langage et IA générative, éthique — avec revue, volume, pagination, et DOI ou identifiant arXiv. Chacun porte en retour **le chapitre et la leçon d'où il est cité**, pour que le lecteur puisse faire le trajet dans les deux sens.

Sept renvois ont été insérés aux endroits exacts où les travaux sont évoqués : Turing 1950 et McCarthy 1955 au chapitre 1, Krizhevsky 2012 pour AlexNet, Rumelhart 1986 pour la rétropropagation, Vaswani 2017 pour le Transformer, Lewis 2020 pour le RAG, Wei 2022 pour la chaîne de pensée.

### Sur les ISBN — je ne les ai pas mis, et voici pourquoi

Vous les demandiez, et je préfère m'en expliquer plutôt qu'inscrire des chiffres approximatifs.

Un ISBN est propre à **une édition et à un format donnés** : le même ouvrage en relié, en broché et en version électronique porte trois identifiants différents, et une nouvelle édition en crée un quatrième. Je ne peux vérifier aucun de ces numéros depuis cet environnement. Et un ISBN erroné renvoie le lecteur vers un ouvrage **qui n'est pas celui que vous citez** — c'est pire que pas d'ISBN du tout, parce que l'erreur est invisible.

La section explique donc au lecteur la marche à suivre, et vous n'avez qu'à relever les numéros sur les exemplaires que vous citez réellement, ou dans le catalogue des éditeurs. Six numéros à saisir.

---

## Ce qui reste

- **Vos réponses** au questionnaire juridique et **votre choix** parmi les seize cas. Ce sont les deux seules choses qui bloquent l'ancrage local.
- **Six ISBN** à relever.
- **Le titre du chapitre 18**, à trancher.
- **Les 5 extraits de code d'origine**, toujours en texte échappé, à reprendre au prompt 7.
- **Les 17 images** : numéro incrusté, 185 dpi. Inchangé depuis le prompt 2, et toujours le seul travail qui doit se faire hors de ce dépôt.
