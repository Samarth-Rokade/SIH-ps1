import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export const api = axios.create({ baseURL: BASE_URL });

export class ApiError extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
  }
}

/** Unwraps the {success, data, meta} envelope; throws ApiError on failure. */
export async function request(config) {
  try {
    const response = await api.request(config);
    const body = response.data;
    if (!body.success) {
      throw new ApiError(body.error?.code ?? "UNKNOWN", body.error?.message ?? "Request failed");
    }
    return { data: body.data, meta: body.meta };
  } catch (err) {
    if (err instanceof ApiError) throw err;
    const body = err.response?.data;
    if (body?.error) throw new ApiError(body.error.code, body.error.message);
    throw new ApiError("NETWORK_ERROR", err.message || "Could not reach the backend");
  }
}

/** Drops null/undefined/empty-string params so they aren't sent as e.g. ministry=. */
export function cleanParams(params) {
  return Object.fromEntries(
    Object.entries(params).filter(([, v]) => v !== null && v !== undefined && v !== "")
  );
}
