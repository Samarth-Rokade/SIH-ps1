import {
  BarChart3,
  BellRing,
  Bot,
  FileText,
  FolderKanban,
  LayoutDashboard,
  Radar,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
  Wallet,
} from "lucide-react";
import { NavLink } from "react-router";
import { useTheme } from "../../theme/themeContext";
import SidebarIllustration from "./SidebarIllustration";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard, ready: true },
  { to: "/risk-radar", label: "Risk Radar", icon: Radar, ready: true },
  { to: "/projects", label: "Projects", icon: FolderKanban, ready: true },
  { to: "/early-warnings", label: "Early Warnings", icon: BellRing, ready: true },
  { to: "/analytics", label: "Analytics", icon: BarChart3, ready: false },
  { to: "/cost-intelligence", label: "Cost Intelligence", icon: Wallet, ready: false },
  { to: "/simulator", label: "What-if Simulator", icon: SlidersHorizontal, ready: false },
  { to: "/assistant", label: "AI Assistant", icon: Bot, ready: false },
  { to: "/reports", label: "Reports", icon: FileText, ready: false },
  { to: "/settings", label: "Settings", icon: Settings, ready: false },
];

export default function Sidebar() {
  const { theme, toggleTheme } = useTheme();

  return (
    <aside className="flex h-full w-64 flex-col border-r border-sidebar-border bg-sidebar-bg">
      <div className="flex items-center gap-2 border-b border-sidebar-border px-5 py-5">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-sidebar-active-bg text-sidebar-active-text">
          <ShieldCheck className="h-5 w-5" strokeWidth={2} />
        </div>
        <div>
          <div className="text-sm font-semibold leading-tight text-sidebar-text">PAIMANA</div>
          <div className="text-sm font-semibold leading-tight text-sidebar-accent-text">
            SENTINEL AI
          </div>
        </div>
      </div>

      <nav className="relative flex-1 space-y-1 overflow-y-auto px-3 py-4">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors ${
                  isActive
                    ? "bg-sidebar-active-bg text-sidebar-active-text font-medium"
                    : "text-sidebar-text-muted hover:bg-sidebar-hover hover:text-sidebar-text"
                }`
              }
            >
              <Icon className="h-4 w-4 shrink-0" strokeWidth={1.8} />
              <span className="flex-1">{item.label}</span>
              {!item.ready && (
                <span className="rounded bg-sidebar-hover px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-sidebar-text-muted">
                  Soon
                </span>
              )}
            </NavLink>
          );
        })}

        <SidebarIllustration className="pointer-events-none absolute inset-x-0 bottom-0 h-56 w-full" />
      </nav>

      <div className="border-t border-sidebar-border px-4 py-3">
        <button
          onClick={toggleTheme}
          className="mb-3 flex w-full items-center justify-between rounded-lg px-2 py-2 text-xs text-sidebar-text-muted transition-colors hover:bg-sidebar-hover hover:text-sidebar-text"
        >
          <span>{theme === "dark" ? "Dark Mode" : "Light Mode"}</span>
          <span className="flex h-5 w-9 items-center rounded-full bg-sidebar-hover px-0.5">
            <span
              className={`h-4 w-4 rounded-full bg-sidebar-active-text transition-transform ${
                theme === "dark" ? "translate-x-0" : "translate-x-4"
              }`}
            />
          </span>
        </button>
        <div className="flex items-center gap-1.5 text-xs text-sidebar-text-muted">
          <span className="h-2 w-2 rounded-full bg-low" />
          All Systems Online
        </div>
      </div>
    </aside>
  );
}
