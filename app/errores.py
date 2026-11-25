from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

codigos = {
    401: "NO_AUTENTICADO",
    403: "PERFIL_SIN_PERMISO",
    404: "NO_ENCONTRADO",
    409: "REGLA_NEGOCIO",
    503: "SERVICIO_NO_DISPONIBLE",
}

async def manejar_http(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"codigo": codigos.get(exc.status_code, "ERROR"), "mensaje": exc.detail}}
    )

async def manejar_validacion(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": {"codigo": "DATOS_INVALIDOS", "mensaje": "Datos invalidos"}}
    )