import re
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

def load_data():
    """Load and prepare data from Excel file"""
    try:
        df = pd.read_excel('DB Data.xlsx', sheet_name=1)
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

def main():
    # Check for API key
    if not GOOGLE_API_KEY:
        print(json.dumps({
            "predicted_comment": "Error: No API key found",
            "reason": "Please set your GOOGLE_API_KEY in the .env file"
        }))
        return
    
    # Load data
    df = load_data()
    if df is None:
        print(json.dumps({
            "predicted_comment": "Error: Could not load data",
            "reason": "Failed to read Excel file"
        }))
        return
    
    # Get prediction
    prompt = prepare_prompt(df)
    prediction = get_prediction(prompt)
    
    # Print JSON output
    print(json.dumps(prediction, indent=2))

if __name__ == "__main__":
    main() 