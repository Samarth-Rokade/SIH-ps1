import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useChartColors } from "../../theme/chartColors";

export default function ProgressChart({ points }) {
  const colors = useChartColors();
  return (
    <div className="h-60">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={points} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
          <XAxis dataKey="month" stroke={colors.axis} fontSize={11} />
          <YAxis domain={[0, 100]} unit="%" stroke={colors.axis} fontSize={11} />
          <Tooltip
            contentStyle={{ background: colors.tooltipBg, border: `1px solid ${colors.tooltipBorder}`, borderRadius: 8 }}
            formatter={(value) => `${value}%`}
          />
          <Legend />
          <Line type="monotone" dataKey="planned_progress" name="Planned" stroke="#3b82f6" strokeWidth={2} strokeDasharray="5 4" dot={false} />
          <Line type="monotone" dataKey="actual_progress" name="Actual" stroke="#22c55e" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
