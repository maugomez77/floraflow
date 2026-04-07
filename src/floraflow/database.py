"""PostgreSQL database layer using SQLAlchemy async."""

from __future__ import annotations

import os
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, Text

DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Convert postgres:// to postgresql+asyncpg:// for SQLAlchemy
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True) if DATABASE_URL else None
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False) if engine else None


class Base(DeclarativeBase):
    pass


# --- SQLAlchemy ORM Models ---


class GreenhouseDB(Base):
    __tablename__ = "greenhouses"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    municipality = Column(String, nullable=False)
    location_lat = Column(Float, nullable=False)
    location_lng = Column(Float, nullable=False)
    area_m2 = Column(Float, nullable=False)
    flower_types = Column(JSON, nullable=False, default=list)
    owner = Column(String, nullable=False)
    contact = Column(String, nullable=False)
    tech_level = Column(String, nullable=False, default="basic")
    created_at = Column(String, nullable=False)


class FlowerBatchDB(Base):
    __tablename__ = "flower_batches"

    id = Column(String, primary_key=True)
    greenhouse_id = Column(String, nullable=False, index=True)
    flower_type = Column(String, nullable=False, index=True)
    variety = Column(String, nullable=False)
    stems_count = Column(Integer, nullable=False)
    quality_grade = Column(String, nullable=False)
    color = Column(String, nullable=False)
    stem_length_cm = Column(Float, nullable=False)
    harvest_date = Column(String, nullable=False)
    shelf_life_days = Column(Integer, nullable=False)
    estimated_value_mxn = Column(Float, nullable=False)


class MarketDemandDB(Base):
    __tablename__ = "market_demand"

    id = Column(String, primary_key=True)
    flower_type = Column(String, nullable=False, index=True)
    market = Column(String, nullable=False, index=True)
    demand_level = Column(String, nullable=False)
    price_per_stem_mxn = Column(Float, nullable=False)
    price_trend = Column(String, nullable=False)
    date = Column(String, nullable=False)
    event_driver = Column(String, nullable=True)


class ColdChainShipmentDB(Base):
    __tablename__ = "cold_chain_shipments"

    id = Column(String, primary_key=True)
    batch_ids = Column(JSON, nullable=False, default=list)
    origin_municipality = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    status = Column(String, nullable=False, index=True)
    carrier = Column(String, nullable=False)
    truck_id = Column(String, nullable=False)
    temperature_c = Column(JSON, nullable=False, default=list)
    departure_time = Column(String, nullable=True)
    eta = Column(String, nullable=True)
    humidity_pct = Column(Float, nullable=False, default=90.0)


class QualityAssessmentDB(Base):
    __tablename__ = "quality_assessments"

    id = Column(String, primary_key=True)
    batch_id = Column(String, nullable=False, index=True)
    inspector = Column(String, nullable=False)
    stem_straightness = Column(Integer, nullable=False)
    petal_count = Column(Integer, nullable=False)
    color_intensity = Column(Integer, nullable=False)
    blemish_pct = Column(Float, nullable=False)
    vase_life_estimate_days = Column(Integer, nullable=False)
    grade_recommendation = Column(String, nullable=False)
    photo_url = Column(String, nullable=True)
    assessment_date = Column(String, nullable=False)


class BuyerOrderDB(Base):
    __tablename__ = "buyer_orders"

    id = Column(String, primary_key=True)
    buyer_name = Column(String, nullable=False)
    buyer_type = Column(String, nullable=False)
    flower_types_needed = Column(JSON, nullable=False, default=list)
    stems_needed = Column(Integer, nullable=False)
    quality_required = Column(String, nullable=False)
    delivery_date = Column(String, nullable=False)
    price_offered_mxn = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="pending", index=True)
    matched_greenhouse = Column(String, nullable=True)


class WeatherAlertDB(Base):
    __tablename__ = "weather_alerts"

    id = Column(String, primary_key=True)
    municipality = Column(String, nullable=False)
    alert_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    forecast_date = Column(String, nullable=False)
    affected_greenhouses = Column(JSON, nullable=False, default=list)


class PriceSignalDB(Base):
    __tablename__ = "price_signals"

    id = Column(String, primary_key=True)
    flower_type = Column(String, nullable=False, index=True)
    signal_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    valid_until = Column(String, nullable=False)
    priority = Column(String, nullable=False)


class HarvestPlanDB(Base):
    __tablename__ = "harvest_plans"

    id = Column(String, primary_key=True)
    greenhouse_id = Column(String, nullable=False, index=True)
    flower_type = Column(String, nullable=False)
    planned_date = Column(String, nullable=False)
    stems_target = Column(Integer, nullable=False)
    market_target = Column(String, nullable=False)
    price_target_mxn = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="planned")


class StatsDB(Base):
    __tablename__ = "stats"

    id = Column(Integer, primary_key=True, default=1)
    total_greenhouses = Column(Integer, nullable=False, default=0)
    total_area_m2 = Column(Float, nullable=False, default=0)
    active_shipments = Column(Integer, nullable=False, default=0)
    weekly_stems_shipped = Column(Integer, nullable=False, default=0)
    revenue_mtd_mxn = Column(Float, nullable=False, default=0)
    top_markets = Column(JSON, nullable=False, default=list)
    upcoming_events = Column(JSON, nullable=False, default=list)


async def init_db() -> None:
    """Create all tables if they don't exist."""
    if engine is None:
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
