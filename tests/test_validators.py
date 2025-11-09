"""Tests for Pydantic validation models."""

from typing import Literal

import pytest
from pydantic import ValidationError
from diagrams_mcp.core.validators import (
    NodeDef,
    CustomNodeDef,
    ConnectionDef,
    ClusterDef,
    FlowStepDef,
    FlowConnectionDef,
    DiagramConfig,
)


# =============================================================================
# NodeDef tests
# =============================================================================


def test_node_def_valid():
    """Test valid NodeDef creation."""
    node = NodeDef(
        id="test_node",
        provider="aws",
        category="compute",
        type="EC2",
        label="Test Node",
    )

    assert node.id == "test_node"
    assert node.provider == "aws"
    assert node.category == "compute"
    assert node.type == "EC2"
    assert node.label == "Test Node"


def test_node_def_invalid_id_special_chars():
    """Test that node IDs with special characters are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        NodeDef(
            id="invalid@id",  # @ not allowed
            provider="aws",
            category="compute",
            type="EC2",
            label="Test",
        )

    assert "alphanumeric" in str(exc_info.value).lower()


def test_node_def_valid_id_formats():
    """Test valid ID formats with underscores and hyphens."""
    valid_ids = ["simple", "with_underscore", "with-hyphen", "mixed_123-test"]

    for valid_id in valid_ids:
        node = NodeDef(
            id=valid_id,
            provider="aws",
            category="compute",
            type="EC2",
            label="Test",
        )
        assert node.id == valid_id


# =============================================================================
# CustomNodeDef tests
# =============================================================================


def test_custom_node_def_url_valid():
    """Test valid CustomNodeDef with URL."""
    node = CustomNodeDef(
        id="custom",
        label="Custom App",
        icon_source="url",
        icon_path="https://example.com/icon.png",
    )

    assert node.icon_source == "url"
    assert node.icon_path == "https://example.com/icon.png"


def test_custom_node_def_local_valid():
    """Test valid CustomNodeDef with local path."""
    node = CustomNodeDef(
        id="custom",
        label="Custom App",
        icon_source="local",
        icon_path="/path/to/icon.png",
    )

    assert node.icon_source == "local"


def test_custom_node_def_non_https_rejected():
    """Test that non-HTTPS URLs are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        CustomNodeDef(
            id="custom",
            label="Custom App",
            icon_source="url",
            icon_path="http://example.com/icon.png",  # HTTP not HTTPS
        )

    assert "https" in str(exc_info.value).lower()


def test_custom_node_def_invalid_id():
    """Test that invalid IDs are rejected."""
    with pytest.raises(ValidationError):
        CustomNodeDef(
            id="invalid id with spaces",
            label="Custom App",
            icon_source="url",
            icon_path="https://example.com/icon.png",
        )


# =============================================================================
# ConnectionDef tests
# =============================================================================


def test_connection_def_valid():
    """Test valid ConnectionDef creation."""
    conn = ConnectionDef(
        from_node="node1",
        to_node="node2",
        direction="forward",
        label="test",
        color="red",
        style="dashed",
    )

    assert conn.from_node == "node1"
    assert conn.to_node == "node2"
    assert conn.direction == "forward"
    assert conn.label == "test"


def test_connection_def_list_to_node():
    """Test ConnectionDef with list of target nodes."""
    conn = ConnectionDef(from_node="node1", to_node=["node2", "node3"])

    assert conn.to_node == ["node2", "node3"]


def test_connection_def_directions():
    """Test all direction variants."""
    directions: list[Literal["forward", "reverse", "bidirectional"]] = [
        "forward",
        "reverse",
        "bidirectional",
    ]
    for direction in directions:
        conn = ConnectionDef(from_node="a", to_node="b", direction=direction)
        assert conn.direction == direction


# =============================================================================
# ClusterDef tests
# =============================================================================


def test_cluster_def_valid():
    """Test valid ClusterDef creation."""
    cluster = ClusterDef(
        name="VPC",
        node_ids=["node1", "node2"],
        graph_attr={"bgcolor": "#E5F5FD"},
    )

    assert cluster.name == "VPC"
    assert len(cluster.node_ids) == 2


def test_cluster_def_empty_node_ids():
    """Test that empty node_ids is rejected."""
    with pytest.raises(ValidationError):
        ClusterDef(name="Test", node_ids=[])


# =============================================================================
# FlowStepDef tests
# =============================================================================


def test_flow_step_def_valid():
    """Test valid FlowStepDef creation."""
    step = FlowStepDef(id="start", shape="StartEnd", label="Start")

    assert step.id == "start"
    assert step.shape == "StartEnd"
    assert step.label == "Start"


def test_flow_step_def_invalid_id():
    """Test that invalid IDs are rejected."""
    with pytest.raises(ValidationError):
        FlowStepDef(id="invalid id", shape="Process", label="Test")


# =============================================================================
# FlowConnectionDef tests
# =============================================================================


def test_flow_connection_def_valid():
    """Test valid FlowConnectionDef creation."""
    flow = FlowConnectionDef(
        from_step="step1",
        to_step="step2",
        label="Yes",
        condition="x > 0",
    )

    assert flow.from_step == "step1"
    assert flow.to_step == "step2"
    assert flow.label == "Yes"


# =============================================================================
# DiagramConfig tests
# =============================================================================


def test_diagram_config_valid():
    """Test valid DiagramConfig creation."""
    config = DiagramConfig(
        name="Test Diagram",
        direction="LR",
        output_format="png",
    )

    assert config.name == "Test Diagram"
    assert config.direction == "LR"
    assert config.output_format == "png"


def test_diagram_config_invalid_output_format():
    """Test that invalid output formats are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        DiagramConfig(output_format="invalid")

    assert "invalid" in str(exc_info.value).lower() or "format" in str(exc_info.value).lower()


def test_diagram_config_valid_output_formats():
    """Test all valid output formats."""
    for fmt in ["png", "pdf", "jpg", "dot"]:
        config = DiagramConfig(output_format=fmt)
        assert config.output_format == fmt


def test_diagram_config_output_format_list():
    """Test output_format as list."""
    config = DiagramConfig(output_format=["png", "pdf"])

    assert config.output_format == ["png", "pdf"]


def test_diagram_config_invalid_format_in_list():
    """Test that invalid format in list is rejected."""
    with pytest.raises(ValidationError):
        DiagramConfig(output_format=["png", "invalid"])


def test_diagram_config_directions():
    """Test all valid directions."""
    directions: list[Literal["LR", "RL", "TB", "BT"]] = ["LR", "RL", "TB", "BT"]
    for direction in directions:
        config = DiagramConfig(direction=direction)
        assert config.direction == direction


def test_diagram_config_defaults():
    """Test DiagramConfig defaults."""
    config = DiagramConfig()

    assert config.direction == "LR"
    assert config.curvestyle == "ortho"
    assert config.output_format == "png"
    assert config.autolabel is False
    assert config.show is False
    assert config.return_base64 is False
