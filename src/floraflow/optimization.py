"""Revenue optimization features."""

from __future__ import annotations

import json

import anthropic

MODEL = "claude-sonnet-4-20250514"


def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic()


def dynamic_pricing(batches: list, demand: list, signals: list) -> dict:
    """Real-time price recommendations based on supply/demand/events.

    Returns: {recommendations: [{flower_type, current_price, recommended_price,
    reasoning, urgency}], potential_revenue_increase_pct}
    """
    client = _client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=(
            "Eres un experto en pricing dinamico para el mercado floricola mexicano. "
            "Optimizas precios considerando oferta, demanda, eventos, competencia y "
            "perecibilidad. Responde en JSON."
        ),
        messages=[{
            "role": "user",
            "content": f"""
Genera recomendaciones de precio dinamico para estos lotes:

Lotes disponibles: {json.dumps(batches[:20], default=str)}
Demanda actual: {json.dumps(demand[:15], default=str)}
Senales de mercado: {json.dumps(signals[:10], default=str)}

Responde en JSON:
{{
  "recommendations": [
    {{
      "flower_type": "str",
      "quality_grade": "str",
      "current_avg_price_mxn": float,
      "recommended_price_mxn": float,
      "change_pct": float,
      "best_market": "jamaica|central_de_abasto|exportacion|eventos",
      "reasoning": "str",
      "urgency": "sell_today|this_week|can_hold",
      "shelf_life_remaining_days": int
    }}
  ],
  "potential_revenue_increase_pct": float,
  "market_timing": "str",
  "summary": "str"
}}""",
        }],
    )
    text = response.content[0].text
    try:
        return json.loads(text)
    except Exception:
        return {"recommendations": [], "summary": text}


def optimize_routes(shipments: list, greenhouses: list) -> dict:
    """Optimal truck routes from greenhouses to CDMX markets.

    Returns: {routes: [{route_name, stops, total_km, estimated_hours,
    fuel_cost_mxn}], savings_vs_current}
    """
    client = _client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=(
            "Eres un experto en logistica de la cadena de frio para flores en Mexico. "
            "Conoces las rutas Villa Guerrero -> CDMX (~120km, 2-3 hrs), "
            "Tenancingo -> CDMX (~100km, 2 hrs). La frescura es critica — cada hora "
            "cuenta. Responde en JSON."
        ),
        messages=[{
            "role": "user",
            "content": f"""
Optimiza las rutas de entrega para estos envios:

Envios activos: {json.dumps(shipments[:10], default=str)}
Invernaderos origen: {json.dumps(greenhouses[:15], default=str)}

Responde en JSON:
{{
  "optimized_routes": [
    {{
      "route_name": "str",
      "stops": ["greenhouse_name -> market_name"],
      "total_km": float,
      "estimated_hours": float,
      "departure_time_recommended": "str (HH:MM)",
      "arrival_before": "str",
      "fuel_cost_mxn": float,
      "cold_chain_risk": "low|medium|high"
    }}
  ],
  "savings_vs_current_pct": float,
  "key_recommendations": ["str"],
  "optimal_departure_window": "str"
}}""",
        }],
    )
    text = response.content[0].text
    try:
        return json.loads(text)
    except Exception:
        return {"optimized_routes": [], "raw": text}


def predict_waste(shipments: list, weather: list) -> dict:
    """Estimate spoilage risk based on temperature, humidity, transport time.

    Returns: {at_risk_shipments: [{id, spoilage_risk_pct, estimated_loss_stems,
    estimated_loss_mxn, cause, mitigation}], total_loss_estimate}
    """
    client = _client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=(
            "Eres un experto en postcosecha floricola. Las flores pierden 10% de valor "
            "por cada grado arriba de 4C en transporte. La vida de florero se reduce 20% "
            "por cada 5% de humedad debajo del 85%. Responde en JSON."
        ),
        messages=[{
            "role": "user",
            "content": f"""
Evalua el riesgo de perdida/merma para estos envios:

Envios: {json.dumps(shipments[:10], default=str)}
Clima en ruta: {json.dumps(weather[:5], default=str)}

Responde en JSON:
{{
  "at_risk_shipments": [
    {{
      "shipment_id": "str",
      "destination": "str",
      "spoilage_risk_pct": float,
      "estimated_loss_stems": int,
      "estimated_loss_mxn": float,
      "primary_cause": "temperature|humidity|transit_time|handling",
      "mitigation": "str"
    }}
  ],
  "total_estimated_loss_mxn": float,
  "total_stems_at_risk": int,
  "preventive_actions": ["str"],
  "cold_chain_compliance_pct": float
}}""",
        }],
    )
    text = response.content[0].text
    try:
        return json.loads(text)
    except Exception:
        return {
            "at_risk_shipments": [],
            "total_estimated_loss_mxn": 0,
            "raw": text,
        }
