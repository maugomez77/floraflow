"""FastAPI application for FloraFlow — floriculture revenue optimization API."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import store
from .database import init_db
from .models import (
    BuyerOrder,
    ColdChainShipment,
    FlowerBatch,
    FlowStats,
    Greenhouse,
    HarvestPlan,
    MarketDemand,
    PriceSignal,
    QualityAssessment,
    WeatherAlert,
)


# --- Background research task ---

async def _background_research():
    """Run background market research on startup (non-blocking)."""
    await asyncio.sleep(2)  # Let the server finish binding
    try:
        from .demo import _research_prices, _research_events
        price_info, event_info = await asyncio.gather(
            _research_prices(),
            _research_events(),
            return_exceptions=True,
        )
        # Store results silently — these enrich the data
    except Exception:
        pass  # Non-critical — don't crash the server


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle — init DB and launch background research."""
    # Initialize database tables (no-op if DATABASE_URL is not set)
    await init_db()
    task = asyncio.create_task(_background_research())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


# --- App ---

app = FastAPI(
    title="FloraFlow API",
    description="AI-powered floriculture revenue optimization for Estado de Mexico",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Health ---

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "floraflow", "version": "0.1.0"}


# --- Greenhouses ---

@app.get("/v1/greenhouses", response_model=list[dict])
async def list_greenhouses():
    items = await store.async_list_greenhouses()
    return [g.model_dump(mode="json") for g in items]


@app.get("/v1/greenhouses/{gh_id}")
async def get_greenhouse(gh_id: str):
    item = await store.async_get_greenhouse(gh_id)
    if not item:
        raise HTTPException(status_code=404, detail="Greenhouse not found")
    return item.model_dump(mode="json")


# --- Batches ---

@app.get("/v1/batches", response_model=list[dict])
async def list_batches(
    greenhouse_id: Optional[str] = Query(None),
    flower_type: Optional[str] = Query(None),
):
    items = await store.async_list_batches(greenhouse_id=greenhouse_id, flower_type=flower_type)
    return [b.model_dump(mode="json") for b in items]


# --- Demand ---

@app.get("/v1/demand", response_model=list[dict])
async def list_demand(
    flower_type: Optional[str] = Query(None),
    market: Optional[str] = Query(None),
):
    items = await store.async_list_demand(flower_type=flower_type, market=market)
    return [d.model_dump(mode="json") for d in items]


# --- Shipments ---

@app.get("/v1/shipments", response_model=list[dict])
async def list_shipments(
    status: Optional[str] = Query(None),
):
    items = await store.async_list_shipments(status=status)
    return [s.model_dump(mode="json") for s in items]


@app.get("/v1/shipments/{shipment_id}")
async def get_shipment(shipment_id: str):
    item = await store.async_get_shipment(shipment_id)
    if not item:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return item.model_dump(mode="json")


# --- Orders ---

@app.get("/v1/orders", response_model=list[dict])
async def list_orders(
    status: Optional[str] = Query(None),
):
    items = await store.async_list_orders(status=status)
    return [o.model_dump(mode="json") for o in items]


# --- Quality ---

@app.get("/v1/quality", response_model=list[dict])
async def list_quality():
    items = await store.async_list_quality()
    return [q.model_dump(mode="json") for q in items]


# --- Signals ---

@app.get("/v1/signals", response_model=list[dict])
async def list_signals():
    items = await store.async_list_signals()
    return [s.model_dump(mode="json") for s in items]


# --- Harvest Plans ---

@app.get("/v1/harvest-plans", response_model=list[dict])
async def list_harvest_plans():
    items = await store.async_list_harvest_plans()
    return [h.model_dump(mode="json") for h in items]


# --- Stats ---

@app.get("/v1/stats")
async def get_stats():
    stats = await store.async_get_stats()
    if not stats:
        return {"message": "No stats available. Load demo data first."}
    return stats.model_dump(mode="json")


# --- Weather Alerts (stored) ---

@app.get("/v1/weather-alerts", response_model=list[dict])
async def weather_alerts():
    alerts = await store.async_list_weather_alerts()
    return [a.model_dump(mode="json") for a in alerts]


# --- Weather (live) ---

@app.get("/v1/weather/live")
async def weather_live():
    """Fetch live weather for all greenhouse locations from Open-Meteo."""
    from .feeds import fetch_all_greenhouse_weather
    try:
        result = await fetch_all_greenhouse_weather()
        return result
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Weather fetch failed: {exc}")


# --- AI Endpoints ---

@app.post("/v1/analyze")
async def analyze():
    """AI-powered market intelligence report."""
    from . import ai
    prices = await store.async_list_demand()
    sigs = await store.async_list_signals()
    if not prices and not sigs:
        raise HTTPException(status_code=400, detail="No market data. Load demo data first.")
    try:
        report = ai.generate_market_intelligence(prices=prices, signals=sigs)
        return {"report": report}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI analysis error: {exc}")


@app.post("/v1/optimize")
async def optimize():
    """AI-powered harvest timing optimization."""
    from . import ai
    batch_list = await store.async_list_batches()
    demand_list = await store.async_list_demand()
    if not batch_list:
        raise HTTPException(status_code=400, detail="No batch data. Load demo data first.")
    try:
        result = ai.optimize_harvest_timing(batch_list, demand_list)
        return {"plan": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI optimization error: {exc}")


@app.post("/v1/match")
async def match_buyers():
    """AI-powered buyer matching."""
    from . import ai
    batch_list = await store.async_list_batches()
    order_list = await store.async_list_orders()
    if not batch_list or not order_list:
        raise HTTPException(status_code=400, detail="Need batches and orders. Load demo data first.")
    try:
        result = ai.match_buyers(batch_list, order_list)
        return {"matches": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI matching error: {exc}")


@app.post("/v1/refresh")
async def refresh_data():
    """Refresh demo data."""
    from .demo import async_generate_demo_data
    try:
        await store.async_clear_all()
        result = await async_generate_demo_data()
        return {"status": "refreshed", "counts": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Refresh error: {exc}")
