"""Persistence layer for FloraFlow — hybrid PostgreSQL + JSON file store."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from sqlalchemy import select, delete

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
from .database import (
    async_session,
    engine,
    GreenhouseDB,
    FlowerBatchDB,
    MarketDemandDB,
    ColdChainShipmentDB,
    QualityAssessmentDB,
    BuyerOrderDB,
    WeatherAlertDB,
    PriceSignalDB,
    HarvestPlanDB,
    StatsDB,
    init_db,
)

# --- JSON file store (fallback) ---

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


def _use_db() -> bool:
    """Check if PostgreSQL is available."""
    return engine is not None


# --- JSON helpers ---

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


# --- Row <-> dict helpers ---

def _row_to_dict(row: Any) -> dict:
    """Convert a SQLAlchemy ORM row to a plain dict."""
    d = {}
    for col in row.__table__.columns:
        d[col.name] = getattr(row, col.name)
    return d


def _model_to_row(model_instance: Any, db_cls: type) -> Any:
    """Convert a Pydantic model instance to a SQLAlchemy ORM row."""
    data = model_instance.model_dump(mode="json")
    return db_cls(**data)


# --- Sync wrapper for CLI ---

def _run_async(coro):
    """Run an async coroutine synchronously for CLI usage."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # We're inside an async context — create a new thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()
    else:
        return asyncio.run(coro)


# =============================================================================
# GREENHOUSES
# =============================================================================

async def async_list_greenhouses() -> list[Greenhouse]:
    if _use_db():
        async with async_session() as session:
            result = await session.execute(select(GreenhouseDB))
            rows = result.scalars().all()
            return [Greenhouse(**_row_to_dict(r)) for r in rows]
    data = load()
    return [Greenhouse(**g) for g in data.get("greenhouses", [])]


async def async_get_greenhouse(gh_id: str) -> Greenhouse | None:
    if _use_db():
        async with async_session() as session:
            result = await session.execute(
                select(GreenhouseDB).where(GreenhouseDB.id == gh_id)
            )
            row = result.scalar_one_or_none()
            return Greenhouse(**_row_to_dict(row)) if row else None
    for g in load().get("greenhouses", []):
        if g["id"] == gh_id:
            return Greenhouse(**g)
    return None


async def async_save_greenhouse(gh: Greenhouse) -> None:
    if _use_db():
        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    delete(GreenhouseDB).where(GreenhouseDB.id == gh.id)
                )
                session.add(_model_to_row(gh, GreenhouseDB))
        return
    data = load()
    data["greenhouses"] = [g for g in data["greenhouses"] if g["id"] != gh.id]
    data["greenhouses"].append(gh.model_dump(mode="json"))
    save(data)


def list_greenhouses() -> list[Greenhouse]:
    if _use_db():
        return _run_async(async_list_greenhouses())
    return [Greenhouse(**g) for g in load()["greenhouses"]]


def get_greenhouse(gh_id: str) -> Greenhouse | None:
    if _use_db():
        return _run_async(async_get_greenhouse(gh_id))
    for g in load()["greenhouses"]:
        if g["id"] == gh_id:
            return Greenhouse(**g)
    return None


def save_greenhouse(gh: Greenhouse) -> None:
    if _use_db():
        _run_async(async_save_greenhouse(gh))
        return
    data = load()
    data["greenhouses"] = [g for g in data["greenhouses"] if g["id"] != gh.id]
    data["greenhouses"].append(gh.model_dump(mode="json"))
    save(data)


# =============================================================================
# FLOWER BATCHES
# =============================================================================

async def async_list_batches(
    greenhouse_id: str | None = None, flower_type: str | None = None
) -> list[FlowerBatch]:
    if _use_db():
        async with async_session() as session:
            stmt = select(FlowerBatchDB)
            if greenhouse_id:
                stmt = stmt.where(FlowerBatchDB.greenhouse_id == greenhouse_id)
            if flower_type:
                stmt = stmt.where(FlowerBatchDB.flower_type == flower_type)
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [FlowerBatch(**_row_to_dict(r)) for r in rows]
    data = load()
    batches = data["batches"]
    if greenhouse_id:
        batches = [b for b in batches if b["greenhouse_id"] == greenhouse_id]
    if flower_type:
        batches = [b for b in batches if b["flower_type"] == flower_type]
    return [FlowerBatch(**b) for b in batches]


