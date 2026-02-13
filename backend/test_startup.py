#!/usr/bin/env python3
"""测试后端启动"""
import sys
import asyncio

async def test_startup():
    """测试启动流程"""
    print("=" * 60)
    print("  测试后端启动流程")
    print("=" * 60)
    print()

    try:
        # 1. 测试配置加载
        print("1. 测试配置加载...")
        from core.config import settings
        print(f"   ✅ APP_NAME: {settings.APP_NAME}")
        print(f"   ✅ DEBUG: {settings.DEBUG}")
        print(f"   ✅ DATABASE_URL: {settings.DATABASE_URL}")
        print()

        # 2. 测试数据库连接
        print("2. 测试数据库连接...")
        from core.database import init_db
        await init_db()
        print()

        # 3. 测试缓存服务
        print("3. 测试缓存服务...")
        from services.cache_service import cache_service
        await cache_service.connect()
        print(f"   ✅ 缓存服务: {'Redis' if cache_service.use_redis else '内存缓存'}")
        print()

        # 4. 测试API导入
        print("4. 测试API模块...")
        from api import api_router
        print("   ✅ API路由导入成功")
        print()

        print("=" * 60)
        print("  ✅ 所有测试通过！后端可以启动")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_startup())
    sys.exit(0 if success else 1)
