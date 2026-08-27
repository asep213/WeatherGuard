# RENCANA IMPLEMENTASI & ROADMAP 3 BULAN (12 MINGGU)
## WeatherGuard AI: Jadwal Kerja Sprint, Alokasi Tim, Deliverable, dan Manajemen Risiko Proyek

---

### 1. Garis Besar Jadwal Pelaksanaan (3-Month Timeline Overview)

Proyek dijalankan dengan metodologi **Agile Scrum** yang terbagi dalam **6 Sprint (masing-masing berdurasi 2 minggu)**:

```mermaid
gantt
    title Roadmap Implementasi WeatherGuard AI (12 Minggu)
    dateFormat  YYYY-MM-DD
    section Bulan 1: Fondasi & Pipeline Data
    Sprint 1 (W1-W2): Setup Infrastruktur & Ingesti Data           :a1, 2026-09-01, 14d
    Sprint 2 (W3-W4): Data Lake Zarr & Baseline AI Model           :a2, after a1, 14d
    section Bulan 2: Fine-Tuning AI & Impact Engine
    Sprint 3 (W5-W6): Fine-Tuning Model BMKG & Downscale 5km       :a3, after a2, 14d
    Sprint 4 (W7-W8): Implementasi 54 Aturan Dampak & API Gateway  :a4, after a3, 14d
    section Bulan 3: UI/UX, Uji Lapangan & Go-Live
    Sprint 5 (W9-W10): Pembuatan PWA Mobile & Dashboard BPBD       :a5, after a4, 14d
    Sprint 6 (W11-W12): Pilot Lapangan, Audit Keamanan & Serah Terima:a6, after a5, 14d
```

---

### 2. Rincian Rencana Kerja per Sprint

#### 📅 BULAN 1: FONDASI INFRASTRUKTUR & PIPELINE MULTI-SUMBER DATA

##### **Sprint 1 (Minggu 1 – 2): Setup Infrastruktur & Ingesti Data Terbuka**
- **Fokus Utama**: Menyiapkan klaster komputasi, database, dan konektor API external.
- **Tugas Spesifik**:
  1. Provisioning cloud server (TimescaleDB, PostGIS, MinIO S3, Redis, dan GPU compute node).
  2. Membangun modul ekstraksi data BMKG (`bmkg_client.py`), OpenWeatherMap (`openweather_client.py`), dan NOAA GFS/WW3 GRIB2 parser.
  3. Membangun sistem Quality Control (QC) otomatis untuk pembersihan data anomali / *missing values*.
- **Deliverables**: Pipeline ingesti otomatis berbasis Celery yang aktif berjalan menyerap data per jam.

##### **Sprint 2 (Minggu 3 – 4): Arsitektur Data Lake Geosparsial & Baseline AI Model**
- **Fokus Utama**: Konversi data multidimensi dan evaluasi performa model pondasi dasar.
- **Tugas Spesifik**:
  1. Membangun pipeline konversi data satelit Himawari-9 (IR/VIS) dan Sentinel-1/3 menjadi format *chunked Zarr arrays*.
  2. Menyiapkan repositori bobot model *IBM-NASA Prithvi WxC* dan *NVIDIA Earth-2*.
  3. Melakukan uji inferensi *baseline* (tanpa fine-tuning) pada grid domain Indonesia ($6^\circ\text{LU} - 11^\circ\text{LS}$, $95^\circ\text{BT} - 141^\circ\text{BT}$).
- **Deliverables**: *Benchmark report* model awal dan skema database spatial *hypertables* terisi data observasi.

---

#### 📅 BULAN 2: FINE-TUNING MODEL AI & MESIN KEPUTUSAN BERBASIS DAMPAK

##### **Sprint 3 (Minggu 5 – 6): Fine-Tuning Data Historis BMKG 10 Tahun & Downscaling 5 km**
- **Fokus Utama**: Meningkatkan akurasi prediksi cuaca lokal kepulauan tropis Indonesia.
- **Tugas Spesifik**:
  1. Menyiapkan dataset latih (*training pipeline*) dari 200+ stasiun synoptic BMKG (2014–2024).
  2. Melatih lapisan *adapter / fine-tuning* model Prithvi WxC menggunakan komputasi GPU A100.
  3. Mengintegrasikan data Digital Elevation Model (DEMNAS 30m) untuk modul *Diffusion Super-Resolution Downscaling* menuju resolusi spasial **5 km**.
  4. Menerapkan koreksi bias statistik (*Quantile Delta Mapping*).
- **Deliverables**: Model AI terkalibrasi lokal dengan akurasi prediksi hujan 3-hari mencapai **$\ge 80\%$**.

##### **Sprint 4 (Minggu 7 – 8): Implementasi 54 Aturan Dampak & REST/WebSocket API**
- **Fokus Utama**: Mengonversi angka cuaca menjadi matriks rekomendasi terukur.
- **Tugas Spesifik**:
  1. Mengodekan modul aturan pertanian: SPI-30 kekeringan, jendela semprot, pemupukan, kalender tanam.
  2. Mengodekan modul aturan maritim: tinggi gelombang $H_s$, *safe sailing window*, peta titik ikan ZPPI.
  3. Mengodekan modul perkotaan: alarm hujan lebat $>50\text{ mm}$, angin kencang $>60\text{ km/jam}$, indeks genangan.
  4. Membangun REST API FastAPI berkecepatan tinggi dengan integrasi Redis Cache dan WebSocket alerting.
