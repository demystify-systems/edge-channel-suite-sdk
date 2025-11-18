"""
Completeness Cache Handler

Manages reading and writing to the product_template_completeness table.
This cache stores intermediate transformed data, validation errors, and metadata
for reuse during export operations.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..core.types import RunType, CompletenessRecord


class CompletenessWriter:
    """Writes completeness records to the cache"""
    
    def __init__(self, db_client):
        """
        Initialize the completeness writer.
        
        Args:
            db_client: Database client (GraphQL or PostgreSQL)
        """
        self.db = db_client
    
    async def write_record(
        self,
        job_id: str,
        run_type: RunType,
        saas_edge_id: str,
        template_id: str,
        transformed_response: Dict[str, Any],
        validation_errors: Dict[str, List[Dict[str, Any]]],
        is_valid: bool,
        error_count: int,
        product_id: Optional[str] = None,
        file_row_number: Optional[int] = None,
        raw_input_snapshot: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Write a single completeness record.
        
        Args:
            job_id: Job identifier
            run_type: IMPORT or EXPORT
            saas_edge_id: Tenant identifier
            template_id: Template identifier
            transformed_response: Transformed field values as JSON
            validation_errors: Validation errors by field
            is_valid: Whether the record passed validation
            error_count: Number of validation errors
            product_id: Product identifier (optional)
            file_row_number: Row number in source file (optional)
            raw_input_snapshot: Original raw data (optional)
        
        Returns:
            internal_id of the created record
        """
        record_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        record = {
            "internal_id": record_id,
            "job_id": job_id,
            "run_type": run_type.value if isinstance(run_type, RunType) else run_type,
            "saas_edge_id": saas_edge_id,
            "product_id": product_id,
            "template_id": template_id,
            "transformed_response": transformed_response,
            "validation_errors": validation_errors,
            "is_valid": is_valid,
            "error_count": error_count,
            "cache_freshness": True,
            "processing_status": "VALIDATED",
            "file_row_number": file_row_number,
            "raw_input_snapshot": raw_input_snapshot,
            "created_at": now,
            "updated_at": now
        }
        
        # Insert into database
        await self.db.insert("product_template_completeness", record)
        
        return record_id
    
    async def write_batch(
        self,
        records: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Write multiple completeness records in a batch.
        
        Args:
            records: List of record dictionaries
        
        Returns:
            List of internal_ids for created records
        """
        record_ids = []
        now = datetime.utcnow()
        
        for record in records:
            record_id = str(uuid.uuid4())
            record["internal_id"] = record_id
            record["created_at"] = now
            record["updated_at"] = now
            record["cache_freshness"] = True
            record_ids.append(record_id)
        
        # Batch insert
        await self.db.insert_batch("product_template_completeness", records)
        
        return record_ids
    
    async def invalidate_cache(
        self,
        saas_edge_id: str,
        template_id: Optional[str] = None,
        product_id: Optional[str] = None
    ) -> int:
        """
        Invalidate cache entries by setting cache_freshness to False.
        
        Args:
            saas_edge_id: Tenant identifier
            template_id: Optional template filter
            product_id: Optional product filter
        
        Returns:
            Number of records invalidated
        """
        filters = {"saas_edge_id": saas_edge_id}
        if template_id:
            filters["template_id"] = template_id
        if product_id:
            filters["product_id"] = product_id
        
        update_data = {
            "cache_freshness": False,
            "updated_at": datetime.utcnow()
        }
        
        count = await self.db.update(
            "product_template_completeness",
            filters,
            update_data
        )
        
        return count


class CompletenessReader:
    """Reads completeness records from the cache"""
    
    def __init__(self, db_client):
        """
        Initialize the completeness reader.
        
        Args:
            db_client: Database client (GraphQL or PostgreSQL)
        """
        self.db = db_client
    
    async def get_record(
        self,
        saas_edge_id: str,
        template_id: str,
        product_id: str,
        check_freshness: bool = True
    ) -> Optional[CompletenessRecord]:
        """
        Get a single completeness record.
        
        Args:
            saas_edge_id: Tenant identifier
            template_id: Template identifier
            product_id: Product identifier
            check_freshness: Only return if cache_freshness is True
        
        Returns:
            Completeness record or None if not found
        """
        filters = {
            "saas_edge_id": saas_edge_id,
            "template_id": template_id,
            "product_id": product_id
        }
        
        if check_freshness:
            filters["cache_freshness"] = True
        
        # Get most recent record
        record = await self.db.query_one(
            "product_template_completeness",
            filters,
            order_by="created_at DESC"
        )
        
        return record
    
    async def get_batch(
        self,
        saas_edge_id: str,
        template_id: str,
        product_ids: List[str],
        check_freshness: bool = True
    ) -> Dict[str, CompletenessRecord]:
        """
        Get multiple completeness records in a batch.
        
        Args:
            saas_edge_id: Tenant identifier
            template_id: Template identifier
            product_ids: List of product identifiers
            check_freshness: Only return if cache_freshness is True
        
        Returns:
            Dictionary mapping product_id to completeness record
        """
        filters = {
            "saas_edge_id": saas_edge_id,
            "template_id": template_id,
            "product_id__in": product_ids
        }
        
        if check_freshness:
            filters["cache_freshness"] = True
        
        records = await self.db.query_many(
            "product_template_completeness",
            filters
        )
        
        # Map by product_id
        result = {}
        for record in records:
            result[record["product_id"]] = record
        
        return result
    
    async def check_freshness(
        self,
        saas_edge_id: str,
        template_id: str,
        product_id: str,
        last_product_updated: datetime,
        last_template_updated: datetime
    ) -> bool:
        """
        Check if cached record is still fresh based on update timestamps.
        
        Args:
            saas_edge_id: Tenant identifier
            template_id: Template identifier
            product_id: Product identifier
            last_product_updated: Last time product was updated
            last_template_updated: Last time template was updated
        
        Returns:
            True if cache is fresh, False otherwise
        """
        record = await self.get_record(
            saas_edge_id,
            template_id,
            product_id,
            check_freshness=True
        )
        
        if not record:
            return False
        
        # Check if cache was created after last product/template update
        cache_created = record.get("created_at")
        if not cache_created:
            return False
        
        if last_product_updated and cache_created < last_product_updated:
            return False
        
        if last_template_updated and cache_created < last_template_updated:
            return False
        
        return True
    
    async def get_validation_errors(
        self,
        saas_edge_id: str,
        template_id: str,
        job_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all validation errors for a template or job.
        
        Args:
            saas_edge_id: Tenant identifier
            template_id: Template identifier
            job_id: Optional job identifier filter
        
        Returns:
            List of records with validation errors
        """
        filters = {
            "saas_edge_id": saas_edge_id,
            "template_id": template_id,
            "is_valid": False
        }
        
        if job_id:
            filters["job_id"] = job_id
        
        records = await self.db.query_many(
            "product_template_completeness",
            filters,
            fields=["product_id", "validation_errors", "error_count", "file_row_number"]
        )
        
        return records
    
    async def get_completeness_stats(
        self,
        saas_edge_id: str,
        template_id: str
    ) -> Dict[str, Any]:
        """
        Get completeness statistics for a template.
        
        Args:
            saas_edge_id: Tenant identifier
            template_id: Template identifier
        
        Returns:
            Statistics dictionary with counts and percentages
        """
        filters = {
            "saas_edge_id": saas_edge_id,
            "template_id": template_id,
            "cache_freshness": True
        }
        
        # Get counts
        total = await self.db.count("product_template_completeness", filters)
        
        filters["is_valid"] = True
        valid = await self.db.count("product_template_completeness", filters)
        
        filters["is_valid"] = False
        invalid = await self.db.count("product_template_completeness", filters)
        
        return {
            "total_records": total,
            "valid_records": valid,
            "invalid_records": invalid,
            "completeness_percentage": (valid / total * 100) if total > 0 else 0,
            "error_rate": (invalid / total * 100) if total > 0 else 0
        }
