import re
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import pyodbc
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# SQL Server configuration
SQL_SERVER = os.getenv('SQL_SERVER')
SQL_DATABASE = os.getenv('SQL_DATABASE')
SQL_USERNAME = os.getenv('SQL_USERNAME')
SQL_PASSWORD = os.getenv('SQL_PASSWORD')
SQL_TABLE = os.getenv('SQL_TABLE', 'OrderTrends')  # Default table name

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn_str = (
            f'DRIVER={{SQL Server}};'
            f'SERVER={SQL_SERVER};'
            f'DATABASE={SQL_DATABASE};'
            f'UID={SQL_USERNAME};'
            f'PWD={SQL_PASSWORD}'
        )
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def load_data():
    """Load and prepare data from SQL Server"""
    try:
        conn = get_db_connection()
        if conn is None:
            return None
            
        # Query to get the data
        query = f"""
        SELECT *
        FROM {SQL_TABLE}
        ORDER BY Date DESC
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def prepare_prompt(df):
    """Prepare prompt for Gemini API"""
    # Get trend columns
    trend_columns = [col for col in df.columns if 'trend' in col.lower()]
    
    # Calculate basic statistics
    stats = df[trend_columns].describe()
    
    # Get recent trends
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

def get_prediction(prompt):
    """Get prediction from Gemini API"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        print(response.text)

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
            return {
                "predicted_comment": "Error: Could not generate prediction",
                "reason": "Failed to parse AI response into JSON format"
            }
            
    except Exception as e:
        return {
            "predicted_comment": "Error: Could not generate prediction",
            "reason": str(e)
        }

def update_database(prediction):
    """Update the database with the new prediction"""
    try:
        conn = get_db_connection()
        if conn is None:
            return False
            
        cursor = conn.cursor()
        
        # Update query - assuming there's a Date column for the latest record
        update_query = f"""
        UPDATE {SQL_TABLE}
        SET Predicted_Comment = ?,
            Prediction_Reason = ?,
            Prediction_Date = ?
        WHERE Date = (
            SELECT MAX(Date)
            FROM {SQL_TABLE}
        )
        """
        
        cursor.execute(update_query, (
            prediction["predicted_comment"],
            prediction["reason"],
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating database: {e}")
        return False

def main():
    # Check for required environment variables
    required_vars = ['GOOGLE_API_KEY', 'SQL_SERVER', 'SQL_DATABASE', 'SQL_USERNAME', 'SQL_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(json.dumps({
            "predicted_comment": "Error: Missing environment variables",
            "reason": f"Please set the following variables in .env file: {', '.join(missing_vars)}"
        }))
        return
    
    # Load data
    df = load_data()
    if df is None:
        print(json.dumps({
            "predicted_comment": "Error: Could not load data",
            "reason": "Failed to read from SQL Server"
        }))
        return
    
    # Get prediction
    prompt = prepare_prompt(df)
    prediction = get_prediction(prompt)
    
    # Update database
    if update_database(prediction):
        print(json.dumps({
            "predicted_comment": prediction["predicted_comment"],
            "reason": prediction["reason"],
            "status": "Database updated successfully"
        }, indent=2))
    else:
        print(json.dumps({
            "predicted_comment": prediction["predicted_comment"],
            "reason": prediction["reason"],
            "status": "Failed to update database"
        }, indent=2))

if __name__ == "__main__":
    main() 