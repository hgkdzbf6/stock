"""舆情API真实数据约束单元测试"""

import os
import sys
import pytest
from fastapi import HTTPException


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api import sentiment as sentiment_api


class DummyUser:
    def __init__(self, user_id: int = 1):
        self.id = user_id


class DummySentimentService:
    def __init__(self):
        self.last_analyze_kwargs = None
        self.last_backtest_kwargs = None

    async def analyze_news(self, **kwargs):
        self.last_analyze_kwargs = kwargs
        yield {"overall_sentiment": 12, "confidence": 0.8}

    async def backtest_sentiment_impact(self, **kwargs):
        self.last_backtest_kwargs = kwargs
        return {"correlation": 0.35, "accuracy": 0.62}


@pytest.mark.asyncio
async def test_analyze_news_requires_real_news_data(monkeypatch):
    service = DummySentimentService()
    monkeypatch.setattr(sentiment_api, "get_sentiment_service", lambda: service)

    request = sentiment_api.AnalyzeSentimentRequest(
        stock_code="600000",
        stock_name="浦发银行",
        news_data=None,
    )

    with pytest.raises(HTTPException) as exc_info:
        await sentiment_api.analyze_news(request=request, current_user=DummyUser())

    assert exc_info.value.status_code == 400
    assert "news_data" in exc_info.value.detail
    assert service.last_analyze_kwargs is None


@pytest.mark.asyncio
async def test_analyze_news_uses_provided_real_news(monkeypatch):
    service = DummySentimentService()
    monkeypatch.setattr(sentiment_api, "get_sentiment_service", lambda: service)

    request = sentiment_api.AnalyzeSentimentRequest(
        stock_code="600000",
        stock_name="浦发银行",
        news_data=[
            sentiment_api.NewsItem(
                id="n1",
                title="真实新闻",
                content="公司披露季度报告",
                source="上交所公告",
                publish_time="2026-03-07T09:30:00",
            )
        ],
    )

    result = await sentiment_api.analyze_news(request=request, current_user=DummyUser())

    assert result["code"] == 200
    assert service.last_analyze_kwargs is not None
    assert service.last_analyze_kwargs["news_data"][0]["title"] == "真实新闻"


@pytest.mark.asyncio
async def test_backtest_requires_real_histories(monkeypatch):
    service = DummySentimentService()
    monkeypatch.setattr(sentiment_api, "get_sentiment_service", lambda: service)

    request = sentiment_api.BacktestRequest(
        stock_code="600000",
        stock_name="浦发银行",
        start_date="2026-02-01",
        end_date="2026-03-01",
        sentiment_history=None,
        price_data=None,
    )

    with pytest.raises(HTTPException) as exc_info:
        await sentiment_api.backtest_sentiment_impact(request=request, current_user=DummyUser())

    assert exc_info.value.status_code == 400
    assert "sentiment_history" in exc_info.value.detail
    assert service.last_backtest_kwargs is None


@pytest.mark.asyncio
async def test_backtest_rejects_invalid_dates(monkeypatch):
    service = DummySentimentService()
    monkeypatch.setattr(sentiment_api, "get_sentiment_service", lambda: service)

    request = sentiment_api.BacktestRequest(
        stock_code="600000",
        stock_name="浦发银行",
        start_date="invalid-date",
        end_date="2026-03-01",
        sentiment_history=[{"date": "2026-02-10", "sentiment_score": 10}],
        price_data=[{"date": "2026-02-10", "close": 10.2}],
    )

    with pytest.raises(HTTPException) as exc_info:
        await sentiment_api.backtest_sentiment_impact(request=request, current_user=DummyUser())

    assert exc_info.value.status_code == 400
    assert "格式错误" in exc_info.value.detail
    assert service.last_backtest_kwargs is None
