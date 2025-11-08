"""Response formatting utilities for diagram generation results."""

import json
from typing import Any, Dict, List, Optional


def format_json(data: Dict[str, Any]) -> str:
    """Format response as clean JSON."""
    return json.dumps(data, indent=2, default=str)


def format_diagram_result(
    file_paths: List[str],
    metadata: Dict[str, Any],
    base64_images: Optional[Dict[str, str]] = None,
) -> str:
    """Format diagram generation result.

    Args:
        file_paths: List of paths to generated diagram files
        metadata: Diagram metadata (node count, generation time, etc.)
        base64_images: Optional dict of format → base64-encoded image

    Returns:
        JSON-formatted result string
    """
    result = {
        "file_paths": file_paths,
        "metadata": metadata,
    }

    if base64_images:
        result["base64_images"] = base64_images

    return format_json(result)


def format_validation_result(
    valid: bool,
    errors: List[str],
    warnings: List[str],
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Format diagram validation result.

    Args:
        valid: Whether the diagram specification is valid
        errors: List of validation errors
        warnings: List of validation warnings
        metadata: Optional metadata (node count, edge count, etc.)

    Returns:
        JSON-formatted validation result
    """
    result = {
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
    }

    if metadata:
        result["metadata"] = metadata

    return format_json(result)


def format_node_catalog(
    nodes: List[Dict[str, Any]],
    total_count: int,
    returned_count: int,
) -> str:
    """Format node catalog listing.

    Args:
        nodes: List of node information dicts
        total_count: Total number of nodes matching filter
        returned_count: Number of nodes in response

    Returns:
        JSON-formatted node catalog
    """
    result = {
        "nodes": nodes,
        "total_count": total_count,
        "returned_count": returned_count,
    }

    return format_json(result)


def format_error(error_message: str, suggestion: Optional[str] = None) -> str:
    """Format actionable error messages.

    Args:
        error_message: Error description
        suggestion: Optional suggestion for fixing the error

    Returns:
        JSON-formatted error
    """
    error_data = {"error": error_message}
    if suggestion:
        error_data["suggestion"] = suggestion
    return format_json(error_data)
