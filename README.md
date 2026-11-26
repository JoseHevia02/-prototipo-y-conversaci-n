Módulo 3: Adopciones  Sistema municipal de tenencia responsable de mascotas
Este módulo gestiona las postulaciones para adoptar animales. Una postulación pasa por seis estados: recibida, en evaluación, aprobada, rechazada, adopción concretada y devuelto. Se conecta con el núcleo (inicio de sesión y personas) y con el M1 simulado (animales), y guarda sus datos en su propia base MongoDB.

Integrantes

Juan Apalmo	apalmo98	Arquitecto de software
José Hevia	JoseHevia02	Back
Angelo Torres	
Alejandro Córdova	AlejandroCordova	UX

link de prototipo 

URL: https://modulo-de-adopciones.onrender.com

Páginas: /postular (HU-02),https://modulo-de-adopciones.onrender.com/postular
 /evaluar (HU-05),https://modulo-de-adopciones.onrender.com/evaluar
 /consultas (HU-05),https://modulo-de-adopciones.onrender.com/consultas

Documentación automática de la API: /docs

El servicio gratuito se duerme tras unos minutos sin uso. La primera petición puede tardar en responder.

Stack

Python 3.12 y FastAPI

MongoDB Atlas (base tr_adopciones, colección postulaciones)

Render (despliegue del módulo)

Páginas HTML simples servidas por la misma aplicación