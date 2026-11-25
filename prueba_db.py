from app.db import get_postulaciones

col = get_postulaciones()
col.insert_one({"id": "POST-TEST-001"})
print(col.find_one({"id": "POST-TEST-001"}, {"_id": 0}))