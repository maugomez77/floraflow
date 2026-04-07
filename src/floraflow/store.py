"""Persistence layer for FloraFlow."""

from __future__ import annotations

import json
from pathlib import Path

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

STORE_DIR = Path.home() / ".floraflow"
STORE_PATH = STORE_DIR / "store.json"

_EMPTY: dict = {
    "greenhouses": [],
    "batches": [],
    "demand": [],
    "shipments": [],
    "orders": [],
    "quality": [],
    "signals": [],
    "harvest_plans": [],
    "weather_alerts": [],
    "stats": None,
}

# In-memory cache for serverless/ephemeral environments (Render free tier)
_cache: dict | None = None


def load() -> dict:
    global _cache
    if _cache is not None:
        return _cache
    try:
        if STORE_PATH.exists():
            _cache = json.loads(STORE_PATH.read_text())
            return _cache
    except Exception:
        pass
    return {k: list(v) if isinstance(v, list) else v for k, v in _EMPTY.items()}


def save(data: dict) -> None:
    global _cache
    _cache = data
    try:
        STORE_DIR.mkdir(parents=True, exist_ok=True)
        STORE_PATH.write_text(json.dumps(data, default=str, indent=2, ensure_ascii=False))
    except Exception:
        pass  # Filesystem may be read-only on some platforms


# --- Greenhouses ---

def list_greenhouses() -> list[Greenhouse]:
    return [Greenhouse(**g) for g in load()["greenhouses"]]


def get_greenhouse(gh_id: str) -> Greenhouse | None:
    for g in load()["greenhouses"]:
        if g["id"] == gh_id:
            return Greenhouse(**g)
    return None


def save_greenhouse(gh: Greenhouse) -> None:
    data = load()
    data["greenhouses"] = [g for g in data["greenhouses"] if g["id"] != gh.id]
    data["greenhouses"].append(gh.model_dump(mode="json"))
    save(data)


# --- Flower Batches ---

def list_batches(greenhouse_id: str | None = None, flower_type: str | None = None) -> list[FlowerBatch]:
    data = load()
    batches = data["batches"]
    if greenhouse_id:
        batches = [b for b in batches if b["greenhouse_id"] == greenhouse_id]
    if flower_type:
        batches = [b for b in batches if b["flower_type"] == flower_type]
    return [FlowerBatch(**b) for b in batches]


def get_batch(batch_id: str) -> FlowerBatch | None:
    for b in load()["batches"]:
        if b["id"] == batch_id:
            return FlowerBatch(**b)
    return None


def save_batch(batch: FlowerBatch) -> None:
    data = load()
    data["batches"] = [b for b in data["batches"] if b["id"] != batch.id]
    data["batches"].append(batch.model_dump(mode="json"))
    save(data)


# --- Market Demand ---

def list_demand(flower_type: str | None = None, market: str | None = None) -> list[MarketDemand]:
    data = load()
    items = data["demand"]
    if flower_type:
        items = [d for d in items if d["flower_type"] == flower_type]
    if market:
        items = [d for d in items if d["market"] == market]
    return [MarketDemand(**d) for d in items]


def save_demand(demand: MarketDemand) -> None:
    data = load()
    data["demand"] = [d for d in data["demand"] if d["id"] != demand.id]
    data["demand"].append(demand.model_dump(mode="json"))
    save(data)


# --- Shipments ---

def list_shipments(status: str | None = None) -> list[ColdChainShipment]:
    data = load()
    items = data["shipments"]
    if status:
        items = [s for s in items if s["status"] == status]
    return [ColdChainShipment(**s) for s in items]


def get_shipment(shipment_id: str) -> ColdChainShipment | None:
    for s in load()["shipments"]:
        if s["id"] == shipment_id:
            return ColdChainShipment(**s)
    return None


def save_shipment(shipment: ColdChainShipment) -> None:
    data = load()
    data["shipments"] = [s for s in data["shipments"] if s["id"] != shipment.id]
    data["shipments"].append(shipment.model_dump(mode="json"))
    save(data)


# --- Orders ---

