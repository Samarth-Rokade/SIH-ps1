import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { useChartColors } from "../../theme/chartColors";
import { RISK_COLORS } from "../../utils/riskColors";

export default function RiskDistributionDonut({ distribution, total }) {
  const colors = useChartColors();
  const data = distribution.map((d) => ({ name: d.level, value: d.count, percentage: d.percentage }));

  return (
    <div className="relative h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            innerRadius={65}
            outerRadius={95}
            paddingAngle={2}
            stroke="none"
          >
            {data.map((entry) => (
              <Cell key={entry.name} fill={RISK_COLORS[entry.name]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: colors.tooltipBg,
              border: `1px solid ${colors.tooltipBorder}`,
              borderRadius: 8,
            }}
            formatter={(value, name, item) => [`${value} (${item.payload.percentage}%)`, name]}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-semibold">{total}</span>
        <span className="text-xs text-text-muted">Total Projects</span>
      </div>
    </div>
  );
}
