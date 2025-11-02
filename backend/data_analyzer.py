import pandas as pd
import numpy as np
from datetime import datetime
import re
from typing import Dict, List, Any


class DataQualityAnalyzer:
    """Analyzes data quality issues in CSV datasets."""

    def __init__(self, df: pd.DataFrame, dataset_name: str):
        self.df = df
        self.dataset_name = dataset_name
        self.total_records = len(df)

    def _clean_for_json(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert DataFrame to list of dicts with JSON-compliant values."""
        # Replace NaN, Infinity, and -Infinity with None
        df_clean = df.replace([np.inf, -np.inf], np.nan)
        # Convert to dict and replace NaN with None
        records = df_clean.to_dict('records')
        # Replace any remaining NaN values with None
        for record in records:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
        return records

    def _safe_percentage(self, count: int, total: int) -> float:
        """Safely calculate percentage, avoiding division by zero."""
        if total == 0:
            return 0.0
        return round((count / total) * 100, 2)

    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive data quality analysis."""
        return {
            "dataset_name": self.dataset_name,
            "total_records": self.total_records,
            "total_columns": len(self.df.columns),
            "data_preview": self.get_data_preview(),
            "missing_values": self.analyze_missing_values(),
            "invalid_values": self.analyze_invalid_values(),
            "duplicates": self.analyze_duplicates(),
            "logical_issues": self.analyze_logical_issues(),
            "statistics": self.generate_statistics(),
            "column_details": self.analyze_columns()
        }

    def get_data_preview(self) -> Dict[str, Any]:
        """Get a preview of the raw data for display."""
        return {
            "columns": self.df.columns.tolist(),
            "data": self._clean_for_json(self.df),
            "total_rows": len(self.df)
        }

    def analyze_missing_values(self) -> Dict[str, Any]:
        """Analyze missing values across all columns."""
        missing_data = []

        for column in self.df.columns:
            missing_count = self.df[column].isna().sum()
            if missing_count > 0:
                missing_data.append({
                    "column": column,
                    "missing_count": int(missing_count),
                    "missing_percentage": self._safe_percentage(missing_count, self.total_records)
                })

        total_missing = self.df.isna().sum().sum()
        total_cells = self.total_records * len(self.df.columns)

        return {
            "columns_with_missing": missing_data,
            "total_missing_values": int(total_missing),
            "overall_missing_percentage": self._safe_percentage(total_missing, total_cells)
        }

    def analyze_invalid_values(self) -> Dict[str, Any]:
        """Detect invalid values based on dataset type."""
        invalid_data = []

        # Email validation
        if 'email' in self.df.columns:
            invalid_emails = self._validate_emails()
            if invalid_emails['count'] > 0:
                invalid_data.append(invalid_emails)

        # Age validation
        if 'age' in self.df.columns:
            invalid_ages = self._validate_ages()
            if invalid_ages['count'] > 0:
                invalid_data.append(invalid_ages)

        # Date validation
        for col in self.df.columns:
            if 'date' in col.lower():
                invalid_dates = self._validate_dates(col)
                if invalid_dates['count'] > 0:
                    invalid_data.append(invalid_dates)

        # Status validation
        if 'status' in self.df.columns:
            invalid_status = self._validate_status()
            if invalid_status['count'] > 0:
                invalid_data.append(invalid_status)

        # Payment method validation
        if 'payment_method' in self.df.columns:
            invalid_payment = self._validate_payment_method()
            if invalid_payment['count'] > 0:
                invalid_data.append(invalid_payment)

        # Price validation
        if 'unit_price' in self.df.columns:
            invalid_prices = self._validate_prices()
            if invalid_prices['count'] > 0:
                invalid_data.append(invalid_prices)

        # Negative amounts
        if 'total_amount' in self.df.columns:
            negative_amounts = self._validate_amounts()
            if negative_amounts['count'] > 0:
                invalid_data.append(negative_amounts)

        return {
            "invalid_patterns": invalid_data,
            "total_invalid_count": sum(item['count'] for item in invalid_data)
        }

    def _validate_emails(self) -> Dict[str, Any]:
        """Validate email formats."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        non_null_emails = self.df['email'].dropna()
        invalid = ~non_null_emails.apply(lambda x: bool(re.match(email_pattern, str(x))))
        invalid_count = invalid.sum()

        # Get full rows with invalid emails
        invalid_rows = []
        if invalid_count > 0:
            invalid_indices = non_null_emails[invalid].index
            invalid_rows = self._clean_for_json(self.df.loc[invalid_indices])

        return {
            "column": "email",
            "issue_type": "Invalid Format",
            "count": int(invalid_count),
            "percentage": self._safe_percentage(invalid_count, self.total_records),
            "description": "Email addresses missing @ symbol or domain",
            "examples": non_null_emails[invalid].head(3).tolist() if invalid_count > 0 else [],
            "invalid_rows": invalid_rows
        }

    def _validate_ages(self) -> Dict[str, Any]:
        """Validate age values."""
        non_null_ages = self.df['age'].dropna()
        invalid = (non_null_ages < 0) | (non_null_ages > 120)
        invalid_count = invalid.sum()

        # Get full rows with invalid ages
        invalid_rows = []
        if invalid_count > 0:
            invalid_indices = non_null_ages[invalid].index
            invalid_rows = self._clean_for_json(self.df.loc[invalid_indices])

        return {
            "column": "age",
            "issue_type": "Invalid Range",
            "count": int(invalid_count),
            "percentage": self._safe_percentage(invalid_count, self.total_records),
            "description": "Age values that are negative or unrealistically high (>120)",
            "examples": non_null_ages[invalid].head(3).tolist() if invalid_count > 0 else [],
            "invalid_rows": invalid_rows
        }

    def _validate_dates(self, column: str) -> Dict[str, Any]:
        """Validate date values."""
        try:
            dates = pd.to_datetime(self.df[column], errors='coerce')
            today = pd.Timestamp.now()
            future_dates = dates > today
            invalid_count = future_dates.sum()

            # Get full rows with future dates
            invalid_rows = []
            if invalid_count > 0:
                invalid_rows = self._clean_for_json(self.df.loc[future_dates])

            return {
                "column": column,
                "issue_type": "Future Date",
                "count": int(invalid_count),
                "percentage": self._safe_percentage(invalid_count, self.total_records),
                "description": f"Future dates in {column} (data entry errors)",
                "examples": self.df.loc[future_dates, column].head(3).tolist() if invalid_count > 0 else [],
                "invalid_rows": invalid_rows
            }
        except:
            return {"column": column, "issue_type": "Date Validation", "count": 0, "percentage": 0, "description": "", "examples": [], "invalid_rows": []}

    def _validate_status(self) -> Dict[str, Any]:
        """Validate status values."""
        # Determine valid statuses based on dataset type
        if 'transaction_id' in self.df.columns:
            # Transaction dataset
            valid_statuses = ['Completed', 'Failed', 'Pending']
            description = "Status values that are not Completed, Failed, or Pending"
        else:
            # Customer dataset
            valid_statuses = ['Active', 'Inactive', 'Suspended']
            description = "Status values that are not Active, Inactive, or Suspended"

        non_null_status = self.df['status'].dropna()
        invalid = ~non_null_status.isin(valid_statuses)
        invalid_count = invalid.sum()

        # Get full rows with invalid status
        invalid_rows = []
        if invalid_count > 0:
            invalid_indices = non_null_status[invalid].index
            invalid_rows = self._clean_for_json(self.df.loc[invalid_indices])

        return {
            "column": "status",
            "issue_type": "Invalid Value",
            "count": int(invalid_count),
            "percentage": self._safe_percentage(invalid_count, self.total_records),
            "description": description,
            "examples": non_null_status[invalid].unique().tolist() if invalid_count > 0 else [],
            "invalid_rows": invalid_rows
        }

    def _validate_payment_method(self) -> Dict[str, Any]:
        """Validate payment method values."""
        valid_methods = ['Credit Card', 'Debit Card', 'PayPal', 'Cash']
        non_null_payment = self.df['payment_method'].dropna()
        invalid = ~non_null_payment.isin(valid_methods)
        invalid_count = invalid.sum()

        # Get full rows with invalid payment methods
        invalid_rows = []
        if invalid_count > 0:
            invalid_indices = non_null_payment[invalid].index
            invalid_rows = self._clean_for_json(self.df.loc[invalid_indices])

        return {
            "column": "payment_method",
            "issue_type": "Invalid Value",
            "count": int(invalid_count),
            "percentage": self._safe_percentage(invalid_count, self.total_records),
            "description": "Payment methods that are not valid options",
            "examples": non_null_payment[invalid].unique().tolist() if invalid_count > 0 else [],
            "invalid_rows": invalid_rows
        }

    def _validate_prices(self) -> Dict[str, Any]:
        """Validate unit prices for unrealistic values."""
        prices = self.df['unit_price'].dropna()
        # Flag prices that seem unrealistic (too high or negative)
        invalid = (prices < 0) | (prices > 1000)
        invalid_count = invalid.sum()

        # Get full rows with invalid prices
        invalid_rows = []
        if invalid_count > 0:
            invalid_indices = prices[invalid].index
            invalid_rows = self._clean_for_json(self.df.loc[invalid_indices])

        return {
            "column": "unit_price",
            "issue_type": "Pricing Error",
            "count": int(invalid_count),
            "percentage": self._safe_percentage(invalid_count, self.total_records),
            "description": "Unit prices that are negative or unrealistically high",
            "examples": prices[invalid].head(3).tolist() if invalid_count > 0 else [],
            "invalid_rows": invalid_rows
        }

    def _validate_amounts(self) -> Dict[str, Any]:
        """Validate transaction amounts."""
        amounts = self.df['total_amount'].dropna()
        invalid = amounts < 0
        invalid_count = invalid.sum()

        # Get full rows with negative amounts
        invalid_rows = []
        if invalid_count > 0:
            invalid_indices = amounts[invalid].index
            invalid_rows = self._clean_for_json(self.df.loc[invalid_indices])

        return {
            "column": "total_amount",
            "issue_type": "Negative Amount",
            "count": int(invalid_count),
            "percentage": self._safe_percentage(invalid_count, self.total_records),
            "description": "Negative transaction amounts (returns or errors)",
            "examples": amounts[invalid].head(3).tolist() if invalid_count > 0 else [],
            "invalid_rows": invalid_rows
        }

    def analyze_duplicates(self) -> Dict[str, Any]:
        """
        Analyze duplicate records.

        Only considers rows as duplicates if ALL non-primary-key columns have identical content.
        Only the primary key column is excluded (e.g., 'transaction_id', 'customer_id', 'id').
        Foreign keys (like 'customer_id' in transactions) are INCLUDED in the comparison.
        """
        duplicate_info = []

        # Identify PRIMARY KEY columns to exclude (not foreign keys)
        # Primary key is typically: 'id', 'ID', or '{dataset_name}_id'
        dataset_base_name = self.dataset_name.replace('.csv', '').lower().split('/')[-1]

        primary_key_columns = []
        for col in self.df.columns:
            col_lower = col.lower()
            # Exact match for 'id'
            if col_lower == 'id':
                primary_key_columns.append(col)
            # Match for '{dataset_name}_id' pattern (e.g., 'transaction_id' for 'transactions.csv')
            elif col_lower == f"{dataset_base_name.rstrip('s')}_id":  # Handle plural dataset names
                primary_key_columns.append(col)
            elif col_lower == f"{dataset_base_name}_id":
                primary_key_columns.append(col)

        # All other columns (including foreign keys like customer_id in transactions)
        non_primary_key_columns = [col for col in self.df.columns if col not in primary_key_columns]

        if not non_primary_key_columns:
            # If all columns are primary keys, no duplicates to check
            return {
                "duplicate_patterns": [],
                "total_duplicates": 0
            }

        # Create a temporary dataframe with only non-primary-key columns for comparison
        df_for_comparison = self.df[non_primary_key_columns].copy()

        # Find duplicates based on ALL non-primary-key columns being identical
        # keep=False marks all duplicates (not just the first/last occurrence)
        duplicates_mask = df_for_comparison.duplicated(keep=False)
        duplicate_count = duplicates_mask.sum()

        if duplicate_count > 0:
            # Group duplicate rows together
            duplicate_groups = []
            df_with_duplicates = self.df[duplicates_mask].copy()
            df_comparison_duplicates = df_for_comparison[duplicates_mask].copy()

            # Add a temporary group identifier
            # Rows with identical non-primary-key values will get the same group number
            df_comparison_duplicates['_temp_group'] = df_comparison_duplicates.groupby(
                non_primary_key_columns, dropna=False
            ).ngroup()

            # Get unique groups
            unique_groups = df_comparison_duplicates['_temp_group'].unique()

            for group_id in unique_groups:
                # Get all rows in this duplicate group
                group_indices = df_comparison_duplicates[
                    df_comparison_duplicates['_temp_group'] == group_id
                ].index

                # Get the full rows (including primary key columns) for this group
                group_rows = self.df.loc[group_indices]

                # Only include groups with 2 or more rows
                if len(group_rows) > 1:
                    duplicate_groups.append(self._clean_for_json(group_rows))

            duplicate_info.append({
                "type": "Full Record Duplicates",
                "count": int(duplicate_count),
                "percentage": self._safe_percentage(duplicate_count, self.total_records),
                "description": f"Records with identical content in all {len(non_primary_key_columns)} columns (excluding primary key)",
                "duplicate_groups": duplicate_groups
            })

        return {
            "duplicate_patterns": duplicate_info,
            "total_duplicates": sum(item['count'] for item in duplicate_info)
        }

    def analyze_logical_issues(self) -> Dict[str, Any]:
        """Analyze logical consistency issues."""
        logical_issues = []

        # Check selling price vs cost price
        if 'selling_price' in self.df.columns and 'cost_price' in self.df.columns:
            price_issues = self.df['selling_price'] < self.df['cost_price']
            issue_count = price_issues.sum()
            if issue_count > 0:
                # Get all rows with price issues
                issue_rows = self._clean_for_json(self.df[price_issues])

                logical_issues.append({
                    "type": "Selling Price Below Cost",
                    "count": int(issue_count),
                    "percentage": self._safe_percentage(issue_count, self.total_records),
                    "description": "Products where selling price is less than cost price",
                    "severity": "high",
                    "issue_rows": issue_rows
                })

        # Check stock levels vs reorder levels
        if 'current_stock' in self.df.columns and 'reorder_level' in self.df.columns:
            stock_issues = self.df['current_stock'] < self.df['reorder_level']
            issue_count = stock_issues.sum()
            if issue_count > 0:
                # Get all rows with stock issues
                issue_rows = self._clean_for_json(self.df[stock_issues])

                logical_issues.append({
                    "type": "Stock Below Reorder Level",
                    "count": int(issue_count),
                    "percentage": self._safe_percentage(issue_count, self.total_records),
                    "description": "Products with stock levels below reorder threshold",
                    "severity": "medium",
                    "issue_rows": issue_rows
                })

        return {
            "logical_inconsistencies": logical_issues,
            "total_issues": sum(item['count'] for item in logical_issues)
        }

    def generate_statistics(self) -> Dict[str, Any]:
        """Generate summary statistics for numeric columns."""
        stats = {}
        numeric_columns = self.df.select_dtypes(include=[np.number]).columns

        for col in numeric_columns:
            # Helper function to safely round values, handling NaN and inf
            def safe_round(value):
                if value is None or np.isnan(value) or np.isinf(value):
                    return None
                return round(float(value), 2)

            stats[col] = {
                "mean": safe_round(self.df[col].mean()) if not self.df[col].isna().all() else None,
                "median": safe_round(self.df[col].median()) if not self.df[col].isna().all() else None,
                "min": safe_round(self.df[col].min()) if not self.df[col].isna().all() else None,
                "max": safe_round(self.df[col].max()) if not self.df[col].isna().all() else None,
                "std": safe_round(self.df[col].std()) if not self.df[col].isna().all() else None
            }

        return stats

    def _simplify_data_type(self, col_name: str, dtype) -> str:
        """Convert pandas dtype to simplified user-friendly type."""
        dtype_str = str(dtype).lower()

        # Check if column name suggests it's a date
        if 'date' in col_name.lower():
            return 'date'

        # Check pandas dtype
        if 'int' in dtype_str:
            return 'int'
        elif 'float' in dtype_str:
            return 'float'
        elif 'bool' in dtype_str:
            return 'boolean'
        elif 'datetime' in dtype_str:
            return 'date'
        elif 'object' in dtype_str:
            return 'string'
        else:
            return 'string'

    def analyze_columns(self) -> List[Dict[str, Any]]:
        """Analyze each column individually."""
        column_details = []

        for col in self.df.columns:
            non_null_count = self.df[col].count()
            null_count = self.df[col].isna().sum()

            detail = {
                "name": col,
                "data_type": self._simplify_data_type(col, self.df[col].dtype),
                "non_null_count": int(non_null_count),
                "null_count": int(null_count),
                "null_percentage": self._safe_percentage(null_count, self.total_records),
                "unique_values": int(self.df[col].nunique())
            }

            # Add sample values
            if non_null_count > 0:
                detail["sample_values"] = self.df[col].dropna().head(3).tolist()

            column_details.append(detail)

        return column_details
