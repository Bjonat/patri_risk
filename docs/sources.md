# Registre des sources

Ce registre décrit des sources **prévues**. Sauf mention contraire,
elles ne sont pas implémentées. Les URL d'API, fichiers d'export et
schémas exacts sont marqués « à vérifier avant implémentation »
lorsqu'ils n'ont pas encore été contrôlés dans ce dépôt.

Les portails publics listés ci-dessous sont des points d'entrée
officiels connus, pas des garanties d'endpoint machine.

## Tableau

| source | producteur | objectif | granularite | methode_jointure | statut_ouverture | fraicheur | statut_implementation | limitations_connues |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mérimée / POP | Ministère de la Culture | identification des monuments historiques ; métadonnées patrimoniales publiques ; protection ; localisation ; informations descriptives disponibles | immeuble protégé / notice | identifiant Mérimée (`PA…`) ; éventuellement commune et coordonnées | données publiques patrimoniales ; licence et modalités d'export à vérifier avant implémentation | dépend de la mise à jour de la notice et du canal d'export ; à vérifier avant implémentation | prévu pour PR-1 | une notice n'est pas un diagnostic d'état ; localisation parfois manquante ou imprécise ; le nom n'est pas unique ; un monument n'équivaut pas toujours à un bâtiment |
| Géorisques | Ministère chargé de la Transition écologique / BRGM selon les données | aléas naturels et environnementaux (inondation, retrait-gonflement des argiles, mouvements de terrain, cavités, séisme, PPR, CATNAT, etc.) | zonage, commune, ou parcelle selon le jeu | intersection spatiale ; éventuellement code INSEE | données publiques ; jeux, licences et API à vérifier avant implémentation | variable selon l'aléa ; à vérifier avant implémentation | prévu | l'exposition à un aléa n'est pas un diagnostic structurel ; la jointure spatiale peut être approximative si la géométrie du monument est pauvre |
| BDNB | CSTB / partenaires de la BDNB (à confirmer selon le millésime) | enrichissement à l'échelle du bâtiment | bâtiment | correspondance spatiale ou identifiant bâtiment ; à vérifier avant implémentation | données ouvertes selon les millésimes ; licence et accès à vérifier avant implémentation | millésimée ; à vérifier avant implémentation | prévu | un monument historique ne correspond pas nécessairement à un unique bâtiment BDNB ; risque de fausse jointure |
| INSEE | INSEE | contexte communal et territorial | commune, zonage administratif | code commune INSEE ; attention aux codes anciens | open data INSEE ; jeux précis à vérifier avant implémentation | selon le millésime et le recensement ou millésime administratif | prévu | le contexte territorial n'est pas un attribut du monument ; les codes commune évoluent |
| OFGL | OFGL | contexte financier des collectivités | collectivité / groupement | code collectivité ou commune ; à vérifier avant implémentation | données publiques ; modalités à vérifier avant implémentation | selon les publications OFGL ; à vérifier avant implémentation | prévu | un agrégat financier de collectivité n'est pas un budget du monument |
| BOAMP / données essentielles de la commande publique | Direction de l'information légale et administrative / AIFE selon les jeux | détecter des signaux publics de travaux et de marchés | marché, avis, lieu d'exécution | correspondance textuelle, identifiant d'acheteur, lieu ; souvent heuristique | données publiques ; schémas et entrepôts à vérifier avant implémentation | selon la publication des avis et données essentielles | prévu | un marché proche n'est pas forcément un chantier du monument ; les faux positifs seront fréquents |
| DGCL / DETR / DSIL | DGCL | détecter des signaux de financement public ou de soutien à l'investissement | collectivité, opération, ou ligne de subvention selon le fichier | identifiant de collectivité, libellé d'opération, commune ; souvent heuristique | données publiques lorsqu'elles sont publiées ; fichiers exacts à vérifier avant implémentation | selon les campagnes et publications ; à vérifier avant implémentation | prévu | l'absence de ligne dans un export n'autorise pas à conclure à l'absence de subvention |

## Détails

### Mérimée / POP

- Producteur : Ministère de la Culture.
- Portail public connu : [https://www.pop.culture.gouv.fr/](https://www.pop.culture.gouv.fr/).
- Endpoint d'export machine, format précis (JSON, CSV, API) et licence
  de réutilisation : **à vérifier avant implémentation**.
- Objectif dans ce projet : constituer l'identité de référence des
  immeubles protégés et les premières preuves patrimoniales.
- Statut : prévu pour PR-1.

### Géorisques

- Producteur : ministère chargé de la Transition écologique / BRGM
  selon les données.
- Portail public connu : [https://www.georisques.gouv.fr/](https://www.georisques.gouv.fr/).
- API, millésimes et géométries exactes : **à vérifier avant
  implémentation**.
- Statut : prévu (PR-2).

### BDNB

- Objectif : enrichissement à l'échelle du bâtiment.
- Producteur, millésime, licence et documentation d'accès : **à
  vérifier avant implémentation**.
- Statut : prévu.

### INSEE

- Producteur : INSEE.
- Portail public connu : [https://www.insee.fr/](https://www.insee.fr/).
- Jeux précis (COG, recensement, bases locales) : **à vérifier avant
  implémentation**.
- Statut : prévu.

### OFGL

- Producteur : OFGL.
- Portail public connu : [https://www.ofgl.fr/](https://www.ofgl.fr/).
- Jeux et identifiants de jointure : **à vérifier avant implémentation**.
- Statut : prévu.

### BOAMP / données essentielles de la commande publique

- Objectif : signaux publics de travaux et de marchés, jamais une
  preuve automatique de travaux réalisés sur le monument.
- Portails publics connus : [https://www.boamp.fr/](https://www.boamp.fr/),
  [https://www.data.gouv.fr/](https://www.data.gouv.fr/).
- Jeu, schéma et entrepôt exacts : **à vérifier avant implémentation**.
- Statut : prévu (PR-4).

### DGCL / DETR / DSIL

- Objectif : signaux de financement public ou de soutien à
  l'investissement.
- Portail public connu : [https://www.collectivites-locales.gouv.fr/](https://www.collectivites-locales.gouv.fr/).
- Fichiers, millésimes et colonnes : **à vérifier avant implémentation**.
- Statut : prévu (PR-4).

## Règle d'usage

Une source listée ici n'est pas une source interrogée. Tant que
`statut_implementation` n'est pas « implémenté », aucune conclusion
du système ne peut s'appuyer sur elle.
