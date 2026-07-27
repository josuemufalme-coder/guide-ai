# Reprise du manuel d'IA avec Claude Code — procédure et prompts

**Principe de travail :** on ne modifie jamais le `.docx` directement. On le convertit en Markdown, qui devient la source de vérité, on travaille dessus avec Git, et on régénère un `.docx` propre à la fin. C'est plus sûr, réversible, et ça permet de tout relire.

**Règle absolue :** un prompt à la fois. Tu lis le rapport, tu valides, tu passes au suivant. Ne colle jamais deux phases d'un coup.

---

## Phase 0 — Préparation (5 minutes, à faire toi-même)

1. Crée un dossier de travail, par exemple `guide-ia`.
2. Copie `Guide_Intelligence_Artificielle.docx` dedans.
3. **Fais une copie de sauvegarde du fichier ailleurs**, hors du dossier. Si quelque chose tourne mal, c'est ton filet.
4. Ouvre un terminal dans ce dossier et lance Claude Code.

Prérequis techniques : Node.js installé, et `pandoc` disponible. Si `pandoc` manque, Claude Code te le dira au prompt 1 — laisse-le t'indiquer la commande d'installation.

---

## Prompt 1 — Mise en place et diagnostic

> Je travaille sur un manuel de formation en intelligence artificielle en français, `Guide_Intelligence_Artificielle.docx` (environ 29 000 mots, 8 parties, 24 chapitres, 156 leçons, 17 images). J'en suis l'auteur et je veux le porter à un niveau publiable et enseignable en université.
>
> Pour cette première étape, **ne modifie rien**. Fais uniquement ceci :
>
> 1. Initialise un dépôt Git et fais un premier commit avec le `.docx` d'origine intact.
> 2. Convertis le document en Markdown avec `pandoc`, en extrayant les images dans un dossier `media/`. Le fichier Markdown devient notre source de travail.
> 3. Décompresse le `.docx` dans un dossier temporaire et analyse `word/document.xml`.
> 4. Produis un rapport `DIAGNOSTIC.md` qui confirme ou infirme chacun des points suivants, avec les preuves :
>    - aucun style de titre n'est utilisé (seulement `ListBullet` et `ListNumber`) ;
>    - aucune table des matières, aucun pied de page, aucun numéro de page, une seule section ;
>    - numérotation cassée : une « Leçon 4bis » sans leçon 4 dans le chapitre sur l'apprentissage par renforcement, une « Leçon 9bis » sans leçon 9 dans le chapitre sur n8n, une leçon 4 manquante dans le chapitre sur la gestion de projets ;
>    - la « Figure 2.1 » n'existe pas alors que les figures 2.2 et 2.3 existent ;
>    - les 24 chapitres ne portent aucun numéro ;
>    - le marqueur `**Leçon** :` est utilisé au sens de « morale de l'exercice » et entre en collision avec le niveau de titre « Leçon N » ;
>    - « ce cours » apparaît une douzaine de fois dans un document qui se présente comme un livre ;
>    - l'étiquette « Exemple — » est employée pour des corrections d'exercices et des définitions ;
>    - la résolution des images est d'environ 190 dpi, en dessous du standard d'impression de 300 dpi.
> 5. Ajoute au rapport un tableau de toutes les leçons avec leur nombre de mots, trié du plus court au plus long.
>
> Ne corrige rien pour l'instant. Présente-moi le rapport et attends ma validation.

---

## Prompt 2 — Structure et numérotation

> Diagnostic validé. Travaille maintenant sur le fichier Markdown, et commite après chaque groupe de corrections.
>
> 1. **Hiérarchie.** Applique un niveau de titre Markdown cohérent : `#` pour les 8 parties, `##` pour les 24 chapitres, `###` pour les leçons. Aucun titre ne doit rester en simple gras.
> 2. **Numérotation des chapitres.** Numérote les 24 chapitres de 1 à 24, en continu à travers les parties. Conserve **exactement** les intitulés existants, sans les reformuler.
> 3. **Numérotation des leçons.** Corrige les trois anomalies : supprime les suffixes « bis » et renumérote les leçons de chaque chapitre en séquence continue à partir de 1.
> 4. **Figures.** Renumérote toutes les figures selon le schéma `Figure <numéro de chapitre>.<numéro d'ordre>`, en séquence continue. Vérifie que chaque légende correspond bien à l'image qui la précède, et signale-moi tout décalage.
> 5. **Renvois internes.** Repère toute mention d'un chapitre, d'une leçon ou d'une figure dans le corps du texte et mets-la à jour. Liste-moi les renvois que tu n'as pas su résoudre.
>
> Produis un rapport des modifications avant de commiter.

