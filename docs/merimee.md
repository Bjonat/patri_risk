# Mérimée / POP — ingestion v0.1

Vérification effectuée le **8 septembre 2026**.

## Source

| Élément | Valeur observée |
| --- | --- |
| Dataset | [Immeubles protégés au titre des Monuments Historiques](https://www.data.gouv.fr/datasets/immeubles-proteges-au-titre-des-monuments-historiques-2) |
| Producteur | Ministère de la Culture |
| Licence | Licence Ouverte / Open Licence version 2.0 (`lov2`) |
| Fréquence annoncée | hebdomadaire (`weekly`) |
| Ressource CSV | `3a52af4a-f9da-4dcc-8110-b07774dfb3bc` |
| URL stable | `https://www.data.gouv.fr/api/1/datasets/r/3a52af4a-f9da-4dcc-8110-b07774dfb3bc` |
| Format | CSV |
| Content-Type | `text/csv` |
| Dernière modification HTTP observée | `Thu, 03 Sep 2026 01:16:41 GMT` |

Le GeoJSON du même jeu est nettement plus ancien (août 2025). PR-1 utilise **uniquement le CSV**.

L'URL stable data.gouv redirige vers le stockage du ministère. patri_risk conserve l'URL data.gouv, pas l'URL OVH.

## Fichier réellement observé

| Propriété | Observation |
| --- | --- |
| Encodage | UTF-8, sans BOM |
| Séparateur | `\|` (barre verticale), pas `;` ni `,` |
| Nombre de colonnes | 78 |
| Intitulés | identifiants techniques (`Reference`, `Departement_format_numerique`, …), pas les libellés documentaires accentués |

## Champs utilisés en PR-1

| Colonne CSV réelle | Usage |
| --- | --- |
| `Reference` | `IdentiteMonument.reference` ; motif attendu `PA` + 8 chiffres |
| `Titre_editorial_de_la_notice` | `IdentiteMonument.nom` (prioritaire) |
| `Denomination_de_l_edifice` | repli du nom |
| `Commune_forme_editoriale` | `IdentiteMonument.nom_commune` |
| `Departement_format_numerique` | filtre territorial et `code_departement` |
| `COG_Insee_lors_de_la_protection` | preuve `cog_insee_protection` uniquement |
| `coordonnees_au_format_WGS84` | `latitude`,`longitude` (ordre observé : lat, lon) |
| `Nature_de_la_protection` | preuve `nature_protection` |
| `Date_et_typologie_de_la_protection` | preuve textuelle `date_typologie_protection` |
| `etat_de_conservation` | preuve `etat_conservation_merimee` |
| `Statut_juridique_de_l_edifice` | preuve `statut_juridique` |
| `Identifiant_Agregee` | preuve `identifiant_agregee` |
| `Precision_de_la_localisation` | preuve `precision_localisation` |
| `Precision_de_la_protection` | preuve `precision_protection` |
| `Type_de_couverture` | preuve `type_couverture` |
| `Materiaux_du_gros_oeuvre` | preuve `materiaux_gros_oeuvre` |
| `Materiaux_de_la_couverture` | preuve `materiaux_couverture` |
| `Date_de_la_derniere_mise_a_jour` | preuve `date_mise_a_jour_notice` (date de la notice, pas du snapshot) |
| `Date_de_creation_de_la_notice` | preuve `date_creation_notice` |

## Anomalies de schéma par rapport à la documentation publique

- Il n'existe **pas** de colonne `Code Insee` (code commune courant) dans le CSV officiel inspecté.
- Le champ `COG_Insee_lors_de_la_protection` est historique. Il **ne** remplit **pas** `code_commune`.
- Il n'existe pas de colonne `code département` : le filtre utilise `Departement_format_numerique`.
- Les coordonnées sont une chaîne `latitude,longitude` (virgule), WGS84. La première valeur est la latitude (vérifié sur des points d'Aube / Champagne, cohérents avec ~48°N, ~4°E).
- Une inversion évidente lat/lon n'est pas corrigée : coordonnées mises à `None` + anomalie.
- `Date_de_la_derniere_mise_a_jour` est une date civile de notice (`YYYY-MM-DD`). Elle n'est pas copiée dans `SourceDonnee.date_mise_a_jour_source`, qui décrit le snapshot national.
- Une cellule vide ne produit aucune preuve.
- Certains libellés de protection contiennent le caractère Unicode
  U+0085 (NEXT LINE). Le JSONL l'échappe pour rester une ligne par dossier.

## Références

- Format attendu dans l'adaptateur : `^PA[0-9]{8}$`.
- Une référence vide : pas de `DossierMonument`.
- Une référence non conforme mais non vide : dossier conservé + anomalie `reference_format_inattendu`.
- Doublons de référence dans le département : **quarantaine** (aucun dossier produit pour cette référence).

## Conservation

```text
donnees/brutes/merimee/merimee-<date>-<sha8>.csv
donnees/brutes/merimee/merimee-<date>-<sha8>.manifeste.json
donnees/traitees/merimee/31/monuments.jsonl
donnees/traitees/merimee/31/rapport.json
donnees/traitees/merimee/31/anomalies.jsonl
```

Chaque `SourceDonnee` porte `empreinte_artefact = sha256:<hex>` du snapshot.
