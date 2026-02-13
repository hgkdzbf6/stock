"""缓存服务"""
import json
from typing import Optional, Any
import redis.asyncio as redis
from core.config import settings
from loguru import logger


class CacheService:
    """Redis缓存服务 (可选，如果Redis未配置则使用内存缓存)"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache: dict = {}  # 降级到内存缓存
        self.use_redis = False

    async def connect(self):
        """连接Redis"""
        if not settings.REDIS_URL:
            logger.info("Redis未配置，使用内存缓存")
            self.use_redis = False
            return

        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            # 测试连接
            await self.redis_client.ping()
            self.use_redis = True
            logger.info("Redis连接成功")
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}，使用内存缓存")
            self.use_redis = False

    async def disconnect(self):
        """断开Redis连接"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis连接已关闭")

    async def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        try:
            if self.use_redis and self.redis_client:
                value = await self.redis_client.get(key)
                return value
            else:
                # 从内存缓存获取
                return self.memory_cache.get(key)
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return None

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """
        设置缓存

        Args:
            key: 键
            value: 值
            expire: 过期时间（秒）
        """
        try:
            if self.use_redis and self.redis_client:
                await self.redis_client.set(key, value, ex=expire)
            else:
                # 使用内存缓存 (暂不实现过期)
                self.memory_cache[key] = value
            return True
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            if self.use_redis and self.redis_client:
                await self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False

    async def get_json(self, key: str) -> Optional[Any]:
        """获取JSON缓存"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}")
        return None

    async def set_json(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """设置JSON缓存"""
        try:
            json_str = json.dumps(value, ensure_ascii=False)
            return await self.set(key, json_str, expire)
        except Exception as e:
            logger.error(f"设置JSON缓存失败: {e}")
            return False


# 全局缓存实例
cache_service = CacheService()