---

## Prompt 3 — Cohérence éditoriale

> Le document oscille entre un livre et une fiche descriptive de cours. Corrige cela.
>
> 1. **Registre.** Remplace chaque occurrence de « ce cours » par « ce chapitre », « ce manuel » ou une reformulation selon le contexte. Traite de la même manière les tournures de catalogue de formation, du type « Vous étudierez aussi… », « Le cours aborde… », « Ce cours vous apprend… ». Le document doit parler d'une seule voix, celle d'un auteur qui s'adresse à son lecteur.
> 2. **Étiquettes.** Dans la partie sur les exercices, renomme tous les encadrés « Exemple — correction » en « Correction ». Ailleurs, chaque encadré « Exemple — » qui n'introduit pas un exemple doit recevoir l'étiquette juste : « Définition », « Attention », « Méthode », « Cas pratique ».
> 3. **Collision de vocabulaire.** Remplace le marqueur `**Leçon** :` employé au sens de « morale de l'exercice » par `**À retenir** :`.
> 4. **Ponctuation.** Le document contient environ 705 tirets cadratins pour 29 000 mots, soit un tous les 41 mots. Réduis-les d'environ moitié, en les remplaçant par des virgules, des deux-points ou des parenthèses selon ce que la phrase demande. Ne touche pas aux tirets qui séparent un titre de son sous-titre.
> 5. **Dates figées.** Supprime toutes les formulations qui datent le manuel : « le visage de l'IA en 2026 », « la grande révolution de 2026 », « l'année 2026 marque… ». Reformule au présent intemporel ou en termes d'évolution.
> 6. **Uniformité mécanique.** Le manuel contient 80 encadrés « L'ESSENTIEL À RETENIR » strictement identiques, toujours composés de trois puces. Fais varier leur forme : certains en trois puces, d'autres en deux, d'autres en un court paragraphe. Ne change pas leur contenu, seulement leur forme.
>
> Rapport avant commit.

---

## Prompt 4 — Densification (la phase la plus longue)

> C'est la phase de fond. Elle ne se fait pas en une fois : procède **chapitre par chapitre**, dans l'ordre, et arrête-toi après chaque chapitre pour que je valide.
>
> Contexte : la médiane est de 125 mots par leçon, et une douzaine de leçons font moins de 50 mots. Ce sont des accroches, pas des leçons.
>
> Pour chaque chapitre, dans l'ordre :
>
> 1. Liste-moi ses leçons avec leur nombre de mots.
> 2. Propose un plan d'extension pour celles qui sont sous 200 mots : ce qui manque, ce qu'il faut ajouter, et pourquoi.
> 3. Une fois que j'ai validé le plan, rédige les extensions. **Cible : 350 à 600 mots par leçon**, avec des longueurs volontairement inégales selon la richesse du sujet.
> 4. Ajoute au moins un exemple chiffré traité en entier par chapitre, quand la matière s'y prête.
>
> Contraintes de rédaction, valables partout :
> - conserve la première personne et le ton direct de l'auteur ;
> - ne reformule jamais un passage déjà écrit à la première personne ;
> - pas de formules de remplissage : chaque paragraphe ajouté doit apporter une information, un exemple ou un raisonnement ;
> - si une affirmation factuelle t'est nécessaire et que tu ne peux pas la vérifier, signale-la-moi au lieu de l'écrire.

---

## Prompt 5 — Code, projets et exercices

> Le manuel prétend enseigner Python, NumPy, Pandas, scikit-learn et l'apprentissage profond, mais ne contient que cinq extraits de code. Et les quatre « projets guidés pas à pas » de la partie VI ne contiennent aucune ligne de code, aucun jeu de données nommé et aucun résultat attendu.
>
> 1. **Projets.** Reprends les quatre projets un par un. Pour chacun : nomme un jeu de données public avec sa source et son URL, écris le code Python complet, commenté en français, étape par étape, indique les résultats attendus (ordres de grandeur des métriques), et ajoute une section « ce qui peut mal se passer ». Le code doit être exécutable tel quel.
> 2. **Vérification.** Crée un dossier `code/`, place-y chaque script, et **exécute-les** pour vérifier qu'ils tournent. Rapporte-moi toute erreur.
> 3. **Code dans les chapitres.** Ajoute des extraits courts et commentés dans les chapitres qui en manquent : Python, mathématiques, données, apprentissage supervisé, réseaux de neurones, langage, IA générative.
> 4. **Exercices.** Le manuel n'a que 14 exercices pour 24 chapitres. Porte-les à au moins 60, répartis par chapitre, avec trois niveaux de difficulté. **Déplace tous les corrigés dans une annexe séparée**, en fin d'ouvrage, avec renvoi depuis l'énoncé.
>
> Procède en quatre commits distincts, un par point.

