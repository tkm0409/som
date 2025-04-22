import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { OrderTable } from './components/OrderTable';
import { PredictionCard } from './components/PredictionCard';
import { Company, ConnectionData, OrderData } from './types/api';
import { api } from './services/api';
import { CircularProgress, Alert, Typography, Paper } from '@mui/material';

// Create a theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#4263eb',
    },
    secondary: {
      main: '#1c2a5e',
    },
    background: {
      default: '#f8fafc',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: "'Inter', 'Roboto', 'Helvetica', sans-serif",
    h1: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '1.5rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.2rem',
      fontWeight: 600,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
          borderRadius: '8px',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '4px',
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderColor: '#e2e8f0',
          padding: '12px 16px',
        },
        head: {
          backgroundColor: '#f8fafc',
          fontWeight: 600,
        },
      },
    },
  },
});

function App() {
  // State for companies, databases, and data
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [databases, setDatabases] = useState<string[]>([]);
  const [selectedDatabase, setSelectedDatabase] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<OrderData[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<OrderData | null>(null);
  const [prediction, setPrediction] = useState<{ predicted_comment: string; reason: string } | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(true);

  // Flag to track if Patterson data has been loaded
  const [pattersonLoaded, setPattersonLoaded] = useState<boolean>(false);

  // Load companies on initial render
  useEffect(() => {
    async function loadCompanies() {
      try {
        setLoading(true);
        setError(null);
        const companiesData = await api.getCompanies();
        setCompanies(companiesData);
        
        // Find Patterson company
        const pattersonCompany = companiesData.find(c => c.name === "Patterson");
        if (pattersonCompany && !pattersonLoaded) {
          setSelectedCompany(pattersonCompany);
        }
      } catch (err) {
        console.error('Error loading companies:', err);
        setError('Failed to load companies. Please check server connection.');
      } finally {
        setLoading(false);
      }
    }

    loadCompanies();
  }, [pattersonLoaded]);

  // Load databases when a company is selected
  useEffect(() => {
    async function loadDatabases() {
      if (!selectedCompany) return;

      try {
        setLoading(true);
        setError(null);
        const result = await api.getDatabases(selectedCompany.name);
        setDatabases(result.databases);
        
        // If Patterson is selected and databases are loaded, select pSUS_Patterson_Mart database
        if (selectedCompany.name === "Patterson" && result.databases.includes("pSUS_Patterson_Mart") && !pattersonLoaded) {
          setSelectedDatabase("pSUS_Patterson_Mart");
        }
      } catch (err) {
        console.error('Error loading databases:', err);
        setError('Failed to load databases. Please check server connection.');
        setDatabases([]);
      } finally {
        setLoading(false);
      }
    }

    loadDatabases();
  }, [selectedCompany, pattersonLoaded]);

  // Automatically load Patterson data once the DB is selected
  useEffect(() => {
    async function autoLoadPattersonData() {
      if (
        !pattersonLoaded && 
        selectedCompany && 
        selectedCompany.name === "Patterson" && 
        selectedDatabase === "pSUS_Patterson_Mart"
      ) {
        await loadData();
        setPattersonLoaded(true);
      }
    }
    
    autoLoadPattersonData();
  }, [selectedCompany, selectedDatabase, pattersonLoaded]);

  // Handle company selection
  const handleCompanySelect = (company: Company) => {
    setSelectedCompany(company);
    setSelectedDatabase('');
    setData([]);
    setSelectedOrder(null);
    setPrediction(null);
  };

  // Handle database selection
  const handleDatabaseSelect = (database: string) => {
    setSelectedDatabase(database);
  };

  // Toggle sidebar visibility
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Load data from selected company and database
  const loadData = async () => {
    if (!selectedCompany || !selectedDatabase) {
      setError('Please select both a company and database');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const connectionData: ConnectionData = {
        server: selectedCompany.server,
        database: selectedDatabase,
        username: selectedCompany.username,
        password: selectedCompany.password,
      };
      
      const result = await api.getData(connectionData);
      setData(result.data);
    } catch (err) {
      console.error('Error loading data:', err);
      setError('Failed to load data. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  // Handle order selection
  const handleOrderSelect = (order: OrderData) => {
    setSelectedOrder(order);
    setPrediction(null);
  };

  // Generate prediction for the selected order
  const generatePrediction = async () => {
    if (!selectedCompany || !selectedDatabase || !selectedOrder) {
      setError('Please select an order to generate a prediction');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const connectionData: ConnectionData = {
        server: selectedCompany.server,
        database: selectedDatabase,
        username: selectedCompany.username,
        password: selectedCompany.password,
      };
      
      // Fix for 422 error - make separate API call to get prediction
      const result = await api.predict(
        { order_number: selectedOrder.ORDERNUMBER }, 
        connectionData
      );
      
      setPrediction(result);
    } catch (err: any) {
      console.error('Error generating prediction:', err);
      // Show more specific error message from API response if available
      const errorMessage = err.response?.data?.detail || 'Failed to generate prediction. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Filter data based on search term
  const filteredData = data.filter((order) => {
    if (!searchTerm) return true;
    
    // Search across all string columns
    return Object.keys(order).some((key) => {
      const value = order[key];
      return typeof value === 'string' && value.toLowerCase().includes(searchTerm.toLowerCase());
    });
  });

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', minHeight: '100vh' }}>
        {/* Sidebar */}
        <Sidebar
          companies={companies}
          selectedCompany={selectedCompany}
          databases={databases}
          selectedDatabase={selectedDatabase}
          onCompanySelect={handleCompanySelect}
          onDatabaseSelect={handleDatabaseSelect}
          onLoadData={loadData}
          loading={loading}
          open={sidebarOpen}
          onClose={toggleSidebar}
        />
        
        {/* Main content */}
        <Box 
          component="main" 
          sx={{ 
            flexGrow: 1, 
            p: 3,
            marginLeft: sidebarOpen ? 0 : -35,
            transition: 'margin 0.2s ease-in-out'
          }}
        >
          <Header 
            searchTerm={searchTerm} 
            onSearchChange={(value) => setSearchTerm(value)}
            sidebarOpen={sidebarOpen}
            onToggleSidebar={toggleSidebar}
          />
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
              <CircularProgress />
            </Box>
          ) : data.length === 0 ? (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">
                Welcome to AI Data Review
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
                Select a server and database from the sidebar, then click "Load Data" to get started.
              </Typography>
            </Paper>
          ) : (
            <>
              {/* Order data table */}
              <OrderTable 
                data={filteredData}
                onOrderSelect={handleOrderSelect}
                selectedOrder={selectedOrder}
              />
              
              {/* Display prediction if available */}
              {selectedOrder && (
                <PredictionCard
                  selectedOrder={selectedOrder}
                  prediction={prediction}
                  onGeneratePrediction={generatePrediction}
                  loading={loading}
                />
              )}
            </>
          )}
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App; 