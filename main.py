from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import evaluar, login, postular, animales, postulaciones
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
app.include_router(animales.router)
app.include_router(postulaciones.router)


@app.get("/", response_class=HTMLResponse)
async def inicio():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Módulo 3: Adopciones</title>
        <style>
            body { font-family: sans-serif; max-width: 520px; margin: 40px auto; padding: 0 16px; line-height: 1.6; }
            a { display: block; padding: 12px 16px; margin: 10px 0; border: 1px solid #ccc; border-radius: 6px; text-decoration: none; color: #111; font-weight: bold; }
            a:hover { background: #f3f3f3; }
            span { display: block; font-weight: normal; font-size: 0.9em; color: #555; }
        </style>
    </head>
    <body>
        <h1>Módulo 3: Adopciones</h1>
        <p>Selecciona una opción:</p>
        <a href="/postular">Postular a adopción<span>Crear postulación (HU-02)</span></a>
        <a href="/evaluar">Evaluar postulación<span>Cambiar estado de postulación (HU-05)</span></a>
        <a href="/consultas">Consultar<span>Ver animales disponibles y mis postulaciones (HU-01 / HU-03)</span></a>
        <a href="/docs">Documentación API<span>Swagger UI (/docs)</span></a>
    </body>
    </html>
    """


@app.get("/api/adopciones/salud")
async def salud_adopciones():
    return {"status": "ok", "service": "adopciones"}


@app.get("/evaluar")
async def pagina_evaluar():
    return FileResponse("static/evaluar.html")


@app.get("/postular")
async def pagina_postular():
    return FileResponse("static/postular.html")


@app.get("/consultas")
async def pagina_consultas():
    return FileResponse("static/consultas.html")