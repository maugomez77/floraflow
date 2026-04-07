"""Demo data generator for FloraFlow — realistic Estado de Mexico floriculture data."""

from __future__ import annotations

import asyncio
import random
from datetime import datetime, timedelta, timezone

from .models import (
    AlertType,
    BuyerOrder,
    BuyerType,
    ColdChainShipment,
    DemandLevel,
    Destination,
    EventDriver,
    FlowerBatch,
    FlowerType,
    FlowStats,
    Greenhouse,
    HarvestPlan,
    HarvestStatus,
    Market,
    MarketDemand,
    Municipality,
    OrderStatus,
    PriceSignal,
    PriceTrend,
    QualityAssessment,
    QualityGrade,
    Severity,
    ShipmentStatus,
    SignalType,
    TechLevel,
    WeatherAlert,
)
from . import store

# --- Municipality coordinates ---
COORDS = {
    Municipality.VILLA_GUERRERO: (18.9614, -99.6353),
    Municipality.TENANCINGO: (18.9603, -99.5904),
    Municipality.COATEPEC_HARINAS: (18.9272, -99.7558),
    Municipality.METEPEC: (19.2550, -99.6040),
    Municipality.TOLUCA: (19.2826, -99.6557),
}


def _jitter(lat: float, lng: float) -> tuple[float, float]:
    return (lat + random.uniform(-0.02, 0.02), lng + random.uniform(-0.02, 0.02))


def _date_offset(days: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).strftime("%Y-%m-%d")


