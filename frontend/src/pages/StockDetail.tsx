import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Card, Row, Col, Spin, message, Descriptions, Statistic, Tag, Space, Alert } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import EnhancedKLineChart from '@components/charts/EnhancedKLineChart';
import { stockService } from '@services/stock';
import { marketService, Quote } from '@services/market';

interface StockKLineData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount?: number;
}

const StockDetail = () => {
  const { code } = useParams<{ code: string }>();
  const [loading, setLoading] = useState(false);
  const [quoteLoading, setQuoteLoading] = useState(false);
  const [stockInfo, setStockInfo] = useState<any>(null);
  const [quote, setQuote] = useState<Quote | null>(null);
  const [kLineData, setKLineData] = useState<StockKLineData[]>([]);
  const [stockInfoError, setStockInfoError] = useState<string | null>(null);
  const [quoteError, setQuoteError] = useState<string | null>(null);
  const [kLineError, setKLineError] = useState<string | null>(null);
  const [activeIndicator, setActiveIndicator] = useState<string>('ma');

  // 加载股票基本信息和实时行情
  useEffect(() => {
    if (code) {
      loadStockInfo();
      loadQuote();
      loadKLineData();
    }
  }, [code]);

  // 定时刷新行情
  useEffect(() => {
    if (!code) return;

    const interval = setInterval(() => {
      loadQuote();
    }, 5000); // 每5秒刷新一次

    return () => clearInterval(interval);
  }, [code]);

  const loadStockInfo = async () => {
    try {
      setLoading(true);
      setStockInfoError(null);
      const response = await stockService.getStock(code);
      setStockInfo(response?.data);
      console.log('成功加载股票信息:', response?.data);
    } catch (error: any) {
      console.error('加载股票信息失败:', error);
      setStockInfo(null);
      // 显示明确的错误信息
      const errorMsg = error?.response?.data?.detail || 
                       error?.response?.data?.message || 
                       error?.message || 
                       '无法连接到服务器，请检查后端服务是否运行';
      setStockInfoError(errorMsg);
      message.error(`加载股票信息失败: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const loadQuote = async () => {
    if (!code) return;

    try {
      setQuoteLoading(true);
      setQuoteError(null);
      const data = await marketService.getQuote(code);
      setQuote(data);
    } catch (error: any) {
      console.error('加载行情失败:', error);
      setQuote(null);
      // 显示明确的错误信息
      const errorMsg = error?.response?.data?.detail || 
                       error?.response?.data?.message || 
                       error?.message || 
                       '无法连接到服务器，请检查后端服务是否运行';
      setQuoteError(errorMsg);
      message.error(`加载行情失败: ${errorMsg}`);
    } finally {
      setQuoteLoading(false);
    }
  };

  const loadKLineData = async () => {
    if (!code) return;

    try {
      setLoading(true);
      setKLineError(null);
      
      // 计算日期范围（过去90天）
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 90);
      
      // 调用市场服务获取K线数据
      const response = await marketService.getKlineData({
        code: code,
        freq: 'daily',
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0]
      });
      
      if (response && response.data && response.data.length > 0) {
        // 转换后端数据格式为前端期望格式
        const formattedData = response.data.map((item: any) => ({
          date: item.timestamp.split('T')[0], // 从timestamp提取日期
          open: item.open,
          high: item.high,
          low: item.low,
          close: item.close,
          volume: item.volume,
          amount: item.amount || (item.volume * item.close) // 计算成交额
        }));
        setKLineData(formattedData);
        console.log('成功加载K线数据:', formattedData.length, '条记录');
      } else {
        const errorMsg = 'API返回空数据，该股票可能没有K线数据';
        setKLineError(errorMsg);
        message.error(errorMsg);
        console.log(errorMsg);
      }
    } catch (error: any) {
      console.error('加载K线数据失败:', error);
      setKLineData([]);
      // 显示明确的错误信息
      const errorMsg = error?.response?.data?.detail || 
                       error?.response?.data?.message || 
                       error?.message || 
                       '无法连接到服务器，请检查后端服务是否运行';
      setKLineError(errorMsg);
      message.error(`加载K线数据失败: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 100000000) {
      return (num / 100000000).toFixed(2) + '亿';
    } else if (num >= 10000) {
      return (num / 10000).toFixed(2) + '万';
    }
    return num.toString();
  };

  return (
    <div>
      <Spin spinning={loading}>
        {/* 错误提示 */}
        {(stockInfoError || quoteError || kLineError) && (
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={24}>
              <Alert
                message="数据加载失败"
                description={
                  <div>
                    {stockInfoError && (
                      <div style={{ marginBottom: 8 }}>
                        <strong>股票信息:</strong> {stockInfoError}
                      </div>
                    )}
                    {quoteError && (
                      <div style={{ marginBottom: 8 }}>
                        <strong>实时行情:</strong> {quoteError}
                      </div>
                    )}
                    {kLineError && (
                      <div style={{ marginBottom: 8 }}>
                        <strong>K线数据:</strong> {kLineError}
                      </div>
                    )}
                    <div style={{ marginTop: 12, color: '#666' }}>
                      <strong>可能的原因:</strong>
                      <ul style={{ marginTop: 8, marginBottom: 0 }}>
                        <li>后端服务未启动，请运行: <code>cd backend && python main.py</code></li>
                        <li>后端服务端口被占用，请检查端口8000是否可用</li>
                        <li>网络连接问题，请检查网络连接</li>
                        <li>数据源API不可用，请检查后端日志</li>
                      </ul>
                    </div>
                  </div>
                }
                type="error"
                showIcon
                icon={<ExclamationCircleOutlined />}
                closable
              />
            </Col>
          </Row>
        )}

        {/* 头部信息 */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={18}>
            <Card>
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '16px' }}>
                  <h1 style={{ margin: 0, fontSize: '28px' }}>
                    {stockInfo?.name || '股票详情'} - {code}
                  </h1>
                  {quote && (
                    <Tag color="blue">{quote.change_pct >= 0 ? '+' : ''}{quote.change_pct}%</Tag>
                  )}
                  {quoteError && !quote && (
                    <Tag color="error">行情加载失败</Tag>
                  )}
                </div>
                
                {quote ? (
                  <Row gutter={24}>
                    <Col span={6}>
                      <Statistic
                        title="当前价"
                        value={quote.price}
                        precision={2}
                        valueStyle={{ 
                          color: quote.change >= 0 ? '#cf1322' : '#3f8600',
                          fontSize: '24px'
                        }}
                        prefix={quote.change >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="涨跌"
                        value={quote.change}
                        precision={2}
                        valueStyle={{ 
                          color: quote.change >= 0 ? '#cf1322' : '#3f8600' 
                        }}
                        prefix={quote.change >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="涨跌幅"
                        value={quote.change_pct}
                        precision={2}
                        suffix="%"
                        valueStyle={{ 
                          color: quote.change_pct >= 0 ? '#cf1322' : '#3f8600' 
                        }}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="成交量"
                        value={formatNumber(quote.volume)}
                        valueStyle={{ color: '#722ed1' }}
                      />
                    </Col>
                  </Row>
                ) : quoteError ? (
                  <div style={{ 
                    padding: '20px', 
                    background: '#fff1f0', 
                    border: '1px solid #ffa39e',
                    borderRadius: '4px',
                    color: '#cf1322'
                  }}>
                    <ExclamationCircleOutlined style={{ marginRight: 8 }} />
                    {quoteError}
                  </div>
                ) : (
                  <div style={{ padding: '20px', color: '#999' }}>
                    加载中...
                  </div>
                )}
              </Space>
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Descriptions column={1} size="small">
                <Descriptions.Item label="开盘">
                  {quote?.open?.toFixed(2) || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="最高">
                  {quote?.high?.toFixed(2) || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="最低">
                  {quote?.low?.toFixed(2) || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="昨收">
                  {quote?.pre_close?.toFixed(2) || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="成交额">
                  {quote?.amount ? formatNumber(quote.amount) : '-'}
                </Descriptions.Item>
                <Descriptions.Item label="更新时间">
                  {quote?.timestamp ? new Date(quote.timestamp).toLocaleTimeString() : '-'}
                </Descriptions.Item>
              </Descriptions>
            </Card>
          </Col>
        </Row>

        {/* 基本信息 */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={24}>
            <Card title="基本信息">
              <Descriptions column={4} bordered>
                <Descriptions.Item label="股票代码">{code}</Descriptions.Item>
                <Descriptions.Item label="股票名称">
                  {stockInfo?.name || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="所属市场">
                  {stockInfo?.market || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="所属板块">
                  {stockInfo?.sector || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="所属行业">
                  {stockInfo?.industry || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="上市日期">
                  {stockInfo?.list_date || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="总股本">
                  {stockInfo?.total_shares ? formatNumber(stockInfo.total_shares) : '-'}
                </Descriptions.Item>
                <Descriptions.Item label="流通股本">
                  {stockInfo?.float_shares ? formatNumber(stockInfo.float_shares) : '-'}
                </Descriptions.Item>
              </Descriptions>
            </Card>
          </Col>
        </Row>

        {/* K线图 */}
        <Row gutter={16}>
          <Col span={24}>
            <Card title="K线图">
              {kLineData.length > 0 ? (
                <EnhancedKLineChart
                  data={kLineData}
                  title={`${stockInfo?.name || code} 日K线`}
                  subtitle="最近60个交易日"
                  height="600px"
                  showVolume={true}
                  theme="light"
                />
              ) : kLineError ? (
                <div style={{ 
                  height: 600, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  flexDirection: 'column',
                  gap: '16px',
                  color: '#999',
                  background: '#fff1f0',
                  borderRadius: '4px',
                  border: '1px solid #ffa39e'
                }}>
                  <ExclamationCircleOutlined style={{ fontSize: 48, color: '#cf1322' }} />
                  <div style={{ color: '#cf1322', fontSize: 16, fontWeight: 500 }}>
                    K线数据加载失败
                  </div>
                  <div style={{ color: '#666', maxWidth: 500, textAlign: 'center' }}>
                    {kLineError}
                  </div>
                  <div style={{ color: '#666', marginTop: 16 }}>
                    <strong>解决方法:</strong>
                    <ul style={{ textAlign: 'left', marginTop: 8 }}>
                      <li>启动后端服务: <code>cd backend && python main.py</code></li>
                      <li>检查后端日志: <code>tail -f logs/app_$(date +%Y-%m-%d).log</code></li>
                      <li>测试API: <code>curl http://localhost:8000/health</code></li>
                    </ul>
                  </div>
                </div>
              ) : (
                <div style={{ 
                  height: 600, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  color: '#999'
                }}>
                  加载中...
                </div>
              )}
            </Card>
          </Col>
        </Row>
      </Spin>
    </div>
  );
};

export default StockDetail;