import re
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import pyodbc
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import uvicorn

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize FastAPI app
app = FastAPI(title="Order Prediction API")

# Load database configuration
def load_db_config():
    try:
        with open('config/database_config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading database config: {e}")
        return None

# Database connection management
class DatabaseManager:
    def __init__(self):
        self.config = load_db_config()
        if not self.config:
            raise Exception("Failed to load database configuration")

    def get_connection(self, server_id: str, database_id: str) -> Optional[pyodbc.Connection]:
        try:
            server_config = self.config['servers'].get(server_id)
            if not server_config:
                raise ValueError(f"Server {server_id} not found in configuration")

            db_config = server_config['databases'].get(database_id)
            if not db_config:
                raise ValueError(f"Database {database_id} not found in server {server_id}")

            conn_str = (
                f'DRIVER={{SQL Server}};'
                f'SERVER={server_config["name"]};'
                f'DATABASE={db_config["name"]};'
                f'UID={db_config["username"]};'
                f'PWD={db_config["password"]}'
            )
            return pyodbc.connect(conn_str)
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None

    def get_table_name(self, server_id: str, database_id: str, table_id: str) -> Optional[str]:
        try:
            return self.config['servers'][server_id]['databases'][database_id]['tables'][table_id]
        except KeyError:
            return None

# Request models
class PredictionRequest(BaseModel):
    server_id: str
    database_id: str
    table_id: str
    limit: Optional[int] = 100

class ServerInfo(BaseModel):
    server_id: str
    databases: List[str]

class DatabaseInfo(BaseModel):
    database_id: str
    tables: List[str]

# Initialize database manager
db_manager = DatabaseManager()

def prepare_prompt(df: pd.DataFrame) -> str:
    """Prepare prompt for Gemini API"""
    trend_columns = [col for col in df.columns if 'trend' in col.lower()]
    stats = df[trend_columns].describe()
    recent_trends = df[trend_columns].tail(5).to_dict()
    
    prompt = f"""
    Based on the following order trend data:
    
    Statistical Summary:
    {stats.to_string()}
    
    Recent Trends:
    {recent_trends}
    
    Previous Comments:
    {df['Journal_Comment'].tail(3).to_list() if 'Journal_Comment' in df.columns else 'No previous comments available'}
    
    Analyze the patterns and provide ONLY a JSON response with exactly two fields:
    1. "predicted_comment": A concise future order journal comment
    2. "reason": A brief explanation of why this prediction was made
    
    The response should be valid JSON and contain ONLY these two fields and no markdown(Ensure the comment is look similar to the previous comments).
    """
    return prompt

def get_prediction(prompt: str) -> Dict:
    """Get prediction from Gemini API"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        
        response_text = re.sub(r'```json\s*', '', response.text)
        response_text = re.sub(r'```', '', response_text)
        
        try:
            result = json.loads(response_text)
            return {
                "predicted_comment": result.get("predicted_comment", ""),
                "reason": result.get("reason", "")
            }
        except json.JSONDecodeError:
            return {
                "predicted_comment": "Error: Could not generate prediction",
                "reason": "Failed to parse AI response into JSON format"
            }
    except Exception as e:
        return {
            "predicted_comment": "Error: Could not generate prediction",
            "reason": str(e)
        }

def update_database(conn: pyodbc.Connection, table_name: str, prediction: Dict) -> bool:
    """Update the database with the new prediction"""
    try:
        cursor = conn.cursor()
        update_query = f"""
        UPDATE {table_name}
        SET Predicted_Comment = ?,
            Prediction_Reason = ?,
            Prediction_Date = ?
        WHERE Date = (
            SELECT MAX(Date)
            FROM {table_name}
        )
        """
        
        cursor.execute(update_query, (
            prediction["predicted_comment"],
            prediction["reason"],
            datetime.now()
        ))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating database: {e}")
        return False

# API Endpoints
@app.get("/servers")
async def list_servers():
    """List all available servers"""
    config = load_db_config()
    if not config:
        raise HTTPException(status_code=500, detail="Failed to load configuration")
    
    servers = []
    for server_id, server_info in config['servers'].items():
        databases = list(server_info['databases'].keys())
        servers.append(ServerInfo(server_id=server_id, databases=databases))
    return servers

@app.get("/servers/{server_id}/databases")
async def list_databases(server_id: str):
    """List all databases for a specific server"""
    config = load_db_config()
    if not config:
        raise HTTPException(status_code=500, detail="Failed to load configuration")
    
    server_config = config['servers'].get(server_id)
    if not server_config:
        raise HTTPException(status_code=404, detail=f"Server {server_id} not found")
    
    databases = []
    for db_id, db_info in server_config['databases'].items():
        tables = list(db_info['tables'].keys())
        databases.append(DatabaseInfo(database_id=db_id, tables=tables))
    return databases

@app.post("/predict")
async def generate_prediction(request: PredictionRequest):
    """Generate prediction for specified server, database, and table"""
    # Get table name from configuration
    table_name = db_manager.get_table_name(request.server_id, request.database_id, request.table_id)
    if not table_name:
        raise HTTPException(status_code=404, detail="Invalid server, database, or table combination")

    # Get database connection
    conn = db_manager.get_connection(request.server_id, request.database_id)
    if not conn:
        raise HTTPException(status_code=500, detail="Failed to connect to database")

    try:
        # Load data
        query = f"""
        SELECT TOP {request.limit} *
        FROM {table_name}
        ORDER BY Date DESC
        """
        df = pd.read_sql(query, conn)
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found in the specified table")

        # Generate prediction
        prompt = prepare_prompt(df)
        prediction = get_prediction(prompt)

        # Update database
        if update_database(conn, table_name, prediction):
            return {
                "predicted_comment": prediction["predicted_comment"],
                "reason": prediction["reason"],
                "status": "Database updated successfully"
            }
        else:
            return {
                "predicted_comment": prediction["predicted_comment"],
                "reason": prediction["reason"],
                "status": "Failed to update database"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 