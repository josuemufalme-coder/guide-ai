# Consignes de travail — dépôt guide-ai

## Contexte

Ce dépôt sert deux chantiers de Josué MUFALME BULENDA, Chef Div Numérique à la Réserve
Armée de la Défense (RAD), Kinshasa :

1. **Correspondance officielle** — production de lettres officielles RAD à partir d'un
   modèle fourni par l'auteur (`modeles/`, `scripts/`, `lettres/`).
2. **Manuel d'IA** — reprise du *Guide Intelligence Artificielle*
   (`Procedure_Claude_Code_Guide_IA.md`). Le `.docx` du manuel n'est pas encore dans le
   dépôt.

## Correspondance officielle — la règle

Quand l'auteur envoie du texte et demande de le mettre « dans mon document officiel » :

1. **Ne jamais recréer le document.** Le modèle est reproduit octet pour octet et seul le
   texte est substitué. Lire `modeles/ANATOMIE.md` avant toute intervention sur la forme.
2. Écrire un fichier `lettres/<nom>.txt` au format décrit ci‑dessous.
3. Générer :
   ```bash
   python3 scripts/lettre.py lettres/<nom>.txt --texte
   ```
   L'option `--texte` affiche la lettre finale, numérotation comprise, pour relecture.
4. Contrôler :
   ```bash
   python3 /root/.claude/skills/docx/scripts/office/validate.py \
       lettres/<nom>.docx --original modeles/lettre_officielle_RAD.docx
   ```
   Doit répondre `All validations PASSED`.
5. Livrer le `.docx` à l'auteur, commiter le `.txt` et le `.docx`.

### Format du fichier d'entrée

```
OBJET: demande d'acquisition de trois onduleurs pour la salle serveurs
DESTINATAIRE: Au Dir AdmLog
DATE: 29 juillet 2026
NUMERO: 087
---
En effet, les coupures répétées de courant ont provoqué **deux arrêts brutaux** des
serveurs, avec un risque réel de corruption des données.

Le besoin minimal est de trois onduleurs de 3 kVA, soit :

- un onduleur pour le serveur de production ;
- un onduleur pour le serveur de sauvegarde ;
- un onduleur pour l'équipement réseau.

Je sollicite votre haute bienveillance pour l'approbation de cette acquisition.

Votre Aut trouve en Ann, le devis détaillé y relatif.
```

Champs reconnus : `OBJET` (obligatoire), `DESTINATAIRE`, `DATE`, `NUMERO`, `ANNEE`,
`OUVERTURE`, `CLOTURE`, `SIGNATAIRE`, `FONCTION`. Valeur `aucune` pour supprimer
l'ouverture ou la clôture. Balisage dans le corps : `**gras**`, `__souligné__`, `- puce`.

### Valeurs par défaut

| Champ | Défaut |
|---|---|
| `DESTINATAIRE` | `Au Dir AdmLog` |
| `DATE` | vide — portée à la main |
| `NUMERO` | vide — porté à la main |
| `ANNEE` | deux derniers chiffres de l'année courante |
| `OUVERTURE` | `Honneur de vous saluer et vous transmettre ce dont l’objet repris en marge.` |
| `CLOTURE` | `Profonds respects.` |
| `SIGNATAIRE` / `FONCTION` | `MUFALME BULENDA Josué` / `Chef Div Numérique` |

### Ce qui est automatique

- **Numérotation des paragraphes** (`1.`, `2.`, `3.` en gras) : gérée par Word via
  `numId 2`. Ne jamais écrire les numéros dans le texte.
- **Séparateurs** entre paragraphes : posés par le générateur, à l'identique du modèle
  (le premier, après la formule d'ouverture, est plus serré que les autres).
- **Typographie française** : apostrophe courbe, espace insécable avant `: ; ! ?` et dans
  `« … »`, points de suspension. Une heure du type `10:30` n'est pas touchée.

### Ce qu'il ne faut pas faire

- Ne pas modifier `modeles/lettre_officielle_RAD.docx` — c'est la référence de l'auteur.
- Ne pas reformuler le texte envoyé par l'auteur. Le respecter tel quel, sauf faute de
  frappe évidente, et signaler la correction.
- Ne pas régénérer le gabarit sans raison. Si c'est nécessaire :
  `python3 scripts/build_gabarit.py modeles/lettre_officielle_RAD.docx modeles`
- Ne pas inventer un numéro d'enregistrement ni une date : les laisser en blanc si
  l'auteur ne les donne pas.

## Limites de l'environnement

- `pandoc` n'est pas installé.
- LibreOffice est présent mais **hors service** (« source file could not be loaded » sur
  tout fichier) : pas de conversion PDF, donc pas de contrôle visuel par image. La
  vérification se fait par comparaison XML et validation XSD.
- `pdftoppm` absent. `defusedxml` et `lxml` s'installent avec `pip install`.

## Langue

Toute la production (documents, rapports, messages) est en **français**.
