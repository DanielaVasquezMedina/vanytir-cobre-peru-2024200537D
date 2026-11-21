# VAN y TIR de un proyecto minero frente a la volatilidad del precio del cobre

- **Autora:** Daniela Andrea Vásquez Medina
- **Código de matrícula:** 2024200537D
- **Curso:** Finanzas I (055D), Escuela Profesional de Economía, UNCP
- **Tema:** 50, Unidad II

## Objetivo
Evaluar la viabilidad financiera de un proyecto minero de cobre tipo en el Perú mediante el VAN y la TIR,
y medir su sensibilidad frente a la volatilidad histórica del precio del cobre entre 2010 y 2025.

## Fuentes de datos
| Vía | Fuente | Variables | Script |
|---|---|---|---|
| 1 (API) | BCRP, series PN38784BM y PN01207PM | Precio del cobre (¢US$/lb, precio de exportación), tipo de cambio interbancario promedio (S/ por US$) | codigo/01_extraccion_api.py |
| 2 (descarga programática) | MINEM, Excel de Anexos del BEM Diciembre 2025 | Producción de cobre (TMF), cartera CPIM (CAPEX, US$ millones) | codigo/02_scraping_web.py |

Ventana de extracción: enero de 2010 a diciembre de 2025 (192 observaciones mensuales).

## Parámetros del modelo y su fuente
| Parámetro | Valor | Fuente |
|---|---|---|
| Capacidad de planta | 80 000 t/día; 483 Mt en total | PEA actualizado de Cotabambas, comunicado de Panoro del 22-09-2015 |
| Vida útil | 17 años | PEA actualizado de Cotabambas |
| Ley de alimentación | 0,318 % Cu | Cálculo propio, promedio ponderado del PEA |
| Recuperación metalúrgica | 84 % | Informe NI 43-101 de La Granja, Tabla 13-1 (pórfido fresco) |
| Costo operativo | 8,38 US$/t procesada | PEA actualizado de Cotabambas |
| CAPEX (P25 / P50 / P75) | 573,4 / 1 388,0 / 2 220,1 millones US$ | Cartera CPIM del MINEM, muestra de 24 proyectos nuevos de cobre |
| Impuesto a la renta | 29,50 % | Artículo 55 del TUO de la Ley del Impuesto a la Renta |
| Tasa de descuento | 10,13 % | Cálculo propio: WACC de Metals and Mining de Damodaran ajustado por riesgo país de Perú |

## Resultados principales
- Producción anual estimada: 167,3 millones de libras de cobre.
- Caso base (precio y CAPEX centrales): **VAN de 608,68 millones US$** y **TIR de 16,78 %**.
- Precio de equilibrio con CAPEX central: **2,6975 US$/lb**. El precio del cobre estuvo por debajo de ese umbral en **53 de los 192 meses (27,6 %)** del periodo analizado.

## Orden de ejecución
1. codigo/01_extraccion_api.py: descarga la API del BCRP y guarda el crudo sin modificar.
2. codigo/02_scraping_web.py: descarga el Excel del MINEM y calcula su SHA-256.
3. codigo/03_limpieza_datos.py: genera la tabla procesada y la verificación cruzada con el MINEM.
4. codigo/04_analisis.py: calcula VAN, TIR, escenarios, sensibilidad y precio de equilibrio.

## Reproducción
Instalar las dependencias y ejecutar los scripts en orden desde la raíz del repositorio:

    pip install -r requirements.txt

## Integridad de los archivos (SHA-256)
| Archivo | Huella |
|---|---|
| datos_procesados/bcrp_mensual_2024200537D.csv | d61f284d788a68b7dc19ff5b3dd93a0fe1ff14eb60499005cf58ff694433a573 |
| datos_crudos/minem/bem_anexos_dic2025.xlsx | 006bcae004c7f12532c778d7d953020b238bba9e3ecb6df87d5c85f130753684 |

## Limitaciones declaradas
- El proyecto evaluado es un caso tipo construido con parámetros de proyectos reales, no un proyecto existente.
- Los ingresos consideran únicamente cobre; no se incluyen oro ni plata.
- El CAPEX proviene de la cartera del MINEM (2025) y los costos operativos del PEA de 2015: no se ajustaron por inflación.
- La depreciación es lineal a 17 años, un supuesto económico simplificado, no la depreciación tributaria peruana por tipo de activo.
- No se modelan regalía minera, impuesto especial a la minería ni gravamen especial a la minería.
- No se modelan capital de trabajo, inversiones de sostenimiento ni costos de cierre de mina.

## Herramientas de apoyo
En la elaboración de este proyecto se utilizó asistencia de inteligencia artificial (Claude) para la redacción y
documentación del código, la verificación de fuentes y la discusión metodológica. Todas las decisiones metodológicas,
la validación de fuentes y la interpretación de resultados fueron realizadas y son sustentadas por la autora.

## Registro
Cada ejecución agrega una línea a log_ejecucion.txt.
