"use client";
import { Card, CardContent, CardActions, Typography, Button } from "@mui/material";
import ToolModal from "./ToolModal";
import { useState } from "react";

export default function ToolCard({ tool }: { tool: any }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Card sx={{ minWidth: 280, maxWidth: 380, flex: "1 0 280px", mb: 2 }}>
        <CardContent>
          <Typography variant="h6">{tool.name}</Typography>
          <Typography variant="body2" color="text.secondary">{tool.developer}</Typography>
          <Typography sx={{ mt: 1 }}>{tool.category}</Typography>
          <Typography sx={{ mt: 1 }}>{tool.keyFeatures?.join(' | ') ?? ""}</Typography>
        </CardContent>
        <CardActions>
          {tool.url && (
            <Button size="small" href={tool.url} target="_blank" rel="noopener" color="primary">
              Site officiel
            </Button>
          )}
          <Button size="small" onClick={() => setOpen(true)}>Détails</Button>
        </CardActions>
      </Card>
      <ToolModal tool={tool} open={open} onClose={() => setOpen(false)} />
    </>
  );
}
