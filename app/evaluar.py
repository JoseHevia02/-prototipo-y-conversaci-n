# HU-05: el funcionario evalua una postulacion (cambia su estado).
from datetime import datetime, timezone
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.auth import requiere_perfil
from app.db import get_postulaciones
from app.estados import ESTADOS_CON_MOTIVO, puede_cambiar

router = APIRouter(prefix="/api/adopciones")

# Solo el perfil funcionario puede evaluar. Sin token da 401 y otro perfil da 403.
solo_funcionario = requiere_perfil(["funcionario"])


class CambioEstado(BaseModel):
    # extra="forbid": si mandan un campo que no esperamos, se rechaza con 400.
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    estado: Literal[
        "recibida",
        "en evaluación",
        "aprobada",
        "rechazada",
        "adopción concretada",
        "devuelto",
    ]
    motivo: Optional[str] = Field(default=None, max_length=300)

    @model_validator(mode="after")
    def exigir_motivo(self):
        if self.estado in ESTADOS_CON_MOTIVO and not self.motivo:
            raise ValueError("Este estado exige un motivo")
        return self


def ahora_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@router.put("/postulaciones/{id}/estado")
def cambiar_estado(id: str, cambio: CambioEstado, usuario=Depends(solo_funcionario)):
    postulaciones = get_postulaciones()

    postulacion = postulaciones.find_one({"id": id})
    if not postulacion:
        raise HTTPException(status_code=404, detail="La postulacion no existe")

    actual = postulacion["estado"]
    if not puede_cambiar(actual, cambio.estado):
        raise HTTPException(
            status_code=409,
            detail="No se puede pasar de '" + actual + "' a '" + cambio.estado + "'",
        )

    # HU-06: al pasar a "adopción concretada" aqui se informa al M1 antes de guardar.

    # El filtro incluye el estado actual: si otro funcionario la cambio
    # justo antes, no se encuentra y no se pisa su decision.
    resultado = postulaciones.update_one(
        {"id": id, "estado": actual},
        {
            "$set": {
                "estado": cambio.estado,
                "motivo": cambio.motivo,
                "evaluadoPor": usuario["rut"],
                "fechaActualizacion": ahora_utc(),
            }
        },
    )
    if resultado.modified_count == 0:
        raise HTTPException(status_code=409, detail="La postulacion cambio de estado, vuelve a intentarlo")

    # {"_id": 0} quita el identificador interno de MongoDB de la respuesta.
    return postulaciones.find_one({"id": id}, {"_id": 0})
