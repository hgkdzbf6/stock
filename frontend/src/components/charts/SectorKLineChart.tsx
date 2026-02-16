/** 板块K线图组件 - 显示指定板块的K线图 */
import { useState, useEffect } from 'react';
import { Spin, message, Select, Space, Card, Row, Col, Statistic } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import EnhancedKLineChart from './EnhancedKLineChart';
import { stockService } from '@services/stock';
import { sectorService, Sector } from '@services/sector';

const { Option } = Select;

interface SectorKLineChartProps {
  height?: string;
  theme?: 'light' | 'dark';
}

export default function SectorKLineChart({ height = '600px', theme = 'light' }: SectorKLineChartProps) {
  const [loading, setLoading] = useState(false);
  const [sectors, setSectors] = useState<Sector[]>([]);
  const [selectedSector, setSelectedSector] = useState<string>('');
  const [kLineData, setKLineData] = useState<any[]>([]);
  const [sectorStats, setSectorStats] = useState({
    totalStocks: 0,
    upStocks: 0,
    downStocks: 0,
    avgChange: 0
  });

  // 加载板块列表
  useEffect(() => {
    loadSectors();
  }, []);

  // 当选择板块时加载数据
  useEffect(() => {
    if (selectedSector) {
      loadSectorData(selectedSector);
    }
  }, [selectedSector]);

  const loadSectors = async () => {
    try {
      const data = await sectorService.getSectorList();
      setSectors(data);
      if (data.length > 0) {
        setSelectedSector(data[0].code);
      }
    } catch (error) {
      message.error('加载板块列表失败');
      console.error('加载板块列表失败:', error);
    }
  };

  const loadSectorData = async (sectorCode: string) => {
    try {
      setLoading(true);
      
      // 获取板块的股票列表（第一页）
      const response = await stockService.getStockList({
        sector: sectorCode,
        page: 1,
        page_size: 50,
        data_source: 'auto'
      });

      // response已经包含items和total
      const stocks = response?.items || [];
      const total = response?.total || 0;
      
      // 计算板块统计
      const upCount = stocks.filter((s: any) => s.change_pct > 0).length;
      const downCount = stocks.filter((s: any) => s.change_pct < 0).length;
      const avgChange = stocks.length > 0 
        ? stocks.reduce((sum: number, s: any) => sum + (s.change_pct || 0), 0) / stocks.length 
        : 0;

      setSectorStats({
        totalStocks: total,
        upStocks: upCount,
        downStocks: downCount,
        avgChange: avgChange
      });

      // 模拟生成板块指数K线数据（实际应该从后端获取）
      const simulatedKLineData = generateSectorIndexKLine(stocks);
      setKLineData(simulatedKLineData);
    } catch (error) {
      message.error('加载板块数据失败');
      console.error('加载板块数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 生成板块指数K线数据（模拟）
  const generateSectorIndexKLine = (stocks: any[]): any[] => {
    // 这里应该是从后端API获取实际的板块指数数据
    // 目前使用模拟数据展示功能
    const endDate = new Date();
    const data: any[] = [];
    
    // 生成60天的K线数据
    for (let i = 60; i >= 0; i--) {
      const date = new Date(endDate);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      
      // 基于股票价格生成指数
      const baseIndex = 1000;
      const randomChange = (Math.random() - 0.5) * 50;
      const indexValue = baseIndex + randomChange - i * 2;
      
      const volatility = 10 + Math.random() * 20;
      const open = indexValue + (Math.random() - 0.5) * volatility;
      const close = indexValue + (Math.random() - 0.5) * volatility;
      const high = Math.max(open, close) + Math.random() * volatility;
      const low = Math.min(open, close) - Math.random() * volatility;
      
      data.push({
        date: dateStr,
        open: parseFloat(open.toFixed(2)),
        high: parseFloat(high.toFixed(2)),
        low: parseFloat(low.toFixed(2)),
        close: parseFloat(close.toFixed(2)),
        volume: Math.floor(Math.random() * 100000000)
      });
    }
    
    return data;
  };

  const handleSectorChange = (sectorCode: string) => {
    setSelectedSector(sectorCode);
  };

  const selectedSectorInfo = sectors.find(s => s.code === selectedSector);

  return (
    <Card 
      title={
        <Space>
          <span>板块K线图</span>
          <Select
            value={selectedSector}
            onChange={handleSectorChange}
            style={{ width: 200 }}
            placeholder="选择板块"
            loading={loading}
          >
            {sectors.map(sector => (
              <Option key={sector.code} value={sector.code}>
                {sector.name}
              </Option>
            ))}
          </Select>
        </Space>
      }
      extra={
        selectedSectorInfo && (
          <Space direction="vertical" size="small">
            <span style={{ color: '#999', fontSize: 12 }}>{selectedSectorInfo.description}</span>
          </Space>
        )
      }
    >
      {/* 板块统计信息 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Statistic
            title="股票总数"
            value={sectorStats.totalStocks}
            valueStyle={{ color: '#1890ff' }}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="上涨"
            value={sectorStats.upStocks}
            valueStyle={{ color: '#cf1322' }}
            prefix={<ArrowUpOutlined />}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="下跌"
            value={sectorStats.downStocks}
            valueStyle={{ color: '#3f8600' }}
            prefix={<ArrowDownOutlined />}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="平均涨跌"
            value={sectorStats.avgChange}
            precision={2}
            valueStyle={{ 
              color: sectorStats.avgChange >= 0 ? '#cf1322' : '#3f8600' 
            }}
            suffix="%"
            prefix={sectorStats.avgChange >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
          />
        </Col>
      </Row>

      {/* K线图 */}
      <Spin spinning={loading}>
        {kLineData.length > 0 ? (
          <EnhancedKLineChart
            data={kLineData}
            title={`${selectedSectorInfo?.name || selectedSector} 板块指数`}
            subtitle={selectedSectorInfo?.description || ''}
            height={height}
            showVolume={true}
            theme={theme}
          />
        ) : (
          <div style={{ 
            textAlign: 'center', 
            padding: '100px 0',
            color: '#999'
          }}>
            <p>请选择板块查看K线图</p>
          </div>
        )}
      </Spin>
    </Card>
  );
}