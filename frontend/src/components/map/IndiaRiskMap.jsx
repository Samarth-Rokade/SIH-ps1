import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useEffect, useMemo, useState } from "react";
import { MapContainer, TileLayer, useMap } from "react-leaflet";
import { RISK_COLORS, RISK_LEVELS } from "../../utils/riskColors";

const INDIA_CENTER = [22.35, 78.66];

/*
 * Draws every project as a Leaflet canvas circle marker, created imperatively
 * in one layer group. The earlier version rendered a React <CircleMarker> and a
 * <Popup> element per project (thousands of component instances), which was the
 * slow part; here popups are built lazily, only when one is opened.
 */
function MarkerLayer({ points }) {
  const map = useMap();

  useEffect(() => {
    const renderer = L.canvas({ padding: 0.5 });
    const group = L.layerGroup();
    for (const p of points) {
      const color = RISK_COLORS[p.risk_level];
      const marker = L.circleMarker([p.latitude, p.longitude], {
        renderer,
        radius: 5,
        color,
        fillColor: color,
        fillOpacity: 0.8,
        weight: 1,
      });
      marker.bindPopup(() => popupContent(p));
      group.addLayer(marker);
    }
    group.addTo(map);
    return () => {
      group.remove();
    };
  }, [map, points]);

  return null;
}

// Built with DOM nodes + textContent so project names are never interpreted as HTML.
function popupContent(p) {
  const root = document.createElement("div");
  root.style.fontSize = "13px";
  const lines = [
    [p.project_name, true],
    [p.state, false],
    [`Risk: ${p.risk_score} (${p.risk_level})`, false],
    [`Delay Probability: ${Math.round(p.delay_probability * 100)}%`, false],
  ];
  for (const [text, bold] of lines) {
    const div = document.createElement("div");
    div.textContent = text;
    if (bold) div.style.fontWeight = "600";
    root.appendChild(div);
  }
  const link = document.createElement("a");
  link.href = `/projects/${p.project_id}`;
  link.textContent = "Open project →";
  link.style.color = "#3b82f6";
  root.appendChild(link);
  return root;
}

export default function IndiaRiskMap({ points }) {
  const [visible, setVisible] = useState(() => new Set(RISK_LEVELS));

  const counts = useMemo(() => {
    const c = { critical: 0, high: 0, medium: 0, low: 0 };
    for (const p of points) c[p.risk_level]++;
    return c;
  }, [points]);

  // Low-risk markers draw first so the critical ones stay visible on top.
  const shown = useMemo(() => {
    const order = { low: 0, medium: 1, high: 2, critical: 3 };
    return points.filter((p) => visible.has(p.risk_level)).sort((a, b) => order[a.risk_level] - order[b.risk_level]);
  }, [points, visible]);

  function toggle(level) {
    setVisible((prev) => {
      const next = new Set(prev);
      if (next.has(level)) next.delete(level);
      else next.add(level);
      return next;
    });
  }

  return (
    <div>
      <div className="mb-2 flex flex-wrap items-center gap-2 text-xs">
        {RISK_LEVELS.map((level) => (
          <button
            key={level}
            onClick={() => toggle(level)}
            className={`flex items-center gap-1.5 rounded-full border border-border px-2.5 py-1 capitalize transition-opacity ${
              visible.has(level) ? "text-text" : "text-text-muted opacity-50"
            }`}
          >
            <span className="h-2.5 w-2.5 rounded-full" style={{ background: RISK_COLORS[level] }} />
            {level} ({counts[level]})
          </button>
        ))}
        <span className="ml-auto text-text-muted">{shown.length.toLocaleString("en-IN")} shown</span>
      </div>
      <div className="h-[420px] overflow-hidden rounded-lg border border-border">
        <MapContainer center={INDIA_CENTER} zoom={4.5} preferCanvas style={{ height: "100%", width: "100%" }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          <MarkerLayer points={shown} />
        </MapContainer>
      </div>
    </div>
  );
}
