# Périmètre v0.1

Territoire expérimental : **Haute-Garonne**, département **31**.

Premier type de patrimoine : **immeubles protégés au titre des monuments
historiques**.

Première source patrimoniale de référence : **Ministère de la Culture /
POP / Mérimée**.

L'ingestion Mérimée n'est pas livrée dans PR-0. Elle est l'objet de
PR-1.

## Inclus

- département 31 ;
- Haute-Garonne ;
- immeubles protégés au titre des monuments historiques ;
- données publiques ;
- données ouvertes lorsque disponibles ;
- ingestion reproductible (à partir de PR-1) ;
- provenance ;
- pipeline de données (contrat et modèles dès PR-0) ;
- CLI minimale ;
- tests automatisés hors ligne.

## Exclus

- objets mobiliers ;
- patrimoine non protégé ;
- déploiement national ;
- prédiction du risque ;
- diagnostic structurel ;
- imagerie ;
- reconnaissance d'images ;
- LLM et intelligence artificielle générative ;
- application web ;
- carte interactive ;
- serveur API ;
- ingestion Géorisques, BDNB, données financières, marchés publics ou
  subventions ;
- infrastructure distribuée ;
- Docker, sauf justification technique réelle ultérieure.

## Feuille de route provisoire

Ce séquencement reste révisable.

| PR | Objet |
| --- | --- |
| PR-0 | Fondation + contrat de données |
| PR-1 | Ingestion Mérimée / POP |
| PR-2 | Enrichissement Géorisques |
| PR-3 | Jeu de référence manuel / contrôle qualité |
| PR-4 | Signaux de travaux et d'investissement public |
| PR-5 | Indicateurs de lacune d'information |
| PR-6 | Expérimentation d'indicateurs de vulnérabilité externe |

PR-0 livre le contrat, les modèles et la CLI. Elle ne calcule aucun
indicateur dérivé et n'ingère aucune source.
