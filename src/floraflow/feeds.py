"""Real-time data feeds for FloraFlow — weather and soil from Open-Meteo."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from .models import (
    AlertType,
    Municipality,
    Severity,
    WeatherAlert,
)

# --- Greenhouse location coordinates ---

LOCATIONS: dict[Municipality, tuple[float, float]] = {
    Municipality.VILLA_GUERRERO: (18.9614, -99.6353),
    Municipality.TENANCINGO: (18.9603, -99.5904),
    Municipality.COATEPEC_HARINAS: (18.9272, -99.7558),
    Municipality.METEPEC: (19.2550, -99.6040),
    Municipality.TOLUCA: (19.2826, -99.6557),
}

OPEN_METEO_FORECAST = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_SOIL = "https://api.open-meteo.com/v1/forecast"


async def _fetch_weather(lat: float, lng: float) -> dict[str, Any]:
    """Fetch current weather + hourly forecast for a single location."""
    params = {
        "latitude": lat,
        "longitude": lng,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
        "hourly": "temperature_2m,precipitation_probability,precipitation,weather_code",
        "forecast_days": 3,
        "timezone": "America/Mexico_City",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(OPEN_METEO_FORECAST, params=params)
        resp.raise_for_status()
        return resp.json()


def _generate_alerts(municipality: Municipality, data: dict) -> list[WeatherAlert]:
    """Generate weather alerts from forecast data."""
    alerts: list[WeatherAlert] = []
    hourly = data.get("hourly", {})
    temps = hourly.get("temperature_2m", [])
    precip = hourly.get("precipitation", [])
    weather_codes = hourly.get("weather_code", [])
    times = hourly.get("time", [])

    for i, t in enumerate(temps):
        if t is None:
            continue
        ts = times[i] if i < len(times) else ""

        # Frost alert — critical for flowers below 3C
        if t < 3.0:
            sev = Severity.CRITICAL if t < 0 else Severity.HIGH
            alerts.append(WeatherAlert(
                municipality=municipality,
                alert_type=AlertType.FROST,
                severity=sev,
                description=f"Temperatura pronosticada {t}°C — riesgo de helada {'severa' if t < 0 else 'moderada'}. Activar calefaccion y cubrir cultivos.",
                forecast_date=ts,
                affected_greenhouses=[],
            ))

        # Heat alert — above 35C
        if t > 35.0:
            sev = Severity.HIGH if t > 40 else Severity.MEDIUM
            alerts.append(WeatherAlert(
                municipality=municipality,
                alert_type=AlertType.HEAT,
                severity=sev,
                description=f"Temperatura pronosticada {t}°C — estres termico en flores. Aumentar riego y ventilacion.",
                forecast_date=ts,
                affected_greenhouses=[],
            ))

    # Hail detection via weather codes (96, 99 = hail)
    for i, code in enumerate(weather_codes):
        if code in (96, 99):
            ts = times[i] if i < len(times) else ""
            alerts.append(WeatherAlert(
                municipality=municipality,
                alert_type=AlertType.HAIL,
                severity=Severity.CRITICAL,
                description="Pronostico de granizo — proteger invernaderos y cultivos a cielo abierto inmediatamente.",
                forecast_date=ts,
                affected_greenhouses=[],
            ))

    # Heavy rain (precipitation > 10mm/hr)
    for i, p in enumerate(precip):
        if p is not None and p > 10:
            ts = times[i] if i < len(times) else ""
            alerts.append(WeatherAlert(
                municipality=municipality,
                alert_type=AlertType.RAIN,
                severity=Severity.MEDIUM,
                description=f"Precipitacion intensa pronosticada ({p}mm) — riesgo de inundacion en invernaderos bajos.",
                forecast_date=ts,
                affected_greenhouses=[],
            ))

    # Deduplicate: keep max 3 alerts per type per municipality
    seen: dict[str, int] = {}
    deduped: list[WeatherAlert] = []
    for a in alerts:
        key = f"{a.municipality}_{a.alert_type}"
        seen[key] = seen.get(key, 0) + 1
        if seen[key] <= 3:
            deduped.append(a)
    return deduped


async def fetch_all_greenhouse_weather() -> dict[str, Any]:
    """Fetch weather for all greenhouse locations and generate alerts.

    Returns dict with keys per municipality: current conditions + alerts.
    """
    results: dict[str, Any] = {}
    all_alerts: list[WeatherAlert] = []

    async with httpx.AsyncClient(timeout=15) as client:
        for muni, (lat, lng) in LOCATIONS.items():
            try:
                params = {
                    "latitude": lat,
                    "longitude": lng,
                    "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
                    "hourly": "temperature_2m,precipitation_probability,precipitation,weather_code",
                    "forecast_days": 3,
                    "timezone": "America/Mexico_City",
                }
                resp = await client.get(OPEN_METEO_FORECAST, params=params)
                resp.raise_for_status()
                data = resp.json()

                current = data.get("current", {})
                results[muni.value] = {
                    "municipality": muni.value,
                    "lat": lat,
                    "lng": lng,
                    "temperature_c": current.get("temperature_2m"),
                    "humidity_pct": current.get("relative_humidity_2m"),
                    "precipitation_mm": current.get("precipitation"),
                    "wind_speed_kmh": current.get("wind_speed_10m"),
                    "weather_code": current.get("weather_code"),
                    "forecast_hours": len(data.get("hourly", {}).get("time", [])),
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

                alerts = _generate_alerts(muni, data)
                all_alerts.extend(alerts)
                results[muni.value]["alerts_count"] = len(alerts)

            except Exception as exc:
                results[muni.value] = {
                    "municipality": muni.value,
                    "lat": lat,
                    "lng": lng,
                    "error": str(exc),
                }

    results["_alerts"] = [a.model_dump(mode="json") for a in all_alerts]
    results["_summary"] = {
        "locations_fetched": sum(1 for k, v in results.items() if not k.startswith("_") and "error" not in v),
        "total_alerts": len(all_alerts),
        "critical_alerts": sum(1 for a in all_alerts if a.severity == Severity.CRITICAL),
    }
    return results


async def fetch_crop_health(lat: float, lng: float) -> dict[str, Any]:
    """Fetch comprehensive crop health data from Open-Meteo.

    Uses: soil moisture, soil temp, ET0, precipitation, sunshine duration.
    Returns: {health_score: 0-100, ndvi_estimate: 0-1, stress_indicators, recommendations}
    """
    params = {
        "latitude": lat,
        "longitude": lng,
        "hourly": "soil_temperature_0cm,soil_moisture_0_to_1cm",
        "daily": "et0_fao_evapotranspiration,precipitation_sum,sunshine_duration",
        "timezone": "America/Mexico_City",
        "past_days": 7,
        "forecast_days": 7,
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(OPEN_METEO_FORECAST, params=params)
            resp.raise_for_status()
            data = resp.json()

        hourly = data.get("hourly", {})
        daily = data.get("daily", {})

        soil_temps = [t for t in hourly.get("soil_temperature_0cm", []) if t is not None]
        soil_moisture_vals = [m for m in hourly.get("soil_moisture_0_to_1cm", []) if m is not None]
        et0_vals = [e for e in daily.get("et0_fao_evapotranspiration", []) if e is not None]
        precip_vals = [p for p in daily.get("precipitation_sum", []) if p is not None]
        sunshine_vals = [s for s in daily.get("sunshine_duration", []) if s is not None]

        # Calculate averages
        avg_soil_temp = sum(soil_temps) / len(soil_temps) if soil_temps else 15.0
        avg_moisture = sum(soil_moisture_vals) / len(soil_moisture_vals) if soil_moisture_vals else 0.2
        avg_et0 = sum(et0_vals) / len(et0_vals) if et0_vals else 3.0
        total_precip_7d = sum(precip_vals[:7]) if precip_vals else 0.0
        avg_sunshine = sum(sunshine_vals) / len(sunshine_vals) if sunshine_vals else 25000.0

        # Calculate health score (0-100)
        score = 100.0
        stress_indicators: list[str] = []

        # Soil moisture scoring: optimal 0.15-0.35
        if avg_moisture < 0.05:
            score -= 40
            stress_indicators.append("Sequia critica — humedad del suelo muy baja")
        elif avg_moisture < 0.10:
            score -= 25
            stress_indicators.append("Estres hidrico — humedad del suelo baja")
        elif avg_moisture < 0.15:
            score -= 10
            stress_indicators.append("Humedad del suelo ligeramente baja")
        elif avg_moisture > 0.40:
            score -= 20
            stress_indicators.append("Exceso de humedad — riesgo de enfermedades fungicas")
        elif avg_moisture > 0.35:
            score -= 8
            stress_indicators.append("Humedad del suelo ligeramente alta")

        # Temperature scoring: optimal 15-25C
        if avg_soil_temp < 0:
            score -= 40
            stress_indicators.append("Helada severa — temperatura del suelo bajo cero")
        elif avg_soil_temp < 5:
            score -= 25
            stress_indicators.append("Estres por frio — temperatura del suelo muy baja")
        elif avg_soil_temp < 15:
            score -= 10
            stress_indicators.append("Temperatura del suelo suboptima (baja)")
        elif avg_soil_temp > 40:
            score -= 35
            stress_indicators.append("Estres termico severo — temperatura del suelo extrema")
        elif avg_soil_temp > 35:
            score -= 20
            stress_indicators.append("Estres termico — temperatura del suelo alta")
        elif avg_soil_temp > 25:
            score -= 8
            stress_indicators.append("Temperatura del suelo ligeramente alta")

        # Precipitation scoring
        if total_precip_7d < 2.0:
            score -= 10
            stress_indicators.append("Precipitacion insuficiente en ultimos 7 dias")
        elif total_precip_7d > 80.0:
            score -= 15
            stress_indicators.append("Exceso de lluvia — riesgo de anegamiento")

        # ET0 scoring (high ET0 = high water demand)
        if avg_et0 > 6.0:
            score -= 8
            stress_indicators.append("Evapotranspiracion alta — aumentar riego")

        score = max(0.0, min(100.0, score))

        # Estimate NDVI from health score (rough mapping)
        ndvi_estimate = 0.2 + (score / 100.0) * 0.6  # Maps 0-100 to 0.2-0.8

        return {
            "lat": lat,
            "lng": lng,
            "health_score": round(score, 1),
            "ndvi_estimate": round(ndvi_estimate, 3),
            "soil_moisture": round(avg_moisture, 4),
            "soil_temp_c": round(avg_soil_temp, 1),
            "et0_mm": round(avg_et0, 2),
            "precipitation_7d_mm": round(total_precip_7d, 1),
            "sunshine_avg_seconds": round(avg_sunshine, 0),
            "stress_indicators": stress_indicators,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as exc:
        return {
            "lat": lat,
            "lng": lng,
            "health_score": 50.0,
            "ndvi_estimate": 0.5,
            "soil_moisture": 0.2,
            "soil_temp_c": 15.0,
            "et0_mm": 3.0,
            "stress_indicators": [f"Error obteniendo datos: {exc}"],
            "error": str(exc),
        }


async def fetch_all_crop_health() -> list[dict[str, Any]]:
    """Fetch crop health for all greenhouse locations.

    Returns: [{municipality, farm_ids, health_score, ndvi_estimate,
    soil_moisture, soil_temp, et0, stress_indicators, trend}]
    """
    results: list[dict[str, Any]] = []

    for muni, (lat, lng) in LOCATIONS.items():
        health = await fetch_crop_health(lat, lng)

        # Determine trend based on score
        score = health.get("health_score", 50.0)
        if score >= 80:
            trend = "improving"
        elif score >= 50:
            trend = "stable"
        else:
            trend = "declining"

        results.append({
            "municipality": muni.value,
            "lat": lat,
            "lng": lng,
            "farm_ids": [],  # Will be populated by caller with actual farm IDs
            "health_score": health.get("health_score", 50.0),
            "ndvi_estimate": health.get("ndvi_estimate", 0.5),
            "soil_moisture": health.get("soil_moisture", 0.2),
            "soil_temp_c": health.get("soil_temp_c", 15.0),
            "et0_mm": health.get("et0_mm", 3.0),
            "precipitation_7d_mm": health.get("precipitation_7d_mm", 0.0),
            "stress_indicators": health.get("stress_indicators", []),
            "trend": trend,
            "fetched_at": health.get("fetched_at", ""),
        })

    return results


async def fetch_soil_data(lat: float, lng: float) -> dict[str, Any]:
    """Fetch soil moisture and temperature for a specific location.

    Uses Open-Meteo soil variables.
    """
    params = {
        "latitude": lat,
        "longitude": lng,
        "hourly": "soil_temperature_0cm,soil_temperature_6cm,soil_moisture_0_to_1cm,soil_moisture_1_to_3cm",
        "forecast_days": 1,
        "timezone": "America/Mexico_City",
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(OPEN_METEO_SOIL, params=params)
            resp.raise_for_status()
            data = resp.json()

        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        soil_temp_0 = hourly.get("soil_temperature_0cm", [])
        soil_temp_6 = hourly.get("soil_temperature_6cm", [])
        moisture_0_1 = hourly.get("soil_moisture_0_to_1cm", [])
        moisture_1_3 = hourly.get("soil_moisture_1_to_3cm", [])

        # Get latest readings
        latest_idx = len(times) - 1 if times else 0
        return {
            "lat": lat,
            "lng": lng,
            "time": times[latest_idx] if times else None,
            "soil_temperature_surface_c": soil_temp_0[latest_idx] if soil_temp_0 else None,
            "soil_temperature_6cm_c": soil_temp_6[latest_idx] if soil_temp_6 else None,
            "soil_moisture_0_1cm_m3m3": moisture_0_1[latest_idx] if moisture_0_1 else None,
            "soil_moisture_1_3cm_m3m3": moisture_1_3[latest_idx] if moisture_1_3 else None,
            "hourly_readings": len(times),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as exc:
        return {
            "lat": lat,
            "lng": lng,
            "error": str(exc),
        }
