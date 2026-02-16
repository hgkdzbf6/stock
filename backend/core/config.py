"""配置管理模块"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    APP_NAME: str = "Stock Platform"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # 数据源配置
    TUSHARE_TOKEN: Optional[str] = None
    DATA_SOURCE: str = "ashare"  # 'ashare'（3rdparty）, 'akshare' 或 'tushare'

    # 数据库配置
    DATABASE_URL: str
    DB_PASSWORD: str = ""

    # Redis配置 (可选)
    REDIS_URL: Optional[str] = None
    REDIS_PASSWORD: str = ""

    # JWT配置
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # AI服务配置
    GLM_API_KEY: str = ""
    GLM_API_BASE: str = "https://open.bigmodel.cn/api/paas/v4/"

    # 券商API配置
    XTP_BROKER_ID: str = ""
    XTP_ACCOUNT: str = ""
    XTP_PASSWORD: str = ""
    XTP_TRADING_SERVER: str = ""
    XTP_TRADING_PORT: int = 6000
    XTP_QUOTE_SERVER: str = ""
    XTP_QUOTE_PORT: int = 6001

    # 告警配置
    SMTP_SERVER: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    ALERT_EMAILS: List[str] = []
    WECHAT_WEBHOOK_URL: str = ""

    # Grafana配置
    GRAFANA_PASSWORD: str = ""

    # CORS配置 - 使用字符串，在应用中转换为列表
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    @field_validator("ALERT_EMAILS", mode="before")
    @classmethod
    def parse_alert_emails(cls, v):
        """解析告警邮箱配置"""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# 创建全局配置实例
settings = Settings()
