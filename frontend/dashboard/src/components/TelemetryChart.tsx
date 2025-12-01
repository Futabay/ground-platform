import { useQuery } from "@tanstack/react-query";
import type { TelemetryPoint } from "../api/telemetry"; // 👈 type-only import
import { fetchTelemetry } from "../api/telemetry";
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
} from "@mui/material";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

type Props = {
  satelliteId?: string;
  parameter?: string;
  limit?: number;
};

function formatTelemetryForChart(
  data: TelemetryPoint[],
  parameter?: string
): { time: string; value: number }[] {
  const filtered = parameter
    ? data.filter((d) => d.parameter === parameter)
    : data;

  return filtered
    .slice()
    .sort(
      (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    )
    .map((point) => ({
      time: new Date(point.timestamp).toLocaleTimeString(),
      value: point.value,
    }));
}

export function TelemetryChart({ satelliteId, parameter, limit = 50 }: Props) {
  const {
    data,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["telemetry", { satelliteId, parameter, limit }],
    queryFn: () => fetchTelemetry({ satelliteId, limit }),
    refetchInterval: 5000,
    refetchOnWindowFocus: false,
  });

  const chartData = data ? formatTelemetryForChart(data, parameter) : [];

  return (
    <Card
      sx={{
        bgcolor: "#111827",
        borderRadius: 3,
        boxShadow: "0 20px 45px rgba(0,0,0,0.5)",
        height: 320,
      }}
    >
      <CardContent
        sx={{ height: "100%", display: "flex", flexDirection: "column" }}
      >
        <Typography variant="h6" sx={{ color: "#e5e7eb", mb: 1 }}>
          Telemetry – {parameter ?? "All parameters"}
        </Typography>
        <Typography variant="body2" sx={{ color: "#9ca3af", mb: 2 }}>
          Satellite: {satelliteId ?? "SAT-001"}
        </Typography>

        {isLoading && (
          <Box
            sx={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <CircularProgress size={28} />
          </Box>
        )}

        {isError && (
          <Typography variant="body2" sx={{ color: "#f97373" }}>
            Failed to load telemetry: {(error as Error).message}
          </Typography>
        )}

        {!isLoading && !isError && (
          <Box sx={{ flex: 1, minHeight: 0 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="time" tick={{ fill: "#9ca3af", fontSize: 12 }} />
                <YAxis tick={{ fill: "#9ca3af", fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#020617", border: "none" }}
                  labelStyle={{ color: "#e5e7eb" }}
                  formatter={(value: any) => [value, "value"]}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#22c55e"
                  dot={false}
                  strokeWidth={2}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
