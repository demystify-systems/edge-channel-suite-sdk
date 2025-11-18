"""
Job Manager

Manages job status updates and metrics in the saas_edge_jobs table.
Tracks job progress through various stages and collects performance metrics.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from ..core.types import JobType, JobStatus


class JobStatusUpdater:
    """Updates job status and metrics"""
    
    def __init__(self, db_client):
        """
        Initialize the job status updater.
        
        Args:
            db_client: Database client (GraphQL or PostgreSQL)
        """
        self.db = db_client
    
    async def create_job(
        self,
        job_name: str,
        job_type: JobType,
        saas_edge_id: str,
        request_args: Dict[str, Any],
        job_id: Optional[str] = None
    ) -> str:
        """
        Create a new job record.
        
        Args:
            job_name: Human-friendly job name
            job_type: Type of job (PRODUCT_IMPORT, PRODUCT_EXPORT, etc.)
            saas_edge_id: Tenant identifier
            request_args: Original request parameters
            job_id: Optional job ID (generated if not provided)
        
        Returns:
            job_id of created job
        """
        if not job_id:
            job_id = str(uuid.uuid4())
        
        now = datetime.utcnow()
        
        job_record = {
            "job_id": job_id,
            "job_name": job_name,
            "job_type": job_type.value if isinstance(job_type, JobType) else job_type,
            "job_status": JobStatus.IMPORT_INIT.value if "IMPORT" in str(job_type) else JobStatus.EXPORT_INIT.value,
            "saas_edge_id": saas_edge_id,
            "request_args": request_args,
            "job_response": {},
            "metrics": {
                "created_at": now.isoformat(),
                "current_step": "INIT",
                "steps": []
            },
            "created_at": now,
            "updated_at": now
        }
        
        await self.db.insert("saas_edge_jobs", job_record)
        
        return job_id
    
    async def update_status(
        self,
        job_id: str,
        new_status: JobStatus,
        metrics_update: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update job status and optionally add metrics.
        
        Args:
            job_id: Job identifier
            new_status: New status to set
            metrics_update: Optional metrics to add to the job
        """
        update_data = {
            "job_status": new_status.value if isinstance(new_status, JobStatus) else new_status,
            "updated_at": datetime.utcnow()
        }
        
        if metrics_update:
            # Get current metrics
            current_job = await self.db.query_one(
                "saas_edge_jobs",
                {"job_id": job_id},
                fields=["metrics"]
            )
            
            current_metrics = current_job.get("metrics", {}) if current_job else {}
            
            # Add new step to metrics
            step_entry = {
                "step": new_status.value if isinstance(new_status, JobStatus) else new_status,
                "started_at": datetime.utcnow().isoformat(),
                **metrics_update
            }
            
            if "steps" not in current_metrics:
                current_metrics["steps"] = []
            
            current_metrics["steps"].append(step_entry)
            current_metrics["current_step"] = new_status.value if isinstance(new_status, JobStatus) else new_status
            
            update_data["metrics"] = current_metrics
        
        await self.db.update(
            "saas_edge_jobs",
            {"job_id": job_id},
            update_data
        )
    
    async def add_metrics(
        self,
        job_id: str,
        metrics: Dict[str, Any]
    ) -> None:
        """
        Add metrics to the current job step.
        
        Args:
            job_id: Job identifier
            metrics: Metrics to add
        """
        # Get current job
        current_job = await self.db.query_one(
            "saas_edge_jobs",
            {"job_id": job_id},
            fields=["metrics"]
        )
        
        if not current_job:
            raise ValueError(f"Job {job_id} not found")
        
        current_metrics = current_job.get("metrics", {})
        
        # Update the latest step with new metrics
        if "steps" in current_metrics and current_metrics["steps"]:
            current_metrics["steps"][-1].update(metrics)
        else:
            # No steps yet, add to root metrics
            current_metrics.update(metrics)
        
        await self.db.update(
            "saas_edge_jobs",
            {"job_id": job_id},
            {"metrics": current_metrics, "updated_at": datetime.utcnow()}
        )
    
    async def complete_step(
        self,
        job_id: str,
        rows_processed: int = 0,
        rows_success: int = 0,
        rows_failed: int = 0,
        errors: Optional[List[str]] = None
    ) -> None:
        """
        Mark the current step as complete with final metrics.
        
        Args:
            job_id: Job identifier
            rows_processed: Total rows processed in this step
            rows_success: Number of successful rows
            rows_failed: Number of failed rows
            errors: Optional list of error messages
        """
        metrics = {
            "completed_at": datetime.utcnow().isoformat(),
            "rows_processed": rows_processed,
            "rows_success": rows_success,
            "rows_failed": rows_failed
        }
        
        if errors:
            metrics["errors"] = errors
        
        await self.add_metrics(job_id, metrics)
    
    async def complete_job(
        self,
        job_id: str,
        success: bool,
        total_rows: int = 0,
        success_count: int = 0,
        failed_count: int = 0,
        response_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Mark job as completed (success or failure).
        
        Args:
            job_id: Job identifier
            success: Whether job completed successfully
            total_rows: Total rows processed
            success_count: Number of successful rows
            failed_count: Number of failed rows
            response_data: Optional additional response data
        """
        job_response = {
            "total": total_rows,
            "success": success_count,
            "failed": failed_count,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        if response_data:
            job_response.update(response_data)
        
        update_data = {
            "job_status": JobStatus.COMPLETED.value if success else JobStatus.FAILED.value,
            "job_response": job_response,
            "updated_at": datetime.utcnow()
        }
        
        await self.db.update(
            "saas_edge_jobs",
            {"job_id": job_id},
            update_data
        )
    
    async def fail_job(
        self,
        job_id: str,
        error_message: str,
        error_detail: Optional[str] = None
    ) -> None:
        """
        Mark job as failed with error details.
        
        Args:
            job_id: Job identifier
            error_message: Short error message
            error_detail: Optional full error details/stack trace
        """
        job_response = {
            "error": error_message,
            "failed_at": datetime.utcnow().isoformat()
        }
        
        update_data = {
            "job_status": JobStatus.FAILED.value,
            "job_response": job_response,
            "updated_at": datetime.utcnow()
        }
        
        if error_detail:
            update_data["error_detail"] = error_detail
        
        await self.db.update(
            "saas_edge_jobs",
            {"job_id": job_id},
            update_data
        )
    
    async def get_job_status(
        self,
        job_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get current job status and metrics.
        
        Args:
            job_id: Job identifier
        
        Returns:
            Job record with status and metrics
        """
        job = await self.db.query_one(
            "saas_edge_jobs",
            {"job_id": job_id}
        )
        
        return job
    
    async def get_jobs_by_status(
        self,
        saas_edge_id: str,
        status: JobStatus,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get jobs by status for a tenant.
        
        Args:
            saas_edge_id: Tenant identifier
            status: Job status to filter by
            limit: Maximum number of jobs to return
        
        Returns:
            List of job records
        """
        jobs = await self.db.query_many(
            "saas_edge_jobs",
            {
                "saas_edge_id": saas_edge_id,
                "job_status": status.value if isinstance(status, JobStatus) else status
            },
            order_by="created_at DESC",
            limit=limit
        )
        
        return jobs
    
    async def get_recent_jobs(
        self,
        saas_edge_id: str,
        job_type: Optional[JobType] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent jobs for a tenant.
        
        Args:
            saas_edge_id: Tenant identifier
            job_type: Optional job type filter
            limit: Maximum number of jobs to return
        
        Returns:
            List of job records
        """
        filters = {"saas_edge_id": saas_edge_id}
        
        if job_type:
            filters["job_type"] = job_type.value if isinstance(job_type, JobType) else job_type
        
        jobs = await self.db.query_many(
            "saas_edge_jobs",
            filters,
            order_by="created_at DESC",
            limit=limit
        )
        
        return jobs
    
    async def calculate_duration(
        self,
        job_id: str
    ) -> Optional[float]:
        """
        Calculate job duration in seconds.
        
        Args:
            job_id: Job identifier
        
        Returns:
            Duration in seconds, or None if job not complete
        """
        job = await self.get_job_status(job_id)
        
        if not job:
            return None
        
        created_at = job.get("created_at")
        updated_at = job.get("updated_at")
        
        if not created_at or not updated_at:
            return None
        
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        duration = (updated_at - created_at).total_seconds()
        return duration
