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

## État d'implémentation (PR-1)

Disponible :

- contrat de données **PatrimoineEvidence v0.1** ;
- modèles de preuve et de provenance ;
- collecte reproductible du CSV national Mérimée ;
- normalisation hors réseau des immeubles protégés de Haute-Garonne ;
- CLI `patri-risk version`, `diagnostic`, `merimee collecter`, `merimee normaliser`.

Non disponible, et non simulé :

- Géorisques, BDNB, INSEE et les autres sources ;
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

## Usage Mérimée (Haute-Garonne)

```bash
patri-risk merimee collecter
```

Puis, avec le snapshot et le manifeste produits :

```bash
patri-risk merimee normaliser \
  --departement 31 \
  --fichier donnees/brutes/merimee/<snapshot.csv>
```

Les artefacts runtime (CSV, JSONL) restent locaux et ne sont pas versionnés.
Voir [docs/merimee.md](docs/merimee.md).

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
- [Ingestion Mérimée](docs/merimee.md)

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

Séquencement révisable. PR-1 ingère Mérimée sans remettre en cause
le modèle de provenance.

## Licence

MIT. Voir [LICENSE](LICENSE).
