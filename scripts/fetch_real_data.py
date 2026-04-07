"""Fetch real floriculture data and populate the Neon database."""

import asyncio
import json
import os
import random
import time

# Ensure dotenv loaded
import floraflow

from anthropic import Anthropic
from ddgs import DDGS
from floraflow.database import init_db
from floraflow import store
from floraflow.models import MarketDemand, PriceSignal, FlowStats


def research_real_data() -> dict:
    """Search DuckDuckGo for real Mexican flower market data."""
    ddgs = DDGS()
    queries = [
        "precio flores Central de Abasto Mexico City 2026",
        "flower wholesale prices Mexico City Jamaica market",
        "Villa Guerrero floricultura produccion 2026",
        "Estado de Mexico flower export statistics",
        "Mexico Valentine flowers rose price per stem 2026",
        "Mother Day flowers Mexico precio mayoreo",
        "Mexico cut flower industry statistics greenhouse hectares",
        "Tenancingo Villa Guerrero flower growers cooperatives",
        "rosas precio docena Mexico 2026",
        "crisantemo gladiola precio mayoreo Mexico",
    ]

    all_results = []
    for q in queries:
        try:
            results = ddgs.text(q, max_results=5)
            for r in results:
                all_results.append(f'{r.get("title", "")}: {r.get("body", "")}')
        except Exception:
            pass
        time.sleep(random.uniform(0.3, 0.8))

    print(f"Gathered {len(all_results)} search results")

    # Ask Claude to extract structured data
    client = Anthropic()
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4000,
        system="You are a Mexican floriculture data expert. Extract REAL data from search results. Return JSON only, no markdown.",
        messages=[{
            "role": "user",
            "content": f"""From these search results about Mexican flower markets, extract real data as JSON:

{chr(10).join(all_results[:40])}

Return this JSON structure:
{{
  "market_prices": [
    {{"flower_type": "rose", "market": "jamaica", "price_per_stem_mxn": 5.0, "price_trend": "up", "source": "Central de Abasto"}},
    {{"flower_type": "chrysanthemum", "market": "central_de_abasto", "price_per_stem_mxn": 3.0, "price_trend": "stable", "source": "SNIIM"}}
  ],
  "production_stats": {{
    "total_hectares_edo_mex": 7000,
    "annual_production_tons": 500000,
    "annual_export_value_usd": 100000000,
    "pct_national_production": 70.0,
    "num_producers": 15000,
    "num_greenhouses_approx": 5000
  }},
  "real_cooperatives": [
    {{"name": "Cooperativa name", "municipality": "villa_guerrero", "specialty": "roses"}}
  ],
  "seasonal_multipliers": [
    {{"event": "San Valentin", "flower": "rose", "normal_price_mxn": 5.0, "event_price_mxn": 20.0, "multiplier": 4.0}},
    {{"event": "Dia de las Madres", "flower": "rose", "normal_price_mxn": 5.0, "event_price_mxn": 15.0, "multiplier": 3.0}}
  ],
  "insights": [
    {{"title": "insight title", "description": "real insight from the data", "priority": "high"}}
  ]
}}

Only include data you can verify or reasonably estimate from search results.""",
        }],
    )

    text = response.content[0].text
    # Strip markdown code blocks if present
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    return json.loads(text.strip())


async def populate_real_data(real_data: dict):
    """Update the database with real market data."""
    await init_db()

    from datetime import date

    today = date.today().isoformat()

    # Map market names to valid enums
    market_map = {
        "jamaica": "jamaica", "mercado jamaica": "jamaica", "mercado de jamaica": "jamaica",
        "central_de_abasto": "central_de_abasto", "central de abasto": "central_de_abasto",
        "mayoreo": "central_de_abasto", "wholesale": "central_de_abasto",
        "exportacion": "exportacion", "export": "exportacion",
        "eventos": "eventos", "retail": "retail",
    }
    valid_flowers = {"rose", "chrysanthemum", "gerbera", "lily", "gladiolus", "alstroemeria", "carnation", "sunflower"}

    # Update market demand with real prices
    for mp in real_data.get("market_prices", []):
        flower = mp.get("flower_type", "rose")
        if flower not in valid_flowers:
            flower = "rose"
        market = market_map.get(mp.get("market", "").lower(), "jamaica")
        price = mp.get("price_per_stem_mxn") or mp.get("price_per_stem_usd", 0) * 17.5
        if not price or price <= 0:
            continue
        # If price seems like per-dozen, convert to per-stem
        if price > 50:
            price = price / 12
        demand = MarketDemand(
            flower_type=flower,
            market=market,
            demand_level="high",
            price_per_stem_mxn=round(price, 2),
            price_trend=mp.get("price_trend", "stable"),
            date=today,
            event_driver=None,
        )
        await store.async_save_demand(demand)

    # Add seasonal price signals
    for sm in real_data.get("seasonal_multipliers", []):
        multiplier = sm.get("multiplier", 2.0)
        event = sm.get("event", "unknown")
        flower = sm.get("flower", "rose")
        if flower not in valid_flowers:
            flower = "chrysanthemum" if "muerto" in event.lower() else "rose"
        date_range = sm.get("date_range", "")
        signal = PriceSignal(
            flower_type=flower,
            signal_type="event_premium",
            description=f'{event} ({date_range}): precio se multiplica {multiplier}x',
            recommended_action=f"Programar cosecha para {event}. Multiplicador de precio: {multiplier}x",
            valid_until=today,
            priority="high",
        )
        await store.async_save_signal(signal)

    # Add real insights as signals
    for insight in real_data.get("insights", []):
        signal = PriceSignal(
            flower_type="rose",  # default
            signal_type="demand_surge" if insight.get("priority") == "high" else "price_spike",
            description=insight["description"],
            recommended_action=insight.get("title", ""),
            valid_until=today,
            priority=insight.get("priority", "medium"),
        )
        await store.async_save_signal(signal)

    # Update stats with real production numbers
    prod = real_data.get("production_stats", {})
    if prod:
        stats = await store.async_get_stats()
        if stats:
            stats = stats.model_copy(update={
                "total_area_m2": prod.get("total_hectares_edo_mex", 7000) * 10000,  # hectares to m2
            })
            await store.async_save_stats(stats)

    print(f"Real data populated:")
    print(f"  Market prices: {len(real_data.get('market_prices', []))}")
    print(f"  Seasonal signals: {len(real_data.get('seasonal_multipliers', []))}")
    print(f"  Insights: {len(real_data.get('insights', []))}")
    print(f"  Cooperatives found: {len(real_data.get('real_cooperatives', []))}")
    if real_data.get("real_cooperatives"):
        for coop in real_data["real_cooperatives"]:
            print(f"    - {coop['name']} ({coop['municipality']}): {coop['specialty']}")
    if prod:
        print(f"  Production stats:")
        print(f"    Hectares: {prod.get('total_hectares_edo_mex', 'N/A')}")
        print(f"    Annual tons: {prod.get('annual_production_tons', 'N/A')}")
        print(f"    Export value: ${prod.get('annual_export_value_usd', 'N/A')} USD")
        print(f"    % national: {prod.get('pct_national_production', 'N/A')}%")
        print(f"    Producers: {prod.get('num_producers', 'N/A')}")


if __name__ == "__main__":
    print("Researching real Mexican floriculture data...")
    real_data = research_real_data()
    print(json.dumps(real_data, indent=2, ensure_ascii=False))
    print("\nPopulating database...")
    asyncio.run(populate_real_data(real_data))
    print("\nDone!")
