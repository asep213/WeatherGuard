# DESAIN ANTARMUKA PENGGUNA (UI/UX) & ALUR PENGGUNA (PERSONA FLOWS)
## WeatherGuard AI: Perancangan Aplikasi Mobile (PWA) Petani, Mobile (PWA) Nelayan, dan Web Command Center BPBD

---

### 1. Filosofi Desain & Pendekatan Human-Centered Design

WeatherGuard AI dirancang dengan prinsip **Inklusivitas & Kesederhanaan Kognitif**:
- **Mobile First & Offline-Ready**: Bekerja mulus pada jaringan seluler 3G/EDGE yang tidak stabil di perdesaan dan tengah laut.
- **Sistem Kode Warna Lampu Lalu Lintas (*Traffic Light UI*)**: Menggunakan Hijau (Aman/Bisa Dilakukan), Kuning (Waspada/Perhatian), dan Merah (Bahaya/Tunda) untuk menghilangkan kebingungan angka meteorologi yang rumit.
- **Tipografi Jelas & Ikonografi Visual**: Menggunakan font modern *Inter / Outfit* dengan kontras rasio WCAG AAA ($> 7:1$) untuk kenyamanan membaca di bawah terik sinar matahari.

---

### 2. Persona 1: Petani Padi & Sayuran (Aplikasi Mobile Android / PWA)

