from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.agent.classification import Intent


DIRECTORY_CITATIONS = (
    {"source": "directorio_especialistas_y_servicios.pdf", "page": 1},
    {"source": "directorio_especialistas_y_servicios.pdf", "page": 2},
    {"source": "directorio_especialistas_y_servicios.pdf", "page": 3},
    {"source": "directorio_especialistas_y_servicios.pdf", "page": 4},
    {"source": "directorio_especialistas_y_servicios.pdf", "page": 5},
)

POLICY_CITATIONS = (
    {"source": "politica_cancelaciones_reagendamiento.pdf", "page": 1},
)

LOCATION_CITATIONS = (
    {"source": "directorio_especialistas_y_servicios.pdf", "page": 1},
    {"source": "directorio_especialistas_y_servicios.pdf", "page": 2},
    {"source": "directorio_especialistas_y_servicios.pdf", "page": 3},
    {"source": "directorio_especialistas_y_servicios.pdf", "page": 4},
    {"source": "directorio_especialistas_y_servicios.pdf", "page": 5},
)

SPECIALTIES = (
    "Cardiología",
    "Clínica médica",
    "Dermatología",
    "Endocrinología",
    "Gastroenterología",
    "Ginecología",
    "Pediatría",
    "Traumatología",
)

PROFESSIONALS_BY_SPECIALTY = (
    ("Cardiología", "Dr. Andrés Ferreyra, Dra. Emilia Ríos, Dr. Nicolás Vega"),
    ("Dermatología", "Dra. Paula Soria, Dr. Martín Ledesma"),
    ("Endocrinología", "Dra. Camila Ortega, Dr. Julián Prieto"),
    ("Gastroenterología", "Dra. Valeria Montes, Dr. Ramiro Salcedo"),
    ("Pediatría", "Dra. Lucía Benítez, Dr. Tomás Arias"),
    ("Traumatología", "Dr. Federico Alonso, Dra. Mariana Costa"),
    ("Clínica médica", "Dra. Sofía Molina, Dr. Esteban Rivas"),
    ("Ginecología", "Dra. Florencia Navarro, Dra. Pilar Acuña"),
)

SPECIALTY_PATTERNS = (
    ("Cardiología", r"cardiolog"),
    ("Gastroenterología", r"gastro|gastroenterolog"),
    ("Dermatología", r"dermatolog"),
    ("Endocrinología", r"endocrinolog"),
    ("Traumatología", r"traumatolog"),
    ("Pediatría", r"pediatr"),
    ("Clínica médica", r"clinica medica|medico clinico"),
    ("Ginecología", r"ginecolog"),
)

PROFESSIONAL_PATTERN = (
    r"\b(?:Dra?\.)\s+[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñ]+"
    r"(?:\s+[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñ]+){1,2}"
)


@dataclass(frozen=True)
class QuickResponse:
    intent: Intent
    answer: str
    citations: tuple[dict[str, Any], ...] = ()
    appointment_professional: str = ""
    appointment_specialty: str = ""

    def as_state(self) -> dict[str, Any]:
        return {
            "answer": self.answer,
            "citations": self.citations,
            "appointment_professional": self.appointment_professional,
            "appointment_specialty": self.appointment_specialty,
        }


def _conversation_text(conversation: tuple[dict[str, str], ...], *, limit: int = 8) -> str:
    return "\n".join(item.get("content", "") for item in conversation[-limit:])


def _detect_specialty(text: str) -> str:
    return next(
        (
            label
            for label, pattern in SPECIALTY_PATTERNS
            if re.search(pattern, text, re.IGNORECASE)
        ),
        "",
    )


def _detect_professional(text: str) -> str:
    professionals = re.findall(PROFESSIONAL_PATTERN, text)
    return professionals[-1] if professionals else ""


