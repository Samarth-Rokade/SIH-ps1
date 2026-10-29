import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useChartColors } from "../../theme/chartColors";
import { RISK_COLORS, riskLevelFromScore } from "../../utils/riskColors";

const ROW_HEIGHT = 28;

/** Horizontal bars of `valueKey` per `labelKey` row, coloured by risk level of the value. */
export default function HorizontalRiskBars({ rows, labelKey, valueKey = "average_risk", valueLabel = "Average Risk" }) {
  const colors = useChartColors();

  return (
    <div style={{ height: Math.max(160, rows.length * ROW_HEIGHT + 40) }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows} layout="vertical" margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} horizontal={false} />
          <XAxis type="number" domain={[0, 100]} stroke={colors.axis} fontSize={12} />
          <YAxis
            type="category"
            dataKey={labelKey}
            width={190}
            stroke={colors.axis}
            fontSize={11}
            tickFormatter={(v) => (v.length > 28 ? `${v.slice(0, 27)}…` : v)}
          />
          <Tooltip
            cursor={{ fill: colors.grid, fillOpacity: 0.3 }}
            contentStyle={{ background: colors.tooltipBg, border: `1px solid ${colors.tooltipBorder}`, borderRadius: 8 }}
            formatter={(v) => [v, valueLabel]}
          />
          <Bar dataKey={valueKey} radius={[0, 4, 4, 0]}>
            {rows.map((r) => (
              <Cell key={r[labelKey]} fill={RISK_COLORS[riskLevelFromScore(r[valueKey])]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
