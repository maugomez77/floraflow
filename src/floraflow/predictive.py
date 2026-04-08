"""Predictive intelligence for floriculture."""

from __future__ import annotations

import json
from datetime import date

import anthropic

MODEL = "claude-sonnet-4-20250514"


def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic()


def forecast_demand(
    flower_type: str,
    current_demand: list,
    weather_forecast: list,
    days_ahead: int = 30,
) -> dict:
    """Predict demand for next N days based on weather + events + historical patterns.

    Returns: {forecast: [{week, predicted_demand_level, predicted_price_mxn,
    confidence, event_driver}], summary, recommendations}
    """
    client = _client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=(
            "Eres un experto en prediccion de demanda del mercado floricola mexicano. "
            "Conoces los patrones estacionales: San Valentin (14 Feb, rosas 300% spike), "
            "Dia de las Madres (10 May, ALL flowers 200-400%), Dia de Muertos (1-2 Nov, "
            "cempasuchil y crisantemos), Navidad, temporada de bodas (Abr-Jun). "
            "Responde en JSON."
        ),
        messages=[{
            "role": "user",
            "content": f"""
Pronostica la demanda de {flower_type} para los proximos {days_ahead} dias.

Datos actuales de demanda: {json.dumps(current_demand[:10], default=str)}
Pronostico del clima: {json.dumps(weather_forecast[:7], default=str)}
Fecha actual: {date.today().isoformat()}

Responde en JSON:
{{
  "forecast": [
    {{"week": 1, "demand_level": "low|medium|high|peak", "predicted_price_mxn": float, "confidence": 0-1, "event_driver": "none|valentines|mothers_day|dia_muertos|xmas|weddings", "reasoning": "str"}}
  ],
  "trend": "increasing|stable|decreasing",
  "key_events_ahead": ["str"],
  "recommendations": ["str"],
  "risk_factors": ["str"]
}}""",
        }],
    )
    text = response.content[0].text
    try:
        return json.loads(text)
    except Exception:
        return {"forecast": [], "trend": "stable", "recommendations": [text]}


def predict_prices(
    flower_type: str,
    current_prices: list,
    weather: list,
) -> dict:
    """Predict Jamaica/Central de Abasto prices 7 days ahead.

    Returns: {predictions: [{day, market, predicted_price_mxn, confidence, factors}],
    arbitrage_opportunities}
    """
    client = _client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=(
            "Eres un analista de precios del mercado floricola de la CDMX. "
            "Conoces los patrones de precios del Mercado de Jamaica y Central de Abasto. "
            "Responde en JSON."
        ),
        messages=[{
            "role": "user",
            "content": f"""
Predice los precios de {flower_type} para los proximos 7 dias.

Precios actuales: {json.dumps(current_prices[:10], default=str)}
Clima proximos dias: {json.dumps(weather[:5], default=str)}

Responde en JSON:
{{
  "predictions": [
    {{"day": 1, "market": "jamaica|central_de_abasto|exportacion", "predicted_price_mxn": float, "confidence": 0-1, "factors": ["str"]}}
  ],
  "best_sell_day": int,
  "best_market": "str",
  "arbitrage_opportunities": ["str"],
  "price_trend": "up|down|stable",
  "volatility": "low|medium|high"
}}""",
        }],
    )
    text = response.content[0].text
    try:
        return json.loads(text)
    except Exception:
        return {"predictions": [], "price_trend": "stable", "raw": text}


def analyze_crop_health(health_data: list, greenhouses: list) -> dict:
    """AI analyzes satellite/sensor data and generates actionable insights.

    Returns: {overall_health, at_risk_zones, recommendations,
    irrigation_schedule, fertilization_schedule}
    """
    client = _client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=(
            "Eres un agronomo experto en floricultura del Estado de Mexico. "
            "Analizas datos de salud de cultivos (humedad del suelo, temperatura, "
            "evapotranspiracion) para generar recomendaciones accionables. "
            "Las flores necesitan: humedad del suelo 0.15-0.35 m3/m3, "
            "temperatura 15-25C, ET0 adecuada para riego. "
            "Responde SOLO en JSON valido."
        ),
        messages=[{
            "role": "user",
            "content": f"""
Analiza la salud de los cultivos en estas zonas floricolas:

Datos de salud: {json.dumps(health_data[:10], default=str)}
Invernaderos: {json.dumps([{{"id": g["id"], "name": g["name"], "municipality": g["municipality"], "flowers": g.get("flower_types", [])}} for g in greenhouses[:15]], default=str)}

Responde en JSON:
{{
  "overall_health": "excellent|good|moderate|poor|critical",
  "overall_score": float,
  "at_risk_zones": [
    {{"municipality": "str", "risk_level": "low|medium|high|critical", "issue": "str", "affected_farms": int}}
  ],
  "recommendations": [
    {{"priority": "urgent|high|medium|low", "action": "str", "target_zone": "str", "expected_impact": "str"}}
  ],
  "irrigation_schedule": [
    {{"zone": "str", "frequency": "str", "volume_liters_m2": float, "best_time": "str"}}
  ],
  "fertilization_schedule": [
    {{"zone": "str", "type": "str", "application_date": "str", "dosage": "str"}}
  ],
  "summary": "str"
}}""",
        }],
    )
    text = response.content[0].text
    try:
        return json.loads(text)
    except Exception:
        return {
            "overall_health": "moderate",
            "recommendations": [],
            "summary": text,
        }


def assess_frost_risk(weather_data: list, greenhouses: list) -> dict:
    """Frost risk assessment per greenhouse based on weather + altitude + microclimate.

    Returns: {risk_level, greenhouses_at_risk: [{id, name, risk, min_temp_forecast,
    recommended_action}], cost_of_inaction_mxn}
    """
    client = _client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=(
            "Eres un agrometeorologo experto en floricultura del Estado de Mexico. "
            "Las flores son extremadamente sensibles al frio — por debajo de 3C hay dano, "
            "por debajo de 0C es perdida total. Responde en JSON."
        ),
        messages=[{
            "role": "user",
            "content": f"""
Evalua el riesgo de heladas para estos invernaderos:

Datos meteorologicos: {json.dumps(weather_data[:10], default=str)}
Invernaderos: {json.dumps(greenhouses[:15], default=str)}

Responde en JSON:
{{
  "overall_risk": "low|medium|high|critical",
  "greenhouses_at_risk": [
    {{"id": "str", "name": "str", "risk_level": "low|medium|high|critical", "min_temp_forecast_c": float, "recommended_action": "str", "estimated_loss_if_no_action_mxn": float}}
  ],
  "total_estimated_loss_mxn": float,
  "recommended_actions": ["str"],
  "monitoring_frequency": "hourly|every_4h|daily"
}}""",
        }],
    )
    text = response.content[0].text
    try:
        return json.loads(text)
    except Exception:
        return {
            "overall_risk": "low",
            "greenhouses_at_risk": [],
            "raw": text,
        }
