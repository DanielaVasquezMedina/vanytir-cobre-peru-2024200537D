# Nombres y apellidos: Daniela Andrea Vásquez Medina
# Código de matrícula: 2024200537D
# Tema y número del temario: Tema 50, VAN y TIR de un proyecto minero frente a la volatilidad del precio del cobre (Unidad II)
# Fecha de extracción: 2026-11-20

# Vía 1: consumo de la API del BCRP (cobre y tipo de cambio)
import os
import datetime
import requests

# Parámetros declarados
BASE_URL = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
SERIES = ["PN38784BM", "PN01207PM"]   # cobre (¢US$/lb) y tipo de cambio interbancario promedio (S/ por US$)
FORMATO = "json"
FECHA_INICIO = "2010-1"               # año-mes, sin cero inicial (ejemplo oficial)
FECHA_CORTE = "2025-12"
IDIOMA = "esp"
TIMEOUT = 60
CABECERAS = {"User-Agent": "Estudiante-UNCP-Finanzas-I/1.0 (trabajo academico)"}
CARPETA_CRUDOS = "datos_crudos/bcrp"
ARCHIVO_LOG = "log_ejecucion.txt"
os.makedirs(CARPETA_CRUDOS, exist_ok=True)

# Construye la URL: base / códigos / formato / inicio / fin / idioma
url = f"{BASE_URL}/{'-'.join(SERIES)}/{FORMATO}/{FECHA_INICIO}/{FECHA_CORTE}/{IDIOMA}"
print("URL de consulta:", url)
momento = datetime.datetime.now().isoformat(timespec="seconds")

# Consulta la API; si falla, registra el error y detiene el script
try:
    respuesta = requests.get(url, headers=CABECERAS, timeout=TIMEOUT)
    respuesta.raise_for_status()
    codigo_http = respuesta.status_code
except requests.RequestException as error:
    with open(ARCHIVO_LOG, "a", encoding="utf-8") as log:
        log.write(f"{momento} | BCRP | ERROR | {url} | {error}\n")
    raise

# Guarda la respuesta original sin modificarla
ruta_crudo = os.path.join(CARPETA_CRUDOS, "bcrp_api_respuesta_cruda.json")
with open(ruta_crudo, "wb") as archivo:
    archivo.write(respuesta.content)

with open(ARCHIVO_LOG, "a", encoding="utf-8") as log:
    log.write(f"{momento} | BCRP | OK | HTTP {codigo_http} | {len(respuesta.content)} bytes | {url}\n")
print("Código HTTP:", codigo_http, "| Archivo crudo:", ruta_crudo)
