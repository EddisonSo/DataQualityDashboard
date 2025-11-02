# Data Quality Dashboard

A fullstack application for analyzing data quality in CSV files. Built with FastAPI (Python) backend and React frontend, with SQLite persistence for analysis history.

## Project Structure

```
data-quality-dashboard/
├── backend/              # FastAPI backend
│   ├── main.py          # API endpoints
│   ├── data_analyzer.py # Data quality analysis logic
│   ├── database.py      # SQLite database operations
│   ├── requirements.txt # Python dependencies
│   ├── .env            # Environment variables (create from .env.example)
│   └── Dockerfile      # Docker configuration
├── frontend/            # React frontend
│   ├── src/            # Source code
│   ├── package.json    # Node dependencies
│   ├── .env            # Environment variables (create from .env.example)
│   ├── Dockerfile      # Docker configuration
│   └── nginx.conf      # Nginx configuration
├── docker-compose.yml  # Docker Compose orchestration
└── sample-data/        # Sample CSV files for testing
```

## Features

### Data Quality Analysis

- **Missing Values Detection**: Identifies columns with incomplete data and calculates percentages
- **Invalid Format Detection**: Validates email formats, dates, ages, and other field-specific patterns
- **Logical Inconsistency Detection**: Identifies business rule violations (e.g., selling price < cost price)
- **Duplicate Detection**: Finds duplicate records (excluding primary keys)
- **Statistical Analysis**: Provides summary statistics for all numeric columns
- **Column Profiling**: Detailed analysis of each column's data type, completeness, and uniqueness

### User Interface

- **File Upload**: Custom styled file browser with multi-file support
- **Data Preview**: Paginated, sortable preview of your data
- **Analysis History**: View, search, and manage past analyses
- **Duplicate Detection**: Smart duplicate file checking with hash-based comparison
- **API Key Management**: Secure API key input with localStorage persistence
- **Custom Modals**: Beautiful confirmation dialogs for delete and re-analyze actions
- **Responsive Design**: Clean, modern UI with sky blue theme

### Data Persistence

- **SQLite Database**: All analyses stored locally with full history
- **File Hash Tracking**: Prevents duplicate analysis of the same file
- **Timestamp Management**: Accurate timezone-aware timestamps
- **Analysis Metadata**: Track dataset name, record counts, and issue status

## Quick Start (Docker - Recommended)

### Prerequisites

