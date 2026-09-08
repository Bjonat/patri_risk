"""Anomalie d'ingestion, distincte d'une preuve."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AnomalieIngestion(BaseModel):
    """Signalement d'un problème de qualité constaté pendant l'ingestion."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    type: str = Field(description="Type d'anomalie, identifiant court.")
    message: str
    reference: str | None = None
    numero_ligne: int | None = None
    champ: str | None = None
    valeur_source: str | None = None
