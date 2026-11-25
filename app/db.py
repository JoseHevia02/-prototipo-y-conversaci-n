import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
uri = os.getenv("conexionmongodc")
if not uri:
    raise Exception("Falta conexionmongodc")

client = MongoClient(uri, serverSelectionTimeoutMS=5000)
db = client["tr_adopciones"]


def get_postulaciones():
    return db["postulaciones"]