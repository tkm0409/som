// Company type
export interface Company {
  name: string;
  server: string;
  database: string;
  username: string;
  password: string;
}

// Database connection type
export interface ConnectionData {
  server: string;
  database: string;
  username: string;
  password: string;
}

// Order data type
export interface OrderData {
  ORDERNUMBER: string;
  ORDER_JRNL_CMT_TXT: string;
  ORDERSTRENGTH: number;
  CUMULSTRENGTH: number;
  INGRD_GRP_NM: string;
  [key: string]: any; // For trend columns (e.g., TREND_LAG1_STRNT)
}

// Prediction request type
export interface PredictionRequest {
  order_number: string;
}

// Prediction response type
export interface PredictionResponse {
  predicted_comment: string;
  reason: string;
} 