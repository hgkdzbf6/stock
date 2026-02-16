import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Market from './pages/Market';
import StockDetail from './pages/StockDetail';
import Strategies from './pages/Strategies';
import DataDownload from './pages/DataDownload';
import TestSearch from './pages/TestSearch';
import TailwindTest from './pages/TailwindTest';
import KLineDashboard from './pages/KLineDashboard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<div>登录页面 - 待实现</div>} />
        <Route path="/test-search" element={<TestSearch />} />
        <Route path="/tailwind-test" element={<TailwindTest />} />
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="market" element={<Market />} />
          <Route path="stock/:code" element={<StockDetail />} />
          <Route path="strategies" element={<Strategies />} />
          <Route path="data-download" element={<DataDownload />} />
          <Route path="kline" element={<KLineDashboard />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;