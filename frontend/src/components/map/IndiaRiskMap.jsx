import "leaflet/dist/leaflet.css";
import { CircleMarker, MapContainer, Popup, TileLayer } from "react-leaflet";
import { RISK_COLORS } from "../../utils/riskColors";

const INDIA_CENTER = [22.35, 78.66];

export default function IndiaRiskMap({ points }) {
  return (
    <div className="h-[420px] overflow-hidden rounded-lg border border-border">
      <MapContainer
        center={INDIA_CENTER}
        zoom={4.5}
        preferCanvas
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {points.map((p) => (
          <CircleMarker
            key={p.project_id}
            center={[p.latitude, p.longitude]}
            radius={5}
            pathOptions={{
              color: RISK_COLORS[p.risk_level],
              fillColor: RISK_COLORS[p.risk_level],
              fillOpacity: 0.8,
              weight: 1,
            }}
          >
            <Popup>
              <div className="text-sm">
                <div className="font-semibold">{p.project_name}</div>
                <div>{p.state}</div>
                <div>
                  Risk: {p.risk_score} ({p.risk_level})
                </div>
                <div>Delay Probability: {Math.round(p.delay_probability * 100)}%</div>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}
