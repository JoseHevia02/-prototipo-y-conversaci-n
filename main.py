from fastapi import Depends, FastAPI
from app.auth import requiere_perfil

app = FastAPI()


@app.get("/api/adopciones/salud")
async def salud_adopciones():
    return {"status": "ok", "service": "adopciones"}


@app.get("/api/adopciones/prueba-funcionario")
async def prueba_funcionario(usuario=Depends(requiere_perfil(["funcionario"]))):
    return {"usuario": usuario}