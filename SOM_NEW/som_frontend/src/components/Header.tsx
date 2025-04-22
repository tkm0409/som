import React from 'react';
import { AppBar, Toolbar, Typography, TextField, Box, InputAdornment, IconButton } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import MenuIcon from '@mui/icons-material/Menu';

interface HeaderProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
}

export const Header: React.FC<HeaderProps> = ({ 
  searchTerm, 
  onSearchChange, 
  sidebarOpen, 
  onToggleSidebar 
}) => {
  return (
    <Box sx={{ mb: 3 }}>
      <AppBar position="static" color="transparent" elevation={0} sx={{ backgroundColor: 'white' }}>
        <Toolbar>
          <IconButton 
            edge="start" 
            color="inherit" 
            aria-label="menu" 
            onClick={onToggleSidebar}
            sx={{ mr: 2, display: sidebarOpen ? 'none' : 'flex' }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h1" component="h1" sx={{ flexGrow: 1, color: '#1c2a5e' }}>
            AI Data Review
          </Typography>
          
          <TextField
            placeholder="Search orders"
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            size="small"
            sx={{
              width: 300,
              '& .MuiOutlinedInput-root': {
                borderRadius: '8px',
                backgroundColor: '#f8fafc',
              },
            }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
            }}
          />
        </Toolbar>
      </AppBar>
    </Box>
  );
}; 