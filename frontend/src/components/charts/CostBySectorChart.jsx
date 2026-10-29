import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useChartColors } from "../../theme/chartColors";
import { formatCrore } from "../../utils/format";

const SERIES = [
  { key: "original_cost_crore", name: "Original", fill: "#64748b" },
  { key: "current_cost_crore", name: "Current", fill: "#3b82f6" },
  { key: "predicted_final_cost_crore", name: "Predicted Final", fill: "#f97316" },
];

export default function CostBySectorChart({ rows }) {
  const colors = useChartColors();

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows} margin={{ top: 5, right: 10, left: 10, bottom: 40 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
          <XAxis
            dataKey="sector"
            stroke={colors.axis}
            fontSize={11}
            interval={0}
            angle={-25}
            textAnchor="end"
            height={60}
            tickFormatter={(v) => (v.length > 16 ? `${v.slice(0, 15)}…` : v)}
          />
          <YAxis stroke={colors.axis} fontSize={12} tickFormatter={formatCrore} width={70} />
          <Tooltip
            cursor={{ fill: colors.grid, fillOpacity: 0.3 }}
            contentStyle={{ background: colors.tooltipBg, border: `1px solid ${colors.tooltipBorder}`, borderRadius: 8 }}
            formatter={(v) => `₹${v.toLocaleString("en-IN")} Cr`}
          />
          <Legend verticalAlign="top" />
          {SERIES.map((s) => (
            <Bar key={s.key} dataKey={s.key} name={s.name} fill={s.fill} radius={[3, 3, 0, 0]} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