---

## Prompt 6 — Contenu manquant

> Trois lacunes de fond à combler.
>
> 1. **Panorama des outils incomplet.** Le chapitre sur les assistants ne traite que ChatGPT, Claude et Perplexity. Ajoute au minimum Gemini, Copilot, Mistral, Llama et DeepSeek, avec pour chacun : positionnement, forces, cas d'usage privilégiés, points de vigilance. Reste sur les caractéristiques durables et évite les numéros de version, qui se périment.
> 2. **Ancrage local.** Le manuel ne mentionne ni la République démocratique du Congo, ni l'Afrique, dans ses 29 000 mots. Le seul cadre réglementaire traité est européen. Ajoute :
>    - une section sur le cadre juridique congolais du numérique dans le chapitre sur l'éthique et la régulation. **Ne rédige pas cette section toi-même** : produis-moi une liste de questions précises et les références à vérifier au Journal officiel, je te fournirai le contenu ;
>    - des exemples et études de cas situés dans le contexte congolais — une PME de Kinshasa, une administration publique, une banque locale, un opérateur de télécommunications. Cas génériques et anonymes, sans nommer d'organisation réelle. Propose-les-moi d'abord sous forme de liste, je choisirai.
> 3. **Appareil critique.** La bibliographie ne comporte ni année, ni éditeur, ni ISBN, et aucun article scientifique n'est référencé alors que Turing, AlexNet et le Transformer sont cités dans le texte. Reconstruis une bibliographie complète et normée, et ajoute les renvois aux articles fondateurs aux endroits du texte où ils sont évoqués.

---

## Prompt 7 — Reconstruction du document final

> Dernière phase : produire le `.docx` publiable.
>
> 1. **Modèle de style.** Crée un `reference.docx` définissant les styles : titres de partie, de chapitre et de leçon, corps de texte, encadrés, légendes de figures, blocs de code. Sobre et académique. Police avec empattements pour les titres, sans empattements pour le corps.
> 2. **Pages liminaires.** Ajoute avant le corps : page de titre, page de droits (auteur, édition, année, version, mention de dépôt légal et emplacement pour l'ISBN), avant-propos existant, puis une **table des matières générée automatiquement**.
> 3. **Annexes.** Vérifie l'ordre de fin : corrigés des exercices, glossaire, bibliographie, index des figures.
> 4. **Génération.** Écris un script de compilation `build.sh` qui régénère le `.docx` depuis le Markdown avec `pandoc`, en appliquant `reference.docx`, la table des matières et les images. Le script doit être rejouable à volonté.
> 5. **Pagination.** Vérifie que le document final a bien des numéros de page en pied de page et des sections distinctes pour les pages liminaires.
> 6. **Contrôle visuel.** Convertis le résultat en PDF, rasterise les pages en images et **regarde-les**. Signale-moi tout défaut : titre orphelin en bas de page, image mal cadrée, tableau coupé, légende séparée de sa figure.
> 7. **Rapport final.** Produis un `RAPPORT_FINAL.md` : nombre de mots avant et après, nombre de leçons étendues, nombre d'exercices, nombre d'extraits de code, liste des points que tu n'as pas pu vérifier et qui exigent ma relecture.

---

## Ce que Claude Code ne peut pas faire à ta place

- **Le contenu juridique congolais.** À vérifier au Journal officiel. Une référence de loi inexacte dans un manuel universitaire est une faute lourde.
- **Les études de cas locales.** Il peut proposer des trames ; la matière doit venir de toi. C'est précisément ce qui distinguera ton manuel de n'importe quelle production automatique.
- **La relecture finale.** Aucun outil ne remplace une lecture intégrale par l'auteur, stylo en main. Compte deux à trois jours.
- **Le dépôt légal.** À faire avant toute diffusion, y compris avant de montrer le manuscrit à une université.

## Ordre de grandeur

Les phases 1 à 3 et 7 sont rapides — quelques heures au total. La phase 4 est le gros du travail : compte plusieurs sessions étalées sur des jours, chapitre par chapitre. Ne cherche pas à l'accélérer, c'est elle qui fait la différence entre un plan bien écrit et un manuel.
