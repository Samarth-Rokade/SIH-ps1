import { useTheme } from "./themeContext";

// Recharts/Leaflet need literal color values (inline SVG/canvas props), which
// can't reference CSS custom properties - so chart chrome (grid/axis/tooltip)
// gets its own small per-theme palette here, kept in sync with index.css.
const CHART_PALETTES = {
  dark: {
    grid: "#232b45",
    axis: "#8b93ab",
    tooltipBg: "#10162a",
    tooltipBorder: "#232b45",
  },
  light: {
    grid: "#c9dcee",
    axis: "#5b6b85",
    tooltipBg: "#ffffff",
    tooltipBorder: "#c9dcee",
  },
};

export function useChartColors() {
  const { theme } = useTheme();
  return CHART_PALETTES[theme];
}
