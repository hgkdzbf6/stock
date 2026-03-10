"""
新闻获取服务测试
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from services.news_fetcher import NewsFetcher, get_news_fetcher


class TestNewsFetcher:
    """新闻获取服务测试"""
    
    @pytest.fixture
    def news_fetcher(self):
        """创建新闻获取器实例"""
        return NewsFetcher()
    
    @pytest.mark.asyncio
    async def test_fetch_rss_news_success(self, news_fetcher):
        """测试成功获取RSS新闻"""
        # Mock HTTP响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <title>测试RSS</title>
                <item>
                    <title>测试新闻标题</title>
                    <description>测试新闻内容</description>
                    <link>https://example.com/news/1</link>
                    <pubDate>Wed, 20 Feb 2026 12:00:00 +0800</pubDate>
                    <author>测试作者</author>
                </item>
            </channel>
        </rss>"""
        
        # Mock HTTP client
        with patch.object(news_fetcher.client, 'get', AsyncMock(return_value=mock_response)):
            news_list = await news_fetcher.fetch_rss_news(
                rss_url="https://example.com/rss",
                limit=10
            )
        
        # 验证结果
        assert len(news_list) > 0
        assert news_list[0]['title'] == "测试新闻标题"
        assert news_list[0]['source'] == "测试"  # _extract_source会去除"RSS"关键词
    
    @pytest.mark.asyncio
    async def test_fetch_rss_news_error(self, news_fetcher):
        """测试获取RSS新闻失败"""
        # Mock HTTP错误
        with patch.object(news_fetcher.client, 'get', side_effect=Exception("网络错误")):
            news_list = await news_fetcher.fetch_rss_news(
                rss_url="https://example.com/rss",
                limit=10
            )
        
        # 验证返回空列表
        assert len(news_list) == 0
    
    @pytest.mark.asyncio
    async def test_clean_text(self, news_fetcher):
        """测试文本清理"""
        # HTML标签
        html_text = "<p>测试文本</p><br/><div>更多内容</div>"
        cleaned = news_fetcher._clean_text(html_text)
        assert "<p>" not in cleaned
        assert "<br/>" not in cleaned
        assert "<div>" not in cleaned
        assert "测试文本" in cleaned
        assert "更多内容" in cleaned
        
        # 长文本截断
        long_text = "A" * 2000
        cleaned = news_fetcher._clean_text(long_text)
        assert len(cleaned) <= 1003  # 1000 + "..."
        
        # 空文本
        cleaned = news_fetcher._clean_text("")
        assert cleaned == ""
        
        # None文本
        cleaned = news_fetcher._clean_text(None)
        assert cleaned == ""
    
    def test_parse_time(self, news_fetcher):
        """测试时间解析"""
        # RFC格式
        time_str = "Wed, 20 Feb 2026 12:00:00 +0800"
        parsed = news_fetcher._parse_time(time_str)
        assert "2026-02-20" in parsed
        
        # ISO格式
        time_str = "2026-02-20T12:00:00+08:00"
        parsed = news_fetcher._parse_time(time_str)
        assert "2026-02-20" in parsed
        
        # 无效格式
        time_str = "invalid time"
        parsed = news_fetcher._parse_time(time_str)
        assert parsed is not None
        
        # None时间
        parsed = news_fetcher._parse_time(None)
        assert parsed is not None
    
    def test_extract_source(self, news_fetcher):
        """测试提取新闻来源"""
        # 正常标题
        title = "新浪财经 RSS"
        source = news_fetcher._extract_source(title)
        assert source == "新浪财经"
        
        # 包含RSS关键词
        title = "财经新闻 RSS Feed"
        source = news_fetcher._extract_source(title)
        assert source == "财经新闻"
        
        # 空标题
        source = news_fetcher._extract_source("")
        assert source == "未知来源"
        
        # None标题
        source = news_fetcher._extract_source(None)
        assert source == "未知来源"
    
    def test_is_relevant_news(self, news_fetcher):
        """测试判断新闻是否相关"""
        news = {
            "title": "浦发银行发布重大利好消息",
            "content": "公司业绩大幅增长"
        }
        keywords = ["浦发银行", "600000"]
        
        # 相关新闻
        is_relevant = news_fetcher._is_relevant_news(news, keywords)
        assert is_relevant == True
        
        # 不相关新闻
        news = {
            "title": "其他股票新闻",
            "content": "其他内容"
        }
        is_relevant = news_fetcher._is_relevant_news(news, keywords)
        assert is_relevant == False
    
    def test_deduplicate_news(self, news_fetcher):
        """测试新闻去重"""
        news_list = [
            {"id": "123", "title": "新闻1"},
            {"id": "123", "title": "新闻1"},  # 重复
            {"id": "456", "title": "新闻2"},
            {"id": "789", "title": "新闻3"},
            {"id": "456", "title": "新闻2"},  # 重复
        ]
        
        unique_news = news_fetcher._deduplicate_news(news_list)
        
        # 验证去重
        assert len(unique_news) == 3
        ids = [news['id'] for news in unique_news]
        assert "123" in ids
        assert "456" in ids
        assert "789" in ids
    
    @pytest.mark.asyncio
    async def test_summarize_fundamentals(self, news_fetcher):
        """测试基本面总结"""
        fundamentals = {
            "market_cap": "5000亿",
            "pe_ratio": 5.5,
            "pb_ratio": 0.6,
            "roe": 12.5,
            "revenue": "1800亿",
            "net_profit": "200亿",
            "revenue_growth": 8.5,
            "profit_growth": 15.2,
            "dividend_yield": 4.2,
            "industry": "银行"
        }
        
        summary = await news_fetcher.summarize_fundamentals(
            stock_code="600000",
            stock_name="浦发银行",
            fundamentals=fundamentals
        )
        
        # 验证总结
        assert summary['stock_code'] == "600000"
        assert summary['stock_name'] == "浦发银行"
        assert summary['market_cap'] == "5000亿"
        assert summary['pe_ratio'] == 5.5
        assert summary['summary_text'] is not None
        assert len(summary['summary_text']) > 0
    
    def test_generate_fundamental_summary(self, news_fetcher):
        """测试生成基本面总结文本"""
        # 低PE
        fundamentals = {"pe_ratio": 10}
        summary = news_fetcher._generate_fundamental_summary(fundamentals)
        assert "估值相对便宜" in summary
        
        # 高PE
        fundamentals = {"pe_ratio": 40}
        summary = news_fetcher._generate_fundamental_summary(fundamentals)
        assert "估值相对昂贵" in summary
        
        # 高ROE
        fundamentals = {"roe": 20}
        summary = news_fetcher._generate_fundamental_summary(fundamentals)
        assert "盈利能力强" in summary
        
        # 高成长
        fundamentals = {"profit_growth": 30}
        summary = news_fetcher._generate_fundamental_summary(fundamentals)
        assert "成长性好" in summary
        
        # 高股息
        fundamentals = {"dividend_yield": 5}
        summary = news_fetcher._generate_fundamental_summary(fundamentals)
        assert "分红回报好" in summary
        
        # 无数据
        fundamentals = {}
        summary = news_fetcher._generate_fundamental_summary(fundamentals)
        assert "数据不足" in summary or len(summary) == 0
    
    def test_format_news_for_sentiment(self, news_fetcher):
        """测试格式化新闻用于舆情分析"""
        news_list = [
            {
                "id": "news_001",
                "title": "测试新闻",
                "content": "新闻内容",
                "source": "测试源",
                "published_time": "2026-02-20T12:00:00",
                "link": "https://example.com/news/1"
            }
        ]
        
        # 不含基本面
        formatted = news_fetcher.format_news_for_sentiment(news_list)
        assert len(formatted) == 1
        assert formatted[0]['id'] == "news_001"
        assert formatted[0]['title'] == "测试新闻"
        assert formatted[0]['url'] == "https://example.com/news/1"
        
        # 含基本面
        fundamentals = {
            "stock_code": "600000",
            "stock_name": "浦发银行",
            "market_cap": "5000亿"
        }
        formatted = news_fetcher.format_news_for_sentiment(news_list, fundamentals)
        assert len(formatted) == 1
        assert "【基本面信息】" in formatted[0]['content']
        assert "600000" in formatted[0]['content']
        assert "5000亿" in formatted[0]['content']
    
    def test_generate_news_id(self, news_fetcher):
        """测试生成新闻ID"""
        entry = {
            "link": "https://example.com/news/1",
            "published": "2026-02-20T12:00:00"
        }
        
        news_id = news_fetcher._generate_news_id(entry)
        
        # 验证ID格式
        assert len(news_id) == 16
        assert news_id.isalnum()
        
        # 相同内容生成相同ID
        news_id2 = news_fetcher._generate_news_id(entry)
        assert news_id == news_id2
        
        # 不同内容生成不同ID
        entry2 = {
            "link": "https://example.com/news/2",
            "published": "2026-02-20T13:00:00"
        }
        news_id3 = news_fetcher._generate_news_id(entry2)
        assert news_id != news_id3
    
    def test_get_news_fetcher_singleton(self):
        """测试新闻获取器单例"""
        fetcher1 = get_news_fetcher()
        fetcher2 = get_news_fetcher()
        
        # 验证是同一个实例
        assert fetcher1 is fetcher2