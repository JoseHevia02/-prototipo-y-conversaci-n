from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest

import app.postular as postular
from main import app

RUTA = "/api/adopciones/postulaciones"


class ListaFake:
    def __init__(self):
        self.items = []

    def find_one(self, filtro):
        for item in self.items:
            if item.get("animalId") == filtro.get("animalId") and item.get("postulanteRut") == filtro.get("postulanteRut"):
                return item
        return None

    def insert_one(self, doc):
        self.items.append(doc)


@pytest.fixture
def cliente(monkeypatch):
    col = ListaFake()
    monkeypatch.setattr(postular, "get_postulaciones", lambda: col)

    async def animal_ok(animal_id, headers=None):
        return {"id": animal_id, "fallecido": False, "tutorRut": None}

    async def usuario_ok(rut, headers=None):
        return {"rut": rut, "prohibicionTenencia": False}

    monkeypatch.setattr(postular, "buscar_animal", animal_ok)
    monkeypatch.setattr(postular, "buscar_usuario", usuario_ok)
    app.dependency_overrides[postular.solo_vecino] = lambda: {"rut": "11111111-1", "perfil": "vecino"}

    yield TestClient(app), col
    app.dependency_overrides.clear()


def test_201(cliente):
    client, col = cliente
    r = client.post(RUTA, json={"animalId": "SIM-000001"})
    assert r.status_code == 201
    assert r.json()["estado"] == "recibida"
    assert len(col.items) == 1


def test_400(cliente):
    client, _ = cliente
    r = client.post(RUTA, json={"animalId": ""})
    assert r.status_code == 400


def test_409_duplicada(cliente):
    client, _ = cliente
    assert client.post(RUTA, json={"animalId": "SIM-000001"}).status_code == 201
    r = client.post(RUTA, json={"animalId": "SIM-000001"})
    assert r.status_code == 409


def test_503(cliente, monkeypatch):
    client, col = cliente

    async def cae(animal_id, headers=None):
        raise HTTPException(status_code=503, detail="Servicio no disponible")

    monkeypatch.setattr(postular, "buscar_animal", cae)
    r = client.post(RUTA, json={"animalId": "SIM-000001"})
    assert r.status_code == 503
    assert len(col.items) == 0