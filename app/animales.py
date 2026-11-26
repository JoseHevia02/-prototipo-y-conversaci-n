import math
import os

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, Header, HTTPException, Query

load_dotenv()
M1_URL = os.getenv("M1_URL")

router = APIRouter(prefix="/api/adopciones")


@router.get("/animales")
async def listar_animales(
    especie: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    authorization: str | None = Header(None),
):
    cabeceras = {}
    if authorization:
        cabeceras["Authorization"] = authorization

    
    todos_los_animales = []
    pagina_m1 = 1

    while pagina_m1 <= 50:
        try:
            async with httpx.AsyncClient(timeout=5) as cliente:
                respuesta = await cliente.get(
                    M1_URL + "/animales",
                    headers=cabeceras,
                    params={"page": pagina_m1, "limit": 100},
                )
        except httpx.HTTPError:
            raise HTTPException(status_code=503, detail="SERVICIO_NO_DISPONIBLE")

        if respuesta.status_code == 401:
            raise HTTPException(status_code=401, detail="TOKEN_INVALIDO")
        if respuesta.status_code != 200:
            raise HTTPException(status_code=503, detail="SERVICIO_NO_DISPONIBLE")

        cuerpo = respuesta.json()
        if isinstance(cuerpo, list):
            lote = cuerpo
        else:
            lote = cuerpo.get("datos", [])

        for animal in lote:
            todos_los_animales.append(animal)

        if len(lote) < 100:
            break
        pagina_m1 = pagina_m1 + 1

    disponibles = []
    for animal in todos_los_animales:
        if animal.get("estado") == "fallecido":
            continue
        if animal.get("tutorRut"):
            continue
        if especie:
            if str(animal.get("especie", "")).lower() != especie.lower():
                continue
        disponibles.append(animal)

    total = len(disponibles)
    if total > 0:
        total_paginas = math.ceil(total / limit)
    else:
        total_paginas = 0

    inicio = (page - 1) * limit
    fin = inicio + limit
    datos_pagina = disponibles[inicio:fin]

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "totalPaginas": total_paginas,
        "datos": datos_pagina,
    }
