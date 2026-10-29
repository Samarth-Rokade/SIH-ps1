import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useChartColors } from "../../theme/chartColors";

const formatCr = (v) => `₹${Number(v).toLocaleString("en-IN")} Cr`;

export default function CostHistoryChart({ points }) {
  const colors = useChartColors();
  return (
    <div className="h-60">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={points} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
          <XAxis dataKey="month" stroke={colors.axis} fontSize={11} />
          <YAxis stroke={colors.axis} fontSize={11} tickFormatter={(v) => Number(v).toLocaleString("en-IN")} width={60} />
          <Tooltip
            contentStyle={{ background: colors.tooltipBg, border: `1px solid ${colors.tooltipBorder}`, borderRadius: 8 }}
            formatter={formatCr}
          />
          <Legend />
          <Line type="monotone" dataKey="original_cost" name="Original cost" stroke="#8b93ab" strokeWidth={2} strokeDasharray="5 4" dot={false} />
          <Line type="monotone" dataKey="current_cost" name="Current cost" stroke="#f97316" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="expenditure" name="Expenditure" stroke="#3b82f6" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
