import { Row, Col, Card, Statistic, Table, Tag, Spin } from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  TrophyOutlined,
} from '@ant-design/icons';
import { useState, useEffect } from 'react';
import { stockService } from '@services/stock';

interface Stock {
  code: string;
  name: string;
  price?: number;
  change?: number;
  change_pct?: number;
  volume?: number;
}

const Dashboard = () => {
  const [loading, setLoading] = useState(false);
  const [stocks, setStocks] = useState<Stock[]>([]);

  // 获取股票列表
  useEffect(() => {
    const fetchStocks = async () => {
      try {
        setLoading(true);
        const response = await stockService.getStockList({ page: 1, page_size: 10 });
        
        if (response.code === 200 && response.data) {
          // 转换数据格式
          const stockList = response.data.items || [];
          setStocks(stockList);
        }
      } catch (error) {
        console.error('获取股票列表失败:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStocks();
  }, []);

  const columns = [
    {
      title: '代码',
      dataIndex: 'code',
      key: 'code',
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '最新价',
      dataIndex: 'price',
      key: 'price',
      render: (price: number) => `¥${price.toFixed(2)}`,
    },
    {
      title: '涨跌',
      dataIndex: 'change',
      key: 'change',
      render: (change: number, record: any) => (
        <span className={change > 0 ? 'text-up' : change < 0 ? 'text-down' : 'text-flat'}>
          {change > 0 ? '+' : ''}{change.toFixed(2)}
        </span>
      ),
    },
    {
      title: '涨跌幅',
      dataIndex: 'change_pct',
      key: 'change_pct',
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
      render: (volume: number) => `${(volume / 10000).toFixed(2)}万`,
    },
  ];

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>仪表板</h1>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总资产"
              value={112893}
              prefix="¥"
              precision={2}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日盈亏"
              value={12893}
              precision={2}
              valueStyle={{ color: '#cf1322' }}
              prefix={<ArrowUpOutlined />}
              suffix="¥"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="持仓数"
              value={3}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="胜率"
              value={65.4}
              precision={1}
              suffix="%"
              valueStyle={{ color: '#3f8600' }}
              prefix={<TrophyOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 关注股票 */}
      <Card title="关注股票" style={{ marginBottom: 24 }}>
        <Spin spinning={loading}>
          <Table
            dataSource={stocks}
            columns={columns}
            pagination={false}
            size="middle"
            rowKey="code"
          />
        </Spin>
      </Card>
    </div>
  );
};

export default Dashboard;
