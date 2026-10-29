import { api, request } from "./client";

export const listReports = () => request({ url: "/reports" });

export const generateProjectReport = (projectId) =>
  request({ url: `/reports/project/${projectId}`, method: "POST", data: { format: "pdf" } });

export const generateDashboardReport = (month) =>
  request({ url: "/reports/dashboard", method: "POST", data: { month: month || null, format: "pdf" } });

/** Downloads through axios (honours the configured base URL) and triggers a browser save. */
export async function downloadReport(reportId) {
  const response = await api.get(`/reports/${reportId}/download`, { responseType: "blob" });
  const url = URL.createObjectURL(response.data);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${reportId}.pdf`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
