# Diccionario de variables

Archivo descrito: datos_procesados/datos_procesados_2024200537D.csv
Observaciones: 3 974 días hábiles, del 4 de enero de 2010 al 31 de diciembre de 2025
Llave común entre fuentes: anio

| Variable | Definición | Unidad | Frecuencia | Tipo | Fuente | URL o endpoint |
|---|---|---|---|---|---|---|
| fecha | Día hábil al que corresponde la observación | Fecha | Diaria | Identificador | BCRP | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04701XD-PD04637PD-PD04638PD/json/2010-01-01/2025-12-31/esp |
| anio | Año de la observación; llave de unión con la fuente anual del MINEM | Año | Diaria | Identificador | Derivada de fecha | No aplica |
| precio_cobre_cent_usd_lb | Cotización internacional del cobre en Londres, serie PD04701XD, fuente Reuters | Centavos de US$ por libra | Diaria | Numérica | BCRP, serie PD04701XD | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04701XD-PD04637PD-PD04638PD/json/2010-01-01/2025-12-31/esp |
| precio_cobre_usd_lb | Precio del cobre convertido a dólares por libra, dividiendo entre 100 | US$ por libra | Diaria | Numérica | Derivada de PD04701XD | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04701XD-PD04637PD-PD04638PD/json/2010-01-01/2025-12-31/esp |
| tc_interbancario_compra_sol_usd | Tipo de cambio interbancario, precio de compra, serie PD04637PD | Soles por US$ | Diaria | Numérica | BCRP, serie PD04637PD | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04701XD-PD04637PD-PD04638PD/json/2010-01-01/2025-12-31/esp |
| tc_interbancario_venta_sol_usd | Tipo de cambio interbancario, precio de venta, serie PD04638PD | Soles por US$ | Diaria | Numérica | BCRP, serie PD04638PD | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04701XD-PD04637PD-PD04638PD/json/2010-01-01/2025-12-31/esp |
| tc_interbancario_promedio_sol_usd | Promedio simple de compra y venta; el BCRP no publica serie diaria del promedio | Soles por US$ | Diaria | Numérica | Derivada de PD04637PD y PD04638PD | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04701XD-PD04637PD-PD04638PD/json/2010-01-01/2025-12-31/esp |
| precio_cobre_soles_lb | Precio del cobre en moneda nacional: precio en dólares por el tipo de cambio promedio | Soles por libra | Diaria | Numérica | Derivada de las tres series del BCRP | https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04701XD-PD04637PD-PD04638PD/json/2010-01-01/2025-12-31/esp |
| produccion_cobre_peru_tmf | Producción nacional de cobre del año correspondiente, Tabla 01 del BEM | Toneladas métricas finas | Anual, armonizada a diaria | Numérica | MINEM, BEM Diciembre 2025 | https://cdn.www.gob.pe/uploads/document/file/9503677/7779621-bem-diciembre-2025-excel-de-anexos.xlsx?v=1772036174 |
| valor_produccion_cobre_mill_usd | Valor de la producción nacional de cobre: producción convertida a libras por el precio | Millones de US$ | Diaria | Numérica | Integra MINEM y BCRP | Ambas fuentes |
| fuente_bcrp | Trazabilidad de la fuente de las series del BCRP | Texto | Diaria | Texto | Declarada en el script 03 | No aplica |
| fuente_minem | Trazabilidad de la fuente del dato del MINEM | Texto | Diaria | Texto | Declarada en el script 03 | No aplica |

## Notas metodológicas

Armonización de frecuencia. La producción del MINEM se publica por año y las series del BCRP son diarias. A cada día se le asigna la producción total del año al que pertenece. El valor no se reparte entre los días ni se interpola: es un atributo anual del país, y así debe interpretarse en cualquier tabla o figura.

Tratamiento de valores faltantes. Se descargaron 4 174 días y se conservaron 3 974. Los 200 restantes corresponden a días sin cotización completa en las tres series, por feriados que no coinciden entre el mercado de Londres y el peruano. Esos días se eliminan; no se imputan ni se rellenan con valores inventados. El script se detiene con error si hay fechas repetidas, precios no positivos, años fuera de la ventana, menos de 1 000 observaciones o si falta algún año de producción del MINEM.

Promedio del tipo de cambio. El BCRP publica series diarias de compra y de venta, pero no del promedio interbancario. El promedio se calcula como media simple de ambas y se declara como variable derivada.

Conversión de unidades. Una tonelada métrica equivale a 2 204,62 libras. El precio del BCRP se publica en centavos de dólar por libra y se divide entre 100.

Ventana de extracción. Del 1 de enero de 2010 al 31 de diciembre de 2025, declarada como constante FECHA_INICIO y FECHA_CORTE en el script 01.
