from __future__ import annotations

import re
import unicodedata
from typing import Literal

Intent = Literal[
    "documental",
    "clinical",
    "appointment",
    "directory",
    "admin_policy",
    "location",
    "greeting",
    "invalid",
]

INVALID_PATTERNS = (
    r"\bboca\b",
    r"\briver\b",
    r"\bfutbol\b",
    r"\bpartido\b",
)
CLINICAL_PATTERNS = (
    r"\bdiagnostic",
    r"\bmedic(?:amento|acion|ina)",
    r"\btratamiento",
    r"\bdosis\b",
    r"\bsintoma",
    r"\bantibiotico",
    r"\bque tengo\b",
    r"\bresultado.*significa",
)
APPOINTMENT_PATTERNS = (
    r"\bver turnos?\b",
    r"\bturnos? con\b",
    r"\bquiero (?:pedir|solicitar|sacar|reservar).{0,20}turnos?",
    r"\bsolicitar (?:un )?turnos?",
    r"\bagendar (?:un )?turnos?",
    r"\bnecesito (?:un )?turnos?",
    r"\b(?:gestionar|gestiono|gestionamos|pedir|sacar|reservar) (?:un )?turnos?",
    r"\b(?:podemos|puedo|como puedo) (?:gestionar|pedir|sacar|reservar|agendar) (?:un )?turnos?",
)
DIRECTORY_PATTERNS = (
    r"\bque especialidades hay\b",
    r"\bespecialidades\b",
    r"\b(?:que|cuales?|ver|mostrar|list(?:a|ado)) (?:medicos|doctores|profesionales)(?: hay| disponibles)?\b",
    r"\b(?:medicos|doctores|profesionales) (?:hay|disponibles|atienden)\b",
    r"\bmedicos disponibles\b",
    r"\bprofesionales disponibles\b",
    r"\bprofesionales hay\b",
    r"\bcartilla\b",
    r"\bservicios disponibles\b",
    r"\bdirectorio\b",
)
ADMIN_POLICY_PATTERNS = (
    r"\bcomo cancelo (?:un )?turnos?\b",
    r"\bcancel(?:ar|o|acion|aciones).{0,25}turnos?\b",
    r"\banul(?:ar|o).{0,25}turnos?\b",
    r"\breagend(?:ar|o|amiento).{0,25}turnos?\b",
    r"\bcambiar.{0,25}turnos?\b",
)
LOCATION_PATTERNS = (
    r"\bdonde queda\b",
    r"\bdonde estan\b",
    r"\bubicaci(?:on|ones)\b",
    r"\bdireccion(?:es)?\b",
    r"\bsedes?\b",
)
GREETING_PATTERN = (
    r"^(?:(?:hola|buen dia|buenos dias|buenas tardes|buenas noches|buenas)"
    r"(?:[!., ]+(?:buen dia|buenos dias|buenas tardes|buenas noches|buenas))?|"
    r"gracias|muchas gracias|chau|adios|hasta luego)[!., ]*$"
)


def normalize_for_classification(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def classify_intent(text: str, *, history_text: str = "") -> Intent:
    normalized = normalize_for_classification(text).strip()
    normalized_history = normalize_for_classification(history_text)
    if not normalized:
        return "invalid"
    if re.fullmatch(GREETING_PATTERN, normalized):
        return "greeting"
    if any(re.search(pattern, normalized) for pattern in INVALID_PATTERNS):
        return "invalid"
    if any(re.search(pattern, normalized) for pattern in CLINICAL_PATTERNS):
        return "clinical"
    if any(re.search(pattern, normalized) for pattern in APPOINTMENT_PATTERNS):
        return "appointment"
    if any(re.search(pattern, normalized) for pattern in DIRECTORY_PATTERNS):
        return "directory"
    if any(re.search(pattern, normalized) for pattern in ADMIN_POLICY_PATTERNS):
        return "admin_policy"
    if any(re.search(pattern, normalized) for pattern in LOCATION_PATTERNS):
        return "location"
    if re.search(r"\bturnos?\b", normalized) and re.search(
        r"\b(?:quiero|quisiera|gustaria|gestion|pedir|sacar|reservar|agendar|con)\b",
        normalized,
    ):
        return "appointment"
    if re.fullmatch(r"(?:si|dale|bueno|perfecto|hagamoslo|quiero)[!., ]*", normalized):
        if "turno" in normalized_history or "solicitud" in normalized_history:
            return "appointment"
    return "documental"