async def async_get_batch(batch_id: str) -> FlowerBatch | None:
    if _use_db():
        async with async_session() as session:
            result = await session.execute(
                select(FlowerBatchDB).where(FlowerBatchDB.id == batch_id)
            )
            row = result.scalar_one_or_none()
            return FlowerBatch(**_row_to_dict(row)) if row else None
    for b in load()["batches"]:
        if b["id"] == batch_id:
            return FlowerBatch(**b)
    return None


async def async_save_batch(batch: FlowerBatch) -> None:
    if _use_db():
        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    delete(FlowerBatchDB).where(FlowerBatchDB.id == batch.id)
                )
                session.add(_model_to_row(batch, FlowerBatchDB))
        return
    data = load()
    data["batches"] = [b for b in data["batches"] if b["id"] != batch.id]
    data["batches"].append(batch.model_dump(mode="json"))
    save(data)


def list_batches(greenhouse_id: str | None = None, flower_type: str | None = None) -> list[FlowerBatch]:
    if _use_db():
        return _run_async(async_list_batches(greenhouse_id=greenhouse_id, flower_type=flower_type))
    data = load()
    batches = data["batches"]
    if greenhouse_id:
        batches = [b for b in batches if b["greenhouse_id"] == greenhouse_id]
    if flower_type:
        batches = [b for b in batches if b["flower_type"] == flower_type]
    return [FlowerBatch(**b) for b in batches]


def get_batch(batch_id: str) -> FlowerBatch | None:
    if _use_db():
        return _run_async(async_get_batch(batch_id))
    for b in load()["batches"]:
        if b["id"] == batch_id:
            return FlowerBatch(**b)
    return None


def save_batch(batch: FlowerBatch) -> None:
    if _use_db():
        _run_async(async_save_batch(batch))
        return
    data = load()
    data["batches"] = [b for b in data["batches"] if b["id"] != batch.id]
    data["batches"].append(batch.model_dump(mode="json"))
    save(data)


# =============================================================================
# MARKET DEMAND
# =============================================================================

async def async_list_demand(
    flower_type: str | None = None, market: str | None = None
) -> list[MarketDemand]:
    if _use_db():
        async with async_session() as session:
            stmt = select(MarketDemandDB)
            if flower_type:
                stmt = stmt.where(MarketDemandDB.flower_type == flower_type)
            if market:
                stmt = stmt.where(MarketDemandDB.market == market)
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [MarketDemand(**_row_to_dict(r)) for r in rows]
    data = load()
    items = data["demand"]
    if flower_type:
        items = [d for d in items if d["flower_type"] == flower_type]
    if market:
        items = [d for d in items if d["market"] == market]
    return [MarketDemand(**d) for d in items]


async def async_save_demand(demand: MarketDemand) -> None:
    if _use_db():
        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    delete(MarketDemandDB).where(MarketDemandDB.id == demand.id)
                )
                session.add(_model_to_row(demand, MarketDemandDB))
        return
    data = load()
    data["demand"] = [d for d in data["demand"] if d["id"] != demand.id]
    data["demand"].append(demand.model_dump(mode="json"))
    save(data)


def list_demand(flower_type: str | None = None, market: str | None = None) -> list[MarketDemand]:
    if _use_db():
        return _run_async(async_list_demand(flower_type=flower_type, market=market))
    data = load()
    items = data["demand"]
    if flower_type:
        items = [d for d in items if d["flower_type"] == flower_type]
    if market:
        items = [d for d in items if d["market"] == market]
    return [MarketDemand(**d) for d in items]


def save_demand(demand: MarketDemand) -> None:
    if _use_db():
        _run_async(async_save_demand(demand))
        return
    data = load()
    data["demand"] = [d for d in data["demand"] if d["id"] != demand.id]
    data["demand"].append(demand.model_dump(mode="json"))
    save(data)


# =============================================================================
# SHIPMENTS
# =============================================================================

async def async_list_shipments(status: str | None = None) -> list[ColdChainShipment]:
    if _use_db():
        async with async_session() as session:
            stmt = select(ColdChainShipmentDB)
            if status:
                stmt = stmt.where(ColdChainShipmentDB.status == status)
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [ColdChainShipment(**_row_to_dict(r)) for r in rows]
    data = load()
    items = data["shipments"]
    if status:
        items = [s for s in items if s["status"] == status]
    return [ColdChainShipment(**s) for s in items]


