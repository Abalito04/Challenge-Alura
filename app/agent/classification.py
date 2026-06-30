from __future__ import annotations

import re
import unicodedata
from typing import Literal

Intent = Literal["documental", "clinical", "appointment", "greeting", "invalid"]

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
    r"\bquiero (?:pedir|solicitar|sacar|reservar).{0,20}turno",
    r"\bsolicitar (?:un )?turno",
    r"\bagendar (?:un )?turno",
    r"\bnecesito (?:un )?turno",
    r"\b(?:gestionar|gestiono|gestionamos|pedir|sacar|reservar) (?:un )?turno",
    r"\b(?:podemos|puedo|como puedo) (?:gestionar|pedir|sacar|reservar|agendar) (?:un )?turno",
)
GREETING_PATTERN = (
    r"^(?:hola|buen dia|buenas tardes|buenas noches|buenas|gracias|muchas gracias|"
    r"chau|adios|hasta luego)[!., ]*$"
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
    if any(re.search(pattern, normalized) for pattern in CLINICAL_PATTERNS):
        return "clinical"
    if any(re.search(pattern, normalized) for pattern in APPOINTMENT_PATTERNS):
        return "appointment"
    if re.search(r"\bturno\b", normalized) and re.search(
        r"\b(?:quiero|quisiera|gustaria|gestion|pedir|sacar|reservar|agendar|con)\b",
        normalized,
    ):
        return "appointment"
    if re.fullmatch(r"(?:si|dale|bueno|perfecto|hagamoslo|quiero)[!., ]*", normalized):
        if "turno" in normalized_history or "solicitud" in normalized_history:
            return "appointment"
    return "documental"
