# Datos de partida con ID fijo, para que la verificacion siempre parta igual.
from app.db import get_postulaciones

SEMILLA = [
    {
        "id": "POST-SEED-001",
        "animalId": "SIM-000001",
        "postulanteRut": "11111111-1",
        "estado": "recibida",
        "fechaPostulacion": "2026-11-20T15:00:00Z",
        "motivo": None,
    },
    {
        "id": "POST-SEED-002",
        "animalId": "SIM-000002",
        "postulanteRut": "12222222-5",
        "estado": "en evaluación",
        "fechaPostulacion": "2026-11-21T15:00:00Z",
        "motivo": None,
    },
]


def restablecer_semilla():
    postulaciones = get_postulaciones()
    for postulacion in SEMILLA:
        # upsert: si no existe la crea, y si existe la deja como al inicio.
        postulaciones.replace_one({"id": postulacion["id"]}, dict(postulacion), upsert=True)
