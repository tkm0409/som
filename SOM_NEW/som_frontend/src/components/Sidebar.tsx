import React from 'react';
import { 
  Box, 
  Drawer, 
  Typography, 
  List, 
  ListItem, 
  ListItemText, 
  Select, 
  MenuItem, 
  FormControl, 
  InputLabel, 
  Button, 
  Divider,
  SelectChangeEvent,
  CircularProgress
} from '@mui/material';
import { Company } from '../types/api';

interface SidebarProps {
  companies: Company[];
  selectedCompany: Company | null;
  databases: string[];
  selectedDatabase: string;
  onCompanySelect: (company: Company) => void;
  onDatabaseSelect: (database: string) => void;
  onLoadData: () => void;
  loading: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  companies,
  selectedCompany,
  databases,
  selectedDatabase,
  onCompanySelect,
  onDatabaseSelect,
  onLoadData,
  loading
}) => {
  const handleCompanyChange = (event: SelectChangeEvent<string>) => {
    const companyName = event.target.value;
    const company = companies.find(c => c.name === companyName);
    if (company) {
      onCompanySelect(company);
    }
  };

  const handleDatabaseChange = (event: SelectChangeEvent<string>) => {
    onDatabaseSelect(event.target.value);
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: 280,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: 280,
          boxSizing: 'border-box',
          backgroundColor: '#f8fafc',
          borderRight: '1px solid #e2e8f0',
        },
      }}
    >
      <Box sx={{ p: 3 }}>
        <Typography variant="h1" component="h1" sx={{ mb: 3, color: '#1c2a5e' }}>
          AI Data Review
        </Typography>

        <Divider sx={{ mb: 3 }} />

        <Box sx={{ mb: 3 }}>
          <FormControl fullWidth size="small" sx={{ mb: 2 }}>
            <InputLabel id="company-select-label">Server</InputLabel>
            <Select
              labelId="company-select-label"
              id="company-select"
              value={selectedCompany?.name || ''}
              label="Server"
              onChange={handleCompanyChange}
              disabled={loading || companies.length === 0}
            >
              {companies.map((company) => (
                <MenuItem key={company.name} value={company.name}>
                  {company.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth size="small" sx={{ mb: 2 }}>
            <InputLabel id="database-select-label">Database</InputLabel>
            <Select
              labelId="database-select-label"
              id="database-select"
              value={selectedDatabase}
              label="Database"
              onChange={handleDatabaseChange}
              disabled={loading || !selectedCompany || databases.length === 0}
            >
              {databases.map((database) => (
                <MenuItem key={database} value={database}>
                  {database}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Button
            variant="contained"
            fullWidth
            onClick={onLoadData}
            disabled={loading || !selectedCompany || !selectedDatabase}
            sx={{ mt: 1 }}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Load Data'}
          </Button>
        </Box>

        <Divider sx={{ mb: 3 }} />

        <Typography variant="h3" component="h3" sx={{ mb: 2 }}>
          Debug Mode
        </Typography>

        <Button
          variant="outlined"
          size="small"
          fullWidth
          sx={{ mb: 2 }}
        >
          Toggle Debug Mode
        </Button>
      </Box>
    </Drawer>
  );
}; 