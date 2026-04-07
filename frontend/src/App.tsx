import { Routes, Route } from "react-router-dom";
import { LangProvider } from "./i18n/LangContext";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Greenhouses from "./pages/Greenhouses";
import GreenhouseDetail from "./pages/GreenhouseDetail";
import Batches from "./pages/Batches";
import Shipments from "./pages/Shipments";
import ShipmentDetail from "./pages/ShipmentDetail";
import Orders from "./pages/Orders";
import Quality from "./pages/Quality";
import Analyze from "./pages/Analyze";

function App() {
  return (
    <LangProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/greenhouses" element={<Greenhouses />} />
          <Route path="/greenhouses/:id" element={<GreenhouseDetail />} />
          <Route path="/batches" element={<Batches />} />
          <Route path="/shipments" element={<Shipments />} />
          <Route path="/shipments/:id" element={<ShipmentDetail />} />
          <Route path="/orders" element={<Orders />} />
          <Route path="/quality" element={<Quality />} />
          <Route path="/analyze" element={<Analyze />} />
        </Routes>
      </Layout>
    </LangProvider>
  );
}

export default App;
