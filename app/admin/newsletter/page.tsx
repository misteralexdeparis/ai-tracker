'use client';

import { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Stack,
  TextField,
  Divider
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import PreviewIcon from '@mui/icons-material/Preview';
import PeopleIcon from '@mui/icons-material/People';
import RefreshIcon from '@mui/icons-material/Refresh';

interface NewsletterStats {
  newTools: number;
  majorUpdates: number;
  minorUpdates: number;
  totalTools: number;
  timestamp: string;
}

interface Subscriber {
  email: string;
  subscribedAt: string;
  active: boolean;
  confirmed: boolean;
}

export default function NewsletterAdminPage() {
  const [loading, setLoading] = useState(false);
  const [previewHTML, setPreviewHTML] = useState('');
  const [stats, setStats] = useState<NewsletterStats | null>(null);
  const [subscribers, setSubscribers] = useState<Subscriber[]>([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [sendDialogOpen, setSendDialogOpen] = useState(false);
  const [adminKey, setAdminKey] = useState('');

  // Load admin key from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('adminKey');
    if (saved) setAdminKey(saved);
  }, []);

  // Save admin key to localStorage
  const saveAdminKey = (key: string) => {
    setAdminKey(key);
    localStorage.setItem('adminKey', key);
  };

  const loadPreview = async () => {
    if (!adminKey) {
      setError('Admin key required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/admin/newsletter/preview', {
        headers: {
          'x-admin-key': adminKey
        }
      });

      if (!response.ok) {
        throw new Error('Failed to load preview');
      }

      const data = await response.json();
      setPreviewHTML(data.html);
      setStats(data.stats);
      setSuccess('Preview loaded successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load preview');
    } finally {
      setLoading(false);
    }
  };

  const loadSubscribers = async () => {
    if (!adminKey) return;

    try {
      const response = await fetch('/api/admin/subscribers', {
        headers: {
          'x-admin-key': adminKey
        }
      });

      if (!response.ok) throw new Error('Failed to load subscribers');

      const data = await response.json();
      setSubscribers(data.subscribers || []);
    } catch (err) {
      console.error('Failed to load subscribers:', err);
    }
  };

  const sendNewsletter = async () => {
    if (!adminKey) {
      setError('Admin key required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/admin/newsletter/send', {
        method: 'POST',
        headers: {
          'x-admin-key': adminKey,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to send newsletter');
      }

      const data = await response.json();
      setSuccess(`Newsletter sent successfully to ${data.sent || subscribers.filter(s => s.active && s.confirmed).length} subscribers!`);
      setSendDialogOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send newsletter');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (adminKey) {
      loadPreview();
      loadSubscribers();
    }
  }, [adminKey]);

  const activeSubscribers = subscribers.filter(s => s.active && s.confirmed).length;

  if (!adminKey) {
    return (
      <Box sx={{ minHeight: '100vh', background: '#f3f4f6', p: 4 }}>
        <Box sx={{ maxWidth: '500px', mx: 'auto', mt: 8 }}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Newsletter Admin
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Enter admin key to access the newsletter dashboard
              </Typography>
              <TextField
                fullWidth
                type="password"
                label="Admin Key"
                value={adminKey}
                onChange={(e) => setAdminKey(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && saveAdminKey(adminKey)}
              />
              <Button
                fullWidth
                variant="contained"
                onClick={() => saveAdminKey(adminKey)}
                sx={{ mt: 2 }}
              >
                Access Dashboard
              </Button>
            </CardContent>
          </Card>
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', background: '#f3f4f6', p: 4 }}>
      <Box sx={{ maxWidth: '1200px', mx: 'auto' }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', color: '#0d9488' }}>
          Newsletter Admin Dashboard
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
            {success}
          </Alert>
        )}

        {/* Stats Cards */}
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} sx={{ mb: 3 }}>
          <Card sx={{ flex: 1 }}>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={1}>
                <PeopleIcon color="primary" />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {activeSubscribers}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active Subscribers
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>

          {stats && (
            <>
              <Card sx={{ flex: 1 }}>
                <CardContent>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {stats.newTools}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    New Tools
                  </Typography>
                </CardContent>
              </Card>

              <Card sx={{ flex: 1 }}>
                <CardContent>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {stats.majorUpdates}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Major Updates
                  </Typography>
                </CardContent>
              </Card>

              <Card sx={{ flex: 1 }}>
                <CardContent>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {stats.totalTools}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Tools
                  </Typography>
                </CardContent>
              </Card>
            </>
          )}
        </Stack>

        {/* Actions */}
        <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={loadPreview}
            disabled={loading}
          >
            Refresh Preview
          </Button>
          <Button
            variant="contained"
            color="success"
            startIcon={<SendIcon />}
            onClick={() => setSendDialogOpen(true)}
            disabled={loading || !previewHTML || activeSubscribers === 0}
          >
            Send Newsletter Now
          </Button>
        </Stack>

        {/* Preview */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Newsletter Preview
            </Typography>
            <Divider sx={{ my: 2 }} />

            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            ) : previewHTML ? (
              <Box
                sx={{
                  border: '1px solid #e5e7eb',
                  borderRadius: 1,
                  overflow: 'auto',
                  maxHeight: '600px'
                }}
                dangerouslySetInnerHTML={{ __html: previewHTML }}
              />
            ) : (
              <Typography color="text.secondary">
                Click "Refresh Preview" to generate newsletter preview
              </Typography>
            )}
          </CardContent>
        </Card>

        {/* Subscribers List */}
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Subscribers ({subscribers.length})
            </Typography>
            <Divider sx={{ my: 2 }} />

            <Stack spacing={1}>
              {subscribers.length === 0 ? (
                <Typography color="text.secondary">No subscribers yet</Typography>
              ) : (
                subscribers.map((sub, idx) => (
                  <Box
                    key={idx}
                    sx={{
                      p: 2,
                      background: '#f9fafb',
                      borderRadius: 1,
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                  >
                    <Box>
                      <Typography variant="body2">{sub.email}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Subscribed: {new Date(sub.subscribedAt).toLocaleDateString()}
                      </Typography>
                    </Box>
                    <Stack direction="row" spacing={1}>
                      {sub.confirmed && <Chip label="Confirmed" color="success" size="small" />}
                      {sub.active ? (
                        <Chip label="Active" color="primary" size="small" />
                      ) : (
                        <Chip label="Inactive" size="small" />
                      )}
                    </Stack>
                  </Box>
                ))
              )}
            </Stack>
          </CardContent>
        </Card>
      </Box>

      {/* Send Confirmation Dialog */}
      <Dialog open={sendDialogOpen} onClose={() => setSendDialogOpen(false)}>
        <DialogTitle>Confirm Newsletter Send</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to send the newsletter to{' '}
            <strong>{activeSubscribers} active subscribers</strong>?
          </Typography>
          <Alert severity="warning" sx={{ mt: 2 }}>
            This action cannot be undone. Make sure you reviewed the preview first.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSendDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={sendNewsletter}
            variant="contained"
            color="success"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Send Now'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
