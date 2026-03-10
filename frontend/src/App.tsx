import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Layout from './components/layout/Layout';
import ProtectedRoute from './components/auth/ProtectedRoute';
import Dashboard from './pages/Dashboard';
import Market from './pages/Market';
import StockDetail from './pages/StockDetail';
import Strategies from './pages/Strategies';
import DataDownload from './pages/DataDownload';
import TestSearch from './pages/TestSearch';
import TailwindTest from './pages/TailwindTest';
import KLineDashboard from './pages/KLineDashboard';
import BacktestReport from './pages/BacktestReport';
import AIAgent from './pages/AIAgent';
import Trading from './pages/Trading';
import Sentiment from './pages/Sentiment';
import News from './pages/News';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 公共路由 */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/test-search" element={<TestSearch />} />
        <Route path="/tailwind-test" element={<TailwindTest />} />
        
        {/* 受保护的路由 */}
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="market" element={<Market />} />
          <Route path="stock/:code" element={<StockDetail />} />
          <Route path="strategies" element={<Strategies />} />
          <Route path="data-download" element={<DataDownload />} />
          <Route path="kline" element={<KLineDashboard />} />
          <Route path="backtest-report" element={<BacktestReport />} />
          <Route path="ai-agent" element={<AIAgent />} />
          <Route path="trading" element={<Trading />} />
          <Route path="sentiment" element={<Sentiment />} />
          <Route path="news" element={<News />} />
          <Route path="profile" element={<Profile />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;