import axios from 'axios';
import { Company, ConnectionData, OrderData, PredictionRequest, PredictionResponse } from '../types/api';

// Create an axios instance with default config
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// API methods
export const api = {
  // Get all companies
  getCompanies: async (): Promise<Company[]> => {
    const response = await apiClient.get<Company[]>('/companies');
    return response.data;
  },

  // Get server status for a company
  getServerStatus: async (companyName: string): Promise<{ company: string; online: boolean }> => {
    const response = await apiClient.get(`/status/${companyName}`);
    return response.data;
  },

  // Get databases for a company
  getDatabases: async (companyName: string): Promise<{ company: string; databases: string[] }> => {
    const response = await apiClient.get(`/databases/${companyName}`);
    return response.data;
  },

  // Get order data from a database
  getData: async (connection: ConnectionData): Promise<{ count: number; data: OrderData[] }> => {
    const response = await apiClient.post('/data', connection);
    return response.data;
  },

  // Generate prediction for an order
  predict: async (
    order: PredictionRequest,
    connection: ConnectionData
  ): Promise<PredictionResponse> => {
    const response = await apiClient.post('/predict', { ...order, ...connection });
    return response.data;
  },

  // Test database connection
  testConnection: async (connection: ConnectionData): Promise<{ online: boolean }> => {
    const response = await apiClient.post('/test-connection', connection);
    return response.data;
  },
}; 