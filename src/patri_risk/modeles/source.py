"""Provenance d'une information publique."""

from __future__ import annotations

from typing import Any

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class SourceDonnee(BaseModel):
    """Provenance d'une information collectée dans une source publique.

    Tous les champs ne sont pas nécessairement renseignés selon la source.
    ``date_collecte`` est obligatoire : c'est le moment où le système a
    obtenu l'enregistrement, distinct de la date du fait observé.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    producteur: str = Field(description="Organisme producteur de la donnée.")
    jeu_donnees: str = Field(description="Nom du jeu ou de la base d'origine.")
    identifiant_enregistrement: str | None = Field(
        default=None,
        description=(
            "Identifiant de l'enregistrement dans la source (ex. référence Mérimée)."
        ),
    )
    url: str | None = Field(
        default=None,
        description="URL d'origine lorsqu'elle est connue et stable.",
    )
    date_collecte: AwareDatetime = Field(
        description="Instant auquel la donnée a été collectée par le système (UTC).",
    )
    licence: str | None = Field(
        default=None,
        description="Licence de réutilisation indiquée par la source, si connue.",
    )
    date_mise_a_jour_source: AwareDatetime | None = Field(
        default=None,
        description="Date de mise à jour déclarée par la source, si disponible.",
    )


class EnregistrementBrut(BaseModel):
    """Couche A : donnée telle que retournée par la source, sans interprétation.

    Le contenu reste un dictionnaire aussi proche que possible du payload
    original. Aucune inférence métier n'est effectuée à ce niveau.
    """

    model_config = ConfigDict(extra="forbid")

    source: SourceDonnee
    contenu: dict[str, Any]
