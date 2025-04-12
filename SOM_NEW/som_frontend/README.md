# AI Data Review Frontend

A modern React-based frontend for the AI Data Review application. This frontend provides a clean, responsive interface for connecting to SQL Server databases, viewing order data, and generating AI predictions for order comments.

## Technologies Used

- React 18 with TypeScript
- Material-UI for UI components
- Axios for API requests

## Setup

1. Install dependencies:

```bash
npm install
```

2. Configure the API endpoint:

Create a `.env` file in the project root with:

```
REACT_APP_API_URL=http://localhost:8000
```

## Development

Start the development server:

```bash
npm start
```

This will run the app in development mode, available at http://localhost:3000.

## Building for Production

Create a production build:

```bash
npm run build
```

The build files will be located in the `build` directory and can be served by any static file server.

## Features

- Server and database selection
- Data loading and visualization
- Order search and filtering
- AI-powered comment prediction

## API Connection

The frontend connects to the FastAPI backend for:
- Retrieving company configurations
- Loading order data
- Generating predictions

Make sure the backend API is running and accessible at the URL specified in your `.env` file. 