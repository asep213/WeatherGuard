"use client";

import "leaflet/dist/leaflet.css";
import { useEffect, useState } from "react";
import { CircleMarker, MapContainer, Popup, TileLayer, useMap, useMapEvents } from "react-leaflet";

type MapLocation = { name: string; lat: number; lon: number };

function MapBounds({ locations }: { locations: MapLocation[] }) {
  const map = useMap();
  useEffect(() => {
    if (locations.length === 1) map.flyTo([locations[0].lat, locations[0].lon], 9, { duration: 0.7 });
  }, [locations, map]);
  return null;
}

function ClickHandler({ onPick }: { onPick?: (lat: number, lon: number) => void }) {
  useMapEvents({ click: (event) => onPick?.(event.latlng.lat, event.latlng.lng) });
  return null;
}

function RainRadarLayer() {
  const [tileUrl, setTileUrl] = useState<string | null>(null);

  useEffect(() => {
    fetch("https://api.rainviewer.com/public/weather-maps.json")
      .then((response) => response.json())
      .then((data) => {
        const frame = data?.radar?.past?.at(-1);
        if (frame?.path) setTileUrl(`https://tilecache.rainviewer.com${frame.path}/256/{z}/{x}/{y}/2/1_1.png`);
      })
      .catch(() => setTileUrl(null));
  }, []);

  return tileUrl ? <TileLayer url={tileUrl} opacity={0.55} attribution='Radar &copy; <a href="https://rainviewer.com">RainViewer</a>' /> : null;
}

export default function WeatherMap({ locations, onPick }: { locations: MapLocation[]; onPick?: (lat: number, lon: number) => void }) {
  return (
    <MapContainer center={[-2.5, 118]} zoom={5} minZoom={4} maxZoom={14} scrollWheelZoom className="leaflet-map">
      <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <RainRadarLayer />
      <MapBounds locations={locations} />
      <ClickHandler onPick={onPick} />
      {locations.map((item) => <CircleMarker key={`${item.name}-${item.lat}`} center={[item.lat, item.lon]} radius={9} pathOptions={{ color: "#fff", weight: 3, fillColor: "#d1495b", fillOpacity: 1 }}><Popup>{item.name}<br />Klik peta untuk mengambil cuaca di titik mana pun.</Popup></CircleMarker>)}
    </MapContainer>
  );
}