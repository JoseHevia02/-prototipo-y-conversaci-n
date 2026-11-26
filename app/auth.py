import os
import httpx
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

load_dotenv()
NUCLEO_URL = os.getenv("NUCLEO_URL", "").rstrip("/")
security = HTTPBearer(auto_error=False)


def requiere_perfil(perfiles_permitidos):
    async def verificar(credenciales: HTTPAuthorizationCredentials | None = Depends(security)):
        if not credenciales or credenciales.scheme.lower() != "bearer" or not credenciales.credentials.strip():
            raise HTTPException(status_code=401, detail="Token no valido")

        header_limpio = f"Bearer {credenciales.credentials.strip()}"

        if not NUCLEO_URL:
            raise HTTPException(status_code=503, detail="Servicio no configurado")

        try:
            async with httpx.AsyncClient(timeout=5) as cliente:
                respuesta = await cliente.get(
                    f"{NUCLEO_URL}/api/nucleo/sesiones/actual",
                    headers={"Authorization": header_limpio},
                )
        except httpx.HTTPError:
            raise HTTPException(status_code=503, detail="El nucleo no responde")

        if respuesta.status_code != 200:
            raise HTTPException(status_code=401, detail="Sesion no valida")

        usuario = respuesta.json()
        if usuario.get("perfil") not in perfiles_permitidos:
            raise HTTPException(status_code=403, detail="Sin permiso")

        usuario["authorization"] = header_limpio
        return usuario

    return verificar