"""Identité et dossier d'un monument historique."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from patri_risk.modeles.preuve import Preuve


class IdentiteMonument(BaseModel):
    """Identité de travail d'un immeuble protégé au titre des monuments historiques.

    ``reference`` est l'identifiant patrimonial principal. Le format n'est
    pas imposé ici : la validation propre à une source (ex. Mérimée)
    appartient à l'adaptateur. Le nom n'est pas un identifiant.
    Les coordonnées WGS84, le code commune et le nom peuvent manquer. Un
    monument ne correspond pas nécessairement à un unique bâtiment
    géométrique.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    reference: str = Field(
        min_length=1,
        description="Identifiant patrimonial principal (ex. PA00094321).",
    )
    nom: str | None = Field(
        default=None,
        description="Dénomination usuelle, non unique.",
    )
    nom_commune: str | None = Field(
        default=None,
        description="Nom de commune associé à l'enregistrement, s'il est connu.",
    )
    code_commune: str | None = Field(
        default=None,
        description="Code commune INSEE ; peut être ancien ou à contrôler.",
    )
    code_departement: str | None = Field(
        default=None,
        description="Code département INSEE (ex. 31 pour la Haute-Garonne).",
    )
    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
        description="Latitude WGS84 (EPSG:4326), si la source en fournit une.",
    )
    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
        description="Longitude WGS84 (EPSG:4326), si la source en fournit une.",
    )

    @model_validator(mode="after")
    def verifier_paire_de_coordonnees(self) -> IdentiteMonument:
        """Refuse une localisation partielle : les deux coordonnées ou aucune."""
        latitude_presente = self.latitude is not None
        longitude_presente = self.longitude is not None
        if latitude_presente != longitude_presente:
            raise ValueError(
                "latitude et longitude doivent être renseignées ensemble, "
                "ou toutes deux absentes."
            )
        return self


class DossierMonument(BaseModel):
    """Regroupement des preuves accumulées autour d'un même monument.

    Le dossier contient uniquement l'identité et les preuves. Les
    artefacts sources bruts sont conservés à part par le pipeline
    d'ingestion. Aucun indicateur dérivé n'est calculé ici.
    """

    model_config = ConfigDict(extra="forbid")

    identite: IdentiteMonument
    preuves: list[Preuve] = Field(default_factory=list)

    def ajouter_preuve(self, preuve: Preuve) -> None:
        """Ajoute une preuve traçable au dossier."""
        self.preuves.append(preuve)

    def preuves_pour_champ(self, champ: str) -> list[Preuve]:
        """Retourne les preuves correspondant à un champ métier."""
        return [preuve for preuve in self.preuves if preuve.champ == champ]
