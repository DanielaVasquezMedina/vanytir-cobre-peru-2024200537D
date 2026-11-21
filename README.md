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
| 1 (API) | BCRP, series PD04701XD, PD04637PD y PD04638PD | Cobre Londres (cUS$/lb), tipo de cambio interbancario compra y venta (S/ por US$), frecuencia diaria | codigo/01_extraccion_api.py |
| 2 (descarga programática) | MINEM, Excel de Anexos del BEM Diciembre 2025 | Producción nacional de cobre (TMF) y cartera CPIM (CAPEX, US$ millones) | codigo/02_scraping_web.py |

Ventana de extracción: 1 de enero de 2010 a 31 de diciembre de 2025.
Base procesada: **3 974 observaciones diarias** y 12 columnas, de las cuales 7 son variables sustantivas.
El mínimo exigido por el numeral 2.4.1 es de 1 000 observaciones, 6 columnas y 4 variables sustantivas.

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
- Escenarios de precio (percentiles de la serie diaria): 2,7997 / 3,3137 / 3,9984 US$/lb.
- Caso base (precio y CAPEX centrales): **VAN de 578,36 millones US$** y **TIR de 16,47 %**.
- Precio de equilibrio con CAPEX central: **2,6975 US$/lb**. El precio estuvo por debajo en **821 de los 3 974 días (20,7 %)**.
- Con CAPEX alto el umbral sube a 3,4616 US$/lb y el 55,9 % de los días quedó por debajo.

## Orden de ejecución
1. codigo/01_extraccion_api.py: descarga las tres series diarias del BCRP en 16 tramos anuales, con pausa de 1 segundo entre solicitudes, y guarda el crudo sin modificar.
2. codigo/02_scraping_web.py: descarga programática del Excel del MINEM y cálculo de su SHA-256.
3. codigo/03_limpieza_datos.py: limpieza, variables derivadas, unión de las dos fuentes por la llave anio y verificación cruzada.
4. codigo/04_analisis.py: VAN, TIR, escenarios, sensibilidad a la tasa y precio de equilibrio.

## Reproducción
Instalar las dependencias y ejecutar los scripts en orden desde la raíz del repositorio:

    pip install -r requirements.txt

## Integridad de los archivos (SHA-256)
| Archivo | Huella |
|---|---|
| datos_procesados/datos_procesados_2024200537D.csv | 3d68a8756f9c623b892122f6a6b055bb266f3f698fd3458641a20368fb1bde69 |
| datos_crudos/bcrp/bcrp_api_respuesta_cruda.json | 24b67cd0622f139a17298ee5985a26a4cdc02096dea35fa355d06c9c9ff5304d |
| datos_crudos/minem/bem_anexos_dic2025.xlsx | 006bcae004c7f12532c778d7d953020b238bba9e3ecb6df87d5c85f130753684 |

## Limitaciones declaradas
- El proyecto evaluado es un caso tipo construido con parámetros de proyectos reales, no un proyecto existente.
- Los ingresos consideran únicamente cobre; no se incluyen oro ni plata.
- El CAPEX proviene de la cartera del MINEM (2025) y los costos operativos del PEA de 2015: no se ajustaron por inflación.
- La depreciación es lineal a 17 años, un supuesto económico simplificado, no la depreciación tributaria peruana por tipo de activo.
- No se modelan regalía minera, impuesto especial a la minería ni gravamen especial a la minería.
- No se modelan capital de trabajo, inversiones de sostenimiento ni costos de cierre de mina.
- El precio se mantiene constante en cada escenario durante los 17 años del proyecto.

## Herramientas de apoyo
En la elaboración de este proyecto se utilizó asistencia de inteligencia artificial (Claude) para la redacción y
documentación del código, la verificación de fuentes y la discusión metodológica. Todas las decisiones metodológicas,
la validación de fuentes y la interpretación de resultados fueron realizadas y son sustentadas por la autora.

## Registro
Cada ejecución agrega una línea a log_ejecucion.txt.