async def async_get_shipment(shipment_id: str) -> ColdChainShipment | None:
    if _use_db():
        async with async_session() as session:
            result = await session.execute(
                select(ColdChainShipmentDB).where(ColdChainShipmentDB.id == shipment_id)
            )
            row = result.scalar_one_or_none()
            return ColdChainShipment(**_row_to_dict(row)) if row else None
    for s in load()["shipments"]:
        if s["id"] == shipment_id:
            return ColdChainShipment(**s)
    return None


async def async_save_shipment(shipment: ColdChainShipment) -> None:
    if _use_db():
        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    delete(ColdChainShipmentDB).where(ColdChainShipmentDB.id == shipment.id)
                )
                session.add(_model_to_row(shipment, ColdChainShipmentDB))
        return
    data = load()
    data["shipments"] = [s for s in data["shipments"] if s["id"] != shipment.id]
    data["shipments"].append(shipment.model_dump(mode="json"))
    save(data)


def list_shipments(status: str | None = None) -> list[ColdChainShipment]:
    if _use_db():
        return _run_async(async_list_shipments(status=status))
    data = load()
    items = data["shipments"]
    if status:
        items = [s for s in items if s["status"] == status]
    return [ColdChainShipment(**s) for s in items]


def get_shipment(shipment_id: str) -> ColdChainShipment | None:
    if _use_db():
        return _run_async(async_get_shipment(shipment_id))
    for s in load()["shipments"]:
        if s["id"] == shipment_id:
            return ColdChainShipment(**s)
    return None


def save_shipment(shipment: ColdChainShipment) -> None:
    if _use_db():
        _run_async(async_save_shipment(shipment))
        return
    data = load()
    data["shipments"] = [s for s in data["shipments"] if s["id"] != shipment.id]
    data["shipments"].append(shipment.model_dump(mode="json"))
    save(data)


# =============================================================================
# ORDERS
# =============================================================================

async def async_list_orders(status: str | None = None) -> list[BuyerOrder]:
    if _use_db():
        async with async_session() as session:
            stmt = select(BuyerOrderDB)
            if status:
                stmt = stmt.where(BuyerOrderDB.status == status)
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [BuyerOrder(**_row_to_dict(r)) for r in rows]
    data = load()
    items = data["orders"]
    if status:
        items = [o for o in items if o["status"] == status]
    return [BuyerOrder(**o) for o in items]


async def async_save_order(order: BuyerOrder) -> None:
    if _use_db():
        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    delete(BuyerOrderDB).where(BuyerOrderDB.id == order.id)
                )
                session.add(_model_to_row(order, BuyerOrderDB))
        return
    data = load()
    data["orders"] = [o for o in data["orders"] if o["id"] != order.id]
    data["orders"].append(order.model_dump(mode="json"))
    save(data)


def list_orders(status: str | None = None) -> list[BuyerOrder]:
    if _use_db():
        return _run_async(async_list_orders(status=status))
    data = load()
    items = data["orders"]
    if status:
        items = [o for o in items if o["status"] == status]
    return [BuyerOrder(**o) for o in items]


def save_order(order: BuyerOrder) -> None:
    if _use_db():
        _run_async(async_save_order(order))
        return
    data = load()
    data["orders"] = [o for o in data["orders"] if o["id"] != order.id]
    data["orders"].append(order.model_dump(mode="json"))
    save(data)


# =============================================================================
# QUALITY
# =============================================================================

async def async_list_quality(batch_id: str | None = None) -> list[QualityAssessment]:
    if _use_db():
        async with async_session() as session:
            stmt = select(QualityAssessmentDB)
            if batch_id:
                stmt = stmt.where(QualityAssessmentDB.batch_id == batch_id)
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [QualityAssessment(**_row_to_dict(r)) for r in rows]
    data = load()
    items = data["quality"]
    if batch_id:
        items = [q for q in items if q["batch_id"] == batch_id]
    return [QualityAssessment(**q) for q in items]


async def async_save_quality(qa: QualityAssessment) -> None:
    if _use_db():
        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    delete(QualityAssessmentDB).where(QualityAssessmentDB.id == qa.id)
                )
                session.add(_model_to_row(qa, QualityAssessmentDB))
        return
    data = load()
    data["quality"] = [q for q in data["quality"] if q["id"] != qa.id]
    data["quality"].append(qa.model_dump(mode="json"))
    save(data)


def list_quality(batch_id: str | None = None) -> list[QualityAssessment]:
    if _use_db():
        return _run_async(async_list_quality(batch_id=batch_id))
    data = load()
    items = data["quality"]
    if batch_id:
        items = [q for q in items if q["batch_id"] == batch_id]
    return [QualityAssessment(**q) for q in items]


