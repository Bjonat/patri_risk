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
identifiant. `reference` n'impose pas de motif `PA…` : ce contrôle
appartient à l'adaptateur de la source.

Les coordonnées normalisées sont en **WGS84 / EPSG:4326**
(`longitude`, `latitude`). Elles peuvent être absentes. Un monument
n'est pas supposé correspondre à un unique bâtiment géométrique. Les
correspondances spatiales futures devront conserver leur
`methode_obtention`.

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
   les champs inconnus. `date_collecte` est un instant timezone-aware
   normalisé UTC. `date_observation` et `date_mise_a_jour_source`
   acceptent une `date` ou un instant aware (`DateOuInstant`) afin de
   ne jamais inventer minuit UTC.
3. **Pas de score dans le dossier.** `DossierMonument` ne contient que
   `identite` et `preuves`. Les indicateurs viendront plus tard, à
   partir des preuves, jamais à la place des preuves.
4. **Données brutes hors dossier.** `EnregistrementBrut` existe pour
   représenter un payload original. Il n'est **pas** un champ de
   `DossierMonument`. À partir de PR-1, l'ingestion conservera
   séparément l'artefact source brut et un manifeste de collecte.
5. **CLI volontairement minimale.** `version` et `diagnostic`
   seulement. Aucune commande `analyser` tant qu'aucune analyse n'existe.
6. **Dépendances limitées.** Runtime : Pydantic v2. Outils : pytest et
   ruff. Pas de framework web, pas d'ORM, pas d'orchestrateur.
7. **`__main__.py`** permet `python -m patri_risk` en plus de la
   commande `patri-risk`.

## Conservation des artefacts bruts

`DossierMonument` reste :

```text
identité
+
preuves
```

Les artefacts sources bruts ne sont pas stockés dans le dossier. À
partir de PR-1, une ingestion devra conserver **séparément** :

```text
artefact source brut
+
manifeste de collecte
```

Le manifeste devra au minimum permettre de connaître :

```text
source
URL ou identifiant de ressource
date de collecte
empreinte SHA-256
taille en octets
licence lorsque connue
```

Une preuve pourra ainsi être auditée contre le snapshot exact utilisé
au moment du traitement. Ce mécanisme n'est pas implémenté dans PR-0.

## Emplacement des sources

Le paquet `src/patri_risk/sources/` est réservé aux adaptateurs. PR-1
devrait y ajouter un module Mérimée / POP qui :

1. récupère un enregistrement public ;
2. conserve l'artefact brut et son manifeste **en dehors** du dossier ;
3. produit des `SourceDonnee` et des `Preuve` ;
4. alimente un `DossierMonument` (identité + preuves uniquement).

Aucune de ces étapes n'est exécutée dans PR-0.

## Règles figées pour l'ingestion Mérimée (PR-1)

Ces règles ne sont pas encore implémentées. Elles sont figées pour
éviter de les ré-inventer dans PR-1.

### Référence

`IdentiteMonument.reference` reste une chaîne libre obligatoire. L'adaptateur
Mérimée contrôle le format attendu (`PA…`), mais une anomalie de
référence ne doit pas interrompre toute l'ingestion. Les
enregistrements anormaux devront pouvoir être comptés et signalés.

### Code commune

Pour Mérimée, le champ `Code Insee` est le candidat utilisé pour
`code_commune`.

Le champ `COG Insee lors de la protection` est une information
historique distincte. Il ne doit pas remplacer silencieusement le code
commune courant.

Si `Code Insee` est absent :

```python
code_commune = None
```

La résolution des communes anciennes, fusionnées ou renommées
viendra dans une phase ultérieure.

### Coordonnées

Les coordonnées de `IdentiteMonument` sont en WGS84 / EPSG:4326
(`longitude`, `latitude`). Elles peuvent être absentes.

PR-1 ne devra pas :

- géocoder automatiquement un monument absent ;
- corriger une localisation ;
- déduire des coordonnées depuis l'adresse ou la commune.

Une localisation manquante reste une information manquante.
