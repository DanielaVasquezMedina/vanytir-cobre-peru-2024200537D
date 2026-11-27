# Nombres y apellidos: Daniela Andrea Vásquez Medina
# Código de matrícula: 2024200537D
# Tema y número del temario: Tema 50, VAN y TIR de un proyecto minero frente a la volatilidad del precio del cobre (Unidad II)
# Fecha de extracción: 2026-11-21

# Vía 1 (API): descarga de tres series DIARIAS del BCRP mediante su API pública.
# Entrada : ninguna (los datos se piden directamente al servidor del BCRP)
# Salidas : datos_crudos/bcrp/bcrp_api_respuesta_cruda.json (respuesta tal cual, sin modificar)
#           datos_crudos/datos_crudos_2024200537D.csv (la misma respuesta volcada a tabla,
#           sin ninguna limpieza, con el codigo de matricula en el nombre como pide el
#           numeral 2.4.2 de la consigna)
import os
import csv
import json
import time
import hashlib
from datetime import datetime

import requests

# ---------------------------------------------------------------------------
# 1. PARÁMETROS DE LA CONSULTA (constantes, nunca fechas dinámicas tipo "hoy")
# ---------------------------------------------------------------------------
# PD04701XD: Cotizaciones internacionales - Cobre (Londres), centavos de US$ por libra. Fuente: Reuters.
# PD04637PD: Tipo de cambio interbancario, soles por dólar, compra.
# PD04638PD: Tipo de cambio interbancario, soles por dólar, venta.
SERIES = ["PD04701XD", "PD04637PD", "PD04638PD"]
FECHA_INICIO = "2010-01-01"      # congelada: la reejecución debe dar el mismo rango
FECHA_CORTE = "2025-12-31"       # congelada
IDIOMA = "esp"
FORMATO = "json"

# La API no documenta un límite de periodos por consulta. Para no pedir 16 años de golpe,
# la descarga se hace por años y con una pausa entre solicitudes, como exige el numeral 2.4.8.
PAUSA_SEGUNDOS = 1.0
TIMEOUT = 60

# User-Agent identificable, exigido por el numeral 2.4.8 de la consigna.
# Se lee de la variable de entorno BCRP_USER_AGENT para no fijar datos de contacto
# dentro del código, conforme al numeral 2.4.4. Si la variable no está definida se usa
# el valor por omisión, de modo que el script corre igual en una máquina limpia.
USER_AGENT_POR_OMISION = "Proyecto academico UNCP - Finanzas I - 2024200537D"
CABECERAS = {"User-Agent": os.environ.get("BCRP_USER_AGENT", USER_AGENT_POR_OMISION)}

BASE = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
CARPETA_CRUDO = "datos_crudos/bcrp"
RUTA_CRUDO = os.path.join(CARPETA_CRUDO, "bcrp_api_respuesta_cruda.json")
# El numeral 2.4.2 exige que los archivos de datos lleven el codigo de matricula en el
# nombre. Este CSV es el mismo contenido del JSON puesto en forma de tabla, sin convertir
# tipos ni corregir nada: los valores van tal como los entrega el BCRP, incluido "n.d.".
RUTA_CRUDO_CSV = os.path.join("datos_crudos", "datos_crudos_2024200537D.csv")
ARCHIVO_LOG = "log_ejecucion.txt"
os.makedirs(CARPETA_CRUDO, exist_ok=True)


def huella_sha256(ruta):
    """Devuelve la huella SHA-256 de un archivo, o None si el archivo no existe.
    Sirve para comprobar la integridad y para comparar una descarga con la anterior."""
    if not os.path.exists(ruta):
        return None
    with open(ruta, "rb") as archivo:
        return hashlib.sha256(archivo.read()).hexdigest()


# Huella de la descarga anterior, tomada ANTES de sobrescribir el archivo. Permite saber
# si el BCRP revisó la serie entre una extracción y otra (numeral 2.4.5 de la consigna).
HUELLA_ANTERIOR = huella_sha256(RUTA_CRUDO)

anio_inicio = int(FECHA_INICIO[:4])
anio_fin = int(FECHA_CORTE[:4])

# ---------------------------------------------------------------------------
# 2. DESCARGA POR TRAMOS ANUALES
# ---------------------------------------------------------------------------
respuestas = []                       # aquí se guarda la respuesta cruda de cada año
codigos_series = "-".join(SERIES)     # la API separa los códigos con guiones

for anio in range(anio_inicio, anio_fin + 1):
    # El primer y el último tramo se recortan a las fechas declaradas como constantes
    desde = FECHA_INICIO if anio == anio_inicio else f"{anio}-01-01"
    hasta = FECHA_CORTE if anio == anio_fin else f"{anio}-12-31"
    url = f"{BASE}/{codigos_series}/{FORMATO}/{desde}/{hasta}/{IDIOMA}"

    respuesta = requests.get(url, headers=CABECERAS, timeout=TIMEOUT)
    respuesta.raise_for_status()      # si el servidor responde con error, el script se detiene aquí
    contenido = respuesta.json()

    # Control: un año hábil tiene alrededor de 250 días. Menos de 200 indica una descarga incompleta.
    n_periodos = len(contenido["periods"])
    assert n_periodos >= 200, f"El año {anio} devolvió solo {n_periodos} periodos: descarga incompleta"

    respuestas.append({
        "anio": anio,
        "url": url,
        "codigo_http": respuesta.status_code,
        "n_periodos": n_periodos,
        "contenido": contenido,       # la respuesta del BCRP se guarda sin tocar
    })
    print(f"Año {anio}: HTTP {respuesta.status_code} | {n_periodos} días")

    time.sleep(PAUSA_SEGUNDOS)        # pausa entre solicitudes para no sobrecargar el portal

