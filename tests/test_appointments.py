from pathlib import Path

import pytest

from app.appointments import append_request, create_request, load_requests


def test_request_round_trip_to_csv(tmp_path: Path) -> None:
    path = tmp_path / "requests.csv"
    request = create_request(
        patient_name="Paciente Demo",
        contact="demo@example.test",
        specialty="Cardiología",
        preferred_time="Por la mañana",
    )
    append_request(path, request)
    rows = load_requests(path)
    assert len(rows) == 1
    assert rows[0]["status"] == "pendiente"
    assert rows[0]["specialty"] == "Cardiología"


def test_request_requires_minimum_fields() -> None:
    with pytest.raises(ValueError, match="obligatorios"):
        create_request(
            patient_name="",
            contact="demo@example.test",
            specialty="Cardiología",
            preferred_time="",
        )
