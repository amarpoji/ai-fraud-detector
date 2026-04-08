import React, { useState, useEffect } from 'react';
import { Container, Paper, TextField, Button, Card, CardContent, Typography, Box, CircularProgress, Alert, Grid, Chip, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { styled } from '@mui/material/styles';
import SendIcon from '@mui/icons-material/Send';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const RiskGaugeContainer = styled(Box)(({ theme }) => ({
  display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: theme.spacing(3),
}));

const GaugeWrapper = styled(Box)(({ theme }) => ({
  position: 'relative', width: 250, height: 250, margin: theme.spacing(2, 0),
}));

const RiskGauge = ({ score }) => {
  const rotation = (score / 100) * 180 - 90;
  const getColor = () => { if (score < 30) return '#4caf50'; if (score < 60) return '#ff9800'; return '#f44336'; };
  return (
    <GaugeWrapper>
      <svg width="100%" height="100%" viewBox="0 0 250 250">
        <circle cx="125" cy="125" r="120" fill="none" stroke="#e0e0e0" strokeWidth="4" />
        <path d="M 125 5 A 120 120 0 0 1 245 125" fill="none" stroke="#4caf50" strokeWidth="8" />
        <path d="M 245 125 A 120 120 0 0 1 125 245" fill="none" stroke="#ff9800" strokeWidth="8" />
        <path d="M 125 245 A 120 120 0 0 1 5 125" fill="none" stroke="#f44336" strokeWidth="8" />
        <line x1="125" y1="125" x2={125 + 100 * Math.cos((rotation * Math.PI) / 180)} y2={125 + 100 * Math.sin((rotation * Math.PI) / 180)} stroke={getColor()} strokeWidth="4" strokeLinecap="round" />
        <circle cx="125" cy="125" r="8" fill={getColor()} />
        <text x="50" y="30" textAnchor="middle" fontSize="12" fill="#666">Low Risk</text>
        <text x="200" y="130" textAnchor="middle" fontSize="12" fill="#666">Medium</text>
        <text x="125" y="235" textAnchor="middle" fontSize="12" fill="#666">High Risk</text>
      </svg>
      <Box sx={{ textAlign: 'center', marginTop: -15 }}>
        <Typography variant="h3" sx={{ fontWeight: 'bold', color: getColor() }}>{score.toFixed(1)}%</Typography>
      </Box>
    </GaugeWrapper>
  );
};

const RedFlagBadge = ({ flag }) => (
  <Chip icon={<WarningIcon sx={{ fontSize: 18 }} />} label={flag} color="error" variant="outlined" sx={{ margin: 0.5 }} />
);

function App() {
  const [message, setMessage] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [availableModels, setAvailableModels] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiHealth, setApiHealth] = useState(false);

  useEffect(() => {
    checkApiHealth();
    fetchAvailableModels();
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      setApiHealth(response.ok);
    } catch (err) {
      setApiHealth(false);
    }
  };

  const fetchAvailableModels = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/models`);
      if (response.ok) {
        const data = await response.json();
        setAvailableModels(data.models || []);
        if (data.models && data.models.length > 0) setSelectedModel(data.models[0]);
      }
    } catch (err) {
      console.error('Failed to fetch models:', err);
    }
  };

  const handleAnalyze = async () => {
    if (!message.trim()) { setError('Please enter a message'); return; }
    if (!selectedModel) { setError('Please select a model'); return; }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, model_name: selectedModel }),
      });
      if (!response.ok) throw new Error('Analysis failed');
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to analyze message');
    } finally {
      setLoading(false);
    }
  };

  const getRiskLabel = (score) => {
    if (score < 30) return 'Low Risk - Likely Legitimate';
    if (score < 60) return 'Medium Risk - Review Recommended';
    return 'High Risk - Likely Phishing';
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h3" sx={{ fontWeight: 'bold', mb: 1 }}>🔒 Email Phishing Detector</Typography>
        <Typography variant="subtitle1" color="textSecondary">AI-powered analysis to protect from phishing</Typography>
      </Box>

      {!apiHealth && <Alert severity="error" sx={{ mb: 3 }}>❌ API Server not responding</Alert>}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>Analyze Message</Typography>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Select Model</InputLabel>
              <Select value={selectedModel} label="Select Model" onChange={(e) => setSelectedModel(e.target.value)}>
                {availableModels.map((model) => <MenuItem key={model} value={model}>{model}</MenuItem>)}
              </Select>
            </FormControl>
            <TextField fullWidth multiline rows={6} placeholder="Paste message..." value={message} onChange={(e) => setMessage(e.target.value)} variant="outlined" sx={{ mb: 2 }} />
            <Button fullWidth variant="contained" color="primary" size="large" endIcon={<SendIcon />} onClick={handleAnalyze} disabled={loading || !apiHealth}>
              {loading ? 'Analyzing...' : 'Analyze'}
            </Button>
            {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
              <CircularProgress />
            </Box>
          ) : result ? (
            <Card elevation={3}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>Analysis Results</Typography>
                <RiskGaugeContainer>
                  <RiskGauge score={result.risk_score} />
                  <Typography variant="subtitle1" sx={{ mt: 2, textAlign: 'center' }}>{getRiskLabel(result.risk_score)}</Typography>
                </RiskGaugeContainer>
                <Box sx={{ my: 3, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                  <Typography variant="body2" color="textSecondary">Prediction:</Typography>
                  <Typography variant="h6" sx={{ fontWeight: 'bold' }}>{result.label === 'Phishing' ? '⚠️ Phishing' : '✅ Legitimate'}</Typography>
                </Box>
                <Box sx={{ my: 2 }}>
                  <Typography variant="body2" color="textSecondary">Explanation:</Typography>
                  <Typography variant="body1">{result.explanation}</Typography>
                </Box>
                {result.red_flags && result.red_flags.length > 0 && (
                  <Box sx={{ my: 2 }}>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>Detected Red Flags:</Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap' }}>
                      {result.red_flags.map((flag, idx) => <RedFlagBadge key={idx} flag={flag} />)}
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card elevation={3} sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="body1" color="textSecondary">Results will appear here</Typography>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Container>
  );
}

export default App;
