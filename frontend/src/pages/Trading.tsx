import React, { useEffect, useState } from 'react';
import {
  Card,
  Row,
  Col,
  Table,
  Button,
  Form,
  Input,
  InputNumber,
  Select,
  Space,
  Tag,
  message,
  Statistic,
  Divider,
  Tabs,
  Modal,
  Drawer,
  Typography,
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  ReloadOutlined,
  DollarOutlined,
  RiseOutlined,
  FallOutlined,
  SettingOutlined,
  SaveOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import tradingService from '../services/trading';
import type {
  Account,
  Order,
  Position,
  OrderSide,
  OrderType,
  OrderStatus,
  OrderStatistics,
  TradingAccountConfig,
} from '../types/trading';

const { Option } = Select;
const { Title, Text } = Typography;

const Trading: React.FC = () => {
  const [form] = Form.useForm();
  const [accountConfigForm] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [account, setAccount] = useState<Account | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [orderStats, setOrderStats] = useState<OrderStatistics | null>(null);
  const [connected, setConnected] = useState(false);
  const [configDrawerVisible, setConfigDrawerVisible] = useState(false);
  const [accountConfig, setAccountConfig] = useState<TradingAccountConfig | null>(null);

  // 加载数据
  const loadData = async () => {
    setLoading(true);
    try {
      const [accountData, ordersData, positionsData, statsData] = await Promise.all([
        tradingService.getAccount(),
        tradingService.getOrders(),
        tradingService.getPositions(),
        tradingService.getOrderStatistics(),
      ]);

      console.log('Account Data:', accountData);
      console.log('Orders Data:', ordersData);
      console.log('Positions Data:', positionsData);
      console.log('Stats Data:', statsData);

      setAccount(accountData);
      setOrders(ordersData?.orders || []);
      setPositions(positionsData?.positions || []);
      setOrderStats(statsData);
    } catch (error) {
      message.error('加载数据失败');
      console.error('Load data error:', error);
    } finally {
      setLoading(false);
    }
  };

  // 加载账户配置
  const loadAccountConfig = () => {
    const savedConfig = localStorage.getItem('trading_account_config');
    if (savedConfig) {
      try {
        const config = JSON.parse(savedConfig);
        setAccountConfig(config);
        accountConfigForm.setFieldsValue(config);
      } catch (error) {
        console.error('Failed to parse account config:', error);
      }
    }
  };

  // 保存账户配置
  const handleSaveAccountConfig = async (values: TradingAccountConfig) => {
    try {
      localStorage.setItem('trading_account_config', JSON.stringify(values));
      setAccountConfig(values);
      message.success('交易账号配置保存成功');
      setConfigDrawerVisible(false);
    } catch (error) {
      message.error('保存配置失败');
      console.error('Save config error:', error);
    }
  };

  // 连接交易系统
  const handleConnect = async () => {
    if (!accountConfig) {
      message.warning('请先配置交易账号');
      setConfigDrawerVisible(true);
      return;
    }

    setLoading(true);
    try {
      const result = await tradingService.connectTrading(accountConfig);
      setConnected(result.connected);
      if (result.connected) {
        message.success('连接成功');
        loadData();
      }
    } catch (error) {
      message.error('连接失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // 创建订单
  const handleSubmitOrder = async (values: any) => {
    setLoading(true);
    try {
      const result = await tradingService.createOrder({
        stock_code: values.stock_code,
        side: values.side,
        order_type: values.order_type,
        quantity: values.quantity,
        price: values.price,
        stop_price: values.stop_price,
        remark: values.remark,
      });

      if (result.risk_passed) {
        message.success(`订单创建成功: ${result.order_id}`);
        form.resetFields();
        loadData();
      } else {
        message.warning(`订单未通过风控: ${result.risk_level}`);
      }
    } catch (error) {
      message.error('创建订单失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // 撤销订单
  const handleCancelOrder = async (orderId: string) => {
    Modal.confirm({
      title: '确认撤销订单',
      content: `确定要撤销订单 ${orderId} 吗？`,
      onOk: async () => {
        try {
          await tradingService.cancelOrder(orderId);
          message.success('订单撤销成功');
          loadData();
        } catch (error) {
          message.error('撤销订单失败');
          console.error(error);
        }
      },
    });
  };

  // 格式化金额
  const formatAmount = (value: number) => {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
    }).format(value);
  };

  // 格式化百分比
  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${(value * 100).toFixed(2)}%`;
  };

  // 订单状态标签
  const getOrderStatusTag = (status: OrderStatus) => {
    const statusMap: Record<OrderStatus, { color: string; text: string }> = {
      pending: { color: 'default', text: '待提交' },
      submitted: { color: 'processing', text: '已提交' },
      partial_filled: { color: 'warning', text: '部分成交' },
      filled: { color: 'success', text: '已成交' },
      cancelled: { color: 'default', text: '已撤销' },
      rejected: { color: 'error', text: '已拒绝' },
    };
    const { color, text } = statusMap[status];
    return <Tag color={color}>{text}</Tag>;
  };

  // 订单表格列
  const orderColumns: ColumnsType<Order> = [
    {
      title: '订单ID',
      dataIndex: 'id',
      key: 'id',
      width: 150,
      ellipsis: true,
    },
    {
      title: '股票代码',
      dataIndex: 'stock_code',
      key: 'stock_code',
      width: 100,
    },
    {
      title: '方向',
      dataIndex: 'side',
      key: 'side',
      width: 80,
      render: (side: OrderSide) => (
        <Tag color={side === 'buy' ? 'green' : 'red'}>
          {side === 'buy' ? '买入' : '卖出'}
        </Tag>
      ),
    },
    {
      title: '类型',
      dataIndex: 'order_type',
      key: 'order_type',
      width: 100,
      render: (type: OrderType) => {
        const typeMap: Record<OrderType, string> = {
          market: '市价',
          limit: '限价',
          stop: '止损',
          stop_limit: '止损限价',
        };
        return typeMap[type];
      },
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 80,
      align: 'right',
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      align: 'right',
      render: (price: number) => (price ? price.toFixed(2) : '-'),
    },
    {
      title: '已成交',
      dataIndex: 'filled_quantity',
      key: 'filled_quantity',
      width: 80,
      align: 'right',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: getOrderStatusTag,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      fixed: 'right',
      render: (_, record) => (
        <Button
          type="link"
          danger
          icon={<DeleteOutlined />}
          onClick={() => handleCancelOrder(record.id)}
          disabled={
            record.status === 'filled' ||
            record.status === 'cancelled' ||
            record.status === 'rejected'
          }
        >
          撤销
        </Button>
      ),
    },
  ];

  // 持仓表格列
  const positionColumns: ColumnsType<Position> = [
    {
      title: '股票代码',
      dataIndex: 'stock_code',
      key: 'stock_code',
      width: 100,
    },
    {
      title: '持仓数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 100,
      align: 'right',
    },
    {
      title: '可用数量',
      dataIndex: 'available_quantity',
      key: 'available_quantity',
      width: 100,
      align: 'right',
    },
    {
      title: '成本价',
      dataIndex: 'cost_price',
      key: 'cost_price',
      width: 100,
      align: 'right',
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '现价',
      dataIndex: 'current_price',
      key: 'current_price',
      width: 100,
      align: 'right',
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '市值',
      dataIndex: 'market_value',
      key: 'market_value',
      width: 120,
      align: 'right',
      render: (value: number) => formatAmount(value),
    },
    {
      title: '盈亏金额',
      dataIndex: 'pnl_amount',
      key: 'pnl_amount',
      width: 120,
      align: 'right',
      render: (value: number) => (
        <span style={{ color: value >= 0 ? '#52c41a' : '#ff4d4f' }}>
          {value >= 0 ? '+' : ''}
          {formatAmount(value)}
        </span>
      ),
    },
    {
      title: '盈亏比例',
      dataIndex: 'pnl_ratio',
      key: 'pnl_ratio',
      width: 120,
      align: 'right',
      render: (ratio: number) => (
        <span style={{ color: ratio >= 0 ? '#52c41a' : '#ff4d4f' }}>
          {formatPercent(ratio)}
        </span>
      ),
    },
  ];

  useEffect(() => {
    loadAccountConfig();
  }, []);

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <Space>
            <Button
              type="primary"
              icon={<ReloadOutlined />}
              onClick={loadData}
              loading={loading}
            >
              刷新数据
            </Button>
            {!connected && (
              <Button
                type="primary"
                onClick={handleConnect}
                loading={loading}
              >
                连接交易系统
              </Button>
            )}
            <Button
              icon={<SettingOutlined />}
              onClick={() => setConfigDrawerVisible(true)}
            >
              配置交易账号
            </Button>
          </Space>
        </Col>
      </Row>

      {/* 账户信息 */}
      {account && (
        <Card title="账户信息" style={{ marginBottom: '24px' }}>
          <Row gutter={16}>
            <Col span={6}>
              <Statistic
                title="总资产"
                value={account.total_assets}
                precision={2}
                prefix={<DollarOutlined />}
                formatter={(value) => formatAmount(Number(value))}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="可用资金"
                value={account.available_cash}
                precision={2}
                formatter={(value) => formatAmount(Number(value))}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="持仓市值"
                value={account.market_value}
                precision={2}
                formatter={(value) => formatAmount(Number(value))}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="总盈亏"
                value={account.pnl_amount}
                precision={2}
                valueStyle={{
                  color: account.pnl_amount >= 0 ? '#3f8600' : '#cf1322',
                }}
                prefix={account.pnl_amount >= 0 ? <RiseOutlined /> : <FallOutlined />}
                formatter={(value) => formatAmount(Number(value))}
              />
            </Col>
          </Row>
        </Card>
      )}

      {/* 订单统计 */}
      {orderStats && (
        <Card title="订单统计" style={{ marginBottom: '24px' }}>
          <Row gutter={16}>
            <Col span={4}>
              <Statistic title="总订单" value={orderStats.total} />
            </Col>
            <Col span={4}>
              <Statistic
                title="待提交"
                value={orderStats.pending}
                valueStyle={{ color: '#faad14' }}
              />
            </Col>
            <Col span={4}>
              <Statistic
                title="已提交"
                value={orderStats.submitted}
                valueStyle={{ color: '#1890ff' }}
              />
            </Col>
            <Col span={4}>
              <Statistic
                title="部分成交"
                value={orderStats.partial_filled}
                valueStyle={{ color: '#faad14' }}
              />
            </Col>
            <Col span={4}>
              <Statistic
                title="已成交"
                value={orderStats.filled}
                valueStyle={{ color: '#52c41a' }}
              />
            </Col>
            <Col span={4}>
              <Statistic
                title="成交率"
                value={orderStats.filled_rate * 100}
                suffix="%"
                precision={2}
              />
            </Col>
          </Row>
        </Card>
      )}

      <Tabs defaultActiveKey="order">
        <Tabs.TabPane tab="下单" key="order">
          <Card>
            <Form form={form} onFinish={handleSubmitOrder} layout="vertical">
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item
                    label="股票代码"
                    name="stock_code"
                    rules={[{ required: true, message: '请输入股票代码' }]}
                  >
                    <Input placeholder="例如: 600000" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    label="买卖方向"
                    name="side"
                    rules={[{ required: true, message: '请选择买卖方向' }]}
                  >
                    <Select placeholder="请选择买卖方向">
                      <Option value="buy">买入</Option>
                      <Option value="sell">卖出</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item
                    label="订单类型"
                    name="order_type"
                    rules={[{ required: true, message: '请选择订单类型' }]}
                  >
                    <Select placeholder="请选择订单类型">
                      <Option value="market">市价单</Option>
                      <Option value="limit">限价单</Option>
                      <Option value="stop">止损单</Option>
                      <Option value="stop_limit">止损限价单</Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item
                    label="数量"
                    name="quantity"
                    rules={[{ required: true, message: '请输入数量' }]}
                  >
                    <InputNumber
                      style={{ width: '100%' }}
                      min={100}
                      step={100}
                      placeholder="请输入数量"
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="价格（限价单）" name="price">
                    <InputNumber
                      style={{ width: '100%' }}
                      min={0}
                      step={0.01}
                      precision={2}
                      placeholder="请输入价格"
                    />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="止损价（止损单）" name="stop_price">
                    <InputNumber
                      style={{ width: '100%' }}
                      min={0}
                      step={0.01}
                      precision={2}
                      placeholder="请输入止损价"
                    />
                  </Form.Item>
                </Col>
              </Row>
              <Row gutter={16}>
                <Col span={24}>
                  <Form.Item label="备注" name="remark">
                    <Input.TextArea rows={3} placeholder="请输入备注" />
                  </Form.Item>
                </Col>
              </Row>
              <Row>
                <Col span={24}>
                  <Form.Item>
                    <Space>
                      <Button
                        type="primary"
                        htmlType="submit"
                        icon={<PlusOutlined />}
                        loading={loading}
                      >
                        提交订单
                      </Button>
                      <Button onClick={() => form.resetFields()}>重置</Button>
                    </Space>
                  </Form.Item>
                </Col>
              </Row>
            </Form>
          </Card>
        </Tabs.TabPane>

        <Tabs.TabPane tab={`订单列表 (${orders.length})`} key="orders">
          <Card>
            <Table
              columns={orderColumns}
              dataSource={orders}
              rowKey="id"
              loading={loading}
              scroll={{ x: 1200 }}
              pagination={{
                pageSize: 20,
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 条`,
              }}
            />
          </Card>
        </Tabs.TabPane>

        <Tabs.TabPane tab={`持仓列表 (${positions.length})`} key="positions">
          <Card>
            <Table
              columns={positionColumns}
              dataSource={positions}
              rowKey="id"
              loading={loading}
              scroll={{ x: 1000 }}
              pagination={{
                pageSize: 20,
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 条`,
              }}
            />
          </Card>
        </Tabs.TabPane>
      </Tabs>

      {/* 交易账号配置抽屉 */}
      <Drawer
        title="配置交易账号"
        placement="right"
        width={500}
        onClose={() => setConfigDrawerVisible(false)}
        open={configDrawerVisible}
        footer={
          <div style={{ textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setConfigDrawerVisible(false)}>取消</Button>
              <Button
                type="primary"
                icon={<SaveOutlined />}
                onClick={() => accountConfigForm.submit()}
              >
                保存配置
              </Button>
            </Space>
          </div>
        }
      >
        <Form
          form={accountConfigForm}
          layout="vertical"
          onFinish={handleSaveAccountConfig}
        >
          <Title level={5}>券商信息</Title>
          <Form.Item
            label="券商ID"
            name="broker_id"
            rules={[{ required: true, message: '请输入券商ID' }]}
          >
            <Input placeholder="例如: 1234" />
          </Form.Item>
          <Form.Item
            label="交易账号"
            name="account"
            rules={[{ required: true, message: '请输入交易账号' }]}
          >
            <Input placeholder="您的交易账号" />
          </Form.Item>
          <Form.Item
            label="交易密码"
            name="password"
            rules={[{ required: true, message: '请输入交易密码' }]}
          >
            <Input.Password placeholder="您的交易密码" />
          </Form.Item>

          <Title level={5}>服务器地址</Title>
          <Form.Item
            label="交易服务器地址"
            name="trading_server"
            rules={[{ required: true, message: '请输入交易服务器地址' }]}
          >
            <Input placeholder="例如: 127.0.0.1" />
          </Form.Item>
          <Form.Item
            label="交易服务器端口"
            name="trading_port"
            rules={[{ required: true, message: '请输入交易服务器端口' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              min={1}
              max={65535}
              placeholder="例如: 6001"
            />
          </Form.Item>
          <Form.Item
            label="行情服务器地址"
            name="quote_server"
            rules={[{ required: true, message: '请输入行情服务器地址' }]}
          >
            <Input placeholder="例如: 127.0.0.1" />
          </Form.Item>
          <Form.Item
            label="行情服务器端口"
            name="quote_port"
            rules={[{ required: true, message: '请输入行情服务器端口' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              min={1}
              max={65535}
              placeholder="例如: 6002"
            />
          </Form.Item>

          <Divider />
          <Text type="secondary">
            配置信息将保存在本地浏览器中，请确保在安全的环境下使用。
          </Text>
        </Form>
      </Drawer>
    </div>
  );
};

export default Trading;