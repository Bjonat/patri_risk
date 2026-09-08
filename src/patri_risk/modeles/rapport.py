"""Rapport déterministe d'une normalisation Mérimée."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RapportIngestionMerimee(BaseModel):
    """Compteurs d'une normalisation Mérimée, sans score métier."""

    model_config = ConfigDict(extra="forbid")

    departement: str
    nombre_lignes_total: int = Field(ge=0)
    nombre_lignes_departement: int = Field(ge=0)
    nombre_dossiers_produits: int = Field(ge=0)
    nombre_references_manquantes: int = Field(ge=0)
    nombre_references_format_inattendu: int = Field(ge=0)
    nombre_coordonnees_absentes: int = Field(ge=0)
    nombre_coordonnees_invalides: int = Field(ge=0)
    nombre_codes_commune_absents: int = Field(ge=0)
    nombre_doublons_reference: int = Field(ge=0)
    nombre_lignes_en_quarantaine: int = Field(ge=0)
    nombre_anomalies: int = Field(ge=0)
    references_dupliquees: list[str] = Field(default_factory=list)
    colonne_code_insee_absente: bool = True
    empreinte_sha256: str | None = None
