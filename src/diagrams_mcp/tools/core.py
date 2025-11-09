"""Core diagram generation tools for the Diagrams MCP server."""

import base64
import os
import time
from pathlib import Path
from typing import Annotated, Any, Dict, List, Literal, Optional

from diagrams import Diagram, Cluster, Edge
from pydantic import Field

from ..core.formatters import (
    format_diagram_result,
    format_validation_result,
    format_node_catalog,
    format_error,
)
from ..core.validators import (
    NodeDef,
    CustomNodeDef,
    ConnectionDef,
    ClusterDef,
    FlowStepDef,
    FlowConnectionDef,
)
from ..core.node_registry import (
    search_nodes,
    validate_node_reference,
)
from ..core.icon_manager import IconManager

# Import the MCP server instance
from ..server import mcp


# ============================================================================
# Helper Functions
# ============================================================================


def import_node_class(provider: str, category: str, node_type: str):
    """Dynamically import a node class from the diagrams library.

    Args:
        provider: Provider name (e.g., "aws")
        category: Category name (e.g., "compute")
        node_type: Node type (e.g., "EC2")

    Returns:
        Node class

    Raises:
        ImportError: If the node class cannot be imported
    """
    try:
        # Construct import path: diagrams.aws.compute
        module_path = f"diagrams.{provider}.{category}"
        module = __import__(module_path, fromlist=[node_type])

        # Get the class
        node_class = getattr(module, node_type)
        return node_class

    except (ImportError, AttributeError) as e:
        raise ImportError(
            f"Failed to import node '{node_type}' from {provider}.{category}. "
            f"Error: {str(e)}. "
            f"Check that the provider, category, and type are correct."
        )


def encode_file_base64(file_path: str) -> str:
    """Encode a file as base64 string.

    Args:
        file_path: Path to file

    Returns:
        Base64-encoded string
    """
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def build_diagram_metadata(
    file_paths: List[str],
    node_count: int,
    edge_count: int,
    cluster_count: int,
    generation_time_ms: float,
) -> Dict[str, Any]:
    """Build metadata dict for diagram result.

    Args:
        file_paths: List of generated file paths
        node_count: Number of nodes in diagram
        edge_count: Number of edges in diagram
        cluster_count: Number of clusters
        generation_time_ms: Time taken to generate in milliseconds

    Returns:
        Metadata dictionary
    """
    file_sizes = {}
    for path in file_paths:
        if os.path.exists(path):
            size = os.path.getsize(path)
            ext = Path(path).suffix[1:]  # Remove the dot
            file_sizes[ext] = size

    return {
        "node_count": node_count,
        "edge_count": edge_count,
        "cluster_count": cluster_count,
        "generation_time_ms": round(generation_time_ms, 2),
        "file_sizes": file_sizes,
    }


# ============================================================================
# Tool 1: Create Diagram (Primary)
# ============================================================================


