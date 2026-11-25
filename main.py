from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import evaluar, login, postular
from app.auth import requiere_perfil
from app.errores import manejar_http, manejar_validacion
from app.semilla import restablecer_semilla


@asynccontextmanager
async def al_iniciar(app):
    restablecer_semilla()
    yield


app = FastAPI(lifespan=al_iniciar)

app.add_exception_handler(StarletteHTTPException, manejar_http)
app.add_exception_handler(RequestValidationError, manejar_validacion)

app.include_router(login.router)
app.include_router(evaluar.router)
app.include_router(postular.router)


@app.get("/api/adopciones/salud")
async def salud_adopciones():
    return {"status": "ok", "service": "adopciones"}


@app.get("/api/adopciones/prueba-funcionario")
async def prueba_funcionario(usuario=Depends(requiere_perfil(["funcionario"]))):
    return {"usuario": usuario}


@app.get("/evaluar")
async def pagina_evaluar():
    return FileResponse("static/evaluar.html")