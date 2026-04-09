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
  Auction,
  Bid,
  CropHealthReport,
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

// --- AI Analysis (longer timeout for Render cold start + Claude processing) ---
export const analyzeMarket = () =>
  api.post<Record<string, unknown>>("/v1/analyze", {}, { timeout: 120000 }).then((r) => r.data);

export const optimizeHarvest = () =>
  api.post<Record<string, unknown>>("/v1/optimize", {}, { timeout: 120000 }).then((r) => r.data);

export const matchBuyers = () =>
  api.post<Record<string, unknown>>("/v1/match", {}, { timeout: 120000 }).then((r) => r.data);

// --- Vision AI ---
export const gradeFlower = (file: File, flowerType: string) => {
  const form = new FormData();
  form.append("file", file);
  return api.post(`/v1/vision/grade?flower_type=${flowerType}`, form, {
    headers: { "Content-Type": "multipart/form-data" },
    timeout: 120000,
  }).then(r => r.data);
};

export const detectDisease = (file: File) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/v1/vision/disease", form, {
    headers: { "Content-Type": "multipart/form-data" },
    timeout: 120000,
  }).then(r => r.data);
};

// --- Predictive Intelligence ---
export const forecastDemand = (flowerType: string, days: number) =>
  api.post(`/v1/predict/demand?flower_type=${flowerType}&days=${days}`, {}, { timeout: 120000 }).then(r => r.data);

export const predictPrices = (flowerType: string) =>
  api.post(`/v1/predict/prices?flower_type=${flowerType}`, {}, { timeout: 120000 }).then(r => r.data);

export const assessFrost = () =>
  api.post("/v1/predict/frost", {}, { timeout: 120000 }).then(r => r.data);

// --- Revenue Optimization ---
export const dynamicPricing = () =>
  api.post("/v1/optimize/pricing", {}, { timeout: 120000 }).then(r => r.data);

export const optimizeRoutes = () =>
  api.post("/v1/optimize/routes", {}, { timeout: 120000 }).then(r => r.data);

export const predictWaste = () =>
  api.post("/v1/optimize/waste", {}, { timeout: 120000 }).then(r => r.data);

// --- Marketplace (Auctions) ---
export const getAuctions = (status?: string) =>
  api.get<Auction[]>("/v1/auctions", { params: status ? { status } : {} }).then(r => r.data);

export const getAuction = (id: string) =>
  api.get<{ auction: Auction; bids: Bid[] }>(`/v1/auctions/${id}`).then(r => r.data);

export const placeBid = (
  id: string,
  bidder_name: string,
  bidder_type: string,
  amount_mxn: number,
  message: string = "",
) =>
  api
    .post(`/v1/auctions/${id}/bid`, { bidder_name, bidder_type, amount_mxn, message })
    .then(r => r.data);

export const buyNow = (id: string, buyer_name: string) =>
  api.post(`/v1/auctions/${id}/buy`, { buyer_name }).then(r => r.data);

// --- Satellite Crop Monitoring ---
export const getCropHealth = () =>
  api.get<CropHealthReport[]>("/v1/satellite").then(r => r.data);

export const getFarmHealth = (farm_id: string) =>
  api.get<CropHealthReport>(`/v1/satellite/${farm_id}`).then(r => r.data);

export const analyzeCropHealth = () =>
  api.post<Record<string, unknown>>("/v1/satellite/analyze", {}, { timeout: 120000 }).then(r => r.data);

export default api;
