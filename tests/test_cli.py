"""Tests de la CLI, hors ligne et déterministes."""

import subprocess
import sys

import pytest

from patri_risk import VERSION_CONTRAT_DONNEES, __version__
from patri_risk.cli import principal


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
