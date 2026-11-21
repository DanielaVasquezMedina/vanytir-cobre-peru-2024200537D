# Nombres y apellidos: Daniela Andrea Vásquez Medina
# Código de matrícula: 2024200537D
# Tema y número del temario: Tema 50, VAN y TIR de un proyecto minero frente a la volatilidad del precio del cobre (Unidad II)
# Fecha de extracción: 2026-11-21

# Limpieza y unión de las dos fuentes: serie DIARIA del BCRP (Vía 1, API) y Excel del MINEM (Vía 2, descarga programática).
# Entradas : datos_crudos/bcrp/bcrp_api_respuesta_cruda.json y datos_crudos/minem/bem_anexos_dic2025.xlsx
# Salida   : datos_procesados/datos_procesados_2024200537D.csv
import os
import json
import pandas as pd

RUTA_CRUDO = "datos_crudos/bcrp/bcrp_api_respuesta_cruda.json"
RUTA_MINEM = "datos_crudos/minem/bem_anexos_dic2025.xlsx"
CARPETA_PROC = "datos_procesados"
RUTA_PROC = os.path.join(CARPETA_PROC, "datos_procesados_2024200537D.csv")
ARCHIVO_LOG = "log_ejecucion.txt"
os.makedirs(CARPETA_PROC, exist_ok=True)

ANIO_INICIO = 2010
ANIO_FIN = 2025
LIBRAS_POR_TONELADA = 2204.62     # una tonelada métrica equivale a 2 204,62 libras

# Abreviaturas de meses que usa el BCRP en los nombres de periodo ("01.Dic.25")
MESES = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6,
         "Jul": 7, "Ago": 8, "Set": 9, "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12}

# ---------------------------------------------------------------------------
# 1. FUENTE 1 (API BCRP): lectura del crudo y armado de la serie diaria
# ---------------------------------------------------------------------------
with open(RUTA_CRUDO, encoding="utf-8") as archivo:   # el crudo solo se lee, nunca se modifica
    crudo = json.load(archivo)

def columna_de(nombre_serie):
    """Traduce el nombre largo que devuelve el BCRP al nombre corto de nuestra columna.
    Es necesario porque la API devuelve las series en un orden distinto al que se piden,
    así que no se puede confiar en la posición: hay que identificarlas por su nombre."""
    texto = nombre_serie.lower()
    if "cobre" in texto:
        return "precio_cobre_cent_usd_lb"
    if "compra" in texto:
        return "tc_interbancario_compra_sol_usd"
    if "venta" in texto:
        return "tc_interbancario_venta_sol_usd"
    raise ValueError(f"Serie no reconocida: {nombre_serie}")

filas = []
for tramo in crudo["respuestas"]:                      # un tramo por año descargado
    contenido = tramo["contenido"]
    # Orden real de las series dentro de ESTE tramo
    nombres = [s["name"] for s in contenido["config"]["series"]]
    columnas_tramo = [columna_de(n) for n in nombres]
    assert len(set(columnas_tramo)) == 3, f"Se esperaban 3 series distintas y llegaron: {nombres}"

    for periodo in contenido["periods"]:
        # El nombre del periodo tiene la forma "01.Dic.25": día, mes abreviado y año de dos dígitos
        dia_txt, mes_txt, anio_txt = periodo["name"].split(".")
        anio = 2000 + int(anio_txt)                    # 10 -> 2010, 25 -> 2025
        assert ANIO_INICIO <= anio <= ANIO_FIN, f"Año fuera de la ventana declarada: {periodo['name']}"
        fecha = pd.Timestamp(year=anio, month=MESES[mes_txt], day=int(dia_txt))

        registro = {"fecha": fecha}
        for columna, valor in zip(columnas_tramo, periodo["values"]):
            registro[columna] = valor
        filas.append(registro)

df = pd.DataFrame(filas)

