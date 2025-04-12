import re
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import pyodbc
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("order_prediction.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("OrderPrediction")

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

def get_db_connection(server, database, username, password):
    """Create and return a database connection"""
    try:
        conn_str = (
            f'DRIVER={{SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password}'
        )
        return pyodbc.connect(conn_str)
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def load_data(server, database, username, password):
    """Load and prepare data from SQL Server using the specific query"""
    start_time = time.time()
    try:
        conn = get_db_connection(server, database, username, password)
        if conn is None:
            return None
            
        # Query to get the data
        query = """
        SELECT TOP 1000
            j.ORDER_JRNL_CMT_TXT,
            hist.ORDERNUMBER,
          hist.ORDERSTRENGTH,
          hist.CUMULSTRENGTH,
          i.INGRD_GRP_NM,
            hist.TREND_LAG12_STRNT,
            hist.TREND_LAG11_STRNT,
            hist.TREND_LAG10_STRNT,
            hist.TREND_LAG9_STRNT,
            hist.TREND_LAG8_STRNT,
            hist.TREND_LAG7_STRNT,
            hist.TREND_LAG6_STRNT,
            hist.TREND_LAG5_STRNT,
            hist.TREND_LAG4_STRNT,
            hist.TREND_LAG3_STRNT,
            hist.TREND_LAG2_STRNT,
            hist.TREND_LAG1_STRNT
        FROM 
            NEW_ATTRIBUTES_TBL_HIST hist
            INNER JOIN SUS_ORDER_TRANS_HDR h ON h.ORDER_CD = hist.ORDERNUMBER
            INNER JOIN SUS_ORDER_TRANS_DETL d ON h.ORDER_HDR_ID = d.ORDER_HDR_ID AND d.INGRD_GRP_ID = hist.INGRD_GRP_ID
            INNER JOIN SUS_ORDER_JRNL j ON j.ORDER_HDR_ID = d.ORDER_HDR_ID AND j.INGRD_GRP_ID = d.INGRD_GRP_ID
            inner join SUS_ORDER_JRNL_TYP k on k.ORDER_JRNL_TYP_ID= j.ORDER_JRNL_TYP_ID 
      inner join SUS_INGRD_FMLY_GRP i on i.INGRD_GRP_ID=hist.INGRD_GRP_ID 
        WHERE 
            k.ORDER_JRNL_TYP_TXT in ('Release','Comment','First Approval','Second Approval') and d.ORDER_STATUS_CD in ('P','C','I') and d.ORDER_SCORE_FCT<>-2
    order by 1 desc
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        # Check if we got any data
        if df.empty:
            logger.warning("No data returned from the query")
            return None
            
        # Clean and prepare the data
        # Convert trend columns to numeric, handling any non-numeric values
        trend_columns = [col for col in df.columns if 'TREND' in col]
        for col in trend_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Remove any rows where all trend values are NaN
        df = df.dropna(subset=trend_columns, how='all')
        
        # Sort by the most recent trend
        if 'TREND_LAG1_STRNT' in df.columns:
            df = df.sort_values('TREND_LAG1_STRNT', ascending=False)
        
        elapsed_time = time.time() - start_time
        logger.info(f"Data loaded successfully in {elapsed_time:.2f} seconds. Shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return None

def prepare_prompt(selected_record, df):
    """Prepare prompt for Gemini API using the selected record and all other records"""
    if df is None or df.empty:
        return None
    
    if selected_record is None:
        return None
        
    # Get trend columns
    trend_columns = [col for col in df.columns if 'TREND' in col]
    
    # Format the selected record data
    selected_trends = {col: float(selected_record[col]) for col in trend_columns}
    
    # Get other records (excluding the selected one) - limit to a reasonable number
    other_records = df[df.ORDERNUMBER != selected_record.ORDERNUMBER].head(500).copy()
    
    # Format other records as a list of dictionaries with their trends and comments
    other_records_data = []
    for _, record in other_records.iterrows():
        record_data = {
            "order_number": record.ORDERNUMBER,
            "comment": record.ORDER_JRNL_CMT_TXT,
            "trends": {col: float(record[col]) for col in trend_columns}
        }
        other_records_data.append(record_data)
    
    prompt = f"""
    Based on the following order data:

    Selected Order Number: {selected_record.ORDERNUMBER}
    
    Selected Order Trend Data:
    {json.dumps(selected_trends, indent=2)}

    Other Recent Orders with Comments:
    {json.dumps(other_records_data, indent=2)}

    Analyze the patterns in the other orders and predict a journal comment for the selected order.
    Consider how the trend values of the selected order compare to those orders where comments are already available.
    Look for similar trend patterns and use the corresponding comments as a guide.

    Return ONLY a valid JSON object with exactly these two fields:
    1. "predicted_comment": A concise, specific journal comment for the selected order that matches the style and terminology of the other order comments
    2. "reason": A brief explanation of why this prediction was made, identifying which other order(s) had similar trend patterns

    The response must be valid JSON without any markdown formatting, explanatory text, or additional fields.
    """
    return prompt

def get_prediction(prompt):
    """Get prediction from Gemini API"""
    start_time = time.time()
    if prompt is None:
        return {
            "predicted_comment": "Error: No data available for prediction",
            "reason": "Failed to generate prompt due to missing or empty data"
        }
        
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        
        # Remove markdown formatting
        response_text = re.sub(r'```json\s*', '', response.text)
        response_text = re.sub(r'```', '', response_text)
        
        # Try to parse the response as JSON
        try:
            result = json.loads(response_text)
            # Ensure only the required fields are present
            elapsed_time = time.time() - start_time
            logger.info(f"Prediction generated successfully in {elapsed_time:.2f} seconds")
            return {
                "predicted_comment": result.get("predicted_comment", ""),
                "reason": result.get("reason", "")
            }
        except json.JSONDecodeError:
            # If response is not valid JSON, create a structured response
            logger.error(f"Failed to parse AI response as JSON: {response_text}")
            return {
                "predicted_comment": "Error: Could not generate prediction",
                "reason": "Failed to parse AI response into JSON format"
            }
            
    except Exception as e:
        logger.error(f"Error getting prediction: {e}")
        return {
            "predicted_comment": "Error: Could not generate prediction",
            "reason": str(e)
        }

def generate_prediction_for_record(selected_record, df):
    """Generate AI prediction for a specific record"""
    start_time = time.time()
    logger.info(f"Starting prediction generation for order {selected_record.ORDERNUMBER}")
    
    # Check for required environment variables
    if not GOOGLE_API_KEY:
        logger.error("Missing GOOGLE_API_KEY environment variable")
        return {
            "predicted_comment": "Error: Missing environment variables",
            "reason": "Please set GOOGLE_API_KEY in .env file"
        }
    
    # Generate prompt with selected record and remaining records
    prompt = prepare_prompt(selected_record, df)
    prediction = get_prediction(prompt)
    
    elapsed_time = time.time() - start_time
    logger.info(f"Prediction generation completed in {elapsed_time:.2f} seconds")
    
    return prediction

if __name__ == "__main__":
    # Check for required environment variables
    required_vars = ['SQL_SERVER', 'SQL_DATABASE', 'SQL_USERNAME', 'SQL_PASSWORD', 'GOOGLE_API_KEY']
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        print(json.dumps({
            "predicted_comment": "Error: Missing environment variables",
            "reason": f"Please set the following variables in .env file: {', '.join(missing_vars)}"
        }))
        exit() 