"""Tests du modèle Preuve et de la provenance."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from patri_risk.modeles import EnregistrementBrut, MethodeObtention, Preuve, SourceDonnee


def test_preuve_accepte_un_niveau_confiance_valide(
    source_merimee: SourceDonnee,
) -> None:
    preuve = Preuve(
        champ="statut_protection",
        valeur="classé",
        source=source_merimee,
        methode_obtention=MethodeObtention.DIRECTE,
        niveau_confiance=1.0,
    )
    assert preuve.niveau_confiance == 1.0
    assert preuve.source.producteur == "Ministère de la Culture"


def test_preuve_refuse_un_niveau_confiance_inferieur_a_zero(
    source_merimee: SourceDonnee,
) -> None:
    with pytest.raises(ValidationError):
        Preuve(
            champ="statut_protection",
            valeur="classé",
            source=source_merimee,
            methode_obtention=MethodeObtention.DIRECTE,
            niveau_confiance=-0.1,
        )


def test_preuve_refuse_un_niveau_confiance_superieur_a_un(
    source_merimee: SourceDonnee,
) -> None:
    with pytest.raises(ValidationError):
        Preuve(
            champ="statut_protection",
            valeur="classé",
            source=source_merimee,
            methode_obtention=MethodeObtention.DIRECTE,
            niveau_confiance=1.01,
        )


def test_preuve_est_serialisable_en_json(source_merimee: SourceDonnee) -> None:
    preuve = Preuve(
        champ="statut_protection",
        valeur="classé",
        source=source_merimee,
        methode_obtention=MethodeObtention.DIRECTE,
        niveau_confiance=1.0,
        date_observation=None,
        notes="Valeur lue dans l'enregistrement source.",
    )
    texte_json = preuve.model_dump_json()
    preuve_relue = Preuve.model_validate_json(texte_json)
    assert preuve_relue.champ == "statut_protection"
    assert preuve_relue.valeur == "classé"
    assert preuve_relue.source.identifiant_enregistrement == "PA00094321"
    assert preuve_relue.date_observation is None
    assert preuve_relue.source.date_collecte == source_merimee.date_collecte


def test_preuve_exige_une_source() -> None:
    with pytest.raises(ValidationError):
        Preuve(
            champ="statut_protection",
            valeur="classé",
            methode_obtention=MethodeObtention.DIRECTE,
            niveau_confiance=1.0,
        )


def test_preuve_conserve_la_distinction_des_dates(
    source_merimee: SourceDonnee,
) -> None:
    date_observation = datetime(1924, 1, 1, tzinfo=UTC)
    preuve = Preuve(
        champ="date_protection",
        valeur="1924",
        source=source_merimee,
        methode_obtention=MethodeObtention.DIRECTE,
        niveau_confiance=1.0,
        date_observation=date_observation,
    )
    assert preuve.date_observation == date_observation
    assert preuve.source.date_collecte != preuve.date_observation


def test_enregistrement_brut_conserve_le_payload_original(
    source_merimee: SourceDonnee,
) -> None:
    brut = EnregistrementBrut(
        source=source_merimee,
        contenu={"REF": "PA00094321", "DENO": "Église", "COM": "Toulouse"},
    )
    assert brut.contenu["REF"] == "PA00094321"
    assert brut.source.jeu_donnees == "Mérimée"


def test_source_refuse_une_date_collecte_naive() -> None:
    with pytest.raises(ValidationError):
        SourceDonnee(
            producteur="Ministère de la Culture",
            jeu_donnees="Mérimée",
            date_collecte=datetime(2026, 9, 8, 18, 0),
        )
