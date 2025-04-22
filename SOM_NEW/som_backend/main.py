from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import os
import logging
import pandas as pd
import pyodbc
import xmltodict
import re
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("OrderPredictionAPI")

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Create FastAPI app
app = FastAPI(
    title="Order Prediction API",
    description="API for AI Data Review",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Pydantic Models -----

class ConnectionData(BaseModel):
    server: str
    database: str
    username: str
    password: str

class Company(BaseModel):
    name: str
    server: str
    database: str
    username: str
    password: str

class PredictionRequest(BaseModel):
    order_number: str

class PredictionResponse(BaseModel):
    predicted_comment: str
    reason: str

class PredictionRequestWithConnection(BaseModel):
    """Combined prediction request with connection data"""
    order_number: str
    server: str
    database: str
    username: str
    password: str

# ----- Database Functions -----

def parse_connection_string(conn_str):
    """Parse SQL Server connection string into components"""
    try:
        # Extract server and database using regex
        server_match = re.search(r'data source=([^;]+)', conn_str, re.IGNORECASE)
        database_match = re.search(r'initial catalog=([^;]+)', conn_str, re.IGNORECASE)
        user_match = re.search(r'User ID=([^;]+)', conn_str, re.IGNORECASE)
        password_match = re.search(r'Password=([^;]+)', conn_str, re.IGNORECASE)
        
        return {
            'server': server_match.group(1) if server_match else None,
            'database': database_match.group(1) if database_match else None,
            'username': user_match.group(1) if user_match else None,
            'password': password_match.group(1) if password_match else None
        }
    except Exception as e:
        logger.error(f"Error parsing connection string: {str(e)}")
        return None

def load_company_config():
    """Load and parse the company configuration XML file"""
    try:
        with open('dataaccessconfig.xml', 'r') as file:
            config = xmltodict.parse(file.read())
            companies = []
            
            for company in config['Config']['Company']:
                conn_str = company.get('ConnectionString', '')
                conn_data = parse_connection_string(conn_str)
                
                if conn_data:
                    companies.append({
                        'name': company['Name'],
                        'server': conn_data['server'],
                        'database': conn_data['database'],
                        'username': conn_data['username'],
                        'password': conn_data['password']
                    })
            
            return companies
    except Exception as e:
        logger.error(f"Error loading company configuration: {str(e)}")
        return []

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

def test_connection(server, database, username, password):
    """Test connection to a SQL Server"""
    try:
        conn_str = f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
        conn = pyodbc.connect(conn_str, timeout=3)  # 3 second timeout
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return False

def get_databases(server, username, password):
    """Get list of databases for the selected company"""
    try:
        conn_str = f"DRIVER={{SQL Server}};SERVER={server};UID={username};PWD={password}"
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Get user databases (exclude system databases)
        cursor.execute("""
            SELECT name 
            FROM sys.databases 
            WHERE database_id > 4 
                AND state = 0  -- Online databases only
                AND is_read_only = 0  -- Exclude read-only databases
            ORDER BY name
        """)
        
        databases = [row[0] for row in cursor.fetchall()]
        conn.close()
        return databases
    except Exception as e:
        logger.error(f"Error fetching databases: {str(e)}")
        return []

def load_data(server, database, username, password):
    """Load and prepare data from SQL Server using the specific query"""
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
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return None

# ----- Prediction Functions -----

def prepare_prompt(selected_record, all_records):
    """Prepare prompt for Gemini API using the selected record and all other records"""
    if not all_records or len(all_records) == 0:
        return None
    
    if selected_record is None:
        return None
        
    # Get trend columns
    trend_columns = [col for col in all_records[0].keys() if 'TREND' in col]
    
    # Format the selected record data
    selected_trends = {col: float(selected_record[col]) for col in trend_columns}
    
    # Get other records (excluding the selected one) - limit to a reasonable number
    other_records = [r for r in all_records if r['ORDERNUMBER'] != selected_record['ORDERNUMBER']][:500]
    
    # Format other records as a list of dictionaries with their trends and comments
    other_records_data = []
    for record in other_records:
        record_data = {
            "order_number": record['ORDERNUMBER'],
            "comment": record['ORDER_JRNL_CMT_TXT'],
            "trends": {col: float(record[col]) for col in trend_columns}
        }
        other_records_data.append(record_data)
    
    prompt = f"""
    Based on the following order data:

    Selected Order Number: {selected_record['ORDERNUMBER']}
    
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

def generate_prediction_for_record(order_number, all_records):
    """Generate AI prediction for a specific record"""
    logger.info(f"Starting prediction generation for order {order_number}")
    
    # Check for required environment variables
    if not GOOGLE_API_KEY:
        logger.error("Missing GOOGLE_API_KEY environment variable")
        return {
            "predicted_comment": "Error: Missing environment variables",
            "reason": "Please set GOOGLE_API_KEY in .env file"
        }
    
    # Find the record with the given order number
    selected_record = next((r for r in all_records if r['ORDERNUMBER'] == order_number), None)
    
    if not selected_record:
        return {
            "predicted_comment": "Error: Order not found",
            "reason": f"Order number {order_number} was not found in the dataset"
        }
    
    # Generate prompt with selected record and remaining records
    prompt = prepare_prompt(selected_record, all_records)
    prediction = get_prediction(prompt)
    
    return prediction

# ----- API Routes -----

@app.get("/")
def read_root():
    return {"message": "Welcome to the Order Prediction API"}

@app.get("/companies", response_model=List[Company])
def get_companies():
    """Get list of available companies from configuration"""
    companies = load_company_config()
    if not companies:
        raise HTTPException(status_code=404, detail="No companies found in configuration")
    return companies

@app.get("/status/{company_name}")
def get_server_status(company_name: str):
    """Get server status for a company"""
    companies = load_company_config()
    company = next((c for c in companies if c['name'] == company_name), None)
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    is_online = test_connection(
        company['server'],
        company['database'],
        company['username'],
        company['password']
    )
    
    return {"company": company_name, "online": is_online}

@app.get("/databases/{company_name}")
def get_company_databases(company_name: str):
    """Get list of databases for the selected company"""
    companies = load_company_config()
    company = next((c for c in companies if c['name'] == company_name), None)
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    databases = get_databases(
        company['server'],
        company['username'],
        company['password']
    )
    
    if not databases:
        raise HTTPException(status_code=404, detail="No databases found or connection failed")
    
    return {"company": company_name, "databases": databases}

@app.post("/data")
def get_data(connection: ConnectionData):
    """Load data from the specified database"""
    data = load_data(
        connection.server,
        connection.database,
        connection.username,
        connection.password
    )
    
    if not data:
        raise HTTPException(status_code=404, detail="No data found or connection failed")
    
    return {"count": len(data), "data": data}

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequestWithConnection):
    """Generate prediction for a specific order"""
    # Load the data
    data = load_data(
        request.server,
        request.database,
        request.username,
        request.password
    )
    
    if not data:
        raise HTTPException(status_code=404, detail="No data found or connection failed")
    
    # Generate prediction
    prediction = generate_prediction_for_record(request.order_number, data)
    
    return prediction

# For testing without a configuration file
@app.post("/test-connection")
def test_db_connection(connection: ConnectionData):
    """Test connection to a database"""
    is_online = test_connection(
        connection.server,
        connection.database,
        connection.username,
        connection.password
    )
    
    return {"online": is_online}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 