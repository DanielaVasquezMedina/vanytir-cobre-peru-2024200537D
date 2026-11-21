# Nombres y apellidos: Daniela Andrea Vásquez Medina
# Código de matrícula: 2024200537D
# Tema y número del temario: Tema 50, VAN y TIR de un proyecto minero frente a la volatilidad del precio del cobre (Unidad II)
# Fecha de extracción: 2026-11-20

# Vía 2: descarga programática del Excel de Anexos del BEM Diciembre 2025 (MINEM)
import os
import datetime
import hashlib
import requests

URL = "https://cdn.www.gob.pe/uploads/document/file/9503677/7779621-bem-diciembre-2025-excel-de-anexos.xlsx?v=1772036174"
CABECERAS = {"User-Agent": "Estudiante-UNCP-Finanzas-I/1.0 (trabajo academico)"}
TIMEOUT = 60
CARPETA = "datos_crudos/minem"
RUTA = os.path.join(CARPETA, "bem_anexos_dic2025.xlsx")
ARCHIVO_LOG = "log_ejecucion.txt"
os.makedirs(CARPETA, exist_ok=True)

# Descarga el archivo; si falla, el script se detiene
momento = datetime.datetime.now().isoformat(timespec="seconds")
respuesta = requests.get(URL, headers=CABECERAS, timeout=TIMEOUT)
respuesta.raise_for_status()

# Guarda el archivo original sin modificarlo
with open(RUTA, "wb") as archivo:
    archivo.write(respuesta.content)

# Calcula la huella SHA-256 para verificar que el archivo no cambió
sha256 = hashlib.sha256(respuesta.content).hexdigest()
with open(ARCHIVO_LOG, "a", encoding="utf-8") as log:
    log.write(f"{momento} | MINEM | OK | HTTP {respuesta.status_code} | {len(respuesta.content)} bytes | SHA-256 {sha256} | {URL}\n")
print("Descarga correcta:", RUTA)
print("SHA-256:", sha256)
