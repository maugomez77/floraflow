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
