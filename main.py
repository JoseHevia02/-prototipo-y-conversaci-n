from fastapi import FastAPI

app = FastAPI()


@app.get("/api/adopciones/salud")
async def salud_adopciones():
    return {"status": "ok", "service": "adopciones"}