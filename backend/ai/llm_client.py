"""LLM客户端封装 - 支持GLM 4.7"""
import os
import json
import httpx
from typing import AsyncIterator, Dict, List, Optional, Any
from loguru import logger


class LLMClient:
    """LLM客户端 - 封装GLM 4.7 API调用"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: str = "glm-4",
        max_tokens: int = 2000,
        temperature: float = 0.7
    ):
        """初始化LLM客户端
        
        Args:
            api_key: API密钥
            api_base: API基础URL
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
        """
        self.api_key = api_key or os.getenv("GLM_API_KEY")
        self.api_base = api_base or os.getenv("GLM_API_BASE", "https://open.bigmodel.cn/api/paas/v4/")
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        if not self.api_key:
            logger.warning("GLM_API_KEY未配置，AI功能将无法使用")
        
        # HTTP客户端
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        
        logger.info(f"LLM客户端初始化完成: {model}")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """发送聊天请求
        
        Args:
            messages: 消息列表
            stream: 是否流式响应
            **kwargs: 其他参数
            
        Yields:
            响应数据
        """
        if not self.api_key:
            raise ValueError("GLM_API_KEY未配置")
        
        # 构建请求
        url = f"{self.api_base}chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "stream": stream
        }
        
        logger.info(f"发送LLM请求: {len(messages)}条消息")
        
        try:
            if stream:
                # 流式响应
                async with self.client.stream("POST", url, headers=headers, json=data) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data_str)
                                yield chunk
                            except json.JSONDecodeError:
                                continue
            else:
                # 非流式响应
                response = await self.client.post(url, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
                
                # 统计token使用
                usage = result.get("usage", {})
                if usage:
                    logger.info(f"Token使用: {usage}")
                
                yield result
        
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM请求失败: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"LLM请求错误: {e}")
            raise
        except Exception as e:
            logger.error(f"LLM调用异常: {e}")
            raise
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """聊天完成（非流式）
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数
            
        Returns:
            完整响应
        """
        async for result in self.chat(messages, stream=False, **kwargs):
            return result
        return {}
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncIterator[str]:
        """聊天流式响应
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数
            
        Yields:
            文本片段
        """
        async for chunk in self.chat(messages, stream=True, **kwargs):
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            content = delta.get("content", "")
            if content:
                yield content
    
    async def analyze(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """分析请求
        
        Args:
            prompt: 提示词
            context: 上下文数据
            **kwargs: 其他参数
            
        Returns:
            分析结果
        """
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的量化投资顾问，擅长分析股票市场和技术指标。"
            }
        ]
        
        # 添加上下文
        if context:
            context_str = json.dumps(context, ensure_ascii=False, indent=2)
            prompt = f"{prompt}\n\n上下文数据：\n{context_str}"
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        result = await self.chat_completion(messages, **kwargs)
        
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()
        logger.info("LLM客户端已关闭")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()


# 单例模式
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """获取LLM客户端单例
    
    Returns:
        LLM客户端实例
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client