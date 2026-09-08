"""Vérification d'intégrité d'un artefact local contre son manifeste."""

from __future__ import annotations

import hashlib
from pathlib import Path

from patri_risk.exceptions import ErreurUtilisateur
from patri_risk.modeles import ManifesteCollecte
from patri_risk.sources.merimee.constantes import TAILLE_BLOC_TELECHARGEMENT


def calculer_empreinte_et_taille(chemin: Path) -> tuple[str, int]:
    """Calcule SHA-256 et taille en flux, sans charger le fichier en mémoire."""
    hasher = hashlib.sha256()
    taille = 0
    with Path(chemin).open("rb") as fichier:
        while True:
            bloc = fichier.read(TAILLE_BLOC_TELECHARGEMENT)
            if not bloc:
                break
            hasher.update(bloc)
            taille += len(bloc)
    return hasher.hexdigest(), taille


def verifier_integrite_artefact(chemin: Path, manifeste: ManifesteCollecte) -> None:
    """Refuse de normaliser un CSV qui n'est pas l'artefact du manifeste.

    L'identité de l'artefact est le contenu (taille + SHA-256), pas le nom
    de fichier.
    """
    chemin = Path(chemin)
    if not chemin.is_file():
        raise ErreurUtilisateur("Le fichier Mérimée est introuvable.")
    empreinte, taille = calculer_empreinte_et_taille(chemin)
    if taille != manifeste.taille_octets:
        raise ErreurUtilisateur(
            "Le snapshot Mérimée ne correspond pas au manifeste : taille différente."
        )
    if empreinte != manifeste.empreinte_sha256:
        raise ErreurUtilisateur(
            "Le snapshot Mérimée ne correspond pas au manifeste : "
            "empreinte SHA-256 différente."
        )
