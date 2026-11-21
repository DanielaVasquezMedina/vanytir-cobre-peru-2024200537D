# Nombres y apellidos: Daniela Andrea Vásquez Medina
# Código de matrícula: 2024200537D
# Tema y número del temario: Tema 50, VAN y TIR de un proyecto minero frente a la volatilidad del precio del cobre (Unidad II)
# Fecha de extracción: 2026-11-20

# Cálculo del VAN y la TIR de un proyecto minero tipo y su sensibilidad al precio del cobre.
# Entrada : datos_procesados/bcrp_mensual_2024200537D.csv (serie mensual del precio del cobre, generada por 03_limpieza_datos.py)
# Salidas : salidas/flujos_caja_2024200537D.csv, salidas/resultados_van_tir_2024200537D.csv, salidas/sensibilidad_tasa_2024200537D.csv
import os                      # os: para construir rutas y crear la carpeta de salidas
import pandas as pd            # pandas: para leer el CSV y construir las tablas de resultados

# ---------------------------------------------------------------------------
# 1. RUTAS DE ARCHIVOS
# ---------------------------------------------------------------------------
RUTA_PROC = "datos_procesados/bcrp_mensual_2024200537D.csv"   # tabla limpia que produce el script 03
CARPETA_SALIDAS = "salidas"                                   # carpeta donde se guardan los resultados del análisis
ARCHIVO_LOG = "log_ejecucion.txt"                             # bitácora exigida por la consigna
os.makedirs(CARPETA_SALIDAS, exist_ok=True)                   # crea la carpeta si todavía no existe (no falla si ya está)

# ---------------------------------------------------------------------------
# 2. PARÁMETROS DEL PROYECTO MINERO TIPO
#    Cada parámetro lleva su fuente. Lo que es supuesto propio está marcado como tal.
# ---------------------------------------------------------------------------

# --- Escala del proyecto: PEA actualizado de Cotabambas, comunicado oficial de Panoro del 22-09-2015 ---
MINERAL_TOTAL_MT = 483.0       # millones de toneladas de mineral alimentado a planta en toda la vida de la mina (fuente: comunicado, p. 5)
VIDA_UTIL_ANIOS = 17           # años de operación; "The mine plan supports a mine life of 17 years" (fuente: comunicado, p. 5)
MINERAL_ANUAL_MT = MINERAL_TOTAL_MT / VIDA_UTIL_ANIOS   # 483 / 17 = 28,41 Mt al año. Se usa el total dividido entre los años
                                                        # para que el tonelaje acumulado del modelo coincida exactamente con el del PEA.

# --- Calidad del mineral y procesamiento ---
LEY_CENTRAL = 0.00318          # 0,318 % de cobre. Cálculo propio: promedio ponderado del PEA (127,3 Mt al 0,37 % y 355,8 Mt al 0,30 %)
RECUPERACION_CENTRAL = 0.84    # 84 %. Fuente: Tabla 13-1 del informe NI 43-101 de La Granja (pórfido fresco), p. 93. SUPUESTO: se aplica a Cotabambas
LIBRAS_POR_TONELADA = 2204.62  # factor de conversión de toneladas métricas a libras (1 t = 2 204,62 lb)

# --- Costos operativos: PEA actualizado, tabla "Cotabambas Operating Costs", columna Updated PEA (p. 5) ---
COSTO_OPERATIVO_USD_T = 8.38   # dólares por tonelada procesada: mina 3,59 + procesamiento 4,38 + administración 0,41

# --- Inversión inicial (CAPEX), en millones de dólares ---
# Fuente: cartera de proyectos mineros (CPIM) del MINEM, muestra A de 24 proyectos nuevos de cobre.
# Son percentiles de la distribución observada, no probabilidades de ocurrencia.
CAPEX_ESCENARIOS = {"P25 (inversión baja)": 573.4, "P50 (central)": 1388.0, "P75 (inversión alta)": 2220.1}

# --- Parámetros tributarios y financieros ---
TASA_IMPUESTO = 0.295          # 29,50 % de impuesto a la renta de tercera categoría (artículo 55° del TUO de la Ley del Impuesto a la Renta)
TASA_DESCUENTO_CENTRAL = 0.1013  # 10,13 %. Cálculo propio: WACC de "Metals & Mining" de Damodaran (ene-2026) ajustado por el riesgo país de Perú (2,07 %)
TASAS_SENSIBILIDAD = [0.0820, 0.1013, 0.1200, 0.1400]  # 8,20 % es el WACC de Damodaran sin ajuste; las demás reflejan mayor exigencia de retorno

# --- Depreciación ---
# SUPUESTO ECONÓMICO SIMPLIFICADO, no depreciación tributaria: se reparte el CAPEX en partes iguales entre los años de operación.
# El artículo 22° del Reglamento de la Ley del Impuesto a la Renta fija topes por tipo de activo (maquinaria minera 20 %, edificios 5 %,
# otros bienes 10 %), pero no conocemos la composición del CAPEX por tipo de activo, así que no podemos aplicarlos.
# Depreciar más rápido adelantaría el ahorro de impuestos y SUBIRÍA el VAN: por eso este supuesto es el conservador.
ANIOS_DEPRECIACION = VIDA_UTIL_ANIOS