def save_quality(qa: QualityAssessment) -> None:
    if _use_db():
        _run_async(async_save_quality(qa))
        return
    data = load()
    data["quality"] = [q for q in data["quality"] if q["id"] != qa.id]
    data["quality"].append(qa.model_dump(mode="json"))
    save(data)


# =============================================================================
# SIGNALS
# =============================================================================

async def async_list_signals() -> list[PriceSignal]:
    if _use_db():
        async with async_session() as session:
            result = await session.execute(select(PriceSignalDB))
            rows = result.scalars().all()
            return [PriceSignal(**_row_to_dict(r)) for r in rows]
    return [PriceSignal(**s) for s in load()["signals"]]


async def async_save_signal(signal: PriceSignal) -> None:
    if _use_db():
        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    delete(PriceSignalDB).where(PriceSignalDB.id == signal.id)
                )
                session.add(_model_to_row(signal, PriceSignalDB))
        return
    data = load()
    data["signals"] = [s for s in data["signals"] if s["id"] != signal.id]
    data["signals"].append(signal.model_dump(mode="json"))
    save(data)


def list_signals() -> list[PriceSignal]:
    if _use_db():
        return _run_async(async_list_signals())
    return [PriceSignal(**s) for s in load()["signals"]]


def save_signal(signal: PriceSignal) -> None:
    if _use_db():
        _run_async(async_save_signal(signal))
        return
    data = load()
    data["signals"] = [s for s in data["signals"] if s["id"] != signal.id]
    data["signals"].append(signal.model_dump(mode="json"))
    save(data)


# =============================================================================
# HARVEST PLANS
# =============================================================================

async def async_list_harvest_plans() -> list[HarvestPlan]:
    if _use_db():
        async with async_session() as session:
            result = await session.execute(select(HarvestPlanDB))
            rows = result.scalars().all()
            return [HarvestPlan(**_row_to_dict(r)) for r in rows]
    return [HarvestPlan(**h) for h in load()["harvest_plans"]]


async def async_save_harvest_plan(hp: HarvestPlan) -> None:
    if _use_db():
        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    delete(HarvestPlanDB).where(HarvestPlanDB.id == hp.id)
                )
                session.add(_model_to_row(hp, HarvestPlanDB))
        return
    data = load()
    data["harvest_plans"] = [h for h in data["harvest_plans"] if h["id"] != hp.id]
    data["harvest_plans"].append(hp.model_dump(mode="json"))
    save(data)


def list_harvest_plans() -> list[HarvestPlan]:
    if _use_db():
        return _run_async(async_list_harvest_plans())
    return [HarvestPlan(**h) for h in load()["harvest_plans"]]


def save_harvest_plan(hp: HarvestPlan) -> None:
    if _use_db():
        _run_async(async_save_harvest_plan(hp))
        return
    data = load()
    data["harvest_plans"] = [h for h in data["harvest_plans"] if h["id"] != hp.id]
    data["harvest_plans"].append(hp.model_dump(mode="json"))
    save(data)


# =============================================================================
# WEATHER ALERTS
# =============================================================================

async def async_list_weather_alerts() -> list[WeatherAlert]:
    if _use_db():
        async with async_session() as session:
            result = await session.execute(select(WeatherAlertDB))
            rows = result.scalars().all()
            return [WeatherAlert(**_row_to_dict(r)) for r in rows]
    return [WeatherAlert(**w) for w in load()["weather_alerts"]]


async def async_save_weather_alert(alert: WeatherAlert) -> None:
    if _use_db():
        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    delete(WeatherAlertDB).where(WeatherAlertDB.id == alert.id)
                )
                session.add(_model_to_row(alert, WeatherAlertDB))
        return
    data = load()
    data["weather_alerts"] = [w for w in data["weather_alerts"] if w["id"] != alert.id]
    data["weather_alerts"].append(alert.model_dump(mode="json"))
    save(data)


def list_weather_alerts() -> list[WeatherAlert]:
    if _use_db():
        return _run_async(async_list_weather_alerts())
    return [WeatherAlert(**w) for w in load()["weather_alerts"]]


def save_weather_alert(alert: WeatherAlert) -> None:
    if _use_db():
        _run_async(async_save_weather_alert(alert))
        return
    data = load()
    data["weather_alerts"] = [w for w in data["weather_alerts"] if w["id"] != alert.id]
    data["weather_alerts"].append(alert.model_dump(mode="json"))
    save(data)


