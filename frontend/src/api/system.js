import { request } from "./client";

export const getSystemStatus = () => request({ url: "/system/status" });

export const getDataInfo = () => request({ url: "/system/data-info" });

export const getModelInfo = () => request({ url: "/system/models" });
