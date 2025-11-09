"""Diagrams MCP - generate infrastructure diagrams as code."""

from fastmcp import FastMCP

# Version
__version__ = "1.0.0"


# Create MCP server instance
mcp = FastMCP(
    "diagrams-mcp",
    version=__version__,
    instructions="""Generate infrastructure and architecture diagrams as code using the Python diagrams library.

**Capabilities:**
• 15+ cloud providers (AWS, Azure, GCP, K8s, on-prem, generic, SaaS, programming)
• 500+ node types (compute, database, network, storage, analytics, ML, security)
• Custom icons from HTTPS URLs or local files
• Cluster grouping with unlimited nesting
• Multiple output formats (PNG, PDF, JPG, DOT)
• Flowchart creation with 24 shapes

**Use for:**
• Infrastructure architecture diagrams
• System design documentation
• Cloud resource visualisation
• Flowcharts and process diagrams""",
)


# ============================================================================
# MCP Resources - Server Documentation
# ============================================================================


@mcp.resource("docs://quick-start")
def quick_start_guide() -> str:
    """Quick start guide for common diagram patterns."""
    return """Quick Start Guide

BASIC AWS 3-TIER ARCHITECTURE

{
  "name": "AWS 3-Tier Web Application",
  "nodes": [
    {"id": "r53", "provider": "aws", "category": "network", "type": "Route53", "label": "DNS"},
    {"id": "elb", "provider": "aws", "category": "network", "type": "ELB", "label": "Load Balancer"},
    {"id": "ec2_1", "provider": "aws", "category": "compute", "type": "EC2", "label": "Web Server 1"},
    {"id": "ec2_2", "provider": "aws", "category": "compute", "type": "EC2", "label": "Web Server 2"},
    {"id": "rds", "provider": "aws", "category": "database", "type": "RDS", "label": "Database"}
  ],
  "connections": [
    {"from_node": "r53", "to_node": "elb"},
    {"from_node": "elb", "to_node": ["ec2_1", "ec2_2"]},
    {"from_node": "ec2_1", "to_node": "rds"},
    {"from_node": "ec2_2", "to_node": "rds"}
  ],
  "direction": "LR",
  "output_format": ["png", "pdf"]
}

OUTPUT CONTROL

{
  "name": "My Architecture",
  "nodes": [...],
  "connections": [...],
  "output_dir": "./diagrams",        // Relative path (auto-created)
  "output_format": "png"
}

// Absolute path example:
"output_dir": "/Users/username/my-diagrams"

// Default (omit output_dir): saves to current directory

WITH CLUSTERS (VPC GROUPING)

{
  "name": "AWS VPC Architecture",
  "nodes": [...],
  "connections": [...],
  "clusters": [
    {
      "name": "VPC",
      "node_ids": ["elb", "ec2_1", "ec2_2", "rds"],
      "graph_attr": {"bgcolor": "#E5F5FD"}
    }
  ]
}

KUBERNETES MICROSERVICES

{
  "name": "K8s Microservices",
  "nodes": [
    {"id": "ing", "provider": "k8s", "category": "network", "type": "Ingress", "label": "Ingress"},
    {"id": "svc_a", "provider": "k8s", "category": "network", "type": "Service", "label": "Service A"},
    {"id": "pod_a1", "provider": "k8s", "category": "compute", "type": "Pod", "label": "Pod A-1"},
    {"id": "pod_a2", "provider": "k8s", "category": "compute", "type": "Pod", "label": "Pod A-2"},
    {"id": "pvc", "provider": "k8s", "category": "storage", "type": "PersistentVolumeClaim", "label": "Storage"}
  ],
  "connections": [
    {"from_node": "ing", "to_node": "svc_a"},
    {"from_node": "svc_a", "to_node": ["pod_a1", "pod_a2"]},
    {"from_node": "pod_a1", "to_node": "pvc"},
    {"from_node": "pod_a2", "to_node": "pvc"}
  ]
}

CUSTOM ICONS ⭐

{
  "custom_nodes": [
    {
      "id": "logo",
      "label": "My App",
      "icon_source": "url",
      "icon_path": "https://example.com/logo.png",
      "cache_icons": true
    },
    {
      "id": "local_icon",
      "label": "Custom Service",
      "icon_source": "local",
      "icon_path": "/path/to/icon.png"
    }
  ],
  "connections": [
    {"from_node": "logo", "to_node": "local_icon"}
  ]
}

FLOWCHART

{
  "name": "Deployment Process",
  "steps": [
    {"id": "start", "shape": "StartEnd", "label": "Start"},
    {"id": "build", "shape": "Process", "label": "Build Code"},
    {"id": "test", "shape": "Decision", "label": "Tests Pass?"},
    {"id": "deploy", "shape": "Process", "label": "Deploy"},
    {"id": "end", "shape": "StartEnd", "label": "End"}
  ],
  "flows": [
    {"from_step": "start", "to_step": "build"},
    {"from_step": "build", "to_step": "test"},
    {"from_step": "test", "to_step": "deploy", "label": "Yes"},
    {"from_step": "test", "to_step": "build", "label": "No"},
    {"from_step": "deploy", "to_step": "end"}
  ]
}

OUTPUT FORMATS
- png: Default raster format
- pdf: Vector format for documents
- jpg: Compressed raster
- dot: Graphviz source code
"""


