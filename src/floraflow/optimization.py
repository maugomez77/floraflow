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


def set_auction_min_price(
    flower_type: str,
    quality_grade: str,
    stems: int,
    demand: list,
    signals: list,
) -> dict:
    """AI sets minimum auction price based on current market conditions.

    Returns: {min_price_mxn, buy_now_price_mxn, reasoning, market_context}
    """
    client = _client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=(
            "Eres un experto en pricing de subastas del mercado floricola mexicano. "
            "Estableces precios minimos competitivos que maximizan ingresos del vendedor "
            "sin espantar compradores. Precios de referencia por tallo (MXN): "
            "rosas $4-8, gerberas $5-7, liliums $12-20, crisantemos $2-4, "
            "gladiolas $2-4, claveles $1.5-3, girasoles $5-10, alstroemeria $3-6. "
            "Calidad export_premium = +40%, first = base, second = -20%, third = -40%. "
            "Responde SOLO en JSON valido."
        ),
        messages=[{
            "role": "user",
            "content": f"""
Establece el precio minimo de subasta para este lote:

Flor: {flower_type}
Calidad: {quality_grade}
Tallos: {stems}
Demanda actual: {json.dumps(demand[:10], default=str)}
Senales de mercado: {json.dumps(signals[:5], default=str)}

Responde en JSON:
{{
  "min_price_mxn": float,
  "buy_now_price_mxn": float,
  "price_per_stem_mxn": float,
  "reasoning": "str",
  "market_context": "str",
  "demand_level": "low|medium|high|peak",
  "recommended_duration_hours": int
}}""",
        }],
    )
    text = response.content[0].text
    try:
        return json.loads(text)
    except Exception:
        return {
            "min_price_mxn": stems * 4.0,
            "buy_now_price_mxn": stems * 6.0,
            "reasoning": text,
        }


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
