# Contrat de données — PatrimoineEvidence v0.1

Version du contrat : **PatrimoineEvidence v0.1**.

Ce contrat définit la manière dont une information publique entre dans le
système, comment elle est reliée à un monument, et ce qu'il est interdit
d'en conclure. Les évolutions ultérieures devront changer ce numéro de
version.

Constante Python : `patri_risk.VERSION_CONTRAT_DONNEES`.

## 11.1 Donnée brute

La donnée brute est ce que la source a réellement retourné, sans
renommage métier ni inférence.

Exemple :

```json
{
  "REF": "PA00094321",
  "DENO": "Église",
  "COM": "Toulouse"
}
```

Modèle : `EnregistrementBrut`.

- `source` décrit la provenance de l'enregistrement.
- `contenu` conserve le payload original.

Cette couche ne doit pas être « nettoyée » au point de perdre
l'identifiant source, un champ vide signifiant, ou une valeur ambiguë.

## 11.2 Preuve

Une preuve est une observation factuelle normalisée, toujours reliée à
une `SourceDonnee`.

Exemple :

```json
{
  "champ": "statut_protection",
  "valeur": "classé",
  "source": {
    "producteur": "Ministère de la Culture",
    "jeu_donnees": "Mérimée",
    "identifiant_enregistrement": "PA00094321",
    "date_collecte": "2026-09-08T18:00:00Z"
  },
  "methode_obtention": "directe",
  "niveau_confiance": 1.0
}
```

Dans le modèle Python, `date_collecte` appartient à `SourceDonnee`,
pas à `Preuve`. `date_observation` appartient à `Preuve` et peut être
absente.

Une `Preuve` sans `SourceDonnee` est invalide.

## 11.3 Indicateur dérivé

Un indicateur dérivé est une information construite à partir d'une ou
plusieurs preuves. Exemples futurs : `lacune_information`,
`exposition_externe`, `anciennete_information`, `activite_travaux`.

PR-0 ne définit aucun calcul, aucun score et aucun modèle d'indicateur.
La place architecturale est réservée : un indicateur devra citer les
preuves utilisées.

## 11.4 Règles d'identité

L'identité de travail est `IdentiteMonument`.

| Champ | Règle |
| --- | --- |
| `reference` | obligatoire ; identifiant patrimonial principal. Le format n'est pas imposé par le modèle ; la validation d'un motif Mérimée `PA…` appartient à l'adaptateur |
| `nom` | optionnel ; jamais un identifiant |
| `nom_commune` | optionnel |
| `code_commune` | optionnel ; code commune INSEE courant lorsqu'il est connu ; jamais remplacé silencieusement par un code historique |
| `code_departement` | optionnel ; `"31"` pour la Haute-Garonne |
| `latitude` / `longitude` | optionnels ; WGS84 / EPSG:4326 ; renseignés ensemble ou absents tous les deux |

Principes :

- un monument peut avoir une localisation manquante ;
- une localisation manquante reste une information manquante : pas de géocodage, de correction ni de déduction depuis l'adresse ou la commune ;
- un monument ne correspond pas forcément à un unique bâtiment
  géométrique ;
- plusieurs preuves de sources distinctes peuvent coexister autour de
  la même `reference` via `DossierMonument` ;
- en cas de doute sur une jointure, la correspondance se traduit par
  une preuve de `methode_obtention` non directe et un
  `niveau_confiance` inférieur à 1, éventuellement des `notes`.

## 11.5 Provenance

Chaque preuve doit indiquer sa source. `SourceDonnee` porte :

