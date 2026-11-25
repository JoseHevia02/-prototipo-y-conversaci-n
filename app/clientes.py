import os
import time
from dotenv import load_dotenv
from fastapi import HTTPException
import httpx

load_dotenv()

NUCLEO_URL = os.getenv("NUCLEO_URL", "").rstrip("/")
M1_URL = os.getenv("M1_URL", "").rstrip("/")
NUCLEO_SERVICE_TOKEN = os.getenv("NUCLEO_SERVICE_TOKEN", "").strip()
NUCLEO_SERVICE_RUT = os.getenv("NUCLEO_SERVICE_RUT", "").strip()
NUCLEO_SERVICE_CLAVE = os.getenv("NUCLEO_SERVICE_CLAVE", "").strip()

_cache_token = {"token": "", "exp": 0.0}


async def obtener_token_servicio():
    if NUCLEO_SERVICE_TOKEN:
        return NUCLEO_SERVICE_TOKEN

    ahora = time.time()
    if _cache_token["token"] and ahora < _cache_token["exp"]:
        return _cache_token["token"]

    if not (NUCLEO_URL and NUCLEO_SERVICE_RUT and NUCLEO_SERVICE_CLAVE):
        return ""

    try:
        async with httpx.AsyncClient(timeout=5) as cliente:
            resp = await cliente.post(
                f"{NUCLEO_URL}/api/nucleo/sesiones",
                json={"rut": NUCLEO_SERVICE_RUT, "clave": NUCLEO_SERVICE_CLAVE},
            )
    except httpx.HTTPError:
        return ""

    if resp.status_code not in (200, 201):
        return ""

    token = (resp.json().get("token") or "").strip()
    if token:
        _cache_token["token"] = token
        _cache_token["exp"] = ahora + 300
    return token


async def consultar_get(url, headers=None):
    if not url:
        raise HTTPException(status_code=503, detail="Servicio no configurado")
    try:
        async with httpx.AsyncClient(timeout=5) as cliente:
            resp = await cliente.get(url, headers=headers)
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail="Servicio no disponible")

    if resp.status_code >= 500:
        raise HTTPException(status_code=503, detail="Servicio no disponible")
    return resp


async def buscar_animal(animal_id, headers=None):
    url = f"{M1_URL}/animales/{animal_id}"
    resp = await consultar_get(url, headers=headers)

    if resp.status_code == 403:
        svc_token = await obtener_token_servicio()
        if not svc_token:
            raise HTTPException(status_code=503, detail="Servicio no disponible")
        resp = await consultar_get(url, headers={"Authorization": f"Bearer {svc_token}"})

    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    if resp.status_code == 403:
        raise HTTPException(status_code=409, detail="Animal no disponible")
    if resp.status_code != 200:
        raise HTTPException(status_code=503, detail=f"Error al consultar animal ({resp.status_code})")
    return resp.json()


async def buscar_usuario(rut, headers=None):
    url = f"{NUCLEO_URL}/api/nucleo/usuarios/{rut}"
    resp = await consultar_get(url, headers=headers)

    if resp.status_code == 403:
        svc_token = await obtener_token_servicio()
        if svc_token:
            resp = await consultar_get(url, headers={"Authorization": f"Bearer {svc_token}"})

    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if resp.status_code != 200:
        raise HTTPException(status_code=503, detail=f"Error al consultar usuario ({resp.status_code})")
    return resp.json()