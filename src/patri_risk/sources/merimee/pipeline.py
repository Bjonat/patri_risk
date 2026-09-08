"""Pipeline hors réseau : snapshot CSV → JSONL PatrimoineEvidence."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from patri_risk.exceptions import ErreurUtilisateur
from patri_risk.modeles import (
    AnomalieIngestion,
    DossierMonument,
    EnregistrementBrut,
    ManifesteCollecte,
    RapportIngestionMerimee,
)
from patri_risk.sources.merimee.constantes import (
    CHAMP_COORDONNEES,
    DEPARTEMENT_REFERENCE,
    URL_RESSOURCE,
)
from patri_risk.sources.merimee.integrite import verifier_integrite_artefact
from patri_risk.sources.merimee.lecture import (
    appartient_au_departement,
    detecter_colonne_code_insee,
    extraire_cellule,
    iterer_lignes_merimee,
    lire_noms_colonnes,
)
from patri_risk.sources.merimee.normalisation import (
    construire_source,
    normaliser_enregistrement_merimee,
)


def charger_manifeste(chemin: Path) -> ManifesteCollecte:
    if not Path(chemin).is_file():
        raise ErreurUtilisateur("Le manifeste de collecte Mérimée est introuvable.")
    return ManifesteCollecte.model_validate_json(
        Path(chemin).read_text(encoding="utf-8")
    )


def chemin_manifeste_associe(chemin_csv: Path) -> Path:
    return Path(chemin_csv).with_suffix(".manifeste.json")


def _securiser_jsonl(texte: str) -> str:
    """Évite que U+0085 / U+2028 / U+2029 cassent un lecteur JSONL."""
    return (
        texte.replace("\u0085", "\\u0085")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def _ecrire_jsonl(chemin: Path, lignes: list[str]) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding="utf-8", newline="\n") as fichier:
        for ligne in lignes:
            fichier.write(_securiser_jsonl(ligne.rstrip("\n")))
            fichier.write("\n")


def normaliser_fichier_merimee(
    chemin_csv: Path,
    manifeste: ManifesteCollecte,
    *,
    departement: str = DEPARTEMENT_REFERENCE,
    repertoire_sortie: Path,
) -> RapportIngestionMerimee:
    """Normalise un snapshot local. Aucun accès réseau."""
    verifier_integrite_artefact(chemin_csv, manifeste)
    departement = departement.strip()
    repertoire_sortie = Path(repertoire_sortie)
    colonne_code_insee = detecter_colonne_code_insee(lire_noms_colonnes(chemin_csv))

    source_commune = construire_source(
        identifiant_enregistrement=None,
        date_collecte=manifeste.date_collecte,
        empreinte_artefact=manifeste.empreinte_artefact(),
        url=manifeste.url_ressource or URL_RESSOURCE,
    )

    nombre_total = 0
    lignes_departement: list[tuple[int, dict[str, str]]] = []
    for numero, contenu in iterer_lignes_merimee(chemin_csv):
        nombre_total += 1
        if appartient_au_departement(contenu, departement):
            lignes_departement.append((numero, contenu))

    par_reference: dict[str, list[tuple[int, dict[str, str]]]] = defaultdict(list)
    sans_reference: list[tuple[int, dict[str, str]]] = []
    for numero, contenu in lignes_departement:
        reference = extraire_cellule(contenu, "Reference")
        if reference is None:
            sans_reference.append((numero, contenu))
        else:
            par_reference[reference].append((numero, contenu))

    anomalies: list[AnomalieIngestion] = []
    dossiers: list[DossierMonument] = []
    nombre_references_inattendues = 0
    nombre_coordonnees_absentes = 0
    nombre_coordonnees_invalides = 0
    nombre_codes_commune_absents = 0
    references_dupliquees: list[str] = []
    lignes_quarantaine = 0

    for numero, contenu in sans_reference:
        enregistrement = EnregistrementBrut(source=source_commune, contenu=contenu)
        _dossier, anomalies_ligne = normaliser_enregistrement_merimee(
            enregistrement,
            numero_ligne=numero,
            colonne_code_insee=colonne_code_insee,
        )
        anomalies.extend(anomalies_ligne)

    for reference, occurences in par_reference.items():
        if len(occurences) > 1:
            references_dupliquees.append(reference)
            lignes_quarantaine += len(occurences)
            numeros = ", ".join(str(numero) for numero, _contenu in occurences)
            anomalies.append(
                AnomalieIngestion(
                    type="doublon_reference",
                    reference=reference,
                    numero_ligne=occurences[0][0],
                    champ="Reference",
                    message=(
                        f"référence présente {len(occurences)} fois "
                        f"(lignes {numeros}) ; dossiers mis en quarantaine"
                    ),
                )
            )
            continue
        numero, contenu = occurences[0]
        enregistrement = EnregistrementBrut(
            source=source_commune.model_copy(
                update={"identifiant_enregistrement": reference}
            ),
            contenu=contenu,
        )
        dossier, anomalies_ligne = normaliser_enregistrement_merimee(
            enregistrement,
            numero_ligne=numero,
            colonne_code_insee=colonne_code_insee,
        )
        for anomalie in anomalies_ligne:
            anomalies.append(anomalie)
            if anomalie.type == "reference_format_inattendu":
                nombre_references_inattendues += 1
            if anomalie.type == "coordonnees_invalides":
                nombre_coordonnees_invalides += 1
        if dossier is None:
            continue
        if extraire_cellule(contenu, CHAMP_COORDONNEES) is None:
            nombre_coordonnees_absentes += 1
        if dossier.identite.code_commune is None:
            nombre_codes_commune_absents += 1
        dossiers.append(dossier)

    dossiers.sort(key=lambda dossier: dossier.identite.reference)
    references_dupliquees.sort()
    anomalies.sort(
        key=lambda anomalie: (
            anomalie.numero_ligne or 0,
            anomalie.type,
            anomalie.reference or "",
        )
    )

    lignes_dossiers = [
        dossier.model_dump_json(exclude_none=False) for dossier in dossiers
    ]
    lignes_anomalies = [anomalie.model_dump_json() for anomalie in anomalies]
    _ecrire_jsonl(repertoire_sortie / "monuments.jsonl", lignes_dossiers)
    _ecrire_jsonl(repertoire_sortie / "anomalies.jsonl", lignes_anomalies)

    rapport = RapportIngestionMerimee(
        departement=departement,
        nombre_lignes_total=nombre_total,
        nombre_lignes_departement=len(lignes_departement),
        nombre_dossiers_produits=len(dossiers),
        nombre_references_manquantes=len(sans_reference),
        nombre_references_format_inattendu=nombre_references_inattendues,
        nombre_coordonnees_absentes=nombre_coordonnees_absentes,
        nombre_coordonnees_invalides=nombre_coordonnees_invalides,
        nombre_codes_commune_absents=nombre_codes_commune_absents,
        nombre_doublons_reference=len(references_dupliquees),
        nombre_lignes_en_quarantaine=lignes_quarantaine,
        nombre_anomalies=len(anomalies),
        references_dupliquees=references_dupliquees,
        colonne_code_insee_absente=colonne_code_insee is None,
        empreinte_sha256=manifeste.empreinte_sha256,
    )
    (repertoire_sortie / "rapport.json").write_text(
        rapport.model_dump_json(indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return rapport
