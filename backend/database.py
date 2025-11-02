import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import os


class AnalysisDatabase:
    """Handles SQLite database operations for storing data quality analysis history."""

    def __init__(self, db_path: str = "data_quality_analyses.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Create the analyses table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                analysis_id TEXT PRIMARY KEY,
                dataset_name TEXT NOT NULL,
                analysis_timestamp TEXT NOT NULL,
                analysis_results TEXT NOT NULL,
                total_records INTEGER,
                total_columns INTEGER,
                has_issues INTEGER DEFAULT 1
            )
        ''')

        conn.commit()
        conn.close()

    def save_analysis(self, dataset_name: str, analysis_results: Dict) -> str:
        """
        Save an analysis to the database.

        Args:
            dataset_name: Name of the dataset/file analyzed
            analysis_results: Complete analysis results dictionary

        Returns:
            The UUID of the saved analysis
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        analysis_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        results_json = json.dumps(analysis_results)
        total_records = analysis_results.get('total_records', 0)
        total_columns = analysis_results.get('total_columns', 0)

        # Determine if dataset has any issues
        has_issues = 1  # Default to True
        try:
            # Handle missing values - could be dict of counts or other structure
            missing_values = analysis_results.get('missing_values', {})
            if isinstance(missing_values, dict):
                missing_count = sum(v if isinstance(v, (int, float)) else 0 for v in missing_values.values())
            else:
                missing_count = 0

            # Handle invalid values - dict of lists
            invalid_values = analysis_results.get('invalid_values', {})
            if isinstance(invalid_values, dict):
                invalid_count = sum(len(v) if isinstance(v, list) else 0 for v in invalid_values.values())
            else:
                invalid_count = 0

            # Handle duplicates
            duplicates = analysis_results.get('duplicates', {})
            duplicate_groups = duplicates.get('duplicate_groups', []) if isinstance(duplicates, dict) else []
            duplicate_count = len(duplicate_groups) if isinstance(duplicate_groups, list) else 0

            # Handle logical issues
            logical_issues = analysis_results.get('logical_issues', {})
            issues = logical_issues.get('issues', []) if isinstance(logical_issues, dict) else []
            logical_count = len(issues) if isinstance(issues, list) else 0

            if missing_count == 0 and invalid_count == 0 and duplicate_count == 0 and logical_count == 0:
                has_issues = 0
        except Exception:
            # If any error occurs, default to has_issues = 1
            has_issues = 1

        cursor.execute('''
            INSERT INTO analyses
            (analysis_id, dataset_name, analysis_timestamp, analysis_results, total_records, total_columns, has_issues)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (analysis_id, dataset_name, timestamp, results_json, total_records, total_columns, has_issues))

        conn.commit()
        conn.close()

        return analysis_id

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
            SELECT analysis_id, dataset_name, analysis_timestamp,
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
                'analysis_timestamp': row[2],
                'analysis_results': json.loads(row[3]),
                'total_records': row[4],
                'total_columns': row[5],
                'has_issues': bool(row[6])
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
            SELECT analysis_id, dataset_name, analysis_timestamp,
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
                'analysis_timestamp': row[2],
                'analysis_results': json.loads(row[3]),
                'total_records': row[4],
                'total_columns': row[5],
                'has_issues': bool(row[6])
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
            SELECT analysis_id, dataset_name, analysis_timestamp,
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
                'analysis_timestamp': row[2],
                'analysis_results': json.loads(row[3]),
                'total_records': row[4],
                'total_columns': row[5],
                'has_issues': bool(row[6])
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
