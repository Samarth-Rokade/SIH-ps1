import { cleanParams, request } from "./client";

export const listProjects = (params) =>
  request({ url: "/projects", params: cleanParams(params) });

export const getProject = (projectId) => request({ url: `/projects/${projectId}` });

export const getProjectRisk = (projectId) => request({ url: `/projects/${projectId}/risk` });

export const getDelayPrediction = (projectId) =>
  request({ url: `/projects/${projectId}/prediction/delay` });

export const getCostPrediction = (projectId) =>
  request({ url: `/projects/${projectId}/prediction/cost` });

export const getRiskDrivers = (projectId) =>
  request({ url: `/projects/${projectId}/risk-drivers` });
