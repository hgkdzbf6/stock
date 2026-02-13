import { useState } from 'react';
import { Input, Table, Tag, Button, Space, Select } from 'antd';
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Option } = Select;

const Market = () => {
  const [searchKeyword, setSearchKeyword] = useState('');
  const [selectedStock, setSelectedStock] = useState<string | null>(null);

  const mockStocks = [
    {
      key: '1',
      code: '600771',
      name: '东阳光',
      market: '沪A',
      sector: '医药',
      price: 10.5,
      change: 0.2,
      change_pct: 1.94,
      volume: 1000000,
      amount: 10500000,
    },
    {
      key: '2',
      code: '000001',
      name: '平安银行',
      market: '深A',
      sector: '银行',
      price: 12.3,
      change: -0.15,
      change_pct: -1.2,
      volume: 2000000,
      amount: 24600000,
    },
    {
      key: '3',
      code: '600519',
      name: '贵州茅台',
      market: '沪A',
      sector: '白酒',
      price: 1850.0,
      change: 25.5,
      change_pct: 1.4,
      volume: 50000,
      amount: 92500000,
    },
    {
      key: '4',
      code: '000002',
      name: '万科A',
      market: '深A',
      sector: '房地产',
      price: 8.5,
      change: -0.1,
      change_pct: -1.16,
      volume: 1500000,
      amount: 12750000,
    },
    {
      key: '5',
      code: '600000',
      name: '浦发银行',
      market: '沪A',
      sector: '银行',
      price: 7.2,
      change: 0.05,
      change_pct: 0.7,
      volume: 3000000,
      amount: 21600000,
    },
  ];

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
        <Button type="primary" size="small" onClick={() => setSelectedStock(record.code)}>
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
          onSearch={setSearchKeyword}
        />
        <Select
          placeholder="选择板块"
          allowClear
          style={{ width: 150 }}
        >
          <Option value="医药">医药</Option>
          <Option value="银行">银行</Option>
          <Option value="白酒">白酒</Option>
          <Option value="房地产">房地产</Option>
        </Select>
        <Button icon={<ReloadOutlined />}>刷新</Button>
      </div>

      <Table
        columns={columns}
        dataSource={mockStocks}
        scroll={{ x: 1200 }}
        pagination={{
          total: mockStocks.length,
          pageSize: 10,
          showSizeChanger: true,
          showQuickJumper: true,
        }}
      />
    </div>
  );
};

export default Market;