# Convierte a número; el BCRP entrega los valores como texto y puede usar "n.d." en días sin cotización
for c in ["precio_cobre_cent_usd_lb", "tc_interbancario_compra_sol_usd", "tc_interbancario_venta_sol_usd"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# ---------------------------------------------------------------------------
# 2. TRATAMIENTO DE VALORES FALTANTES Y DUPLICADOS
# ---------------------------------------------------------------------------
filas_iniciales = len(df)
df = df.drop_duplicates(subset="fecha")                # por si dos tramos compartieran un día
filas_sin_duplicados = len(df)

# Se eliminan los días sin cotización completa: son feriados o días sin operación,
# no datos perdidos que haya que imputar. Nunca se rellenan con valores inventados.
df = df.dropna(subset=["precio_cobre_cent_usd_lb",
                       "tc_interbancario_compra_sol_usd",
                       "tc_interbancario_venta_sol_usd"])
filas_finales = len(df)
print(f"Días descargados: {filas_iniciales} | sin duplicados: {filas_sin_duplicados} | con cotización completa: {filas_finales}")

df = df.sort_values("fecha").reset_index(drop=True)
df["anio"] = df["fecha"].dt.year                       # llave común para unir con el MINEM

assert df["fecha"].is_unique, "Hay fechas repetidas"
assert len(df) >= 1000, f"La base tiene {len(df)} observaciones y el mínimo exigido es 1000"
assert df["precio_cobre_cent_usd_lb"].gt(0).all(), "Hay precios no positivos"

# ---------------------------------------------------------------------------
# 3. VARIABLES DERIVADAS DEL BCRP
# ---------------------------------------------------------------------------
df["precio_cobre_usd_lb"] = df["precio_cobre_cent_usd_lb"] / 100   # de centavos a dólares por libra

# El BCRP no publica una serie diaria del interbancario promedio, así que se calcula
# como el promedio simple de compra y venta. La declaración de este cálculo es obligatoria.
df["tc_interbancario_promedio_sol_usd"] = (
    df["tc_interbancario_compra_sol_usd"] + df["tc_interbancario_venta_sol_usd"]
) / 2

df["precio_cobre_soles_lb"] = df["precio_cobre_usd_lb"] * df["tc_interbancario_promedio_sol_usd"]

# ---------------------------------------------------------------------------
# 4. FUENTE 2 (MINEM): producción anual de cobre en toneladas métricas finas
# ---------------------------------------------------------------------------
# La hoja trae filas de años (2000-2025) y, debajo, los meses del último año.
# Solo se conservan las filas cuyo PERIODO es un año, para no mezclar meses con años.
produccion = pd.read_excel(RUTA_MINEM, sheet_name="1. PRODUCCIÓN METÁLICA", header=None)
periodo_num = pd.to_numeric(produccion[0], errors="coerce")   # las filas de meses quedan como NaN
es_anio = periodo_num.between(1990, 2100)

minem = pd.DataFrame({
    "anio": periodo_num[es_anio].astype(int),
    "produccion_cobre_peru_tmf": pd.to_numeric(produccion.loc[es_anio, 1], errors="coerce"),
}).dropna().reset_index(drop=True)

assert minem["anio"].is_unique, "Hay años repetidos en la hoja de producción"
assert minem["produccion_cobre_peru_tmf"].gt(0).all(), "Hay producciones no positivas"

faltantes = set(range(ANIO_INICIO, ANIO_FIN + 1)) - set(minem["anio"])
assert not faltantes, f"Faltan años de producción en el MINEM: {sorted(faltantes)}"

# ---------------------------------------------------------------------------
# 5. UNIÓN DE LAS DOS FUENTES POR LA LLAVE COMÚN (año)
# ---------------------------------------------------------------------------
# Armonización de frecuencia declarada: la producción del MINEM es anual y la serie del BCRP es diaria.
# A cada día se le asigna la producción total del año al que pertenece. El valor no se reparte entre
# los días ni se interpola: es un atributo anual del país, y así debe interpretarse.
filas_antes = len(df)
df = df.merge(minem, on="anio", how="left")
assert len(df) == filas_antes, "La unión alteró el número de filas"
assert df["produccion_cobre_peru_tmf"].notna().all(), "Quedaron días sin producción asignada"

# Variable que integra las dos fuentes: valor de la producción nacional de cobre, en millones de dólares
df["valor_produccion_cobre_mill_usd"] = (
    df["produccion_cobre_peru_tmf"] * LIBRAS_POR_TONELADA * df["precio_cobre_usd_lb"] / 1_000_000
)

# ---------------------------------------------------------------------------
# 6. TRAZABILIDAD DE LAS FUENTES Y GUARDADO
# ---------------------------------------------------------------------------
df["fuente_bcrp"] = "BCRP API, series PD04701XD, PD04637PD y PD04638PD"
df["fuente_minem"] = "MINEM, BEM Diciembre 2025, Tabla 01 Produccion metalica"

df = df[[
    "fecha", "anio",
    "precio_cobre_cent_usd_lb", "precio_cobre_usd_lb",
    "tc_interbancario_compra_sol_usd", "tc_interbancario_venta_sol_usd",
    "tc_interbancario_promedio_sol_usd", "precio_cobre_soles_lb",
    "produccion_cobre_peru_tmf", "valor_produccion_cobre_mill_usd",
    "fuente_bcrp", "fuente_minem",
]]
df.to_csv(RUTA_PROC, index=False, encoding="utf-8")

print("\nTabla procesada:", RUTA_PROC)
print("Observaciones:", len(df), "| Columnas:", len(df.columns))
print("Rango de fechas:", df["fecha"].min().date(), "a", df["fecha"].max().date())
print(df.head(3).to_string(index=False))

# ---------------------------------------------------------------------------
# 7. VERIFICACIÓN CRUZADA CON EL MINEM (hoja 5, que cita al BCRP como fuente)
#    Es una nota de consistencia, no una verificación independiente.
#    Se comparan los promedios mensuales de 2025 del tipo de cambio diario con los del MINEM.
# ---------------------------------------------------------------------------
macro = pd.read_excel(RUTA_MINEM, sheet_name="5. MACROECONÓMICAS", header=None)
minem_2025 = macro.iloc[17:29, [0, 4]].copy()
minem_2025.columns = ["mes", "tc_minem"]
minem_2025["tc_minem"] = pd.to_numeric(minem_2025["tc_minem"].astype(str).str.replace(",", "."), errors="coerce")

promedio_mensual = (df[df["anio"] == 2025]
                    .groupby(df["fecha"].dt.month)["tc_interbancario_promedio_sol_usd"]
                    .mean()
                    .reindex(range(1, 13)))
diferencia = (promedio_mensual.values - minem_2025["tc_minem"].values)
print("\nDiferencia máxima del tipo de cambio mensual (BCRP diario promediado vs MINEM, 2025):",
      round(pd.Series(diferencia).abs().max(), 4))

with open(ARCHIVO_LOG, "a", encoding="utf-8") as log:
    log.write(f"Limpieza y union diaria | {len(df)} observaciones | {len(df.columns)} columnas | {RUTA_PROC}\n")