def list_orders(status: str | None = None) -> list[BuyerOrder]:
    data = load()
    items = data["orders"]
    if status:
        items = [o for o in items if o["status"] == status]
    return [BuyerOrder(**o) for o in items]


def save_order(order: BuyerOrder) -> None:
    data = load()
    data["orders"] = [o for o in data["orders"] if o["id"] != order.id]
    data["orders"].append(order.model_dump(mode="json"))
    save(data)


# --- Quality ---

def list_quality(batch_id: str | None = None) -> list[QualityAssessment]:
    data = load()
    items = data["quality"]
    if batch_id:
        items = [q for q in items if q["batch_id"] == batch_id]
    return [QualityAssessment(**q) for q in items]


def save_quality(qa: QualityAssessment) -> None:
    data = load()
    data["quality"] = [q for q in data["quality"] if q["id"] != qa.id]
    data["quality"].append(qa.model_dump(mode="json"))
    save(data)


# --- Signals ---

def list_signals() -> list[PriceSignal]:
    return [PriceSignal(**s) for s in load()["signals"]]


def save_signal(signal: PriceSignal) -> None:
    data = load()
    data["signals"] = [s for s in data["signals"] if s["id"] != signal.id]
    data["signals"].append(signal.model_dump(mode="json"))
    save(data)


# --- Harvest Plans ---

def list_harvest_plans() -> list[HarvestPlan]:
    return [HarvestPlan(**h) for h in load()["harvest_plans"]]


def save_harvest_plan(hp: HarvestPlan) -> None:
    data = load()
    data["harvest_plans"] = [h for h in data["harvest_plans"] if h["id"] != hp.id]
    data["harvest_plans"].append(hp.model_dump(mode="json"))
    save(data)


# --- Weather Alerts ---

def list_weather_alerts() -> list[WeatherAlert]:
    return [WeatherAlert(**w) for w in load()["weather_alerts"]]


def save_weather_alert(alert: WeatherAlert) -> None:
    data = load()
    data["weather_alerts"] = [w for w in data["weather_alerts"] if w["id"] != alert.id]
    data["weather_alerts"].append(alert.model_dump(mode="json"))
    save(data)


# --- Stats ---

def get_stats() -> FlowStats | None:
    data = load()
    if data.get("stats"):
        return FlowStats(**data["stats"])
    return None


def save_stats(stats: FlowStats) -> None:
    data = load()
    data["stats"] = stats.model_dump(mode="json")
    save(data)


# --- Bulk save (for demo) ---

def save_all(
    greenhouses: list[Greenhouse] | None = None,
    batches: list[FlowerBatch] | None = None,
    demand: list[MarketDemand] | None = None,
    shipments: list[ColdChainShipment] | None = None,
    orders: list[BuyerOrder] | None = None,
    quality: list[QualityAssessment] | None = None,
    signals: list[PriceSignal] | None = None,
    harvest_plans: list[HarvestPlan] | None = None,
    weather_alerts: list[WeatherAlert] | None = None,
    stats: FlowStats | None = None,
) -> None:
    data = load()
    if greenhouses is not None:
        data["greenhouses"] = [g.model_dump(mode="json") for g in greenhouses]
    if batches is not None:
        data["batches"] = [b.model_dump(mode="json") for b in batches]
    if demand is not None:
        data["demand"] = [d.model_dump(mode="json") for d in demand]
    if shipments is not None:
        data["shipments"] = [s.model_dump(mode="json") for s in shipments]
    if orders is not None:
        data["orders"] = [o.model_dump(mode="json") for o in orders]
    if quality is not None:
        data["quality"] = [q.model_dump(mode="json") for q in quality]
    if signals is not None:
        data["signals"] = [s.model_dump(mode="json") for s in signals]
    if harvest_plans is not None:
        data["harvest_plans"] = [h.model_dump(mode="json") for h in harvest_plans]
    if weather_alerts is not None:
        data["weather_alerts"] = [w.model_dump(mode="json") for w in weather_alerts]
    if stats is not None:
        data["stats"] = stats.model_dump(mode="json")
    save(data)
