# AI Data Review Application

A modern application for reviewing order data with AI-powered comment prediction. This project consists of a FastAPI backend and React frontend, replacing the original Streamlit interface with a more modern and responsive UI.

## Project Structure

- `som_backend/`: FastAPI backend
- `som_frontend/`: React TypeScript frontend

## Backend Setup

The backend is built with FastAPI and provides APIs for accessing SQL Server databases and generating predictions using Google's Gemini AI.

1. Navigate to the backend directory:
   ```bash
   cd som_backend
   ```

2. Create and activate a virtual environment:
   ```bash
   # Create the virtual environment
   python -m venv venv

   # Activate on Windows
   venv\Scripts\activate

   # Activate on Linux/macOS
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the environment:
   - Copy `.env.example` to `.env` and update with your Google API key
   - Copy `dataaccessconfig.xml.example` to `dataaccessconfig.xml` and update with your database connection details

5. Start the backend:
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at http://localhost:8000 with documentation at http://localhost:8000/docs

## Frontend Setup

The frontend is built with React and TypeScript, using Material-UI for components.

1. Navigate to the frontend directory:
   ```bash
   cd som_frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure the API endpoint:
   Create a `.env` file with:
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```

4. Start the development server:
   ```bash
   npm start
   ```

The frontend will be available at http://localhost:3000

## Features

- Server and database selection
- Data loading and visualization
- Order search and filtering
- AI-powered comment prediction

## Requirements

- Python 3.8+
- Node.js 14+
- SQL Server with appropriate database access
- Google API key for Gemini 