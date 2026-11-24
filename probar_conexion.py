import os
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()


mongodb_uri = os.getenv("conexionmongodc")

if not mongodb_uri:
    raise ValueError("La variable de entorno MONGODB_URI no está definida o está vacía.")


client = MongoClient(mongodb_uri)

try:
    ping_response = client.admin.command("ping")
    print("Respuesta del ping:", ping_response)
finally:
    client.close()