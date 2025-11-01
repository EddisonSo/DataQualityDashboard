# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

## Option 1: Using Startup Scripts (Recommended)

### Step 1: Start the Backend

Open a terminal and run:
```bash
./start-backend.sh
```

This will:
- Create a virtual environment
- Install Python dependencies
- Start the FastAPI server on http://localhost:8000

### Step 2: Start the Frontend

Open a **new terminal** and run:
```bash
./start-frontend.sh
```

This will:
- Install Node dependencies
- Start the React dev server on http://localhost:3000

### Step 3: Use the Application

1. Open your browser to http://localhost:3000
2. Upload the sample CSV files from `sample-data/`
3. Click "Analyze Data Quality"
4. View the comprehensive analysis results

## Option 2: Manual Setup

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Testing with Sample Data

The `sample-data/` directory contains three CSV files with intentional data quality issues:

1. **customers.csv** (505 records)
   - Missing email addresses (4%)
   - Invalid email formats (2%)
   - Missing phone numbers (7%)
   - Future registration dates (3%)
   - Invalid ages and status values
   - 5 duplicate customer records

2. **inventory.csv** (15 products)
   - Missing supplier information (12.5%)
   - Selling prices below cost prices (20%)
   - Stock below reorder levels (25%)
   - Future restock dates (10%)
   - Missing warehouse locations and quality ratings

3. **transactions.csv** (2,000 transactions)
   - Pricing errors (1%)
   - Negative total amounts (0.7%)
   - Missing payment methods (1.25%)
   - Invalid payment methods (0.8%)
   - Missing transaction status (1.7%)

## Expected Results

The dashboard will identify and report:

- ✓ All missing values with percentages
- ✓ Invalid email formats
- ✓ Invalid date ranges (future dates)
- ✓ Invalid age values
- ✓ Duplicate customer records
- ✓ Selling prices below cost prices
- ✓ Stock levels below reorder thresholds
- ✓ Negative transaction amounts
- ✓ Invalid payment methods and status values
- ✓ Comprehensive statistics for all numeric columns

## API Documentation

Once the backend is running, you can explore the API:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Find and kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

**Virtual environment issues:**
```bash
# Remove and recreate the virtual environment
rm -rf backend/venv
cd backend
python3 -m venv venv
```

### Frontend Issues

**Port 3000 already in use:**
- The Vite server will automatically try the next available port (3001, 3002, etc.)

**Dependency issues:**
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### CORS Issues

If you see CORS errors in the browser console:
1. Ensure the backend is running on port 8000
2. Ensure the frontend is running on port 3000
3. Check that both servers are accessible

## Next Steps

- Explore the different data quality checks in the code
- Customize the validation rules in `backend/data_analyzer.py`
- Add new visualizations in `frontend/src/components/`
- Integrate with your own CSV files
- Deploy to production (see main README.md)

## Features Demonstrated

✓ **File Upload**: Multi-file upload support
✓ **Data Profiling**: Automatic column type detection and statistics
✓ **Missing Value Analysis**: Comprehensive missing data reporting
✓ **Format Validation**: Email, date, and numeric range validation
✓ **Business Rules**: Logical consistency checks
✓ **Duplicate Detection**: Identifying duplicate records
✓ **Statistical Analysis**: Summary statistics for numeric columns
✓ **Interactive Dashboard**: User-friendly results presentation
✓ **Error Handling**: Robust error handling and user feedback
✓ **API Documentation**: Auto-generated API docs with FastAPI

Enjoy exploring the Data Quality Dashboard!
