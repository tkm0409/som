# Order Prediction System

This system analyzes trend data and uses Google's Gemini AI to predict future order journal comments based on historical patterns. The system supports both Excel and SQL Server data sources.

## Project Structure

The project consists of three main Python scripts:

1. `order_prediction.py`: The base script that reads data from an Excel file and generates predictions
2. `order_prediction_sql.py`: A SQL Server version that reads data from a database and updates predictions
3. `order_prediction_api.py`: A FastAPI-based REST API that provides endpoints for prediction generation

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables:
   - Copy `.env.example` to `.env`
   - Add your Google Gemini API key to the `.env` file
   - For SQL Server usage, add your database credentials:
     - SQL_SERVER
     - SQL_DATABASE
     - SQL_USERNAME
     - SQL_PASSWORD
     - SQL_TABLE (optional, defaults to 'OrderTrends')

3. For Excel-based predictions:
   - Ensure your Excel file `DB Data.xlsx` is in the same directory as the script
   - The script expects data in sheet 2

## Usage

### Excel-based Predictions
```bash
python order_prediction.py
```

### SQL Server-based Predictions
```bash
python order_prediction_sql.py
```

### API Server
```bash
python order_prediction_api.py
```

The API server provides the following endpoints:
- `GET /servers`: List all available database servers
- `GET /servers/{server_id}/databases`: List databases for a specific server
- `POST /predict`: Generate predictions for specified server/database/table

## Output

The system provides:
- Trend visualization (saved as `trend_analysis.png`)
- Statistical analysis
- Future order journal comment predictions
- Trend direction predictions
- Seasonal pattern analysis
- Prediction results (saved as `prediction_results_[timestamp].txt`)

## File Descriptions

### order_prediction.py
- Reads data from Excel file
- Analyzes trends and patterns
- Generates predictions using Gemini AI
- Saves results to files

### order_prediction_sql.py
- Connects to SQL Server database
- Reads historical order data
- Generates predictions using Gemini AI
- Updates the database with new predictions
- Includes error handling and logging

### order_prediction_api.py
- Provides REST API endpoints for prediction generation
- Supports multiple database servers and tables
- Handles database connections and configurations
- Includes input validation and error handling
- Updates database with predictions automatically

## Requirements

- Python 3.7+
- Pandas
- Google Generative AI
- Matplotlib
- Seaborn
- Python-dotenv
- OpenPyXL
- FastAPI (for API version)
- PyODBC (for SQL Server version)
- Uvicorn (for API server) 