from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True)
class AppointmentRequest:
    request_id: str
    created_at: str
    patient_name: str
    contact: str
    specialty: str
    preferred_time: str
    notes: str
    status: str = "pendiente"


FIELDS = tuple(AppointmentRequest.__dataclass_fields__)


def create_request(
    *,
    patient_name: str,
    contact: str,
    specialty: str,
    preferred_time: str,
    notes: str = "",
) -> AppointmentRequest:
    if not patient_name.strip() or not contact.strip() or not specialty.strip():
        raise ValueError("Nombre, contacto y especialidad son obligatorios.")
    return AppointmentRequest(
        request_id=uuid4().hex[:10],
        created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        patient_name=patient_name.strip(),
        contact=contact.strip(),
        specialty=specialty.strip(),
        preferred_time=preferred_time.strip(),
        notes=notes.strip(),
    )


def append_request(path: Path, request: AppointmentRequest) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow(asdict(request))


def load_requests(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))
