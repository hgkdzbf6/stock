/** 舆情分析相关类型定义 */

/** 影响时间 */
export enum ImpactDuration {
  SHORT_TERM = 'short_term',    // 短期（1-3天）
  MEDIUM_TERM = 'medium_term',  // 中期（4-7天）
  LONG_TERM = 'long_term',      // 长期（8天以上）
}

/** 影响等级 */
export enum ImpactLevel {
  LOW = 'low',       // 低影响
  MEDIUM = 'medium',  // 中等影响
  HIGH = 'high',      // 高影响
}

/** 舆情趋势 */
export enum SentimentTrend {
  STRONGLY_POSITIVE = 'strongly_positive',  // 强烈正面
  POSITIVE = 'positive',                // 正面
  NEUTRAL = 'neutral',                  // 中性
  NEGATIVE = 'negative',                // 负面
  STRONGLY_NEGATIVE = 'strongly_negative',  // 强烈负面
}

/** 新闻数据 */
export interface NewsItem {
  id: string;
  title: string;
  content: string;
  source: string;
  publish_time: string;
  url?: string;
}

/** 单条新闻分析结果 */
export interface NewsAnalysis {
  news_id: string;
  title: string;
  sentiment_score: number;  // -100 到 +100
  impact_level: ImpactLevel;
  impact_hours: number;     // 影响持续时间（小时）
  reason: string;
  confidence: number;        // 0 到 1
}

/** 舆情分析结果 */
export interface SentimentAnalysis {
  overall_sentiment: number;  // -100 到 +100
  positive_factors: string[];
  negative_factors: string[];
  impact_duration: ImpactDuration;
  impact_hours: number;
  confidence: number;
  investment_advice: string;
  news_analysis: NewsAnalysis[];
}

/** 批量分析结果 */
export interface BatchAnalysisResult {
  results: NewsAnalysis[];
  total: number;
}

/** 舆情历史记录 */
export interface SentimentHistory {
  date: string;
  sentiment_score: number;
  impact_hours: number;
}

/** 舆情回测结果 */
export interface SentimentBacktestResult {
  correlation: number;          // 相关系数（-1 到 1）
  accuracy: number;             // 预测准确率（0 到 1）
  impact_duration_hours: number;  // 平均影响时间（小时）
  key_findings: string[];
  investment_advice: string;
  data_points: number;
  positive_cases: number;
  negative_cases: number;
}

/** 舆情聚合结果 */
export interface SentimentAggregation {
  overall_score: number;
  trend: SentimentTrend;
  confidence: number;
  count: number;
}

/** 舆情分析请求 */
export interface AnalyzeSentimentRequest {
  stock_code: string;
  stock_name: string;
  sector_name?: string;
  news_data?: NewsItem[];
}

/** 批量分析请求 */
export interface BatchAnalyzeRequest {
  news_items: NewsItem[];
  stock_code: string;
  stock_name: string;
}

/** 回测请求 */
export interface BacktestRequest {
  stock_code: string;
  stock_name: string;
  start_date: string;
  end_date: string;
  sentiment_history?: SentimentHistory[];
  price_data?: PriceData[];
}

/** 价格数据 */
export interface PriceData {
  date: string;
  close: number;
  change_pct: number;
}

/** 聚合请求 */
export interface AggregateRequest {
  sentiment_scores: number[];
  weights?: number[];
}