import { MapContainer, TileLayer, CircleMarker, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { states, type StateData, type StatusKey } from "../data/states";

export const INDIA_BOUNDS: [[number, number], [number, number]] = [
  [6.5, 68.0],
  [35.5, 97.5],
];

export const statusHex: Record<StatusKey, string> = {
  safe: "#4da8ff",
  semi: "#f0b34f",
  critical: "#f08a3c",
  over: "#b53e3e",
};

interface IndiaLeafletMapProps {
  onSelect?: (state: StateData) => void;
  selected?: string | null;
  visible?: StateData[];
}

export default function IndiaLeafletMap({ onSelect, selected, visible }: IndiaLeafletMapProps) {
  const shown = visible ?? states;

  return (
    <MapContainer
      bounds={INDIA_BOUNDS}
      maxBounds={INDIA_BOUNDS}
      maxBoundsViscosity={1}
      zoomSnap={0.25}
      minZoom={4}
      maxZoom={10}
      zoomControl={false}
      scrollWheelZoom
      style={{ height: "100%", width: "100%" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
      />
      {shown.map((s) => (
        <CircleMarker
          key={s.name}
          center={[s.lat, s.lng]}
          radius={selected === s.name ? 11 : 7}
          pathOptions={{
            color: statusHex[s.status],
            fillColor: statusHex[s.status],
            fillOpacity: 0.85,
            weight: 2,
          }}
          eventHandlers={{ click: () => onSelect?.(s) }}
        >
          <Tooltip direction="top" offset={[0, -6]}>
            <b>{s.name}</b> — {s.status === "over" ? "Over-Exploited" : s.status === "semi" ? "Semi-Critical" : s.status === "critical" ? "Critical" : "Safe"}
          </Tooltip>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
