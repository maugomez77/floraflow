"""Data models for FloraFlow."""

from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


def _make_id(prefix: str) -> str:
    ts = int(time.time())
    h = hashlib.md5(f"{ts}{time.monotonic_ns()}".encode()).hexdigest()[:8]
    return f"{prefix}-{ts}-{h}"


# --- Enums ---

class Municipality(str, Enum):
    VILLA_GUERRERO = "villa_guerrero"
    TENANCINGO = "tenancingo"
    COATEPEC_HARINAS = "coatepec_harinas"
    METEPEC = "metepec"
    TOLUCA = "toluca"


class FlowerType(str, Enum):
    ROSE = "rose"
    CHRYSANTHEMUM = "chrysanthemum"
    GERBERA = "gerbera"
    LILY = "lily"
    GLADIOLUS = "gladiolus"
    ALSTROEMERIA = "alstroemeria"
    CARNATION = "carnation"
    SUNFLOWER = "sunflower"


class QualityGrade(str, Enum):
    EXPORT_PREMIUM = "export_premium"
    FIRST = "first"
    SECOND = "second"
    THIRD = "third"


class Market(str, Enum):
    JAMAICA = "jamaica"
    CENTRAL_DE_ABASTO = "central_de_abasto"
    EXPORTACION = "exportacion"
    EVENTOS = "eventos"
    RETAIL = "retail"


class DemandLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PEAK = "peak"


class PriceTrend(str, Enum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class ShipmentStatus(str, Enum):
    HARVESTING = "harvesting"
    COOLING = "cooling"
    LOADING = "loading"
    IN_TRANSIT = "in_transit"
    AT_MARKET = "at_market"
    DELIVERED = "delivered"


class Destination(str, Enum):
    CDMX_JAMAICA = "cdmx_jamaica"
    CDMX_CENTRAL_ABASTO = "cdmx_central_abasto"
    CDMX_POLANCO = "cdmx_polanco"
    GUADALAJARA = "guadalajara"
    MONTERREY = "monterrey"
    EXPORT_US = "export_us"


class BuyerType(str, Enum):
    WHOLESALER = "wholesaler"
    RETAILER = "retailer"
    EVENT_PLANNER = "event_planner"
    EXPORTER = "exporter"
    HOTEL_CHAIN = "hotel_chain"


class OrderStatus(str, Enum):
    PENDING = "pending"
    MATCHED = "matched"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"


class AlertType(str, Enum):
    FROST = "frost"
    HAIL = "hail"
    RAIN = "rain"
    HEAT = "heat"
    WIND = "wind"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SignalType(str, Enum):
    PRICE_SPIKE = "price_spike"
    DEMAND_SURGE = "demand_surge"
    OVERSUPPLY = "oversupply"
    EVENT_PREMIUM = "event_premium"
    SEASONAL_LOW = "seasonal_low"


class TechLevel(str, Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class HarvestStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EventDriver(str, Enum):
    VALENTINES = "valentines"
    MOTHERS_DAY = "mothers_day"
    DIA_MUERTOS = "dia_muertos"
    XMAS = "xmas"
    WEDDINGS = "weddings"
    NONE = "none"


# --- Models ---

class Greenhouse(BaseModel):
    id: str = Field(default_factory=lambda: _make_id("gh"))
    name: str
    municipality: Municipality
    location_lat: float
    location_lng: float
    area_m2: float
    flower_types: list[str]
    owner: str
    contact: str
    tech_level: TechLevel = TechLevel.BASIC
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class FlowerBatch(BaseModel):
    id: str = Field(default_factory=lambda: _make_id("fb"))
    greenhouse_id: str
    flower_type: FlowerType
    variety: str
    stems_count: int
    quality_grade: QualityGrade
    color: str
    stem_length_cm: float
    harvest_date: str
    shelf_life_days: int
    estimated_value_mxn: float


class MarketDemand(BaseModel):
    id: str = Field(default_factory=lambda: _make_id("md"))
    flower_type: FlowerType
    market: Market
    demand_level: DemandLevel
    price_per_stem_mxn: float
    price_trend: PriceTrend
    date: str
    event_driver: Optional[str] = None


class ColdChainShipment(BaseModel):
    id: str = Field(default_factory=lambda: _make_id("cc"))
    batch_ids: list[str]
    origin_municipality: Municipality
    destination: Destination
    status: ShipmentStatus
    carrier: str
    truck_id: str
    temperature_c: list[float]
    departure_time: Optional[str] = None
    eta: Optional[str] = None
    humidity_pct: float = 90.0


class QualityAssessment(BaseModel):
    id: str = Field(default_factory=lambda: _make_id("qa"))
    batch_id: str
    inspector: str
    stem_straightness: int  # 1-10
    petal_count: int
    color_intensity: int  # 1-10
    blemish_pct: float
    vase_life_estimate_days: int
    grade_recommendation: QualityGrade
    photo_url: Optional[str] = None
    assessment_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class BuyerOrder(BaseModel):
    id: str = Field(default_factory=lambda: _make_id("bo"))
    buyer_name: str
    buyer_type: BuyerType
    flower_types_needed: list[str]
    stems_needed: int
    quality_required: QualityGrade
    delivery_date: str
    price_offered_mxn: float
    status: OrderStatus = OrderStatus.PENDING
    matched_greenhouse: Optional[str] = None


class WeatherAlert(BaseModel):
    id: str = Field(default_factory=lambda: _make_id("wa"))
    municipality: Municipality
    alert_type: AlertType
    severity: Severity
    description: str
    forecast_date: str
    affected_greenhouses: list[str]


class PriceSignal(BaseModel):
    id: str = Field(default_factory=lambda: _make_id("ps"))
    flower_type: FlowerType
    signal_type: SignalType
    description: str
    recommended_action: str
    valid_until: str
    priority: Severity


class HarvestPlan(BaseModel):
    id: str = Field(default_factory=lambda: _make_id("hp"))
    greenhouse_id: str
    flower_type: FlowerType
    planned_date: str
    stems_target: int
    market_target: Market
    price_target_mxn: float
    status: HarvestStatus = HarvestStatus.PLANNED


class FlowStats(BaseModel):
    total_greenhouses: int = 0
    total_area_m2: float = 0
    active_shipments: int = 0
    weekly_stems_shipped: int = 0
    revenue_mtd_mxn: float = 0
    top_markets: list[str] = Field(default_factory=list)
    upcoming_events: list[str] = Field(default_factory=list)
