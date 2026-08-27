import logging
from typing import Dict, Any, List

logger = logging.getLogger("WeatherGuard.Impact.Agri")

class AgricultureImpactEngine:
    """
    Mesin Analisis Dampak Agrometeorologi & Ketahanan Pangan
    Menerjemahkan variabel cuaca menjadi rekomendasi tanam, pemupukan, semprot, dan manajemen kekeringan (SPI).
    """

    @staticmethod
    def calculate_spi_30(precipitation_history_mm: List[float]) -> Dict[str, Any]:
        """
        Menghitung Standardized Precipitation Index 30 Hari (SPI-30) untuk klasifikasi status kekeringan.
        """
        total_precip = sum(precipitation_history_mm) if precipitation_history_mm else 120.0
        # Nilai acuan iklim normal bulanan ~150 mm
        mean_climatology = 150.0
        std_climatology = 45.0
        
        spi_val = (total_precip - mean_climatology) / std_climatology
        spi_val = max(-3.0, min(3.0, round(spi_val, 2)))
        
        if spi_val < -2.00:
            status = "Kekeringan Ekstrem"
            irrigation_advice = "🚨 DARURAT: Air tanah kritis. Tutup saluran keluar sawah, aktifkan pompa sumur dalam."
            action_code = "AGR-01"
        elif spi_val < -1.50:
            status = "Sangat Kering"
            irrigation_advice = "⚠️ TINGGI: Berlakukan irigasi bergilir 4 hari sekali. Gunakan mulsa jerami."
            action_code = "AGR-02"
        elif spi_val < -1.00:
            status = "Kering Sedang"
            irrigation_advice = "⚠️ TINGGI: Genangi sawah hanya saat fase pembungaan/malai keluar."
            action_code = "AGR-03"
        elif spi_val <= 0.99:
            status = "Normal"
            irrigation_advice = "🟢 NORMAL: Neraca air seimbang. Jalankan jadwal irigasi reguler."
            action_code = "AGR-04"
        elif spi_val <= 1.49:
            status = "Agak Basah"
            irrigation_advice = "🟡 WASPADA: Bersihkan saluran tersier agar petakan tidak tergenang lumpur asam."
            action_code = "AGR-05"
        else:
            status = "Sangat Basah (La Niña)"
            irrigation_advice = "⚠️ TINGGI: Bahaya busuk akar. Buka penuh parit pembuangan, gunakan varietas tahan genangan."
            action_code = "AGR-06"
            
        return {
            "spi_30": spi_val,
            "status": status,
            "action_code": action_code,
            "irrigation_advice": irrigation_advice
        }

    @staticmethod
    def evaluate_daily_farm_actions(day_forecast: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mengevaluasi keputusan harian petani (Semprot Pestisida, Pemupukan, Panen & Jemur, Risiko Hama).
        """
        temp = day_forecast.get("temperature_c", 30.0)
        rain_24h = day_forecast.get("rain_accum_24h_mm", 0.0)
        rain_prob = day_forecast.get("rain_probability_pct", 10)
        wind_kmh = day_forecast.get("wind_speed_kmh", 10.0)
        humidity = day_forecast.get("humidity_pct", 75)
        
        # 1. Evaluasi Jendela Semprot Pestisida/Insektisida
        if rain_24h > 15.0 or wind_kmh > 22.0 or rain_prob > 60:
            spray_status = "FORBIDDEN" # Dilarang
            spray_color = "red"
            spray_hours = "TIDAK DISARANKAN"
            spray_note = "🛑 DILARANG: Angin kencang / risiko hujan lebat mencuci obat (wash-off)."
        elif wind_kmh > 14.0:
            spray_status = "CAUTION" # Waspada
            spray_color = "yellow"
            spray_hours = "06:00 - 07:30 WIB"
            spray_note = "🟡 WASPADA: Gunakan nosel drift-reduction, semprot searah angin."
        else:
            spray_status = "OPTIMAL" # Optimal
            spray_color = "green"
            spray_hours = "06:30 - 09:00 WIB"
            spray_note = "🟢 SANGAT BAIK: Angin tenang (<12 km/j), cuaca cerah sejuk."

        # 2. Evaluasi Pemupukan Urea / NPK Tabur
        if rain_24h > 20.0:
            fert_status = "RISK_OF_WASHOFF"
            fert_color = "red"
            fert_note = "🛑 TUNDA PEMUPUKAN: Hujan lebat diprediksi (>20 mm), pupuk akan hanyut."
        elif temp > 34.0 and rain_24h == 0.0:
            fert_status = "RISK_OF_VOLATILIZATION"
            fert_color = "yellow"
            fert_note = "🟡 WASPADA: Terik panas ekstrim, pupuk urea menguap jika tanah kering."
        else:
            fert_status = "SAFE"
            fert_color = "green"
            fert_note = "🟢 AMAN MEMUPUK: Kondisi tanah lembab ideal, penyerapan hara maksimal."

        # 3. Evaluasi Panen & Jemur Gabah
        if rain_24h == 0.0 and humidity < 75:
            drying_status = "EXCELLENT"
            drying_color = "green"
            drying_note = "🟢 WAKTU EMAS PANEN & JEMUR: Pengeringan gabah optimal kadar air <14%."
        elif rain_24h < 5.0:
            drying_status = "MODERATE"
            drying_color = "yellow"
            drying_note = "🟡 JEMUR DENGAN PENGAWASAN: Siagakan terpal penutup jika awan gelap."
        else:
            drying_status = "POOR"
            drying_color = "red"
            drying_note = "🛑 JANGAN MENJEMUR: Risiko gabah basah & berkecambah di lantai jemur."

        # 4. Deteksi Dini Penyakit Jamur (Blast Padi / Hawar Daun)
        fungal_risk = "HIGH" if (humidity > 82 and 23 <= temp <= 29) else "LOW"
        fungal_note = "⚠️ ALARM JAMUR BLAST: Kelembaban tinggi memicu spora jamur. Semprot fungisida preventif." if fungal_risk == "HIGH" else "Kondisi jamur terkendali."

        return {
            "spray_window": {
                "status": spray_status,
                "color": spray_color,
                "recommended_hours": spray_hours,
                "note": spray_note
            },
            "fertilization": {
                "status": fert_status,
                "color": fert_color,
                "note": fert_note
            },
            "harvest_and_drying": {
                "status": drying_status,
                "color": drying_color,
                "note": drying_note
            },
            "fungal_disease_risk": {
                "risk_level": fungal_risk,
                "note": fungal_note
            }
        }
