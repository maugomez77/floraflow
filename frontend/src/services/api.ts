import axios from "axios";
import type {
  Greenhouse,
  FlowerBatch,
  MarketDemand,
  ColdChainShipment,
  QualityAssessment,
  BuyerOrder,
  WeatherAlert,
  PriceSignal,
  HarvestPlan,
  FlowStats,
} from "../types";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// --- Stats ---
export const getStats = () => api.get<FlowStats>("/v1/stats").then((r) => r.data);

// --- Greenhouses ---
export const getGreenhouses = () =>
  api.get<Greenhouse[]>("/v1/greenhouses").then((r) => r.data);

export const getGreenhouse = (id: string) =>
  api.get<Greenhouse>(`/v1/greenhouses/${id}`).then((r) => r.data);

// --- Batches ---
export const getBatches = (params?: {
  greenhouse_id?: string;
  flower_type?: string;
}) => api.get<FlowerBatch[]>("/v1/batches", { params }).then((r) => r.data);

export const getBatch = (id: string) =>
  api.get<FlowerBatch>(`/v1/batches/${id}`).then((r) => r.data);

// --- Market Demand ---
export const getDemand = (params?: {
  flower_type?: string;
  market?: string;
}) => api.get<MarketDemand[]>("/v1/demand", { params }).then((r) => r.data);

// --- Shipments ---
export const getShipments = (params?: { status?: string }) =>
  api.get<ColdChainShipment[]>("/v1/shipments", { params }).then((r) => r.data);

export const getShipment = (id: string) =>
  api.get<ColdChainShipment>(`/v1/shipments/${id}`).then((r) => r.data);

// --- Orders ---
export const getOrders = (params?: { status?: string }) =>
  api.get<BuyerOrder[]>("/v1/orders", { params }).then((r) => r.data);

// --- Quality ---
export const getQuality = (params?: { batch_id?: string }) =>
  api.get<QualityAssessment[]>("/v1/quality", { params }).then((r) => r.data);

// --- Signals ---
export const getSignals = () =>
  api.get<PriceSignal[]>("/v1/signals").then((r) => r.data);

// --- Harvest Plans ---
export const getHarvestPlans = () =>
  api.get<HarvestPlan[]>("/v1/harvest-plans").then((r) => r.data);

// --- Weather Alerts ---
export const getWeatherAlerts = () =>
  api.get<WeatherAlert[]>("/v1/weather-alerts").then((r) => r.data);

// --- AI Analysis ---
export const analyzeMarket = () =>
  api.post<Record<string, unknown>>("/v1/analyze").then((r) => r.data);

export const optimizeHarvest = () =>
  api.post<Record<string, unknown>>("/v1/optimize").then((r) => r.data);

export const matchBuyers = () =>
  api.post<Record<string, unknown>>("/v1/match").then((r) => r.data);

export default api;
