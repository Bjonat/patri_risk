# Architecture

Le projet distingue trois niveaux de données. Cette séparation est le
cœur de l'architecture : une donnée brute n'est pas une preuve, une
preuve n'est pas un indicateur.

## Flux cible

```text
sources publiques
       │
       ▼
adaptateurs de sources
       │
       ▼
données normalisées
       │
       ▼
preuves
       │
       ▼
dossier du monument
       │
       ├───────────────┐
       ▼               ▼
qualité des       indicateurs
données            dérivés
                       │
                       ▼
                priorisation future
```

## Périmètre réel de PR-0

```text
sources publiques
→ adaptateurs
→ données normalisées
→ preuves
→ dossier monument
```

Les adaptateurs et l'ingestion ne sont pas implémentés. Les paquets
`patri_risk.sources` et `patri_risk.modeles` existent pour que PR-1
puisse brancher Mérimée sans changer le modèle de provenance.

Les niveaux « qualité des données », « indicateurs dérivés » et
« priorisation » restent conceptuels. Aucun score n'est calculé.

## Couches

### A. Donnée source brute — `EnregistrementBrut`

Ce que la source a réellement retourné. Le contenu reste un dictionnaire
aussi proche que possible du payload original (ex. champs Mérimée
`REF`, `DENO`, `COM`).

### B. Preuve normalisée — `Preuve`

Observation factuelle, toujours liée à une `SourceDonnee`. Elle porte
le champ métier, la valeur, la méthode d'obtention et le niveau de
confiance.

### C. Indicateur dérivé

Information calculée à partir d'une ou plusieurs preuves (lacune
d'information, exposition externe, ancienneté de l'information,
activité de travaux, etc.). Non implémenté.

## Modèles de PR-0

| Modèle | Rôle |
| --- | --- |
| `SourceDonnee` | provenance d'une information |
| `EnregistrementBrut` | payload original d'une source |
| `Preuve` | observation normalisée et traçable |
| `IdentiteMonument` | clés de jointure et d'affichage, pas un diagnostic |
| `DossierMonument` | accumulation de preuves autour d'une identité |

`IdentiteMonument` est un index de travail. Les faits qu'il reprend
(nom, commune, coordonnées) doivent aussi pouvoir exister comme
`Preuve` lorsqu'ils proviennent d'une source. Le nom n'est jamais un
identifiant.

Un monument n'est pas supposé correspondre à un unique bâtiment
géométrique. Les correspondances spatiales futures devront conserver
leur `methode_obtention`.

## Ce que chaque preuve doit préserver

- identifiant original de la source ;
- date de collecte ;
- date d'observation lorsqu'elle existe ;
- producteur et jeu de données ;
- méthode de correspondance (`MethodeObtention`) ;
- niveau de confiance ;
- URL d'origine lorsque disponible.

Ces éléments rendent possible un audit ultérieur de toute conclusion.

## Décisions structurantes

1. **Français métier, anglais technique.** Les modèles, champs,
   messages CLI et tests métier sont en français. Les API Python restent
   inchangées.
2. **Pydantic v2, contrat explicite.** `extra="forbid"` pour détecter
   les champs inconnus. Les dates de collecte et d'observation sont
   des `datetime` avec fuseau (UTC).
3. **Pas de score dans le dossier.** `DossierMonument` ne contient que
   `identite` et `preuves`. Les indicateurs viendront plus tard, à
   partir des preuves, jamais à la place des preuves.
4. **`EnregistrementBrut` est ajouté** par rapport à la liste minimale
   des fichiers : PR-1 doit pouvoir conserver le payload Mérimée sans
   inventer une quatrième couche.
5. **CLI volontairement minimale.** `version` et `diagnostic`
   seulement. Aucune commande `analyser` tant qu'aucune analyse n'existe.
6. **Dépendances limitées.** Runtime : Pydantic v2. Outils : pytest et
   ruff. Pas de framework web, pas d'ORM, pas d'orchestrateur.
7. **`__main__.py`** permet `python -m patri_risk` en plus de la
   commande `patri-risk`.

## Emplacement des sources

Le paquet `src/patri_risk/sources/` est réservé aux adaptateurs. PR-1
devrait y ajouter un module Mérimée / POP qui :

1. récupère un enregistrement public ;
2. le stocke en `EnregistrementBrut` ;
3. produit des `SourceDonnee` et des `Preuve` ;
4. alimente un `DossierMonument`.

Aucune de ces étapes n'est exécutée dans PR-0.
