# Études de cas congolaises — propositions à choisir

**Destination :** répartis dans les chapitres 15, 16, 20, 21 et 23, à côté des cas existants et non à leur place.

**Pourquoi ce document.** Vous m'avez demandé de vous proposer ces cas sous forme de liste avant de les écrire, et de rester sur des cas génériques et anonymes. Voici seize propositions. **Cochez celles que vous retenez**, corrigez ce qui sonne faux, et je les rédigerai.

**Ce que je ne peux pas faire seul.** Chaque cas a besoin de chiffres pour valoir quelque chose — un volume, un délai, un coût. Je peux construire la structure et le raisonnement ; **les ordres de grandeur doivent venir de vous**, parce que je n'ai aucun moyen de les vérifier et qu'un chiffre inventé dans un manuel se retourne contre son auteur. Chaque fiche indique donc précisément ce dont j'ai besoin.

**Règles que je respecterai** : aucune organisation nommée, aucun secteur si étroit qu'il rende une organisation identifiable, aucun chiffre que vous n'aurez pas fourni ou validé.

---

## A. PME de Kinshasa

| # | Cas proposé | Chapitre | Ce qu'il illustre | Ce dont j'ai besoin de vous |
|---:|---|---|---|---|
| **A1** | Une PME de distribution reçoit ses commandes par messagerie instantanée et les recopie à la main dans un tableur | 20 | Le candidat idéal à l'automatisation : répétitif, fréquent, faible risque. Et le fait que le canal d'entrée n'est pas toujours le courriel | Volume quotidien de commandes, temps de saisie unitaire |
| **A2** | Un commerce tient son stock sur un cahier et sur un tableur qui divergent | 4 | Que la qualité des données précède tout projet d'IA, et qu'il faut parfois commencer par ne rien automatiser | Nature des écarts constatés, fréquence |
| **A3** | Une PME veut un assistant qui réponde aux questions de ses clients sur ses produits | 10, 24 | Un RAG à l'échelle d'une petite structure : quelques dizaines de fiches suffisent | Nombre de fiches produit, types de questions reçues |
| **A4** | Un artisan facture à la main et perd du temps au recouvrement | 22 | L'IA comme gain de temps administratif, sans modèle prédictif | Nombre de factures mensuel, délai de paiement moyen |

## B. Administration publique

| # | Cas proposé | Chapitre | Ce qu'il illustre | Ce dont j'ai besoin de vous |
|---:|---|---|---|---|
| **B1** | Un service traite des demandes d'acte administratif déposées sur formulaire papier | 20 | La lecture automatique de documents, et surtout la limite : l'écriture manuscrite et la qualité des scans | Volume mensuel, délai actuel de traitement |
| **B2** | Une administration veut orienter automatiquement les demandes vers le bon service | 20, 23 | Le routage par classification, avec sortie de boucle obligatoire pour l'usager | Nombre de services destinataires, volume |
| **B3** | Un service public envisage un tri automatique de dossiers de candidature à une aide | 14 | **Le cas où il faut dire non**, ou du moins encadrer très strictement : décision affectant l'accès à un droit | Nature de l'aide, volume, critères actuels |
| **B4** | Une administration souhaite un assistant interne pour ses agents sur les procédures | 24 | La différence entre outiller les agents et automatiser la décision | Volume documentaire, fréquence de mise à jour |

**Sur B3, une remarque.** C'est le cas le plus instructif de la liste et le plus délicat. Il permet de montrer, sur un exemple congolais, ce que le chapitre 14 énonce en général : une décision qui conditionne l'accès à un droit appelle documentation, mesure des biais et supervision humaine effective. Je vous recommande de le retenir, en le traitant comme un **contre-exemple** — ce qu'il ne faut pas faire, et pourquoi.

## C. Banque locale

| # | Cas proposé | Chapitre | Ce qu'il illustre | Ce dont j'ai besoin de vous |
|---:|---|---|---|---|
| **C1** | Une banque veut détecter les opérations suspectes sur les transactions par téléphone mobile | 5, 7 | La matrice de confusion en situation réelle, et le coût des fausses alertes en heures d'analystes | Volume quotidien d'opérations, effectif du service conformité |
| **C2** | Une banque envisage un score de crédit pour une clientèle largement sans historique bancaire formel | 14 | **Le meilleur cas de tout ce document** : que faire quand les données historiques n'existent pas, et le risque d'exclure ceux qu'on prétend inclure | Part de la clientèle sans historique, critères actuels d'octroi |
| **C3** | Un établissement veut un assistant pour ses conseillers en agence, sur les produits et procédures | 24 | Un assistant interne dans un secteur régulé : traçabilité et validation humaine | Nombre d'agences, volume documentaire |
| **C4** | Une banque traite les réclamations par courriel avec des délais qui s'allongent | 20, 23 | Le tri intelligent du chapitre 20 appliqué à un contexte contraint en personnel | Volume mensuel, délai actuel |

