import React, { useState } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Space,
  DatePicker,
  Select,
  InputNumber,
  message,
  Row,
  Col,
  Typography,
  Divider,
  Tag,
  Progress,
  Alert,
  Tabs,
  List,
  Statistic,
  Spin,
} from 'antd';
import {
  SearchOutlined,
  BarChartOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  MinusOutlined,
} from '@ant-design/icons';
import type { Dayjs } from 'dayjs';
import dayjs from 'dayjs';
import sentimentService from '@/services/sentiment';
import { newsService } from '@/services/news';
import { marketService } from '@/services/market';
import type {
  SentimentAnalysis,
  SentimentBacktestResult,
  SentimentAggregation,
  NewsItem,
  ImpactDuration,
  SentimentTrend,
  SentimentHistory,
  PriceData,
} from '@/types/sentiment';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

const Sentiment: React.FC = () => {
  const [form] = Form.useForm();
  const [backtestForm] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [sentimentResult, setSentimentResult] = useState<SentimentAnalysis | null>(null);
  const [backtestResult, setBacktestResult] = useState<SentimentBacktestResult | null>(null);
  const [aggregationResult, setAggregationResult] = useState<SentimentAggregation | null>(null);

  // 处理舆情分析
  const handleAnalyze = async (values: any) => {
    setLoading(true);
    try {
      const newsData: NewsItem[] = values.news_items.map((item: any, index: number) => ({
        id: `news_${index}`,
        title: item.title,
        content: item.content,
        source: item.source || '未知来源',
        publish_time: dayjs().toISOString(),
      }));

      const result = await sentimentService.analyzeSentiment({
        stock_code: values.stock_code,
        stock_name: values.stock_name,
        sector_name: values.sector_name,
        news_data: newsData,
      });

      setSentimentResult(result);
      message.success('舆情分析完成');
    } catch (error: any) {
      message.error(`分析失败: ${error.message || '未知错误'}`);
    } finally {
      setLoading(false);
    }
  };

  // 处理回测
  const handleBacktest = async (values: any) => {
    setLoading(true);
    const loadingKey = 'sentiment-backtest-loading';
    try {
      const dateRange = values.date_range as [Dayjs, Dayjs];
      const start_date = dateRange[0].format('YYYY-MM-DD');
      const end_date = dateRange[1].format('YYYY-MM-DD');

      message.loading({
        content: '正在拉取真实新闻与行情数据...',
        key: loadingKey,
        duration: 0,
      });

      const stockCode = values.stock_code;
      const stockName = values.stock_name;

      // 1) 拉取真实新闻
      const newsResponse = await newsService.fetchStockNews({
        stock_code: stockCode,
        stock_name: stockName,
        limit: 80,
      });

      const fetchedNews = Array.isArray(newsResponse?.news) ? newsResponse.news : [];
      const startDateObj = dayjs(start_date);
      const endDateObj = dayjs(end_date);

      const backtestNewsItems = fetchedNews
        .map((item, index) => {
          const publishTime = item.published_time || '';
          return {
            id: `news_${index}`,
            title: item.title,
            content: item.content || item.summary || item.title,
            source: item.source || '未知来源',
            publish_time: publishTime,
          } as NewsItem;
        })
        .filter((item) => {
          if (!item.publish_time) return false;
          const publishDate = dayjs(item.publish_time);
          return publishDate.isValid() &&
            (publishDate.isAfter(startDateObj) || publishDate.isSame(startDateObj, 'day')) &&
            (publishDate.isBefore(endDateObj) || publishDate.isSame(endDateObj, 'day'));
        });

      if (backtestNewsItems.length === 0) {
        throw new Error('回测区间内未获取到真实新闻，请调整时间范围或股票后重试');
      }

      // 2) 对真实新闻做批量舆情分析，生成真实舆情历史
      const batchResult = await sentimentService.batchAnalyze({
        stock_code: stockCode,
        stock_name: stockName,
        news_items: backtestNewsItems,
      });

      const sentimentByNewsId = new Map(
        (batchResult?.results || []).map((item) => [item.news_id, item])
      );

      const sentimentHistory: SentimentHistory[] = backtestNewsItems
        .map((item) => {
          const analysis = sentimentByNewsId.get(item.id);
          if (!analysis) return null;
          const date = dayjs(item.publish_time).format('YYYY-MM-DD');
          return {
            date,
            sentiment_score: Number(analysis.sentiment_score ?? 0),
            impact_hours: Number(analysis.impact_hours ?? 24),
          } as SentimentHistory;
        })
        .filter((item): item is SentimentHistory => item !== null);

      if (sentimentHistory.length === 0) {
        throw new Error('未能生成真实舆情历史，请稍后重试');
      }

      // 3) 拉取真实K线数据，生成真实价格序列
      const klineResponse = await marketService.getKlineData({
        code: stockCode,
        freq: 'daily',
        start_date,
        end_date,
      });

      const rawKlineData: any[] = Array.isArray(klineResponse)
        ? klineResponse
        : Array.isArray(klineResponse?.data)
          ? klineResponse.data
          : [];

      if (rawKlineData.length === 0) {
        throw new Error('回测区间内未获取到真实价格数据，请调整时间范围后重试');
      }

      const sortedKlineData = [...rawKlineData].sort((left, right) => {
        const leftDate = dayjs(left.timestamp || left.date).valueOf();
        const rightDate = dayjs(right.timestamp || right.date).valueOf();
        return leftDate - rightDate;
      });

      const priceData: PriceData[] = sortedKlineData
        .map((item, index) => {
          const close = Number(item.close);
          if (!Number.isFinite(close)) return null;
          const date = dayjs(item.timestamp || item.date).format('YYYY-MM-DD');
          if (date === 'Invalid Date') return null;

          let changePct = Number(item.change_pct);
          if (!Number.isFinite(changePct)) {
            const prev = sortedKlineData[index - 1];
            const prevClose = Number(prev?.close);
            if (Number.isFinite(prevClose) && prevClose !== 0) {
              changePct = ((close - prevClose) / prevClose) * 100;
            } else {
              changePct = 0;
            }
          }

          return {
            date,
            close,
            change_pct: Number(changePct.toFixed(4)),
          } as PriceData;
        })
        .filter((item): item is PriceData => item !== null);

      if (priceData.length === 0) {
        throw new Error('未能生成真实价格序列，请稍后重试');
      }

      message.loading({
        content: '真实数据准备完成，正在执行回测...',
        key: loadingKey,
        duration: 0,
      });

      const result = await sentimentService.backtestSentiment({
        stock_code: stockCode,
        stock_name: stockName,
        start_date,
        end_date,
        sentiment_history: sentimentHistory,
        price_data: priceData,
      });

      setBacktestResult(result);
      message.success({
        content: `回测完成（新闻${sentimentHistory.length}条，K线${priceData.length}条）`,
        key: loadingKey,
      });
    } catch (error: any) {
      message.error({
        content: `回测失败: ${error?.response?.data?.detail || error.message || '未知错误'}`,
        key: loadingKey,
      });
    } finally {
      setLoading(false);
    }
  };

  // 处理聚合
  const handleAggregate = async (values: any) => {
    try {
      const scores = values.scores.split(',').map((s: string) => parseFloat(s.trim()));
      
      const result = await sentimentService.aggregateSentiment({
        sentiment_scores: scores,
        weights: values.weights ? values.weights.split(',').map((s: string) => parseFloat(s.trim())) : undefined,
      });

      setAggregationResult(result);
      message.success('聚合完成');
    } catch (error: any) {
      message.error(`聚合失败: ${error.message || '未知错误'}`);
    }
  };

  // 获取舆情分数颜色
  const getSentimentColor = (score: number) => {
    if (score > 50) return '#52c41a'; // 强正面
    if (score > 20) return '#95de64'; // 正面
    if (score > -20) return '#faad14'; // 中性
    if (score > -50) return '#ff7a45'; // 负面
    return '#ff4d4f'; // 强负面
  };

  // 获取影响时间文本
  const getImpactDurationText = (duration: ImpactDuration) => {
    const map: Record<ImpactDuration, string> = {
      short_term: '短期（1-3天）',
      medium_term: '中期（4-7天）',
      long_term: '长期（8天以上）',
    };
    return map[duration];
  };

  // 获取趋势图标
  const getTrendIcon = (trend: SentimentTrend) => {
    const map: Record<SentimentTrend, React.ReactNode> = {
      strongly_positive: <ArrowUpOutlined style={{ color: '#52c41a' }} />,
      positive: <ArrowUpOutlined style={{ color: '#95de64' }} />,
      neutral: <MinusOutlined style={{ color: '#faad14' }} />,
      negative: <ArrowDownOutlined style={{ color: '#ff7a45' }} />,
      strongly_negative: <ArrowDownOutlined style={{ color: '#ff4d4f' }} />,
    };
    return map[trend];
  };

  // 动态新闻项表单项
  const NewsItems = () => (
    <Form.List name="news_items">
      {(fields, { add, remove }) => (
        <>
          {fields.map(({ key, name, ...restField }) => (
            <Card
              key={key}
              size="small"
              style={{ marginBottom: 16 }}
              extra={
                <Button type="link" danger onClick={() => remove(name)}>
                  删除
                </Button>
              }
            >
              <Form.Item
                {...restField}
                name={[name, 'title']}
                label="新闻标题"
                rules={[{ required: true, message: '请输入新闻标题' }]}
              >
                <Input placeholder="输入新闻标题" />
              </Form.Item>
              <Form.Item
                {...restField}
                name={[name, 'content']}
                label="新闻内容"
                rules={[{ required: true, message: '请输入新闻内容' }]}
              >
                <TextArea rows={3} placeholder="输入新闻内容" />
              </Form.Item>
              <Form.Item
                {...restField}
                name={[name, 'source']}
                label="新闻来源"
              >
                <Input placeholder="输入新闻来源（可选）" />
              </Form.Item>
            </Card>
          ))}
          <Button type="dashed" onClick={() => add()} block icon={<SearchOutlined />}>
            添加新闻
          </Button>
        </>
      )}
    </Form.List>
  );

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>舆情分析</Title>
      <Paragraph type="secondary">
        分析新闻舆情对股票走势的影响，基于AI智能打分和回测分析
      </Paragraph>

      <Tabs
        defaultActiveKey="analyze"
        items={[
          {
            key: 'analyze',
            label: (
              <span>
                <ThunderboltOutlined />
                舆情分析
              </span>
            ),
            children: (
              <Row gutter={[16, 16]}>
                <Col xs={24} md={12}>
                  <Card title="输入信息" bordered>
                    <Form
                      form={form}
                      layout="vertical"
                      onFinish={handleAnalyze}
                      initialValues={{
                        news_items: [
                          {
                            title: '',
                            content: '',
                            source: '',
                          },
                        ],
                      }}
                    >
                      <Row gutter={16}>
                        <Col span={12}>
                          <Form.Item
                            name="stock_code"
                            label="股票代码"
                            rules={[{ required: true, message: '请输入股票代码' }]}
                          >
                            <Input placeholder="例如: 600000" />
                          </Form.Item>
                        </Col>
                        <Col span={12}>
                          <Form.Item
                            name="stock_name"
                            label="股票名称"
                            rules={[{ required: true, message: '请输入股票名称' }]}
                          >
                            <Input placeholder="例如: 浦发银行" />
                          </Form.Item>
                        </Col>
                      </Row>
                      <Form.Item name="sector_name" label="板块名称">
                        <Input placeholder="输入板块名称（可选）" />
                      </Form.Item>
                      <Divider orientation="left">新闻信息</Divider>
                      <NewsItems />
                      <Form.Item style={{ marginTop: 16 }}>
                        <Button
                          type="primary"
                          htmlType="submit"
                          loading={loading}
                          block
                          size="large"
                          icon={<SearchOutlined />}
                        >
                          开始分析
                        </Button>
                      </Form.Item>
                    </Form>
                  </Card>
                </Col>
                <Col xs={24} md={12}>
                  <Card title="分析结果" bordered>
                    {loading ? (
                      <div style={{ textAlign: 'center', padding: 40 }}>
                        <Spin size="large" />
                        <div style={{ marginTop: 16 }}>正在分析中...</div>
                      </div>
                    ) : sentimentResult ? (
                      <Space direction="vertical" style={{ width: '100%' }} size="large">
                        <Alert
                          message="分析完成"
                          description="舆情分析结果已生成"
                          type="success"
                          showIcon
                        />
                        
                        <div>
                          <Text strong>整体舆情评分：</Text>
                          <Title
                            level={1}
                            style={{ color: getSentimentColor(sentimentResult.overall_sentiment) }}
                          >
                            {sentimentResult.overall_sentiment > 0 ? '+' : ''}
                            {sentimentResult.overall_sentiment}
                          </Title>
                          <Progress
                            percent={((sentimentResult.overall_sentiment + 100) / 200) * 100}
                            strokeColor={getSentimentColor(sentimentResult.overall_sentiment)}
                            showInfo={false}
                          />
                        </div>

                        <Row gutter={16}>
                          <Col span={12}>
                            <Statistic
                              title="影响时间"
                              value={getImpactDurationText(sentimentResult.impact_duration)}
                              prefix={<ClockCircleOutlined />}
                            />
                          </Col>
                          <Col span={12}>
                            <Statistic
                              title="置信度"
                              value={sentimentResult.confidence}
                              precision={2}
                              suffix="%"
                              prefix={<CheckCircleOutlined />}
                            />
                          </Col>
                        </Row>

                        {sentimentResult.impact_hours > 0 && (
                          <div>
                            <Text strong>预估影响时长：</Text>
                            <Text type="secondary">
                              约 {sentimentResult.impact_hours} 小时
                            </Text>
                          </div>
                        )}

                        <div>
                          <Text strong>投资建议：</Text>
                          <Paragraph type={sentimentResult.overall_sentiment > 0 ? 'success' : 'warning'}>
                            {sentimentResult.investment_advice}
                          </Paragraph>
                        </div>

                        {sentimentResult.positive_factors.length > 0 && (
                          <div>
                            <Text strong style={{ color: '#52c41a' }}>正面因素：</Text>
                            <Space direction="vertical" style={{ width: '100%' }}>
                              {sentimentResult.positive_factors.map((factor, index) => (
                                <Tag key={index} color="success">
                                  {factor}
                                </Tag>
                              ))}
                            </Space>
                          </div>
                        )}

                        {sentimentResult.negative_factors.length > 0 && (
                          <div>
                            <Text strong style={{ color: '#ff4d4f' }}>负面因素：</Text>
                            <Space direction="vertical" style={{ width: '100%' }}>
                              {sentimentResult.negative_factors.map((factor, index) => (
                                <Tag key={index} color="error">
                                  {factor}
                                </Tag>
                              ))}
                            </Space>
                          </div>
                        )}

                        {sentimentResult.news_analysis.length > 0 && (
                          <div>
                            <Text strong>新闻详情：</Text>
                            <List
                              size="small"
                              dataSource={sentimentResult.news_analysis}
                              renderItem={(item) => (
                                <List.Item>
                                  <List.Item.Meta
                                    title={item.title}
                                    description={
                                      <Space>
                                        <Text type="secondary">
                                          评分: {item.sentiment_score}
                                        </Text>
                                        <Tag color={getSentimentColor(item.sentiment_score)}>
                                          {item.sentiment_score > 0 ? '正面' : item.sentiment_score < 0 ? '负面' : '中性'}
                                        </Tag>
                                      </Space>
                                    }
                                  />
                                </List.Item>
                              )}
                            />
                          </div>
                        )}
                      </Space>
                    ) : (
                      <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                        <SearchOutlined style={{ fontSize: 48 }} />
                        <div style={{ marginTop: 16 }}>请输入信息并点击分析</div>
                      </div>
                    )}
                  </Card>
                </Col>
              </Row>
            ),
          },
          {
            key: 'backtest',
            label: (
              <span>
                <BarChartOutlined />
                舆情回测
              </span>
            ),
            children: (
              <Row gutter={[16, 16]}>
                <Col xs={24} md={12}>
                  <Card title="回测参数" bordered>
                    <Form
                      form={backtestForm}
                      layout="vertical"
                      onFinish={handleBacktest}
                      initialValues={{
                        date_range: [dayjs().subtract(30, 'day'), dayjs()],
                      }}
                    >
                      <Row gutter={16}>
                        <Col span={12}>
                          <Form.Item
                            name="stock_code"
                            label="股票代码"
                            rules={[{ required: true, message: '请输入股票代码' }]}
                          >
                            <Input placeholder="例如: 600000" />
                          </Form.Item>
                        </Col>
                        <Col span={12}>
                          <Form.Item
                            name="stock_name"
                            label="股票名称"
                            rules={[{ required: true, message: '请输入股票名称' }]}
                          >
                            <Input placeholder="例如: 浦发银行" />
                          </Form.Item>
                        </Col>
                      </Row>
                      <Form.Item
                        name="date_range"
                        label="回测时间范围"
                        rules={[{ required: true, message: '请选择时间范围' }]}
                      >
                        <RangePicker style={{ width: '100%' }} />
                      </Form.Item>
                      <Form.Item style={{ marginTop: 16 }}>
                        <Button
                          type="primary"
                          htmlType="submit"
                          loading={loading}
                          block
                          size="large"
                          icon={<BarChartOutlined />}
                        >
                          开始回测
                        </Button>
                      </Form.Item>
                    </Form>
                  </Card>
                </Col>
                <Col xs={24} md={12}>
                  <Card title="回测结果" bordered>
                    {loading ? (
                      <div style={{ textAlign: 'center', padding: 40 }}>
                        <Spin size="large" />
                        <div style={{ marginTop: 16 }}>正在回测中...</div>
                      </div>
                    ) : backtestResult ? (
                      <Space direction="vertical" style={{ width: '100%' }} size="large">
                        <Alert
                          message="回测完成"
                          description="舆情影响回测结果已生成"
                          type="success"
                          showIcon
                        />
                        
                        <Row gutter={16}>
                          <Col span={12}>
                            <Statistic
                              title="相关系数"
                              value={backtestResult.correlation}
                              precision={3}
                              prefix={
                                backtestResult.correlation > 0 ? (
                                  <ArrowUpOutlined style={{ color: '#52c41a' }} />
                                ) : (
                                  <ArrowDownOutlined style={{ color: '#ff4d4f' }} />
                                )
                              }
                            />
                          </Col>
                          <Col span={12}>
                            <Statistic
                              title="预测准确率"
                              value={backtestResult.accuracy * 100}
                              precision={2}
                              suffix="%"
                              prefix={<CheckCircleOutlined />}
                            />
                          </Col>
                        </Row>

                        <div>
                          <Text strong>平均影响时长：</Text>
                          <Text type="secondary">
                            约 {backtestResult.impact_duration_hours} 小时
                          </Text>
                        </div>

                        <Row gutter={16}>
                          <Col span={8}>
                            <Statistic
                              title="数据点数"
                              value={backtestResult.data_points}
                            />
                          </Col>
                          <Col span={8}>
                            <Statistic
                              title="正面案例"
                              value={backtestResult.positive_cases}
                              valueStyle={{ color: '#52c41a' }}
                            />
                          </Col>
                          <Col span={8}>
                            <Statistic
                              title="负面案例"
                              value={backtestResult.negative_cases}
                              valueStyle={{ color: '#ff4d4f' }}
                            />
                          </Col>
                        </Row>

                        <div>
                          <Text strong>关键发现：</Text>
                          <List
                            size="small"
                            dataSource={backtestResult.key_findings}
                            renderItem={(item) => (
                              <List.Item>
                                <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                                {item}
                              </List.Item>
                            )}
                          />
                        </div>

                        <div>
                          <Text strong>投资建议：</Text>
                          <Paragraph type="secondary">
                            {backtestResult.investment_advice}
                          </Paragraph>
                        </div>
                      </Space>
                    ) : (
                      <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                        <BarChartOutlined style={{ fontSize: 48 }} />
                        <div style={{ marginTop: 16 }}>请输入参数并点击回测</div>
                      </div>
                    )}
                  </Card>
                </Col>
              </Row>
            ),
          },
          {
            key: 'aggregate',
            label: (
              <span>
                <ThunderboltOutlined />
                舆情聚合
              </span>
            ),
            children: (
              <Row gutter={[16, 16]}>
                <Col xs={24} md={12}>
                  <Card title="聚合参数" bordered>
                    <Form layout="vertical" onFinish={handleAggregate}>
                      <Form.Item
                        name="scores"
                        label="舆情分数（逗号分隔，范围-100到+100）"
                        rules={[{ required: true, message: '请输入舆情分数' }]}
                      >
                        <Input placeholder="例如: 60, 45, -30, 70, -20" />
                      </Form.Item>
                      <Form.Item name="weights" label="权重（逗号分隔，可选）">
                        <Input placeholder="例如: 1.0, 0.8, 0.6, 0.4, 0.2" />
                      </Form.Item>
                      <Form.Item>
                        <Button
                          type="primary"
                          htmlType="submit"
                          block
                          size="large"
                          icon={<ThunderboltOutlined />}
                        >
                          计算聚合
                        </Button>
                      </Form.Item>
                    </Form>
                  </Card>
                </Col>
                <Col xs={24} md={12}>
                  <Card title="聚合结果" bordered>
                    {aggregationResult ? (
                      <Space direction="vertical" style={{ width: '100%' }} size="large">
                        <Alert
                          message="聚合完成"
                          description="舆情聚合结果已生成"
                          type="success"
                          showIcon
                        />
                        
                        <div>
                          <Text strong>综合评分：</Text>
                          <Title
                            level={1}
                            style={{ color: getSentimentColor(aggregationResult.overall_score) }}
                          >
                            {aggregationResult.overall_score > 0 ? '+' : ''}
                            {aggregationResult.overall_score}
                          </Title>
                          {getTrendIcon(aggregationResult.trend)}
                          <Text strong style={{ marginLeft: 8 }}>
                            {aggregationResult.trend.replace('_', ' ').toUpperCase()}
                          </Text>
                        </div>

                        <Row gutter={16}>
                          <Col span={12}>
                            <Statistic
                              title="置信度"
                              value={aggregationResult.confidence * 100}
                              precision={2}
                              suffix="%"
                            />
                          </Col>
                          <Col span={12}>
                            <Statistic
                              title="数据条数"
                              value={aggregationResult.count}
                            />
                          </Col>
                        </Row>
                      </Space>
                    ) : (
                      <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                        <ThunderboltOutlined style={{ fontSize: 48 }} />
                        <div style={{ marginTop: 16 }}>请输入分数并点击计算</div>
                      </div>
                    )}
                  </Card>
                </Col>
              </Row>
            ),
          },
        ]}
      />
    </div>
  );
};

export default Sentiment;
