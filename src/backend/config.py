import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "WeatherGuard AI"
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me-in-production"
    LOG_LEVEL: str = "INFO"
    API_V1_STR: str = "/api/v1"
    
    # Server Ports
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 8501
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://weatherguard_admin:WeatherGuardSecure2026!@localhost:5432/weatherguard_db"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # External APIs
    OPENWEATHER_API_KEY: Optional[str] = os.getenv("OPENWEATHER_API_KEY", "")
    BMKG_API_TOKEN: Optional[str] = os.getenv("BMKG_API_TOKEN", "")
    NASA_EARTHDATA_TOKEN: Optional[str] = os.getenv("NASA_EARTHDATA_TOKEN", "")
    
    # AI Engine Settings
    INFERENCE_DEVICE: str = os.getenv("INFERENCE_DEVICE", "cpu")
    AI_MODEL_BACKBONE: str = os.getenv("AI_MODEL_BACKBONE", "PRITHVI_WXC_SURYA")
    GRID_RESOLUTION_KM: float = float(os.getenv("GRID_RESOLUTION_KM", "5.0"))
    FORECAST_HORIZON_DAYS: int = int(os.getenv("FORECAST_HORIZON_DAYS", "7"))
    
    # Thresholds
    EXTREME_RAIN_DAILY_THRESHOLD_MM: float = 50.0
    EXTREME_WIND_GUST_THRESHOLD_KMH: float = 60.0
    HIGH_WAVE_THRESHOLD_METER: float = 2.5
    CORS_ORIGINS: str = "*"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