- Docker and Docker Compose installed on your system
- [Get Docker](https://docs.docker.com/get-docker/)

### Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd data-quality-dashboard
```

2. **Configure environment variables**:

Create backend environment file:
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and set your API key:
```env
API_KEY=your-secure-api-key-here
```

Create frontend environment file:
```bash
cp frontend/.env.example frontend/.env
```

Edit `frontend/.env` and set the same API key:
```env
VITE_API_URL=http://localhost:8000
VITE_API_KEY=your-secure-api-key-here
```

3. **Start the application**:
```bash
docker-compose up -d
```

This will:
- Build the backend and frontend Docker images
- Start both services in detached mode
- Set up networking between services
- Persist the SQLite database across restarts

4. **Access the application**:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

### Docker Commands

**View logs**:
```bash
docker-compose logs -f
```

**Stop the application**:
```bash
docker-compose down
```

**Rebuild after code changes**:
```bash
docker-compose up -d --build
```

**Remove all data and start fresh**:
```bash
docker-compose down -v
rm backend/data_quality_analyses.db
docker-compose up -d
```

## Using the Application

1. Open your browser to `http://localhost:3000`
2. **Set your API key**: Click the "🔓 Set API Key" button in the header and enter your API key
3. Upload one or more CSV files using the custom file browser
4. Click "Analyze Data Quality" to process the files
5. Review the comprehensive analysis results
6. View analysis history in the "Analysis History" tab
7. Click "View Details" on any analysis to see the full report

### First-Time Setup

When you first use the application:
1. The API key you configured in the `.env` files is required for all file uploads
2. Click the API key button in the header to enter it
3. The key will be stored in your browser's localStorage for convenience
4. You can clear or change the API key at any time

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

All file upload endpoints require an API key in the `X-API-Key` header.

#### POST /check-files
Check if uploaded files have been analyzed before.

**Headers**: `X-API-Key: your-api-key`

**Request**: multipart/form-data with `files` field

**Response**:
```json
{
  "success": true,
  "file_checks": [...]
}
```

#### POST /analyze
Upload multiple CSV files for analysis.

**Headers**: `X-API-Key: your-api-key`

**Request**: multipart/form-data with `files` field

**Response**:
```json
{
  "success": true,
  "files_analyzed": 3,
  "results": [...]
}
```

#### GET /history
Get all analysis history.

**Response**:
```json
{
  "success": true,
  "count": 10,
  "analyses": [...]
}
```

#### GET /history/{analysis_id}
Get a specific analysis by ID.

#### DELETE /history/{analysis_id}
Delete a specific analysis.

#### GET /health
Health check endpoint.

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework with API key authentication
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **SQLite**: Lightweight database for analysis history
- **python-dotenv**: Environment variable management
- **Uvicorn**: ASGI server

### Frontend
- **React**: UI library with hooks
- **Vite**: Fast build tool and dev server
- **Axios**: HTTP client
- **CSS3**: Custom styling with gradients and animations

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Production web server for frontend

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

### Development Mode Configuration

Set `DEVELOPMENT = True` in `backend/database.py` to automatically reset the database on each backend restart (useful during development).

**Warning**: This deletes all data when the server restarts!

```python
# backend/database.py
DEVELOPMENT = True  # Set to False in production
```

## Alternative: Manual Setup (Without Docker)

If you prefer to run the services directly without Docker:

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and configure environment file:
```bash
cp .env.example .env
```

Edit `.env` and set your API key:
```env
API_KEY=your-secure-api-key-here
```

3. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Start the server:
```bash
uvicorn main:app --reload  # With auto-reload for development
# OR
python main.py  # Production mode
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Create and configure environment file:
```bash
cp .env.example .env
```

Edit `.env` and set your API key:
```env
VITE_API_URL=http://localhost:8000
VITE_API_KEY=your-secure-api-key-here
```

3. Install dependencies:
```bash
npm install
```

4. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Building for Production

Frontend:
```bash
cd frontend
npm run build
```

The built files will be in the `dist` directory, ready to be served by any static file server.

## Security

### API Key Authentication

All file upload endpoints are protected with API key authentication:

1. **Set a secure API key**: Use a strong, randomly generated key for production
2. **Environment variables**: Never commit `.env` files to version control
3. **Key rotation**: Change your API key periodically
4. **Browser storage**: The frontend stores the API key in localStorage for convenience

### Generating a Secure API Key

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -base64 32
```

### Security Best Practices

- Keep your `.env` files private (already in `.gitignore`)
- Use HTTPS in production
- Regularly update dependencies
- Review and limit file upload sizes
- Monitor analysis history for unusual activity

## Troubleshooting

### Docker Issues

**Port already in use**:
```bash
# Check what's using the port
lsof -i :8000
lsof -i :3000

# Kill the process or change ports in docker-compose.yml
```

**Database locked**:
```bash
# Stop containers and remove the database
docker-compose down
rm backend/data_quality_analyses.db
docker-compose up -d
```

**Changes not reflected**:
```bash
# Rebuild the images
docker-compose up -d --build
```

### API Key Issues

**401 Unauthorized Error**:
- Ensure the API key in `backend/.env` matches the one you're using
- Check that the API key is entered correctly in the frontend
- Clear browser localStorage and re-enter the key

**API key not persisting**:
- Check browser console for localStorage errors
- Ensure cookies/localStorage are enabled in your browser

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions, please create an issue in the repository.
