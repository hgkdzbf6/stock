/** 板块K线图组件 - 显示指定板块的K线图 */
import { useState, useEffect, useMemo } from 'react';
import { Spin, message, AutoComplete, Space, Card, Row, Col, Statistic, Tag } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, SearchOutlined } from '@ant-design/icons';
import EnhancedKLineChart from './EnhancedKLineChart';
import { sectorService, Sector } from '@services/sector';

interface SectorKLineChartProps {
  height?: string;
  theme?: 'light' | 'dark';
}

export default function SectorKLineChart({ height = '600px', theme = 'light' }: SectorKLineChartProps) {
  const [loading, setLoading] = useState(false);
  const [loadingSectors, setLoadingSectors] = useState(false);
  const [sectors, setSectors] = useState<Sector[]>([]);
  const [selectedSector, setSelectedSector] = useState<string>('');
  const [searchValue, setSearchValue] = useState<string>('');
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

  // 过滤板块列表（支持模糊搜索）
  const filteredSectors = useMemo(() => {
    if (!searchValue.trim()) {
      return sectors;
    }
    
    const lowerSearch = searchValue.toLowerCase();
    return sectors.filter(sector => 
      sector.name.toLowerCase().includes(lowerSearch) ||
      sector.code.toLowerCase().includes(lowerSearch)
    );
  }, [sectors, searchValue]);

  // AutoComplete选项数据
  const autoCompleteOptions = useMemo(() => {
    return filteredSectors.map(sector => ({
      value: sector.code,
      label: (
        <div>
          <span style={{ fontWeight: 'bold' }}>{sector.name}</span>
          <Tag color={sector.type === 'industry' ? 'blue' : 'purple'} style={{ marginLeft: 8 }}>
            {sector.type === 'industry' ? '行业' : '概念'}
          </Tag>
          <span style={{ color: '#999', marginLeft: 8, fontSize: 12 }}>{sector.market}</span>
        </div>
      )
    }));
  }, [filteredSectors]);

  const loadSectors = async () => {
    try {
      setLoadingSectors(true);
      const data = await sectorService.getSectorList();
      setSectors(data);
      if (data.length > 0) {
        setSelectedSector(data[0].code);
      }
    } catch (error) {
      message.error('加载板块列表失败');
      console.error('加载板块列表失败:', error);
    } finally {
      setLoadingSectors(false);
    }
  };

  const loadSectorData = async (sectorCode: string) => {
    try {
      setLoading(true);
      
      // 获取板块的股票列表（第一页，最多50只）
      const stocksResponse = await sectorService.getStocksBySector(
        sectorCode,
        1,
        50
      );

      const stocks = stocksResponse?.items || [];
      const total = stocksResponse?.total || 0;
      
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

      // 获取真实的板块K线数据
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 90);
      
      const klineResponse = await sectorService.getKlineData({
        code: sectorCode,
        freq: 'daily',
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0]
      });
      
      if (klineResponse && klineResponse.data && klineResponse.data.length > 0) {
        setKLineData(klineResponse.data);
      } else {
        message.warning('暂无板块K线数据');
        setKLineData([]);
      }
    } catch (error) {
      message.error('加载板块数据失败');
      console.error('加载板块数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectedSectorInfo = sectors.find(s => s.code === selectedSector);

  return (
    <Card 
      title={
        <Space>
          <span>板块K线图</span>
          <AutoComplete
            value={selectedSector}
            onChange={setSelectedSector}
            options={autoCompleteOptions}
            placeholder="搜索板块（支持代码或名称）"
            style={{ width: 400 }}
            filterOption={(inputValue, option) => {
              const sector = sectors.find(s => s.code === option?.value);
              if (!sector) return false;
              return (
                sector.name.toLowerCase().includes(inputValue.toLowerCase()) ||
                sector.code.toLowerCase().includes(inputValue.toLowerCase())
              );
            }}
            notFoundContent="未找到匹配的板块"
            disabled={loadingSectors}
            prefix={<SearchOutlined />}
          />
        </Space>
      }
      extra={
        selectedSectorInfo && (
          <Space direction="vertical" size="small">
            <Tag color={selectedSectorInfo.type === 'industry' ? 'blue' : 'purple'}>
              {selectedSectorInfo.type === 'industry' ? '行业板块' : '概念板块'}
            </Tag>
            <span style={{ color: '#999', fontSize: 12 }}>{selectedSectorInfo.market} - {selectedSectorInfo.description}</span>
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