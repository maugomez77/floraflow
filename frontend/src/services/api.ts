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
export const getStats = () => api.get<FlowStats>("/stats").then((r) => r.data);

// --- Greenhouses ---
export const getGreenhouses = () =>
  api.get<Greenhouse[]>("/greenhouses").then((r) => r.data);

export const getGreenhouse = (id: string) =>
  api.get<Greenhouse>(`/greenhouses/${id}`).then((r) => r.data);

// --- Batches ---
export const getBatches = (params?: {
  greenhouse_id?: string;
  flower_type?: string;
}) => api.get<FlowerBatch[]>("/batches", { params }).then((r) => r.data);

export const getBatch = (id: string) =>
  api.get<FlowerBatch>(`/batches/${id}`).then((r) => r.data);

// --- Market Demand ---
export const getDemand = (params?: {
  flower_type?: string;
  market?: string;
}) => api.get<MarketDemand[]>("/demand", { params }).then((r) => r.data);

// --- Shipments ---
export const getShipments = (params?: { status?: string }) =>
  api.get<ColdChainShipment[]>("/shipments", { params }).then((r) => r.data);

export const getShipment = (id: string) =>
  api.get<ColdChainShipment>(`/shipments/${id}`).then((r) => r.data);

// --- Orders ---
export const getOrders = (params?: { status?: string }) =>
  api.get<BuyerOrder[]>("/orders", { params }).then((r) => r.data);

// --- Quality ---
export const getQuality = (params?: { batch_id?: string }) =>
  api.get<QualityAssessment[]>("/quality", { params }).then((r) => r.data);

// --- Signals ---
export const getSignals = () =>
  api.get<PriceSignal[]>("/signals").then((r) => r.data);

// --- Harvest Plans ---
export const getHarvestPlans = () =>
  api.get<HarvestPlan[]>("/harvest-plans").then((r) => r.data);

// --- Weather Alerts ---
export const getWeatherAlerts = () =>
  api.get<WeatherAlert[]>("/weather-alerts").then((r) => r.data);

// --- AI Analysis ---
export const analyzeMarket = () =>
  api.post<{ result: string }>("/analyze/market").then((r) => r.data);

export const optimizeHarvest = () =>
  api.post<{ result: string }>("/analyze/harvest").then((r) => r.data);

export const matchBuyers = () =>
  api.post<{ result: string }>("/analyze/buyers").then((r) => r.data);

export default api;
