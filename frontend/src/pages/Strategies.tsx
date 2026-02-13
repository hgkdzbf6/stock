import { Table, Button, Tag, Space } from 'antd';
import { PlusOutlined, PlayCircleOutlined, BarChartOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const Strategies = () => {
  const mockStrategies = [
    {
      key: '1',
      id: 1,
      name: '双均线策略',
      type: 'MA',
      description: '基于5日和20日均线交叉',
      status: 'active',
      total_return: 15.0,
      sharpe_ratio: 1.2,
      created_at: '2026-02-01',
    },
    {
      key: '2',
      id: 2,
      name: 'RSI策略',
      type: 'RSI',
      description: '基于RSI指标的超买超卖',
      status: 'active',
      total_return: 12.0,
      sharpe_ratio: 1.0,
      created_at: '2026-02-02',
    },
    {
      key: '3',
      id: 3,
      name: 'MACD策略',
      type: 'MACD',
      description: '基于MACD金叉死叉',
      status: 'inactive',
      total_return: 8.5,
      sharpe_ratio: 0.8,
      created_at: '2026-02-03',
    },
  ];

  const columns: ColumnsType<any> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
    },
    {
      title: '策略名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: string) => <Tag color="blue">{type}</Tag>,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={status === 'active' ? 'green' : 'default'}>
          {status === 'active' ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '总收益率',
      dataIndex: 'total_return',
      key: 'total_return',
      width: 120,
      render: (value: number) => `${value > 0 ? '+' : ''}${value.toFixed(2)}%`,
    },
    {
      title: '夏普比率',
      dataIndex: 'sharpe_ratio',
      key: 'sharpe_ratio',
      width: 100,
      render: (value: number) => value.toFixed(2),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 120,
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right',
      width: 180,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="primary"
            size="small"
            icon={<PlayCircleOutlined />}
            onClick={() => console.log('回测', record.id)}
          >
            回测
          </Button>
          <Button
            size="small"
            icon={<BarChartOutlined />}
            onClick={() => console.log('优化', record.id)}
          >
            优化
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h1 style={{ margin: 0 }}>策略管理</h1>
        <Button type="primary" icon={<PlusOutlined />}>
          新建策略
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={mockStrategies}
        scroll={{ x: 1400 }}
        pagination={{
          total: mockStrategies.length,
          pageSize: 10,
          showSizeChanger: true,
          showQuickJumper: true,
        }}
      />
    </div>
  );
};

export default Strategies;
