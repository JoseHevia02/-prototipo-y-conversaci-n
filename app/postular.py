from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, field_validator

from app.auth import requiere_perfil
from app.clientes import buscar_animal, buscar_usuario
from app.db import get_postulaciones
from app.estados import APROBADA, CONCRETADA, EN_EVALUACION, RECIBIDA

router = APIRouter(prefix="/api/adopciones")
solo_vecino = requiere_perfil(["vecino"])


class NuevaPostulacion(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    animalId: str

    @field_validator("animalId")
    @classmethod
    def no_vacio(cls, v):
        if not v:
            raise ValueError("animalId obligatorio")
        return v


def ahora_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@router.post("/postulaciones", status_code=201)
async def postular(
    datos: NuevaPostulacion,
    usuario: dict = Depends(solo_vecino),
):
    auth_header = usuario.get("authorization")
    headers = {"Authorization": auth_header} if auth_header else None
    rut = usuario.get("rut")

    animal = await buscar_animal(datos.animalId, headers=headers)
    if animal.get("estado") == "fallecido" or animal.get("fallecido"):
        raise HTTPException(status_code=409, detail="Animal no disponible")

    if rut:
        info_usuario = await buscar_usuario(rut, headers=headers)
        if info_usuario.get("prohibicionTenencia") or info_usuario.get("prohibicion"):
            raise HTTPException(status_code=409, detail="Usuario con prohibicion")

    col = get_postulaciones()
    activa = col.find_one({
        "animalId": datos.animalId,
        "postulanteRut": rut,
        "estado": {"$in": [RECIBIDA, EN_EVALUACION, APROBADA, CONCRETADA]},
    })
    if activa:
        raise HTTPException(status_code=409, detail="Ya tienes una postulacion activa")

    postulacion = {
        "id": f"POST-{uuid4().hex[:6].upper()}",
        "animalId": datos.animalId,
        "postulanteRut": rut,
        "estado": RECIBIDA,
        "fechaPostulacion": ahora_iso(),
        "motivo": None,
    }
    col.insert_one(postulacion.copy())
    return postulacion