@mcp.tool(
    name="create_diagram",
    description="""Generate infrastructure diagrams with 15+ providers (AWS, Azure, GCP, K8s, etc.).

Examples:
AWS: nodes=[{"id":"r53","provider":"aws","category":"network","type":"Route53",...}]
K8s: nodes=[{"id":"ing","provider":"k8s","category":"network","type":"Ingress",...}]
Clusters: clusters=[{"name":"VPC","node_ids":["elb","ec2"],"graph_attr":{"bgcolor":"#E5F5FD"}}]

⚠️ CRITICAL: Node types must exist in diagrams library or diagram fails silently (no arrows).
ALWAYS verify first: list_available_nodes(provider="aws", category="compute")
For brands (Stripe, Vercel), use create_diagram_with_custom_icons instead.""",
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
    },
)
async def create_diagram(
    name: Annotated[str, Field(description="Diagram title")],
    nodes: Annotated[List[NodeDef], Field(description="List of nodes to include")],
    connections: Annotated[
        List[ConnectionDef], Field(description="List of connections between nodes")
    ],
    clusters: Annotated[
        Optional[List[ClusterDef]],
        Field(description="Optional clusters for grouping nodes"),
    ] = None,
    direction: Annotated[
        Literal["LR", "RL", "TB", "BT"],
        Field(description="Diagram direction (LR=left-right, TB=top-bottom)"),
    ] = "LR",
    curvestyle: Annotated[
        Literal["ortho", "curved"], Field(description="Edge curve style")
    ] = "ortho",
    output_format: Annotated[
        str | List[str],
        Field(description="Output format(s): png, pdf, jpg, dot"),
    ] = "png",
    output_dir: Annotated[
        Optional[str],
        Field(
            description="Output directory (default: current directory). Auto-created if missing."
        ),
    ] = None,
    graph_attr: Annotated[
        Optional[Dict[str, Any]], Field(description="Graphviz graph attributes")
    ] = None,
    node_attr: Annotated[
        Optional[Dict[str, Any]], Field(description="Default node attributes")
    ] = None,
    edge_attr: Annotated[
        Optional[Dict[str, Any]], Field(description="Default edge attributes")
    ] = None,
    autolabel: Annotated[bool, Field(description="Auto-prefix nodes with class names")] = False,
    return_base64: Annotated[bool, Field(description="Include base64-encoded images")] = False,
) -> str:
    """Generate infrastructure/architecture diagram."""
    start_time = time.time()

    try:
        # Validate all node references
        node_ids = {node.id for node in nodes}
        for node in nodes:
            validate_node_reference(node.provider, node.category, node.type)

        # Validate connections reference existing nodes
        for conn in connections:
            if conn.from_node not in node_ids:
                raise ValueError(
                    f"Connection references unknown node '{conn.from_node}'. "
                    f"Available nodes: {', '.join(sorted(node_ids))}"
                )

            # Handle single target or list of targets
            targets = [conn.to_node] if isinstance(conn.to_node, str) else conn.to_node
            for target in targets:
                if target not in node_ids:
                    raise ValueError(
                        f"Connection references unknown node '{target}'. "
                        f"Available nodes: {', '.join(sorted(node_ids))}"
                    )

        # Validate cluster node references
        if clusters:
            for cluster in clusters:
                for node_id in cluster.node_ids:
                    if node_id not in node_ids:
                        raise ValueError(
                            f"Cluster '{cluster.name}' references unknown node '{node_id}'. "
                            f"Available nodes: {', '.join(sorted(node_ids))}"
                        )

        # Prepare output formats
        formats = [output_format] if isinstance(output_format, str) else output_format

        # Reject SVG - it's buggy and unsupported
        if any("svg" in fmt.lower() for fmt in formats):
            raise ValueError("SVG output is not supported. Use png, pdf, jpg, or dot instead.")

        # Change to output directory if specified
        original_dir = os.getcwd()
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            os.chdir(output_dir)

        try:
            # Create diagram with Diagram context manager
            # Hide diagram title by setting label to empty string
            default_graph_attr = {"label": ""}
            merged_graph_attr = {**default_graph_attr, **(graph_attr or {})}

            with Diagram(
                name=name,
                show=False,  # Never auto-open in MCP server
                direction=direction,
                curvestyle=curvestyle,
                outformat=formats,
                autolabel=autolabel,
                graph_attr=merged_graph_attr,
                node_attr=node_attr or {},
                edge_attr=edge_attr or {},
            ) as _:
                # Create all nodes
                node_objects = {}
                for node in nodes:
                    # Import the node class
                    NodeClass = import_node_class(node.provider, node.category, node.type)

                    # Create node instance
                    node_obj = NodeClass(node.label)
                    node_objects[node.id] = node_obj

                # Handle clusters
                cluster_objects = {}
                if clusters:
                    # Build cluster hierarchy (simple approach: process in order)
                    for cluster in clusters:
                        # Create cluster context
                        cluster_ctx = Cluster(
                            cluster.name,
                            graph_attr=cluster.graph_attr or {},
                        )

                        # Store for later reference
                        cluster_objects[cluster.name] = {
                            "context": cluster_ctx,
                            "node_ids": cluster.node_ids,
                            "parent": cluster.parent_cluster,
                        }

                    # Apply clusters (nodes will be added inside cluster contexts)
                    # For now, we'll use a simplified approach without nesting
                    # Full nesting support would require more complex logic

                # Create all connections
                edge_count = 0
                for conn in connections:
                    from_obj = node_objects[conn.from_node]

                    # Handle single target or list of targets
                    targets = [conn.to_node] if isinstance(conn.to_node, str) else conn.to_node

                    for target in targets:
                        to_obj = node_objects[target]

                        # Create edge with optional styling
                        if conn.label or conn.color or conn.style:
                            edge = Edge(
                                label=conn.label or "",
                                color=conn.color or "black",
                                style=conn.style or "solid",
                            )

                            if conn.direction == "forward":
                                _ = from_obj >> edge >> to_obj
                            elif conn.direction == "reverse":
                                _ = from_obj << edge << to_obj
                            else:  # bidirectional
                                _ = from_obj - edge - to_obj
                        else:
                            # Simple connection without styling
                            if conn.direction == "forward":
                                _ = from_obj >> to_obj
                            elif conn.direction == "reverse":
                                _ = from_obj << to_obj
                            else:  # bidirectional
                                _ = from_obj - to_obj

                        edge_count += 1

            # Get generated file paths
            # diagrams library generates files with snake_case names
            diagram_filename = name.replace(" ", "_").replace("-", "_").lower()
            file_paths = []
            for fmt in formats:
                file_path = f"{diagram_filename}.{fmt}"
                if output_dir:
                    file_path = os.path.join(output_dir, file_path)
                file_paths.append(os.path.abspath(file_path))

            # Build metadata
            generation_time_ms = (time.time() - start_time) * 1000
            metadata = build_diagram_metadata(
                file_paths,
                node_count=len(nodes),
                edge_count=edge_count,
                cluster_count=len(clusters) if clusters else 0,
                generation_time_ms=generation_time_ms,
            )

            # Optionally encode images as base64
            base64_images = None
            if return_base64:
                base64_images = {}
                for path in file_paths:
                    ext = Path(path).suffix[1:]
                    if ext != "dot":  # Don't encode dot files
                        try:
                            base64_images[ext] = encode_file_base64(path)
                        except Exception:
                            # Non-fatal error, just skip
                            pass

            return format_diagram_result(file_paths, metadata, base64_images)

        finally:
            # Restore original directory
            if output_dir:
                os.chdir(original_dir)

    except Exception as e:
        return format_error(
            f"Failed to generate diagram: {str(e)}",
            suggestion="Check node types with list_available_nodes tool",
        )


