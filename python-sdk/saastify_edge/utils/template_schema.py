"""
Template Schema Utilities

Functions for generating and managing JSON schemas from template attributes.
"""

from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger(__name__)


def generate_json_schema(template_attrs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate JSON Schema dynamically from template attributes, including hierarchy support.
    Also generates the order array based on column_pos or alphabetic order.
    
    Args:
        template_attrs: List of template attribute dictionaries from database
        
    Returns:
        JSON schema dictionary
    """
    try:
        # Base schema
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {},
            "required": [],
            "order": [],
        }

        # Helper to handle hierarchical properties
        def add_property(
            properties: Dict[str, Any],
            attr: Dict[str, Any],
            parent_property: Optional[str] = None,
        ):
            column_name = attr["column_name"]
            data_type = (attr.get("data_type") or "text").lower()
            data_type_format = attr.get("data_type_format")

            # Map data_type to JSON schema types
            json_type_mapping = {
                "text": "string",
                "number": "number",
                "integer": "integer",
                "boolean": "boolean",
                "array": "array",
                "object": "object",
                "decimal": "number",
                "timestamp": "string",
                "url": "string",
                "date": "string",
                "datetime": "string",
                "time": "string",
            }
            field_type = json_type_mapping.get(data_type, "string")

            # Define the property schema
            property_schema = {
                "title": attr.get("custom_title", column_name),
                "type": field_type,
                "description": attr.get("description", f"Field for {column_name}"),
                "default": attr.get("default_value"),
                "nullable": attr.get("is_nullable", True),
            }

            # Handle data_type_format if available
            if data_type_format:
                property_schema["format"] = data_type_format

            # Handle multi-valued fields (array)
            if attr.get("accepts_multiple_values", False):
                property_schema = {
                    "type": "array",
                    "items": {"type": field_type},
                    "description": f"Array of {data_type} values for {column_name}",
                }

            # Add validation rules
            validation_rules = attr.get("validation_rules", {})
            if validation_rules:
                if isinstance(validation_rules, str):
                    try:
                        validation_rules = json.loads(validation_rules)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in validation_rules for {column_name}")
                        validation_rules = {}
                
                if "minLength" in validation_rules:
                    property_schema["minLength"] = validation_rules["minLength"]
                if "maxLength" in validation_rules:
                    property_schema["maxLength"] = validation_rules["maxLength"]
                if "pattern" in validation_rules:
                    property_schema["pattern"] = validation_rules["pattern"]
                if "enum" in validation_rules:
                    property_schema["enum"] = validation_rules["enum"]

            # Add to the appropriate place in the properties structure
            if parent_property:
                if "properties" not in properties[parent_property]:
                    properties[parent_property]["properties"] = {}
                properties[parent_property]["properties"][column_name] = property_schema
            else:
                properties[column_name] = property_schema

            # Add to required list if mandatory
            if attr.get("mandatory", False):
                if parent_property:
                    if "required" not in properties[parent_property]:
                        properties[parent_property]["required"] = []
                    properties[parent_property]["required"].append(column_name)
                else:
                    schema["required"].append(column_name)

            # Add to order list
            if not parent_property:
                schema["order"].append(column_name)

        # Process attributes considering hierarchy
        for attr in template_attrs:
            parent_id = attr.get("parent_id")
            if parent_id:
                # Find the parent property in existing attributes
                parent_attr = next(
                    (a for a in template_attrs if a.get("template_attr_id") == parent_id),
                    None,
                )
                if parent_attr:
                    add_property(schema["properties"], attr, parent_attr["column_name"])
            else:
                add_property(schema["properties"], attr)

        return schema

    except Exception as e:
        logger.error(f"Error generating JSON schema: {e}")
        raise


async def get_or_generate_template_schema(
    db_client: Any,
    saas_edge_id: str,
    template_id: str
) -> Dict[str, Any]:
    """
    Get existing schema from database or generate and save new one.
    
    Args:
        db_client: Database client
        saas_edge_id: Tenant identifier
        template_id: Template identifier
        
    Returns:
        JSON schema dictionary
    """
    # Check if schema exists
    existing_schema = await db_client.query_one(
        "saas_template_schema",
        {
            "saas_edge_id": saas_edge_id,
            "template_id": template_id
        },
        fields=["schema"]
    )
    
    if existing_schema and existing_schema.get("schema"):
        logger.info(f"Schema found in database for template {template_id}")
        schema = existing_schema["schema"]
        if isinstance(schema, str):
            schema = json.loads(schema)
        return schema
    
    # Generate new schema
    logger.info(f"No schema found. Generating schema for template {template_id}")
    
    # Fetch template attributes
    template_attrs = await db_client.query_many(
        "saas_channel_attr_template",
        {
            "saas_edge_id": saas_edge_id,
            "template_id": template_id
        },
        order_by="column_pos ASC NULLS LAST, column_name ASC"
    )
    
    if not template_attrs:
        raise ValueError(
            f"No attributes found for saas_edge_id: {saas_edge_id} and template_id: {template_id}"
        )
    
    # Generate schema
    generated_schema = generate_json_schema(template_attrs)
    
    # Save to database
    schema_json = json.dumps(generated_schema)
    await db_client.insert(
        "saas_template_schema",
        {
            "saas_edge_id": saas_edge_id,
            "template_id": template_id,
            "schema": schema_json
        },
        on_conflict="(saas_edge_id, template_id) DO UPDATE SET schema = EXCLUDED.schema, updated_at = CURRENT_TIMESTAMP"
    )
    
    logger.info(f"Schema generated and saved for template {template_id}")
    return generated_schema

