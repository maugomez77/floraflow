# FloraFlow — AI-Powered Floriculture Revenue Optimization

## What This Is
FloraFlow is an AI-powered floriculture platform for Estado de México — the region that produces 70% of Mexico's flowers ($2B+ industry). It provides computer vision, predictive intelligence, and revenue optimization for flower growers in Villa Guerrero, Tenancingo, Coatepec Harinas, Metepec, and Toluca.

## Quick Start
```bash
floraflow demo          # Load demo data (with real-time research)
floraflow status        # Dashboard with KPIs
floraflow greenhouses   # List all greenhouses
floraflow weather       # Live weather from Open-Meteo
floraflow serve         # Start FastAPI server at localhost:8000
```

## Deployed
- **Frontend**: https://floraflow-fawn.vercel.app (Vercel static site)
- **Backend API**: https://floraflow-api.onrender.com (Render free tier)
- **Database**: Neon PostgreSQL (free, serverless, persistent)
- **Repo**: https://github.com/maugomez77/floraflow

## Architecture

### Data Storage: Neon PostgreSQL (NOT in-memory)
- **Connection**: `DATABASE_URL` env var on Render → Neon serverless PostgreSQL
- **Driver**: SQLAlchemy async + asyncpg
- **Hybrid store**: PostgreSQL when `DATABASE_URL` set, JSON file fallback for local dev
- **Tables auto-created** on startup via `init_db()`
- **Data persists** across Render restarts — no more data loss
- The `sslmode=require` in Neon URLs must be converted to `ssl=require` for asyncpg

### Stack
- **CLI**: typer + rich (15 commands)
- **API**: FastAPI with 29 endpoints (CRUD + 11 AI + live feeds)
- **Frontend**: React + TypeScript + Vite (9 pages, bilingual ES/EN)
- **Database**: Neon PostgreSQL via SQLAlchemy async + asyncpg
- **AI**: Claude Sonnet (analysis, vision, predictions, optimization)
- **Weather**: Open-Meteo (no API key needed)
- **Research**: DuckDuckGo + Claude Haiku for real-time market data
- **i18n**: ES/EN toggle with localStorage persistence

### 11 AI Features

#### Vision AI (Claude Vision API)
- **Photo Quality Grading**: Upload flower photo → grade (export_premium/first/second/third)
- **Disease Detection**: Upload plant photo → identify diseases, pests, deficiencies

#### Predictive Intelligence
- **Demand Forecasting**: 30-day demand prediction by flower type + seasonal events
- **Price Prediction**: 7-day price forecast for Jamaica/Central de Abasto markets
- **Frost Risk Assessment**: Per-greenhouse risk with estimated loss in MXN

#### Revenue Optimization
- **Dynamic Pricing Engine**: Real-time price recommendations based on supply/demand/events
- **Route Optimizer**: Truck routes from greenhouses → CDMX markets
- **Waste Predictor**: Spoilage risk based on temperature, humidity, transport time

#### General Analysis
- **Market Intelligence**: Full market report with actionable insights
- **Harvest Optimization**: When to cut for maximum revenue
- **Buyer Matching**: Match supply with buyer orders

### API Endpoints
```
CRUD: /v1/greenhouses, batches, demand, shipments, orders, quality, signals, harvest-plans, stats, weather-alerts
AI General: /v1/analyze, /v1/optimize, /v1/match
AI Vision: /v1/vision/grade (file upload), /v1/vision/disease (file upload)
AI Predict: /v1/predict/demand, /v1/predict/prices, /v1/predict/frost
AI Optimize: /v1/optimize/pricing, /v1/optimize/routes, /v1/optimize/waste
Live: /v1/weather/live, /v1/refresh
Health: /health
```

## Key Files
```
src/floraflow/
  cli.py              # 15 Typer commands
  api.py              # FastAPI with 29 endpoints + lifespan
  database.py         # SQLAlchemy ORM models + init_db()
  store.py            # Hybrid PostgreSQL/JSON store with async functions
  models.py           # 11 Pydantic models with enums
  demo.py             # Demo data generator with real-time research
  feeds.py            # Open-Meteo weather for 5 municipalities
  ai.py               # Claude analysis (market, harvest, buyers)
  vision.py           # Claude Vision (quality grading, disease detection)
  predictive.py       # Demand forecast, price prediction, frost risk
  optimization.py     # Dynamic pricing, route optimizer, waste predictor
frontend/
  src/pages/Analyze.tsx   # 4-tab AI analysis page (11 features)
  src/i18n/              # Bilingual ES/EN translations
  src/services/api.ts    # Typed axios API client
```

## Technical Notes
- `python-multipart` required for file upload endpoints (vision AI)
- Render free tier sleeps after 15 min — first request takes ~30s cold start
- AI endpoints need 120s timeout on frontend (Render wake + Claude processing)
- `asyncpg` doesn't support `sslmode=require` — auto-converted to `ssl=require` in database.py
- Background research runs via `asyncio.create_task()` in lifespan — must NOT block port binding
- All prices in MXN (Mexican pesos) — this is a domestic market play
- Flower market is EXTREMELY seasonal — Valentine's (300% spike), Mother's Day (200-400%)

## Origin
Council deep session 2026-04-05, Estado de México focus.
#2 pick (Score: 8.6, 19/31 votes, Judge: 7.0/10).
"Estado de México dominates Mexico's flower production, and there's no AI tooling for it."
