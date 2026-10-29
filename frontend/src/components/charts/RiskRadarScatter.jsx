import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import { useChartColors } from "../../theme/chartColors";
import { RISK_COLORS, RISK_LEVELS, riskLevelFromScore } from "../../utils/riskColors";

export default function RiskRadarScatter({ points, onSelect }) {
  const colors = useChartColors();
  const byLevel = RISK_LEVELS.map((level) => ({
    level,
    data: points
      .filter((p) => riskLevelFromScore(p.risk_score) === level)
      .map((p) => ({
        x: Math.round(p.cost_risk * 100),
        y: Math.round(p.delay_probability * 100),
        z: p.risk_score,
        ...p,
      })),
  }));

  return (
    <div className="h-[420px]">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
          <XAxis
            type="number"
            dataKey="x"
            name="Cost Overrun Risk"
            unit="%"
            domain={[0, 100]}
            stroke={colors.axis}
            fontSize={12}
            label={{ value: "Cost Overrun Risk (%)", position: "insideBottom", offset: -5, fill: colors.axis }}
          />
          <YAxis
            type="number"
            dataKey="y"
            name="Delay Probability"
            unit="%"
            domain={[0, 100]}
            stroke={colors.axis}
            fontSize={12}
            label={{ value: "Delay Probability (%)", angle: -90, position: "insideLeft", fill: colors.axis }}
          />
          <ZAxis type="number" dataKey="z" range={[40, 300]} />
          <Tooltip
            cursor={{ strokeDasharray: "3 3" }}
            contentStyle={{ background: colors.tooltipBg, border: `1px solid ${colors.tooltipBorder}`, borderRadius: 8 }}
            content={({ payload }) => {
              if (!payload?.length) return null;
              const p = payload[0].payload;
              return (
                <div className="rounded-lg border border-border bg-surface p-3 text-xs shadow-lg">
                  <div className="mb-1 font-semibold text-text">{p.project_name}</div>
                  <div className="text-text-muted">Risk Score: {p.risk_score}</div>
                  <div className="text-text-muted">Delay Prob.: {p.y}%</div>
                  <div className="text-text-muted">Cost Risk: {p.x}%</div>
                </div>
              );
            }}
          />
          {byLevel.map(({ level, data }) => (
            <Scatter
              key={level}
              data={data}
              fill={RISK_COLORS[level]}
              fillOpacity={0.75}
              onClick={(p) => onSelect?.(p.project_id)}
              cursor="pointer"
            />
          ))}
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
