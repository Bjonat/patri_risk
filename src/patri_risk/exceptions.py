"""Erreurs destinées à l'utilisateur de la CLI."""

from __future__ import annotations


class ErreurUtilisateur(Exception):
    """Erreur explicable, sans traceback pour un usage normal."""

    def __init__(self, message: str, code_sortie: int = 1) -> None:
        super().__init__(message)
        self.message = message
        self.code_sortie = code_sortie
