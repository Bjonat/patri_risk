"""Lecture en flux du CSV Mérimée, hors réseau."""

from __future__ import annotations

import csv
from collections.abc import Iterator
from pathlib import Path

from patri_risk.exceptions import ErreurUtilisateur
from patri_risk.sources.merimee.constantes import (
    CHAMP_CODE_INSEE_COURANT,
    CHAMP_DEPARTEMENT,
    COLONNES_OBLIGATOIRES,
    ENCODAGE,
    SEPARATEUR,
)


def extraire_cellule(contenu: dict[str, str | None], champ: str) -> str | None:
    """Retourne la cellule stripée, ou ``None`` si elle est vide."""
    valeur = contenu.get(champ)
    if valeur is None:
        return None
    texte = valeur.strip()
    return texte or None


def code_departement_source(contenu: dict[str, str | None]) -> str | None:
    return extraire_cellule(contenu, CHAMP_DEPARTEMENT)


def appartient_au_departement(
    contenu: dict[str, str | None],
    departement: str,
) -> bool:
    """Compare le code département source au code demandé, sans texte libre."""
    brut = code_departement_source(contenu)
    if brut is None:
        return False
    return brut == departement.strip()


def verifier_colonnes(noms: list[str] | None) -> None:
    if not noms:
        raise ErreurUtilisateur("Le fichier Mérimée ne contient pas d'en-tête CSV.")
    absentes = [colonne for colonne in COLONNES_OBLIGATOIRES if colonne not in noms]
    if absentes:
        raise ErreurUtilisateur(
            f'La colonne obligatoire "{absentes[0]}" est absente du CSV.'
        )


def lire_noms_colonnes(chemin: Path) -> list[str]:
    """Lit uniquement l'en-tête du CSV."""
    chemin = Path(chemin)
    if not chemin.is_file():
        raise ErreurUtilisateur("Le fichier Mérimée est introuvable.")
    with chemin.open(encoding=ENCODAGE, newline="") as fichier:
        lecteur = csv.DictReader(fichier, delimiter=SEPARATEUR)
        verifier_colonnes(lecteur.fieldnames)
        return list(lecteur.fieldnames or [])


def detecter_colonne_code_insee(noms: list[str] | None) -> str | None:
    """Retourne le nom de colonne du code INSEE courant s'il est présent.

    Le snapshot inspecté le 8 septembre 2026 n'a pas cette colonne.
    ``Code_Insee`` est un candidat de schéma, pas une observation de ce millésime.
    """
    if not noms:
        return None
    if CHAMP_CODE_INSEE_COURANT in noms:
        return CHAMP_CODE_INSEE_COURANT
    return None


def iterer_lignes_merimee(
    chemin: Path,
    *,
    departement: str | None = None,
) -> Iterator[tuple[int, dict[str, str]]]:
    """Lit le CSV en streaming.

    Yield ``(numero_ligne, contenu)`` pour chaque ligne de données retenue.
    ``numero_ligne`` est 1-indexé (l'en-tête est la ligne 1).
    """
    chemin = Path(chemin)
    if not chemin.is_file():
        raise ErreurUtilisateur("Le fichier Mérimée est introuvable.")

    with chemin.open(encoding=ENCODAGE, newline="") as fichier:
        lecteur = csv.DictReader(fichier, delimiter=SEPARATEUR)
        verifier_colonnes(lecteur.fieldnames)
        for index, ligne in enumerate(lecteur, start=2):
            if ligne is None:
                continue
            contenu = {cle: (valeur or "") for cle, valeur in ligne.items() if cle}
            if not any(valeur.strip() for valeur in contenu.values()):
                continue
            if departement is not None and not appartient_au_departement(
                contenu, departement
            ):
                continue
            yield index, contenu


def compter_lignes_nationales(chemin: Path) -> int:
    """Compte les lignes de données non vides, sans tout charger en mémoire."""
    total = 0
    for _numero, _contenu in iterer_lignes_merimee(chemin):
        total += 1
    return total
