"""Constantes de l'adaptateur Mérimée / POP.

Les intitulés de colonnes sont ceux réellement observés dans le CSV
officiel, pas ceux de la documentation marketing du jeu de données.
"""

from __future__ import annotations

URL_JEU_DONNEES = (
    "https://www.data.gouv.fr/datasets/"
    "immeubles-proteges-au-titre-des-monuments-historiques-2"
)
URL_RESSOURCE = (
    "https://www.data.gouv.fr/api/1/datasets/r/3a52af4a-f9da-4dcc-8110-b07774dfb3bc"
)
PRODUCTEUR = "Ministère de la Culture"
JEU_DONNEES = "Mérimée"
LICENCE = "Licence Ouverte / Open Licence version 2.0"
FORMAT_FICHIER = "csv"
ENCODAGE = "utf-8"
SEPARATEUR = "|"
DEPARTEMENT_REFERENCE = "31"
USER_AGENT = "patri-risk/0.1.0-dev (https://github.com/Bjonat/patri_risk)"

CHAMP_REFERENCE = "Reference"
CHAMP_TITRE_EDITORIAL = "Titre_editorial_de_la_notice"
CHAMP_DENOMINATION = "Denomination_de_l_edifice"
CHAMP_COMMUNE = "Commune_forme_editoriale"
CHAMP_DEPARTEMENT = "Departement_format_numerique"
CHAMP_COG_PROTECTION = "COG_Insee_lors_de_la_protection"
CHAMP_COORDONNEES = "coordonnees_au_format_WGS84"
CHAMP_NATURE_PROTECTION = "Nature_de_la_protection"
CHAMP_DATE_TYPOLOGIE_PROTECTION = "Date_et_typologie_de_la_protection"
CHAMP_ETAT_CONSERVATION = "etat_de_conservation"
CHAMP_STATUT_JURIDIQUE = "Statut_juridique_de_l_edifice"
CHAMP_IDENTIFIANT_AGREGEE = "Identifiant_Agregee"
CHAMP_PRECISION_LOCALISATION = "Precision_de_la_localisation"
CHAMP_PRECISION_PROTECTION = "Precision_de_la_protection"
CHAMP_TYPE_COUVERTURE = "Type_de_couverture"
CHAMP_MATERIAUX_GROS_OEUVRE = "Materiaux_du_gros_oeuvre"
CHAMP_MATERIAUX_COUVERTURE = "Materiaux_de_la_couverture"
CHAMP_DATE_MISE_A_JOUR_NOTICE = "Date_de_la_derniere_mise_a_jour"
CHAMP_DATE_CREATION_NOTICE = "Date_de_creation_de_la_notice"

COLONNES_OBLIGATOIRES = (CHAMP_REFERENCE, CHAMP_DEPARTEMENT)

# Le CSV officiel n'expose pas de colonne « Code Insee » courant.
# code_commune reste donc vide en PR-1 ; le COG historique est une preuve.
CHAMP_PREUVE_PAR_COLONNE: tuple[tuple[str, str], ...] = (
    (CHAMP_NATURE_PROTECTION, "nature_protection"),
    (CHAMP_DATE_TYPOLOGIE_PROTECTION, "date_typologie_protection"),
    (CHAMP_ETAT_CONSERVATION, "etat_conservation_merimee"),
    (CHAMP_STATUT_JURIDIQUE, "statut_juridique"),
    (CHAMP_IDENTIFIANT_AGREGEE, "identifiant_agregee"),
    (CHAMP_COG_PROTECTION, "cog_insee_protection"),
    (CHAMP_PRECISION_LOCALISATION, "precision_localisation"),
    (CHAMP_PRECISION_PROTECTION, "precision_protection"),
    (CHAMP_TYPE_COUVERTURE, "type_couverture"),
    (CHAMP_MATERIAUX_GROS_OEUVRE, "materiaux_gros_oeuvre"),
    (CHAMP_MATERIAUX_COUVERTURE, "materiaux_couverture"),
    (CHAMP_DATE_MISE_A_JOUR_NOTICE, "date_mise_a_jour_notice"),
    (CHAMP_DATE_CREATION_NOTICE, "date_creation_notice"),
)

TAILLE_BLOC_TELECHARGEMENT = 64 * 1024