# ---------------------------------------------------------------------------
# 3. LECTURA DE LA SERIE DEL PRECIO DEL COBRE Y ESCENARIOS DE PRECIO
# ---------------------------------------------------------------------------
precios = pd.read_csv(RUTA_PROC, parse_dates=["fecha"])       # lee la tabla limpia; convierte la columna fecha a tipo fecha
assert "precio_cobre_usd_lb" in precios.columns, "Falta la columna del precio del cobre en dólares por libra"
assert len(precios) == 192, f"Se esperaban 192 meses (ene-2010 a dic-2025) y hay {len(precios)}"  # control de integridad

serie_precio = precios["precio_cobre_usd_lb"]                 # serie mensual del precio del cobre en US$ por libra

# Los escenarios de precio se construyen con los percentiles de la propia serie histórica, igual que los del CAPEX.
# Son posiciones dentro de la distribución observada 2010-2025, no pronósticos del precio futuro.
PRECIO_ESCENARIOS = {
    "P25 (precio bajo)": round(serie_precio.quantile(0.25), 4),    # un 25 % de los meses tuvo un precio igual o menor
    "P50 (precio central)": round(serie_precio.quantile(0.50), 4), # mediana: el valor que parte la serie en dos mitades
    "P75 (precio alto)": round(serie_precio.quantile(0.75), 4),    # un 75 % de los meses tuvo un precio igual o menor
}

# ---------------------------------------------------------------------------
# 4. FUNCIONES DE CÁLCULO
# ---------------------------------------------------------------------------

def libras_cobre_por_anio(ley, recuperacion):
    """Cobre vendible en millones de libras por año.
    Cadena de cálculo: toneladas de mineral -> cobre contenido -> cobre recuperado -> libras."""
    toneladas_mineral = MINERAL_ANUAL_MT * 1_000_000          # pasa de millones de toneladas a toneladas
    cobre_contenido_t = toneladas_mineral * ley               # el mineral solo contiene un pequeño porcentaje de cobre (la ley)
    cobre_recuperado_t = cobre_contenido_t * recuperacion     # la planta no logra extraer todo el cobre contenido
    return cobre_recuperado_t * LIBRAS_POR_TONELADA / 1_000_000  # convierte a libras y luego a millones de libras


def construir_flujos(precio_usd_lb, capex_millones, ley=LEY_CENTRAL, recuperacion=RECUPERACION_CENTRAL):
    """Devuelve la lista de flujos de caja libres en millones de dólares.
    Posición 0 = año 0 (solo la inversión); posiciones 1..17 = años de operación.
    Supuesto: el precio se mantiene constante durante toda la vida del proyecto en cada escenario."""
    produccion_mlb = libras_cobre_por_anio(ley, recuperacion)         # millones de libras vendidas cada año
    ingresos = produccion_mlb * precio_usd_lb                          # millones de dólares de ingreso anual
    costos = MINERAL_ANUAL_MT * 1_000_000 * COSTO_OPERATIVO_USD_T / 1_000_000  # costo anual en millones de dólares
    depreciacion = capex_millones / ANIOS_DEPRECIACION                 # parte del CAPEX que se descuenta cada año para el impuesto

    flujos = [-capex_millones]                                         # año 0: sale toda la inversión (signo negativo)
    for _ in range(VIDA_UTIL_ANIOS):                                   # se repite igual en cada año de operación
        utilidad_operativa = ingresos - costos                         # lo que queda antes de depreciación e impuesto (EBITDA)
        base_imponible = utilidad_operativa - depreciacion             # la depreciación reduce la renta sobre la que se paga impuesto
        impuesto = TASA_IMPUESTO * base_imponible if base_imponible > 0 else 0.0  # si hay pérdida no se paga impuesto
        flujo_libre = utilidad_operativa - impuesto                    # la depreciación se vuelve a sumar: no es salida de dinero
        flujos.append(flujo_libre)
    return flujos


def valor_actual_neto(flujos, tasa):
    """VAN: suma de los flujos traídos a valor de hoy. Cada flujo se divide entre (1 + tasa) elevado al año."""
    return sum(flujo / (1 + tasa) ** anio for anio, flujo in enumerate(flujos))