@mcp.resource("docs://custom-icons")
def custom_icons_guide() -> str:
    """Comprehensive guide for using custom icons."""
    return """Custom Icons Guide ⭐

OVERVIEW
Custom icons allow you to use your own images for nodes instead of the built-in provider icons.
Supports both web URLs (https://) and local file paths.

WEB URLS (Recommended for shared diagrams)

{
  "custom_nodes": [
    {
      "id": "app",
      "label": "My Application",
      "icon_source": "url",
      "icon_path": "https://example.com/images/app-logo.png",
      "cache_icons": true
    }
  ],
  "connections": [...]
}

Features:
- Automatic downloading and caching
- HTTPS-only for security
- 5MB file size limit
- Formats: PNG, JPG
- 5-second download timeout

Cache location: ~/.diagrams_mcp/icon_cache

LOCAL FILES (For private/proprietary icons)

{
  "custom_nodes": [
    {
      "id": "internal_service",
      "label": "Internal API",
      "icon_source": "local",
      "icon_path": "/Users/username/icons/service.png"
    }
  ],
  "connections": [...]
}

Requirements:
- Absolute or relative file paths
- File must exist and be readable
- Formats: PNG, JPG
- Validated before diagram generation

MIXING STANDARD AND CUSTOM NODES

{
  "nodes": [
    {"id": "s3", "provider": "aws", "category": "storage", "type": "S3", "label": "Storage"},
    {"id": "lambda", "provider": "aws", "category": "compute", "type": "Lambda", "label": "Function"}
  ],
  "custom_nodes": [
    {
      "id": "custom_app",
      "label": "Custom App",
      "icon_source": "url",
      "icon_path": "https://example.com/app.png"
    }
  ],
  "connections": [
    {"from_node": "s3", "to_node": "custom_app"},
    {"from_node": "custom_app", "to_node": "lambda"}
  ]
}

BEST PRACTICES
1. Use square icons (1:1 aspect ratio) for consistency
2. Recommended size: 256x256 pixels
3. PNG with transparency works best
4. Cache icons when using the same URL multiple times
5. Use descriptive IDs for custom nodes

ERROR HANDLING
- Invalid URL → Clear error with suggestion
- Download failure → Detailed error message
- File not found → Path validation error
- Invalid format → Supported formats listed
- Too large → Size limit specified

SECURITY
- HTTPS-only URLs (HTTP rejected)
- File size limits (5MB)
- Image format validation
- No arbitrary code execution
- Download timeout protection
"""


@mcp.resource("tools://available")
def available_tools() -> str:
    """List all available diagram generation tools."""
    return """Available Diagram Tools (5)

PRIMARY TOOL
create_diagram: Generate infrastructure/architecture diagrams with full control
  - Supports all 15+ providers (AWS, Azure, GCP, K8s, on-prem, etc.)
  - 500+ node types across all categories
  - Connections with styling (labels, colours, line styles)
  - Clusters for logical grouping (unlimited nesting)
  - Multiple output formats (PNG, PDF, JPG, DOT)
  - Custom Graphviz attributes for advanced styling

CUSTOM ICONS ⭐
create_diagram_with_custom_icons: Create diagrams with custom node icons
  - Load icons from HTTPS URLs (automatic caching)
  - Use local file paths for proprietary icons
  - Mix custom icons with standard provider nodes
  - Full validation and security checks

DISCOVERY
list_available_nodes: Search and discover available node types
  - Filter by provider (aws, azure, gcp, etc.)
  - Filter by category (compute, database, network, etc.)
  - Search by keyword
  - Returns import paths for each node

SIMPLIFIED FLOWCHARTS
create_flowchart: Quick flowchart creation without cloud-specific nodes
  - 24 flowchart shapes (StartEnd, Process, Decision, Data, etc.)
  - Decision tree support with conditional labels
  - Simpler API than full create_diagram

VALIDATION
validate_diagram_spec: Validate diagram before generation (dry-run)
  - Check node references are valid
  - Detect missing connections
  - Validate cluster memberships
  - Returns actionable errors and warnings

See docs://quick-start for examples
See docs://custom-icons for custom icon guide ⭐
"""


# Import and register all tools (must be after mcp instance creation for decorators)
from .tools import core  # noqa: E402

# Explicitly declare as part of module interface
__all__ = ["mcp", "core"]


def main():
    """Entry point for uvx."""
    mcp.run()


if __name__ == "__main__":
    main()
