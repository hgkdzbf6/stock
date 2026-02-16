import { useState } from 'react';
import { Table, Button, Tag, Space, Modal, Form, Input, Select, DatePicker, InputNumber, message, Spin, Card, Row, Col, Statistic, Tabs, Divider } from 'antd';
import { PlusOutlined, PlayCircleOutlined, BarChartOutlined, LineChartOutlined, FileTextOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import { Line, LineChart, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useNavigate } from 'react-router-dom';

const { RangePicker } = DatePicker;
const { Option } = Select;

interface Strategy {
  key: string;
  id: number;
  name: string;
  type: string;
  description: string;
  status: string;
  total_return?: number;
  sharpe_ratio?: number;
  created_at: string;
}

interface BacktestResult {
  stock_code: string;
  start_date: string;
  end_date: string;
  frequency: string;
  initial_capital: number;
  final_capital: number;
  metrics: {
    total_return: number;
    annual_return: number;
    max_drawdown: number;
    sharpe_ratio: number;
    win_rate: number;
    trade_count: number;
    profit_loss_ratio: number;
    volatility: number;
    calmar_ratio: number;
  };
  trades: Array<{
    date: string;
    type: string;
    price: number;
    amount: number;
    cash: number;
    shares: number;
    total_value: number;
  }>;
  equity_curve: Array<{
    date: string;
    total_value: number;
    cumulative_return: number;
    drawdown: number;
  }>;
}

const Strategies = () => {
  const navigate = useNavigate();
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [backtestModalVisible, setBacktestModalVisible] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null);
  const [backtestLoading, setBacktestLoading] = useState(false);
  const [backtestResult, setBacktestResult] = useState<BacktestResult | null>(null);
  const [form] = Form.useForm();

  const mockStrategies: Strategy[] = [
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
      status: 'active',
      total_return: 8.5,
      sharpe_ratio: 0.8,
      created_at: '2026-02-03',
    },
    {
      key: '4',
      id: 4,
      name: '布林带策略',
      type: 'BOLL',
      description: '基于布林带突破交易',
      status: 'active',
      total_return: 10.2,
      sharpe_ratio: 0.95,
      created_at: '2026-02-04',
    },
  ];

  const handleBacktest = (record: Strategy) => {
    setSelectedStrategy(record);
    setBacktestResult(null);
    form.resetFields();
    form.setFieldsValue({
      strategy_type: record.type,
      start_date: dayjs().subtract(6, 'month'),
      end_date: dayjs(),
      initial_capital: 100000,
    });
    setBacktestModalVisible(true);
  };

  const handleBacktestSubmit = async () => {
    try {
      const values = await form.validateFields();
      setBacktestLoading(true);

      const response = await fetch(`http://localhost:8000/api/v1/strategies/${selectedStrategy?.id}/backtest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          stock_code: values.stock_code,
          start_date: values.dateRange[0].format('YYYY-MM-DD'),
          end_date: values.dateRange[1].format('YYYY-MM-DD'),
          frequency: values.frequency,
          initial_capital: values.initial_capital,
          strategy_type: values.strategy_type,
          custom_params: getCustomParams(values),
        }),
      });

      const result = await response.json();

      if (result.code === 200) {
        setBacktestResult(result.data);
        message.success('回测完成！');
      } else {
        message.error('回测失败：' + result.message);
      }
    } catch (error) {
      console.error('回测错误:', error);
      message.error('回测失败，请检查参数');
    } finally {
      setBacktestLoading(false);
    }
  };

  const getCustomParams = (values: any) => {
    const params: any = {};
    const strategyType = values.strategy_type;

    if (strategyType === 'MA') {
      if (values.short_window) params.short_window = values.short_window;
      if (values.long_window) params.long_window = values.long_window;
      if (values.stop_loss) params.stop_loss = values.stop_loss;
    } else if (strategyType === 'RSI') {
      if (values.rsi_window) params.rsi_window = values.rsi_window;
      if (values.oversold) params.oversold = values.oversold;
      if (values.overbought) params.overbought = values.overbought;
    } else if (strategyType === 'BOLL') {
      if (values.boll_window) params.boll_window = values.boll_window;
      if (values.num_std) params.num_std = values.num_std;
    } else if (strategyType === 'MACD') {
      if (values.fast) params.fast = values.fast;
      if (values.slow) params.slow = values.slow;
      if (values.signal) params.signal = values.signal;
    }

    return Object.keys(params).length > 0 ? params : null;
  };

  const columns: ColumnsType<Strategy> = [
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
      render: (value: number) => (
        <span style={{ color: value > 0 ? '#52c41a' : '#ff4d4f' }}>
          {value > 0 ? '+' : ''}{value?.toFixed(2)}%
        </span>
      ),
    },
    {
      title: '夏普比率',
      dataIndex: 'sharpe_ratio',
      key: 'sharpe_ratio',
      width: 100,
      render: (value: number) => value?.toFixed(2) || '-',
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
            onClick={() => handleBacktest(record)}
          >
            回测
          </Button>
          <Button
            size="small"
            icon={<BarChartOutlined />}
            onClick={() => message.info('优化功能开发中')}
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
        <Button type="primary" icon={<PlusOutlined />} onClick={() => message.info('新建策略功能开发中')}>
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

      {/* 回测模态框 */}
      <Modal
        title={`回测: ${selectedStrategy?.name}`}
        open={backtestModalVisible}
        onCancel={() => setBacktestModalVisible(false)}
        width={1200}
        footer={null}
      >
        <Spin spinning={backtestLoading}>
          <Form form={form} layout="vertical">
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  label="股票代码"
                  name="stock_code"
                  rules={[{ required: true, message: '请输入股票代码' }]}
                >
                  <Input placeholder="例如: 600771" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  label="策略类型"
                  name="strategy_type"
                  rules={[{ required: true, message: '请选择策略类型' }]}
                >
                  <Select>
                    <Option value="MA">双均线策略</Option>
                    <Option value="RSI">RSI策略</Option>
                    <Option value="BOLL">布林带策略</Option>
                    <Option value="MACD">MACD策略</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  label="回测周期"
                  name="dateRange"
                  rules={[{ required: true, message: '请选择回测周期' }]}
                >
                  <RangePicker style={{ width: '100%' }} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  label="数据频率"
                  name="frequency"
                  initialValue="daily"
                >
                  <Select>
                    <Option value="daily">日线</Option>
                    <Option value="60min">60分钟</Option>
                    <Option value="30min">30分钟</Option>
                    <Option value="15min">15分钟</Option>
                    <Option value="5min">5分钟</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Form.Item
              label="初始资金"
              name="initial_capital"
              rules={[{ required: true, message: '请输入初始资金' }]}
            >
              <InputNumber
                style={{ width: '100%' }}
                min={10000}
                step={10000}
                formatter={(value) => `¥ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                parser={(value) => (value ? Number(value.replace(/¥\s?|(,*)/g, '')) : 10000) as number}
              />
            </Form.Item>

            <Divider>策略参数</Divider>

            <Row gutter={16}>
              <Col span={8}>
                <Form.Item
                  label="短期均线周期"
                  name="short_window"
                >
                  <InputNumber min={1} max={60} style={{ width: '100%' }} placeholder="默认: 5" />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  label="长期均线周期"
                  name="long_window"
                >
                  <InputNumber min={1} max={200} style={{ width: '100%' }} placeholder="默认: 20" />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  label="止损比例 (%)"
                  name="stop_loss"
                >
                  <InputNumber min={0} max={100} style={{ width: '100%' }} placeholder="默认: 10" />
                </Form.Item>
              </Col>
            </Row>

            <Form.Item style={{ textAlign: 'right' }}>
              <Button onClick={() => setBacktestModalVisible(false)} style={{ marginRight: 8 }}>
                取消
              </Button>
              <Button type="primary" onClick={handleBacktestSubmit}>
                开始回测
              </Button>
            </Form.Item>
          </Form>

          {/* 回测结果 */}
          {backtestResult && (
            <div style={{ marginTop: 24 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <Divider orientation="left" style={{ margin: 0, flex: 1 }}>回测结果</Divider>
                <Button 
                  type="primary" 
                  icon={<FileTextOutlined />} 
                  onClick={() => {
                    navigate('/backtest-report', { 
                      state: { 
                        backtestData: backtestResult,
                        strategyName: selectedStrategy?.name 
                      } 
                    });
                  }}
                >
                  查看详细报告
                </Button>
              </div>
              
              <Row gutter={16} style={{ marginBottom: 16 }}>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="总收益率"
                      value={backtestResult.metrics.total_return * 100}
                      precision={2}
                      suffix="%"
                      valueStyle={{ color: backtestResult.metrics.total_return > 0 ? '#52c41a' : '#ff4d4f' }}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="年化收益率"
                      value={backtestResult.metrics.annual_return * 100}
                      precision={2}
                      suffix="%"
                      valueStyle={{ color: backtestResult.metrics.annual_return > 0 ? '#52c41a' : '#ff4d4f' }}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="最大回撤"
                      value={backtestResult.metrics.max_drawdown * 100}
                      precision={2}
                      suffix="%"
                      valueStyle={{ color: '#ff4d4f' }}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="夏普比率"
                      value={backtestResult.metrics.sharpe_ratio}
                      precision={2}
                      valueStyle={{ color: backtestResult.metrics.sharpe_ratio > 1 ? '#52c41a' : '#faad14' }}
                    />
                  </Card>
                </Col>
              </Row>

              <Row gutter={16} style={{ marginBottom: 16 }}>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="胜率"
                      value={backtestResult.metrics.win_rate * 100}
                      precision={2}
                      suffix="%"
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="交易次数"
                      value={backtestResult.metrics.trade_count}
                      suffix="次"
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="盈亏比"
                      value={backtestResult.metrics.profit_loss_ratio}
                      precision={2}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card>
                    <Statistic
                      title="卡尔马比率"
                      value={backtestResult.metrics.calmar_ratio}
                      precision={2}
                    />
                  </Card>
                </Col>
              </Row>

              <Card title="净值曲线" style={{ marginBottom: 16 }}>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={backtestResult.equity_curve.slice(0, 100)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" hide />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="cumulative_return" stroke="#1890ff" name="累计收益率" />
                    <Line type="monotone" dataKey="drawdown" stroke="#ff4d4f" name="回撤" />
                  </LineChart>
                </ResponsiveContainer>
              </Card>

              <Card title="交易明细">
                <Table
                  columns={[
                    { title: '日期', dataIndex: 'date', key: 'date', width: 180 },
                    {
                      title: '类型',
                      dataIndex: 'type',
                      key: 'type',
                      width: 100,
                      render: (type: string) => (
                        <Tag color={type === '买入' ? 'green' : 'red'}>{type}</Tag>
                      ),
                    },
                    { title: '价格', dataIndex: 'price', key: 'price', render: (v: number) => v.toFixed(2) },
                    { title: '数量', dataIndex: 'amount', key: 'amount', render: (v: number) => v.toFixed(2) },
                    { title: '现金', dataIndex: 'cash', key: 'cash', render: (v: number) => v.toFixed(2) },
                    { title: '持股', dataIndex: 'shares', key: 'shares', render: (v: number) => v.toFixed(0) },
                    { title: '总资产', dataIndex: 'total_value', key: 'total_value', render: (v: number) => v.toFixed(2) },
                  ]}
                  dataSource={backtestResult.trades}
                  pagination={{ pageSize: 10 }}
                  scroll={{ y: 300 }}
                  size="small"
                />
              </Card>
            </div>
          )}
        </Spin>
      </Modal>
    </div>
  );
};

export default Strategies;