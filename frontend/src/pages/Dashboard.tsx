import { Row, Col, Card, Statistic, Table, Tag } from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  DollarOutlined,
  TrophyOutlined,
} from '@ant-design/icons';

const Dashboard = () => {
  const mockStocks = [
    {
      key: '1',
      code: '600771',
      name: '东阳光',
      price: 10.5,
      change: 0.2,
      change_pct: 1.94,
      volume: 1000000,
    },
    {
      key: '2',
      code: '000001',
      name: '平安银行',
      price: 12.3,
      change: -0.15,
      change_pct: -1.2,
      volume: 2000000,
    },
    {
      key: '3',
      code: '600519',
      name: '贵州茅台',
      price: 1850.0,
      change: 25.5,
      change_pct: 1.4,
      volume: 50000,
    },
  ];

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
              prefix={<DollarOutlined />}
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
        <Table
          dataSource={mockStocks}
          columns={columns}
          pagination={false}
          size="middle"
        />
      </Card>
    </div>
  );
};

export default Dashboard;