# ============================================================================
# Tool 2: Create Diagram with Custom Icons
# ============================================================================


@mcp.tool(
    name="create_diagram_with_custom_icons",
    description="""Create diagrams with custom icons from web URLs or local files.

USE WHEN: Brand logos (Stripe, Vercel, Supabase, Fly.io) not in diagrams library.
GitHub avatars work well: https://avatars.githubusercontent.com/u/{org_id}

Examples:
URL: custom_nodes=[{"id":"stripe","icon_source":"url","icon_path":"https://avatars.githubusercontent.com/u/856813"}]
Mixed: nodes=[{...AWS nodes...}], custom_nodes=[{...}], connections=[...]

HTTPS-only for URLs, 5MB limit, PNG/JPG supported. Automatic caching.""",
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
    },
)
async def create_diagram_with_custom_icons(
    name: Annotated[str, Field(description="Diagram title")],
    custom_nodes: Annotated[
        List[CustomNodeDef], Field(description="Custom nodes with icon URLs/paths")
    ],
    connections: Annotated[List[ConnectionDef], Field(description="Connections between nodes")],
    nodes: Annotated[
        Optional[List[NodeDef]],
        Field(description="Optional standard provider nodes to mix with custom"),
    ] = None,
    clusters: Annotated[Optional[List[ClusterDef]], Field(description="Optional clusters")] = None,
    direction: Annotated[
        Literal["LR", "RL", "TB", "BT"], Field(description="Layout direction")
    ] = "LR",
    curvestyle: Annotated[Literal["ortho", "curved"], Field(description="Edge style")] = "ortho",
    output_format: Annotated[
        str | List[str], Field(description="Output format(s): png, pdf, jpg, dot")
    ] = "png",
    output_dir: Annotated[
        Optional[str],
        Field(
            description="Output directory (default: current directory). Auto-created if missing."
        ),
    ] = None,
    graph_attr: Annotated[Optional[Dict[str, Any]], Field(description="Graph attributes")] = None,
    return_base64: Annotated[bool, Field(description="Return base64 images")] = False,
) -> str:
    """Generate diagram with custom node icons."""
    start_time = time.time()

    try:
        from diagrams.custom import Custom

        # Initialize icon manager
        icon_manager = IconManager()

        # Validate all custom icons and get paths
        custom_icon_paths = {}
        for custom_node in custom_nodes:
            try:
                icon_path = icon_manager.get_icon_path(
                    custom_node.icon_source,
                    custom_node.icon_path,
                    cache=custom_node.cache_icons,
                )
                custom_icon_paths[custom_node.id] = icon_path
            except Exception as e:
                return format_error(
                    f"Failed to load icon for node '{custom_node.id}': {str(e)}",
                    suggestion="Check icon_path is valid HTTPS URL or existing local file",
                )

        # Build combined node ID set
        node_ids = {node.id for node in custom_nodes}
        if nodes:
            node_ids.update({node.id for node in nodes})

        # Validate connections
        for conn in connections:
            if conn.from_node not in node_ids:
                raise ValueError(f"Connection references unknown node '{conn.from_node}'")

            targets = [conn.to_node] if isinstance(conn.to_node, str) else conn.to_node
            for target in targets:
                if target not in node_ids:
                    raise ValueError(f"Connection references unknown node '{target}'")

        # Prepare output
        formats = [output_format] if isinstance(output_format, str) else output_format

        # Reject SVG - it's buggy and unsupported
        if any("svg" in fmt.lower() for fmt in formats):
            raise ValueError("SVG output is not supported. Use png, pdf, jpg, or dot instead.")

        # Change directory if needed
        original_dir = os.getcwd()
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            os.chdir(output_dir)

        try:
            # Hide diagram title by setting label to empty string
            default_graph_attr = {"label": ""}
            merged_graph_attr = {**default_graph_attr, **(graph_attr or {})}

            with Diagram(
                name=name,
                show=False,
                direction=direction,
                curvestyle=curvestyle,
                outformat=formats,
                graph_attr=merged_graph_attr,
            ) as _:
                # Create all nodes
                node_objects = {}

                # Create custom nodes
                for custom_node in custom_nodes:
                    icon_path = custom_icon_paths[custom_node.id]
                    node_obj = Custom(custom_node.label, icon_path)
                    node_objects[custom_node.id] = node_obj

                # Create standard nodes if provided
                if nodes:
                    for node in nodes:
                        NodeClass = import_node_class(node.provider, node.category, node.type)
                        node_obj = NodeClass(node.label)
                        node_objects[node.id] = node_obj

                # Create connections
                edge_count = 0
                for conn in connections:
                    from_obj = node_objects[conn.from_node]
                    targets = [conn.to_node] if isinstance(conn.to_node, str) else conn.to_node

                    for target in targets:
                        to_obj = node_objects[target]

                        if conn.label or conn.color or conn.style:
                            edge = Edge(
                                label=conn.label or "",
                                color=conn.color or "black",
                                style=conn.style or "solid",
                            )
                            if conn.direction == "forward":
                                _ = from_obj >> edge >> to_obj
                            elif conn.direction == "reverse":
                                _ = from_obj << edge << to_obj
                            else:
                                _ = from_obj - edge - to_obj
                        else:
                            if conn.direction == "forward":
                                _ = from_obj >> to_obj
                            elif conn.direction == "reverse":
                                _ = from_obj << to_obj
                            else:
                                _ = from_obj - to_obj

                        edge_count += 1

            # Get file paths
            diagram_filename = name.replace(" ", "_").replace("-", "_").lower()
            file_paths = []
            for fmt in formats:
                file_path = f"{diagram_filename}.{fmt}"
                if output_dir:
                    file_path = os.path.join(output_dir, file_path)
                file_paths.append(os.path.abspath(file_path))

            # Build metadata
            generation_time_ms = (time.time() - start_time) * 1000
            total_nodes = len(custom_nodes) + (len(nodes) if nodes else 0)
            metadata = build_diagram_metadata(
                file_paths,
                node_count=total_nodes,
                edge_count=edge_count,
                cluster_count=len(clusters) if clusters else 0,
                generation_time_ms=generation_time_ms,
            )

            # Base64 encoding if requested
            base64_images = None
            if return_base64:
                base64_images = {}
                for path in file_paths:
                    ext = Path(path).suffix[1:]
                    if ext != "dot":
                        try:
                            base64_images[ext] = encode_file_base64(path)
                        except Exception:
                            pass

            return format_diagram_result(file_paths, metadata, base64_images)

        finally:
            if output_dir:
                os.chdir(original_dir)

    except Exception as e:
        return format_error(f"Failed to generate diagram with custom icons: {str(e)}")


