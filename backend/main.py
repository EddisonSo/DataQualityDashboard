from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import io
from typing import List
from data_analyzer import DataQualityAnalyzer

app = FastAPI(
    title="Data Quality Dashboard API",
    description="API for analyzing data quality in CSV files",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Data Quality Dashboard API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "POST - Analyze CSV files",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/analyze")
async def analyze_csv(files: List[UploadFile] = File(...)):
    """
    Analyze one or more CSV files for data quality issues.

    Returns comprehensive analysis including:
    - Missing values
    - Invalid values
    - Duplicates
    - Logical inconsistencies
    - Statistical summaries
    """
    try:
        results = []

        for file in files:
            # Validate file type
            if not file.filename.endswith('.csv'):
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} is not a CSV file"
                )

            # Read CSV file
            contents = await file.read()
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

            # Analyze the data
            analyzer = DataQualityAnalyzer(df, file.filename)
            analysis = analyzer.analyze()

            results.append(analysis)

        return JSONResponse(content={
            "success": True,
            "files_analyzed": len(files),
            "results": results
        })

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="One or more CSV files are empty")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Error parsing CSV file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")


@app.post("/analyze-single")
async def analyze_single_csv(file: UploadFile = File(...)):
    """
    Analyze a single CSV file for data quality issues.
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} is not a CSV file"
            )

        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

        # Analyze the data
        analyzer = DataQualityAnalyzer(df, file.filename)
        analysis = analyzer.analyze()

        return JSONResponse(content={
            "success": True,
            "result": analysis
        })

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Error parsing CSV file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
