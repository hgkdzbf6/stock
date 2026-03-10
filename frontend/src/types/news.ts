/**
 * 新闻相关类型定义
 */

export interface NewsItem {
  /** 新闻ID */
  id: string;
  /** 标题 */
  title: string;
  /** 内容 */
  content: string;
  /** 摘要 */
  summary?: string;
  /** 链接 */
  link?: string;
  /** 发布时间 */
  published_time: string;
  /** 作者 */
  author?: string;
  /** 来源 */
  source: string;
  /** 来源详细信息 */
  source_info?: SourceInfo;
  /** 标签 */
  tags?: string[];
  /** URL（用于舆情分析） */
  url?: string;
  /** 股票代码 */
  stock_code?: string;
  /** 股票名称 */
  stock_name?: string;
}

export interface SourceInfo {
  /** 英文名称 */
  name: string;
  /** 中文名称 */
  name_cn: string;
  /** 英文描述 */
  description: string;
  /** 中文描述 */
  description_cn: string;
  /** 国家 */
  country: string;
  /** 国家（中文） */
  country_cn: string;
  /** 语言 */
  language: string;
  /** 语言（中文） */
  language_cn: string;
  /** 类别 */
  category: string;
  /** 覆盖范围 */
  coverage: string;
  /** 覆盖范围（中文） */
  coverage_cn: string;
}

export interface FundamentalsData {
  /** 市值 */
  market_cap?: string;
  /** 市盈率 */
  pe_ratio?: number;
  /** 市净率 */
  pb_ratio?: number;
  /** 净资产收益率 */
  roe?: number;
  /** 营收 */
  revenue?: string;
  /** 净利润 */
  net_profit?: string;
  /** 营收增长率 */
  revenue_growth?: number;
  /** 净利润增长率 */
  profit_growth?: number;
  /** 股息率 */
  dividend_yield?: number;
  /** 所属行业 */
  industry?: string;
}

export interface FundamentalsSummary {
  /** 股票代码 */
  stock_code: string;
  /** 股票名称 */
  stock_name: string;
  /** 市值 */
  market_cap: string;
  /** 市盈率 */
  pe_ratio: string;
  /** 市净率 */
  pb_ratio: string;
  /** 净资产收益率 */
  roe: string;
  /** 营收 */
  revenue: string;
  /** 净利润 */
  net_profit: string;
  /** 营收增长率 */
  revenue_growth: string;
  /** 净利润增长率 */
  profit_growth: string;
  /** 股息率 */
  dividend_yield: string;
  /** 所属行业 */
  industry: string;
  /** 总结文本 */
  summary_text: string;
}

export interface FetchStockNewsRequest {
  /** 股票代码 */
  stock_code: string;
  /** 股票名称 */
  stock_name: string;
  /** 板块名称（可选） */
  sector_name?: string;
  /** 市场类型: domestic(国内) 或 international(国外) */
  market?: string;
  /** 数据来源列表 */
  sources?: string[];
  /** 最大新闻数量 */
  limit?: number;
}

export interface FetchSectorNewsRequest {
  /** 板块名称 */
  sector_name: string;
  /** 最大新闻数量 */
  limit?: number;
}

export interface NewsResponse {
  /** 新闻列表 */
  news: NewsItem[];
  /** 总数 */
  total: number;
}