# ---------------------------------------------------------------------------
# 3. GUARDADO DEL CRUDO Y REGISTRO EN LA BITÁCORA
# ---------------------------------------------------------------------------
crudo = {
    "consulta": {
        "series": SERIES,
        "fecha_inicio": FECHA_INICIO,
        "fecha_corte": FECHA_CORTE,
        "idioma": IDIOMA,
        "tramos": len(respuestas),
    },
    "respuestas": respuestas,
}
with open(RUTA_CRUDO, "w", encoding="utf-8") as archivo:
    json.dump(crudo, archivo, ensure_ascii=False)

total_dias = sum(r["n_periodos"] for r in respuestas)
print("\nArchivo crudo (JSON):", RUTA_CRUDO)
print("Tramos descargados:", len(respuestas), "| Total de días:", total_dias)

# ---------------------------------------------------------------------------
# 4. EL MISMO CRUDO EN FORMATO CSV, CON EL CÓDIGO DE MATRÍCULA EN EL NOMBRE
# ---------------------------------------------------------------------------
# Esto NO es limpieza: no se convierten tipos, no se descartan filas, no se renombran
# variables y no se calcula nada. Cada fila es un periodo tal como lo devolvió la API y
# cada valor es la cadena de texto original, incluido el "n.d." de los días sin cotización.
# La limpieza ocurre después, en 03_limpieza_datos.py, que lee el JSON.
#
# Cuidado con un detalle: la API NO devuelve las series en el orden en que se piden.
# Por eso las columnas se identifican por el nombre que el propio BCRP les da y los
# valores se asignan por nombre, nunca por posición.
nombres_series = [s["name"] for s in respuestas[0]["contenido"]["config"]["series"]]
COLUMNAS = ["periodo"] + nombres_series

filas_csv = []
for tramo in respuestas:
    # Nombres de las series de ESTE tramo, en el orden en que llegaron
    nombres_tramo = [s["name"] for s in tramo["contenido"]["config"]["series"]]
    assert set(nombres_tramo) == set(nombres_series), (
        f"El tramo {tramo['anio']} devolvió series distintas: {nombres_tramo}")

    for periodo in tramo["contenido"]["periods"]:
        fila = {"periodo": periodo["name"]}            # p. ej. "01.Dic.25", sin convertir
        for nombre, valor in zip(nombres_tramo, periodo["values"]):
            fila[nombre] = valor                       # el valor queda como texto, sin tocar
        filas_csv.append(fila)

with open(RUTA_CRUDO_CSV, "w", encoding="utf-8", newline="") as archivo:
    escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS)
    escritor.writeheader()
    escritor.writerows(filas_csv)

assert len(filas_csv) == total_dias, "El CSV crudo no tiene una fila por periodo descargado"
print("Archivo crudo (CSV):", RUTA_CRUDO_CSV, "|", len(filas_csv), "filas |", len(COLUMNAS), "columnas")

# ---------------------------------------------------------------------------
# 5. INTEGRIDAD Y COMPARACIÓN CON LA DESCARGA ANTERIOR
# ---------------------------------------------------------------------------
# El numeral 2.4.5 admite que una fuente viva revise sus datos hacia atrás. Comparar la
# huella de esta descarga con la de la anterior permite demostrar si la serie cambió.
huella_json = huella_sha256(RUTA_CRUDO)
huella_csv = huella_sha256(RUTA_CRUDO_CSV)
print("\nSHA-256 del JSON:", huella_json)
print("SHA-256 del CSV :", huella_csv)

if HUELLA_ANTERIOR is None:
    estado_fuente = "primera extraccion, sin descarga previa con la que comparar"
elif HUELLA_ANTERIOR == huella_json:
    estado_fuente = "sin cambios respecto de la descarga anterior"
else:
    estado_fuente = "ATENCION: la fuente cambio respecto de la descarga anterior"
print(estado_fuente.upper() if estado_fuente.startswith("ATENCION") else estado_fuente)

# ---------------------------------------------------------------------------
# 6. REGISTRO EN LA BITÁCORA
# ---------------------------------------------------------------------------
# El numeral 2.4.2 pide fecha y hora de cada extracción, número de filas y código HTTP.
# astimezone() adjunta el desplazamiento horario del entorno. Sin él, un mismo sello
# puede leerse como hora local o como UTC: Colab corre en UTC y el usuario está en
# Lima (UTC-05:00), de modo que una corrida de las 22:56 figuraría como las 03:56
# del día siguiente. Con el desplazamiento explícito la hora deja de ser ambigua.
sello = datetime.now().astimezone().isoformat(timespec="seconds")
with open(ARCHIVO_LOG, "a", encoding="utf-8") as log:
    log.write(
        f"{sello} | Extraccion API BCRP diaria | {len(respuestas)} tramos | "
        f"{total_dias} dias | HTTP 200 | {RUTA_CRUDO} | SHA-256 {huella_json}\n")
    log.write(
        f"{sello} | Crudo en CSV | {len(filas_csv)} filas | {len(COLUMNAS)} columnas | "
        f"{RUTA_CRUDO_CSV} | SHA-256 {huella_csv} | {estado_fuente}\n")
