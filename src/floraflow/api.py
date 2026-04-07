"""FastAPI application for FloraFlow — floriculture revenue optimization API."""

from __future__ import annotations

import asyncio
import base64
from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import FastAPI, File, Query, HTTPException, UploadFile
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


# =============================================================================
# VISION AI
# =============================================================================

@app.post("/v1/vision/grade")
async def vision_grade(file: UploadFile = File(...), flower_type: str = Query("rose")):
    """Grade flower quality from photo using Claude Vision."""
    from .vision import grade_flower_quality
    try:
        contents = await file.read()
        image_b64 = base64.b64encode(contents).decode()
        result = grade_flower_quality(image_b64, flower_type=flower_type)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Vision grading error: {exc}")


@app.post("/v1/vision/disease")
async def vision_disease(file: UploadFile = File(...)):
    """Detect diseases from photo using Claude Vision."""
    from .vision import detect_disease
    try:
        contents = await file.read()
        image_b64 = base64.b64encode(contents).decode()
        result = detect_disease(image_b64)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Vision disease detection error: {exc}")


# =============================================================================
# PREDICTIVE INTELLIGENCE
# =============================================================================

@app.post("/v1/predict/demand")
async def predict_demand_endpoint(
    flower_type: str = Query("rose"),
    days: int = Query(30),
):
    """Forecast demand for flower type."""
    from .predictive import forecast_demand
    from .feeds import fetch_all_greenhouse_weather
    demand_list = await store.async_list_demand(flower_type=flower_type)
    if not demand_list:
        raise HTTPException(status_code=400, detail="No demand data. Load demo data first.")
    current_demand = [
        {
            "flower": d.flower_type.value,
            "market": d.market.value,
            "price_mxn": d.price_per_stem_mxn,
            "demand": d.demand_level.value,
            "trend": d.price_trend.value,
            "event": d.event_driver,
        }
        for d in demand_list
    ]
    try:
        weather = await fetch_all_greenhouse_weather()
        weather_forecast = [
            v for k, v in weather.items()
            if not k.startswith("_") and isinstance(v, dict) and "error" not in v
        ]
    except Exception:
        weather_forecast = []
    try:
        result = forecast_demand(flower_type, current_demand, weather_forecast, days_ahead=days)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Demand forecast error: {exc}")


@app.post("/v1/predict/prices")
async def predict_prices_endpoint(flower_type: str = Query("rose")):
    """Predict prices 7 days ahead."""
    from .predictive import predict_prices
    from .feeds import fetch_all_greenhouse_weather
    demand_list = await store.async_list_demand(flower_type=flower_type)
    if not demand_list:
        raise HTTPException(status_code=400, detail="No price data. Load demo data first.")
    current_prices = [
        {
            "flower": d.flower_type.value,
            "market": d.market.value,
            "price_mxn": d.price_per_stem_mxn,
            "demand": d.demand_level.value,
            "trend": d.price_trend.value,
        }
        for d in demand_list
    ]
    try:
        weather = await fetch_all_greenhouse_weather()
        weather_data = [
            v for k, v in weather.items()
            if not k.startswith("_") and isinstance(v, dict) and "error" not in v
        ]
    except Exception:
        weather_data = []
    try:
        result = predict_prices(flower_type, current_prices, weather_data)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Price prediction error: {exc}")


@app.post("/v1/predict/frost")
async def predict_frost_endpoint():
    """Assess frost risk for all greenhouses."""
    from .predictive import assess_frost_risk
    from .feeds import fetch_all_greenhouse_weather
    greenhouses = await store.async_list_greenhouses()
    if not greenhouses:
        raise HTTPException(status_code=400, detail="No greenhouse data. Load demo data first.")
    gh_data = [
        {
            "id": g.id,
            "name": g.name,
            "municipality": g.municipality.value,
            "lat": g.location_lat,
            "lng": g.location_lng,
            "area_m2": g.area_m2,
            "flower_types": g.flower_types,
        }
        for g in greenhouses
    ]
    try:
        weather = await fetch_all_greenhouse_weather()
        weather_data = [
            v for k, v in weather.items()
            if not k.startswith("_") and isinstance(v, dict) and "error" not in v
        ]
    except Exception:
        weather_data = []
    try:
        result = assess_frost_risk(weather_data, gh_data)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Frost risk assessment error: {exc}")


