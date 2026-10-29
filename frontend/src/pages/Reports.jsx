import { useState } from "react";
import { useSearchParams } from "react-router";
import { downloadReport, generateDashboardReport, generateProjectReport, listReports } from "../api/reports";
import { getProject } from "../api/projects";
import ErrorState from "../components/common/ErrorState";
import LoadingState from "../components/common/LoadingState";
import ProjectPicker from "../components/common/ProjectPicker";
import Topbar from "../components/layout/Topbar";
import { useApiData } from "../hooks/useApiData";

const MONTH_RE = /^\d{4}-(0[1-9]|1[0-2])$/;

export default function Reports() {
  const [searchParams, setSearchParams] = useSearchParams();
  const projectId = searchParams.get("project");

  const reports = useApiData(listReports, []);
  const project = useApiData(() => (projectId ? getProject(projectId) : Promise.resolve({ data: null })), [projectId]);

  const [month, setMonth] = useState("");
  const [busy, setBusy] = useState(null); // "dashboard" | "project" | report_id (download)
  const [banner, setBanner] = useState(null); // {type: "success"|"error", text}

  async function generate(kind) {
    if (kind === "dashboard" && month && !MONTH_RE.test(month)) {
      setBanner({ type: "error", text: "Month must be in YYYY-MM format, e.g. 2026-07." });
      return;
    }
    setBusy(kind);
    setBanner(null);
    try {
      const { data } =
        kind === "dashboard" ? await generateDashboardReport(month.trim()) : await generateProjectReport(projectId);
      setBanner({ type: "success", text: `${data.title} generated (${data.report_id}).` });
      reports.refetch();
    } catch (err) {
      setBanner({ type: "error", text: err.message });
    } finally {
      setBusy(null);
    }
  }

  async function download(reportId) {
    setBusy(reportId);
    setBanner(null);
    try {
      await downloadReport(reportId);
    } catch (err) {
      setBanner({ type: "error", text: err.message || "Download failed." });
    } finally {
      setBusy(null);
    }
  }

  return (
    <div>
      <Topbar title="Reports" subtitle="Generate and download PDF reports" />

      {banner && (
        <div
          className={`mb-4 rounded-lg border px-4 py-2 text-sm ${
            banner.type === "success"
              ? "border-low/30 bg-low-soft text-low"
              : "border-critical/30 bg-critical-soft text-critical"
          }`}
        >
          {banner.text}
        </div>
      )}

      <div className="mb-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="rounded-xl border border-border bg-surface p-5">
          <h2 className="text-sm font-semibold">Portfolio (dashboard) report</h2>
          <p className="mt-1 text-xs text-text-muted">
            KPIs, risk distribution, top priority projects, and ministry and sector benchmarks.
          </p>
          <label className="mt-4 block text-xs text-text-muted">
            Reporting month (optional, YYYY-MM)
            <input
              value={month}
              onChange={(e) => setMonth(e.target.value)}
              placeholder="2026-07"
              maxLength={7}
              className="mt-1 w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm text-text placeholder:text-text-muted"
            />
          </label>
          <button
            onClick={() => generate("dashboard")}
            disabled={busy === "dashboard"}
            className="mt-4 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
          >
            {busy === "dashboard" ? "Generating..." : "Generate Portfolio Report"}
          </button>
        </div>

        <div className="rounded-xl border border-border bg-surface p-5">
          <h2 className="text-sm font-semibold">Project report</h2>
          <p className="mt-1 text-xs text-text-muted">
            Risk assessment, delay and cost forecasts, SHAP drivers, peer benchmark and alerts for one project.
          </p>
          <div className="mt-4">
            <ProjectPicker
              selected={project.data}
              onSelect={(p) => setSearchParams({ project: p.project_id })}
              placeholder="Search for a project..."
            />
          </div>
          {project.data && (
            <p className="mt-2 text-xs text-text-muted">
              Selected: <span className="font-medium text-text">{project.data.project_name}</span> ({project.data.project_id})
            </p>
          )}
          {project.error && <p className="mt-2 text-xs text-critical">{project.error.message}</p>}
          <button
            onClick={() => generate("project")}
            disabled={!projectId || busy === "project"}
            className="mt-4 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
          >
            {busy === "project" ? "Generating..." : "Generate Project Report"}
          </button>
        </div>
      </div>

      <div className="overflow-hidden rounded-xl border border-border bg-surface">
        <h2 className="border-b border-border px-4 py-3 text-sm font-semibold">Generated reports</h2>
        {reports.loading && !reports.data && <LoadingState />}
        {reports.error && <ErrorState error={reports.error} onRetry={reports.refetch} />}
        {reports.data && (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase text-text-muted">
                <th className="px-4 py-2">ID</th>
                <th className="px-4 py-2">Type</th>
                <th className="px-4 py-2">Title</th>
                <th className="px-4 py-2">Created</th>
                <th className="px-4 py-2 text-right">Download</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {reports.data.map((r) => (
                <tr key={r.report_id} className="hover:bg-surface-hover">
                  <td className="px-4 py-2 font-medium">{r.report_id}</td>
                  <td className="px-4 py-2 capitalize text-text-muted">{r.kind}</td>
                  <td className="px-4 py-2">{r.title}</td>
                  <td className="px-4 py-2 text-text-muted">{new Date(r.created_at).toLocaleString()}</td>
                  <td className="px-4 py-2 text-right">
                    <button
                      onClick={() => download(r.report_id)}
                      disabled={busy === r.report_id}
                      className="rounded border border-border px-3 py-1 text-xs hover:bg-surface-hover disabled:opacity-50"
                    >
                      {busy === r.report_id ? "..." : "Download PDF"}
                    </button>
                  </td>
                </tr>
              ))}
              {reports.data.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-text-muted">
                    No reports generated yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
