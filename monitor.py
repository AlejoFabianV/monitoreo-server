import requests
import csv
import os
from dotenv import load_dotenv
from datetime import datetime

# URLs
LOGIN_URL = "https://autogestion.frd.utn.edu.ar/loginAlumno.asp?refrescar" # URL donde se procesa el login
TARGET_URL = "https://autogestion.frd.utn.edu.ar/estadoAcademico.asp?id=14833" # La URL protegida a medir
ARCHIVO_CSV = "tiempos_servidor.csv"
LIMITE_MEDICIONES = 4

load_dotenv()
USUARIO = os.environ.get("APP_USER")
PASSWORD = os.environ.get("APP_PASS")

def contar_mediciones():
    if not os.path.exists(ARCHIVO_CSV):
        return 0
    with open(ARCHIVO_CSV, "r", encoding="utf-8") as f:
        # Cuenta las lineas restando el encabezado
        return sum(1 for _ in f) - 1

def ejecutar_medicion():
    total_actual = contar_mediciones()
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    estado = "N/A"
    tiempo_ms = "N/A"
    observacion = "OK"

    with requests.Session() as sesion:
        try:
            # 1. POST a la URL de login con las credenciales
            payload = {
                "Legajo": USUARIO, 
                "Contraseña": PASSWORD 
            }
            
            #Inicio sesion
            respuesta_login = sesion.post(LOGIN_URL, data=payload, timeout=10)
            
            #Verifica si el login
            if respuesta_login.status_code != 200:
                print("Advertencia: El login pudo haber fallado.")

            # 2. Medimos la URL protegida usando la misma sesion ya autenticada
            respuesta = sesion.get(TARGET_URL, timeout=20)
            tiempo_ms = round(respuesta.elapsed.total_seconds() * 1000, 2)
            estado = respuesta.status_code
            
            if estado != 200:
                observacion = f"Error HTTP {estado}"

        except Exception as e:
            observacion = str(e)

    # 3. Guardar en CSV
    if total_actual == 0 and not os.path.exists(ARCHIVO_CSV):
        with open(ARCHIVO_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Fecha y Hora", "URL", "Estado HTTP", "Tiempo (ms)", "Observacion"])
    if total_actual <= LIMITE_MEDICIONES:
        with open(ARCHIVO_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([ahora, TARGET_URL, estado, tiempo_ms, observacion])
            print(f"Medición {total_actual + 1}/5 registrada: {tiempo_ms} ms")
    else:
        print(f"limite de medicones alcanzado")

if __name__ == "__main__":
    if not USUARIO or not PASSWORD:
        print("Error: Credenciales no encontradas en las variables de entorno.")
    else:
        ejecutar_medicion()