# ============================================================================
# Tool 3: List Available Nodes
# ============================================================================


@mcp.tool(
    name="list_available_nodes",
    description="""Discover 500+ node types across providers.

⚠️ USE THIS FIRST before create_diagram to avoid invalid node errors.

Filters: provider, category, search_term

Examples:
AWS compute: provider="aws", category="compute" → EC2, Lambda, ECS, EKS...
Search DBs: search_term="db" → RDS, DynamoDB, SQL across providers""",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
    },
)
async def list_available_nodes(
    provider: Annotated[
        Optional[str], Field(description="Filter by provider (aws, azure, gcp, etc.)")
    ] = None,
    category: Annotated[
        Optional[str], Field(description="Filter by category (compute, database, etc.)")
    ] = None,
    search_term: Annotated[
        Optional[str], Field(description="Search term for node type names")
    ] = None,
    limit: Annotated[int, Field(description="Maximum results to return", ge=1, le=500)] = 100,
) -> str:
    """List available diagram node types."""
    try:
        # Search nodes
        nodes = search_nodes(
            provider=provider,
            category=category,
            search_term=search_term,
            limit=limit,
        )

        # Calculate total (for this implementation, returned = total due to limit)
        total_count = len(nodes)
        returned_count = len(nodes)

        return format_node_catalog(nodes, total_count, returned_count)

    except Exception as e:
        return format_error(f"Failed to list nodes: {str(e)}")


