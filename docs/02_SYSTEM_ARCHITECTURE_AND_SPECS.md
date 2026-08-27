# SPESIFIKASI TEKNIS & ARSITEKTUR SISTEM
## WeatherGuard AI: Arsitektur End-to-End, Model AI Pondasi, Database Time-Series Spasial, dan Pipeline Inferensi

---

### 1. Arsitektur Sistem Terintegrasi (System Block Diagram)

Sistem dirancang menggunakan arsitektur modular berorientasi layanan (*Microservices-oriented & Event-Driven Architecture*), memisahkan tugas penyerapan data (*data ingestion*), pelatihan/inferensi AI berkinerja tinggi (*AI core*), pemrosesan logika dampak (*impact engine*), dan antarmuka pengguna (*frontend delivery*).

```mermaid
graph TB
    subgraph Data_Sources["1. Sumber Data Eksternal"]
        DS_BMKG["BMKG Open Data\n(API, Radar, AWS Synoptic)"]
        DS_OWM["OpenWeatherMap\n(OneCall API 3.0)"]
        DS_HIMA["JMA Himawari-9\n(Band 08, 13, 14 Cloud/Rain)"]
        DS_SENT["ESA Sentinel-1/3\n(SAR Wind, SLSTR SST, OLCI Chl-a)"]
        DS_GFS["NOAA GFS / WW3\n(GRIB2 0.25 deg)"]
    end

    subgraph Ingestion_Cluster["2. Pipeline Ingesti & ETL (Celery + Apache Airflow/Cron)"]
        ING_FETCHER["Data Fetcher Workers\n(Async HTTP & S3 Downloader)"]
        ING_PARSER["Format Normalizer\n(GRIB2, NetCDF, HDF5, XML, JSON)"]
        ING_GRID["Spatial Regridding & Interpolator\n(Xarray, CDO, Bilinear/Conservative)"]
    end

    subgraph Storage_Layer["3. Lapisan Penyimpanan (Hybrid Time-Series & Spatial)"]
        DB_TIME[("TimescaleDB (PostgreSQL)\n- Hypertables Time-Series\n- PostGIS Geometry/Polygon")]
        STORAGE_OBJ[("MinIO / AWS S3\n- Gridded Zarr Arrays\n- NetCDF4 Files (5km Spatial Grid)")]
        DB_REDIS[("Redis In-Memory Cache\n- Session, Rate Limit, API Cache")]
    end

    subgraph AI_Inference_Cluster["4. Weather Foundation AI & Downscaling Engine"]
        AI_LOADER["Tensor Pipeline & Boundary Loader"]
        AI_BACKBONE["Foundation Model Backbone\n(IBM-NASA Prithvi WxC / Earth-2)"]
        AI_DOWNSCALE["Spatial Downscaling Model (5 km)\n(Physics-Informed CorrDiff / UNet-DEM)"]
        AI_POST["Post-Processing & Bias Correction\n(Quantile Mapping & Kalman Filter)"]
    end

    subgraph Impact_Engine_Layer["5. Mesin Keputusan Berbasis Dampak (Impact Engine)"]
        IMP_AGRI["🌾 Modul Pertanian\n- SPI Kekeringan\n- Jendela Semprot / Pupuk\n- Kalender Tanam Dinamis"]
        IMP_MARI["⚓ Modul Maritim\n- Tinggi Gelombang Signifikan\n- Arus Permukaan & Swell\n- Safe Window & ZPPI Nelayan"]
        IMP_URBAN["🏙️ Modul Perkotaan\n- Early Warning Hujan >50mm\n- Angin Kencang >60km/jam\n- Indeks Limpasan Genangan"]
    end

    subgraph API_Serving["6. Gateway Layanan (FastAPI + WebSocket)"]
        API_REST["FastAPI REST Endpoints\n(/api/v1/forecast, /api/v1/impact)"]
        API_WS["WebSocket Server\n(Realtime Emergency Alerting)"]
        NOTIF_DISP["Notification Dispatcher\n(WhatsApp, Firebase FCM, SMS)"]
    end

    subgraph Presentation["7. Antarmuka Pengguna (Clients)"]
        CLI_AGRI["📱 Petani PWA Mobile\n(Offline-First, Low Bandwidth)"]
        CLI_MARI["📱 Nelayan PWA Mobile\n(High Contrast, GPS Safe-Window)"]
        CLI_BPBD["🖥️ BPBD Web Dashboard\n(Leaflet/MapLibre Multi-layer GIS)"]
    end

    Data_Sources --> Ingestion_Cluster
    Ingestion_Cluster --> Storage_Layer
    Storage_Layer --> AI_Inference_Cluster
    AI_Inference_Cluster --> Impact_Engine_Layer
    Impact_Engine_Layer --> Storage_Layer
    Impact_Engine_Layer --> API_Serving
    API_Serving --> Presentation
```

---

### 2. Spesifikasi Detail Komponen Sistem

#### A. Pipeline Ingesti Data & Normalisasi Grid
- **Pustaka Pemrosesan Geosparsial**: `xarray`, `rioxarray`, `netCDF4`, `cfgrib`, `pyresample`.
- **Cakupan Spasial Domain Indonesia**:
  - Garis Lintang: $6.0^\circ\text{ LU}$ s.d. $11.0^\circ\text{ LS}$
  - Garis Bujur: $95.0^\circ\text{ BT}$ s.d. $141.0^\circ\text{ BT}$
- **Format Penyimpanan Grid**: Data prediksi spasial disimpan dalam format **Zarr chunked store** di MinIO untuk pemotongan koordinat (*slicing*) secepat kilat ($<50\text{ ms}$).

#### B. Model AI Pondasi & Strategi Downscaling 5 km

Sistem mengadopsi model **IBM-NASA Prithvi WxC** (atau **NVIDIA Earth-2 FourCastNet / CorrDiff**) sebagai *foundation model*, dengan detail teknis berikut:

```mermaid
flowchart LR
    INPUT_GFS["Global Boundary (GFS / ERA5)\n(25 km Grid / 0.25 deg)"] --> EMBED["Patch Embedding &\nPositional Encoders"]
    EMBED --> VIT_BLOCKS["Prithvi WxC Vision Transformer\n(120M - 1B Parameters)"]
    VIT_BLOCKS --> TOPOGRAPHY["Digital Elevation Model (SRTM 30m)\n+ Land Use / Land Cover (ESA)"]
    TOPOGRAPHY --> DOWNSCALER["Diffusion Downscaler (CorrDiff / UNet)\n(High-Resolution 5 km Grid)"]
    DOWNSCALER --> BIAS["BMKG 10-Yr Station Bias Correction\n(Quantile Delta Mapping)"]
    BIAS --> OUTPUT["Prediksi 7-10 Hari (1-Hour Step)\n- Suhu, Hujan, Angin, Kelembaban, UV, Gelombang"]
```

1. **Backbone Model (Prithvi WxC / Earth-2)**:
   - Arsitektur berbasis *Masked Autoencoder (MAE)* dan *Vision Transformer (ViT)* 3D yang dilatih pada representasi data atmosfer multi-level (geopotensial, temperatur udara, angin U/V pada level 1000hPa hingga 200hPa).
2. **Fine-Tuning dengan Data BMKG 10 Tahun (2014–2024)**:
   - Memasukkan data observasi 200+ stasiun synoptic BMKG, radar maritim C-Band/X-Band, dan AWS untuk mengoreksi bias monsun tropis dan sirkulasi lokal darat-laut (*land-sea breeze*).
3. **Super-Resolusi & Downscaling Spasial (5 km)**:
   - Menggunakan *Physics-Informed Generative Downscaling* dengan menyuntikkan data medan elevasi (*Shuttle Radar Topography Mission - SRTM 30m*) dan tutupan lahan (*Copernicus Land Cover*) sebagai variabel pembimbing (*conditioning features*).

---

### 3. Skema Basis Data (TimescaleDB & PostGIS)

Sistem menggunakan **PostgreSQL 16** yang diperkaya dengan ekstensi:
- **TimescaleDB**: Untuk mengelola data *time-series* cuaca observasi dan prediksi dalam struktur *hypertables* terpartisi otomatis.
- **PostGIS**: Untuk kueri spasial poligon batas administratif desa, koordinat pelabuhan, daerah aliran sungai (DAS), dan polygon lahan pertanian.

#### Diagram Relasi Entitas (ERD)

```mermaid
erDiagram
    LOCATIONS ||--o{ WEATHER_FORECASTS : "has time-series"
    LOCATIONS ||--o{ EARLY_WARNING_LOGS : "triggers alert"
    LOCATIONS ||--o{ AGRI_RECOMMENDATIONS : "receives"
    LOCATIONS ||--o{ MARITIME_SAFETY_WINDOWS : "receives"
    LOCATIONS ||--o{ USERS : "belongs to"

    LOCATIONS {
        uuid id PK
        string name
        string sector_type "AGRI | MARITIME | URBAN"
        geometry geom "PostGIS Point / Polygon"
        float elevation_m
        string province
        string regency
        string district
    }

    WEATHER_FORECASTS {
        timestamptz time PK
        uuid location_id FK, PK
        float temp_c
        float rain_rate_mm_h
        float rain_accum_24h_mm
        float wind_speed_kmh
        float wind_direction_deg
        float humidity_pct
        float uv_index
        float wave_height_m
        float wave_period_s
        float sea_surface_temp_c
        string data_source "AI_PRITHVI | BMKG | OWM"
    }

    EARLY_WARNING_LOGS {
        uuid id PK
        uuid location_id FK
        timestamptz triggered_at
        string hazard_type "EXTREME_RAIN | HIGH_WIND | DROUGHT | HIGH_WAVE"
        string severity "WARNING | WATCH | ADVISORY"
        jsonb payload_detail
        boolean is_broadcasted
    }

    AGRI_RECOMMENDATIONS {
        uuid id PK
        uuid location_id FK
        date valid_date
        float spi_30_value
        string spray_window_status "OPTIMAL | CAUTION | FORBIDDEN"
        string fertilizer_status "SAFE | RISK_OF_WASHOFF"
        text action_notes
    }

    MARITIME_SAFETY_WINDOWS {
        uuid id PK
        uuid location_id FK
        timestamptz window_start
        timestamptz window_end
        string sailing_status "SAFE | CAUTION | DANGER"
        float max_wave_height_m
        float max_wind_kmh
        text recommendation_text
    }
```