# =============================================================================
# STATS
# =============================================================================

async def async_get_stats() -> FlowStats | None:
    if _use_db():
        async with async_session() as session:
            result = await session.execute(select(StatsDB).where(StatsDB.id == 1))
            row = result.scalar_one_or_none()
            if row:
                d = _row_to_dict(row)
                d.pop("id", None)
                return FlowStats(**d)
            return None
    data = load()
    if data.get("stats"):
        return FlowStats(**data["stats"])
    return None


async def async_save_stats(stats: FlowStats) -> None:
    if _use_db():
        async with async_session() as session:
            async with session.begin():
                await session.execute(delete(StatsDB).where(StatsDB.id == 1))
                row = StatsDB(id=1, **stats.model_dump(mode="json"))
                session.add(row)
        return
    data = load()
    data["stats"] = stats.model_dump(mode="json")
    save(data)


def get_stats() -> FlowStats | None:
    if _use_db():
        return _run_async(async_get_stats())
    data = load()
    if data.get("stats"):
        return FlowStats(**data["stats"])
    return None


def save_stats(stats: FlowStats) -> None:
    if _use_db():
        _run_async(async_save_stats(stats))
        return
    data = load()
    data["stats"] = stats.model_dump(mode="json")
    save(data)


# =============================================================================
# CLEAR ALL (for refresh)
# =============================================================================

async def async_clear_all() -> None:
    """Delete all data from all tables (DB) or reset cache (JSON)."""
    if _use_db():
        async with async_session() as session:
            async with session.begin():
                await session.execute(delete(GreenhouseDB))
                await session.execute(delete(FlowerBatchDB))
                await session.execute(delete(MarketDemandDB))
                await session.execute(delete(ColdChainShipmentDB))
                await session.execute(delete(QualityAssessmentDB))
                await session.execute(delete(BuyerOrderDB))
                await session.execute(delete(WeatherAlertDB))
                await session.execute(delete(PriceSignalDB))
                await session.execute(delete(HarvestPlanDB))
                await session.execute(delete(StatsDB))
        return
    global _cache
    _cache = None


def clear_all() -> None:
    if _use_db():
        _run_async(async_clear_all())
        return
    global _cache
    _cache = None


# =============================================================================
# BULK SAVE (for demo)
# =============================================================================

async def async_save_all(
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
    """Bulk save all data — used by demo generator."""
    if _use_db():
        async with async_session() as session:
            async with session.begin():
                if greenhouses is not None:
                    await session.execute(delete(GreenhouseDB))
                    for g in greenhouses:
                        session.add(_model_to_row(g, GreenhouseDB))
                if batches is not None:
                    await session.execute(delete(FlowerBatchDB))
                    for b in batches:
                        session.add(_model_to_row(b, FlowerBatchDB))
                if demand is not None:
                    await session.execute(delete(MarketDemandDB))
                    for d in demand:
                        session.add(_model_to_row(d, MarketDemandDB))
                if shipments is not None:
                    await session.execute(delete(ColdChainShipmentDB))
                    for s in shipments:
                        session.add(_model_to_row(s, ColdChainShipmentDB))
                if orders is not None:
                    await session.execute(delete(BuyerOrderDB))
                    for o in orders:
                        session.add(_model_to_row(o, BuyerOrderDB))
                if quality is not None:
                    await session.execute(delete(QualityAssessmentDB))
                    for q in quality:
                        session.add(_model_to_row(q, QualityAssessmentDB))
                if signals is not None:
                    await session.execute(delete(PriceSignalDB))
                    for s in signals:
                        session.add(_model_to_row(s, PriceSignalDB))
                if harvest_plans is not None:
                    await session.execute(delete(HarvestPlanDB))
                    for h in harvest_plans:
                        session.add(_model_to_row(h, HarvestPlanDB))
                if weather_alerts is not None:
                    await session.execute(delete(WeatherAlertDB))
                    for w in weather_alerts:
                        session.add(_model_to_row(w, WeatherAlertDB))
                if stats is not None:
                    await session.execute(delete(StatsDB))
                    session.add(StatsDB(id=1, **stats.model_dump(mode="json")))
        return
    # Fallback to JSON
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
    if _use_db():
        _run_async(async_save_all(
            greenhouses=greenhouses, batches=batches, demand=demand,
            shipments=shipments, orders=orders, quality=quality,
            signals=signals, harvest_plans=harvest_plans,
            weather_alerts=weather_alerts, stats=stats,
        ))
        return
    # Fallback to JSON
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
