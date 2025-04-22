# SOM - Supply Order Management AI System

An intelligent system for analyzing and predicting order journal comments based on historical order trend data using Google's Gemini AI.

## Overview

This application provides an intuitive interface for supply chain management that:

1. Connects to SQL Server databases to retrieve order data
2. Analyzes historical trend patterns in orders
3. Uses Google Gemini AI to predict journal comments for orders based on similar patterns
4. Presents data in an interactive UI built with Streamlit
5. Allows users to query databases using natural language

## Features

- **Database Connectivity**: Connect to multiple SQL Server databases
- **Data Visualization**: View and explore order data with interactive tables and charts
- **AI-Powered Predictions**: Generate intelligent journal comment predictions based on similar historical orders
- **Natural Language to SQL**: Convert natural language questions to SQL queries and execute them
- **SQL Query Editing**: Review and edit AI-generated SQL queries before execution
- **Company Configuration**: Support for multiple company databases

## Requirements

- Python 3.8+
- SQL Server database with order data
- Google Gemini API key

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd SOM
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv som-env
   # On Windows
   som-env\Scripts\activate
   # On macOS/Linux
   source som-env/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up configuration:
   - Copy `.env.example` to `.env` and add your Google Gemini API key and database credentials
   - Copy `dataaccessconfig.xml.example` to `dataaccessconfig.xml` and configure your database connections

## Usage

Start the application:
```
streamlit run app.py
```

The application will be available at `http://localhost:8501`.

### Using the Order Prediction Feature

1. Select "Order Prediction" mode from the sidebar
2. Choose a server and database from the dropdown menus
3. Click "Load Data" to retrieve order information
4. Use the search box to find specific orders or browse the recent orders list
5. Select an order to analyze and click "Generate AI Comment Prediction"
6. View the AI-generated comment prediction and reasoning

### Using the Natural Language to SQL Feature

1. Select "NL to SQL" mode from the sidebar
2. Choose a server and database from the dropdown menus
3. Click "Connect to Database" to establish connection and fetch schema information
4. Enter your question in natural language (e.g., "Show me the top 10 orders by order strength")
5. Click "Generate SQL Query" to convert your question to SQL
6. Review the generated SQL query and explanation
7. Optionally edit the SQL query if needed
8. Click "Execute Query" to run the query against the database
9. View the results and download as CSV if desired

## Core Components

- `app.py`: Main Streamlit application with UI
- `order_prediction_sql.py`: Core logic for database connection and AI predictions
- `nl_to_sql.py`: Natural language to SQL conversion and execution

## Configuration

### Environment Variables
Required variables in `.env` file:
- `GOOGLE_API_KEY`: Your Google Gemini API key
- `SQL_SERVER`, `SQL_DATABASE`, `SQL_USERNAME`, `SQL_PASSWORD`: SQL Server connection details

### Database Configuration
Alternative to environment variables is using the `dataaccessconfig.xml` file for multiple database connections.