#### Profil Persona
- **Nama Persona**: Pak Slamet (48 Tahun), Petani Padi di Karawang, Jawa Barat.
- **Perangkat**: Smartphone Android Entry-Level (RAM 2-3 GB, Layar 5.5", Android 10+).
- **Tantangan**: Koneksi internet sering putus di petak sawah; sulit memahami grafik cuaca kurva probabilitas.
- **Kebutuhan Utama**: Tahu pasti apakah hari ini boleh menyemprot hama atau menabur pupuk tanpa takut hanyut terkena hujan.

#### Wireframe & Tata Letak Antarmuka Petani (Mobile Android)

```
+---------------------------------------------------------+
|  [☰ Menu]         🌾 WeatherGuard Tani       [🔊 Audio] |
|  📍 Sawah Sukamaju, Karawang (Otomatis GPS)            |
+---------------------------------------------------------+
|                                                         |
|  +---------------------------------------------------+  |
|  |  STATUS HARI INI: JUMAT, 21 AGUSTUS 2026           |  |
|  |  🌤️ Cerah Berawan | 31°C | Angin Sejuk (8 km/j)   |  |
|  +---------------------------------------------------+  |
|                                                         |
|  📢 REKOMENDASI TANI HARI INI (AKSI UTAMA):             |
|  +---------------------------------------------------+  |
|  | 🟢 [IKON SEMPROT] PENYEMPROTAN PESTISIDA: SANGAT BAIK |
|  |    Waktu Terbaik: 06.30 - 09.00 WIB                |
|  |    Alasan: Angin tenang, tidak ada hujan 12 jam.   |
|  +---------------------------------------------------+  |
|  | 🟢 [IKON PUPUK] PEMUPUKAN UREA/NPK: AMAN             |
|  |    Pupuk tidak akan hanyut tererosi.               |
|  +---------------------------------------------------+  |
|  | 🟡 [IKON AIR] KONDISI AIR TANAH (SPI): AGAK KERING   |
|  |    Rekomendasi: Alirkan air irigasi setinggi 2 cm. |
|  +---------------------------------------------------+  |
|                                                         |
|  📅 JENDELA WAKTU 7 HARI KE DEPAN:                      |
|  +---------------------------------------------------+  |
|  | Sab | 🟢 Semprot: Aman    | 🟢 Pupuk: Aman           |
|  | Min | 🛑 Semprot: Dilarang | 🛑 Hujan Lebat (45 mm)   |
|  | Sen | 🟢 Semprot: Aman    | 🟢 Jemur Gabah: Bagus    |
|  +---------------------------------------------------+  |
|                                                         |
|  [ 📞 Konsultasi Penyuluh Pertanian ]  [ 💾 Mode Offline ]|
+---------------------------------------------------------+
```

#### Alur Pengguna (User Flow) Petani
1. Petani membuka aplikasi di pagi hari (aplikasi otomatis mendeteksi lokasi sawah dari GPS).
2. Kartu utama langsung menampilkan warna **Hijau / Kuning / Merah** untuk 3 kegiatan kunci: Semprot, Pupuk, dan Air.
3. Petani dapat menekan tombol **"🔊 Audio"** untuk mendengarkan arahan suara dalam Bahasa Indonesia / Bahasa Daerah (Sunda/Jawa).
4. Data 7 hari terakhir otomatis tersimpan di memori HP (*Service Worker Cache*), sehingga tetap dapat dibaca saat berada di tengah petak sawah tanpa sinyal.

---

### 3. Persona 2: Nelayan Tradisional (Aplikasi Mobile Android / PWA)

#### Profil Persona
- **Nama Persona**: Pak Basri (44 Tahun), Nakhoda Perahu Motor Katir 3 GT di Pesisir Cilacap.
- **Perangkat**: Smartphone Android dengan pelindung anti-air (*waterproof pouch*).
- **Tantangan**: Silau sinar matahari laut lepas, tangan basah, bahaya gelombang tinggi mendadak di malam hari.
- **Kebutuhan Utama**: Tahu jam berapa aman keluar muara dan pulang, serta koordinat titik kumpul ikan terdekat.

#### Wireframe & Tata Letak Antarmuka Nelayan (Outdoor High-Contrast)

```
+---------------------------------------------------------+
|  ⚓ WeatherGuard Laut                     [ 🆘 DARURAT ]|
|  📍 Pelabuhan Teluk Penyu, Cilacap                      |
+---------------------------------------------------------+
|                                                         |
|  +---------------------------------------------------+  |
|  |  STATUS KESELAMATAN BERLAYAR (KAPAL < 5 GT):      |  |
|  |                                                   |  |
|  |             🟢 STATUS: AMAN MELAUT                 |  |
|  |                                                   |  |
|  |  🌊 Gelombang: 0.8 meter (Tenang)                 |  |
|  |  💨 Angin: 10 knot (Barat Daya)                   |  |
|  |  ⏰ Jendela Aman: Hari Ini 15.00 s/d Besok 09.00  |  |
|  +---------------------------------------------------+  |
|                                                         |
|  🐟 ZONA POTENSI TANGKAPAN IKAN (ZPPI) HARI INI:        |
|  +---------------------------------------------------+  |
|  |  Spot 1 (Tuna/Tongkol): 8.4 Mil Arah Selatan      |  |
|  |  Suhu Air: 28.5°C | Klorofil: Melimpah (Subur)   |  |
|  |  [ 🧭 Mulai Pandu Navigasi Kompas ke Lokasi ]     |  |
|  +---------------------------------------------------+  |
|                                                         |
|  ⚠️ PERINGATAN GELOMBANG PASANG / BADAI:                |
|  +---------------------------------------------------+  |
|  |  Minggu Malam: Gelombang naik ke 2.8 meter (BAHAYA)|  |
|  |  Rekomendasi: Semua perahu wajib sandar sblm 18.00|  |
|  +---------------------------------------------------+  |
|                                                         |
|  [ 📻 Panggil Radio Nelayan ]      [ 🧭 Peta Offline GPS ]|
+---------------------------------------------------------+
```

#### Alur Pengguna (User Flow) Nelayan
1. Nelayan membuka aplikasi saat memeriksa mesin di dermaga pendaratan ikan.
2. Membaca **Lampu Status Berlayar**: Jika Hijau, nelayan mengecek estimasi jam gelombang naik.
3. Menekan tombol **"Mulai Pandu Navigasi"** untuk mengarahkan haluan perahu ke koordinat ZPPI (Klorofil tinggi).
4. Jika terjadi mesin mati di tengah laut atau badai tiba-tiba, nelayan menekan tombol **"🆘 DARURAT"** selama 3 detik untuk memancarkan SMS koordinat GPS darurat ke Basarnas dan rukun nelayan setempat.

---

### 4. Persona 3: Petugas Pusdalops BPBD (Web Command Center Dashboard)

#### Profil Persona
- **Nama Persona**: Ibu Rina (32 Tahun), Operator Pusdalops Penanggulangan Bencana BPBD Provinsi.
- **Perangkat**: Workstation Desktop 3 Monitor (Layar 4K/FHD 27"), Koneksi Internet Fiber Optik Stabil.
- **Tantangan**: Memantau ratusan kecamatan sekaligus, memilah informasi hoaks, dan mempercepat *lead time* evakuasi sebelum banjir datang.
- **Kebutuhan Utama**: Peta spasial GIS interaktif multi-layer, deteksi hujan ekstrem $>50\text{ mm}$, dan tombol otomatis siaran peringatan dini ke publik/aparat desa.

#### Wireframe Antarmuka BPBD Command Center (Web Desktop)

```
+---------------------------------------------------------------------------------------------------------------+
|  🛡️ WeatherGuard BPBD Command Center | Wilayah: DKI Jakarta & Jawa Barat | [Status: Normal-Siaga] [16:26 WIB]  |
+---------------------------------------------------------------------------------------------------------------+
| [Layer Peta]           | [PETA GEOSPASIAL INTERAKTIF MULTI-LAYER (Leaflet / MapLibre)]      | [PANEL ALARM AKTIF]      |
| [X] Curah Hujan (mm)   |                                                                    | 🚨 3 PERINGATAN DINI    |
| [X] Radar Himawari-9   |      [Polygon DAS Ciliwung: KUNING (Hujan 38 mm/j)]                |                          |
| [ ] Kecepatan Angin    |      [Titik Karawang: MERAH (Hujan Ekstrem 62 mm)]                 | 1. Karawang (Kec. Rengas)|
| [ ] Indeks Genangan    |                                                                    |    Hujan: 62 mm/hari     |
| [ ] Lokasi Posko Pompa |                 📍 Pintu Air Manggarai: Normal (650 cm)            |    Potensi: Genangan 40cm|
| [ ] Batas Administrasi |                                                                    |    [📲 Kirim WA Blast]   |
| ---------------------- |                                                                    | ------------------------ |
| [Filter Wilayah]       |                                                                    | 2. Pesisir Indramayu     |
| [ Kab. Karawang    v ] |                                                                    |    Angin Gust: 64 km/jam |
| [ Kab. Indramayu   v ] |                                                                    |    [📲 Kirim Notif Laut] |
+---------------------------------------------------------------------------------------------------------------+
| 📊 ANALISIS TREN WAKTU & TIMELINE KESIAPSIAGAAN (10 HARI KE DEPAN)                                            |
| [Grafik Prediksi Hujan Kumulatif vs Debit Sungai] | [Matriks Kesiapan 24 Kecamatan] | [Log Diseminasi Pesan] |
+---------------------------------------------------------------------------------------------------------------+
```

#### Alur Pengguna (User Flow) Petugas BPBD
1. Dashboard berjalan 24 jam nonstop di layar video wall monitor Command Center.
2. Ketika sistem AI mendeteksi sel badai dengan curah hujan $>50\text{ mm/hari}$ di suatu kecamatan, polygon wilayah tersebut otomatis menyala berkedip merah disertai bunyi alarm audio.
3. Petugas mengklik polygon wilayah terdampak untuk melihat detail estimasi jumlah warga terdampak, kapasitas saluran pembuang, dan draf pesan darurat.
4. Petugas menekan tombol **"Kirim WA Blast & Sirene"**; sistem secara otomatis mendistribusikan notifikasi darurat dalam waktu $< 10\text{ detik}$ ke nomor WhatsApp Camat, Kepala Desa, dan relawan bencana setempat.
