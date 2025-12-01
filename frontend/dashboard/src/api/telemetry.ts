export type TelemetryPoint = {
  timestamp: string;      // ISO string from backend
  satellite_id: string;
  subsystem: string;
  parameter: string;
  value: number;
  unit: string;
  status: string;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function fetchTelemetry(params?: {
  satelliteId?: string;
  limit?: number;
}): Promise<TelemetryPoint[]> {
  const url = new URL(`${API_BASE_URL}/telemetry`);

  if (params?.satelliteId) {
    url.searchParams.set("satellite_id", params.satelliteId);
  }
  if (params?.limit) {
    url.searchParams.set("limit", String(params.limit));
  } else {
    url.searchParams.set("limit", "50");
  }

  const res = await fetch(url.toString());
  if (!res.ok) {
    throw new Error(`Telemetry request failed with status ${res.status}`);
  }
  return res.json();
}
