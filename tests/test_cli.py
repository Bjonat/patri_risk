"""Tests de la CLI, hors ligne et déterministes."""

import hashlib
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from patri_risk import VERSION_CONTRAT_DONNEES, __version__
from patri_risk.cli import principal
from patri_risk.modeles import ManifesteCollecte
from patri_risk.sources.merimee.constantes import URL_RESSOURCE


def test_commande_version(capsys: pytest.CaptureFixture[str]) -> None:
    code = principal(["version"])
    sortie = capsys.readouterr().out
    assert code == 0
    assert sortie.strip() == f"patri-risk {__version__}"
    assert "0.1.0-dev" in sortie


def test_commande_diagnostic(capsys: pytest.CaptureFixture[str]) -> None:
    code = principal(["diagnostic"])
    sortie = capsys.readouterr().out
    assert code == 0
    assert "Installation valide." in sortie
    assert "Python :" in sortie
    assert f"patri-risk : {__version__}" in sortie
    assert f"Contrat de données : {VERSION_CONTRAT_DONNEES}" in sortie


def test_commande_version_via_module() -> None:
    resultat = subprocess.run(
        [sys.executable, "-m", "patri_risk", "version"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert resultat.returncode == 0
    assert resultat.stdout.strip() == f"patri-risk {__version__}"
    assert resultat.stderr == ""


def test_commande_inconnue_renvoie_une_erreur() -> None:
    with pytest.raises(SystemExit):
        principal(["analyser"])


def test_commande_merimee_fichier_introuvable(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = principal(["merimee", "normaliser", "--fichier", "absent-merimee.csv"])
    erreur = capsys.readouterr().err
    assert code == 1
    assert "Le fichier Mérimée est introuvable." in erreur


def test_commande_normaliser_affiche_le_departement_demande(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    csv = Path(__file__).parent / "fixtures" / "merimee_extrait.csv"
    manifeste = ManifesteCollecte(
        source="Mérimée",
        url_ressource=URL_RESSOURCE,
        date_collecte=datetime(2026, 9, 8, 19, 0, tzinfo=UTC),
        empreinte_sha256=hashlib.sha256(csv.read_bytes()).hexdigest(),
        taille_octets=csv.stat().st_size,
        licence="Licence Ouverte / Open Licence version 2.0",
        nom_fichier=csv.name,
        format="csv",
    )
    chemin_manifeste = tmp_path / "extrait.manifeste.json"
    chemin_manifeste.write_text(manifeste.model_dump_json(), encoding="utf-8")
    code = principal(
        [
            "merimee",
            "normaliser",
            "--departement",
            "31",
            "--fichier",
            str(csv),
            "--manifeste",
            str(chemin_manifeste),
            "--sortie",
            str(tmp_path / "out"),
        ]
    )
    sortie = capsys.readouterr().out
    assert code == 0
    assert "Lignes du département 31 :" in sortie
    assert "Lignes Haute-Garonne" not in sortie
