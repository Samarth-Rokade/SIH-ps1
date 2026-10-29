import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useChartColors } from "../../theme/chartColors";
import { RISK_COLORS, RISK_LEVELS, riskLevelFromScore } from "../../utils/riskColors";

/*
 * Canvas scatter for the risk radar.
 *
 * The previous Recharts version created one SVG node per project (thousands of
 * them, each with its own animation and hit-testing), which made the page lag.
 * Drawing every point onto a single <canvas> makes the cost ~constant, and a
 * coarse spatial grid keeps hover/click hit-testing O(1) instead of scanning
 * every point on each mouse move.
 */

const MARGIN = { top: 12, right: 20, bottom: 44, left: 52 };
const HEIGHT = 420;
const TICKS = [0, 20, 40, 60, 80, 100];
const THRESHOLD = 50; // matches the "Project Clusters" quadrant split on the page
const HIT_RADIUS = 9; // px
const GRID_CELL = 12; // px, spatial index cell size
const DRAW_ORDER = [...RISK_LEVELS].reverse(); // low first so critical sits on top

function pointRadius(score) {
  return 2 + (score / 100) * 3;
}

export default function RiskRadarScatter({ points, onSelect }) {
  const colors = useChartColors();
  const containerRef = useRef(null);
  const baseRef = useRef(null);
  const overlayRef = useRef(null);
  const [width, setWidth] = useState(0);
  const [hover, setHover] = useState(null);

  // Precompute plotted data once per dataset (not per render / mouse move).
  const prepared = useMemo(
    () =>
      points.map((p) => ({
        ...p,
        x: p.cost_risk * 100,
        y: p.delay_probability * 100,
        level: riskLevelFromScore(p.risk_score),
      })),
    [points]
  );

  const counts = useMemo(() => {
    const c = { critical: 0, high: 0, medium: 0, low: 0 };
    for (const p of prepared) c[p.level]++;
    return c;
  }, [prepared]);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return undefined;
    const observer = new ResizeObserver(([entry]) => setWidth(Math.floor(entry.contentRect.width)));
    observer.observe(el);
    setWidth(Math.floor(el.getBoundingClientRect().width));
    return () => observer.disconnect();
  }, []);

  const plot = useMemo(
    () => ({
      w: Math.max(0, width - MARGIN.left - MARGIN.right),
      h: HEIGHT - MARGIN.top - MARGIN.bottom,
    }),
    [width]
  );
  const toPx = useCallback(
    (x, y) => [MARGIN.left + (x / 100) * plot.w, MARGIN.top + (1 - y / 100) * plot.h],
    [plot]
  );

  // Spatial hash of pixel positions -> point indexes, rebuilt only when data/size change.
  const spatialIndex = useMemo(() => {
    const grid = new Map();
    prepared.forEach((p, i) => {
      const [px, py] = toPx(p.x, p.y);
      const key = `${Math.floor(px / GRID_CELL)},${Math.floor(py / GRID_CELL)}`;
      const bucket = grid.get(key);
      if (bucket) bucket.push(i);
      else grid.set(key, [i]);
    });
    return grid;
  }, [prepared, toPx]);

  const setupCanvas = useCallback(
    (canvas) => {
      const dpr = window.devicePixelRatio || 1;
      canvas.width = width * dpr;
      canvas.height = HEIGHT * dpr;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${HEIGHT}px`;
      const ctx = canvas.getContext("2d");
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      return ctx;
    },
    [width]
  );

  // Static layer: grid, axes, quadrant guides, points.
  useEffect(() => {
    const canvas = baseRef.current;
    if (!canvas || width === 0) return;
    const ctx = setupCanvas(canvas);
    ctx.clearRect(0, 0, width, HEIGHT);

    ctx.font = "12px system-ui, sans-serif";
    ctx.fillStyle = colors.axis;
    ctx.strokeStyle = colors.grid;
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 3]);
    ctx.textAlign = "center";
    for (const t of TICKS) {
      const [gx] = toPx(t, 0);
      const [, gy] = toPx(0, t);
      ctx.beginPath();
      ctx.moveTo(gx, MARGIN.top);
      ctx.lineTo(gx, MARGIN.top + plot.h);
      ctx.moveTo(MARGIN.left, gy);
      ctx.lineTo(MARGIN.left + plot.w, gy);
      ctx.stroke();
      ctx.fillText(`${t}%`, gx, MARGIN.top + plot.h + 16);
      ctx.textAlign = "right";
      ctx.fillText(`${t}%`, MARGIN.left - 8, gy + 4);
      ctx.textAlign = "center";
    }
    ctx.setLineDash([]);

    // Quadrant guides at 50/50.
    ctx.strokeStyle = colors.axis;
    ctx.globalAlpha = 0.45;
    const [tx, ty] = toPx(THRESHOLD, THRESHOLD);
    ctx.beginPath();
    ctx.moveTo(tx, MARGIN.top);
    ctx.lineTo(tx, MARGIN.top + plot.h);
    ctx.moveTo(MARGIN.left, ty);
    ctx.lineTo(MARGIN.left + plot.w, ty);
    ctx.stroke();
    ctx.globalAlpha = 1;

    ctx.fillStyle = colors.axis;
    ctx.fillText("Cost Overrun Risk (%)", MARGIN.left + plot.w / 2, HEIGHT - 8);
    ctx.save();
    ctx.translate(14, MARGIN.top + plot.h / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText("Delay Probability (%)", 0, 0);
    ctx.restore();

    ctx.globalAlpha = 0.7;
    for (const level of DRAW_ORDER) {
      ctx.fillStyle = RISK_COLORS[level];
      ctx.beginPath();
      for (const p of prepared) {
        if (p.level !== level) continue;
        const [px, py] = toPx(p.x, p.y);
        const r = pointRadius(p.risk_score);
        ctx.moveTo(px + r, py);
        ctx.arc(px, py, r, 0, Math.PI * 2);
      }
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }, [prepared, colors, width, plot, toPx, setupCanvas]);

  // Overlay layer: just the hovered point's highlight ring (cheap to redraw per mouse move).
  useEffect(() => {
    const canvas = overlayRef.current;
    if (!canvas || width === 0) return;
    const ctx = setupCanvas(canvas);
    ctx.clearRect(0, 0, width, HEIGHT);
    if (!hover) return;
    const [px, py] = toPx(hover.point.x, hover.point.y);
    ctx.lineWidth = 2;
    ctx.strokeStyle = colors.axis;
    ctx.beginPath();
    ctx.arc(px, py, pointRadius(hover.point.risk_score) + 3, 0, Math.PI * 2);
    ctx.stroke();
  }, [hover, width, colors, toPx, setupCanvas]);

  function findNearest(mx, my) {
    const cx = Math.floor(mx / GRID_CELL);
    const cy = Math.floor(my / GRID_CELL);
    let best = null;
    let bestDist = HIT_RADIUS * HIT_RADIUS;
    for (let dx = -1; dx <= 1; dx++) {
      for (let dy = -1; dy <= 1; dy++) {
        for (const i of spatialIndex.get(`${cx + dx},${cy + dy}`) ?? []) {
          const [px, py] = toPx(prepared[i].x, prepared[i].y);
          const dist = (px - mx) ** 2 + (py - my) ** 2;
          // On ties prefer the higher-risk point, which is drawn on top.
          if (dist < bestDist || (dist === bestDist && best && prepared[i].risk_score > best.risk_score)) {
            best = prepared[i];
            bestDist = dist;
          }
        }
      }
    }
    return best;
  }

  function handleMove(e) {
    const rect = e.currentTarget.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const nearest = findNearest(mx, my);
    setHover((prev) => {
      if (!nearest) return null;
      if (prev?.point === nearest) return prev;
      return { point: nearest, mx, my };
    });
  }

  return (
    <div>
      <div className="mb-2 flex flex-wrap items-center gap-4 text-xs text-text-muted">
        {RISK_LEVELS.map((level) => (
          <span key={level} className="flex items-center gap-1.5 capitalize">
            <span className="h-2.5 w-2.5 rounded-full" style={{ background: RISK_COLORS[level] }} />
            {level} ({counts[level].toLocaleString("en-IN")})
          </span>
        ))}
        <span className="ml-auto">{prepared.length.toLocaleString("en-IN")} projects plotted</span>
      </div>

      <div ref={containerRef} className="relative w-full" style={{ height: HEIGHT }}>
        <canvas ref={baseRef} className="absolute left-0 top-0" />
        <canvas
          ref={overlayRef}
          className="absolute left-0 top-0"
          style={{ cursor: hover ? "pointer" : "default" }}
          onMouseMove={handleMove}
          onMouseLeave={() => setHover(null)}
          onClick={() => hover && onSelect?.(hover.point.project_id)}
        />
        {hover && (
          <div
            className="pointer-events-none absolute z-10 max-w-xs rounded-lg border border-border bg-surface p-3 text-xs shadow-lg"
            style={{
              left: Math.min(hover.mx + 14, Math.max(0, width - 230)),
              top: Math.max(0, hover.my - 70),
            }}
          >
            <div className="mb-1 font-semibold text-text">{hover.point.project_name}</div>
            <div className="text-text-muted">Risk Score: {hover.point.risk_score}</div>
            <div className="text-text-muted">Delay Prob.: {Math.round(hover.point.y)}%</div>
            <div className="text-text-muted">Cost Risk: {Math.round(hover.point.x)}%</div>
            <div className="mt-1 text-text-muted">Click to open project</div>
          </div>
        )}
      </div>
    </div>
  );
}
