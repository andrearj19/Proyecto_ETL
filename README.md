# Uso de internet en Ecuador, 2016–2025

Proyecto bimestral de Inteligencia de Negocios de la Universidad Técnica Particular de Loja.

**Pregunta:** ¿Qué porcentaje de la población ecuatoriana usó internet cada año y a cuántas personas equivale aproximadamente?

## Fuentes abiertas

Ambas series fueron publicadas en World Development Indicators (Banco Mundial), con licencia CC BY 4.0. Las copias JSON conservan los registros devueltos por la API para Ecuador entre 2016 y 2025.

| Archivo | Indicador | Fuente |
| --- | --- | --- |
| `datos_fuente/poblacion_total.json` | SP.POP.TOTL, habitantes | [Ficha del indicador](https://data.worldbank.org/indicator/SP.POP.TOTL?locations=EC) · [Datos JSON](https://api.worldbank.org/v2/country/ECU/indicator/SP.POP.TOTL?date=2016:2025&format=json&per_page=100) |
| `datos_fuente/uso_internet.json` | IT.NET.USER.ZS, porcentaje de población (UIT) | [Ficha del indicador](https://data.worldbank.org/indicator/IT.NET.USER.ZS?locations=EC) · [Datos JSON](https://api.worldbank.org/v2/country/ECU/indicator/IT.NET.USER.ZS?date=2016:2025&format=json&per_page=100) |

## Ejecutar el ETL

Desde la carpeta del proyecto, ejecuta con Python 3. No requiere paquetes externos ni conexión.

```bash
python scripts_etl/integrar.py
```

El programa escribe `datos_resultantes/conectividad_ecuador.csv` y `evidencias/validacion.json`. El CSV contiene una fila por país y año. Las celdas vacías representan datos sin valor publicado. La estimación en personas es población × porcentaje / 100, redondeada al entero más cercano.

La evidencia registra claves, duplicados, valores nulos y huellas SHA-256 de los JSON de entrada. Para repetir la carga con una publicación posterior, conserva primero una copia de la versión previa y documenta la fecha de actualización.
