"""Tests hors ligne de la lecture du CSV Mérimée."""

from __future__ import annotations

from pathlib import Path

import pytest

from patri_risk.exceptions import ErreurUtilisateur
from patri_risk.sources.merimee.constantes import ENCODAGE, SEPARATEUR
from patri_risk.sources.merimee.lecture import iterer_lignes_merimee

FIXTURE = Path(__file__).parent / "fixtures" / "merimee_extrait.csv"


def test_lecture_separateur_et_encodage() -> None:
    texte = FIXTURE.read_text(encoding=ENCODAGE)
    assert SEPARATEUR in texte.splitlines()[0]
    assert "é" in texte or "Église" in texte or "édifice" in texte


def test_filtrage_departement_31() -> None:
    lignes = list(iterer_lignes_merimee(FIXTURE, departement="31"))
    references = [contenu["Reference"] for _numero, contenu in lignes]
    assert "PA00075000" not in references
    assert all(
        contenu["Departement_format_numerique"] == "31" for _n, contenu in lignes
    )


def test_conservation_des_cellules_originales() -> None:
    _numero, contenu = next(iterer_lignes_merimee(FIXTURE, departement="31"))
    assert "Titre_editorial_de_la_notice" in contenu
    assert "Reference" in contenu


def test_colonne_obligatoire_absente(tmp_path: Path) -> None:
    chemin = tmp_path / "mauvais.csv"
    chemin.write_text("Foo|Bar\n1|2\n", encoding="utf-8")
    with pytest.raises(ErreurUtilisateur, match='colonne obligatoire "Reference"'):
        list(iterer_lignes_merimee(chemin))


def test_fichier_introuvable(tmp_path: Path) -> None:
    with pytest.raises(ErreurUtilisateur, match="introuvable"):
        list(iterer_lignes_merimee(tmp_path / "absent.csv"))


def test_ligne_vide_ignoree(tmp_path: Path) -> None:
    chemin = tmp_path / "vide.csv"
    chemin.write_text(
        "Reference|Departement_format_numerique\nPA00094321|31\n\nPA00094322|31\n",
        encoding="utf-8",
    )
    lignes = list(iterer_lignes_merimee(chemin))
    assert len(lignes) == 2
