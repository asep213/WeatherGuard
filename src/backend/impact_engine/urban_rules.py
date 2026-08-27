import logging
from typing import Dict, Any, List

logger = logging.getLogger("WeatherGuard.Impact.Urban")

class UrbanImpactEngine:
    """
    Mesin Analisis Dampak Perkotaan & Sistem Peringatan Dini Bencana BPBD (Early Warning System)
    Mendeteksi ambang batas hujan ekstrem (>50 mm/hari), angin kencang (>60 km/jam), dan bahaya genangan/UHI.
    """

    @staticmethod
    def evaluate_urban_hazards(forecast_7d: List[Dict[str, Any]], location_name: str = "DKI Jakarta") -> List[Dict[str, Any]]:
        """
        Memindai ramalan cuaca 7 hari untuk memicu Early Warning Bencana Hidrometeorologi.
        """
        active_alerts = []
        
        for idx, day in enumerate(forecast_7d):
            date_str = day.get("date")
            rain_24h = day.get("rain_accum_24h_mm", 0.0)
            wind_gust = day.get("wind_gust_kmh", 0.0)
            uv_index = day.get("uv_index", 5.0)
            temp_max = day.get("temp_max_c", 32.0)
            
            # 1. Peringatan Hujan Ekstrem (>50 mm / >100 mm)
            if rain_24h >= 100.0:
                active_alerts.append({
                    "alert_id": f"ALERT-RAIN-100-{idx}",
                    "date": date_str,
                    "hazard_type": "EXTREME_RAIN",
                    "severity": "WARNING",
                    "alert_level": 1,
                    "level_text": "🚨 SIAGA 1 (AWAS / DARURAT)",
                    "title": f"PERINGATAN DINI HUJAN EKSTREM ({rain_24h} mm/hari)",
                    "location": location_name,
                    "description": f"Potensi banjir bandang perkotaan dan luapan DAS skala besar pada {date_str}.",
                    "action_instructions": "Bunyikan sirine peringatan dini. Buka seluruh pintu air pengendali. Evakuasi segera warga bantaran kali.",
                    "target_sector": "BPBD, Dinas SDA, Camat/Lurah",
                    "rule_id": "URB-03"
                })
            elif rain_24h >= 50.0:
                active_alerts.append({
                    "alert_id": f"ALERT-RAIN-50-{idx}",
                    "date": date_str,
                    "hazard_type": "HEAVY_RAIN",
                    "severity": "WATCH",
                    "alert_level": 2,
                    "level_text": "🛑 SIAGA 2 (BAHAYA GENANGAN)",
                    "title": f"PERINGATAN HUJAN LEBAT ({rain_24h} mm/hari)",
                    "location": location_name,
                    "description": f"Kapasitas drainase perkotaan terlampaui; potensi genangan 30-60 cm pada {date_str}.",
                    "action_instructions": "Siagakan pompa mobile cekungan. Imbau pengguna jalan hindari jalur rawan genangan.",
                    "target_sector": "BPBD, Dishub, Bina Marga",
                    "rule_id": "URB-02"
                })

            # 2. Peringatan Angin Kencang (>60 km/jam)
            if wind_gust >= 60.0:
                active_alerts.append({
                    "alert_id": f"ALERT-WIND-60-{idx}",
                    "date": date_str,
                    "hazard_type": "HIGH_WIND",
                    "severity": "WARNING",
                    "alert_level": 1,
                    "level_text": "🚨 ANGIN KENCANG EKSTREM (>60 km/jam)",
                    "title": f"PERINGATAN HEMBUSAN ANGIN KENCANG ({wind_gust} km/jam)",
                    "location": location_name,
                    "description": f"Potensi pohon tumbang masif, papan baliho roboh, gangguan penerbangan rendah pada {date_str}.",
                    "action_instructions": "Hentikan crane proyek tinggi. Amankan atap seng. Pangkas pohon rawan tumbang.",
                    "target_sector": "Dinas Pertamanan, PLN, Bandara",
                    "rule_id": "URB-05"
                })

            # 3. Peringatan Indeks UV Ekstrem (UV Index >= 11)
            if uv_index >= 11.0:
                active_alerts.append({
                    "alert_id": f"ALERT-UV-11-{idx}",
                    "date": date_str,
                    "hazard_type": "EXTREME_UV",
                    "severity": "ADVISORY",
                    "alert_level": 3,
                    "level_text": "⚠️ WASPADA SINAR UV EKSTREM",
                    "title": f"PERINGATAN INDEKS RADIASI UV TINGGI ({uv_index})",
                    "location": location_name,
                    "description": f"Paparan langsung sinar matahari tengah hari dapat membakar kulit dalam <15 menit.",
                    "action_instructions": "Gunakan pelindung tabir surya SPF 30+ dan topi/payung saat beraktivitas luar.",
                    "target_sector": "Dinas Kesehatan, Publik",
                    "rule_id": "URB-08"
                })

        return active_alerts
