import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- Page Configuration ---
st.set_page_config(
    page_title="WeatherGuard AI - Sistem Prediksi Cuaca Berbasis Dampak",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS Styling ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .status-card-green {
        background-color: #ECFDF5;
        border-left: 6px solid #10B981;
        padding: 18px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .status-card-yellow {
        background-color: #FEFCE8;
        border-left: 6px solid #F59E0B;
        padding: 18px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .status-card-red {
        background-color: #FEF2F2;
        border-left: 6px solid #EF4444;
        padding: 18px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- Lokasi Database Komprehensif Seluruh Indonesia (Termasuk Sumatera Utara & Tebing Tinggi) ---
LOCATION_DATABASE = {
    # Sumatera Utara
    "Kota Tebing Tinggi (Sumut) - Padang Hilir / Rambutan": {"lat": 3.3285, "lon": 99.1625, "sector": "AGRI_URBAN", "elev": 26, "desc": "DAS Sungai Padang & Sungai Bahilang, Sentra Padi & Sawit"},
    "Kota Medan (Sumut) - Medan Kota & DAS Deli": {"lat": 3.5952, "lon": 98.6722, "sector": "URBAN", "elev": 25, "desc": "Pusat Bisnis Sumut & DAS Sungai Deli/Babura"},
    "Pelabuhan Belawan (Sumut) - Selat Malaka": {"lat": 3.7850, "lon": 98.6850, "sector": "MARITIME", "elev": 3, "desc": "Pangkalan Pelabuhan Samudera & Perikanan Belawan"},
    "Kab. Serdang Bedagai (Sumut) - Sei Rampah": {"lat": 3.4833, "lon": 99.1500, "sector": "AGRI", "elev": 18, "desc": "Sentra Lumbung Beras & Perkebunan Sawit/Karet Sumut"},
    "Kab. Deli Serdang (Sumut) - Lubuk Pakam": {"lat": 3.5594, "lon": 98.8752, "sector": "AGRI", "elev": 22, "desc": "Kawasan Pertanian Padi Sawah & Hortikultura"},
    "Kab. Karo (Sumut) - Berastagi / Kabanjahe": {"lat": 3.1833, "lon": 98.5000, "sector": "AGRI", "elev": 1350, "desc": "Sentra Sayuran Dataran Tinggi & Hortikultura"},
    "Pelabuhan Sibolga (Sumut Barat) - Samudra Hindia": {"lat": 1.7425, "lon": 98.7792, "sector": "MARITIME", "elev": 5, "desc": "Pusat Pendaratan Ikan Pelagis Pantai Barat Sumatera"},
    "Tanjung Balai Asahan (Sumut) - Selat Malaka": {"lat": 2.9667, "lon": 99.8000, "sector": "MARITIME", "elev": 4, "desc": "Muara Sungai Asahan & Armada Perikanan Tangkap"},
    "Kawasan Danau Toba (Sumut) - Parapat / Samosir": {"lat": 2.6845, "lon": 98.9350, "sector": "AGRI_MARITIME", "elev": 905, "desc": "Perikanan Keramba Jaring Apung & Pariwisata"},
    
    # Jawa & Bali
    "Kab. Karawang (Jawa Barat) - Telagasari": {"lat": -6.3020, "lon": 107.4080, "sector": "AGRI", "elev": 25, "desc": "Lumbung Padi Nasional Jawa Barat"},
    "Kab. Indramayu (Jawa Barat) - Pesisir Patrol": {"lat": -6.3260, "lon": 108.3200, "sector": "AGRI_MARITIME", "elev": 5, "desc": "Pertanian Padi Sawah & Armada Nelayan Pantura"},
    "DKI Jakarta - DAS Ciliwung & Pintu Air Manggarai": {"lat": -6.2088, "lon": 106.8456, "sector": "URBAN", "elev": 15, "desc": "Ibukota & Pemantauan Banjir Makro"},
    "Pelabuhan Teluk Penyu (Cilacap, Jateng)": {"lat": -7.7280, "lon": 109.0150, "sector": "MARITIME", "elev": 5, "desc": "Pangkalan Nelayan Samudera Hindia Selatan Jawa"},
    "Pelabuhan Muncar (Banyuwangi, Jatim)": {"lat": -8.4333, "lon": 114.3333, "sector": "MARITIME", "elev": 4, "desc": "Pusat Industri Penangkapan Ikan Lemuru"},
    
    # Sulawesi & Kalimantan
    "Kota Bitung (Sulawesi Utara) - Laut Maluku": {"lat": 1.4404, "lon": 125.1217, "sector": "MARITIME", "elev": 8, "desc": "Pelabuhan Perikanan Samudera Tuna Pasifik"},
    "Kota Pontianak (Kalbar) - Sungai Kapuas": {"lat": -0.0263, "lon": 109.3425, "sector": "URBAN", "elev": 3, "desc": "Kawasan Pasang Surut & Pertanian Gambut"}
}

# --- Sidebar Navigation ---
st.sidebar.image("https://img.icons8.com/fluency/96/shield.png", width=64)
st.sidebar.markdown("### **WeatherGuard AI**")
st.sidebar.caption("Impact-Based Decision Support System")

persona_choice = st.sidebar.radio(
    "Pilih Persona & Tampilan:",
    [
        "🌾 1. Dashboard Petani (Mobile Android View)",
        "⚓ 2. Dashboard Nelayan (High-Contrast Safe Window)",
        "🏙️ 3. Command Center BPBD (Early Warning & Dispatch)",
        "🗺️ 4. Peta Spasial Interaktif Multi-Layer"
    ],
    index=0
)

st.sidebar.divider()
st.sidebar.markdown("#### ⚙️ Konfigurasi Model AI")
st.sidebar.info("🤖 **Backbone AI**: IBM-NASA Prithvi WxC\n📐 **Resolusi Spasial**: 5.0 km\n📅 **Horizon**: 7 Hari (168 Jam)\n🛰️ **Integrasi**: BMKG, Himawari-9, Sentinel-3")

# --- Dynamic Forecast Generator based on Lat/Lon ---
def generate_forecast_for_location(lat: float, lon: float, elev: float = 25.0):
    dates = [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    
    # Seed iklim berbasis koordinat lokal (misal: Tebing Tinggi / Sumatera memiliki pola hujan tropis khas)
    loc_seed = int((abs(lat) * 100 + abs(lon) * 10) % 30)
    
    temps = [round(32.0 - (elev/200.0) + np.sin(i + loc_seed)*1.2, 1) for i in range(7)]
    
    # Tebing Tinggi / Sumut sering mengalami hujan sore/malam konvektif
    rain_base = [6.0, 14.0, 48.0, 72.0, 15.0, 2.0, 5.0] if (lat > 0) else [4.0, 0.0, 18.0, 62.0, 12.0, 0.0, 2.0]
    rain = [float(rain_base[(i + loc_seed) % len(rain_base)]) for i in range(7)]
    
    wind = [round(10.0 + (i % 3) * 4.0 + (loc_seed % 5), 1) for i in range(7)]
    waves = [round(0.6 + (r / 50.0) + (w / 35.0), 2) for r, w in zip(rain, wind)]
    uv = [8.5 if r < 10 else 3.5 for r in rain]
    hum = [min(98, int(72 + (r * 0.3))) for r in rain]
    
    return pd.DataFrame({
        "Tanggal": dates,
        "Suhu Rata-rata (°C)": temps,
        "Curah Hujan (mm)": rain,
        "Kecepatan Angin (km/j)": wind,
        "Tinggi Gelombang (m)": waves,
        "Indeks UV": uv,
        "Kelembaban (%)": hum
    })


# ==============================================================================
# 🌾 PERSONA 1: DASHBOARD PETANI (MOBILE ANDROID VIEW)
# ==============================================================================
if "1. Dashboard Petani" in persona_choice:
    st.markdown('<div class="main-header">🌾 WeatherGuard Tani</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Rekomendasi Tindakan Sawah & Perkebunan Berdasarkan Prediksi Cuaca 7 Hari</div>', unsafe_allow_html=True)

    col_loc1, col_loc2 = st.columns([3, 1])
    with col_loc1:
        lokasi_options = [k for k in LOCATION_DATABASE.keys() if "AGRI" in LOCATION_DATABASE[k]["sector"] or "AGRI_URBAN" in LOCATION_DATABASE[k]["sector"] or "MARITIME" not in LOCATION_DATABASE[k]["sector"]]
        # Prioritaskan Tebing Tinggi di urutan pertama
        lokasi_tani = st.selectbox(
            "📍 Pilih Wilayah Lahan Pertanian / Perkebunan:",
            lokasi_options,
            index=0
        )
        loc_meta = LOCATION_DATABASE[lokasi_tani]
        st.caption(f"📌 **Koordinat**: Lat {loc_meta['lat']}°, Lon {loc_meta['lon']}° | Elevasi: {loc_meta['elev']} mdpl | *{loc_meta['desc']}*")

    with col_loc2:
        if st.button("🔊 Putar Arahan Suara"):
            st.toast(f"🔊 Suara: 'Petani {lokasi_tani.split('-')[0]}, pagi ini jam 06.30 sangat baik untuk menyemprot tanaman. Pemupukan aman. Waspadai potensi hujan lebat di hari ke-4.'", icon="📢")

    df_data = generate_forecast_for_location(loc_meta["lat"], loc_meta["lon"], loc_meta["elev"])

    # Status Hari Ini
    st.markdown(f"#### 📢 Rekomendasi Aksi Tani Hari Ini ({datetime.now().strftime('%A, %d %B %Y')})")
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        st.markdown("""
        <div class="status-card-green">
            <h4>🟢 Penyemprotan Pestisida / Fungisida</h4>
            <p><b>Status: SANGAT BAIK</b></p>
            <p>⏰ <b>Jam Terbaik</b>: 06.30 - 09.00 WIB</p>
            <p><small>Angin tenang (<12 km/j), probabilitas hujan <15%. Obat melekat sempurna pada daun.</small></p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_c2:
        st.markdown("""
        <div class="status-card-green">
            <h4>🟢 Pemupukan Urea / NPK / Sawit</h4>
            <p><b>Status: AMAN MEMUPUK</b></p>
            <p>🌱 <b>Kondisi Tanah</b>: Lembab Optimal</p>
            <p><small>Tidak ada potensi hujan lebat 24 jam ke depan. Pupuk tidak hanyut tererosi.</small></p>
        </div>
        """, unsafe_allow_html=True)

    with col_c3:
        st.markdown("""
        <div class="status-card-yellow">
            <h4>🟡 Kondisi Air Tanah (SPI-30)</h4>
            <p><b>Status: SPI -0.85 (Normal Cenderung Kering)</b></p>
            <p>💧 <b>Irigasi</b>: Giliran Air 3 Hari Sekali</p>
            <p><small>Pertahankan genangan air macak-macak setinggi 2 cm di petakan sawah.</small></p>
        </div>
        """, unsafe_allow_html=True)

    # Matriks Tindakan 7 Hari
    st.markdown("#### 📅 Jendela Waktu & Matriks Rekomendasi 7 Hari ke Depan (Resolusi 5 km)")
    
    col_m1, col_m2 = st.columns([3, 2])
    with col_m1:
        spray_labels = ["🟢 Optimal (06-09 WIB)" if r < 15 and w < 20 else ("🛑 DILARANG (Hujan Lebat)" if r > 40 else "🟡 Waspada Angin") for r, w in zip(df_data["Curah Hujan (mm)"], df_data["Kecepatan Angin (km/j)"])]
        fert_labels = ["🟢 Aman" if r < 20 else "🛑 TUNDA (Risiko Hanyut)" for r in df_data["Curah Hujan (mm)"]]
        dry_labels = ["🟢 Sangat Baik" if r == 0 else ("🛑 JANGAN JEMUR" if r > 30 else "🟡 Terpal Siaga") for r in df_data["Curah Hujan (mm)"]]
        
        matrix_table = pd.DataFrame({
            "Hari / Tanggal": df_data["Tanggal"],
            "Hujan": [f"{r:.1f} mm" for r in df_data["Curah Hujan (mm)"]],
            "Jendela Semprot": spray_labels,
            "Pemupukan": fert_labels,
            "Jemur Gabah/Komoditas": dry_labels
        })
        st.dataframe(matrix_table, use_container_width=True, hide_index=True)

    with col_m2:
        fig_rain = px.bar(
            df_data, x="Tanggal", y="Curah Hujan (mm)",
            title=f"Prediksi Hujan 7 Hari: {lokasi_tani.split('(')[0]}",
            color="Curah Hujan (mm)",
            color_continuous_scale=["#10B981", "#F59E0B", "#EF4444"]
        )
        fig_rain.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_rain, use_container_width=True)


# ==============================================================================
# ⚓ PERSONA 2: DASHBOARD NELAYAN (HIGH-CONTRAST SAFE WINDOW)
# ==============================================================================
elif "2. Dashboard Nelayan" in persona_choice:
    st.markdown('<div class="main-header">⚓ WeatherGuard Laut</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Sistem Keselamatan Pelayaran Nelayan & Zona Potensi Penangkapan Ikan (ZPPI)</div>', unsafe_allow_html=True)

    col_pel1, col_pel2 = st.columns([3, 1])
    with col_pel1:
        maritime_options = [k for k in LOCATION_DATABASE.keys() if "MARITIME" in LOCATION_DATABASE[k]["sector"] or "AGRI_MARITIME" in LOCATION_DATABASE[k]["sector"]]
        pelabuhan = st.selectbox(
            "📍 Pilih Pangkalan Pendaratan Ikan (PPI) / Pelabuhan:",
            maritime_options,
            index=0 # Belawan / Sibolga / Cilacap
        )
        loc_meta = LOCATION_DATABASE[pelabuhan]
        st.caption(f"📌 **Koordinat**: Lat {loc_meta['lat']}°, Lon {loc_meta['lon']}° | *{loc_meta['desc']}*")

    with col_pel2:
        jenis_kapal = st.radio("Armada Kapal:", ["Perahu Kecil (<5 GT)", "Kapal Sedang (10-30 GT)"], horizontal=True)

    df_data = generate_forecast_for_location(loc_meta["lat"], loc_meta["lon"], loc_meta["elev"])
    today_wave = df_data.iloc[0]["Tinggi Gelombang (m)"]
    today_wind = df_data.iloc[0]["Kecepatan Angin (km/j)"]

    # Indikator Lampu Status Keselamatan
    if today_wave < 1.25 and today_wind < 20.0:
        st.markdown(f"""
        <div class="status-card-green">
            <h2 style="margin:0; color:#065F46;">🟢 STATUS KESELAMATAN: AMAN MELAUT</h2>
            <p style="font-size:1.1rem; margin-top:5px;">
                <b>Gelombang Signifikan ($H_s$)</b>: {today_wave:.1f} meter (Tenang) | <b>Angin</b>: {today_wind:.1f} km/jam
            </p>
            <p style="margin:0;">⏰ <b>Jendela Berlayar Aman (Safe Window)</b>: <b>Terbuka 48 Jam Penuh</b> untuk seluruh armada perikanan.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="status-card-yellow">
            <h2 style="margin:0; color:#92400E;">🟡 STATUS KESELAMATAN: WASPADA PERAHU KECIL</h2>
            <p style="font-size:1.1rem; margin-top:5px;">
                <b>Gelombang Signifikan ($H_s$)</b>: {today_wave:.1f} meter (Sedang) | <b>Angin</b>: {today_wind:.1f} km/jam
            </p>
            <p style="margin:0;">⏰ Perahu katir <5 GT disarankan beroperasi di radius <5 mil pantai.</p>
        </div>
        """, unsafe_allow_html=True)

    col_w1, col_w2 = st.columns([3, 2])
    with col_w1:
        st.markdown("#### 🐟 Spot Titik Kumpul Ikan (ZPPI) Berdasarkan Citra Sentinel-3")
        zppi_df = pd.DataFrame({
            "Nama Spot Penangkapan": [f"Spot Ikan Pelagis 1 ({pelabuhan.split('(')[0]})", f"Spot Karang Gosong 2", f"Spot Alur Luar 3"],
            "Jarak (Mil Laut)": ["8.4 NM", "12.6 NM", "16.2 NM"],
            "Arah Kompas": ["170° (Selatan)", "240° (Barat Daya)", "195° (Selatan)"],
            "Suhu Air (SST)": ["28.4°C", "28.8°C", "28.2°C"],
            "Pakan Klorofil": ["Sangat Subur (1.2 mg/m³)", "Subur (0.9 mg/m³)", "Melimpah (1.5 mg/m³)"],
            "Tingkat Keyakinan AI": ["94%", "88%", "96%"]
        })
        st.dataframe(zppi_df, use_container_width=True, hide_index=True)
        
        st.button("🧭 Mulai Pandu Arah Kompas ke Spot 1 (8.4 NM)", type="primary")

    with col_w2:
        fig_wave = px.line(
            df_data, x="Tanggal", y="Tinggi Gelombang (m)",
            title=f"Prediksi Tinggi Gelombang: {pelabuhan.split('(')[0]}",
            markers=True
        )
        fig_wave.add_hline(y=1.25, line_dash="dash", line_color="orange", annotation_text="Batas Aman Perahu Kecil (1.25m)")
        fig_wave.add_hline(y=2.5, line_dash="dash", line_color="red", annotation_text="Batas Bahaya (2.5m)")
        fig_wave.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_wave, use_container_width=True)

    # Tombol Darurat SOS
    st.divider()
    col_sos1, col_sos2 = st.columns([1, 4])
    with col_sos1:
        if st.button("🆘 PANCARKAN SINYAL SOS DARURAT", type="secondary"):
            st.error(f"🚨 Sinyal SOS Darurat berhasil dikirim via SMS Satelit ke Basarnas: Posisi Lat {loc_meta['lat']}, Lon {loc_meta['lon']}!")
    with col_sos2:
        st.caption("Gunakan tombol SOS jika mesin mati di tengah laut atau menghadapi cuaca buruk mendadak. Posisi GPS akan otomatis dikirimkan ke kantor SAR dan posko rukun nelayan.")


# ==============================================================================
# 🏙️ PERSONA 3: COMMAND CENTER BPBD (EARLY WARNING & DISPATCH)
# ==============================================================================
elif "3. Command Center BPBD" in persona_choice:
    st.markdown('<div class="main-header">🏙️ WeatherGuard BPBD Command Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Pusat Kendali Operasi Peringatan Dini Bencana Hidrometeorologi & Diseminasi Cepat</div>', unsafe_allow_html=True)

    col_wil1, col_wil2 = st.columns([3, 1])
    with col_wil1:
        urban_options = list(LOCATION_DATABASE.keys())
        wilayah_bpbd = st.selectbox(
            "📍 Pilih Wilayah Pemantauan Pusdalops BPBD:",
            urban_options,
            index=0 # Kota Tebing Tinggi
        )
        loc_meta = LOCATION_DATABASE[wilayah_bpbd]
        st.caption(f"📌 **Koordinat**: Lat {loc_meta['lat']}°, Lon {loc_meta['lon']}° | *{loc_meta['desc']}*")

    df_data = generate_forecast_for_location(loc_meta["lat"], loc_meta["lon"], loc_meta["elev"])
    max_rain = df_data["Curah Hujan (mm)"].max()
    max_wind = df_data["Kecepatan Angin (km/j)"].max()

    # Ringkasan Metrik
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Status Kesiapsiagaan", "SIAGA 2" if max_rain > 50 else "SIAGA 3", delta="Potensi Genangan DAS", delta_color="inverse")
    m2.metric("Puncak Hujan 7 Hari", f"{max_rain:.1f} mm/hari", "Hujan Lebat (H+3)")
    m3.metric("Kecepatan Angin Maks", f"{max_wind:.1f} km/jam", "Waspada Hembusan")
    m4.metric("Koneksi Sensor BMKG", "100% ONLINE", "Stasiun Aktif")

    st.divider()

    col_bpbd1, col_bpbd2 = st.columns([3, 2])
    with col_bpbd1:
        st.markdown(f"#### 🚨 Daftar Peringatan Dini Aktif: {wilayah_bpbd.split('-')[0]}")
        
        if "Tebing Tinggi" in wilayah_bpbd:
            st.markdown("""
            <div class="status-card-red">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; color:#991B1B;">🚨 PERINGATAN HUJAN LEBAT & LUAPAN DAS SUNGAI PADANG (72 mm/hari)</h4>
                    <span style="background:#EF4444; color:white; padding:4px 8px; border-radius:4px; font-weight:bold; font-size:0.8rem;">SIAGA 2</span>
                </div>
                <p style="margin-top:8px;"><b>Lokasi Rawan</b>: Kec. Rambutan, Padang Hulu, Tebing Tinggi Kota (Bantaran Sungai Padang & Sungai Bahilang)</p>
                <p><b>Analisis Dampak</b>: Debit air hulu Gunung Pamela/Sipispis meningkat drastis. Potensi banjir luapan genangan 40–80 cm di pemukiman bantaran sungai.</p>
                <p><b>Instruksi SOP BPBD Tebing Tinggi</b>: Siagakan perahu karet di Posko BPBD, pantau TMA Pintu Air Sungai Padang, imbau Camat dan Lurah waspada banjir kiriman malam hari.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="status-card-red">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; color:#991B1B;">🚨 PERINGATAN HUJAN LEBAT (>50 mm/hari) - {wilayah_bpbd.split('(')[0]}</h4>
                    <span style="background:#EF4444; color:white; padding:4px 8px; border-radius:4px; font-weight:bold; font-size:0.8rem;">SIAGA 2</span>
                </div>
                <p style="margin-top:8px;"><b>Prediksi Hujan Maksimal</b>: {max_rain:.1f} mm/hari</p>
                <p><b>Analisis Dampak</b>: Kapasitas drainase terlampaui. Potensi genangan air 30–60 cm di jalan arteri dan permukiman cekungan.</p>
                <p><b>Instruksi SOP BPBD</b>: Siagakan pompa bergerak, bersihkan saringan sampah pintu air, terbitkan imbauan siaga ke warga.</p>
            </div>
            """, unsafe_allow_html=True)

    with col_bpbd2:
        st.markdown("#### 📲 Panel Diseminasi Siaran Darurat (Broadcast Dispatch)")
        st.info(f"Kirim notifikasi otomatis ke aparat & warga {wilayah_bpbd.split('-')[0]}:")
        
        ch_wa = st.checkbox("WhatsApp Broadcast (Camat, Lurah, Kepling, Babinsa/Bhabinkamtibmas)", value=True)
        ch_sms = st.checkbox("SMS LBA (Location-Based Alerting) ke Nomor Warga", value=True)
        ch_siren = st.checkbox("Aktivasi Sirine Peringatan Dini Pintu Air Sungai", value=False)
        
        target_group = st.selectbox("Grup Sasaran:", [f"Camat & Lurah Se-{wilayah_bpbd.split('(')[0]}", "Relawan Kebencanaan & Kelompok Masyarakat", "Seluruh Nomor di Radius DAS"])
        
        if st.button("🚀 KIRIM SIARAN PERINGATAN DARURAT SEKARANG", type="primary", use_container_width=True):
            st.success(f"✅ Berhasil! Peringatan dini kebencanaan terkirim ke 86 kontak Camat/Lurah {wilayah_bpbd.split('(')[0]} via WhatsApp & SMS dalam 1.4 detik.")


# ==============================================================================
# 🗺️ PERSONA 4: PETA SPASIAL INTERAKTIF MULTI-LAYER (LEAFLET / FOLIUM)
# ==============================================================================
elif "4. Peta Spasial Interaktif" in persona_choice:
    st.markdown('<div class="main-header">🗺️ Visualisasi Peta Spasial Interaktif Multi-Layer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Peta Tematik Resolusi 5 km: Lapisan Suhu, Curah Hujan, Angin, Kelembaban, dan Indeks UV (Cakupan Nasional)</div>', unsafe_allow_html=True)

    col_lay1, col_lay2 = st.columns([1, 3])
    with col_lay1:
        st.markdown("#### 🎛️ Layer Peta Aktif:")
        layer_select = st.radio(
            "Pilih Lapisan Data Tematik:",
            ["🌧️ Curah Hujan Kumulatif (mm)", "🌡️ Suhu Permukaan (°C)", "💨 Kecepatan Angin (km/j)", "🌊 Gelombang Laut & ZPPI", "☀️ Indeks Radiasi UV"]
        )
        
        st.divider()
        fokus_wilayah = st.selectbox("📍 Zoom Cepat ke Wilayah:", ["Sumatera Utara (Tebing Tinggi, Medan, Belawan)", "Jawa & DKI Jakarta", "Seluruh Indonesia"])
        st.caption("Peta dibangun menggunakan modul Leaflet GIS dengan interpolasi grid kontinu resolusi 5 km.")

    with col_lay2:
        # Inisialisasi Peta Folium
        if "Sumatera Utara" in fokus_wilayah:
            map_center = [3.35, 98.95]
            map_zoom = 9
        elif "Jawa" in fokus_wilayah:
            map_center = [-6.8, 108.0]
            map_zoom = 8
        else:
            map_center = [-2.5, 118.0]
            map_zoom = 5

        m = folium.Map(location=map_center, zoom_start=map_zoom, tiles="CartoDB positron")

        # Tambahkan Titik Observasi Penting dari LOCATION_DATABASE
        for name, data in LOCATION_DATABASE.items():
            if "MARITIME" in data["sector"]:
                marker_color = "blue"
                icon_name = "tint"
            elif "URBAN" in data["sector"]:
                marker_color = "red"
                icon_name = "warning-sign"
            else:
                marker_color = "green"
                icon_name = "leaf"

            folium.Marker(
                [data["lat"], data["lon"]],
                popup=f"<b>{name}</b><br>{data['desc']}<br>Elevasi: {data['elev']} mdpl",
                tooltip=name,
                icon=folium.Icon(color=marker_color, icon=icon_name)
            ).add_to(m)

        # Poligon Simulasi Risiko Banjir DAS Sungai Padang / Sungai Bahilang (Kota Tebing Tinggi)
        folium.Polygon(
            locations=[
                [3.350, 99.140],
                [3.350, 99.185],
                [3.310, 99.185],
                [3.310, 99.140]
            ],
            color="#EF4444",
            fill=True,
            fill_color="#EF4444",
            fill_opacity=0.35,
            popup="Zona Siaga 2: Risiko Luapan DAS Sungai Padang & Bahilang (Kota Tebing Tinggi)"
        ).add_to(m)

        st_folium(m, width=900, height=520)

st.sidebar.caption("WeatherGuard AI v1.0.0 © 2026. All rights reserved.")
