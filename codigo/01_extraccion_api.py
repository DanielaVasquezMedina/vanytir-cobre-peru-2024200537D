# Nombres y apellidos: Daniela Andrea Vásquez Medina
# Código de matrícula: 2024200537D
# Tema y número del temario: Tema 50, VAN y TIR de un proyecto minero frente a la volatilidad del precio del cobre (Unidad II)
# Fecha de extracción: 2026-11-21

# Vía 1 (API): descarga de tres series DIARIAS del BCRP mediante su API pública.
# Entrada : ninguna (los datos se piden directamente al servidor del BCRP)
# Salida  : datos_crudos/bcrp/bcrp_api_respuesta_cruda.json (respuesta tal cual, sin modificar)
import os
import json
import time
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

# User-Agent identificable, también exigido por la consigna
CABECERAS = {"User-Agent": "Proyecto academico UNCP - Finanzas I - 2024200537D"}

BASE = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
CARPETA_CRUDO = "datos_crudos/bcrp"
RUTA_CRUDO = os.path.join(CARPETA_CRUDO, "bcrp_api_respuesta_cruda.json")
ARCHIVO_LOG = "log_ejecucion.txt"
os.makedirs(CARPETA_CRUDO, exist_ok=True)

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
print("\nArchivo crudo:", RUTA_CRUDO)
print("Tramos descargados:", len(respuestas), "| Total de días:", total_dias)

with open(ARCHIVO_LOG, "a", encoding="utf-8") as log:
    log.write(f"Extraccion API BCRP diaria | {len(respuestas)} tramos | {total_dias} dias | HTTP 200 | {RUTA_CRUDO}\n")