def _datetime_offset(hours: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


# ---------- Greenhouses ----------

def _generate_greenhouses() -> list[Greenhouse]:
    specs = [
        # Villa Guerrero (6) — Mexico's flower capital
        ("Invernadero Rosas del Valle", Municipality.VILLA_GUERRERO, 12000, ["rose", "chrysanthemum"], "Jose Luis Garcia Lopez", "961-555-0101", TechLevel.ADVANCED),
        ("Flores Don Miguel", Municipality.VILLA_GUERRERO, 8500, ["rose"], "Miguel Angel Hernandez", "961-555-0102", TechLevel.INTERMEDIATE),
        ("Viveros La Esperanza", Municipality.VILLA_GUERRERO, 10000, ["rose", "gerbera", "lily"], "Rosa Maria Hernandez", "961-555-0103", TechLevel.ADVANCED),
        ("Crisantemos Villa Guerrero", Municipality.VILLA_GUERRERO, 7000, ["chrysanthemum"], "Fernando Ramirez Torres", "961-555-0104", TechLevel.INTERMEDIATE),
        ("Rosas Premium del Sur", Municipality.VILLA_GUERRERO, 15000, ["rose", "alstroemeria"], "Patricia Gomez Diaz", "961-555-0105", TechLevel.ADVANCED),
        ("Flores Silvestres VG", Municipality.VILLA_GUERRERO, 4500, ["carnation", "sunflower"], "Carlos Mendoza Ruiz", "961-555-0106", TechLevel.BASIC),
        # Tenancingo (4)
        ("Gladiolos El Cerro", Municipality.TENANCINGO, 6000, ["gladiolus"], "Juan Pablo Martinez", "961-555-0201", TechLevel.INTERMEDIATE),
        ("Invernadero Tenancingo Flores", Municipality.TENANCINGO, 5000, ["gladiolus", "chrysanthemum"], "Maria Elena Vargas", "961-555-0202", TechLevel.BASIC),
        ("Flores Finas de Tenancingo", Municipality.TENANCINGO, 3500, ["rose", "carnation"], "Alberto Sanchez Luna", "961-555-0203", TechLevel.INTERMEDIATE),
        ("Jardines del Valle", Municipality.TENANCINGO, 4000, ["lily", "alstroemeria"], "Guadalupe Torres Mendez", "961-555-0204", TechLevel.BASIC),
        # Coatepec Harinas (3)
        ("Gerberas de Coatepec", Municipality.COATEPEC_HARINAS, 5500, ["gerbera"], "Roberto Flores Jimenez", "961-555-0301", TechLevel.INTERMEDIATE),
        ("Flores Exoticas Coatepec", Municipality.COATEPEC_HARINAS, 3000, ["gerbera", "lily", "sunflower"], "Ana Lucia Perez", "961-555-0302", TechLevel.BASIC),
        ("Vivero Premium Harinas", Municipality.COATEPEC_HARINAS, 4000, ["rose", "gerbera"], "Diego Castillo Ortiz", "961-555-0303", TechLevel.INTERMEDIATE),
        # Metepec (1)
        ("Arreglos Florales Metepec", Municipality.METEPEC, 2000, ["rose", "lily", "alstroemeria"], "Mariana Delgado Rivera", "961-555-0401", TechLevel.ADVANCED),
        # Toluca (1)
        ("Hub Logistico Toluca Flores", Municipality.TOLUCA, 3000, ["rose", "chrysanthemum", "gladiolus"], "Ernesto Reyes Morales", "961-555-0501", TechLevel.ADVANCED),
    ]
    greenhouses = []
    for name, muni, area, flowers, owner, contact, tech in specs:
        lat, lng = _jitter(*COORDS[muni])
        greenhouses.append(Greenhouse(
            name=name, municipality=muni,
            location_lat=round(lat, 4), location_lng=round(lng, 4),
            area_m2=area, flower_types=flowers, owner=owner, contact=contact,
            tech_level=tech,
        ))
    return greenhouses


# ---------- Batches ----------

def _generate_batches(greenhouses: list[Greenhouse]) -> list[FlowerBatch]:
    rose_colors = ["rojo", "blanco", "rosa", "amarillo"]
    chrysanthemum_colors = ["blanco", "amarillo", "morado"]
    gerbera_colors = ["naranja", "rojo", "rosa", "amarillo"]
    gladiolus_colors = ["blanco", "rojo"]

    batches = []
    gh_map = {g.id: g for g in greenhouses}

    def _add(gh_id, ftype, variety, count, grade, color, stem_len, price_per):
        batches.append(FlowerBatch(
            greenhouse_id=gh_id, flower_type=ftype, variety=variety,
            stems_count=count, quality_grade=grade, color=color,
            stem_length_cm=stem_len,
            harvest_date=_date_offset(random.randint(-3, 7)),
            shelf_life_days=random.randint(5, 14),
            estimated_value_mxn=round(count * price_per, 2),
        ))

    for gh in greenhouses:
        for ft in gh.flower_types:
            num = random.randint(2, 5) if ft == "rose" else random.randint(1, 3)
            for _ in range(num):
                if ft == "rose":
                    color = random.choice(rose_colors)
                    grade = random.choice([QualityGrade.EXPORT_PREMIUM, QualityGrade.FIRST, QualityGrade.FIRST, QualityGrade.SECOND])
                    _add(gh.id, FlowerType.ROSE, f"Rosa {color.title()}", random.randint(500, 5000), grade, color, round(random.uniform(60, 80), 1), round(random.uniform(3, 8), 2))
                elif ft == "chrysanthemum":
                    color = random.choice(chrysanthemum_colors)
                    _add(gh.id, FlowerType.CHRYSANTHEMUM, f"Crisantemo {color.title()}", random.randint(800, 4000), random.choice([QualityGrade.FIRST, QualityGrade.SECOND]), color, round(random.uniform(40, 60), 1), round(random.uniform(2, 5), 2))
                elif ft == "gerbera":
                    color = random.choice(gerbera_colors)
                    _add(gh.id, FlowerType.GERBERA, f"Gerbera {color.title()}", random.randint(300, 2000), random.choice([QualityGrade.FIRST, QualityGrade.SECOND]), color, round(random.uniform(35, 50), 1), round(random.uniform(4, 7), 2))
                elif ft == "gladiolus":
                    color = random.choice(gladiolus_colors)
                    _add(gh.id, FlowerType.GLADIOLUS, f"Gladiola {color.title()}", random.randint(500, 3000), random.choice([QualityGrade.FIRST, QualityGrade.SECOND, QualityGrade.THIRD]), color, round(random.uniform(80, 120), 1), round(random.uniform(2, 4), 2))
                elif ft == "lily":
                    _add(gh.id, FlowerType.LILY, "Lilium Oriental", random.randint(200, 1000), random.choice([QualityGrade.EXPORT_PREMIUM, QualityGrade.FIRST]), "blanco", round(random.uniform(50, 70), 1), round(random.uniform(8, 15), 2))
                elif ft == "alstroemeria":
                    _add(gh.id, FlowerType.ALSTROEMERIA, "Alstroemeria Mix", random.randint(400, 1500), QualityGrade.FIRST, random.choice(["rosa", "naranja", "morado"]), round(random.uniform(40, 55), 1), round(random.uniform(3, 6), 2))
                elif ft == "carnation":
                    _add(gh.id, FlowerType.CARNATION, "Clavel Estandar", random.randint(1000, 5000), random.choice([QualityGrade.FIRST, QualityGrade.SECOND, QualityGrade.THIRD]), random.choice(["rojo", "blanco", "rosa"]), round(random.uniform(45, 60), 1), round(random.uniform(1.5, 3), 2))
                elif ft == "sunflower":
                    _add(gh.id, FlowerType.SUNFLOWER, "Girasol Mexicano", random.randint(200, 800), QualityGrade.FIRST, "amarillo", round(random.uniform(60, 90), 1), round(random.uniform(5, 10), 2))
                if len(batches) >= 50:
                    return batches
    return batches[:50]


# ---------- Market Demand ----------

def _generate_demand() -> list[MarketDemand]:
    now = datetime.now(timezone.utc)
    month = now.month
    items = []

    # Determine current event driver
    if month == 2:
        event = EventDriver.VALENTINES
    elif month == 5:
        event = EventDriver.MOTHERS_DAY
    elif month in (10, 11):
        event = EventDriver.DIA_MUERTOS
    elif month == 12:
        event = EventDriver.XMAS
    elif month in (4, 5, 6):
        event = EventDriver.WEDDINGS
    else:
        event = EventDriver.NONE

    flower_base_prices = {
        FlowerType.ROSE: 5.0,
        FlowerType.CHRYSANTHEMUM: 3.0,
        FlowerType.GERBERA: 5.0,
        FlowerType.LILY: 10.0,
        FlowerType.GLADIOLUS: 3.0,
        FlowerType.ALSTROEMERIA: 4.0,
        FlowerType.CARNATION: 2.0,
        FlowerType.SUNFLOWER: 7.0,
    }

    for ft in FlowerType:
        base = flower_base_prices[ft]
        for market in [Market.JAMAICA, Market.CENTRAL_DE_ABASTO, Market.EXPORTACION, Market.EVENTOS, Market.RETAIL]:
            multiplier = 1.0
            demand = DemandLevel.MEDIUM
            trend = PriceTrend.STABLE

            # Market premiums
            if market == Market.EXPORTACION:
                multiplier *= 1.8
            elif market == Market.EVENTOS:
                multiplier *= 1.5
            elif market == Market.RETAIL:
                multiplier *= 1.3

            # Event premiums
            if event == EventDriver.VALENTINES and ft == FlowerType.ROSE:
                multiplier *= random.uniform(3, 5)
                demand = DemandLevel.PEAK
                trend = PriceTrend.UP
            elif event == EventDriver.MOTHERS_DAY:
                multiplier *= random.uniform(2, 4)
                demand = DemandLevel.PEAK
                trend = PriceTrend.UP
            elif event == EventDriver.DIA_MUERTOS and ft == FlowerType.CHRYSANTHEMUM:
                multiplier *= random.uniform(2.5, 4)
                demand = DemandLevel.PEAK
                trend = PriceTrend.UP
            elif event == EventDriver.XMAS and ft == FlowerType.ROSE:
                multiplier *= random.uniform(1.5, 2.5)
                demand = DemandLevel.HIGH
                trend = PriceTrend.UP
            elif event == EventDriver.WEDDINGS:
                if ft in (FlowerType.ROSE, FlowerType.LILY, FlowerType.ALSTROEMERIA):
                    multiplier *= random.uniform(1.3, 2.0)
                    demand = DemandLevel.HIGH
                    trend = PriceTrend.UP

            price = round(base * multiplier, 2)
            items.append(MarketDemand(
                flower_type=ft, market=market, demand_level=demand,
                price_per_stem_mxn=price, price_trend=trend,
                date=_date_offset(0), event_driver=event.value,
            ))
    return items


# ---------- Shipments ----------

def _generate_shipments(batches: list[FlowerBatch]) -> list[ColdChainShipment]:
    batch_ids_pool = [b.id for b in batches[:20]]
    carriers = ["Transportes Refrigerados del Sur", "Frio Express Toluca", "FloresLog CDMX", "Cadena Fria MX"]

    specs = [
        (Destination.CDMX_JAMAICA, Municipality.VILLA_GUERRERO, ShipmentStatus.IN_TRANSIT),
        (Destination.CDMX_JAMAICA, Municipality.TENANCINGO, ShipmentStatus.AT_MARKET),
        (Destination.CDMX_JAMAICA, Municipality.VILLA_GUERRERO, ShipmentStatus.LOADING),
        (Destination.CDMX_CENTRAL_ABASTO, Municipality.VILLA_GUERRERO, ShipmentStatus.IN_TRANSIT),
        (Destination.CDMX_CENTRAL_ABASTO, Municipality.COATEPEC_HARINAS, ShipmentStatus.DELIVERED),
        (Destination.GUADALAJARA, Municipality.VILLA_GUERRERO, ShipmentStatus.COOLING),
    ]
    shipments = []
    for dest, origin, status in specs:
        # Temperature readings: target 2-4C, slight variations
        temps = [round(random.uniform(2.0, 4.5), 1) for _ in range(random.randint(4, 10))]
        if random.random() < 0.15:  # 15% chance of temp spike
            temps.append(round(random.uniform(6, 9), 1))
        used_batches = random.sample(batch_ids_pool, min(random.randint(2, 5), len(batch_ids_pool)))
        shipments.append(ColdChainShipment(
            batch_ids=used_batches, origin_municipality=origin, destination=dest,
            status=status, carrier=random.choice(carriers),
            truck_id=f"TR-{random.randint(100,999)}",
            temperature_c=temps,
            departure_time=_datetime_offset(random.randint(-6, -1)),
            eta=_datetime_offset(random.randint(1, 8)),
            humidity_pct=round(random.uniform(85, 95), 1),
        ))
    return shipments


# ---------- Orders ----------

def _generate_orders(greenhouses: list[Greenhouse]) -> list[BuyerOrder]:
    specs = [
        ("Flores Mayoreo Jamaica", BuyerType.WHOLESALER, ["rose", "chrysanthemum"], 10000, QualityGrade.SECOND, 45000, OrderStatus.CONFIRMED),
        ("Flores Mayoreo Jamaica #2", BuyerType.WHOLESALER, ["gladiolus", "carnation"], 8000, QualityGrade.SECOND, 20000, OrderStatus.PENDING),
        ("Liverpool Floral CDMX", BuyerType.RETAILER, ["rose", "lily"], 3000, QualityGrade.FIRST, 35000, OrderStatus.MATCHED),
        ("Palacio de Hierro Flores", BuyerType.RETAILER, ["rose", "gerbera", "alstroemeria"], 2000, QualityGrade.FIRST, 22000, OrderStatus.CONFIRMED),
        ("Eventos Elegantes SA", BuyerType.EVENT_PLANNER, ["rose", "lily", "alstroemeria"], 5000, QualityGrade.EXPORT_PREMIUM, 65000, OrderStatus.PENDING),
        ("Bodas Premium CDMX", BuyerType.EVENT_PLANNER, ["rose", "gerbera"], 3000, QualityGrade.FIRST, 28000, OrderStatus.SHIPPED),
        ("Hilton CDMX Reforma", BuyerType.HOTEL_CHAIN, ["rose", "lily"], 1500, QualityGrade.EXPORT_PREMIUM, 25000, OrderStatus.CONFIRMED),
        ("US Flowers Import Co.", BuyerType.EXPORTER, ["rose"], 20000, QualityGrade.EXPORT_PREMIUM, 160000, OrderStatus.PENDING),
    ]
    orders = []
    gh_names = [g.name for g in greenhouses]
    for name, btype, flowers, stems, grade, price, status in specs:
        orders.append(BuyerOrder(
            buyer_name=name, buyer_type=btype, flower_types_needed=flowers,
            stems_needed=stems, quality_required=grade,
            delivery_date=_date_offset(random.randint(1, 14)),
            price_offered_mxn=price, status=status,
            matched_greenhouse=random.choice(gh_names) if status != OrderStatus.PENDING else None,
        ))
    return orders


# ---------- Quality Assessments ----------

def _generate_quality(batches: list[FlowerBatch]) -> list[QualityAssessment]:
    inspectors = ["Ing. Sofia Castillo", "Tec. Pedro Navarro", "Ing. Laura Vega", "Tec. Ricardo Fuentes"]
    assessments = []
    for batch in random.sample(batches, min(10, len(batches))):
        straightness = random.randint(5, 10)
        color_int = random.randint(5, 10)
        blemish = round(random.uniform(0, 15), 1)
        vase_life = random.randint(5, 14)

        # Grade recommendation based on quality
        score = straightness + color_int - blemish / 2
        if score > 17:
            grade = QualityGrade.EXPORT_PREMIUM
        elif score > 13:
            grade = QualityGrade.FIRST
        elif score > 9:
            grade = QualityGrade.SECOND
        else:
            grade = QualityGrade.THIRD

        assessments.append(QualityAssessment(
            batch_id=batch.id, inspector=random.choice(inspectors),
            stem_straightness=straightness,
            petal_count=random.randint(20, 60),
            color_intensity=color_int, blemish_pct=blemish,
            vase_life_estimate_days=vase_life,
            grade_recommendation=grade,
        ))
    return assessments


# ---------- Price Signals ----------

def _generate_signals() -> list[PriceSignal]:
    now = datetime.now(timezone.utc)
    month = now.month
    signals = [
        PriceSignal(
            flower_type=FlowerType.ROSE, signal_type=SignalType.EVENT_PREMIUM,
            description="Temporada de bodas activa en CDMX — demanda alta de rosas rojas y blancas",
            recommended_action="Priorizar corte de rosas de primera calidad para mercado de eventos",
            valid_until=_date_offset(30), priority=Severity.HIGH,
        ),
        PriceSignal(
            flower_type=FlowerType.CHRYSANTHEMUM, signal_type=SignalType.SEASONAL_LOW,
            description="Demanda baja de crisantemos fuera de temporada de Dia de Muertos",
            recommended_action="Reducir produccion de crisantemos, diversificar a gerberas",
            valid_until=_date_offset(60), priority=Severity.MEDIUM,
        ),
        PriceSignal(
            flower_type=FlowerType.GERBERA, signal_type=SignalType.DEMAND_SURGE,
            description="Gerberas trending en arreglos modernos — mercado retail en crecimiento",
            recommended_action="Incrementar produccion de gerberas de colores vibrantes",
            valid_until=_date_offset(45), priority=Severity.HIGH,
        ),
        PriceSignal(
            flower_type=FlowerType.ROSE, signal_type=SignalType.PRICE_SPIKE,
            description="Precio de rosas de exportacion sube 15% por demanda USA pre-Mother's Day",
            recommended_action="Desviar lotes export_premium a canal de exportacion",
            valid_until=_date_offset(20), priority=Severity.CRITICAL,
        ),
        PriceSignal(
            flower_type=FlowerType.GLADIOLUS, signal_type=SignalType.OVERSUPPLY,
            description="Exceso de gladiolas en Central de Abasto — precios deprimidos",
            recommended_action="Retrasar cosecha 3-5 dias o buscar mercados alternativos (Guadalajara)",
            valid_until=_date_offset(10), priority=Severity.MEDIUM,
        ),
        PriceSignal(
            flower_type=FlowerType.LILY, signal_type=SignalType.EVENT_PREMIUM,
            description="Liliums premium demandados por hoteles 5 estrellas en CDMX Polanco",
            recommended_action="Destinar lotes de lilium oriental a canal hotel_chain",
            valid_until=_date_offset(30), priority=Severity.HIGH,
        ),
    ]
    return signals


# ---------- Harvest Plans ----------

def _generate_harvest_plans(greenhouses: list[Greenhouse]) -> list[HarvestPlan]:
    plans = []
    rose_ghs = [g for g in greenhouses if "rose" in g.flower_types]
    others = [g for g in greenhouses if "rose" not in g.flower_types]

    for i, gh in enumerate(rose_ghs[:3]):
        plans.append(HarvestPlan(
            greenhouse_id=gh.id, flower_type=FlowerType.ROSE,
            planned_date=_date_offset(i + 1), stems_target=random.randint(3000, 8000),
            market_target=random.choice([Market.JAMAICA, Market.EXPORTACION, Market.EVENTOS]),
            price_target_mxn=round(random.uniform(4.5, 7.5), 2),
            status=HarvestStatus.PLANNED if i > 0 else HarvestStatus.IN_PROGRESS,
        ))

    for gh in others[:2]:
        ft = FlowerType(gh.flower_types[0]) if gh.flower_types else FlowerType.CHRYSANTHEMUM
        plans.append(HarvestPlan(
            greenhouse_id=gh.id, flower_type=ft,
            planned_date=_date_offset(random.randint(2, 7)),
            stems_target=random.randint(2000, 5000),
            market_target=Market.JAMAICA,
            price_target_mxn=round(random.uniform(2.5, 5.0), 2),
        ))
    return plans


# ---------- Weather Alerts ----------

def _generate_weather_alerts(greenhouses: list[Greenhouse]) -> list[WeatherAlert]:
    vg_ghs = [g.name for g in greenhouses if g.municipality == Municipality.VILLA_GUERRERO]
    ten_ghs = [g.name for g in greenhouses if g.municipality == Municipality.TENANCINGO]
    return [
        WeatherAlert(
            municipality=Municipality.VILLA_GUERRERO,
            alert_type=AlertType.FROST,
            severity=Severity.HIGH,
            description="Pronostico de helada nocturna (1-2C) — cubrir invernaderos y activar calefaccion",
            forecast_date=_date_offset(1),
            affected_greenhouses=vg_ghs[:3],
        ),
        WeatherAlert(
            municipality=Municipality.TENANCINGO,
            alert_type=AlertType.HAIL,
            severity=Severity.MEDIUM,
            description="Posible granizo en la tarde — proteger cultivos expuestos",
            forecast_date=_date_offset(2),
            affected_greenhouses=ten_ghs[:2],
        ),
    ]


# ---------- Stats ----------

def _generate_stats(greenhouses, batches, shipments) -> FlowStats:
    total_area = sum(g.area_m2 for g in greenhouses)
    active = len([s for s in shipments if s.status in (ShipmentStatus.IN_TRANSIT, ShipmentStatus.LOADING, ShipmentStatus.COOLING)])
    total_stems = sum(b.stems_count for b in batches)
    revenue = sum(b.estimated_value_mxn for b in batches)

    now = datetime.now(timezone.utc)
    month = now.month
    events = []
    if month <= 2:
        events.append("San Valentin (14 Feb) — Pico de rosas")
    if month <= 5:
        events.append("Dia de las Madres (10 May) — Pico total")
    if month <= 6:
        events.append("Temporada de bodas (Abr-Jun)")
    if month <= 11:
        events.append("Dia de Muertos (1-2 Nov) — Crisantemos")
    if month <= 12:
        events.append("Navidad (Dic) — Rosas y nochebuenas")

    return FlowStats(
        total_greenhouses=len(greenhouses),
        total_area_m2=total_area,
        active_shipments=active,
        weekly_stems_shipped=total_stems,
        revenue_mtd_mxn=round(revenue, 2),
        top_markets=["Mercado de Jamaica", "Central de Abasto", "Exportacion USA"],
        upcoming_events=events[:3],
    )


# ---------- DuckDuckGo + Haiku research ----------

async def _research_prices() -> str:
    """Fetch current flower prices via DuckDuckGo + Haiku."""
    try:
        from ddgs import DDGS
        ddg = DDGS()
        results = ddg.text("precios flores mayoreo Mexico City Jamaica 2026", max_results=5)
        snippets = "\n".join(r.get("body", "") for r in results if r.get("body"))
        if not snippets:
            return ""

        import anthropic
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=500,
            messages=[{"role": "user", "content": f"Analiza estos datos sobre precios de flores en Mexico y resume los precios actuales por tipo de flor en MXN. Datos:\n{snippets}"}],
        )
        return resp.content[0].text
    except Exception:
        return ""


