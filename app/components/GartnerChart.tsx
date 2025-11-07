"use client";
import { Scatter } from "react-chartjs-2";
import { Box, Typography, Container } from "@mui/material";
import {
  Chart as ChartJS,
  PointElement,
  Tooltip,
  Legend,
  LinearScale,
  Title,
} from "chart.js";

ChartJS.register(PointElement, Tooltip, Legend, LinearScale, Title);

// Palette de 22 couleurs DISTINCTES par outil (pas par quadrant)
const toolColors: { [key: string]: string } = {
  "gpt-5-pro": "#FF1744",      // Red
  "gpt-5": "#FF6E40",          // Deep Orange
  "claude-4-5": "#9C27B0",     // Purple
  "gemini-2-5-pro": "#2196F3", // Blue
  "midjourney-v7": "#00BCD4",  // Cyan
  "lovable": "#009688",        // Teal
  "github-copilot": "#4CAF50", // Green
  "bolt-new": "#8BC34A",       // Light Green
  "sora-2": "#CDDC39",         // Lime
  "dalle-3": "#FFEB3B",        // Yellow
  "grok-4": "#FF9800",         // Orange
  "perplexity": "#FF5722",     // Deep Orange Red
  "gemini-canvas": "#673AB7",  // Deep Purple
  "synthesia": "#3F51B5",      // Indigo
  "deepseek-r1": "#00838F",    // Dark Cyan
  "aws-q": "#1565C0",          // Dark Blue
  "gamma": "#C2185B",          // Pink
  "claude-opus": "#D32F2F",    // Dark Red
  "notebooklm": "#F57C00",     // Dark Orange
  "llama-3": "#388E3C",        // Dark Green
  "nano-banana": "#F06292",    // Light Pink
  "ideogram": "#AB47BC",       // Light Purple
};

// Plugin pour les quadrants background
const quadrantBackground = {
  id: "quadrant-bg",
  afterDatasetsDraw: (chart: any) => {
    const ctx = chart.ctx;
    const { left, right, top, bottom } = chart.chartArea;
    const midX = left + (right - left) / 2;
    const midY = top + (bottom - top) / 2;

    // Leader (top-right) - bleu clair
    ctx.fillStyle = "rgba(33, 150, 243, 0.03)";
    ctx.fillRect(midX, top, right - midX, midY - top);
    ctx.fillStyle = "rgba(33, 150, 243, 0.7)";
    ctx.font = "bold 16px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("LEADER", midX + (right - midX) / 2, top + 35);

    // Visionary (bottom-right) - vert clair
    ctx.fillStyle = "rgba(76, 175, 80, 0.03)";
    ctx.fillRect(midX, midY, right - midX, bottom - midY);
    ctx.fillStyle = "rgba(76, 175, 80, 0.7)";
    ctx.font = "bold 16px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("VISIONARY", midX + (right - midX) / 2, midY + (bottom - midY) / 2 + 15);

    // Challenger (top-left) - violet clair
    ctx.fillStyle = "rgba(156, 39, 176, 0.03)";
    ctx.fillRect(left, top, midX - left, midY - top);
    ctx.fillStyle = "rgba(156, 39, 176, 0.7)";
    ctx.font = "bold 16px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("CHALLENGER", left + (midX - left) / 2, top + 35);

    // Niche (bottom-left) - orange clair
    ctx.fillStyle = "rgba(255, 160, 0, 0.03)";
    ctx.fillRect(left, midY, midX - left, bottom - midY);
    ctx.fillStyle = "rgba(255, 160, 0, 0.7)";
    ctx.font = "bold 16px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("NICHE", left + (midX - left) / 2, midY + (bottom - midY) / 2 + 15);

    // Axes lignes
    ctx.strokeStyle = "#666";
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(midX, top);
    ctx.lineTo(midX, bottom);
    ctx.moveTo(left, midY);
    ctx.lineTo(right, midY);
    ctx.stroke();
    ctx.setLineDash([]);
  },
};

export default function GartnerChart({ tools }: { tools: any[] }) {
  const datasets = tools.map((tool) => {
    const vision = parseInt(String(tool.vision)) || 50;
    const ability = parseInt(String(tool.ability)) || 50;
    const toolColor = toolColors[tool.id] || "#999999";

    return {
      label: tool.name,
      data: [{ x: vision, y: ability }],
      pointBackgroundColor: toolColor,
      pointRadius: 10,
      pointHoverRadius: 14,
      pointBorderWidth: 2,
      pointBorderColor: "#fff",
      pointStyle: "circle",
    };
  });

  const data = {
    datasets: datasets,
  };

  const options: any = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: true,
        position: "right" as const,
        labels: {
          usePointStyle: true,
          padding: 12,
          font: { size: 11 },
        },
      },
      title: {
        display: true,
        text: "Matrice Gartner - AI Tools 2025",
        font: { size: 20, weight: "bold" },
        padding: 20,
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const toolName = context.dataset.label;
            const x = context.parsed.x;
            const y = context.parsed.y;
            return `${toolName}: Vision ${x}, Ability ${y}`;
          },
        },
        backgroundColor: "rgba(0, 0, 0, 0.8)",
        titleFont: { size: 12, weight: "bold" },
        bodyFont: { size: 11 },
        padding: 12,
        borderColor: "#fff",
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        type: "linear" as const,
        position: "bottom" as const,
        title: {
          display: true,
          text: "Vision",
          font: { size: 15, weight: "bold" },
        },
        min: 0,
        max: 100,
        ticks: {
          stepSize: 10,
          font: { size: 12 },
        },
        grid: {
          color: "rgba(0, 0, 0, 0.08)",
          drawBorder: true,
        },
      },
      y: {
        title: {
          display: true,
          text: "Ability to Execute",
          font: { size: 15, weight: "bold" },
        },
        min: 0,
        max: 100,
        ticks: {
          stepSize: 10,
          font: { size: 12 },
        },
        grid: {
          color: "rgba(0, 0, 0, 0.08)",
          drawBorder: true,
        },
      },
    },
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ p: 3 }}>
        <Typography variant="h5" mb={3}>
          📊 Matrice Gartner Interactive - AI Tools 2025
        </Typography>
        <Box sx={{ height: 700, position: "relative" }}>
          <Scatter data={data} options={options} plugins={[quadrantBackground]} />
        </Box>

        <Box sx={{ display: "flex", gap: 3, mt: 4, flexWrap: "wrap" }}>
          <Box>
            <Typography color="primary" variant="body2">
              <strong>🔵 Leader</strong>: High Vision ≥50 + High Ability ≥50
            </Typography>
          </Box>
          <Box>
            <Typography color="success.main" variant="body2">
              <strong>🟢 Visionary</strong>: High Vision ≥50 + Low Ability &lt;50
            </Typography>
          </Box>
          <Box>
            <Typography color="secondary" variant="body2">
              <strong>🟣 Challenger</strong>: Low Vision &lt;50 + High Ability ≥50
            </Typography>
          </Box>
          <Box>
            <Typography color="warning.main" variant="body2">
              <strong>🟠 Niche</strong>: Low Vision &lt;50 + Low Ability &lt;50
            </Typography>
          </Box>
        </Box>
      </Box>
    </Container>
  );
}