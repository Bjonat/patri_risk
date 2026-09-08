"""Normalisation d'un enregistrement Mérimée vers PatrimoineEvidence v0.1."""

from __future__ import annotations

import re
from datetime import date, datetime

from patri_risk.modeles import (
    AnomalieIngestion,
    DossierMonument,
    EnregistrementBrut,
    IdentiteMonument,
    MethodeObtention,
    Preuve,
    SourceDonnee,
)
from patri_risk.sources.merimee.constantes import (
    CHAMP_COMMUNE,
    CHAMP_COORDONNEES,
    CHAMP_DATE_CREATION_NOTICE,
    CHAMP_DATE_MISE_A_JOUR_NOTICE,
    CHAMP_DENOMINATION,
    CHAMP_DEPARTEMENT,
    CHAMP_PREUVE_PAR_COLONNE,
    CHAMP_REFERENCE,
    CHAMP_TITRE_EDITORIAL,
    JEU_DONNEES,
    LICENCE,
    PRODUCTEUR,
    URL_RESSOURCE,
)
from patri_risk.sources.merimee.lecture import extraire_cellule

MOTIF_REFERENCE_MERIMEE = re.compile(r"^PA[0-9]{8}$")
# France métropolitaine : détection d'une inversion lat/lon évidente.
LATITUDE_METROPOLE = (41.0, 51.5)
LONGITUDE_METROPOLE = (-5.5, 9.8)


def construire_source(
    *,
    identifiant_enregistrement: str | None,
    date_collecte: datetime,
    empreinte_artefact: str | None,
    url: str = URL_RESSOURCE,
) -> SourceDonnee:
    """Provenance d'une ligne Mérimée, reliée au snapshot national."""
    return SourceDonnee(
        producteur=PRODUCTEUR,
        jeu_donnees=JEU_DONNEES,
        identifiant_enregistrement=identifiant_enregistrement,
        url=url,
        date_collecte=date_collecte,
        licence=LICENCE,
        date_mise_a_jour_source=None,
        empreinte_artefact=empreinte_artefact,
    )


def choisir_nom(contenu: dict[str, str]) -> str | None:
    """Libellé humain : titre éditorial, sinon dénomination."""
    titre = extraire_cellule(contenu, CHAMP_TITRE_EDITORIAL)
    if titre:
        return titre
    return extraire_cellule(contenu, CHAMP_DENOMINATION)


def interpreter_coordonnees(
    valeur: str | None,
    *,
    reference: str | None,
    numero_ligne: int | None,
) -> tuple[float | None, float | None, AnomalieIngestion | None]:
    """Interprète ``lat,lon`` WGS84 sans réparer une inversion.

    L'ordre observé dans le CSV officiel est latitude puis longitude.
    """
    if valeur is None:
        return None, None, None
    parties = [partie.strip() for partie in valeur.split(",")]
    if len(parties) != 2:
        return (
            None,
            None,
            AnomalieIngestion(
                type="coordonnees_invalides",
                reference=reference,
                numero_ligne=numero_ligne,
                champ=CHAMP_COORDONNEES,
                valeur_source=valeur,
                message="coordonnées absentes de la forme attendue lat,lon",
            ),
        )
    try:
        latitude = float(parties[0])
        longitude = float(parties[1])
    except ValueError:
        return (
            None,
            None,
            AnomalieIngestion(
                type="coordonnees_invalides",
                reference=reference,
                numero_ligne=numero_ligne,
                champ=CHAMP_COORDONNEES,
                valeur_source=valeur,
                message="coordonnées non numériques",
            ),
        )
    if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0):
        return (
            None,
            None,
            AnomalieIngestion(
                type="coordonnees_invalides",
                reference=reference,
                numero_ligne=numero_ligne,
                champ=CHAMP_COORDONNEES,
                valeur_source=valeur,
                message="coordonnées hors bornes WGS84",
            ),
        )
    inversion_probable = (
        LONGITUDE_METROPOLE[0] <= latitude <= LONGITUDE_METROPOLE[1]
        and LATITUDE_METROPOLE[0] <= longitude <= LATITUDE_METROPOLE[1]
    )
    if inversion_probable:
        return (
            None,
            None,
            AnomalieIngestion(
                type="coordonnees_invalides",
                reference=reference,
                numero_ligne=numero_ligne,
                champ=CHAMP_COORDONNEES,
                valeur_source=valeur,
                message=(
                    "coordonnées ambiguës (inversion lat/lon probable) ; "
                    "aucune correction silencieuse"
                ),
            ),
        )
    return latitude, longitude, None


def _lire_date_civile(valeur: str) -> date | None:
    try:
        return date.fromisoformat(valeur)
    except ValueError:
        return None


def _creer_preuve(
    champ: str,
    valeur: str,
    source: SourceDonnee,
    *,
    date_observation: date | None = None,
) -> Preuve:
    return Preuve(
        champ=champ,
        valeur=valeur,
        source=source,
        methode_obtention=MethodeObtention.DIRECTE,
        niveau_confiance=1.0,
        date_observation=date_observation,
    )


def normaliser_enregistrement_merimee(
    enregistrement: EnregistrementBrut,
    *,
    numero_ligne: int | None = None,
) -> tuple[DossierMonument | None, list[AnomalieIngestion]]:
    """Transforme une ligne brute en dossier, sans inventer de fait."""
    anomalies: list[AnomalieIngestion] = []
    contenu = {
        str(cle): str(valeur) if valeur is not None else ""
        for cle, valeur in enregistrement.contenu.items()
    }
    reference = extraire_cellule(contenu, CHAMP_REFERENCE)
    if reference is None:
        anomalies.append(
            AnomalieIngestion(
                type="reference_manquante",
                numero_ligne=numero_ligne,
                champ=CHAMP_REFERENCE,
                message="référence vide : dossier non produit",
            )
        )
        return None, anomalies

    if MOTIF_REFERENCE_MERIMEE.fullmatch(reference) is None:
        anomalies.append(
            AnomalieIngestion(
                type="reference_format_inattendu",
                reference=reference,
                numero_ligne=numero_ligne,
                champ=CHAMP_REFERENCE,
                valeur_source=reference,
                message=(
                    "référence conservée malgré un format distinct de "
                    "PA suivi de 8 chiffres"
                ),
            )
        )

    latitude, longitude, anomalie_coord = interpreter_coordonnees(
        extraire_cellule(contenu, CHAMP_COORDONNEES),
        reference=reference,
        numero_ligne=numero_ligne,
    )
    if anomalie_coord is not None:
        anomalies.append(anomalie_coord)

    source = enregistrement.source.model_copy(
        update={"identifiant_enregistrement": reference}
    )
    identite = IdentiteMonument(
        reference=reference,
        nom=choisir_nom(contenu),
        nom_commune=extraire_cellule(contenu, CHAMP_COMMUNE),
        code_commune=None,
        code_departement=extraire_cellule(contenu, CHAMP_DEPARTEMENT),
        latitude=latitude,
        longitude=longitude,
    )
    dossier = DossierMonument(identite=identite)
    for colonne, champ_preuve in CHAMP_PREUVE_PAR_COLONNE:
        valeur = extraire_cellule(contenu, colonne)
        if valeur is None:
            continue
        date_observation = None
        if colonne in {CHAMP_DATE_MISE_A_JOUR_NOTICE, CHAMP_DATE_CREATION_NOTICE}:
            date_observation = _lire_date_civile(valeur)
        dossier.ajouter_preuve(
            _creer_preuve(
                champ_preuve,
                valeur,
                source,
                date_observation=date_observation,
            )
        )
    return dossier, anomalies
