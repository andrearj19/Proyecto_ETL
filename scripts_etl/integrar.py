"""Integra indicadores de población y uso de internet en Ecuador."""

import csv
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "datos_fuente"
OUTPUT = ROOT / "datos_resultantes"
EVIDENCE = ROOT / "evidencias"


def extract_series(filename, indicator):
    path = SOURCE / filename
    raw = path.read_bytes()
    metadata, observations = json.loads(raw, parse_float=Decimal)
    if metadata["pages"] != 1 or metadata["total"] != len(observations):
        raise ValueError(f"Extracción incompleta: {filename}")

    series = {}
    duplicates = 0
    for row in observations:
        country = row["countryiso3code"].strip().upper()
        year = int(row["date"])
        if row["indicator"]["id"] != indicator or country != "ECU":
            raise ValueError(f"Indicador o país inesperado en {filename}")
        if not 2016 <= year <= 2025:
            raise ValueError(f"Año fuera del período en {filename}: {year}")

        key = (country, year)
        value = row["value"]
        if key in series:
            if series[key] != value:
                raise ValueError(f"Clave duplicada con valores distintos: {key}")
            duplicates += 1
        series[key] = value

    return series, {
        "archivo": filename,
        "indicador": indicator,
        "fecha_version_fuente": metadata["lastupdated"],
        "sha256": hashlib.sha256(raw).hexdigest(),
        "filas": len(observations),
        "claves_unicas": len(series),
        "duplicados_identicos": duplicates,
        "valores_nulos": sum(value is None for value in series.values()),
    }


def main():
    population, pop_stats = extract_series("poblacion_total.json", "SP.POP.TOTL")
    internet, net_stats = extract_series("uso_internet.json", "IT.NET.USER.ZS")

    expected = {("ECU", year) for year in range(2016, 2026)}
    if population.keys() != expected:
        raise ValueError("La serie de población no cubre todos los años esperados.")

    rows = []
    for country, year in sorted(population):
        key = (country, year)
        total = population[key]
        percentage = internet.get(key)
        if type(total) is not int or total <= 0:
            raise ValueError(f"Población inválida para {year}")
        if percentage is not None and not 0 <= percentage <= 100:
            raise ValueError(f"Porcentaje inválido para {year}")

        if percentage is None:
            estimate = None
            status = "sin_dato" if key in internet else "sin_correspondencia"
        else:
            estimate = int(
                (Decimal(total) * Decimal(percentage) / 100).quantize(
                    Decimal("1"), rounding=ROUND_HALF_UP
                )
            )
            if not 0 <= estimate <= total:
                raise ValueError(f"Estimación inválida para {year}")
            status = "disponible"

        rows.append({
            "codigo_pais": country,
            "anio": year,
            "poblacion_total": total,
            "personas_usuarias_internet_pct": percentage,
            "personas_usuarias_internet_estimadas": estimate,
            "estado_dato_internet": status,
        })

    quality = {
        "fuentes": [pop_stats, net_stats],
        "filas_integradas": len(rows),
        "claves_unicas_integradas": len({(r["codigo_pais"], r["anio"]) for r in rows}),
        "claves_emparejadas": len(population.keys() & internet.keys()),
        "anios_sin_correspondencia_en_internet": sorted(
            year for _, year in population.keys() - internet.keys()
        ),
        "anios_sin_valor_de_internet": [
            r["anio"] for r in rows if r["estado_dato_internet"] == "sin_dato"
        ],
        "estimaciones_calculadas": sum(
            r["personas_usuarias_internet_estimadas"] is not None for r in rows
        ),
        "validacion_rangos": "correcta",
    }

    OUTPUT.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)
    with (OUTPUT / "conectividad_ecuador.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    report = json.dumps(quality, ensure_ascii=False, indent=2)
    (EVIDENCE / "validacion.json").write_text(report + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
