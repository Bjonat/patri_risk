# Patrimoine Evidence Engine

Moteur open source expérimental d'agrégation de preuves publiques
relatives aux monuments historiques français.

Nom du dépôt et du paquet Python : `patri_risk`.
Commande : `patri-risk`.

État du projet : **pré-v0.1**, expérimental.

Territoire initial : **Haute-Garonne**, département **31**.

## Ce que le projet n'est pas

- pas un outil de diagnostic ;
- pas un outil réglementaire ;
- pas une base officielle ;
- pas un outil de prédiction d'effondrement ;
- pas un substitut des DRAC, CRMH, UDAP ou d'AgrÉgée.

## Principe fondamental

**Aucune information dérivée sans preuve traçable.**

Le système relie chaque information importante à une source, un
producteur, un identifiant source, une date de collecte, une méthode
d'obtention et un niveau de confiance.

Une donnée absente signifie uniquement qu'aucune preuve correspondante
n'a été trouvée dans les sources interrogées par la version actuelle.
Elle ne signifie pas « aucun risque », « aucuns travaux » ou « bon état ».

## État d'implémentation (PR-0)

Disponible :

- contrat de données **PatrimoineEvidence v0.1** ;
- modèles `SourceDonnee`, `EnregistrementBrut`, `Preuve`,
  `IdentiteMonument`, `DossierMonument` ;
- CLI `patri-risk version` et `patri-risk diagnostic` ;
- tests unitaires hors ligne.

Non disponible, et non simulé :

- ingestion Mérimée / POP ;
- toute autre source (Géorisques, BDNB, INSEE, etc.) ;
- indicateur dérivé, score de risque, score de vulnérabilité ;
- application web, carte, API HTTP.

## Installation développement

Python 3.12 ou supérieur est requis.

```bash
python -m pip install -e ".[dev]"
```

Vérifier l'installation :

```bash
patri-risk version
patri-risk diagnostic
```

## Tests

```bash
python -m pytest
ruff check .
ruff format --check .
```

## Documentation

- [Vision](docs/vision.md)
- [Périmètre v0.1](docs/perimetre-v0.1.md)
- [Architecture](docs/architecture.md)
- [Contrat de données v0.1](docs/contrat-donnees-v0.1.md)
- [Registre des sources](docs/sources.md)

## Feuille de route

| PR | Objet |
| --- | --- |
| PR-0 | Fondation + contrat de données |
| PR-1 | Ingestion Mérimée / POP |
| PR-2 | Enrichissement Géorisques |
| PR-3 | Jeu de référence manuel / contrôle qualité |
| PR-4 | Signaux de travaux et d'investissement public |
| PR-5 | Indicateurs de lacune d'information |
| PR-6 | Expérimentation d'indicateurs de vulnérabilité externe |

Séquencement révisable. PR-1 devra pouvoir brancher Mérimée sur les
modèles de provenance et de preuve sans les remettre en cause.

## Licence

MIT. Voir [LICENSE](LICENSE).
