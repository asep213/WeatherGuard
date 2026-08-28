"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { Activity, Anchor, Bell, CloudRain, Droplets, Leaf, Map, ShieldCheck, Ship, Sun, Trees, Waves, Wind } from "lucide-react";

type Mode = "farmer" | "maritime" | "bpbd" | "map";
type Forecast = { date: string; temperature_c: number; temp_min_c: number; temp_max_c: number; rain_accum_24h_mm: number; wind_speed_kmh: number; wave_height_m: number; humidity_pct: number; uv_index: number };
type Location = { name: string; detail: string; lat: number; lon: number; elevation: number };
type SearchResult = { name: string; latitude: number; longitude: number; admin1?: string; country?: string };
const WeatherMap = dynamic(() => import("../components/WeatherMap"), { ssr: false });

const locations = [
  { name: "Kota Tebing Tinggi", detail: "Sumatera Utara • DAS Sungai Padang", lat: 3.3285, lon: 99.1625, elevation: 26 },
  { name: "Kab. Karawang", detail: "Jawa Barat • Telagasari", lat: -6.302, lon: 107.408, elevation: 25 },
  { name: "Pelabuhan Teluk Penyu", detail: "Cilacap • Samudra Hindia", lat: -7.728, lon: 109.015, elevation: 5 },
];

const fallback: Forecast[] = [5, 0, 18, 62, 8, 0, 2].map((rain, index) => ({ date: `2026-08-${28 + index}`, temperature_c: 28.5 - index * .2, temp_min_c: 23, temp_max_c: 32 - index * .2, rain_accum_24h_mm: rain, wind_speed_kmh: 12 + (index % 3) * 4.5, wave_height_m: .8 + rain / 40, humidity_pct: 72 + rain * .3, uv_index: rain < 10 ? 8.5 : 3.2 }));

const modeConfig: Record<Mode, { label: string; title: string; icon: typeof Leaf }> = {
  farmer: { label: "Petani", title: "WeatherGuard Tani", icon: Leaf },
  maritime: { label: "Nelayan", title: "WeatherGuard Laut", icon: Anchor },
  bpbd: { label: "BPBD", title: "Command Center", icon: ShieldCheck },
  map: { label: "Peta", title: "Peta Spasial", icon: Map },
};

