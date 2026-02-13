#!/usr/bin/env python3
"""快速启动测试脚本"""
import subprocess
import sys
import time

def check_command(cmd):
    """检查命令是否可用"""
    try:
        subprocess.run(
            cmd,
            capture_output=True,
            check=True,
            shell=True
        )
        return True
    except:
        return False

def run_tests():
    """运行测试"""
    print("=" * 60)
    print("  量化交易平台 - 快速启动测试")
    print("=" * 60)
    print()

    # 检查Python
    print("1. 检查Python环境...")
    python_version = sys.version.split()[0]
    print(f"   ✅ Python版本: {python_version}")

    # 检查依赖
    print()
    print("2. 检查核心依赖...")
    dependencies = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'pydantic-settings',
    ]

    for dep in dependencies:
        try:
            if dep == 'pydantic-settings':
                import pydantic_settings
                print(f"   ✅ {dep} ({pydantic_settings.__version__})")
            else:
                __import__(dep)
                print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} 未安装")
            print()
            print("请运行: pip install -r requirements.txt")
            return False

    # 检查配置
    print()
    print("3. 检查配置...")
    try:
        from core.config import settings
        print(f"   ✅ 配置文件加载成功")
        print(f"   APP_NAME: {settings.APP_NAME}")
        print(f"   DEBUG: {settings.DEBUG}")
    except Exception as e:
        print(f"   ❌ 配置加载失败: {e}")
        print("请确保 .env 文件存在并正确配置")
        return False

    # 检查模块导入
    print()
    print("4. 检查模块导入...")
    try:
        from core import settings, database, security
        from models import user, stock, quote, strategy
        from services import data_fetcher, market_service, cache_service
        from api import api_router
        print("   ✅ 所有模块导入成功")
    except Exception as e:
        print(f"   ❌ 模块导入失败: {e}")
        return False

    print()
    print("=" * 60)
    print("  ✅ 所有检查通过！")
    print("=" * 60)
    print()
    print("启动后端服务:")
    print("  方式1: python backend/main.py")
    print("  方式2: uvicorn backend.main:app --reload")
    print()
    print("访问地址:")
    print("  API文档: http://localhost:8000/docs")
    print("  健康检查: http://localhost:8000/health")
    print()
    return True

if __name__ == "__main__":
    import os
    import sys

    # 切换到backend目录
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)

    # 确保backend目录在Python路径中
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    success = run_tests()
    sys.exit(0 if success else 1)
