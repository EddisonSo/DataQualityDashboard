"""
Database module for storing and retrieving data quality analysis history.

DEVELOPMENT MODE:
    Set DEVELOPMENT = True to automatically drop and recreate all database tables
    every time the backend server restarts. This is useful during development to
    ensure a clean database state.

    WARNING: All data will be lost on each restart when DEVELOPMENT = True!
    Always set to False in production.
"""

import sqlite3
import json
import uuid
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
import os

# ============================================================================
# DEVELOPMENT MODE - Set to True to reset database on every backend restart
# WARNING: This will DELETE ALL DATA when the server starts!
# ============================================================================
DEVELOPMENT = True


class AnalysisDatabase:
    """Handles SQLite database operations for storing data quality analysis history."""

    def __init__(self, db_path: str = "data_quality_analyses.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Create the analyses table if it doesn't exist. In development mode, drops all tables first."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if DEVELOPMENT:
            print("=" * 60)
            print("🔧 DEVELOPMENT MODE: Resetting all database tables...")
            print("=" * 60)

            # Drop all tables
            cursor.execute("DROP TABLE IF EXISTS analyses")
            print("✓ Dropped 'analyses' table")

            conn.commit()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                analysis_id TEXT PRIMARY KEY,
                dataset_name TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                analysis_timestamp TEXT NOT NULL,
                analysis_results TEXT NOT NULL,
                total_records INTEGER,
                total_columns INTEGER,
                has_issues INTEGER DEFAULT 1
            )
        ''')

        # Create index on file_hash for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_file_hash ON analyses(file_hash)
        ''')

        if DEVELOPMENT:
            print("✓ Created 'analyses' table")
            print("✓ Created index on 'file_hash'")
            print("=" * 60)
            print("✅ Database reset complete!")
            print("=" * 60)

        conn.commit()
        conn.close()

    def save_analysis(self, dataset_name: str, file_hash: str, analysis_results: Dict) -> str:
        """
        Save an analysis to the database.

        Args:
            dataset_name: Name of the dataset/file analyzed
            file_hash: SHA-256 hash of the file content
            analysis_results: Complete analysis results dictionary

        Returns:
            The UUID of the saved analysis
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        analysis_id = str(uuid.uuid4())
        # Use UTC timestamp with timezone info for correct timezone handling
        timestamp = datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
        results_json = json.dumps(analysis_results)
        total_records = analysis_results.get('total_records', 0)
        total_columns = analysis_results.get('total_columns', 0)

        # Determine if dataset has any issues
        has_issues = 1  # Default to True
        try:
            # Handle missing values
            missing_values = analysis_results.get('missing_values', {})
            missing_count = missing_values.get('total_missing_values', 0) if isinstance(missing_values, dict) else 0

            # Handle invalid values
            invalid_values = analysis_results.get('invalid_values', {})
            invalid_count = invalid_values.get('total_invalid_count', 0) if isinstance(invalid_values, dict) else 0

            # Handle duplicates
            duplicates = analysis_results.get('duplicates', {})
            duplicate_count = duplicates.get('total_duplicates', 0) if isinstance(duplicates, dict) else 0

            # Handle logical issues
            logical_issues = analysis_results.get('logical_issues', {})
            logical_count = logical_issues.get('total_issues', 0) if isinstance(logical_issues, dict) else 0

            if missing_count == 0 and invalid_count == 0 and duplicate_count == 0 and logical_count == 0:
                has_issues = 0
        except Exception:
            # If any error occurs, default to has_issues = 1
            has_issues = 1

        cursor.execute('''
            INSERT INTO analyses
            (analysis_id, dataset_name, file_hash, analysis_timestamp, analysis_results, total_records, total_columns, has_issues)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (analysis_id, dataset_name, file_hash, timestamp, results_json, total_records, total_columns, has_issues))

        conn.commit()
        conn.close()

        return analysis_id

    def get_analysis_by_hash(self, file_hash: str) -> Optional[Dict]:
        """
        Check if a file with this hash has been analyzed before.

        Args:
            file_hash: SHA-256 hash of the file content

        Returns:
            The most recent analysis for this file hash, or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT analysis_id, dataset_name, file_hash, analysis_timestamp,
                   analysis_results, total_records, total_columns, has_issues
            FROM analyses
            WHERE file_hash = ?
            ORDER BY analysis_timestamp DESC
            LIMIT 1
        ''', (file_hash,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'analysis_id': row[0],
                'dataset_name': row[1],
                'file_hash': row[2],
                'analysis_timestamp': row[3],
                'analysis_results': json.loads(row[4]),
                'total_records': row[5],
                'total_columns': row[6],
                'has_issues': bool(row[7])
            }

        return None

    def get_all_analyses(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Retrieve all analyses from the database, ordered by most recent first.

        Args:
            limit: Maximum number of analyses to return (None for all)

        Returns:
            List of analysis records with metadata
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = '''
            SELECT analysis_id, dataset_name, file_hash, analysis_timestamp,
                   analysis_results, total_records, total_columns, has_issues
            FROM analyses
            ORDER BY analysis_timestamp DESC
        '''

        if limit:
            query += f' LIMIT {limit}'

        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        analyses = []
        for row in rows:
            analyses.append({
                'analysis_id': row[0],
                'dataset_name': row[1],
                'file_hash': row[2],
                'analysis_timestamp': row[3],
                'analysis_results': json.loads(row[4]),
                'total_records': row[5],
                'total_columns': row[6],
                'has_issues': bool(row[7])
            })

        return analyses

    def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict]:
        """
        Retrieve a specific analysis by ID.

        Args:
            analysis_id: The ID of the analysis to retrieve

        Returns:
            Analysis record or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT analysis_id, dataset_name, file_hash, analysis_timestamp,
                   analysis_results, total_records, total_columns, has_issues
            FROM analyses
            WHERE analysis_id = ?
        ''', (analysis_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'analysis_id': row[0],
                'dataset_name': row[1],
                'file_hash': row[2],
                'analysis_timestamp': row[3],
                'analysis_results': json.loads(row[4]),
                'total_records': row[5],
                'total_columns': row[6],
                'has_issues': bool(row[7])
            }

        return None

    def get_analyses_by_dataset(self, dataset_name: str) -> List[Dict]:
        """
        Retrieve all analyses for a specific dataset.

        Args:
            dataset_name: Name of the dataset to filter by

        Returns:
            List of analysis records for the dataset
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT analysis_id, dataset_name, file_hash, analysis_timestamp,
                   analysis_results, total_records, total_columns, has_issues
            FROM analyses
            WHERE dataset_name = ?
            ORDER BY analysis_timestamp DESC
        ''', (dataset_name,))

        rows = cursor.fetchall()
        conn.close()

        analyses = []
        for row in rows:
            analyses.append({
                'analysis_id': row[0],
                'dataset_name': row[1],
                'file_hash': row[2],
                'analysis_timestamp': row[3],
                'analysis_results': json.loads(row[4]),
                'total_records': row[5],
                'total_columns': row[6],
                'has_issues': bool(row[7])
            })

        return analyses

    def delete_analysis(self, analysis_id: str) -> bool:
        """
        Delete a specific analysis.

        Args:
            analysis_id: The ID of the analysis to delete

        Returns:
            True if deleted, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM analyses WHERE analysis_id = ?', (analysis_id,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return deleted

    def get_summary_stats(self) -> Dict:
        """
        Get summary statistics about all analyses.

        Returns:
            Dictionary with summary stats
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                COUNT(*) as total_analyses,
                COUNT(DISTINCT dataset_name) as unique_datasets,
                SUM(has_issues) as analyses_with_issues,
                MIN(analysis_timestamp) as first_analysis,
                MAX(analysis_timestamp) as last_analysis
            FROM analyses
        ''')

        row = cursor.fetchone()
        conn.close()

        return {
            'total_analyses': row[0],
            'unique_datasets': row[1],
            'analyses_with_issues': row[2],
            'first_analysis': row[3],
            'last_analysis': row[4]
        }