async def _research_events() -> str:
    """Fetch upcoming events driving flower demand."""
    try:
        from ddgs import DDGS
        ddg = DDGS()
        results = ddg.text("eventos floricultura Estado Mexico 2026 demanda flores", max_results=5)
        snippets = "\n".join(r.get("body", "") for r in results if r.get("body"))
        if not snippets:
            return ""

        import anthropic
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=500,
            messages=[{"role": "user", "content": f"Identifica eventos proximos que impacten la demanda de flores en Mexico. Datos:\n{snippets}"}],
        )
        return resp.content[0].text
    except Exception:
        return ""


# ---------- Main generator ----------

async def generate_demo_data() -> dict:
    """Generate all demo data and persist to store."""
    greenhouses = _generate_greenhouses()
    batches = _generate_batches(greenhouses)
    demand = _generate_demand()
    shipments = _generate_shipments(batches)
    orders = _generate_orders(greenhouses)
    quality = _generate_quality(batches)
    signals = _generate_signals()
    harvest_plans = _generate_harvest_plans(greenhouses)
    weather_alerts = _generate_weather_alerts(greenhouses)
    stats = _generate_stats(greenhouses, batches, shipments)

    # Run async research in background
    price_info, event_info = await asyncio.gather(
        _research_prices(),
        _research_events(),
    )

    store.save_all(
        greenhouses=greenhouses,
        batches=batches,
        demand=demand,
        shipments=shipments,
        orders=orders,
        quality=quality,
        signals=signals,
        harvest_plans=harvest_plans,
        weather_alerts=weather_alerts,
        stats=stats,
    )

    return {
        "greenhouses": len(greenhouses),
        "batches": len(batches),
        "demand": len(demand),
        "shipments": len(shipments),
        "orders": len(orders),
        "quality": len(quality),
        "signals": len(signals),
        "harvest_plans": len(harvest_plans),
        "weather_alerts": len(weather_alerts),
        "research_prices": price_info[:200] if price_info else "Sin datos en tiempo real",
        "research_events": event_info[:200] if event_info else "Sin datos en tiempo real",
    }
