"""Jeux de données locaux pour les tests, sans accès réseau."""

from datetime import UTC, datetime

import pytest

from patri_risk.modeles import SourceDonnee


@pytest.fixture
def source_merimee() -> SourceDonnee:
    """Source de référence minimale, inspirée de Mérimée, sans appel distant."""
    return SourceDonnee(
        producteur="Ministère de la Culture",
        jeu_donnees="Mérimée",
        identifiant_enregistrement="PA00094321",
        url="https://www.pop.culture.gouv.fr/",
        date_collecte=datetime(2026, 9, 8, 18, 0, tzinfo=UTC),
        licence="Licence Ouverte",
    )
