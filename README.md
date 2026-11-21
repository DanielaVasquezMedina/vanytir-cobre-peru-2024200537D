# VAN y TIR de un proyecto minero frente a la volatilidad del precio del cobre

- **Autora:** Daniela Andrea Vásquez Medina
- **Código de matrícula:** 2024200537D
- **Curso:** Finanzas I (055D), Escuela Profesional de Economía, UNCP
- **Tema:** 50, Unidad II

## Estado del proyecto
En desarrollo. Fuentes verificadas: BCRP (API) y MINEM (descarga programática). Pendientes: ley del mineral, costo unitario, tasa de impuesto y WACC.

## Fuentes
| Vía | Fuente | Variables | Script |
|---|---|---|---|
| 1 (API) | BCRP, series PN38784BM y PN01207PM | Precio del cobre (¢US$/lb, precio de exportación), tipo de cambio interbancario promedio (S/ por US$) | codigo/01_extraccion_api.py |
| 2 (descarga programática) | MINEM, Excel de Anexos del BEM Diciembre 2025 | Producción de cobre (TMF), cartera CPIM (CAPEX, US$ millones) | codigo/02_scraping_web.py |

Ventana de extracción: enero de 2010 a diciembre de 2025.

## Orden de ejecución
1. `codigo/01_extraccion_api.py`: descarga la API del BCRP y guarda el crudo sin modificar.
2. `codigo/02_scraping_web.py`: descarga el Excel del MINEM y calcula su SHA-256.
3. `codigo/03_limpieza_datos.py`: genera la tabla procesada y la verificación cruzada.

## Reproducción
```
pip install -r requirements.txt
```
Ejecutar los scripts en orden desde la raíz del repositorio. Los archivos de `datos_crudos/` se generan al ejecutar los scripts 01 y 02.

## Registro
Cada ejecución agrega una línea a `log_ejecucion.txt`.
