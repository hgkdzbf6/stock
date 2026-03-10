"""
新闻获取服务 - RSS订阅和新闻抓取
"""
import feedparser
import httpx
import pandas as pd
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from loguru import logger
import re
import time


class NewsFetcher:
    """新闻获取服务"""
    
    def __init__(self):
        """初始化新闻获取服务"""
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )
        
        # RSS源详细信息配置
        self.rss_source_info = {
            "https://www.cnbc.com/id/10000664/device/rss/rss.html": {
                "name": "CNBC International Business News",
                "name_cn": "CNBC国际商业新闻",
                "description": "Leading source of global business news, financial market coverage, and economic analysis",
                "description_cn": "全球商业新闻、金融市场覆盖和经济分析的领先来源",
                "country": "United States",
                "country_cn": "美国",
                "language": "English",
                "language_cn": "英语",
                "category": "财经",
                "coverage": "Global financial markets and business news",
                "coverage_cn": "全球金融市场和商业新闻"
            },
            "https://finance.yahoo.com/news/rssindex": {
                "name": "Yahoo Finance",
                "name_cn": "雅虎财经",
                "description": "Comprehensive financial news, stock data, and market analysis",
                "description_cn": "综合财经新闻、股票数据和市场分析",
                "country": "United States",
                "country_cn": "美国",
                "language": "English",
                "language_cn": "英语",
                "category": "财经",
                "coverage": "Global financial markets, stocks, and investment news",
                "coverage_cn": "全球金融市场、股票和投资新闻"
            },
            "https://feeds.bloomberg.com/markets/news.rss": {
                "name": "Bloomberg Markets News",
                "name_cn": "彭博市场新闻",
                "description": "Real-time financial market news, analysis, and data",
                "description_cn": "实时金融市场新闻、分析和数据",
                "country": "United States",
                "country_cn": "美国",
                "language": "English",
                "language_cn": "英语",
                "category": "财经",
                "coverage": "Global financial markets and business news",
                "coverage_cn": "全球金融市场和商业新闻"
            },
            "https://www.cnbc.com/id/100727362/device/rss/rss.html": {
                "name": "CNBC Stock Market News",
                "name_cn": "CNBC股市新闻",
                "description": "Real-time stock market news, quotes, and analysis",
                "description_cn": "实时股市新闻、报价和分析",
                "country": "United States",
                "country_cn": "美国",
                "language": "English",
                "language_cn": "英语",
                "category": "股票",
                "coverage": "US and global stock market coverage",
                "coverage_cn": "美国和全球股市覆盖"
            },
            "https://feeds.a.dj.com/rss/RSSMarketsMain.xml": {
                "name": "The Wall Street Journal - Markets",
                "name_cn": "华尔街日报-市场",
                "description": "In-depth financial news, market analysis, and business reporting",
                "description_cn": "深入财经新闻、市场分析和商业报道",
                "country": "United States",
                "country_cn": "美国",
                "language": "English",
                "language_cn": "英语",
                "category": "股票",
                "coverage": "Global markets, stocks, and financial news",
                "coverage_cn": "全球市场、股票和财经新闻"
            },
            "https://www.marketwatch.com/rss/topstories": {
                "name": "MarketWatch",
                "name_cn": "市场观察",
                "description": "Financial market news, analysis, and investment tools",
                "description_cn": "金融市场新闻、分析和投资工具",
                "country": "United States",
                "country_cn": "美国",
                "language": "English",
                "language_cn": "英语",
                "category": "国际",
                "coverage": "US and international financial markets",
                "coverage_cn": "美国和国际金融市场"
            },
            "https://finance.sina.com.cn": {
                "name": "Sina Finance",
                "name_cn": "新浪财经",
                "description": "China's leading financial news and information portal",
                "description_cn": "中国领先的财经新闻和信息门户",
                "country": "China",
                "country_cn": "中国",
                "language": "Chinese",
                "language_cn": "中文",
                "category": "A股",
                "coverage": "Chinese A-share market and financial news",
                "coverage_cn": "中国A股市场和财经新闻"
            }
        }
        
        # 默认RSS源配置（使用经过验证的真实RSS源）
        self.default_rss_sources = {
            "财经": [
                "https://www.cnbc.com/id/10000664/device/rss/rss.html",  # CNBC国际财经 - 30条
                "https://finance.yahoo.com/news/rssindex",  # 雅虎财经 - 45条
                "https://feeds.bloomberg.com/markets/news.rss",  # Bloomberg - 30条
            ],
            "股票": [
                "https://www.cnbc.com/id/100727362/device/rss/rss.html",  # CNBC股票 - 30条
                "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",  # 华尔街日报 - 20条
            ],
            "国际": [
                "https://www.marketwatch.com/rss/topstories",  # MarketWatch - 10条
            ]
        }
        
        logger.info(f"配置了 {len(self.default_rss_sources)} 个RSS源类别")
        for category, urls in self.default_rss_sources.items():
            logger.info(f"  {category}: {len(urls)} 个源")
        
        logger.info("新闻获取服务初始化完成")
    
    async def fetch_a_share_news(
        self,
        stock_code: Optional[str] = None,
        stock_name: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取A股相关新闻（从新浪财经）
        
        Args:
            stock_code: 股票代码（可选）
            stock_name: 股票名称（可选）
            limit: 最大新闻数量
            
        Returns:
            新闻列表
        """
        try:
            logger.info(f"开始获取A股新闻: {stock_code} - {stock_name}")
            
            # 构建新浪财经新闻API URL
            base_url = "https://feed.sina.com.cn/api/roll/get"
            
            # 构建查询参数
            params = {
                "page": "1",
                "num": str(limit),
                "length": "120",
                "page": str(1)
            }
            
            # 如果有股票代码，添加到查询参数
            if stock_code:
                params["keyword"] = stock_code.strip()
            elif stock_name:
                params["keyword"] = stock_name.strip()
            else:
                # 没有股票信息，使用财经关键词获取最新新闻
                params["keyword"] = "财经"
            
            # 获取新闻数据
            response = await self.client.get(
                base_url,
                params=params,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Referer": "https://finance.sina.com.cn/",
                    "Accept": "application/json, text/plain, */*"
                }
            )
            response.raise_for_status()
            
            # 解析JSON响应
            data = response.json()
            
            if not data or "result" not in data or not data["result"]["data"]:
                logger.warning("新浪财经新闻数据为空")
                return []
            
            news_list = []
            
            for item in data["result"]["data"]:
                try:
                    # 解析新闻时间
                    publish_time = item.get("ctime", "")
                    if publish_time:
                        try:
                            # 时间格式：2025-02-21 14:35:02
                            dt = datetime.strptime(publish_time, "%Y-%m-%d %H:%M:%S")
                            publish_time = dt.isoformat()
                        except Exception as e:
                            logger.warning(f"解析时间失败: {publish_time}, {e}")
                            publish_time = datetime.now().isoformat()
                    
                    # 如果有股票名称，进行过滤
                    if stock_name:
                        title = item.get("title", "")
                        if stock_name not in title:
                            continue
                    
                    news_item = {
                        "id": self._generate_news_id({
                            "link": item.get("url", ""),
                            "published": publish_time
                        }),
                        "title": item.get("title", ""),
                        "content": item.get("content", "")[:1000] if item.get("content") else item.get("title", ""),
                        "summary": item.get("title", "")[:200],
                        "link": item.get("url", ""),
                        "published_time": publish_time,
                        "author": item.get("author", "新浪财经"),
                        "source": "新浪财经",
                        "source_info": self.rss_source_info.get("https://finance.sina.com.cn", {}),
                        "tags": [],
                        "stock_code": stock_code or "",
                        "stock_name": stock_name or ""
                    }
                    news_list.append(news_item)
                except Exception as e:
                    logger.warning(f"处理新闻失败: {e}")
                    continue
            
            logger.info(f"成功获取 {len(news_list)} 条A股新闻")
            return news_list[:limit]
            
        except Exception as e:
            logger.error(f"获取A股新闻失败: {e}")
            # 如果失败，返回空列表
            return []
    
    async def fetch_rss_news(
        self,
        rss_url: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """从RSS源获取新闻
        
        Args:
            rss_url: RSS URL
            limit: 最大新闻数量
            
        Returns:
            新闻列表
        """
        try:
            # 获取RSS内容
            response = await self.client.get(rss_url)
            response.raise_for_status()
            
            # 解析RSS
            feed = feedparser.parse(response.text)
            
            # 提取新闻
            news_list = []
            for entry in feed.entries[:limit]:
                source = self._extract_source(feed.feed.get("title", rss_url))
                news_item = {
                    "id": self._generate_news_id(entry),
                    "title": self._clean_text(entry.get("title", "")),
                    "content": self._clean_text(entry.get("description", "")),
                    "summary": self._clean_text(entry.get("summary", "")),
                    "link": entry.get("link", ""),
                    "published_time": self._parse_time(entry.get("published")),
                    "author": entry.get("author", ""),
                    "source": source,
                    "source_info": self.rss_source_info.get(rss_url, {}),
                    "tags": [tag.term for tag in entry.get("tags", [])]
                }
                
                # 优先使用summary，其次description
                if news_item["summary"] and len(news_item["summary"]) > len(news_item["content"]):
                    news_item["content"] = news_item["summary"]
                
                news_list.append(news_item)
            
            logger.info(f"从 {rss_url} 获取了 {len(news_list)} 条新闻")
            return news_list
            
        except Exception as e:
            logger.error(f"获取RSS新闻失败: {rss_url}, 错误: {e}")
            return []
    
    async def fetch_stock_news(
        self,
        stock_code: str,
        stock_name: str,
        sector_name: Optional[str] = None,
        market: Optional[str] = None,
        sources: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取股票相关新闻（优先A股）
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            sector_name: 板块名称
            market: 市场类型 (domestic/international)
            sources: 数据来源列表
            limit: 最大新闻数量
            
        Returns:
            新闻列表
        """
        logger.info(f"开始获取股票新闻: {stock_code} - {stock_name}, market={market}, sources={sources}")
        
        news_list = []
        
        # 清理输入
        code = stock_code.strip() if stock_code else ""
        name = stock_name.strip() if stock_name else ""
        
        # 确定使用哪些RSS源
        rss_sources_to_use = []
        if sources and len(sources) > 0:
            # 用户指定了具体来源 - 只从这些来源获取新闻
            logger.info(f"用户指定了数据来源: {sources}")
            for source_name in sources:
                for category, urls in self.default_rss_sources.items():
                    for url in urls:
                        source_info = self.rss_source_info.get(url, {})
                        if source_info.get("name_cn") == source_name or source_info.get("name") == source_name:
                            rss_sources_to_use.append(url)
                            logger.info(f"添加RSS源: {source_name} -> {url}")
                            break
        else:
            # 用户未指定来源，根据市场类型选择来源
            if market == "domestic":
                # 国内市场：只使用新浪财经
                rss_sources_to_use = ["https://finance.sina.com.cn"]
                logger.info("使用国内市场源: 新浪财经")
            elif market == "international":
                # 国际市场：使用国外RSS源
                rss_sources_to_use = []
                rss_sources_to_use.extend(self.default_rss_sources.get("财经", []))
                rss_sources_to_use.extend(self.default_rss_sources.get("股票", []))
                rss_sources_to_use.extend(self.default_rss_sources.get("国际", []))
                logger.info(f"使用国际市场源: {len(rss_sources_to_use)} 个RSS源")
            else:
                # 默认：优先A股，然后RSS源
                rss_sources_to_use = []
                rss_sources_to_use.extend(self.default_rss_sources.get("财经", []))
                rss_sources_to_use.extend(self.default_rss_sources.get("股票", []))
                rss_sources_to_use.extend(self.default_rss_sources.get("国际", []))
                logger.info(f"使用默认源: {len(rss_sources_to_use)} 个RSS源")
        
        # 获取A股新闻（如果未指定只使用国际市场，并且来源中包含新浪财经或未指定来源）
        should_fetch_a_share = False
        if sources and len(sources) > 0:
            # 用户指定了来源，检查是否包含新浪财经
            # 注意：由于新浪财经API不可用，我们会从RSS源获取新闻
            has_sina = "新浪财经" in sources or "Sina Finance" in sources
            if has_sina:
                # 如果包含新浪财经，从RSS源获取新闻
                should_fetch_a_share = False
                # 使用所有RSS源
                rss_sources_to_use = []
                rss_sources_to_use.extend(self.default_rss_sources.get("财经", []))
                rss_sources_to_use.extend(self.default_rss_sources.get("股票", []))
                rss_sources_to_use.extend(self.default_rss_sources.get("国际", []))
                logger.info("新浪财经选项：使用RSS源获取新闻")
            else:
                # 没有新浪财经，正常处理
                should_fetch_a_share = False
        elif market == "domestic" or market is None:
            # 用户未指定来源，国内市场或默认情况下
            # 新浪财经API不可用，使用RSS源
            should_fetch_a_share = False
            rss_sources_to_use = []
            rss_sources_to_use.extend(self.default_rss_sources.get("财经", []))
            rss_sources_to_use.extend(self.default_rss_sources.get("股票", []))
            rss_sources_to_use.extend(self.default_rss_sources.get("国际", []))
            logger.info("使用RSS源获取新闻")
        
        # 如果需要获取A股新闻
        if should_fetch_a_share:
            try:
                logger.info("获取A股新闻...")
                a_share_news = await self.fetch_a_share_news(
                    stock_code=code if code else None,
                    stock_name=name if name else None,
                    limit=limit
                )
                if a_share_news:
                    news_list.extend(a_share_news)
                    logger.info(f"获取到 {len(a_share_news)} 条A股新闻")
            except Exception as e:
                logger.warning(f"获取A股新闻失败: {e}")
        
        # 从RSS源获取新闻
        # 注意：新浪财经不是RSS源，只通过API获取，不需要从这里获取
        should_fetch_rss = False
        if sources and len(sources) > 0:
            # 用户指定了来源，只有当来源中包含RSS源时才获取RSS新闻
            # 新浪财经不是RSS源，应该被排除
            has_rss_sources = any(
                source_name not in ["新浪财经", "Sina Finance"] 
                for source_name in sources
            )
            should_fetch_rss = has_rss_sources and len(rss_sources_to_use) > 0
        else:
            # 用户未指定来源，根据市场类型决定
            should_fetch_rss = market != "domestic" and len(rss_sources_to_use) > 0
        
        if should_fetch_rss and (len(news_list) < limit or market == "international"):
            needed = limit - len(news_list) if len(news_list) < limit else limit
            logger.info(f"从RSS源获取新闻，需要 {needed} 条，可用源: {len(rss_sources_to_use)} 个")
            
            # 构建搜索关键词
            keywords = []
            if code:
                keywords.append(code)
            if name:
                keywords.append(name)
            if sector_name and sector_name.strip():
                keywords.append(sector_name.strip())
            
            # 从选定的RSS源获取新闻
            for rss_url in rss_sources_to_use:
                if len(news_list) >= limit:
                    break
                    
                try:
                    all_news = await self.fetch_rss_news(rss_url, limit=needed)
                    
                    # 过滤相关新闻
                    for news in all_news:
                        if len(news_list) >= limit:
                            break
                            
                        if keywords:
                            if self._is_relevant_news(news, keywords):
                                news_list.append(news)
                        else:
                            # 没有关键词，返回所有新闻
                            news_list.append(news)
                except Exception as e:
                    logger.warning(f"从 {rss_url} 获取新闻失败: {e}")
        
        # 去重和排序
        news_list = self._deduplicate_news(news_list)
        news_list = sorted(
            news_list,
            key=lambda x: x.get("published_time", ""),
            reverse=True
        )
        
        logger.info(f"找到 {len(news_list)} 条相关新闻")
        return news_list[:limit]
    
    async def fetch_sector_news(
        self,
        sector_name: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取板块相关新闻
        
        Args:
            sector_name: 板块名称
            limit: 最大新闻数量
            
        Returns:
            新闻列表
        """
        logger.info(f"开始获取板块新闻: {sector_name}")
        
        news_list = []
        
        # 清理板块名称
        sector = sector_name.strip() if sector_name else ""
        
        # 获取板块相关的RSS源
        sources = self.default_rss_sources.get(sector, [])
        if not sources:
            # 如果没有专门的板块源，使用财经源
            sources = self.default_rss_sources.get("财经", [])
        
        for rss_url in sources:
            try:
                all_news = await self.fetch_rss_news(rss_url, limit=limit)
                
                # 过滤板块相关新闻（如果有板块名称则过滤，否则返回所有新闻）
                if sector:
                    for news in all_news:
                        if sector in news["title"] or sector in news["content"]:
                            news_list.append(news)
                else:
                    # 没有板块名称，返回所有新闻
                    news_list.extend(all_news)
            except Exception as e:
                logger.warning(f"从 {rss_url} 获取新闻失败: {e}")
        
        # 去重和排序
        news_list = self._deduplicate_news(news_list)
        news_list = sorted(
            news_list,
            key=lambda x: x.get("published_time", ""),
            reverse=True
        )
        
        logger.info(f"找到 {len(news_list)} 条板块新闻")
        return news_list[:limit]
    
    async def summarize_fundamentals(
        self,
        stock_code: str,
        stock_name: str,
        fundamentals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """总结基本面信息
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            fundamentals: 基本面数据
            
        Returns:
            基本面总结
        """
        logger.info(f"总结基本面信息: {stock_code} - {stock_name}")
        
        # 提取关键指标
        summary = {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "market_cap": fundamentals.get("market_cap", "未知"),
            "pe_ratio": fundamentals.get("pe_ratio", "未知"),
            "pb_ratio": fundamentals.get("pb_ratio", "未知"),
            "roe": fundamentals.get("roe", "未知"),
            "revenue": fundamentals.get("revenue", "未知"),
            "net_profit": fundamentals.get("net_profit", "未知"),
            "revenue_growth": fundamentals.get("revenue_growth", "未知"),
            "profit_growth": fundamentals.get("profit_growth", "未知"),
            "dividend_yield": fundamentals.get("dividend_yield", "未知"),
            "industry": fundamentals.get("industry", "未知"),
            "summary_text": self._generate_fundamental_summary(fundamentals)
        }
        
        return summary
    
    def format_news_for_sentiment(
        self,
        news_list: List[Dict[str, Any]],
        fundamentals: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """格式化新闻用于舆情分析
        
        Args:
            news_list: 新闻列表
            fundamentals: 基本面数据（可选）
            
        Returns:
            格式化后的新闻列表
        """
        formatted_news = []
        
        for news in news_list:
            formatted_item = {
                "id": news.get("id", ""),
                "title": news.get("title", ""),
                "content": news.get("content", ""),
                "source": news.get("source", ""),
                "publish_time": news.get("published_time", ""),
                "url": news.get("link", "")
            }
            formatted_news.append(formatted_item)
        
        # 如果有基本面数据，添加到第一条新闻中
        if fundamentals and formatted_news:
            formatted_news[0]["content"] = f"""{formatted_news[0]['content']}

【基本面信息】
股票代码: {fundamentals.get('stock_code', '')}
股票名称: {fundamentals.get('stock_name', '')}
市值: {fundamentals.get('market_cap', '')}
市盈率: {fundamentals.get('pe_ratio', '')}
市净率: {fundamentals.get('pb_ratio', '')}
净资产收益率: {fundamentals.get('roe', '')}
营收: {fundamentals.get('revenue', '')}
净利润: {fundamentals.get('net_profit', '')}
营收增长率: {fundamentals.get('revenue_growth', '')}
净利润增长率: {fundamentals.get('profit_growth', '')}
股息率: {fundamentals.get('dividend_yield', '')}
所属行业: {fundamentals.get('industry', '')}

总结: {fundamentals.get('summary_text', '')}
"""
        
        return formatted_news
    
    def _generate_news_id(self, entry: Dict[str, Any]) -> str:
        """生成新闻ID"""
        import hashlib
        content = f"{entry.get('link', '')}{entry.get('published', '')}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        
        # 截断过长文本
        if len(text) > 1000:
            text = text[:1000] + "..."
        
        return text.strip()
    
    def _parse_time(self, time_str: Optional[str]) -> str:
        """解析时间"""
        if not time_str:
            return datetime.now().isoformat()
        
        try:
            # 尝试解析各种时间格式
            dt = datetime.strptime(time_str, "%a, %d %b %Y %H:%M:%S %z")
            return dt.isoformat()
        except:
            try:
                dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S%z")
                return dt.isoformat()
            except:
                return datetime.now().isoformat()
    
    def _extract_source(self, title: str) -> str:
        """提取新闻来源"""
        if not title:
            return "未知来源"
        
        # 移除RSS、feed等关键词
        source = re.sub(r'\s*(RSS|Feed|订阅)\s*', '', title, flags=re.IGNORECASE)
        return source.strip()
    
    def _is_relevant_news(self, news: Dict[str, Any], keywords: List[str]) -> bool:
        """判断新闻是否相关"""
        text = f"{news.get('title', '')} {news.get('content', '')}"
        
        for keyword in keywords:
            if keyword in text:
                return True
        
        return False
    
    def _deduplicate_news(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重新闻"""
        seen_ids = set()
        unique_news = []
        
        for news in news_list:
            news_id = news.get("id", "")
            if news_id and news_id not in seen_ids:
                seen_ids.add(news_id)
                unique_news.append(news)
        
        return unique_news
    
    def _generate_fundamental_summary(self, fundamentals: Dict[str, Any]) -> str:
        """生成基本面总结"""
        summary_parts = []
        
        # 估值分析
        pe = fundamentals.get("pe_ratio", 0)
        if pe and isinstance(pe, (int, float)):
            if pe < 15:
                summary_parts.append("市盈率较低，估值相对便宜")
            elif pe > 30:
                summary_parts.append("市盈率较高，估值相对昂贵")
            else:
                summary_parts.append("市盈率处于合理水平")
        
        # 盈利能力
        roe = fundamentals.get("roe", 0)
        if roe and isinstance(roe, (int, float)):
            if roe > 15:
                summary_parts.append("净资产收益率高，盈利能力强")
            elif roe > 10:
                summary_parts.append("净资产收益率中等，盈利能力尚可")
            else:
                summary_parts.append("净资产收益率较低，盈利能力偏弱")
        
        # 成长性
        growth = fundamentals.get("profit_growth", 0)
        if growth and isinstance(growth, (int, float)):
            if growth > 20:
                summary_parts.append("净利润增长率高，成长性好")
            elif growth > 10:
                summary_parts.append("净利润增长率中等，成长性尚可")
            elif growth > 0:
                summary_parts.append("净利润有增长")
            else:
                summary_parts.append("净利润增长为负，成长性较差")
        
        # 股息率
        dividend = fundamentals.get("dividend_yield", 0)
        if dividend and isinstance(dividend, (int, float)):
            if dividend > 3:
                summary_parts.append("股息率高，分红回报好")
            elif dividend > 1:
                summary_parts.append("股息率中等，有一定分红")
            else:
                summary_parts.append("股息率较低，分红回报少")
        
        return "；".join(summary_parts) if summary_parts else "基本面数据不足，无法总结"
    
    async def check_sina_api(self) -> bool:
        """检查新浪财经API是否可用
        
        Returns:
            True如果可用，False如果不可用
        """
        try:
            base_url = "https://feed.sina.com.cn/api/roll/get"
            params = {
                "page": "1",
                "num": "1",
                "length": "120",
                "keyword": "测试"
            }
            
            response = await self.client.get(
                base_url,
                params=params,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Referer": "https://finance.sina.com.cn/",
                    "Accept": "application/json, text/plain, */*"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and "result" in data:
                    logger.info("新浪财经API可用")
                    return True
            
            logger.warning("新浪财经API不可用")
            return False
        except Exception as e:
            logger.warning(f"新浪财经API检查失败: {e}")
            return False
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()
        logger.info("新闻获取服务已关闭")


# 单例模式
_news_fetcher: Optional[NewsFetcher] = None


def get_news_fetcher() -> NewsFetcher:
    """获取新闻获取服务单例
    
    Returns:
        新闻获取服务实例
    """
    global _news_fetcher
    if _news_fetcher is None:
        _news_fetcher = NewsFetcher()
    return _news_fetcher