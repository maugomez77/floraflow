"""AI analysis module for FloraFlow — Claude-powered floriculture intelligence."""

from __future__ import annotations

import json
import os
from typing import Any

import anthropic

from .models import (
    BuyerOrder,
    FlowerBatch,
    MarketDemand,
    PriceSignal,
)

MODEL = "claude-sonnet-4-20250514"


def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic()


def _call(system: str, prompt: str, max_tokens: int = 2000) -> str:
    """Call Claude and return text response."""
    client = _client()
    resp = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


# ---------- Harvest Optimization ----------

def optimize_harvest_timing(
    batches: list[FlowerBatch],
    demand: list[MarketDemand],
    weather: dict[str, Any] | None = None,
) -> str:
    """AI-powered harvest timing optimization for maximum revenue."""
    system = (
        "Eres un experto agronomo especializado en floricultura del Estado de Mexico. "
        "Analizas datos de lotes de flores, demanda de mercado y clima para recomendar "
        "el momento optimo de cosecha que maximice ingresos. Responde en espanol. "
        "Da recomendaciones concretas con fechas, cantidades y precios esperados en MXN."
    )
    batches_data = [
        {
            "id": b.id,
            "flower": b.flower_type.value,
            "variety": b.variety,
            "stems": b.stems_count,
            "grade": b.quality_grade.value,
            "harvest_date": b.harvest_date,
            "shelf_life_days": b.shelf_life_days,
            "value_mxn": b.estimated_value_mxn,
        }
        for b in batches[:20]
    ]
    demand_data = [
        {
            "flower": d.flower_type.value,
            "market": d.market.value,
            "demand": d.demand_level.value,
            "price_mxn": d.price_per_stem_mxn,
            "trend": d.price_trend.value,
            "event": d.event_driver,
        }
        for d in demand[:20]
    ]
    prompt = (
        f"Analiza estos lotes de flores disponibles y la demanda actual para optimizar "
        f"el timing de cosecha:\n\n"
        f"## Lotes disponibles\n```json\n{json.dumps(batches_data, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## Demanda de mercado\n```json\n{json.dumps(demand_data, ensure_ascii=False, indent=2)}\n```\n\n"
    )
    if weather:
        prompt += f"## Clima actual\n```json\n{json.dumps(weather, ensure_ascii=False, indent=2)}\n```\n\n"
    prompt += (
        "Genera un plan de cosecha optimizado que incluya:\n"
        "1. Prioridad de corte por lote (cual cortar primero)\n"
        "2. Mercado destino recomendado para cada lote\n"
        "3. Precio esperado y revenue total estimado en MXN\n"
        "4. Alertas de clima que afecten el plan\n"
        "5. Recomendaciones especificas por tipo de flor"
    )
    return _call(system, prompt, max_tokens=3000)


# ---------- Buyer Matching ----------

def match_buyers(
    batches: list[FlowerBatch],
    orders: list[BuyerOrder],
) -> str:
    """AI-powered matching of flower supply with buyer demand."""
    system = (
        "Eres un broker especializado en el Mercado de Jamaica y la cadena de suministro "
        "de flores del Estado de Mexico. Emparejas oferta de invernaderos con pedidos "
        "de compradores para maximizar satisfaction y revenue. Responde en espanol. "
        "Usa precios en MXN."
    )
    supply = [
        {
            "batch_id": b.id,
            "flower": b.flower_type.value,
            "variety": b.variety,
            "stems": b.stems_count,
            "grade": b.quality_grade.value,
            "color": b.color,
            "value_mxn": b.estimated_value_mxn,
            "harvest_date": b.harvest_date,
        }
        for b in batches[:20]
    ]
    demand = [
        {
            "order_id": o.id,
            "buyer": o.buyer_name,
            "type": o.buyer_type.value,
            "flowers_needed": o.flower_types_needed,
            "stems_needed": o.stems_needed,
            "quality_required": o.quality_required.value,
            "delivery_date": o.delivery_date,
            "price_offered_mxn": o.price_offered_mxn,
            "status": o.status.value,
        }
        for o in orders[:15]
    ]
    prompt = (
        f"Empareja la oferta disponible con los pedidos de compradores:\n\n"
        f"## Oferta (lotes disponibles)\n```json\n{json.dumps(supply, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## Demanda (pedidos)\n```json\n{json.dumps(demand, ensure_ascii=False, indent=2)}\n```\n\n"
        "Genera:\n"
        "1. Emparejamiento optimo (que lotes a que pedido)\n"
        "2. Revenue estimado por match en MXN\n"
        "3. Pedidos sin cubrir y acciones recomendadas\n"
        "4. Lotes sobrantes y mercados alternativos sugeridos\n"
        "5. Score de satisfaccion del match (1-10)"
    )
    return _call(system, prompt, max_tokens=3000)