export default function Home() {
  const [mode, setMode] = useState<Mode>("farmer");
  const [locationIndex, setLocationIndex] = useState(0);
  const [forecast, setForecast] = useState<Forecast[]>(fallback);
  const [connected, setConnected] = useState(false);
  const [mapPoint, setMapPoint] = useState<Location | null>(null);
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [notice, setNotice] = useState("");

  const selectedLocation = locations[locationIndex >= 0 ? locationIndex : 0];
  const location = mapPoint || selectedLocation;
  const config = modeConfig[mode];
  const Icon = config.icon;
  const today = forecast[0];
  const peakRain = Math.max(...forecast.map((day) => day.rain_accum_24h_mm));
  const peakWind = Math.max(...forecast.map((day) => day.wind_speed_kmh));

  useEffect(() => {
    const api = process.env.NEXT_PUBLIC_API_URL;
    const url = api
      ? `${api}/forecast/point?lat=${location.lat}&lon=${location.lon}&name=${encodeURIComponent(location.name)}&elevation_m=${location.elevation}&days=7`
      : `https://api.open-meteo.com/v1/forecast?latitude=${location.lat}&longitude=${location.lon}&daily=temperature_2m_mean,temperature_2m_min,temperature_2m_max,precipitation_sum,wind_speed_10m_max,relative_humidity_2m_mean,uv_index_max&timezone=Asia%2FJakarta&forecast_days=7`;
    const weatherRequest = fetch(url).then((response) => { if (!response.ok) throw new Error("Weather provider offline"); return response.json(); });
    const marineRequest = mode === "maritime" && !api
      ? fetch(`https://marine-api.open-meteo.com/v1/marine?latitude=${location.lat}&longitude=${location.lon}&daily=wave_height_max&timezone=Asia%2FJakarta&forecast_days=7`).then((response) => { if (!response.ok) throw new Error("Marine provider offline"); return response.json(); })
      : Promise.resolve(null);
    Promise.all([weatherRequest, marineRequest])
      .then(([data, marine]) => {
        if (api) setForecast(data.daily_forecasts);
        else setForecast(data.daily.time.map((date: string, index: number) => ({ date, temperature_c: data.daily.temperature_2m_mean[index], temp_min_c: data.daily.temperature_2m_min[index], temp_max_c: data.daily.temperature_2m_max[index], rain_accum_24h_mm: data.daily.precipitation_sum[index], wind_speed_kmh: data.daily.wind_speed_10m_max[index], wave_height_m: marine?.daily?.wave_height_max?.[index] ?? 0, humidity_pct: data.daily.relative_humidity_2m_mean[index], uv_index: data.daily.uv_index_max[index] })));
        setConnected(true);
      })
      .catch(() => setConnected(false));
  }, [location, mode, refreshKey]);

  const searchLocations = () => {
    if (query.trim().length < 2) return;
    setSearching(true);
    fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(query.trim())}&count=10&language=id&format=json`)
      .then((response) => response.json())
      .then((data) => setSearchResults((data.results || []).filter((result: SearchResult) => result.country === "Indonesia")))
      .finally(() => setSearching(false));
  };

  const chooseSearchResult = (result: SearchResult) => {
    setMapPoint({ name: result.name, detail: `${result.admin1 || "Indonesia"} • data Open-Meteo`, lat: result.latitude, lon: result.longitude, elevation: 25 });
    setLocationIndex(-1);
    setSearchResults([]);
    setQuery("");
  };

  const pickMapPoint = (lat: number, lon: number) => {
    setMapPoint({ name: "Titik pilihan peta", detail: `${lat.toFixed(3)}, ${lon.toFixed(3)} • Open-Meteo`, lat, lon, elevation: 25 });
    setLocationIndex(-1);
  };
  const activeLocation = location;

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark"><ShieldCheck size={21} /></div><span>WeatherGuard</span></div>
        <div className="sidebar-label">Workspace</div>
        <nav className="nav">
          <NavButton active={mode === "farmer"} onClick={() => setMode("farmer")} icon={<Leaf size={18} />} text="Pertanian" />
          <NavButton active={mode === "maritime"} onClick={() => setMode("maritime")} icon={<Anchor size={18} />} text="Maritim" />
          <NavButton active={mode === "bpbd"} onClick={() => setMode("bpbd")} icon={<ShieldCheck size={18} />} text="Command Center" />
          <NavButton active={mode === "map"} onClick={() => setMode("map")} icon={<Map size={18} />} text="Peta Spasial" />
        </nav>
        <div className="sidebar-foot">Impact-based weather intelligence<br /><strong>v1.0 • Indonesia</strong></div>
      </aside>
      <main className="main">
        <header className="topbar">
          <div><p className="eyebrow">Dashboard / {config.label}</p><h1>{config.title}</h1></div>
          <div className="top-actions"><span className="sync"><i className="dot" /> {connected ? "API tersambung" : "Mode demo aktif"}</span><button className="ghost" aria-label="Notifikasi" onClick={() => setNotice("Tidak ada peringatan baru untuk lokasi ini.")}><Bell size={17} /></button></div>
        </header>
        {notice && <div className="notice" role="status">{notice}<button onClick={() => setNotice("")} aria-label="Tutup notifikasi">×</button></div>}

        <section className="hero">
          <div><p className="eyebrow">Pusat keputusan cuaca</p><h2>Cuaca yang diterjemahkan menjadi tindakan.</h2><p>Pantau risiko, temukan jendela aman, dan bergerak lebih cepat dengan prakiraan berbasis dampak.</p></div>
          <div className="location"><label>Lokasi pemantauan</label><select value={locationIndex >= 0 ? locationIndex : "map"} onChange={(event) => { if (event.target.value !== "map") { setMapPoint(null); setLocationIndex(Number(event.target.value)); } }}>{mapPoint && <option value="map">{mapPoint.name}</option>}{locations.map((item, index) => <option value={index} key={item.name}>{item.name}</option>)}</select><small>{activeLocation.detail}</small><div className="search-row"><input value={query} onChange={(event) => setQuery(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") searchLocations(); }} placeholder="Cari kota atau kabupaten..." aria-label="Cari daerah" /><button className="search-button" onClick={searchLocations}>{searching ? "..." : "Cari"}</button></div>{searchResults.length > 0 && <div className="search-results">{searchResults.map((result) => <button key={`${result.name}-${result.latitude}`} onClick={() => chooseSearchResult(result)}>{result.name}<small>{result.admin1 || result.country}</small></button>)}</div>}</div>
        </section>

        {mode === "map" ? <MapPanel locations={locations} onPick={pickMapPoint} /> : <>
          <section className="metrics">
            <Metric icon={<CloudRain size={18} />} label="Hujan hari ini" value={`${today.rain_accum_24h_mm.toFixed(1)} mm`} note={today.rain_accum_24h_mm > 50 ? "Risiko tinggi" : "Kondisi terkendali"} />
            <Metric icon={<Sun size={18} />} label="Suhu rata-rata" value={`${today.temperature_c.toFixed(1)}°C`} note={`Maks ${today.temp_max_c.toFixed(1)}°C`} />
            <Metric icon={<Wind size={18} />} label="Angin maksimum" value={`${peakWind.toFixed(1)} km/j`} note="Pantau hembusan" />
            <Metric icon={<Activity size={18} />} label="Sumber data" value="Live" note="Open-Meteo" />
          </section>
          <section className="content-grid">
            <div className="panel"><div className="panel-head"><div><h2>Prakiraan 7 hari</h2><span className="panel-subtitle">Open-Meteo Weather + Marine • live</span></div><button className="ghost" aria-label="Segarkan data" onClick={() => setRefreshKey((value) => value + 1)}>↻</button></div><ForecastTable forecast={forecast} mode={mode} /></div>
            <RiskPanel mode={mode} peakRain={peakRain} today={today} />
            <ActionPanel mode={mode} today={today} />
            <div className="panel"><div className="panel-head"><div><h2>Peta risiko wilayah</h2><span className="panel-subtitle">Radar hujan live • klik untuk forecast titik</span></div><Map size={18} color="#087e8b" /></div><MapPanel locations={[activeLocation]} onPick={pickMapPoint} compact /></div>
          </section>
        </>}
      </main>
    </div>
  );
}

function NavButton({ active, onClick, icon, text }: { active: boolean; onClick: () => void; icon: React.ReactNode; text: string }) { return <button className={active ? "active" : ""} onClick={onClick}>{icon}<span>{text}</span></button>; }
function Metric({ icon, label, value, note }: { icon: React.ReactNode; label: string; value: string; note: string }) { return <div className="metric"><span className="metric-label">{icon} &nbsp;{label}</span><strong className="metric-value">{value}</strong><span className="metric-note">{note}</span></div>; }
function ForecastTable({ forecast, mode }: { forecast: Forecast[]; mode: Mode }) { return <div className="forecast-list"><div className="forecast-row"><span>Hari</span><span>Kondisi</span><span>Hujan</span><span>Status</span></div>{forecast.map((day, index) => { const bad = day.rain_accum_24h_mm > 50; const maritime = mode === "maritime"; return <div className="forecast-row" key={day.date}><strong>{index === 0 ? "Hari ini" : `H+${index}`}<small> · {day.date.slice(5)}</small></strong><span>{maritime ? `${day.wave_height_m.toFixed(1)} m gelombang` : `${day.temperature_c.toFixed(1)}°C`}</span><span>{day.rain_accum_24h_mm.toFixed(1)} mm</span><span className={`status ${bad ? "bad" : day.rain_accum_24h_mm > 15 ? "warn" : "good"}`}>{bad ? "Waspada" : day.rain_accum_24h_mm > 15 ? "Pantau" : "Aman"}</span></div>; })}</div>; }
function RiskPanel({ mode, peakRain, today }: { mode: Mode; peakRain: number; today: Forecast }) { const maritime = mode === "maritime"; const score = maritime ? (today.wave_height_m < 1.8 ? "Aman" : "Siaga") : peakRain > 50 ? "Siaga 2" : "Siaga 3"; return <div className="panel risk-panel"><div className="panel-head"><div><h2>Ringkasan risiko</h2><span className="panel-subtitle">Analisis WeatherGuard</span></div><Droplets size={19} /></div><div className="risk-score"><div className="score-ring">{maritime ? "72" : peakRain > 50 ? "58" : "82"}</div><div className="risk-copy"><strong>{score}</strong><span>{maritime ? "Jendela aman terbatas" : "Kesiapsiagaan wilayah"}</span></div></div><div className="risk-list"><div className="risk-item"><span>Curah hujan puncak</span><b>{peakRain.toFixed(1)} mm</b></div><div className="risk-item"><span>Kelembaban</span><b>{today.humidity_pct.toFixed(0)}%</b></div><div className="risk-item"><span>Rekomendasi</span><b>{maritime ? "Dekat pantai" : "Pantau DAS"}</b></div></div></div>; }
function ActionPanel({ mode, today }: { mode: Mode; today: Forecast }) { const maritime = mode === "maritime"; const bpbd = mode === "bpbd"; return <div className="panel"><div className="panel-head"><div><h2>Aksi yang disarankan</h2><span className="panel-subtitle">Berdasarkan kondisi hari ini</span></div><Trees size={18} color="#238b72" /></div><div className="actions"><div className="action"><span className="action-icon">{maritime ? <Ship size={19} /> : bpbd ? <Bell size={19} /> : <Leaf size={19} />}</span><div><h3>{maritime ? "Batasi radius pelayaran" : bpbd ? "Siagakan posko DAS" : today.rain_accum_24h_mm > 15 ? "Tunda penyemprotan" : "Jendela semprot optimal"}</h3><p>{maritime ? "Gelombang dan angin perlu dipantau sebelum berangkat." : bpbd ? "Pantau titik genangan dan siapkan notifikasi warga." : "Gunakan prakiraan ini sebagai panduan operasional lapangan."}</p></div></div><div className="action"><span className="action-icon"><Waves size={19} /></span><div><h3>Perbarui keputusan</h3><p>Data berikutnya tersedia setelah sinkronisasi provider cuaca.</p></div></div></div></div>; }
function MapPanel({ locations, compact = false, onPick }: { locations: Location[]; compact?: boolean; onPick?: (lat: number, lon: number) => void }) { return <div className={`panel ${compact ? "map-panel" : "wide"}`}><div className="panel-head"><div><h2>{compact ? "" : "Peta interaktif"}</h2><span className="panel-subtitle">{compact ? "" : "OpenStreetMap + RainViewer radar • klik lokasi"}</span></div></div><div className="map"><WeatherMap locations={locations} onPick={onPick} /><span className="map-label">Radar hujan live • OpenStreetMap / RainViewer</span></div></div>; }