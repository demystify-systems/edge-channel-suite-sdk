"""
Mock database client for testing purposes.

Provides in-memory storage for job tracking and completeness cache without
requiring a real database connection.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid


class MockDBClient:
    """Mock database client for testing."""

    def __init__(self):
        """Initialize mock database with in-memory storage."""
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.completeness_records: Dict[str, Dict[str, Any]] = {}

    async def insert(self, table: str, record: Dict[str, Any]) -> str:
        """
        Insert a record into a table.
        
        Args:
            table: Table name
            record: Record data
            
        Returns:
            Record ID
        """
        if table == "saas_edge_jobs":
            job_id = record.get("job_id", str(uuid.uuid4()))
            self.jobs[job_id] = record.copy()
            return job_id
        elif table == "product_template_completeness":
            internal_id = record.get("internal_id", str(uuid.uuid4()))
            record["internal_id"] = internal_id
            self.completeness_records[internal_id] = record.copy()
            return internal_id
        else:
            raise ValueError(f"Unknown table: {table}")

    async def insert_batch(self, table: str, records: List[Dict[str, Any]]) -> List[str]:
        """
        Insert multiple records.
        
        Args:
            table: Table name
            records: List of records
            
        Returns:
            List of record IDs
        """
        ids = []
        for record in records:
            record_id = await self.insert(table, record)
            ids.append(record_id)
        return ids

    async def update(self, table: str, record_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a record.
        
        Args:
            table: Table name
            record_id: Record identifier
            updates: Fields to update
            
        Returns:
            True if successful
        """
        if table == "saas_edge_jobs":
            if record_id in self.jobs:
                self.jobs[record_id].update(updates)
                self.jobs[record_id]["updated_at"] = datetime.now()
                return True
            return False
        elif table == "product_template_completeness":
            if record_id in self.completeness_records:
                self.completeness_records[record_id].update(updates)
                self.completeness_records[record_id]["updated_at"] = datetime.now()
                return True
            return False
        else:
            raise ValueError(f"Unknown table: {table}")

    async def query(self, table: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Query records from a table.
        
        Args:
            table: Table name
            filters: Filter conditions
            
        Returns:
            List of matching records
        """
        filters = filters or {}

        if table == "saas_edge_jobs":
            records = list(self.jobs.values())
        elif table == "product_template_completeness":
            records = list(self.completeness_records.values())
        else:
            raise ValueError(f"Unknown table: {table}")

        # Apply filters
        for key, value in filters.items():
            records = [r for r in records if r.get(key) == value]

        return records

    async def get_by_id(self, table: str, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a record by ID.
        
        Args:
            table: Table name
            record_id: Record identifier
            
        Returns:
            Record or None
        """
        if table == "saas_edge_jobs":
            return self.jobs.get(record_id)
        elif table == "product_template_completeness":
            return self.completeness_records.get(record_id)
        else:
            raise ValueError(f"Unknown table: {table}")

    async def delete(self, table: str, record_id: str) -> bool:
        """
        Delete a record.
        
        Args:
            table: Table name
            record_id: Record identifier
            
        Returns:
            True if deleted
        """
        if table == "saas_edge_jobs":
            if record_id in self.jobs:
                del self.jobs[record_id]
                return True
            return False
        elif table == "product_template_completeness":
            if record_id in self.completeness_records:
                del self.completeness_records[record_id]
                return True
            return False
        else:
            raise ValueError(f"Unknown table: {table}")

    def clear_all(self):
        """Clear all data (useful for test cleanup)."""
        self.jobs.clear()
        self.completeness_records.clear()

    def get_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        return {
            "jobs": len(self.jobs),
            "completeness_records": len(self.completeness_records),
        }
