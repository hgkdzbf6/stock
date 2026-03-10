import { useEffect, useState } from 'react';
import { Table, Button, Tag, Space, Modal, Form, Input, Select, DatePicker, InputNumber, message, Spin, Card, Row, Col, Statistic, Divider, Empty } from 'antd';
import { PlusOutlined, PlayCircleOutlined, BarChartOutlined, FileTextOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import { Line, LineChart, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useNavigate } from 'react-router-dom';
import { strategyService } from '../services/strategy';

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
    open?: number;
    high?: number;
    low?: number;
    close?: number;
    volume?: number;
  }>;
}

const Strategies = () => {
  const navigate = useNavigate();
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [listLoading, setListLoading] = useState(false);
  const [backtestModalVisible, setBacktestModalVisible] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null);
  const [backtestLoading, setBacktestLoading] = useState(false);
  const [backtestResult, setBacktestResult] = useState<BacktestResult | null>(null);
  const [form] = Form.useForm();

  const loadStrategies = async () => {
    try {
      setListLoading(true);
      const response = await strategyService.getStrategies();
      const items = response?.data?.items || [];
      const normalized: Strategy[] = items.map((item: any) => ({
        key: String(item.id),
        id: item.id,
        name: item.name,
        type: item.type,
        description: item.description || '',
        status: item.status || 'active',
        total_return: item.performance?.total_return ? item.performance.total_return * 100 : 0,
        sharpe_ratio: item.performance?.sharpe_ratio || 0,
        created_at: item.created_at ? item.created_at.slice(0, 10) : '-',
      }));
      setStrategies(normalized);
    } catch (error) {
      console.error('加载策略列表失败:', error);
      message.error('加载策略列表失败');
    } finally {
      setListLoading(false);
    }
  };

  useEffect(() => {
    loadStrategies();
  }, []);

  const handleBacktest = (record: Strategy) => {
    setSelectedStrategy(record);
    setBacktestResult(null);
    form.resetFields();
    form.setFieldsValue({
      strategy_type: record.type,
      dateRange: [dayjs().subtract(1, 'year'), dayjs()],
      initial_capital: 100000,
    });
    setBacktestModalVisible(true);
  };

  const handleBacktestSubmit = async () => {
    try {
      const values = await form.validateFields();
      setBacktestLoading(true);

      const result = await strategyService.runBacktest(selectedStrategy?.id || 0, {
        stock_code: values.stock_code,
        start_date: values.dateRange[0].format('YYYY-MM-DD'),
        end_date: values.dateRange[1].format('YYYY-MM-DD'),
        frequency: values.frequency,
        initial_capital: values.initial_capital,
        strategy_type: values.strategy_type,
        custom_params: getCustomParams(values),
      } as any);

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

  const handleOptimize = async () => {
    try {
      const values = await form.validateFields();
      message.loading({ content: '参数优化中...', key: 'optimize' });

      // 定义参数优化范围
      const optimizeParams: any = {
        stock_code: values.stock_code,
        start_date: values.dateRange[0].format('YYYY-MM-DD'),
        end_date: values.dateRange[1].format('YYYY-MM-DD'),
        strategy_type: values.strategy_type,
      };

      // 根据策略类型设置参数范围
      const strategyType = values.strategy_type;
      if (strategyType === 'MA') {
        optimizeParams.param_ranges = {
          short_window: [5, 10, 15, 20],
          long_window: [20, 30, 40, 60],
          stop_loss: [0.05, 0.1, 0.15, 0.2]
        };
      } else if (strategyType === 'RSI') {
        optimizeParams.param_ranges = {
          rsi_window: [10, 14, 20, 25],
          oversold: [20, 25, 30, 35],
          overbought: [65, 70, 75, 80]
        };
      } else if (strategyType === 'BOLL') {
        optimizeParams.param_ranges = {
          boll_window: [10, 15, 20, 25, 30],
          num_std: [1.5, 2.0, 2.5, 3.0]
        };
      } else if (strategyType === 'MACD') {
        optimizeParams.param_ranges = {
          fast: [8, 12, 16, 20],
          slow: [20, 26, 32, 40],
          signal: [6, 9, 12]
        };
      } else if (strategyType === 'TURTLE') {
        optimizeParams.param_ranges = {
          period: [10, 15, 20, 30, 40]
        };
      } else if (strategyType === 'KDJ') {
        optimizeParams.param_ranges = {
          fastk_period: [7, 9, 12, 15],
          slowk_period: [2, 3, 5],
          slowd_period: [2, 3, 5],
          kdj_buy: [15, 20, 25, 30],
          kdj_sell: [70, 75, 80, 85]
        };
      } else if (strategyType === 'ATR') {
        optimizeParams.param_ranges = {
          atr_period: [10, 14, 20, 25],
          atr_multiplier: [1.5, 2.0, 2.5, 3.0]
        };
      } else if (strategyType === 'DUAL_THRUST') {
        optimizeParams.param_ranges = {
          n_days: [3, 5, 7, 10],
          k1: [0.5, 0.6, 0.7, 0.8, 0.9],
          k2: [0.5, 0.6, 0.7, 0.8, 0.9]
        };
      } else if (strategyType === 'HANS123') {
        optimizeParams.param_ranges = {
          morning_bars: [4, 6, 8, 10],
          breakout_percent: [0.05, 0.1, 0.15, 0.2]
        };
      }

      const result = await strategyService.optimizeStrategy(
        selectedStrategy?.id || 0,
        optimizeParams,
        'grid_search'
      );

      if (result.code === 200 && result.data?.best_params) {
        form.setFieldsValue(result.data.best_params);
        message.success({ content: '参数优化完成！', key: 'optimize', duration: 3 });
      } else {
        message.error({ content: result.message || '参数优化失败', key: 'optimize' });
      }
    } catch (error) {
      console.error('优化错误:', error);
      message.error({ content: '参数优化失败', key: 'optimize' });
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
    } else if (strategyType === 'TURTLE') {
      if (values.period) params.period = values.period;
    } else if (strategyType === 'KDJ') {
      if (values.fastk_period) params.fastk_period = values.fastk_period;
      if (values.slowk_period) params.slowk_period = values.slowk_period;
      if (values.slowd_period) params.slowd_period = values.slowd_period;
      if (values.kdj_buy) params.kdj_buy = values.kdj_buy;
      if (values.kdj_sell) params.kdj_sell = values.kdj_sell;
    } else if (strategyType === 'ATR') {
      if (values.atr_period) params.atr_period = values.atr_period;
      if (values.atr_multiplier) params.atr_multiplier = values.atr_multiplier;
    } else if (strategyType === 'DUAL_THRUST') {
      if (values.n_days) params.n_days = values.n_days;
      if (values.k1) params.k1 = values.k1;
      if (values.k2) params.k2 = values.k2;
    } else if (strategyType === 'HANS123') {
      if (values.morning_bars) params.morning_bars = values.morning_bars;
      if (values.breakout_percent) params.breakout_percent = values.breakout_percent;
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
        loading={listLoading}
        locale={{ emptyText: <Empty description="暂无策略，请先创建策略" /> }}
        dataSource={strategies}
        scroll={{ x: 1400 }}
        pagination={{
          total: strategies.length,
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
                    <Option value="TURTLE">海龟交易策略</Option>
                    <Option value="KDJ">KDJ策略</Option>
                    <Option value="ATR">ATR策略</Option>
                    <Option value="DUAL_THRUST">Dual-Thrust策略</Option>
                    <Option value="HANS123">Hans123策略</Option>
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
                parser={(value) => value ? Number(value.replace(/¥\s?|(,*)/g, '')) as any : 10000}
              />
            </Form.Item>

            <Divider>策略参数</Divider>

            {/* 动态显示策略参数 */}
            <Form.Item noStyle shouldUpdate={(prevValues, currentValues) => prevValues.strategy_type !== currentValues.strategy_type}>
              {({ getFieldValue }) => {
                const strategyType = getFieldValue('strategy_type');
                
                if (strategyType === 'MA') {
                  return (
                    <Row gutter={16}>
                      <Col span={8}>
                        <Form.Item label="短期均线周期" name="short_window">
                          <InputNumber min={1} max={60} style={{ width: '100%' }} placeholder="默认: 5" />
                        </Form.Item>
                      </Col>
                      <Col span={8}>
                        <Form.Item label="长期均线周期" name="long_window">
                          <InputNumber min={1} max={200} style={{ width: '100%' }} placeholder="默认: 20" />
                        </Form.Item>
                      </Col>
                      <Col span={8}>
                        <Form.Item label="止损比例 (%)" name="stop_loss">
                          <InputNumber min={0} max={100} style={{ width: '100%' }} placeholder="默认: 10" />
                        </Form.Item>
                      </Col>
                    </Row>
                  );
                } else if (strategyType === 'RSI') {
                  return (
                    <Row gutter={16}>
                      <Col span={8}>
                        <Form.Item label="RSI周期" name="rsi_window">
                          <InputNumber min={5} max={30} style={{ width: '100%' }} placeholder="默认: 14" />
                        </Form.Item>
                      </Col>
                      <Col span={8}>
                        <Form.Item label="超卖阈值" name="oversold">
                          <InputNumber min={10} max={40} style={{ width: '100%' }} placeholder="默认: 30" />
                        </Form.Item>
                      </Col>
                      <Col span={8}>
                        <Form.Item label="超买阈值" name="overbought">
                          <InputNumber min={60} max={90} style={{ width: '100%' }} placeholder="默认: 70" />
                        </Form.Item>
                      </Col>
                    </Row>
                  );
                } else if (strategyType === 'BOLL') {
                  return (
                    <Row gutter={16}>
                      <Col span={12}>
                        <Form.Item label="布林带周期" name="boll_window">
                          <InputNumber min={5} max={50} style={{ width: '100%' }} placeholder="默认: 20" />
                        </Form.Item>
                      </Col>
                      <Col span={12}>
                        <Form.Item label="标准差倍数" name="num_std">
                          <InputNumber min={1} max={3} step={0.1} style={{ width: '100%' }} placeholder="默认: 2" />
                        </Form.Item>
                      </Col>
                    </Row>
                  );
                } else if (strategyType === 'MACD') {
                  return (
                    <Row gutter={16}>
                      <Col span={8}>
                        <Form.Item label="快线周期" name="fast">
                          <InputNumber min={5} max={20} style={{ width: '100%' }} placeholder="默认: 12" />
                        </Form.Item>
                      </Col>
                      <Col span={8}>
                        <Form.Item label="慢线周期" name="slow">
                          <InputNumber min={10} max={50} style={{ width: '100%' }} placeholder="默认: 26" />
                        </Form.Item>
                      </Col>
                      <Col span={8}>
                        <Form.Item label="信号线周期" name="signal">
                          <InputNumber min={5} max={20} style={{ width: '100%' }} placeholder="默认: 9" />
                        </Form.Item>
                      </Col>
                    </Row>
                  );
                } else if (strategyType === 'TURTLE') {
                  return (
                    <Row gutter={16}>
                      <Col span={8}>
                        <Form.Item label="突破周期（日）" name="period">
                          <InputNumber min={10} max={60} style={{ width: '100%' }} placeholder="默认: 20" />
                        </Form.Item>
                      </Col>
                    </Row>
                  );
                } else if (strategyType === 'KDJ') {
                  return (
                    <Row gutter={16}>
                      <Col span={6}>
                        <Form.Item label="快速K线周期" name="fastk_period">
                          <InputNumber min={5} max={20} style={{ width: '100%' }} placeholder="默认: 9" />
                        </Form.Item>
                      </Col>
                      <Col span={6}>
                        <Form.Item label="慢速K线周期" name="slowk_period">
                          <InputNumber min={1} max={10} style={{ width: '100%' }} placeholder="默认: 3" />
                        </Form.Item>
                      </Col>
                      <Col span={6}>
                        <Form.Item label="D线周期" name="slowd_period">
                          <InputNumber min={1} max={10} style={{ width: '100%' }} placeholder="默认: 3" />
                        </Form.Item>
                      </Col>
                      <Col span={6}>
                        <Form.Item label="买入阈值" name="kdj_buy">
                          <InputNumber min={5} max={40} style={{ width: '100%' }} placeholder="默认: 20" />
                        </Form.Item>
                      </Col>
                      <Col span={6}>
                        <Form.Item label="卖出阈值" name="kdj_sell">
                          <InputNumber min={60} max={95} style={{ width: '100%' }} placeholder="默认: 80" />
                        </Form.Item>
                      </Col>
                    </Row>
                  );
                } else if (strategyType === 'ATR') {
                  return (
                    <Row gutter={16}>
                      <Col span={12}>
                        <Form.Item label="ATR周期" name="atr_period">
                          <InputNumber min={5} max={30} style={{ width: '100%' }} placeholder="默认: 14" />
                        </Form.Item>
                      </Col>
                      <Col span={12}>
                        <Form.Item label="ATR倍数" name="atr_multiplier">
                          <InputNumber min={1} max={5} step={0.1} style={{ width: '100%' }} placeholder="默认: 2.0" />
                        </Form.Item>
                      </Col>
                    </Row>
                  );
                } else if (strategyType === 'DUAL_THRUST') {
                  return (
                    <Row gutter={16}>
                      <Col span={8}>
                        <Form.Item label="回看天数" name="n_days">
                          <InputNumber min={3} max={10} style={{ width: '100%' }} placeholder="默认: 5" />
                        </Form.Item>
                      </Col>
                      <Col span={8}>
                        <Form.Item label="上轨系数" name="k1">
                          <InputNumber min={0.5} max={1.0} step={0.1} style={{ width: '100%' }} placeholder="默认: 0.7" />
                        </Form.Item>
                      </Col>
                      <Col span={8}>
                        <Form.Item label="下轨系数" name="k2">
                          <InputNumber min={0.5} max={1.0} step={0.1} style={{ width: '100%' }} placeholder="默认: 0.7" />
                        </Form.Item>
                      </Col>
                    </Row>
                  );
                } else if (strategyType === 'HANS123') {
                  return (
                    <Row gutter={16}>
                      <Col span={12}>
                        <Form.Item label="早盘K线数量" name="morning_bars">
                          <InputNumber min={3} max={12} style={{ width: '100%' }} placeholder="默认: 6（30分钟）" />
                        </Form.Item>
                      </Col>
                      <Col span={12}>
                        <Form.Item label="突破百分比" name="breakout_percent">
                          <InputNumber min={0.05} max={0.3} step={0.05} style={{ width: '100%' }} placeholder="默认: 0.1" />
                        </Form.Item>
                      </Col>
                    </Row>
                  );
                }
                return null;
              }}
            </Form.Item>

            <Form.Item style={{ textAlign: 'right' }}>
              <Button onClick={() => setBacktestModalVisible(false)} style={{ marginRight: 8 }}>
                取消
              </Button>
              <Button 
                onClick={handleOptimize} 
                style={{ marginRight: 8 }}
                icon={<BarChartOutlined />}
              >
                优化参数
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
