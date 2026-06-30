from __future__ import annotations

import re
import unicodedata
from typing import Literal

Intent = Literal["documental", "clinical", "appointment", "invalid"]

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
)


def normalize_for_classification(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def classify_intent(text: str) -> Intent:
    normalized = normalize_for_classification(text).strip()
    if not normalized:
        return "invalid"
    if any(re.search(pattern, normalized) for pattern in CLINICAL_PATTERNS):
        return "clinical"
    if any(re.search(pattern, normalized) for pattern in APPOINTMENT_PATTERNS):
        return "appointment"
    return "documental"

