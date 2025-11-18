"""
Template Mapper - Load and map templates to transform/validate product data.

Handles:
- Loading channel templates (from mock data or external API)
- Column-to-field mapping
- Transformation pipeline configuration
- Validation rule configuration
"""

from typing import Dict, List, Any, Optional
from ..core.types import (
    ChannelTemplate,
    AttributeDefinition,
    TransformationStep,
    ValidationRule,
)


class TemplateMapper:
    """Maps raw data columns to template fields with transformation/validation configs."""

    def __init__(self, db_client: Optional[Any] = None):
        """
        Initialize template mapper.
        
        Args:
            db_client: Database client for fetching templates (optional for testing)
        """
        self.db_client = db_client
        self._template_cache: Dict[str, ChannelTemplate] = {}

    async def load_template(self, template_id: str, saas_edge_id: str) -> ChannelTemplate:
        """
        Load channel template by ID.
        
        Args:
            template_id: UUID of the template
            saas_edge_id: Tenant ID for isolation
            
        Returns:
            ChannelTemplate with attributes, transformations, validations
            
        Raises:
            ValueError: If template not found
        """
        cache_key = f"{saas_edge_id}:{template_id}"
        
        # Check cache first
        if cache_key in self._template_cache:
            return self._template_cache[cache_key]
        
        # Load from database (mock implementation for now)
        if self.db_client:
            template_data = await self._fetch_from_db(template_id, saas_edge_id)
        else:
            template_data = self._get_mock_template(template_id)
        
        if not template_data:
            raise ValueError(f"Template {template_id} not found for tenant {saas_edge_id}")
        
        # Parse and cache
        template = self._parse_template(template_data)
        self._template_cache[cache_key] = template
        
        return template

    async def _fetch_from_db(self, template_id: str, saas_edge_id: str) -> Dict[str, Any]:
        """Fetch template from database via GraphQL/SQL."""
        # Placeholder for actual GraphQL query
        # In production, this would call:
        # query = '''
        #   query GetTemplate($templateId: uuid!, $edgeId: uuid!) {
        #     channel_templates(where: {
        #       id: {_eq: $templateId},
        #       saas_edge_id: {_eq: $edgeId}
        #     }) {
        #       id
        #       channel_name
        #       template_name
        #       attributes
        #     }
        #   }
        # '''
        raise NotImplementedError("Database client integration pending")

    def _get_mock_template(self, template_id: str) -> Dict[str, Any]:
        """Return mock template for testing."""
        return {
            "id": template_id,
            "channel_name": "amazon",
            "template_name": "Amazon Standard Product",
            "attributes": [
                {
                    "name": "title",
                    "column_name": "product_title",
                    "data_type": "string",
                    "is_required": True,
                    "transformations": [
                        {"operation": "strip", "args": {}},
                        {"operation": "title_case", "args": {}},
                    ],
                    "validations": [
                        {"rule": "required", "args": {}},
                        {"rule": "max_length", "args": {"max": 200}},
                    ],
                },
                {
                    "name": "price",
                    "column_name": "selling_price",
                    "data_type": "number",
                    "is_required": True,
                    "transformations": [
                        {"operation": "clean_numeric_value", "args": {}},
                    ],
                    "validations": [
                        {"rule": "required", "args": {}},
                        {"rule": "numeric_range", "args": {"min": 0.01, "max": 999999}},
                    ],
                },
                {
                    "name": "quantity",
                    "column_name": "stock_qty",
                    "data_type": "integer",
                    "is_required": True,
                    "transformations": [
                        {"operation": "clean_numeric_value", "args": {}},
                    ],
                    "validations": [
                        {"rule": "required", "args": {}},
                        {"rule": "numeric_range", "args": {"min": 0, "max": 100000}},
                    ],
                },
                {
                    "name": "sku",
                    "column_name": "product_sku",
                    "data_type": "string",
                    "is_required": True,
                    "transformations": [
                        {"operation": "strip", "args": {}},
                        {"operation": "uppercase", "args": {}},
                    ],
                    "validations": [
                        {"rule": "required", "args": {}},
                        {"rule": "max_length", "args": {"max": 50}},
                    ],
                },
                {
                    "name": "description",
                    "column_name": "product_description",
                    "data_type": "string",
                    "is_required": False,
                    "transformations": [
                        {"operation": "strip", "args": {}},
                        {"operation": "clean_html", "args": {}},
                    ],
                    "validations": [
                        {"rule": "max_length", "args": {"max": 2000}},
                    ],
                },
            ],
        }

    def _parse_template(self, template_data: Dict[str, Any]) -> ChannelTemplate:
        """Parse raw template data into ChannelTemplate object."""
        attributes = []
        
        for attr_data in template_data.get("attributes", []):
            # Parse transformations
            transformations: List[TransformationStep] = [
                TransformationStep(
                    operation=t["operation"],
                    args=t.get("args", {}),
                )
                for t in attr_data.get("transformations", [])
            ]
            
            # Parse validations
            validations: List[ValidationRule] = [
                ValidationRule(
                    rule=v["rule"],
                    args=v.get("args", {}),
                    error_message=v.get("error_message"),
                )
                for v in attr_data.get("validations", [])
            ]
            
            # Create attribute definition
            attribute = AttributeDefinition(
                name=attr_data["name"],
                column_name=attr_data.get("column_name", attr_data["name"]),
                data_type=attr_data.get("data_type", "string"),
                is_required=attr_data.get("is_required", False),
                transformations=transformations,
                validations=validations,
            )
            attributes.append(attribute)
        
        return ChannelTemplate(
            id=template_data["id"],
            channel_name=template_data["channel_name"],
            template_name=template_data["template_name"],
            attributes=attributes,
        )

    def map_row_to_fields(
        self,
        raw_row: Dict[str, Any],
        template: ChannelTemplate,
    ) -> Dict[str, Any]:
        """
        Map raw CSV/file columns to template field names.
        
        Args:
            raw_row: Raw row data from file (column_name -> value)
            template: Channel template with attribute definitions
            
        Returns:
            Mapped field data (attribute_name -> raw_value)
        """
        mapped_data = {}
        
        for attribute in template.attributes:
            column_name = attribute.column_name
            field_name = attribute.name
            
            # Get value from raw row (case-insensitive match)
            raw_value = None
            for col_key, col_value in raw_row.items():
                if col_key.lower() == column_name.lower():
                    raw_value = col_value
                    break
            
            mapped_data[field_name] = raw_value
        
        return mapped_data

    def get_transformation_pipeline(
        self,
        template: ChannelTemplate,
        field_name: str,
    ) -> List[TransformationStep]:
        """Get transformation pipeline for a specific field."""
        for attribute in template.attributes:
            if attribute.name == field_name:
                return attribute.transformations
        return []

    def get_validation_rules(
        self,
        template: ChannelTemplate,
        field_name: str,
    ) -> List[ValidationRule]:
        """Get validation rules for a specific field."""
        for attribute in template.attributes:
            if attribute.name == field_name:
                return attribute.validations
        return []

    def get_required_fields(self, template: ChannelTemplate) -> List[str]:
        """Get list of required field names."""
        return [attr.name for attr in template.attributes if attr.is_required]

    def get_all_field_names(self, template: ChannelTemplate) -> List[str]:
        """Get list of all field names in template."""
        return [attr.name for attr in template.attributes]

    def clear_cache(self) -> None:
        """Clear template cache (useful for testing or cache invalidation)."""
        self._template_cache.clear()
