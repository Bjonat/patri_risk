"""Interface en ligne de commande minimale.

Les commandes disponibles dans PR-0 se limitent à ce que le paquet
sait réellement faire : afficher sa version et contrôler l'environnement
local. Aucune analyse patrimoniale n'est simulée.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from patri_risk import VERSION_CONTRAT_DONNEES, __version__


def construire_analyseur() -> argparse.ArgumentParser:
    """Construit l'analyseur des arguments de ``patri-risk``."""
    analyseur = argparse.ArgumentParser(
        prog="patri-risk",
        description=(
            "Moteur expérimental d'agrégation de preuves publiques "
            "relatives aux monuments historiques français."
        ),
    )
    sous_commandes = analyseur.add_subparsers(dest="commande", required=True)

    sous_commandes.add_parser(
        "version",
        help="Affiche la version du paquet.",
    )
    sous_commandes.add_parser(
        "diagnostic",
        help="Contrôle l'environnement local d'exécution.",
    )
    return analyseur


def afficher_version() -> None:
    """Affiche la version publique du paquet."""
    print(f"patri-risk {__version__}")


def afficher_diagnostic() -> None:
    """Affiche un contrôle réel de l'installation locale."""
    import pydantic

    version_python = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    print("Installation valide.")
    print(f"Python : {version_python}")
    print(f"patri-risk : {__version__}")
    print(f"pydantic : {pydantic.__version__}")
    print(f"Contrat de données : {VERSION_CONTRAT_DONNEES}")


def principal(arguments: Sequence[str] | None = None) -> int:
    """Exécute la CLI et retourne un code de sortie.

    Parameters
    ----------
    arguments
        Arguments à analyser. ``None`` lit ``sys.argv``.
    """
    analyseur = construire_analyseur()
    args = analyseur.parse_args(arguments)
    if args.commande == "version":
        afficher_version()
        return 0
    if args.commande == "diagnostic":
        afficher_diagnostic()
        return 0
    raise AssertionError(f"Commande inattendue : {args.commande}")


def point_entree() -> None:
    """Point d'entrée de la commande ``patri-risk``."""
    raise SystemExit(principal())
