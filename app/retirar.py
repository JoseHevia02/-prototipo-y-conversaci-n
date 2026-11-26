from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException

from app.auth import requiere_perfil
from app.db import get_postulaciones
from app.estados import EN_EVALUACION, RECIBIDA

router = APIRouter(prefix="/api/adopciones")
solo_vecino = requiere_perfil(["vecino"])


def ahora_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@router.post("/postulaciones/{postulacion_id}/retirar")
async def retirar_postulacion(
    postulacion_id: str,
    usuario: dict = Depends(solo_vecino),
):
    col = get_postulaciones()
    postulacion = col.find_one({"id": postulacion_id})
    if not postulacion:
        raise HTTPException(status_code=404, detail="Postulacion no encontrada")
    if postulacion.get("postulanteRut") != usuario.get("rut"):
        raise HTTPException(status_code=403, detail="Sin permiso sobre esta postulacion")
    if postulacion.get("estado") not in {RECIBIDA, EN_EVALUACION}:
        raise HTTPException(status_code=409, detail="Estado no permite retirar la postulacion")

    actualizada = {
        **{k: v for k, v in postulacion.items() if k != "_id"},
        "estado": "retirada",
        "fechaRetiro": ahora_iso(),
    }
    col.update_one({"id": postulacion_id}, {"$set": actualizada})
    return actualizada