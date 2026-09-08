"""Interface en ligne de commande.

Commandes disponibles :
``version``, ``diagnostic``, ``merimee collecter``, ``merimee normaliser``.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from patri_risk import VERSION_CONTRAT_DONNEES, __version__
from patri_risk.exceptions import ErreurUtilisateur
from patri_risk.sources.merimee.constantes import DEPARTEMENT_REFERENCE


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

    sous_commandes.add_parser("version", help="Affiche la version du paquet.")
    sous_commandes.add_parser(
        "diagnostic",
        help="Contrôle l'environnement local d'exécution.",
    )

    analyseur_merimee = sous_commandes.add_parser(
        "merimee",
        help="Collecte et normalisation de l'export Mérimée.",
    )
    sous_merimee = analyseur_merimee.add_subparsers(
        dest="commande_merimee",
        required=True,
    )
    collecter = sous_merimee.add_parser(
        "collecter",
        help="Télécharge le CSV national Mérimée et écrit le manifeste.",
    )
    collecter.add_argument(
        "--repertoire",
        default="donnees/brutes/merimee",
        help="Répertoire de destination des snapshots.",
    )
    normaliser = sous_merimee.add_parser(
        "normaliser",
        help="Normalise un snapshot CSV local, hors réseau.",
    )
    normaliser.add_argument(
        "--departement",
        default=DEPARTEMENT_REFERENCE,
        help="Code département à retenir (défaut : 31, Haute-Garonne).",
    )
    normaliser.add_argument(
        "--fichier",
        required=True,
        help="Chemin du snapshot CSV Mérimée.",
    )
    normaliser.add_argument(
        "--manifeste",
        default=None,
        help="Chemin du manifeste JSON. Défaut : <fichier>.manifeste.json",
    )
    normaliser.add_argument(
        "--sortie",
        default=None,
        help="Répertoire des fichiers produits (JSONL, rapport, anomalies).",
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


def _formater_entier(valeur: int) -> str:
    return f"{valeur:,}".replace(",", " ")


def executer_collecte(repertoire: str) -> int:
    from patri_risk.sources.merimee.collecte import collecter_merimee

    manifeste = collecter_merimee(Path(repertoire))
    chemin_csv = Path(repertoire) / manifeste.nom_fichier
    chemin_manifeste = Path(repertoire) / f"{chemin_csv.stem}.manifeste.json"
    print("Collecte Mérimée terminée.")
    print(f"Fichier : {chemin_csv}")
    print(f"Taille : {_formater_entier(manifeste.taille_octets)} octets")
    print(f"SHA-256 : {manifeste.empreinte_sha256}")
    print(f"Manifeste : {chemin_manifeste}")
    return 0


def executer_normalisation(
    *,
    departement: str,
    fichier: str,
    manifeste: str | None,
    sortie: str | None,
) -> int:
    from patri_risk.sources.merimee.pipeline import (
        charger_manifeste,
        chemin_manifeste_associe,
        normaliser_fichier_merimee,
    )

    chemin_csv = Path(fichier)
    if not chemin_csv.is_file():
        raise ErreurUtilisateur("Le fichier Mérimée est introuvable.")
    chemin_manifeste = (
        Path(manifeste) if manifeste else chemin_manifeste_associe(chemin_csv)
    )
    if sortie:
        repertoire_sortie = Path(sortie)
    else:
        repertoire_sortie = Path("donnees/traitees/merimee") / departement.strip()
    manifeste_charge = charger_manifeste(chemin_manifeste)
    rapport = normaliser_fichier_merimee(
        chemin_csv,
        manifeste_charge,
        departement=departement,
        repertoire_sortie=repertoire_sortie,
    )
    print("Normalisation Mérimée terminée.")
    print()
    print(f"Département : {rapport.departement}")
    print(f"Lignes nationales : {_formater_entier(rapport.nombre_lignes_total)}")
    print(
        f"Lignes Haute-Garonne : {_formater_entier(rapport.nombre_lignes_departement)}"
    )
    dossiers = _formater_entier(rapport.nombre_dossiers_produits)
    print(f"Dossiers produits : {dossiers}")
    absentes = _formater_entier(rapport.nombre_coordonnees_absentes)
    print(f"Coordonnées absentes : {absentes}")
    print(f"Anomalies : {_formater_entier(rapport.nombre_anomalies)}")
    print()
    print(f"Données : {repertoire_sortie / 'monuments.jsonl'}")
    print(f"Rapport : {repertoire_sortie / 'rapport.json'}")
    print(f"Anomalies : {repertoire_sortie / 'anomalies.jsonl'}")
    return 0


def principal(arguments: Sequence[str] | None = None) -> int:
    """Exécute la CLI et retourne un code de sortie."""
    analyseur = construire_analyseur()
    try:
        args = analyseur.parse_args(arguments)
        if args.commande == "version":
            afficher_version()
            return 0
        if args.commande == "diagnostic":
            afficher_diagnostic()
            return 0
        if args.commande == "merimee":
            if args.commande_merimee == "collecter":
                return executer_collecte(args.repertoire)
            if args.commande_merimee == "normaliser":
                return executer_normalisation(
                    departement=args.departement,
                    fichier=args.fichier,
                    manifeste=args.manifeste,
                    sortie=args.sortie,
                )
            raise AssertionError(
                f"Commande Mérimée inattendue : {args.commande_merimee}"
            )
        raise AssertionError(f"Commande inattendue : {args.commande}")
    except ErreurUtilisateur as erreur:
        print(erreur.message, file=sys.stderr)
        return erreur.code_sortie


def point_entree() -> None:
    """Point d'entrée de la commande ``patri-risk``."""
    raise SystemExit(principal())
