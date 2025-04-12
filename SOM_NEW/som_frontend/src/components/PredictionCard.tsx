import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Button,
  Divider,
  CircularProgress,
  Card,
  CardContent,
  CardHeader,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { OrderData } from '../types/api';

interface PredictionCardProps {
  selectedOrder: OrderData;
  prediction: { predicted_comment: string; reason: string } | null;
  onGeneratePrediction: () => void;
  loading: boolean;
}

export const PredictionCard: React.FC<PredictionCardProps> = ({
  selectedOrder,
  prediction,
  onGeneratePrediction,
  loading
}) => {
  // Get trend columns
  const trendColumns = Object.keys(selectedOrder)
    .filter(key => key.includes('TREND_LAG'))
    .sort((a, b) => {
      const numA = parseInt(a.replace('TREND_LAG', '').replace('_STRNT', ''), 10);
      const numB = parseInt(b.replace('TREND_LAG', '').replace('_STRNT', ''), 10);
      return numA - numB;
    });

  return (
    <Paper sx={{ borderRadius: '8px', overflow: 'hidden', mb: 4 }}>
      <Box sx={{ p: 2, backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
        <Typography variant="h2">Selected Order</Typography>
      </Box>
      
      <Box sx={{ p: 3 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Order Details
          </Typography>
          
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
            <Typography variant="body1">
              <strong>Order Number:</strong> {selectedOrder.ORDERNUMBER}
            </Typography>
            <Typography variant="body1">
              <strong>Ingredient Group:</strong> {selectedOrder.INGRD_GRP_NM}
            </Typography>
            <Typography variant="body1">
              <strong>Order Strength:</strong> {selectedOrder.ORDERSTRENGTH}
            </Typography>
            <Typography variant="body1">
              <strong>Cumulative Strength:</strong> {selectedOrder.CUMULSTRENGTH}
            </Typography>
          </Box>
        </Box>
        
        <Accordion defaultExpanded>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">Trend Data</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 2 }}>
              {trendColumns.map((column) => (
                <Typography key={column} variant="body2">
                  <strong>Trend {column.replace('TREND_LAG', '').replace('_STRNT', '')}:</strong>{' '}
                  {typeof selectedOrder[column] === 'number' 
                    ? selectedOrder[column].toFixed(2) 
                    : selectedOrder[column]}
                </Typography>
              ))}
            </Box>
          </AccordionDetails>
        </Accordion>
        
        <Accordion defaultExpanded sx={{ mt: 2 }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">Comment</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
              {selectedOrder.ORDER_JRNL_CMT_TXT || 'No comment available'}
            </Typography>
          </AccordionDetails>
        </Accordion>
        
        <Box sx={{ mt: 3 }}>
          <Button
            variant="contained"
            color="primary"
            onClick={onGeneratePrediction}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
          >
            {loading ? 'Generating...' : 'Generate AI Comment Prediction'}
          </Button>
        </Box>
        
        {prediction && (
          <Card sx={{ mt: 3, border: '1px solid #e2e8f0', boxShadow: 'none' }}>
            <CardHeader 
              title="AI Predicted Comment" 
              sx={{ 
                backgroundColor: '#f0f9ff', 
                borderBottom: '1px solid #e2e8f0',
                py: 1.5
              }} 
            />
            <CardContent>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', mb: 2 }}>
                {prediction.predicted_comment}
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="h6" gutterBottom>
                Reasoning
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
                {prediction.reason}
              </Typography>
            </CardContent>
          </Card>
        )}
      </Box>
    </Paper>
  );
} 