# ---------- Demand Prediction ----------

def predict_demand(
    flower_type: str,
    season: str | None = None,
    events: list[str] | None = None,
) -> str:
    """AI-powered demand forecasting for a specific flower type."""
    system = (
        "Eres un analista de mercado de flores mexicano con 20 anos de experiencia. "
        "Conoces los patrones estacionales del Mercado de Jamaica, Central de Abasto, "
        "y exportacion. Responde en espanol con datos cuantitativos en MXN."
    )
    prompt = (
        f"Pronostica la demanda para: **{flower_type}**\n\n"
        f"Temporada actual: {season or 'primavera'}\n"
        f"Eventos proximos: {', '.join(events) if events else 'ninguno especial'}\n\n"
        "Incluye:\n"
        "1. Demanda estimada en stems para los proximos 30 dias\n"
        "2. Precio esperado por tallo en MXN por mercado\n"
        "3. Tendencia (subiendo/bajando/estable) con justificacion\n"
        "4. Eventos que pueden impactar la demanda\n"
        "5. Recomendacion de produccion para los floricultores"
    )
    return _call(system, prompt, max_tokens=2000)


# ---------- Market Intelligence ----------

def generate_market_intelligence(
    prices: list[MarketDemand] | None = None,
    signals: list[PriceSignal] | None = None,
) -> str:
    """AI-powered market intelligence report."""
    system = (
        "Eres un analista de inteligencia de mercado de la industria floricola mexicana. "
        "Generas reportes ejecutivos con insights accionables para productores del "
        "Estado de Mexico. Responde en espanol. Precios en MXN."
    )
    price_data = []
    if prices:
        price_data = [
            {
                "flower": p.flower_type.value,
                "market": p.market.value,
                "price_mxn": p.price_per_stem_mxn,
                "demand": p.demand_level.value,
                "trend": p.price_trend.value,
                "event": p.event_driver,
            }
            for p in prices[:30]
        ]
    signal_data = []
    if signals:
        signal_data = [
            {
                "flower": s.flower_type.value,
                "signal": s.signal_type.value,
                "description": s.description,
                "action": s.recommended_action,
                "priority": s.priority.value,
            }
            for s in signals[:10]
        ]
    prompt = (
        "Genera un reporte de inteligencia de mercado floricola:\n\n"
        f"## Precios actuales\n```json\n{json.dumps(price_data, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## Senales de mercado\n```json\n{json.dumps(signal_data, ensure_ascii=False, indent=2)}\n```\n\n"
        "Incluye:\n"
        "1. Resumen ejecutivo (3-5 puntos clave)\n"
        "2. Oportunidades de alto margen\n"
        "3. Riesgos y amenazas\n"
        "4. Recomendaciones por tipo de flor\n"
        "5. Perspectiva a 30 dias\n"
        "6. Top 3 acciones inmediatas para maximizar revenue"
    )
    return _call(system, prompt, max_tokens=3000)
