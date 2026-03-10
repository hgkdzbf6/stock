"""
测试GLM API可用性
"""
import asyncio
import sys
from core.config import settings
from ai.llm_client import get_llm_client
from loguru import logger


async def test_glm_api():
    """测试GLM API是否可用"""
    
    logger.info("=" * 60)
    logger.info("开始测试GLM API")
    logger.info("=" * 60)
    
    # 检查配置
    logger.info("\n[1] 检查配置...")
    if not settings.GLM_API_KEY:
        logger.error("❌ GLM_API_KEY 未配置")
        logger.info("请在 backend/.env 文件中设置 GLM_API_KEY")
        return False
    
    logger.success(f"✓ GLM_API_KEY 已配置: {settings.GLM_API_KEY[:10]}...")
    logger.success(f"✓ GLM_API_BASE: {settings.GLM_API_BASE}")
    
    try:
        # 初始化客户端
        logger.info("\n[2] 初始化LLM客户端...")
        client = get_llm_client()
        logger.success("✓ LLM客户端初始化成功")
        
        # 测试简单对话
        logger.info("\n[3] 测试简单对话...")
        messages = [
            {"role": "user", "content": "请用一句话介绍你自己。"}
        ]
        
        logger.info(f"发送测试提示: {messages[0]['content']}")
        response = await client.chat_completion(messages)
        
        if response:
            logger.success("✓ 对话成功")
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            logger.info(f"AI回复: {content}")
        else:
            logger.error("❌ 对话失败，返回空响应")
            return False
        
        # 测试结构化输出
        logger.info("\n[4] 测试结构化输出...")
        structured_messages = [
            {
                "role": "user",
                "content": """请分析以下新闻的情感：
标题：公司发布业绩预告，净利润同比增长50%

请以JSON格式返回分析结果，包含以下字段：
- sentiment_score: 情感分数（-100到100）
- sentiment_label: 情感标签（正面/负面/中性）
- reason: 分析原因
"""
            }
        ]
        
        logger.info(f"发送结构化测试提示...")
        structured_response = await client.chat_completion(structured_messages)
        
        if structured_response:
            logger.success("✓ 结构化输出成功")
            content = structured_response.get("choices", [{}])[0].get("message", {}).get("content", "")
            logger.info(f"AI回复: {content}")
        else:
            logger.error("❌ 结构化输出失败")
            return False
        
        # 测试舆情分析
        logger.info("\n[5] 测试舆情分析...")
        from ai.sentiment_service import SentimentService, get_sentiment_service
        
        service = get_sentiment_service()
        
        # 准备测试数据
        test_news = [
            {
                "id": "test_001",
                "title": "浦发银行发布重大利好消息",
                "content": "公司发布业绩预告，预计净利润同比增长50%以上，远超市场预期。",
                "source": "财经新闻",
                "publish_time": "2026-02-20T12:00:00"
            }
        ]
        
        logger.info(f"测试股票: 浦发银行 (600000)")
        logger.info(f"测试新闻数量: {len(test_news)}")
        
        result_generator = service.analyze_news(
            user_id=1,
            news_data=test_news,
            stock_code="600000",
            stock_name="浦发银行",
            sector_name="银行",
            stream=False
        )
        
        # 提取结果
        result = None
        async for item in result_generator:
            result = item
            break
        
        if result:
            logger.success("✓ 舆情分析成功")
            logger.info(f"整体舆情分数: {result.get('overall_sentiment')}")
            logger.info(f"影响时间: {result.get('impact_duration')}")
            logger.info(f"置信度: {result.get('confidence')}")
            logger.info(f"正面因素: {result.get('positive_factors')}")
            logger.info(f"负面因素: {result.get('negative_factors')}")
            logger.info(f"投资建议: {result.get('investment_advice')}")
        else:
            logger.error("❌ 舆情分析失败")
            return False
        
        logger.info("\n" + "=" * 60)
        logger.success("🎉 所有测试通过！GLM API 可用性良好")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"\n❌ 测试失败: {str(e)}")
        logger.exception("详细错误信息:")
        return False


async def main():
    """主函数"""
    try:
        success = await test_glm_api()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.warning("\n用户中断测试")
        sys.exit(1)
    except Exception as e:
        logger.error(f"测试过程出错: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())