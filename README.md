# VAN y TIR de un proyecto minero frente a la volatilidad del precio del cobre

- **Autora:** Daniela Andrea Vásquez Medina
- **Código de matrícula:** 2024200537D
- **Curso:** Finanzas I (055D), Escuela Profesional de Economía, UNCP
- **Tema:** 50, Unidad II
- **Repositorio:** https://github.com/DanielaVasquezMedina/vanytir-cobre-peru-2024200537D

## Objetivo
Evaluar la viabilidad financiera de un proyecto minero de cobre tipo en el Perú mediante el VAN y la TIR,
y medir su sensibilidad frente a la volatilidad histórica del precio del cobre entre 2010 y 2025.

## Fuentes de datos y endpoints
| Vía | Fuente | Endpoint o URL | Variables | Script |
|---|---|---|---|---|
| 1 (API) | BCRP, estadísticas series | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{series}/json/{desde}/{hasta}/esp | Series PD04701XD (cobre Londres, cUS$/lb), PD04637PD y PD04638PD (tipo de cambio interbancario compra y venta, S/ por US$), frecuencia diaria | codigo/01_extraccion_api.py |
| 2 (descarga programática) | MINEM, Excel de Anexos del BEM Diciembre 2025 | https://cdn.www.gob.pe/uploads/document/file/9503677/7779621-bem-diciembre-2025-excel-de-anexos.xlsx | Producción nacional de cobre (TMF) y cartera CPIM (CAPEX, US$ millones) | codigo/02_scraping_web.py |

Ventana de extracción congelada en los scripts: FECHA_INICIO = 2010-01-01 y FECHA_CORTE = 2025-12-31.
Base procesada: **3 974 observaciones diarias** y 12 columnas, de las cuales 7 son variables sustantivas.
El mínimo exigido por el numeral 2.4.1 es de 1 000 observaciones, 6 columnas y 4 variables sustantivas.

## Claves de API
Ninguna de las dos fuentes exige clave. La API del BCRP es de acceso público y el archivo del MINEM se
descarga desde una URL abierta, por lo que el docente puede ejecutar los scripts sin credenciales propias.
El archivo `.env.example` documenta esa situación y declara las dos variables que sí admite el proyecto,
BCRP_USER_AGENT y MINEM_USER_AGENT, usadas para el User-Agent identificable que exige el numeral 2.4.8.
Si no se definen, los scripts usan un valor por omisión.

## Parámetros del modelo y su fuente
| Parámetro | Valor | Fuente |
|---|---|---|
| Capacidad de planta | 80 000 t/día; 483 Mt en total | PEA actualizado de Cotabambas, comunicado de Panoro del 22-09-2015 |
| Vida útil | 17 años | PEA actualizado de Cotabambas |
| Ley de alimentación | 0.318 % Cu | Cálculo propio, promedio ponderado del PEA |
| Recuperación metalúrgica | 84 % | Informe NI 43-101 de La Granja, Tabla 13-1 (pórfido fresco) |
| Costo operativo | 8.38 US$/t procesada | PEA actualizado de Cotabambas (mina 3.59 + procesamiento 4.38 + G&A 0.41) |
| CAPEX (P25 / P50 / P75) | 573.4 / 1 388.0 / 2 220.1 millones US$ | Cartera CPIM del MINEM, muestra de 24 proyectos nuevos de cobre |
| Impuesto a la renta | 29.50 % | Artículo 55 del TUO de la Ley del Impuesto a la Renta |
| Tasa de descuento | 10.13 % | Cálculo propio: WACC de Metals and Mining de Damodaran ajustado por riesgo país de Perú |

## Resultados principales
- Producción anual estimada: 167.3 millones de libras de cobre recuperado.
- Escenarios de precio (percentiles de la serie diaria): 2.7997 / 3.3137 / 3.9984 US$/lb.
- Caso base: **VAN de 578.36 millones US$**, **TIR de 16.47 %** y **recuperación descontada en 8.73 años**.
- Precio de equilibrio con CAPEX central: **2.6975 US$/lb**. El precio estuvo por debajo en **821 de los 3 974 días (20.7 %)**.
- Con CAPEX alto el umbral sube a 3.4616 US$/lb y el 55.9 % de los días quedó por debajo.

