import React, { useState } from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Typography,
  Box,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { OrderData } from '../types/api';

interface OrderTableProps {
  data: OrderData[];
  onOrderSelect: (order: OrderData) => void;
  selectedOrder: OrderData | null;
}

export const OrderTable: React.FC<OrderTableProps> = ({
  data,
  onOrderSelect,
  selectedOrder
}) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Get trend columns
  const trendColumns = Object.keys(data[0] || {})
    .filter(key => key.includes('TREND_LAG'))
    .sort((a, b) => {
      const numA = parseInt(a.replace('TREND_LAG', '').replace('_STRNT', ''), 10);
      const numB = parseInt(b.replace('TREND_LAG', '').replace('_STRNT', ''), 10);
      return numA - numB;
    });

  // Determine which columns to display
  const displayColumns = ['ORDERNUMBER', 'INGRD_GRP_NM', 'ORDERSTRENGTH', 'CUMULSTRENGTH'];
  
  return (
    <Paper sx={{ width: '100%', mb: 4, borderRadius: '8px', overflow: 'hidden' }}>
      <Typography variant="h2" sx={{ p: 2, backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
        Order Data
      </Typography>
      
      <TableContainer sx={{ maxHeight: 440 }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>Action</TableCell>
              {displayColumns.map((column) => (
                <TableCell key={column}>
                  {column === 'ORDERNUMBER' ? 'Order #' :
                   column === 'INGRD_GRP_NM' ? 'Ingredient Group' :
                   column === 'ORDERSTRENGTH' ? 'Order Str' :
                   column === 'CUMULSTRENGTH' ? 'Cumul. Str' :
                   column}
                </TableCell>
              ))}
              {trendColumns.slice(0, 4).map((column) => (
                <TableCell key={column}>
                  {`Trend ${column.replace('TREND_LAG', '').replace('_STRNT', '')}`}
                </TableCell>
              ))}
              <TableCell>Comment</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((row) => (
                <TableRow 
                  hover 
                  key={row.ORDERNUMBER}
                  selected={selectedOrder?.ORDERNUMBER === row.ORDERNUMBER}
                  sx={{ '&:hover': { cursor: 'pointer' } }}
                >
                  <TableCell>
                    <Tooltip title="View Details">
                      <IconButton 
                        size="small" 
                        color="primary"
                        onClick={() => onOrderSelect(row)}
                      >
                        <VisibilityIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                  
                  {displayColumns.map((column) => (
                    <TableCell key={`${row.ORDERNUMBER}-${column}`}>
                      {column === 'ORDERNUMBER' ? (
                        <Typography variant="body2" fontWeight={500}>
                          {row[column]}
                        </Typography>
                      ) : (
                        row[column]
                      )}
                    </TableCell>
                  ))}
                  
                  {trendColumns.slice(0, 4).map((column) => (
                    <TableCell key={`${row.ORDERNUMBER}-${column}`}>
                      {typeof row[column] === 'number' ? row[column].toFixed(2) : row[column]}
                    </TableCell>
                  ))}
                  
                  <TableCell sx={{ maxWidth: 300 }}>
                    <Box sx={{ maxHeight: 60, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      <Typography variant="body2" sx={{ wordWrap: 'break-word' }}>
                        {row.ORDER_JRNL_CMT_TXT || 'No comment'}
                      </Typography>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </TableContainer>
      
      <TablePagination
        rowsPerPageOptions={[10, 25, 50, 100]}
        component="div"
        count={data.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Paper>
  );
}; 