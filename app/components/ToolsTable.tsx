"use client";
import { useState, useEffect } from "react";
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Typography, Container, Box, TextField, Select, MenuItem, InputLabel, FormControl
} from "@mui/material";
import ToolCard from "./ToolCard";
import GartnerChart from "./GartnerChart";

const categories = [
  "All", "LLM", "Vibe Coding", "Video Generation", "Image Generation", "AI Agents"
];

export default function ToolsTable() {
  const [tools, setTools] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [cat, setCat] = useState("All");
  const [view, setView] = useState<"table" | "card" | "chart">("table");
  
  useEffect(() => {
    fetch("/ai_tracker_enhanced.json")
      .then(res => res.json())
      .then(setTools);
  }, []);

  const filtered = tools.filter(tool =>
    (cat === "All" || tool.category === cat) &&
    (tool.name.toLowerCase().includes(search.toLowerCase())
      || tool.developer?.toLowerCase().includes(search.toLowerCase()))
  );
  
  return (
    <Container maxWidth="xl" sx={{ marginTop: 4 }}>
      <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 3 }}>
        <Typography variant="h4" sx={{ flex: 1 }}>🧭 Community AI Tracker</Typography>
        <button onClick={() => setView("table")}>Table</button>
        <button onClick={() => setView("card")}>Cards</button>
        <button onClick={() => setView("chart")}>Matrice Gartner</button>
      </Box>

      <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
        <TextField
          label="Recherche"
          variant="outlined"
          size="small"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <FormControl size="small" sx={{ minWidth: 180 }}>
          <InputLabel id="cat-label">Catégorie</InputLabel>
          <Select
            labelId="cat-label"
            value={cat}
            label="Catégorie"
            onChange={e => setCat(e.target.value)}
          >
            {categories.map(c => <MenuItem key={c} value={c}>{c}</MenuItem>)}
          </Select>
        </FormControl>
      </Box>

      {view === "table" && (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell><TableCell>Category</TableCell>
                <TableCell>Quadrant</TableCell><TableCell>Score</TableCell>
                <TableCell>Key Features</TableCell><TableCell>Site</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filtered.map(tool => (
                <TableRow key={tool.id}>
                  <TableCell>
                    <b>{tool.name}</b><br />
                    <span style={{ color: "#888", fontSize: "0.9em" }}>{tool.developer}</span>
                  </TableCell>
                  <TableCell>{tool.category}</TableCell>
                  <TableCell>{tool.quadrant}</TableCell>
                  <TableCell>{tool.score ?? ""}</TableCell>
                  <TableCell>{tool.keyFeatures?.join(' / ') ?? ''}</TableCell>
                  <TableCell>
                    {tool.url ? <a href={tool.url} target="_blank" rel="noopener noreferrer">{tool.url.split("//")[1]?.split("/")[0]}</a> : ""}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {view === "card" && (
        <Box sx={{display:"flex", flexWrap:"wrap", gap:3}}>
          {filtered.map(tool => <ToolCard key={tool.id} tool={tool} />)}
        </Box>
      )}

      {view === "chart" && (
        <GartnerChart tools={filtered} />
      )}

      <Box textAlign="center" pt={4}>
        <Typography variant="body2" color="text.secondary">
          Last update: {tools[0]?.lastUpdated?.split('T')[0]}
        </Typography>
      </Box>
    </Container>
  )
}