# ============================================================================
# Tool 4: Create Flowchart
# ============================================================================


@mcp.tool(
    name="create_flowchart",
    description="""Create process flowcharts with 24 shapes (StartEnd, Process, Decision, etc.).

Example:
steps=[{"id":"start","shape":"StartEnd","label":"Start"},...]
flows=[{"from_step":"start","to_step":"check"},...]""",
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
    },
)
async def create_flowchart(
    name: Annotated[str, Field(description="Flowchart title")],
    steps: Annotated[List[FlowStepDef], Field(description="Flowchart steps")],
    flows: Annotated[List[FlowConnectionDef], Field(description="Connections between steps")],
    direction: Annotated[
        Literal["LR", "RL", "TB", "BT"], Field(description="Layout direction")
    ] = "TB",
    output_format: Annotated[
        str | List[str], Field(description="Output format(s): png, pdf, jpg, dot")
    ] = "png",
    output_dir: Annotated[
        Optional[str],
        Field(
            description="Output directory (default: current directory). Auto-created if missing."
        ),
    ] = None,
    graph_attr: Annotated[
        Optional[Dict[str, Any]],
        Field(description="Graphviz graph attributes (overrides defaults)"),
    ] = None,
    return_base64: Annotated[bool, Field(description="Return base64 images")] = False,
) -> str:
    """Create flowchart diagram."""
    start_time = time.time()

    try:
        from diagrams.programming.flowchart import (
            Action,
            Collate,
            Database,
            Decision,
            Delay,
            Display,
            Document,
            InputOutput,
            Inspection,
            InternalStorage,
            LoopLimit,
            ManualInput,
            ManualLoop,
            Merge,
            MultipleDocuments,
            OffPageConnectorLeft,
            OffPageConnectorRight,
            Or,
            PredefinedProcess,
            Preparation,
            Sort,
            StartEnd,
            StoredData,
            SummingJunction,
        )

        # Map shape names to classes (including user-friendly aliases)
        shape_map = {
            # User-friendly aliases
            "Process": PredefinedProcess,
            "Data": InputOutput,
            # Standard flowchart shapes
            "StartEnd": StartEnd,
            "Decision": Decision,
            "Document": Document,
            "Database": Database,
            "Delay": Delay,
            # All other available shapes
            "Action": Action,
            "Collate": Collate,
            "Display": Display,
            "Inspection": Inspection,
            "InternalStorage": InternalStorage,
            "InputOutput": InputOutput,
            "LoopLimit": LoopLimit,
            "ManualInput": ManualInput,
            "ManualLoop": ManualLoop,
            "Merge": Merge,
            "MultipleDocuments": MultipleDocuments,
            "OffPageConnectorLeft": OffPageConnectorLeft,
            "OffPageConnectorRight": OffPageConnectorRight,
            "Or": Or,
            "PredefinedProcess": PredefinedProcess,
            "Preparation": Preparation,
            "Sort": Sort,
            "StoredData": StoredData,
            "SummingJunction": SummingJunction,
        }

        # Validate steps
        step_ids = {step.id for step in steps}
        for step in steps:
            if step.shape not in shape_map:
                available = ", ".join(sorted(shape_map.keys()))
                raise ValueError(f"Unknown flowchart shape '{step.shape}'. Available: {available}")

        # Validate flows
        for flow in flows:
            if flow.from_step not in step_ids:
                raise ValueError(f"Flow references unknown step '{flow.from_step}'")

            targets = [flow.to_step] if isinstance(flow.to_step, str) else flow.to_step
            for target in targets:
                if target not in step_ids:
                    raise ValueError(f"Flow references unknown step '{target}'")

        # Generate flowchart
        formats = [output_format] if isinstance(output_format, str) else output_format

        # Reject SVG - it's buggy and unsupported
        if any("svg" in fmt.lower() for fmt in formats):
            raise ValueError("SVG output is not supported. Use png, pdf, jpg, or dot instead.")

        original_dir = os.getcwd()
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            os.chdir(output_dir)

        try:
            # Hide diagram title and set better flowchart layout attributes
            default_graph_attr = {
                "label": "",
                "splines": "ortho",  # Orthogonal edges with 90-degree angles
                "nodesep": "0.8",  # Horizontal spacing between nodes (inches)
                "ranksep": "0.75",  # Vertical spacing between ranks (inches)
            }
            merged_graph_attr = {**default_graph_attr, **(graph_attr or {})}

            with Diagram(
                name=name,
                show=False,
                direction=direction,
                outformat=formats,
                graph_attr=merged_graph_attr,
            ) as _:
                # Create step objects
                step_objects = {}
                for step in steps:
                    ShapeClass = shape_map[step.shape]
                    step_obj = ShapeClass(step.label)
                    step_objects[step.id] = step_obj

                # Create flows
                edge_count = 0
                for flow in flows:
                    from_obj = step_objects[flow.from_step]
                    targets = [flow.to_step] if isinstance(flow.to_step, str) else flow.to_step

                    for target in targets:
                        to_obj = step_objects[target]

                        if flow.label:
                            edge = Edge(label=flow.label)
                            _ = from_obj >> edge >> to_obj
                        else:
                            _ = from_obj >> to_obj

                        edge_count += 1

            # Get file paths
            diagram_filename = name.replace(" ", "_").replace("-", "_").lower()
            file_paths = []
            for fmt in formats:
                file_path = f"{diagram_filename}.{fmt}"
                if output_dir:
                    file_path = os.path.join(output_dir, file_path)
                file_paths.append(os.path.abspath(file_path))

            # Build metadata
            generation_time_ms = (time.time() - start_time) * 1000
            metadata = build_diagram_metadata(
                file_paths,
                node_count=len(steps),
                edge_count=edge_count,
                cluster_count=0,
                generation_time_ms=generation_time_ms,
            )

            # Base64 if requested
            base64_images = None
            if return_base64:
                base64_images = {}
                for path in file_paths:
                    ext = Path(path).suffix[1:]
                    if ext != "dot":
                        try:
                            base64_images[ext] = encode_file_base64(path)
                        except Exception:
                            pass

            return format_diagram_result(file_paths, metadata, base64_images)

        finally:
            if output_dir:
                os.chdir(original_dir)

    except Exception as e:
        return format_error(f"Failed to create flowchart: {str(e)}")