**Sur C2, pourquoi j'y tiens.** Le manuel explique au chapitre 14 qu'un modèle entraîné sur des décisions passées reproduit les biais de ces décisions. Le cas congolais rend cette leçon beaucoup plus forte : si l'historique de crédit ne couvre qu'une fraction de la population, un score appris dessus **exclura structurellement** ceux qui n'y figurent pas, quelle que soit leur solvabilité réelle. C'est un enseignement que le cadrage européen habituel ne fait pas apparaître, et il justifie à lui seul l'ancrage local que vous demandez.

## D. Opérateur de télécommunications

| # | Cas proposé | Chapitre | Ce qu'il illustre | Ce dont j'ai besoin de vous |
|---:|---|---|---|---|
| **D1** | Un opérateur veut anticiper les pannes de ses sites relais | 16 | La maintenance prédictive du chapitre 16, avec la contrainte de l'accès physique aux sites | Nombre de sites, fréquence de panne, coût d'intervention |
| **D2** | Un opérateur veut réduire le départ de ses abonnés prépayés | 15 | Le calcul de rentabilité du chapitre 15, avec une marge par abonné très différente du cas européen | Marge mensuelle par abonné, taux de départ |
| **D3** | Un service client reçoit des messages en plusieurs langues nationales | 9 | **La limite la plus honnête du manuel** : les modèles sont inégalement performants selon les langues | Langues concernées, part de chacune dans le volume |
| **D4** | Un opérateur veut déployer un assistant dans un contexte de connectivité irrégulière et coûteuse | 13, 18 | Pourquoi un modèle exécuté localement peut l'emporter sur un service hébergé, indépendamment de ses performances brutes | Contraintes de connectivité et de coût rencontrées |

**Sur D3, une remarque de fond.** Aucun chapitre du manuel ne dit aujourd'hui que ces outils fonctionnent mieux en anglais et en français qu'en lingala, en swahili, en tshiluba ou en kikongo, et que cet écart tient à la quantité de textes disponibles pour l'entraînement. C'est une information dont un lecteur congolais a besoin avant de bâtir quoi que ce soit, et elle manque. Que vous reteniez ou non ce cas, je vous recommande d'ajouter au moins un paragraphe sur ce point au chapitre 9.

---

## Trois cas transversaux, si vous voulez aller plus loin

| # | Cas proposé | Chapitre | Ce qu'il illustre |
|---:|---|---|---|
| **E1** | Une organisation dispose d'une connectivité intermittente et d'un coût de données élevé | 7, 20 | Que l'architecture d'un système dépend de contraintes que les manuels supposent absentes : traitement par lot plutôt que temps réel, modèle local plutôt que service distant |
| **E2** | Une équipe technique de trois personnes veut mettre un modèle en production | 7, 21 | Le MLOps à petite échelle : ce qui est indispensable et ce qui peut attendre |
| **E3** | Une organisation ne trouve pas les compétences qu'elle cherche sur le marché local | 21 | La leçon 7 du chapitre 21 appliquée : former en interne plutôt que recruter, et pourquoi c'est souvent le meilleur choix |

---

## Ma recommandation, si vous voulez un jeu resserré

Six cas suffisent à transformer le manuel, et je choisirais ceux-ci : **C2** (score de crédit sans historique), **D3** (langues nationales), **B3** (tri de dossiers d'aide, en contre-exemple), **A1** (commandes par messagerie), **D4** (connectivité contrainte) et **E1** (architecture sous contrainte).

Ils ont un point commun qui me paraît décisif : **chacun révèle une limite que le cadrage habituel ne fait pas voir**. Un manuel qui ajouterait seulement des noms de villes à des cas européens n'aurait rien ancré du tout. Ceux-là changent les conclusions, pas le décor.

---

## Comment nous procéderons

1. Vous cochez les cas retenus et corrigez ce qui sonne faux.
2. Vous me fournissez les ordres de grandeur demandés, même approximatifs — dites-moi simplement lesquels sont estimés, je les présenterai comme tels.
3. Je rédige chaque cas dans la forme du manuel : encadré « Cas pratique », 150 à 250 mots, situation, ce qu'on tente, ce qui coince, ce qu'on en retient.
4. Vous relisez avant que je commite.

**Un point que je ne trancherai pas seul.** Faut-il que ces cas soient explicitement situés — « une PME de Kinshasa » — ou décrits sans localisation ? Les nommer ancre l'ouvrage et parle à votre lecteur ; les laisser génériques élargit l'audience. Je penche pour les nommer, puisque c'est précisément ce que vous cherchez, mais c'est votre livre.
