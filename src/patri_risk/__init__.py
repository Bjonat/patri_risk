"""patri_risk — moteur d'agrégation de preuves patrimoniales publiques.

Le domaine métier est exprimé en français. Les API Python et les
bibliothèques externes conservent leurs noms d'origine.
"""

from patri_risk.modeles import (
    DossierMonument,
    EnregistrementBrut,
    IdentiteMonument,
    MethodeObtention,
    Preuve,
    SourceDonnee,
)

__version__ = "0.1.0-dev"
VERSION_CONTRAT_DONNEES = "PatrimoineEvidence v0.1"

__all__ = [
    "DossierMonument",
    "EnregistrementBrut",
    "IdentiteMonument",
    "MethodeObtention",
    "Preuve",
    "SourceDonnee",
    "VERSION_CONTRAT_DONNEES",
    "__version__",
]
