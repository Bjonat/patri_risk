"""Tests hors ligne de la normalisation Mérimée."""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

from patri_risk.modeles import (
    EnregistrementBrut,
    ManifesteCollecte,
    MethodeObtention,
    SourceDonnee,
)
from patri_risk.sources.merimee.constantes import URL_RESSOURCE
from patri_risk.sources.merimee.lecture import extraire_cellule, iterer_lignes_merimee
from patri_risk.sources.merimee.normalisation import (
    choisir_nom,
    interpreter_coordonnees,
    normaliser_enregistrement_merimee,
)
from patri_risk.sources.merimee.pipeline import (
    charger_manifeste,
    normaliser_fichier_merimee,
)

FIXTURE = Path(__file__).parent / "fixtures" / "merimee_extrait.csv"
INSTANT = datetime(2026, 9, 8, 19, 0, tzinfo=UTC)


def _source() -> SourceDonnee:
    return SourceDonnee(
        producteur="Ministère de la Culture",
        jeu_donnees="Mérimée",
        identifiant_enregistrement="PA00094322",
        url=URL_RESSOURCE,
        date_collecte=INSTANT,
        licence="Licence Ouverte / Open Licence version 2.0",
        empreinte_artefact="sha256:" + "ab" * 32,
    )


def _manifeste_pour(chemin_csv: Path) -> ManifesteCollecte:
    empreinte = __import__("hashlib").sha256(chemin_csv.read_bytes()).hexdigest()
    return ManifesteCollecte(
        source="Mérimée",
        url_ressource=URL_RESSOURCE,
        date_collecte=INSTANT,
        empreinte_sha256=empreinte,
        taille_octets=chemin_csv.stat().st_size,
        licence="Licence Ouverte / Open Licence version 2.0",
        nom_fichier=chemin_csv.name,
        format="csv",
    )


def _contenu(reference: str) -> dict[str, str]:
    for _numero, contenu in iterer_lignes_merimee(FIXTURE):
        if contenu.get("Reference") == reference:
            return contenu
    raise AssertionError(reference)


def test_choisir_nom_privilegie_le_titre_editorial() -> None:
    contenu = _contenu("PA00094322")
    assert choisir_nom(contenu) == "Hôtel d'Assézat"


def test_coordonnees_valides_lat_lon() -> None:
    latitude, longitude, anomalie = interpreter_coordonnees(
        "43.6083,1.4419",
        reference="PA1",
        numero_ligne=2,
    )
    assert anomalie is None
    assert latitude == 43.6083
    assert longitude == 1.4419


def test_coordonnees_absentes() -> None:
    latitude, longitude, anomalie = interpreter_coordonnees(
        None, reference="PA1", numero_ligne=2
    )
    assert latitude is None
    assert longitude is None
    assert anomalie is None


def test_coordonnees_invalides() -> None:
    latitude, longitude, anomalie = interpreter_coordonnees(
        "invalide", reference="PA1", numero_ligne=2
    )
    assert latitude is None
    assert longitude is None
    assert anomalie is not None
    assert anomalie.type == "coordonnees_invalides"


def test_coordonnees_inversion_non_corrigee() -> None:
    latitude, longitude, anomalie = interpreter_coordonnees(
        "1.44,43.60", reference="PA1", numero_ligne=2
    )
    assert latitude is None
    assert longitude is None
    assert anomalie is not None


def test_normalisation_monument_complet() -> None:
    contenu = _contenu("PA00094322")
    enregistrement = EnregistrementBrut(source=_source(), contenu=contenu)
    dossier, anomalies = normaliser_enregistrement_merimee(
        enregistrement, numero_ligne=3
    )
    assert dossier is not None
    assert anomalies == []
    assert dossier.identite.reference == "PA00094322"
    assert dossier.identite.nom == "Hôtel d'Assézat"
    assert dossier.identite.nom_commune == "Toulouse"
    assert dossier.identite.code_commune is None
    assert dossier.identite.code_departement == "31"
    assert dossier.identite.latitude is None
    assert dossier.identite.longitude is None
    preuves = {preuve.champ: preuve for preuve in dossier.preuves}
    assert "etat_conservation_merimee" not in preuves
    assert preuves["nature_protection"].valeur == "arrêté"
    assert preuves["nature_protection"].methode_obtention == MethodeObtention.DIRECTE
    assert preuves["nature_protection"].niveau_confiance == 1.0
    assert (
        preuves["nature_protection"].source.empreinte_artefact == "sha256:" + "ab" * 32
    )
    assert preuves["date_mise_a_jour_notice"].date_observation == date(2026, 7, 24)


