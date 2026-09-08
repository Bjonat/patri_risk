# Vision

**Patrimoine Evidence Engine** est un moteur open source expérimental
d'agrégation de preuves publiques relatives aux monuments historiques
français.

Nom de dépôt et de paquet : `patri_risk`. État actuel : pré-v0.1,
expérimental.

## Question centrale

Peut-on combiner des données publiques françaises afin de construire un
système reproductible et explicable de pré-triage aidant à identifier les
monuments historiques pour lesquels les informations publiques sont
anciennes, incomplètes ou accompagnées de signaux externes défavorables ?

## Ce que le système vise à faire

Le système est un outil :

- d'aide à l'investigation ;
- de pré-triage ;
- d'agrégation de preuves publiques ;
- d'aide à la priorisation d'investigation.

Il doit permettre, à terme, de répondre à une question du type :

> Pour un monument historique français donné, quelles preuves publiques
> sont actuellement disponibles concernant son état connu, son
> exposition à différents aléas, les signaux de travaux ou
> d'investissement, son contexte territorial et les lacunes de données ?

## Ce que le système n'est pas

Le système ne diagnostique pas l'état structurel d'un monument. Il ne
prédit pas un effondrement. Il ne remplace ni l'expertise des DRAC,
CRMH ou UDAP, ni AgrÉgée. Il ne fournit pas de score officiel de risque.

Une absence de donnée n'est pas une conclusion. Un signal d'exposition
n'est pas un diagnostic. Une lacune d'information n'est pas une
preuve de bon ou de mauvais état.

## Vocabulaire retenu

| Terme | Usage |
| --- | --- |
| preuve | observation factuelle normalisée, reliée à une source |
| signal | indice public nécessitant investigation, non une conclusion |
| exposition | présence dans un zonage ou un aléa selon une source nommée |
| pré-triage | aide à ordonner le travail d'investigation |
| priorité d'investigation | ordre de regard, jamais un classement de danger |
| lacune d'information | absence de preuve dans les sources interrogées |
| qualité des données | fraîcheur, complétude, traçabilité des preuves |

## Principe fondamental

**Aucune information dérivée sans preuve traçable.**

Toute information importante doit pouvoir être reliée à sa source, son
producteur, son identifiant source, sa date de collecte, sa méthode
d'obtention, son niveau de confiance et, lorsque possible, son URL
d'origine.