- `producteur`
- `jeu_donnees`
- `identifiant_enregistrement` (si la source en fournit un)
- `url` (si une URL d'origine est connue)
- `date_collecte` (obligatoire)
- `licence` (si connue)
- `date_mise_a_jour_source` (si la source la déclare pour l'artefact collecté)
- `empreinte_artefact` (optionnel, format `sha256:<64 hex>` ; relie la preuve au snapshot)

L'absence d'URL n'autorise pas à inventer une URL. L'absence de licence
n'autorise pas à en déduire une. `empreinte_artefact` est une extension
additive de PatrimoineEvidence v0.1, introduite pour l'ingestion Mérimée.

L'absence d'URL n'autorise pas à inventer une URL. L'absence de licence
n'autorise pas à en déduire une.

## 11.6 Confiance

`niveau_confiance` est un nombre entre 0 et 1. Il décrit la confiance
dans **l'obtention et l'association** de la preuve au monument, pas
la « gravité » d'un aléa et pas la qualité patrimoniale de l'édifice.

Convention indicative de v0.1, non figée :

| Valeur | Signification |
| --- | --- |
| 1.0 | information obtenue directement depuis une source de référence |
| 0.9 | correspondance très forte |
| 0.7 | correspondance probable |
| 0.5 | information incertaine nécessitant vérification |
| < 0.5 | association faible ; à n'utiliser qu'avec des `notes` explicites |

Cette grille pourra être précisée lorsque les premières jointures
réelles (PR-1, PR-2) auront été observées. Elle n'est pas un barème
officiel.

## 11.7 Temporalité

Trois informations temporelles peuvent coexister. Elles ne sont pas
interchangeables et n'ont pas la même précision.

| Notion | Où | Sens | Précision |
| --- | --- | --- | --- |
| `date_collecte` | `SourceDonnee` | instant précis auquel patri_risk a collecté l'enregistrement | timezone-aware, normalisé UTC |
| `date_observation` | `Preuve` | date ou instant du fait, selon la précision réelle de la source | `date` ou instant aware, ou absente |
| `date_mise_a_jour_source` | `SourceDonnee` | date ou instant annoncé par la source | `date` ou instant aware, ou absente |

`date_collecte` est toujours un horodatage : le système sait réellement
quand il a obtenu la donnée.

`date_observation` et `date_mise_a_jour_source` conservent la
précision fournie. Une source qui ne connaît que le jour (ex.
`2025-01-14`) reste au niveau du jour. Une source qui fournit un
véritable timestamp conserve cet instant. Le type partagé
`DateOuInstant` formalise cette union.

> Le système ne doit jamais fabriquer une heure, un fuseau ou une
> précision temporelle absente de la source.

En particulier, une date civile ne doit jamais être transformée en
`2025-01-14T00:00:00Z`. Si la source ne donne pas la date du fait,
`date_observation` reste vide. On ne la remplit pas avec
`date_collecte`.

## 11.8 Données absentes

Une donnée absente ne doit **jamais** être transformée silencieusement
en :

- `0`
- aucun risque
- aucuns travaux
- aucun financement
- bon état
- aucun événement

L'absence de preuve signifie uniquement :

> aucune preuve correspondante n'a été trouvée dans les sources
> interrogées par la version actuelle du système.

Elle ne signifie pas que le fait n'existe pas. Elle ne signifie pas
que le monument est sans enjeu.

## 11.9 Correspondances futures

Certaines données seront reliées par :

- identifiant exact ;
- code INSEE ;
- coordonnées ;
- intersection spatiale ;
- correspondance textuelle ;
- heuristique ;
- combinaison de plusieurs signaux.

La méthode de correspondance est conservée dans
`methode_obtention` :

- `directe`
- `intersection_spatiale`
- `correspondance_exacte`
- `correspondance_approximative`
- `derivee`

`derivee` est réservée à une valeur obtenue par un calcul explicite à
partir d'autres preuves déjà tracées. Elle n'autorise pas une
inférence non documentée. Dans PR-0, aucun calcul dérivé n'est
produit.

## 11.10 Limites d'interprétation

Le système peut dire :

> aucune subvention correspondante n'a été retrouvée dans les sources
> interrogées.

Il ne peut pas dire :

> ce monument n'a reçu aucune subvention.

Le système peut dire :

> le monument est situé dans une zone exposée à tel aléa selon telle
> source.

Il ne peut pas automatiquement conclure :

> le monument est structurellement menacé.

Le système peut dire :

> la dernière preuve publique identifiée sur ce champ est ancienne.

Il ne peut pas dire :

> le monument est en bon état faute d'alerte récente.

Toute formulation qui transforme une preuve, une lacune ou un signal
en diagnostic structurel, en prédiction d'effondrement ou en score
officiel de risque est hors contrat.

## 11.11 Version du contrat

- Nom : **PatrimoineEvidence**
- Version : **v0.1**
- Introduite par : PR-0

Les PR suivantes devront indiquer si elles restent compatibles avec
v0.1 ou si elles introduisent v0.2 (nouveaux champs incompatibles,
changement de sémantique de la confiance, etc.). Un ajout de source
qui produit des preuves conformes à ce contrat n'exige pas, à lui
seul, un changement de version.
