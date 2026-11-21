# Nombres y apellidos: Daniela Andrea Vásquez Medina
# Código de matrícula: 2024200537D
# Tema y número del temario: Tema 50, VAN y TIR de un proyecto minero frente a la volatilidad del precio del cobre (Unidad II)
# Fecha de extracción: 2026-11-20

# Limpieza de la serie mensual del BCRP y verificación cruzada con el Excel del MINEM
import os
import json
import pandas as pd

RUTA_CRUDO = "datos_crudos/bcrp/bcrp_api_respuesta_cruda.json"
CARPETA_PROC = "datos_procesados"
RUTA_PROC = os.path.join(CARPETA_PROC, "bcrp_mensual_2024200537D.csv")
RUTA_MINEM = "datos_crudos/minem/bem_anexos_dic2025.xlsx"
ARCHIVO_LOG = "log_ejecucion.txt"
os.makedirs(CARPETA_PROC, exist_ok=True)

# Abreviaturas de meses del BCRP a número de mes
MESES = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6,
         "Jul": 7, "Ago": 8, "Set": 9, "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12}

# 1. Lee el JSON crudo sin modificarlo
with open(RUTA_CRUDO, encoding="utf-8") as archivo:
    datos = json.load(archivo)

# 2. Verifica el orden de las series (tipo de cambio primero, cobre después)
nombres_series = [s["name"] for s in datos["config"]["series"]]
assert len(nombres_series) == 2, "Se esperaban 2 series"
assert "Interbancario" in nombres_series[0], "El orden de las series cambió"
assert "Cobre" in nombres_series[1], "El orden de las series cambió"
columnas = ["tipo_cambio_interbancario_sol_usd", "precio_cobre_cent_usd_lb"]

# 3. Convierte "Ene.2010" en fecha (primer día del mes)
filas = []
for periodo in datos["periods"]:
    mes_txt, anio_txt = periodo["name"].split(".")
    fecha = pd.Timestamp(year=int(anio_txt), month=MESES[mes_txt], day=1)
    filas.append([fecha] + periodo["values"])
df = pd.DataFrame(filas, columns=["fecha"] + columnas)
assert len(df) == 192, f"Se esperaban 192 periodos y hay {len(df)}"

# 4. Convierte a número; detiene el script si algún valor no es numérico
for c in columnas:
    df[c] = pd.to_numeric(df[c], errors="coerce")
assert df[columnas].notna().all().all(), "Hay valores no numéricos"
assert df["fecha"].is_unique, "Hay fechas repetidas"

# 5. Cobre de ¢US$/lb a US$/lb
df["precio_cobre_usd_lb"] = df["precio_cobre_cent_usd_lb"] / 100

# 6. Ordena y registra la fuente de cada variable
df = df.sort_values("fecha").reset_index(drop=True)
df["fuente_tipo_cambio"] = "BCRP PN01207PM"
df["fuente_cobre"] = "BCRP PN38784BM"
df.to_csv(RUTA_PROC, index=False, encoding="utf-8")
print("Tabla procesada:", RUTA_PROC)

# 7. Verificación cruzada con el Excel del MINEM (la hoja 5 cita al BCRP como fuente: consistencia, no independencia)
macro = pd.read_excel(RUTA_MINEM, sheet_name="5. MACROECONÓMICAS", header=None)
minem_2025 = macro.iloc[17:29, [0, 4]].copy()
minem_2025.columns = ["mes", "tc_minem"]
minem_2025["tc_minem"] = pd.to_numeric(minem_2025["tc_minem"].astype(str).str.replace(",", "."), errors="coerce")
bcrp_2025 = df[df["fecha"].dt.year == 2025].reset_index(drop=True)
comparacion = pd.DataFrame({
    "mes": bcrp_2025["fecha"].dt.month,
    "tc_bcrp": bcrp_2025["tipo_cambio_interbancario_sol_usd"],
    "tc_minem": minem_2025["tc_minem"].values,
})
comparacion["diferencia"] = comparacion["tc_bcrp"] - comparacion["tc_minem"]
print("Diferencia máxima absoluta (BCRP vs MINEM, 2025):", round(comparacion["diferencia"].abs().max(), 6))

with open(ARCHIVO_LOG, "a", encoding="utf-8") as log:
    log.write(f"Limpieza BCRP | {len(df)} periodos | {RUTA_PROC}\n")
