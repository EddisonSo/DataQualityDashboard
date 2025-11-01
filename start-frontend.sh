#!/bin/bash

echo "Starting Data Quality Dashboard Frontend..."

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the development server
echo "Starting React development server on http://localhost:3000"
npm run dev
