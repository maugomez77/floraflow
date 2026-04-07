"""CLI for FloraFlow — Beautiful floriculture dashboard."""

from __future__ import annotations

import asyncio
from typing import Optional

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import store
from .models import (
    DemandLevel,
    OrderStatus,
    PriceTrend,
    QualityGrade,
    Severity,
    ShipmentStatus,
    SignalType,
)

app = typer.Typer(
    name="floraflow",
    help="FloraFlow — AI-powered floriculture revenue optimization for Estado de Mexico",
    no_args_is_help=True,
)
console = Console()


# --- Helpers ---

def _demand_color(level: str) -> str:
    return {"low": "dim", "medium": "yellow", "high": "green", "peak": "bold red"}.get(level, "white")


def _trend_icon(trend: str) -> str:
    return {"up": "[green]UP[/green]", "down": "[red]DOWN[/red]", "stable": "[yellow]STABLE[/yellow]"}.get(trend, trend)


def _severity_badge(sev: str) -> str:
    return {
        "low": "[dim]LOW[/dim]",
        "medium": "[yellow]MEDIUM[/yellow]",
        "high": "[bold yellow]HIGH[/bold yellow]",
        "critical": "[bold red]CRITICAL[/bold red]",
    }.get(sev, sev)


def _shipment_badge(status: str) -> str:
    colors = {
        "harvesting": "magenta",
        "cooling": "cyan",
        "loading": "yellow",
        "in_transit": "blue",
        "at_market": "green",
        "delivered": "bold green",
    }
    c = colors.get(status, "white")
    return f"[{c}]{status.upper().replace('_', ' ')}[/{c}]"


def _order_badge(status: str) -> str:
    colors = {
        "pending": "yellow",
        "matched": "cyan",
        "confirmed": "blue",
        "shipped": "magenta",
        "delivered": "bold green",
    }
    c = colors.get(status, "white")
    return f"[{c}]{status.upper()}[/{c}]"


def _grade_badge(grade: str) -> str:
    colors = {
        "export_premium": "bold green",
        "first": "green",
        "second": "yellow",
        "third": "dim",
    }
    c = colors.get(grade, "white")
    label = grade.replace("_", " ").title()
    return f"[{c}]{label}[/{c}]"


def _signal_badge(sig: str) -> str:
    colors = {
        "price_spike": "bold red",
        "demand_surge": "bold green",
        "oversupply": "yellow",
        "event_premium": "bold magenta",
        "seasonal_low": "dim",
    }
    c = colors.get(sig, "white")
    return f"[{c}]{sig.replace('_', ' ').upper()}[/{c}]"


def _mxn(value: float) -> str:
    return f"${value:,.2f} MXN"


# --- Commands ---

@app.command()
def greenhouses():
    """List all registered greenhouses."""
    items = store.list_greenhouses()
    if not items:
        console.print("[yellow]No greenhouses found. Run [bold]floraflow demo[/bold] first.[/yellow]")
        return

    table = Table(title="Invernaderos Registrados", box=box.ROUNDED, show_lines=True)
    table.add_column("Name", style="bold cyan", max_width=30)
    table.add_column("Municipality", style="green")
    table.add_column("Area m2", justify="right")
    table.add_column("Flowers", style="magenta")
    table.add_column("Owner", style="white")
    table.add_column("Tech", style="yellow")

    for g in items:
        table.add_row(
            g.name,
            g.municipality.value.replace("_", " ").title(),
            f"{g.area_m2:,.0f}",
            ", ".join(g.flower_types),
            g.owner,
            g.tech_level.value.upper(),
        )
    console.print(table)
    console.print(f"\n[dim]Total: {len(items)} greenhouses | {sum(g.area_m2 for g in items):,.0f} m2[/dim]")


