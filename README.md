# Data Quality Dashboard

A fullstack application for analyzing data quality in CSV files. Built with FastAPI (Python) backend and React frontend.

## Project Structure

```
data-quality-dashboard/
├── backend/              # FastAPI backend
│   ├── main.py          # API endpoints
│   ├── data_analyzer.py # Data quality analysis logic
│   └── requirements.txt # Python dependencies
├── frontend/            # React frontend
│   ├── src/            # Source code
│   └── package.json    # Node dependencies
└── sample-data/        # Sample CSV files for testing
```

## Features

### Data Quality Analysis

- **Missing Values Detection**: Identifies columns with incomplete data and calculates percentages
- **Invalid Format Detection**: Validates email formats, dates, ages, and other field-specific patterns
- **Logical Inconsistency Detection**: Identifies business rule violations (e.g., selling price < cost price)
- **Duplicate Detection**: Finds duplicate records with different IDs
- **Outlier Detection**: Identifies unusual values in numeric columns
- **Statistical Analysis**: Provides summary statistics for all numeric columns
- **Column Profiling**: Detailed analysis of each column's data type, completeness, and uniqueness

### User Interface

- Drag-and-drop file upload
- Support for multiple CSV files
- Real-time progress indicators
- Interactive dashboard with visualizations
- Detailed issue reporting with severity levels
- Business-friendly language and recommendations

## Quick Start

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Using the Application

1. Start both the backend and frontend servers
2. Open your browser to `http://localhost:3000`
3. Upload one or more CSV files using the file input
4. Click "Analyze Data Quality" to process the files
5. Review the comprehensive analysis results

## Sample Data

The `sample-data` directory contains example CSV files with intentional data quality issues:

- `customers.csv` - Customer data with missing values, invalid emails, and duplicates
- `inventory.csv` - Product inventory with logical inconsistencies
- `transactions.csv` - Transaction records with invalid values and pricing errors

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### API Endpoints

#### POST /analyze
Upload multiple CSV files for analysis.

**Request**: multipart/form-data with `files` field

**Response**:
```json
{
  "success": true,
  "files_analyzed": 3,
  "results": [...]
}
```

#### POST /analyze-single
Upload a single CSV file for analysis.

#### GET /health
Health check endpoint.

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Uvicorn**: ASGI server

### Frontend
- **React**: UI library
- **Vite**: Build tool
- **Axios**: HTTP client
- **Recharts**: Charting library (optional)

## Data Quality Checks

### Missing Values
- Calculates percentage of missing values per column
- Identifies columns with high missing rates

### Invalid Values
- Email format validation
- Date range validation (no future dates for historical events)
- Numeric range validation (realistic ages, positive prices)
- Status and payment method validation

### Duplicates
- Identifies records with identical data but different IDs
- Configurable columns for duplicate detection

### Logical Inconsistencies
- Selling price >= cost price
- Stock levels vs reorder thresholds
- Custom business rules

### Statistical Analysis
- Mean, median, min, max, standard deviation
- Distribution analysis
- Outlier detection

## Development

### Running in Development Mode

Backend with auto-reload:
```bash
cd backend
uvicorn main:app --reload
```

Frontend with hot module replacement:
```bash
cd frontend
npm run dev
```

### Building for Production

Backend:
- The FastAPI application is production-ready
- Deploy with Gunicorn or uvicorn

Frontend:
```bash
cd frontend
npm run build
```

## License

MIT License

## Support

For issues or questions, please create an issue in the repository.
