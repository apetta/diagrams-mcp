"""Pydantic models for diagram validation."""

import re
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Node Definitions
# ============================================================================


class NodeDef(BaseModel):
    """Definition of a diagram node."""

    id: str = Field(
        description="Unique node ID (used in connections)",
        min_length=1,
        max_length=200,
    )
    provider: str = Field(
        description="Provider - MUST be exact: aws, azure, gcp, k8s, onprem, generic, saas, etc.",
        min_length=1,
    )
    category: str = Field(
        description="Category - MUST exist for provider: compute, database, network, storage, etc.",
        min_length=1,
    )
    type: str = Field(
        description="Node type - MUST match class in diagrams.{provider}.{category}: EC2, RDS, Lambda, etc.",
        min_length=1,
    )
    label: str = Field(
        description="Display label",
        min_length=1,
    )

    @field_validator("id")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Validate ID contains only alphanumeric + underscore + hyphen."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                f"Invalid node ID '{v}': only alphanumeric characters, "
                "underscores, and hyphens allowed"
            )
        return v


class CustomNodeDef(BaseModel):
    """Definition of a custom node with icon from URL or local file."""

    id: str = Field(
        description="Unique node ID",
        min_length=1,
        max_length=200,
    )
    label: str = Field(
        description="Display label",
        min_length=1,
    )
    icon_source: Literal["url", "local"] = Field(description="Icon from web URL or local file")
    icon_path: str = Field(
        description="HTTPS URL or local file path",
        min_length=1,
    )
    cache_icons: bool = Field(
        default=True,
        description="Cache downloaded icons",
    )

    @field_validator("id")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Validate ID format."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                f"Invalid node ID '{v}': only alphanumeric characters, "
                "underscores, and hyphens allowed"
            )
        return v

    @field_validator("icon_path")
    @classmethod
    def validate_icon_path(cls, v: str, info) -> str:
        """Validate icon path format based on source type."""
        icon_source = info.data.get("icon_source")

        if icon_source == "url":
            if not v.startswith("https://"):
                raise ValueError(f"Icon URL must start with 'https://', got: {v}")
        # For local paths, we'll validate existence at runtime

        return v


# ============================================================================
# Connection/Edge Definitions
# ============================================================================


class ConnectionDef(BaseModel):
    """Definition of a connection between nodes."""

    from_node: str = Field(
        description="Source node ID",
        min_length=1,
    )
    to_node: str | List[str] = Field(
        description="Target node ID(s)",
    )
    direction: Literal["forward", "reverse", "bidirectional"] = Field(
        default="forward",
        description="Direction (forward: >>, reverse: <<, bidirectional: -)",
    )
    label: Optional[str] = Field(
        default=None,
        description="Connection label",
    )
    color: Optional[str] = Field(
        default=None,
        description="Colour (name or hex, e.g. 'red', '#FF0000')",
    )
    style: Optional[Literal["solid", "dashed", "dotted", "bold"]] = Field(
        default=None,
        description="Edge style",
    )


# ============================================================================
# Cluster Definitions
# ============================================================================


class ClusterDef(BaseModel):
    """Definition of a cluster (logical grouping of nodes)."""

    name: str = Field(
        description="Cluster name",
        min_length=1,
    )
    node_ids: List[str] = Field(
        description="Node IDs in this cluster",
        min_length=1,
    )
    graph_attr: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Graphviz attributes (bgcolor, pencolor...)",
    )
    parent_cluster: Optional[str] = Field(
        default=None,
        description="Parent cluster for nesting",
    )


# ============================================================================
# Flowchart Definitions
# ============================================================================


class FlowStepDef(BaseModel):
    """Definition of a flowchart step."""

    id: str = Field(
        description="Unique step ID",
        min_length=1,
        max_length=200,
    )
    shape: str = Field(
        description="Shape (StartEnd, Process, Decision, Data...)",
        min_length=1,
    )
    label: str = Field(
        description="Display label",
        min_length=1,
    )

    @field_validator("id")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Validate ID format."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                f"Invalid step ID '{v}': only alphanumeric characters, "
                "underscores, and hyphens allowed"
            )
        return v


class FlowConnectionDef(BaseModel):
    """Definition of a flowchart connection."""

    from_step: str = Field(
        description="Source step ID",
        min_length=1,
    )
    to_step: str | List[str] = Field(
        description="Target step ID(s)",
    )
    label: Optional[str] = Field(
        default=None,
        description="Label (e.g. 'Yes', 'No')",
    )
    condition: Optional[str] = Field(
        default=None,
        description="Condition description",
    )


# ============================================================================
# Diagram Configuration
# ============================================================================


class DiagramConfig(BaseModel):
    """Configuration for diagram generation."""

    name: str = Field(
        default="",
        description="Diagram title",
    )
    filename: Optional[str] = Field(
        default=None,
        description="Output filename (auto-generated if omitted)",
    )
    direction: Literal["LR", "RL", "TB", "BT"] = Field(
        default="LR",
        description="Layout direction (LR, TB, etc.)",
    )
    curvestyle: Literal["ortho", "curved"] = Field(
        default="ortho",
        description="Edge style (ortho=straight, curved)",
    )
    output_format: str | List[str] = Field(
        default="png",
        description="Output format(s): png, pdf, jpg, dot",
    )
    output_dir: Optional[str] = Field(
        default=None,
        description="Output directory (default: current directory). Relative (./diagrams) or absolute (/path/to/output). Auto-created if missing.",
    )
    graph_attr: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Graphviz graph attributes",
    )
    node_attr: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Default node attributes",
    )
    edge_attr: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Default edge attributes",
    )
    autolabel: bool = Field(
        default=False,
        description="Auto-prefix nodes with class names",
    )
    show: bool = Field(
        default=False,
        description="Auto-open file (disabled for MCP)",
    )
    return_base64: bool = Field(
        default=False,
        description="Include base64-encoded images",
    )

    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, v: str | List[str]) -> str | List[str]:
        """Validate output format is supported."""
        valid_formats = {"png", "pdf", "jpg", "dot"}

        formats = [v] if isinstance(v, str) else v

        for fmt in formats:
            if fmt not in valid_formats:
                raise ValueError(
                    f"Invalid output format '{fmt}'. "
                    f"Valid formats: {', '.join(sorted(valid_formats))}"
                )

        return v
