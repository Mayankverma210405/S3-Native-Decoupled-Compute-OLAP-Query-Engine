import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class CsvAnalysisResult:
    """
    Structured metadata extracted from a CSV file.

    This object is not stored directly in the database.
    Its values are used to populate the datasets table.
    """

    file_size_bytes: int
    row_count: int
    column_count: int
    schema_json: dict[str, Any]


class CsvAnalyzer:
    """
    Analyze CSV files and extract lightweight metadata.

    This service intentionally uses Python's built-in csv module.
    It avoids loading the entire file into memory, which is important
    for a query engine that may handle large datasets later.
    """

    def analyze(self, file_path: str | Path, sample_size: int = 1000) -> CsvAnalysisResult:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")

        if path.suffix.lower() != ".csv":
            raise ValueError(f"Only CSV files are supported in v1: {path.name}")

        file_size_bytes = path.stat().st_size

        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise ValueError("CSV file does not contain a header row")

            columns = self._normalize_columns(reader.fieldnames)
            observed_types: dict[str, set[str]] = {column: set() for column in columns}

            row_count = 0

            for row in reader:
                row_count += 1

                if row_count <= sample_size:
                    for column in columns:
                        value = row.get(column)
                        observed_types[column].add(self._infer_value_type(value))

        schema_json = {
            "columns": [
                {
                    "name": column,
                    "type": self._resolve_column_type(observed_types[column]),
                }
                for column in columns
            ]
        }

        return CsvAnalysisResult(
            file_size_bytes=file_size_bytes,
            row_count=row_count,
            column_count=len(columns),
            schema_json=schema_json,
        )

    def _normalize_columns(self, fieldnames: list[str]) -> list[str]:
        """
        Clean column names from the CSV header.

        Blank column names are replaced with column_1, column_2, etc.
        """
        normalized_columns: list[str] = []

        for index, name in enumerate(fieldnames, start=1):
            cleaned_name = (name or "").strip()

            if not cleaned_name:
                cleaned_name = f"column_{index}"

            normalized_columns.append(cleaned_name)

        return normalized_columns

    def _infer_value_type(self, value: str | None) -> str:
        """
        Infer the type of a single CSV cell value.

        CSV values arrive as strings, so we detect the most likely type.
        """
        if value is None:
            return "null"

        cleaned_value = value.strip()

        if cleaned_value == "":
            return "null"

        lowered_value = cleaned_value.lower()

        if lowered_value in {"true", "false", "yes", "no"}:
            return "boolean"

        if self._is_integer(cleaned_value):
            return "integer"

        if self._is_float(cleaned_value):
            return "double"

        if self._is_datetime(cleaned_value):
            return "datetime"

        return "string"

    def _resolve_column_type(self, observed_types: set[str]) -> str:
        """
        Resolve many observed cell types into one column type.
        """
        non_null_types = observed_types - {"null"}

        if not non_null_types:
            return "string"

        if "string" in non_null_types:
            return "string"

        if "datetime" in non_null_types:
            return "datetime"

        if "double" in non_null_types:
            return "double"

        if "integer" in non_null_types:
            return "integer"

        if "boolean" in non_null_types:
            return "boolean"

        return "string"

    def _is_integer(self, value: str) -> bool:
        try:
            int(value)
            return True
        except ValueError:
            return False

    def _is_float(self, value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _is_datetime(self, value: str) -> bool:
        try:
            datetime.fromisoformat(value)
            return True
        except ValueError:
            return False