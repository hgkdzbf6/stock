"""数据库连接模块"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.config import settings

# 从settings中获取数据库URL
DATABASE_URL = settings.DATABASE_URL

# 检测数据库类型并选择合适的驱动
if 'postgresql' in DATABASE_URL:
    try:
        import asyncpg
        print(f"✅ 使用PostgreSQL数据库")
    except ImportError:
        print("⚠️  asyncpg未安装，降级到SQLite")
        DATABASE_URL = 'sqlite+aiosqlite:///./stock.db'
elif 'mysql' in DATABASE_URL:
    try:
        import aiomysql
        print(f"✅ 使用MySQL数据库")
    except ImportError:
        print("⚠️  aiomysql未安装，降级到SQLite")
        DATABASE_URL = 'sqlite+aiosqlite:///./stock.db'
else:
    # 默认使用SQLite
    print(f"✅ 使用SQLite数据库")

# 创建异步引擎
pool_kwargs = {}
if 'postgresql' in DATABASE_URL:
    pool_kwargs = {
        'pool_size': 10,
        'max_overflow': 20
    }

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    **pool_kwargs
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# 创建基类
Base = declarative_base()


async def get_db() -> AsyncSession:
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化数据库"""
    try:
        async with engine.begin() as conn:
            # 导入所有模型以确保它们被注册
            from models import user, stock, quote, strategy  # noqa: F401

            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
            
        print(f"✅ 数据库初始化成功: {DATABASE_URL}")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        raise
