/* FloraFlow data types — mirrors Python Pydantic models */

export interface Greenhouse {
  id: string;
  name: string;
  municipality: string;
  location_lat: number;
  location_lng: number;
  area_m2: number;
  flower_types: string[];
  owner: string;
  contact: string;
  tech_level: string;
  created_at: string;
}

export interface FlowerBatch {
  id: string;
  greenhouse_id: string;
  flower_type: string;
  variety: string;
  stems_count: number;
  quality_grade: string;
  color: string;
  stem_length_cm: number;
  harvest_date: string;
  shelf_life_days: number;
  estimated_value_mxn: number;
}

export interface MarketDemand {
  id: string;
  flower_type: string;
  market: string;
  demand_level: string;
  price_per_stem_mxn: number;
  price_trend: string;
  date: string;
  event_driver: string | null;
}

export interface ColdChainShipment {
  id: string;
  batch_ids: string[];
  origin_municipality: string;
  destination: string;
  status: string;
  carrier: string;
  truck_id: string;
  temperature_c: number[];
  departure_time: string | null;
  eta: string | null;
  humidity_pct: number;
}

export interface QualityAssessment {
  id: string;
  batch_id: string;
  inspector: string;
  stem_straightness: number;
  petal_count: number;
  color_intensity: number;
  blemish_pct: number;
  vase_life_estimate_days: number;
  grade_recommendation: string;
  photo_url: string | null;
  assessment_date: string;
}

export interface BuyerOrder {
  id: string;
  buyer_name: string;
  buyer_type: string;
  flower_types_needed: string[];
  stems_needed: number;
  quality_required: string;
  delivery_date: string;
  price_offered_mxn: number;
  status: string;
  matched_greenhouse: string | null;
}

export interface WeatherAlert {
  id: string;
  municipality: string;
  alert_type: string;
  severity: string;
  description: string;
  forecast_date: string;
  affected_greenhouses: string[];
}

export interface PriceSignal {
  id: string;
  flower_type: string;
  signal_type: string;
  description: string;
  recommended_action: string;
  valid_until: string;
  priority: string;
}

export interface HarvestPlan {
  id: string;
  greenhouse_id: string;
  flower_type: string;
  planned_date: string;
  stems_target: number;
  market_target: string;
  price_target_mxn: number;
  status: string;
}

export interface FlowStats {
  total_greenhouses: number;
  total_area_m2: number;
  active_shipments: number;
  weekly_stems_shipped: number;
  revenue_mtd_mxn: number;
  top_markets: string[];
  upcoming_events: string[];
}

export interface Auction {
  id: string;
  greenhouse_id: string;
  seller_name: string;
  flower_type: string;
  variety: string;
  stems_count: number;
  quality_grade: "export_premium" | "first" | "second" | "third";
  color: string;
  stem_length_cm: number;
  min_price_mxn: number;
  current_bid_mxn: number;
  buy_now_price_mxn: number;
  status: "open" | "bidding" | "sold" | "expired" | "cancelled";
  photos: string[];
  expires_at: string;
  created_at: string;
}

export interface Bid {
  id: string;
  auction_id: string;
  bidder_name: string;
  bidder_type: string;
  amount_mxn: number;
  message: string;
  created_at: string;
}

export interface CropHealthReport {
  id?: string;
  municipality: string;
  farm_ids: string[];
  health_score: number;
  ndvi_estimate: number;
  soil_moisture: number;
  soil_temp_c: number;
  et0_mm: number;
  stress_indicators: string[];
  trend: "improving" | "stable" | "declining";
  report_date?: string;
}