def tasa_interna_retorno(flujos, limite_inferior=-0.99, limite_superior=10.0, tolerancia=1e-7):
    """TIR: tasa que hace que el VAN sea exactamente cero.
    Se busca por bisección: se parte de un intervalo donde el VAN cambia de signo y se va reduciendo a la mitad."""
    van_inferior = valor_actual_neto(flujos, limite_inferior)
    van_superior = valor_actual_neto(flujos, limite_superior)
    if van_inferior * van_superior > 0:          # si el VAN no cambia de signo, la TIR no existe dentro del intervalo
        return None
    for _ in range(200):                         # 200 repeticiones bastan de sobra para la precisión pedida
        punto_medio = (limite_inferior + limite_superior) / 2
        van_medio = valor_actual_neto(flujos, punto_medio)
        if abs(van_medio) < tolerancia:          # si el VAN ya es prácticamente cero, se encontró la TIR
            return punto_medio
        if van_inferior * van_medio < 0:         # el cambio de signo está en la mitad izquierda
            limite_superior = punto_medio
        else:                                    # el cambio de signo está en la mitad derecha
            limite_inferior, van_inferior = punto_medio, van_medio
    return (limite_inferior + limite_superior) / 2


# ---------------------------------------------------------------------------
# 5. CASO BASE: FLUJO DE CAJA AÑO POR AÑO
# ---------------------------------------------------------------------------
precio_base = PRECIO_ESCENARIOS["P50 (precio central)"]       # precio mediano de la serie histórica
capex_base = CAPEX_ESCENARIOS["P50 (central)"]                # CAPEX mediano de la cartera del MINEM
flujos_base = construir_flujos(precio_base, capex_base)       # lista de 18 valores: año 0 más 17 años de operación

tabla_flujos = pd.DataFrame({                                  # se arma una tabla para guardarla y mostrarla en el dashboard
    "anio": range(len(flujos_base)),                           # 0, 1, 2, ..., 17
    "flujo_caja_millones_usd": [round(f, 2) for f in flujos_base],
})
tabla_flujos.to_csv(os.path.join(CARPETA_SALIDAS, "flujos_caja_2024200537D.csv"), index=False, encoding="utf-8")

# ---------------------------------------------------------------------------
# 6. MATRIZ DE ESCENARIOS: PRECIO DEL COBRE x CAPEX
# ---------------------------------------------------------------------------
filas = []
for nombre_precio, precio in PRECIO_ESCENARIOS.items():        # recorre los tres escenarios de precio
    for nombre_capex, capex in CAPEX_ESCENARIOS.items():       # y dentro de cada uno, los tres de inversión
        flujos = construir_flujos(precio, capex)
        van = valor_actual_neto(flujos, TASA_DESCUENTO_CENTRAL)
        tir = tasa_interna_retorno(flujos)
        filas.append({
            "escenario_precio": nombre_precio,
            "precio_usd_lb": precio,
            "escenario_capex": nombre_capex,
            "capex_millones_usd": capex,
            "van_millones_usd": round(van, 2),
            "tir_porcentaje": round(tir * 100, 2) if tir is not None else None,  # None si no existe TIR en el intervalo
        })
tabla_escenarios = pd.DataFrame(filas)
tabla_escenarios.to_csv(os.path.join(CARPETA_SALIDAS, "resultados_van_tir_2024200537D.csv"), index=False, encoding="utf-8")

# ---------------------------------------------------------------------------
# 7. SENSIBILIDAD DEL VAN A LA TASA DE DESCUENTO (con el CAPEX central)
# ---------------------------------------------------------------------------
filas_tasa = []
for nombre_precio, precio in PRECIO_ESCENARIOS.items():
    flujos = construir_flujos(precio, capex_base)
    for tasa in TASAS_SENSIBILIDAD:                            # el mismo proyecto evaluado con distintas exigencias de retorno
        filas_tasa.append({
            "escenario_precio": nombre_precio,
            "precio_usd_lb": precio,
            "tasa_descuento_porcentaje": round(tasa * 100, 2),
            "van_millones_usd": round(valor_actual_neto(flujos, tasa), 2),
        })
tabla_tasa = pd.DataFrame(filas_tasa)
tabla_tasa.to_csv(os.path.join(CARPETA_SALIDAS, "sensibilidad_tasa_2024200537D.csv"), index=False, encoding="utf-8")

# ---------------------------------------------------------------------------
# 8. RESUMEN EN PANTALLA Y BITÁCORA
# ---------------------------------------------------------------------------
print("Producción anual de cobre (millones de libras):", round(libras_cobre_por_anio(LEY_CENTRAL, RECUPERACION_CENTRAL), 1))
print("Escenarios de precio (US$/lb):", PRECIO_ESCENARIOS)
print("\nCaso base (precio y CAPEX centrales):")
print("  VAN (millones US$):", round(valor_actual_neto(flujos_base, TASA_DESCUENTO_CENTRAL), 2))
tir_base = tasa_interna_retorno(flujos_base)
print("  TIR (%):", round(tir_base * 100, 2) if tir_base is not None else "no existe")
print("\nMatriz de escenarios:")
print(tabla_escenarios.to_string(index=False))

with open(ARCHIVO_LOG, "a", encoding="utf-8") as log:
    log.write(f"Analisis VAN-TIR | {len(tabla_escenarios)} escenarios | salidas/resultados_van_tir_2024200537D.csv\n")