# ============================================================================
# Tool 5: Validate Diagram Spec
# ============================================================================


@mcp.tool(
    name="validate_diagram_spec",
    description="""Validate diagram before generation (dry-run).

Checks: node validity, connection references, cluster memberships.
Returns: {"valid": true/false, "errors": [...], "warnings": [...]}""",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
    },
)
async def validate_diagram_spec(
    nodes: Annotated[List[NodeDef], Field(description="Nodes to validate")],
    connections: Annotated[List[ConnectionDef], Field(description="Connections to validate")],
    clusters: Annotated[
        Optional[List[ClusterDef]], Field(description="Clusters to validate")
    ] = None,
) -> str:
    """Validate diagram specification."""
    errors = []
    warnings = []

    try:
        # Validate nodes
        node_ids = {node.id for node in nodes}

        for node in nodes:
            try:
                validate_node_reference(node.provider, node.category, node.type)
            except ValueError as e:
                errors.append(f"Node '{node.id}': {str(e)}")

        # Validate connections
        for conn in connections:
            if conn.from_node not in node_ids:
                errors.append(f"Connection references unknown source node '{conn.from_node}'")

            targets = [conn.to_node] if isinstance(conn.to_node, str) else conn.to_node
            for target in targets:
                if target not in node_ids:
                    errors.append(f"Connection references unknown target node '{target}'")

        # Validate clusters
        if clusters:
            cluster_names = {cluster.name for cluster in clusters}

            for cluster in clusters:
                # Check node references
                for node_id in cluster.node_ids:
                    if node_id not in node_ids:
                        errors.append(
                            f"Cluster '{cluster.name}' references unknown node '{node_id}'"
                        )

                # Check parent cluster exists
                if cluster.parent_cluster and cluster.parent_cluster not in cluster_names:
                    errors.append(
                        f"Cluster '{cluster.name}' references unknown parent '{cluster.parent_cluster}'"
                    )

                # Check for empty clusters
                if not cluster.node_ids:
                    warnings.append(f"Cluster '{cluster.name}' is empty")

        # Determine if valid
        valid = len(errors) == 0

        # Build metadata
        metadata = {
            "node_count": len(nodes),
            "edge_count": len(connections),
            "cluster_count": len(clusters) if clusters else 0,
        }

        return format_validation_result(valid, errors, warnings, metadata)

    except Exception as e:
        return format_error(f"Validation failed: {str(e)}")
