"use client";
import { useState, useEffect } from "react";
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Typography, Container, Box, TextField, Select, MenuItem, InputLabel, FormControl
} from "@mui/material";
import ToolCard from "./ToolCard";
import GartnerChart from "./GartnerChart";


const categories = [
  "All", "LLM", "AI Coding", "Video Generation", "Image Generation", "Search & Research", "Audio", "Infrastructure", "Presentation", "Other"
];


export default function ToolsTable() {
  const [tools, setTools] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [cat, setCat] = useState("All");
  const [view, setView] = useState<"table" | "card" | "chart">("table");
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Cache busting: force fresh data from GitHub raw content
    const fetchTools = async () => {
      try {
        setLoading(true);
        const cacheBreaker = Math.random().toString(36).substring(7);
        const timestamp = Date.now();
        
        // Fetch directly from GitHub to bypass Vercel cache
        const url = `https://raw.githubusercontent.com/misteralexdeparis/ai-tracker/main/public/ai_tracker_enhanced.json?t=${timestamp}&cb=${cacheBreaker}`;
        
        const res = await fetch(url, {
          cache: 'no-store',
          headers: {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
          }
        });
        
        if (!res.ok) {
          throw new Error(`Failed to fetch: ${res.status}`);
        }
        
        const data = await res.json();
        setTools(data.tools || data || []);
      } catch (error) {
        console.error("Error fetching tools:", error);
        // Fallback to local cache if GitHub fails
        try {
          const localRes = await fetch("/ai_tracker_enhanced.json");
          const localData = await localRes.json();
          setTools(localData.tools || localData || []);
        } catch (e) {
          console.error("Error fetching from local fallback:", e);
          setTools([]);
        }
      } finally {
        setLoading(false);
      }
    };
    
    fetchTools();
  }, []);


  const filtered = tools.filter(tool =>
    (cat === "All" || tool.category === cat) &&
    (tool.name.toLowerCase().includes(search.toLowerCase())
      || tool.developer?.toLowerCase().includes(search.toLowerCase()))
  );
  
  return (
    <Container maxWidth="xl" sx={{ marginTop: 4 }}>
      <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 3 }}>
        <Typography variant="h4" sx={{ flex: 1 }}>🧭 AI Tools Tracker</Typography>
        <Typography variant="body2" sx={{ color: "text.secondary" }}>
          {loading ? "Loading..." : `${filtered.length} tools`}
        </Typography>
        <a href="/find-tool" style={{ textDecoration: 'none' }}>
          <button style={{
            background: 'linear-gradient(135deg, #0d9488 0%, #14b8a6 100%)',
            color: 'white',
            border: 'none',
            padding: '10px 20px',
            borderRadius: '6px',
            fontSize: '14px',
            fontWeight: 'bold',
            cursor: 'pointer',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            transition: 'all 0.2s'
          }}
          onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
          onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
          >
            🎯 Find Your Perfect Tool
          </button>
        </a>
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
          disabled={loading}
        />
        <FormControl size="small" sx={{ minWidth: 180 }}>
          <InputLabel id="cat-label">Catégorie</InputLabel>
          <Select
            labelId="cat-label"
            value={cat}
            label="Catégorie"
            onChange={e => setCat(e.target.value)}
            disabled={loading}
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
                <TableCell>Quadrant</TableCell><TableCell>Vision/Ability</TableCell>
                <TableCell>Status</TableCell><TableCell>Site</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">Loading tools...</TableCell>
                </TableRow>
              ) : filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">No tools found</TableCell>
                </TableRow>
              ) : (
                filtered.map(tool => (
                  <TableRow key={tool.name}>
                    <TableCell>
                      <b>{tool.name}</b>
                    </TableCell>
                    <TableCell>{tool.category}</TableCell>
                    <TableCell>{tool.quadrant}</TableCell>
                    <TableCell>{tool.vision}/{tool.ability}</TableCell>
                    <TableCell>{tool.status}</TableCell>
                    <TableCell>
                      {tool.official_url ? <a href={tool.official_url} target="_blank" rel="noopener noreferrer">Link</a> : ""}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}


      {view === "card" && (
        <Box sx={{display:"flex", flexWrap:"wrap", gap:3}}>
          {filtered.map(tool => <ToolCard key={tool.name} tool={tool} />)}
        </Box>
      )}


      {view === "chart" && (
        <GartnerChart tools={filtered} />
      )}


      <Box textAlign="center" pt={4}>
        <Typography variant="body2" color="text.secondary">
          Total tools tracked: {tools.length} | Last auto-update: bi-weekly
        </Typography>
      </Box>
    </Container>
  )
}