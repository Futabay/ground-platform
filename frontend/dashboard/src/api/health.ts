export type HealthResponse = {
  status: string;
  service?: string;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) {
    throw new Error(`Health check failed with status ${res.status}`);
  }
  return res.json();
}
