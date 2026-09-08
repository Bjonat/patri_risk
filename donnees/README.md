# Données locales

Les snapshots Mérimée, manifestes de collecte et JSONL normalisés sont
locaux. Ils ne sont pas versionnés.

```text
donnees/brutes/merimee/     snapshots CSV + manifestes
donnees/traitees/merimee/31/  JSONL, rapport, anomalies
```

Collecte :

```bash
patri-risk merimee collecter --repertoire donnees/brutes/merimee
```

Normalisation :

```bash
patri-risk merimee normaliser \
  --departement 31 \
  --fichier donnees/brutes/merimee/<snapshot.csv>
```
