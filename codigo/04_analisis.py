# Nombres y apellidos: Daniela Andrea Vásquez Medina
# Código de matrícula: 2024200537D
# Tema y número del temario: Tema 50, VAN y TIR de un proyecto minero frente a la volatilidad del precio del cobre (Unidad II)
# Fecha de extracción: 2026-11-21

# Cálculo del VAN y la TIR de un proyecto minero tipo y su sensibilidad al precio del cobre.
# Entrada : datos_procesados/datos_procesados_2024200537D.csv
#           (serie DIARIA del precio del cobre y del tipo de cambio, generada por 03_limpieza_datos.py)
# Salidas : cuatro tablas en salidas/ (flujos_caja, resultados_van_tir, sensibilidad_tasa y
#           precio_equilibrio) y seis figuras en PNG, todas con el código de matrícula en el nombre.
import os                      # os: para construir rutas y crear la carpeta de salidas
import pandas as pd            # pandas: para leer el CSV y construir las tablas de resultados

# ---------------------------------------------------------------------------
# 1. RUTAS DE ARCHIVOS
# ---------------------------------------------------------------------------
RUTA_PROC = "datos_procesados/datos_procesados_2024200537D.csv"   # tabla limpia que produce el script 03
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
# VERIFICADO: tabla "Cotabambas Operating Costs ($US per tonne milled)", columna "Updated PEA",
# comunicado oficial de Panoro del 22-09-2015, página 5. El valor central NO es un supuesto propio;
# lo único propio es el rango de ±20 % que se usa en el gráfico de tornado.

# --- Inversión inicial (CAPEX), en millones de dólares ---
# Fuente: cartera de proyectos mineros (CPIM) del MINEM, muestra A de 24 proyectos nuevos de cobre.
# Son percentiles de la distribución observada, no probabilidades de ocurrencia.
CAPEX_ESCENARIOS = {"P25 (inversión baja)": 573.4, "P50 (central)": 1388.0, "P75 (inversión alta)": 2220.1}

# --- Parámetros tributarios y financieros ---
TASA_IMPUESTO = 0.295          # 29,50 % de impuesto a la renta de tercera categoría (artículo 55° del TUO de la Ley del Impuesto a la Renta)
TASA_DESCUENTO_CENTRAL = 0.1013  # 10.13 %. Cálculo propio: WACC de "Metals & Mining" de Damodaran (ene-2026) ajustado por el riesgo país de Perú (2.07 %)
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
assert len(precios) >= 1000, f"La base tiene {len(precios)} observaciones y el mínimo exigido es 1000"

serie_precio = precios["precio_cobre_usd_lb"]                 # serie diaria del precio del cobre en US$ por libra