@app.command()
def batches(
    greenhouse: Optional[str] = typer.Option(None, "--greenhouse", "-g", help="Filter by greenhouse name"),
    flower: Optional[str] = typer.Option(None, "--flower", "-f", help="Filter by flower type"),
):
    """List flower batches with quality and value."""
    # Resolve greenhouse name to ID
    gh_id = None
    if greenhouse:
        for g in store.list_greenhouses():
            if greenhouse.lower() in g.name.lower():
                gh_id = g.id
                break
        if not gh_id:
            console.print(f"[red]Greenhouse '{greenhouse}' not found.[/red]")
            return

    items = store.list_batches(greenhouse_id=gh_id, flower_type=flower)
    if not items:
        console.print("[yellow]No batches found. Run [bold]floraflow demo[/bold] first.[/yellow]")
        return

    table = Table(title="Lotes de Flores", box=box.ROUNDED, show_lines=True)
    table.add_column("ID", style="dim", max_width=20)
    table.add_column("Flower", style="bold magenta")
    table.add_column("Variety", style="cyan")
    table.add_column("Stems", justify="right", style="green")
    table.add_column("Grade")
    table.add_column("Color", style="yellow")
    table.add_column("Stem cm", justify="right")
    table.add_column("Harvest", style="dim")
    table.add_column("Value", justify="right", style="bold green")

    total_value = 0.0
    total_stems = 0
    for b in items:
        total_value += b.estimated_value_mxn
        total_stems += b.stems_count
        table.add_row(
            b.id[:18] + "...",
            b.flower_type.value.title(),
            b.variety,
            f"{b.stems_count:,}",
            _grade_badge(b.quality_grade.value),
            b.color.title(),
            f"{b.stem_length_cm:.0f}",
            b.harvest_date,
            _mxn(b.estimated_value_mxn),
        )
    console.print(table)
    console.print(f"\n[dim]Total: {len(items)} batches | {total_stems:,} stems | {_mxn(total_value)}[/dim]")


@app.command()
def demand(
    flower: Optional[str] = typer.Option(None, "--flower", "-f", help="Filter by flower type"),
):
    """Show market demand with event premiums."""
    items = store.list_demand(flower_type=flower)
    if not items:
        console.print("[yellow]No demand data found. Run [bold]floraflow demo[/bold] first.[/yellow]")
        return

    table = Table(title="Demanda de Mercado", box=box.ROUNDED, show_lines=True)
    table.add_column("Flower", style="bold magenta")
    table.add_column("Market", style="cyan")
    table.add_column("Demand")
    table.add_column("Price/Stem", justify="right", style="bold green")
    table.add_column("Trend")
    table.add_column("Event", style="yellow")

    for d in items:
        table.add_row(
            d.flower_type.value.title(),
            d.market.value.replace("_", " ").title(),
            f"[{_demand_color(d.demand_level.value)}]{d.demand_level.value.upper()}[/{_demand_color(d.demand_level.value)}]",
            _mxn(d.price_per_stem_mxn),
            _trend_icon(d.price_trend.value),
            (d.event_driver or "none").replace("_", " ").title(),
        )
    console.print(table)


@app.command()
def shipments(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
):
    """Track cold chain shipments."""
    items = store.list_shipments(status=status)
    if not items:
        console.print("[yellow]No shipments found. Run [bold]floraflow demo[/bold] first.[/yellow]")
        return

    table = Table(title="Cadena de Frio — Envios", box=box.ROUNDED, show_lines=True)
    table.add_column("ID", style="dim", max_width=18)
    table.add_column("Status")
    table.add_column("Origin", style="cyan")
    table.add_column("Destination", style="green")
    table.add_column("Carrier", style="white")
    table.add_column("Truck", style="yellow")
    table.add_column("Temp C", justify="right")
    table.add_column("Humidity", justify="right")
    table.add_column("ETA", style="dim")

    for s in items:
        avg_temp = sum(s.temperature_c) / len(s.temperature_c) if s.temperature_c else 0
        max_temp = max(s.temperature_c) if s.temperature_c else 0
        temp_color = "green" if max_temp < 5 else "yellow" if max_temp < 8 else "red"
        table.add_row(
            s.id[:16] + "...",
            _shipment_badge(s.status.value),
            s.origin_municipality.value.replace("_", " ").title(),
            s.destination.value.replace("_", " ").title(),
            s.carrier,
            s.truck_id,
            f"[{temp_color}]{avg_temp:.1f} (max {max_temp:.1f})[/{temp_color}]",
            f"{s.humidity_pct:.0f}%",
            (s.eta or "—")[:16],
        )
    console.print(table)


@app.command()
def orders(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
):
    """Show buyer orders."""
    items = store.list_orders(status=status)
    if not items:
        console.print("[yellow]No orders found. Run [bold]floraflow demo[/bold] first.[/yellow]")
        return

    table = Table(title="Pedidos de Compradores", box=box.ROUNDED, show_lines=True)
    table.add_column("Buyer", style="bold cyan", max_width=25)
    table.add_column("Type", style="magenta")
    table.add_column("Flowers", style="yellow")
    table.add_column("Stems", justify="right", style="green")
    table.add_column("Grade")
    table.add_column("Price", justify="right", style="bold green")
    table.add_column("Status")
    table.add_column("Delivery", style="dim")

    total_value = 0.0
    for o in items:
        total_value += o.price_offered_mxn
        table.add_row(
            o.buyer_name,
            o.buyer_type.value.replace("_", " ").title(),
            ", ".join(o.flower_types_needed),
            f"{o.stems_needed:,}",
            _grade_badge(o.quality_required.value),
            _mxn(o.price_offered_mxn),
            _order_badge(o.status.value),
            o.delivery_date,
        )
    console.print(table)
    console.print(f"\n[dim]Total: {len(items)} orders | {_mxn(total_value)}[/dim]")