# =============================================================================
# REVENUE OPTIMIZATION
# =============================================================================

@app.post("/v1/optimize/pricing")
async def optimize_pricing_endpoint():
    """Dynamic pricing recommendations."""
    from .optimization import dynamic_pricing
    batch_list = await store.async_list_batches()
    demand_list = await store.async_list_demand()
    signal_list = await store.async_list_signals()
    if not batch_list:
        raise HTTPException(status_code=400, detail="No batch data. Load demo data first.")
    batches_data = [
        {
            "flower": b.flower_type.value,
            "variety": b.variety,
            "stems": b.stems_count,
            "grade": b.quality_grade.value,
            "harvest_date": b.harvest_date,
            "shelf_life_days": b.shelf_life_days,
            "value_mxn": b.estimated_value_mxn,
        }
        for b in batch_list
    ]
    demand_data = [
        {
            "flower": d.flower_type.value,
            "market": d.market.value,
            "price_mxn": d.price_per_stem_mxn,
            "demand": d.demand_level.value,
            "trend": d.price_trend.value,
            "event": d.event_driver,
        }
        for d in demand_list
    ]
    signal_data = [
        {
            "flower": s.flower_type.value,
            "signal": s.signal_type.value,
            "description": s.description,
            "action": s.recommended_action,
            "priority": s.priority.value,
        }
        for s in signal_list
    ]
    try:
        result = dynamic_pricing(batches_data, demand_data, signal_data)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Dynamic pricing error: {exc}")


@app.post("/v1/optimize/routes")
async def optimize_routes_endpoint():
    """Optimize delivery routes."""
    from .optimization import optimize_routes
    shipments = await store.async_list_shipments()
    greenhouses = await store.async_list_greenhouses()
    if not shipments:
        raise HTTPException(status_code=400, detail="No shipment data. Load demo data first.")
    shipment_data = [
        {
            "id": s.id,
            "batch_ids": s.batch_ids,
            "origin": s.origin_municipality.value,
            "destination": s.destination.value,
            "status": s.status.value,
            "carrier": s.carrier,
            "truck_id": s.truck_id,
            "temperature_c": s.temperature_c,
            "departure_time": s.departure_time,
            "eta": s.eta,
        }
        for s in shipments
    ]
    gh_data = [
        {
            "id": g.id,
            "name": g.name,
            "municipality": g.municipality.value,
            "lat": g.location_lat,
            "lng": g.location_lng,
        }
        for g in greenhouses
    ]
    try:
        result = optimize_routes(shipment_data, gh_data)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Route optimization error: {exc}")


@app.post("/v1/optimize/waste")
async def predict_waste_endpoint():
    """Predict waste/spoilage risk."""
    from .optimization import predict_waste
    from .feeds import fetch_all_greenhouse_weather
    shipments = await store.async_list_shipments()
    if not shipments:
        raise HTTPException(status_code=400, detail="No shipment data. Load demo data first.")
    shipment_data = [
        {
            "id": s.id,
            "origin": s.origin_municipality.value,
            "destination": s.destination.value,
            "status": s.status.value,
            "temperature_c": s.temperature_c,
            "humidity_pct": s.humidity_pct,
            "departure_time": s.departure_time,
            "eta": s.eta,
        }
        for s in shipments
    ]
    try:
        weather = await fetch_all_greenhouse_weather()
        weather_data = [
            v for k, v in weather.items()
            if not k.startswith("_") and isinstance(v, dict) and "error" not in v
        ]
    except Exception:
        weather_data = []
    try:
        result = predict_waste(shipment_data, weather_data)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Waste prediction error: {exc}")