# Los escenarios de precio se construyen con los percentiles de la propia serie histórica, igual que los del CAPEX.
# Son posiciones dentro de la distribución observada 2010-2025, no pronósticos del precio futuro.
PRECIO_ESCENARIOS = {
    "P25 (precio bajo)": round(serie_precio.quantile(0.25), 4),    # un 25 % de los días tuvo un precio igual o menor
    "P50 (precio central)": round(serie_precio.quantile(0.50), 4), # mediana: el valor que parte la serie en dos mitades
    "P75 (precio alto)": round(serie_precio.quantile(0.75), 4),    # un 75 % de los días tuvo un precio igual o menor
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


def construir_flujos(precio_usd_lb, capex_millones, ley=LEY_CENTRAL, recuperacion=RECUPERACION_CENTRAL,
                     costo_usd_t=COSTO_OPERATIVO_USD_T, anios=VIDA_UTIL_ANIOS):
    """Devuelve la lista de flujos de caja libres en millones de dólares.
    Posición 0 = año 0 (solo la inversión); las siguientes, los años de operación.
    Los parámetros tienen valor por defecto igual al caso base: se pasan distintos solo
    cuando se quiere medir cuánto cambia el resultado al mover ese supuesto (gráfico de tornado).
    Supuesto: el precio se mantiene constante durante toda la vida del proyecto en cada escenario.
    Si la vida útil cambia, el tratamiento anual de mineral NO cambia: la planta tiene una capacidad
    fija de 80 000 t/día, así que una mina más corta procesa menos mineral en total, no más por año."""
    produccion_mlb = libras_cobre_por_anio(ley, recuperacion)         # millones de libras vendidas cada año
    ingresos = produccion_mlb * precio_usd_lb                          # millones de dólares de ingreso anual
    costos = MINERAL_ANUAL_MT * 1_000_000 * costo_usd_t / 1_000_000    # costo anual en millones de dólares
    depreciacion = capex_millones / anios                              # parte del CAPEX que se descuenta cada año para el impuesto

    flujos = [-capex_millones]                                         # año 0: sale toda la inversión (signo negativo)
    for _ in range(anios):                                             # se repite igual en cada año de operación
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
# 8. PRECIO DE EQUILIBRIO: EL PRECIO DEL COBRE QUE HACE EL VAN IGUAL A CERO
#    Es el umbral por debajo del cual el proyecto deja de ser viable.
# ---------------------------------------------------------------------------

def precio_de_equilibrio(capex_millones, tasa, limite_inferior=0.10, limite_superior=20.0, tolerancia=1e-6):
    """Precio del cobre, en dólares por libra, que hace que el VAN sea exactamente cero.
    Se busca por bisección, igual que la TIR, pero moviendo el precio en lugar de la tasa:
    como a mayor precio mayor VAN, basta con partir el intervalo a la mitad hasta encontrar el cruce por cero."""
    van_inferior = valor_actual_neto(construir_flujos(limite_inferior, capex_millones), tasa)  # VAN con un precio muy bajo (negativo)
    van_superior = valor_actual_neto(construir_flujos(limite_superior, capex_millones), tasa)  # VAN con un precio muy alto (positivo)
    if van_inferior * van_superior > 0:          # si ambos tienen el mismo signo, no hay cruce dentro del intervalo
        return None
    for _ in range(200):                         # 200 repeticiones dan precisión más que suficiente
        punto_medio = (limite_inferior + limite_superior) / 2
        van_medio = valor_actual_neto(construir_flujos(punto_medio, capex_millones), tasa)
        if abs(van_medio) < tolerancia:          # el VAN ya es prácticamente cero: ese es el precio de equilibrio
            return punto_medio
        if van_inferior * van_medio < 0:         # el cruce está en la mitad izquierda del intervalo
            limite_superior = punto_medio
        else:                                    # el cruce está en la mitad derecha
            limite_inferior, van_inferior = punto_medio, van_medio
    return (limite_inferior + limite_superior) / 2

filas_equilibrio = []
for nombre_capex, capex in CAPEX_ESCENARIOS.items():                 # un precio de equilibrio por cada escenario de inversión
    precio_cero = precio_de_equilibrio(capex, TASA_DESCUENTO_CENTRAL)
    # Cuenta cuántos días de la serie histórica 2010-2025 tuvieron un precio por debajo de ese umbral.
    # Es la forma de conectar la volatilidad observada del cobre con el riesgo concreto del proyecto.
    dias_debajo = int((serie_precio < precio_cero).sum())
    filas_equilibrio.append({
        "escenario_capex": nombre_capex,
        "capex_millones_usd": capex,
        "precio_equilibrio_usd_lb": round(precio_cero, 4),
        "dias_bajo_el_umbral": dias_debajo,
        "total_dias": len(serie_precio),
        "porcentaje_dias_bajo_el_umbral": round(100 * dias_debajo / len(serie_precio), 1),
    })
tabla_equilibrio = pd.DataFrame(filas_equilibrio)
tabla_equilibrio.to_csv(os.path.join(CARPETA_SALIDAS, "precio_equilibrio_2024200537D.csv"), index=False, encoding="utf-8")
# ---------------------------------------------------------------------------
# 9. FIGURAS DEL ARTÍCULO
#    Se generan desde este mismo script para que el artículo, el póster y el dashboard
#    muestren exactamente los mismos números que las tablas.
# ---------------------------------------------------------------------------
import matplotlib                    # biblioteca de gráficos de Python
matplotlib.use("Agg")                # dibuja en archivo y no necesita pantalla: funciona en Colab
import matplotlib.pyplot as plt
import matplotlib.dates as mdates    # para escribir años en el eje de fechas
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch

# Estilo predefinido de matplotlib: fondo blanco con rejilla tenue. Una sola línea
# define tipografía, colores, grosores y rejilla; no hace falta configurarlos uno por uno.
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams["savefig.dpi"] = 300    # resolución alta, para que las figuras se vean nítidas impresas

# Colores que trae ese estilo, en su orden. Se toman de ahí en lugar de inventarlos,
# así todas las figuras usan la misma secuencia de colores.
PALETA = plt.rcParams["axes.prop_cycle"].by_key()["color"]
AZUL, NARANJA, VERDE, ROJO = PALETA[0], PALETA[1], PALETA[2], PALETA[3]
COLORES = {"bajo": AZUL, "central": NARANJA, "alto": VERDE}

# Nombres en palabras para los escenarios de inversion. Se usan en las figuras en lugar
# de P25, P50 y P75, porque esas siglas ya designan los percentiles del PRECIO y usarlas
# para dos cosas distintas confunde al lector.
NOMBRE_CAPEX = {"P25 (inversión baja)": "Inversión baja",
                "P50 (central)": "Inversión central",
                "P75 (inversión alta)": "Inversión alta"}

def num(x, decimales=0):
    """Da formato a un número con la convención del artículo: espacio fino para los miles
    y PUNTO para los decimales, como en el artículo de la Unidad I y en APA 7.
    Así 1234.56 se escribe 1 234.56. Unifica el formato de las figuras con el del texto."""
    return f"{x:,.{decimales}f}".replace(",", " ")

def formato_del_eje(eje, decimales):
    """Aplica a las marcas de un eje el mismo formato numérico del artículo."""
    eje.set_major_formatter(FuncFormatter(lambda v, _: num(v, decimales)))

nombres_precio = list(PRECIO_ESCENARIOS.keys())
nombres_capex = list(CAPEX_ESCENARIOS.keys())
precio_equilibrio_central = tabla_equilibrio.loc[
    tabla_equilibrio["escenario_capex"] == "P50 (central)", "precio_equilibrio_usd_lb"].iloc[0]

# --- Figura 1: evolución del precio del cobre y umbrales de viabilidad ---
fig, ax = plt.subplots(figsize=(10, 4.8))
piso = max(0, min(precios["precio_cobre_usd_lb"].min(),
                  tabla_equilibrio["precio_equilibrio_usd_lb"].min()) - 0.35)
# Zona sombreada: precios a los que el proyecto con inversión central destruiría valor
ax.axhspan(piso, precio_equilibrio_central, color=ROJO, alpha=0.07)
ax.plot(precios["fecha"], precios["precio_cobre_usd_lb"], linewidth=0.7, color="dimgray")

# Cada umbral lleva su nombre escrito al lado, de modo que se distingan aunque se imprima
# en blanco y negro o quien lo lea sea daltónico.
borde_derecho = precios["fecha"].max() + pd.Timedelta(days=620)
for (_, fila), clave in zip(tabla_equilibrio.iterrows(), ["bajo", "central", "alto"]):
    y = fila["precio_equilibrio_usd_lb"]
    ax.axhline(y, linestyle="--", linewidth=1.4, color=COLORES[clave])
    ax.text(borde_derecho, y, f"  {NOMBRE_CAPEX[fila['escenario_capex']]}: {num(y, 2)}",
            va="center", fontsize=9, color=COLORES[clave])

ax.set_xlim(precios["fecha"].min(), borde_derecho)
ax.set_ylim(bottom=piso)
ax.xaxis.set_major_locator(mdates.YearLocator(2))     # una marca cada dos años
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
formato_del_eje(ax.yaxis, 2)
ax.set_title("Precio diario del cobre y umbrales de viabilidad del proyecto, 2010-2025")
ax.set_ylabel("US$ por libra")
ax.text(precios["fecha"].min() + pd.Timedelta(days=120), piso + 0.07,
        "Zona de VAN negativo con inversión central", fontsize=8.5, color=ROJO)
fig.savefig(os.path.join(CARPETA_SALIDAS, "fig1_precio_umbrales_2024200537D.png"), bbox_inches="tight")
plt.close(fig)

# --- Figura 2: VAN por escenario de precio y de inversión ---
fig, ax = plt.subplots(figsize=(9.5, 5))
ancho = 0.26                                          # ancho de cada barra dentro del grupo
posiciones = list(range(len(nombres_precio)))
for i, (nombre_capex, clave) in enumerate(zip(nombres_capex, ["bajo", "central", "alto"])):
    valores = [tabla_escenarios.query("escenario_precio == @p and escenario_capex == @nombre_capex")
               ["van_millones_usd"].iloc[0] for p in nombres_precio]
    x = [p + (i - 1) * ancho for p in posiciones]     # desplaza cada serie para que no se superpongan
    ax.bar(x, valores, width=ancho, color=COLORES[clave], label=nombre_capex)
    for xi, v in zip(x, valores):                     # la cifra exacta sobre cada barra
        ax.text(xi, v + (28 if v >= 0 else -28), num(v), ha="center",
                va="bottom" if v >= 0 else "top", fontsize=8)

ax.axhline(0, color="gray", linewidth=1)              # el cero separa crear y destruir valor
ax.set_xticks(posiciones)
ax.set_xticklabels([f"{n.split(' ')[0]}  ·  {num(PRECIO_ESCENARIOS[n], 2)} US$/lb" for n in nombres_precio])
formato_del_eje(ax.yaxis, 0)
ax.set_title("VAN según el precio del cobre y el nivel de inversión")
ax.set_xlabel("Escenario de precio del cobre")
ax.set_ylabel("VAN (millones de US$)")
ax.margins(y=0.16)
ax.legend(title="Escenario de inversión (CAPEX)", fontsize=9,
          loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3)
fig.savefig(os.path.join(CARPETA_SALIDAS, "fig2_van_escenarios_2024200537D.png"), bbox_inches="tight")
plt.close(fig)

# --- Figura 3: sensibilidad del VAN a la tasa de descuento ---
fig, ax = plt.subplots(figsize=(8.5, 4.8))
for nombre_precio, clave in zip(nombres_precio, ["bajo", "central", "alto"]):
    sub = tabla_tasa[tabla_tasa["escenario_precio"] == nombre_precio]
    ax.plot(sub["tasa_descuento_porcentaje"], sub["van_millones_usd"],
            marker="o", linewidth=2, color=COLORES[clave])
    ultimo = sub.iloc[-1]                             # nombre al final de la línea, en vez de leyenda
    ax.text(ultimo["tasa_descuento_porcentaje"] + 0.15, ultimo["van_millones_usd"],
            nombre_precio.split(" ")[0], va="center", fontsize=9, color=COLORES[clave])

ax.axhline(0, color="gray", linewidth=1)
ax.axvline(TASA_DESCUENTO_CENTRAL * 100, color="gray", linestyle=":", linewidth=1.2)
ax.annotate(f"Tasa del estudio: {num(TASA_DESCUENTO_CENTRAL*100, 2)} %",
            xy=(TASA_DESCUENTO_CENTRAL * 100, ax.get_ylim()[1]), xytext=(4, -10),
            textcoords="offset points", fontsize=9, color="gray", va="top")
ax.set_xlim(right=max(TASAS_SENSIBILIDAD) * 100 + 0.9)
formato_del_eje(ax.yaxis, 0)
formato_del_eje(ax.xaxis, 2)
ax.set_title("Sensibilidad del VAN a la tasa de descuento (inversión central)")
ax.set_xlabel("Tasa de descuento (%)")
ax.set_ylabel("VAN (millones de US$)")
fig.savefig(os.path.join(CARPETA_SALIDAS, "fig3_sensibilidad_tasa_2024200537D.png"), bbox_inches="tight")
plt.close(fig)

# --- Figura 4: recuperación de la inversión (flujo de caja acumulado descontado) ---
# Qué entra : los flujos del caso base y la tasa de descuento.
# Qué hace  : trae cada flujo a valor presente y los va sumando año a año.
# Qué enseña: tres cosas en un solo gráfico. Dónde empieza el proyecto (la inversión),
#             en qué año deja de estar en rojo (periodo de recuperación descontado) y
#             dónde termina la curva, que es exactamente el VAN. Reemplaza al gráfico de
#             barras anterior, que mostraba diecisiete barras iguales porque el modelo
#             supone producción, precio y costos constantes.
acumulado = []
suma = 0.0
for t_anio, flujo in enumerate(flujos_base):
    suma += flujo / (1 + TASA_DESCUENTO_CENTRAL) ** t_anio   # cada flujo, traído a hoy
    acumulado.append(suma)

# Año en que el acumulado pasa de negativo a positivo. Se interpola dentro del año
# para dar el momento exacto en lugar de redondear al año siguiente.
anio_recuperacion = None
for t_anio in range(1, len(acumulado)):
    if acumulado[t_anio - 1] < 0 <= acumulado[t_anio]:
        fraccion = -acumulado[t_anio - 1] / (acumulado[t_anio] - acumulado[t_anio - 1])
        anio_recuperacion = (t_anio - 1) + fraccion
        break

anios = list(range(len(acumulado)))
fig, ax = plt.subplots(figsize=(9.5, 4.6))
ax.axhline(0, color="gray", linewidth=1)
# El área sombreada distingue de un vistazo la etapa en que el proyecto aún no se paga
ax.fill_between(anios, acumulado, 0, where=[v < 0 for v in acumulado],
                color=ROJO, alpha=0.10, interpolate=True)
ax.fill_between(anios, acumulado, 0, where=[v >= 0 for v in acumulado],
                color=AZUL, alpha=0.10, interpolate=True)
ax.plot(anios, acumulado, marker="o", markersize=4.5, linewidth=2, color=AZUL)

if anio_recuperacion is not None:
    ax.axvline(anio_recuperacion, color=VERDE, linestyle=":", linewidth=1.6)
    ax.text(anio_recuperacion + 0.2, min(acumulado) * 0.62,
            f"Inversión recuperada\nen el año {num(anio_recuperacion, 1)}",
            fontsize=9, color=VERDE)

# Las dos cifras que el lector necesita: de dónde parte y a dónde llega
ax.text(0, acumulado[0], f" {num(acumulado[0])}", va="center", ha="left", fontsize=9, color=ROJO)
ax.text(anios[-1] + 0.25, acumulado[-1], f"VAN = {num(acumulado[-1])}",
        va="center", fontsize=9, color=AZUL)

ax.set_xticks(anios)
ax.set_xlim(-0.6, anios[-1] + 3.2)
ax.margins(y=0.10)                 # aire arriba y abajo, para que las cifras no toquen el borde
formato_del_eje(ax.yaxis, 0)
ax.set_title(f"Recuperación de la inversión: {num(precio_base, 2)} US$/lb y CAPEX de {num(capex_base)} millones")
ax.set_xlabel("Año del proyecto (0 = inversión inicial)")
ax.set_ylabel("Flujo acumulado descontado (millones de US$)")
fig.savefig(os.path.join(CARPETA_SALIDAS, "fig4_recuperacion_inversion_2024200537D.png"), bbox_inches="tight")
plt.close(fig)

# --- Figura 5: con qué frecuencia el precio estuvo por debajo de cada umbral ---
# Qué entra : la serie diaria de precios y los tres precios de equilibrio.
# Qué hace  : ordena los 3 974 días de menor a mayor precio y, para cada precio,
#             calcula qué porcentaje de días quedó en ese nivel o por debajo.
# Qué enseña: se lee directamente el riesgo. Sobre cada umbral de viabilidad se lee el
#             porcentaje de días en que el proyecto habría tenido VAN negativo.
#             Reemplaza al histograma, que repetía información de la figura 1 y usaba
#             las etiquetas P25/P50/P75 con un significado distinto.
serie_ordenada = serie_precio.sort_values().reset_index(drop=True)
frecuencia_acumulada = [(i + 1) / len(serie_ordenada) * 100 for i in range(len(serie_ordenada))]

fig, ax = plt.subplots(figsize=(9.5, 4.8))
ax.plot(serie_ordenada, frecuencia_acumulada, linewidth=2, color="dimgray")

limite_izquierdo = min(serie_ordenada.min(), tabla_equilibrio["precio_equilibrio_usd_lb"].min()) - 0.12
for (_, fila), clave in zip(tabla_equilibrio.iterrows(), ["bajo", "central", "alto"]):
    x = fila["precio_equilibrio_usd_lb"]
    y = fila["porcentaje_dias_bajo_el_umbral"]
    color = COLORES[clave]
    # Dos tramos punteados que llevan la vista del umbral al porcentaje que le corresponde
    ax.plot([x, x], [0, y], linestyle="--", linewidth=1.3, color=color)
    ax.plot([limite_izquierdo, x], [y, y], linestyle="--", linewidth=1.3, color=color)
    ax.plot([x], [y], marker="o", markersize=8, color=color)
    # Si el umbral cae en el tercio derecho del gráfico, la etiqueta se escribe hacia la
    # izquierda para que no se salga del área del dibujo.
    a_la_derecha = x > limite_izquierdo + 0.66 * (serie_ordenada.max() - limite_izquierdo)
    ax.annotate(f"{NOMBRE_CAPEX[fila['escenario_capex']]}\n"
                f"umbral {num(x, 2)} US$/lb · {num(y, 1)} % de los días",
                xy=(x, y), xytext=(-10 if a_la_derecha else 10, 14),
                textcoords="offset points",
                ha="right" if a_la_derecha else "left",
                fontsize=9, color=color)

formato_del_eje(ax.xaxis, 2)
formato_del_eje(ax.yaxis, 0)
ax.set_xlim(limite_izquierdo, serie_ordenada.max() + 0.12)
ax.set_ylim(0, 104)
ax.set_title("Porcentaje de días en que el precio del cobre estuvo por debajo de cada umbral, 2010-2025")
ax.set_xlabel("Precio del cobre (US$ por libra)")
ax.set_ylabel("Días acumulados (%)")
fig.savefig(os.path.join(CARPETA_SALIDAS, "fig5_frecuencia_acumulada_2024200537D.png"), bbox_inches="tight")
plt.close(fig)

# --- Figura 6: gráfico de tornado, sensibilidad del VAN a cada supuesto ---
# Mueve un supuesto por vez a los extremos de su rango y deja los demás en el caso base.
# Los rangos provienen de las fuentes documentadas del estudio; la única excepción es el
# costo operativo, cuyo rango es un supuesto propio y así se indica en su etiqueta.
van_base = valor_actual_neto(flujos_base, TASA_DESCUENTO_CENTRAL)

def van_con(**cambios):
    """Calcula el VAN cambiando un solo supuesto respecto del caso base."""
    tasa = cambios.pop("tasa", TASA_DESCUENTO_CENTRAL)
    flujos = construir_flujos(cambios.pop("precio", precio_base),
                              cambios.pop("capex", capex_base), **cambios)
    return valor_actual_neto(flujos, tasa)

# Cada supuesto se declara UNA SOLA VEZ, en esta tabla. La etiqueta de la figura se
# construye a partir de los mismos números que se le pasan al modelo, de modo que es
# imposible que el texto del gráfico diga algo distinto de lo que se calculó. Antes los
# rangos estaban escritos a mano en la etiqueta: si alguien cambiaba una constante y
# olvidaba editar el texto, la figura habría mostrado un rango falso.
#
# Columnas: nombre visible | parámetro de construir_flujos | valor en el extremo que BAJA
# el VAN | valor en el extremo que lo SUBE | unidad de la etiqueta | factor para mostrar
# (100 convierte una proporción en porcentaje) | decimales de la etiqueta.
RANGOS_TORNADO = [
    ("Precio del cobre", "precio",
     PRECIO_ESCENARIOS["P25 (precio bajo)"], PRECIO_ESCENARIOS["P75 (precio alto)"],
     "US$/lb", 1, 2),
    ("Inversión (CAPEX)", "capex",
     CAPEX_ESCENARIOS["P75 (inversión alta)"], CAPEX_ESCENARIOS["P25 (inversión baja)"],
     "millones US$", 1, 0),
    ("Ley del mineral", "ley",
     0.0027, 0.0056, "% Cu", 100, 2),
    ("Recuperación metalúrgica", "recuperacion",
     0.60, 0.90, "%", 100, 0),
    ("Vida útil de la mina", "anios",
     12, 19, "años", 1, 0),
    ("Tasa de descuento", "tasa",
     0.14, 0.0820, "%", 100, 2),
    # Único rango que es supuesto propio: ±20 % sobre el costo verificado en el PEA.
    ("Costo operativo (rango supuesto)", "costo_usd_t",
     COSTO_OPERATIVO_USD_T * 1.2, COSTO_OPERATIVO_USD_T * 0.8, "US$/t", 1, 2),
]

supuestos = []
for nombre, parametro, desfavorable, favorable, unidad, escala, decimales in RANGOS_TORNADO:
    # El rango se escribe siempre de menor a mayor, aunque el extremo desfavorable sea el
    # mayor (como ocurre con el CAPEX, la tasa de descuento y el costo operativo).
    menor, mayor = sorted([desfavorable * escala, favorable * escala])
    etiqueta = f"{nombre}\n{num(menor, decimales)} – {num(mayor, decimales)} {unidad}"
    supuestos.append((etiqueta,
                      van_con(**{parametro: desfavorable}),
                      van_con(**{parametro: favorable})))

supuestos.sort(key=lambda s: abs(s[2] - s[1]))        # el supuesto más influyente queda arriba

fig, ax = plt.subplots(figsize=(9.5, 5.4))
for i, (etiqueta, van_bajo, van_alto) in enumerate(supuestos):
    ax.barh(i, van_bajo - van_base, left=van_base, height=0.6, color=AZUL)
    ax.barh(i, van_alto - van_base, left=van_base, height=0.6, color=NARANJA)
    ax.text(van_bajo, i, f"{num(van_bajo)}  ", va="center", ha="right", fontsize=8)
    ax.text(van_alto, i, f"  {num(van_alto)}", va="center", ha="left", fontsize=8)

ax.axvline(van_base, color="gray", linewidth=1.2)     # línea del caso base
ax.set_yticks(range(len(supuestos)))
ax.set_yticklabels([s[0] for s in supuestos], fontsize=9)
formato_del_eje(ax.xaxis, 0)
ax.set_title("¿Qué supuesto mueve más el resultado? Sensibilidad del VAN")
ax.set_xlabel(f"VAN (millones de US$). Caso base = {num(van_base)}")
ax.margins(x=0.13)
ax.legend(handles=[Patch(facecolor=AZUL, label="Extremo desfavorable del rango"),
                   Patch(facecolor=NARANJA, label="Extremo favorable del rango")],
          fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2)
fig.savefig(os.path.join(CARPETA_SALIDAS, "fig6_tornado_2024200537D.png"), bbox_inches="tight")
plt.close(fig)

print("\nFiguras generadas en la carpeta salidas:")
for nombre in sorted(f for f in os.listdir(CARPETA_SALIDAS) if f.endswith(".png")):
    print("  ", nombre)

# ---------------------------------------------------------------------------
# 10. RESUMEN EN PANTALLA Y BITÁCORA
# ---------------------------------------------------------------------------
print("Producción anual de cobre (millones de libras):", round(libras_cobre_por_anio(LEY_CENTRAL, RECUPERACION_CENTRAL), 1))
print("Escenarios de precio (US$/lb):", PRECIO_ESCENARIOS)
print("\nCaso base (precio y CAPEX centrales):")
print("  VAN (millones US$):", round(valor_actual_neto(flujos_base, TASA_DESCUENTO_CENTRAL), 2))
tir_base = tasa_interna_retorno(flujos_base)
print("  TIR (%):", round(tir_base * 100, 2) if tir_base is not None else "no existe")
# Periodo de recuperacion descontado: tercer indicador, calculado en la figura 4.
# Es el momento en que el flujo acumulado descontado pasa de negativo a positivo.
print("  Periodo de recuperacion descontado (anios):",
      round(anio_recuperacion, 2) if anio_recuperacion is not None else "no se recupera")
print("\nMatriz de escenarios:")
print(tabla_escenarios.to_string(index=False))
print("\nPrecio de equilibrio (el VAN se hace cero) y días históricos por debajo de ese umbral:")
print(tabla_equilibrio.to_string(index=False))

# Los tres indicadores del caso base se guardan tambien en un CSV, para que el articulo,
# el Beamer, el poster y el dashboard tomen las cifras de un archivo y no de la pantalla.
pd.DataFrame([{
    "precio_usd_lb": precio_base,
    "capex_millones_usd": capex_base,
    "tasa_descuento": TASA_DESCUENTO_CENTRAL,
    "van_millones_usd": round(valor_actual_neto(flujos_base, TASA_DESCUENTO_CENTRAL), 2),
    "tir_porcentaje": round(tir_base * 100, 2) if tir_base is not None else None,
    "recuperacion_descontada_anios": round(anio_recuperacion, 2) if anio_recuperacion is not None else None,
}]).to_csv(os.path.join(CARPETA_SALIDAS, "indicadores_caso_base_2024200537D.csv"),
           index=False, encoding="utf-8")

with open(ARCHIVO_LOG, "a", encoding="utf-8") as log:
    log.write(f"Analisis VAN-TIR | {len(tabla_escenarios)} escenarios | salidas/resultados_van_tir_2024200537D.csv\n")
