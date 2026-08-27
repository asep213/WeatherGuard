import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Boolean, Text, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from src.backend.database.db_session import Base

class Location(Base):
    """
    Tabel Master Wilayah Pantauan (Titik Sawah, Pelabuhan, Kota, atau DAS)
    """
    __tablename__ = "locations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    sector_type = Column(String(50), nullable=False) # 'AGRICULTURE', 'MARITIME', 'URBAN'
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    elevation_m = Column(Float, default=0.0)
    province = Column(String(100), nullable=True)
    regency = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class WeatherForecast(Base):
    """
    Tabel Time-Series Prediksi Cuaca Beresolusi Tinggi 5 km (TimescaleDB Hypertable)
    """
    __tablename__ = "weather_forecasts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    location_id = Column(String(36), ForeignKey("locations.id"), nullable=False, index=True)
    forecast_time = Column(DateTime, nullable=False, index=True)
    
    # Parameter Meteorologi
    temperature_c = Column(Float, nullable=False)
    temp_min_c = Column(Float, nullable=True)
    temp_max_c = Column(Float, nullable=True)
    rain_rate_mm_h = Column(Float, default=0.0)
    rain_accum_24h_mm = Column(Float, default=0.0)
    rain_probability_pct = Column(Float, default=0.0)
    humidity_pct = Column(Float, nullable=False)
    wind_speed_kmh = Column(Float, nullable=False)
    wind_gust_kmh = Column(Float, default=0.0)
    wind_direction_deg = Column(Float, default=0.0)
    uv_index = Column(Float, default=0.0)
    surface_pressure_hpa = Column(Float, default=1013.25)
    
    # Parameter Oseanografi & Maritim
    wave_height_m = Column(Float, nullable=True)
    wave_period_s = Column(Float, nullable=True)
    wave_direction_deg = Column(Float, nullable=True)
    sea_surface_temp_c = Column(Float, nullable=True)
    ocean_current_speed_ms = Column(Float, nullable=True)
    
    data_source = Column(String(50), default="AI_PRITHVI_WXC") # 'AI_PRITHVI_WXC', 'BMKG', 'OPENWEATHER'
    created_at = Column(DateTime, default=datetime.utcnow)

class EarlyWarningLog(Base):
    """
    Tabel Pencatatan Peringatan Dini Bencana (Hujan Ekstrem, Angin Kencang, Gelombang Tinggi)
    """
    __tablename__ = "early_warning_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    location_id = Column(String(36), ForeignKey("locations.id"), nullable=False, index=True)
    hazard_type = Column(String(50), nullable=False) # 'EXTREME_RAIN', 'HIGH_WIND', 'HIGH_WAVE', 'DROUGHT'
    severity = Column(String(30), nullable=False)    # 'WARNING', 'WATCH', 'ADVISORY'
    alert_level = Column(Integer, default=3)         # 1: Awas/Darurat, 2: Siaga/Bahaya, 3: Waspada
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    action_instructions = Column(Text, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    is_broadcasted = Column(Boolean, default=False)
    triggered_at = Column(DateTime, default=datetime.utcnow)

class AgriRecommendation(Base):
    """
    Tabel Rekomendasi Khusus Sektor Pertanian (Kalender Tanam, Semprot, Pupuk, SPI)
    """
    __tablename__ = "agri_recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    location_id = Column(String(36), ForeignKey("locations.id"), nullable=False, index=True)
    valid_date = Column(DateTime, nullable=False)
    spi_30_value = Column(Float, default=0.0)
    spi_status = Column(String(50), default="NORMAL")
    spray_window_status = Column(String(30), default="OPTIMAL") # 'OPTIMAL', 'CAUTION', 'FORBIDDEN'
    best_spray_hours = Column(String(50), default="06:00 - 09:00 WIB")
    fertilizer_status = Column(String(30), default="SAFE")      # 'SAFE', 'RISK_OF_WASHOFF'
    harvest_drying_status = Column(String(30), default="GOOD")
    fungal_disease_risk = Column(String(30), default="LOW")
    detailed_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class MaritimeSafetyWindow(Base):
    """
    Tabel Jendela Berlayar Aman & Zona Tangkap Nelayan
    """
    __tablename__ = "maritime_safety_windows"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    location_id = Column(String(36), ForeignKey("locations.id"), nullable=False, index=True)
    window_start = Column(DateTime, nullable=False)
    window_end = Column(DateTime, nullable=False)
    sailing_status = Column(String(30), default="SAFE") # 'SAFE', 'CAUTION', 'DANGER'
    max_wave_height_m = Column(Float, default=1.0)
    max_wind_kmh = Column(Float, default=15.0)
    potential_fishing_zone = Column(JSON, nullable=True) # GeoJSON coordinates & chlorophyll index
    recommendation_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
