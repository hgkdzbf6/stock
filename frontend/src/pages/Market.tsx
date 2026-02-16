import { useState, useEffect, useCallback } from 'react';
import { Input, Table, Tag, Button, Select, Spin, message, DatePicker } from 'antd';
import { SearchOutlined, ReloadOutlined, CalendarOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { useNavigate } from 'react-router-dom';
import { stockService } from '@services/stock';
import { sectorService } from '@services/sector';
import dayjs, { Dayjs } from 'dayjs';

const { Option } = Select;

interface Stock {
  code: string;
  name: string;
  market?: string;
  sector?: string;
  price?: number;
  change?: number;
  change_pct?: number;
  volume?: number;
  amount?: number;
}

const Market = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });
  const [filters, setFilters] = useState({
    keyword: '',
    sector: '',
  });
  const [sectors, setSectors] = useState<any[]>([]);
  const [selectedDate, setSelectedDate] = useState<Dayjs | null>(dayjs());
  const [dataSource, setDataSource] = useState('auto'); // 默认auto模式

  // 获取股票列表
  const fetchStocks = useCallback(async () => {
    try {
      setLoading(true);
      const response = await stockService.getStockList({
        page: pagination.current,
        page_size: pagination.pageSize,
        keyword: filters.keyword,
        sector: filters.sector || undefined,
        data_source: dataSource,
      });

      if (response.code === 200 && response.data) {
        setStocks(response.data.items || []);
        setPagination({
          ...pagination,
          total: response.data.total || 0,
        });
      }
    } catch (error) {
      console.error('获取股票列表失败:', error);
      message.error('获取股票列表失败');
    } finally {
      setLoading(false);
    }
  }, [pagination.current, pagination.pageSize, filters.keyword, filters.sector, dataSource]);

  // 初始加载
  // 加载板块列表
  useEffect(() => {
    sectorService.getSectorList()
      .then(setSectors)
      .catch(error => {
        console.error('获取板块列表失败:', error);
      });
  }, []);
  
  useEffect(() => {
    fetchStocks();
  }, [fetchStocks]);

  // 搜索处理
  const handleSearch = (keyword: string) => {
    setFilters({ ...filters, keyword });
    setPagination({ ...pagination, current: 1 });
  };

  // 板块过滤
  const handleSectorChange = (sector: string | null) => {
    setFilters({ ...filters, sector: sector || '' });
    setPagination({ ...pagination, current: 1 });
  };

  // 数据源变化
  const handleDataSourceChange = (source: string) => {
    setDataSource(source);
    setPagination({ ...pagination, current: 1 });
  };

  // 日期变化
  const handleDateChange = (date: Dayjs | null) => {
    setSelectedDate(date);
    if (date) {
      // 重新获取数据
      setPagination({ ...pagination, current: 1 });
    }
  };

  // 详情跳转
  const handleDetail = (code: string) => {
    navigate(`/stock/${code}`);
  };

  // 刷新
  const handleRefresh = () => {
    fetchStocks();
  };

  // 分页变化
  const handleTableChange = (newPagination: any) => {
    setPagination({
      current: newPagination.current,
      pageSize: newPagination.pageSize,
      total: pagination.total,
    });
  };

  const columns: ColumnsType<any> = [
    {
      title: '代码',
      dataIndex: 'code',
      key: 'code',
      fixed: 'left',
      width: 100,
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      fixed: 'left',
      width: 120,
    },
    {
      title: '市场',
      dataIndex: 'market',
      key: 'market',
      width: 80,
    },
    {
      title: '板块',
      dataIndex: 'sector',
      key: 'sector',
      width: 100,
    },
    {
      title: '最新价',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: (price: number) => `¥${price.toFixed(2)}`,
    },
    {
      title: '涨跌',
      dataIndex: 'change',
      key: 'change',
      width: 100,
      render: (change: number) => (
        <span className={change > 0 ? 'text-up' : change < 0 ? 'text-down' : 'text-flat'}>
          {change > 0 ? '+' : ''}{change.toFixed(2)}
        </span>
      ),
    },
    {
      title: '涨跌幅',
      dataIndex: 'change_pct',
      key: 'change_pct',
      width: 100,
      render: (change_pct: number) => (
        <Tag color={change_pct > 0 ? 'red' : change_pct < 0 ? 'green' : 'default'}>
          {change_pct > 0 ? '+' : ''}{change_pct.toFixed(2)}%
        </Tag>
      ),
    },
    {
      title: '成交量',
      dataIndex: 'volume',
      key: 'volume',
      width: 100,
      render: (volume: number) => `${(volume / 10000).toFixed(2)}万`,
    },
    {
      title: '成交额',
      dataIndex: 'amount',
      key: 'amount',
      width: 100,
      render: (amount: number) => `${(amount / 10000).toFixed(2)}万`,
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right',
      width: 120,
      render: (_, record) => (
        <Button type="primary" size="small" onClick={() => handleDetail(record.code)}>
          详情
        </Button>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', gap: 16, alignItems: 'center' }}>
        <Input.Search
          placeholder="搜索股票代码或名称"
          allowClear
          enterButton={<SearchOutlined />}
          style={{ width: 300 }}
          onSearch={handleSearch}
        />
        <Select
          placeholder="选择板块"
          allowClear
          style={{ width: 150 }}
          onChange={handleSectorChange}
        >
          {/* ✅ 使用动态板块列表 */}
          {sectors.map(sector => (
            <Option key={sector.code} value={sector.code}>
              {sector.name}
            </Option>
          ))}
        </Select>
        <Select
          placeholder="数据源"
          value={dataSource}
          onChange={handleDataSourceChange}
          style={{ width: 150 }}
        >
          <Option value="auto">自动</Option>
          <Option value="baostock">BaoStock</Option>
          <Option value="akshare">AkShare</Option>
          <Option value="tushare">Tushare</Option>
          <Option value="sina">新浪</Option>
          <Option value="tencent">腾讯</Option>
          <Option value="eastmoney">东方财富</Option>
        </Select>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <CalendarOutlined style={{ color: '#666' }} />
          <DatePicker
            value={selectedDate}
            onChange={handleDateChange}
            placeholder="选择交易日"
            allowClear={false}
            style={{ width: 180 }}
          />
        </div>
        <Button icon={<ReloadOutlined />} onClick={handleRefresh}>刷新</Button>
      </div>

      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={stocks}
          rowKey="code"
          scroll={{ x: 1200 }}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            onChange: (page, pageSize) => {
              setPagination({ ...pagination, current: page, pageSize: pageSize || 10 });
            },
          }}
          onChange={handleTableChange}
        />
      </Spin>
    </div>
  );
};

export default Market;