@app.command()
def quality():
    """Show quality assessments."""
    items = store.list_quality()
    if not items:
        console.print("[yellow]No quality data found. Run [bold]floraflow demo[/bold] first.[/yellow]")
        return

    table = Table(title="Evaluaciones de Calidad", box=box.ROUNDED, show_lines=True)
    table.add_column("Batch", style="dim", max_width=18)
    table.add_column("Inspector", style="cyan")
    table.add_column("Straight", justify="right")
    table.add_column("Petals", justify="right")
    table.add_column("Color", justify="right")
    table.add_column("Blemish %", justify="right")
    table.add_column("Vase Life", justify="right")
    table.add_column("Grade")

    for q in items:
        str_color = "green" if q.stem_straightness >= 8 else "yellow" if q.stem_straightness >= 6 else "red"
        blem_color = "green" if q.blemish_pct < 5 else "yellow" if q.blemish_pct < 10 else "red"
        table.add_row(
            q.batch_id[:16] + "...",
            q.inspector,
            f"[{str_color}]{q.stem_straightness}/10[/{str_color}]",
            str(q.petal_count),
            f"{q.color_intensity}/10",
            f"[{blem_color}]{q.blemish_pct:.1f}%[/{blem_color}]",
            f"{q.vase_life_estimate_days}d",
            _grade_badge(q.grade_recommendation.value),
        )
    console.print(table)


@app.command()
def signals():
    """Show market price signals."""
    items = store.list_signals()
    if not items:
        console.print("[yellow]No signals found. Run [bold]floraflow demo[/bold] first.[/yellow]")
        return

    for s in items:
        panel = Panel(
            f"[bold]{s.description}[/bold]\n\n"
            f"[green]Accion recomendada:[/green] {s.recommended_action}\n"
            f"[dim]Valido hasta: {s.valid_until}[/dim]",
            title=f"{_signal_badge(s.signal_type.value)} — {s.flower_type.value.title()}",
            subtitle=_severity_badge(s.priority.value),
            box=box.ROUNDED,
            border_style="yellow" if s.priority.value in ("high", "critical") else "dim",
        )
        console.print(panel)


@app.command(name="harvest-plan")
def harvest_plan():
    """Show upcoming harvest plans."""
    items = store.list_harvest_plans()
    if not items:
        console.print("[yellow]No harvest plans found. Run [bold]floraflow demo[/bold] first.[/yellow]")
        return

    table = Table(title="Plan de Cosecha", box=box.ROUNDED, show_lines=True)
    table.add_column("Greenhouse", style="dim", max_width=18)
    table.add_column("Flower", style="bold magenta")
    table.add_column("Date", style="cyan")
    table.add_column("Stems Target", justify="right", style="green")
    table.add_column("Market", style="yellow")
    table.add_column("Price Target", justify="right", style="bold green")
    table.add_column("Status")

    gh_map = {g.id: g.name for g in store.list_greenhouses()}
    for h in items:
        status_color = {
            "planned": "yellow", "in_progress": "cyan", "completed": "green", "cancelled": "red"
        }.get(h.status.value, "white")
        table.add_row(
            gh_map.get(h.greenhouse_id, h.greenhouse_id[:16] + "..."),
            h.flower_type.value.title(),
            h.planned_date,
            f"{h.stems_target:,}",
            h.market_target.value.replace("_", " ").title(),
            _mxn(h.price_target_mxn) + "/stem",
            f"[{status_color}]{h.status.value.upper().replace('_', ' ')}[/{status_color}]",
        )
    console.print(table)


