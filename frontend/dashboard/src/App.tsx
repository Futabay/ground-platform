import { useQuery } from "@tanstack/react-query";
import { fetchHealth } from "./api/health";
import { TelemetryChart } from "./components/TelemetryChart";
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Button,
  Container,
} from "@mui/material";

function App() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
    refetchOnWindowFocus: false,
  });

  let statusText = "UNKNOWN";
  let statusColor = "#64748b";

  if (isLoading) {
    statusText = "CHECKING...";
    statusColor = "#0284c7";
  } else if (isError) {
    statusText = "API: DOWN";
    statusColor = "#ef4444";
  } else if (data?.status?.toLowerCase() === "ok") {
    statusText = "API: OK";
    statusColor = "#22c55e";
  } else {
    statusText = `API: ${data?.status ?? "UNKNOWN"}`;
    statusColor = "#f59e0b";
  }

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "#020617", py: 4 }}>
      <Container maxWidth="lg">
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            gap: 3,
          }}
        >
          {/* Health card */}
          <Card
            sx={{
              bgcolor: "#111827",
              borderRadius: 3,
              boxShadow: "0 20px 45px rgba(0,0,0,0.5)",
            }}
          >
            <CardContent>
              <Typography variant="h5" sx={{ color: "#e5e7eb", mb: 1 }}>
                Ground Platform Dashboard
              </Typography>
              <Typography variant="body2" sx={{ color: "#9ca3af", mb: 2 }}>
                FastAPI health status
              </Typography>

              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 2,
                  mb: 2,
                }}
              >
                <Box
                  sx={{
                    width: 14,
                    height: 14,
                    borderRadius: "50%",
                    bgcolor: statusColor,
                    boxShadow: `0 0 12px ${statusColor}`,
                  }}
                />
                <Typography variant="h6">{statusText}</Typography>
                {isLoading && <CircularProgress size={20} />}
              </Box>

              {data?.service && (
                <Typography variant="body2" sx={{ color: "#9ca3af", mb: 1 }}>
                  Service: <strong>{data.service}</strong>
                </Typography>
              )}

              {isError && (
                <Typography variant="body2" sx={{ color: "#f97373", mb: 1 }}>
                  Could not reach API. Check Docker / FastAPI logs.
                </Typography>
              )}

              <Button variant="contained" onClick={() => refetch()}>
                Recheck
              </Button>
            </CardContent>
          </Card>

          {/* Telemetry chart */}
          <TelemetryChart
            satelliteId="SAT-001"
            parameter="battery_voltage"
            limit={50}
          />
        </Box>
      </Container>
    </Box>
  );
}

export default App;
