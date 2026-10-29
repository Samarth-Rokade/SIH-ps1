import { request } from "./client";

export const getSimulatorParameters = (projectId) =>
  request({ url: `/simulator/${projectId}/parameters` });

export const runSimulation = (payload) =>
  request({ url: "/simulator/run", method: "POST", data: payload });