@app.command()
def weather():
    """Fetch live weather from Open-Meteo for all greenhouse locations."""
    from .feeds import fetch_all_greenhouse_weather

    console.print("[bold cyan]Consultando clima en tiempo real...[/bold cyan]\n")
    try:
        result = asyncio.run(fetch_all_greenhouse_weather())
    except Exception as exc:
        console.print(f"[red]Error fetching weather: {exc}[/red]")
        return

    table = Table(title="Clima en Zonas Floricolas", box=box.ROUNDED, show_lines=True)
    table.add_column("Municipality", style="bold cyan")
    table.add_column("Temp C", justify="right")
    table.add_column("Humidity", justify="right")
    table.add_column("Precip mm", justify="right")
    table.add_column("Wind km/h", justify="right")
    table.add_column("Alerts", justify="right")

    for key, val in result.items():
        if key.startswith("_"):
            continue
        if "error" in val:
            table.add_row(val["municipality"].replace("_", " ").title(), "[red]Error[/red]", "", "", "", "")
            continue
        temp = val.get("temperature_c")
        temp_color = "red" if temp and temp > 35 else "cyan" if temp and temp < 3 else "green"
        table.add_row(
            val["municipality"].replace("_", " ").title(),
            f"[{temp_color}]{temp:.1f}[/{temp_color}]" if temp is not None else "—",
            f"{val.get('humidity_pct', 0):.0f}%" if val.get("humidity_pct") else "—",
            f"{val.get('precipitation_mm', 0):.1f}" if val.get("precipitation_mm") is not None else "—",
            f"{val.get('wind_speed_kmh', 0):.0f}" if val.get("wind_speed_kmh") is not None else "—",
            str(val.get("alerts_count", 0)),
        )
    console.print(table)

    # Show alerts
    alerts_data = result.get("_alerts", [])
    if alerts_data:
        console.print(f"\n[bold yellow]Alertas Meteorologicas ({len(alerts_data)})[/bold yellow]\n")
        for a in alerts_data[:10]:
            sev = a.get("severity", "low")
            alert_type = a.get("alert_type", "unknown")
            desc = a.get("description", "")
            muni = a.get("municipality", "").replace("_", " ").title()
            console.print(f"  {_severity_badge(sev)} [{muni}] {alert_type.upper()}: {desc}")

    summary = result.get("_summary", {})
    console.print(f"\n[dim]Locations: {summary.get('locations_fetched', 0)} | "
                  f"Alerts: {summary.get('total_alerts', 0)} | "
                  f"Critical: {summary.get('critical_alerts', 0)}[/dim]")


@app.command()
def analyze():
    """AI-powered market analysis using Claude."""
    from . import ai

    console.print("[bold cyan]Generando inteligencia de mercado con IA...[/bold cyan]\n")
    prices = store.list_demand()
    sigs = store.list_signals()

    if not prices and not sigs:
        console.print("[yellow]No market data. Run [bold]floraflow demo[/bold] first.[/yellow]")
        return

    try:
        report = ai.generate_market_intelligence(prices=prices, signals=sigs)
        panel = Panel(
            report,
            title="[bold green]Reporte de Inteligencia de Mercado[/bold green]",
            box=box.DOUBLE,
            border_style="green",
        )
        console.print(panel)
    except Exception as exc:
        console.print(f"[red]AI analysis error: {exc}[/red]")


@app.command()
def optimize():
    """AI-powered harvest timing optimization."""
    from . import ai

    console.print("[bold cyan]Optimizando timing de cosecha con IA...[/bold cyan]\n")
    batch_list = store.list_batches()
    demand_list = store.list_demand()

    if not batch_list:
        console.print("[yellow]No batch data. Run [bold]floraflow demo[/bold] first.[/yellow]")
        return

    try:
        result = ai.optimize_harvest_timing(batch_list, demand_list)
        panel = Panel(
            result,
            title="[bold green]Plan de Cosecha Optimizado[/bold green]",
            box=box.DOUBLE,
            border_style="green",
        )
        console.print(panel)
    except Exception as exc:
        console.print(f"[red]AI optimization error: {exc}[/red]")


@app.command()
def match():
    """AI-powered buyer matching."""
    from . import ai

    console.print("[bold cyan]Emparejando oferta con demanda usando IA...[/bold cyan]\n")
    batch_list = store.list_batches()
    order_list = store.list_orders()

    if not batch_list or not order_list:
        console.print("[yellow]Need batches and orders. Run [bold]floraflow demo[/bold] first.[/yellow]")
        return

    try:
        result = ai.match_buyers(batch_list, order_list)
        panel = Panel(
            result,
            title="[bold green]Emparejamiento Oferta-Demanda[/bold green]",
            box=box.DOUBLE,
            border_style="green",
        )
        console.print(panel)
    except Exception as exc:
        console.print(f"[red]AI matching error: {exc}[/red]")


