"use client";
import { Dialog, DialogTitle, DialogContent, Typography, IconButton } from "@mui/material";
import CloseIcon from '@mui/icons-material/Close';

export default function ToolModal({ tool, open, onClose }: { tool:any, open:boolean, onClose:()=>void }) {
  if (!tool) return null;
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm">
      <DialogTitle>
        {tool.name} <span style={{fontSize:"0.8em",color:"#888"}}>{tool.developer}</span>
        <IconButton onClick={onClose} sx={{position:"absolute",right:8,top:8}}><CloseIcon/></IconButton>
      </DialogTitle>
      <DialogContent dividers>
        <Typography variant="subtitle2">{tool.category} — {tool.status} — {tool.quadrant}</Typography>
        <Typography variant="body1" sx={{mt:2}}>{tool.keyFeatures?.join(', ')}</Typography>
        {tool.strengths && <Typography color="success.main">Forces : {tool.strengths.join(', ')}</Typography>}
        {tool.limitations && <Typography color="error.main">Limites : {tool.limitations.join(', ')}</Typography>}
        {tool.url && <Typography sx={{mt:2}}><a href={tool.url} target="_blank">Site officiel</a></Typography>}
        {tool.integrations && <Typography sx={{mt:2}}>Intégrations : {tool.integrations}</Typography>}
        {tool.lastUpdated && <Typography sx={{mt:2}}>Mise à jour : {tool.lastUpdated.split('T')[0]}</Typography>}
      </DialogContent>
    </Dialog>
  );
}
