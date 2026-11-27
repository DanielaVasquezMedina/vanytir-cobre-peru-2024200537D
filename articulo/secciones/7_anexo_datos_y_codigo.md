# 7. Anexo de datos y código

Este anexo reúne la información necesaria para reproducir íntegramente los resultados del
artículo. Todos los archivos mencionados están disponibles en el repositorio público del
proyecto.

## 7.1 Repositorio

**https://github.com/DanielaVasquezMedina/vanytir-cobre-peru-2024200537D**

El repositorio contiene los cuatro scripts de extracción y análisis, los datos crudos tal
como salieron de cada fuente, los datos procesados, las figuras y tablas generadas, el
diccionario de variables, la bitácora de ejecución y el archivo de dependencias.

## 7.2 Fuentes y puntos de acceso

| Vía | Fuente | Punto de acceso (endpoint) | Variables obtenidas |
|---|---|---|---|
| Interfaz de programación | Banco Central de Reserva del Perú, servicio de series estadísticas | `https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{series}/json/{desde}/{hasta}/esp` | Series PD04701XD (cobre, mercado de Londres, cUS$/lb), PD04637PD y PD04638PD (tipo de cambio interbancario de compra y de venta, S/ por US$), frecuencia diaria |
| Descarga programática | Ministerio de Energía y Minas, Excel de anexos del Boletín Estadístico Minero de diciembre de 2025 | `https://cdn.www.gob.pe/uploads/document/file/9503677/7779621-bem-diciembre-2025-excel-de-anexos.xlsx` | Producción nacional de cobre en toneladas métricas finas y cartera de proyectos de inversión minera (CAPEX, millones de US$) |

Ninguna de las dos fuentes exige credenciales de acceso.

## 7.3 Periodo y fecha de corte

La ventana de consulta está declarada en el código como dos constantes, no como fechas
dinámicas:

```
FECHA_INICIO = 2010-01-01
FECHA_CORTE  = 2025-12-31
```

La descarga del archivo del Ministerio de Energía y Minas quedó registrada en la bitácora
el 21 de noviembre de 2026 a las 03:34, y la reejecución verificada del script de
extracción de la interfaz del Banco Central, el 27 de noviembre de 2026 a las 03:56. Las
horas de la bitácora corresponden a la zona horaria del entorno de ejecución, y se
registran con su desplazamiento explícito para evitar ambigüedad. Esa reejecución devolvió
un archivo idéntico byte por byte al de la extracción previa, lo que acredita que la fuente
no revisó la serie entre ambas fechas. La base procesada comprende 3 974 días hábiles, del
4 de enero de 2010 al 31 de diciembre de 2025.

## 7.4 Diccionario de variables

El archivo `diccionario_variables.md` del repositorio describe las 12 columnas del archivo
procesado, indicando para cada una su definición, unidad de medida, frecuencia, tipo,
fuente y punto de acceso de origen. De las 12 columnas, 7 son variables sustantivas y al
menos una proviene de cada fuente. La llave común de integración entre ambas fuentes es el
año.

## 7.5 Orden de ejecución

| Archivo | Función |
|---|---|
| `codigo/01_extraccion_api.py` | Descarga las tres series diarias del BCRP en dieciséis tramos anuales y guarda el crudo en formato JSON y en formato tabular |
| `codigo/02_scraping_web.py` | Descarga programática del Excel del Ministerio de Energía y Minas y cálculo de su huella digital |
| `codigo/03_limpieza_datos.py` | Depuración, tipificación, unión de las fuentes por el año y generación del archivo procesado |
| `codigo/04_analisis.py` | Cálculo de los indicadores, los escenarios y el análisis de sensibilidad; generación de las figuras y las tablas |

Los scripts se ejecutan en ese orden, con rutas relativas a la carpeta del proyecto. El
entorno empleado fue Python 3.13.18 con las versiones de librerías declaradas en
`requirements.txt`: requests 2.32.4, pandas 2.2.3, matplotlib 3.10.0 y openpyxl 3.1.5.

## 7.6 Huellas de verificación

Las huellas digitales SHA-256 permiten comprobar que los archivos entregados son
exactamente los que produjo el código:

| Archivo | Huella SHA-256 |
|---|---|
| `datos_crudos/bcrp/bcrp_api_respuesta_cruda.json` | `24b67cd0622f139a17298ee5985a26a4cdc02096dea35fa355d06c9c9ff5304d` |
| `datos_crudos/datos_crudos_2024200537D.csv` | `20abd4384ec470d3ad37b55b2ef5139b582b8d0586701d4cde491d658856a356` |
| `datos_crudos/minem/bem_anexos_dic2025.xlsx` | `006bcae004c7f12532c778d7d953020b238bba9e3ecb6df87d5c85f130753684` |
| `datos_procesados/datos_procesados_2024200537D.csv` | `3d68a8756f9c623b892122f6a6b055bb266f3f698fd3458641a20368fb1bde69` |

## 7.7 Parámetros del proyecto modelado y sus fuentes

| Parámetro | Valor | Fuente |
|---|---|---|
| Capacidad de planta | 80 000 t/día; 483 Mt de mineral en total | Evaluación económica preliminar actualizada de Cotabambas |
| Vida útil | 17 años | Evaluación económica preliminar actualizada de Cotabambas |
| Ley de alimentación | 0.318 % de cobre | Cálculo propio, promedio ponderado de la evaluación preliminar |
| Recuperación metalúrgica | 84 % | Informe técnico NI 43-101 del proyecto La Granja, Tabla 13-1 (pórfido fresco) |
| Costo operativo | 8.38 US$ por tonelada procesada | Evaluación preliminar de Cotabambas (mina 3.59, procesamiento 4.38, administración 0.41) |
| Inversión (P25 / P50 / P75) | 573.4 / 1 388.0 / 2 220.1 millones de US$ | Cartera de proyectos del Ministerio de Energía y Minas, muestra de 24 proyectos nuevos de cobre |
| Impuesto a la renta | 29.50 % | Artículo 55 del Texto Único Ordenado de la Ley del Impuesto a la Renta |
| Tasa de descuento | 10.13 % | Cálculo propio: costo promedio ponderado de capital del sector Metals and Mining, ajustado por el riesgo país del Perú |
