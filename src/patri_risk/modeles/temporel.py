"""Types temporels du contrat de données.

``date_collecte`` est un instant. ``date_observation`` et
``date_mise_a_jour_source`` conservent la précision réelle de la source :
un jour civil ou un horodatage avec fuseau, jamais une heure inventée.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Annotated

from pydantic import BeforeValidator

_LONGUEUR_DATE_ISO = 10


def normaliser_instant_utc(valeur: datetime) -> datetime:
    """Convertit un instant timezone-aware vers UTC, sans changer l'instant."""
    return valeur.astimezone(UTC)


def lire_date_ou_instant(valeur: object) -> date | datetime:
    """Conserve un jour civil ou un instant aware, sans inventer de précision.

    Une chaîne ``YYYY-MM-DD`` reste une ``date``. Un horodatage avec fuseau
    reste un ``datetime``. Une datetime naïve est rejetée.
    """
    if isinstance(valeur, datetime):
        if valeur.tzinfo is None:
            raise ValueError(
                "une datetime naïve n'est pas acceptée ; fournir une date "
                "civile ou un instant avec fuseau"
            )
        return valeur
    if isinstance(valeur, date):
        return valeur
    if isinstance(valeur, str):
        texte = valeur.strip()
        if len(texte) == _LONGUEUR_DATE_ISO and texte[4] == "-" and texte[7] == "-":
            return date.fromisoformat(texte)
        instant = datetime.fromisoformat(texte.replace("Z", "+00:00"))
        if instant.tzinfo is None:
            raise ValueError(
                "un instant sans fuseau n'est pas accepté ; fournir une date "
                "civile ou un instant avec fuseau"
            )
        return instant
    raise TypeError(
        f"une date ou un instant est attendu, reçu : {type(valeur).__name__}"
    )


DateOuInstant = Annotated[date | datetime, BeforeValidator(lire_date_ou_instant)]
