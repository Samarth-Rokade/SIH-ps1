import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useChartColors } from "../../theme/chartColors";
import { RISK_COLORS } from "../../utils/riskColors";

export default function RiskTrendChart({ points }) {
  const colors = useChartColors();

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={points} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
          <XAxis dataKey="month" stroke={colors.axis} fontSize={12} />
          <YAxis stroke={colors.axis} fontSize={12} />
          <Tooltip
            contentStyle={{
              background: colors.tooltipBg,
              border: `1px solid ${colors.tooltipBorder}`,
              borderRadius: 8,
            }}
          />
          <Legend />
          {["critical", "high", "medium", "low"].map((level) => (
            <Line
              key={level}
              type="monotone"
              dataKey={level}
              stroke={RISK_COLORS[level]}
              strokeWidth={2}
              dot={false}
              name={level[0].toUpperCase() + level.slice(1)}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
