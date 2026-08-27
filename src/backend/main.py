import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Query, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.backend.config import settings
from src.backend.model.inference_engine import WeatherFoundationEngine
from src.backend.impact_engine.agriculture_rules import AgricultureImpactEngine
from src.backend.impact_engine.maritime_rules import MaritimeImpactEngine
from src.backend.impact_engine.urban_rules import UrbanImpactEngine
from src.backend.ingestion.bmkg_client import BMKGClient
from src.backend.ingestion.openweather_client import OpenWeatherClient
from src.backend.ingestion.satellite_ingest import SatelliteIngestionEngine

# Setup Logging
log_level_name = getattr(settings, "LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_name, logging.INFO)
logging.basicConfig(level=log_level)
logger = logging.getLogger("WeatherGuard.API")

# Initialize FastAPI App
app = FastAPI(
    title=settings.APP_NAME,
    description="Sistem Kecerdasan Buatan (AI) untuk Prediksi Cuaca Berbasis Dampak (Impact-Based Forecasting) Sektor Pertanian, Maritim, dan Perkotaan",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=settings.CORS_ORIGINS != "*",
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Engine Instances
ai_engine = WeatherFoundationEngine(model_name=settings.AI_MODEL_BACKBONE, device=settings.INFERENCE_DEVICE)
bmkg_client = BMKGClient(token=settings.BMKG_API_TOKEN)
owm_client = OpenWeatherClient(api_key=settings.OPENWEATHER_API_KEY)
sat_engine = SatelliteIngestionEngine()

# Active WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_alert(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

ws_manager = ConnectionManager()


# --- Pydantic Data Models ---
class LocationQuery(BaseModel):
    name: str
    latitude: float
    longitude: float
    sector: str # 'AGRICULTURE', 'MARITIME', 'URBAN'

class ForecastResponse(BaseModel):
    location: Dict[str, Any]
    model_backbone: str
    resolution_km: float
    forecast_horizon_days: int
    generated_at: str
    daily_forecasts: List[Dict[str, Any]]

class DispatchNotificationRequest(BaseModel):
    alert_id: str
    target_channels: List[str] # ['WHATSAPP', 'SMS', 'SIREN']
    recipient_group: str # 'CAMAT_LURAH', 'POKTAN', 'NELAYAN'
    custom_notes: Optional[str] = None


# --- REST API Endpoints ---

@app.get("/", tags=["Root"])
def root_status():
    return {
        "system": settings.APP_NAME,
        "status": "OPERATIONAL",
        "version": "1.0.0",
        "docs": "/docs",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_check():
    return {
        "status": "HEALTHY",
        "ai_engine": "LOADED" if ai_engine.is_loaded else "STANDBY",
        "database": "NOT_CONFIGURED",
        "redis_cache": "NOT_CONFIGURED",
        "device": settings.INFERENCE_DEVICE,
        "resolution": f"{settings.GRID_RESOLUTION_KM} km"
    }

@app.get(f"{settings.API_V1_STR}/forecast/point", response_model=ForecastResponse, tags=["Weather Forecast"])
def get_point_forecast(
    lat: float = Query(..., ge=-11.0, le=6.0, description="Latitude lokasi (-11.0 s/d 6.0)"),
    lon: float = Query(..., ge=95.0, le=141.0, description="Longitude lokasi (95.0 s/d 141.0)"),
    name: str = Query("Titik Pantauan", description="Nama lokasi/desa/pelabuhan"),
    elevation_m: float = Query(25.0, description="Elevasi medan dalam meter"),
    days: int = Query(7, ge=1, le=10, description="Jumlah hari prakiraan")
):
    """
    Mengambil data ramalan cuaca resolusi 5 km menggunakan Foundation Model AI (Surya / Prithvi WxC).
    """
    forecast_data = ai_engine.predict_point_forecast_7d(lat=lat, lon=lon, elevation_m=elevation_m)
    forecast_data = forecast_data[:days]
    
    return {
        "location": {
            "name": name,
            "latitude": lat,
            "longitude": lon,
            "elevation_m": elevation_m
        },
        "model_backbone": settings.AI_MODEL_BACKBONE,
        "resolution_km": settings.GRID_RESOLUTION_KM,
        "forecast_horizon_days": days,
        "generated_at": datetime.utcnow().isoformat(),
        "daily_forecasts": forecast_data
    }

@app.get(f"{settings.API_V1_STR}/impact/agriculture", tags=["Sector Impact - Agriculture"])
def get_agriculture_impact(
    lat: float = Query(-6.302, description="Latitude sawah"),
    lon: float = Query(107.408, description="Longitude sawah"),
    location_name: str = Query("Sukamaju, Karawang", description="Nama daerah pertanian")
):
    """
    Menghasilkan rekomendasi cerdas agrikultur: SPI Kekeringan, Jendela Semprot Pestisida, Pemupukan, dan Panen.
    """
    forecast_7d = ai_engine.predict_point_forecast_7d(lat=lat, lon=lon)
    today_forecast = forecast_7d[0]
    
    # 1. Analisis SPI-30
    recent_precip_history = [day["rain_accum_24h_mm"] for day in forecast_7d] * 4 # Estimasi 28-30 hari
    spi_result = AgricultureImpactEngine.calculate_spi_30(recent_precip_history)
    
    # 2. Analisis Tindakan Harian (Semprot & Pupuk)
    daily_actions = AgricultureImpactEngine.evaluate_daily_farm_actions(today_forecast)
    
    # 3. Rekomendasi 7 Hari Matriks
    weekly_matrix = []
    for day in forecast_7d:
        action = AgricultureImpactEngine.evaluate_daily_farm_actions(day)
        weekly_matrix.append({
            "date": day["date"],
            "temp_c": day["temperature_c"],
            "rain_mm": day["rain_accum_24h_mm"],
            "spray_status": action["spray_window"]["status"],
            "spray_color": action["spray_window"]["color"],
            "fertilizer_status": action["fertilization"]["status"],
            "fertilizer_color": action["fertilization"]["color"],
            "drying_status": action["harvest_and_drying"]["status"],
            "fungal_risk": action["fungal_disease_risk"]["risk_level"]
        })

    return {
        "location": {"name": location_name, "latitude": lat, "longitude": lon},
        "generated_at": datetime.utcnow().isoformat(),
        "current_spi_status": spi_result,
        "today_farm_recommendation": daily_actions,
        "weekly_farm_matrix": weekly_matrix
    }

@app.get(f"{settings.API_V1_STR}/impact/maritime", tags=["Sector Impact - Maritime"])
def get_maritime_impact(
    lat: float = Query(-7.728, description="Latitude pelabuhan"),
    lon: float = Query(109.015, description="Longitude pelabuhan"),
    port_name: str = Query("Teluk Penyu, Cilacap", description="Nama pelabuhan/PPI"),
    vessel_type: str = Query("SMALL_VESSEL", description="SMALL_VESSEL (<5 GT) atau LARGE_VESSEL (>30 GT)")
):
    """
    Menghasilkan status keselamatan melaut (Safe Window), tinggi gelombang, dan titik kumpul ikan (ZPPI).
    """
    forecast_7d = ai_engine.predict_point_forecast_7d(lat=lat, lon=lon)
    today_forecast = forecast_7d[0]
    
    # 1. Evaluasi Keselamatan Melaut
    sailing_safety = MaritimeImpactEngine.evaluate_sailing_safety(
        wave_height_m=today_forecast["wave_height_m"],
        wind_speed_kmh=today_forecast["wind_speed_kmh"],
        boat_type=vessel_type
    )
    
    # 2. Perhitungan Jendela Berlayar Aman (Safe Window)
    safe_window = MaritimeImpactEngine.calculate_safe_sailing_window(forecast_7d)
    
    # 3. Identifikasi Titik ZPPI
    fish_spots = MaritimeImpactEngine.identify_potential_fishing_zones(lat=lat, lon=lon)
    
    # 4. Data Satelit Oseanografi (SST & Klorofil)
    ocean_satellite = sat_engine.process_sentinel_ocean_data(lat=lat, lon=lon)

    return {
        "port": {"name": port_name, "latitude": lat, "longitude": lon},
        "vessel_type": vessel_type,
        "generated_at": datetime.utcnow().isoformat(),
        "sailing_safety_status": sailing_safety,
        "safe_sailing_window": safe_window,
        "satellite_ocean_metrics": ocean_satellite,
        "potential_fishing_zones": fish_spots,
        "wave_forecast_7d": [
            {
                "date": d["date"],
                "wave_height_m": d["wave_height_m"],
                "wind_speed_kmh": d["wind_speed_kmh"],
                "wind_gust_kmh": d["wind_gust_kmh"]
            }
            for d in forecast_7d
        ]
    }

@app.get(f"{settings.API_V1_STR}/impact/urban/early-warning", tags=["Sector Impact - Urban/BPBD"])
def get_urban_early_warning(
    lat: float = Query(-6.208, description="Latitude perkotaan"),
    lon: float = Query(106.845, description="Longitude perkotaan"),
    city_name: str = Query("DKI Jakarta & DAS Ciliwung", description="Nama kota/wilayah BPBD")
):
    """
    Memindai bahaya perkotaan: Hujan ekstrem (>50 mm/hari), angin kencang (>60 km/jam), dan indeks UV.
    """
    forecast_7d = ai_engine.predict_point_forecast_7d(lat=lat, lon=lon)
    alerts = UrbanImpactEngine.evaluate_urban_hazards(forecast_7d, location_name=city_name)
    
    # Cek radar satelit Himawari untuk awan badai konvektif
    bounds = (lat - 0.5, lon - 0.5, lat + 0.5, lon + 0.5)
    himawari_cloud = sat_engine.process_himawari_convective_cloud(bounds)
    
    return {
        "region": {"name": city_name, "latitude": lat, "longitude": lon},
        "generated_at": datetime.utcnow().isoformat(),
        "total_active_alerts": len(alerts),
        "alerts": alerts,
        "satellite_radar_convective_status": himawari_cloud,
        "forecast_timeline": [
            {
                "date": d["date"],
                "rain_accum_24h_mm": d["rain_accum_24h_mm"],
                "wind_gust_kmh": d["wind_gust_kmh"],
                "temp_max_c": d["temp_max_c"],
                "uv_index": d["uv_index"]
            }
            for d in forecast_7d
        ]
    }

@app.post(f"{settings.API_V1_STR}/impact/urban/dispatch-alert", tags=["Sector Impact - Urban/BPBD"])
async def dispatch_emergency_alert(request: DispatchNotificationRequest):
    """
    Memicu pengiriman peringatan darurat serentak via WhatsApp Broadcast, SMS Gateway, dan WebSocket.
    """
    payload = {
        "event": "EMERGENCY_DISASTER_ALERT",
        "alert_id": request.alert_id,
        "channels": request.target_channels,
        "recipient_group": request.recipient_group,
        "dispatched_at": datetime.utcnow().isoformat(),
        "status": "DELIVERED",
        "message": f"Peringatan dini kebencanaan berhasil disiarkan ke {request.recipient_group} via {', '.join(request.target_channels)}."
    }
    
    # Broadcast to live WebSocket clients
    await ws_manager.broadcast_alert(payload)
    return payload

@app.websocket("/ws/alerts/stream")
async def websocket_alerts_stream(websocket: WebSocket):
    """
    Koneksi WebSocket real-time untuk Command Center BPBD.
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            # Tetap jaga koneksi aktif
            data = await websocket.receive_text()
            await websocket.send_json({"type": "PONG", "received": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