def _directory_response(question: str) -> QuickResponse:
    asks_professionals = re.search(
        r"medic|médic|profesional|doctor|doctora|cartilla", question, re.IGNORECASE
    )
    if asks_professionals:
        formatted_professionals = "\n".join(
            f"- {specialty}: {names}" for specialty, names in PROFESSIONALS_BY_SPECIALTY
        )
        return QuickResponse(
            intent="directory",
            answer=(
                "El directorio de Medinova registra estos profesionales por especialidad:\n\n"
                f"{formatted_professionals}\n\n"
                "Esto no confirma disponibilidad de turnos; para eso puedo derivarte "
                "a la sección Solicitudes y registrar una solicitud pendiente."
            ),
            citations=DIRECTORY_CITATIONS,
        )
    formatted = "\n".join(f"- {specialty}" for specialty in SPECIALTIES)
    return QuickResponse(
        intent="directory",
        answer=(
            "Las especialidades disponibles en el directorio de Medinova son:\n\n"
            f"{formatted}\n\n"
            "Si querés, puedo ayudarte a ver profesionales por especialidad o derivarte "
            "a Solicitudes para registrar una solicitud pendiente."
        ),
        citations=DIRECTORY_CITATIONS,
    )


def quick_response_for_intent(
    intent: Intent,
    *,
    question: str,
    conversation: tuple[dict[str, str], ...] = (),
) -> QuickResponse | None:
    if intent == "documental":
        return None
    if intent == "greeting":
        return QuickResponse(
            intent=intent,
            answer=(
                "¡Hola! Soy Medinova AI Agent. Puedo ayudarte con información institucional, "
                "especialistas, sedes, horarios, coberturas y solicitudes de turno disponibles "
                "en los documentos de la clínica. ¿Qué necesitás consultar?"
            ),
        )
    if intent == "clinical":
        return QuickResponse(
            intent=intent,
            answer=(
                "No puedo brindar diagnósticos, interpretar síntomas o resultados, ni indicar "
                "medicación o tratamientos. Consultá con un profesional de salud o con el canal "
                "correspondiente de la clínica."
            ),
        )
    if intent == "invalid":
        return QuickResponse(
            intent=intent,
            answer=(
                "Puedo ayudarte con información administrativa de Medinova: especialidades, "
                "profesionales, sedes, coberturas, políticas y solicitudes de turno."
            ),
        )
    if intent == "directory":
        return _directory_response(question)
    if intent == "admin_policy":
        return QuickResponse(
            intent=intent,
            answer=(
                "Para cancelar o reagendar un turno, la política institucional indica avisar "
                "con 24 horas de anticipación. La solicitud queda sujeta a revisión del equipo "
                "de admisión; una solicitud pendiente no equivale a un turno confirmado."
            ),
            citations=POLICY_CITATIONS,
        )
    if intent == "location":
        return QuickResponse(
            intent=intent,
            answer=(
                "La documentación del directorio menciona atención en sedes de Medinova "
                "como Sede Centro y Sede Norte. No tengo una dirección postal exacta en "
                "los fragmentos disponibles; si querés, puedo ayudarte a consultar "
                "profesionales por sede o registrar una solicitud pendiente."
            ),
            citations=LOCATION_CITATIONS,
        )
    if intent == "appointment":
        context = _conversation_text(conversation)
        full_context = f"{context}\n{question}"
        professional = _detect_professional(context)
        specialty = _detect_specialty(full_context)
        detail = ""
        if professional:
            detail = f" para {professional}"
        elif specialty:
            detail = f" para {specialty}"
        return QuickResponse(
            intent=intent,
            answer=(
                f"Sí. Puedo derivarte al formulario de la sección Solicitudes{detail}. "
                "Completá los datos de contacto y preferencia horaria. La solicitud quedará "
                "registrada como pendiente; no confirma una reserva ni asigna automáticamente un turno."
            ),
            appointment_professional=professional,
            appointment_specialty=specialty,
        )
    return None