- **Deliverables**: Backend FastAPI lengkap dengan dokumentasi Swagger UI dan waktu respons $<1.5\text{ detik}$.

---

#### 📅 BULAN 3: ANTARMUKA PENGGUNA (UI/UX), PILOT TEST & DEPLOYMENT PRODUKSI

##### **Sprint 5 (Minggu 9 – 10): Antarmuka Multi-Persona (PWA Mobile & Web Command Center)**
- **Fokus Utama**: Pengembangan antarmuka interaktif yang mudah dipahami persona sasaran.
- **Tugas Spesifik**:
  1. Membangun aplikasi PWA Mobile Petani (Tampilan kartu hijau/kuning/merah, fitur pembaca suara).
  2. Membangun aplikasi PWA Mobile Nelayan (Tampilan kontras tinggi, kompas ZPPI, tombol darurat SOS).
  3. Membangun Web Command Center BPBD (Peta spasial interaktif Leaflet/MapLibre, layer visualisasi multi-hazard, panel broadcast WhatsApp).
- **Deliverables**: Antarmuka interaktif responsif untuk 3 persona yang terhubung penuh ke API Backend.

##### **Sprint 6 (Minggu 11 – 12): Uji Coba Pilot Lapangan, Validasi Ahli, dan Go-Live**
- **Fokus Utama**: Uji coba langsung bersama pengguna akhir di 3 lokasi percontohan.
- **Tugas Spesifik**:
  1. Pelaksanaan uji coba pilot di 3 lokasi:
     - Sentra Padi: Kabupaten Karawang, Jawa Barat.
     - Kawasan Pesisir/Nelayan: Pelabuhan Teluk Penyu, Cilacap, Jawa Tengah.
     - Kawasan Perkotaan/BPBD: DKI Jakarta & DAS Ciliwung.
  2. *Focus Group Discussion (FGD)* validasi bersama agronomis, oseanografer, dan petugas Pusdalops.
  3. Uji beban performa (*load testing* 10.000 concurrent requests) dan audit keamanan siber (*penetration testing*).
  4. Penyusunan laporan akhir, penyerahan repositori, dan *Go-Live*.
- **Deliverables**: Sistem WeatherGuard AI operasional penuh dan siap diserahterimakan ke pemangku kepentingan.

---

### 3. Komposisi Tim Pengembang & Alokasi Sumber Daya

| Peran Tim | Jumlah Personel | Tanggung Jawab Utama |
|---|---|---|
| **Project Manager / Scrum Master** | 1 Orang | Manajemen sprint, koordinasi pemangku kepentingan, mitigasi hambatan proyek. |
| **Lead AI / Deep Learning Scientist** | 2 Orang | Fine-tuning model Prithvi WxC / Earth-2, downscaling super-resolution, validasi akurasi. |
| **Geospatial & Data Engineer** | 2 Orang | Pipeline ingesti GRIB2/Zarr/NetCDF, konfigurasi TimescaleDB, PostGIS, dan MinIO S3. |
| **Backend & Cloud/DevOps Engineer** | 2 Orang | Pengembangan FastAPI, arsitektur microservices, Redis caching, Docker & Kubernetes. |
| **Frontend & Mobile UI/UX Developer** | 2 Orang | PWA Mobile Petani & Nelayan, Dashboard Web GIS Command Center BPBD. |
| **Panel Ahli Domain (Konsultan Mitra)** | 3 Orang | 1x Agronomis (IPB/Balitklimat), 1x Ahli Oseanografi (ITB/BRIN), 1x Analis Bencana (BNPB). |
| **QA Engineer & Field Officer** | 2 Orang | Pengujian sistem, uji coba langsung di lapangan bersama poktan dan kelompok nelayan. |

---

### 4. Matriks Manajemen Risiko Proyek (Risk Management)

| Potensi Risiko | Tingkat Dampak | Probabilitas | Rencana Mitigasi (Mitigation Strategy) |
|---|---|---|---|
| **API Eksternal BMKG / Satelit Mengalami Gangguan (*Downtime*)** | Tinggi | Sedang | Menerapkan *fallback otomatis* ke data satelit global (GFS/ECMWF) dan estimasi *persistence nowcasting* berbasis radar terdekat. |
| **Konektivitas Internet Buruk di Sawah / Tengah Laut** | Sedang | Tinggi | Menerapkan arsitektur *Progressive Web App (PWA)* dengan *Service Worker Cache* lokal sehingga data ramalan tetap dapat dibuka saat offline. |
| **Waktu Pelatihan AI Lambat karena Keterbatasan GPU** | Tinggi | Rendah | Memanfaatkan klaster GPU HPC berbasis spot instances (A100) khusus pada sprint pelatihan, dan menggunakan model kuantisasi ONNX INT8 untuk inferensi harian. |
| **Resistensi / Kesulitan Adopsi oleh Petani & Nelayan Sepuh** | Sedang | Sedang | Menyederhanakan UI dengan hanya menampilkan warna hijau/merah, tombol berukuran besar, dan menyediakan instruksi suara dalam bahasa daerah. |
