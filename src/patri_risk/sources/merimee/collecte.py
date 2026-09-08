"""Collecte en flux de l'export CSV national Mérimée."""

from __future__ import annotations

import hashlib
import os
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from patri_risk.exceptions import ErreurUtilisateur
from patri_risk.modeles import ManifesteCollecte
from patri_risk.sources.merimee.constantes import (
    FORMAT_FICHIER,
    JEU_DONNEES,
    LICENCE,
    TAILLE_BLOC_TELECHARGEMENT,
    URL_RESSOURCE,
    USER_AGENT,
)


def ouvrir_url(url: str, timeout: int = 300) -> Any:
    """Ouvre l'URL officielle. L'objet exposé doit fournir ``read`` et ``headers``."""
    requete = Request(url, headers={"User-Agent": USER_AGENT})
    return urlopen(requete, timeout=timeout)


def _lire_entete(reponse: object, nom: str) -> str | None:
    en_tetes = getattr(reponse, "headers", None)
    if en_tetes is None or not hasattr(en_tetes, "get"):
        return None
    valeur = en_tetes.get(nom) or en_tetes.get(nom.lower())
    if not valeur:
        return None
    return str(valeur)


def _ecrire_depuis_reponse(reponse: object, chemin_temporaire: Path) -> tuple[str, int]:
    hasher = hashlib.sha256()
    taille = 0
    with chemin_temporaire.open("wb") as fichier:
        while True:
            bloc = reponse.read(TAILLE_BLOC_TELECHARGEMENT)
            if not bloc:
                break
            hasher.update(bloc)
            fichier.write(bloc)
            taille += len(bloc)
    return hasher.hexdigest(), taille


def collecter_merimee(
    repertoire: Path,
    url: str = URL_RESSOURCE,
    *,
    ouvrir: Callable[[str], Any] = ouvrir_url,
    date_collecte: datetime | None = None,
) -> ManifesteCollecte:
    """Télécharge le CSV Mérimée, calcule le SHA-256 et écrit le manifeste.

    Le fichier final n'est créé qu'après un téléchargement complet.
    """
    repertoire = Path(repertoire)
    repertoire.mkdir(parents=True, exist_ok=True)
    instant = date_collecte or datetime.now(UTC)
    tampon = repertoire / ".merimee-telechargement.tmp"
    if tampon.exists():
        tampon.unlink()

    etag: str | None = None
    derniere_modification: str | None = None
    try:
        reponse = ouvrir(url)
        contexte = getattr(reponse, "__enter__", None)
        if callable(contexte):
            reponse = reponse.__enter__()
        try:
            empreinte, taille = _ecrire_depuis_reponse(reponse, tampon)
            etag_brut = _lire_entete(reponse, "ETag")
            etag = etag_brut.strip('"') if etag_brut else None
            derniere_modification = _lire_entete(reponse, "Last-Modified")
        finally:
            sortir = getattr(reponse, "__exit__", None)
            if callable(sortir):
                reponse.__exit__(None, None, None)
            else:
                fermer = getattr(reponse, "close", None)
                if callable(fermer):
                    fermer()
    except ErreurUtilisateur:
        if tampon.exists():
            tampon.unlink()
        raise
    except (OSError, URLError, TimeoutError) as erreur:
        if tampon.exists():
            tampon.unlink()
        raise ErreurUtilisateur(
            "Le téléchargement du fichier Mérimée a échoué."
        ) from erreur
    except Exception:
        if tampon.exists():
            tampon.unlink()
        raise

    horodatage = instant.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
    nom_fichier = f"merimee-{horodatage}-{empreinte[:8]}.csv"
    chemin_final = repertoire / nom_fichier
    os.replace(tampon, chemin_final)

    manifeste = ManifesteCollecte(
        source=JEU_DONNEES,
        url_ressource=url,
        date_collecte=instant,
        empreinte_sha256=empreinte,
        taille_octets=taille,
        licence=LICENCE,
        nom_fichier=nom_fichier,
        format=FORMAT_FICHIER,
        etag=etag,
        derniere_modification_http=derniere_modification,
    )
    chemin_manifeste = repertoire / f"{chemin_final.stem}.manifeste.json"
    chemin_manifeste.write_text(
        manifeste.model_dump_json(indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifeste
