# PANDUAN INSTALASI & DEPLOYMENT TEKNIS
## WeatherGuard AI: Panduan Setup Lingkungan Pengembangan, Docker Compose, Database TimescaleDB/PostGIS, dan Model AI

---

### 1. Prasyarat Sistem & Kebutuhan Perangkat Keras

#### Spesifikasi Minimum (Pengujian Lokal / Server Pengembangan)
- **CPU**: 4 Core x86_64 (Intel Core i5 / AMD Ryzen 5 / Intel Xeon)
- **RAM**: 16 GB DDR4
- **Penyimpanan**: 100 GB SSD / NVMe
- **OS**: Ubuntu 22.04 / 24.04 LTS, Debian 12, atau Windows 11 (dengan WSL2 / Docker Desktop)
- **Akselerasi AI**: CPU Inference (atau GPU NVIDIA 6GB+ VRAM opsional)

#### Spesifikasi Rekomendasi (Server Produksi Skala Provinsi/Nasional)
- **CPU**: 8–16 vCPU (AMD EPYC / Intel Xeon Scalable)
- **RAM**: 32–64 GB ECC RAM
- **Penyimpanan**: 500 GB – 1 TB NVMe SSD (Penyimpanan database & cache Zarr)
- **GPU**: 1x NVIDIA L4 (24GB), NVIDIA A100 (40/80GB), atau NVIDIA RTX 4090 (24GB)
- **Driver & Toolkit**: NVIDIA Driver 535+, CUDA Toolkit 12.1+, NVIDIA Container Toolkit

---

### 2. Metode 1: Instalasi Instan Menggunakan Docker Compose (Direkomendasikan)

Metode ini akan secara otomatis mengorkestrasi 5 kontainer utama:
1. `weatherguard-db`: PostgreSQL 16 dengan ekstensi TimescaleDB & PostGIS aktif.
2. `weatherguard-redis`: Redis In-Memory Cache & Message Broker.
3. `weatherguard-backend`: FastAPI REST API & WebSocket Server.
4. `weatherguard-worker`: Celery Background Worker untuk tugas ingesti berkala.
5. `weatherguard-frontend`: Streamlit Multi-Persona Interactive UI.

#### Langkah 1: Kloning Repositori & Persiapan Environment
```bash
# Pindah ke direktori workspace
cd c:/Users/Lenovo/Documents/personal/WeatherGuard

# Salin template variabel lingkungan
cp .env.example .env
```

#### Langkah 2: Konfigurasi Berkas `.env`
Buka berkas `.env` dan masukkan kredensial yang sesuai:
```ini
# --- DATABASE CONFIGURATION ---
POSTGRES_USER=weatherguard_admin
POSTGRES_PASSWORD=WeatherGuardSecure2026!
POSTGRES_DB=weatherguard_db
POSTGRES_HOST=weatherguard-db
POSTGRES_PORT=5432

# --- REDIS CONFIGURATION ---
REDIS_URL=redis://weatherguard-redis:6379/0

# --- API KEYS & EXTERNAL DATA ---
OPENWEATHER_API_KEY=your_openweather_api_key_here
BMKG_API_TOKEN=optional_bmkg_partner_token
NASA_EARTHDATA_TOKEN=optional_nasa_token

# --- APPLICATION SETTINGS ---
APP_ENV=production
SECRET_KEY=super-secret-jwt-key-change-this-in-production
INFERENCE_DEVICE=cpu # Ganti ke 'cuda' jika memiliki GPU NVIDIA
LOG_LEVEL=INFO
```

#### Langkah 3: Menjalankan Klaster Kontainer
```bash
# Bangun image dan jalankan di latar belakang (detached mode)
docker compose up --build -d

# Periksa status seluruh container
docker compose ps
```

#### Langkah 4: Verifikasi Layanan
- **FastAPI Documentation (Swagger UI)**: Buka `http://localhost:8000/docs`
- **Streamlit Interactive UI**: Buka `http://localhost:8501`
- **Celery Worker Logs**: `docker compose logs -f weatherguard-worker`

---

### 3. Metode 2: Instalasi Manual (Lokal Python Virtual Environment)

Jika Anda ingin melakukan pengembangan (*debugging*) langsung tanpa Docker:

#### Langkah 1: Setup Python Virtual Environment
```bash
# Buat virtual environment dengan Python 3.10 atau 3.11
python -m venv venv

# Aktivasi virtual environment
# Pada Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Pada Linux / macOS:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

#### Langkah 2: Instalasi Dependensi Inti
```bash
# Instalasi seluruh pustaka yang tercantum pada requirements.txt
pip install -r requirements.txt
```

> [!NOTE]
> Jika Anda mengalami kendala instalasi `GDAL` atau `rasterio` pada sistem operasi Windows, disarankan menggunakan *pre-compiled wheels* dari Christoph Gohlke atau menggunakan distribusi Conda: `conda install -c conda-forge gdal xarray netcdf4`.

#### Langkah 3: Menjalankan Database PostgreSQL + TimescaleDB & PostGIS
Jalankan PostgreSQL lokal Anda, kemudian eksekusi perintah SQL berikut untuk mengaktifkan ekstensi yang diperlukan:
```sql
CREATE DATABASE weatherguard_db;
\c weatherguard_db;

-- Mengaktifkan ekstensi PostGIS untuk data spasial
CREATE EXTENSION IF NOT EXISTS postgis;

-- Mengaktifkan ekstensi TimescaleDB untuk data time-series
CREATE EXTENSION IF NOT EXISTS timescaledb;
```

#### Langkah 4: Menjalankan Server Backend FastAPI
```bash
# Jalankan server backend dengan reload otomatis saat ada perubahan kode
uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Langkah 5: Menjalankan Streamlit Interactive Dashboard
```bash
# Buka terminal baru (pastikan venv aktif)
streamlit run src/frontend/app.py --server.port 8501 --server.address 0.0.0.0
```

---

### 4. Setup Model AI Pondasi (IBM-NASA Prithvi WxC / Surya Weights)

Sistem telah dilengkapi dengan *inference engine* modular yang dapat memuat bobot model PyTorch / ONNX:

1. **Unduh Model Weights**:
   ```bash
   # Buat folder penyimpanan bobot model
   mkdir -p models/checkpoints

   # Unduh checkpoint model dasar (contoh dari Hugging Face Hub)
   # git lfs install
   # git clone https://huggingface.co/ibm-nasa-geospatial/Prithvi-WxC models/checkpoints/Prithvi-WxC
   ```
2. **Kompilasi Model ke ONNX / TensorRT (Opsional untuk Akselerasi 3x Lebih Cepat)**:
   Modul `src/backend/model/inference_engine.py` secara otomatis mendeteksi ketersediaan runtime GPU CUDA. Jika GPU tidak terdeteksi, sistem secara cerdas beralih ke mode *CPU high-performance downscaling*.

---

### 5. Panduan Pemeliharaan & Monitoring Sistem di Produksi

#### Manajemen Log & Kinerja
- **Monitoring Health API**: Endpoint `GET /api/v1/health` menyediakan metrik koneksi database, antrean Celery, dan penggunaan memori.
- **Pembersihan Data Berkala (Retention Policy)**:
  Data grid resolusi 5 km historis yang berusia lebih dari 90 hari otomatis dipindahkan ke *cold storage* (S3 Glacier/MinIO archive) melalui kebijakan retensi TimescaleDB:
  ```sql
  -- Menambahkan policy drop chunk otomatis untuk data ramalan lama
  SELECT add_retention_policy('weather_forecasts', INTERVAL '90 days');
  ```
