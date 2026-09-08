"""Tests hors ligne de la collecte Mérimée."""

from __future__ import annotations

import hashlib
import io
from datetime import UTC, datetime
from pathlib import Path

import pytest

from patri_risk.exceptions import ErreurUtilisateur
from patri_risk.sources.merimee.collecte import collecter_merimee


class FluxFactice:
    """Réponse HTTP minimale, sans réseau."""

    def __init__(
        self,
        contenu: bytes,
        en_tetes: dict[str, str] | None = None,
        erreur_apres: int | None = None,
    ) -> None:
        self._tampon = io.BytesIO(contenu)
        self.headers = en_tetes or {}
        self._erreur_apres = erreur_apres
        self._lus = 0

    def read(self, taille: int = -1) -> bytes:
        if self._erreur_apres is not None and self._lus >= self._erreur_apres:
            raise OSError("connexion interrompue")
        bloc = self._tampon.read(taille)
        self._lus += len(bloc)
        if self._erreur_apres is not None and self._lus >= self._erreur_apres:
            raise OSError("connexion interrompue")
        return bloc

    def __enter__(self) -> FluxFactice:
        return self

    def __exit__(self, *_args: object) -> None:
        return None


def test_collecte_ecrit_snapshot_et_manifeste(tmp_path: Path) -> None:
    contenu = b"Reference|Departement_format_numerique\nPA00094321|31\n"
    empreinte = hashlib.sha256(contenu).hexdigest()
    instant = datetime(2026, 9, 8, 19, 15, tzinfo=UTC)

    def ouvrir(_url: str) -> FluxFactice:
        return FluxFactice(
            contenu,
            en_tetes={
                "ETag": '"abc123"',
                "Last-Modified": "Thu, 03 Sep 2026 01:16:41 GMT",
            },
        )

    manifeste = collecter_merimee(
        tmp_path,
        ouvrir=ouvrir,
        date_collecte=instant,
    )
    assert manifeste.empreinte_sha256 == empreinte
    assert manifeste.taille_octets == len(contenu)
    assert manifeste.etag == "abc123"
    assert manifeste.derniere_modification_http == "Thu, 03 Sep 2026 01:16:41 GMT"
    csv_final = tmp_path / manifeste.nom_fichier
    assert csv_final.is_file()
    assert csv_final.read_bytes() == contenu
    manifeste_chemin = tmp_path / f"{csv_final.stem}.manifeste.json"
    assert manifeste_chemin.is_file()
    assert not (tmp_path / ".merimee-telechargement.tmp").exists()
    assert manifeste.nom_fichier.startswith("merimee-20260908T191500Z-")


def test_collecte_interrompu_ne_laisse_pas_de_snapshot(tmp_path: Path) -> None:
    contenu = b"x" * 10_000

    def ouvrir(_url: str) -> FluxFactice:
        return FluxFactice(contenu, erreur_apres=100)

    with pytest.raises(
        ErreurUtilisateur, match="téléchargement du fichier Mérimée a échoué"
    ):
        collecter_merimee(tmp_path, ouvrir=ouvrir)

    restants = list(tmp_path.iterdir())
    assert restants == []