---

### 4. Spesifikasi API Gateway & Format Response

FastAPI mengelola routing RESTful dan koneksi WebSocket berkinerja tinggi.

#### Contoh Endpoint Utama

| Method | Endpoint | Deskripsi |
|---|---|---|
| `GET` | `/api/v1/forecast/point?lat=-6.9&lon=107.6&days=7` | Mengambil data ramalan cuaca 7 hari resolusi 1 jam pada titik koordinat. |
| `GET` | `/api/v1/impact/agriculture?location_id=xxx` | Menghasilkan rekomendasi tanam, pemupukan, dan indeks SPI. |
| `GET` | `/api/v1/impact/maritime?port_code=TanjungPriok` | Menghasilkan tinggi gelombang, status *Safe Window*, dan peta ZPPI. |
| `GET` | `/api/v1/impact/urban/early-warning` | Mengambil daftar peringatan dini aktif hujan ekstrem & angin kencang. |
| `WS` | `/ws/alerts/stream` | Koneksi WebSocket *realtime* untuk notifikasi gawat darurat BPBD. |

#### Contoh Payload JSON Respon Impact Pertanian
```json
{
  "location": {
    "name": "Kecamatan Telagasari, Karawang",
    "coordinates": [-6.302, 107.408],
    "sector": "AGRICULTURE"
  },
  "generated_at": "2026-08-21T09:00:00Z",
  "spi_index": {
    "spi_30": -0.85,
    "classification": "Normal cenderung kering",
    "irrigation_recommendation": "Aktifkan giliran air irigasi tersier 3 hari sekali."
  },
  "forecast_summary_7d": {
    "total_precipitation_mm": 18.5,
    "max_temp_c": 33.2,
    "avg_humidity_pct": 76.0
  },
  "action_matrix": [
    {
      "date": "2026-08-22",
      "pesticide_spray_window": {
        "status": "OPTIMAL",
        "recommended_hours": "06:00 - 09:00 WIB",
        "reason": "Kecepatan angin <10 km/jam, probabilitas hujan <10%."
      },
      "fertilization": {
        "status": "SAFE",
        "reason": "Tidak ada potensi hujan lebat dalam 24 jam ke depan."
      }
    }
  ]
}
```

---

### 5. Arsitektur Deployment & Orkestrasi Kontainer

Sistem dikemas secara utuh menggunakan standar **Docker & OCI Container**, siap dijalankan pada lingkungan lokal/single-server via **Docker Compose** atau skala *production enterprise* via **Kubernetes (K8s)**.

```mermaid
graph TD
    LB["Ingress Nginx / Cloudflare Load Balancer\n(SSL Termination & Rate Limiting)"]
    
    subgraph K8s_Cluster["Kubernetes Production Cluster"]
        API_PODS["FastAPI Pods (Replica 3-5)\n(Stateless API Service)"]
        STREAMLIT_PODS["Streamlit UI Pods (Replica 2)\n(Interactive Visualization)"]
        CELERY_WORKER["Celery Data Ingestion Workers\n(Scheduled Ingestion Pods)"]
        GPU_WORKER["GPU Inference Worker Pods\n(NVIDIA Triton / PyTorch ONNX)"]
    end

    subgraph State_Storage["Stateful Services"]
        REDIS_NODE[("Redis Cluster")]
        TIMESCALE_CLUSTER[("TimescaleDB HA Primary + Replica")]
        S3_STORAGE[("MinIO S3 Object Storage")]
    end

    LB --> API_PODS
    LB --> STREAMLIT_PODS
    API_PODS --> REDIS_NODE
    API_PODS --> TIMESCALE_CLUSTER
    CELERY_WORKER --> S3_STORAGE
    CELERY_WORKER --> TIMESCALE_CLUSTER
    GPU_WORKER --> S3_STORAGE
    GPU_WORKER --> TIMESCALE_CLUSTER
```

- **GPU Acceleration**: Inferensi model dijalankan pada *container* beralaskan CUDA 12.0+ dengan dukungan *ONNX Runtime GPU* / *TensorRT* untuk efisiensi throughput komputasi.
- **Failover & Caching**: Setiap hasil prediksi grid 5 km yang telah dihitung akan di-*cache* di Redis dan MinIO, menjamin waktu respons API konsisten di bawah **1.5 detik** meskipun diakses oleh ribuan pengguna secara bersamaan.
