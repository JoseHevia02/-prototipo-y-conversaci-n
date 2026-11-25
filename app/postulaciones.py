import math

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth import requiere_perfil
from app.db import get_postulaciones

router = APIRouter(prefix="/api/adopciones")

puede_consultar = requiere_perfil(["vecino", "funcionario", "admin"])


@router.get("/postulaciones")
def listar_postulaciones(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    usuario=Depends(puede_consultar),
):
    postulaciones = get_postulaciones()

    filtro = {}
    if usuario["perfil"] == "vecino":
        filtro["postulanteRut"] = usuario["rut"]

    total = postulaciones.count_documents(filtro)
    if total > 0:
        total_paginas = math.ceil(total / limit)
    else:
        total_paginas = 0

    saltar = (page - 1) * limit
    datos = []
    for postulacion in postulaciones.find(filtro, {"_id": 0}).skip(saltar).limit(limit):
        datos.append(postulacion)

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "totalPaginas": total_paginas,
        "datos": datos,
    }


@router.get("/postulaciones/{id}")
def obtener_postulacion(id: str, usuario=Depends(puede_consultar)):
    postulaciones = get_postulaciones()

    filtro = {"id": id}
    
    if usuario["perfil"] == "vecino":
        filtro["postulanteRut"] = usuario["rut"]

    postulacion = postulaciones.find_one(filtro, {"_id": 0})
    if not postulacion:
        raise HTTPException(status_code=404, detail="La postulacion no existe")

    return postulacion
