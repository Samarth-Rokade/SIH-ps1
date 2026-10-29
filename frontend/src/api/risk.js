import { cleanParams, request } from "./client";

export const getRadar = (filters = {}, limit = 1000) =>
  request({ url: "/risk/radar", params: cleanParams({ ...filters, limit }) });

export const getSummary = () => request({ url: "/risk/summary" });

export const getFilterOptions = () => request({ url: "/risk/filters" });
