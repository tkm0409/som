# Order Prediction API

A FastAPI-based backend for the AI Data Review application. This API provides endpoints for connecting to SQL Server databases, retrieving order data, and generating AI predictions for order comments.

## Setup

1. Create and activate a virtual environment:

```bash
# Create the virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/macOS
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configuration:

   - Copy `.env.example` to `.env` and update with your Google API key
   - Copy `dataaccessconfig.xml.example` to `dataaccessconfig.xml` and update with your database connection details

## Running the API

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once running, you can access the Swagger UI documentation at:

http://localhost:8000/docs

## Endpoints

- `GET /companies` - List available companies from configuration
- `GET /status/{company_name}` - Check server status for a company
- `GET /databases/{company_name}` - List databases for a company
- `POST /data` - Load order data from a database
- `POST /predict` - Generate AI prediction for an order
- `POST /test-connection` - Test database connection 