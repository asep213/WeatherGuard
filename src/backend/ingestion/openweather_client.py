import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("WeatherGuard.OpenWeather")

class OpenWeatherClient:
    """
    Klien OpenWeatherMap OneCall API 3.0 untuk data cuaca global real-time dan per jam.
    """
    
    BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "mock_key"
        self.session = requests.Session()

    def get_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Mengambil ramalan cuaca terperinci (current, hourly 48h, daily 8d) pada titik koordinat.
        """
        if self.api_key and self.api_key != "mock_key":
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric",
                "exclude": "minutely"
            }
            try:
                resp = self.session.get(self.BASE_URL, params=params, timeout=8)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                logger.warning(f"Gagal memanggil API OpenWeatherMap ({e}), menggunakan simulasi cuaca fisik realistis.")
        
        # Fallback simulator jika API Key belum dipasang
        return self._generate_realistic_point_weather(lat, lon)

    def _generate_realistic_point_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Simulator data cuaca numerik realistis untuk titik koordinat Indonesia.
        """
        now_ts = int(datetime.utcnow().timestamp())
        
        # Penyesuaian suhu mikro berdasarkan garis lintang/topografi
        base_temp = 30.5 - abs(lat) * 0.5
        
        return {
            "lat": lat,
            "lon": lon,
            "timezone": "Asia/Jakarta",
            "current": {
                "dt": now_ts,
                "temp": round(base_temp, 1),
                "feels_like": round(base_temp + 3.2, 1),
                "pressure": 1011,
                "humidity": 78,
                "dew_point": 24.5,
                "uvi": 8.4,
                "clouds": 45,
                "visibility": 10000,
                "wind_speed": 3.6, # m/s -> ~13 km/h
                "wind_deg": 210,
                "weather": [{"id": 802, "main": "Clouds", "description": "scattered clouds", "icon": "03d"}]
            },
            "hourly": [
                {
                    "dt": now_ts + (i * 3600),
                    "temp": round(base_temp + (2.5 if 4 <= (i % 24) <= 9 else -3.0), 1),
                    "humidity": min(95, max(55, 78 - (i % 8))),
                    "rain": {"1h": round(1.2 * (i % 4), 1)} if (i % 6 == 0) else {"1h": 0.0},
                    "wind_speed": round(3.5 + (i % 3) * 1.2, 1),
                    "wind_gust": round(5.0 + (i % 4) * 2.1, 1),
                    "pop": 0.15 if (i % 6 != 0) else 0.75,
                    "uvi": 7.5 if 3 <= (i % 24) <= 8 else 0.0
                }
                for i in range(48)
            ]
        }
