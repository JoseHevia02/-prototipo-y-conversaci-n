# Maquina de estados de una postulacion.
# La usan HU-05 (evaluar) y HU-06 (entrega): es la unica fuente de reglas.

RECIBIDA = "recibida"
EN_EVALUACION = "en evaluación"
APROBADA = "aprobada"
RECHAZADA = "rechazada"
CONCRETADA = "adopción concretada"
DEVUELTO = "devuelto"

ESTADOS = [RECIBIDA, EN_EVALUACION, APROBADA, RECHAZADA, CONCRETADA, DEVUELTO]

# Para cada estado, a cuales se puede pasar. Lista vacia = estado final.
TRANSICIONES = {
    RECIBIDA: [EN_EVALUACION],
    EN_EVALUACION: [APROBADA, RECHAZADA],
    APROBADA: [CONCRETADA],
    CONCRETADA: [DEVUELTO],
    RECHAZADA: [],
    DEVUELTO: [],
}

# RN-07: estos estados deben guardar el motivo.
ESTADOS_CON_MOTIVO = [RECHAZADA, DEVUELTO]


def puede_cambiar(actual, nuevo):
    return nuevo in TRANSICIONES.get(actual, [])
