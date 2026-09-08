"""Preuve normalisée et traçable."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from patri_risk.modeles.source import SourceDonnee


class MethodeObtention(StrEnum):
    """Méthode par laquelle la preuve a été obtenue ou associée au monument.

    Cette liste est volontairement courte. Elle pourra être étendue
    lorsqu'une nouvelle méthode de correspondance deviendra nécessaire.
    """

    DIRECTE = "directe"
    INTERSECTION_SPATIALE = "intersection_spatiale"
    CORRESPONDANCE_EXACTE = "correspondance_exacte"
    CORRESPONDANCE_APPROXIMATIVE = "correspondance_approximative"
    DERIVEE = "derivee"


class Preuve(BaseModel):
    """Observation factuelle normalisée, toujours reliée à une source.

    Une preuve n'est pas un indicateur dérivé : elle décrit un fait issu
    d'une source, ou une correspondance explicite avec cette source.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    champ: str = Field(
        min_length=1,
        description="Nom normalisé du champ métier (ex. statut_protection).",
    )
    valeur: str | int | float | bool | None | list[Any] | dict[str, Any] = Field(
        description="Valeur observée, sans inférence supplémentaire.",
    )
    source: SourceDonnee
    methode_obtention: MethodeObtention
    niveau_confiance: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "Confiance dans l'obtention et l'association de la preuve, "
            "comprise entre 0 et 1."
        ),
    )
    date_observation: AwareDatetime | None = Field(
        default=None,
        description=(
            "Date du fait lorsque la source la fournit ; distincte de date_collecte."
        ),
    )
    notes: str | None = Field(
        default=None,
        description="Précisions sur les limites, ambiguïtés ou contrôles nécessaires.",
    )
