"""Tests de l'identité et du dossier monument."""

import pytest
from pydantic import ValidationError

from patri_risk.modeles import (
    DossierMonument,
    IdentiteMonument,
    MethodeObtention,
    Preuve,
    SourceDonnee,
)


def test_identite_monument_exige_une_reference() -> None:
    with pytest.raises(ValidationError):
        IdentiteMonument(reference="")


def test_identite_monument_accepte_des_coordonnees_absentes() -> None:
    identite = IdentiteMonument(
        reference="PA00094321",
        nom="Église",
        nom_commune="Toulouse",
        code_commune="31555",
        code_departement="31",
    )
    assert identite.latitude is None
    assert identite.longitude is None
    assert identite.reference == "PA00094321"


def test_identite_monument_conserve_le_code_departement() -> None:
    identite = IdentiteMonument(
        reference="PA00094321",
        code_departement="31",
    )
    assert identite.code_departement == "31"
    assert identite.nom is None
    assert identite.code_commune is None


def test_identite_monument_est_serialisable_en_json() -> None:
    identite = IdentiteMonument(
        reference="PA00094321",
        nom="Hôtel d'Assézat",
        nom_commune="Toulouse",
        code_commune="31555",
        code_departement="31",
        latitude=43.6003,
        longitude=1.4416,
    )
    texte_json = identite.model_dump_json()
    identite_relue = IdentiteMonument.model_validate_json(texte_json)
    assert identite_relue.reference == "PA00094321"
    assert identite_relue.code_departement == "31"
    assert identite_relue.latitude == identite.latitude


def test_identite_monument_refuse_une_coordonnee_isolee() -> None:
    with pytest.raises(ValidationError):
        IdentiteMonument(reference="PA00094321", latitude=43.6)


def test_dossier_monument_accumule_des_preuves(
    source_merimee: SourceDonnee,
) -> None:
    dossier = DossierMonument(
        identite=IdentiteMonument(
            reference="PA00094321",
            nom_commune="Toulouse",
            code_departement="31",
        )
    )
    assert dossier.preuves == []
    dossier.ajouter_preuve(
        Preuve(
            champ="statut_protection",
            valeur="classé",
            source=source_merimee,
            methode_obtention=MethodeObtention.DIRECTE,
            niveau_confiance=1.0,
        )
    )
    dossier.ajouter_preuve(
        Preuve(
            champ="nom_commune",
            valeur="Toulouse",
            source=source_merimee,
            methode_obtention=MethodeObtention.DIRECTE,
            niveau_confiance=1.0,
        )
    )
    assert len(dossier.preuves) == 2
    assert len(dossier.preuves_pour_champ("statut_protection")) == 1
