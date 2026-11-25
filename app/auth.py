import os  
import httpx  
from dotenv import load_dotenv  
from fastapi import Depends, Header, HTTPException  

load_dotenv()  
NUCLEO_URL = os.getenv("NUCLEO_URL")  

def requiere_perfil(perfiles_permitidos):
    async def verificar(authorization: str = Header(None)):
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token no valido")

        async with httpx.AsyncClient(timeout=5) as cliente:
            respuesta = await cliente.get(
                NUCLEO_URL + "/api/nucleo/sesiones/actual",
                headers={"Authorization": authorization},
            )

        if respuesta.status_code != 200:
            raise HTTPException(status_code=401, detail="Sesion no valida")

        usuario = respuesta.json()

        if usuario.get("perfil") not in perfiles_permitidos:
            raise HTTPException(status_code=403, detail="Sin permiso")

        return usuario

    return verificar