## Orden de ejecución
1. `codigo/01_extraccion_api.py`: descarga las tres series diarias del BCRP en 16 tramos anuales, con pausa de 1 segundo entre solicitudes, y guarda el crudo sin modificar en dos formatos: la respuesta original en JSON y la misma respuesta volcada a tabla en `datos_crudos/datos_crudos_2024200537D.csv`. El CSV no aplica ninguna limpieza: los valores van tal como los entrega la API, incluido el `n.d.` de los días sin cotización. Al final calcula la huella SHA-256 de ambos archivos y la compara con la de la descarga anterior, para detectar si la fuente revisó la serie.
2. `codigo/02_scraping_web.py`: descarga programática del Excel del MINEM y cálculo de su SHA-256.
3. `codigo/03_limpieza_datos.py`: limpieza, variables derivadas, unión de las dos fuentes por la llave `anio` y verificación cruzada con la hoja 5 del MINEM.
4. `codigo/04_analisis.py`: VAN, TIR, recuperación descontada, precio de equilibrio, escenarios, sensibilidad y las seis figuras.

## Entorno de ejecución
- Lenguaje: Python 3.13.18

| Librería | Versión |
|---|---|
| requests | 2.32.4 |
| pandas | 2.2.3 |
| matplotlib | 3.10.0 |
| openpyxl | 3.1.5 |

Reproducción, desde la raíz del repositorio:

    pip install -r requirements.txt

## Salidas que genera el script 04
En `salidas/`: cuatro tablas en CSV (flujos de caja, resultados de VAN y TIR, sensibilidad a la tasa y
precio de equilibrio), más `indicadores_caso_base_2024200537D.csv` con los tres indicadores del caso base,
y seis figuras en PNG. Cinco de esas figuras se usan en el artículo; la de sensibilidad a la tasa se reserva
para el dashboard, porque el gráfico de tornado ya cubre ese análisis en el artículo.

## Integridad de los archivos (SHA-256)
| Archivo | Huella |
|---|---|
| datos_procesados/datos_procesados_2024200537D.csv | 3d68a8756f9c623b892122f6a6b055bb266f3f698fd3458641a20368fb1bde69 |
| datos_crudos/bcrp/bcrp_api_respuesta_cruda.json | 24b67cd0622f139a17298ee5985a26a4cdc02096dea35fa355d06c9c9ff5304d |
| datos_crudos/datos_crudos_2024200537D.csv | 20abd4384ec470d3ad37b55b2ef5139b582b8d0586701d4cde491d658856a356 |
| datos_crudos/minem/bem_anexos_dic2025.xlsx | 006bcae004c7f12532c778d7d953020b238bba9e3ecb6df87d5c85f130753684 |

## Trazabilidad del número de observaciones
El archivo crudo tiene 4 174 filas, una por cada día hábil que devolvió la API entre el 01-01-2010 y el
31-12-2025. De ellas, 200 tienen `n.d.` en al menos una de las tres series: 11 días sin cotización del cobre
y 196 sin tipo de cambio, con 7 días a los que les faltan ambos. Al descartarlas quedan las **3 974
observaciones completas** del archivo procesado. La resta se puede comprobar directamente sobre
`datos_crudos/datos_crudos_2024200537D.csv`.

Una reejecución del script 01 realizada el 22-11-2026 devolvió un archivo JSON idéntico byte por byte al de
la extracción original, de modo que la serie no fue revisada por la fuente entre ambas fechas.

## Limitaciones declaradas
- El proyecto evaluado es un caso tipo construido con parámetros de proyectos reales, no un proyecto existente.
- Los ingresos consideran únicamente cobre; no se incluyen oro ni plata, que el PEA sí contempla.
- La producción es de cobre recuperado, no pagable. El PEA declara un pay factor de 96.3 % a 96.5 %.
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
Cada ejecución agrega una línea a `log_ejecucion.txt` con la fecha, la hora, el código de respuesta HTTP y el
número de filas o bytes obtenidos.
