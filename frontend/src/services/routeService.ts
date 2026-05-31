import api from "./api";
import type { RouteRequest, RouteResponse } from "../types/route";

export async function planRoute(request: RouteRequest): Promise<RouteResponse> {
  const { data } = await api.post<RouteResponse>("/routes/", request);
  return data;
}
