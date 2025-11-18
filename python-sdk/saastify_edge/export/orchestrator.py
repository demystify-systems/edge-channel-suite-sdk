"""
Export Pipeline Orchestrator - End-to-end export workflow.

Stages:
1. EXPORT_INIT - Initialize job
2. EXPORT_LOAD_TEMPLATE - Load channel template
3. EXPORT_FETCH_PRODUCTS - Fetch products from database
4. EXPORT_TRANSFORM - Apply transformations (with cache reuse)
5. EXPORT_VALIDATE - Validate data
6. EXPORT_WRITE_CACHE - Write/update completeness cache
7. EXPORT_BUILD_FILE - Generate output file
8. EXPORT_UPLOAD_FILE - Upload to destination
9. EXPORT_NOTIFY - Finalize and notify
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import uuid

from ..transformations.engine import apply_transformations
from ..validation.engine import validate_field, validate_row
from ..db.completeness_cache import CompletenessWriter, CompletenessReader
from ..db.job_manager import JobStatusUpdater
from ..import_pipeline.template_mapper import TemplateMapper
from .file_builders import FileBuilderFactory

logger = logging.getLogger(__name__)


class ExportPipelineConfig:
    """Configuration for export pipeline."""

    def __init__(
        self,
        template_id: str,
        saas_edge_id: str,
        output_path: str,
        file_format: str = "csv",
        job_name: Optional[str] = None,
        product_filters: Optional[Dict[str, Any]] = None,
        file_config: Optional[Dict[str, Any]] = None,
        reuse_cache: bool = True,
        db_client: Optional[Any] = None,
    ):
        self.template_id = template_id
        self.saas_edge_id = saas_edge_id
        self.output_path = output_path
        self.file_format = file_format
        self.job_name = job_name or f"Export-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.product_filters = product_filters or {}
        self.file_config = file_config or {}
        self.reuse_cache = reuse_cache
        self.db_client = db_client


class ExportPipeline:
    """Orchestrates end-to-end export workflow."""

    def __init__(self, config: ExportPipelineConfig):
        """
        Initialize export pipeline.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config
        self.template_mapper = TemplateMapper(db_client=config.db_client)
        self.job_manager = JobStatusUpdater(db_client=config.db_client)
        self.completeness_reader = CompletenessReader(db_client=config.db_client)
        self.completeness_writer = CompletenessWriter(db_client=config.db_client)
        
        self.job_id: Optional[str] = None
        self.template = None
        self.products: List[Dict[str, Any]] = []

    async def run(self) -> Dict[str, Any]:
        """
        Execute full export pipeline.
        
        Returns:
            Job results with metrics
        """
        try:
            # Stage 1: Init job
            await self._initialize_job()

            # Stage 2: Load template
            await self._load_template()

            # Stage 3: Fetch products
            await self._fetch_products()

            # Stage 4-6: Transform, validate, cache
            transformed_data = await self._transform_and_validate()

            # Stage 7: Build file
            output_file = await self._build_file(transformed_data)

            # Stage 8: Upload (optional, for now just local)
            await self._upload_file(output_file)

            # Stage 9: Complete
            await self.job_manager.complete_job(
                job_id=self.job_id,
                job_response={
                    "output_path": output_file,
                    "total_rows": len(transformed_data),
                    "format": self.config.file_format,
                },
            )

            logger.info(f"Export job {self.job_id} completed successfully")
            return {
                "output_path": output_file,
                "total_rows": len(transformed_data),
                "job_id": self.job_id,
            }

        except Exception as e:
            logger.error(f"Export job {self.job_id} failed: {e}")
            if self.job_id:
                await self.job_manager.fail_job(
                    job_id=self.job_id,
                    error_message=str(e),
                )
            raise

    async def _initialize_job(self) -> None:
        """Stage 1: Initialize export job."""
        self.job_id = str(uuid.uuid4())
        await self.job_manager.create_job(
            job_id=self.job_id,
            job_name=self.config.job_name,
            job_type="EXPORT",
            saas_edge_id=self.config.saas_edge_id,
            request_args={
                "template_id": self.config.template_id,
                "file_format": self.config.file_format,
                "output_path": self.config.output_path,
                "filters": self.config.product_filters,
            },
        )
        logger.info(f"Started export job {self.job_id}")

    async def _load_template(self) -> None:
        """Stage 2: Load channel template."""
        await self.job_manager.update_status(
            job_id=self.job_id,
            status="EXPORT_LOAD_TEMPLATE",
        )

        logger.info(f"Loading template {self.config.template_id}")
        self.template = await self.template_mapper.load_template(
            template_id=self.config.template_id,
            saas_edge_id=self.config.saas_edge_id,
        )

    async def _fetch_products(self) -> None:
        """Stage 3: Fetch products from database."""
        await self.job_manager.update_status(
            job_id=self.job_id,
            status="EXPORT_FETCH_PRODUCTS",
        )

        # In production, this would fetch from database
        # For now, use mock data
        self.products = self._get_mock_products()

        logger.info(f"Fetched {len(self.products)} products for export")

        await self.job_manager.complete_step(
            job_id=self.job_id,
            step_name="fetch_products",
            metrics={"product_count": len(self.products)},
        )

    def _get_mock_products(self) -> List[Dict[str, Any]]:
        """Get mock product data for testing."""
        return [
            {
                "product_id": "prod-001",
                "product_title": "  wireless bluetooth headphones  ",
                "selling_price": "$49.99",
                "stock_qty": "150",
                "product_sku": "wbh-001",
                "product_description": "<p>Premium wireless headphones</p>",
            },
            {
                "product_id": "prod-002",
                "product_title": "smart watch fitness tracker",
                "selling_price": "99.00",
                "stock_qty": "75",
                "product_sku": "swft-002",
                "product_description": "Track your fitness goals",
            },
            {
                "product_id": "prod-003",
                "product_title": "portable power bank 20000mah",
                "selling_price": "29.99",
                "stock_qty": "200",
                "product_sku": "ppb-003",
                "product_description": "High capacity power bank",
            },
        ]

    async def _transform_and_validate(self) -> List[Dict[str, Any]]:
        """Stage 4-6: Transform, validate, and cache products."""
        await self.job_manager.update_status(
            job_id=self.job_id,
            status="EXPORT_TRANSFORM",
        )

        transformed_products = []
        completeness_records = []

        for product in self.products:
            # Check cache first if enabled
            if self.config.reuse_cache:
                cached = await self.completeness_reader.get_record(
                    saas_edge_id=self.config.saas_edge_id,
                    template_id=self.config.template_id,
                    product_id=product.get("product_id"),
                )
                
                if cached and cached.get("cache_freshness"):
                    logger.debug(f"Using cached data for product {product.get('product_id')}")
                    transformed_products.append(cached["transformed_response"])
                    continue

            # Transform product
            mapped_data = self.template_mapper.map_row_to_fields(
                raw_row=product,
                template=self.template,
            )

            transformed_data = {}
            for field_name, raw_value in mapped_data.items():
                transformations = self.template_mapper.get_transformation_pipeline(
                    template=self.template,
                    field_name=field_name,
                )
                
                if transformations:
                    rule_parts = []
                    for trans in transformations:
                        if trans.args:
                            args_str = "|".join(str(v) for v in trans.args.values())
                            rule_parts.append(f"{trans.operation}|{args_str}")
                        else:
                            rule_parts.append(trans.operation)
                    rule_string = " + ".join(rule_parts)
                    transformed_value = apply_transformations(raw_value, rule_string)
                else:
                    transformed_value = raw_value
                
                transformed_data[field_name] = transformed_value

            # Validate
            validation_errors = {}
            for field_name, value in transformed_data.items():
                validation_rules = self.template_mapper.get_validation_rules(
                    template=self.template,
                    field_name=field_name,
                )
                
                for rule in validation_rules:
                    error = validate_field(
                        value=value,
                        rule_name=rule.rule,
                        **rule.args,
                    )
                    if error:
                        if field_name not in validation_errors:
                            validation_errors[field_name] = []
                        validation_errors[field_name].append(error)

            is_valid = len(validation_errors) == 0

            # Cache result
            completeness_records.append({
                "job_id": self.job_id,
                "run_type": "EXPORT",
                "saas_edge_id": self.config.saas_edge_id,
                "product_id": product.get("product_id"),
                "template_id": self.config.template_id,
                "transformed_response": transformed_data,
                "validation_errors": validation_errors,
                "is_valid": is_valid,
                "error_count": len(validation_errors),
                "raw_input_snapshot": product,
            })

            transformed_products.append(transformed_data)

        # Write to cache
        if completeness_records:
            await self.completeness_writer.write_batch(completeness_records)

        await self.job_manager.update_status(
            job_id=self.job_id,
            status="EXPORT_WRITE_CACHE",
        )

        return transformed_products

    async def _build_file(self, data: List[Dict[str, Any]]) -> str:
        """Stage 7: Build output file."""
        await self.job_manager.update_status(
            job_id=self.job_id,
            status="EXPORT_BUILD_FILE",
        )

        logger.info(f"Building {self.config.file_format} file: {self.config.output_path}")

        output_file = FileBuilderFactory.build_file(
            data=data,
            output_path=self.config.output_path,
            file_format=self.config.file_format,
            config=self.config.file_config,
        )

        await self.job_manager.complete_step(
            job_id=self.job_id,
            step_name="build_file",
            metrics={
                "output_path": output_file,
                "row_count": len(data),
            },
        )

        return output_file

    async def _upload_file(self, file_path: str) -> None:
        """Stage 8: Upload file to destination (optional)."""
        await self.job_manager.update_status(
            job_id=self.job_id,
            status="EXPORT_UPLOAD_FILE",
        )

        # In production, this would upload to GCS/S3/channel API
        # For now, file is already at output_path
        logger.info(f"File ready at {file_path}")

        await self.job_manager.complete_step(
            job_id=self.job_id,
            step_name="upload_file",
            metrics={"upload_path": file_path},
        )


async def run_product_export(config: ExportPipelineConfig) -> Dict[str, Any]:
    """
    Convenience function to run export pipeline.
    
    Args:
        config: Export configuration
        
    Returns:
        Job results
    """
    pipeline = ExportPipeline(config)
    return await pipeline.run()