def test_cellule_vide_sans_fausse_preuve() -> None:
    contenu = _contenu("PA00094325")
    dossier, _anomalies = normaliser_enregistrement_merimee(
        EnregistrementBrut(source=_source(), contenu=contenu),
        numero_ligne=9,
    )
    assert dossier is not None
    assert dossier.preuves_pour_champ("etat_conservation_merimee") == []
    assert dossier.preuves_pour_champ("identifiant_agregee") == []


def test_reference_format_inattendu_conservee() -> None:
    contenu = _contenu("XX99999999")
    dossier, anomalies = normaliser_enregistrement_merimee(
        EnregistrementBrut(source=_source(), contenu=contenu),
        numero_ligne=6,
    )
    assert dossier is not None
    assert dossier.identite.reference == "XX99999999"
    assert any(anomalie.type == "reference_format_inattendu" for anomalie in anomalies)


def test_pipeline_doublons_en_quarantaine(tmp_path: Path) -> None:
    manifeste = _manifeste_pour(FIXTURE)
    rapport = normaliser_fichier_merimee(
        FIXTURE,
        manifeste,
        departement="31",
        repertoire_sortie=tmp_path,
    )
    assert "PA00094321" in rapport.references_dupliquees
    assert rapport.nombre_doublons_reference == 1
    assert rapport.nombre_lignes_en_quarantaine == 2
    texte = (tmp_path / "monuments.jsonl").read_text(encoding="utf-8")
    assert "PA00094321" not in texte
    assert rapport.nombre_dossiers_produits >= 1


def test_pipeline_deterministe(tmp_path: Path) -> None:
    manifeste = _manifeste_pour(FIXTURE)
    premiere = tmp_path / "a"
    seconde = tmp_path / "b"
    normaliser_fichier_merimee(FIXTURE, manifeste, repertoire_sortie=premiere)
    normaliser_fichier_merimee(FIXTURE, manifeste, repertoire_sortie=seconde)
    assert (premiere / "monuments.jsonl").read_bytes() == (
        seconde / "monuments.jsonl"
    ).read_bytes()
    assert (premiere / "rapport.json").read_bytes() == (
        seconde / "rapport.json"
    ).read_bytes()
    assert (premiere / "anomalies.jsonl").read_bytes() == (
        seconde / "anomalies.jsonl"
    ).read_bytes()


def test_pipeline_filtre_hors_departement(tmp_path: Path) -> None:
    rapport = normaliser_fichier_merimee(
        FIXTURE,
        _manifeste_pour(FIXTURE),
        repertoire_sortie=tmp_path,
    )
    texte = (tmp_path / "monuments.jsonl").read_text(encoding="utf-8")
    assert "PA00075000" not in texte
    assert rapport.nombre_lignes_total > rapport.nombre_lignes_departement


def test_jsonl_ne_se_casse_pas_sur_un_separateur_unicode(tmp_path: Path) -> None:
    import json

    from patri_risk.sources.merimee.pipeline import _ecrire_jsonl

    payload = '{"valeur": "fontaine, bassin\u0085, jardin"}'
    _ecrire_jsonl(tmp_path / "x.jsonl", [payload])
    ligne = (tmp_path / "x.jsonl").read_text(encoding="utf-8").split("\n")[0]
    relu = json.loads(ligne)
    assert "bassin" in relu["valeur"]


def test_charger_manifeste_sidecar(tmp_path: Path) -> None:
    manifeste = _manifeste_pour(FIXTURE)
    chemin = tmp_path / "x.manifeste.json"
    chemin.write_text(manifeste.model_dump_json(), encoding="utf-8")
    relu = charger_manifeste(chemin)
    assert relu.empreinte_sha256 == manifeste.empreinte_sha256


def test_coordonnees_valides_dans_le_pipeline(tmp_path: Path) -> None:
    rapport = normaliser_fichier_merimee(
        FIXTURE,
        _manifeste_pour(FIXTURE),
        repertoire_sortie=tmp_path,
    )
    assert rapport.nombre_coordonnees_absentes >= 1
    assert rapport.nombre_coordonnees_invalides >= 2
    assert rapport.nombre_codes_commune_absents == rapport.nombre_dossiers_produits
    assert extraire_cellule({"x": "  "}, "x") is None