@app.command()
def demo():
    """Load realistic demo data for Estado de Mexico floriculture."""
    from .demo import generate_demo_data

    console.print("[bold cyan]Generando datos demo de floricultura del Estado de Mexico...[/bold cyan]\n")
    result = asyncio.run(generate_demo_data())

    table = Table(title="Demo Data Loaded", box=box.ROUNDED)
    table.add_column("Entity", style="cyan")
    table.add_column("Count", justify="right", style="bold green")

    for key, val in result.items():
        if key.startswith("research_"):
            continue
        table.add_row(key.replace("_", " ").title(), str(val))
    console.print(table)

    # Show research results
    for key in ("research_prices", "research_events"):
        val = result.get(key, "")
        if val:
            label = "Precios en Tiempo Real" if "prices" in key else "Eventos y Demanda"
            console.print(Panel(str(val), title=f"[bold yellow]{label}[/bold yellow]", box=box.ROUNDED, border_style="yellow"))

    console.print("\n[bold green]Demo data loaded successfully![/bold green] Run [bold]floraflow status[/bold] for dashboard.")


@app.command()
def status():
    """Dashboard with KPIs and overview."""
    stats = store.get_stats()
    greenhouses_list = store.list_greenhouses()
    batch_list = store.list_batches()
    shipment_list = store.list_shipments()
    order_list = store.list_orders()
    alert_list = store.list_weather_alerts()
    signal_list = store.list_signals()

    if not greenhouses_list:
        console.print("[yellow]No data found. Run [bold]floraflow demo[/bold] to load demo data.[/yellow]")
        return

    # Header
    console.print(Panel(
        "[bold white]FloraFlow[/bold white] — AI-Powered Floriculture Revenue Optimization\n"
        "[dim]Estado de Mexico | Villa Guerrero, Tenancingo, Coatepec Harinas, Metepec, Toluca[/dim]",
        box=box.DOUBLE,
        border_style="green",
    ))

    # KPIs
    total_stems = sum(b.stems_count for b in batch_list)
    total_value = sum(b.estimated_value_mxn for b in batch_list)
    active_ships = len([s for s in shipment_list if s.status.value in ("in_transit", "loading", "cooling")])
    pending_orders = len([o for o in order_list if o.status.value == "pending"])
    critical_alerts = len([a for a in alert_list if a.severity.value == "critical"])

    kpi_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    kpi_table.add_column("Metric", style="dim")
    kpi_table.add_column("Value", style="bold green", justify="right")
    kpi_table.add_row("Greenhouses", str(len(greenhouses_list)))
    kpi_table.add_row("Total Area", f"{sum(g.area_m2 for g in greenhouses_list):,.0f} m2")
    kpi_table.add_row("Active Batches", str(len(batch_list)))
    kpi_table.add_row("Total Stems", f"{total_stems:,}")
    kpi_table.add_row("Inventory Value", _mxn(total_value))
    kpi_table.add_row("Active Shipments", str(active_ships))
    kpi_table.add_row("Pending Orders", str(pending_orders))
    kpi_table.add_row("Price Signals", str(len(signal_list)))
    if critical_alerts > 0:
        kpi_table.add_row("[bold red]Critical Alerts[/bold red]", f"[bold red]{critical_alerts}[/bold red]")
    console.print(Panel(kpi_table, title="[bold]KPIs[/bold]", box=box.ROUNDED, border_style="cyan"))

    # Upcoming events
    if stats and stats.upcoming_events:
        events_text = "\n".join(f"  [yellow]>[/yellow] {e}" for e in stats.upcoming_events)
        console.print(Panel(events_text, title="[bold]Proximos Eventos[/bold]", box=box.ROUNDED, border_style="yellow"))

    # Top markets
    if stats and stats.top_markets:
        markets_text = "\n".join(f"  [green]>[/green] {m}" for m in stats.top_markets)
        console.print(Panel(markets_text, title="[bold]Top Mercados[/bold]", box=box.ROUNDED, border_style="green"))

    # Active alerts
    if alert_list:
        console.print(f"\n[bold yellow]Alertas Activas ({len(alert_list)})[/bold yellow]")
        for a in alert_list[:5]:
            console.print(f"  {_severity_badge(a.severity.value)} [{a.municipality.value.replace('_', ' ').title()}] {a.description[:80]}")

    console.print(f"\n[dim]Use [bold]floraflow --help[/bold] for all commands[/dim]")


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h"),
    port: int = typer.Option(8000, "--port", "-p"),
):
    """Start FastAPI server."""
    import uvicorn
    console.print(f"[bold green]Starting FloraFlow API at http://{host}:{port}[/bold green]")
    console.print("[dim]Docs: http://localhost:8000/docs[/dim]")
    uvicorn.run("floraflow.api:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    app()
