"""Manifeste d'une collecte d'artefact source."""

from __future__ import annotations

from datetime import datetime

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator

from patri_risk.modeles.temporel import normaliser_instant_utc


class ManifesteCollecte(BaseModel):
    """Trace cryptographique et administrative d'un snapshot collecté.

    Ce manifeste n'est pas stocké dans ``DossierMonument``. Il permet
    d'auditer une preuve contre l'artefact exact utilisé au traitement.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    source: str = Field(description="Nom court de la source (ex. Mérimée).")
    url_ressource: str = Field(description="URL de la ressource collectée.")
    date_collecte: AwareDatetime
    empreinte_sha256: str = Field(
        min_length=64,
        max_length=64,
        description="Empreinte SHA-256 hexadécimale des octets téléchargés.",
    )
    taille_octets: int = Field(ge=0)
    licence: str | None = None
    nom_fichier: str
    format: str
    etag: str | None = None
    derniere_modification_http: str | None = None

    @field_validator("date_collecte")
    @classmethod
    def convertir_date_collecte_en_utc(cls, valeur: datetime) -> datetime:
        return normaliser_instant_utc(valeur)

    @field_validator("empreinte_sha256")
    @classmethod
    def verifier_empreinte_hexadecimale(cls, valeur: str) -> str:
        texte = valeur.lower()
        if any(caractere not in "0123456789abcdef" for caractere in texte):
            raise ValueError("empreinte_sha256 doit être hexadécimale.")
        return texte

    def empreinte_artefact(self) -> str:
        """Identifiant d'artefact pour ``SourceDonnee.empreinte_artefact``."""
        return f"sha256:{self.empreinte_sha256}"
