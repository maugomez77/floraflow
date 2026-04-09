# FloraFlow — AI-Powered Floriculture Revenue Optimization

## What This Is
FloraFlow is a world-class AI-powered floriculture platform for Estado de México — the region that produces 70% of Mexico's flowers ($2B+ industry). It provides computer vision, predictive intelligence, revenue optimization, real-time auction marketplace, and satellite crop monitoring for flower growers in Villa Guerrero, Tenancingo, Coatepec Harinas, Metepec, and Toluca.

## Quick Start
```bash
floraflow demo          # Load demo data (with real-time research)
floraflow status        # Dashboard with KPIs
floraflow greenhouses   # List all greenhouses
floraflow auctions      # List active marketplace auctions
floraflow satellite     # Show crop health monitoring
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
- **CLI**: typer + rich (17 commands)
- **API**: FastAPI with 39 endpoints (CRUD + 21 AI features + Marketplace + Satellite + live feeds)
- **Frontend**: React + TypeScript + Vite (11 pages, bilingual ES/EN, premium floral UI)
- **Database**: Neon PostgreSQL via SQLAlchemy async + asyncpg
- **AI**: Claude Sonnet (analysis, vision, predictions, optimization, auction pricing)
- **Weather**: Open-Meteo (no API key needed)
- **Satellite**: Open-Meteo ERA5 soil/ET0/sunshine data for NDVI estimation
- **Research**: DuckDuckGo + Claude Haiku for real-time market data
- **i18n**: ES/EN toggle with localStorage persistence

### 21 AI Features (5 categories)

#### Vision AI (Claude Vision API)
1. **Photo Quality Grading**: Upload flower photo → grade (export_premium/first/second/third)
2. **Disease Detection**: Upload plant photo → identify diseases, pests, deficiencies

#### Predictive Intelligence
3. **Demand Forecasting**: 30-day demand prediction by flower type + seasonal events
4. **Price Prediction**: 7-day price forecast for Jamaica/Central de Abasto markets
5. **Frost Risk Assessment**: Per-greenhouse risk with estimated loss in MXN

#### Revenue Optimization
6. **Dynamic Pricing Engine**: Real-time price recommendations based on supply/demand/events
7. **Route Optimizer**: Truck routes from greenhouses → CDMX markets
8. **Waste Predictor**: Spoilage risk based on temperature, humidity, transport time

#### General Analysis
9. **Market Intelligence**: Full market report with actionable insights
10. **Harvest Optimization**: When to cut for maximum revenue
11. **Buyer Matching**: Match supply with buyer orders

#### Real-Time Auction Marketplace
12. **AI Minimum Pricing**: Sets auction floor price based on quality + demand
13. **Bidding System**: Place bids with message, buy-now support
14. **Auction Status Tracking**: open → bidding → sold/expired
15. **Live Countdown**: Auto-refresh every 30s, time-to-close tracking

#### Satellite Crop Monitoring (Open-Meteo ERA5)
16. **Crop Health Scoring**: 0-100 score from soil moisture + temp + ET0 + sunshine
17. **NDVI Estimation**: Vegetation index from multi-factor analysis
18. **Stress Detection**: Drought, frost, heat, waterlogging, high ET0
19. **Trend Analysis**: Improving/stable/declining over past 7 days
20. **AI Satellite Analysis**: Full irrigation + fertilization schedules
21. **Per-farm Health Drilldown**: Individual greenhouse monitoring

### API Endpoints (39 total)
```
CRUD: /v1/greenhouses, batches, demand, shipments, orders, quality, signals, harvest-plans, stats, weather-alerts
AI General: /v1/analyze, /v1/optimize, /v1/match
AI Vision: /v1/vision/grade, /v1/vision/disease (multipart file upload)
AI Predict: /v1/predict/demand, /v1/predict/prices, /v1/predict/frost
AI Optimize: /v1/optimize/pricing, /v1/optimize/routes, /v1/optimize/waste
Marketplace: /v1/auctions (GET/POST), /v1/auctions/{id}, /v1/auctions/{id}/bid,
             /v1/auctions/{id}/buy, /v1/auctions/{id}/close, /v1/auctions/ai-price
Satellite: /v1/satellite (all farms), /v1/satellite/{farm_id}, /v1/satellite/analyze
Live: /v1/weather/live, /v1/refresh
Health: /health
```

## Key Files
```
src/floraflow/
  cli.py              # 17 Typer commands
  api.py              # FastAPI with 39 endpoints + lifespan
  database.py         # SQLAlchemy ORM: 13 tables (including auctions, bids, crop_health)
  store.py            # Hybrid PostgreSQL/JSON store with async functions
  models.py           # 14 Pydantic models with enums
  demo.py             # Demo data generator with real-time research
  feeds.py            # Open-Meteo weather + soil + crop health for 5 municipalities
  ai.py               # Claude analysis (market, harvest, buyers)
  vision.py           # Claude Vision (quality grading, disease detection)
  predictive.py       # Demand forecast, price prediction, frost risk, crop health AI
  optimization.py     # Dynamic pricing, route optimizer, waste predictor, auction pricing
frontend/
  src/pages/
    Dashboard.tsx        # KPIs, dynamic event calendar with countdowns
    Greenhouses.tsx      # Farms list + detail
    Batches.tsx          # Flower batches
    Shipments.tsx        # Cold chain tracking
    Orders.tsx           # Buyer orders
    Quality.tsx          # Quality assessments
    Analyze.tsx          # 4-tab AI analysis page (11 features)
    Marketplace.tsx      # Auction grid with bidding modal
    Satellite.tsx        # NASA-style crop health dashboard
  src/components/
    Layout.tsx           # Sidebar with dark gradient + botanical pattern
    AIResultRenderer.tsx # Smart chart/table renderer for any AI JSON response
  src/i18n/              # Bilingual ES/EN translations (200+ keys)
  src/services/api.ts    # Typed axios API client
  src/index.css          # Premium floral UI (Bloomberg meets luxury brand)
```

## Technical Notes
- `python-multipart` required for file upload endpoints (vision AI)
- Render free tier sleeps after 15 min — first request takes ~30s cold start
- AI endpoints need 120s timeout on frontend (Render wake + Claude processing)
- `asyncpg` doesn't support `sslmode=require` — auto-converted to `ssl=require` in database.py
- Background research runs via `asyncio.create_task()` in lifespan — must NOT block port binding
- All prices in MXN (Mexican pesos) — this is a domestic market play
- Flower market is EXTREMELY seasonal — Valentine's (300% spike), Mother's Day (200-400%)
- AIResultRenderer auto-detects JSON shapes (pricing, forecast, routes, waste, frost, greenhouse risk) and renders charts/tables
- Dynamic event calendar calculates from today's date with countdown badges (urgent if <14d)

## Origin
Council deep session 2026-04-05, Estado de México focus.
#2 pick (Score: 8.6, 19/31 votes, Judge: 7.0/10).
"Estado de México dominates Mexico's flower production, and there's no AI tooling for it."
