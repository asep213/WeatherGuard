from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import logging
from src.backend.config import settings

logger = logging.getLogger("WeatherGuard.DB")

try:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    logger.warning(f"Database connection setup fallback (using in-memory SQLite if PostgreSQL unreachable): {e}")
    engine = create_engine("sqlite:///./weatherguard_fallback.db", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
