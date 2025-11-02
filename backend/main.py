from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import io
import hashlib
from typing import List, Optional
from data_analyzer import DataQualityAnalyzer
from database import AnalysisDatabase

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

# Initialize database
db = AnalysisDatabase()


def compute_file_hash(content: bytes) -> str:
    """Compute SHA-256 hash of file content."""
    return hashlib.sha256(content).hexdigest()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Data Quality Dashboard API",
        "version": "1.0.0",
        "endpoints": {
            "/check-files": "POST - Check if files have been analyzed before",
            "/analyze": "POST - Analyze CSV files",
            "/history": "GET - Get all analysis history",
            "/history/{analysis_id}": "GET - Get specific analysis by ID",
            "/history/dataset/{dataset_name}": "GET - Get analyses for a dataset",
            "/stats": "GET - Get summary statistics",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/check-files")
async def check_files(files: List[UploadFile] = File(...)):
    """
    Check if uploaded files have been analyzed before.
    Returns information about previous analyses if found.
    """
    try:
        file_checks = []

        for file in files:
            # Validate file type
            if not file.filename.endswith('.csv'):
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} is not a CSV file"
                )

            # Read and hash file
            contents = await file.read()
            file_hash = compute_file_hash(contents)

            # Check if this file has been analyzed before
            previous_analysis = db.get_analysis_by_hash(file_hash)

            file_checks.append({
                "filename": file.filename,
                "file_hash": file_hash,
                "previously_analyzed": previous_analysis is not None,
                "previous_analysis": {
                    "analysis_id": previous_analysis['analysis_id'],
                    "analysis_timestamp": previous_analysis['analysis_timestamp'],
                    "total_records": previous_analysis['total_records'],
                    "total_columns": previous_analysis['total_columns'],
                    "has_issues": previous_analysis['has_issues']
                } if previous_analysis else None
            })

        return JSONResponse(content={
            "success": True,
            "file_checks": file_checks
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking files: {str(e)}")


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
            file_hash = compute_file_hash(contents)
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

            # Analyze the data
            analyzer = DataQualityAnalyzer(df, file.filename)
            analysis = analyzer.analyze()

            # Save analysis to database
            analysis_id = db.save_analysis(file.filename, file_hash, analysis)
            analysis['analysis_id'] = analysis_id
            analysis['file_hash'] = file_hash

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
        file_hash = compute_file_hash(contents)
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

        # Analyze the data
        analyzer = DataQualityAnalyzer(df, file.filename)
        analysis = analyzer.analyze()

        # Save analysis to database
        analysis_id = db.save_analysis(file.filename, file_hash, analysis)
        analysis['analysis_id'] = analysis_id
        analysis['file_hash'] = file_hash

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


@app.get("/history")
async def get_analysis_history(limit: Optional[int] = None):
    """
    Get all analysis history, ordered by most recent first.

    Args:
        limit: Optional limit on number of results to return
    """
    try:
        analyses = db.get_all_analyses(limit=limit)
        return JSONResponse(content={
            "success": True,
            "count": len(analyses),
            "analyses": analyses
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")


@app.get("/history/{analysis_id}")
async def get_analysis_by_id(analysis_id: str):
    """
    Get a specific analysis by its ID.

    Args:
        analysis_id: The ID of the analysis to retrieve
    """
    try:
        analysis = db.get_analysis_by_id(analysis_id)
        if analysis is None:
            raise HTTPException(status_code=404, detail=f"Analysis with ID {analysis_id} not found")

        return JSONResponse(content={
            "success": True,
            "analysis": analysis
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis: {str(e)}")


@app.get("/history/dataset/{dataset_name}")
async def get_analyses_by_dataset(dataset_name: str):
    """
    Get all analyses for a specific dataset.

    Args:
        dataset_name: Name of the dataset to filter by
    """
    try:
        analyses = db.get_analyses_by_dataset(dataset_name)
        return JSONResponse(content={
            "success": True,
            "dataset_name": dataset_name,
            "count": len(analyses),
            "analyses": analyses
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analyses: {str(e)}")


@app.delete("/history/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """
    Delete a specific analysis.

    Args:
        analysis_id: The ID of the analysis to delete
    """
    try:
        deleted = db.delete_analysis(analysis_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Analysis with ID {analysis_id} not found")

        return JSONResponse(content={
            "success": True,
            "message": f"Analysis {analysis_id} deleted successfully"
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting analysis: {str(e)}")


@app.get("/stats")
async def get_summary_stats():
    """
    Get summary statistics about all analyses in the database.
    """
    try:
        stats = db.get_summary_stats()
        return JSONResponse(content={
            "success": True,
            "stats": stats
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
