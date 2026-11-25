# Reenvia el inicio de sesion al nucleo, para que la pagina no dependa de CORS.
import os

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

load_dotenv()
NUCLEO_URL = os.getenv("NUCLEO_URL")

router = APIRouter(prefix="/api/adopciones")


class Credenciales(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rut: str = Field(min_length=3, max_length=12)
    clave: str = Field(min_length=1, max_length=100)


@router.post("/sesiones")
async def iniciar_sesion(credenciales: Credenciales):
    try:
        async with httpx.AsyncClient(timeout=5) as cliente:
            respuesta = await cliente.post(
                NUCLEO_URL + "/api/nucleo/sesiones",
                json={"rut": credenciales.rut, "clave": credenciales.clave},
            )
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail="El nucleo no responde")

    if respuesta.status_code != 201:
        raise HTTPException(status_code=401, detail="RUT o clave incorrectos")

    return JSONResponse(status_code=201, content=respuesta.json())
