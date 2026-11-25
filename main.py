from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.auth import requiere_perfil
from app.errores import manejar_http, manejar_validacion

app = FastAPI()

app.add_exception_handler(StarletteHTTPException, manejar_http)
app.add_exception_handler(RequestValidationError, manejar_validacion)


@app.get("/api/adopciones/salud")
async def salud_adopciones():
    return {"status": "ok", "service": "adopciones"}


@app.get("/api/adopciones/prueba-funcionario")
async def prueba_funcionario(usuario=Depends(requiere_perfil(["funcionario"]))):
    return {"usuario": usuario}