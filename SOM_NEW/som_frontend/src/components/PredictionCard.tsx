import React, { useState } from 'react';
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
  AccordionDetails,
  Chip,
  Fade,
  Skeleton
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import ScienceIcon from '@mui/icons-material/Science';
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
  const [showPlaceholder, setShowPlaceholder] = useState(false);

  // Get trend columns
  const trendColumns = Object.keys(selectedOrder)
    .filter(key => key.includes('TREND_LAG'))
    .sort((a, b) => {
      const numA = parseInt(a.replace('TREND_LAG', '').replace('_STRNT', ''), 10);
      const numB = parseInt(b.replace('TREND_LAG', '').replace('_STRNT', ''), 10);
      return numA - numB;
    });
    
  // Show placeholder when loading starts
  React.useEffect(() => {
    if (loading && !prediction) {
      setShowPlaceholder(true);
    }
  }, [loading, prediction]);

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
        
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-start' }}>
          <Button
            variant="contained"
            color="primary"
            onClick={onGeneratePrediction}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <AutoFixHighIcon />}
            sx={{ 
              px: 3, 
              py: 1, 
              borderRadius: '20px',
              boxShadow: '0 4px 6px rgba(66, 99, 235, 0.2)',
              background: 'linear-gradient(45deg, #4263eb 30%, #5e81f4 90%)',
              '&:hover': {
                background: 'linear-gradient(45deg, #3656d7 30%, #4263eb 90%)',
                boxShadow: '0 6px 8px rgba(66, 99, 235, 0.3)',
              }
            }}
          >
            {loading ? 'AI Magic in Progress...' : 'Generate AI Prediction'}
            {!loading && <Chip 
              label="AI" 
              size="small" 
              color="secondary" 
              sx={{ ml: 1, height: '20px', background: 'rgba(255, 255, 255, 0.3)', color: 'white' }} 
            />}
          </Button>
        </Box>
        
        {/* Loading placeholder or prediction */}
        {(loading || prediction || showPlaceholder) && (
          <Card 
            sx={{ 
              mt: 3, 
              border: '1px solid #e2e8f0', 
              boxShadow: loading ? '0 0 10px rgba(66, 99, 235, 0.3)' : 'none',
              transition: 'all 0.3s ease-in-out'
            }}
          >
            <CardHeader 
              title={loading ? "AI Generating Prediction..." : "AI Predicted Comment"}
              avatar={loading ? <ScienceIcon /> : <AutoFixHighIcon />}
              sx={{ 
                backgroundColor: loading ? '#e6f0ff' : '#f0f9ff', 
                borderBottom: '1px solid #e2e8f0',
                py: 1.5
              }} 
            />
            
            <CardContent>
              {loading ? (
                <Fade in={loading}>
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <CircularProgress size={24} sx={{ mr: 2 }} />
                      <Typography variant="subtitle1" color="primary">
                        AI is analyzing order patterns...
                      </Typography>
                    </Box>
                    <Skeleton variant="text" height={30} animation="wave" />
                    <Skeleton variant="text" height={30} animation="wave" width="80%" />
                    <Skeleton variant="text" height={30} animation="wave" width="90%" />
                    
                    <Divider sx={{ my: 2 }} />
                    
                    <Typography variant="h6" gutterBottom>
                      Reasoning
                    </Typography>
                    <Skeleton variant="text" height={20} animation="wave" />
                    <Skeleton variant="text" height={20} animation="wave" />
                    <Skeleton variant="text" height={20} animation="wave" width="70%" />
                  </Box>
                </Fade>
              ) : (
                prediction && (
                  <Box>
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
                  </Box>
                )
              )}
            </CardContent>
          </Card>
        )}
      </Box>
    </Paper>
  );
} 