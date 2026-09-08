"""Tests hors ligne de l'intégrité snapshot / manifeste."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import pytest

from patri_risk.cli import principal
from patri_risk.exceptions import ErreurUtilisateur
from patri_risk.modeles import ManifesteCollecte
from patri_risk.sources.merimee.constantes import URL_RESSOURCE
from patri_risk.sources.merimee.integrite import verifier_integrite_artefact
from patri_risk.sources.merimee.pipeline import normaliser_fichier_merimee

FIXTURE = Path(__file__).parent / "fixtures" / "merimee_extrait.csv"
INSTANT = datetime(2026, 9, 8, 19, 0, tzinfo=UTC)


def _manifeste_pour(
    chemin_csv: Path,
    *,
    empreinte_sha256: str | None = None,
    taille_octets: int | None = None,
) -> ManifesteCollecte:
    return ManifesteCollecte(
        source="Mérimée",
        url_ressource=URL_RESSOURCE,
        date_collecte=INSTANT,
        empreinte_sha256=empreinte_sha256
        or hashlib.sha256(chemin_csv.read_bytes()).hexdigest(),
        taille_octets=taille_octets
        if taille_octets is not None
        else chemin_csv.stat().st_size,
        licence="Licence Ouverte / Open Licence version 2.0",
        nom_fichier=chemin_csv.name,
        format="csv",
    )


def test_integrite_accepte_le_snapshot_du_manifeste() -> None:
    verifier_integrite_artefact(FIXTURE, _manifeste_pour(FIXTURE))


def test_integrite_refuse_un_sha_different() -> None:
    manifeste = _manifeste_pour(FIXTURE)
    manifeste_faux = manifeste.model_copy(update={"empreinte_sha256": "ab" * 32})
    with pytest.raises(ErreurUtilisateur, match="empreinte SHA-256 différente"):
        verifier_integrite_artefact(FIXTURE, manifeste_faux)


def test_integrite_refuse_une_taille_differente() -> None:
    manifeste = _manifeste_pour(FIXTURE)
    manifeste_faux = manifeste.model_copy(
        update={"taille_octets": manifeste.taille_octets + 1}
    )
    with pytest.raises(ErreurUtilisateur, match="taille différente"):
        verifier_integrite_artefact(FIXTURE, manifeste_faux)


def test_pipeline_ne_produit_rien_si_integrite_invalide(tmp_path: Path) -> None:
    manifeste = _manifeste_pour(FIXTURE)
    manifeste_faux = manifeste.model_copy(update={"taille_octets": 1})
    sortie = tmp_path / "sortie"
    with pytest.raises(ErreurUtilisateur, match="taille différente"):
        normaliser_fichier_merimee(
            FIXTURE,
            manifeste_faux,
            repertoire_sortie=sortie,
        )
    assert not (sortie / "monuments.jsonl").exists()
    assert not (sortie / "rapport.json").exists()
    assert not (sortie / "anomalies.jsonl").exists()


def test_integrite_accepte_un_fichier_renomme_aux_memes_octets(
    tmp_path: Path,
) -> None:
    copie = tmp_path / "copie.csv"
    copie.write_bytes(FIXTURE.read_bytes())
    manifeste = _manifeste_pour(FIXTURE)
    assert manifeste.nom_fichier != copie.name
    verifier_integrite_artefact(copie, manifeste)
    rapport = normaliser_fichier_merimee(
        copie,
        manifeste,
        repertoire_sortie=tmp_path / "ok",
    )
    assert rapport.nombre_dossiers_produits >= 1
    assert (tmp_path / "ok" / "monuments.jsonl").is_file()


def test_cli_integrite_invalide_code_non_nul(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    manifeste = _manifeste_pour(FIXTURE).model_copy(update={"taille_octets": 1})
    chemin_manifeste = tmp_path / "faux.manifeste.json"
    chemin_manifeste.write_text(manifeste.model_dump_json(), encoding="utf-8")
    sortie = tmp_path / "sortie"
    code = principal(
        [
            "merimee",
            "normaliser",
            "--fichier",
            str(FIXTURE),
            "--manifeste",
            str(chemin_manifeste),
            "--sortie",
            str(sortie),
        ]
    )
    erreur = capsys.readouterr().err
    assert code != 0
    assert "taille différente" in erreur
    assert not (sortie / "monuments.jsonl").exists()
    assert not (sortie / "rapport.json").exists()
    assert not (sortie / "anomalies.jsonl").exists()
