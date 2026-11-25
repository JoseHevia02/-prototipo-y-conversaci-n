# Pruebas de HU-05. Se ejecutan con: python -m pytest
# No tocan Atlas ni el nucleo: usan una coleccion falsa en memoria.
import os

os.environ.setdefault("conexionmongodc", "mongodb://localhost:27017")
os.environ.setdefault("NUCLEO_URL", "http://nucleo.invalid")

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import app.evaluar as evaluar
from main import app

RUTA = "/api/adopciones/postulaciones/"


class ColeccionFalsa:
    def __init__(self, documentos):
        self.documentos = documentos

    def find_one(self, filtro, proyeccion=None):
        for doc in self.documentos:
            if all(doc.get(k) == v for k, v in filtro.items()):
                return doc
        return None

    def update_one(self, filtro, cambio):
        doc = self.find_one(filtro)
        if doc:
            doc.update(cambio["$set"])
        return SimpleNamespace(modified_count=1 if doc else 0)


@pytest.fixture
def cliente(monkeypatch):
    coleccion = ColeccionFalsa([
        {"id": "P-REC", "estado": "recibida"},
        {"id": "P-EVA", "estado": "en evaluación"},
        {"id": "P-APR", "estado": "aprobada"},
    ])
    monkeypatch.setattr(evaluar, "get_postulaciones", lambda: coleccion)
    app.dependency_overrides[evaluar.solo_funcionario] = lambda: {"rut": "17777777-3", "perfil": "funcionario"}
    yield TestClient(app)  # sin "with": no corre el arranque, asi no toca la base
    app.dependency_overrides.clear()


def test_aprobar(cliente):
    r = cliente.put(RUTA + "P-EVA/estado", json={"estado": "aprobada"})
    assert r.status_code == 200
    assert r.json()["estado"] == "aprobada"
    assert r.json()["evaluadoPor"] == "17777777-3"
    assert r.json()["fechaActualizacion"].endswith("Z")


def test_rechazar_con_motivo(cliente):
    r = cliente.put(RUTA + "P-EVA/estado", json={"estado": "rechazada", "motivo": "Vivienda no apta"})
    assert r.status_code == 200
    assert r.json()["motivo"] == "Vivienda no apta"


def test_rechazar_sin_motivo_da_400(cliente):
    r = cliente.put(RUTA + "P-EVA/estado", json={"estado": "rechazada"})
    assert r.status_code == 400
    assert r.json()["error"]["codigo"] == "DATOS_INVALIDOS"


def test_motivo_en_blanco_da_400(cliente):
    r = cliente.put(RUTA + "P-EVA/estado", json={"estado": "rechazada", "motivo": "   "})
    assert r.status_code == 400


def test_estado_desconocido_da_400(cliente):
    r = cliente.put(RUTA + "P-EVA/estado", json={"estado": "regalada"})
    assert r.status_code == 400


def test_campo_extra_da_400(cliente):
    r = cliente.put(RUTA + "P-EVA/estado", json={"estado": "aprobada", "postulanteRut": "1-9"})
    assert r.status_code == 400


def test_transicion_no_permitida_da_409(cliente):
    r = cliente.put(RUTA + "P-REC/estado", json={"estado": "aprobada"})
    assert r.status_code == 409
    assert r.json()["error"]["codigo"] == "REGLA_NEGOCIO"


def test_repetir_la_misma_evaluacion_da_409(cliente):
    cliente.put(RUTA + "P-EVA/estado", json={"estado": "aprobada"})
    r = cliente.put(RUTA + "P-EVA/estado", json={"estado": "aprobada"})
    assert r.status_code == 409


def test_inexistente_da_404(cliente):
    r = cliente.put(RUTA + "NO-EXISTE/estado", json={"estado": "aprobada"})
    assert r.status_code == 404
    assert r.json()["error"]["codigo"] == "NO_ENCONTRADO"


def test_sin_token_da_401(cliente):
    app.dependency_overrides.clear()
    r = cliente.put(RUTA + "P-EVA/estado", json={"estado": "aprobada"})
    assert r.status_code == 401
    assert r.json()["error"]["codigo"] == "NO_AUTENTICADO"
