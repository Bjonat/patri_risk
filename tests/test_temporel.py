"""Tests de la précision temporelle des sources et des preuves."""

from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from patri_risk.modeles import MethodeObtention, Preuve, SourceDonnee


def _source(
    *,
    date_collecte: datetime | None = None,
    date_mise_a_jour_source: date | datetime | None = None,
) -> SourceDonnee:
    return SourceDonnee(
        producteur="Ministère de la Culture",
        jeu_donnees="Mérimée",
        identifiant_enregistrement="PA00094321",
        date_collecte=date_collecte or datetime(2026, 9, 8, 18, 0, tzinfo=UTC),
        date_mise_a_jour_source=date_mise_a_jour_source,
    )


def test_date_collecte_accepte_une_datetime_aware() -> None:
    instant = datetime(2026, 9, 8, 18, 0, tzinfo=UTC)
    source = _source(date_collecte=instant)
    assert source.date_collecte == instant
    assert source.date_collecte.tzinfo is UTC


def test_date_collecte_refuse_une_datetime_naive() -> None:
    with pytest.raises(ValidationError):
        _source(date_collecte=datetime(2026, 9, 8, 18, 0))


def test_date_collecte_est_normalisee_vers_utc() -> None:
    instant_paris = datetime(2026, 9, 8, 20, 0, tzinfo=ZoneInfo("Europe/Paris"))
    source = _source(date_collecte=instant_paris)
    assert source.date_collecte == datetime(2026, 9, 8, 18, 0, tzinfo=UTC)
    assert source.date_collecte.utcoffset().total_seconds() == 0


def test_date_mise_a_jour_source_accepte_une_date() -> None:
    jour = date(2025, 1, 14)
    source = _source(date_mise_a_jour_source=jour)
    assert source.date_mise_a_jour_source == jour
    assert isinstance(source.date_mise_a_jour_source, date)
    assert not isinstance(source.date_mise_a_jour_source, datetime)


def test_date_mise_a_jour_source_accepte_une_datetime_aware() -> None:
    instant = datetime(2025, 1, 14, 9, 30, tzinfo=UTC)
    source = _source(date_mise_a_jour_source=instant)
    assert source.date_mise_a_jour_source == instant
    assert isinstance(source.date_mise_a_jour_source, datetime)


def test_date_observation_accepte_une_date(
    source_merimee: SourceDonnee,
) -> None:
    jour = date(1924, 1, 1)
    preuve = Preuve(
        champ="date_protection",
        valeur="1924-01-01",
        source=source_merimee,
        methode_obtention=MethodeObtention.DIRECTE,
        niveau_confiance=1.0,
        date_observation=jour,
    )
    assert preuve.date_observation == jour
    assert isinstance(preuve.date_observation, date)
    assert not isinstance(preuve.date_observation, datetime)


def test_date_observation_accepte_une_datetime_aware(
    source_merimee: SourceDonnee,
) -> None:
    instant = datetime(2025, 1, 14, 15, 30, tzinfo=UTC)
    preuve = Preuve(
        champ="date_protection",
        valeur="2025-01-14T15:30:00Z",
        source=source_merimee,
        methode_obtention=MethodeObtention.DIRECTE,
        niveau_confiance=1.0,
        date_observation=instant,
    )
    assert preuve.date_observation == instant
    assert isinstance(preuve.date_observation, datetime)


def test_une_date_n_est_pas_convertie_en_minuit_utc(
    source_merimee: SourceDonnee,
) -> None:
    jour = date(2025, 1, 14)
    source = _source(date_mise_a_jour_source=jour)
    preuve = Preuve(
        champ="mise_a_jour_notice",
        valeur="2025-01-14",
        source=source_merimee,
        methode_obtention=MethodeObtention.DIRECTE,
        niveau_confiance=1.0,
        date_observation=jour,
    )
    assert isinstance(source.date_mise_a_jour_source, date)
    assert not isinstance(source.date_mise_a_jour_source, datetime)
    assert isinstance(preuve.date_observation, date)
    assert not isinstance(preuve.date_observation, datetime)
    assert "2025-01-14T00:00:00" not in source.model_dump_json()
    assert "2025-01-14T00:00:00" not in preuve.model_dump_json()
    source_relue = SourceDonnee.model_validate_json(source.model_dump_json())
    preuve_relue = Preuve.model_validate_json(preuve.model_dump_json())
    assert source_relue.date_mise_a_jour_source == jour
    assert isinstance(source_relue.date_mise_a_jour_source, date)
    assert not isinstance(source_relue.date_mise_a_jour_source, datetime)
    assert preuve_relue.date_observation == jour
    assert isinstance(preuve_relue.date_observation, date)
    assert not isinstance(preuve_relue.date_observation, datetime)
