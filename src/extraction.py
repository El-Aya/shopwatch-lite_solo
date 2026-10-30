import re

from src.contrat import Signal

_SECRETS = re.compile(
    r"(password|pwd|token|secret|card|iban)(\s*[=:]\s*)[^\s&,;]+",
    re.IGNORECASE,
)

_BEARER = re.compile(r"(Bearer\s+)[^\s]+", re.IGNORECASE)

def masquer_donnees(texte: str) -> str:
    texte = _SECRETS.sub(r"\1\2[MASQUE]", texte)
    return _BEARER.sub(r"\1[MASQUE]", texte)


def lire_journal(ligne: str, numero: int, origine: str = "PAIEMENT",
                 env: str = "production") -> Signal:
    champs = ligne.split()
    if len(champs) < 5:
        raise ValueError("ligne de journal invalide")
    niveau = champs[3].upper()
    if niveau in ("FATAL", "CRITICAL"):
        gravite = "BLOQUANT"
    elif niveau == "ERROR":
        gravite = "MAJEUR"
    elif niveau in ("WARN", "WARNING"):
        gravite = "MODERE"
    else:
        gravite = "MINEUR"
    return Signal(
        ref=f"SH-{numero:04d}",
        date=f"{champs[0]}T{champs[1]}Z",
        origine=origine,
        service=champs[2],
        env=env,
        categorie="JOURNAL",
        gravite=gravite,
        texte=masquer_donnees(" ".join(champs[4:])),
    )


def lire_scan(rapport: dict, numero: int, env: str = "production") -> Signal:
    for cle in ("id_faille", "paquet", "risque", "date"):
        if cle not in rapport:
            raise ValueError(f"cle manquante : {cle}")
    gravites = {"critique": "BLOQUANT", "haut": "MAJEUR", "moyen": "MODERE"}
    return Signal(
        ref=f"SH-{numero:04d}",
        date=rapport["date"],
        origine="SCANNER",
        service=rapport["paquet"],
        env=env,
        categorie="FAILLE",
        gravite=gravites.get(rapport["risque"].lower(), "MINEUR"),
        texte=f"Faille {rapport['id_faille']} dans {rapport['paquet']}",
    )


def lire_build(rapport: dict, numero: int, env: str = "production") -> Signal:
    for cle in ("etape", "resultat", "date"):
        if cle not in rapport:
            raise ValueError(f"cle manquante : {cle}")
    echec = rapport["resultat"].lower() == "echec"
    return Signal(
        ref=f"SH-{numero:04d}",
        date=rapport["date"],
        origine="BUILD",
        service=rapport["etape"],
        env=env,
        categorie="BUILD_ECHEC" if echec else "BUILD_OK",
        gravite="MAJEUR" if echec else "MINEUR",
        texte=f"Build {rapport['etape']} : {rapport['resultat']}",
    )