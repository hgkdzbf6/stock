import React, { useState, useCallback, useEffect } from 'react';
import { Card, Input, Button, Select, List, Tag, Space, Spin, Alert, message, Divider, Row, Col, Statistic, AutoComplete, Modal } from 'antd';
import { SearchOutlined, SendOutlined, FundOutlined, ThunderboltOutlined, BarChartOutlined } from '@ant-design/icons';
import { newsService } from '../services/news';
import { stockCodeService, StockInfo } from '../services/stockCode';
import { NewsItem, FundamentalsData, FundamentalsSummary } from '../types/news';
import { useNavigate } from 'react-router-dom';
import debounce from 'lodash.debounce';
import './News.css';

const { Option } = Select;
const { TextArea } = Input;

const News: React.FC = () => {
  const navigate = useNavigate();
  
  // 状态
  const [loading, setLoading] = useState(false);
  const [stockInfoLoading, setStockInfoLoading] = useState(false);
  const [newsType, setNewsType] = useState<'stock' | 'sector'>('stock');
  const [market, setMarket] = useState<'all' | 'domestic' | 'international'>('all');
  const [stockCode, setStockCode] = useState('');
  const [stockName, setStockName] = useState('');
  const [sectorName, setSectorName] = useState('');
  const [newsList, setNewsList] = useState<NewsItem[]>([]);
  const [fundamentals, setFundamentals] = useState<FundamentalsData>({});
  const [fundamentalSummary, setFundamentalSummary] = useState<FundamentalsSummary | null>(null);
  const [autoFillFundamentals, setAutoFillFundamentals] = useState(true);
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  
  // 情绪分析相关状态
  const [sentimentModalVisible, setSentimentModalVisible] = useState(false);
  const [sentimentLoading, setSentimentLoading] = useState(false);
  const [sentimentResult, setSentimentResult] = useState<any>(null);
  
  // 新闻来源信息弹窗
  const [sourceInfoVisible, setSourceInfoVisible] = useState(false);
  const [selectedSourceInfo, setSelectedSourceInfo] = useState<any>(null);
  
  // 自动补全相关状态
  const [codeSuggestions, setCodeSuggestions] = useState<StockInfo[]>([]);
  const [nameSuggestions, setNameSuggestions] = useState<StockInfo[]>([]);
  
  // 新闻源健康状态
  const [sourceHealth, setSourceHealth] = useState<Record<string, boolean>>({});
  const [checkingHealth, setCheckingHealth] = useState(false);

  // 防抖搜索股票代码
  const searchStockCode = useCallback(
    debounce(async (code: string) => {
      if (code.length < 2) {
        setCodeSuggestions([]);
        return;
      }
      
      const results = await stockCodeService.searchByCode(code, 10);
      setCodeSuggestions(results);
    }, 300),
    []
  );

  // 防抖搜索股票名称
  const searchStockName = useCallback(
    debounce(async (name: string) => {
      if (name.length < 2) {
        setNameSuggestions([]);
        return;
      }
      
      const results = await stockCodeService.searchByName(name, 10);
      setNameSuggestions(results);
    }, 300),
    []
  );

  // 根据股票代码自动填充信息
  const autoFillByCode = useCallback(
    debounce(async (code: string) => {
      if (code.length < 6) return; // 股票代码至少6位
      
      setStockInfoLoading(true);
      try {
        const info = await stockCodeService.getStockInfo(code);
        if (info) {
          setStockName(info.name);
          if (info.sector) {
            setSectorName(info.sector);
          }
          message.success(`已自动填充: ${info.name}`);
        }
      } catch (error) {
        // 静默失败，不打扰用户
      } finally {
        setStockInfoLoading(false);
      }
    }, 500),
    []
  );

  // 根据股票名称自动填充信息
  const autoFillByName = useCallback(
    debounce(async (name: string) => {
      if (name.length < 2) return;
      
      setStockInfoLoading(true);
      try {
        const results = await stockCodeService.searchByName(name, 1);
        if (results.length > 0 && results[0].name === name) {
          const stock = results[0];
          setStockCode(stock.code);
          if (stock.sector) {
            setSectorName(stock.sector);
          }
          message.success(`已自动填充代码: ${stock.code}`);
        }
      } catch (error) {
        // 静默失败，不打扰用户
      } finally {
        setStockInfoLoading(false);
      }
    }, 500),
    []
  );

  // 处理股票代码变化
  const handleStockCodeChange = (value: string) => {
    setStockCode(value);
    searchStockCode(value);
    autoFillByCode(value);
  };

  // 处理股票名称变化
  const handleStockNameChange = (value: string) => {
    setStockName(value);
    searchStockName(value);
    autoFillByName(value);
  };

  // 选择股票代码建议
  const handleCodeSelect = (value: string, option: any) => {
    const stock = option.stock;
    setStockCode(stock.code);
    setStockName(stock.name);
    if (stock.sector) {
      setSectorName(stock.sector);
    }
    setCodeSuggestions([]);
  };

  // 选择股票名称建议
  const handleNameSelect = (value: string, option: any) => {
    const stock = option.stock;
    setStockCode(stock.code);
    setStockName(stock.name);
    if (stock.sector) {
      setSectorName(stock.sector);
    }
    setNameSuggestions([]);
  };

  // 获取新闻
  const fetchNews = async () => {
    setLoading(true);
    try {
      let response;
      if (newsType === 'stock') {
        response = await newsService.fetchStockNews({
          stock_code: stockCode || '',  // 如果为空则使用空字符串
          stock_name: stockName || '',  // 如果为空则使用空字符串
          sector_name: sectorName || undefined,
          market: market === 'all' ? undefined : market,
          sources: selectedSources.length > 0 ? selectedSources : undefined,
          limit: 10
        });
      } else {
        // 板块新闻也可以不输入，获取所有相关新闻
        response = await newsService.fetchSectorNews({
          sector_name: sectorName || '',
          limit: 20
        });
      }
      
      setNewsList(response.news || []);
      
      if (response.total === 0) {
        message.info('未找到相关新闻，请尝试调整搜索条件');
      } else {
        message.success(`成功获取 ${response.total} 条新闻`);
      }
    } catch (error: any) {
      message.error(`获取新闻失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 总结基本面
  const summarizeFundamentals = async () => {
    if (!stockCode || !stockName) {
      message.error('请先输入股票代码和名称');
      return;
    }

    setLoading(true);
    try {
      const summary = await newsService.summarizeFundamentals(stockCode, stockName, fundamentals);
      setFundamentalSummary(summary);
      message.success('基本面总结成功');
    } catch (error: any) {
      message.error(`总结失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 格式化并发送到舆情分析
  const sendToSentiment = async () => {
    if (newsList.length === 0) {
      message.error('请先获取新闻');
      return;
    }

    setLoading(true);
    try {
      const formatted = await newsService.formatNewsForSentiment(newsList, fundamentals);
      
      // 导航到舆情分析页面并传递数据
      navigate('/sentiment', {
        state: {
          stockCode: stockCode || sectorName,
          stockName: stockName || sectorName,
          sectorName: sectorName,
          newsData: formatted.news
        }
      });
    } catch (error: any) {
      message.error(`格式化失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 格式化时间
  const formatTime = (timeStr: string) => {
    try {
      const date = new Date(timeStr);
      return date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return timeStr;
    }
  };

  // 渲染股票代码选项
  const renderCodeOptions = () => {
    return codeSuggestions.map(stock => ({
      value: stock.code,
      label: (
        <div>
          <span style={{ fontWeight: 'bold' }}>{stock.code}</span>
          <span style={{ marginLeft: 8 }}>{stock.name}</span>
        </div>
      ),
      stock
    }));
  };

  // 渲染股票名称选项
  const renderNameOptions = () => {
    return nameSuggestions.map(stock => ({
      value: stock.name,
      label: (
        <div>
          <span style={{ fontWeight: 'bold' }}>{stock.name}</span>
          <span style={{ marginLeft: 8 }}>{stock.code}</span>
        </div>
      ),
      stock
    }));
  };

  // 一键情绪分析
  const analyzeSentiment = async () => {
    if (newsList.length === 0) {
      message.error('请先获取新闻');
      return;
    }

    setSentimentLoading(true);
    setSentimentModalVisible(true);
    setSentimentResult(null);

    try {
      const result = await newsService.analyzeSentiment({
        stock_code: stockCode || sectorName || '未知',
        stock_name: stockName || sectorName || '未知',
        sector_name: sectorName || undefined,
        news_list: newsList
      });
      setSentimentResult(result);
      message.success('情绪分析完成');
    } catch (error: any) {
      message.error(`情绪分析失败: ${error.response?.data?.detail || error.message}`);
      setSentimentModalVisible(false);
    } finally {
      setSentimentLoading(false);
    }
  };

  // 检查新闻源健康状态
  const checkSourceHealthStatus = async () => {
    setCheckingHealth(true);
    try {
      const healthData = await newsService.checkSourceHealth();
      const healthMap: Record<string, boolean> = {};
      
      healthData.sources.forEach((source: any) => {
        healthMap[source.name] = source.available;
      });
      
      setSourceHealth(healthMap);
      message.success('新闻源健康状态已更新');
    } catch (error: any) {
      message.error(`检查健康状态失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      setCheckingHealth(false);
    }
  };

  // 页面加载时检查源健康状态
  useEffect(() => {
    checkSourceHealthStatus();
  }, []);

  return (
    <div className="news-page">
      <Card title="新闻获取" className="news-card">
        {/* 获取新闻区域 */}
        <div className="section">
          <h3>获取新闻</h3>
          <div className="form-row" style={{ marginBottom: 16 }}>
            <Select
              value={newsType}
              onChange={setNewsType}
              style={{ width: 150 }}
            >
              <Option value="stock">股票新闻</Option>
              <Option value="sector">板块新闻</Option>
            </Select>

            {newsType === 'stock' && (
              <>
                <AutoComplete
                  placeholder="股票代码 (如: 600000)"
                  value={stockCode}
                  onChange={handleStockCodeChange}
                  onSelect={handleCodeSelect}
                  options={renderCodeOptions()}
                  style={{ width: 200 }}
                />
                <AutoComplete
                  placeholder="股票名称 (如: 浦发银行)"
                  value={stockName}
                  onChange={handleStockNameChange}
                  onSelect={handleNameSelect}
                  options={renderNameOptions()}
                  style={{ width: 200 }}
                />
                {stockInfoLoading && <Spin size="small" />}
              </>
            )}

            <Input
              placeholder="板块名称 (如: 银行)"
              value={sectorName}
              onChange={(e) => setSectorName(e.target.value)}
              style={{ width: 200 }}
            />
          </div>

          {/* 市场和数据来源选择 */}
          <div className="form-row" style={{ marginBottom: 16 }}>
            <Select
              value={market}
              onChange={(value: any) => setMarket(value)}
              style={{ width: 120 }}
              placeholder="选择市场"
            >
              <Option value="all">全部市场</Option>
              <Option value="domestic">国内市场</Option>
              <Option value="international">国外市场</Option>
            </Select>

            <Space>
              <Select
                mode="multiple"
                placeholder="选择数据来源（可选）"
                value={selectedSources}
                onChange={setSelectedSources}
                style={{ width: 450 }}
                allowClear
              >
                <Option value="新浪财经">
                  <Space>
                    <span>新浪财经（A股）</span>
                    {checkingHealth ? (
                      <Spin size="small" />
                    ) : (
                      <Tag color={sourceHealth['新浪财经'] ? 'green' : 'red'} style={{ fontSize: '11px' }}>
                        {sourceHealth['新浪财经'] !== undefined ? (sourceHealth['新浪财经'] ? '可用' : '不可用') : '检查中'}
                      </Tag>
                    )}
                  </Space>
                </Option>
                <Option value="CNBC国际商业新闻">
                  <Space>
                    <span>CNBC国际商业新闻</span>
                    <Tag color="green" style={{ fontSize: '11px' }}>可用</Tag>
                  </Space>
                </Option>
                <Option value="雅虎财经">
                  <Space>
                    <span>雅虎财经</span>
                    <Tag color="green" style={{ fontSize: '11px' }}>可用</Tag>
                  </Space>
                </Option>
                <Option value="彭博市场新闻">
                  <Space>
                    <span>彭博市场新闻</span>
                    <Tag color="green" style={{ fontSize: '11px' }}>可用</Tag>
                  </Space>
                </Option>
                <Option value="CNBC股市新闻">
                  <Space>
                    <span>CNBC股市新闻</span>
                    <Tag color="green" style={{ fontSize: '11px' }}>可用</Tag>
                  </Space>
                </Option>
                <Option value="华尔街日报-市场">
                  <Space>
                    <span>华尔街日报-市场</span>
                    <Tag color="green" style={{ fontSize: '11px' }}>可用</Tag>
                  </Space>
                </Option>
                <Option value="市场观察">
                  <Space>
                    <span>市场观察</span>
                    <Tag color="green" style={{ fontSize: '11px' }}>可用</Tag>
                  </Space>
                </Option>
              </Select>
              <Button
                icon={<SearchOutlined />}
                onClick={checkSourceHealthStatus}
                loading={checkingHealth}
                size="small"
              >
                刷新状态
              </Button>
            </Space>
          </div>

          <div className="form-row">
            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={fetchNews}
              loading={loading}
            >
              获取新闻
            </Button>
          </div>
        </div>

        <Divider />

        {/* 基本面数据输入 */}
        {newsType === 'stock' && (
          <div className="section">
            <h3><FundOutlined /> 基本面数据（可选）</h3>
            <Row gutter={16}>
              <Col span={6}>
                <Input
                  placeholder="市值 (如: 5000亿)"
                  value={fundamentals.market_cap}
                  onChange={(e) => setFundamentals({ ...fundamentals, market_cap: e.target.value })}
                  addonBefore="市值"
                />
              </Col>
              <Col span={6}>
                <Input
                  type="number"
                  placeholder="市盈率"
                  value={fundamentals.pe_ratio || ''}
                  onChange={(e) => setFundamentals({ ...fundamentals, pe_ratio: Number(e.target.value) })}
                  addonBefore="PE"
                />
              </Col>
              <Col span={6}>
                <Input
                  type="number"
                  placeholder="市净率"
                  value={fundamentals.pb_ratio || ''}
                  onChange={(e) => setFundamentals({ ...fundamentals, pb_ratio: Number(e.target.value) })}
                  addonBefore="PB"
                />
              </Col>
              <Col span={6}>
                <Input
                  type="number"
                  placeholder="净资产收益率 (%)"
                  value={fundamentals.roe || ''}
                  onChange={(e) => setFundamentals({ ...fundamentals, roe: Number(e.target.value) })}
                  addonBefore="ROE"
                />
              </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 16 }}>
              <Col span={6}>
                <Input
                  placeholder="营收 (如: 1000亿)"
                  value={fundamentals.revenue}
                  onChange={(e) => setFundamentals({ ...fundamentals, revenue: e.target.value })}
                  addonBefore="营收"
                />
              </Col>
              <Col span={6}>
                <Input
                  placeholder="净利润 (如: 200亿)"
                  value={fundamentals.net_profit}
                  onChange={(e) => setFundamentals({ ...fundamentals, net_profit: e.target.value })}
                  addonBefore="净利润"
                />
              </Col>
              <Col span={6}>
                <Input
                  type="number"
                  placeholder="营收增长率 (%)"
                  value={fundamentals.revenue_growth || ''}
                  onChange={(e) => setFundamentals({ ...fundamentals, revenue_growth: Number(e.target.value) })}
                  addonBefore="营收增长"
                />
              </Col>
              <Col span={6}>
                <Input
                  type="number"
                  placeholder="净利润增长率 (%)"
                  value={fundamentals.profit_growth || ''}
                  onChange={(e) => setFundamentals({ ...fundamentals, profit_growth: Number(e.target.value) })}
                  addonBefore="利润增长"
                />
              </Col>
            </Row>
            <Row gutter={16} style={{ marginTop: 16 }}>
              <Col span={6}>
                <Input
                  type="number"
                  placeholder="股息率 (%)"
                  value={fundamentals.dividend_yield || ''}
                  onChange={(e) => setFundamentals({ ...fundamentals, dividend_yield: Number(e.target.value) })}
                  addonBefore="股息率"
                />
              </Col>
              <Col span={12}>
                <Input
                  placeholder="所属行业 (如: 银行)"
                  value={fundamentals.industry}
                  onChange={(e) => setFundamentals({ ...fundamentals, industry: e.target.value })}
                  addonBefore="行业"
                />
              </Col>
              <Col span={6}>
                <Button
                  type="primary"
                  icon={<FundOutlined />}
                  onClick={summarizeFundamentals}
                  loading={loading}
                  block
                >
                  总结基本面
                </Button>
              </Col>
            </Row>

            {/* 基本面总结 */}
            {fundamentalSummary && (
              <Alert
                style={{ marginTop: 16 }}
                type="info"
                message="基本面总结"
                description={
                  <div>
                    <p>{fundamentalSummary.summary_text}</p>
                    <Row gutter={16} style={{ marginTop: 12 }}>
                      <Col span={4}>
                        <Statistic
                          title="市值"
                          value={fundamentalSummary.market_cap}
                          valueStyle={{ fontSize: '14px' }}
                        />
                      </Col>
                      <Col span={4}>
                        <Statistic
                          title="PE"
                          value={fundamentalSummary.pe_ratio}
                          valueStyle={{ fontSize: '14px' }}
                        />
                      </Col>
                      <Col span={4}>
                        <Statistic
                          title="PB"
                          value={fundamentalSummary.pb_ratio}
                          valueStyle={{ fontSize: '14px' }}
                        />
                      </Col>
                      <Col span={4}>
                        <Statistic
                          title="ROE"
                          value={fundamentalSummary.roe}
                          suffix="%"
                          valueStyle={{ fontSize: '14px' }}
                        />
                      </Col>
                      <Col span={4}>
                        <Statistic
                          title="营收增长"
                          value={fundamentalSummary.revenue_growth}
                          suffix="%"
                          valueStyle={{ fontSize: '14px' }}
                        />
                      </Col>
                      <Col span={4}>
                        <Statistic
                          title="利润增长"
                          value={fundamentalSummary.profit_growth}
                          suffix="%"
                          valueStyle={{ fontSize: '14px' }}
                        />
                      </Col>
                    </Row>
                  </div>
                }
              />
            )}
          </div>
        )}

        <Divider />

        {/* 新闻列表 */}
        <div className="section">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h3><ThunderboltOutlined /> 新闻列表 ({newsList.length}条)</h3>
            <Space>
              <Button
                type="primary"
                icon={<BarChartOutlined />}
                onClick={analyzeSentiment}
                loading={sentimentLoading}
                disabled={newsList.length === 0}
              >
                一键情绪分析
              </Button>
              <Button
                icon={<SendOutlined />}
                onClick={sendToSentiment}
                loading={loading}
                disabled={newsList.length === 0}
              >
                发送到舆情分析
              </Button>
            </Space>
          </div>
          
          {newsList.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
              暂无新闻数据，请先获取新闻
            </div>
          ) : (
            <List
              itemLayout="vertical"
              size="large"
              dataSource={newsList}
              renderItem={(item) => {
                const sourceInfo = item.source_info;
                const stockRelation = item.stock_code || item.stock_name ? 
                  `关联${item.stock_name || ''}(${item.stock_code || ''})` : 
                  '通用财经新闻';
                
                return (
                  <List.Item
                    key={item.id}
                    actions={[
                      <span style={{ cursor: 'pointer', color: '#1890ff' }} 
                            onClick={() => {
                              if (sourceInfo && Object.keys(sourceInfo).length > 0) {
                                setSelectedSourceInfo(sourceInfo);
                                setSourceInfoVisible(true);
                              }
                            }}>
                        <Space>
                          <span>{item.source}</span>
                          {sourceInfo && Object.keys(sourceInfo).length > 0 && (
                            <Tag color="blue" style={{ fontSize: '12px' }}>
                              {sourceInfo.country_cn || sourceInfo.country}
                            </Tag>
                          )}
                        </Space>
                      </span>,
                      <span>{formatTime(item.published_time)}</span>
                    ]}
                  >
                    <List.Item.Meta
                      title={
                        <div>
                          <a href={item.link} target="_blank" rel="noopener noreferrer">
                            {item.title}
                          </a>
                          <Tag color={stockRelation.includes('通用') ? 'default' : 'green'} 
                                style={{ marginLeft: 12, fontSize: '12px' }}>
                            {stockRelation}
                          </Tag>
                        </div>
                      }
                      description={
                        <div>
                          <Space wrap style={{ marginBottom: 8 }}>
                            {item.tags?.map(tag => (
                              <Tag key={tag} color="blue">{tag}</Tag>
                            ))}
                          </Space>
                          {sourceInfo && Object.keys(sourceInfo).length > 0 && (
                            <div style={{ fontSize: '12px', color: '#666', marginTop: 4 }}>
                              <Space size="large">
                                <span><strong>来源：</strong>{sourceInfo.name_cn}</span>
                                <span><strong>国家：</strong>{sourceInfo.country_cn}</span>
                                <span><strong>语言：</strong>{sourceInfo.language_cn}</span>
                                <span><strong>覆盖：</strong>{sourceInfo.coverage_cn}</span>
                              </Space>
                            </div>
                          )}
                        </div>
                      }
                    />
                    <div className="news-content">
                      {item.content}
                    </div>
                  </List.Item>
                );
              }}
            />
          )}
        </div>
      </Card>

      {/* 情绪分析结果模态框 */}
      <Modal
        title={<span><BarChartOutlined /> 情绪分析结果</span>}
        open={sentimentModalVisible}
        onCancel={() => setSentimentModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setSentimentModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        {sentimentLoading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <Spin size="large" tip="正在分析情绪..." />
          </div>
        ) : sentimentResult ? (
          <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
            {/* 整体情绪分数 */}
            {sentimentResult.overall_sentiment !== undefined && (
              <Alert
                style={{ marginBottom: 16 }}
                type={
                  sentimentResult.overall_sentiment > 50 ? 'success' :
                  sentimentResult.overall_sentiment < -50 ? 'error' : 'info'
                }
                message="整体情绪"
                description={
                  <div>
                    <Row gutter={16}>
                      <Col span={12}>
                        <Statistic
                          title="情绪分数"
                          value={sentimentResult.overall_sentiment}
                          valueStyle={{
                            color: sentimentResult.overall_sentiment > 50 ? '#52c41a' :
                                   sentimentResult.overall_sentiment < -50 ? '#ff4d4f' : '#1890ff'
                          }}
                        />
                      </Col>
                      <Col span={12}>
                        <Statistic
                          title="置信度"
                          value={sentimentResult.confidence * 100}
                          suffix="%"
                          precision={1}
                        />
                      </Col>
                    </Row>
                  </div>
                }
              />
            )}

            {/* 新闻影响分析 */}
            {sentimentResult.news_impacts && sentimentResult.news_impacts.length > 0 && (
              <div style={{ marginBottom: 16 }}>
                <h4>新闻影响分析</h4>
                <List
                  size="small"
                  dataSource={sentimentResult.news_impacts}
                  renderItem={(item: any) => (
                    <List.Item>
                      <List.Item.Meta
                        title={
                          <span>
                            {item.title}
                            <Tag
                              color={
                                item.sentiment > 50 ? 'green' :
                                item.sentiment < -50 ? 'red' : 'blue'
                              }
                              style={{ marginLeft: 8 }}
                            >
                              {item.sentiment > 50 ? '积极' :
                               item.sentiment < -50 ? '消极' : '中性'}
                            </Tag>
                          </span>
                        }
                        description={
                          <div>
                            <Space direction="vertical" style={{ width: '100%' }}>
                              <div>
                                <strong>情绪分数：</strong>
                                <span style={{ marginLeft: 8 }}>{item.sentiment}</span>
                              </div>
                              {item.impact_level && (
                                <div>
                                  <strong>影响程度：</strong>
                                  <Tag color="orange" style={{ marginLeft: 8 }}>
                                    {item.impact_level}
                                  </Tag>
                                </div>
                              )}
                              {item.summary && (
                                <div>
                                  <strong>分析：</strong>
                                  <p style={{ marginTop: 8 }}>{item.summary}</p>
                                </div>
                              )}
                            </Space>
                          </div>
                        }
                      />
                    </List.Item>
                  )}
                />
              </div>
            )}

            {/* 投资建议 */}
            {sentimentResult.investment_advice && (
              <Alert
                style={{ marginBottom: 16 }}
                type="warning"
                message="投资建议"
                description={
                  <div>
                    <p>{sentimentResult.investment_advice}</p>
                    {sentimentResult.risk_level && (
                      <div style={{ marginTop: 12 }}>
                        <strong>风险等级：</strong>
                        <Tag
                          color={
                            sentimentResult.risk_level === 'low' ? 'green' :
                            sentimentResult.risk_level === 'medium' ? 'orange' : 'red'
                          }
                          style={{ marginLeft: 8 }}
                        >
                          {sentimentResult.risk_level === 'low' ? '低' :
                           sentimentResult.risk_level === 'medium' ? '中' : '高'}
                        </Tag>
                      </div>
                    )}
                  </div>
                }
              />
            )}

            {/* 原始响应（用于调试） */}
            {sentimentResult.raw_response && (
              <Alert
                type="info"
                message="原始分析结果"
                description={
                  <pre style={{ maxHeight: '200px', overflow: 'auto', fontSize: '12px' }}>
                    {typeof sentimentResult.raw_response === 'string'
                      ? sentimentResult.raw_response
                      : JSON.stringify(sentimentResult.raw_response, null, 2)}
                  </pre>
                }
              />
            )}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
            暂无分析结果
          </div>
        )}
      </Modal>

      {/* 新闻来源详情模态框 */}
      <Modal
        title={<span><SearchOutlined /> 新闻来源详情</span>}
        open={sourceInfoVisible}
        onCancel={() => setSourceInfoVisible(false)}
        footer={[
          <Button key="close" onClick={() => setSourceInfoVisible(false)}>
            关闭
          </Button>
        ]}
        width={700}
      >
        {selectedSourceInfo && (
          <div>
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={12}>
                <Alert
                  type="info"
                  message="中文名称"
                  description={selectedSourceInfo.name_cn}
                />
              </Col>
              <Col span={12}>
                <Alert
                  type="info"
                  message="英文名称"
                  description={selectedSourceInfo.name}
                />
              </Col>
            </Row>
            
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={12}>
                <Alert
                  type="info"
                  message="国家"
                  description={selectedSourceInfo.country_cn}
                />
              </Col>
              <Col span={12}>
                <Alert
                  type="info"
                  message="语言"
                  description={selectedSourceInfo.language_cn}
                />
              </Col>
            </Row>
            
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={12}>
                <Alert
                  type="info"
                  message="类别"
                  description={selectedSourceInfo.category}
                />
              </Col>
              <Col span={12}>
                <Alert
                  type="info"
                  message="覆盖范围（中文）"
                  description={selectedSourceInfo.coverage_cn}
                />
              </Col>
            </Row>
            
            <div style={{ marginBottom: 16 }}>
              <Alert
                type="success"
                message="中文描述"
                description={selectedSourceInfo.description_cn}
              />
            </div>
            
            <div>
              <Alert
                type="success"
                message="English Description"
                description={selectedSourceInfo.description}
              />
            </div>
            
            <div style={{ marginTop: 16, padding: '16px', background: '#f5f5f5', borderRadius: '8px' }}>
              <h4>来源可信度分析：</h4>
              <ul style={{ lineHeight: '1.8' }}>
                <li><strong>国际权威度：</strong>
                  {selectedSourceInfo.country === 'United States' ? ' 美国主流财经媒体，覆盖全球金融市场' :
                   selectedSourceInfo.country === 'China' ? ' 中国本土财经媒体，专注A股市场' :
                   ' 国际财经媒体，提供全球视角'}
                </li>
                <li><strong>内容时效性：</strong>
                  实时更新，提供最新财经资讯和市场动态
                </li>
                <li><strong>专业程度：</strong>
                  拥有专业分析师团队，提供深度市场分析
                </li>
                <li><strong>数据来源：</strong>
                  基于官方RSS订阅，数据真实可靠
                </li>
              </ul>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default News;
