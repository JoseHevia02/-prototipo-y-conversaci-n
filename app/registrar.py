from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, field_validator

from app.auth import requiere_perfil
from app.db import get_postulaciones
from app.estados import CONCRETADA, DEVUELTO

router = APIRouter(prefix="/api/adopciones")
solo_funcionario = requiere_perfil(["funcionario"])


class DevolucionAdopcion(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    motivo: str

    @field_validator("motivo")
    @classmethod
    def motivo_obligatorio(cls, v):
        if not v:
            raise ValueError("motivo obligatorio")
        return v


def ahora_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@router.post("/postulaciones/{postulacion_id}/devolucion")
async def registrar_devolucion(
    postulacion_id: str,
    datos: DevolucionAdopcion,
    usuario: dict = Depends(solo_funcionario),
):
    col = get_postulaciones()
    postulacion = col.find_one({"id": postulacion_id})
    if not postulacion:
        raise HTTPException(status_code=404, detail="Postulacion no encontrada")
    if postulacion.get("estado") != CONCRETADA:
        raise HTTPException(status_code=409, detail="Solo se puede devolver una adopcion concretada")

    actualizada = {
        **{k: v for k, v in postulacion.items() if k != "_id"},
        "estado": DEVUELTO,
        "motivo": datos.motivo,
        "fechaDevolucion": ahora_iso(),
    }
    col.update_one({"id": postulacion_id}, {"$set": actualizada})
    return actualizada